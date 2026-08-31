#!/usr/bin/env python3
"""Parallel wrapper for refreshing every Commons-backed attraction image."""
from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

from refresh_commons_media import ROOT, download, original_url, save_webp, title_from_source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--report", default="reports/all-commons-media-refresh.json")
    args = parser.parse_args()
    jobs = []
    for path in sorted((ROOT / "content" / "attractions").glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        media = []
        if data.get("image"):
            media.append((data["image"], (data.get("image_credit") or {}).get("source", "")))
        media.extend((item.get("image", ""), item.get("source", "")) for item in data.get("gallery") or [])
        for image_ref, source in media:
            title = title_from_source(source)
            if title and image_ref.startswith("/assets/photos/"):
                jobs.append((path.stem, image_ref, source, title))

    lock = threading.Lock()
    completed = 0

    def refresh(job: tuple[str, str, str, str]) -> dict:
        nonlocal completed
        slug, image_ref, source, title = job
        row = {"slug": slug, "image": image_ref, "source": source, "title": title}
        try:
            destination = ROOT / "static" / image_ref.removeprefix("/assets/")
            destination.parent.mkdir(parents=True, exist_ok=True)
            row["size"] = save_webp(download(original_url(title)), destination)
            row["bytes"] = destination.stat().st_size
            row["status"] = "refreshed"
        except Exception as exc:
            row["status"] = "error"
            row["error"] = str(exc)
        with lock:
            completed += 1
            if completed % 50 == 0 or completed == len(jobs):
                print(f"progress {completed}/{len(jobs)}", flush=True)
        time.sleep(0.05)
        return row

    rows = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(refresh, job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: (row["slug"], row["image"]))
    output = ROOT / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"items": len(rows), "refreshed": sum(r["status"] == "refreshed" for r in rows),
                      "errors": sum(r["status"] == "error" for r in rows), "report": str(output)}))


if __name__ == "__main__":
    main()
