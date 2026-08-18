"""Audit attraction photos against Wikimedia Commons metadata and coordinates."""

from __future__ import annotations

import argparse
import json
import math
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml


API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "FleetHouseImageAudit/1.0 (https://rentup.ge)"


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except (TimeoutError, OSError):
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def source_title(source: str) -> str:
    if "/wiki/File:" not in source:
        return ""
    return "File:" + urllib.parse.unquote(source.split("/wiki/File:", 1)[1]).replace("_", " ")


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def strip_html(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value or "")).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", default="content/attractions")
    parser.add_argument("--output", default="reports/attraction-image-audit.json")
    args = parser.parse_args()
    records = []
    titles = []
    for path in sorted(Path(args.content).glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        items = []
        credit = data.get("image_credit") or {}
        if data.get("image"):
            items.append({"slot": "primary", "image": data["image"], "source": credit.get("source", "")})
        for index, item in enumerate(data.get("gallery") or [], 1):
            items.append({"slot": f"gallery-{index}", "image": item.get("image", ""), "source": item.get("source", "")})
        record = {
            "slug": path.stem,
            "name": (data.get("en") or {}).get("name", path.stem),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "items": items,
        }
        records.append(record)
        titles.extend(source_title(item["source"]) for item in items if source_title(item["source"]))

    metadata = {}
    unique_titles = sorted(set(titles))
    for offset in range(0, len(unique_titles), 20):
        batch = unique_titles[offset : offset + 20]
        result = api({
            "action": "query",
            "titles": "|".join(batch),
            "prop": "imageinfo|coordinates",
            "iiprop": "extmetadata|url",
        })
        for page in (result.get("query") or {}).get("pages", {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            ext = info.get("extmetadata") or {}
            coordinates = (page.get("coordinates") or [{}])[0]
            metadata[page.get("title", "")] = {
                "description": strip_html((ext.get("ImageDescription") or {}).get("value", "")),
                "categories": (ext.get("Categories") or {}).get("value", ""),
                "object_name": strip_html((ext.get("ObjectName") or {}).get("value", "")),
                "artist": strip_html((ext.get("Artist") or {}).get("value", "")),
                "license": (ext.get("LicenseShortName") or {}).get("value", ""),
                "lat": coordinates.get("lat"),
                "lon": coordinates.get("lon"),
                "url": info.get("descriptionurl", ""),
            }
        time.sleep(0.1)

    for record in records:
        for item in record["items"]:
            title = source_title(item["source"])
            item["commons_title"] = title
            item["metadata"] = metadata.get(title, {})
            photo_lat = item["metadata"].get("lat")
            photo_lon = item["metadata"].get("lon")
            if None not in (record["lat"], record["lon"], photo_lat, photo_lon):
                item["distance_km"] = round(distance_km(record["lat"], record["lon"], photo_lat, photo_lon), 1)
            else:
                item["distance_km"] = None

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Audited {len(records)} attractions, {sum(len(r['items']) for r in records)} photos -> {output}")


if __name__ == "__main__":
    main()
