# New SEO category pages: business and van — 2026-08-30

## Scope

Added two entries to `content/settings/seo_categories.yml` — `business` and `van` — completing
the set of six landing pages implied by `content/settings/categories.yml`'s six fleet
categories (economy, suv, business, offroad, minivan, van). Only `economy`, `suv`, `offroad`
(public slug `4x4`) and `minivan` existed before this pass. All copy is in all 6 languages
(ka/en/ru/fa/he/ar), in the same shape and voice as the four existing entries. No other file
was modified except this report.

## Real car data behind each new page

### `business` (public slug `/car-rental/business/`)

Source: `content/cars/toyota-camry.yml`, `mercedes-benz-e-class.yml`, `bmw-5-series.yml`.

| Car | Seats | Luggage | Clearance | Fuel (l/100km) | price_1_6 | Deposit |
|---|---|---|---|---|---|---|
| Toyota Camry (2.5 hybrid, FWD) | 5 | 3 | 145 mm | 5.5 | 210 ₾ | 1000 ₾ |
| Mercedes-Benz E-Class (2.0 diesel, RWD) | 5 | 3 | 130 mm | 6.2 | 290 ₾ | 1000 ₾ |
| BMW 5 Series (2.0 petrol, RWD) | 5 | 3 | 135 mm | 7.5 | 310 ₾ | 1000 ₾ |

Computed `data:` block: `price_from_gel: 210` (cheapest car's `price_1_6`, same rule the four
existing entries use), `seats_range: "5"`, `luggage_range: "3"`, `clearance_range: "130-145"`.
Deposit (1000 ₾), excess (1000 ₾) and SCDW (25–45 ₾/day → 0) come from
`content/pages/pricing.yml`'s "Deposit and excess by category" table, which agrees exactly with
every car's own `deposit:` field. Minimum age (25) and licence experience (5 years) come from
`content/pages/terms.yml`'s age/experience table ("Business class — 25 years — 5 years — 25
₾/day surcharge for ages 25–27"); the young-driver surcharge itself was **not** added to
`terms_note`, matching the fact that none of the four existing category entries state it either
(kept for consistency of shape, not because it's untrue).

**Positioning called out honestly:** all three business cars sit at 130–145 mm clearance — the
*same range as economy (135–145 mm), and BMW/Camry are within it while the E-Class (130 mm) is
actually below economy's floor*. So the copy never claims business is more capable off-road; it
says plainly that clearance is "the same range as economy or lower" and that Ushguli/Omalo stay
reserved for the 4x4 class regardless of price. The class is sold on comfort and presentation
(quiet cabin, adaptive cruise control on the E-Class, RWD handling on the BMW, chauffeur service
— genuinely offered on all three car pages, unlike most other categories) for corporate travel,
delegations, weddings and airport pickups.

### `van` (public slug `/car-rental/van/`, "Commercial van" per `categories.yml`)

Source: `content/cars/ford-transit.yml`, `mercedes-benz-sprinter.yml`.

| Car | Seats | Cargo volume | Payload | Clearance | Fuel (l/100km) | price_1_6 | Deposit |
|---|---|---|---|---|---|---|---|
| Ford Transit (2.0 diesel, manual, FWD) | 3 | 11 m³ | 1,200 kg | 170 mm | 9.5 | 185 ₾ | 800 ₾ |
| Mercedes-Benz Sprinter (2.1 diesel, manual, RWD) | 3 | 14 m³ | 1,500 kg | 175 mm | 10.5 | 215 ₾ | 800 ₾ |

Computed `data:` block: `price_from_gel: 185`, `seats_range: "3"`, `luggage_range: "11-14 m³"`
(unit called out explicitly — this is cargo volume, not the suitcase count every other category
uses, and it would be misleading to present it as a bare number), `clearance_range: "170-175"`.
Deposit/excess 800 ₾ and SCDW → 0 match `pricing.yml`'s "Commercial van" row exactly. Minimum
age 25 / licence 3 years, no young-driver surcharge, per `terms.yml`'s table row for "Commercial
van." Both car bios state that cargo damage is excluded from the standard cover and that
third-party courier/haulage work needs written consent in advance — both facts are carried into
`terms_note`/`limitations` since they are genuinely distinctive commercial terms for this class.

**Correction to the brief:** the task description characterized `van` as "maximum passengers and
luggage." That is not what the data says — `van` (Ford Transit, Mercedes-Benz Sprinter) is a
**3-seat cargo category**; the 7–9-seat, passenger-maximizing vehicles are the *already-existing*
`minivan` category (Staria/Vito/Alphard). Writing `van` copy as a passenger-capacity class would
have been an invented fact, so it was written honestly instead: van = maximum cargo volume and
payload, explicitly not a passenger or group-travel option, with FAQs pointing anyone who needs
people capacity to the minivan class instead.

## Routes/attractions join

`docs/seo/INTERNAL_LINKING_REVIEW.md` §12 documents that `route.car_category` /
`attraction.car_category` are only ever `economy`, `suv` or `offroad` — road-surface tags — so
`minivan` (a party-size category) can never win that join directly, and proposes a substitute:
routes where **every** waypoint is `paved`/`mostly_paved` **and** `max_people >= 7` (22 of 32
routes) can honestly link to minivan as a group-travel option.

That substitute join was checked against `business` and `van` and **does not hold for either**:
`business` cars seat 5 (not ≥7), and `van` seats only 3 in the cab (it's a cargo category, not a
passenger one, so party size isn't even the right axis to join on). No other field in
`content/routes/*.yml` or `content/attractions/*.yml` ties to a comfort tier or a cargo vehicle
either. Rather than borrow minivan's routes, invent a new join, or leave the page thin without
saying why, both `business.data.route_slugs`/`attraction_slugs` and `van.data.route_slugs`/
`attraction_slugs` were left as empty lists (`[]`), exactly like minivan's own current, honest
state, and the file's header comment was extended to explain why for all three categories. The
`when_to_choose`/`limitations` prose for both new categories names roads by description (e.g.
"the Tbilisi–Batumi motorway," "the curves between Gudauri and Kazbegi," "Batumi or the port at
Poti") rather than linking to specific route/attraction pages, since none is genuinely tagged for
either class.

## Facts refused / not claimed

- No young-driver surcharge line added to `business`/`van` `terms_note`, even though `terms.yml`
  states one for business (25 ₾/day, ages 25–27) — omitted only to match the shape of the four
  existing entries, which also omit it for SUV/minivan despite `terms.yml` stating a surcharge
  for them too. This is a shape-consistency choice, not a suppressed fact — the surcharge is
  real and is documented here for the record.
- Did not claim business class has better road capability than economy — the data says the
  opposite (E-Class's 130 mm clearance is below economy's 135 mm floor).
- Did not claim van accommodates passengers/groups — it seats 3; copy says so plainly and
  redirects to minivan.
- Did not invent a maximum rental length, a WiFi router extra, or "full insurance coverage" —
  none of these exist for any category per `docs/seo/FACT_RECONCILIATION.md`, and this pass
  didn't reintroduce them for the new categories either.
- Did not touch `build.py`, `content/pages/*`, `content/settings/rental_policy.yml`, or the
  existing `economy`/`suv`/`offroad`/`minivan` entries, per the task's file-write restriction —
  including the existing entries' `ექსცესი` (should be `ფრანშიზა`) wording, which is
  pre-existing technical debt outside this task's editable-file list. The two new Georgian
  entries use `ფრანშიზა` throughout, as instructed, so this introduces a temporary
  inconsistency with the four older entries until that separate cleanup happens.

## Why `/car-rental/business/` and `/car-rental/van/` don't exist in the build yet

`build.py` already knows the URL shape for both categories —
`CATEGORY_SLUG = {"economy": "economy", "suv": "suv", "offroad": "4x4", "minivan": "minivan",
"business": "business", "van": "van"}` (build.py, `CATEGORY_SLUG` dict) — but four separate
hardcoded tuples still read `("economy", "suv", "offroad", "minivan")` and don't include
`business`/`van`:

- **`build.py:2992`** — `sitemap_children()`, builds the `car-rental` sitemap entries.
- **`build.py:3082`** — `llms_full_txt()` (or equivalent llms.txt builder), lists category pages.
- **`build.py:3599`** — `render_car_rental_hub()`, the `order` list of category cards shown on
  the `/car-rental/` hub page.
- **`build.py:4760`** — the main page-generation loop in `main()`, which actually calls
  `render_rental_category(lang, _k)` and writes the HTML file. This is the one that matters for
  `/car-rental/business/index.html` / `/car-rental/van/index.html` to exist at all.

Each of these four lines needs `"business", "van"` appended to its tuple/list literal. This repo
task's file-write list is limited to `content/settings/seo_categories.yml` and this report, so
`build.py` was left untouched — confirmed by direct verification instead: importing `build.py`
and calling `build.rental_quality_ok("category", build._seo_cats()["business"])` /
`["van"]` both return `True` (each has ≥2 `car_slugs`), and calling
`build.render_rental_category("en"/"ka", "business"/"van")` directly produces full, correct HTML
(unique `<title>`, one `<h1>`, 4 FAQ entries, no leaked `4x4_only`/`mostly_paved` tokens) — so the
content is ready and only that one-line-times-four change in `build.py` is needed to ship it.

## Verification

- `python3 build.py --validate-only` → `✔ content validation passed` (same pre-existing,
  unrelated warning as before this change: 17 car records with no main image).
- `python3 build.py /tmp/cat` → `✔ 2292 HTML pages (17 cars, 4 articles, 6 languages)` — same
  page count as before this change, confirming `/car-rental/business/` and `/car-rental/van/`
  are **not** generated yet (expected — see above). `/tmp/cat/car-rental/business/` and
  `/tmp/cat/car-rental/van/` do not exist.
- `python3 scripts/seo_audit.py /tmp/cat` → **0 ERROR**, 2 WARN (pre-existing, unrelated:
  `/ka/trip-planner/` and `/ru/trip-planner/` title length), 20 INFO (pre-existing noindex-page
  notices) — identical to the baseline recorded in `docs/seo/PROSE_ALIGNMENT.md`, confirming this
  change introduced no regressions.
- Direct in-process check (`import build`) confirms both new categories pass
  `rental_quality_ok("category", ...)` and render correctly in all languages once the four
  `build.py` tuples above are extended.

## Summary (10 lines)

1. Added `business` and `van` entries to `content/settings/seo_categories.yml`, all 6 languages, matching the existing four entries' structure and voice exactly.
2. `business` data (BMW 5 Series, Mercedes-Benz E-Class, Toyota Camry): price from 210 ₾/day, 5 seats, 3 suitcases, 130–145 mm clearance, 1000 ₾ deposit/excess — all read from `content/cars/*.yml` and `pricing.yml`/`terms.yml`.
3. `van` data (Ford Transit, Mercedes-Benz Sprinter): price from 185 ₾/day, 3 seats, 11–14 m³ cargo, 170–175 mm clearance, 800 ₾ deposit/excess — same sourcing.
4. Positioning is honest: business is sold on comfort/presentation, explicitly noting its clearance is at or below economy's, not superior to it; van is sold on cargo volume and payload, explicitly not a passenger/group option.
5. Corrected an inaccurate premise in the task brief: `van` is a 3-seat cargo category, not a passenger-maximizing one — that description fits the already-existing `minivan` category instead.
6. Checked `docs/seo/INTERNAL_LINKING_REVIEW.md`'s minivan route/attraction join (all-paved + max_people ≥ 7) against business (5 seats) and van (3 seats, cargo) — it holds for neither, so both got empty `route_slugs`/`attraction_slugs`, same honest-vacuum treatment as minivan, with the reasoning documented in the file's header comment.
7. Commercial terms (age, licence years, insurance framing, excess amounts) match `content/pages/terms.yml`/`pricing.yml` exactly; CDW+TPL are stated as included together with the per-category excess, never "zero excess" or "full coverage."
8. Georgian text uses `გაქირავება`/`ჯავშანი` correctly, avoids `ქირაობა`, and uses `ფრანშიზა` (not `ექსცესი`) — noting this creates a temporary inconsistency with the four pre-existing entries, which still say `ექსცესი` and are out of this task's scope to fix.
9. `fa` uses Persian digits and spells ranges with "تا" (no dash); `he`/`ar` use a plain hyphen in number ranges, never an en dash.
10. `build.py --validate-only` passes; a full build produces the same 2292-page count as before (business/van pages are not yet generated — four hardcoded category tuples at `build.py:2992/3082/3599/4760` need `"business", "van"` appended); `seo_audit.py` reports 0 ERROR, unchanged from baseline; direct rendering checks confirm the new content is correct and ready once that one-line-times-four change lands.
