# Local implementation status

Last reviewed: 2026-08-14. This describes the local branch only. Nothing was deployed or pushed.

## Completed locally

- One Leaflet travel workspace provides discovery, route and planner modes.
- Six-language KA/EN/RU/FA/HE/AR generated site with RTL and multilingual place search.
- Progressive map clusters, real-road routing integration, traffic layer, GPS/manual location, visited filtering and cycling candidates.
- Curated difficult-road legs, conservative winter warnings, unified overnight/hotel towns and a strict safe vehicle recommendation floor.
- Static rental inquiry forms with contextual WhatsApp and Netlify Forms fallback on cars and relevant entry/tourism pages.
- Admin management for car status, availability, photos, three GEL tiers, deposit, franchise, insurance, mileage and extra services.
- Optional accounts, saved trips and community contracts remain isolated from the core public/rental path.
- PWA manifest/service worker provides an installable responsive web-app base.

## Verified locally

- 22 automated unit/content/data-contract tests pass.
- JavaScript source syntax passes.
- Full build succeeds: 1,800 HTML pages, 17 cars, 4 articles and 6 languages.
- Generated contact details use the central site settings source.
- Generated car gallery supports the CMS object format without broken image URLs.
- Strict build returns exit code 2 for unresolved publication warnings.

## Production blockers requiring owner data

- Real phone, mobile/WhatsApp, email and social links.
- Real main/gallery photos and confirmed availability for all 17 published cars.
- Final human verification that every attraction photo depicts the correct place.
- Hosting OAuth and optional Firebase configuration after local acceptance.

## Intentionally not implemented

- Payment gateway, realtime fleet locking or automatically confirmed booking.
- Fabricated reviews, prices, availability, photos or business facts.
- Signed native App Store/Google Play packages; the current deliverable is a PWA base.

## Final release step

After owner data is supplied: run validation and strict build, review locally, then commit/push and deploy only with explicit approval.
