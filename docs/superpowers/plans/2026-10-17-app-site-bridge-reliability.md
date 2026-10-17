# App ↔ Website Bridge Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every customer request reaches the owner's phone, the site never quotes a price or a free date the app disagrees with, and the app says so itself when either breaks.

**Architecture:** Two repositories joined only by three Firestore collections. The app's inbound fetch moves from an unordered 300-document list to a watermarked range query; the hourly sync gains an outbound half so availability is published without a human tap; the outbox stops blocking on its first failure; and one computed verdict, `BridgeHealth`, turns the signals that already exist into a dashboard card and a notification. The site stops quoting a build-time price and records which price it used.

**Tech Stack:** Flutter 3.47.5 / Dart, sqflite, Firestore REST over `package:http` (no Firebase SDK). Static site: Python `build.py`, vanilla JS, Firestore Web SDK, `firestore.rules`.

**Spec:** `docs/superpowers/specs/2026-10-17-app-site-bridge-reliability-design.md`

## Global Constraints

- **Schema changes are additive only.** Every new column is nullable or has a `DEFAULT`; nothing is renamed or dropped. A database written by the new build must still open in the old one.
- **Every new column must be listed in `_columnsAddedAfterV18` on BOTH the export side (`buildEnvelope`) and the import side (`_restoreRows`).** Listing it on one side only is a defect that has already shipped once.
- **Firestore rules must be deployed before the site that writes `priceSource`** (Task 1 before Task 17). `hasOnly` rejects an unlisted key, so the reverse order rejects every booking.
- **Never `git add -A` in the site repository.** Another agent commits to it concurrently. Stage named paths only, commit immediately, never force-push.
- **No Firebase SDK in the app.** REST over `package:http`, as the existing code does.
- **`DashboardSectionX.id` values are persisted.** Never change an existing one; only add.
- **App test command:** `flutter test test/<file>.dart --plain-name '<test name>'`. Site JS test command: `node tests/<name>.test.js`. Site Python: `python -m unittest tests.test_<name>`.
- Georgian is the app's and the site's owner-facing language; all new user-visible copy is Georgian.

## Review Focus

Five input classes the spec implies but whose tests no task would otherwise carry. Each line's test is added to the task named.

1. **Two bookings carrying the identical server timestamp.** A strict `created > watermark` loses the second one forever. Expected: both absorbed, no request skipped. → Task 3.
2. **A `created` timestamp the app cannot parse** (missing, empty, or a format variant). Falling back to epoch refetches everything each run; falling back to `now` skips everything. Expected: an unparseable timestamp advances nothing and is reported, never silently treated as either extreme. → Task 3.
3. **The app opened after a week closed, with the dirty flag set and the 12-hour timer long expired.** Expected: exactly one publish, not one per dirty action, and the backlog of requests announced once rather than once per request per run. → Task 8 (publish), Task 15 (announce).
4. **A car whose `model_slug` the owner edits after it was published.** The documents under the old slug keep selling a car at a price nothing updates. Expected: the old slug is retired. → Task 9.
5. **A booking with a missing or malformed `start` / `end`.** Expected: the row is still absorbed and visible so the owner can see and decline it, rather than dropped or crashing the run. → Task 14.

---

## File Structure

### Site repository (`C:\Projects\car-rental-site\car-rental-site`)

| File | Responsibility | Tasks |
|---|---|---|
| `firestore.rules` | `priceSource` joins the `bookings` create `hasOnly` list | 1 |
| `tests/test_sitegen.py` | textual guard that the rules list contains `priceSource` | 1 |
| `static/booking.js` | await the live price, record `priceSource`, 72-hour trust, idempotency, offline timeout, drop the dead Netlify post | 17, 18, 19 |
| `static/catalogue.js` | 72-hour trust; stop writing a stale price into `FH_CFG.cars` | 18 |
| `tests/booking.test.js` (new) | `booking.js` under `vm` against a faked DOM | 17, 18, 19 |
| `tests/test_booking_js.py` (new) | gate wrapper for the above, mirroring `test_catalogue_js.py` | 17 |
| `docs/superpowers/plans/…` | this plan | — |

### App repository (`src/leasor`)

| File | Responsibility | Tasks |
|---|---|---|
| `lib/services/cloud/firestore_rest.dart` | a range query; a guarded `CloudDocument` | 2, 14 |
| `lib/services/cloud/cloud_sync_service.dart` | watermarked inbox, id-refresh, non-blocking drain | 3, 4, 6, 14 |
| `lib/database/database_helper.dart` | `sync_outbox.status` (schema 26), announced-ids table | 5, 15 |
| `lib/services/backup_service.dart` | the new columns on both sides of the envelope | 5 |
| `lib/services/cloud/cloud_config.dart` | `lastPublishAt`, `fleetDirty`, 72-hour trust window | 7, 18 |
| `lib/services/cloud/fleet_publisher.dart` | `retired` tombstones | 9 |
| `lib/services/cloud/bridge_health.dart` (new) | the computed verdict | 10 |
| `lib/services/cloud/web_sync.dart` | publish when due or dirty; announce from the database | 8, 15 |
| `lib/providers/app_state.dart` | mark dirty on mutation; overdue rental blocks the car | 7, 13 |
| `lib/models/web_booking.dart` | local-time day parsing | 12 |
| `lib/models/dashboard_section.dart` + `lib/screens/dashboard_screen.dart` | the health card | 11 |
| `lib/screens/car_detail_screen.dart`, `lib/services/photo_export.dart` | slug parity | 16 |

---

## Phase A — the rules, first

### Task 1: `priceSource` is allowed before anything writes it

**Files:**
- Modify: `firestore.rules:75` (the `bookings` create `hasOnly` list)
- Test: `tests/test_sitegen.py`

**Interfaces:**
- Consumes: nothing.
- Produces: the deployed rules accept a `bookings` document carrying `priceSource`. Task 17 depends on this being **deployed**, not merely committed.

- [ ] **Step 1: Write the failing test**

In `tests/test_sitegen.py`, a new test:

```python
def test_rules_allow_the_price_source_field(self):
    rules = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    create = rules.split("match /bookings/{id}")[1].split("allow update")[0]
    self.assertIn("'priceSource'", create,
                  "booking.js წერს priceSource-ს; hasOnly-ში არ არის — "
                  "ყველა ჯავშანი უარყოფილი იქნება")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m unittest tests.test_sitegen -k price_source -v`
Expected: FAIL — `'priceSource'` not found.

- [ ] **Step 3: Add `'priceSource'` to the `hasOnly` list in `firestore.rules:75`**

Append it to the existing array. `hasOnly` is a subset check, so a document that omits the key is still accepted — the change is backward compatible and the currently deployed site keeps working.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest tests.test_sitegen -k price_source -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add firestore.rules tests/test_sitegen.py
git commit -m "წესები: priceSource დაშვებულია (საიტამდე)"
```

- [ ] **Step 6: The owner deploys the rules**

This step is the owner's: double-click `DEPLOY-RULES.bat` and confirm `OK - rules published.` **Task 17 does not start until this has happened.** A deploy failure means the Firebase CLI needs `npm install -g firebase-tools`; the log is `deploy-rules.log`.

---

## Phase B — the inbox stops having a ceiling

### Task 2: a range query on the REST client

**Files:**
- Modify: `lib/services/cloud/firestore_rest.dart` (new method beside `queryWhereEquals:315`)
- Test: `test/cloud_bridge_test.dart`

**Interfaces:**
- Consumes: the private `_client`, `_host`, `_root`, `_headers()`, `_throwIfFailed`, `encodeValue` and the `runQuery` row-decoding already used by `queryWhereEquals`.
- Produces:

```dart
Future<List<CloudDocument>> queryRange(
  String collection, {
  required String field,
  Object? greaterThan,
  int limit = 300,
  bool descending = false,
})
```

Orders by `field` (ascending unless `descending`). When `greaterThan` is null the `where` clause is omitted, which is how the first run reads the newest documents.

- [ ] **Step 1: Write the failing tests**

In `test/cloud_bridge_test.dart`, against the existing `_FakeClient`:

```dart
test('queryRange asks Firestore for a bounded, ordered range', () async {
  // capture the posted body
  expect(body['structuredQuery']['orderBy'][0]['field']['fieldPath'], 'created');
  expect(body['structuredQuery']['orderBy'][0]['direction'], 'ASCENDING');
  expect(body['structuredQuery']['where']['fieldFilter']['op'], 'GREATER_THAN');
  expect(body['structuredQuery']['limit'], 300);
});

test('queryRange omits the filter when there is no watermark', () async {
  expect(body['structuredQuery'].containsKey('where'), isFalse);
  expect(body['structuredQuery']['orderBy'][0]['direction'], 'DESCENDING');
});

test('queryRange ignores a readTime-only heartbeat row', () async {
  // a runQuery reply of [{readTime: ...}] decodes to zero documents, not a crash
  expect(docs, isEmpty);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'queryRange'`
Expected: FAIL — `queryRange` is not defined.

- [ ] **Step 3: Implement `queryRange` in `firestore_rest.dart`**

Mirror `queryWhereEquals`: same `from`, same `_throwIfFailed` label style, same row loop that skips a row with no `document` key. The filter is `fieldFilter` with `op: 'GREATER_THAN'` and `value: encodeValue(greaterThan)`, omitted entirely when `greaterThan` is null.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'queryRange'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/firestore_rest.dart test/cloud_bridge_test.dart
git commit -m "REST: დიაპაზონის მოთხოვნა (queryRange)"
```

### Task 3: the inbox reads by watermark, not by luck

**Files:**
- Modify: `lib/services/cloud/cloud_sync_service.dart:204-230` (`sync`)
- Test: `test/cloud_bridge_test.dart`

**Interfaces:**
- Consumes: `FirestoreRest.queryRange` (Task 2); `DatabaseHelper.syncState(String key)` and `setSyncState(String key, String value)` (`database_helper.dart:2437,2449`).
- Produces, on `CloudSyncService`: `static const String watermarkKey = 'bookings_created_watermark';` and `bool lastFetchWasFull` (true when the range query returned exactly `fetchLimit` rows — Task 10 reads it as the truncation canary). On `SyncReport`: a new `final int skipped` field, defaulting to 0, counting documents this run could not use; `fetched` now counts only what this run actually read.

- [ ] **Step 1: Delete the test that asserts the defect**

`test/cloud_bridge_test.dart:247-276` (*"follows page tokens and stops at the limit"*) asserts that the fetch discards the page cursor at the limit. That was the ceiling. Remove the `capped` assertions; keep the page-token-following assertions, which are still correct behaviour for `listDocuments`.

- [ ] **Step 2: Write the failing tests**

```dart
test('a booking whose id sorts below the first 300 is still absorbed', () async {
  // 300 documents with ids 'z…', then one with id 'a…' and the newest `created`
  expect(absorbed.map((b) => b.id), contains('a-newest'));
});

test('the second run asks only for what is newer', () async {
  // run once; assert the second posted body's GREATER_THAN value
  expect(secondBody['structuredQuery']['where']['fieldFilter']['value'],
      <String, Object?>{'timestampValue': '2026-10-17T09:00:00Z'});
});

test('the first run with no watermark reads the newest descending', () async {
  expect(firstBody['structuredQuery']['orderBy'][0]['direction'], 'DESCENDING');
  expect(firstBody['structuredQuery'].containsKey('where'), isFalse);
});

// Review Focus 1
test('two bookings sharing one created timestamp are both absorbed', () async {
  // both carry created == '2026-10-17T09:00:00Z'; run twice
  expect(absorbedIds, containsAll(<String>['twin-a', 'twin-b']));
});

// Review Focus 2
test('an unparseable created timestamp does not move the watermark', () async {
  // a document with created == '' alongside a good one
  expect(await db.syncState(CloudSyncService.watermarkKey),
      '2026-10-17T09:00:00Z');       // the good one, not epoch and not now
  expect(report.skipped, 1);
});

test('a full page sets the truncation canary', () async {
  expect(service.lastFetchWasFull, isTrue);
});
```

- [ ] **Step 3: Run them to verify they fail**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'watermark'` and `--plain-name 'absorbed'`
Expected: FAIL — the fetch is still `listDocuments`.

- [ ] **Step 4: Replace the fetch in `sync()`**

Read the stored watermark; call `queryRange(bookingsCollection, field: 'created', greaterThan: watermark, limit: fetchLimit, descending: watermark == null)`. After `_absorb`, advance the watermark to the newest **parseable** `created` seen in this run and persist it.

Review Focus 1's fix is in this step: the watermark is advanced to the newest `created`, and because the filter is strictly `>`, a document sharing that exact timestamp would be lost — so re-request from one millisecond **before** the newest seen timestamp and rely on `_absorb` already being idempotent for a known id (`cloud_sync_service.dart:264`). Review Focus 2's fix is also here: a document whose `created` does not parse is absorbed but contributes nothing to the watermark, and increments a `skipped` count on `SyncReport`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `flutter test test/cloud_bridge_test.dart`
Expected: PASS, whole file.

- [ ] **Step 6: Commit**

```bash
git add lib/services/cloud/cloud_sync_service.dart test/cloud_bridge_test.dart
git commit -m "შემომავალი: watermark 300-დოკუმენტიანი ჭერის ნაცვლად"
```

### Task 4: answers to requests already on the phone

**Files:**
- Modify: `lib/services/cloud/cloud_sync_service.dart` (`sync`)
- Modify: `lib/screens/web_bookings_screen.dart:271`
- Test: `test/cloud_bridge_test.dart`, `test/web_booking_flow_test.dart`

**Interfaces:**
- Consumes: `FirestoreRest.getDocument(String collection, String id)` (`firestore_rest.dart:249`), which returns `Map<String, Object?>?` — null on 404.
- Produces: nothing new for later tasks.

- [ ] **Step 1: Write the failing tests**

```dart
test('a pending request gets its remote status refreshed by id', () async {
  expect(reloaded.status, 'cancelled');
});

test('a pending request whose document is gone is recorded as withdrawn', () async {
  expect(reloaded.isCancelledRemotely, isTrue);
});

test('answered requests are not re-fetched', () async {
  expect(getDocumentCalls, 1);   // only the one still awaiting an answer
});

test('a cancellation after acceptance is shown, not hidden', (tester) async {
  // booking.isCancelledRemotely == true, booking.isNew == false
  expect(find.textContaining('გაუქმებულია'), findsOneWidget);
});
```

The last test is spec §5.2's invisible cancellation: the warning at
`web_bookings_screen.dart:271` is gated on `booking.isNew`, so an
accepted-then-cancelled request keeps blocking the car and sitting in the P&L
with nothing on screen. Dropping `&& booking.isNew` is the whole fix.

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'by id'`
Expected: FAIL

- [ ] **Step 3: Add the id-refresh pass to `sync()`, and ungate the cancellation warning**

For each local `web_booking` still awaiting an answer, `getDocument`; a non-null reply refreshes `status` / `paymentStatus` through the same path `_absorb` uses, a null reply marks it withdrawn. Separately, remove `&& booking.isNew` from the warning condition at `web_bookings_screen.dart:271`.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/cloud_sync_service.dart lib/screens/web_bookings_screen.dart test/cloud_bridge_test.dart test/web_booking_flow_test.dart
git commit -m "შემომავალი: პასუხის განახლება id-ით; გაუქმება ჩანს მიღების შემდეგაც"
```

---

## Phase C — the outbox stops blocking

### Task 5: `sync_outbox.status` (schema 26)

**Files:**
- Modify: `lib/database/database_helper.dart:641-656` (table), the `_addColumnIfMissing` migration block, `schemaVersion`
- Modify: `lib/services/backup_service.dart` (`_columnsAddedAfterV18`, `buildEnvelope`, `_restoreRows`)
- Test: `test/migrations_test.dart`, `test/drive_backup_test.dart`

**Interfaces:**
- Produces: `sync_outbox.status TEXT NOT NULL DEFAULT 'pending'`, values `'pending'` and `'failed'`. `DatabaseHelper.getOutbox({int limit})` (`:2408`) gains a `bool includeFailed = false` parameter; `DatabaseHelper.failedOutboxCount()` returns `Future<int>`.

- [ ] **Step 1: Write the failing tests**

```dart
// migrations_test.dart
test('schema 26 adds sync_outbox.status defaulting to pending', () async {
  expect(columns['status'], isNotNull);
  expect(row['status'], 'pending');
});

test('a v25 database opens at v26 without losing an outbox row', () async {
  expect(rows, hasLength(1));
});

// drive_backup_test.dart
test('a v9 envelope carries sync_outbox.status and restores it', () async {
  expect(restored.first['status'], 'failed');
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/migrations_test.dart test/drive_backup_test.dart --plain-name 'status'`
Expected: FAIL — no such column.

- [ ] **Step 3: Add the column, bump `schemaVersion` to 26, and list it on both sides of the envelope**

`_addColumnIfMissing('sync_outbox', 'status', "TEXT NOT NULL DEFAULT 'pending'")`, and add `'status'` to `sync_outbox`'s entry in `_columnsAddedAfterV18` so **both** `buildEnvelope` and `_restoreRows` carry it. Add `includeFailed` to `getOutbox` and `failedOutboxCount()`.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Run the whole suite** — Run: `flutter test` · Expected: all green.
- [ ] **Step 6: Commit**

```bash
git add lib/database/database_helper.dart lib/services/backup_service.dart test/migrations_test.dart test/drive_backup_test.dart
git commit -m "სქემა 26: sync_outbox.status"
```

### Task 6: one failure no longer blocks the rest

**Files:**
- Modify: `lib/services/cloud/cloud_sync_service.dart:323-355` (`_drainOutbox`), `:204-230` (`sync`)
- Test: `test/cloud_bridge_test.dart`

**Interfaces:**
- Consumes: `getOutbox({includeFailed})`, `failedOutboxCount()`, `markOutboxFailure` (Task 5).
- Produces: `static const int maxOutboxAttempts = 5;` on `CloudSyncService`. `SyncReport.stuck` becomes the count of `failed` entries.

- [ ] **Step 1: Write the failing tests**

```dart
test('a failing entry does not block the entry behind it', () async {
  expect(delivered, contains('second'));
});

test('an entry that fails five times is marked failed and skipped after', () async {
  expect(row['status'], 'failed');
  expect(attemptsOnNextRun, 5);   // not 6 — it is no longer attempted
});

test('a malformed payload fails immediately rather than five times', () async {
  expect(row['attempts'], 1);
  expect(row['status'], 'failed');
});

test('sync reports an error when anything is failed', () async {
  expect(report.error, isNotNull);
  expect(await CloudConfig.lastResult(), isNot('ok'));
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'outbox'`
Expected: FAIL — the drain still `break`s and `sync` still records `ok`.

- [ ] **Step 3: Rewrite the drain loop**

Replace the `break` at `:349` with `continue`. Load only `pending` entries. On an exception, increment attempts and set `status = 'failed'` once attempts reach `maxOutboxAttempts`; a `jsonDecode` failure sets `failed` on the first attempt. In `sync()`, do not write `setLastResult('ok')` when `failedOutboxCount() > 0`.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/cloud_sync_service.dart test/cloud_bridge_test.dart
git commit -m "outbox: ერთი ჩავარდნა აღარ ბლოკავს დანარჩენს"
```

---

## Phase D — availability is published without a tap

### Task 7: the app knows when it last published, and when it is stale

**Files:**
- Modify: `lib/services/cloud/cloud_config.dart`
- Modify: `lib/providers/app_state.dart` (the mutating methods)
- Test: `test/fleet_publisher_test.dart`

**Interfaces:**
- Produces, on `CloudConfig`:

```dart
static const String prefLastPublishMs = 'cloud_last_publish_ms';
static const String prefFleetDirty    = 'cloud_fleet_dirty';
static Future<DateTime?> lastPublishAt();
static Future<void> markPublished(DateTime at);   // also clears the dirty flag
static Future<bool> isFleetDirty();
static Future<void> markFleetDirty();
static const Duration publishInterval = Duration(hours: 12);
```

- [ ] **Step 1: Write the failing tests**

```dart
test('publishing stamps the time and clears the dirty flag', () async {
  expect(await CloudConfig.isFleetDirty(), isFalse);
  expect(await CloudConfig.lastPublishAt(), isNotNull);
});

test('creating a rental marks the fleet dirty', () async {
  expect(await CloudConfig.isFleetDirty(), isTrue);
});

// the same assertion for each remaining mutation:
test('returning a rental marks the fleet dirty', () async {
  await app.returnRental(rental);
  expect(await CloudConfig.isFleetDirty(), isTrue);
});
// …and likewise for: accepting a web booking, editing a rental,
// changing a car's price, switching a car off the site, deleting a car.
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/fleet_publisher_test.dart --plain-name 'dirty'`
Expected: FAIL — `isFleetDirty` is not defined.

- [ ] **Step 3: Add the `CloudConfig` members, call `markPublished` at the end of `publishFleet` (`app_state.dart:901`), and `markFleetDirty` from each mutating method**

The mutations are: rental created, returned or edited; web booking accepted; a car's price, `isPublic` or archive state changed; a car deleted. Each is a single `await CloudConfig.markFleetDirty();` on the success path.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/cloud_config.dart lib/providers/app_state.dart test/fleet_publisher_test.dart
git commit -m "გამოქვეყნება: lastPublishAt და fleetDirty"
```

### Task 8: the hourly sync publishes too

**Files:**
- Modify: `lib/services/cloud/web_sync.dart:63-83` (`run`)
- Modify: `lib/providers/app_state.dart` (new method)
- Test: `test/web_booking_flow_test.dart`

**Interfaces:**
- Consumes: `CloudConfig.lastPublishAt`, `isFleetDirty`, `publishInterval` (Task 7).
- Produces: `Future<PublishReport?> AppState.publishFleetIfDue()` on `AppState` — null when nothing was due.

- [ ] **Step 1: Write the failing tests**

```dart
test('a sync 13 hours after the last publish writes availability', () async {
  expect(published, isTrue);
});

test('a sync 1 hour after the last publish does not publish', () async {
  expect(published, isFalse);
});

test('a dirty fleet publishes regardless of the interval', () async {
  expect(published, isTrue);
});

// Review Focus 3
test('a week of dirty mutations publishes once, not once each', () async {
  expect(publishCalls, 1);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/web_booking_flow_test.dart --plain-name 'publish'`
Expected: FAIL — `publishFleetIfDue` is not defined.

- [ ] **Step 3: Implement `publishFleetIfDue()` and call it from `WebSync.run` after `syncWebsite()`**

Due when `isFleetDirty()` or `lastPublishAt()` is null or older than `publishInterval`. It must not throw out of `run` — the existing `catch` at `:77` is the net, and a publish failure must still leave the inbound result intact.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/web_sync.dart lib/providers/app_state.dart test/web_booking_flow_test.dart
git commit -m "WebSync: ავტომატური გამოქვეყნება (12სთ ან ცვლილება)"
```

### Task 9: a car taken off the site stops selling

**Files:**
- Modify: `lib/services/cloud/fleet_publisher.dart` (`publish`)
- Modify: `static/catalogue.js`, `static/booking.js` (skip a retired document)
- Test: `test/fleet_publisher_test.dart`, `tests/catalogue.test.js`

**Interfaces:**
- Produces: `fleet/{slug}` and `availability/{slug}` may carry `retired: true` with `updatedAt`. Nothing else changes shape.

- [ ] **Step 1: Write the failing tests**

```dart
// fleet_publisher_test.dart
test('a car switched off the site is written as retired', () async {
  expect(written['fleet/audi-q5']!['retired'], true);
});

test('a retired slug is not counted as a published model', () async {
  expect(report.models, 0);
});

// Review Focus 4
test('a slug the owner renamed retires the old slug', () async {
  expect(written.keys, contains('fleet/audi-q5'));      // the old one, retired
  expect(written['fleet/audi-q5']!['retired'], true);
});
```

```javascript
// catalogue.test.js — case 10, in the file's existing numbered style
assert.equal(cardsFor('audi-q5').length, 0,
  'retired დოკუმენტი ბარათს აღარ ხატავს');
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/fleet_publisher_test.dart --plain-name 'retired'` and `node tests/catalogue.test.js`
Expected: FAIL both.

- [ ] **Step 3: Write the tombstone and skip it on the site**

In `publish`, compare the slugs present in Firestore (the publisher already reads them for its report) against the slugs it is about to write; any previously-published slug now absent gets `{retired: true, updatedAt: now}` on both collections. In `catalogue.js` and `booking.js`, a document whose `retired` is truthy is treated as absent.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS both
- [ ] **Step 5: Commit** (two repositories, two commits)

```bash
# app
git add lib/services/cloud/fleet_publisher.dart test/fleet_publisher_test.dart
git commit -m "გამოქვეყნება: retired გაყიდულ მანქანაზე"
# site
git add static/catalogue.js static/booking.js tests/catalogue.test.js
git commit -m "საიტი: retired დოკუმენტი აღარ ჩანს"
```

---

## Phase E — the bridge reports on itself

### Task 10: `BridgeHealth`

**Files:**
- Create: `lib/services/cloud/bridge_health.dart`
- Test: `test/bridge_health_test.dart` (new)

**Interfaces:**
- Consumes: `CloudConfig.lastPublishAt`, `lastResult` (`cloud_config.dart:90`), `availabilityTrustWindow`; `DatabaseHelper.outboxCount()` (`:2429`), `failedOutboxCount()` (Task 5); `CloudSyncService.lastFetchWasFull` (Task 3); `FleetReporter` (`fleet_report.dart:225`).
- Produces:

```dart
enum BridgeStatus { ok, warning, broken }

class BridgeHealth {
  const BridgeHealth({
    required this.status,
    required this.headline,
    this.action,
    required this.checkedAt,
  });
  final BridgeStatus status;
  final String headline;    // Georgian, one sentence
  final String? action;
  final DateTime checkedAt;

  static Future<BridgeHealth> compute({
    required DatabaseHelper db,
    DateTime? now,
  });
}
```

Thresholds, exactly as the spec fixes them: availability age ≥ 48 h → `warning`, ≥ 72 h → `broken`; any failed outbox entry → `broken`; a queued entry older than 6 h → `warning`; a full inbox page → `warning`; any price mismatch → `warning`; `lastResult` not `'ok'` → `broken`. **Only the worst signal is reported**, and `headline` names that one problem.

- [ ] **Step 1: Write the failing tests**

```dart
test('a fresh bridge is ok and says nothing', () async {
  expect(health.status, BridgeStatus.ok);
});

test('availability 50 hours old warns', () async {
  expect(health.status, BridgeStatus.warning);
});

test('availability 73 hours old is broken', () async {
  expect(health.status, BridgeStatus.broken);
});

test('a failed outbox entry is broken even when everything else is fresh', () async {
  expect(health.status, BridgeStatus.broken);
});

test('only the worst problem is named', () async {
  // stale availability AND a failed entry
  expect(health.headline, contains('გაუგზავნელი'));
  expect(health.headline, isNot(contains('ხელმისაწვდომობა')));
});

test('a full inbox page warns', () async {
  expect(health.status, BridgeStatus.warning);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/bridge_health_test.dart`
Expected: FAIL — the file does not compile; `BridgeHealth` is not defined.

- [ ] **Step 3: Implement `BridgeHealth.compute`**

Collect the signals, keep the worst by `BridgeStatus` order, and build the headline from a `switch` on which signal won. Every `headline` and `action` string is Georgian.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/bridge_health.dart test/bridge_health_test.dart
git commit -m "BridgeHealth: ხიდის თვითშემოწმება"
```

### Task 11: the owner sees it without looking for it

**Files:**
- Modify: `lib/models/dashboard_section.dart` (enum + `id` + `label` + `hint`)
- Modify: `lib/screens/dashboard_screen.dart`
- Modify: `lib/services/cloud/web_sync.dart` (`run`)
- Test: `test/dashboard_sections_test.dart`, `test/bridge_health_test.dart`

**Interfaces:**
- Consumes: `BridgeHealth.compute` (Task 10).
- Produces: `DashboardSection.bridgeHealth` with `id == 'bridge_health'`; a `BridgeHealthCard` widget in `lib/screens/dashboard_screen.dart` taking a `BridgeHealth`; the previous status persisted under `CloudConfig.prefLastBridgeStatus` (a `String`, the `BridgeStatus.name`).

- [ ] **Step 1: Write the failing tests**

```dart
// dashboard_sections_test.dart
test('bridgeHealth has a stable id, a label and a hint', () {
  expect(DashboardSection.bridgeHealth.id, 'bridge_health');
  expect(DashboardSection.bridgeHealth.label, isNotEmpty);
  expect(DashboardSection.bridgeHealth.hint, isNotEmpty);
});

test('every section id is still unique', () { /* existing test must stay green */ });

// bridge_health_test.dart
test('the card renders nothing when the bridge is ok', (tester) async {
  expect(find.byType(BridgeHealthCard), findsNothing);
});

test('degradation notifies once, not on every run', () async {
  expect(notifications, 1);     // two runs, same broken status
});

test('recovery back to ok notifies nothing', () async {
  expect(notifications, 0);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/dashboard_sections_test.dart test/bridge_health_test.dart`
Expected: FAIL — the enum has no `bridgeHealth`; the `id`/`label`/`hint` switches are exhaustive, so this is a compile error that names each switch to update.

- [ ] **Step 3: Add the enum member, the three switch arms, the card, and the notification**

The card renders only when `status != ok`, following the dashboard's existing has-content rule. In `WebSync.run`, after the sync and the publish, compute the health and notify **only** when the status is worse than the persisted previous one; then persist the new status.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Run the whole suite** — Run: `flutter test` · Expected: all green.
- [ ] **Step 6: Commit**

```bash
git add lib/models/dashboard_section.dart lib/screens/dashboard_screen.dart lib/services/cloud/web_sync.dart test/dashboard_sections_test.dart test/bridge_health_test.dart
git commit -m "დაფა: ხიდის მდგომარეობის ბარათი და გაფრთხილება"
```

---

## Phase F — correctness the spec lists under §5

### Task 12: a date from the site is the date the customer meant

**Files:**
- Modify: `lib/models/web_booking.dart:430-435` (`_day`)
- Test: `test/web_booking_flow_test.dart`

- [ ] **Step 1: Write the failing tests**

```dart
test('a Z-suffixed start of 20 October is 20 October in Georgia', () {
  expect(WebBooking.fromCloud(fieldsWithStart('2026-10-20T00:00:00Z')).start,
      DateTime(2026, 10, 20));
});

test('a date-only start is unchanged', () {
  expect(parsed.start, DateTime(2026, 10, 20));
});

test('the night count does not shift when only one end carries a zone', () {
  expect(booking.days, 3);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/web_booking_flow_test.dart --plain-name 'October'`
Expected: FAIL — 19 October.

- [ ] **Step 3: Call `.toLocal()` before reading the parts in `_day`**

`DateTime.tryParse` returns a UTC instant for a `Z`-suffixed string and a local one otherwise; `.toLocal()` makes both read the same way.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/models/web_booking.dart test/web_booking_flow_test.dart
git commit -m "თარიღი: UTC-ის გამო ერთი დღით წინ აღარ იწევს"
```

### Task 13: a car that has not come back is not free

**Files:**
- Modify: `lib/providers/app_state.dart:2027-2030` (`isCarFreeBetween`)
- Test: `test/fleet_publisher_test.dart`

- [ ] **Step 1: Write the failing tests**

```dart
test('an overdue open rental still blocks the car', () {
  // endDate was three days ago, actualEndDate is null
  expect(app.isCarFreeBetween(car, from: tomorrow, to: dayAfter), isFalse);
});

test('a returned rental stops blocking on its actual end date', () {
  expect(app.isCarFreeBetween(car, from: tomorrow, to: dayAfter), isTrue);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/fleet_publisher_test.dart --plain-name 'overdue'`
Expected: FAIL — the car reads as free.

- [ ] **Step 3: Treat an open rental with no `actualEndDate` as blocking indefinitely**

The fallback to `DateTime.now()` becomes a far-future sentinel for an open rental; a rental with an `actualEndDate` is unchanged.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/providers/app_state.dart test/fleet_publisher_test.dart
git commit -m "ხელმისაწვდომობა: ვადაგადაცილებული მანქანა თავისუფალი არ არის"
```

### Task 14: one bad document is one bad document

**Files:**
- Modify: `lib/services/cloud/firestore_rest.dart:393-410` (`CloudDocument`), `lib/services/cloud/cloud_sync_service.dart:264` (`_absorb`)
- Test: `test/cloud_bridge_test.dart`

**Interfaces:**
- Produces: `SyncReport.skipped` (`int`), already introduced in Task 3, now also counting documents that threw.

- [ ] **Step 1: Write the failing tests**

```dart
test('a document with a non-string status skips only itself', () async {
  expect(absorbedIds, contains('good-after-the-bad'));
  expect(report.skipped, 1);
});

// Review Focus 5
test('a booking with no start is still absorbed so it can be declined', () async {
  expect(absorbedIds, contains('no-dates'));
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/cloud_bridge_test.dart --plain-name 'skips only itself'`
Expected: FAIL — the cast throws and the run stops.

- [ ] **Step 3: Make `CloudDocument.string` tolerant and wrap each document in `_absorb`**

`string` returns `fields[key]?.toString() ?? ''` rather than casting. `_absorb` wraps each document in a `try`; a throw increments `skipped` and continues. A booking missing its dates is absorbed with null dates so the owner can see and decline it.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/services/cloud/firestore_rest.dart lib/services/cloud/cloud_sync_service.dart test/cloud_bridge_test.dart
git commit -m "შემომავალი: ერთი გაუგებარი დოკუმენტი აღარ აჩერებს დანარჩენს"
```

### Task 15: a request is announced once, whichever path found it

**Files:**
- Modify: `lib/database/database_helper.dart` (new `announced_bookings` table, schema 27)
- Modify: `lib/services/cloud/web_sync.dart:45,89-102` (`_announced`, `_announce`)
- Modify: `lib/services/backup_service.dart`
- Test: `test/web_booking_flow_test.dart`, `test/migrations_test.dart`

**Interfaces:**
- Produces: `DatabaseHelper.isAnnounced(String bookingId)` → `Future<bool>`, `DatabaseHelper.markAnnounced(String bookingId)` → `Future<void>`. The in-memory `WebSync._announced` set is deleted.

- [ ] **Step 1: Write the failing tests**

```dart
test('a request first seen by a manual sync is still announced', () async {
  expect(notified.map((b) => b.id), contains('seen-elsewhere-first'));
});

test('a request already announced is not announced again after a restart', () async {
  expect(notified, isEmpty);
});

// Review Focus 3
test('a backlog of five requests is announced once as five, not five times', () async {
  expect(notificationCalls, 1);
  expect(notified, hasLength(5));
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/web_booking_flow_test.dart --plain-name 'announce'`
Expected: FAIL

- [ ] **Step 3: Add the table at schema 27, list it on both sides of the envelope, and rewrite `_announce` to query it**

`_announce` no longer takes a `before` snapshot: it selects every `web_booking` that still needs an answer and is not in `announced_bookings`, notifies them in one call, and marks them.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/database/database_helper.dart lib/services/cloud/web_sync.dart lib/services/backup_service.dart test/web_booking_flow_test.dart test/migrations_test.dart
git commit -m "შეტყობინება: გამოცხადებული მოთხოვნები ბაზაში (სქემა 27)"
```

### Task 16: one slug, everywhere

**Files:**
- Modify: `lib/screens/car_detail_screen.dart:1635`
- Modify: `lib/services/photo_export.dart`
- Test: `test/fleet_publisher_test.dart`, `test/photo_export_test.dart`

**Interfaces:**
- Consumes: `SiteModels.slugFor(make, model)` (`lib/models/site_model.dart`), the same derivation `FleetPublisher.publish` uses.
- Produces: `static String siteSlug(Car car)` — the single derivation (`car.modelSlug` when set, otherwise `SiteModels.slugFor`), defined once on `FleetPublisher` and re-exported by `PhotoExport.siteSlug` so both tests can name it.

- [ ] **Step 1: Write the failing tests**

```dart
test('the car page publishes only its own car', () async {
  expect(publishedSlugs, <String>['tesla-model-3']);   // not the whole fleet
});

test('photo export uses the same derived slug as the publisher', () {
  expect(PhotoExport.siteSlug(car), FleetPublisher.siteSlug(car));
});

test('rebuilding the mapping keeps a hand-picked slug\'s images', () {
  expect(mapping['audi-q5'], isNotEmpty);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `flutter test test/fleet_publisher_test.dart test/photo_export_test.dart --plain-name 'slug'`
Expected: FAIL — an empty `modelSlug` publishes everything.

- [ ] **Step 3: Pass the derived slug from the car page, and derive the same way in `photo_export`**

Extract the publisher's derivation into one shared function and call it from both; `buildMapping` merges into the existing mapping rather than replacing it.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add lib/screens/car_detail_screen.dart lib/services/photo_export.dart test/fleet_publisher_test.dart test/photo_export_test.dart
git commit -m "slug: ერთი წარმოშობა გამოქვეყნებასა და ფოტოში"
```

---

## Phase G — the site

### Task 17: the form quotes the price that is true now

**Files:**
- Modify: `static/booking.js:130-150` (the submit handler), `:239` (`sendToCloud`)
- Create: `tests/booking.test.js`, `tests/test_booking_js.py`
- **Blocked on:** Task 1 Step 6 — the rules must be deployed.

**Interfaces:**
- Consumes: `fetchLive(slug)` (`booking.js:313`), which already caches its promise in `LIVE[slug]` and overwrites `FH_CFG.cars[slug]` when the document is fresh; `drawQuote()` (`:79`), which reads `FH_CFG.cars`.
- Produces: the `bookings` document gains `priceSource: 'live' | 'built'`.

- [ ] **Step 1: Create the harness and write the failing tests**

`tests/booking.test.js` mirrors `tests/catalogue.test.js`: read `static/booking.js`, run it under `vm` against a faked DOM and a real-shaped Firestore reply. `tests/test_booking_js.py` mirrors `tests/test_catalogue_js.py` exactly, including the `node`-missing skip and the two file-exists assertions.

```javascript
// 1. a submit waits for the live price and writes it
// 2. priceSource is 'live' when the live document was used
// 3. priceSource is 'built' when the live fetch times out
// 4. a live fetch that never resolves does not hang the submit past 3s
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node tests/booking.test.js`
Expected: FAIL — the baked price is written and there is no `priceSource`.

- [ ] **Step 3: Await the live price in the submit handler, then quote**

Race `fetchLive(q.slug)` against a 3 s timer; after it settles, call `drawQuote()` again so it reads whatever `fetchLive` wrote into `FH_CFG.cars`, and pass a `priceSource` of `'live'` when the live document won and `'built'` otherwise. `sendToCloud` adds the field to the document.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node tests/booking.test.js && python -m unittest tests.test_booking_js -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add static/booking.js tests/booking.test.js tests/test_booking_js.py
git commit -m "ჯავშანი: ცოცხალ ფასს ელოდება, priceSource-ს წერს"
```

### Task 18: one trust window, 72 hours, on both sides

**Files:**
- Modify: `static/booking.js:291` (`TRUST_MS`), `static/catalogue.js:56` (`TRUST_MS`), `static/catalogue.js:220-226`
- Modify: `lib/services/cloud/cloud_config.dart:43` (`availabilityTrustWindow`)
- Test: `tests/booking.test.js`, `tests/catalogue.test.js`, `test/bridge_health_test.dart`

- [ ] **Step 1: Write the failing tests**

```javascript
// booking.test.js
// 5. a 60-hour-old availability document is still trusted
// 6. a 73-hour-old availability document is not trusted
// catalogue.test.js
// 11. a 30-day-old fleet document does not reach FH_CFG.cars
```

```dart
test('the app trusts availability for 72 hours', () {
  expect(CloudConfig.availabilityTrustWindow, const Duration(hours: 72));
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node tests/booking.test.js && node tests/catalogue.test.js`
Expected: FAIL — 48 hours and 30 days respectively.

- [ ] **Step 3: Set both `TRUST_MS` to 72 hours, the Dart constant to 72 hours, and make `catalogue.js` apply its own freshness check before writing `cfg.cars`**

`catalogue.js` currently writes prices from documents up to 30 days old into the very map `booking.js` quotes from; the same `freshDoc` window must gate that write.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS all three
- [ ] **Step 5: Commit** (two repositories, two commits)

```bash
# site
git add static/booking.js static/catalogue.js tests/booking.test.js tests/catalogue.test.js
git commit -m "ნდობის ფანჯარა: 72 საათი ორივე მხარეს"
# app
git add lib/services/cloud/cloud_config.dart test/bridge_health_test.dart
git commit -m "ნდობის ფანჯარა: 72 საათი აპში"
```

### Task 19: the submit tells the truth

**Files:**
- Modify: `static/booking.js:130-170` (submit), `:401-411` (`postForm`), `:239` (`sendToCloud`)
- Test: `tests/booking.test.js`

**Interfaces:**
- Produces: a client-generated `requestId` held in the form's dataset for the life of the page, so a retry after a transport error does not create a second booking.

- [ ] **Step 1: Write the failing tests**

```javascript
// 7. pressing Send twice after a transport error creates one booking, not two
// 8. an offline submit fails with a message within the timeout, not forever
// 9. no request is made to the Netlify origin
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node tests/booking.test.js`
Expected: FAIL

- [ ] **Step 3: Add the request id, a submit timeout, and delete `postForm` and `NETLIFY_ORIGIN`**

The Netlify endpoint is documented in the file itself as returning 404 and `no-cors` makes its failure invisible, so it contributes nothing; the code and the comment claiming it saves the lead both go. Keep `ajaxifyForms` for the non-booking forms that rely on it.

- [ ] **Step 4: Run the tests to verify they pass** — Expected: PASS
- [ ] **Step 5: Commit**

```bash
git add static/booking.js tests/booking.test.js
git commit -m "ჯავშანი: იდემპოტენტურობა, ტაიმაუტი, მკვდარი Netlify-ს წაშლა"
```

---

## Phase H — close out

### Task 20: the holiday surcharge — the owner decides

**Files:** `content/settings/booking.yml`, and `build.py:257` only if the key is removed.

**Blocked on the owner.** `holiday_percent: 10` is published to every page and nothing reads it, because no holiday dates exist anywhere in the repository. Spec §5.3. Two outcomes:

- [ ] **(a)** The owner supplies the dates → add `holiday_dates` to `booking.yml`, publish it alongside `holidayPercent`, and apply the surcharge in `quoteFor` the way `peakNights` (`booking.js:195`) already does, with a test for a stay that straddles one holiday night.
- [ ] **(b)** The owner declines → delete `holiday_percent` from `booking.yml` and `build.py:257`, with a test asserting the key is gone, so the configuration stops describing a charge the business does not make.

Do not implement either without his answer.

### Task 21: prove it on the live system

- [ ] **Step 1: App gates**

Run: `flutter analyze` → no issues. Run: `flutter test` → all green (510 before this plan, plus everything added here).

- [ ] **Step 2: Site gates**

Run: `python -m pytest tests/ -q` and `node tests/booking.test.js && node tests/catalogue.test.js` → all green. Run the build and confirm the page count is unchanged.

- [ ] **Step 3: Push the site and deploy**

The owner runs `PUSH-NOW.bat` (its `WANT=` must be updated to the final commit first, and the script refuses unless that commit's parent is `origin/main`), then on GitHub: Actions → "Quality Gate and Manual Deploy" → Run workflow → `deploy: true`.

- [ ] **Step 4: The end-to-end check**

Submit a real request on the deployed site. Confirm it appears on the phone within one sync, that its `priceSource` reads `live`, answer it, and confirm the answer is visible on the site. Then switch a car off the site and confirm, after a sync, that it stops being offered.

**Nothing in this plan is called finished until Step 4 has passed.** Unit tests prove the pieces; only this proves the bridge.

- [ ] **Step 5: Build the APK and install it**

The release build needs `android/carrental-release.jks` and `key.properties`, which live only on the owner's computer. Build with `--target-platform android-arm64`.
