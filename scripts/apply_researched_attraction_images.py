#!/usr/bin/env python3
"""Apply manually verified Commons photos from the attraction research report."""

from __future__ import annotations

import argparse
import html
import json
import re
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
RESEARCH = json.loads((ROOT / "reports" / "photo-wave6-research.json").read_text(encoding="utf-8"))
SELECTIONS = json.loads(
    (ROOT / "reports" / "verified-attraction-gallery-selections.json").read_text(encoding="utf-8")
)


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value or "")).replace("\n", " ").strip()


def license_url(name: str) -> str:
    low = (name or "").lower()
    for label, url in (
        ("cc by-sa 4", "https://creativecommons.org/licenses/by-sa/4.0/"),
        ("cc by 4", "https://creativecommons.org/licenses/by/4.0/"),
        ("cc by-sa 3", "https://creativecommons.org/licenses/by-sa/3.0/"),
        ("cc by 3", "https://creativecommons.org/licenses/by/3.0/"),
        ("cc by-sa 2", "https://creativecommons.org/licenses/by-sa/2.0/"),
        ("cc by 2", "https://creativecommons.org/licenses/by/2.0/"),
    ):
        if label in low:
            return url
    return ""


def credit(candidate: dict) -> dict:
    return {
        "author": clean(candidate.get("artist", "")),
        "license": clean(candidate.get("license", "")),
        "license_url": license_url(candidate.get("license", "")),
        "source": candidate["page_url"],
    }


def gallery_entry(slug: str, position: int, candidate: dict) -> dict:
    return {"image": f"/assets/photos/{slug}-{position}.webp", **credit(candidate)}


def replace_sections(path: Path, gallery: list[dict], primary_credit: dict) -> None:
    text = path.read_text(encoding="utf-8")
    gallery_dump = yaml.safe_dump(
        {"gallery": gallery}, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    text, count = re.subn(
        r"gallery:(?: \[\])?\n.*?(?=visit_hours:)", gallery_dump + "\n", text, count=1, flags=re.S
    )
    if count != 1:
        raise RuntimeError(f"gallery section not found: {path}")
    credit_dump = yaml.safe_dump(
        {"image_credit": primary_credit}, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    text, count = re.subn(
        r"image_credit:\n.*?(?=rating:)", credit_dump + "\n", text, count=1, flags=re.S
    )
    if count != 1:
        raise RuntimeError(f"image_credit section not found: {path}")
    path.write_text(text, encoding="utf-8")


def download_webp(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url, headers={"User-Agent": "FleetHouseImageAudit/2.0 (rentup.ge; attraction verification)"}
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == 5:
                raise
            delay = 35 if isinstance(exc, urllib.error.HTTPError) and exc.code == 429 else 2 ** attempt
            time.sleep(delay)
    with Image.open(BytesIO(raw)) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        image.save(destination, "WEBP", quality=86, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Update metadata without downloads")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between Commons requests")
    args = parser.parse_args()

    applied = downloaded = 0
    for slug, selection in SELECTIONS.items():
        primary = RESEARCH[selection["primary"]]
        gallery_candidates = [RESEARCH[index] for index in selection["gallery"]]
        if primary["slug"] != slug or any(item["slug"] != slug for item in gallery_candidates):
            raise RuntimeError(f"Selection/slug mismatch for {slug}")

        targets = [(PHOTOS / f"{slug}.webp", primary)] + [
            (PHOTOS / f"{slug}-{position}.webp", candidate)
            for position, candidate in enumerate(gallery_candidates, start=1)
        ]
        if not args.offline:
            for destination, candidate in targets:
                download_webp(candidate["image_url"], destination)
                downloaded += 1
                time.sleep(args.delay)

        gallery = [
            gallery_entry(slug, position, candidate)
            for position, candidate in enumerate(gallery_candidates, start=1)
        ]
        replace_sections(CONTENT / f"{slug}.yml", gallery, credit(primary))
        applied += 1

    print(json.dumps({"places_applied": applied, "files_downloaded": downloaded}))


if __name__ == "__main__":
    main()
