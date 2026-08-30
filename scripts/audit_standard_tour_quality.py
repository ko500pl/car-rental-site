#!/usr/bin/env python3
"""Audit standard tours for practical time, distance, media, and source quality."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES_DIR = ROOT / "content" / "routes"
ATTRACTIONS_DIR = ROOT / "content" / "attractions"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_duration(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    try:
        hours, minutes = text.split(":", 1)
        hours_value = int(hours)
        minutes_value = int(minutes)
    except (TypeError, ValueError):
        return None
    if hours_value < 0 or not 0 <= minutes_value < 60:
        return None
    return hours_value + minutes_value / 60


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    radius = 6371.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    value = min(1.0, max(0.0, value))
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def attraction_index() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for path in sorted(ATTRACTIONS_DIR.glob("*.yml")):
        data = load_yaml(path)
        image = str(data.get("image") or "")
        normalized_image = image.lstrip("/")
        if normalized_image.startswith("assets/photos/"):
            normalized_image = normalized_image.removeprefix("assets/")
        image_path = ROOT / "static" / normalized_image if image else None
        records[path.stem] = {
            "name": (data.get("ka") or {}).get("name", path.stem),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "visit_hours": float(data.get("visit_hours") or 0),
            "elevation": float(data.get("elevation") or 0),
            "image": image,
            "image_exists": bool(image_path and image_path.exists()),
        }
    return records


def add_issue(issues: list[dict], severity: str, code: str, detail: str) -> None:
    issues.append({"severity": severity, "code": code, "detail": detail})


def audit_route(path: Path, attractions: dict[str, dict]) -> dict:
    data = load_yaml(path)
    days = int(data.get("days") or 0)
    daily_hours = float(data.get("daily_hours") or 0)
    capacity_hours = days * daily_hours
    drive_hours = parse_duration(data.get("drive_time_total"))
    purpose = str(data.get("purpose") or "").strip().lower()
    inferred_mode = "cycling" if purpose == "cycling" else "hiking" if purpose == "hiking" else "road"
    routing_mode = str(data.get("routing_mode") or inferred_mode).strip().lower()
    return_to_origin = bool(data.get("return_to_origin"))
    waypoints = [str(value) for value in data.get("waypoints") or []]
    missing = [slug for slug in waypoints if slug not in attractions]
    known = [attractions[slug] for slug in waypoints if slug in attractions]
    visit_hours = sum(item["visit_hours"] for item in known)
    total_hours = (drive_hours or 0) + visit_hours
    load_ratio = total_hours / capacity_hours if capacity_hours else None

    coords: list[tuple[float, float]] = []
    origin = data.get("origin") or {}
    if origin.get("lat") is not None and origin.get("lon") is not None:
        coords.append((float(origin["lat"]), float(origin["lon"])))
    for item in known:
        if item["lat"] is not None and item["lon"] is not None:
            coords.append((float(item["lat"]), float(item["lon"])))
    if return_to_origin and len(coords) > 1:
        coords.append(coords[0])
    legs = [haversine_km(a, b) for a, b in zip(coords, coords[1:])]
    straight_chain = sum(legs)
    longest_leg = max(legs, default=0)
    stated_distance = float(data.get("distance_km") or 0)
    distance_ratio = stated_distance / straight_chain if straight_chain else None
    missing_photos = [slug for slug in waypoints if slug in attractions and not attractions[slug]["image_exists"]]
    high_elevation = [slug for slug in waypoints if slug in attractions and attractions[slug]["elevation"] >= 2000]
    source_count = len(data.get("sources") or [])

    issues: list[dict] = []
    if missing:
        add_issue(issues, "error", "missing-waypoint", ", ".join(missing))
    if days <= 0 or daily_hours <= 0:
        add_issue(issues, "error", "invalid-time-capacity", f"days={days}, daily_hours={daily_hours:g}")
    if drive_hours is None:
        add_issue(issues, "error", "invalid-drive-time", str(data.get("drive_time_total")))
    if len(waypoints) < 2:
        add_issue(issues, "error", "too-few-waypoints", str(len(waypoints)))
    if load_ratio is not None and load_ratio > 1:
        add_issue(issues, "error", "time-budget-exceeded", f"{total_hours:.1f}/{capacity_hours:.1f} h")
    elif load_ratio is not None and load_ratio > 0.9:
        add_issue(issues, "warning", "very-tight-time-budget", f"{load_ratio:.0%}")
    if days == 1 and ((drive_hours or 0) > 6.5 or stated_distance > 350 or len(waypoints) > 5):
        add_issue(
            issues,
            "warning",
            "one-day-overloaded",
            f"drive={drive_hours or 0:.1f} h, distance={stated_distance:.0f} km, stops={len(waypoints)}",
        )
    if longest_leg > 250 and routing_mode == "road":
        add_issue(issues, "warning", "long-single-leg", f"{longest_leg:.0f} km straight-line")
    if routing_mode == "road" and distance_ratio is not None and distance_ratio < 0.95:
        add_issue(issues, "error", "distance-under-straight-chain", f"ratio={distance_ratio:.2f}")
    if missing_photos:
        add_issue(issues, "warning", "missing-primary-photo", ", ".join(missing_photos))
    if source_count < 2:
        add_issue(issues, "warning", "thin-source-support", str(source_count))
    if high_elevation and str(data.get("best_season") or "").lower() in {"all", "all-year", "year-round"}:
        add_issue(issues, "warning", "high-elevation-season-review", ", ".join(high_elevation))

    return {
        "slug": path.stem,
        "name": (data.get("ka") or {}).get("name", path.stem),
        "days": days,
        "routing_mode": routing_mode,
        "return_to_origin": return_to_origin,
        "daily_hours": daily_hours,
        "capacity_hours": round(capacity_hours, 1),
        "drive_hours": round(drive_hours, 2) if drive_hours is not None else None,
        "visit_hours": round(visit_hours, 2),
        "total_program_hours": round(total_hours, 2),
        "load_ratio": round(load_ratio, 3) if load_ratio is not None else None,
        "waypoint_count": len(waypoints),
        "stated_distance_km": round(stated_distance, 1),
        "straight_chain_km": round(straight_chain, 1),
        "distance_ratio": round(distance_ratio, 2) if distance_ratio is not None else None,
        "longest_leg_km": round(longest_leg, 1),
        "source_count": source_count,
        "missing_photos": missing_photos,
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="reports/standard-tour-quality-audit.json")
    parser.add_argument("--markdown", default="reports/STANDARD_TOUR_QUALITY_AUDIT_2026-08-29.md")
    args = parser.parse_args()

    attractions = attraction_index()
    rows = [audit_route(path, attractions) for path in sorted(ROUTES_DIR.glob("*.yml"))]
    counts = Counter(issue["code"] for row in rows for issue in row["issues"])
    errors = sum(issue["severity"] == "error" for row in rows for issue in row["issues"])
    warnings = sum(issue["severity"] == "warning" for row in rows for issue in row["issues"])
    needs_review = sum(bool(row["issues"]) for row in rows)
    payload = {
        "generated_on": date.today().isoformat(),
        "summary": {
            "routes": len(rows),
            "errors": errors,
            "warnings": warnings,
            "routes_needing_review": needs_review,
        },
        "issue_codes": dict(sorted(counts.items())),
        "routes": rows,
    }

    json_path = ROOT / args.json
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Standard Tour Quality Audit",
        "",
        f"Generated: {payload['generated_on']}",
        "",
        "## Summary",
        "",
        f"- Routes: **{len(rows)}**",
        f"- Errors: **{errors}**",
        f"- Warnings: **{warnings}**",
        f"- Routes needing review: **{needs_review}**",
        "",
        "## Findings",
        "",
    ]
    for row in rows:
        result = "PASS" if not row["issues"] else ", ".join(
            f"{issue['severity']}:{issue['code']}" for issue in row["issues"]
        )
        load_text = f"{row['load_ratio']:.0%}" if row["load_ratio"] is not None else "n/a"
        lines.extend([
            f"### {row['name']} (`{row['slug']}`)",
            "",
            f"- Program: {row['total_program_hours']} h / {row['capacity_hours']} h ({load_text}); mode: {row['routing_mode']}; return: {row['return_to_origin']}",
            f"- Distance: {row['stated_distance_km']} km stated; {row['straight_chain_km']} km straight chain; longest leg {row['longest_leg_km']} km",
            f"- Stops: {row['waypoint_count']}; sources: {row['source_count']}",
            f"- Result: **{result}**",
            "",
        ])
    markdown_path = ROOT / args.markdown
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"Wrote {json_path.relative_to(ROOT)} and {markdown_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
