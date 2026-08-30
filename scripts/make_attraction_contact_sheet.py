#!/usr/bin/env python3
"""Create a labelled contact sheet for manual attraction-photo QA.

The sheet is an audit artifact only; it never edits source media or content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "reports" / "attraction-image-classification.json"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    choices = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in choices:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def local_media(item: dict) -> Path:
    value = str(item.get("image") or "").removeprefix("/assets/")
    return ROOT / "static" / value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slugs", default="", help="Comma-separated attraction slugs")
    parser.add_argument("--output", default="reports/attraction-primary-contact-sheet.jpg")
    parser.add_argument("--all-items", action="store_true", help="Include gallery images too")
    args = parser.parse_args()

    wanted = {part.strip() for part in args.slugs.split(",") if part.strip()}
    rows = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    rows = [row for row in rows if not wanted or row["slug"] in wanted]

    tile_w, tile_h, image_h = 420, 300, 228
    cols = 4
    count = sum(len(row.get("items") or []) if args.all_items else 1 for row in rows)
    rows_count = max(1, (count + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * tile_w, rows_count * tile_h), "#f4f7f8")
    draw = ImageDraw.Draw(sheet)
    title_font = font(17, True)
    meta_font = font(13)

    index = 0
    for row in rows:
        items = row.get("items") or []
        if not args.all_items:
            items = items[:1]
        if not items:
            items = [{"slot": "primary", "image": "", "evidence": "missing"}]
        for item in items:
            x = (index % cols) * tile_w
            y = (index // cols) * tile_h
            image_path = local_media(item)
            # A blank or malformed media value can resolve to a directory.
            # Pillow can only open actual files, so treat every other path as
            # a missing audit slot instead of aborting the whole contact sheet.
            if image_path.is_file():
                with Image.open(image_path) as source:
                    photo = ImageOps.fit(source.convert("RGB"), (tile_w - 16, image_h - 8))
                sheet.paste(photo, (x + 8, y + 8))
            else:
                draw.rectangle((x + 8, y + 8, x + tile_w - 8, y + image_h), fill="#dfe7ea")
                draw.text((x + 24, y + 90), "MISSING IMAGE", font=title_font, fill="#8a2635")
            draw.text((x + 10, y + image_h + 6), row["slug"][:43], font=title_font, fill="#10252b")
            detail = f"{item.get('slot', '')} | {item.get('evidence', '')}"
            draw.text((x + 10, y + image_h + 32), detail, font=meta_font, fill="#5f7078")
            draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline="#c8d4d9", width=1)
            index += 1

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "JPEG", quality=88, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
