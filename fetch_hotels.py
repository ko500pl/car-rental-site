# -*- coding: utf-8 -*-
"""სასტუმროების მოძიება OpenStreetMap-იდან (Overpass API) ქალაქების გარშემო.
მონაცემები ODbL ლიცენზიით — საიტზე მითითებულია „© OpenStreetMap contributors“.
    python3 fetch_hotels.py
"""
import json
import time
import urllib.parse
import urllib.request

import yaml

from yaml_io import dump

UA = "FleetHouseSiteBot/1.0 (travel site; contact via site)"
OP = "https://overpass-api.de/api/interpreter"

BUDGET = {"hostel": "low", "guest_house": "low", "apartment": "mid",
          "motel": "low", "hotel": "mid", "chalet": "mid", "resort": "high"}


def q(lat, lon, r=5000):
    return f"""[out:json][timeout:25];
(nwr["tourism"~"^(hotel|guest_house|hostel|apartment|chalet|motel)$"]["name"]
   (around:{r},{lat},{lon}););
out center tags 40;"""


def fetch(lat, lon):
    for attempt in range(3):
        try:
            body = urllib.parse.urlencode({"data": q(lat, lon)}).encode()
            req = urllib.request.Request(OP, data=body, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8")).get("elements", [])
        except Exception:
            time.sleep(4 * (attempt + 1))
    return []


def rank(e):
    t = e.get("tags", {})
    stars = t.get("stars", "")
    s = 0
    if stars.replace(".", "").isdigit():
        s += float(stars)
    if t.get("website") or t.get("contact:website"):
        s += 1
    if t.get("phone") or t.get("contact:phone"):
        s += .5
    return -s


def main():
    places = yaml.safe_load(open("content/settings/places.yml", encoding="utf-8"))["places"]
    out = {}
    have = {}
    try:
        have = yaml.safe_load(open("content/settings/hotels.yml", encoding="utf-8"))["towns"]
    except Exception:
        pass
    for p in places:
        if p["kind"] != "city":
            continue
        if have.get(p["key"]):
            out[p["key"]] = have[p["key"]]
            continue
        els = fetch(p["lat"], p["lon"])
        seen, rows = set(), []
        for e in sorted(els, key=rank):
            t = e.get("tags", {})
            name = t.get("name:en") or t.get("name")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            ty = t.get("tourism", "hotel")
            stars = t.get("stars", "")
            b = "high" if stars in ("4", "4.5", "5") else BUDGET.get(ty, "mid")
            la = e.get("lat") or (e.get("center") or {}).get("lat")
            lo = e.get("lon") or (e.get("center") or {}).get("lon")
            if la is None:
                continue
            rows.append({"n": name[:60], "ty": ty, "b": b,
                         "la": round(la, 5), "lo": round(lo, 5),
                         **({"st": stars} if stars else {})})
            if len(rows) >= 12:
                break
        out[p["key"]] = rows
        print(f"  {p['key']:epr20s}" if False else f"  {p['key']:20s} {len(rows)}")
        time.sleep(1.2)
    dump("content/settings/hotels.yml", {"note": "© OpenStreetMap contributors (ODbL)",
                                         "towns": out})
    total = sum(len(v) for v in out.values())
    print(f"✔ {total} სასტუმრო {len(out)} ქალაქში")


if __name__ == "__main__":
    main()
