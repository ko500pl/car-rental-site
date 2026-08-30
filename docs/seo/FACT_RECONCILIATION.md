# Rental policy fact reconciliation — 2026-08-30

## Why this exists

The site was stating three or four different versions of its own rental policy at once:
`content/settings/rental_policy.yml` (an assistant's proposed draft, explicitly labelled as
such and never actually wired into `build.py`), the pre-existing published pages
`content/pages/terms.yml` / `faq.yml` / `pricing.yml`, and `content/settings/meta.yml`'s
`llms_facts` (what `dist/llms.txt` tells AI assistants). An AI assistant, a search engine and
a customer reading different pages would get different answers to the same question.

**Authority ranking used below:** `terms.yml`, `faq.yml` and `pricing.yml` are pre-existing,
already-published business content. `rental_policy.yml` is explicitly headed "PROPOSED
DEFAULTS drafted for the owner's approval (2026-08-29)" — an assistant's draft, not the
business's. Where the three published pages agree with each other, that agreement is treated
as the real policy and `rental_policy.yml` was corrected to match. Where the published pages
disagree **with each other**, no side was picked — see "Owner decisions" at the end.

**Important structural finding:** `RENTAL_POLICY = load_opt("content/settings/rental_policy.yml")`
(`build.py:84`) is loaded into a module-level variable and then **never read anywhere else in
build.py** — grepped for every key name (`min_driver_age`, `insurance`, `cross_border`, etc.)
with zero hits outside that one assignment. The file currently drives no rendered page. Its
`note_key` values (`mileage_unlimited`, `no_cross_border`, `one_way_between_served_cities`) also
don't exist in `ui.yml` or `travel.yml`. Reconciling it is still worthwhile per this task's
brief — presumably it's meant to be wired in — but as shipped today it is inert scaffolding,
not something a customer or AI assistant can currently read from the live site.

---

## Conflict matrix

Values are English-section unless noted; numeric/date facts were spot-checked across all 6
languages (ka/en/ru/fa/he/ar) for the highest-risk rows (night surcharge, additional driver,
cross-border fee) and found consistent language-to-language.

| Term | rental_policy.yml (before) | terms.yml | faq.yml | pricing.yml | meta.yml llms_facts (en) | site.yml/contact.yml | Verdict |
|---|---|---|---|---|---|---|---|
| Min. driver age | `min_driver_age: 21` (flat) — line 11 | Tiered table: economy 21y, crossover/minivan 23y, business/4x4 25y — lines 270–307 | "Economy class from 21... Crossovers and minivans from 23. Business class and 4x4 from 25." — lines 211–214 | (not stated) | Already correct: "21 for economy, 23 for SUV/minivan, 25 for business class and 4x4" — line 87 | — | terms+faq+meta agree on tiers. Kept flat field at 21 (the floor) with a comment; schema can't hold tiers. |
| Min. licence experience | `min_licence_years: 2` (flat) — line 12 | Tiered: economy 2y, crossover/minivan/van 3y, 4x4 4y, business 5y — lines 270–307 | "held for at least 2 years" — line 205 | — | — | — | Agrees at the floor (2y, economy). Kept flat at 2, commented. |
| Young driver surcharge | *(no field)* | 15 ₾/day ages 23–25 (crossover/SUV/minivan); 25 ₾/day ages 25–27 (business/4x4) — lines 287–297 | "15–25 GEL per day" for drivers under 27 — line 214 | — | *(missing, now added)* | — | terms+faq agree. No field existed in rental_policy.yml; added a comment flagging the gap (owner ask below) and added a fact to `llms_facts`. |
| Mileage | `unlimited: true` | — | "Within Georgia, no — mileage is unlimited. ... cross-border ... 300 km" — lines 257–260 | "Unlimited mileage within Georgia" — line 425 | "Unlimited within Georgia; 300 km/day limit on cross-border" — line 89 | — | Consistent everywhere. No change. |
| Fuel policy | `same_to_same` — line 33 | **"full to full"** principle, +20 ₾ service fee if not full — lines 314–317 | — | (penalty table implies full-to-full: "Tank not returned full" charge) — line 533 | Already correct: "Full to full" — line 91 | — | terms.yml + meta.yml already agreed on full-to-full; rental_policy.yml alone said same-to-same. **Corrected to `full_to_full`.** |
| Deposit handling | `card_hold`, cash accepted, 3-day release, no waiver | — | "blocked on the card... released within 3 business days" — lines 225–226 | "blocked on a credit or debit card... released within 3 business days... cash returned on the spot" — lines 538–541 | "blocked on card and released within 3 business days" — line 95 | — | Consistent. No change. |
| Deposit amount by category | *(delegated to content/cars/*.yml)* | — | "From 300 GEL (economy) up to 1,200 GEL (4x4)" — line 225 | Full table: economy 300, SUV 600, business/minivan 1,000, 4x4 1,200, van 800 — lines 542–580 | "300–1,200 GEL depending on category" — line 95 | — | `content/cars/*.yml` deposit fields match the pricing.yml table exactly (checked all 17 cars). No conflict, no change. |
| Airport delivery fee — Tbilisi | `30` ₾ — line 41 | — | "For shorter rentals the charge is 40–60 GEL" (range) — line 272 | 1–2 days: **40** ₾, free from 3 days — lines 502–505 | — | — | pricing.yml is the only itemized source. **Corrected to 40.** |
| Airport delivery fee — Kutaisi | `60` ₾ — line 42 | — | (range 40–60) | 1–4 days: **60** ₾, free from 5 days — lines 507–510 | — | — | Already matched. No change. |
| Airport delivery fee — Batumi | `60` ₾ — line 43 | — | (range 40–60) | 1–4 days: **50** ₾, free from 5 days — lines 511–515 | — | — | **Corrected to 50.** |
| City-centre delivery — Kutaisi/Batumi | `50` ₾ each — lines 45–46 | — | — | "Batumi/Kutaisi, city centre": **40** ₾ (1–4 days), free 5+ — lines 516–520 | — | — | **Corrected to 40 for both.** |
| Night handover/return surcharge | `20` ₾, window 22:00–**08:00** — lines 47–49 | — | "Between 22:00 and 07:00 an extra **40 GEL**" — line 274 (confirmed identical wording in ka/ru/fa/he/ar) | "**Night handover and return** (22:00–**07:00**) — an extra **40** ₾" — line 533 | — | — | faq.yml + pricing.yml agree with each other, disagree with rental_policy.yml on both the amount and the window end. **Corrected to 40 ₾, 22:00–07:00.** |
| One-way fee | `100` ₾ between served cities | — | "start at 100 GEL" (Tbilisi↔Kutaisi↔Batumi) — line 276 | "from 100 ₾" — line 470 | — | — | Consistent. No change. |
| Min. rental length | `1` day | — | — | — | — | index.yml: "Minimum rental period: 1 day" (not one of the 4 named sources, but corroborating and uncontradicted) | Consistent. No change. |
| Max. rental length | `90` days — line 59 | *(not stated)* | *(not stated)* | Monthly rate table is open-ended past "30+ days"; ">3 months" is a **corporate-pricing trigger** (also needs 3+ vehicles), not a stated cap — lines 328, 585 | — | — | No source states a maximum. **Removed** the field rather than keep an unsourced number — see owner ask. |
| Insurance included in base rate | `tpl` only; CDW framed as a paid add-on — lines 63–64 | **"The price includes CDW... and TPL"** — line 326 | — | "What the price includes": CDW insurance coverage + TPL — lines 423–424 | Already correct: "CDW and TPL included" — line 93 | — | terms.yml + pricing.yml + meta.yml's own llms_facts all agree CDW is included, not optional. rental_policy.yml alone said otherwise. **Corrected `included` to `tpl_cdw`.** |
| Zero-excess add-on (SCDW) price | `cdw_daily_gel: 25` (flat, framed as "CDW as add-on") — line 65 | "Adding SCDW reduces the excess to zero" (no price stated) — line 328 | "SCDW (25–45 GEL per day) reduces the excess to zero" — line 230 | "Full excess waiver (SCDW): 25–45 ₾/day, depending on category" — line 462 | "SCDW zero-excess option for 25–45 GEL/day" — line 93 | — | It's a **range** (25–45 by category), not a flat 25. Kept 25 as the stored low end with an explicit comment that it's a range; relabelled as SCDW, not CDW, pricing. |
| Excess amount | `excess_gel: 1000`, labelled "standard excess without CDW" — line 66 | — | "The excess is 300 GEL on economy class and 1,200 GEL on a 4x4" — line 229 | Table by category: economy 300, SUV 600, business/minivan 1,000, 4x4 1,200, van 800 — lines 550–580 | *(not previously stated; now added)* | — | faq.yml + pricing.yml agree on a per-category table; 300/1,000/1,200 are all real, for different categories — none of them is "the" excess. **Corrected the flat field to 300 (economy headline)** with the full table in a comment, and added the range to `llms_facts`. |
| Cross-border travel | `allowed: false` — line 71 | Armenia **permitted** (150 ₾, 300 km/day), Turkey **permitted**, selected categories (250 ₾, 300 km/day); Azerbaijan/Russia prohibited; 48h advance arrangement required — lines 342–374 | — | "Cross-border travel (Armenia): 150 ₾, includes international insurance" — line 473 | Already correct: "Armenia (150 GEL) and Turkey (250 GEL) allowed with permit; Azerbaijan and Russia prohibited" — line 97 | — | terms.yml + pricing.yml + meta.yml's own llms_facts all agree travel is permitted (to specific countries, with a fee). rental_policy.yml alone flatly denied it. **Corrected to `allowed: true`**, `note_key` renamed from `no_cross_border` to `cross_border_limited` (still doesn't resolve to real copy — see report). |
| Cancellation window | `free_until_hours: 24`, `no_show_charge_days: 1` — lines 76–77 | Three tiers: free >48h ahead; **1 day's rate** 24–48h ahead; **2 days' rate** <24h ahead or no-show — lines 376–385 | — | — | *(not previously stated; now added)* | — | terms.yml is the only detailed source (uncontradicted). **Corrected to `free_until_hours: 48`, `no_show_charge_days: 2`**; the 24–48h middle tier has no field in this schema — flagged in a comment, not invented into a new key. |
| Prepayment required to confirm | `prepayment_required: false` ("pay at pickup") — line 78 | "Booking requests are confirmed after availability is checked **and the required payment is completed**" — line 379 | "Submit the booking request on the website. ... the booking is confirmed after the required payment." — lines 183–186 | "Submit the booking request online; confirmation follows the required payment." — line 601 | "Booking requests are submitted online and require payment before confirmation" — line 99 (before this pass) | **contact.yml**: "Bookings are made by phone or email — **the site has no online form or payment system.**" — line 90 | **Genuine conflict between pre-existing pages** (contact.yml vs. terms+faq+pricing+meta). Not resolved — left at `false`, `# CONFLICT:` comment added, listed as an owner decision below. `llms_facts`'s "Booking" line was softened to avoid asserting either disputed claim. |
| Additional driver fee | `extras_gel.additional_driver: 10` — line 83 | — | "Yes, for **20 GEL** per day, up to two additional drivers" — line 217 | "Additional driver: **20** ₾/day, maximum of 2" — lines 440–443 | — | — | faq.yml + pricing.yml agree at 20. **Corrected to 20.** |
| Child seat fee | `extras_gel.child_seat: 10` | — | "at 10 GEL per day" — line 304 | "Child seat: 10 ₾/day" — lines 444–447 | — | — | Consistent. No change. |
| GPS | `extras_gel.gps: 0`, commented "not offered separately — phones do it" — line 84 | — | — | "GPS navigator: **15 ₾/day**, with offline maps" — lines 448–451 | — | — | pricing.yml lists it as a real, priced extra. rental_policy.yml's "not offered" claim was simply wrong. **Corrected to 15.** |
| WiFi router | `extras_gel.wifi_router: 15` — line 85 | *(not mentioned)* | *(not mentioned)* | *(not mentioned)* | *(not mentioned)* | *(not mentioned)* | **No source anywhere states this.** Removed rather than guessed — see owner ask. |
| Roadside assistance | `support.roadside_assistance: true`, `hours_key: office_hours` — lines 89–90 | — | "roadside assistance operates 24/7... replacement car within 6 hours" — lines 306–309 | "24/7 roadside assistance nationwide" (included in price) — line 427 | — | site.yml `opens`/`closes`: 09:00–21:00 | faq.yml + pricing.yml agree assistance is **24/7**, not tied to office hours. `hours_key: office_hours` looks wrong, but no "24/7" copy key exists to repoint it at. Flagged in a comment; not silently fixed since no correct key exists yet. |
| Contract languages | `support.languages: [ka, en, ru]` | "drawn up in Georgian, English or Russian" — line 230 | — | — | — | — | Consistent. No change. |
| Booking channel | *(no field)* | "Booking requests are confirmed..." (implies online submission) | "Submit the booking request **on the website**" | "Submit the booking request **online**" | "submitted online" (before this pass) | contact.yml: "no online form... phone or email" | Same conflict as prepayment, different angle — see owner decision below. |
| Seasonal surcharge | *(no field)* | — | "+15% in July/August... +10% Easter/New Year" — lines 195–198 | "seasonal adjustment applies in July and August (+15%)" — line 316 | — | — | faq.yml states more (Easter/New Year) than pricing.yml, but pricing.yml doesn't contradict it (silence, not disagreement). Not added to rental_policy.yml — out of scope of the "structure unchanged" instruction; noted here only. |
| Long-term / corporate discount | *(no field)* | — | "7 days... 10%... 30 days... 25%... corporate >3 months... 40%" — lines 179–182 | "25–40% off the base rate, depending on volume" (corporate, >3 months + 3+ vehicles) — lines 588–589 | — | — | Compatible ranges, not contradictory. Not added — out of scope. |
| Delivery to other cities / border crossings | *(no field)* | — | — | "Other cities (Telavi, Gori, Zugdidi): 80/80/50 ₾"; "Border crossing (Sarpi, Kazbegi): from 120 ₾" — lines 521–530 | — | — | Real, published, but rental_policy.yml has no place-key fields for them. Not added — out of scope; noted here as a gap. |
| "Full insurance coverage" claim | *(n/a — separate file)* | — | — | — | **meta.yml org_desc, all 6 languages**, said "full insurance coverage" / equivalents | index.yml hero (en/he/ar confirmed, likely ka/ru/fa too) says the same; index.yml's *own body* elsewhere correctly says "CDW insurance included... 300–1,200 GEL excess by class" | Directly contradicts the reconciled insurance model (TPL + CDW included, SCDW optional, real excess). **Fixed in `meta.yml` (all 6 languages)** — see below. `content/pages/index.yml` has the identical problem in its hero line but is off-limits to this pass; flagged for the page owner. |

---

## What changed

### `content/settings/rental_policy.yml`
Corrected in place (structure and key names unchanged, per instructions): `fuel_policy`,
`delivery.airport_fee_gel.*`, `delivery.city_fee_gel.*`, `delivery.night_surcharge_gel`,
`delivery.night_to`, `insurance.included`, `insurance.excess_gel`, `cross_border.allowed`,
`cross_border.note_key`, `cancellation.free_until_hours`, `cancellation.no_show_charge_days`,
`extras_gel.additional_driver`, `extras_gel.gps`. Removed as unsourced: `max_rental_days`,
`extras_gel.wifi_router`. Left unresolved with an inline `# CONFLICT:` comment:
`cancellation.prepayment_required`. The file header was rewritten from "PROPOSED DEFAULTS" to
"RECONCILED 2026-08-30" with a pointer to this document, and every changed/flagged line carries
an inline comment citing its source.

### `content/settings/meta.yml`
- `org_desc` corrected in all 6 languages: "full insurance coverage" (and equivalents) replaced
  with "CDW and TPL insurance included" (and equivalents) — same sentence length and tone, one
  clause swapped.
- `en.llms_facts` rewritten: `Insurance` now states the real excess range and that SCDW is an
  *optional* add-on (not the only option); added `Young driver surcharge` and `Cancellation`
  facts (previously entirely missing, now sourced from terms.yml/faq.yml consensus);
  `Cross-border` note tightened to mention the 48h advance-arrangement requirement; `Booking`
  reworded to state only the undisputed fact (RentUp confirms after checking availability) and
  drop the disputed claim that a website form and prepayment are required — see the
  `prepayment_required` conflict above. `ka/ru/fa/he/ar.llms_facts` were left as empty lists,
  matching their prior state — `build.py`'s `llms_txt()` reads only `META["en"]`, so the other
  languages' arrays are unused.

### `content/settings/seo_trust.yml`
Fixed the header comment (lines ~25–30) that said `seo_meta.yml records a planned rebrand to
"RentUp"` — self-contradictory, since the brand it's rebranding *to* is the same name it's
rebranding *from*. Checked `seo_meta.yml`: it contains no rebrand language at all, just
`brand: RentUp` used consistently. The comment was residue of an earlier find-and-replace that
overwrote the old brand name wherever it appeared, including inside this explanatory note.
Rewritten to state accurately that both settings files agree on "RentUp" and there is no
pending rebrand.

### `dist/llms.txt` — reported, not fixed
Line 25 (`## Pages`, the Map & planner entry) ships an unsubstituted `{attractions}` template
placeholder instead of a number: *"Interactive map: {attractions} attractions across 11
regions..."*. This is a `build.py` bug (a `.replace("{attractions}", ...)` call exists at
`build.py:1935` but evidently isn't reached for this string) and per the task instructions was
left alone for the process already fixing `build.py`.

### Not changed (out of scope, flagged for the page owner)
`content/pages/index.yml` repeats the same false "full insurance coverage" claim in its hero
(confirmed in en/he/ar; likely also ka/ru/fa) while its own body text elsewhere on the same page
already correctly states the CDW/excess model. `content/settings/site.yml` uses
`usd_rate: 2.6` while `content/pages/pricing.yml`'s USD table is built on "1 USD = 2.70 ₾" —
a real numeric mismatch, but `site.yml` is not in this pass's editable file list.

### Validation
`python3 build.py --validate-only` → `✔ content validation passed` (one pre-existing, unrelated
warning: `cars: 17 published records have no main image`).

---

## Decisions the owner must make

1. **Is prepayment required to confirm a booking, or is payment collected at pickup?**
   `contact.yml` says the site has no online form or payment system and booking is by phone or
   email only. `terms.yml`, `faq.yml` and `pricing.yml` all say the opposite: a request is
   submitted on the website and the booking is confirmed only once the required payment is
   completed. `rental_policy.yml` currently says "pay at pickup" (no prepayment). Pick one and
   the other pages need correcting to match.

2. **Does RentUp actually offer a WiFi router as a paid extra?** It appeared only in
   `rental_policy.yml` (15 GEL/day) and nowhere else — not in `pricing.yml`'s extras table, not
   in `faq.yml`. It has been removed rather than guessed. If it's real, say the price and it can
   be restored.

3. **Is there an actual maximum rental length for a single (non-corporate) booking?**
   `rental_policy.yml` said 90 days with no source. `pricing.yml`'s monthly rate table doesn't
   cap at any day count, and its "over 3 months" threshold is a *corporate-pricing* trigger
   (also requires 3+ vehicles), not a stated single-rental cap. Removed rather than guessed —
   if there is a real cap, what is it?

4. **`support.hours_key: office_hours` looks wrong for 24/7 roadside assistance** — both
   `faq.yml` and `pricing.yml` say assistance runs 24/7, not 09:00–21:00. There's currently no
   "24/7" copy key to point this at instead. Should one be added, or is roadside assistance
   actually limited to office hours (in which case faq.yml/pricing.yml need correcting)?

5. **`content/pages/index.yml`'s hero still says "full insurance coverage"** — the same
   inaccurate claim just fixed in `meta.yml`, and it contradicts the correct CDW/excess
   explanation already written elsewhere on that same page. It's a `content/pages/*` file, out
   of scope for this pass — should whoever owns page content correct it to match?

6. **`site.yml`'s `usd_rate: 2.6` doesn't match `pricing.yml`'s stated conversion rate of 1
   USD = 2.70 ₾.** Which rate is current? (Also out of scope for this pass — `site.yml` isn't
   in the editable file list.)

7. **The young-driver surcharge (15–25 GEL/day by category and age band, per `terms.yml` and
   `faq.yml`) has no field in `rental_policy.yml`'s schema.** Should a field be added once this
   file is wired into `build.py`, and if so, as a flat number or a small table by category?

8. **`dist/llms.txt` contains a literal, unsubstituted `{attractions}` placeholder** on its Map
   & planner line — a `build.py` templating bug, reported here per instructions and left for
   the process already working on `build.py`.
