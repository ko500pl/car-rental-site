#!/usr/bin/env python3
"""Find Wikimedia Commons candidates for attractions without exact evidence."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED = ROOT / "reports" / "attraction-image-classification.json"
OUT = ROOT / "reports" / "attraction-image-candidates.json"
API = "https://commons.wikimedia.org/w/api.php"


def request(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    req = urllib.request.Request(url, headers={"User-Agent": "FleetHouseImageAudit/1.0 (rentup.ge)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:
            if attempt == 3:
                raise
            time.sleep(30 if exc.code == 429 else 2 ** attempt)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    return {}


def search(query: str) -> list[dict]:
    data = request({
        "action": "query", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": query, "gsrlimit": 8,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 900,
    })
    out = []
    for page in data.get("query", {}).get("pages", []):
        ii = (page.get("imageinfo") or [{}])[0]
        ext = ii.get("extmetadata") or {}
        val = lambda key: (ext.get(key) or {}).get("value", "")
        out.append({
            "title": page.get("title"), "page_url": ii.get("descriptionurl"),
            "image_url": ii.get("thumburl") or ii.get("url"),
            "description": val("ImageDescription"), "categories": val("Categories"),
            "license": val("LicenseShortName"), "artist": val("Artist"),
        })
    return out


def main() -> None:
    rows = json.loads(CLASSIFIED.read_text(encoding="utf-8"))
    missing = [p for p in rows if not any(i.get("verified_exact") for i in p.get("items", []))]
    results = []
    for idx, place in enumerate(missing, 1):
        query = f'"{place["name"]}" Georgia'
        results.append({"slug": place["slug"], "name": place["name"], "query": query,
                        "candidates": search(query)})
        OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{idx}/{len(missing)} {place['slug']}", flush=True)
        time.sleep(2)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
