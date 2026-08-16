from dataclasses import dataclass, field

LANGS = ("ka", "en", "ru", "fa", "he", "ar")
PUBLIC = {None, "published"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def require(self, ok, message):
        if not ok:
            self.errors.append(message)


def is_public(item):
    return item.get("status") in PUBLIC and not item.get("draft", False)


def validate(site, cars, regions, attractions, routes, pages, posts):
    r = Report()
    rate, step = site.get("usd_rate"), site.get("usd_rounding", 10)
    r.require(isinstance(rate, (int, float)) and rate > 0, "settings/site.yml: usd_rate must be positive")
    r.require(isinstance(step, (int, float)) and step > 0, "settings/site.yml: usd_rounding must be positive")

    groups = {"car": cars, "region": regions, "attraction": attractions,
              "route": routes, "page": pages, "post": posts}
    for kind, items in groups.items():
        for slug, item in items.items():
            if not is_public(item):
                continue
            missing = [lang for lang in LANGS if lang not in item]
            r.require(not missing, f"{kind}/{slug}: missing languages: {', '.join(missing)}")

    for slug, car in cars.items():
        if not is_public(car):
            continue
        try:
            prices = [int(car[k]) for k in ("price_1_6", "price_7_29", "price_30")]
            r.require(all(v >= 0 for v in prices), f"car/{slug}: prices cannot be negative")
            r.require(prices[0] >= prices[1] >= prices[2], f"car/{slug}: expected 1–6 ≥ 7–29 ≥ 30+ day prices")
            r.require(1 <= int(car["seats"]) <= 20, f"car/{slug}: seats must be 1–20")
            r.require(80 <= int(car["clearance"]) <= 500, f"car/{slug}: clearance must be 80–500 mm")
        except (KeyError, TypeError, ValueError) as exc:
            r.errors.append(f"car/{slug}: invalid numeric field ({exc})")

    for slug, attraction in attractions.items():
        if not is_public(attraction):
            continue
        r.require(attraction.get("region") in regions and is_public(regions[attraction["region"]]),
                  f"attraction/{slug}: missing or unpublished region '{attraction.get('region')}'")
        for ref in attraction.get("nearby", []):
            r.require(ref in attractions and is_public(attractions[ref]),
                      f"attraction/{slug}: nearby reference '{ref}' is missing or unpublished")
    for slug, route in routes.items():
        if not is_public(route):
            continue
        for ref in route.get("waypoints", []):
            r.require(ref in attractions and is_public(attractions[ref]),
                      f"route/{slug}: waypoint '{ref}' is missing or unpublished")

    # "000000" without spaces matters too: the whatsapp field stores a bare
    # E.164 number, and a placeholder there silently breaks the main
    # conversion path while every displayed number looks correct.
    placeholders = ("example.", "000 000", "00 00 00", "/example", "000000")
    for key in ("phone", "mobile", "email", "software_email", "whatsapp"):
        if any(x in str(site.get(key, "")).lower() for x in placeholders):
            r.warnings.append(f"settings/site.yml: '{key}' still contains placeholder data")
    # A rental site with no reachable number cannot convert at all.
    if not str(site.get("phone_e164", "")).strip():
        r.warnings.append("settings/site.yml: 'phone_e164' is empty; no contact number is published")
    if any("example" in str(x).lower() for x in site.get("social", [])):
        r.warnings.append("settings/site.yml: social links still contain placeholder data")
    missing_images = sum(1 for c in cars.values() if is_public(c) and not c.get("image"))
    if missing_images:
        r.warnings.append(f"cars: {missing_images} published records have no main image")
    return r
