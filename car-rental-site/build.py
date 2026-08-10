#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
სტატიკური საიტის გენერატორი — კონტენტი იკითხება content/*.yml-იდან (ადმინიდან იმართება).
გამოყენება:  python3 build.py [outdir]
"""
import glob, html, json, os, re, shutil, sys
from datetime import date, datetime

import yaml
import markdown as md

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

PAGE_ORDER = ["index", "fleet", "pricing", "map", "terms", "faq", "blog",
              "about", "contact", "software"]
PAGE_SLUG = {"index": "", "fleet": "fleet/", "pricing": "pricing/", "map": "map/",
             "terms": "terms/", "faq": "faq/", "blog": "blog/", "about": "about/",
             "contact": "contact/", "software": "fleet-management-software/"}

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
CATS = load("content/settings/categories.yml")["categories"]

PAGES = {os.path.splitext(os.path.basename(p))[0]: load(p)
         for p in glob.glob("content/pages/*.yml")}
CARS = {os.path.splitext(os.path.basename(p))[0]: load(p)
        for p in sorted(glob.glob("content/cars/*.yml"))}
CARS = dict(sorted(CARS.items(), key=lambda kv: kv[1].get("order", 999)))
POSTS = {os.path.splitext(os.path.basename(p))[0]: load(p)
         for p in sorted(glob.glob("content/posts/*.yml"))}
POSTS = {k: v for k, v in sorted(POSTS.items(),
                                 key=lambda kv: str(kv[1].get("date", "")), reverse=True)
         if not v.get("draft")}

REGIONS = {os.path.splitext(os.path.basename(p))[0]: load(p)
           for p in sorted(glob.glob("content/regions/*.yml"))}
REGIONS = dict(sorted(REGIONS.items(), key=lambda kv: kv[1].get("order", 999)))
ATTRACTIONS = {os.path.splitext(os.path.basename(p))[0]: load(p)
               for p in sorted(glob.glob("content/attractions/*.yml"))}
ATTRACTIONS = dict(sorted(ATTRACTIONS.items(),
                          key=lambda kv: (kv[1].get("region", ""), kv[1].get("order", 999))))
ROUTES = {os.path.splitext(os.path.basename(p))[0]: load(p)
          for p in sorted(glob.glob("content/routes/*.yml"))}
ROUTES = dict(sorted(ROUTES.items(), key=lambda kv: kv[1].get("order", 999)))

# რეალურად ხელმისაწვდომი ენები (თარგმანის მიხედვით)
LANGS = [l for l in ALL_LANGS if l in UI and l in META and all(l in p for p in PAGES.values())]

SITE_URL = SITE["site_url"].rstrip("/")
BRAND = SITE["rental_brand"]

from theme import css as build_css  # noqa: E402


# ══════════════════════════════════════════════════════════════ URL helpers
def lang_root(lang):
    return "/" if lang == "ka" else f"/{lang}/"


def page_url(lang, page, absolute=True):
    p = lang_root(lang) + PAGE_SLUG[page]
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
            f'<div class="foot"><span class="p">{E(c["price_1_6"])} ₾ '
            f'<small>/ {E(unit)}</small></span>'
            f'<a class="more" href="{car_url(lang, slug, False)}">'
            f'{E(UI[lang]["ui"]["more"])} →</a></div></div></article>')
    return f'<div class="cars">{"".join(out)}</div>'


# ══════════════════════════════════════════════════════════════ markdown
_MD = md.Markdown(extensions=["tables", "attr_list", "sane_lists"])


def render_md(text, lang):
    _MD.reset()
    out = _MD.convert(text or "")
    out = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{localize_href(m.group(1), lang)}"', out)
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
                   "price": c["price_1_6"], "availability": "https://schema.org/InStock",
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


def head_html(lang, current, title, desc, keywords, url, alternates, depth, ld,
              og_type="website", image=None, leaflet=False):
    css_href = rel_prefix(depth) + "assets/style.css"
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
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="keywords" content="{E(keywords)}">
<link rel="canonical" href="{url}">
{alts}
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
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
<link rel="stylesheet" href="{css_href}">{lf}
<script type="application/ld+json">
{J(ld)}
</script>"""


def header_html(lang, current):
    u = UI[lang]
    CUR = ' aria-current="page"'
    lis = "".join(
        f'<li><a href="{page_url(lang, p, False)}"'
        f'{CUR if p == current else ""}>{E(u["nav"][p])}</a></li>'
        for p in PAGE_ORDER)
    langs = "".join(
        f'<a href="{lang_root(l)}" hreflang="{l}" lang="{l}" '
        f'class="{"on" if l == lang else ""}" title="{E(LANG_LABEL[l])}">{LANG_SHORT[l]}</a>'
        for l in LANGS)
    logo_img = DESIGN.get("logo_image")
    logo = (f'<img src="{E(logo_img)}" alt="{E(BRAND)}">' if logo_img
            else f'<span class="dot"></span>{E(BRAND)} <small>{E(u["ui"]["logo_sub"])}</small>')
    return f"""<header class="site-head"><div class="head-in">
<a class="logo" href="{lang_root(lang)}">{logo}</a>
<nav class="main" aria-label="{E(u['ui']['nav_label'])}"><ul>{lis}</ul></nav>
<span class="head-tel"><a dir="ltr" href="tel:{SITE['phone_e164']}">{E(SITE['phone'])}</a></span>
<div class="langs" role="group" aria-label="{E(u['ui']['lang_label'])}">{langs}</div>
</div></header>"""


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
    links = "".join(f'<li><a href="{page_url(lang, p, False)}">{E(u["nav"][p])}</a></li>'
                    for p in PAGE_ORDER[1:])
    langlinks = "".join(f'<li><a href="{lang_root(l)}" hreflang="{l}" lang="{l}">'
                        f"{E(LANG_LABEL[l])}</a></li>" for l in LANGS)
    return f"""<footer class="site-foot"><div class="wrap"><div class="foot-grid">
<div><h2>{E(u['ui']['foot_about'])}</h2><p>{inline(u['ui']['foot_about_text'], lang)}</p></div>
<div><h2>{E(u['ui']['foot_pages'])}</h2><ul>{links}</ul></div>
<div><h2>{E(u['ui']['foot_contact'])}</h2><ul>
<li><a dir="ltr" href="tel:{SITE['phone_e164']}">{E(SITE['phone'])}</a></li>
<li><a dir="ltr" href="tel:{SITE['mobile_e164']}">{E(SITE['mobile'])}</a></li>
<li><a dir="ltr" href="mailto:{SITE['email']}">{E(SITE['email'])}</a></li>
<li>{E(a['street'])}, {E(a['city'])} {E(SITE['address_zip'])}</li>
<li>{E(u['ui']['hours'])}</li></ul></div>
<div><h2>{E(u['ui']['foot_langs'])}</h2><ul>{langlinks}</ul></div>
</div><div class="foot-bottom">
<span>© {date.today().year} {E(BRAND)}. {E(u['ui']['rights'])}</span>
<span>{E(u['ui']['updated'])}: {TODAY}</span></div></div></footer>"""


def shell(lang, current, head, body, depth, tail=""):
    u = UI[lang]
    fs = LANG_FONT_STACK.get(lang, "")
    style = (f'<style>:root{{--font:{fs}{DESIGN["font_family"]}}}</style>\n' if fs else "")
    return (f'<!DOCTYPE html>\n<html lang="{lang}" dir="{LANG_DIR[lang]}">\n<head>\n{head}\n'
            f'{style}</head>\n<body>\n'
            f'<a class="skip" href="#main">{E(u["ui"]["skip"])}</a>\n'
            f'{header_html(lang, current)}\n{body}\n{footer_html(lang)}\n{tail}\n</body>\n</html>\n')


# ══════════════════════════════════════════════════════════════ page renders
def render_static_page(lang, page):
    p = PAGES[page][lang]
    u = UI[lang]
    depth = 0 if page == "index" else 1
    if lang != "ka":
        depth += 1
    body = []
    if page == "index":
        h = p["hero"]
        facts = "".join(f"<div><b>{E(x['v'])}</b><span>{E(x['k'])}</span></div>"
                        for x in h["facts"])
        body.append(f'<section class="hero"><div class="wrap">'
                    f'<span class="kicker">{E(h["kicker"])}</span><h1>{E(p["h1"])}</h1>'
                    f'<p class="lead">{inline(h["lead"], lang)}</p>'
                    f'<div class="hero-facts">{facts}</div></div></section>')
    else:
        body.append(f'<section class="page-head"><div class="wrap"><h1>{E(p["h1"])}</h1>'
                    f'<p class="lead">{inline(p["lead"], lang)}</p></div></section>')

    sections, cur = [], []
    for b in p["blocks"]:
        if b["type"] == "h2" and cur:
            sections.append(cur); cur = []
        cur.append(b)
    if cur:
        sections.append(cur)
    for i, s in enumerate(sections):
        inner = "\n".join(render_block(b, lang) for b in s)
        body.append(f'<section class="sec{" alt" if i % 2 else ""}">'
                    f'<div class="wrap">{inner}</div></section>')

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
    if page == "pricing":
        graph.append(offer_catalog(lang))
    if page == "fleet":
        graph.append({"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": car_url(lang, s)}
            for i, s in enumerate(CARS)]})

    head = head_html(lang, page, p["title"], p["desc"], p.get("keywords", ""),
                     page_url(lang, page),
                     {l: page_url(l, page) for l in LANGS}, depth,
                     {"@context": "https://schema.org", "@graph": graph})
    crumbs = crumbs_html(lang, [] if page == "index" else
                         [(u["nav"]["index"], page_url(lang, "index", False)),
                          (u["nav"][page], None)])
    return shell(lang, page, head, crumbs + '<main id="main">' + "".join(body) + "</main>", depth)


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
    gal = "".join(f'<img src="{E(g)}" alt="{E(L["name"])}" loading="lazy">'
                  for g in (c.get("gallery") or []))
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
        f'<tr><th scope="row">{E(spec_label(k, lang))}</th><td>{E(c[k])} ₾</td></tr>'
        for k in ("price_1_6", "price_7_29", "price_30") if c.get(k))
    prices += (f'<tr><th scope="row">{E(spec_label("deposit", lang))}</th>'
               f'<td>{E(c["deposit"])} ₾</td></tr>')

    feats = "".join(f"<li>{inline(x, lang)}</li>" for x in L.get("features", []))
    body_html = render_md(L.get("body", ""), lang)

    body = f"""<section class="page-head"><div class="wrap">
<h1>{E(L['name'])}</h1><p class="lead">{E(L.get('summary',''))} · {E(cat_label(c['category'], lang))}</p>
</div></section>
<section class="sec"><div class="wrap"><div class="cardetail">
<div class="gal">{main_img}{gal}</div>
<div>
<div class="pricebox"><span class="big">{E(c['price_1_6'])} ₾ <small>/ {E(SPECS['units']['day'][lang])}</small></span></div>
<div class="tbl-wrap"><table class="spec"><tbody>{"".join(rows)}</tbody></table></div>
<div class="tbl-wrap"><table class="spec"><caption>{E(u['ui']['price_table'])}</caption><tbody>{prices}</tbody></table></div>
<ul>{feats}</ul>
</div></div>
<div class="article">{body_html}</div>
<div class="cta"><h2>{E(u['ui']['book_title'])}</h2><p>{inline(u['ui']['book_text'], lang)}</p>
<div class="row"><a class="btn" href="{page_url(lang,'contact',False)}">{E(u['nav']['contact'])}</a>
<a class="btn ghost" href="{page_url(lang,'pricing',False)}">{E(u['nav']['pricing'])}</a>
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


def render_map_page(lang):
    p = PAGES["map"][lang]
    u = UI[lang]
    depth = 1 if lang == "ka" else 2
    mp, js = map_block(lang)
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
        f'<section class="sec"><div class="wrap">{mp}{legend_html(lang)}</div></section>'
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
        f'<div class="card"><span class="tag">{E(tl(lang,"type",a["type"]))}</span>'
        f'<h3><a href="{attr_url(lang, s, False)}">{E(a[lang]["name"])}</a></h3>'
        f'<p>{E(a[lang]["short"])}</p><ul>'
        f'<li>{E(tu(lang,"visit_time"))}: {E(a["visit_hours"])} {E(tu(lang,"hrs"))}</li>'
        f'<li>{E(tu(lang,"from_tbilisi"))}: {a["distance_tbilisi_km"]} {E(tu(lang,"km"))} · {E(a["drive_time_tbilisi"])}</li>'
        f'<li>{E(tu(lang,"car_needed"))}: {E(car_cat_label(a["car_category"], lang))}</li>'
        f"</ul></div>" for s, a in sub.items())
    best = "".join(f"<li>{inline(x, lang)}</li>" for x in L["best_for"])
    title = f'{L["name"]} — {tu(lang, "attractions")}, {tu(lang, "routes")} | {BRAND}'
    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:176]
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


def render_attraction(lang, slug, a):
    L = a[lang]
    u = UI[lang]
    r = REGIONS[a["region"]]
    depth = 2 if lang == "ka" else 3
    mp, js = map_block(lang, 360, (a["lat"], a["lon"]), 12,
                       attractions={slug: a}, routes={})
    near = "".join(
        f'<div class="card"><span class="tag">{E(tl(lang,"type",ATTRACTIONS[n]["type"]))}</span>'
        f'<h3><a href="{attr_url(lang, n, False)}">{E(ATTRACTIONS[n][lang]["name"])}</a></h3>'
        f'<p>{E(ATTRACTIONS[n][lang]["short"])}</p></div>'
        for n in a.get("nearby", []) if n in ATTRACTIONS)
    badge = (f'<span class="tag">{E(tu(lang,"unesco"))}</span>' if a["unesco"] else "")
    title = f'{L["name"]} — {tl(lang, "type", a["type"])}, {a["drive_time_tbilisi"]} {tu(lang,"from_tbilisi")}'
    title = title[:70] + f" | {BRAND}" if len(title) < 55 else title[:74]
    desc = re.sub(r"\s+", " ", f'{L["short"]} {tu(lang,"visit_time")}: {a["visit_hours"]} '
                               f'{tu(lang,"hrs")}. {tu(lang,"from_tbilisi")} '
                               f'{a["distance_tbilisi_km"]} {tu(lang,"km")}, '
                               f'{a["drive_time_tbilisi"]}. {L["body"]}')[:178]
    body = (
        f'<section class="page-head"><div class="wrap">{badge}<h1>{E(L["name"])}</h1>'
        f'<p class="lead">{E(L["short"])}</p></div></section>'
        f'<section class="sec"><div class="wrap">{attr_facts(a, lang)}'
        f'<div class="article">{render_md(L["body"], lang)}</div></div></section>'
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
                     depth, {"@context": "https://schema.org", "@graph": graph}, leaflet=True)
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
    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:176]
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


# ══════════════════════════════════════════════════════════════ sitemap etc.
def sitemap():
    urls = []

    def add(loc_fn, prio, langs=LANGS):
        for lang in langs:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{loc_fn(l)}"/>'
                for l in LANGS)
            alts += (f'\n    <xhtml:link rel="alternate" hreflang="x-default" '
                     f'href="{loc_fn("en")}"/>')
            urls.append(f"""  <url>
    <loc>{loc_fn(lang)}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{prio}</priority>{alts}
  </url>""")

    for page in PAGE_ORDER:
        add(lambda l, p=page: page_url(l, p),
            "1.0" if page == "index" else
            ("0.9" if page in ("fleet", "pricing", "software", "blog") else "0.7"))
    for slug in CARS:
        add(lambda l, s=slug: car_url(l, s), "0.8")
    for slug in POSTS:
        add(lambda l, s=slug: post_url(l, s), "0.6")
    for key in REGIONS:
        add(lambda l, k=key: region_url(l, k), "0.8")
    for slug in ATTRACTIONS:
        add(lambda l, s=slug: attr_url(l, s), "0.7")
    for slug in ROUTES:
        add(lambda l, s=slug: route_url(l, s), "0.8")
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
        out.append(f"- [{u['nav'][p]}]({page_url('en', p)}): {PAGES[p]['en']['desc']}")
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
        pg = PAGES[p]["en"]
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


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)

    write(os.path.join(out, "assets", "style.css"), build_css(DESIGN))

    for src, dst in (("static", os.path.join(out, "assets")),
                     ("admin", os.path.join(out, "admin"))):
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
    up = os.path.join("static", "uploads")
    if os.path.isdir(up):
        shutil.copytree(up, os.path.join(out, "uploads"), dirs_exist_ok=True)
    fav = os.path.join(out, "assets", "favicon.svg")
    if os.path.exists(fav):
        shutil.copy2(fav, os.path.join(out, "favicon.svg"))

    n = 0
    for lang in LANGS:
        for page in PAGE_ORDER:
            rel = page_url(lang, page, False).lstrip("/")
            if page == "blog":
                write(os.path.join(out, rel, "index.html"), render_blog_index(lang))
            elif page == "map":
                write(os.path.join(out, rel, "index.html"), render_map_page(lang))
            else:
                write(os.path.join(out, rel, "index.html"), render_static_page(lang, page))
            n += 1
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

    for name, data in [("sitemap.xml", sitemap()), ("robots.txt", robots()),
                       ("llms.txt", llms_txt()), ("llms-full.txt", llms_full_txt()),
                       ("404.html", render_404()), (".nojekyll", "")]:
        write(os.path.join(out, name), data)

    print(f"✔ {n} HTML გვერდი ({len(CARS)} ავტომობილი, {len(POSTS)} სტატია, {len(LANGS)} ენა) → ./{out}")


if __name__ == "__main__":
    main()
