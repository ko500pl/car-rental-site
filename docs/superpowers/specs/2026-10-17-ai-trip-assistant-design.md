# RentUp AI — trip assistant on the site (design, 2026-10-17)

Owner decisions (chat, 2026-10-17): purpose = **lead to a booking**; placement =
**full chat on every page**, map proposals on the planner; backend =
**Cloudflare Worker**; model = Claude **Haiku 5.5** on the owner's own Claude API
account. A Claude Max subscription cannot back a public product and is not used.

## 1. Shape

```
browser (assistant.js)  ──POST /chat──▶  Cloudflare Worker  ──▶  Claude API (Haiku 5.5, tools)
        ▲                                   │ catalog cached from
        │ {reply, plan?}                    │ https://rentup.ge/assets/ai-catalog.json
        └── planner map (FH_TRAVEL_EXPLORER.applyTour) ◀── plan.places
```

- The site stays static. The Worker holds the only secret (`ANTHROPIC_API_KEY`).
- The widget is emitted on every public page when `site.yml → ai_assistant.endpoint`
  is set. Empty endpoint = no widget, no script, no CSS cost.
- The model never draws. It returns a **structured plan** (origin, days, place
  slugs, car); the existing planner renders it, so the map is always exact.

## 2. Knowledge: `assets/ai-catalog.json` (build output, not committed)

Built by `scripts/build_ai_catalog.py` from `content/` only, written into
`dist/assets/` by `build.py`. One file, ~250 KB, gzip ≈ 60 KB:

- `places[]`: `s` slug, `n` {6 langs}, `t` type, `r` region, `la/lo`, `km`
  from Tbilisi, `dm` drive minutes from Tbilisi, `vh` visit hours, `rt` rating,
  `cc` car category needed, `road`, `fee`, `season`, `uns` unesco.
- `cars[]`: slug, name, category, seats, transmission, drive, clearance, prices
  (1–6 / 7–29 / 30+ days), deposit.
- `routes[]`: slug, name {6}, days, purpose, region, waypoints, car category,
  distance, drive total.
- `policy`: the rental_policy.yml facts the assistant may quote (age, licence,
  fuel, deposit, insurance, cancellation, delivery fees, extras, one-way).
- `site`: phone, WhatsApp number, office address {6}, hours.
- `regions`/`types`: label tables {6}.

Guard: `tests/test_ai_catalog.py` — every place has coords, drive time, visit
hours and all 6 names; every car has a price; file under 400 KB.

## 3. Worker (`worker/`)

`POST /chat` body `{lang, messages:[{role,content}], page}` → `{reply, plan?, car?}`.

Tools the model may call (executed in the Worker, deterministic, from the catalog):

| tool | does |
|---|---|
| `find_places({max_drive_min?, types?, regions?, max_visit_h?, query?, limit})` | filter + rank by rating |
| `fit_day({hours, types?, regions?, origin?})` | greedy day plan: drive there + visits + drive back ≤ hours; returns candidate sets |
| `get_cars({category?, seats?})` | cars with prices |
| `get_policy()` | the policy block |
| `propose_plan({title, origin, days, places[], car, why})` | **terminal**: Worker validates slugs, totals the hours, returns it to the client as `plan` |

System prompt: RentUp's assistant; answer in `lang`; only the catalog; prices and
rules only from tools; never invent places, prices or availability; a plan must
end with one car suggestion and the booking nudge; off-topic → one polite
sentence back to trips/cars; keep replies short (≤ 120 words unless listing).

Limits: ≤ 12 turns kept (older dropped), ≤ 1 000 chars per message, `max_tokens`
900, 3 tool rounds max. CORS allow-list: `https://rentup.ge`, `https://www.rentup.ge`,
`http://localhost:*`. Rate limit: Cloudflare `ratelimit` binding 30 req / 60 s per
IP (falls back to open when the binding is absent, logged). Nothing is stored.

`MOCK=1` env: no Claude call; a canned tool-driven answer, for tests and the
Playwright run. Tests: `node --test worker/test/` (fit_day math, slug validation,
CORS, limits, request shape).

## 4. Widget (`static/assistant.js` + CSS block in theme.py)

- Button bottom-end (RTL aware) with the arrow-u mark; panel 380×560 desktop,
  full-screen sheet on mobile; `aria-live` list; Esc closes.
- Quick prompts per language ("8 hours from Tbilisi", "2 days wine", "which car
  for Tusheti"). Language = `<html lang>`.
- Plan card: title, stops with drive/visit minutes, total, car with price,
  buttons **Show on map** and **Book this car** (wa.me prefilled, same text shape
  as the planner's WhatsApp button; fires Umami `whatsapp_click` source=assistant).
- History in `sessionStorage` (`rentup-ai`), cleared by "new chat".
- Errors: offline / rate-limited / 5xx → one friendly line + phone & WhatsApp.

## 5. Planner hook

- On `/map/`: `window.RentUpAI.showPlan(plan)` → `FH_TRAVEL_EXPLORER.applyTour(slugs, {days})`
  and scroll to `#planner`.
- Elsewhere: navigate to `{plannerUrl}?plan=s1,s2,s3&days=N#planner`; `explorer.js`
  reads `plan` on load and applies it once the data is in.

## 6. Build & ops

- `build.py`: writes the catalog, ships `assistant.js` hashed, emits
  `window.FH_CFG.ai = {endpoint, lang}` and the widget root when configured.
- `worker/wrangler.toml`, `worker/README.md` (Georgian) with the three owner
  commands: `npx wrangler login`, `npx wrangler secret put ANTHROPIC_API_KEY`,
  `npx wrangler deploy`. The owner types the key; Claude never handles it.
- Cost: Haiku 5.5 $0.10/M in, $0.50/M out; ≈ 4–6 k tokens per turn ≈ $0.001–0.002.

## 7. Out of scope (now)

Streaming, server-side history, voice, booking inside the chat, photos in replies.
