#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
სტატიკური საიტის გენერატორი — კონტენტი იკითხება content/*.yml-იდან (ადმინიდან იმართება).
გამოყენება:  python3 build.py [outdir]
"""
import glob, html, json, os, re, shutil, sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml
import markdown as md
from sitegen.validation import is_public, validate

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

ALL_LANGS = ["ka", "en", "ru", "fa", "he", "ar"]
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
             "community": "community/", "about": "about/", "contact": "contact/", "software": "fleet-management-software/"}

TODAY = date.today().isoformat()
E = lambda s: html.escape(str(s), quote=True)                # noqa: E731
J = lambda o: json.dumps(o, ensure_ascii=False, indent=2)    # noqa: E731


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

PAGES = {os.path.splitext(os.path.basename(p))[0]: load(p)
         for p in glob.glob("content/pages/*.yml")}
CARS = {os.path.splitext(os.path.basename(p))[0]: load(p)
        for p in sorted(glob.glob("content/cars/*.yml"))}
CARS_ALL = CARS
CARS = {k: v for k, v in CARS.items() if is_public(v)}
CARS = dict(sorted(CARS.items(), key=lambda kv: kv[1].get("order", 999)))
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


def gel_to_usd(gel):
    """Convert the GEL source price to an approximate USD price.

    Business rule: divide by the admin-managed exchange rate and round half-up
    to the configured USD step (10 dollars by default).
    """
    rate = Decimal(str(SITE.get("usd_rate", 2.6)))
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
    return "/" if lang == "ka" else f"/{lang}/"


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
    if lang != "ka" and href.startswith("/") and not href.startswith(f"/{lang}/"):
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
        return cars_grid(b.get("category"), lang)
    raise ValueError(f"უცნობი ბლოკის ტიპი: {t}")


def cars_grid(category, lang):
    items = [(s, c) for s, c in CARS.items() if not category or c["category"] == category]
    out = []
    for slug, c in items:
        L = c[lang]
        img = c.get("image")
        ph = (f'<div class="ph"><img src="{E(img)}" alt="{E(L["name"])} — '
              f'{E(cat_label(c["category"], lang))}" loading="lazy" width="640" height="400"></div>'
              if img else f'<div class="ph">{E(L["name"])}</div>')
        feats = "".join(f"<li>{inline(x, lang)}</li>" for x in L.get("features", [])[:3])
        unit = SPECS["units"]["day"][lang]
        out.append(
            f'<article class="car">{ph}<div class="in">'
            f'<h3><a href="{car_url(lang, slug, False)}">{E(L["name"])}</a></h3>'
            f'<p class="sub">{E(L.get("summary", ""))}</p><ul>{feats}</ul>'
            f'<div class="foot"><span class="p">{E(money(c["price_1_6"]))} '
            f'<small>/ {E(unit)}</small></span>'
            f'<span class="car-actions"><a class="more" href="{car_url(lang, slug, False)}">'
            f'{E(UI[lang]["ui"]["more"])} →</a>'
            f'<button class="book-car-link" type="button" data-booking-open data-car="{E(slug)}" data-car-name="{E(L["name"])}">'
            f'{E(BOOKING_TEXT[lang]["book"])}</button></span></div></div></article>')
    return f'<div class="cars">{"".join(out)}</div>'


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
    return {
        "@type": ["AutoRental", "LocalBusiness"],
        "@id": SITE_URL + "/#organization",
        "name": BRAND,
        "alternateName": SITE["rental_brand_ka"],
        "url": SITE_URL + lang_root(lang),
        "description": META[lang]["org_desc"],
        "telephone": SITE["phone_e164"],
        "email": SITE["email"],
        "foundingDate": SITE["founded"],
        "priceRange": "$$",
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
        "sameAs": SITE["social"],
    }


def website_node(lang):
    return {"@type": "WebSite", "@id": SITE_URL + "/#website",
            "url": SITE_URL + lang_root(lang), "name": BRAND,
            "inLanguage": lang, "publisher": {"@id": SITE_URL + "/#organization"}}


def crumbs_node(lang, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
        for i, (n, u) in enumerate(trail)]}


def faq_node(blocks):
    qas = [x for b in blocks if b["type"] == "faq" for x in b["items"]]
    if not qas:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": x["q"],
         "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in qas]}


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
        "offers": {"@type": "Offer", "priceCurrency": "GEL",
                   "price": c["price_1_6"], "availability": ("https://schema.org/InStock"
                       if c.get("available", True) else "https://schema.org/OutOfStock"),
                   "priceSpecification": {
                       "@type": "UnitPriceSpecification", "price": c["price_1_6"],
                       "priceCurrency": "GEL", "unitCode": "DAY",
                       "referenceQuantity": {"@type": "QuantitativeValue", "value": 1,
                                             "unitCode": "DAY"}},
                   "seller": {"@id": SITE_URL + "/#organization"}},
    }
    if c.get("image"):
        node["image"] = SITE_URL + c["image"] if c["image"].startswith("/") else c["image"]
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
        node["image"] = SITE_URL + p["image"] if p["image"].startswith("/") else p["image"]
    return node


# ══════════════════════════════════════════════════════════════ chrome
LEAFLET_CSS = "/assets/leaflet/leaflet.css"
LEAFLET_JS = "/assets/leaflet/leaflet.js"


ASSET = {"css": "/assets/style.css", "explorer": "/assets/explorer.js",
         "planner": "/assets/planner.js"}


def _hash(data):
    import hashlib
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()[:10]


def write_hashed(out, rel, data, key):
    """ჩაწერს ფაილს შიგთავსის ჰეშით სახელში — ბრაუზერი ძველს ვეღარ აჩვენებს."""
    base, ext = os.path.splitext(rel)
    name = base + "." + _hash(data) + ext
    write(os.path.join(out, "assets", name), data)
    write(os.path.join(out, "assets", rel), data)
    ASSET[key] = "/assets/" + name
    return ASSET[key]


def head_html(lang, current, title, desc, keywords, url, alternates, depth, ld,
              og_type="website", image=None, leaflet=False):
    css_href = ASSET["css"]
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{u}">'
                     for l, u in alternates.items())
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{alternates["en"]}">'
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
<meta name="apple-mobile-web-app-title" content="Fleet House">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="keywords" content="{E(keywords)}">
<link rel="canonical" href="{url}">
{alts}
<meta name="robots" content="{"noindex, nofollow" if current == "account" else "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"}">
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
<link rel="apple-touch-icon" href="/assets/app-icon.svg">
<link rel="manifest" href="/assets/manifest.webmanifest">
<link rel="stylesheet" href="{css_href}">{lf}
<script type="application/ld+json">
{J(ld)}
</script>"""


def header_html(lang, current):
    u = UI[lang]
    CUR = ' aria-current="page"'
    # Trip planning and community are the product's primary navigation.
    # Fleet stays available, but appears contextually and in the secondary menu.
    more_pages = {"fleet", "terms", "faq", "blog", "software"}
    lis = "".join(
        f'<li><a href="{page_url(lang, "map", False) + "#planner" if p == "planner" else page_url(lang, p, False)}"'
        f'{CUR if p == current else ""}>{E(u["nav"][p])}</a></li>'
        for p in PAGE_ORDER if p not in NAV_HIDDEN and p not in more_pages)
    more = "".join(
        f'<li><a href="{page_url(lang, p, False)}"'
        f'{CUR if p == current else ""}>{E(u["nav"][p])}</a></li>'
        for p in PAGE_ORDER if p in more_pages)
    langs = "".join(
        f'<a href="{lang_root(l)}" hreflang="{l}" lang="{l}" '
        f'class="{"on" if l == lang else ""}" title="{E(LANG_LABEL[l])}">{LANG_SHORT[l]}</a>'
        for l in LANGS)
    logo_img = DESIGN.get("logo_image")
    mark = DESIGN.get("logo_mark") or "".join(w[0] for w in BRAND.split()[:2]).upper()
    logo = (f'<img src="{E(logo_img)}" alt="" aria-hidden="true">'
            f'<span class="logo-name">{E(BRAND)} <small>{E(u["ui"]["logo_sub"])}</small></span>' if logo_img
            else f'<span class="mark" aria-hidden="true">{E(mark)}</span>'
                 f'{E(BRAND)} <small>{E(u["ui"]["logo_sub"])}</small>')
    return f"""<header class="site-head"><div class="head-in">
<a class="logo" href="{lang_root(lang)}">{logo}</a>
<nav class="main" aria-label="{E(u['ui']['nav_label'])}"><ul>{lis}
<li class="nav-more"><details><summary aria-label="More">•••</summary><ul>{more}</ul></details></li>
</ul></nav>
<div class="head-actions"><span class="head-tel"><a dir="ltr" href="tel:{SITE['phone_e164']}">{E(SITE['phone'])}</a></span></div>
</div></header><div class="corner-tools"><div class="langs corner-langs" role="group" aria-label="{E(u['ui']['lang_label'])}">{langs}</div><div id="authbox" class="authbox authbox-corner"></div></div>"""


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
    return f"""<footer class="site-foot"><div class="wrap"><div class="foot-compact">
<nav aria-label="{E(u['ui']['foot_pages'])}">
<a href="{page_url(lang, 'fleet', False)}">{E(u['nav']['fleet'])}</a>
<a href="{page_url(lang, 'contact', False)}">{E(u['nav']['contact'])}</a></nav>
<div class="foot-contact">
<a dir="ltr" href="tel:{SITE['phone_e164']}">{E(SITE['phone'])}</a>
<a dir="ltr" href="tel:{SITE['mobile_e164']}">{E(SITE['mobile'])}</a>
<a dir="ltr" href="mailto:{SITE['email']}">{E(SITE['email'])}</a>
<span>{E(a['street'])}, {E(a['city'])}</span></div>
</div><div class="foot-bottom">
<span>© {date.today().year} {E(BRAND)}. {E(u['ui']['rights'])}</span>
</div></div></footer>"""


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
        cfg["booking"] = BOOKING
        cfg["whatsapp"] = str(SITE.get("whatsapp") or SITE.get("mobile_e164", "")).replace("+", "").replace(" ", "")
        cfg["siteUrl"] = SITE_URL
        cfg["t"] = {k: u["ui"][k] for k in (
            "account", "sign_in", "sign_up", "sign_out", "with_google", "or_email", "email",
            "password", "forgot", "reset_sent", "why_account", "legal_note", "please_sign_in",
            "no_trips", "to_planner", "planned", "done", "mark_done", "mark_planned", "open",
            "delete", "confirm_del", "days", "stops", "save_trip", "saved") if k in u["ui"]}
        fb = (f'\n<script>window.FH_CFG={J(cfg)};</script>'
              f'\n<script type="module" src="{ASSET.get("auth", "/assets/auth.js")}"></script>'
              f'\n<script type="module" src="{ASSET.get("booking", "/assets/booking.js")}"></script>'
              f'\n<script type="module" src="{ASSET.get("community", "/assets/community.js")}"></script>'
              f'\n<script defer src="{ASSET.get("app", "/assets/app.js")}"></script>')
    inquiry = inquiry_widget(lang, current) if current in ("index", "fleet", "map", "planner") else ""
    return (f'<!DOCTYPE html>\n<html lang="{lang}" dir="{LANG_DIR[lang]}">\n<head>\n{head}\n'
            f'{style}</head>\n<body class="page-{E(current)}">\n'
            f'<a class="skip" href="#main">{E(u["ui"]["skip"])}</a>\n'
            f'{header_html(lang, current)}\n{body}\n{inquiry}{footer_html(lang)}\n{tail}{fb}\n</body>\n</html>\n')


def inquiry_widget(lang, context=""):
    tx = {
        "ka": ("დაჯავშნეთ ავტომობილი", "არჩეული ავტომობილი", "დაწყება", "დაბრუნება", "სახელი", "ტელეფონი / WhatsApp", "შენიშვნა (არასავალდებულო)", "WhatsApp", "მოთხოვნის გაგზავნა", "ხელმისაწვდომობას სწრაფად გადავამოწმებთ და დაგიკავშირდებით.", "დახურვა"),
        "en": ("Book a car", "Selected car", "Start date", "Return date", "Name", "Phone / WhatsApp", "Notes (optional)", "WhatsApp", "Send request", "We’ll quickly confirm availability and contact you.", "Close"),
        "ru": ("Забронировать автомобиль", "Выбранный автомобиль", "Дата начала", "Дата возврата", "Имя", "Телефон / WhatsApp", "Комментарий (необязательно)", "WhatsApp", "Отправить запрос", "Мы быстро проверим наличие и свяжемся с вами.", "Закрыть"),
        "fa": ("رزرو خودرو", "خودروی انتخابی", "تاریخ شروع", "تاریخ بازگشت", "نام", "تلفن / واتس‌اپ", "یادداشت (اختیاری)", "واتس‌اپ", "ارسال درخواست", "موجودی را سریع بررسی کرده و با شما تماس می‌گیریم.", "بستن"),
        "he": ("הזמנת רכב", "הרכב שנבחר", "תאריך התחלה", "תאריך החזרה", "שם", "טלפון / WhatsApp", "הערות (לא חובה)", "WhatsApp", "שליחת בקשה", "נבדוק זמינות במהירות וניצור קשר.", "סגירה"),
        "ar": ("حجز سيارة", "السيارة المختارة", "تاريخ البدء", "تاريخ الإرجاع", "الاسم", "الهاتف / واتساب", "ملاحظات (اختياري)", "واتساب", "إرسال الطلب", "سنتحقق من التوفر سريعًا ونتواصل معك.", "إغلاق")
    }[lang]
    return f'''<div class="booking-dialog" data-booking-dialog hidden role="dialog" aria-modal="true" aria-labelledby="booking-title-{lang}"><div class="booking-modal-card">
<button class="booking-close" type="button" data-booking-close aria-label="{E(tx[10])}">×</button><div class="booking-brand" aria-hidden="true">SL</div>
<form class="inquiry-mini" data-inquiry name="rental-inquiry" method="POST" data-netlify="true" netlify-honeypot="company" data-lang="{lang}">
<input type="hidden" name="form-name" value="rental-inquiry"><input type="hidden" name="context" value="{E(context)}"><input type="hidden" name="requested_car" value=""><input type="hidden" name="page_url" value=""><p class="hp" hidden><label>Company<input name="company" tabindex="-1" autocomplete="off"></label></p>
<h2 id="booking-title-{lang}">{E(tx[0])}</h2><p class="booking-lead">{E(tx[9])}</p><div class="booking-choice" data-booking-choice hidden><small>{E(tx[1])}</small><strong></strong></div>
<div class="inquiry-grid"><label>{E(tx[2])}<input name="start" type="date" required></label><label>{E(tx[3])}<input name="end" type="date" required></label><label>{E(tx[4])}<input name="name" required autocomplete="name"></label><label>{E(tx[5])}<input name="phone" required autocomplete="tel"></label><label class="inquiry-notes">{E(tx[6])}<textarea name="notes" rows="2"></textarea></label></div>
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
    if lang != "ka":
        depth += 1
    body = []
    tail_js = ""
    if page == "index":
        h = dict(p["hero"])
        h.update(HOME_HERO[lang])
        p["h1"] = h["h1"]
        hero_cta = {
            "ka": ("დაიწყე ტურის დაგეგმვა", "ნახე საჯარო ტურები", "დაწყება უფასოა · რეგისტრაცია მხოლოდ შენახვისა და გაზიარებისთვის დაგჭირდება"),
            "en": ("Start planning your trip", "Explore public trips", "Start for free · Sign in only when you want to save or share"),
            "ru": ("Начать планирование", "Смотреть публичные поездки", "Начните бесплатно · Вход нужен только для сохранения и публикации"),
            "fa": ("برنامه‌ریزی سفر را شروع کنید", "سفرهای عمومی را ببینید", "شروع رایگان است · ورود فقط برای ذخیره یا اشتراک‌گذاری لازم است"),
            "he": ("התחילו לתכנן טיול", "גלו טיולים ציבוריים", "מתחילים בחינם · כניסה נדרשת רק לשמירה או לשיתוף"),
            "ar": ("ابدأ تخطيط رحلتك", "استكشف الرحلات العامة", "ابدأ مجانًا · تسجيل الدخول مطلوب فقط للحفظ أو المشاركة"),
        }[lang]
        quick = {
            "ka": (("მაქვს იდეა", "რუკაზე ადგილების აღმოჩენა", "#explore"),
                   ("მინდა მზა გეგმა", "სტანდარტული ტურიდან დაწყება", "#planner"),
                   ("მივდივარ სხვებთან", "საჯარო ტურების ნახვა", page_url(lang, "community", False))),
            "en": (("I have an idea", "Discover places on the map", "#explore"),
                   ("I want a ready plan", "Start with a standard tour", "#planner"),
                   ("I want company", "Browse public trips", page_url(lang, "community", False))),
            "ru": (("У меня есть идея", "Найти места на карте", "#explore"),
                   ("Мне нужен готовый план", "Начать со стандартного тура", "#planner"),
                   ("Ищу попутчиков", "Смотреть публичные поездки", page_url(lang, "community", False))),
            "fa": (("ایده دارم", "کشف مکان‌ها روی نقشه", "#explore"),
                   ("برنامه آماده می‌خواهم", "شروع با یک تور استاندارد", "#planner"),
                   ("همسفر می‌خواهم", "مشاهده سفرهای عمومی", page_url(lang, "community", False))),
            "he": (("יש לי רעיון", "גילוי מקומות במפה", "#explore"),
                   ("אני רוצה מסלול מוכן", "התחלה מטיול סטנדרטי", "#planner"),
                   ("אני מחפש שותפים", "צפייה בטיולים ציבוריים", page_url(lang, "community", False))),
            "ar": (("لدي فكرة", "اكتشف الأماكن على الخريطة", "#explore"),
                   ("أريد خطة جاهزة", "ابدأ بجولة قياسية", "#planner"),
                   ("أبحث عن رفقاء", "تصفح الرحلات العامة", page_url(lang, "community", False))),
        }[lang]
        x = TRAVEL[lang]["exp"]
        facts = "".join(f"<div><b>{E(x2['v'])}</b><span>{E(x2['k'])}</span></div>"
                        for x2 in h["facts"])
        mp, tail_js = travel_workspace_block(lang, depth, "64vh", hero=True, initial="planner")
        quick_html = "".join(
            f'<a class="home-quick-card" href="{E(q[2])}"><span>{i}</span><div><b>{E(q[0])}</b><small>{E(q[1])}</small></div><i aria-hidden="true">→</i></a>'
            for i, q in enumerate(quick, 1))
        body.append(f'<section class="hero home-hero"><div class="wrap wide home-hero-grid">'
                    f'<div class="home-hero-copy"><span class="kicker">{E(h["kicker"])}</span><h1>{E(p["h1"])}</h1>'
                    f'<p class="lead">{inline(h["lead"], lang)}</p>'
                    f'<div class="home-hero-actions"><a class="btn" href="#planner">{E(hero_cta[0])}</a>'
                    f'<a class="btn alt" href="{page_url(lang, "community", False)}">{E(hero_cta[1])}</a></div>'
                    f'<p class="home-hero-note">✓ {E(hero_cta[2])}</p></div>'
                    f'<aside class="home-quick" aria-label="Quick start">{quick_html}</aside>'
                    f'</div></section>')
        map_section = (f'<section class="sec wide maphero" id="planner"><div class="wrap wide">'
                       f'<div class="map-intro"><h2>{E(x["explore_h"])}</h2>'
                       f'<p class="map-sub">{E(x["explore_sub"])}</p></div>'
                       f'{mp}{legend_html(lang)}</div></section>')
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
        body.append(map_section)
    else:
        body.append(f'<section class="page-head"><div class="wrap"><h1>{E(p["h1"])}</h1>'
                    f'<p class="lead">{inline(p["lead"], lang)}</p></div></section>')
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
            f'<div><dt class="k">{E(contact_tx[2])}</dt><dd class="v"><a dir="ltr" href="tel:{E(SITE["mobile_e164"])}">{E(SITE["mobile"])}</a></dd></div>'
            f'<div><dt class="k">{E(contact_tx[3])}</dt><dd class="v"><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></dd></div>'
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
                      "itemListElement": [
                          {"@type": "ListItem", "position": i + 1,
                           "url": attr_url(lang, s), "name": a[lang]["name"]}
                          for i, (s, a) in enumerate(ATTRACTIONS.items())]})
    if page == "fleet":
        graph.append(offer_catalog(lang))
        graph.append({"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": car_url(lang, s)}
            for i, s in enumerate(CARS)]})

    head = head_html(lang, page, p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, page),
                     {l: page_url(l, page) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph},
                     leaflet=(page == "index"))
    crumbs = crumbs_html(lang, [] if page == "index" else
                         [(u["nav"]["index"], page_url(lang, "index", False)),
                          (u["nav"][page], None)])
    return shell(lang, page, head, crumbs + '<main id="main">' + "".join(body) + "</main>",
                 depth, tail_js)


def render_car(lang, slug, c):
    L = c[lang]
    u = UI[lang]
    depth = 2 if lang == "ka" else 3
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

    feats = "".join(f"<li>{inline(x, lang)}</li>" for x in L.get("features", []))
    body_html = render_md(L.get("body", ""), lang)

    body = f"""<section class="page-head"><div class="wrap">
<h1>{E(L['name'])}</h1><p class="lead">{E(L.get('summary',''))} · {E(cat_label(c['category'], lang))}</p>
</div></section>
<section class="sec"><div class="wrap"><div class="cardetail">
<div class="gal">{main_img}{gal}</div>
<div>
<div class="pricebox"><span class="big">{E(money(c['price_1_6']))} <small>/ {E(SPECS['units']['day'][lang])}</small></span></div>
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
    head = head_html(lang, "fleet", title, desc,
                     f'{L["name"]}, {L["name"]} {u["ui"]["rent_word"]}, {cat_label(c["category"], lang)}',
                     car_url(lang, slug), {l: car_url(l, slug) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph},
                     og_type="product", image=(SITE_URL + img) if img and img.startswith("/") else img)
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
    depth = 1 if lang == "ka" else 2
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
    depth = 2 if lang == "ka" else 3
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
                     image=(SITE_URL + post["image"]) if post.get("image", "").startswith("/") else post.get("image"))
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
}


def tl(lang, group, key):
    """travel.yml-იდან ლეიბლი."""
    return TRAVEL[lang][group].get(str(key), str(key))


def tu(lang, key):
    return TRAVEL[lang]["ui"].get(key, key)


def car_cat_label(cat, lang):
    return cat_label({"economy": "economy", "suv": "suv", "offroad": "offroad"}[cat], lang)


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
    cap = te(lang, "photo_by")
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
        return ""
    c = a.get("image_credit") or {}
    who = c.get("author") or "Wikimedia Commons"
    lic = c.get("license") or ""
    src = c.get("source") or ""
    lurl = c.get("license_url") or ""
    cap = f'{E(te(lang, "photo_by") if "photo_by" in TRAVEL[lang]["exp"] else "Photo")}: '
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
            "img": a.get("image") or "", "r": a.get("rating") or 0,
            "rd": ROAD_RANK_NUM.get(a["road"], 0), "el": a.get("elevation") or 0,
            "bike": a["type"] in {"nature", "lake", "town", "beach", "mountain", "canyon", "waterfall"}
                    and ROAD_RANK_NUM.get(a["road"], 0) <= 2,
        })
    pts.sort(key=lambda p: p["n"])
    return pts


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
<script src="%(js)s"></script>
<script src="/assets/weather.js"></script>
<script>window.EXP=%(cfg)s;</script>
<script src="%(exp)s"></script>"""


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
    visit_labels = {
        "ka": ("ყველა ადგილი", "ნამყოფი ვარ", "არ ვარ ნამყოფი", "ნამყოფი ვარ", "ნამყოფად მონიშვნა"),
        "en": ("All places", "Visited", "Not visited", "Visited", "Mark as visited"),
        "ru": ("Все места", "Посещённые", "Не посещённые", "Посещено", "Отметить посещённым"),
        "fa": ("همه مکان‌ها", "بازدید شده", "بازدید نشده", "بازدید شده", "علامت‌گذاری به‌عنوان بازدیدشده"),
        "he": ("כל המקומות", "ביקרתי", "טרם ביקרתי", "ביקרתי", "סימון כמקום שביקרתי בו"),
        "ar": ("كل الأماكن", "تمت زيارتها", "لم تتم زيارتها", "تمت الزيارة", "وضع علامة تمت الزيارة"),
    }[lang]
    cfg = J({
        "pts": explorer_points(lang),
        "towns": explorer_towns(lang),
        "lang": lang, "base": base, "center": [42.15, 43.6], "zoom": 7,
        "planner": page_url(lang, "map", False) + "#planner",
        "ui": {**{k: v for k, v in x.items()},
               "hrs": u["hrs"], "km": u["km"], "h_short": u["hrs"], "days": u["days"],
               "tip_title": u["tip_title"], "route_title": u["route_title"],
               "nearby_title": u["nearby_title"],
               "visited_yes": visit_labels[3], "visited_mark": visit_labels[4],
               "write_review": {"ka":"რივიუს დაწერა","en":"Write review","ru":"Написать отзыв","fa":"نوشتن نظر","he":"כתיבת ביקורת","ar":"كتابة مراجعة"}[lang],
               "review_saved": {"ka":"რივიუ შენახულია","en":"Review saved","ru":"Отзыв сохранён","fa":"نظر ذخیره شد","he":"הביקורת נשמרה","ar":"تم حفظ المراجعة"}[lang]},
    })
    js = EXPLORER_JS % {"js": LEAFLET_JS, "cfg": cfg, "exp": ASSET["explorer"]}
    html = f'''<div class="explorer{" hero" if hero else ""}">
  <div class="expbar">
    <input id="expq" class="expsearch" type="search" placeholder="{E(x["search_ph"])}"
           aria-label="{E(x["search_ph"])}">
    <div id="expqlist" class="expqlist" role="listbox"></div>
    <select id="exptype" aria-label="{E(x["all_types"])}"><option value="">{E(x["all_types"])}</option>{topts}</select>
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
        <label class="expslider" id="expbudgetwrap">
          <span id="expbudgetv">8 {E(u["hrs"])}</span>
          <input id="expbudget" type="range" min="2" max="72" step="1" value="8">
        </label>
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


def counts_sub(s):
    """{attractions} / {regions} / {routes} — რიცხვები არასდროს ძველდება."""
    if not isinstance(s, str):
        return s
    return (s.replace("{attractions}", str(len(ATTRACTIONS)))
             .replace("{regions}", str(len(REGIONS)))
             .replace("{routes}", str(len(ROUTES)))
             .replace("{cars}", str(len(CARS))))


def render_map_page(lang):
    """Legacy URL: the unified map and planner now live on Home."""
    target = page_url(lang, "index", False)
    canonical = page_url(lang, "index")
    direction = "rtl" if lang in ("fa", "he", "ar") else "ltr"
    return f'''<!doctype html><html lang="{lang}" dir="{direction}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,follow"><link rel="canonical" href="{E(canonical)}">
<meta http-equiv="refresh" content="0;url={E(target)}#explore">
<title>{E(UI[lang]["nav"]["map"])}</title></head><body>
<p><a href="{E(target)}#explore">{E(UI[lang]["nav"]["index"])}</a></p>
<script>(function(){{var h=location.hash||'#explore';location.replace({J(target)}+(location.search||'')+h);}})();</script>
</body></html>'''

    # Kept below temporarily as migration history; unreachable by design.
    p = {k: counts_sub(v) for k, v in PAGES["map"][lang].items()}
    u = UI[lang]
    depth = 1 if lang == "ka" else 2
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
    depth = 2 if lang == "ka" else 3
    sub = {s: a for s, a in ATTRACTIONS.items() if a["region"] == key}
    mp, js = map_block(lang, 420, (r["center_lat"], r["center_lon"]), r["zoom"],
                       attractions=sub, routes={})
    cards = "".join(
        f'<div class="card">'
        + (f'<a class="card-img" href="{attr_url(lang, s, False)}">'
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
    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{mp}</div></section>'
        f'<section class="sec alt"><div class="wrap"><div class="article">{render_md(L["body"], lang)}</div>'
        f'<h2>{E(tu(lang,"best_for"))}</h2><ul>{best}</ul></div></section>'
        f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"driving_title"))}</h2>'
        f'<div class="article">{render_md(L["driving"], lang)}</div></div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"in_region"))} — '
        f'{len(sub)} {E(tu(lang,"obj"))}</h2><div class="cards">{cards}</div></div></section>')
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
    num = SITE.get("whatsapp") or SITE.get("mobile_e164", "").lstrip("+")
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
    depth = 2 if lang == "ka" else 3
    mp, js = map_block(lang, 360, (a["lat"], a["lon"]), 12,
                       attractions={slug: a}, routes={})
    near = "".join(
        f'<div class="card">'
        + (f'<a class="card-img" href="{attr_url(lang, n, False)}">'
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
    title = title[:70] + f" | {BRAND}" if len(title) < 55 else title[:74]
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
        + f'<section class="sec alt"><div class="wrap"><div class="cta">'
          f'<h2>{E(u["ui"]["book_title"])}</h2><p>{inline(u["ui"]["book_text"], lang)}</p>'
          f'<div class="row"><a class="btn" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
          f'<a class="btn ghost" href="{page_url(lang,"fleet",False)}">{E(u["nav"]["fleet"])}</a>'
          f'<a class="btn ghost" href="{region_url(lang, a["region"], False)}">{E(r[lang]["name"])}</a>'
          f"</div></div></div></section>")
    graph = [org_node(lang), website_node(lang),
             {"@type": "TouristAttraction", "@id": attr_url(lang, slug) + "#attraction",
              "name": L["name"], "description": L["short"], "url": attr_url(lang, slug),
              **({"image": SITE_URL + a["image"]} if a.get("image") else {}),
              "geo": {"@type": "GeoCoordinates", "latitude": a["lat"], "longitude": a["lon"],
                      "elevation": a["elevation"]},
              "address": {"@type": "PostalAddress", "addressRegion": r[lang]["name"],
                          "addressCountry": "GE"},
              "isAccessibleForFree": a["entry_fee"] in ("free", "უფასო", "Бесплатно"),
              "touristType": tl(lang, "type", a["type"]),
              "publicAccess": True,
              "containedInPlace": {"@type": "TouristDestination", "name": r[lang]["name"],
                                   "url": region_url(lang, a["region"])}},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], page_url(lang, "map")),
                                (r[lang]["name"], region_url(lang, a["region"])),
                                (L["name"], attr_url(lang, slug))])]
    head = head_html(lang, "map", title, desc,
                     f'{L["name"]}, {tl(lang,"type",a["type"])}, {r[lang]["name"]}',
                     attr_url(lang, slug), {l: attr_url(l, slug) for l in LANGS},
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True,
                     image=(SITE_URL + a["image"]) if a.get("image") else None)
    crumbs = crumbs_html(lang, [(u["nav"]["index"], page_url(lang, "index", False)),
                                (u["nav"]["map"], page_url(lang, "map", False)),
                                (r[lang]["name"], region_url(lang, a["region"], False)),
                                (L["name"], None)])
    return shell(lang, "map", head, crumbs + f'<main id="main">{body}</main>', depth, js)


def render_route(lang, slug, r):
    L = r[lang]
    u = UI[lang]
    depth = 2 if lang == "ka" else 3
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
        f'<div class="card"><span class="tag">{E(tl(lang,"type",a["type"]))}</span>'
        f'<h3><a href="{attr_url(lang, s, False)}">{E(a[lang]["name"])}</a></h3>'
        f'<p>{E(a[lang]["short"])}</p>'
        f'<span class="price">{E(a["visit_hours"])} {E(tu(lang,"hrs"))}</span></div>'
        for s, a in wp.items())
    tips = "".join(f"<li>{inline(x, lang)}</li>" for x in L["tips"])
    title = f'{L["name"]} — {r["days"]} {tu(lang,"days")}, {r["distance_km"]} {tu(lang,"km")} | {BRAND}'
    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
    body = (
        f'<section class="page-head"><div class="wrap"><h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{fh}{mp}'
        f'<div class="article">{render_md(L["body"], lang)}</div></div></section>'
        f'<section class="sec alt"><div class="wrap"><h2>{E(tu(lang,"plan_title"))}</h2>'
        f'<div class="article">{render_md(L["plan"], lang)}</div></div></section>'
        f'<section class="sec"><div class="wrap"><h2>{E(tu(lang,"waypoints_title"))}</h2>'
        f'<div class="cards">{stops}</div>'
        f'<h2>{E(tu(lang,"tips_title"))}</h2><ul>{tips}</ul>'
        f'<div class="cta"><h2>{E(u["ui"]["book_title"])}</h2>'
        f'<p>{inline(u["ui"]["book_text"], lang)}</p><div class="row">'
        f'<a class="btn" href="{page_url(lang,"contact",False)}">{E(u["nav"]["contact"])}</a>'
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
        "ka": {"day": "დღე", "people": "ადამიანი", "view": "ნახვა"},
        "en": {"day": "days", "people": "people", "view": "View"},
        "ru": {"day": "дн.", "people": "чел.", "view": "Открыть"},
        "fa": {"day": "روز", "people": "نفر", "view": "مشاهده"},
        "he": {"day": "ימים", "people": "אנשים", "view": "צפייה"},
        "ar": {"day": "أيام", "people": "أشخاص", "view": "عرض"},
    }[lang]
    purpose_by_route = {
        "kakheti-wine-loop": "culinary", "imereti-caves-canyons": "nature",
        "black-sea-adjara": "beach", "military-highway-kazbegi": "mountains",
        "vardzia-borjomi-south": "culture", "svaneti-expedition": "mountains",
        "racha-mountain-loop": "nature",
    }
    standard_tours = [{
        "s": slug, "n": route[lang]["name"], "sh": route[lang]["short"],
        "days": int(route["days"]), "nights": int(route["nights"]), "km": int(route["distance_km"]),
        "season": route["best_season"], "purpose": route.get("purpose", purpose_by_route.get(slug, "classic")),
        "minPeople": int(route.get("min_people", 1)), "maxPeople": int(route.get("max_people", 8)),
        "availableFrom": route.get("available_from", ""), "availableTo": route.get("available_to", ""),
        "img": route.get("image") or "", "u": route_url(lang, slug, False),
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
    purpose_names = {
        "ka": ("კლასიკური", "კულინარიული", "ღვინის", "კულტურული", "ბუნება", "ველო", "მთები", "ზღვა", "ოჯახური"),
        "en": ("Classic", "Culinary", "Wine", "Culture", "Nature", "Cycling", "Mountains", "Beach", "Family"),
        "ru": ("Классический", "Кулинарный", "Винный", "Культурный", "Природа", "Велотур", "Горы", "Море", "Семейный"),
        "fa": ("کلاسیک", "آشپزی", "شراب", "فرهنگی", "طبیعت", "دوچرخه‌سواری", "کوهستان", "ساحل", "خانوادگی"),
        "he": ("קלאסי", "קולינרי", "יין", "תרבות", "טבע", "אופניים", "הרים", "חוף", "משפחתי"),
        "ar": ("كلاسيكية", "الطهي", "النبيذ", "ثقافية", "الطبيعة", "الدراجات", "الجبال", "الشاطئ", "عائلية"),
    }[lang]
    purpose_keys = ("classic", "culinary", "wine", "culture", "nature", "cycling", "mountains", "beach", "family")
    purposes = list(zip(purpose_keys, purpose_names))

    def opt_pace():
        return "".join(
            f'<option value="{v}"{" selected" if v == 480 else ""}>{E(lbl)}</option>'
            for v, lbl in ((360, t["pace_easy"]), (480, t["pace_normal"]), (600, t["pace_full"])))

    form = f"""<div class="pform planner-toolbar">
<div class="pf"><label for="start">{E(t['start'])}</label><select id="start"></select></div>
<div class="pf period-field"><label>{E(labels[0])}</label><div class="date-pair"><input id="datefrom" type="date" aria-label="{E(labels[1])}"><input id="dateto" type="date" aria-label="{E(labels[2])}"></div></div>
<div class="pf"><label for="days">{E(t['days'])}</label><select id="days">
{"".join(f'<option value="{d}"{" selected" if d == 3 else ""}>{d}</option>' for d in range(1, 11))}
</select></div>
<div class="pf derived-month"><label for="month">{E(t['month'])}</label><select id="month"></select></div>
<div class="pf"><label for="party">{E(t['party'])}</label><select id="party">
{"".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n}</option>' for n in range(1, 9))}
</select></div>
<div class="pf tour-purpose-field"><label for="tourpurpose">{E(labels[3])}</label><select id="tourpurpose">{"".join(f'<option value="{k}">{E(v)}</option>' for k,v in purposes)}</select></div>
<div class="pf pf-wide carmode">
<label class="tog"><input type="radio" name="carmode" id="carauto" value="auto" checked>
<span>{E(t['car_auto'])}</span></label>
<label class="tog"><input type="radio" name="carmode" id="carown" value="own">
<span>{E(t['own_car'])}</span></label>
<label class="tog"><input type="radio" name="carmode" id="carpick" value="pick">
<span>{E(t['car_pick'])}</span></label>
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
<div class="pf standard-launch"><label>{E(labels[4])}</label><button type="button" class="btn ghost" id="standardopen">{E(labels[4])} <span id="standardcount"></span></button></div>
<div class="standard-modal" id="standardmodal" hidden><div class="standard-dialog" role="dialog" aria-modal="true" aria-labelledby="standardtitle">
<button type="button" class="standard-close" id="standardclose" aria-label="Close">&#10005;</button>
<div class="standard-dialog-head"><h3 id="standardtitle">{E(labels[4])}</h3><label for="tourpurposemodal">{E(labels[3])}</label><select id="tourpurposemodal">{"".join(f'<option value="{k}">{E(v)}</option>' for k,v in purposes)}</select></div>
<div id="standardtours" class="standard-grid"></div></div></div>
</div>"""

    return form


def travel_workspace_block(lang, depth, height="72vh", hero=False, initial="explore"):
    """Shared travel workspace used on home, map and planner pages."""
    explore, explore_js = explorer_block(lang, depth, height, hero)
    labels = {
        "ka": ("დაგეგმე", "აღმოაჩინე", "მარშრუტი"),
        "en": ("Plan", "Explore", "Route"),
        "ru": ("План", "Открыть", "Маршрут"),
        "fa": ("برنامه‌ریزی", "کاوش", "مسیر"),
        "he": ("תכנון", "גילוי", "מסלול"),
        "ar": ("خطط", "استكشف", "المسار"),
    }[lang]
    form = planner_form_html(lang)
    html = f'''<section class="travel-workspace" data-mode="{E(initial)}">
  <div class="workspace-tabs" role="tablist" aria-label="Travel tools">
    <button type="button" data-workmode="planner">{E(labels[0])}</button>
    <button type="button" data-workmode="explore">{E(labels[1])}</button>
    <button type="button" data-workmode="route">{E(labels[2])}</button>
  </div>
  <div class="workspace-plan">{form}</div>
  {explore}
  <div id="result" class="workspace-result"></div>
</section>'''
    mode_js = '''<script>(function(){
var w=document.querySelector('.travel-workspace');if(!w)return;
function setMode(m){w.dataset.mode=m;w.querySelectorAll('[data-workmode]').forEach(function(b){
b.classList.toggle('on',b.dataset.workmode===m);b.setAttribute('aria-selected',b.dataset.workmode===m?'true':'false');});
if(m==='planner')document.dispatchEvent(new CustomEvent('fh:planner'));
if(window.FH_TRAVEL_MAP)setTimeout(function(){window.FH_TRAVEL_MAP.invalidateSize();},40);}
w.querySelectorAll('[data-workmode]').forEach(function(b){b.onclick=function(){setMode(b.dataset.workmode);history.replaceState(null,'','#'+b.dataset.workmode);};});
window.addEventListener('hashchange',function(){var m=location.hash.slice(1);if(/^(explore|route|planner)$/.test(m))setMode(m);});
var first=location.hash.slice(1);setMode(/^(explore|route|planner)$/.test(first)?first:(w.dataset.mode||'explore'));})();</script>'''
    js = (f'<script>window.PLANNER_DATA={J(planner_data(lang))};</script>\n' +
          explore_js + f'\n<script src="{ASSET["planner"]}"></script>\n' + mode_js)
    return html, js


def render_planner(lang):
    P = PLANNER[lang]
    u = UI[lang]
    depth = 1 if lang == "ka" else 2
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
def source_lastmod(path):
    """Stable sitemap date derived from the content source, not build time."""
    try:
        return date.fromtimestamp(Path(path).stat().st_mtime).isoformat()
    except (OSError, ValueError):
        return TODAY


def sitemap():
    urls = []

    def add(loc_fn, prio, langs=LANGS, source=None):
        lastmod = source_lastmod(source) if source else source_lastmod("build.py")
        for lang in langs:
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

    for page in PAGE_ORDER:
        if page == "planner":
            continue
        if page in NAV_HIDDEN:
            continue
        add(lambda l, p=page: page_url(l, p),
            "1.0" if page == "index" else
            ("0.9" if page in ("fleet", "pricing", "software", "blog") else "0.7"),
            source=Path("content/pages") / f"{page}.yml")
    for slug in CARS:
        add(lambda l, s=slug: car_url(l, s), "0.8", source=Path("content/cars") / f"{slug}.yml")
    for slug in POSTS:
        add(lambda l, s=slug: post_url(l, s), "0.6", source=Path("content/posts") / f"{slug}.yml")
    for key in REGIONS:
        add(lambda l, k=key: region_url(l, k), "0.8", source=Path("content/regions") / f"{key}.yml")
    for slug in ATTRACTIONS:
        add(lambda l, s=slug: attr_url(l, s), "0.7", source=Path("content/attractions") / f"{slug}.yml")
    for slug in ROUTES:
        add(lambda l, s=slug: route_url(l, s), "0.8", source=Path("content/routes") / f"{slug}.yml")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
           "Claude-SearchBot", "anthropic-ai", "PerplexityBot", "Perplexity-User",
           "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot",
           "Meta-ExternalAgent", "cohere-ai", "YandexBot", "Amazonbot",
           "DuckAssistBot", "MistralAI-User"]


def robots():
    out = ["User-agent: *", "Allow: /", "Disallow: /admin/", ""]
    for b in AI_BOTS:
        out += [f"User-agent: {b}", "Allow: /", ""]
    out += [f"Sitemap: {SITE_URL}/sitemap.xml", f"Host: {SITE_URL.split('//')[1]}", ""]
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
        d = (PLANNER["en"] if p == "planner" else PAGES[p]["en"])["desc"]
        out.append(f"- [{u['nav'][p]}]({page_url('en', p)}): {d}")
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
            f'<link rel="stylesheet" href="/assets/style.css"></head><body>'
            f'{header_html(lang, "index")}<main id="main"><section class="page-head">'
            f'<div class="wrap"><h1>{E(u["ui"]["e404_title"])}</h1>'
            f'<p class="lead">{E(u["ui"]["e404_text"])}</p><ul>{links}</ul>'
            f"</div></section></main>{footer_html(lang)}</body></html>")


# ══════════════════════════════════════════════════════════════ main
def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def render_booking_admin():
    cfg = {k: AUTH.get(k, "") for k in ("apiKey", "authDomain", "projectId",
                                         "storageBucket", "messagingSenderId", "appId")}
    return f'''<!doctype html><html lang="ka"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>ჯავშნების მართვა — Fleet House</title>
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

    for sdir, dst in (("static", os.path.join(out, "assets")),
                      ("admin", os.path.join(out, "admin"))):
        if os.path.isdir(sdir):
            shutil.copytree(sdir, dst, dirs_exist_ok=True)

    write_hashed(out, "style.css", build_css(DESIGN), "css")
    for fn, key in (("explorer.js", "explorer"), ("planner.js", "planner"), ("auth.js", "auth"), ("booking.js", "booking"),
                    ("community.js", "community"), ("admin-bookings.js", "admin_bookings"), ("app.js", "app")):
        p = os.path.join("static", fn)
        if os.path.exists(p):
            write_hashed(out, fn, open(p, encoding="utf-8").read(), key)
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
                      f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
                      f'<link rel="canonical" href="{page_url(lang, "map")}">'
                      f'<meta http-equiv="refresh" content="0;url={target}">'
                      f'<script>location.replace({J(target)})</script>')
            else:
                write(os.path.join(out, rel, "index.html"), render_static_page(lang, page))
            n += 1
        # Preserve old bookmarked pricing URLs, but send visitors to the fleet where all rates live.
        pricing_rel = lang_root(lang).lstrip("/") + PAGE_SLUG["pricing"]
        fleet_target = page_url(lang, "fleet", False)
        write(os.path.join(out, pricing_rel, "index.html"),
              f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
              f'<link rel="canonical" href="{page_url(lang, "fleet")}">'
              f'<meta http-equiv="refresh" content="0;url={fleet_target}">'
              f'<script>location.replace({J(fleet_target)})</script>')
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
        for slug, a in ATTRACTIONS.items():
            write(os.path.join(out, "data", "attr", lang, f"{slug}.json"),
                  J(attr_detail(lang, slug, a)))

    for name, data in [("sitemap.xml", sitemap()), ("robots.txt", robots()),
                       ("llms.txt", llms_txt()), ("llms-full.txt", llms_full_txt()),
                       ("404.html", render_404()), (".nojekyll", "")]:
        write(os.path.join(out, name), data)

    print(f"✔ {n} HTML გვერდი ({len(CARS)} ავტომობილი, {len(POSTS)} სტატია, {len(LANGS)} ენა) → ./{out}")


if __name__ == "__main__":
    main()
