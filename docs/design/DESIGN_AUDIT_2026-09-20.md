# rentup.ge — design audit and rework

_2026-09-20. Audited with three skills installed for this pass: **ui-ux-pro-max**
(119 UX guidelines, 192 palettes, stack data), **Anthropic frontend-design**
(aesthetic direction and typography), and **design-audit** (six-category review
with severity scoring, `marketing-site` profile). Evidence: Playwright captures
of the live site at 1440×900 and 390×844 across `/`, `/car-rental/`, `/fleet/`,
`/guides/…`, `/day-trip/` and `/ka/`._

**Context profile:** marketing site — car rental, conversion-focused, no
authenticated state, six languages including three RTL. Primary user task:
decide whether these cars fit the trip, then start a booking.

**Overall.** The content work of the previous waves landed: the facts are real,
the terms are consistent and the road data is genuinely unique. The *design* had
not kept up with it. Every page had become a column of prose, the product itself
was never shown, and the first screen asked the visitor for nothing.

---

## Findings

| # | Severity | Category | Finding | Status |
|---|---|---|---|---|
| 1 | 🔴 Critical | Marketing / CTA | Hero had **no call to action** at any viewport. The first screen of a rental site asked for nothing. | **fixed** |
| 2 | 🔴 Critical | Visual / UI patterns | **0 of 17 cars carry a photograph.** Fleet cards opened on a grey box; in Georgian the box printed `"<model> — ფოტო"`, a placeholder shipped to production. | **mitigated** — see below |
| 3 | 🔴 Critical | Trust / UX copy | Home advertised **"5000+ travellers"** (no source anywhere in the repo) and **"3.9 average rating"** — which is the mean *attraction* rating, relabelled as a customer score. Invented social proof, and unflattering. | **fixed** |
| 4 | 🟠 Major | Layout / responsive | At 390px the hero headline and lead were **clipped by the photo** and the nav row ran off-screen. | **fixed** |
| 5 | 🟠 Major | IA / UI patterns | `linklist` had **no CSS at all** — 17 blocks sitewide ("Browse places", "Pickup locations", "Guides") rendered as raw browser bullets, reading as a sitemap dump. | **fixed** |
| 6 | 🟠 Major | Visual hierarchy | `/car-rental/` stacked **twelve identical heading + paragraph sections** on alternating backgrounds. Alternation does not create scannability; it only made the page 6 555px long. | **fixed** |
| 7 | 🟠 Major | UX heuristics | **"How booking works" rendered as a bare heading.** The section holds `steps`, the renderer only read `body` — so the one block explaining how to actually rent a car had been invisible. | **fixed** |
| 8 | 🟡 Minor | Typography | Base font **15px**, below the 16px floor for body text on a content-heavy site. | **fixed** |
| 9 | 🟡 Minor | Accessibility | Focus rings existed only on `<a>`; buttons, `summary` and inputs had none. Touch targets below 44×44. No `prefers-reduced-motion`. | **fixed** |

### On finding 2 — the one I cannot close in code

A car rental site sells on photographs, and there are none. I will not download
stock images of other people's cars and present them as this fleet. What the
build does now is stop pretending: the slot draws the vehicle class on a branded
plate, holds the exact 16:10 box the real photo will occupy (so nothing shifts
when the pictures arrive) and never prints a placeholder string at a customer.

**Seventeen photographs is the single highest-return piece of work left on this
site** — higher than any further SEO. Three-quarter front, same angle, same
light, one per car.

---

## What changed in the build

**`theme.py`** — each block is named after the finding it closes, so the next
person knows why it exists.

- `ul.linklist` → a 248px-minimum auto-fill grid of 44px-tall link cards with a
  chevron affordance, collapsing to one column under 760px (F-5).
- `.car-plate` → the class plate described above (F-2).
- `.land-hero-cta` → primary + secondary action in the hero. The copy block is
  `pointer-events:none`, so the buttons take their own `pointer-events` back;
  without that they would have been decorative (F-1).
- Mobile hero: the copy is a *child* of the photo box, so the fix is not an
  opaque background — that hides the photo. The image becomes a band of
  `min(210px,30vh)` and the copy takes the space under it (F-4).
- `.prose-grid` → the ten reference topics as one scannable card grid (F-6).
- `ol.steps` → real numerals for the booking sequence (F-7).
- `.act-bar` → a sticky primary action under 760px, with safe-area padding.
- `overflow-x:hidden` on the root, focus-visible on every focusable element,
  44px minimum targets, `prefers-reduced-motion` honoured (F-9).

**`content/settings/design.yml`** — `base_font_size` 15 → 16 (F-8).

**`build.py`**

- `landing_stats` strip: places, cars, **pickup points**, **24/7 support** —
  every number counted from the repository at build time (F-3).
- `car_plate()` used by `_car_card`, `cars_grid` and the car detail page (F-2).
- `render_car_rental_hub`: `intro` and `how_it_works` stay full width as the
  page's argument; the ten policy topics move into the grid. Sections whose
  body resolves to nothing are now skipped rather than printed as empty
  headings (F-6, F-7).

## Verification

2 424 pages build, SEO audit **0 ERROR**, all tests pass, and no horizontal
overflow at 390px or 1440px on `/`, `/fleet/` or `/car-rental/` — checked in
Chromium, including the Hebrew RTL tree.

## Still open

- **Photographs of the 17 cars** (owner).
- No date-range picker anywhere: the site explains renting rather than starting
  one. A two-field "pick-up / return" control on the hub is the next build.
- The four home cards are illustrations in a different visual register from the
  photographic hero — they read as stock art next to real Georgian landscape.
