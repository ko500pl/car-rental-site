# -*- coding: utf-8 -*-
"""გალერეა: +3 დამატებითი ფოტო თითო ღირსშესანიშნაობაზე (Wikimedia Commons).
    python3 fetch_gallery.py            # მხოლოდ ის, ვისაც გალერეა არ აქვს
"""
import glob
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import yaml
from PIL import Image

import fetch_photos as FP
from yaml_io import dump

OUT = FP.OUT
WANT = 3           # დამატებითი ფოტო მთავარის გარდა
GW = 900           # გალერეის სიგანე


def save_g(slug, i, url):
    os.makedirs(OUT, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": FP.UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
    tmp = os.path.join(OUT, f"{slug}-g{i}.src")
    open(tmp, "wb").write(raw)
    im = Image.open(tmp).convert("RGB")
    im.thumbnail((GW, GW))
    path = os.path.join(OUT, f"{slug}-{i}.webp")
    im.save(path, "WEBP", quality=62, method=5)
    os.remove(tmp)
    return "/assets/photos/" + f"{slug}-{i}.webp", os.path.getsize(path)


def name_words(a):
    names = [a.get("en", {}).get("name", ""), a.get("ka", {}).get("name", "")]
    words = set()
    for name in names:
        words.update(w.lower() for w in re.findall(r"[^\W_]+", name, re.UNICODE) if len(w) >= 4)
    return words


def relevant(title, source, words):
    hay = urllib.parse.unquote((title + " " + source).replace("_", " ")).lower()
    return any(w in hay for w in words)


def candidates(a):
    """Commons-ის გეოძებნის ყველა შესაფერისი ფაილი, მთავარი ფოტოს გარდა."""
    la, lo = float(a["lat"]), float(a["lon"])
    main_src = (a.get("image_credit") or {}).get("source", "")
    out, seen, words = [], set(), name_words(a)
    # Name search is preferred: nearby photos can depict an unrelated field or building.
    query = a.get("en", {}).get("name", "") + " Georgia"
    searches = [FP.get(FP.CM, {"action": "query", "generator": "search",
                               "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": 30,
                               "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": GW})]
    for radius in (700, 2000, 5000):
        searches.append(FP.get(FP.CM, {"action": "query", "generator": "geosearch",
                           "ggscoord": f"{la}|{lo}", "ggsradius": radius,
                           "ggslimit": 20, "ggsnamespace": 6,
                           "prop": "imageinfo", "iiprop": "url|extmetadata|size",
                           "iiurlwidth": GW}))
    for d in searches:
        pages = list((d.get("query", {}).get("pages") or {}).values())
        pages.sort(key=lambda p: p.get("index", 99))
        for p in pages:
            t = p.get("title", "")
            if FP.BAD.search(t) or t in seen:
                continue
            seen.add(t)
            ii = (p.get("imageinfo") or [None])[0]
            if not ii or ii.get("width", 0) < 640:
                continue
            em = ii.get("extmetadata", {})
            lic = em.get("LicenseShortName", {}).get("value", "")
            if FP.re.search(r"fair use|non[- ]free", lic, FP.re.I):
                continue
            src = ii.get("descriptionurl", "")
            if not relevant(t, src, words):
                continue
            if src and src == main_src:
                continue
            out.append({"url": ii.get("thumburl") or ii.get("url"),
                        "author": FP.strip_html(em.get("Artist", {}).get("value", "")) or "Wikimedia Commons",
                        "license": FP.strip_html(lic) or "see source",
                        "license_url": em.get("LicenseUrl", {}).get("value", ""),
                        "source": src})
            if len(out) >= WANT + 3:
                return out
    return out


def one(path):
    slug = os.path.basename(path)[:-4]
    a = yaml.safe_load(open(path, encoding="utf-8"))
    rows, size = list(a.get("gallery") or []), 0
    if len(rows) >= WANT:
        return slug, "skip", 0
    existing = {x.get("source", "") for x in rows}
    for c in candidates(a):
        if c.get("source") in existing:
            continue
        i = len(rows) + 1
        try:
            rel, sz = save_g(slug, i, c["url"])
        except Exception:
            continue
        rows.append({"image": rel, "author": c["author"], "license": c["license"],
                     "license_url": c["license_url"], "source": c["source"]})
        existing.add(c.get("source", ""))
        size += sz
        if len(rows) >= WANT:
            break
    if not rows:
        return slug, "none", 0
    a["gallery"] = rows
    dump(path, a)
    return slug, f"ok:{len(rows)}", size


def main():
    files = sorted(glob.glob("content/attractions/*.yml"))
    only = [x for x in sys.argv[1:] if not x.startswith("--")]
    if only:
        files = [f for f in files if os.path.basename(f)[:-4] in only]
    ok = none = skip = 0
    total = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for slug, st, size in ex.map(one, files):
            if st.startswith("ok"):
                ok += 1; total += size
            elif st == "none":
                none += 1; print("  no gallery:", slug)
            else:
                skip += 1
    print(f"✔ გალერეა: {ok} ადგილი, {none} ვერ მოიძებნა, {skip} უკვე იყო · {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
