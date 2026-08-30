#!/usr/bin/env python3
"""Add planner-critical metadata to legacy standard tours without reformatting YAML."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "content" / "routes"


CITIES = {
    "tbilisi": {
        "lat": 41.7151,
        "lon": 44.8271,
        "road_factor": 1.25,
        "speed_kmh": 55,
        "names": {"ka": "თბილისი", "en": "Tbilisi", "ru": "Тбилиси", "fa": "تفلیس", "he": "טביליסי", "ar": "تبليسي"},
    },
    "kutaisi": {
        "lat": 42.2679,
        "lon": 42.7180,
        "road_factor": 1.30,
        "speed_kmh": 50,
        "names": {"ka": "ქუთაისი", "en": "Kutaisi", "ru": "Кутаиси", "fa": "کوتایسی", "he": "כותאיסי", "ar": "كوتايسي"},
    },
    "batumi": {
        "lat": 41.6168,
        "lon": 41.6367,
        "road_factor": 1.30,
        "speed_kmh": 45,
        "names": {"ka": "ბათუმი", "en": "Batumi", "ru": "Батуми", "fa": "باتومی", "he": "בטומי", "ar": "باتومي"},
    },
    "borjomi": {
        "lat": 41.8414,
        "lon": 43.3846,
        "road_factor": 1.25,
        "speed_kmh": 45,
        "names": {"ka": "ბორჯომი", "en": "Borjomi", "ru": "Боржоми", "fa": "برجومی", "he": "בורג'ומי", "ar": "بورجومي"},
    },
    "mestia": {
        "lat": 43.0458,
        "lon": 42.7297,
        "road_factor": 1.45,
        "speed_kmh": 35,
        "names": {"ka": "მესტია", "en": "Mestia", "ru": "Местиа", "fa": "مستیا", "he": "מסטיה", "ar": "ميستيا"},
    },
}


ORIGINS = {
    "adjara-guria-green-road": "batumi",
    "black-sea-adjara": "tbilisi",
    "borjomi-bike-and-nature": "borjomi",
    "family-georgia-seven-days": "tbilisi",
    "grand-georgia-classic": "tbilisi",
    "guria-slow-food-and-coast": "kutaisi",
    "imereti-caves-canyons": "tbilisi",
    "imereti-family-discovery": "kutaisi",
    "javakheti-lakes-and-birds": "tbilisi",
    "kakheti-cycle-and-wine": "tbilisi",
    "kakheti-table-and-cellar": "tbilisi",
    "kakheti-wine-loop": "tbilisi",
    "kazbegi-hiking-base": "tbilisi",
    "kvemo-kartli-archaeology-road": "tbilisi",
    "military-highway-kazbegi": "tbilisi",
    "mtskheta-gori-heritage": "tbilisi",
    "racha-alpine-hiking-week": "kutaisi",
    "racha-wine-and-mountains": "kutaisi",
    "samegrelo-kingdoms-and-wetlands": "kutaisi",
    "samtskhe-heritage-road": "tbilisi",
    "shida-kartli-monastery-trail": "tbilisi",
    "svaneti-alpine-circuit": "mestia",
    "svaneti-expedition": "tbilisi",
    "svaneti-village-trek": "mestia",
    "tbilisi-architecture-and-markets": "tbilisi",
    "tbilisi-history-walk": "tbilisi",
    "tbilisi-theatre-night": "tbilisi",
    "tusheti-highland-hike": "tbilisi",
    "upper-adjara-wine-and-villages": "batumi",
    "vardzia-borjomi-south": "tbilisi",
    "western-georgia-food-road": "kutaisi",
}


SOURCE_FALLBACKS = {
    "black-sea-adjara": [
        "https://georgia.travel/regions/ajara",
        "https://georgia.travel/9-amazing-sights-in-ajara",
    ],
    "imereti-caves-canyons": [
        "https://gulf.georgia.travel/brochure/en/UAG_Imereti_en.pdf",
        "https://georgia.travel/destinations-in-georgia",
    ],
    "kakheti-wine-loop": [
        "https://georgia.travel/regions/kakheti",
        "https://georgia.travel/biking-along-the-kakheti-wine-route",
    ],
    "military-highway-kazbegi": [
        "https://georgia.travel/cities-towns/stepantsminda",
        "https://georgia.travel/kazbegi-national-park",
    ],
    "svaneti-expedition": [
        "https://georgia.travel/popular-trips/two-day-tour-svaneti",
        "https://georgia.travel/ushguli-shkhara-glacier-namkvami-lake",
    ],
    "vardzia-borjomi-south": [
        "https://georgia.travel/destinations-in-georgia",
        "https://georgia.travel/regions/samtskhe-javakheti",
    ],
}


def daily_hours(data: dict) -> int:
    purpose = str(data.get("purpose") or "")
    if purpose == "performance":
        return 6
    if purpose in {"hiking", "mountains"}:
        return 9
    if purpose == "classic" or int(data.get("days") or 0) >= 7:
        return 9
    return 8


def origin_yaml(city_key: str) -> str:
    city = CITIES[city_key]
    lines = [
        "origin:",
        f"  lat: {city['lat']}",
        f"  lon: {city['lon']}",
        f"  road_factor: {city['road_factor']}",
        f"  speed_kmh: {city['speed_kmh']}",
    ]
    lines.extend(f"  name_{lang}: {name}" for lang, name in city["names"].items())
    return "\n".join(lines)


def sources_yaml(urls: list[str]) -> str:
    lines = ["sources:"]
    lines.extend(f"  - {url}" for url in urls)
    return "\n".join(lines)


def main() -> None:
    changed = []
    for path in sorted(ROUTES.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        additions = []

        if not data.get("daily_hours"):
            additions.append(f"daily_hours: {daily_hours(data)}")
        if not data.get("origin"):
            city_key = ORIGINS.get(path.stem)
            if not city_key:
                raise RuntimeError(f"No reviewed origin mapping for {path.stem}")
            additions.append(origin_yaml(city_key))

        if additions:
            marker = re.search(r"(?m)^car_category:", text)
            if not marker:
                raise RuntimeError(f"No car_category marker in {path.name}")
            text = text[: marker.start()] + "\n".join(additions) + "\n" + text[marker.start() :]

        if not data.get("sources"):
            urls = SOURCE_FALLBACKS.get(path.stem)
            if not urls:
                raise RuntimeError(f"No reviewed source fallback for {path.stem}")
            marker = re.search(r"(?m)^ka:", text)
            if not marker:
                raise RuntimeError(f"No Georgian content marker in {path.name}")
            text = text[: marker.start()] + sources_yaml(urls) + "\n" + text[marker.start() :]

        current = path.read_text(encoding="utf-8")
        if text != current:
            yaml.safe_load(text)
            path.write_text(text, encoding="utf-8")
            changed.append(path.name)

    print(f"Updated {len(changed)} routes")
    for name in changed:
        print(f"- {name}")


if __name__ == "__main__":
    main()
