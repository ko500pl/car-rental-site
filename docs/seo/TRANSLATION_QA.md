# TRANSLATION_QA — rentup.ge multilingual content review

**Date:** 2026-08-29
**Scope:** the content packs generated most recently and never language-reviewed —
`content/settings/seo_meta.yml`, `seo_ui.yml`, `seo_car_rental.yml`, `seo_categories.yml`,
`seo_trip_planner.yml`, `seo_trust.yml`, `content/itineraries/*.yml` — plus everything they
render into `dist/`.
**Languages:** en (root), ka, ru, fa, he, ar.
**Method:** read every template string in the packs, resolved every placeholder against the real
data (`places.yml` 40 places, 11 region files, `categories.yml` 6 categories, 32 routes,
257 attractions, 5 itineraries, 17 cars), then verified the claims against the built HTML in
`dist/`. Every "current string" below is either the literal YAML value or a literal string
copied out of a built page.

**Nothing in this repository was modified.** This file is the only output; all YAML and
`build.py` remain read-only. Every fix is given as a paste-ready replacement in the appendices.

---

## 1. Verdict per language

| Lang | Fluency of the prose | Correctness of the *generated* strings | Safe to leave live? |
|------|---------------------|-----------------------------------------|---------------------|
| en | Good — natural, specific, no MT feel | 5 itinerary meta descriptions print raw `{days}/{km}/{stops}`; `car_category`, `suv`, `offroad`, `best_season`, `4x4_only`, `year-round` appear as raw enum tokens in body prose | Mostly |
| ka | Hand-written quality in `seo_car_rental` / `seo_categories`; several MT-flavoured passages in `itineraries` | **Broken.** Case suffixes are glued on with a hyphen (`კახეთი-ში`, `თბილისი-ში`, `ეკონომ კლასი-ის`) on ~200 pages | **No** |
| ru | Good, idiomatic prose | **Broken.** No numeral agreement anywhere (`2 дней`, `3 моделей`, `32 достопримечательностей`); category names left in the nominative after `Аренда` | **No** |
| ar | Good MSA prose | Numeral–noun agreement wrong in 3 template families (`2 أيام`, `1 أيام`, `14 أيام`, `3 طرازاً`, `5 برنامج`); one proper name mistranslated | No (titles only) |
| he | Good, natural | `1 ימים` / `2 ימים` on 9 route titles; otherwise clean | Borderline |
| fa | Good, natural | Numerals are correct (Persian needs no agreement), but Eastern/Western digits are mixed on 309 of 349 pages | Borderline |
| **all RTL** | — | Time ranges written with an en dash reverse visually (`09:00–21:00` renders `21:00–09:00`) on **781** pages | **No** |
| **all 6** | — | The literal string `photo_by:` is printed as the image-caption label on **1 488** pages | **No** |

Severity key used below: **S1** = wrong text visible to users/Google now; **S2** = wrong grammar
that a native speaker will notice; **S3** = consistency / typography.

---

## 2. Cross-language defects (hit every locale)

| # | Sev | File · key path | Current (as rendered) | Corrected | Reason |
|---|-----|-----------------|------------------------|-----------|--------|
| X1 | S1 | `content/settings/planner.yml` → `<lang>.ui.photo_by` (values are fine); consumed at `build.py:1537` and `build.py:1570` | `<figcaption>photo_by: Wikimedia Commons · CC BY-SA 4.0</figcaption>` — on 1 488 pages, all 6 languages | `<figcaption>ფოტო: …</figcaption>` / `Photo:` / `Фото:` / `عکس:` / `צילום:` / `صورة:` | `te(lang,"photo_by")` reads `TRAVEL[lang]["exp"]` (`travel.yml`), but `photo_by` is defined in `planner.yml → <lang>.ui`. The lookup misses and `te()` returns the key itself. Translations already exist — only the lookup is wrong. |
| X2 | S1 | `content/settings/seo_meta.yml` → `templates.itinerary.<lang>.description`; caller `build.py:3694` | `A {days}-day Georgia itinerary covering {km} km and {stops} stops…` / `Маршрут по Грузии на {days} дней — {km} км и {stops} остановок…` / `מסלול טיול בגאורגיה ל-{days} ימים — {km} ק״מ ו-{stops} תחנות…` | see Appendix E | `seo_meta("itinerary", …)` is never passed `stops`, and no itinerary YAML has a `stops:` field. `fill()` swallows the `KeyError` and returns the **whole raw template**, so all three placeholders leak. 5 itineraries × 6 languages = 30 meta descriptions. |
| X3 | S1 | `content/settings/seo_ui.yml` → `popular_routes_from.<lang>`; caller `build.py:3505` | `<h2>Популярные маршруты из {place}</h2>`, `<h2>პოპულარული მარშრუტები {place}-დან</h2>`, `<h2>مسلولי טיול פופולריים מ{place}</h2>`, `<h2>رحلات برية شائعة من {place}</h2>` | `su()` must be `.format(place=…)`d, or the heading must drop the placeholder (Appendix E) | `su()` returns the string verbatim — it has no formatting step. A raw `{place}` token is visible in an `<h2>` on 36 pages (6 rental locations × 6 languages). |
| X4 | S1 | `content/itineraries/*.yml` → `<lang>.tips[]`; `content/settings/seo_categories.yml` → `<lang>.when_to_choose` / `limitations` | ka: `ამ მარშრუტისთვის car_category არის suv, მაგრამ … offroad/მხოლოდ-4x4-ადაა შეფასებული`; ru: `car_category маршрута — suv, но участок … отмечен как offroad/только 4x4`; he: `קטגוריית הרכב של המסלול היא suv`; ar: `فئة السيارة لهذا المسار هي دفع رباعي (suv)`; en: `best_season is June–September only`, `not the 4x4_only tracks beyond` | Appendix E | Raw YAML field names and enum values (`car_category`, `best_season`, `suv`, `offroad`, `4x4_only`, `year-round`) written into user-facing prose. Counted in `dist/`: `car_category` 12 pages, `offroad` 20, `4x4_only` 16, `year-round` 23, `best_season` 5. |
| X5 | S1 | `content/settings/seo_trust.yml` → `<lang>.editorial.policy_body` (all 6) | ka `…იმავე road და car_category ველებიდან…`; ru `…тех же полей road и car_category…`; he `…אותם שדות road ו-car_category…`; ar `…نفس حقلَي road وcar_category…`; fa `…همان فیلدهای road و car_category…` | Appendix E | The E-E-A-T "how this page was made" copy names internal YAML fields. Not yet wired into `build.py` (`SEO_TRUST` is loaded but never read), so it is not live — must be fixed **before** it is wired. |
| X6 | S3 | `content/settings/seo_trust.yml` header comment, lines 25–30 | `site.yml → rental_brand is currently "RentUp" … seo_meta.yml records a planned rebrand to "RentUp"` | Delete the paragraph, or restore the two distinct brand names it was written about | A "rebrand from RentUp to RentUp" is the residue of a blanket find-and-replace. The note now instructs a future editor to perform a no-op. |

---

## 3. Georgian (ka) — primary market

### 3.1 The headline defect: hyphenated case suffixes

Georgian attaches case suffixes directly to the stem and **drops the nominative `-ი`** first:
`კახეთი` + locative → `კახეთში`, not `კახეთი-ში`. A hyphen before a case suffix is correct **only**
when the stem is Latin script, an acronym or a numeral (`RentUp-ში`, `SUV-ის`, `4x4-ის`, `3-დღიანი`).
The generated templates hyphenate Georgian stems, producing a form no Georgian speaker writes.

The proof that this is a templating artefact and not an editorial choice is on one page:
`dist/ka/car-rental/batumi/index.html` carries the hand-written `<h1>მანქანის გაქირავება ბათუმში</h1>`
directly above the templated `<title>მანქანის დაქირავება ბათუმი-ში | RentUp</title>`.

| # | Sev | File · key path | Current string | Corrected string | Reason | Pages hit |
|---|-----|-----------------|----------------|------------------|--------|-----------|
| KA1 | S1 | `seo_meta.yml` → `templates.attraction.by_type.{fortress,monastery,nature,museum,lake,spa,archaeology,winery,beach,cave,waterfall,canyon,ski,theatre}.ka.description` | `{name} — მონასტერი {region}-ში, {km} კმ თბილისიდან` → renders `…მონასტერი მცხეთა-მთიანეთი-ში…` | `{name} — მონასტერი {region_in}, {km} კმ თბილისიდან` with `{region_in}` = pre-inflected locative (Appendix A) | Hyphen + undropped nominative `-ი`. Two errors in one token. | **195** attraction pages |
| KA2 | S1 | `seo_meta.yml` → `templates.car_rental_location.city.ka.title` | `მანქანის დაქირავება {city}-ში \| RentUp` → `…ბათუმი-ში` | `მანქანის გაქირავება {city_in} \| RentUp` → `…ბათუმში` | same | 3 (highest-value commercial pages) |
| KA3 | S1 | `seo_meta.yml` → `templates.car_rental_location.city.ka.description` | `აიღეთ ავტომობილი {city}-ში: რომელი მარშრუტები იწყება აქედან…` | `აიღეთ ავტომობილი {city_in}: რომელი მარშრუტები იწყება აქედან…` | same | 3 |
| KA4 | S1 | `seo_meta.yml` → `templates.car_rental_location.airport.ka.title` | `{city}ის აეროპორტში მანქანის დაქირავება ({iata})` → `თბილისიის აეროპორტში…` | `{city_of} აეროპორტში მანქანის გაქირავება ({iata})` → `თბილისის აეროპორტში…` | Genitive of `თბილისი` is `თბილისის` — the stem `-ი` must be dropped before `-ის`. The template concatenates `ის` onto the full nominative, giving `თბილისიის`. | 3 |
| KA5 | S1 | `seo_meta.yml` → `templates.car_rental_location.airport.ka.description` | `იქირავეთ ავტომობილი {city}ის აეროპორტში ({iata})…` | `იქირავეთ ავტომობილი {city_of} აეროპორტში ({iata})…` | same | 3 |
| KA6 | S1 | `seo_meta.yml` → `templates.car_rental_category.ka.title` | `{category}-ის დაქირავება საქართველოში — {price} ₾-დან` → `ეკონომ კლასი-ის…`, `მინივენი-ის…` | `{category_of} გაქირავება საქართველოში — {price} ₾-დან` → `ეკონომ კლასის გაქირავება…` | Category labels are Georgian words, so the hyphen is wrong and the nominative must be dropped. `მაღალი გამავლობის 4x4-ის` happens to be correct only because that label ends in a numeral. | 3 of 4 category pages |
| KA7 | S1 | `seo_meta.yml` → `templates.car_rental_category.ka.description` | `{count} {category} მოდელი საქართველოში…` → `3 კროსოვერი / SUV მოდელი` | `{count} {category_of} მოდელი საქართველოში…` → `3 კროსოვერის / SUV-ის მოდელი` | A noun modifying another noun takes the genitive in Georgian; `კროსოვერი მოდელი` is two nominatives in a row. | 4 |
| KA8 | S1 | `seo_ui.yml` → `popular_routes_from.ka` | `პოპულარული მარშრუტები {place}-დან` | `პოპულარული მარშრუტები {place_from}` (pre-inflected ablative, Appendix A) | Same hyphen artefact; `თბილისი-დან` → `თბილისიდან`. Compounded by X3 (the placeholder is not substituted at all today). | 6 |
| KA9 | S2 | `seo_meta.yml` → `templates.region.ka.description` | `{count} სანახავი ადგილი {name}-ში: სამგზავრო დრო თბილისიდან…` | `{count} სანახავი ადგილი {name_in}: მგზავრობის დრო თბილისიდან…` | Same artefact. Currently latent: `build.py:2050–2053` overwrites `desc` with the region body, so this template string never reaches a page — it will the moment that line changes. | 0 today, 11 when wired |

`places.yml → stepantsminda.ka` is `სტეფანწმინდა (ყაზბეგი)`. No suffix can be attached to a string
ending in a parenthesis, so this entry cannot be inflected at all in any template. Recommendation:
set the display name to `სტეფანწმინდა` and carry `ყაზბეგი` as a separate alias field.

### 3.2 Terminology: `დაქირავება` / `გაქირავება` / `ქირაობა`

All three are in use, and on the flagship page they collide inside a single document:

```
dist/ka/car-rental/index.html
  <title>მანქანის დაქირავება საქართველოში | RentUp</title>   ← seo_meta.yml
  <h1>მანქანის გაქირავება საქართველოში</h1>                  ← seo_car_rental.yml
  seo_car_rental.yml meta_title (overridden, never rendered): მანქანის ქირაობა საქართველოში
```

**Decision — standardise on `გაქირავება`.** It is the verb of the party who *hands the car over*,
which is what this site is: `გა-` is the outward-directed preverb (`გააქირავა` = "rented it out"),
while `და-` is inward-directed (`დაიქირავა` = "hired it"). A rental company's own service pages
describe the company's action, so `ავტომობილების გაქირავება` is the correct commercial register, and
it is already what every hand-written H1 in `seo_car_rental.yml` and `seo_categories.yml` uses. Keep
`დაქირავება` **only** where the grammatical subject is the customer (the imperative `იქირავეთ`
stays as-is, and it is the right CTA verb). **Retire `ქირაობა` entirely** — see 3.3.

Every place the wrong term appears:

| Sev | File · key path | Current | Corrected | Reason |
|-----|-----------------|---------|-----------|--------|
| S2 | `seo_meta.yml:59` `templates.home.ka.title` | `ავტომობილის დაქირავება და მარშრუტის დაგეგმვა საქართველოში \| RentUp` | `ავტომობილების გაქირავება და მარშრუტის დაგეგმვა საქართველოში \| RentUp` | company-voice page |
| S2 | `seo_meta.yml:106` `templates.car.ka.title` | `{name}-ის დაქირავება საქართველოში — {price} ₾-დან \| RentUp` | `{name}-ის გაქირავება საქართველოში — {price} ₾-დან \| RentUp` | hyphen is correct here ({name} is Latin); only the verb is wrong |
| S2 | `seo_meta.yml:795` `templates.blog.ka.description` | `…ავტომობილის დაქირავებასა და მართვაზე…` | `…ავტომობილის გაქირავებასა და მართვაზე…` | consistency |
| S2 | `seo_meta.yml:869` `templates.faq.ka.title` | `ხშირად დასმული კითხვები — მანქანის დაქირავება \| RentUp` | `ხშირად დასმული კითხვები — მანქანის გაქირავება \| RentUp` | consistency |
| S2 | `seo_meta.yml:870` `templates.faq.ka.description` | `30-ზე მეტი პასუხი მანქანის დაქირავებაზე საქართველოში…` | `30-ზე მეტი პასუხი მანქანის გაქირავებაზე საქართველოში…` | consistency |
| S2 | `seo_meta.yml:986` `templates.car_rental_hub.ka.title` | `მანქანის დაქირავება საქართველოში \| RentUp` | `მანქანის გაქირავება საქართველოში \| RentUp` | **title ≠ H1 on the same page today** |
| S2 | `seo_meta.yml:1012` `templates.car_rental_location.city.ka.title` | `მანქანის დაქირავება {city}-ში` | `მანქანის გაქირავება {city_in}` | title ≠ H1 (see KA2) |
| S2 | `seo_meta.yml:1031` `car_rental_location.airport.ka.title` | `{city}ის აეროპორტში მანქანის დაქირავება ({iata})` | `{city_of} აეროპორტში მანქანის გაქირავება ({iata})` | title ≠ H1 (see KA4) |
| S2 | `seo_meta.yml:1055` `car_rental_category.ka.title` | `{category}-ის დაქირავება საქართველოში` | `{category_of} გაქირავება საქართველოში` | title ≠ H1 (see KA6) |
| S2 | `seo_ui.yml:120` `car_rental.ka` | `მანქანის დაქირავება` | `მანქანის გაქირავება` | nav/breadcrumb label must match the H1 it links to |
| S2 | `seo_ui.yml:128` `rental_terms.ka` | `დაქირავების პირობები` | `გაქირავების პირობები` | `seo_meta.yml:846` already says `გაქირავების პირობები` for the same page |
| S2 | `seo_ui.yml:192` `one_way.ka` | `ცალმხრივი დაქირავება` | `ცალმხრივი გაქირავება` | `seo_car_rental.yml:242` heading says `ცალმხრივი ქირაობა` — three terms, one concept |

### 3.3 `ქირაობა` used as a countable noun (machine-translation tell)

`ქირაობა` is a verbal noun — "the activity of renting". It cannot be counted or pluralised. The pack
uses it as a direct calque of English "a rental / every rental / all rentals", which is
ungrammatical and immediately reads as translated.

| Sev | `seo_car_rental.yml` line · key | Current | Corrected | Reason |
|-----|--------------------------------|---------|-----------|--------|
| S2 | 159 `ka.meta_title` | `მანქანის ქირაობა საქართველოში — შეუზღუდავი გარბენი \| RentUp` | `მანქანის გაქირავება საქართველოში — შეუზღუდავი გარბენი \| RentUp` | head term must match the H1 above it |
| S2 | 169 `ka.sections.intro.body` | `ყველა ქირაობაში გარბენი შეზღუდვის გარეშეა` | `ყველა ჯავშანში გარბენი შეზღუდვის გარეშეა` | "every rental" as a countable event = `ჯავშანი` |
| S2 | 173 `ka.sections.intro.body` | `…რაც უფრო ხანგრძლივია ქირაობა — კვირა უფრო იაფია…` | `…რაც უფრო ხანგრძლივია გაქირავების ვადა — კვირა უფრო იაფია…` | duration of the hire, not the activity |
| S2 | 189 `ka.sections.requirements.heading` | `ვის შეუძლია ქირაობა` | `ვის შეუძლია მანქანის დაქირავება` | customer-voice → `დაქირავება` is right here; `ქირაობა` bare is incomplete |
| S2 | 199 `ka.sections.deposit_explained.body` | `ყოველი ქირაობა მოითხოვს დასაბრუნებელ დეპოზიტს` | `ყოველი ჯავშანი მოითხოვს დასაბრუნებელ დეპოზიტს` | countable |
| S2 | 204 `ka.sections.deposit_explained.body` | `ის ყოველ ქირაობაზეა საჭირო, კატეგორიის მიუხედავად` | `ის ყოველ ჯავშანზეა საჭირო, კატეგორიის მიუხედავად` | countable |
| S2 | 209 `ka.sections.mileage.body` | `ყოველ ქირაობას თან ახლავს შეზღუდვის გარეშე გარბენი` | `ყოველ ჯავშანს თან ახლავს შეზღუდვის გარეშე გარბენი` | countable |
| S2 | 242 `ka.sections.one_way.heading` | `ცალმხრივი ქირაობა` | `ცალმხრივი გაქირავება` | must match `seo_ui.yml → one_way.ka` |
| S2 | 248 `ka.sections.one_way.body` | `საზღვრისგარეთა მოგზაურობა არცერთ ქირაობაზე არ არის შესაძლებელი` | `საზღვრისგარეთა მოგზაურობა არცერთ ჯავშანზე არ არის შესაძლებელი` | countable |
| S2 | 268 `ka.sections.support.body` | `გზაზე დახმარება ყველა ქირაობაზეა ჩართული` | `გზაზე დახმარება ყველა ჯავშანშია ჩართული` | countable |
| S2 | 282 `ka.faq[].a` | `დიახ, ყოველ ქირაობაზე, მთელ საქართველოში` | `დიახ, ყოველ ჯავშანზე, მთელ საქართველოში` | countable |
| S2 | 884 / 1079 / 1279 / 1472 / 1669 / 1855 `ka.meta_title` (6 location pages) | `მანქანის ქირაობა თბილისში — …` etc. | `მანქანის გაქირავება თბილისში — …` etc. | head term; also currently dead (overridden by `seo_meta.yml`) but must be fixed before it is ever un-overridden |
| S2 | 909 | `თუ თბილისში ქირაობას აბრუნებთ ბათუმიდან ან ქუთაისიდან` | `თუ თბილისში აღებულ მანქანას აბრუნებთ ბათუმში ან ქუთაისში` | you return a *car*, not a "renting"; the original also reverses the direction of `-დან`/`-ში` |
| S2 | 1300 / 1690 / 1695 | `ყოველი ქირაობა მიეწოდება` / `ყოველი ქირაობა საქართველოში რჩება` | `ყოველი მანქანა მიეწოდება` / `ყოველი ავტომობილი საქართველოში რჩება` | a rental cannot be delivered or stay in a country; a car can |
| S2 | 1875 | `…ქირაობაზე არ არის შესაძლებელი` | `…ჯავშანზე არ არის შესაძლებელი` | countable |
| S2 | `seo_trip_planner.yml:716` | `ყველა ქირაობა შეზღუდვის გარეშე` | `ყველა ჯავშანი შეზღუდვის გარეშე` | countable |
| S2 | `seo_trip_planner.yml:719` | `…რაც უფრო ხანგრძლივია ქირაობა` | `…რაც უფრო ხანგრძლივია გაქირავების ვადა` | as line 173 |

### 3.4 Other Georgian issues

| # | Sev | File · key path | Current | Corrected | Reason |
|---|-----|-----------------|---------|-----------|--------|
| KA10 | S2 | `seo_categories.yml` → `economy.ka.limitations` | `…ოთხთვალა წამყვანის არქონა ამას გამორიცხავს` | `…ოთხივე წამყვანი თვლის არქონა ამას გამორიცხავს` | `ოთხთვალა` means "four-wheeled (cart)". The automotive term for 4WD/AWD is `ოთხივე წამყვანი თვალი` (or `სრული წამყვანი`). |
| KA11 | S2 | `content/itineraries/georgia-5-days.yml` → `ka.tips[0]` | `…offroad/მხოლოდ-4x4-ადაა შეფასებული` | `…მხოლოდ 4x4-ისთვისაა შეფასებული` | raw enum `offroad` + a case ending welded onto a hyphenated compound; `-ადაა` is not a valid ending here |
| KA12 | S2 | `content/itineraries/georgia-5-days.yml` → `ka.tips[2]` | `მე-3 დღე აკლიმატიზაციის დღედაა აგებული, სავალის გარეშე` | `მე-3 დღე აკლიმატიზაციის დღედაა აგებული, მართვის გარეშე` | `სავალი` is an adjective ("travel-"), not a noun for "driving" |
| KA13 | S2 | `content/itineraries/georgia-5-days.yml` → `ka.tips[4]` | `ორივე ყველაზე გრძელი სავალი დღე (1 და 2) კვირის 13-საათიანი სავალი დროის დაახლოებით მესამედს შეადგენს თითოეული` | `ორი ყველაზე გრძელი სამგზავრო დღე (1 და 2) თითოეული მოგზაურობის 13-საათიანი მართვის დროის დაახლოებით მესამედს შეადგენს` | three faults: `ორივე` = "both" ≠ "the two"; `კვირის` ("of the week") mistranslates "the trip's"; the stranded `თითოეული` at the end is English word order |
| KA14 | S3 | `seo_meta.yml` (all ka route/attraction/itinerary descriptions) vs `seo_ui.yml → total_drive.ka` vs `seo_trust.yml → ka.editorial.policy_body` | `სამგზავრო დრო` / `სულ მართვაში` / `სავალი დრო` | pick one: `მართვის დრო` (label) and `მგზავრობის დრო` (running text) | three different Georgian terms for "drive time" across three files in the same pack |
| KA15 | S3 | `seo_meta.yml → templates.*.ka` vs `seo_categories.yml → *.ka` | `შეუზღუდავი გარბენი` vs `კილომეტრაჟის შეზღუდვის გარეშე` | standardise on `შეუზღუდავი გარბენი` (already the term in `seo_ui.yml → mileage.ka`) | two words for "mileage" in adjacent packs |
| KA16 | S3 | `seo_ui.yml → itineraries.ka` | `მზა მარშრუტების გეგმები` | `მზა მარშრუტები` | "ready routes' plans" is doubled; the plain noun is what a Georgian user would type |
| KA17 | S3 | `seo_ui.yml → trip_planner.ka`, `open_planner.ka` | `მოგზაურობის დამგეგმავი`, `დამგეგმავის გახსნა` | `მარშრუტის დამგეგმავი`, `დამგეგმავის გახსნა` | `დამგეგმავი` as a name for a *tool* is a calque; anchoring it to `მარშრუტი` matches the phrasing Georgian users actually use for route planning and keeps the keyword on-page |
| KA18 | S3 | 69 occurrences across `content/**/*.yml` (12 in the new packs, incl. `itineraries/georgia-3-days.yml`, `georgia-5-days.yml`) | `„მხოლოდ ზაფხულია"` — low-9 open quote closed with a straight ASCII `"` | `„მხოლოდ ზაფხულია“` | Georgian uses `„…“`. 61 pairs in the repo are correct, 69 are mismatched. |
| KA19 | S3 | `seo_categories.yml → *.ka.meta_title` (4 pages) | `… \| 75 ₾-დან/დღეში — RentUp.ge` | `… — 75 ₾-დან/დღეში \| RentUp` | brand suffix disagrees with the convention `seo_meta.yml` documents at its head ("All titles end with the literal Latin brand suffix `| RentUp`"). Two brand spellings (`RentUp` vs `RentUp.ge`) and two separators. |

### 3.5 Georgian keyword localisation (not translation)

- The site currently splits its own head term across `დაქირავება` / `გაქირავება` / `ქირაობა`, so the
  three highest-value Georgian pages (`/ka/`, `/ka/car-rental/`, `/ka/fleet/`) each rank against a
  different phrase and cannibalise one another. Fixing 3.2 is a keyword decision, not a style one.
- `მოგზაურობის დამგეგმავი` (KA17) is a word-for-word rendering of "trip planner". The Georgian
  phrasing built around `მარშრუტი` ("route") is the natural head noun and is already used everywhere
  else in the pack (`მზა მარშრუტები`, `მარშრუტის გაჩერებები`), so aligning on it also fixes an
  internal inconsistency.
- Do **not** translate `SUV` / `4x4`; they are used untranslated in Georgian and `categories.yml`
  correctly keeps them. That is right and should be preserved through the genitive fix (KA6) —
  `კროსოვერის / SUV-ის`, keeping the Latin-stem hyphen on `SUV` only.

---

## 4. Russian (ru)

### 4.1 Numeral agreement — the dominant defect

Russian requires three forms (1 / 2–4 / 5–0, with 11–14 always taking the last). No template
implements it, so every count-bearing generated string is wrong for part of its range.

| # | Sev | File · key path | Current (rendered) | Corrected | Reason | Pages |
|---|-----|-----------------|---------------------|-----------|--------|-------|
| RU1 | S1 | `seo_meta.yml` → `templates.route.default.ru.title` and all 12 `by_purpose.*.ru.title` | `Чёрное море и Аджария — прибрежный маршрут, 4 дней, 880 км`; `…, 2 дней, …`; `…, 1 дней, …` | `4 дня`, `2 дня`, `1 день` — needs `ru_plural(days, [день, дня, дней])` | route `days` values in content are 1, 2, 3, 4, 5, 6, 7, 10 — the fixed form `дней` is only right for 5, 6, 7, 10 | **23 of 32 route titles** |
| RU2 | S1 | `seo_meta.yml` → `templates.itinerary.ru.title` | `Маршрут по Грузии на 3 дней \| RentUp` | `Маршрут по Грузии на 3 дня \| RentUp` | itinerary days are 3, 5, 7, 10, 14; only 3 is wrong, but it is the entry-level page | 1 |
| RU3 | S1 | `seo_meta.yml` → `templates.region.ru.title` | `Кахетия — 32 достопримечательностей`; `Аджария — 24 достопримечательностей` | `32 достопримечательности`; `24 достопримечательности` | counts ending in 2/3/4 take the genitive **singular** | 4 of 11 (kakheti 32, samtskhe-javakheti 22, mtskheta-mtianeti 23, adjara 24) |
| RU4 | S1 | `seo_meta.yml` → `templates.region.ru.description` | `{count} мест для посещения в регионе {name}` → `32 мест` | `32 места для посещения…` | same rule | 4 (latent — see KA9, the region description is overwritten today) |
| RU5 | S1 | `seo_meta.yml` → `templates.car_rental_category.ru.description` | `3 моделей категории Кроссовер / SUV в Грузии от 130 ₾ в день` | `3 модели категории «Кроссовер / SUV» в Грузии от 130 ₾ в день` | every category holds 2 or 3 cars, so `моделей` is wrong on **all** of them | 4 (all) |
| RU6 | S2 | `seo_meta.yml` → `templates.routes_hub.ru.title` / `.description` | `Готовые маршруты по Грузии — {count} путешествий` / `{count} готовых автомобильных маршрутов` → with 32: `32 путешествий`, `32 готовых автомобильных маршрутов` | `32 путешествия`, `32 готовых автомобильных маршрута` | same rule. Currently dead — `routes_hub` is never passed to `seo_meta()` (see §7) — but wrong the day it is wired | 0 today, 1 when wired |

### 4.2 Case agreement after prepositions and after `Аренда`

| # | Sev | File · key path | Current | Corrected | Reason |
|---|-----|-----------------|---------|-----------|--------|
| RU7 | S1 | `seo_meta.yml` → `templates.car_rental_category.ru.title` | `Аренда Эконом-класс в Грузии — от 75 ₾/день`; `Аренда Кроссовер / SUV в Грузии`; `Аренда Внедорожник 4x4 в Грузии`; `Аренда Минивэн в Грузии` | `Аренда автомобиля эконом-класса…`; `Аренда кроссовера / SUV…`; `Аренда внедорожника 4x4…`; `Аренда минивэна…` | `аренда` governs the genitive; the template injects the nominative label verbatim, and capitalised mid-sentence. All 4 category pages | 
| RU8 | S2 | `seo_ui.yml` → `popular_routes_from.ru` | `Популярные маршруты из {place}` | `Популярные маршруты из {place_gen}` (pre-inflected, Appendix B) | `из` takes the genitive. Most Georgian toponyms are indeclinable in Russian (`из Тбилиси`, `из Батуми`), but five in `places.yml` are not: `Мцхета→из Мцхеты`, `Чиатура→из Чиатуры`, `Анаклия→из Анаклии`, `Ахмета→из Ахметы`, `Степанцминда→из Степанцминды` |
| RU9 | S2 | `seo_meta.yml` → `templates.car_rental_location.city.ru.title` / `.description` | `Аренда авто в {city}` / `Заберите арендованный автомобиль в {city}` | `Аренда авто в {city_prep}` | `в` + prepositional. Same five names decline: `в Мцхете`, `в Чиатуре`, `в Анаклии`, `в Ахмете`, `в Степанцминде`. The three live rental cities (Тбилиси, Кутаиси, Батуми) are indeclinable, so this is latent until a fourth city is added |
| — | ok | `templates.region.ru.*`, `car_rental_location.airport.ru.*` | `в регионе {name}`, `в аэропорту {city}` | — | Correct as written: the appositive after `регионе`/`аэропорту` legitimately stays in the nominative |

### 4.3 Russian consistency and localisation

| # | Sev | Where | Current | Corrected | Reason |
|---|-----|-------|---------|-----------|--------|
| RU10 | S3 | `content/routes/*.yml` → `ru.name`, `content/regions/*.yml` → `ru.name` | `Имеретия` vs `Имерети`; `Кахетия` vs `Кахети`; `Сванети` vs `Сванетия` — all four spellings appear in route names while the region files use only the `-ия` forms | use the region files' forms everywhere: `Имеретия`, `Кахетия`, `Сванетия`, `Аджария`, `Гурия` | a user landing from a `Кахетия` query sees `Кахети` in the route list; also splits internal anchor text |
| RU11 | S3 | all ru packs | only `аренда` is used | add `прокат` as a secondary term in H2/body on `/ru/car-rental/` and the category pages | `прокат автомобилей` is the other standard Russian commercial term for this service and is entirely absent from the site; this is a localisation gap, not a translation error. (No search-volume claim is made here — this needs to be checked in a keyword tool before the copy is written.) |
| RU12 | S2 | `content/itineraries/georgia-5-days.yml` → `ru.tips[4]` | `На два самых длинных дня вождения (1-й и 2-й) приходится примерно по трети из 13 часов общего времени поездки` | `На два самых длинных дня за рулём (1-й и 2-й) приходится примерно по трети от 13 часов общего времени в пути` | `из 13 часов` is an English "of the 13 hours"; Russian needs `от`. `время поездки` also drifts from `время в пути`, the term used in every other ru string in the pack |

---

## 5. Arabic (ar)

Arabic counted-noun agreement has four cases: 1 = noun alone, 2 = dual, 3–10 = broken plural in the
genitive, 11–99 = **singular** in the accusative (`تمييز`). The templates hard-code one form each.

| # | Sev | File · key path | Current (rendered) | Corrected | Reason | Pages |
|---|-----|-----------------|---------------------|-----------|--------|-------|
| AR1 | S1 | `seo_meta.yml` → `templates.route.default.ar.title` + all 12 `by_purpose.*.ar.title` and `.description` | `…مسار تاريخي، 2 أيام، 285 كم`; `…مسار قيادة ممتع، 1 أيام، 9 كم` | `يومان` (title, nominative) / `يومين` (after `لمدة`); `يوم واحد` | 3–10 take `أيام`, which is right for days 3–7 and 10, but the content also has 1-day and 2-day routes | **9 of 32 route titles** |
| AR2 | S1 | `seo_meta.yml` → `templates.itinerary.ar.title` / `.description` | `برنامج رحلة جورجيا لمدة 14 أيام` | `برنامج رحلة جورجيا لمدة 14 يوماً` | 11–99 take the accusative singular, not the plural | 1 (`georgia-14-days`) |
| AR3 | S1 | `seo_meta.yml` → `templates.car_rental_category.ar.description` | `3 طرازاً من فئة كروس أوفر / SUV متاحة في جورجيا` | `3 طُرُز من فئة «كروس أوفر / SUV» متاحة في جورجيا` | `طرازاً` is the 11–99 form; with 2 or 3 cars per category it is wrong on every page. 2 → `طرازان` | 4 (all) |
| AR4 | S1 | `seo_meta.yml` → `templates.itineraries_hub.ar.description` | `5 برنامج رحلة مُعدّ لجورجيا من 3 إلى 14 يوماً` | `5 برامج رحلات مُعدّة لجورجيا من 3 إلى 14 يوماً` | 5 takes the broken plural `برامج`, and the adjective must agree | 1 |
| AR5 | S2 | `seo_meta.yml` → `templates.routes_hub.ar.title` / `.description` | `{count} مساراً` with count = 32 | correct as written (`32 مساراً`) — no change, but note it breaks if the route count ever drops below 11 | documented so the fix in AR1 is applied consistently | 0 |
| AR6 | S2 | `content/itineraries/georgia-5-days.yml` → `ar.tips[1]` | `مسار أودزيرو/أوبا مسجل في البيانات` | `مسار أودزيرو/بوبا مسجل في البيانات` | the place is **Buba** (`Удзиро/Буба` in ru, `بوبا` in fa). `أوبا` reads "Uba" — the initial B was dropped |
| AR7 | S2 | `content/itineraries/*.yml` → `ar.*` | `جورجيا في ٥ أيام` / `اليومان ١-٢` / `كارثة ٢٠٢٣` in prose, next to `المسافة الإجمالية 1020 كم` / `18:30` / `7 أيام` from the templates | pick one numeral system per locale and apply it everywhere | 17 Arabic pages mix Eastern Arabic-Indic (`٠١٢`) and Western (`012`) digits inside one document; the other 332 use Western only. Either is acceptable MSA practice — mixing is not |
| AR8 | S1 | `content/itineraries/*.yml` → `ar.tips[]` | `اليومان ١-٢` | `اليومان ٢–١` is what a browser actually paints — write `اليومان الأول والثاني`, or use Western digits `1-2` | bidi: a hyphen between two *Arabic-Indic* numbers is not covered by UAX#9 rule W4 (which only joins European numbers), so N1 resolves it to RTL and the range renders reversed. With Western digits the same string is safe |
| AR9 | S2 | `seo_trust.yml` → `ar.editorial.policy_body` | `نفس حقلَي road وcar_category` | see X5 / Appendix E | raw YAML field names in user copy |
| AR10 | S3 | `seo_meta.yml` → all `ar` price strings | `من 75 لاري يومياً` (the word) while ka/ru/he use the `₾` glyph | keep `لاري` — it is the right call in RTL and avoids the ET/EN bidi edge — but state it as a deliberate rule so it is not "fixed" later | currency rendering differs by language with no documented reason |

### 5.1 Bidi in the built Arabic pages (`dist/ar/car-rental/index.html` verified)

- `<html lang="ar" dir="rtl">` — correct.
- `تأجير سيارات في جورجيا | RentUp` — the Latin brand in the title is fine: the `|` sits between an
  RTL run and an L run and resolves to the paragraph direction, which is what MSA typography wants.
- `6 نقاط استلام من بينها 3 مطارات، و6 فئات سيارات بسعر يبدأ من 75 لاري يومياً` — all numbers are
  bare EN runs with no neutral between them; renders correctly.
- Arabic comma `،` used throughout instead of `,` — correct.
- **Fails:** `09:00–21:00` in the footer (see §8) and `١-٢` in the itineraries (AR8).

---

## 6. Hebrew (he)

| # | Sev | File · key path | Current (rendered) | Corrected | Reason | Pages |
|---|-----|-----------------|---------------------|-----------|--------|-------|
| HE1 | S1 | `seo_meta.yml` → `templates.route.default.he.title` + all 12 `by_purpose.*.he.title` | `…מסלול היסטורי, 2 ימים, 285 ק״מ`; `…מסלול נהיגה נופי, 1 ימים, 9 ק״מ` | `יומיים` (Hebrew has a dedicated dual); `יום אחד` | `ימים` is right for 3+, wrong for 1 and 2 | **9 of 32 route titles** |
| HE2 | S2 | `seo_meta.yml` → `templates.route.by_purpose.*.he.description` | `{name} הוא מסלול היסטורי בן {days} ימים` with days = 2 | `…בן יומיים` | same rule inside the description | 9 |
| HE3 | S2 | `seo_meta.yml` → `templates.car_rental_category.he.description` | `3 דגמי קרוסאובר / SUV זמינים בגאורגיה` | `שלושה דגמי קרוסאובר / SUV זמינים בגאורגיה` | with a small count Hebrew prefers the spelled numeral in running text; `2 דגמי` in particular reads wrong. Not a hard error — S2 | 4 |
| HE4 | S3 | `content/itineraries/*.yml` → `he.*`, `content/routes/*.yml` → `he.name` | `1020 ק&quot;מ`, `בורג&#x27;ומי`, `אג&#x27;רה` — ASCII `"` and `'` used as gershayim/geresh | `ק״מ` (U+05F4), `בורג׳ומי` (U+05F3) — `seo_meta.yml` already uses the correct `ק״מ` | two typographic conventions inside one page; the ASCII forms also HTML-escape into `&quot;`/`&#x27;` in the source, which trips up copy-paste and some readers |
| HE5 | S2 | `seo_trust.yml` → `he.editorial.policy_body` | `אותם שדות road ו-car_category` | see X5 / Appendix E | raw YAML field names in user copy |
| — | ok | `seo_ui.yml → popular_routes_from.he` = `מסלולי טיול פופולריים מ{place}` | — | — | The prefixed `מ` with no space is correct Hebrew and works for every place name in `places.yml`. The only problem here is X3 (the placeholder is never substituted) |

### 6.1 Bidi in the built Hebrew pages (`dist/he/itineraries/georgia-7-days/index.html` verified)

- `<html lang="he" dir="rtl">`, canonical, and all 7 hreflang links — correct.
- `מסלול טיול בגאורגיה ל-7 ימים | RentUp` — `ל-7` is correct: the hyphen is bidi class ES between a
  Hebrew letter and a European number, and browsers paint it as intended.
- `1020 ק״מ`, `18:30`, `ימים 1-2` — all safe. A hyphen **between two Western digits** is joined into
  the number run by UAX#9 W4, so `1-2` does not reverse (unlike the Arabic-Indic case, AR8).
- `החל מ-130 ₾ ליום` — `₾` is bidi class ET and absorbs into the preceding EN run, so `130 ₾`
  paints correctly. No fix needed.
- **Fails:** the meta description prints raw `{days}/{km}/{stops}` (X2), and `09:00–21:00` /
  `22:00–08:00` reverse (see §8).

---

## 7. Persian (fa)

Persian requires no numeral–noun agreement (the noun stays singular after a number), and every
`fa` template gets this right — `{days} روز`, `{days} روزه`, `{count} جاذبهٔ گردشگری`, `{count} مدل`
are all correct. Persian is the cleanest of the three RTL locales.

| # | Sev | File · key path | Current | Corrected | Reason | Pages |
|---|-----|-----------------|---------|-----------|--------|-------|
| FA1 | S2 | `content/itineraries/*.yml` → `fa.*` and 140+ `content/attractions/*.yml` → `fa.*` | `گرجستان در ۵ روز` / `کارثه ۲۰۲۳` / `فقط ۴×۴` in prose, beside `1020 کیلومتر`, `18:30`, `5 روزه`, `130 لاری` from the templates | choose one system for `fa` — recommend Eastern (`۰–۹`) throughout, since the hand-written prose already uses it — and convert the template output to match | **309 of 349** Persian pages mix Eastern and Western digits inside a single document |
| FA2 | S2 | `content/itineraries/georgia-5-days.yml` → `fa.tips[0]` | `مسیر روز چهارم به دریاچه اودزیرو آفرود/فقط ۴×۴ رتبه‌بندی شده` | `مسیر روز چهارم به دریاچه اودزیرو «فقط ۴×۴» درجه‌بندی شده` | `آفرود` is the raw enum `offroad` transliterated; `رتبه‌بندی` means "ranked", not "rated/graded" — a machine-translation tell |
| FA3 | S2 | `content/itineraries/georgia-5-days.yml` → `fa.tips[0]` | `بدون فاصله واقعی از زمین به‌تنهایی وارد آن نشوید` | `با خودرویی که ارتفاع واقعی از زمین ندارد، به‌تنهایی وارد آن نشوید` | the English "in a touring SUV that lacks real ground clearance" lost its subject; as written it tells the reader not to enter "without real distance from the ground", which is meaningless |
| FA4 | S2 | `seo_trust.yml` → `fa.trust.heading` | `ما چه کسی هستیم` | `ما که هستیم` | `چه کسی` is singular ("who is he"); this is a literal rendering of "Who we are" and is ungrammatical with the plural `ما`. Reads machine-translated |
| FA5 | S2 | `seo_trust.yml` → `fa.editorial.policy_body` | `همان فیلدهای road و car_category` | see X5 / Appendix E | raw YAML field names in user copy |
| FA6 | S3 | `seo_ui.yml` → `season.*.fa` vs `content/itineraries/*.yml → fa` | `ژوئن–سپتامبر` (labels) vs `ژوئن تا سپتامبر` (prose) | acceptable; but the label form uses an en dash between two Persian month names — safe because both sides are RTL | noted so the §8 en-dash sweep does not "fix" these |
| FA7 | S3 | `seo_ui.yml` → `road.4x4_only.fa` = `فقط 4x4` vs `content/itineraries/georgia-5-days.yml → fa.tips[0]` = `فقط ۴×۴` | two spellings of the same term | standardise on `4x4` (Latin, matching the brand-neutral usage in the fa titles) | consistency |

### 7.1 Bidi in the built Persian pages (`dist/fa/attractions/gergeti-trinity-church/index.html` verified)

- `<html lang="fa" dir="rtl">`, canonical, `og:locale fa_IR`, all 7 hreflang links — correct.
- `کلیسای تثلیث گرگتی — راهنمای بازدید از صومعه، 3:10 از تفلیس | RentUp` — the drive time `3:10` is
  safe: the colon is bidi class CS between two European numbers and is joined into the number run.
- `160 کیلومتر از تفلیس (3:10)` — the parenthesised number resolves through the Unicode bracket-pair
  algorithm and paints correctly.
- Persian comma `،` used correctly throughout.
- **Fails:** `09:00–21:00` in the footer (§8) and the digit mixing (FA1).

---

## 8. RTL bidi: the en-dash time range (781 pages)

**Sev S1.** A hyphen-minus between two Western digits is joined into the number run by UAX#9 rule W4
and is safe. An **en dash (U+2013) is not** — it is bidi class ON, rule N1 resolves it to the
paragraph direction, and in an RTL paragraph the two number runs are then laid out right-to-left.
`09:00–21:00` is painted as **`21:00–09:00`**.

Confirmed present in the built output of every RTL locale:
`dist/ar/index.html`, `dist/he/index.html`, `dist/fa/index.html` and 778 more
(ar 259, he 263, fa 259 pages — the footer opening-hours line is on nearly every page).

| File · key path | Current | Corrected | Reason |
|-----------------|---------|-----------|--------|
| `content/settings/ui.yml:254` → `fa.…hours` | `دوشنبه–یکشنبه 09:00–21:00` | `دوشنبه تا یکشنبه، ۹:۰۰ تا ۲۱:۰۰` | replace the numeric en dash with the word `تا`; the month/day-name dash is safe and may stay |
| `content/settings/ui.yml:329` → `he.…hours` | `א׳–ש׳ 09:00–21:00` | `א׳–ש׳ 09:00 עד 21:00` | as above, with `עד` |
| `content/settings/ui.yml:404` → `ar.…hours` | `الاثنين–الأحد 09:00–21:00` | `الاثنين–الأحد، من 09:00 إلى 21:00` | as above, with `من … إلى` |
| `content/pages/contact.yml:261, 283` (fa) | `همه‌روزه 09:00–21:00` | `همه‌روزه ۹:۰۰ تا ۲۱:۰۰` | same |
| `content/pages/contact.yml:341, 362` (he) | `כל ימות השבוע 09:00–21:00` | `כל ימות השבוע 09:00 עד 21:00` | same |
| `content/pages/contact.yml:420, 441` (ar) | `يومياً 09:00–21:00` | `يومياً من 09:00 إلى 21:00` | same |
| `content/pages/index.yml:831, 1056, 1277` | same three strings | as above | same |
| `content/settings/seo_car_rental.yml:984` (he) | `פתוח 09:00–21:00` | `פתוח בין 09:00 ל-21:00` (the same file already uses this form at line 683) | internally inconsistent *and* wrong |
| `content/settings/seo_car_rental.yml:1197` (he) | `22:00–08:00 (20 ₾) שכיחה כאן` | `תוספת הלילה (20 ₾, בין 22:00 ל-08:00) שכיחה כאן` | same |
| `content/settings/seo_car_rental.yml:1586` (he) | `תוספת הלילה (20 ₾, 22:00–08:00)` | `תוספת הלילה (20 ₾, בין 22:00 ל-08:00)` | same |
| `content/regions/tbilisi.yml:210` (he) | `שעות העומס הן בערך 08:30–10:00 ו-17:30–19:30` | `…בערך בין 08:30 ל-10:00 ובין 17:30 ל-19:30` | same |
| `content/pages/pricing.yml:1141` (fa), `:1444` (he), `:1746` (ar) | `(22:00–07:00)` | `(از 22:00 تا 07:00)` / `(בין 22:00 ל-07:00)` / `(من 22:00 إلى 07:00)` | same |

An alternative fix that preserves the dash is to wrap each range in `<span dir="ltr">…</span>` or to
insert U+200E (LRM) either side of the dash. Rewriting to a word is simpler and reads better in all
three languages, and `seo_car_rental.yml` already does it that way in the majority of its strings.

> Separately (not a translation issue, flagged only because a translator will otherwise "harmonise"
> them): `content/pages/pricing.yml` states a night window of **22:00–07:00 with a 40 ₾ surcharge**,
> while `content/settings/rental_policy.yml:47–48` and `seo_car_rental.yml` state **22:00–08:00 with
> 20 ₾**. Two different facts in six languages each. This needs a business decision, not a language
> one — do not let a translator pick.

---

## 9. hreflang / `lang` / `dir` verification

Checked on the three files named in the brief plus the ka/ru trees. **All correct — no action.**

| Check | Result |
|-------|--------|
| `<html lang>` | `ar` / `he` / `fa` / `ka` / `ru` / `en` — correct on every page sampled |
| `dir="rtl"` | present on ar, he, fa; absent on en, ka, ru — correct |
| hreflang set | all 7 links (`en`, `ka`, `ru`, `fa`, `he`, `ar`, `x-default`) on every page, self-referential included, reciprocal, `x-default` → the `/` root — correct |
| canonical | each language self-canonicals (`https://rentup.ge/he/itineraries/georgia-7-days/`) — correct, no cross-language canonical |
| `og:locale` / `og:locale:alternate` | `ar_AE` / `he_IL` / `fa_IR` / `ka_GE` / `ru_RU` / `en_US`, alternates list the other five — correct |
| `geo.placename` | localised per language (`تبليسي` / `טביליסי` / `تفلیس`) — correct |
| Silent English fallback | **None found.** Every `content/itineraries/*.yml` carries all six language blocks; the fa/he/ar itinerary bodies are fully translated. The only English visible in a non-English page is the raw enum leakage in X4 (`suv`, `offroad`, `car_category`), not a fallback |

---

# Appendix A — Georgian inflection tables (paste-ready)

Georgian cannot be inflected by string concatenation. The correct fix is to carry the two inflected
forms as data. Add these keys to `content/settings/places.yml` and to each `content/regions/*.yml`,
then use `{city_in}` / `{city_of}` / `{place_from}` / `{region_in}` / `{region_of}` in the templates.

### A.1 `content/settings/places.yml` — add `ka_in` (locative), `ka_of` (genitive), `ka_from` (ablative)

```yaml
# tbilisi
  ka_in: თბილისში
  ka_of: თბილისის
  ka_from: თბილისიდან
# tbilisi-airport
  ka_in: თბილისის აეროპორტში
  ka_of: თბილისის აეროპორტის
  ka_from: თბილისის აეროპორტიდან
# kutaisi
  ka_in: ქუთაისში
  ka_of: ქუთაისის
  ka_from: ქუთაისიდან
# kutaisi-airport
  ka_in: ქუთაისის აეროპორტში
  ka_of: ქუთაისის აეროპორტის
  ka_from: ქუთაისის აეროპორტიდან
# batumi
  ka_in: ბათუმში
  ka_of: ბათუმის
  ka_from: ბათუმიდან
# batumi-airport
  ka_in: ბათუმის აეროპორტში
  ka_of: ბათუმის აეროპორტის
  ka_from: ბათუმის აეროპორტიდან
# rustavi
  ka_in: რუსთავში
  ka_of: რუსთავის
  ka_from: რუსთავიდან
# mtskheta
  ka_in: მცხეთაში
  ka_of: მცხეთის
  ka_from: მცხეთიდან
# gori
  ka_in: გორში
  ka_of: გორის
  ka_from: გორიდან
# khashuri
  ka_in: ხაშურში
  ka_of: ხაშურის
  ka_from: ხაშურიდან
# borjomi
  ka_in: ბორჯომში
  ka_of: ბორჯომის
  ka_from: ბორჯომიდან
# bakuriani
  ka_in: ბაკურიანში
  ka_of: ბაკურიანის
  ka_from: ბაკურიანიდან
# akhaltsikhe
  ka_in: ახალციხეში
  ka_of: ახალციხის
  ka_from: ახალციხიდან
# akhalkalaki
  ka_in: ახალქალაქში
  ka_of: ახალქალაქის
  ka_from: ახალქალაქიდან
# zestafoni
  ka_in: ზესტაფონში
  ka_of: ზესტაფონის
  ka_from: ზესტაფონიდან
# chiatura
  ka_in: ჭიათურაში
  ka_of: ჭიათურის
  ka_from: ჭიათურიდან
# sachkhere
  ka_in: საჩხერეში
  ka_of: საჩხერის
  ka_from: საჩხერიდან
# tkibuli
  ka_in: ტყიბულში
  ka_of: ტყიბულის
  ka_from: ტყიბულიდან
# samtredia
  ka_in: სამტრედიაში
  ka_of: სამტრედიის
  ka_from: სამტრედიიდან
# senaki
  ka_in: სენაკში
  ka_of: სენაკის
  ka_from: სენაკიდან
# poti
  ka_in: ფოთში
  ka_of: ფოთის
  ka_from: ფოთიდან
# zugdidi
  ka_in: ზუგდიდში
  ka_of: ზუგდიდის
  ka_from: ზუგდიდიდან
# anaklia
  ka_in: ანაკლიაში
  ka_of: ანაკლიის
  ka_from: ანაკლიიდან
# ambrolauri
  ka_in: ამბროლაურში
  ka_of: ამბროლაურის
  ka_from: ამბროლაურიდან
# oni
  ka_in: ონში
  ka_of: ონის
  ka_from: ონიდან
# ozurgeti
  ka_in: ოზურგეთში
  ka_of: ოზურგეთის
  ka_from: ოზურგეთიდან
# khulo
  ka_in: ხულოში
  ka_of: ხულოს
  ka_from: ხულოდან
# telavi
  ka_in: თელავში
  ka_of: თელავის
  ka_from: თელავიდან
# gurjaani
  ka_in: გურჯაანში
  ka_of: გურჯაანის
  ka_from: გურჯაანიდან
# kvareli
  ka_in: ყვარელში
  ka_of: ყვარლის
  ka_from: ყვარლიდან
# lagodekhi
  ka_in: ლაგოდეხში
  ka_of: ლაგოდეხის
  ka_from: ლაგოდეხიდან
# sagarejo
  ka_in: საგარეჯოში
  ka_of: საგარეჯოს
  ka_from: საგარეჯოდან
# akhmeta
  ka_in: ახმეტაში
  ka_of: ახმეტის
  ka_from: ახმეტიდან
# dedoplistskaro
  ka_in: დედოფლისწყაროში
  ka_of: დედოფლისწყაროს
  ka_from: დედოფლისწყაროდან
# stepantsminda   ← also change `ka:` to `სტეფანწმინდა` and move `(ყაზბეგი)` to an alias field
  ka_in: სტეფანწმინდაში
  ka_of: სტეფანწმინდის
  ka_from: სტეფანწმინდიდან
# dusheti
  ka_in: დუშეთში
  ka_of: დუშეთის
  ka_from: დუშეთიდან
# marneuli
  ka_in: მარნეულში
  ka_of: მარნეულის
  ka_from: მარნეულიდან
# bolnisi
  ka_in: ბოლნისში
  ka_of: ბოლნისის
  ka_from: ბოლნისიდან
# shekvetili
  ka_in: შეკვეთილში
  ka_of: შეკვეთილის
  ka_from: შეკვეთილიდან
# mestia-town
  ka_in: მესტიაში
  ka_of: მესტიის
  ka_from: მესტიიდან
```

### A.2 `content/regions/*.yml` — add under `ka:`

| file | `ka.name` | `ka.name_in` (locative) | `ka.name_of` (genitive) |
|------|-----------|--------------------------|--------------------------|
| `adjara.yml` | აჭარა | აჭარაში | აჭარის |
| `guria.yml` | გურია | გურიაში | გურიის |
| `imereti.yml` | იმერეთი | იმერეთში | იმერეთის |
| `kakheti.yml` | კახეთი | კახეთში | კახეთის |
| `kvemo-kartli.yml` | ქვემო ქართლი | ქვემო ქართლში | ქვემო ქართლის |
| `mtskheta-mtianeti.yml` | მცხეთა-მთიანეთი | მცხეთა-მთიანეთში | მცხეთა-მთიანეთის |
| `racha-lechkhumi.yml` | რაჭა-ლეჩხუმი | რაჭა-ლეჩხუმში | რაჭა-ლეჩხუმის |
| `samegrelo-zemo-svaneti.yml` | სამეგრელო-ზემო სვანეთი | სამეგრელო-ზემო სვანეთში | სამეგრელო-ზემო სვანეთის |
| `samtskhe-javakheti.yml` | სამცხე-ჯავახეთი | სამცხე-ჯავახეთში | სამცხე-ჯავახეთის |
| `shida-kartli.yml` | შიდა ქართლი | შიდა ქართლში | შიდა ქართლის |
| `tbilisi.yml` | თბილისი | თბილისში | თბილისის |

### A.3 `content/settings/categories.yml` — add `ka_of` (genitive)

```yaml
- key: economy
  ka_of: ეკონომ კლასის
- key: suv
  ka_of: კროსოვერის / SUV-ის
- key: business
  ka_of: ბიზნეს კლასის
- key: offroad
  ka_of: მაღალი გამავლობის 4x4-ის
- key: minivan
  ka_of: მინივენის
- key: van
  ka_of: კომერციული ფურგონის
```

---

# Appendix B — Russian inflection data (paste-ready)

### B.1 `content/settings/categories.yml` — add `ru_of` (genitive, for `Аренда …`)

```yaml
- key: economy
  ru_of: автомобиля эконом-класса
- key: suv
  ru_of: кроссовера / SUV
- key: business
  ru_of: автомобиля бизнес-класса
- key: offroad
  ru_of: внедорожника 4x4
- key: minivan
  ru_of: минивэна
- key: van
  ru_of: коммерческого фургона
```

### B.2 `content/settings/places.yml` — add `ru_in` / `ru_from` for the five declinable names only

```yaml
# mtskheta
  ru_in: Мцхете
  ru_from: Мцхеты
# chiatura
  ru_in: Чиатуре
  ru_from: Чиатуры
# anaklia
  ru_in: Анаклии
  ru_from: Анаклии
# akhmeta
  ru_in: Ахмете
  ru_from: Ахметы
# stepantsminda
  ru_in: Степанцминде
  ru_from: Степанцминды
```

All other `places.yml` entries are indeclinable in Russian (`Тбилиси`, `Кутаиси`, `Батуми`,
`Рустави`, `Гори`, `Хашури`, `Боржоми`, `Бакуриани`, `Ахалцихе`, `Ахалкалаки`, `Зестафони`,
`Сачхере`, `Ткибули`, `Самтредиа`, `Сенаки`, `Поти`, `Зугдиди`, `Амбролаури`, `Они`, `Озургети`,
`Хуло`, `Телави`, `Гурджаани`, `Кварели`, `Лагодехи`, `Сагареджо`, `Дедоплисцкаро`, `Душети`,
`Марнеули`, `Болниси`, `Шекветили`, `Местиа`) — `ru_in`/`ru_from` may fall back to `ru`.

---

# Appendix C — plural-form tables for ru / ar / he (paste-ready)

Add to `content/settings/seo_ui.yml` and select the form by count at render time. Rules:

- **ru** — index 0 if `n%10==1 and n%100!=11`; index 2 if `n%10 in {0,5,6,7,8,9}` or `n%100 in 11..14`; else index 1.
- **ar** — 1 → `one`; 2 → `two`; 3–10 → `few`; 11–99 → `many` (singular accusative); 0 → `few`.
- **he** — 1 → `one`; 2 → `two`; else `other`.

```yaml
plural:
  days:
    ru: [день, дня, дней]
    ar: {one: يوم واحد, two: يومان, few: أيام, many: يوماً}
    ar_after_limuddah: {one: يوم واحد, two: يومين, few: أيام, many: يوماً}   # after لمدة
    he: {one: יום אחד, two: יומיים, other: ימים}
    ka: დღე            # invariant
    fa: روز            # invariant
  attractions:
    ru: [достопримечательность, достопримечательности, достопримечательностей]
    ar: {one: معلم واحد, two: معلمان, few: معالم, many: معلماً سياحياً}
    he: {one: אתר אחד, two: שני אתרים, other: אתרים}
  places:
    ru: [место, места, мест]
  models:
    ru: [модель, модели, моделей]
    ar: {one: طراز واحد, two: طرازان, few: طُرُز, many: طرازاً}
    he: {one: דגם אחד, two: שני דגמי, other: דגמי}
  routes:
    ru: [маршрут, маршрута, маршрутов]
    ar: {one: مسار واحد, two: مساران, few: مسارات, many: مساراً}
    he: {one: מסלול אחד, two: שני מסלולים, other: מסלולים}
  itineraries:
    ru: [готовый маршрут, готовых маршрута, готовых маршрутов]
    ar: {one: برنامج رحلة, two: برنامجا رحلات, few: برامج رحلات, many: برنامج رحلة}
    he: {one: מסלול טיול, two: שני מסלולי טיול, other: מסלולי טיול}
  stops:
    ru: [остановка, остановки, остановок]
    ar: {one: محطة واحدة, two: محطتان, few: محطات, many: محطة توقف}
    he: {one: תחנה אחת, two: שתי תחנות, other: תחנות}
```

Resulting corrected strings for the concrete data in the repo:

| Page | Current | Corrected |
|------|---------|-----------|
| ru route, days=1 | `маршрут для драйва, 1 дней` | `маршрут для драйва, 1 день` |
| ru route, days=2 | `исторический маршрут, 2 дней` | `исторический маршрут, 2 дня` |
| ru route, days=3 | `природный маршрут, 3 дней` | `природный маршрут, 3 дня` |
| ru route, days=4 | `прибрежный маршрут, 4 дней` | `прибрежный маршрут, 4 дня` |
| ru route, days=5/6/7/10 | `…, 5 дней` | unchanged (correct) |
| ru itinerary, days=3 | `Маршрут по Грузии на 3 дней` | `Маршрут по Грузии на 3 дня` |
| ru region, count=32/24/23/22 | `32 достопримечательностей` | `32 достопримечательности` |
| ru region, count=18/20/26/30 | `30 достопримечательностей` | unchanged (correct) |
| ru category, count=2 | `2 моделей категории …` | `2 модели категории …` |
| ru category, count=3 | `3 моделей категории …` | `3 модели категории …` |
| ar route, days=1 | `مسار قيادة ممتع، 1 أيام` | `مسار قيادة ممتع، يوم واحد` |
| ar route, days=2 | `مسار تاريخي، 2 أيام` | `مسار تاريخي، يومان` |
| ar route, days=3–10 | `مسار طبيعي، 5 أيام` | unchanged (correct) |
| ar itinerary, days=14 | `لمدة 14 أيام` | `لمدة 14 يوماً` |
| ar itinerary, days=3/5/7/10 | `لمدة 7 أيام` | unchanged (correct) |
| ar category, count=3 | `3 طرازاً من فئة …` | `3 طُرُز من فئة …` |
| ar category, count=2 | `2 طرازاً من فئة …` | `طرازان من فئة …` |
| ar itineraries hub, count=5 | `5 برنامج رحلة مُعدّ` | `5 برامج رحلات مُعدّة` |
| ar region, count=18–32 | `32 معلماً سياحياً` | unchanged (correct — 11–99 range) |
| he route, days=1 | `מסלול נהיגה נופי, 1 ימים` | `מסלול נהיגה נופי, יום אחד` |
| he route, days=2 | `מסלול היסטורי, 2 ימים` | `מסלול היסטורי, יומיים` |
| he route, days=3+ | `מסלול טבע, 5 ימים` | unchanged (correct) |

---

# Appendix D — corrected `seo_meta.yml` Georgian templates (paste-ready)

Replaces the hyphen artefacts (KA1–KA9) and applies the `გაქირავება` decision (§3.2). Placeholders
`{region_in}`, `{city_in}`, `{city_of}`, `{category_of}`, `{name_in}` are fed from Appendix A.

```yaml
# templates.car.ka
    ka:
      title: "{name}-ის გაქირავება საქართველოში — {price} ₾-დან | RentUp"
      description: "იქირავეთ {name} საქართველოში: {category}, {seats} ადგილი, {price} ₾-დან დღეში, სრული დაზღვევითა და შეუზღუდავი გარბენით."

# templates.attraction.by_type.fortress.ka
        ka:
          title: "{name} — ციხე-სიმაგრის გზამკვლევი, {drive} თბილისიდან | RentUp"
          description: "{name} — ციხე-სიმაგრე {region_in}, {km} კმ თბილისიდან ({drive}) — ისტორია, გამაგრებების მდგომარეობა და საჭირო გზა."

# templates.attraction.by_type.monastery.ka
        ka:
          title: "{name} — მონასტრის სანახავად გზამკვლევი, {drive} თბილისიდან | RentUp"
          description: "{name} — მონასტერი {region_in}, {km} კმ თბილისიდან ({drive}) — სანახავი საათები, რა ფუნქციონირებს დღემდე და როგორ ჩახვიდეთ ავტომობილით."

# templates.attraction.by_type.nature.ka
          description: "{name} — ბუნების ძეგლი {region_in}, {km} კმ თბილისიდან ({drive}) — საუკეთესო სეზონი, ბილიკის მდგომარეობა და მისასვლელი გზა."

# templates.attraction.by_type.museum.ka
          description: "{name} — მუზეუმი {region_in}, {km} კმ თბილისიდან ({drive}) — ექსპოზიცია, სამუშაო საათები და შესვლის ღირებულება."

# templates.attraction.by_type.lake.ka
          description: "{name} — ტბა {region_in}, {km} კმ თბილისიდან ({drive}) — ცურვა, ნავები, სანაპირო და საუკეთესო სეზონი."

# templates.attraction.by_type.spa.ka
          description: "{name} — თერმული აბანო {region_in}, {km} კმ თბილისიდან ({drive}) — წყლის ტემპერატურა, ინფრასტრუქტურა და დაჯავშნის დრო."

# templates.attraction.by_type.archaeology.ka
          description: "{name} — არქეოლოგიური ძეგლი {region_in}, {km} კმ თბილისიდან ({drive}) — რა არის გათხრილი და რისი ნახვა შეიძლება ადგილზე."

# templates.attraction.by_type.winery.ka
          description: "{name} — მარანი {region_in}, {km} კმ თბილისიდან ({drive}) — დეგუსტაცია, მარნის ტური და აქ დაყენებული ჯიშები."

# templates.attraction.by_type.beach.ka
          description: "{name} — პლაჟი {region_in}, {km} კმ თბილისიდან ({drive}) — საცურაო სეზონი, ქვიშა თუ ხრეში და სად გავჩერდეთ."

# templates.attraction.by_type.cave.ka
          description: "{name} — გამოქვაბული {region_in}, {km} კმ თბილისიდან ({drive}) — რა ნაწილია ღია ვიზიტორებისთვის, ტურის ხანგრძლივობა და რა წაიღოთ."

# templates.attraction.by_type.waterfall.ka
          description: "{name} — ჩანჩქერი {region_in}, {km} კმ თბილისიდან ({drive}) — მისასვლელი ბილიკი, საუკეთესო სეზონი და საჭირო ფეხსაცმელი."

# templates.attraction.by_type.canyon.ka
          description: "{name} — კანიონი {region_in}, {km} კმ თბილისიდან ({drive}) — სათვალიერო პუნქტები, საფეხმავლო ბილიკები და მისასვლელი გზა."

# templates.attraction.by_type.ski.ka
          description: "{name} — სათხილამურო კურორტი {region_in}, {km} კმ თბილისიდან ({drive}) — სეზონის ხანგრძლივობა, ბაგირგზა და ზამთრის გზა."

# templates.attraction.by_type.theatre.ka
          description: "{name} — თეატრი {region_in}, {km} კმ თბილისიდან ({drive}) — შენობა, რეპერტუარი და როგორ ვიყიდოთ ბილეთი."

# templates.region.ka
    ka:
      title: "{name} — {count} ღირსშესანიშნაობა | RentUp"
      description: "{count} სანახავი ადგილი {name_in}: მგზავრობის დრო თბილისიდან, გზის მდგომარეობა და საჭირო ავტომობილის კატეგორია თითოეულისთვის."

# templates.car_rental_hub.ka
    ka:
      title: "მანქანის გაქირავება საქართველოში | RentUp"
      description: "იქირავეთ ავტომობილი საქართველოს ნებისმიერ წერტილში: 6 მიწოდების პუნქტი, მათ შორის 3 აეროპორტი, 6 კატეგორია 75 ₾-დან და გამჭვირვალე პირობები."

# templates.car_rental_location.city.ka
      ka:
        title: "მანქანის გაქირავება {city_in} | RentUp"
        description: "აიღეთ ავტომობილი {city_in}: რომელი მარშრუტები იწყება აქედან, უახლოესი ღირსშესანიშნაობები, რეკომენდებული კატეგორია და მგზავრობის დრო."

# templates.car_rental_location.airport.ka
      ka:
        title: "{city_of} აეროპორტში მანქანის გაქირავება ({iata}) | RentUp"
        description: "იქირავეთ ავტომობილი {city_of} აეროპორტში ({iata}): მარტივი აღება, უახლოესი მარშრუტები და ღირსშესანიშნაობები, ხელმისაწვდომი კატეგორიები."

# templates.car_rental_category.ka
    ka:
      title: "{category_of} გაქირავება საქართველოში — {price} ₾-დან | RentUp"
      description: "{count} {category_of} მოდელი საქართველოში {price} ₾-დან დღეში: მახასიათებლები, ადგილების რაოდენობა, ბარგის სივრცე და შესაფერისი მარშრუტები."

# templates.home.ka
    ka:
      title: "ავტომობილების გაქირავება და მარშრუტის დაგეგმვა საქართველოში | RentUp"
      description: "იქირავეთ ავტომობილი საქართველოს ნებისმიერ წერტილში 75 ₾-დან დღეში და დაგეგმეთ მარშრუტი იმავე საიტზე — 257 ადგილისა და 32 მზა მარშრუტის მონაცემები."

# templates.faq.ka
    ka:
      title: "ხშირად დასმული კითხვები — მანქანის გაქირავება | RentUp"
      description: "30-ზე მეტი პასუხი მანქანის გაქირავებაზე საქართველოში: ფასი, საბუთები, დაზღვევა, საზღვრის კვეთა, ზამთრის მართვა და დეპოზიტის დაბრუნება."

# templates.blog.ka
      description: "პრაქტიკული სტატიები საქართველოში ავტომობილის გაქირავებასა და მართვაზე: ზამთრის გზები, საზღვრის კვეთა, ხარჯების შედარება და მარშრუტები."
```

### `seo_ui.yml` Georgian replacements

```yaml
popular_routes_from:
  ka: პოპულარული მარშრუტები {place_from}     # was: {place}-დან

car_rental:
  ka: მანქანის გაქირავება                      # was: მანქანის დაქირავება

rental_terms:
  ka: გაქირავების პირობები                     # was: დაქირავების პირობები

one_way:
  ka: ცალმხრივი გაქირავება                     # was: ცალმხრივი დაქირავება

itineraries:
  ka: მზა მარშრუტები                           # was: მზა მარშრუტების გეგმები

trip_planner:
  ka: მარშრუტის დამგეგმავი                     # was: მოგზაურობის დამგეგმავი

total_drive:
  ka: სულ მართვის დრო                          # was: სულ მართვაში
```

---

# Appendix E — token-leak replacements (all languages)

### E.1 `seo_meta.yml → templates.itinerary.*.description` — remove `{stops}`

No itinerary carries a `stops` field, and `build.py:3694` does not pass one. Either add
`stops:` to all five itinerary YAMLs and pass it, or drop the placeholder. The shorter fix:

```yaml
  itinerary:
    en:
      description: "A {days}-day Georgia itinerary covering {km} km, with a day-by-day plan, drive times and the car category it needs."
    ka:
      description: "{days}-დღიანი მარშრუტი საქართველოში — {km} კმ, დღეების მიხედვით გეგმით, მართვის დროითა და საჭირო ავტომობილით."
    ru:
      description: "Маршрут по Грузии на {days} дн. — {km} км, с планом по дням, временем в пути и нужной категорией автомобиля."
    fa:
      description: "برنامهٔ سفر {days} روزه در گرجستان شامل {km} کیلومتر، با برنامهٔ روز به روز، زمان رانندگی و دستهٔ خودروی لازم."
    he:
      description: "מסלול טיול בגאורגיה ל-{days} ימים — {km} ק״מ, עם תוכנית יומית, זמני נסיעה וקטגוריית הרכב הנדרשת."
    ar:
      description: "برنامج رحلة في جورجيا يغطي {km} كم، مع خطة يومية وأوقات قيادة وفئة السيارة المطلوبة."
```

(The `ru` title still needs the plural fix from Appendix C; `дн.` in the description sidesteps it.)

### E.2 `seo_ui.yml → popular_routes_from` — if `su()` will not be given a formatter

```yaml
popular_routes_from:
  ka: პოპულარული მარშრუტები აქედან
  en: Popular road trips from here
  ru: Популярные маршруты отсюда
  fa: سفرهای جاده‌ای محبوب از اینجا
  he: מסלולי טיול פופולריים מכאן
  ar: رحلات برية شائعة من هنا
```

The `{place_from}` version in Appendix D is better for SEO (the place name in an H2 is a
ranking signal) — use it if `build.py:3505` can be given the substitution.

### E.3 `seo_trust.yml → <lang>.editorial.policy_body` — remove `road` / `car_category`

```yaml
ka: "…ჩვენივე სტრუქტურირებული მარშრუტის მონაცემებიდან — იმავე მონაცემებიდან, რომლებიც საიტზე ჯავშნასა და ფასწარმოქმნასაც განსაზღვრავს."
en: "…from our own structured trip data — the same road-surface and vehicle-category records that also drive bookings and pricing on this site."
ru: "…из наших собственных структурированных данных о маршрутах — тех же записей о покрытии дороги и категории автомобиля, по которым на сайте формируются бронирования и цены."
fa: "…از داده‌های ساختاریافتهٔ خودمان دربارهٔ مسیرها — همان داده‌های نوع جاده و دستهٔ خودرو که رزرو و قیمت‌گذاری در سایت را نیز تعیین می‌کنند."
he: "…על נתוני המסלולים המובנים שלנו — אותם נתוני סוג הדרך וקטגוריית הרכב שקובעים גם הזמנות ותמחור באתר."
ar: "…من بيانات مساراتنا المُهيكلة الخاصة بنا — نفس بيانات نوع الطريق وفئة السيارة التي تحدد أيضاً الحجوزات والتسعير في الموقع."
```

### E.4 `content/itineraries/*.yml → <lang>.tips[]` — remove raw enums

Example, `georgia-5-days.yml` (apply the same pattern to `georgia-7-days`, `-10-days`, `-14-days`):

```yaml
en: "The recommended category for this itinerary is SUV, but the day-4 leg to Udziro Lake is graded 4x4-only — don't attempt it in a touring SUV that lacks real ground clearance."
ka: "ამ მარშრუტისთვის რეკომენდებული კატეგორიაა კროსოვერი, მაგრამ მე-4 დღის მონაკვეთი უძირო ტბამდე მხოლოდ 4x4-ისთვისაა შეფასებული — თუ თქვენს ავტომობილს რეალური გამავლობა არ აქვს, მარტო ნუ სცდით."
ru: "Рекомендуемая категория для этого маршрута — кроссовер, но участок 4-го дня к озеру Удзиро отмечен как «только 4x4» — не пытайтесь проехать его на обычном кроссовере без реального клиренса."
fa: "دستهٔ پیشنهادی این مسیر کراس‌اوور است، اما مسیر روز چهارم به دریاچه اودزیرو «فقط 4x4» درجه‌بندی شده — با خودرویی که ارتفاع واقعی از زمین ندارد، به‌تنهایی وارد آن نشوید."
he: "הקטגוריה המומלצת למסלול זה היא קרוסאובר, אך המקטע ביום הרביעי אל אגם אודזירו מדורג כ'4x4 בלבד' — אל תנסו אותו לבד ברכב ללא גובה גחון אמיתי."
ar: "الفئة الموصى بها لهذا المسار هي كروس أوفر، لكن مقطع اليوم الرابع نحو بحيرة أودزيرو مصنف كـ«دفع رباعي فقط» — لا تحاولوا سلوكه بمفردكم في سيارة بلا خلوص أرضي حقيقي."
```

```yaml
en: "The best season is June–September only: the Udziro/Buba trailhead is marked 'summer only', and Shovi itself is seasonal."
ar: "الموسم المناسب هو يونيو–سبتمبر فقط؛ مسار أودزيرو/بوبا مسجل كـ«صيفي فقط»، وشوفي نفسها موسمية."   # أوبا → بوبا
```

### E.5 `seo_categories.yml` — remove `4x4_only` from `en` body copy

```yaml
en: "…for paved highways and the gravel roads that lead to them — not the 4x4-only tracks beyond."
en: "…SUV clearance and AWD/4WD handle gravel, not the 4x4-only tracks into Tusheti, Svaneti's remoter villages or Khevsureti."
```

---

# Appendix F — build.py changes these fixes require

Listed for the engineer who applies them; **not applied here.**

| Location | Change |
|----------|--------|
| `build.py:1537`, `build.py:1570` | `te(lang,"photo_by")` reads `TRAVEL[lang]["exp"]`, but `photo_by` lives in `planner.yml → <lang>.ui`. Point the lookup at the right file/group, or copy the six values into `travel.yml → <lang>.exp`. Fixes X1 (1 488 pages). |
| `build.py:3694` | `seo_meta("itinerary", …)` must pass `stops=` (or the template must drop it, E.1). Fixes X2 (30 pages). |
| `build.py:3505` | `su("popular_routes_from", lang)` needs `.format(place=…)`. Fixes X3 (36 pages). |
| `build.py:107–130` (`seo_meta`) | `fill()` swallows `KeyError` and returns the raw template. Make it substitute what it can and log the missing key, so a future gap degrades to one bad word rather than a whole raw string. |
| `build.py:2050–2053` | `desc` is unconditionally overwritten from `L["short"] + L["body"]`, so `templates.region.<lang>.description` never renders. Either use `_sd` or delete the template. |
| new | `seo_meta()` needs the inflected placeholders: `region_in`/`region_of`/`name_in` from the region YAML, `city_in`/`city_of`/`place_from` and `ru_in`/`ru_from` from `places.yml`, `category_of`/`ru_of` from `categories.yml` (Appendices A, B). |
| new | A `plural(n, lang, key)` helper reading the `plural:` block in Appendix C, applied to `days`, `count` and `stops` in every `route`, `itinerary`, `region`, `routes_hub`, `itineraries_hub` and `car_rental_category` template. |
| `build.py:1234–1239` | `routes_hub`, `blog` and `post` exist in `seo_meta.yml` but are never passed to `seo_meta()` — the `_tpl` map covers only `index/fleet/terms/faq/about/contact/community/software`. Either wire them or delete them; today `/tours/` uses page YAML and ignores the template entirely. |

---

## Fix order

1. **X1** `photo_by` — one lookup, 1 488 pages, all six languages. Biggest ratio of impact to effort.
2. **§8** en-dash time ranges — 781 RTL pages currently painting times backwards.
3. **KA1–KA8** Georgian case suffixes — ~210 pages in the primary market, including every commercial `/ka/car-rental/*` page.
4. **RU1–RU7** Russian numeral and case agreement — 31 pages, all of them titles.
5. **X2, X3, X4, X5** raw token leaks — 66 pages plus the not-yet-live trust copy.
6. **AR1–AR4, HE1–HE2** Arabic and Hebrew numeral agreement — 24 titles.
7. **§3.2 / §3.3** the `გაქირავება` / `ქირაობა` cleanup — no pages break, but it is the Georgian keyword decision and everything else in ka should be edited in the same pass.
8. **FA1, AR7** digit-system consistency; **KA18, HE4** quotation typography.
