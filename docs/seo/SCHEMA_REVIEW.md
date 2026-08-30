# RentUp.ge — Structured Data (JSON-LD) Review

Review date: 2026-08-29 · Scope: every `application/ld+json` block emitted by `build.py` into `dist/`
Method: read `build.py` helpers → parsed all 2 140 built HTML files → validated JSON, `@id` graph
resolution and every claim against the source YAML in `content/`.

**Nothing in this document was applied.** `build.py` and all content YAML are unchanged. Every
proposal below is a copy-pasteable patch for someone else to apply.

**Rule followed throughout:** no property is proposed unless a real value for it already exists in
`content/settings/site.yml`, `content/settings/rental_policy.yml`, `content/cars/*.yml`,
`content/attractions/*.yml`, `content/routes/*.yml`, `content/itineraries/*.yml`,
`content/settings/places.yml` or `content/pages/contact.yml`. Where a schema type needs a fact the
repo does not hold, the type is listed in [§9 Blocked](#9-blocked--needs-real-data-from-the-owner)
instead of being filled with a plausible guess.

---

## 1. How JSON-LD is produced

There is exactly **one** emission point:

| What | Where |
|---|---|
| The `<script type="application/ld+json">` tag | `build.py:797` inside `head_html()` |
| Serialiser | `J = json.dumps(o, ensure_ascii=False, indent=2)` — `build.py:56` |
| Node factories | `build.py:585–705` (the `# JSON-LD` section) |
| Per-page graph assembly | inline in each `render_*()`, as a `graph = [...]` list |

Every page passes a single object of the shape `{"@context": "https://schema.org", "@graph": [...]}`
as the `ld` argument of `head_html()`. There is no second script tag and no microdata/RDFa anywhere
in the output.

### Node factories (`build.py:585–705`)

| Function | Line | Emits |
|---|---|---|
| `org_node(lang)` | 586 | `["AutoRental","LocalBusiness"]` — `@id` `https://rentup.ge/#organization` |
| `website_node(lang)` | 622 | `WebSite` — `@id` `https://rentup.ge/#website` |
| `crumbs_node(lang, trail)` | 628 | `BreadcrumbList` (no `@id`) |
| `faq_node(blocks)` | 634 | `FAQPage` from page blocks of `type: faq` (no `@id`) |
| `software_node(lang)` | 643 | `SoftwareApplication` — `@id` `https://rentup.ge/#software` |
| `offer_catalog(lang)` | 656 | `OfferCatalog` of six category `Offer`s |
| `car_node(slug, c, lang)` | 667 | `Car` — `@id` `<car url>#vehicle` |
| `post_node(slug, p, lang)` | 693 | `BlogPosting` — `@id` `<post url>#post` |

Everything else (`WebPage`, `CollectionPage`, `ItemList`, `TouristAttraction`, `TouristDestination`,
`TouristTrip`, `Blog`, `WebApplication`, `Person`) is written as an inline dict literal inside the
`render_*()` function, which is why those nodes drifted apart in quality.

---

## 2. Current-state inventory — every block, per template

Counts are per language; the site ships 6 languages (`en` at `/`, `ka ru fa he ar` under `/{lang}/`).

| Template / URL | Producer | Nodes in `@graph` | Pages × 6 langs |
|---|---|---|---|
| Home `/` | `render_static_page` (1207–1233) | `AutoRental+LocalBusiness`, `WebSite`, `WebPage`, `BreadcrumbList`, `FAQPage`, `SoftwareApplication`, `ItemList` (257 attractions) | 6 |
| Static pages `/about/ /terms/ /faq/ /community/ /contact/` | `render_static_page` (1207) | org, `WebSite`, `WebPage`, `BreadcrumbList` (+`FAQPage` on `/faq/`) | 30 |
| `/fleet/` | `render_static_page` (1229–1233) | org, `WebSite`, `WebPage`, `BreadcrumbList`, `OfferCatalog`, `ItemList` (17 cars) | 6 |
| `/fleet-management-software/` | `render_static_page` (1220) | org, `WebSite`, `WebPage`, `BreadcrumbList`, `FAQPage`, `SoftwareApplication` | 6 |
| Car detail `/fleet/<slug>/` | `render_car` (1374) | org, `WebSite`, **`Car`**, `BreadcrumbList` | 17 × 6 = 102 |
| `/blog/` | `render_blog_index` (1431) | org, `WebSite`, `Blog` (with 4 embedded `BlogPosting`), `BreadcrumbList` | 6 |
| Post `/blog/<slug>/` | `render_post` (1464) | org, `WebSite`, **`BlogPosting`**, `BreadcrumbList` | 4 × 6 = 24 |
| `/map/` | `render_map_page` (1957) | org, `WebSite`, `CollectionPage` — **no `BreadcrumbList`** | 6 |
| Region `/regions/<key>/` | `render_region` (2070) | org, `WebSite`, **`TouristDestination`**, `BreadcrumbList` | 11 × 6 = 66 |
| Attraction `/attractions/<slug>/` | `render_attraction` (2192) | org, `WebSite`, **`TouristAttraction`**, `BreadcrumbList` | 257 × 6 = 1 542 |
| Route `/routes/<slug>/` | `render_route` (2277) | org, `WebSite`, **`TouristTrip`**, `BreadcrumbList` | 32 × 6 = 192 |
| `/car-rental/` | `render_car_rental_hub` (3466) | org, `WebSite`, `WebPage`, `ItemList`, `BreadcrumbList` | 6 |
| `/car-rental/<city>/` | `render_rental_location` (3536) | org, `WebSite`, `WebPage` (+ inline `about: Place`), `BreadcrumbList` | 6 × 6 = 36 |
| `/car-rental/<category>/` | `render_rental_category` (3590) | org, `WebSite`, `WebPage`, `ItemList`, `BreadcrumbList` | 4 × 6 = 24 |
| `/itineraries/` | `render_itineraries_hub` (3745) | org, `WebSite`, `CollectionPage`, `ItemList`, `BreadcrumbList` | 6 |
| Itinerary `/itineraries/<slug>/` | `render_itinerary` (3700) | org, `WebSite`, **`TouristTrip`**, `BreadcrumbList` | 5 × 6 = 30 |
| `/trip-planner/` | `render_planner_landing` (3793) | org, `WebSite`, `WebApplication`, `BreadcrumbList` | 6 |
| `/tours/` | `render_tours_page` (3844) | org, `WebSite` **only** | 6 |
| `/trip/` (noindex) | `render_trip_page` (3930) | org, `WebSite` only | 6 |
| `/business-card/` (noindex) | `render_business_card` (1268) | **`Person`** only — no org, no `WebSite`, no breadcrumb | 6 |
| `/planner/` `/pricing/` | redirect stubs | none — correct, they are `noindex` meta-refresh files | 12 |
| `/app/` | `render_app_page` | none — `noindex` | 6 |
| `404.html`, `/admin/*` | — | none — correct | 4 |
| **`render_planner`** (2821) `WebApplication` | dead route | never written to `dist/` | 0 |

Also note **`build.py:1986–2027` is unreachable code** — `_render_map_page_legacy_redirect()`
`return`s at line 1983, so the richer `/map/` graph below it (with `ItemList` of 257 attractions and
a `BreadcrumbList`) never runs. The live `/map/` page gets the thin graph from
`render_map_page()` at line 1957.

### Aggregate node census across the built site

```
2118  ld+json blocks in 2140 HTML files   (22 without: 4 admin/404, 18 noindex stubs)
   0  JSON parse errors
   0  unresolved @id references inside any page graph

2112  AutoRental+LocalBusiness      102  Car                 12  SoftwareApplication
2112  WebSite                        66  TouristDestination  12  CollectionPage
2094  BreadcrumbList                 48  ItemList             6  Blog
1542  TouristAttraction              24  BlogPosting          6  Person
 222  TouristTrip                    18  FAQPage              6  WebApplication
 120  WebPage                                                 6  OfferCatalog
```

**Validation verdict: every block parses, and every `{"@id": …}` reference resolves to a node defined
in the same page graph.** The two `@id` targets used as references — `#organization` and `#website` —
are both present in every graph that references them. There are no dangling pointers and no
duplicate-`@id`-with-different-content collisions *within* a page.

---

## 3. Defects in what is emitted today

Severity: **P0** = wrong or unsupportable claim / policy risk · **P1** = wrong modelling that costs
comprehension · **P2** = hygiene.

### P0

| # | Finding | Evidence |
|---|---|---|
| P0-1 | **`Organization.description` claims "full insurance coverage"** — `content/settings/rental_policy.yml` says the opposite in a comment written for this exact reason: `insurance.included: tpl`, `cdw_available: true` at 25 GEL/day, `excess_gel: 1000`, and `# Deliberately NOT claimed: "full coverage", "zero excess".` The claim is on all 2 112 pages, in all 6 languages. | `meta.yml` `org_desc` (all langs) → `build.py:594` |
| P0-2 | **`Offer.availability: "https://schema.org/InStock"` on all 17 cars and all 6 category offers.** No car YAML has an `available:` key (`grep` → 0 hits), so `c.get("available", True)` hard-codes in-stock for every vehicle on every day. There is no inventory system behind it. | `build.py:679`, `build.py:664` |
| P0-3 | **`SoftwareApplication.operatingSystem: "Android 7.0+, iOS 13+"` while the site's own header renders `iPhone / iOS — Coming soon`.** Markup asserting a product that does not exist. | `build.py:648`; `dist/index.html` app menu |
| P0-4 | **`publicAccess: true` hard-coded on all 257 `TouristAttraction` nodes**, regardless of `open_year_round` (which is `false` for e.g. Abano Pass, a June–October 4×4-only track). | `build.py:2202` |
| P0-5 | **`datePublished: "2026-01-15"` hard-coded on every static-page `WebPage` node**, in every language — a fabricated publication date. `dateModified: TODAY` re-dates every page on every build even when nothing changed. | `build.py:1212` |
| P0-6 | **`content/settings/meta.yml` → `llms_facts` (rendered into `dist/llms.txt`) contradicts `rental_policy.yml` and `contact.yml` on five material points.** Not JSON-LD, but it is the machine-readable fact sheet AI answer engines read, and it is the source anyone would reach for when filling schema. See table below. | `build.py:2958`; `dist/llms.txt` |

**P0-6 detail — five direct contradictions:**

| Claim in `llms.txt` / `meta.yml` | `rental_policy.yml` / `contact.yml` says |
|---|---|
| "Minimum driver age: 21 for economy, 23 for SUV/minivan, 25 for business class and 4x4" | `min_driver_age: 21` (flat) |
| "Mileage: Unlimited within Georgia; 300 km/day limit on cross-border trips" | `cross_border.allowed: false` — there are no cross-border trips |
| "Fuel policy: Full to full" | `fuel_policy: same_to_same` |
| "Insurance: CDW and TPL included; SCDW zero-excess option for 25–45 GEL/day" | `insurance.included: tpl`, CDW is a 25 GEL/day add-on, `excess_gel: 1000`, zero-excess explicitly not offered |
| "Cross-border: Armenia (150 GEL) and Turkey (250 GEL) allowed with permit" | `cross_border.allowed: false` |
| "Booking requests are submitted online and require payment before confirmation" | `contact.yml` (all 6 langs): "the site has no online form or payment system"; `rental_policy.yml`: `prepayment_required: false`; `booking.yml`: `enabled: true, payment_required: true` |

Three files give three different answers to "can you book and pay online?". That has to be resolved
before any `Offer`, `potentialAction` or booking-related markup is written.

### P1

| # | Finding | Evidence |
|---|---|---|
| P1-1 | **No `WebPage` node on the highest-value templates.** Car, attraction, region, route, itinerary and post pages emit the entity but no page node — so nothing declares `mainEntity`, `primaryImageOfPage`, `breadcrumb`, `isPartOf` or (on most of them) `inLanguage`. The entity floats unattached to the URL it describes. | 1 908 of 2 118 pages |
| P1-2 | **`touristType` is misused as a *kind-of-place* / *difficulty* field.** `touristType` describes the *visitor* ("families", "hikers"). The site emits `"touristType": "Monastery"` on attractions and `"touristType": "Hard"` on routes. | `build.py:2201`, `build.py:2280` |
| P1-3 | **`fuelConsumption.unitCode: "LTR"` is wrong.** `LTR` is *litre*, not litres-per-100 km. schema.org's own note: there is no UN/CEFACT code for L/100 km — use `unitText`. `"name": "l/100km"` is also not a `QuantitativeValue` property that consumers read. | `build.py:675` |
| P1-4 | **`driveWheelConfiguration` emits bare `"FWD"/"RWD"/"AWD"/"4WD"`** instead of the `DriveWheelConfigurationValue` enumeration URLs. | `build.py:673` |
| P1-5 | **Tiered pricing is not marked up.** `price_7_29` and `price_30` are printed in a visible price table on every car page (`build.py:1343`) but only `price_1_6` reaches the `Offer`. `deposit` is printed too and never marked up. | `build.py:678–686` |
| P1-6 | **`OfferCatalog` "from" prices are presented as exact prices** with `availability: InStock`. The six values (75/130/210/240/200/185 GEL) are verified correct as *cheapest in category*, so the honest type is `AggregateOffer` with `lowPrice`, not `Offer` with `price`. | `build.py:656–664` |
| P1-7 | **`Offer` uses no `businessFunction`.** Without `http://purl.org/goodrelations/v1#LeaseOut` a consumer reads 88 GEL as the price to *buy* a Toyota Corolla. | `build.py:678` |
| P1-8 | **`TouristTrip.provider: RentUp`** on all 32 routes and 5 itineraries. Routes are editorial driving guides with no price and no booking; `provider` asserts RentUp sells them as trips. (`provider` is also not a valid way to express authorship — `TouristTrip` is an `Intangible`, so `author` cannot be used on it either; the authorship belongs on the page node.) | `build.py:2281`, `build.py:3703` |
| P1-9 | **719 licensed gallery images + 250 licensed hero images carry full `author` / `license` / `license_url` / `source` metadata and none of it reaches JSON-LD.** Image licensing is one of the few genuinely rich-result-eligible features this site qualifies for outright. | `content/attractions/*.yml`; `build.py:1533–1580` |
| P1-10 | **`/map/` emits no `BreadcrumbList`** although the page renders visible breadcrumbs, and its `CollectionPage` has no `inLanguage`/`isPartOf`. **`/tours/` emits only org + WebSite** — no page node, no breadcrumb, no `ItemList`. | `build.py:1957`, `build.py:3844` |
| P1-11 | **`WebSite` uses one language-neutral `@id` (`/#website`) but a per-language `url` and `inLanguage`.** Six different node contents share one identifier. See [§7](#7-multilingual-correctness). | `build.py:622–625` |
| P1-12 | **`Organization.logo` is absent.** The only logo asset (`/assets/rentup-header-logo.png`) is 180 × 72 px and fails Google's ≥ 112 px-per-side logo requirement; `/assets/app-icon-512.png` (512 × 512) does not. | `design.yml`; `dist/assets/` |

### P2

| # | Finding |
|---|---|
| P2-1 | `BreadcrumbList` has no `@id`, so no `WebPage` can point `breadcrumb` at it. |
| P2-2 | Homepage `BreadcrumbList` has a single item ("Home") — inert. |
| P2-3 | `isAccessibleForFree: false` is asserted for `entry_fee: "check locally"` and `entry_fee: "ticket"`. Unknown ≠ false; omitting the property is the correct signal. The free-entry test also string-matches only `ka/en/ru` (`"free", "უფასო", "Бесплатно"`) so the `fa/he/ar` builds fall through to whatever the shared `entry_fee` string is — in practice fine, because `entry_fee` is language-neutral, but the list is fragile. |
| P2-4 | `geo.latitude` / `longitude` on the Organization are strings (`"41.7245"`); attractions correctly emit numbers. |
| P2-5 | `priceRange: "$$"` is a guess. Real day rates run 75–310 GEL and are on the site. |
| P2-6 | `Blog.blogPost` inlines all four full `BlogPosting` nodes on `/blog/`; a list of `{"@id": …}` references would be equivalent and much smaller. |
| P2-7 | `attraction` / `region` cross-references (`includesAttraction`, `containedInPlace`) create stub nodes with `name`+`url` but no `@id`, so the same real-world place gets a fresh anonymous node on every page that mentions it. |
| P2-8 | `J(ld)` does not escape `</`. A `</script>` sequence anywhere in a YAML description would close the tag early. Currently harmless, one line to make safe. |
| P2-9 | `render_business_card` emits a lone `Person` with no `@context`-level org/website nodes. Page is `noindex`, so this is cosmetic. |
| P2-10 | Only 4 of 6 car categories have `/car-rental/<category>/` pages (business and van fail `rental_quality_ok`), but `head_html` writes hreflang alternates for all 6 languages unconditionally on the pages that do exist. Not a schema defect; flagged because the `ItemList` on `/car-rental/` correctly lists only the 4 that exist. |

---

## 4. Gap table — what exists, what is missing, what is rich-result eligible in 2026

"Rich result" = Google shows a distinct SERP feature. "Understanding" = no SERP feature, but the
markup feeds entity understanding, Google's travel/local surfaces and AI answer engines.

| Type | Where it belongs | Status today | 2026 Google eligibility | Priority |
|---|---|---|---|---|
| `Organization` / `AutoRental` | every page | present, needs fixes (P0-1, P1-12) | **Rich** — knowledge panel / business info | P0 |
| `BreadcrumbList` | every page | present except `/map/`, `/tours/` | **Rich** — breadcrumb trail | P1 |
| `WebPage` + `mainEntity` | every page | missing on 1 908 pages | Understanding (the spine everything hangs off) | P1 |
| `WebSite` | every page | present, `@id` broken across languages | Understanding | P1 |
| `WebSite` + `SearchAction` | — | absent | **Retired.** Google removed the sitelinks-searchbox rich result in Nov 2024, and rentup.ge has no search endpoint to point at. **Do not add.** | — |
| `Car` (⊂ `Vehicle` ⊂ `Product`) | `/fleet/<slug>/` | present, thin | Understanding. Google's *vehicle listing* rich result is for cars **for sale** (needs VIN, mileage, condition) — a rental is out of scope. Merchant listings need a purchasable item. | P1 |
| `Offer` with `LeaseOut` + tiers | `/fleet/<slug>/` | single tier, no business function | Understanding + price comprehension | P1 |
| `RentalCarReservation` | — | absent | **Not applicable to public pages.** It is a *transaction* type for confirmation emails and Actions, not a listing. The public-page equivalent is `Car` + `Offer(businessFunction=LeaseOut)`, plus a `ReserveAction` **only if** a bookable URL exists — it does not (§9). | — |
| `AggregateOffer` | `/fleet/`, `/car-rental/<cat>/` | `OfferCatalog` misuses `Offer` | Understanding | P1 |
| `Product` | category pages | absent — and unnecessary: `Car` already inherits from `Product`, so co-typing adds nothing on car pages; category pages want `ItemList` + `AggregateOffer` | Understanding | P2 |
| `ImageObject` with licence | 969 attraction photos | absent | **Rich** — Licensable badge in Google Images. Requires `license` + `acquireLicensePage`; **both are already in the YAML.** | P1 |
| `TouristAttraction` (+ subtype) | 257 pages | present, `touristType` misused, `publicAccess` fabricated | Understanding | P1 |
| `Place` / `TouristDestination` | regions, itinerary stops | regions yes; itinerary stops no | Understanding | P2 |
| `TouristTrip` + `itinerary` `ItemList` | routes, itineraries | present but flat and `provider`-tainted | Understanding | P1 |
| `TouristTrip.subTrip` per day | `/itineraries/<slug>/` | absent — the day-by-day plan (`plan[].day/from/to/km/drive/stops/overnight/road`) is fully structured in YAML and rendered on the page | Understanding | P2 |
| `FAQPage` | `/faq/`, home, software | present (18 nodes) | **Understanding only.** Google restricted FAQ rich results to authoritative government and health sites in Aug 2023. Keep it for comprehension, expect no SERP change. | P2 |
| `FAQPage` on `/car-rental/*` | hub + 4 categories | **missing** although genuine visible Q&A renders there via `_faq_html()` | Understanding | P2 |
| `Service` for airport delivery | `/car-rental/<airport>/` | absent — real fees exist (`rental_policy.delivery.airport_fee_gel`: TBS 30, KUT 60, BUS 60 GEL) | Understanding | P2 |
| `speakable` | — | absent | **Do not add.** Never left limited availability: US news publishers, Google Assistant only. | — |
| `HowTo` | — | absent | **Retired** by Google in 2023. Do not add. | — |
| `SoftwareApplication` | home, `/fleet-management-software/` | present, one false claim (P0-3) | Understanding — the software-app rich result was retired | P0 (fix claim) |
| `Article` / `BlogPosting` | 4 posts | present and correct | **Rich** — article result | ok |
| `aggregateRating` / `review` | — | **absent — correctly** | Rich, but **blocked**; see §8 and §9 | — |

---

## 5. Proposed patches

All snippets follow the existing house style: module-level factories in the
`# ═══ JSON-LD` block (`build.py:585`), dict literals, `SITE_URL`/`lang_root()`/`E()`/`J()` helpers,
English comments explaining *why a value is safe to assert*.

> **Placement note.** `TRAVEL`, `PLACES`/`PLACE_BY_KEY` and `RENTAL_POLICY` are assigned at
> `build.py:1481`, `3238` and `84`. Python resolves module globals at *call* time, so new factories
> may live in the JSON-LD block at line ~700 even though they read those names — the `render_*()`
> callers all run from `main()`, long after module init.

---

### Patch 1 — `@id` helpers + a real `WebPage` node (P1-1, P1-11, P2-1)

Add after `website_node()` (`build.py:625`):

```python
def website_id(lang):
    """One WebSite entity per language. The six language homes have different
    URLs and different inLanguage values, so they cannot share one @id."""
    return SITE_URL + lang_root(lang) + "#website"


def website_node(lang):
    return {"@type": "WebSite", "@id": website_id(lang),
            "url": SITE_URL + lang_root(lang), "name": BRAND,
            "inLanguage": lang, "publisher": {"@id": SITE_URL + "/#organization"}}


def crumbs_node(lang, trail, url=None):
    """`url` gives the list an @id so a WebPage can point `breadcrumb` at it.
    Existing three-argument-less callers keep working unchanged."""
    node = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
        for i, (n, u) in enumerate(trail)]}
    if url:
        node["@id"] = url + "#breadcrumb"
    return node


def page_node(lang, url, name, desc, types=("WebPage",), main_entity=None,
              image=None, breadcrumb=True, published=None, modified=None,
              parts=()):
    """The page node every template was missing. Optional keys are emitted only
    when a real value exists — no placeholder date, no placeholder image."""
    node = {"@type": list(types) if len(types) > 1 else types[0],
            "@id": url + "#webpage", "url": url, "name": name,
            "description": desc, "inLanguage": lang,
            "isPartOf": {"@id": website_id(lang)},
            "publisher": {"@id": SITE_URL + "/#organization"}}
    if main_entity:
        node["mainEntity"] = {"@id": main_entity}
    if breadcrumb:
        node["breadcrumb"] = {"@id": url + "#breadcrumb"}
    if image:
        node["primaryImageOfPage"] = {"@id": image}
    if published:
        node["datePublished"] = published
    if modified:
        node["dateModified"] = modified
    if parts:
        node["hasPart"] = [{"@id": p} for p in parts]
    return node
```

Then in `render_car()` (`build.py:1374`) the graph becomes:

```python
    _url = car_url(lang, slug)
    graph = [org_node(lang), website_node(lang),
             page_node(lang, _url, title, desc,
                       main_entity=_url + "#vehicle"),
             car_node(slug, c, lang),
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["fleet"], page_url(lang, "fleet")),
                                (L["name"], _url)], _url)]
```

The identical two-line change applies to `render_attraction` (2192), `render_region` (2070),
`render_route` (2277), `render_itinerary` (3700) and `render_post` (1464). In
`render_static_page` (1207–1216) and the `/car-rental/*` renderers, replace the hand-written
`{"@type": "WebPage", ...}` literal with `page_node(...)` and pass the page URL to `crumbs_node`.

Also update the two remaining hard-coded `WebSite` references:
`build.py:1210` and `build.py:2014` — `{"@id": SITE_URL + "/#website"}` → `{"@id": website_id(lang)}`.

**Produces (car page, `en`):**

```json
{
  "@type": "WebPage",
  "@id": "https://rentup.ge/fleet/toyota-corolla/#webpage",
  "url": "https://rentup.ge/fleet/toyota-corolla/",
  "name": "Toyota Corolla — rent 88 ₾/day | RentUp",
  "description": "Toyota Corolla, 2020–2023, 1.6 petrol. …",
  "inLanguage": "en",
  "isPartOf": { "@id": "https://rentup.ge/#website" },
  "publisher": { "@id": "https://rentup.ge/#organization" },
  "mainEntity": { "@id": "https://rentup.ge/fleet/toyota-corolla/#vehicle" },
  "breadcrumb": { "@id": "https://rentup.ge/fleet/toyota-corolla/#breadcrumb" }
}
```

---

### Patch 2 — `org_node`: real logo, real price band, real contact points (P0-1, P1-12, P2-4, P2-5)

Replace `org_node()` (`build.py:586–619`):

```python
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]


def price_band():
    """Real daily-rate band from content/cars/*.yml — replaces the "$$" guess."""
    rates = [int(c["price_1_6"]) for c in CARS.values()]
    return f"{min(rates)}-{max(rates)} GEL"


def contact_points(lang):
    """Only channels that genuinely exist. One phone number serves both the
    reservations line and WhatsApp (site.yml: phone_e164 == whatsapp)."""
    langs = [l.upper() for l in ((RENTAL_POLICY.get("support") or {})
                                 .get("languages") or ["ka", "en", "ru"])]
    cps = [{"@type": "ContactPoint", "@id": SITE_URL + "/#contact-reservations",
            "contactType": "reservations", "telephone": SITE["phone_e164"],
            "availableLanguage": langs, "areaServed": "GE",
            "hoursAvailable": {"@type": "OpeningHoursSpecification",
                               "dayOfWeek": DAYS_OF_WEEK,
                               "opens": SITE["opens"], "closes": SITE["closes"]}}]
    if SITE.get("whatsapp"):
        cps.append({"@type": "ContactPoint", "@id": SITE_URL + "/#contact-whatsapp",
                    "contactType": "customer support",
                    "telephone": SITE["phone_e164"], "areaServed": "GE",
                    "url": f"https://wa.me/{SITE['whatsapp']}"})
    return cps


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
        # Real band from the fleet, not a "$$" guess.
        "priceRange": price_band(),
        "currenciesAccepted": "GEL, USD, EUR",
        "paymentAccepted": META[lang]["payments"],
        "areaServed": {"@type": "Country", "name": META[lang]["country"]},
        "address": {"@type": "PostalAddress", "streetAddress": a["street"],
                    "addressLocality": a["city"], "postalCode": SITE["address_zip"],
                    "addressCountry": "GE"},
        # Numbers, not strings — attraction nodes already do this correctly.
        "geo": {"@type": "GeoCoordinates", "latitude": float(SITE["geo_lat"]),
                "longitude": float(SITE["geo_lon"])},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification", "dayOfWeek": DAYS_OF_WEEK,
            "opens": SITE["opens"], "closes": SITE["closes"]}],
        # 512x512 app icon: the header logo is 180x72 and fails Google's
        # 112px minimum on the short side.
        "logo": {"@type": "ImageObject", "@id": SITE_URL + "/#logo",
                 "url": SITE_URL + "/assets/app-icon-512.png",
                 "contentUrl": SITE_URL + "/assets/app-icon-512.png",
                 "width": 512, "height": 512, "caption": BRAND},
        "image": {"@id": SITE_URL + "/#logo"},
        "contactPoint": contact_points(lang),
        "knowsLanguage": LANGS,
    }
    # Optional contact details: emit each key only when it holds a real value,
    # so an empty admin field never becomes an empty mailto: or a bare sameAs.
    if SITE.get("email"):
        node["email"] = SITE["email"]
    if SITE.get("social"):
        node["sameAs"] = SITE["social"]
    return node
```

**Content fix that must ship with it (not a `build.py` change).** `content/settings/meta.yml`,
key `org_desc`, in all six languages: replace *"full insurance coverage"* with the policy the
repo actually holds, e.g. *"third-party liability included, optional CDW from 25 GEL/day"*. Until
that edit lands, Patch 2 propagates P0-1 into a more prominent node.

**Produces (`en`, abridged):**

```json
{
  "@type": ["AutoRental", "LocalBusiness"],
  "@id": "https://rentup.ge/#organization",
  "name": "RentUp",
  "priceRange": "75-310 GEL",
  "geo": { "@type": "GeoCoordinates", "latitude": 41.7245, "longitude": 44.7509 },
  "logo": {
    "@type": "ImageObject", "@id": "https://rentup.ge/#logo",
    "url": "https://rentup.ge/assets/app-icon-512.png",
    "contentUrl": "https://rentup.ge/assets/app-icon-512.png",
    "width": 512, "height": 512, "caption": "RentUp"
  },
  "image": { "@id": "https://rentup.ge/#logo" },
  "contactPoint": [
    {
      "@type": "ContactPoint", "@id": "https://rentup.ge/#contact-reservations",
      "contactType": "reservations", "telephone": "+995597555565",
      "availableLanguage": ["KA", "EN", "RU"], "areaServed": "GE",
      "hoursAvailable": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "opens": "09:00", "closes": "21:00"
      }
    },
    {
      "@type": "ContactPoint", "@id": "https://rentup.ge/#contact-whatsapp",
      "contactType": "customer support", "telephone": "+995597555565",
      "areaServed": "GE", "url": "https://wa.me/995597555565"
    }
  ],
  "knowsLanguage": ["en", "ka", "ru", "fa", "he", "ar"]
}
```

Deliberately **not** emitted: `hasPOS`/branch nodes for the airport pickup points (arrivals-hall
meeting points are a delivery service, not premises); a second 24/7 `ContactPoint` (the contact page
prints a 24/7 hotline as free text — see §9 item 3); `aggregateRating`.

---

### Patch 3 — `car_node`: correct units, tiers, lease semantics, deposit (P0-2, P1-3…P1-7)

Replace `car_node()` (`build.py:667–690`) and add the constants above it:

```python
# GoodRelations: a rental is a lease-out, not a sale. Without this a consumer
# reads "88 GEL" as the price to buy the car.
LEASE_OUT = "http://purl.org/goodrelations/v1#LeaseOut"

DRIVE_WHEEL_URI = {
    "fwd": "https://schema.org/FrontWheelDriveConfiguration",
    "rwd": "https://schema.org/RearWheelDriveConfiguration",
    "awd": "https://schema.org/AllWheelDriveConfiguration",
    "4wd": "https://schema.org/FourWheelDriveConfiguration",
}
FUEL_TYPE_EN = {"petrol": "Petrol", "diesel": "Diesel", "hybrid": "Hybrid"}
# (lo, hi) rental length in days for each published tier; hi=None means open-ended.
PRICE_TIERS = [("price_1_6", 1, 6), ("price_7_29", 7, 29), ("price_30", 30, None)]


def car_price_specs(c, lang):
    """One UnitPriceSpecification per published tier. Every tier here is also
    printed in the visible price table on the same page (build.py:1343)."""
    out = []
    for key, lo, hi in PRICE_TIERS:
        if not c.get(key):
            continue
        qty = {"@type": "QuantitativeValue", "minValue": lo, "unitCode": "DAY"}
        if hi:
            qty["maxValue"] = hi
        out.append({"@type": "UnitPriceSpecification", "name": spec_label(key, lang),
                    "price": c[key], "priceCurrency": "GEL", "unitCode": "DAY",
                    "referenceQuantity": {"@type": "QuantitativeValue", "value": 1,
                                          "unitCode": "DAY"},
                    "eligibleQuantity": qty})
    return out


def car_offer(slug, c, lang):
    """No `availability`: there is no inventory system, so in-stock cannot be
    asserted. No `priceValidUntil`: no expiry date exists in the data."""
    pol = RENTAL_POLICY or {}
    node = {"@type": "Offer", "@id": car_url(lang, slug) + "#offer",
            "url": car_url(lang, slug), "businessFunction": LEASE_OUT,
            "price": c["price_1_6"], "priceCurrency": "GEL",
            "priceSpecification": car_price_specs(c, lang),
            "areaServed": {"@type": "Country", "name": META[lang]["country"]},
            "availableAtOrFrom": {"@id": SITE_URL + "/#organization"},
            "seller": {"@id": SITE_URL + "/#organization"}}
    if pol.get("min_rental_days") and pol.get("max_rental_days"):
        node["eligibleDuration"] = {"@type": "QuantitativeValue",
                                    "minValue": pol["min_rental_days"],
                                    "maxValue": pol["max_rental_days"],
                                    "unitCode": "DAY"}
    return node


def car_node(slug, c, lang):
    L = c[lang]
    brand, _, model = L["name"].partition(" ")
    fuel = str(c.get("engine", "")).split()[-1] if c.get("engine") else ""
    node = {
        # Car already inherits from Vehicle -> Product; no co-typing needed.
        "@type": "Car", "@id": car_url(lang, slug) + "#vehicle",
        "name": L["name"], "description": L.get("summary", ""),
        "url": car_url(lang, slug), "inLanguage": lang,
        "brand": {"@type": "Brand", "name": brand},
        "model": model or L["name"],
        "vehicleTransmission": spec_value(c["transmission"], lang),
        "vehicleSeatingCapacity": {"@type": "QuantitativeValue",
                                   "value": int(c["seats"])},
        "vehicleConfiguration": cat_label(c["category"], lang),
        # schema.org has no unit code for L/100 km — its own note says use unitText.
        "fuelConsumption": {"@type": "QuantitativeValue",
                            "value": float(c["fuel_100km"]),
                            "unitText": "L/100 km"},
        "offers": car_offer(slug, c, lang),
        "mainEntityOfPage": {"@id": car_url(lang, slug) + "#webpage"},
    }
    drive = DRIVE_WHEEL_URI.get(str(c.get("drive", "")).lower())
    if drive:
        node["driveWheelConfiguration"] = drive
    if fuel in FUEL_TYPE_EN:
        node["fuelType"] = FUEL_TYPE_EN[fuel]
    # Facts printed on the page that schema.org has no dedicated property for.
    props = []
    if c.get("years"):
        props.append({"@type": "PropertyValue", "name": spec_label("years", lang),
                      "value": str(c["years"])})
    if c.get("deposit"):
        props.append({"@type": "PropertyValue", "name": spec_label("deposit", lang),
                      "value": int(c["deposit"]), "unitText": "GEL"})
    if c.get("clearance"):
        props.append({"@type": "PropertyValue", "name": spec_label("clearance", lang),
                      "value": int(c["clearance"]), "unitCode": "MMT"})
    if c.get("luggage"):
        props.append({"@type": "PropertyValue", "name": spec_label("luggage", lang),
                      "value": int(c["luggage"])})
    if props:
        node["additionalProperty"] = props
    if c.get("image"):
        node["image"] = SITE_URL + c["image"] if c["image"].startswith("/") else c["image"]
    return node
```

**Produces (`/fleet/toyota-corolla/`, `en`):**

```json
{
  "@type": "Car",
  "@id": "https://rentup.ge/fleet/toyota-corolla/#vehicle",
  "name": "Toyota Corolla",
  "description": "2020–2023 · 1.6 petrol · automatic",
  "url": "https://rentup.ge/fleet/toyota-corolla/",
  "inLanguage": "en",
  "brand": { "@type": "Brand", "name": "Toyota" },
  "model": "Corolla",
  "vehicleTransmission": "Automatic",
  "vehicleSeatingCapacity": { "@type": "QuantitativeValue", "value": 5 },
  "vehicleConfiguration": "Economy class",
  "fuelConsumption": { "@type": "QuantitativeValue", "value": 6.0, "unitText": "L/100 km" },
  "driveWheelConfiguration": "https://schema.org/FrontWheelDriveConfiguration",
  "fuelType": "Petrol",
  "mainEntityOfPage": { "@id": "https://rentup.ge/fleet/toyota-corolla/#webpage" },
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "Year", "value": "2020–2023" },
    { "@type": "PropertyValue", "name": "Deposit", "value": 300, "unitText": "GEL" },
    { "@type": "PropertyValue", "name": "Ground clearance", "value": 135, "unitCode": "MMT" },
    { "@type": "PropertyValue", "name": "Luggage", "value": 2 }
  ],
  "offers": {
    "@type": "Offer",
    "@id": "https://rentup.ge/fleet/toyota-corolla/#offer",
    "url": "https://rentup.ge/fleet/toyota-corolla/",
    "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut",
    "price": "88",
    "priceCurrency": "GEL",
    "priceSpecification": [
      { "@type": "UnitPriceSpecification", "name": "1–6 days", "price": "88",
        "priceCurrency": "GEL", "unitCode": "DAY",
        "referenceQuantity": { "@type": "QuantitativeValue", "value": 1, "unitCode": "DAY" },
        "eligibleQuantity": { "@type": "QuantitativeValue", "minValue": 1, "maxValue": 6, "unitCode": "DAY" } },
      { "@type": "UnitPriceSpecification", "name": "7–29 days", "price": "79",
        "priceCurrency": "GEL", "unitCode": "DAY",
        "referenceQuantity": { "@type": "QuantitativeValue", "value": 1, "unitCode": "DAY" },
        "eligibleQuantity": { "@type": "QuantitativeValue", "minValue": 7, "maxValue": 29, "unitCode": "DAY" } },
      { "@type": "UnitPriceSpecification", "name": "30+ days", "price": "66",
        "priceCurrency": "GEL", "unitCode": "DAY",
        "referenceQuantity": { "@type": "QuantitativeValue", "value": 1, "unitCode": "DAY" },
        "eligibleQuantity": { "@type": "QuantitativeValue", "minValue": 30, "unitCode": "DAY" } }
    ],
    "eligibleDuration": { "@type": "QuantitativeValue", "minValue": 1, "maxValue": 90, "unitCode": "DAY" },
    "areaServed": { "@type": "Country", "name": "Georgia" },
    "availableAtOrFrom": { "@id": "https://rentup.ge/#organization" },
    "seller": { "@id": "https://rentup.ge/#organization" }
  }
}
```

*(Tier prices shown are the real `toyota-corolla.yml` values; verify against the file when applying.)*

---

### Patch 4 — category and fleet pages: `AggregateOffer`, not fake exact `Offer`s (P1-6)

Replace `offer_catalog()` (`build.py:656–664`) and add a reusable factory:

```python
def category_aggregate_offer(lang, key, url, slugs=None):
    """A category page promises a *from* price, so the honest type is
    AggregateOffer with lowPrice — not an Offer with an exact price and a
    fabricated InStock availability."""
    slugs = [s for s in (slugs or [s for s, c in CARS.items()
                                   if c["category"] == key]) if s in CARS]
    rates = [int(CARS[s]["price_1_6"]) for s in slugs]
    if not rates:
        return None
    return {"@type": "AggregateOffer", "@id": url + "#offers",
            "name": cat_label(key, lang), "priceCurrency": "GEL",
            "lowPrice": min(rates), "highPrice": max(rates),
            "offerCount": len(rates), "businessFunction": LEASE_OUT,
            "offers": [{"@id": car_url(lang, s) + "#offer"} for s in slugs],
            "seller": {"@id": SITE_URL + "/#organization"}}


def offer_catalog(lang):
    """Six category entries on /fleet/. Prices come from the cheapest car in
    each category (verified: they match META[lang]['offers'] exactly), so they
    are derived from content/cars/*.yml rather than restated in meta.yml."""
    url = page_url(lang, "fleet")
    items = []
    for c in CATS:
        agg = category_aggregate_offer(lang, c["key"], url + "#" + c["key"])
        if not agg:
            continue
        items.append({"@type": "Offer", "businessFunction": LEASE_OUT,
                      "itemOffered": {"@type": "Service",
                                      "serviceType": cat_label(c["key"], lang),
                                      "provider": {"@id": SITE_URL + "/#organization"}},
                      "priceSpecification": {
                          "@type": "UnitPriceSpecification",
                          "price": agg["lowPrice"], "priceCurrency": "GEL",
                          "unitCode": "DAY", "minPrice": agg["lowPrice"],
                          "referenceQuantity": {"@type": "QuantitativeValue",
                                                "value": 1, "unitCode": "DAY"}}})
    return {"@type": "OfferCatalog", "@id": url + "#catalog",
            "name": PAGES["fleet"][lang]["title"], "itemListElement": items}
```

In `render_rental_category()` (`build.py:3590`) append the aggregate to the graph:

```python
    _agg = category_aggregate_offer(lang, key, url, d.get("car_slugs"))
    if _agg:
        graph.append(_agg)
```

**Produces (`/car-rental/economy/`, `en`):**

```json
{
  "@type": "AggregateOffer",
  "@id": "https://rentup.ge/car-rental/economy/#offers",
  "name": "Economy class",
  "priceCurrency": "GEL",
  "lowPrice": 75,
  "highPrice": 88,
  "offerCount": 3,
  "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut",
  "offers": [
    { "@id": "https://rentup.ge/fleet/toyota-prius/#offer" },
    { "@id": "https://rentup.ge/fleet/hyundai-elantra/#offer" },
    { "@id": "https://rentup.ge/fleet/toyota-corolla/#offer" }
  ],
  "seller": { "@id": "https://rentup.ge/#organization" }
}
```

---

### Patch 5 — Licensable `ImageObject` for 969 attraction photos (P1-9) — the highest-ROI patch

969 images (250 hero + 719 gallery) already carry `author`, `license`, `license_url` and `source`,
and the credits are already rendered visibly under each photo (`build.py:1533–1580`). Google's image
licensing feature needs exactly `license` + `acquireLicensePage`. Add after `post_node()`:

```python
def image_object(path, credit, caption=None):
    """Licensable image node. Emitted only when the YAML carries a real licence
    — Google's image-licence feature requires both `license` and
    `acquireLicensePage`, and Wikimedia Commons photos give us both. The same
    author/licence line is already printed under the photo by photo_html()."""
    if not path:
        return None
    url = SITE_URL + path if path.startswith("/") else path
    node = {"@type": "ImageObject", "@id": url + "#image",
            "url": url, "contentUrl": url}
    if caption:
        node["caption"] = caption
    c = credit or {}
    if c.get("author"):
        node["creditText"] = c["author"]
        node["copyrightNotice"] = c["author"]
        node["author"] = {"@type": "Person", "name": c["author"]}
    if c.get("license_url"):
        node["license"] = c["license_url"]
    if c.get("source"):
        node["acquireLicensePage"] = c["source"]
    return node


def attraction_images(a, lang):
    """Hero photo first, then the gallery, in the order the page renders them."""
    L = a[lang]
    out = [image_object(a.get("image"), a.get("image_credit"), L["name"])]
    out += [image_object(g.get("image"), g, f'{L["name"]} — {i + 1}')
            for i, g in enumerate(a.get("gallery") or []) if isinstance(g, dict)]
    return [x for x in out if x]
```

In `render_attraction()` (`build.py:2192`):

```python
    imgs = attraction_images(a, lang)
    graph = [org_node(lang), website_node(lang),
             page_node(lang, attr_url(lang, slug), title, desc,
                       main_entity=attr_url(lang, slug) + "#attraction",
                       image=imgs[0]["@id"] if imgs else None),
             attraction_node(slug, a, lang, imgs),
             crumbs_node(lang, [...], attr_url(lang, slug))] + imgs
```

**Produces (one gallery image on `/attractions/abano-pass/`):**

```json
{
  "@type": "ImageObject",
  "@id": "https://rentup.ge/assets/photos/abano-pass-1.webp#image",
  "url": "https://rentup.ge/assets/photos/abano-pass-1.webp",
  "contentUrl": "https://rentup.ge/assets/photos/abano-pass-1.webp",
  "caption": "Abano Pass — 1",
  "creditText": "Moahim",
  "copyrightNotice": "Moahim",
  "author": { "@type": "Person", "name": "Moahim" },
  "license": "https://creativecommons.org/licenses/by-sa/4.0",
  "acquireLicensePage": "https://commons.wikimedia.org/wiki/File:2019_-_Tusheti_National_Park_-_the_view_from_Abano_pass.jpg"
}
```

Coverage: 250 / 257 attractions have a licensed hero image; 248 have a licensed gallery. The 7
without are simply skipped by the `if not path: return None` guard.

---

### Patch 6 — `TouristAttraction`: real subtypes, drop fabricated flags (P0-4, P1-2, P2-3, P2-7)

Add above `render_attraction()`:

```python
# `type:` in content/attractions/*.yml -> a schema.org Place subtype we can
# assert without inventing anything. `winery`, `spa` and `ski` are deliberately
# unmapped: Winery, DaySpa and SkiResort are LocalBusiness subtypes and would
# imply opening hours, an address and a contact for third-party places we do
# not hold. Those stay bare TouristAttraction.
ATTRACTION_SUBTYPE = {
    "monastery": "PlaceOfWorship", "fortress": "LandmarksOrHistoricalBuildings",
    "archaeology": "LandmarksOrHistoricalBuildings", "museum": "Museum",
    "theatre": "PerformingArtsTheater", "mountain": "Mountain",
    "lake": "LakeBodyOfWater", "waterfall": "Waterfall", "beach": "Beach",
    "cave": "Landform", "canyon": "Landform", "nature": "Landform",
    "town": "TouristDestination",
}
FREE_ENTRY = {"free", "უფასო", "Бесплатно", "رایگان", "חינם", "مجاني"}


def attraction_node(slug, a, lang, imgs=()):
    L, r = a[lang], REGIONS[a["region"]]
    types = ["TouristAttraction"]
    sub = ATTRACTION_SUBTYPE.get(a.get("type"))
    if sub:
        types.append(sub)
    node = {
        "@type": types if len(types) > 1 else types[0],
        "@id": attr_url(lang, slug) + "#attraction",
        "name": L["name"], "description": L["short"],
        "url": attr_url(lang, slug), "inLanguage": lang,
        "geo": {"@type": "GeoCoordinates", "latitude": a["lat"],
                "longitude": a["lon"], "elevation": a["elevation"]},
        "address": {"@type": "PostalAddress", "addressRegion": r[lang]["name"],
                    "addressCountry": "GE"},
        # `touristType` describes the *visitor*, not the place — the old
        # "Monastery"/"Cave" values were a type error. The kind of place now
        # lives in @type above and in keywords.
        "keywords": tl(lang, "type", a["type"]),
        # Stable @id so the same place is one entity across every page that
        # links to it, instead of a fresh anonymous stub each time.
        "containedInPlace": {"@id": region_url(lang, a["region"]) + "#dest"},
        "mainEntityOfPage": {"@id": attr_url(lang, slug) + "#webpage"},
    }
    if imgs:
        node["image"] = [{"@id": x["@id"]} for x in imgs]
    # Assert only what the data says. Unknown != false, so a non-free or
    # unclear entry fee omits the property rather than claiming `false`.
    if str(a.get("entry_fee", "")).strip() in FREE_ENTRY:
        node["isAccessibleForFree"] = True
    # `publicAccess` was hard-coded True for all 257 places, including seasonal
    # 4x4-only passes. Gate it on the field that actually answers the question.
    if a.get("open_year_round"):
        node["publicAccess"] = True
    if a.get("visit_hours"):
        node["additionalProperty"] = [{
            "@type": "PropertyValue", "name": TRAVEL[lang]["ui"]["visit_time"],
            "value": float(a["visit_hours"]), "unitCode": "HUR"}]
    return node
```

`render_region()` should give its `TouristDestination` the matching `@id` it already uses
(`region_url(lang, key) + "#dest"` — unchanged) and reference its attractions by `@id` too:

```python
              "includesAttraction": [{"@id": attr_url(lang, s) + "#attraction"}
                                     for s in sub],
```

**Produces (`/attractions/gergeti-trinity-church/`, `en`):**

```json
{
  "@type": ["TouristAttraction", "PlaceOfWorship"],
  "@id": "https://rentup.ge/attractions/gergeti-trinity-church/#attraction",
  "name": "Gergeti Trinity Church",
  "description": "A 14th-century church at 2,170 m with Mount Kazbek behind it — the single most recognisable view in Georgia.",
  "url": "https://rentup.ge/attractions/gergeti-trinity-church/",
  "inLanguage": "en",
  "geo": { "@type": "GeoCoordinates", "latitude": 42.6625, "longitude": 44.6206, "elevation": 2170 },
  "address": { "@type": "PostalAddress", "addressRegion": "Mtskheta-Mtianeti", "addressCountry": "GE" },
  "keywords": "Monastery",
  "containedInPlace": { "@id": "https://rentup.ge/regions/mtskheta-mtianeti/#dest" },
  "mainEntityOfPage": { "@id": "https://rentup.ge/attractions/gergeti-trinity-church/#webpage" },
  "image": [{ "@id": "https://rentup.ge/assets/photos/gergeti-trinity-church.webp#image" }],
  "isAccessibleForFree": true,
  "publicAccess": true,
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "Time needed", "value": 3.0, "unitCode": "HUR" }
  ]
}
```

For Abano Pass (`open_year_round: false`, `entry_fee: free`) the same code correctly emits
`isAccessibleForFree: true` and **omits** `publicAccess` — today it claims `true`.

---

### Patch 7 — routes: `TouristTrip` with real numbers, no false `provider` (P1-8)

Add near the other trip helpers:

```python
def trip_properties(lang, **facts):
    """schema.org's Trip has no duration/distance/difficulty properties, so the
    numbers printed on the page go in additionalProperty. Only keys with a real
    value are emitted."""
    label = {"days": tu(lang, "days"), "km": tu(lang, "km")}
    out = []
    if facts.get("days"):
        out.append({"@type": "PropertyValue", "name": label["days"],
                    "value": facts["days"], "unitCode": "DAY"})
    if facts.get("km"):
        out.append({"@type": "PropertyValue", "name": label["km"],
                    "value": facts["km"], "unitCode": "KMT"})
    if facts.get("drive"):
        out.append({"@type": "PropertyValue", "name": tu(lang, "hrs"),
                    "value": facts["drive"]})
    if facts.get("difficulty"):
        out.append({"@type": "PropertyValue", "name": tu(lang, "difficulty"),
                    "value": tl(lang, "difficulty", facts["difficulty"])})
    if facts.get("season"):
        out.append({"@type": "PropertyValue", "name": tu(lang, "season"),
                    "value": tl(lang, "season", facts["season"])})
    if facts.get("car_category"):
        out.append({"@type": "PropertyValue",
                    "name": TRAVEL[lang]["ui"]["car_needed"],
                    "value": car_cat_label(facts["car_category"], lang)})
    return out


def route_trip_node(lang, slug, r, wp):
    L = r[lang]
    node = {
        "@type": "TouristTrip", "@id": route_url(lang, slug) + "#trip",
        "name": L["name"], "description": L["short"],
        "url": route_url(lang, slug), "inLanguage": lang,
        # `provider` was asserting that RentUp sells this trip. It does not:
        # these are editorial driving guides with no price and no booking.
        # Authorship belongs on the WebPage node, which carries `publisher`.
        "mainEntityOfPage": {"@id": route_url(lang, slug) + "#webpage"},
        "additionalProperty": trip_properties(
            lang, days=r.get("days"), km=r.get("distance_km"),
            drive=r.get("drive_time_total"), difficulty=r.get("difficulty"),
            season=r.get("best_season"), car_category=r.get("car_category")),
        "itinerary": {"@type": "ItemList", "numberOfItems": len(wp),
                      "itemListElement": [
                          {"@type": "ListItem", "position": i + 1,
                           "item": {"@id": attr_url(lang, s) + "#attraction",
                                    "@type": "TouristAttraction",
                                    "name": a[lang]["name"],
                                    "url": attr_url(lang, s)}}
                          for i, (s, a) in enumerate(wp.items())]},
    }
    return node
```

> `min_people` / `max_people` in the route YAML are **group sizes, not ages** — do not map them to
> `Audience.suggestedMinAge`. If you want them marked up, add another `PropertyValue` to
> `trip_properties()`; that is the only safe form.

**Produces (`/routes/svaneti-expedition/`, `en`, abridged):**

```json
{
  "@type": "TouristTrip",
  "@id": "https://rentup.ge/routes/svaneti-expedition/#trip",
  "name": "Svaneti Expedition",
  "description": "Five days in Upper Svaneti: Kutaisi, Zugdidi, the Enguri dam, Mestia and Ushguli.",
  "url": "https://rentup.ge/routes/svaneti-expedition/",
  "inLanguage": "en",
  "mainEntityOfPage": { "@id": "https://rentup.ge/routes/svaneti-expedition/#webpage" },
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "days", "value": 5, "unitCode": "DAY" },
    { "@type": "PropertyValue", "name": "km", "value": 1050, "unitCode": "KMT" },
    { "@type": "PropertyValue", "name": "h", "value": "21:00" },
    { "@type": "PropertyValue", "name": "Difficulty", "value": "Hard" },
    { "@type": "PropertyValue", "name": "Season", "value": "June–September" },
    { "@type": "PropertyValue", "name": "Car needed", "value": "Off-road 4x4" }
  ],
  "itinerary": {
    "@type": "ItemList", "numberOfItems": 6,
    "itemListElement": [
      { "@type": "ListItem", "position": 1,
        "item": { "@id": "https://rentup.ge/attractions/bagrati-cathedral/#attraction",
                  "@type": "TouristAttraction", "name": "Bagrati Cathedral and central Kutaisi",
                  "url": "https://rentup.ge/attractions/bagrati-cathedral/" } }
    ]
  }
}
```

---

### Patch 8 — itineraries: `subTrip` per day + `TouristDestination` chain (task item)

`content/itineraries/*.yml` holds a fully structured day plan (`plan[].day/from/to/km/drive/
stops/overnight/road`) and `content/settings/places.yml` gives every `from`/`to`/`overnight` key a
real `lat`/`lon`. That is enough for the `ItemList` of `TouristDestination` the brief asks for, plus
a per-day `subTrip`:

```python
def place_dest_node(lang, key):
    """A city/airport from places.yml as a TouristDestination with real geo.
    The @id is language-neutral because a page only ever carries one language,
    so `name` never conflicts within a graph."""
    p = PLACE_BY_KEY.get(key)
    if not p:
        return None
    return {"@type": "TouristDestination", "@id": SITE_URL + "/#place-" + key,
            "name": p.get(lang) or p.get("en") or key,
            "geo": {"@type": "GeoCoordinates",
                    "latitude": p["lat"], "longitude": p["lon"]},
            "containedInPlace": {"@type": "Country", "name": META[lang]["country"]}}


def itinerary_trip_node(lang, slug, it):
    """The visible day-by-day plan, one subTrip per day. Every number here is
    printed on the page by the trip-day renderer (build.py:3663)."""
    L, url = it[lang], itin_url(lang, slug)
    days, chain, seen = [], [], set()
    for d in it.get("plan") or []:
        stops = [s for s in (d.get("stops") or []) if s in ATTRACTIONS]
        day = {"@type": "TouristTrip", "@id": f'{url}#day-{d["day"]}',
               "name": f'{su("day", lang)} {d["day"]} — '
                       f'{_place_name(lang, d.get("from", ""))} → '
                       f'{_place_name(lang, d.get("to", ""))}',
               "additionalProperty": trip_properties(lang, km=d.get("km"),
                                                     drive=d.get("drive"))}
        # No arrivalTime/departureTime: the plan has driving durations, not
        # clock times, and Trip's time properties are DateTime-valued.
        if stops:
            day["itinerary"] = {"@type": "ItemList", "numberOfItems": len(stops),
                                "itemListElement": [
                                    {"@type": "ListItem", "position": i + 1,
                                     "item": {"@id": attr_url(lang, s) + "#attraction",
                                              "@type": "TouristAttraction",
                                              "name": ATTRACTIONS[s][lang]["name"],
                                              "url": attr_url(lang, s)}}
                                    for i, s in enumerate(stops)]}
        days.append(day)
        for key in (d.get("from"), d.get("overnight"), d.get("to")):
            node = place_dest_node(lang, key)
            if node and node["@id"] not in seen:
                seen.add(node["@id"])
                chain.append(node)
    node = {"@type": "TouristTrip", "@id": url + "#trip",
            "name": L.get("name", ""), "description": L.get("short", ""),
            "url": url, "inLanguage": lang,
            "mainEntityOfPage": {"@id": url + "#webpage"},
            "additionalProperty": trip_properties(
                lang, days=it.get("days"), km=it.get("total_km"),
                drive=it.get("total_drive"), season=it.get("best_season"),
                car_category=it.get("car_category")),
            "itinerary": {"@type": "ItemList", "numberOfItems": len(chain),
                          "itemListElement": [
                              {"@type": "ListItem", "position": i + 1,
                               "item": {"@id": p["@id"]}}
                              for i, p in enumerate(chain)]}}
    if days:
        node["subTrip"] = days
    return node, chain
```

and in `render_itinerary()` (`build.py:3700`):

```python
    _trip, _places = itinerary_trip_node(lang, slug, it)
    graph = [org_node(lang), website_node(lang),
             page_node(lang, url, title, desc, main_entity=url + "#trip"),
             _trip,
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (hub_h1, itin_hub_url(lang)),
                                (L.get("name", ""), url)], url)] + _places
```

**Produces (`/itineraries/georgia-10-days/`, `en`, abridged):**

```json
{
  "@type": "TouristTrip",
  "@id": "https://rentup.ge/itineraries/georgia-10-days/#trip",
  "name": "Georgia in 10 Days: Imereti Caves to the Guria Coast",
  "url": "https://rentup.ge/itineraries/georgia-10-days/",
  "inLanguage": "en",
  "mainEntityOfPage": { "@id": "https://rentup.ge/itineraries/georgia-10-days/#webpage" },
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "days", "value": 10, "unitCode": "DAY" },
    { "@type": "PropertyValue", "name": "km", "value": 1450, "unitCode": "KMT" },
    { "@type": "PropertyValue", "name": "h", "value": "27:00" }
  ],
  "itinerary": {
    "@type": "ItemList", "numberOfItems": 5,
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "item": { "@id": "https://rentup.ge/#place-tbilisi" } },
      { "@type": "ListItem", "position": 2, "item": { "@id": "https://rentup.ge/#place-kutaisi" } },
      { "@type": "ListItem", "position": 3, "item": { "@id": "https://rentup.ge/#place-zugdidi" } }
    ]
  },
  "subTrip": [
    {
      "@type": "TouristTrip",
      "@id": "https://rentup.ge/itineraries/georgia-10-days/#day-1",
      "name": "Day 1 — Tbilisi → Kutaisi",
      "additionalProperty": [
        { "@type": "PropertyValue", "name": "km", "value": 245, "unitCode": "KMT" },
        { "@type": "PropertyValue", "name": "h", "value": "4:00" }
      ],
      "itinerary": {
        "@type": "ItemList", "numberOfItems": 2,
        "itemListElement": [
          { "@type": "ListItem", "position": 1,
            "item": { "@id": "https://rentup.ge/attractions/uplistsikhe/#attraction",
                      "@type": "TouristAttraction", "name": "Uplistsikhe",
                      "url": "https://rentup.ge/attractions/uplistsikhe/" } }
        ]
      }
    }
  ]
},
{
  "@type": "TouristDestination",
  "@id": "https://rentup.ge/#place-kutaisi",
  "name": "Kutaisi",
  "geo": { "@type": "GeoCoordinates", "latitude": 42.2679, "longitude": 42.705 },
  "containedInPlace": { "@type": "Country", "name": "Georgia" }
}
```

---

### Patch 9 — `FAQPage` for the `/car-rental/*` cluster (P2, and drop it from the homepage)

```python
def faq_pairs_node(url, items):
    """FAQPage from an explicit q/a list (seo_car_rental.yml, seo_categories.yml).
    Every pair is rendered on the same page by _faq_html(), so markup and
    visible content cannot drift. Own @id + mainEntityOfPage so it coexists
    cleanly with the page's WebPage node instead of competing for the URL."""
    qas = [x for x in (items or []) if x.get("q") and x.get("a")]
    if not qas:
        return None
    return {"@type": "FAQPage", "@id": url + "#faq",
            "mainEntityOfPage": {"@id": url + "#webpage"},
            "mainEntity": [{"@type": "Question", "name": x["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": x["a"]}}
                           for x in qas]}
```

Call it in `render_car_rental_hub()` (after line 3475) and `render_rental_category()`
(after 3600):

```python
    _faq = faq_pairs_node(url, h.get("faq"))     # hub
    _faq = faq_pairs_node(url, L.get("faq"))     # category
    if _faq:
        graph.append(_faq)
```

Give `faq_node()` the same `@id` treatment for `/faq/`, and **remove `FAQPage` from the homepage**:
the six homepage Q&As render inside `<details class="home-more">` labelled "Rental terms and more
information" (`build.py:1200`). Google permits accordion FAQ content, so this is not a clear
violation — but the outer container does not announce Q&A, FAQ rich results are unavailable to this
site anyway, and the same six answers are marked up on `/faq/` where they are plainly visible.
Cheapest correct move: keep `faq_node()` for `/faq/` and `/fleet-management-software/`, skip it on
`index`:

```python
    f = faq_node(p["blocks"]) if page != "index" else None
```

---

### Patch 10 — `/map/` and `/tours/` (P1-10)

`render_map_page()` (`build.py:1957`) — restore the breadcrumb and the attraction list that the dead
code at 1986–2027 was meant to provide, and delete lines 1985–2027 while you are there:

```python
    _url = page_url(lang, "map")
    graph = [org_node(lang), website_node(lang),
             page_node(lang, _url, p["title"], p["desc"], types=("CollectionPage",)),
             {"@type": "ItemList", "@id": _url + "#attractions",
              "numberOfItems": len(ATTRACTIONS), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1,
                   "url": attr_url(lang, s), "name": a[lang]["name"]}
                  for i, (s, a) in enumerate(ATTRACTIONS.items())]},
             crumbs_node(lang, [(u["nav"]["index"], page_url(lang, "index")),
                                (u["nav"]["map"], _url)], _url)]
```

`render_tours_page()` (`build.py:3842`) currently ships org + WebSite only; give it the same
`page_node` + `crumbs_node` + `ItemList` of the themed tours it renders.

---

### Patch 11 — honest dates (P0-5)

```python
def content_date(path):
    """Real last-change date for a content file. Git is the source of truth so
    a fresh checkout (which resets mtimes) cannot invent a date; if git is
    unavailable the caller omits the property rather than guessing.
    NOTE: CI must check out with fetch-depth: 0 for this to be meaningful."""
    try:
        import subprocess
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                             capture_output=True, text=True, timeout=5)
        return (out.stdout or "").strip() or None
    except Exception:
        return None
```

Then in `render_static_page()` drop the hard-coded `"datePublished": "2026-01-15"` entirely and pass
`modified=content_date(f"content/pages/{page}.yml")` to `page_node()`. Same for posts
(`content/posts/<slug>.yml`), cars, attractions, routes and itineraries. If `content_date()` returns
`None`, `page_node()` already omits the key.

---

### Patch 12 — serialiser hardening (P2-8)

In `head_html()` (`build.py:797`):

```python
<script type="application/ld+json">
{J(ld).replace("</", "<\\/")}
</script>
```

`<\/` is a valid JSON string escape and prevents a `</script>` sequence inside any YAML description
from closing the tag early.

---

## 6. Deliberately **not** proposed

| Type | Why not |
|---|---|
| `aggregateRating`, `review` | No review source exists. See §8-1 and §9-1. |
| `priceValidUntil` | No expiry date exists for any rate. Inventing one is exactly the failure mode the brief forbids. |
| `Offer.availability` | No inventory system. Omitting is the honest signal; today's `InStock` is not. |
| `WebSite.potentialAction` / `SearchAction` | Retired by Google (Nov 2024) **and** rentup.ge has no search endpoint — it would describe a feature that does not exist. |
| `speakable` | Never left limited availability (US news publishers, Google Assistant). Zero upside, adds a claim about audio rendering the site does not support. |
| `HowTo` | Retired by Google in 2023. |
| `ReserveAction` / `RentAction` `potentialAction` | The booking flow is a JS modal (`data-booking-open`) with no URL. `target` needs a real bookable URL. §9-6. |
| `LocalBusiness` branch nodes for the airport pickup points | An arrivals-hall meeting point is a delivery service, not premises. Model it as a `Service` (Patch idea below) once structured hours exist. |
| `Winery` / `DaySpa` / `SkiResort` subtypes for 18 attractions | They are `LocalBusiness` subtypes and imply hours, address and contact for third-party businesses the repo does not describe. |
| `Organization.sameAs` | `site.yml` has `social: []`. The current code already guards this correctly — keep the guard. |

**Optional follow-up worth doing once hours exist** — the airport delivery fees are real
(`rental_policy.delivery.airport_fee_gel`: TBS 30, KUT 60, BUS 60 GEL; `city_fee_gel`: Kutaisi 50,
Batumi 50; `one_way.fee_gel`: 100). On `/car-rental/<airport>/` these support a truthful `Service`
node with an `Offer` — no availability claim, no opening hours, just the published fee.

---

## 7. Multilingual correctness

The site ships `en` (root), `ka`, `ru`, `fa`, `he`, `ar`. `head_html()` writes a complete
`hreflang` set plus `x-default → en` for every page. Three rules should govern the graph:

**1. One real-world entity, one `@id` — but only for entities that really are one thing.**

| Entity | `@id` | Rationale |
|---|---|---|
| The company | `https://rentup.ge/#organization` (language-neutral) — **keep as is** | There is one RentUp. `name`, `description`, `url` and `address` vary per language, which is fine: Google evaluates one page at a time, and each page's graph is internally consistent. |
| The logo | `https://rentup.ge/#logo` | One file. |
| A city/airport from `places.yml` | `https://rentup.ge/#place-<key>` | One real place, per-language `name`. |
| A website | `https://rentup.ge/<lang>/#website` — **change from the current shared `/#website`** | Six different `url` + `inLanguage` values cannot share one identifier. |
| A page, a breadcrumb, an FAQ, an offer, a vehicle, an attraction, a trip | `<per-language page URL>#webpage` / `#breadcrumb` / `#faq` / `#offer` / `#vehicle` / `#attraction` / `#trip` — **keep the current per-language scheme** | These nodes carry translated prose. Per-language `@id` keeps each graph self-describing and avoids one identifier claiming six different `name` values. |

**2. `inLanguage` on everything that carries prose.** Today only `WebSite`, `Blog`, `BlogPosting`,
`WebApplication` and three of the `WebPage` variants have it. Every patch above adds it to `WebPage`,
`Car`, `TouristAttraction`, `TouristTrip`, `TouristDestination`.

**3. Do not cross-link language variants in `sameAs`.** `sameAs` means "the same entity described by
another *authority*" (Wikidata, an official profile) — not "the same content in another language".
That relationship is `hreflang`'s job and it is already correct. If a schema-level link is wanted,
the only defensible form is `WebPage.translationOfWork: {"@id": "<x-default en page>#webpage"}` on
the five non-English variants; it is understanding-only and entirely optional.

One consequence to watch: `SoftwareApplication` has the same shared-`@id` problem as `WebSite`
(`https://rentup.ge/#software`, but per-language `url`, `description` and `applicationSubCategory`).
Give it `page_url(lang, "software") + "#software"`, or move the language-varying prose out.

---

## 8. Manual-action risk register

| Risk | Assessment |
|---|---|
| **8-1. `rating:` on 248 attractions.** Each attraction YAML carries an editorially assigned 1–5 score, rendered as visible stars (`stars_html`, `build.py:1516`). It is **not** in the JSON-LD today. | **Keep it that way.** Mapping it to `aggregateRating` would be a self-assigned, self-serving rating with no `reviewCount`/`ratingCount` and no user or expert source — squarely inside Google's unsupported-review-snippet policy, and `TouristAttraction` is not a rating-eligible type anyway. The visible stars are fine because the `title`/`aria-label` already frame them as an editorial score; consider making that label explicit in the visible text too. |
| **8-2. `SoftwareApplication.operatingSystem` claims iOS 13+.** The site's own header renders "iPhone / iOS — Coming soon". | Markup asserting a product that does not ship. Fix to `"Android 7.0+"` until the iOS build exists. P0-3. |
| **8-3. Homepage `FAQPage` inside a collapsed `<details>`.** Answers render at byte 81 497; the collapsed container opens at 74 983. | Google explicitly permits FAQ content in expandable sections, so this is **not** a clear violation — but the container is labelled "Rental terms and more information", not an FAQ, and FAQ rich results are unavailable to this site regardless. Lowest-cost resolution is Patch 9: drop `FAQPage` from `index` and keep it on `/faq/`. |
| **8-4. `Offer.availability: InStock` on 102 car pages + 6 fleet pages.** | Unverifiable availability claim with no inventory behind it. Not a rating violation, but it is marked-up content the page cannot substantiate. Patch 3 removes it. |
| **8-5. `publicAccess: true` on all 257 attractions**, including seasonal 4×4-only passes closed 8 months a year. | Same category. Patch 6 gates it on `open_year_round`. |
| **8-6. `Organization.description` claims "full insurance coverage".** | The strongest factual exposure on the site: it appears on all 2 112 pages in 6 languages, and the repo's own policy file explicitly refuses the claim. Content fix, not a code fix. P0-1. |
| **8-7. `llms.txt` contradicts `rental_policy.yml` on five commercial terms** (age, mileage, fuel, insurance, cross-border) and on whether online payment exists. | Not structured data, but it is the machine-readable fact sheet and the most likely source anyone would copy into schema. Resolve before writing any commercial-terms markup. P0-6. |
| **8-8. `TouristTrip.provider: RentUp` on 222 pages.** | Asserts RentUp provides trips it does not sell. Low policy risk, high accuracy risk with AI answer engines that will repeat it. P1-8. |

No unsupported `review`, `aggregateRating`, `Event`, `JobPosting` or `Recipe` markup exists anywhere
in `dist/`. The site's current exposure is claim accuracy, not markup abuse.

---

## 9. Blocked — needs real data from the owner

Each item lists the schema it unlocks and the exact question to ask.

| # | Ask | Unlocks | Where the answer goes |
|---|---|---|---|
| 1 | **Do you have a real, published review source** (Google Business Profile reviews, a review platform, or first-party reviews you would publish with author + date)? How many, and what is the average? | `aggregateRating`, `review` — the only remaining large rich-result win. **Until then: nothing.** The `rating:` field on attractions is an editorial score and must never be used for this. | new `content/settings/reviews.yml`; nothing until it exists |
| 2 | **Photographs of the 17 cars.** All 17 have `image: ''` and `gallery: []`. | `Car.image` (required for essentially every product-shaped rich result), per-car `og:image`, `primaryImageOfPage` on `/fleet/<slug>/` | `content/cars/*.yml` → `image:`, `gallery:` |
| 3 | **Opening hours per pickup point, as structured values.** The contact page prints six rows as free text ("Arrivals hall, 24 hours", "According to flight schedule", "By arrangement", "May–October"). Which of these are staffed premises, and what are the exact `opens`/`closes` per day? Also: is the 24/7 hotline genuinely staffed 24/7? | `OpeningHoursSpecification` per location, a second 24/7 `ContactPoint`, and possibly `Service` nodes on `/car-rental/<city>/` | `content/settings/places.yml` (per-place `opens`/`closes`) and `site.yml` (`hotline_24_7`) |
| 4 | **Is online booking + prepayment real?** `booking.yml` says `enabled: true, payment_required: true`; `contact.yml` says "the site has no online form or payment system"; `rental_policy.yml` says `prepayment_required: false`; `llms.txt` says payment is required before confirmation. | `Offer.acceptedPaymentMethod`, `advanceBookingRequirement`, `potentialAction` | resolve across `booking.yml`, `rental_policy.yml`, `contact.yml`, `meta.yml` |
| 5 | **Sign off `rental_policy.yml`.** The file's own header says *"STATUS: PROPOSED DEFAULTS drafted for the owner's approval (2026-08-29)"*. Patch 3 reads `min_rental_days`/`max_rental_days` from it and Patch 2 reads `support.languages`. | `Offer.eligibleDuration`, `ContactPoint.availableLanguage`, and every commercial-terms statement on the `/car-rental/` cluster | `content/settings/rental_policy.yml` header |
| 6 | **A bookable URL.** The booking flow is a JS modal with no address; there is no `/book/` or `?book=` route. | `ReserveAction`/`RentAction` `potentialAction`, and a precise `Offer.url` per car | new route in `build.py` + `Offer.url` |
| 7 | **Cross-border, fuel, mileage, driver age, insurance — one authoritative answer each** (see the P0-6 table). | Any commercial-terms markup at all; also stops AI answer engines repeating contradictions | `rental_policy.yml` as sole source; regenerate `meta.yml` `llms_facts` from it |
| 8 | **Do you actually operate the 32 routes and 5 itineraries as sellable trips** (with a driver, at a price), or are they editorial guides? | Decides `TouristTrip.provider` and whether an `Offer` may hang off a trip at all | `content/routes/*.yml`, `content/itineraries/*.yml` |
| 9 | **Legal entity name, company registration number, VAT/tax ID.** | `Organization.legalName`, `taxID`, `vatID`, `identifier` — strong entity-disambiguation signals | `site.yml` |
| 10 | **Social profiles and a Google Business Profile URL / CID.** `site.yml` has `social: []`. | `Organization.sameAs`, `hasMap` — the single strongest local-entity signal after NAP consistency | `site.yml` → `social:` |
| 11 | **A contact email.** `site.yml` has `email: ''`, yet `contact.yml` says bookings are made "by phone or email" in all six languages. | `Organization.email`, `ContactPoint.email` | `site.yml` |
| 12 | **A square logo at ≥ 112 px per side** with the brand mark. The only logo asset is 180 × 72. Patch 2 substitutes `app-icon-512.png` as a stopgap. | `Organization.logo` at the quality Google wants | `content/settings/design.yml` |
| 13 | **Airport pickup reality check.** Is there a counter/desk at TBS/KUT/BUS, or only a meeting point? | Whether any location may be typed as an `AutoRental` branch, or must stay a `Service` with `areaServed` | `content/settings/places.yml` |
| 14 | **Wikidata / Wikipedia IDs for the 257 attractions** (or at least the 6 UNESCO sites). | `TouristAttraction.sameAs` — the highest-value entity-linking signal for the travel cluster, and cheap to source from the Wikimedia Commons URLs already in the YAML | `content/attractions/*.yml` → `sameAs:` |
| 15 | **Payment methods and currencies, confirmed.** `meta.yml` asserts "Cash, Visa, Mastercard, bank transfer" and `GEL, USD, EUR`. Does the office genuinely take EUR and USD cash? | `paymentAccepted`, `currenciesAccepted` — currently asserted without a source in the repo | `site.yml` or `rental_policy.yml` |

---

## 10. Suggested order of work

1. **P0 content fixes first, no code:** `meta.yml` `org_desc` (insurance claim) and `llms_facts`
   (five contradictions), regenerated from `rental_policy.yml`. Nothing else is safe to amplify
   until these are true.
2. **Patch 12** (serialiser), **Patch 1** (`website_id`, `page_node`, `crumbs_node` `@id`) — the
   structural spine; every later patch depends on it.
3. **Patch 2** (org), **Patch 3** (car), **Patch 6** (attraction) — removes P0-2, P0-4, P1-2…P1-7.
4. **Patch 5** (`ImageObject` licences) — the only new rich-result eligibility available today.
5. **Patch 11** (dates), **Patch 10** (`/map/`, `/tours/`), **Patch 4** (`AggregateOffer`),
   **Patch 9** (FAQ), **Patch 7 / 8** (trips).
6. Re-run the validator: `dist/` should still show 0 parse errors and 0 unresolved `@id`s, plus
   `WebPage` on ~2 100 pages instead of 120 and `ImageObject` on ~1 500 attraction pages.
