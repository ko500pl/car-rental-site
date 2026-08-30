# RentUp.ge — Content Strategy

**Compiled:** 2026-08-29 · **Scope:** what to build, in what order, in which languages, and how to know it worked.

Companion documents — read in this order:
`SEO_AUDIT.md` (state) → `SEO_URL_MAP.md` (which URLs may exist) → `SEO_KEYWORD_MAP.md` (one intent per page) →
`KEYWORD_CLUSTERS.md` (the query space) → **this file** (what content to make) → `SEO_IMPLEMENTATION_PLAN.md` (how to ship it).

Where this file proposes something the URL map currently forbids, it is flagged **REVISES URL MAP** with the
gate that makes it not a doorway page. Nothing here overrides `SEO_VALIDATION.md`'s `seo_quality_ok()` gate.

> **Evidence note.** Every count in §1 was measured directly from `content/*.yml` and the built `dist/` tree on
> 2026-08-29 by parsing the files, not read from a prior document. Where an earlier doc and the data disagree,
> the measurement wins and the discrepancy is noted. **No keyword-volume tool and no Search Console access were
> available.** Priority in §6 is therefore ranked on intent value × data defensibility × effort — never on an
> invented traffic number. Every "expected impact" is a directional judgement, not a forecast.

---

## 1. Content audit — what exists today

### 1.1 Published inventory (measured)

`dist/` contains **2 137 `index.html` files**; **2 100** are indexable and in the sitemap (350 unique pages × 6 languages).
The sitemap is an index of 8 children.

| Content type | URL pattern | Pages / language | × 6 langs | In sitemap | Source of truth |
|---|---|---|---|---|---|
| Home | `/` | 1 | 6 | ✅ | `pages/index.yml` |
| Attraction guide | `/attractions/{slug}/` | **257** | 1 542 | ✅ | `attractions/*.yml` |
| Road trip route | `/routes/{slug}/` | **32** | 192 | ✅ | `routes/*.yml` |
| Vehicle | `/fleet/{car}/` | **17** | 102 | ✅ | `cars/*.yml` |
| Region hub | `/regions/{key}/` | **11** | 66 | ✅ | `regions/*.yml` |
| Car-rental hub | `/car-rental/` | 1 | 6 | ✅ | `cars`, `categories.yml`, `rental_policy.yml` |
| Rental location | `/car-rental/{city\|airport}/` | **6** | 36 | ✅ | `places.yml`, `rental_policy.yml` |
| Rental category | `/car-rental/{economy,suv,4x4,minivan}/` | **4** | 24 | ✅ | `categories.yml` + `cars` |
| Itinerary | `/itineraries/georgia-{3,5,7,10,14}-days/` | **5** | 30 | ✅ | `itineraries/*.yml` |
| Itineraries hub | `/itineraries/` | 1 | 6 | ✅ | derived |
| Trip-planner landing | `/trip-planner/` | 1 | 6 | ✅ | derived |
| Planner app | `/map/` | 1 | 6 | ✅ | derived |
| Routes hub | `/tours/` | 1 | 6 | ✅ | `routes/*.yml` |
| Fleet catalogue | `/fleet/` | 1 | 6 | ✅ | `cars/*.yml` |
| Blog | `/blog/` + 4 posts | 5 | 24 (index counted once/lang + 4) | ✅ | `posts/*.yml` |
| Static | `/about/ /contact/ /terms/ /faq/ /community/ /fleet-management-software/` | 6 | 36 | ✅ | `pages/*.yml` |
| Utility (noindex) | `/trip/ /account/ /app/ /admin/ /pricing/ /planner/ /business-card/` | 7 | — | ❌ correct | — |

Sitemap children as built: `attractions.xml` 1 542 · `routes.xml` 192 · `cars.xml` 102 · `car-rental.xml` 66 ·
`regions.xml` 66 · `core.xml` 66 · `itineraries.xml` 42 · `blog.xml` 24.

### 1.2 Language coverage — complete parity, measured

There is **no language gap in existing content**. Every record carries all six languages:

| Type | ka | en | ru | fa | he | ar | Mean body length (EN → HE) |
|---|---|---|---|---|---|---|---|
| Attractions (257) | 257 | 257 | 257 | 257 | 257 | 257 | 1 487 → 1 085 chars (`body`), plus `short` + `tip` on all 257 × 6 |
| Routes (32) | 32 | 32 | 32 | 32 | 32 | 32 | `body` + `plan` + `tips` complete in all six |
| Cars (17) | 17 | 17 | 17 | 17 | 17 | 17 | full `body` in all six |
| Regions (11) | 11 | 11 | 11 | 11 | 11 | 11 | 1 538 → 1 222 chars |
| Blog posts (4) | 4 | 4 | 4 | 4 | 4 | 4 | 4 928–6 472 chars per post per language |
| FAQ | 30 Q&A | 30 | 30 | 30 | 30 | 30 | — |

**This is unusual and it is the single largest sunk asset in the project.** Roughly 1.9 million characters of
human-quality prose across six languages already exists. Any strategy that starts by writing more prose is
ignoring what is already paid for.

### 1.3 Data completeness on the 257 attractions — 100 % on every SEO-relevant field

| Field | Coverage | Distribution (measured) |
|---|---|---|
| `road` | **257 / 257** | paved 149 · mostly_paved 71 · gravel 20 · 4x4_only 17 |
| `car_category` | **257 / 257** | economy 175 · suv 59 · offroad 23 |
| `best_season` | **257 / 257** | all 153 · may–october 67 · june–september 34 · december–march 2 · april–october 1 |
| `drive_time_tbilisi` | **257 / 257** | ≤1 h 40 · 1–2 h 46 · 2–3 h 34 · 3–4 h 36 · >4 h 101 |
| `distance_tbilisi_km` | 257 / 257 | — |
| `visit_hours`, `entry_fee`, `open_year_round` | 257 / 257 | free entry 196 · open all year 209 · seasonally closed 48 |
| `region`, `type`, `lat/lon`, `elevation`, `unesco` | 257 / 257 | 11 regions · 16 types · 6 UNESCO · 40 places ≥1 500 m, 18 ≥2 000 m |
| `nearby[]` | 257 / 257 | 849 edges, mean 3.3 per place |
| `image` / `gallery` | 250 / 248 | 719 gallery photos with author + licence + source |
| `rating` | 248 / 257 | — |

Routes carry `days`, `nights`, `distance_km`, `drive_time_total`, `car_category`, `best_season`, `difficulty`,
`purpose`, `waypoints[]` at **32 / 32**. Cars carry `clearance`, `fuel_100km`, `seats`, `luggage`, and three
price bands + `deposit` at **17 / 17**.

### 1.4 Structural gaps found in the build

| # | Gap | Evidence | Severity |
|---|---|---|---|
| G1 | **No `/attractions/` hub.** 257 pages, no index. | `dist/attractions/index.html` does not exist | High — 1 542 URLs with no topical parent |
| G2 | **No `/regions/` hub.** 11 region pages, no index. | `dist/regions/index.html` absent | Medium |
| G3 | **No `/routes/` hub.** `/tours/` is the de-facto hub, titled `Standard tours \| RentUp`. | live title | Medium |
| G4 | **132 of 257 attractions appear in no route.** Only 125 unique places are waypoints on the 32 routes. | reverse index of `route.waypoints[]` | Medium — half the place corpus is weakly linked |
| G5 | **Zero images on routes (0/32) and cars (0/17).** All photography sits on attractions. | `image: ''` on every route and car file | High for CTR and for `/fleet/` conversion |
| G6 | `business` (3 cars) and `van` (2 cars) categories have data but no `/car-rental/` page. | `dist/car-rental/` has 4 category dirs | Low–Medium |
| G7 | Polylines on only **6 of 32** routes. | `polyline` field | Low (map UX, not SEO) |

### 1.5 Content-integrity defects — these block the strategy and come first

These are not SEO nits. They are places where the site currently publishes **contradictory commercial facts about
itself**, which damages trust signals, AI answer quality, and — if a customer relies on them — the business.

| # | Defect | Evidence | Why it blocks content work |
|---|---|---|---|
| **I1** | **`content/settings/rental_policy.yml` is labelled `STATUS: PROPOSED DEFAULTS drafted for the owner's approval (2026-08-29)` — and its values are already published live** on `/car-rental/` in six languages (min age 21, unlimited mileage, deposit handling, airport fees 30/60/60 ₾, one-way 100 ₾). | file header vs `dist/car-rental/index.html` | Every new commercial page multiplies an unapproved claim by 6 languages. **Owner sign-off is a prerequisite, not a follow-up.** |
| **I2** | **`/faq/` contradicts `rental_policy.yml` on at least four material terms.** FAQ: "rate includes CDW insurance", excess 300–1 200 ₾, cross-border allowed with a 300 km/day cap, SCDW 25–45 ₾/day. Policy: `cdw_available: true, cdw_daily_gel: 25` (an **add-on**, not included), `excess_gel: 1000`, `cross_border.allowed: false`. | `content/pages/faq.yml` vs `content/settings/rental_policy.yml` | The FAQ is 30 Q&A × 6 languages = the largest commercial text asset on the site and it cannot be reused on money pages while it disagrees with the policy file. |
| **I3** | **`llms.txt` states a third, different set of facts**: fuel "Full to full" (policy: `same_to_same`), tiered minimum age 21/23/25 by category (policy: flat 21), cross-border to Armenia 150 ₾ / Turkey 250 ₾ (policy: prohibited), "full insurance coverage" (policy explicitly says *"Deliberately NOT claimed: full coverage, zero excess"*), "Founded: 2019", "average age 4 years". | `dist/llms.txt` | This file is what AI assistants read. It is currently the most authoritative-looking and least accurate surface on the site. |
| **I4** | `llms.txt` ships an unsubstituted template placeholder: `"{attractions} attractions across 11 regions"`. | `dist/llms.txt` | Trivial fix, visible to every crawler. |
| **I5** | **14 attraction `entry_fee` values are Georgian-script strings rendered on all six languages**, e.g. `მუზეუმი ~20 ₾, ციხე უფასო` on `gori-fortress-stalin-museum`, `ფუნიკულიორი ~6 ₾` on `mtatsminda-park`, `~20 ₾ + შატლი ~5 ₾` on `okatse-canyon`. | measured across `attractions/*.yml` | 14 × 5 non-Georgian languages = 70 pages showing untranslated text in a data field. |
| **I6** | Raw enum tokens leak into English prose: the SUV category page reads *"not the 4x4_only tracks beyond"*. | `dist/car-rental/suv/` copy path | Machine-generated seams visible to readers on a commercial page. |
| **I7** | 245 pages carry over-length titles after the RTL fix (per `SEO_VALIDATION.md` Release D). | prior release log | Non-blocking, tracked. |

**Rule for this programme: no new commercial page ships until I1–I3 are resolved by the owner and a single
source of truth is designated.** `rental_policy.yml` should be that source; `faq.yml` and `llms.txt` should be
generated from it or reconciled against it.

---

## 2. The two intents and the bridge between them

### 2.1 The two audiences, as the data serves them

| | **Intent R — rent a car** | **Intent T — plan a Georgia road trip** |
|---|---|---|
| Who | Already decided to rent. Comparing suppliers. | Deciding *whether* to go, *where*, and *how to get around*. Has not thought about a car yet. |
| Queries | `car rental tbilisi`, `аренда авто в грузии`, `tbilisi airport car rental`, `4x4 rental georgia` | `things to do in georgia`, `georgia itinerary 7 days`, `svaneti`, `tusheti`, `is ushguli worth it` |
| Pages today | 11 (`/car-rental/*`) + 18 (`/fleet/*`) = **29** | 257 + 32 + 11 + 5 + 3 hubs = **308** |
| SERP reality | Aggregators (Localrent, Myrentacar, Discover Cars, Rentalcars) plus 8+ established Georgian operators own page one. New domain, **not winnable inside 2 quarters.** | Fragmented: travel blogs (wander-lush.org is the dominant English authority), Tripadvisor threads, thin listicles. **Winnable — nobody has structured data.** |
| Commercial value per session | High, immediate | Low, delayed |

The site is currently **91 % travel content and 9 % commercial content**, competing for 100 % of its revenue
in the commercial 9 %. That is not a flaw. It is the correct shape *if and only if* the travel content
converts. Making it convert is what the rest of this document is about.

### 2.2 The bridge — the one question only RentUp can answer

A traveller reading about Ushguli does not think "I should rent a car." They think:

> *"Can I actually get there? What kind of car do I need? Is it open in October?"*

Every competitor answers with prose ("a 4x4 is recommended"). **RentUp answers with a structured field on all
257 places** — `road`, `car_category`, `best_season`, `drive_time_tbilisi` — and then hands the reader a car in
that exact category, with a real clearance figure and a real price.

Measured against the fleet: `clearance` ranges 135 mm (economy) to 235 mm (offroad), and 37 of 257 places sit
on `gravel` or `4x4_only` roads. That mapping is the product.

### 2.3 The funnel, as it exists and as it should exist

```
             ┌──────────────────────────── DISCOVER (Intent T) ─────────────────────────────┐
             │  /attractions/{257}   /regions/{11}   /routes/{32}   /itineraries/{5}        │
             │  Query: "things to do in Georgia", "Svaneti", "Georgia itinerary 7 days"     │
             └────────────────────────────────────┬────────────────────────────────────────┘
                                                  │  reader has picked a destination
                                                  ▼
             ┌────────────────────────── QUALIFY — THE BRIDGE ─────────────────────────────┐
             │  Query: "do I need a 4x4 in Georgia", "is the road to Ushguli paved",       │
             │         "can you drive to Tusheti", "day trips from Tbilisi by car",        │
             │         "is Kazbegi open in winter", "best time to visit Georgia"           │
             │                                                                             │
             │  DATA THAT ANSWERS IT (100 % coverage, already in YAML):                    │
             │    road · car_category · best_season · drive_time_tbilisi · elevation       │
             │                                                                             │
             │  PAGES THAT OWN THESE QUERIES TODAY:  ███ NONE ███                          │
             │  Currently expressed only as a per-page link on 257 attraction pages.       │
             └────────────────────────────────────┬────────────────────────────────────────┘
                                                  │  reader now knows they need a car,
                                                  │  and which category
                                                  ▼
             ┌──────────────────────────── CONVERT (Intent R) ──────────────────────────────┐
             │  /car-rental/{category}   /car-rental/{location}   /fleet/{car}   booking    │
             └──────────────────────────────────────────────────────────────────────────────┘
```

**The bridge tier is the entire opportunity, and it is empty.** Verified in `dist/`:

- All **257 / 257** attraction pages already link to the correct `/car-rental/{category}/`
  (economy 175, suv 59, 4x4 23). All **32 / 32** route pages link to their category. The *plumbing is done*.
- But **zero pages exist that the bridge queries can land on.** Measured in `dist/`: the phrase
  "day trips from Tbilisi" appears **0 times**, "do I need a 4x4" **0 times**, "best time to visit" **0 times**.
- Result: the site can only monetise a traveller who has *already found* a specific attraction page. It cannot
  capture the far larger population searching the qualifying question itself.

Closing the bridge is Q1 and Q2 of this programme. Everything else is secondary.

---

## 3. Topical authority map

Four pillars. Each pillar owns a head intent; each cluster is a template fed by measured data; each supporting
page exists only where the data clears a stated bar.

```
PILLAR 1 — CAR RENTAL IN GEORGIA                                    /car-rental/          [EXISTS]
│  head intent: "car rental Georgia" · difficulty Very High · long game, not a Q1 target
├── Locations       /car-rental/{tbilisi,tbilisi-airport,kutaisi,kutaisi-airport,batumi,batumi-airport}/   6  [EXISTS]
├── Categories      /car-rental/{economy,suv,4x4,minivan}/                                                 4  [EXISTS]
│                   /car-rental/business/                                                                  1  [NEW, gated]
├── Vehicles        /fleet/{car}/                                                                         17  [EXISTS]
└── Terms & trust   /terms/ /faq/ /contact/                                                                3  [EXISTS — see I2]

PILLAR 2 — DRIVING IN GEORGIA  ◄── THE BRIDGE                       /driving-in-georgia/   [NEW]
│  head intent: "driving in Georgia" / "do I need a 4x4 in Georgia" · difficulty Medium · uniquely defensible
├── 4x4 & gravel roads          /driving-in-georgia/4x4-and-gravel-roads/       37 places, 10 regions   [NEW]
├── Roads that close in winter  /driving-in-georgia/seasonal-road-closures/     48 seasonal places      [NEW]
├── Mountain passes & altitude  /driving-in-georgia/mountain-passes/            40 places ≥1 500 m      [NEW]
└── Which car for which road    /driving-in-georgia/choosing-a-car/  ── links straight into Pillar 1    [NEW]

PILLAR 3 — PLACES TO VISIT IN GEORGIA                               /attractions/          [NEW HUB — G1]
│  head intent: "places to visit in Georgia" · difficulty Medium–High · 257 pages currently orphaned
├── Day trips from Tbilisi      /attractions/day-trips-from-tbilisi/            86 places ≤2 h          [NEW]
├── Best time to visit          /attractions/best-time-to-visit/                month × region matrix   [NEW]
├── Free to visit               /attractions/free-to-visit/                     196 free places         [NEW]
├── Regions hub + 11 regions    /regions/ + /regions/{key}/                     1 new + 11 upgraded     [HUB NEW — G2]
└── Types (gated, ≥14 places)   /attractions/{monastery,town,fortress,nature,mountain,museum,lake}/  7  [NEW, Q3]

PILLAR 4 — GEORGIA ROAD TRIPS & ITINERARIES                         /routes/ + /itineraries/
│  head intent: "Georgia road trip" / "Georgia itinerary" · difficulty Medium
├── Routes hub                  /routes/  (retitle & recanonicalise /tours/)                            [NEW — G3]
├── Routes                      /routes/{slug}/                                 32                      [EXISTS]
├── Duration itineraries        /itineraries/georgia-{3,5,7,10,14}-days/        5                       [EXISTS]
├── Themed itineraries (gated)  /itineraries/{hiking,history,nature,culinary,culture}/  ≤5              [NEW, Q3]
└── Planner                     /trip-planner/ + /map/                                                  [EXISTS]
```

**Cross-pillar links (already generated, keep):** every attraction → its category page; every route → its
category page; every category → the routes and places that need it. Pillar 2 is the missing hub that gives
those 289 existing edges a destination to aggregate into.

---

## 4. Template-driven page types built on the unique asset

This is the heart of the programme. Each type below is a **single template rendered from YAML in six
languages** — not an article. Each carries an explicit quality bar; a page that fails its bar is rendered
`noindex` and kept out of the sitemap, per `SEO_VALIDATION.md § seo_quality_ok()`.

### Why competitors cannot copy these

| Competitor | What they have | What they lack |
|---|---|---|
| Localrent / Myrentacar / Discover Cars | Inventory, prices, reviews, brand authority | **No place data at all.** They are booking engines. They cannot tell you whether the road to Omalo is passable. |
| Georgian operators (carrentgeorgia.ge, gsscarrental.com, geodrive.info, …) | Local fleet, local knowledge in a salesperson's head | No structured place corpus. Their "destinations" pages are 3–5 hand-written paragraphs. |
| Travel blogs (wander-lush.org et al.) | Excellent prose, real trip reports, backlinks | **No car.** They can say "you need a 4x4" once, about one road. They cannot produce a filterable, complete, 257-row surface — and they have no reason to maintain one. |
| Google / AI answers | Everything | Nothing structured to cite for *"which Georgian attractions need a 4x4"*. This is a citable-gap; see `AI_VISIBILITY.md`. |

The moat is **completeness × structure × commercial relevance**: 257 places × 4 qualifying fields × a fleet
whose clearance figures make the recommendation actionable. A blogger could write one of these pages. Nobody
will maintain 257 rows of road-surface data they cannot monetise.

### 4.1 `/driving-in-georgia/` — pillar

- **Data:** road distribution across 257 places (paved 149 / mostly_paved 71 / gravel 20 / 4x4_only 17);
  car_category distribution (economy 175 / suv 59 / offroad 23); fleet clearance range 135–235 mm; the
  12 curated legs in `road_legs.yml`.
- **Content:** what each of the four road classes means in practice, how many places fall in each, which fleet
  clearance clears which class, region-by-region summary table, links down to the three clusters and across to
  `/car-rental/{category}/`.
- **Quality bar:** must render all four road classes with real counts, a region × road-class matrix covering
  all 11 regions, and ≥3 named worked examples drawn from real records. **Never state that a road is passable
  or impassable beyond what `attraction.road` and `road_legs.yml` say.**

### 4.2 `/driving-in-georgia/4x4-and-gravel-roads/` — cluster

- **Data:** the 37 places with `road ∈ {gravel, 4x4_only}`, spread across 10 regions —
  samegrelo-zemo-svaneti 8, kakheti 7, mtskheta-mtianeti 6, adjara 5, kvemo-kartli 3, guria 2,
  racha-lechkhumi 2, shida-kartli 2, imereti 1, samtskhe-javakheti 1. Each row carries drive time from
  Tbilisi, `best_season`, `open_year_round`, elevation, and required category.
- **Quality bar:** ≥25 rows, each with road class + drive time + season + linked attraction page; a season
  window per row; an explicit "what we do *not* know" line where `road_legs.yml` has no leg.
- **Why it wins:** this is the highest-intent bridge query in the entire corpus and the answer is 37 rows nobody
  else holds. It also routes directly to `/car-rental/4x4/`, the highest-margin category.

### 4.3 `/driving-in-georgia/seasonal-road-closures/` — cluster

- **Data:** 48 places with `open_year_round: false`; 34 with `best_season: june-september`;
  67 `may-october`; 2 `december-march` (ski). Cross-referenced with region and elevation.
- **Quality bar:** ≥30 places, each with its season window and region; a plain statement that seasons are
  typical windows from our own records, not a live road-status service.

### 4.4 `/driving-in-georgia/mountain-passes/` — cluster

- **Data:** 40 places at ≥1 500 m, 18 at ≥2 000 m, top at 2 850 m (Abano Pass); joined with `road` and
  `best_season`. `road_legs.yml` supplies four 4x4-only Svaneti/Ushguli legs with km and minutes.
- **Quality bar:** ≥15 places ≥1 500 m with elevation + road + season; ≥1 measured leg per named pass or the
  pass is omitted.

### 4.5 `/attractions/day-trips-from-tbilisi/` — cluster

- **Data:** **86 places within 2 h drive of Tbilisi** (40 within 1 h, 46 at 1–2 h); 120 within 3 h.
  76 of the 86 are `car_category: economy`. Each row: drive time, km, road class, entry fee, visit hours, season.
- **Quality bar:** ≥40 places with measured `drive_time_tbilisi` ≤ 2 h, each linking to its attraction page,
  each showing road class and required car category.
- **Deliberately NOT built: `/day-trips-from-kutaisi/` or `/day-trips-from-batumi/`.** Distance and drive
  time are recorded **from Tbilisi only**. `road_legs.yml` holds 12 curated legs, of which just 2 originate
  outside Tbilisi. Generating Kutaisi/Batumi variants would require inventing drive times — exactly the
  doorway pattern this strategy exists to avoid. Build them if and when the legs are measured, not before.

### 4.6 `/attractions/best-time-to-visit/` — cluster

- **Data:** `best_season` × `region` matrix, all 257 places. 153 places open in every season; 67 May–October;
  34 June–September. Region skews are real and interesting: Tbilisi 24/26 all-season, racha-lechkhumi only
  5/20 all-season.
- **Quality bar:** a full 11-region × 5-season-bucket matrix with real counts, and ≥3 named examples per bucket.
- **Deliberately NOT built: 12 monthly pages.** `best_season` has only 5 distinct values. Twelve monthly URLs
  would be near-identical renderings of a five-value field — a doorway set by any definition. One matrix page,
  built once, in six languages.

### 4.7 `/attractions/free-to-visit/` — cluster

- **Data:** 196 of 257 places have `entry_fee: free`; the paid remainder ranges ~2 ₾ to ~50 ₾.
- **Quality bar:** ≥100 rows, each with region + drive time + road class. **Blocked on defect I5** — 14
  `entry_fee` values are Georgian-script strings and must be normalised into structured fields
  (`entry_fee_gel`, `entry_fee_note.{lang}`) before this page is honest in five of six languages.

### 4.8 `/attractions/` and `/regions/` — hubs (fixes G1, G2)

- **Data:** the whole corpus, faceted statically by region (11), type (16), road class (4), car category (3),
  season (5), drive-time band (5).
- **Quality bar:** every one of the 257 places reachable in ≤2 clicks from the hub; every facet shows a real
  count; no facet combination gets its own URL (facets are rendered as in-page groupings and as links to the
  cluster pages in §4.2–4.7 — **never** as a `/attractions/{region}/{type}/{road}/` matrix).

### 4.9 `/car-rental/business/` — completes Pillar 1 (fixes G6)

- **Data:** 3 business-class cars with full specs and three price bands each.
- **Gate problem, stated honestly:** the standard category gate in `SEO_VALIDATION.md` requires ≥1 linked
  route, and **no route has `car_category: business`** (routes are suv 17 / economy 11 / offroad 4). The gate
  must be amended for this one type: substitute "≥1 linked route" with "≥100 linked `paved`-road places"
  (149 qualify) plus the standard "≥2 real vehicles with real prices + limitations text".
- **`/car-rental/van/` is NOT proposed.** 2 commercial vans, no consumer search intent, no route link, no
  place link. It would fail any honest bar.

### 4.10 What is explicitly rejected

| Rejected | Data reason |
|---|---|
| `/car-rental/{31 more cities}/` | `places.yml` has 37 cities, but `rental_policy.yml` defines delivery for only 6 places. The other 31 have no pickup, no fee, no route link — nothing but a name. Textbook doorway set. |
| `/attractions/{region}/{type}/` matrix | 11 × 16 = 176 cells; only **2 cells hold ≥8 places** and only 15 hold ≥5. 160+ near-empty pages. |
| Monthly "Georgia in {month}" pages | 5 distinct `best_season` values cannot support 12 pages. |
| `/itineraries/georgia-{1,2,4,6,8,9,11,12,13}-days/` | Route `days` values are 1–10 with a long tail; only the 5 curated bands compose into real day-by-day plans. |
| Per-attraction "hotels near X" / "restaurants near X" | No hotel or restaurant data in the repo beyond `hotels.yml`. Would require invention. |
| Any page requiring a fuel price, a road-status feed, or a live weather claim | Not in the data. Present as a formula the reader fills in, or omit. |

---

## 5. The blog — recommendation

### 5.1 What is actually there

4 posts, all `draft: false`, dated Jan–Jun 2026, all six languages, 4 123–6 472 characters each. Topics:
7 best road-trip routes · rental car vs taxi in Tbilisi · how to rent a car in Georgia · winter driving.
All four have `image: ''`.

Two observations that decide the recommendation:

1. **None of the four is a blog post.** Not one is dated in substance, newsworthy, or perishable. They are
   evergreen guides sitting under a dated URL scheme, in a section whose index is titled
   *"Blog — driving and car rental advice for Georgia"*. The format is wrong for the content that already exists.
2. **The true cost is 6×.** Measured: one post = roughly 5 400 characters × 6 languages ≈ 32 000 characters of
   publication-quality translated prose. A weekly cadence is ~1.7 million characters a year of translation.
   For a company with 17 cars, that is not a rational allocation.

### 5.2 Recommendation

> **Do not run a blog. Run a capped evergreen-guide track, and put the freed effort into §4 templates.**

Concretely:

- **Keep `/blog/` and the 4 posts.** They are indexed, good, and complete in six languages. Removing them
  destroys value for no gain. Drop the visible dates from the template so they do not decay in appearance.
- **Stop the dated-post format for new work.** New long-form goes under the topic pillar it belongs to
  (`/driving-in-georgia/…`), where it accumulates topical authority and links to a category page, rather than
  into a chronological archive that links nowhere commercial.
- **Cap prose at 12 pieces over 12 months** — one a month, not one a week. The constraint is deliberate:
  every prose page competes for the same translation budget as a §4 template that serves 257 places at once.
- **Two-gate admission.** A prose piece may be commissioned only if it clears **one** of:
  - **Gate A — countable:** it is anchored in a number measured from this repo's YAML (e.g. "37 of 257 places
    need gravel or 4x4 clearance"). The page then *cites its own data* and links to the template page that
    renders it.
  - **Gate B — unanswerable by template:** it answers a genuine traveller question for which **no field exists**
    (border formalities, fines and enforcement, parking in Tbilisi, what an insurance excess means in practice).
    These need prose because there is no data to render — and they are exactly where competitors are also weak.

  A piece that clears neither gate is not written. "Top 10 things to do in Georgia" clears neither: the
  `/attractions/` hub does it better, with data.

- **Ratio discipline:** for every prose piece shipped, at least one §4 template page must ship in the same
  month. Templates first; prose is the garnish, not the meal.

### 5.3 Editorial calendar — 12 pieces, 12 months, each with its supporting data

| # | Month | Working title | Gate | Supporting data (measured) | Publishes under | Langs |
|---|---|---|---|---|---|---|
| 1 | Q1 M1 | Do you need a 4x4 in Georgia? | A | 37/257 places on gravel or 4x4-only; 23 require `offroad`; fleet clearance 135–235 mm | `/driving-in-georgia/` | ka·en·ru |
| 2 | Q1 M2 | How far you can get from Tbilisi in a day | A | 40 places ≤1 h, 46 at 1–2 h, 34 at 2–3 h; 76 of the 86 ≤2 h need only economy | `/attractions/day-trips-from-tbilisi/` | ka·en·ru |
| 3 | Q1 M3 | Which Georgian roads close, and when | A | 48 places not open year-round; 34 June–Sep; 67 May–Oct; 2 Dec–Mar | `/driving-in-georgia/seasonal-road-closures/` | ka·en·ru |
| 4 | Q2 M4 | Economy, SUV or 4x4: matching the car to the road | A | clearance 135–235 mm across 17 cars vs `road` on 257 places; 175 places fine in economy | `/driving-in-georgia/choosing-a-car/` | **all 6** |
| 5 | Q2 M5 | What a Georgia road trip actually costs to drive | A | `fuel_100km` on 17 cars (7.5 l/100 km on the 5-Series) × `distance_km` on 32 routes (up to 1 050 km) + 3 price bands. **Present as a formula — no fuel price is in the repo; do not invent one.** | `/car-rental/` | **all 6** |
| 6 | Q2 M6 | Georgia's six UNESCO sites and how to drive to each | A | 6 `unesco: true` records: Gelati, Jvari, Kolkheti NP, Samtavro, Svetitskhoveli, Ushguli — each with drive time, road class, season | `/attractions/` | ka·en·ru |
| 7 | Q3 M7 | Driving to Svaneti: Mestia, and then Ushguli | A | `road_legs.yml`: tbilisi\|mestia 465 km / 8 h 30 mostly_paved; mestia\|ushguli 47 km / 2 h 30 **4x4-only, seasonal**; 26 Samegrelo–Zemo Svaneti places, 8 on rough road | `/driving-in-georgia/4x4-and-gravel-roads/` | ka·en·ru |
| 8 | Q3 M8 | Crossing a mountain pass in Georgia | A | 40 places ≥1 500 m, 18 ≥2 000 m, Abano at 2 850 m; Gombori and Jvari pass records | `/driving-in-georgia/mountain-passes/` | ka·en·ru |
| 9 | Q3 M9 | Georgia on no budget: 196 places that cost nothing | A | 196/257 `entry_fee: free`. **Blocked until I5 is fixed.** | `/attractions/free-to-visit/` | ka·en·ru |
| 10 | Q4 M10 | Traffic fines, police and what enforcement is like | **B** | No field exists. Requires a cited external legal source, or it is not published. | `/driving-in-georgia/` | ka·en·ru |
| 11 | Q4 M11 | What "excess" means when you scrape a wing mirror | **B** | Derived from the reconciled `rental_policy.yml` **after I1–I2 are signed off** — not before. | `/car-rental/` | **all 6** |
| 12 | Q4 M12 | Rtveli: driving Kakheti in harvest season | A | 32 Kakheti places (23 all-season, 5 May–Oct, 4 Jun–Sep); 7 on rough road; 3 wine routes | `/regions/kakheti/` | ka·en·ru |

Pieces 5, 6, 8 and 12 also make good candidates for outreach and citation — they are the only ones in the list
a third party would plausibly link to.

---

## 6. The six-language question

### 6.1 The honest position

Every existing page already exists in six languages. **There is nothing to cut** — deleting a language from
existing content would break the hreflang cluster, throw away paid-for work, and gain nothing. The six-language
question is therefore entirely about **new** content, and about **maintenance**.

### 6.2 The split, and why it falls where it does

The codebase already draws the right line without anyone naming it: **template strings live in `ui.yml` /
`travel.yml` / `seo_*.yml`; prose lives per-record.** That is exactly the cost boundary.

| Content class | Languages | Marginal translation cost | Reasoning |
|---|---|---|---|
| **Template-driven pages** (§4.1–4.9): tables, counts, place names, road classes, drive times | **All 6** | **Near zero.** The variable content is numbers and already-translated place names. Only the ~40 template strings per page type need translating — once, then reused across every row and every page of that type. | A 257-row table costs the same to localise as a 10-row one. There is no reason to withhold it. |
| **Commercial cluster** (`/car-rental/*`, `/fleet/*`, terms, FAQ, policy-derived copy) | **All 6** | Moderate, but this is the revenue surface | fa/he/ar visitors to Georgia *do* rent cars; an Arabic or Hebrew speaker landing on an English rental page converts worse. Never withhold a money page from a language the business serves. |
| **Long-form prose** (the §5.3 track) | **ka · en · ru**, with named exceptions | High — ~5 400 chars × 3 extra languages ≈ 16 000 chars per piece | See below. |
| **Structured data / schema / hreflang / titles** | All 6 | Mechanical | Already handled by `head_html()`. |

**Why ka · en · ru for prose:**

- **ka** — the domestic renting market. Georgians rent from Georgian companies; this is where brand and
  repeat business live. Non-negotiable for anything commercial. Lower value for pure travel discovery prose.
- **en** — the inbound lingua franca and the `x-default` target. Carries every visitor the site cannot serve
  in their own language.
- **ru** — the largest self-drive inbound cohort for Georgia by a wide margin (Russia, Armenia, Belarus,
  Kazakhstan), and the segment most likely to search rental terms in detail before arriving.

**Why fa · he · ar get templates but not prose (with exceptions):**

- The template pages carry the *decision-critical* information — road, car, season, drive time — with almost no
  prose in them. An Arabic-speaking visitor gets the answer they came for.
- Long-form opinion prose is the part that costs most and converts least. Three languages of it, per piece,
  for an audience segment measured in a handful of bookings, is not defensible before there is Search Console
  data proving demand.
- **Named exceptions — always all six:** pieces 4, 5 and 11 in §5.3. Those three are commercial-decision
  content (which car, what it costs, what the excess means), not travel colour. Withholding them from a
  language the business rents cars in is a conversion loss, not a saving.
- **Revisit trigger:** once Search Console shows ≥300 impressions/month from any of fa/he/ar on non-brand
  queries, promote that language into the prose tier. Decide with data, not with this document.

### 6.3 Multilingual maintenance debt to clear first

| Item | Scale | Note |
|---|---|---|
| I5 — 14 Georgian-script `entry_fee` values | 14 records × 5 non-ka languages = 70 affected pages | Restructure into `entry_fee_gel` + `entry_fee_note.{lang}`. Blocks §4.7. |
| I6 — raw enum tokens in English prose (`4x4_only`) | at least the SUV category page | Add a label map for road classes in all six languages. |
| I7 — 245 over-length titles, concentrated in RTL | tracked from Release D | Non-blocking, but every new page type adds six titles; fix the template, not the pages. |
| Adding a 7th language | — | **Do not.** Six is already at the edge of what one team can keep truthful, as I5–I7 demonstrate. |

---

## 7. Prioritised roadmap

Priority = **intent value × data defensibility ÷ effort**. Effort is in engineer-days for the template plus
translator-hours for the strings; "×6" is stated where the page count multiplies by language.

**Q0 — prerequisite, blocks everything commercial**

| # | Item | Effort | Why it is first |
|---|---|---|---|
| 0.1 | Owner sign-off on `rental_policy.yml`; designate it the single source of truth (I1) | 0 dev-days, 1 meeting | Every commercial page repeats these claims × 6 languages |
| 0.2 | Reconcile `faq.yml` and `llms.txt` against the signed-off policy (I2, I3); fix the `{attractions}` placeholder (I4) | 2 days | Site currently publishes three contradictory versions of its own terms |

### Roadmap table

| # | Page type | URL pattern | Pages / lang | × 6 | Data source | Quality bar | Effort | Expected impact | Quarter |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Driving-in-Georgia pillar** | `/driving-in-georgia/` | 1 | 6 | `road`, `car_category` on 257; `clearance` on 17 cars; `road_legs.yml` | 4 road classes with real counts + 11-region matrix + ≥3 worked examples | M (4 d) | **Highest.** Creates the bridge tier; head term "driving in Georgia" is Medium difficulty and uncontested by operators | **Q1** |
| 2 | **4x4 & gravel roads** | `/driving-in-georgia/4x4-and-gravel-roads/` | 1 | 6 | 37 places `road ∈ {gravel,4x4_only}` across 10 regions | ≥25 rows, each with road + drive time + season + linked page | S (2 d) | **Highest.** Highest-intent bridge query; routes to the top-margin `/car-rental/4x4/` | **Q1** |
| 3 | **Day trips from Tbilisi** | `/attractions/day-trips-from-tbilisi/` | 1 | 6 | 86 places ≤2 h (40 ≤1 h, 46 1–2 h); 120 ≤3 h | ≥40 places with measured drive time, road class and car category | S (2 d) | **High.** Large evergreen travel query; 76/86 land on `/car-rental/economy/` | **Q1** |
| 4 | **Attractions hub** (fixes G1) | `/attractions/` | 1 | 6 | all 257, faceted 6 ways | all 257 reachable in ≤2 clicks; every facet a real count; no facet URLs | S (2 d) | **High.** 1 542 URLs currently have no topical parent | **Q1** |
| 5 | **Routes hub** (fixes G3) | `/routes/` ← retitle/canonicalise `/tours/` | 1 | 6 | 32 routes | ItemList of all 32 with days, km, category, season | XS (1 d) | Medium. Head term "Georgia road trip"; also fixes a generic title | **Q1** |
| 6 | **Seasonal road closures** | `/driving-in-georgia/seasonal-road-closures/` | 1 | 6 | 48 seasonal places; 34 Jun–Sep; 67 May–Oct | ≥30 places with season window + region + explicit "typical, not live" caveat | S (2 d) | **High.** Strong autumn/winter seasonality; pairs with the existing winter post | **Q2** |
| 7 | **Choosing a car for the road** | `/driving-in-georgia/choosing-a-car/` | 1 | 6 | clearance 135–235 mm × `road` on 257 | every fleet category mapped to a road class with real counts; honest limitations | S (2 d) | **High.** The purest bridge page — informational query, transactional answer | **Q2** |
| 8 | **Regions hub** (fixes G2) + upgrade 11 region pages with a road-class table | `/regions/` + `/regions/{key}/` | 1 new + 11 upgraded | 6 + 66 | region × road × car_category × season matrices (measured per region) | hub: all 11 with counts; page: full road-class breakdown for that region | M (3 d) | Medium–High. Region pages are already strong (≈10 800 chars); this adds the unique layer | **Q2** |
| 9 | **Best time to visit** | `/attractions/best-time-to-visit/` | 1 | 6 | `best_season` × region, all 257 | full 11 × 5 matrix with real counts + ≥3 named examples per bucket | S (2 d) | Medium–High. Big evergreen query; explicitly replaces 12 monthly doorway pages | **Q2** |
| 10 | **Mountain passes** | `/driving-in-georgia/mountain-passes/` | 1 | 6 | 40 places ≥1 500 m, 18 ≥2 000 m, max 2 850 m; 4 measured 4x4 legs | ≥15 places with elevation + road + season; a measured leg per named pass | S (2 d) | Medium. Distinctive, linkable, feeds `/car-rental/4x4/` | **Q2** |
| 11 | **Business category** (fixes G6) | `/car-rental/business/` | 1 | 6 | 3 business cars, full specs + 3 price bands | amended gate: ≥2 cars with real prices + ≥100 linked paved places + limitations text | XS (1 d) | Medium. Completes the commercial cluster; corporate/airport-transfer intent | **Q2** |
| 12 | **Route photography + waypoint expansion** (fixes G5, G4) | `/routes/{slug}/`, `/fleet/{car}/` | 32 + 17 records | — | reuse the 719 licensed attraction photos via `waypoints[]`; extend waypoints to cover more of the 132 orphaned places | every route shows ≥3 stop photos; ≥180 of 257 places on ≥1 route | M (4 d) | **High for conversion, not for rankings.** 0/32 routes and 0/17 cars currently have an image | **Q2–Q3** |
| 13 | **Free-to-visit places** | `/attractions/free-to-visit/` | 1 | 6 | 196 places `entry_fee: free` | ≥100 rows with region + drive time + road. **Blocked on I5** | S (2 d) + 1 d data fix | Medium. Budget-travel query, high volume, low competition | **Q3** |
| 14 | **Type hubs, gated** — *REVISES URL MAP* | `/attractions/{type}/` for monastery 61, town 40, fortress 27, nature 24, mountain 22, museum 20, lake 14 | 7 | 42 | `type` field, gated at ≥14 places | **≥14 places, each with road + car category + season + drive time**; types below 14 (winery 7, archaeology 7, cave 6, beach 6, spa 8, waterfall 5, canyon 4, ski 3, theatre 3) are **not** built | M (3 d) | Medium. The URL map rejected `/attractions/{type}/` *for all types*; the ≥14 gate makes 7 of 16 genuinely substantive and leaves 9 unbuilt | **Q3** |
| 15 | **Themed itineraries, gated** | `/itineraries/{hiking,history,nature,culinary,culture}/` | ≤5 | ≤30 | `route.purpose`: hiking 5, history 5, nature 4, culinary 4, culture 3 | existing itinerary gate: ≥3 day rows each with destination + km + drive time, ≥5 linked attractions. Purposes with <3 routes (beach, classic, performance, wine, cycling, family, mountains) are **not** built | M (3 d) | Medium | **Q3** |
| 16 | **Prose track** — 12 pieces per §5.3 | topic pillars, not `/blog/` | 12 over 4 quarters | 36–72 | see §5.3 | two-gate admission (countable, or unanswerable by template) | 1–2 d each + translation | Low–Medium individually; the citation and link candidates are pieces 5, 6, 8, 12 | **Q1–Q4** |
| 17 | **Multilingual debt** — I5, I6, I7 | data + templates | — | — | — | 0 Georgian-script strings in non-ka output; 0 raw enum tokens in prose | S (2 d) | Enabling, not ranking. Unblocks #13 | **Q2** |

### 7.1 Net effect on the corpus

| | Today | After Q1 | After Q2 | After Q4 |
|---|---|---|---|---|
| Unique pages / language | 350 | 355 | 362 | 386 |
| Indexable URLs (× 6) | 2 100 | 2 130 | 2 172 | 2 316 |
| Bridge-tier pages | **0** | **4** | **7** | **7** |
| Commercial-intent pages | 29 | 29 | 30 | 30 |

The corpus grows about **10 %**. That is the point. This programme is not a volume play — it is 36 new pages
that make 2 100 existing ones convert.

---

## 8. Measurement

### 8.1 What to track, by content type

| Content type | Primary metric | Secondary | Health check |
|---|---|---|---|
| Bridge pages (§4.1–4.7) | **Bridge rate** = sessions that view a bridge page **and then** a `/car-rental/*` or `/fleet/*` page ÷ bridge-page sessions | Impressions on qualifying queries ("do i need a 4x4", "day trips from tbilisi", "roads closed winter georgia") | Not orphaned; ≥1 inbound link from each relevant cluster |
| Attractions (257) | Impressions on place-name queries; unique pages receiving ≥1 impression | Clicks; onward click to a route or car page | **Coverage ratio**: how many of the 257 have *any* impression. Below 60 % after 6 months = the hub or the internal graph is failing, not the content |
| Routes (32) / Itineraries (5+) | Impressions on "{place} road trip" and "georgia itinerary N days" | Planner opens (`/map/#tour=`) | Every route reachable from `/routes/` and ≥1 itinerary |
| Regions (11) | Impressions on "{region} georgia attractions" | Onward clicks to attractions | — |
| Car rental (11) + Fleet (18) | **Booking-form submissions attributed to organic** | Non-brand impressions; position on `car rental {city}` | Price and terms match `rental_policy.yml` — automated, not eyeballed |
| Prose (≤12) | **Referring domains earned** | Assisted sessions | If a piece earns 0 links and 0 assisted sessions in 6 months, do not commission another in its genre |
| All | Indexed ÷ submitted, per sitemap child | Core Web Vitals per template | `scripts/seo_audit.py dist` → 0 errors on every deploy |

**The one number that decides whether this strategy worked is the bridge rate.** Everything else is diagnostic.
If travel traffic grows and the bridge rate stays flat, the content is a travel blog that happens to be owned by
a rental company — and the programme has failed regardless of traffic.

### 8.2 Instrumentation prerequisites (none of this is currently verifiable)

1. Google Search Console verified, all six language paths, **sitemap children submitted individually** —
   without per-child submission the coverage gaps that hid `/map/` for months stay invisible.
2. Bing Webmaster Tools (material for ru and fa audiences).
3. Analytics with a **content-group dimension per page type** (attraction / route / region / itinerary /
   bridge / car-rental / fleet / prose). The bridge rate cannot be computed without it.
4. Booking-form submissions as a tracked event with landing-page and content-group attribution.
5. A monthly rank check on ~40 tracked terms across ka/en/ru. Manual is fine at this size.

### 8.3 What "working" looks like

All targets below are **provisional** — set from a baseline of essentially zero organic presence and **no
Search Console history**. Re-baseline at month 1 with real data and replace these numbers.

**Month 3 — the metric is indexation, not traffic**

- ≥90 % of the 2 100 submitted URLs indexed in ka/en/ru; ≥70 % in fa/he/ar.
- ≥40 % of the 257 attraction pages have received at least one impression.
- 4 bridge pages live, indexed, internally linked.
- Non-brand clicks: low double digits per month. **This is the expected result.** A new domain does not rank in
  90 days; a Q1 report showing meaningful traffic would more likely indicate a measurement error than success.
- 0 errors from `scripts/seo_audit.py`; 0 contradictions between `rental_policy.yml`, `/faq/` and `llms.txt`.
- Bridge rate measurable at all (instrumentation live) — the value itself is not yet meaningful.

**Month 6 — long-tail movement and the first bridge signal**

- ≥70 % of attraction pages with impressions; the long tail is where a new site first wins.
- Page-1 or strong page-2 positions on genuinely low-competition bridge terms: "do i need a 4x4 in georgia",
  "roads that close in winter georgia", "day trips from tbilisi by car" — in at least one of en/ru.
- **Bridge rate ≥ 8 %** of bridge-page sessions continuing to a rental page.
- Travel → commercial internal click-through visible in analytics from the attraction corpus at ≥3 %.
- First organic booking enquiries attributable to a travel or bridge landing page — measured in single digits,
  not dozens.
- Head terms ("car rental tbilisi", "аренда авто в грузии"): **still not ranking. Expected. Do not chase them.**

**Month 12 — defensible mid-tail authority, and revenue attribution**

- Top-10 in en and/or ru for a basket of 10–15 mid-tail bridge and itinerary terms.
- ≥85 % of attraction pages with impressions; ≥30 % with clicks.
- **Bridge rate ≥ 15 %**; organic-attributed booking enquiries a consistent monthly line item.
- ≥10 referring domains earned by the §5.3 prose track and the data pages (pieces 5, 6, 8, 12 are the
  candidates); the road-surface dataset cited by at least one third party or AI assistant.
- Head commercial terms: page-2 at best. **If the 12-month plan is judged on "car rental Georgia", it will be
  judged a failure. It should be judged on enquiries attributed to organic, and on the bridge rate.**

### 8.4 Kill criteria — when to stop, honestly

| Signal at 6 months | Interpretation | Action |
|---|---|---|
| Travel impressions grow, bridge rate < 3 % | The bridge pages are not persuading, or the CTAs are wrong | Rework the bridge CTAs before building any more content |
| Bridge pages get < 200 impressions/month combined | The qualifying queries are smaller than assumed | Re-price the whole travel strategy; shift effort to `/car-rental/*` and paid |
| A prose piece earns 0 links and 0 assisted sessions | Gate B was wrong for that genre | Stop commissioning that genre |
| < 60 % of attraction pages have impressions | Internal graph or hub problem, not a content problem | Fix `/attractions/`, the facets and the 132 route-orphans — do not write more |

---

## 9. Guardrails

1. **No page ships without a source field.** Every number on every generated page traces to a YAML key. If a
   claim has no key, it is not made — even if it is probably true.
2. **The quality bar is enforced in code**, via `seo_quality_ok()`. A page below its bar renders `noindex` and
   stays out of the sitemap. It is not "published and improved later".
3. **Templates before prose, always.** One template serves 257 places in six languages. One article serves one
   query in three. When the two compete for the same week, the template wins.
4. **No facet-matrix URLs.** Facets are in-page groupings and links to the seven curated cluster pages. There is
   no `/attractions/{region}/{type}/{road}/`.
5. **Road claims never exceed the data.** `road` and `road_legs.yml` say what they say. The site does not tell
   anyone a road is safe, open, or passable today.
6. **Commercial terms have exactly one source.** After Q0 that is `rental_policy.yml`. `/faq/`, `llms.txt`,
   `/terms/` and every `/car-rental/*` page derive from it or are reconciled against it — never restate it
   independently.
7. **Six languages for templates, three for prose**, with the three named commercial exceptions in §6.2.
   Revisit only when Search Console justifies it.
