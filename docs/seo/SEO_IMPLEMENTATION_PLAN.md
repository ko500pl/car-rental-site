# RentUp.ge — SEO Implementation Plan

Derived from `SEO_AUDIT.md`. Sequenced into five releases; each release ships independently, passes the quality gate, and is committed separately.

---

## Release A — Technical foundation

| # | Change | File | Risk |
|---|---|---|---|
| A1 | **Brand → RentUp.** `rental_brand: RentUp` (+ `rental_brand_ka: რენტაპი`). Propagates to every title, `og:site_name`, `author`, `AutoRental.name`, footer. | `content/settings/site.yml` | Low — one value, 2 142 pages inherit |
| A2 | **Add `/map/`, `/tours/`, `/business-card/` decision to sitemap.** `/map/` + `/tours/` indexable and included; `/business-card/` stays out (`noindex`). | `build.py:sitemap()` | Low |
| A3 | **Sitemap index.** `/sitemap.xml` becomes an index pointing at `/sitemaps/core.xml`, `cars.xml`, `attractions.xml`, `routes.xml`, `regions.xml`, `blog.xml` (+ later `car-rental.xml`, `itineraries.xml`). Only canonical 200 pages. | `build.py` | Medium — must keep old URL working (it does: index at same path) |
| A4 | **`/map/` gets an `<h1>`** and search-intent title/description. | `build.py:render_map_page()` | Low |
| A5 | **Title templates by page type**, English rewritten for intent (see table below). | `build.py` + `content/pages/*.yml` | Medium |
| A6 | **Remove `<meta name="keywords">`.** | `build.py:head_html()` | Low |
| A7 | **`/app/` → single `<h1>`** (a11y). | `build.py:render_app_page()` | Low |
| A8 | **SEO test suite** `tests/test_seo.py` + `scripts/seo_audit.py` (see `SEO_VALIDATION.md`). | new | Low |

### Title templates (Release A)

| Page type | Template |
|---|---|
| Home | `Car Rental & Georgia Road Trip Planner \| RentUp` |
| Fleet | `Rental Cars in Georgia — Economy, SUV & 4x4 \| RentUp` |
| Vehicle | `{Model} Rental in Georgia — from {price} ₾/day \| RentUp` |
| Planner (`/map/`) | `Georgia Road Trip Planner — Build Your Route \| RentUp` |
| Routes hub (`/tours/`) | `Georgia Road Trips — {n} Ready-Made Routes \| RentUp` |
| Route | `{Route}: Route, Stops & Best Car — {days} days, {km} km \| RentUp` |
| Attraction | `{Place}: {type} Guide — {drive} from Tbilisi \| RentUp` (varied by type) |
| Region | `{Region} Attractions — {n} Places to Visit \| RentUp` |
| Car rental hub | `Car Rental in Georgia — Rent a Car with RentUp` |
| Location | `Car Rental in {City} \| RentUp Georgia` |
| Airport | `{Airport} Car Rental ({IATA}) \| RentUp` |
| Category | `{Category} Rental in Georgia — {n} Cars from {price} ₾/day \| RentUp` |
| Itinerary | `{N}-Day Georgia Road Trip Itinerary — Route, Km & Car \| RentUp` |

---

## Release B — Car rental cluster

1. `render_car_rental_hub(lang)` → `/car-rental/`
   Sections: categories overview · real fleet preview with real rates · rental requirements (from `terms.yml` only) · deposit per car (`car.deposit`, real) · pickup locations (`places.yml`) · FAQ reused from `faq.yml` · booking CTA · links to locations, categories, routes.
2. `render_rental_location(lang, place)` for the 6 served places.
   **Genuinely unique per page:** coordinates/map, distance table to that place's nearest routes, which routes start there, which categories are recommended for those routes, airport vs city pickup wording, drive times from `road_legs.yml`.
   Any page that cannot be filled with ≥3 location-specific data blocks is **not generated**.
3. `render_rental_category(lang, category)` for `economy, suv, offroad(4x4), minivan`.
   Real models, seats, luggage, clearance, fuel, price bands; routes where `route.car_category == category`; attractions where `attraction.car_category == category`; honest limitations.
4. Internal links wired both ways; sitemap child `car-rental.xml`.
5. Schema: `WebPage` + `BreadcrumbList` + `ItemList` of real `Car` nodes. **No fake `Offer`/`AggregateRating`.**

---

## Release C — Travel cluster

1. `/trip-planner/` landing — crawlable explanation of the actual tool + embedded entry to `/map/`; links to routes, itineraries, attractions, car rental.
2. `/itineraries/` hub + curated `georgia-{3,5,7,10,14}-days` pages composed from real routes.
   Each day row: start → destination, km, drive time, stops (linked attractions), overnight, road note, recommended vehicle — all from YAML.
3. Route template upgrade: road quality, seasonality, vehicle requirement, "open in planner", "rent a car", stop photos (already shipped), next-route link.
4. Attraction template upgrade: nearby places, part-of-routes, best car, add-to-trip CTA, differentiated titles.

---

## Release D — Performance & images

Lighthouse pass on: `/`, `/car-rental/`, `/trip-planner/`, `/fleet/`, vehicle, attraction, route, itinerary.
Targets LCP ≤ 2.5 s · INP ≤ 200 ms · CLS ≤ 0.1.
Focus: hero image sizing/`fetchpriority`, Leaflet loading strategy, font loading, explicit image dimensions, `srcset`, alt-text audit across 257 attraction images.

---

## Release E — Quality gate & scale

- Content quality gate: a generated page is indexable only if it passes `seo_quality_ok()` (min data completeness). Otherwise `noindex` + excluded from sitemap.
- Index-bloat prevention: confirm `noindex` on `/trip/`, `/account/`, `/app/`, `/admin/`, `/pricing/`, planner state URLs.
- Extend internal graph; add remaining high-value routes only where data is reliable.

---

## Open questions — require business input (do NOT guess)

| # | Question | Why it blocks | Placeholder behaviour |
|---|---|---|---|
| 1 | Is **airport delivery** offered at TBS/KUT/BUS, and at what fee? | Airport pages need pickup logistics to be non-doorway | Pages describe location + routes only; no delivery claims |
| 2 | **Mileage policy** — unlimited or capped? | Blocks "unlimited mileage" query | Term omitted entirely |
| 3 | **Deposit waiver** — is a no-deposit option available? | Blocks "no deposit" query | Only per-car `deposit` values shown |
| 4 | **One-way rental** between cities — allowed? fee? | Blocks "one way car rental" | Not mentioned |
| 5 | Minimum **driver age / licence experience** requirement | Standard rental-terms content | Only what `terms.yml` already states |
| 6 | **Insurance** inclusions/excess | Trust + terms section | Only existing terms text |
| 7 | Is the **Vazha-Pshavela 71** office publicly visitable (for `LocalBusiness` address)? | Already in schema — confirm it is a real public office | Left as-is (existing data) |
| 8 | Confirm **RentUp** is the final brand and "Drive On" is retired everywhere | A1 depends on it | Proceeding with RentUp per product/domain/APK evidence; reversible in one YAML value |

## Phase 25 — tripup.ge / tripup.com.ge

Both are **redirect-only domains**, not part of this repo's deployment. `tripup.com.ge` already 301s to `https://rentup.ge/` preserving path; `tripup.ge` is pending registrar action. **Recommendation: keep them as pure 301s. Do not publish content on them** — a cloned site would compete with rentup.ge for identical queries. No DNS changes will be made without explicit authorization.
