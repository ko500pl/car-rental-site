#!/usr/bin/env python3
"""Export the public fleet as CSV for rental aggregators (Localrent, DiscoverCars).

Usage: python scripts/export_fleet.py localrent|discovercars
Writes exports/fleet-<platform>.csv (UTF-8 with BOM, opens cleanly in Excel).
When a partner sends its own template, change the header labels in COLUMNS —
one line per column; our keys on the left never change.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
KEYS = ("slug", "name_en", "category", "years", "engine", "transmission", "drive", "seats",
        "luggage", "deposit_gel", "price_1_6_gel", "price_7_29_gel", "price_30_gel",
        "excess_gel", "min_age", "mileage")
COLUMNS = {
    "localrent": {k: k for k in KEYS},
    "discovercars": {k: k for k in KEYS},
}
TIER_ORDER = {"economy": 0, "suv": 1, "business": 2, "offroad": 3, "minivan": 4, "van": 5}
INT_FIELDS = {"deposit": "deposit_gel", "price_1_6": "price_1_6_gel",
              "price_7_29": "price_7_29_gel", "price_30": "price_30_gel"}


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _public_cars() -> dict:
    cars = {}
    for f in sorted((ROOT / "content/cars").glob("*.yml")):
        d = _yaml(f)
        if d.get("status") in (None, "published") and not d.get("draft", False):
            cars[f.stem] = d
    return cars


def _int_or_none(value):
    s = str(value if value is not None else "").replace(" ", "").replace(" ", "")
    return int(s) if s.isdigit() else None


def fleet_rows(cars: dict | None = None) -> tuple[list[dict], list[str]]:
    policy = _yaml(ROOT / "content/settings/rental_policy.yml")
    ages = policy.get("min_driver_age_by_category") or {}
    excess = (policy.get("insurance") or {}).get("excess_gel_by_category") or {}
    mileage = "unlimited" if (policy.get("mileage") or {}).get("unlimited") else "limited"
    cars = _public_cars() if cars is None else cars
    rows, warnings = [], []
    for slug, c in cars.items():
        cat = c.get("category", "")
        row = {"slug": slug, "name_en": (c.get("en") or {}).get("name", slug), "category": cat,
               "years": c.get("years", ""), "engine": c.get("engine", ""),
               "transmission": c.get("transmission", ""), "drive": c.get("drive", ""),
               "seats": c.get("seats", ""), "luggage": c.get("luggage", ""),
               "excess_gel": excess.get(cat), "min_age": ages.get(cat), "mileage": mileage}
        for src, key in INT_FIELDS.items():
            row[key] = _int_or_none(c.get(src))
            if row[key] is None:
                warnings.append(f"{slug}: {src} is blank or not a whole number ({c.get(src)!r})")
        for key in ("excess_gel", "min_age"):
            if row[key] is None:
                warnings.append(f"{slug}: no {key} for category {cat!r} in rental_policy.yml")
        rows.append(row)
    rows.sort(key=lambda r: (TIER_ORDER.get(r["category"], 99), r["price_1_6_gel"] or 0, r["slug"]))
    return rows, warnings


def write_csv(platform: str, out: Path) -> Path:
    if platform not in COLUMNS:
        raise ValueError(f"unknown platform {platform!r}; expected one of {sorted(COLUMNS)}")
    rows, _ = fleet_rows()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"fleet-{platform}.csv"
    labels = COLUMNS[platform]
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([labels[k] for k in KEYS])
        for r in rows:
            w.writerow(["" if r[k] is None else r[k] for k in KEYS])
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = write_csv(sys.argv[1], ROOT / "exports")
    rows, warnings = fleet_rows()
    for w in warnings:
        print("WARNING:", w)
    print(f"{path.relative_to(ROOT)}: {len(rows)} rows, {len(warnings)} warnings")
