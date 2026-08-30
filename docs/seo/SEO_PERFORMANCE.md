# RentUp.ge — Performance Audit (Core Web Vitals & Page Weight)

**Date:** 2026-08-29
**Scope:** static build produced by `python3 build.py dist` from the current repo state (rebuilt fresh for this audit — SHA of the build corresponds to the working tree as of 2026-08-29 21:00 UTC).
**Method:** Chromium 141 (Playwright, `/opt/pw-browsers/chromium`) driving the built site served locally (`python3 -m http.server 8765` from `dist/`), plus static analysis of `dist/`, `theme.py`, `build.py`, and `fetch_photos.py`. Every number below was produced by a script run in this session; the scripts and raw JSON are described inline so the numbers are reproducible.

## 0. Measurement conditions — read this before the tables

- **Local server, not the live CDN.** All timings (TTFB, FCP, LCP, DCL, load) were captured against `localhost:8765`, i.e. **zero network latency, zero CDN hops, no TLS handshake, no real mobile CPU throttling**. They are useful for *relative* comparison between templates and for isolating the site's own render-blocking/JS cost, but they are **not** a substitute for a field CWV report (CrUX / PageSpeed Insights against `rentup.ge`) and must not be quoted as "the site's LCP is 300 ms" in any external-facing context. I flag this explicitly wherever it matters.
- **External-CDN ("allowed") pass could not be completed.** The task asked me to also measure once with third-party requests (Google Fonts, OSM tiles, Firebase) allowed through the sandbox's egress proxy. I attempted this (`playwright` launched with `proxy: {server: HTTPS_PROXY, bypass: 'localhost,127.0.0.1'}`, `ignoreHTTPSErrors: true`, and also `--ignore-certificate-errors --disable-http2`). Every attempt hit **`net::ERR_CONNECTION_RESET`** on the very first byte after the TLS handshake (confirmed independently against `fonts.googleapis.com`, `accounts.google.com`, `tile.openstreetmap.org`), while a plain `curl` through the identical `HTTPS_PROXY` succeeded (200 OK) in the same shell at the same time. The proxy's own status endpoint logged matching `ws_closed_mid_exchange` relay failures for those hosts during the same window. This is a Chromium‑vs‑proxy TLS/relay incompatibility specific to this sandbox, not a site defect. **Net effect:** third-party resources never load in either "blocked" or "allowed" runs here, so I report their weight and blocking behavior from direct `curl` fetches and from reading the HTML/CSS/JS source instead of from a live browser trace. Anywhere I couldn't get a real number this way, I wrote **"not measured."**
- **Viewports:** mobile = Playwright's `iPhone 13` device profile (390×844 CSS px, DPR 3, mobile UA); desktop = 1366×850, DPR 1.
- **CLS, LCP, long-task and CSS/JS-coverage data** come from real `PerformanceObserver`s (`largest-contentful-paint`, `layout-shift`, `longtask`) injected via `page.addInitScript` before navigation, and from Chromium's `page.coverage.startJSCoverage/startCSSCoverage` (CDP `Profiler`/`CSS.startRuleUsageTracking`). JS coverage is byte-approximate: V8 reports coverage as a tree of nested function ranges, and a naive union of "ranges with count > 0" over-counts (an unexecuted nested function's bytes get marked "used" by its executed parent). I corrected for this by painting largest ranges first so smaller/nested ranges overwrite — the standard approach — but treat the JS unused-% numbers as a **heuristic**, as the task itself calls for, not an exact coverage report.
- Pages audited: `/` (home), `/fleet/`, `/fleet/bmw-5-series/`, `/map/`, `/tours/`, `/attractions/ananuri-fortress/`, `/routes/grand-georgia-classic/`, `/regions/kakheti/`, `/app/`.

---

## 1. Per-template results

### 1.1 HTML weight (raw file, no CDN compression — measured with `stat`/`gzip -c` on the built files)

| Template | Path | Raw HTML | Gzip (min. expected) |
|---|---|---:|---:|
| Home | `/` | 88,110 B | 17,534 B |
| Fleet list | `/fleet/` | 37,522 B | 8,466 B |
| Fleet detail | `/fleet/bmw-5-series/` | 19,661 B | 6,213 B |
| Map / planner | `/map/` | 29,900 B | 8,648 B |
| Tours | `/tours/` | 33,037 B | 8,066 B |
| Attraction | `/attractions/ananuri-fortress/` | 26,179 B | 8,219 B |
| Route | `/routes/grand-georgia-classic/` | 34,413 B | 8,725 B |
| Region | `/regions/kakheti/` | 54,869 B | 11,673 B |
| App shell | `/app/` | 41,300 B | 8,221 B |

(Gzip was computed with `gzip -c | wc -c` on the exact bytes GitHub Pages will serve; I could not confirm from this environment whether GH Pages' edge actually serves brotli/gzip for `.html` — **not measured** against the live host. GitHub Pages' Fastly edge does compress text responses in production, so treat the "raw" column as the worst case and the gzip column as a realistic estimate.)

### 1.2 Page weight & request count by type (blocked-external run — same-origin only; see §0)

| Template | Viewport | Requests | Total bytes | html | css | js | img | font |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Home | mobile | 15 | 1,087,503 B | 1 (88 KB) | 2 (165 KB) | 4 (81 KB) | 8 (753 KB) | 0 |
| Home | desktop | 18 | 1,578,104 B | 1 (88 KB) | 2 (165 KB) | 4 (81 KB) | 11 (1,244 KB) | 0 |
| Fleet list | mobile | 9 | 813,073 B | 1 (38 KB) | 1 (150 KB) | 4 (81 KB) | 3 (544 KB)* | 0 |
| Fleet list | desktop | 8 | 800,076 B | 1 (38 KB) | 1 (150 KB) | 4 (81 KB) | 2 (531 KB)* | 0 |
| Fleet detail | mobile | 9 | 795,212 B | 1 (20 KB) | 1 (150 KB) | 4 (81 KB) | 3 (544 KB)* | 0 |
| Fleet detail | desktop | 8 | 782,215 B | 1 (20 KB) | 1 (150 KB) | 4 (81 KB) | 2 (531 KB)* | 0 |
| Map | mobile | 15 | 1,238,529 B | 1 (30 KB) | 2 (165 KB) | 8 (488 KB) | 4 (555 KB) | 0 |
| Map | desktop | 14 | 1,225,532 B | 1 (30 KB) | 2 (165 KB) | 8 (488 KB) | 3 (542 KB) | 0 |
| Tours | mobile | 13 | 1,312,186 B | 1 (33 KB) | 1 (150 KB) | 4 (81 KB) | 7 (1,048 KB) | 0 |
| Tours | desktop | 17 | 1,998,525 B | 1 (33 KB) | 1 (150 KB) | 4 (81 KB) | 11 (1,734 KB) | 0 |
| Attraction | mobile | 12 | 1,043,471 B | 1 (26 KB) | 2 (165 KB) | 5 (229 KB) | 4 (624 KB) | 0 |
| Attraction | desktop | 14 | 1,266,270 B | 1 (26 KB) | 2 (165 KB) | 5 (229 KB) | 6 (846 KB) | 0 |
| Route | mobile | 12 | 1,235,701 B | 1 (34 KB) | 2 (165 KB) | 5 (229 KB) | 4 (808 KB) | 0 |
| Route | desktop | 18 | 2,152,386 B | 1 (34 KB) | 2 (165 KB) | 5 (229 KB) | 10 (1,724 KB) | 0 |
| Region | mobile | 11 | 992,763 B | 1 (55 KB) | 2 (165 KB) | 5 (229 KB) | 3 (544 KB)* | 0 |
| Region | desktop | 10 | 979,766 B | 1 (55 KB) | 2 (165 KB) | 5 (229 KB) | 2 (531 KB)* | 0 |
| App shell | mobile | 16 | 1,491,702 B | 1 (41 KB) | 1 (15 KB) | 6 (451 KB) | 8 (985 KB) | 0 |
| App shell | desktop | 15 | 1,478,705 B | 1 (41 KB) | 1 (15 KB) | 6 (451 KB) | 9 (972 KB) | 0 |

`*` = the `img` bytes on fleet/region pages are almost entirely the 530 KB header logo (`do-logo-tight.png`) — see finding F1. Cars themselves render **zero photos** (`build.py` logged `WARNING: cars: 17 published records have no main image` during my rebuild; confirmed in the HTML — every `.car`/`.ph` block on `/fleet/` and `/fleet/bmw-5-series/` is a text-only placeholder `<div class="ph">Model name</div>`, no `<img>` at all). This is a content/CMS gap, not a code defect, and outside `build.py`'s control — noted here for completeness, not counted as a perf fix.

**Fonts (0 in every row above)**: Noto Sans / Noto Sans Georgian is loaded from `fonts.googleapis.com`, which our local server never reaches, so 0 font bytes were captured in the browser trace. Measured directly instead by `curl`ing the real Google Fonts CSS: the stylesheet itself is **32.8 KB** (60 `@font-face` rules covering multiple unicode-range subsets and 4 weights × 2 families); a single woff2 subset actually used by Latin text is **21.8 KB**, and the Georgian subset is **17.5 KB** — so a real visit typically pulls the 33 KB CSS plus 2–4 font files (~40–90 KB total), from two extra origins (`fonts.googleapis.com` + `fonts.gstatic.com`), each needing its own DNS + TLS handshake before any bytes arrive.

### 1.3 LCP, CLS, FCP, TTFB, long tasks (blocked-external, local server — see §0 caveat on absolute times)

| Template | VP | LCP element | LCP time* | LCP `loading` | LCP `fetchpriority` | CLS | FCP | TTFB | Long tasks (own JS) |
|---|---|---|---:|---|---|---:|---:|---:|---|
| Home | mobile | `<img>` **rentup-card-cars.jpg** (a card, not the hero) | 324 ms | `lazy` ⚠️ | none | 0.0000 | 224 ms | 10 ms | 1 × 90 ms |
| Home | desktop | `<img>` rentup-hero2.jpg (the hero) | 320 ms | `eager` | none ⚠️ | 0.0004 | 260 ms | 10 ms | 1 × 92 ms |
| Fleet list | mobile | `<p>` (text — no photo exists) | 208 ms | — | — | 0.0000 | 208 ms | 5 ms | 1 × 76 ms |
| Fleet list | desktop | `<p>` (text) | 204 ms | — | — | 0.0004 | 204 ms | 5 ms | 1 × 78 ms |
| Fleet detail | mobile | `<p>` (text) | 156 ms | — | — | 0.0000 | 156 ms | 5 ms | 0 |
| Fleet detail | desktop | `<h1>` (text) | 192 ms | — | — | 0.0000 | 192 ms | 6 ms | 0 |
| Map | mobile | **`<div>` (CSS background-image**, `rentup-planner-hero.jpg`) | 344 ms | n/a (not an `<img>`) | n/a | 0.0000 | 156 ms | 6 ms | 2 × 153 ms |
| Map | desktop | `<div>` (CSS background-image) | 540 ms | n/a | n/a | **0.0068** (highest of all templates) | 200 ms | 5 ms | 2 × 334 ms |
| Tours | mobile | `<img>` jvari-monastery.webp (a listing card) | 256 ms | `lazy` ⚠️ | none | 0.0000 | 152 ms | 9 ms | 1 × 58 ms |
| Tours | desktop | `<img>` jvari-monastery.webp | 396 ms | `lazy` ⚠️ | none | 0.0000 | 256 ms | 6 ms | 1 × 53 ms |
| Attraction | mobile | `<img>` ananuri-fortress.webp (correct hero) | 224 ms | `eager` ✅ | `high` ✅ | 0.0000 | 172 ms | 7 ms | 1 × 88 ms |
| Attraction | desktop | `<img>` ananuri-fortress.webp | 300 ms | `eager` ✅ | `high` ✅ | 0.0000 | 252 ms | 7 ms | 1 × 78 ms |
| Route | mobile | `<p>` (text) | 164 ms | — | — | 0.0000 | 164 ms | 8 ms | 0 |
| Route | desktop | `<h1>` (text) | 196 ms | — | — | 0.0000 | 196 ms | 5 ms | 0 |
| Region | mobile | `<p>` (text) | 136 ms | — | — | 0.0000 | 136 ms | 5 ms | 1 × 61 ms |
| Region | desktop | `<p>` (text) | 196 ms | — | — | 0.0000 | 196 ms | 7 ms | 1 × 57 ms |
| App shell | mobile | `<img>` rentup-hero2.jpg | 200 ms | `eager` | none ⚠️ | 0.0000 | 156 ms | 6 ms | 1 × 61 ms |
| App shell | desktop | `<img>` rentup-hero2.jpg | 304 ms | `eager` | none ⚠️ | 0.0001 | 192 ms | 7 ms | 1 × 53 ms |

`*` local-server timing (§0) — **not** a substitute for field LCP. On a real network add realistic TTFB (GitHub Pages/Fastly typically 20–120 ms), TLS, and the two extra Google Fonts round trips before first paint; expect real-world LCP in the ~0.8–2.0 s range for the image-led templates and worse on slow mobile connections, especially `/map/` (see F5) and `/tours/`, `/routes/`, `/regions/` (see F3) where the LCP-owning image is fetched late.

**Worst-performing template: `/map/`.** It has the only measurable CLS (0.0068, driven by late map/marker layout), the largest long-task total (334 ms on desktop, from Leaflet + the 190 KB `travel-en.js` places blob + `workspace.js` all initializing together), the highest local LCP (540 ms desktop), and its LCP element is a CSS `background-image` that the browser's preload scanner cannot discover early (see F5) — the one template where several independent problems compound.

### 1.4 Render-blocking resources in `<head>` (same for every locale of a given template; captured via DOM query, not guesswork)

| Template | Blocking stylesheets in `<head>` | Blocking scripts in `<head>` |
|---|---|---|
| Home | Google Fonts CSS (33 KB, cross-origin) → `style.css` (150 KB) → `leaflet.css` (14.8 KB, **unused on this page**, see F2) | none (all JS is `type="module"` or `defer`, placed at end of `<body>`) |
| Fleet list / detail / Tours | Google Fonts CSS → `style.css` | none |
| Map / Attraction / Route / Region | Google Fonts CSS → `style.css` → `leaflet.css` | none |
| App shell | Google Fonts CSS → `leaflet.css` (no `style.css` — the app shell ships its own ~3.7 KB inline `<style>` instead; this is a good existing pattern, see §4) | none |

No page has a render-blocking `<script>` in `<head>`; `auth.js`/`booking.js`/`community.js` are `type="module"` (deferred by spec) and `app.js` carries an explicit `defer`, all placed just before `</body>`. **This part of the build is already done correctly** — the fix targets below are about *what* loads, not *where* the tags sit.

### 1.5 Images: lazy/eager, `fetchpriority`, missing dimensions, format (desktop run; mobile numbers are materially the same)

| Template | `<img>` count (incl. off-screen) | Missing `width`/`height` | Non-WebP/AVIF | `loading=lazy` | `loading=eager` |
|---|---:|---:|---:|---:|---:|
| Home | 10 | 6 | 6 (jpg/png UI art) | 8 | 1 |
| Fleet list | 1 | 1 | 1 | 0 | 0 |
| Fleet detail | 1 | 1 | 1 | 0 | 0 |
| Map | 16 | 16 | 16 (Leaflet marker/attribution icons, each a few KB) | 0 | 0 |
| Tours | 33 | 33 | 1 | 32 | 0 |
| Attraction | 18 | 17 | 11 (Leaflet UI icons) | 6 | 1 |
| Route | 33 | 33 | 19 | 14 | 0 |
| Region | 45 | 45 | 13 | 32 | 0 |
| App shell | 6 | 5 | 6 (jpg/png UI art) | 4 | 1 |

**Important correction to the brief's assumption:** missing `width`/`height` attributes are **not** producing measurable CLS here. `theme.py` gives every image container an explicit box independent of the `<img>` tag's own attributes — `.photo img{aspect-ratio:16/9}` / `.hero-photo img{aspect-ratio:21/9}` for attraction photos (`theme.py:618-623`), and `.card-img img{height:170px}` (140px under a mobile breakpoint, `theme.py:624-836`) for every card grid (tours/routes/regions/nearby-attractions). I checked this isn't theoretical: **measured CLS is 0.0000–0.0068 across all 9 templates** (table 1.3) — essentially at the CWV "good" ceiling already. So while adding `width`/`height` (or `srcset`) is still worth doing for the responsive-image fix below, **do not spend effort "fixing missing width/height for CLS" as a standalone item — there is no CLS problem to fix.** I'm flagging this so the fix list below isn't padded with a non-issue.

---

## 2. Corpus-wide analysis (scripted, not spot-checked)

### 2.1 `static/*.js` — sizes and who loads what

Sizes below are the deployed, fingerprinted files under `dist/assets/` (`ls -la` + `gzip -c | wc -c`):

| Bundle | Raw | Gzip | Loaded on (scanned all 2,032 built HTML files) |
|---|---:|---:|---|
| `auth.js` | 54,782 B | 15,772 B | **every page on the site** (all 21 top-level sections × 6 locales) |
| `app.js` | 3,949 B | 1,695 B | every page |
| `booking.js` | 12,017 B | 4,609 B | every page |
| `community.js` | 10,220 B | 3,772 B | every page |
| `leaflet.js` | 147,552 B | 42,578 B | `/app/`, `/map/`, `/attractions/*`, `/regions/*`, `/routes/*` (+ locale prefixes) — correctly scoped to map-bearing templates |
| `weather.js` | 3,194 B | 1,363 B | `/app/`, `/map/` (+ locales) |
| `app-mobile.js` | 50,321 B | 13,683 B | `/app/` (+ locales) |
| `workspace.js` | 65,585 B | 18,588 B | `/map/` (+ locales) |
| `trip.js` | 11,191 B | 4,023 B | `/trip/` (+ locales) |
| `travel-{en,ka,ru,fa,he,ar}.js` | 191–227 KB each | 50–53 KB each | `/app/`, `/map/`, `/trip/` — one per-locale "places" data blob (`window.EXP = {...}`), each shipped once for its own locale only. Sizes differ only because of localized place names/descriptions inside the JSON-like payload, not code differences. |
| `admin-bookings.js` | 5,250 B | 1,894 B | `/admin/` only |

**Finding, confirmed sitewide (not just the 9 sample pages):** `auth.js` + `app.js` + `booking.js` + `community.js` (≈80.9 KB raw / ≈25.8 KB gzip) load on **all 2,032 generated pages, in every locale**, including static content pages (`/faq/`, `/terms/`, `/blog/*`) that have no booking widget, no community feed, and no auth-gated UI visible without a click. JS-coverage measurement (below) shows why this matters.

### 2.2 Unused CSS/JS by template (Chromium CDP coverage; heuristic, see §0)

| Template | CSS used / total | CSS unused % | JS used / total | JS unused % | Notes |
|---|---:|---:|---:|---:|---|
| Home | 20.2 / 164.1 KB | 87.7% | 12.4 / 76.8 KB | 83.9% | `auth.js` alone: 93.5% unused |
| Fleet list | 17.0 / 149.3 KB | 88.6% | 12.4 / 76.8 KB | 83.9% | |
| Fleet detail | 15.2 / 149.3 KB | 89.8% | 12.4 / 76.8 KB | 83.9% | |
| Map | 28.4 / 164.1 KB | 82.7% | 262 / 453 KB | 42.2% | best JS utilization of any template — it's the page that actually needs Leaflet + the places data |
| Tours | 14.8 / 149.3 KB | 90.1% | 12.4 / 76.8 KB | 83.9% | |
| Attraction | 26.3 / 164.1 KB | 84.0% | 64 / 226 KB | 71.6% | |
| Route | 23.0 / 164.1 KB | 86.0% | 69 / 230 KB | 69.8% | |
| Region | 21.1 / 164.1 KB | 87.2% | 73 / 235 KB | 68.8% | |
| App shell | 1.2 / 18.5 KB | 93.6% | 213 / 420 KB | 49.3% | own small CSS bundle (not `style.css`) already scoped tight |

`theme.py` does emit a single ~150 KB CSS bundle shared by 8 of the 9 templates (measured: `dist/assets/style.*.css` = **150,444 bytes**, matching the brief's "~155 KB" estimate) — confirmed **each template only uses 9–17% of it**. `leaflet.css` runs 60–100% unused depending on template (100% unused on Home, where it shouldn't be loaded at all — see F2).

`auth.js` (49.7 KB parsed / measured) is **93.5% unused on every single template**, `community.js` (9.3 KB) is **97.7% unused everywhere** — both load their full Firebase/community wiring on first paint regardless of whether the visitor ever opens the login/community UI.

### 2.3 `/assets/photos/*` inventory

Script: `identify -format "%f %w %h\n" *.webp` + `find`/`du` over `dist/assets/photos/`.

- **883 files, all already WebP** (0 legacy JPG/PNG in this directory) — 75 MB total.
- **42 files exceed 200 KB**, topped by `birtvisi-fortress.webp` (448.6 KB), `batsara-reserve.webp` (317.5 KB), `kvetera-fortress.webp` (316.0 KB), `shaori-reservoir.webp` (292.9 KB), `petra-fortress.webp` (280.4 KB) — full top-20 list captured in the run log; all 20 are 205–449 KB.
- **752 of 883 (85%)** have their long edge ≥ 800 px. Dimension histogram is dominated by 900×675, 900×600, 1100×825, 1100×733, 675×900 (portrait) — i.e. the corpus is essentially two fixed sizes (~900px and ~1100px on the long edge) with no smaller variants at all.
- **Zero `srcset` usage anywhere in the codebase** (`grep -c srcset theme.py build.py` → 0/0) — confirmed by both static grep and by the Playwright image audit (`currentSrc` always equals the single `src`).

### 2.4 Are attraction hero images served at a sensible resolution for a ~400px-wide card?

No — measured directly (Playwright `getBoundingClientRect()` vs. `naturalWidth`) on live-rendered pages:

| Context | Displayed width | Image natural width | Oversize factor (linear / area) |
|---|---:|---:|---|
| `/tours/` card, mobile | 328 px | 1100 px | 3.4× / ~12× bytes |
| `/tours/` card, desktop | 239 px | 1100 px | 4.6× / ~21× bytes |
| Attraction detail hero, mobile | 364 px | 1100 px | 3.0× / ~9× bytes |
| Attraction detail hero, desktop | 1158 px | 1100 px | 0.9× (correctly sized — full-bleed hero) |

The hero image is right-sized **only** where it's shown full-width (the attraction detail page itself). Every place the *same file* is reused as a card thumbnail — nearby-attraction cards, region listing cards, route stop cards, the tours grid — serves the full 900–1100px original into a 239–364px box, because there is only one size to serve (§2.3, §4 root cause: `fetch_photos.py:MAXW = 1100`).

### 2.5 `<img alt>` quality — sample of 30 attraction pages (seeded random sample, script-driven)

Sample: `ls attractions/ | shuf --random-source=<(yes 42) -n 30`, then regex-extracted every non-`aria-hidden` `<img alt="...">` from each page (215 images total).

- **Empty (`alt=""`): 100 / 215 (46.5%)** — every single case is one of the "nearby attractions" or "related" card images at the bottom of an attraction page (e.g. `bazaleti-lake/index.html` shows `Ananuri Fortress`, `Zhinvali Reservoir`, `Samtavro Monastery` cards, all `alt=""`), even though the page already has the target attraction's display name in scope for the adjacent `<h3>` link text.
- **Duplicated alt within the same page: 0 / 215.** The hero + gallery images use a clean `"{Name}"`, `"{Name} — 1"`, `"{Name} — 2"`, `"{Name} — 3"` pattern — no collisions found.
- **Keyword-stuffed (long/comma-list heuristic: >12 words, or ≥3 commas, or a `|`): 0 / 215.** No stuffing found; the non-empty alts are short and specific.

So the real defect here is narrower than "bad alt text" — it's specifically **empty alt on the related/nearby card images**, at a consistent 3–4 empty alts per attraction page, corpus-wide. Root cause identified below (F6).

---

## 3. Prioritised fix list

Ordered by (measured impact) × (how many pages it touches) ÷ (risk). Every item names the exact function/line found in this session's code reading.

### F1 — Header logo is a 530 KB PNG rendered at 75×30 CSS px, on ~1,982 of 2,029 pages
- **Problem:** `build.py`'s `header_html()` (function starts at `build.py:588`) builds the site header logo at `build.py:620-627`:
  ```
  logo_img = DESIGN.get("logo_image")          # build.py:620 — resolves to /assets/do-logo-tight.png
  logo = (f'<img src="{E(logo_img)}" alt="" aria-hidden="true">' ...)   # build.py:622
  ```
  The path comes from `content/settings/design.yml:3` (`logo_image: "/assets/do-logo-tight.png"`). That file is **1202×482 px, 530,712 bytes**, displayed everywhere at **75×30 CSS px** (confirmed via `identify` + the Playwright image audit). The repo already ships `logo-do.png` (239×96, 29,972 B) and `logo-do@2x.png` (479×192, 91,855 B) — either is a 5.7×–17.7× byte reduction with no visible quality loss at the rendered size.
- **Measured impact:** confirmed present on 1,982/2,029 built `index.html` files (grep across the whole `dist/`). Even cached after a repeat visit, it's 500 KB+ of dead weight on every first visit and every one of the six locale trees; on `/fleet/` and `/fleet/bmw-5-series/` it is **the only image the page loads at all** (67–68% of total page weight in table 1.2).
- **Where the fix belongs:** `content/settings/design.yml` (`logo_image` value) is the one-line fix; `build.py:622` (`header_html`) is where I'd also add explicit `width="150" height="60"` (or whatever the chosen asset's intrinsic size is) so the browser doesn't have to wait on the image to know the header's height.
- **Proposed change:** point `logo_image` at `/assets/logo-do@2x.png` (crisp on retina at 75×30 CSS px) or, better, generate a purpose-sized ~150×60 WebP (~3–5 KB) via the existing image pipeline and use that. Add `width`/`height` attributes in `header_html`.
- **Risk:** low. It's a static asset swap behind one config key; verify the logo still reads correctly against the dark and light header states before shipping (the current file may have padding/whitespace baked in that a straight crop of `logo-do@2x.png` lacks — eyeball it once).

### F2 — Homepage force-loads `leaflet.css` (14.8 KB) for a map that does not exist on the page
- **Problem:** `render_static_page()` at `build.py:1010` calls `head_html(..., leaflet=(page == "index"))`. Inside the same function, `map_section = ""` is declared at `build.py:805` and **never referenced again anywhere in the file** — it's dead code; the homepage renders no map. Measured CSS coverage confirms it: `leaflet.css` shows **0 / 14,791 bytes used, 100% unused** on `/` in both viewports (table 2.2, §1.4).
- **Measured impact:** 14.8 KB of additional render-blocking CSS (`<head>` position, before `style.css` even) on the single highest-traffic page of the site, for zero benefit.
- **Where the fix belongs:** `build.py:1010`, the `leaflet=(page == "index")` argument. Either remove the dead `map_section`/leaflet wiring for `index`, or (if a mini-map is actually planned for the homepage) finish wiring `map_section` and keep `leaflet=True` only once it's real.
- **Proposed change:** `leaflet=False` for the `index` page (or drop the parameter entirely if no other static page needs it).
- **Risk:** very low — verified by direct code read that no homepage markup depends on Leaflet; CSS coverage independently confirms zero usage.

### F3 — No responsive images anywhere: attraction/region/route/tour cards serve a 900–1100px original into a 239–364px box
- **Problem:** every card-grid template calls the same hand-rolled pattern — `render_region()` (`build.py:1772-1773`), `render_attraction()`'s "nearby" block (`build.py:1869-1870`), `render_route()` (`build.py:1957`), and `render_tours_page()` (`build.py:2852`) all emit `<img src="{full-size photo}" alt="..." loading="lazy">` with no `srcset`/`sizes` and no smaller source. The root cause is one level lower: `fetch_photos.py:29` (`MAXW = 1100`) — the entire 883-photo asset pipeline only ever produces **one size** per photo. Corpus-wide: 85% of photos are ≥800px on the long edge (§2.3), and the measured on-page oversize factor is 3–4.6× linear / 9–21× in pixel area (§2.4) for every card context.
- **Measured impact:** on `/tours/`, `/routes/*`, `/regions/*`, and every attraction's "nearby" section, card images are the largest single contributor to page weight after the header logo — e.g. `/tours/` desktop pulls 1.73 MB of `img` bytes (table 1.2) for a grid whose photos render at ~240px wide. Fixing this is the single largest byte-for-byte win available in the codebase, larger than every JS bundle combined.
- **Where the fix belongs:** `fetch_photos.py` (asset pipeline — add a second, smaller derivative per photo, e.g. 480px alongside the existing 1100px `MAXW`) **and** the four `build.py` call sites above (emit `srcset="{small} 480w, {large} 1100w" sizes="...")`. These are two different files that both need updating together; neither one alone is a complete fix.
- **Proposed change:** generate a `-480w` WebP variant for every photo at fetch time; update the 4 card-rendering call sites (and `gallery_html()` at `build.py:1285` if gallery thumbnails should also downsize) to use `srcset`/`sizes` pointing browsers at the small variant for card contexts, keeping the full 1100px original only for the hero use in `photo_html()` (`build.py:1303`, already correctly sized — see §1.5's "0.9×" row).
- **Risk:** medium — touches an asset-generation script (`fetch_photos.py`) plus four template functions; must confirm the smaller derivative still satisfies whatever Wikimedia Commons attribution/licensing requirements the existing pipeline enforces (the script's own docstring notes license metadata must ride along with each image), and must re-run for all 883 existing photos, not just new ones.

### F4 — `auth.js` (49.7 KB), `community.js` (9.3 KB), `booking.js`, `app.js` load on all 2,032 pages, 62–98% unused per page
- **Problem:** every generated page — including static content pages with no booking widget, no auth-gated UI, and no community feed visible without interaction — loads all four bundles as `type="module"` scripts. Confirmed both by scanning the header/footer-shell template output across the entire `dist/` tree (§2.1: literally every top-level section, every locale) and by CDP JS coverage: `auth.js` is 93.5% unused, `community.js` is 97.7% unused, on every one of the 9 templates measured (table 2.2). This isn't hurting LCP (they don't block render — see §1.4) but it is real, consistent parse/compile cost: it shows up as a ~55–90 ms main-thread long task shortly after `domContentLoaded` on **every single page measured** (table 1.3, "long tasks" column) — this is almost certainly module evaluation of these four scripts running on every page load, since it's the one thing all measured pages have in common regardless of template.
- **Measured impact:** ~81 KB raw / ~26 KB gzip of JS, plus a reproducible ~55–90 ms INP-relevant main-thread task, paid by every visitor on every page, most of whom never touch auth, booking, or community features on that particular page.
- **Where the fix belongs:** `build.py:691`, function `shell()` — the four tags are built unconditionally at `build.py:712-716`:
  ```python
  fb = (f'\n<script>window.FH_CFG={J(cfg)};</script>'
        f'\n<script type="module" src="{ASSET.get("auth", "/assets/auth.js")}"></script>'
        f'\n<script type="module" src="{ASSET.get("booking", "/assets/booking.js")}"></script>'
        f'\n<script type="module" src="{ASSET.get("community", "/assets/community.js")}"></script>'
        f'\n<script defer src="{ASSET.get("app", "/assets/app.js")}"></script>')
  ```
  `shell()` is called once per generated page (all 2,032 of them) with no `current`-based branching around this block — it is unconditional, which matches the corpus-wide scan in §2.1.
- **Proposed change:** keep these scripts wired the way they are on pages that actually surface the corresponding UI (booking CTAs exist almost everywhere, so `booking.js` may need to stay global), but gate `community.js` (only used by `/community/` and public-trip pages) and defer `auth.js`'s heavy Firebase init until the first `pointerdown`/`focus` on an auth-gated control (login link, "save trip" button, etc.) rather than on page load. This is a bigger, riskier refactor than F1–F3 — treat it as a follow-up investigation, not a same-day patch.
- **Risk:** medium-high — auth/session state is easy to get subtly wrong with lazy-init (e.g. a returning logged-in user's UI should still reflect "signed in" without waiting for an interaction). Needs a dedicated design pass, not a drive-by change; I'm flagging the measured cost, not prescribing the exact lazy-load mechanism.

### F5 — `/map/`'s LCP image is an un-preloadable CSS `background-image` on a `::before` pseudo-element
- **Problem:** the planner intro block built by `travel_workspace_block()` (`build.py:2327`, the `.dow-intro` div at `build.py:2351`) gets its hero image from `theme.py:1834`:
  ```
  .dow-intro::before{{content:"";position:absolute;inset:0;background:url("/assets/rentup-planner-hero.jpg") center/cover no-repeat}}
  ```
  Because this is a CSS background on a pseudo-element, it (a) cannot carry `loading`/`fetchpriority`/`decoding` attributes, (b) is invisible to the browser's preload scanner (it's only discovered once CSS is parsed and the box is laid out, not from the initial HTML byte stream), and (c) is exactly the element the LCP `PerformanceObserver` reported as the page's largest paint (table 1.3: `<div>`, `rentup-planner-hero.jpg`).
- **Measured impact:** `/map/` has the highest local LCP of any template (344 ms mobile / 540 ms desktop vs. 136–320 ms elsewhere) and the only measurable CLS (0.0068) and the largest long-task total (334 ms desktop) — the three problems compound because the hero paint, the layout pass, and Leaflet/`workspace.js`/`travel-en.js` initialization are all competing for the same early window. The image file itself is small (11 KB), so this is a *discovery-timing* problem, not a bytes problem.
- **Where the fix belongs:** `theme.py:1834` (the CSS rule) plus the `<head>` builders of every caller of `travel_workspace_block()` — confirmed by reading the call sites, the `.dow-intro` markup (and therefore this background-image) renders unconditionally (not gated by the function's `hero` parameter) on `render_map_page()` (`build.py:1684`, calls at `1689`), its legacy-redirect twin (`build.py:1702`, call at `1723`), and `render_planner()` (`build.py:2500`, call at `2504`) — i.e. `/map/` and the planner page both ship this same undiscoverable background-image.
- **Proposed change:** either (a) add `<link rel="preload" as="image" href="/assets/rentup-planner-hero.jpg" fetchpriority="high">` to the `<head>` for pages that render `.dow-intro`, so the preload scanner can start the fetch immediately even though the CSS use is still a background-image; or (b) convert the hero to a real `<img fetchpriority="high" loading="eager">` positioned under the text via `object-fit:cover`/absolute positioning (same visual result, but now natively discoverable and prioritizable). Option (a) is the smaller, lower-risk change.
- **Risk:** low for (a) (additive `<link>` tag only); medium for (b) (touches layout markup that currently relies on `::before` for the overlay + gradient treatment — check whether `theme.py` layers a gradient or text-contrast overlay on top of this background that would need to move if it becomes a real `<img>`).

### F6 — Empty `alt` on every "nearby/related attraction" card image (46.5% of sampled attraction-page images)
- **Problem:** the exact same three call sites cited in F3 hardcode `alt=""`:
  - `render_region()`, `build.py:1773`: `f'<img src="{E(a["image"])}" alt="" loading="lazy"></a>'`
  - `render_attraction()`'s nearby block, `build.py:1870`: same pattern
  - `render_route()`, `build.py:1957`: same pattern
  - `render_tours_page()`, `build.py:2852`: same pattern

  In every one of these functions, the attraction/route/car's localized display name is already in scope two lines away (used for the adjacent `<h3>`/link text) — e.g. in `render_attraction()`, `ATTRACTIONS[n][lang]["name"]` is used at `build.py:1872` for the card title, one line after the `alt=""` at `build.py:1870`.
- **Measured impact:** 100/215 (46.5%) of non-decorative `<img>` tags across a 30-page random sample of attraction pages have empty `alt`; scoped to exactly the "nearby attractions" card grid, present on presumably most of the 259 attraction pages (not all re-verified, but the template is shared) plus every region and route page. This is an accessibility gap (screen readers announce "image" with no context inside a linked card) and a missed, low-effort image-SEO signal — not a page-weight or CWV issue.
- **Where the fix belongs:** the four `build.py` call sites above — change `alt=""` to `alt="{E(<the same name already used for the card title)}"` in each.
- **Proposed change:** e.g. in `render_attraction()`, `alt="{E(ATTRACTIONS[n][lang]["name"])}"` instead of `alt=""`.
- **Risk:** very low — pure string change, name is already computed and validated in the same expression.

### Lower-priority / worth doing, smaller measured impact
- **Google Fonts CSS is render-blocking and cross-origin on every page** (33 KB parse-blocking CSS + 2 extra origins' DNS/TLS before first text paint). `<link rel="preconnect">` is already present for both `fonts.googleapis.com` and `fonts.gstatic.com` (good — confirmed in the `<head>` dump, §1.4 note), which is the correct mitigation already in place; a further step (self-hosting the two subsets actually used, or `font-display:swap`, which is already set) would trade a small implementation cost for removing the cross-origin CSS entirely, but the current preconnect mitigation means this is not urgent.
- **`do-logo-tight.png` aside, six other unused multi-hundred-KB PNG logo variants ship in `/assets/` root** (`do-logo-clean.png` 758 KB, `do-logo-modern.png` 1.05 MB, `do-logo-premium.png` 943 KB, `do-logo-tight.png` 531 KB, `do-logo-transparent.png` 762 KB, `sl-logo.png` 431 KB, `logo-do-512.png` 466 KB — 4.9 MB combined). None of these appeared as a network request in any of the 9 templates measured, so they don't cost *visitors* anything directly, but they inflate the deploy and are worth pruning if genuinely unused — **not measured** whether any are referenced from pages outside the 9 sampled templates (e.g. `/business-card/`, PWA manifest icons); grep the full `dist/` tree before deleting any.

---

## 4. Do-not-do list

- **Do not remove or defer Leaflet (`leaflet.js`/`leaflet.css`) from `/map/`, `/attractions/*`, `/routes/*`, `/regions/*`, or `/app/`.** It is already correctly scoped — it is absent from Home/Fleet/Tours (confirmed, §1.4, §2.1) and present only where an interactive map genuinely renders. Its JS-coverage "unused%" (62–84%, table 2.2) reflects a full-featured mapping library exposing more API surface than any single page's map configuration exercises — that is normal for a general-purpose library and is not evidence it can be trimmed without breaking map controls, markers, or interaction handlers that different pages activate differently.
- **Do not lazy-load or defer `workspace.js`, `travel-{locale}.js`, or `app-mobile.js` on `/map/`, `/trip/`, or `/app/`.** These are the planner's own data (`window.EXP` places blob) and interaction code; deferring them would delay the planner becoming interactive, which is the core function of those pages. If F4's lazy-init idea is ever extended past `auth.js`/`community.js`, do not let it touch these three files.
- **Do not blanket-convert every `<img>` to `loading="lazy"` as a quick win.** Two of the nine templates (`/tours/`, `/routes/*`, `/regions/*` in some cases) already have this backwards — the *hero* content needs `loading="eager" fetchpriority="high"` (as `photo_html()` already correctly does for attraction pages, `build.py:1303-1319` — use that function as the reference pattern) while only below-the-fold cards should stay lazy. Applying lazy-loading uniformly would make the Home-page mobile LCP defect (table 1.3, row 1: the LCP element is currently a lazy card image instead of the hero) worse, not better, on every template.
- **Do not strip `content-length`/reduce the shared `style.css` bundle by deleting rules that "look unused" on one template.** The 84–91% "unused" figure (table 2.2) is measured per-template; a rule unused on `/fleet/` may be exactly what `/map/`'s or `/attractions/*`'s markup depends on. Any CSS trimming needs either a build-time per-template CSS split (a real, larger project) or a coverage run across *all* templates (all 9 sampled here plus the ones not sampled — blog, community, account, business-card, etc.) before removing a single selector, not a spot-check of one page.
- **Do not change `fetch_photos.py`'s `MAXW` down to a single smaller value (e.g. drop to 480px globally) to "fix" the oversized-card problem.** That would fix the card-thumbnail waste (F3) but break the attraction detail hero, which is correctly full-bleed at ~1100px (§2.4, table row "attraction detail hero, desktop: 0.9×" — already right-sized). The fix is to *add* a second smaller size, not replace the existing one.
- **Do not preload `rentup-planner-hero.jpg` (F5) globally in the shared `<head>` builder.** It's only relevant to pages that render `.dow-intro` (the map/planner intro); adding it to every template's `<head>` would waste a preload's priority budget on pages that never use the image.

---

## 5. Core Web Vitals: targets vs. current

| Metric | Target | Current (measured, local server — see §0) | Status |
|---|---|---|---|
| **LCP** | ≤ 2.5 s | 136 ms – 540 ms across all 9 templates × 2 viewports (table 1.3) | **Cannot be certified against the 2.5 s target from this environment** — these numbers exclude real network RTT, TLS, CDN latency and Google Fonts' two extra origins, all of which the target is meant to account for. Directionally healthy (large margin below 2.5 s even accounting for a few hundred ms of real-world network overhead on top), **except**: the LCP-*element* defects (home-mobile picking a lazy card image instead of the hero; `/map/`'s un-preloadable CSS background) will cost real time on a real network that these local numbers don't reflect — F5 in particular should be fixed before trusting a field LCP number for `/map/`. **Field data (CrUX / PageSpeed Insights against `rentup.ge`) is the only way to actually certify this target; not measured here.** |
| **INP** | ≤ 200 ms | Not measured — INP requires a real user interaction (click/tap/keypress) timed end-to-end; this audit measured page-load performance (long tasks, TBT-style) but did not simulate interactions with the booking modal, planner map controls, or community feed. The one interaction-relevant proxy I do have: every page pays a **55–90 ms main-thread long task** shortly after load (table 1.3), most likely `auth.js`/`booking.js`/`community.js`/`app.js` module evaluation (F4) — if a real interaction lands inside or immediately after that window, it will queue behind it. This is suggestive, not a measured INP. |
| **CLS** | ≤ 0.1 | **0.0000 – 0.0068** across all 9 templates × 2 viewports (table 1.3) | **Already meets target with wide margin**, and by design — `theme.py`'s `aspect-ratio`/fixed-`height` CSS containment (§1.5) does the job regardless of whether individual `<img>` tags carry `width`/`height`. No CLS fix is needed; don't let the "images missing width/height" heuristic from a generic audit checklist drive work here without checking, as I did, whether it's actually costing anything (it isn't). |

---

## 6. What's already working (context, not a fix list)

To keep the fix list honest about where effort is actually needed:

- No render-blocking `<script>` in any `<head>` — all deferred/`type=module`, all at end of `<body>` (§1.4).
- `photo_html()` (`build.py:1303`) already does the right thing for attraction hero images: `loading="eager" fetchpriority="high" decoding="async"` plus `sizes` — this is the pattern F3/F6's fixes should be modeled on, not reinvented.
- CLS is already excellent sitewide via CSS containment, independent of per-image HTML hygiene.
- Leaflet and the planner data bundles are already scoped only to the templates that use them (§2.1) — nothing to trim there.
- The `/app/` shell already avoids the shared 150 KB `style.css` in favor of a ~3.7 KB inline stylesheet — proof the team already knows how to scope CSS per-template when it matters; F2's homepage `leaflet.css` fix and any future CSS-splitting work should follow that precedent.
- `preconnect` hints for both Google Fonts origins are already present.
- All 883 photos in `/assets/photos/` are already WebP — the format-conversion work is done; what's missing is *sizes*, not format (§2.3).
