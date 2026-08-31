# `/car-rental/monthly/` — content report

**Written:** 2026-08-31 · **Content lives in:** `content/settings/seo_car_rental.yml` →
new top-level `durations:` block, key `monthly` · **Brief:** `docs/seo/CONTENT_BRIEFS.md` §Brief 4 ·
**Ranking:** `docs/seo/KEYWORD_CLUSTERS.md` A20 (#2 of 20)

Only two files were touched: `content/settings/seo_car_rental.yml` (the new block plus four
lines added to the file's own header comment documenting the `durations:` shape) and this report.
`build.py` was not opened for editing.

---

## 1. The measured price table

Computed directly from all 17 `content/cars/*.yml` records — `price_1_6`, `price_7_29`,
`price_30`, `deposit` — not taken from any prose source. One row per category, using the
**cheapest car in that category at the 30+ day tier**.

| Category | Cheapest car | 30+ day rate | 30 days at that rate | Same 30 days at the 1–6 day rate | Saving | Saving % | Deposit / CDW excess |
|---|---|---|---|---|---|---|---|
| Economy class | Toyota Prius | **56 ₾/day** | **1 680 ₾** | 2 250 ₾ | −570 ₾ | 25.3% | 300 ₾ |
| Crossover / SUV | Hyundai Tucson | 98 ₾/day | 2 940 ₾ | 3 900 ₾ | −960 ₾ | 24.6% | 600 ₾ |
| Commercial van | Ford Transit | 139 ₾/day | 4 170 ₾ | 5 550 ₾ | −1 380 ₾ | 24.9% | 800 ₾ |
| Minivan | Mercedes-Benz Vito | 150 ₾/day | 4 500 ₾ | 6 000 ₾ | −1 500 ₾ | 25.0% | 1 000 ₾ |
| Business class | Toyota Camry | 158 ₾/day | 4 740 ₾ | 6 300 ₾ | −1 560 ₾ | 24.8% | 1 000 ₾ |
| Off-road 4x4 | Mitsubishi Pajero | 180 ₾/day | 5 400 ₾ | 7 200 ₾ | −1 800 ₾ | 25.0% | 1 200 ₾ |

### Both figures in the task brief check out

- **"the cheapest is 56 ₾/day, so about 1 680 ₾ for thirty days"** — confirmed. Toyota Prius
  `price_30: 56`; 56 × 30 = 1 680 ₾ exactly. Independently corroborated by
  `content/pages/pricing.yml`'s published "Monthly package" column, which lists 1 680 ₾ for
  economy class. All six of my computed 30-day totals match that column cell for cell
  (1 680 / 2 940 / 4 740 / 5 400 / 4 500 / 4 170).
- **"roughly 24–25% below the daily rate"** — confirmed, and it is tighter than that. Measured
  across **all 17 cars**, the 30-day discount off the same car's `price_1_6` runs from **24.4%**
  (Hyundai Elantra, 82 → 62) to **25.3%** (Toyota Prius, 75 → 56). The 7–29 day tier runs
  9.3%–10.3%. Both tiers are consistent to within one percentage point fleet-wide, which is why
  the page states the range rather than a rounded marketing number.

Full per-car working (all 17, sorted by category then 30-day rate):

| Car | Category | 1–6 | 7–29 | 30+ | 7-day disc. | 30-day disc. | 30 days | Deposit |
|---|---|---|---|---|---|---|---|---|
| Toyota Prius | economy | 75 | 68 | 56 | 9.3% | 25.3% | 1 680 | 300 |
| Hyundai Elantra | economy | 82 | 74 | 62 | 9.8% | 24.4% | 1 860 | 300 |
| Toyota Corolla | economy | 88 | 79 | 66 | 10.2% | 25.0% | 1 980 | 300 |
| Hyundai Tucson | suv | 130 | 117 | 98 | 10.0% | 24.6% | 2 940 | 600 |
| Mitsubishi Outlander | suv | 138 | 124 | 104 | 10.1% | 24.6% | 3 120 | 600 |
| Toyota RAV4 | suv | 145 | 130 | 109 | 10.3% | 24.8% | 3 270 | 600 |
| Toyota Camry | business | 210 | 189 | 158 | 10.0% | 24.8% | 4 740 | 1 000 |
| Mercedes-Benz E-Class | business | 290 | 261 | 218 | 10.0% | 24.8% | 6 540 | 1 000 |
| BMW 5 Series | business | 310 | 279 | 232 | 10.0% | 25.2% | 6 960 | 1 000 |
| Mitsubishi Pajero | offroad | 240 | 216 | 180 | 10.0% | 25.0% | 5 400 | 1 200 |
| Mitsubishi Delica D:5 | offroad | 290 | 261 | 218 | 10.0% | 24.8% | 6 540 | 1 200 |
| Toyota Land Cruiser Prado | offroad | 330 | 297 | 248 | 10.0% | 24.8% | 7 440 | 1 200 |
| Mercedes-Benz Vito | minivan | 200 | 180 | 150 | 10.0% | 25.0% | 4 500 | 1 000 |
| Hyundai Staria | minivan | 260 | 234 | 195 | 10.0% | 25.0% | 5 850 | 1 000 |
| Toyota Alphard | minivan | 310 | 279 | 232 | 10.0% | 25.2% | 6 960 | 1 000 |
| Ford Transit | van | 185 | 166 | 139 | 10.3% | 24.9% | 4 170 | 800 |
| Mercedes-Benz Sprinter | van | 215 | 194 | 161 | 9.8% | 25.1% | 4 830 | 800 |

Fleet range at the 30+ tier: **56–248 ₾/day**.

**One precision note for whoever writes the on-page table caption.** `price_1_6` in
`content/cars/*.yml` is *not* the site's highest daily rate. `pricing.yml` splits short rentals
into 1–2 days and 3–6 days, and the car files' `price_1_6` equals the **3–6 day** column
(economy 75 ₾, while 1–2 days is 85 ₾). The page therefore says the saving is measured against
the car's "1–6 day price", which is what the car files hold. Measured against `pricing.yml`'s
1–2 day column the saving would look larger (economy 56 vs 85 = 34.1%) — that comparison was
deliberately **not** used, because no per-car field supports it.

---

## 2. Every commercial claim on the page, and where it comes from

| Claim as written | Source |
|---|---|
| No prepayment; the request is confirmed by phone or email and payment is made at pickup | `content/pages/terms.yml` en/blocks[16].items[0] "Booking requests are confirmed by phone or email; no prepayment is required"; `content/pages/pricing.yml` en/blocks[17].items[3] "Booking is confirmed by phone or email; payment is made at pickup"; `content/settings/rental_policy.yml` `cancellation.prepayment_required: false`. Owner decision of 2026-08-30. |
| No maximum rental length; the 30+ rate applies from day 30 onwards | `rental_policy.yml` — `max_rental_days` was removed as unsourced (see the file's own comment, lines 86–92) and `docs/seo/FACT_RECONCILIATION.md` row "Max. rental length"; `pricing.yml`'s rate table is open-ended past "30+ days". Owner confirmed 2026-08-30. |
| Documents: passport (Georgian citizens, ID card), licence held 2+ years, card for the deposit; IDP if the licence is not in Latin script | `terms.yml` en/blocks[1] (requirements-by-nationality table) and blocks[2] (IDP note); `faq.yml` en/blocks[3].items[0]. |
| Deposit by category: 300 / 600 / 800 / 1000 / 1200 ₾ | `content/cars/*.yml` `deposit` field on all 17 cars; identical to `pricing.yml` en/blocks[12] (deposit & excess table). |
| Deposit blocked on a card, or taken in cash and returned on the spot; released within 3 working days | `pricing.yml` en/blocks[11]; `faq.yml` en/blocks[5].items[0]; `rental_policy.yml` `deposit.method: card_hold`, `cash_accepted: true`, `released_days: 3`. |
| Deposit does not change with rental length | Absence of any duration qualifier on the `deposit` field in `content/cars/*.yml` and on `pricing.yml`'s deposit table; `rental_policy.yml` `deposit.waiver_available: false`. Stated as "does not shrink", i.e. a negative claim about what is *not* discounted — not an invented benefit. |
| CDW and TPL included in the rate | `terms.yml` en/blocks[9]; `pricing.yml` en/blocks[4].items[0-1]; `rental_policy.yml` `insurance.included: tpl_cdw`. |
| CDW excess varies by category: 300 economy / 600 crossover / 800 van / 1000 business & minivan / 1200 off-road 4x4 | `pricing.yml` en/blocks[12] (CDW excess column); `faq.yml` en/blocks[5].items[1] (300 economy, 1 200 4x4). **The excess is stated in the same sentence as the insurance, in all six languages.** |
| CDW does not cover tyres, wheels, underbody, mirrors or interior; a replacement tyre is 120–400 ₾ | `terms.yml` en/blocks[11].items[3]; `faq.yml` en/blocks[5].items[2]. |
| SCDW is a paid upgrade at 25–45 ₾/day depending on category | `pricing.yml` en/blocks[6] extras table; `faq.yml` en/blocks[5].items[1]. Deliberately phrased as an upgrade that exists, **without** repeating the "reduces the excess to zero" wording — see §4. |
| Mileage unlimited within Georgia, unchanged at 30 days | `rental_policy.yml` `mileage.unlimited: true` (no duration qualifier); `pricing.yml` en/blocks[4].items[2]; `faq.yml` en/blocks[7].items[3]. |
| Servicing and wear items — oil, filters, tyres — included in the rate | `pricing.yml` en/blocks[4].items[3] "**Servicing and wear items** — oil, filters, tyres"; `faq.yml` en/blocks[1].items[4] ("includes VAT, CDW and TPL insurance, servicing and unlimited mileage"). |
| Winter tyres on every car 1 December – 1 April | `pricing.yml` en/blocks[4].items[5]; `faq.yml` en/blocks[7].items[2]. |
| 24/7 roadside assistance nationwide | `pricing.yml` en/blocks[4].items[4]; `faq.yml` en/blocks[11].items[4]; `rental_policy.yml` `support.roadside_assistance: true`, `hours_key: always` with the inline "owner confirmed 24/7" note. Owner confirmed 2026-08-30. |
| Replacement car within six hours, free, for a technical fault not caused by the renter | `faq.yml` en/blocks[11].items[4], verbatim scope ("if the fault is technical and not caused by the renter"). |
| Fuel full to full; missing fuel charged plus a 20 ₾ service fee | `terms.yml` en/blocks[7].items[0-1]; `pricing.yml` en/blocks[20] penalty row; `rental_policy.yml` `fuel_policy: full_to_full`. |
| Delivery free from the fifth day: office, any Tbilisi address, all three airports; Telavi/Gori/Zugdidi 50 ₾; border handover from 120 ₾ | `pricing.yml` en/blocks[8] delivery table, "5+ days" column. This is the one genuinely *new* long-rental benefit on the page and it is read straight off that column, not inferred. |
| Date changes free if the car is available | `terms.yml` en/blocks[16].items[4]. |
| Early return refunded, whole rental re-rated at the tier for the days actually used | `terms.yml` en/blocks[16].items[5] "unused days are refunded, recalculated at the rate applicable to the actual rental length". The worked example (a 30-day booking ended on day 20 falls back to the 7–29 tier) is arithmetic on that rule plus the car files' tier fields. |
| Young-driver surcharge: 15 ₾/day crossover & minivan ages 23–25; 25 ₾/day business & 4x4 ages 25–27; none on economy; 450 ₾ / 750 ₾ over thirty days | `terms.yml` en/blocks[4] (age table, per-category surcharge column); `faq.yml` en/blocks[1] band summary; `rental_policy.yml` `young_driver.bands` ("confirmed by the owner 2026-08-30"). The 450/750 totals are 15×30 and 25×30. |
| Seasonal adjustment +15% July–August, +10% Easter and New Year weeks | `pricing.yml` en/lead ("a seasonal adjustment applies in July and August (+15%)"); `faq.yml` en/blocks[1].items[5] (adds the +10% Easter/New Year weeks). |
| Traffic fines can arrive up to 30 days after return | `faq.yml` en/blocks[5].items[3]. |
| Companies taking 3+ cars for over 3 months are quoted individually; a 12–36 month operating rental is a separate product | `pricing.yml` en/blocks[14] ("Contracts longer than 3 months and covering 3 or more vehicles are priced individually"); `faq.yml` en/blocks[11].items[5]. **No percentage published** — see §4. |

---

## 3. What the page says about the reader, and what it refuses to promise

The page is written for someone staying a month or more — a remote worker, a family relocating,
a long project — and is explicit that **almost nothing changes at thirty days except the price
and the delivery fee**. Mileage was already unlimited, the deposit is the same as on a one-day
booking, the excess is the same, the insurance terms are the same, the fuel rule is the same,
and the young-driver surcharge is charged per day so it *grows* with length rather than being
absorbed. That honesty is the page's differentiator; the competitor pages listed in
`CONTENT_BRIEFS.md` Brief 4 all sell "monthly" as a package without saying which terms move.

Prose keys used, and what is in each (for the renderer):

- `lead` — the tier and the two headline numbers (56 ₾/day, 1 680 ₾).
- `pickup` — starting a long rental: no prepayment, documents, deposit by category, delivery
  becoming free at length.
- `getting_around` — living with the car for a month: mileage, servicing and wear items,
  winter tyres, 24/7 assistance and the six-hour replacement, insurance **with the excess
  stated**, what CDW excludes, SCDW, fuel, fines arriving late.
- `good_to_know` — six bullets: no maximum length; extension and early-return re-rating;
  young-driver cost over thirty days; seasonal adjustment; deposit unchanged; corporate and
  operating-rental products being out of scope of the table.

`route_slugs` and `nearest_attraction_slugs` were **deliberately left out** — a duration page has
no geography, and inventing route lists for it would be padding. See §5 for the consequence.

---

## 4. What I refused to state

1. **The "up to 40% corporate discount".** `faq.yml` en/blocks[1].items[1] states it and
   `pricing.yml` en/blocks[15].items[0] states "25–40% off the base rate, depending on volume".
   No price field anywhere in `content/` supports a fourth tier, and `CONTENT_BRIEFS.md` §0.3
   flags the figure as unverified. The page says corporate contracts are "quoted individually"
   and gives no percentage. **Owner must confirm a real corporate rate card before any number
   is published.**
2. **"Zero excess" / "full coverage with no deductible" — never written, in any language.**
   `pricing.yml`'s deposit table does say SCDW takes the excess to 0 ₾ (and to 300 ₾, not 0, on
   off-road 4x4 — the one category where the "zero" claim would be false anyway). The page
   describes SCDW only as a paid upgrade at 25–45 ₾/day and always prints the standard excess
   beside the insurance sentence.
3. **A long-term discount other than the measured one.** The page publishes only what the car
   files contain: the 7–29 and 30+ tiers, at the measured 24.4%–25.3%. No "extra 5% for three
   months", no negotiable rate, no loyalty tier.
4. **Any delivery arrangement not in `pricing.yml`'s table.** No free delivery outside what the
   "5+ days" column states; no monthly re-delivery, no doorstep swaps.
5. **Any vehicle-swap or scheduled-servicing arrangement.** Nothing in `content/` says who books
   an oil change on a 90-day rental, where the car goes during it, or whether a courtesy car is
   provided for routine (as opposed to fault) servicing. The page states only the two things that
   *are* sourced: servicing and wear items are included in the rate (`pricing.yml`), and a
   *technical fault not caused by the renter* gets a free replacement within six hours
   (`faq.yml`). **Owner ask below.**
6. **A monthly billing arrangement.** `pricing.yml` promises corporate clients "a single monthly
   invoice"; nothing says how an individual on a 90-day rental is billed — one payment at pickup,
   or monthly. The page says only "payment is made at pickup", which is what the sources say.
   **Owner ask below.**
7. **How the seasonal +15% composes with the 30+ tier.** `pricing.yml`'s lead applies the
   adjustment to "the rates" generally, and its monthly table sits under that lead, so the page
   states the adjustment exists and tells the reader to ask for a written quote if their month
   crosses July–August. It does not compute a summer monthly price. **Owner ask below.**

---

## 5. Things the owner or the renderer must decide

**For the owner:**

1. **Corporate rate card.** Is the 25–40% band in `pricing.yml` real and current, and does it
   still require both ">3 months" *and* "3+ vehicles"? Until confirmed, the monthly page will
   keep saying "quoted individually".
2. **Routine servicing on a long rental.** Who arranges the oil change / periodic service on a
   60- or 90-day rental, where does the customer take the car, how long is it off the road, and
   is a replacement provided for *scheduled* servicing (the six-hour replacement is documented
   only for faults)? This is the single most-asked question on a monthly-rental page and the
   repo cannot currently answer it.
3. **Billing rhythm for individuals on long rentals.** One payment at pickup for the whole
   1 680 ₾+, or monthly instalments? Sources say only "payment is made at pickup".
4. **Does the July–August +15% apply to the 30+ day tier?** If it does not, that is a strong,
   publishable fact for the page. If it does, the page should probably show the summer monthly
   figure outright.
5. **Is there a long-rental deposit practice that differs from the daily one** (e.g. a card hold
   re-authorised monthly)? Nothing states one; the page currently says the deposit is identical
   to a one-day booking.
6. Still open from `docs/seo/FACT_RECONCILIATION.md` and unaffected by this page:
   `content/pages/index.yml`'s hero still says "full insurance coverage", and `site.yml`'s
   `usd_rate: 2.6` disagrees with `pricing.yml`'s 2.70 ₾/USD (the page publishes no USD figures,
   partly for that reason).

**For whoever writes the renderer:**

- `rental_quality_ok()` in `build.py` gates location pages on `route_slugs >= 2` and
  `nearest_attraction_slugs >= 3`. The `monthly` entry has neither by design. A
  `kind == "duration"` branch is needed — a sensible gate is
  `len(data["category_keys"]) >= 1 and len(data["price_table"]) >= 1`.
- `data.price_table` is the on-page table. Each row: `category` (a key that resolves through
  `content/settings/categories.yml` for the localised label), `car_slug`, `price_1_6`,
  `price_7_29`, `price_30`, `thirty_days_gel`, `thirty_days_at_short_rate_gel`, `saving_gel`,
  `saving_pct`, `deposit_gel`, `excess_gel`. Rows are ordered cheapest-first by 30-day rate.
  `data` also carries `tier_days: 30`, `fleet_min_price_30`, `fleet_max_price_30`,
  `saving_pct_min`, `saving_pct_max` for headings and any `AggregateOffer` node.
- Column headings and the table caption are not in this file — they belong in
  `content/settings/seo_ui.yml` alongside the other six-language UI strings.
- The `getting_around` key carries "what a month with the car is like", not geography. Give it a
  duration-scoped heading rather than reusing the location template's wording.
- Internal links the brief asks for (`/fleet/`, `/car-rental/`, the six category pages,
  `/pricing/`, `/terms/`) are not embedded in the copy — `data.category_keys` and
  `price_table[].car_slug` give the renderer everything it needs to build them.
- If the numbers in `content/cars/*.yml` change, `data.price_table` goes stale. It is a cached
  computation, and the safest long-term fix is for the renderer to derive the table from `CARS`
  at build time and use this block only for the prose.

---

## 6. Verification run

```
python3 -c "import yaml; yaml.safe_load(open('content/settings/seo_car_rental.yml',encoding='utf-8'))"   → parses
python3 build.py --validate-only                                                                          → ✔ content validation passed
```

(One pre-existing, unrelated warning: `cars: 17 published records have no main image` — present
before this change, documented in `FACT_RECONCILIATION.md`.)

Language checks run over the new block: `meta_title` 51–57 characters in all six languages
(limit 65, including " | RentUp"); `meta_description` 144–156 characters in all six (target
140–158). Georgian contains no instance of `ქირაობა` or `ექსცესი`, uses `გაქირავება` in company
voice and `დაქირავება` where the customer is the subject, and declines place names normally.
`fa`, `he` and `ar` contain no dash between two digits anywhere — every numeric range is written
with `تا` / `עד` / `إلى` so it does not reverse under bidi.
