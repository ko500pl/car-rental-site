# Prose Alignment Report — SEO Landing Pages vs. Reconciled Facts

Scope: `content/settings/seo_car_rental.yml` and `content/settings/seo_categories.yml`,
reconciled against `docs/seo/FACT_RECONCILIATION.md`, `content/settings/rental_policy.yml`,
and the published pages `content/pages/pricing.yml` / `terms.yml`. All 6 languages
(ka/en/ru/fa/he/ar) checked. Only the two files above and this report were written;
`build.py`, `rental_policy.yml`, and `content/pages/*` were not touched.

## 1. Numbers corrected

### `content/settings/seo_car_rental.yml`

| Field / location | Languages | Old value | New value | Source |
|---|---|---|---|---|
| Tbilisi airport delivery fee (hub `delivery`, Tbilisi-airport location page) | all 6 | 30 ₾ | 40 ₾ | FACT_RECONCILIATION conflict matrix; pricing.yml |
| Batumi airport delivery fee (hub `delivery`, Batumi-airport location page) | all 6 | 60 ₾ | 50 ₾ | pricing.yml (Kutaisi airport stays 60 ₾ — not changed) |
| Kutaisi/Batumi city delivery fee | all 6 | 50 ₾ | 40 ₾ | pricing.yml delivery table |
| Night surcharge amount | all 6 | 20 ₾ | 40 ₾ | rental_policy.yml / pricing.yml |
| Night surcharge window end | all 6 | 08:00 | 07:00 | rental_policy.yml |
| Excess / franchise (economy) | all 6 | flat 1000 ₾ | 300 ₾ | pricing.yml deposit/excess table |
| Excess / franchise (SUV) | all 6 | flat 1000 ₾ | 600 ₾ | pricing.yml |
| Excess / franchise (business/minivan) | all 6 | flat 1000 ₾ | 1000 ₾ (framing fixed, number unchanged) | pricing.yml |
| Excess / franchise (4x4/offroad) | all 6 | flat 1000 ₾ | 1200 ₾ | pricing.yml |
| Insurance add-on name and price | all 6 | "CDW" for 25 ₾/day (CDW framed as optional) | "SCDW" 25–45 ₾/day, reduces excess to zero; CDW itself is included in the base rate along with TPL | rental_policy.yml / terms.yml — CDW is standard, SCDW is the paid excess-reduction add-on |
| Additional driver fee | all 6 (hub `extras`) | 10 ₾/day | 20 ₾/day (max 2 drivers) | pricing.yml extras table |
| GPS navigator | all 6 (hub `extras`) | listed as "not offered" / 0 ₾ | 15 ₾/day, real paid extra | pricing.yml extras table |
| WiFi router | all 6 (hub `extras`) | 15 ₾/day | removed entirely (unsourced in pricing.yml) | — |
| Cross-border policy (hub `one_way`, hub FAQ, Batumi/Batumi-airport good_to_know) | all 6 | "not available" / "car stays inside Georgia" | Armenia 150 ₾, Turkey 250 ₾ (selected categories), 48h advance notice, 300 km/day | pricing.yml, terms.yml cross-border table |
| Cancellation free window | all 6 (hub `cancellation`, hub FAQ) | free until 24h before pickup | free until 48h before pickup; new 24–48h middle tier charges one day's rate; <24h/no-show charges two days' rate | terms.yml cancellation tiers |
| Young-driver surcharge (hub `requirements`) | all 6 | claimed no surcharge exists | economy: none; higher categories: 15–25 ₾/day for drivers under 27 | terms.yml age/licence and young-driver-surcharge tables |

### `content/settings/seo_categories.yml`

All 24 `terms_note` blocks (4 categories × 6 languages) shared the same two defects and were rewritten:

| Category | Field | Old | New | Source |
|---|---|---|---|---|
| economy (all 6 langs) | excess/insurance framing | "TPL included; standard excess without CDW 1000 ₾; CDW optional 25 ₾/day" | "TPL and CDW both included; excess 300 ₾; SCDW optional 25–45 ₾/day, reduces excess to zero" | terms.yml, pricing.yml |
| economy (all 6 langs) | driver age/licence | 21y / 2yr | 21y / 2yr (unchanged — already correct for this category) | terms.yml age tier table |
| suv (all 6 langs) | excess/insurance framing | same generic 1000 ₾/CDW wording | excess 600 ₾; SCDW 25–45 ₾/day | terms.yml, pricing.yml |
| suv (all 6 langs) | driver age/licence | 21y / 2yr (wrong for this category) | 23y / 3yr | terms.yml age tier table |
| offroad/4x4 (all 6 langs) | excess/insurance framing | same generic 1000 ₾/CDW wording | excess 1200 ₾; SCDW 25–45 ₾/day | terms.yml, pricing.yml |
| offroad/4x4 (all 6 langs) | driver age/licence | 21y / 2yr (wrong for this category) | 25y / 4yr | terms.yml age tier table |
| minivan (all 6 langs) | excess/insurance framing | "excess without CDW 1000 ₾; CDW optional 25 ₾/day" | "CDW included; excess 1000 ₾ (number unchanged); SCDW optional 25–45 ₾/day" | terms.yml, pricing.yml |
| minivan (all 6 langs) | driver age/licence | 21y / 2yr (wrong for this category) | 23y / 3yr | terms.yml age tier table |

Note: the age/licence error (flat 21y/2yr stated for every category) was not in the original
task brief — it was discovered while auditing the `terms_note` blocks for the excess/CDW fix,
since both errors lived in the same sentences. Corrected using terms.yml's per-category tiers:
economy 21y/2yr, SUV & minivan 23y/3yr, business & 4x4/offroad 25y/4yr.

Category deposit amounts (300/600/1200/1000 ₾) and `price_from_gel` fleet-pricing figures
(75/130/240/200 ₾) in `seo_categories.yml` were already correct and were left untouched — they
are unrelated to the insurance/excess/age reconciliation.

## 2. Claims removed (no replacement invented)

- WiFi router as a paid extra (15 ₾/day) — no source for this figure or offering in
  pricing.yml/terms.yml; deleted from the hub `extras` section rather than guessing a price.
- False comparative claims that became incorrect as a side effect of the airport-fee fix
  (e.g. "Batumi airport delivery is the same as Kutaisi's," "double the Tbilisi rate") were
  removed and replaced with each city's actual, distinct fee instead of a now-broken equality.
- "The car cannot cross into Turkey / stays inside Georgia" (Batumi and Batumi-airport
  `good_to_know`) — replaced with the real, sourced policy (Turkey crossing possible, 250 ₾,
  48h notice, selected categories) since it was factually false, not merely outdated.

## 3. Raw YAML token / internal-tag leaks fixed

| File | Token | Occurrences | Fix |
|---|---|---|---|
| seo_categories.yml | `4x4_only` in prose | 15 | Rewritten as natural `4x4-only` (hyphenated adjective) in EN prose; the one legitimate data-field list item (`road_types: - 4x4_only`, line 810) was left untouched |
| seo_categories.yml | bare `offroad` in prose | 6 (ka/en/ru × 2 locations) | Replaced with human labels from `categories.yml`: ka "მაღალი გამავლობის 4x4", en "Off-road 4x4", ru "«Внедорожник 4x4»" |
| seo_categories.yml | quoted `'suv'` as an internal tag reference in FAQ answers | 4 (en/ru/fa/he) | Reworded as natural language, e.g. "gravel roads suited to an SUV" instead of "rated ''suv'' in our route data" |
| seo_car_rental.yml | bare `offroad` in prose (Kutaisi page, en + ka) | 2 | Replaced with "Off-road 4x4 category" / "მაღალი გამავლობის 4x4 კატეგორია" |

`road_types:` and `car_category:` YAML keys/list items elsewhere in both files are legitimate
structured data (not prose) and were left untouched.

## 4. Georgian-specific fixes (per `docs/seo/TRANSLATION_QA.md`)

- **Hyphen-glued case suffixes** (e.g. "ბათუმი-ში"): scanned both files with a targeted regex
  for Georgian-script + hyphen + case-suffix patterns. **None found** in `seo_car_rental.yml` or
  `seo_categories.yml` — the only defect of this shape is a legitimate numeral hyphen ("195
  მმ-ის"). This defect is confined to `seo_meta.yml`/`seo_ui.yml`, which are out of scope for
  this task. No changes made for this item; documented here as checked.
- **ქირაობა retirement / გაქირავება vs დაქირავება split**: all instances of ქირაობა in
  `seo_car_rental.yml` were retired (verified via final `grep -n "ქირაობ"` returning empty in
  both files). Company-voice titles/H1s (6 location `meta_title`s plus the hub `meta_title`)
  standardized on გაქირავება ("მანქანის ქირაობა {X}" → "მანქანის გაქირავება {X}"). Countable-noun
  instances were replaced with ჯავშანი ("booking") or a concrete noun (მანქანა, "car") per
  TRANSLATION_QA.md's exact terminology table, since ქირაობა is an uncountable verbal noun that
  cannot stand in for a countable event. A garbled/direction-reversed sentence in the Tbilisi
  `good_to_know` ("თუ თბილისში ქირაობას აბრუნებთ ბათუმიდან...") was also corrected to
  "თუ თბილისში აღებულ მანქანას აბრუნებთ ბათუმში ან ქუთაისში გასვლის წინ...".

## 5. Verification

- `python3 build.py --validate-only` → `✔ content validation passed` (one pre-existing,
  unrelated warning: 17 car records with no main image).
  - Fixed along the way: two YAML scanner errors in `seo_car_rental.yml` (Hebrew and Arabic
    Batumi `good_to_know` entries) caused by an unescaped `": "` (colon+space) inside a plain
    scalar — introduced while drafting the Turkey cross-border replacement text. Reworded both
    sentences to avoid the mid-scalar colon; both now parse cleanly.
- `python3 build.py /tmp/pa` → `✔ 2292 HTML pages (17 cars, 4 articles, 6 languages)`.
- `python3 scripts/seo_audit.py /tmp/pa` → **0 ERROR**, 2 WARN (pre-existing, unrelated:
  `/ka/trip-planner/` and `/ru/trip-planner/` title length), 20 INFO (pre-existing noindex-page
  notices).
- Grep of the entire built `/tmp/pa` tree for `4x4_only` → **zero HTML files match** (only
  JS asset bundles, itinerary JSON data files, and `admin/config.yml` contain it, all outside
  this task's two source files). Grep for `car_category`/`best_season`/`ქირაობ` → present only
  in itinerary pages (built from a different, out-of-scope content source), zero occurrences
  in any `/car-rental/*` page generated from `seo_car_rental.yml`/`seo_categories.yml`.

## Summary (10 lines)

1. Reconciled every commercial figure in `seo_car_rental.yml` and `seo_categories.yml` (6 languages) against `FACT_RECONCILIATION.md`, `rental_policy.yml`, `pricing.yml`, `terms.yml`.
2. Fixed airport/city delivery fees (Tbilisi 30→40 ₾, Batumi airport 60→50 ₾, Kutaisi/Batumi city 50→40 ₾), night surcharge (20→40 ₾, window to 07:00), and cascading comparative claims that broke as a result.
3. Corrected insurance framing everywhere: CDW is included (not a paid add-on); SCDW is the real paid add-on at 25–45 ₾/day; excess now varies by category (300/600/1000/1200 ₾) instead of a flat 1000 ₾.
4. Fixed extras: additional driver 10→20 ₾/day; added GPS as a real 15 ₾/day extra; removed the unsourced 15 ₾/day WiFi router claim entirely rather than inventing a source.
5. Replaced the false "no cross-border travel" claims with the real policy (Armenia 150 ₾, Turkey 250 ₾ selected categories, 48h notice) across the hub and Batumi-area pages.
6. Fixed cancellation terms (free window 24→48h, added the 24–48h and no-show tiers) and added the real young-driver surcharge (15–25 ₾/day for under-27 in non-economy categories).
7. In `seo_categories.yml`, discovered and fixed a second latent bug while correcting the 24 `terms_note` blocks: every category wrongly stated a flat 21y/2yr driver-age minimum; corrected to the real per-category tiers (23y/3yr for SUV/minivan, 25y/4yr for 4x4).
8. Removed raw YAML tokens leaked into prose (`4x4_only`, bare `offroad`, quoted `'suv'`) and replaced with natural human-facing labels matching `categories.yml`.
9. Confirmed no hyphen-glued Georgian case-suffix defects exist in either file (checked, not found); retired all instances of ქირაობა in favor of გაქირავება (company voice) / დაქირავება / ჯავშანი / მანქანა per TRANSLATION_QA.md.
10. Verified: `build.py --validate-only` passes (after fixing two YAML scalar colon errors introduced mid-edit), full build produces 2292 pages, `seo_audit.py` reports 0 ERROR, and no raw enum token survives in any built `/car-rental/*` HTML page.
