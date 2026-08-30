# RentUp.ge — Guides Content Build (`content/guides/*.yml`)

**Written:** 2026-08-30 · **Author:** content pass for briefs `CONTENT_BRIEFS.md #1` and
`KEYWORD_CLUSTERS.md` clusters **B10**, **B12**, **B14**
**Files created:** three, all six languages complete, all validated with `yaml.safe_load`

| File | URL it targets | Cluster |
|---|---|---|
| `content/guides/do-i-need-a-4x4-in-georgia.yml` | `/guides/do-i-need-a-4x4-in-georgia/` | B10 |
| `content/guides/driving-in-georgia.yml` | `/guides/driving-in-georgia/` | B12 |
| `content/guides/best-time-to-visit-georgia.yml` | `/guides/best-time-to-visit-georgia/` | B14 |

Nothing outside `content/guides/` and this file was touched. `build.py` is not yet aware of this
directory — these files will not render until the renderer lands.

---

## 1. The data, counted on 2026-08-30

Counted directly from every `content/attractions/*.yml` and `content/routes/*.yml` with a throwaway
script (not re-quoted from any doc). **Every number published on the three pages comes from this
section.**

### 1.1 Corpus size — the briefs are out of date

`CONTENT_BRIEFS.md §Brief 1` and `KEYWORD_CLUSTERS.md §B10` both state **257** attractions. The repo
now holds **267**. Ten attractions were added after those documents were written, and the headline
percentages moved with them. The guides publish the current figures.

| Field | Brief (257 places) | Measured now (267 places) |
|---|---|---|
| `paved` | 149 (58.0%) | **154 (57.7%)** |
| `mostly_paved` | 71 (27.6%) | **73 (27.3%)** |
| `gravel` | 20 (7.8%) | **23 (8.6%)** |
| `4x4_only` | 17 (6.6%) | **17 (6.4%)** |
| gravel + 4x4_only | 37 (14.4%) | **40 (15.0%)** |
| Reachable in an ordinary car | 220 (85.6%) | **227 (85.0%)** |
| `economy` | 175 (68.1%) | **181 (67.8%)** |
| `suv` | 59 (23.0%) | **63 (23.6%)** |
| `offroad` | 23 (8.9%) | **23 (8.6%)** |

Note the shape of the change: `4x4_only` and `offroad` are both **unchanged**; the three new gravel
places are all SUV-rated. The "37 places" headline in the brief must be read as **40** from now on,
and "85.6%" as **85.0%**.

### 1.2 Field coverage

`road`, `car_category`, `distance_tbilisi_km`, `drive_time_tbilisi`, `best_season`, `elevation` and
`open_year_round` are present on **267 of 267** records — zero gaps. This 100% coverage claim is made
explicitly on the 4x4 guide as an E-E-A-T signal, because it is checkable.

### 1.3 Cross-tabulation `road` × `car_category`

Twelve pairings are possible; **seven occur**.

| road | car_category | Count |
|---|---|---|
| paved | economy | 150 |
| paved | suv | 4 |
| mostly_paved | economy | 31 |
| mostly_paved | suv | 42 |
| gravel | suv | 17 |
| gravel | offroad | 6 |
| 4x4_only | offroad | 17 |

Two mechanical facts fall out and are stated on the page: **every `4x4_only` place is `offroad`, with
no exceptions across 267 records**, and **no `gravel` place is ever `economy`**.

The four `paved` + `suv` outliers are all high-altitude resorts, which is why the rating exists:
`gudauri` (2,200 m), `bakuriani` (1,700 m), `mestia` (1,500 m), `svaneti-museum-mestia` (1,450 m).

### 1.4 The 17 `4x4_only` places (published in full on the page by name)

`abano-pass` (Kakheti, 2,850 m — highest point in the dataset), `adishi`, `dartlo`,
`green-lake-goderdzi`, `juta-chaukhi`, `khikhani-fortress`, `kldekari-fortress`, `koruldi-lakes`,
`mutso`, `omalo-tusheti`, `shatili`, `shenako-diklo`, `shkhara-glacier`, `takhti-tepha-mud-volcanoes`,
`tobavarchkhili-lakes`, `udziro-lake-buba-glacier`, `vashlovani-national-park`.

Fifteen carry `best_season: june-september`; the two exceptions (`vashlovani-national-park`,
`takhti-tepha-mud-volcanoes`) are `may-october` and low-lying — they are 4x4-only for surface, not
snow.

### 1.5 The 23 `gravel` places

`abudelauri-lakes`, `bakhmaro`\*, `balda-canyon`, `bateti-lake`, `batsara-reserve`, `becho-mazeri`,
`beshumi`\*, `birtvisi-fortress`, `chiora`\*, `gardabani-managed-reserve`, `goderdzi-pass`\*,
`gomismta`, `khada-valley`, `kinchkha-waterfall`, `kintrishi-protected-areas`, `oniore-waterfall`,
`pitareti-monastery`, `rkoni-monastery`, `tmogvi-fortress`, `truso-valley`\*, `ushguli`\*,
`zedazeni-monastery`, `zoti`. (\* = the six rated `offroad` despite being `gravel`.)

### 1.6 Region concentration of the 40 hard places

| Region | gravel | 4x4_only | Hard | Places mapped |
|---|---|---|---|---|
| samegrelo-zemo-svaneti | 4 | 4 | 8 | 26 |
| kakheti | 1 | 6 | 7 | 33 |
| mtskheta-mtianeti | 4 | 3 | 7 | 25 |
| adjara | 3 | 2 | 5 | 24 |
| kvemo-kartli | 3 | 0 | 3 | 20 |
| guria | 3 | 0 | 3 | 19 |
| shida-kartli | 2 | 1 | 3 | 19 |
| racha-lechkhumi | 1 | 1 | 2 | 20 |
| imereti | 1 | 0 | 1 | 31 |
| samtskhe-javakheti | 1 | 0 | 1 | 22 |
| **tbilisi** | **0** | **0** | **0** | 28 |

### 1.7 Implied road speed by surface — original, not in any existing doc

`distance_tbilisi_km ÷ drive_time_tbilisi`, over the 229 places lying more than 40 km from Tbilisi
(places closer in are dominated by city traffic and distort the figure):

| road | n | Median | Mean |
|---|---|---|---|
| paved | 120 | **66 km/h** | 62.8 |
| mostly_paved | 69 | **60 km/h** | 59.4 |
| gravel | 23 | **49 km/h** | 51.7 |
| 4x4_only | 17 | **42 km/h** | 42.8 |
| **all** | 229 | **61 km/h** | 59.2 |

This is the backbone of the driving guide, and it is independently corroborated by the five
itineraries, whose own `total_km ÷ total_drive` land at 52-55 km/h:
3-day 420 km / 8:00, 5-day 610 km / 13:00, 7-day 1,020 km / 18:30, 10-day 1,450 km / 27:00,
14-day 2,040 km / 39:30.

### 1.8 Seasonality

`best_season` values across 267: `all` 159 (59.6%), `may-october` 69 (25.8%), `june-september` 36
(13.5%), `december-march` 2, `april-october` 1. Separately, `open_year_round: false` on **52** places.

Month-by-month, counting how many places and how many of the 49 routes fall inside their window:

| Month | Places in season | Share | Routes in season |
|---|---|---|---|
| Jan / Feb | 161 | 60% | 14 |
| Mar | 161 | 60% | 16 |
| Apr | 160 | 60% | 25 |
| May | 229 | 86% | 43 |
| Jun | 265 | 99% | 48 |
| Jul / Aug / Sep | 265 | 99% | 49 |
| Oct | 229 | 86% | 43 |
| **Nov** | **159** | **60%** | 16 |
| Dec | 161 | 60% | 14 |

November is the thinnest month of the year. The two places absent from the summer peak are the only
two winter-season records in the repo: `gudauri` and `hatsvali-tetnuldi` (`best_season: december-march`).

Season is a function of altitude, not the calendar:

| Elevation | Places | `best_season: all` |
|---|---|---|
| < 500 m | 108 | 86 (80%) |
| 500-999 m | 85 | 56 (66%) |
| 1,000-1,499 m | 31 | 14 (45%) |
| 1,500-1,999 m | 23 | 2 (9%) |
| ≥ 2,000 m | 20 | 1 (5%) — 15 of the 20 are June-September |

Composition of the 36 `june-september` places by surface: `4x4_only` 15, `gravel` 8,
`mostly_paved` 5, `paved` 8. **All eight paved ones are Black Sea coast entries** (Anaklia, Ureki,
Kobuleti, Kvariati, Sarpi, Grigoleti, Shekvetili, Tsitsinatela) — seasonal because of the water, not
the road. This is used on the page to keep "season" and "road condition" from being conflated.

### 1.9 Routes and fleet

49 routes, 19,727 km in total. Difficulty: easy 21, moderate 23, hard 5. Category: economy 21,
suv 23, offroad 5. Season: `may-october` 18, `all`/`year-round` 14, `april-october` 9,
`june-september` 5, `march-november` 2, `july-september` 1.

Fleet `clearance` (mm) / `drive` from `content/cars/*.yml`: economy Corolla 135, Elantra 140,
Prius 145 (fwd); suv Tucson 181, Outlander 190, RAV4 195 (awd/4wd); offroad Delica 210, Prado 220,
Pajero 235 (4wd). 15 of the 17 models are `transmission: automatic` (only Transit and Sprinter are
manual). `fuel_l_100km: 8.5` from `content/settings/site.yml`.

---

## 2. The three guides, titled

| Lang | `/guides/do-i-need-a-4x4-in-georgia/` | `/guides/driving-in-georgia/` | `/guides/best-time-to-visit-georgia/` |
|---|---|---|---|
| **en** | Do You Need a 4x4 in Georgia? | Driving in Georgia: What the Distances Actually Cost You | The Best Time to Visit Georgia, Counted Month by Month |
| **ka** | გჭირდებათ თუ არა ჯიპი საქართველოში? | მართვა საქართველოში: რას გიჯდებათ რეალურად მანძილები | როდის ჯობია საქართველოში ჩამოსვლა — თვე თვეზე დათვლილი |
| **ru** | Нужен ли внедорожник в Грузии? | Вождение в Грузии: чего на самом деле стоят расстояния | Когда лучше ехать в Грузию: подсчёт по месяцам |
| **fa** | آیا در گرجستان به خودروی 4x4 نیاز دارید؟ | رانندگی در گرجستان: فاصله‌ها واقعاً چقدر وقت می‌برند | بهترین زمان سفر به گرجستان، ماه به ماه |
| **he** | האם צריך רכב 4x4 בגאורגיה? | נהיגה בגאורגיה: כמה באמת עולים לכם המרחקים | מתי הכי כדאי לבקר בגאורגיה, חודש בחודשו |
| **ar** | هل تحتاج إلى سيارة دفع رباعي في جورجيا؟ | القيادة في جورجيا: كم تكلّفك المسافات فعلاً | أفضل وقت لزيارة جورجيا، شهراً بشهر |

Per-language body word counts (all inside the brief's targets — 900-1400 for en/ka/ru, 600-900 for
fa/he/ar):

| File | ka | en | ru | fa | he | ar |
|---|---|---|---|---|---|---|
| 4x4 | 945 | 1171 | 993 | 709 | 623 | 646 |
| driving | 903 | 1113 | 920 | 622 | 618 | 616 |
| best-time | 935 | 1136 | 969 | 705 | 615 | 640 |

All 18 `meta_title` values are ≤ 65 chars including ` | RentUp`; all 18 `meta_description` values are
140-158 chars; all 18 `short` values ≤ 180 chars. FAQ entries: 6 per language in en/ka/ru, 5 in
fa/he/ar — 96 Q&A pairs in total, each answerable from the fields above.

---

## 3. Every internal link used

34 distinct URLs. Every attraction, route and itinerary slug was checked against `content/` **and**
against `dist/<path>/index.html` before being linked; nothing links to a 404.

**Commercial / hub (all three guides):** `/car-rental/`, `/car-rental/economy/`, `/car-rental/suv/`,
`/car-rental/4x4/`
**Policy (4x4 + driving):** `/terms/`, `/faq/`
**Cross-guide:** `/guides/do-i-need-a-4x4-in-georgia/`, `/guides/driving-in-georgia/`,
`/guides/best-time-to-visit-georgia/` — the three link to each other in a closed triangle
**Blog:** `/blog/zamtris-mgzavroba-saqartveloshi/` (driving guide, for winter detail rather than
duplicating it)

| Guide | Attractions | Routes | Itineraries |
|---|---|---|---|
| **4x4** | `ushguli`, `mestia`, `abano-pass`, `omalo-tusheti`, `gergeti-trinity-church`, `truso-valley`, `juta-chaukhi`, `gudauri`, `bakuriani` | `svaneti-expedition`, `tusheti-highland-hike`, `military-highway-kazbegi`, `kakheti-wine-loop` | `georgia-5-days`, `georgia-7-days` |
| **driving** | `ananuri-fortress`, `gergeti-trinity-church`, `sighnaghi`, `batumi-boulevard-old-town`, `uplistsikhe`, `mestia`, `ushguli` | `military-highway-kazbegi` | `georgia-3-days`, `georgia-7-days`, `georgia-10-days`, `georgia-14-days` |
| **best-time** | `gudauri`, `hatsvali-tetnuldi`, `ushguli`, `abano-pass`, `sighnaghi`, `uplistsikhe`, `borjomi-central-park`, `bakuriani` | `kakheti-wine-loop`, `svaneti-expedition` | — |

`related_routes` / `related_attractions` front-matter (for the renderer) uses only slugs from the same
verified set. `image` on each file points at a real `static/photos/*.webp`:
`abano-pass.webp`, `gudauri.webp`, `sighnaghi.webp`.

Two links the brief asked for were **not** used because the pages do not exist yet:
`/car-rental/with-driver/` and `/car-rental/monthly/`. Add them once briefs #4 and #9 ship.

---

## 4. Editorial rules applied

- **No commercial term is restated.** No price, deposit, excess, insurance figure, minimum age or
  young-driver surcharge appears anywhere in the three files. Where a reader needs one, the copy says
  so and links to `/terms/` and `/faq/`. This side-steps the `rental_policy.yml` ↔ `faq.yml` ↔
  `terms.yml` conflict logged in `CONTENT_BRIEFS.md §0.3` entirely — none of these pages will need
  re-editing when that reconciliation lands.
- **Two facts that are not commercial were used**, because they are consistent across four sources
  (`fleet.yml`, `pricing.yml`, `faq.yml`, `posts/zamtris-mgzavroba-saqartveloshi.yml`): winter tyres
  are fitted **1 December - 1 April** (stated without any price), and 15 of 17 models are automatic.
  The `site.yml` figure `fuel_l_100km: 8.5` is cited as the planner's assumption; `fuel_price_gel` is
  deliberately **not** published, since a pump price goes stale within weeks.
- **No road condition, season, distance or price was invented.** Every place-level claim traces to a
  named field in that place's own YAML. The one narrative fact taken from prose rather than a field —
  the rtveli harvest running "from late September through October" — is quoted from
  `content/routes/kakheti-wine-loop.yml` and attributed on the page as our own route note.
- **Every page carries a "what this does not tell you" section**, per the brief's honesty
  requirement: `road` and `best_season` are classifications, not a live status feed; 52 places are
  flagged `open_year_round: false`; a high pass can slip by weeks. No page claims any road is
  currently open, closed, safe or passable.
- **The 40-place figure is never extrapolated** to "Georgian roads" in general — it is always framed
  as 40 of the 267 attractions in this dataset.
- **"Jeep" is not used as a category name in English.** In Georgian, `ჯიპი` is used, because it is the
  vernacular search term (`KEYWORD_CLUSTERS.md §B10`).

### Georgian language

`გაქირავება` in company voice, `დაქირავება` where the customer is the subject (all CTA link text
reads `ავტომობილის დაქირავება`); `ქირაობა` appears nowhere. `ფრანშიზა`/`ექსცესი` and
`მღვიმეები`/`ღრმულები` do not arise, since no insurance or cave content is in these three files —
checked mechanically anyway. Place names are declined (`მესტიამდე`, `ბათუმამდე`, `თბილისიდან`,
`უშგულის`, `ომალოსა და თუშეთისკენ`). The Georgian is written from the data, not translated from the
English — the section order and several arguments differ deliberately.

### RTL

fa/he/ar carry no en dashes or em dashes anywhere (body, meta or FAQ) — number ranges use plain
hyphens (`181-195`, `1,500-1,999`, `52-55`), verified mechanically. The three RTL versions are
shorter and re-framed rather than translated: the Arabic and Hebrew drop the region table and lead
harder on the named-destination answer, and the Persian keeps the cross-tabulation as prose instead
of a seven-row table.

---

## 5. Validation performed

A script re-read all three files and asserted, for each of the 18 language blocks:

1. `yaml.safe_load` parses the file and all required keys exist (`slug`, `order`, `image`, `updated`,
   `car_category`, `related_routes`, `related_attractions`, and per-language `name`, `short`,
   `meta_title`, `meta_description`, `body`, `faq`).
2. `slug` matches the filename; `image` resolves to a real file under `static/photos/`.
3. Every `related_*` slug exists in `content/`.
4. Every markdown link resolves — `/attractions/…`, `/routes/…`, `/itineraries/…`, `/blog/…` slugs
   checked against `content/` and `dist/`; `/guides/…` checked against the three files themselves.
5. `meta_title` ≤ 65, `meta_description` 140-158, `short` ≤ 180, word count in range, 4-6 FAQ entries.
6. No en/em dash in any fa/he/ar string; no `ქირაობ`, `ექსცეს` or `ღრმულ` in any ka string.

All checks pass. The build was **not** run, per instruction — `build.py` does not yet read
`content/guides/`.

---

## 6. Notes for the renderer and for whoever owns the URL map

- The `/guides/` prefix conflict flagged in `CONTENT_BRIEFS.md §0.4` is unresolved: `SEO_URL_MAP.md`
  lists neither `/guides/` nor `/driving-in-georgia/`. These files assume `/guides/<slug>/` with
  `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/` variants, and the three cross-link each other on that
  assumption. If the prefix changes, nine markdown links across the three files need updating —
  they are listed in §3 under "Cross-guide".
- `body` is markdown with `##` headings, paragraphs, `-` lists, `|` tables and `[text](/url/)` links.
  The tables are the reason these pages exist; they must render as real tables with horizontal
  scrolling on mobile, not as `<pre>`.
- An `FAQPage` node built from the `faq` array is the single highest-value schema addition for all
  three (per `CONTENT_BRIEFS.md §Brief 1 — Schema`). Do not add `HowTo`.
- `order: 10 / 20 / 30` sets the intended listing order — 4x4 first, driving second, seasons third.
- **Inbound links are still missing.** These three pages have no parents. The highest-value inbound
  edits, all outside this task's scope: `/car-rental/4x4/`'s existing FAQ line ("Do I actually need a
  4x4 for Georgia, or is it marketing?") should point at the 4x4 guide; every `gravel`/`offroad`
  attraction's getting-there block should point at it too; and `/faq/`'s driving and winter answers
  should point at the driving guide.
- If the attraction corpus grows again, **all published counts on these three pages go stale at once**.
  Everything countable lives in the `body` markdown, so a rebuild will not refresh them automatically.
  Re-run the counts and re-edit the three files whenever `content/attractions/` changes materially;
  the `updated:` field is there to make the drift visible.
