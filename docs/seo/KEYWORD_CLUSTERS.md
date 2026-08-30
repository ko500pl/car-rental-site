# RentUp.ge — Keyword Clusters (ka · en · ru)

Companion to `SEO_KEYWORD_MAP.md` (which fixes *one primary intent per page*) and
`SEO_URL_MAP.md` (which fixes *which URLs may exist*). This file does the layer
underneath both: it enumerates the **query space** in the three commercially
important languages, groups it into clusters, and says for each cluster whether
the site can serve it today, with what data.

Nothing here overrides those two documents. Where this file proposes a URL that
`SEO_URL_MAP.md` does not list, it is marked **NEW URL NEEDED** with the exact
path, and the reason a `/car-rental/{city}` style doorway page is *not* being
proposed instead.

**Compiled:** 2026-08-29 · **Site snapshot:** 17 cars · 6 categories · 6 pickup
points · 32 routes · 5 itineraries · 257 attractions · 11 regions · 4 blog posts.

---

## 0. How to read this file

### 0.1 Evidence base — read before trusting a number

No keyword-volume tool (Ahrefs / Semrush / Keyword Planner / Search Console) was
available in this environment. **Every volume figure in this document is a
labelled estimate, not measured data.** Where a number would be invented, a band
is given instead, with the reasoning stated.

| Band | Meaning | How it was inferred |
|---|---|---|
| **High** | plausibly 1,000+/mo for this language, Georgia market | SERP is fully commercial: paid ads, OTA aggregators (Localrent, DiscoverCars, Rentalcars), multiple purpose-built landing pages competing |
| **Medium** | plausibly 100–1,000/mo | SERP is mixed: a few dedicated commercial pages plus blogs/forums; no ad saturation |
| **Low** | plausibly <100/mo | SERP falls back to forums, Tripadvisor threads, generic hub pages, or classifieds — nobody has built a page for the query |
| **Unknown** | genuinely unclear | stated explicitly rather than guessed |

**These bands must be replaced with Search Console + a keyword tool before any
budget decision is made.** They are good enough to rank *relative* priority, not
to forecast traffic.

Difficulty is expressed the same way, from observed SERPs on 2026-08-29:

| Difficulty | What was observed |
|---|---|
| **Very High** | OTA aggregators + ads own the whole first page (Localrent, Myrentacar, DiscoverCars, Rentalcars, Expedia) |
| **High** | 5+ established Georgian rental operators with dedicated landing pages (carrentgeorgia.ge, gsscarrental.com, geocarrent.ge, starcar.ge, cars4rent.ge, geodrive.info, triprents.com, autohub.rent) |
| **Medium** | one or two operator pages, rest is blog/editorial (wander-lush.org is the dominant English travel authority in this niche) |
| **Low** | forums, Tripadvisor, DRIVE2 posts, classifieds aggregators (manqanebi.ge, servisebi.ge, binebi.info), or nothing purpose-built at all |

### 0.2 Status vocabulary

| Status | Meaning |
|---|---|
| **covered** | a URL exists, in all three languages, with copy that actually answers the query |
| **thin** | the URL exists but the cluster's specific question is answered in one line or not at all |
| **missing** | no URL addresses this intent; the cluster is unserved |
| **blocked** | cannot be published until a source-data conflict or gap is resolved (see §5.3) |

### 0.3 Prioritisation formula used

`priority = intent value × achievability`, never volume alone.

- **intent value** — how close the query is to a booking, or to the one decision
  only this site can help with (which car for which road).
- **achievability** — whether the site holds data a competitor does not, and
  whether the SERP is winnable by a new domain within ~2 quarters.

The consequence: the highest-volume head terms (`car rental Tbilisi`,
`аренда авто в Грузии`) are **not** at the top of the build list. They are Very
High difficulty against aggregators with years of authority. The top of the build
list is the intersection of *high commercial intent* and *data nobody else has* —
the per-attraction `road` / `car_category` / `best_season` / `distance_tbilisi_km`
fields across 257 places, which turn "do I need a 4x4?" into an answerable,
defensible page.

---

## 1. Language notes — why the three sets are not translations

### 1.1 Georgian (ka)

Georgian rental search does **not** mirror English. Observed on real SERPs:

- The dominant noun phrase is **მანქანის ქირაობა** ("car hire"), not
  ავტომობილის დაქირავება. `ავტომობილის ქირაობა` / `ავტომობილის დაქირავება` are
  the formal register and appear mostly in operator page titles, not in the way
  people type.
- **მანქანების ქირაობა** (plural) is as common as the singular, because the
  classifieds portals that own these SERPs index plural listing pages.
- Georgian marks place with the locative suffix **-ში**: `თბილისში`,
  `ბათუმში`, `ქუთაისში`, `აეროპორტში`. A page that only carries the nominative
  `თბილისი` misses the actual query form.
- **`ჯიპი`** is the everyday word for a capable 4x4. A Georgian will search
  `ჯიპის ქირაობა` far sooner than `4x4 ქირაობა`. Georgian copy that only says
  "4x4" is written for an English speaker.
- `დღიურად` (per day), `თვიურად` / `თვეში` (monthly), `იაფად` (cheaply) attach
  directly to the head term rather than forming separate phrases.

### 1.2 Latin-script transliteration — what Georgians actually type

This is not a theoretical concern. The Georgian classifieds portals that
currently rank build keyword URLs directly from transliterated input, which is
observational proof of what users type into the box:

- `manqanebi.ge/ka/auto?keyword=manqanis-qiraoba-TBILISI-`
- `manqanebi.ge/ka/auto?keyword=manqanis-gaqiraveba-tbilisi-dgiurat`
- `manqanebi.ge/ka/auto?keyword=manqanebis-qiraoba-dgiurad-50-lari`
- `binebi.info/ka/search?keyword=Manqanis-qiraoba`

So the live transliterated set includes: `manqanis qiraoba`,
`manqanis qiraoba tbilisshi`, `manqanebis qiraoba`, `manqanis gaqiraveba`,
`manqanis gaqiraveba dgiurad`, `avtomobilis qiraoba`, `jipis qiraoba`,
`manqanis qiraoba fasebi`, `rent a kari`.

Note the orthographic instability: `dgiurad` / `dgiurat`, `tbilisshi` /
`tbilisi`, mixed case. This is typed on a Latin keyboard by a Georgian speaker
who has not switched layouts — commonly on mobile.

**What to do with it — and what not to do.**

- Do **not** create transliterated URLs. `/car-rental/manqanis-qiraoba/` would be
  a doorway page and duplicates `/ka/car-rental/`.
- Do put the transliterated forms in **body copy and FAQ answers** on the Georgian
  pages, where they read naturally — e.g. a line acknowledging "manqanis qiraoba"
  as the common spelling. Google matches these to the Georgian-script page
  reasonably well when both appear on it.
- The existing blog slugs already do the right thing:
  `/blog/rogor-viqiravot-manqana-saqartveloshi/`,
  `/blog/manqanis-daqiraveba-tu-taqsi/`,
  `/blog/avtomobilit-mogzauroba-saqartveloshi/`. Transliterated **slug**,
  Georgian-script **content**. Keep this pattern for any new Georgian-first page.

### 1.3 Russian (ru)

Russian is the highest-value non-English market for this site and has query
patterns with **no English equivalent at all**:

- **`без залога`** ("without deposit") is arguably the single most competitive
  modifier in the Russian rental SERP for Georgia. Multiple ranking pages lead
  with it in the title. RentUp **does not offer a deposit-free product**
  (`rental_policy.yml → deposit.waiver_available: false`), so this cluster must be
  answered honestly, not chased — see cluster **A16**.
- **`для россиян`** ("for Russians") and adjacent forms (`с российскими правами`,
  `оплата картой МИР`, `без банковской карты`) are a large, distinct
  post-2022 cluster driven by payment and documentation friction. The SERP for it
  is dominated by *editorial* pages on vc.ru, dtf.ru and in-trips.ru rather than
  by operators — meaning it is **winnable**, unlike the head terms.
- `аренда` and `прокат` are both used and are **not** interchangeable in search
  behaviour: `прокат` skews short-term/tourist, `аренда` skews longer-term. Both
  belong on the page.
- `авто` / `машины` / `автомобиля` all appear; `авто` is the highest-frequency
  form.
- `Военно-Грузинская дорога` is a Russian-only travel head term with real weight
  and no English counterpart of similar size.

---

# PART A — Intent A: renting a car in Georgia

## A1 — Head term: car rental in Georgia

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/` · `/ka/car-rental/` · `/ru/car-rental/` |
| **Status** | **covered** — full hub copy in `seo_car_rental.yml` in all 6 languages, 12 sections + 8 FAQs |
| **Difficulty** | **Very High** (en/ru), **High** (ka) — aggregators + 8 established operators |
| **Volume (est.)** | High in all three. *Reasoning: fully commercial SERP with paid ads and OTA aggregators; nobody buys ads against a query nobody searches.* |
| **Data behind it** | 17 × `content/cars/*.yml`, `categories.yml`, `rental_policy.yml`, `seo_car_rental.yml` |

**EN** — primary `car rental georgia`
`rent a car georgia` · `car hire georgia` · `car rental in georgia country` ·
`rent a car in georgia country` · `georgia car rental company` ·
`self drive georgia` · `hire a car georgia` · `car rental georgia prices` ·
`best car rental in georgia` · `rent a car georgia reviews`

*Note the disambiguation problem: "Georgia" collides with the US state. English
copy and titles must carry "Georgia (country)", "the Caucasus", "Tbilisi" and
"Kutaisi" as disambiguating tokens. The observed SERP already splits this way.*

**KA** — primary `მანქანის ქირაობა`
`მანქანების ქირაობა` · `მანქანის გაქირავება` · `ავტომობილის ქირაობა` ·
`ავტომობილის დაქირავება` · `რენტ ა კარი` · `ქირავდება მანქანა` ·
`მანქანის ქირაობა საქართველოში` · `მანქანის ქირაობის ფასები` ·
`მანქანების ქირაობა დღიურად`
Latin: `manqanis qiraoba` · `manqanebis qiraoba` · `avtomobilis qiraoba`

**RU** — primary `аренда авто в Грузии`
`прокат авто Грузия` · `аренда машины в Грузии` · `прокат машин в Грузии` ·
`арендовать авто в Грузии` · `взять машину напрокат в Грузии` ·
`аренда автомобиля Грузия` · `автопрокат Грузия` ·
`аренда авто в Грузии цены` · `аренда авто в Грузии отзывы`

---

## A2 — Tbilisi city pickup

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/tbilisi/` (+ `/ka/`, `/ru/`) |
| **Status** | **covered** — location block exists in `seo_car_rental.yml → locations.tbilisi` |
| **Difficulty** | **Very High** — this is the most contested rental query in the country |
| **Volume (est.)** | High (all three languages) |
| **Data behind it** | `places.yml:tbilisi`, office at 71 Vazha-Pshavela Ave, **free city delivery anywhere in Tbilisi** (`delivery.city_delivery_free_in: [tbilisi]`), routes starting near Tbilisi |

**EN** `car rental tbilisi` · `rent a car tbilisi` · `car hire tbilisi` ·
`tbilisi car rental cheap` · `rent a car tbilisi city centre` ·
`car rental tbilisi old town` · `car rental tbilisi delivery to hotel` ·
`tbilisi car rental automatic` · `rent car tbilisi georgia`

**KA** `მანქანის ქირაობა თბილისში` · `მანქანების ქირაობა თბილისში` ·
`მანქანის გაქირავება თბილისში` · `ავტომობილის ქირაობა თბილისში` ·
`მანქანის ქირაობა თბილისში დღიურად` · `იაფი მანქანის ქირაობა თბილისში` ·
`მანქანის ქირაობა ვაჟა-ფშაველაზე`
Latin: `manqanis qiraoba tbilisshi` · `manqanis gaqiraveba tbilisi dgiurad`

**RU** `аренда авто Тбилиси` · `прокат авто в Тбилиси` ·
`аренда машины в Тбилиси` · `аренда авто Тбилиси недорого` ·
`прокат машин Тбилиси центр` · `аренда авто Тбилиси с доставкой в отель` ·
`аренда авто Тбилиси на сутки`

**Differentiator available and unused by competitors:** free delivery anywhere in
the city is a hard fact in `rental_policy.yml`. Most competitors charge or
require office collection. This belongs in the title/meta, not buried in a
section.

---

## A3 — Tbilisi Airport (TBS)

| | |
|---|---|
| **Intent / stage** | transactional / BOFU — highest booking intent in the whole map |
| **Target URL** | `/car-rental/tbilisi-airport/` |
| **Status** | **covered** |
| **Difficulty** | **Very High** — OTA aggregators bid hardest here |
| **Volume (est.)** | High |
| **Data behind it** | `places.yml:tbilisi-airport` (41.6692, 44.9547), **airport delivery fee 30 ₾** (cheapest of the three airports), night surcharge 20 ₾ for 22:00–08:00 arrivals |

**EN** `tbilisi airport car rental` · `car rental tbilisi airport tbs` ·
`rent a car tbilisi airport` · `car hire tbilisi international airport` ·
`tbs airport car rental` · `car rental tbilisi airport arrivals` ·
`tbilisi airport car rental late night` · `pick up car tbilisi airport` ·
`car delivery tbilisi airport`

**KA** `მანქანის ქირაობა თბილისის აეროპორტში` ·
`ავტომობილის ქირაობა აეროპორტში` · `მანქანის ქირაობა აეროპორტთან` ·
`მანქანის მიწოდება აეროპორტში` · `თბილისის აეროპორტში მანქანის დაქირავება`

**RU** `аренда авто аэропорт Тбилиси` · `прокат авто в аэропорту Тбилиси` ·
`аренда машины аэропорт Тбилиси` · `аренда авто Тбилиси аэропорт ночью` ·
`забрать машину в аэропорту Тбилиси` · `доставка авто в аэропорт Тбилиси` ·
`аренда авто TBS`

**Winnable sub-angle:** late-night arrivals. A large share of TBS traffic lands
after 22:00. The site has an exact, publishable answer (20 ₾ night surcharge,
stated, no "call us"). Competitors mostly say nothing. Build this as an H2 with
the arrival-hour framing.

---

## A4 — Kutaisi city

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/kutaisi/` |
| **Status** | **covered** |
| **Difficulty** | **High** — thinner than Tbilisi, fewer dedicated pages |
| **Volume (est.)** | Medium (en/ru), Low–Medium (ka) |
| **Data behind it** | `places.yml:kutaisi`, city delivery fee 50 ₾ |

**EN** `car rental kutaisi` · `rent a car kutaisi` · `car hire kutaisi georgia` ·
`kutaisi car rental cheap` · `rent a car kutaisi city` ·
`car rental kutaisi to tbilisi` · `car rental imereti`

**KA** `მანქანის ქირაობა ქუთაისში` · `მანქანების ქირაობა ქუთაისში` ·
`ავტომობილის ქირაობა ქუთაისში` · `მანქანის გაქირავება ქუთაისი` ·
`მანქანის ქირაობა იმერეთში`

**RU** `аренда авто Кутаиси` · `прокат авто в Кутаиси` ·
`аренда машины Кутаиси` · `аренда авто Кутаиси недорого` ·
`прокат авто Имеретия`

---

## A5 — Kutaisi Airport (KUT)

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/kutaisi-airport/` |
| **Status** | **covered** |
| **Difficulty** | **High** |
| **Volume (est.)** | Medium–High. *Reasoning: KUT is the low-cost carrier gateway (Wizz Air); arrivals are price-sensitive and disproportionately likely to rent rather than transfer, and the airport is 20 km from the city with poor public transport.* |
| **Data behind it** | `places.yml:kutaisi-airport` (42.1767, 42.4826), airport delivery fee 60 ₾ |

**EN** `kutaisi airport car rental` · `car rental kutaisi airport kut` ·
`rent a car kutaisi airport` · `kut airport car hire` ·
`car rental kutaisi airport wizz air` · `cheap car rental kutaisi airport` ·
`kutaisi airport to batumi car rental` · `car rental kutaisi airport one way`

**KA** `მანქანის ქირაობა ქუთაისის აეროპორტში` ·
`ავტომობილის ქირაობა ქუთაისის აეროპორტში` ·
`მანქანის მიწოდება ქუთაისის აეროპორტში`

**RU** `аренда авто аэропорт Кутаиси` · `прокат авто в аэропорту Кутаиси` ·
`аренда машины Кутаиси аэропорт` · `аренда авто Кутаиси аэропорт Батуми` ·
`дешевая аренда авто аэропорт Кутаиси`

**Winnable sub-angle:** `kutaisi airport → batumi one way`. KUT is the natural
arrival for a Black Sea holiday, and the one-way fee is a published 100 ₾. This
is a real, low-competition, high-intent query — see cluster **A21**.

---

## A6 — Batumi city

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/batumi/` |
| **Status** | **covered** |
| **Difficulty** | **High** — a busy Russian-language SERP (dracarsrent.com and similar are Batumi-first) |
| **Volume (est.)** | High (ru), Medium (en), Low–Medium (ka) |
| **Data behind it** | `places.yml:batumi`, city delivery 50 ₾ |

**EN** `car rental batumi` · `rent a car batumi` · `car hire batumi georgia` ·
`batumi car rental cheap` · `rent a car batumi beach` ·
`car rental batumi to tbilisi` · `car rental adjara`

**KA** `მანქანის ქირაობა ბათუმში` · `მანქანების ქირაობა ბათუმში` ·
`ავტომობილის ქირაობა ბათუმში` · `მანქანის გაქირავება ბათუმი` ·
`მანქანის ქირაობა აჭარაში`
Latin: `manqanis qiraoba batumshi`

**RU** `аренда авто Батуми` · `прокат авто в Батуми` ·
`аренда машины Батуми` · `аренда авто Батуми без залога` ·
`прокат авто Батуми недорого` · `аренда авто Батуми на сутки` ·
`автопрокат Аджария`

---

## A7 — Batumi Airport (BUS)

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/batumi-airport/` |
| **Status** | **covered** |
| **Difficulty** | **Medium–High** — the thinnest of the six location SERPs |
| **Volume (est.)** | Medium |
| **Data behind it** | `places.yml:batumi-airport` (41.6102, 41.5997), delivery 60 ₾ |

**EN** `batumi airport car rental` · `car rental batumi airport bus` ·
`rent a car batumi airport` · `bus airport car hire georgia` ·
`car rental batumi airport arrivals` · `batumi airport to kobuleti car rental`

**KA** `მანქანის ქირაობა ბათუმის აეროპორტში` ·
`ავტომობილის ქირაობა ბათუმის აეროპორტში`

**RU** `аренда авто аэропорт Батуми` · `прокат авто в аэропорту Батуми` ·
`аренда машины Батуми аэропорт` · `аренда авто Батуми аэропорт с доставкой`

---

## A8 — Economy / cheap

| | |
|---|---|
| **Intent / stage** | transactional / BOFU with price qualification |
| **Target URL** | `/car-rental/economy/` |
| **Status** | **covered** — `seo_categories.yml → economy`, H1 "Economy Car Rental in Georgia", 4 FAQs |
| **Difficulty** | **Very High** — "cheap" is the most contested modifier and the classifieds portals (manqanebi.ge, servisebi.ge) own the Georgian side with price-in-title pages |
| **Volume (est.)** | High (all three) |
| **Data behind it** | 3 cars — Prius 75 ₾, Elantra 82 ₾, Corolla 88 ₾; 30-day rates 56/62/66 ₾; deposit 300 ₾ |

**EN** `cheap car rental georgia` · `economy car rental georgia` ·
`budget car hire georgia` · `cheapest car rental tbilisi` ·
`small car rental georgia` · `car rental georgia from 25 usd` ·
`affordable car rental tbilisi` · `low cost car rental georgia`

**KA** `იაფი მანქანის ქირაობა` · `მანქანის ქირაობა იაფად` ·
`ეკონომ კლასის მანქანის ქირაობა` · `მანქანის ქირაობა 50 ლარად` ·
`მანქანის ქირაობა დღიურად იაფად` · `ყველაზე იაფი მანქანის ქირაობა თბილისში`
Latin: `manqanebis qiraoba dgiurad 50 lari` (a live keyword URL on manqanebi.ge)

**RU** `дешевая аренда авто в Грузии` · `недорогой прокат авто Тбилиси` ·
`аренда авто эконом класса Грузия` · `аренда авто в Грузии от 25 долларов` ·
`бюджетная аренда машины Тбилиси` · `самая дешевая аренда авто в Тбилиси`

**Honesty constraint:** the Georgian classifieds SERP is full of "50 ₾/day"
titles. RentUp's floor is 75 ₾ (Prius) and 56 ₾ only at 30+ days. Do **not**
title against a price the fleet cannot deliver. Compete on
*what 75 ₾ includes* — unlimited mileage, TPL, no prepayment — which the 50 ₾
classifieds listings do not include and cannot match.

---

## A9 — SUV / crossover

| | |
|---|---|
| **Intent / stage** | transactional / MOFU→BOFU |
| **Target URL** | `/car-rental/suv/` |
| **Status** | **covered** — `seo_categories.yml → suv` |
| **Difficulty** | **High** |
| **Volume (est.)** | Medium–High |
| **Data behind it** | Tucson 130 ₾ (AWD, 181 mm), Outlander 138 ₾ (4WD, 190 mm, 7 seats), RAV4 145 ₾ (AWD hybrid, 195 mm); deposit 600 ₾ |

**EN** `suv rental georgia` · `crossover rental tbilisi` ·
`rent an suv in georgia` · `4wd car rental georgia` ·
`suv hire georgia mountains` · `best suv for georgia roads` ·
`rav4 rental georgia` · `awd car rental tbilisi` · `suv rental batumi`

**KA** `ჯიპის ქირაობა` · `კროსოვერის ქირაობა` · `ჯიპის ქირაობა თბილისში` ·
`მაღალი გამავლობის მანქანის ქირაობა` · `SUV ქირაობა საქართველოში` ·
`ოთხთვალას ქირაობა`

**RU** `аренда кроссовера в Грузии` · `аренда внедорожника Тбилиси` ·
`прокат SUV Грузия` · `аренда полноприводного авто Грузия` ·
`аренда джипа в Тбилиси` · `аренда RAV4 Грузия`

---

## A10 — 4x4 / off-road

| | |
|---|---|
| **Intent / stage** | transactional / BOFU, **highest margin in the fleet** |
| **Target URL** | `/car-rental/4x4/` |
| **Status** | **covered** — `seo_categories.yml → offroad`, and its FAQ already asks the right question ("Do I actually need a 4x4 for Georgia, or is it marketing?") |
| **Difficulty** | **Medium** — genuinely lighter than the head terms; fstarentcar.com and gsscarrental.com compete, most others do not |
| **Volume (est.)** | Medium |
| **Data behind it** | Pajero 240 ₾ (235 mm, 4WD), Delica 290 ₾ (210 mm), Prado 330 ₾ (220 mm, low range + diff lock); deposit 1,200 ₾; **23 attractions flagged `car_category: offroad`** and **17 flagged `road: 4x4_only`** |

**EN** `4x4 rental georgia` · `off road car rental georgia` ·
`jeep rental tbilisi` · `land cruiser rental georgia` ·
`prado rental georgia` · `4x4 hire for tusheti` · `4x4 rental for svaneti` ·
`rent 4x4 for ushguli` · `off road vehicle rental caucasus` ·
`4wd rental georgia mountains`

**KA** `ჯიპის ქირაობა თუშეთისთვის` · `მაღალი გამავლობის ჯიპის ქირაობა` ·
`4x4 მანქანის ქირაობა` · `პრადოს ქირაობა` · `ჯიპის ქირაობა სვანეთისთვის` ·
`ჯიპის ქირაობა ომალოსთვის`
Latin: `jipis qiraoba`

**RU** `аренда внедорожника в Грузии` · `аренда джипа Тбилиси` ·
`аренда 4x4 Грузия` · `аренда Прадо Грузия` ·
`аренда внедорожника для Тушетии` · `аренда джипа для Сванетии` ·
`аренда авто для Ушгули` · `внедорожник напрокат Грузия`

**This is the site's strongest commercial cluster.** It is where the intent-B
data (`road`, `car_category` on 257 attractions) converts directly to an
intent-A booking, and where the difficulty is lowest relative to value. See
build-list items #1 and #3.

---

## A11 — Minivan / 7–9 seater

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/minivan/` |
| **Status** | **covered** — `seo_categories.yml → minivan` |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium |
| **Data behind it** | Vito 200 ₾ (8 seats), Staria 260 ₾ (9 seats, AWD), Alphard 310 ₾ (7 seats, hybrid); deposit 1,000 ₾ |

**EN** `minivan rental georgia` · `7 seater car rental tbilisi` ·
`8 seater rental georgia` · `9 seater van rental georgia` ·
`family car rental georgia` · `van rental for group georgia` ·
`mercedes vito rental tbilisi` · `alphard rental georgia` ·
`minibus rental georgia with driver`

**KA** `მინივენის ქირაობა` · `7 ადგილიანი მანქანის ქირაობა` ·
`8 ადგილიანი მანქანის ქირაობა` · `მიკროავტობუსის ქირაობა` ·
`ვიტოს ქირაობა` · `საოჯახო მანქანის ქირაობა`

**RU** `аренда минивэна в Грузии` · `аренда 7 местного авто Тбилиси` ·
`аренда 8 местного минивэна Грузия` · `аренда микроавтобуса Тбилиси` ·
`аренда Vito Грузия` · `аренда Alphard Тбилиси` ·
`аренда авто для большой семьи Грузия`

---

## A12 — Business / executive class

| | |
|---|---|
| **Intent / stage** | transactional / BOFU, high ticket |
| **Target URL** | **NEW URL NEEDED → `/car-rental/business/`** |
| **Status** | **missing** — the category exists in `categories.yml` and 3 cars are assigned to it, but `seo_categories.yml` has **no `business` entry**, so no page is generated. `SEO_URL_MAP.md` lists it as "deferred until data exists" — **the data now exists.** |
| **Difficulty** | **Low–Medium** — very few Georgian operators build a business-class page |
| **Volume (est.)** | Low–Medium, but per-booking value is the highest in the fleet (210–310 ₾/day) |
| **Data behind it** | Camry 210 ₾ (hybrid), E-Class 290 ₾, BMW 5 310 ₾; deposit 1,000 ₾; `fleet.yml` line 231 already states these are "available with a driver if required" |

**EN** `business car rental tbilisi` · `executive car rental georgia` ·
`mercedes e class rental tbilisi` · `bmw rental georgia` ·
`luxury car rental tbilisi` · `premium car hire georgia` ·
`corporate car rental georgia` · `car rental for business trip tbilisi` ·
`airport transfer mercedes tbilisi`

**KA** `ბიზნეს კლასის მანქანის ქირაობა` · `მერსედესის ქირაობა თბილისში` ·
`BMW-ს ქირაობა` · `პრემიუმ კლასის ავტომობილის ქირაობა` ·
`კორპორატიული მანქანის ქირაობა` · `წარმომადგენლობითი მანქანის ქირაობა`

**RU** `аренда авто бизнес класса Тбилиси` · `аренда Мерседес Е класса Грузия` ·
`аренда BMW Тбилиси` · `премиум прокат авто Грузия` ·
`аренда представительского авто Тбилиси` ·
`корпоративная аренда авто Грузия`

---

## A13 — Commercial van / cargo

| | |
|---|---|
| **Intent / stage** | transactional / BOFU, B2B and domestic |
| **Target URL** | **NEW URL NEEDED → `/car-rental/van/`** |
| **Status** | **missing** — same situation as A12: category and 2 cars exist, no `seo_categories.yml` entry |
| **Difficulty** | **Low** |
| **Volume (est.)** | Low (en/ru), Low–Medium (ka — this is a domestic/business query, not a tourist one) |
| **Data behind it** | Ford Transit 185 ₾ (manual, 3 seats), Sprinter 215 ₾ (manual, 3 seats); deposit 800 ₾. **Both are manual — the only two manuals in the fleet.** |

**EN** `van rental georgia` · `cargo van rental tbilisi` ·
`sprinter rental georgia` · `transit van hire tbilisi` ·
`moving van rental tbilisi` · `commercial vehicle rental georgia`

**KA** `ფურგონის ქირაობა` · `სატვირთო მანქანის ქირაობა თბილისში` ·
`სპრინტერის ქირაობა` · `ტრანზიტის ქირაობა` ·
`გადაზიდვისთვის მანქანის ქირაობა` · `ბორტიანი მანქანის ქირაობა`

**RU** `аренда фургона в Тбилиси` · `аренда Спринтера Грузия` ·
`аренда грузового авто Тбилиси` · `аренда микроавтобуса для переезда Тбилиси`

**Priority note:** genuinely low. Listed for completeness and because the page is
cheap to build from data that already exists, not because it will move revenue.

---

## A14 — Automatic transmission

| | |
|---|---|
| **Intent / stage** | transactional qualifier / BOFU |
| **Target URL** | **NEW URL NEEDED → `/car-rental/automatic/`** (low priority) — or fold into `/car-rental/` + `/fleet/` |
| **Status** | **thin** — no page states the fleet-wide fact |
| **Difficulty** | **Low–Medium** |
| **Volume (est.)** | Medium in ru (`на автомате` is a standard Russian qualifier), Low–Medium in en, Low in ka |
| **Data behind it** | **15 of 17 cars are automatic.** Only Transit and Sprinter are manual. That is a clean, checkable, category-wide claim. |

**EN** `automatic car rental georgia` · `automatic car hire tbilisi` ·
`rent automatic car georgia` · `automatic transmission rental tbilisi airport` ·
`no manual car rental georgia`

**KA** `ავტომატიკიანი მანქანის ქირაობა` ·
`ავტომატური გადაცემათა კოლოფის მანქანის ქირაობა` · `ავტომატზე მანქანის ქირაობა`

**RU** `аренда авто на автомате в Грузии` · `прокат авто автомат Тбилиси` ·
`аренда машины с автоматической коробкой Грузия` ·
`аренда авто автомат Батуми`

**Recommendation — resist the page at first.** A `/car-rental/automatic/` page
listing 15 of 17 cars is 88% duplicate of `/fleet/`. Better first move: state
"15 of our 17 cars are automatic" prominently on `/car-rental/` and on each
category page, and add a transmission line to every `/fleet/{car}/` page. Only
build the standalone URL if Search Console later shows the query pulling
impressions that the hub is not capturing.

---

## A15 — Unlimited mileage

| | |
|---|---|
| **Intent / stage** | policy / MOFU — a filter query, not a browse query |
| **Target URL** | `/car-rental/` (§mileage anchor) — **no separate URL** |
| **Status** | **covered** — `rental_policy.yml → mileage.unlimited: true`, hub section + FAQ "Is the mileage really unlimited?" |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium (en/ru), Low (ka — Georgians renting domestically rarely think in mileage caps) |
| **Data behind it** | `mileage.unlimited: true`, unqualified, all categories |

**EN** `car rental georgia unlimited mileage` ·
`unlimited km car hire georgia` · `car rental georgia no mileage limit` ·
`is mileage unlimited car rental georgia` · `car rental georgia km limit`

**KA** `შეუზღუდავი გარბენით მანქანის ქირაობა` ·
`მანქანის ქირაობა კილომეტრაჟის შეზღუდვის გარეშე` · `გარბენის ლიმიტი`

**RU** `аренда авто без ограничения пробега Грузия` ·
`прокат авто безлимитный пробег Тбилиси` ·
`есть ли ограничение по километражу аренда авто Грузия` ·
`лимит км аренда авто Грузия`

**Note — this cluster was previously "held back" in `SEO_KEYWORD_MAP.md §Cluster 1`
for lack of source data. `rental_policy.yml` now supplies it. The hold can be
released.** But see §5.3: `llms.txt` currently contradicts it with a "300 km/day
limit on cross-border trips" claim.

---

## A16 — Deposit, and the "no deposit" problem

| | |
|---|---|
| **Intent / stage** | policy / MOFU — **very high commercial pull, especially in Russian** |
| **Target URL** | **NEW URL NEEDED → `/car-rental/deposit/`** (an honest explainer), plus the existing `/car-rental/` §deposit anchor |
| **Status** | **thin** — the hub explains the deposit well, but nothing addresses the *query as asked* |
| **Difficulty** | **High** in ru (a saturated, aggressively-titled SERP), **Medium** in en, **Low–Medium** in ka |
| **Volume (est.)** | **High** in ru. *Reasoning: multiple ranking pages put `без залога` in the title tag — operators only do that for queries that convert.* Medium en, Low–Medium ka. |
| **Data behind it** | deposits 300 ₾ (economy) → 1,200 ₾ (4x4); `method: card_hold`, `cash_accepted: true`, `released_days: 3`, **`waiver_available: false`** |

**EN** `car rental georgia no deposit` · `car hire georgia without deposit` ·
`car rental tbilisi no credit card` · `car rental georgia deposit amount` ·
`how much deposit car rental georgia` · `car rental georgia cash deposit` ·
`when is deposit refunded car rental georgia` ·
`car rental georgia no credit card required`

**KA** `მანქანის ქირაობა დეპოზიტის გარეშე` · `უდეპოზიტოდ მანქანის ქირაობა` ·
`რამდენია დეპოზიტი მანქანის ქირაობისას` · `დეპოზიტის დაბრუნება` ·
`მანქანის ქირაობა ბარათის გარეშე`

**RU** `аренда авто без залога Грузия` · `прокат авто без депозита Тбилиси` ·
`аренда авто в Грузии без залога и франшизы` ·
`аренда авто без банковской карты Грузия` ·
`какой залог при аренде авто в Грузии` ·
`аренда авто залог наличными Тбилиси` ·
`когда возвращают залог аренда авто Грузия` ·
`аренда авто Батуми без залога`

**Strategy — do not chase the term dishonestly.** `waiver_available: false` is
explicit and `seo_car_rental.yml` already says in plain words: *"There is no
deposit-free option; every rental requires one."* Keep that. The winnable page
is the **honest counter-page**: what the hold actually is, that **cash is
accepted** so no card limit is blocked (a genuine differentiator against
operators that require a credit card), the exact 300–1,200 ₾ range by category,
and the 3-working-day release. That page can legitimately rank for
"без залога" as the answer to the question rather than as a false claim, and it
will not create the refund disputes that a false claim would.

---

## A17 — Insurance, excess and CDW

| | |
|---|---|
| **Intent / stage** | policy / MOFU |
| **Target URL** | `/car-rental/deposit/` (shared with A16) or `/car-rental/insurance/` — **NEW URL NEEDED**; currently `/car-rental/` §insurance + `/terms/` |
| **Status** | **thin** |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium |
| **Data behind it** | `insurance.included: tpl`, `cdw_available: true`, `cdw_daily_gel: 25`, `excess_gel: 1000`; the file explicitly notes *"Deliberately NOT claimed: full coverage, zero excess"* |

**EN** `car rental georgia insurance` · `cdw car rental georgia` ·
`car rental georgia full insurance` · `car rental excess georgia` ·
`is insurance included car rental georgia` ·
`super cdw georgia car rental` · `car rental georgia franchise`

**KA** `მანქანის ქირაობა დაზღვევით` · `სრული დაზღვევა მანქანის ქირაობისას` ·
`ფრანშიზა მანქანის ქირაობა` · `რას ფარავს დაზღვევა`

**RU** `аренда авто в Грузии страховка` · `КАСКО аренда авто Грузия` ·
`аренда авто без франшизы Грузия` · `франшиза при аренде авто Тбилиси` ·
`полная страховка аренда авто Грузия` · `что покрывает страховка аренда авто`

**Conflict warning — see §5.3.** `rental_policy.yml` says TPL included, CDW is a
25 ₾/day *add-on*, excess 1,000 ₾, no zero-excess product. `faq.yml` says
*"the rate ... includes VAT, CDW insurance"* and `llms.txt` advertises an
*"SCDW zero-excess option for 25–45 GEL/day"*. These cannot all be true. **This
cluster is BLOCKED until one answer is chosen** — publishing an insurance page
across three languages on top of contradictory source data is the fastest route
to a refund dispute and a trust penalty.

---

## A18 — Age, licence, documents, IDP

| | |
|---|---|
| **Intent / stage** | qualifying / MOFU — a pre-booking blocker question |
| **Target URL** | **NEW URL NEEDED → `/car-rental/requirements/`**; currently split across `/car-rental/` §requirements, `/faq/`, `/terms/` |
| **Status** | **thin** (well answered, but spread across three URLs with different numbers — see §5.3) |
| **Difficulty** | **Medium** — mostly blog/editorial competition (wander-lush.org), not operators |
| **Volume (est.)** | Medium–High. *Reasoning: this is the question every first-time renter asks, and it is answered on nearly every travel blog covering Georgia, which is itself the signal.* |
| **Data behind it** | `min_driver_age: 21`, `min_licence_years: 2`, `licence_accepted: [national, idp]`, `passport_required: true`, no young-driver surcharge |

**EN** `car rental georgia age limit` · `minimum age to rent a car in georgia` ·
`do i need an idp in georgia` · `international driving permit georgia rental` ·
`documents to rent a car in georgia` · `can i rent a car in georgia at 21` ·
`rent a car georgia with foreign licence` ·
`us licence car rental georgia` · `young driver surcharge georgia`

**KA** `მართვის მოწმობა მანქანის ქირაობისთვის` ·
`რამდენი წლიდან შეიძლება მანქანის ქირაობა` ·
`მანქანის ქირაობისთვის საჭირო დოკუმენტები` ·
`საერთაშორისო მართვის მოწმობა საქართველოში`

**RU** `со скольки лет можно арендовать авто в Грузии` ·
`какие документы нужны для аренды авто в Грузии` ·
`нужны ли международные права в Грузии` ·
`аренда авто в Грузии с российскими правами` ·
`аренда авто для россиян Грузия` · `водительский стаж аренда авто Грузия` ·
`аренда авто в Грузии по национальным правам`

**The Russian sub-cluster is the opportunity here.** `аренда авто для россиян`
and its variants are currently answered by *editorial* sites (vc.ru, dtf.ru,
in-trips.ru), not by operators. An operator page that answers the documentation
and payment questions concretely — which licences are accepted without an IDP,
what happens with a card that will not authorise — is a genuinely winnable
position with direct booking intent behind it.

---

## A19 — Cross-border (Armenia, Turkey, Azerbaijan)

| | |
|---|---|
| **Intent / stage** | policy / MOFU |
| **Target URL** | `/car-rental/requirements/` §cross-border, or `/terms/` — **no dedicated URL recommended** |
| **Status** | **BLOCKED** |
| **Difficulty** | **Low–Medium** |
| **Volume (est.)** | Medium (en/ru) — a real query for the Tbilisi→Yerevan and Batumi→Trabzon corridors |
| **Data behind it** | **contradictory. Do not publish.** |

**EN** `can i take a rental car from georgia to armenia` ·
`rental car georgia to turkey` · `cross border car rental georgia` ·
`georgia armenia car rental one way` · `drive rental car georgia to azerbaijan`

**KA** `ქირავნობით აღებული მანქანით საზღვრის გადაკვეთა` ·
`სომხეთში გასვლა ქირავნობის მანქანით` · `თურქეთში გასვლა ნაქირავები მანქანით`

**RU** `можно ли выехать из Грузии на арендованной машине` ·
`аренда авто Грузия выезд в Армению` · `арендованная машина Грузия Турция` ·
`пересечение границы на арендованном авто Грузия` ·
`аренда авто Грузия Азербайджан`

**Why blocked:** `rental_policy.yml → cross_border.allowed: false` ("vehicles
stay in Georgia") and `seo_car_rental.yml` says "cross-border travel isn't
available on any rental". But `llms.txt` publicly states *"Armenia (150 GEL) and
Turkey (250 GEL) allowed with permit; Azerbaijan and Russia prohibited"*, with a
300 km/day cap. One of these is already live and wrong. Resolve before writing a
word of cluster copy — and note that `llms.txt` is machine-read by AI assistants,
so the wrong version is currently the one being quoted to users.

---

## A20 — Long-term and monthly rental

| | |
|---|---|
| **Intent / stage** | transactional / BOFU — **highest lifetime value per booking** |
| **Target URL** | **NEW URL NEEDED → `/car-rental/monthly/`** |
| **Status** | **missing** — 30-day pricing exists on every car but no page targets the intent; `/pricing/` is `noindex` |
| **Difficulty** | **Low–Medium** — thin SERP; the aggregators are built around short rentals and do not compete well here |
| **Volume (est.)** | Medium and structurally growing. *Reasoning: Georgia's remote-worker/relocation population rents by the month; the Russian-language SERP for `аренда авто на месяц` is noticeably less commercial than the daily-rental SERP.* |
| **Data behind it** | `price_30` on **all 17 cars** (56–248 ₾/day), `price_7_29` tier, `max_rental_days: 90`, FAQ tiers (−10% from 7 days, −25% from 30, up to −40% corporate 3 months+) |

**EN** `monthly car rental georgia` · `long term car rental tbilisi` ·
`rent a car for a month in georgia` · `car subscription georgia` ·
`car rental georgia 30 days` · `cheap monthly car hire tbilisi` ·
`long term car hire georgia expat` · `car rental georgia for digital nomads` ·
`corporate car rental georgia`

**KA** `მანქანის ქირაობა თვიურად` · `გრძელვადიანი მანქანის ქირაობა` ·
`მანქანის ქირაობა თვეში` · `მანქანის ქირაობა ერთი თვით` ·
`კორპორატიული მანქანის ქირაობა` · `მანქანის ქირაობა 30 დღით`

**RU** `аренда авто на месяц в Грузии` · `долгосрочная аренда авто Тбилиси` ·
`аренда авто на длительный срок Грузия` · `аренда машины на месяц Батуми` ·
`аренда авто для релокантов Грузия` · `подписка на авто Грузия` ·
`аренда авто на 30 дней Тбилиси`

**This is the single best unbuilt commercial page on the site:** the data is
complete for all 17 vehicles, the intent is unambiguous, the SERP is soft, and
the booking value is 20–30× a one-day rental.

---

## A21 — One-way rental

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | **NEW URL NEEDED → `/car-rental/one-way/`** |
| **Status** | **thin** — hub §one_way covers the policy; nothing targets the query or the specific city pairs |
| **Difficulty** | **Low–Medium** |
| **Volume (est.)** | Medium. *Reasoning: fly-into-Kutaisi / fly-out-of-Tbilisi is a common Georgia itinerary shape; the query has almost no purpose-built competition.* |
| **Data behind it** | `one_way.available: true`, `fee_gel: 100`, 6 served pickup points = up to 30 ordered city pairs (present them as a small matrix on one page, **not** as 30 URLs) |

**EN** `one way car rental georgia` · `car rental kutaisi airport drop off tbilisi` ·
`pick up tbilisi drop off batumi car rental` ·
`one way car hire tbilisi to batumi` · `car rental georgia different drop off` ·
`one way rental fee georgia` · `car rental batumi return tbilisi`

**KA** `ცალმხრივი მანქანის ქირაობა` ·
`მანქანის ქირაობა თბილისში აღება ბათუმში დაბრუნება` ·
`სხვა ქალაქში დაბრუნება მანქანის ქირაობისას`

**RU** `аренда авто в один конец Грузия` ·
`взять авто в Тбилиси сдать в Батуми` ·
`аренда авто Кутаиси аэропорт сдать в Тбилиси` ·
`прокат авто с возвратом в другом городе Грузия` ·
`доплата за возврат в другом городе Грузия`

**Cannibalisation guard:** the airport pages (A3/A5/A7) each mention one-way.
The dedicated page must be the *matrix and the fee*; the airport pages must link
to it rather than restate it, or the four pages will compete.

---

## A22 — Airport delivery, hotel delivery, late-night pickup

| | |
|---|---|
| **Intent / stage** | transactional qualifier / BOFU |
| **Target URL** | the three airport pages + `/car-rental/tbilisi/` — **no new URL** |
| **Status** | **covered** (data), **thin** (framing — the fees are stated but not targeted at the query) |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Low–Medium individually, Medium in aggregate |
| **Data behind it** | free city delivery in Tbilisi; airport fees 30/60/60 ₾; night surcharge 20 ₾ (22:00–08:00) with exact window |

**EN** `car rental delivery to hotel tbilisi` ·
`car delivered to airport georgia` · `meet and greet car rental tbilisi` ·
`car rental georgia night pickup` · `late arrival car rental tbilisi airport` ·
`car rental georgia free delivery`

**KA** `მანქანის მიწოდება სასტუმროში` · `მანქანის მიწოდება აეროპორტში` ·
`მანქანის მიტანა მისამართზე` · `ღამის საათებში მანქანის მიღება`

**RU** `доставка авто в отель Тбилиси` ·
`доставка арендованного авто в аэропорт Грузия` ·
`подача авто по адресу Тбилиси` · `аренда авто ночной прилет Тбилиси` ·
`бесплатная доставка авто Тбилиси`

---

## A23 — Rental with driver / chauffeur

| | |
|---|---|
| **Intent / stage** | transactional / BOFU — a *different customer*, not a rental variant |
| **Target URL** | **NEW URL NEEDED → `/car-rental/with-driver/`** |
| **Status** | **missing as a page** — the service exists and is priced, but only inside a `/faq/` answer |
| **Difficulty** | **Medium** — competes with tour operators and transfer companies, not rental firms |
| **Volume (est.)** | Medium (ru/en). *Reasoning: a large share of visitors who will not drive Georgian mountain roads themselves still want a car; the transfer/tour SERP is crowded but the "rental with driver" framing is not.* |
| **Data behind it** | `faq.yml`: **chauffeur service 120 ₾/day (8 h), overtime 20 ₾/h**; `fleet.yml` line 231: business cars "available with a driver if required"; 32 routes with `drive_time_total` to scope a day |

**EN** `car rental with driver georgia` · `hire a car and driver tbilisi` ·
`chauffeur service tbilisi` · `private driver georgia day trip` ·
`car with driver kazbegi from tbilisi` · `english speaking driver georgia` ·
`minivan with driver tbilisi` · `car and driver hire batumi`

**KA** `მანქანის ქირაობა მძღოლით` · `მძღოლიანი მანქანის დაქირავება` ·
`პირადი მძღოლის დაქირავება` · `ტრანსფერი მძღოლით`

**RU** `аренда авто с водителем в Грузии` · `машина с водителем Тбилиси` ·
`личный водитель Грузия` · `трансфер с водителем Тбилиси Казбеги` ·
`русскоговорящий водитель Грузия` · `минивэн с водителем Тбилиси` ·
`нанять водителя с машиной Батуми`

**Natural cross-sell:** every intent-B page that flags a route as
`car_category: offroad` or `difficulty: hard` should link here. A visitor who has
just read that the Abano Pass is 4x4-only gravel at 2,850 m is the exact person
who converts on "with driver".

---

## A24 — Winter tyres, winter conditions, ski season

| | |
|---|---|
| **Intent / stage** | seasonal qualifier / MOFU→BOFU (Dec–Mar) |
| **Target URL** | `/blog/zamtris-mgzavroba-saqartveloshi/` (exists) — **recommend promoting to `/guides/winter-driving-georgia/`** |
| **Status** | **thin** — one blog post in 6 languages, no link from the car-rental cluster, not positioned for the rental query |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium, sharply seasonal (Nov–Mar) |
| **Data behind it** | winter tyres Dec–Apr stated on car pages (e.g. Prado); Gudauri and Hatsvali-Tetnuldi are the **2 attractions flagged `best_season: december-march`**; 48 attractions are `open_year_round: false`; `military-highway-kazbegi` route is `best_season: all` |

**EN** `winter tyres car rental georgia` · `driving in georgia in winter` ·
`car rental gudauri ski` · `4x4 rental for gudauri` ·
`snow chains georgia rental car` · `is the military highway open in winter` ·
`car rental bakuriani winter` · `driving to gudauri from tbilisi airport`

**KA** `ზამთრის საბურავები` · `ზამთარში მანქანით მგზავრობა` ·
`გუდაურში მანქანით ასვლა` · `ჯვრის უღელტეხილი დაკეტილია` ·
`ჯაჭვები საბურავებზე` · `მანქანის ქირაობა გუდაურისთვის`

**RU** `зимняя резина аренда авто Грузия` · `Грузия зимой на машине` ·
`аренда авто Гудаури зимой` · `Военно-Грузинская дорога зимой закрыта` ·
`цепи на колеса Грузия` · `аренда внедорожника Гудаури` ·
`доехать до Гудаури из аэропорта Тбилиси зимой`

**The Russian "Военно-Грузинская дорога зимой" angle is the highest-value piece
here** and bridges directly into intent B (cluster B11).

---

## A25 — Rent vs taxi vs tour vs transfer (comparison)

| | |
|---|---|
| **Intent / stage** | comparison / MOFU — the decision *before* the rental decision |
| **Target URL** | `/blog/manqanis-daqiraveba-tu-taqsi/` (exists, Tbilisi-specific) |
| **Status** | **covered for Tbilisi taxi**, **missing for tour/transfer/marshrutka comparisons** |
| **Difficulty** | **Low–Medium** — blog SERP, no operator competition |
| **Volume (est.)** | Low–Medium |
| **Data behind it** | existing post with real numbers; `site.yml` fuel figures (`fuel_l_100km: 8.5`, `fuel_price_gel: 3.1`) and per-car `fuel_100km` make a *cost-per-route* comparison computable for all 32 routes |

**EN** `is it worth renting a car in georgia` · `rent a car or taxi in tbilisi` ·
`car rental vs tour georgia` · `bolt vs car rental tbilisi` ·
`marshrutka or rental car georgia` · `cost of driving in georgia` ·
`do you need a car in georgia`

**KA** `მანქანის ქირაობა თუ ტაქსი` · `ღირს თუ არა მანქანის ქირაობა` ·
`ტაქსი თუ საკუთარი მანქანა` · `რა ჯობია ტური თუ მანქანა`

**RU** `стоит ли брать машину в аренду в Грузии` ·
`аренда авто или такси в Тбилиси` · `Bolt или аренда авто Тбилиси` ·
`нужна ли машина в Грузии` · `аренда авто или экскурсии Грузия` ·
`маршрутка или аренда авто Грузия`

**High-leverage extension:** compute fuel cost per route from `distance_km` ×
`fuel_100km` × 3.1 ₾/l, and put a "rental + fuel vs. organised tour" figure on
each of the 32 route pages. No competitor can do that, because no competitor has
both the fleet consumption figures and the route distances in one dataset.

---

## A26 — Price and tariff queries

| | |
|---|---|
| **Intent / stage** | transactional / BOFU |
| **Target URL** | `/car-rental/` + the category pages — **`/pricing/` is `noindex` and must stay so** |
| **Status** | **thin** — prices are on the pages but the *query* ("how much does it cost per day") is not targeted |
| **Difficulty** | **High** |
| **Volume (est.)** | High (ka especially — Georgian search is strongly price-led, with prices in the ranking page titles) |
| **Data behind it** | `price_1_6` / `price_7_29` / `price_30` on all 17 cars; `usd_rate: 2.6` for USD display |

**EN** `car rental georgia price per day` · `how much is car rental in georgia` ·
`car rental georgia cost` · `tbilisi car rental daily rate` ·
`car rental georgia price list` · `car rental georgia 2026 prices`

**KA** `მანქანის ქირაობის ფასები` · `მანქანის ქირაობა რა ღირს` ·
`მანქანის ქირაობა დღეში რამდენი ღირს` · `მანქანის ქირაობის ტარიფები` ·
`მანქანის ქირაობა 50 ლარი` · `მანქანის ქირაობა 100 ლარი`
Latin: `manqanis qiraoba fasebi`

**RU** `аренда авто в Грузии цены` · `сколько стоит аренда авто в Грузии` ·
`прокат авто Тбилиси цена за сутки` · `аренда авто Грузия прайс` ·
`аренда авто в Грузии 2026 цены`

**Note on the Georgian SERP shape:** the classifieds portals rank with the price
*in the URL and title* (`manqanebis-qiraoba-dgiurad-50-lari`). Matching that
pattern with a false price is not an option — see A8. Match it with a real one:
"from 75 ₾/day, 56 ₾/day at 30 days" is a specific, defensible title.

---

# PART B — Intent B: planning a Georgia trip by car

The asset that makes this half of the site defensible: **all 257 attractions
carry `road`, `car_category`, `best_season`, `open_year_round`, `elevation`,
`distance_tbilisi_km` and `drive_time_tbilisi`.** No travel blog and no rental
competitor has that combination as structured data. Every high-priority cluster
in Part B is built on it.

Distribution, for sizing the pages:

| Field | Values |
|---|---|
| `road` | paved 149 · mostly_paved 71 · gravel 20 · **4x4_only 17** |
| `car_category` | economy 175 · suv 59 · **offroad 23** |
| `best_season` | all 153 · may-october 67 · june-september 34 · april-october 1 · **december-march 2** |
| `open_year_round` | true 209 · **false 48** |

---

## B1 — Trip planner (tool intent)

| | |
|---|---|
| **Intent / stage** | tool / MOFU |
| **Target URL** | `/trip-planner/` (canonical for the query) · `/map/` (the app) · `/planner/` |
| **Status** | **covered** — page exists, copy in `seo_trip_planner.yml` in 6 languages |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium (en), Low–Medium (ru), Low (ka) |
| **Data behind it** | the planner product itself + 32 routes + 257 attractions |

**EN** `georgia trip planner` · `georgia road trip planner` ·
`plan a trip to georgia` · `georgia itinerary planner` ·
`self drive georgia planner` · `georgia travel route planner` ·
`build a georgia itinerary` · `georgia road trip map`

**KA** `მოგზაურობის დაგეგმვა` · `მარშრუტის დაგეგმვა საქართველოში` ·
`მარშრუტის შედგენა` · `სად წავიდეთ საქართველოში`

**RU** `планировщик маршрута по Грузии` · `составить маршрут по Грузии` ·
`маршрут по Грузии на машине планировщик` ·
`спланировать поездку в Грузию` · `карта маршрутов Грузия`

**See §5.1 — `/trip-planner/` vs `/map/` vs `/planner/` is the site's most urgent
three-way cannibalisation.**

---

## B2 — Itinerary duration bands

| | |
|---|---|
| **Intent / stage** | informational → tool / TOFU–MOFU |
| **Target URL** | `/itineraries/` + `/itineraries/georgia-{3,5,7,10,14}-days/` |
| **Status** | **covered** — all five bands built, each with a real day-by-day `plan` array (from/to/km/drive/stops/overnight/**road**) |
| **Difficulty** | **Medium–High** — established travel blogs and TourRadar own these SERPs |
| **Volume (est.)** | **High for 7 and 10 days**, Medium for 5 and 14, Medium for 3. *Reasoning: "7 days" and "10 days" match the standard European holiday length and pull the most dedicated blog pages.* |
| **Data behind it** | e.g. `georgia-7-days.yml`: 1,020 km, 18:30 drive, `car_category: economy`, 3 composed routes, per-day road surface. **The per-day `road` and `car_category` fields are the differentiator** — competing itineraries do not tell you what car you need. |

**EN** `georgia itinerary 7 days` · `georgia 10 day itinerary` ·
`georgia road trip itinerary 5 days` · `3 days in georgia itinerary` ·
`2 weeks in georgia itinerary` · `georgia self drive itinerary 7 days` ·
`one week in georgia by car` · `georgia itinerary from tbilisi` ·
`best georgia road trip route`

**KA** `საქართველოს მარშრუტი 7 დღე` · `7 დღიანი მარშრუტი მანქანით` ·
`კვირიანი მოგზაურობა საქართველოში` ·
`სამდღიანი მარშრუტი თბილისიდან` · `10 დღიანი მოგზაურობა საქართველოში`

**RU** `маршрут по Грузии на 7 дней на машине` ·
`маршрут по Грузии на 10 дней` · `Грузия за 5 дней на авто` ·
`Грузия на машине самостоятельно маршрут` ·
`две недели в Грузии на машине` · `маршрут по Грузии на 3 дня из Тбилиси` ·
`автопутешествие по Грузии маршрут`

**Angle that wins against the blogs:** every competing "7 days in Georgia" post
is written by someone who took a tour or a driver. Ours is the only one that can
say, per day, *this leg is paved / mostly paved / gravel, and here is the car
class it needs*. Lead with that in the H1 and meta, not with "the perfect week".

---

## B3 — Kazbegi / Stepantsminda / Military Highway

| | |
|---|---|
| **Intent / stage** | destination / TOFU–MOFU |
| **Target URL** | `/routes/military-highway-kazbegi/` (2 days) · `/routes/kazbegi-hiking-base/` (4 days) · `/regions/mtskheta-mtianeti/` |
| **Status** | **covered but cannibalised** — two routes plus a region hub compete; the region is named `mtskheta-mtianeti` while everyone searches "Kazbegi" |
| **Difficulty** | **Medium** |
| **Volume (est.)** | **High** — the single most-searched Georgian destination after Tbilisi and Batumi, in all three languages |
| **Data behind it** | `military-highway-kazbegi` (340 km, 6:40, `best_season: all`, `car_category: suv`); attractions Gergeti Trinity, Ananuri, Jvari Pass, Dariali Gorge, Truso Valley (gravel), Juta-Chaukhi (4x4_only), Gudauri |

**EN** `tbilisi to kazbegi road trip` · `kazbegi day trip from tbilisi` ·
`how to get to kazbegi by car` · `gergeti trinity church drive` ·
`military highway georgia drive` · `kazbegi self drive` ·
`do i need 4x4 for kazbegi` · `tbilisi to stepantsminda driving time` ·
`ananuri to kazbegi road`

**KA** `ყაზბეგი მანქანით` · `თბილისი ყაზბეგი მანძილი` ·
`სტეფანწმინდაში მანქანით` · `გერგეტის სამება მანქანით` ·
`ჯვრის უღელტეხილი` · `ერთდღიანი მოგზაურობა ყაზბეგში`

**RU** `Казбеги на машине из Тбилиси` · `Военно-Грузинская дорога маршрут` ·
`как добраться до Казбеги на авто` · `Гергети на машине` ·
`Тбилиси Казбеги расстояние` · `нужен ли внедорожник для Казбеги` ·
`Степанцминда самостоятельно на машине`

**Key answerable question, currently unanswered anywhere on the site:** *the
main Kazbegi road is paved — an economy car is enough to Stepantsminda; the 4x4
is needed only for Juta/Chaukhi and Truso.* The data says exactly this
(`gergeti-trinity-church` vs `juta-chaukhi: 4x4_only`, `truso-valley: gravel`).
Saying it plainly builds trust *and* upsells correctly, because it tells the
minority who need the 4x4 precisely why.

---

## B4 — Svaneti / Mestia / Ushguli

| | |
|---|---|
| **Intent / stage** | destination / TOFU–MOFU, **strong 4x4 pull-through** |
| **Target URL** | `/routes/svaneti-expedition/` (5 d) · `/routes/svaneti-alpine-circuit/` (6 d) · `/routes/svaneti-village-trek/` (6 d) · `/regions/samegrelo-zemo-svaneti/` |
| **Status** | **covered but heavily cannibalised** — three near-identical route pages |
| **Difficulty** | **Medium** — SERP is Tripadvisor threads, komoot and small tour operators |
| **Volume (est.)** | Medium–High |
| **Data behind it** | `svaneti-expedition` (1,050 km, 21:00 drive, `car_category: offroad`, `best_season: june-september`); Ushguli `road: gravel`, Adishi / Koruldi / Shkhara `4x4_only`, Becho-Mazeri `gravel`, Enguri Dam, Chalaadi Glacier |

**EN** `mestia to ushguli road` · `is the road to ushguli paved` ·
`do i need 4x4 for ushguli` · `driving to svaneti from tbilisi` ·
`zugdidi to mestia road condition` · `svaneti road trip` ·
`ushguli self drive` · `enguri dam to mestia drive time` ·
`best time to drive to svaneti`

**KA** `უშგულის გზა` · `მესტიიდან უშგულამდე გზა` ·
`სვანეთი მანქანით` · `ზუგდიდი მესტია გზა` ·
`სვანეთში ჯიპით` · `როდის არის სვანეთში წასვლა უკეთესი`

**RU** `дорога Местия Ушгули` · `дорога в Сванетию на машине` ·
`нужен ли внедорожник в Ушгули` · `Зугдиди Местия дорога состояние` ·
`Сванетия на машине самостоятельно` · `Ушгули как добраться на авто` ·
`Ингури ГЭС Местия дорога`

**"Is the road to Ushguli paved?" is a live, high-frequency, unresolved question**
— the observed SERP is Tripadvisor forum threads and a wanderlog place page. The
site holds a definite answer (`ushguli: road: gravel`, `car_category: offroad`,
`best_season: june-september`). This is the cleanest achievable win in Part B.

---

## B5 — Kakheti wine route

| | |
|---|---|
| **Intent / stage** | destination / TOFU–MOFU |
| **Target URL** | `/routes/kakheti-wine-loop/` (3 d) · `/routes/kakheti-table-and-cellar/` (3 d) · `/routes/kakheti-cycle-and-wine/` (5 d) · `/regions/kakheti/` |
| **Status** | **covered but cannibalised** — three routes, two of them near-identical in intent (both 3-day culinary/wine loops) |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium–High |
| **Data behind it** | `kakheti-wine-loop` (420 km, 8:00, `car_category: economy`, `best_season: all`); Sighnaghi, Bodbe, Telavi, Tsinandali, Alaverdi, Khareba Wine Tunnel, Kvareli; Gombori Pass |

**EN** `tbilisi to kakheti road trip` · `kakheti wine route by car` ·
`sighnaghi day trip from tbilisi` · `kakheti self drive wine tour` ·
`driving and wine tasting georgia` · `telavi from tbilisi by car` ·
`gombori pass road condition` · `best kakheti wineries by car`

**KA** `კახეთის ღვინის მარშრუტი` · `სიღნაღი ერთდღიანი მოგზაურობა` ·
`თელავი მანქანით` · `გომბორის უღელტეხილი` ·
`კახეთში მანქანით` · `ღვინის მარშრუტი მანქანით`

**RU** `винный маршрут Кахетия на машине` · `Сигнахи из Тбилиси на авто` ·
`Кахетия на машине маршрут` · `Телави из Тбилиси на машине` ·
`Гомборский перевал дорога` · `дегустация вина Кахетия на авто`

**Honest, differentiating and commercially useful:** the wine route is the one
major itinerary where you should *not* upsell a 4x4 — `car_category: economy`,
`best_season: all`. But it is the one where the drink-driving question is real.
A "who drives?" section that links to A23 (with driver) is the correct
monetisation, and no competitor does it.

---

## B6 — Tusheti / Abano Pass

| | |
|---|---|
| **Intent / stage** | destination / MOFU, **the strongest 4x4 conversion path on the site** |
| **Target URL** | `/routes/tusheti-highland-hike/` (5 d) · `/attractions/abano-pass/` · `/attractions/omalo-tusheti/` |
| **Status** | **covered** — `abano-pass.yml` is one of the best-researched pages in the repo (2,850 m, June–Oct, `road: 4x4_only`, insurance-exclusion warning, shared-jeep alternative, full route description in 6 languages) |
| **Difficulty** | **Low–Medium** — the SERP is DRIVE2 blog posts and small tour sites |
| **Volume (est.)** | Medium in ru (Tushetia is a Russian-language travel obsession), Low–Medium en, Low ka |
| **Data behind it** | Abano Pass, Omalo, Dartlo, Shenako-Diklo — all `4x4_only`, `june-september`; route 430 km / 13:30 / `difficulty: hard` |

**EN** `abano pass road` · `when does abano pass open` ·
`driving to tusheti` · `do i need 4x4 for tusheti` ·
`tusheti road danger` · `omalo by car` · `tusheti self drive` ·
`abano pass 4x4 rental` · `is the tusheti road open`

**KA** `აბანოს უღელტეხილი` · `თუშეთის გზა` ·
`აბანოს უღელტეხილი როდის იხსნება` · `ომალოში მანქანით` ·
`თუშეთში ჯიპით` · `თუშეთის გზა საშიშია`

**RU** `перевал Абано` · `когда открывается перевал Абано` ·
`дорога в Тушетию` · `Тушетия на машине` ·
`нужен ли внедорожник в Тушетию` · `Омало как добраться` ·
`дорога смерти Грузия Абано` · `Тушетия на кроссовере`

**Note the Russian long-tail `Тушетия на кроссовере`** ("Tusheti in a
crossover") — observed as a real DRIVE2 post title. That query is someone about
to make an expensive mistake. Answering it correctly (Tucson/RAV4 is **not**
enough; `car_category: offroad`; insurance may exclude the road) is both a
safety obligation and the highest-intent 4x4 upsell on the site.

---

## B7 — Racha

| | |
|---|---|
| **Intent / stage** | destination / TOFU |
| **Target URL** | `/routes/racha-mountain-loop/` (2 d) · `/routes/racha-wine-and-mountains/` (4 d) · `/routes/racha-alpine-hiking-week/` (5 d) · `/regions/racha-lechkhumi/` |
| **Status** | **covered but cannibalised** — three routes for a low-volume destination |
| **Difficulty** | **Low** |
| **Volume (est.)** | Low–Medium |
| **Data behind it** | Nakerala Pass, Shaori, Nikortsminda, Ambrolauri, Khvanchkara wine zone, Oni, Shovi, Chiora (`gravel`), Udziro Lake (`4x4_only`) |

**EN** `racha georgia road trip` · `ambrolauri by car` ·
`khvanchkara wine region drive` · `shovi resort road` ·
`racha road condition` · `oni to shovi drive` · `nakerala pass`

**KA** `რაჭა მანქანით` · `ამბროლაური მანქანით` · `ხვანჭკარის მარშრუტი` ·
`შოვი მანქანით` · `ნაკერალის უღელტეხილი` · `რაჭის გზები`

**RU** `Рача на машине` · `Амбролаури как добраться` ·
`Хванчкара винный маршрут` · `Шови дорога` · `Рача дороги состояние`

**Recommendation:** merge to one strong Racha route + region hub. Three route
pages for a Low-volume destination is the clearest case of self-inflicted
dilution in the routes set.

---

## B8 — Adjara: Batumi hinterland, Goderdzi, Khulo

| | |
|---|---|
| **Intent / stage** | destination / TOFU–MOFU |
| **Target URL** | `/routes/upper-adjara-wine-and-villages/` (4 d) · `/routes/adjara-guria-green-road/` (5 d) · `/routes/black-sea-adjara/` (4 d) · `/regions/adjara/` |
| **Status** | **covered but cannibalised** — three routes |
| **Difficulty** | **Low–Medium** |
| **Volume (est.)** | Medium (ru — Batumi is the Russian-speaking market's primary Georgia destination) |
| **Data behind it** | Makhuntseti waterfall, Keda wine cellars, Khulo cable car, Goderdzi Pass (`gravel`, `june-september`), Green Lake (`4x4_only`), Beshumi (`gravel`), Khikhani Fortress (`4x4_only`), Mtirala NP |

**EN** `batumi to khulo drive` · `goderdzi pass road` ·
`upper adjara road trip` · `batumi day trips by car` ·
`makhuntseti waterfall drive` · `is goderdzi pass open` ·
`batumi to akhaltsikhe road` · `adjara mountain road 4x4`

**KA** `ზემო აჭარა მანქანით` · `გოდერძის უღელტეხილი` ·
`ხულო მანქანით` · `ბათუმიდან ერთდღიანი მარშრუტი` ·
`მახუნცეთის ჩანჩქერი` · `გოდერძის გზა ღიაა`

**RU** `Верхняя Аджария на машине` · `перевал Годердзи` ·
`Хуло из Батуми на машине` · `однодневные поездки из Батуми на авто` ·
`водопад Махунцети как добраться` · `дорога Батуми Ахалцихе через Годердзи`

**The Batumi→Akhaltsikhe route over Goderdzi is a genuinely dangerous
information gap:** it looks like a short cut on a map, it is gravel, and it is
seasonal (`june-september`). Publishing that clearly is a safety contribution and
a strong 4x4 case, and it directly supports the `/car-rental/batumi/` page.

---

## B9 — Samtskhe-Javakheti: Vardzia, Borjomi, Rabati

| | |
|---|---|
| **Intent / stage** | destination / TOFU–MOFU |
| **Target URL** | `/routes/vardzia-borjomi-south/` (2 d) · `/routes/samtskhe-heritage-road/` (4 d) · `/routes/javakheti-lakes-and-birds/` (3 d) · `/regions/samtskhe-javakheti/` |
| **Status** | **covered** — the least cannibalised of the region sets (the three routes have genuinely different purposes) |
| **Difficulty** | **Low–Medium** |
| **Volume (est.)** | Medium |
| **Data behind it** | Vardzia, Khertvisi, Rabati, Sapara, Borjomi-Kharagauli NP, Paravani/Tabatskuri lakes, Tmogvi (`gravel`), Abastumani observatory; `vardzia-borjomi-south` = 550 km / 9:00 / `economy` / `best_season: all` |

**EN** `tbilisi to vardzia day trip` · `vardzia by car` ·
`borjomi from tbilisi driving` · `rabati castle akhaltsikhe drive` ·
`vardzia borjomi road trip` · `is vardzia worth the drive` ·
`bakuriani from tbilisi by car`

**KA** `ვარძია მანქანით` · `ბორჯომი მანქანით თბილისიდან` ·
`რაბათის ციხე` · `ახალციხე მანქანით` · `ბაკურიანი მანქანით`

**RU** `Вардзия на машине из Тбилиси` · `Боржоми на авто` ·
`крепость Рабат Ахалцихе как добраться` ·
`Вардзия Боржоми маршрут на машине` · `Бакуриани из Тбилиси на машине`

---

## B10 — "Do I need a 4x4 for X?" (vehicle-suitability)

| | |
|---|---|
| **Intent / stage** | **the bridge cluster** — informational query, transactional answer / MOFU→BOFU |
| **Target URL** | **NEW URL NEEDED → `/guides/do-i-need-a-4x4-in-georgia/`** |
| **Status** | **missing as a page**; the answer exists as data on 257 attraction records and as one FAQ line on `/car-rental/4x4/` |
| **Difficulty** | **Low–Medium** — the SERP is Tripadvisor threads, DRIVE2 posts and operator blog posts with no data behind them |
| **Volume (est.)** | Medium in aggregate across the long tail. *Reasoning: individually each "do I need 4x4 for [place]" is Low, but there are dozens of them and they all resolve to one page.* |
| **Data behind it** | **the single best dataset on the site** — 23 attractions `car_category: offroad`, 17 `road: 4x4_only`, 20 `gravel`, 59 `suv`, 175 `economy`, each with season and clearance requirements; plus clearance figures for all 17 cars (135 mm Corolla → 235 mm Pajero) |

**EN** `do i need a 4x4 in georgia` · `do you need 4wd in georgia country` ·
`is 2wd enough for georgia` · `what car do i need for georgia roads` ·
`4x4 or normal car georgia` · `do i need 4x4 for svaneti` ·
`do i need 4x4 for kazbegi` · `do i need 4x4 for tusheti` ·
`ground clearance needed georgia roads` · `can i drive a sedan in georgia mountains`

**KA** `მჭირდება თუ არა ჯიპი` · `რომელი მანქანა ჯობია მთაში` ·
`მაღალი გამავლობა საჭიროა?` · `სედანით შეიძლება მთაში ასვლა` ·
`კლირენსი რამდენი უნდა იყოს`

**RU** `нужен ли внедорожник в Грузии` · `хватит ли седана для Грузии` ·
`какая машина нужна для дорог Грузии` · `нужен ли полный привод в Грузии` ·
`клиренс для грузинских дорог` · `можно ли на кроссовере в Сванетию` ·
`нужен ли 4x4 для Казбеги`

**Build shape:** one page, one table, generated from the data — place · region ·
road surface · minimum car class · open season · distance from Tbilisi. Then a
"so which of our cars" block mapping the three answer classes to the three
fleet categories. This is the highest achievability-per-hour page in the entire
map, and it feeds A9, A10 and A23 simultaneously.

---

## B11 — Road conditions and mountain-pass opening dates

| | |
|---|---|
| **Intent / stage** | informational / MOFU — sharply seasonal, high urgency |
| **Target URL** | **NEW URL NEEDED → `/guides/mountain-passes-and-road-conditions/`** |
| **Status** | **missing** |
| **Difficulty** | **Low** — nobody owns this; the current answers live in forum posts of unknown vintage |
| **Volume (est.)** | Medium, extremely spiky (Apr–Jun "is it open yet", Oct–Dec "is it closed yet") |
| **Data behind it** | `best_season` and `open_year_round` on all 257 attractions; the passes are individually documented — Abano (2,850 m, June–Oct, 4x4_only), Jvari Pass, Goderdzi (gravel, June–Sep), Nakerala, Gombori, Zagari; **48 attractions are `open_year_round: false`** |

**EN** `abano pass opening date` · `when does the road to tusheti open` ·
`jvari pass closed today` · `is goderdzi pass open` ·
`georgia mountain passes open dates` · `military highway closed snow` ·
`when does the road to ushguli open` · `georgia road conditions spring` ·
`zagari pass open`

**KA** `აბანოს უღელტეხილი როდის იხსნება` · `ჯვრის უღელტეხილი დახურულია` ·
`გოდერძის უღელტეხილი ღიაა` · `გზის მდგომარეობა` ·
`უღელტეხილები საქართველოში` · `მთის გზები როდის იხსნება`

**RU** `когда открывается перевал Абано` · `Крестовый перевал закрыт` ·
`перевал Годердзи открыт` · `состояние дорог в Грузии` ·
`Военно-Грузинская дорога закрыта сегодня` ·
`когда открывают дорогу в Ушгули` · `перевалы Грузии когда открываются`

**Caveat that must be on the page:** the site holds *typical* seasons, not live
closure status. The page must say so and link to the Roads Department, or it
will earn the wrong kind of trust. A typical-season table plus an honest "this
is the pattern, here is where to check today" beats a stale live-status claim.

---

## B12 — Driving in Georgia (rules, safety, fuel, practicalities)

| | |
|---|---|
| **Intent / stage** | informational / TOFU — the biggest top-of-funnel term in Part B |
| **Target URL** | **NEW URL NEEDED → `/guides/driving-in-georgia/`** |
| **Status** | **missing** — `/faq/` and `/terms/` answer fragments; nothing owns the head term |
| **Difficulty** | **Medium–High** — `wander-lush.org/driving-in-georgia-car-rental-tbilisi/` is the incumbent and is genuinely good; vitistravel.com and several operator blogs also compete |
| **Volume (est.)** | **High** — this is the query every first-time self-drive visitor runs before booking |
| **Data behind it** | `site.yml` fuel figures (8.5 l/100 km, 3.1 ₾/l), per-car consumption, `terms.yml`, `faq.yml`, the road-surface distribution across 257 places, winter tyre period Dec–Apr |

**EN** `driving in georgia country` · `is it safe to drive in georgia` ·
`driving in georgia tips` · `georgia driving rules for tourists` ·
`petrol price georgia` · `speed limits georgia` ·
`are georgian roads bad` · `driving in tbilisi traffic` ·
`toll roads georgia` · `parking in tbilisi`

**KA** `მართვა საქართველოში` · `საგზაო წესები` ·
`სიჩქარის ლიმიტი საქართველოში` · `ჯარიმები` ·
`ბენზინის ფასი` · `პარკირება თბილისში`

**RU** `вождение в Грузии` · `безопасно ли ездить в Грузии` ·
`правила дорожного движения Грузия` · `штрафы Грузия за превышение` ·
`цена бензина в Грузии` · `платные дороги Грузия` ·
`парковка в Тбилиси` · `как ездят в Тбилиси`

**Positioning against wander-lush:** do not write a better travel-blog post —
that fight is already lost on authority. Write the thing a blogger cannot: the
**operator's** view, with the numbers. Real fuel cost per route across 32 routes.
Real road-surface distribution across 257 places. What actually happens at a
handover. What insurance actually excludes. Different page, different query
intent, no head-to-head.

---

## B13 — Attraction-driven "how do I get to X by car"

| | |
|---|---|
| **Intent / stage** | informational / TOFU — a very long tail |
| **Target URL** | `/attractions/{slug}/` × 257 (exists) |
| **Status** | **covered** structurally; **thin** on the query framing — the data is on the page but not written as the answer to "how do I get there" |
| **Difficulty** | **Low** per query |
| **Volume (est.)** | Low individually, **High in aggregate**. *Reasoning: 257 places × 3 languages × several phrasings; individually invisible, collectively the largest addressable set on the site.* |
| **Data behind it** | every attraction has `distance_tbilisi_km`, `drive_time_tbilisi`, `road`, `car_category`, `best_season`, `elevation`, `nearby[]`, plus a `route` narrative field in all 6 languages |

**EN** `how to get to {place} from tbilisi` · `{place} distance from tbilisi` ·
`{place} by car` · `{place} driving time` · `{place} road condition` ·
`{place} parking` · `{place} best time to visit` · `is {place} worth visiting`

**KA** `{ადგილი} როგორ მივიდეთ` · `{ადგილი} მანძილი თბილისიდან` ·
`{ადგილი} მანქანით` · `{ადგილი} რამდენი კილომეტრია`

**RU** `{место} как добраться из Тбилиси` · `{место} расстояние от Тбилиси` ·
`{место} на машине` · `{место} сколько ехать` · `{место} дорога состояние`

**Do not build new URLs for this.** The 257 pages exist. The work is a template
change: promote `distance_tbilisi_km` + `drive_time_tbilisi` + `road` +
`car_category` into a visible "Getting there by car" block with a heading that
matches the query, in all three languages. One template edit, 771 language-pages
improved.

---

## B14 — Seasonal travel

| | |
|---|---|
| **Intent / stage** | informational / TOFU, cyclical |
| **Target URL** | `/itineraries/` seasonal filters + `/guides/winter-driving-georgia/` — **no separate seasonal URLs** |
| **Status** | **thin** |
| **Difficulty** | **Medium** |
| **Volume (est.)** | Medium, cyclical |
| **Data behind it** | `best_season` on all attractions and all 32 routes; 153 places are year-round, 34 are June–Sep only, 2 are winter-only; route seasons range `year-round` → `july-september` |

**EN** `best time to visit georgia` · `georgia in winter road trip` ·
`georgia in autumn driving` · `rtveli grape harvest season georgia` ·
`georgia in may road trip` · `when to visit svaneti` ·
`georgia ski season driving` · `georgia summer road trip heat`

**KA** `როდის ჯობია მოგზაურობა` · `რთველი კახეთში` ·
`შემოდგომაზე სად წავიდეთ` · `ზამთარში სად წავიდეთ მანქანით` ·
`გაზაფხულზე მთაში ასვლა`

**RU** `когда лучше ехать в Грузию на машине` ·
`Грузия осенью на авто ртвели` · `Грузия зимой на машине маршрут` ·
`Грузия в мае на машине` · `когда ехать в Сванетию` ·
`горнолыжный сезон Грузия на машине`

**Warning:** do not spawn `/itineraries/georgia-in-{month}/` pages. That is the
mass-generation anti-pattern `SEO_URL_MAP.md` already rejects. Handle season as
a **filter and a section**, not as a URL dimension.

---

## B15 — Day trips from Tbilisi (predominantly Georgian-domestic)

| | |
|---|---|
| **Intent / stage** | informational / TOFU — **the main Georgian-language travel intent** |
| **Target URL** | **NEW URL NEEDED → `/itineraries/day-trips-from-tbilisi/`** (or `/ka/`-first) |
| **Status** | **missing** — routes exist at 2+ days; the 1-day intent has only `tbilisi-theatre-night` (`days: 1`, in-city) |
| **Difficulty** | **Low–Medium** — the Georgian SERP is news portals (ambebi.ge, allnews.ge) recycling listicles, not purpose-built travel pages |
| **Volume (est.)** | **Medium–High in ka** (this, not "car rental", is what Georgians search on a Friday), Medium in ru, Medium in en |
| **Data behind it** | `distance_tbilisi_km` and `drive_time_tbilisi` on all 257 attractions makes "everything within a 2-hour drive of Tbilisi" a *computable* page — filter, sort, group by drive time |

**EN** `day trips from tbilisi by car` · `best day trips from tbilisi` ·
`places near tbilisi to drive` · `1 day trip from tbilisi` ·
`what to see within 2 hours of tbilisi` · `weekend trips from tbilisi` ·
`mtskheta day trip from tbilisi`

**KA** `სად წავიდეთ შაბათ-კვირას` · `ერთდღიანი მარშრუტი თბილისიდან` ·
`თბილისთან ახლოს სად წავიდეთ` · `სად წავიდეთ მანქანით` ·
`შაბათ-კვირის მარშრუტები` · `ერთდღიანი ექსკურსია თბილისიდან` ·
`სად დავისვენოთ თბილისთან ახლოს`

**RU** `куда поехать из Тбилиси на один день` ·
`однодневные поездки из Тбилиси на машине` ·
`куда съездить из Тбилиси на выходные` ·
`что посмотреть рядом с Тбилиси на авто` ·
`Мцхета из Тбилиси на машине`

**Why this matters commercially:** it is the strongest **Georgian-language**
intent-B cluster, and Georgians renting for a weekend are a repeat-business
segment that tourists are not. `тbilisi + 2 hours` maps directly to the economy
category, which is the fleet's volume tier.

---

## B16 — Distances and drive times

| | |
|---|---|
| **Intent / stage** | informational / TOFU, extremely high-frequency, low-dwell |
| **Target URL** | `/attractions/{slug}/` and `/routes/{slug}/` (exists) — **no new URLs; do not build a distance-matrix page set** |
| **Status** | **covered** structurally, **thin** in presentation |
| **Difficulty** | **Low** |
| **Volume (est.)** | High in aggregate, but low value per visit — these searchers often want only the number |
| **Data behind it** | `distance_tbilisi_km` + `drive_time_tbilisi` on 257 attractions; `distance_km` + `drive_time_total` on 32 routes; `road_legs.yml` |

**EN** `tbilisi to batumi distance` · `tbilisi to kazbegi how long` ·
`tbilisi to mestia driving time` · `kutaisi to batumi drive` ·
`tbilisi to sighnaghi distance` · `how long to drive across georgia`

**KA** `თბილისი ბათუმი მანძილი` · `თბილისი ყაზბეგი რამდენი კილომეტრია` ·
`თბილისი მესტია მანძილი` · `ქუთაისი ბათუმი მანძილი`

**RU** `Тбилиси Батуми расстояние на машине` ·
`Тбилиси Казбеги сколько ехать` · `Тбилиси Местия расстояние` ·
`Кутаиси Батуми на машине сколько` · `сколько ехать через всю Грузию`

**Deliberate restraint:** a `{from}-{to}` distance page matrix would generate
hundreds of near-empty URLs — exactly the doorway pattern `SEO_URL_MAP.md`
rejects. Serve these queries from the pages that already exist by surfacing the
numbers prominently.

---

# 5. Cannibalisation check

## 5.1 Live conflicts — decide these first

| # | Competing URLs | Query they both chase | **Which should win, and why** |
|---|---|---|---|
| **1** | `/trip-planner/` · `/map/` · `/planner/` | "georgia trip planner", "составить маршрут" | **`/trip-planner/` wins.** Three URLs for one intent is one more than `SEO_KEYWORD_MAP.md` anticipated — `/planner/` is not in the URL map at all but is live and appears in `llms.txt`. Action: `/trip-planner/` is canonical and the only one in the sitemap; `/map/` stays as the interactive app with `canonical → /trip-planner/`; **`/planner/` gets `noindex`** (it is a tool state, not a document). Resolve before building anything else in Part B — every internal link from the itinerary and route pages depends on which one is the destination. |
| **2** | `/tours/` · `/itineraries/` · `/routes/` | "georgia road trip", "маршрут по Грузии" | **`/itineraries/` wins the duration queries; `/routes/` wins the named-route queries; `/tours/` should stop competing.** `/tours/` is currently the routes index but its name signals a guided-tour product the business does not sell. Rename its purpose to "all road trips" and canonicalise, or fold it into `/routes/`. Leaving three hubs is the largest structural dilution on the site. |
| **3** | 3 × Svaneti routes | "svaneti road trip", "дорога в Сванетию" | **`/routes/svaneti-expedition/` wins** (5 days, `offroad`, the only one that starts from Tbilisi at 1,050 km — it matches the query "drive to Svaneti"). `svaneti-alpine-circuit` and `svaneti-village-trek` are both 6-day hiking products differentiated only by trail choice; they must be retitled around **hiking**, not driving, or merged. As written, three pages split the same link equity. |
| **4** | 3 × Racha routes | "racha on machine", "Рача на машине" | **`/routes/racha-mountain-loop/` wins** (2 days, the entry-level shape most searchers want). Merge `racha-wine-and-mountains` into it as a "make it 4 days" extension; keep `racha-alpine-hiking-week` only if it is genuinely re-pitched as hiking. Racha is a Low-volume destination carrying three pages. |
| **5** | 3 × Kakheti routes | "kakheti wine route by car" | **`/routes/kakheti-wine-loop/` wins** (3 days, `economy`, `best_season: all` — the canonical shape). `kakheti-table-and-cellar` is a near-duplicate 3-day culinary loop and should merge. `kakheti-cycle-and-wine` is genuinely different (cycling) and survives. |
| **6** | 3 × Adjara routes | "upper adjara", "Аджария на машине" | **`/routes/upper-adjara-wine-and-villages/` wins the mountain query; `/routes/black-sea-adjara/` wins the coast query.** These are genuinely different intents. `adjara-guria-green-road` straddles both and should be retitled to lead on **Guria**, which nothing else covers. |
| **7** | 2 × Kazbegi routes | "tbilisi to kazbegi" | **`/routes/military-highway-kazbegi/` wins** — 2 days, `best_season: all`, and it carries the Russian head term Военно-Грузинская дорога. `kazbegi-hiking-base` is a 4-day hiking product; retitle around hiking. |
| **8** | 2 × Tbilisi city routes | "things to do in tbilisi" | `tbilisi-history-walk` and `tbilisi-architecture-and-markets` overlap heavily (both 2-day, `economy`, sharing Sololaki, the National Museum and Chronicle of Georgia). **Neither should chase "things to do in Tbilisi"** — that query wants `/regions/tbilisi/` or `/map/`. Merge the two, or clearly split walking vs. markets. |
| **9** | `/fleet/` vs `/car-rental/` | "rental cars georgia" | Already decided in `SEO_KEYWORD_MAP.md` — catalogue vs. intent hub. **Still correct, no change.** Verify the retitle actually shipped. |
| **10** | `/car-rental/suv/` vs `/car-rental/4x4/` | "4wd rental georgia" | Already decided — comfort/clearance vs. genuine off-road. **Still correct**, and the data now backs it hard (181–195 mm AWD vs. 210–235 mm 4WD with low range). Make the clearance numbers visible on both pages so the distinction is checkable rather than asserted. |
| **11** | `/faq/` vs `/car-rental/` vs `/terms/` | "car rental georgia deposit / age / insurance" | **`/car-rental/` and its child policy pages win; `/faq/` must stop restating the same facts** in long-form. `/faq/` has 30+ answers duplicating hub sections — and, worse, **contradicting them** (§5.3). Reduce `/faq/` to short answers that link to the authoritative page. |
| **12** | `/regions/{key}/` vs `/routes/{slug}/` | "kazbegi", "svaneti", "racha" | **Routes win the "by car" queries; regions win the "what's in this region" queries.** But note the naming mismatch: nobody searches "Mtskheta-Mtianeti" — they search "Kazbegi". Region pages must carry the popular destination name in the H1/title (e.g. "Mtskheta-Mtianeti — Kazbegi, Gudauri and the Military Highway") or they will never be found. |

## 5.2 Guards to apply to the new pages proposed here

| New page | Would cannibalise | Guard |
|---|---|---|
| `/car-rental/monthly/` | `/car-rental/` and every category page (all carry `price_30`) | Monthly page owns *duration* pricing and the tier table; category pages link to it and do not restate the discount tiers |
| `/car-rental/one-way/` | 3 airport pages + 3 city pages | One-way page owns the fee and the city-pair matrix; location pages get one sentence + link |
| `/car-rental/deposit/` | `/car-rental/` §deposit, `/faq/`, `/terms/` | Deposit page becomes the single authority; the hub keeps 2 sentences + link; `/faq/` answers shrink to one line + link |
| `/car-rental/with-driver/` | `/car-rental/business/`, `/faq/` | Driver page owns the service and its pricing; business page mentions availability + link |
| `/guides/do-i-need-a-4x4-in-georgia/` | `/car-rental/4x4/`, `/car-rental/suv/` | Guide is **informational** (which road needs what); category pages are **transactional** (book this car). Guide must not carry booking CTAs above the fold, or it will compete for the commercial query |
| `/guides/driving-in-georgia/` | `/faq/`, `/blog/*`, `/terms/` | Guide is the pillar; the 4 blog posts become supporting spokes linking up. Consider consolidating `rogor-viqiravot-manqana-saqartveloshi` into it |
| `/guides/mountain-passes-and-road-conditions/` | `/attractions/abano-pass/`, `/attractions/goderdzi-pass/` | Guide covers **all** passes comparatively; individual attraction pages keep their own detail and link up. Guide must not out-detail the attraction page on any single pass |
| `/itineraries/day-trips-from-tbilisi/` | `/itineraries/georgia-3-days/`, `/map/` | Day-trips page is strictly **1-day, from Tbilisi**; the 3-day page must not claim day-trip framing |

## 5.3 Blocked clusters — source-data conflicts that must be resolved

These are contradictions **between files already in the repo**. They are not
matters of opinion, and no cluster copy should be written on top of them.

| Fact | `rental_policy.yml` (stated as source of truth) | `faq.yml` / `llms.txt` (currently live) | Blocks |
|---|---|---|---|
| **Cross-border** | `allowed: false` — vehicles stay in Georgia | `llms.txt`: "Armenia (150 GEL) and Turkey (250 GEL) allowed with permit" | **A19** |
| **Insurance** | TPL included; CDW is a 25 ₾/day add-on; excess 1,000 ₾; "deliberately NOT claimed: full coverage, zero excess" | `faq.yml`: rate "includes ... CDW insurance"; `llms.txt`: "SCDW zero-excess option for 25–45 GEL/day" | **A17** |
| **Mileage** | `unlimited: true`, unqualified | `llms.txt`: "300 km/day limit on cross-border trips" | **A15** (partially) |
| **Minimum age** | `min_driver_age: 21` flat, "no separate young-driver surcharge" | `faq.yml` + `llms.txt`: 21 economy / 23 SUV+minivan / 25 business+4x4 — and `toyota-land-cruiser-prado.yml` body text says "minimum driver age 25" | **A18** |
| **Long-term discount** | tiers implied by `price_7_29` / `price_30` (≈ −10% / −25%) | `faq.yml`: −10% / −25% / −40% corporate; plus a **+15% July–August seasonal coefficient** that appears nowhere in `rental_policy.yml` | **A20** (partially — build the page, but reconcile the discount claims first) |
| **Prepayment** | `prepayment_required: false` — "pay at pickup" | `faq.yml`: "the booking is confirmed after the required payment"; `booking.yml`: `payment_required: true`; `llms.txt`: "require payment before confirmation" | **A1 hub trust copy** |

`llms.txt` is the most urgent of these: it is machine-read by AI assistants, so
the unreconciled version is the one currently being quoted to users who ask an
assistant about renting from RentUp.

---

# 6. Ranked build list — the next 20 pages

Ranked by `intent value × achievability`, not volume. "Data ready" means the page
can be written today from files in the repo, with no new business facts invented.

| # | Cluster | Target URL | New? | Data already available | Why here |
|---|---|---|---|---|---|
| **1** | B10 — do I need a 4x4 | `/guides/do-i-need-a-4x4-in-georgia/` | **NEW** | 257 attractions × (`road`, `car_category`, `best_season`); 17 cars × `clearance` (135–235 mm) + `drive` | Highest achievability on the site. Unique data, weak SERP (forums), and it feeds the 4x4/SUV/with-driver clusters at once. Nothing else converts intent B into intent A this directly. |
| **2** | A20 — monthly / long term | `/car-rental/monthly/` | **NEW** | `price_30` on all 17 cars (56–248 ₾), `price_7_29`, `max_rental_days: 90`, FAQ tiers | Best unbuilt commercial page. Soft SERP, 20–30× booking value, data 100% complete. Reconcile the discount tiers (§5.3) first. |
| **3** | B4 — Svaneti / Ushguli road | `/routes/svaneti-expedition/` (rewrite) | existing | `ushguli: gravel/offroad/june-september`; Adishi, Koruldi, Shkhara `4x4_only`; route 1,050 km / 21:00 | "Is the road to Ushguli paved?" is unanswered on the live SERP and the site has the answer. Also fixes cannibalisation #3. |
| **4** | B6 — Tusheti / Abano Pass | `/attractions/abano-pass/` (promote + interlink) | existing | Already the best-researched page in the repo, 6 languages, with the insurance-exclusion warning | Zero writing cost — it needs surfacing, internal links from `/car-rental/4x4/` and `/car-rental/with-driver/`, and sitemap prominence. Highest 4x4 conversion intent on the site. |
| **5** | B11 — passes and road conditions | `/guides/mountain-passes-and-road-conditions/` | **NEW** | `best_season` + `open_year_round` on 257 places; 48 seasonal; individual pass records | Nobody owns it. Spiky but reliable seasonal demand in all three languages. Must carry the "typical, not live" caveat. |
| **6** | A16 — deposit (honest counter-page) | `/car-rental/deposit/` | **NEW** | 300–1,200 ₾ by category, `card_hold` + `cash_accepted: true`, 3-day release | `без залога` is the highest-pull Russian modifier and we cannot claim it. Cash-accepted is a real differentiator against card-only operators. |
| **7** | A12 — business class | `/car-rental/business/` | **NEW** | Camry 210 ₾, E-Class 290 ₾, BMW 5 310 ₾, deposit 1,000 ₾; `fleet.yml` driver note | Category exists with 3 cars and no page. Low competition, highest per-day rate. Cheapest revenue on this list. |
| **8** | A21 — one way | `/car-rental/one-way/` | **NEW** | `one_way.fee_gel: 100`, 6 pickup points, airport fees | Kutaisi-in / Tbilisi-out is a standard Georgia trip shape and nobody has built the page. Small page, clear intent. |
| **9** | B15 — day trips from Tbilisi | `/itineraries/day-trips-from-tbilisi/` | **NEW** | `distance_tbilisi_km` + `drive_time_tbilisi` on all 257 places — the page is computable | The strongest Georgian-language travel intent, currently served by recycled news listicles. Repeat-business audience. |
| **10** | B13 — "getting there by car" block | `/attractions/{slug}/` × 257 (template) | existing | Every attraction already has all six fields | One template edit improves 771 language-pages. Best effort-to-coverage ratio in the document. |
| **11** | A23 — with driver | `/car-rental/with-driver/` | **NEW** | `faq.yml`: 120 ₾/day (8 h) + 20 ₾/h overtime; business cars available with driver; 32 routes with drive times | A different customer, not a rental variant. Natural conversion for everyone who reads #1 and decides not to drive it themselves. |
| **12** | B12 — driving in Georgia | `/guides/driving-in-georgia/` | **NEW** | fuel 8.5 l/100 km @ 3.1 ₾/l, per-car consumption, road-surface distribution, terms | The biggest TOFU term in Part B. Do not fight wander-lush on travel-blog terms — win on operator numbers. |
| **13** | A18 — requirements / documents | `/car-rental/requirements/` | **NEW** | age 21, 2 years, licence types, passport — **after** reconciling §5.3 age conflict | The Russian `для россиян` sub-cluster is editorial-owned and winnable with concrete answers. |
| **14** | B3 — Kazbegi road | `/routes/military-highway-kazbegi/` (rewrite) | existing | 340 km / 6:40 / `best_season: all`; Gergeti paved vs Juta/Truso non-paved | Highest-volume destination in Part B. Carries the Russian head term. Rewrite to answer "do I need a 4x4?" honestly — no for Stepantsminda, yes for Juta. |
| **15** | A24 — winter driving | `/guides/winter-driving-georgia/` (promote from blog) | promote | existing blog post ×6 languages; Gudauri + Hatsvali winter-only; winter tyres Dec–Apr | Seasonal revenue (Gudauri/Bakuriani). Decide the blog→guide canonical rather than running both. |
| **16** | B8 — Goderdzi / Upper Adjara | `/routes/upper-adjara-wine-and-villages/` (rewrite) | existing | Goderdzi `gravel/june-september`, Green Lake + Khikhani `4x4_only` | A genuine safety gap: Batumi→Akhaltsikhe looks like a shortcut and is a seasonal gravel pass. Supports `/car-rental/batumi/`. |
| **17** | B5 — Kakheti wine + who drives | `/routes/kakheti-wine-loop/` (rewrite) | existing | 420 km / 8:00 / `economy` / `best_season: all` | High volume, and the one route where the honest answer is "you do not need a 4x4" — which makes the "who drives after the tasting?" link to #11 credible rather than salesy. |
| **18** | A17 — insurance and excess | `/car-rental/insurance/` | **NEW — BLOCKED** | TPL/CDW/excess in `rental_policy.yml`, contradicted by `faq.yml` and `llms.txt` | Do not write until §5.3 is resolved. Listed here so it is scheduled, not forgotten. |
| **19** | A14 — automatic | `/car-rental/automatic/` | **NEW (low)** | 15 of 17 automatic; only Transit + Sprinter manual | Try the hub-section route first. Build the URL only if Search Console shows the hub failing to capture the query. |
| **20** | A13 — commercial van | `/car-rental/van/` | **NEW (low)** | Transit 185 ₾, Sprinter 215 ₾, deposit 800 ₾, both manual | Completes the category set at near-zero cost. Domestic/B2B intent. Genuinely low priority — do not let it displace #1–#12. |

## 6.1 What is deliberately not on the list

| Not building | Why |
|---|---|
| `/car-rental/no-deposit/` | We do not offer it. `waiver_available: false`. #6 answers the query honestly instead. |
| `/car-rental/{city}/` beyond the 6 pickup points | `places.yml` has 37 cities; only 6 are served. The other 31 would be doorway pages with no distinct information — already rejected in `SEO_URL_MAP.md`. |
| `/itineraries/georgia-{1..30}-days/` | Mass generation. The five curated bands are correct. (2-day and 4-day bands are *arguable* — the route data supports them — but only after the five existing bands are shown to perform.) |
| `/itineraries/georgia-in-{month}/` | Season is a filter, not a URL dimension. |
| `{from}-{to}` distance matrix pages | Hundreds of near-empty URLs for a low-value, low-dwell query. Serve from existing pages (B16). |
| Transliterated Georgian URLs (`/manqanis-qiraoba/`) | Duplicates `/ka/car-rental/`. Handle transliteration in body copy (§1.2). |
| A `/guides/cross-border/` page | Blocked on contradictory source data (§5.3). |

---

## 7. Summary of counts

| | |
|---|---|
| Clusters defined | **42** — 26 intent A, 16 intent B |
| Languages per cluster | 3 (ka · en · ru), with native query sets, not translations |
| Supporting variants listed | ~1,150 across the three languages |
| Clusters mapped to an **existing** URL | 24 |
| Clusters requiring a **new** URL | 13 (each with the exact proposed path) |
| Clusters served by a section/anchor, **no new URL** | 5 |
| Clusters **blocked** on source-data conflicts | 3 (A15 partial, A17, A19) |
| Cannibalisation conflicts identified | 12 live + 8 guards for proposed pages |
| Pages in the ranked build list | 20 (13 new, 7 rewrites/promotions) |

**Single most important next action** is not a page. It is §5.3: reconcile
`rental_policy.yml`, `faq.yml` and `llms.txt` so that cross-border, insurance,
mileage, age and prepayment each have one answer. Three of the highest-intent
clusters are blocked on it, `llms.txt` is currently feeding the wrong version to
AI assistants, and every page built before the reconciliation will have to be
rewritten in three languages afterwards.

---

*Estimates in this document are labelled as such throughout. Replace the volume
and difficulty bands with Search Console and keyword-tool data before committing
budget. SERP observations were made on 2026-08-29 and will drift.*
