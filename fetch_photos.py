# -*- coding: utf-8 -*-
"""ფოტოების მოძიება Wikimedia Commons-იდან და ლოკალურად შენახვა.

ყველა სურათი თავისუფალი ლიცენზიითაა; ავტორი და ლიცენზია ინახება YAML-ში
და გამოისახება გვერდზე — ეს ლიცენზიის მოთხოვნაა.

    python3 fetch_photos.py            # მხოლოდ ის, რასაც ჯერ ფოტო არ აქვს
    python3 fetch_photos.py --all      # ყველაფერი თავიდან
"""
import glob
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import yaml
from PIL import Image

from yaml_io import dump

UA = "FleetHouseSiteBot/1.0 (https://fleethouse.ge; contact via site) python-urllib"
WP = "https://en.wikipedia.org/w/api.php"
CM = "https://commons.wikimedia.org/w/api.php"
OUT = os.path.join("static", "photos")
MAXW = 1100
BAD = re.compile(r"(map|flag|coat[_ ]of[_ ]arms|logo|seal|diagram|plan|blueprint|"
                 r"location|locator|chart|graph|stamp|banner|icon)", re.I)


def get(url, params, tries=3):
    q = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url + "?" + q, headers={"User-Agent": UA})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if i == tries - 1:
                return {}
            time.sleep(1.5 * (i + 1))
    return {}


def hav(a1, o1, a2, o2):
    R, t = 6371.0, math.pi / 180
    dA, dO = (a2 - a1) * t, (o2 - o1) * t
    x = math.sin(dA / 2) ** 2 + math.cos(a1 * t) * math.cos(a2 * t) * math.sin(dO / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()[:120]


def commons_meta(title):
    """ფაილის ლიცენზია, ავტორი და thumbnail."""
    d = get(CM, {"action": "query", "titles": title, "prop": "imageinfo",
                 "iiprop": "url|extmetadata|size", "iiurlwidth": MAXW})
    for p in (d.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        if re.search(r"fair use|non[- ]free", lic, re.I):
            return None
        return {
            "url": ii.get("thumburl") or ii.get("url"),
            "author": strip_html(em.get("Artist", {}).get("value", "")) or "Wikimedia Commons",
            "license": strip_html(lic) or "see source",
            "license_url": em.get("LicenseUrl", {}).get("value", ""),
            "source": ii.get("descriptionurl", ""),
            "w": ii.get("width", 0),
        }
    return None


def from_wikipedia(name, lat, lon):
    """ვიკიპედიის სტატიის მთავარი სურათი — კოორდინატით გადამოწმებული."""
    s = get(WP, {"action": "query", "list": "search", "srsearch": name,
                 "srlimit": 3, "srnamespace": 0})
    hits = [h["title"] for h in s.get("query", {}).get("search", [])]
    if not hits:
        return None
    d = get(WP, {"action": "query", "titles": "|".join(hits),
                 "prop": "coordinates|pageimages", "piprop": "original"})
    for p in (d.get("query", {}).get("pages") or {}).values():
        co = (p.get("coordinates") or [None])[0]
        img = (p.get("original") or {}).get("source")
        if not co or not img:
            continue
        if hav(lat, lon, co["lat"], co["lon"]) > 6:      # არასწორი სტატია
            continue
        fn = urllib.parse.unquote(img.rsplit("/", 1)[-1])
        if BAD.search(fn):
            continue
        m = commons_meta("File:" + fn)
        if m:
            return m
    return None


def from_geosearch(lat, lon):
    """Commons-ის გეოძებნა — სივრცობრივად სწორი, თუ სტატია ვერ მოიძებნა."""
    for radius in (900, 2500, 6000):
        d = get(CM, {"action": "query", "generator": "geosearch",
                     "ggscoord": f"{lat}|{lon}", "ggsradius": radius,
                     "ggslimit": 12, "ggsnamespace": 6,
                     "prop": "imageinfo", "iiprop": "url|extmetadata",
                     "iiurlwidth": MAXW})
        pages = list((d.get("query", {}).get("pages") or {}).values())
        pages.sort(key=lambda p: p.get("index", 99))
        for p in pages:
            t = p.get("title", "")
            if BAD.search(t):
                continue
            m = commons_meta(t)
            if m and m.get("w", 0) >= 700:
                return m
    return None


def relevant_source(meta, name):
    """Reject a merely nearby photograph unless its Commons page identifies the place."""
    source = urllib.parse.unquote((meta or {}).get("source", "")).lower().replace("_", " ")
    words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if len(w) >= 4]
    return bool(words and sum(w in source for w in words) >= min(2, len(words)))


def save(slug, url):
    os.makedirs(OUT, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
    tmp = os.path.join(OUT, slug + ".src")
    with open(tmp, "wb") as f:
        f.write(raw)
    im = Image.open(tmp)
    im = im.convert("RGB")
    im.thumbnail((MAXW, MAXW))
    path = os.path.join(OUT, slug + ".webp")
    im.save(path, "WEBP", quality=70, method=5)
    os.remove(tmp)
    return "/assets/photos/" + slug + ".webp", os.path.getsize(path)


def one(path, force):
    slug = os.path.basename(path)[:-4]
    a = yaml.safe_load(open(path, encoding="utf-8"))
    if a.get("image") and not force:
        return slug, "skip", 0
    lat, lon = float(a["lat"]), float(a["lon"])
    name = a["en"]["name"]
    m = from_wikipedia(name, lat, lon)
    if not m:
        nearby = from_geosearch(lat, lon)
        m = nearby if relevant_source(nearby, name) else None
    if not m or not m.get("url"):
        return slug, "none", 0
    try:
        rel, size = save(slug, m["url"])
    except Exception as e:
        return slug, "err:" + str(e)[:40], 0
    a["image"] = rel
    a["image_credit"] = {"author": m["author"], "license": m["license"],
                         "license_url": m["license_url"], "source": m["source"]}
    dump(path, a)
    return slug, "ok", size


def main():
    force = "--all" in sys.argv
    files = sorted(glob.glob("content/attractions/*.yml"))
    only = [x for x in sys.argv[1:] if not x.startswith("--")]
    if only:
        files = [f for f in files if os.path.basename(f)[:-4] in only]
    ok = none = err = skip = 0
    total = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for slug, st, size in ex.map(lambda f: one(f, force), files):
            if st == "ok":
                ok += 1; total += size
            elif st == "none":
                none += 1; print("  no image:", slug)
            elif st == "skip":
                skip += 1
            else:
                err += 1; print("  ", slug, st)
    print(f"✔ ფოტო: {ok} ჩამოტვირთული, {skip} უკვე იყო, {none} ვერ მოიძებნა, "
          f"{err} შეცდომა · {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
