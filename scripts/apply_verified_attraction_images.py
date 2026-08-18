#!/usr/bin/env python3
"""Keep only attraction photos supported by exact Wikimedia object evidence."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

import yaml
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "attractions"
PHOTOS = ROOT / "static" / "photos"
CLASSIFIED = json.loads((ROOT / "reports" / "attraction-image-classification.json").read_text(encoding="utf-8"))
CANDIDATES = json.loads((ROOT / "reports" / "attraction-image-candidates.json").read_text(encoding="utf-8"))
SELECTIONS = json.loads((ROOT / "reports" / "verified-image-selections.json").read_text(encoding="utf-8"))
BY_CANDIDATE = {row["slug"]: {c["title"]: c for c in row["candidates"]} for row in CANDIDATES}
BY_CLASSIFIED = {row["slug"]: row for row in CLASSIFIED}


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value or "")).replace("\n", " ").strip()


def license_url(name: str) -> str:
    low = (name or "").lower()
    if "cc by-sa 4" in low:
        return "https://creativecommons.org/licenses/by-sa/4.0"
    if "cc by 4" in low:
        return "https://creativecommons.org/licenses/by/4.0"
    if "cc by-sa 3" in low:
        return "https://creativecommons.org/licenses/by-sa/3.0"
    if "cc by 3" in low:
        return "https://creativecommons.org/licenses/by/3.0"
    if "cc by-sa 2" in low:
        return "https://creativecommons.org/licenses/by-sa/2.0"
    if "cc by 2" in low:
        return "https://creativecommons.org/licenses/by/2.0"
    return ""


def credit_block(author: str, license_name: str, source: str) -> str:
    payload = {
        "author": clean(author), "license": clean(license_name),
        "license_url": license_url(license_name), "source": source,
    }
    block = yaml.safe_dump({"image_credit": payload}, allow_unicode=True, sort_keys=False, width=1000)
    return block.rstrip()


def replace_sections(path: Path, gallery: list[dict], credit: str) -> None:
    text = path.read_text(encoding="utf-8")
    gallery_dump = yaml.safe_dump({"gallery": gallery}, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    text, count = re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)", gallery_dump + "\n", text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"gallery section not found: {path}")
    text, count = re.subn(r"image_credit:\n(?:  [^\n]*\n){4}", credit + "\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"image_credit section not found: {path}")
    path.write_text(text, encoding="utf-8")


def download_webp(url: str, destination: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "FleetHouseImageAudit/1.0 (rentup.ge)"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                raw = response.read()
            break
        except urllib.error.HTTPError as exc:
            if attempt == 4:
                raise
            time.sleep(35 if exc.code == 429 else 2 ** attempt)
    else:
        raise RuntimeError(f"Could not download {url}")
    with Image.open(BytesIO(raw)) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        if image.width > 1600:
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        image.save(destination, "WEBP", quality=86, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Do not download selected replacements")
    args = parser.parse_args()
    promoted = downloaded = removed = 0
    for slug, audit in BY_CLASSIFIED.items():
        path = CONTENT / f"{slug}.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        gallery_by_source = {g.get("source"): g for g in data.get("gallery") or []}
        exact = [i for i in audit["items"] if i.get("evidence") == "exact-name"]
        primary = next((i for i in exact if i["slot"] == "primary"), None)
        selected = SELECTIONS.get(slug)
        if selected:
            candidate = BY_CANDIDATE[slug][selected]
            already_selected = (data.get("image_credit") or {}).get("source") == candidate["page_url"]
            if not already_selected and args.offline:
                continue
            if not already_selected:
                download_webp(candidate["image_url"], PHOTOS / f"{slug}.webp")
                time.sleep(2)
            primary = {
                "source": candidate["page_url"],
                "metadata": {"artist": candidate["artist"], "license": candidate["license"]},
            }
            downloaded += 1
        elif not primary:
            promote = next((i for i in exact if i["slot"].startswith("gallery-")), None)
            if promote:
                shutil.copyfile(ROOT / "static" / promote["image"].removeprefix("/assets/"), PHOTOS / f"{slug}.webp")
                primary = promote
                promoted += 1

        safe_gallery = []
        for item in exact:
            if item["slot"] == "primary":
                continue
            original = gallery_by_source.get(item["source"])
            if original:
                safe_gallery.append(original)
        removed += max(0, len(data.get("gallery") or []) - len(safe_gallery))

        if primary:
            md = primary.get("metadata") or {}
            credit = credit_block(md.get("artist", ""), md.get("license", ""), primary.get("source", ""))
            replace_sections(path, safe_gallery, credit)

    print(json.dumps({"downloaded": downloaded, "promoted": promoted, "removed_gallery_items": removed}))


if __name__ == "__main__":
    main()
