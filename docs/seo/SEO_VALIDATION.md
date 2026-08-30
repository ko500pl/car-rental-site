# RentUp.ge — SEO Validation

Automated checks live in `tests/test_seo.py` and the human-readable report in `scripts/seo_audit.py`
(run: `python scripts/seo_audit.py dist`). Both run against the built `dist/` tree, so they validate
exactly what ships.

## Automated assertions

| # | Assertion | Scope |
|---|---|---|
| 1 | Exactly one `<link rel="canonical">` per page, absolute, https, `rentup.ge` host | every HTML page |
| 2 | Canonical is self-referencing unless page is a deliberate alias (`/pricing/`) | every indexable page |
| 3 | `<title>` present, non-empty, ≤ 70 chars visible, unique within a language | every indexable page |
| 4 | `<meta name="description">` present and non-empty | every indexable page |
| 5 | Exactly one `<h1>` | every indexable page |
| 6 | `<meta name="keywords">` absent | all pages |
| 7 | hreflang cluster complete: 6 languages + `x-default`, all absolute, reciprocal | every localized page |
| 8 | Sitemap contains only URLs that exist in `dist/` and are not `noindex` | sitemap(s) |
| 9 | Every indexable page is present in exactly one sitemap child | dist vs sitemaps |
| 10 | No `noindex` on: `/`, `/fleet/`, `/map/`, `/tours/`, `/car-rental/*`, `/routes/*`, `/attractions/*`, `/itineraries/*` | guard list |
| 11 | `noindex` present on: `/trip/`, `/account/`, `/app/`, `/admin/*`, `/pricing/` | guard list |
| 12 | All JSON-LD blocks parse as valid JSON | every page |
| 13 | `BreadcrumbList` items all resolve to real files | pages with breadcrumbs |
| 14 | No internal link 404s (every `href` starting `/` resolves in `dist/`) | whole site |
| 15 | `robots.txt` exists, allows `/`, disallows `/admin/`, references sitemap | root |
| 16 | Brand string is consistent (no legacy brand left in titles) | every page |
| 17 | Every `<img>` has non-empty `alt` (or explicit `alt=""` for decorative) | every page |
| 18 | Generated cluster pages pass `seo_quality_ok()` before being indexable | car-rental, itineraries |

## Content quality gate — `seo_quality_ok()`

A generated page may be **indexable + in the sitemap** only if it satisfies its type's minimum:

| Page type | Minimum data |
|---|---|
| Location (`/car-rental/{place}/`) | coordinates + ≥ 2 linked routes + ≥ 1 recommended category + ≥ 400 chars of location-specific text |
| Category (`/car-rental/{cat}/`) | ≥ 2 real vehicles with real prices + ≥ 1 linked route + limitations text |
| Itinerary (`/itineraries/…`) | ≥ 3 day rows, each with destination + km + drive time; total km; total drive time; recommended vehicle; ≥ 5 linked attractions |
| Route | days, distance_km, drive_time_total, ≥ 3 waypoints |

Pages that fail the gate are rendered as `noindex` and excluded from sitemaps — they never enter the index as thin content.

## Manual validation checklist (per release)

- [ ] `python build.py --validate-only`
- [ ] `python build.py dist`
- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/seo_audit.py dist` → 0 errors
- [ ] Spot-check 3 pages with JavaScript disabled — headings, prices, route data visible
- [ ] Google Rich Results Test on: home, vehicle, route, attraction, car-rental hub
- [ ] Lighthouse mobile on the 8 representative templates (Release D)
- [ ] Confirm no new URL breaks an existing indexed URL

## Results log

| Date | Release | Before | After | Issue | Fix | Test | Status |
|---|---|---|---|---|---|---|---|
| 2026-08-29 | Baseline | — | — | Audit only, no changes | — | — | ✅ documented |
| 2026-08-29 | A — Technical foundation | `meta keywords` on 2 130 pages; single flat sitemap; no canonical/hreflang audit | keywords removed; sitemap index + 8 children; canonical + 6-lang hreflang + x-default on every page | Flat sitemap would exceed limits as the cluster grows | `sitemap_index()` + `sitemap_children()` in `build.py` | `scripts/seo_audit.py dist` | ✅ 0 errors |
| 2026-08-29 | B — Car-rental cluster | no commercial landing pages | `/car-rental/` hub + 6 locations + 4 categories × 6 languages (66 URLs) | `KeyError: 'business'` in `car_cat_label` | fall back to the fleet category label | `tests.test_seo` | ✅ pass |
| 2026-08-29 | C — Trip-planner cluster | planner had no crawlable content | `/trip-planner/` landing + `/itineraries/` hub + 5 itineraries × 6 languages (42 URLs) | `georgia-5-days` silently dropped — a rest day has `km: 0` | quality gate uses `is not None`, not truthiness | `tests.test_seo` | ✅ pass |
| 2026-08-29 | D — Performance & trust | Leaflet + booking bundles on every page; 530 KB logo | JS bundles gated per page; 19 KB logo; internal-link graph on attractions, routes and home | 616 title-length warnings in RTL languages | drop the ` | RentUp` suffix past 70 chars (245 remain, non-blocking) | `scripts/seo_audit.py dist` | ⚠️ 0 errors, warnings tracked |
| 2026-08-29 | D — NAP consistency | contact page published `+995 32 2 000 000`, `info@example.ge`, ID `4XXXXXXXX` and a visible "these details are placeholders" note in all 6 languages | real phone from `site.yml` everywhere; invented company-details table, fake email and the placeholder note removed | published data contradicted the JSON-LD `Organization` node | rewrite `content/pages/contact.yml` | `build.py --validate-only` | ✅ fixed |
| 2026-08-30 | E — Audit sweep (11 skills, 10 agents) | unknown | 20 review docs in `docs/seo/`, 6 shipping render bugs found | audits ran against `dist/`, not assumptions | `docs/seo/*_REVIEW.md`, `AI_VISIBILITY.md`, `BROKEN_LINKS.md`, `TRANSLATION_QA.md` | `scripts/seo_audit.py` | ✅ documented |
| 2026-08-30 | E — Placeholder leaks | literal `{days} {km} {stops}` in 30 itinerary descriptions, `{place}` in a visible `<h2>` on 36 location pages | 0 leaked placeholders in any HTML page | `fill()` returned the raw template on `KeyError`; `su()` never formatted at all | `_Blanks`/`_fmt()`; `su(**fmt)`; pass `stops`/`start`/`end` | `grep -rl '{days}' dist --include=*.html` | ✅ 0 |
| 2026-08-30 | E — Georgian grammar | `ბათუმი-ში`, `მცხეთა-მთიანეთი-ში`, `ეკონომ კლასი-ის` on ~210 pages | correct `ბათუმში`, `მცხეთა-მთიანეთში`, `ეკონომ კლასის` | case suffixes were glued on with a hyphen in the templates | `ka_case()` + `{region_loc}`/`{name_gen}` placeholders, table-driven via `ka_forms.yml` | build + grep | ✅ 0 |
| 2026-08-30 | E — Title length | 257 titles over 70 chars (ka 96, ru 67, en 66) | 2 | the old guard only dropped the brand suffix | `_trim_title()` drops whole trailing clauses, never the entity name | `scripts/seo_audit.py dist` | ✅ 257 → 2 |
| 2026-08-30 | E — Dead asset | `/assets/analytics.js` linked on 2 125 pages, 404 live | linked only when the file exists | `ASSET` carried a default path for a file the build never wrote | `analytics_html()` returns `""` when unset | live fetch + grep | ✅ fixed |
| 2026-08-30 | E — Broken markup/links | `<div class="wrap"<div>` on 192 route pages; `#planner` on 6 home pages with no such anchor; `rentup.gehttps://…` og:image | valid markup, `/map/#planner`, absolute URLs preserved | missing `>`; fragment pointed at another page's anchor; `SITE_URL` prepended unconditionally | one-char fix; `page_url(lang,"map")+"#planner"`; new `abs_url()` | grep on `dist/` | ✅ 0 |
| 2026-08-30 | E — Truncated descriptions | route and region meta descriptions cut mid-sentence (~258 pages) | full hand-written descriptions | `_sd` was computed then discarded | `desc = _sd or …` | `scripts/seo_audit.py` | ✅ fixed |
| 2026-08-30 | E — Discarded copy | hand-written `meta_title`/`meta_description` for 60 car-rental pages never rendered | hand-written copy wins, template is the fallback | precedence was `template or hand-written`, and the template always returns a value | inverted at 3 call sites | build + spot-check | ✅ fixed |
| 2026-08-30 | E — Image credits | `photo_by` — a raw YAML key — printed as the caption label on 1 488 pages | localised “Photo/ფოტო/Фото/…” | the string lived in `planner.yml`, the lookup read `travel.yml` | added `photo_by` to `travel.yml → ui` in 6 languages | grep on `dist/` | ✅ 0 |
| 2026-08-30 | E — Fact base | 4 files published contradictory rental terms in 6 languages each; `org_desc` claimed “full insurance coverage” | one reconciled policy, sourced from the pre-existing published terms | `rental_policy.yml` was an assistant's proposal outranking real business content | reconciled `rental_policy.yml`, `meta.yml`, `seo_trust.yml`; 8 open questions listed for the owner | `docs/seo/FACT_RECONCILIATION.md` | ⚠️ needs owner sign-off |
| 2026-08-30 | E — Content restore | 27 attraction/route YAMLs missing from the working copy; 162 live URLs would have 404'd | restored from upstream `HEAD` | the local copy predated two upstream commits | `docs/seo/RESTORED_CONTENT.md` | `build.py --validate-only` | ✅ restored |
| 2026-08-30 | E — Link graph | attraction → pickup point 0/267, route → individual cars 0/49, itinerary → pickup 0/5; `/car-rental/tbilisi/` ranked 351/360 by PageRank | 267/267, 49/49, 5/5; `/car-rental/tbilisi/` now has 113 in-content inbound links | the commercial cluster was a leaf — everything linked out to it, nothing linked back | `nearest_rental_place()`, `pickup_link_block()`, cars-in-category block | link-graph count over `dist/` | ✅ fixed |
| 2026-08-30 | E — FAQ schema | 18 pages carried `FAQPage` while 2 112 rendered visible Q&A | 54 | `faq_node()` only understood the `PAGES` block format | `faq_items_node()` wired into hub, location, category and planner | `grep -rl FAQPage dist` | ✅ 18 → 54 |
| 2026-08-30 | E — llms.txt | `{attractions}` unsubstituted; listed the noindex `/planner/`; zero mentions of `/car-rental/`, `/itineraries/` or `/trip-planner/` | placeholders resolved, noindex pages excluded, all 11 commercial + 5 itinerary URLs listed | the file an AI assistant reads described a site that no longer exists | `llms_txt()` rewrite + `NOINDEX_PAGES` | `grep car-rental dist/llms.txt` | ✅ 0 → 18 |
| 2026-08-30 | E — Prose vs policy | landing copy stated fees, excess, insurance and age limits that contradicted the reconciled policy, in 6 languages | every figure matches `rental_policy.yml` and the published terms | the SEO copy predated the reconciliation | `docs/seo/PROSE_ALIGNMENT.md` | `seo_audit.py` + grep | ✅ aligned |
| 2026-08-30 | E — Raw enums in copy | `4x4_only`, bare `offroad`, quoted `'suv'` printed as English prose on the category pages | natural wording matching `categories.yml` | YAML identifiers were written straight into the copy | prose rewrite in 6 languages | `grep -r 4x4_only dist --include=*.html` | ✅ 0 |
| 2026-08-30 | F — Owner's answers | 8 policy questions open; 4 files disagreeing | prepayment, WiFi extra, max duration, 24/7 assistance, insurance wording, USD rate and young-driver surcharge all settled and applied in 6 languages | the reconciliation could not be finished without the business | `docs/seo/PAGES_ALIGNMENT.md` | `tests.test_content_quality` | ✅ applied |
| 2026-08-30 | F — Live USD rate | `usd_rate: 2.6` hard-coded in `site.yml`; `pricing.yml` said 2.70 | fetched from the National Bank of Georgia at build time, cached, with a sanity band and offline fallback | a typed rate goes stale and two files disagreed | `_load_usd_rate()`, `SKIP_NBG` escape hatch | `python3 -c "import build; print(build.USD)"` | ✅ live |
| 2026-08-30 | F — Policy is now real | `RENTAL_POLICY` was loaded by `build.py` and read by nothing | a visible terms table on the car-rental hub, in 6 languages, driven entirely by `rental_policy.yml` | the owner's single source of truth drove no page | `policy_facts()` / `policy_table_html()` | build + spot-check | ✅ wired |
| 2026-08-30 | F — Live 404s | `/attractions/`, `/routes/`, `/regions/` indexed live but never generated — 18 hard 404s | three real index hubs with the road/car/season data as browsable tables | the URLs existed only in the sitemap | `render_attractions_hub()` and siblings | `ls dist/attractions/index.html` | ✅ fixed |
| 2026-08-30 | F — Click depth | in-content depth histogram `{1:20, 2:84, 3:132, 4:88, 5:26}` — 114 pages 4–5 clicks deep | `{1:23, 2:362}` — **every** indexable page within 2 clicks, 0 unreachable | the only path to a place page was a JavaScript map | index hubs + a crawlable cluster index on the home page | BFS over `dist/` | ✅ 114 → 0 |
| 2026-08-30 | F — Guides cluster | nothing answered the pre-purchase question ("do I need a 4×4?") — 0 occurrences sitewide | `/guides/` + 3 data-built guides × 6 languages, 318 inbound links in the EN tree alone | the road/car dataset was the site's unique asset and was published nowhere as prose | `render_guide()`, `guides_for_place()` | `seo_audit.py` | ✅ 24 new pages |
| 2026-08-30 | F — Missing categories | `business` and `van` had real cars and real prices but no landing page | all 6 fleet categories have one | the category list was hard-coded in 4 places | `SEO_CATEGORY_ORDER` | build | ✅ +12 pages |
| 2026-08-30 | F — Attraction schema | road, required vehicle, drive time and season were visible but not machine-readable | `additionalProperty` on every attraction page (1 602 pages) | the dataset no competitor has was invisible to answer engines | `TouristAttraction.additionalProperty` | JSON-LD spot-check | ✅ added |
| 2026-08-30 | F — Fabricated stock | `availability: InStock` on 102 car pages with no stock field in the data | removed; replaced by a real `AggregateOffer` over the three published price tiers | invented availability is a manual-action risk | `car_node()` | `grep InStock dist` → 0 | ✅ fixed |
| 2026-08-30 | F — robots.txt | `Host:` (retired 2018); personal pages crawlable; 20 AI agents allowed | `Host:` dropped, `/account/ /trip/ /app/` disallowed, 22 AI agents allowed, noindex aliases left crawlable so their canonicals still count | crawl budget on 2 346 pages | `robots()` | `python3 -c "import build; print(build.robots())"` | ✅ tightened |
| 2026-08-30 | F — Stale guard | `test_booking_copy_does_not_deny_online_requests` enforced the opposite of the real policy | rewritten to check both directions against `rental_policy.yml` | the owner confirmed there is no online payment, so the test was enforcing a false fact | `tests/test_content_quality.py` | `unittest` | ✅ rewritten |
| 2026-08-30 | F — Image licensing | 994 photos carried author, licence and source in YAML and rendered the credit visibly, but published no rights metadata | `ImageObject` with `license`, `acquireLicensePage`, `creditText` and `author` on every fully-credited photo | this is the one Google rich result the site qualifies for outright | `image_object()` | JSON-LD spot-check | ✅ added |
| 2026-08-30 | F — Empty anchors | 28.2% of in-content links (1 306) were image links duplicating the card's text link | 0 undeclared — the duplicates are marked `aria-hidden`/`tabindex=-1`, as two templates already did | a screen reader and a crawler both saw two links per card | consistent decorative marking | anchor scan of `dist/` | ✅ 0 |
| 2026-08-30 | F — Sitemap lastmod | every URL carried one identical date in production (`actions/checkout` resets mtimes) | real per-file dates from `git log` | an unchanging lastmod tells a crawler nothing | `_git_commit_dates()` with an mtime fallback | `grep lastmod dist/sitemaps/*.xml \| sort -u` | ✅ varied |
| 2026-08-30 | G — Head weight | home page `</head>` at **60 578 bytes**, 57 KB of it pretty-printed JSON-LD ahead of the stylesheet | **9 577 bytes** (-84%); every template similar | `indent=2` on machine-read markup, plus an unbounded `ItemList` of all 267 attractions that grew with the content | compact `JC()` for JSON-LD; the home `ItemList` now points at the regions and the new `/attractions/` hub | byte offset of `</head>` in `dist/` | ✅ 60.6 KB → 9.6 KB |
| 2026-08-30 | G — Organization logo | no `logo` on the `Organization` node; the only asset was 180×72, under Google's 112 px minimum | 540×540 logo derived from the header mark, declared with width and height | a missing logo blocks the knowledge-panel and several rich results | `static/rentup-logo-square.png` | JSON-LD spot-check | ✅ added |
| 2026-08-30 | G — Inverted price band | `priceRange` published as `104-88 GEL` | `56-330 GEL` | prices are strings in the YAML, so `min`/`max` compared them as text and `"104"` sorted below `"88"` | `_num()` coercion; the same latent bug fixed in the car `AggregateOffer` | `python3 -c "import build; print(build.org_node('en')['priceRange'])"` | ✅ fixed |

_(rows appended per release)_
