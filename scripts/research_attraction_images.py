#!/usr/bin/env python3
"""Research and visually review exact Wikimedia Commons images for attractions.

The script is intentionally conservative: it searches using explicit object names,
keeps only reusable raster images, downloads small previews, and produces both a
JSON evidence file and a labelled contact sheet. It does not modify content.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "attractions"
REPORTS = ROOT / "reports"
CACHE = REPORTS / "image-research-cache"
API = "https://commons.wikimedia.org/w/api.php"
ALLOWED_LICENSES = ("cc by", "cc-by", "public domain", "cc0")

QUERY_OVERRIDES = {
    "georgian-national-museum": ["Georgian National Museum Tbilisi", "Simon Janashia Museum"],
    "open-air-museum-of-ethnography": ["Tbilisi Open Air Museum of Ethnography", "Tbilisi Ethnographic Museum"],
    "petra-fortress": ["Petra Fortress Tsikhisdziri Georgia", "Tsikhisdziri Petra Georgia"],
    "mtatsminda-park": ["Mtatsminda Park Tbilisi", "Mtatsminda funicular park"],
    "rustaveli-avenue": ["Rustaveli Avenue Tbilisi"],
    "svaneti-museum-mestia": ["Svaneti Museum Mestia", "Svaneti Museum of History and Ethnography"],
    "hatsvali-tetnuldi": ["Hatsvali ski resort", "Tetnuldi ski resort"],
    "kintrishi-protected-areas": ["Kintrishi Protected Areas Georgia", "Kintrishi Nature Reserve"],
    "nunisi-resort": ["Nunisi resort Georgia", "Nunisi Borjomi"],
    "batsara-reserve": ["Batsara Nature Reserve Georgia", "Batsara-Babaneuri"],
    "utsera": ["Utsera Racha Georgia"],
    "chiora": ["Chiora Racha Georgia", "Chiora Oni Georgia"],
}


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value or "")).replace("\n", " ").strip()


def request(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    req = urllib.request.Request(url, headers={"User-Agent": "FleetHouseImageAudit/1.0 (rentup.ge)"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if attempt == 4:
                raise
            time.sleep(35 if exc.code == 429 else 2 ** attempt)
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    return {}


def search(query: str, limit: int) -> list[dict]:
    data = request({
        "action": "query", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": query, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 700,
    })
    rows = []
    for page in data.get("query", {}).get("pages", []):
        info = (page.get("imageinfo") or [{}])[0]
        ext = info.get("extmetadata") or {}
        val = lambda key: clean((ext.get(key) or {}).get("value", ""))
        license_name = val("LicenseShortName")
        mime = info.get("mime", "")
        if not mime.startswith("image/") or mime in {"image/svg+xml", "image/gif"}:
            continue
        if license_name and not any(token in license_name.lower() for token in ALLOWED_LICENSES):
            continue
        rows.append({
            "title": page.get("title", ""), "query": query,
            "page_url": info.get("descriptionurl", ""),
            "image_url": info.get("thumburl") or info.get("url", ""),
            "original_url": info.get("url", ""),
            "width": info.get("width"), "height": info.get("height"),
            "description": val("ImageDescription"), "categories": val("Categories"),
            "license": license_name, "artist": val("Artist"),
        })
    return rows


def download(url: str, path: Path) -> None:
    if path.is_file() and path.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "FleetHouseImageAudit/1.0 (rentup.ge)"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                path.write_bytes(response.read())
            time.sleep(1.5)
            return
        except urllib.error.HTTPError as exc:
            if attempt == 5:
                raise
            time.sleep(40 if exc.code == 429 else 2 ** attempt)
        except Exception:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)


def contact_sheet(rows: list[dict], path: Path) -> None:
    cell_w, image_h, label_h, cols = 360, 230, 82, 4
    cell_h = image_h + label_h
    sheet = Image.new("RGB", (cell_w * cols, cell_h * ((len(rows) + cols - 1) // cols)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, row in enumerate(rows):
        x, y = (idx % cols) * cell_w, (idx // cols) * cell_h
        cache_key = hashlib.sha1(row["page_url"].encode("utf-8")).hexdigest()[:16]
        cache_path = CACHE / f"{cache_key}.jpg"
        try:
            download(row["image_url"], cache_path)
            with Image.open(cache_path) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((cell_w - 8, image_h - 8), Image.Resampling.LANCZOS)
                sheet.paste(image, (x + (cell_w - image.width) // 2, y + 4))
        except Exception as exc:
            row["preview_error"] = str(exc)
        label = f'{idx:03d} {row["slug"]}\n{row["title"]}'
        draw.multiline_text((x + 5, y + image_h + 3), label[:180], fill="black", font=font, spacing=2)
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#cbd5e1")
    sheet.save(path, "JPEG", quality=82, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slugs", required=True, help="Comma-separated attraction slugs")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--output-prefix", default="photo-research")
    args = parser.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    seen: set[str] = set()
    for slug in [item.strip() for item in args.slugs.split(",") if item.strip()]:
        path = CONTENT / f"{slug}.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        queries = QUERY_OVERRIDES.get(slug) or [f'{(data.get("en") or {}).get("name", slug)} Georgia']
        for query in queries:
            for row in search(query, args.limit):
                if row["page_url"] in seen:
                    continue
                seen.add(row["page_url"])
                row["slug"] = slug
                all_rows.append(row)
            time.sleep(1.5)

    json_path = REPORTS / f"{args.output_prefix}.json"
    sheet_path = REPORTS / f"{args.output_prefix}.jpg"
    json_path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    contact_sheet(all_rows, sheet_path)
    json_path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidates": len(all_rows), "json": str(json_path), "sheet": str(sheet_path)}))


if __name__ == "__main__":
    main()
