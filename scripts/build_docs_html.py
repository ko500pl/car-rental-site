#!/usr/bin/env python3
"""Generate docs/*.html from docs/*.md.

Markdown is the source of truth; the HTML versions are for reading in a browser
and must never be edited by hand. Run after changing any file in docs/:

    python scripts/build_docs_html.py

Prints one line per written file and exits 0 on success.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INDEX = "00-DOCUMENTATION-INDEX"

# Repo-root documents that are worth reading in a browser. Their HTML twins are
# written into docs/ so every link in the index resolves to a rendered page.
ROOT_DOCS = [
    "README",
    "AUDIT",
    "RESEARCH",
    "IMPLEMENTATION_PLAN",
    "IMPLEMENTATION_REPORT",
    "ADMIN_SETUP",
    "FIREBASE",
    "ATTRACTION_SPEC",
]

TEMPLATE = """<!doctype html><html lang="ka"><head><meta charset="utf-8">\
<meta name="viewport" content="width=device-width"><title>{title}</title>\
<style>body{{font:15px/1.65 system-ui;max-width:940px;margin:36px auto;padding:0 22px;color:#172033}}\
a{{color:#087ea4}}h1,h2{{line-height:1.2}}h1{{font-size:30px}}\
h2{{margin-top:30px;border-top:1px solid #dce2ea;padding-top:18px}}h3{{margin-top:22px}}\
code{{background:#eef2f6;padding:2px 5px;border-radius:4px}}\
pre{{background:#eef2f6;padding:12px 14px;border-radius:8px;overflow-x:auto}}\
pre code{{background:none;padding:0}}li{{margin:5px 0}}\
table{{border-collapse:collapse;width:100%;margin:14px 0;display:block;overflow-x:auto}}\
th,td{{border:1px solid #dce2ea;padding:7px 10px;text-align:left;vertical-align:top}}\
th{{background:#f7fafc}}blockquote{{margin:14px 0;padding:10px 16px;border-left:3px solid #087ea4;background:#f7fafc}}\
blockquote p{{margin:6px 0}}.back{{display:inline-block;margin-bottom:18px}}\
.meta{{color:#64748b;font-size:13px}}</style></head><body>{back}\
<div class="meta">ლოკალური დოკუმენტაცია · {stamp}</div>
{body}</body></html>
"""

BACK = '<a class="back" href="{}.html">← დოკუმენტაციის ინდექსი</a>'.format(INDEX)


def md_links_to_html(html: str, known: set[str]) -> str:
    """Rewrite markdown links to their generated HTML twins.

    Every generated page lives in docs/, so "foo.md", "../foo.md" and
    "docs/foo.md" all collapse to "foo.html". A link whose target has no
    generated twin is left untouched rather than pointed at a missing file.
    """

    def repl(m: re.Match[str]) -> str:
        href = m.group(1)
        stem = href[:-3]
        for prefix in ("../", "docs/", "./"):
            if stem.startswith(prefix):
                stem = stem[len(prefix):]
                break
        if "/" in stem:
            return m.group(0)
        if stem in known:
            return 'href="{}.html"'.format(stem)
        return m.group(0)

    return re.sub(r'href="([^"#]+\.md)"', repl, html)


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def main() -> int:
    if not DOCS.is_dir():
        print("docs/ not found", file=sys.stderr)
        return 1

    sources = sorted(DOCS.glob("*.md"))
    if not sources:
        print("no markdown sources in docs/", file=sys.stderr)
        return 1

    for name in ROOT_DOCS:
        candidate = ROOT / (name + ".md")
        if candidate.exists():
            sources.append(candidate)
        else:
            print("skipped missing root doc:", candidate.name, file=sys.stderr)

    known = {p.stem for p in sources}
    stamp = date.today().isoformat()
    written = 0

    for src in sources:
        text = src.read_text(encoding="utf-8")
        body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        )
        body = md_links_to_html(body, known)
        page = TEMPLATE.format(
            title=title_of(text, src.stem),
            back="" if src.stem == INDEX else BACK,
            stamp=stamp,
            body=body,
        )
        out = DOCS / (src.stem + ".html")
        out.write_text(page, encoding="utf-8")
        print("wrote", out.name)
        written += 1

    # index.html keeps working for old bookmarks by mirroring the real index.
    index_src = DOCS / (INDEX + ".html")
    if index_src.exists():
        (DOCS / "index.html").write_text(
            index_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
        print("wrote index.html (mirror of {}.html)".format(INDEX))
        written += 1

    print("{} files".format(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
