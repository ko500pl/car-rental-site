#!/usr/bin/env python3
"""Verify standard-tour waypoint chains against OSRM road routing.

The script is deliberately read-only with respect to content. It writes a
cacheable JSON report that editors can use before changing published distance
or drive-time values. Routes that OSRM cannot resolve are reported, not guessed.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES_DIR = ROOT / "content" / "routes"
ATTRACTIONS_DIR = ROOT / "content" / "attractions"
DEFAULT_ENDPOINT = "https://router.project-osrm.org/route/v1/driving"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_duration(value: object) -> float | None:
    try:
        hours, minutes = str(value).strip().split(":", 1)
        return int(hours) + int(minutes) / 60
    except (TypeError, ValueError):
        return None


def attraction_coordinates() -> dict[str, tuple[float, float]]:
    result: dict[str, tuple[float, float]] = {}
    for path in ATTRACTIONS_DIR.glob("*.yml"):
        data = load_yaml(path)
        if data.get("lat") is None or data.get("lon") is None:
            continue
        result[path.stem] = (float(data["lat"]), float(data["lon"]))
    return result


def osrm_route(
    endpoint: str,
    coordinates: list[tuple[float, float]],
    stop_labels: list[str],
    timeout: int,
) -> dict:
    encoded = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in coordinates)
    query = urllib.parse.urlencode({"overview": "false", "steps": "false", "alternatives": "false"})
    url = f"{endpoint.rstrip('/')}/{encoded}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "Fleet-House-content-audit/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise RuntimeError(f"OSRM response code: {payload.get('code', 'unknown')}")
    route = payload["routes"][0]
    legs = []
    for index, leg in enumerate(route.get("legs") or []):
        legs.append({
            "from": stop_labels[index],
            "to": stop_labels[index + 1],
            "distance_km": round(float(leg["distance"]) / 1000, 1),
            "drive_hours": round(float(leg["duration"]) / 3600, 2),
        })
    return {
        "distance_km": round(float(route["distance"]) / 1000, 1),
        "drive_hours": round(float(route["duration"]) / 3600, 2),
        "legs": legs,
        "url": url,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="reports/standard-tour-osrm-verification.json")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=int, default=35)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--slug", action="append", default=[])
    args = parser.parse_args()

    attraction_coords = attraction_coordinates()
    selected = set(args.slug)
    rows: list[dict] = []
    for path in sorted(ROUTES_DIR.glob("*.yml")):
        if selected and path.stem not in selected:
            continue
        data = load_yaml(path)
        purpose = str(data.get("purpose") or "").strip().lower()
        inferred_mode = "cycling" if purpose == "cycling" else "hiking" if purpose == "hiking" else "road"
        routing_mode = str(data.get("routing_mode") or inferred_mode).strip().lower()
        origin = data.get("origin") or {}
        waypoints = [str(value) for value in data.get("waypoints") or []]
        missing = [slug for slug in waypoints if slug not in attraction_coords]
        coordinates: list[tuple[float, float]] = []
        stop_labels: list[str] = []
        if origin.get("lat") is not None and origin.get("lon") is not None:
            coordinates.append((float(origin["lat"]), float(origin["lon"])))
            stop_labels.append("origin")
        for slug in waypoints:
            if slug in attraction_coords:
                coordinates.append(attraction_coords[slug])
                stop_labels.append(slug)
        return_to_origin = bool(data.get("return_to_origin"))
        if return_to_origin and coordinates and stop_labels[0] == "origin":
            coordinates.append(coordinates[0])
            stop_labels.append("origin:return")
        row = {
            "slug": path.stem,
            "name": (data.get("ka") or {}).get("name", path.stem),
            "waypoints": waypoints,
            "return_to_origin": return_to_origin,
            "routing_mode": routing_mode,
            "missing_waypoints": missing,
            "stated_distance_km": float(data.get("distance_km") or 0),
            "stated_drive_hours": parse_duration(data.get("drive_time_total")),
            "osrm": None,
            "distance_ratio": None,
            "drive_time_ratio": None,
            "status": "pending",
            "error": None,
        }
        if routing_mode != "road":
            row["status"] = "skipped-non-road"
            row["error"] = f"OSRM driving comparison is not applicable to {routing_mode} routes"
        elif missing or len(coordinates) < 2:
            row["status"] = "invalid-input"
            row["error"] = "missing coordinates: " + ", ".join(missing)
        else:
            try:
                result = osrm_route(args.endpoint, coordinates, stop_labels, args.timeout)
                row["osrm"] = {key: value for key, value in result.items() if key != "url"}
                if result["distance_km"]:
                    row["distance_ratio"] = round(row["stated_distance_km"] / result["distance_km"], 2)
                if result["drive_hours"] and row["stated_drive_hours"] is not None:
                    row["drive_time_ratio"] = round(row["stated_drive_hours"] / result["drive_hours"], 2)
                row["status"] = "ok"
            except (OSError, RuntimeError, urllib.error.URLError, ValueError) as exc:
                row["status"] = "routing-failed"
                row["error"] = str(exc)
            time.sleep(max(0, args.delay))
        rows.append(row)

    payload = {
        "generated_on": date.today().isoformat(),
        "method": "OSRM driving route through origin and ordered waypoints for road routes only; cycling, hiking and off-road routes are explicitly skipped; return leg is included only when return_to_origin=true",
        "endpoint": args.endpoint,
        "summary": {
            "routes": len(rows),
            "verified": sum(row["status"] == "ok" for row in rows),
            "skipped_non_road": sum(row["status"] == "skipped-non-road" for row in rows),
            "failed": sum(row["status"] not in {"ok", "skipped-non-road"} for row in rows),
            "stated_below_osrm_distance": sum(
                row["status"] == "ok" and row["distance_ratio"] is not None and row["distance_ratio"] < 0.9
                for row in rows
            ),
            "stated_below_osrm_time": sum(
                row["status"] == "ok" and row["drive_time_ratio"] is not None and row["drive_time_ratio"] < 0.85
                for row in rows
            ),
        },
        "routes": rows,
    }
    output = ROOT / args.json
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()


