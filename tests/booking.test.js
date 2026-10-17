/* booking.js — გაგზავნის შემოწმება ნამდვილი ბრაუზერის გარეშე.
   ═══════════════════════════════════════════════════════════════════

   ფორმა კლიენტის ფულს ითვლის და ჯავშანში წერს. შეცდომა აქ deploy-ის
   შემდეგ ჩანს — ანუ კლიენტის ჯავშანში, არასწორი ფასით. ეს ჰარნესი
   `static/booking.js`-ს ნამდვილ ტექსტს ასრულებს `vm`-ში, DOM-ის იმ ნაწილით,
   რომელსაც სკრიპტი ეხება, Firestore-ის REST პასუხის ნამდვილი ფორმითა და
   ხელოვნური საათით (რომ 3-წამიანი ლოდინი ტესტს 3 წამით არ აჩერებდეს).

   რას ამოწმებს — ყველა მათგანი რეალური ზიანია, არა სტილი:
     1. გაგზავნა ცოცხალ ფასს ელოდება და სწორედ მას წერს
     2. priceSource არის 'live', როცა ცოცხალი დოკუმენტი გამოიყენეს
     3. priceSource არის 'built', როცა ცოცხალი მოთხოვნა დრომ გადაჭრა
     4. არასოდეს პასუხობადი მოთხოვნა გაგზავნას 3 წამზე მეტხანს არ აყოვნებს
     5. 60 საათის კალენდარი ჯერ კიდევ სანდოა (72-საათიანი ფანჯარა)
     6. 73 საათის კალენდარი უკვე უგულებელყოფილია
     7. „გაგზავნა" ორჯერ ტრანსპორტის შეცდომის შემდეგ ერთ ჯავშანს ქმნის
     8. ოფლაინ გაგზავნა შეტყობინებით სრულდება და არა უსასრულოდ
     9. Netlify-ს მისამართზე არავითარი მოთხოვნა არ გადის
    13. ცოცხალი ფასი ფორმაში ჩანს და ჩანაწერში 'live'-ია
    14. ჩაშენებული ფასი ფორმაში ჩანს და ჩანაწერში 'built'-ია
    15. ფასის გარეშე მანქანა: ფორმაში ციფრი არ ჩანს, იგზავნება, 'none'-ია
    16. ფიგურა უცვლელია — ერთი დაჭერა საკმარისია, 'live'
    17. ხელახალი დაჭერა: დოკუმენტი ქეშშია — წარმატებაა, ახალი ჩაწერა არ არის
    18. ხელახალი დაჭერა: ქსელი არ არის, ჩანაწერი უკვე არსებობს — წარმატებაა
    19. წესების უარყოფა წარმატებად არ ითვლება, ხელახლაც
    20. ლოდინისას მანქანა შეიცვალა: ეტიკეტი მეორე მანქანის ფასს აღწერს
    10. ძველი (ნდობის ფანჯრის გარეთ) ფასის დოკუმენტი 'live'-ად არ ითვლება */

const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

// The script ships from `static/`; this suite lives in `tests/` so the
// quality gate's unittest discovery can reach it.
const SRC = fs.readFileSync(__dirname + '/../static/booking.js', 'utf8');

const HOUR = 3600 * 1000;
const T = {
  sending: 'იგზავნება…',
  success: 'მოთხოვნა მიღებულია. ჯავშანი დადასტურებული არ არის, სანამ გადახდა არ შესრულდება.',
  failed: 'მოთხოვნა ვერ გაიგზავნა. სცადეთ ხელახლა.',
  busy: 'ამ თარიღებზე ეს მოდელი დაკავებული ჩანს — მოთხოვნას მაინც განვიხილავთ.',
};

// ── თარიღები ───────────────────────────────────────────────────────────
function ymd(offsetDays) {
  const d = new Date();
  d.setHours(12, 0, 0, 0);
  d.setDate(d.getDate() + offsetDays);
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') +
    '-' + String(d.getDate()).padStart(2, '0');
}
const ago = (ms) => new Date(Date.now() - ms).toISOString();

// ── Firestore REST-ის ნამდვილი ფორმა ───────────────────────────────────
function encode(v) {
  if (Array.isArray(v)) return { arrayValue: { values: v.map(encode) } };
  if (typeof v === 'number') {
    return Number.isInteger(v) ? { integerValue: String(v) } : { doubleValue: v };
  }
  if (typeof v === 'boolean') return { booleanValue: v };
  return { stringValue: String(v) };
}
function fsDocOf(col, slug, fields) {
  const out = {};
  Object.keys(fields).forEach(function (k) { out[k] = encode(fields[k]); });
  return { name: 'projects/p/databases/(default)/documents/' + col + '/' + slug, fields: out };
}

// ── DOM-ის მინიმალური ბაძვა ────────────────────────────────────────────
function makeRoot(fields) {
  const listeners = {};
  const els = {};
  const status = { textContent: '' };
  const quote = { textContent: '', parentNode: { insertBefore() {} } };
  const button = { disabled: false };
  function field(name) {
    if (!els[name]) {
      const el = { name: name, min: '', addEventListener() {} };
      // `value` reads and writes the same bag FormData reads from, as the
      // real form does.
      Object.defineProperty(el, 'value', {
        get() { return fields[name] === undefined ? '' : fields[name]; },
        set(v) { fields[name] = v; },
      });
      els[name] = el;
    }
    return els[name];
  }
  const root = {
    dataset: { lang: 'ka' },
    fields: fields,
    status: status,
    quote: quote,
    button: button,
    querySelector(sel) {
      const m = sel.match(/^\[name="(.+)"\]$/);
      if (m) return field(m[1]);
      if (sel === '.inquiry-status') return status;
      if (sel === '[data-quote]') return quote;
      if (sel === '[type="submit"]') return button;
      if (sel === '[data-inquiry-wa]') return { addEventListener() {} };
      return null;
    },
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    reportValidity() { return true; },
    reset() { Object.keys(fields).forEach(function (k) { delete fields[k]; }); },
    fire(ev) { (listeners[ev] || []).forEach(function (fn) { fn({ preventDefault() {} }); }); },
  };
  return root;
}

const settle = async () => { for (let i = 0; i < 25; i++) await new Promise((r) => setImmediate(r)); };

/// Boots the script against one fake form and returns handles on everything
/// the tests look at. `opts`:
///   built      — the price baked into FH_CFG.cars at build time
///   fleet      — fields of the live fleet document (null = 404)
///   avail      — fields of the live availability document (null = 404)
///   cars       — the whole FH_CFG.cars map (default: one baked car, audi-q5)
///   write      — 'hang' | 'lostAck' | 'denied' (default: accepted)
///   getMode    — 'cache' | 'unavailable' (default: the server answers)
///   fetchAfter — ms (fake clock) before fetch answers; default: at once
///   fetchHangs — fetch never answers (a phone in a tunnel)
async function start(opts) {
  opts = opts || {};
  const fields = Object.assign({
    start: ymd(1), end: ymd(3), car_slug: 'audi-q5', requested_car: 'Audi Q5',
    name: 'Nino Beridze', phone: '+995555123456', page_url: '',
  }, opts.fields || {});
  const root = makeRoot(fields);

  // ხელოვნური საათი: setTimeout არ ელოდება, advance() ამოქმედებს.
  let now = 0, seq = 0;
  const timers = [];
  const fetched = [];
  const db = { docs: {}, setCalls: 0, addCalls: 0 };
  const docListeners = {};

  const M = {
    auth: { signInAnonymously() { return Promise.resolve({ user: { uid: 'u1' } }); } },
    db: {
      serverTimestamp() { return 'TS'; },
      collection(_d, name) { return { col: name }; },
      doc(_d, col, id) { return { col: col, id: id }; },
      addDoc(c, data) {
        db.addCalls += 1;
        if (opts.write === 'denied') return Promise.reject({ code: 'permission-denied' });
        if (opts.write === 'hang') return new Promise(function () {});
        const id = 'auto' + (++seq);
        db.docs[c.col + '/' + id] = data;
        if (opts.write === 'lostAck' && db.addCalls === 1) {
          return Promise.reject({ code: 'unavailable' });
        }
        return Promise.resolve({ id: id });
      },
      setDoc(ref, data) {
        db.setCalls += 1;
        if (opts.write === 'denied') return Promise.reject({ code: 'permission-denied' });
        if (opts.write === 'hang') return new Promise(function () {});
        const key = ref.col + '/' + ref.id;
        // The real rules: a second write to an existing id is an update, and
        // a customer may not update a booking.
        if (db.docs[key]) return Promise.reject({ code: 'permission-denied' });
        db.docs[key] = data;
        if (opts.write === 'lostAck' && db.setCalls === 1) {
          return Promise.reject({ code: 'unavailable' });
        }
        return Promise.resolve();
      },
      getDoc(ref) {
        const key = ref.col + '/' + ref.id;
        // `getMode` models what an offline client does: answer from its
        // cache, or fail with `unavailable` when the cache has nothing.
        if (opts.getMode === 'cache') {
          return Promise.resolve({ exists() { return true; }, metadata: { fromCache: true } });
        }
        if (opts.getMode === 'unavailable') return Promise.reject({ code: 'unavailable' });
        // The real rules read `resource.data`, so asking for a document that
        // is not there is itself denied.
        if (!db.docs[key]) return Promise.reject({ code: 'permission-denied' });
        return Promise.resolve({ exists() { return true; }, metadata: { fromCache: false } });
      },
    },
  };

  const cfg = {
    projectId: 'p', whatsapp: '',
    cars: opts.cars || { 'audi-q5': opts.built || { p1: 100, p7: 90, p30: 80, dep: 500 } },
  };
  const sandbox = {
    window: {
      FH_CFG: cfg,
      FH: { firebase() { return Promise.resolve({ M: M, db: {}, auth: {} }); } },
    },
    document: {
      readyState: 'complete',
      querySelectorAll(sel) { return sel === '[data-inquiry]' ? [root] : []; },
      querySelector() { return null; },
      getElementById() { return null; },
      // The page redraws the quote on `fh:live-availability`; the fake has
      // to deliver it or the calendar tests would look at a stale box.
      addEventListener(type, fn) { (docListeners[type] = docListeners[type] || []).push(fn); },
      dispatchEvent(ev) { (docListeners[ev.type] || []).forEach(function (fn) { fn(ev); }); return true; },
      createElement() { return { setAttribute() {}, style: {} }; },
    },
    location: { href: 'https://rentup.ge/cars/audi-q5/', hostname: 'rentup.ge', search: '', origin: 'https://rentup.ge' },
    FormData: function (r) { this.r = r; },
    URLSearchParams: URLSearchParams,
    CustomEvent: function (name, init) { this.type = name; this.detail = (init || {}).detail; },
    fetch: function (url) {
      fetched.push(String(url));
      if (opts.fetchHangs) return new Promise(function () {});
      const m = String(url).match(/documents\/(fleet|availability)\/(.+)$/);
      if (!m) return Promise.reject(new TypeError('Failed to fetch'));
      const f = opts[m[1] === 'fleet' ? 'fleet' : 'avail'];
      const answer = f
        ? { ok: true, json() { return Promise.resolve(fsDocOf(m[1], m[2], f)); } }
        : { ok: false };
      if (!opts.fetchAfter) return Promise.resolve(answer);
      // A slow answer: still in flight when a quick visitor presses Send.
      return new Promise(function (resolve) {
        sandbox.setTimeout(function () { resolve(answer); }, opts.fetchAfter);
      });
    },
    setTimeout: function (fn, ms) {
      const id = ++seq;
      timers.push({ id: id, at: now + (ms || 0), fn: fn });
      return id;
    },
    clearTimeout: function (id) {
      const i = timers.findIndex(function (t) { return t.id === id; });
      if (i >= 0) timers.splice(i, 1);
    },
    console: { warn() {}, log: console.log, error: console.error },
  };
  sandbox.FormData.prototype.get = function (k) {
    const v = this.r.fields[k];
    return v === undefined ? null : v;
  };
  sandbox.FormData.prototype.forEach = function (cb) {
    const f = this.r.fields;
    Object.keys(f).forEach(function (k) { cb(f[k], k); });
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox);
  await settle();

  const h = {
    root: root, cfg: cfg, db: db, fetched: fetched,
    docs() { return Object.keys(db.docs).map(function (k) { return db.docs[k]; }); },
    submit() { root.fire('submit'); },
    async advance(ms) {
      const until = now + ms;
      for (;;) {
        timers.sort(function (a, b) { return a.at - b.at; });
        if (!timers.length || timers[0].at > until) break;
        // Everything due at the same instant fires in the same tick, as
        // two real timers expiring together would.
        const at = timers[0].at;
        now = at;
        while (timers.length && timers[0].at === at) timers.shift().fn();
        await settle();
      }
      now = until;
      await settle();
    },
  };
  await settle();
  return h;
}

const LIVE_FLEET = () => ({ name: 'Audi Q5', p1: 150, p7: 140, p30: 120, dep: 700, updatedAt: ago(1 * HOUR) });

// ── ტესტები ───────────────────────────────────────────────────────────
const tests = [];
function test(name, fn) { tests.push([name, fn]); }

test('გაგზავნა ცოცხალ ფასს ელოდება; შეცვლილ ფასს კლიენტი ჯერ ხედავს', async () => {
  // 1. ფორმა ივსება წამებში, ცოცხალი მოთხოვნა კი ჯერ გზაშია. ეკრანზე
  // ჩაშენებული ფასია (100). ცოცხალი (150) დღევანდელია, მაგრამ კლიენტმა 100
  // ნახა და ღილაკი მასზე დააჭირა — ჯავშანი ჩუმად 150-ით არ იწერება.
  // ახალი ფასი ეკრანზე გამოდის, ღილაკი იხსნება, და მეორე დაჭერა უკვე
  // ნანახ ფასზეა.
  const r = await start({ fleet: LIVE_FLEET(), fetchAfter: 500 });
  assert.ok(r.root.quote.textContent.includes('100 ₾'), r.root.quote.textContent);
  r.submit();
  await settle();
  assert.strictEqual(r.docs().length, 0, 'ცოცხალ პასუხამდე არაფერი იწერება');
  await r.advance(500);
  assert.strictEqual(r.docs().length, 0, 'ფასი შეიცვალა — კლიენტმა ჯერ უნდა ნახოს');
  assert.ok(r.root.quote.textContent.includes('150 ₾'), r.root.quote.textContent);
  assert.strictEqual(r.root.button.disabled, false, 'ღილაკი ისევ უნდა გაიხსნას');
  assert.notStrictEqual(r.root.status.textContent, T.sending, '„იგზავნება…" არ უნდა დარჩეს');
  assert.notStrictEqual(r.root.status.textContent, T.success);
  r.submit();
  await settle();
  const doc = r.docs()[0];
  assert.ok(doc, 'მეორე დაჭერაზე ჯავშანი უნდა ჩაწერილიყო');
  assert.strictEqual(r.docs().length, 1);
  assert.strictEqual(doc.dailyRateGel, 150);
  assert.strictEqual(doc.rentalGel, 150 * 2);
  assert.strictEqual(doc.depositGel, 700);
  assert.strictEqual(doc.paymentDueGel, 150 * 2 + 700);
  assert.strictEqual(r.root.status.textContent, T.success);
});

test("priceSource არის 'live', როცა ცოცხალი დოკუმენტი გამოიყენეს", async () => {
  const r = await start({ fleet: LIVE_FLEET(), fetchAfter: 500 });
  r.submit();
  await r.advance(500);      // ფასი შეიცვალა — პირველი დაჭერა არ წერს
  r.submit();
  await settle();
  assert.strictEqual(r.docs()[0].priceSource, 'live');
});

test("priceSource არის 'built', როცა ცოცხალი მოთხოვნა დრომ გადაჭრა", async () => {
  // 3. ქსელი არ პასუხობს: ჯავშანი ჩაშენებული ფასით იწერება, და ეს ჩანს —
  // გამქირავებელმა იცის, რომ ფასი deploy-ის დღისაა და არა დღევანდელი.
  const r = await start({ fleet: LIVE_FLEET(), fetchHangs: true });
  r.submit();
  await r.advance(3000);
  const doc = r.docs()[0];
  assert.ok(doc, 'ჯავშანი უნდა ჩაწერილიყო');
  assert.strictEqual(doc.priceSource, 'built');
  assert.strictEqual(doc.dailyRateGel, 100, 'დროის გასვლისას ჩაშენებული ფასია');
});

test('არასოდეს პასუხობადი მოთხოვნა გაგზავნას 3 წამზე მეტხანს არ აყოვნებს', async () => {
  const r = await start({ fleet: LIVE_FLEET(), fetchHangs: true });
  r.submit();
  await r.advance(2999);
  assert.strictEqual(r.docs().length, 0, '3 წამამდე ჯერ ელოდება');
  await r.advance(1);
  assert.strictEqual(r.docs().length, 1, '3 წამზე ჩაწერა უნდა მოხდეს');
});

/// Free units per night, starting today; the two nights the form asks for
/// (tomorrow and the day after) are sold out.
const BUSY_CALENDAR = (ageMs) => ({ from: ymd(0), free: [1, 0, 0, 1, 1, 1, 1, 1, 1, 1], updatedAt: ago(ageMs) });

test('60 საათის კალენდარი ჯერ კიდევ სანდოა', async () => {
  // 5. ტელეფონი სამი დღით უსიგნალოდ იყო — ეს ჯერ კიდევ ერთი ციკლია, და
  // დაკავებული ღამე ისევ უნდა ჩანდეს.
  const r = await start({ avail: BUSY_CALENDAR(60 * HOUR) });
  assert.ok(r.root.quote.textContent.includes(T.busy), r.root.quote.textContent);
});

test('73 საათის კალენდარი უკვე უგულებელყოფილია', async () => {
  // 6. ფანჯარას გადაცილებული კალენდარი თავისუფალ მანქანას მალავს — გვერდი
  // ისე იქცევა, როგორც კალენდრის გარეშე.
  const r = await start({ avail: BUSY_CALENDAR(73 * HOUR) });
  assert.ok(!r.root.quote.textContent.includes(T.busy), r.root.quote.textContent);
});

test("ნდობის ფანჯრის გარეთ მყოფი ფასი 'live'-ად არ ითვლება", async () => {
  // 10. 100 საათის წინანდელი დოკუმენტი გამოუსადეგარია: ჩაშენებული ფასი
  // რჩება და ჩანაწერიც ამას ამბობს.
  const r = await start({ fleet: Object.assign(LIVE_FLEET(), { updatedAt: ago(100 * HOUR) }), fetchAfter: 500 });
  r.submit();
  await r.advance(500);
  const doc = r.docs()[0];
  assert.strictEqual(doc.priceSource, 'built');
  assert.strictEqual(doc.dailyRateGel, 100);
});

test('„გაგზავნა" ორჯერ ტრანსპორტის შეცდომის შემდეგ ერთ ჯავშანს ქმნის', async () => {
  // 7. სერვერმა ჩანაწერი მიიღო, პასუხი კი გზაში დაიკარგა. ფორმა სავსე
  // რჩება, კლიენტი ხელახლა აჭერს — და ახალი ჯავშანი არ უნდა შეიქმნას.
  const r = await start({ write: 'lostAck' });
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.failed);
  assert.strictEqual(r.root.button.disabled, false, 'ღილაკი ისევ უნდა გაიხსნას');
  assert.strictEqual(r.docs().length, 1, 'სერვერმა პირველი ჩანაწერი მიიღო');
  r.submit();
  await settle();
  assert.strictEqual(r.docs().length, 1, 'მეორე დაჭერამ დუბლი შექმნა');
  assert.strictEqual(r.root.status.textContent, T.success,
    'ჯავშანი არსებობს — კლიენტს „ვერ გაიგზავნა" არ უნდა ეთქვას');
});

test('ოფლაინ გაგზავნა შეტყობინებით სრულდება და არა უსასრულოდ', async () => {
  // 8. Firestore SDK ოფლაინში ჩაწერას რიგში სვამს და არ ჩავარდება —
  // ღილაკი სამუდამოდ დაბლოკილი რჩებოდა, სტატუსი „იგზავნება…"-ზე.
  const r = await start({ write: 'hang' });
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.sending);
  await r.advance(30000);
  assert.strictEqual(r.root.status.textContent, T.failed);
  assert.strictEqual(r.root.button.disabled, false);
  // ხელახლა დაჭერა იმავე რიგში მდგარ ჩაწერას ელოდება და მეორეს არ სვამს.
  r.submit();
  await r.advance(30000);
  assert.strictEqual(r.root.status.textContent, T.failed);
  assert.strictEqual(r.db.setCalls + r.db.addCalls, 1, 'ორი ჩანაწერი რიგში');
});

test('Netlify-ს მისამართზე არავითარი მოთხოვნა არ გადის', async () => {
  // 9. ის მისამართი 404-ს აბრუნებს და no-cors მის წარუმატებლობას მალავდა.
  const r = await start();
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.success);
  const bad = r.fetched.filter(function (u) { return /netlify/i.test(u); });
  assert.deepStrictEqual(bad, [], 'Netlify-ს გაუგზავნია: ' + bad.join(', '));
});

test('წარმატებული ჯავშნის შემდეგ იდენტური გაგზავნა ახალი ჯავშანია', async () => {
  // 11. მოთხოვნის ნომერი ერთ ჯავშანს ეკუთვნის. წარმატების მერე იგივე
  // კლიენტი იგივე მანქანას იგივე თარიღებზე ხელახლა ჯავშნის (სხვა მიზეზით,
  // ან პირველი დაავიწყდა) — ეს ახალი მოთხოვნაა და არა დუბლი. თარიღის
  // შეცვლა აქ არაფერს ამოწმებდა: თითი თვითონ ცვლიდა ნომერს.
  const r = await start();
  const same = Object.assign({}, r.root.fields);
  r.submit();
  await settle();
  assert.strictEqual(r.docs().length, 1);
  assert.strictEqual(Object.keys(r.root.fields).length, 0, 'ფორმა გასუფთავდა');
  Object.assign(r.root.fields, same);
  r.submit();
  await settle();
  assert.strictEqual(r.docs().length, 2);
});

test('შეცდომის შემდეგ შეცვლილი ფორმა ახალი მოთხოვნაა', async () => {
  // 12. კლიენტმა ჩავარდნის მერე ტელეფონი გაასწორა — ძველ ნომერზე გაგზავნა
  // ძველ ჩანაწერს დაუბრუნებდა პასუხს და გასწორებული ნომერი დაიკარგებოდა.
  // (თარიღის შეცვლა ფასსაც ცვლის და იმ შემთხვევას 1-ლი ტესტი ფარავს.)
  const r = await start({ write: 'lostAck' });
  r.submit();
  await settle();
  r.root.fields.phone = '+995599000111';
  r.submit();
  await settle();
  const phones = r.docs().map(function (d) { return d.phone; }).sort();
  assert.deepStrictEqual(phones, ['+995555123456', '+995599000111'].sort());
  assert.strictEqual(r.root.status.textContent, T.success);
});

test("ცოცხალი ფასი ფორმაში ჩანს და ჩანაწერში 'live'-ია", async () => {
  // 13. ცოცხალი დოკუმენტი ახალია — კლიენტი მას ხედავს და ჯავშანიც მას წერს.
  const r = await start({ fleet: LIVE_FLEET(), fetchAfter: 500 });
  await r.advance(500);
  assert.ok(r.root.quote.textContent.includes('150 ₾'), r.root.quote.textContent);
  r.submit();
  await settle();
  const doc = r.docs()[0];
  assert.strictEqual(doc.priceSource, 'live');
  assert.strictEqual(doc.dailyRateGel, 150);
});

test("ჩაშენებული ფასი ფორმაში ჩანს და ჩანაწერში 'built'-ია", async () => {
  // 14. გვერდის მქონე მანქანა, ცოცხალი დოკუმენტი არ არის: ისე, როგორც
  // აქამდე — ჩაშენებული ფასი, ოღონდ ახლა ჩანაწერი ამას ამბობს.
  const r = await start({ fleet: null });
  assert.ok(r.root.quote.textContent.includes('100 ₾'), r.root.quote.textContent);
  r.submit();
  await settle();
  const doc = r.docs()[0];
  assert.strictEqual(doc.priceSource, 'built');
  assert.strictEqual(doc.dailyRateGel, 100);
  assert.strictEqual(doc.rentalGel, 200);
});

test("ფასის გარეშე მანქანა: ციფრი არ ჩანს, იგზავნება, 'none'-ია", async () => {
  // 15. კატალოგის მანქანა, რომლის დოკუმენტი 72 საათზე ძველია და
  // ჩაშენებული ფასი არ აქვს. „0 ₾" უფასო ქირის დაპირებად იკითხება, ამიტომ
  // ფასი არ იწერება; მოთხოვნა კი არ იკარგება.
  const r = await start({
    cars: {},
    fields: { car_slug: 'jaguar-xf', requested_car: 'Jaguar XF' },
    fleet: Object.assign(LIVE_FLEET(), { updatedAt: ago(100 * HOUR) }),
  });
  assert.ok(r.root.quote.textContent.length > 0, 'დღეების რაოდენობა ჩანს');
  assert.ok(!r.root.quote.textContent.includes('₾'), r.root.quote.textContent);
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.success, 'მოთხოვნა არ უნდა დაიკარგოს');
  const doc = r.docs()[0];
  assert.strictEqual(doc.priceSource, 'none');
  assert.strictEqual(doc.carSlug, 'jaguar-xf');
  assert.strictEqual(doc.rentalGel, 0);
});

test("ფიგურა უცვლელია — ერთი დაჭერა საკმარისია, 'live'", async () => {
  // 16. ცოცხალი დოკუმენტი ეკრანზე ნანახ ფასს ემთხვევა (ჩვეულებრივი შემთხვევა:
  // catalogue.js უკვე ჩადო). მეორე დაჭერა არ მოითხოვება.
  const same = { name: 'Audi Q5', p1: 100, p7: 90, p30: 80, dep: 500, updatedAt: ago(HOUR) };
  const r = await start({ fleet: same, fetchAfter: 500 });
  r.submit();
  await r.advance(500);
  assert.strictEqual(r.docs().length, 1);
  assert.strictEqual(r.docs()[0].priceSource, 'live');
  assert.strictEqual(r.root.status.textContent, T.success);
});

test('ხელახალი დაჭერა: დოკუმენტი ქეშშია — წარმატებაა, ახალი ჩაწერა არ არის', async () => {
  // 17. ოფლაინში SDK ან ქეშიდან პასუხობს, ან „unavailable"-ს აბრუნებს.
  // ქეშში ნანახი დოკუმენტი = ჯავშანი არსებობს; „ვერ გაიგზავნა" ტყუილი იქნებოდა.
  const r = await start({ write: 'lostAck', getMode: 'cache' });
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.failed);
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.success);
  assert.strictEqual(r.db.setCalls, 1, 'არსებულ დოკუმენტზე მეორე ჩაწერა რიგში არ ჩადგეს');
  assert.strictEqual(r.docs().length, 1);
});

test('ხელახალი დაჭერა: ქსელი არ არის, ჩანაწერი უკვე არსებობს — წარმატებაა', async () => {
  // 18. წაკითხვა „unavailable"-ით ვარდება — არ ვიცით. ვწერთ, წესები
  // განახლებას უარყოფს, და ეს უარყოფა ჯავშნის არსებობაა და არა ჩავარდნა.
  const r = await start({ write: 'lostAck', getMode: 'unavailable' });
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.failed);
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.success);
  assert.strictEqual(r.docs().length, 1);
});

test('წესების უარყოფა წარმატებად არ ითვლება, ხელახლაც', async () => {
  // 19. თუ წესები ჩანაწერსაც უარყოფს, ორი დაჭერის მერეც ჩავარდნაა — ეს
  // „არსებული ჯავშნის" ლოგიკით არ უნდა დაიმალოს.
  const r = await start({ write: 'denied', getMode: 'unavailable' });
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.failed);
  r.submit();
  await settle();
  assert.strictEqual(r.root.status.textContent, T.failed);
  assert.strictEqual(r.docs().length, 0);
});

test('ლოდინისას მანქანა შეიცვალა: ეტიკეტი მეორე მანქანის ფასს აღწერს', async () => {
  // 20. ორივე მანქანის ჩაშენებული ფასი ერთია, A-ს ცოცხალი დოკუმენტი
  // მოდის. B-ს ფასი ცოცხალი არ არის — 'live' მისთვის ტყუილი იქნებოდა.
  const base = { p1: 100, p7: 90, p30: 80, dep: 500 };
  const same = { name: 'Audi Q5', p1: 100, p7: 90, p30: 80, dep: 500, updatedAt: ago(HOUR) };
  const r = await start({ cars: { 'audi-q5': base, 'bmw-x5': Object.assign({}, base) },
                          fleet: same, fetchAfter: 500 });
  r.submit();
  r.root.fields.car_slug = 'bmw-x5';
  r.root.fields.requested_car = 'BMW X5';
  await r.advance(500);
  const doc = r.docs()[0];
  assert.ok(doc, 'ფიგურა უცვლელია — იგზავნება');
  assert.strictEqual(doc.carSlug, 'bmw-x5');
  assert.strictEqual(doc.priceSource, 'built');
});

(async function () {
  let failed = 0;
  for (const [name, fn] of tests) {
    try {
      await fn();
      console.log('  ✓ ' + name);
    } catch (e) {
      failed += 1;
      console.log('  ✗ ' + name + '\n      ' + e.message);
    }
  }
  console.log(failed ? `\n${failed} / ${tests.length} ჩავარდა` : `\nყველა ${tests.length} გავიდა`);
  process.exit(failed ? 1 : 0);
})();
