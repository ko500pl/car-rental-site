# Owner steps (each ~5 minutes)

Claude prepares everything; creating accounts and verifying them must be done by you.

1. **Umami Cloud** — cloud.umami.is → sign up → *Add website* → domain `rentup.ge` → copy the *Website ID* (a UUID) → send it to Claude, or paste it into `content/settings/site.yml → analytics.website_id`.
2. **Bing Webmaster Tools** — bing.com/webmasters → sign in → *Import from Google Search Console* → choose rentup.ge.
3. **Yandex Webmaster** — webmaster.yandex.com → add site → choose *Meta tag* → send the `content=` value (goes into `site.yml → verification.yandex`).
4. **Google Business Profile** — business.google.com → add business → name exactly `RentUp` → paste the fields from `LISTINGS_PACK.md` → verify (video or postcard) → send Claude the public Maps link.
5. **Yandex Business, 2GIS, Apple Business Connect** — same as step 4 with the matching section of the pack.
6. **Localrent** (first), then **DiscoverCars** — partner sign-up → contract → upload `exports/fleet-<platform>.csv` (`python scripts/export_fleet.py localrent`). If their template uses other column names, change `COLUMNS[platform]` in `scripts/export_fleet.py` (one line per column).
7. After every publish: `python scripts/indexnow_submit.py`.
