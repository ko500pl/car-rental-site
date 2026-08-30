# AI Visibility Report: RentUp (რენტაპი) — rentup.ge

**Generative Engine Optimization (GEO) audit**
Date: 2026-08-29 · Scope: `dist/` (2 137 pages), `content/`, `build.py`, `theme.py` · Domain: https://rentup.ge
Category: car rental in Georgia (the country) + Georgia road-trip planning
Method: static analysis of the built site + web research on how the answer space is currently served. **No production file was changed.**

> **Read this first.** RentUp's *content* is far better than its *AI visibility*. The site holds one of the best structured travel-and-rental datasets in the Georgian market (257 attractions with road grade, required car category, drive time and season; 32 routes; 5 itineraries; 17 vehicles with real prices and deposits). Almost none of that is currently reachable, citable, or internally consistent enough for an answer engine to quote it safely. Two of the three fixes with the highest impact are **data-consistency fixes, not content production.**

---

## 1. Current Visibility Score: **27 / 100**

| Dimension | Score (0–10) | Reasoning |
|---|---|---|
| **Presence** | **1** | A web search for `rentup.ge car rental Georgia` returns *zero* RentUp results — the SERP is entirely US-state-of-Georgia aggregators (Kayak, Expedia, Enterprise, Turo) plus Localrent. No third-party citation, no directory listing, no review-platform profile, no Reddit/forum mention was found. AI assistants cite what other sites say about you; nothing says anything about RentUp. |
| **Accuracy** | **3** | On-page facts are unusually specific and sourced from YAML — but the site contradicts itself on nearly every commercial term (§4). Worse, the `AutoRental` JSON-LD emitted on all 2 137 pages claims *"full insurance coverage"*, which `/car-rental/` explicitly disclaims. An assistant that quotes RentUp today has a ~50 % chance of quoting a term RentUp does not offer. |
| **Sentiment** | **5** | Neutral by absence. No negative signal exists (no complaint threads, no scam-warning posts — genuinely good), but no positive signal exists either. Neutral-by-absence is the default score, not an achievement. |
| **Position** | **0** | Never appears in any answer for any target prompt. The answer space is owned by independent travel blogs (wander-lush.org, goingthewholehogg.com, againstthecompass.com) and by aggregators (Localrent, Discover Cars, Skyscanner). |
| **Completeness** | **6** | Where content exists, it is *unusually* complete — `/car-rental/4x4/` names the exact roads that require 4x4 and the exact routes, `/attractions/ushguli/` gives road grade + required category + season + fuel estimate. This is the asset. It is undercut by leaking raw field values (`4x4_only`, `car_category`, `best_season`, `mostly-paved`) into user-facing prose. |
| **Consistency** | **1** | Four sources of truth disagree: `content/settings/rental_policy.yml` → `/car-rental/*`, `content/pages/terms.yml` → `/terms/`, `content/pages/faq.yml` → `/faq/`, `content/settings/meta.yml` → `/llms.txt` + all JSON-LD. Cross-border travel is simultaneously "prohibited on every rental" and "Armenia 150 ₾ / Turkey 250 ₾, 300 km/day". |

**Overall: (1+3+5+0+6+1) ÷ 6 × 10 = 26.7 → 27 / 100.**

**Honest framing:** 27 is roughly what a technically-competent, content-rich, zero-authority domain scores. It is *not* a technical failure — crawlability, canonicals, hreflang, JSON-LD baseline and pre-rendering are already better than most competitors in this market. It is an **authority and consistency** score. Presence and Position cannot be engineered from inside `build.py`; they need off-site citation. Accuracy and Consistency *can* be fixed entirely inside this repo, this week, and they are what turns "found" into "quoted".

---

## 2. Prompt Analysis

Evaluated by (a) running the target queries through web search to see who currently supplies the answer, and (b) checking whether rentup.ge contains a page that could supply it. **These are modelled, not live LLM API tests** — set up real tracking before claiming movement.

| Prompt | RentUp mentioned? | Position | Sentiment | Accurate? | Who owns the answer today |
|---|---|---|---|---|---|
| "What does car rental cost in Georgia?" | No | — | n/a | n/a | roadiscalling.com, Localrent, finalrentals, triplinkhub |
| "Best car rental company in Tbilisi" | No | — | n/a | n/a | wander-lush.org, Expedia, Skyscanner, wheree.com, OG Drive |
| "Do I need a 4x4 for Tusheti?" | No | — | n/a | n/a | fstarentcar.com (blog), sunnygeorgia.travel, georgia-spirit.com |
| "Can I drive to Ushguli in a sedan?" | No | — | n/a | n/a | wander-lush.org, forum/blog answers |
| "7-day Georgia itinerary by car" | No | — | n/a | n/a | wander-lush.org, goingthewholehogg.com, againstthecompass.com, nextleveloftravel.com |
| "Car rental at Tbilisi airport" | No | — | n/a | n/a | Localrent, Discover Cars, Skyscanner, Rentalcars |
| "Georgia road trip planner" | No | — | n/a | n/a | no dominant owner — **contested, winnable** |
| "Is the Abano Pass open?" | No | — | n/a | n/a | fstarentcar.com, sunnygeorgia.travel |
| "Deposit for car rental in Georgia" | No | — | n/a | n/a | unitedcarsrent.com, geodrive.info |
| "RentUp car rental review" | No | — | n/a | n/a | nothing — brand is invisible to search |

**Two structural observations that matter more than the table:**

1. **Brand-name ambiguity.** "RentUp" collides with unrelated SaaS/property products, and "Georgia" collides with the US state. Query `rentup.ge car rental Georgia` and the engine returns Atlanta. Every page must disambiguate explicitly and repeatedly: *Georgia (the country) / Sakartvelo / Caucasus / GE*. The `areaServed: {"@type":"Country","name":"Georgia"}` node is correct but not sufficient — the prose must carry it too.
2. **The competitor that is actually beating you is a blog.** `fstarentcar.com/blog/tusheti-4x4-adventure-guide-abano-pass/` is a rental company doing exactly the GEO play RentUp should do — publishing the road-condition answer, then attaching the vehicle. RentUp already *has* better data than that post; it just has not shaped it into the answer.

---

## 3. Competitor Comparison

| Brand | Est. AI visibility | Most mentioned for | Why AI cites them |
|---|---|---|---|
| **Localrent** | **High (~75)** | "rent a car Georgia", "cheap car rental Tbilisi", deposit questions | Marketplace scale, thousands of inbound links, review corpus, present in every listicle |
| **Discover Cars / Rentalcars** | **High (~75)** | price comparison, airport pickup | Global brand entities with Wikipedia-adjacent authority and affiliate saturation across travel blogs |
| **Myrentacar** | Medium-high (~60) | Georgia + Armenia regional rental | Regional marketplace, heavily cited in Russian-language travel content |
| **wander-lush.org** | **Very high (~85)** on travel prompts | "renting a car in Georgia", "Georgia road trip itinerary", "driving in Georgia" | Not a competitor for cars — a competitor for *the answer*. Deep first-person guides, updated yearly, cited by everyone |
| **Naniko** | Medium (~50) | "car rental Georgia", corporate/long-term | Long-established .ge domain, multilingual, decades of citations |
| **Caucasus Rent / local ops** | Low-medium (~30) | niche/4x4 | Thin but present in local listicles |
| **fstarentcar.com** | Low-medium (~30), rising | "Abano Pass 4x4", "Tusheti self-drive" | **Blog-led GEO** — publishes the road answer, wins the query, attaches the car |
| **RentUp** | **Very low (27)** | nothing | No citations; contradicts itself; best data, zero distribution |

**Strategic read:** RentUp cannot out-authority Localrent or Discover Cars on `car rental Georgia`. It *can* own the **road-condition / vehicle-requirement / itinerary-feasibility** answer space, because it holds structured data none of them have (per-attraction `road`, `car_category`, `drive_time_tbilisi`, `best_season` across 257 places). That is a defensible GEO wedge, and it converts — the person asking "do I need a 4x4 for Tusheti" is one step from renting a 4x4.

---

## 4. 🔴 The blocking issue: RentUp contradicts RentUp

This is the single most damaging finding in the audit and it outranks every content recommendation below.

The site publishes **two mutually exclusive rental policies on the same domain**, and the *wrong* one carries the machine-readable markup.

| Fact | `/terms/` + `/faq/` (from `content/pages/terms.yml`, `faq.yml`) | `/car-rental/*` (from `content/settings/rental_policy.yml`) |
|---|---|---|
| Minimum age | 21 / 23 / 25 by class, **+ young-driver surcharge 15–25 ₾/day** | **21 flat, explicitly "no young-driver surcharge"** |
| Insurance included | **CDW + TPL included in the rate** | **TPL only**; CDW is a 25 ₾/day add-on |
| Excess | 300 ₾ economy → 1 200 ₾ 4x4; **SCDW reduces excess to zero** | **Flat 1 000 ₾**; "We don't sell a zero-excess product" |
| Cross-border | **Armenia 150 ₾, Turkey 250 ₾, 300 km/day** | **"Cross-border travel isn't available on any rental"** |
| Additional driver | 20 ₾/day | 10 ₾/day |
| Night surcharge | 40 ₾, 22:00–07:00 | 20 ₾, 22:00–08:00 |
| Airport delivery | Free from 3–5 days, else 40–60 ₾ | 30 ₾ TBS / 60 ₾ KUT / 60 ₾ BUS, **no free threshold** |
| Cancellation | Free >48 h; tiered 24–48 h | Free ≤24 h before pickup |
| Prepayment | "confirmed after the required payment is completed" | **"Nothing is prepaid when you book"** |
| Mileage | Unlimited in GE; 300 km/day cross-border | Unlimited in GE; cross-border does not exist |

Add a third and fourth source of truth:

- **`content/settings/meta.yml` → `org_desc`** claims *"full insurance coverage and unlimited mileage"*. That string is emitted as `AutoRental.description` in JSON-LD on **all 2 137 pages** and as the opening line of `/llms.txt`. `/car-rental/` explicitly says the opposite.
- **`dist/llms.txt` `## Key facts`** — the file written *specifically for LLMs* — states: `Insurance: CDW and TPL included; SCDW zero-excess option for 25–45 GEL/day`, `Fuel policy: Full to full`, `Cross-border: Armenia (150 GEL) and Turkey (250 GEL) allowed with permit`, `Minimum driver age: 21 for economy, 23 for SUV/minivan, 25 for business class and 4x4`. Every one of those contradicts `rental_policy.yml`. `fuel_policy: same_to_same` ≠ "full to full".

**Why this is a GEO emergency, not a tidy-up:**

- The `/faq/` page is one of only **18 pages on the entire site with `FAQPage` JSON-LD** — it is the *most* extractable page you have, and it carries the *wrong* policy.
- `/terms/` presents its (contradictory) policy in real `<table>` markup — the highest-confidence extraction format there is. `/car-rental/` presents the correct policy in `<p>` prose with zero tables. **The format hierarchy is inverted: the wrong facts are better marked up than the right ones.**
- LLMs resolve conflicts by picking the most structured, most schema-marked source, or by hedging. Both outcomes are bad: you either get quoted an offer you don't sell (a real commercial and legal exposure — a customer arriving expecting zero-excess SCDW), or you get dropped as unreliable.

**Fix order is non-negotiable: reconcile the facts before producing one word of new content.** Publishing more pages on top of a contradictory fact base multiplies the damage.

---

## 5. Machine-readability audit — can an LLM actually extract your facts?

Measured on the real built files.

### 5.1 Crawlable body text (inside `<main>`, tags stripped)

| Page | Chars | Verdict |
|---|---|---|
| `/` | 9 497 | Good |
| `/car-rental/` | 6 712 | Good — best commercial page on the site |
| `/faq/` | 6 197 | Good (but wrong facts) |
| `/trip-planner/` | 4 725 | Good |
| `/routes/svaneti-expedition/` | 4 517 | Good |
| `/terms/` | 4 513 | Good (but wrong facts) |
| `/attractions/ushguli/` | 4 146 | Good |
| `/car-rental/4x4/` | 3 517 | Adequate |
| `/itineraries/georgia-7-days/` | 3 244 | Adequate |
| `/car-rental/tbilisi-airport/` | **2 064** | **Thin** — the highest-converting query class on the site |
| `/map/` | 1 958 | Thin (interactive by nature; `/trip-planner/` carries the text — correct design) |
| `/fleet/toyota-rav4/` | **1 831** | **Thin** ×17 pages |
| `/itineraries/` | **1 266** | **Thin** — hub with no comparison content |

Everything is server-rendered static HTML with no JS dependency for text. **The crawl layer is genuinely good** — this is a real advantage over JS-heavy competitors.

### 5.2 Structured-format coverage across `dist/`

| Signal | Count | Verdict |
|---|---|---|
| Pages with `<details>` Q&A blocks | **2 112** | The FAQ content exists nearly everywhere |
| Pages with `FAQPage` JSON-LD | **18** | 🔴 **~2 100 pages of Q&A carry no Q&A markup** |
| Pages with `Offer` / price schema | 120 | Only `/fleet/{car}/` (17 × 6 = 102) + a few |
| Pages with `AggregateRating` | 0 | Correct — do not fabricate one |
| Pages with `Review` | 0 | Correct — do not fabricate one |
| Pages with `HowTo` | 0 | Missed opportunity on itineraries |
| Pages with `speakable` | 0 | Low priority |
| `<table>` on `/car-rental/` | **0** | 🔴 Prices, deposits, categories all in prose/cards |
| `<table>` on `/itineraries/georgia-7-days/` | **0** | 🔴 Day plan is `<div class="trip-day">` + `<ul>` |
| `<table>` on `/car-rental/tbilisi-airport/` | 1 | Straight-line distances to attractions (correctly labelled as great-circle) |
| `<table>` on `/terms/` | several | The contradictory policy is the best-marked-up content you have |

**Concrete extraction failures found:**

1. **No fleet price table anywhere.** `/car-rental/` renders prices as `<span class="price">Price from 75 ₾/day</span>` inside category cards. An LLM must infer the category↔price↔deposit↔clearance↔seats relationship from scattered spans. A single `<table>` with `category | cars | from ₾/day | deposit ₾ | clearance mm | seats` would be extracted verbatim with near-certainty. **All six rows already exist in `content/cars/*.yml`** — economy 75 ₾ / 300 ₾ dep, suv 130 / 600, minivan 200 / 1000, business 210 / 1000, offroad 240 / 1200, van 185 / 800.
2. **Itinerary day tables are lists, not tables.** `/itineraries/georgia-7-days/` renders `Day 1 — Tbilisi → Gori · 115 km · 2:10` as an `<h3>` with a `<small>`, then stops as `<li>`. Readable, but a `<table>` of `Day | From → To | km | Drive | Stops | Overnight | Road` is the format an assistant reproduces when asked "give me a 7-day Georgia itinerary".
3. **Per-day distances are derived, not real, and are not labelled as such.** Days 5/6/7 all show `80 km · 1:43`, days 1/2 both `115 km · 2:10` — the component route's total is being divided evenly across its days. The totals are honest (80×3 = 240 km = the real route total), but an LLM will quote "Day 6: 80 km" as a factual daily figure. Either label the split (`≈`, "average day") or store per-day km.
4. **Raw YAML tokens leak into prose.** `/car-rental/4x4/` publishes: *"roads our data tags `4x4_only`"*, *"`car_category` is economy for all seven days"*, *"`best_season` is 'all'"*, *"not the `4x4_only` tracks beyond"*. These will be quoted verbatim by an assistant. They read as a database dump, which lowers the perceived authority of an otherwise excellent answer.
5. **`llms.txt` contains an unsubstituted template placeholder.** `dist/llms.txt` line for `/map/` reads *"Interactive map: `{attractions}` attractions across 11 regions"*. The HTML substitutes it correctly (`257`); `llms_txt()` reads `PAGES[p]["en"]["desc"]` raw and does not.
6. **`llms.txt` emits empty fields.** `- Mobile: ` and `- Email: ` are emitted blank because `site.yml` has `mobile: ''` and `email: ''`.
7. **`llms.txt` and `llms-full.txt` omit the entire commercial cluster.** `grep -c "car-rental" dist/llms.txt` → **0**. Same for `itineraries` and `trip-planner`. The two files written *for AI consumption* list every one of the 257 attractions but not a single one of the 11 `/car-rental/*` pages, 6 `/itineraries/*` pages, or `/trip-planner/`. They also list `/account/` — a `noindex, nofollow` private page.
8. **No `sameAs` and no `email` in `Organization` schema.** `site.yml` has `social: []` and `email: ''`, so `org_node()` emits neither. `sameAs` is the primary entity-reconciliation signal for knowledge graphs and AI assistants — without it, "RentUp" is an unresolvable string, not an entity.
9. **`llms.txt` is not discoverable from HTML.** No `<link rel="alternate" type="text/markdown" href="/llms.txt">` in any page head; the file is only findable by convention.
10. **Unverified business claims are highly extractable.** `/about/` publishes *"Rentals per year 4 800+"*, *"Employees 34"*, *"utilisation target 65 %, summer 85 %, winter 45 %"* in a marked-up stats block. These are the numbers an assistant will quote as fact about RentUp. They are not sourced from any dataset in the repo. Either verify them or remove them — an AI repeating an unverifiable operational claim is a liability, not a win. Likewise the `★★★★★ 5` star display on attraction pages (from `rating: 5` in the YAML) reads as a customer review rating to an extractor; it is an editorial score. Label it or drop the star glyphs.

**What is already right and must not be "fixed":** 100 % static pre-rendering, self-referencing canonicals, 6-language hreflang + `x-default`, `BreadcrumbList` everywhere, `Car` + `Offer` + `UnitPriceSpecification` on vehicle pages, `TouristTrip` on itineraries, `TouristAttraction` with `geo` + `elevation` on 257 pages, and an unusually honest `_rental_distance_table()` that labels its distances as great-circle rather than passing them off as driving distance. That last one is exactly the discipline GEO rewards.

---

## 6. Proposed `llms.txt` / `llms-full.txt`

### 6.1 What is wrong with the current files

| Problem | Current | Should be |
|---|---|---|
| Size | `llms.txt` = **89 KB**, 257 attractions inline | The spec calls for a short **index** — target < 8 KB |
| Coverage | 0 `/car-rental/*`, 0 `/itineraries/*`, 0 `/trip-planner/` | All commercial and itinerary URLs first |
| Facts | From `meta.yml`, contradicts `rental_policy.yml` | Generated **from `rental_policy.yml` + `cars/*.yml`** — one source of truth |
| Placeholders | `{attractions}` unsubstituted | Substituted |
| Empty fields | `- Mobile: `, `- Email: ` | Omitted when empty |
| Private pages | `/account/` listed | Excluded (`noindex` pages never appear) |
| Discovery | No `<link>` in head | `<link rel="alternate" type="text/markdown">` |

### 6.2 Proposed `llms.txt` (exact content, all values from real repo data)

```markdown
# RentUp (რენტაპი)

> RentUp is a car rental company based in Tbilisi, Georgia (the country, not the US state),
> renting 17 vehicles across 6 categories with pickup at 6 points including Tbilisi (TBS),
> Kutaisi (KUT) and Batumi (BUS) airports. RentUp also publishes a free road-trip planner
> for Georgia covering 257 attractions, 32 routes and 5 multi-day itineraries, with road
> grade and required vehicle category recorded for every place.

## Key facts

- **Business:** Car rental, Georgia (country) — ISO 3166 code GE, capital Tbilisi
- **Founded:** 2019
- **Fleet:** 17 vehicles, 6 categories
- **Daily rate from:** 75 GEL (economy)
- **Pickup points:** Tbilisi office (71 Vazha-Pshavela Ave.), Tbilisi, Kutaisi and Batumi
  city delivery, Tbilisi (TBS), Kutaisi (KUT) and Batumi (BUS) airports
- **Minimum driver age:** 21, licence held 2+ years, all categories
- **Licence accepted:** national licence in Latin script, or national licence + IDP; passport required
- **Mileage:** unlimited within Georgia, every category, every rental length
- **Fuel policy:** same-to-same (returned at the level it left at)
- **Insurance:** third-party liability included; standard excess 1000 GEL;
  optional CDW 25 GEL/day reduces exposure. No zero-excess or fully-comprehensive product is sold.
- **Deposit:** 300 GEL (economy) to 1200 GEL (4x4), card hold or cash,
  released within 3 working days after undamaged return
- **Cross-border:** not available — vehicles stay inside Georgia on every rental
- **Delivery:** free at the Tbilisi office and anywhere in Tbilisi;
  Tbilisi airport 30 GEL; Kutaisi and Batumi airports 60 GEL; Kutaisi/Batumi city address 50 GEL
- **Night surcharge:** 20 GEL for pickup or return between 22:00 and 08:00
- **One-way:** 100 GEL between served cities
- **Extras:** child seat 10 GEL/day, additional driver 10 GEL/day, WiFi router 15 GEL/day
- **Cancellation:** free up to 24 h before pickup; later or no-show is charged one rental day.
  Nothing is prepaid at booking.
- **Rental length:** 1 to 90 days
- **Support:** roadside assistance included; office 09:00–21:00; Georgian, English, Russian

## Fleet and prices

| Category | Cars | From (GEL/day) | Deposit (GEL) | Clearance (mm) |
|---|---|---|---|---|
| Economy | 3 | 75 | 300 | 135–145 |
| SUV / crossover | 3 | 130 | 600 | 181–195 |
| Commercial van | 2 | 185 | 800 | 170–175 |
| Minivan (7–9 seats) | 3 | 200 | 1000 | 160–186 |
| Business | 3 | 210 | 1000 | 130–145 |
| Off-road 4x4 | 3 | 240 | 1200 | 210–235 |

Rates fall with duration: 1–6 days, 7–29 days, 30+ days tiers on every vehicle.

## Car rental

- [Car rental in Georgia](https://rentup.ge/car-rental/): terms, categories, pickup points, deposits
- [Economy car rental](https://rentup.ge/car-rental/economy/): from 75 GEL/day, 300 GEL deposit
- [SUV / crossover rental](https://rentup.ge/car-rental/suv/): from 130 GEL/day, 600 GEL deposit
- [4x4 / off-road rental](https://rentup.ge/car-rental/4x4/): from 240 GEL/day, 1200 GEL deposit —
  required for Tusheti, Khevsureti and upper Svaneti
- [Minivan rental](https://rentup.ge/car-rental/minivan/): from 200 GEL/day, 7–9 seats
- [Car rental in Tbilisi](https://rentup.ge/car-rental/tbilisi/): free city delivery
- [Tbilisi Airport (TBS) car rental](https://rentup.ge/car-rental/tbilisi-airport/): 30 GEL delivery
- [Car rental in Kutaisi](https://rentup.ge/car-rental/kutaisi/): 50 GEL delivery
- [Kutaisi Airport (KUT) car rental](https://rentup.ge/car-rental/kutaisi-airport/): 60 GEL delivery
- [Car rental in Batumi](https://rentup.ge/car-rental/batumi/): 50 GEL delivery
- [Batumi Airport (BUS) car rental](https://rentup.ge/car-rental/batumi-airport/): 60 GEL delivery

## Itineraries

| Itinerary | Days | Distance | Driving | Car needed | Season |
|---|---|---|---|---|---|
| [Georgia in 3 days](https://rentup.ge/itineraries/georgia-3-days/) | 3 | 420 km | 8:00 | Economy | All year |
| [Georgia in 5 days](https://rentup.ge/itineraries/georgia-5-days/) | 5 | 610 km | 13:00 | SUV | Jun–Sep |
| [Georgia in 7 days](https://rentup.ge/itineraries/georgia-7-days/) | 7 | 1020 km | 18:30 | Economy | All year |
| [Georgia in 10 days](https://rentup.ge/itineraries/georgia-10-days/) | 10 | 1450 km | 27:00 | SUV | May–Oct |
| [Georgia in 14 days](https://rentup.ge/itineraries/georgia-14-days/) | 14 | 2040 km | 39:30 | SUV | May–Oct |

All itineraries start in Tbilisi and are built from RentUp's own route data.

## Trip planning

- [Georgia road trip planner](https://rentup.ge/trip-planner/): build a route from 257 mapped places
- [Interactive map](https://rentup.ge/map/): 257 attractions across 11 regions
- [Ready-made routes](https://rentup.ge/tours/): 32 routes with distance, driving time and required car
- [Regions of Georgia](https://rentup.ge/regions/): 11 regions

## Road conditions and vehicle requirements

Every one of the 257 attractions carries a recorded road grade (paved / mostly paved /
gravel / 4x4-only) and a required vehicle category. Summary:

- Paved, any car: 149 places
- Mostly paved, any car: 71 places
- Gravel — SUV or 4x4 required: 20 places
- 4x4-only: 17 places, all seasonal (typically June–September)

4x4-only destinations include Omalo and Tusheti (via Abano Pass), Dartlo,
Shenako and Diklo, Shatili, Mutso, Juta, Adishi, Shkhara Glacier, Koruldi Lakes,
Vashlovani National Park and Tobavarchkhili Lakes.
Ushguli is graded gravel and requires the off-road 4x4 category.

## Reference

- [Rental terms](https://rentup.ge/terms/)
- [FAQ](https://rentup.ge/faq/)
- [About RentUp](https://rentup.ge/about/)
- [Contact](https://rentup.ge/contact/)
- [Full site content](https://rentup.ge/llms-full.txt)

## Languages

English (/), ქართული (/ka/), Русский (/ru/), فارسی (/fa/), עברית (/he/), العربية (/ar/)

## Contact

- Phone: +995 597 55 55 65
- WhatsApp: +995 597 55 55 65
- Address: 71 Vazha-Pshavela Ave., Tbilisi 0186, Georgia (country)
- Hours: Mon–Sun 09:00–21:00

Last updated: 2026-08-29
```

**Note on the road-grade counts:** the four bucket numbers above must be *computed*, not typed. The patch in §8.3 derives them from `ATTRACTIONS`. Live counts from the current data: `paved` 149, `mostly_paved` 71, `gravel` 20, `4x4_only` 17 (English entries).

### 6.3 `llms-full.txt`

Keep the current design — it is genuinely good — with three changes:

1. Add a `## Rental policy` section rendered from `rental_policy.yml` (every field, as `key: value` lines) so the *authoritative* policy is the one in the full dump.
2. Add `## Car rental pages` and `## Itineraries` sections mirroring the HTML (currently absent — 0 occurrences of either string in the 822 KB file).
3. Add a `## Road grade index` table: one row per attraction with `name | road | car_category | km from Tbilisi | drive time | season`. This is the highest-value block in the whole file for GEO and it is 257 rows of data you already have.

---

## 7. `robots.txt` — AI bot policy

Current `dist/robots.txt` (from `robots()` at `build.py:2941`, `AI_BOTS` at `build.py:2933`) allows **all 20** AI user-agents: `GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, Claude-SearchBot, anthropic-ai, PerplexityBot, Perplexity-User, Google-Extended, Applebot, Applebot-Extended, Bingbot, CCBot, Meta-ExternalAgent, cohere-ai, YandexBot, Amazonbot, DuckAssistBot, MistralAI-User`.

**Recommendation: keep allowing all of them. Change nothing except adding two more.** Justification is commercial, not ideological:

| Bot class | Verdict | Commercial reasoning |
|---|---|---|
| **Answer-engine retrieval** (`OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User`, `DuckAssistBot`, `MistralAI-User`, `Bingbot`, `Applebot`) | **Allow — non-negotiable** | These fetch a page *because a real user just asked a question*. Blocking them removes RentUp from the answer at the exact moment of purchase intent. Zero downside. |
| **Training crawlers** (`GPTBot`, `ClaudeBot`, `anthropic-ai`, `Google-Extended`, `Applebot-Extended`, `Meta-ExternalAgent`, `cohere-ai`, `Amazonbot`, `CCBot`) | **Allow** | The usual argument for blocking is protecting proprietary content from being learned for free. That calculus applies to publishers whose *content is the product*. RentUp's product is a car in Tbilisi. Being learned into a model's weights as "the Georgian rental company that documents which roads need a 4x4" is **the entire objective**. A brand with 27/100 visibility and zero citations blocking training crawlers is choosing permanent invisibility. |
| **`YandexBot`** | **Allow** | Russian is a top-3 inbound market for Georgian car rental (`/ru/` is a full locale, and Myrentacar/Localrent's Russian-language reach proves the demand). |
| **Missing — add** | `Bytespider` (TikTok/Doubao), `Google-CloudVertexBot` | Both are legitimate AI crawlers absent from the list. `Bytespider` matters for the Persian/Arabic and Chinese-adjacent travel audiences the site already builds `/fa/` and `/ar/` for. |
| **`Disallow: /admin/`** | Keep | Correct. |
| **Add `Disallow:`** | `/trip/`, `/account/`, `/app/` | Already `noindex, nofollow`, but AI crawlers do not consistently honour meta robots. These render private user output; there is no reason for them in a training corpus or an answer. Cheap, zero-risk. |

Add one line the file currently lacks:

```
# Machine-readable summary for AI assistants
Llms: https://rentup.ge/llms.txt
```

`Llms:` is not a ratified directive — treat it as a discovery hint only. The load-bearing discovery mechanism is the `<link rel="alternate">` tag in §8.4.

---

## 8. Implementation in this codebase

Every patch below is against real functions at real line numbers. **None has been applied.**

### 8.0 P0 — Reconcile the fact base (do this before anything else)

No code patch — a data decision only the owner can make. `content/settings/rental_policy.yml` carries a header saying its values are *"PROPOSED DEFAULTS drafted for the owner's approval (2026-08-29)"*. Until that approval lands, the site ships two policies.

Once the real policy is confirmed, `rental_policy.yml` becomes the single source of truth and three files must be rewritten to match it:

1. `content/pages/terms.yml` — the age matrix, young-driver surcharge rows, the CDW/SCDW paragraphs, the cross-border table, the cancellation tiers.
2. `content/pages/faq.yml` — the answers on age, additional driver, excess, SCDW, mileage/cross-border, airport delivery, night pickup.
3. `content/settings/meta.yml` — `org_desc` (drop *"full insurance coverage"*) and the entire `llms_facts` list, which the §8.3 patch replaces with derived values anyway.

Then add a regression test in `tests/test_content_quality.py` so it cannot drift again:

```python
def test_policy_is_single_source_of_truth():
    """Terms, FAQ and meta must not contradict rental_policy.yml."""
    import build
    pol = build.RENTAL_POLICY          # add this global if absent (see 8.3)
    terms = yaml.safe_load(open("content/pages/terms.yml"))
    faq = yaml.safe_load(open("content/pages/faq.yml"))
    blob = json.dumps([terms, faq], ensure_ascii=False).lower()
    if not pol["cross_border"]["allowed"]:
        for word in ("armenia", "turkey", "cross-border travel is permitted"):
            assert word not in blob, f"cross-border claim in terms/faq: {word}"
    if not pol["insurance"].get("scdw_available"):
        assert "scdw" not in blob, "SCDW is advertised but not offered"
    age = pol["min_driver_age"]
    assert f"from {age}" in blob or str(age) in blob
```

**Expected impact: High.** Nothing else in this document works until the site agrees with itself.

---

### 8.1 P0 — `FAQPage` JSON-LD on the ~2 100 pages that already have FAQ content

`faq_node()` exists at `build.py:633` but only consumes `blocks` (the `PAGES` format). The SEO cluster builds FAQs from `seo_car_rental.yml` / `seo_categories.yml` / `seo_trip_planner.yml` and renders them via `_faq_html()` (`build.py:3320`) with **no schema at all**.

**Add next to `faq_node()`, after `build.py:640`:**

```python
def faq_node_items(items):
    """FAQPage from a plain [{q, a}] list — the SEO-cluster FAQ format.
    Mirrors faq_node(), which only reads the PAGES `blocks` structure."""
    qas = [x for x in (items or []) if x.get("q") and x.get("a")]
    if not qas:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": x["q"],
         "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in qas]}
```

**Then append it to the graph in four render functions.** In each, the `graph = [...]` list is built and passed to `head_html()`; insert one line between them.

`render_car_rental_hub()` — after `build.py:3474` (`crumbs_node(...)]`):

```python
    graph = [n for n in (graph + [faq_node_items(h.get("faq"))]) if n]
```

`render_rental_location()` — same line after its `crumbs_node(...)]`, using the location's FAQ:

```python
    graph = [n for n in (graph + [faq_node_items(L.get("faq"))]) if n]
```

`render_rental_category()` — after `build.py:3603`:

```python
    graph = [n for n in (graph + [faq_node_items(L.get("faq"))]) if n]
```

`render_planner_landing()` — after its `crumbs_node(...)]` near `build.py:3801`:

```python
    graph = [n for n in (graph + [faq_node_items(P.get("faq"))]) if n]
```

`/car-rental/` alone has 8 hub FAQs + 2 more rendered; `/car-rental/4x4/` has 6. Across 6 languages this is roughly **100+ commercial pages** gaining explicit Q&A markup, and it is the format answer engines extract with the highest confidence.

**Expected impact: High.** Cost: ~15 lines.

---

### 8.2 P0 — Fleet price table on `/car-rental/`

`render_car_rental_hub()` currently emits category `<div class="card">` blocks with a `<span class="price">`. Add a real table. **Insert after `_car_card` helpers, near `build.py:3320`:**

```python
def _fleet_price_table(lang):
    """Category × price × deposit × clearance, straight from content/cars/*.yml.
    Every value is real; nothing here is computed from a policy assumption."""
    rows = {}
    for slug, c in CARS.items():
        k = c["category"]
        r = rows.setdefault(k, {"n": 0, "price": [], "dep": set(), "cl": [], "seats": set()})
        r["n"] += 1
        r["price"].append(int(c["price_1_6"]))
        r["dep"].add(int(c["deposit"]))
        r["cl"].append(int(c["clearance"]))
        r["seats"].add(int(c["seats"]))
    order = sorted(rows, key=lambda k: min(rows[k]["price"]))
    head = [su("category", lang) or "Category", su("cars", lang) or "Cars",
            su("price_from", lang) or "From ₾/day", su("deposit", lang) or "Deposit ₾",
            su("clearance", lang) or "Clearance mm", su("seats", lang) or "Seats"]
    body = ""
    for k in order:
        r = rows[k]
        dep = (f'{min(r["dep"])}' if len(r["dep"]) == 1
               else f'{min(r["dep"])}–{max(r["dep"])}')
        st = (f'{min(r["seats"])}' if len(r["seats"]) == 1
              else f'{min(r["seats"])}–{max(r["seats"])}')
        body += (f'<tr><th scope="row"><a href="{rental_cat_url(lang, k, False)}">'
                 f'{E(cat_label(k, lang))}</a></th>'
                 f'<td>{r["n"]}</td><td>{min(r["price"])}</td><td>{dep}</td>'
                 f'<td>{min(r["cl"])}–{max(r["cl"])}</td><td>{st}</td></tr>')
    return ('<div class="tablewrap"><table class="pricetable"><thead><tr>'
            + "".join(f"<th>{E(h)}</th>" for h in head)
            + f"</tr></thead><tbody>{body}</tbody></table></div>")
```

**Wire it into `render_car_rental_hub()` body at `build.py:3450`**, between the category cards and the pickup-locations section:

```python
        + _sec(su("prices", lang) or "Prices and deposits",
               _fleet_price_table(lang), alt=True)
```

Note `rental_cat_url()` only resolves for the four published categories (`economy, suv, offroad, minivan`); guard the link for `business` and `van` rows, or render those two as plain `<th>` text.

**Also add a matching `Offer` block to the hub graph** so the price range is machine-stated, not only rendered:

```python
    prices = [int(c["price_1_6"]) for c in CARS.values()]
    graph.append({
        "@type": "AggregateOffer", "priceCurrency": "GEL",
        "lowPrice": min(prices), "highPrice": max(prices),
        "offerCount": len(CARS),
        "itemOffered": {"@id": SITE_URL + "/#organization"},
        "seller": {"@id": SITE_URL + "/#organization"}})
```

**Expected impact: High.** Answers "what does car rental cost in Georgia" in one extractable block.

---

### 8.3 P0 — Rewrite `llms_txt()` from the authoritative data

Replace `llms_txt()` (`build.py:2958–2996`) entirely. Add `RENTAL_POLICY = load_opt("content/settings/rental_policy.yml")` next to the other globals at `build.py:87–89` if it is not already loaded.

```python
def _llms_policy_facts():
    """Key facts derived from rental_policy.yml + cars/*.yml — never from
    meta.yml, which is prose and has drifted from the policy."""
    p = RENTAL_POLICY
    d, ins, dl = p["deposit"], p["insurance"], p["delivery"]
    deps = sorted(int(c["deposit"]) for c in CARS.values())
    prices = sorted(int(c["price_1_6"]) for c in CARS.values())
    f = [
        ("Business", "Car rental, Georgia (country) — ISO code GE, capital Tbilisi"),
        ("Founded", SITE["founded"]),
        ("Fleet", f"{len(CARS)} vehicles, {len({c['category'] for c in CARS.values()})} categories"),
        ("Daily rate from", f"{prices[0]} GEL (economy)"),
        ("Minimum driver age", f"{p['min_driver_age']}, licence held "
                               f"{p['min_licence_years']}+ years, all categories"),
        ("Mileage", "Unlimited within Georgia" if p["mileage"]["unlimited"] else "Limited"),
        ("Fuel policy", p["fuel_policy"].replace("_", "-")),
        ("Insurance", f"{ins['included'].upper()} included; standard excess "
                      f"{ins['excess_gel']} GEL; optional CDW {ins['cdw_daily_gel']} GEL/day. "
                      f"No zero-excess product is sold."),
        ("Deposit", f"{deps[0]}–{deps[-1]} GEL, {d['method'].replace('_', ' ')}"
                    f"{' or cash' if d['cash_accepted'] else ''}, released within "
                    f"{d['released_days']} working days"),
        ("Cross-border", "Permitted" if p["cross_border"]["allowed"]
                         else "Not available — vehicles stay inside Georgia"),
        ("Delivery", "Free at the Tbilisi office and in Tbilisi; "
                     + ", ".join(f"{k} {v} GEL" for k, v in dl["airport_fee_gel"].items() if v)
                     + "; " + ", ".join(f"{k} {v} GEL" for k, v in dl["city_fee_gel"].items())),
        ("Night surcharge", f"{dl['night_surcharge_gel']} GEL between "
                            f"{dl['night_from']} and {dl['night_to']}"),
        ("One-way", f"{p['one_way']['fee_gel']} GEL between served cities"
                    if p["one_way"]["available"] else "Not available"),
        ("Extras", ", ".join(f"{k.replace('_', ' ')} {v} GEL/day"
                             for k, v in p["extras_gel"].items() if v)),
        ("Cancellation", f"Free up to {p['cancellation']['free_until_hours']} h before pickup; "
                         f"no-show charged {p['cancellation']['no_show_charge_days']} rental day"
                         + ("" if p["cancellation"]["prepayment_required"]
                            else ". Nothing is prepaid at booking.")),
        ("Rental length", f"{p['min_rental_days']}–{p['max_rental_days']} days"),
        ("Support", f"Roadside assistance included; office {SITE['opens']}–{SITE['closes']}; "
                    + ", ".join(LANG_LABEL[l] for l in p["support"]["languages"] if l in LANG_LABEL)),
    ]
    return f


def _llms_fleet_table():
    rows = {}
    for c in CARS.values():
        r = rows.setdefault(c["category"], {"n": 0, "p": [], "d": set(), "cl": []})
        r["n"] += 1
        r["p"].append(int(c["price_1_6"]))
        r["d"].add(int(c["deposit"]))
        r["cl"].append(int(c["clearance"]))
    out = ["| Category | Cars | From (GEL/day) | Deposit (GEL) | Clearance (mm) |",
           "|---|---|---|---|---|"]
    for k in sorted(rows, key=lambda k: min(rows[k]["p"])):
        r = rows[k]
        dep = (str(min(r["d"])) if len(r["d"]) == 1 else f'{min(r["d"])}–{max(r["d"])}')
        out.append(f'| {cat_label(k, "en")} | {r["n"]} | {min(r["p"])} | {dep} | '
                   f'{min(r["cl"])}–{max(r["cl"])} |')
    return out


def _llms_road_summary():
    """Road grade distribution across the attraction dataset — computed, never typed."""
    from collections import Counter
    c = Counter(a["road"] for a in ATTRACTIONS.values())
    label = {"paved": "Paved, any car", "mostly_paved": "Mostly paved, any car",
             "gravel": "Gravel — SUV or 4x4 required", "4x4_only": "4x4-only"}
    out = [f"- {label.get(k, k)}: {v} places" for k, v in c.most_common()]
    hard = [a["en"]["name"] for a in ATTRACTIONS.values() if a["road"] == "4x4_only"]
    out += ["", "4x4-only destinations: " + ", ".join(sorted(hard)) + "."]
    return out


def llms_txt():
    """Concise index for AI assistants. Facts come from rental_policy.yml and
    cars/*.yml so this file can never contradict the rendered pages.
    Target: < 8 KB. The exhaustive dump lives in llms-full.txt."""
    out = [f"# {BRAND} ({SITE['rental_brand_ka']})", "",
           f"> {META['en']['org_desc']}", "", "## Key facts", ""]
    out += [f"- **{k}:** {v}" for k, v in _llms_policy_facts()]
    out += ["", "## Fleet and prices", ""] + _llms_fleet_table()
    out += ["", "Rates fall with duration: 1–6, 7–29 and 30+ day tiers on every vehicle.", ""]

    out += ["## Car rental", ""]
    hub = (SEO_CAR_RENTAL.get("hub") or {}).get("en") or {}
    if hub:
        out.append(f"- [{hub.get('h1','Car rental in Georgia')}]"
                   f"({rental_hub_url('en')}): {hub.get('meta_description','')}")
    for k, cat in _seo_cats().items():
        if not rental_quality_ok("category", cat):
            continue
        L = cat.get("en") or {}
        out.append(f"- [{L.get('h1', k)}]({rental_cat_url('en', k)}): "
                   f"from {cat['data'].get('price_from_gel', cheapest_price(k))} GEL/day")
    for k in RENTAL_PLACES:
        loc = (SEO_CAR_RENTAL.get("locations") or {}).get(k) or {}
        if not rental_quality_ok("location", loc):
            continue
        L = loc.get("en") or {}
        fee = (RENTAL_POLICY["delivery"]["airport_fee_gel"].get(k)
               or RENTAL_POLICY["delivery"]["city_fee_gel"].get(k))
        note = f"{fee} GEL delivery" if fee else "free delivery"
        out.append(f"- [{L.get('h1', k)}]({rental_place_url('en', k)}): {note}")

    good = [(k, v) for k, v in ITINERARIES.items() if itinerary_quality_ok(v)]
    if good:
        out += ["", "## Itineraries", "",
                "| Itinerary | Days | Distance | Driving | Car needed | Season |",
                "|---|---|---|---|---|---|"]
        for k, it in sorted(good, key=lambda kv: kv[1]["days"]):
            out.append(f'| [{it["en"]["name"]}]({itin_url("en", k)}) | {it["days"]} | '
                       f'{it["total_km"]} km | {it["total_drive"]} | '
                       f'{car_cat_label(it.get("car_category", "economy"), "en")} | '
                       f'{it.get("best_season", "all")} |')

    out += ["", "## Trip planning", "",
            f"- [Georgia road trip planner]({planner_landing_url('en')}): "
            f"build a route from {len(ATTRACTIONS)} mapped places",
            f"- [Interactive map]({page_url('en', 'map')}): {len(ATTRACTIONS)} attractions "
            f"across {len(REGIONS)} regions",
            f"- [Ready-made routes]({SITE_URL}/tours/): {len(ROUTES)} routes with distance, "
            f"driving time and required car category"]

    out += ["", "## Road conditions and vehicle requirements", "",
            f"Every one of the {len(ATTRACTIONS)} attractions carries a recorded road grade "
            f"and a required vehicle category.", ""] + _llms_road_summary()

    out += ["", "## Reference", ""]
    for p in PAGE_ORDER:
        if p in ("account", "index"):        # never advertise noindex / private pages
            continue
        d = (PLANNER["en"] if p == "planner" else PAGES[p]["en"])["desc"]
        d = d.replace("{attractions}", str(len(ATTRACTIONS)))   # substitute, as head_html does
        out.append(f"- [{UI['en']['nav'][p]}]({page_url('en', p)}): {d}")
    out.append(f"- [Full site content]({SITE_URL}/llms-full.txt)")

    out += ["", "## Languages", ""]
    out += [f"- [{LANG_LABEL[l]}]({SITE_URL + lang_root(l)})" for l in LANGS]

    out += ["", "## Contact", "", f"- Phone: {SITE['phone']}"]
    if SITE.get("whatsapp"):
        out.append(f"- WhatsApp: +{SITE['whatsapp']}")
    for k, label in (("mobile", "Mobile"), ("email", "Email")):
        if SITE.get(k):                       # omit empty fields instead of emitting blanks
            out.append(f"- {label}: {SITE[k]}")
    a = SITE["address"]["en"]
    out += [f"- Address: {a['street']}, {a['city']} {SITE['address_zip']}, Georgia (country)",
            f"- Hours: Mon–Sun {SITE['opens']}–{SITE['closes']}", "",
            f"Last updated: {TODAY}", ""]
    return "\n".join(out)
```

The `main()` write loop at `build.py:4606` needs no change — it already writes `llms.txt` and `llms-full.txt`.

For `llms_full_txt()` (`build.py:2999`), append three blocks before `return`:

```python
    out += ["\n## Rental policy (authoritative)", "",
            "Source: content/settings/rental_policy.yml"]
    out += [f"{k}: {v}" for k, v in _llms_policy_facts()]

    out += ["\n## Car rental pages", ""]
    for k, cat in _seo_cats().items():
        if not rental_quality_ok("category", cat):
            continue
        L = cat.get("en") or {}
        out += [f"### {L.get('h1', k)}", f"URL: {rental_cat_url('en', k)}",
                L.get("lead", ""), L.get("when_to_choose", ""), L.get("limitations", ""), ""]
    for k in RENTAL_PLACES:
        loc = (SEO_CAR_RENTAL.get("locations") or {}).get(k) or {}
        if not rental_quality_ok("location", loc):
            continue
        L = loc.get("en") or {}
        out += [f"### {L.get('h1', k)}", f"URL: {rental_place_url('en', k)}",
                L.get("lead", ""), " ".join(L.get("good_to_know") or []), ""]

    out += ["\n## Itineraries", ""]
    for k, it in ITINERARIES.items():
        if not itinerary_quality_ok(it):
            continue
        out += [f"### {it['en']['name']}", f"URL: {itin_url('en', k)}",
                f"{it['days']} days | {it['total_km']} km | {it['total_drive']} driving | "
                f"car: {it.get('car_category')} | season: {it.get('best_season')}",
                "| Day | From → To | km | Drive | Overnight | Road | Stops |",
                "|---|---|---|---|---|---|---|"]
        for d in it.get("plan") or []:
            stops = ", ".join(ATTRACTIONS[s]["en"]["name"]
                              for s in (d.get("stops") or []) if s in ATTRACTIONS)
            out.append(f'| {d["day"]} | {_place_name("en", d.get("from",""))} → '
                       f'{_place_name("en", d.get("to",""))} | ~{d["km"]} | {d["drive"]} | '
                       f'{_place_name("en", d.get("overnight",""))} | {d.get("road","paved")} '
                       f'| {stops} |')
        out += ["", strip_md(it["en"].get("body", "")), ""]

    out += ["\n## Road grade index", "",
            "| Place | Road | Car needed | km from Tbilisi | Drive time | Season |",
            "|---|---|---|---|---|---|"]
    for s, a in sorted(ATTRACTIONS.items(), key=lambda kv: kv[1]["en"]["name"]):
        out.append(f'| [{a["en"]["name"]}]({attr_url("en", s)}) | {a["road"]} | '
                   f'{a["car_category"]} | {a["distance_tbilisi_km"]} | '
                   f'{a["drive_time_tbilisi"]} | {a["best_season"]} |')
```

**Expected impact: High.** The two files AI assistants read by convention currently omit 100 % of the commercial cluster and contradict the site on policy.

---

### 8.4 P1 — Make `llms.txt` discoverable + fix the `Organization` entity

**(a)** In `head_html()` (`build.py:534`), beside the existing canonical/hreflang emission, add:

```python
    f'<link rel="alternate" type="text/markdown" href="{SITE_URL}/llms.txt" '
    f'title="Machine-readable site summary">'
```

**(b)** In `robots()` (`build.py:2941`), extend the bot list and lock down private paths:

```python
AI_BOTS = [... existing 20 ..., "Bytespider", "Google-CloudVertexBot"]

def robots(include_docs=False):
    out = ["User-agent: *", "Allow: /", "Disallow: /admin/",
           "Disallow: /trip/", "Disallow: /account/", "Disallow: /app/"]
    ...
    out += [f"Sitemap: {SITE_URL}/sitemap.xml",
            "# Machine-readable summary for AI assistants",
            f"Llms: {SITE_URL}/llms.txt",
            f"Host: {SITE_URL.split('//')[1]}", ""]
```

**(c)** `content/settings/site.yml` — fill `email` and `social`. `org_node()` (`build.py:586`) already emits `email` and `sameAs` **only when non-empty**, so the code needs no change; the data does. `sameAs` is the single strongest entity-reconciliation signal available to an AI assistant, and it is currently `[]`:

```yaml
email: info@rentup.ge          # any real, monitored address
social:
  - https://www.facebook.com/<rentup page>
  - https://www.instagram.com/<rentup handle>
  - https://www.google.com/maps/place/?q=place_id:<GBP place id>
  - https://www.tripadvisor.com/<listing>
```

**(d)** `content/settings/meta.yml → org_desc` — remove the false *"full insurance coverage"* claim and add country disambiguation. Proposed replacement, consistent with `rental_policy.yml`:

> RentUp is a car rental company based in Tbilisi, Georgia (the country in the Caucasus, not the US state). 17 vehicles in 6 categories, daily to monthly rentals, delivery in Tbilisi, Kutaisi and Batumi and at all three international airports, unlimited mileage within Georgia and third-party liability insurance included in every rate.

That string propagates to `AutoRental.description` on all 2 137 pages and to the `llms.txt` header.

**Expected impact: High** for (c) and (d), **Medium** for (a) and (b).

---

### 8.5 P1 — Itinerary day table + `HowTo`/`Trip` enrichment

In `render_itinerary()` (`build.py:3646`), the `days_html` loop builds `<div class="trip-day">`. Add a table **before** the day cards (keep the cards — they are the better mobile UI; the table is for extraction):

```python
    day_rows = "".join(
        f'<tr><th scope="row">{d["day"]}</th>'
        f'<td>{E(_place_name(lang, d.get("from","")))} → '
        f'{E(_place_name(lang, d.get("to","")))}</td>'
        f'<td>≈{d["km"]}</td><td>{E(d["drive"])}</td>'
        f'<td>{E(_place_name(lang, d.get("overnight","")))}</td>'
        f'<td>{E(su("road", lang, d.get("road","paved")))}</td>'
        f'<td>{", ".join(E(ATTRACTIONS[s][lang]["name"]) for s in (d.get("stops") or []) if s in ATTRACTIONS)}</td>'
        f'</tr>' for d in (it.get("plan") or []))
    day_table = (
        f'<div class="tablewrap"><table class="daytable"><caption>'
        f'{E(su("day_by_day", lang))} — {it["total_km"]} {E(tu(lang,"km"))}, '
        f'{E(it["total_drive"])}</caption><thead><tr>'
        f'<th>{E(su("day", lang))}</th><th>{E(su("route", lang) or "Route")}</th>'
        f'<th>{E(tu(lang,"km"))}</th><th>{E(su("total_drive", lang))}</th>'
        f'<th>{E(su("overnight", lang))}</th><th>{E(su("road", lang))}</th>'
        f'<th>{E(tu(lang,"attractions"))}</th></tr></thead>'
        f'<tbody>{day_rows}</tbody></table>'
        f'<p class="pshort"><small>{E(su("km_note", lang) or "Daily distances are the component route total divided across its days.")}</small></p></div>')
```

then change the day-by-day section at `build.py:3684` to `day_table + f'<div class="trip-days">{days_html}</div>'`.

The `≈` and the footnote resolve finding §5.3 — the number stays, but it is no longer presented as a surveyed daily distance.

Enrich the `TouristTrip` node (`build.py:3702`) with the facts already on the page:

```python
             {"@type": "TouristTrip", "@id": url + "#trip", ...,
              "touristType": car_cat_label(it.get("car_category", "economy"), lang),
              "subjectOf": {"@type": "Trip", "name": L.get("name", "")},
              "additionalProperty": [
                  {"@type": "PropertyValue", "name": "durationDays", "value": it["days"]},
                  {"@type": "PropertyValue", "name": "totalDistanceKm", "value": it["total_km"]},
                  {"@type": "PropertyValue", "name": "totalDrivingTime", "value": it["total_drive"]},
                  {"@type": "PropertyValue", "name": "requiredVehicleCategory",
                   "value": it.get("car_category", "economy")},
                  {"@type": "PropertyValue", "name": "bestSeason",
                   "value": it.get("best_season", "all")}],
              "itinerary": {...unchanged...}}
```

**Expected impact: High** on "N-day Georgia itinerary" prompts, currently owned entirely by travel blogs.

---

### 8.6 P1 — `additionalProperty` on `TouristAttraction` (road grade + required vehicle)

The single most citable fact per attraction — *what car do I need to get there* — is rendered as visible text but never as data. In the `TouristAttraction` node (`build.py:2193`), add:

```python
              "additionalProperty": [
                  {"@type": "PropertyValue", "name": "roadSurface", "value": a["road"]},
                  {"@type": "PropertyValue", "name": "requiredVehicleCategory",
                   "value": a["car_category"]},
                  {"@type": "PropertyValue", "name": "distanceFromTbilisiKm",
                   "value": a["distance_tbilisi_km"], "unitCode": "KMT"},
                  {"@type": "PropertyValue", "name": "driveTimeFromTbilisi",
                   "value": a["drive_time_tbilisi"]},
                  {"@type": "PropertyValue", "name": "bestSeason", "value": a["best_season"]},
                  {"@type": "PropertyValue", "name": "openYearRound",
                   "value": bool(a.get("open_year_round"))}],
              "isAccessibleForFree": str(a.get("entry_fee", "")).strip().lower() in ("free", "0", ""),
```

257 pages × 6 languages = **1 542 pages** gain machine-readable road/vehicle data. No new content, no new page, no new claim.

**Expected impact: High.** This is the cheapest large win in the document.

---

### 8.7 P2 — Stop leaking YAML tokens into published prose

Editorial fixes in `content/settings/seo_categories.yml`, `seo_car_rental.yml` and `content/itineraries/*.yml`. Replace in the English (and all localized) copy:

| Published today | Replace with |
|---|---|
| `4x4_only` | *4x4-only* |
| `car_category is economy for all seven days` | *every day of this itinerary runs on economy-class roads* |
| `best_season is 'all' for every component route` | *every leg of this route runs year-round* |
| `mostly-paved rather than fully paved` | *partly unsealed* |
| `not the 4x4_only tracks beyond` | *not the 4x4-only tracks beyond* |

Add a guard to `tests/test_content_quality.py`:

```python
FORBIDDEN_TOKENS = ("4x4_only", "mostly_paved", "car_category", "best_season",
                    "same_to_same", "{attractions}", "{cars}", "{routes}")

def test_no_raw_field_tokens_in_published_text():
    for path in glob.glob("dist/**/index.html", recursive=True) + ["dist/llms.txt"]:
        body = open(path, encoding="utf-8").read()
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        for tok in FORBIDDEN_TOKENS:
            assert tok not in body, f"{tok} leaked into {path}"
```

**Expected impact: Medium.** Perceived authority — an assistant quoting *"roads our data tags 4x4_only"* makes RentUp read like a database, not an operator.

---

### 8.8 P2 — Verify or remove unverifiable business claims

`content/pages/about.yml` publishes, in an extractable stats block: *Rentals per year 4 800+*, *Employees 34*, *utilisation 65 % target / 85 % summer / 45 % winter*, and a *"typical vehicle economics"* table with purchase prices. None is derived from any dataset in this repo. The star display on attraction pages (`rating: 5` → `★★★★★ 5`) reads to an extractor as a customer review score; it is an editorial pick.

Either confirm each figure with the owner and keep it, or delete it. Do **not** add `AggregateRating` or `Review` schema to compensate — the site currently has zero of both, which is the correct and honest state for a business with no verifiable review corpus. Fabricated review markup is the fastest way to earn a manual action and a negative sentiment signal in training data.

**Expected impact: Medium** (risk reduction, not gain).

---

## 9. Answer-shaped content gaps

Mapped to the existing URL scheme in `docs/seo/SEO_URL_MAP.md`. Every one is buildable from data already in `content/` — none requires inventing a fact.

| Target prompt | Best URL today | Gap | Proposed URL | Data source |
|---|---|---|---|---|
| **"Do I need a 4x4 for Tusheti / in Georgia?"** | `/car-rental/4x4/` — good prose, but the evidence is a bulleted list of 8 links | **No table of which places need which car.** 37 attractions are graded `gravel` or `4x4_only`; 17 are `4x4_only`. This is the flagship dataset and it is not presented as an answer. | **New: `/car-rental/4x4/road-requirements/`** or a table section on `/car-rental/4x4/` | `ATTRACTIONS[*].road`, `.car_category`, `.distance_tbilisi_km`, `.drive_time_tbilisi`, `.best_season` — all present |
| **"Can I drive to Ushguli in a sedan?"** | `/attractions/ushguli/` — answers it in prose ("gravel", "Off-road 4x4") | Answer is correct but only reachable if the assistant already found the page. No `additionalProperty` markup (§8.6). No cross-linked "sedan-reachable vs not" comparison. | Same URL + §8.6 markup + a row in the road table above | `content/attractions/ushguli.yml` (`road: gravel`, `car_category: offroad`) |
| **"What does car rental cost in Georgia?"** | `/car-rental/` | Prices in prose and card spans; no table; no `AggregateOffer` | Same URL + §8.2 | `content/cars/*.yml` |
| **"7-day Georgia itinerary by car"** | `/itineraries/georgia-7-days/` | Content is genuinely good; day plan is `<div>` + `<ul>`, not a table; no `HowTo`; per-day km unlabelled as derived | Same URL + §8.5 | `content/itineraries/georgia-7-days.yml` |
| **"Rent a car at Tbilisi airport"** | `/car-rental/tbilisi-airport/` | **2 064 chars — thinnest commercial page on the site.** Missing: terminal/meeting-point description, after-hours procedure (the 20 ₾ night surcharge exists in policy but is not stated here), the 30 ₾ delivery fee prominently, drive times to Tbilisi centre and Kazbegi/Kakheti | Same URL — expand | `rental_policy.yml` (`airport_fee_gel`, `night_surcharge_gel`), `places.yml`, `road_legs.yml` |
| **"Is the Abano Pass open?"** | `/attractions/abano-pass/` | `best_season: june-september`, `road: 4x4_only` exist in the data but there is no seasonal-closure explainer page — a high-volume, recurring, seasonally-spiking query | **New: `/blog/abano-pass-tusheti-road/`** (blog cluster already exists, 4 posts) | `abano-pass.yml`, `omalo-tusheti.yml`, `dartlo.yml`, `shenako-diklo.yml` + the Tusheti route |
| **"Cheapest car rental in Georgia"** | `/car-rental/economy/` | No price-per-duration comparison; `price_7_29` and `price_30` tiers exist on every car but are never tabulated | Same URL — add duration-tier table | `content/cars/*.yml` |
| **"Georgia road trip planner"** | `/trip-planner/` (4 725 chars — solid) | **Contested query with no dominant owner. Most winnable prompt on the list.** Needs the "what makes this planner different" answer: 257 places with road grade and required vehicle — no competitor has that | Same URL — sharpen | `ATTRACTIONS`, `ROUTES` |
| **"Do I need an IDP to drive in Georgia?"** | `/faq/`, `/terms/` | Answered — **but by the contradictory policy set** (§4) | Fix at source (§8.0), then it becomes an asset | `rental_policy.yml → licence_accepted` |
| **"Georgia in winter by car / winter tyres"** | `/faq/` one answer | No dedicated page; `open_year_round` exists on all 257 attractions and is never aggregated | **New: `/blog/driving-georgia-winter/`** | `ATTRACTIONS[*].open_year_round`, `.best_season` |

### Off-site work — the only lever for Presence and Position

Nothing in `build.py` moves Presence from 1/10. The site scores 0 on Position because **no third party has ever mentioned RentUp**. Required, roughly in order of impact per unit of effort:

- [ ] **Google Business Profile** for the Vazha-Pshavela office — the single highest-impact off-site asset for a local business, and the `sameAs` anchor for §8.4(c)
- [ ] Listings on Localrent / Myrentacar as a supplier — competitor-adjacent, but they are how AI-cited marketplaces learn a supplier's name
- [ ] A profile on the review platforms AI assistants actually read for this category (Google Maps, TripAdvisor)
- [ ] Answer the exact questions in the table above where they are being asked *right now* — the Georgia travel subreddits, Caucasus travel forums, Facebook groups — linking the road-grade data, not the booking page
- [ ] Pitch the road-grade dataset to the blogs that currently own the answer space (wander-lush.org, goingthewholehogg.com). *"257 Georgian attractions with verified road grade and required vehicle category"* is a genuinely citable resource and a natural link target
- [ ] Wikidata entry for RentUp as an organization (Wikipedia notability is not met; Wikidata's bar is lower and it feeds knowledge graphs)

---

## 10. Action plan

### P0 — do first, in this order

| # | Action | Where | Impact |
|---|---|---|---|
| 1 | **Reconcile the fact base.** Owner approves `rental_policy.yml`; rewrite `terms.yml`, `faq.yml`, `meta.yml → org_desc` + `llms_facts` to match; add the consistency test | §8.0 | **High** — blocks everything else |
| 2 | Rewrite `llms_txt()` / extend `llms_full_txt()` from `rental_policy.yml` + `cars/*.yml`; add the commercial and itinerary clusters; drop `/account/`; substitute `{attractions}`; omit empty contact fields | §8.3 | **High** |
| 3 | `FAQPage` JSON-LD on the ~2 100 pages that already render Q&A | §8.1 | **High** |
| 4 | Fleet price/deposit table + `AggregateOffer` on `/car-rental/` | §8.2 | **High** |

### P1 — next

| # | Action | Where | Impact |
|---|---|---|---|
| 5 | Fill `site.yml → email` and `social[]` so `Organization` emits `email` + `sameAs` | §8.4(c) | **High** |
| 6 | Fix `org_desc` — remove "full insurance coverage", add "Georgia (the country)" | §8.4(d) | **High** |
| 7 | `additionalProperty` (road, required vehicle, distance, drive time, season) on 1 542 attraction pages | §8.6 | **High** |
| 8 | Itinerary day table + enriched `TouristTrip`; label derived per-day km | §8.5 | **High** |
| 9 | Road-requirements table — the "do I need a 4x4" answer | §9 row 1 | **High** |
| 10 | Expand `/car-rental/tbilisi-airport/` from 2 064 chars | §9 row 5 | Medium |
| 11 | `<link rel="alternate" type="text/markdown">`; `robots.txt` additions | §8.4(a,b) | Medium |

### P2 — hygiene

| # | Action | Where | Impact |
|---|---|---|---|
| 12 | Strip raw YAML tokens from published prose + regression test | §8.7 | Medium |
| 13 | Verify or remove the `/about/` operational claims; reconsider `★★★★★` on attractions | §8.8 | Medium (risk) |
| 14 | Duration-tier price table on `/car-rental/economy/` | §9 row 7 | Medium |
| 15 | `/blog/abano-pass-tusheti-road/`, `/blog/driving-georgia-winter/` | §9 | Medium |
| 16 | Off-site: GBP, marketplace listings, review profiles, dataset outreach | §9 | **High, slowest** |

---

## Content to create

- [ ] **Road requirements table** — 37 places graded gravel/4x4-only with required category, drive time and season. Targets *"do I need a 4x4 in Georgia"*, *"can I drive to Ushguli in a sedan"*. Data: `ATTRACTIONS`.
- [ ] **`/blog/abano-pass-tusheti-road/`** — the seasonal-closure answer, honestly scoped ("depends on snow conditions each year"). Targets *"is Abano Pass open"*.
- [ ] **`/blog/driving-georgia-winter/`** — built from `open_year_round` + `best_season`. Targets *"Georgia in winter by car"*.
- [ ] **Airport-page expansion ×3** — terminal, after-hours, fees, drive times. Targets *"car rental Tbilisi airport"*.
- [ ] **Duration-price comparison** on `/car-rental/economy/` from `price_1_6` / `price_7_29` / `price_30`. Targets *"cheap car rental Georgia"*.
- [ ] **`/trip-planner/` sharpening** — lead with the differentiator (road grade + required vehicle on 257 places). The most winnable prompt in the set.

---

## Measurement

Before claiming any movement, establish a baseline. AI training corpora refresh on a scale of weeks to months; retrieval-based answers (Perplexity, ChatGPT search, Claude with search) update within days of a crawl.

- Run the 10 prompts in §2 monthly against ChatGPT, Claude, Gemini and Perplexity; log mentioned / position / sentiment / accuracy verbatim.
- Watch server logs for `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `Claude-SearchBot`, `PerplexityBot` — crawl frequency is the leading indicator; answer presence is the lagging one.
- Track referral traffic from `chat.openai.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`.
- **Expected trajectory:** the technical work (P0 + P1) is a prerequisite, not a cause. Score should move 27 → ~45 on Accuracy, Consistency and Completeness alone within a build cycle. Presence and Position will not move without the off-site work in §9, and realistically not for 3–6 months after it starts.

---

## Sources

- [Renting a Car in Tbilisi & Driving in Georgia in 2026 — Wander-Lush](https://wander-lush.org/driving-in-georgia-car-rental-tbilisi/)
- [Georgia (Country) Road Trip: An Adventurous 10 Day Itinerary — Wander-Lush](https://wander-lush.org/georgia-country-road-trip-itinerary/)
- [Western Georgia Road Trip: A Relaxed 7 Day Itinerary — Going the Whole Hogg](https://www.goingthewholehogg.com/western-georgia-road-trip-itinerary/)
- [What to do in Georgia in a 7-day itinerary — Against the Compass](https://againstthecompass.com/en/georgia-itinerary/)
- [Rent a Car in Georgia, Cheap Car Rental — Localrent](https://www.localrent.com/en/georgia/)
- [Renting a Car in Georgia: Everything You Need to Know — Road is Calling](https://www.roadiscalling.com/renting-a-car-in-georgia-country/)
- [Tusheti 4x4 Guide: Abano Pass Self-Drive 2026 — FSTA Rent Car](https://fstarentcar.com/blog/tusheti-4x4-adventure-guide-abano-pass/)
- [Tbilisi to Tusheti: Abano Pass Guide — FSTA Rent Car](https://fstarentcar.com/blog/tbilisi-to-tusheti-abano-pass-transport-guide/)
- [Tusheti: How to Get There and What to See — Sunny Georgia](https://sunnygeorgia.travel/blog/en/tusheti-travel-guide)
- [Jeep tours in Georgia: the routes that need a 4x4 — Georgia Spirit](https://www.georgia-spirit.com/guides/jeep-tours-georgia/)
- [Car Rental in Georgia – Complete Guide and Hidden Pitfalls (2026) — TripLinkHub](https://www.triplinkhub.com/en/blog/car-rental-georgia-guide)
- [Cheap car hire in Tbilisi, Georgia — Skyscanner](https://www.skyscanner.net/car-hire-in/car-hire-in-tbilisi/27547139.html)

*For continuous AI visibility monitoring across ChatGPT, Claude, Gemini and Perplexity, see [SearchFit.ai](https://searchfit.ai).*
