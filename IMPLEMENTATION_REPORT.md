# Implementation report

Prepared: 2026-08-14  
Scope: local implementation and verification; nothing deployed or pushed.

## Completed

- Preserved the Python/static HTML/Decap architecture and six-language/RTL output.
- Added curated important road-leg overrides and conservative difficult-road metadata.
- Unified planner towns and accommodation lookup through `places.yml`.
- Passed year-round and seasonal data into planner decisions and added long-drive/winter warnings.
- Unified vehicle requirement ranking. The recommender now returns no vehicle instead of suggesting one below the safe minimum.
- Added contextual WhatsApp handoff using the admin-managed number.
- Replaced Firebase rental booking with static Netlify-compatible inquiry forms; Firebase remains limited to optional accounts/trip sync.
- Added a compact reusable inquiry form to homepage, fleet, map/planner and tourism pages, plus the detailed car request form.
- Expanded car CMS fields for availability, franchise, insurance, mileage, minimum rental, additional driver, child seat, airport delivery and cross-border rules.
- Added availability-aware Car Offer structured data and excluded unavailable cars from planner recommendations.
- Added attraction hero LCP attributes and safe lazy loading for ordinary images.
- Added OG fallback files for Persian, Hebrew and Arabic.
- Changed sitemap `lastmod` from build date to each source file's modification date.
- Added multilingual map search data, progressive count clusters, visited/unvisited state and cycling candidates already present in the local product work.
- Added strict placeholder validation and documented the owner workflow in `ADMIN_SETUP.md`.

## Bugs fixed

- Mountain travel estimates: curated road legs take precedence over straight-line fallback.
- Overnight/hotel mismatch: one town source now drives both labels and hotel selection.
- Winter safety: year-round destinations remain eligible, while winter mountain travel raises the vehicle floor and warnings.
- Required/recommended car contradiction: both use the strictest shared rank; unsafe fallback was removed.
- Dead-end conversion: tourist traffic can now continue to contextual WhatsApp or a form.
- Misleading sitemap freshness: content-specific dates replace a universal build date.
- Missing social images: all six language fallbacks exist.

## Admin capabilities

From `/admin/` the owner can create, edit, publish, archive and order cars; upload main/gallery images; manage specifications, three GEL price tiers, deposit, availability and commercial conditions; edit multilingual content; and change site identity, logo, contacts, address, hours and social links. Published content feeds the generated pages automatically.

## Remaining manual owner inputs

- Replace placeholder phone/mobile/WhatsApp and email values.
- Replace placeholder social links and confirm the real business address/details.
- Upload real main photos for all 17 published vehicles and verify their real specifications, rates and availability.
- Supply only real testimonials/reviews if that feature is populated.
- Configure hosting OAuth and, only if account sync is wanted, real Firebase credentials.

## Remaining limitations

- Route estimates are planning estimates, not live road-condition guarantees. Mountain access must still be confirmed near travel time.
- No payment gateway, live inventory lock or transactional booking database was added; phase one ends at inquiry.
- Source mtimes are used for sitemap dates. A future CMS `updated_at` field or Git commit date can replace them.
- Tbilisi no-car-day rental-window adjustment and a full browser layout regression suite remain phase-two work.
- Responsive source-image variants are not generated yet; hero dimensions, priority and sizes are set.

## Future availability integration point

Replace the current `fleet_for_planner()` availability filter with a build-time export or small read-only availability API. Preserve the inquiry payload contract (car, dates, pickup/return, itinerary and page URL) so a fleet-management system can consume it later.

## Deployment steps

1. Complete the manual owner inputs above in Admin/content.
2. Run `python build.py --validate-only`.
3. Run `python build.py dist --strict`; it must finish without warnings.
4. Commit and push only after review.
5. Deploy `dist`, configure GitHub OAuth, then test `/admin/`, a WhatsApp inquiry and a form submission on the real domain.

## Tests

- JavaScript syntax: passed for `planner.js` and `booking.js`.
- Python unit/content tests: 22/22 passed.
- Full generated-site build: generated successfully; console-only Unicode output required UTF-8 on Windows.
- Strict publication build: intentionally blocked by real owner-data requirements — placeholder contacts/social URLs and 17 missing vehicle main images. These values were not fabricated.
