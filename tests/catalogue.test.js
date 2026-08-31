/* catalogue.js — რენდერის შემოწმება ნამდვილი ბრაუზერის გარეშე.
   ═══════════════════════════════════════════════════════════════════

   სკრიპტი მხოლოდ ცოცხალ საიტზე იმუშავებდა, ანუ შემოწმება deploy-ის შემდეგ
   მოხდებოდა — ესე იგი კლიენტზე. ეს ჰარნესი DOM-ის იმ ნაწილს ბაძავს,
   რომელსაც სკრიპტი ეხება, და Firestore-ის ნამდვილი ფორმის პასუხს აწვდის.

   რას ამოწმებს — ყველა მათგანი რეალური ზიანია, არა სტილი:
     1. ბარათი კატეგორიის სწორ განყოფილებაში ხვდება
     2. კატეგორიის გარეშე მოსული მანქანა არ ქრება
     3. სტატიკური ბარათი არ დუბლირდება
     4. `_probe` მანქანად არ ითვლება
     5. ძველი და ნულფასიანი დოკუმენტი არ ჩნდება
     6. შეუვსებელი ველი არ იბეჭდება (და არაფერი წერს „0 ადგილს")
     7. ელექტრო გარბენს წერს, ხარჯს — არა
     8. ჯავშნის ფასი `FH_CFG.cars`-ში ჩაჯდება
     9. HTML-ის ინექცია სახელიდან ვერ გადის                                */

const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

// The script ships from `static/`; this suite lives in `tests/` so the
// quality gate's unittest discovery can reach it.
const SRC = fs.readFileSync(__dirname + '/../static/catalogue.js', 'utf8');

// ── DOM-ის მინიმალური ბაძვა ────────────────────────────────────────────
class El {
  constructor(attrs = {}) {
    this.attrs = attrs;
    this.html = '';
    this.hidden = false;
    this.dataset = {};
    if (attrs['data-car']) this.dataset.car = attrs['data-car'];
    this.parent = null;
  }
  getAttribute(k) { return this.attrs[k] === undefined ? null : this.attrs[k]; }
  insertAdjacentHTML(_where, html) { this.html += html; }
  closest(sel) {
    const key = sel.replace(/[[\]]/g, '');
    let node = this;
    while (node) {
      if (node.attrs[key] !== undefined) return node;
      node = node.parent;
    }
    return null;
  }
}

function makeDoc(grids, staticCars) {
  const all = [];
  const sections = {};
  Object.keys(grids).forEach(function (cat) {
    const grid = new El({ 'data-live-catalogue': cat });
    grids[cat] = grid;
    if (cat === '*') {
      const section = new El({ 'data-live-other': '' });
      section.hidden = true;
      grid.parent = section;
      sections['*'] = section;
    }
    all.push(grid);
  });
  const statics = (staticCars || []).map(function (slug) {
    return new El({ 'data-car': slug });
  });
  return {
    doc: {
      querySelector() { return null; },
      querySelectorAll(sel) {
        if (sel === '[data-live-catalogue]') return all;
        if (sel === '[data-car]') return statics;
        return [];
      },
      dispatchEvent() { return true; },
    },
    sections,
  };
}

function fsDocOf(slug, fields) {
  const out = {};
  Object.keys(fields).forEach(function (k) {
    const v = fields[k];
    if (typeof v === 'number') {
      out[k] = Number.isInteger(v) ? { integerValue: String(v) }
                                   : { doubleValue: v };
    } else if (typeof v === 'boolean') {
      out[k] = { booleanValue: v };
    } else {
      out[k] = { stringValue: String(v) };
    }
  });
  return { name: 'projects/p/databases/(default)/documents/fleet/' + slug, fields: out };
}

const NOW = new Date().toISOString();
const OLD = new Date(Date.now() - 60 * 24 * 3600 * 1000).toISOString();

const CAT = {
  usdRate: 2.6125,
  usdStep: 10,
  book: 'დაჯავშნის მოთხოვნა',
  l: { seats: 'ადგილი', luggage: 'ჩემოდანი', clearance: 'კლირენსი',
       range: 'გარბენი დატენვაზე', transmission: 'ტრანსმისია', drive: 'წამყვანი' },
  v: { automatic: 'ავტომატი', manual: 'მექანიკა', fwd: 'წინა', rwd: 'უკანა',
       awd: 'სრული (AWD)', petrol: 'ბენზინი', diesel: 'დიზელი',
       hybrid: 'ჰიბრიდი', electric: 'ელექტრო', phev: 'დატენვადი ჰიბრიდი', lpg: 'გაზი' },
  u: { mm: 'მმ', l: 'ლ', day: 'დღე', km: 'კმ' },
};

/// Runs the script against `documents` and returns the grids it filled.
function run(documents, opts) {
  opts = opts || {};
  const grids = {};
  (opts.categories || ['economy', 'suv', 'business', '*']).forEach(function (c) {
    grids[c] = null;
  });
  const built = makeDoc(grids, opts.staticCars);
  const cfg = { projectId: 'p', cars: {} };

  let fetched = null;
  const sandbox = {
    window: { FH_CAT: opts.noCat ? undefined : CAT, FH_CFG: cfg },
    document: built.doc,
    CustomEvent: function (name, init) { this.type = name; this.detail = (init || {}).detail; },
    fetch: function (url) {
      fetched = url;
      return Promise.resolve({
        ok: opts.httpFail ? false : true,
        json: function () { return Promise.resolve({ documents: documents }); },
      });
    },
    console,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox);

  // The script's work happens in a promise chain; two ticks is enough for
  // `fetch().then().then()`.
  return new Promise(function (resolve) {
    setImmediate(function () {
      setImmediate(function () {
        resolve({ grids: grids, cfg: cfg, sections: built.sections, url: fetched });
      });
    });
  });
}

// ── ტესტები ───────────────────────────────────────────────────────────
const tests = [];
function test(name, fn) { tests.push([name, fn]); }

test('კატეგორიის მქონე მანქანა თავის განყოფილებაში ხვდება', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, p7: 230, p30: 200,
                         cat: 'suv', seats: 5, updatedAt: NOW }),
  ]);
  assert.ok(r.grids.suv.html.includes('Audi Q5'), 'SUV-ის ბადეში უნდა იყოს');
  assert.strictEqual(r.grids.economy.html, '', 'სხვაგან არ უნდა იყოს');
  assert.strictEqual(r.grids['*'].html, '', 'შემკრებში არ უნდა იყოს');
});

test('კატეგორიის გარეშე მოსული მანქანა არ ქრება', async () => {
  // ეს არის მთელი ცვლილების აზრი: მანქანა ვერსად ქრება.
  const r = await run([
    fsDocOf('jaguar-xf', { name: 'Jaguar XF', p1: 300, updatedAt: NOW }),
  ]);
  assert.ok(r.grids['*'].html.includes('Jaguar XF'));
  assert.strictEqual(r.sections['*'].hidden, false, 'განყოფილება უნდა გაიხსნას');
});

test('უცნობი კატეგორია გამოცნობის ნაცვლად შემკრებში ხვდება', async () => {
  const r = await run([
    fsDocOf('kia-ev6', { name: 'Kia EV6', p1: 200, cat: 'coupe', updatedAt: NOW }),
  ]);
  assert.ok(r.grids['*'].html.includes('Kia EV6'));
});

test('შემკრები დამალული რჩება, თუ არაფერი ჩაჯდა', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ]);
  assert.strictEqual(r.sections['*'].hidden, true, 'ცარიელი სათაური არ უნდა ჩანდეს');
});

test('სტატიკური ბარათი არ დუბლირდება', async () => {
  // ერთი მანქანა ორჯერ, ორი სხვადასხვა ფასით, კლიენტს ეუბნება რომ საიტს
  // არ ენდოს — ეს დაკარგულ ბარათზე უარესია.
  const r = await run([
    fsDocOf('toyota-prius', { name: 'Toyota Prius', p1: 75, cat: 'economy', updatedAt: NOW }),
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ], { staticCars: ['toyota-prius'] });
  assert.ok(!r.grids.economy.html.includes('Toyota Prius'), 'უკვე დახატულია');
  assert.ok(r.grids.suv.html.includes('Audi Q5'));
});

test('_probe მანქანად არ ითვლება', async () => {
  const r = await run([
    fsDocOf('_probe', { probe: true, p1: 1, updatedAt: NOW }),
  ]);
  assert.strictEqual(r.grids['*'].html, '');
});

test('თვეზე ძველი დოკუმენტი არ ჩნდება', async () => {
  // გაყიდული მანქანის მიტოვებული დოკუმენტი. საიტმა ის აღარ უნდა გაყიდოს.
  const r = await run([
    fsDocOf('sold-car', { name: 'Sold Car', p1: 100, cat: 'suv', updatedAt: OLD }),
  ]);
  assert.strictEqual(r.grids.suv.html, '');
});

test('ნულოვანი ფასი შეთავაზებად არ იქცევა', async () => {
  const r = await run([
    fsDocOf('broken', { name: 'Broken', p1: 0, cat: 'suv', updatedAt: NOW }),
  ]);
  assert.strictEqual(r.grids.suv.html, '');
});

test('შეუვსებელი ველი არ იბეჭდება', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ]);
  const h = r.grids.suv.html;
  assert.ok(h.includes('Audi Q5'));
  assert.ok(!h.includes('0 ადგილი'), '„0 ადგილი" მანქანას გამოუსადეგარად აჩვენებს');
  assert.ok(!h.includes('undefined'), 'undefined ვერასდროს გავა კლიენტთან');
  assert.ok(!h.includes('კლირენსი'), 'შეუვსებელი კლირენსი არ უნდა ეწეროს');
});

test('ელექტრო გარბენს წერს და ხარჯს — არა', async () => {
  const r = await run([
    fsDocOf('tesla-model-x', { name: 'Tesla Model X', p1: 400, cat: 'suv',
                               fuel: 'electric', range: 350, l100: 8.5,
                               updatedAt: NOW }),
  ]);
  const h = r.grids.suv.html;
  assert.ok(h.includes('350 კმ'), 'გარბენი უნდა ეწეროს');
  assert.ok(h.includes('ელექტრო'));
  assert.ok(!h.includes('8.5'), 'ელექტრომობილს ლიტრი არ აქვს');
});

test('ბენზინიანი ხარჯს წერს', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', fuel: 'petrol',
                         engine: 2.0, l100: 9.5, clear: 200, seats: 5, bags: 3,
                         updatedAt: NOW }),
  ]);
  const h = r.grids.suv.html;
  assert.ok(h.includes('5 ადგილი'));
  assert.ok(h.includes('2 ბენზინი') || h.includes('2.0 ბენზინი'));
  assert.ok(h.includes('9.5 ლ / 100 კმ'));
  assert.ok(h.includes('კლირენსი 200 მმ'));
  assert.ok(h.includes('3 ჩემოდანი'));
});

test('ჯავშნის ფასი FH_CFG-ში ჩაჯდება', async () => {
  // ამის გარეშე ღილაკი გაიხსნება და 0 ₾-ს დათვლის — ჯავშანშიც ნული ჩაიწერება.
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, p7: 230, p30: 200, dep: 800,
                         cat: 'suv', updatedAt: NOW }),
  ]);
  // `deepStrictEqual` compares prototypes, and this object was built inside
  // the vm's own realm — so it is compared field by field instead.
  assert.deepStrictEqual(
    Object.assign({}, r.cfg.cars['audi-q5']),
    { p1: 250, p7: 230, p30: 200, dep: 800 },
  );
});

test('ზოლების გარეშე მოსული დოკუმენტი ფასს არ ანულებს', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ]);
  const c = r.cfg.cars['audi-q5'];
  assert.strictEqual(c.p7, 250, 'p7 უნდა დაბრუნდეს p1-ზე, არა ნულზე');
  assert.strictEqual(c.p30, 250);
});

test('სახელიდან HTML ვერ გადის', async () => {
  // მოდელის სახელს პატრონი წერს. ერთი დღე ვინმე <script>-ს ჩაწერს.
  const r = await run([
    fsDocOf('x', { name: '<img src=x onerror=alert(1)>', p1: 100, cat: 'suv',
                   updatedAt: NOW }),
  ]);
  assert.ok(!r.grids.suv.html.includes('<img src=x'), 'უნდა იყოს escape-ული');
  assert.ok(r.grids.suv.html.includes('&lt;img'));
});

test('ფასი ისევე იწერება, როგორც სტატიკურ ბარათზე', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ]);
  // 250 / 2.6125 = 95.7 → უახლოეს 10-ზე = 100
  assert.ok(r.grids.suv.html.includes('250 ₾ · ≈ $100'), r.grids.suv.html.slice(0, 300));
});

test('FH_CAT-ის გარეშე საერთოდ არ ირთვება', async () => {
  const r = await run([
    fsDocOf('audi-q5', { name: 'Audi Q5', p1: 250, cat: 'suv', updatedAt: NOW }),
  ], { noCat: true });
  assert.strictEqual(r.url, null, 'გვერდი, რომელსაც კატალოგი არ სჭირდება, არაფერს ითხოვს');
});

test('უპასუხო Firestore გვერდს არ ტეხს', async () => {
  const r = await run([], { httpFail: true });
  assert.strictEqual(r.grids.suv.html, '');
  assert.strictEqual(r.sections['*'].hidden, true);
});

test('იაფიდან ძვირისკენ', async () => {
  const r = await run([
    fsDocOf('b-car', { name: 'Bcar', p1: 300, cat: 'suv', updatedAt: NOW }),
    fsDocOf('a-car', { name: 'Acar', p1: 100, cat: 'suv', updatedAt: NOW }),
  ]);
  assert.ok(r.grids.suv.html.indexOf('Acar') < r.grids.suv.html.indexOf('Bcar'));
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
