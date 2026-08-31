#!/usr/bin/env python3
"""Refresh local attraction media from its declared Wikimedia Commons source.

This repairs the dangerous case where YAML credit points at the right object but
the local image file contains unrelated pixels. Only Commons-backed media are
touched; site-owned and AI-assisted assets are left unchanged.
"""
from __future__ import annotations

import argparse
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
API = "https://commons.wikimedia.org/w/api.php"
UA = "DriveOnCommonsMediaRefresh/1.0 (https://rentup.ge)"


def title_from_source(source: str) -> str:
    if "/wiki/File:" not in source:
        return ""
    return "File:" + urllib.parse.unquote(source.split("/wiki/File:", 1)[1]).replace("_", " ")


def original_url(title: str) -> str:
    query = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title,
                                    "prop": "imageinfo", "iiprop": "url|mime"})
    req = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        page = next(iter(json.load(response)["query"]["pages"].values()))
    info = page["imageinfo"][0]
    if not info.get("mime", "").startswith("image/"):
        raise ValueError(f"Not an image: {title}")
    return info["url"]


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.read()
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


def save_webp(raw: bytes, destination: Path) -> tuple[int, int]:
    with Image.open(io.BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((1800, 1400), Image.Resampling.LANCZOS)
        temporary = destination.with_suffix(destination.suffix + ".part")
        image.save(temporary, "WEBP", quality=88, method=6)
        temporary.replace(destination)
        return image.size


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", action="append")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", default="reports/commons-media-refresh.json")
    args = parser.parse_args()
    wanted = set(args.slug or [])
    rows = []
    for path in sorted((ROOT / "content" / "attractions").glob("*.yml")):
        if wanted and path.stem not in wanted:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        media = []
        if data.get("image"):
            media.append((data["image"], (data.get("image_credit") or {}).get("source", "")))
        media.extend((item.get("image", ""), item.get("source", "")) for item in data.get("gallery") or [])
        for image_ref, source in media:
            title = title_from_source(source)
            if not title or not image_ref.startswith("/assets/photos/"):
                continue
            row = {"slug": path.stem, "image": image_ref, "source": source, "title": title, "status": "validated"}
            try:
                url = original_url(title)
                if args.apply:
                    destination = ROOT / "static" / image_ref.removeprefix("/assets/")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    row["size"] = save_webp(download(url), destination)
                    row["bytes"] = destination.stat().st_size
                    row["status"] = "refreshed"
            except Exception as exc:
                row["status"] = "error"
                row["error"] = str(exc)
            rows.append(row)
            time.sleep(0.12)
    output = ROOT / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"items": len(rows), "refreshed": sum(r["status"] == "refreshed" for r in rows),
                      "errors": sum(r["status"] == "error" for r in rows), "report": str(output)}))


if __name__ == "__main__":
    main()
