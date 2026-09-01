# RentUp.ge — Road-condition guides (`/guides/road-to-*`)

Companion to `KEYWORD_CLUSTERS.md` (clusters **B3** Kazbegi, **B4** Svaneti,
**B6** Tusheti, **B12** mountain passes) and to the existing decision guide
`/guides/do-i-need-a-4x4-in-georgia/`. Three new guide files were added on
2026-09-01, in the same schema as `content/guides/do-i-need-a-4x4-in-georgia.yml`
and complete in all six languages (ka · en · ru · fa · he · ar).

**Written:** 2026-09-01 · **Source of every figure:** `content/attractions/*.yml`
and `content/routes/*.yml` as loaded by `build.ATTRACTIONS` / `build.ROUTES`.
Nothing on these pages comes from memory or from third-party road reports.

---

## 1. The three files

| File | Slug / URL | `order` | `car_category` | Cluster served |
|---|---|---|---|---|
| `content/guides/road-to-kazbegi-georgian-military-highway.yml` | `/guides/road-to-kazbegi-georgian-military-highway/` | 30 | `suv` | B3 (+ Russian head term *Военно-Грузинская дорога*) |
| `content/guides/road-to-svaneti-mestia-ushguli.yml` | `/guides/road-to-svaneti-mestia-ushguli/` | 31 | `offroad` | B4 ("is the road to Ushguli paved?") |
| `content/guides/road-to-tusheti-abano-pass.yml` | `/guides/road-to-tusheti-abano-pass/` | 32 | `offroad` | B6 (+ *Тушетия на кроссовере*) and the seasonal half of B12 |

`car_category` is taken from the matching route file (`military-highway-kazbegi:
suv`, `svaneti-expedition: offroad`, `tusheti-highland-hike: offroad`), which is
what `_guide_related()` uses for the "best car for this trip" button.

Note: `best-time-to-visit-georgia.yml` already carries `order: 30`. The Kazbegi
guide was given `order: 30` as instructed; if hub ordering matters, bump one of
them — the field only affects sort order on `/guides/`.

---

## 2. What each page says, and the fields it says it from

### 2.1 Kazbegi — Georgian Military Highway

Segment table drawn from `road` / `car_category` / `elevation` /
`distance_tbilisi_km` / `drive_time_tbilisi` / `best_season` / `open_year_round`:

| Stop | road | car | m | km / time | season | year-round |
|---|---|---|---|---|---|---|
| zhinvali-reservoir | paved | economy | 810 | 65 / 1:15 | may-october | yes |
| ananuri-fortress | paved | economy | 830 | 70 / 1:20 | all | yes |
| gudauri | paved | **suv** | 2,200 | 120 / 2:10 | december-march | yes |
| jvari-pass-friendship-monument | paved | economy | 2,380 | 125 / 2:20 | all | yes |
| gergeti-trinity-church | mostly_paved | **suv** | 2,170 | 160 / 3:10 | may-october | yes |
| dariali-gorge-gveleti-waterfalls | mostly_paved | **suv** | 1,550 | 170 / 3:25 | may-october | yes |
| sno-valley | paved | economy | 1,650 | 152 / 3:00 | may-october | yes |
| truso-valley | gravel | **offroad** | 2,100 | 145 / 3:00 | june-september | **no** |
| juta-chaukhi | 4x4_only | **offroad** | 2,150 | 165 / 3:45 | june-september | **no** |

Route: `military-highway-kazbegi` — 340 km, 6:40, 2 days, `suv`, `best_season:
all`, `moderate`. The day plan on the page is the route's own `plan` block.
Derived figure: "roughly 1,550 m of climbing in 55 km" = Jvari Pass (2,380 m,
125 km) minus Ananuri (830 m, 70 km).

Headline answer: **main road economy to the pass, SUV for Gudauri/Gergeti/
Dariali, off-road only for Truso and Juta.** This is the "key answerable
question, currently unanswered anywhere on the site" flagged under B3.

### 2.2 Svaneti — Zugdidi, Mestia, Ushguli

| Stop | road | car | m | km / time | season | year-round |
|---|---|---|---|---|---|---|
| bagrati-cathedral | paved | economy | 180 | 230 / 3:20 | all | yes |
| dadiani-palace-zugdidi | paved | economy | 100 | 320 / 4:40 | all | yes |
| enguri-dam | paved | economy | 300 | 350 / 5:10 | all | yes |
| mestia | paved | **suv** | 1,500 | 470 / 8:30 | may-october | yes |
| ushguli | gravel | **offroad** | 2,100 | 515 / 10:30 | june-september | **no** |
| chalaadi-glacier | mostly_paved | suv | 1,900 | 480 / 8:50 | june-september | no |
| hatsvali-tetnuldi | mostly_paved | suv | 1,870 | 478 / 8:50 | december-march | no |
| becho-mazeri | gravel | suv | 1,600 | 455 / 8:20 | may-october | no |
| koruldi-lakes | 4x4_only | offroad | 2,740 | 480 / 9:30 | june-september | no |
| adishi | 4x4_only | offroad | 2,040 | 505 / 10:15 | june-september | no |
| shkhara-glacier | 4x4_only | offroad | 2,350 | 515 / 10:30 | june-september | no |

Route: `svaneti-expedition` — 1,050 km, 21:00, 5 days, `offroad`,
`june-september`, `hard`; day plan is the route's `plan` block.
`svaneti-alpine-circuit` (6 days, 720 km, `july-september`) is linked as the
harder extension. Derived figure: "the gorge lifts you 1,200 m" = Mestia
(1,500 m) minus Enguri Dam (300 m).

Headline answer: **paved to Mestia (SUV-rated for altitude/winter, sedan will
manage per the YAML), gravel/off-road for the last 45-47 km to Ushguli.** This
is the "cleanest achievable win in Part B" under B4.

### 2.3 Tusheti — Abano Pass

| Stop | road | car | m | km / time | season | year-round |
|---|---|---|---|---|---|---|
| gombori-pass | paved | economy | 1,620 | 62 / 1:20 | all | yes |
| telavi-batonis-tsikhe | paved | economy | 755 | 95 / 1:45 | all | yes |
| alaverdi-cathedral | paved | economy | 470 | 110 / 2:05 | all | yes |
| abano-pass | 4x4_only | offroad | **2,850** | 180 / 5:00 | june-september | **no** |
| omalo-tusheti | 4x4_only | offroad | 1,880 | 220 / 6:30 | june-september | **no** |
| dartlo | 4x4_only | offroad | 1,980 | 228 / 7:00 | june-september | **no** |
| shenako-diklo | 4x4_only | offroad | 2,100 | 235 / 7:30 | june-september | **no** |

Route: `tusheti-highland-hike` — 430 km, 13:30, 5 days, `offroad`,
`june-september`, `hard`; its `plan` is a one-line-per-day sketch and the page
reproduces it as such rather than inventing timings. Derived figure: "about
2,100 m of climbing" = Abano (2,850 m) minus Telavi (755 m); Pshaveli has no
elevation in the data, so the page does not give one.

Seasonal wording is deliberately limited to what the YAML holds:
`best_season: june-september`, `open_year_round: false`, and the Abano `tip`
text "Closed all winter". The KEYWORD_CLUSTERS note that says "June–Oct" is not
repeated because no field says it.

Insurance wording is limited to the two sentences already in the attraction
YAML (`abano-pass.tip`: "check that the insurance covers the Tusheti road — many
companies exclude it outright"; `omalo-tusheti.tip`: "confirm in advance whether
your rental agreement permits the Abano Pass … see our /terms/"). The pages link
`/terms/` and `/faq/` and make no claim about what RentUp's own cover includes,
because cluster A17 is still **blocked** on contradictory source data.

---

## 3. Linking

Every page links, in every language:

- the attractions in its segment table (`/attractions/{slug}/`);
- its route page(s) (`/routes/{slug}/`);
- `/car-rental/suv/` and `/car-rental/4x4/` as the data dictates (Kazbegi: SUV
  primary, 4x4 for the side valleys; Svaneti and Tusheti: 4x4 primary, SUV as
  the "stops here" contrast);
- `/guides/do-i-need-a-4x4-in-georgia/` for the clearance argument;
- `/terms/` (and `/faq/` on Tusheti).

`related_routes` and `related_attractions` in the front-matter drive the
generated "part of routes" / "nearby places" blocks. All slugs were verified
against `build.ROUTES` and `build.ATTRACTIONS`.

Inbound: nothing in `build.py` was touched. `guides_for_place()` still returns
only the three original guides, so the new pages currently receive links from the
`/guides/` hub and from each other's `related_*` blocks only. **Suggested
follow-up (not done here, out of scope for this task):** extend
`guides_for_place()` so that `mtskheta-mtianeti` places on the E117 point to the
Kazbegi guide, `samegrelo-zemo-svaneti` places to the Svaneti guide, and the
four Tusheti places to the Tusheti guide; and add the Tusheti guide to the
`/car-rental/4x4/` copy, which B6 already identifies as the highest-intent 4x4
conversion path.

---

## 4. Constraints applied

| Rule | How it was met |
|---|---|
| Every fact from YAML | Segment tables, distances, times, altitudes, seasons, fuel stops, visit hours and warnings all trace to `attractions/*.yml` fields or `en.route` / `en.tip` text; day plans to `routes/*.yml → plan`. |
| No prices, no commercial terms | Checked by regex for `₾ / GEL / lari / price / цена / ფასი / deposit / залог` across bodies and FAQs in all 18 language bodies. |
| Georgian voice | `გაქირავება` in the terms link; declined place names throughout (`ყაზბეგში`, `მესტიაში`, `ომალოში`, `სტეფანწმინდაში`, `ფშაველიდან`, `თელავამდე`); `ჯიპი` / `კროსოვერი` as in the existing guide. |
| RTL number ranges with a hyphen | `45-47`, `15-20`, `5-8`, `07:00-10:00` etc. use ASCII hyphen in fa/he/ar; checked by regex for en/em dashes between digits. |
| Word counts | en/ka/ru 900-1300, fa/he/ar 600-900 — see §5. |
| `meta_title` ≤ 65 incl. " \| RentUp" | Longest is 58 (ar, Svaneti). |
| `meta_description` 140-158 | All 18 in range. |
| 4-6 FAQ per language | 6 in en/ka/ru, 5 in fa/he/ar. |
| Only existing slugs in links | Validated against `build.ATTRACTIONS`, `build.ROUTES`, `build.CATEGORY_SLUG`, `build.GUIDES` + the three new slugs. |
| `guide_quality_ok()` | True for all 18 language bodies (≥ 1,500 chars, name + meta_description present), so all three pages are indexable and enter the sitemap. |

---

## 5. Measured on 2026-09-01

| Guide | en | ka | ru | fa | he | ar |
|---|---|---|---|---|---|---|
| Kazbegi — words | 1,166 | 913 | 1,003 | 895 | 849 | 892 |
| Kazbegi — title / desc chars | 57 / 153 | 48 / 151 | 51 / 153 | 45 / 145 | 39 / 141 | 51 / 147 |
| Svaneti — words | 1,227 | 928 | 1,073 | 899 | 829 | 900 |
| Svaneti — title / desc chars | 55 / 151 | 52 / 156 | 55 / 157 | 52 / 154 | 50 / 142 | 58 / 142 |
| Tusheti — words | 1,073 | 914 | 916 | 899 | 783 | 848 |
| Tusheti — title / desc chars | 47 / 155 | 52 / 152 | 51 / 152 | 48 / 151 | 44 / 141 | 51 / 150 |

Validation script used (scratchpad, not committed): loads each file with
`yaml.safe_load`, checks the front-matter slugs, meta lengths, FAQ counts, word
bands, link targets, RTL dash usage and `build.guide_quality_ok()`, then renders
each page with `build.render_guide()` for all six languages.

---

## 6. What these pages deliberately do not do

- They do not say a road is open, closed or safe today. Each carries the same
  "classification, not a live road report" caveat as the 4x4 guide, which B12
  requires.
- They do not describe RentUp's insurance position on the Abano Pass beyond
  "read the terms", for the A17 reason above.
- They do not repeat the "with driver" upsell, because `/car-rental/with-driver/`
  is not a URL the generator emits today; the Tusheti page instead relays the
  YAML's own "shared jeeps from Pshaveli and Alvani" alternative.
- They do not give Pshaveli, Kobi, Stepantsminda or Zugdidi-to-Mestia
  elevations, because no attraction record carries them.
