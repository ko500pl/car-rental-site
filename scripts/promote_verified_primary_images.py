#!/usr/bin/env python3
"""Promote an exact, open-license gallery image to an attraction's primary image.

The allowlist is intentionally conservative: every entry was manually reviewed in
the image audit.  The script never downloads media and never removes gallery
images.  Run without --apply to preview the changes.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "attractions"
REPORT = ROOT / "reports" / "attraction-image-classification.json"

# Current primary is demonstrably another object, while an exact-name Commons
# image is already present locally in the attraction's gallery.
SAFE_SLUGS = {
    "abano-pass",
    "ajameti-managed-reserve",
    "balda-canyon",
    "barakoni-church",
    "batumi-botanical-garden",
    "bazaleti-lake",
    "birtvisi-fortress",
    "bolnisi-sioni",
    "dartlo",
    "gombori-pass",
    "khikhani-fortress",
    "koruldi-lakes",
    "likani-palace",
    "martvili-canyon",
    "motsameta-monastery",
    "mount-khvamli",
    "nabeghlavi",
    "navenakhevi-cave",
    "nokalakevi",
    "oni-synagogue",
    "rkoni-monastery",
    "sairme-resort",
    "samtavisi-cathedral",
    "sataplia-nature-reserve",
    "shiomghvime-monastery",
    "sno-valley",
    "vani-archaeological-museum",
    "vanis-kvabebi",
}


def license_url(name: str) -> str:
    low = (name or "").lower()
    for version in ("4.0", "3.0", "2.5", "2.0"):
        if f"cc by-sa {version}" in low:
            return f"https://creativecommons.org/licenses/by-sa/{version}"
        if f"cc by {version}" in low:
            return f"https://creativecommons.org/licenses/by/{version}"
    if "public domain" in low or low in {"pd", "cc0"}:
        return "https://creativecommons.org/publicdomain/mark/1.0/"
    return ""


def replace_primary(path: Path, image: str, metadata: dict, source: str) -> bool:
    text = path.read_text(encoding="utf-8")
    current = yaml.safe_load(text) or {}
    if current.get("image") == image and (current.get("image_credit") or {}).get("source") == source:
        return False

    text, image_count = re.subn(r"^image:.*$", f"image: {image}", text, count=1, flags=re.M)
    if image_count != 1:
        raise RuntimeError(f"Primary image field not found: {path}")

    credit = {
        "author": metadata.get("artist") or "",
        "license": metadata.get("license") or "",
        "license_url": license_url(metadata.get("license") or ""),
        "source": source,
    }
    dumped = yaml.safe_dump(
        {"image_credit": credit}, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    text, credit_count = re.subn(
        r"^image_credit:\n(?:  .*\n?)*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z)",
        dumped + "\n",
        text,
        count=1,
        flags=re.M,
    )
    if credit_count != 1:
        raise RuntimeError(f"Image credit block not found: {path}")
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows = json.loads(REPORT.read_text(encoding="utf-8"))
    by_slug = {row["slug"]: row for row in rows}
    plan: list[dict] = []
    for slug in sorted(SAFE_SLUGS):
        audit = by_slug.get(slug)
        if not audit:
            raise RuntimeError(f"Missing audit row: {slug}")
        exact_gallery = [
            item
            for item in audit["items"]
            if item.get("evidence") == "exact-name" and item.get("slot", "").startswith("gallery-")
        ]
        if not exact_gallery:
            raise RuntimeError(f"No exact-name gallery image: {slug}")
        chosen = exact_gallery[0]
        local_path = ROOT / "static" / chosen["image"].removeprefix("/assets/")
        if not local_path.exists():
            raise RuntimeError(f"Missing local media: {local_path}")
        entry = {
            "slug": slug,
            "image": chosen["image"],
            "source": chosen["source"],
            "applied": False,
        }
        if args.apply:
            entry["applied"] = replace_primary(
                CONTENT / f"{slug}.yml",
                chosen["image"],
                chosen.get("metadata") or {},
                chosen["source"],
            )
        plan.append(entry)

    print(json.dumps({"apply": args.apply, "count": len(plan), "items": plan}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
