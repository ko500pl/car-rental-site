# Practical guides — winter driving & rental requirements (2026-09-01)

Two guides added to `content/guides/`, complete in ka/en/ru/fa/he/ar, same schema as
`driving-in-georgia.yml` (top-level `slug/order/image/updated/car_category/related_routes/
related_attractions`, per-language `name/short/meta_title/meta_description/body/faq`).

| File | URL | order | Hero image | car_category |
|---|---|---|---|---|
| `content/guides/winter-driving-in-georgia.yml` | `/guides/winter-driving-in-georgia/` | 40 | `/assets/photos/bakuriani.webp` | `suv` |
| `content/guides/car-rental-georgia-requirements-documents.yml` | `/guides/car-rental-georgia-requirements-documents/` | 41 | `/assets/photos/narikala-fortress.webp` | `economy` |

Both pass `python3 build.py --validate-only`, render in all six languages through
`render_guide()`, and clear `guide_quality_ok()` (name + body ≥ 1500 chars + meta_description)
in every language. Every internal link was checked against existing slugs in
`content/attractions`, `content/routes`, `content/guides`, `content/posts` and the
`/car-rental/*` cluster (`economy suv 4x4 minivan business van monthly` all pass
`rental_quality_ok`, so the links are live, not 404s).

## Measured limits

| | en | ka | ru | fa | he | ar |
|---|---|---|---|---|---|---|
| Winter — body words | 1,144 | 932 | 1,025 | 894 | 819 | 840 |
| Winter — meta_title chars | 57 | 54 | 52 | 53 | 52 | 51 |
| Winter — meta_description chars | 156 | 155 | 156 | 157 | 148 | 157 |
| Winter — FAQ items | 6 | 6 | 6 | 6 | 6 | 6 |
| Requirements — body words | 1,093 | 905 | 985 | 899 | 830 | 855 |
| Requirements — meta_title chars | 54 | 49 | 53 | 46 | 43 | 46 |
| Requirements — meta_description chars | 158 | 157 | 153 | 158 | 156 | 158 |
| Requirements — FAQ items | 8 | 8 | 8 | 7 | 7 | 7 |

Targets: 900–1300 words en/ka/ru, 600–900 fa/he/ar; meta_title ≤ 65 incl. " | RentUp";
meta_description 140–158; 5–8 FAQ. Words counted on whitespace, tables included.

## Winter guide — the computed numbers (source: `content/attractions/*.yml`, 267 records)

| Figure published | Value | How computed |
|---|---|---|
| Places in season Dec–Mar | **161** | `best_season in {all, december-march}` = 159 + 2 |
| Places whose window excludes winter | **106** | 69 `may-october` + 36 `june-september` + 1 `april-october` |
| `open_year_round: false` | **52** | flag count; `true` = 215 |
| Of the 161 winter places: by category | 147 economy, 14 suv, 0 offroad | `car_category` |
| Of the 161: by road | 128 paved, 32 mostly_paved, 1 gravel, 0 `4x4_only` | `road` |
| Of the 52 closed: by category | 21 offroad, 26 suv, 5 economy | `car_category` |
| Of the 52 closed: `4x4_only` roads | 15 (of 17 nationwide) | `road` |
| Of the 52 closed: above 2,000 m | 16 | `elevation >= 2000` |
| Places above 2,000 m with a winter season | 2 of 20 (Gudauri, Jvari Pass) | `elevation >= 2000` ∧ season ∈ {all, december-march} |
| Routes with a year-round season | 14 of 49 | `content/routes/*.yml` `best_season in {all, year-round}` |
| Winter-only entries | Gudauri, Hatsvali–Tetnuldi | `best_season: december-march` |

Per-place rows in the tables (elevation, distance, drive time, road, car_category, best_season,
open_year_round) are copied verbatim from the attraction YAML: `abano-pass`, `goderdzi-pass`,
`jvari-pass-friendship-monument`, `gombori-pass`, `nakerala-pass`, `gudauri`, `bakuriani`,
`hatsvali-tetnuldi`, `mestia`, `ushguli`.

**Goderdzi Pass — note for the brief.** The task listed `goderdzi-pass` among the winter
resorts. The data says otherwise: `best_season: june-september`, `open_year_round: false`,
`road: gravel`, `car_category: offroad`, and the attraction page itself states the road closes
"from about November to May". The guide therefore lists Goderdzi under *passes that close*,
mentions that a small ski resort exists near the summit (from the attraction body), and says
explicitly that we do not treat it as a winter driving destination. Nothing was invented to
make it fit.

## Commercial figures used, with source file

| Figure | Value | Source |
|---|---|---|
| Winter tyres on every car | 1 December – 1 April, included | `faq.yml` ("What are the roads like in winter?"), `pricing.yml` ("What the price includes") — **not** in `terms.yml` |
| Snow chains | 20 ₾ per rental, Dec–Mar, free on 4x4 | `pricing.yml` extras table (also `posts/zamtris-…`) |
| Roof rack | 25 ₾/day, SUV and 4x4 only | `pricing.yml` extras table |
| Min age / licence years by category | 21/2 economy; 23/3 SUV & minivan; 25/5 business; 25/4 4x4; 25/3 van; no upper limit | `terms.yml` age table; `faq.yml` agrees at tier level; `rental_policy.yml` comment |
| Young-driver surcharge | 15 ₾/day ages 23–25 (SUV, minivan); 25 ₾/day ages 25–27 (business, 4x4) | `terms.yml`, `faq.yml`, `rental_policy.yml young_driver` (owner-confirmed 2026-08-30) |
| Additional driver | 20 ₾/day, max two, same requirements, must sign | `faq.yml`, `pricing.yml`, `rental_policy.yml extras_gel` |
| Unnamed driver not covered | — | `terms.yml` "insurance does not cover" |
| Documents | passport / ID; national licence; IDP if non-Latin; card for deposit; company extract + POA + stamp | `terms.yml` documents table |
| Licences valid as-is | EU, USA, UK, CIS (`terms.yml`) + Israel (`faq.yml`) | both cited; Israel appears only in `faq.yml` |
| Deposit by category | 300 / 600 / 800 van / 1,000 business & minivan / 1,200 4x4 | `pricing.yml` deposit table; `faq.yml` range 300–1,200; `rental_policy.yml` comment; `content/cars/*.yml` |
| Deposit handling | card hold not charge, released within 3 business days; cash taken and returned on the spot; no deposit-free option | `faq.yml`, `pricing.yml`, `rental_policy.yml deposit` (`waiver_available: false`) |
| Insurance included | CDW + TPL | `terms.yml`, `pricing.yml`, `rental_policy.yml insurance.included: tpl_cdw` |
| CDW excess by category | same table as deposit (300…1,200) | `pricing.yml` "Deposit and excess by category"; `faq.yml` (300 economy, 1,200 4x4) |
| SCDW | 25–45 ₾/day by category, lowers the excess; **300 ₾ excess remains on 4x4** | `faq.yml`, `pricing.yml` extras; residual 300 ₾ from `pricing.yml` table column "Excess with SCDW" |
| Not covered | DUI; unnamed driver; gravel/unpaved unless 4x4; tyres, wheels, underbody, interior (+ mirrors); key loss 400–1,200 ₾; misfuelling; commercial use | `terms.yml`; mirrors and tyre 120–400 ₾ from `faq.yml` |
| Tusheti / Abano extra excess | 500 ₾ + prior written agreement; June–October | `faq.yml` |
| Ushguli | 4x4 category only | `faq.yml` |
| Fuel | full to full; fuel + 20 ₾ service fee; hybrids petrol only | `terms.yml`, `rental_policy.yml fuel_policy` |
| Mileage | unlimited in Georgia; 300 km/day cross-border; 0.5 ₾/extra km | `faq.yml`, `terms.yml`, `rental_policy.yml mileage` |
| Cross-border | Armenia 150 ₾ / Turkey 250 ₾ selected categories, 300 km/day; Azerbaijan & Russia prohibited; ≥ 48 h notice; full deposit forfeited otherwise | `terms.yml` cross-border table; `rental_policy.yml cross_border.allowed: true` |
| Booking / payment | no prepayment; confirmed by phone or email; pay at pickup; GEL, cash USD/EUR at NBG rate; Visa/Mastercard/Amex | `terms.yml`, `faq.yml`, `pricing.yml` "Payment methods"; `rental_policy.yml prepayment_required: false` |
| Cancellation | free > 48 h; 1 day's rate 24–48 h; 2 days' rate < 24 h / no-show; date change free if available; early return recalculated | `terms.yml`; `rental_policy.yml cancellation` |
| Late return | ≤ 2 h free; then ⅓ daily rate per 3 h; > 8 h = full day | `faq.yml`, `terms.yml` penalties table |
| Roadside assistance | 24/7; replacement within 6 h for a technical fault not caused by the renter; 112 | `faq.yml`, `pricing.yml`; `rental_policy.yml support` (owner-confirmed 24/7) |
| Traffic fines | renter pays; can arrive within 30 days; fine + 20 ₾ | `faq.yml`, `terms.yml` |
| Handover photos | four sides, interior, odometer, fuel | `faq.yml` |
| Seasonal coefficient | +10% New Year and Easter weeks | `faq.yml` |
| Child seat | 10 ₾/day; required under 12 | `faq.yml`, `pricing.yml` |
| Contract languages | Georgian, English, Russian | `terms.yml` |
| Gudauri section closes periodically for avalanche risk; Tbilisi–Batumi and Tbilisi–Kazbegi open all year | — | `faq.yml` |
| December sunset in Tbilisi ≈ 17:20 | — | `posts/zamtris-mgzavroba-saqartveloshi.yml` (physical fact, not a commercial term) |

Where `FACT_RECONCILIATION.md` records a reconciled value, the guides follow it: CDW included
(not an add-on), per-category excess (not a flat 1,000), cross-border permitted with fees,
48-hour cancellation tiers, 20 ₾ additional driver, no prepayment (the published pages now agree
on pay-at-pickup; `rental_policy.yml prepayment_required: false`).

## Deliberately left out (no source states it)

- **Extension tariff.** No page in `terms.yml`/`faq.yml`/`pricing.yml`/`rental_policy.yml`
  publishes an extension rate. The guide says so and advises phoning before the return time,
  then states the *published* late-return rule. No number was invented.
- **A "zero excess" claim.** Never used. SCDW is described as *lowering* the excess, with the
  300 ₾ residual on the 4x4 stated wherever SCDW appears.
- **"Full insurance".** Never used. Every mention of insurance states the excess.
- **Maximum rental length, WiFi router, Kazbegi/Sarpi border handover fees** — not needed here
  and/or unresolved in `FACT_RECONCILIATION.md`.

## Discrepancies noticed while writing (for the owner / next pass)

1. **SCDW residual excess on the 4x4.** `pricing.yml`'s "Deposit and excess by category"
   table gives *Excess with SCDW* = 300 ₾ for the off-road 4x4 (0 ₾ elsewhere), while
   `faq.yml` and `terms.yml` say SCDW "reduces the excess to zero" without exception, and the
   `rental_policy.yml` comment says "SCDW brings the excess to 0 GEL on every category". The
   guides follow the itemised `pricing.yml` table (the more specific source) and never say
   "zero". One of the two needs correcting.
2. **Winter-tyre rule location.** The brief said the 1 Dec – 1 Apr rule "is in
   `terms.yml`/`faq.yml`". It is in `faq.yml` and `pricing.yml`; `terms.yml` does not mention
   winter tyres at all. Worth adding a line to `terms.yml` so the contract page carries it.
3. **Israel** is listed among licences valid as-is in `faq.yml` but not in `terms.yml`'s IDP
   note (EU, USA, UK, CIS). The guides cite both; `terms.yml` should probably add Israel.
4. **Mirrors** appear in `faq.yml`'s not-covered list but not in `terms.yml`'s. Guides include
   them (the stricter reading).
5. **`hatsvali-tetnuldi`** is the only `best_season: december-march` record that is also
   `open_year_round: false`. Consistent with a short ski season and a partly rough approach,
   and the guide says so — but it is the one place where "winter destination" and "not
   year-round" coexist, so it may confuse a future counting pass.
6. **Goderdzi Pass** is not a winter destination in the data (see above).
