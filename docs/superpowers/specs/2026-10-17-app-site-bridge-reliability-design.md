# RentUp — app ↔ website bridge: reliability (design)

**Date:** 2026-10-17
**Status:** design approved in conversation; awaiting spec review
**Approach:** B — fix what loses money, then make the bridge able to say when it is broken
**Priority set by the owner:** reliability (სანდოობა) before speed and before less manual work

---

## 1. Intent

One business, two codebases, one bridge.

- **RentUp Leasor** — Flutter/Android, offline-first SQLite, one user: the owner.
- **rentup.ge** — a static site, 2400+ pages, six languages, no server.
- **Firestore** — the only thing they share. Three collections: `fleet/{slug}` and
  `availability/{slug}` (app writes, site reads), `bookings/{id}` (site writes,
  app reads).

**The outcome this design commits to:** a customer's request always reaches the
owner's phone, the site never quotes a price or a free date the app disagrees
with, and when either of those breaks the owner is told — by the app, without
being asked.

**Success is measurable:** a booking created on the site is visible on the phone
within one sync cycle regardless of how many bookings exist; the site's
availability is never older than 72 hours without the owner having been warned
at 48; and no failure path reports success.

**Where the work lands.** Two repositories, and the plan must keep them
straight:

- **app** — `lib/services/cloud/*`, `lib/database/database_helper.dart`,
  `lib/providers/app_state.dart`, `lib/models/web_booking.dart`, plus the
  dashboard section. D1, D2, D4, §5.1 and most of §5.2.
- **site** — `static/booking.js`, `static/catalogue.js`, `firestore.rules`,
  and `content/settings/booking.yml` if §5.3 goes that way. D3, §3.6, §7.

**Out of scope, deliberately** — see §6.

---

## 2. What is wrong today

Four parallel audits (publish path, inbound path, website JS, security rules)
found 19 confirmed defects. The four below are the ones that lose money or
bookings, silently. The remaining fifteen are in §5.1 and §5.2; §5.3 is the one
item that cannot be decided without the owner.

### D1 — The inbox has a hard ceiling of 300 documents · CRITICAL

`CloudSyncService.sync()` calls `rest.listDocuments('bookings', limit: 300)`
(`cloud_sync_service.dart:216`). `listDocuments` sends only `pageSize` and
`pageToken` (`firestore_rest.dart:275-278`) — **no ordering** — so Firestore
returns documents ordered by document name ascending. The site creates bookings
with `addDoc` (`booking.js:277`), whose IDs are random 20-character strings.
The limit then hard-returns and discards the page cursor
(`firestore_rest.dart:293`). No watermark exists; `sync_state`
(`lib/database/database_helper.dart:658`) is never used for bookings.

**Consequence:** above 300 documents the app sees the same 300
lexicographically-smallest IDs forever. A new booking is fetched with
probability ≈ 300/N. At 600 bookings, half of all customer requests never reach
the phone — and `sync()` records `ok`.

The existing test (`test/cloud_bridge_test.dart:247-276`, *"follows page tokens and stops at the
limit"*) asserts the truncation
as correct behaviour. It must be rewritten, not merely extended.

### D2 — Availability is published only by a human tap · CRITICAL

`publishFleet` is reached from exactly four button handlers
(`fleet_report_screen.dart:69,115,138`, `cloud_settings_screen.dart:109`,
`car_detail_screen.dart:1635`). The hourly `WebSync.run` drains the outbox and
fetches bookings and **writes nothing** to `fleet/` or `availability/`.

**Consequence:** 48 hours after the last tap the site's freshness check
(`booking.js:291`) rejects the availability document and `busyFor` returns
`false` for every date — the site offers every day on every car, including cars
already rented. Double bookings, with no signal on either side.

### D3 — The booking form quotes and writes a build-time price · CRITICAL

`booking.js:79-83` computes the quote from `FH_CFG.cars` (baked into the HTML at
build time) and only then starts `fetchLive(slug)`. The submit handler takes the
quote synchronously (`:138`) and nothing awaits the live fetch.

**Consequence:** a visitor who completes the form within roughly a second of
opening it is quoted, and has written into their booking document, whatever
price was current at the last site deploy. Deploys are infrequent; the gap is
unbounded.

### D4 — One failed answer blocks every answer behind it, forever · CRITICAL

`_drainOutbox` marks the entry and `break`s on any exception
(`cloud_sync_service.dart:347-350`). `attempts` is incremented
(`lib/database/database_helper.dart:2423`) and never read: no cap, no backoff, no
dead-letter. `_drainOutbox` does not rethrow, so `sync()` still reaches
`setLastResult('ok')` (`:222`) and returns `error: null`.

**Consequence:** one undeliverable accept/decline — a deleted document, a
revoked permission — and every subsequent confirmation the owner sends stays on
the phone permanently. Customers are never told they are confirmed. Nothing on
screen says so.

---

## 3. Design

### 3.1 The one new idea — `BridgeHealth`

A **computed verdict, never a stored flag.** Recomputed on every sync run and on
demand. It answers one question: *is the website's view of the fleet currently
true, and is anything stuck?*

```
enum BridgeStatus { ok, warning, broken }

class BridgeHealth {
  BridgeStatus status;
  String headline;   // Georgian, one sentence, names the single worst problem
  String? action;    // what the owner should do, or null when nothing to do
  DateTime checkedAt;
}
```

Inputs, each already available or cheap:

| Signal | Source | `warning` | `broken` |
|---|---|---|---|
| Age of the newest published availability | `CloudConfig.lastPublishAt` | ≥ 48 h | ≥ 72 h |
| Failed outbox entries | new `status` column | — | ≥ 1 |
| Queued outbox entries | `outboxCount()` (`database_helper.dart:2429`) | ≥ 1 for > 6 h | — |
| Inbox truncation canary | last fetch returned == limit | ✓ | — |
| Price mismatches | existing `FleetReporter` | ≥ 1 | — |
| Last sync failed | `CloudConfig.lastResult` | — | ✓ |

**Only the worst signal is spoken.** A health card that lists six things is a
card nobody reads; the owner needs one sentence and one action.

Surfaced in two places, both reusing machinery that already exists:

1. **A dashboard section** — a new `DashboardSection.bridgeHealth`, which
   inherits the existing hide/reorder/has-content behaviour. It renders nothing
   when the status is `ok`, following the rule the dashboard already follows.
2. **A notification on degradation only** — fired when the status is worse than
   the last recorded one, never on every run. The previous status is persisted
   so a phone reopened an hour later does not re-ring.

**Why a verdict and not a log:** the existing failure modes are not silent for
lack of data — `FleetReporter` can already find mismatches and `outboxCount()`
already counts. They are silent because nothing *asserts* a conclusion where the
owner will see it without asking.

### 3.2 D1 — replace the inbox fetch

Two bounded queries replace the one unbounded list:

**Query A — what is new.** A structured query (`runQuery`, the mechanism
`queryWhereEquals` already uses at `firestore_rest.dart:315`):

```
from:    bookings
where:   created > <watermark>
orderBy: created ASC
limit:   300
```

`created` is a `serverTimestamp()` the site always sets (`booking.js:265`).
Firestore maintains single-field indexes automatically, so no index needs
deploying. The rules permit it: `admin()` (`firestore.rules:22-24`) is
field-independent, and the bookings read rule (`firestore.rules:132`) grants it
unconditionally, so any query shape is allowed for the owner's account.

After absorbing, the watermark advances to the newest `created` seen and is
persisted in `sync_state`.

**First run (no watermark):** fetch the newest 300 by `created DESC`, absorb
them, and set the watermark from the newest. Anything older is not fetched.
This is correct rather than lazy: on a fresh install the older requests are
historical and already answered, and `web_bookings` is deliberately excluded
from the backup archive.

**Query B — what changed.** For each locally pending `web_booking`, a direct
`getDocument('bookings', id)` to refresh `status` / `paymentStatus`. Bounded by
the number of unanswered requests, which is small by definition. A 404 means the
customer withdrew it before the owner answered — recorded as withdrawn rather
than left pending forever.

**The canary.** When Query A returns exactly its limit, the run records
`inboxTruncated = true`. `BridgeHealth` turns that into a warning. The ceiling
is gone, but the detector for *any* future ceiling stays.

**Side benefit:** the hourly sync stops downloading 300 documents and downloads
the handful that are new.

### 3.3 D2 — publish on a schedule and on change

`WebSync.run` gains a second half: after the inbound sync, call
`AppState.publishFleetIfDue()`.

It publishes when either holds:

- `now - lastPublishAt >= 12 h`, or
- a **dirty flag** is set.

The dirty flag is persisted (so it survives a restart) and set by every action
that changes what the site should show: a rental created, returned or edited; a
web booking accepted; a car's price, `isPublic` or archive state changed; a car
deleted.

**What this does not change:** the app must still be open. That constraint is
real and is already stated on the settings screen. "Every 12 hours or on any
change, whenever the app is open" is a different promise from "whenever the
owner remembers", and it is the one the 72-hour trust window can be met with.

**Retirement.** `publish` currently stops writing a car's documents when it is
sold or switched off, leaving the last price and calendar live forever. It will
instead write a tombstone — `{retired: true, updatedAt: now}` — for any slug
that was previously published and is no longer public. The site skips any
document carrying `retired`. No rules change: `fleet/*` and `availability/*`
(`firestore.rules:235-236`) accept any shape from an admin.

The set of previously-published slugs is read from Firestore at the start of the
run, which the publisher already does for its report.

### 3.4 D3 — the form waits for the live price

`sendToCloud` awaits `fetchLive(slug)` before computing the quote, with a 3 s
ceiling via `Promise.race`. The result is cached per slug, so for any visitor who
opened the dialog more than a moment ago this costs nothing.

When the live fetch does not land in time the baked price is used — the current
behaviour — but the document records which it was:

```
priceSource: 'live' | 'built'
```

The owner can then see, per booking, whether it was quoted from current data.

**This requires a rules change** (`priceSource` must join `hasOnly`,
`firestore.rules:75`), and the rules must be deployed **before** the site, or
every booking is rejected. See §7.

### 3.5 D4 — the outbox stops blocking

- `sync_outbox` (`lib/database/database_helper.dart:641-656`) gains a `status`
  column (`pending` / `failed`): an additive migration with a `DEFAULT`, nothing
  renamed and nothing dropped, so a database written by the new build still
  opens in the old one.
- An entry that reaches 5 attempts becomes `failed`. A `jsonDecode` failure
  becomes `failed` immediately — it will never succeed.
- `_drainOutbox` skips `failed` entries and keeps draining.
- Any `failed` entry makes `BridgeHealth` **broken**, with the action "open the
  cloud screen" where the entries can be inspected and retried or discarded.

### 3.6 Aligning the two trust windows

Today `booking.js` trusts a document for 48 hours (`:291`) and `catalogue.js`
for 30 days (`:56`), and `catalogue.js` writes prices from documents up to 30
days old into the very map `booking.js` quotes from (`:220-226`) — so a price
`booking.js` was written to refuse is used anyway.

Both become **72 hours**, and `BridgeHealth` warns at **48**. One number, one
meaning, and the owner is told a full day before anything stops being trusted.

---

## 4. Data contract

What changes on the wire. Everything else is unchanged.

| Collection | Field | Direction | Change |
|---|---|---|---|
| `bookings` | `priceSource` | site → app | **new**; `'live'` or `'built'`. Requires a rules change before the site ships. |
| `fleet/{slug}` | `retired` | app → site | **new**; `true` on a sold or switched-off model. No rules change. |
| `availability/{slug}` | `retired` | app → site | **new**; same. |

No field is removed or renamed. An older app build reading a `retired` document
ignores the field; an older site build ignores it too and keeps showing the car
until its trust window expires — a degradation, not a break.

---

## 5. Also included

### 5.1 Correctness of money and dates

- **Stale catalogue prices** no longer leak into the quote map (§3.6).
- **The UTC date shift.** `WebBooking._day` (`web_booking.dart:430-435`) parses
  an ISO string and reads `.year/.month/.day` without `.toLocal()`. Georgia is
  UTC+4, so a `Z`-suffixed timestamp for 20 October is stored as 19 October —
  wrong pickup date on the card, wrong availability check in
  `acceptWebBooking`, and a wrong night count when only one end shifts. No test
  covers a `Z`-suffixed value.
- **An overdue rental publishes the car as free.** `isCarFreeBetween` falls back
  to `DateTime.now()` for an open rental whose `endDate` has passed
  (`app_state.dart:2027-2030`), so a car still with a customer is offered.
  **Intended behaviour:** an open rental with no `actualEndDate` blocks the car
  until it is returned, whatever its planned end date — the car is physically
  out, and an overdue return is exactly when the site must not sell it again.

### 5.2 Failures that must stop being silent

- **One malformed document halts the whole inbox.** `CloudDocument.string` is an
  unguarded cast (`firestore_rest.dart:399`); `_absorb` wraps nothing, so one
  unexpected field type skips every document after it, every run. Per-document
  guard, and the skipped count reaches `BridgeHealth`.
- **The dead fallback.** `postForm` posts to a Netlify origin the file itself
  documents as a 404 (`booking.js:398-411`). "The lead is never lost" is false
  today. The code goes; the claim goes with it.
- **No idempotency on the booking write.** A transport error after the server
  accepted leaves the form populated and the visitor presses Send again. A
  client-generated request id, checked before writing.
- **An offline submit hangs forever.** The Firestore SDK queues rather than
  rejecting, so the button stays disabled and the status stays "sending"
  indefinitely. A timeout and an honest message.
- **Notifications missed.** `WebSync._announce` filters against a snapshot of
  `app.webBookings` taken inside `run`, so a request first absorbed by a
  `syncWebsite()` call made anywhere else — after answering a request
  (`app_state.dart:5229,5275`) or from the cloud screen's manual sync
  (`cloud_settings_screen.dart:247`) — is already present when `run` next looks
  and is therefore never announced. The announced-set moves to the database, keyed by booking id.
- **A remote cancellation after acceptance is invisible.** The warning is gated
  on `isNew` (`web_bookings_screen.dart:271`), so an accepted-then-cancelled
  request keeps blocking the car and sitting in the P&L.
- **The car page's button publishes the whole fleet.** It passes
  `_currentCar.modelSlug`, which is empty for the now-normal derived-slug case,
  and an empty slug means a full run (`fleet_publisher.dart:87-89`). The same
  `build` already computes the right slug.
- **Photo export and price publish disagree on the slug.** `photo_export.dart`
  uses only `car.modelSlug` while the publisher derives one, so a derived-slug
  car gets a price and no photograph; and `buildMapping` rewrites the mapping
  whole, so losing a hand-picked slug drops existing images.

### 5.3 Open question — the holiday surcharge

`booking.yml` declares `holiday_percent: 10` and `build.py:257` publishes it to
every page as `holidayPercent`. **No holiday dates exist anywhere in the
repository, and no code reads the value.**

It cannot be implemented from what is here. Two honest options:

- **a.** The owner supplies the dates (Easter, New Year, any other period), they
  join `booking.yml`, and the quote applies the surcharge the same way
  `peakNights` already does.
- **b.** The key is removed, so the configuration stops describing a charge the
  business does not make.

**This needs the owner's answer and is not implemented until it has one.**

---

## 6. Non-goals

Named so nobody has to re-derive why they are absent.

- **Partner PII.** A released booking hands every partner company the customer's
  name, phone, email and notes (`firestore.rules:133`) — Firestore has no
  field-level read security. It is a real exposure, but the partner board is
  dead code: `Marketplace.visibleTo` and `queryWhereEquals` have no call sites.
  **It must be fixed before that feature is switched on**, and a redacted
  `bookingOffers/{id}` collection is the shape to fix it with.
- **Retention and erasure.** No booking is ever deleted; there is no
  `allow delete: if admin()`. Permanent retention of customer personal data for
  a site serving EU and Israeli audiences is a policy question plus a scheduled
  job — its own sub-project, not a line item here.
- **The owner's web console** refuses to render without a custom claim
  (`admin-bookings.js:22`) that the documented `adminUids()` setup path never
  sets. The phone works, so this blocks nothing.
- **Background sync with the app closed.** Deliberately refused before, for the
  reason recorded in `web_sync.dart:11-21`, and refused again.
- **Rewriting the bridge.** Considered and rejected: the architecture is sound
  — REST over `http`, offline-first, no Firebase SDK — and every defect above is
  local to one function. A rewrite would risk the parts that work in order to
  fix the parts that do not.

---

## 7. Sequencing constraint

One ordering is not negotiable:

**Firestore rules must be deployed before the site that writes `priceSource`.**
`hasOnly` (`firestore.rules:75`) rejects any document carrying a key it does not
list — so a site deployed first would have *every booking rejected*, the visitor
would see a failure, and the owner would never learn a request existed. That is
strictly worse than the defect being fixed.

The app may ship in any order: it tolerates a missing `priceSource`, and the
`retired` tombstone needs no rules change.

---

## 8. Verification

Per `superpowers:test-driven-development`, each critical starts from a test that
**fails against today's code**:

| # | Test that must fail first | Then pass |
|---|---|---|
| D1 | The 301st booking, with an ID sorting below the first 300, is absorbed | ✓ |
| D1 | A second sync with an unchanged watermark fetches zero documents | ✓ |
| D2 | A sync 13 hours after the last publish writes `availability/*` | ✓ |
| D2 | Accepting a web booking marks the fleet dirty and the next sync publishes | ✓ |
| D2 | A car switched off is written as `retired`, not merely left behind | ✓ |
| D3 | A submit with a live price in flight writes the live figure, not the baked one | ✓ |
| D4 | A permanently failing entry does not block the entry behind it | ✓ |
| D4 | A failed entry makes `BridgeHealth` report `broken` | ✓ |
| 5.1 | A `Z`-suffixed `start` of 20 Oct is stored as 20 Oct in Georgia | ✓ |
| 5.1 | An overdue open rental publishes the car as taken | ✓ |
| 5.2 | A document with a non-string `status` skips itself only | ✓ |

Gates before anything is called done:

- `flutter analyze` clean; the full app suite green (510 tests today, plus the new ones).
- Site: build, internal links, SEO audit, JS syntax, unit tests. The D3 and
  §3.6 tests follow the pattern already proven by `tests/catalogue.test.js` plus
  its `tests/test_catalogue_js.py` wrapper — the script is run under `vm`
  against a faked DOM and a real-shaped Firestore reply, so browser behaviour is
  tested in the gate rather than after deploy. A new `tests/booking.test.js`
  pair does the same for `static/booking.js`, which has no suite today.
- **A live end-to-end check:** a real request submitted on the deployed site,
  confirmed to arrive on the phone, answered, and the answer confirmed back on
  the site. Nothing here is called finished on the strength of unit tests alone.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| Another agent is committing to the site repository concurrently; working-tree edits were lost once already | Commit early and often; build each commit from `HEAD` at the time; never `git add -A` |
| The watermark query silently returns nothing if `created` is absent on older documents | First run uses `created DESC` and sets the watermark from real data; the canary catches a persistent empty result |
| `priceSource` deployed out of order rejects every booking | §7; the rules deploy is its own plan step with its own verification |
| The schema migration must stay restorable into older builds | Additive column with a default, listed in `_columnsAddedAfterV18` on **both** the export and the import side — the defect that has already happened once |
