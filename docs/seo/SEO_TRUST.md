# RentUp.ge — Trust / E-E-A-T Audit

Audit date: 2026-08-29 · Scope: trust, transparency and editorial-integrity signals only
(technical/keyword SEO is covered separately in `docs/seo/SEO_AUDIT.md`; this document does not
repeat those findings except where they bear directly on trust).

Read for this audit: `content/pages/{about,contact,terms,faq,community}.yml`,
`content/settings/{site,rental_policy}.yml`, `build.py` (`org_node()`, `render_static_page()`),
`docs/seo/SEO_AUDIT.md`. Nothing in this list, or in `build.py`/`theme.py`, was modified.

---

## 1. Trust signals that exist today, and where

| Signal | Present? | Where | Notes |
|---|---|---|---|
| Phone number | ✅ (but see §3) | `/contact/` page, `org_node()` JSON-LD | Real number `+995 597 55 55 65` lives in `site.yml`. The **visible contact page shows a different, placeholder number** — see §3, finding 1. |
| WhatsApp | ✅ in data, not surfaced | `site.yml: whatsapp` | Real value exists (`995597555565`) but is not rendered on `/contact/` (the page shows a separate placeholder "Mobile / WhatsApp" number instead) and not emitted in `org_node()`. |
| Postal address | ✅ | `org_node()` JSON-LD, `/contact/` table, `/about/` | Consistent: Vazha-Pshavela Ave. 71, Tbilisi 0186, across schema and the visible page. This one is solid. |
| Opening hours | ✅ | `org_node()` `openingHoursSpecification`, `/contact/` table | Consistent 09:00–21:00, all days, in both schema and visible copy. |
| Company founding date | ✅ | `org_node()` `foundingDate`, `/about/` | Consistent: 2019 in both schema and the About page narrative. |
| Terms of service / rental terms | ✅ strong | `/terms/` (`content/pages/terms.yml`) | Detailed and genuinely useful: documents by nationality, age/experience tables, fuel policy, insurance (CDW/TPL/SCDW) with an explicit "insurance does not cover" list, cross-border rules, penalties table. This is above-average transparency for the category. |
| Cancellation policy | ✅ (on `/terms/` only) | `terms.yml → "Booking, cancellation and changes"` | Clear tiered policy (>48h free, 24–48h = 1 day, <24h/no-show = 2 days). Not duplicated anywhere else, not surfaced on `/pricing/` or `/fleet/` at the point of decision. See §3, finding 4 for a second, contradicting cancellation policy in `rental_policy.yml`. |
| Insurance explanation | ✅ good | `terms.yml`, reinforced in `faq.yml` | CDW/TPL explained in plain language, excess amounts given, exclusions listed (off-road damage outside 4x4 category, tyres/wheels/underbody, keys, DUI, unauthorized drivers, commercial use). This is genuinely above the category norm. |
| FAQ covering deposits, documents, routes | ✅ strong | `/faq/` (`content/pages/faq.yml`) | 30+ Q&As, including honest specifics like "we have no EVs, only hybrids" and named mountain-road caveats (Abano Pass, Ushguli). |
| Company legal identity (name, reg. number) | ⚠️ present but marked fake | `/contact/` "Company details" table | Table has real-looking fields (legal name, tax ID, bank, VAT) but the content itself contains an explicit editorial note in all 6 languages: *"these company details are placeholders — replace them with the real data before going live."* See §3, finding 2. |
| Privacy policy | ❌ missing | — | No `content/pages/privacy.yml`, no page in `PAGES`, no link anywhere. |
| Refund policy as a standalone page | ❌ missing | — | Cancellation terms exist only buried inside `/terms/`; no dedicated, linkable refund page. |
| Complaints / dispute route | ❌ missing | — | No stated escalation path if a customer disputes a charge or a deposit deduction beyond "call us." |
| "Who wrote/reviewed this" for travel guides | ❌ missing | — | 257 attraction pages and 32 route pages carry no author, reviewer, or last-updated date anywhere in the content schema or templates. |
| Reviews / testimonials | ❌ not real | `content/pages/community.yml` | The community page exists in all 6 languages but every `blocks:` array is empty — it is a shell, not live social proof. `attraction.rating` (e.g. `4.0` on Abano Pass) is an **editorial star rating** (`stars_html()`'s own docstring: "სარედაქციო შეფასება" — editorial assessment), not a user/aggregate rating, and it is correctly **not** emitted as schema.org `AggregateRating` — so no false review signal reaches Google. It is, however, displayed to users as plain stars with no "editorial rating, not user reviews" label. See §3, finding 6. |

---

## 2. What `org_node()` asserts vs. what a visitor can verify

`org_node()` (build.py:379) builds the `AutoRental` + `LocalBusiness` JSON-LD emitted on every
indexable page. Field by field:

| Schema field | Value | Verifiable on the live site? |
|---|---|---|
| `name` | `BRAND` = `site.yml → rental_brand` = **"Drive On"** | ✅ Matches every visible page title and heading — the site is internally consistent about its own name today. (Separately flagged in `SEO_AUDIT.md` P0-1: the *domain* is `rentup.ge` while the *displayed brand* is "Drive On" — not a fabrication, but a naming mismatch worth resolving before or alongside a trust push.) |
| `telephone` | `site.yml → phone_e164` = **+995597555565** | ❌ **No.** The `/contact/` page — the one page a user or Google would check to confirm this number — shows **`+995 32 2 000 000`**, a different number, in all 6 languages. **This is exactly the kind of schema-vs-visible-content mismatch Google's structured-data guidelines treat as a policy violation risk**, because the schema asserts a fact the page itself contradicts. |
| `foundingDate` | 2019 | ✅ Matches `/about/`. |
| `address` | 71 Vazha-Pshavela Ave., Tbilisi 0186 | ✅ Matches `/contact/` and `/about/`. |
| `geo` | lat/lon from `site.yml` | Not independently checkable by a lay user, but internally consistent; no finding. |
| `openingHoursSpecification` | 09:00–21:00, all 7 days | ✅ Matches `/contact/`. |
| `email` | Emitted only `if SITE.get("email")` | `site.yml → email` is `''` (empty) — **correctly omitted**. The code comment even explains why (avoid an empty `mailto:`). This is good defensive practice, not a finding. |
| `sameAs` (social profiles) | Emitted only `if SITE.get("social")` | `site.yml → social` is `[]` — **correctly omitted**. No phantom social presence claimed. |
| `priceRange` | Hard-coded `"$$"` | Not independently falsifiable; low risk, no finding. |
| `currenciesAccepted` | `"GEL, USD, EUR"` | Matches FAQ ("cash accepted in USD/EUR at NBG rate") — consistent. |
| Legal entity name / registration number / VAT | **Not present in schema at all** | N/A — and that is the *correct* choice given §1's finding that the only legal-identity data in the content is explicitly marked as placeholder. `org_node()` is not overclaiming here; the risk sits entirely in the visible `/contact/` table, not in the schema. |

**Net finding:** `org_node()` itself is disciplined — it omits fields it has no real data for (email,
social) rather than inventing them. The one concrete schema-vs-visible-page contradiction is the
**phone number** (finding 1 below). Everything else the schema asserts is either verifiable on-page
or correctly absent.

---

## 3. Findings, prioritised

Each item is marked **[CAN DO NOW]** — the real fact already exists in the repo and just needs to
replace a placeholder or be surfaced — or **[DATA NEEDED]** — only RentUp/Drive On's owner can supply
the fact.

1. **[CAN DO NOW] — Phone number mismatch between schema and the `/contact/` page.**
   `org_node()` emits the real number from `site.yml` (`+995 597 55 55 65`), but `contact.yml`
   hard-codes a placeholder (`+995 32 2 000 000`) and a placeholder email (`info@example.ge`) in
   all 6 languages, plus a second placeholder "Mobile/WhatsApp" number that doesn't match
   `site.yml`'s real WhatsApp value either. This is the single highest-priority fix: a schema
   claim a user can disprove by reading the same page is a structured-data policy risk, not just
   a copywriting gap. Fix: replace the four placeholder contact fields in `contact.yml` with
   `site.yml`'s real `phone_e164` / `whatsapp` values (email stays blank until finding 8 is
   resolved).

2. **[DATA NEEDED] — Legal entity name, tax ID and bank details on `/contact/` are fabricated
   placeholders.** The "Company details" table shows `Drive On LLC` / `4XXXXXXXX` / two named
   banks / "VAT: Yes" — none of which exist in any settings file, and the content itself says so
   explicitly ("these company details are placeholders... replace them with the real data before
   going live"). This is the most consequential gap for E-E-A-T: a car-rental business's legal
   registration is exactly the kind of fact Google and users use to judge whether a "Company" is
   real. Needed from the owner: registered legal name, Georgian tax/ID number (საიდენტიფიკაციო
   კოდი), actual bank, actual VAT status. Until supplied, the honest interim fix is to **remove
   the fabricated table**, not leave it live — a wrong tax ID is worse than none.

3. **[DATA NEEDED] — No privacy policy.** No page, no content file, no link. Required for any
   business that collects personal data (ID/passport copies, driving licence, payment card for
   deposit hold, phone number, corporate registry extracts per `terms.yml`). Needed from the
   owner: how long ID/licence copies are retained, whether they're shared with insurers or banks
   for the deposit hold, and a contact for data requests. Once those facts exist, the page itself
   is **[CAN DO NOW]** to build — the terms.yml block structure already supports a page like this.

4. **[DATA NEEDED / inconsistency] — Two different, contradicting cancellation and cross-border
   policies exist in the repo.** `terms.yml` (the live, visible page) states: free cancellation
   at >48h, 1-day charge at 24–48h, 2-day charge at <24h/no-show; and cross-border travel to
   Armenia and Turkey is *permitted* with a per-day fee and a 300 km/day cap. `rental_policy.yml`
   — explicitly headed **"PROPOSED DEFAULTS drafted for the owner's approval (2026-08-29)"** —
   states a different cancellation window (`free_until_hours: 24`, `no_show_charge_days: 1`) and
   `cross_border.allowed: false` ("vehicles stay in Georgia"). Neither file references the other.
   If `rental_policy.yml` is ever wired into a future `/car-rental/` template (as its header
   implies it will be), the site will show two different cancellation policies and two different
   cross-border answers depending on which page a visitor lands on — a direct trust/consistency
   failure, and potentially a contractual one. This needs the owner to confirm which numbers are
   actually correct before either file is treated as authoritative; it cannot be resolved by
   guessing.

5. **[DATA NEEDED] — No named insurer, and no explanation of who underwrites CDW/TPL.**
   `terms.yml` and `faq.yml` explain CDW/TPL/SCDW mechanics well (what's covered, the excess
   amounts, what's excluded) but never name an insurance provider. For a category where "we
   handle your accident risk" is the core trust question, saying *who* actually carries that risk
   (a licensed Georgian insurer's name) would materially strengthen this. This is squarely a fact
   only the business can supply.

6. **[CAN DO NOW] — Editorial star ratings on attraction pages have no visible label
   distinguishing them from user reviews.** `attraction.rating` (e.g. `4.0`) is rendered via
   `stars_html()` as plain stars with a `title`/`aria-label` of "{rate_label}: 4/5" — the
   underlying `te(lang, "rate_label")` string should be checked to confirm it reads as an
   editorial/curatorial rating (e.g. "Our rating") rather than something a user could mistake for
   a crowd rating. Correctly, this rating is **not** emitted as schema.org `AggregateRating`
   anywhere (verified in `build.py`), so there's no false-reviews schema risk — only a labeling
   clarity gap on the visible page. Low effort, no new data needed.

7. **[CAN DO NOW] — No complaints/dispute-resolution route stated anywhere.** `/faq/` and
   `/terms/` explain what happens in a technical breakdown (call the 24/7 hotline) but nothing
   explains how a customer disputes a deposit deduction, a damage assessment, or a charge they
   believe is wrong. Every fact needed already exists (the same phone/WhatsApp channel, the same
   09:00–21:00 hours) — this is a copy addition, not a new data need. Recommend one paragraph on
   `/terms/` and `/faq/`: how to raise a dispute, and what response time to expect (the site
   already promises "15 minutes" for booking replies — the same claim could extend to disputes if
   the owner confirms it's true for that channel too).

8. **[DATA NEEDED] — `site.yml → email` is empty; the visible `/contact/` page nonetheless shows
   a placeholder email (`info@example.ge`) six times over.** Either the business has a real
   support email (owner to supply, then it becomes [CAN DO NOW] to add to `site.yml` and swap in),
   or it deliberately operates phone/WhatsApp-only — in which case the honest fix is to **remove**
   the placeholder email from `/contact/` rather than publish a non-functional address in six
   languages.

9. **[CAN DO NOW] — No "last reviewed" convention exists for the 257 attraction / 32 route
   pages**, and none of the content schema fields support one yet (`content/attractions/*.yml`
   has no `reviewed:` or `updated:` key; confirmed by grep). This is listed here as a **process**
   fix, not a data fix: adding a `last_reviewed:` field to the attraction/route schema and
   populating it with the date each entry's `road:`/`car_category:`/`drive_time_*:` values were
   last checked against real conditions requires no external fact from the owner — only a
   decision to start dating entries going forward, using today's date for anything checked during
   this or a following audit pass. See §4 for the exact convention proposed.

---

## 4. Editorial transparency for the 257 travel guides and 32 routes

**What should be stated, and why:** every attraction and route page recommends a road quality, a
drive time, and a vehicle category. Right now nothing on the page tells a reader *how* those
numbers were produced. The honest answer is also the reassuring one — they come from the site's
own structured trip data (`road:`, `car_category:`, `drive_time_tbilisi:` / `drive_time_total:`
fields, confirmed present on every attraction and route file), the same fields the booking and
pricing logic reads. That is a legitimate, defensible "how this page was made" statement, and it
is what `content/settings/seo_trust.yml` (`editorial.policy_body`, all 6 languages) says.

**Two things it should explicitly avoid claiming**, because neither is true today:

- **A named author or reviewer per page.** There is no author field in the content schema, no
  editorial-team page, and inventing bylines or "written by our local guide" language for 257
  auto-generated pages would be exactly the kind of fabricated authorship E-E-A-T guidance
  penalizes, not rewards. The honest framing is a data-source statement, not a person.
- **First-hand travel experience.** Several attraction bodies already use experiential language
  ("the last hour is usually driven in shadow," "a hat and a windproof jacket matter") that reads
  as first-hand — but nothing in the repo indicates these were road-tested by RentUp/Drive On
  staff specifically, as opposed to compiled from public sources, driver reports, or general
  knowledge of the routes. **Do not add "we drove this personally" language unless the owner
  confirms each specific route was actually driven and by whom** — that is squarely
  **[DATA NEEDED]**, route by route, and should not be assumed.

**What "drive time" should be stated to mean:** an estimate derived from road type and distance
in the structured data, not live traffic or a personally timed drive. This matters because several
routes (Abano Pass: "5:00" for ~30 km of gravel climbing) already read as realistic, hard-won
numbers — stating plainly that they're *estimates from road/distance*, not live-traffic
predictions, protects the site from a visitor who hits a landslide closure or a slower personal
pace and feels misled.

**Proposed "last reviewed" convention** (process, not data):
1. Add an optional `last_reviewed: 'YYYY-MM-DD'` key to the attraction and route YAML schema.
2. Populate it whenever `road:`, `car_category:`, `entry_fee:`, `best_season:`, or
   `open_year_round:` is edited for accuracy (not on every unrelated copy edit).
3. Render it next to `data_source_label` from `seo_trust.yml` using `last_reviewed_label`, e.g.
   *"Last reviewed: 12 March 2026 · Source: route and place data."*
4. Entries with no `last_reviewed` value yet should show the source line without a date, rather
   than a fabricated or build-date placeholder — a missing date is honest; a fake one is not.
5. Prioritise dating the mountain/border-adjacent entries first (Abano Pass, Ushguli, anything
   with `road: 4x4_only` or a cross-border note) — these are exactly the pages where a reader's
   safety depends on the information being current, and where "last reviewed" carries the most
   trust value.

---

## 5. Summary counts

- **[DATA NEEDED]: 5** — legal entity/tax ID/bank/VAT (#2), privacy policy substance (#3),
  the cancellation/cross-border policy conflict (#4, needs an owner ruling on which numbers are
  correct), named insurer (#5), real support email or a decision to go phone/WhatsApp-only (#8).
- **[CAN DO NOW]: 4** — fix the phone/WhatsApp mismatch on `/contact/` (#1), label editorial
  ratings clearly (#6), add a dispute/complaints paragraph using existing contact channels (#7),
  and start a `last_reviewed` convention for attractions/routes (#9).

## 6. Schema claim not visible to a user (headline finding for this audit)

**`org_node()`'s `telephone` field (`+995 597 55 55 65`, from `site.yml`) does not match the phone
number printed on `/contact/` (`+995 32 2 000 000`, a hard-coded placeholder in
`content/pages/contact.yml`, repeated in all 6 languages).** Every other schema field checked in
§2 is either verifiable on-page or correctly omitted when no real data exists — this is the one
concrete case in the entire `org_node()` output of the schema asserting something the visible page
contradicts, and it should be fixed before any broader trust push, since it is trivial to fix
(§3, finding 1) and is precisely the class of issue automated structured-data review tools flag.

---

## Deliverables from this audit

- `docs/seo/SEO_TRUST.md` — this document.
- `content/settings/seo_trust.yml` — CAN-DO-NOW copy (editorial policy note, last-reviewed/source
  labels, a trust paragraph for car-rental pages, and a travel-page disclaimer), in all 6
  languages (ka, en, ru, fa, he, ar). Content-only, matching the existing convention of
  `content/settings/seo_meta.yml`: not yet wired into `build.py`.
