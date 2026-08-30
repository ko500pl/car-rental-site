# Restored content: 27 missing attraction/route source files (2026-08-30)

## Correction to the premise

The task brief assumed the 27 missing files (`content/attractions/*.yml` × 10,
`content/routes/*.yml` × 17) had been **deleted from git history** and needed
recovery via `git log --diff-filter=D`. That premise did not hold:

- This working copy (`/home/claude/carrent2`) has **no `.git` directory at
  all** — it is a plain file copy, not a git checkout.
- The actual source of truth is the GitHub repo **`ko500pl/car-rental-site`**
  (identified from `claude/rentup-landing-hero-fix-2026-08-24.md` in this
  Project), cloned fresh for this task. Its `main` branch HEAD
  (`8154934827f3…`, "Production update: tours, attractions, planner UX and
  verified photos", 2026-08-29) already contains **267 attractions and 49
  routes** — exactly matching what's live on rentup.ge today.
- `git log --diff-filter=D --name-only -- content/attractions content/routes`
  against the real repo returns **zero deletions** for any of the 27 files in
  question. They were never removed from git; they simply never existed in
  this particular local copy. The 10 attractions were added in commit
  `4f66861` (2026-08-19, "Places list: …"); the 17 routes were added in the
  latest commit `8154934` (2026-08-29). This local copy is a partial/stale
  snapshot (its unrelated files match commit `9571e80`, several commits
  behind HEAD) that picked up later edits to existing files but missed files
  that were newly *added* by later commits.
- Conclusion for step 4 of the task ("check why they were deleted, don't
  restore blindly if deliberate"): **not applicable — nothing was
  deliberately removed.** Restoring from the real repo's HEAD is correct and
  safe; it's the same content already serving the 162 live URLs.

## What was restored

Copied verbatim from `ko500pl/car-rental-site@8154934` into this working
copy (attractions written with CRLF line endings to match this repo's
existing convention for that directory; routes written as LF, matching its
existing convention):

**Attractions (10)** — added upstream in `4f66861`:
`abudelauri-lakes`, `artsivi-eagle-gorge`, `bateti-lake`, `bebris-tsikhe`,
`betania-monastery`, `didgori-battle-memorial`, `gomismta`, `kojori-fortress`,
`niko-nikoladze-house-museum`, `tbilisi-sea`

**Routes (17)** — added upstream in `8154934`:
`batumi-coast-family-day`, `borjomi-spa-day`, `georgia-essential-five-days`,
`gori-uplistsikhe-day`, `guria-coast-day`, `guria-mountain-spa-weekend`,
`kakheti-cycling-day`, `kakheti-wine-day`, `kazbegi-mountain-day`,
`kutaisi-monasteries-caves-day`, `kvemo-kartli-monasteries-day`,
`lagodekhi-nature-weekend`, `martvili-nokalakevi-day`, `mtskheta-heritage-day`,
`racha-family-weekend`, `racha-lechkhumi-heritage-three-days`,
`tbilisi-stage-and-museum-day`

`content/attractions/` now has 267 files, `content/routes/` has 49 — matching
the live site.

## Field completeness

Every restored file was checked against its template's required fields:
- Attractions: `region`, `type`, `lat`, `lon`, `road`, `car_category`,
  `visit_hours`, `best_season`, `entry_fee`, `distance_tbilisi_km`,
  `drive_time_tbilisi` — all present, all non-empty, in all 10 files.
- Routes: `days`, `distance_km`, `drive_time_total`, `car_category`,
  `best_season`, `waypoints` — all present, all non-empty, in all 17 files.
- No fields needed to be filled in from live-page content; nothing was
  invented.
- All route `waypoints` slugs resolve to an existing attraction file in the
  267-file set (no dangling cross-references introduced).

## Brand string

Checked all 27 files for the old "Drive On" / "დრაივ ონ" branding — **none
found**. No edits needed on that front.

## Photos: pre-existing gap, out of scope, not touched

`static/photos/` in this local working copy is **also an incomplete
snapshot** of the real repo (which has 892 photo files; this copy has
fewer). This predates and is unrelated to the content restoration:

- Before restoring anything, `tests.test_content_quality
  .AttractionMediaTests.test_every_media_reference_exists` was **already
  failing** on this copy: 97 image/gallery references from the pre-existing
  257 attractions point to files missing from local `static/photos/`.
- The 10 restored attractions add **25 more** missing references (all of
  their `image:`/`gallery:` entries — every one of these 10 files' photos is
  absent locally): `abudelauri-lakes` (×3), `artsivi-eagle-gorge` (×2),
  `bateti-lake` (×3), `bebris-tsikhe` (×3), `betania-monastery` (×3),
  `didgori-battle-memorial` (×3), `gomismta` (×3), `kojori-fortress` (×1),
  `niko-nikoladze-house-museum` (×2), `tbilisi-sea` (×2).
- Critically, **these photos are not actually missing from the live
  deployment** — they exist in the real `ko500pl/car-rental-site` repo (892
  files there vs. fewer here) and rentup.ge serves them today. The gap is
  local to this sandbox's `static/photos/` copy, not a real content-loss
  event. Per the task's file-scope restriction, `static/*` was left
  untouched; rewriting the restored records' `image:`/`gallery:` fields to
  point at different, locally-present photos would have been a *regression*
  from the correct (live) state, so that was deliberately not done.
- **Action needed (outside this task's file scope):** sync `static/photos/`
  in this working copy from the same upstream repo/commit before the next
  build that runs with `--strict` image checks, or confirm the deploy
  pipeline pulls `static/` from the authoritative repo rather than this
  local copy.

## Validation

- `python3 build.py --validate-only` → **passes** (`✔ content validation
  passed`; pre-existing unrelated warning: "17 published cars have no main
  image").
- `python3 -m unittest tests.test_content_quality tests.test_sitegen -q` →
  **25/26 pass.** The one failure,
  `test_every_media_reference_exists`, is the pre-existing photo-sync gap
  described above (97 missing before this change, 122 after — the 25 new
  ones all belong to the 10 restored attractions, all photo files that exist
  in the real repo, not part of `content/*` scope).

## Files touched

- `content/attractions/*.yml` — 10 new files added
- `content/routes/*.yml` — 17 new files added
- `docs/seo/RESTORED_CONTENT.md` — this report

No other files were modified (`build.py`, `theme.py`,
`content/settings/*`, `static/*`, `tests/*` untouched).
