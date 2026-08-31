#!/usr/bin/env python3
"""Retry Commons media not refreshed after a given timestamp."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import yaml

from refresh_commons_media import ROOT, download, original_url, save_webp, title_from_source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--after", required=True, help="ISO local timestamp")
    parser.add_argument("--report", default="reports/stale-commons-media-retry.json")
    args = parser.parse_args()
    cutoff = datetime.fromisoformat(args.after).timestamp()
    jobs = []
    for path in sorted((ROOT / "content" / "attractions").glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        media = []
        if data.get("image"):
            media.append((data["image"], (data.get("image_credit") or {}).get("source", "")))
        media.extend((item.get("image", ""), item.get("source", "")) for item in data.get("gallery") or [])
        for image_ref, source in media:
            title = title_from_source(source)
            destination = ROOT / "static" / image_ref.removeprefix("/assets/")
            if title and image_ref.startswith("/assets/photos/") and (
                not destination.exists() or destination.stat().st_mtime < cutoff
            ):
                jobs.append((path.stem, image_ref, source, title, destination))
    rows = []
    for index, (slug, image_ref, source, title, destination) in enumerate(jobs, 1):
        row = {"slug": slug, "image": image_ref, "source": source, "title": title}
        try:
            row["size"] = save_webp(download(original_url(title)), destination)
            row["bytes"] = destination.stat().st_size
            row["status"] = "refreshed"
        except Exception as exc:
            row["status"] = "error"
            row["error"] = str(exc)
        rows.append(row)
        if index % 25 == 0 or index == len(jobs):
            print(f"progress {index}/{len(jobs)}", flush=True)
        time.sleep(0.8)
    output = ROOT / args.report
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"items": len(rows), "refreshed": sum(r["status"] == "refreshed" for r in rows),
                      "errors": sum(r["status"] == "error" for r in rows), "report": str(output)}))


if __name__ == "__main__":
    main()
