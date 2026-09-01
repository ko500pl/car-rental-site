#!/usr/bin/env python3
"""Tell Bing, Yandex, Seznam and Naver which pages changed.

A new site waits weeks for a first crawl. IndexNow inverts that: one POST and
the participating engines fetch the listed URLs within hours. It costs nothing
and needs no account — the only proof of ownership is the key file the build
publishes at https://rentup.ge/<key>.txt.

Google does not participate, so this does not replace Search Console; it covers
Bing (which also feeds DuckDuckGo and ChatGPT search) and Yandex, and Yandex
matters here because a large share of Georgia's rental demand searches in
Russian.

    python scripts/indexnow_submit.py                 # everything in the sitemap
    python scripts/indexnow_submit.py --changed-since 2026-09-01
    python scripts/indexnow_submit.py --dry-run       # show what would be sent

Run it after a deploy, once the pages are actually live: the engines fetch the
URLs you name, and naming a URL that 404s wastes the submission.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://api.indexnow.org/IndexNow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
BATCH = 10_000          # the protocol's per-request ceiling


def load_site() -> dict:
    return yaml.safe_load((ROOT / "content/settings/site.yml").read_text(encoding="utf-8"))


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "RentUp-IndexNow/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sitemap_urls(index_url: str, changed_since: str | None) -> list[str]:
    """Every URL in the sitemap index, optionally only those modified since a date."""
    urls: list[str] = []
    root = ET.fromstring(fetch(index_url))
    children = [el.text.strip() for el in root.findall(".//sm:sitemap/sm:loc", NS) if el.text]
    if not children:                      # a flat sitemap rather than an index
        children = [index_url]
    for child in children:
        try:
            tree = ET.fromstring(fetch(child))
        except (urllib.error.URLError, ET.ParseError) as e:
            print(f"  ! could not read {child}: {e}", file=sys.stderr)
            continue
        for url in tree.findall(".//sm:url", NS):
            loc = url.findtext("sm:loc", namespaces=NS)
            if not loc:
                continue
            if changed_since:
                lastmod = (url.findtext("sm:lastmod", namespaces=NS) or "")[:10]
                if lastmod and lastmod < changed_since:
                    continue
            urls.append(loc.strip())
    return sorted(set(urls))


def submit(host: str, key: str, key_location: str, urls: list[str]) -> bool:
    payload = json.dumps({
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "RentUp-IndexNow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            # 200 accepted, 202 accepted but the key is still being verified.
            print(f"  {r.status} {r.reason} for {len(urls)} URLs")
            return r.status in (200, 202)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        hint = {
            400: "malformed request",
            403: "the key file is not reachable at keyLocation — deploy first",
            422: "a URL does not belong to this host, or the key does not match",
            429: "too many requests; wait and retry",
        }.get(e.code, "")
        print(f"  ! {e.code} {e.reason}{' — ' + hint if hint else ''}\n    {body}",
              file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"  ! could not reach IndexNow: {e}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--changed-since", metavar="YYYY-MM-DD",
                    help="only URLs whose sitemap lastmod is on or after this date")
    ap.add_argument("--limit", type=int, help="submit at most this many URLs")
    ap.add_argument("--dry-run", action="store_true", help="print, do not send")
    args = ap.parse_args()

    site = load_site()
    key = str(site.get("indexnow_key", "")).strip()
    if not key:
        print("No indexnow_key in content/settings/site.yml — nothing to submit.",
              file=sys.stderr)
        return 1
    site_url = site["site_url"].rstrip("/")
    host = site_url.split("//", 1)[-1]
    key_location = f"{site_url}/{key}.txt"

    print(f"Checking the key file at {key_location}")
    try:
        published = fetch(key_location, timeout=20).decode().strip()
    except Exception as e:
        print(f"  ! not reachable ({e}). Deploy the site first — the engines "
              f"verify ownership by fetching this file.", file=sys.stderr)
        return 1
    if published != key:
        print(f"  ! the published key does not match site.yml", file=sys.stderr)
        return 1
    print("  ok")

    print(f"Reading {site_url}/sitemap.xml")
    urls = sitemap_urls(f"{site_url}/sitemap.xml", args.changed_since)
    if args.limit:
        urls = urls[:args.limit]
    if not urls:
        print("Nothing to submit.")
        return 0
    print(f"  {len(urls)} URLs"
          + (f" changed since {args.changed_since}" if args.changed_since else ""))

    if args.dry_run:
        for u in urls[:20]:
            print("   ", u)
        if len(urls) > 20:
            print(f"    … and {len(urls) - 20} more")
        return 0

    ok = True
    for i in range(0, len(urls), BATCH):
        batch = urls[i:i + BATCH]
        print(f"Submitting {i + 1}-{i + len(batch)}")
        ok = submit(host, key, key_location, batch) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
