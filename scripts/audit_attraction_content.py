"""Create a repeatable, region-by-region attraction content audit.

The report intentionally separates mechanical validation from editorial review.
An image without exact Wikimedia metadata is not automatically wrong; it is
flagged for a human visual check instead of being silently accepted or removed.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "attractions"
STATIC_DIR = ROOT / "static"
REPORTS_DIR = ROOT / "reports"
CLASSIFICATION_PATH = REPORTS_DIR / "attraction-image-classification.json"

LANGUAGES = ("ka", "en", "ru", "fa", "he", "ar")
LANGUAGE_FIELDS = ("name", "short", "body", "tip", "route")
EXPECTED_KEYS = (
    "region",
    "type",
    "lat",
    "lon",
    "elevation",
    "unesco",
    "featured",
    "order",
    "image",
    "gallery",
    "visit_hours",
    "best_season",
    "open_year_round",
    "entry_fee",
    "distance_tbilisi_km",
    "drive_time_tbilisi",
    "road",
    "car_category",
    "nearby",
    *LANGUAGES,
    "image_credit",
    "rating",
)

REGIONS = (
    "tbilisi",
    "adjara",
    "guria",
    "imereti",
    "kakheti",
    "kvemo-kartli",
    "mtskheta-mtianeti",
    "racha-lechkhumi",
    "samegrelo-zemo-svaneti",
    "samtskhe-javakheti",
    "shida-kartli",
)

ALLOWED_TYPES = {
    "archaeology",
    "beach",
    "canyon",
    "cave",
    "fortress",
    "lake",
    "monastery",
    "mountain",
    "museum",
    "nature",
    "ski",
    "spa",
    "town",
    "theatre",
    "waterfall",
    "winery",
}
ALLOWED_RATINGS = {3.0, 3.5, 4.0, 4.5, 5.0}
ALLOWED_VISIT_HOURS = {"0.5", "1", "1.5", "2", "2.5", "3", "4", "6", "8"}
ALLOWED_SEASONS = {"all", "may-october", "june-september", "december-march"}
ALLOWED_ROADS = {"paved", "mostly_paved", "gravel", "4x4_only"}
ALLOWED_CARS = {"economy", "suv", "offroad"}
GEORGIA_BOUNDS = (40.80, 43.75, 39.90, 46.85)
TBILISI = (41.7151, 44.8271)

EDITORIAL_TERMS = {
    "en": ("breathtaking", "hidden gem", "must-see", "unforgettable"),
    "ka": ("თვალწარმტაცი", "დაუვიწყარი", "აუცილებლად სანახავი"),
    "ru": ("захватывающ", "скрытая жемчужина", "обязательно посет"),
}


def text_words(value: Any) -> int:
    text = re.sub(r"[*_#>`\-]", " ", str(value or ""))
    return len(re.findall(r"[^\W_]+(?:[-’'][^\W_]+)*", text, flags=re.UNICODE))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    value = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def asset_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value.startswith("/assets/"):
        return None
    return STATIC_DIR / value.removeprefix("/assets/")


def load_exact_image_index() -> dict[tuple[str, str, str], dict[str, Any]]:
    if not CLASSIFICATION_PATH.exists():
        return {}
    rows = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for attraction in rows:
        slug = attraction.get("slug", "")
        for item in attraction.get("items", []):
            key = (slug, str(item.get("slot", "")), str(item.get("image", "")))
            index[key] = item
    return index


def image_metrics(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
        "width": None,
        "height": None,
        "format": None,
        "sha256": None,
    }
    if not path.exists():
        return result
    result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        with Image.open(path) as image:
            result["width"], result["height"] = image.size
            result["format"] = image.format
    except Exception as exc:  # pragma: no cover - corrupt files are report data
        result["error"] = str(exc)
    return result


def issue(level: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"level": level, "code": code, "message": message, **details}


def audit_file(
    path: Path,
    known_slugs: set[str],
    exact_index: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    slug = path.stem
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    problems: list[dict[str, Any]] = []

    keys = list(data.keys())
    expected_present = [key for key in EXPECTED_KEYS if key in data]
    actual_relevant = [key for key in keys if key in EXPECTED_KEYS]
    if actual_relevant != expected_present:
        problems.append(issue("warning", "key-order", "ველების მიმდევრობა სპეციფიკაციას არ ემთხვევა."))

    missing_top = [key for key in EXPECTED_KEYS if key not in data]
    if missing_top:
        problems.append(issue("error", "missing-fields", "აკლია აუცილებელი ზედა დონის ველები.", fields=missing_top))

    region = data.get("region")
    if region not in REGIONS:
        problems.append(issue("error", "invalid-region", f"უცნობი რეგიონი: {region!r}."))
    if data.get("type") not in ALLOWED_TYPES:
        problems.append(issue("error", "invalid-type", f"უცნობი ტიპი: {data.get('type')!r}."))

    lat, lon = data.get("lat"), data.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        problems.append(issue("error", "coordinates", "კოორდინატები რიცხვითი არ არის."))
        straight_km = None
    else:
        south, north, west, east = GEORGIA_BOUNDS
        if not (south <= lat <= north and west <= lon <= east):
            problems.append(issue("error", "coordinates", "კოორდინატები საქართველოს საზღვრებს გარეთაა."))
        straight_km = haversine_km(TBILISI[0], TBILISI[1], float(lat), float(lon))
        road_km = data.get("distance_tbilisi_km")
        if isinstance(road_km, (int, float)) and road_km + 5 < straight_km:
            problems.append(
                issue(
                    "error",
                    "road-distance",
                    "თბილისიდან საგზაო მანძილი პირდაპირ ხაზზე მანძილზე ნაკლებია.",
                    straight_km=round(straight_km, 1),
                    stated_km=road_km,
                )
            )

    if str(data.get("visit_hours")) not in ALLOWED_VISIT_HOURS:
        problems.append(issue("warning", "visit-hours", f"არასტანდარტული მონახულების დრო: {data.get('visit_hours')!r}."))
    if data.get("best_season") not in ALLOWED_SEASONS:
        problems.append(issue("error", "best-season", f"უცნობი სეზონი: {data.get('best_season')!r}."))
    if data.get("road") not in ALLOWED_ROADS:
        problems.append(issue("error", "road", f"უცნობი გზის ტიპი: {data.get('road')!r}."))
    if data.get("car_category") not in ALLOWED_CARS:
        problems.append(issue("error", "car-category", f"უცნობი მანქანის კატეგორია: {data.get('car_category')!r}."))

    rating = data.get("rating")
    try:
        rating_number = float(rating)
    except (TypeError, ValueError):
        rating_number = None
    if rating_number not in ALLOWED_RATINGS:
        problems.append(
            issue(
                "review",
                "rating-rubric",
                "ვარსკვლავი არ არის ერთიანი სარედაქციო სკალის ნაწილი (3/3.5/4/4.5/5).",
                rating=rating,
            )
        )

    nearby = data.get("nearby") or []
    if not isinstance(nearby, list):
        problems.append(issue("error", "nearby-format", "nearby სია არ არის."))
    else:
        unknown = sorted({str(value) for value in nearby if value not in known_slugs})
        if unknown:
            problems.append(issue("error", "nearby-missing", "nearby-ში არარსებული slug-ებია.", slugs=unknown))
        if slug in nearby:
            problems.append(issue("error", "nearby-self", "ობიექტი nearby-ში საკუთარ თავს უთითებს."))
        if not 2 <= len(nearby) <= 4:
            problems.append(issue("warning", "nearby-count", "nearby-ის რეკომენდებული რაოდენობაა 2–4.", count=len(nearby)))

    language_stats: dict[str, Any] = {}
    for lang in LANGUAGES:
        block = data.get(lang)
        if not isinstance(block, dict):
            problems.append(issue("error", "language-block", f"აკლია ან დაზიანებულია {lang} ენის ბლოკი."))
            continue
        missing = [field for field in LANGUAGE_FIELDS if not str(block.get(field, "")).strip()]
        if missing:
            problems.append(issue("error", "language-fields", f"{lang} ენაზე აკლია ველები.", fields=missing))
        counts = {field: text_words(block.get(field)) for field in LANGUAGE_FIELDS}
        language_stats[lang] = counts
        if counts.get("short", 0) and not 8 <= counts["short"] <= 32:
            problems.append(issue("review", "short-length", f"{lang} მოკლე აღწერა გადასახედია.", words=counts["short"]))
        if counts.get("body", 0) and not 180 <= counts["body"] <= 460:
            problems.append(issue("review", "body-length", f"{lang} ძირითადი ტექსტი სპეციფიკაციის ფარგლებს სცდება.", words=counts["body"]))
        if counts.get("tip", 0) and not 35 <= counts["tip"] <= 130:
            problems.append(issue("review", "tip-length", f"{lang} პრაქტიკული რჩევა გადასახედია.", words=counts["tip"]))
        if counts.get("route", 0) and not 35 <= counts["route"] <= 130:
            problems.append(issue("review", "route-length", f"{lang} მისასვლელი ტექსტი გადასახედია.", words=counts["route"]))
        combined = " ".join(str(block.get(field, "")).lower() for field in LANGUAGE_FIELDS)
        hits = [term for term in EDITORIAL_TERMS.get(lang, ()) if term in combined]
        if hits:
            problems.append(issue("review", "marketing-copy", f"{lang} ტექსტში სარეკლამო კლიშეა.", terms=hits))

    media: list[dict[str, Any]] = []
    image_value = data.get("image")
    gallery = data.get("gallery") if isinstance(data.get("gallery"), list) else []
    media_values: list[tuple[str, Any, Any]] = [("primary", image_value, data.get("image_credit"))]
    for index, gallery_item in enumerate(gallery, 1):
        if isinstance(gallery_item, dict):
            media_values.append((f"gallery-{index}", gallery_item.get("image"), gallery_item))
        else:
            media_values.append((f"gallery-{index}", gallery_item, None))

    for slot, value, credit in media_values:
        local = asset_path(value)
        metrics = image_metrics(local) if local else {"exists": False}
        classification = exact_index.get((slug, slot, str(value or "")), {})
        source = credit.get("source") if isinstance(credit, dict) else None
        entry = {
            "slot": slot,
            "image": value,
            "source": source,
            "local_path": str(local.relative_to(ROOT)) if local and local.is_relative_to(ROOT) else None,
            "verified_exact_metadata": bool(classification.get("verified_exact")),
            "evidence": classification.get("evidence"),
            **metrics,
        }
        media.append(entry)
        if value and (not local or not metrics.get("exists")):
            problems.append(issue("error", "missing-image", f"{slot} ფოტო ლოკალურად არ არსებობს.", image=value))
        if slot == "primary" and not value:
            problems.append(issue("review", "missing-primary", "მთავარი ფოტო არ არის."))
        if value and not source:
            problems.append(issue("review", "missing-source", f"{slot} ფოტოს წყარო არ აქვს."))
        if metrics.get("exists"):
            width, height = metrics.get("width"), metrics.get("height")
            if not isinstance(width, int) or not isinstance(height, int):
                problems.append(issue("error", "image-corrupt", f"{slot} ფოტო ვერ გაიხსნა."))
            else:
                if width < 800 or height < 500:
                    problems.append(
                        issue(
                            "review",
                            "image-resolution",
                            f"{slot} ფოტო დაბალი გარჩევადობისაა.",
                            width=width,
                            height=height,
                        )
                    )
                if slot == "primary" and width / max(height, 1) < 1.15:
                    problems.append(issue("review", "image-aspect", "მთავარი ფოტო ჰორიზონტალური ქავერისთვის ვიწროა."))
        if value and not classification.get("verified_exact"):
            problems.append(
                issue(
                    "review",
                    "image-identity",
                    f"{slot} ფოტოს ზუსტი ობიექტი მეტამონაცემებით ვერ დასტურდება; საჭიროა ვიზუალური შემოწმება.",
                )
            )

    return {
        "slug": slug,
        "file": str(path.relative_to(ROOT)),
        "region": region,
        "type": data.get("type"),
        "name": (data.get("ka") or {}).get("name", slug),
        "rating": rating,
        "featured": bool(data.get("featured")),
        "coordinates": {"lat": lat, "lon": lon},
        "straight_line_tbilisi_km": round(straight_km, 1) if straight_km is not None else None,
        "language_words": language_stats,
        "media": media,
        "issues": problems,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# საქართველოს ღირსშესანიშნაობების კონტენტ-აუდიტი",
        "",
        f"განახლებულია: {payload['generated_on']}",
        "",
        "ეს ანგარიში ავტომატურად ამოწმებს სქემას, თარგმანების სისრულეს, ტექსტის მოცულობას,",
        "ფოტოს ტექნიკურ ხარისხს, წყაროსა და მეტამონაცემების მტკიცებულებას. `review` ნიშნავს",
        "ადამიანის სარედაქციო/ვიზუალურ შემოწმებას და არა ავტომატურად დადასტურებულ შეცდომას.",
        "",
        "## შეჯამება",
        "",
        f"- ობიექტი: **{summary['attractions']}**",
        f"- რეგიონი: **{summary['regions']}**",
        f"- მექანიკური შეცდომა: **{summary['errors']}**",
        f"- გაფრთხილება: **{summary['warnings']}**",
        f"- სარედაქციო/ვიზუალური გადამოწმება: **{summary['reviews']}**",
        f"- მთავარი ფოტო ზუსტი სახელობრივი მტკიცებულებით: **{summary['primary_exact']} / {summary['primary_total']}**",
        f"- მთავარ ფოტოს გარეშე: **{summary['missing_primary']}**",
        f"- დაბალი გარჩევადობის მედია: **{summary['low_resolution_media']}**",
        f"- ერთი და იგივე ფაილის დუბლირებული ჯგუფი: **{summary['duplicate_image_groups']}**",
        "",
        "## ვარსკვლავების განაწილება",
        "",
    ]
    for rating, count in payload["rating_distribution"].items():
        lines.append(f"- {rating}: {count}")

    lines.extend(["", "## რეგიონების მიხედვით", ""])
    for region in REGIONS:
        region_payload = payload["regions"].get(region, {})
        lines.extend(
            [
                f"### {region}",
                "",
                f"ობიექტები: **{region_payload.get('count', 0)}** · შეცდომები: **{region_payload.get('errors', 0)}** · გადასამოწმებელი: **{region_payload.get('reviews', 0)}**",
                "",
            ]
        )
        for attraction in region_payload.get("items", []):
            counts = collections.Counter(item["level"] for item in attraction["issues"])
            lines.append(
                f"- `{attraction['slug']}` — {attraction['name']} — ★{attraction['rating']} "
                f"(error {counts['error']}, warning {counts['warning']}, review {counts['review']})"
            )
        lines.append("")

    lines.extend(["## ყველაზე ხშირი საკითხები", ""])
    for code, count in payload["issue_codes"].items():
        lines.append(f"- `{code}`: {count}")

    lines.extend(["", "## დუბლირებული ფოტოები", ""])
    if payload["duplicate_images"]:
        for duplicate in payload["duplicate_images"]:
            refs = ", ".join(f"`{value}`" for value in duplicate["references"][:12])
            suffix = " …" if len(duplicate["references"]) > 12 else ""
            lines.append(f"- {duplicate['count']} გამოყენება: {refs}{suffix}")
    else:
        lines.append("- დუბლირებული ფაილები ვერ მოიძებნა.")

    return "\n".join(lines) + "\n"


def build_audit() -> dict[str, Any]:
    files = sorted(CONTENT_DIR.glob("*.yml"))
    known_slugs = {path.stem for path in files}
    exact_index = load_exact_image_index()
    attractions = [audit_file(path, known_slugs, exact_index) for path in files]

    issue_codes: collections.Counter[str] = collections.Counter()
    levels: collections.Counter[str] = collections.Counter()
    ratings: collections.Counter[str] = collections.Counter()
    regions: dict[str, Any] = {}
    hashes: dict[str, list[str]] = collections.defaultdict(list)
    primary_exact = 0
    primary_total = 0
    missing_primary = 0
    low_resolution = 0

    for attraction in attractions:
        ratings[str(attraction.get("rating"))] += 1
        local_levels: collections.Counter[str] = collections.Counter()
        for current in attraction["issues"]:
            issue_codes[current["code"]] += 1
            levels[current["level"]] += 1
            local_levels[current["level"]] += 1
        for media in attraction["media"]:
            if media["slot"] == "primary":
                if media.get("image"):
                    primary_total += 1
                    primary_exact += int(bool(media.get("verified_exact_metadata")))
                else:
                    missing_primary += 1
            if media.get("width") and media.get("height") and (media["width"] < 800 or media["height"] < 500):
                low_resolution += 1
            if media.get("sha256"):
                hashes[media["sha256"]].append(f"{attraction['slug']}:{media['slot']}")
        region = str(attraction.get("region"))
        bucket = regions.setdefault(region, {"count": 0, "errors": 0, "warnings": 0, "reviews": 0, "items": []})
        bucket["count"] += 1
        bucket["errors"] += local_levels["error"]
        bucket["warnings"] += local_levels["warning"]
        bucket["reviews"] += local_levels["review"]
        bucket["items"].append(attraction)

    duplicates = [
        {"sha256": digest, "count": len(references), "references": references}
        for digest, references in hashes.items()
        if len({reference.split(":", 1)[0] for reference in references}) > 1
    ]
    duplicates.sort(key=lambda item: (-item["count"], item["sha256"]))

    return {
        "generated_on": "2026-08-28",
        "summary": {
            "attractions": len(attractions),
            "regions": len({item.get("region") for item in attractions}),
            "errors": levels["error"],
            "warnings": levels["warning"],
            "reviews": levels["review"],
            "primary_exact": primary_exact,
            "primary_total": primary_total,
            "missing_primary": missing_primary,
            "low_resolution_media": low_resolution,
            "duplicate_image_groups": len(duplicates),
        },
        "rating_distribution": dict(sorted(ratings.items(), key=lambda item: item[0])),
        "issue_codes": dict(issue_codes.most_common()),
        "duplicate_images": duplicates,
        "regions": regions,
        "attractions": attractions,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=REPORTS_DIR / "attraction-content-audit.json")
    parser.add_argument("--markdown", type=Path, default=REPORTS_DIR / "ATTRACTION_CONTENT_AUDIT.md")
    args = parser.parse_args()

    payload = build_audit()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"JSON: {args.json}")
    print(f"Markdown: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
