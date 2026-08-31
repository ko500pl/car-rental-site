/* ცოცხალი კატალოგი — მანქანები, რომლებსაც საიტზე დაწერილი გვერდი არ აქვთ.
   ═══════════════════════════════════════════════════════════════════════

   ## რატომ არსებობს

   rentup.ge სტატიკური საიტია: თითო მოდელს თავისი YAML ფაილი აქვს, გვერდი
   `build.py`-ით იწყობა და deploy-ით ქვეყნდება. სანამ ეს ფაილი არ არსებობს,
   მანქანა საიტზე ვერ იყიდება — ტელეფონი ფასს აქვეყნებდა იმ მისამართზე,
   რომელსაც ვერცერთი გვერდი ვერ კითხულობდა, და ტელეფონიდან ეს წარმატებას
   ჰგავდა.

   ანუ ყოველი ახალი მანქანა deploy-ს ითხოვდა. ეს სკრიპტი ამას წყვეტს:
   `fleet/` კოლექციას მთლიანად კითხულობს და იმ მოდელებს, რომლებსაც ამ
   გვერდზე უკვე არ აქვთ ბარათი, თვითონ ხატავს — ფასით, აღწერით და
   დაჯავშნის ღილაკით. ახალი მანქანა აპში ჩაირთვება და იმავე წუთს იყიდება.

   ## რას ვერ აკეთებს — და ეს გულწრფელად უნდა ეწეროს

   **ფოტო არ აქვს.** ფოტოები ფაილებია, სტატიკური საიტი მათ თავისი
   რეპოზიტორიიდან ასერვირებს, და ღრუბლით ვერ გაივლის. ასეთი ბარათი
   სილუეტით ჩანს. ჯავშნისთვის საკმარისია, ვიტრინისთვის — არა.

   **საკუთარი გვერდი არ აქვს.** ანუ Google-ში ცალკე არ იძებნება. ეს
   განზრახაა: „Jaguar XF ქირაობა თბილისი"-ს პრაქტიკულად არავინ ეძებს, და
   ცარიელი გვერდი ვერც დარეიტინგდებოდა და მთელ საიტს დასწევდა.

   ## ნდობის ფანჯარა

   `booking.js`-ს ფასებზე 48 საათი აქვს, რადგან **კალენდარი** ძველდება:
   კვირისწინანდელი კალენდარი თავისუფალ მანქანას მალავს. აქ სხვა კითხვაა —
   „არსებობს თუ არა ეს მანქანა". ფასი კვირაში ერთხელ არ იცვლება, და თუ
   პატრონი შვებულებაშია, მანქანა საიტიდან არ უნდა გაქრეს. ამიტომ 30 დღეა:
   თვეზე მეტი დუმილი უკვე ნიშნავს, რომ მანქანა გაიყიდა და დოკუმენტი
   მიტოვებულია. */
(function () {
  'use strict';

  var cat = window.FH_CAT;
  if (!cat || typeof fetch !== 'function') return;

  var cfg = window.FH_CFG || (window.FH_CFG = {});
  var pid = cfg.projectId;
  if (!pid) return;

  /* გვერდზე თითო კატეგორიას თავისი ბადე აქვს, პლუს ერთი შემკრები („*"),
     რომელშიც კატეგორიის გარეშე მოსული მანქანა ხვდება. შემკრები დამალულია და
     მხოლოდ მაშინ ჩნდება, თუ მართლა რამე ჩაჯდა — ცარიელი სათაური იმაზე
     უარესია, ვიდრე მისი არქონა. */
  var grids = {};
  document.querySelectorAll('[data-live-catalogue]').forEach(function (el) {
    grids[el.getAttribute('data-live-catalogue') || ''] = el;
  });
  if (!Object.keys(grids).length) return;

  /* 30 დღე — იხ. ზემოთ. */
  var TRUST_MS = 30 * 24 * 3600 * 1000;

  /* ── Firestore-ის REST პასუხის გახსნა ──────────────────────────────────
     იგივე ფორმა, რაც booking.js-ს აქვს. განზრახ გამეორებულია და არ არის
     გატანილი: ორივე ფაილი ცალკე იტვირთება და საერთო მოდული ერთი ზედმეტი
     მოთხოვნა იქნებოდა იმ გვერდზე, სადაც ერთი მათგანი საერთოდ არ სჭირდება. */
  function fsValue(v) {
    if (!v || typeof v !== 'object') return v;
    if ('integerValue' in v) return Number(v.integerValue);
    if ('doubleValue' in v) return Number(v.doubleValue);
    if ('stringValue' in v) return v.stringValue;
    if ('timestampValue' in v) return v.timestampValue;
    if ('booleanValue' in v) return v.booleanValue;
    if ('arrayValue' in v) return ((v.arrayValue || {}).values || []).map(fsValue);
    return null;
  }

  function fsDoc(json) {
    if (!json || !json.fields) return null;
    var out = {};
    Object.keys(json.fields).forEach(function (k) { out[k] = fsValue(json.fields[k]); });
    /* დოკუმენტის სახელის ბოლო ნაწილი slug-ია. */
    var name = String(json.name || '');
    out._slug = name.slice(name.lastIndexOf('/') + 1);
    return out;
  }

  function fresh(doc) {
    if (!doc || !doc.updatedAt) return false;
    var t = Date.parse(doc.updatedAt);
    return isFinite(t) && (Date.now() - t) < TRUST_MS;
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ── ერთი ბარათის აწყობა ───────────────────────────────────────────── */

  /* მეტა-ხაზი: „5 ადგილი · ავტომატი · 2.0 ბენზინი · სრული (AWD)".
     მხოლოდ ის, რაც შევსებულია. შეუვსებელი ველი არ ჩნდება — გამოგონილი
     „5 ადგილი" კომერციულ საიტზე იმ ოჯახს ეუბნება ტყუილს, რომელიც ექვსნი
     არიან. */
  function metaLine(d) {
    var parts = [];
    if (d.seats > 0) parts.push(d.seats + ' ' + cat.l.seats);
    if (d.gear && cat.v[d.gear]) parts.push(cat.v[d.gear]);
    /* ძრავი და საწვავი ერთ ერთეულად იკითხება: „2.0 ბენზინი". */
    var engine = '';
    if (d.engine > 0) engine = String(d.engine);
    if (d.fuel && cat.v[d.fuel]) engine = (engine ? engine + ' ' : '') + cat.v[d.fuel];
    if (engine) parts.push(engine);
    if (d.drive && cat.v[d.drive]) parts.push(cat.v[d.drive]);
    return parts.join(' · ');
  }

  /* მეორე ხაზი — ის, რაც არჩევანზე მოქმედებს, მაგრამ პირველ ხაზში აღარ ეტევა. */
  function specLine(d) {
    var parts = [];
    if (d.bags > 0) parts.push(d.bags + ' ' + cat.l.luggage);
    if (d.clear > 0) parts.push(cat.l.clearance + ' ' + d.clear + ' ' + cat.u.mm);
    /* ხარჯი და გარბენი ერთმანეთს გამორიცხავს — ელექტრომობილს ლიტრი არ აქვს,
       ბენზინიანს დატენვა. ტელეფონი მხოლოდ ერთს აგზავნის, მაგრამ ბარათი
       მაინც ცალკე ამოწმებს: ორივეს დაბეჭდვა ერთმანეთის საწინააღმდეგო
       ორ ხაზს ნიშნავს. */
    if (d.range > 0) parts.push(cat.l.range + ' ' + d.range + ' ' + cat.u.km);
    else if (d.l100 > 0) parts.push(d.l100 + ' ' + cat.u.l + ' / 100 ' + cat.u.km);
    return parts.join(' · ');
  }

  /* „130 ₾ · ≈ $50" — იგივე ფორმა, რაც build.py-ს `money()`-ს აქვს. კურსი და
     დამრგვალების საფეხური `FH_CAT`-იდან მოდის, რომ ცოცხალმა ბარათმა ფული
     სხვანაირად არ დაწეროს, ვიდრე გვერდზე მის გვერდით მდგარმა. */
  function money(n) {
    var gel = Math.round(Number(n) || 0);
    var rate = Number(cat.usdRate) || 0;
    var step = Number(cat.usdStep) || 0;
    if (!(rate > 0) || !(step > 0)) return gel + ' ₾';
    var usd = Math.round(gel / rate / step) * step;
    return gel + ' ₾ · ≈ $' + usd;
  }

  function card(d) {
    var name = String(d.name || d._slug);
    var title = d.year > 1900 ? name + ' · ' + d.year : name;
    var meta = metaLine(d);
    var spec = specLine(d);

    var tiers = '';
    if (d.p7 > 0 && d.p30 > 0 && (d.p7 !== d.p1 || d.p30 !== d.p1)) {
      tiers = '<p class="tiers">7–29: ' + esc(money(d.p7)) +
              ' · 30+: ' + esc(money(d.p30)) + '</p>';
    }

    /* ფოტოს ადგილი. ცარიელი ჩარჩო და არა გატეხილი <img>: ფაილი მართლა არ
       არსებობს, და 404-ის მოთხოვნა ყოველ ბარათზე უბრალოდ ნაგავია. */
    var ph = '<div class="ph ph-none" aria-hidden="true"></div>';

    return '<article class="car car-live" data-analytics-car data-car="' + esc(d._slug) +
      '" data-car-name="' + esc(name) + '" data-price="' + esc(d.p1) + '">' +
      ph + '<div class="in">' +
      '<div class="trow"><h3>' + esc(title) + '</h3>' +
      '<span class="p">' + esc(money(d.p1)) + ' <small>/ ' + esc(cat.u.day) + '</small></span></div>' +
      (meta ? '<p class="sub">' + esc(meta) + '</p>' : '') +
      (spec ? '<p class="meta">' + esc(spec) + '</p>' : '') +
      tiers +
      '<div class="btns"><button class="btn sm" type="button" data-booking-open ' +
      'data-car="' + esc(d._slug) + '" data-car-name="' + esc(name) + '">' +
      esc(cat.book) + '</button></div></div></article>';
  }

  /* ── გაშვება ───────────────────────────────────────────────────────── */

  /* რომელი მოდელები უკვე ხატია ამ გვერდზე. დუბლიკატი უარესია, ვიდრე
     დაკარგული ბარათი: ერთი და იგივე მანქანა ორჯერ, ორი სხვადასხვა ფასით
     (ჩაშენებული და ცოცხალი), კლიენტს ეუბნება, რომ საიტს არ ენდოს. */
  var already = {};
  document.querySelectorAll('[data-car]').forEach(function (el) {
    if (el.dataset.car) already[el.dataset.car] = 1;
  });

  var url = 'https://firestore.googleapis.com/v1/projects/' + encodeURIComponent(pid) +
    '/databases/(default)/documents/fleet?pageSize=300';

  fetch(url)
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (json) {
      if (!json || !Array.isArray(json.documents)) return;

      var rows = [];
      json.documents.forEach(function (raw) {
        var d = fsDoc(raw);
        if (!d) return;
        /* `fleet/_probe` არის ნებართვის შემოწმება, რომელსაც სინქრონიზაცია
           წერს — მანქანა არ არის. */
        if (!d._slug || d._slug.charAt(0) === '_') return;
        if (already[d._slug]) return;
        if (!fresh(d)) return;
        /* ნულოვანი ფასი ბარათს უსარგებლოს ხდის — და უფრო საშიშია, ვიდრე
           ბარათის არქონა: „0 ₾ / დღე" შეთავაზებაა. */
        if (!(Number(d.p1) > 0)) return;
        rows.push(d);
      });

      if (!rows.length) return;

      /* იაფიდან ძვირისკენ — იგივე რიგი, რაც სტატიკურ ბარათებს აქვთ. */
      rows.sort(function (a, b) { return (Number(a.p1) || 0) - (Number(b.p1) || 0); });

      var html = {}, added = 0;
      rows.forEach(function (d) {
        /* კატეგორიის ბადე, თუ არსებობს; თუ არა — შემკრები. კატეგორიის
           გამოცნობა (მაგ. „ადგილები > 6 ნიშნავს მინივენს") განზრახ არ ხდება:
           მანქანა არასწორ განყოფილებაში იმაზე უარესია, ვიდრე „სხვა"-ში. */
        var key = (d.cat && grids[d.cat]) ? d.cat : '*';
        var into = grids[key];
        if (!into) return;
        html[key] = (html[key] || '') + card(d);
        added += 1;

        /* ჯავშნის დიალოგი `FH_CFG.cars[slug]`-იდან ითვლის ფასს. ამის
           გარეშე ღილაკი გაიხსნებოდა და 0 ₾-ს დათვლიდა. */
        cfg.cars = cfg.cars || {};
        cfg.cars[d._slug] = {
          p1: Number(d.p1) || 0,
          p7: Number(d.p7) || Number(d.p1) || 0,
          p30: Number(d.p30) || Number(d.p7) || Number(d.p1) || 0,
          dep: Number(d.dep) || 0
        };
      });

      Object.keys(html).forEach(function (key) {
        grids[key].insertAdjacentHTML('beforeend', html[key]);
        /* შემკრები განყოფილება — და ნებისმიერი სხვა, რომელიც ცარიელი იყო —
           ახლა ჩნდება. `hidden` ატრიბუტით და არა style-ით: გვერდის CSS-ს
           `[hidden]` ისედაც სცნობს, და ატრიბუტი ეკრანის წამკითხველსაც
           ესმის. */
        var section = grids[key].closest('[data-live-other]');
        if (section) section.hidden = false;
      });

      if (added) {
        document.dispatchEvent(new CustomEvent('fh:live-catalogue', {
          detail: { count: added }
        }));
      }
    })
    .catch(function () {
      /* ქსელი არ არის, ან Firestore არ პასუხობს. გვერდი ისე რჩება, როგორც
         აიწყო — სტატიკური ბარათებით. გაფრთხილება არ ეწერება: კლიენტს
         საიტის შიდა პრობლემა არ ეხება. */
    });
})();
