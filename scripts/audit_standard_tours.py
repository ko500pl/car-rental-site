#!/usr/bin/env python3
"""Audit standard tours for coverage, references, metadata, and route plausibility."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "content" / "routes"
ATTRACTIONS = ROOT / "content" / "attractions"
LANGUAGES = ("ka", "en", "ru", "fa", "he", "ar")
REGION_TARGETS = {
    "adjara": 5,
    "guria": 4,
    "imereti": 6,
    "kakheti": 6,
    "kvemo-kartli": 4,
    "mtskheta-mtianeti": 6,
    "racha-lechkhumi": 5,
    "samegrelo-zemo-svaneti": 6,
    "samtskhe-javakheti": 6,
    "shida-kartli": 5,
    "tbilisi": 5,
}
PURPOSE_TARGETS = {
    "beach": 2,
    "classic": 2,
    "culinary": 4,
    "culture": 4,
    "cycling": 3,
    "family": 4,
    "hiking": 5,
    "history": 5,
    "mountains": 3,
    "nature": 5,
    "performance": 2,
    "spa": 2,
    "wine": 3,
}
DURATION_TARGETS = {"1 day": 10, "2 days": 10, "3 days": 8, "4 days": 5, "5 days": 4}


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    radius = 6371.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def attraction_index() -> dict[str, dict]:
    records = {}
    for path in sorted(ATTRACTIONS.glob("*.yml")):
        data = load_yaml(path)
        records[path.stem] = {
            "region": data.get("region", "unknown"),
            "type": data.get("type", "unknown"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "rating": data.get("rating"),
            "name": (data.get("ka") or {}).get("name", path.stem),
        }
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="reports/standard-tour-audit.json")
    parser.add_argument("--markdown", default="reports/STANDARD_TOUR_AUDIT.md")
    args = parser.parse_args()

    attractions = attraction_index()
    rows = []
    purpose_counts: Counter[str] = Counter()
    duration_counts: Counter[str] = Counter()
    region_counts: Counter[str] = Counter()
    vehicle_counts: Counter[str] = Counter()
    waypoint_sets: defaultdict[tuple[str, ...], list[str]] = defaultdict(list)

    for path in sorted(ROUTES.glob("*.yml")):
        data = load_yaml(path)
        waypoints = [str(v) for v in data.get("waypoints") or []]
        missing = [slug for slug in waypoints if slug not in attractions]
        known = [attractions[slug] for slug in waypoints if slug in attractions]
        regions = Counter(item["region"] for item in known)
        types = Counter(item["type"] for item in known)
        days = int(data.get("days") or 0)
        purpose = str(data.get("purpose") or "unspecified")
        vehicle = str(data.get("car_category") or "unspecified")
        duration_bucket = "1 day" if days == 1 else f"{days} days"
        purpose_counts[purpose] += 1
        duration_counts[duration_bucket] += 1
        vehicle_counts[vehicle] += 1
        for region in regions:
            region_counts[region] += 1
        waypoint_sets[tuple(sorted(waypoints))].append(path.stem)

        coords = [(float(item["lat"]), float(item["lon"])) for item in known if item["lat"] is not None and item["lon"] is not None]
        origin = data.get("origin") or {}
        if origin.get("lat") is not None and origin.get("lon") is not None:
            coords.insert(0, (float(origin["lat"]), float(origin["lon"])))
        straight_chain = round(sum(haversine_km(a, b) for a, b in zip(coords, coords[1:])), 1)
        stated_distance = float(data.get("distance_km") or 0)
        ratio = round(stated_distance / straight_chain, 2) if straight_chain else None

        issues = []
        if missing:
            issues.append({"severity": "error", "code": "missing-waypoint", "detail": ", ".join(missing)})
        if len(waypoints) < 2:
            issues.append({"severity": "error", "code": "too-few-waypoints", "detail": str(len(waypoints))})
        if days < 1:
            issues.append({"severity": "error", "code": "invalid-days", "detail": str(days)})
        if not data.get("daily_hours"):
            issues.append({"severity": "warning", "code": "missing-daily-hours", "detail": ""})
        if not origin:
            issues.append({"severity": "warning", "code": "missing-origin", "detail": ""})
        if not data.get("sources"):
            issues.append({"severity": "warning", "code": "missing-sources", "detail": ""})
        if stated_distance and straight_chain and ratio is not None and ratio < 1:
            issues.append({"severity": "warning", "code": "distance-under-straight-line", "detail": f"ratio={ratio}"})
        if days and len(waypoints) > days * 8:
            issues.append({"severity": "warning", "code": "dense-itinerary", "detail": f"{len(waypoints)} stops/{days} days"})
        for lang in LANGUAGES:
            block = data.get(lang) or {}
            missing_fields = [field for field in ("name", "short", "body", "plan") if not block.get(field)]
            if missing_fields:
                issues.append({"severity": "warning", "code": f"missing-{lang}", "detail": ", ".join(missing_fields)})

        rows.append({
            "slug": path.stem,
            "name": (data.get("ka") or {}).get("name", path.stem),
            "status": data.get("status"),
            "days": days,
            "purpose": purpose,
            "vehicle": vehicle,
            "daily_hours": data.get("daily_hours"),
            "waypoint_count": len(waypoints),
            "waypoints": waypoints,
            "regions": dict(regions),
            "types": dict(types),
            "stated_distance_km": stated_distance,
            "straight_chain_km": straight_chain,
            "distance_ratio": ratio,
            "source_count": len(data.get("sources") or []),
            "issues": issues,
        })

    duplicates = [{"routes": values, "waypoints": list(key)} for key, values in waypoint_sets.items() if len(values) > 1]
    issue_counts = Counter(issue["code"] for row in rows for issue in row["issues"])
    error_count = sum(issue["severity"] == "error" for row in rows for issue in row["issues"])
    warning_count = sum(issue["severity"] == "warning" for row in rows for issue in row["issues"])
    payload = {
        "generated_on": date.today().isoformat(),
        "summary": {"routes": len(rows), "errors": error_count, "warnings": warning_count, "duplicates": len(duplicates)},
        "coverage": {
            "purposes": dict(sorted(purpose_counts.items())),
            "durations": dict(sorted(duration_counts.items())),
            "vehicles": dict(sorted(vehicle_counts.items())),
            "regions": dict(sorted(region_counts.items())),
        },
        "coverage_gaps": {
            "regions": {
                key: {"current": region_counts.get(key, 0), "target": target, "missing": max(0, target - region_counts.get(key, 0))}
                for key, target in REGION_TARGETS.items()
                if region_counts.get(key, 0) < target
            },
            "purposes": {
                key: {"current": purpose_counts.get(key, 0), "target": target, "missing": max(0, target - purpose_counts.get(key, 0))}
                for key, target in PURPOSE_TARGETS.items()
                if purpose_counts.get(key, 0) < target
            },
            "durations": {
                key: {"current": duration_counts.get(key, 0), "target": target, "missing": max(0, target - duration_counts.get(key, 0))}
                for key, target in DURATION_TARGETS.items()
                if duration_counts.get(key, 0) < target
            },
        },
        "issue_codes": dict(sorted(issue_counts.items())),
        "duplicates": duplicates,
        "routes": rows,
    }
    json_path = ROOT / args.json
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Standard Tour Audit",
        "",
        f"Generated: {payload['generated_on']}",
        "",
        "## Summary",
        "",
        f"- Tours: **{len(rows)}**",
        f"- Errors: **{error_count}**",
        f"- Warnings: **{warning_count}**",
        f"- Duplicate waypoint sets: **{len(duplicates)}**",
        "",
        "## Coverage",
        "",
        "### Regions",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(region_counts.items()))
    lines.extend(["", "### Purposes", ""])
    lines.extend(f"- {key}: {value}" for key, value in sorted(purpose_counts.items()))
    lines.extend(["", "### Durations", ""])
    lines.extend(f"- {key}: {value}" for key, value in sorted(duration_counts.items()))
    lines.extend(["", "## Coverage gaps", "", "Targets are editorial minimums for a balanced first release, not arbitrary route quotas.", "", "### Regions below target", ""])
    if payload["coverage_gaps"]["regions"]:
        lines.extend(
            f"- {key}: {value['current']}/{value['target']} (add {value['missing']})"
            for key, value in payload["coverage_gaps"]["regions"].items()
        )
    else:
        lines.append("- None")
    lines.extend(["", "### Purposes below target", ""])
    if payload["coverage_gaps"]["purposes"]:
        lines.extend(
            f"- {key}: {value['current']}/{value['target']} (add {value['missing']})"
            for key, value in payload["coverage_gaps"]["purposes"].items()
        )
    else:
        lines.append("- None")
    lines.extend(["", "### Durations below target", ""])
    if payload["coverage_gaps"]["durations"]:
        lines.extend(
            f"- {key}: {value['current']}/{value['target']} (add {value['missing']})"
            for key, value in payload["coverage_gaps"]["durations"].items()
        )
    else:
        lines.append("- None")
    lines.extend(["", "## Route findings", ""])
    for row in rows:
        marker = "PASS" if not row["issues"] else ", ".join(i["code"] for i in row["issues"])
        regions_text = ", ".join(f"{k} ({v})" for k, v in row["regions"].items()) or "none"
        lines.extend([
            f"### {row['name']} (`{row['slug']}`)",
            "",
            f"- {row['days']} day(s); {row['purpose']}; {row['vehicle']}; {row['waypoint_count']} stops",
            f"- Regions: {regions_text}",
            f"- Distance: stated {row['stated_distance_km']} km; coordinate chain {row['straight_chain_km']} km; ratio {row['distance_ratio']}",
            f"- Result: **{marker}**",
            "",
        ])
    md_path = ROOT / args.markdown
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"Wrote {json_path.relative_to(ROOT)} and {md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
