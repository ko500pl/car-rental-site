# RentUp.ge — URL Map

Convention (unchanged, already correct — **do not migrate**):
- English at root `/…`, other languages at `/{lang}/…` for `ka, ru, fa, he, ar`
- **Trailing slash always**, lowercase, no query parameters in canonical URLs
- Absolute self-referencing canonical, hreflang cluster of 6 + `x-default` → English

> Existing indexed URLs are preserved. New URLs are additive only. No 301 migrations are proposed.

---

## Existing (keep)

| URL | Type | Count | Index |
|---|---|---|---|
| `/` | Home | 1 | ✅ |
| `/fleet/` | Fleet catalogue | 1 | ✅ |
| `/fleet/{car}/` | Vehicle | 17 | ✅ |
| `/map/` | Interactive planner | 1 | ✅ (fix: add H1 + sitemap) |
| `/tours/` | Ready-made routes index | 1 | ✅ (fix: add to sitemap) |
| `/routes/{slug}/` | Road trip | 32 | ✅ |
| `/attractions/{slug}/` | Place guide | 257 | ✅ |
| `/regions/{key}/` | Region hub | 11 | ✅ |
| `/blog/`, `/blog/{post}/` | Editorial | 5 | ✅ |
| `/about/`, `/contact/`, `/terms/`, `/faq/`, `/community/`, `/fleet-management-software/` | Static | 6 | ✅ |
| `/trip/`, `/account/`, `/app/`, `/admin/…`, `/pricing/` | Utility | 5 | ❌ noindex |

## New — Release B (car rental cluster)

| URL | Primary intent | Data source |
|---|---|---|
| `/car-rental/` | car rental Georgia · rent a car Georgia | `cars/*`, `categories.yml`, `booking.yml`, `pages/terms.yml` |
| `/car-rental/tbilisi/` | car rental Tbilisi | `places.yml:tbilisi` + routes starting near Tbilisi |
| `/car-rental/tbilisi-airport/` | Tbilisi airport car rental (TBS) | `places.yml:tbilisi-airport` |
| `/car-rental/kutaisi/` | car rental Kutaisi | `places.yml:kutaisi` |
| `/car-rental/kutaisi-airport/` | Kutaisi airport car rental (KUT) | `places.yml:kutaisi-airport` |
| `/car-rental/batumi/` | car rental Batumi | `places.yml:batumi` |
| `/car-rental/batumi-airport/` | Batumi airport car rental (BUS) | `places.yml:batumi-airport` |
| `/car-rental/economy/` | cheap car rental Georgia | `categories.yml:economy` + cars |
| `/car-rental/suv/` | SUV rental Georgia | `categories.yml:suv` |
| `/car-rental/4x4/` | 4x4 rental Georgia | `categories.yml:offroad` |
| `/car-rental/minivan/` | minivan / 7-seater rental Georgia | `categories.yml:minivan` |

Deferred until data exists: `business`, `van` category pages; additional cities.

## New — Release C (travel cluster)

| URL | Primary intent | Data source |
|---|---|---|
| `/trip-planner/` | Georgia trip planner · road trip planner | planner product + routes + attractions |
| `/itineraries/` | Georgia itinerary (hub) | routes aggregated by `days` |
| `/itineraries/georgia-3-days/` | Georgia itinerary 3 days | routes with `days == 3` |
| `/itineraries/georgia-5-days/` | Georgia itinerary 5 days | `days == 5` |
| `/itineraries/georgia-7-days/` | Georgia itinerary 7 days | `days == 7` (or 6–8 band) |
| `/itineraries/georgia-10-days/` | Georgia itinerary 10 days | combination of routes |
| `/itineraries/georgia-14-days/` | Georgia itinerary 14 days | combination of routes |

**Quality gate:** an itinerary URL is only emitted (and only enters the sitemap) if it resolves to real day-by-day data — see `SEO_VALIDATION.md`. Bands with no qualifying data are **not** published.

## Deliberately NOT created

| Rejected | Why |
|---|---|
| `/car-rental/{37 cities}/` | No genuinely different information per city → doorway pages |
| `/attractions/{type}/` for all types | Region hubs already provide navigation |
| Per-language duplicate domains, `tripup.ge` clone | Duplicate competing site — see `SEO_IMPLEMENTATION_PLAN.md §Phase 25` |
| `/itineraries/georgia-{1..30}-days/` | Mass-generated variants |
| Filter/sort/search URLs | Index bloat — kept out of sitemap and `noindex` where they exist |
