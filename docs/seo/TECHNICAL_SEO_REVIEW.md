# RentUp.ge — Technical SEO Review (delivery layer)

**Date:** 2026-08-29
**Scope:** crawlability, indexation, sitemaps, hreflang delivery, host-level (GitHub Pages) behaviour, rendering, structured-data *delivery*, and build scalability.
**Method:** static inspection of the working-tree `dist/` (2,140 HTML files, rebuilt 2026-08-29 22:06), the sources that produce it (`build.py`, `static/sw.js`, `.github/workflows/pages.yml`, `netlify.toml`), plus live HTTP probes against `https://rentup.ge` (GitHub Pages, `server: GitHub.com`, HTTP/2 via Fastly).

**Deliberately out of scope** (owned elsewhere, not repeated here):
- Everything `scripts/seo_audit.py` already asserts — see §4.
- Core Web Vitals / page weight / image sizing / render-blocking CSS — `docs/seo/SEO_PERFORMANCE.md`. Only two *delivery* items it did not measure appear below (T-05 head size, T-13 duplicate assets); nothing from its F1–F6 list is restated.
- Schema **design** (which types, which properties). Only schema **delivery** faults are flagged (T-05).
- On-page copy, keyword targeting, internal-link editorial strategy.

---

## 0. Two facts that frame everything below

**(a) Production is running an older build than this working tree.** Live `https://rentup.ge/sitemap.xml` is a single flat `<urlset>` with **2,142** URLs; the working tree produces a `<sitemapindex>` with 8 children and **2,100** URLs. Live HTML carries no `/assets/analytics.js` tag. So T-01 and T-03 are *regressions staged in the working tree that will ship on the next push to `main`* — they are not live yet. Everything else is already live.

**(b) Counts in the brief are stale.** Actual built content: **257** attractions (not 267), **32** routes (not 49), **11** regions, **17** cars, **5** itineraries, **10** car-rental locations + 4 categories, **4** blog posts, **11** core pages — × 6 languages = 2,100 indexable URLs + 40 noindex = 2,140 files.

---

## 1. Findings table

| ID | Sev | File:line | Issue | Patch (summary — full diff in §2) | Verification command |
|---|---|---|---|---|---|
| **T-01** | **P0** | `build.py:715`, `build.py:719-723` | `<script defer src="/assets/analytics.js">` is emitted on **2,125 of 2,140** pages, but `static/analytics.js` does not exist, so the file is never written. Every page load and every Googlebot render fetches a 404 that returns `text/html` (the 5.6 KB 404 page) instead of JS. | Make `analytics_html()` return `""` when the asset was never hashed in; drop the hard-coded fallback in `ASSET`. | `test ! -e dist/assets/analytics.js && grep -rl 'assets/analytics.js' dist --include=*.html \| wc -l` → must be `0` |
| **T-02** | **P0** | `build.py:2839-2844`, `.github/workflows/pages.yml:23` | `source_lastmod()` reads **filesystem mtime**. `actions/checkout@v4` writes every file fresh, so in CI every mtime equals the checkout time. **Proven in production: all 2,142 live sitemap URLs carry `<lastmod>2026-08-29</lastmod>` — 100%, one single date.** Locally mtimes survive, so the bug is invisible on a dev machine (local build shows 5 distinct dates). Google learns the signal is worthless and stops using it for a 2,100-URL site. | Derive lastmod from `git log -1 --format=%cs -- <path>`, fall back to mtime; set `fetch-depth: 0` on checkout. | `curl -s https://rentup.ge/sitemap.xml \| grep -o '<lastmod>[^<]*' \| sort \| uniq -c` → must show >1 distinct date |
| **T-03** | **P0** | `content/attractions/*`, `content/routes/*` (deleted); `build.py:4601-4608` | 27 source YAMLs were deleted (10 attractions, 17 routes). Their **162 live, indexed, HTTP-200 URLs** (27 × 6 languages) disappear from `dist/` on the next deploy and become hard 404s with no `410`, no `301`, and no removal from Search Console. Verified live 200: `/attractions/betania-monastery/`, `/routes/kakheti-wine-day/`, `/ka/attractions/tbilisi-sea/`. | Add a `content/settings/gone.yml` redirect map and emit meta-refresh + canonical stubs (same pattern already used for `/pricing/`), or restore the sources. | `comm -23 <(curl -s https://rentup.ge/sitemap.xml\|grep -o 'https://rentup.ge/[^<]*'\|sort) <(grep -ho 'https://rentup.ge/[^<]*' dist/sitemaps/*.xml\|sort) \| wc -l` → must be `0` |
| **T-04** | **P1** | `build.py:4569-4580` (region/attraction loops), `build.py:4601` | `/attractions/`, `/routes/`, `/regions/` and their 5 language mirrors — **18 URLs** — return **404** (verified live). These are the parent directories of 1,542 + 192 + 66 sitemap URLs. Nothing links to them, so `seo_audit.py`'s broken-link check cannot see it. URL-trimming users, external citations and Googlebot's own path-walking all hit a 404. | Emit meta-refresh + canonical stubs to `/map/` (the parent the site's own `BreadcrumbList` already declares for all three types). Real hub pages are the follow-up. | `for l in "" ka/ ru/ fa/ he/ ar/; do for d in attractions routes regions; do curl -so/dev/null -w "%{http_code} /$l$d/\n" https://rentup.ge/$l$d/; done; done \| grep -v ^200` → empty |
| **T-05** | **P1** | `build.py:798`, `build.py:1223-1228` | The homepage `<head>` is **58,486 bytes**, of which **55,133 is one pretty-printed JSON-LD block** (`J()` = `indent=2`), including an `ItemList` of **every one of the 257 attractions**. `</head>` does not close until byte 58 K, so the hero `<img>` is not in the first ~58 KB of the document on the site's most important page, in all 6 languages (~330 KB of deploy). Grows linearly: at 1,000 attractions this is ~130 KB per homepage. Not covered by `SEO_PERFORMANCE.md` (it measured render-blocking *subresources*, not document head size). | `J(ld)` → `JC(ld)` (already defined, `build.py:57`) — ~30% off immediately; cap the homepage `ItemList` at 24 items. | `python3 -c "import re,pathlib;r=pathlib.Path('dist/index.html').read_text();print(r.lower().find('</head>'))"` → target < 12000 |
| **T-06** | **P1** | `build.py:752-754`, `build.py:775` | `head_html()` emits the full 7-entry hreflang cluster unconditionally, including on the **18 pages it simultaneously marks `noindex, nofollow`** (`/account/`, `/trip/`, `/business-card/` × 6). An hreflang cluster whose members are noindex is a contradictory pair: the annotation asks Google to swap the page into SERPs for other locales while `noindex` forbids it. Google discards the cluster; the reciprocity `seo_audit.py` validates is validating a set that will never be used. | Skip `alts` when the page resolves to noindex. | `python3 -c "import sys;sys.path.insert(0,'scripts');import seo_audit as S;from pathlib import Path;p=S.crawl(Path('dist'));print([k for k,v in p.items() if S.is_noindex(v.robots) and v.hreflang_pairs])"` → `[]` |
| **T-07** | **P1** | `build.py:4510-4514`, `build.py:4564-4568` | The 12 alias stubs (`/pricing/`, `/planner/` × 6) carry `<meta name="robots" content="noindex">` **and** `<link rel="canonical">` on the same document. Google's guidance is explicit that `noindex` + `canonical` is a conflicting pair — it honours `noindex` and drops the consolidation, so any external link equity pointing at the old `/pricing/` URLs is discarded rather than passed to `/fleet/`. A 0-second meta-refresh is already treated as a redirect; the `noindex` is what breaks it. Also: `netlify.toml`'s real 301s for these paths are dead on GitHub Pages (T-14), so these stubs are the *only* mechanism. | Remove `noindex` from both stubs, keep canonical + refresh. **Also update `scripts/seo_audit.py:61-63`** — `/pricing/` and `/planner/` must move out of `DEFAULT_MUST_BE_NOINDEX` or the audit will start erroring. | `curl -s https://rentup.ge/pricing/ \| grep -c noindex` → `0`; `python3 scripts/seo_audit.py dist` → still 0 ERROR |
| **T-08** | **P1** | `.github/workflows/pages.yml:28` | The Pages workflow runs `python build.py dist` **without `--strict`**. `netlify.toml:8` used `--strict` deliberately as a publication gate ("placeholder contacts or a car with no main photo blocks the build with exit 2"). Moving to Pages silently removed that gate from the only pipeline that now publishes. | `- run: python build.py dist --strict` | `grep -n 'build.py dist' .github/workflows/pages.yml` → must contain `--strict` |
| **T-09** | **P1** | `build.py:2847-2867` | `_sitemap_urls()` has no split guard. `attractions.xml` is already **1.44 MB / 1,542 URLs** (≈932 B per URL — the 7 `xhtml:link` alternates dominate). The 50,000-URL cap is hit at ~8,300 attractions and the 50 MB cap at ~53,600 URLs; neither is checked, so the build will one day emit a file Google rejects **wholesale and silently**. | Chunk each child at 45,000 URLs into `<name>-1.xml`, `<name>-2.xml`; register every chunk in the index. | `python3 -c "import re,glob;[print(f,len(re.findall('<loc>',open(f).read()))) for f in glob.glob('dist/sitemaps/*.xml')]"` → every count < 45000 |
| **T-10** | **P1** | (consequence of T-04) | **1,344 indexable pages sit at click depth ≥ 4** from `/` (histogram: d0=1, d1=25, d2=184, d3=552, d4=748, d5=466, d6=130). No orphans and no unreachable indexable pages — the graph is sound — but the depth profile is what you get when 1,542 attraction URLs have no hub and are reachable only through region pages and "nearby" cards. | Fixing T-04 with real (not stub) hubs collapses attractions/routes/regions to depth 2–3. Track this metric after the fix. | Re-run the depth script in §3.3; target: ≤ 400 indexable pages at depth ≥ 4 |
| **T-11** | **P2** | `build.py:3075-3087` | `render_404()` hard-codes `lang = "ka"` and `<html lang="ka">`. GitHub Pages serves this single file for **every** missing path in all 6 language trees, so an Arabic or Hebrew visitor who mistypes a URL gets a Georgian, LTR 404 page whose nav links all point into `/ka/`. Status code is a correct hard 404 (verified). | Ship a language-neutral 404 that picks its locale from `location.pathname` client-side; keep the Georgian copy as the no-JS default. | `curl -s https://rentup.ge/ar/attractions/does-not-exist/ \| grep -o '<html[^>]*>'` |
| **T-12** | **P2** | `build.py:3080`, `build.py:4510-4514`, `build.py:4564-4568` | 16 pages have a wrong or absent `<html lang>`: `404.html` and `/admin/*` (3 files) declare `lang="ka"` regardless of content; the 12 alias stubs declare no `lang` and no `dir` at all — including the RTL ones (`/ar/pricing/`, `/he/planner/`, …). All 16 are noindex so ranking impact is nil, but it is an accessibility and locale-detection defect that no existing check catches (`seo_audit.py` reads `<html lang>` but never validates it against the directory). | Add `lang`/`dir` to the stub template; make `render_404()` locale-neutral (T-11). | `python3 -c "import sys;sys.path.insert(0,'scripts');import seo_audit as S;from pathlib import Path;p=S.crawl(Path('dist'));print([(k,v.lang) for k,v in p.items() if v.lang!=S.strip_lang(k)[0]])"` → `[]` |
| **T-13** | **P2** | `static/sw.js:13-25`, `build.py:4455-4456` | Service worker is **cache-first for every same-origin non-navigation GET** with no expiry and no size cap, and `weather.js` / `workspace.js` ship **unhashed** (`build.py:4455` omits them from `hashed_sources`, so both the plain and hashed copies are deployed and 12 pages link the plain one). A returning visitor is pinned to a stale `weather.js` until `CACHE` is manually bumped from `drive-on-v3`. Separately, the navigation fallback `caches.match("/")` serves the **English homepage** for any failed navigation in any language — a soft-404 shape. Googlebot does not run service workers, so this is a user-experience/staleness defect, not an indexation one. | Add `weather.js`/`workspace.js` to `hashed_sources` and to the `write_hashed` loop; make the SW network-first (or stale-while-revalidate) for unhashed paths; fall back to `/404.html`, not `/`. | `ls dist/assets/weather.js dist/assets/workspace.js` → both absent |
| **T-14** | **P2** | `netlify.toml` (whole file) | Every rule in this file is **dead** — GitHub Pages supports neither `[[redirects]]` nor `[[headers]]`. That silently drops: the 301s for `/pricing/` and `/planner/`, `Cache-Control: immutable` on `/assets/*` (live GH Pages sends a flat `max-age=600` on hashed assets), `X-Content-Type-Options`, `Referrer-Policy`, `X-Robots-Tag: noindex` on `/admin/*` and `/docs/*`, and the `text/plain` content-type pin on `llms.txt`. Keeping the file invites someone to "fix SEO" by editing rules that never execute. | Add a header block to `netlify.toml` stating it is inert on the current host, and record which of its guarantees are now unavailable. If any header actually matters, GitHub Pages cannot provide it — that needs a proxy (Cloudflare) in front. | `curl -sI https://rentup.ge/assets/style.$(ls dist/assets \| grep -o 'style\.[a-f0-9]*\.css' \| head -1 \| cut -d. -f2).css \| grep -i cache-control` |
| **T-15** | **P2** | `build.py:2950` | `robots.txt` ends with `Host: rentup.ge`. The `Host` directive was a Yandex-only extension and Yandex **dropped support in 2021**; no other crawler has ever parsed it. It is inert, and a non-standard trailing directive is exactly the kind of line a strict parser can choke on. Canonicalisation is already handled correctly at the host level (verified: `http://rentup.ge/` → 301 → `https://`, `https://www.rentup.ge/` → 301 → apex). | Delete the `Host:` line. | `curl -s https://rentup.ge/robots.txt \| grep -c '^Host:'` → `0` |
| **T-16** | **P2** | `build.py:1293` | The business-card template hard-codes `href="https://www.rentup.ge/"` while `SITE_URL` is the apex. Live this 301s to the apex, so it works — but it is the one place in the corpus that links to a non-canonical host, and it costs a redirect hop on 6 pages. | `https://www.rentup.ge/` → `{SITE_URL}/`, keep the `www.rentup.ge` display text. | `grep -rc 'https://www\.rentup\.ge' dist --include=*.html \| grep -v ':0' \| wc -l` → `0` |
| **T-17** | **P2** | `build.py` (photo-credit block; 24 occurrences in `dist/`) | 24 outbound links use `http://creativecommons.org/publicdomain/zero/1.0/deed.en`. No mixed-content risk (they are `href`, not subresources) but every click eats an extra insecure hop, and an `http://` link in a photo-credit line is a trust signal a reviewer will notice. | Rewrite the constant to `https://creativecommons.org/...`. | `grep -rc 'href="http://' dist --include=*.html \| grep -v ':0'` → empty |
| **T-18** | **P2** | `build.py:1212`, `build.py:2015` | `"dateModified": TODAY` on 54 pages (the 9 core templates × 6 languages) stamps the **build date**, not a content date — same class of defect as T-02, so every deploy re-dates pages that did not change. `"datePublished": "2026-01-15"` (`build.py:1212`) is likewise a hard-coded literal applied to all of them. | Reuse the `git`-backed helper from T-02 for both fields. | `grep -rho '"dateModified": *"[^"]*"' dist --include=*.html \| sort -u` → more than one value |
| **T-19** | **P2** | `dist/routes/*` | Measured intra-language near-duplication (8-gram Jaccard against the shorter document, seeded sample): routes **median 0.37 / max 0.60** (`kakheti-table-and-cellar` vs `kakheti-wine-loop`), fleet detail 0.36, attractions 0.25, car-rental 0.23. Attractions and car-rental are fine (that band is header/nav/footer boilerplate). Routes at 0.60 between two Kakheti pages is above boilerplate and is the one cluster worth watching as routes scale back toward 49. Flagged as a measurement, not a verdict — the content call belongs to the content reviewer. | No code patch. Add the §3.4 script to CI as a WARN gate at 0.55. | §3.4 script; watch the `max` column for routes |
| **T-20** | **P2** | `.github/workflows/pages.yml:29-31`, `dist/` | No `CNAME` file is produced. With the artifact-based Pages deployment the custom domain lives in repo **settings**, and it is currently working (apex 200, `www` 301, `http` → `https` 301 — all verified today), so **no change is required**. Recording it because it is the single un-versioned piece of the site's canonicalisation: if the Pages setting is ever cleared, nothing in this repo restores it. | None. Verify quarterly, or after any Pages settings change. | `curl -so/dev/null -w '%{http_code} %{redirect_url}\n' http://rentup.ge/ https://www.rentup.ge/` |

---

## 2. Patches

### T-01 — `/assets/analytics.js` 404 on 2,125 pages

`static/analytics.js` does not exist. `build.py:4482` guards with `if os.path.exists(p)` so `ASSET["analytics"]` is never assigned — but `build.py:715` pre-seeds a fallback value and `analytics_html()` uses it unconditionally.

```diff
--- a/build.py
+++ b/build.py
@@ -712,8 +712,7 @@
 ASSET = {"css": "/assets/style.css", "explorer": "/assets/explorer.js",
          "planner": "/assets/planner.js", "workspace": "/assets/workspace.js",
-         "app_mobile": "/assets/app-mobile.js", "trip": "/assets/trip.js",
-         "analytics": "/assets/analytics.js"}
+         "app_mobile": "/assets/app-mobile.js", "trip": "/assets/trip.js"}
 TRAVEL_ASSET = {}
 
 
 def analytics_html():
     """Build-time GA4 config. Empty IDs intentionally produce a client-side no-op."""
+    src = ASSET.get("analytics")
+    if not src:
+        return ""          # static/analytics.js absent — emit nothing, never a 404
     measurement_id = os.environ.get("GA_MEASUREMENT_ID", "").strip()
     return (f'<script>window.FH_ANALYTICS_CONFIG={{"measurementId":{J(measurement_id)}}};</script>\n'
-            f'<script defer src="{ASSET.get("analytics", "/assets/analytics.js")}"></script>')
+            f'<script defer src="{src}"></script>')
```

If GA4 is actually wanted, the alternative fix is to add `static/analytics.js` — but do not ship the tag without the file.

### T-02 — sitemap `lastmod` is the deploy date for 100% of URLs

```diff
--- a/build.py
+++ b/build.py
@@ -2836,10 +2836,26 @@
 # ══════════════════════════════════════════════════════════════ sitemap etc.
+_GIT_DATE_CACHE = {}
+
+
 def source_lastmod(path):
-    """Stable sitemap date derived from the content source, not build time."""
+    """Stable sitemap date from the source file's last *commit*, not its mtime.
+
+    mtime is useless in CI: actions/checkout writes every file fresh, so every
+    mtime equals the checkout time and every <lastmod> collapses to the deploy
+    date. Requires the workflow to check out with fetch-depth: 0.
+    """
+    key = str(path)
+    if key in _GIT_DATE_CACHE:
+        return _GIT_DATE_CACHE[key]
+    try:
+        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", key],
+                             capture_output=True, text=True, timeout=10)
+        stamp = out.stdout.strip()
+        if out.returncode == 0 and len(stamp) == 10:
+            _GIT_DATE_CACHE[key] = stamp
+            return stamp
+    except (OSError, subprocess.SubprocessError):
+        pass
     try:
-        return date.fromtimestamp(Path(path).stat().st_mtime).isoformat()
+        stamp = date.fromtimestamp(Path(path).stat().st_mtime).isoformat()
     except (OSError, ValueError):
-        return TODAY
+        stamp = TODAY
+    _GIT_DATE_CACHE[key] = stamp
+    return stamp
```

Add `import subprocess` to the imports at the top of `build.py`.

`sitemap_index()` (`build.py:2925`) has the same problem — it stamps every child with `source_lastmod("build.py")`. A child sitemap's `lastmod` should be the newest `lastmod` inside it:

```diff
--- a/build.py
+++ b/build.py
@@ -2922,10 +2922,14 @@
 def sitemap_index(children):
-    lastmod = source_lastmod("build.py")
-    items = "\n".join(
-        f"  <sitemap>\n    <loc>{SITE_URL}/sitemaps/{n}.xml</loc>\n"
-        f"    <lastmod>{lastmod}</lastmod>\n  </sitemap>" for n in children)
+    def child_lastmod(entries):
+        dates = [source_lastmod(src) if src else source_lastmod("build.py")
+                 for _, _, src in entries]
+        return max(dates) if dates else TODAY
+    items = "\n".join(
+        f"  <sitemap>\n    <loc>{SITE_URL}/sitemaps/{n}.xml</loc>\n"
+        f"    <lastmod>{child_lastmod(e)}</lastmod>\n  </sitemap>"
+        for n, e in children.items())
     return ('<?xml version="1.0" encoding="UTF-8"?>\n'
```

And the workflow must fetch history, or `git log` returns nothing and the fallback silently reinstates the bug:

```diff
--- a/.github/workflows/pages.yml
+++ b/.github/workflows/pages.yml
@@ -21,7 +21,9 @@
     steps:
       - uses: actions/checkout@v4
+        with:
+          fetch-depth: 0        # source_lastmod() needs commit history
       - uses: actions/setup-python@v5
```

### T-03 — 162 live URLs about to 404

The 27 deleted slugs (verified live 200 today, absent from `dist/`):

```
attractions: abudelauri-lakes artsivi-eagle-gorge bateti-lake bebris-tsikhe
             betania-monastery didgori-battle-memorial gomismta kojori-fortress
             niko-nikoladze-house-museum tbilisi-sea
routes:      batumi-coast-family-day borjomi-spa-day georgia-essential-five-days
             gori-uplistsikhe-day guria-coast-day guria-mountain-spa-weekend
             kakheti-cycling-day kakheti-wine-day kazbegi-mountain-day
             kutaisi-monasteries-caves-day kvemo-kartli-monasteries-day
             lagodekhi-nature-weekend martvili-nokalakevi-day mtskheta-heritage-day
             racha-family-weekend racha-lechkhumi-heritage-three-days
             tbilisi-stage-and-museum-day
```

Decide per slug whether it has a successor (redirect) or is genuinely gone (leave the 404 and remove it from Search Console). Do not guess successors — that is a content decision. The mechanism, reusing the pattern already at `build.py:4564`:

```python
# build.py — new, near the alias-stub writers (~line 4560)
GONE = load_yaml("content/settings/gone.yml") or {}   # {"attractions/kakheti-wine-day": "routes/kakheti-wine-loop"}

for old, new in GONE.items():
    for lang in LANGS:
        target = lang_root(lang) + new.rstrip("/") + "/"
        write(os.path.join(out, lang_root(lang).lstrip("/") + old.rstrip("/"), "index.html"),
              f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
              f'<meta charset="utf-8">'
              f'<link rel="canonical" href="{SITE_URL}{target}">'
              f'<meta http-equiv="refresh" content="0;url={target}">'
              f'<script>location.replace({J(target)})</script></html>')
```

No `noindex` on these stubs — see T-07 for why.

Add a regression guard so this can never happen unnoticed again:

```bash
# CI step: fail if the new sitemap drops a URL the live one still lists
curl -sf https://rentup.ge/sitemap.xml | grep -o 'https://rentup.ge/[^<]*' | sort -u > /tmp/live.txt
grep -ho 'https://rentup.ge/[^<]*' dist/sitemaps/*.xml | sort -u > /tmp/new.txt
comm -23 /tmp/live.txt /tmp/new.txt > /tmp/dropped.txt
[ -s /tmp/dropped.txt ] && { echo "ERROR: dropping live URLs:"; cat /tmp/dropped.txt; exit 1; } || true
```

### T-04 — `/attractions/`, `/routes/`, `/regions/` return 404

`/map/` is already the declared parent of all three in the site's own `BreadcrumbList` (verified on an attraction, a route and a region page), so this stub invents nothing. Insert next to the `/pricing/` stub (`build.py:4562`):

```python
# build.py — inside the per-language loop, beside the pricing/planner stubs
for hub in ("attractions", "routes", "regions"):
    hub_target = page_url(lang, "map", False)
    write(os.path.join(out, lang_root(lang).lstrip("/") + hub, "index.html"),
          f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
          f'<meta charset="utf-8">'
          f'<link rel="canonical" href="{page_url(lang, "map")}">'
          f'<meta http-equiv="refresh" content="0;url={hub_target}">'
          f'<script>location.replace({J(hub_target)})</script></html>')
```

This is the 30-minute fix that removes 18 live 404s. The real fix — paginated hubs at those three URLs, which also resolves T-10 — needs titles and descriptions in `content/pages/` and belongs on the content roadmap.

### T-05 — 55 KB of pretty-printed JSON-LD in every homepage `<head>`

Two independent changes; do both.

```diff
--- a/build.py
+++ b/build.py
@@ -795,7 +795,7 @@
 <link rel="stylesheet" href="{css_href}">{lf}
 <script type="application/ld+json">
-{J(ld)}
+{JC(ld)}
 </script>"""
```

`JC` is already defined at `build.py:57` with `separators=(",", ":")`. This alone removes ~16 KB from the homepage head and shrinks every JSON-LD block on all 2,140 pages.

```diff
--- a/build.py
+++ b/build.py
@@ -1221,10 +1221,13 @@
     if page == "index":
+        # The homepage advertises a sample; /map/ is the CollectionPage that
+        # carries the full list. An unbounded ItemList here grows the critical
+        # HTML document linearly with the attraction count.
+        _top = list(ATTRACTIONS.items())[:24]
         graph.append({"@type": "ItemList", "name": TRAVEL[lang]["exp"]["explore_h"],
                       "numberOfItems": len(ATTRACTIONS),
                       "itemListElement": [
                           {"@type": "ListItem", "position": i + 1,
                            "url": attr_url(lang, s), "name": a[lang]["name"]}
-                          for i, (s, a) in enumerate(ATTRACTIONS.items())]})
+                          for i, (s, a) in enumerate(_top)]})
```

Measured effect: homepage `</head>` offset 58,486 → ≈ 8,000 bytes; homepage HTML 90,845 → ≈ 40,000 bytes, × 6 languages.

### T-06 — hreflang on 18 noindex pages

```diff
--- a/build.py
+++ b/build.py
@@ -749,9 +749,14 @@
 def head_html(lang, current, title, desc, keywords, url, alternates, depth, ld,
               og_type="website", image=None, leaflet=False):
     css_href = ASSET["css"]
-    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{u}">'
-                     for l, u in alternates.items())
-    alts += f'\n<link rel="alternate" hreflang="x-default" href="{alternates["en"]}">'
+    # An hreflang cluster on a noindex page is a contradictory pair: it asks
+    # Google to swap the page into SERPs for other locales while noindex
+    # forbids indexing it at all. Google discards such clusters.
+    _noindexed = current in ("account", "trip", "card")
+    alts = "" if _noindexed else (
+        "\n".join(f'<link rel="alternate" hreflang="{l}" href="{u}">'
+                  for l, u in alternates.items())
+        + f'\n<link rel="alternate" hreflang="x-default" href="{alternates["en"]}">')
```

The `current in ("account", "trip", "card")` tuple is the same one that already drives the robots meta at `build.py:775`; keep the two in sync (or better, lift it to a module constant `NOINDEX_PAGES` and reference it from both sites).

### T-07 — `noindex` + `canonical` on the alias stubs

```diff
--- a/build.py
+++ b/build.py
@@ -4508,10 +4508,11 @@
             elif page == "planner":
                 target = page_url(lang, "map", False) + "#planner"
                 write(os.path.join(out, rel, "index.html"),
-                      f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
+                      f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
+                      f'<meta charset="utf-8">'
                       f'<link rel="canonical" href="{page_url(lang, "map")}">'
                       f'<meta http-equiv="refresh" content="0;url={target}">'
-                      f'<script>location.replace({J(target)})</script>')
+                      f'<script>location.replace({J(target)})</script></html>')
@@ -4562,10 +4563,11 @@
         write(os.path.join(out, pricing_rel, "index.html"),
-              f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
+              f'<!doctype html><html lang="{lang}" dir="{LANG_DIR[lang]}">'
+              f'<meta charset="utf-8">'
               f'<link rel="canonical" href="{page_url(lang, "fleet")}">'
               f'<meta http-equiv="refresh" content="0;url={fleet_target}">'
-              f'<script>location.replace({J(fleet_target)})</script>')
+              f'<script>location.replace({J(fleet_target)})</script></html>')
```

This also fixes T-12 for these 12 files. **This patch breaks `scripts/seo_audit.py` unless applied together with:**

```diff
--- a/scripts/seo_audit.py
+++ b/scripts/seo_audit.py
@@ -60,7 +60,10 @@
 DEFAULT_MUST_BE_NOINDEX: Tuple[str, ...] = (
-    "/trip/", "/account/", "/app/", "/admin/*", "/pricing/",
+    "/trip/", "/account/", "/app/", "/admin/*",
 )
+# /pricing/ and /planner/ are 0-second meta-refresh redirect stubs. They are
+# deliberately indexable-but-canonicalised so Google consolidates external
+# links into /fleet/ and /map/ instead of discarding them (noindex would).
```

The existing `DEFAULT_CANONICAL_ALIASES` entries (`seo_audit.py:48-51`) already cover the non-self-referencing canonicals, so nothing else in the audit needs touching.

### T-08 — restore the `--strict` publication gate

```diff
--- a/.github/workflows/pages.yml
+++ b/.github/workflows/pages.yml
@@ -27,1 +27,1 @@
-      - run: python build.py dist
+      - run: python build.py dist --strict
```

### T-09 — sitemap split guard

```diff
--- a/build.py
+++ b/build.py
@@ -4598,6 +4598,14 @@
     children = sitemap_children()
+    MAX_URLS = 45_000           # sitemaps.org hard cap is 50,000 / 50 MB
+    split = {}
+    for cname, entries in children.items():
+        per_file = max(1, MAX_URLS // len(LANGS))   # each entry emits len(LANGS) <loc>
+        if len(entries) <= per_file:
+            split[cname] = entries
+        else:
+            for i in range(0, len(entries), per_file):
+                split[f"{cname}-{i // per_file + 1}"] = entries[i:i + per_file]
+    children = split
     for cname, entries in children.items():
         write(os.path.join(out, "sitemaps", f"{cname}.xml"), _sitemap_urls(entries))
```

`sitemap_index(children)` then picks up the chunk names automatically.

### T-13 — hash `weather.js` / `workspace.js`; make the SW safe

```diff
--- a/build.py
+++ b/build.py
@@ -4454,3 +4454,4 @@
     hashed_sources = {"explorer.js", "planner.js", "auth.js", "booking.js", "analytics.js",
-                      "community.js", "admin-bookings.js", "app.js", "app-mobile.js", "trip.js"}
+                      "community.js", "admin-bookings.js", "app.js", "app-mobile.js",
+                      "trip.js", "workspace.js", "weather.js"}
```

`workspace.js` is already in the `write_hashed` loop at `build.py:4476`; add `("weather.js", "weather")` to the same tuple and an `ASSET["weather"]` reference wherever the 12 pages emit it.

```diff
--- a/static/sw.js
+++ b/static/sw.js
@@ -16,7 +16,7 @@
   if (request.mode === "navigate") {
     event.respondWith(fetch(request).then(response => {
       const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(request, copy)); return response;
-    }).catch(() => caches.match(request).then(hit => hit || caches.match("/"))));
+    }).catch(() => caches.match(request).then(hit => hit || caches.match("/404.html"))));
     return;
   }
-  event.respondWith(caches.match(request).then(hit => hit || fetch(request).then(response => {
+  // Cache-first only for content-hashed assets; anything else must revalidate.
+  const hashed = /\.[0-9a-f]{10}\.(js|css)$/.test(new URL(request.url).pathname);
+  if (!hashed) {
+    event.respondWith(fetch(request).catch(() => caches.match(request)));
+    return;
+  }
+  event.respondWith(caches.match(request).then(hit => hit || fetch(request).then(response => {
```

Bump `CACHE` to `"drive-on-v4"` (`static/sw.js:2`) in the same commit so existing clients drop the stale entries.

### T-15 / T-16 / T-17 — one-liners

```diff
--- a/build.py
+++ b/build.py
@@ -2949,2 +2949,2 @@
-    out += [f"Sitemap: {SITE_URL}/sitemap.xml", f"Host: {SITE_URL.split('//')[1]}", ""]
+    out += [f"Sitemap: {SITE_URL}/sitemap.xml", ""]
@@ -1293,1 +1293,1 @@
-<a class="card-contact-line card-site" href="https://www.rentup.ge/" aria-label="{E(website)}: www.rentup.ge">
+<a class="card-contact-line card-site" href="{SITE_URL}/" aria-label="{E(website)}: www.rentup.ge">
```

For T-17, replace the `http://creativecommons.org` literal in the photo-credit builder with `https://creativecommons.org`; `grep -n 'creativecommons' build.py` locates it.

---

## 3. Verification scripts

### 3.1 Full post-patch gate

```bash
cd /home/claude/carrent2
python3 build.py dist --strict
python3 scripts/seo_audit.py dist                          # must stay 0 ERROR
test ! -e dist/assets/analytics.js && ! grep -rq 'assets/analytics.js' dist --include=*.html && echo "T-01 ok"
python3 -c "import re,glob;from pathlib import Path;d={m for f in glob.glob('dist/sitemaps/*.xml') for m in re.findall(r'<lastmod>([^<]+)',Path(f).read_text())};print('T-02',len(d),'distinct lastmods'); assert len(d)>1"
for l in '' ka/ ru/ fa/ he/ ar/; do for d in attractions routes regions; do test -f "dist/$l$d/index.html" || echo "T-04 MISSING /$l$d/"; done; done
python3 -c "import pathlib;n=pathlib.Path('dist/index.html').read_text().lower().find('</head>');print('T-05 head bytes',n); assert n<12000"
```

### 3.2 Live host probe

```bash
for u in http://rentup.ge/ https://www.rentup.ge/ https://rentup.ge/ \
         https://rentup.ge/robots.txt https://rentup.ge/sitemap.xml \
         https://rentup.ge/sitemaps/attractions.xml https://rentup.ge/attractions/ \
         https://rentup.ge/assets/analytics.js https://rentup.ge/fleet ; do
  printf '%-52s ' "$u"
  curl -so /dev/null -m 20 -w '%{http_code} %{redirect_url}\n' "$u"
done
```

Baseline captured 2026-08-29: `http→https` 301 ok, `www→apex` 301 ok, apex 200, `robots.txt` 200 `text/plain`, `sitemap.xml` 200, `/sitemaps/*.xml` **404 (old build — expected to become 200 next deploy)**, `/attractions/` **404**, `/assets/analytics.js` **404**, `/fleet` → 301 `/fleet/`.

### 3.3 Click-depth / orphan check (T-10)

```python
import sys, collections as C
from pathlib import Path
from collections import deque
sys.path.insert(0, 'scripts'); import seo_audit as S
pages = S.crawl(Path('dist'))
g = C.defaultdict(set); inbound = C.Counter()
for p, d in pages.items():
    for h in d.anchors:
        t = h.split('#')[0].split('?')[0]
        if t in pages and t != p:
            g[p].add(t); inbound[t] += 1
depth = {'/': 0}; q = deque(['/'])
while q:
    u = q.popleft()
    for v in g[u]:
        if v not in depth: depth[v] = depth[u] + 1; q.append(v)
print('orphans (indexable):', [p for p in pages if not inbound[p] and not S.is_noindex(pages[p].robots)])
print('unreachable (indexable):', sum(1 for p in pages if p not in depth and not S.is_noindex(pages[p].robots)))
print('depth histogram:', sorted(C.Counter(depth.values()).items()))
print('indexable at depth>=4:', sum(1 for p in pages if depth.get(p, 99) >= 4 and not S.is_noindex(pages[p].robots)))
```

Baseline 2026-08-29: 0 indexable orphans, 0 unreachable, `[(0,1),(1,25),(2,184),(3,552),(4,748),(5,466),(6,130)]`, **1,344** indexable at depth ≥ 4.

### 3.4 Near-duplicate watch (T-19)

```python
import re, itertools, glob
from pathlib import Path
TAG = re.compile(r'<(script|style)[^>]*>.*?</\1>|<[^>]+>', re.S)
def sh(f, n=8):
    w = re.sub(r'\s+', ' ', TAG.sub(' ', Path(f).read_text().split('<body', 1)[-1])).split()
    return {tuple(w[i:i+n]) for i in range(len(w)-n+1)}
for label, pat in (('routes', 'dist/routes/*/index.html'),
                   ('attractions', 'dist/attractions/*/index.html'),
                   ('car-rental', 'dist/car-rental/*/index.html'),
                   ('fleet', 'dist/fleet/*/index.html')):
    fs = sorted(glob.glob(pat))[:24]; t = {f: sh(f) for f in fs}
    ov = sorted(len(t[a] & t[b]) / max(1, min(len(t[a]), len(t[b])))
                for a, b in itertools.combinations(fs, 2))
    print(f'{label:12s} n={len(fs):3d} median={ov[len(ov)//2]:.3f} max={ov[-1]:.3f}')
```

Baseline: routes 0.373 / 0.603 · attractions 0.246 / 0.522 · car-rental 0.229 / 0.383 · fleet 0.363 / 0.458.

---

## 4. Already covered by `scripts/seo_audit.py` — no action

These were re-verified against the current `dist/` and are correct. They are listed so nothing here is re-reported by another reviewer.

| Area | Status | Where it is enforced |
|---|---|---|
| Exactly one absolute, self-referencing (or documented-alias) canonical per page | Pass, 2,140 pages | `_check_canonical`, `seo_audit.py:385` |
| `<title>` present, unique within a language | Pass (247 WARNs are length-only, all RTL/Georgian titles > 70 chars) | `_check_titles:430` |
| `<meta name="description">` present on every indexable page | Pass | `_check_descriptions:459` |
| Exactly one `<h1>` per indexable page | Pass (20 INFOs are noindex-only) | `_check_h1:468` |
| No `<meta name="keywords">` | Pass | `_check_keywords:481` |
| hreflang: all 7 codes present, absolute, no duplicates, fully reciprocal, targets resolve to real files | Pass — **and** independently confirmed here: `x-default` === the `en` href on all 2,118 annotated pages; 0 indexable pages missing an hreflang cluster | `_check_hreflang:487` |
| Sitemap `<loc>` values all on-domain, all resolve to a real file, no duplicates | Pass, 2,100 URLs | `_check_sitemap:531` |
| Sitemap contains **no** noindex page | Pass — independently re-verified: all 40 noindex files are absent from all 8 children | `_check_sitemap:573` |
| Every indexable page appears in exactly one sitemap | Pass — independently re-verified: 2,100 / 2,100 | `_check_sitemap:580` |
| Sitemap index children all exist on disk | Pass, 8/8 | `_check_sitemap:543` |
| Guard lists: `/`, `/fleet/`, `/map/`, `/tours/`, `/car-rental/*`, `/routes/*`, `/attractions/*`, `/itineraries/*` indexable; `/trip/`, `/account/`, `/app/`, `/admin/*` noindex | Pass | `_check_guard_lists:606` |
| All JSON-LD parses as JSON | Pass, every block on all 2,140 pages | `_check_ld_json:634` |
| Every `BreadcrumbList` item resolves to a real on-site file | Pass | `_check_breadcrumbs:648` |
| Zero broken internal links | Pass | `_check_internal_links:673` |
| `robots.txt` has `Allow: /`, `Disallow: /admin/`, a `Sitemap:` line | Pass | `_check_robots_txt:689` |
| No legacy "Drive On" brand in any `<title>` | Pass | `_check_brand:708` |
| Every `<img>` has an `alt` attribute | Pass (alt *quality* is `SEO_PERFORMANCE.md` F6) | `_check_img_alt:719` |

Additionally verified in this review and found **clean — no finding, no action**:

- **Rendering.** All SEO-critical content is in the HTML source, not JS-injected. Sampled `/itineraries/georgia-7-days/` (27,412 B): `<h1>`, 5 `<h2>`, 7 `<h3>`, all six day-by-day headings present in the served bytes; corpus-wide `innerHTML` count on that template is 0. `/fleet/` renders `75 ₾` and per-car pricing in source. Attraction and route bodies are 580–880 words of server-rendered text.
- **Trailing-slash and URL hygiene.** 0 internal links without a trailing slash, 0 links to `/index.html`, 0 uppercase path segments, 0 double slashes, 0 canonicals not ending in `/`. Nothing to fix.
- **RTL delivery.** `dist/ar/`, `dist/he/`, `dist/fa/` all emit `<html lang="xx" dir="rtl">` correctly; the two `dir="ltr"` overrides per page are intentional (Latin-script inline runs).
- **Cross-language duplication.** Not machine-translated boilerplate: 8-gram overlap between each localised attraction page and its English source is **0.02–0.04** across a 6-slug sample × 5 languages, with Latin-character ratios of 0.04–0.07. Genuine per-language content.
- **Faceted / paginated URLs.** Only 24 faceted links exist site-wide (`/map/?interest={culture,food,cycling,hotel}` × 6 languages). They point at a page whose canonical is the bare `/map/`, they are not in any sitemap, and there is no pagination anywhere in the corpus. No crawl trap, no parameter-handling work needed.
- **JSON-LD placement.** Every block sits inside `<head>`, one `<script type="application/ld+json">` per page, no HTML entities and no `</script>` sequences inside the JSON. Delivery is correct — only its *size* is a problem (T-05).
- **Mixed content.** Zero `http://` subresources anywhere in `dist/`. External origins are limited to `fonts.googleapis.com`, `fonts.gstatic.com`, `commons.wikimedia.org`, `creativecommons.org`, `wa.me`, one `upload.wikimedia.org`, and `unpkg.com` (Decap CMS, inside the robots-disallowed `/admin/`).
- **`.nojekyll`** is present at `dist/.nojekyll`, so GitHub Pages serves `_`-prefixed paths and skips Jekyll. Correct.
- **404 status.** GitHub Pages returns a genuine `404` status with `dist/404.html`, not a soft 200. Correct (the page's *language* is T-11).
- **Host canonicalisation and HTTPS.** `http://rentup.ge/` → 301 → `https://rentup.ge/`; `https://www.rentup.ge/` → 301 → apex. HTTP/2, `vary: Accept-Encoding`, gzip on HTML (8,747 B for a 27 KB attraction page). Correct.

---

## 5. Suggested order of work

1. **T-01, T-03, T-08** — all three are regressions or gate-removals that ship with the next push to `main`. Fix before deploying.
2. **T-02** — invisible locally, wrong in production on 100% of URLs. One function plus one workflow line.
3. **T-04, T-05, T-06, T-07** — one afternoon together; T-04 and T-07 share the stub template, T-06 and T-07 share the noindex-page list.
4. **T-09, T-13** — hardening, no user-visible change today.
5. **T-10** — real hub pages; needs content, schedule it.
6. **T-11 … T-20** — batch into one hygiene commit.
