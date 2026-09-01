# Day-trip guides: Tbilisi, Kutaisi, Batumi

**Written:** 2026-09-01 · **Files:** `content/guides/day-trips-from-{tbilisi,kutaisi,batumi}.yml` (orders 20, 21, 22) ·
**URL:** `/guides/{slug}/` in all six languages · **Schema:** identical to `do-i-need-a-4x4-in-georgia.yml`.

Three prose guides from the §5.3 editorial track (piece 2, "How far you can get from Tbilisi in a day",
extended to the two western pickup cities). Every number on the pages was computed from `build.ATTRACTIONS`
on 2026-09-01 by `scratchpad/daytrips.py` + `counts.py`; nothing was estimated by hand.

## 1. Method

| City | Drive-time source | Nature of the figure |
|---|---|---|
| Tbilisi | `distance_tbilisi_km`, `drive_time_tbilisi` on each record | **Exact** measured fields, the same ones shown on every attraction page |
| Kutaisi, Batumi | `_hav(city, place) × f / v`, where `(f, v) = build.road_model(place)` | **Estimate.** `f` = road km ÷ straight-line km from Tbilisi (winding factor, clamped 1.15–2.9); `v` = road km ÷ Tbilisi drive time (mean speed, clamped 18–80 km/h). Both are that place's own measured numbers, applied to the straight line from the western city. |

The pages say this in plain words in a "how these times are made" paragraph placed before the table, and repeat
it in the first FAQ. They also name the known failure mode: where a ridge separates the city from the place
(Kutaisi → Samtskhe over the Meskheti range; Batumi → Samtskhe over the Goderdzi ridge) the straight line is
short and the road is not, so Borjomi / Rabati / Abastumani / Zarzma rows are labelled "optimistic". No
alternative figure is invented for them.

City-own places are excluded from all counts (Tbilisi: `region == tbilisi`, 28; Kutaisi: 4 records with
estimate < 3 min; Batumi: 6 records with estimate < 4 min).

## 2. Measured counts (places outside the city, one-way)

| Band | Tbilisi (exact) | Kutaisi (est.) | Batumi (est.) |
|---|---|---|---|
| ≤ 1:30 | 42 (eco 37 · suv 5 · off 0) | 64 (eco 49 · suv 15 · off 0) | 33 (eco 26 · suv 7 · off 0) |
| 1:30–3:00 | 58 (41 · 15 · 2) | 63 (43 · 15 · 5) | 56 (39 · 12 · 5) |
| 3:00–5:00 | 74 (49 · 20 · 5) | 44 (16 · 20 · 8) | 37 (23 · 13 · 1) |
| **≤ 3:00** | **100 (78 · 20 · 2)** | **127 (92 · 30 · 5)** | **89 (65 · 19 · 5)** |
| ≤ 5:00 | 174 (127 · 40 · 7) | 171 (108 · 50 · 13) | 126 (88 · 32 · 6) |
| Outside city | 239 | 263 | 261 |

Road surface ≤ 3:00 — Tbilisi: paved 61 · mostly_paved 28 · gravel 10 · 4x4_only 1. Kutaisi: 75 · 40 · 10 · 2.
Batumi: 54 · 24 · 9 · 2. Open-all-year ≤ 3:00: Tbilisi 89/100, Kutaisi 107/127, Batumi 75/89.

Types ≤ 1:30 drive the section choice per city:

- **Tbilisi:** monastery 16, fortress 7, town 5, lake 3, archaeology 3 → sections: Mtskheta UNESCO trio,
  Kvemo Kartli fortresses, Gori/Uplistsikhe, Kakheti wine (1:30–3:00 band), Military Highway band by band,
  3–5 h "not a day trip".
- **Kutaisi:** monastery 15, museum 9, town 8, fortress 6, spa 4, cave 3, canyon 3, waterfall 3 → sections:
  20-minute ring, canyons & waterfalls, Racha, Samegrelo & coast, Guria mountains (off-road), east/south
  optimistic rows, Svaneti 3–5 h.
- **Batumi:** town 7, nature 6, monastery 6, beach 5, fortress 4 → sections: five beaches, fortresses &
  garden, four parks/reserves, Upper Adjara climb, Guria, Samegrelo/Imereti at two hours, 3–5 h.

## 3. Table picks (20 per city, by `rating` + type variety)

- **Tbilisi:** Svetitskhoveli, Jvari, Château Mukhrani, Gori, Birtvisi, Algeti NP, Didgori, Ananuri,
  Uplistsikhe, Dashbashi, David Gareja, Sighnaghi, Bodbe, Gudauri, Borjomi, Kvareli, Truso, Gergeti, Rabati, Vardzia.
- **Kutaisi:** Motsameta, Gelati, Sataplia, Tskaltubo, Prometheus, Okatse, Martvili, Kinchkha, Khvamli,
  Katskhi, Nokalakevi, Nikortsminda, Chiatura, Shaori, Khvanchkara, Ureki, Kolkheti NP, Bakhmaro, Mestia, Ushguli.
- **Batumi:** Botanical Garden, Gonio, Kvariati, Petra, Machakhela, Mtirala, Kobuleti, Makhuntseti, Keda,
  Ureki, Kintrishi, Kolkheti NP, Gomismta, Dumbadze museum, Bakhmaro, Khulo, Prometheus, Gelati, Goderdzi, Vardzia.

Table columns: drive · (km, Tbilisi only) · `visit_hours` · `road` · `car_category` · `best_season`.

## 4. Rules applied

- Every fact comes from a YAML field (`road`, `car_category`, `best_season`, `open_year_round`,
  `visit_hours`, `elevation`, `rating`, `unesco`, route `days`/`distance_km`/`car_category`). No fees, prices,
  deposit, insurance or opening hours. Commercial links only: `/car-rental/{city}/`, `/car-rental/{economy,suv,4x4}/`.
- `/day-trip/` linked as the interactive tool; cross-links to the other two guides, to
  `/guides/do-i-need-a-4x4-in-georgia/`, region pages and existing routes/itineraries.
- Georgian: company voice `გაქირავება` only (validator greps for `ქირაობ`); place names declined
  (`თბილისიდან`, `ქუთაისიდან`, `ბათუმიდან`).
- RTL (fa/he/ar): no dash inside number ranges — seasons written as "مه تا اکتبر", "מאי עד אוקטובר",
  "مايو إلى أكتوبر"; drive times as `h:mm`.
- Length (validator, links stripped): en/ka/ru 1 055–1 268 words; fa/he/ar 817–898 words.
  `meta_title` ≤ 61 chars incl. " | RentUp"; `meta_description` 140–157 chars; 5–6 FAQ per language.

## 5. Validation performed

`scratchpad/validate.py {city}`:

1. `yaml.safe_load` parses; `image` exists in `dist/assets/photos/`; `related_routes` / `related_attractions` exist.
2. Every `/attractions/`, `/routes/`, `/regions/`, `/guides/`, `/car-rental/`, `/itineraries/` link resolves to a
   real slug or built directory. (0 bad links across 18 language bodies + FAQs.)
3. Every `h:mm` token that follows an attraction link is compared with the computed figure for that slug
   (exact for Tbilisi, estimate for the others). All match; the only flag is a deliberate "0:54 to 0:58" range.
4. `build.guide_quality_ok()` returns True for all 3 × 6.

Known limitation to state if asked: Tbilisi figures were first drafted from the estimate column by mistake
and were rewritten programmatically against `drive_time_tbilisi`; the validator in step 3 is what guarantees
the published values are the exact fields.
