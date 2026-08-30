# GRAMMAR_FIXES — applying TRANSLATION_QA.md to the SEO template packs

**Date:** 2026-08-30
**Source of truth:** `docs/seo/TRANSLATION_QA.md` (2026-08-29)
**Files written:** `content/settings/ka_forms.yml` (new), `content/settings/seo_meta.yml`,
`content/settings/seo_ui.yml`, this report. Nothing else was touched.

**Verification:** `python3 build.py --validate-only` → passed ·
`python3 build.py /tmp/gr` → 2 292 pages ·
`python3 scripts/seo_audit.py /tmp/gr` → **0 ERROR**, 2 WARN, 20 INFO.
Both WARNs (`/ka/trip-planner/`, `/ru/trip-planner/` titles over 70 chars) are byte-identical to
the ones in the existing `dist/` and originate in `seo_trip_planner.yml`, which is out of scope.
A scan of all 2 292 built pages found **0** hyphen-glued Georgian case suffixes, **0** leaked
`{placeholder}` tokens, and **0** stranded punctuation / double spaces in any `<title>` or
`<meta name="description">`.

---

## A. `content/settings/ka_forms.yml`

Covers all **40** names in `places.yml` and all **11** in `content/regions/*.yml`, keyed on the
rendered Georgian string, with `gen` / `loc` / `abl` / `dat` for each. Verified with
`build.ka_case()` after creation: every key resolves, none is missed.

Most entries agree with the algorithmic fallback and are present only as a guard. These are the
ones where **the fallback is wrong** and the table actually changes output:

| Name | Case | Fallback produced | Correct (now in table) | Why |
|------|------|-------------------|------------------------|-----|
| ახალციხე (Akhaltsikhe) | gen | `ახალციხეს` | `ახალციხის` | `-ე` truncates before `-ის`; the rule engine treats `-ე` as a stable vowel stem |
| ახალციხე | abl | `ახალციხედან` | `ახალციხიდან` | same truncation before `-იდან` |
| საჩხერე (Sachkhere) | gen | `საჩხერეს` | `საჩხერის` | same |
| საჩხერე | abl | `საჩხერედან` | `საჩხერიდან` | same |
| ყვარელი (Kvareli) | gen | `ყვარელის` | `ყვარლის` | syncopating stem — the stem vowel drops (`ყვარელ-` → `ყვარლ-`) |
| ყვარელი | abl | `ყვარელიდან` | `ყვარლიდან` | same |
| სტეფანწმინდა (ყაზბეგი) | gen | `სტეფანწმინდა (ყაზბეგი)ის` | `სტეფანწმინდის (ყაზბეგის)` | the display name ends in `)`; no ending can attach to it |
| სტეფანწმინდა (ყაზბეგი) | loc | `სტეფანწმინდა (ყაზბეგი)ში` | `სტეფანწმინდაში (ყაზბეგში)` | as above |
| სტეფანწმინდა (ყაზბეგი) | abl | `სტეფანწმინდა (ყაზბეგი)იდან` | `სტეფანწმინდიდან (ყაზბეგიდან)` | as above |
| სტეფანწმინდა (ყაზბეგი) | dat | `სტეფანწმინდა (ყაზბეგი)ს` | `სტეფანწმინდას (ყაზბეგს)` | as above |

**All 11 regions**: the fallback is already correct for every one of them (including the hyphenated
`მცხეთა-მთიანეთი`, `რაჭა-ლეჩხუმი`, `სამცხე-ჯავახეთი` and the two-word `ქვემო ქართლი`,
`შიდა ქართლი`, `სამეგრელო-ზემო სვანეთი`). They are listed anyway so a future rule change cannot
silently break the region hubs.

**Still recommended (out of scope here):** `places.yml → stepantsminda.ka` should become
`სტეფანწმინდა` with `ყაზბეგი` carried as a separate alias field, per TRANSLATION_QA §3.1. The
table above makes the current value safe, but a parenthesis inside a declinable name stays fragile.

---

## B. Georgian (ka)

### B.1 Hyphen / concatenation artefacts

| File · key | Before | After |
|---|---|---|
| `seo_meta.yml` `car_rental_location.airport.ka.title` | `{city}ის აეროპორტში მანქანის დაქირავება ({iata})` → *თბილისიის…* | `{city_gen} აეროპორტში მანქანის გაქირავება ({iata})` → *თბილისის აეროპორტში…* |
| `seo_meta.yml` `car_rental_location.airport.ka.description` | `იქირავეთ ავტომობილი {city}ის აეროპორტში…` | `იქირავეთ ავტომობილი {city_gen} აეროპორტში…` |
| `seo_meta.yml` `car.ka.title` | `{name_gen} დაქირავება…` → *BMW 5 Seriesის* | `{name}-ის გაქირავება…` → *BMW 5 Series-ის* |
| `seo_meta.yml` `car_rental_category.ka.title` | `{category_gen} დაქირავება…` → *კროსოვერი / SUVის*, *მაღალი გამავლობის 4x4ის* | `{category} — გაქირავება საქართველოში, {price} ₾-დან` |
| `seo_meta.yml` `car_rental_category.ka.description` | `{count} {category} მოდელი…` (two nominatives in a row) | `{count} მოდელი კატეგორიაში „{category}“…` |

`{name_gen}` and `{category_gen}` were the two places where the *declension machinery itself* made
things worse: `ka_case()` is a rule engine for Georgian stems, and both of these placeholders carry
Latin-tailed values (`BMW 5 Series`, `Toyota Prius (ჰიბრიდი)`, `კროსოვერი / SUV`,
`მაღალი გამავლობის 4x4`). A Latin/numeral stem takes a **hyphen** before the ending, so `{name}-ის`
is right and `{name_gen}` is not. For the category label the genitive was dropped entirely in favour
of a dash construction, because 2 of the 6 labels end in `SUV` / `4x4` and no `places:`/`regions:`
table can legitimately hold them. All 6 category titles now render correctly and under 70 chars.

Everything else already used `{region_loc}` / `{city_loc}` / `{name_loc}` / `{place_abl}` correctly.

### B.2 Terminology — `გაქირავება` (company voice) vs `დაქირავება` (customer voice)

| File · key | Before | After |
|---|---|---|
| `seo_meta.yml` `home.ka.title` | `ავტომობილის დაქირავება და მარშრუტის დაგეგმვა…` | `ავტომობილების გაქირავება და მარშრუტის დაგეგმვა…` |
| `seo_meta.yml` `car.ka.title` | `…დაქირავება საქართველოში` | `…გაქირავება საქართველოში` |
| `seo_meta.yml` `blog.ka.description` | `…ავტომობილის დაქირავებასა და მართვაზე` | `…ავტომობილის გაქირავებასა და მართვაზე` |
| `seo_meta.yml` `faq.ka.title` | `…— მანქანის დაქირავება` | `…— მანქანის გაქირავება` |
| `seo_meta.yml` `faq.ka.description` | `…პასუხი მანქანის დაქირავებაზე…` | `…პასუხი მანქანის გაქირავებაზე…` |
| `seo_meta.yml` `car_rental_hub.ka.title` | `მანქანის დაქირავება საქართველოში` | `მანქანის გაქირავება საქართველოში` (now matches the H1) |
| `seo_meta.yml` `car_rental_location.city.ka.title` | `მანქანის დაქირავება {city_loc}` | `მანქანის გაქირავება {city_loc}` |
| `seo_ui.yml` `car_rental.ka` | `მანქანის დაქირავება` | `მანქანის გაქირავება` |
| `seo_ui.yml` `rental_terms.ka` | `დაქირავების პირობები` | `გაქირავების პირობები` |
| `seo_ui.yml` `one_way.ka` | `ცალმხრივი დაქირავება` | `ცალმხრივი გაქირავება` |
| `seo_ui.yml` `rent_car_for_trip.ka` | `დაიქირავეთ მანქანა ამ მოგზაურობისთვის` | `იქირავეთ მანქანა ამ მოგზაურობისთვის` (QA §3.2 keeps `იქირავეთ` as the CTA verb) |

After the rebuild, every remaining `დაქირავება` in `/ka/` is legitimate customer-voice prose in
files outside this scope (`ვის შეუძლია მანქანის დაქირავება`, `ცხენების დაქირავება`, blog posts).

### B.3 Terminology — one word for "drive time" (KA14), one for the itineraries hub (KA16/KA17)

`სამგზავრო დრო` is gone from `seo_meta.yml` (0 occurrences). Running text now uses
`მგზავრობის დრო`, totals use `მართვის დრო`:

| File · key | Before | After |
|---|---|---|
| `seo_meta.yml` `planner.ka.description` | `…რეალური სამგზავრო დროითა…` | `…რეალური მართვის დროითა…` |
| `seo_meta.yml` `routes_hub.ka.description` | `…მანძილით, სამგზავრო დროით…` | `…მანძილით, მართვის დროით…` |
| `seo_meta.yml` `route.default.ka.description` | `({drive} მთლიანი სამგზავრო დრო)` | `({drive} მთლიანი მართვის დრო)` |
| `seo_meta.yml` `route.by_purpose.performance.ka.description` | `თავად სამგზავრო პროცესზეა აგებული` | `თავად მართვის პროცესზეა აგებული` |
| `seo_meta.yml` `region.ka.description` | `სამგზავრო დრო თბილისიდან` | `მგზავრობის დრო თბილისიდან` |
| `seo_meta.yml` `car_rental_location.city.ka.description` | `…კატეგორია და სამგზავრო დრო` | `…კატეგორია და მგზავრობის დრო` |
| `seo_meta.yml` `itinerary.ka.description` | `…გეგმით, სამგზავრო დროითა…` | `…გეგმით, მართვის დროითა…` |
| `seo_ui.yml` `total_drive.ka` | `სულ მართვაში` | `სულ მართვის დრო` |
| `seo_ui.yml` `trip_planner.ka` | `მოგზაურობის დამგეგმავი` | `მარშრუტის დამგეგმავი` (KA17) |
| `seo_meta.yml` `planner.ka.title` | `საქართველოს მოგზაურობის დამგეგმავი — ააგე მარშრუტი` | `მარშრუტის დამგეგმავი საქართველოში — ააგეთ თქვენი გზა` (keeps the title in step with the nav label) |
| `seo_ui.yml` `itineraries.ka` | `მზა მარშრუტების გეგმები` | `მოგზაურობის გეგმები` |
| `seo_meta.yml` `itineraries_hub.ka.description` | `{count} შერჩეული მარშრუტის გეგმა…` | `{count} შერჩეული მოგზაურობის გეგმა…` |

**Deviation from QA, deliberate.** KA16 proposes `მზა მარშრუტები` for `itineraries.ka`. That string
is already `ready_made_routes.ka`, and `build.py:3997–3998` renders both labels as **adjacent
buttons** on `/ka/trip-planner/` (one to `/tours/`, one to `/itineraries/`). Taking KA16 literally
would have produced two identical buttons and two near-identical Georgian page titles for
`/ka/tours/` and `/ka/itineraries/` — a cannibalisation risk QA did not consider. `მოგზაურობის
გეგმები` removes the doubling KA16 objected to (`მარშრუტების გეგმები`) while keeping the two hubs
distinct. Verified in the build: `/ka/tours/` = *მზა მარშრუტები*, `/ka/itineraries/` =
*მოგზაურობის გეგმები*.

---

## C. Russian (ru)

Russian needs three forms (1 / 2–4 / 5+, with 11–14 always taking the third) and `build.py` has no
count-selection helper. Every fix below therefore **detaches the numeral from the counted noun** so
one string is correct for every value, rather than for part of the range.

| File · key | Before (rendered) | After | Range fixed |
|---|---|---|---|
| `route.default.ru.title` + all 12 `by_purpose.*.ru.title` | `…, 2 дней, 285 км`; `…, 1 дней` | `{name} — {days}-дневный исторический маршрут, {km} км` (the adjective is invariant) | days 1, 2, 3, 4 — **23 of 32 route titles** |
| `route.default.ru.description` | `{name} — это {km} км за {days} дней` | `{name} — {days}-дневный маршрут на {km} км` | as above |
| `itinerary.ru.title` | `Маршрут по Грузии на 3 дней` | `{days}-дневный маршрут по Грузии` | days 3 |
| `itinerary.ru.description` | `…на {days} дней — {km} км и {stops} остановок` | `{days}-дневный маршрут по Грузии — {km} км, остановок: {stops}. План по дням…` | all counts |
| `region.ru.title` | `Кахетия — 33 достопримечательностей` | `{name} — достопримечательности, всего {count}` | counts ending 2/3/4 — 4 of 11 regions |
| `region.ru.description` | `33 мест для посещения в регионе {name}` | `Все места для посещения в регионе {name} на одной карте` | all counts |
| `car_rental_category.ru.title` | `Аренда Эконом-класс в Грузии` (nominative after `аренда`, capitalised mid-sentence) | `Аренда авто «{category}» в Грузии — от {price} ₾/день` | all 4 category pages |
| `car_rental_category.ru.description` | `3 моделей категории Кроссовер / SUV` | `Модели категории «{category}» в Грузии от {price} ₾ в день, всего {count}` | every category (all hold 3 cars) |
| `car.ru.description` | `{seats} мест` → `3 мест` | `число мест — {seats}` | 2 of 17 cars (seats = 3) |
| `routes_hub.ru.title` | `— {count} путешествий` | `— всего {count}` | latent (`routes_hub` is unwired) |
| `routes_hub.ru.description` | `{count} готовых автомобильных маршрутов` | `Готовые автомобильные маршруты по Грузии, всего {count} —` | latent |
| `itineraries_hub.ru.description` | `{count} готовых маршрутов путешествия` | `Готовые маршруты путешествия…, всего {count} —` | correct at 5 today, now safe at any count |
| `seo_ui.yml` `popular_routes_from.ru` | `Популярные маршруты из {place}` → *из Аэропорт Тбилиси* | `{place}: популярные маршруты` | 6 rental-location pages (3 of them airports, where `из` + an undeclinable multi-word label was outright ungrammatical) |

`{seats} мест` → `число мест — {seats}` also removes the same defect the QA doc did not catch:
`content/cars/*.yml` contains `seats: 3` twice, and `3 мест` needs `3 места`.

Rendered checks: `Воды Боржоми… — 1-дневный маршрут…`, `Два семейных дня… — 2-дневный прибрежный
маршрут`, `Кахетия — достопримечательности, всего 33`, `3-дневный маршрут по Грузии — 420 км,
остановок: 6.`, `Mitsubishi Delica D:5 … число мест — 8`.

**Cost:** the adjectival form is ~1 char longer than `{days} дней`, so `_trim_title` now drops the
`| RentUp` suffix on 3 of 32 ru route titles that were already at the 70-char boundary
(`kazbegi-hiking-base`, `svaneti-alpine-circuit`, `kakheti-wine-loop`). That is the trimmer's
designed degradation and was judged a better trade than 23 ungrammatical titles.

**Not applied (latent, correct for the live data):** RU9 — `car_rental_location.city.ru`
`в {city}`. The three live rental cities (Тбилиси, Кутаиси, Батуми) are indeclinable in Russian, so
the string is correct today; it needs a `ru_in` field in `places.yml` (not writable here) before a
declinable fourth city is added. RU10 (`Имерети` vs `Имеретия` in `content/routes/*.yml`) and RU11
(`прокат` as a secondary term) are content-file work, also out of scope.

---

## D. Arabic (ar)

Arabic has four agreement patterns (1 / 2 dual / 3–10 broken plural / 11–99 accusative singular).
As with Russian, the fix is to move the numeral out of the counted-noun slot — either as the
labelled value `الأيام: {days}` / `عدد المحطات {stops}` / `عددها {count}`, or by dropping the
counted noun where km and drive time already carry the scale.

| File · key | Before (rendered) | After | Range fixed |
|---|---|---|---|
| `route.default.ar.title` + all 12 `by_purpose.*.ar.title` | `…، 2 أيام، 285 كم`; `…، 1 أيام` | `{name} — مسار تاريخي، {km} كم، الأيام: {days}` | days 1 and 2 — **9 of 32 route titles** |
| `route.default.ar.description` | `على مدى {days} أيام` | (removed; km + drive time retained) | as above |
| all 12 `by_purpose.*.ar.description` | `لمدة {days} أيام` | (removed) | as above |
| `itinerary.ar.title` | `برنامج رحلة جورجيا لمدة 14 أيام` | `برنامج رحلة جورجيا — الأيام: {days}` | days 14 |
| `itinerary.ar.description` | `لمدة {days} أيام … {stops} محطة توقف` | `الأيام: {days}، يغطي {km} كم، وعدد المحطات {stops}` | days 14; **stops 6** (`6 محطة` needed `محطات`) on 2 of 5 itineraries |
| `car_rental_category.ar.description` | `3 طرازاً من فئة كروس أوفر / SUV` | `طرازات من فئة «{category}» متاحة في جورجيا …، عددها {count}` | every category (all hold 3) |
| `itineraries_hub.ar.description` | `5 برنامج رحلة مُعدّ لجورجيا` | `برامج رحلات مُعدّة لجورجيا …، عددها {count}` | count 5 |

Bidi: `الأيام: {days}` is safe — a single EN run adjacent to Arabic text resolves to AN and the
colon takes the paragraph direction, so nothing reverses. No en dash was introduced between two
numbers anywhere.

**Not applied:** AR5 — `routes_hub.ar` `{count} مساراً` is correct at 32 and QA explicitly says
"no change"; it is left as documented. AR6 (`أوبا` → `بوبا`) lives in
`content/itineraries/georgia-5-days.yml`, AR7/AR8 (digit mixing, `اليومان ١-٢`) in
`content/itineraries/*.yml`, AR9 in `seo_trust.yml` — all outside the writable set.
AR10 (`لاري` instead of `₾`) is confirmed as a deliberate rule and left alone.

---

## E. Hebrew (he)

| File · key | Before (rendered) | After | Range fixed |
|---|---|---|---|
| `route.default.he.title` + all 12 `by_purpose.*.he.title` | `…, 2 ימים, 285 ק״מ`; `…, 1 ימים` | `{name} — מסלול היסטורי, {km} ק״מ, ימים: {days}` | days 1 and 2 — **9 of 32 route titles** |
| all 12 `by_purpose.*.he.description` | `הוא מסלול היסטורי בן {days} ימים:` | `הוא מסלול היסטורי:` (count now carried by the title label) | as above |
| `route.default.he.description` | `{name} כולל {km} ק״מ על פני {days} ימים ({drive} נסיעה כוללת)` | `{name} כולל {km} ק״מ ו-{drive} נסיעה כוללת` | as above |
| `car_rental_category.he.description` | `3 דגמי קרוסאובר / SUV זמינים` | `דגמי {category} זמינים בגאורגיה … סה״כ {count}` | HE3 — every category |

`itinerary.he` (`ל-{days} ימים`, days 3–14) and `region.he` / `routes_hub.he` (counts ≥ 3) are
already correct for the whole live range and were left unchanged, per QA §6.

HE4 (ASCII `"`/`'` as gershayim/geresh) lives in `content/itineraries/*.yml` and
`content/routes/*.yml`; HE5 in `seo_trust.yml` — both out of scope. `seo_meta.yml` already uses the
correct `ק״מ` (U+05F4) throughout.

---

## F. Persian (fa)

`seo_meta.yml` and `seo_ui.yml` were audited character by character: **zero** Eastern Arabic-Indic
digits (`۰–۹` / `٠–٩`) in either file. Both packs are already 100 % Western-digit, which is the
system this report recommends keeping — it is the safer one for search and it is what the templates
emit into every locale.

| File · key | Before | After | Reason |
|---|---|---|---|
| `seo_ui.yml` `popular_routes_from.fa` | `سفرهای جادهٔ محبوب از {place}` | `سفرهای جاده‌ای محبوب از {place}` | the ezafe turned "road trips" into "the road's popular trips"; `جاده‌ای` is the adjective |

Persian numerals need no agreement and every `fa` template was already correct
(`{days} روز`, `{days} روزه`, `{count} مدل`, `{count} جاذبهٔ گردشگری`) — nothing else changed.

FA4 (`ما چه کسی هستیم`) is in `seo_trust.yml`, which is not writable here.
`seo_meta.yml → about.fa` already reads `ما که هستیم`, so the two packs now agree once
`seo_trust.yml` is corrected. FA1/FA2/FA3 (itinerary and attraction prose) and FA7
(`فقط ۴×۴` vs `فقط 4x4`) are content-file work; `seo_ui.yml → road.4x4_only.fa` is already the
Western `فقط 4x4`. FA6 confirmed: the en dashes in `seo_ui.yml → season.*` sit between two Persian
month names, are RTL on both sides, and were deliberately **not** touched.

---

## G. Raw YAML tokens

`seo_meta.yml` and `seo_ui.yml` contain **no** raw enum or field name in any user-visible string in
any language. The only occurrences of `car_category`, `best_season`, `4x4_only`, `year-round` in
these two files are YAML **keys** and structural comments, which never render. Verified after the
build with a token sweep across all 2 292 pages.

Tokens that still reach `dist/` come from files this task may not write:

| Token | Pages | Source | Fix |
|---|---|---|---|
| `car_category` | 12 | `content/itineraries/*.yml → <lang>.tips[]` | TRANSLATION_QA Appendix E.4 |
| `best_season` | 5 | `content/itineraries/*.yml → <lang>.tips[]` | Appendix E.4 |
| `year-round` (in prose) | 1 | `content/itineraries/georgia-10-days.yml` | Appendix E.4 |
| `year-round` (as a rendered **label**) | 19 | **`content/settings/travel.yml`** — see below | see below |

**New finding, not in TRANSLATION_QA.** Route and attraction pages print the season through
`tl(lang, "season", …)` (`build.py:1689`, `:1863`, `:2334`, `:2750`), which reads
`travel.yml → <lang>.season`. That map is missing **four** of the eight `best_season` values used in
content — `year-round`, `april-october`, `july-september`, `march-november` — **in all six
languages**, so the raw key is printed as the label. `seo_ui.yml → season` already carries correct
translations for all eight values in all six languages (it is consumed only by `su("season", …)` at
`build.py:3871`, for itineraries). The fix is one of:

1. point `tl(lang, "season", …)` at `SEO_UI["season"]` when the key is absent from `travel.yml`, or
2. copy the four missing keys from `seo_ui.yml → season` into `travel.yml → <lang>.season`.

Both touch files outside this task's writable set. **19 pages are affected today.**

---

## H. RTL en-dash time ranges — not fixable from these two files

Neither `seo_meta.yml` nor `seo_ui.yml` contains a time range. A scan of both files found no
`HH:MM–HH:MM` pattern and no en dash between two digits in any `ar` / `he` / `fa` string. The
`09:00–21:00` / `22:00–08:00` defect (TRANSLATION_QA §8, 781 pages) lives entirely in:

`content/settings/ui.yml`, `content/settings/rental_policy.yml`,
`content/settings/seo_car_rental.yml`, `content/pages/contact.yml`, `content/pages/faq.yml`,
`content/pages/index.yml`, `content/pages/pricing.yml` — **all out of scope.**

**One additional RTL dash found while verifying the build**, also out of scope:
`seo_categories.yml → minivan.he.meta_description` renders `ל-7–9 נוסעים` on
`/he/car-rental/minivan/`. An en dash between two Western digits inside an RTL paragraph is bidi
class ON, resolves to RTL under UAX#9 N1, and paints as `9–7`. It needs `ל-7 עד 9 נוסעים` (or a
hyphen). This is the only such string left in the whole built site.

---

## I. Georgian vocabulary items that could not be fixed here

The four Georgian word-level fixes requested (`ექსცესი` → `ფრანშიზა`, `ღრმულები` → `მღვიმეები`,
`სანახაობები` → a natural phrase for "places to visit", and the non-word `განვერიანდი`) do **not**
occur anywhere in `seo_meta.yml` or `seo_ui.yml`. Located for whoever owns those files:

| Term | Occurrences | Files |
|---|---|---|
| `ექსცესი` | 7 | `seo_car_rental.yml:227,231,234`; `seo_categories.yml:40,294,554,838` |
| `ღრმულ*` | 7 | `content/routes/imereti-caves-canyons.yml` (incl. the route **name**, line 90); `content/attractions/{oniore-waterfall,navenakhevi-cave,prometheus-cave,mgvimevi-monastery}.yml` |
| `სანახაობ*` | 12 | `seo_trip_planner.yml:739` (an `h2`); `content/settings/planner.yml:112`; 9 `content/attractions/*.yml`; `content/posts/avtomobilit-mogzauroba-saqartveloshi.yml:13`; `content/regions/kvemo-kartli.yml:16` |
| `განვერიანდი` | **0** | not present anywhere in the repository |

Note that several `სანახაობა` uses are idiomatic and correct in place ("a sight", "a spectacle");
only the list-heading uses (`seo_trip_planner.yml:739` `h2: სანახაობები`,
`planner.yml:112` `საქართველოს მთავარი სანახაობები`) read as "spectacles" where
`სანახავი ადგილები` ("places worth seeing") is meant. `seo_meta.yml → region.ka.description`
already uses `სანახავი ადგილი`, so aligning those two strings would make the pack consistent.

---

## J. What in TRANSLATION_QA is still open

| Item | Where it lives | Status |
|---|---|---|
| X1 `photo_by:` label, 1 488 pages | `build.py:1537`, `:1570` | **open** — build.py not writable here |
| X4 raw enums in tips, 66 pages | `content/itineraries/*.yml`, `seo_categories.yml` | open |
| X5 `road` / `car_category` in trust copy | `seo_trust.yml` | open (not yet wired, fix before wiring) |
| X6 "rebrand from RentUp to RentUp" note | `seo_trust.yml` | open |
| §8 en-dash time ranges, 781 pages | `ui.yml`, `pages/*.yml`, `seo_car_rental.yml` | open |
| §3.3 `ქირაობა` as a countable noun, 20 strings | `seo_car_rental.yml`, `seo_trip_planner.yml` | open |
| KA10 `ოთხთვალა` → `ოთხივე წამყვანი თვალი` | `seo_categories.yml` | open |
| KA11–KA13, KA18 | `content/itineraries/*.yml` | open |
| KA19 brand suffix `RentUp.ge` vs `RentUp` | `seo_categories.yml` | open |
| RU10, RU11, RU12 | `content/routes/*.yml`, `content/itineraries/*.yml` | open |
| AR6, AR7, AR8, AR9 | `content/itineraries/*.yml`, `seo_trust.yml` | open |
| HE4, HE5 | `content/itineraries/*.yml`, `content/routes/*.yml`, `seo_trust.yml` | open |
| FA1, FA2, FA3, FA4, FA5 | `content/itineraries/*.yml`, `content/attractions/*.yml`, `seo_trust.yml` | open |
| **New:** `travel.yml → season` missing 4 keys × 6 languages, 19 pages | `content/settings/travel.yml` or `build.py` | **new finding, open** |
| **New:** `ל-7–9 נוסעים` bidi reversal | `seo_categories.yml` | **new finding, open** |

Note that `car_rental_location.*`, `car_rental_category.*` and `car_rental_hub.*` titles and
descriptions are overridden today by `meta_title` / `meta_description` in `seo_car_rental.yml` and
`seo_categories.yml` (`build.py:3717`, `:3777`). The corrections applied here to those templates are
therefore latent on most of those pages until the overrides are removed or themselves corrected —
they are still worth having, and the `region`, `route`, `attraction`, `itinerary`, `car`,
`home`, `faq`, `terms` and `itineraries_hub` templates render live on every page.
