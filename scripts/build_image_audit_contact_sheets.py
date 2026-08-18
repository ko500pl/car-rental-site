#!/usr/bin/env python3
"""Build labeled contact sheets for attraction photos changed in the worktree."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "contact-sheets"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.all:
        paths = []
        for yml in sorted((ROOT / "content" / "attractions").glob("*.yml")):
            import yaml
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
            value = str(data.get("image") or "").removeprefix("/assets/")
            if value and not value.startswith(("http://", "https://")):
                paths.append(ROOT / "static" / value)
    else:
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "--", "static/photos"], cwd=ROOT, text=True
        ).splitlines()
        paths = [ROOT / p for p in changed if p.lower().endswith((".webp", ".jpg", ".png"))]
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=16)
    for page, start in enumerate(range(0, len(paths), 20), 1):
        canvas = Image.new("RGB", (1600, 1000), "#eceff1")
        draw = ImageDraw.Draw(canvas)
        for idx, path in enumerate(paths[start:start + 20]):
            x = (idx % 4) * 400
            y = (idx // 4) * 200
            with Image.open(path) as image:
                thumb = ImageOps.fit(image.convert("RGB"), (380, 155), method=Image.Resampling.LANCZOS)
            canvas.paste(thumb, (x + 10, y + 8))
            draw.rectangle((x + 10, y + 163, x + 390, y + 193), fill="#ffffff")
            draw.text((x + 18, y + 169), path.stem, fill="#10202a", font=font)
        prefix = "all-attractions" if args.all else "changed-attractions"
        canvas.save(OUT / f"{prefix}-{page}.jpg", quality=90)
    print(f"{len(paths)} photos -> {OUT}")


if __name__ == "__main__":
    main()
