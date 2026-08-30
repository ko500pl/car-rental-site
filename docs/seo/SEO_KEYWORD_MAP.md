# RentUp.ge — Keyword → Page Map

One primary intent per page. Secondary terms may appear on the page but must not spawn their own URL.

## Cluster 1 — Car rental (transactional)

| Primary query | Page | Status | Secondary terms held by same page |
|---|---|---|---|
| car rental Georgia / rent a car Georgia | `/car-rental/` | **NEW** | car hire Georgia, rental terms, deposit, mileage |
| car rental Tbilisi / rent a car Tbilisi | `/car-rental/tbilisi/` | **NEW** | Tbilisi car hire, city pickup |
| Tbilisi airport car rental / TBS | `/car-rental/tbilisi-airport/` | **NEW** | airport pickup, arrivals delivery |
| car rental Kutaisi | `/car-rental/kutaisi/` | **NEW** | — |
| Kutaisi airport car rental / KUT | `/car-rental/kutaisi-airport/` | **NEW** | low-cost flight arrivals |
| car rental Batumi | `/car-rental/batumi/` | **NEW** | seaside pickup |
| Batumi airport car rental / BUS | `/car-rental/batumi-airport/` | **NEW** | — |
| cheap car rental Georgia | `/car-rental/economy/` | **NEW** | economy car rental, budget car hire |
| SUV rental Georgia | `/car-rental/suv/` | **NEW** | crossover rental |
| 4x4 rental Georgia | `/car-rental/4x4/` | **NEW** | off-road rental, Tusheti/Ushguli vehicle |
| minivan rental Georgia | `/car-rental/minivan/` | **NEW** | 7 seater, family car rental |
| {model} rental Georgia | `/fleet/{car}/` | exists | model specs, daily rate |
| rental fleet / all cars | `/fleet/` | exists | catalogue |

**Held back (no source data — see Open Questions):** `car rental Georgia unlimited mileage`, `car rental Georgia no deposit`, `one way car rental Georgia`. These must not be targeted until `content/settings/booking.yml` (or terms) states the actual policy. Targeting them without data would mean inventing commercial terms.

## Cluster 2 — Trip planning (tool intent)

| Primary query | Page | Status |
|---|---|---|
| Georgia trip planner / Georgia road trip planner | `/trip-planner/` (+ `/map/` as the app) | **NEW landing, existing app** |
| Georgia self drive itinerary | `/trip-planner/` | NEW |
| plan a trip to Georgia | `/trip-planner/` | NEW |

## Cluster 3 — Itineraries (informational → tool)

| Primary query | Page | Status |
|---|---|---|
| Georgia itinerary | `/itineraries/` | **NEW hub** |
| Georgia itinerary 3 days | `/itineraries/georgia-3-days/` | NEW (gated on data) |
| Georgia itinerary 5 days | `/itineraries/georgia-5-days/` | NEW (gated) |
| Georgia itinerary 7 days | `/itineraries/georgia-7-days/` | NEW (gated) |
| Georgia itinerary 10 days | `/itineraries/georgia-10-days/` | NEW (gated) |
| Georgia itinerary 14 days | `/itineraries/georgia-14-days/` | NEW (gated) |

## Cluster 4 — Road trips (route intent)

| Primary query | Page | Status |
|---|---|---|
| Georgia road trip (head) | `/tours/` → repositioned as routes hub | exists, needs sitemap + title |
| Tbilisi to Kazbegi road trip | `/routes/{kazbegi route}/` | exists — verify slug |
| Tbilisi to Kakheti road trip | `/routes/{kakheti route}/` | exists |
| Tbilisi to Batumi road trip | `/routes/{batumi route}/` | exists |
| driving in Georgia country | `/blog/` post or `/trip-planner/` section | decide in Release C |
| best car for Georgia road trip | `/car-rental/suv/` + route→vehicle links | cross-cluster |

## Cluster 5 — Places (discovery)

| Primary query | Page |
|---|---|
| things to do in Georgia / places to visit in Georgia | `/map/` + `/attractions/` listing on `/map/` |
| {place} Georgia (×257) | `/attractions/{slug}/` |
| {region} Georgia attractions | `/regions/{key}/` |

---

## Cannibalisation register

| Overlap | Decision |
|---|---|
| `/fleet/` vs `/car-rental/` | **KEEP BOTH.** `/fleet/` = catalogue (browse inventory). `/car-rental/` = intent hub (terms, categories, locations, booking). `/car-rental/` targets the head term; `/fleet/` retitled to "Rental Cars in Georgia — Economy, SUV & 4x4" and links up to the hub. |
| `/map/` vs `/trip-planner/` | **`/trip-planner/` is canonical for the query**; `/map/` remains the interactive application page and links to it. If both cannot be justified after Release C, `/map/` gets `canonical → /trip-planner/`. Decision recorded, not yet executed. |
| `/tours/` vs `/itineraries/` | `/tours/` = **ready-made operator routes** (product). `/itineraries/` = **duration-based travel planning** (informational). Different intent, must stay differentiated in copy or merge. |
| `/car-rental/4x4/` vs `/car-rental/suv/` | Distinct: 4x4 = genuine off-road need (Tusheti, Ushguli, Khevsureti); SUV = comfort/clearance on paved+gravel. Copy must state the difference explicitly. |
| Attraction pages vs region pages | Region = navigational list; attraction = the guide. No overlap. |

## Anti-patterns explicitly avoided

- No city page unless the business genuinely serves it **and** the page carries different information (routes from there, pickup logistics, distances).
- No `{keyword} + {city}` matrix generation.
- No FAQ-schema-for-rich-results strategy.
- No auto-generated itinerary variants beyond the 5 curated bands.
- No keyword-stuffed alt text or hidden SEO text.
