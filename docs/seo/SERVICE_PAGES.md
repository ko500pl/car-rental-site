# Service landing pages — one-way, with-driver, airport-pickup (2026-09-01)

Three service pages were added as new keys under `durations:` in
`content/settings/seo_car_rental.yml` (lines 2552–3816), so the renderer maps them to
`/car-rental/one-way/`, `/car-rental/with-driver/` and `/car-rental/airport-pickup/`
(plus `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`). Each carries the same per-language keys as
`monthly` — `h1, meta_title, meta_description, lead, pickup, getting_around, good_to_know[]`
— in all six languages, plus a `data:` block. They are **not** price-tier pages, so there is
no `price_table`. Nothing else in the file was changed (first 2551 lines are byte-identical
to the pre-edit copy).

Briefs followed: `docs/seo/CONTENT_BRIEFS.md` #8 (one-way) and #9 (with-driver). Brief #9
asked for owner confirmation of the driver rate before publishing; that rate turned out to be
already published in two places (`faq.yml`, `pricing.yml`), so it is used here as a repo
fact, not an unconfirmed one.

---

## BLOCKER — build.py will not render these pages as-is

`build.py:3781–3786`:

```python
if kind == "duration":
    d = payload.get("data") or {}
    return (len(d.get("price_table") or []) >= 3
            and len(d.get("category_keys") or []) >= 3)
```

`render_rental_duration()` (`build.py:4231`) returns `None` when this gate fails, and the
sitemap loop (`build.py:3326`) skips the key too. With no `price_table`, all three service
pages are silently **not written and not in the sitemap**. `python3 build.py --validate-only`
passes because validation does not exercise the gate.

Per this task's file list build.py was not edited. Whoever owns build.py needs one change:

- Each new entry carries `data.kind: service`. Extend the gate so a `duration` payload with
  `data.kind == "service"` passes on `category_keys` alone (≥ 3 for one-way and
  airport-pickup, exactly 3 for with-driver — that is all the categories the driver service
  is offered on, so a "≥ 3" threshold is still met).
- `_duration_price_table()` already returns `""` for an empty table, and the `Product` /
  `AggregateOffer` node is already dropped when there are no rows (`if rows else None`), so
  nothing else in `render_rental_duration` breaks. For with-driver a `Service` node
  (`serviceType: "Chauffeur-driven car rental"`, brief #9) would be the correct schema; for the
  other two, `WebPage` + breadcrumbs is enough.

### Three smaller things the renderer should pick up (not blockers)

1. **Section heading** — `render_rental_duration` labels the `getting_around` block with
   `seo_ui.yml → dur_a_month_with_the_car` ("A month with the car"). Wrong for service pages;
   a generic key (e.g. `svc_on_the_road` / "On the road") should be used when
   `data.kind == "service"`. `dur_what_it_costs` is skipped automatically (empty table).
2. **`cheapest_price()` (`build.py:2478`)** maps `business` and `minivan` to the *economy*
   price, so the category cards on `with-driver` (category_keys `business, minivan, offroad`)
   would show "from 75 ₾" for business class and minivan instead of the real 210 ₾ / 200 ₾
   (`content/cars/toyota-camry.yml`, `mercedes-benz-vito.yml`). Pre-existing bug; it affects
   the monthly page's cards too.
3. **Cross-links** — page text goes through `E()` so anchors cannot be written into prose.
   Each entry therefore carries `data.location_keys` (the location entries to link:
   airport-pickup → `tbilisi-airport, kutaisi-airport, batumi-airport`; one-way → all six;
   with-driver → the office plus the three airports) and `data.related_keys` (the other two
   service pages). The renderer should turn these into a link row / card list. The prose
   refers to "the airport pickup page", "the one-way page", "Tbilisi Airport, Kutaisi Airport
   and Batumi Airport" so the links read naturally once rendered.

---

## Every figure and where it comes from

| Figure | Used on | Source |
|---|---|---|
| One-way available; **100 ₾** between Tbilisi, Kutaisi and Batumi (city or airport) | one-way, airport-pickup | `rental_policy.yml:79–81` (`one_way.available: true`, `fee_gel: 100`); `faq.yml:278` (en) / `:116` (ka) "start at 100 GEL"; `pricing.yml:470–473` "One-way rental, from 100 ₾, Tbilisi↔Kutaisi↔Batumi" |
| Other cities for one-way: "by arrangement", quoted individually | one-way | `faq.yml:278` "Other cities by arrangement" (same in ka/ru/fa/he/ar) |
| Tbilisi office and any Tbilisi address: free delivery at every length | all three | `pricing.yml:493–502`; `rental_policy.yml:62–64` |
| Tbilisi Airport (TBS) **40 ₾** on 1–2 days, **free from the 3rd day** | all three | `pricing.yml:503–507`; `rental_policy.yml:66–67`; `faq.yml:273` "In Tbilisi delivery is free from 3 days" |
| Kutaisi Airport (KUT) **60 ₾** on 1–4 days, **free from the 5th day** | all three | `pricing.yml:508–512`; `rental_policy.yml:68`; `faq.yml:273–274` |
| Batumi Airport (BUS) **50 ₾** on 1–4 days, **free from the 5th day** | all three | `pricing.yml:513–517`; `rental_policy.yml:69–70`; `faq.yml:273–274` |
| Kutaisi / Batumi city address **40 ₾** on 1–4 days, free from the 5th | one-way | `pricing.yml:518–522`; `rental_policy.yml:71–73` |
| Night handover **and return** surcharge **40 ₾**, **22:00–07:00**; handover "24 hours a day" | all three | `rental_policy.yml:74–76`; `pricing.yml:533–536` ("Night handover and return"); `faq.yml:275–276` ("Yes, 24 hours a day") |
| Chauffeur **120 ₾ / day (8 hours)**, overtime **20 ₾ / hour** | with-driver | `faq.yml:138–141` (ka) / `:300–303` (en) / `:462–464` (ru) / `:619–621` (fa) / `:764–766` (he) / `:925–927` (ar); `pricing.yml:466–469` "Chauffeur service, 120 ₾ / day, 8 hours, overtime 20 ₾/h" |
| Driver offered on **business class, minivans and 4x4** only | with-driver (prose + `category_keys`) | `faq.yml:140–141` (ka) / `:303` (en) and the other four languages |
| Driver fee is an add-on to the car's rate | with-driver | `pricing.yml:432–469` — chauffeur is a row of the "Optional extras / Cost of additional services" table |
| Booking form "I need a driver" checkbox (ka «მძღოლით მჭირდება», ru «Нужен водитель», fa «راننده لازم دارم», he "אני צריך נהג", ar «أحتاج سائقاً»); pickup / return location fields | with-driver, one-way | `build.py:1207–1212` `inquiry_widget()` — `tx[12]`, `tx[13]`, `tx[14]`, input `name="with_driver"` |
| Business class from **210 ₾**, minivan from **200 ₾**, off-road 4x4 from **240 ₾** a day (→ cheapest chauffeured car 320 ₾ for 8 h; 12-h day = 200 ₾ driver; 2 days = 240 ₾ driver) | with-driver | `content/cars/toyota-camry.yml`, `mercedes-benz-vito.yml`, `mitsubishi-pajero.yml` (`price_1_6`), as already published in `seo_car_rental.yml` monthly `price_table`; `faq.yml:178–179` also states the 4x4 240 ₾ figure. The 320/200/240 figures are arithmetic on those, not new prices |
| 7–29 day price from the 7th day, 30+ from the 30th | with-driver | `faq.yml:180–183`; `seo_car_rental.yml` monthly `price_table` (`price_7_29`, `price_30`) |
| Deposit **300 / 600 / 800 / 1000 / 1200 ₾** (economy / crossover / commercial van / business+minivan / 4x4) | one-way, airport-pickup | `pricing.yml` deposit table (l. 544ff); `rental_policy.yml:44–46`; identical wording to `durations.monthly` |
| CDW + TPL included; **excess 300 / 600 / 800 / 1000 / 1200 ₾** by category; SCDW **25–45 ₾ / day** brings it to zero | one-way, airport-pickup | `terms.yml:324–328`; `pricing.yml:462–465`; `faq.yml:229–232`; `rental_policy.yml:109–131`. Not mentioned on with-driver (no source says who bears the excess when RentUp supplies the driver) |
| Unlimited mileage inside Georgia | all three | `rental_policy.yml:38–39`; `faq.yml:259–262`; `pricing.yml:427` |
| Fuel full-to-full; missing fuel + **20 ₾** service fee | all three | `terms.yml:314–317`; `rental_policy.yml:55–58` |
| Roadside assistance 24/7; replacement car within **6 hours** at no charge | all three | `faq.yml:308–311`; `pricing.yml:429`; `rental_policy.yml:180–181` |
| Handover report with photos (four sides, interior, odometer, fuel) | one-way, airport-pickup | `faq.yml:283–287` (ka `:122–125`) |
| Late return: **2 h** free, then **1/3** daily rate per **3 h** started, > **8 h** = full day | one-way, airport-pickup | `faq.yml:279–282`; `pricing.yml:535–536`; `terms.yml:419–420` |
| Cancellation free > **48 h**, one day's rate **24–48 h**, two days' rate < **24 h** / no-show; date change free if car available | one-way, airport-pickup | `terms.yml:379–385`; `rental_policy.yml:147–155` |
| No prepayment; request confirmed by phone or email; pay at pickup | all three | `terms.yml:379`; `faq.yml:184–187`; `rental_policy.yml:163` (flagged CONFLICT there; the monthly page already uses this wording, so the service pages match it) |
| Documents: passport (ID card for Georgian citizens), licence held ≥ **2 years**, IDP if not Latin-script, card for deposit | one-way, airport-pickup | `terms.yml:233–267`; `faq.yml:205–212` |
| Age / experience: business **25 y / 5 y**, minivan **23 y / 3 y**, off-road 4x4 **25 y / 4 y**; driving by a person not named on the agreement is not insured | with-driver | `terms.yml:278–302`, `:334` |
| Child seat **10 ₾ / day**, groups **0–3, 3–7, 7–12**; law requires a seat under 12 | with-driver | `faq.yml:304–307`; `pricing.yml:446–449` |
| Meeting point: flight number at booking, name sign at arrivals, handover in the terminal car park, "whatever the airline" | airport-pickup, one-way, with-driver | `seo_car_rental.yml → locations.tbilisi-airport / kutaisi-airport / batumi-airport → pickup` (all six languages) |
| TBS ≈ **13 km** east of centre on the Kakheti highway; KUT ≈ **21 km** from Kutaisi, nearer Vani; BUS ≈ **5 km** south of central Batumi, near Sarpi | airport-pickup | `seo_car_rental.yml → locations.*-airport → getting_around` |
| Turkey: **250 ₾**, selected categories, **48 h** notice; otherwise the car stays in Georgia | airport-pickup | `terms.yml:355–374`; `seo_car_rental.yml → locations.batumi-airport` |
| "Flights into Tbilisi / low-cost slots into Kutaisi often land late" | airport-pickup | `seo_car_rental.yml → locations.tbilisi-airport.good_to_know[0]`, `locations.kutaisi-airport.good_to_know[1]` |

### Deliberately not claimed

- No discount of any kind on one-way, driver or airport pickup.
- No per-car or per-category restriction on one-way (brief #8 asked the owner; no source
  either way, so the page says nothing about it).
- No driver language guarantee (`rental_policy.yml → support.languages` is the *support*
  list, per brief #9's caveat).
- No statement about deposit or insurance excess on with-driver.
- No same-day drop-off-city availability claim (brief #8 do-not-claim list).
- No meeting-point detail beyond what the three airport location entries already publish
  (no terminal names, desk numbers, waiting times).
- No return-end fee on one-way: `pricing.yml`'s table is headed "Delivery charges by
  location" under "Delivery and return", and does not say whether an airport *return* carries
  the location fee. The page prices the pickup end only and says the quote lists the one-way
  fee and any delivery fee separately. **Owner ask:** does a one-way *return* at KUT/BUS/TBS
  carry the airport fee on short rentals?

### Language notes

- Georgian is in company voice — `გაქირავება` throughout, no `ქირაობა` (grep-checked); place
  names declined (`თბილისში`, `ქუთაისში`, `ბათუმში`, `აეროპორტში`). The one-way term follows
  `pricing.yml`'s own row, `ერთმხრივი გაქირავება` (the location pages use `ცალმხრივი`; both
  are current — worth unifying in a later pass).
- fa/he/ar write ranges as words (`22:00 تا 07:00`, `בין 22:00 ל-07:00`, `بين 22:00 و07:00`,
  `25 تا 45`, `25 עד 45`, `من 25 إلى 45`) rather than with a hyphen, matching the monthly page.
- `meta_title` ≤ 65 chars including " | RentUp" in every language (longest: ru one-way, 65);
  `meta_description` 140–158 chars in every language; `good_to_know` 6 items (one-way) or 7
  (with-driver, airport-pickup) per language.

### Follow-ups already noted in the briefs

- The six location pages each restate the 100 ₾ one-way fee in `good_to_know`; brief #8 asks
  that they link to `/car-rental/one-way/` instead of restating it (cannibalisation guard).
- The hub (`/car-rental/`) has no link to any of the three service pages yet — brief batch
  item "More ways to rent" section.
