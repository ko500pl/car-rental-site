#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
სტატიკური საიტის გენერატორი — კონტენტი იკითხება content/*.yml-იდან (ადმინიდან იმართება).
გამოყენება:  python3 build.py [outdir]
"""
import functools
import subprocess
import glob, hashlib, html, json, os, re, shutil, sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml
import markdown as md
from sitegen.validation import is_public, validate

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

ALL_LANGS = ["en", "ka", "ru", "fa", "he", "ar"]
# საიტის ძირითადი (root) ენა — rentup.ge/ ამ ენაზე იხსნება,
# დანარჩენები /{lang}/ ქვესაქაღალდეებში.
ROOT_LANG = "en"
LANG_LABEL = {"ka": "ქართული", "en": "English", "ru": "Русский",
              "fa": "فارسی", "he": "עברית", "ar": "العربية"}
LANG_SHORT = {"ka": "KA", "en": "EN", "ru": "RU", "fa": "FA", "he": "HE", "ar": "AR"}
OG_LOCALE = {"ka": "ka_GE", "en": "en_US", "ru": "ru_RU",
             "fa": "fa_IR", "he": "he_IL", "ar": "ar_AE"}
LANG_DIR = {"ka": "ltr", "en": "ltr", "ru": "ltr", "fa": "rtl", "he": "rtl", "ar": "rtl"}
# დამატებითი Google-ფონტი ენის მიხედვით
LANG_FONT = {"fa": "Vazirmatn:wght@400;500;600;700",
             "he": "Noto+Sans+Hebrew:wght@400;500;600;700",
             "ar": "Noto+Kufi+Arabic:wght@400;500;600;700"}
LANG_FONT_STACK = {"fa": '"Vazirmatn","Noto Sans Arabic",',
                   "he": '"Noto Sans Hebrew","Noto Sans",',
                   "ar": '"Noto Kufi Arabic","Noto Sans Arabic",'}

BOOKING_TEXT = {
    "ka": {"start": "დაწყება", "end": "დასრულება", "drivers": "მძღოლები", "book": "დაჯავშნის მოთხოვნა"},
    "en": {"start": "Start", "end": "End", "drivers": "Drivers", "book": "Request booking"},
    "ru": {"start": "Начало", "end": "Окончание", "drivers": "Водители", "book": "Запросить бронирование"},
    "fa": {"start": "شروع", "end": "پایان", "drivers": "رانندگان", "book": "درخواست رزرو"},
    "he": {"start": "התחלה", "end": "סיום", "drivers": "נהגים", "book": "בקשת הזמנה"},
    "ar": {"start": "البداية", "end": "النهاية", "drivers": "السائقون", "book": "طلب الحجز"},
}

NAV_HIDDEN = {"account", "planner", "map"}
PAGE_ORDER = ["index", "fleet", "map", "planner", "terms", "faq", "blog",
              "community", "about", "contact", "software", "account"]
PAGE_SLUG = {"index": "", "account": "account/", "fleet": "fleet/", "pricing": "pricing/", "map": "map/",
             "planner": "planner/", "terms": "terms/", "faq": "faq/", "blog": "blog/",
             "community": "community/", "about": "about/", "contact": "contact/", "software": "fleet-management-software/",
             "card": "business-card/"}

TODAY = date.today().isoformat()
E = lambda s: html.escape(str(s), quote=True)                # noqa: E731
J = lambda o: json.dumps(o, ensure_ascii=False, indent=2)    # noqa: E731
JC = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))  # noqa: E731



def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


SITE = load("content/settings/site.yml")
DESIGN = load("content/settings/design.yml")
UI = load("content/settings/ui.yml")
META = load("content/settings/meta.yml")
SPECS = load("content/settings/specs.yml")
PLANNER_LANGS = set(load("content/settings/planner.yml"))
MAPS = load("content/settings/maps.yml") if os.path.exists("content/settings/maps.yml") else {}
BOOKING = load("content/settings/booking.yml") if os.path.exists("content/settings/booking.yml") else {}
HOME_HERO = load("content/settings/home_hero.yml")
CATS = load("content/settings/categories.yml")["categories"]


def load_opt(path, default=None):
    """SEO content packs are optional — the site must build without them."""
    return load(path) if os.path.exists(path) else (default if default is not None else {})


# ── SEO content packs (docs/seo/*) ────────────────────────────────────────
RENTAL_POLICY = load_opt("content/settings/rental_policy.yml")
SEO_META = load_opt("content/settings/seo_meta.yml")
SEO_UI = load_opt("content/settings/seo_ui.yml")
SEO_CAR_RENTAL = load_opt("content/settings/seo_car_rental.yml")
SEO_CATEGORIES = load_opt("content/settings/seo_categories.yml")
SEO_TRIP_PLANNER = load_opt("content/settings/seo_trip_planner.yml")
SEO_TRUST = load_opt("content/settings/seo_trust.yml")
KA_FORMS = load_opt("content/settings/ka_forms.yml")
ITINERARIES = {os.path.splitext(os.path.basename(p))[0]: load(p)
               for p in sorted(glob.glob("content/itineraries/*.yml"))}
GUIDES = {os.path.splitext(os.path.basename(p))[0]: load(p)
          for p in sorted(glob.glob("content/guides/*.yml"))}
# Landing pages exist for every fleet category that has real cars behind it.
SEO_CATEGORY_ORDER = ("economy", "suv", "offroad", "minivan", "business", "van")


def ka_case(name, case="loc"):
    """Georgian place names take case endings, and gluing them on with a hyphen
    ("ბათუმი-ში") is the clearest sign of machine-generated text. Hand-checked
    forms live in content/settings/ka_forms.yml; the rules below are the
    fallback for anything not in that table.

    case: 'gen' -ის · 'loc' -ში · 'abl' -დან · 'dat' -ს
    """
    if not name:
        return ""
    entry = (KA_FORMS.get("places") or {}).get(name) or (KA_FORMS.get("regions") or {}).get(name)
    if isinstance(entry, dict) and entry.get(case):
        return entry[case]
    # Multi-word names decline on the last word only.
    head, _, last = name.rpartition(" ")
    if head:
        return (head + " " + ka_case(last, case)).strip()
    if name.endswith("ი"):          # consonantal stem: the -ი drops out
        stem = name[:-1]
        return {"gen": stem + "ის", "loc": stem + "ში",
                "abl": stem + "იდან", "dat": stem + "ს"}[case]
    if name.endswith("ა"):          # -ა stem: kept in the locative, dropped elsewhere
        stem = name[:-1]
        return {"gen": stem + "ის", "loc": name + "ში",
                "abl": stem + "იდან", "dat": name + "ს"}[case]
    if name[-1] in "ეოუ":           # vowel stems keep the vowel
        return {"gen": name + "ს", "loc": name + "ში",
                "abl": name + "დან", "dat": name + "ს"}[case]
    return {"gen": name + "ის", "loc": name + "ში",
            "abl": name + "იდან", "dat": name + "ს"}[case]


def abs_url(u):
    """Absolutise a site-relative path. Already-absolute URLs pass through — a
    gallery photo hosted on Wikimedia must not become rentup.gehttps://…"""
    if not u:
        return None
    return (SITE_URL + u) if u.startswith("/") else u


class _Blanks(dict):
    """format_map helper: an unsupplied placeholder renders as nothing rather
    than raising, so a missing value can never leak `{name}` onto a page."""

    def __missing__(self, key):
        return ""


def _ka_variants(fmt):
    """Georgian templates need declined forms, not a hyphen-glued suffix. For
    every string value we also expose {x_gen}, {x_loc}, {x_abl} and {x_dat}, so
    a template writes "{region_loc}" instead of the wrong "{region}-ში"."""
    out = dict(fmt or {})
    for k, v in list(out.items()):
        if isinstance(v, str) and v and not k.endswith(("_gen", "_loc", "_abl", "_dat")):
            for c in ("gen", "loc", "abl", "dat"):
                out.setdefault(f"{k}_{c}", ka_case(v, c))
    return out


def _fmt(s, fmt, lang=None):
    """Substitute {placeholders} and tidy what an empty substitution leaves behind."""
    if not s:
        return ""
    if lang == "ka":
        fmt = _ka_variants(fmt)
    try:
        s = str(s).format_map(_Blanks(fmt or {}))
    except (IndexError, ValueError):
        return str(s)
    # An emptied placeholder can strand its punctuation: "Routes from  — RentUp".
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([,.;:!?»])", r"\1", s)
    s = re.sub(r"[ \t]*[—–·|,]\s*(?=[—–·|,]|$)", "", s)
    return s.strip(" \t—–·|,")


def su(key, lang, *path, **fmt):
    """seo_ui.yml lookup: su('nearby_places', lang) or su('road', lang, 'gravel').

    Strings may carry {placeholders} — pass them as keywords:
    su('popular_routes_from', lang, place='Batumi')."""
    node = SEO_UI.get(key)
    for p in path:
        if not isinstance(node, dict):
            return ""
        node = node.get(p)
    if isinstance(node, dict):
        node = node.get(lang) or node.get("en") or ""
    return _fmt(node, fmt, lang) if fmt else (node or "")


def seo_meta(template, lang, **fmt):
    """seo_meta.yml → (title, description). Falls back to ('','') when absent."""
    t = (SEO_META.get("templates") or {}).get(template)
    if not isinstance(t, dict):
        return "", ""
    # nested variants: attraction.by_type.<type>, route.by_purpose.<purpose>,
    # car_rental_location.<city|airport>
    for group, key in (("by_type", fmt.get("type")), ("by_purpose", fmt.get("purpose")),
                       (None, fmt.get("kind"))):
        if group and group in t:
            t = t[group].get(key) or t[group].get("default") or t.get("default") or {}
            break
        if group is None and key and key in t:
            t = t[key]
            break
    else:
        if "default" in t and lang not in t:
            t = t["default"]
    node = t.get(lang) or t.get("en") or {}
    title = _fmt(node.get("title", ""), fmt, lang)
    return _trim_title(title), _fmt(node.get("description", ""), fmt, lang)


def _trim_title(title, limit=70):
    """Keep a title under the SERP cut without ever truncating mid-word.

    Titles here are built as clauses joined by " — " / " · " / " | ", the first
    clause always being the entity's own name. We drop whole trailing clauses,
    least important first, and never touch the first one — so a long name stays
    intact and simply loses its qualifiers."""
    if len(title) <= limit:
        return title
    parts = re.split(r"\s+(?=[—–·|]\s)", title)
    while len(parts) > 1 and len(" ".join(parts)) > limit:
        parts.pop()
    out = " ".join(parts).strip(" \t—–·|,")
    return out or title
# ══════════════════════════════════════════════ ფასის დანამატები (გამჭვირვალობა)
# წყარო: content/settings/booking.yml → season: / young_driver:.
# იგივე ციფრები მიდის FH_CFG-ში (JS) და ჩანს ავტომობილისა და ავტოპარკის გვერდზე.
def _bk_int(section, key, default):
    v = (BOOKING.get(section) or {}).get(key)
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


_PEAK_MONTHS = (BOOKING.get("season") or {}).get("peak_months")
SEASON_CFG = {
    "peakMonths": ([int(m) for m in _PEAK_MONTHS]
                   if isinstance(_PEAK_MONTHS, (list, tuple)) and _PEAK_MONTHS else [7, 8]),
    "peakPercent": _bk_int("season", "peak_percent", 15),
    "holidayPercent": _bk_int("season", "holiday_percent", 10),
}
YOUNG_DRIVER_CFG = {
    "underAge": _bk_int("young_driver", "under_age", 27),
    "minGel": _bk_int("young_driver", "min_gel", 15),
    "maxGel": _bk_int("young_driver", "max_gel", 25),
}

PAGES = {os.path.splitext(os.path.basename(p))[0]: load(p)
         for p in glob.glob("content/pages/*.yml")}
CARS = {os.path.splitext(os.path.basename(p))[0]: load(p)
        for p in sorted(glob.glob("content/cars/*.yml"))}

# Photos come from the rental program, not from this repository's YAML.
#
# `content/settings/car_photos.yml` is written by Fleet Freak's photo export
# and unzipped here together with the image files. Overlaying it -- rather than
# editing every car file -- keeps one owner for the mapping: the phone knows
# which photos belong to which model, and this build just reads the answer.
#
# Missing file, missing model or an empty list all mean "leave the car alone",
# so a site checked out without an export still builds exactly as before.
CAR_PHOTOS = (load("content/settings/car_photos.yml")
              if os.path.exists("content/settings/car_photos.yml") else {}) or {}
for _slug, _photos in CAR_PHOTOS.items():
    _car = CARS.get(_slug)
    if not _car or not isinstance(_photos, dict):
        continue
    # ტიპები ფრთხილად: ამ ფაილს ტელეფონი წერს, და ერთი არასწორი ველი
    # მთელ build-ს არ უნდა აჩერებდეს და არც სიმბოლო-სიმბოლო დაშლილი
    # gallery უნდა უშვებდეს გვერდზე.
    _main = _photos.get("image")
    if isinstance(_main, str) and _main.strip():
        _car["image"] = _main.strip()
    _gal = _photos.get("gallery")
    if isinstance(_gal, list):
        _clean = [g for g in _gal if isinstance(g, str) and g.strip()]
        if _clean:
            _car["gallery"] = _clean

CARS_ALL = CARS
CARS = {k: v for k, v in CARS.items() if is_public(v)}
CARS = dict(sorted(CARS.items(), key=lambda kv: kv[1].get("order", 999)))


def _price(value, fallback=0.0):
    """A YAML price cell as a number. Empty, missing or unparsable -> fallback."""
    try:
        return float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return fallback


# Price map handed to the browser so the booking dialog can quote a car without
# a round trip. The bands are the same three the rental program uses --
# 1+ / 7+ / 30+ nights -- so the site and the program never disagree on a price.
CAR_PRICES = {}
for _slug, _car in CARS.items():
    _p1 = _price(_car.get("price_1_6"))
    _p7 = _price(_car.get("price_7_29"), _p1) or _p1
    _p30 = _price(_car.get("price_30"), _p7) or _p7
    CAR_PRICES[_slug] = {"p1": _p1, "p7": _p7, "p30": _p30,
                         "dep": _price(_car.get("deposit"))}

POSTS = {os.path.splitext(os.path.basename(p))[0]: load(p)
         for p in sorted(glob.glob("content/posts/*.yml"))}
POSTS_ALL = POSTS
POSTS = {k: v for k, v in sorted(POSTS.items(),
                                 key=lambda kv: str(kv[1].get("date", "")), reverse=True)
         if is_public(v)}

REGIONS = {os.path.splitext(os.path.basename(p))[0]: load(p)
           for p in sorted(glob.glob("content/regions/*.yml"))}
REGIONS_ALL = REGIONS
REGIONS = {k: v for k, v in REGIONS.items() if is_public(v)}
REGIONS = dict(sorted(REGIONS.items(), key=lambda kv: kv[1].get("order", 999)))
ATTRACTIONS = {os.path.splitext(os.path.basename(p))[0]: load(p)
               for p in sorted(glob.glob("content/attractions/*.yml"))}
ATTRACTIONS_ALL = ATTRACTIONS
ATTRACTIONS = {k: v for k, v in ATTRACTIONS.items() if is_public(v)}
ATTRACTIONS = dict(sorted(ATTRACTIONS.items(),
                          key=lambda kv: (kv[1].get("region", ""), kv[1].get("order", 999))))
ROUTES = {os.path.splitext(os.path.basename(p))[0]: load(p)
          for p in sorted(glob.glob("content/routes/*.yml"))}
ROUTES_ALL = ROUTES
ROUTES = {k: v for k, v in ROUTES.items() if is_public(v)}
ROUTES = dict(sorted(ROUTES.items(), key=lambda kv: kv[1].get("order", 999)))

# რეალურად ხელმისაწვდომი ენები (თარგმანის მიხედვით)
LANGS = [l for l in ALL_LANGS if l in UI and l in META and l in PLANNER_LANGS
         and all(l in p for p in PAGES.values())]

SITE_URL = SITE["site_url"].rstrip("/")
BRAND = SITE["rental_brand"]
# ხილული ბრენდი და დომენი ერთ ხაზზე — ქვედა კოლონტიტულისთვის.
SITE_HOST = SITE_URL.split("//", 1)[-1].rstrip("/")


# ── USD reference rate ────────────────────────────────────────────────────
# The owner's rule: the rate comes from the National Bank of Georgia, not from
# a number typed into a config file that goes stale. Fetched once per build,
# cached to disk so an offline build still uses the last real rate rather than
# silently reverting to a hard-coded one.
NBG_URL = "https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json/?currencies=USD"
NBG_CACHE = ".nbg-usd.json"


def _load_usd_rate():
    fallback = {"rate": float(SITE.get("usd_rate", 2.6)), "date": "", "source": "site.yml"}
    if os.environ.get("SKIP_NBG"):
        return fallback
    try:
        import urllib.request
        with urllib.request.urlopen(NBG_URL, timeout=15) as r:
            d = json.load(r)
        cur = d[0]["currencies"][0]
        got = {"rate": float(cur["rate"]) / int(cur.get("quantity", 1) or 1),
               "date": str(cur.get("validFromDate", ""))[:10], "source": "nbg.gov.ge"}
        if not (0.5 < got["rate"] < 20):          # sanity: never publish nonsense
            raise ValueError(f"implausible NBG rate {got['rate']}")
        try:
            json.dump(got, open(NBG_CACHE, "w", encoding="utf-8"))
        except OSError:
            pass
        return got
    except Exception as e:                        # offline, rate-limited, shape changed
        print(f"WARNING: National Bank rate unavailable ({e}); using cached/config value")
        try:
            return json.load(open(NBG_CACHE, encoding="utf-8"))
        except Exception:
            return fallback


USD = _load_usd_rate()
USD_RATE = Decimal(str(USD["rate"]))
USD_RATE_DATE = USD.get("date", "")


def gel_to_usd(gel):
    """Convert GEL to USD and round to the nearest configured step."""
    rate = USD_RATE
    step = Decimal(str(SITE.get("usd_rounding", 10)))
    if rate <= 0 or step <= 0:
        raise ValueError("site.yml: usd_rate and usd_rounding must be positive")
    units = (Decimal(str(gel)) / rate / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(units * step)


def rental_daily_rate(car, days):
    """Return the admin-managed GEL daily rate for the rental length."""
    days = max(1, int(days))
    key = "price_30" if days >= 30 else ("price_7_29" if days >= 7 else "price_1_6")
    return Decimal(str(car[key]))


def rental_total(car, days):
    return rental_daily_rate(car, days) * max(1, int(days))


def money(gel):
    """Public dual-currency label; GEL remains the source of truth."""
    return f"{gel} ₾ · ≈ ${gel_to_usd(gel)}"

from theme import css as build_css  # noqa: E402


# ══════════════════════════════════════════════════════════════ URL helpers
def lang_root(lang):
    return "/" if lang == ROOT_LANG else f"/{lang}/"


def page_url(lang, page, absolute=True):
    # Pricing is part of the fleet experience; keep the old URL only as a redirect.
    target = "fleet" if page == "pricing" else page
    p = lang_root(lang) + PAGE_SLUG[target]
    return (SITE_URL + p) if absolute else p


def car_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}fleet/{slug}/"
    return (SITE_URL + p) if absolute else p


def post_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}blog/{slug}/"
    return (SITE_URL + p) if absolute else p


def region_url(lang, key, absolute=True):
    p = f"{lang_root(lang)}regions/{key}/"
    return (SITE_URL + p) if absolute else p


def attr_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}attractions/{slug}/"
    return (SITE_URL + p) if absolute else p


def route_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}routes/{slug}/"
    return (SITE_URL + p) if absolute else p


def localize_href(href, lang):
    if href.rstrip("/") == "/pricing":
        return page_url(lang, "fleet", False)
    if lang != ROOT_LANG and href.startswith("/") and not href.startswith(f"/{lang}/"):
        return f"/{lang}{href}"
    return href


def rel_prefix(depth):
    return "../" * depth if depth else ""


# ══════════════════════════════════════════════════════════════ inline text
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")


def inline(s, lang="ka"):
    s = E(s)
    s = _LINK.sub(lambda m: f'<a href="{localize_href(m.group(2), lang)}">{m.group(1)}</a>', s)
    return _BOLD.sub(r"<strong>\1</strong>", s)


_LTRISH = re.compile(r"^[+()\d][\d\s\-()+./]*$|@|^https?://|^www\.")


def bidi(v):
    """ტელეფონი, ელფოსტა და მისთანანი RTL გვერდზე მარცხნიდან-მარჯვნივ დარჩეს."""
    t = str(v).strip()
    return f'<bdi dir="ltr">{E(t)}</bdi>' if _LTRISH.search(t) else inline(t)


def slugify_anchor(s):
    s = re.sub(r"[^\wႠ-ჿЀ-ӿ]+", "-", s.lower()).strip("-")
    return s[:60] or "s"


def spec_label(key, lang):
    return SPECS["labels"].get(key, {}).get(lang, key)


def spec_value(v, lang):
    return SPECS["values"].get(str(v), {}).get(lang, v)


def engine_label(engine, lang):
    """'2.5 hybrid' → '2.5 ჰიბრიდი'"""
    parts = str(engine).split()
    if parts and parts[-1] in SPECS["values"]:
        parts[-1] = SPECS["values"][parts[-1]][lang]
    return " ".join(parts)


def cat_label(key, lang):
    for c in CATS:
        if c["key"] == key:
            return c[lang]
    return key


# ══════════════════════════════════════════════════════════════ block render
def render_block(b, lang):
    t = b["type"]
    if t == "h2":
        return f'<h2 id="{slugify_anchor(b["text"])}">{E(b["text"])}</h2>'
    if t == "h3":
        return f"<h3>{E(b['text'])}</h3>"
    if t == "p":
        return f"<p>{inline(b['text'], lang)}</p>"
    if t == "note":
        return f'<div class="note">{inline(b["text"], lang)}</div>'
    if t in ("ul", "ol"):
        items = "".join(f"<li>{inline(x, lang)}</li>" for x in b["items"])
        return f"<{t}>{items}</{t}>"
    if t == "table":
        head = "".join(f'<th scope="col">{inline(h, lang)}</th>' for h in b["head"])
        rows = ""
        for r in b["rows"]:
            cells = r["cells"] if isinstance(r, dict) else r
            tds = "".join(
                (f'<th scope="row">{inline(c, lang)}</th>' if i == 0 and b.get("rowhead")
                 else f"<td>{inline(c, lang)}</td>")
                for i, c in enumerate(cells))
            rows += f"<tr>{tds}</tr>"
        cap = f"<caption>{inline(b['caption'], lang)}</caption>" if b.get("caption") else ""
        return (f'<div class="tbl-wrap"><table>{cap}<thead><tr>{head}</tr></thead>'
                f"<tbody>{rows}</tbody></table></div>")
    if t == "facts":
        cells = "".join(
            f'<div><dt class="k">{inline(x["k"], lang)}</dt>'
            f'<dd class="v">{bidi(x["v"])}</dd></div>' for x in b["items"])
        return f'<dl class="facts">{cells}</dl>'
    if t == "cards":
        out = []
        for c in b["items"]:
            tag = f'<span class="tag">{E(c["tag"])}</span>' if c.get("tag") else ""
            txt = f"<p>{inline(c['text'], lang)}</p>" if c.get("text") else ""
            lst = ("<ul>" + "".join(f"<li>{inline(x, lang)}</li>" for x in c["list"]) + "</ul>"
                   if c.get("list") else "")
            pr = f'<span class="price">{inline(c["price"], lang)}</span>' if c.get("price") else ""
            out.append(f'<div class="card">{tag}<h3>{E(c["title"])}</h3>{txt}{lst}{pr}</div>')
        return f'<div class="cards">{"".join(out)}</div>'
    if t == "faq":
        qas = "".join(f'<div class="qa"><h3>{E(x["q"])}</h3><p>{inline(x["a"], lang)}</p></div>'
                      for x in b["items"])
        return f'<div class="faq">{qas}</div>'
    if t == "cta":
        row = "".join(
            f'<a class="btn{"" if i == 0 else " ghost"}" '
            f'href="{E(localize_href(a["href"], lang))}">{E(a["label"])}</a>'
            for i, a in enumerate(b.get("actions", [])))
        return (f'<div class="cta"><h2>{E(b["title"])}</h2><p>{inline(b["text"], lang)}</p>'
                f'<div class="row">{row}</div></div>')
    if t == "cars":
        return cars_grid(b.get("category"), lang, live=True)
    raise ValueError(f"უცნობი ბლოკის ტიპი: {t}")


DETAILS_LABEL = {"ka": "დეტალები", "en": "Details", "ru": "Подробнее",
                 "fa": "جزئیات", "he": "פרטים", "ar": "التفاصيل"}


# ─────────────────────────────── ფასის დანამატის გამჭვირვალე ტექსტი (6 ენა)
_MONTH_NAMES = {
    "ka": ["იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი", "ივლისი",
           "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "ru": ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
           "август", "сентябрь", "октябрь", "ноябрь", "декабрь"],
    "fa": ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه",
           "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
    "he": ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי",
           "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"],
    "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو",
           "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
}

SURCHARGE_LABEL = {
    "ka": "სეზონური და ასაკობრივი დანამატი",
    "en": "Seasonal & young-driver surcharge",
    "ru": "Сезонная и возрастная доплата",
    "fa": "افزایش فصلی و رانندهٔ جوان",
    "he": "תוספת עונתית ותוספת נהג צעיר",
    "ar": "الرسوم الموسمية ورسوم السائق الشاب",
}

SURCHARGE_SHORT = {
    "ka": "{months}: +{p}% · {age} წლამდე: +{min}–{max} ₾/დღე",
    "en": "{months}: +{p}% · under {age}: +{min}–{max} GEL/day",
    "ru": "{months}: +{p}% · до {age} лет: +{min}–{max} ₾/сут",
    "fa": "{months}: +{p}٪ · زیر {age} سال: +{min}–{max} لاری/روز",
    "he": "{months}: {p}%+ · מתחת לגיל {age}: +{min}–{max} ₾/יום",
    "ar": "{months}: +{p}٪ · دون {age}: +{min}–{max} لاري/يوم",
}

SURCHARGE_NOTE = {
    "ka": "სეზონური კოეფიციენტი ({months}) — დღიურ ტარიფზე +{p}%. ახალგაზრდა მძღოლის "
          "დანამატი ({age} წლამდე) — {min}–{max} ₾ დღეში. ორივე ჯავშნის დადასტურებამდე ჩანს.",
    "en": "Seasonal rate ({months}): +{p}% on the daily price. Young-driver surcharge "
          "(under {age}): {min}–{max} GEL per day. Both are shown before you confirm.",
    "ru": "Сезонный коэффициент ({months}): +{p}% к дневному тарифу. Надбавка молодого "
          "водителя (до {age} лет): {min}–{max} ₾ в сутки. И то и другое видно до подтверждения.",
    "fa": "ضریب فصلی ({months}): +{p}٪ روی نرخ روزانه. هزینهٔ رانندهٔ جوان (زیر {age} سال): "
          "{min}–{max} لاری در روز. هر دو پیش از تأیید رزرو نمایش داده می‌شود.",
    "he": "תוספת עונתית ({months}): {p}%+ על המחיר היומי. תוספת נהג צעיר (מתחת לגיל {age}): "
          "{min}–{max} ₾ ליום. שתיהן מוצגות לפני אישור ההזמנה.",
    "ar": "معامل موسمي ({months}): +{p}٪ على السعر اليومي. رسوم السائق الشاب (دون {age} عامًا): "
          "{min}–{max} لاري يوميًا. يُعرض كلاهما قبل تأكيد الحجز.",
}


def peak_months_label(lang):
    """სეზონური თვეების სახელები მიმდინარე ენაზე (booking.yml-იდან)."""
    names = _MONTH_NAMES.get(lang, _MONTH_NAMES["en"])
    ms = [m for m in SEASON_CFG["peakMonths"] if 1 <= int(m) <= 12]
    if not ms:
        return ""
    labels = [names[int(m) - 1] for m in ms]
    if len(ms) > 1 and list(ms) == list(range(int(ms[0]), int(ms[-1]) + 1)):
        return f"{labels[0]}–{labels[-1]}"
    return " · ".join(labels)


def surcharge_fmt(tpl, lang):
    return tpl.format(months=peak_months_label(lang), p=SEASON_CFG["peakPercent"],
                      age=YOUNG_DRIVER_CFG["underAge"], min=YOUNG_DRIVER_CFG["minGel"],
                      max=YOUNG_DRIVER_CFG["maxGel"])


def surcharge_note_html(lang, cls="pricenote"):
    """ღია ტექსტი ფასის დანამატებზე — ფასის გვერდით, არა ქვედა კოლონტიტულში."""
    return (f'<p class="{cls}" data-surcharge-note>'
            f'<strong>{E(SURCHARGE_LABEL[lang])}:</strong> '
            f'{E(surcharge_fmt(SURCHARGE_NOTE[lang], lang))}</p>')


# ─────────────────────────────── ჯავშნის CTA რეგიონის/ღირსშესანიშნაობის გვერდზე
TRIP_CTA_TEXT = {
    "ka": "ამ ადგილებამდე ყველაზე მოხერხებულად საკუთარი ავტომობილით მიხვალთ — "
          "მარშრუტსა და გაჩერებებს თავად ირჩევთ.",
    "en": "The easiest way to reach these places is by car — you pick the route and the stops.",
    "ru": "До этих мест удобнее всего добираться на машине — маршрут и остановки выбираете вы.",
    "fa": "راحت‌ترین راه رسیدن به این نقاط، خودرو است — مسیر و توقف‌ها را خودتان انتخاب می‌کنید.",
    "he": "הדרך הנוחה ביותר להגיע למקומות האלה היא ברכב — אתם בוחרים את המסלול והעצירות.",
    "ar": "أسهل طريقة للوصول إلى هذه الأماكن هي بالسيارة — أنت تختار المسار والمحطات.",
}


def booking_open_btn(lang, cls="btn booking-hero-cta"):
    """დიალოგის გამხსნელი ღილაკი კონკრეტული ავტომობილის გარეშე."""
    return (f'<button class="{cls}" type="button" data-booking-open>'
            f'{E(BOOKING_TEXT[lang]["book"])}</button>')


def cars_grid(category, lang, limit=None, live=False):
    # RentUp Pages მაკეტის ბარათი: სახელი + ფირუზი ფასი ერთ ხაზზე, მეტა,
    # ვადიანი ფასები, ფირუზი „დაჯავშნა" + ghost „დეტალები".
    items = [(s, c) for s, c in CARS.items() if not category or c["category"] == category]
    if limit:
        items = items[:limit]
    out = []
    for slug, c in items:
        L = c[lang]
        img = c.get("image")
        ph = (f'<div class="ph"><img src="{E(img)}" alt="{E(L["name"])} — '
              f'{E(cat_label(c["category"], lang))}" loading="lazy" width="640" height="400"></div>'
              if img else f'<div class="ph">{E(L["name"])} — ფოტო</div>' if lang == "ka"
              else f'<div class="ph">{E(L["name"])}</div>')
        feats = " · ".join(re.sub(r"<[^>]+>", "", inline(x, lang)) for x in L.get(
            "features", [])[:3])
        unit = SPECS["units"]["day"][lang]
        p7 = c.get("price_7_29")
        p30 = c.get("price_30")
        tiers = ""
        if p7 and p30:
            tiers = (f'<p class="tiers">7–29: {E(money(p7))} · 30+: {E(money(p30))}</p>')
        brand, _, model = L["name"].partition(" ")
        out.append(
            f'<article class="car" data-analytics-car data-car="{E(slug)}" '
            f'data-car-name="{E(L["name"])}" data-brand="{E(brand)}" '
            f'data-model="{E(model)}" data-price="{E(c["price_1_6"])}">{ph}<div class="in">'
            f'<div class="trow"><h3><a href="{car_url(lang, slug, False)}">{E(L["name"])}</a></h3>'
            f'<span class="p">{E(money(c["price_1_6"]))} <small>/ {E(unit)}</small></span></div>'
            f'<p class="sub">{E(L.get("summary", ""))}</p>'
            + (f'<p class="meta">{feats}</p>' if feats else "")
            + tiers +
            f'<div class="btns"><button class="btn sm" type="button" data-booking-open '
            f'data-car="{E(slug)}" data-car-name="{E(L["name"])}">{E(BOOKING_TEXT[lang]["book"])}</button>'
            f'<a class="btn sm ghost" href="{car_url(lang, slug, False)}">{E(DETAILS_LABEL[lang])}</a>'
            f'</div></div></article>')
    # `data-live-catalogue` is what `catalogue.js` looks for. Its value is the
    # category this grid holds, so a car published from the phone lands in the
    # right section of the page rather than all of them in a heap at the end.
    # Absent on the home page teaser and anywhere else a grid is decorative:
    # a three-car preview that silently grew to nineteen is not a preview.
    tag = f' data-live-catalogue="{E(category or "")}"' if live else ""
    return f'<div class="cars"{tag}>{"".join(out)}</div>'


# ══════════════════════════════════════════════════════════════ markdown
_MD = md.Markdown(extensions=["tables", "attr_list", "sane_lists"])


def render_md(text, lang):
    _MD.reset()
    out = _MD.convert(text or "")
    out = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{localize_href(m.group(1), lang)}"', out)
    out = out.replace(f'href="{page_url(lang, "pricing", False)}"',
                      f'href="{page_url(lang, "fleet", False)}"')
    out = out.replace("<table>", '<div class="tbl-wrap"><table>').replace("</table>", "</table></div>")
    return out


# ══════════════════════════════════════════════════════════════ JSON-LD
def org_node(lang):
    a = SITE["address"][lang]
    node = {
        "@type": ["AutoRental", "LocalBusiness"],
        "@id": SITE_URL + "/#organization",
        "name": BRAND,
        "alternateName": SITE["rental_brand_ka"],
        "url": SITE_URL + lang_root(lang),
        "description": META[lang]["org_desc"],
        "telephone": SITE["phone_e164"],
        "foundingDate": SITE["founded"],
        "priceRange": f'{_fleet_price_low()}-{_fleet_price_high()} GEL',
        # Google requires the organisation logo to be at least 112px on its
        # smallest side; the 180x72 header mark does not qualify on its own.
        "logo": {"@type": "ImageObject", "url": SITE_URL + "/assets/rentup-logo-square.png",
                 "width": 540, "height": 540},
        "image": SITE_URL + "/assets/rentup-logo-square.png",
        "currenciesAccepted": "GEL, USD, EUR",
        "paymentAccepted": META[lang]["payments"],
        "areaServed": {"@type": "Country", "name": META[lang]["country"]},
        "address": {"@type": "PostalAddress", "streetAddress": a["street"],
                    "addressLocality": a["city"], "postalCode": SITE["address_zip"],
                    "addressCountry": "GE"},
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["geo_lat"],
                "longitude": SITE["geo_lon"]},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": SITE["opens"], "closes": SITE["closes"]}],
    }
    # Optional contact details: the owner may genuinely have only a phone
    # number. Emit each key only when it holds a real value, so an empty admin
    # field never becomes an empty mailto: or a bare sameAs entry.
    if SITE.get("email"):
        node["email"] = SITE["email"]
    if SITE.get("social"):
        node["sameAs"] = SITE["social"]
    node["contactPoint"] = {
        "@type": "ContactPoint", "contactType": "reservations",
        "telephone": SITE["phone_e164"],
        "availableLanguage": [LANG_LABEL.get(l, l) for l in LANGS],
        "areaServed": "GE",
        **({"email": SITE["email"]} if SITE.get("email") else {})}
    return node


def _num(v, default=0):
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return default


def _fleet_tiers():
    """Prices are strings in the YAML, so compare them as numbers, not text —
    otherwise "104" sorts below "88" and the published band comes out inverted."""
    out = []
    for c in CARS.values():
        for k in ("price_1_6", "price_7_29", "price_30"):
            try:
                out.append(int(str(c[k]).strip()))
            except (KeyError, ValueError, TypeError):
                pass
    return out


def _fleet_price_low():
    return min(_fleet_tiers()) if CARS else 0


def _fleet_price_high():
    return max(_fleet_tiers()) if CARS else 0


def website_node(lang):
    return {"@type": "WebSite", "@id": SITE_URL + "/#website",
            "url": SITE_URL + lang_root(lang), "name": BRAND,
            "inLanguage": lang, "publisher": {"@id": SITE_URL + "/#organization"}}


def crumbs_node(lang, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
        for i, (n, u) in enumerate(trail)]}


def faq_items_node(items):
    """FAQPage from a plain [{q, a}] list — the shape the SEO cluster uses.
    Only ever called where the same Q&A is rendered visibly on the page."""
    items = [x for x in (items or []) if x.get("q") and x.get("a")]
    if not items:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": x["q"],
         "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in items]}


def faq_node(blocks):
    return faq_items_node([x for b in blocks if b["type"] == "faq" for x in b["items"]])


def software_node(lang):
    m = META[lang]
    return {"@type": "SoftwareApplication", "@id": SITE_URL + "/#software",
            "name": SITE["software_brand"], "applicationCategory": "BusinessApplication",
            "applicationSubCategory": m["software_subcat"],
            "operatingSystem": "Android 7.0+, iOS 13+", "description": m["software_desc"],
            "url": page_url(lang, "software"), "inLanguage": ["ka", "en"],
            "softwareVersion": "2.16", "author": {"@id": SITE_URL + "/#organization"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GEL",
                       "description": m["software_offer"]},
            "featureList": m["software_features"]}


def offer_catalog(lang):
    return {"@type": "OfferCatalog", "name": PAGES["pricing"][lang]["title"],
            "itemListElement": [{
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "serviceType": o["name"],
                                "provider": {"@id": SITE_URL + "/#organization"}},
                "priceSpecification": {"@type": "UnitPriceSpecification", "price": o["price"],
                                       "priceCurrency": "GEL", "unitCode": "DAY"},
                "availability": "https://schema.org/InStock"} for o in META[lang]["offers"]]}


def car_node(slug, c, lang):
    L = c[lang]
    node = {
        "@type": "Car", "@id": car_url(lang, slug) + "#vehicle", "name": L["name"],
        "description": L.get("summary", ""), "url": car_url(lang, slug),
        "vehicleTransmission": spec_value(c["transmission"], lang),
        "driveWheelConfiguration": str(c["drive"]).upper(),
        "vehicleSeatingCapacity": c["seats"],
        "fuelConsumption": {"@type": "QuantitativeValue", "value": c["fuel_100km"],
                            "unitCode": "LTR", "name": "l/100km"},
        "vehicleConfiguration": cat_label(c["category"], lang),
        # Three real tiers, from the car's own record. No `availability` — the
        # fleet YAML carries no stock field, so claiming InStock was invented.
        "offers": {"@type": "AggregateOffer", "priceCurrency": "GEL",
                   "lowPrice": min(_num(c["price_1_6"]), _num(c["price_7_29"]), _num(c["price_30"])),
                   "highPrice": max(_num(c["price_1_6"]), _num(c["price_7_29"]), _num(c["price_30"])),
                   "offerCount": 3,
                   "offers": [
                       {"@type": "Offer", "priceCurrency": "GEL", "price": price,
                        "name": name,
                        "priceSpecification": {
                            "@type": "UnitPriceSpecification", "price": price,
                            "priceCurrency": "GEL", "unitCode": "DAY",
                            "referenceQuantity": {
                                "@type": "QuantitativeValue", "value": 1, "unitCode": "DAY"}},
                        "seller": {"@id": SITE_URL + "/#organization"}}
                       for price, name in ((c["price_1_6"], "1-6 days"),
                                           (c["price_7_29"], "7-29 days"),
                                           (c["price_30"], "30+ days"))],
                   "seller": {"@id": SITE_URL + "/#organization"}},
    }
    if c.get("image"):
        node["image"] = abs_url(c["image"])
    return node


def post_node(slug, p, lang):
    L = p[lang]
    node = {"@type": "BlogPosting", "@id": post_url(lang, slug) + "#post",
            "headline": L["title"], "description": L["desc"],
            "url": post_url(lang, slug), "inLanguage": lang,
            "datePublished": str(p["date"]), "dateModified": str(p["date"]),
            "author": {"@id": SITE_URL + "/#organization"},
            "publisher": {"@id": SITE_URL + "/#organization"},
            "mainEntityOfPage": post_url(lang, slug)}
    if p.get("image"):
        node["image"] = abs_url(p["image"])
    return node


# ══════════════════════════════════════════════════════════════ chrome
LEAFLET_CSS = "/assets/leaflet/leaflet.css"
LEAFLET_JS = "/assets/leaflet/leaflet.js"


ASSET = {"css": "/assets/style.css", "explorer": "/assets/explorer.js",
         "planner": "/assets/planner.js", "workspace": "/assets/workspace.js",
         "app_mobile": "/assets/app-mobile.js", "trip": "/assets/trip.js"}
TRAVEL_ASSET = {}


def analytics_html():
    """Build-time GA4 config. Empty IDs intentionally produce a client-side no-op.

    `static/analytics.js` is optional. Emitting the tag unconditionally shipped a
    404 on every page, so the loader is only linked once the file is actually
    written into dist/ by write_hashed()."""
    src = ASSET.get("analytics")
    if not src:
        return ""
    measurement_id = os.environ.get("GA_MEASUREMENT_ID", "").strip()
    return (f'<script>window.FH_ANALYTICS_CONFIG={{"measurementId":{J(measurement_id)}}};</script>\n'
            f'<script defer src="{src}"></script>')


def _hash(data):
    import hashlib
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()[:10]


def write_hashed(out, rel, data, key, also_plain=False):
    """ჩაწერს ფაილს შიგთავსის ჰეშით სახელში — ბრაუზერი ძველს ვეღარ აჩვენებს.

    `also_plain` წერს ჰეშის გარეშე ასლსაც. ეს მხოლოდ style.css-ს სჭირდება,
    რომელსაც Decap CMS-ის preview ფიქსირებული მისამართით ითხოვს. დანარჩენ
    ფაილებზე ასლი მკვდარი წონაა — HTML ყოველთვის ჰეშიან ვერსიას ბმულობს.
    """
    base, ext = os.path.splitext(rel)
    name = base + "." + _hash(data) + ext
    write(os.path.join(out, "assets", name), data)
    if also_plain:
        write(os.path.join(out, "assets", rel), data)
    ASSET[key] = "/assets/" + name
    return ASSET[key]


def _noindex(current):
    return current in ("account", "trip", "card", "planner", "pricing")


def _add_webpage_node(ld, lang, url, title, desc, image=None):
    """Every page should say what it *is*, and tie its entity, breadcrumb and
    language together. Without a WebPage node a crawler sees a bare Car or
    TouristAttraction with nothing declaring which page it belongs to."""
    graph = (ld or {}).get("@graph")
    if not isinstance(graph, list) or not url:
        return ld
    if any(isinstance(n, dict) and n.get("@type") in
           ("WebPage", "CollectionPage", "ItemPage", "AboutPage", "ContactPage", "FAQPage")
           for n in graph):
        return ld
    crumbs = next((n for n in graph if isinstance(n, dict)
                   and n.get("@type") == "BreadcrumbList"), None)
    main = next((n for n in graph if isinstance(n, dict) and n.get("@type") not in
                 ("Organization", "AutoRental", "LocalBusiness", "WebSite",
                  "BreadcrumbList", "SoftwareApplication", "ImageObject", "FAQPage")
                 and n.get("@id")), None)
    node = {"@type": "WebPage", "@id": url + "#webpage", "url": url,
            "name": title, "description": desc, "inLanguage": lang,
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "publisher": {"@id": SITE_URL + "/#organization"}}
    if main:
        node["mainEntity"] = {"@id": main["@id"]}
    if crumbs and crumbs.get("@id"):
        node["breadcrumb"] = {"@id": crumbs["@id"]}
    if image:
        node["primaryImageOfPage"] = image
    graph.insert(2 if len(graph) > 2 else len(graph), node)
    return ld


def head_html(lang, current, title, desc, keywords, url, alternates, depth, ld,
              og_type="website", image=None, leaflet=False):
    css_href = ASSET["css"]
    # A noindex page is not part of any language cluster — advertising hreflang
    # on it invites a crawler to treat six excluded URLs as alternates.
    if _noindex(current):
        alts = ""
    else:
        alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{u}">'
                         for l, u in alternates.items())
        alts += f'\n<link rel="alternate" hreflang="x-default" href="{alternates["en"]}">'
    ld = _add_webpage_node(ld, lang, url, title, desc, image)
    og_img = image or f"{SITE_URL}/assets/og-{lang}.png"
    gf = DESIGN.get("google_fonts", "")
    if lang in LANG_FONT:
        gf = LANG_FONT[lang] + ("&family=" + gf if gf else "")
    fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={gf}&display=swap">'
             ) if gf else ""
    lf = (f'\n<link rel="stylesheet" href="{LEAFLET_CSS}">' if leaflet else "")
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0f4c81">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="RentUp">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
{alts}
<meta name="robots" content="{"noindex, nofollow" if current in ("account", "trip", "card") else "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"}">
<meta name="author" content="{E(BRAND)}">
<meta name="geo.region" content="GE">
<meta name="geo.placename" content="{E(SITE['address'][lang]['city'])}">
<meta name="geo.position" content="{SITE['geo_lat']};{SITE['geo_lon']}">
<meta name="ICBM" content="{SITE['geo_lat']}, {SITE['geo_lon']}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{E(BRAND)}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
{"".join(f'<meta property="og:locale:alternate" content="{OG_LOCALE[l]}">' for l in LANGS if l != lang)}
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
{fonts}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/app-icon-180.png">
<link rel="manifest" href="/assets/manifest.webmanifest">
<link rel="stylesheet" href="{css_href}">{lf}
<script type="application/ld+json">
{JC(ld)}
</script>"""


def header_html(lang, current):
    u = UI[lang]
    app_copy = {
        "ka": ("აპლიკაცია", "Android APK", "iPhone / iOS", "ჩამოტვირთეთ Android-ზე", "ინსტალაციის ინსტრუქცია"),
        "en": ("App", "Android APK", "iPhone / iOS", "Download for Android", "Installation instructions"),
        "ru": ("Приложение", "Android APK", "iPhone / iOS", "Скачать для Android", "Инструкция по установке"),
        "fa": ("اپلیکیشن", "Android APK", "iPhone / iOS", "دانلود برای اندروید", "راهنمای نصب"),
        "he": ("אפליקציה", "Android APK", "iPhone / iOS", "הורדה לאנדרואיד", "הוראות התקנה"),
        "ar": ("التطبيق", "Android APK", "iPhone / iOS", "تنزيل لأندرويد", "تعليمات التثبيت"),
    }[lang]
    app_soon = {"ka": "მალე", "en": "Coming soon", "ru": "Скоро", "fa": "به‌زودی",
                "he": "בקרוב", "ar": "قريباً"}[lang]
    CUR = ' aria-current="page"'
    # RentUp Pages მაკეტი: ტაბები — მთავარი გვერდები; დანარჩენი "..." მენიუში.
    more_pages = {"terms", "faq", "blog", "software"}
    lis = "".join(
        f'<li><a href="{page_url(lang, "map", False) + "#planner" if p == "planner" else page_url(lang, p, False)}"'
        f'{CUR if p == current else ""}>{E(u["nav"][p])}</a></li>'
        for p in PAGE_ORDER if p not in NAV_HIDDEN and p not in more_pages)
    more = "".join(
        f'<li><a href="{page_url(lang, p, False)}"'
        f'{CUR if p == current else ""}>{E(u["nav"][p])}</a></li>'
        for p in PAGE_ORDER if p in more_pages)
    lang_opts = "".join(
        f'<option value="{page_url(l, "card", False) if current == "card" else lang_root(l)}"'
        f'{" selected" if l == lang else ""}>{E(LANG_LABEL[l])}</option>'
        for l in LANGS)
    lang_links = "".join(
        f'<a href="{page_url(l, "card", False) if current == "card" else lang_root(l)}" hreflang="{l}" lang="{l}">'
        f'{LANG_SHORT[l]}</a> ' for l in LANGS)
    plan_label = {"ka": "დაგეგმე მოგზაურობა", "en": "Plan a trip", "ru": "Спланируйте поездку",
                  "fa": "سفر را برنامه‌ریزی کنید", "he": "תכננו נסיעה", "ar": "خطّط رحلتك"}[lang]
    logo_img = DESIGN.get("logo_image")
    mark = DESIGN.get("logo_mark") or "".join(w[0] for w in BRAND.split()[:2]).upper()
    logo = (f'<img src="{E(logo_img)}" alt="" aria-hidden="true">'
            f'<span class="logo-name">{E(BRAND)} <small>{E(u["ui"]["logo_sub"])}</small></span>' if logo_img
            else f'<span class="mark" aria-hidden="true">{E(mark)}</span>'
                 f'<span class="logo-name">{E(BRAND)} <small>{E(u["ui"]["logo_sub"])}</small></span>')
    return f"""<header class="site-head"><div class="head-top">
<a class="logo" href="{lang_root(lang)}">{logo}</a>
<span class="head-sp"></span>
<details class="head-app">
<summary>
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="2.5"></rect><path d="M10.5 18.5h3"></path></svg>
<span>{E(app_copy[0])}</span>
<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M6 9l6 6 6-6"></path></svg>
</summary>
<div class="head-app-menu">
<a class="app-download" href="/assets/downloads/rentup-android.apk" download>
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5"></path><path d="M4 19h16"></path></svg>
<span><b>{E(app_copy[1])}</b><small>{E(app_copy[3])}</small></span></a>
<button type="button" class="head-app-soon" data-ios-install>
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="2.5"></rect><path d="M10.5 18.5h3"></path></svg>
<span><b>{E(app_copy[2])}</b><small>{E(app_soon)}</small></span></button>
</div>
</details>
<label class="lang-nav"><span class="sr-only">{E(u['ui']['lang_label'])}</span>
<select onchange="location.href=this.value">{lang_opts}</select></label>
<noscript><span class="lang-links">{lang_links}</span></noscript>
<div id="authbox" class="authbox"></div>
</div>
<nav class="head-tabs" aria-label="{E(u['ui']['nav_label'])}"><ul>{lis}
<li class="nav-more"><details><summary aria-label="More">•••</summary><ul>{more}</ul></details></li>
</ul><span class="head-sp"></span>
<a class="plan-cta" href="{page_url(lang, 'map', False)}#planner">{E(plan_label)}</a></nav>
</header>"""


def crumbs_html(lang, trail_rel):
    if not trail_rel:
        return ""
    u = UI[lang]
    items = "".join(
        (f'<li><a href="{href}">{E(name)}</a></li>' if href
         else f'<li><span aria-current="page">{E(name)}</span></li>')
        for name, href in trail_rel)
    return (f'<nav class="crumbs" aria-label="{E(u["ui"]["crumbs"])}">'
            f"<div class=\"wrap\"><ol>{items}</ol></div></nav>")


def footer_html(lang):
    u = UI[lang]
    a = SITE["address"][lang]
    card_label = {"ka": "ვიზიტკა", "en": "Business card", "ru": "Визитка",
                  "fa": "کارت ویزیت", "he": "כרטיס ביקור", "ar": "بطاقة العمل"}[lang]
    app_label = {"ka": "აპლიკაცია (Android APK)", "en": "App (Android APK)", "ru": "Приложение (Android APK)",
                 "fa": "اپلیکیشن (Android APK)", "he": "אפליקציה (Android APK)", "ar": "التطبيق (Android APK)"}[lang]
    return f"""<footer class="site-foot"><div class="wrap"><div class="foot-compact">
<nav aria-label="{E(u['ui']['foot_pages'])}">
<a href="{page_url(lang, 'fleet', False)}">{E(u['nav']['fleet'])}</a>
<a href="{page_url(lang, 'contact', False)}">{E(u['nav']['contact'])}</a>
<a href="{page_url(lang, 'card', False)}">{E(card_label)}</a>
<a href="/assets/downloads/rentup-android.apk" download>{E(app_label)}</a></nav>
<div class="foot-contact">
<a dir="ltr" href="tel:{SITE['phone_e164']}">{E(SITE['phone'])}</a>
{f'''<a dir="ltr" href="tel:{SITE['mobile_e164']}">{E(SITE['mobile'])}</a>''' if SITE.get('mobile') else ''}
{f'''<a dir="ltr" href="mailto:{SITE['email']}">{E(SITE['email'])}</a>''' if SITE.get('email') else ''}
<span>{E(a['street'])}, {E(a['city'])}</span></div>
</div><div class="foot-bottom">
<span class="foot-brandline" dir="ltr">{E(BRAND)} · {E(SITE_HOST)}</span>
<span>© {date.today().year} {E(BRAND)}. {E(u['ui']['rights'])}</span>
</div></div></footer>"""


def catalogue_cfg(lang):
    """The words `catalogue.js` needs to draw a card in this language.

    Every value comes from `content/settings/specs.yml`, the same table the
    static car pages print from — so a Tucson with a page and an Audi without
    one say „ავტომატი" the same way, in all six languages. The phone publishes
    codes (`automatic`, `awd`, `petrol`); this is where a code becomes a word.

    A code the site has never heard of simply produces no text: the card omits
    that line rather than printing the raw code at a customer.
    """
    lab = SPECS["labels"]
    val = SPECS["values"]
    unit = SPECS["units"]

    def pick(table, key):
        entry = table.get(key) or {}
        return entry.get(lang) or entry.get("en") or ""

    return {
        # The card prints „130 ₾ · ≈ $50", the same shape `money()` builds for
        # every static price on the site. The rate and the rounding step travel
        # rather than a finished string, because the number is only known in
        # the browser — and a live card that formatted money differently from
        # the card beside it would read as two different websites.
        "usdRate": float(USD_RATE),
        "usdStep": int(SITE.get("usd_rounding", 10)),
        "book": BOOKING_TEXT[lang]["book"],
        "l": {k: pick(lab, k) for k in
              ("seats", "luggage", "clearance", "range", "transmission", "drive")},
        "v": {k: pick(val, k) for k in val},
        "u": {k: pick(unit, k) for k in unit},
    }


def shell(lang, current, head, body, depth, tail=""):
    u = UI[lang]
    fs = LANG_FONT_STACK.get(lang, "")
    style = (f'<style>:root{{--font:{fs}{DESIGN["font_family"]}}}</style>\n' if fs else "")
    fb = ""
    if True:
        cfg = {k: AUTH.get(k, "") for k in ("apiKey", "authDomain", "projectId",
                                            "storageBucket", "messagingSenderId", "appId")}
        cfg["accountUrl"] = page_url(lang, "account", False)
        cfg["plannerUrl"] = page_url(lang, "map", False) + "#planner"
        cfg["tripUrl"] = lang_root(lang) + "trip/"
        cfg["booking"] = BOOKING
        cfg["cars"] = CAR_PRICES
        # ფასის დანამატები — booking.js აჩვენებს ფასის გამოთვლისას (booking.yml-იდან).
        cfg["season"] = SEASON_CFG
        cfg["youngDriver"] = YOUNG_DRIVER_CFG
        cfg["whatsapp"] = str(SITE.get("whatsapp") or SITE.get("mobile_e164")
                              or SITE.get("phone_e164", "")).replace("+", "").replace(" ", "")
        cfg["siteUrl"] = SITE_URL
        cfg["t"] = {k: u["ui"][k] for k in (
            "account", "sign_in", "sign_up", "sign_out", "with_google", "or_email", "email",
            "password", "forgot", "reset_sent", "why_account", "legal_note", "please_sign_in",
            "no_trips", "to_planner", "planned", "done", "mark_done", "mark_planned", "open",
            "delete", "confirm_del", "days", "stops", "save_trip", "saved") if k in u["ui"]}
        # Perf: only ship the bundles a page can actually use. auth.js and app.js
        # are global (header account state + shared UI); booking.js is needed
        # wherever a booking CTA exists; community.js only on the community page.
        _needs_booking = current in ("index", "fleet", "map", "planner", "account")
        _needs_community = current == "community"
        # The live catalogue only has somewhere to draw on the fleet page,
        # which is the one page with a grid per category and a catch-all
        # section. Shipping it elsewhere would be a fetch that renders nothing.
        _needs_catalogue = current == "fleet"
        fb = (f'\n<script>window.FH_CFG={J(cfg)};</script>'
              + (f'\n<script>window.FH_CAT={J(catalogue_cfg(lang))};</script>'
                 if _needs_catalogue else "")
              + f'\n<script type="module" src="{ASSET.get("auth", "/assets/auth.js")}"></script>'
              + (f'\n<script type="module" src="{ASSET.get("booking", "/assets/booking.js")}"></script>'
                 if _needs_booking else "")
              + (f'\n<script defer src="{ASSET.get("catalogue", "/assets/catalogue.js")}"></script>'
                 if _needs_catalogue else "")
              + (f'\n<script type="module" src="{ASSET.get("community", "/assets/community.js")}"></script>'
                 if _needs_community else "")
              + f'\n<script defer src="{ASSET.get("app", "/assets/app.js")}"></script>')
    inquiry = inquiry_widget(lang, current) if current in ("index", "fleet", "map", "planner") else ""
    return (f'<!DOCTYPE html>\n<html lang="{lang}" dir="{LANG_DIR[lang]}">\n<head>\n{head}\n{analytics_html()}\n'
            f'{style}</head>\n<body class="page-{E(current)}">\n'
            f'<a class="skip" href="#main">{E(u["ui"]["skip"])}</a>\n'
            f'{header_html(lang, current)}\n{body}\n{inquiry}{footer_html(lang)}\n{tail}{fb}\n</body>\n</html>\n')


def inquiry_widget(lang, context=""):
    tx = {
        "ka": ("დაჯავშნეთ ავტომობილი", "არჩეული ავტომობილი", "დაწყება", "დაბრუნება", "სახელი", "ტელეფონი / WhatsApp", "შენიშვნა (არასავალდებულო)", "WhatsApp", "მოთხოვნის გაგზავნა", "ხელმისაწვდომობას სწრაფად გადავამოწმებთ და დაგიკავშირდებით.", "დახურვა", "ელფოსტა (არასავალდებულო)", "აღების ადგილი (არასავალდებულო)", "დაბრუნების ადგილი (არასავალდებულო)", "მძღოლით მჭირდება"),
        "en": ("Book a car", "Selected car", "Start date", "Return date", "Name", "Phone / WhatsApp", "Notes (optional)", "WhatsApp", "Send request", "We’ll quickly confirm availability and contact you.", "Close", "Email (optional)", "Pickup location (optional)", "Return location (optional)", "I need a driver"),
        "ru": ("Забронировать автомобиль", "Выбранный автомобиль", "Дата начала", "Дата возврата", "Имя", "Телефон / WhatsApp", "Комментарий (необязательно)", "WhatsApp", "Отправить запрос", "Мы быстро проверим наличие и свяжемся с вами.", "Закрыть", "Эл. почта (необязательно)", "Место получения (необязательно)", "Место возврата (необязательно)", "Нужен водитель"),
        "fa": ("رزرو خودرو", "خودروی انتخابی", "تاریخ شروع", "تاریخ بازگشت", "نام", "تلفن / واتس‌اپ", "یادداشت (اختیاری)", "واتس‌اپ", "ارسال درخواست", "موجودی را سریع بررسی کرده و با شما تماس می‌گیریم.", "بستن", "ایمیل (اختیاری)", "محل تحویل (اختیاری)", "محل بازگرداندن (اختیاری)", "راننده لازم دارم"),
        "he": ("הזמנת רכב", "הרכב שנבחר", "תאריך התחלה", "תאריך החזרה", "שם", "טלפון / WhatsApp", "הערות (לא חובה)", "WhatsApp", "שליחת בקשה", "נבדוק זמינות במהירות וניצור קשר.", "סגירה", "אימייל (לא חובה)", "מקום איסוף (לא חובה)", "מקום החזרה (לא חובה)", "אני צריך נהג"),
        "ar": ("حجز سيارة", "السيارة المختارة", "تاريخ البدء", "تاريخ الإرجاع", "الاسم", "الهاتف / واتساب", "ملاحظات (اختياري)", "واتساب", "إرسال الطلب", "سنتحقق من التوفر سريعًا ونتواصل معك.", "إغلاق", "البريد الإلكتروني (اختياري)", "مكان الاستلام (اختياري)", "مكان الإرجاع (اختياري)", "أحتاج سائقًا")
    }[lang]
    return f'''<div class="booking-dialog" data-booking-dialog hidden role="dialog" aria-modal="true" aria-labelledby="booking-title-{lang}"><div class="booking-modal-card">
<button class="booking-close" type="button" data-booking-close aria-label="{E(tx[10])}">×</button><div class="booking-brand" aria-hidden="true">DO</div>
<form class="inquiry-mini" data-inquiry name="rental-inquiry" method="POST" action="?booking_sent=1" data-netlify="true" netlify-honeypot="company" data-lang="{lang}">
<input type="hidden" name="form-name" value="rental-inquiry"><input type="hidden" name="context" value="{E(context)}"><input type="hidden" name="requested_car" value=""><input type="hidden" name="car_slug" value=""><input type="hidden" name="page_url" value=""><p class="hp" hidden><label>Company<input name="company" tabindex="-1" autocomplete="off"></label></p>
<h2 id="booking-title-{lang}">{E(tx[0])}</h2><p class="booking-lead">{E(tx[9])}</p><div class="booking-choice" data-booking-choice hidden><small>{E(tx[1])}</small><strong></strong></div>
<div class="inquiry-grid"><label>{E(tx[2])}<input name="start" type="date" required></label><label>{E(tx[3])}<input name="end" type="date" required></label><label>{E(tx[4])}<input name="name" required autocomplete="name"></label><label>{E(tx[5])}<input name="phone" required autocomplete="tel"></label><label>{E(tx[11])}<input name="email" type="email" autocomplete="email"></label><label>{E(tx[12])}<input name="pickup" autocomplete="off"></label><label>{E(tx[13])}<input name="dropoff" autocomplete="off"></label><label class="inquiry-notes inquiry-driver"><input type="checkbox" name="with_driver" value="1"> {E(tx[14])}</label><label class="inquiry-notes">{E(tx[6])}<textarea name="notes" rows="2"></textarea></label></div>
<p class="inquiry-quote" data-quote aria-live="polite"></p>
<div class="inquiry-actions"><button class="btn" type="submit">{E(tx[8])}</button><button class="btn ghost wa" type="button" data-inquiry-wa>{E(tx[7])}</button></div><p class="inquiry-status" role="status" aria-live="polite"></p></form></div></div>'''


# ══════════════════════════════════════════════════════════════ page renders
def community_block(lang):
    tx = {
        "ka": ("აღმოაჩინეთ ინტერესის მიხედვით", "კულინარია", "სასტუმროები", "მიზნობრივი ტურები", "ველოტურები", "მოგზაურთა საზოგადოება", "საჯარო ტურები", "ჯგუფები", "შეფასებები", "შესვლა და მონაწილეობა"),
        "en": ("Explore by interest", "Culinary", "Hotels", "Themed tours", "Cycling", "Traveller community", "Public trips", "Groups", "Reviews", "Sign in to participate"),
        "ru": ("Выберите интерес", "Кулинария", "Отели", "Тематические туры", "Велотуры", "Сообщество путешественников", "Открытые поездки", "Группы", "Отзывы", "Войдите, чтобы участвовать"),
        "fa": ("بر اساس علاقه کاوش کنید", "آشپزی", "هتل‌ها", "تورهای موضوعی", "دوچرخه‌سواری", "جامعه مسافران", "سفرهای عمومی", "گروه‌ها", "نظرها", "برای مشارکت وارد شوید"),
        "he": ("גלו לפי עניין", "קולינריה", "מלונות", "סיורים נושאיים", "רכיבה על אופניים", "קהילת מטיילים", "טיולים ציבוריים", "קבוצות", "ביקורות", "התחברו כדי להשתתף"),
        "ar": ("استكشف حسب الاهتمام", "الطهي", "الفنادق", "جولات هادفة", "ركوب الدراجات", "مجتمع المسافرين", "رحلات عامة", "مجموعات", "تقييمات", "سجّل الدخول للمشاركة")
    }[lang]
    cards = [(tx[1], "food", "food"), (tx[2], "hotel", "hotel"),
             (tx[3], "tour", "culture"), (tx[4], "bike", "cycling")]
    interests = "".join(
        f'<a class="interest-card {kind}" href="{page_url(lang, "map", False)}?interest={query}"><span></span><b>{E(label)}</b></a>'
        for label, kind, query in cards)
    return (f'<section class="sec community-interests"><div class="wrap"><h2>{E(tx[0])}</h2>'
            f'<div class="interest-grid">{interests}</div></div></section>'
            f'<section class="sec alt"><div class="wrap"><h2>{E(tx[5])}</h2>'
            f'<div class="community-tabs" role="tablist"><button class="on" data-community-tab="trips">{E(tx[6])}</button>'
            f'<button data-community-tab="groups">{E(tx[7])}</button><button data-community-tab="reviews">{E(tx[8])}</button></div>'
            f'<div id="community-app" class="community-app" data-signin="{E(tx[9])}"><p class="muted">…</p></div>'
            f'</div></section>')


def render_static_page(lang, page):
    p = {k: counts_sub(v) for k, v in PAGES[page][lang].items()}
    if page == "contact":
        contact_leads = {
            "ka": "მოგვწერეთ ან დაგვირეკეთ ავტომობილის მოთხოვნისთვის. მიუთითეთ თარიღები, აღების ადგილი და სასურველი ავტომობილი.",
            "en": "Send a rental request or contact us by phone or WhatsApp. Include your dates, pickup point and preferred vehicle.",
            "ru": "Отправьте запрос на аренду или свяжитесь с нами по телефону или WhatsApp. Укажите даты, место получения и автомобиль.",
            "fa": "درخواست اجاره ارسال کنید یا از طریق تلفن و واتس‌اپ تماس بگیرید. تاریخ، محل تحویل و خودروی موردنظر را ذکر کنید.",
            "he": "שלחו בקשת השכרה או צרו קשר בטלפון או ב-WhatsApp. ציינו תאריכים, מקום איסוף ורכב מועדף.",
            "ar": "أرسل طلب تأجير أو تواصل معنا عبر الهاتف أو واتساب، مع ذكر التواريخ ومكان الاستلام والسيارة المفضلة."
        }
        p["lead"] = contact_leads[lang]
    u = UI[lang]
    depth = 0 if page == "index" else 1
    if lang != ROOT_LANG:
        depth += 1
    body = []
    tail_js = ""
    if page == "index":
        h = dict(p["hero"])
        h.update(HOME_HERO[lang])
        p["h1"] = h["h1"]
        # (primary CTA, public trips, note, standard tours, community)
        # Standard tours and public trips are different products — curated
        # build-time routes versus user-published trips — so they stay as
        # separate buttons instead of one label covering both.
        hero_cta = {
            "ka": ("დაიწყე ტურის დაგეგმვა", "ნახე საჯარო ტურები", "დაწყება უფასოა · რეგისტრაცია მხოლოდ შენახვისა და გაზიარებისთვის დაგჭირდება", "სტანდარტული ტურები", "Community"),
            "en": ("Start planning your trip", "Explore public trips", "Start for free · Sign in only when you want to save or share", "Standard tours", "Community"),
            "ru": ("Начать планирование", "Смотреть публичные поездки", "Начните бесплатно · Вход нужен только для сохранения и публикации", "Стандартные туры", "Community"),
            "fa": ("برنامه‌ریزی سفر را شروع کنید", "سفرهای عمومی را ببینید", "شروع رایگان است · ورود فقط برای ذخیره یا اشتراک‌گذاری لازم است", "تورهای استاندارد", "Community"),
            "he": ("התחילו לתכנן טיול", "גלו טיולים ציבוריים", "מתחילים בחינם · כניסה נדרשת רק לשמירה או לשיתוף", "טיולים סטנדרטיים", "Community"),
            "ar": ("ابدأ تخطيط رحلتك", "استكشف الرحلات العامة", "ابدأ مجانًا · تسجيل الدخول مطلوب فقط للحفظ أو المشاركة", "الجولات القياسية", "Community"),
        }[lang]
        x = TRAVEL[lang]["exp"]
        facts = "".join(f"<div><b>{E(x2['v'])}</b><span>{E(x2['k'])}</span></div>"
                        for x2 in h["facts"])
        body.append(landing_block(lang))
        map_section = ""
        flow = {
            "ka": ("დაგეგმე. მოარგე. გააზიარე.", "მოგზაურობის სრული გზა ერთ სივრცეში.",
                   "1", "დაგეგმე", "მიუთითე დრო, ინტერესები და თანამგზავრები.",
                   "2", "მოარგე", "დაამატე ან ამოიღე ადგილები პირდაპირ რუკაზე.",
                   "3", "გააზიარე", "მოიწვიე მეგობრები ან იპოვე თანამგზავრები.",
                   "საჯარო ტურების ნახვა"),
            "en": ("Plan. Shape. Share.", "The complete trip journey in one place.",
                   "1", "Plan", "Set your dates, interests, and travel party.",
                   "2", "Shape", "Add or remove places directly on the map.",
                   "3", "Share", "Invite friends or connect with fellow travellers.",
                   "Explore public trips"),
            "ru": ("Планируйте. Настраивайте. Делитесь.", "Весь путь путешествия в одном месте.",
                   "1", "Планируйте", "Укажите даты, интересы и состав группы.",
                   "2", "Настраивайте", "Добавляйте и удаляйте места прямо на карте.",
                   "3", "Делитесь", "Приглашайте друзей или находите попутчиков.",
                   "Смотреть публичные поездки"),
            "fa": ("برنامه‌ریزی. شخصی‌سازی. اشتراک‌گذاری.", "تمام مسیر سفر در یک فضا.",
                   "۱", "برنامه‌ریزی", "تاریخ، علایق و همراهان را مشخص کنید.",
                   "۲", "شخصی‌سازی", "مکان‌ها را مستقیماً روی نقشه اضافه یا حذف کنید.",
                   "۳", "اشتراک‌گذاری", "دوستان را دعوت کنید یا هم‌سفر پیدا کنید.",
                   "مشاهده سفرهای عمومی"),
            "he": ("מתכננים. מתאימים. משתפים.", "כל מסע הטיול במקום אחד.",
                   "1", "מתכננים", "בחרו תאריכים, תחומי עניין והרכב מטיילים.",
                   "2", "מתאימים", "הוסיפו או הסירו מקומות ישירות במפה.",
                   "3", "משתפים", "הזמינו חברים או מצאו שותפים למסע.",
                   "צפייה בטיולים ציבוריים"),
            "ar": ("خطط. خصص. شارك.", "رحلة التخطيط كاملة في مكان واحد.",
                   "١", "خطط", "حدد التواريخ والاهتمامات ورفقاء السفر.",
                   "٢", "خصص", "أضف الأماكن أو احذفها مباشرة على الخريطة.",
                   "٣", "شارك", "ادعُ الأصدقاء أو تواصل مع مسافرين آخرين.",
                   "استكشف الرحلات العامة"),
        }[lang]
        steps = "".join(
            f'<article><span>{E(flow[i])}</span><div><h3>{E(flow[i + 1])}</h3><p>{E(flow[i + 2])}</p></div></article>'
            for i in (2, 5, 8))
        body.append(f'<section class="journey-flow"><div class="wrap"><div class="journey-flow-head">'
                    f'<div><h2>{E(flow[0])}</h2><p>{E(flow[1])}</p></div>'
                    f'<a class="text-link" href="{page_url(lang, "community", False)}">{E(flow[11])} →</a>'
                    f'</div><div class="journey-steps">{steps}</div></div></section>')
        # ── RentUp Pages მაკეტის სექციები: სტანდარტული ტურები + ავტოპარკი ──
        tt = {
            "ka": ("სტანდარტული ტურები", "მზა მარშრუტები ღამისთევებით, რეალური სავალი დროებით და რეკომენდებული ავტომობილით.",
                   "დღე", "კმ", "ნახვა", "დაგეგმვა", "ყველა ტურის ნახვა",
                   "ავტოპარკი", "რომელი მანქანები გვაქვს — ფასი დამოკიდებულია ვადაზე: 1–6, 7–29 და 30+ დღე.",
                   "ყველა ავტომობილი"),
            "en": ("Standard tours", "Ready-made routes with overnights, realistic drive times and a recommended vehicle.",
                   "days", "km", "View", "Plan", "See all tours",
                   "Fleet", "Our vehicles — pricing depends on duration: 1–6, 7–29 and 30+ days.",
                   "All vehicles"),
            "ru": ("Стандартные туры", "Готовые маршруты с ночёвками, реальным временем в пути и рекомендованным автомобилем.",
                   "дн.", "км", "Смотреть", "Спланировать", "Все туры",
                   "Автопарк", "Наши автомобили — цена зависит от срока: 1–6, 7–29 и 30+ дней.",
                   "Все автомобили"),
            "fa": ("تورهای استاندارد", "مسیرهای آماده با اقامت شبانه، زمان واقعی رانندگی و خودروی پیشنهادی.",
                   "روز", "کیلومتر", "مشاهده", "برنامه‌ریزی", "همه تورها",
                   "ناوگان", "خودروهای ما — قیمت به مدت بستگی دارد: ۱–۶، ۷–۲۹ و ۳۰+ روز.",
                   "همه خودروها"),
            "he": ("טיולים סטנדרטיים", "מסלולים מוכנים עם לינות, זמני נסיעה מציאותיים ורכב מומלץ.",
                   "ימים", "ק״מ", "צפייה", "תכנון", "כל הטיולים",
                   "צי הרכבים", "הרכבים שלנו — המחיר תלוי במשך: 1–6, 7–29 ו-30+ ימים.",
                   "כל הרכבים"),
            "ar": ("الجولات القياسية", "مسارات جاهزة مع مبيت وأوقات قيادة واقعية وسيارة موصى بها.",
                   "أيام", "كم", "عرض", "خطط", "كل الجولات",
                   "الأسطول", "سياراتنا — السعر حسب المدة: 1–6، 7–29 و30+ يومًا.",
                   "كل السيارات"),
        }[lang]
        tcards = []
        for slug, route in list(ROUTES.items())[:4]:
            R = route[lang]
            rimg = route.get("image")
            if not rimg:
                for w in route.get("waypoints", []):
                    if w in ATTRACTIONS and ATTRACTIONS[w].get("image"):
                        rimg = ATTRACTIONS[w]["image"]
                        break
            rph = (f'<div class="ph"><img src="{E(rimg)}" alt="{E(R["name"])}" loading="lazy" '
                   f'width="640" height="360"></div>' if rimg
                   else f'<div class="ph">{E(R["name"])}{" — ფოტო" if lang == "ka" else ""}</div>')
            days = int(route["days"])
            km = int(route["distance_km"])
            ru_ = route_url(lang, slug, False)
            tcards.append(
                f'<article class="tourcard">{rph}<div class="in">'
                f'<div class="trow"><h3><a href="{ru_}">{E(R["name"])}</a></h3>'
                f'<span class="tag">{days} {E(tt[2])}</span></div>'
                f'<p class="meta">{days} {E(tt[2])} · {km} {E(tt[3])}</p>'
                f'<p class="sub">{E(R.get("short", ""))}</p>'
                f'<div class="btns"><a class="btn sm" href="{ru_}">{E(tt[4])}</a>'
                f'<a class="btn sm ghost" href="{page_url(lang, "map", False)}#planner" data-open-standard-tour data-tour="{E(slug)}">{E(tt[5])}</a>'
                f'</div></div></article>')
        body.append(f'<section class="sec home-tours"><div class="wrap">'
                    f'<div class="sec-head"><div><h2>{E(tt[0])}</h2><p class="lead">{E(tt[1])}</p></div>'
                    f'<a class="btn ghost" href="{page_url(lang, "map", False)}#planner" data-open-standard-tour>{E(tt[6])}</a></div>'
                    f'<div class="tour-grid">{"".join(tcards)}</div></div></section>')
        body.append(f'<section class="sec alt home-fleet"><div class="wrap">'
                    f'<div class="sec-head"><div><h2>{E(tt[7])}</h2><p class="lead">{E(tt[8])}</p></div>'
                    f'<a class="btn alt" data-car-search href="{page_url(lang, "fleet", False)}">{E(tt[9])}</a></div>'
                    f'{cars_grid(None, lang, limit=3)}</div></section>')
    else:
        body.append(f'<section class="page-head"><div class="wrap"><h1>{E(p["h1"])}</h1>'
                    f'<p class="lead">{inline(p["lead"], lang)}</p></div></section>')
    if page == "fleet":
        # ღია ტექსტი დანამატებზე — ავტოპარკის სიის თავში, ფასების გვერდით.
        body.append(f'<section class="sec fleet-pricenote"><div class="wrap">'
                    f'{surcharge_note_html(lang, "pricenote fleet-note")}</div></section>')
    if page == "account":
        body.append('<section class="sec account-sec"><div class="wrap"><div id="account" class="account-shell"></div></div></section>')
    if page == "community":
        body.append(community_block(lang))
    if page == "contact":
        uu = u["ui"]
        contact_tx = {
            "ka": ("დაგვიკავშირდით", "ტელეფონი", "მობილური / WhatsApp", "ელფოსტა", "მისამართი", "სამუშაო საათები", "ჯავშნის მოთხოვნისთვის მოგვწერეთ თარიღები, აღების ადგილი და სასურველი ავტომობილი."),
            "en": ("Contact us", "Phone", "Mobile / WhatsApp", "Email", "Address", "Working hours", "For a rental request, send us your dates, pickup point and preferred vehicle."),
            "ru": ("Свяжитесь с нами", "Телефон", "Мобильный / WhatsApp", "Эл. почта", "Адрес", "Часы работы", "Для запроса аренды укажите даты, место получения и желаемый автомобиль."),
            "fa": ("تماس با ما", "تلفن", "موبایل / واتس‌اپ", "ایمیل", "نشانی", "ساعات کاری", "برای درخواست اجاره، تاریخ‌ها، محل تحویل و خودروی موردنظر را ارسال کنید."),
            "he": ("צרו קשר", "טלפון", "נייד / WhatsApp", "דוא״ל", "כתובת", "שעות פעילות", "לבקשת השכרה שלחו תאריכים, מקום איסוף ורכב מועדף."),
            "ar": ("اتصل بنا", "الهاتف", "الجوال / واتساب", "البريد الإلكتروني", "العنوان", "ساعات العمل", "لطلب التأجير أرسل التواريخ ومكان الاستلام والسيارة المفضلة.")
        }[lang]
        addr = SITE["address"][lang]
        body.append(
            f'<section class="sec"><div class="wrap"><h2>{E(contact_tx[0])}</h2>'
            f'<dl class="facts contact-facts">'
            f'<div><dt class="k">{E(contact_tx[1])}</dt><dd class="v"><a dir="ltr" href="tel:{E(SITE["phone_e164"])}">{E(SITE["phone"])}</a></dd></div>'
            + (f'<div><dt class="k">{E(contact_tx[2])}</dt><dd class="v"><a dir="ltr" href="tel:{E(SITE["mobile_e164"])}">{E(SITE["mobile"])}</a></dd></div>'
               if SITE.get("mobile") else "")
            + (f'<div><dt class="k">{E(contact_tx[3])}</dt><dd class="v"><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></dd></div>'
               if SITE.get("email") else "")
            +
            f'<div><dt class="k">{E(contact_tx[4])}</dt><dd class="v">{E(addr["street"])}, {E(addr["city"])} {E(SITE["address_zip"])}</dd></div>'
            f'<div><dt class="k">{E(contact_tx[5])}</dt><dd class="v">{E(SITE["opens"])}–{E(SITE["closes"])}</dd></div></dl>'
            f'<p>{E(contact_tx[6])}</p><h2>{E(uu["f_title"])}</h2>'
            f'<form class="cform" name="contact" method="POST" data-netlify="true" '
            f'netlify-honeypot="bot-field" action="?sent=1">'
            f'<input type="hidden" name="form-name" value="contact">'
            f'<p class="vh"><label>bot<input name="bot-field"></label></p>'
            f'<div class="cf2"><label>{E(uu["f_name"])}<input name="name" required></label>'
            f'<label>{E(uu["f_email"])}<input type="email" name="email" required></label></div>'
            f'<label>{E(uu["f_dates"])}<input name="dates"></label>'
            f'<label>{E(uu["f_msg"])}<textarea name="message" rows="5" required></textarea></label>'
            f'<div class="prow"><button class="btn" type="submit">{E(uu["f_send"])}</button>'
            f'<a class="btn wa" href="{wa_link(lang)}" rel="noopener" target="_blank">'
            f'{E(uu["wa_btn"])}</a></div>'
            f'<p class="rentnote fok" hidden>{E(uu["f_ok"])}</p></form>'
            f'<script>if(location.search.indexOf("sent=1")>-1)'
            f'{{var f=document.querySelector(".fok");if(f)f.hidden=false;}}</script>'
            f'</div></section>')

    sections, cur = [], []
    for b in p["blocks"]:
        if b["type"] == "h2" and cur:
            sections.append(cur); cur = []
        cur.append(b)
    if cur:
        sections.append(cur)
    rendered_sections = []
    for i, s in enumerate([] if page == "contact" else sections):
        inner = "\n".join(render_block(b, lang) for b in s)
        rendered_sections.append(f'<section class="sec{" alt" if i % 2 else ""}">'
                                 f'<div class="wrap">{inner}</div></section>')
    if page == "index" and rendered_sections:
        more_label = {
            "ka": "კომპანიის პირობები და დამატებითი ინფორმაცია",
            "en": "Rental terms and more information",
            "ru": "Условия аренды и дополнительная информация",
            "fa": "شرایط اجاره و اطلاعات بیشتر",
            "he": "תנאי השכרה ומידע נוסף",
            "ar": "شروط التأجير ومعلومات إضافية",
        }[lang]
        body.append(f'<section class="home-more-wrap"><div class="wrap">'
                    f'<details class="home-more"><summary>{E(more_label)}</summary>'
                    f'<div class="home-more-facts hero-facts">{facts}</div>'
                    f'{"".join(rendered_sections)}</details></div></section>')
    else:
        body.extend(rendered_sections)

    if page == "fleet":
        other_label = {
            "ka": "სხვა ავტომობილები",
            "en": "More cars",
            "ru": "Другие автомобили",
            "fa": "خودروهای دیگر",
            "he": "רכבים נוספים",
            "ar": "سيارات أخرى",
        }[lang]
        # Hidden until `catalogue.js` puts a car in it — see the note above.
        body.append(
            f'<section class="sec" data-live-other hidden>'
            f'<div class="wrap"><h2 id="{slugify_anchor(other_label)}">'
            f'{E(other_label)}</h2>'
            f'<div class="cars" data-live-catalogue="*"></div></div></section>')

    graph = [org_node(lang), website_node(lang),
             {"@type": "WebPage", "@id": page_url(lang, page) + "#webpage",
              "url": page_url(lang, page), "name": p["title"], "description": p["desc"],
              "inLanguage": lang, "isPartOf": {"@id": SITE_URL + "/#website"},
              "about": {"@id": SITE_URL + "/#organization"},
              "datePublished": "2026-01-15", "dateModified": TODAY}]
    trail = [(u["nav"]["index"], page_url(lang, "index"))]
    if page != "index":
        trail.append((u["nav"][page], page_url(lang, page)))
    graph.append(crumbs_node(lang, trail))
    f = faq_node(p["blocks"])
    if f:
        graph.append(f)
    if page in ("index", "software"):
        graph.append(software_node(lang))
    if page == "index":
        graph.append({"@type": "ItemList", "name": TRAVEL[lang]["exp"]["explore_h"],
                      "numberOfItems": len(ATTRACTIONS),
                      "url": index_hub_url(lang, "attractions"),
                      "itemListElement": [
                          {"@type": "ListItem", "position": i + 1,
                           "url": region_url(lang, k), "name": REGIONS[k][lang]["name"]}
                          for i, k in enumerate(REGIONS)]})
    if page == "fleet":
        graph.append(offer_catalog(lang))
        graph.append({"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": car_url(lang, s)}
            for i, s in enumerate(CARS)]})

    _tpl = {"index": "home", "fleet": "fleet", "terms": "terms", "faq": "faq",
            "about": "about", "contact": "contact", "community": "community",
            "software": "software"}.get(page)
    if _tpl:
        _st, _sd = seo_meta(_tpl, lang, count=len(CARS))
        if _st:
            p = dict(p); p["title"] = _st; p["desc"] = _sd or p["desc"]
    head = head_html(lang, page, p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, page),
                     {l: page_url(l, page) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph},
                     # The homepage is a landing page since the planner moved to
                     # /map/ — it renders no Leaflet map, so don't ship its CSS.
                     leaflet=False)
    crumbs = crumbs_html(lang, [] if page == "index" else
                         [(u["nav"]["index"], page_url(lang, "index", False)),
                          (u["nav"][page], None)])
    return shell(lang, page, head, crumbs + '<main id="main">' + "".join(body) + "</main>",
                 depth, tail_js)


def render_business_card(lang):
    tx = {
        "ka": ("შოთა ლომიძე", "ავტო გაქირავება • მძღოლით მომსახურება", "დარეკვა", "ვებგვერდი", "კონტაქტის შენახვა", "დაასკანირე QR და დაამატე კონტაქტებში", "შოთა ლომიძე — RentUp | ელექტრონული ვიზიტკა", "RentUp-ის ავტო გაქირავებისა და მძღოლით მომსახურების საკონტაქტო ვიზიტკა."),
        "en": ("Shota Lomidze", "Car rental • Chauffeur service", "Call", "Website", "Save contact", "Scan the QR code to add the contact", "Shota Lomidze — RentUp | Business card", "RentUp car rental and chauffeur service contact card."),
        "ru": ("Шота Ломидзе", "Аренда автомобилей • Услуги водителя", "Позвонить", "Веб-сайт", "Сохранить контакт", "Отсканируйте QR-код, чтобы добавить контакт", "Шота Ломидзе — RentUp | Визитка", "Контактная визитка RentUp: аренда автомобилей и услуги водителя."),
        "fa": ("شوتا لومیدزه", "اجاره خودرو • خدمات خودرو با راننده", "تماس", "وب‌سایت", "ذخیره مخاطب", "برای افزودن مخاطب، کد QR را اسکن کنید", "شوتا لومیدزه — RentUp | کارت ویزیت", "کارت تماس خدمات اجاره خودرو و خودرو با راننده RentUp."),
        "he": ("שוטה לומידזה", "השכרת רכב • שירות עם נהג", "התקשרו", "אתר", "שמירת איש קשר", "סרקו את קוד ה-QR כדי להוסיף את איש הקשר", "שוטה לומידזה — RentUp | כרטיס ביקור", "כרטיס קשר לשירותי השכרת רכב ורכב עם נהג של RentUp."),
        "ar": ("شوتا لوميدزه", "تأجير السيارات • خدمة سيارة مع سائق", "اتصال", "الموقع", "حفظ جهة الاتصال", "امسح رمز QR لإضافة جهة الاتصال", "شوتا لوميدزه — RentUp | بطاقة العمل", "بطاقة اتصال لخدمات تأجير السيارات والسيارة مع سائق من RentUp."),
    }[lang]
    name, role, call, website, save, scan, title, desc = tx
    url = page_url(lang, "card")
    alternates = {l: page_url(l, "card") for l in LANGS}
    ld = {"@context": "https://schema.org", "@type": "Person", "name": "Shota Lomidze",
          "worksFor": {"@type": "Organization", "name": "RentUp", "url": SITE_URL},
          "telephone": "+995597555565", "url": url}
    head = head_html(lang, "card", title, desc, "RentUp, Shota Lomidze", url,
                     alternates, 1, ld)
    def card_lang_href(target):
        if target == lang:
            return "./"
        if lang == ROOT_LANG:
            return f"../{target}/business-card/"
        if target == ROOT_LANG:
            return "../../business-card/"
        return f"../../{target}/business-card/"

    card_langs = "".join(
        f'<a href="{card_lang_href(l)}" hreflang="{l}" lang="{l}" class="{"on" if l == lang else ""}">{LANG_SHORT[l]}</a>'
        for l in LANGS)
    body = f'''<main id="main" class="digital-card-page"><div class="digital-card-shell">
<nav class="card-languages" aria-label="{E(UI[lang]['ui']['lang_label'])}">{card_langs}</nav>
<article class="road-pass-card" aria-labelledby="card-name">
<div class="road-pass-top"><span>DRIVE ON • GEORGIA</span><strong>ROAD PASS <span aria-hidden="true">✈</span></strong></div>
<div class="road-pass-body"><div class="road-pass-identity">
<div class="road-pass-brand"><img src="/assets/do-logo-tight.png" alt=""><b>RentUp</b></div>
<h1 id="card-name">{E(name)}</h1><p class="road-pass-role">{E(role)}</p>
<a class="card-contact-line" href="tel:+995597555565" aria-label="{E(call)}: +995 597 55 55 65"><span aria-hidden="true">☎</span><bdi dir="ltr">+995 597 55 55 65</bdi></a>
<a class="card-contact-line card-site" href="https://www.rentup.ge/" aria-label="{E(website)}: www.rentup.ge"><span aria-hidden="true">↗</span><bdi dir="ltr">www.rentup.ge</bdi></a>
<a class="btn card-save" href="/assets/shota-lomidze-drive-on.vcf" download>{E(save)}</a>
</div><div class="road-pass-qr"><a href="/assets/shota-lomidze-drive-on.vcf" download aria-label="{E(save)}"><img src="/assets/shota-lomidze-vcard.svg" alt="QR — {E(save)}"></a><p>{E(scan)}</p></div></div>
</article></div></main>'''
    depth = 1 if lang == ROOT_LANG else 2
    page = (f'<!DOCTYPE html>\n<html lang="{lang}" dir="{LANG_DIR[lang]}"><head>\n{head}\n{analytics_html()}\n</head>'
            f'<body class="page-card card-standalone">{body}</body></html>')
    # Keep the generated card fully previewable as a local file as well as on the deployed site.
    # Root-relative assets resolve against the drive root under file://, so card assets use a
    # directory-relative prefix here.
    asset_prefix = "../" if lang == ROOT_LANG else "../../"
    page = page.replace('href="/assets/', f'href="{asset_prefix}assets/')
    page = page.replace('src="/assets/', f'src="{asset_prefix}assets/')
    page = page.replace('href="/favicon.svg"', f'href="{asset_prefix}favicon.svg"')
    return page


def render_car(lang, slug, c):
    L = c[lang]
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    title = f'{L["name"]} — {u["ui"]["rent_word"]} {SITE["fleet_size"]}'  # placeholder replaced below
    title = f'{L["name"]} — {u["ui"]["rent_word"]} {c["price_1_6"]} ₾/{SPECS["units"]["day"][lang]} | {BRAND}'
    desc = f'{L["name"]}, {c["years"]}, {engine_label(c["engine"], lang)}. {L.get("summary","")}. ' \
           f'{spec_label("price_1_6", lang)}: {c["price_1_6"]} ₾. {L.get("body","")[:80]}'
    desc = re.sub(r"\s+", " ", desc)[:178]

    img = c.get("image")
    gal_items = [g.get("image") if isinstance(g, dict) else g for g in (c.get("gallery") or [])]
    gal = "".join(f'<img src="{E(g)}" alt="{E(L["name"])}" loading="lazy">'
                  for g in gal_items if g)
    main_img = (f'<img src="{E(img)}" alt="{E(L["name"])} — {E(cat_label(c["category"], lang))}" '
                f'width="960" height="600">' if img else f'<div class="ph">{E(L["name"])}</div>')

    rows = []
    for k in ("years", "engine", "transmission", "drive", "seats", "luggage",
              "fuel_100km", "clearance"):
        v = c.get(k)
        if not v:
            continue
        if k == "engine":
            v = engine_label(v, lang)
        elif k in ("transmission", "drive"):
            v = spec_value(v, lang)
        elif k == "fuel_100km":
            v = f'{v} {SPECS["units"]["l"][lang]}'
        elif k == "clearance":
            v = f'{v} {SPECS["units"]["mm"][lang]}'
        rows.append(f'<tr><th scope="row">{E(spec_label(k, lang))}</th><td>{E(v)}</td></tr>')

    prices = "".join(
        f'<tr><th scope="row">{E(spec_label(k, lang))}</th><td>{E(money(c[k]))}</td></tr>'
        for k in ("price_1_6", "price_7_29", "price_30") if c.get(k))
    prices += (f'<tr><th scope="row">{E(spec_label("deposit", lang))}</th>'
               f'<td>{E(money(c["deposit"]))}</td></tr>')
    prices += (f'<tr><th scope="row">{E(SURCHARGE_LABEL[lang])}</th>'
               f'<td>{E(surcharge_fmt(SURCHARGE_SHORT[lang], lang))}</td></tr>')

    feats = "".join(f"<li>{inline(x, lang)}</li>" for x in L.get("features", []))
    body_html = render_md(L.get("body", ""), lang)

    brand, _, model = L["name"].partition(" ")
    body = f"""<section class="page-head" data-analytics-car data-analytics-car-view data-car="{E(slug)}" data-car-name="{E(L['name'])}" data-brand="{E(brand)}" data-model="{E(model)}" data-price="{E(c['price_1_6'])}"><div class="wrap">
<h1>{E(L['name'])}</h1><p class="lead">{E(L.get('summary',''))} · {E(cat_label(c['category'], lang))}</p>
</div></section>
<section class="sec"><div class="wrap"><div class="cardetail">
<div class="gal">{main_img}{gal}</div>
<div>
<div class="pricebox"><span class="big">{E(money(c['price_1_6']))} <small>/ {E(SPECS['units']['day'][lang])}</small></span></div>
{surcharge_note_html(lang)}
<div class="tbl-wrap"><table class="spec"><tbody>{"".join(rows)}</tbody></table></div>
<div class="tbl-wrap"><table class="spec"><caption>{E(u['ui']['price_table'])}</caption><tbody>{prices}</tbody></table></div>
<ul>{feats}</ul>
</div></div>
<div class="article">{body_html}</div>
<div class="cta"><h2>{E(u['ui']['book_title'])}</h2><p>{inline(u['ui']['book_text'], lang)}</p>
<button class="btn booking-hero-cta" type="button" data-booking-open data-car="{E(slug)}" data-car-name="{E(L['name'])}">{E(BOOKING_TEXT[lang]['book'])}</button>
<div class="row"><a class="btn ghost" href="{page_url(lang,'contact',False)}">{E(u['nav']['contact'])}</a>
<a class="btn ghost" href="{page_url(lang,'fleet',False)}">{E(u['nav']['fleet'])}</a></div></div>
</div></section>"""

    graph = [org_node(lang), website_node(lang), car_node(slug, c, lang),
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["fleet"], page_url(lang, "fleet")),
                                (L["name"], car_url(lang, slug))])]
    _st, _sd = seo_meta("car", lang, name=L["name"], price=c.get("price_1_6", ""),
                        category=car_cat_label(c["category"], lang), seats=c.get("seats", ""))
    if _st:
        title, desc = _st, (_sd or desc)
    head = head_html(lang, "fleet", title, desc,
                     f'{L["name"]}, {L["name"]} {u["ui"]["rent_word"]}, {cat_label(c["category"], lang)}',
                     car_url(lang, slug), {l: car_url(l, slug) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph},
                     og_type="product", image=abs_url(img))
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["fleet"], page_url(lang, "fleet", False)),
                                (L["name"], None)])
    return shell(lang, "fleet", head, crumbs + f'<main id="main">{body}</main>', depth)


def fmt_date(d, lang):
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    months = {
        "ka": ["იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი", "ივლისი",
               "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"],
        "en": ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"],
        "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
               "августа", "сентября", "октября", "ноября", "декабря"],
        "fa": ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه",
               "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
        "he": ["בינואר", "בפברואר", "במרץ", "באפריל", "במאי", "ביוני", "ביולי",
               "באוגוסט", "בספטמבר", "באוקטובר", "בנובמבר", "בדצמבר"],
        "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو",
               "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    }[lang]
    return (f"{months[d.month-1]} {d.day}, {d.year}" if lang == "en"
            else f"{d.day} {months[d.month-1]} {d.year}")


def render_blog_index(lang):
    p = PAGES["blog"][lang]
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    cards = []
    for slug, post in POSTS.items():
        L = post[lang]
        ph = (f'<div class="ph"><img src="{E(post["image"])}" alt="{E(L["title"])}" '
              f'loading="lazy" width="640" height="360"></div>' if post.get("image") else "")
        cards.append(f'<article class="post-c">{ph}<div class="in">'
                     f'<time datetime="{post["date"]}">{E(fmt_date(post["date"], lang))}</time>'
                     f'<h2><a href="{post_url(lang, slug, False)}">{E(L["title"])}</a></h2>'
                     f'<p>{E(L["desc"])}</p></div></article>')
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(p["h1"])}</h1>'
            f'<p class="lead">{inline(p["lead"], lang)}</p></div></section>'
            f'<section class="sec"><div class="wrap"><div class="posts">'
            f'{"".join(cards)}</div></div></section>')
    graph = [org_node(lang), website_node(lang),
             {"@type": "Blog", "@id": page_url(lang, "blog") + "#blog",
              "name": p["title"], "description": p["desc"], "inLanguage": lang,
              "publisher": {"@id": SITE_URL + "/#organization"},
              "blogPost": [post_node(s, po, lang) for s, po in POSTS.items()]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["blog"], page_url(lang, "blog"))])]
    head = head_html(lang, "blog", p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, "blog"), {l: page_url(l, "blog") for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["blog"], None)])
    return shell(lang, "blog", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_post(lang, slug, post):
    L = post[lang]
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    img = (f'<img src="{E(post["image"])}" alt="{E(L["title"])}" width="1200" height="675" '
           f'style="border-radius:var(--radius);margin:0 0 26px">' if post.get("image") else "")
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(L["title"])}</h1>'
            f'<p class="lead">{inline(L["lead"], lang)}</p></div></section>'
            f'<section class="sec"><div class="wrap">{img}'
            f'<p class="meta-line"><time datetime="{post["date"]}">'
            f'{E(fmt_date(post["date"], lang))}</time> · {E(BRAND)}</p>'
            f'<div class="article">{render_md(L["body"], lang)}</div>'
            f'<div class="cta"><h2>{E(u["ui"]["book_title"])}</h2>'
            f'<p>{inline(u["ui"]["book_text"], lang)}</p><div class="row">'
            f'<a class="btn" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
            f'<a class="btn ghost" href="{page_url(lang,"fleet",False)}">{E(u["nav"]["fleet"])}</a>'
            f'<a class="btn ghost" href="{page_url(lang,"blog",False)}">{E(u["nav"]["blog"])}</a>'
            f"</div></div></div></section>")
    graph = [org_node(lang), website_node(lang), post_node(slug, post, lang),
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["blog"], page_url(lang, "blog")),
                                (L["title"], post_url(lang, slug))])]
    head = head_html(lang, "blog", f'{L["title"]} | {BRAND}', L["desc"],
                     L.get("keywords", ""), post_url(lang, slug),
                     {l: post_url(l, slug) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph},
                     og_type="article",
                     image=abs_url(post.get("image")))
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["blog"], page_url(lang, "blog", False)),
                                (L["title"], None)])
    return shell(lang, "blog", head, crumbs + f'<main id="main">{body}</main>', depth)


# ══════════════════════════════════════════════════════════════ travel pages
TRAVEL = load("content/settings/travel.yml")
PLACES = load("content/settings/places.yml")["places"]
ROAD_LEGS = (load("content/settings/road_legs.yml") if os.path.exists("content/settings/road_legs.yml") else {"legs": {}}).get("legs", {})
AUTH = load("content/settings/auth.yml") if os.path.exists("content/settings/auth.yml") else {}
HOTELS = (load("content/settings/hotels.yml") if os.path.exists("content/settings/hotels.yml") else {"towns": {}})["towns"]
SLOW_TOWNS = {"stepantsminda", "mestia-town", "khulo", "oni", "bakuriani",
              "ambrolauri", "akhalkalaki", "tkibuli", "sachkhere", "chiatura"}
ROAD_RANK_NUM = {"paved": 0, "mostly_paved": 1, "gravel": 2, "4x4_only": 3}
TB = (41.7151, 44.8271)          # თბილისი — მარშრუტების საწყისი წერტილი

TYPE_COLOR = {
    "monastery": "#8e6bb5", "fortress": "#b5563f", "cave": "#6b7a8f",
    "canyon": "#2b8a9e", "waterfall": "#2f9fd0", "lake": "#2f7fd0",
    "mountain": "#5b7c4a", "nature": "#3f8f5f", "town": "#c8963e",
    "museum": "#a0703c", "winery": "#8f2f52", "spa": "#3f9f8f",
    "beach": "#d8a13a", "ski": "#4a76b5", "archaeology": "#7a6a4f",
    "theatre": "#b43f72",
}


def tl(lang, group, key):
    """travel.yml-იდან ლეიბლი."""
    return TRAVEL[lang][group].get(str(key), str(key))


def tu(lang, key):
    return TRAVEL[lang]["ui"].get(key, key)


def car_cat_label(cat, lang):
    # Routes/attractions only ever recommend economy/suv/offroad, but the fleet
    # also has business/minivan/van — fall back to the fleet category label.
    return cat_label(cat, lang) if cat in {c["key"] for c in CATS} else cat_label("economy", lang)


def stars_html(r, lang, small=False):
    """სარედაქციო შეფასება 1–5 — ვიზუალური ვარსკვლავები + რიცხვი."""
    try:
        r = float(r)
    except (TypeError, ValueError):
        return ""
    if r <= 0:
        return ""
    full = int(r)
    half = 1 if r - full >= 0.5 else 0
    stars = "★" * full + ("½" if half else "") + "☆" * (5 - full - half)
    lbl = te(lang, "rate_label")
    cls = "stars sm" if small else "stars"
    return (f'<span class="{cls}" title="{E(lbl)}: {r:g}/5" aria-label="{E(lbl)}: {r:g}/5">'
            f'<i>{stars}</i><b>{r:g}</b></span>')


def gallery_html(a, lang):
    g = a.get("gallery") or []
    if not g:
        return ""
    cap = tu(lang, "photo_by")
    figs = "".join(
        f'<figure class="gph"><img src="{E(x["image"])}" alt="{E(a[lang]["name"])} — {i+1}" '
        f'loading="lazy" decoding="async">'
        f'<figcaption>{E(cap)}: '
        + (f'<a href="{E(x["source"])}" rel="nofollow noopener" target="_blank">{E(x["author"])}</a>'
           if x.get("source") else E(x["author"]))
        + (f' · <a href="{E(x["license_url"])}" rel="license nofollow noopener" target="_blank">'
           f'{E(x["license"])}</a>' if x.get("license_url") else f' · {E(x["license"])}' if x.get("license") else "")
        + '</figcaption></figure>'
        for i, x in enumerate(g))
    return f'<div class="gallery"><h2 class="vh">{E(te(lang, "gallery"))}</h2>{figs}</div>'


def photo_html(a, lang, cls="photo", hero=False):
    """სურათი + ავტორის მითითება — ლიცენზიის მოთხოვნაა."""
    img = a.get("image")
    if not img:
        pending = {
            "ka": "ფოტო გადამოწმების პროცესშია",
            "en": "Photo verification in progress",
            "ru": "Фото проходит проверку",
            "fa": "عکس در حال بررسی است",
            "he": "התמונה בתהליך אימות",
            "ar": "الصورة قيد التحقق",
        }
        return (f'<div class="note photo-pending" role="status">'
                f'{E(pending.get(lang, pending["en"]))}</div>')
    c = a.get("image_credit") or {}
    who = c.get("author") or "Wikimedia Commons"
    lic = c.get("license") or ""
    src = c.get("source") or ""
    lurl = c.get("license_url") or ""
    cap = f'{E(tu(lang, "photo_by"))}: '
    bits = [f'<a href="{E(src)}" rel="nofollow noopener" target="_blank">{E(who)}</a>' if src
            else E(who)]
    if lic:
        bits.append(f'<a href="{E(lurl)}" rel="license nofollow noopener" target="_blank">{E(lic)}</a>'
                    if lurl else E(lic))
    priority = ('loading="eager" fetchpriority="high" decoding="async" width="1100" height="688"'
                if hero else 'loading="lazy" decoding="async" width="1100" height="688"')
    return (f'<figure class="{cls}"><img src="{E(img)}" alt="{E(a[lang]["name"])}" {priority} '
            f'sizes="(max-width: 760px) 100vw, 1100px">'
            f'<figcaption>{cap}{" · ".join(bits)}</figcaption></figure>')


def attr_facts(a, lang):
    u = TRAVEL[lang]["ui"]
    items = [
        {"k": u["visit_time"], "v": f'{a["visit_hours"]} {u["hrs"]}'},
        {"k": u["from_tbilisi"], "v": f'{a["distance_tbilisi_km"]} {u["km"]} · {a["drive_time_tbilisi"]}'},
        {"k": u["road_label"], "v": tl(lang, "road", a["road"])},
        {"k": u["car_needed"], "v": car_cat_label(a["car_category"], lang)},
        {"k": u["season"], "v": tl(lang, "season", a["best_season"])},
        {"k": u["entry"], "v": a["entry_fee"]},
    ]
    return ('<dl class="facts">' + "".join(
        f'<div><dt class="k">{E(x["k"])}</dt><dd class="v">{E(x["v"])}</dd></div>'
        for x in items) + "</dl>")


def map_data_json(lang, attractions=None, routes=None):
    aa = attractions if attractions is not None else ATTRACTIONS
    rr = routes if routes is not None else ROUTES
    u = TRAVEL[lang]["ui"]
    pts = [{
        "s": s, "n": a[lang]["name"], "la": a["lat"], "lo": a["lon"],
        "t": tl(lang, "type", a["type"]), "c": TYPE_COLOR.get(a["type"], "#0f4c81"),
        "h": f'{a["visit_hours"]} {u["hrs"]}',
        "d": f'{a["distance_tbilisi_km"]} {u["km"]} · {a["drive_time_tbilisi"]}',
        "r": tl(lang, "road", a["road"]),
        "u": attr_url(lang, s, False),
        "g": a["region"],
    } for s, a in aa.items()]
    lines = [{
        "s": s, "n": r[lang]["name"], "c": list(TYPE_COLOR.values())[i * 3 % 15],
        "p": r["polyline"], "u": route_url(lang, s, False),
        "k": f'{r["days"]} {u["days"]} · {r["distance_km"]} {u["km"]}',
    } for i, (s, r) in enumerate(rr.items())]
    return J({"pts": pts, "lines": lines, "more": u["see_on_map"]})


MAP_JS = """
<script src="%(js)s"></script>
<script>
(function(){
  var D = %(data)s;
  var m = L.map('gmap', {scrollWheelZoom:false}).setView([%(lat)s, %(lon)s], %(zoom)s);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {maxZoom:17, attribution:'&copy; OpenStreetMap'}).addTo(m);
  D.lines.forEach(function(r){
    var pl = L.polyline(r.p, {color:r.c, weight:4, opacity:.75}).addTo(m);
    pl.bindPopup('<b>'+r.n+'</b><br>'+r.k+'<br><a href="'+r.u+'">&rarr;</a>');
  });
  D.pts.forEach(function(p){
    var mk = L.circleMarker([p.la, p.lo], {radius:7, color:'#fff', weight:2,
      fillColor:p.c, fillOpacity:1}).addTo(m);
    mk.bindPopup('<b><a href="'+p.u+'">'+p.n+'</a></b><br>'+p.t+
      '<br>&#9201; '+p.h+'<br>&#128663; '+p.d+'<br>&#128739; '+p.r);
    mk.bindTooltip(p.n);
  });
  m.on('click', function(){ m.scrollWheelZoom.enable(); });
})();
</script>"""


def map_block(lang, height=520, center=(42.15, 43.6), zoom=7,
              attractions=None, routes=None):
    js = MAP_JS % {"js": LEAFLET_JS, "data": map_data_json(lang, attractions, routes),
                   "lat": center[0], "lon": center[1], "zoom": zoom}
    return (f'<div id="gmap" class="gmap" style="height:{height}px"></div>'
            f'<p class="map-hint">{E(tu(lang, "map_hint"))}</p>'), js


def legend_html(lang):
    seen = sorted({a["type"] for a in ATTRACTIONS.values()})
    items = "".join(
        f'<span class="lg"><i style="background:{TYPE_COLOR.get(t, "#0f4c81")}"></i>'
        f"{E(tl(lang, 'type', t))}</span>" for t in seen)
    return f'<div class="legend"><b>{E(tu(lang,"legend_title"))}:</b> {items}</div>'


def te(lang, key):
    return TRAVEL[lang]["exp"].get(key, key)


# ══════════════════════════════════════════════ interactive map explorer
def explorer_points(lang):
    """მსუბუქი მონაცემები რუკის მარკერებისთვის — ყველა ღირსშესანიშნაობა."""
    u = TRAVEL[lang]["ui"]
    pts = []
    for s, a in ATTRACTIONS.items():
        f, v = road_model(a)
        pts.append({
            "s": s, "n": a[lang]["name"], "la": a["lat"], "lo": a["lon"],
            "names": [a.get(l, {}).get("name", "") for l in LANGS],
            "t": tl(lang, "type", a["type"]), "ty": a["type"],
            "c": TYPE_COLOR.get(a["type"], "#0f4c81"),
            "g": a["region"], "gn": REGIONS[a["region"]][lang]["name"],
            "h": f'{a["visit_hours"]} {u["hrs"]}', "hh": float(a["visit_hours"]),
            "d": f'{a["distance_tbilisi_km"]} {u["km"]} · {a["drive_time_tbilisi"]}',
            "u": attr_url(lang, s, False), "f": f, "v": v,
            "un": bool(a["unesco"]), "fe": bool(a["featured"]),
            # day-trip finder: which car the road needs, and when it is open
            "cc": a.get("car_category") or "economy",
            "bs": a.get("best_season") or "all",
            "oy": bool(a.get("open_year_round", True)),
            "img": a.get("image") or "", "r": a.get("rating") or 0,
            "rd": ROAD_RANK_NUM.get(a["road"], 0), "el": a.get("elevation") or 0,
            "bike": a["type"] in {"nature", "lake", "town", "beach", "mountain", "canyon", "waterfall"}
                    and ROAD_RANK_NUM.get(a["road"], 0) <= 2,
        })
    pts.sort(key=lambda p: p["n"])
    return pts


EXPLORER_INDEX_KEYS = (
    "s", "n", "la", "lo", "names", "t", "ty", "c", "g", "gn",
    "hh", "f", "v", "r", "rd", "el", "bike", "cc", "bs", "oy",
)


def explorer_point_index(lang):
    """Country-wide map index: enough for search, clustering and routing.

    Images, URLs and descriptive display fields live in regional chunks and are
    merged into these objects by workspace.js only when the relevant area is
    opened.  Keeping every slug here preserves instant multilingual search and
    lets a shared/standard tour be selected before any chunk has arrived.
    """
    return [{key: point[key] for key in EXPLORER_INDEX_KEYS}
            for point in explorer_points(lang)]


def explorer_chunks(lang):
    """Manifest and rich point payloads grouped by content region."""
    grouped = {}
    for point in explorer_points(lang):
        grouped.setdefault(point["g"], []).append(point)
    chunks, manifest = {}, {}
    for region, points in sorted(grouped.items()):
        bounds = [
            min(point["la"] for point in points),
            min(point["lo"] for point in points),
            max(point["la"] for point in points),
            max(point["lo"] for point in points),
        ]
        body = {"region": region, "pts": points}
        version = hashlib.sha256(JC(body).encode("utf-8")).hexdigest()[:12]
        manifest[region] = {
            "url": f"/data/points/{lang}/{region}.json?v={version}",
            "bounds": bounds,
            "count": len(points),
        }
        chunks[region] = body
    return manifest, chunks


def explorer_towns(lang):
    """ქალაქები და აეროპორტები — ათვლის/დანიშნულების წერტილებად."""
    out = []
    for p in PLACES:
        slow = p["key"] in SLOW_TOWNS
        out.append({
            "s": "town:" + p["key"], "n": p[lang], "la": p["lat"], "lo": p["lon"],
            "names": [p.get(l, "") for l in LANGS],
            "t": te(lang, p["kind"]), "k": p["kind"], "hh": 0.0,
            "c": "#37485c" if p["kind"] == "city" else "#8a6d3b",
            "f": 1.8 if slow else 1.4, "v": 38.0 if slow else 62.0,
            "gn": "", "h": "",
        })
    out.sort(key=lambda x: x["n"])
    return out


def attr_detail(lang, slug, a):
    """სრული აღწერა, რომელიც რუკის პანელში იტვირთება."""
    L = a[lang]
    u = TRAVEL[lang]["ui"]
    return {
        "s": slug, "n": L["name"], "t": tl(lang, "type", a["type"]),
        "gn": REGIONS[a["region"]][lang]["name"], "unesco": bool(a["unesco"]),
        "u": attr_url(lang, slug, False),
        "short": L["short"],
        "r": a.get("rating") or 0,
        "gal": [x["image"] for x in (a.get("gallery") or [])[:3]],
        "facts": [
            [u["visit_time"], f'{a["visit_hours"]} {u["hrs"]}'],
            [u["from_tbilisi"], f'{a["distance_tbilisi_km"]} {u["km"]} · {a["drive_time_tbilisi"]}'],
            [u["road_label"], tl(lang, "road", a["road"])],
            [u["car_needed"], car_cat_label(a["car_category"], lang)],
            [u["season"], tl(lang, "season", a["best_season"])],
            [u["entry"], str(a["entry_fee"])],
            [u["elevation"], f'{a["elevation"]} m'],
        ],
        "img": a.get("image") or "",
        "credit": (lambda c: (f'{c.get("author","")} · {c.get("license","")}' if c else ""))(
            a.get("image_credit")),
        "credit_url": (a.get("image_credit") or {}).get("source", ""),
        "body": render_md(L["body"], lang),
        "tip": render_md(L["tip"], lang),
        "route": render_md(L["route"], lang),
        "near": [[n, ATTRACTIONS[n][lang]["name"]]
                 for n in a.get("nearby", []) if n in ATTRACTIONS],
    }


EXPLORER_JS = """
<script>window.FH_EXP_BASE=%(base)s;</script>
<script defer src="%(js)s"></script>
<script defer src="/assets/weather.js"></script>
<script defer src="%(data)s"></script>
<script defer src="%(exp)s"></script>"""


def get_visit_labels(lang):
    return {
        "ka": ("ყველა ადგილი", "ნამყოფი ვარ", "არ ვარ ნამყოფი", "ნამყოფი ვარ", "ნამყოფად მონიშვნა"),
        "en": ("All places", "Visited", "Not visited", "Visited", "Mark as visited"),
        "ru": ("Все места", "Посещённые", "Не посещённые", "Посещено", "Отметить посещённым"),
        "fa": ("همه مکان‌ها", "بازدید شده", "بازدید نشده", "بازدید شده", "علامت‌گذاری به‌عنوان بازدیدشده"),
        "he": ("כל המקומות", "ביקרתי", "טרם ביקרתי", "ביקרתי", "סימון כמקום שביקרתי בו"),
        "ar": ("كل الأماكن", "تمت زيارتها", "لم تتم زيارتها", "تمت الزيارة", "وضع علامة تمت الزيارة"),
    }[lang]


def explorer_config(lang, base="/"):
    x = TRAVEL[lang]["exp"]
    u = TRAVEL[lang]["ui"]
    visited = get_visit_labels(lang)
    chunk_manifest, _ = explorer_chunks(lang)
    return {
        "pts": explorer_point_index(lang),
        "chunks": chunk_manifest,
        "towns": explorer_towns(lang),
        "lang": lang, "base": base, "center": [42.15, 43.6], "zoom": 7,
        "planner": page_url(lang, "map", False) + "#planner",
        "ui": {**{k: v for k, v in x.items()},
               "hrs": u["hrs"], "km": u["km"], "h_short": u["hrs"], "days": u["days"],
               "tip_title": u["tip_title"], "route_title": u["route_title"],
               "nearby_title": u["nearby_title"],
               "visited_yes": visited[3], "visited_mark": visited[4],
               "write_review": {"ka":"რივიუს დაწერა","en":"Write review","ru":"Написать отзыв","fa":"نوشتن نظر","he":"כתיבת ביקורת","ar":"كتابة مراجعة"}[lang],
               "review_saved": {"ka":"რივიუ შენახულია","en":"Review saved","ru":"Отзыв сохранён","fa":"نظر ذخیره شد","he":"הביקורת נשמרה","ar":"تم حفظ المراجعة"}[lang],
               "route_add": {"ka":"მარშრუტში დამატება","en":"Add to route","ru":"Добавить в маршрут","fa":"افزودن به مسیر","he":"הוספה למסלול","ar":"إضافة إلى المسار"}[lang],
               "route_remove": {"ka":"✓ მარშრუტშია","en":"✓ In route","ru":"✓ В маршруте","fa":"✓ در مسیر","he":"✓ במסלול","ar":"✓ في المسار"}[lang],
               "open_details": {"ka":"დეტალების ნახვა","en":"View details","ru":"Подробнее","fa":"مشاهده جزئیات","he":"הצגת פרטים","ar":"عرض التفاصيل"}[lang]},
    }


def explorer_block(lang, depth, height="72vh", hero=False):
    """ინტერაქტიული რუკა ძებნით, ფილტრებით, დეტალური პანელით და
       „საიდან → სად + გზად სანახავი“ ბლოკით."""
    x = TRAVEL[lang]["exp"]
    u = TRAVEL[lang]["ui"]
    base = rel_prefix(depth)
    types = sorted({a["type"] for a in ATTRACTIONS.values()},
                   key=lambda t: tl(lang, "type", t))
    topts = "".join(f'<option value="{E(t)}">{E(tl(lang,"type",t))}</option>' for t in types)
    bike_label = {"ka":"ველოგზები","en":"Cycling routes","ru":"Веломаршруты","fa":"مسیرهای دوچرخه‌سواری","he":"מסלולי אופניים","ar":"مسارات الدراجات"}[lang]
    topts += f'<option value="__cycling__">{E(bike_label)}</option>'
    ropts = "".join(f'<option value="{E(k)}">{E(r[lang]["name"])}</option>'
                    for k, r in REGIONS.items())
    visit_labels = get_visit_labels(lang)
    rating_labels = {
        "ka": ("ყველა შეფასება", "3★ და მეტი", "4★ და მეტი", "მხოლოდ 5★"),
        "en": ("All ratings", "3★ and up", "4★ and up", "5★ only"),
        "ru": ("Все оценки", "3★ и выше", "4★ и выше", "Только 5★"),
        "fa": ("همه امتیازها", "۳★ به بالا", "۴★ به بالا", "فقط ۵★"),
        "he": ("כל הדירוגים", "3★ ומעלה", "4★ ומעלה", "5★ בלבד"),
        "ar": ("كل التقييمات", "3★ فأكثر", "4★ فأكثر", "5★ فقط"),
    }[lang]
    js = EXPLORER_JS % {"js": LEAFLET_JS, "base": J(base),
                        "data": TRAVEL_ASSET[lang], "exp": ASSET["explorer"]}
    html = f'''<div class="explorer{" hero" if hero else ""}">
  <section id="selectedtour" class="selected-tour-banner" hidden aria-live="polite">
    <div><span id="selectedtourlabel"></span><strong id="selectedtourname"></strong></div>
    <dl><div><dt id="selectedtourtimelabel"></dt><dd id="selectedtourtime"></dd></div>
      <div><dt id="selectedtourcarlabel"></dt><dd id="selectedtourcar"></dd></div>
      <div><dt id="selectedtourgrouplabel"></dt><dd id="selectedtourgroup"></dd></div>
      <div><dt id="selectedtourregionlabel"></dt><dd id="selectedtourregion"></dd></div></dl>
  </section>
  <div class="expbar">
    <div class="expsearch-wrap">
      <input id="expq" class="expsearch" type="search" placeholder="{E(x["search_ph"])}"
             aria-label="{E(x["search_ph"])}" autocomplete="off">
      <div id="expqlist" class="expqlist" role="listbox"></div>
    </div>
    <select id="exptype" aria-label="{E(x["all_types"])}"><option value="">{E(x["all_types"])}</option>{topts}</select>
    <select id="exprating" aria-label="{E(rating_labels[0])}"><option value="">{E(rating_labels[0])}</option><option value="3">{E(rating_labels[1])}</option><option value="4">{E(rating_labels[2])}</option><option value="5">{E(rating_labels[3])}</option></select>
    <details class="expfilters">
      <summary>{E({"ka":"მეტი ფილტრი","en":"More filters","ru":"Ещё фильтры","fa":"فیلترهای بیشتر","he":"מסננים נוספים","ar":"مزيد من الفلاتر"}[lang])}</summary>
      <div class="expfilters-pop">
        <select id="expregion" aria-label="{E(x["all_regions"])}"><option value="">{E(x["all_regions"])}</option>{ropts}</select>
        <select id="expvisited" aria-label="{E(visit_labels[0])}"><option value="">{E(visit_labels[0])}</option><option value="yes">{E(visit_labels[1])}</option><option value="no">{E(visit_labels[2])}</option></select>
        <label class="expdate">{E(x["date"])}
          <input id="expday" type="date" aria-label="{E(x["date"])}">
        </label>
        <button id="expreset" class="btn sm ghost" type="button">{E(x["reset"])}</button>
      </div>
    </details>
    <span id="expcount" class="expcount"></span>
  </div>
  <div class="expgrid" style="--exph:{height}">
    <div class="expside">
      <div class="expfind">
        <div class="expfindrow">
          <button id="expgeo" class="btn sm ghost" type="button">◎ {E(x["my_loc"])}</button>
          <button id="expdraw" class="btn sm ghost" type="button">✎ {E(x["draw"])}</button>
          <button id="expwp" class="btn sm ghost" type="button">{E(x["wp_mode"])}</button>
        </div>
        <div class="expmodes">
          <label class="tog sm"><input type="radio" name="expmode" value="time" checked>
            <span>{E(x["by_time"])}</span></label>
          <label class="tog sm"><input type="radio" name="expmode" value="km">
            <span>{E(x["by_km"])}</span></label>
        </div>
        <div class="budget-stepper" id="expbudgetwrap">
          <button id="expbudgetminus" type="button" aria-label="−">−</button>
          <label><span class="vh" id="expbudgetlabel">{E(x["by_time"])}</span>
            <input id="expbudget" type="number" min="0.5" max="72" step="0.5" value="8" inputmode="decimal">
          </label>
          <span id="expbudgetv">{E(u["hrs"])}</span>
          <button id="expbudgetplus" type="button" aria-label="+">+</button>
        </div>
        <div id="expnear" class="expnear"></div>
      </div>
      <div class="exproutebox">
        <div class="exppair">
          <label>{E(x["from_label"])}
            <input id="expfrom" type="text" autocomplete="off" placeholder="{E(x["pick_start"])}">
            <div id="expfromlist" class="expsug"></div>
          </label>
          <button id="expswap" class="btn sm ghost" type="button" title="{E(x["swap"])}">⇅</button>
          <label>{E(x["to_label"])}
            <input id="expto" type="text" autocomplete="off" placeholder="{E(x["pick_end"])}">
            <div id="exptolist" class="expsug"></div>
          </label>
        </div>
        <label class="expslider">{E(x["detour"])} ≤ <span id="expdetourv">15 {E(u["km"])}</span>
          <input id="expdetour" type="range" min="5" max="80" step="5" value="15">
        </label>
        <div id="exproute" class="exprouteout"></div>
      </div>
    </div>
    <div class="expmapwrap">
      <div id="expmap" class="expmap"></div>
      <aside id="exppanel" class="exppanel" aria-hidden="true">
        <button id="expclose" class="expclose" type="button" aria-label="{E(x["close"])}">✕</button>
        <h3 id="exptitle"></h3>
        <div id="expbody"></div>
      </aside>
    </div>
  </div>
</div>'''
    return html, js


NOINDEX_PAGES = {"account", "trip", "card", "planner", "pricing"}


def counts_sub(s):
    """{attractions} / {regions} / {routes} — რიცხვები არასდროს ძველდება."""
    if not isinstance(s, str):
        return s
    return (s.replace("{attractions}", str(len(ATTRACTIONS)))
             .replace("{regions}", str(len(REGIONS)))
             .replace("{routes}", str(len(ROUTES)))
             .replace("{cars}", str(len(CARS))))


def render_map_page(lang):
    """დამგეგმავის ცალკე გვერდი — მთავარი გვერდი მხოლოდ landing-ია."""
    p = {k: counts_sub(v) for k, v in PAGES["map"][lang].items()}
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    mp, js = travel_workspace_block(lang, depth, "72vh", initial="planner")
    # SEO: the planner page needs a real H1 and search-intent metadata.
    pl = (SEO_TRIP_PLANNER.get("planner") or {}).get(lang) or {}
    h1 = pl.get("h1") or p["title"]
    lead = pl.get("lead") or p["desc"]
    st, sd = seo_meta("planner", lang)
    p["title"] = st or p["title"]
    p["desc"] = sd or p["desc"]
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(h1)}</h1>'
            f'<p class="lead">{E(lead)}</p></div></section>'
            f'<section class="sec wide maphero" id="planner"><div class="wrap wide">{mp}</div></section>'
            + _sec(tu(lang, "regions") or "Regions",
                   '<ul class="linklist">' + "".join(
                       f'<li><a href="{region_url(lang, k, False)}">'
                       f'{E(REGIONS[k][lang]["name"])}</a> '
                       f'<small>{sum(1 for a in ATTRACTIONS.values() if a["region"] == k)}</small></li>'
                       for k in REGIONS) + '</ul>', alt=True)
            + guide_links_block(lang, list(GUIDES)))
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": page_url(lang, "map") + "#webpage",
              "url": page_url(lang, "map"), "name": p["title"], "description": p["desc"],
              "inLanguage": lang},
             # The planner is the parent of every attraction and region page in
             # our own breadcrumbs, but it listed none of them. An ItemList of
             # the regions gives a crawler a path down from here.
             {"@type": "ItemList", "name": tu(lang, "regions") or "Regions",
              "numberOfItems": len(REGIONS), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "url": region_url(lang, k),
                   "name": REGIONS[k][lang]["name"]}
                  for i, k in enumerate(REGIONS)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map"))])]
    head = head_html(lang, "map", p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, "map"), {l: page_url(l, "map") for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def _render_map_page_legacy_redirect(lang):
    target = page_url(lang, "index", False)
    canonical = page_url(lang, "index")
    direction = "rtl" if lang in ("fa", "he", "ar") else "ltr"
    loading = {"ka":"რუკა იტვირთება…","en":"Loading the map…","ru":"Карта загружается…","fa":"در حال بارگذاری نقشه…","he":"המפה نطעה…","ar":"جارٍ تحميل الخريطة…"}[lang]
    return f'''<!doctype html><html lang="{lang}" dir="{direction}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,follow"><link rel="canonical" href="{E(canonical)}">
<meta http-equiv="refresh" content="0;url={E(target)}#explore">
<title>{E(UI[lang]["nav"]["map"])}</title><style>
html,body{{height:100%;margin:0}}body{{display:grid;place-items:center;background:#f2f6f8;color:#17313a;font:600 15px/1.5 system-ui,sans-serif}}
.load{{display:flex;align-items:center;gap:12px}}.spin{{width:22px;height:22px;border:3px solid #cbdde1;border-top-color:#078995;border-radius:50%;animation:r .7s linear infinite}}@keyframes r{{to{{transform:rotate(360deg)}}}}
</style></head><body>
<div class="load" role="status"><span class="spin"></span><span>{E(loading)}</span></div>
<script>(function(){{var h=location.hash||'#explore';location.replace({J(target)}+(location.search||'')+h);}})();</script>
</body></html>'''

    # Kept below temporarily as migration history; unreachable by design.
    p = {k: counts_sub(v) for k, v in PAGES["map"][lang].items()}
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    mp, js = travel_workspace_block(lang, depth, "68vh", initial="explore")
    regions = "".join(
        f'<div class="card"><h3><a href="{region_url(lang, k, False)}">{E(r[lang]["name"])}</a></h3>'
        f'<p>{E(r[lang]["short"])}</p>'
        f'<span class="price">{sum(1 for a in ATTRACTIONS.values() if a["region"] == k)} '
        f'{E(tu(lang,"obj"))}</span></div>'
        for k, r in REGIONS.items())
    routes = "".join(
        f'<div class="card"><span class="tag">{E(tl(lang,"difficulty",r["difficulty"]))}</span>'
        f'<h3><a href="{route_url(lang, s, False)}">{E(r[lang]["name"])}</a></h3>'
        f'<p>{E(r[lang]["short"])}</p>'
        f'<span class="price">{r["days"]} {E(tu(lang,"days"))} · {r["distance_km"]} '
        f'{E(tu(lang,"km"))} · {E(car_cat_label(r["car_category"], lang))}</span></div>'
        for s, r in ROUTES.items())
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(p["h1"])}</h1>'
        f'<p class="lead">{inline(p["lead"], lang)}</p></div></section>'
        f'<section class="sec wide"><div class="wrap wide">{mp}{legend_html(lang)}</div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"routes"))}</h2>'
        f'<div class="cards">{routes}</div></div></section>'
        f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"regions"))}</h2>'
        f'<div class="cards">{regions}</div></div></section>')
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": page_url(lang, "map") + "#webpage",
              "url": page_url(lang, "map"), "name": p["title"], "description": p["desc"],
              "inLanguage": lang, "isPartOf": {"@id": SITE_URL + "/#website"},
              "dateModified": TODAY},
             {"@type": "ItemList", "numberOfItems": len(ATTRACTIONS),
              "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                   "url": attr_url(lang, s), "name": a[lang]["name"]}
                                  for i, (s, a) in enumerate(ATTRACTIONS.items())]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map"))])]
    head = head_html(lang, "map", p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, "map"), {l: page_url(l, "map") for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def render_region(lang, key, r):
    L = r[lang]
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    sub = {s: a for s, a in ATTRACTIONS.items() if a["region"] == key}
    mp, js = map_block(lang, 420, (r["center_lat"], r["center_lon"]), r["zoom"],
                       attractions=sub, routes={})
    cards = "".join(
        f'<div class="card">'
        + (f'<a class="card-img" href="{attr_url(lang, s, False)}" tabindex="-1" aria-hidden="true">'
           f'<img src="{E(a["image"])}" alt="" loading="lazy"></a>' if a.get("image") else "")
        + f'<span class="tag">{E(tl(lang,"type",a["type"]))}</span>{stars_html(a.get("rating"), lang, True)}'
        f'<h3><a href="{attr_url(lang, s, False)}">{E(a[lang]["name"])}</a></h3>'
        f'<p>{E(a[lang]["short"])}</p><ul>'
        f'<li>{E(tu(lang,"visit_time"))}: {E(a["visit_hours"])} {E(tu(lang,"hrs"))}</li>'
        f'<li>{E(tu(lang,"from_tbilisi"))}: {a["distance_tbilisi_km"]} {E(tu(lang,"km"))} · {E(a["drive_time_tbilisi"])}</li>'
        f'<li>{E(tu(lang,"car_needed"))}: {E(car_cat_label(a["car_category"], lang))}</li>'
        f"</ul></div>" for s, a in sub.items())
    best = "".join(f"<li>{inline(x, lang)}</li>" for x in L["best_for"])
    title = f'{L["name"]} — {tu(lang, "attractions")}, {tu(lang, "routes")} | {BRAND}'
    _st, _sd = seo_meta("region", lang, name=L["name"], count=len(sub))
    if _st:
        title = _st
    desc = _sd or re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{mp}</div></section>'
        f'<section class="sec alt"><div class="wrap"><div class="article">{render_md(L["body"], lang)}</div>'
        f'<h2>{E(tu(lang,"best_for"))}</h2><ul>{best}</ul></div></section>'
        f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"driving_title"))}</h2>'
        f'<div class="article">{render_md(L["driving"], lang)}</div></div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"in_region"))} — '
        f'{len(sub)} {E(tu(lang,"obj"))}</h2><div class="cards">{cards}</div></div></section>'
        f'<section class="sec"><div class="wrap"><div class="cta">'
        f'<h2>{E(u["ui"]["book_title"])}</h2><p>{E(TRIP_CTA_TEXT[lang])}</p>'
        f'<div class="row">{booking_open_btn(lang)}'
        f'<a class="btn ghost" href="{page_url(lang,"fleet",False)}">{E(u["nav"]["fleet"])}</a>'
        f'<a class="btn ghost" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
        f'</div></div></div></section>')
    graph = [org_node(lang), website_node(lang),
             {"@type": "TouristDestination", "@id": region_url(lang, key) + "#dest",
              "name": L["name"], "description": L["short"], "url": region_url(lang, key),
              "geo": {"@type": "GeoCoordinates", "latitude": r["center_lat"],
                      "longitude": r["center_lon"]},
              "containedInPlace": {"@type": "Country", "name": META[lang]["country"]},
              "includesAttraction": [{"@type": "TouristAttraction", "name": a[lang]["name"],
                                      "url": attr_url(lang, s)} for s, a in sub.items()]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map")),
                                (L["name"], region_url(lang, key))])]
    head = head_html(lang, "map", title, desc,
                     f'{L["name"]}, {tu(lang,"attractions")}, {tu(lang,"routes")}',
                     region_url(lang, key), {l: region_url(l, key) for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], page_url(lang, "map", False)),
                                (L["name"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def cheapest_price(cat):
    """იმ კატეგორიის ყველაზე იაფი ავტომობილის დღიური ტარიფი."""
    m = {"economy": "economy", "suv": "suv", "offroad": "offroad"}.get(cat, "economy")
    ps = [int(c["price_1_6"]) for c in CARS.values() if c["category"] == m]
    if not ps:
        ps = [int(c["price_1_6"]) for c in CARS.values()]
    return min(ps) if ps else 0


def wa_link(lang, text=""):
    import urllib.parse as _u
    # One number is enough: fall back to the main phone when no separate
    # mobile is configured, so the WhatsApp handoff never silently dies.
    num = (SITE.get("whatsapp") or SITE.get("mobile_e164")
           or SITE.get("phone_e164", "")).lstrip("+")
    msg = text or UI[lang]["ui"].get("wa_msg", "")
    return f'https://wa.me/{num}?text={_u.quote(msg)}'


def rent_box(lang, a):
    """გვერდითი ბარათი — „დაიქირავე მანქანა ამ მოგზაურობისთვის“."""
    r = TRAVEL[lang]["rent"]
    cat = car_cat_label(a["car_category"], lang)
    road = tl(lang, "road", a["road"]).lower()
    day = cheapest_price(a["car_category"])
    km = float(a["distance_tbilisi_km"]) * 2
    lit = float(SITE.get("fuel_l_100km", 8.5))
    gel = float(SITE.get("fuel_price_gel", 3.1))
    fuel = int(round(km * lit / 100.0 * gel / 5.0) * 5)
    return (
        f'<aside class="rentbox">'
        f'<h3>{E(r["title"])}</h3>'
        f'<p>{E(r["text"].format(cat=cat, road=road))}</p>'
        f'<div class="rentrow"><span>{E(r["per_day"].format(cat=cat))}</span>'
        f'<b>{E(r["from"])} {day} ₾</b></div>'
        f'<div class="rentrow"><span>{E(r["fuel"])}</span>'
        f'<b>{E(r["approx"])}{fuel} ₾</b></div>'
        f'<a class="btn" dir="ltr" href="tel:{SITE["phone_e164"]}">{E(SITE["phone"])}</a>'
        f'<a class="btn wa" href="{wa_link(lang, UI[lang]["ui"]["wa_msg"] + " — " + a[lang]["name"])}" '
        f'rel="noopener" target="_blank">{E(UI[lang]["ui"]["wa_btn"])}</a>'
        f'<p class="rentnote">{E(r["note"].format(o=SITE["opens"], c=SITE["closes"]))}</p>'
        f'<p class="rentnote">{E(r["est"].format(l=lit, g=gel))}</p>'
        f'</aside>')


def render_attraction(lang, slug, a):
    L = a[lang]
    u = UI[lang]
    r = REGIONS[a["region"]]
    depth = 2 if lang == ROOT_LANG else 3
    mp, js = map_block(lang, 360, (a["lat"], a["lon"]), 12,
                       attractions={slug: a}, routes={})
    near = "".join(
        f'<div class="card">'
        + (f'<a class="card-img" href="{attr_url(lang, n, False)}" tabindex="-1" aria-hidden="true">'
           f'<img src="{E(ATTRACTIONS[n]["image"])}" alt="" loading="lazy"></a>'
           if ATTRACTIONS[n].get("image") else "")
        + f'<span class="tag">{E(tl(lang,"type",ATTRACTIONS[n]["type"]))}</span>'
        f'<h3><a href="{attr_url(lang, n, False)}">{E(ATTRACTIONS[n][lang]["name"])}</a></h3>'
        f'<p>{E(ATTRACTIONS[n][lang]["short"])}</p></div>'
        for n in a.get("nearby", []) if n in ATTRACTIONS)
    badge = (f'<span class="tag">{E(tl(lang,"type",a["type"]))}</span>'
             f'<span class="tag muted">{E(r[lang]["name"])}</span>'
             + (f'<span class="tag muted">{E(tu(lang,"unesco"))}</span>' if a["unesco"] else ""))
    title = f'{L["name"]} — {tl(lang, "type", a["type"])}, {a["drive_time_tbilisi"]} {tu(lang,"from_tbilisi")}'
    _st, _sd = seo_meta("attraction", lang, type=a.get("type", ""), name=L["name"],
                        region=r[lang]["name"], drive=a.get("drive_time_tbilisi", ""),
                        km=a.get("distance_tbilisi_km", ""))
    title = title[:70] + f" | {BRAND}" if len(title) < 55 else title[:74]
    if _st:
        title = _st
    desc = re.sub(r"\s+", " ", f'{L["short"]} {tu(lang,"visit_time")}: {a["visit_hours"]} '
                               f'{tu(lang,"hrs")}. {tu(lang,"from_tbilisi")} '
                               f'{a["distance_tbilisi_km"]} {tu(lang,"km")}, '
                               f'{a["drive_time_tbilisi"]}. {L["body"]}')[:158].rsplit(" ", 1)[0]
    body = (
        f'<section class="page-head"><div class="wrap"><div class="tagrow">{badge}'
        f'{stars_html(a.get("rating"), lang)}</div>'
        f'<h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{photo_html(a, lang, "photo hero-photo", True)}'
        f'{attr_facts(a, lang)}'
        f'<div class="attr-grid"><div class="article">{render_md(L["body"], lang)}'
        f'{gallery_html(a, lang)}</div>'
        f'{rent_box(lang, a)}</div></div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"tip_title"))}</h2>'
        f'<div class="note">{render_md(L["tip"], lang)}</div>'
        f'<h2>{E(tu(lang,"route_title"))}</h2>'
        f'<div class="article">{render_md(L["route"], lang)}</div>{mp}</div></section>'
        + (f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"nearby_title"))}</h2>'
           f'<div class="cards">{near}</div></div></section>' if near else "")
        + attraction_links_block(lang, slug, a)
        + f'<section class="sec alt"><div class="wrap"><div class="cta">'
          f'<h2>{E(u["ui"]["book_title"])}</h2><p>{E(TRIP_CTA_TEXT[lang])}</p>'
          f'<div class="row">{booking_open_btn(lang)}'
          f'<a class="btn ghost" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
          f'<a class="btn ghost" href="{page_url(lang,"fleet",False)}">{E(u["nav"]["fleet"])}</a>'
          f'<a class="btn ghost" href="{region_url(lang, a["region"], False)}">{E(r[lang]["name"])}</a>'
          f"</div></div></div></section>")
    if _sd:
        desc = _sd
    graph = [org_node(lang), website_node(lang),
             {"@type": "TouristAttraction", "@id": attr_url(lang, slug) + "#attraction",
              "name": L["name"], "description": L["short"], "url": attr_url(lang, slug),
              **({"image": abs_url(a["image"])} if a.get("image") else {}),
              "geo": {"@type": "GeoCoordinates", "latitude": a["lat"], "longitude": a["lon"],
                      "elevation": a["elevation"]},
              "address": {"@type": "PostalAddress", "addressRegion": r[lang]["name"],
                          "addressCountry": "GE"},
              "isAccessibleForFree": a["entry_fee"] in ("free", "უფასო", "Бесплатно"),
              "touristType": tl(lang, "type", a["type"]),
              # Road surface, required vehicle class, drive time and season are
              # the fields no competitor publishes. Machine-readable here, and
              # rendered visibly by attr_facts() on the same page.
              "additionalProperty": [
                  {"@type": "PropertyValue", "name": su("road_surface", lang) or "Road surface",
                   "value": su("road", lang, a.get("road", "paved")) or a.get("road", "")},
                  {"@type": "PropertyValue", "name": su("car_needed", lang) or tu(lang, "car_needed"),
                   "value": car_cat_label(a.get("car_category", "economy"), lang)},
                  {"@type": "PropertyValue", "name": tu(lang, "from_tbilisi"),
                   "value": f'{a["distance_tbilisi_km"]} km, {a["drive_time_tbilisi"]}'},
                  {"@type": "PropertyValue", "name": su("best_season", lang) or tu(lang, "season"),
                   "value": su("season", lang, a.get("best_season", "all")) or a.get("best_season", "")},
                  {"@type": "PropertyValue", "name": tu(lang, "visit_time"),
                   "value": f'{a["visit_hours"]} {tu(lang, "hrs")}'},
              ],
              "containedInPlace": {"@type": "TouristDestination", "name": r[lang]["name"],
                                   "url": region_url(lang, a["region"])}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map")),
                                (r[lang]["name"], region_url(lang, a["region"])),
                                (L["name"], attr_url(lang, slug))])]
    _imgs = [image_object(a.get("image"), a.get("image_credit"), L["name"])]
    _imgs += [image_object(x.get("image"), x, L["name"]) for x in (a.get("gallery") or [])]
    graph += [i for i in _imgs if i]
    head = head_html(lang, "map", title, desc,
                     f'{L["name"]}, {tl(lang,"type",a["type"])}, {r[lang]["name"]}',
                     attr_url(lang, slug), {l: attr_url(l, slug) for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True,
                     image=abs_url(a.get("image")))
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], page_url(lang, "map", False)),
                                (r[lang]["name"], region_url(lang, a["region"], False)),
                                (L["name"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def render_route(lang, slug, r):
    L = r[lang]
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    wp = {s: ATTRACTIONS[s] for s in r["waypoints"] if s in ATTRACTIONS}
    mp, js = map_block(lang, 460, (42.15, 43.9), 8, attractions=wp, routes={slug: r})
    facts = [
        {"k": tu(lang, "days"), "v": f'{r["days"]} / {r["nights"]} {tu(lang, "nights")}'},
        {"k": tu(lang, "total_km"), "v": f'{r["distance_km"]} {tu(lang, "km")}'},
        {"k": tu(lang, "total_drive"), "v": r["drive_time_total"]},
        {"k": tu(lang, "car_needed"), "v": car_cat_label(r["car_category"], lang)},
        {"k": tu(lang, "season"), "v": tl(lang, "season", r["best_season"])},
        {"k": tu(lang, "difficulty"), "v": tl(lang, "difficulty", r["difficulty"])},
    ]
    fh = ('<dl class="facts">' + "".join(
        f'<div><dt class="k">{E(x["k"])}</dt><dd class="v">{E(x["v"])}</dd></div>'
        for x in facts) + "</dl>")
    stops = "".join(
        f'<div class="card stop-card">'
        + (f'<a class="stop-img" href="{attr_url(lang, s, False)}" tabindex="-1" aria-hidden="true">'
           f'<img src="{E(a["image"])}" alt="" loading="lazy"></a>' if a.get("image") else "")
        + f'<span class="tag">{E(tl(lang,"type",a["type"]))}</span>'
        f'<h3><a href="{attr_url(lang, s, False)}">{E(a[lang]["name"])}</a></h3>'
        f'<p>{E(a[lang]["short"])}</p>'
        f'<span class="price">{E(a["visit_hours"])} {E(tu(lang,"hrs"))}</span></div>'
        for s, a in wp.items())
    tips = "".join(f"<li>{inline(x, lang)}</li>" for x in L["tips"])
    title = f'{L["name"]} — {r["days"]} {tu(lang,"days")}, {r["distance_km"]} {tu(lang,"km")} | {BRAND}'
    _st, _sd = seo_meta("route", lang, purpose=r.get("purpose", ""), name=L["name"],
                        days=r.get("days", ""), km=r.get("distance_km", ""),
                        drive=r.get("drive_time_total", ""),
                        car=car_cat_label(r.get("car_category", "economy"), lang))
    if _st:
        title = _st
    desc = _sd or re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{fh}'
        f'<div class="row" style="margin:4px 0 14px">'
        f'<a class="btn" href="{page_url(lang, "map", False)}#tour={slug}">{E(TOURS_UI[lang][7])}</a></div>{mp}'
        f'<div class="article">{render_md(L["body"], lang)}</div></div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"plan_title"))}</h2>'
        f'<div class="article">{render_md(L["plan"], lang)}</div></div></section>'
        f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"waypoints_title"))}</h2>'
        f'<div class="cards">{stops}</div>'
        f'<h2>{E(tu(lang,"tips_title"))}</h2><ul>{tips}</ul></div></section>'
        + route_links_block(lang, slug, r)
        + f'<section class="sec"><div class="wrap">'
        f'<div class="cta"><h2>{E(u["ui"]["book_title"])}</h2>'
        f'<p>{E(TRIP_CTA_TEXT[lang])}</p><div class="row">'
        f'{booking_open_btn(lang)}'
        f'<a class="btn ghost" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
        f'<a class="btn ghost" href="{page_url(lang,"fleet",False)}">{E(u["nav"]["fleet"])}</a>'
        f'<a class="btn ghost" href="{page_url(lang,"map",False)}">{E(u["nav"]["map"])}</a>'
        f"</div></div></div></section>")
    graph = [org_node(lang), website_node(lang),
             {"@type": "TouristTrip", "@id": route_url(lang, slug) + "#trip",
              "name": L["name"], "description": L["short"], "url": route_url(lang, slug),
              "touristType": tl(lang, "difficulty", r["difficulty"]),
              "provider": {"@id": SITE_URL + "/#organization"},
              "itinerary": {"@type": "ItemList", "numberOfItems": len(wp),
                            "itemListElement": [
                                {"@type": "ListItem", "position": i + 1,
                                 "item": {"@type": "TouristAttraction", "name": a[lang]["name"],
                                          "url": attr_url(lang, s)}}
                                for i, (s, a) in enumerate(wp.items())]}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map")),
                                (L["name"], route_url(lang, slug))])]
    head = head_html(lang, "map", title, desc,
                     f'{L["name"]}, {tu(lang,"routes")}, {META[lang]["country"]}',
                     route_url(lang, slug), {l: route_url(l, slug) for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], page_url(lang, "map", False)),
                                (L["name"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


# ══════════════════════════════════════════════════════════════ ტურის დამგეგმავი
PLANNER = load("content/settings/planner.yml")
TB_LAT, TB_LON = 41.7151, 44.8271
AIRPORTS = [(41.6692, 44.9547), (42.1783, 42.4826), (41.6103, 41.5997)]  # TBS, KUT, BUS


def _hav(lat1, lon1, lat2, lon2):
    import math
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = (math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def road_model(a):
    """f — გზის კლაკნილობა, v — საშუალო სიჩქარე. აღებულია თბილისიდან
    რეალური მანძილისა და დროის შეფარდებით, ანუ რელიეფი ჩაშენებულია."""
    d = _hav(TB_LAT, TB_LON, a["lat"], a["lon"])
    km = float(a["distance_tbilisi_km"])
    hh, mm = str(a["drive_time_tbilisi"]).split(":")
    minutes = int(hh) * 60 + int(mm)
    if d < 6 or minutes <= 0:
        return 1.5, 26.0
    f = min(2.9, max(1.15, km / d))
    v = min(80.0, max(18.0, km / (minutes / 60.0)))
    return round(f, 3), round(v, 1)


# ავტომობილის შერჩევის რიგი: რაც უფრო მაღალია, მით უფრო „უხეშ“ გზას უძლებს
ROAD_RANK = {"paved": 0, "mostly_paved": 1, "gravel": 2, "4x4_only": 3}
CAT_RANK = {"economy": 0, "business": 0, "minivan": 1, "van": 1, "suv": 2, "offroad": 3}


def fleet_for_planner(lang):
    """მანქანების მსუბუქი სია — დამგეგმავი აქედან ირჩევს."""
    out = []
    for s, c in CARS.items():
        if not c.get("available", True):
            continue
        out.append({
            "s": s, "n": c[lang]["name"], "cat": c["category"],
            "rank": CAT_RANK.get(c["category"], 1),
            "seats": int(str(c["seats"]).split("-")[0].split("+")[0] or 5),
            "price": int(c["price_1_6"]), "price7": int(c["price_7_29"]),
            "priceUsd": gel_to_usd(c["price_1_6"]),
            "price7Usd": gel_to_usd(c["price_7_29"]),
            "fuel": str(c.get("fuel_100km", "")),
            "cl": int(c.get("clearance") or 150),
            "img": c.get("image") or "",
            "u": car_url(lang, s, False),
            "cat_n": cat_label(c["category"], lang),
        })
    out.sort(key=lambda x: (x["rank"], x["price"]))
    return out


def planner_data(lang):
    P = PLANNER[lang]
    tour_ui = {
        "ka": {"day": "დღე", "people": "ადამიანი", "view": "მინდა", "region": "რეგიონი", "car": "ავტომობილი", "time": "ხანგრძლივობა", "group": "რეკომენდებული ჯგუფი", "chosen": "არჩეული სტანდარტული ტური"},
        "en": {"day": "days", "people": "people", "view": "Choose", "region": "Region", "car": "Vehicle", "time": "Duration", "group": "Recommended group", "chosen": "Selected standard tour"},
        "ru": {"day": "дн.", "people": "чел.", "view": "Выбрать", "region": "Регион", "car": "Автомобиль", "time": "Длительность", "group": "Рекомендуемая группа", "chosen": "Выбранный стандартный тур"},
        "fa": {"day": "روز", "people": "نفر", "view": "انتخاب", "region": "منطقه", "car": "خودرو", "time": "مدت", "group": "گروه پیشنهادی", "chosen": "تور استاندارد انتخاب‌شده"},
        "he": {"day": "ימים", "people": "אנשים", "view": "בחירה", "region": "אזור", "car": "רכב", "time": "משך", "group": "קבוצה מומלצת", "chosen": "טיול סטנדרטי שנבחר"},
        "ar": {"day": "أيام", "people": "أشخاص", "view": "اختيار", "region": "المنطقة", "car": "المركبة", "time": "المدة", "group": "المجموعة المقترحة", "chosen": "الجولة القياسية المختارة"},
    }[lang]
    purpose_by_route = {
        "kakheti-wine-loop": "culinary", "imereti-caves-canyons": "nature",
        "black-sea-adjara": "beach", "military-highway-kazbegi": "mountains",
        "vardzia-borjomi-south": "culture", "svaneti-expedition": "mountains",
        "racha-mountain-loop": "nature",
    }
    car_names = {
        "ka": {"standard": "სტანდარტული", "4x4": "4X4"}, "en": {"standard": "Standard", "4x4": "4X4"},
        "ru": {"standard": "Стандарт", "4x4": "4X4"}, "fa": {"standard": "استاندارد", "4x4": "4X4"},
        "he": {"standard": "רגיל", "4x4": "4X4"}, "ar": {"standard": "قياسية", "4x4": "4X4"},
    }[lang]
    def route_origin(route):
        origin = route.get("origin")
        if not isinstance(origin, dict):
            return None
        try:
            lat = float(origin["lat"])
            lon = float(origin["lon"])
        except (KeyError, TypeError, ValueError):
            return None
        return {
            "n": origin.get(f"name_{lang}") or origin.get("name_en") or origin.get("name_ka") or origin.get(lang) or origin.get("en") or origin.get("ka") or "",
            "la": lat, "lo": lon,
            "f": float(origin.get("road_factor", 1.4)),
            "v": float(origin.get("speed_kmh", 55)),
        }

    standard_tours = [{
        "s": slug, "n": route[lang]["name"], "sh": route[lang]["short"],
        "days": int(route["days"]), "nights": int(route["nights"]), "km": int(route["distance_km"]),
        "season": route["best_season"], "purpose": route.get("purpose", purpose_by_route.get(slug, "classic")),
        "drive": route.get("drive_time_total", ""),
        "dailyHours": float(route.get("daily_hours", 8)),
        "origin": route_origin(route),
        "car": "4x4" if route.get("car_category") in ("suv", "offroad") else "standard",
        "carLabel": car_names["4x4" if route.get("car_category") in ("suv", "offroad") else "standard"],
        "region": ", ".join(dict.fromkeys(REGIONS[ATTRACTIONS[w]["region"]][lang]["name"] for w in route.get("waypoints", []) if w in ATTRACTIONS)),
        "minPeople": int(route.get("min_people", 1)), "maxPeople": int(route.get("max_people", 8)),
        "availableFrom": route.get("available_from", ""), "availableTo": route.get("available_to", ""),
        "img": route.get("image") or next(
            (ATTRACTIONS[w]["image"] for w in route.get("waypoints", [])
             if w in ATTRACTIONS and ATTRACTIONS[w].get("image")), ""),
        "u": route_url(lang, slug, False),
        "wp": route.get("waypoints", []),
    } for slug, route in ROUTES.items()]
    items = []
    for s, a in ATTRACTIONS.items():
        f, v = road_model(a)
        items.append({
            "s": s, "n": a[lang]["name"], "sh": a[lang]["short"],
            "lat": a["lat"], "lon": a["lon"], "r": a["region"], "ty": a["type"],
            "h": float(a["visit_hours"]), "car": a["car_category"],
            "season": a["best_season"], "yearRound": bool(a.get("open_year_round", False)), "f": f, "v": v,
            "u": attr_url(lang, s, False), "fe": bool(a["featured"]), "un": bool(a["unesco"]),
            "c": "",
            "img": a.get("image") or "", "road": a["road"],
            "rd": ROAD_RANK_NUM.get(a["road"], 0), "el": a.get("elevation") or 0,
            # Localised type label and rating, so an itinerary row can carry the
            # same facts as a map list card. "r" is already the region here.
            "tl": tl(lang, "type", a["type"]), "rt": a.get("rating") or 0,
        })
    towns = [i for i in items if i["ty"] == "town"]
    starts = [{"s": "tbilisi", "n": P["starts"][0], "lat": TB_LAT, "lon": TB_LON, "f": 1.4, "v": 55}]
    for i, (la, lo) in enumerate(AIRPORTS):
        starts.append({"s": ("tbilisi-airport", "kutaisi-airport", "batumi-airport")[i], "n": P["starts"][i + 1], "lat": la, "lon": lo, "f": 1.4, "v": 60})
    for t in towns:
        starts.append({"s": t["s"], "n": t["n"], "lat": t["lat"], "lon": t["lon"], "f": t["f"], "v": t["v"]})
    return {
        "a": items,
        "regions": [{"k": k, "n": r[lang]["name"]} for k, r in REGIONS.items()],
        "types": [{"k": t, "n": tl(lang, "type", t)}
                  for t in sorted({a["type"] for a in ATTRACTIONS.values()})],
        "car": {c: cat_label(c, lang) for c in ("economy", "suv", "offroad")},
        "styles": P.get("styles", []),
        "standardTours": standard_tours,
        "tourUi": tour_ui,
        "hotels": HOTELS,
        "towns": [{"k": p["key"], "n": p[lang], "lat": p["lat"], "lon": p["lon"]}
                  for p in PLACES if p["kind"] == "city"],
        "roadLegs": ROAD_LEGS,
        "htowns": [{"k": p["key"], "la": p["lat"], "lo": p["lon"]}
                   for p in PLACES if p["kind"] == "city"],
        "roads": {k: tl(lang, "road", k) for k in ("paved", "mostly_paved", "gravel", "4x4_only")},
        "fleet": fleet_for_planner(lang),
        "maps": {
            "provider": MAPS.get("provider", "osrm"),
            "tomtomKey": MAPS.get("tomtom_api_key", ""),
            "traffic": bool(MAPS.get("traffic_enabled", False)),
            "routing": bool(MAPS.get("routing_enabled", True)),
            "trafficOpacity": float(MAPS.get("traffic_opacity", 0.82)),
            "fallback": MAPS.get("fallback_provider", "osrm"),
        },
        "brand": {"site": SITE_URL, "phone": SITE["phone"],
                  "slogan": "You Drive. We handle the rest."},
        "starts": starts,
        "t": P["ui"],
        "nav": {"contact": UI[lang]["nav"]["contact"], "fleet": UI[lang]["nav"]["fleet"]},
        "url": {"contact": page_url(lang, "contact", False), "fleet": page_url(lang, "fleet", False)},
    }


def workspace_planner_data(lang):
    """Planner metadata used by the unified map workspace.

    Attraction geometry already arrives through EXP's lightweight point index,
    so sending planner_data.a here duplicated the complete catalogue in every
    language asset without a single workspace.js consumer.
    """
    data = planner_data(lang)
    data.pop("a", None)
    return data


def planner_form_html(lang):
    P = PLANNER[lang]
    u, t = UI[lang], P["ui"]
    labels = {
        "ka": ("პერიოდი", "დან", "მდე", "ტურის ტიპი", "სტანდარტული ტურები"),
        "en": ("Travel period", "From", "To", "Tour type", "Standard tours"),
        "ru": ("Период", "С", "До", "Тип тура", "Стандартные туры"),
        "fa": ("بازه سفر", "از", "تا", "نوع تور", "تورهای استاندارد"),
        "he": ("תקופת הנסיעה", "מתאריך", "עד תאריך", "סוג הטיול", "טיולים מוכנים"),
        "ar": ("فترة السفر", "من", "إلى", "نوع الجولة", "جولات جاهزة"),
    }[lang]
    geo_labels = {
        "ka": ("ჩემი მდებარეობა", "მდებარეობას ვადგენთ…", "მდებარეობა ვერ განისაზღვრა"),
        "en": ("My location", "Locating…", "Location could not be determined"),
        "ru": ("Моё местоположение", "Определяем…", "Не удалось определить местоположение"),
        "fa": ("موقعیت من", "در حال یافتن…", "موقعیت پیدا نشد"),
        "he": ("המיקום שלי", "מאתר…", "לא ניתן לאתר את המיקום"),
        "ar": ("موقعي", "جارٍ تحديد الموقع…", "تعذر تحديد الموقع"),
    }[lang]
    purpose_names = {
        "ka": ("კლასიკური", "კულინარიული", "ღვინის", "კულტურული", "ბუნება", "ველო", "მთები", "ჰაიქინგი", "ისტორიული", "ზღვა", "ოჯახური", "თეატრი და სპექტაკლი"),
        "en": ("Classic", "Culinary", "Wine", "Culture", "Nature", "Cycling", "Mountains", "Hiking", "History", "Beach", "Family", "Theatre & performance"),
        "ru": ("Классический", "Кулинарный", "Винный", "Культурный", "Природа", "Велотур", "Горы", "Хайкинг", "Исторический", "Море", "Семейный", "Театр и спектакль"),
        "fa": ("کلاسیک", "آشپزی", "شراب", "فرهنگی", "طبیعت", "دوچرخه‌سواری", "کوهستان", "پیاده‌روی", "تاریخی", "ساحل", "خانوادگی", "تئاتر و اجرا"),
        "he": ("קלאסי", "קולינרי", "יין", "תרבות", "טבע", "אופניים", "הרים", "הליכה", "היסטורי", "חוף", "משפחתי", "תיאטרון ומופע"),
        "ar": ("كلاسيكية", "الطهي", "النبيذ", "ثقافية", "الطبيعة", "الدراجات", "الجبال", "المشي", "تاريخية", "الشاطئ", "عائلية", "مسرح وعروض"),
    }[lang]
    purpose_keys = ("classic", "culinary", "wine", "culture", "nature", "cycling", "mountains", "hiking", "history", "beach", "family", "performance")
    purposes = list(zip(purpose_keys, purpose_names))

    def opt_pace():
        return "".join(
            f'<option value="{v}"{" selected" if v == 480 else ""}>{E(lbl)}</option>'
            for v, lbl in ((360, t["pace_easy"]), (480, t["pace_normal"]), (600, t["pace_full"])))

    form = f"""<div class="pform planner-toolbar">
<div class="pf start-field"><label for="startsearch">{E(t['start'])}</label>
<div class="start-input-row"><input id="startsearch" type="search" list="startoptions" autocomplete="off"
  role="combobox" aria-autocomplete="list" aria-controls="startoptions">
<button type="button" id="startgeo" class="start-geo" data-label="{E(geo_labels[0])}"
 data-loading="{E(geo_labels[1])}" data-error="{E(geo_labels[2])}">⌖ <span>{E(geo_labels[0])}</span></button></div>
<datalist id="startoptions"></datalist><select id="start" hidden aria-hidden="true" tabindex="-1"></select></div>
<div class="pf period-field"><label>{E(labels[0])}</label><div class="date-pair"><input id="datefrom" type="date" aria-label="{E(labels[1])}"><input id="dateto" type="date" aria-label="{E(labels[2])}"></div></div>
<div class="pf days-field"><label for="days">{E(t['days'])}</label><div class="days-stepper">
<button id="daysminus" type="button" aria-label="−">−</button>
<input id="days" type="number" min="1" max="30" step="1" value="3" inputmode="numeric">
<button id="daysplus" type="button" aria-label="+">+</button></div><small class="days-help">1–30</small></div>
<div class="pf derived-month"><label for="month">{E(t['month'])}</label><select id="month"></select></div>
<div class="pf party-field"><label for="party">{E(t['party'])}</label><div class="party-stepper">
<button id="partyminus" type="button" aria-label="−">−</button>
<input id="party" type="number" min="1" max="8" step="1" value="2" inputmode="numeric">
<button id="partyplus" type="button" aria-label="+">+</button></div><small class="party-help">1–8</small></div>
<div class="pf tour-purpose-field"><label for="tourpurpose">{E(labels[3])}</label><select id="tourpurpose">{"".join(f'<option value="{k}">{E(v)}</option>' for k,v in purposes)}</select></div>
<div class="pf pf-wide carmode">
<label class="tog"><input type="radio" name="carmode" id="carauto" value="auto" checked>
<span>{E(t['car_auto'])}</span></label>
<label class="tog"><input type="radio" name="carmode" id="carown" value="own">
<span>{E(t['own_car'])}</span></label>
<label class="tog"><input type="radio" name="carmode" id="carpick" value="pick">
<span>{E(t['car_pick'])}</span></label>
<label class="tog"><input type="radio" name="carmode" id="cardriver" value="driver">
<span>{E({'ka':'მძღოლით','en':'With driver','ru':'С водителем','fa':'با راننده','he':'עם נהג','ar':'مع سائق'}[lang])}</span></label>
<select id="car" hidden>
<option value="economy">{E(cat_label('economy', lang))}</option>
<option value="suv" selected>{E(cat_label('suv', lang))}</option>
<option value="offroad">{E(cat_label('offroad', lang))}</option>
</select></div>
<div class="pf secondary-planner-field"><label for="pace">{E(t['pace'])}</label><select id="pace">{opt_pace()}</select></div>
<div class="pf secondary-planner-field"><label for="hbudget">{E(t['stay'])} · {E(t['budget'])}</label><select id="hbudget">
<option value="">—</option><option value="low">{E(t['b_low'])}</option>
<option value="mid" selected>{E(t['b_mid'])}</option><option value="high">{E(t['b_high'])}</option>
</select></div>
<div class="pf pf-check"><label><input type="checkbox" id="back" checked> {E(t['return'])}</label></div>
<details class="planner-more pf-wide"><summary>{E(t['style'])} · {E(t['regions'])} · {E(t['interests'])}</summary><div class="planner-more-in">
<div class="pf pf-wide"><label>{E(t['style'])}</label><div id="styles" class="chips styles"></div></div>
<div class="pf pf-wide"><label>{E(t['regions'])} <span id="regions-count" class="cnt"></span>
<small>{E(t['all_regions'])}</small></label><div id="regions" class="chips"></div></div>
<div class="pf pf-wide"><label>{E(t['interests'])} <span id="interests-count" class="cnt"></span>
<small>{E(t['all_interests'])}</small></label><div id="interests" class="chips"></div></div></div></details>
<div class="pf pf-wide prow">
<button type="button" class="btn" id="build">{E(t['build'])}</button>
<button type="button" class="btn ghost" id="reset">{E(t['reset'])}</button></div>
<div class="standard-modal" id="standardmodal" hidden><div class="standard-dialog" role="dialog" aria-modal="true" aria-labelledby="standardtitle">
<button type="button" class="standard-close" id="standardclose" aria-label="Close">&#10005;</button>
<div class="standard-dialog-head"><h3 id="standardtitle">{E(labels[4])}</h3><label for="tourpurposemodal">{E(labels[3])}</label><select id="tourpurposemodal">{"".join(f'<option value="{k}">{E(v)}</option>' for k,v in purposes)}</select></div>
<div id="standardtours" class="standard-grid"></div></div></div>
</div>"""

    return form


DOW_UI = {
    "ka": dict(h1="დაგეგმე მოგზაურობა საქართველოში", lead="აირჩიე ადგილები რუკაზე, დაითვალე დრო დღეების მიხედვით და გააზიარე მარშრუტი. მანქანა, ქირაობა ან მძღოლი ბოლოს ემატება.", plan="დაგეგმე მოგზაურობა", tours="სტანდარტული ტურები", origin="საწყისი ადგილი", origin_ph="ქალაქი ან ადგილი", myLoc="ჩემი მდებარეობა", start="დაწყება", end="დასრულება", days="რამდენი დღე", people="რამდენი ხართ", transport="ტრანსპორტი", t_suggest="შემომთავაზეთ მანქანა", t_own="ჩემი მანქანით ვარ", t_rent="მანქანის ქირაობა მინდა", t_driver="მძღოლი მჭირდება", dayTime="დღიური დრო", byDay="დღეების მიხედვით", chosen="არჩეული დრო", used="გამოყენებული", left="დარჩენილი", save="მარშრუტის შენახვა", share="გაზიარება", searchPlace="ადგილის ძებნა", allCats="ყველა კატეგორია", allRegs="ყველა რეგიონი", tabPlaces="ადგილები", tabMap="რუკა", tabRoute="მარშრუტი", traffic="ტრაფიკი", weather="ამინდი", book="მანქანის დაჯავშნა", legend_sel="არჩეული", legend_ok="ხელმისაწვდომი", legend_nofit="დროში არ ეტევა", legend_vis="ნამყოფი", loadingRoute="მარშრუტი იგება…", routeErr="გზის სერვისი მიუწვდომელია — ნაჩვენებია სავარაუდო ხაზი", emptyT="ფილტრებს ადგილი არ ემთხვევა", emptyS="გაზარდეთ დღიური დრო ან მოხსენით ფილტრი.", clearF="ფილტრების გასუფთავება", noStops="მარშრუტი ცარიელია — აირჩიეთ ადგილები სიიდან ან სტანდარტული ტური.", tourSearch="ტურის ძებნა", f_dur="ხანგრძლივობა", f_type="ტიპი", f_season="სეზონი", f_car="ავტომობილი", noTours="ამ ფილტრით ტური არ არის", offF="ფილტრის მოხსნა", bTitle="მანქანის დაჯავშნა", bName="სახელი", bPhone="ტელეფონი", bInvalid="შეავსეთ სახელი და ტელეფონი", bSend="მოთხოვნის გაგზავნა", bDoneT="მოთხოვნა გაიგზავნა", bookCar="დაჯავშნე მანქანა", ret_back="↩ ვბრუნდები საწყის წერტილში", ret_last="ვრჩები ბოლო გაჩერებაზე", ret_other="ვრჩები სხვაგან…", stay_ph="სად რჩებით?", reassure="წინასწარი გადახდა არ არის · ოპერატორი მალე დაგირეკავთ", sendErr="ვერ გაიგზავნა — სცადეთ თავიდან ან მოგვწერეთ WhatsApp-ზე", waBtn="WhatsApp-ით მოწერა", phoneHint="მაგ. 5XX 12 34 56", meterHint="მონიშნე ადგილები სიაში — დრო ავტომატურად დაითვლება", plusDay="+1 დღე"),
    "en": dict(h1="Plan a trip in Georgia", lead="Pick places on the map, count the time day by day and share the route. A car, a rental or a driver comes last.", plan="Plan a trip", tours="Standard tours", origin="Starting point", origin_ph="City or place", myLoc="My location", start="From", end="To", days="How many days", people="How many of you", transport="Transport", t_suggest="Suggest me a car", t_own="I have my own car", t_rent="I want to rent a car", t_driver="I need a driver", dayTime="Hours per day", byDay="Per day", chosen="Budget", used="Used", left="Left", save="Save route", share="Share", searchPlace="Search a place", allCats="All categories", allRegs="All regions", tabPlaces="Places", tabMap="Map", tabRoute="Route", traffic="Traffic", weather="Weather", book="Book the car", legend_sel="Selected", legend_ok="Available", legend_nofit="Doesn't fit the time", legend_vis="Visited", loadingRoute="Building the route…", routeErr="Road service unavailable — showing an approximate line", emptyT="No places match the filters", emptyS="Increase the daily time or remove a filter.", clearF="Clear filters", noStops="The route is empty — pick places from the list or a standard tour.", tourSearch="Search tours", f_dur="Duration", f_type="Type", f_season="Season", f_car="Vehicle", noTours="No tours for this filter", offF="Remove filter", bTitle="Book the car", bName="Name", bPhone="Phone", bInvalid="Fill in name and phone", bSend="Send request", bDoneT="Request sent", bookCar="Book a car", ret_back="↩ Returning to the start", ret_last="Staying at the last stop", ret_other="Staying elsewhere…", stay_ph="Where do you stay?", reassure="No prepayment · an operator will call you shortly", sendErr="Could not send — try again or write us on WhatsApp", waBtn="Write on WhatsApp", phoneHint="e.g. 5XX 12 34 56", meterHint="Tick places in the list — time is counted automatically", plusDay="+1 day"),
    "ru": dict(h1="Спланируйте поездку по Грузии", lead="Выберите места на карте, посчитайте время по дням и поделитесь маршрутом. Машина, аренда или водитель — в конце.", plan="Спланировать поездку", tours="Готовые туры", origin="Начальная точка", origin_ph="Город или место", myLoc="Моё местоположение", start="С", end="По", days="Сколько дней", people="Сколько вас", transport="Транспорт", t_suggest="Предложите машину", t_own="Я на своей машине", t_rent="Хочу арендовать машину", t_driver="Нужен водитель", dayTime="Часов в день", byDay="По дням", chosen="Бюджет", used="Использовано", left="Осталось", save="Сохранить маршрут", share="Поделиться", searchPlace="Поиск места", allCats="Все категории", allRegs="Все регионы", tabPlaces="Места", tabMap="Карта", tabRoute="Маршрут", traffic="Трафик", weather="Погода", book="Забронировать машину", legend_sel="Выбрано", legend_ok="Доступно", legend_nofit="Не помещается по времени", legend_vis="Посещено", loadingRoute="Строим маршрут…", routeErr="Сервис дорог недоступен — показана примерная линия", emptyT="Нет мест по фильтрам", emptyS="Увеличьте дневное время или снимите фильтр.", clearF="Сбросить фильтры", noStops="Маршрут пуст — выберите места из списка или готовый тур.", tourSearch="Поиск тура", f_dur="Длительность", f_type="Тип", f_season="Сезон", f_car="Автомобиль", noTours="Нет туров по этому фильтру", offF="Снять фильтр", bTitle="Бронирование машины", bName="Имя", bPhone="Телефон", bInvalid="Заполните имя и телефон", bSend="Отправить запрос", bDoneT="Запрос отправлен", bookCar="Забронировать машину", ret_back="↩ Возвращаюсь в начальную точку", ret_last="Остаюсь на последней остановке", ret_other="Остаюсь в другом месте…", stay_ph="Где останетесь?", reassure="Без предоплаты · оператор скоро перезвонит", sendErr="Не отправилось — попробуйте снова или напишите в WhatsApp", waBtn="Написать в WhatsApp", phoneHint="напр. 5XX 12 34 56", meterHint="Отмечайте места в списке — время считается автоматически", plusDay="+1 день"),
    "fa": dict(h1="سفر خود در گرجستان را برنامه‌ریزی کنید", lead="مکان‌ها را روی نقشه انتخاب کنید، زمان را روزبه‌روز بشمارید و مسیر را به اشتراک بگذارید. خودرو، اجاره یا راننده در پایان.", plan="برنامه‌ریزی سفر", tours="تورهای استاندارد", origin="نقطهٔ شروع", origin_ph="شهر یا مکان", myLoc="موقعیت من", start="از", end="تا", days="چند روز", people="چند نفرید", transport="حمل‌ونقل", t_suggest="خودرو پیشنهاد دهید", t_own="با خودروی خودم هستم", t_rent="می‌خواهم خودرو اجاره کنم", t_driver="راننده لازم دارم", dayTime="ساعت در روز", byDay="به تفکیک روز", chosen="زمان انتخابی", used="مصرف‌شده", left="باقی‌مانده", save="ذخیرهٔ مسیر", share="اشتراک‌گذاری", searchPlace="جست‌وجوی مکان", allCats="همهٔ دسته‌ها", allRegs="همهٔ مناطق", tabPlaces="مکان‌ها", tabMap="نقشه", tabRoute="مسیر", traffic="ترافیک", weather="آب‌وهوا", book="رزرو خودرو", legend_sel="انتخاب‌شده", legend_ok="در دسترس", legend_nofit="در زمان نمی‌گنجد", legend_vis="بازدیدشده", loadingRoute="در حال ساخت مسیر…", routeErr="سرویس جاده در دسترس نیست — خط تقریبی نمایش داده می‌شود", emptyT="مکانی با این فیلترها نیست", emptyS="زمان روزانه را افزایش دهید یا فیلتر را بردارید.", clearF="پاک‌کردن فیلترها", noStops="مسیر خالی است — از فهرست مکان انتخاب کنید یا توری استاندارد.", tourSearch="جست‌وجوی تور", f_dur="مدت", f_type="نوع", f_season="فصل", f_car="خودرو", noTours="توری با این فیلتر نیست", offF="حذف فیلتر", bTitle="رزرو خودرو", bName="نام", bPhone="تلفن", bInvalid="نام و تلفن را پر کنید", bSend="ارسال درخواست", bDoneT="درخواست ارسال شد", bookCar="رزرو خودرو", ret_back="↩ به نقطهٔ شروع برمی‌گردم", ret_last="در آخرین توقف می‌مانم", ret_other="جای دیگری می‌مانم…", stay_ph="کجا می‌مانید؟", reassure="بدون پیش‌پرداخت · اپراتور به‌زودی تماس می‌گیرد", sendErr="ارسال نشد — دوباره تلاش کنید یا در واتساپ بنویسید", waBtn="پیام در واتساپ", phoneHint="مثلاً 5XX 12 34 56", meterHint="مکان‌ها را در فهرست علامت بزنید — زمان خودکار حساب می‌شود", plusDay="+۱ روز"),
    "he": dict(h1="תכננו טיול בגאורגיה", lead="בחרו מקומות על המפה, חשבו את הזמן לפי ימים ושתפו את המסלול. רכב, השכרה או נהג — בסוף.", plan="לתכנן טיול", tours="טיולים סטנדרטיים", origin="נקודת מוצא", origin_ph="עיר או מקום", myLoc="המיקום שלי", start="מתאריך", end="עד", days="כמה ימים", people="כמה אתם", transport="תחבורה", t_suggest="הציעו לי רכב", t_own="אני עם רכב משלי", t_rent="רוצה לשכור רכב", t_driver="צריך נהג", dayTime="שעות ביום", byDay="לפי ימים", chosen="תקציב זמן", used="בשימוש", left="נותר", save="שמירת מסלול", share="שיתוף", searchPlace="חיפוש מקום", allCats="כל הקטגוריות", allRegs="כל האזורים", tabPlaces="מקומות", tabMap="מפה", tabRoute="מסלול", traffic="תנועה", weather="מזג אוויר", book="הזמנת רכב", legend_sel="נבחר", legend_ok="זמין", legend_nofit="לא נכנס בזמן", legend_vis="ביקרתי", loadingRoute="בונים מסלול…", routeErr="שירות הדרכים אינו זמין — מוצג קו משוער", emptyT="אין מקומות למסננים", emptyS="הגדילו את הזמן היומי או הסירו מסנן.", clearF="ניקוי מסננים", noStops="המסלול ריק — בחרו מקומות מהרשימה או טיול סטנדרטי.", tourSearch="חיפוש טיול", f_dur="משך", f_type="סוג", f_season="עונה", f_car="רכב", noTours="אין טיולים למסנן זה", offF="הסרת מסנן", bTitle="הזמנת רכב", bName="שם", bPhone="טלפון", bInvalid="מלאו שם וטלפון", bSend="שליחת בקשה", bDoneT="הבקשה נשלחה", bookCar="הזמנת רכב", ret_back="↩ חוזרים לנקודת המוצא", ret_last="נשארים בעצירה האחרונה", ret_other="נשארים במקום אחר…", stay_ph="איפה נשארים?", reassure="ללא תשלום מראש · נציג יחזור אליכם בקרוב", sendErr="לא נשלח — נסו שוב או כתבו לנו בוואטסאפ", waBtn="כתבו בוואטסאפ", phoneHint="לדוגמה 5XX 12 34 56", meterHint="סמנו מקומות ברשימה — הזמן מחושב אוטומטית", plusDay="+יום"),
    "ar": dict(h1="خطط رحلتك في جورجيا", lead="اختر الأماكن على الخريطة، واحسب الوقت يوماً بيوم، وشارك المسار. السيارة أو الاستئجار أو السائق في النهاية.", plan="خطط رحلة", tours="جولات قياسية", origin="نقطة البداية", origin_ph="مدينة أو مكان", myLoc="موقعي", start="من", end="إلى", days="كم يوماً", people="كم عددكم", transport="التنقل", t_suggest="اقترحوا لي سيارة", t_own="لدي سيارتي الخاصة", t_rent="أريد استئجار سيارة", t_driver="أحتاج سائقاً", dayTime="ساعات في اليوم", byDay="حسب الأيام", chosen="الوقت المختار", used="المستخدم", left="المتبقي", save="حفظ المسار", share="مشاركة", searchPlace="ابحث عن مكان", allCats="كل الفئات", allRegs="كل المناطق", tabPlaces="الأماكن", tabMap="الخريطة", tabRoute="المسار", traffic="الحركة", weather="الطقس", book="احجز السيارة", legend_sel="مختار", legend_ok="متاح", legend_nofit="لا يتسع في الوقت", legend_vis="تمت زيارته", loadingRoute="جارٍ بناء المسار…", routeErr="خدمة الطرق غير متاحة — يظهر خط تقريبي", emptyT="لا أماكن تطابق الفلاتر", emptyS="زد الوقت اليومي أو أزل فلتراً.", clearF="مسح الفلاتر", noStops="المسار فارغ — اختر أماكن من القائمة أو جولة قياسية.", tourSearch="ابحث عن جولة", f_dur="المدة", f_type="النوع", f_season="الموسم", f_car="السيارة", noTours="لا جولات بهذا الفلتر", offF="إزالة الفلتر", bTitle="حجز السيارة", bName="الاسم", bPhone="الهاتف", bInvalid="املأ الاسم والهاتف", bSend="إرسال الطلب", bDoneT="تم إرسال الطلب", bookCar="احجز سيارة", ret_back="↩ أعود إلى نقطة البداية", ret_last="أبقى في آخر محطة", ret_other="أبقى في مكان آخر…", stay_ph="أين ستبقون؟", reassure="بدون دفع مسبق · سيتصل بك الموظف قريباً", sendErr="لم يُرسل — حاول مجدداً أو راسلنا على واتساب", waBtn="راسلنا على واتساب", phoneHint="مثلاً 5XX 12 34 56", meterHint="علّم الأماكن في القائمة — يُحسب الوقت تلقائياً", plusDay="+يوم")}

DOW_JS_T = {
    "ka": dict(h="სთ", m="წთ", day="დღე", day1="დღე", person="ადამიანი", km="კმ", place="ადგილი", places="ადგილი", total="სულ", chosenN="არჩეული", visit="დათვალიერება", visited="ნამყოფი", notVisited="არ ვარ ნამყოფი", fitsTime="ეტევა დროში", noFit="დროში არ ეტევა", details="დეტალები", road="გზა", inGroup="ადგილი ამ ჯგუფში", placeDetails="ადგილის დეტალები", removeStop="მარშრუტიდან მოშორება", addStop="მარშრუტში დამატება", markVisited="ნამყოფად მონიშვნა", visitedYes="ნამყოფი ✓", fullPage="სრული გვერდი →", saved="შენახულია ✓", linkCopied="ბმული დაკოპირდა ✓", shareOpened="გაზიარება გაიხსნა", stop="გაჩერება", myLocName="ჩემი მდებარეობა", notFound="ვერ მოიძებნა — სცადეთ სხვა სახელი", seat="ადგილი", per100="ლ / 100 კმ", sum="სულ", need4="მარშრუტში მაღალმთიანი გზაა — 4×4 რეკომენდებულია", noNeed4="მარშრუტი ასფალტის გზებზეა — სტანდარტული კლასი საკმარისია", chooseTour="ამ ტურის არჩევა", onRoad="გზაში", ratingAll="★ ყველა", noFitNeed="დროში ვერ ეტევა — საჭიროა კიდევ", undo="დაბრუნება", tourApplied="ტური დაიგეგმა რუკაზე", teaserA="მანქანები", teaserB="₾/დღიდან — აირჩიე ადგილები და ნახავ ფასს მარშრუტზე", sending="იგზავნება…", moveUp="ადრე გადატანა", moveDown="გვიან გადატანა", removeL="წაშლა", almostOut="დრო თითქმის ამოიწურა"),
    "en": dict(h="h", m="min", day="days", day1="day", person="people", km="km", place="places", places="places", total="Total", chosenN="Selected", visit="visit", visited="Visited", notVisited="Not visited", fitsTime="Fits the time", noFit="Doesn't fit the time", details="Details", road="drive", inGroup="places in this group", placeDetails="Place details", removeStop="Remove from route", addStop="Add to route", markVisited="Mark as visited", visitedYes="Visited ✓", fullPage="Full page →", saved="Saved ✓", linkCopied="Link copied ✓", shareOpened="Share opened", stop="stops", myLocName="My location", notFound="Nothing found — try another name", seat="seats", per100="l / 100 km", sum="total", need4="The route includes high-mountain roads — 4×4 recommended", noNeed4="The route is on paved roads — a standard class is enough", chooseTour="Choose this tour", onRoad="on the road", ratingAll="★ all", noFitNeed="Doesn't fit — you need about", undo="Undo", tourApplied="Tour applied to the map", teaserA="Cars from", teaserB="₾/day — pick places to see the price for your route", sending="Sending…", moveUp="Move earlier", moveDown="Move later", removeL="Remove", almostOut="Time is almost used up"),
    "ru": dict(h="ч", m="мин", day="дн.", day1="день", person="чел.", km="км", place="мест", places="мест", total="Всего", chosenN="Выбрано", visit="осмотр", visited="Посещено", notVisited="Не посещено", fitsTime="Помещается", noFit="Не помещается по времени", details="Детали", road="в пути", inGroup="мест в этой группе", placeDetails="Детали места", removeStop="Убрать из маршрута", addStop="Добавить в маршрут", markVisited="Отметить посещённым", visitedYes="Посещено ✓", fullPage="Полная страница →", saved="Сохранено ✓", linkCopied="Ссылка скопирована ✓", shareOpened="Открыт шеринг", stop="остановок", myLocName="Моё местоположение", notFound="Не найдено — попробуйте другое имя", seat="мест", per100="л / 100 км", sum="итого", need4="В маршруте высокогорные дороги — рекомендуем 4×4", noNeed4="Маршрут по асфальту — достаточно стандартного класса", chooseTour="Выбрать этот тур", onRoad="в пути", ratingAll="★ все", noFitNeed="Не помещается — нужно ещё около", undo="Вернуть", tourApplied="Тур построен на карте", teaserA="Машины от", teaserB="₾/день — выберите места и увидите цену маршрута", sending="Отправка…", moveUp="Раньше", moveDown="Позже", removeL="Удалить", almostOut="Время почти исчерпано"),
    "fa": dict(h="س", m="د", day="روز", day1="روز", person="نفر", km="کم", place="مکان", places="مکان", total="مجموع", chosenN="انتخاب‌شده", visit="بازدید", visited="بازدیدشده", notVisited="بازدیدنشده", fitsTime="در زمان می‌گنجد", noFit="در زمان نمی‌گنجد", details="جزئیات", road="در راه", inGroup="مکان در این گروه", placeDetails="جزئیات مکان", removeStop="حذف از مسیر", addStop="افزودن به مسیر", markVisited="علامت بازدید", visitedYes="بازدید ✓", fullPage="صفحهٔ کامل →", saved="ذخیره شد ✓", linkCopied="پیوند کپی شد ✓", shareOpened="اشتراک‌گذاری باز شد", stop="توقف", myLocName="موقعیت من", notFound="یافت نشد — نام دیگری امتحان کنید", seat="صندلی", per100="ل/۱۰۰کم", sum="جمع", need4="مسیر شامل جاده‌های کوهستانی است — 4×4 توصیه می‌شود", noNeed4="مسیر آسفالت است — کلاس استاندارد کافی است", chooseTour="انتخاب این تور", onRoad="در راه", ratingAll="★ همه", noFitNeed="نمی‌گنجد — حدوداً نیاز دارید", undo="بازگردانی", tourApplied="تور روی نقشه اعمال شد", teaserA="خودروها از", teaserB="لاری/روز — مکان‌ها را انتخاب کنید تا قیمت مسیر را ببینید", sending="در حال ارسال…", moveUp="جلوتر", moveDown="عقب‌تر", removeL="حذف", almostOut="زمان تقریباً تمام شد"),
    "he": dict(h="ש׳", m="דק׳", day="ימים", day1="יום", person="אנשים", km='ק"מ', place="מקומות", places="מקומות", total='סה"כ', chosenN="נבחרו", visit="ביקור", visited="ביקרתי", notVisited="טרם ביקרתי", fitsTime="נכנס בזמן", noFit="לא נכנס בזמן", details="פרטים", road="נסיעה", inGroup="מקומות בקבוצה", placeDetails="פרטי מקום", removeStop="הסרה מהמסלול", addStop="הוספה למסלול", markVisited="סימון כביקרתי", visitedYes="ביקרתי ✓", fullPage="עמוד מלא →", saved="נשמר ✓", linkCopied="הקישור הועתק ✓", shareOpened="השיתוף נפתח", stop="עצירות", myLocName="המיקום שלי", notFound="לא נמצא — נסו שם אחר", seat="מושבים", per100='ל/100 ק"מ', sum='סה"כ', need4="במסלול דרכים הרריות — מומלץ 4×4", noNeed4="המסלול על כבישים סלולים — מחלקה רגילה מספיקה", chooseTour="בחירת הטיול", onRoad="בדרך", ratingAll="★ הכל", noFitNeed="לא נכנס — צריך עוד בערך", undo="שחזור", tourApplied="הטיול הוחל על המפה", teaserA="רכבים מ-", teaserB="₾/יום — בחרו מקומות ותראו את המחיר למסלול", sending="שולח…", moveUp="הקדמה", moveDown="דחייה", removeL="הסרה", almostOut="הזמן כמעט נגמר"),
    "ar": dict(h="س", m="د", day="أيام", day1="يوم", person="أشخاص", km="كم", place="أماكن", places="أماكن", total="المجموع", chosenN="المختار", visit="زيارة", visited="تمت زيارته", notVisited="لم تتم زيارته", fitsTime="يتسع في الوقت", noFit="لا يتسع في الوقت", details="التفاصيل", road="طريق", inGroup="أماكن في هذه المجموعة", placeDetails="تفاصيل المكان", removeStop="إزالة من المسار", addStop="إضافة إلى المسار", markVisited="وضع علامة زيارة", visitedYes="تمت الزيارة ✓", fullPage="الصفحة الكاملة →", saved="تم الحفظ ✓", linkCopied="تم نسخ الرابط ✓", shareOpened="فُتحت المشاركة", stop="توقفات", myLocName="موقعي", notFound="لم يُعثر — جرّب اسماً آخر", seat="مقاعد", per100="ل/100كم", sum="الإجمالي", need4="المسار يتضمن طرقاً جبلية — يُنصح بـ 4×4", noNeed4="المسار على طرق معبدة — الفئة القياسية كافية", chooseTour="اختيار هذه الجولة", onRoad="في الطريق", ratingAll="★ الكل", noFitNeed="لا يتسع — تحتاج نحو", undo="تراجع", tourApplied="طُبّقت الجولة على الخريطة", teaserA="سيارات من", teaserB="لاري/يوم — اختر أماكن لترى سعر مسارك", sending="جارٍ الإرسال…", moveUp="تقديم", moveDown="تأخير", removeL="إزالة", almostOut="الوقت أوشك على النفاد")}

_DOW_OPT_T = {
    "ka": ("⚡ უმოკლეს დროზე გადალაგება", "მარშრუტი გადალაგდა — %s დაზოგილი", "მარშრუტი უკვე ოპტიმალურია", "გადათრიეთ რიგის შესაცვლელად"),
    "en": ("⚡ Sort for the shortest time", "Route reordered — %s saved", "The route is already optimal", "Drag to reorder"),
    "ru": ("⚡ Кратчайший маршрут", "Маршрут перестроен — экономия %s", "Маршрут уже оптимален", "Перетащите, чтобы изменить порядок"),
    "fa": ("⚡ چیدمان کوتاه‌ترین زمان", "مسیر بازچیده شد — %s صرفه‌جویی", "مسیر از قبل بهینه است", "برای تغییر ترتیب بکشید"),
    "he": ("⚡ סידור לזמן הקצר ביותר", "המסלול סודר מחדש — נחסכו %s", "המסלול כבר אופטימלי", "גררו לשינוי הסדר"),
    "ar": ("⚡ ترتيب لأقصر وقت", "أُعيد ترتيب المسار — تم توفير %s", "المسار مثالي بالفعل", "اسحب لإعادة الترتيب"),
}

_DOW_CAT_T = {
    "ka": ("ყველა", "ბუნება", "კულტურა", "ქალაქი", "ზღვა", "სხვა"),
    "en": ("All", "Nature", "Culture", "Cities", "Sea", "More"),
    "ru": ("Все", "Природа", "Культура", "Города", "Море", "Ещё"),
    "fa": ("همه", "طبیعت", "فرهنگ", "شهرها", "دریا", "دیگر"),
    "he": ("הכול", "טבע", "תרבות", "ערים", "ים", "עוד"),
    "ar": ("الكل", "طبيعة", "ثقافة", "مدن", "بحر", "أخرى"),
}
for _l, _v in _DOW_CAT_T.items():
    (DOW_JS_T[_l]["catAll"], DOW_JS_T[_l]["catNature"], DOW_JS_T[_l]["catCulture"],
     DOW_JS_T[_l]["catCity"], DOW_JS_T[_l]["catSea"], DOW_JS_T[_l]["catOther"]) = _v

_DOW_VIEWTRIP_T = {"ka": "ჩემი ტურის ნახვა", "en": "View my tour", "ru": "Посмотреть мой тур",
                   "fa": "مشاهده تور من", "he": "צפייה בטיול שלי", "ar": "عرض جولتي"}
for _l, _v in _DOW_VIEWTRIP_T.items():
    DOW_UI[_l]["viewTrip"] = _v

for _l, _v in _DOW_OPT_T.items():
    DOW_UI[_l]["optimize"] = _v[0]
    DOW_JS_T[_l]["optDone"], DOW_JS_T[_l]["optNone"], DOW_JS_T[_l]["dragHint"] = _v[1], _v[2], _v[3]

_DOW_DETOUR_T = {"ka": ("გადახვევა", "გზაზეა"), "en": ("detour", "on the way"),
                 "ru": ("крюк", "по пути"), "fa": ("انحراف", "در مسیر"),
                 "he": ("סטייה", "על הדרך"), "ar": ("انحراف", "على الطريق")}
for _l, _v in _DOW_DETOUR_T.items():
    DOW_JS_T[_l]["detour"], DOW_JS_T[_l]["onWay"] = _v

_DOW_SAVE_T = {
    "ka": ("შედით ანგარიშში, რომ მარშრუტი შეინახოთ", "შენახვა ვერ მოხერხდა — სცადეთ ხელახლა"),
    "en": ("Sign in to save your route", "Could not save — try again"),
    "ru": ("Войдите, чтобы сохранить маршрут", "Не удалось сохранить — попробуйте ещё раз"),
    "fa": ("برای ذخیره مسیر وارد شوید", "ذخیره نشد — دوباره تلاش کنید"),
    "he": ("התחברו כדי לשמור את המסלול", "השמירה נכשלה — נסו שוב"),
    "ar": ("سجّل الدخول لحفظ المسار", "تعذر الحفظ — حاول مجدداً"),
}
for _l, _v in _DOW_SAVE_T.items():
    DOW_JS_T[_l]["signinToSave"], DOW_JS_T[_l]["saveErr"] = _v




def travel_workspace_block(lang, depth, height="72vh", hero=False, initial="explore"):
    """RentUp Trip Workspace — მომხმარებლის მაკეტის ზუსტი განლაგება."""
    base = rel_prefix(depth)
    U = DOW_UI[lang]
    types = sorted({a["type"] for a in ATTRACTIONS.values()},
                   key=lambda t: tl(lang, "type", t))
    topts = "".join(f'<option value="{E(t)}">{E(tl(lang, "type", t))}</option>' for t in types)
    ropts = "".join(f'<option value="{E(k)}">{E(r[lang]["name"])}</option>'
                    for k, r in REGIONS.items())
    seasons = sorted({r.get("best_season", "") for r in ROUTES.values() if r.get("best_season")})
    sopts = "".join(f'<option value="{E(s)}">{E(tl(lang, "season", s))}</option>' for s in seasons)
    purposes = sorted({r.get("purpose", "classic") for r in ROUTES.values()})
    purpose_names = {
        "ka": {"classic": "კლასიკური", "culinary": "კულინარიული", "wine": "ღვინის", "culture": "კულტურული", "nature": "ბუნება", "cycling": "ველო", "mountains": "მთები", "hiking": "ჰაიქინგი", "history": "ისტორიული", "beach": "ზღვა", "family": "ოჯახური", "performance": "თეატრი"},
        "en": {"classic": "Classic", "culinary": "Culinary", "wine": "Wine", "culture": "Culture", "nature": "Nature", "cycling": "Cycling", "mountains": "Mountains", "hiking": "Hiking", "history": "History", "beach": "Beach", "family": "Family", "performance": "Theatre"},
        "ru": {"classic": "Классический", "culinary": "Кулинарный", "wine": "Винный", "culture": "Культурный", "nature": "Природа", "cycling": "Вело", "mountains": "Горы", "hiking": "Хайкинг", "history": "Исторический", "beach": "Море", "family": "Семейный", "performance": "Театр"},
        "fa": {"classic": "کلاسیک", "culinary": "آشپزی", "wine": "شراب", "culture": "فرهنگی", "nature": "طبیعت", "cycling": "دوچرخه", "mountains": "کوهستان", "hiking": "پیاده‌روی", "history": "تاریخی", "beach": "ساحل", "family": "خانوادگی", "performance": "تئاتر"},
        "he": {"classic": "קלאסי", "culinary": "קולינרי", "wine": "יין", "culture": "תרבות", "nature": "טבע", "cycling": "אופניים", "mountains": "הרים", "hiking": "הליכה", "history": "היסטורי", "beach": "חוף", "family": "משפחתי", "performance": "תיאטרון"},
        "ar": {"classic": "كلاسيكية", "culinary": "طهي", "wine": "نبيذ", "culture": "ثقافية", "nature": "طبيعة", "cycling": "دراجات", "mountains": "جبال", "hiking": "مشي", "history": "تاريخية", "beach": "شاطئ", "family": "عائلية", "performance": "مسرح"},
    }[lang]
    popts = "".join(f'<option value="{E(p)}">{E(purpose_names.get(p, p))}</option>' for p in purposes)
    copts = "".join(f'<option value="{c}">{E(cat_label(c, lang))}</option>'
                    for c in ("economy", "suv", "offroad"))
    html = f'''<section class="dow" id="dow">
<div class="dow-intro"><div><h2 class="dow-h1">{E(U["h1"])}</h2>
<p class="dow-sub">{E(U["lead"])}</p></div>
<div class="dow-intro-b"><a class="dow-btn tealsolid" href="{page_url(lang, 'fleet', False)}">{E(U["bookCar"])}</a>
<button type="button" id="dowplan" class="dow-btn navy">{E(U["plan"])}</button>
<button type="button" id="dowtours" class="dow-btn outline">{E(U["tours"])}</button></div></div>
<div class="dow-formwrap">
<div class="dow-prow">
<div class="dow-f dow-f-origin"><label for="doworigin">{E(U["origin"])}</label>
<input id="doworigin" type="text" autocomplete="off" placeholder="{E(U["origin_ph"])}" aria-label="{E(U["origin"])}">
<div id="dowsuggest" class="dow-suggest do-scroll" role="listbox" hidden></div></div>
<div class="dow-f dow-f-btn"><span>&nbsp;</span>
<button type="button" id="dowmyloc" class="dow-fbtn"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0d94ae" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path></svg> <span>{E(U["myLoc"])}</span></button></div>
<div class="dow-f"><label for="dowstart">{E(U["start"])}</label><input id="dowstart" type="date"></div>
<div class="dow-f"><label for="dowend">{E(U["end"])}</label><input id="dowend" type="date"></div>
<div class="dow-f"><span>{E(U["days"])}</span><div class="dow-step">
<button type="button" id="dowdaysminus" aria-label="−">−</button><div id="dowdays"></div>
<button type="button" id="dowdaysplus" aria-label="+">+</button></div></div>
<div class="dow-f"><span>{E(U["people"])}</span><div class="dow-step">
<button type="button" id="dowpplminus" aria-label="−">−</button><div id="dowpeople"></div>
<button type="button" id="dowpplplus" aria-label="+">+</button></div></div>
<div class="dow-f"><label for="dowtransport">{E(U["transport"])}</label><select id="dowtransport">
<option value="suggest">{E(U["t_suggest"])}</option><option value="own">{E(U["t_own"])}</option>
<option value="rent">{E(U["t_rent"])}</option><option value="driver">{E(U["t_driver"])}</option></select></div>
</div>
<div class="dow-brow">
<div class="dow-bud"><span>{E(U["dayTime"])}</span>
<div class="dow-budstep"><button type="button" id="dowbudminus" aria-label="−">−</button>
<input id="dowbudget" aria-label="{E(U["dayTime"])}">
<button type="button" id="dowbudplus" aria-label="+">+</button></div>
<button type="button" id="dowbyday" class="dow-bydaybtn">{E(U["byDay"])}</button></div>
<div class="dow-ret"><select id="dowret" aria-label="{E(U["ret_back"])}">
<option value="back">{E(U["ret_back"])}</option>
<option value="last">{E(U["ret_last"])}</option>
<option value="other">{E(U["ret_other"])}</option></select>
<input id="dowstay" list="dowstaylist" placeholder="{E(U["stay_ph"])}" aria-label="{E(U["stay_ph"])}" hidden>
<datalist id="dowstaylist"></datalist></div>
<div class="dow-meterwrap"><div class="dow-meterlabels">
<span>{E(U["chosen"])} <strong id="dowchosen"></strong></span>
<span>{E(U["used"])} <strong id="dowused"></strong></span>
<span>{E(U["left"])} <strong id="dowleft" class="ok"></strong></span>
<span id="dowmeterhint" class="dow-meterhint"></span></div>
<div class="dow-meter"><div id="dowmeter"></div></div></div>
<div id="dowactions" class="dow-tripbtns" hidden>
<button type="button" id="dowopt" class="dow-btn outline sm" hidden>{E(U["optimize"])}</button>
<a id="dowtrip" class="dow-btn tealsolid sm" target="_blank" rel="noopener" hidden>{E(U["viewTrip"])}</a>
<button type="button" id="dowsave" class="dow-btn outline sm">{E(U["save"])}</button>
<button type="button" id="dowshare" class="dow-btn ghost sm">{E(U["share"])}</button>
<span id="dowmsg" role="status" class="dow-msg"></span></div>
<div id="dowtourchip" class="dow-tourchip" hidden><b id="dowtourname"></b>
<span id="dowtourmeta"></span><button type="button" id="dowtourclear" aria-label="×">×</button></div>
</div>
<div id="dowdaygrid" class="dow-daygrid" hidden></div>
</div>
<div class="dow-tabs">
<button type="button" id="dowtab-places">{E(U["tabPlaces"])}</button>
<button type="button" id="dowtab-map">{E(U["tabMap"])}</button>
<button type="button" id="dowtab-route">{E(U["tabRoute"])} <span id="dowtabroutec" class="dow-tabbadge" hidden></span></button></div>
<div class="dow-ws">
<div class="dow-places do-scroll">
<div id="dowroutepanel" class="dow-routepanel" hidden>
<div class="dow-rpmeta"><span>{E(U["used"])} <strong id="dowrpused"></strong></span>
<span>{E(U["left"])} <strong id="dowrpleft" class="ok"></strong></span></div>
<div id="dowroutelist"></div>
<span id="downostops" class="dow-nostops">{E(U["noStops"])}</span>
<div id="dowcar2" class="dow-car static" hidden><div class="dow-car-h"><span class="dow-car-n"></span>
<span class="dow-car-p"></span></div><span class="dow-car-s"></span><span class="dow-car-r"></span>
<select class="dow-car-sel" aria-label="{E(U["f_car"])}" hidden></select>
<button type="button" class="dow-btn teal" data-dow-book>{E(U["book"])}</button></div>
</div>
<div class="dow-filters">
<input id="dowq" type="search" placeholder="{E(U["searchPlace"])}" aria-label="{E(U["searchPlace"])}">
<div id="dowcattiles" class="dow-cattiles"></div>
<div id="dowchips" class="dow-chiprow"></div>
<div class="dow-selrow">
<select id="dowcat" aria-label="{E(U["allCats"])}"><option value="">{E(U["allCats"])}</option>{topts}</select>
<select id="dowreg" aria-label="{E(U["allRegs"])}"><option value="">{E(U["allRegs"])}</option>{ropts}</select></div>
<div class="dow-counters"><span id="dowcount"></span><span id="dowselcount"></span></div>
</div>
<div id="dowlist" class="dow-list do-scroll"></div>
<div id="dowempty" class="dow-empty" hidden><b>{E(U["emptyT"])}</b><span>{E(U["emptyS"])}</span>
<button type="button" id="dowreset" class="dow-fbtn">{E(U["clearF"])}</button></div>
</div>
<div class="dow-mapcol">
<div id="dowmap" role="application" aria-label="{E(U["tabMap"])}"></div>
<div class="dow-mapover">
<div id="dowroutechips" class="dow-routechips do-scroll"></div>
<div class="dow-mapbtns">
<button type="button" id="dowtraffic" aria-pressed="false">{E(U["traffic"])}</button>
<button type="button" id="dowweather" aria-pressed="true">{E(U["weather"])}</button></div></div>
<div id="dowloading" class="dow-status" role="status" hidden>{E(U["loadingRoute"])}</div>
<div id="dowerror" class="dow-status err" role="status" hidden>{E(U["routeErr"])}</div>
<div class="dow-legend">
<span><i style="background:#0d94ae"></i>{E(U["legend_sel"])}</span>
<span><i style="background:#0b2f4d"></i>{E(U["legend_ok"])}</span>
<span><i style="background:#b9c6d1"></i>{E(U["legend_nofit"])}</span>
<span><i style="background:#7f8c99;opacity:.55"></i>{E(U["legend_vis"])}</span></div>
<div id="dowcar" class="dow-car float" hidden><div class="dow-car-h"><span class="dow-car-n"></span>
<span class="dow-car-p"></span></div><span class="dow-car-s"></span><span class="dow-car-r"></span>
<select class="dow-car-sel" aria-label="{E(U["f_car"])}" hidden></select>
<button type="button" class="dow-btn teal" data-dow-book>{E(U["book"])}</button></div>
<div id="dowdetail" class="dow-detail do-scroll" role="dialog" hidden>
<div class="dow-dhead"><b id="dowdtitle"></b>
<button type="button" id="dowdclose" aria-label="×">×</button></div>
<div id="dowdbody"></div></div>
</div>
</div>
<div id="dowdrawer" class="dow-overlay right" hidden>
<button type="button" id="dowtback" class="dow-scrim" aria-label="×"></button>
<div class="dow-drawer do-scroll" role="dialog" aria-label="{E(U["tours"])}">
<div class="dow-drawerhead"><div class="dow-dh-r"><span>{E(U["tours"])}</span>
<button type="button" id="dowtclose" aria-label="×">×</button></div>
<input id="dowtq" type="search" placeholder="{E(U["tourSearch"])}" aria-label="{E(U["tourSearch"])}">
<div class="dow-tf">
<select id="dowtf-dur" aria-label="{E(U["f_dur"])}"><option value="">{E(U["f_dur"])}</option>
<option value="1-2">1–2</option><option value="3-4">3–4</option><option value="5+">5+</option></select>
<select id="dowtf-type" aria-label="{E(U["f_type"])}"><option value="">{E(U["f_type"])}</option>{popts}</select>
<select id="dowtf-season" aria-label="{E(U["f_season"])}"><option value="">{E(U["f_season"])}</option>{sopts}</select>
<select id="dowtf-car" aria-label="{E(U["f_car"])}"><option value="">{E(U["f_car"])}</option>{copts}</select></div></div>
<div id="dowtlist" class="dow-tlist"></div>
<div id="dowtempty" class="dow-empty" hidden><b>{E(U["noTours"])}</b>
<button type="button" id="dowtreset" class="dow-fbtn">{E(U["offF"])}</button></div>
</div></div>
<div id="dowbooking" class="dow-overlay center" hidden>
<button type="button" id="dowbback" class="dow-scrim" aria-label="×"></button>
<div class="dow-modal" role="dialog" aria-label="{E(U["bTitle"])}">
<div class="dow-dh-r"><span>{E(U["bTitle"])}</span>
<button type="button" id="dowbclose" aria-label="×">×</button></div>
<div id="dowbdone" class="dow-bdone" hidden><b>{E(U["bDoneT"])}</b><span id="dowbsum2"></span>
<span class="dow-reassure">{E(U["reassure"])}</span>
<a id="dowbwa2" class="dow-btn ghost sm" target="_blank" rel="noopener" hidden>{E(U["waBtn"])}</a></div>
<div id="dowbform"><div class="dow-bcar"><span id="dowbcar"></span><span id="dowbsum"></span>
<span id="dowbprice" class="dow-bprice"></span></div>
<div class="dow-brow2"><label>{E(U["bName"])}<input id="dowbname" autocomplete="name"></label>
<label>{E(U["bPhone"])}<input id="dowbphone" type="tel" inputmode="tel" autocomplete="tel" placeholder="{E(U["phoneHint"])}"></label></div>
<span id="dowbinvalid" role="alert" class="dow-alert" hidden>{E(U["bInvalid"])}</span>
<span id="dowberr" role="alert" class="dow-alert" hidden>{E(U["sendErr"])}</span>
<button type="button" id="dowbsend" class="dow-btn teal big">{E(U["bSend"])}</button>
<span class="dow-reassure">{E(U["reassure"])}</span>
<a id="dowbwa" class="dow-btn ghost sm" target="_blank" rel="noopener" hidden>{E(U["waBtn"])}</a></div>
</div></div>
<div id="dowmcta" class="dow-mcta" hidden><span id="dowmctatxt"></span>
<button type="button" class="dow-btn teal" data-dow-book>{E(U["book"])}</button></div>
</section>'''
    js = (EXPLORER_JS % {"js": LEAFLET_JS, "base": J(base),
                         "data": TRAVEL_ASSET[lang], "exp": ASSET["workspace"]}
          + f'\n<script>window.DOWT={J(dict(DOW_JS_T[lang], tripUrl=lang_root(lang) + "trip/"))};</script>')
    return html, js


def render_planner(lang):
    P = PLANNER[lang]
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    workspace, tail = travel_workspace_block(lang, depth, "78vh", initial="planner")

    body = (f'<section class="page-head compact"><div class="wrap"><h1>{E(P["h1"])}</h1>'
            f'<p class="lead">{inline(P["lead"], lang)}</p></div></section>'
            f'<section class="sec planner-map-sec"><div class="wrap wide">{workspace}</div></section>')

    graph = [org_node(lang), website_node(lang),
             {"@type": "WebApplication", "@id": page_url(lang, "planner") + "#app",
              "name": P["h1"], "description": P["desc"], "url": page_url(lang, "planner"),
              "applicationCategory": "TravelApplication", "operatingSystem": "Web browser",
              "inLanguage": lang, "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GEL"},
              "provider": {"@id": SITE_URL + "/#organization"}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["planner"], page_url(lang, "planner"))])]
    head = head_html(lang, "planner", P["title"], P["desc"], P.get("keywords", ""),
                     page_url(lang, "planner"), {l: page_url(l, "planner") for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["planner"], None)])
    return shell(lang, "planner", head, crumbs + f'<main id="main">{body}</main>', depth, tail)


# ══════════════════════════════════════════════════════════════ sitemap etc.
@functools.lru_cache(maxsize=1)
def _git_commit_dates():
    """Last commit date per tracked file.

    `actions/checkout` rewrites every mtime to the moment of checkout, so the
    filesystem-based lastmod collapsed to a single identical date across the
    whole sitemap in CI — which tells a crawler nothing. Git knows the real one.
    One `git log` walk for the whole tree; empty dict if git is unavailable."""
    out = {}
    try:
        raw = subprocess.run(
            ["git", "log", "--name-only", "--no-merges", "--format=%x00%cs", "-z"],
            capture_output=True, text=True, timeout=120, check=True).stdout
    except Exception:
        return out
    cur = None
    for tok in raw.split("\x00"):
        for part in tok.split("\0"):
            part = part.strip()
            if not part:
                continue
            if len(part) == 10 and part[4] == "-" and part[7] == "-":
                cur = part
            elif cur:
                out.setdefault(part, cur)   # first sighting = most recent commit
    return out


def source_lastmod(path):
    """Stable sitemap date derived from the content source, not build time."""
    if path:
        d = _git_commit_dates().get(Path(path).as_posix())
        if d:
            return d
    try:
        return date.fromtimestamp(Path(path).stat().st_mtime).isoformat()
    except (OSError, ValueError, TypeError):
        return TODAY


def _sitemap_urls(entries):
    """entries: list of (loc_fn, priority, source_path or None)."""
    urls = []
    for loc_fn, prio, source in entries:
        lastmod = source_lastmod(source) if source else source_lastmod("build.py")
        for lang in LANGS:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{loc_fn(l)}"/>'
                for l in LANGS)
            alts += (f'\n    <xhtml:link rel="alternate" hreflang="x-default" '
                     f'href="{loc_fn("en")}"/>')
            urls.append(f"""  <url>
    <loc>{loc_fn(lang)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{prio}</priority>{alts}
  </url>""")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def sitemap_children():
    """Sitemap split by content type. Only canonical, indexable, 200 pages."""
    core = []
    for page in PAGE_ORDER:
        if page in ("planner", "account"):
            continue          # planner is an alias of /map/; account is noindex
        prio = ("1.0" if page == "index" else
                "0.9" if page in ("fleet", "map", "blog", "software") else "0.7")
        core.append((lambda l, p=page: page_url(l, p), prio,
                     Path("content/pages") / f"{page}.yml"))
    # /tours/ — the ready-made routes hub (was missing from the sitemap)
    core.append((lambda l: SITE_URL + lang_root(l) + "tours/", "0.9", None))
    out = {"core": core}
    rental = []
    if (SEO_CAR_RENTAL.get("hub") or {}):
        rental.append((lambda l: rental_hub_url(l), "0.9", Path("content/settings/seo_car_rental.yml")))
    for k in RENTAL_PLACES:
        if rental_quality_ok("location", (SEO_CAR_RENTAL.get("locations") or {}).get(k, {})):
            rental.append((lambda l, kk=k: rental_place_url(l, kk), "0.8",
                           Path("content/settings/seo_car_rental.yml")))
    for k in SEO_CATEGORY_ORDER:
        if rental_quality_ok("category", _seo_cats().get(k, {})):
            rental.append((lambda l, kk=k: rental_cat_url(l, kk), "0.8",
                           Path("content/settings/seo_categories.yml")))
    if rental:
        out["car-rental"] = rental
    travel = []
    if (SEO_TRIP_PLANNER.get("planner") or {}):
        travel.append((lambda l: planner_landing_url(l), "0.9",
                       Path("content/settings/seo_trip_planner.yml")))
    good_itins = [k for k, v in ITINERARIES.items() if itinerary_quality_ok(v)]
    if good_itins:
        travel.append((lambda l: itin_hub_url(l), "0.8", None))
        for k in good_itins:
            travel.append((lambda l, kk=k: itin_url(l, kk), "0.8",
                           Path("content/itineraries") / f"{k}.yml"))
    if travel:
        out["itineraries"] = travel
    good_guides = [k for k, v in GUIDES.items() if guide_quality_ok(v, ROOT_LANG)]
    if good_guides:
        out["guides"] = [(lambda l: guides_hub_url(l), "0.8", None)] + [
            (lambda l, kk=k: guide_url(l, kk), "0.8", Path("content/guides") / f"{k}.yml")
            for k in good_guides]
    out["cars"] = [(lambda l, s=slug: car_url(l, s), "0.8",
                    Path("content/cars") / f"{slug}.yml") for slug in CARS]
    out["core"].append((lambda l: day_trip_url(l), "0.9", None))
    out["core"].append((lambda l: index_hub_url(l, "attractions"), "0.8", None))
    out["core"].append((lambda l: index_hub_url(l, "routes"), "0.8", None))
    out["core"].append((lambda l: index_hub_url(l, "regions"), "0.8", None))
    out["attractions"] = [(lambda l, s=slug: attr_url(l, s), "0.7",
                           Path("content/attractions") / f"{slug}.yml") for slug in ATTRACTIONS]
    out["routes"] = [(lambda l, s=slug: route_url(l, s), "0.8",
                      Path("content/routes") / f"{slug}.yml") for slug in ROUTES]
    out["regions"] = [(lambda l, k=key: region_url(l, k), "0.8",
                       Path("content/regions") / f"{key}.yml") for key in REGIONS]
    out["blog"] = [(lambda l, s=slug: post_url(l, s), "0.6",
                    Path("content/posts") / f"{slug}.yml") for slug in POSTS]
    for name, entries in list(out.items()):
        if not entries:
            del out[name]
    return out


def sitemap_index(children):
    lastmod = source_lastmod("build.py")
    items = "\n".join(
        f"  <sitemap>\n    <loc>{SITE_URL}/sitemaps/{n}.xml</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n  </sitemap>" for n in children)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + items + "\n</sitemapindex>\n")


AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
           "Claude-SearchBot", "anthropic-ai", "PerplexityBot", "Perplexity-User",
           "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot",
           "Meta-ExternalAgent", "cohere-ai", "YandexBot", "Amazonbot",
           "DuckAssistBot", "MistralAI-User",
           "Bytespider",
           "Google-CloudVertexBot"]


def robots(include_docs=False):
    # Personal, per-visitor pages. They are already noindex; keeping crawlers
    # out of them as well saves crawl budget on a 2 300-page site.
    # /planner/ and /pricing/ stay crawlable: they are noindex *aliases* and
    # their rel=canonical only consolidates if a crawler can read it.
    private = ["/account/", "/trip/", "/app/"]
    out = ["User-agent: *", "Allow: /", "Disallow: /admin/"] + \
          [f"Disallow: {p}" for p in private]
    # Only advertise /docs/ when it is actually published; a Disallow line for
    # a path that does not exist just points at it.
    if include_docs:
        out.append("Disallow: /docs/")
    out.append("")
    for b in AI_BOTS:
        out += [f"User-agent: {b}", "Allow: /", ""]
    # `Host:` was a Yandex-only directive, retired in 2018 — it does nothing now.
    out += [f"Sitemap: {SITE_URL}/sitemap.xml", ""]
    return "\n".join(out)


def strip_md(s):
    return _LINK.sub(r"\1", s or "").replace("**", "")


def llms_txt():
    u, m = UI["en"], META["en"]
    out = [f"# {BRAND}", "", f"> {m['org_desc']}", "", "## Key facts", ""]
    for k, v in m["llms_facts"]:
        out.append(f"- **{k}:** {v}")
    out += ["", "## Pages", ""]
    for p in PAGE_ORDER:
        if p in NOINDEX_PAGES:          # never point an assistant at a noindex page
            continue
        d = counts_sub((PLANNER["en"] if p == "planner" else PAGES[p]["en"])["desc"])
        out.append(f"- [{u['nav'][p]}]({page_url('en', p)}): {d}")
    # The commercial and planning clusters are the pages an assistant is most
    # likely to be asked about, and they were missing entirely.
    _hub = (SEO_CAR_RENTAL.get("hub") or {}).get("en") or {}
    if _hub:
        out.append(f"- [{_hub.get('h1', 'Car rental in Georgia')}]"
                   f"({rental_hub_url('en')}): {_hub.get('lead', '')}")
    for k in RENTAL_PLACES:
        loc = (SEO_CAR_RENTAL.get("locations") or {}).get(k) or {}
        L = loc.get("en") or {}
        if L and rental_quality_ok("location", loc):
            out.append(f"- [{L.get('h1', k)}]({rental_place_url('en', k)}): {L.get('lead', '')}")
    for k in SEO_CATEGORY_ORDER:
        cat = (_seo_cats() or {}).get(k) or {}
        L = cat.get("en") or {}
        if L and rental_quality_ok("category", cat):
            out.append(f"- [{L.get('h1', k)}]({rental_cat_url('en', k)}): {L.get('lead', '')}")
    _pl = (SEO_TRIP_PLANNER.get("planner") or {}).get("en") or {}
    if _pl:
        out.append(f"- [{_pl.get('h1', 'Trip planner')}]"
                   f"({planner_landing_url('en')}): {_pl.get('lead', '')}")
    out += ["", "## Ready-made itineraries", ""]
    for sl, it in ITINERARIES.items():
        if not itinerary_quality_ok(it):
            continue
        L = it.get("en") or {}
        out.append(f"- [{L.get('name', sl)}]({itin_url('en', sl)}): {it['days']} days, "
                   f"{it['total_km']} km, {it['total_drive']} driving, "
                   f"{it.get('car_category', 'economy')} category — {L.get('short', '')}")
    out += ["", "## Fleet", ""]
    for s, c in CARS.items():
        L = c["en"]
        out.append(f"- [{L['name']}]({car_url('en', s)}): {cat_label(c['category'],'en')}, "
                   f"{c['years']}, {c['engine']}, {c['seats']} seats, "
                   f"{c['price_1_6']} GEL/day, deposit {c['deposit']} GEL")
    out += ["", "## Articles", ""]
    for s, p in POSTS.items():
        out.append(f"- [{p['en']['title']}]({post_url('en', s)}) ({p['date']}): {p['en']['desc']}")
    out += ["", "## Road trips", ""]
    for s, r in ROUTES.items():
        out.append(f"- [{r['en']['name']}]({route_url('en', s)}): {r['days']} days, "
                   f"{r['distance_km']} km, {r['drive_time_total']} driving, "
                   f"{r['car_category']} category — {r['en']['short']}")
    out += ["", "## Regions", ""]
    for k, r in REGIONS.items():
        out.append(f"- [{r['en']['name']}]({region_url('en', k)}): {r['en']['short']}")
    out += ["", "## Attractions", ""]
    for s, a in ATTRACTIONS.items():
        out.append(f"- [{a['en']['name']}]({attr_url('en', s)}): {a['en']['short']} "
                   f"Time needed {a['visit_hours']} h; {a['distance_tbilisi_km']} km / "
                   f"{a['drive_time_tbilisi']} from Tbilisi; road {a['road']}; "
                   f"car {a['car_category']}; season {a['best_season']}; entry {a['entry_fee']}")
    out += ["", "## Languages", ""]
    out += [f"- [{LANG_LABEL[l]}]({SITE_URL + lang_root(l)})" for l in LANGS]
    out += ["", "## Contact", "", f"- Phone: {SITE['phone']}", f"- Mobile: {SITE['mobile']}",
            f"- Email: {SITE['email']}",
            f"- Address: {SITE['address']['en']['street']}, {SITE['address']['en']['city']} "
            f"{SITE['address_zip']}, Georgia", "", f"Last updated: {TODAY}", ""]
    return "\n".join(out)


def llms_full_txt():
    out = [f"# {BRAND} — full site content (English)", ""]
    for p in PAGE_ORDER:
        pg = PLANNER["en"] if p == "planner" else PAGES[p]["en"]
        out += [f"\n## {pg['title']}", f"URL: {page_url('en', p)}", "", pg.get("lead", ""), ""]
        for b in pg.get("blocks", []):
            t = b["type"]
            if t in ("h2", "h3"):
                out.append(("### " if t == "h2" else "#### ") + b["text"])
            elif t in ("p", "note"):
                out.append(strip_md(b["text"]))
            elif t in ("ul", "ol"):
                out += ["- " + strip_md(x) for x in b["items"]]
            elif t == "table":
                out.append(" | ".join(b["head"]))
                out += [" | ".join(str(x) for x in (r["cells"] if isinstance(r, dict) else r))
                        for r in b["rows"]]
            elif t == "facts":
                out += [f"{x['k']}: {x['v']}" for x in b["items"]]
            elif t == "cards":
                for x in b["items"]:
                    out.append(f"- {x['title']}: {strip_md(x.get('text',''))} "
                               + " ".join(strip_md(i) for i in x.get("list", [])))
            elif t == "faq":
                for x in b["items"]:
                    out += [f"Q: {x['q']}", f"A: {strip_md(x['a'])}"]
            elif t == "cars":
                for s, c in CARS.items():
                    if c["category"] == b.get("category"):
                        out.append(f"- {c['en']['name']}: {c['en']['summary']}, "
                                   f"{c['price_1_6']} GEL/day")
            elif t == "cta":
                out.append(strip_md(b["text"]))
            out.append("")
    out += ["\n## Fleet detail", ""]
    for s, c in CARS.items():
        L = c["en"]
        out += [f"### {L['name']}", f"URL: {car_url('en', s)}",
                f"Category: {cat_label(c['category'],'en')} | Years: {c['years']} | "
                f"Engine: {c['engine']} | {c['transmission']} | {c['drive']} | "
                f"{c['seats']} seats | {c['fuel_100km']} l/100km | clearance {c['clearance']} mm",
                f"Price: {c['price_1_6']} GEL/day (1-6 d), {c['price_7_29']} (7-29 d), "
                f"{c['price_30']} (30+ d) | Deposit: {c['deposit']} GEL",
                strip_md(L.get("body", "")), ""]
    out += ["\n## Articles", ""]
    for s, p in POSTS.items():
        out += [f"### {p['en']['title']}", f"URL: {post_url('en', s)} ({p['date']})",
                strip_md(p["en"]["body"]), ""]
    out += ["\n## Road trips", ""]
    for s, r in ROUTES.items():
        out += [f"### {r['en']['name']}", f"URL: {route_url('en', s)}",
                f"{r['days']} days / {r['nights']} nights | {r['distance_km']} km | "
                f"{r['drive_time_total']} driving | car: {r['car_category']} | "
                f"season: {r['best_season']} | difficulty: {r['difficulty']}",
                f"Stops: {', '.join(ATTRACTIONS[w]['en']['name'] for w in r['waypoints'] if w in ATTRACTIONS)}",
                strip_md(r["en"]["body"]), strip_md(r["en"]["plan"]),
                "Tips: " + " ".join(strip_md(t) for t in r["en"]["tips"]), ""]
    out += ["\n## Regions", ""]
    for k, rg in REGIONS.items():
        out += [f"### {rg['en']['name']}", f"URL: {region_url('en', k)}",
                strip_md(rg["en"]["body"]),
                "Driving: " + strip_md(rg["en"]["driving"]), ""]
    out += ["\n## Attractions", ""]
    for s, a in ATTRACTIONS.items():
        out += [f"### {a['en']['name']}", f"URL: {attr_url('en', s)}",
                f"Region: {REGIONS[a['region']]['en']['name']} | type: {a['type']} | "
                f"coordinates: {a['lat']}, {a['lon']} | elevation: {a['elevation']} m | "
                f"time needed: {a['visit_hours']} h | from Tbilisi: {a['distance_tbilisi_km']} km "
                f"/ {a['drive_time_tbilisi']} | road: {a['road']} | car: {a['car_category']} | "
                f"season: {a['best_season']} | entry: {a['entry_fee']}",
                strip_md(a["en"]["body"]),
                "Tip: " + strip_md(a["en"]["tip"]),
                "Route from Tbilisi: " + strip_md(a["en"]["route"]), ""]
    return "\n".join(out)


def render_404():
    lang = "ka"
    u = UI[lang]
    links = "".join(f'<li><a href="{page_url(lang, p, False)}">{E(u["nav"][p])}</a></li>'
                    for p in PAGE_ORDER)
    return (f'<!DOCTYPE html><html lang="ka"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>404 — {E(BRAND)}</title><meta name=\"robots\" content=\"noindex, follow\">"
            f'<link rel="stylesheet" href="{ASSET["css"]}">{analytics_html()}</head><body>'
            f'{header_html(lang, "index")}<main id="main"><section class="page-head">'
            f'<div class="wrap"><h1>{E(u["ui"]["e404_title"])}</h1>'
            f'<p class="lead">{E(u["ui"]["e404_text"])}</p><ul>{links}</ul>'
            f"</div></section></main>{footer_html(lang)}</body></html>")


# ══════════════════════════════════════════════════════════════ main
# ══════════════════════════════════════════════════ Landing (მთავარი ჰერო)
# "RentUp - Landing" მაკეტის პორტი: ჰერო ფოტო + 4 სამოქმედო ბარათი + სტატისტიკა.
LAND_UI = {
    "ka": {"h1": "რა გეგმა გაქვს დღეს?", "lead": "აირჩიე სასურველი და დაიწყე შენი მოგზაურობა საქართველოში",
           "c1t": "დაგეგმე ტური დამოუკიდებლად", "c1d": "შეადგინე შენი მარშრუტი, აირჩიე ადგილები და დაგეგმე დღეები",
           "c2t": "სტანდარტული ტურები", "c2d": "აირჩიე უკვე დაგეგმილი ტური საქართველოს რეგიონებში",
           "c3t": "მანქანის დაჯავშნა", "c3d": "იპოვე და დაჯავშნე მარშრუტისთვის შესაბამისი ავტომობილი",
           "c4t": "განვერიანდი Community-ში", "c4d": "გაუზიარე გამოცდილება, იპოვე თანამგზავრები და ახალი ადგილები",
           "s1": "სანახავი ადგილი", "s2": "ავტომობილი", "s3": "მოგზაური", "s4": "საშუალო რეიტინგი"},
    "en": {"h1": "What is your plan for today?", "lead": "Pick what you feel like and start your journey across Georgia",
           "c1t": "Plan your own trip", "c1d": "Build your route, pick the places and lay out the days",
           "c2t": "Standard tours", "c2d": "Take a ready-made route through the regions of Georgia",
           "c3t": "Book a car", "c3d": "Find and book the car that matches your route",
           "c4t": "Join the community", "c4d": "Share what you know, find companions and new places",
           "s1": "places to see", "s2": "cars", "s3": "travellers", "s4": "average rating"},
    "ru": {"h1": "Какие планы на сегодня?", "lead": "Выберите, что вам ближе, и начните путешествие по Грузии",
           "c1t": "Спланировать поездку самому", "c1d": "Составьте маршрут, выберите места и распределите дни",
           "c2t": "Готовые туры", "c2d": "Возьмите готовый маршрут по регионам Грузии",
           "c3t": "Забронировать машину", "c3d": "Найдите и забронируйте машину под ваш маршрут",
           "c4t": "Присоединиться к сообществу", "c4d": "Делитесь опытом, находите попутчиков и новые места",
           "s1": "мест", "s2": "машин", "s3": "путешественников", "s4": "средний рейтинг"},
    "fa": {"h1": "برنامهٔ امروز شما چیست؟", "lead": "آنچه دوست دارید انتخاب کنید و سفر خود در گرجستان را آغاز کنید",
           "c1t": "سفر خود را بسازید", "c1d": "مسیر خود را بچینید، مکان‌ها را انتخاب و روزها را تقسیم کنید",
           "c2t": "تورهای آماده", "c2d": "یک مسیر آماده در مناطق گرجستان را انتخاب کنید",
           "c3t": "رزرو خودرو", "c3d": "خودروی مناسب مسیر خود را پیدا و رزرو کنید",
           "c4t": "به جامعه بپیوندید", "c4d": "تجربه‌تان را بگویید، همسفر و مکان‌های نو پیدا کنید",
           "s1": "مکان دیدنی", "s2": "خودرو", "s3": "مسافر", "s4": "میانگین امتیاز"},
    "he": {"h1": "מה התוכנית שלך להיום?", "lead": "בחרו את מה שמתאים לכם והתחילו את המסע בגאורגיה",
           "c1t": "לתכנן טיול בעצמכם", "c1d": "בנו מסלול, בחרו מקומות וחלקו את הימים",
           "c2t": "טיולים מוכנים", "c2d": "קחו מסלול מוכן באזורי גאורגיה",
           "c3t": "להזמין רכב", "c3d": "מצאו והזמינו את הרכב שמתאים למסלול",
           "c4t": "להצטרף לקהילה", "c4d": "שתפו ידע, מצאו שותפים ומקומות חדשים",
           "s1": "מקומות", "s2": "רכבים", "s3": "מטיילים", "s4": "דירוג ממוצע"},
    "ar": {"h1": "ما خطتك اليوم؟", "lead": "اختر ما يناسبك وابدأ رحلتك في جورجيا",
           "c1t": "خطط رحلتك بنفسك", "c1d": "ارسم مسارك، اختر الأماكن ووزّع الأيام",
           "c2t": "جولات جاهزة", "c2d": "اختر مساراً جاهزاً في مناطق جورجيا",
           "c3t": "احجز سيارة", "c3d": "اعثر على السيارة المناسبة لمسارك واحجزها",
           "c4t": "انضم إلى المجتمع", "c4d": "شارك خبرتك، واعثر على رفقاء وأماكن جديدة",
           "s1": "أماكن للزيارة", "s2": "سيارات", "s3": "مسافرين", "s4": "متوسط التقييم"},
}

_LAND_ICONS = {
    "pin": '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#0b5f9e" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><path d="M12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/></svg>',
    "car": '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#0b7a55" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h14M3 17v-4.2L5.4 7A2 2 0 0 1 7.3 5.7h9.4A2 2 0 0 1 18.6 7L21 12.8V17"/><path d="M6.5 17v1.5M17.5 17v1.5M3 12.8h18"/><path d="M7 14.4h.01M17 14.4h.01"/></svg>',
    "users": '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#6b3fa0" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 19v-1.2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4V19"/><path d="M9 9.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M22 19v-1.2a4 4 0 0 0-3-3.9M16.5 3.7a3 3 0 0 1 0 5.8"/></svg>',
    "star": '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#a5760a" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3.6 2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.8l5.9-.8L12 3.6Z"/></svg>',
}
_LAND_ARROW = ('<span class="land-arrow" style="border-color:{b}">'
               '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="{i}" stroke-width="2.2" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M5 12h13"/><path d="m12 5 7 7-7 7"/></svg></span>')


def landing_stats():
    """რეალური რიცხვები კონტენტიდან — ადგილები, მანქანები, საშ. რეიტინგი."""
    places = len(ATTRACTIONS)
    cars = len([c for c in CARS.values() if c.get("available", True)])
    ratings = [a["rating"] for a in ATTRACTIONS.values() if a.get("rating")]
    avg = round(sum(ratings) / len(ratings), 1) if ratings else 0
    return places, cars, avg


def home_semantic_block(lang):
    """Crawlable prose that states, in HTML, what RentUp actually is.
    Rendered under the visual landing hero — visible to users, not hidden text."""
    H = (SEO_TRIP_PLANNER.get("home") or {}).get(lang) or {}
    secs = H.get("sections") or {}
    if not secs:
        return ""
    links = {
        "rent_a_car": (rental_hub_url(lang, False), su("car_rental", lang)),
        "plan_your_trip": (planner_landing_url(lang, False), su("trip_planner", lang)),
        "ready_made_routes": (lang_root(lang) + "tours/", su("ready_made_routes", lang)),
        "places_to_visit": (page_url(lang, "map", False), su("browse_places", lang)),
        "cars_for_every_route": (page_url(lang, "fleet", False), su("see_all_cars", lang)),
    }
    out = ""
    for i, key in enumerate(["rent_a_car", "plan_your_trip", "ready_made_routes",
                             "places_to_visit", "cars_for_every_route"]):
        v = secs.get(key)
        if not v:
            continue
        href, label = links.get(key, ("", ""))
        cta = (f'<p><a class="btn ghost" href="{href}">{E(label)}</a></p>'
               if href and label else "")
        out += (f'<section class="sec{" alt" if i % 2 else ""}"><div class="wrap">'
                f'<h2>{E(v.get("h2", ""))}</h2>'
                f'<div class="article"><p>{E(v.get("body", ""))}</p>{cta}</div>'
                f'</div></section>')
    # A crawlable index of every cluster. Without it the hub pages are reachable
    # only through the header, which puts the content four to five clicks deep.
    hubs = [
        (day_trip_url(lang, False), su("day_trip_h1", lang)),
        (rental_hub_url(lang, False), su("car_rental", lang) or UI[lang]["nav"]["fleet"]),
        (index_hub_url(lang, "attractions", False), tu(lang, "attractions")),
        (index_hub_url(lang, "routes", False), tu(lang, "routes")),
        (index_hub_url(lang, "regions", False), tu(lang, "regions")),
        (itin_hub_url(lang, False), su("itineraries", lang)),
        (guides_hub_url(lang, False), su("guides", lang)),
        (planner_landing_url(lang, False), su("trip_planner", lang)),
        (page_url(lang, "blog", False), UI[lang]["nav"]["blog"]),
    ]
    out += _sec(su("browse_places", lang) or UI[lang]["nav"]["map"],
                '<ul class="linklist">' + "".join(
                    f'<li><a href="{h}">{E(l)}</a></li>' for h, l in hubs if h and l)
                + '</ul>', alt=len(secs) % 2 == 0)
    return out


def landing_block(lang):
    t = LAND_UI[lang]
    places, cars_n, avg = landing_stats()
    cards = [
        (page_url(lang, "fleet", False), "", t["c3t"], t["c3d"], "rentup-card-cars.jpg", "#eaf3fc", "#cfe1f2", "#0b5f9e"),
        (lang_root(lang) + "tours/", "", t["c2t"], t["c2d"], "rentup-card-tours.jpg", "#fdf6e3", "#f0e2bd", "#a5760a"),
        (page_url(lang, "map", False) + "#planner", "", t["c1t"], t["c1d"], "rentup-card-plan.jpg", "#e9f7ef", "#cbe8d8", "#0b7a55"),
        (page_url(lang, "community", False), "", t["c4t"], t["c4d"], "rentup-card-community.jpg", "#f4eefc", "#e0d3f4", "#6b3fa0"),
    ]
    cards_html = "".join(
        f'<a class="land-card" href="{href}"{attr} style="background:{bg};border-color:{border}">'
        f'<span class="land-card-img"><img src="/assets/{img}" alt="" loading="lazy"></span>'
        f'<span class="land-card-body"><b>{E(title)}</b><span>{E(desc)}</span>'
        f'{_LAND_ARROW.format(b=border, i=ink)}</span></a>'
        for href, attr, title, desc, img, bg, border, ink in cards)
    stats = [
        (f"{places}", t["s1"], _LAND_ICONS["pin"], "#e9f2fa"),
        (f"{cars_n}", t["s2"], _LAND_ICONS["car"], "#e9f7ef"),
        ("5000+", t["s3"], _LAND_ICONS["users"], "#f4eefc"),
        (f"{avg}", t["s4"], _LAND_ICONS["star"], "#fdf6e3"),
    ]
    stats_html = "".join(
        f'<div class="land-stat"><span class="land-stat-ico" style="background:{bg}">{ico}</span>'
        f'<span class="land-stat-t"><b>{E(v)}</b><span>{E(lbl)}</span></span></div>'
        for v, lbl, ico, bg in stats)
    return (f'<section class="land"><div class="land-shell">'
            f'<div class="land-hero"><div class="land-hero-photo">'
            f'<img class="land-hero-img" src="/assets/rentup-hero2.jpg" alt="" loading="eager" decoding="async">'
            f'<div class="land-hero-fade"></div>'
            f'<div class="land-hero-copy"><h1>{E(t["h1"])}</h1><p>{E(t["lead"])}</p></div></div>'
            f'<div class="land-cards">{cards_html}</div></div>'
            f'<div class="land-stats">{stats_html}</div>'
            f'</div></section>'
            + home_semantic_block(lang))



# ══════════════════════════════════════════════════ სტანდარტული ტურები (/tours/)
TOURS_UI = {
    "ka": ("სტანდარტული ტურები", "მზა მარშრუტები საქართველოს რეგიონებში — რეალური სავალი დროებით და რეკომენდებული ავტომობილით.", "დღე", "ღამე", "კმ", "მართვაში", "ტურის ნახვა", "დამგეგმავში დაგეგმვა"),
    "en": ("Standard tours", "Ready-made routes through the regions of Georgia — with real driving times and a recommended car.", "days", "nights", "km", "driving", "View the tour", "Plan it in the planner"),
    "ru": ("Готовые туры", "Готовые маршруты по регионам Грузии — с реальным временем в пути и рекомендованной машиной.", "дн.", "ноч.", "км", "в пути", "Смотреть тур", "Открыть в планировщике"),
    "fa": ("تورهای آماده", "مسیرهای آماده در مناطق گرجستان — با زمان واقعی رانندگی و خودروی پیشنهادی.", "روز", "شب", "کیلومتر", "رانندگی", "مشاهده تور", "در برنامه‌ریز باز کنید"),
    "he": ("טיולים מוכנים", "מסלולים מוכנים באזורי גאורגיה — עם זמני נסיעה אמיתיים ורכב מומלץ.", "ימים", "לילות", 'ק"מ', "נהיגה", "צפייה בטיול", "פתיחה במתכנן"),
    "ar": ("جولات جاهزة", "مسارات جاهزة في مناطق جورجيا — بأوقات قيادة حقيقية وسيارة مقترحة.", "أيام", "ليالٍ", "كم", "قيادة", "عرض الجولة", "افتح في المخطط"),
}


# ══════════════════════════════════════════ car-rental cluster (/car-rental/)
CAR_RENTAL_SLUG = "car-rental"
RENTAL_PLACES = ["tbilisi", "tbilisi-airport", "kutaisi", "kutaisi-airport",
                 "batumi", "batumi-airport"]
# public URL slug per fleet category key
CATEGORY_SLUG = {"economy": "economy", "suv": "suv", "offroad": "4x4",
                 "minivan": "minivan", "business": "business", "van": "van"}
PLACE_BY_KEY = {p["key"]: p for p in PLACES}


def rental_hub_url(lang, absolute=True):
    p = f"{lang_root(lang)}{CAR_RENTAL_SLUG}/"
    return (SITE_URL + p) if absolute else p


def rental_place_url(lang, key, absolute=True):
    p = f"{lang_root(lang)}{CAR_RENTAL_SLUG}/{key}/"
    return (SITE_URL + p) if absolute else p


def rental_cat_url(lang, cat, absolute=True):
    p = f"{lang_root(lang)}{CAR_RENTAL_SLUG}/{CATEGORY_SLUG.get(cat, cat)}/"
    return (SITE_URL + p) if absolute else p


def _seo_cats():
    return {c["key"]: c for c in (SEO_CATEGORIES.get("seo_categories") or [])}


def rental_quality_ok(kind, payload):
    """Content quality gate — a generated page is only indexable when it
    carries enough genuine data (docs/seo/SEO_VALIDATION.md)."""
    if kind == "location":
        d = payload.get("data") or {}
        return (len(d.get("route_slugs") or []) >= 2
                and len(d.get("category_keys") or []) >= 1
                and len(d.get("nearest_attraction_slugs") or []) >= 3)
    if kind == "category":
        d = payload.get("data") or {}
        return len(d.get("car_slugs") or []) >= 2
    return True


def _car_card(lang, slug):
    c = CARS.get(slug)
    if not c:
        return ""
    L = c[lang]
    price = c.get("price_1_6")
    specs = " · ".join(str(x) for x in [
        f'{c.get("seats")} {su("seats", lang)}' if c.get("seats") else "",
        f'{c.get("luggage")} {su("luggage", lang)}' if c.get("luggage") else "",
        f'{c.get("clearance")} mm' if c.get("clearance") else "",
    ] if x)
    img = (f'<a class="stop-img" href="{car_url(lang, slug, False)}" tabindex="-1" aria-hidden="true">'
           f'<img src="{E(c["image"])}" alt="" loading="lazy"></a>') if c.get("image") else ""
    return (f'<div class="card stop-card">{img}'
            f'<h3><a href="{car_url(lang, slug, False)}">{E(L["name"])}</a></h3>'
            f'<p>{E(specs)}</p>'
            f'<span class="price">{su("price_from", lang)} {price} ₾/{SPECS["units"]["day"][lang]}</span>'
            f'</div>')


def _route_links(lang, slugs, limit=6):
    out = []
    for sl in list(slugs)[:limit]:
        r = ROUTES.get(sl)
        if not r:
            continue
        out.append(f'<li><a href="{route_url(lang, sl, False)}">{E(r[lang]["name"])}</a> '
                   f'<small>{r["days"]} {E(tu(lang, "days"))} · {r["distance_km"]} {E(tu(lang, "km"))}</small></li>')
    return "".join(out)


def _attr_links(lang, slugs, limit=8):
    out = []
    for sl in list(slugs)[:limit]:
        a = ATTRACTIONS.get(sl)
        if not a:
            continue
        out.append(f'<li><a href="{attr_url(lang, sl, False)}">{E(a[lang]["name"])}</a></li>')
    return "".join(out)


def _sec(h, body, alt=False):
    return (f'<section class="sec{" alt" if alt else ""}"><div class="wrap">'
            f'<h2>{E(h)}</h2>{body}</div></section>')


def _faq_html(items):
    return "".join(f'<details class="faq-item"><summary>{E(x["q"])}</summary>'
                   f'<div class="article"><p>{E(x["a"])}</p></div></details>'
                   for x in (items or []))


def _rental_distance_table(lang, key, attr_slugs, limit=6):
    """Real distances from this pickup point to the nearest mapped places.
    Straight-line (great-circle) km — labelled as such, never presented as
    driving distance, because no per-place road distance exists in the data."""
    place = PLACE_BY_KEY.get(key)
    if not place or not attr_slugs:
        return ""
    rows = []
    for sl in attr_slugs[:limit]:
        a = ATTRACTIONS.get(sl)
        if not a:
            continue
        km = _hav(place["lat"], place["lon"], a["lat"], a["lon"])
        rows.append((km, sl, a))
    rows.sort(key=lambda x: x[0])
    if not rows:
        return ""
    body = "".join(
        f'<tr><td><a href="{attr_url(lang, sl, False)}">{E(a[lang]["name"])}</a></td>'
        f'<td>{round(km)} {E(tu(lang, "km"))}</td>'
        f'<td>{E(su("road", lang, a.get("road", "paved")))}</td></tr>'
        for km, sl, a in rows)
    return (f'<div class="tbl-wrap"><table class="spec"><tbody>{body}</tbody></table></div>')


# ── internal-linking graph (computed from real relationships) ─────────────
def _routes_by_attraction():
    idx = {}
    for slug, r in ROUTES.items():
        for w in r.get("waypoints") or []:
            idx.setdefault(w, []).append(slug)
    return idx


ROUTES_BY_ATTRACTION = _routes_by_attraction()


def _itineraries_by_attraction():
    idx = {}
    for slug, it in ITINERARIES.items():
        if not itinerary_quality_ok(it):
            continue
        for d in it.get("plan") or []:
            for w in d.get("stops") or []:
                idx.setdefault(w, []).append(slug)
    return idx


def nearest_rental_place(lat, lon):
    """Which of our pickup points a visitor would actually collect a car from.
    Great-circle, which is enough to pick between Tbilisi, Kutaisi and Batumi."""
    best, best_km = None, None
    for k in RENTAL_PLACES:
        p = PLACE_BY_KEY.get(k)
        if not p or p.get("lat") is None:
            continue
        km = _hav(p["lat"], p["lon"], lat, lon)
        if best_km is None or km < best_km:
            best, best_km = k, km
    return best, best_km


def pickup_link_block(lang, lat, lon):
    """A place page's link to the pickup point that serves it. Without this the
    commercial cluster is a leaf: routes and attractions link *out* to it and
    nothing links back, so it collects no authority."""
    if lat is None or lon is None:
        return ""
    key, km = nearest_rental_place(lat, lon)
    if not key:
        return ""
    loc = (SEO_CAR_RENTAL.get("locations") or {}).get(key) or {}
    if not rental_quality_ok("location", loc):
        return ""
    p = PLACE_BY_KEY.get(key, {})
    name = p.get(lang) or p.get("en", key)
    h1 = (loc.get(lang) or {}).get("h1") or name
    return _sec(su("pickup_locations", lang),
                f'<div class="article"><p>'
                f'<a href="{rental_place_url(lang, key, False)}">{E(h1)}</a> — '
                f'{round(km)} {E(tu(lang, "km"))} ({E(su("straight_line", lang) or "straight line")})'
                f'</p></div>', alt=True)


def attraction_links_block(lang, slug, a):
    """Part-of-these-routes + best-car-for-this-drive + where to pick the car up."""
    out = ""
    rs = ROUTES_BY_ATTRACTION.get(slug) or []
    if rs:
        out += _sec(su("part_of_routes", lang),
                    f'<ul class="linklist">{_route_links(lang, rs, 4)}</ul>')
    cat = a.get("car_category") or "economy"
    road = a.get("road") or "paved"
    if cat in {c["key"] for c in CATS}:
        out += _sec(su("best_car_for_trip", lang),
                    f'<div class="article"><p>{E(su("road", lang, road))}</p>'
                    f'<p><a class="btn ghost" href="{rental_cat_url(lang, cat, False)}">'
                    f'{E(cat_label(cat, lang))} — {E(su("price_from", lang))} '
                    f'{cheapest_price(cat)} ₾/{E(SPECS["units"]["day"][lang])}</a></p></div>', alt=True)
    out += guide_links_block(lang, guides_for_place(a))
    out += pickup_link_block(lang, a.get("lat"), a.get("lon"))
    return out


def route_links_block(lang, slug, r):
    """Recommended vehicle + open-in-planner + itineraries that include it."""
    cat = r.get("car_category") or "economy"
    out = _sec(su("best_car_for_trip", lang),
               f'<div class="article"><p><a class="btn ghost" '
               f'href="{rental_cat_url(lang, cat, False)}">{E(cat_label(cat, lang))} — '
               f'{E(su("price_from", lang))} {cheapest_price(cat)} ₾/'
               f'{E(SPECS["units"]["day"][lang])}</a></p></div>')
    # The specific cars in that class, not just the class page — a visitor
    # deciding on a route wants to see the actual vehicle.
    cars_in_cat = [s for s, c in CARS.items() if c.get("category") == cat][:3]
    if cars_in_cat:
        out += _sec(su("cars_in_category", lang) or UI[lang]["nav"]["fleet"],
                    f'<div class="cards">{"".join(_car_card(lang, s) for s in cars_in_cat)}</div>')
    its = ITINERARIES_BY_ATTRACTION_ROUTES.get(slug) or []
    if its:
        cards = "".join(
            f'<li><a href="{itin_url(lang, sl, False)}">{E(ITINERARIES[sl][lang]["name"])}</a> '
            f'<small>{ITINERARIES[sl]["days"]} {E(tu(lang, "days"))}</small></li>'
            for sl in its if ITINERARIES.get(sl, {}).get(lang))
        if cards:
            out += _sec(su("itineraries", lang), f'<ul class="linklist">{cards}</ul>', alt=True)
    # Where the trip actually starts from.
    out += guide_links_block(lang, guides_for_place(
        {"car_category": r.get("car_category"), "best_season": r.get("best_season")}), alt=True)
    wps = [w for w in (r.get("waypoints") or []) if w in ATTRACTIONS]
    if wps:
        a0 = ATTRACTIONS[wps[0]]
        out += pickup_link_block(lang, a0.get("lat"), a0.get("lon"))
    return out


def policy_facts(lang):
    """Rental terms as a real table, straight from content/settings/rental_policy.yml.

    This is the single place the owner edits a commercial term. It renders as a
    visible table (so it is honest and extractable) and the same values feed the
    JSON-LD, so a search engine and an AI assistant read exactly what a customer
    sees. Every row is omitted when the underlying value is absent — the file is
    the source of truth, not the template."""
    P = RENTAL_POLICY
    if not P:
        return []
    gel = SPECS["units"].get("gel", {}).get(lang, "₾")
    day = SPECS["units"]["day"][lang]
    rows = []

    def add(key, value):
        if value:
            rows.append((su(key, lang) or key.replace("_", " ").capitalize(), value))

    if P.get("min_driver_age"):
        v = f'{P["min_driver_age"]}+'
        if P.get("min_licence_years"):
            v += f' · {P["min_licence_years"]}+ {su("licence_years", lang) or "years licence"}'
        add("min_driver_age", v)
    if (P.get("mileage") or {}).get("unlimited"):
        add("mileage", su("mileage_unlimited", lang) or "Unlimited")
    if P.get("fuel_policy"):
        add("fuel_policy", su("fuel", lang, P["fuel_policy"]) or P["fuel_policy"].replace("_", " "))
    ins = P.get("insurance") or {}
    if ins.get("included"):
        v = su("insurance_kind", lang, ins["included"]) or ins["included"].upper().replace("_", " + ")
        if ins.get("excess_gel"):
            v += f' · {su("excess", lang) or "excess"} {ins["excess_gel"]} {gel}'
        add("insurance", v)
    dep = P.get("deposit") or {}
    if dep.get("released_days"):
        add("deposit", f'{su("deposit_" + str(dep.get("method", "card_hold")), lang) or "card hold"}'
                       f' · {dep["released_days"]} {su("working_days", lang) or "working days"}')
    can = P.get("cancellation") or {}
    if can.get("free_until_hours"):
        add("cancellation", f'{su("free_until", lang) or "Free until"} '
                            f'{can["free_until_hours"]} {su("hours_before", lang) or "h before pickup"}')
    if can.get("prepayment_required") is False:
        add("payment", su("pay_at_pickup", lang) or "Pay at pickup")
    if P.get("max_rental_days") is None and P.get("min_rental_days"):
        add("rental_length", su("no_max_duration", lang) or "From 1 day, no maximum")
    yd = P.get("young_driver") or {}
    if yd.get("applies") and yd.get("bands"):
        v = " · ".join(f'{b["min_age"]}-{b["max_age"]}: {b["fee_gel_per_day"]} {gel}/{day}'
                       for b in yd["bands"])
        add("young_driver", v)
    if (P.get("support") or {}).get("roadside_assistance"):
        v = "24/7" if (P["support"].get("hours_key") == "always") else (su("office_hours", lang) or "")
        add("roadside_assistance", v)
    return rows


def policy_table_html(lang):
    rows = policy_facts(lang)
    if not rows:
        return ""
    body = "".join(f'<tr><td>{E(k)}</td><td>{E(v)}</td></tr>' for k, v in rows)
    return f'<div class="tbl-wrap"><table class="spec"><tbody>{body}</tbody></table></div>'


def render_car_rental_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    h = (SEO_CAR_RENTAL.get("hub") or {}).get(lang) or {}
    if not h:
        return None
    sec = h.get("sections") or {}
    cats = _seo_cats()
    order = [k for k in SEO_CATEGORY_ORDER if k in cats]
    cat_cards = "".join(
        f'<div class="card"><h3><a href="{rental_cat_url(lang, k, False)}">'
        f'{E((cats[k].get(lang) or {}).get("h1", cat_label(k, lang)))}</a></h3>'
        f'<p>{E((cats[k].get(lang) or {}).get("lead", ""))}</p>'
        f'<span class="price">{su("price_from", lang)} '
        f'{cats[k]["data"].get("price_from_gel", cheapest_price(k))} ₾/{SPECS["units"]["day"][lang]}</span></div>'
        for k in order if rental_quality_ok("category", cats[k]))
    loc_links = "".join(
        f'<li><a href="{rental_place_url(lang, k, False)}">'
        f'{E(((SEO_CAR_RENTAL.get("locations") or {}).get(k, {}).get(lang) or {}).get("h1", k))}</a></li>'
        for k in RENTAL_PLACES
        if rental_quality_ok("location", (SEO_CAR_RENTAL.get("locations") or {}).get(k, {})))
    fleet_preview = "".join(_car_card(lang, s) for s in list(CARS)[:6])
    order_keys = ["intro", "how_it_works", "requirements", "deposit_explained", "mileage",
                  "fuel", "insurance", "delivery", "one_way", "extras", "cancellation", "support"]
    prose = ""
    for k in order_keys:
        v = sec.get(k)
        if not v:
            continue
        if isinstance(v, list):
            inner = "<ol>" + "".join(f"<li>{E(x)}</li>" for x in v) + "</ol>"
        elif isinstance(v, dict):
            inner = (f'<p>{E(v.get("body", ""))}</p>' if v.get("body") else "")
            k_head = v.get("heading")
        else:
            inner = f"<p>{E(v)}</p>"
        head = (v.get("heading") if isinstance(v, dict) else None) or su(k, lang) or k.replace("_", " ").title()
        prose += _sec(head, f'<div class="article">{inner}</div>', alt=(len(prose) // 900) % 2 == 1)
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(h.get("h1", ""))}</h1>'
        f'<p class="lead">{E(h.get("lead", ""))}</p></div></section>'
        + _sec(su("cars_in_category", lang) or u["nav"]["fleet"],
               f'<div class="cards">{cat_cards}</div>')
        + _sec(su("pickup_locations", lang), f'<ul class="linklist">{loc_links}</ul>', alt=True)
        + _sec(u["nav"]["fleet"], f'<div class="cards">{fleet_preview}</div>'
               f'<p><a class="btn ghost" href="{page_url(lang, "fleet", False)}">'
               f'{su("see_all_cars", lang)}</a></p>')
        + prose
        + (_sec(su("rental_terms", lang) or "Rental terms", policy_table_html(lang), alt=True)
           if policy_facts(lang) else "")
        + guide_links_block(lang, list(GUIDES))
        + (_sec("FAQ", f'<div class="faq">{_faq_html(h.get("faq"))}</div>', alt=True)
           if h.get("faq") else "")
    )
    _tt, _td = seo_meta("car_rental_hub", lang, count=len(CARS), price=cheapest_price("economy"))
    title = h.get("meta_title") or _tt or f'{h.get("h1", "")} | {BRAND}'
    desc = h.get("meta_description") or _td or ""
    title = _trim_title(title)
    url = rental_hub_url(lang)
    graph = [org_node(lang), website_node(lang),
             {"@type": "WebPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             {"@type": "ItemList", "name": h.get("h1", ""),
              "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "url": rental_cat_url(lang, k),
                   "name": (cats[k].get(lang) or {}).get("h1", k)}
                  for i, k in enumerate(order)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (h.get("h1", "Car rental"), url)])]
    _fq = faq_items_node(h.get("faq"))
    if _fq:
        graph.append(_fq)
    head = head_html(lang, "fleet", title, desc, "", url,
                     {l: rental_hub_url(l) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (h.get("h1", "Car rental"), None)])
    return shell(lang, "fleet", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_rental_location(lang, key):
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    loc = (SEO_CAR_RENTAL.get("locations") or {}).get(key) or {}
    L = loc.get(lang) or {}
    if not L or not rental_quality_ok("location", loc):
        return None
    d = loc.get("data") or {}
    place = PLACE_BY_KEY.get(key, {})
    hub_h1 = ((SEO_CAR_RENTAL.get("hub") or {}).get(lang) or {}).get("h1", "Car rental")
    gtk = "".join(f"<li>{E(x)}</li>" for x in (L.get("good_to_know") or []))
    cat_cards = "".join(
        f'<div class="card"><h3><a href="{rental_cat_url(lang, k, False)}">'
        f'{E(cat_label(k, lang))}</a></h3>'
        f'<span class="price">{su("price_from", lang)} {cheapest_price(k)} ₾/'
        f'{SPECS["units"]["day"][lang]}</span></div>'
        for k in (d.get("category_keys") or []))
    # The airport template already says "Airport"; feed the bare city name so we
    # never render "Tbilisi Airport Airport Car Rental".
    _city_key = key.replace("-airport", "")
    _city_place = PLACE_BY_KEY.get(_city_key) or place
    _city = _city_place.get(lang) or _city_place.get("en", _city_key)
    # Heading strings such as "Popular road trips from {place}" take the full
    # place name, declined for Georgian.
    _place_label = place.get(lang) or place.get("en", key)
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L.get("h1", ""))}</h1>'
        f'<p class="lead">{E(L.get("lead", ""))}</p></div></section>'
        + _sec(su("pickup_locations", lang), f'<div class="article"><p>{E(L.get("pickup", ""))}</p></div>')
        + (_sec(su("popular_routes_from", lang, place=_place_label, place_abl=ka_case(_place_label, "abl")),
                f'<ul class="linklist">{_route_links(lang, d.get("route_slugs") or [])}</ul>'
                + _rental_distance_table(lang, key, d.get("nearest_attraction_slugs") or []), alt=True)
           if d.get("route_slugs") else "")
        + _sec(su("best_car_for_trip", lang), f'<div class="cards">{cat_cards}</div>')
        + (_sec(su("nearby_places", lang),
                f'<ul class="linklist">{_attr_links(lang, d.get("nearest_attraction_slugs") or [])}</ul>', alt=True)
           if d.get("nearest_attraction_slugs") else "")
        + _sec(u["nav"].get("faq", "Good to know"),
               f'<div class="article"><p>{E(L.get("getting_around", ""))}</p><ul>{gtk}</ul></div>')
        + f'<section class="sec"><div class="wrap"><div class="cta">'
          f'<h2>{E(su("request_booking", lang))}</h2>'
          f'<div class="row"><a class="btn" href="{page_url(lang, "contact", False)}">'
          f'{E(u["nav"]["contact"])}</a>'
          f'<a class="btn ghost" href="{rental_hub_url(lang, False)}">{E(hub_h1)}</a>'
          f'</div></div></div></section>'
    )
    kind = "airport" if place.get("kind") == "airport" else "city"
    title, desc = seo_meta("car_rental_location", lang, kind=kind,
                           city=_city,
                           name=place.get(lang, place.get("en", key)),
                           iata={"tbilisi-airport": "TBS", "kutaisi-airport": "KUT",
                                 "batumi-airport": "BUS"}.get(key, ""))
    title = L.get("meta_title") or title or f'{L.get("h1", "")} | {BRAND}'
    desc = L.get("meta_description") or desc or ""
    title = _trim_title(title)
    url = rental_place_url(lang, key)
    graph = [org_node(lang), website_node(lang),
             {"@type": "WebPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang,
              **({"about": {"@type": "Place", "name": place.get(lang, key),
                            "geo": {"@type": "GeoCoordinates", "latitude": place["lat"],
                                    "longitude": place["lon"]}}}
                 if place.get("lat") else {})},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (hub_h1, rental_hub_url(lang)),
                                (L.get("h1", key), url)])]
    _fq = faq_items_node(L.get("faq"))
    if _fq:
        graph.append(_fq)
    head = head_html(lang, "fleet", title, desc, "", url,
                     {l: rental_place_url(l, key) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (hub_h1, rental_hub_url(lang, False)),
                                (L.get("h1", key), None)])
    return shell(lang, "fleet", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_rental_category(lang, key):
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    cat = _seo_cats().get(key) or {}
    L = cat.get(lang) or {}
    if not L or not rental_quality_ok("category", cat):
        return None
    d = cat.get("data") or {}
    hub_h1 = ((SEO_CAR_RENTAL.get("hub") or {}).get(lang) or {}).get("h1", "Car rental")
    cars_html = "".join(_car_card(lang, s) for s in (d.get("car_slugs") or []))
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L.get("h1", ""))}</h1>'
        f'<p class="lead">{E(L.get("lead", ""))}</p></div></section>'
        + _sec(su("all_cars_in_class", lang) or u["nav"]["fleet"], f'<div class="cards">{cars_html}</div>')
        + _sec(su("best_car_for_trip", lang),
               f'<div class="article"><p>{E(L.get("when_to_choose", ""))}</p></div>', alt=True)
        + _sec(su("rental_terms", lang),
               f'<div class="article"><p>{E(L.get("limitations", ""))}</p>'
               f'<p>{E(L.get("terms_note", ""))}</p></div>')
        + (_sec(su("routes_needing_this_car", lang),
                f'<ul class="linklist">{_route_links(lang, d.get("route_slugs") or [], 8)}</ul>', alt=True)
           if d.get("route_slugs") else "")
        + (_sec(su("attractions_for_this_car", lang),
                f'<ul class="linklist">{_attr_links(lang, d.get("attraction_slugs") or [])}</ul>')
           if d.get("attraction_slugs") else "")
        + (_sec("FAQ", f'<div class="faq">{_faq_html(L.get("faq"))}</div>', alt=True)
           if L.get("faq") else "")
    )
    title, desc = seo_meta("car_rental_category", lang,
                           category=cat_label(key, lang), name=cat_label(key, lang),
                           count=len(d.get("car_slugs") or []),
                           price=d.get("price_from_gel", cheapest_price(key)))
    title = L.get("meta_title") or title or f'{L.get("h1", "")} | {BRAND}'
    desc = L.get("meta_description") or desc or ""
    title = _trim_title(title)
    url = rental_cat_url(lang, key)
    graph = [org_node(lang), website_node(lang),
             {"@type": "WebPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             {"@type": "ItemList", "numberOfItems": len(d.get("car_slugs") or []),
              "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "url": car_url(lang, s),
                   "name": CARS[s][lang]["name"]}
                  for i, s in enumerate(d.get("car_slugs") or []) if s in CARS]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (hub_h1, rental_hub_url(lang)),
                                (L.get("h1", key), url)])]
    _fq = faq_items_node(L.get("faq"))
    if _fq:
        graph.append(_fq)
    head = head_html(lang, "fleet", title, desc, "", url,
                     {l: rental_cat_url(l, key) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (hub_h1, rental_hub_url(lang, False)),
                                (L.get("h1", key), None)])
    return shell(lang, "fleet", head, crumbs + f'<main id="main">{body}</main>', depth)


# ══════════════════════════════════════ itineraries + trip-planner landing
def itin_hub_url(lang, absolute=True):
    p = f"{lang_root(lang)}itineraries/"
    return (SITE_URL + p) if absolute else p


def itin_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}itineraries/{slug}/"
    return (SITE_URL + p) if absolute else p


def planner_landing_url(lang, absolute=True):
    p = f"{lang_root(lang)}trip-planner/"
    return (SITE_URL + p) if absolute else p


def itinerary_quality_ok(it):
    plan = it.get("plan") or []
    stops = {s for d in plan for s in (d.get("stops") or [])}
    return (len(plan) >= 3
            # a rest day legitimately has km == 0 — require presence, not truthiness
            and all(d.get("to") and d.get("km") is not None and d.get("drive") for d in plan)
            and (it.get("total_km") or 0) > 0
            and len(stops) >= 5)


def _place_name(lang, key):
    p = PLACE_BY_KEY.get(key)
    if p:
        return p.get(lang) or p.get("en") or key
    a = ATTRACTIONS.get(key)
    if a:
        return a[lang]["name"]
    return key


def _itin_pickup_block(lang, it):
    """Link the trip back to the pickup point it starts from — otherwise the
    commercial pages receive no links from the planning cluster at all."""
    key = it.get("start", "")
    if key not in RENTAL_PLACES:
        p = PLACE_BY_KEY.get(key) or {}
        if p.get("lat") is None:
            return ""
        return pickup_link_block(lang, p["lat"], p["lon"])
    loc = (SEO_CAR_RENTAL.get("locations") or {}).get(key) or {}
    if not rental_quality_ok("location", loc):
        return ""
    h1 = (loc.get(lang) or {}).get("h1") or _place_name(lang, key)
    return _sec(su("pickup_locations", lang),
                f'<div class="article"><p>'
                f'<a href="{rental_place_url(lang, key, False)}">{E(h1)}</a></p></div>', alt=True)


def render_itinerary(lang, slug, it):
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    L = it.get(lang) or {}
    if not L or not itinerary_quality_ok(it):
        return None
    hub_h1 = su("itineraries", lang) or "Itineraries"
    facts = [
        (tu(lang, "days"), f'{it["days"]}'),
        (su("total_distance", lang), f'{it["total_km"]} {tu(lang, "km")}'),
        (su("total_drive", lang), it["total_drive"]),
        (su("recommended_car", lang), car_cat_label(it.get("car_category", "economy"), lang)),
        (su("best_season", lang), su("season", lang, it.get("best_season", "all")) or it.get("best_season", "")),
        (su("start_point", lang), _place_name(lang, it.get("start", ""))),
    ]
    fh = ('<dl class="facts">' + "".join(
        f'<div><dt class="k">{E(k)}</dt><dd class="v">{E(v)}</dd></div>' for k, v in facts if v) + "</dl>")
    days_html = ""
    for d in it.get("plan") or []:
        stops = "".join(
            f'<li><a href="{attr_url(lang, sl, False)}">{E(ATTRACTIONS[sl][lang]["name"])}</a></li>'
            for sl in (d.get("stops") or []) if sl in ATTRACTIONS)
        days_html += (
            f'<div class="trip-day"><h3>{E(su("day", lang))} {d["day"]} — '
            f'{E(_place_name(lang, d.get("from", "")))} → {E(_place_name(lang, d.get("to", "")))} '
            f'<small>{d["km"]} {E(tu(lang, "km"))} · {E(d["drive"])}</small></h3>'
            f'<ul>{stops}</ul>'
            f'<p class="pshort">{E(su("overnight", lang))}: {E(_place_name(lang, d.get("overnight", "")))}'
            f' · {E(su("road", lang, d.get("road", "paved")))}</p></div>')
    tips = "".join(f"<li>{inline(t, lang)}</li>" for t in (L.get("tips") or []))
    tour_hash = ",".join(
        sl for d in (it.get("plan") or []) for sl in (d.get("stops") or []) if sl in ATTRACTIONS)
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L.get("name", ""))}</h1>'
        f'<p class="lead">{E(L.get("short", ""))}</p></div></section>'
        f'<section class="sec"><div class="wrap">{fh}'
        f'<div class="article">{render_md(L.get("body", ""), lang)}</div></div></section>'
        + _sec(su("day_by_day", lang), f'<div class="trip-days">{days_html}</div>', alt=True)
        + (_sec(tu(lang, "tips_title"), f"<ul>{tips}</ul>") if tips else "")
        + _itin_pickup_block(lang, it)
        + _sec(su("routes_needing_this_car", lang) or tu(lang, "routes"),
               f'<ul class="linklist">{_route_links(lang, it.get("route_slugs") or [], 6)}</ul>', alt=True)
        + f'<section class="sec"><div class="wrap"><div class="cta">'
          f'<h2>{E(su("customize_this_trip", lang))}</h2><div class="row">'
          f'<a class="btn" href="{page_url(lang, "map", False)}#trip='
          f'{tour_hash}">{E(su("open_in_planner", lang))}</a>'
          f'<a class="btn ghost" href="{rental_cat_url(lang, it.get("car_category", "economy"), False)}">'
          f'{E(su("rent_car_for_trip", lang))}</a></div></div></div></section>'
    )
    title, desc = seo_meta("itinerary", lang, days=it["days"], km=it["total_km"],
                           drive=it["total_drive"], name=L.get("name", ""),
                           stops=sum(len(d.get("stops") or []) for d in (it.get("plan") or [])),
                           start=_place_name(lang, it.get("start", "")),
                           end=_place_name(lang, it.get("end", "")),
                           car=car_cat_label(it.get("car_category", "economy"), lang))
    title = title or f'{L.get("name", "")} | {BRAND}'
    desc = desc or L.get("short", "")
    url = itin_url(lang, slug)
    graph = [org_node(lang), website_node(lang),
             {"@type": "TouristTrip", "@id": url + "#trip", "name": L.get("name", ""),
              "description": L.get("short", ""), "url": url,
              "provider": {"@id": SITE_URL + "/#organization"},
              "itinerary": {"@type": "ItemList", "itemListElement": [
                  {"@type": "ListItem", "position": i + 1,
                   "item": {"@type": "TouristAttraction", "name": ATTRACTIONS[sl][lang]["name"],
                            "url": attr_url(lang, sl)}}
                  for i, sl in enumerate(dict.fromkeys(
                      sl for d in (it.get("plan") or []) for sl in (d.get("stops") or [])
                      if sl in ATTRACTIONS))]}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (hub_h1, itin_hub_url(lang)), (L.get("name", ""), url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: itin_url(l, slug) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (hub_h1, itin_hub_url(lang, False)), (L.get("name", ""), None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


# ── /guides/ — evergreen decision guides built from the attraction dataset ──
def guides_hub_url(lang, absolute=True):
    p = f"{lang_root(lang)}guides/"
    return (SITE_URL + p) if absolute else p


def guide_url(lang, slug, absolute=True):
    p = f"{lang_root(lang)}guides/{slug}/"
    return (SITE_URL + p) if absolute else p


def guide_quality_ok(g, lang):
    """A guide is only indexable once it has a real article behind it — the
    same bar the rest of the generated clusters are held to."""
    L = g.get(lang) or {}
    return bool(L.get("name") and L.get("body") and len(L["body"]) >= 1500
                and L.get("meta_description"))


def _guide_related(lang, g):
    out = ""
    rs = [s for s in (g.get("related_routes") or []) if s in ROUTES]
    if rs:
        out += _sec(su("part_of_routes", lang) or tu(lang, "routes"),
                    f'<ul class="linklist">{_route_links(lang, rs, 6)}</ul>')
    at = [s for s in (g.get("related_attractions") or []) if s in ATTRACTIONS]
    if at:
        out += _sec(su("nearby_places", lang) or tu(lang, "attractions"),
                    f'<ul class="linklist">{_attr_links(lang, at, 8)}</ul>', alt=True)
    cat = g.get("car_category")
    if cat and cat in {c["key"] for c in CATS}:
        out += _sec(su("best_car_for_trip", lang),
                    f'<div class="article"><p><a class="btn ghost" '
                    f'href="{rental_cat_url(lang, cat, False)}">{E(cat_label(cat, lang))} — '
                    f'{E(su("price_from", lang))} {cheapest_price(cat)} ₾/'
                    f'{E(SPECS["units"]["day"][lang])}</a></p></div>')
    return out


def guide_links_block(lang, slugs, alt=False):
    """Contextual links into /guides/. Guides answer the question a visitor has
    *before* they pick a car, so every place and route page should offer the one
    that matches its own data."""
    items = [(sl, GUIDES[sl]) for sl in slugs
             if sl in GUIDES and guide_quality_ok(GUIDES[sl], lang)]
    if not items:
        return ""
    li = "".join(
        f'<li><a href="{guide_url(lang, sl, False)}">{E(g[lang]["name"])}</a> '
        f'<small>{E(g[lang].get("short", "")[:110])}</small></li>'
        for sl, g in items)
    return _sec(su("guides", lang) or "Guides", f'<ul class="linklist">{li}</ul>', alt=alt)


def guides_for_place(a):
    """Which guides actually answer this place's own question."""
    out = []
    if (a.get("road") in ("gravel", "4x4_only")) or a.get("car_category") == "offroad":
        out.append("do-i-need-a-4x4-in-georgia")
    if (a.get("best_season") or "all") != "all" or a.get("open_year_round") is False:
        out.append("best-time-to-visit-georgia")
    out.append("driving-in-georgia")
    return list(dict.fromkeys(out))[:2]


def image_object(url, credit, name=""):
    """A Licensable ImageObject, but only when the credit is genuinely complete.

    994 of the site's photos already carry author, licence and source in YAML and
    render that credit visibly under the photo — so the markup states exactly
    what the page states. A photo without a real licence URL is left as a plain
    src, never dressed up with invented rights metadata."""
    credit = credit or {}
    src = abs_url(url)
    if not src or not credit.get("license_url"):
        return None
    node = {"@type": "ImageObject", "@id": src + "#image", "contentUrl": src, "url": src,
            "license": credit["license_url"],
            "acquireLicensePage": credit.get("source") or credit["license_url"]}
    if credit.get("author"):
        node["creditText"] = credit["author"]
        node["author"] = {"@type": "Person", "name": credit["author"]}
    if credit.get("license"):
        node["copyrightNotice"] = credit["license"]
    if name:
        node["name"] = name
    return node


def render_guide(lang, slug, g):
    u = UI[lang]
    depth = 2 if lang == ROOT_LANG else 3
    L = g.get(lang) or {}
    if not guide_quality_ok(g, lang):
        return None
    hub_h1 = su("guides", lang) or "Guides"
    faq = L.get("faq") or []
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L.get("short", ""))}</p></div></section>'
        f'<section class="sec"><div class="wrap"><div class="article">'
        f'{render_md(L["body"], lang)}</div></div></section>'
        + _guide_related(lang, g)
        + (_sec("FAQ", f'<div class="faq">{_faq_html(faq)}</div>', alt=True) if faq else "")
        + f'<section class="sec"><div class="wrap"><div class="cta">'
          f'<h2>{E(su("request_booking", lang))}</h2>'
          f'<div class="row"><a class="btn" href="{rental_hub_url(lang, False)}">'
          f'{E(((SEO_CAR_RENTAL.get("hub") or {}).get(lang) or {}).get("h1", u["nav"]["fleet"]))}</a>'
          f'<a class="btn ghost" href="{planner_landing_url(lang, False)}">'
          f'{E(su("open_in_planner", lang))}</a></div></div></div></section>'
    )
    title = _trim_title(L.get("meta_title") or f'{L["name"]} | {BRAND}')
    desc = L.get("meta_description", "")
    url = guide_url(lang, slug)
    graph = [org_node(lang), website_node(lang),
             {"@type": "Article", "@id": url + "#article", "headline": L["name"],
              "description": desc, "url": url, "inLanguage": lang,
              "author": {"@id": SITE_URL + "/#organization"},
              "publisher": {"@id": SITE_URL + "/#organization"},
              "mainEntityOfPage": url,
              **({"dateModified": g["updated"]} if g.get("updated") else {}),
              **({"image": abs_url(g["image"])} if g.get("image") else {})},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (hub_h1, guides_hub_url(lang)), (L["name"], url)])]
    _fq = faq_items_node(faq)
    if _fq:
        graph.append(_fq)
    head = head_html(lang, "map", title, desc, "", url,
                     {l: guide_url(l, slug) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (hub_h1, guides_hub_url(lang, False)), (L["name"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


# ── /attractions/, /routes/, /regions/ — the index hubs ────────────────────
# These URLs are live and indexed today but the generator never wrote them, so
# they 404. They also fix the depth problem: 108 attractions sat 4-5 clicks from
# the home page because /map/ is a JavaScript interface with no crawlable list.
def index_hub_url(lang, kind, absolute=True):
    p = f"{lang_root(lang)}{kind}/"
    return (SITE_URL + p) if absolute else p


def render_attractions_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    hub_h1 = tu(lang, "attractions") or "Attractions"
    by_region = {}
    for sl, a in ATTRACTIONS.items():
        by_region.setdefault(a["region"], []).append((sl, a))
    secs = ""
    for rk in REGIONS:
        rows = sorted(by_region.get(rk, []), key=lambda kv: kv[1][lang]["name"])
        if not rows:
            continue
        body = "".join(
            f'<tr><td><a href="{attr_url(lang, sl, False)}">{E(a[lang]["name"])}</a></td>'
            f'<td>{a["distance_tbilisi_km"]} {E(tu(lang, "km"))}</td>'
            f'<td>{E(a["drive_time_tbilisi"])}</td>'
            f'<td>{E(su("road", lang, a.get("road", "paved")))}</td>'
            f'<td>{E(car_cat_label(a.get("car_category", "economy"), lang))}</td></tr>'
            for sl, a in rows)
        head = (f'<tr><th>{E(hub_h1)}</th><th>{E(tu(lang, "from_tbilisi"))}</th>'
                f'<th>{E(tu(lang, "drive_time"))}</th><th>{E(su("road_surface", lang))}</th>'
                f'<th>{E(su("car_needed", lang))}</th></tr>')
        secs += _sec(f'<a href="{region_url(lang, rk, False)}">{E(REGIONS[rk][lang]["name"])}</a>',
                     f'<div class="tbl-wrap"><table class="spec"><thead>{head}</thead>'
                     f'<tbody>{body}</tbody></table></div>',
                     alt=(len(secs) // 900) % 2 == 1)
    title, desc = seo_meta("attractions_hub", lang, count=len(ATTRACTIONS),
                           regions=len(REGIONS))
    title = title or f'{hub_h1} | {BRAND}'
    lead = su("attractions_hub_lead", lang) or desc
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(hub_h1)}</h1>'
            f'<p class="lead">{E(lead)}</p></div></section>' + secs
            + guide_links_block(lang, list(GUIDES), alt=True))
    url = index_hub_url(lang, "attractions")
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (hub_h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: index_hub_url(l, "attractions") for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (hub_h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_routes_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    hub_h1 = tu(lang, "routes") or "Road trips"
    rows = sorted(ROUTES.items(), key=lambda kv: (kv[1].get("days", 0), kv[1][lang]["name"]))
    body_rows = "".join(
        f'<tr><td><a href="{route_url(lang, sl, False)}">{E(r[lang]["name"])}</a></td>'
        f'<td>{r["days"]} {E(tu(lang, "days"))}</td>'
        f'<td>{r["distance_km"]} {E(tu(lang, "km"))}</td>'
        f'<td>{E(r["drive_time_total"])}</td>'
        f'<td><a href="{rental_cat_url(lang, r.get("car_category", "economy"), False)}">'
        f'{E(car_cat_label(r.get("car_category", "economy"), lang))}</a></td></tr>'
        for sl, r in rows)
    head_row = (f'<tr><th>{E(hub_h1)}</th><th>{E(tu(lang, "days"))}</th>'
                f'<th>{E(tu(lang, "km"))}</th><th>{E(tu(lang, "drive_time"))}</th>'
                f'<th>{E(su("car_needed", lang))}</th></tr>')
    title, desc = seo_meta("routes_hub", lang, count=len(ROUTES))
    title = title or f'{hub_h1} | {BRAND}'
    lead = su("routes_hub_lead", lang) or desc
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(hub_h1)}</h1>'
            f'<p class="lead">{E(lead)}</p></div></section>'
            + _sec(hub_h1, f'<div class="tbl-wrap"><table class="spec"><thead>{head_row}</thead>'
                           f'<tbody>{body_rows}</tbody></table></div>')
            + guide_links_block(lang, list(GUIDES), alt=True))
    url = index_hub_url(lang, "routes")
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             {"@type": "ItemList", "numberOfItems": len(rows), "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": route_url(lang, sl),
                  "name": r[lang]["name"]} for i, (sl, r) in enumerate(rows)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (hub_h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: index_hub_url(l, "routes") for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (hub_h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_regions_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    hub_h1 = tu(lang, "regions") or "Regions"
    counts = {k: sum(1 for a in ATTRACTIONS.values() if a["region"] == k) for k in REGIONS}
    cards = "".join(
        f'<div class="card"><h3><a href="{region_url(lang, k, False)}">'
        f'{E(REGIONS[k][lang]["name"])}</a></h3>'
        f'<p class="meta">{counts[k]} {E(tu(lang, "attractions"))}</p>'
        f'<p>{E(REGIONS[k][lang].get("short", ""))}</p></div>'
        for k in REGIONS)
    title, desc = seo_meta("regions_hub", lang, count=len(REGIONS),
                           attractions=len(ATTRACTIONS))
    title = title or f'{hub_h1} | {BRAND}'
    lead = su("regions_hub_lead", lang) or desc
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(hub_h1)}</h1>'
            f'<p class="lead">{E(lead)}</p></div></section>'
            f'<section class="sec"><div class="wrap"><div class="cards">{cards}</div></div></section>'
            + guide_links_block(lang, list(GUIDES), alt=True))
    url = index_hub_url(lang, "regions")
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             {"@type": "ItemList", "numberOfItems": len(REGIONS), "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": region_url(lang, k),
                  "name": REGIONS[k][lang]["name"]} for i, k in enumerate(REGIONS)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (hub_h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: index_hub_url(l, "regions") for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (hub_h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


# ── /day-trip/ — "I am free today, where do I go?" ─────────────────────────
def day_trip_url(lang, absolute=True):
    p = f"{lang_root(lang)}day-trip/"
    return (SITE_URL + p) if absolute else p


DT_HOURS = ((3, "3h"), (5, "half"), (9, "full"), (12, "long"))


def _dt_reach_table(lang, key):
    """What a visitor can actually reach from one pickup point in a day.
    Static, crawlable, and computed from the same road model the tool uses."""
    place = PLACE_BY_KEY.get(key)
    if not place or place.get("lat") is None:
        return ""
    bands = [(1.5, "1:30"), (3, "3:00"), (5, "5:00")]
    counts = {b[1]: 0 for b in bands}
    for a in ATTRACTIONS.values():
        f, v = road_model(a)
        h = (_hav(place["lat"], place["lon"], a["lat"], a["lon"]) * f) / v
        for lim, lab in bands:
            if h <= lim:
                counts[lab] += 1
    name = place.get(lang) or place.get("en", key)
    return (f'<tr><td>{E(name)}</td>'
            + "".join(f'<td>{counts[lab]}</td>' for _, lab in bands) + "</tr>")


def render_day_trip(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    h1 = su("day_trip_h1", lang) or "What can I do today?"
    lead = su("day_trip_lead", lang) or ""

    cities = "".join(
        f'<button type="button" class="chip" data-dt-city data-la="{PLACE_BY_KEY[k]["lat"]}" '
        f'data-lo="{PLACE_BY_KEY[k]["lon"]}">'
        f'{E(PLACE_BY_KEY[k].get(lang) or PLACE_BY_KEY[k].get("en", k))}</button>'
        for k in RENTAL_PLACES if PLACE_BY_KEY.get(k, {}).get("lat") is not None
        and not k.endswith("-airport"))
    types = sorted({a["type"] for a in ATTRACTIONS.values()},
                   key=lambda t: tl(lang, "type", t))
    tchips = "".join(
        f'<button type="button" class="chip" data-dt-type="{E(t)}">{E(tl(lang, "type", t))}</button>'
        for t in types)
    hchips = "".join(
        f'<button type="button" class="chip{" on" if n == 5 else ""}" data-dt-hours="{n}">'
        f'{E(su("dt_hours", lang, k) or f"{n} h")}</button>' for n, k in DT_HOURS)
    pchips = "".join(
        f'<button type="button" class="chip{" on" if n == 2 else ""}" data-dt-people="{n}">{n}{plus}</button>'
        for n, plus in ((1, ""), (2, ""), (4, ""), (7, "+")))

    rows = "".join(_dt_reach_table(lang, k) for k in RENTAL_PLACES if not k.endswith("-airport"))
    reach = (f'<div class="tbl-wrap"><table class="spec"><thead><tr>'
             f'<th>{E(su("pickup_locations", lang))}</th><th>1:30</th><th>3:00</th><th>5:00</th>'
             f'</tr></thead><tbody>{rows}</tbody></table></div>') if rows else ""

    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(h1)}</h1>'
        f'<p class="lead">{E(lead)}</p></div></section>'
        f'<section class="sec"><div class="wrap"><div id="daytrip" class="dt">'
        f'<div class="dt-row"><span class="dt-label">{E(su("dt_from", lang) or "Starting from")}</span>'
        f'<div class="chips"><button type="button" class="chip" id="dt-geo">'
        f'{E(su("dt_near_me", lang) or "Near me")}</button>{cities}</div></div>'
        f'<div class="dt-row"><span class="dt-label">{E(su("dt_people", lang) or "How many of you")}</span>'
        f'<div class="chips">{pchips}</div></div>'
        f'<div class="dt-row"><span class="dt-label">{E(su("dt_interest", lang) or "What interests you")}</span>'
        f'<div class="chips">{tchips}</div></div>'
        f'<div class="dt-row"><span class="dt-label">{E(su("dt_time", lang) or "How long you have")}</span>'
        f'<div class="chips">{hchips}</div></div>'
        f'<div id="dt-result" class="dt-result"></div>'
        f'</div></div></section>'
        + (_sec(su("dt_reach_title", lang) or "What is within reach", reach, alt=True) if reach else "")
        + guide_links_block(lang, list(GUIDES))
        + f'<section class="sec alt"><div class="wrap"><div class="cta">'
          f'<h2>{E(su("request_booking", lang))}</h2>'
          f'<div class="row"><a class="btn" href="{rental_hub_url(lang, False)}">'
          f'{E(((SEO_CAR_RENTAL.get("hub") or {}).get(lang) or {}).get("h1", u["nav"]["fleet"]))}</a>'
          f'<a class="btn ghost" href="{planner_landing_url(lang, False)}">'
          f'{E(su("open_in_planner", lang))}</a></div></div></div></section>'
    )
    title, desc = seo_meta("day_trip", lang, count=len(ATTRACTIONS))
    title = title or f'{h1} | {BRAND}'
    desc = desc or lead
    url = day_trip_url(lang)
    graph = [org_node(lang), website_node(lang),
             {"@type": "WebApplication", "@id": url + "#app", "name": h1,
              "url": url, "description": desc, "inLanguage": lang,
              "applicationCategory": "TravelApplication",
              "browserRequirements": "Requires JavaScript",
              "offers": {"@type": "Offer", "price": 0, "priceCurrency": "GEL"},
              "provider": {"@id": SITE_URL + "/#organization"}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: day_trip_url(l) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    t = {
        "pick_start": su("dt_pick_start", lang), "nothing": su("dt_nothing", lang),
        "best": su("dt_best", lang), "also": su("dt_also", lang),
        "km": tu(lang, "km"), "h": tu(lang, "hrs"), "drive": su("dt_drive", lang),
        "total_drive": su("total_drive", lang), "total_km": su("total_distance", lang),
        "day_total": su("dt_day_total", lang), "car_needed": su("car_needed", lang),
        "estimate": su("dt_estimate", lang), "open_planner": su("open_in_planner", lang),
        "book_car": su("rent_car_for_trip", lang), "locating": su("dt_locating", lang),
        "you_are_here": su("dt_near_me", lang), "geo_failed": su("dt_geo_failed", lang),
        "planner_url": page_url(lang, "map", False),
        # The shared map index deliberately omits per-place URLs to stay light
        # (tests.test_map_chunking guards that), so build them from the slug.
        "attr_prefix": f"{lang_root(lang)}attractions/",
        # Every fleet category, not just the three the road model recommends:
        # a large group is sent to the minivan, and it must be named in the
        # visitor's own language rather than shown as the raw key.
        "car_urls": {c: rental_cat_url(lang, c, False) for c in SEO_CATEGORY_ORDER},
        "car_names": {c: cat_label(c, lang) for c in SEO_CATEGORY_ORDER},
    }
    js = (f'\n<script src="{TRAVEL_ASSET[lang]}"></script>'
          f'\n<script>window.DAYTRIP_T={JC(t)};</script>'
          f'\n<script defer src="{ASSET.get("daytrip", "/assets/daytrip.js")}"></script>')
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def render_guides_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    items = [(sl, g) for sl, g in sorted(GUIDES.items(), key=lambda kv: kv[1].get("order", 99))
             if guide_quality_ok(g, lang)]
    if not items:
        return None
    hub_h1 = su("guides", lang) or "Guides"
    cards = "".join(
        f'<div class="card"><h3><a href="{guide_url(lang, sl, False)}">'
        f'{E(g[lang]["name"])}</a></h3><p>{E(g[lang].get("short", ""))}</p></div>'
        for sl, g in items)
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(hub_h1)}</h1>'
            f'<p class="lead">{E(su("guides_lead", lang))}</p></div></section>'
            f'<section class="sec"><div class="wrap"><div class="cards">{cards}</div></div></section>')
    title, desc = seo_meta("guides_hub", lang, count=len(items))
    title = title or f'{hub_h1} | {BRAND}'
    desc = desc or su("guides_lead", lang)
    url = guides_hub_url(lang)
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": lang},
             {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": guide_url(lang, sl),
                  "name": g[lang]["name"]} for i, (sl, g) in enumerate(items)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (hub_h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: guides_hub_url(l) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (hub_h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_itineraries_hub(lang):
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    items = [(sl, it) for sl, it in sorted(ITINERARIES.items(), key=lambda kv: kv[1].get("days", 0))
             if itinerary_quality_ok(it) and it.get(lang)]
    if not items:
        return None
    hub_h1 = su("itineraries", lang) or "Itineraries"
    cards = "".join(
        f'<div class="card tour-card"><h3><a href="{itin_url(lang, sl, False)}">'
        f'{E(it[lang]["name"])}</a></h3>'
        f'<p class="tour-meta">{it["days"]} {E(tu(lang, "days"))} · {it["total_km"]} '
        f'{E(tu(lang, "km"))} · {E(it["total_drive"])} · '
        f'{E(car_cat_label(it.get("car_category", "economy"), lang))}</p>'
        f'<p>{E(it[lang].get("short", ""))}</p>'
        f'<div class="row"><a class="btn sm" href="{itin_url(lang, sl, False)}">'
        f'{E(su("day_by_day", lang))}</a></div></div>'
        for sl, it in items)
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(hub_h1)}</h1>'
            f'<p class="lead">{E(su("plan_your_own", lang))}</p></div></section>'
            f'<section class="sec"><div class="wrap"><div class="cards tours-grid">{cards}</div></div></section>')
    title, desc = seo_meta("itineraries_hub", lang, count=len(items))
    title = title or f'{hub_h1} | {BRAND}'
    url = itin_hub_url(lang)
    graph = [org_node(lang), website_node(lang),
             {"@type": "CollectionPage", "@id": url + "#webpage", "url": url,
              "name": title, "description": desc},
             {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": itin_url(lang, sl),
                  "name": it[lang]["name"]} for i, (sl, it) in enumerate(items)]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")), (hub_h1, url)])]
    head = head_html(lang, "map", title, desc, "", url,
                     {l: itin_hub_url(l) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)), (hub_h1, None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


def render_planner_landing(lang):
    """/trip-planner/ — crawlable landing for the interactive planner at /map/."""
    u = UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    P = (SEO_TRIP_PLANNER.get("planner") or {}).get(lang) or {}
    if not P:
        return None
    steps = "".join(
        f'<li><b>{E(x.get("title", ""))}</b> — {E(x.get("body", x.get("text", "")))}</li>'
        if isinstance(x, dict) else f"<li>{E(x)}</li>" for x in (P.get("steps") or []))
    feats = "".join(f"<li>{E(x)}</li>" for x in (P.get("features") or []))
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(P.get("h1", ""))}</h1>'
        f'<p class="lead">{E(P.get("lead", ""))}</p></div></section>'
        + _sec(su("how_it_works", lang) or "How it works",
               f'<div class="article"><p>{E(P.get("what_it_does", ""))}</p><ol>{steps}</ol></div>')
        + _sec(su("trip_planner", lang), f"<ul>{feats}</ul>", alt=True)
        + (f'<section class="sec"><div class="wrap"><div class="article">'
           f'<p>{E(P.get("for_whom", ""))}</p></div></div></section>' if P.get("for_whom") else "")
        + _sec(su("ready_made_routes", lang),
               f'<ul class="linklist">{_route_links(lang, list(ROUTES)[:8], 8)}</ul>'
               f'<p><a class="btn ghost" href="{lang_root(lang)}tours/">{E(su("ready_made_routes", lang))}</a>'
               f' <a class="btn ghost" href="{itin_hub_url(lang, False)}">{E(su("itineraries", lang))}</a></p>', alt=True)
        + _sec(su("day_trip_h1", lang),
               f'<div class="article"><p>{E(su("day_trip_lead", lang))}</p>'
               f'<p><a class="btn ghost" href="{day_trip_url(lang, False)}">'
               f'{E(su("day_trip_h1", lang))}</a></p></div>')
        + guide_links_block(lang, list(GUIDES), alt=True)
        + (_sec("FAQ", f'<div class="faq">{_faq_html(P.get("faq"))}</div>') if P.get("faq") else "")
        + f'<section class="sec alt"><div class="wrap"><div class="cta">'
          f'<h2>{E(P.get("cta_open", ""))}</h2><div class="row">'
          f'<a class="btn" href="{page_url(lang, "map", False)}">{E(P.get("cta_open", ""))}</a>'
          f'<a class="btn ghost" href="{rental_hub_url(lang, False)}">{E(P.get("cta_car", ""))}</a>'
          f'</div></div></div></section>'
    )
    title = P.get("meta_title") or f'{P.get("h1", "")} | {BRAND}'
    desc = P.get("meta_description", "")
    url = planner_landing_url(lang)
    graph = [org_node(lang), website_node(lang),
             {"@type": "WebApplication", "@id": url + "#app", "name": P.get("h1", ""),
              "description": desc, "url": page_url(lang, "map"),
              "applicationCategory": "TravelApplication", "operatingSystem": "Web browser",
              "inLanguage": lang, "isAccessibleForFree": True,
              "provider": {"@id": SITE_URL + "/#organization"}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (P.get("h1", ""), url)])]
    _fq = faq_items_node(P.get("faq"))
    if _fq:
        graph.append(_fq)
    head = head_html(lang, "map", title, desc, "", url,
                     {l: planner_landing_url(l) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (P.get("h1", ""), None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


ITINERARIES_BY_ATTRACTION_ROUTES = {
    rs: [sl for sl, it in ITINERARIES.items()
         if itinerary_quality_ok(it) and rs in (it.get("route_slugs") or [])]
    for rs in ROUTES}


def render_tours_page(lang):
    u = UI[lang]
    t = TOURS_UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    tours = planner_data(lang)["standardTours"]
    cards = "".join(
        f'<div class="card tour-card">'
        + (f'<img src="{E(r["img"])}" alt="" loading="lazy">' if r.get("img") else "")
        + f'<span class="tag">{E(r["carLabel"])}</span>'
        f'<h3><a href="{E(r["u"])}">{E(r["n"])}</a></h3>'
        f'<p class="tour-meta">{r["days"]} {E(t[2])} / {r["nights"]} {E(t[3])} · {r["km"]} {E(t[4])}'
        + (f' · {E(r["drive"])} {E(t[5])}' if r.get("drive") else "")
        + f' · {r["minPeople"]}–{r["maxPeople"]}</p>'
        f'<p>{E(r.get("sh") or "")}</p>'
        f'<div class="row"><a class="btn sm" href="{E(r["u"])}">{E(t[6])}</a>'
        f'<a class="btn ghost sm" href="{page_url(lang, "map", False)}#tour={E(r["s"])}">{E(t[7])}</a></div>'
        f'</div>'
        for r in tours)
    body = (f'<section class="page-head"><div class="wrap"><h1>{E(t[0])}</h1>'
            f'<p class="lead">{E(t[1])}</p></div></section>'
            f'<section class="sec"><div class="wrap"><div class="cards tours-grid">{cards}</div></div></section>'
            + _sec(su("itineraries", lang),
                   f'<p><a class="btn ghost" href="{itin_hub_url(lang, False)}">'
                   f'{E(su("itineraries", lang))}</a> '
                   f'<a class="btn ghost" href="{planner_landing_url(lang, False)}">'
                   f'{E(su("trip_planner", lang))}</a></p>', alt=True))
    title = f'{t[0]} | {BRAND}'
    url = SITE_URL + lang_root(lang) + "tours/"
    head = head_html(lang, "map", title, t[1], "", url,
                     {l: SITE_URL + lang_root(l) + "tours/" for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": [org_node(lang), website_node(lang)]})
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (t[0], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth)


# ══════════════════════════════════════════════════ ჩემი ტური (/trip/)
# მომხმარებლის აგებული მარშრუტი — სტანდარტული ტურის გვერდის სახით.
# გვერდი სტატიკურია: მარშრუტი #trip=... ჰეშიდან იკითხება და ბრაუზერშივე
# ეხატება იმავე მონაცემებით, რითიც დამგეგმავი მუშაობს.
TRIP_UI = {
    "ka": {"h1": "ჩემი მარშრუტი", "lead": "დამგეგმავში აგებული ტური — გაჩერებები, დრო და რეკომენდებული ავტომობილი.",
           "empty": "მარშრუტი ცარიელია", "emptyText": "დაგეგმეთ ტური და დააჭირეთ „ჩემი ტურის ნახვა“.",
           "toPlanner": "დამგეგმავში გახსნა", "stopsW": "გაჩერება", "dayW": "დღე",
           "share": "ბმულის კოპირება", "copied": "ბმული დაკოპირდა ✓", "fromW": "საიდან", "period": "პერიოდი",
           "driveW": "გზაში", "visitW": "დათვალიერება", "backW": "დაბრუნება", "print": "დაბეჭდვა / PDF",
           "routeErr": "გზის სერვისი მიუწვდომელია — ნაჩვენებია პირდაპირი ხაზი", "people": "ადამიანი", "minsW": "წთ"},
    "en": {"h1": "My route", "lead": "A tour built in the planner — stops, timing and the recommended car.",
           "empty": "The route is empty", "emptyText": "Plan a trip and press “View my tour”.",
           "toPlanner": "Open in the planner", "stopsW": "stops", "dayW": "Day",
           "share": "Copy link", "copied": "Link copied ✓", "fromW": "From", "period": "Dates",
           "driveW": "drive", "visitW": "visit", "backW": "Return", "print": "Print / PDF",
           "routeErr": "Routing service unavailable — showing a straight line", "people": "people", "minsW": "min"},
    "ru": {"h1": "Мой маршрут", "lead": "Тур, собранный в планировщике — остановки, время и рекомендуемый автомобиль.",
           "empty": "Маршрут пуст", "emptyText": "Спланируйте поездку и нажмите «Посмотреть мой тур».",
           "toPlanner": "Открыть в планировщике", "stopsW": "остановок", "dayW": "День",
           "share": "Скопировать ссылку", "copied": "Ссылка скопирована ✓", "fromW": "Откуда", "period": "Даты",
           "driveW": "в пути", "visitW": "осмотр", "backW": "Возвращение", "print": "Печать / PDF",
           "routeErr": "Сервис маршрутов недоступен — показана прямая линия", "people": "чел.", "minsW": "мин"},
    "fa": {"h1": "مسیر من", "lead": "توری که در برنامه‌ریز ساخته‌اید — توقف‌ها، زمان و خودروی پیشنهادی.",
           "empty": "مسیر خالی است", "emptyText": "سفری برنامه‌ریزی کنید و «مشاهده تور من» را بزنید.",
           "toPlanner": "باز کردن در برنامه‌ریز", "stopsW": "توقف", "dayW": "روز",
           "share": "کپی پیوند", "copied": "پیوند کپی شد ✓", "fromW": "از", "period": "تاریخ",
           "driveW": "در راه", "visitW": "بازدید", "backW": "بازگشت", "print": "چاپ / PDF",
           "routeErr": "سرویس مسیریابی در دسترس نیست — خط مستقیم نمایش داده می‌شود", "people": "نفر", "minsW": "دقیقه"},
    "he": {"h1": "המסלול שלי", "lead": "טיול שבניתם במתכנן — עצירות, זמנים והרכב המומלץ.",
           "empty": "המסלול ריק", "emptyText": "תכננו טיול ולחצו «צפייה בטיול שלי».",
           "toPlanner": "פתיחה במתכנן", "stopsW": "עצירות", "dayW": "יום",
           "share": "העתקת קישור", "copied": "הקישור הועתק ✓", "fromW": "מ", "period": "תאריכים",
           "driveW": "נסיעה", "visitW": "ביקור", "backW": "חזרה", "print": "הדפסה / PDF",
           "routeErr": "שירות הניווט אינו זמין — מוצג קו ישר", "people": "אנשים", "minsW": "דק׳"},
    "ar": {"h1": "مساري", "lead": "جولة أنشأتها في المخطط — المحطات والوقت والسيارة المقترحة.",
           "empty": "المسار فارغ", "emptyText": "خطط رحلة ثم اضغط «عرض جولتي».",
           "toPlanner": "افتح في المخطط", "stopsW": "محطات", "dayW": "اليوم",
           "share": "نسخ الرابط", "copied": "تم نسخ الرابط ✓", "fromW": "من", "period": "التواريخ",
           "driveW": "قيادة", "visitW": "زيارة", "backW": "العودة", "print": "طباعة / PDF",
           "routeErr": "خدمة المسارات غير متاحة — يظهر خط مستقيم", "people": "أشخاص", "minsW": "د"},
}


def render_trip_page(lang):
    u = UI[lang]
    t = TRIP_UI[lang]
    depth = 1 if lang == ROOT_LANG else 2
    labels = dict(t)
    labels.update({k: tu(lang, k) for k in ("days", "total_km", "total_drive", "car_needed",
                                            "season", "difficulty", "km", "hrs",
                                            "waypoints_title", "plan_title")})
    labels["plannerUrl"] = page_url(lang, "map", False) + "#planner"
    labels["fleetUrl"] = page_url(lang, "fleet", False)
    body = (
        f'<section class="page-head"><div class="wrap">'
        f'<h1 id="triph1">{E(t["h1"])}</h1>'
        f'<p class="lead" id="triplead">{E(t["lead"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">'
        f'<div id="tripempty" class="trip-empty" hidden><h2>{E(t["empty"])}</h2>'
        f'<p class="pshort">{E(t["emptyText"])}</p>'
        f'<a class="btn" href="{labels["plannerUrl"]}">{E(t["toPlanner"])}</a></div>'
        f'<div id="tripbody" hidden>'
        f'<dl class="facts" id="tripfacts"></dl>'
        f'<div id="tripmap" class="trip-map"></div>'
        f'<div id="tripstatus" class="trip-status" role="status" hidden></div>'
        f'<h2>{E(labels["plan_title"])}</h2><div id="tripdays" class="trip-days"></div>'
        f'<h2>{E(labels["waypoints_title"])}</h2><div class="cards" id="tripstops"></div>'
        f'<div class="cta"><h2>{E(u["ui"]["book_title"])}</h2>'
        f'<p>{inline(u["ui"]["book_text"], lang)}</p><div class="row">'
        f'<a class="btn" id="tripbook" href="{page_url(lang, "contact", False)}">{E(u["nav"]["contact"])}</a>'
        f'<a class="btn ghost" id="tripplanner" href="{labels["plannerUrl"]}">{E(t["toPlanner"])}</a>'
        f'<button type="button" class="btn ghost" id="tripshare">{E(t["share"])}</button>'
        f'<button type="button" class="btn ghost" id="tripprint">{E(t["print"])}</button>'
        f'</div><p id="tripmsg" role="status" class="trip-msg"></p></div>'
        f'</div></div></section>')
    title = f'{t["h1"]} | {BRAND}'
    url = SITE_URL + lang_root(lang) + "trip/"
    head = head_html(lang, "trip", title, t["lead"], "", url,
                     {l: SITE_URL + lang_root(l) + "trip/" for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": [org_node(lang), website_node(lang)]},
                     leaflet=True)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], page_url(lang, "map", False)),
                                (t["h1"], None)])
    tail = (f'\n<script>window.TRIPT={J(labels)};</script>'
            f'\n<script src="{TRAVEL_ASSET[lang]}"></script>'
            f'\n<script defer src="{ASSET.get("trip", "/assets/trip.js")}"></script>')
    return shell(lang, "trip", head, crumbs + f'<main id="main">{body}</main>', depth, tail)


# ══════════════════════════════════════════════════════════ Mobile App (/app/)
# "RentUp - Mobile App" მაკეტის ზუსტი პორტი — ცალკე დგას საიტის ქრომისგან.
DOA_UI = {
    "ka": {"appSub": "მოგზაურობის დამგეგმავი", "h1": "დაგეგმე მოგზაურობა საქართველოში", "lead": "აირჩიე ადგილები, დაითვალე დრო და გააზიარე მარშრუტი.", "origin": "საწყისი ადგილი", "originPh": "ქალაქი ან ადგილი", "myLoc": "ჩემი მდებარეობა", "start": "დაწყება", "end": "დასრულება", "days": "რამდენი დღე", "people": "რამდენი ხართ", "transport": "ტრანსპორტი", "tr1": "შემომთავაზეთ მანქანა", "tr2": "ჩემი მანქანით ვარ", "tr3": "მანქანის ქირაობა მინდა", "tr4": "მძღოლი მჭირდება", "dayTime": "დღიური დრო", "plan": "დაგეგმე მოგზაურობა", "tours": "სტანდარტული ტურები", "searchTour": "ტურის ძებნა", "chooseTour": "ამ ტურის არჩევა", "chosen": "არჩეული", "used": "გამოყენებული", "left": "დარჩენილი", "searchPlace": "ადგილის ძებნა", "details": "დეტალები", "tabHome": "მთავარი", "tabMap": "რუკა", "tabRoute": "მარშრუტი", "tabComm": "საზოგადოება", "tabAcc": "ჩემი", "save": "მარშრუტის შენახვა", "share": "გაზიარება", "book": "მანქანის დაჯავშნა", "close": "დახურვა", "notifications": "შეტყობინებები", "emptyTitle": "შედეგი არ არის", "resetFilters": "ფილტრების მოხსნა", "routeEmptyTitle": "მარშრუტი ცარიელია", "routeEmptyText": "აირჩიე ადგილები რუკაზე ან სტანდარტული ტური.", "routeLoading": "მარშრუტი იგება…", "routeError": "გზის სერვისი მიუწვდომელია", "name": "სახელი", "phone": "ტელეფონი", "sendRequest": "მოთხოვნის გაგზავნა", "bookingDone": "მოთხოვნა გაიგზავნა", "bookingInvalid": "შეავსეთ სახელი და ტელეფონი", "commH1": "მოგზაურთა საზოგადოება", "commLead": "იპოვეთ თანამგზავრები, გააზიარეთ მარშრუტი და გამოცდილება, ან შეუერთდით თქვენთვის საინტერესო ტურს.", "accH1": "ჩემი გვერდი", "accLead": "აქ ინახება მარშრუტები, რომლებიც დამგეგმავში ააგეთ — თარიღით და სტატუსით.", "install": "მთავარ ეკრანზე დამატება", "join": "შეერთება", "joined": "შეერთებული ✓", "pub": "საჯარო", "priv": "პირადი", "day": "დღე", "visitedMark": "ნამყოფად მონიშვნა", "visited": "ნამყოფი ✓", "add": "მარშრუტში დამატება", "remove": "მარშრუტიდან მოშორება", "noTime": "დროში არ ეტევა", "saved": "შენახულია ✓", "copied": "ბმული დაკოპირდა ✓", "placeDetails": "ადგილის დეტალები", "inGroup": "ადგილი ამ ჯგუფში", "fitsL": "ეტევა დროში", "notVisited": "არ ვარ ნამყოფი", "placesWord": "ადგილი", "tripsWord": "მოგზაურობა", "freeSeats": "თავისუფალი ადგილი", "noSeats": "ადგილები შევსებულია", "all": "ყველა", "installHint": "მენიუდან აირჩიეთ „მთავარ ეკრანზე დამატება“", "minU": "წთ", "hU": "სთ", "kmU": "კმ", "seats": "ადგილი", "people2": "ადამიანი", "stdCar": "სტანდარტული", "sending": "იგზავნება…", "sendErr": "ვერ გაიგზავნა — სცადეთ ხელახლა ან დაგვირეკეთ", "carWhy4": "მაღალმთიანი გზა — 4WD რეკომენდებულია", "carWhyStd": "ასფალტის მარშრუტი — სტანდარტული კლასი საკმარისია", "accPlanned": "დაგეგმილი ტურები", "accSaved": "შენახული მარშრუტები", "accVisited": "მონახულებული ადგილები", "accGroups": "ჯგუფები", "accCars": "ნაქირავები ავტომობილები", "notif1": "გიორგიმ მოგიწვია ჯგუფში „სვანეთი, სექტემბერი“", "when1": "2 საათის წინ", "notif2": "თქვენი მარშრუტი გაზიარებულია", "when2": "გუშინ"},
    "en": {"appSub": "Trip planner", "h1": "Plan a trip in Georgia", "lead": "Pick places, count the time and share the route.", "origin": "Starting point", "originPh": "City or place", "myLoc": "My location", "start": "From", "end": "To", "days": "How many days", "people": "How many of you", "transport": "Transport", "tr1": "Suggest a car", "tr2": "I have my own car", "tr3": "I want to rent a car", "tr4": "I need a driver", "dayTime": "Hours per day", "plan": "Plan a trip", "tours": "Standard tours", "searchTour": "Search a tour", "chooseTour": "Choose this tour", "chosen": "Budget", "used": "Used", "left": "Left", "searchPlace": "Search a place", "details": "Details", "tabHome": "Home", "tabMap": "Map", "tabRoute": "Route", "tabComm": "Community", "tabAcc": "Me", "save": "Save route", "share": "Share", "book": "Book the car", "close": "Close", "notifications": "Notifications", "emptyTitle": "No results", "resetFilters": "Clear filters", "routeEmptyTitle": "The route is empty", "routeEmptyText": "Pick places on the map or choose a standard tour.", "routeLoading": "Building the route…", "routeError": "Routing service unavailable", "name": "Name", "phone": "Phone", "sendRequest": "Send request", "bookingDone": "Request sent", "bookingInvalid": "Fill in name and phone", "commH1": "Traveller community", "commLead": "Find travel companions, share a route and experience, or join a trip that interests you.", "accH1": "My page", "accLead": "This is where the routes you build in the planner are kept — with the date and the status.", "install": "Add to home screen", "join": "Join", "joined": "Joined ✓", "pub": "Public", "priv": "Private", "day": "day", "visitedMark": "Mark as visited", "visited": "Visited ✓", "add": "Add to route", "remove": "Remove from route", "noTime": "does not fit in time", "saved": "Saved ✓", "copied": "Link copied ✓", "placeDetails": "Place details", "inGroup": "places in this cluster", "fitsL": "Fits in time", "notVisited": "Not visited", "placesWord": "places", "tripsWord": "trips", "freeSeats": "seats free", "noSeats": "full", "all": "All", "installHint": "Use the browser menu → “Add to home screen”", "minU": "min", "hU": "h", "kmU": "km", "seats": "seats", "people2": "people", "stdCar": "Standard", "sending": "Sending…", "sendErr": "Could not send — try again or call us", "carWhy4": "High mountain road — 4WD recommended", "carWhyStd": "Paved route — a standard class is enough", "accPlanned": "Planned trips", "accSaved": "Saved routes", "accVisited": "Visited places", "accGroups": "Groups", "accCars": "Rented cars", "notif1": "Giorgi invited you to “Svaneti, September”", "when1": "2 h ago", "notif2": "Your route has been shared", "when2": "yesterday"},
    "ru": {"appSub": "Планировщик поездок", "h1": "Спланируйте поездку по Грузии", "lead": "Выберите места, посчитайте время и поделитесь маршрутом.", "origin": "Начальная точка", "originPh": "Город или место", "myLoc": "Моё местоположение", "start": "С", "end": "По", "days": "Сколько дней", "people": "Сколько вас", "transport": "Транспорт", "tr1": "Предложите машину", "tr2": "Я на своей машине", "tr3": "Хочу арендовать машину", "tr4": "Нужен водитель", "dayTime": "Часов в день", "plan": "Спланировать поездку", "tours": "Готовые туры", "searchTour": "Поиск тура", "chooseTour": "Выбрать этот тур", "chosen": "Бюджет", "used": "Использовано", "left": "Осталось", "searchPlace": "Поиск места", "details": "Детали", "tabHome": "Главная", "tabMap": "Карта", "tabRoute": "Маршрут", "tabComm": "Сообщество", "tabAcc": "Я", "save": "Сохранить маршрут", "share": "Поделиться", "book": "Забронировать машину", "close": "Закрыть", "notifications": "Уведомления", "emptyTitle": "Нет результатов", "resetFilters": "Сбросить фильтры", "routeEmptyTitle": "Маршрут пуст", "routeEmptyText": "Выберите места на карте или готовый тур.", "routeLoading": "Строим маршрут…", "routeError": "Сервис маршрутов недоступен", "name": "Имя", "phone": "Телефон", "sendRequest": "Отправить запрос", "bookingDone": "Запрос отправлен", "bookingInvalid": "Заполните имя и телефон", "commH1": "Сообщество путешественников", "commLead": "Найдите попутчиков, поделитесь маршрутом и впечатлениями или присоединитесь к интересной поездке.", "accH1": "Моя страница", "accLead": "Здесь хранятся маршруты, построенные в планировщике, — с датой и статусом.", "install": "Добавить на главный экран", "join": "Присоединиться", "joined": "Вы в поездке ✓", "pub": "Открытая", "priv": "Личная", "day": "дн.", "visitedMark": "Отметить посещённым", "visited": "Посещено ✓", "add": "Добавить в маршрут", "remove": "Убрать из маршрута", "noTime": "не влезает по времени", "saved": "Сохранено ✓", "copied": "Ссылка скопирована ✓", "placeDetails": "О месте", "inGroup": "мест в кластере", "fitsL": "Влезает по времени", "notVisited": "Не был", "placesWord": "мест", "tripsWord": "поездок", "freeSeats": "свободных мест", "noSeats": "мест нет", "all": "Все", "installHint": "В меню браузера → «На главный экран»", "minU": "мин", "hU": "ч", "kmU": "км", "seats": "мест", "people2": "чел.", "stdCar": "Стандарт", "sending": "Отправка…", "sendErr": "Не отправилось — попробуйте ещё раз или позвоните", "carWhy4": "Горная дорога — рекомендуется 4WD", "carWhyStd": "Асфальтовый маршрут — достаточно стандартного класса", "accPlanned": "Запланированные поездки", "accSaved": "Сохранённые маршруты", "accVisited": "Посещённые места", "accGroups": "Группы", "accCars": "Арендованные машины", "notif1": "Гиорги пригласил вас в «Сванети, сентябрь»", "when1": "2 ч назад", "notif2": "Ваш маршрут опубликован", "when2": "вчера"},
    "fa": {"appSub": "برنامه‌ریز سفر", "h1": "سفر خود در گرجستان را برنامه‌ریزی کنید", "lead": "مکان‌ها را انتخاب کنید، زمان را بشمارید و مسیر را به اشتراک بگذارید.", "origin": "نقطهٔ شروع", "originPh": "شهر یا مکان", "myLoc": "موقعیت من", "start": "از", "end": "تا", "days": "چند روز", "people": "چند نفرید", "transport": "حمل‌ونقل", "tr1": "خودرو پیشنهاد دهید", "tr2": "خودروی خودم را دارم", "tr3": "می‌خواهم خودرو اجاره کنم", "tr4": "راننده لازم دارم", "dayTime": "ساعت در روز", "plan": "برنامه‌ریزی سفر", "tours": "تورهای آماده", "searchTour": "جست‌وجوی تور", "chooseTour": "انتخاب این تور", "chosen": "زمان انتخابی", "used": "مصرف‌شده", "left": "باقی‌مانده", "searchPlace": "جست‌وجوی مکان", "details": "جزئیات", "tabHome": "خانه", "tabMap": "نقشه", "tabRoute": "مسیر", "tabComm": "جامعه", "tabAcc": "من", "save": "ذخیرهٔ مسیر", "share": "اشتراک‌گذاری", "book": "رزرو خودرو", "close": "بستن", "notifications": "اعلان‌ها", "emptyTitle": "نتیجه‌ای نیست", "resetFilters": "حذف فیلترها", "routeEmptyTitle": "مسیر خالی است", "routeEmptyText": "روی نقشه مکان انتخاب کنید یا یک تور آماده بگیرید.", "routeLoading": "در حال ساخت مسیر…", "routeError": "سرویس مسیریابی در دسترس نیست", "name": "نام", "phone": "تلفن", "sendRequest": "ارسال درخواست", "bookingDone": "درخواست ارسال شد", "bookingInvalid": "نام و تلفن را وارد کنید", "commH1": "جامعه مسافران", "commLead": "همسفر پیدا کنید، مسیر و تجربه خود را به اشتراک بگذارید یا به یک سفر بپیوندید.", "accH1": "صفحهٔ من", "accLead": "مسیرهایی که در برنامه‌ریز می‌سازید اینجا نگه داشته می‌شوند — با تاریخ و وضعیت.", "install": "افزودن به صفحهٔ اصلی", "join": "پیوستن", "joined": "پیوستید ✓", "pub": "عمومی", "priv": "خصوصی", "day": "روز", "visitedMark": "علامت بازدیدشده", "visited": "بازدیدشده ✓", "add": "افزودن به مسیر", "remove": "حذف از مسیر", "noTime": "در زمان جا نمی‌شود", "saved": "ذخیره شد ✓", "copied": "پیوند کپی شد ✓", "placeDetails": "جزئیات مکان", "inGroup": "مکان در این خوشه", "fitsL": "در زمان جا می‌شود", "notVisited": "بازدید نکرده‌ام", "placesWord": "مکان", "tripsWord": "سفر", "freeSeats": "جای خالی", "noSeats": "تکمیل", "all": "همه", "installHint": "از منوی مرورگر «افزودن به صفحهٔ اصلی»", "minU": "دقیقه", "hU": "ساعت", "kmU": "کیلومتر", "seats": "صندلی", "people2": "نفر", "stdCar": "استاندارد", "sending": "در حال ارسال…", "sendErr": "ارسال نشد — دوباره تلاش کنید یا تماس بگیرید", "carWhy4": "جاده کوهستانی — 4WD توصیه می‌شود", "carWhyStd": "مسیر آسفالت — کلاس استاندارد کافی است", "accPlanned": "سفرهای برنامه‌ریزی‌شده", "accSaved": "مسیرهای ذخیره‌شده", "accVisited": "مکان‌های بازدیدشده", "accGroups": "گروه‌ها", "accCars": "خودروهای اجاره‌شده", "notif1": "گیورگی شما را به «سوانتی، سپتامبر» دعوت کرد", "when1": "۲ ساعت پیش", "notif2": "مسیر شما به اشتراک گذاشته شد", "when2": "دیروز"},
    "he": {"appSub": "מתכנן טיולים", "h1": "תכננו טיול בגאורגיה", "lead": "בחרו מקומות, חשבו את הזמן ושתפו את המסלול.", "origin": "נקודת מוצא", "originPh": "עיר או מקום", "myLoc": "המקום שלי", "start": "מתאריך", "end": "עד", "days": "כמה ימים", "people": "כמה אתם", "transport": "תחבורה", "tr1": "הציעו לי רכב", "tr2": "יש לי רכב", "tr3": "רוצה לשכור רכב", "tr4": "צריך נהג", "dayTime": "שעות ביום", "plan": "לתכנן טיול", "tours": "טיולים מוכנים", "searchTour": "חיפוש טיול", "chooseTour": "בחירת הטיול", "chosen": "תקציב זמן", "used": "בשימוש", "left": "נותר", "searchPlace": "חיפוש מקום", "details": "פרטים", "tabHome": "בית", "tabMap": "מפה", "tabRoute": "מסלול", "tabComm": "קהילה", "tabAcc": "אני", "save": "שמירת מסלול", "share": "שיתוף", "book": "הזמנת רכב", "close": "סגירה", "notifications": "התראות", "emptyTitle": "אין תוצאות", "resetFilters": "ניקוי מסננים", "routeEmptyTitle": "המסלול ריק", "routeEmptyText": "בחרו מקומות במפה או טיול מוכן.", "routeLoading": "בונים מסלול…", "routeError": "שירות הניווט אינו זמין", "name": "שם", "phone": "טלפון", "sendRequest": "שליחת בקשה", "bookingDone": "הבקשה נשלחה", "bookingInvalid": "מלאו שם וטלפון", "commH1": "קהילת מטיילים", "commLead": "מצאו שותפים לדרך, שתפו מסלול וחוויה או הצטרפו לטיול שמעניין אתכם.", "accH1": "העמוד שלי", "accLead": "כאן נשמרים המסלולים שבניתם במתכנן — עם התאריך והסטטוס.", "install": "הוספה למסך הבית", "join": "הצטרפות", "joined": "הצטרפת ✓", "pub": "ציבורי", "priv": "פרטי", "day": "יום", "visitedMark": "סימון כביקרתי", "visited": "ביקרתי ✓", "add": "הוספה למסלול", "remove": "הסרה מהמסלול", "noTime": "לא נכנס בזמן", "saved": "נשמר ✓", "copied": "הקישור הועתק ✓", "placeDetails": "פרטי המקום", "inGroup": "מקומות באשכול", "fitsL": "נכנס בזמן", "notVisited": "לא ביקרתי", "placesWord": "מקומות", "tripsWord": "טיולים", "freeSeats": "מקומות פנויים", "noSeats": "מלא", "all": "הכול", "installHint": "בתפריט הדפדפן → «הוספה למסך הבית»", "minU": "דק׳", "hU": "שע׳", "kmU": 'ק"מ', "seats": "מושבים", "people2": "אנשים", "stdCar": "רגיל", "sending": "שולח…", "sendErr": "השליחה נכשלה — נסו שוב או התקשרו", "carWhy4": "דרך הרים — מומלץ 4WD", "carWhyStd": "מסלול סלול — מחלקה רגילה מספיקה", "accPlanned": "טיולים מתוכננים", "accSaved": "מסלולים שמורים", "accVisited": "מקומות שביקרתי", "accGroups": "קבוצות", "accCars": "רכבים שנשכרו", "notif1": "גיורגי הזמין אתכם ל״סוואנתי, ספטמבר״", "when1": "לפני שעתיים", "notif2": "המסלול שלכם שותף", "when2": "אתמול"},
    "ar": {"appSub": "مخطط الرحلات", "h1": "خطط رحلتك في جورجيا", "lead": "اختر الأماكن، واحسب الوقت، وشارك المسار.", "origin": "نقطة البداية", "originPh": "مدينة أو مكان", "myLoc": "موقعي", "start": "من", "end": "إلى", "days": "كم يوماً", "people": "كم عددكم", "transport": "التنقل", "tr1": "اقترحوا سيارة", "tr2": "لدي سيارتي", "tr3": "أريد استئجار سيارة", "tr4": "أحتاج سائقاً", "dayTime": "ساعات في اليوم", "plan": "خطط رحلة", "tours": "جولات جاهزة", "searchTour": "ابحث عن جولة", "chooseTour": "اختر هذه الجولة", "chosen": "الوقت المختار", "used": "المستخدم", "left": "المتبقي", "searchPlace": "ابحث عن مكان", "details": "التفاصيل", "tabHome": "الرئيسية", "tabMap": "الخريطة", "tabRoute": "المسار", "tabComm": "المجتمع", "tabAcc": "حسابي", "save": "حفظ المسار", "share": "مشاركة", "book": "احجز السيارة", "close": "إغلاق", "notifications": "الإشعارات", "emptyTitle": "لا نتائج", "resetFilters": "إزالة المرشحات", "routeEmptyTitle": "المسار فارغ", "routeEmptyText": "اختر أماكن على الخريطة أو جولة جاهزة.", "routeLoading": "جارٍ بناء المسار…", "routeError": "خدمة المسارات غير متاحة", "name": "الاسم", "phone": "الهاتف", "sendRequest": "إرسال الطلب", "bookingDone": "تم إرسال الطلب", "bookingInvalid": "أدخل الاسم والهاتف", "commH1": "مجتمع المسافرين", "commLead": "اعثر على رفقاء سفر وشارك مسارك وتجربتك أو انضم إلى رحلة تهمك.", "accH1": "صفحتي", "accLead": "هنا تُحفظ المسارات التي تبنيها في المخطط — مع التاريخ والحالة.", "install": "أضف إلى الشاشة الرئيسية", "join": "انضم", "joined": "انضممت ✓", "pub": "عامة", "priv": "خاصة", "day": "يوم", "visitedMark": "تحديد كمُزار", "visited": "مُزار ✓", "add": "أضف إلى المسار", "remove": "أزل من المسار", "noTime": "لا يتسع في الوقت", "saved": "تم الحفظ ✓", "copied": "تم نسخ الرابط ✓", "placeDetails": "تفاصيل المكان", "inGroup": "أماكن في هذه المجموعة", "fitsL": "يتسع في الوقت", "notVisited": "لم أزره", "placesWord": "أماكن", "tripsWord": "رحلات", "freeSeats": "مقاعد متاحة", "noSeats": "مكتمل", "all": "الكل", "installHint": "من قائمة المتصفح ← «أضف إلى الشاشة الرئيسية»", "minU": "د", "hU": "س", "kmU": "كم", "seats": "مقاعد", "people2": "أشخاص", "stdCar": "قياسية", "sending": "جارٍ الإرسال…", "sendErr": "تعذر الإرسال — حاول مجدداً أو اتصل بنا", "carWhy4": "طريق جبلي — يُنصح بدفع رباعي", "carWhyStd": "طريق معبد — الفئة القياسية كافية", "accPlanned": "رحلات مخططة", "accSaved": "مسارات محفوظة", "accVisited": "أماكن مُزارة", "accGroups": "مجموعات", "accCars": "سيارات مستأجرة", "notif1": "دعاك جيورجي إلى «سفانيتي، سبتمبر»", "when1": "قبل ساعتين", "notif2": "تمت مشاركة مسارك", "when2": "أمس"},
}

_DOA_PROF_T = {
    "ka": ("ჩემი ინფორმაცია", "ავტომატურად ჩაისმება მანქანის მოთხოვნაში — იქვე შეგიძლიათ შეცვლა.", "შენახვა"),
    "en": ("My details", "Filled into the car request automatically — you can change it there.", "Save"),
    "ru": ("Мои данные", "Подставляются в заявку на автомобиль — там можно изменить.", "Сохранить"),
    "fa": ("اطلاعات من", "به‌طور خودکار در درخواست خودرو وارد می‌شود — همان‌جا قابل تغییر است.", "ذخیره"),
    "he": ("הפרטים שלי", "ממולאים אוטומטית בבקשת הרכב — אפשר לשנות שם.", "שמירה"),
    "ar": ("بياناتي", "تُدرج تلقائياً في طلب السيارة — يمكن تعديلها هناك.", "حفظ"),
}
for _l, _v in _DOA_PROF_T.items():
    DOA_UI[_l]["myDetails"], DOA_UI[_l]["myDetailsLead"], DOA_UI[_l]["save2"] = _v

_DOA_LAND_T = {
    "ka": ("რა გეგმა გაქვს დღეს?", "აირჩიე სასურველი და დაიწყე შენი მოგზაურობა საქართველოში",
           "დაგეგმე ტური დამოუკიდებლად", "სტანდარტული ტურები", "მანქანის დაჯავშნა", "განვერიანდი Community-ში"),
    "en": ("What is your plan for today?", "Pick what you feel like and start your journey across Georgia",
           "Plan your own trip", "Standard tours", "Book a car", "Join the community"),
    "ru": ("Какие планы на сегодня?", "Выберите, что вам ближе, и начните путешествие по Грузии",
           "Спланировать поездку самому", "Готовые туры", "Забронировать машину", "Присоединиться к сообществу"),
    "fa": ("برنامهٔ امروز شما چیست؟", "آنچه دوست دارید انتخاب کنید و سفر خود در گرجستان را آغاز کنید",
           "سفر خود را بسازید", "تورهای آماده", "رزرو خودرو", "به جامعه بپیوندید"),
    "he": ("מה התוכנית שלך להיום?", "בחרו את מה שמתאים לכם והתחילו את המסע בגאורגיה",
           "לתכנן טיול בעצמכם", "טיולים מוכנים", "להזמין רכב", "להצטרף לקהילה"),
    "ar": ("ما خطتك اليوم؟", "اختر ما يناسبك وابدأ رحلتك في جورجيا",
           "خطط رحلتك بنفسك", "جولات جاهزة", "احجز سيارة", "انضم إلى المجتمع"),
}
for _l, _v in _DOA_LAND_T.items():
    (DOA_UI[_l]["landH1"], DOA_UI[_l]["landLead"], DOA_UI[_l]["lc1"],
     DOA_UI[_l]["lc2"], DOA_UI[_l]["lc3"], DOA_UI[_l]["lc4"]) = _v

_DOA_VIEWTRIP_T = {"ka": "ჩემი ტურის ნახვა", "en": "View my tour", "ru": "Посмотреть мой тур",
                   "fa": "مشاهده تور من", "he": "צפייה בטיול שלי", "ar": "عرض جولتي"}
for _l, _v in _DOA_VIEWTRIP_T.items():
    DOA_UI[_l]["viewTrip"] = _v
    DOA_UI[_l]["tripUrl"] = lang_root(_l) + "trip/"

_DOA_DETOUR_T = {"ka": ("გადახვევა", "გზაზეა"), "en": ("detour", "on the way"),
                 "ru": ("крюк", "по пути"), "fa": ("انحراف", "در مسیر"),
                 "he": ("סטייה", "על הדרך"), "ar": ("انحراف", "على الطريق")}
for _l, _v in _DOA_DETOUR_T.items():
    DOA_UI[_l]["detour"], DOA_UI[_l]["onWay"] = _v

DOA_STYLE = """
  html,body{margin:0;padding:0;height:100%;overscroll-behavior:none}
  body{background:#f4f7f9;color:#0e2333;font-family:"Noto Sans Georgian","Noto Sans",system-ui,sans-serif;font-size:15px;-webkit-font-smoothing:antialiased;-webkit-tap-highlight-color:transparent}
  *{box-sizing:border-box}
  a{color:#0b5f73;text-decoration:none}
  a:hover{color:#0d94ae}
  button,input,select{font-family:inherit;font-size:15px;color:#0e2333}
  button{cursor:pointer}
  :focus-visible{outline:2px solid #0d94ae;outline-offset:2px}
  [hidden]{display:none!important}
  .do-scroll{scrollbar-width:none}
  .do-scroll::-webkit-scrollbar{display:none}
  .leaflet-container{font-family:inherit;background:#eaf0f4}
  .do-pin{border-radius:999px;border:2px solid #fff;display:grid;place-items:center;font-size:11px;font-weight:700;color:#fff;box-shadow:0 1px 3px rgba(14,35,51,.35)}
  .do-cluster{background:#0b2f4d;color:#fff;border:2px solid #fff;border-radius:999px;display:grid;place-items:center;font-weight:700;font-size:13px;box-shadow:0 0 0 3px rgba(11,47,77,.16)}
  .app-install-card{position:fixed;left:12px;right:12px;bottom:76px;z-index:900;display:flex;gap:10px;align-items:center;background:#fff;border:1px solid #dde5ec;border-radius:14px;box-shadow:0 14px 30px rgba(14,35,51,.16);padding:10px;max-width:496px;margin:0 auto}
  .app-install-card img{width:40px;height:40px;border-radius:10px}
  .app-install-card div{flex:1;display:flex;flex-direction:column;gap:2px;min-width:0}
  .app-install-card strong{font-size:14px}
  .app-install-card span{font-size:12px;color:#5a6b7b}
  .app-install-action{height:40px;padding:0 14px;border:0;border-radius:10px;background:#0b2f4d;color:#fff;font-size:13px;font-weight:600}
  .app-install-close{width:32px;height:32px;border:0;background:transparent;font-size:16px;color:#5a6b7b}
  .authdlg{position:fixed;inset:0;z-index:950;background:rgba(14,35,51,.5);display:flex;align-items:center;justify-content:center;padding:16px}
  .authcard{position:relative;width:min(420px,100%);max-height:90vh;overflow:auto;background:#fff;border:1px solid #dde5ec;border-radius:16px;padding:20px;box-shadow:0 18px 40px rgba(14,35,51,.25)}
  .authcard h3{margin:0 0 6px;font-size:22px;color:#0e2333}
  .authcard .pshort{margin:0 0 14px;font-size:13px;color:#5a6b7b}
  .authbrand img{height:30px;margin-bottom:10px}
  .authcard label{display:block;font-size:13px;color:#5a6b7b;margin:0 0 10px}
  .authcard input{width:100%;font:inherit;font-size:15px;height:46px;padding:0 12px;margin-top:4px;border:1px solid #dde5ec;border-radius:10px;background:#fff;color:#0e2333}
  .authcard .btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:46px;margin:0 0 10px;border:0;border-radius:10px;background:#0b2f4d;color:#fff;font-size:14px;font-weight:600}
  .authcard .btn.goog{background:#fff;color:#0e2333;border:1px solid #dde5ec}
  .authcard .btn.goog .gicon svg{width:18px;height:18px;display:block}
  .authcard .facebook{background:#1877f2;color:#fff}
  .authcard .fbicon{font-weight:800}
  .author{display:flex;align-items:center;gap:10px;margin:4px 0 12px;color:#5a6b7b;font-size:12px}
  .author:before,.author:after{content:"";flex:1;height:1px;background:#dde5ec}
  .autherr{display:none;font-size:13px;color:#8c2d20;margin:0 0 8px}
  .autherr.show{display:block}
  .authrow{display:flex;gap:8px}
  .authx{position:absolute;top:10px;inset-inline-end:10px;width:38px;height:38px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:14px}
  .lnk{border:0;background:none;color:#0b5f73;font-size:13px;padding:4px 0;text-decoration:underline}
  .authsignup{margin:6px 0 0}
  .authnote{margin:10px 0 0;font-size:11px;color:#718091}
  body.auth-open{overflow:hidden}
"""


def render_app_page(lang):
    t = DOA_UI[lang]
    dr = "rtl" if lang in ("fa", "he", "ar") else "ltr"
    gf = DESIGN.get("google_fonts", "")
    fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={gf}&display=swap">') if gf else ""
    lang_urls = {l: lang_root(l) + "app/" for l in LANGS}
    u = UI[lang]
    fh_cfg = {k: AUTH.get(k, "") for k in ("apiKey", "authDomain", "projectId",
                                           "storageBucket", "messagingSenderId", "appId")}
    fh_cfg["accountUrl"] = page_url(lang, "account", False)
    fh_cfg["plannerUrl"] = page_url(lang, "map", False) + "#planner"
    fh_cfg["siteUrl"] = SITE_URL
    fh_cfg["season"] = SEASON_CFG
    fh_cfg["youngDriver"] = YOUNG_DRIVER_CFG
    fh_cfg["whatsapp"] = str(SITE.get("whatsapp") or SITE.get("mobile_e164")
                             or SITE.get("phone_e164", "")).replace("+", "").replace(" ", "")
    fh_cfg["t"] = {k: u["ui"][k] for k in (
        "account", "sign_in", "sign_up", "sign_out", "with_google", "or_email", "email",
        "password", "forgot", "reset_sent", "why_account", "legal_note", "please_sign_in",
        "no_trips", "to_planner", "planned", "done", "mark_done", "mark_planned", "open",
        "delete", "confirm_del", "days", "stops", "save_trip", "saved") if k in u["ui"]}
    doat = dict(t)
    doat["langUrls"] = lang_urls
    doat["accountUrl"] = fh_cfg["accountUrl"]
    doat["signinToSave"] = _DOW_SAVE_T[lang][0]
    doat["saveErr"] = _DOW_SAVE_T[lang][1]
    lang_opts = "".join(
        f'<option value="{l}"{" selected" if l == lang else ""}>{l.upper()}</option>' for l in LANGS)
    tr_opts = "".join(
        f'<option value="{v}">{E(t[k])}</option>'
        for v, k in (("suggest", "tr1"), ("own", "tr2"), ("rent", "tr3"), ("driver", "tr4")))
    tabs_html = "".join(
        f'<button type="button" id="doatab-{key}" aria-current="{"page" if key == "home" else "false"}" '
        f'style="min-height:52px;border:0;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;'
        f'color:{"#0b2f4d" if key == "home" else "#8494a2"};font-size:11px;font-weight:600;border-radius:10px">'
        f'<span style="width:22px;height:22px;display:grid;place-items:center;font-size:18px" aria-hidden="true">{icon}</span>'
        f'<span>{E(label)}</span></button>'
        for key, label, icon in (("home", t["tabHome"], "⌂"), ("map", t["tabMap"], "◎"),
                                 ("route", t["tabRoute"], "⇄"), ("community", t["tabComm"], "☰"),
                                 ("account", t["tabAcc"], "☺")))
    return f"""<!doctype html>
<html lang="{lang}" dir="{dr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b2f4d">
<meta name="robots" content="noindex">
<title>RentUp — {E(t["appSub"])}</title>
<link rel="manifest" href="/assets/manifest.webmanifest">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/app-icon-180.png">
{fonts}
<link rel="stylesheet" href="{LEAFLET_CSS}">
<style>{DOA_STYLE}</style>
{analytics_html()}
</head>
<body>
<div id="doa" style="height:100dvh;max-width:520px;margin:0 auto;display:flex;flex-direction:column;background:#f4f7f9;overflow:hidden;position:relative">

  <div style="flex:0 0 auto;display:flex;align-items:center;gap:8px;height:54px;padding:0 12px;padding-top:env(safe-area-inset-top);background:#fff;border-bottom:1px solid #dde5ec">
    <img src="/assets/do-logo-transparent.png" alt="RentUp" width="92" height="28" style="height:28px;width:auto;display:block">
    <span style="font-size:13px;font-weight:600;color:#5a6b7b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{E(t["appSub"])}</span>
    <div style="flex:1"></div>
    <select id="doalang" aria-label="Language" style="height:44px;padding:0 6px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:13px">{lang_opts}</select>
    <button type="button" id="doabellbtn" aria-label="{E(t["notifications"])}" style="position:relative;width:44px;height:44px;border:1px solid #dde5ec;border-radius:10px;background:#fff;display:grid;place-items:center">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0b2f4d" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8"></path><path d="M10.3 21a2 2 0 0 0 3.4 0"></path></svg>
      <span style="position:absolute;top:-3px;right:-3px;min-width:16px;height:16px;padding:0 4px;background:#c0392b;color:#fff;border-radius:999px;font-size:10px;font-weight:700;display:grid;place-items:center">2</span>
    </button>
  </div>

  <div id="doabell" role="dialog" aria-label="{E(t["notifications"])}" hidden style="position:absolute;top:56px;left:12px;right:12px;z-index:600;background:#fff;border:1px solid #dde5ec;border-radius:14px;box-shadow:0 14px 30px rgba(14,35,51,.16);padding:10px;display:flex;flex-direction:column;gap:8px">
    <div style="display:flex;flex-direction:column;gap:2px;padding:9px;border:1px solid #eef3f6;border-radius:10px">
      <span style="font-size:14px;font-weight:600">{E(t["notif1"])}</span>
      <span style="font-size:12px;color:#5a6b7b">{E(t["when1"])}</span>
    </div>
    <div style="display:flex;flex-direction:column;gap:2px;padding:9px;border:1px solid #eef3f6;border-radius:10px">
      <span style="font-size:14px;font-weight:600">{E(t["notif2"])}</span>
      <span style="font-size:12px;color:#5a6b7b">{E(t["when2"])}</span>
    </div>
    <button type="button" id="doabellclose" style="height:44px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:14px">{E(t["close"])}</button>
  </div>

  <div class="do-scroll" style="flex:1;min-height:0;overflow:auto;position:relative">

    <div id="doav-home">
      <div style="position:relative;background:#dfeaf1;padding:0 0 12px">
        <div style="position:relative;min-height:190px;overflow:hidden">
          <img src="/assets/rentup-hero2.jpg" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover" loading="eager" decoding="async">
          <div style="position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(255,255,255,.93) 0%,rgba(255,255,255,.86) 46%,rgba(255,255,255,.72) 100%)"></div>
          <div style="position:relative;pointer-events:none;padding:20px 14px 16px;display:flex;flex-direction:column;gap:8px">
            <h1 style="margin:0;font-size:27px;line-height:1.18;font-weight:800;letter-spacing:-.3px">{E(t["landH1"])}</h1>
            <p style="margin:0;font-size:14px;line-height:1.5;color:#41525f">{E(t["landLead"])}</p>
          </div>
        </div>
        <div style="position:relative;margin-top:14px;padding:0 12px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
          {"".join(
            f'<div style="border:1px solid {border};border-radius:14px;background:{bg};overflow:hidden;display:flex;flex-direction:column">'
            f'<span style="display:block;height:92px"><img src="/assets/{img}" alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block"></span>'
            f'<button type="button" data-doaland="{act}" style="display:flex;flex-direction:column;gap:6px;padding:10px;flex:1;border:0;background:transparent;text-align:start;font-family:inherit;cursor:pointer">'
            f'<span style="font-size:14px;font-weight:700;line-height:1.25;flex:1">{E(title)}</span>'
            f'<span style="width:30px;height:30px;border-radius:999px;background:#fff;border:1px solid {border};display:grid;place-items:center">'
            f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h13"></path><path d="m12 5 7 7-7 7"></path></svg>'
            f'</span></button></div>'
            for act, title, img, bg, border, ink in (
                ("plan", t["lc1"], "rentup-card-plan.jpg", "#e9f7ef", "#cbe8d8", "#0b7a55"),
                ("tours", t["lc2"], "rentup-card-tours.jpg", "#fdf6e3", "#f0e2bd", "#a5760a"),
                ("cars", t["lc3"], "rentup-card-cars.jpg", "#eaf3fc", "#cfe1f2", "#0b5f9e"),
                ("community", t["lc4"], "rentup-card-community.jpg", "#f4eefc", "#e0d3f4", "#6b3fa0"),
            ))}
        </div>
      </div>
      <div id="doaform" style="padding:12px;display:flex;flex-direction:column;gap:12px">
      <div style="display:flex;flex-direction:column;gap:6px">
        <h1 style="margin:0;font-size:22px;line-height:1.2;font-weight:700">{E(t["h1"])}</h1>
        <p style="margin:0;font-size:14px;color:#5a6b7b">{E(t["lead"])}</p>
      </div>

      <div style="background:#fff;border:1px solid #dde5ec;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:10px">
        <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["origin"])}
          <span style="display:flex;gap:6px">
            <input id="doaorigin" type="text" autocomplete="off" placeholder="{E(t["originPh"])}" style="flex:1;height:46px;padding:0 10px;border:1px solid #dde5ec;border-radius:10px;min-width:0">
            <button type="button" id="doamyloc" aria-label="{E(t["myLoc"])}" style="width:46px;height:46px;border:1px solid #dde5ec;border-radius:10px;background:#fff;display:grid;place-items:center;flex:0 0 auto">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0d94ae" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path></svg>
            </button>
          </span>
        </label>
        <div id="doasuggest" role="listbox" class="do-scroll" hidden style="max-height:210px;overflow:auto;border:1px solid #dde5ec;border-radius:10px"></div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["start"])}
            <input id="doastart" type="date" style="height:46px;padding:0 8px;border:1px solid #dde5ec;border-radius:10px">
          </label>
          <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["end"])}
            <input id="doaend" type="date" style="height:46px;padding:0 8px;border:1px solid #dde5ec;border-radius:10px">
          </label>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div style="display:flex;flex-direction:column;gap:5px">
            <span style="font-size:12px;font-weight:600;color:#5a6b7b">{E(t["days"])}</span>
            <div style="height:46px;display:grid;grid-template-columns:46px 1fr 46px;border:1px solid #dde5ec;border-radius:10px;overflow:hidden;background:#fff">
              <button type="button" id="doadaysdown" aria-label="−" style="border:0;border-inline-end:1px solid #dde5ec;background:#fff;font-size:18px">−</button>
              <span id="doadays" style="display:grid;place-items:center;font-size:14px;font-weight:600"></span>
              <button type="button" id="doadaysup" aria-label="+" style="border:0;border-inline-start:1px solid #dde5ec;background:#fff;font-size:18px">+</button>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:5px">
            <span style="font-size:12px;font-weight:600;color:#5a6b7b">{E(t["people"])}</span>
            <div style="height:46px;display:grid;grid-template-columns:46px 1fr 46px;border:1px solid #dde5ec;border-radius:10px;overflow:hidden;background:#fff">
              <button type="button" id="doapeopledown" aria-label="−" style="border:0;border-inline-end:1px solid #dde5ec;background:#fff;font-size:18px">−</button>
              <span id="doapeople" style="display:grid;place-items:center;font-size:14px;font-weight:600"></span>
              <button type="button" id="doapeopleup" aria-label="+" style="border:0;border-inline-start:1px solid #dde5ec;background:#fff;font-size:18px">+</button>
            </div>
          </div>
        </div>

        <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["transport"])}
          <select id="doatransport" style="height:46px;padding:0 8px;border:1px solid #dde5ec;border-radius:10px;background:#fff">{tr_opts}</select>
        </label>

        <div style="display:flex;align-items:center;gap:8px;padding:8px;border:1px solid #dde5ec;border-radius:10px;background:#fbfdfe">
          <span style="font-size:12px;font-weight:600;color:#5a6b7b;flex:1">{E(t["dayTime"])}</span>
          <div style="display:grid;grid-template-columns:40px 62px 40px;height:44px;border:1px solid #dde5ec;border-radius:10px;overflow:hidden;background:#fff">
            <button type="button" id="doahoursdown" aria-label="−0.5" style="border:0;border-inline-end:1px solid #dde5ec;background:#fff;font-size:18px">−</button>
            <span id="doahours" style="display:grid;place-items:center;font-size:13px;font-weight:600"></span>
            <button type="button" id="doahoursup" aria-label="+0.5" style="border:0;border-inline-start:1px solid #dde5ec;background:#fff;font-size:18px">+</button>
          </div>
        </div>

        <button type="button" id="doaplan" style="height:50px;border:0;border-radius:12px;background:#0b2f4d;color:#fff;font-size:15px;font-weight:600">{E(t["plan"])}</button>
        <button type="button" id="doatoursbtn" style="height:48px;border:1px solid #0b2f4d;border-radius:12px;background:#fff;color:#0b2f4d;font-size:15px;font-weight:600">{E(t["tours"])}</button>
      </div>

      <div style="display:flex;justify-content:space-between;gap:8px;padding:10px 12px;background:#fff;border:1px solid #dde5ec;border-radius:14px">
        <span style="font-size:12px;color:#5a6b7b">{E(t["chosen"])} <strong id="doabudget" style="color:#0e2333"></strong></span>
        <span style="font-size:12px;color:#5a6b7b">{E(t["used"])} <strong id="doaused" style="color:#0e2333"></strong></span>
        <span style="font-size:12px;color:#5a6b7b">{E(t["left"])} <strong id="doaleft" style="color:#0b7a55"></strong></span>
      </div>
      </div>
    </div>

    <div id="doav-map" hidden style="position:absolute;inset:0">
      <div id="doamap" role="application" aria-label="{E(t["tabMap"])}" style="position:absolute;inset:0"></div>

      <div style="position:absolute;top:10px;left:10px;right:10px;display:flex;gap:6px;z-index:500">
        <input id="doasearch" type="search" aria-label="{E(t["searchPlace"])}" placeholder="{E(t["searchPlace"])}" style="flex:1;height:46px;padding:0 12px;border:1px solid #dde5ec;border-radius:12px;background:#fff;box-shadow:0 2px 8px rgba(14,35,51,.12);min-width:0">
        <button type="button" id="doawx" aria-pressed="true" style="width:46px;height:46px;border:1px solid #dde5ec;border-radius:12px;background:#e6f6f9;box-shadow:0 2px 8px rgba(14,35,51,.12);font-size:16px">☀</button>
      </div>

      <div id="doahits" class="do-scroll" hidden style="position:absolute;top:62px;left:10px;right:10px;max-height:44%;overflow:auto;background:#fff;border:1px solid #dde5ec;border-radius:12px;box-shadow:0 8px 22px rgba(14,35,51,.16);z-index:520"></div>

      <div id="doaloading" role="status" hidden style="position:absolute;top:66px;left:50%;transform:translateX(-50%);padding:7px 14px;background:#0b2f4d;color:#fff;border-radius:999px;font-size:12px;z-index:540">{E(t["routeLoading"])}</div>
      <div id="doarouteerr" role="status" hidden style="position:absolute;top:66px;left:50%;transform:translateX(-50%);padding:7px 14px;background:#fff;border:1px solid #e6c9c4;color:#8c2d20;border-radius:999px;font-size:12px;z-index:540">{E(t["routeError"])}</div>

      <div class="do-scroll" style="position:absolute;left:0;right:0;bottom:0;max-height:52%;overflow:auto;background:#fff;border-top:1px solid #dde5ec;border-radius:16px 16px 0 0;box-shadow:0 -6px 20px rgba(14,35,51,.12);z-index:510">
        <div style="position:sticky;top:0;background:#fff;padding:8px 12px 6px;border-bottom:1px solid #eef3f6;z-index:2">
          <div style="width:38px;height:4px;border-radius:999px;background:#cfdae3;margin:0 auto 8px"></div>
          <div id="doachips" class="do-scroll" style="display:flex;gap:6px;overflow-x:auto;min-height:36px"></div>
          <div style="display:flex;justify-content:space-between;padding-top:6px;font-size:12px;color:#5a6b7b">
            <span id="doacount"></span>
            <span id="doaselcount"></span>
          </div>
        </div>
        <div id="doalist"></div>
        <div id="doaempty" hidden style="padding:20px 12px;display:flex;flex-direction:column;gap:8px;align-items:flex-start">
          <span style="font-size:14px;font-weight:600">{E(t["emptyTitle"])}</span>
          <button type="button" id="doaresetf" style="min-height:44px;padding:0 14px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:14px">{E(t["resetFilters"])}</button>
        </div>
      </div>
    </div>

    <div id="doav-route" hidden style="padding:12px;display:flex;flex-direction:column;gap:12px">
      <div style="display:flex;justify-content:space-between;gap:8px;padding:10px 12px;background:#fff;border:1px solid #dde5ec;border-radius:14px">
        <span style="font-size:12px;color:#5a6b7b">{E(t["used"])} <strong id="doaused2" style="color:#0e2333"></strong></span>
        <span style="font-size:12px;color:#5a6b7b">{E(t["left"])} <strong id="doaleft2" style="color:#0b7a55"></strong></span>
      </div>

      <div id="doatourchip" hidden style="display:flex;align-items:center;gap:8px;padding:10px 12px;border:1px solid #cbe8ee;border-radius:14px;background:#eefafc">
        <span id="doatourname" style="font-size:13px;font-weight:700;color:#0b5f73;flex:1"></span>
        <button type="button" id="doacleartour" aria-label="{E(t["close"])}" style="width:36px;height:36px;border:1px solid #cbe8ee;border-radius:10px;background:#fff">×</button>
      </div>

      <div id="doastops" style="display:flex;flex-direction:column;gap:12px"></div>

      <div id="doaroutempty" style="padding:20px 12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;display:flex;flex-direction:column;gap:10px;align-items:flex-start">
        <span style="font-size:14px;font-weight:600">{E(t["routeEmptyTitle"])}</span>
        <span style="font-size:13px;color:#5a6b7b">{E(t["routeEmptyText"])}</span>
        <button type="button" id="doaroutemap" style="min-height:46px;padding:0 14px;border:1px solid #0b2f4d;border-radius:10px;background:#fff;color:#0b2f4d;font-size:14px;font-weight:600">{E(t["tabMap"])}</button>
      </div>

      <div id="doacar" hidden style="padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;display:flex;flex-direction:column;gap:6px">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline">
          <span id="doacarname" style="font-size:15px;font-weight:700"></span>
          <span id="doacarprice" style="font-size:14px;font-weight:700;color:#0b7a55"></span>
        </div>
        <span id="doacarspecs" style="font-size:12px;color:#5a6b7b"></span>
        <span id="doacartiers" style="font-size:12px;color:#5a6b7b"></span>
        <span id="doacarwhy" style="font-size:12px;color:#5a6b7b"></span>
        <button type="button" id="doabook" style="height:48px;border:0;border-radius:12px;background:#0d94ae;color:#fff;font-size:15px;font-weight:600">{E(t["book"])}</button>
      </div>

      <a id="doatrip" href="#" target="_blank" rel="noopener" hidden style="display:flex;align-items:center;justify-content:center;height:48px;border:1px solid #0d94ae;border-radius:12px;background:#eefafc;color:#0b5f73;font-size:14px;font-weight:600;text-decoration:none">{E(t["viewTrip"])}</a>
      <div id="doasavegrid" hidden style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <button type="button" id="doasave" style="height:48px;border:1px solid #0b2f4d;border-radius:12px;background:#fff;color:#0b2f4d;font-size:14px;font-weight:600">{E(t["save"])}</button>
        <button type="button" id="doashare" style="height:48px;border:1px solid #dde5ec;border-radius:12px;background:#fff;font-size:14px;font-weight:600">{E(t["share"])}</button>
      </div>
      <span id="doatripmsg" role="status" style="font-size:13px;color:#0b7a55"></span>
    </div>

    <div id="doav-community" hidden style="padding:12px;display:flex;flex-direction:column;gap:12px">
      <div style="display:flex;flex-direction:column;gap:5px">
        <h1 style="margin:0;font-size:24px;line-height:1.2;font-weight:700">{E(t["commH1"])}</h1>
        <p style="margin:0;font-size:14px;color:#5a6b7b">{E(t["commLead"])}</p>
      </div>
      <div id="doacomm" style="display:flex;flex-direction:column;gap:12px"></div>
    </div>

    <div id="doav-account" hidden style="padding:12px;display:flex;flex-direction:column;gap:12px">
      <div style="display:flex;gap:12px;align-items:center">
        <span style="width:56px;height:56px;border-radius:999px;background:#0d94ae;color:#fff;font-size:18px;font-weight:700;display:grid;place-items:center;flex:0 0 auto">DO</span>
        <div style="display:flex;flex-direction:column;gap:3px;min-width:0">
          <h1 style="margin:0;font-size:22px;line-height:1.2;font-weight:700">{E(t["accH1"])}</h1>
          <span style="font-size:13px;color:#5a6b7b">{E(t["accLead"])}</span>
        </div>
      </div>
      <div style="padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;display:flex;flex-direction:column;gap:8px">
        <span style="font-size:15px;font-weight:700">{E(t["myDetails"])}</span>
        <span style="font-size:12px;color:#5a6b7b">{E(t["myDetailsLead"])}</span>
        <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["name"])}
          <input id="doaprofname" type="text" autocomplete="name" style="height:46px;padding:0 12px;border:1px solid #dde5ec;border-radius:10px">
        </label>
        <label style="display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:600;color:#5a6b7b">{E(t["phone"])}
          <input id="doaprofphone" type="tel" inputmode="tel" autocomplete="tel" style="height:46px;padding:0 12px;border:1px solid #dde5ec;border-radius:10px">
        </label>
        <button type="button" id="doaprofsave" style="height:46px;border:1px solid #0b2f4d;border-radius:10px;background:#fff;color:#0b2f4d;font-size:14px;font-weight:600">{E(t["save2"])}</button>
      </div>
      <button type="button" data-acc="route" style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:56px;padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;text-align:start">
        <span style="font-size:15px;font-weight:600">{E(t["accPlanned"])}</span>
        <span id="doaacc-planned" style="font-size:14px;color:#5a6b7b">0</span>
      </button>
      <button type="button" data-acc="saved" style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:56px;padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;text-align:start">
        <span style="font-size:15px;font-weight:600">{E(t["accSaved"])}</span>
        <span id="doaacc-saved" style="font-size:14px;color:#5a6b7b">0</span>
      </button>
      <button type="button" data-acc="visited" style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:56px;padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;text-align:start">
        <span style="font-size:15px;font-weight:600">{E(t["accVisited"])}</span>
        <span id="doaacc-visited" style="font-size:14px;color:#5a6b7b">0</span>
      </button>
      <button type="button" data-acc="community" style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:56px;padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;text-align:start">
        <span style="font-size:15px;font-weight:600">{E(t["accGroups"])}</span>
        <span id="doaacc-groups" style="font-size:14px;color:#5a6b7b">0</span>
      </button>
      <button type="button" data-acc="route" style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:56px;padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;text-align:start">
        <span style="font-size:15px;font-weight:600">{E(t["accCars"])}</span>
        <span id="doaacc-cars" style="font-size:14px;color:#5a6b7b">0</span>
      </button>
      <button type="button" id="doainstall" style="min-height:48px;padding:0 14px;border:1px solid #0b2f4d;border-radius:12px;background:#fff;color:#0b2f4d;font-size:14px;font-weight:600">{E(t["install"])}</button>
    </div>
  </div>

  <div style="flex:0 0 auto;display:grid;grid-template-columns:repeat(5,1fr);gap:2px;background:#fff;border-top:1px solid #dde5ec;padding:6px 4px calc(6px + env(safe-area-inset-bottom))">{tabs_html}</div>

  <div id="doadetailwrap" hidden style="position:absolute;inset:0;background:rgba(14,35,51,.42);z-index:700;display:flex;align-items:flex-end">
    <button type="button" id="doadetailbg" aria-label="{E(t["close"])}" style="position:absolute;inset:0;border:0;background:transparent"></button>
    <div role="dialog" aria-label="{E(t["placeDetails"])}" class="do-scroll" style="position:relative;width:100%;max-height:80%;overflow:auto;background:#fff;border-radius:16px 16px 0 0;padding:12px;display:flex;flex-direction:column;gap:10px">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
        <span id="doadetailtitle" style="font-size:16px;font-weight:700"></span>
        <button type="button" id="doadetailclose" aria-label="{E(t["close"])}" style="width:40px;height:40px;border:1px solid #dde5ec;border-radius:10px;background:#fff">×</button>
      </div>
      <div id="doadetailitems" style="display:flex;flex-direction:column;gap:10px"></div>
    </div>
  </div>

  <div id="doatourswrap" hidden style="position:absolute;inset:0;background:#fff;z-index:720;display:flex;flex-direction:column">
    <div style="display:flex;align-items:center;gap:8px;padding:10px 12px;border-bottom:1px solid #dde5ec">
      <button type="button" id="doatoursclose" aria-label="{E(t["close"])}" style="width:44px;height:44px;border:1px solid #dde5ec;border-radius:10px;background:#fff">‹</button>
      <span style="font-size:16px;font-weight:700;flex:1">{E(t["tours"])}</span>
    </div>
    <div class="do-scroll" style="flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:10px">
      <input id="doatoursearch" type="search" aria-label="{E(t["tours"])}" placeholder="{E(t["searchTour"])}" style="height:46px;padding:0 12px;border:1px solid #dde5ec;border-radius:12px">
      <div id="doatourchips" class="do-scroll" style="display:flex;gap:6px;overflow-x:auto;flex:0 0 auto;min-height:38px"></div>
      <div id="doatourlist" style="display:flex;flex-direction:column;gap:10px"></div>
      <span id="doatoursempty" hidden style="font-size:14px;color:#5a6b7b">{E(t["emptyTitle"])}</span>
    </div>
  </div>

  <div id="doabookingwrap" hidden style="position:absolute;inset:0;background:rgba(14,35,51,.42);z-index:740;display:flex;align-items:flex-end">
    <div role="dialog" aria-label="{E(t["book"])}" style="width:100%;background:#fff;border-radius:16px 16px 0 0;padding:12px;display:flex;flex-direction:column;gap:10px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:16px;font-weight:700">{E(t["book"])}</span>
        <button type="button" id="doabkclose" aria-label="{E(t["close"])}" style="width:40px;height:40px;border:1px solid #dde5ec;border-radius:10px;background:#fff">×</button>
      </div>
      <div id="doabkdone" hidden style="padding:12px;border:1px solid #cfe9dd;border-radius:12px;background:#f2fbf7;display:flex;flex-direction:column;gap:4px">
        <span style="font-size:14px;font-weight:700;color:#0b7a55">{E(t["bookingDone"])}</span>
        <span id="doabksum2" style="font-size:13px;color:#5a6b7b"></span>
      </div>
      <div id="doabkform" style="display:flex;flex-direction:column;gap:10px">
        <span id="doabksum" style="font-size:13px;color:#5a6b7b"></span>
        <input id="doabkname" aria-label="{E(t["name"])}" placeholder="{E(t["name"])}" style="height:48px;padding:0 12px;border:1px solid #dde5ec;border-radius:12px">
        <input id="doabkphone" aria-label="{E(t["phone"])}" placeholder="{E(t["phone"])}" inputmode="tel" style="height:48px;padding:0 12px;border:1px solid #dde5ec;border-radius:12px">
        <span id="doabkinvalid" role="alert" hidden style="font-size:13px;color:#8c2d20">{E(t["bookingInvalid"])}</span>
        <span id="doabkerr" role="alert" hidden style="font-size:13px;color:#8c2d20">{E(t["sendErr"])}</span>
        <button type="button" id="doabksend" style="height:50px;border:0;border-radius:12px;background:#0d94ae;color:#fff;font-size:15px;font-weight:600">{E(t["sendRequest"])}</button>
      </div>
    </div>
  </div>

  <div id="doatoast" role="status" hidden style="position:absolute;left:12px;right:12px;bottom:80px;z-index:800;padding:12px 14px;background:#0b2f4d;color:#fff;border-radius:12px;font-size:14px;text-align:center"></div>
</div>
<script>window.DOAT={J(doat)};window.FH_CFG={J(fh_cfg)};</script>
<script>
document.addEventListener('click',function(e){{var b=e.target.closest('[data-acc]');if(!b||!window.DOA_GO)return;window.DOA_GO(b.getAttribute('data-acc'));}});
</script>
<script src="{TRAVEL_ASSET[lang]}"></script>
<script src="{LEAFLET_JS}"></script>
<script defer src="/assets/weather.js"></script>
<script defer src="{ASSET["app_mobile"]}"></script>
<script type="module" src="{ASSET.get("auth", "/assets/auth.js")}"></script>
<script defer src="{ASSET.get("app", "/assets/app.js")}"></script>
</body>
</html>"""


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def render_booking_admin():
    cfg = {k: AUTH.get(k, "") for k in ("apiKey", "authDomain", "projectId",
                                         "storageBucket", "messagingSenderId", "appId")}
    return f'''<!doctype html><html lang="ka"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>ჯავშნების მართვა — RentUp</title>
<link rel="stylesheet" href="{ASSET["css"]}"><style>
body{{background:#07101a;color:#edf6fc}}#booking-admin{{width:min(1100px,94%);margin:30px auto}}.admin-head{{display:flex;justify-content:space-between;align-items:center}}
.admin-filters{{display:flex;gap:10px;margin:20px 0}}.admin-booking{{display:grid;grid-template-columns:minmax(250px,1fr) 170px 170px auto;gap:12px;align-items:end;padding:15px;margin:8px 0;border:1px solid #26384a;border-radius:14px;background:#0d1824}}
.admin-booking>div,.admin-booking label{{display:grid;gap:5px}}.admin-booking span,.admin-booking label{{font-size:13px;color:#9db0c2}}.admin-note{{padding:20px;border:1px solid #26384a;border-radius:12px}}.admin-note.error{{border-color:#ef4444;color:#fecaca}}
@media(max-width:760px){{.admin-booking{{grid-template-columns:1fr}}}}</style></head><body>
<main id="booking-admin"></main><script>window.FH_ADMIN_CFG={J(cfg)};</script><script type="module" src="{ASSET["admin_bookings"]}"></script></body></html>'''


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    out = args[0] if args else "dist"
    strict = "--strict" in sys.argv
    validate_only = "--validate-only" in sys.argv
    # Internal documentation is opt-in. Netlify cannot password-protect a
    # single path on this plan, so anything shipped under /docs/ is readable
    # by anyone who knows the URL. Default off means a production build is
    # safe even when the flag is forgotten.
    with_docs = "--with-docs" in sys.argv
    report = validate(SITE, CARS_ALL, REGIONS_ALL, ATTRACTIONS_ALL, ROUTES_ALL,
                      PAGES, POSTS_ALL)
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    if report.errors or (strict and report.warnings):
        for error in report.errors:
            print(f"ERROR: {error}")
        if strict and report.warnings:
            print("ERROR: strict mode treats warnings as publication blockers")
        raise SystemExit(2)
    if validate_only:
        print("✔ content validation passed")
        return
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)

    # These are written again by write_hashed under a content-hashed name, and
    # the HTML only ever links the hashed one. Copying the plain source as well
    # leaves an unversioned duplicate that no page requests but a browser can
    # still cache indefinitely.
    hashed_sources = {"explorer.js", "planner.js", "auth.js", "booking.js", "analytics.js", "daytrip.js",
                      "community.js", "admin-bookings.js", "app.js", "app-mobile.js", "trip.js",
                      "catalogue.js"}
    for sdir, dst in (("static", os.path.join(out, "assets")),
                      ("admin", os.path.join(out, "admin"))):
        if os.path.isdir(sdir):
            skip = (lambda d, names: [n for n in names if n in hashed_sources]) \
                if sdir == "static" else None
            shutil.copytree(sdir, dst, dirs_exist_ok=True, ignore=skip)

    # Internal team documentation, only with --with-docs. The markdown sources
    # never ship. Even when included it stays out of robots.txt and the
    # sitemap, but noindex is not access control — see docs/08-build-architecture.
    if with_docs and os.path.isdir("docs"):
        docs_dst = os.path.join(out, "docs")
        os.makedirs(docs_dst, exist_ok=True)
        for name in sorted(os.listdir("docs")):
            if name.endswith(".html"):
                shutil.copy2(os.path.join("docs", name),
                             os.path.join(docs_dst, name))

    write_hashed(out, "style.css", build_css(DESIGN), "css", also_plain=True)
    for fn, key in (("explorer.js", "explorer"), ("planner.js", "planner"), ("workspace.js", "workspace"),
                    ("app-mobile.js", "app_mobile"), ("trip.js", "trip"),
                    ("auth.js", "auth"), ("booking.js", "booking"),
                    ("community.js", "community"), ("admin-bookings.js", "admin_bookings"),
                    ("analytics.js", "analytics"), ("app.js", "app"),
                    ("catalogue.js", "catalogue"),
                    ("daytrip.js", "daytrip")):
        p = os.path.join("static", fn)
        if os.path.exists(p):
            write_hashed(out, fn, open(p, encoding="utf-8").read(), key)
    for lang in LANGS:
        payload = ("window.EXP=" + JC(explorer_config(lang, "/")) + ";\n" +
                   "window.PLANNER_DATA=" + JC(workspace_planner_data(lang)) + ";\n")
        TRAVEL_ASSET[lang] = write_hashed(out, f"travel-{lang}.js", payload,
                                          f"travel_{lang}")
    write(os.path.join(out, "admin", "bookings.html"), render_booking_admin())
    up = os.path.join("static", "uploads")
    if os.path.isdir(up):
        shutil.copytree(up, os.path.join(out, "uploads"), dirs_exist_ok=True)
    fav = os.path.join(out, "assets", "favicon.svg")
    if os.path.exists(fav):
        shutil.copy2(fav, os.path.join(out, "favicon.svg"))
    sw = os.path.join("static", "sw.js")
    if os.path.exists(sw):
        shutil.copy2(sw, os.path.join(out, "sw.js"))

    n = 0
    for lang in LANGS:
        for page in PAGE_ORDER:
            rel = page_url(lang, page, False).lstrip("/")
            if page == "blog":
                write(os.path.join(out, rel, "index.html"), render_blog_index(lang))
            elif page == "map":
                write(os.path.join(out, rel, "index.html"), render_map_page(lang))
            elif page == "planner":
                target = page_url(lang, "map", False) + "#planner"
                write(os.path.join(out, rel, "index.html"),
                      f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
                      f'<meta charset="utf-8"><meta name="robots" content="noindex">'
                      f'<link rel="canonical" href="{page_url(lang, "map")}">'
                      f'<meta http-equiv="refresh" content="0;url={target}">'
                      f'<script>location.replace({J(target)})</script></html>')
            else:
                write(os.path.join(out, rel, "index.html"), render_static_page(lang, page))
            n += 1
        card_rel = page_url(lang, "card", False).lstrip("/")
        write(os.path.join(out, card_rel, "index.html"), render_business_card(lang))
        n += 1
        app_rel = (lang_root(lang) + "app/").lstrip("/")
        write(os.path.join(out, app_rel, "index.html"), render_app_page(lang))
        n += 1
        trip_rel = (lang_root(lang) + "trip/").lstrip("/")
        write(os.path.join(out, trip_rel, "index.html"), render_trip_page(lang))
        n += 1
        tours_rel = (lang_root(lang) + "tours/").lstrip("/")
        write(os.path.join(out, tours_rel, "index.html"), render_tours_page(lang))

        # ── car-rental cluster ────────────────────────────────────────────
        html_hub = render_car_rental_hub(lang)
        if html_hub:
            write(os.path.join(out, rental_hub_url(lang, False).lstrip("/"), "index.html"), html_hub)
            n += 1
        for _k in RENTAL_PLACES:
            _h = render_rental_location(lang, _k)
            if _h:
                write(os.path.join(out, rental_place_url(lang, _k, False).lstrip("/"), "index.html"), _h)
                n += 1
        for _k in SEO_CATEGORY_ORDER:
            _h = render_rental_category(lang, _k)
            if _h:
                write(os.path.join(out, rental_cat_url(lang, _k, False).lstrip("/"), "index.html"), _h)
                n += 1

        # ── travel cluster: planner landing + itineraries ─────────────────
        _pl = render_planner_landing(lang)
        if _pl:
            write(os.path.join(out, planner_landing_url(lang, False).lstrip("/"), "index.html"), _pl)
            n += 1
        _ih = render_itineraries_hub(lang)
        if _ih:
            write(os.path.join(out, itin_hub_url(lang, False).lstrip("/"), "index.html"), _ih)
            n += 1
        for _sl, _it in ITINERARIES.items():
            _h = render_itinerary(lang, _sl, _it)
            if _h:
                write(os.path.join(out, itin_url(lang, _sl, False).lstrip("/"), "index.html"), _h)
                n += 1

        _dt = render_day_trip(lang)
        if _dt:
            write(os.path.join(out, day_trip_url(lang, False).lstrip("/"), "index.html"), _dt)
            n += 1

        # ── index hubs: /attractions/, /routes/, /regions/ ────────────────
        for _kind, _fn in (("attractions", render_attractions_hub),
                           ("routes", render_routes_hub),
                           ("regions", render_regions_hub)):
            _h = _fn(lang)
            if _h:
                write(os.path.join(out, index_hub_url(lang, _kind, False).lstrip("/"),
                                   "index.html"), _h)
                n += 1

        # ── guides cluster ────────────────────────────────────────────────
        _gh = render_guides_hub(lang)
        if _gh:
            write(os.path.join(out, guides_hub_url(lang, False).lstrip("/"), "index.html"), _gh)
            n += 1
        for _sl, _g in GUIDES.items():
            _h = render_guide(lang, _sl, _g)
            if _h:
                write(os.path.join(out, guide_url(lang, _sl, False).lstrip("/"), "index.html"), _h)
                n += 1
        n += 1
        # Preserve old bookmarked pricing URLs, but send visitors to the fleet where all rates live.
        pricing_rel = lang_root(lang).lstrip("/") + PAGE_SLUG["pricing"]
        fleet_target = page_url(lang, "fleet", False)
        write(os.path.join(out, pricing_rel, "index.html"),
              f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
              f'<meta charset="utf-8"><meta name="robots" content="noindex">'
              f'<link rel="canonical" href="{page_url(lang, "fleet")}">'
              f'<meta http-equiv="refresh" content="0;url={fleet_target}">'
              f'<script>location.replace({J(fleet_target)})</script></html>')
        for key, r in REGIONS.items():
            write(os.path.join(out, region_url(lang, key, False).lstrip("/"), "index.html"),
                  render_region(lang, key, r))
            n += 1
        for slug, a in ATTRACTIONS.items():
            write(os.path.join(out, attr_url(lang, slug, False).lstrip("/"), "index.html"),
                  render_attraction(lang, slug, a))
            n += 1
        for slug, r in ROUTES.items():
            write(os.path.join(out, route_url(lang, slug, False).lstrip("/"), "index.html"),
                  render_route(lang, slug, r))
            n += 1
        for slug, c in CARS.items():
            write(os.path.join(out, car_url(lang, slug, False).lstrip("/"), "index.html"),
                  render_car(lang, slug, c))
            n += 1
        for slug, p in POSTS.items():
            write(os.path.join(out, post_url(lang, slug, False).lstrip("/"), "index.html"),
                  render_post(lang, slug, p))
            n += 1

    for lang in LANGS:
        write(os.path.join(out, "data", f"points-{lang}.json"),
              J({"pts": explorer_points(lang)}))
        _, chunks = explorer_chunks(lang)
        for region, body in chunks.items():
            write(os.path.join(out, "data", "points", lang, f"{region}.json"),
                  J(body))
        for slug, a in ATTRACTIONS.items():
            write(os.path.join(out, "data", "attr", lang, f"{slug}.json"),
                  J(attr_detail(lang, slug, a)))

    children = sitemap_children()
    for cname, entries in children.items():
        write(os.path.join(out, "sitemaps", f"{cname}.xml"), _sitemap_urls(entries))
    for name, data in [("sitemap.xml", sitemap_index(children)),
                       ("robots.txt", robots(with_docs)),
                       ("llms.txt", llms_txt()), ("llms-full.txt", llms_full_txt()),
                       ("404.html", render_404()), (".nojekyll", "")]:
        write(os.path.join(out, name), data)

    print(f"✔ {n} HTML გვერდი ({len(CARS)} ავტომობილი, {len(POSTS)} სტატია, {len(LANGS)} ენა) → ./{out}")


if __name__ == "__main__":
    main()
