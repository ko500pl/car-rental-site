# RentUp.ge — Internal Linking Review (measured)

**Date:** 2026-08-29 · **Corpus:** `dist/` as built (2,140 HTML files) · **Primary tree:** English (`dist/` root, excluding `/ka/ /ru/ /fa/ /he/ /ar/`) · **Confirmation tree:** `/ka/`

This document is an **audit of the shipped HTML**, not of the design. `docs/seo/SEO_INTERNAL_LINKING.md` describes the intended graph; everything below is the graph that actually renders. Where the two disagree, the measurement wins.

---

## 1. Method

Every number here comes from parsing the built HTML, not from reading `build.py`.

| Step | What was done |
|---|---|
| Node set | Every `*.html` under `dist/` except `assets/`, `data/`, `sitemaps/`. `dist/x/y/index.html` → `/x/y/`. |
| Link extraction | BeautifulSoup/lxml over each file. `mailto:`, `tel:`, `#`, `wa.me`, and off-site hosts dropped. Relative hrefs resolved against the page URL. |
| **Boilerplate split** | `header.site-head` and `footer.site-foot` → **nav**; `nav.crumbs` → **breadcrumb**; everything remaining inside `<main>` after removing `a.skip`, `.booking-dialog`, `<script>`, `<noscript>`, `<template>` → **in-content**. |
| Metrics | In-content in/out degree (deduplicated per `src→tgt` pair), BFS click depth from `/`, PageRank (d=0.85, 100 iterations, dangling mass redistributed uniformly) computed twice — once on all links, once on in-content links only. |
| Simulation | The proposed rules were applied to the *real* measured graph and PageRank re-run, so the "after" column is a computed number, not an estimate. |

Analysis scripts were throwaway and written under `/tmp`; no repository file other than this document was created or modified.

**Definition used throughout:** *in-content inbound links* = distinct source pages that link to a target from inside `<main>`. This is the only number that carries topical signal; the 19.6 header/footer links every page emits are identical on all 2,140 pages and carry none.

---

## 2. The graph at a glance

### Whole site (all 6 languages)

| Measure | Value |
|---|---|
| Pages (nodes) | **2,140** |
| In-content links (edges) | **27,890** |
| Header/footer links | 42,260 |
| Breadcrumb links | 5,670 |
| Total anchors | 75,820 |
| Boilerplate share of all internal anchors | **63.2%** |

### English tree

| Measure | Value |
|---|---|
| Nodes | **360** (350 indexable, 10 `noindex`) |
| In-content edges (raw anchors) | **4,672** |
| In-content edges (unique `src→tgt` pairs) | **3,160** |
| — of which duplicate anchors to the same target on the same page | 1,512 (32.4%) |
| Header/footer edges | 7,060 (19.6 per page, identical everywhere) |
| Breadcrumb edges | 945 |
| Broken internal in-content links | **0** |
| Mean in-content out-degree | 13.0 raw / 8.8 unique |
| Median in-content **inbound** (indexable pages) | **5** |

### Node census by template (English)

| Template | Pages | Mean in-content inbound | Median | Min | Max | Zero |
|---|---:|---:|---:|---:|---:|---:|
| attraction | 257 | 5.6 | 4 | 1 | 20 | 0 |
| route | 32 | 9.8 | 10 | 6 | 17 | 0 |
| car (`/fleet/{car}/`) | 17 | 2.2 | 2 | 1 | 4 | 0 |
| region | 11 | 23.4 | 23 | 18 | 32 | 0 |
| **rental-location** (`/car-rental/{place}/`) | 6 | **1.0** | 1 | 1 | 1 | 0 |
| itinerary | 5 | 3.0 | 3 | 2 | 4 | 0 |
| **rental-category** | 4 | 78.0 | 58 | **1** | 195 | 0 |
| blog-post | 4 | 1.0 | 1 | 1 | 1 | 0 |
| **rental-hub** (`/car-rental/`) | 1 | **8** | — | — | — | 0 |
| fleet-hub (`/fleet/`) | 1 | 326 | — | — | — | 0 |
| `/contact/` | 1 | **334** | — | — | — | 0 |
| planner (`/map/`, `/planner/`, `/trip-planner/`) | 3 | 14.7 | 2 | 0 | 42 | 1 |
| home | 1 | 1 | — | — | — | 0 |
| other static | 21 | — | — | 0 | 9 | 7 |

Two facts jump out of that table and drive most of this review:

1. `/contact/` receives **334** in-content inbound links — more than any commercial page, and more than the entire `/car-rental/` cluster combined (11 pages, 328 inbound between them, 296 of which land on two category pages).
2. All six `/car-rental/{place}/` pages have exactly **one** in-content inbound link each — the card grid on `/car-rental/`. Nothing else on 360 pages points at a pickup location.

---

## 3. Orphans, nav-only pages, dead ends

| Class | English | `/ka/` |
|---|---:|---:|
| Pages with **0** in-content inbound links | 9 | 6 |
| — of which **indexable** | **0** | **0** |
| Reachable only via header/footer | 1 (`/business-card/`, `noindex`) | 1 (`/ka/business-card/`, `noindex`) |
| Unreachable by any link at all | 8 | 5 |
| Dead ends (0 in-content outbound) | 6 | 6 |

**There are no indexable orphans.** Every one of the 350 indexable English pages has at least one contextual inbound link. The nine content-orphans are all `noindex`: `/404.html`, `/account/`, `/admin/`, `/admin/bookings.html`, `/admin/cms.html`, `/app/`, `/business-card/`, `/planner/`, `/pricing/`, `/trip/`. That is correct behaviour, not a defect — these are app surfaces and legal/utility pages that are deliberately excluded, and design-doc Rule 6 ("no link to a `noindex` page from indexable content") is being honoured.

Dead ends: `/account/`, `/admin/bookings.html`, `/app/`, `/planner/`, `/pricing/` (all `noindex`) and **`/contact/`** — which is indexable, absorbs 334 in-content links, and emits zero. It is a perfect PageRank sink.

**The real problem is not orphans, it is near-orphans.** Of 350 indexable English pages:

| In-content inbound ≤ | Pages | Share |
|---|---:|---:|
| 1 | 28 | 8.0% |
| 2 | 81 | 23.1% |
| 3 | 123 | 35.1% |
| 5 | 198 | 56.6% |

---

## 4. Click depth from `/`

BFS over all links (header/footer included), English tree:

| Depth | Pages | Cumulative |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 20 | 21 |
| 2 | 84 | 105 |
| 3 | 132 | 237 |
| 4 | 88 | 325 |
| 5 | 26 | 351 |
| unreached | 9 | 360 |

Content-only BFS reaches 345/360 with an almost identical shape `{0:1, 1:17, 2:81, 3:132, 4:88, 5:26}` — i.e. **the header contributes almost nothing to reachability**; it saves exactly six pages one click each. It is 7,060 anchors of pure dilution.

### Depth by template (all links)

| Template | 1 | 2 | 3 | 4 | 5 | unreached |
|---|---:|---:|---:|---:|---:|---:|
| attraction | | 24 | 125 | 82 | 26 | |
| route | 4 | 28 | | | | |
| car | 3 | 14 | | | | |
| **region** | | | **5** | **6** | | |
| rental-location | | 6 | | | | |
| rental-category | | 4 | | | | |
| itinerary | | 3 | 2 | | | |
| blog-post | | 4 | | | | |
| rental-hub | 1 | | | | | |
| fleet-hub | 1 | | | | | |
| tours-hub / itineraries-hub | 1 | 1 | | | | |
| planner (`/map/`, `/trip-planner/`) | 2 | | | | 1 | |

Findings:

- **108 of 257 attraction pages (42%) sit at depth 4–5.** They are reachable only by walking `home → route → attraction → nearby → nearby`. There is no `/attractions/` index page in `dist/` (nor `/routes/` nor `/regions/`) — `attractions.xml`, `routes.xml` and `regions.xml` exist in `dist/sitemaps/` but the corresponding HTML hubs do not.
- **All 11 region pages are at depth 3–4**, despite being the second-best-linked template on the site (mean 23.4 inbound). They are well-linked *upward from* their attractions and never linked *down to* from anything above them. A region hub is missing.
- `/map/` emits exactly **one** in-content link (to `/fleet/`). The design doc specifies "planner → routes / attractions / car rental: static crawlable link blocks" — that block does not exist in the HTML. The map's 257 places are JS-rendered and contribute zero crawlable edges.

---

## 5. The 20 pages with the fewest in-content inbound links

Indexable pages only, ascending. The commercial rows are the story.

| # | URL | Template | In-content inbound | Depth | PageRank (content) |
|---:|---|---|---:|---:|---:|
| 1 | `/car-rental/tbilisi/` | rental-location | 1 | 2 | 0.00073 |
| 2 | `/car-rental/tbilisi-airport/` | rental-location | 1 | 2 | 0.00073 |
| 3 | `/car-rental/kutaisi/` | rental-location | 1 | 2 | 0.00073 |
| 4 | `/car-rental/kutaisi-airport/` | rental-location | 1 | 2 | 0.00073 |
| 5 | `/car-rental/batumi/` | rental-location | 1 | 2 | 0.00073 |
| 6 | `/car-rental/batumi-airport/` | rental-location | 1 | 2 | 0.00073 |
| 7 | `/car-rental/minivan/` | rental-category | 1 | 2 | 0.00073 |
| 8 | `/fleet/bmw-5-series/` | car | 1 | 2 | 0.00549 |
| 9 | `/fleet/ford-transit/` | car | 1 | 2 | 0.00549 |
| 10 | `/fleet/mercedes-benz-e-class/` | car | 1 | 2 | 0.00549 |
| 11 | `/fleet/mercedes-benz-sprinter/` | car | 1 | 2 | 0.00549 |
| 12 | `/fleet/toyota-camry/` | car | 1 | 2 | 0.00549 |
| 13 | `/blog/avtomobilit-mogzauroba-saqartveloshi/` | blog-post | 1 | 2 | 0.00097 |
| 14 | `/blog/manqanis-daqiraveba-tu-taqsi/` | blog-post | 1 | 2 | 0.00097 |
| 15 | `/blog/rogor-viqiravot-manqana-saqartveloshi/` | blog-post | 1 | 2 | 0.00097 |
| 16 | `/blog/zamtris-mgzavroba-saqartveloshi/` | blog-post | 1 | 2 | 0.00097 |
| 17 | `/attractions/lisi-lake/` | attraction | 1 | 5 | 0.00084 |
| 18 | `/attractions/minda-fortress/` | attraction | 1 | 5 | 0.00082 |
| 19 | `/attractions/tobavarchkhili-lakes/` | attraction | 1 | 5 | 0.00082 |
| 20 | `/attractions/tsalenjikha-cathedral/` | attraction | 1 | 5 | 0.00082 |

Also on 1 inbound: `/attractions/mravaldzali/`, `/attractions/pitareti-monastery/`, `/attractions/ateni-valley-wine-cellars/`, `/attractions/gori-war-museum/`, `/attractions/tianeti/`, `/attractions/zarzma-monastery/` (28 pages at ≤1 in total). `/` itself shows 1, which is an artefact of the logo living in the header — not a defect.

**Seven of the twenty weakest pages on the site are money pages.** The five `car` pages at 1 inbound are precisely the `business` (BMW 5 Series, E-Class, Camry) and `van` (Sprinter, Transit) vehicles — the two fleet categories with **no `/car-rental/{category}/` page at all**, so they sit outside the category cluster entirely and are reachable only from `/fleet/`.

---

## 6. Anchor text: quality and over-optimisation

| Measure | English | `/ka/` |
|---|---:|---:|
| In-content anchors | 4,639 | 4,638 |
| Distinct anchor strings | 396 | 398 |
| Anchors per distinct string | 11.7 | 11.7 |
| **Empty anchors** (image-only `<a class="card-img">`) | **1,306 (28.2%)** | 1,306 (28.2%) |
| Literal generic phrases ("Details", etc.) | 24 (0.5%) | 24 (0.5%) |
| "read more" / "click here" / "see details" | **0** | **0** |

### The good news

The design doc's Rule 2 is genuinely upheld. There is not one "read more" or "click here" in 27,890 in-content links across the whole site. Nearly every anchor is a real entity name — "Narikala Fortress", "Bagrati Cathedral and central Kutaisi", "Grand Classic Georgia Tour".

### Problem A — 1,306 empty anchors (28% of all in-content links)

Every card in the nearby-places, route-stops and region grids renders **two** anchors to the same URL: an image-only `<a class="card-img">` with no text, followed by a text link. Measured sources:

| Source template → target | Empty anchors |
|---|---:|
| attraction → attraction (nearby cards) | 845 |
| region → attraction (region grid) | 250 |
| route → attraction (stop cards) | 211 |

This is 32.4% duplicate `src→tgt` edges. Google's first-link-counts behaviour means the *empty* anchor is the one that gets attributed on many of these pairs, throwing away the descriptive text that follows. It is a pure loss with a one-line fix.

### Problem B — templated commercial anchors repeated at scale

| Anchor | Occurrences | Target |
|---|---:|---|
| `Economy class — Price from 75 ₾/day` | **186** | `/car-rental/economy/` |
| `Crossover / SUV — Price from 130 ₾/day` | **76** | `/car-rental/suv/` |
| `Off-road 4x4 — Price from 240 ₾/day` | **27** | `/car-rental/4x4/` |
| `Contact` | **324** | `/contact/` |
| `Fleet` | **324** | `/fleet/` |

`/car-rental/economy/` has 195 in-content inbound links carrying **4 distinct anchor strings**, 186 of them character-identical. That is a classic exact-match templated-anchor footprint. It is not deceptive — the price is true and generated from `specs.yml` — but the *uniformity* is the risk, and it is free to fix: the block already knows the attraction, the region and the road type, so the anchor can vary along a truthful axis ("Economy car for paved roads in Kakheti — from 75 ₾/day") without inventing anything.

### Problem C — 674 boilerplate CTA links living inside `<main>`

`render_attraction`, `render_route`, `render_region`, `render_car` and `render_rental_location` each append a "book a car" CTA section containing `/contact/` and `/fleet/` links. That is 674 of 4,672 in-content edges (14.4%) that are sitewide boilerplate wearing a contextual costume. They are the reason `/contact/` outranks every commercial page in the content-only PageRank.

---

## 7. Does PageRank reach the money pages?

Two PageRank runs on the real English graph (d=0.85, 100 iterations). "Commercial cluster" = `/car-rental/` + 6 locations + 4 categories + `/fleet/` + 17 cars = **29 pages, 8.1% of the tree**.

### Share of PageRank by template

| Template | Pages | All links | **In-content only** |
|---|---:|---:|---:|
| attraction | 257 | 15.9% | 42.8% |
| `/fleet/` | 1 | 5.7% | **10.8%** |
| **`/contact/`** | 1 | 5.7% | **10.5%** |
| car | 17 | 5.2% | 10.2% |
| route | 32 | 4.6% | 8.9% |
| rental-category | 4 | 1.3% | 5.5% |
| region | 11 | 1.3% | 5.1% |
| `/terms/` | 1 | 5.7% | 1.2% |
| `/faq/` | 1 | 5.7% | 1.0% |
| planner | 3 | 6.2% | 1.0% |
| itinerary | 5 | 0.3% | 0.6% |
| **rental-location** | 6 | 0.4% | **0.44%** |
| **`/car-rental/` hub** | 1 | 0.5% | **0.11%** |
| **Commercial cluster (29 pages)** | 29 | 13.0% | **26.7%** |

### Where the money pages actually rank (in-content PageRank, 1 = highest of 360)

| Page | Rank | Share |
|---|---:|---:|
| `/fleet/` | **1** | 10.76% |
| `/car-rental/economy/` | 3 | 3.47% |
| `/car-rental/suv/` | 4 | 1.44% |
| `/fleet/{car}/` × 17 | 8–26 | 10.19% total |
| `/car-rental/4x4/` | 29 | 0.49% |
| **`/car-rental/`** | **288** | 0.11% |
| **`/car-rental/kutaisi/`** | **348** | 0.073% |
| **`/car-rental/minivan/`** | **349** | 0.073% |
| **`/car-rental/tbilisi/`** | **351 of 360** | 0.073% |

**Verdict: half of the commercial cluster is fed, half is starving.** The `/fleet/` branch (fleet hub + 17 car pages) is healthy — 21% of all in-content PageRank between 18 pages. The `/car-rental/` branch is the opposite: the hub itself ranks **288th** and its six location pages occupy ranks **345–351 out of 360**, i.e. the bottom 2% of the site. `/car-rental/tbilisi/` — the single highest-commercial-intent URL on the domain — is the third-lowest-ranked indexable page in the tree.

The cause is structural, not accidental: `/car-rental/{place}/` pages **emit** 20 links each (to attractions, routes, categories, the hub) and **receive** one. They are pure donors.

The counterpart finding: **`/contact/` is the site's second-largest PageRank holder (10.5%)** — a `noindex`-worthy transactional page absorbing more equity than all six rental locations and the rental hub combined, by a factor of 20.

---

## 8. Relationship coverage — what the graph is missing

The design doc lists 17 intended edge types. Measured coverage in the English tree:

| Intended edge | Doc says | **Measured** | Verdict |
|---|---|---|---|
| attraction → nearby attractions | `nearby[]` | 849 edges, 257/257 pages | ✅ |
| attraction → region | `attraction.region` | 257/257 (100%) | ✅ |
| attraction → car category | `road` + `car_category` | 257/257 (100%) | ✅ |
| attraction → routes containing it | reverse index | **125/257 (49%)** | ⚠️ 132 attractions are on no route |
| route → attractions | `waypoints[]` | 216 edges, 32/32 | ✅ |
| route → car category | `route.car_category` | 32/32 (100%) | ✅ |
| route → planner | slug | 32/32 (100%) | ✅ |
| route → itinerary band | `route.days` | **10/32 (31%)** | ⚠️ |
| itinerary → routes | curated list | 5/5 (100%) | ✅ |
| itinerary → car rental | dominant category | 5/5 (100%) | ✅ |
| itinerary → planner | composed slugs | 5/5 (100%) | ✅ |
| category → vehicles | `car.category` | 3 each, 4/4 | ✅ |
| category → routes needing it | `route.car_category` | economy 8, suv 8, 4x4 4, **minivan 0** | ⚠️ |
| location → routes starting nearby | `places.yml` coords | 4–5 each, 6/6 | ✅ |
| location → car rental hub | static | 6/6 | ✅ |
| **planner → routes / attractions / car rental** | "static crawlable link blocks" | **`/map/` emits 1 in-content link total** | ❌ **not implemented** |
| **"Continue your road trip" (route → next route)** | listed as a reusable block | **0 of 32 routes link to any other route** | ❌ **not implemented** |

### Answers to the three specific questions asked

| Question | Measured answer |
|---|---|
| Do attraction pages link to the rental location nearest them? | **No — 0 of 257 (0%).** No attraction page links to any `/car-rental/{place}/`, nor to `/car-rental/` itself. All 257 have `lat`/`lon` in `content/attractions/*.yml`, so the nearest of Tbilisi / Kutaisi / Batumi is computable today: 117 → Tbilisi, 102 → Kutaisi, 38 → Batumi; median great-circle distance 49 km, 254 of 257 within 120 km. `_hav()` already exists at `build.py:2307`. |
| Do route pages link to the recommended car category **and to the cars in it**? | **Category: yes, 32/32. Cars: no, 0 of 32.** `seo_categories.yml` gives each category exactly 3 `car_slugs`; a route knows its `car_category`; the join is one dictionary lookup and is not being made. |
| Do itineraries link back to rental locations at their start point? | **No — 0 of 5.** Every itinerary in `content/itineraries/*.yml` carries `start: tbilisi` and `end: tbilisi`. `/car-rental/tbilisi/` exists. The link is one line and is absent. |

### Other unexploited joins in the existing data

| Join | Source of truth | Missing edges per language tree |
|---|---|---:|
| region → routes in that region | majority region of `route.waypoints[]` → all 11 regions have ≥1 route (4, 4, 4, 4, 3, 3, 2, 1, 1, 1, 5) | 32 |
| region → nearest rental location | region centroid vs `places.yml` | 11 |
| car → its `/car-rental/{category}/` page | `car.category` | 17 |
| rental-location → cars available there | `seo_car_rental.yml` `category_keys` → `car_slugs` | 18 |
| itinerary → attractions **back** (attraction → itinerary) | `itinerary.plan[].stops[]` — 68 forward edges exist, **0 reciprocated** | up to 68 |

---

## 9. Reciprocity

In-content, English, unique directed pairs: **3,138**, of which **1,518 reciprocated (48.4%)**.

| Edge type | Edges | Reciprocated |
|---|---:|---:|
| attraction ↔ region | 257 / 257 | **100%** |
| attraction ↔ route | 213 / 216 | **99–100%** |
| rental-category ↔ attraction | 24 | 100% |
| rental-category ↔ route | 20 | 100% |
| `/fleet/` ↔ car | 17 | 100% |
| attraction ↔ attraction (nearby) | 849 | 48% |
| route → rental-category | 32 | 62% |
| attraction → rental-category | 257 | **9%** |
| **itinerary → attraction** | 68 | **0%** |
| **rental-location → attraction** | 33 | **0%** |
| **rental-location → route** | 28 | **0%** |
| **rental-location → rental-category** | 14 | **0%** |
| tours-hub → route | 32 | 0% |
| attraction/route/car → `/contact/`, `/fleet/` | 674 | 0% |

Rule 4 of the design doc ("bidirectional where truthful") is honoured perfectly for the route↔attraction and region↔attraction axes and **not at all for anything touching `/car-rental/`**. Every single one of the 75 edges leaving a rental-location page is one-way. That is exactly why those pages rank 345–351.

The `nearby` reciprocity at 48% is expected and fine — `nearby[]` is a hand-curated asymmetric list (173 attractions list 3 neighbours, 82 list 4, 2 list 1) and forcing symmetry would be dishonest.

---

## 10. Cross-language leakage

| Measure | Value |
|---|---:|
| In-content links crossing a language boundary, all 2,140 pages | **47** |
| — on indexable pages | **0** |
| Breadcrumb links crossing a language boundary | **0** |
| Header/footer language-switcher links (expected) | 10,579 |

The 47 in-content cross-language links come from exactly 7 pages, all `noindex`:

- `/404.html` → 12 links to `/ka/…` (the Georgian fallback nav on the error page).
- The 6 `/{lang}/business-card/` pages → 5–6 links each, a deliberate language picker on a `noindex` vCard page.

**Design-doc Rule 5 ("language-local links only") holds across 27,890 in-content links with zero violations on indexable pages.** Every `/ka/` page links only to `/ka/` targets. This is the cleanest result in the audit.

Broken in-content internal links: **0** in every tree.

---

## 11. `/ka/` confirmation

The Georgian tree is structurally identical, as it must be — it is emitted by the same render functions.

| Measure | English | `/ka/` |
|---|---:|---:|
| Pages | 360 | 356 |
| In-content edges | 4,672 | 4,644 |
| Header/footer edges | 7,060 | 7,040 |
| Indexable orphans | 0 | 0 |
| Depth histogram (all links) | `{0:1, 1:20, 2:84, 3:132, 4:88, 5:26}` | `{0:1, 1:20, 2:84, 3:132, 4:88, 5:26}` — identical |
| Empty anchors | 1,306 (28.2%) | 1,306 (28.2%) |
| `/…/car-rental/{place}/` inbound | 1 each | 1 each |
| `/…/car-rental/` hub PageRank rank | 288 / 360 | **287 / 356** |
| `/…/car-rental/tbilisi/` rank | 351 / 360 | **350 / 356** |
| `/…/car-rental/minivan/` rank | 349 / 360 | **348 / 356** |
| Commercial cluster PR share | 26.7% | 27.1% |

The English tree has 4 extra nodes (`/404.html`, `/admin/`, `/admin/bookings.html`, `/admin/cms.html`) which exist only at the root. `/ru/`, `/fa/`, `/he/`, `/ar/` each have 356 pages and 4,642–4,644 in-content edges — the same shape again.

**Consequence for prioritisation: every fix below multiplies by six.** A rule that adds 294 links to the English tree adds 1,764 across the site.

---

## 12. Should `/car-rental/minivan/` stay indexable?

**Yes — keep it indexed, and fix its link supply instead.** The reasoning, from the data:

**Against noindex:**
- It is not a thin or fabricated page. `content/settings/seo_categories.yml` gives it 3 real `car_slugs` (`hyundai-staria` 9 seats, `mercedes-benz-vito` 8 seats, `toyota-alphard` 7 seats) with real rate cards (`price_1_6` / `price_7_29` / `price_30`) and `price_from_gel: 200`. It renders the same body template as `/car-rental/economy/`, which is the site's third-strongest page.
- It answers a distinct commercial query class (7–9-seater / group / family rental) that no other URL on the domain targets. `/fleet/` is a flat list of 17 cars; there is no other seats-based entry point.
- `noindex`-ing it would strand `hyundai-staria`, `mercedes-benz-vito` and `toyota-alphard`, which already sit at 2–3 inbound links each.

**The actual diagnosis:** minivan has 0 linked routes and 0 linked attractions because **the linking rule that populates the other three categories is road-type-based, and minivan is not a road-type category.** `attraction.car_category` is only ever `economy` (175), `suv` (59) or `offroad` (23); `route.car_category` is only ever `economy` (11), `suv` (17) or `offroad` (4). Minivan can never win a `road`-driven join. Its `road_types` is `[paved, mostly_paved]` — it is a *party-size* category, and party size is the axis nothing links on.

**The truthful join that does exist:** 22 of 32 routes have **every** waypoint at `road: paved` or `mostly_paved`, and all 22 have `max_people ≥ 7`. Those 22 routes can honestly link to `/car-rental/minivan/` as a group-travel option without claiming anything about road conditions that `attraction.road` does not already state. Add the 6 rental-location pages (`category_keys` currently lists only 2–3 of the 4 categories) and the page goes from 1 inbound to ~29.

Simulated: with the P0+P1 rules applied, `/car-rental/minivan/` moves from **rank 349/360 to rank 11/360**. There is no case for de-indexing a page that one rule change lifts into the top 3%.

**Separate issue surfaced by this:** the `business` and `van` fleet categories have **no `/car-rental/{category}/` page at all** (`render_car_rental_hub` iterates `order = ["economy", "suv", "offroad", "minivan"]`). Their 5 cars — BMW 5 Series, Mercedes E-Class, Toyota Camry, Sprinter, Transit — are the five weakest `car` pages on the site at 1 inbound link each. Either add the two category pages, or accept that those five vehicles will never rank.

---

## 13. Proposed link rules

Each rule is stated as an exact change to a named `build.py` function. Nothing invents a business fact: every rule reads a field that already exists in `content/`. Every UI string named below (`su(...)` key) **already exists in all six languages** in `content/settings/seo_ui.yml` — no new translation work.

### P0 — feed the `/car-rental/` cluster (1,764 pages affected sitewide)

The single highest-leverage change in the audit. Three functions, one new helper.

**P0.1 — New helper, place beside `_hav()` (`build.py:2307`) and `PLACE_BY_KEY` (`build.py:3237`):**

```python
_RENTAL_CITIES = ["tbilisi", "kutaisi", "batumi"]

def nearest_rental_place(lat, lon):
    """Nearest pickup city by great-circle distance. Data: places.yml coords.
    Returns (key, km). Straight-line — never labelled as driving distance."""
    best = min(_RENTAL_CITIES,
               key=lambda k: _hav(lat, lon, PLACE_BY_KEY[k]["lat"], PLACE_BY_KEY[k]["lon"]))
    return best, _hav(lat, lon, PLACE_BY_KEY[best]["lat"], PLACE_BY_KEY[best]["lon"])
```

**P0.2 — `attraction_links_block(lang, slug, a)` (`build.py:3374`)** — append a "Pick up your car" section. All 257 attractions have `lat`/`lon`; no page is skipped.

```python
key, km = nearest_rental_place(float(a["lat"]), float(a["lon"]))
loc = (SEO_CAR_RENTAL.get("locations") or {}).get(key, {})
if rental_quality_ok("location", loc):
    h1 = (loc.get(lang) or {}).get("h1", key)
    out += _sec(su("pickup_locations", lang),
                f'<div class="article"><p><a href="{rental_place_url(lang, key, False)}">{E(h1)}</a> '
                f'— {round(km)} {E(tu(lang, "km"))} {E(su("road", lang, a.get("road","paved")))}</p></div>')
```
*Distribution: 117 → `/car-rental/tbilisi/`, 102 → `/car-rental/kutaisi/`, 38 → `/car-rental/batumi/`. **257 new edges per tree, 1,542 sitewide.***

**P0.3 — `route_links_block(lang, slug, r)` (`build.py:3392`)** — same block, keyed on the first waypoint (the route's start), using existing `su("pickup_locations")`. Anchor should name the city, e.g. *"Car Rental in Tbilisi"*. *Distribution: 16 Tbilisi / 13 Kutaisi / 3 Batumi. **32 new edges per tree.***

**P0.4 — `render_itinerary` (`build.py:3646`)** — every itinerary has `start:` and `end:` (all currently `tbilisi`); emit a "Pick up in {start}" link using `rental_place_url(lang, it["start"])`, guarded by `it.get("start") in PLACE_BY_KEY`. ***5 new edges per tree.***

**Measured effect of P0 alone** (simulated on the real graph): `/car-rental/` hub **288 → 52**; `/car-rental/tbilisi/` **351 → 4**; `/car-rental/kutaisi/` **348 → 5**; `/car-rental/batumi/` **346 → 10**; rental-location PageRank share **0.44% → 4.96%**; commercial cluster **26.7% → 29.7%**.

### P1 — close the category ↔ vehicle ↔ region loops (396 pages sitewide)

**P1.1 — `route_links_block` (`build.py:3392`): link the actual cars, not just the class.** The category's 3 `car_slugs` are already loaded in `_seo_cats()`; reuse `_car_card(lang, slug)` (`build.py:3274`) and the existing `su("cars_in_category", lang)` heading.
```python
cars = (_seo_cats().get(cat, {}).get("data") or {}).get("car_slugs") or []
if cars:
    out += _sec(su("cars_in_category", lang),
                f'<div class="cards">{"".join(_car_card(lang, s) for s in cars[:3])}</div>', alt=True)
```
***96 new edges per tree.*** Fixes "0 of 32 routes link to a car page" and lifts the 5 orphaned business/van vehicles once P1.4 lands.

**P1.2 — `render_car` (`build.py:1310`): link each car up to its category page.** Uses `rental_cat_url(lang, c["category"])` and existing `su("all_cars_in_class", lang)`. Requires `CATEGORY_SLUG` to cover `business` and `van` (see P1.5). ***17 new edges per tree; makes `/fleet/` ↔ car ↔ category a closed triangle.***

**P1.3 — `render_rental_location` (`build.py:3484`): add a car grid.** The function already resolves `d["category_keys"]`; expand each to its `car_slugs` and render `_car_card`. Cap at 6. ***18 new edges per tree — and, critically, gives the location pages an outbound path into the fleet cluster so they stop being pure donors.***

**P1.4 — `render_region` (`build.py:2030`): add "Road trips in {region}" and "Pick up a car near {region}".** Build a reverse index next to `ROUTES_BY_ATTRACTION` (`build.py:3360`):
```python
def _routes_by_region():
    idx = {}
    for slug, r in ROUTES.items():
        regs = Counter(ATTRACTIONS[w]["region"] for w in (r.get("waypoints") or [])
                       if w in ATTRACTIONS)
        if regs:
            idx.setdefault(regs.most_common(1)[0][0], []).append(slug)
    return idx
ROUTES_BY_REGION = _routes_by_region()
```
All 11 regions get ≥1 route (Samegrelo 5, Mtskheta-Mtianeti / Tbilisi / Kakheti / Samtskhe 4 each, Racha / Adjara 3, Imereti 2, Guria / Kvemo Kartli / Shida Kartli 1). Reuse `_route_links(lang, ROUTES_BY_REGION[key], 6)` and `su("popular_routes_from", lang)`. Plus one `nearest_rental_place()` link from the region centroid (`region.center_lat` / `center_lon` already exist). ***43 new edges per tree; also pulls all 11 region pages from depth 3–4 to depth 2 once a region hub exists (P2.4).***

**P1.5 — `CATEGORY_SLUG` / `render_car_rental_hub` (`build.py:3237`, `3411`): decide on `business` and `van`.** Either add them to `order` so `/car-rental/business/` and `/car-rental/van/` exist, or accept that 5 of 17 car pages stay at 1 inbound link. The rate data (`price_1_6`, `seats`) is present for all 5 vehicles.

**P1.6 — Minivan-specific rule, `route_links_block`.** Where every waypoint of a route is `paved`/`mostly_paved` **and** `route.max_people >= 7`, add a second, clearly-labelled group-travel link to `/car-rental/minivan/`. That is 22 of 32 routes, and it is the only truthful join available for a party-size category. Add `minivan` to `category_keys` for all 6 locations in `content/settings/seo_car_rental.yml` (data change, no code). ***~28 new inbound for the minivan page; rank 349 → 11.***

**P1.7 — Reciprocate the itinerary axis.** Build `ITINERARIES_BY_ATTRACTION` — the function already exists as `_itineraries_by_attraction()` (`build.py:3363`) and **is defined but never called**. Wire it into `attraction_links_block` under the existing `su("itineraries", lang)` heading. Fixes the 68 one-way itinerary→attraction edges and lifts all 5 itineraries (currently 3 inbound each).

### P2 — stop the leaks (1,962 pages sitewide)

**P2.1 — Remove `/contact/` from the in-`<main>` CTA on templated pages** (`render_attraction` ~`build.py:2270`, `render_route` ~`2068`, `render_region` ~`2188`, `render_car`, `render_rental_location` ~`3517`). Keep the WhatsApp/phone buttons and the booking-dialog trigger — those are not crawlable links and lose nothing. `/contact/` stays in the footer on all 2,140 pages, which is ample. ***Removes 327 edges per tree and reclaims 8.6% of in-content PageRank; `/contact/` drops from rank 1 to rank 5.***

**P2.2 — Collapse the duplicate image anchors.** In the card markup, wrap the image *inside* the existing text anchor rather than emitting a second `<a class="card-img">`, or give the image anchor `tabindex="-1" aria-hidden="true"`. ***Eliminates 1,306 empty anchors per tree (28.2% of all in-content links), 7,836 sitewide, with no visual change.***

**P2.3 — Vary the category anchor.** In `attraction_links_block`, the anchor currently renders `f'{cat_label(cat, lang)} — {su("price_from")} {cheapest_price(cat)} ₾/day'` identically on 186 pages. Compose it from data already in scope — region name and `road` label — so the 186 exact-match anchors become ~11 variants (one per region) that are still generated and still true.

**P2.4 — Build the three missing hubs: `/attractions/`, `/routes/`, `/regions/`.** `dist/sitemaps/` already ships `attractions.xml`, `routes.xml` and `regions.xml`, so the URL sets exist; only the HTML index is missing. A region hub alone moves 11 region pages from depth 3–4 to depth 2 and every attraction from depth 3–5 to depth ≤3.

**P2.5 — Give `/map/` a crawlable link block.** It currently emits **one** in-content link. The design doc already specifies this block ("planner → routes / attractions / car rental"). Rendering the 32 routes plus the 11 regions as a static `<noscript>`-independent list would cost 43 links and shorten the path to every attraction.

**P2.6 — "Continue your road trip" (route → next route).** Listed in the design doc, implemented nowhere: 0 of 32 routes link to another route. The nearest truthful join is shared waypoints or shared region via `ROUTES_BY_REGION`.

**P2.7 — Raise the route cap in `attraction_links_block`.** `_route_links(lang, rs, 4)` truncates only 2 attractions (`bagrati-cathedral` 6 routes, `borjomi-central-park` 5). Raising the cap to 6 is harmless and recovers 3 edges. Low value — listed for completeness.

### Simulated impact (computed on the real English graph)

| Scenario | Edges | Commercial cluster PR | `/car-rental/` rank | `/car-rental/tbilisi/` rank | `/car-rental/minivan/` rank | `/contact/` rank |
|---|---:|---:|---:|---:|---:|---:|
| **Measured today** | 3,138 | 26.7% | 288 / 360 | **351 / 360** | 349 / 360 | **1** |
| + P0 | 3,432 | 29.7% | 52 | **4** | 336 | 1 |
| + P0 + P1 | 3,619 | 33.5% | 79 | **4** | **25** | 1 |
| + P0 + P1 + P2.1 | 3,292 | **43.6%** | 80 | **4** | **11** | 5 |

P0+P1+P2.1 moves 16.9 points of in-content PageRank into the commercial cluster while **removing** 327 links — the graph gets smaller and better-aimed at the same time.

One residual after the simulation: the three **airport** pages (`tbilisi-airport`, `kutaisi-airport`, `batumi-airport`) stay at ranks 334–337 even after P0+P1, because `nearest_rental_place()` resolves to the city, never the airport. They need their own rule — a city → airport link ("arriving by air") on each of the three city pages, and an airport link on itineraries, which is truthful since every itinerary starts and ends in Tbilisi.

---

## 14. Priority summary

| # | Change | Priority | Pages affected (sitewide) | Measured payoff |
|---|---|---|---:|---|
| P0.2 | attraction → nearest rental location | **P0** | 1,542 | rental-locations 0.44% → 4.96% of PR |
| P0.3 | route → rental location at start | **P0** | 192 | `/car-rental/` hub 288 → 52 |
| P0.4 | itinerary → rental location at `start` | **P0** | 30 | closes the highest-intent gap in the funnel |
| P2.1 | drop `/contact/` from in-`<main>` CTAs | **P0** | 1,962 | reclaims 8.6% of in-content PR |
| P2.2 | collapse 1,306 empty image anchors | **P0** | 1,776 | recovers 28.2% of anchor signal |
| P1.1 | route → the 3 cars in its category | P1 | 192 | fixes 0/32 route→car coverage |
| P1.4 | region → routes + nearest rental location | P1 | 66 | regions depth 3–4 → 2 |
| P1.3 | rental-location → cars | P1 | 36 | ends 100% one-way outflow from locations |
| P1.6 | minivan group-travel rule (22 routes) | P1 | 132 | minivan rank 349 → 11 |
| P1.7 | wire up the unused `_itineraries_by_attraction()` | P1 | 1,542 | reciprocates 68 one-way edges |
| P1.2 | car → its category page | P1 | 102 | closes fleet↔category triangle |
| P1.5 | `/car-rental/business/`, `/car-rental/van/` | P1 | 12 new pages | rescues the 5 weakest car pages |
| P2.4 | `/attractions/`, `/routes/`, `/regions/` hubs | P2 | 18 new pages | 108 attractions from depth 4–5 to ≤3 |
| P2.5 | crawlable link block on `/map/` | P2 | 18 | `/map/` currently emits 1 link |
| P2.3 | vary the 186 identical category anchors | P2 | 1,542 | removes exact-match footprint |
| P2.6 | "Continue your road trip" | P2 | 192 | 0/32 today |
| — | airport-page rule (city → airport) | P2 | 36 | airports stay at rank 334+ without it |
| P2.7 | raise route cap 4 → 6 | P2 | 12 | 3 edges |

---

## 15. What to re-measure after shipping

Re-run the same extraction and assert, per language tree:

1. `/car-rental/{place}/` in-content inbound ≥ 30 (today: 1).
2. `/car-rental/` hub PageRank rank ≤ 80 of 360 (today: 288).
3. Empty in-content anchors ≤ 1% (today: 28.2%).
4. `/contact/` in-content inbound ≤ 10 (today: 334).
5. Indexable pages with ≤1 in-content inbound ≤ 5 (today: 28).
6. Attractions at click depth ≥ 4: 0 (today: 108).
7. Cross-language in-content links on indexable pages: 0 (today: 0 — do not regress this).
8. Broken in-content internal links: 0 (today: 0).
