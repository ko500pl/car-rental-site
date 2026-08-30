# On-Page SEO Review — eight page templates, ka / en / ru (+ ar / he / fa spot-check)

Reviewed against the **built output in `dist/`**, not against the source templates.
Date: 2026-08-29. Build audited: `python3 scripts/seo_audit.py` → 0 ERROR / 247 WARN / 20 INFO.

Scope: title, meta description, H1 + heading hierarchy, keyword & semantic coverage,
intro copy, image alt text, above-the-fold clarity, internal-link anchors — for
Home, Car-rental hub, Car-rental location, Car-rental category, Vehicle, Attraction,
Route, Itinerary (+ itineraries hub).

---

## 0. Executive summary

Content quality on this site is genuinely good — the attraction, route, category and
vehicle **body copy reads like a person wrote it**, in all three primary languages, with
real numbers pulled from the data files. The problems are almost entirely in the
**generated metadata layer** and in **six shipped rendering bugs**, not in the prose.

Six things are broken in the built HTML right now and are visible to users and to Google:

| # | Bug | Blast radius |
|---|-----|--------------|
| B1 | Literal `{days} {km} {stops}` in the itinerary meta description | 5 itineraries × 6 langs = **30 pages** |
| B2 | Literal `{place}` in a visible `<h2>` on every car-rental location page | 6 places × 6 langs = **36 pages** |
| B3 | Route + region meta descriptions are raw body text cut mid-sentence — `seo_meta()`'s description is computed and thrown away | 32 routes + 11 regions × 6 langs ≈ **258 pages** |
| B4 | `photo_by:` — a raw YAML key — printed as visible caption text | **1,488 pages** |
| B5 | Georgian and Russian case/agreement broken in generated car-rental titles (`ბათუმი-ში`, `თბილისიის`, `ეკონომ კლასი-ის`, `Аренда Эконом-класс`, `3 моделей`) | **60 pages** |
| B6 | Malformed HTML `<div class="wrap"<div class="cta">` on every route page | **192 pages** |

And the single highest-leverage finding:

> **`content/settings/seo_car_rental.yml` and `content/settings/seo_categories.yml` already
> contain hand-written, grammatical, differentiated `meta_title` / `meta_description` for
> every car-rental hub / location / category page in all six languages — and `build.py`
> discards them**, because `seo_meta()` is consulted first and `L.get("meta_title")` is only
> reached when the generated template returns empty (`build.py:3463`, `3533`, `3587`).
> Inverting that precedence fixes B5 outright and replaces 60 near-duplicate generated
> titles with 60 unique human ones. It is a three-line change.

### Priority counts

| | P0 | P1 | P2 |
|---|---|---|---|
| Findings | 9 | 17 | 12 |

### On the known "245–257 titles over 70 chars" issue

**The stated cause is wrong.** It is not an ar/he/fa problem. Measured on the current build
(275 over-70 titles once noindex pages are excluded):

| lang | attractions | routes | other | total |
|---|---|---|---|---|
| **ka** | 90 | 5 | 1 | **96** |
| **ru** | 62 | 4 | 1 | **67** |
| **en** | 60 | 6 | 0 | **66** |
| fa | 17 | 1 | 0 | 18 |
| he | 16 | 3 | 0 | 19 |
| ar | 9 | 0 | 0 | 9 |

Georgian, Russian and English are **84% of the problem**; the RTL languages are 17%.
Longest offenders are `ka` 121 chars, `ru` 105, `en` 99. See §10 for the fix and the
measured before/after. Short version: a guarded clause-trim in `seo_meta()` takes
275 → 1 with no template edits at all, and shortening the ka/en/ru attraction templates
reduces how often that trim has to fire (en 42→16, ka 90→36, ru 62→4 titles trimmed).

---

## 1. Home — `dist/index.html`, `dist/ka/index.html`, `dist/ru/index.html`

**Target intent:** commercial + navigational ("car rental Georgia", "საქართველოში მანქანის ქირაობა", "аренда авто Грузия").

| Element | Built value | Verdict |
|---|---|---|
| Title en | `Car Rental & Georgia Road Trip Planner \| RentUp` (51) | Good. Keyword first, brand last, unique. |
| Title ka | `ავტომობილის დაქირავება და მარშრუტის დაგეგმვა საქართველოში \| RentUp` (66) | Fits. But uses `დაქირავება` while every H1 and body on the site uses `გაქირავება` — see F-KA-1. |
| Title ru | `Аренда авто и планировщик поездок по Грузии \| RentUp` (52) | Good. |
| Desc en/ka/ru | 138 / 146 / 136 chars | Good length, concrete numbers (75 ₾, 257 places, 32 trips), reads human. No explicit CTA verb in en ("Rent a car…" is imperative — fine). |
| **H1** | en `What is your plan for today?` · ka `რა გეგმა გაქვს დღეს?` · ru `Какие планы на сегодня?` | **P0.** Zero keyword. The site's most-linked page announces nothing about car rental or Georgia. |
| Hierarchy | H1 → 20× H2 → H3 — no skips | Good. |
| Above the fold | Hero image + conversational H1 + 4 action cards | The page's actual value proposition ("rent a car anywhere in Georgia from 75 ₾/day, plan your route on the same site" — already in the meta description) is nowhere above the fold. |
| Images | 10 `<img>`, **6 with `alt=""`** including `rentup-header-logo.png` and the hero `rentup-hero2.jpg` | P1. Logo needs `alt="RentUp"`; hero is arguably decorative but currently the largest image on the site carries no text. |
| Internal anchors | 31 links; **4× "View", 3× "Details"** | P1. Generic anchors on the site's strongest page. |
| Missing links | No link to `/itineraries/`, `/attractions/`, `/regions/` | P1 — see F-IL-1. |

### Findings

**F-HOME-1 (P0) — H1 carries no keyword.**
`build.py:3094` (ka), `:3100` (en), `:3106` (ru); duplicated at `build.py:3964–3969`.
Keep the conversational line as a kicker `<p>`, promote a keyword-bearing H1. Replacement text
(all three restate the page's own existing title/description — no new claims):

```python
# build.py:3094 / 3100 / 3106 — LAND_UI
"ka": {"h1": "იქირავეთ ავტომობილი და დაგეგმეთ მარშრუტი საქართველოში",   # 53
       "kicker": "რა გეგმა გაქვს დღეს?", ...
"en": {"h1": "Rent a car in Georgia and plan the route",                # 40
       "kicker": "What is your plan for today?", ...
"ru": {"h1": "Аренда авто в Грузии и планировщик маршрутов",            # 44
       "kicker": "Какие планы на сегодня?", ...
```
Apply the same pair to `_DOA_LAND_T` at `build.py:3964–3969` so the app shell stays in sync.

**F-HOME-2 (P0) — nonsense Georgian word on the homepage.**
`build.py:3098` and `build.py:3965`: `"c4t": "განვერიანდი Community-ში"`.
`განვერიანდი` is not a Georgian word (the verb is `გაერთიანდი` / formal `გაერთიანდით`), and
`Community` is left untranslated inside a Georgian sentence. Rendered verbatim in
`dist/ka/index.html`. Replacement: `"c4t": "შემოგვიერთდით საზოგადოებაში"`.

**F-HOME-3 (P1) — logo and hero have empty alt.**
`build.py:836` (`logo`), `build.py:3210` and `build.py:4129` (hero).
Logo → `alt="RentUp"` and drop `aria-hidden="true"` (it is inside the site-name link).
Hero → `alt` from the same source as the H1, or keep `alt=""` **and** add
`<img ... alt="" role="presentation">` deliberately; do not leave it ambiguous.

**F-HOME-4 (P1) — generic anchors "View" / "Details".**
Replace with the target's own name, e.g. `View` on the fleet card → `See all 17 rental cars`,
`Details` on a tour card → the route name. Georgian: `ნახეთ ყველა ავტომობილი`; Russian:
`Посмотреть весь автопарк`.

**F-HOME-5 (P2) — register mismatch in Georgian.** See §9.

---

## 2. Car-rental hub — `dist/car-rental/index.html` (+ ka, ru)

Strongest commercial page on the site: **1,241 words en / 983 ka**, 15 H2 sections covering
booking, eligibility, deposit, mileage, fuel, insurance, delivery, one-way, extras,
cancellation, support, FAQ. Content is excellent.

| Element | Built value | Verdict |
|---|---|---|
| Title en | `Car Rental in Georgia \| RentUp` (30) | Too short — 30 of ~60 usable chars wasted, no differentiator. |
| Title ka | `მანქანის დაქირავება საქართველოში \| RentUp` (41) | Same, plus `დაქირავება` vs H1's `გაქირავება`. |
| Title ru | `Аренда автомобиля в Грузии \| RentUp` (35) | Same; H1 says `Аренда авто`. |
| Desc | 136 / 140 / 124 | Fine, but generic — it lists what the terms sections already say. |
| **Hand-written alternative (discarded by build)** | en `Car Rental in Georgia — Unlimited Mileage, No Hidden Fees \| RentUp` (66) · ka `მანქანის ქირაობა საქართველოში — შეუზღუდავი გარბენი \| RentUp` (59) · ru `Аренда авто в Грузии — без ограничения пробега \| RentUp` (55) | **Strictly better.** Present at `seo_car_rental.yml:159`+, unused. |
| H1 | matches title concept | OK |
| Hierarchy | H1 → H2 `Cars in this category` → H3 category names | **Wrong label** — this is a hub, not a category. |
| Duplicate H2 | ka H1 `მანქანის გაქირავება საქართველოში` **=** H2 `მანქანის გაქირავება საქართველოში` verbatim | P1 |
| Images | **1** — the logo, `alt=""` | P1. Zero content images on the top money page. |
| Untranslated | H2 `FAQ` in ka / ru / fa / he / ar | P1 |

### Findings

**F-HUB-1 (P0) — hand-written metadata is overridden by a generic template.**
`build.py:3462–3464`:
```python
title, desc = seo_meta("car_rental_hub", lang, count=len(CARS), price=cheapest_price("economy"))
title = title or h.get("meta_title") or f'{h.get("h1", "")} | {BRAND}'
desc  = desc  or h.get("meta_description", "")
```
`seo_meta()` always returns non-empty here, so the human text never wins. Invert:
```python
title, desc = seo_meta("car_rental_hub", lang, count=len(CARS), price=cheapest_price("economy"))
title = h.get("meta_title") or title or f'{h.get("h1", "")} | {BRAND}'
desc  = h.get("meta_description") or desc
```
Same three-line change at `build.py:3533–3534` (location) and `build.py:3587–3588` (category).
This resolves B5 and F-LOC-1/F-CAT-1/F-CAT-2 in one go.
Before shipping, trim the hand-written descriptions to ≤160 chars — they run 142–211 today.
Exact trimmed text in Appendix A.4.

**F-HUB-2 (P1) — H2 "Cars in this category" on a hub page.**
`content/settings/seo_ui.yml:102` (`cars_in_category`) is reused for the hub's category grid.
Add a distinct key and use it on the hub. Exact YAML in Appendix A.2.

**F-HUB-3 (P1) — H1 and a body H2 are byte-identical in Georgian.**
`content/settings/seo_car_rental.yml:156` (h1) vs. the prose section heading. Change the prose
H2 to a narrower phrase, e.g. ka `როგორ ვაქირავებთ ავტომობილს` / en `How renting works with RentUp`
/ ru `Как устроена аренда у RentUp`.

**F-HUB-4 (P1) — `FAQ` hard-coded in English.**
`build.py:3459`, `:3580`, `:3782` all pass the literal `"FAQ"` to `_sec()`.
Replace with `su("faq_title", lang)` and add the key (Appendix A.2).

**F-HUB-5 (P1) — no images at all.** Add the fleet-card thumbnails (they exist: `c["image"]`
is used on other pages at `build.py:3286`) with real alt text — see F-IMG-1.

**F-HUB-6 (P1) — two commercial categories have no landing page.**
`content/settings/categories.yml` defines six categories (`economy, suv, business, offroad,
minivan, van`) but only four have `/car-rental/{cat}/` pages. `business` and `van` are
unserved commercial keywords, and the hub description's "6 vehicle categories" points at a
grid that shows four.

---

## 3. Car-rental location — `dist/car-rental/tbilisi-airport/`, `dist/car-rental/batumi/`

Content is good (369 words en at the airport, a specific 30 ₾ meet-and-greet hook), and the
internal-link block to nearby routes and attractions is genuinely useful.

| Element | tbilisi-airport | batumi |
|---|---|---|
| Title en | `Tbilisi Airport Car Rental (TBS) \| RentUp` (41) | `Car Rental in Batumi \| RentUp Georgia` (37) |
| Title ka | `თბილისიის აეროპორტში მანქანის დაქირავება (TBS) \| RentUp` (55) | `მანქანის დაქირავება ბათუმი-ში \| RentUp` (38) |
| Title ru | — | `Аренда авто в Батуми \| RentUp` (29) |
| H1 | `Car Rental at Tbilisi Airport` / ka `მანქანის გაქირავება თბილისის აეროპორტში` | `Car Rental in Batumi` / ka `მანქანის გაქირავება ბათუმში` |
| Images | 1 (logo, `alt=""`) | 1 |

### Findings

**F-LOC-1 (P0) — literal `{place}` in a rendered `<h2>` on all 36 location pages.**
`build.py:3505` calls `su("popular_routes_from", lang)` and never substitutes the placeholder
defined at `content/settings/seo_ui.yml:46–52`. Output today, verbatim:
`Popular road trips from {place}` · `პოპულარული მარშრუტები {place}-დან` ·
`Популярные маршруты из {place}` · `מסלולי טיול פופולריים מ{place}` · `رحلات برية شائعة من {place}`.
Fix at `build.py:3505`:
```python
+ (_sec(su("popular_routes_from", lang).replace("{place}", place.get(lang, place.get("en", key))),
```
Note the Georgian string then still produces `ბათუმი-დან`; see F-KA-2 for the full fix.

**F-LOC-2 (P0) — Georgian case endings are hyphenated onto native nouns.**
`content/settings/seo_meta.yml:1012` (`{city}-ში`) and `:1031` (`{city}ის აეროპორტში`) produce
`ბათუმი-ში`, `თბილისი-ში`, `ქუთაისი-ში` and `თბილისიის`, `ბათუმიის`, `ქუთაისიის` — all
ungrammatical. The correct forms are `ბათუმში`, `თბილისში`, `ქუთაისში` and `თბილისის`,
`ბათუმის`, `ქუთაისის`. Confirmed in all six built location titles. The page's own **H1s are
correct** (`seo_car_rental.yml:883`, `:1078`, `:1278`, `:1471`), so the fastest correct fix is
F-HUB-1 (prefer `meta_title`). YAML for the fallback templates in Appendix A.1.

**F-LOC-3 (P1) — brand suffix inconsistency.**
`seo_meta.yml:1009` uses `| RentUp Georgia` for the en *city* variant while every sibling —
including the en *airport* variant at `:1028` — uses `| RentUp`. `brand:` is declared as
`RentUp` at `seo_meta.yml:27`. Make it `| RentUp`.

**F-LOC-4 (P1) — the same five attractions are rendered twice on the page.**
`build.py:3506–3512`: `_rental_distance_table(..., nearest_attraction_slugs)` inside the
"Popular road trips" section and `_attr_links(..., nearest_attraction_slugs)` in the
"Nearby places" section list the identical slugs. On `/car-rental/tbilisi-airport/` that is
10 links to 5 URLs. Drop the second block, or feed the two blocks different slug sets.

**F-LOC-5 (P1) — mislabelled H2 "Best car for this trip".**
`build.py:3509` uses `su("best_car_for_trip")` — a *route* label — on a location page where
there is no "this trip". Use a location-scoped key (Appendix A.2):
en `Car categories available in {place}` / ka `ხელმისაწვდომი კატეგორიები` / ru `Доступные категории`.

**F-LOC-6 (P2) — "1 days · 9 km".**
`build.py:3301` interpolates `{r["days"]} {tu(lang,"days")}` with no plural rule; produces
`1 days` in en and `1 дней` / `2 дней` in ru. Add a `plural(n, lang)` helper, or at minimum
special-case `n == 1`.

**F-LOC-7 (P2) — thin unique copy.** Of 369 words on the airport page only ~90 are unique to
the location (the pickup paragraph); the rest is card text. Each location page should carry a
second unique section — the terms that differ by location (delivery fee, night surcharge,
one-way) already exist in the data and are partially written.

---

## 4. Car-rental category — `dist/car-rental/4x4/index.html` (+ ka, ru)

Best-structured page in the audit: **629 words**, 15 internal links, all of them contextual
and none generic. The prose reasons from the site's own route data ("RentUp's own route list
assigns the Tusheti Highland Hike and all three Svaneti routes to this class").

| Element | Built value |
|---|---|
| Title en | `Off-road 4x4 Rental in Georgia — from 240 ₾/day \| RentUp` (56) |
| Title ka | `მაღალი გამავლობის 4x4-ის დაქირავება საქართველოში — 240 ₾-დან \| RentUp` (69) |
| Title ru | `Аренда Внедорожник 4x4 в Грузии — от 240 ₾/день \| RentUp` (56) |
| Desc ru | `3 моделей категории Внедорожник 4x4 в Грузии от 240 ₾ в день: …` |
| H1 en | `4x4 / Off-Road Rental in Georgia` |
| Images | 1 (logo) |

### Findings

**F-CAT-1 (P0) — Russian titles are ungrammatical on all four category pages.**
`content/settings/seo_meta.yml:1058` — `"Аренда {category} в Грузии"` inserts the label in the
nominative, producing `Аренда Внедорожник 4x4`, `Аренда Эконом-класс`, `Аренда Минивэн`,
`Аренда Кроссовер / SUV`. Russian requires the genitive after «аренда». The page's own H1
(`Аренда 4x4 / внедорожника в Грузии`) is correct. Additionally `:1059` produces
`3 моделей` — after 2–4, Russian takes the genitive **singular** (`3 модели`).

**F-CAT-2 (P0) — Georgian category titles are ungrammatical on all four pages.**
`content/settings/seo_meta.yml:1055` — `{category}-ის` produces `ეკონომ კლასი-ის`,
`მინივენი-ის` (correct: `ეკონომ კლასის`, `მინივენის`). The hyphen form is only valid after a
Latin-script or numeral token, which is why `4x4-ის` and `SUV-ის` happen to read correctly and
the two native-word categories do not. `:1056` similarly yields `3 ეკონომ კლასი მოდელი`
instead of `ეკონომ კლასის 3 მოდელი`.

Both are resolved by F-HUB-1 — `seo_categories.yml` already holds correct hand-written
`meta_title` for all 4 categories × 6 languages. Two caveats before promoting them:
they end `— RentUp.ge` / `– RentUp.ge` (en-dash in en) instead of the site-wide `| RentUp`,
and they use a third Georgian term, `გაქირავება`. Normalise both — Appendix A.4.

**F-CAT-3 (P1) — internal data key leaking into prose.**
`/car-rental/4x4/` renders, twice: *"roads that our own route and attraction data marks as
gravel or `4x4_only`"*. `4x4_only` is a YAML enum value, not English. Replace with
"4x4-only" in en, `მხოლოდ 4x4` in ka, `только 4x4` in ru. Source: the category body in
`content/settings/seo_categories.yml` (offroad block, ~line 574 en / 529 ka / 615 ru).

**F-CAT-4 (P1) — mislabelled H2 "Best car for this trip"** on a category page.
`build.py:3569` — same key and same fix as F-LOC-5 (`build.py:3509`); here it should read en `When to choose 4x4` / ka `როდის ავირჩიოთ 4x4` /
ru `Когда выбирать 4x4`.

**F-CAT-5 (P1) — no images.** Three cars are listed by name with prices and zero photos, on a
page whose whole job is to make someone choose a vehicle class. `c["image"]` exists.

**F-CAT-6 (P2) — title ↔ H1 label drift.** Title says `Off-road 4x4 Rental`, H1 says
`4x4 / Off-Road Rental`. `cat_label()` and the `seo_categories.yml` `h1` are two different
label sources. Pick one.

---

## 5. Vehicle — `dist/fleet/toyota-rav4/index.html` (+ ka, ru)

Note: vehicle pages live at `/fleet/{slug}/`, not `/cars/{slug}/`.

The 331-word body is the best writing on the site — specific, honest, and it names the exact
limitation of the vehicle ("this is a crossover, not an off-road vehicle"). Everything around
it is bare.

| Element | Built value | Verdict |
|---|---|---|
| Title en | `Toyota RAV4 Rental in Georgia — from 145 ₾/day \| RentUp` (55) | Good. |
| Title ka | `Toyota RAV4-ის დაქირავება საქართველოში — 145 ₾-დან \| RentUp` (59) | Grammatical — the hyphen is correct here because `RAV4` is Latin/numeric. |
| Title ru | `Аренда Toyota RAV4 в Грузии — от 145 ₾/день \| RentUp` (52) | Good — proper nouns don't decline. |
| Desc | 135 / 119 / 121 | Good, human, includes category + seats + price + insurance + mileage. |
| **H1** | `Toyota RAV4` | **P0.** No intent keyword at all. |
| Hierarchy | H1 → H2 `Booking and enquiries` → H2 `Book a car`. **Two H2s on the whole page.** | P0. |
| Images | **1** — the logo. **No photo of the car.** | P0. |
| Internal links | **3**: `/fleet/` ×2, `/contact/` ×1 | P0. |
| Above the fold | Spec strip + price + surcharge note | Good, actually. |

### Findings

**F-VEH-1 (P0) — H1 is the bare model name.**
`build.py:1356`: `<h1>{E(L['name'])}</h1>`. The H1 should carry the transactional phrase the title already uses.
Replacement, using values already on the page:
`en: Toyota RAV4 rental in Georgia` · `ka: Toyota RAV4-ის ქირაობა საქართველოში` ·
`ru: Аренда Toyota RAV4 в Грузии`. Generic form: `f'{L["name"]} {su("rental_in_georgia", lang)}'`.

**F-VEH-2 (P0) — no image of the vehicle.** (`render_car`, `build.py:1310–1400`)
Every other card grid on the site renders `c["image"]` (`build.py:3286`). The detail page for
that same car renders none. Add a hero `<figure>` with
`alt="{name} — {category}, {seats} seats, rental in Georgia"` (all four values already exist
on the page), and add `image` to the `Car`/`Product` JSON-LD node.

**F-VEH-3 (P0) — three internal links, two of them the same generic anchor.**
The body already names `Kazbegi`, `Racha`, `Kakheti`, `Gudauri`, `Bakuriani`, `Ushguli`,
`Svaneti`, `Omalo`, `Tusheti` and "the 4x4 category" — every one of which is a page on this
site — and links none of them. Minimum additions, all with descriptive anchors:
`/car-rental/suv/` (the car's own class), `/car-rental/` (hub), `/terms/` (the insurance and
deposit sentences), and 2–3 route pages the car actually suits.

**F-VEH-4 (P1) — the one link that exists has broken grammar in ka and ru.**
`content/cars/toyota-rav4.yml:64` (en), `:40` (ka), `:87` (ru) inline the anchor mid-sentence
without a case-bearing wrapper:
- en → `compare the categories on Fleet .` (stray space before the period)
- ka → `კატეგორიები ავტოპარკი გვერდზე შეადარეთ.` — `ავტოპარკი` is nominative where the
  sentence requires genitive `ავტოპარკის`
- ru → `категории удобно сравнить на Автопарк .` — nominative after «на»

This is the single clearest "machine-translated" tell in the Georgian corpus. Exact
replacements in Appendix A.5. The same `[Anchor](/url)` pattern should be audited across all
17 `content/cars/*.yml` and all `content/attractions/*.yml` bodies.

**F-VEH-5 (P1) — page has no H2 structure.** Add, from data already present:
`Specifications`, `Rates by rental length`, `What this car is good for`,
`Routes this car suits`, `Booking and enquiries`.

---

## 6. Attraction — `dist/attractions/gergeti-trinity-church/` (+ ka, ru)

682 words, 13 internal links, 4 real photos with alt text, a stars/rating widget, a facts
table and a map. The best-covered template on the site.

| Element | Built value | Verdict |
|---|---|---|
| Title en | `Gergeti Trinity Church Monastery — Visiting Guide, 3:10 from Tbilisi` (68, brand dropped) | Reads badly: "Church … Monastery". |
| Title ka | `გერგეტის სამების ეკლესია — მონასტრის სანახავად გზამკვლევი, 3:10 თბილისიდან` (74) | Over 70; same noun collision. |
| Title ru | `Церковь Святой Троицы в Гергети — гид по монастырю, 3:10 от Тбилиси` (67) | Acceptable. |
| Desc | 154 / 156 / 159 | Good length and specificity. |
| **Desc ka** | `… მონასტერი მცხეთა-მთიანეთი-ში, 160 კმ …` | **Ungrammatical** — see F-ATT-2. |
| H1 | entity name | Fine for this template (the title carries intent). |
| Hierarchy | H1 → H2 `Gallery` → **H3 `Rent a car for this trip`** → H2 … | H3 is not a subsection of Gallery. |
| Images | 8; **4 with `alt=""`** (logo + 3 nearby-place thumbs) | P1 |
| Anchors | 3 image links with **empty accessible name** duplicating the 3 title links beneath them | P1 |
| Visible junk | `photo_by: Lika Kharazishvili · CC BY-SA 4.0` | P1, 1,488 pages |

### Findings

**F-ATT-1 (P0) — `{name} Monastery` / `{name} Museum` etc. collide with names that already
contain the noun.** `seo_meta.yml:478` (`{name} Monastery — Visiting Guide`), `:554`
(`{name} Museum — Visitor Guide`), `:725` (`{name} Ski Resort Guide`), `:573` (`{name} Lake`).
Live examples in the current build:
- `The Green Monastery (Chitakhevi St George) Monastery — Visiting Guide`
- `Svaneti Museum of History and Ethnography Museum — Visitor Guide`
- `Gudauri and the Russia–Georgia Friendship Monument Ski Resort Guide`
- `Rkoni Monastery and Tamar's Bridge Monastery — Visiting Guide`

Fix: move the type noun behind a colon so it reads as a category label rather than an
apposition — `{name}: Monastery Guide, {drive} from Tbilisi`. This also shortens the title by
6–9 chars. Full YAML in Appendix A.1.

**F-ATT-2 (P0) — Georgian region names carry a hyphenated locative.**
`seo_meta.yml:443, 463, 482, 501, 520, 539, 558, 577, 596, 615, 634, 653, 672, 691, 710, 729, 748`
— every `ka` attraction description uses `{region}-ში`. All 11 region names are native Georgian
nouns, so this renders `მცხეთა-მთიანეთი-ში`, `სამცხე-ჯავახეთი-ში`, `იმერეთი-ში`. Correct:
`მცხეთა-მთიანეთში`, `სამცხე-ჯავახეთში`, `იმერეთში`. **257 attractions × 1 = 257 Georgian
descriptions affected.** Fix in Appendix A.1 (restructure so no suffix attaches), or properly
via a `ka_in` field on each region.

**F-ATT-3 (P1) — `photo_by:` printed as caption text on 1,488 pages.**
`build.py:1537`: `cap = te(lang, "photo_by")`. The key `photo_by` does not exist under
`TRAVEL[lang]["exp"]` in `content/settings/travel.yml`, so `te()` returns the key itself.
`photo_html()` at `build.py:1570` has a guard for exactly this and falls back to `"Photo"`;
`gallery_html()` does not. Data fix in Appendix A.3 (add `photo_by` beside the existing
`gallery` key at `travel.yml:136 / 283 / 429 / 575 / 720 / 866`).

**F-ATT-4 (P1) — nearby-place thumbnails have `alt=""` and their anchors have no accessible
name.** `build.py:2146`. Each nearby card renders
`<a class="card-img" href="…"><img src="…" alt="" loading="lazy"></a>` immediately followed by
an `<h3><a href="…">Name</a></h3>` to the same URL. The image anchor is a link with zero
accessible name (WCAG 2.4.4 / 4.1.2 failure) and a wasted internal link. Two acceptable fixes:
give the `<img>` the place name as alt, or mark the wrapper `tabindex="-1" aria-hidden="true"`
as the route template already does at `build.py:2241`. Prefer the first — it adds image-search
surface. Same pattern at `build.py:2040` (region cards) and `build.py:3821` (tour cards).

**F-ATT-5 (P1) — heading hierarchy break.** The H3 `Rent a car for this trip` sits between H2
`Gallery` and H2 `Practical advice`, implying it is part of the gallery. Promote to H2, or move
it inside its own section. Source label: `content/settings/travel.yml:138`.

**F-ATT-6 (P2) — generic H2 "Gallery".** `Photos of {name}` / ka `{name} — ფოტოები` /
ru `Фотографии: {name}` gives the image block a keyworded heading.

**F-ATT-7 (P2) — `როგორ ჩახვიდეთ თბილისიდან`** — "how to go *down* from Tbilisi" for a site at
2,170 m. See §9.

---

## 7. Route — `dist/routes/military-highway-kazbegi/` (+ ka, ru)

| Element | Built value | Verdict |
|---|---|---|
| Title en | `Georgian Military Highway and Kazbegi: Mountain Road Trip — 2 Days, 340 km` (74) | Over 70; brand dropped. |
| Title ka | `სამხედრო გზა და ყაზბეგი — მთის მარშრუტი, 2 დღე, 340 კმ \| RentUp` (63) | Good. |
| Title ru | `Военно-Грузинская дорога и Казбеги — горный маршрут, 2 дней, 340 км` (67) | `2 дней` is wrong Russian. |
| **Desc en** | `…The Georgian Military Highway is the country's most famous` — **cut mid-sentence, no full stop** | **P0** |
| **Desc ka / ru** | both end `… 155` — cut mid-number | **P0** |
| H1 | route name | Good. |
| Hierarchy | H1 → H2 plan → H2 stops → H3 ×6 → H2 tips → H2 car → H2 booking | Clean. |
| Images | 7; **all 7 `alt=""`** including 6 real stop photographs | P1 |

### Findings

**F-RTE-1 (P0) — the meta description from `seo_meta.yml` is computed and thrown away.**
`build.py:2249` binds `_sd`, `build.py:2253–2255`:
```python
    if _st:
        title = _st
    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
```
`_sd` is never read. Every route in every language therefore ships a hard-truncated body
fragment. Fix — insert after line 2254:
```python
    if _st:
        title = _st
    desc = _sd or re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
```
**The identical bug exists for regions** at `build.py:2050` / `:2053` — `_sd` bound, never used;
`/regions/mtskheta-mtianeti/` currently ends `…Mtskheta-Mtianeti starts immediately`.
Apply the same one-word change there.

**F-RTE-2 (P0) — malformed HTML on every route page.**
`build.py:2269`: `f'<section class="sec"><div class="wrap"'` — the `>` is missing, so the
built markup is `<div class="wrap"<div class="cta">`. Present in all 32 routes × 6 languages.
Fix: `f'<section class="sec"><div class="wrap">'`.

**F-RTE-3 (P1) — six stop photographs with `alt=""`.**
`build.py:2241`. Here the wrapper *is* `aria-hidden="true" tabindex="-1"`, so a11y is
technically satisfied — but these are the only photographs of Jvari, Zhinvali, Ananuri,
Gudauri, Gergeti and Dariali on the page, and they are invisible to image search. Give the
`<img>` `alt="{stop name} — stop on the {route name} route"` and drop the `aria-hidden`.

**F-RTE-4 (P1) — number agreement in ru / ar / he.**
`2 дней` should be `2 дня`; the Arabic route titles render `2 أيام` where the dual `يومان`
is required. `seo_meta.yml` cannot express this — it needs a `plural(n, lang, unit)` helper in
`build.py` used by both `seo_meta()`'s `fill()` and `tu(lang,"days")`.

**F-RTE-5 (P1) — en title overflow from double punctuation.**
`seo_meta.yml:294` `{name}: Mountain Road Trip — {days} Days, {km} km` collides with route
names that already contain a colon or dash, e.g.
`Racha in Two Days — Churches, Lake and Mountain Villages: Nature Road Trip — 2 Days, 330 km`
(91 chars, two em-dashes, one colon). Covered by the trim in §10.

**F-RTE-6 (P2) — the audit's length check counts HTML entities.**
`&amp;` and `&#x27;` in titles are counted as 5–6 characters by `scripts/seo_audit.py`,
inflating a handful of en results (`Rkoni Monastery and Tamar&#x27;s Bridge …`). Unescape
before measuring.

---

## 8. Itinerary — `dist/itineraries/georgia-7-days/` and hub `dist/itineraries/`

The detail page is strong: 529 words, **21 internal links**, every attraction named in the
prose is linked with its own name as the anchor. The hub is thin.

| Element | Detail (7-day) | Hub |
|---|---|---|
| Title en | `7-Day Georgia Road Trip Itinerary \| RentUp` (42) | `Georgia Road Trip Itineraries — 3 to 14 Days \| RentUp` (53) |
| **Desc** | `A {days}-day Georgia itinerary covering {km} km and {stops} stops, …` | `5 curated Georgia itineraries…` (127) — fine |
| H1 | `Georgia in 7 Days: Heritage Road from Mtskheta to Kutaisi` | **`Itineraries`** / ka `მზა მარშრუტების გეგმები` / ru `Готовые планы поездок` |
| Hierarchy | H1 → H2 → H3 ×7 → H2 ×3 | **H1 → H3** — H2 level skipped |
| Images | 1 (logo) | 1 (logo) |

### Findings

**F-ITI-1 (P0) — unrendered `{days}`, `{km}`, `{stops}` in the meta description of all 30
itinerary pages.** `build.py:3694` does not pass `stops`:
```python
    title, desc = seo_meta("itinerary", lang, days=it["days"], km=it["total_km"],
                           drive=it["total_drive"], name=L.get("name", ""),
                           car=car_cat_label(it.get("car_category", "economy"), lang))
```
`seo_meta.fill()` (`build.py:126–130`) catches the resulting `KeyError` and returns the
template **verbatim**, so *all three* placeholders survive — which is why the title (which
uses only `{days}`) renders correctly and the description does not. Two fixes, apply either:

```python
# build.py:3694 — pass the missing value
    title, desc = seo_meta("itinerary", lang, days=it["days"], km=it["total_km"],
                           stops=len(it.get("stops") or it.get("attraction_slugs") or []),
                           drive=it["total_drive"], name=L.get("name", ""),
                           car=car_cat_label(it.get("car_category", "economy"), lang))
```
or, data-only, drop `{stops}` from `seo_meta.yml:1101–1116` (Appendix A.1).
Independently, **harden `fill()`** so one missing key can never leak a whole template —
Appendix A.6.

**F-ITI-2 (P1) — hub H1 is a bare category word.**
`build.py:3728`: `hub_h1 = su("itineraries", lang) or "Itineraries"` — the H1 reuses the *nav
label* at `content/settings/seo_ui.yml:336–342`. Result: `Itineraries` /
`მზა მარშრუტების გეგმები` / `Готовые планы поездок` — none names Georgia, none matches the
title. Do **not** change the nav key (it is correct as a nav label); add a dedicated H1 key
(Appendix A.2) and use it at `build.py:3728` only:
`en: Georgia road trip itineraries, 3 to 14 days` ·
`ka: საქართველოს მზა მარშრუტები — 3-დან 14 დღემდე` ·
`ru: Готовые маршруты по Грузии на 3–14 дней`.

**F-ITI-3 (P1) — mislabelled H2 "Routes that need this car" on an itinerary page.**
`su("routes_needing_this_car")` (`seo_ui.yml:86`) is a *category* label. On an itinerary the
section lists the routes the itinerary is built from. Use a new key:
en `Routes in this itinerary` / ka `მარშრუტები ამ გეგმაში` / ru `Маршруты в этом плане`.

**F-ITI-4 (P1) — the itineraries cluster is nearly orphaned.**
`/itineraries/` has **7 inbound links** site-wide: its own 5 children, `/tours/`, and
`/trip-planner/`. It is not in the header nav and not on the homepage. Add it to the home
"Ready-made routes" section and to the primary nav, and cross-link each itinerary from the
`/car-rental/{city}/` page whose city it starts in.

**F-ITI-5 (P2) — heading-level skip on the hub.** H1 → H3 with no H2. Wrap the card grid in a
section with an H2 (`Itineraries by length` / `მარშრუტები ხანგრძლივობის მიხედვით` /
`Маршруты по длительности`).

**F-ITI-6 (P2) — visible day-plan data looks wrong and undermines trust.**
`/itineraries/georgia-7-days/` shows `Day 2 — Gori → Gori 115 km · 2:10` (identical to Day 1)
and `Day 4 — Akhaltsikhe → Vardzia 345 km · 5:40`. I am not proposing values — flag for the
data owner to re-derive from `content/settings/road_legs.yml`.

---

## 9. Georgian copy — naturalness review

The Georgian *long-form body copy* (attractions, routes, categories, vehicles) is good and
does not read as machine output. The problems are concentrated in **short UI strings and
generated metadata**, which is exactly where a Georgian reader notices machine translation
first. Eleven items, all confirmed in the built HTML.

| # | Where | Rendered now | Why it's wrong | Replacement |
|---|---|---|---|---|
| **KA-1** | Site-wide terminology | `დაქირავება` (136 hits) vs `გაქირავება` (461) vs `ქირაობა` (25) | Three different words for "rent" across title / H1 / body of the *same page*. `seo_meta.yml` titles say `დაქირავება`, every H1 says `გაქირავება`, the hand-written `meta_title`s say `ქირაობა`. | Pick one and enforce. Recommend `ქირაობა` for user-intent pages (it is the customer-side verb and is what the hand-written metadata already uses), `გაქირავება` nowhere in titles. Minimum: make title match its own H1. |
| **KA-2** | `seo_meta.yml:1012, 1013` | `ბათუმი-ში`, `თბილისი-ში`, `ქუთაისი-ში` | Hyphenated case ending on a native Georgian noun. The hyphen form is reserved for Latin-script tokens (`RAV4-ის` is correct). | `ბათუმში`, `თბილისში`, `ქუთაისში` — see Appendix A.1 |
| **KA-3** | `seo_meta.yml:1031, 1032` | `თბილისიის აეროპორტში` | Double genitive. `თბილისი` → `თბილისის`, not `თბილისიის`. The page's own H1 is correct. | `თბილისის აეროპორტში` |
| **KA-4** | `seo_meta.yml:1055, 1056` | `ეკონომ კლასი-ის დაქირავება`, `მინივენი-ის დაქირავება`, `3 ეკონომ კლასი მოდელი` | Same hyphen error plus unmarked noun-noun juxtaposition. | `ეკონომ კლასის ქირაობა`, `მინივენის ქირაობა`, `ეკონომ კლასის 3 მოდელი` |
| **KA-5** | `seo_meta.yml` ka attraction block (17 `description` lines) | `მცხეთა-მთიანეთი-ში`, `იმერეთი-ში` | Hyphenated locative on native region names, on 257 pages. | `მცხეთა-მთიანეთში`, `იმერეთში` |
| **KA-6** | `build.py:3098`, `:3965` | `განვერიანდი Community-ში` | `განვერიანდი` is not a word; `Community` untranslated. Homepage, above the fold. | `შემოგვიერთდით საზოგადოებაში` |
| **KA-7** | `seo_ui.yml:224` | `ფასი დან 240 ₾/დღე` | Word-for-word "Price from". `-დან` is a suffix, not a free-standing word. Appears on every car card and category card. | `ka: "ფასი:"` → `ფასი: 240 ₾/დღე`. Ideal (needs code): `240 ₾-დან დღეში`. |
| **KA-8** | `seo_car_rental.yml:223, 226, 229` | `დაზღვევა და დეპოზიტის ექსცესი`, `სტანდარტული ექსცესი 1000 ₾` | `ექსცესი` is a false friend — in Georgian it means *disturbance/incident*, never an insurance excess. Russian correctly uses `франшиза`. | `ფრანშიზა`: `დაზღვევა და ფრანშიზა`, `სტანდარტული ფრანშიზა 1000 ₾`, `ნულოვანი ფრანშიზის` |
| **KA-9** | `content/routes/imereti-caves-canyons.yml:90`, `:109` | `იმერეთი: ღრმულები და კანიონები` | `ღრმული` = hollow / pit. The word for cave is `მღვიმე` — used correctly elsewhere, e.g. `content/attractions/navenakhevi-cave.yml:65`. This string is a route H1, a homepage H3 and a `<title>`. | `იმერეთი: მღვიმეები და კანიონები` (and line 109 body likewise) |
| **KA-10** | `seo_trip_planner.yml:739` | H2 `სანახაობები` for "Places to visit" | `სანახაობა` = a spectacle / show, not a sight to visit. | `სანახავი ადგილები` |
| **KA-11** | `seo_trip_planner.yml:721`; `travel.yml:138`; `build.py:3094–3098` | `დაგეგმე შენი მოგზაურობა`, `დაიქირავე მანქანა…`, `აირჩიე სასურველი`, `რა გეგმა გაქვს დღეს?` | Informal 2nd-person singular, on the same pages whose meta descriptions and CTAs use the formal plural (`იქირავეთ`, `დაგეგმეთ`, `დაჯავშნეთ`). A Georgian reader registers the switch immediately. | Move everything to the formal register: `დაგეგმეთ თქვენი მოგზაურობა`, `იქირავეთ მანქანა ამ მოგზაურობისთვის`, `აირჩიეთ სასურველი`, `რა გეგმა გაქვთ დღეს?` |

Two more, lower confidence, worth a native pass:
- `dist/ka/attractions/*/`: H2 `როგორ ჩახვიდეთ თბილისიდან` — `ჩასვლა` is "to go down". Correct
  for Kakheti, wrong for Gergeti (2,170 m) or Ushguli. Neutral alternative: `როგორ მიაღწიოთ თბილისიდან`.
- `dist/ka/fleet/toyota-rav4/`: `6.5–8.5 ლ / 100 კმ -ში ეტევა` — stray space before the suffix
  and an unusual verb choice. More natural: `საშუალო ხარჯი 6.5–8.5 ლ/100 კმ-ია`.

**Russian** carries the same class of defect in generated strings only:
`Аренда Внедорожник 4x4` (needs genitive), `3 моделей` (needs `3 модели`), `2 дней`
(needs `2 дня`), `сравнить на Автопарк` (needs a preposition-governed form).
**Arabic** spot-check: `2 أيام` should be the dual; `3 طرازاً` should be plural genitive for
3–10. Both need a native pass — flagged, not asserted.

---

## 10. The over-70 titles — a real fix, measured

**Restating the problem correctly:** 275 titles exceed 70 characters (247 flagged by
`scripts/seo_audit.py`; the difference is entity-escaping, see F-RTE-6). 96 are Georgian,
67 Russian, 66 English, 46 across fa/he/ar. `seo_meta()` already drops the ` | RentUp` suffix
above 70 (`build.py:132–136`); everything in the 275 is *already* post-suffix-drop.

**Root causes, in order of contribution:**
1. Entity names are long (ka p90 = 34 chars, max 72; en max 57) and the attraction templates
   add 37–48 chars of fixed overhead.
2. The `by_type` variants spend those characters on a redundant type noun that often already
   appears in the name (F-ATT-1).
3. There is no fallback below "drop the brand".

**Rejected options.** Per-language length budgets is not a fix — Google truncates on pixel
width, and Georgian Mkhedruli and Arabic script are *wider* per character than Latin at the
same point size, so a longer budget for ka/ar/he would be exactly backwards. Hard truncation
with an ellipsis produces mid-word cuts in Georgian, which has no reliable word-boundary
heuristic at that length. Accepting long titles as a documented decision is defensible only
for the residual case where the entity name alone exceeds the budget.

### Recommended fix — two parts

**Part 1 — a guarded clause-trim in `seo_meta()`.** After the existing brand-drop, repeatedly
remove the last comma/dash/colon-delimited clause while the title is over 70, but **never cut
into the entity name**. Code in Appendix A.6.

**Part 2 — shorten the ka / en / ru attraction templates** so the trim rarely has to fire and
the surviving titles keep their type keyword. YAML in Appendix A.1.

### Measured result

Applied to all 257 attractions × 6 languages and all 32 routes × 6 languages:

| lang | now | Part 1 only | Part 1 + Part 2 (titles trimmed) |
|---|---|---|---|
| ka attractions | 90 over | **1 over** | 1 over, 36 trimmed (was 90) |
| ru attractions | 62 over | **0 over** | 0 over, 4 trimmed (was 62) |
| en attractions | 42 over* | **0 over** | 0 over, 16 trimmed (was 42) |
| fa / he / ar attractions | 17 / 10 / 9 | **0 / 0 / 0** | — |
| routes, all langs | 15 over | **0 over** | — |

\* 42 measured on unescaped text; the audit reports 60 for en because of F-RTE-6.

**Total: 275 → 1.**

### The documented decision for the residual

Exactly one page cannot be fixed by templating:
`content/attractions/kukushka-narrow-gauge-railway.yml`, whose `ka.name` is
`„კუკუშკა“ — ბორჯომ-ბაკურიანის ვიწროლიანდაგიანი რკინიგზა და ცაღვერის ხიდი` — **72 characters
before any template is applied**. The correct fix is editorial, not technical: shorten the
`ka.name` (and the 99-character `en.name`) to the common short form, e.g. ka
`კუკუშკა — ბორჯომ-ბაკურიანის ვიწროლიანდაგიანი რკინიგზა` (52), en
`The Kukushka narrow-gauge railway` (33). Until then, `scripts/seo_audit.py` will report
1 WARN, which is the correct signal — it is a content task, not a template failure.

**Recommendation:** tighten the audit threshold from a bare `> 70` count to a two-tier check —
ERROR if a title exceeds 70 *after* the trim (i.e. the name itself is too long, a content
task), WARN if the trim had to fire at all (i.e. the page lost its differentiator, a template
task). That turns a 247-line noise wall into an actionable two-line signal.

---

## 11. Consolidated findings table

P0 = shipping a visible defect or losing the page's primary ranking signal.
P1 = material SEO or a11y loss. P2 = polish.

| ID | Pri | Template | Finding | Location |
|---|---|---|---|---|
| F-ITI-1 | **P0** | Itinerary | `{days} {km} {stops}` literal in meta description, 30 pages | `build.py:3694` |
| F-LOC-1 | **P0** | Location | `{place}` literal in a visible `<h2>`, 36 pages | `build.py:3505` |
| F-RTE-1 | **P0** | Route, Region | `_sd` computed and discarded → descriptions truncated mid-sentence, ~258 pages | `build.py:2255`, `build.py:2053` |
| F-RTE-2 | **P0** | Route | Malformed `<div class="wrap"<div>`, 192 pages | `build.py:2269` |
| F-HUB-1 | **P0** | Hub, Location, Category | Hand-written `meta_title`/`meta_description` overridden by generic templates, 60 pages | `build.py:3463, 3533, 3587` |
| F-CAT-1 | **P0** | Category | `Аренда Внедорожник 4x4`, `3 моделей` — Russian case + numeral agreement | `seo_meta.yml:1058, 1059` |
| F-CAT-2 | **P0** | Category | `ეკონომ კლასი-ის`, `მინივენი-ის` — Georgian case | `seo_meta.yml:1055, 1056` |
| F-LOC-2 | **P0** | Location | `ბათუმი-ში`, `თბილისიის` — Georgian case | `seo_meta.yml:1012, 1031` |
| F-ATT-2 | **P0** | Attraction | `{region}-ში` on 257 Georgian descriptions | `seo_meta.yml`, ka attraction block |
| F-HOME-1 | **P0** | Home | H1 carries no keyword | `build.py:3094, 3100, 3106, 3964` |
| F-HOME-2 | **P0** | Home | `განვერიანდი Community-ში` — non-word, above the fold | `build.py:3098, 3965` |
| F-VEH-1 | **P0** | Vehicle | H1 is the bare model name | `build.py:1356` |
| F-VEH-2 | **P0** | Vehicle | No photo of the car on the car's own page | `render_car`, `build.py:1310–1400` |
| F-VEH-3 | **P0** | Vehicle | 3 internal links, 2 with the anchor "Fleet" | `content/cars/*.yml` |
| F-ATT-1 | P1 | Attraction | `{name} Monastery` collides with names containing the noun | `seo_meta.yml:478, 554, 573, 725` |
| F-ATT-3 | P1 | Attraction | `photo_by:` printed as caption text, 1,488 pages | `build.py:1537` |
| F-ATT-4 | P1 | Attraction, Region, Home | `alt=""` + empty link anchor on card thumbnails | `build.py:2040, 2146, 3821` |
| F-RTE-3 | P1 | Route | 6 stop photographs with `alt=""` | `build.py:2241` |
| F-RTE-4 | P1 | Route | `2 дней`, `2 أيام` — number agreement | `seo_meta.yml` route block |
| F-HUB-2 | P1 | Hub | H2 "Cars in this category" on a hub | `seo_ui.yml:102` |
| F-HUB-3 | P1 | Hub | ka H1 and body H2 byte-identical | `seo_car_rental.yml:156` |
| F-HUB-4 | P1 | Hub, Category, Post | `FAQ` hard-coded in English in 6 languages | `build.py:3459, 3580, 3782` |
| F-HUB-5 | P1 | Hub | Zero content images | `render_car_rental_hub`, `build.py:3411–3481` |
| F-HUB-6 | P1 | Hub | `business` and `van` categories have no landing page | `categories.yml` vs `dist/car-rental/` |
| F-LOC-4 | P1 | Location | Same 5 attractions rendered twice | `build.py:3506–3512` |
| F-LOC-5 | P1 | Location | H2 "Best car for this trip" on a location page | `build.py:3509` |
| F-CAT-3 | P1 | Category | `4x4_only` YAML enum leaking into prose | `seo_categories.yml` offroad body |
| F-CAT-4 | P1 | Category | H2 "Best car for this trip" on a category page | `build.py:3569` |
| F-CAT-5 | P1 | Category | Zero images on a vehicle-choice page | `render_rental_category`, `build.py:3555–3610` |
| F-VEH-4 | P1 | Vehicle | Inline link breaks case in ka and ru | `content/cars/toyota-rav4.yml:40, 64, 87` |
| F-VEH-5 | P1 | Vehicle | Two H2s on the whole page | `render_car`, `build.py:1310–1400` |
| F-ITI-2 | P1 | Itineraries hub | H1 reuses the nav label; no keyword | `build.py:3728`, `seo_ui.yml:336` |
| F-ITI-3 | P1 | Itinerary | H2 "Routes that need this car" | `seo_ui.yml:86` |
| F-ITI-4 | P1 | Itineraries | Cluster nearly orphaned — 7 inbound links | site-wide |
| F-HOME-3 | P1 | Home | Logo + hero `alt=""` | `build.py:836, 3210, 4129` |
| F-HOME-4 | P1 | Home | 4× "View", 3× "Details" anchors | `build.py:3194`, `4139` |
| F-ATT-5 | P2 | Attraction | H3 nested under H2 "Gallery" | `travel.yml:138` |
| F-ATT-6 | P2 | Attraction | Generic H2 "Gallery" | `travel.yml:136` + 5 |
| F-ATT-7 | P2 | Attraction | `ჩახვიდეთ` for a 2,170 m site | `travel.yml` ka |
| F-LOC-3 | P2 | Location | `\| RentUp Georgia` vs `\| RentUp` | `seo_meta.yml:1009` |
| F-LOC-6 | P2 | Location | `1 days`, `1 дней` | `build.py:3301` |
| F-LOC-7 | P2 | Location | ~90 words of unique copy | `seo_car_rental.yml` locations |
| F-CAT-6 | P2 | Category | Title label ≠ H1 label | `cat_label()` vs `seo_categories.yml` |
| F-RTE-5 | P2 | Route | Double punctuation in en titles | `seo_meta.yml:294` |
| F-RTE-6 | P2 | Audit | Length check counts HTML entities | `scripts/seo_audit.py` |
| F-ITI-5 | P2 | Itineraries hub | H1 → H3, H2 skipped | `build.py:3739` |
| F-ITI-6 | P2 | Itinerary | Day-plan legs look wrong (Day 2 = Day 1) | `content/itineraries/georgia-7-days.yml` |
| F-HOME-5 | P2 | Home | ka informal/formal register mismatch | see §9 KA-11 |

---

# Appendix A — exact patches

## A.1 `content/settings/seo_meta.yml`

### A.1.1 Attraction — Georgian locative (F-ATT-2). Replace `{region}-ში` throughout the `ka` attraction block.

The suffix cannot be attached to a placeholder. Restructure so the region is apposed, not
inflected. Pattern change, applied to `templates.attraction.default.ka` (line 443) and each of
the 16 `by_type.*.ka` description lines (463, 482, 501, 520, 539, 558, 577, 596, 615, 634, 653,
672, 691, 710, 729, 748):

```yaml
# BEFORE  (seo_meta.yml:482, monastery)
        ka:
          description: "{name} — მონასტერი {region}-ში, {km} კმ თბილისიდან ({drive}) — სანახავი საათები, რა ფუნქციონირებს დღემდე და როგორ ჩახვიდეთ ავტომობილით."

# AFTER
        ka:
          description: "{name} — მონასტერი, რეგიონი {region}, {km} კმ თბილისიდან ({drive}) — სანახავი საათები, რა ფუნქციონირებს დღემდე და როგორ მიაღწიოთ ავტომობილით."
```

Apply the same `X-ში` → `რეგიონი X` swap to the other 16 lines. (The fully correct alternative
is a `ka_in` field per region plus a `{region_in}` placeholder — see A.7.)

### A.1.2 Attraction — shorter en / ka / ru titles (F-ATT-1, §10 Part 2)

```yaml
  attraction:
    default:
      en:
        title: "{name}: {type} Guide, {drive} from Tbilisi | RentUp"
      ka:
        title: "{name} — {type} გზამკვლევი, {drive} თბილისიდან | RentUp"
      ru:
        title: "{name} — {type}, {drive} от Тбилиси | RentUp"
    by_type:
      monastery:
        en:
          title: "{name}: Monastery Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — მონასტრის გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — монастырь, {drive} от Тбилиси | RentUp"
      fortress:
        en:
          title: "{name}: Fortress Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — ციხის გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — крепость, {drive} от Тбилиси | RentUp"
      museum:
        en:
          title: "{name}: Museum Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — მუზეუმის გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — музей, {drive} от Тбилиси | RentUp"
      nature:
        en:
          title: "{name}: Nature Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — ბუნების გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — природный объект, {drive} от Тбилиси | RentUp"
      ski:
        en:
          title: "{name}: Ski Resort Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — კურორტის გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — горнолыжный курорт, {drive} от Тбилиси | RentUp"
      spa:
        en:
          title: "{name}: Hot Springs Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — თერმული აბანოს გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — термы, {drive} от Тбилиси | RentUp"
      archaeology:
        en:
          title: "{name}: Ancient Site Guide, {drive} from Tbilisi | RentUp"
        ka:
          title: "{name} — ძეგლის გზამკვლევი, {drive} თბილისიდან | RentUp"
        ru:
          title: "{name} — древний памятник, {drive} от Тбилиси | RentUp"
```
Remaining types follow the identical shape with these nouns —
`town`: `Town` / `ქალაქის` / `город`; `mountain`: `Mountain` / `მთის` / `гора`;
`lake`: `Lake` / `ტბის` / `озеро`; `winery`: `Winery` / `მარნის` / `винодельня`;
`beach`: `Beach` / `პლაჟის` / `пляж`; `cave`: `Cave` / `გამოქვაბულის` / `пещера`;
`waterfall`: `Waterfall` / `ჩანჩქერის` / `водопад`; `canyon`: `Canyon` / `კანიონის` / `каньон`;
`theatre`: `Theatre` / `თეატრის` / `театр`.
Leave `fa`, `he`, `ar` unchanged — Part 1 alone brings them to zero.

### A.1.3 Car-rental location — Georgian (F-LOC-2, KA-2, KA-3) and en brand suffix (F-LOC-3)

These are the *fallback* templates; after F-HUB-1 the hand-written `meta_title` wins. Fix
anyway so the fallback is never wrong.

```yaml
  car_rental_location:
    city:
      en:
        title: "Car Rental in {city} | RentUp"          # was "| RentUp Georgia"
        description: "Pick up a rental car in {city}: which routes start here, the nearest attractions, recommended vehicle categories and drive times."
      ka:
        title: "მანქანის ქირაობა — {city} | RentUp"
        description: "აიღეთ ავტომობილი — {city}: რომელი მარშრუტები იწყება აქედან, უახლოესი ღირსშესანიშნაობები, რეკომენდებული კატეგორია და სამგზავრო დრო."
    airport:
      ka:
        title: "მანქანის ქირაობა — {name} ({iata}) | RentUp"
        description: "იქირავეთ ავტომობილი — {name} ({iata}): მარტივი აღება, უახლოესი მარშრუტები და ღირსშესანიშნაობები, ხელმისაწვდომი კატეგორიები."
```
`{name}` is already passed at `build.py:3530` and holds the airport's own `places.yml` name,
which is correctly inflected there (`თბილისის აეროპორტი`, `ქუთაისის აეროპორტი`,
`ბათუმის აეროპორტი`). No new data needed. Result: `მანქანის ქირაობა — თბილისის აეროპორტი (TBS) | RentUp` (53).

### A.1.4 Car-rental category — Georgian and Russian (F-CAT-1, F-CAT-2)

```yaml
  car_rental_category:
    ka:
      title: "{category} — ქირაობა საქართველოში, {price} ₾-დან | RentUp"
      description: "{category}: {count} მოდელი საქართველოში, ფასი {price} ₾-დან დღეში — მახასიათებლები, ადგილების რაოდენობა, ბარგის სივრცე და შესაფერისი მარშრუტები."
    ru:
      title: "{category} в аренду в Грузии — от {price} ₾/день | RentUp"
      description: "{category}: {count} моделей в Грузии от {price} ₾ в день — характеристики, число мест, багажник и подходящие маршруты."
```
Putting `{category}` in front of a dash sidesteps the case problem in both languages without
needing inflected label data. `{count} моделей` is left as-is here because the correct Russian
form depends on the number; the proper fix is the `plural()` helper in A.6.

### A.1.5 Itinerary — remove the unpassed placeholder (F-ITI-1, data-only variant)

```yaml
  itinerary:
    en:
      description: "A {days}-day Georgia itinerary covering {km} km, with a day-by-day plan, drive times and the car category it needs."
    ka:
      description: "{days}-დღიანი მარშრუტი საქართველოში — {km} კმ, დღეების მიხედვით გეგმით, სამგზავრო დროითა და საჭირო ავტომობილით."
    ru:
      description: "Маршрут по Грузии на {days} дней — {km} км, с планом по дням, временем в пути и нужной категорией автомобиля."
    fa:
      description: "برنامهٔ سفر {days} روزه در گرجستان شامل {km} کیلومتر، با برنامهٔ روز به روز، زمان رانندگی و دستهٔ خودروی لازم."
    he:
      description: "מסלול טיול בגאורגיה ל-{days} ימים — {km} ק״מ, עם תוכנית יומית, זמני נסיעה וקטגוריית הרכב הנדרשת."
    ar:
      description: "برنامج رحلة في جورجيا لمدة {days} أيام يغطي {km} كم، مع خطة يومية وأوقات قيادة وفئة السيارة المطلوبة."
```
Prefer the `build.py:3694` fix (pass `stops=…`) if the stop count is wanted in the snippet;
use this only if it is not.

## A.2 `content/settings/seo_ui.yml`

```yaml
# ── new key: hub category grid (F-HUB-2) ────────────────────────────────
browse_by_category:
  ka: კატეგორიები
  en: Browse by category
  ru: Категории автомобилей
  fa: دسته‌بندی خودروها
  he: קטגוריות רכב
  ar: تصفح حسب الفئة

# ── new key: category options on a location page (F-LOC-5) ──────────────
categories_available_here:
  ka: ხელმისაწვდომი კატეგორიები
  en: Car categories available here
  ru: Доступные категории
  fa: دسته‌های موجود در این نقطه
  he: קטגוריות זמינות כאן
  ar: الفئات المتاحة هنا

# ── new key: when to pick this class, on a category page (F-CAT-4) ──────
when_to_choose_this_class:
  ka: როდის ავირჩიოთ ეს კატეგორია
  en: When to choose this class
  ru: Когда выбирать этот класс
  fa: چه زمانی این کلاس را انتخاب کنیم
  he: מתי לבחור בקטגוריה זו
  ar: متى تختار هذه الفئة

# ── new key: routes an itinerary is built from (F-ITI-3) ────────────────
routes_in_this_itinerary:
  ka: მარშრუტები ამ გეგმაში
  en: Routes in this itinerary
  ru: Маршруты в этом плане
  fa: مسیرهای این برنامهٔ سفر
  he: המסלולים בתוכנית הזו
  ar: المسارات في هذا البرنامج

# ── new key: itineraries-hub H1, separate from the nav label (F-ITI-2) ──
#    the existing `itineraries:` key at line 336 stays as the nav label
itineraries_h1:
  ka: საქართველოს მზა მარშრუტები — 3-დან 14 დღემდე
  en: Georgia road trip itineraries, 3 to 14 days
  ru: Готовые маршруты по Грузии на 3–14 дней
  fa: برنامه‌های سفر گرجستان، از ۳ تا ۱۴ روز
  he: מסלולי טיול בגאורגיה, 3 עד 14 ימים
  ar: برامج رحلات جورجيا، من 3 إلى 14 يوماً

# ── new key: H2 for the itineraries card grid (F-ITI-5) ─────────────────
itineraries_by_length:
  ka: მარშრუტები ხანგრძლივობის მიხედვით
  en: Itineraries by length
  ru: Маршруты по длительности
  fa: برنامه‌ها بر اساس مدت سفر
  he: מסלולים לפי אורך
  ar: البرامج حسب المدة

# ── new key: replaces the hard-coded English "FAQ" (F-HUB-4) ────────────
faq_title:
  ka: ხშირად დასმული კითხვები
  en: Frequently asked questions
  ru: Частые вопросы
  fa: پرسش‌های متداول
  he: שאלות נפוצות
  ar: الأسئلة الشائعة

# ── line 223–229 REPLACE: "ფასი დან" is not Georgian (KA-7) ─────────────
price_from:
  ka: "ფასი:"
  en: Price from
  ru: Цена от
  fa: قیمت از
  he: מחיר החל מ-
  ar: السعر يبدأ من
```

## A.3 `content/settings/travel.yml` — stop `photo_by:` leaking (F-ATT-3)

Insert one line after each existing `gallery:` key, at the same indentation:

```yaml
# line 136 (ka)
    gallery: გალერეა
    photo_by: ფოტო
# line 283 (en)
    gallery: Gallery
    photo_by: Photo
# line 429 (ru)
    gallery: Галерея
    photo_by: Фото
# line 575 (fa)
    gallery: گالری
    photo_by: عکس
# line 720 (he)
    gallery: גלריה
    photo_by: צילום
# line 866 (ar)
    gallery: المعرض
    photo_by: تصوير
```
Also mirror the existing guard from `build.py:1570` into `gallery_html()` at `build.py:1537`
so a future missing key degrades gracefully:
```python
    cap = te(lang, "photo_by") if "photo_by" in TRAVEL[lang]["exp"] else "Photo"
```

## A.4 Promoting the hand-written car-rental metadata (F-HUB-1)

**Code — three identical edits.**

```python
# build.py:3463  (hub)
-    title = title or h.get("meta_title") or f'{h.get("h1", "")} | {BRAND}'
-    desc  = desc  or h.get("meta_description", "")
+    title = h.get("meta_title") or title or f'{h.get("h1", "")} | {BRAND}'
+    desc  = h.get("meta_description") or desc

# build.py:3533  (location)
-    title = title or L.get("meta_title") or f'{L.get("h1", "")} | {BRAND}'
-    desc  = desc  or L.get("meta_description", "")
+    title = L.get("meta_title") or title or f'{L.get("h1", "")} | {BRAND}'
+    desc  = L.get("meta_description") or desc

# build.py:3587  (category)
-    title = title or L.get("meta_title") or f'{L.get("h1", "")} | {BRAND}'
-    desc  = desc  or L.get("meta_description", "")
+    title = L.get("meta_title") or title or f'{L.get("h1", "")} | {BRAND}'
+    desc  = L.get("meta_description") or desc
```

**Data — normalise the brand suffix on the four category titles.**
`content/settings/seo_categories.yml` currently ends them `— RentUp.ge` (and `– RentUp.ge`
with an en-dash in en). Change all 24 (4 categories × 6 languages) to `| RentUp`. Example for
the `offroad` block:

```yaml
  ka:
    meta_title: 4x4 ქირაობა საქართველოში — 240 ₾-დან/დღეში | RentUp
  en:
    meta_title: 4x4 Rental in Georgia — from 240 ₾/day | RentUp
  ru:
    meta_title: Аренда 4x4 в Грузии — от 240 ₾/день | RentUp
```

**Data — trim the three over-long hand-written descriptions to ≤160 chars.**
Nothing added; only the trailing clause removed.

```yaml
# content/settings/seo_car_rental.yml — hub
  en:
    meta_description: "Rent a car in Georgia from RentUp — economy to 4x4, unlimited mileage, pickup in Tbilisi, Kutaisi or Batumi. Real deposit, insurance and fuel terms."   # 148
  ka:
    meta_description: "იქირავეთ მანქანა საქართველოში RentUp-თან — ეკონომ კლასიდან 4x4-მდე, შეუზღუდავი გარბენი, აღება თბილისში, ქუთაისში ან ბათუმში."                            # 124
  ru:
    meta_description: "Арендуйте машину в Грузии у RentUp — от эконом-класса до 4x4, пробег без ограничений, выдача в Тбилиси, Кутаиси или Батуми."                            # 123

# content/settings/seo_car_rental.yml — locations.tbilisi-airport
  en:
    meta_description: "Rent a car at Tbilisi International Airport for a 30 ₾ delivery fee. We meet you at arrivals with the car ready, unlimited mileage included."          # 140
  ka:
    meta_description: "იქირავეთ მანქანა თბილისის საერთაშორისო აეროპორტში 30 ₾ მიწოდების საფასურად. შეგხვდებით ჩამოსვლისთანავე მზა მანქანით, შეუზღუდავი გარბენით."              # 137
  ru:
    meta_description: "Арендуйте машину в аэропорту Тбилиси за 30 ₾ доставки. Встретим вас в зале прилёта с готовой машиной, пробег без ограничений."                          # 125
```

Resulting titles after the change (all under 70, all unique):

| page | en | ka | ru |
|---|---|---|---|
| `/car-rental/` | `Car Rental in Georgia — Unlimited Mileage, No Hidden Fees \| RentUp` (66) | `მანქანის ქირაობა საქართველოში — შეუზღუდავი გარბენი \| RentUp` (59) | `Аренда авто в Грузии — без ограничения пробега \| RentUp` (55) |
| `/car-rental/batumi/` | `Car Rental in Batumi — Delivered to Your Address \| RentUp` (57) | `მანქანის ქირაობა ბათუმში — მიწოდება თქვენს მისამართზე \| RentUp` (62) | `Аренда авто в Батуми — доставка по вашему адресу \| RentUp` (57) |
| `/car-rental/tbilisi-airport/` | `Tbilisi Airport Car Rental — Arrivals Meet-and-Greet \| RentUp` (61) | `მანქანის ქირაობა თბილისის აეროპორტში — შეხვედრა ჩამოსვლისას \| RentUp` (68) | `Аренда авто в аэропорту Тбилиси — встреча в зале прилёта \| RentUp` (65) |
| `/car-rental/4x4/` | `4x4 Rental in Georgia — from 240 ₾/day \| RentUp` (47) | `4x4 ქირაობა საქართველოში — 240 ₾-დან/დღეში \| RentUp` (51) | `Аренда 4x4 в Грузии — от 240 ₾/день \| RentUp` (44) |

## A.5 `content/cars/toyota-rav4.yml` — inline anchors (F-VEH-4)

```yaml
# line 64 (en) — BEFORE
    The rest of the country is fair game at 145 ₾ a day — compare the categories on [Fleet](/fleet/).
# AFTER
    The rest of the country is fair game at 145 ₾ a day — see how it compares in
    [SUV and crossover rental in Georgia](/car-rental/suv/).

# line 40 (ka) — BEFORE
    კი დღეში 145 ₾-ად თქვენია — კატეგორიები [ავტოპარკი](/fleet/) გვერდზე შეადარეთ.
# AFTER
    კი დღეში 145 ₾-ად თქვენია — შეადარეთ სხვა კატეგორიებს
    [SUV და კროსოვერების ქირაობის გვერდზე](/car-rental/suv/).

# line 87 (ru) — BEFORE
    Грузия доступна за 145 ₾ в сутки — категории удобно сравнить на [Автопарк](/fleet/).
# AFTER
    Грузия доступна за 145 ₾ в сутки — сравните с другими классами на странице
    [аренды SUV и кроссоверов](/car-rental/suv/).
```
Audit the same `[Anchor](/url)` mid-sentence pattern across all 17 `content/cars/*.yml`
and the `body` fields of `content/attractions/*.yml`.

## A.6 `build.py` — code fixes

```python
# ── build.py:126–137 — harden fill(), add the guarded clause-trim ───────
def seo_meta(template, lang, **fmt):
    ...
    node = t.get(lang) or t.get("en") or {}

    class _Missing(dict):
        def __missing__(self, k):
            return ""                      # a missing key blanks that token only,
                                           # never the whole template (F-ITI-1)
    def fill(s):
        try:
            return str(s).format_map(_Missing(fmt))
        except (IndexError, ValueError):
            return str(s)

    title = fill(node.get("title", ""))
    title = _fit_title(title, fill(node.get("name", "")) or fmt.get("name", ""))
    return title, fill(node.get("description", ""))


# ── new helper, place above seo_meta() ─────────────────────────────────
_TITLE_SEPS = (", ", " — ", ": ", "، ")

def _fit_title(title, name="", limit=70):
    """Keep a title inside the SERP budget without ever cutting mid-word.

    1. drop the brand suffix — the domain already carries the brand;
    2. drop trailing clauses one at a time;
    3. never cut into the entity name — if the name alone is over budget that is
       a content task (shorten the name), not a template failure.
    Measured on the current corpus: 275 over-70 titles -> 1.
    """
    brand = f" | {BRAND}"
    if len(title) <= limit:
        return title
    if title.endswith(brand):
        title = title[: -len(brand)]
    if len(title) <= limit:
        return title
    while len(title) > limit:
        cut = max(title.rfind(s) for s in _TITLE_SEPS)
        if cut < len(name):        # would eat into the entity name — stop
            break
        title = title[:cut]
    return title


# ── build.py:2053 — region description (F-RTE-1) ───────────────────────
-    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
+    desc = _sd or re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]

# ── build.py:2255 — route description (F-RTE-1) ────────────────────────
-    desc = re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]
+    desc = _sd or re.sub(r"\s+", " ", L["short"] + " " + L["body"])[:158].rsplit(" ", 1)[0]

# ── build.py:2269 — malformed div (F-RTE-2) ────────────────────────────
-        + f'<section class="sec"><div class="wrap"'
+        + f'<section class="sec"><div class="wrap">'

# ── build.py:3505 — {place} placeholder (F-LOC-1) ──────────────────────
-        + (_sec(su("popular_routes_from", lang),
+        + (_sec(su("popular_routes_from", lang).replace(
+                    "{place}", place.get(lang, place.get("en", key))),

# ── build.py:3694 — pass the missing stop count (F-ITI-1) ──────────────
     title, desc = seo_meta("itinerary", lang, days=it["days"], km=it["total_km"],
+                           stops=len(it.get("stops") or it.get("attraction_slugs") or []),
                            drive=it["total_drive"], name=L.get("name", ""),
                            car=car_cat_label(it.get("car_category", "economy"), lang))

# ── build.py:3459, 3580, 3782 — translate FAQ (F-HUB-4) ────────────────
-        + (_sec("FAQ", f'<div class="faq">{_faq_html(h.get("faq"))}</div>', alt=True)
+        + (_sec(su("faq_title", lang), f'<div class="faq">{_faq_html(h.get("faq"))}</div>', alt=True)

# ── build.py:2146 — nearby-card alt text (F-ATT-4) ─────────────────────
-           f'<img src="{E(ATTRACTIONS[n]["image"])}" alt="" loading="lazy"></a>'
+           f'<img src="{E(ATTRACTIONS[n]["image"])}" '
+           f'alt="{E(ATTRACTIONS[n][lang]["name"])}" loading="lazy"></a>'
#   apply the same shape at build.py:2040 (region cards) and 3821 (tour cards)

# ── build.py:2241 — route stop photos (F-RTE-3) ────────────────────────
-        + (f'<a class="stop-img" href="{attr_url(lang, s, False)}" tabindex="-1" aria-hidden="true">'
-           f'<img src="{E(a["image"])}" alt="" loading="lazy"></a>' if a.get("image") else "")
+        + (f'<a class="stop-img" href="{attr_url(lang, s, False)}">'
+           f'<img src="{E(a["image"])}" alt="{E(a[lang]["name"])} — {E(L["name"])}" '
+           f'loading="lazy"></a>' if a.get("image") else "")

# ── build.py:836 — logo alt (F-HOME-3) ─────────────────────────────────
-    logo = (f'<img src="{E(logo_img)}" alt="" aria-hidden="true">'
+    logo = (f'<img src="{E(logo_img)}" alt="{E(BRAND)}">'

# ── build.py:3301 — plural agreement (F-LOC-6, F-RTE-4) ────────────────
def plural(n, lang, one, few, many):
    """ru/ar need real agreement; en needs 1 vs many; ka/fa are invariant."""
    n = int(n)
    if lang in ("ka", "fa", "he"):
        return one
    if lang == "en":
        return one if n == 1 else many
    if lang == "ar":
        return one if n == 1 else (few if n == 2 else many)
    r100, r10 = n % 100, n % 10          # ru
    if 11 <= r100 <= 14:
        return many
    return one if r10 == 1 else (few if 2 <= r10 <= 4 else many)
```

## A.7 The proper fix for Georgian place and region inflection (optional, replaces A.1.1/A.1.3)

Georgian needs case-marked forms; a template cannot derive them. Add them to the data once:

```yaml
# content/settings/places.yml — one new key per place
places:
  - key: tbilisi
    ka: თბილისი
    ka_in: თბილისში          # locative  — "in Tbilisi"
    ka_gen: თბილისის         # genitive  — "Tbilisi's"
  - key: batumi
    ka: ბათუმი
    ka_in: ბათუმში
    ka_gen: ბათუმის
  - key: kutaisi
    ka: ქუთაისი
    ka_in: ქუთაისში
    ka_gen: ქუთაისის
  - key: tbilisi-airport
    ka: თბილისის აეროპორტი
    ka_in: თბილისის აეროპორტში
  - key: batumi-airport
    ka: ბათუმის აეროპორტი
    ka_in: ბათუმის აეროპორტში
  - key: kutaisi-airport
    ka: ქუთაისის აეროპორტი
    ka_in: ქუთაისის აეროპორტში
```
```python
# build.py:3528 — pass the inflected form
     title, desc = seo_meta("car_rental_location", lang, kind=kind,
                            city=_city,
+                           city_in=(place.get(f"{lang}_in") or place.get(lang) or key),
                            name=place.get(lang, place.get("en", key)), ...)
```
```yaml
# content/settings/seo_meta.yml
  car_rental_location:
    city:
      ka:
        title: "მანქანის ქირაობა {city_in} | RentUp"     # → მანქანის ქირაობა ბათუმში | RentUp
    airport:
      ka:
        title: "მანქანის ქირაობა {city_in} ({iata}) | RentUp"
```
Do the same with a `ka_in` on each of the 11 regions for the attraction descriptions
(`{region_in}` → `მცხეთა-მთიანეთში`). This is the version to ship if the Georgian pages matter
commercially; A.1.1/A.1.3 is the interim that needs no schema change.

---

## Appendix B — suggested fix order

1. **B1–B6 rendering bugs** (A.6). One afternoon, ~1,900 pages corrected, no content work.
2. **F-HUB-1** (A.4). Three lines + a brand-suffix normalisation; fixes every P0 Georgian and
   Russian grammar defect in the car-rental cluster and replaces 60 generic titles with 60
   human ones.
3. **§10 title fix** (A.6 `_fit_title` + A.1.2). 275 WARN → 1.
4. **Georgian naturalness sweep** (§9, A.1–A.3, A.5). 11 confirmed items, all short strings.
5. **Image and anchor work** (F-VEH-2, F-CAT-5, F-HUB-5, F-ATT-4, F-HOME-4). The commercial
   pages currently ship one image each — the logo.
6. **Home and vehicle H1s** (F-HOME-1, F-VEH-1) and the missing `business` / `van` category
   pages (F-HUB-6).
