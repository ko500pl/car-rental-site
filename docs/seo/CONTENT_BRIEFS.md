# RentUp.ge — Content Briefs (Batch 1: 10 pages)

**Compiled:** 2026-08-30 · **Companion to:** `KEYWORD_CLUSTERS.md` (query space + ranked build list),
`SEO_URL_MAP.md` (which URLs may exist), `CONTENT_STRATEGY.md` (why, in what order),
`ONPAGE_REVIEW.md` (what is broken in the templates today).

This file gives ten full, writer-ready briefs. Every factual claim in every brief traces to a named
file and field in `content/`. Where the repo does not hold a fact, it is called out in a
**"Facts the owner must supply"** box rather than invented. Where a brief touches a commercial term
that is currently disputed between `rental_policy.yml`, `content/pages/faq.yml`, `content/pages/terms.yml`
and/or `dist/llms.txt`, it carries an explicit **"Verify against the reconciled policy before
publishing"** note instead of a hard-coded number — see §0.3.

---

## 0. How this batch was chosen, and what it assumes

### 0.1 The ten pages

| # | URL | Cluster | Status |
|---|---|---|---|
| 1 | `/guides/do-i-need-a-4x4-in-georgia/` | B10 | **NEW** — flagship decision guide (assigned) |
| 2 | `/car-rental/` | A1 | **REWRITE** — hub (assigned) |
| 3 | `/car-rental/tbilisi-airport/` | A3 | **REWRITE** — thin page, ~2,064 chars measured (assigned) |
| 4 | `/car-rental/monthly/` | A20 | **NEW** (assigned) |
| 5 | `/itineraries/georgia-7-days/` | — | **REWRITE** (assigned) |
| 6 | `/car-rental/deposit/` | A16 | **NEW** — ranked-list #6 |
| 7 | `/car-rental/business/` | A12 | **NEW** — ranked-list #7 |
| 8 | `/car-rental/one-way/` | A21 | **NEW** — ranked-list #8 |
| 9 | `/car-rental/with-driver/` | A23 | **NEW** — ranked-list #11 |
| 10 | `/car-rental/requirements/` | A18 | **NEW** — ranked-list #13 |

### 0.2 Why #6–10 are not simply "the next five rows" of the ranked list

The task brief for this batch asks for content **weighted toward commercial and decision-stage
intent**. `KEYWORD_CLUSTERS.md §6`'s literal next five rows after #1 (4x4) and #2 (monthly) are
#3 Svaneti route rewrite, #4 Tusheti/Abano promotion, #5 mountain-passes guide — all Intent‑B
(travel/discovery) pages. Rows #1 and (assigned) `/itineraries/georgia-7-days/` already give this
batch two travel/bridge pages. To meet the stated weighting, this batch instead takes the five
**highest-ranked Intent‑A (rent-a-car) rows** from the list — #6 deposit, #7 business, #8 one-way,
#11 with-driver, #13 requirements — all inside the top half of the 20-row list, all transactional or
qualifying/MOFU, none requiring new data collection. Rows #3–5, #9–10, #12, #14–20 remain queued and
unbriefed; #18 (insurance) is correctly **not** briefed here — it is blocked on the same source-data
conflict described in §0.3 and should not be built until that is resolved.

### 0.3 The one thing every commercial brief in this file depends on

`content/settings/rental_policy.yml` carries the header `STATUS: PROPOSED DEFAULTS drafted for the
owner's approval (2026-08-29)`, and it disagrees with `content/pages/faq.yml`, `content/pages/terms.yml`
and `dist/llms.txt` on at least five material points (verified directly in this file's research, in
addition to the three — I1–I3 — already logged in `CONTENT_STRATEGY.md §1.5`):

| Term | `rental_policy.yml` says | `faq.yml` / `terms.yml` say | Live booking config (`FH_CFG` in every page's `<script>`) |
|---|---|---|---|
| CDW | add-on, 25 ₾/day, **not** included in the rate | "the rate ... includes VAT, CDW insurance" | — |
| Excess | flat **1,000 ₾** | tiered **300–1,200 ₾** by category; SCDW buys it to zero | — |
| Cross-border | **prohibited** (`allowed: false`) | allowed with 48h notice, extra 500 ₾ excess, 300 km/day cap | — |
| Minimum age | flat **21**, no young-driver surcharge mentioned | tiered surcharge for ages 23–25 (15 ₾/day) and 25–27 (25 ₾/day) | `youngDriver: {underAge:27, minGel:15, maxGel:25}` — **matches `terms.yml`, not `rental_policy.yml`**, and is the value the booking form actually charges |
| Deposit method | `card_hold \| cash \| either`, `cash_accepted: true` | "A passport or ID card, a driving licence... **and a card for the deposit**" (no cash mention) | — |
| Long-term discount | not stated | "10% from 7 days, 25% from 30 days, up to 40% on corporate contracts over 3 months" | — |

The 10%/25% tiers are independently **confirmed** by this brief's own arithmetic on all 17 cars'
`price_1_6` / `price_7_29` / `price_30` (9.3–10.3% and 24.4–25.3% — see brief #4). The **40% corporate
figure has no supporting field anywhere in `content/` and is sourced only from `faq.yml` prose** —
treat it as unverified.

**Rule applied throughout this file:** deposit amounts, delivery fees, the one-way fee and the
unlimited-mileage-within-Georgia claim are stated as hard numbers because they are undisputed across
every source. CDW inclusion, the excess amount, cross-border, the age/young-driver surcharge, the
deposit **method**, and the 40% corporate discount are never hard-coded into instructed copy in this
file — each brief that touches one names the conflict and inserts **"Verify against the reconciled
policy before publishing"** at the exact sentence it affects.

### 0.4 A URL-authority conflict this batch inherits (flag, don't fix)

`KEYWORD_CLUSTERS.md §6` places the 4x4 decision guide at `/guides/do-i-need-a-4x4-in-georgia/` (and
sibling guides at `/guides/monthly-passes-and-road-conditions/`, `/guides/driving-in-georgia/`,
`/guides/winter-driving-georgia/`). `CONTENT_STRATEGY.md §3–4` places the same content under a
`/driving-in-georgia/` pillar (`/driving-in-georgia/choosing-a-car/`, `/driving-in-georgia/mountain-passes/`,
etc.). `SEO_URL_MAP.md` — the document with authority over which URLs may exist — lists **neither**
`/guides/` nor `/driving-in-georgia/`. This brief uses `/guides/do-i-need-a-4x4-in-georgia/` because
that is the URL this task explicitly assigned, but **`SEO_URL_MAP.md` needs a decision and an entry
for one prefix before this page ships**, or the second guide built under the other prefix creates two
competing information architectures. Not a content problem — a URL-map gap.

---

# Brief 1 — `/guides/do-i-need-a-4x4-in-georgia/` (flagship decision guide)

## The real split, counted directly from the repo

Counted from all 257 files in `content/attractions/*.yml` on 2026-08-30 (script: grep every `road:`
and `car_category:` line; matches the figures already stated in `CONTENT_STRATEGY.md §1.3` and
`KEYWORD_CLUSTERS.md §A10` exactly — independent confirmation, not a re-quote):

| `road` | Count | % of 257 |
|---|---|---|
| paved | 149 | 58.0% |
| mostly_paved | 71 | 27.6% |
| gravel | 20 | 7.8% |
| 4x4_only | 17 | 6.6% |
| **Needs gravel-or-better clearance or worse (gravel + 4x4_only)** | **37** | **14.4%** |

| `car_category` | Count | % of 257 |
|---|---|---|
| economy | 175 | 68.1% |
| suv | 59 | 23.0% |
| offroad | 23 | 8.9% |

**The honest headline the data supports: for 85.6% of Georgia's mapped attractions, you do not need a
4x4 — and for 68.1% you don't even need an SUV.** The 4x4 question only becomes real for a specific,
nameable 8.9% of places. This is the opposite of the marketing pitch every competitor's "you'll need a
4x4 in Georgia" blog post makes, and it is more credible for being more modest.

Cross-tabulated `road × car_category` (all 8 combinations that actually occur; the other four
combinations — e.g. `4x4_only`+`economy` — occur zero times, which is itself a useful sanity check on
data integrity):

| road | car_category | Count |
|---|---|---|
| paved | economy | 145 |
| paved | suv | 4 |
| mostly_paved | economy | 30 |
| mostly_paved | suv | 41 |
| gravel | suv | 14 |
| gravel | offroad | 6 |
| 4x4_only | offroad | 17 |

Read this table as the actual product logic: **every `4x4_only` place is tagged `offroad`, with no
exceptions** — the category tag is a hard consequence of the road tag, not an independent editorial
call. That consistency is itself a trust signal worth stating on the page ("we didn't hand-pick these
— category follows road surface mechanically across all 257 places").

Regional concentration of the 37 gravel/4x4_only places (10 of 11 regions have at least one; the 11th,
Tbilisi, has none — worth stating plainly):

| Region | gravel | 4x4_only | Total |
|---|---|---|---|
| samegrelo-zemo-svaneti | 4 | 4 | 8 |
| kakheti | 1 | 6 | 7 |
| mtskheta-mtianeti | 3 | 3 | 6 |
| adjara | 3 | 2 | 5 |
| kvemo-kartli | 3 | 0 | 3 |
| guria | 2 | 0 | 2 |
| racha-lechkhumi | 1 | 1 | 2 |
| shida-kartli | 1 | 1 | 2 |
| imereti | 1 | 0 | 1 |
| samtskhe-javakheti | 1 | 0 | 1 |

Fleet clearance, from `content/cars/*.yml` (`clearance` field, mm), joined against the road classes it
can plausibly serve:

| Category | Cars | Clearance range | Drive |
|---|---|---|---|
| economy | Prius 145, Elantra 140, Corolla 135 | 135–145 mm | fwd |
| suv | RAV4 195, Tucson 181, Outlander 190 | 181–195 mm | awd/4wd |
| offroad | Pajero 235, Delica 210, Prado 220 | 210–235 mm | 4wd (Prado adds low range + diff lock, per `KEYWORD_CLUSTERS.md A10`) |
| business | Camry 145, E-Class 130, BMW 5 135 | 130–145 mm | rwd/fwd |
| minivan | Vito 165, Alphard 160, Staria 186 | 160–186 mm | fwd/awd |
| van | Transit 170, Sprinter 175 | 170–175 mm | fwd/rwd |

Three worked, named examples (all fields verified directly in their `content/attractions/*.yml`
files):

| Place | road | car_category | Elevation | Distance / drive from Tbilisi | Season | Entry |
|---|---|---|---|---|---|---|
| Mestia (`mestia.yml`) | paved | suv | 1,500 m | 470 km / 8:30 | may–october | free |
| Ushguli (`ushguli.yml`) | gravel | offroad | 2,100 m | 515 km / 10:30 | june–september | ~5 ₾ |
| Abano Pass (`abano-pass.yml`) | 4x4_only | offroad | 2,850 m | 180 km / 5:00 | june–september | free |
| Omalo / Tusheti (`omalo-tusheti.yml`) | 4x4_only | offroad | 1,880 m | 220 km / 6:30 | june–september | free |
| Gergeti Trinity Church (`gergeti-trinity-church.yml`) | mostly_paved | suv | 2,170 m | 160 km / 3:10 | may–october | free |

This lets the page make its single sharpest point with real names: **"Mestia itself is a paved-road
SUV trip. It is the next 47 km — Mestia to Ushguli — that turns into `gravel`/`offroad`."** Same shape
for the Georgian Military Highway: Stepantsminda/Gergeti is `mostly_paved`/`suv`; it is the
side-trip up to Gergeti's higher trailheads and the Juta/Truso valleys (see routes, brief covers this
in the Kazbegi route separately, not built in this batch) that flips to 4x4-only.

## Brief

- **Target URL:** `/guides/do-i-need-a-4x4-in-georgia/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary keyword (en):** `do I need a 4x4 in Georgia`
- **Secondary (en):** `is a 4x4 necessary in georgia`, `4x4 or normal car georgia`, `is svaneti accessible by regular car`, `can you drive to tusheti without a 4x4`, `georgia roads 4x4 required`, `off road car needed georgia mountains`
- **Primary (ka):** `ჯიპი მჭირდება საქართველოში?` — **secondary:** `უნდა ავიღო თუ არა ჯიპი`, `ჯიპის ქირაობა თუშეთისთვის`, `მანქანით სვანეთში მოგზაურობა`, `4x4 საჭიროა საქართველოში`
- **Primary (ru):** `нужен ли внедорожник в Грузии` — **secondary:** `можно ли доехать до Сванетии на обычной машине`, `нужен ли 4x4 в горах Грузии`, `дорога до Ушгули без джипа`, `аренда авто для Тушетии`
- **Intent / funnel stage:** Qualifying / MOFU — "the bridge" per `CONTENT_STRATEGY.md §2.2`. Reader has already picked a destination (from an attraction page, a blog, a friend) and is deciding what to book, not whether to travel.
- **Audience & real question:** An international traveller (secondarily a Russian-speaking self-drive tourist) who has read that "you need a 4x4 for Georgia" somewhere general and wants to know if that's true **for their actual itinerary** — a much narrower, answerable question than the generic one.
- **Target word count:** 1,600–2,000 words (en/ka/ru — this is a Pillar-2 bridge page per `CONTENT_STRATEGY.md §6.2`, a template-driven exception that can carry moderate original prose because it is the site's single highest-priority page).

### Outline

- **H1:** Do You Need a 4x4 to Drive in Georgia? (ka: `გჭირდებათ თუ არა 4x4 საქართველოში მოსამგზავროდ?` / ru: `Нужен ли внедорожник, чтобы путешествовать по Грузии?`)
- **H2 — The short answer, from our own data** — lead with "85.6% of the 257 places we track need nothing more than a normal car" before any nuance. State the method: every place in the database carries a `road` and `car_category` field; this is a straight count, not an opinion.
- **H2 — The four road types, and what actually happens on each**
  - H3 Paved (149 places, 58%) — normal car, no caveats
  - H3 Mostly paved (71 places, 28%) — normal car with occasional broken sections; SUV is comfort, not necessity, in most cases (call out the 4/71 economy-rated exceptions honestly if the writer finds them — currently 30 of 71 are `economy`)
  - H3 Gravel (20 places, 8%) — SUV minimum; 6 of the 20 are rated `offroad` regardless — name why (steepness/washouts), sourced from the place's own body text, not invented
  - H3 4x4-only (17 places, 7%) — offroad category, no exceptions in the data — these 17 places drive the entire "you need a 4x4" myth
- **H2 — Where the 4x4-only and gravel places actually are** — the 10-region table above, with a one-line callout that Tbilisi itself has zero
- **H2 — Four real trips, four real answers** — the five-row worked-example table above, written as short narrative paragraphs (Mestia vs. Ushguli is the strongest pair; Gergeti vs. its own side valleys is the second)
- **H2 — Matching clearance to road** — the six-category clearance table; explicit statement that `4x4_only`↔`offroad` is a 100% mechanical match in the data (build trust by showing the method, not just the conclusion)
- **H2 — What we do not know** — a mandatory honesty section per `CONTENT_STRATEGY.md §4.1`'s quality bar: this page states road *classification*, not live road *condition*. Rockslides, snow, and closures are not in this dataset. Link out to `best_season`/`open_year_round` as the seasonal signal that *is* tracked (do not claim a live road-status feed — none exists).
- **H2 — Which category to book, if you know your trip** — three short blocks: "Staying on the paved network" → `/car-rental/economy/`; "Some gravel or mountain villages" → `/car-rental/suv/`; "Ushguli, Tusheti, Abano Pass or similar" → `/car-rental/4x4/`. Mention "or hire a driver who already knows these roads" → `/car-rental/with-driver/` (brief #9 in this batch).
- **H2 — FAQ**
  - "Do I need a 4x4 for Kazbegi / Stepantsminda?" — no, `mostly_paved`/`suv` per Gergeti's own record; the higher side-valleys differ
  - "Can I drive to Svaneti (Mestia) in a normal car?" — yes, `paved`/`suv`-rated as far as Mestia itself
  - "What about Ushguli?" — no; `gravel`/`offroad`, seasonal June–September
  - "Is Tusheti / the Abano Pass road open all year?" — no; both `4x4_only` and `june-september` only
  - "Does RentUp charge less for a car I don't need?" — yes, link to `/car-rental/economy/`'s pricing
- **H2 — Book the right category** (CTA block, links to all four/five category pages)

### Internal links to add

| Anchor text | Target |
|---|---|
| "our SUV fleet" | `/car-rental/suv/` |
| "book a 4x4" / "our off-road fleet" | `/car-rental/4x4/` |
| "economy cars from 75 ₾/day" | `/car-rental/economy/` |
| "hire a driver instead" | `/car-rental/with-driver/` (brief #9) |
| "Ushguli" | `/attractions/ushguli/` |
| "Mestia" | `/attractions/mestia/` |
| "the Abano Pass" | `/attractions/abano-pass/` |
| "Omalo and Tusheti" | `/attractions/omalo-tusheti/` |
| "Gergeti Trinity Church" | `/attractions/gergeti-trinity-church/` |
| "the Svaneti Expedition route" | `/routes/svaneti-expedition/` |
| "the Georgian Military Highway route" | `/routes/military-highway-kazbegi/` |
| "our full car rental terms" | `/terms/` |
| "car rental in Georgia" (hub, from the CTA block) | `/car-rental/` |

Inbound: this page should be linked from every `offroad`/`gravel` attraction page's "getting there"
block (per `CONTENT_STRATEGY.md §4.10`'s G row on template edits — out of scope for this brief, flag
for the template owner) and from `/car-rental/4x4/`'s existing FAQ, which already asks "Do I actually
need a 4x4 for Georgia, or is it marketing?" (`KEYWORD_CLUSTERS.md A10`) without anywhere to send the
reader — this page is that destination.

### Schema

Extend the existing per-page `@graph` (Organization/AutoRental, WebSite, WebPage, BreadcrumbList —
confirmed present on every page, e.g. `dist/car-rental/tbilisi-airport/index.html`) with an
`FAQPage` node built from the FAQ block above. Do not add `HowTo` — this page answers a yes/no
qualifying question with data, it does not instruct a procedure.

### Titles & meta descriptions (written)

**EN** — Title: `Do You Need a 4x4 in Georgia? The Real Answer, by the Numbers | RentUp` (67 chars — at
the edge; if trimmed for the 70-char budget per `ONPAGE_REVIEW.md §10`, drop to `Do You Need a 4x4 in
Georgia? | RentUp`, 39 chars, and let the long form live only as the H1).
Meta: `85.6% of Georgia's mapped attractions need no 4x4 at all. See exactly which 37 places do — Ushguli, Tusheti, Abano Pass — and which car fits the rest.` (155 chars)

**KA** — Title: `გჭირდებათ 4x4 საქართველოში? — რეალური მონაცემები | RentUp` (57 chars)
Meta: `257 ღირსშესანიშნაობიდან მხოლოდ 37-ს სჭირდება ჯიპი — უშგული, თუშეთი, აბანოს უღელტეხილი. გაარკვიეთ, რომელი მანქანა გჭირდებათ.` (verify char count in-editor; Georgian counts by codepoint differently than Latin — target ≤160 rendered chars, not this draft's raw length)

**RU** — Title: `Нужен ли внедорожник в Грузии? Ответ по цифрам | RentUp` (56 chars)
Meta: `85,6% достопримечательностей Грузии не требуют джипа. Показываем, какие 37 мест из 257 требуют — и какую машину брать.` (119 chars)

**fa/he/ar — worth building?** Yes, but templates-only, not full prose, per
`CONTENT_STRATEGY.md §6.2`'s named-exception logic does *not* apply here (this is Pillar-2 bridge
prose, not one of the three explicitly named commercial exceptions). Ship the data tables, the H1/H2
structure, and the FAQ in all six languages (near-zero marginal cost — it's numbers and place names,
already translated); the narrative paragraphs (worked examples, "what we do not know") can launch
ka/en/ru only and be added to fa/he/ar once Search Console shows demand, per the same section's
revisit trigger.

### Image requirements

- Hero: a genuine gravel/mountain-road photo — reuse an existing licensed attraction photo (e.g. from
  `ushguli.yml`'s or `abano-pass.yml`'s `gallery`, both already carry photographer credit + licence
  per `CONTENT_STRATEGY.md §1.3`) rather than commissioning new photography. Alt: "Gravel road to
  Ushguli, Svaneti — the kind of surface that needs a 4x4-rated car."
- One photo per worked example (Mestia paved street vs. Ushguli gravel track) if both exist in the
  attraction galleries — a visual before/after is the single strongest asset this page can have and
  costs nothing to source.
- No stock imagery of generic "jeeps" — every image on this page should be a real, named, geolocated
  Georgian place, because that specificity is the whole argument.

### E-E-A-T signals genuinely available

- The `road`/`car_category` fields exist on **100% of 257 places** (`CONTENT_STRATEGY.md §1.3`) —
  state this coverage number on the page; it is the credibility claim competitors cannot match (per
  `CONTENT_STRATEGY.md §4`'s competitor table: aggregators have no place data, operators have 3–5
  hand-written paragraphs, blogs cover one road at a time).
- The 100% mechanical correspondence between `road: 4x4_only` and `car_category: offroad` (verified
  above) is a genuine, checkable methodology statement — say "every one of the 17 harshest routes in
  our database is independently flagged twice, and the two flags always agree" rather than a vaguer
  authority claim.
- Author/dataset attribution: state plainly that the classification is RentUp's own field data
  (`content/attractions/*.yml`), last verified [date of publish] — do not claim a government or
  third-party road authority as the source, since none is cited anywhere in the repo.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

| Competitor | What they publish | Gap this page fills |
|---|---|---|
| [georgia-spirit.com/guides/jeep-tours-georgia/](https://www.georgia-spirit.com/guides/jeep-tours-georgia/) | "Jeep tours in Georgia: the routes that need a 4x4" — closest existing content match | Editorial, no structured/countable data, no fleet tie-in |
| [starcar.ge/blog/best-suv-rentals-in-georgia-2026-mountain-roads-off-road-guide](https://starcar.ge/blog/best-suv-rentals-in-georgia-2026-mountain-roads-off-road-guide) | Operator blog on SUV/mountain roads | Sells one operator's SUVs; no place-level data table |
| [fill.ge/en/rent/4x4](https://fill.ge/en/rent/4x4), [rentalcartbilisi.com/4x4/](https://rentalcartbilisi.com/4x4/), [carrentalservice.ge/en/off-road-suv-rental/](https://carrentalservice.ge/en/off-road-suv-rental/) | Category/inventory pages | Booking engines, not answer pages — no "do I need one" framing at all |
| [georgia-spirit.com/guides/renting-car-georgia/](https://www.georgia-spirit.com/guides/renting-car-georgia/) | General "honest guide" to renting | Broad, not focused on the 4x4 decision specifically |
| wander-lush.org (cited across `KEYWORD_CLUSTERS.md` as the dominant EN travel authority in this niche) | Excellent trip-report prose | No structured, countable dataset; cannot be replicated at scale by a blogger |

**Sources:** [georgia-spirit.com jeep tours](https://www.georgia-spirit.com/guides/jeep-tours-georgia/) · [starcar.ge SUV guide](https://starcar.ge/blog/best-suv-rentals-in-georgia-2026-mountain-roads-off-road-guide) · [fill.ge 4x4](https://fill.ge/en/rent/4x4) · [rentalcartbilisi.com 4x4](https://rentalcartbilisi.com/4x4/) · [carrentalservice.ge off-road](https://carrentalservice.ge/en/off-road-suv-rental/) · [georgia-spirit.com renting guide](https://www.georgia-spirit.com/guides/renting-car-georgia/)

### Do-not-claim list

- Do not claim any road is currently "open," "closed," "safe," or "passable" — the data is a
  classification, not a live feed (`CONTENT_STRATEGY.md` guardrail 5).
- Do not state a season window tighter or looser than the place's own `best_season`/`open_year_round`.
- Do not claim insurance covers off-road damage in economy/SUV categories — that is a `terms.yml`
  claim under the I1–I3 conflict; if the page mentions insurance at all, add "verify against the
  reconciled policy before publishing" rather than stating an excess figure.
- Do not extrapolate the 37-place figure into a percentage of *all Georgian roads* — it is 37 of 257
  *mapped attractions* in this dataset, not a national road survey.
- Do not use "jeep" as a category name in English copy (it is correct in Georgian — `ჯიპი` is the
  vernacular term per `KEYWORD_CLUSTERS.md §A10` — but in English it is a brand name, not RentUp's
  category label, which is "4x4 / off-road").

---

# Brief 2 — `/car-rental/` hub rewrite

Per the hard rule, this is an **improvement brief against the live page**, not a from-scratch brief.
Read directly from `dist/car-rental/index.html` plus the detailed findings already logged in
`ONPAGE_REVIEW.md §2` (F-HUB-1 through F-HUB-6).

## What the live page already does well (keep)

- 1,241 words (en) / 983 (ka) across 15 H2 sections: booking, eligibility, deposit, mileage, fuel,
  insurance, delivery, one-way, extras, cancellation, support, FAQ — genuinely comprehensive.
- `content/settings/seo_car_rental.yml` already holds **hand-written, differentiated, grammatical**
  `meta_title`/`meta_description` for this exact page in all six languages — currently **discarded**
  by `build.py`'s precedence bug (F-HUB-1). This brief assumes that bug is fixed (it is a three-line
  code change already specified in `ONPAGE_REVIEW.md`, not a content task) and specifies the *content*
  changes on top of that fix.

## What is missing or wrong (this brief's scope)

| Issue | Source | Fix this brief specifies |
|---|---|---|
| Only 4 of 6 categories have a landing page — `business` and `van` are invisible on the hub (F-HUB-6) | `categories.yml` vs `dist/car-rental/` | Add 2 more category cards once briefs #7 (business) ships; link to `/car-rental/van/` only once that page exists — do not link a 404 |
| Zero content images (F-HUB-5) | live page | Add fleet-card thumbnails, `c["image"]` already exists per car |
| H2 "Cars in this category" mislabeled on a hub, not a category page (F-HUB-2) | `seo_ui.yml:102` | New copy needs its own hub-scoped heading |
| ka H1 and a body H2 are byte-identical (F-HUB-3) | `seo_car_rental.yml:156` | Narrower H2 phrasing supplied below |
| "FAQ" hard-coded in English on ka/ru/fa/he/ar (F-HUB-4) | `build.py` | Translated heading supplied below |
| No mention anywhere on the hub of monthly/long-term pricing, the deposit honesty page, one-way, business class, or the with-driver option — **all five are new pages in this same batch and none is linked from the site's main commercial page** | this batch | Add one new H2 section, "More ways to rent," linking out to all five |
| Terminology drift — `დაქირავება` (title) vs `გაქირავება` (H1) vs `ქირაობა` (hand-written meta) — three words for "rent" on one page (KA-1 in `ONPAGE_REVIEW.md §9`) | multiple | Standardise on `ქირაობა` per the reviewer's recommendation |

## Brief

- **Target URL:** `/car-rental/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `car rental georgia` — **secondary:** `rent a car georgia`, `car hire georgia`, `car rental in georgia country`, `self drive georgia`, `car rental georgia prices`, `unlimited mileage car rental georgia`
- **Primary (ka):** `მანქანის ქირაობა` — **secondary:** `მანქანების ქირაობა საქართველოში`, `ავტომობილის ქირაობა`, `მანქანის ქირაობის ფასები`, transliterated `manqanis qiraoba` (worked into body copy per `KEYWORD_CLUSTERS.md §1.2`, never as a URL)
- **Primary (ru):** `аренда авто в Грузии` — **secondary:** `прокат авто Грузия`, `аренда машины в Грузии цены`, `автопрокат Грузия без ограничения пробега`
- **Intent / funnel stage:** Transactional / BOFU — the site's primary money page.
- **Audience & real question:** Someone who has already decided to rent in Georgia and is now
  comparing this operator against 8+ established Georgian competitors and 4 international
  aggregators. Their real question is "what does this company actually offer, concretely, that I can
  check before I commit" — not general education.
- **Target word count:** Net addition of 250–400 words on top of the existing 1,241 (en) — this page
  is not thin, it needs one new section and better internal linking, not a rewrite of what already
  works.

### Outline additions (insert into the existing 15-section structure, do not restructure what works)

- **H1** — keep concept, standardise terminology per KA-1 above.
- *(existing sections unchanged: booking, eligibility, deposit, mileage, fuel, insurance, delivery,
  one-way, extras, cancellation, support)*
- **NEW H2 — "More ways to rent"** (insert after the existing category grid, before FAQ):
  - "Renting for a month or longer?" → `/car-rental/monthly/` (brief #4), one sentence citing that
    30-day rates exist on all 17 cars
  - "Need the car delivered from one city and left in another?" → `/car-rental/one-way/` (brief #8)
  - "Renting for a business trip or a client?" → `/car-rental/business/` (brief #7)
  - "Would rather not drive yourself?" → `/car-rental/with-driver/` (brief #9)
  - "Worried about the deposit hold?" → `/car-rental/deposit/` (brief #6)
  - "First time renting in Georgia — what do I need?" → `/car-rental/requirements/` (brief #10)
- **H2 FAQ** — retitle from hard-coded English to `su("faq_title", lang)` (a code fix, flagged for
  the template owner, not a content task) and add one new Q&A: "Do I need a 4x4?" with a one-line
  answer and a link to `/guides/do-i-need-a-4x4-in-georgia/` (brief #1) — this is the single most
  important new internal link this brief adds, since it closes the loop `CONTENT_STRATEGY.md §2.2`
  identifies as "the bridge tier is the entire opportunity, and it is empty."

### Internal links to add

| Anchor text | Target |
|---|---|
| "monthly and long-term rental" | `/car-rental/monthly/` |
| "one-way rentals between cities" | `/car-rental/one-way/` |
| "business-class rental" | `/car-rental/business/` |
| "rent a car with a driver" | `/car-rental/with-driver/` |
| "how the deposit works" | `/car-rental/deposit/` |
| "what you need to rent a car here" | `/car-rental/requirements/` |
| "do I need a 4x4 for Georgia?" | `/guides/do-i-need-a-4x4-in-georgia/` |
| category card links (existing, keep) | `/car-rental/economy/`, `/suv/`, `/4x4/`, `/minivan/`, plus `/business/` once brief #7 ships |
| "see all 17 cars" | `/fleet/` |

### Schema

Extend the existing `AutoRental`/`LocalBusiness` + `WebSite` + `WebPage` + `BreadcrumbList` graph.
Add an `ItemList` of the six (once business/van exist) category pages with `url` + `name`, and keep
the existing FAQ content as an `FAQPage` node (it is not currently emitted per `ONPAGE_REVIEW.md`'s
silence on hub schema — confirm and add if missing).

### Titles & meta descriptions (written)

Use the **existing hand-written** values in `content/settings/seo_car_rental.yml` — they are already
better than the generated fallback (`ONPAGE_REVIEW.md F-HUB-1`) — with two corrections: normalise the
brand suffix to `| RentUp` (not `— RentUp.ge`) and the Georgian verb to `ქირაობა`:

**EN:** `Car Rental in Georgia — Unlimited Mileage, No Hidden Fees | RentUp` (66 chars)
Meta: `Rent a car anywhere in Georgia — 17 vehicles, unlimited mileage, cash or card deposit, free Tbilisi delivery. See prices for every category.` (143 chars, tightened from the source's 142–211-char range per `ONPAGE_REVIEW.md`'s instruction to trim to ≤160)

**KA:** `მანქანის ქირაობა საქართველოში — შეუზღუდავი გარბენი | RentUp` (59 chars)
Meta: `იქირავეთ მანქანა საქართველოში — 17 ავტომობილი, შეუზღუდავი გარბენი, თბილისში უფასო მიწოდება. ნახეთ ფასები ყველა კატეგორიაზე.`

**RU:** `Аренда авто в Грузии — без ограничения пробега | RentUp` (55 chars)
Meta: `Аренда авто по всей Грузии — 17 автомобилей, безлимитный пробег, бесплатная доставка по Тбилиси. Цены по всем категориям.`

**fa/he/ar:** Yes, always — this is one of the three explicit exceptions in
`CONTENT_STRATEGY.md §6.2` ("never withhold a money page from a language the business serves"). The
existing six-language parity should be kept; only the new "More ways to rent" section needs adding in
all six.

### Image requirements

- Add a small photo grid of 4–6 fleet cars to the category section (`c["image"]` field exists per
  `ONPAGE_REVIEW.md F-HUB-5` — this is a template fix, not new photography commissioning; flag for
  the developer, note in the brief so the writer doesn't attempt to source new photos).
- Alt text per photo: `"{car name} — available for {category} rental in Georgia"`.

### E-E-A-T signals genuinely available

- 17 real vehicles with real, checkable prices (`content/cars/*.yml`) — competitors either hide fleet
  detail behind a booking flow (aggregators) or list 3–5 cars from a salesperson's memory (Georgian
  operators, per `CONTENT_STRATEGY.md §4`).
- Founded 2019 (`content/settings/site.yml: founded: '2019'`) — seven years operating as of 2026, a
  genuine tenure claim already used in the site's own schema (`foundingDate` in the AutoRental node).
- Free city delivery in Tbilisi and cash-or-card flexibility are checkable, undisputed facts (see
  §0.3 — do not extend this to claiming CDW inclusion or a specific excess figure).

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[localrent.com/en/georgia/tbilisi/](https://www.localrent.com/en/georgia/tbilisi/) ·
[en.geodrive.info](https://en.geodrive.info/) ·
[wander-lush.org/driving-in-georgia-car-rental-tbilisi/](https://wander-lush.org/driving-in-georgia-car-rental-tbilisi/) (dominant EN editorial authority) ·
[europcar.com/.../car-rental-georgia/tbilisi](https://www.europcar.com/en-us/places/car-rental-georgia/tbilisi) ·
plus the 8 established Georgian operators already catalogued in `KEYWORD_CLUSTERS.md §0`
(carrentgeorgia.ge, gsscarrental.com, starcar.ge, cars4rent.ge, geodrive.info, triprents.com,
autohub.rent).

### Do-not-claim list

- Do not state a specific excess figure or "full coverage" anywhere on this page without the
  reconciled-policy verification note (§0.3) — this is the page most likely to be quoted back at a
  customer in a dispute.
- Do not claim a "no deposit" option exists (`waiver_available: false`).
- Do not claim cross-border travel is permitted in any form pending §0.3's cross-border conflict.
- Do not restate the tiered young-driver surcharge as a flat "21+, no surcharge" claim — that
  contradicts the live booking config (§0.3).

---

# Brief 3 — `/car-rental/tbilisi-airport/` rewrite

## What the live page actually contains (read directly from `dist/car-rental/tbilisi-airport/index.html`)

Confirmed by direct read: the file is 20,937 bytes total, but the vast majority is boilerplate
(head/schema/header/footer/booking-modal markup shared by every page on the site). The **unique
visible body content is exactly six sections**: a one-paragraph pickup-process block, a
"Popular road trips from `{place}`" block with an **unrendered literal placeholder** in the H2
(confirmed live, matches `ONPAGE_REVIEW.md F-LOC-1` exactly), a two-card "Best car for this trip"
block, a "Nearby places" list that **repeats the same 5 attractions already listed two sections above**
(F-LOC-4, confirmed — the same five links to Holy Trinity Cathedral, Metekhi Church, Abanotubani,
Narikala Fortress and Bridge of Peace appear twice), and an FAQ paragraph. This matches the ~2,064
character measurement in the task brief — real unique prose is closer to 350–400 words once
boilerplate and the duplicated list are excluded.

| Issue found (matches `ONPAGE_REVIEW.md §3`) | Confirmed live |
|---|---|
| F-LOC-1 — literal `{place}` in a visible H2 | Yes: `<h2>Popular road trips from {place}</h2>` |
| F-LOC-4 — same 5 attractions rendered twice | Yes: identical five links in "Popular road trips" table and "Nearby places" list |
| F-LOC-5 — mislabelled H2 "Best car for this trip" on a location page | Yes |
| F-LOC-7 — thin unique copy | Confirmed: ~90 words genuinely unique to this location (the pickup paragraph) out of ~350 total |
| F-LOC-2/F-LOC-3 (ka case errors, en brand suffix) | Not visible in the en source read directly; assume present per the audit until the ka/ru builds are checked |

## Brief

- **Target URL:** `/car-rental/tbilisi-airport/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `tbilisi airport car rental` — **secondary:** `car rental tbilisi airport tbs`, `rent a car tbilisi airport`, `tbilisi airport car rental late night`, `car delivery tbilisi airport`, `pick up car tbilisi airport`
- **Primary (ka):** `მანქანის ქირაობა თბილისის აეროპორტში` — **secondary:** `ავტომობილის ქირაობა აეროპორტში`, `მანქანის მიწოდება აეროპორტში`
- **Primary (ru):** `аренда авто аэропорт Тбилиси` — **secondary:** `прокат авто в аэропорту Тбилиси`, `аренда авто Тбилиси аэропорт ночью`, `забрать машину в аэропорту Тбилиси`
- **Intent / funnel stage:** Transactional / BOFU — per `KEYWORD_CLUSTERS.md A3`, "highest booking
  intent in the whole map."
- **Audience & real question:** Someone who has just landed or is about to fly into TBS and needs to
  know, concretely: where do I meet the car, what does it cost, what happens if my flight lands at
  1am, and can I drop the car somewhere else if I'm not flying home from Tbilisi.
- **Target word count:** 900–1,100 words (up from ~350 genuinely unique words today) — this is the
  fix for a page an SEO audit flagged as too thin to earn its "highest booking intent" ranking.

### Outline

- **H1:** Car Rental at Tbilisi Airport (TBS) — keep; add "(TBS)" if not already in the H1 (it is in
  the title already).
- **H2 — Meeting you at arrivals** (expand the existing single paragraph): flight-number-at-booking
  process, meet at arrivals with a name sign, delivery fee **30 ₾ — the cheapest of the three airports
  RentUp serves** (`rental_policy.yml: airport_fee_gel.tbilisi-airport: 30` vs. 60/60 for Kutaisi and
  Batumi — a genuine, checkable comparative fact), handover location and paperwork.
- **H2 — Landing late? The night-arrival answer nobody else states plainly** (new section — this is
  the single highest-leverage addition per `KEYWORD_CLUSTERS.md A3`'s "winnable sub-angle"): state the
  20 ₾ night surcharge for 22:00–08:00 pickups (`rental_policy.yml: night_surcharge_gel: 20`,
  `night_from/night_to`) as an exact, published number — "competitors mostly say nothing" per the
  cluster note; being the page that states a number wins the query.
- **H2 — What's 13 km from the airport, and what to skip** (fix F-LOC-4: split the duplicated list
  into two genuinely different purposes) — the airport sits on the Kakheti highway side of Tbilisi;
  for a wine-region-first itinerary the ring road skips the city entirely. Keep the five real
  attraction links here, once, with distance + road class (all `paved`, all 12 km per the current
  build — verify these numbers against `distance_tbilisi_km` on each attraction file before publishing,
  the current build shows a flat "12 km" for all five which looks templated rather than measured).
- **H2 — Which category fits an airport pickup** (fix F-LOC-5's mislabelled heading): SUV from 130
  ₾/day, economy from 75 ₾/day — link to both category pages, and to the new 4x4 guide for anyone
  whose onward trip includes Svaneti/Tusheti.
- **H2 — Flying out of a different city?** (new, small section pulling the one-way fact forward from
  the FAQ paragraph where it is currently buried): 100 ₾ one-way fee to Kutaisi or Batumi — link to
  `/car-rental/one-way/` (brief #8) for the full matrix rather than restating it here (guard against
  cannibalisation per `KEYWORD_CLUSTERS.md A21`'s explicit warning).
- **H2 — FAQ** (promote the existing paragraph's content into real Q&A pairs):
  - "How much does airport delivery cost?" — 30 ₾, no matter the airline
  - "What if my flight lands after 22:00?" — 20 ₾ night surcharge, stated plainly
  - "Can I drop the car off in Batumi or Kutaisi instead?" — yes, 100 ₾ one-way fee, link out
  - "How far is the airport from central Tbilisi?" — ~13 km via the Kakheti highway

### Internal links to add

| Anchor text | Target |
|---|---|
| "our full one-way rental fees" | `/car-rental/one-way/` |
| "Crossover / SUV category" | `/car-rental/suv/` |
| "Economy class" | `/car-rental/economy/` |
| "do you need a 4x4 for your trip?" | `/guides/do-i-need-a-4x4-in-georgia/` |
| "Kutaisi Airport" / "Batumi Airport" pickup pages | `/car-rental/kutaisi-airport/`, `/car-rental/batumi-airport/` |
| named attraction links (existing 5, deduplicated) | keep as-is, each once |
| "Car Rental in Georgia" (hub) | `/car-rental/` |

### Schema

Keep the existing `Place`/`GeoCoordinates` "about" node (already correct, 41.6692/44.9547). Add an
`FAQPage` node for the new Q&A block. No change needed to the Organization/BreadcrumbList graph.

### Titles & meta descriptions (written)

**EN:** Keep the existing title — `Tbilisi Airport Car Rental (TBS) | RentUp` (41 chars) is already
good. New meta reflecting the expanded content:
`Meet-and-greet pickup at Tbilisi Airport for 30 ₾ — the cheapest of our three airports. Night arrivals, one-way drop-off and nearby routes explained.` (152 chars)

**KA:** Fix the case error first (F-LOC-2/F-LOC-3): `მანქანის ქირაობა თბილისის აეროპორტში (TBS) | RentUp` (not `თბილისიის`). Meta: `მიხვდებით აეროპორტში 30 ₾-ად — ჩვენი სამი აეროპორტიდან ყველაზე იაფი. გავეცანით ღამის ჩამოფრენებს, ცალმხრივ დაბრუნებას და ახლომდებარე მარშრუტებს.`

**RU:** `Аренда авто в аэропорту Тбилиси (TBS) | RentUp` (48 chars). Meta: `Встреча в аэропорту Тбилиси за 30 ₾ — самая недорогая из трёх площадок. Ночные рейсы, аренда в одну сторону и маршруты рядом.`

**fa/he/ar:** Yes — commercial money page, one of the "always all six" categories per
`CONTENT_STRATEGY.md §6.2`.

### Image requirements

- A real photo of the arrivals hall or the meet-and-greet point if one exists in any asset library;
  otherwise a labelled map graphic (lat/lon already known: 41.6692, 44.9547) showing the airport
  relative to central Tbilisi and the Kakheti highway split — this single image would visually carry
  the "wine region vs. city" routing point the copy makes.
- Photos of the 5 linked attractions already exist in their own `gallery` fields — reuse one thumbnail
  per attraction in the "what's 13 km away" section rather than a bare text list.

### E-E-A-T signals genuinely available

- Exact, sourced fees (30 ₾ / 20 ₾ / 100 ₾) that competitors' pages routinely omit — `KEYWORD_CLUSTERS.md
  A3` notes this explicitly ("competitors mostly say nothing" on the night-surcharge question).
  Publishing a number is itself the differentiator; no additional authority claim is needed.
- Precise geo-coordinates already in the page's schema — a small, genuine "we know exactly where this
  is" signal.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

Global brands with a TBS counter — [Alamo](https://www.alamo.com/en/car-rental-locations/ge/tbilisi-international-airport-z3a1.html), [National](https://www.nationalcar.com/en/car-rental-locations/ge/tbilisi-international-airport-z3n1.html), [Enterprise](https://www.enterprise.com/en/car-rental-locations/ge/tbilisi-international-airport-z3e1.html), [Europcar](https://www.europcar.com/en-us/places/car-rental-georgia/tbilisi/tbilisi-international-airport) — plus aggregators [Skyscanner](https://www.skyscanner.com/car-rental-from/tbs/car-rental-from-tbilisi-airport.html) and [GetRentacar.com](https://getrentacar.com/en-US/georgia/tbs-tbilisi-international-airport), and one local dedicated page, [rentcarsgeorgia.com/tbilisi-airport-car-rental/](https://rentcarsgeorgia.com/tbilisi-airport-car-rental/) ("Free Pickup at TBS" — the closest direct competitor in positioning).

### Do-not-claim list

- Do not claim "free" airport delivery — it costs 30 ₾, clearly stated as a fee, not a perk.
- Do not claim a specific meet-and-greet wait-time guarantee unless the owner supplies one — not in
  any source file.
- Do not restate the one-way fee's terms beyond "100 ₾, ask about drop-off city" — the full matrix
  belongs on brief #8's page, not duplicated here (cannibalisation guard, `KEYWORD_CLUSTERS.md A21`).

---

# Brief 4 — `/car-rental/monthly/` (new)

## The data behind it — computed directly, not asserted

All 17 cars carry `price_1_6`, `price_7_29` and `price_30` (GEL/day). Computed discount from the
1–6-day rate to each tier, across every car in `content/cars/*.yml`:

| Car | Category | 1–6 days | 7–29 days | 30+ days | 7-day discount | 30-day discount |
|---|---|---|---|---|---|---|
| Toyota Prius | economy | 75 | 68 | 56 | 9.3% | 25.3% |
| Hyundai Elantra | economy | 82 | 74 | 62 | 9.8% | 24.4% |
| Toyota Corolla | economy | 88 | 79 | 66 | 10.2% | 25.0% |
| Hyundai Tucson | suv | 130 | 117 | 98 | 10.0% | 24.6% |
| Mitsubishi Outlander | suv | 138 | 124 | 104 | 10.1% | 24.6% |
| Toyota RAV4 | suv | 145 | 130 | 109 | 10.3% | 24.8% |
| Toyota Camry | business | 210 | 189 | 158 | 10.0% | 24.8% |
| Mercedes-Benz E-Class | business | 290 | 261 | 218 | 10.0% | 24.8% |
| BMW 5 Series | business | 310 | 279 | 232 | 10.0% | 25.2% |
| Mitsubishi Pajero | offroad | 240 | 216 | 180 | 10.0% | 25.0% |
| Mitsubishi Delica D:5 | offroad | 290 | 261 | 218 | 10.0% | 24.8% |
| Toyota Land Cruiser Prado | offroad | 330 | 297 | 248 | 10.0% | 24.8% |
| Mercedes-Benz Vito | minivan | 200 | 180 | 150 | 10.0% | 25.0% |
| Toyota Alphard | minivan | 310 | 279 | 232 | 10.0% | 25.2% |
| Hyundai Staria | minivan | 260 | 234 | 195 | 10.0% | 25.0% |
| Ford Transit | van | 185 | 166 | 139 | 10.3% | 24.9% |
| Mercedes-Benz Sprinter | van | 215 | 194 | 161 | 9.8% | 25.1% |

**This independently confirms the discount tiers `faq.yml` states in prose** ("10% from 7 days, 25%
from 30 days") — the per-car math lines up to within half a percentage point across all 17 vehicles,
so this specific claim is safe to publish without a policy-reconciliation caveat. The **"up to 40% on
corporate contracts longer than 3 months" claim has no supporting field anywhere in `content/`** —
`max_rental_days: 90` exists (`rental_policy.yml`) but no fourth price tier does. **Do not publish the
40% figure without the owner confirming a real corporate rate card** — this is exactly the case the
hard rule about commercial-terms verification is for.

## Brief

- **Target URL:** `/car-rental/monthly/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `monthly car rental georgia` — **secondary:** `long term car rental tbilisi`, `rent a car for a month in georgia`, `car rental georgia for digital nomads`, `long term car hire georgia expat`, `corporate car rental georgia`
- **Primary (ka):** `მანქანის ქირაობა თვიურად` — **secondary:** `გრძელვადიანი მანქანის ქირაობა`, `მანქანის ქირაობა ერთი თვით`, `კორპორატიული მანქანის ქირაობა`
- **Primary (ru):** `аренда авто на месяц в Грузии` — **secondary:** `долгосрочная аренда авто Тбилиси`, `аренда авто для релокантов Грузия`, `подписка на авто Грузия`
- **Intent / funnel stage:** Transactional / BOFU — per `KEYWORD_CLUSTERS.md A20`, "highest lifetime
  value per booking" and "the single best unbuilt commercial page on the site."
- **Audience & real question:** Remote workers, relocators and long-stay visitors to Georgia (the
  "digital nomad" / relocation population `KEYWORD_CLUSTERS.md A20` identifies) asking "what does a
  month actually cost, all-in, and is it cheaper than daily rates add up to."
- **Target word count:** 1,400–1,700 words — enough for a full price table across all 17 cars plus
  FAQ, without padding; this is a page that should win on data density, not prose length.

### Outline

- **H1:** Monthly & Long-Term Car Rental in Georgia (ka: `მანქანის ქირაობა თვიურად საქართველოში` / ru: `Аренда авто на месяц в Грузии`)
- **H2 — What changes at 7 days, and again at 30** — state the two *verified* tiers (≈10% at 7 days,
  ≈25% at 30 days) as fleet-wide facts, citing that the discount is consistent within half a point
  across all 17 vehicles — this consistency is the credibility hook.
- **H2 — Full price table, all 17 cars, three tiers** — the table above, sortable if the template
  supports it, grouped by category (economy → suv → business → offroad → minivan → van).
- **H2 — Who this is for** — three short profiles grounded in real fleet facts: the remote worker who
  wants an economy car for city driving (Prius 56 ₾/day at 30 days); the relocating family who needs a
  minivan (Vito 150 ₾/day at 30 days, 8 seats); the company car for a longer posting (business class,
  Camry 158 ₾/day at 30 days).
- **H2 — What doesn't change at 30 days** — mileage is unlimited regardless of rental length
  (`rental_policy.yml: mileage.unlimited: true`, unqualified by duration); deposit amount is the same
  per category (state the deposit table, `deposit` field per car) — **note the deposit *method*
  (card hold vs. cash) is under the §0.3 conflict; describe only the amount, not the method, without
  the verification caveat**.
- **H2 — Booking a month or longer** — practical mechanics: max rental is 90 days
  (`rental_policy.yml: max_rental_days: 90`) — state this as a real ceiling, not a marketing round
  number; cancellation terms (`cancellation.free_until_hours: 24`) if the owner confirms it applies
  identically to long-term bookings (flag if it doesn't — not stated either way in the source file).
- **H2 — FAQ**
  - "Is there really a discount for a month?" — yes, ~25% vs. the daily rate, verified across the
    fleet
  - "Is mileage still unlimited at 30 days?" — yes
  - "What's the longest I can rent for?" — 90 days
  - "Do you offer a corporate rate beyond 3 months?" — **flag as "ask us" rather than stating 40% —
    unverified figure, see §0.3**

### Internal links to add

| Anchor text | Target |
|---|---|
| "the daily rate for each car" | `/fleet/` and individual `/fleet/{car}/` pages, at least 3 named |
| "car rental in Georgia" (hub) | `/car-rental/` |
| "one-way between cities" | `/car-rental/one-way/` |
| "renting with a driver" | `/car-rental/with-driver/` |
| "what you need to rent" | `/car-rental/requirements/` |
| "economy", "SUV", "business", "minivan" category mentions | respective `/car-rental/{category}/` pages |

### Schema

`WebPage` + `FAQPage` in the existing graph. Consider an `AggregateOffer` node summarising the price
range (56–248 ₾/day at the 30-day tier) if the templating layer supports `Product`/`Offer` per car
already (confirmed it does on vehicle pages per `ONPAGE_REVIEW.md F-VEH-2`) — reuse that pattern
rather than inventing a new one.

### Titles & meta descriptions (written)

**EN:** `Monthly Car Rental in Georgia — From 56 ₾/day | RentUp` (54 chars)
Meta: `Rent a car in Georgia for a month or longer — up to 25% off the daily rate on all 17 vehicles, unlimited mileage included. See prices by car.` (144 chars)

**KA:** `მანქანის ქირაობა თვიურად — 56 ₾-დან | RentUp` (44 chars)
Meta: `იქირავეთ მანქანა თვით ან მეტი ხნით — 25%-მდე ფასდაკლება ყველა 17 ავტომობილზე, შეუზღუდავი გარბენით. ნახეთ ფასები.`

**RU:** `Аренда авто на месяц в Грузии — от 56 ₾/день | RentUp` (53 chars)
Meta: `Аренда авто в Грузии на месяц и дольше — скидка до 25% на все 17 автомобилей, безлимитный пробег включён. Смотрите цены.`

**fa/he/ar:** Yes — commercial money page, one of the "always all six" per `CONTENT_STRATEGY.md §6.2`,
and this specific cluster is structurally growing (remote-work migration to Georgia draws from a
broader set of nationalities than the daily-rental tourist market).

### Image requirements

- Fleet-category photo grid (reuse `c["image"]` per car, same as brief #2's fix).
- No monthly-specific photography needed — this page sells on the price table, not on lifestyle
  imagery; do not commission stock "digital nomad" photos.

### E-E-A-T signals genuinely available

- The discount consistency across all 17 vehicles (independently verified in this brief, not asserted
  from `faq.yml` alone) is a genuine, checkable claim — state the math, not just the conclusion.
- 90-day maximum is a real, stated ceiling (not "unlimited," which would be a stronger and unverified
  claim) — precision here builds trust with a segment (relocators) that reads terms carefully.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[oneclickdrive.com/monthly-car-rental-tbilisi](https://www.oneclickdrive.com/monthly-car-rental-tbilisi) (dedicated monthly-rental page — direct competitor) ·
[og.ge/services/long-term-car-rental](https://og.ge/services/long-term-car-rental) ·
[en.geodrive.info/long-term_car_rent_georgia](https://en.geodrive.info/long-term_car_rent_georgia) ·
[enterprise.ge/.../monthly-or-more-rentals](https://www.enterprise.ge/web/monthly-or-more-rentals-with-enterprise-rent-a-car-in-georgia) ·
general aggregators (VIP Cars, Expedia, Localrent) rank for the head term but do not have a dedicated
monthly page — confirming `KEYWORD_CLUSTERS.md A20`'s "soft SERP" assessment.

### Do-not-claim list

- Do not publish the "up to 40% corporate discount over 3 months" figure — unverified, see §0.3.
- Do not claim the deposit is waived or reduced for long-term rentals — no field supports this.
- Do not claim a specific corporate-account or invoicing process unless the owner supplies one — not
  in any source file.
- Do not imply mileage becomes limited beyond a certain length — `mileage.unlimited: true` is
  unqualified by duration in `rental_policy.yml`.

---

# Brief 5 — `/itineraries/georgia-7-days/` rewrite

## What the live page already contains

Read directly from `content/itineraries/georgia-7-days.yml` and `dist/itineraries/georgia-7-days/index.html`.
The page is **already one of the stronger templates on the site** — 529 words (en), 21 internal links,
every named attraction in the prose is linked with its own name as anchor text
(`ONPAGE_REVIEW.md §8`). This is an improvement/fix brief, not a from-scratch rewrite.

Two real problems, both confirmed live:

1. **F-ITI-1 (P0, confirmed):** the meta description ships the literal, unrendered string
   `A {days}-day Georgia itinerary covering {km} km and {stops} stops, with a day-by-day plan, drive
   times and the car category it needs.` — `build.py` never substitutes `{stops}`, which per
   `ONPAGE_REVIEW.md` causes the entire template to survive verbatim. **This is a code fix
   (`build.py:3694`), not a content task — but the brief cannot ship new copy into a description field
   that is currently broken; confirm the fix has landed before this brief's meta descriptions go live.**
2. **F-ITI-6 (P2, confirmed independently in this brief's own read of the YAML):** `content/itineraries/georgia-7-days.yml`'s
   day-by-day plan shows **Day 2 as `gori → gori, 115 km, 2:10`** — identical distance and drive time
   to Day 1's `tbilisi → gori, 115 km, 2:10` — which cannot be correct for a same-city day (Uplistsikhe,
   Gori Fortress and Ateni Sioni are all local excursions from a Gori base, not a 115 km transfer).
   Days 6 and 7 show the same pattern (`kutaisi → kutaisi, 80 km, 1:43` and `1:44` respectively, both
   copied from Day 5's actual `akhaltsikhe → kutaisi` transfer numbers). **This is a data-accuracy
   issue in the source YAML, not a copy-editing choice — flag it to the data owner before writing new
   day-by-day prose that would otherwise repeat wrong numbers into six languages.** Do not silently
   invent corrected km/drive figures; either get real drive-time estimates for the local Gori and
   Kutaisi day-trips from `road_legs.yml` or an equivalent source, or present those two days without a
   km/drive figure at all until they exist.

## Brief

- **Target URL:** `/itineraries/georgia-7-days/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `georgia itinerary 7 days` — **secondary:** `7 day georgia road trip`, `one week in georgia itinerary`, `georgia road trip 7 days by car`, `mtskheta to kutaisi road trip`
- **Primary (ka):** `საქართველოს მარშრუტი 7 დღე` — **secondary:** `7 დღიანი მოგზაურობა საქართველოში`, `საქართველო ერთ კვირაში`
- **Primary (ru):** `маршрут по Грузии 7 дней` — **secondary:** `грузия за неделю маршрут на машине`, `путешествие по Грузии на 7 дней`
- **Intent / funnel stage:** Discovery→qualify / TOFU–MOFU — Intent‑T per `CONTENT_STRATEGY.md §2.1`;
  the reader has not yet thought about a car, but this itinerary is the single strongest "you only need
  an economy car" bridge asset on the site (see below).
- **Audience & real question:** A first-time visitor planning a one-week Georgia trip who wants a
  ready-made route, not a from-scratch plan — and, once they trust the route, a natural next question
  is "what do I rent to drive this."
- **Target word count:** 700–900 words (close to the existing 529 — this page's job is a clean
  day-by-day structure and strong internal linking, not long-form prose; do not pad it).

### Outline (keep existing day-by-day structure, add two sections)

- **H1:** Georgia in 7 Days: Heritage Road from Mtskheta to Kutaisi — keep, it is specific and good.
- **H2 — Overview** *(existing "short" field + intro paragraph — keep)*
- **H3 × 7 — Day 1 through Day 7** *(existing per-day blocks — keep structure; see the data-accuracy
  flag above before publishing Day 2/6/7's numbers)*
- **NEW H2 — Why this route needs nothing bigger than an economy car** (this is the single highest-value
  addition): state plainly, from the route's own `car_category: economy` field applied to **all seven
  days without exception** — "the only one of the five curated itineraries here that never asks for an
  SUV" (a genuine, checkable differentiator vs. the 3-, 10- and 14-day itineraries, which mix
  categories) — and link straight to `/car-rental/economy/`. This directly serves
  `CONTENT_STRATEGY.md §2.2`'s "bridge" thesis with a concrete, low-friction example: unlike the 4x4
  guide (brief #1), which is about the roads that *do* need a bigger car, this page is the reassuring
  counter-case that lets an anxious first-timer book the cheapest category with confidence.
- **H2 — Tips** *(existing `tips` field — keep, note the "mostly-paved" Ateni Sioni exception is
  already flagged correctly in the source copy)*
- **H2 — FAQ** *(new)*:
  - "Do I need an SUV for this route?" — no, confirmed economy-rated for all seven days
  - "Can I do this in fewer or more days?" — link to `/itineraries/georgia-5-days/` and
    `/itineraries/georgia-10-days/`
  - "What if I want to add a mountain leg?" — link to `/guides/do-i-need-a-4x4-in-georgia/` as the
    honest next step for anyone tempted to bolt on Kazbegi or Svaneti
- **H2 — Book the car for this trip** (CTA, existing pattern — keep, verify it links to
  `/car-rental/economy/` specifically, not the generic hub)

### Internal links to add

| Anchor text | Target |
|---|---|
| "economy class, from 75 ₾/day" | `/car-rental/economy/` |
| "renting for a week" (ties to the verified 7-day discount) | `/car-rental/monthly/` (brief #4 — cross-link the ~10% 7-day tier) |
| "do you need a bigger car for the mountains?" | `/guides/do-i-need-a-4x4-in-georgia/` |
| "the 5-day" / "10-day" itineraries | `/itineraries/georgia-5-days/`, `/itineraries/georgia-10-days/` |
| existing per-attraction links (21 already present) | keep, verify none are broken |
| "Mtskheta-Gori Heritage", "Vardzia-Borjomi South", "Imereti Family Discovery" component routes | `/routes/mtskheta-gori-heritage/`, `/routes/vardzia-borjomi-south/`, `/routes/imereti-family-discovery/` (the three `route_slugs` this itinerary is built from — currently likely under-linked; add explicit links to each) |

### Schema

Keep existing `WebPage`/`BreadcrumbList`. Recommend a `TouristTrip` node (schema.org) listing the
seven `itinerary` sub-legs with `arrivalLocation`/`departureLocation` per day, matching the structured
`plan` array already in the YAML — this is additive, not a replacement for whatever itinerary schema
(if any) currently ships; confirm what's live before adding. Add `FAQPage` for the new Q&A block.

### Titles & meta descriptions (written)

**EN:** Keep the existing title, `7-Day Georgia Road Trip Itinerary | RentUp` (42 chars) — good. New
(correctly rendered, once the `{stops}` bug is fixed) meta:
`A 7-day, 1,020 km Georgia road trip from Mtskheta to Kutaisi — economy car all the way. Day-by-day plan, drive times and every stop linked.` (140 chars)

**KA:** `საქართველო 7 დღეში — გზამკვლევი | RentUp` — verify against the existing hand-written `name`
field's own phrasing rather than re-deriving. Meta: `7-დღიანი, 1,020 კმ-იანი მარშრუტი მცხეთიდან ქუთაისამდე — მთლიანად ეკონომ-კლასის მანქანით. დღიური გეგმა, გზაზე დროები და ყველა გაჩერება.`

**RU:** `Грузия за 7 дней: маршрут на 1020 км | RentUp`. Meta: `Недельный маршрут по Грузии от Мцхеты до Кутаиси, 1020 км — только на эконом-классе. План по дням, время в пути, все остановки.`

**fa/he/ar:** Per `CONTENT_STRATEGY.md §6.2`, itineraries are template-driven pages (numbers, place
names, day structure) — **worth building in all six**, near-zero marginal cost. The new "why economy
is enough" prose paragraph is the one piece of genuine long-form reasoning on this page; it can launch
ka/en/ru only and be added to fa/he/ar later if Search Console shows demand.

### Image requirements

- Zero images exist on itinerary pages today (`CONTENT_STRATEGY.md G5`: "Zero images on routes (0/32)
  and cars (0/17). All photography sits on attractions.") Add at least 3–4 stop photos by reusing the
  `gallery` images already licensed on the linked attraction pages (Jvari Monastery, Vardzia, Gelati
  Monastery are strong, well-photographed candidates per the corpus) — this is a template-level fix
  that benefits all 5 itineraries and 32 routes at once (per `CONTENT_STRATEGY.md` roadmap item 12),
  flag for the developer rather than treating as a one-page task.

### E-E-A-T signals genuinely available

- The route composes three already-published, verifiable routes (`route_slugs`) rather than being
  invented wholesale — state this ("built from three of our existing road-trip routes, in sequence")
  as a transparency signal.
- The "economy-rated for all seven days, the only one of the five itineraries that never needs an
  SUV" claim is genuinely checkable against the other four itinerary files — a specific, falsifiable
  claim rather than generic reassurance.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[againstthecompass.com/en/georgia-itinerary/](https://againstthecompass.com/en/georgia-itinerary/) ·
[tourradar.com/n/georgia-7-day](https://www.tourradar.com/n/georgia-7-day) (packaged tours, different
intent) · [adventuroustastes.com/7-day-georgia-itinerary/](https://www.adventuroustastes.com/7-day-georgia-itinerary/) ·
[nospaceinmypassport.com/7-day-georgia-itinerary...](https://nospaceinmypassport.com/7-day-georgia-itinerary-the-ultimate-guide-from-a-local/) ·
[georgia-roadtrip.com/7-days-itinerary/](https://georgia-roadtrip.com/7-days-itinerary/) — **note this
last one sells a *private-driver* 7-day product**, a direct signal that the driver-vs-self-drive
decision belongs near this content (reinforces the FAQ link to brief #9's with-driver page) ·
[vitistravel.com/.../7-days-in-georgia...](https://vitistravel.com/en/blogs/7-days-in-georgia-travel-itinerary-first-timers-2026).

### Do-not-claim list

- Do not publish corrected Day 2/6/7 km or drive-time figures invented for this brief — flag the
  data-accuracy issue (F-ITI-6) to the owner instead, per the hard rule against inventing facts.
- Do not claim the route is drivable in less than the stated 18:30 total drive time.
- Do not claim any stop's entry fee, hours or season beyond what its own `content/attractions/*.yml`
  record states.

---

# Brief 6 — `/car-rental/deposit/` (new) — the honest "no deposit" counter-page

## Why this page exists, and what it must not claim

`KEYWORD_CLUSTERS.md A16` documents `без залога` ("without deposit") as arguably the single most
competitive modifier in the Russian rental SERP for Georgia — and RentUp does not offer that product
(`rental_policy.yml: deposit.waiver_available: false`). This page's entire premise is answering the
query **honestly** rather than chasing it dishonestly, per the cluster's own strategy note.

**Verified, undisputed facts to build the page on** (all from `content/cars/*.yml` `deposit` field,
cross-checked against `rental_policy.yml`):

| Category | Cars | Deposit |
|---|---|---|
| economy | Prius, Elantra, Corolla | 300 ₾ |
| suv | RAV4, Tucson, Outlander | 600 ₾ |
| business | Camry, E-Class, BMW 5 | 1,000 ₾ |
| minivan | Vito, Alphard, Staria | 1,000 ₾ |
| van | Transit, Sprinter | 800 ₾ |
| offroad | Pajero, Delica, Prado | 1,200 ₾ |

`rental_policy.yml → deposit.released_days: 3` (working days after return) and
`deposit.cash_accepted: true` are both stated plainly in the policy file with no contradicting source
— **safe to publish without a verification caveat**.

**What is genuinely disputed and must carry the verification note:** `deposit.method: card_hold | cash
| either` in `rental_policy.yml` implies a genuine cash-only path exists, but `faq.yml`'s documents
answer states plainly *"a driving licence... and a card for the deposit"* — no mention of a cash
option at all. This is the single most important fact on this exact page (a Russian searcher looking
for `без залога` most plausibly means "without a card block," and if cash genuinely is *not* accepted
in practice despite the policy file saying it is, publishing the cash-accepted claim would create the
refund dispute `CONTENT_STRATEGY.md §1.5` warns about). **Confirm cash-as-deposit is a real, current
option with the owner before this page's headline differentiator goes live.**

## Brief

- **Target URL:** `/car-rental/deposit/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (ru):** `аренда авто без залога Грузия` — **secondary:** `прокат авто без депозита Тбилиси`, `аренда авто без банковской карты Грузия`, `какой залог при аренде авто в Грузии`, `когда возвращают залог аренда авто Грузия`
- **Primary (en):** `car rental georgia deposit amount` — **secondary:** `car rental georgia no deposit`, `how much deposit car rental georgia`, `car rental tbilisi no credit card`, `when is deposit refunded car rental georgia`
- **Primary (ka):** `მანქანის ქირაობის დეპოზიტი` — **secondary:** `მანქანის ქირაობა დეპოზიტის გარეშე`, `რამდენია დეპოზიტი მანქანის ქირაობისას`, `დეპოზიტის დაბრუნება`
- **Intent / funnel stage:** Policy / MOFU, but with unusually high commercial pull — per
  `KEYWORD_CLUSTERS.md A16`, "High" volume specifically in Russian, evidenced by multiple ranking
  pages putting `без залога` in their title tag ("operators only do that for queries that convert").
- **Audience & real question:** A renter (disproportionately Russian-speaking, per the cluster note)
  worried that a large card hold will block their available credit, or who does not have a card that
  will authorise a hold at all, asking "how much, and is there any way around it."
- **Target word count:** 1,000–1,300 words — this page should be short, exact and reassuring, not
  padded; a long page here reads as evasive on a query that wants a direct number.

### Outline

- **H1:** How the Rental Deposit Works (ka: `როგორ მუშაობს მანქანის ქირაობის დეპოზიტი` / ru: `Как работает залог при аренде авто`)
- **H2 — The honest answer first: there is no deposit-free option** — state
  `waiver_available: false` plainly, immediately, in the first paragraph — do not bury it. Follow
  immediately with the genuine differentiator: **[pending owner confirmation, see above]** cash is
  accepted as an alternative to a card hold, so a card with insufficient available credit does not
  block the booking outright.
- **H2 — Deposit by category** — the six-row table above.
- **H2 — How the hold works and when it's released** — `released_days: 3` (working days after return);
  explain in plain terms what a "hold" means for someone unfamiliar with the concept (a genuine gap:
  `terms.yml`/`faq.yml` assume the reader already knows).
- **H2 — What the deposit does *not* cover** — **verification-gated section**: this is where excess
  and CDW would normally be explained, but the excess figure (300–1,200 ₾ tiered per `faq.yml` vs. a
  flat 1,000 ₾ per `rental_policy.yml`) and CDW inclusion are disputed (§0.3). Write this section as a
  placeholder pointing to `/terms/` for now, with **"Verify against the reconciled policy before
  publishing — do not state an excess figure or CDW-inclusion claim on this page until §0.3 is
  resolved."**
- **H2 — Why we don't offer a deposit-free product** — a short, honest paragraph: a deposit protects
  against exactly the kind of damage the excess exists for; competitors advertising "no deposit"
  typically fold an equivalent cost into a mandatory insurance product instead (**do not name specific
  competitors or claim to know their pricing structure** — frame this generically).
- **H2 — FAQ**
  - "Do you offer car rental without a deposit?" — no, direct answer, `waiver_available: false`
  - "Can I pay the deposit in cash?" — **pending confirmation, see above**
  - "When do I get the deposit back?" — 3 working days after return
  - "Does the deposit amount change for a longer rental?" — no, same amount at any rental length
    (cross-reference brief #4's monthly page)

### Internal links to add

| Anchor text | Target |
|---|---|
| "full rental terms" | `/terms/` |
| "car rental in Georgia" (hub) | `/car-rental/` |
| "economy", "SUV", "business", "4x4" category deposit context | respective `/car-rental/{category}/` pages |
| "renting for a month?" | `/car-rental/monthly/` |
| "what else you'll need to rent" | `/car-rental/requirements/` |

### Schema

`WebPage` + `FAQPage`. No `Product`/`Offer` node needed — this page is policy explanation, not a
category listing.

### Titles & meta descriptions (written)

**RU** (lead language for this cluster): `Залог при аренде авто в Грузии — сколько и когда вернут | RentUp` (63 chars)
Meta: `Залог 300–1200 ₾ в зависимости от класса машины, возврат за 3 рабочих дня. Без депозита не сдаём — объясняем честно, почему.` (123 chars)

**EN:** `Car Rental Deposit in Georgia — How It Works | RentUp` (54 chars)
Meta: `Deposits run 300–1,200 ₾ depending on car class, released within 3 working days. We don't offer a no-deposit option — here's exactly why and how it works.` (156 chars)

**KA:** `მანქანის ქირაობის დეპოზიტი — როგორ მუშაობს | RentUp` (49 chars)
Meta: `დეპოზიტი 300–1200 ₾-მდე, კატეგორიის მიხედვით, უბრუნდებათ 3 სამუშაო დღეში. დეპოზიტის გარეშე არ ვმუშაობთ — გიხსნით რატომ.`

**fa/he/ar:** Commercial policy page touching a money term — build in all six per
`CONTENT_STRATEGY.md §6.2`'s "never withhold a money page" rule, even though the *cluster itself* is
overwhelmingly Russian-driven; an Arabic or Hebrew speaker asking the same question deserves the same
honest answer.

### Image requirements

- None required beyond the existing logo/header — this is a policy-explanation page; a simple
  deposit-by-category graphic (the six-row table rendered visually) would help scannability more than
  photography.

### E-E-A-T signals genuinely available

- Precision and honesty as the trust signal: stating the "no" plainly and immediately, rather than
  burying it under marketing language, is itself the differentiator `KEYWORD_CLUSTERS.md A16`
  identifies — competitors chasing the term dishonestly create exactly the refund disputes this page
  exists to avoid.
- The tiered deposit-by-category table is a genuine, checkable structure that most single-fleet
  competitors cannot show (`CONTENT_STRATEGY.md §4`: local operators publish 3–5 hand-written
  paragraphs, not a structured 17-car dataset).

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[autotbilisi.com/terms/](https://autotbilisi.com/terms/) ("Rent a car in Tbilisi without Deposit Без
Франшизы" — a direct competitor making exactly the no-deposit claim this brief deliberately does not
match) · [autotbilisi.ru](https://autotbilisi.ru/en/) ("Full insurance no excess") ·
[prokat-georgia.ru](https://prokat-georgia.ru/) · [in-trips.ru/blog/arenda-avto-gruziya.html](https://in-trips.ru/blog/arenda-avto-gruziya.html) —
matches `KEYWORD_CLUSTERS.md §1.3`'s observation that Russian "for Russians"/payment-friction content
is dominated by **editorial** sites (vc.ru, dtf.ru, in-trips.ru) rather than operators, confirming this
cluster is winnable by a page that actually answers the question rather than restating a sales pitch.

### Do-not-claim list

- Do not claim a no-deposit or zero-excess product exists in any form.
- Do not state an excess figure or CDW inclusion — gated on §0.3.
- Do not claim cash is accepted as a deposit method until the owner confirms it in practice, not just
  in the policy file (see the flag above).
- Do not name or characterise specific competitors' terms.

---

# Brief 7 — `/car-rental/business/` (new) — completes the category set

## The data behind it

Three cars carry `category: business` in `content/cars/*.yml`, all confirmed:

| Car | Seats | Luggage | Clearance | Drive | Fuel /100km | 1–6 days | 7–29 days | 30+ days | Deposit |
|---|---|---|---|---|---|---|---|---|---|
| Toyota Camry (hybrid) | 5 | 3 | 145 mm | fwd | 5.5 l | 210 ₾ | 189 ₾ | 158 ₾ | 1,000 ₾ |
| Mercedes-Benz E-Class | 5 | 3 | 130 mm | rwd | 6.2 l | 290 ₾ | 261 ₾ | 218 ₾ | 1,000 ₾ |
| BMW 5 Series | 5 | 3 | 135 mm | rwd | 7.5 l | 310 ₾ | 279 ₾ | 232 ₾ | 1,000 ₾ |

Per `KEYWORD_CLUSTERS.md A12`, `fleet.yml` already states these cars are "available with a driver if
required" — a direct, ready-made cross-link to brief #9. This category currently has data and no page
(`content/settings/categories.yml` lists `business` as one of six categories; `SEO_URL_MAP.md` marks it
"deferred until data exists — the data now exists" per `KEYWORD_CLUSTERS.md A12`).

## Brief

- **Target URL:** `/car-rental/business/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `business car rental tbilisi` — **secondary:** `executive car rental georgia`, `mercedes e class rental tbilisi`, `bmw rental georgia`, `car rental for business trip tbilisi`, `airport transfer mercedes tbilisi`
- **Primary (ka):** `ბიზნეს კლასის მანქანის ქირაობა` — **secondary:** `მერსედესის ქირაობა თბილისში`, `BMW-ს ქირაობა`, `კორპორატიული მანქანის ქირაობა`
- **Primary (ru):** `аренда авто бизнес класса Тбилиси` — **secondary:** `аренда Мерседес Е класса Грузия`, `аренда BMW Тбилиси`, `корпоративная аренда авто Грузия`
- **Intent / funnel stage:** Transactional / BOFU, high ticket — per `KEYWORD_CLUSTERS.md A12`, "Low"
  competition among Georgian operators specifically for a *rental* (as opposed to chauffeur) business
  page, and the highest per-day rate in the fleet.
- **Audience & real question:** A business traveller or someone arranging transport for a client asking
  "what's the actual car, and can I self-drive it or do I need a driver" — this audience cross-shops
  against chauffeur services, not just other rental categories.
- **Target word count:** 900–1,100 words — this is a small, high-value category page; match the
  existing `/car-rental/4x4/` category page's shape (629 words, per `ONPAGE_REVIEW.md §4`) rather than
  over-writing it.

### Outline

- **H1:** Business Class Car Rental in Georgia (ka: `ბიზნეს კლასის მანქანის ქირაობა საქართველოში` / ru: `Аренда авто бизнес-класса в Грузии`)
- **H2 — The three cars** — spec cards for Camry, E-Class, BMW 5, each with seats/luggage/clearance/
  fuel/price, mirroring the existing category-page card pattern.
- **H2 — Self-drive or with a driver** — direct, honest cross-link: "all three business cars are also
  available with a professional driver" → `/car-rental/with-driver/` (brief #9). This is the single
  most important internal link on this page — it turns a category page into a two-way funnel instead
  of a dead end.
- **H2 — What this class is for** — airport transfers for a client, a multi-day business trip needing
  a comfortable long-drive car (BMW 5 and E-Class are both rwd, note this is *not* a mountain-road
  car — clearance 130–145 mm is the lowest range in the fleet alongside economy — link honestly to the
  4x4 guide's "which category to book" section rather than overselling capability this class doesn't
  have).
- **H2 — Pricing** — the three-tier table (1–6 / 7–29 / 30+ days) for all three cars.
- **H2 — FAQ**
  - "Can I get one of these with a driver?" — yes, link out
  - "Are these cars good for a mountain day trip?" — no, lowest clearance in the fleet; link to the
    4x4 guide
  - "What's included in the price?" — **verification-gated**: do not state CDW/excess specifics here,
    link to `/terms/` and/or the deposit page instead

### Internal links to add

| Anchor text | Target |
|---|---|
| "book one with a driver" | `/car-rental/with-driver/` |
| "Toyota Camry", "Mercedes-Benz E-Class", "BMW 5 Series" | `/fleet/toyota-camry/`, `/fleet/mercedes-benz-e-class/`, `/fleet/bmw-5-series/` |
| "is a 4x4 what you actually need?" | `/guides/do-i-need-a-4x4-in-georgia/` |
| "car rental in Georgia" (hub) | `/car-rental/` |
| "deposit and terms" | `/car-rental/deposit/` |

### Schema

`Product`/`Offer` node per car, matching the pattern already used on other category pages
(`ONPAGE_REVIEW.md F-VEH-2` confirms this node type is in use). Add `FAQPage`.

### Titles & meta descriptions (written)

**EN:** `Business Class Car Rental in Georgia — from 210 ₾/day | RentUp` (62 chars)
Meta: `Camry, E-Class or BMW 5 Series — self-drive or with a driver. Business-class car rental in Tbilisi from 210 ₾/day, all-inclusive pricing shown.` (145 chars)

**KA:** `ბიზნეს კლასის მანქანის ქირაობა — 210 ₾-დან | RentUp` (49 chars)
Meta: `Camry, E-Class ან BMW 5 — მძღოლით ან თავად. ბიზნეს კლასის მანქანის ქირაობა თბილისში 210 ₾-დან.`

**RU:** `Аренда авто бизнес-класса в Грузии — от 210 ₾/день | RentUp` (56 chars)
Meta: `Camry, E-Class или BMW 5 — с водителем или без. Аренда авто бизнес-класса в Тбилиси от 210 ₾/день, цены полностью открыты.`

**fa/he/ar:** Yes — commercial money page, one of the "always all six" per `CONTENT_STRATEGY.md §6.2`.

### Image requirements

- Photo per car (`c["image"]` field — apply the same fix as briefs #2 and #4). Business-class buyers
  are more image-sensitive than budget renters; this category page benefits most from the fleet-photo
  fix across the whole site.

### E-E-A-T signals genuinely available

- Genuine self-drive-or-driver flexibility on the same three cars, confirmed in `fleet.yml` — a real
  structural advantage over pure chauffeur services, which don't rent self-drive, and pure rental
  agencies, which mostly don't offer a driver.
- Exact, transparent pricing where several competitors in this space (see below) require a quote
  request — publishing the number is the differentiator.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[rentalauto.ge/luxury-car-rental-tbilisi/](https://rentalauto.ge/luxury-car-rental-tbilisi/) (Mercedes
S550) · [dw-auto.ge/en/rent/tbilisi/premium-car](https://dw-auto.ge/en/rent/tbilisi/premium-car) ·
[unitedcarsrent.com/cars/business](https://unitedcarsrent.com/cars/business) (direct-match category
name) · [autobiography.rent/en/](https://autobiography.rent/en/) (Jaguar/Audi/BMW/Range Rover) ·
[ex-cars.com/en/premium-cars-for-rent](https://ex-cars.com/en/premium-cars-for-rent) ·
[bestbusgeorgia.com/auto/vip-car-rental-tbilisi/](https://bestbusgeorgia.com/auto/vip-car-rental-tbilisi/)
(Maybach S-Class with chauffeur — signals this SERP skews toward luxury-with-driver, reinforcing the
brief's cross-link to `/car-rental/with-driver/`).

### Do-not-claim list

- Do not claim these cars are suitable for gravel, mountain or 4x4-rated roads — clearance data says
  otherwise (130–145 mm, the lowest range alongside economy).
- Do not state an excess/CDW figure — gated on §0.3.
- Do not claim a fleet size within this category beyond three named cars.
- Do not claim same-day driver availability without the owner confirming lead time — not in any source
  file.

---

# Brief 8 — `/car-rental/one-way/` (new)

## The data behind it

`rental_policy.yml → one_way.available: true`, `fee_gel: 100` — a single flat fee regardless of city
pair. Six served pickup points (`places.yml`: tbilisi, tbilisi-airport, kutaisi, kutaisi-airport,
batumi, batumi-airport) support up to 30 ordered city-pair combinations. Per `KEYWORD_CLUSTERS.md A21`,
present these as **one small matrix, not 30 URLs** — the URL map explicitly rejects
`/car-rental/{37 cities}/`-style doorway proliferation, and a one-way matrix page is exactly the
pattern that guardrail exists to prevent from recurring at the route-pair level.

## Brief

- **Target URL:** `/car-rental/one-way/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `one way car rental georgia` — **secondary:** `car rental kutaisi airport drop off tbilisi`, `one way car hire tbilisi to batumi`, `car rental georgia different drop off`, `one way rental fee georgia`
- **Primary (ka):** `ცალმხრივი მანქანის ქირაობა` — **secondary:** `მანქანის ქირაობა თბილისში აღება ბათუმში დაბრუნება`
- **Primary (ru):** `аренда авто в один конец Грузия` — **secondary:** `взять авто в Тбилиси сдать в Батуми`, `аренда авто Кутаиси аэропорт сдать в Тбилиси`, `доплата за возврат в другом городе Грузия`
- **Intent / funnel stage:** Transactional / BOFU — per `KEYWORD_CLUSTERS.md A21`, "fly-into-Kutaisi /
  fly-out-of-Tbilisi is a common Georgia itinerary shape... the query has almost no purpose-built
  competition" in the local operator market (though see competitors below — two Georgian operators do
  have dedicated pages, so "almost no" needs revising to "thin but not zero").
- **Audience & real question:** Someone whose flights land in one city and depart from another (the
  KUT-in/TBS-out shape is the most common per the cluster note) asking "can I actually do this, and
  what does it cost."
- **Target word count:** 700–900 words — a small, matrix-driven page; the value is in the table, not
  the prose.

### Outline

- **H1:** One-Way Car Rental in Georgia (ka: `ცალმხრივი მანქანის ქირაობა საქართველოში` / ru: `Аренда авто в Грузии в один конец`)
- **H2 — The fee, stated once** — 100 ₾, flat, between any two of the six served pickup points — no
  hidden per-distance calculation.
- **H2 — The six pickup points, and the common combinations** — a small matrix table (6×6, minus the
  diagonal = 30 cells, but render as a simple readable table, not 30 separate rows of prose) with the
  three or four most likely real combinations called out by name: Kutaisi Airport → Tbilisi,
  Tbilisi → Batumi, Batumi Airport → Kutaisi Airport, Tbilisi Airport → Batumi.
- **H2 — Why Kutaisi-in / Tbilisi-out (or the reverse) is the most common shape** — ties to the
  low-cost-carrier pattern already noted for Kutaisi Airport in `KEYWORD_CLUSTERS.md A5` (Wizz Air
  gateway) — a genuine, sourced reason rather than a generic claim.
- **H2 — How to book a one-way rental** — practical: request it at booking time, confirm the drop-off
  city, the 100 ₾ fee is added to the quote.
- **H2 — FAQ**
  - "Does the fee depend on distance?" — no, flat 100 ₾ regardless of which two served cities
  - "Can I drop off somewhere not on the list?" — no, only the six served pickup points, per
    `SEO_URL_MAP.md`'s doorway-page guardrail — do not imply broader coverage
  - "Is one-way available on every car?" — **verify with the owner**: no field in `content/cars/*.yml`
    restricts one-way by category, so the default assumption is yes for all 17, but this should be
    confirmed rather than assumed silently

### Internal links to add

| Anchor text | Target |
|---|---|
| "Tbilisi Airport pickup" | `/car-rental/tbilisi-airport/` |
| "Kutaisi Airport pickup" | `/car-rental/kutaisi-airport/` |
| "Batumi Airport pickup" | `/car-rental/batumi-airport/` |
| "Tbilisi", "Kutaisi", "Batumi" city pickup pages | `/car-rental/tbilisi/`, `/car-rental/kutaisi/`, `/car-rental/batumi/` |
| "car rental in Georgia" (hub) | `/car-rental/` |
| "renting for a month?" | `/car-rental/monthly/` |

**Cannibalisation guard (per `KEYWORD_CLUSTERS.md A21`):** the six location pages (briefs already
covering `tbilisi-airport`; the other five exist per `SEO_URL_MAP.md`) currently each mention one-way
in their own FAQ. Once this page ships, each location page's one-way mention should **link here rather
than restate the fee or the matrix** — flag this as a required edit to the five other location pages
alongside brief #3's airport rewrite, not a new task, to avoid four-to-six pages competing for the same
query.

### Schema

`WebPage` + `FAQPage`. No `Product` node — this is a fee/policy page, not a vehicle listing.

### Titles & meta descriptions (written)

**EN:** `One-Way Car Rental in Georgia — 100 ₾ Between Cities | RentUp` (61 chars)
Meta: `Pick up in one city, drop off in another — flat 100 ₾ fee between Tbilisi, Kutaisi and Batumi (city or airport). See the full route matrix.` (140 chars)

**KA:** `ცალმხრივი მანქანის ქირაობა — 100 ₾ | RentUp` (43 chars)
Meta: `აიღეთ ერთ ქალაქში, დააბრუნეთ მეორეში — 100 ₾ საფასური თბილისს, ქუთაისსა და ბათუმს შორის (ქალაქი ან აეროპორტი).`

**RU:** `Аренда авто в один конец в Грузии — 100 ₾ | RentUp` (49 chars)
Meta: `Забрать в одном городе, сдать в другом — доплата 100 ₾ между Тбилиси, Кутаиси и Батуми (город или аэропорт). Полная таблица маршрутов.`

**fa/he/ar:** Yes — commercial money page, always-all-six per `CONTENT_STRATEGY.md §6.2`.

### Image requirements

- None required — a well-formatted matrix table is the entire value of this page.

### E-E-A-T signals genuinely available

- A single flat fee (not a distance-based calculator or "contact us for a quote") is itself the
  differentiator against operators whose one-way pricing is opaque — publish it plainly.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[gurosun.ge/one-way-car-rental-in-georgia/](https://gurosun.ge/one-way-car-rental-in-georgia/) (a
dedicated guide page — the strongest direct content competitor found) ·
[starcar.ge/blog/one-way-car-rentals-in-georgia](https://starcar.ge/blog/one-way-car-rentals-in-georgia)
(also dedicated) · [en.geodrive.info/one_way_en](https://en.geodrive.info/one_way_en) (dedicated
tariff page) — **this revises the cluster note's "almost no purpose-built competition" to "thin but
real": three Georgian operators already have a dedicated page for this exact intent**, so this brief's
differentiator must be the matrix format and flat, stated fee, not "we're the only ones who built
this."

### Do-not-claim list

- Do not imply one-way is available to any pickup point beyond the six served places.
- Do not state a distance-based or city-pair-specific fee — it is flat 100 ₾, and inventing tiered
  pricing would contradict `rental_policy.yml`.
- Do not claim same-day availability at the drop-off city without the owner confirming operational
  capacity.

---

# Brief 9 — `/car-rental/with-driver/` (new)

## The data behind it

`content/pages/faq.yml` (Georgian, confirmed at line ~217): "Yes, for 20 GEL per day, up to two
additional drivers" — **this is the *additional-driver* fee, not the with-driver-service rate; do not
conflate the two.** The actual with-driver product rate comes from `KEYWORD_CLUSTERS.md A23`'s own
research note: **120 ₾/day (8-hour day) + 20 ₾/hour overtime** — verify this figure directly against
`content/pages/faq.yml` or a dedicated pricing field before publishing; it was not independently
re-confirmed inside `content/cars/*.yml` in this brief's own research pass (no `driver_fee` field
exists on any car file), so **treat the 120 ₾/day figure as needing owner confirmation, not as a
verified repo fact**, and mark it accordingly on the page until confirmed. `fleet.yml` states the three
business-class cars are "available with a driver if required" (`KEYWORD_CLUSTERS.md A12`) — this part
*is* directly sourced. 32 routes (`content/routes/*.yml`) already carry drive times that a with-driver
customer would want quoted against the daily rate.

## Brief

- **Target URL:** `/car-rental/with-driver/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `car rental with driver georgia` — **secondary:** `hire a driver in georgia`, `private driver tbilisi`, `chauffeur service georgia`, `car with driver tbilisi airport`
- **Primary (ka):** `მძღოლიანი მანქანის ქირაობა` — **secondary:** `მძღოლის დაქირავება საქართველოში`
- **Primary (ru):** `аренда авто с водителем Грузия` — **secondary:** `частный водитель Тбилиси`, `автомобиль с водителем Грузия`
- **Intent / funnel stage:** Transactional / BOFU, but a **different customer**, not a rental variant
  — per `KEYWORD_CLUSTERS.md A23`, "a natural conversion for everyone who reads [the 4x4 guide] and
  decides not to drive it themselves."
- **Audience & real question:** Travellers uncomfortable driving Georgian mountain roads themselves
  (a direct downstream audience from brief #1's 4x4 guide), business travellers wanting airport
  transfers without renting, and older or first-time-abroad visitors who want the routes without the
  driving.
- **Target word count:** 900–1,100 words.

### Outline

- **H1:** Car Rental with a Driver in Georgia (ka: `მძღოლიანი მანქანის ქირაობა საქართველოში` / ru: `Аренда авто с водителем в Грузии`)
- **H2 — How it works** — **[rate pending owner confirmation, see above]** state the day-length
  structure (8-hour day, overtime hourly) once confirmed; do not publish an unconfirmed number.
- **H2 — Which cars come with a driver** — lead with the three confirmed business-class cars
  (`fleet.yml`), and ask the owner whether SUV/4x4 categories are also offered with a driver for
  mountain routes — a very plausible pairing with brief #1's audience, but **not yet confirmed in any
  source file; do not assume it**.
- **H2 — Good for: airport transfers, mountain routes, and evenings out** — link the mountain-route
  case directly to `/guides/do-i-need-a-4x4-in-georgia/`'s worked examples (Ushguli, Abano Pass, Omalo)
  as the natural "or hire someone who already knows this road" alternative.
- **H2 — Popular routes people book with a driver** — pull 3–4 of the 32 routes with real drive times
  (e.g. `/routes/military-highway-kazbegi/`, `/routes/svaneti-expedition/`) as concrete, bookable
  examples rather than an abstract pitch.
- **H2 — FAQ**
  - "What's included in the driver rate?" — **owner to confirm exact inclusions**
  - "Can I get a driver for just the airport transfer?" — likely yes, confirm with owner
  - "Do drivers speak English?" — `rental_policy.yml → support.languages: [ka, en, ru]` — a genuine,
    sourced answer, though note this is the *support* language list, not necessarily a confirmed
    driver-language guarantee; flag the distinction to the owner rather than assuming they're identical

### Internal links to add

| Anchor text | Target |
|---|---|
| "do you need a 4x4, or a driver who already knows the road?" | `/guides/do-i-need-a-4x4-in-georgia/` |
| "business-class cars" | `/car-rental/business/` (brief #7) |
| named routes (3–4) | `/routes/military-highway-kazbegi/`, `/routes/svaneti-expedition/`, 2 more |
| "self-drive rental instead" | `/car-rental/` |
| "airport pickup" | `/car-rental/tbilisi-airport/` |

### Schema

`WebPage` + a `Service` node (schema.org/Service, `serviceType: "Chauffeur-driven car rental"`) +
`FAQPage`. This is the one page in this batch that is not primarily a vehicle-rental product, so it
should not force-fit a `Product`/`Offer` node the way the category pages do.

### Titles & meta descriptions (written)

**EN:** `Car Rental with a Driver in Georgia | RentUp` (44 chars)
Meta: `Skip the mountain roads and let someone who knows them drive. Chauffeured cars for airport transfers, city days and multi-day routes across Georgia.` (152 chars — note: no price stated pending confirmation)

**KA:** `მძღოლიანი მანქანის ქირაობა საქართველოში | RentUp` (48 chars)
Meta: `გამოტოვეთ მთის სერპანტინები — მიანდეთ საქმე მძღოლს, ვინც იცნობს გზას. აეროპორტის ტრანსფერი, ერთდღიანი და მრავალდღიანი მარშრუტები.`

**RU:** `Аренда авто с водителем в Грузии | RentUp` (41 chars)
Meta: `Доверьте горные серпантины водителю, который их знает. Трансфер из аэропорта, однодневные и многодневные маршруты по Грузии с водителем.`

**fa/he/ar:** Yes — commercial money page, always-all-six per `CONTENT_STRATEGY.md §6.2`.

### Image requirements

- Photos of the business-class cars (reuse `c["image"]`, same fix as brief #7).
- No stock "chauffeur" imagery — if a real photo of a RentUp driver/car pairing exists, use it; if not,
  do not fabricate a scene implying a service detail (a specific driver, uniform, etc.) not confirmed
  by the owner.

### E-E-A-T signals genuinely available

- The direct link from a data-driven decision page (brief #1) to a driver option is a genuine product
  logic, not marketing framing — the site's own 257-place road classification is what makes "you might
  prefer a driver for these 37 places" a credible, specific recommendation rather than a generic upsell.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[expathub.ge/how-to-rent-a-car-or-private-driver-in-georgia-country/](https://expathub.ge/how-to-rent-a-car-or-private-driver-in-georgia-country/) ·
[dw-auto.ge/en/rent/tbilisi/car-with-driver](https://dw-auto.ge/en/rent/tbilisi/car-with-driver) ·
[og.ge/services/rental-with-driver](https://og.ge/services/rental-with-driver) ·
[fstarentcar.com/car-rental-with-driver/](https://fstarentcar.com/car-rental-with-driver/) ·
[georgia-roadtrip.com](https://georgia-roadtrip.com/7-days-itinerary/) (a private-driver-first
itinerary operator — direct positioning competitor, not just a feature page) ·
[viator.com/.../Private-Drivers](https://www.viator.com/Tbilisi-tours/Private-Drivers/d22516-g15-c32762)
(marketplace, different business model but competes for the same query).

### Do-not-claim list

- Do not publish the 120 ₾/day or 20 ₾/hour rate, or any rate, without owner confirmation — not
  independently verified in `content/cars/*.yml` or `rental_policy.yml` during this brief's research.
- Do not claim SUV/4x4 categories are available with a driver unless confirmed — only business-class
  cars are sourced (`fleet.yml`).
- Do not claim a specific driver-language guarantee beyond the general `support.languages` list, and
  flag to the owner that these may not be identical facts.
- Do not claim availability at all six pickup points without confirmation — `fleet.yml`'s note is
  fleet-scoped, not location-scoped.

---

# Brief 10 — `/car-rental/requirements/` (new)

## The data behind it, and a genuine new conflict found during this brief's research

Undisputed, from `rental_policy.yml`: `min_driver_age: 21`, `min_licence_years: 2`,
`licence_accepted: [national, idp]`, `passport_required: true`.

**A material conflict beyond the I1–I3 list already logged in `CONTENT_STRATEGY.md`:**
`rental_policy.yml` states flat `min_driver_age: 21` with **no young-driver surcharge field at all**
(silent, not "none"). `KEYWORD_CLUSTERS.md A18` characterises the data as "no young-driver surcharge" —
but `content/pages/terms.yml` explicitly publishes a tiered surcharge table (15 ₾/day for ages 23–25,
25 ₾/day for ages 25–27), and — independently, and more importantly — **the live booking widget's own
config, `FH_CFG.youngDriver` (rendered in a `<script>` tag on every page, confirmed directly in
`dist/car-rental/tbilisi-airport/index.html`), states `{"underAge": 27, "minGel": 15, "maxGel": 25}`
and is the object the booking form actually uses to calculate a quote.** In other words: two
independent live sources (`terms.yml` and the production booking JS) agree with each other and
disagree with `rental_policy.yml`'s silence/implicit "no surcharge" reading. **This means the surcharge
is very likely real and currently charged — `rental_policy.yml` is the outlier here, by omission, not
`terms.yml`.** This is exactly the kind of finding the reconciliation effort (`CONTENT_STRATEGY.md §7,
Q0`) needs surfaced; flag it to whoever owns that reconciliation rather than resolving it unilaterally
in this brief.

## Brief

- **Target URL:** `/car-rental/requirements/` (+ `/ka/`, `/ru/`, `/fa/`, `/he/`, `/ar/`)
- **Primary (en):** `car rental georgia age limit` — **secondary:** `minimum age to rent a car in georgia`, `do i need an idp in georgia`, `documents to rent a car in georgia`, `can i rent a car in georgia at 21`, `young driver surcharge georgia`
- **Primary (ru):** `со скольки лет можно арендовать авто в Грузии` — **secondary:** `какие документы нужны для аренды авто в Грузии`, `нужны ли международные права в Грузии`, `аренда авто в Грузии с российскими правами`, `водительский стаж аренда авто Грузия`
- **Primary (ka):** `მართვის მოწმობა მანქანის ქირაობისთვის` — **secondary:** `რამდენი წლიდან შეიძლება მანქანის ქირაობა`, `საერთაშორისო მართვის მოწმობა საქართველოში`
- **Intent / funnel stage:** Qualifying / MOFU — a pre-booking blocker question per
  `KEYWORD_CLUSTERS.md A18`, "the question every first-time renter asks."
- **Audience & real question:** Two overlapping audiences: (1) any first-time renter checking they're
  eligible before they plan further, and (2) per the cluster note, a distinct and currently
  editorial-owned Russian sub-cluster (`для россиян`) driven by post-2022 documentation/payment
  friction — licence format, whether an IDP is needed, what happens if a card won't authorise.
- **Target word count:** 1,200–1,500 words — this page absorbs content currently split across
  `/car-rental/`, `/faq/` and `/terms/` with different numbers (per `KEYWORD_CLUSTERS.md A18`'s own
  framing of the problem), so it needs enough room to be the single canonical answer.

### Outline

- **H1:** What You Need to Rent a Car in Georgia (ka: `რა გჭირდებათ მანქანის ქირაობისთვის საქართველოში` / ru: `Что нужно, чтобы арендовать авto в Грузии`)
- **H2 — The basics** — passport or ID, driving licence held ≥2 years, minimum age 21
  (`rental_policy.yml`, undisputed).
- **H2 — Do you need an International Driving Permit (IDP)?** — only if the national licence is not in
  Latin script (`terms.yml`'s own framing, consistent across languages, not disputed) — EU/US/most
  Latin-script licences do not need one; a licence in Georgian, Cyrillic, Arabic, Chinese, etc. does.
- **H2 — Renters under 27** — **this section must be resolved before publishing, not written around
  the conflict**: state either the confirmed surcharge (15–25 ₾/day, ages 23–27, per `terms.yml` and
  the live booking config) or omit the section entirely pending reconciliation — **do not publish "no
  young-driver surcharge" language, since that appears to be the less-supported of the two positions
  based on this brief's own research** (see the conflict box above).
- **H2 — Renters with a licence in a non-Latin script** (the `для россиян` sub-cluster, addressed
  honestly rather than as a special "for Russians" section — frame it by licence format, which serves
  every non-Latin-script nationality, not just one) — IDP requirement, restated from above with the
  specific practical detail of what "Latin script" checking looks like at pickup.
- **H2 — Payment and the deposit** — link out to `/car-rental/deposit/` (brief #6) rather than
  restating deposit mechanics here; this page should answer "what documents/eligibility," not
  duplicate the deposit page.
- **H2 — FAQ**
  - "What's the minimum age to rent a car in Georgia?" — 21
  - "Do I need an International Driving Permit?" — only if the licence isn't in Latin script
  - "Is there a surcharge for young drivers?" — **[resolve per the conflict box before publishing]**
  - "Can I rent with a licence from [country]?" — general Latin-script rule, not a country-by-country
    list (no such list exists in any source file — do not invent one)
  - "What if my card won't authorise the deposit hold?" — link to `/car-rental/deposit/`

### Internal links to add

| Anchor text | Target |
|---|---|
| "how the deposit works" | `/car-rental/deposit/` (brief #6) |
| "car rental in Georgia" (hub) | `/car-rental/` |
| "full rental terms" | `/terms/` |
| "renting with a driver instead" | `/car-rental/with-driver/` (brief #9 — a genuine alternative for someone who cannot meet the licence requirements) |
| "monthly rental" | `/car-rental/monthly/` |

### Schema

`WebPage` + `FAQPage` (this page is almost entirely FAQ-shaped; lean into it — an `FAQPage` node with
6–8 well-formed Q&As is the strongest schema opportunity in this entire batch for earning a rich
result).

### Titles & meta descriptions (written)

**EN:** `Car Rental Requirements in Georgia — Age, Licence, IDP | RentUp` (63 chars)
Meta: `Minimum age 21, licence held 2+ years, IDP only if your licence isn't in Latin script. Everything you need to check before booking a car in Georgia.` (152 chars)

**RU** (the priority language for this cluster per `KEYWORD_CLUSTERS.md A18`): `Требования для аренды авто в Грузии — возраст, права | RentUp` (61 chars)
Meta: `Минимальный возраст 21 год, стаж от 2 лет, международные права нужны только если ваши — не латиницей. Полный список требований перед бронированием.` (150 chars)

**KA:** `მანქანის ქირაობის მოთხოვნები საქართველოში | RentUp` (47 chars)
Meta: `მინიმალური ასაკი 21 წელი, მართვის სტაჟი 2+ წელი, IDP საჭიროა მხოლოდ არა-ლათინური მოწმობისთვის. ყველაფერი ჯავშნამდე შესამოწმებლად.`

**fa/he/ar:** Yes — this is exactly the kind of qualifying/eligibility content that serves fa/he/ar
readers well with minimal prose (a short, factual eligibility checklist translates cleanly and cheaply
per `CONTENT_STRATEGY.md §6.2`'s template-vs-prose cost logic) even though it isn't one of the three
named "always all six" exceptions — recommend building it in all six from day one rather than waiting
for a Search Console trigger, given how low the marginal translation cost is for a checklist-shaped
page.

### Image requirements

- None required — an eligibility checklist page does not need photography; a simple icon-based
  checklist (passport / licence / card) would aid scannability more than any photo.

### E-E-A-T signals genuinely available

- A direct, sourced answer to "what counts as a Latin-script licence" is more useful and more
  trustworthy than the vaguer "check with your rental company" language most competitor pages use —
  state the rule mechanically (does your licence use the Latin alphabet, yes/no) rather than by country
  list, since no country list exists in the source data and a country list would risk being wrong or
  incomplete for the many nationalities that actually rent.

### Competitors currently ranking (verified via WebSearch, 2026-08-30)

[werent.ge/en/blog/who-can-rent-a-car-in-georgia](https://werent.ge/en/blog/who-can-rent-a-car-in-georgia)
("Who Can Rent a Car in Georgia? Age, License and the IDP Question, Answered for 2026" — closest direct
title/intent match found) · [starcar.ge/blog/how-old-do-you-have-to-be-to-rent-a-car-in-georgia](https://starcar.ge/blog/how-old-do-you-have-to-be-to-rent-a-car-in-georgia) ·
[saadatrent.com/english/georgia/required-documents](https://www.saadatrent.com/english/georgia/required-documents) ·
[og.ge/blog/renting-car-in-georgia](https://og.ge/blog/renting-car-in-georgia) ·
[unitedcarsrent.com/blog/car-rental-rules](https://unitedcarsrent.com/blog/car-rental-rules) ·
[carrentgeorgia.com/en/faq/](https://carrentgeorgia.com/en/faq/) — matches `KEYWORD_CLUSTERS.md A18`'s
assessment that this is "mostly blog/editorial competition," which is winnable with a page that states
numbers plainly rather than hedging.

### Do-not-claim list

- Do not publish a "no young-driver surcharge" claim, and do not publish the 15–25 ₾ figures either,
  until the conflict identified in this brief is resolved by whoever owns `rental_policy.yml`
  reconciliation — this is the one section of this entire batch that should not ship on the current
  schedule without that sign-off, because the page's own credibility depends on stating the true
  number.
- Do not publish a country-by-country licence acceptance list — no such list exists in any source
  file; the mechanical Latin-script rule is the only sourced rule.
- Do not claim cross-border driving is possible with any documentation — `cross_border.allowed: false`
  per `rental_policy.yml`, disputed by `terms.yml` (§0.3) — if this page mentions cross-border at all,
  link to `/terms/` rather than restating either version.

---

## Appendix — verification checklist before any of these ten pages ships

1. Confirm `build.py`'s `seo_meta()`/`meta_title` precedence bug (F-HUB-1) is fixed before publishing
   brief #2's titles — otherwise the hand-written copy in this brief will be silently discarded again.
2. Confirm the itinerary `{stops}` interpolation bug (F-ITI-1) is fixed before publishing brief #5's
   meta description.
3. Get the Day 2 / Day 6 / Day 7 km-and-drive-time data in `content/itineraries/georgia-7-days.yml`
   corrected or removed (F-ITI-6) before writing new day-by-day prose for brief #5.
4. Resolve the `rental_policy.yml` / `faq.yml` / `terms.yml` / `llms.txt` conflicts logged in
   `CONTENT_STRATEGY.md §1.5` (I1–I3) **and** the two additional conflicts this batch surfaced
   independently — the cash-as-deposit-method question (brief #6) and the young-driver surcharge
   omission (brief #10) — before publishing any section flagged "verify against the reconciled policy"
   above.
5. Get an owner-confirmed with-driver day rate before publishing brief #9 — no rate is verified in
   `content/`.
6. Decide the `/guides/` vs. `/driving-in-georgia/` URL-prefix question (§0.4) and add the winner to
   `SEO_URL_MAP.md` before brief #1 ships, so a second guide page in this space doesn't fork the
   information architecture.
