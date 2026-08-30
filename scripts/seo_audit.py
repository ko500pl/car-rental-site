#!/usr/bin/env python3
"""SEO audit for the built RentUp.ge ``dist/`` tree.

Pure filesystem + regex/HTMLParser inspection — no network calls, no
dependencies beyond the standard library. This validates the assertions
documented in ``docs/seo/SEO_VALIDATION.md`` (Automated assertions #1-#17).

Usage:
    python scripts/seo_audit.py [dist]

Exit code is non-zero if any ERROR-level finding is produced.

This module is import-safe: importing it runs nothing. Call :func:`audit`
to run the checks and get back a :class:`Report`. The CLI only runs under
``if __name__ == "__main__":``.
"""

from __future__ import annotations

import argparse
import collections
import html as html_lib
import json
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urlsplit

# --------------------------------------------------------------------------
# Constants / defaults (kept data-driven so callers — and future content —
# can extend them without editing check logic).
# --------------------------------------------------------------------------

DOMAIN = "rentup.ge"
ORIGIN = f"https://{DOMAIN}"

ALL_LANGS: Tuple[str, ...] = ("en", "ka", "ru", "fa", "he", "ar")
ROOT_LANG = "en"
EXPECTED_HREFLANGS: Set[str] = set(ALL_LANGS) | {"x-default"}

DEFAULT_LEGACY_BRANDS: Tuple[str, ...] = ("Drive On",)

# Canonical aliases: a lang-stripped path that is *deliberately* not
# self-referencing, mapped to the lang-stripped path it canonicalizes to.
DEFAULT_CANONICAL_ALIASES: Dict[str, str] = {
    "/pricing/": "/fleet/",
    "/planner/": "/map/",
}

# Guard lists (SEO_VALIDATION.md #10 / #11). Lang-stripped paths, checked
# across every language mirror that exists. A trailing '*' is a prefix
# match. A pattern that matches zero pages today is reported as INFO
# ("not built yet"), never as an ERROR — see module docstring.
DEFAULT_MUST_BE_INDEXABLE: Tuple[str, ...] = (
    "/", "/fleet/", "/map/", "/tours/",
    "/car-rental/*", "/routes/*", "/attractions/*", "/itineraries/*",
)
DEFAULT_MUST_BE_NOINDEX: Tuple[str, ...] = (
    "/trip/", "/account/", "/app/", "/admin/*", "/pricing/",
)

# Pages exempt from "exactly one canonical" (#1): disallowed-by-robots or
# app-shell pages that are never meant to be crawled/indexed at all.
DEFAULT_CANONICAL_EXEMPT_PREFIXES: Tuple[str, ...] = ("/admin/",)
DEFAULT_CANONICAL_EXEMPT_PATHS: Tuple[str, ...] = ("/404.html", "/app/")

MAX_TITLE_CHARS = 70

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
_SEVERITY_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

CHECK_CANONICAL = "canonical"
CHECK_TITLE = "title"
CHECK_DESCRIPTION = "meta-description"
CHECK_H1 = "h1"
CHECK_KEYWORDS = "meta-keywords"
CHECK_HREFLANG = "hreflang"
CHECK_SITEMAP_VALID = "sitemap-valid-entries"
CHECK_SITEMAP_COVERAGE = "sitemap-coverage"
CHECK_GUARD_INDEXABLE = "guard-must-be-indexable"
CHECK_GUARD_NOINDEX = "guard-must-be-noindex"
CHECK_LDJSON = "ld-json-valid"
CHECK_BREADCRUMBS = "breadcrumb-links"
CHECK_INTERNAL_LINKS = "internal-links"
CHECK_ROBOTS_TXT = "robots-txt"
CHECK_BRAND = "legacy-brand"
CHECK_IMG_ALT = "img-alt"
CHECK_DIST = "dist"

ALL_CHECKS: Tuple[str, ...] = (
    CHECK_DIST, CHECK_CANONICAL, CHECK_TITLE, CHECK_DESCRIPTION, CHECK_H1,
    CHECK_KEYWORDS, CHECK_HREFLANG, CHECK_SITEMAP_VALID, CHECK_SITEMAP_COVERAGE,
    CHECK_GUARD_INDEXABLE, CHECK_GUARD_NOINDEX, CHECK_LDJSON, CHECK_BREADCRUMBS,
    CHECK_INTERNAL_LINKS, CHECK_ROBOTS_TXT, CHECK_BRAND, CHECK_IMG_ALT,
)


# --------------------------------------------------------------------------
# Report / Finding
# --------------------------------------------------------------------------


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    page: Optional[str] = None


@dataclass
class Report:
    findings: List[Finding] = field(default_factory=list)

    def add(self, check: str, severity: str, message: str, page: Optional[str] = None) -> None:
        self.findings.append(Finding(check=check, severity=severity, message=message, page=page))

    def merge(self, other: "Report") -> None:
        self.findings.extend(other.findings)

    def by_check(self, check: str) -> List[Finding]:
        return [f for f in self.findings if f.check == check]

    def by_severity(self, severity: str) -> List[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def counts(self) -> Dict[str, int]:
        c = {ERROR: 0, WARN: 0, INFO: 0}
        for f in self.findings:
            c[f.severity] = c.get(f.severity, 0) + 1
        return c

    @property
    def has_errors(self) -> bool:
        return any(f.severity == ERROR for f in self.findings)

    def render(self, max_examples: int = 10) -> str:
        lines: List[str] = []
        counts = self.counts()

        lines.append("RentUp.ge SEO Audit")
        lines.append("=" * 72)
        lines.append("")
        lines.append(f"{'Severity':<10}{'Count':>8}")
        lines.append("-" * 18)
        for sev in (ERROR, WARN, INFO):
            lines.append(f"{sev:<10}{counts.get(sev, 0):>8}")
        lines.append("")

        by_check: "collections.OrderedDict[str, List[Finding]]" = collections.OrderedDict()
        for f in self.findings:
            by_check.setdefault(f.check, []).append(f)

        lines.append(f"{'Check':<28}{'ERROR':>7}{'WARN':>7}{'INFO':>7}")
        lines.append("-" * 49)
        for check, items in by_check.items():
            c = collections.Counter(i.severity for i in items)
            lines.append(f"{check:<28}{c.get(ERROR, 0):>7}{c.get(WARN, 0):>7}{c.get(INFO, 0):>7}")
        lines.append("")

        if not by_check:
            lines.append("No findings — every check passed with nothing to report.")
        for check, items in by_check.items():
            items = sorted(items, key=lambda f: _SEVERITY_ORDER.get(f.severity, 9))
            plural = "" if len(items) == 1 else "s"
            lines.append(f"## {check}  ({len(items)} finding{plural})")
            for item in items[:max_examples]:
                loc = f"{item.page}: " if item.page else ""
                lines.append(f"  [{item.severity}] {loc}{item.message}")
            remaining = len(items) - max_examples
            if remaining > 0:
                lines.append(f"  ... +{remaining} more")
            lines.append("")

        lines.append(
            f"TOTAL: {counts.get(ERROR, 0)} ERROR, {counts.get(WARN, 0)} WARN, {counts.get(INFO, 0)} INFO"
        )
        return "\n".join(lines)


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


@dataclass
class AuditConfig:
    legacy_brands: Sequence[str] = DEFAULT_LEGACY_BRANDS
    canonical_aliases: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_CANONICAL_ALIASES))
    must_be_indexable: Sequence[str] = DEFAULT_MUST_BE_INDEXABLE
    must_be_noindex: Sequence[str] = DEFAULT_MUST_BE_NOINDEX
    canonical_exempt_prefixes: Sequence[str] = DEFAULT_CANONICAL_EXEMPT_PREFIXES
    canonical_exempt_paths: Sequence[str] = DEFAULT_CANONICAL_EXEMPT_PATHS


# --------------------------------------------------------------------------
# Path helpers
# --------------------------------------------------------------------------


def dist_path_for(dist_dir: Path, file: Path) -> str:
    """Map a file under dist/ to the site-relative URL path it serves."""
    rel = file.relative_to(dist_dir).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def strip_lang(path: str) -> Tuple[str, str]:
    """Split a site path into (lang, lang-stripped path). Root lang = 'en'."""
    for lang in ALL_LANGS:
        if lang == ROOT_LANG:
            continue
        prefix = f"/{lang}/"
        if path == f"/{lang}":
            return lang, "/"
        if path.startswith(prefix):
            return lang, "/" + path[len(prefix):]
    return ROOT_LANG, path


def relocalize(lang: str, stripped_path: str) -> str:
    """Inverse of strip_lang: rebuild a full path for `lang` from a base path."""
    if lang == ROOT_LANG:
        return stripped_path
    return f"/{lang}" + stripped_path


def url_to_path(url: str) -> Optional[str]:
    """Extract the site-relative path from an absolute rentup.ge URL.

    Returns None if the URL is not on our domain (or is unparsable).
    """
    if not url:
        return None
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return None
    if parts.netloc and parts.netloc != DOMAIN:
        return None
    if not parts.netloc and not url.startswith("/"):
        return None
    return parts.path or "/"


def resolve_path_to_file(dist_dir: Path, path: str) -> Optional[Path]:
    """Resolve a site path to a real file under dist/, honoring the
    directory + index.html convention, or None if nothing matches."""
    if not path or not path.startswith("/"):
        return None
    rel = path.lstrip("/")
    candidate = dist_dir / rel if rel else dist_dir
    try:
        if candidate.is_dir():
            index = candidate / "index.html"
            return index if index.is_file() else None
        if candidate.is_file():
            return candidate
    except OSError:
        return None
    return None


def is_noindex(robots_content: str) -> bool:
    return "noindex" in (robots_content or "").lower()


# --------------------------------------------------------------------------
# Page parsing (regex-based: the generated markup is consistent enough that
# a full HTML tree is unnecessary, and this keeps a whole-corpus crawl fast)
# --------------------------------------------------------------------------

_ROBOTS_RE = re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']*)["\']', re.I)
_CANON_RE = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']*)["\']', re.I)
_LANG_RE = re.compile(r'<html\b[^>]*\blang=["\']([^"\']*)["\']', re.I)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', re.I)
_KEYWORDS_RE = re.compile(r'<meta\s+name=["\']keywords["\']', re.I)
_H1_RE = re.compile(r"<h1\b", re.I)
_HREFLANG_RE = re.compile(
    r'<link\s+rel=["\']alternate["\']\s+hreflang=["\']([^"\']+)["\']\s+href=["\']([^"\']+)["\']', re.I
)
_IMG_RE = re.compile(r"<img\b([^>]*)>", re.I)
_ALT_ATTR_RE = re.compile(r"(?:^|\s)alt\s*=", re.I)
_ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref=["\'](/[^"\']*)["\']', re.I)
_LDJSON_RE = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.I | re.S)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")


@dataclass
class PageData:
    path: str
    file: Path
    lang: Optional[str]
    robots: str
    canonical_urls: List[str]
    title: Optional[str]
    description: Optional[str]
    has_keywords_meta: bool
    h1_count: int
    hreflang: Dict[str, str]
    hreflang_pairs: List[Tuple[str, str]]
    images_have_alt: List[bool]
    anchors: List[str]
    ld_json_blocks: List[str]
    readable: bool


def load_page(dist_dir: Path, file: Path) -> PageData:
    path = dist_path_for(dist_dir, file)
    try:
        raw = file.read_text(encoding="utf-8", errors="replace")
        readable = True
    except OSError:
        raw = ""
        readable = False

    lang_m = _LANG_RE.search(raw)
    robots_m = _ROBOTS_RE.search(raw)
    title_m = _TITLE_RE.search(raw)
    desc_m = _DESC_RE.search(raw)

    title = None
    if title_m:
        title = html_lib.unescape(_TAG_STRIP_RE.sub("", title_m.group(1))).strip()

    description = html_lib.unescape(desc_m.group(1)).strip() if desc_m else None

    hreflang_pairs = list(_HREFLANG_RE.findall(raw))
    hreflang: Dict[str, str] = {}
    for lang, href in hreflang_pairs:
        hreflang[lang] = href

    images_have_alt = [bool(_ALT_ATTR_RE.search(m)) for m in _IMG_RE.findall(raw)]
    anchors = _ANCHOR_RE.findall(raw)
    ld_json_blocks = _LDJSON_RE.findall(raw)

    return PageData(
        path=path,
        file=file,
        lang=(lang_m.group(1) if lang_m else None),
        robots=(robots_m.group(1) if robots_m else ""),
        canonical_urls=list(_CANON_RE.findall(raw)),
        title=title,
        description=description,
        has_keywords_meta=bool(_KEYWORDS_RE.search(raw)),
        h1_count=len(_H1_RE.findall(raw)),
        hreflang=hreflang,
        hreflang_pairs=hreflang_pairs,
        images_have_alt=images_have_alt,
        anchors=anchors,
        ld_json_blocks=ld_json_blocks,
        readable=readable,
    )


def _iter_ld_nodes(data) -> Iterable[dict]:
    if isinstance(data, dict):
        graph = data.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                yield node
        else:
            yield data
    elif isinstance(data, list):
        for node in data:
            yield node


# --------------------------------------------------------------------------
# Individual checks. Each takes the full `pages` map (so cross-page lookups
# — hreflang reciprocity, sitemap, guard lists — always see the whole site)
# plus a `sample_paths` set that bounds which pages get *reported on* for
# the per-page checks. Sitemap coverage and guard-list checks ignore the
# sample entirely, as required.
# --------------------------------------------------------------------------


def _check_canonical(pages: Dict[str, PageData], sample_paths: Set[str], config: AuditConfig, report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        _, stripped_for_exempt = strip_lang(path)
        exempt = (
            path in config.canonical_exempt_paths
            or stripped_for_exempt in config.canonical_exempt_paths
            or any(path.startswith(prefix) for prefix in config.canonical_exempt_prefixes)
        )
        if exempt:
            continue

        urls = page.canonical_urls
        if not urls:
            report.add(CHECK_CANONICAL, ERROR, "missing <link rel=\"canonical\">", path)
            continue
        if len(urls) > 1:
            report.add(CHECK_CANONICAL, ERROR, f"{len(urls)} canonical tags found (expected exactly 1)", path)

        url = urls[0]
        if not (url == ORIGIN or url.startswith(ORIGIN + "/")):
            report.add(CHECK_CANONICAL, ERROR, f"canonical is not absolute https://{DOMAIN}/...: {url!r}", path)
            continue

        if is_noindex(page.robots):
            continue  # self-reference is only required for indexable pages (#2)

        expected_self = ORIGIN + path
        if url == expected_self:
            continue

        lang, stripped = strip_lang(path)
        alias_target = config.canonical_aliases.get(stripped)
        if alias_target is not None:
            expected_alias = ORIGIN + relocalize(lang, alias_target)
            if url == expected_alias:
                continue

        report.add(
            CHECK_CANONICAL, ERROR,
            f"canonical {url!r} is neither self-referencing ({expected_self!r}) nor a documented alias",
            path,
        )


def _check_titles(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    by_lang: Dict[str, Dict[str, List[str]]] = collections.defaultdict(dict)
    for path in sorted(sample_paths):
        page = pages[path]
        if is_noindex(page.robots):
            continue
        if not page.title:
            report.add(CHECK_TITLE, ERROR, "missing or empty <title>", path)
            continue
        if len(page.title) > MAX_TITLE_CHARS:
            report.add(
                CHECK_TITLE, WARN,
                f"title is {len(page.title)} chars, recommended <= {MAX_TITLE_CHARS}: {page.title!r}",
                path,
            )
        lang = page.lang or strip_lang(path)[0]
        by_lang[lang].setdefault(page.title, []).append(path)

    for lang, titles in by_lang.items():
        for title, paths in titles.items():
            if len(paths) > 1:
                shown = ", ".join(sorted(paths)[:5])
                extra = f" (+{len(paths) - 5} more)" if len(paths) > 5 else ""
                report.add(
                    CHECK_TITLE, ERROR,
                    f"title duplicated across {len(paths)} pages in lang={lang}: {title!r} -> {shown}{extra}",
                )


def _check_descriptions(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        if is_noindex(page.robots):
            continue
        if not page.description:
            report.add(CHECK_DESCRIPTION, ERROR, "missing or empty <meta name=\"description\">", path)


def _check_h1(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        if page.h1_count == 1:
            continue
        if is_noindex(page.robots):
            # noindex pages are SEO-neutral; a bad H1 count there is an
            # accessibility hygiene issue, not a ranking issue.
            report.add(CHECK_H1, INFO, f"{page.h1_count} <h1> elements (noindex page, a11y only)", path)
        else:
            report.add(CHECK_H1, ERROR, f"{page.h1_count} <h1> elements found (expected exactly 1)", path)


def _check_keywords(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        if pages[path].has_keywords_meta:
            report.add(CHECK_KEYWORDS, ERROR, "<meta name=\"keywords\"> present (should be removed)", path)


def _check_hreflang(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        pairs = page.hreflang_pairs
        if not pairs:
            continue  # not a "localized" page (admin/app/404/aliases, etc.)

        langs_seen = [lang for lang, _ in pairs]
        dup_langs = sorted({lang for lang in langs_seen if langs_seen.count(lang) > 1})
        if dup_langs:
            report.add(CHECK_HREFLANG, ERROR, f"duplicate hreflang code(s): {dup_langs}", path)

        keys = set(page.hreflang.keys())
        missing = sorted(EXPECTED_HREFLANGS - keys)
        extra = sorted(keys - EXPECTED_HREFLANGS)
        if missing:
            report.add(CHECK_HREFLANG, ERROR, f"missing hreflang(s): {missing}", path)
        if extra:
            report.add(CHECK_HREFLANG, ERROR, f"unexpected hreflang code(s): {extra}", path)

        for lang, href in page.hreflang.items():
            if not (href == ORIGIN or href.startswith(ORIGIN + "/")):
                report.add(CHECK_HREFLANG, ERROR, f"hreflang[{lang}] is not absolute https://{DOMAIN}/...: {href!r}", path)

        src_lang = page.lang or strip_lang(path)[0]
        for lang, href in page.hreflang.items():
            if lang == "x-default":
                continue
            target_path = url_to_path(href)
            if target_path is None:
                continue
            target = pages.get(target_path)
            if target is None:
                report.add(CHECK_HREFLANG, ERROR, f"hreflang[{lang}] target has no matching file in dist/: {href}", path)
                continue
            back = target.hreflang.get(src_lang)
            if back != ORIGIN + path:
                report.add(
                    CHECK_HREFLANG, ERROR,
                    f"not reciprocal: hreflang[{lang}]={href} but {target_path} lists lang={src_lang} as {back!r}",
                    path,
                )


def _check_sitemap(dist_dir: Path, pages: Dict[str, PageData], report: Report) -> None:
    # A sitemap index (sitemap.xml) may point at children under dist/sitemaps/.
    sitemap_files = sorted(dist_dir.glob("sitemap*.xml")) + sorted(dist_dir.glob("sitemaps/*.xml"))
    if not sitemap_files:
        report.add(CHECK_SITEMAP_VALID, ERROR, "no sitemap*.xml found under dist/")
        return
    index_locs = set()
    for sm in sitemap_files:
        try:
            raw = sm.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "<sitemapindex" in raw:
            for child in re.findall(r"<loc>([^<]+)</loc>", raw):
                index_locs.add(child.strip())
                rel = child.strip().split(DOMAIN, 1)[-1].lstrip("/")
                if not (dist_dir / rel).exists():
                    report.add(CHECK_SITEMAP_VALID, ERROR,
                               f"sitemap index points at a missing child: {child}")

    all_locs: List[str] = []
    for sm in sitemap_files:
        try:
            raw = sm.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            report.add(CHECK_SITEMAP_VALID, ERROR, f"could not read {sm.name}: {exc}")
            continue
        all_locs.extend(re.findall(r"<loc>([^<]+)</loc>", raw))

    seen_paths: "collections.Counter[str]" = collections.Counter()
    for loc in all_locs:
        if loc.strip() in index_locs:
            continue                      # child sitemap reference, not a page
        target_path = url_to_path(loc.strip())
        if target_path is None:
            report.add(CHECK_SITEMAP_VALID, ERROR, f"sitemap <loc> is not on {DOMAIN}: {loc}")
            continue
        seen_paths[target_path] += 1
        page = pages.get(target_path)
        if page is None:
            report.add(CHECK_SITEMAP_VALID, ERROR, f"sitemap <loc> has no matching file in dist/: {loc}")
            continue
        if is_noindex(page.robots):
            report.add(CHECK_SITEMAP_VALID, ERROR, f"sitemap contains a noindex page: {loc}")

    for target_path, count in sorted(seen_paths.items()):
        if count > 1:
            report.add(CHECK_SITEMAP_COVERAGE, ERROR, f"appears {count} times across sitemap(s)", target_path)

    for target_path, page in sorted(pages.items()):
        if is_noindex(page.robots):
            continue
        if seen_paths.get(target_path, 0) == 0:
            report.add(CHECK_SITEMAP_COVERAGE, ERROR, "indexable page is missing from every sitemap", target_path)


def _match_guard(pattern: str, all_paths: Set[str]) -> Set[str]:
    """Concrete paths matching a guard-list pattern, across every language
    mirror. A trailing '*' means prefix match on the lang-stripped base."""
    matches: Set[str] = set()
    if pattern.endswith("*"):
        base = pattern[:-1]
        for lang in ALL_LANGS:
            localized_base = relocalize(lang, base)
            for p in all_paths:
                if p.startswith(localized_base):
                    matches.add(p)
    else:
        for lang in ALL_LANGS:
            localized = relocalize(lang, pattern)
            if localized in all_paths:
                matches.add(localized)
    return matches


def _check_guard_lists(pages: Dict[str, PageData], config: AuditConfig, report: Report) -> None:
    all_paths = set(pages.keys())

    for pattern in config.must_be_indexable:
        matches = _match_guard(pattern, all_paths)
        if not matches:
            report.add(CHECK_GUARD_INDEXABLE, INFO, f"pattern {pattern!r} matches no pages yet (not built) — skipped")
            continue
        for path in sorted(matches):
            if is_noindex(pages[path].robots):
                report.add(
                    CHECK_GUARD_INDEXABLE, ERROR,
                    f"must be indexable per guard list ({pattern!r}) but is noindex", path,
                )

    for pattern in config.must_be_noindex:
        matches = _match_guard(pattern, all_paths)
        if not matches:
            report.add(CHECK_GUARD_NOINDEX, INFO, f"pattern {pattern!r} matches no pages — nothing to check")
            continue
        for path in sorted(matches):
            if not is_noindex(pages[path].robots):
                report.add(
                    CHECK_GUARD_NOINDEX, ERROR,
                    f"must be noindex per guard list ({pattern!r}) but is indexable", path,
                )


def _check_ld_json(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        for i, block in enumerate(page.ld_json_blocks):
            text = block.strip()
            if not text:
                report.add(CHECK_LDJSON, WARN, f"empty ld+json block #{i}", path)
                continue
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                report.add(CHECK_LDJSON, ERROR, f"ld+json block #{i} failed to parse: {exc}", path)


def _check_breadcrumbs(dist_dir: Path, pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        page = pages[path]
        for block in page.ld_json_blocks:
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                continue  # already reported by _check_ld_json
            for node in _iter_ld_nodes(data):
                if not isinstance(node, dict) or node.get("@type") != "BreadcrumbList":
                    continue
                for item in node.get("itemListElement", []):
                    if not isinstance(item, dict):
                        continue
                    url = item.get("item")
                    if not url:
                        continue
                    target_path = url_to_path(url)
                    if target_path is None:
                        report.add(CHECK_BREADCRUMBS, ERROR, f"breadcrumb item is not on {DOMAIN}: {url}", path)
                        continue
                    if resolve_path_to_file(dist_dir, target_path) is None:
                        report.add(CHECK_BREADCRUMBS, ERROR, f"breadcrumb item does not resolve to a file: {url}", path)


def _check_internal_links(dist_dir: Path, pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    seen: Set[Tuple[str, str]] = set()
    for path in sorted(sample_paths):
        page = pages[path]
        for href in page.anchors:
            url_path = urlsplit(href).path
            if not url_path:
                continue
            key = (path, url_path)
            if key in seen:
                continue
            seen.add(key)
            if resolve_path_to_file(dist_dir, url_path) is None:
                report.add(CHECK_INTERNAL_LINKS, ERROR, f"broken internal link {href!r}", path)


def _check_robots_txt(dist_dir: Path, report: Report) -> None:
    robots_path = dist_dir / "robots.txt"
    if not robots_path.is_file():
        report.add(CHECK_ROBOTS_TXT, ERROR, "robots.txt not found under dist/")
        return
    try:
        text = robots_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        report.add(CHECK_ROBOTS_TXT, ERROR, f"could not read robots.txt: {exc}")
        return

    if not re.search(r"(?im)^\s*allow\s*:\s*/\s*$", text):
        report.add(CHECK_ROBOTS_TXT, ERROR, "robots.txt does not have an 'Allow: /' directive")
    if not re.search(r"(?im)^\s*disallow\s*:\s*/admin/\s*$", text):
        report.add(CHECK_ROBOTS_TXT, ERROR, "robots.txt does not have a 'Disallow: /admin/' directive")
    if not re.search(r"(?im)^\s*sitemap\s*:\s*https?://", text):
        report.add(CHECK_ROBOTS_TXT, ERROR, "robots.txt has no 'Sitemap:' directive")


def _check_brand(pages: Dict[str, PageData], sample_paths: Set[str], config: AuditConfig, report: Report) -> None:
    for path in sorted(sample_paths):
        title = pages[path].title
        if not title:
            continue
        for brand in config.legacy_brands:
            if brand and brand in title:
                report.add(CHECK_BRAND, ERROR, f"legacy brand {brand!r} found in <title>: {title!r}", path)
                break


def _check_img_alt(pages: Dict[str, PageData], sample_paths: Set[str], report: Report) -> None:
    for path in sorted(sample_paths):
        images = pages[path].images_have_alt
        missing = sum(1 for has_alt in images if not has_alt)
        if missing:
            report.add(CHECK_IMG_ALT, ERROR, f"{missing} of {len(images)} <img> tag(s) missing an alt attribute", path)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def crawl(dist_dir: Path) -> Dict[str, PageData]:
    """Parse every .html file under dist_dir into a path -> PageData map."""
    files = sorted(dist_dir.rglob("*.html"))
    pages: Dict[str, PageData] = {}
    for f in files:
        page = load_page(dist_dir, f)
        pages[page.path] = page
    return pages


def audit(
    dist_dir: "str | Path",
    config: Optional[AuditConfig] = None,
    sample: Optional[int] = None,
    seed: int = 0,
) -> Report:
    """Run the full SEO audit against a built dist/ tree.

    `sample`, if given, bounds the per-page checks (canonical, title, meta
    description, h1, keywords, hreflang, ld+json, breadcrumbs, internal
    links, brand, img alt) to a deterministic random sample of at most
    `sample` pages, to keep repeated runs (e.g. in tests) fast. Sitemap
    coverage and the noindex/indexable guard lists always run against the
    full site regardless of `sample`, since they are cheap (no full-page
    parsing needed) and correctness-critical.
    """
    dist_dir = Path(dist_dir)
    config = config or AuditConfig()
    report = Report()

    if not dist_dir.is_dir():
        report.add(CHECK_DIST, ERROR, f"dist directory not found: {dist_dir}")
        return report

    pages = crawl(dist_dir)
    if not pages:
        report.add(CHECK_DIST, ERROR, f"no .html files found under {dist_dir}")
        return report

    all_paths = sorted(pages.keys())
    if sample is not None and sample < len(all_paths):
        rng = random.Random(seed)
        sample_paths: Set[str] = set(rng.sample(all_paths, sample))
    else:
        sample_paths = set(all_paths)

    _check_canonical(pages, sample_paths, config, report)
    _check_titles(pages, sample_paths, report)
    _check_descriptions(pages, sample_paths, report)
    _check_h1(pages, sample_paths, report)
    _check_keywords(pages, sample_paths, report)
    _check_hreflang(pages, sample_paths, report)
    _check_sitemap(dist_dir, pages, report)
    _check_guard_lists(pages, config, report)
    _check_ld_json(pages, sample_paths, report)
    _check_breadcrumbs(dist_dir, pages, sample_paths, report)
    _check_internal_links(dist_dir, pages, sample_paths, report)
    _check_robots_txt(dist_dir, report)
    _check_brand(pages, sample_paths, config, report)
    _check_img_alt(pages, sample_paths, report)

    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="RentUp.ge SEO audit over a built dist/ tree.")
    parser.add_argument("dist", nargs="?", default="dist", help="path to the built dist/ directory (default: dist)")
    parser.add_argument(
        "--brand", action="append", metavar="STRING",
        help="legacy brand string to flag in <title> (repeatable; default: 'Drive On')",
    )
    parser.add_argument("--max-examples", type=int, default=10, help="examples to print per check (default: 10)")
    parser.add_argument(
        "--sample", type=int, default=None, metavar="N",
        help="limit per-page checks to N sampled pages (sitemap + guard lists always run on the whole site)",
    )
    args = parser.parse_args(argv)

    config = AuditConfig()
    if args.brand:
        config.legacy_brands = tuple(args.brand)

    report = audit(args.dist, config=config, sample=args.sample)
    print(report.render(max_examples=args.max_examples))
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
