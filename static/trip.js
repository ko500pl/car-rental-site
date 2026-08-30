/* RentUp — „ჩემი ტური“ (/trip/).
   მარშრუტი მოდის მისამართის ჰეშიდან: #trip=slug1,slug2;o=საწყისი;s=2026-08-26;d=3;h=8
   ხატავს იმავე მონაცემებით, რითიც დამგეგმავი ითვლის — EXP + PLANNER_DATA. */
(function () {
  var E = window.EXP, D = window.PLANNER_DATA, T = window.TRIPT;
  if (!E || !D || !T) return;
  var $ = function (id) { return document.getElementById(id); };
  if (!$('tripbody')) return;
  var PTS = E.pts, TOWNS = E.towns || [];
  var BY = {}; PTS.forEach(function (p) { BY[p.s] = p; });

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function hav(a1, o1, a2, o2) {
    var r = 6371, dl = (a2 - a1) * Math.PI / 180, dn = (o2 - o1) * Math.PI / 180;
    var x = Math.sin(dl / 2) * Math.sin(dl / 2) + Math.cos(a1 * Math.PI / 180) * Math.cos(a2 * Math.PI / 180) * Math.sin(dn / 2) * Math.sin(dn / 2);
    return 2 * r * Math.asin(Math.min(1, Math.sqrt(x)));
  }
  var RD_SLOW = { 2: { len: 30, v: 24 }, 3: { len: 45, v: 18 } };
  function leg(a, b) {
    var d = hav(a.la, a.lo, b.la, b.lo);
    var f = ((a.f || 1.4) + (b.f || 1.4)) / 2;
    var va = a.v || 55, vb = b.v || 55;
    var rank = Math.max(a.rd || 0, b.rd || 0);
    var mtn = (a.el || 0) > 1200 || (b.el || 0) > 1200;
    var v = (rank >= 1 || mtn || Math.min(va, vb) < 45) ? Math.min(va, vb) : (va + vb) / 2;
    if (mtn) { v = Math.min(v, 45); f = Math.max(f, 1.5); }
    if (rank === 1) v = Math.min(v, 40);
    var km = d * f, min;
    if (rank >= 2) {
      var rs = RD_SLOW[rank], kr = Math.min(km, rs.len);
      min = (kr / rs.v + (km - kr) / Math.max(v, 30)) * 60;
    } else {
      if (km < 12) v = Math.min(v, 32);
      min = (km / v) * 60;
    }
    return { km: km, min: min };
  }
  function hm(min) {
    var m = Math.max(0, Math.round(min)), h = Math.floor(m / 60), r = m % 60;
    if (h && r) return h + ' ' + T.hrs + ' ' + r + ' ' + T.minsW;
    if (h) return h + ' ' + T.hrs;
    return r + ' ' + T.minsW;
  }

  /* ── ჰეშის წაკითხვა ─────────────────────────────────────────────── */
  var st = { stops: [], origin: null, start: '', end: '', days: 3, hours: 8, people: 2 };
  var m = location.hash.match(/#trip=([^&]+)/);
  if (m) {
    try {
      var parts = decodeURIComponent(m[1]).split(';');
      st.stops = parts[0].split(',').filter(function (s) { return BY[s]; });
      parts.slice(1).forEach(function (kv) {
        var i = kv.indexOf('=');
        if (i < 0) return;
        var k = kv.slice(0, i), v = kv.slice(i + 1);
        if (k === 'o') st.originName = v;
        if (k === 's' && /^\d{4}-\d{2}-\d{2}$/.test(v)) st.start = v;
        if (k === 'd') st.days = Math.max(1, Math.min(30, parseInt(v, 10) || 3));
        if (k === 'h') st.hours = Math.max(1, Math.min(14, parseFloat(v) || 8));
        if (k === 'p') st.people = Math.max(1, Math.min(12, parseInt(v, 10) || 2));
      });
      if (st.start) {
        var d0 = new Date(st.start);
        if (!isNaN(d0)) st.end = new Date(d0.getTime() + (st.days - 1) * 864e5).toISOString().slice(0, 10);
      }
    } catch (e) {}
  }
  var start0 = null;
  if (st.originName) {
    start0 = TOWNS.filter(function (t) { return t.n === st.originName; })[0] ||
      PTS.filter(function (p) { return p.n === st.originName; })[0];
  }
  if (!start0) start0 = TOWNS.filter(function (t) { return t.s === 'town:tbilisi'; })[0] || TOWNS[0] || PTS[0];
  st.origin = { n: start0.n, la: start0.la, lo: start0.lo, f: start0.f, v: start0.v };

  if (!st.stops.length) { $('tripempty').hidden = false; return; }
  $('tripbody').hidden = false;

  /* ── ანგარიში ───────────────────────────────────────────────────── */
  var seq = st.stops.map(function (s) { return BY[s]; }).filter(Boolean);
  var legs = [], prev = st.origin, totKm = 0, totMin = 0, visitMin = 0;
  seq.forEach(function (p) {
    var l = leg(prev, p);
    legs.push(l); totKm += l.km; totMin += l.min; visitMin += p.hh * 60;
    prev = p;
  });
  var back = leg(prev, st.origin);
  totKm += back.km; totMin += back.min;

  function mountain() {
    return seq.some(function (p) { return (p.rd || 0) >= 2 || (p.el || 0) > 1200; });
  }
  function suggestCar() {
    if (!D.fleet || !D.fleet.length) return null;
    var need4 = mountain();
    var cand = D.fleet.filter(function (c) {
      if (c.seats < Math.min(8, st.people)) return false;
      if (need4) return c.cat === 'offroad' || c.cat === 'suv' || c.cl >= 190;
      return true;
    });
    cand.sort(function (a, b) { return a.price - b.price; });
    return cand[0] || D.fleet[0];
  }
  var car = suggestCar();

  /* სათაური და შესავალი */
  var regions = [];
  seq.forEach(function (p) { if (regions.indexOf(p.gn) < 0) regions.push(p.gn); });
  $('triph1').textContent = T.h1 + ' — ' + regions.slice(0, 3).join(', ');
  $('triplead').textContent = st.origin.n + ' · ' + seq.length + ' ' + T.stopsW +
    (st.start ? ' · ' + st.start + (st.end ? ' – ' + st.end : '') : '') +
    ' · ' + st.days + ' ' + T.days;

  /* ფაქტების ბლოკი — სტანდარტული ტურის გვერდის სტილში */
  var facts = [
    [T.days, st.days + ' ' + T.days],
    [T.total_km, Math.round(totKm) + ' ' + T.km],
    [T.total_drive, hm(totMin)],
    [T.visitW, hm(visitMin)],
    [T.car_needed, car ? car.cat_n : '—'],
    [T.fromW, st.origin.n]
  ];
  $('tripfacts').innerHTML = facts.map(function (f) {
    return '<div><dt class="k">' + esc(f[0]) + '</dt><dd class="v">' + esc(f[1]) + '</dd></div>';
  }).join('');

  /* ── დღეების გეგმა — დღიური ბიუჯეტით ─────────────────────────────── */
  var dayBudget = st.hours * 60, days = [], cur = { n: 1, items: [], min: 0 };
  seq.forEach(function (p, i) {
    var need = legs[i].min + p.hh * 60;
    if (cur.items.length && cur.min + need > dayBudget && days.length + 1 < st.days + 1) {
      days.push(cur); cur = { n: days.length + 1, items: [], min: 0 };
    }
    cur.items.push({ p: p, leg: legs[i] });
    cur.min += need;
  });
  if (cur.items.length) days.push(cur);
  $('tripdays').innerHTML = days.map(function (d) {
    return '<div class="trip-day"><h3>' + esc(T.dayW + ' ' + d.n) + ' <small>' + esc(hm(d.min)) + '</small></h3><ol>' +
      d.items.map(function (it) {
        return '<li><b>' + esc(it.p.n) + '</b> <small>' +
          esc(Math.round(it.leg.km) + ' ' + T.km + ' ' + T.driveW + ' · ' + hm(it.p.hh * 60) + ' ' + T.visitW) +
          '</small></li>';
      }).join('') + '</ol></div>';
  }).join('') +
    '<div class="trip-day back"><h3>' + esc(T.backW) + ' <small>' + esc(hm(back.min)) + '</small></h3>' +
    '<p>' + esc(st.origin.n + ' · ' + Math.round(back.km) + ' ' + T.km) + '</p></div>';

  /* ── გაჩერებების ბარათები ───────────────────────────────────────── */
  $('tripstops').innerHTML = seq.map(function (p, i) {
    return '<div class="card trip-card">' +
      (p.img ? '<img src="' + esc(p.img) + '" alt="" loading="lazy">' : '') +
      '<span class="tag">' + esc((i + 1) + ' · ' + p.t) + '</span>' +
      '<h3><a href="' + esc(p.u) + '">' + esc(p.n) + '</a></h3>' +
      '<p>' + esc(p.gn + (p.r ? ' · ' + Number(p.r).toFixed(1) + ' ★' : '')) + '</p>' +
      '<span class="price">' + esc(hm(p.hh * 60) + ' ' + T.visitW) + '</span></div>';
  }).join('');

  /* ── რუკა ───────────────────────────────────────────────────────── */
  if (window.L) {
    var map = L.map('tripmap', { scrollWheelZoom: false, minZoom: 6 });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap, &copy; CARTO', maxZoom: 18, crossOrigin: true
    }).addTo(map);
    var pts = [st.origin].concat(seq).concat([st.origin]);
    var straight = pts.map(function (p) { return [p.la, p.lo]; });
    var line = L.polyline(straight, { color: '#0b2f4d', weight: 3, opacity: .35, dashArray: '6 6' }).addTo(map);
    map.fitBounds(line.getBounds().pad(0.15));
    L.marker([st.origin.la, st.origin.lo], {
      title: st.origin.n,
      icon: L.divIcon({ className: '', html: '<div class="do-pin" style="width:26px;height:26px;background:#8a97a3">A</div>', iconSize: [26, 26], iconAnchor: [13, 13] })
    }).addTo(map);
    seq.forEach(function (p, i) {
      L.marker([p.la, p.lo], {
        title: p.n,
        icon: L.divIcon({ className: '', html: '<div class="do-pin" style="width:28px;height:28px;background:#0d94ae">' + (i + 1) + '</div>', iconSize: [28, 28], iconAnchor: [14, 14] })
      }).addTo(map).bindPopup('<b>' + esc(p.n) + '</b><br><a href="' + esc(p.u) + '">' + esc(p.gn) + '</a>');
    });
    fetch('https://router.project-osrm.org/route/v1/driving/' +
      pts.map(function (p) { return p.lo + ',' + p.la; }).join(';') + '?overview=full&geometries=geojson')
      .then(function (r) { return r.json(); }).then(function (j) {
        var g = j && j.routes && j.routes[0] && j.routes[0].geometry;
        if (!g) throw new Error('no geometry');
        map.removeLayer(line);
        var real = L.polyline(g.coordinates.map(function (c) { return [c[1], c[0]]; }),
          { color: '#0b2f4d', weight: 5, opacity: .9 }).addTo(map);
        map.fitBounds(real.getBounds().pad(0.12));
      }).catch(function () {
        var s = $('tripstatus');
        s.hidden = false; s.textContent = T.routeErr;
      });
  }

  /* ── ღილაკები ───────────────────────────────────────────────────── */
  function msg(text) {
    $('tripmsg').textContent = text;
    setTimeout(function () { $('tripmsg').textContent = ''; }, 2600);
  }
  $('tripplanner').href = T.plannerUrl.split('#')[0] + location.hash;
  $('tripshare').onclick = function () {
    var url = location.href;
    if (navigator.share) navigator.share({ title: $('triph1').textContent, url: url }).catch(function () {});
    else if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { msg(T.copied); }).catch(function () { msg(url); });
    else msg(url);
  };
  $('tripprint').onclick = function () { window.print(); };
  if (car) {
    var b = $('tripbook');
    b.setAttribute('data-car-name', car.n);
    b.href = T.fleetUrl;
    b.textContent = b.textContent + ' — ' + car.n;
  }
})();
