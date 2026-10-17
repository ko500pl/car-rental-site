"""Compact knowledge catalog for the site's AI trip assistant.

Everything the assistant may state comes from content/ through this file:
places with drive times, the fleet with prices, the ready-made routes, the
rental policy and the contact details. The Worker (worker/src) loads it from
/assets/ai-catalog.json and answers tool calls against it, so the model picks
from facts instead of inventing them.

One file per language (ai-catalog.<lang>.json): names and summaries in six
languages at once made the file 800 KB, and the Worker only ever needs the
language of the conversation. build.py writes them into dist/assets/ on every
build; nothing is committed.
Run alone:  python scripts/build_ai_catalog.py [out_dir]
"""
from __future__ import annotations

import glob
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ("ka", "en", "ru", "fa", "he", "ar")


def _load(path):
    with open(path, encoding="utf-8-sig") as f:
        return yaml.safe_load(f) or {}


def _slug(path):
    return os.path.splitext(os.path.basename(path))[0]


def _public(d):
    return d.get("status", "published") == "published" and not d.get("draft")


def _minutes(hhmm):
    """'5:00' / '03:30' / 90 → minutes."""
    if hhmm in (None, ""):
        return None
    if isinstance(hhmm, (int, float)):
        return int(hhmm)
    parts = str(hhmm).split(":")
    try:
        return int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
    except ValueError:
        return None


def _names(d, key="name"):
    return {l: (d.get(l) or {}).get(key, "") for l in LANGS}


def _num(v):
    """YAML written by the CMS stores numbers as strings ('310', '1.5')."""
    if v in (None, ""):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return int(f) if f == int(f) else f


def places():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/attractions/*.yml"))):
        d = _load(p)
        if not _public(d):
            continue
        out.append({
            "s": _slug(p),
            "n": _names(d),
            "t": d.get("type"),
            "r": d.get("region"),
            "la": d.get("lat"), "lo": d.get("lon"),
            "km": _num(d.get("distance_tbilisi_km")),
            "dm": _minutes(d.get("drive_time_tbilisi")),
            "vh": _num(d.get("visit_hours")),
            "rt": _num(d.get("rating")),
            "cc": d.get("car_category"),
            "road": d.get("road"),
            "fee": d.get("entry_fee"),
            "season": d.get("best_season"),
            "uns": bool(d.get("unesco")),
            "short": {l: (d.get(l) or {}).get("short", "")[:160] for l in LANGS},
        })
    return out


def cars():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/cars/*.yml"))):
        d = _load(p)
        if not _public(d) or d.get("is_public") is False:
            continue
        out.append({
            "s": _slug(p),
            "n": (d.get("en") or {}).get("name") or _slug(p),
            "cat": d.get("category"),
            "seats": _num(d.get("seats")),
            "tr": d.get("transmission"),
            "drive": d.get("drive"),
            "cl": _num(d.get("clearance")),
            "p": [_num(d.get("price_1_6")), _num(d.get("price_7_29")), _num(d.get("price_30"))],
            "dep": _num(d.get("deposit")),
            "fuel": _num(d.get("fuel_100km")),
        })
    return out


def routes():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/routes/*.yml"))):
        d = _load(p)
        if not _public(d):
            continue
        out.append({
            "s": _slug(p),
            "n": _names(d),
            "days": _num(d.get("days")),
            "purpose": d.get("purpose"),
            "cc": d.get("car_category"),
            "km": _num(d.get("distance_km")),
            "dm": _minutes(d.get("drive_time_total")),
            "wp": list(d.get("waypoints") or []),
            "diff": d.get("difficulty"),
            "season": d.get("best_season"),
        })
    return out


def policy():
    r = _load(os.path.join(ROOT, "content/settings/rental_policy.yml"))
    keep = ("min_driver_age", "min_licence_years", "licence_accepted", "passport_required",
            "mileage", "deposit", "fuel_policy", "delivery", "one_way", "min_rental_days",
            "young_driver", "insurance", "cross_border", "cancellation", "extras_gel", "support")
    return {k: r[k] for k in keep if k in r}


def site():
    s = _load(os.path.join(ROOT, "content/settings/site.yml"))
    return {
        "url": s.get("site_url"),
        "brand": s.get("rental_brand"),
        "phone": s.get("phone"),
        "whatsapp": str(s.get("whatsapp") or s.get("phone_e164") or "").replace("+", ""),
        "address": {l: (s.get("address") or {}).get(l, {}) for l in LANGS},
        "hours": f'{s.get("opens")}–{s.get("closes")}',
        "usd_rate": s.get("usd_rate"),
    }


def labels():
    t = _load(os.path.join(ROOT, "content/settings/travel.yml"))
    regions = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "content/regions/*.yml"))):
        d = _load(p)
        regions[_slug(p)] = {l: (d.get(l) or {}).get("name", _slug(p)) for l in LANGS}
    cats = {}
    for c in _load(os.path.join(ROOT, "content/settings/categories.yml")).get("categories", []):
        cats[c["key"]] = {l: c.get(l, c["key"]) for l in LANGS}
    return {
        "types": {k: {l: t[l]["type"].get(k, k) for l in LANGS} for k in t["en"]["type"]},
        "road": {k: {l: t[l]["road"].get(k, k) for l in LANGS} for k in t["en"]["road"]},
        "regions": regions,
        "car_categories": cats,
    }


def build():
    return {
        "v": 1,
        "places": places(),
        "cars": cars(),
        "routes": routes(),
        "policy": policy(),
        "site": site(),
        "labels": labels(),
    }


def _pick(v, lang):
    """Collapse {ka,en,...} tables to the one language, recursively."""
    if isinstance(v, dict):
        if set(v) == set(LANGS):
            return v[lang]
        return {k: _pick(x, lang) for k, x in v.items()}
    if isinstance(v, list):
        return [_pick(x, lang) for x in v]
    return v


def for_lang(cat, lang):
    out = _pick(cat, lang)
    out["lang"] = lang
    return out


def dumps(cat):
    return json.dumps(cat, ensure_ascii=False, separators=(",", ":"))


def write_all(out_dir, cat=None):
    cat = cat or build()
    os.makedirs(out_dir, exist_ok=True)
    sizes = {}
    for lang in LANGS:
        path = os.path.join(out_dir, f"ai-catalog.{lang}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(dumps(for_lang(cat, lang)))
        sizes[lang] = os.path.getsize(path) // 1024
    return cat, sizes


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist/assets")
    cat, sizes = write_all(out_dir)
    print(f"ai-catalog: {len(cat['places'])} places, {len(cat['cars'])} cars, "
          f"{len(cat['routes'])} routes → {out_dir}/ai-catalog.<lang>.json {sizes} KB")
