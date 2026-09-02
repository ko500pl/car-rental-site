# AI Citation Plan: which sources answer engines use for "car rental in Georgia", and how RentUp gets into them

Date: 2026-09-01 · Domain: https://rentup.ge · Follows `docs/seo/AI_VISIBILITY.md` (2026-08-29 audit)
Method: the retrieval queries an assistant issues for this topic were run through web search (EN + RU); recurring domains were opened and inspected for *how a company gets named there*; rentup.ge's own AI-facing surface (`/llms.txt`, `/robots.txt`, `/car-rental/`, `/car-rental/airport-pickup/`, three `/guides/*`) was fetched live on 2026-09-01. Facts in the answer blocks (§4) come only from `content/settings/rental_policy.yml`, `content/pages/faq.yml`, `content/settings/seo_car_rental.yml` and `content/guides/*.yml`. **No production file was changed.**

> **Read this first.** Answer engines do not rank car-rental companies; they repeat whoever the *travel blogs, TripAdvisor forum regulars and Russian-language "личный опыт" articles* already name. In every English retrieval set the same four names came back — Localrent, GoTrip, Martyna z Gruzji, Discover Cars — because three bloggers with affiliate links and two TripAdvisor forum regulars say so. RentUp appeared in none of the 14 query sets. There is no shortcut: the path in is (a) a verifiable listing on TripAdvisor + Google Business Profile so the *brand exists as an entity*, (b) real customers leaving real reviews there, (c) getting RentUp's road-condition dataset in front of the five or six bloggers who own the "renting a car in Georgia" answer, and (d) making rentup.ge pages so quotable that Perplexity/ChatGPT pick them up directly for the *road* questions (4x4, Kazbegi, documents), where no aggregator has better data.

---

## 1. What the retrieval layer actually returns

Queries run 2026-09-01 (US-locale search index; results are the URLs an assistant's own search tool sees before it writes an answer).

| Query | Domains returned (in order) | Type |
|---|---|---|
| best car rental company in georgia country | ensun.io (directory), sixt.com, vipcars.com, avis.com (**US Georgia**), cars4rent.ge, yelp.com (**Atlanta**), europcar.com, geodrive.info | Brand/aggregator pages; state-of-Georgia pollution |
| car rental georgia reddit | kayak.com ×4 (**US Georgia**), skyscanner, travelocity, expedia ×2 | 100 % US-state noise, zero Reddit threads surfaced |
| is it safe to rent a car in georgia | roadiscalling.com, **wander-lush.org**, passaportenobolso.com, **localrent.com/journal**, **discovercars.com/blog**, tripwis.com, og.ge/blog, travelwithfoldbjerg.com, unitedcarsrent.com/blog | Blogs + aggregator blogs |
| renting a car in georgia tips tbilisi | **wander-lush.org**, thewholeworldisaplayground.com, localrent.com, og.ge, tripmydream.com, kayak, skyscanner | Blogs + aggregators |
| car rental tbilisi reviews | **tripadvisor.com** (product review + forum thread), gsscarrental.com, tbilisiautorent.com, kayak ×2 | TripAdvisor + local sites |
| 4x4 rental georgia recommendations | tripadvisor.com (Overlando review), ountravela.com, fill.ge, carrentalservice.ge, starcar.ge/blog, rentalcartbilisi.com, overlando.com, pampacruz.com, rentcarsgeorgia.com/blog, **georgia-spirit.com** | Local operator blogs + one listicle |
| tripadvisor car rental Georgia which company | **tripadvisor.com Georgia Forum** ×7 threads ("Best car rental company in Tbilisi for a 10-day road trip?", "Recommended car rental", "no credit card needed", "cross border Armenia & Azerbaijan"), Cars & Host review | Forum |
| аренда авто в грузии отзывы | howtrip.ru, **vc.ru/travel** (rating article), tip-to-trip.com, georgia.in-facts.info, trip-blog.ru, App Store (Localrent app) | RU personal-experience blogs |
| какую компанию выбрать аренда авто грузия | **vc.ru** ×2, **dtf.ru** (ТОП-6 без депозита), tonkosti.ru, aleksblog.com, tip-to-trip.com, geodrive.info | RU rating/listicle articles |
| (Reddit-restricted searches) | Proxy refused domain-restricted query; unrestricted "reddit" queries returned no reddit.com results at all | See §2.3 |

Note on the query set: `car rental georgia reddit` and `best car rental company in georgia` are **dominated by the US state**. Any assistant that does not append "country"/"Tbilisi"/"Caucasus" gets Kayak/Atlanta. This is why the disambiguation rule from the previous audit (every page says *Georgia (the country)* in prose, not just in `areaServed`) is load-bearing: it decides whether a retrieval even lands on the right continent.

### 1.1 Who the recurring sources themselves recommend

Opened and read (2026-09-01):

| Source | Companies named | How they got there | Last updated |
|---|---|---|---|
| **wander-lush.org** "Renting a Car in Tbilisi & Driving in Georgia in 2026" | Local Rent ("rented through more than a dozen times"), GoTrip, Martyna z Gruzji (discount code), Hertz/Europcar via DiscoverCars | Personal use + affiliate links; affiliate disclaimer present; no submission policy stated | 2026-08-23 |
| **roadiscalling.com** "Renting a Car in Georgia" | LocalRent (affiliate `?r=3920`), DiscoverCars, RentalCars; comments add "Tbilisi Car Rental" (border crossing) and a WhatsApp-only "Sergey" | Affiliate + reader comments | 2024-09-18 |
| **TripAdvisor Georgia Forum** "Best car rental company in Tbilisi for a 10-day road trip?" | Martyna z Gruzji + LocalRent (worldcitizen1961), WeRent ×2 (two travellers, "delivered it to the airport… WhatsApp support"), DiscoverCars/QEEQ/RenACar, Auto Europe | Traveller posts; **one reply removed as inappropriate** | thread live |
| **TripAdvisor Georgia Forum** "Recommended car rental" | Enterprise ×2, Auto Europe, Discover Cars, VIP Cars; Destination Expert *trip4realGEORGIA* (1,923 posts) answers on cross-border | Traveller posts; **one post removed by staff for self-promotional advertising** | thread live |
| **vc.ru** "Аренда авто в Грузии 2026: рейтинг сервисов и личный опыт" (Andrey, Re:Trust) | Localrent (top, 6 trips since 2021, names partner **Naniko** and a manager), GetRentacar, EconomyBookings (partners Autogrand, Sixt, Hertz, Budget) | Personal experience + `tpo.li` referral links | 2026-04-23 |
| **georgia-spirit.com** "Renting a car in Georgia: honest guide" | Hertz, Sixt, Europcar, Enterprise, Budget, Avis; local: Naniko, MyRentACar, Rental Cars Georgia, Top Rent | Market-presence list, no endorsements, no submission policy | "Last reviewed 2026-07-12" |

Pattern: **every named local company got there through one of three doors** — a marketplace listing (Localrent/GetRentacar/EconomyBookings partner → the blogger names the partner that delivered the car, e.g. Naniko, Autogrand), a traveller who had a good airport handover and said so on TripAdvisor (WeRent), or a blogger's personal rental with an affiliate arrangement (Martyna z Gruzji, GoTrip).

---

## 2. The top source domains and how to get on each — legitimately

Ranked by how often they recur across the query sets *and* how much an assistant trusts them. "Off-limits" marks anything that amounts to fake or undisclosed endorsement; do not do it, and do not pay anyone to do it.

### 2.1 TripAdvisor — Georgia Forum + Tbilisi "Car Hire"/Attraction listings (`tripadvisor.com`)
Recurs in 4 of 9 query sets; the only place with both reviews *and* Q&A threads that assistants quote by name.
- **Listing:** RentUp has no TripAdvisor presence. Claim/create a business listing (competitors sit under *Tbilisi › Transportation › Taxis & Shuttles / Car Hire* as "Attraction" products: Tbiliso Car Rental, GSS Car Rental, RENT AUTO GEORGIA, Cars & Host). Use the legal name, the Vazha-Pshavela 71 address, the +995 597 55 55 65 number, and the same description text as `/about/` so entity data matches across properties.
- **Reviews:** only from real customers, asked *after* the return, with a direct link to the listing on the handover e-mail/WhatsApp. TripAdvisor's fraud detection and its "Review Express" tool are the sanctioned route. **Off-limits:** incentivised reviews, staff/family reviews, review swaps with other operators, bought reviews — TripAdvisor penalises with a public red badge that an assistant *will* quote.
- **Forum:** a business owner may answer in the Georgia Forum **only with a disclosed identity** (profile states "Owner, RentUp car rental, Tbilisi") and **only with information, never a pitch** — e.g. answering "do I need a 4x4 for Ushguli?" with the road-grade facts and a link to the guide page. Two threads in §1.1 show staff removing self-promotional posts; the Destination Expert *trip4realGEORGIA* is the model — 1,900 informative posts, zero sales copy. Aim to become a DE for "Georgia" over 12 months by answering road/driving questions.

### 2.2 wander-lush.org (Emily Lush)
The single most-cited travel authority for Georgia; updated August 2026; cited by everyone else in the set.
- **How companies get in:** she names only services she has personally used, with affiliate links (Localrent, GoTrip, Martyna z Gruzji discount code).
- **Legitimate route:** (1) offer a *dataset*, not a car — the 267-place road-grade/car-category table and the 4x4 guide are the kind of resource her "driving in Georgia" post links to as a reference; (2) offer a genuine press rental for a specific route she has not covered (e.g. Racha 5-day) with full disclosure on her side; (3) set up an affiliate/referral code so a mention can be commercially neutral for her — her disclaimer page shows she uses them. **Off-limits:** paying for an undisclosed mention, or asking her to copy RentUp marketing text.

### 2.3 Reddit — r/Sakartvelo, r/travel, r/solotravel
Reddit is the heaviest single weight in LLM training data for "which company" questions, but this search index returned **zero Reddit URLs** for any Georgia-country car-rental query (and refused the domain-restricted search). Treat the earlier audit's assumption "Reddit threads dominate" as unverified for this niche; the *forum* that actually surfaces is TripAdvisor. Still worth doing because assistants with live Reddit access (Perplexity, ChatGPT search) weigh it:
- **Legitimate route:** one account, flair or bio "RentUp car rental, Tbilisi (owner)", answers *only* road/route/documents questions with facts and links to the guide pages; never "DM me" or price posts; follow r/Sakartvelo's self-promotion rule (could not fetch the rules page — read it before the first post). Reply when someone asks "Abano Pass open?", "sedan to Ushguli?", "IDP needed?". One helpful answer a week for a year beats anything else.
- **Off-limits:** sock-puppet "I used RentUp and loved it" posts, asking customers to post reviews on Reddit, upvote rings.

### 2.4 Localrent.com (marketplace + `localrent.com/journal`)
Named first in wander-lush, roadiscalling, vc.ru, TripAdvisor; its *journal* ("Prohibited routes for rental cars in Georgia") also ranks for the safety query. Bloggers then name the **partner operator** that handed over the car (vc.ru names Naniko and a manager by name).
- **Legitimate route:** list RentUp's fleet as a Localrent supplier (standard supplier onboarding; they verify the company and cars). Every Localrent booking becomes a chance for the blogger/traveller to name RentUp as "the local company Localrent sent". Check the commission against the 75–330 ₾/day rates before committing the whole fleet; listing only the 4x4s and SUVs (the categories aggregators are thin on) is a reasonable first step.
- Same logic, smaller weight: **GetRentacar**, **EconomyBookings**, **Discover Cars** (supplier programme), **Myrentacar** (RU market).

### 2.5 Russian-language personal-experience platforms — vc.ru, dtf.ru, tonkosti.ru, howtrip.ru, tip-to-trip.com, aleksblog.com
The RU query sets are entirely "личный опыт" articles with referral links, plus tonkosti.ru (an editorial encyclopaedia). `/ru/` is a full locale on rentup.ge and Russian is a top inbound market.
- **vc.ru / dtf.ru:** anyone can publish under their own name. **Legitimate route:** publish under the company's own name, in Russian, the road-grade guides (Казбеги по участкам, нужен ли 4x4, документы) — informational, with one link to rentup.ge/ru/, clearly labelled as by RentUp. These platforms' travel sections are exactly what the RU retrieval returns. **Off-limits:** ghost-written "мой опыт с RentUp" reviews under a traveller persona.
- **tonkosti.ru:** editorial; write to the editors with the dataset/guide as a source to cite in the "Аренда авто в Грузии" article.
- **aleksblog.com / tip-to-trip / howtrip:** same as §2.2 — offer data or a disclosed press rental.

### 2.6 Google Business Profile / Google Maps (`google.com/maps`)
Not in the search sets above (Maps results are not returned as web pages) but it is the entity source assistants — Gemini in particular — reconcile a company name against, and the `sameAs`/review count feed into "is this a real business".
- **Legitimate route:** claim the profile at Vazha-Pshavela 71 with matching name, hours 09:00–21:00, phone, website; add the fleet photos; ask real customers for reviews via the post-return message. Add the GBP URL to `site.yml → social` so it appears as `sameAs`. **Off-limits:** review gating, bought reviews.

### 2.7 Aggregator blogs and Georgia-specific listicles — discovercars.com/blog, localrent.com/journal, og.ge/blog, georgia-spirit.com, ountravela.com ("4x4 rental in Georgia — the best rental agencies")
These pages *list local companies*. georgia-spirit's "local operators" list (Naniko, MyRentACar, Rental Cars Georgia, Top Rent) and ountravela's 4x4 list are editorial with no stated criteria.
- **Legitimate route:** e-mail the editor with a one-paragraph factual entry (fleet, categories, deposit, cross-border, 4x4 policy, URL) and the road-grade guide as a reason to include RentUp specifically in the *4x4 / mountain* section, where the fleet (Pajero 235 mm, Prado 220 mm, Delica 210 mm) is a genuine differentiator. Ask for correction, not praise. **Off-limits:** paying for placement without a "sponsored" label.

### 2.8 Trustpilot (`trustpilot.com/review/cars4rent.ge` surfaced for "car rental Georgia Tbilisi")
A competitor's Trustpilot page ranks for the brand-agnostic query, which is why a review profile matters even at low volume.
- **Legitimate route:** create the free `trustpilot.com/review/rentup.ge` profile and invite customers post-return with Trustpilot's own invitation link. **Off-limits:** as above.

### 2.9 Also present, lower priority
- **Lonely Planet forum (Thorntree)** — closed in 2021; no live threads surfaced. Skip.
- **Nomadic Matt** — no Georgia car-rental content surfaced. Skip.
- **ensun.io** "Top 13 car rental companies in Georgia" — auto-generated directory; free company profile, harmless, low weight.
- **Kayak / Skyscanner / Expedia** supplier pages — only reachable through a broker (e.g. Auto Europe, Discover Cars); indirect.
- **Local operator blogs** (fstarentcar, starcar.ge, rentcarsgeorgia, unitedcarsrent, og.ge) — these are competitors doing the same play. Beat them on data, not on link exchanges.

---

## 3. What rentup.ge exposes to AI crawlers today (live, 2026-09-01)

### 3.1 `/robots.txt` — good, nothing to change
All 22 AI user-agents from the previous audit are explicitly allowed (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, Claude-SearchBot, anthropic-ai, PerplexityBot, Perplexity-User, Google-Extended, Applebot(-Extended), Bingbot, CCBot, Meta-ExternalAgent, cohere-ai, YandexBot, Amazonbot, DuckAssistBot, MistralAI-User, Bytespider, Google-CloudVertexBot); `/admin/ /account/ /trip/ /app/` disallowed; sitemap declared. Only the optional `Llms:` hint line is absent.

### 3.2 `/llms.txt` — facts now correct, still the wrong shape
- 100 KB, 437 lines; 267 attraction lines make up two thirds of it. The spec wants a short index; the exhaustive dump belongs in `llms-full.txt`.
- **Key facts are now consistent with `rental_policy.yml` / `faq.yml`** (CDW+TPL included, excess 300–1,200, SCDW 25–45, cross-border Armenia 150 / Turkey 250, cancellation 48 h tiers, age 21/23/25). The 2026-08-29 contradiction is resolved here.
- It now lists all `/car-rental/*` pages and the 5 itineraries. **It does not list a single `/guides/*` page** — the eleven guides (4x4, documents, Kazbegi, Svaneti, Tusheti, winter, day trips, best time) are the most quotable content on the site and are invisible in the one file written for assistants. Only the four `/blog/` posts are under "## Articles".
- Doubled apostrophes leak: `RentUp''s`, `class''s` (lines 46–47, from YAML-quoted strings) — an assistant quoting the business/van line will reproduce them.
- Live file differs from a fresh local build in two data lines (Imereti route driving time 12:45 vs 10:30; Waterfall of Love season) — the deployed build is slightly behind `content/`.

### 3.3 The commercial pages
- `/car-rental/` (9,765 chars, 1 table, `FAQPage` present): still says **"same-to-same"** fuel in the Fuel section, while `rental_policy.yml`, `faq.yml`, the requirements guide and `/car-rental/airport-pickup/` all say **full to full**. This is the last live policy contradiction on the hub and it sits in the exact sentence an assistant would quote for "what is the fuel policy". Fix `seo_car_rental.yml → hub.en.sections.fuel.body` (and the other five languages).
- `/car-rental/` delivery section gives airport fees (40/60/50 ₾) **without the free-from-day-3/day-5 thresholds** that `/car-rental/airport-pickup/` states. Not a contradiction, but the hub is where the "airport fee" fact gets lifted from, and the incomplete version is the one that will be quoted.
- `/car-rental/airport-pickup/` (6,080 chars, `Service` + `Airport` JSON-LD, **no `FAQPage`**): the `good_to_know` bullets are already FAQ-shaped; render them as `<details>` + `FAQPage` the way the hub does.

### 3.4 The three guide pages — quotable, with four gaps
| Page | Body chars | Tables | `FAQPage` | `Article.dateModified` | Visible date | Author line | Raw tokens in prose |
|---|---|---|---|---|---|---|---|
| `/guides/do-i-need-a-4x4-in-georgia/` | 7,940 | 4 | yes (8 Q) | 2026-08-30 | **none** | schema only (`author → #organization`) | **16** `<code>` tokens (`paved`, `mostly_paved`, `4x4_only`, `offroad`) |
| `/guides/car-rental-georgia-requirements-documents/` | 8,538 | 3 | yes (10 Q) | 2026-09-01 | **none** | schema only | 0 |
| `/guides/road-to-kazbegi-georgian-military-highway/` | 8,438 | 1 | yes (8 Q) | 2026-09-01 | **none** | schema only | 3 |

Judgement: **these are already the best citation candidates on the site** — declarative sentences, real numbers with units, per-category tables, every claim traceable to YAML, and an explicit "what this page does not tell you" disclaimer (which raises trust, not lowers it). The 4x4 guide's opening ("227 places — 85.0% — sit at the end of paved or mostly paved roads… The number of places where a genuine off-road vehicle is not optional is 17") is exactly the sentence shape assistants lift. What is missing is the *framing* an extractor uses to decide whether to trust and attribute the page:

1. **No visible date.** `dateModified` exists in JSON-LD but no human-readable "Last verified" line. Perplexity/ChatGPT show and weigh visible dates; a 2026 date next to "Georgia road conditions" is a ranking signal against the 2024 blog posts they currently cite.
2. **No visible author/organisation line.** The `Article.author` is the organisation `@id`, which is correct, but the page never says in text *who* counted the 267 places and *why they would know*. One sentence — "Published by RentUp, a car rental company in Tbilisi; road grades are recorded by our own fleet team" — is the E-E-A-T line assistants look for.
3. **No key-facts box.** The answer is spread across the first three paragraphs. A 5-line box at the top (the §4 blocks) gives the extractor a single span to quote.
4. **Raw field tokens in `<code>`** (`4x4_only`, `mostly_paved`) will be quoted verbatim as jargon. Keep the concept, drop the monospace: "4x4-only", "mostly paved".

### 3.5 Concrete edits (all in `build.py: render_guide()` at ~line 4633 unless stated)

| # | Edit | Where | Impact |
|---|---|---|---|
| E1 | **Key-facts / answer block** at the top of each guide and the two commercial pages: a `<div class="keyfacts">` with a 60–90-word declarative paragraph (texts in §4). Store as `en.answer:` in each guide YAML and `hub.en.answer` / `services.airport-pickup.en.answer` in `seo_car_rental.yml`; render immediately after `<p class="lead">`. Also emit it as `Article.abstract` (guides) / `WebPage.abstract` (hub) in JSON-LD, and as the `speakable` target (`cssSelector: [".keyfacts"]`). | `render_guide()` body string; `render_car_rental_hub()` ~4060; airport-pickup renderer | High — one quotable span per page |
| E2 | **Visible "Last verified" line** using the existing `updated:` field: `<p class="meta"><time datetime="2026-09-01">Last verified 1 September 2026</time> · Source: RentUp road data and rental terms</p>` directly under the H1. Add `datePublished` (introduce `published:` in the guide YAML) so `dateModified` is not the only date. | `render_guide()`; guide YAMLs | High — the date is currently invisible to humans and to extractors that read text |
| E3 | **Author/organisation line in text**, not only in schema: "By RentUp — car rental, Tbilisi, Georgia (the country). Road grades and car categories are recorded by our own team for all 267 places we map." Append `"author": {"@id": …}` → keep, and add an `Organization.knowsAbout` list (`"Car rental in Georgia", "Georgian road conditions", "Georgian Military Highway"`) to `org_node()`. | `render_guide()`; `org_node()` ~586 | Medium — E-E-A-T attribution |
| E4 | **Remove `<code>` styling from data tokens** in guide prose: in `render_md()` for guides, or by editing the three YAML bodies (`\`paved\`` → "paved", `\`4x4_only\`` → "4x4-only", `\`mostly_paved\`` → "mostly paved"). 19 occurrences across the three pages. | `content/guides/do-i-need-a-4x4-in-georgia.yml`, `road-to-kazbegi….yml` | Medium — stops jargon being quoted |
| E5 | **Add `/guides/*` to `llms.txt`** as a `## Guides` section right after `## Key facts` (name, URL, `short`, `updated`), and move the 267 attraction lines out to `llms-full.txt` so the index drops from 100 KB to < 15 KB. | `llms_txt()` ~3400–3495 | High — the guides are the citation targets and are absent from the AI index |
| E6 | **Fix the last policy contradiction**: `hub.en.sections.fuel.body` "same-to-same" → "full to full"; add the free-from-day-3/5 thresholds to `hub.en.sections.delivery.body`. Mirror in ka/ru/fa/he/ar. Extend `tests/test_content_quality.py` to assert "same-to-same" no longer appears anywhere in `content/`. | `content/settings/seo_car_rental.yml` | High — stops the wrong fuel policy being quoted from the hub |
| E7 | **`FAQPage` on `/car-rental/airport-pickup/`** from its `good_to_know` list (reuse `faq_items_node()`); add a 3-row fee table (`Airport | Fee 1–2 / 1–4 days | Free from`). | airport-pickup renderer | Medium |
| E8 | **Escape fix in `llms_txt()`**: `RentUp''s` → `RentUp's` (unescape the YAML-doubled apostrophe before writing). | `llms_txt()` | Low, cheap |
| E9 | **`sameAs`** — fill `site.yml → social` with the TripAdvisor, Google Business Profile and Trustpilot URLs from §2 once they exist; `org_node()` already emits them. Add `Llms: https://rentup.ge/llms.txt` to `robots()` and `<link rel="alternate" type="text/markdown" href="/llms.txt">` to `head_html()`. | `site.yml`, `robots()`, `head_html()` | Medium — entity reconciliation |
| E10 | **Redeploy** — the live `llms.txt` is behind the current `content/` (two data lines differ). | CI | Low |

---

## 4. The five answer blocks (English, 60–90 words, lift-verbatim)

Every number below is traceable to the repo: `rental_policy.yml` (age, licence years, deposit handling, fuel, delivery fees, night surcharge, one-way, cancellation, extras, insurance, cross-border), `faq.yml` (prices, 24/7 roadside assistance, winter tyres, SCDW), `seo_car_rental.yml` (airport thresholds, hub facts), `content/cars/*.yml` (75 ₾ Prius, 240 ₾ Pajero, clearances), `content/guides/*.yml` (road counts, distances, altitudes). Wire each as `answer:` per E1. Word counts in brackets.

### 4.1 `/car-rental/` — "Car rental in Georgia" [90]

> RentUp is a car rental company in Tbilisi, Georgia (the country), with 17 vehicles in six categories, from 75 ₾ a day for an economy car to 240 ₾ for an off-road 4x4. Every rental includes unlimited mileage inside Georgia, CDW and TPL insurance and 24/7 roadside assistance. Drivers must be 21 or over with a licence held 2 years. The deposit is 300–1,200 ₾ by category, blocked on a card and released within 3 business days. Fuel is full to full. Nothing is prepaid; cancellation is free more than 48 hours ahead.

### 4.2 `/guides/do-i-need-a-4x4-in-georgia/` — "Do you need a 4x4 in Georgia?" [89]

> Most of Georgia does not need a 4x4. Of the 267 places in RentUp's road database (counted 30 August 2026), 227 — 85 % — are reached on paved or mostly paved roads, and 181 are rated for an ordinary economy car. Only 17 places are 4x4-only, all seasonal, mostly June to September: Tusheti via the Abano Pass (2,850 m), Juta, Shatili and Dartlo. Ushguli is gravel and needs the off-road category; Mestia, the Kazbegi road and all of Kakheti are paved. An SUV covers 63 places; a 4x4 the remaining 23.

### 4.3 `/guides/car-rental-georgia-requirements-documents/` — "Requirements and documents" [88]

> To rent a car in Georgia from RentUp you need a passport, a driving licence held at least 2 years, and a card or cash for the deposit. An International Driving Permit is needed only if the licence is not in the Latin alphabet; EU, US, UK, Israeli and CIS licences are accepted as they are. Minimum age: 21 economy, 23 SUVs and minivans, 25 business and 4x4. The deposit, 300 ₾ (economy) to 1,200 ₾ (4x4), is blocked not charged and released within 3 business days. Nothing is prepaid.

### 4.4 `/car-rental/airport-pickup/` — "Airport car rental in Georgia" [89]

> RentUp delivers rental cars to all three international airports in Georgia and meets you at arrivals with a name sign: Tbilisi (TBS) costs 40 ₾ and is free from the third rental day; Batumi (BUS) 50 ₾ and Kutaisi (KUT) 60 ₾, both free from the fifth day. Handover runs 24 hours; a pickup or return between 22:00 and 07:00 adds a 40 ₾ night surcharge. Give your flight number when booking and bring a passport, licence and a card for the 300–1,200 ₾ deposit. A one-way return between the three cities costs 100 ₾.

### 4.5 `/guides/road-to-kazbegi-georgian-military-highway/` — "The road to Kazbegi" [90]

> The Georgian Military Highway from Tbilisi to Stepantsminda (Kazbegi) is paved throughout: Ananuri at 70 km, Gudauri at 120 km (2,200 m), the Jvari Pass at 125 km (2,380 m) and Stepantsminda at 155 km, about three hours. An economy car is enough for the main road; the final 6 km concrete climb to Gergeti Trinity Church (2,170 m) is rated SUV. Only the side valleys, Truso (gravel) and Juta (4x4-only), need an off-road 4x4, June–September. RentUp fits winter tyres 1 December to 1 April; Gudauri closes periodically in winter.

**Readiness:** all five are wired-in ready as `answer:` strings for E1. One caveat on 4.1: it states "full to full", which is correct per `rental_policy.yml`/`faq.yml`/`terms` but contradicts the hub's own Fuel section until E6 lands — ship E6 in the same commit. 4.2 names Shatili and Dartlo from `content/attractions/*.yml` (`road: 4x4_only`), not from the guide text; they are in the dataset the guide counts.

---

## 5. Sequence

1. **This week, in the repo:** E6 (fuel contradiction), E1 (answer blocks), E2 (visible date), E3 (author line), E4 (drop `<code>` tokens), E5 (guides into `llms.txt`), E8, E10. All inside `build.py` + YAML; no external dependency.
2. **This month, off-site, entity first:** TripAdvisor listing, Google Business Profile, Trustpilot profile — then put their URLs into `site.yml → social` (E9). Start the post-return review request (one message, one link, no incentive).
3. **Next 90 days, distribution:** Localrent supplier listing for the SUV/4x4 categories; disclosed-identity answers on TripAdvisor Georgia Forum and r/Sakartvelo to road/document questions (target: 2 per week, zero pitches); the three Russian guides republished under RentUp's name on vc.ru; outreach to wander-lush, georgia-spirit, ountravela and tonkosti.ru offering the road-grade dataset and the 4x4 guide as a source — ask to be *cited*, not praised.
4. **Measure:** re-run the nine queries in §1 monthly; the first success signal is not a RentUp result for "best car rental company" but a `rentup.ge/guides/…` URL appearing for "do I need a 4x4 in Georgia" / "Georgian Military Highway road conditions", where no aggregator holds better data.
