# RentUp.ge — SEO Audit (Phase 0 baseline)

Audit date: 2026-08-29 · Auditor: lead SEO engineer pass over repo + live production
Production: https://rentup.ge (GitHub Pages) · Repo: `ko500pl/car-rental-site`

This document records **observed** behaviour. No production code was changed to produce it.

---

## 1. Architecture

| Aspect | Finding |
|---|---|
| Framework | Custom Python static site generator. `build.py` (295 KB) + `theme.py` (155 KB CSS) → `dist/` |
| Rendering | **100 % pre-rendered static HTML.** No SSR runtime, no client-side routing. Excellent crawlability baseline. |
| Routing | Filesystem: every page is `dist/<path>/index.html` |
| Content source | YAML under `content/` — `attractions/` (257), `routes/` (32), `cars/` (17), `regions/` (11), `posts/` (4), `pages/` (12), `settings/` (15) |
| Metadata | Centralised in `head_html()` (build.py:534) — single choke point for title/desc/canonical/hreflang/OG/JSON-LD. **Major asset.** |
| Localization | `ALL_LANGS = [en, ka, ru, fa, he, ar]`; `ROOT_LANG = "en"` → English at `/`, others at `/{lang}/`. RTL handled (`dir="rtl"` for fa/he/ar). |
| Images | `/assets/photos/*.webp`, hashed asset pipeline (`write_hashed`), `loading="lazy"` in listings |
| Deployment | GitHub Pages via `.github/workflows/pages.yml` — quality gate on push, **manual `workflow_dispatch` to deploy** |
| Tests | `tests/test_sitegen.py`, `tests/test_content_quality.py`, `tests/test_map_chunking.py` (36 tests) + `scripts/run_quality_gate.py` |
| CDN/caching | GitHub Pages edge; hashed asset filenames give immutable caching |

### Data model strength (the core SEO asset)

**Attraction** (`content/attractions/*.yml`): `region, type, lat, lon, elevation, unesco, image, gallery, visit_hours, best_season, open_year_round, entry_fee, distance_tbilisi_km, drive_time_tbilisi, road, car_category, nearby[], rating` + per-language `name, short, body, tip, route`.

**Route** (`content/routes/*.yml`): `days, nights, purpose, min_people, max_people, distance_km, drive_time_total, car_category, best_season, difficulty, waypoints[], sources[]` + per-language `name, short, body, plan, tips`.

**Car** (`content/cars/*.yml`): `category, years, engine, transmission, drive, seats, luggage, fuel_100km, clearance, price_1_6, price_7_29, price_30, deposit` + per-language `name, summary, features[]`.

**Places** (`content/settings/places.yml`): 40 places including `tbilisi-airport`, `kutaisi-airport`, `batumi-airport` (kind: `airport`) and 37 cities.

**Categories**: `economy, suv, business, offroad, minivan, van`.

> This is real, structured, product-backed data. The SEO strategy is to **expose relationships that already exist in the data**, not to write filler.

---

## 2. Technical SEO — current state

| Check | Status | Evidence |
|---|---|---|
| `robots.txt` | ✅ Valid | `User-agent: * / Allow: / / Disallow: /admin/`, AI-bot allow list, `Sitemap:` + `Host:` |
| Sitemap exists | ✅ | `/sitemap.xml`, 2 142 `<loc>`, 1.9 MB, `xhtml:link` alternates per URL |
| Sitemap = index? | ❌ | Single monolithic file. Within limits but unmanageable and hides gaps. |
| http → https | ✅ 301 | `http://rentup.ge/` → `https://rentup.ge/` |
| www → apex | ✅ 301 | `https://www.rentup.ge/` → `https://rentup.ge/` |
| Trailing slash | ✅ 301 | `/fleet` → `/fleet/` (consistent trailing-slash policy) |
| 404 | ✅ | `/nonexistent-xyz/` → 404, custom 404 page, `noindex, follow` |
| Canonical | ✅ Self-referencing absolute on every indexable page |
| hreflang | ✅ 6 langs + `x-default` (7 links) on all localized pages |
| Redirect chains/loops | ✅ None observed |
| JS dependency for SEO text | ✅ None — headings, descriptions, prices, route data all in static HTML |
| Structured data | ✅ Rich (table below) |
| Breadcrumbs | ✅ Visible + `BreadcrumbList` JSON-LD |

### Structured data per template (live)

| Template | JSON-LD `@type`s |
|---|---|
| `/` | AutoRental+LocalBusiness, WebSite, WebPage, BreadcrumbList, **FAQPage**, SoftwareApplication, ItemList |
| `/fleet/` | AutoRental+LocalBusiness, WebSite, WebPage, BreadcrumbList, OfferCatalog, ItemList |
| `/map/` | AutoRental+LocalBusiness, WebSite, CollectionPage |
| `/attractions/{slug}/` | AutoRental+LocalBusiness, WebSite, TouristAttraction, BreadcrumbList |
| `/routes/{slug}/` | AutoRental+LocalBusiness, WebSite, TouristTrip, BreadcrumbList |
| `/fleet/{car}/` | AutoRental+LocalBusiness, WebSite, Car, BreadcrumbList |

---

## 3. Page / template inventory

Legend — **Idx** = indexable, **SD** = structured data, **SM** = in sitemap.

| URL pattern | Type | Idx | Canonical | Title (live, EN) | H1 | SD | SM | SEO intent | Problems | Recommended action |
|---|---|---|---|---|---|---|---|---|---|---|
| `/` | Home | ✅ | self | `Plan and Share a Trip in Georgia \| Drive On` | `What is your plan for today?` | 7 types | ✅ | brand + dual product | **Brand = "Drive On"**; H1 has zero keyword signal; no "car rental" in title | Rebrand to RentUp; H1 → *Car Rental & Road Trip Planning in Georgia*; add semantic H2 sections |
| `/fleet/` | Product list | ✅ | self | `Fleet — the cars we rent out \| Drive On` | `Our fleet` | OfferCatalog | ✅ | fleet browsing | Weak title; not a transactional intent page | Keep as catalogue; create `/car-rental/` as intent hub linking here |
| `/fleet/{car}/` (17) | Product | ✅ | self | `{Car} — rental in Georgia…` | car name | Car | ✅ | model rental | OK | Add category + route cross-links |
| `/map/` | **Trip planner** | ✅ | self | `Map of Georgia's attractions — 267 places…` | **none (0 H1)** | CollectionPage | ❌ **absent** | *Georgia trip planner* | **Not in sitemap. No H1.** Highest-value miss on the travel side. | Add H1, rewrite title/desc, add crawlable explainer copy, add to sitemap, alias `/trip-planner/` |
| `/tours/` | Route index | ✅ | self | `Standard tours \| Drive On` | `Standard tours` | — | ❌ **absent** | ready-made road trips | Not in sitemap; no schema; generic title | Add to sitemap, `ItemList`, better title, becomes `/routes/` hub |
| `/routes/{slug}/` (32) | Road trip | ✅ | self | `{Route} — 3 days, 640 km \| Drive On` | route name | TouristTrip | ✅ | *Tbilisi to X road trip* | Good base; missing stop images (fixed), vehicle/category links | Upgrade template: road quality, seasonality, vehicle CTA, itinerary links |
| `/attractions/{slug}/` (257) | Place guide | ✅ | self | `{Place} — Fortress, 1:20 From Tbilisi \| Drive On` | place name | TouristAttraction | ✅ | *things to do / places to visit* | Formulaic titles across 257 pages | Differentiate titles by type; add nearby/route/vehicle links |
| `/regions/{key}/` (11) | Region hub | ✅ | self | region | region | — | ✅ | regional browsing | Thin schema | Add `CollectionPage` + `ItemList` |
| `/blog/`, `/blog/{post}/` (4) | Editorial | ✅ | self | ok | ok | — | ✅ | informational | Only 4 posts | Low priority |
| `/terms/`, `/faq/`, `/about/`, `/contact/`, `/community/`, `/fleet-management-software/` | Static | ✅ | self | ok | ok | — | ✅ | trust / support | FAQ content not reused on money pages | Reuse FAQ blocks on `/car-rental/` |
| `/trip/` | User trip view | ❌ noindex,nofollow | self | `My route` | `My route` | — | ❌ | private output | Correct | Keep noindex |
| `/account/` | Account | ❌ noindex,nofollow | self | `My page` | `My page` | — | ❌ | private | Correct | Keep noindex |
| `/app/` | Mobile app UI | ❌ noindex | — | `Drive On — Trip planner` | **4 × H1** | — | ❌ | app shell | 4 H1s; no hreflang | Reduce to 1 H1 (a11y) |
| `/pricing/` | Legacy | ❌ noindex | → `/fleet/` | — | — | — | ❌ | legacy | Meta-refresh soft redirect | Acceptable on GH Pages; keep canonical + noindex |
| `/business-card/` | Card | ✅? | self | — | — | — | ❌ | offline | Not in sitemap | Decide: noindex or index |
| `/admin/bookings.html` | Admin | ❌ noindex,nofollow + `Disallow` | — | — | — | — | ❌ | internal | Correct | Keep |
| **`/car-rental/`** | — | — | — | — | — | — | — | **car rental Georgia** | **DOES NOT EXIST** | Create (Release B) |
| **`/car-rental/{city\|airport}/`** | — | — | — | — | — | — | — | **car rental Tbilisi / TBS airport…** | **DOES NOT EXIST** | Create from `places.yml` (Release B) |
| **`/car-rental/{category}/`** | — | — | — | — | — | — | — | **4x4 / SUV rental Georgia** | **DOES NOT EXIST** | Create from `categories.yml` (Release B) |
| **`/itineraries/`, `/itineraries/georgia-N-days/`** | — | — | — | — | — | — | — | **Georgia itinerary N days** | **DOES NOT EXIST** | Curate from routes (Release C) |

---

## 4. Findings ranked by impact

### P0 — blocking commercial visibility

1. **Brand identity mismatch.** Every `<title>`, `og:site_name`, `author`, and `AutoRental.name` says **"Drive On"**, while the domain, the app, the APK and the UI say **RentUp**. Brand queries for "RentUp" have no matching title signal, and the site looks inconsistent to both users and Google. Source: `content/settings/site.yml → rental_brand: Drive On`.
2. **No `/car-rental/` hub.** The single highest-value commercial cluster ("car rental Georgia", "rent a car Georgia") has no landing page. `/fleet/` is a catalogue, not an intent page, and its title ("Fleet — the cars we rent out") targets nothing.
3. **No location pages.** `places.yml` already contains `tbilisi-airport`, `kutaisi-airport`, `batumi-airport` + 37 cities, yet there is no page for "Tbilisi airport car rental" — one of the highest-converting query classes in the market.
4. **No vehicle-category pages.** `categories.yml` has 6 categories; "4x4 rental Georgia" and "SUV rental Georgia" have nowhere to land.

### P1 — blocking travel visibility

5. **`/map/` — the trip planner — is missing from the sitemap and has no `<h1>`.** It is the product that should own "Georgia trip planner" / "Georgia road trip planner".
6. **`/tours/` missing from the sitemap** (new page, not yet wired into `sitemap()`).
7. **No itinerary cluster.** 32 routes carry `days`, `distance_km`, `drive_time_total`, `car_category`, `best_season`, `waypoints` — everything needed for "Georgia itinerary 3/5/7/10/14 days" — but no N-day pages exist.
8. **English titles are translations of Georgian marketing copy**, not search-intent phrasing.

### P2 — quality / hygiene

9. `FAQPage` schema on `/` — Google restricts FAQ rich results to authoritative gov/health sites; keep the FAQ for users, do not treat the markup as a ranking device.
10. `<meta name="keywords">` emitted on every page — obsolete, ignored, remove.
11. `/app/` has 4 `<h1>` elements (noindex, so SEO-neutral, but an accessibility defect).
12. Attraction titles are formulaic across 257 pages (`{Name} — {Type}, {H:MM} From Tbilisi`).
13. Single 1.9 MB sitemap instead of an index — makes coverage gaps (like `/map/`) invisible.
14. `/business-card/` not in sitemap and has no explicit index decision.

### Not problems (verified good — do not "fix")

- Static pre-rendering, canonicals, hreflang, redirect policy, 404s, breadcrumbs, and the JSON-LD baseline are all in good shape.
- Content is genuine and product-backed. There is **no** existing doorway/thin-content problem to unwind.

---

## 5. Constraints that shape the plan

| Constraint | Consequence |
|---|---|
| GitHub Pages hosting | No server-side 301s or header control. Redirects must be meta-refresh + canonical (already the pattern for `/pricing/`), or DNS/CDN level. |
| Manual deploy gate | Every release must pass `scripts/run_quality_gate.py` and then a manual `workflow_dispatch`. |
| 6 languages × every new page | Each new template multiplies by 6. New clusters must be data-driven templates, never hand-written per language. |
| No invented facts | Deposit, mileage, insurance, delivery fees, airport pickup rules are **not** all present in `content/settings/booking.yml`. Any page needing them must either source them from YAML or omit the claim. Gaps are listed in `SEO_IMPLEMENTATION_PLAN.md §Open questions`. |

---

## 6. Baseline metrics (2026-08-29)

| Metric | Value |
|---|---|
| Indexable URLs in sitemap | 2 142 (357 × 6 languages) |
| Attraction pages | 257 × 6 = 1 542 |
| Route pages | 32 × 6 = 192 |
| Car pages | 17 × 6 = 102 |
| Region pages | 11 × 6 = 66 |
| Commercial intent pages | **0** |
| Itinerary pages | **0** |
| Trip-planner landing in sitemap | **No** |
| Homepage crawlable text | 8 570 chars |
| `/map/` crawlable text | 2 539 chars (mostly chrome) |
