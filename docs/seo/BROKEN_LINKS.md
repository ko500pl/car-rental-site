# Broken Links Audit — rentup.ge

**Date:** 2026-08-29
**Scope:** the built tree at `dist/` (2,140 HTML pages, 4,725 files total), plus a live spot-check against https://rentup.ge
**Method:** filesystem resolution of every extracted reference, plus `curl` HTTP checks for external and live URLs. Every finding below was produced by a command reproduced in §6. Nothing here is inferred.

---

## 1. Summary counts

| Metric | Value |
|---|---|
| HTML pages in `dist/` | 2,140 |
| Files in `dist/` | 4,725 |
| References extracted (`<a href>`, `<link href>`, `<img src/srcset>`, `<script src>`, `<source src/srcset>`, `<video poster>`, `<iframe src>`, `<form action>`, `<meta content>` URLs, `<use href>`, CSS `url()`) | **164,910** |
| Internal references that resolve to a real file | **134,940** |
| **Internal references that do NOT resolve** | **2,911 occurrences / 91 unique paths** |
| — of which: missing script `/assets/analytics.js` | **2,125 occurrences on 2,125 pages** |
| — of which: missing photos | **786 occurrences / 88 unique files** (HTML only) |
| Additional missing-photo references inside `dist/data/**.json` (map + attraction feeds) | **672 occurrences / 88 unique / 390 JSON files** |
| Broken same-page fragments (`href="#..."` with no matching `id`) | **30 occurrences / 1 unique** (out of 2,148 fragment links) |
| Malformed absolute URL emitted into `og:image` | **6 occurrences / 1 unique** |
| Unique external URLs | **2,485** across **9 hosts**, 19,201 occurrences |
| External URLs that are dead | **1** (the malformed one above) |
| External URLs that 301-redirect | **7 unique / 5,394 occurrences** |
| External `http://` links that should be `https://` | **1 unique / 24 occurrences** |
| **Live URLs that this build would turn into 404s** | **162** (27 slugs × 6 languages) |
| New URLs this build adds that are 404 live today | 120 |

`scripts/seo_audit.py dist` was run for cross-check on the same tree: **0 ERROR, 247 WARN (title length), 20 INFO (h1)**. It reports none of the breakages below — it checks `<a href="/...">` page links only, and every page link in the build does resolve. Every finding in this report is in a category that audit does not cover.

---

## 2. Internal breakages

### 2.1 `/assets/analytics.js` — 2,125 pages load a script that does not exist

**Verified independently.** The prior review's "~2125 pages" figure is **exactly correct**: 2,125.

```
$ grep -rl "analytics.js" dist --include="*.html" | wc -l   # 2125
$ grep -ro "assets/analytics\.js" dist/ | wc -l             # 2125
$ ls static/analytics.js dist/assets/analytics.js
ls: cannot access 'static/analytics.js': No such file or directory
ls: cannot access 'dist/assets/analytics.js': No such file or directory
$ curl -o /dev/null -w '%{http_code}' https://rentup.ge/assets/analytics.js   # 404 (already live)
```

2,140 HTML pages − 15 exempt pages (3 × `admin/*.html`, 12 × `planner`/`pricing` alias pages) = **2,125**. Every one is a real 404 on production today, confirmed by the live curl above.

| Reference | Occurrences | Source files | Fix |
|---|---|---|---|
| `/assets/analytics.js` (root-relative) | 2,119 | 2,119 HTML pages, e.g. `dist/index.html:1776`, `dist/404.html`, `dist/community/index.html` | see below |
| `../assets/analytics.js` (relative) | 1 | `dist/business-card/index.html:59` | same |
| `../../assets/analytics.js` (relative) | 5 | `dist/{ka,ru,fa,he,ar}/business-card/index.html` | same |

**Root cause — `build.py`:**

- `build.py:715` — `ASSET` seeds `"analytics": "/assets/analytics.js"`.
- `build.py:723` — `analytics_html()` emits `<script defer src="{ASSET.get("analytics", "/assets/analytics.js")}">` on every page.
- `build.py:4455` — `analytics.js` is listed in `hashed_sources`, so the plain `static/` → `dist/assets/` copytree **skips** it.
- `build.py:4480-4483` — the hashing loop only writes it `if os.path.exists(p)`, and `static/analytics.js` **does not exist**, so `ASSET["analytics"]` is never rewritten to a hashed name and no file is ever emitted.

The `if os.path.exists(p)` guard silently swallows the missing source, so the build exits 0 with a 404 script tag on 2,125 pages.

**Exact fix — pick one:**

1. **Create `static/analytics.js`.** `analytics_html()` (`build.py:721`) already sets `window.FH_ANALYTICS_CONFIG = {"measurementId": ...}` and its docstring says "Empty IDs intentionally produce a client-side no-op" — so the missing file is the intended consumer of that config. Adding it makes the existing hashing path work with no build change.
2. **Or make the emission conditional.** At `build.py:723`, emit the tag only when the asset was actually written — and drop the `"analytics"` default from the `ASSET` dict at `build.py:715` so its presence in `ASSET` is proof the file exists:
   ```python
   src = ASSET.get("analytics")
   tag = f'\n<script defer src="{src}"></script>' if src else ""
   return f'<script>window.FH_ANALYTICS_CONFIG={{"measurementId":{J(measurement_id)}}};</script>' + tag
   ```
3. **Add a build guard** so this class of bug fails loudly: after the `write_hashed` loop at `build.py:4480`, assert that every name in `hashed_sources` a page can reference exists on disk.

### 2.2 Missing attraction photos — 88 files, 786 HTML + 672 JSON occurrences

Every one of these is referenced from `content/attractions/*.yml` but is absent from `static/photos/` (883 files) and therefore from `dist/assets/photos/` (883 files — the two directories are identical, `diff` is empty).

**This is a regression, not a legacy gap.** All 11 sampled paths return **200 on the live site today**:

```
$ curl -o /dev/null -w '%{http_code}' https://rentup.ge/assets/photos/dry-bridge-market.jpg   # 200
… same for poka-nunnery.jpg, nodar-dumbadze-house-museum.jpg, sameba-jikheti-monastery-summer.jpg,
  tmogvi-fortress.jpg, telefisi-fortress.jpg, zando-st-george-monastery.jpg,
  takhti-tepha-mud-volcanoes-2.webp, abano-pass-1.webp, geguti-palace-3.webp,
  vashlovani-national-park-1.webp   → all 200
```

So the source files were removed from `static/photos/` (most look like a `.jpg` → `-N.webp` re-encode) without updating the YAML that points at them. Deploying this build breaks 88 images that currently work.

**8 of the 88 are also the page's `og:image`**, so the social/preview card 404s too — marked **+og:image** below. Those 8 sit on `image:` at line 9 of the YAML (page hero *and* og) and again under `gallery:`; the rest are gallery-only.

The same 88 paths are also baked into 390 files under `dist/data/` (`points-<lang>.json` and `data/attr/<lang>/<slug>.json`), which feed the map and attraction explorer — 672 further broken image requests at runtime.

| Missing file | Occurrences (HTML) | Referenced at | Fix |
|---|---|---|---|
| `/assets/photos/dry-bridge-market.jpg` **+og:image** | 60 | `content/attractions/dry-bridge-market.yml:9; content/attractions/dry-bridge-market.yml:16` | point at `dry-bridge-market-1.webp` (also available: dry-bridge-market-2.webp, dry-bridge-market-3.webp) |
| `/assets/photos/nodar-dumbadze-house-museum.jpg` **+og:image** | 42 | `content/attractions/nodar-dumbadze-house-museum.yml:9; content/attractions/nodar-dumbadze-house-museum.yml:16` | **no sibling file exists — re-source the image** |
| `/assets/photos/poka-nunnery.jpg` **+og:image** | 42 | `content/attractions/poka-nunnery.yml:9; content/attractions/poka-nunnery.yml:16` | point at `poka-nunnery-1.webp` (also available: poka-nunnery-2.webp, poka-nunnery-3.webp) |
| `/assets/photos/sameba-jikheti-monastery-summer.jpg` **+og:image** | 42 | `content/attractions/sameba-jikheti-monastery.yml:9; content/attractions/sameba-jikheti-monastery.yml:16` | **no sibling file exists — re-source the image** |
| `/assets/photos/takhti-tepha-mud-volcanoes-2.webp` **+og:image** | 30 | `content/attractions/takhti-tepha-mud-volcanoes.yml:9; content/attractions/takhti-tepha-mud-volcanoes.yml:16` | point at `takhti-tepha-mud-volcanoes-1.webp` |
| `/assets/photos/telefisi-fortress.jpg` **+og:image** | 30 | `content/attractions/telefisi-fortress.yml:9; content/attractions/telefisi-fortress.yml:16` | **no sibling file exists — re-source the image** |
| `/assets/photos/tmogvi-fortress.jpg` **+og:image** | 30 | `content/attractions/tmogvi-fortress.yml:9; content/attractions/tmogvi-fortress.yml:16` | point at `tmogvi-fortress-1.webp` (also available: tmogvi-fortress-2.webp, tmogvi-fortress-3.webp) |
| `/assets/photos/zando-st-george-monastery.jpg` **+og:image** | 30 | `content/attractions/zando-st-george-monastery.yml:9; content/attractions/zando-st-george-monastery.yml:16` | **no sibling file exists — re-source the image** |
| `/assets/photos/abano-pass-1.webp` | 6 | `content/attractions/abano-pass.yml:11` | point at `abano-pass.webp` |
| `/assets/photos/abano-pass-2.webp` | 6 | `content/attractions/abano-pass.yml:16` | point at `abano-pass.webp` |
| `/assets/photos/abano-pass-3.webp` | 6 | `content/attractions/abano-pass.yml:21` | point at `abano-pass.webp` |
| `/assets/photos/ajameti-managed-reserve-1.webp` | 6 | `content/attractions/ajameti-managed-reserve.yml:11` | point at `ajameti-managed-reserve.webp` |
| `/assets/photos/ateni-sioni-church-1.webp` | 6 | `content/attractions/ateni-sioni-church.yml:11` | point at `ateni-sioni-church.webp` |
| `/assets/photos/ateni-sioni-church-2.webp` | 6 | `content/attractions/ateni-sioni-church.yml:16` | point at `ateni-sioni-church.webp` |
| `/assets/photos/ateni-sioni-church-3.webp` | 6 | `content/attractions/ateni-sioni-church.yml:21` | point at `ateni-sioni-church.webp` |
| `/assets/photos/bazaleti-lake-3.webp` | 6 | `content/attractions/bazaleti-lake.yml:21` | point at `bazaleti-lake-1.webp` (also available: bazaleti-lake-2.webp, bazaleti-lake.webp) |
| `/assets/photos/becho-mazeri-2.webp` | 6 | `content/attractions/becho-mazeri.yml:16` | point at `becho-mazeri-1.webp` (also available: becho-mazeri.webp) |
| `/assets/photos/bolnisi-sioni-1.webp` | 6 | `content/attractions/bolnisi-sioni.yml:11` | point at `bolnisi-sioni.webp` |
| `/assets/photos/bolnisi-sioni-2.webp` | 6 | `content/attractions/bolnisi-sioni.yml:16` | point at `bolnisi-sioni.webp` |
| `/assets/photos/bolnisi-sioni-3.webp` | 6 | `content/attractions/bolnisi-sioni.yml:21` | point at `bolnisi-sioni.webp` |
| `/assets/photos/bolnisi-town-2.webp` | 6 | `content/attractions/bolnisi-town.yml:16` | point at `bolnisi-town-1.webp` (also available: bolnisi-town.webp) |
| `/assets/photos/bolnisi-town-3.webp` | 6 | `content/attractions/bolnisi-town.yml:22` | point at `bolnisi-town-1.webp` (also available: bolnisi-town.webp) |
| `/assets/photos/borjomi-central-park-3.webp` | 6 | `content/attractions/borjomi-central-park.yml:23` | point at `borjomi-central-park-1.webp` (also available: borjomi-central-park-2.webp, borjomi-central-park.webp) |
| `/assets/photos/bridge-of-peace-rike-park-2.webp` | 6 | `content/attractions/bridge-of-peace-rike-park.yml:16` | point at `bridge-of-peace-rike-park-1.webp` (also available: bridge-of-peace-rike-park.webp) |
| `/assets/photos/bridge-of-peace-rike-park-3.webp` | 6 | `content/attractions/bridge-of-peace-rike-park.yml:21` | point at `bridge-of-peace-rike-park-1.webp` (also available: bridge-of-peace-rike-park.webp) |
| `/assets/photos/chateau-mukhrani-3.webp` | 6 | `content/attractions/chateau-mukhrani.yml:21` | point at `chateau-mukhrani-1.webp` (also available: chateau-mukhrani-2.webp, chateau-mukhrani.webp) |
| `/assets/photos/dariali-gorge-gveleti-waterfalls-3.webp` | 6 | `content/attractions/dariali-gorge-gveleti-waterfalls.yml:22` | point at `dariali-gorge-gveleti-waterfalls-1.webp` (also available: dariali-gorge-gveleti-waterfalls-2.webp, dariali-gorge-gveleti-waterfalls.webp) |
| `/assets/photos/dartlo-1.webp` | 6 | `content/attractions/dartlo.yml:11` | point at `dartlo.webp` |
| `/assets/photos/dartlo-2.webp` | 6 | `content/attractions/dartlo.yml:16` | point at `dartlo.webp` |
| `/assets/photos/dartlo-3.webp` | 6 | `content/attractions/dartlo.yml:21` | point at `dartlo.webp` |
| `/assets/photos/freedom-square-old-parliament-2.webp` | 6 | `content/attractions/freedom-square-old-parliament.yml:16` | point at `freedom-square-old-parliament-1.webp` (also available: freedom-square-old-parliament.webp) |
| `/assets/photos/freedom-square-old-parliament-3.webp` | 6 | `content/attractions/freedom-square-old-parliament.yml:21` | point at `freedom-square-old-parliament-1.webp` (also available: freedom-square-old-parliament.webp) |
| `/assets/photos/geguti-palace-1.webp` | 6 | `content/attractions/geguti-palace.yml:11` | point at `geguti-palace.webp` |
| `/assets/photos/geguti-palace-2.webp` | 6 | `content/attractions/geguti-palace.yml:16` | point at `geguti-palace.webp` |
| `/assets/photos/geguti-palace-3.webp` | 6 | `content/attractions/geguti-palace.yml:21` | point at `geguti-palace.webp` |
| `/assets/photos/jumati-monastery-2.webp` | 6 | `content/attractions/jumati-monastery.yml:16` | point at `jumati-monastery-1.webp` (also available: jumati-monastery.webp) |
| `/assets/photos/khada-valley-1.webp` | 6 | `content/attractions/khada-valley.yml:11` | point at `khada-valley.webp` |
| `/assets/photos/khertvisi-fortress-2.webp` | 6 | `content/attractions/khertvisi-fortress.yml:16` | point at `khertvisi-fortress-1.webp` (also available: khertvisi-fortress.webp) |
| `/assets/photos/khertvisi-fortress-3.webp` | 6 | `content/attractions/khertvisi-fortress.yml:21` | point at `khertvisi-fortress-1.webp` (also available: khertvisi-fortress.webp) |
| `/assets/photos/khikhani-fortress-1.webp` | 6 | `content/attractions/khikhani-fortress.yml:11` | point at `khikhani-fortress.webp` |
| `/assets/photos/khikhani-fortress-2.webp` | 6 | `content/attractions/khikhani-fortress.yml:16` | point at `khikhani-fortress.webp` |
| `/assets/photos/khikhani-fortress-3.webp` | 6 | `content/attractions/khikhani-fortress.yml:21` | point at `khikhani-fortress.webp` |
| `/assets/photos/kintrishi-protected-areas-1.webp` | 6 | `content/attractions/kintrishi-protected-areas.yml:11` | point at `kintrishi-protected-areas.webp` |
| `/assets/photos/kintrishi-protected-areas-2.webp` | 6 | `content/attractions/kintrishi-protected-areas.yml:16` | point at `kintrishi-protected-areas.webp` |
| `/assets/photos/kobuleti-3.webp` | 6 | `content/attractions/kobuleti.yml:21` | point at `kobuleti-1.webp` (also available: kobuleti-2.webp, kobuleti.webp) |
| `/assets/photos/koruldi-lakes-3.webp` | 6 | `content/attractions/koruldi-lakes.yml:22` | point at `koruldi-lakes-1.webp` (also available: koruldi-lakes-2.webp, koruldi-lakes.webp) |
| `/assets/photos/kumisi-lake-2.webp` | 6 | `content/attractions/kumisi-lake.yml:16` | point at `kumisi-lake-1.webp` (also available: kumisi-lake.webp) |
| `/assets/photos/kumisi-lake-3.webp` | 6 | `content/attractions/kumisi-lake.yml:21` | point at `kumisi-lake-1.webp` (also available: kumisi-lake.webp) |
| `/assets/photos/lentekhi-3.webp` | 6 | `content/attractions/lentekhi.yml:21` | point at `lentekhi-1.webp` (also available: lentekhi-2.webp, lentekhi.webp) |
| `/assets/photos/likhauri-church-3.webp` | 6 | `content/attractions/likhauri-church.yml:21` | point at `likhauri-church-1.webp` (also available: likhauri-church-2.webp, likhauri-church.webp) |
| `/assets/photos/lomisa-church-3.webp` | 6 | `content/attractions/lomisa-church.yml:21` | point at `lomisa-church-1.webp` (also available: lomisa-church-2.webp, lomisa-church.webp) |
| `/assets/photos/manglisi-cathedral-3.webp` | 6 | `content/attractions/manglisi-cathedral.yml:21` | point at `manglisi-cathedral-1.webp` (also available: manglisi-cathedral-2.webp, manglisi-cathedral.webp) |
| `/assets/photos/martvili-canyon-2.webp` | 6 | `content/attractions/martvili-canyon.yml:16` | point at `martvili-canyon-1.webp` (also available: martvili-canyon.webp) |
| `/assets/photos/martvili-canyon-3.webp` | 6 | `content/attractions/martvili-canyon.yml:21` | point at `martvili-canyon-1.webp` (also available: martvili-canyon.webp) |
| `/assets/photos/metekhi-church-3.webp` | 6 | `content/attractions/metekhi-church.yml:22` | point at `metekhi-church-1.webp` (also available: metekhi-church-2.webp, metekhi-church.webp) |
| `/assets/photos/modinakhe-fortress-3.webp` | 6 | `content/attractions/modinakhe-fortress.yml:22` | point at `modinakhe-fortress-1.webp` (also available: modinakhe-fortress-2.webp, modinakhe-fortress.webp) |
| `/assets/photos/mount-khvamli-2.webp` | 6 | `content/attractions/mount-khvamli.yml:16` | point at `mount-khvamli-1.webp` (also available: mount-khvamli.webp) |
| `/assets/photos/mount-khvamli-3.webp` | 6 | `content/attractions/mount-khvamli.yml:21` | point at `mount-khvamli-1.webp` (also available: mount-khvamli.webp) |
| `/assets/photos/nabeghlavi-2.webp` | 6 | `content/attractions/nabeghlavi.yml:16` | point at `nabeghlavi-1.webp` (also available: nabeghlavi.webp) |
| `/assets/photos/nabeghlavi-3.webp` | 6 | `content/attractions/nabeghlavi.yml:21` | point at `nabeghlavi-1.webp` (also available: nabeghlavi.webp) |
| `/assets/photos/napareuli-2.webp` | 6 | `content/attractions/napareuli.yml:16` | point at `napareuli-1.webp` (also available: napareuli.webp) |
| `/assets/photos/napareuli-3.webp` | 6 | `content/attractions/napareuli.yml:21` | point at `napareuli-1.webp` (also available: napareuli.webp) |
| `/assets/photos/navenakhevi-cave-1.webp` | 6 | `content/attractions/navenakhevi-cave.yml:11` | point at `navenakhevi-cave.webp` |
| `/assets/photos/navenakhevi-cave-2.webp` | 6 | `content/attractions/navenakhevi-cave.yml:17` | point at `navenakhevi-cave.webp` |
| `/assets/photos/okatse-canyon-3.webp` | 6 | `content/attractions/okatse-canyon.yml:21` | point at `okatse-canyon-1.webp` (also available: okatse-canyon-2.webp, okatse-canyon.webp) |
| `/assets/photos/oniore-waterfall-3.webp` | 6 | `content/attractions/oniore-waterfall.yml:21` | point at `oniore-waterfall-1.webp` (also available: oniore-waterfall-2.webp, oniore-waterfall.webp) |
| `/assets/photos/pankisi-gorge-3.webp` | 6 | `content/attractions/pankisi-gorge.yml:21` | point at `pankisi-gorge-1.webp` (also available: pankisi-gorge-2.webp, pankisi-gorge.webp) |
| `/assets/photos/poti-3.webp` | 6 | `content/attractions/poti.yml:23` | point at `poti-1.webp` (also available: poti-2.webp, poti.webp) |
| `/assets/photos/ruisi-cathedral-3.webp` | 6 | `content/attractions/ruisi-cathedral.yml:21` | point at `ruisi-cathedral-1.webp` (also available: ruisi-cathedral-2.webp, ruisi-cathedral.webp) |
| `/assets/photos/rukhi-fortress-3.webp` | 6 | `content/attractions/rukhi-fortress.yml:21` | point at `rukhi-fortress-1.webp` (also available: rukhi-fortress-2.webp, rukhi-fortress.webp) |
| `/assets/photos/sairme-resort-1.webp` | 6 | `content/attractions/sairme-resort.yml:11` | point at `sairme-resort.webp` |
| `/assets/photos/sairme-resort-2.webp` | 6 | `content/attractions/sairme-resort.yml:16` | point at `sairme-resort.webp` |
| `/assets/photos/sairme-resort-3.webp` | 6 | `content/attractions/sairme-resort.yml:21` | point at `sairme-resort.webp` |
| `/assets/photos/sameba-jikheti-monastery-3.jpg` | 6 | `content/attractions/sameba-jikheti-monastery.yml:26` | **no sibling file exists — re-source the image** |
| `/assets/photos/sameba-jikheti-monastery-7.jpg` | 6 | `content/attractions/sameba-jikheti-monastery.yml:21` | **no sibling file exists — re-source the image** |
| `/assets/photos/samtavisi-cathedral-3.webp` | 6 | `content/attractions/samtavisi-cathedral.yml:21` | point at `samtavisi-cathedral-1.webp` (also available: samtavisi-cathedral-2.webp, samtavisi-cathedral.webp) |
| `/assets/photos/skhvitori-akaki-tsereteli-museum-3.webp` | 6 | `content/attractions/skhvitori-akaki-tsereteli-museum.yml:23` | point at `skhvitori-akaki-tsereteli-museum-1.webp` (also available: skhvitori-akaki-tsereteli-museum-2.webp, skhvitori-akaki-tsereteli-museum.webp) |
| `/assets/photos/svaneti-museum-mestia-3.webp` | 6 | `content/attractions/svaneti-museum-mestia.yml:21` | point at `svaneti-museum-mestia-1.webp` (also available: svaneti-museum-mestia-2.webp, svaneti-museum-mestia.webp) |
| `/assets/photos/tbilisi-botanical-garden-3.webp` | 6 | `content/attractions/tbilisi-botanical-garden.yml:23` | point at `tbilisi-botanical-garden-1.webp` (also available: tbilisi-botanical-garden-2.webp, tbilisi-botanical-garden.webp) |
| `/assets/photos/tobavarchkhili-lakes-1.webp` | 6 | `content/attractions/tobavarchkhili-lakes.yml:11` | point at `tobavarchkhili-lakes.webp` |
| `/assets/photos/truso-valley-3.webp` | 6 | `content/attractions/truso-valley.yml:21` | point at `truso-valley-1.webp` (also available: truso-valley-2.webp, truso-valley.webp) |
| `/assets/photos/tsinandali-estate-3.webp` | 6 | `content/attractions/tsinandali-estate.yml:21` | point at `tsinandali-estate-1.webp` (also available: tsinandali-estate-2.webp, tsinandali-estate.webp) |
| `/assets/photos/tsughrughasheni-church-3.webp` | 6 | `content/attractions/tsughrughasheni-church.yml:21` | point at `tsughrughasheni-church-1.webp` (also available: tsughrughasheni-church-2.webp, tsughrughasheni-church.webp) |
| `/assets/photos/turtle-lake-vake-park-3.webp` | 6 | `content/attractions/turtle-lake-vake-park.yml:21` | point at `turtle-lake-vake-park-1.webp` (also available: turtle-lake-vake-park-2.webp, turtle-lake-vake-park.webp) |
| `/assets/photos/vani-archaeological-museum-3.webp` | 6 | `content/attractions/vani-archaeological-museum.yml:22` | point at `vani-archaeological-museum-1.webp` (also available: vani-archaeological-museum-2.webp, vani-archaeological-museum.webp) |
| `/assets/photos/vashlovani-national-park-1.webp` | 6 | `content/attractions/vashlovani-national-park.yml:11` | point at `vashlovani-national-park.webp` |
| `/assets/photos/vashlovani-national-park-2.webp` | 6 | `content/attractions/vashlovani-national-park.yml:16` | point at `vashlovani-national-park.webp` |
| `/assets/photos/vashlovani-national-park-3.webp` | 6 | `content/attractions/vashlovani-national-park.yml:21` | point at `vashlovani-national-park.webp` |

**Fix mechanics:** these are content-data errors, not build-code errors — edit the `image:` values in `content/attractions/*.yml` at the lines above to name a file that exists in `static/photos/`. Six of them have no sibling on disk at all (`nodar-dumbadze-house-museum.jpg`, `sameba-jikheti-monastery-summer.jpg`, `sameba-jikheti-monastery-3.jpg`, `sameba-jikheti-monastery-7.jpg`, `telefisi-fortress.jpg`, `zando-st-george-monastery.jpg`) — those must be re-sourced or the gallery entry removed. Do **not** leave the YAML pointing at a name that exists only on the old deploy.

**Also add a build guard.** The build already has a `--strict` publication gate (used by `netlify.toml`, and worth adding to the Pages workflow). Extend it: every `image:` in `content/**` must resolve under `static/`, or the build fails. Without that, the next photo rename repeats this silently.

### 2.3 Broken same-page fragment — `href="#planner"` on all 6 home pages

Out of **2,148** fragment links in the build, **exactly one** target does not exist: `#planner` on the language home pages — 5 links per page × 6 languages = **30 occurrences**.

| Fragment | Occurrences | Source files | Why it is broken |
|---|---|---|---|
| `#planner` | 30 | `dist/index.html:1808` (×5) and `dist/{ka,ru,fa,he,ar}/index.html` | No element with `id="planner"` exists on any home page. `id="planner"` exists only on the 6 `/…/map/` pages. |

These links carry `data-open-standard-tour`, so the intent is a JS handler. But that handler lives only in `planner.js` and `workspace.js`, and the home page loads **only** `analytics.js` (broken), `auth.js`, `booking.js` and `app.js`:

```
$ grep -o '<script[^>]*src="[^"]*"' dist/index.html
<script defer src="/assets/analytics.js"
<script type="module" src="/assets/auth.86352f60c6.js"
<script type="module" src="/assets/booking.182c74370a.js"
<script defer src="/assets/app.500610917e.js"
$ grep -l "open-standard-tour" dist/assets/*.js
dist/assets/planner.dade8ecc52.js
dist/assets/workspace.f2e83fa2d5.js
```

Nothing intercepts the click. "See all tours" and every tour card's "Plan" button appends `#planner` to the URL and does nothing.

**Exact fix — `build.py:1119` and `build.py:1123`.** Both hardcode a bare fragment; every other planner link in the file (`build.py:818, 866, 915, 1809, 3189, 3902, 4052, 4509`) already uses the correct absolute form:

```python
# build.py:1119
f'<a class="btn sm ghost" href="#planner" data-open-standard-tour data-tour="{E(slug)}">…'
# →
f'<a class="btn sm ghost" href="{page_url(lang, "map", False)}#planner" data-open-standard-tour data-tour="{E(slug)}">…'

# build.py:1123
f'<a class="btn ghost" href="#planner" data-open-standard-tour>…'
# →
f'<a class="btn ghost" href="{page_url(lang, "map", False)}#planner" data-open-standard-tour>…'
```

This also makes the links work with JS off, and matches the home page's own "Plan your own trip" card, which already uses `href="/map/#planner"`.

### 2.4 Malformed `og:image` — `https://rentup.gehttps://upload.wikimedia.org/...`

| Bad URL | Occurrences | Source files | Status |
|---|---|---|---|
| `https://rentup.gehttps://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Georgiaren_Kronikak_…jpg` | 6 | `dist/attractions/chronicle-of-georgia/index.html` and the `ka/ru/fa/he/ar` mirrors | `curl` → `000` (host `rentup.gehttps:` does not resolve) |

`content/attractions/chronicle-of-georgia.yml:9` sets `image:` to a full `https://upload.wikimedia.org/...` URL (that URL itself is fine — verified 200). But `build.py:2213` prepends `SITE_URL` unconditionally:

```python
image=(SITE_URL + a["image"]) if a.get("image") else None)
```

**Exact fix — `build.py:2213`**, matching the guard already used at `build.py:1386` and `build.py:1473`:

```python
image=(SITE_URL + a["image"]) if a.get("image", "").startswith("/") else (a.get("image") or None))
```

That same line is why the 8 `og:image` entries in §2.2 also 404.

### 2.5 Categories checked and found clean

Stated explicitly so coverage is auditable — these are the categories `scripts/seo_audit.py` does *not* check, each resolved against the built tree.

| Category | Occurrences in `dist/` | Broken |
|---|---|---|
| `<link rel="icon">` → `/favicon.svg`, `../favicon.svg`, `../../favicon.svg` | 2,126 | 0 — `dist/favicon.svg` exists (430 B) |
| `<link rel="apple-touch-icon">` → `/assets/app-icon-180.png` (+ relative forms) | 2,124 | 0 — file exists (7,619 B) |
| `<link rel="manifest">` → `/assets/manifest.webmanifest` | 2,124 | 0 — file exists |
| Manifest icon/shortcut targets (`app-icon-192/512/maskable-512.png`, `/app/`, `/fleet/`, `/map/#planner`, `/account/`) | 6 | 0 — all resolve |
| `static/sw.js` `CORE` precache list (`/assets/manifest.webmanifest`, `/assets/app-icon-192.png`, `/assets/app-icon-512.png`) and its `caches.match("/")` fallback | 4 | 0 — all resolve, so `cache.addAll(CORE)` will not reject at install |
| `admin/index.html` → `../assets/do-logo-tight.png`, `../index.html`, `cms.html#/...`, `bookings.html` | 16 | 0 |
| `admin/bookings.html` → `/assets/style.094cdcf85b.css`, `/assets/admin-bookings.e92edcdd57.js` | 2 | 0 |
| `admin/cms.html` → `./`, `/favicon.svg` | 2 | 0 |
| CSS `url()` — 17 across 6 files (`style.css`, hashed `style.*.css`, `leaflet.css`) | 17 | 0 — `/assets/rentup-planner-hero.jpg`, `/assets/georgia-id-security-bg.webp`, relative `georgian-heritage-watermark.webp`, `leaflet/layers*.png`, `marker-icon.png`, plus `data:` and `url(#default#VML)` |
| `<script src>` other than analytics (hashed `app`, `auth`, `booking`, `explorer`, `planner`, `workspace`, `trip`, `app-mobile`, `travel-<lang>`, `admin-bookings`, `leaflet`) | 5,000+ | 0 |
| `<a href="/...">` page links | 100,000+ | 0 (matches `seo_audit.py`) |
| `srcset`, `<source>`, `<video poster>`, `<iframe src>`, `rel="preload"`, `rel="prefetch"` | **0 in the build** | n/a — the generator emits none of these, so there is nothing to break |
| `/uploads/**` (Decap `public_folder: /uploads`, `admin/config.yml:24`) | 0 references | Not broken today, but **latent**: `static/uploads/` does not exist and `build.py:4491` copies it only `if os.path.isdir(up)`. The first image an editor uploads through the CMS is written as `/uploads/<name>` and will 404 until that directory is committed. |

Two dead-weight files, not broken but unreferenced: `dist/assets/workspace.js` and `dist/assets/sw.js` are plain copies that **no page requests** (0 references each) — pages link the hashed `workspace.f2e83fa2d5.js` and the root `/sw.js`. `build.py:4455`'s `hashed_sources` omits `workspace.js`, and `sw.js` is copied twice (`static/` → `dist/assets/` by the copytree, then `build.py:4497` → `dist/sw.js`). Adding `workspace.js` and `sw.js` to `hashed_sources` removes both.

---

## 3. External links

2,485 unique URLs / 19,201 occurrences across **9 hosts**. Every unique URL on 7 of the 9 hosts was checked; the two high-cardinality hosts were handled as noted.

| Host | Unique URLs | Occurrences | Checked | Result |
|---|---|---|---|---|
| `commons.wikimedia.org` | 918 | 5,790 | **all 918** | **all 200.** First pass: 813 × 200 + 105 × 429 (rate-limit); all 105 re-checked at lower concurrency → 200. |
| `creativecommons.org` | 7 | 5,394 | all 7 | **all 200, all after a 301** — see below |
| `fonts.googleapis.com` | 5 | 4,248 | all 5 | 4 stylesheet URLs 200; the bare origin is `rel="preconnect"` only |
| `fonts.gstatic.com` | 1 | 2,124 | 1 | `rel="preconnect"` only |
| `wa.me` | 1,548 | 1,548 | 40 random samples | **all 200** (302 → `api.whatsapp.com/send/?phone=995597555565&…`). All 1,548 share one host and one phone number and differ only in the `?text=` payload, which WhatsApp does not use for routing, so the sample generalises. |
| `www.samtredia.gov.ge` | 3 | 48 | all 3 | all 200 |
| `upload.wikimedia.org` | 1 | 42 | 1 | 200 |
| `rentup.gehttps:` | 1 | 6 | 1 | **DEAD — see §2.4** |
| `unpkg.com` | 1 | 1 | 1 | 200 after 302 |

### Issues

| Issue | URL | Occurrences | Source | Fix |
|---|---|---|---|---|
| **Dead** | `https://rentup.gehttps://upload.wikimedia.org/…` | 6 | `og:image` on `chronicle-of-georgia` × 6 langs | `build.py:2213` — see §2.4 |
| **`http://` should be `https://`** | `http://creativecommons.org/publicdomain/zero/1.0/deed.en` | 24 | `image_credit` license links on `pankisi-gorge`, `zhinvali-reservoir`, `gudauri` (× 6 langs each) | 301s to `https://…`. Change the license URL in those `content/attractions/*.yml` to `https://`. |
| **301 on every attraction page** | `https://creativecommons.org/licenses/by-sa/4.0` → `…/4.0/` | 2,280 | attraction galleries | append the trailing slash |
| 301 | `…/licenses/by-sa/3.0` → `…/3.0/` | 1,326 | attraction galleries | add `/` |
| 301 | `…/licenses/by-sa/2.0` → `…/2.0/` | 618 | attraction galleries | add `/` |
| 301 | `…/licenses/by/3.0` → `…/3.0/` | 486 | attraction galleries | add `/` |
| 301 | `…/licenses/by/2.0` → `…/2.0/` | 414 | attraction galleries | add `/` |
| 301 | `…/licenses/by/4.0` → `…/4.0/` | 246 | attraction galleries | add `/` |

The 6 CC license redirects total **5,370 occurrences** and are one hop each — harmless for users, but they are the single most-repeated outbound link on the site and cost a redirect on every gallery render. The URLs are derived from the `license:` string in each `content/attractions/*.yml` gallery entry (e.g. `CC BY-SA 4.0`), so the mapping table that turns `CC BY-SA 4.0` into a URL is the one place to add the trailing slash.

| Note (not broken) | Detail |
|---|---|
| `fonts.googleapis.com` / `fonts.gstatic.com` bare origins return 404 to a GET | They appear **only** as `rel="preconnect"`, which opens a TCP/TLS connection and never requests `/`. Not a broken link — recorded so a future crawler report can be dismissed. |
| `https://unpkg.com/decap-cms@^3.8.4/dist/decap-cms.js` (`dist/admin/cms.html`) | Resolves 200 via 302 → `decap-cms@3.15.1`. The `^3.8.4` range floats, so the admin UI silently picks up new minors. Not broken; pin an exact version if admin stability matters. |

---

## 4. Live vs. build diff

**The production site is running an older build.** Proof:

- Live `https://rentup.ge/sitemap.xml` is a flat `<urlset>` with **2,142** `<loc>` entries.
- The current build's `dist/sitemap.xml` is a `<sitemapindex>` pointing at 8 child sitemaps under `/sitemaps/`, which together hold **2,100** `<loc>` entries.
- `https://rentup.ge/sitemaps/attractions.xml` → **404** live.
- `https://rentup.ge/car-rental/tbilisi/` → **404**; `https://rentup.ge/itineraries/georgia-7-days/` → **404**; `https://rentup.ge/trip-planner/` → **404**. All three are in the current build.

### 4.1 Live-only URLs — deploying this build creates 162 new 404s

27 slugs (10 attractions + 17 routes) exist live in all 6 languages and are **absent from both `content/` and `dist/`**. **All 162 were checked with `curl`; all 162 returned 200.**

Inventory: live has 267 attraction slugs and 49 route slugs; the build has `content/attractions/*.yml` = **257** and `content/routes/*.yml` = **32**, matching `dist/attractions/*/` = 257 and `dist/routes/*/` = 32.

| Live URL (lang-stripped) | Type | Language mirrors | Live status | In `content/` | In `dist/` |
|---|---|---|---|---|---|
| `/attractions/abudelauri-lakes/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/artsivi-eagle-gorge/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/bateti-lake/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/bebris-tsikhe/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/betania-monastery/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/didgori-battle-memorial/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/gomismta/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/kojori-fortress/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/niko-nikoladze-house-museum/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/attractions/tbilisi-sea/` | attraction | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/batumi-coast-family-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/borjomi-spa-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/georgia-essential-five-days/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/gori-uplistsikhe-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/guria-coast-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/guria-mountain-spa-weekend/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/kakheti-cycling-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/kakheti-wine-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/kazbegi-mountain-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/kutaisi-monasteries-caves-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/kvemo-kartli-monasteries-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/lagodekhi-nature-weekend/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/martvili-nokalakevi-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/mtskheta-heritage-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/racha-family-weekend/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/racha-lechkhumi-heritage-three-days/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |
| `/routes/tbilisi-stage-and-museum-day/` | route | 6 (`ar, en, fa, he, ka, ru`) | 200 | absent | absent |

### 4.2 Build-only URLs — 120 new URLs (no action needed)

| Section | New URLs | Live status today |
|---|---|---|
| `/car-rental/` hub + 10 city/class landing pages × 6 langs | 66 | 404 (genuinely new) |
| `/itineraries/` hub + 5 duration pages × 6 langs | 36 | 404 (genuinely new) |
| `/trip-planner/` × 6 langs | 6 | 404 (genuinely new) |
| `/map/` × 6 langs | 6 | 200 live — newly **added to the sitemap**, page already exists |
| `/tours/` × 6 langs | 6 | 200 live — newly **added to the sitemap**, page already exists |

### 4.3 Parity confirmed

| Section | Live locs | Build locs | Identical |
|---|---|---|---|
| `/regions/**` | 66 (11 regions × 6 langs) | 66 | **yes** |

One pre-existing gap, unchanged by this build and therefore *not* a deploy regression, but worth closing: **`https://rentup.ge/regions/` is a 404** — 11 region pages exist but there is no `dist/regions/index.html` hub, so a trimmed or hand-typed URL lands on the 404 page.

---

## 5. Fixing the 162 URLs — and why a "301" is not available here

**GitHub Pages cannot serve a 301 from a static tree.** Confirmed by `.github/workflows/pages.yml`: the site is built by `python build.py dist` and published with `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`. GitHub Pages serves that artifact as flat files with no rules layer — no `_redirects`, no `.htaccess`, no `netlify.toml` processing, no edge config. The `[[redirects]]` blocks in `netlify.toml:17-38` (`/planner/` → `/map/#planner`, `/pricing/` → `/fleet/`) are **inert** on the current host; they are a leftover from the paused Netlify pipeline that the workflow header explicitly says it replaced.

The only server-side behaviour GitHub Pages offers is serving `dist/404.html` (present, 5,640 B) with an HTTP 404 status for any unmatched path. That is a soft landing, not a redirect, and it preserves no link equity.

**So the mechanism must be a built HTML stub page — and the repo already uses exactly this pattern.** `dist/planner/index.html` and `dist/pricing/index.html` are real generated pages whose `<link rel="canonical">` points elsewhere:

```
$ grep -o '<link rel="canonical"[^>]*>' dist/planner/index.html dist/pricing/index.html
dist/planner/index.html:<link rel="canonical" href="https://rentup.ge/map/">
dist/pricing/index.html:<link rel="canonical" href="https://rentup.ge/fleet/">
```

`scripts/seo_audit.py` already codifies this convention — `DEFAULT_CANONICAL_ALIASES` maps `/pricing/` → `/fleet/` and `/planner/` → `/map/`.

### Three options, in order of preference

**Option A — restore the content (best for SEO).** These 27 slugs are live, indexable and returning 200. If they were removed by accident, restore the 10 `content/attractions/*.yml` and 17 `content/routes/*.yml` files from git history and the problem disappears with no redirect infrastructure at all. Check this first: 17 of 49 routes and 10 of 267 attractions vanishing in one build looks more like a deletion than a decision.

**Option B — generate 162 canonical stub pages** (the `/planner/` pattern applied to retirements). Add a `content/settings/retired.yml` mapping each retired slug to its replacement, and a loop in `build.py` that emits, for each retired slug × each language:

```html
<link rel="canonical" href="https://rentup.ge/<replacement>/">
<meta http-equiv="refresh" content="0; url=/<replacement>/">
```

Suggested replacements (all exist in the build):

| Retired | Send to |
|---|---|
| the 10 attractions (`abudelauri-lakes`, `artsivi-eagle-gorge`, `bateti-lake`, `bebris-tsikhe`, `betania-monastery`, `didgori-battle-memorial`, `gomismta`, `kojori-fortress`, `niko-nikoladze-house-museum`, `tbilisi-sea`) | the `/regions/<region>/` page for that attraction's region, else `/map/` |
| the 17 routes (`batumi-coast-family-day`, `borjomi-spa-day`, `georgia-essential-five-days`, `gori-uplistsikhe-day`, `guria-coast-day`, `guria-mountain-spa-weekend`, `kakheti-cycling-day`, `kakheti-wine-day`, `kazbegi-mountain-day`, `kutaisi-monasteries-caves-day`, `kvemo-kartli-monasteries-day`, `lagodekhi-nature-weekend`, `martvili-nokalakevi-day`, `mtskheta-heritage-day`, `racha-family-weekend`, `racha-lechkhumi-heritage-three-days`, `tbilisi-stage-and-museum-day`) | the nearest surviving route (e.g. `kakheti-wine-day` → `/routes/kakheti-wine-loop/`), else `/tours/` |

Trade-off, stated plainly: a `meta refresh` plus a cross-page canonical is treated by Google as a soft 301 and passes most equity, but it returns **HTTP 200**, so the old URLs linger in the index as thin pages until Google consolidates them. Adding `noindex` would prevent that lingering but also blocks consolidation — so use canonical + refresh **without** `noindex` if the goal is passing equity. That is exactly what the existing `/planner/` alias does.

**Option C — move off GitHub Pages** if true 301s matter. Cloudflare Pages (`_redirects`), Netlify (the `netlify.toml` already in this repo), or a Cloudflare Worker in front of Pages all serve real 301s. Restoring the Netlify pipeline would give real 301s for the 27 slugs *and* turn the `/planner/` and `/pricing/` aliases into actual redirects instead of duplicate 200s.

**Required regardless of option:** verify the GitHub Pages custom-domain setting still holds. There is **no `CNAME` file** in the repo or in `dist/`, so `rentup.ge` is bound purely through the repo's Settings → Pages field. That survives `deploy-pages` runs, but it is a single unversioned setting with the whole domain behind it.

---

## 6. Verification commands

Every number above came from one of these. All are read-only.

**Build the reference index and resolve it (the 164,910 / 2,911 figures):**
```bash
# /tmp/linkcheck.py — walks dist/, extracts <a href>, <link href>, <img src|srcset>,
# <script src>, <source src|srcset>, <video poster>, <iframe src>, <form action>,
# <meta content> URLs and <use href> from *.html/*.xml/*.svg, plus url() from *.css,
# then resolves each root-relative, absolute-rentup.ge and relative path against the
# real file set (dir -> index.html; extensionless -> /index.html or .html).
python3 /tmp/linkcheck.py
# total refs: 164910  ok: 134940  bad-unique: 91  bad-occurrences: 2911
# external unique: 2485
```

**analytics.js, three independent ways:**
```bash
grep -rl "analytics.js" dist --include="*.html" | wc -l    # 2125
grep -ro "assets/analytics\.js" dist/ | wc -l              # 2125
find dist -name "*.html" | wc -l                           # 2140
comm -13 <(grep -rl "assets/analytics.js" dist --include="*.html" | sort) \
         <(find dist -name "*.html" | sort)                # the 15 exempt pages
ls static/analytics.js dist/assets/analytics.js            # both: No such file
grep -n "analytics.js" build.py                            # 715, 723, 4455, 4480
curl -s -o /dev/null -w '%{http_code}' https://rentup.ge/assets/analytics.js   # 404
```

**Missing photos:**
```bash
ls static/photos | wc -l ; ls dist/assets/photos | wc -l   # 883 / 883
diff <(ls static/photos) <(ls dist/assets/photos)          # empty
grep -rn "dry-bridge-market.jpg" content/                  # content/attractions/dry-bridge-market.yml:9,16
# live proof the files used to exist:
for p in dry-bridge-market.jpg poka-nunnery.jpg abano-pass-1.webp geguti-palace-3.webp ; do
  curl -s -o /dev/null -w "%{http_code} $p\n" https://rentup.ge/assets/photos/$p ; done   # all 200
# JSON feeds: 672 occurrences / 88 unique / 390 files under dist/data/
```

**Fragments:**
```bash
# For every *.html: collect id="..." and <a name="...">, then test each href="#...".
# 2148 fragment links; 1 unique broken target (#planner); 30 occurrences.
grep -o 'href="#planner"' dist/index.html | wc -l          # 5
grep -rl 'id="planner"' dist/ | wc -l                      # 6 (the /map/ pages only)
grep -o '<script[^>]*src="[^"]*"' dist/index.html          # no planner.js / workspace.js
grep -l "open-standard-tour" dist/assets/*.js              # planner.*.js, workspace.*.js only
grep -n '#planner' build.py                                # 818,866,915,1119,1123,1809,3189,3902,4052,4509
```

**External checks (`curl -L`, 25–30 s timeout, browser UA):**
```bash
# all 43 low-cardinality URLs plus samples:
while read u ; do
  curl -sS -o /dev/null -w "%{http_code}|%{num_redirects}|%{url_effective}|||$u\n" \
    --max-time 30 -L -A "Mozilla/5.0 (compatible; LinkAudit/1.0)" "$u"
done < /tmp/ext_targets.txt
# all 918 commons.wikimedia.org URLs, 8-way parallel, then retry the 429s at 2-way:
xargs -a /tmp/commons.txt -P 8 -I@ sh -c \
  'printf "%s %s\n" "$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 -L "$1")" "$1"' _ @
# -> 813x200 + 105x429 ; the 105 retried -> 105x200. Total 918/918 = 200.
# 40 random wa.me samples -> 40x200.
```

**Live vs. build:**
```bash
curl -sS -L -o /tmp/live_sitemap.xml https://rentup.ge/sitemap.xml     # 200, 1,978,904 bytes
# live <loc> count = 2142 (flat urlset) ; dist/sitemap.xml = 8 <loc> (sitemapindex)
# union of dist/sitemaps/*.xml = 2100 <loc>
# set difference -> 162 live-only, 120 build-only
xargs -a /tmp/live_only.txt -P 6 -I@ sh -c \
  'printf "%s %s\n" "$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 -L "$1")" "$1"' _ @
# -> 162 x 200
ls content/attractions/*.yml | wc -l   # 257
ls content/routes/*.yml      | wc -l   # 32
ls -d dist/attractions/*/    | wc -l   # 257
ls -d dist/routes/*/         | wc -l   # 32
for u in /car-rental/tbilisi/ /itineraries/georgia-7-days/ /sitemaps/attractions.xml \
         /trip-planner/ /regions/ /map/ /tours/ ; do
  curl -s -o /dev/null -w "%{http_code} $u\n" -L "https://rentup.ge$u" ; done
# 404 404 404 404 404 200 200
```

**Cross-check against the existing audit:**
```bash
python3 scripts/seo_audit.py dist
# TOTAL: 0 ERROR, 247 WARN, 20 INFO  — none of the findings above
```

---

## 7. Fix order

| # | Fix | Impact | Where |
|---|---|---|---|
| 1 | Restore or stub the 27 retired slugs **before deploying** | stops 162 live 200s becoming 404s | `content/attractions/`, `content/routes/`, or a retirement loop in `build.py` |
| 2 | Ship `static/analytics.js`, or stop emitting the tag | fixes a 404 script on 2,125 pages (already live) | `build.py:715 / 723 / 4480` |
| 3 | Repoint the 88 photo paths at files that exist | fixes 786 HTML + 672 JSON image 404s, incl. 8 `og:image` | `content/attractions/*.yml` (lines in §2.2) |
| 4 | Guard `og:image` against already-absolute values | fixes 1 dead URL on 6 pages | `build.py:2213` |
| 5 | Make `#planner` absolute | fixes 30 dead in-page links on the 6 home pages | `build.py:1119, 1123` |
| 6 | Trailing slash on the CC license URLs; `http:` → `https:` on the CC0 deed | removes 5,394 redirect hops | license-URL mapping + 3 `content/attractions/*.yml` |
| 7 | Add `--strict` assertions: every `content/**` `image:` resolves under `static/`, and every name in `hashed_sources` exists | stops #2 and #3 recurring silently | `build.py:4455-4483` |
| 8 | Commit `static/uploads/`; add a `/regions/` hub page | closes a latent CMS 404 and a hub-page gap | `static/`, `build.py` |
