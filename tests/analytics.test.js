/* analytics.js — Umami events checked without a browser.

   What it guards (each is a real loss, not style):
     1. an ad-blocked or still-loading Umami never breaks a tap on "call"
     2. call / WhatsApp taps are counted once, even when the tap lands on
        a child of the link (the ☎ span, the <bdi> number)
     3. every event carries the page language and page type, so RTL pages
        report he/ar/fa and not en
     4. the listener never blocks the link's own navigation             */

const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const SRC = fs.readFileSync(__dirname + '/../static/analytics.js', 'utf8');

function anchor(href) {
  const a = { tagName: 'A', href, getAttribute: (k) => (k === 'href' ? href : null) };
  a.closest = (sel) => (sel === 'a' ? a : null);
  return a;
}
function childOf(a) {
  return { tagName: 'SPAN', closest: (sel) => (sel === 'a' ? a : null) };
}

function load({ umami = true, lang = 'en', bodyClass = 'page-home', pathname = '/' } = {}) {
  const calls = [];
  const handlers = {};
  const document = {
    documentElement: { lang },
    body: { className: bodyClass },
    readyState: 'complete',
    addEventListener: (type, fn) => { (handlers[type] = handlers[type] || []).push(fn); },
    querySelector: () => null,
  };
  const window = { document, location: { href: 'https://rentup.ge' + pathname, pathname, search: '' } };
  if (umami) window.umami = { track: (name, data) => calls.push([name, data]) };
  window.window = window;
  const ctx = vm.createContext({ window, document, location: window.location, URLSearchParams, WeakMap, Object, String, Number, Math, Date, console });
  vm.runInContext(SRC, ctx);
  const click = (target) => {
    const ev = { target, prevented: false, preventDefault() { this.prevented = true; } };
    (handlers.click || []).forEach((fn) => fn(ev));
    return ev;
  };
  return { window, calls, click };
}

const tests = {
  'track returns false and does not throw when window.umami is undefined'() {
    const { window } = load({ umami: false });
    assert.strictEqual(window.RentUpAnalytics.track('call_click', {}), false);
  },
  'track forwards name and adds lang/page_type'() {
    const { window, calls } = load({ lang: 'he', bodyClass: 'page-map foo', pathname: '/he/attractions/kazbegi/' });
    assert.strictEqual(window.RentUpAnalytics.track('call_click', { href_kind: 'tel' }), true);
    // objects come from the vm realm, so compare their JSON, not prototypes
    assert.strictEqual(JSON.stringify(calls), JSON.stringify([['call_click', { href_kind: 'tel', lang: 'he', page_type: 'attraction' }]]));
  },
  'click on a <span> inside a tel: link fires call_click exactly once'() {
    const { calls, click } = load();
    click(childOf(anchor('tel:+995597555565')));
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0][0], 'call_click');
  },
  'click on a wa.me link fires whatsapp_click'() {
    const { calls, click } = load({ lang: 'ar' });
    click(anchor('https://wa.me/995597555565?text=hi'));
    assert.deepStrictEqual(calls.map((c) => c[0]), ['whatsapp_click']);
    assert.strictEqual(calls[0][1].lang, 'ar');
  },
  'click on an ordinary link fires nothing'() {
    const { calls, click } = load();
    click(anchor('/en/fleet/'));
    assert.strictEqual(calls.length, 0);
  },
  'listener never calls preventDefault'() {
    const { click } = load();
    assert.strictEqual(click(anchor('tel:+995597555565')).prevented, false);
    const blocked = load({ umami: false });
    assert.strictEqual(blocked.click(anchor('tel:+995597555565')).prevented, false);
  },
  'page_type comes from the URL section, not the nav highlight'() {
    const cases = { '/': 'home', '/ka/': 'home', '/fleet/': 'fleet', '/fleet/bmw-5-series/': 'car',
      '/ru/car-rental/one-way/': 'car-rental', '/guides/kazbegi-road/': 'guide', '/ar/regions/kakheti/': 'region',
      '/routes/x/': 'route', '/tours/x/': 'tour', '/itineraries/x/': 'itinerary', '/day-trip/x/': 'day-trip',
      '/fa/contact/': 'contact', '/faq/': 'faq' };
    for (const [pathname, want] of Object.entries(cases)) {
      const { window, calls } = load({ bodyClass: 'page-map', pathname });
      window.RentUpAnalytics.track('call_click', {});
      assert.strictEqual(calls[0][1].page_type, want, pathname);
    }
  },
  'tap on the inquiry WhatsApp button is left to booking.js (it may fail validation)'() {
    const { calls, click } = load();
    const btn = { tagName: 'BUTTON', getAttribute: () => null, matches: (sel) => sel === '[data-inquiry-wa]' };
    btn.closest = (sel) => (sel === 'button' ? btn : null);
    click(btn);
    assert.strictEqual(calls.length, 0);
  },
  'page_type falls back to other'() {
    const { window, calls } = load({ bodyClass: '', pathname: '/unknown-section/' });
    window.RentUpAnalytics.track('booking_request', {});
    assert.strictEqual(calls[0][1].page_type, 'other');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); }
  catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + e.message); }
}
if (failed) { console.log(failed + ' failed'); process.exit(1); }
console.log('all ' + Object.keys(tests).length + ' passed');
