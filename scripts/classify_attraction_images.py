#!/usr/bin/env python3
"""Classify attraction photos using exact Commons metadata evidence.

This intentionally uses a conservative rule: an image is only considered an
exact match when the attraction name (or a substantial name token sequence)
appears in Wikimedia's title, description, object name, or categories.
Coordinates are supporting evidence, never sufficient on their own.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports" / "attraction-image-audit.json"
OUT = ROOT / "reports" / "attraction-image-classification.json"

STOP = {
    "the", "of", "and", "in", "at", "on", "a", "an", "georgia", "georgian",
    "church", "monastery", "cathedral", "fortress", "museum", "bridge", "lake",
    "park", "canyon", "waterfall", "reserve", "complex", "tower", "palace",
    "house", "national", "historic", "historical", "site", "old", "great",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def meaningful_tokens(value: str) -> list[str]:
    return [t for t in norm(value).split() if len(t) >= 4 and t not in STOP]


def classify(place: dict, item: dict) -> dict:
    md = item.get("metadata") or {}
    hay = norm(" ".join(str(md.get(k) or "") for k in ("description", "categories", "object_name")))
    title = norm(item.get("commons_title") or "")
    name = norm(place.get("name") or "")
    slug = norm((place.get("slug") or "").replace("-", " "))
    variants = {v for v in (name, slug) if len(v) >= 4}
    tokens = sorted(set(meaningful_tokens(name) + meaningful_tokens(slug)), key=len, reverse=True)
    exact_phrase = any(v in hay or v in title for v in variants)
    matched = [t for t in tokens if t in hay or t in title]
    # A distinctive long token is strong evidence; otherwise require two tokens.
    token_evidence = any(len(t) >= 7 for t in matched) or len(matched) >= 2
    supported = bool(exact_phrase or token_evidence)
    return {
        **item,
        "verified_exact": supported,
        "evidence": "exact-name" if exact_phrase else ("name-token" if token_evidence else "none"),
        "matched_tokens": matched,
    }


def main() -> None:
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    result = []
    for place in rows:
        items = [classify(place, i) for i in place.get("items", [])]
        result.append({**{k: v for k, v in place.items() if k != "items"}, "items": items})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    exact = sum(i["verified_exact"] for p in result for i in p["items"])
    have = sum(any(i["verified_exact"] for i in p["items"]) for p in result)
    prim = sum(bool(p["items"] and p["items"][0]["verified_exact"]) for p in result)
    print(json.dumps({"places": len(result), "images": sum(len(p['items']) for p in result),
                      "verified_images": exact, "places_with_verified_image": have,
                      "verified_primary": prim}, ensure_ascii=False))


if __name__ == "__main__":
    main()
