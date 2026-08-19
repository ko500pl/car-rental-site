/* Drive On — Trip Workspace (მომხმარებლის მაკეტის ზუსტი პორტი).
   Needs: window.EXP (pts, towns), window.PLANNER_DATA (fleet, standardTours),
   window.DOWT (ლოკალიზებული ტექსტები), window.WX (ამინდი), Leaflet. */
(function () {
  var E = window.EXP, D = window.PLANNER_DATA, T = window.DOWT;
  if (!E || !D || !T || !window.L) return;
  var $ = function (id) { return document.getElementById(id); };
  var root = $('dow');
  if (!root) return;
  var PTS = E.pts, TOWNS = E.towns;
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
  /* კალიბრებული სავალი დროის მოდელი — იგივე, რაც explorer/planner-ში */
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
    var m = Math.max(0, Math.round(min));
    var h = Math.floor(m / 60), r = m % 60;
    if (h && r) return h + ' ' + T.h + ' ' + r + ' ' + T.m;
    if (h) return h + ' ' + T.h;
    return r + ' ' + T.m;
  }
  function iso(d) { return d.toISOString().slice(0, 10); }

  /* ── state ─────────────────────────────────────────────────────────── */
  var origin0 = TOWNS.filter(function (t) { return t.s === 'town:tbilisi'; })[0] ||
    TOWNS.filter(function (t) { return t.k === 'city'; })[0] || TOWNS[0];
  var st = {
    origin: { n: origin0.n, la: origin0.la, lo: origin0.lo, f: origin0.f, v: origin0.v },
    start: iso(new Date(Date.now() + 6048e5)), end: iso(new Date(Date.now() + 7776e5)),
    days: 3, people: 2, transport: 'suggest',
    dayHours: [8, 8, 8], dayGridOpen: false,
    selected: [], visited: {},
    q: '', cat: '', reg: '', minRating: 0, visitedFilter: '', fitsOnly: false,
    tourId: '', detail: null,
    traffic: false, weather: true,
    tab: 'map'
  };
  try { var v0 = JSON.parse(localStorage.getItem('do-visited') || '{}'); if (v0 && typeof v0 === 'object') st.visited = v0; } catch (e) {}
  var mh = location.hash.match(/#trip=([^&]+)/);
  if (mh) {
    try { st.selected = decodeURIComponent(mh[1]).split(',').filter(function (s) { return BY[s]; }); } catch (e) {}
  }

  /* ── engine ───────────────────────────────────────────────────────── */
  function lastPoint() {
    if (!st.selected.length) return st.origin;
    return BY[st.selected[st.selected.length - 1]] || st.origin;
  }
  function travel(a, b) { return leg(a, b).min; }
  function usedMin() {
    var t = 0, prev = st.origin;
    st.selected.forEach(function (s) { var p = BY[s]; if (!p) return; t += travel(prev, p) + p.hh * 60; prev = p; });
    if (st.selected.length) t += travel(prev, st.origin);
    return t;
  }
  function budgetMin() {
    var t = 0;
    for (var i = 0; i < st.days; i++) t += (st.dayHours[i] || 8) * 60;
    return t;
  }
  function cost(p) { return p.hh * 60 + travel(lastPoint(), p) * 1.2; }
  function fits(p) {
    if (st.selected.indexOf(p.s) >= 0) return true;
    return cost(p) <= budgetMin() - usedMin() + 1;
  }
  function visible() {
    var q = st.q.trim().toLowerCase();
    var routeTab = st.tab === 'route' && window.innerWidth <= 960;
    return PTS.filter(function (p) {
      if (routeTab && st.selected.indexOf(p.s) < 0) return false;
      if (st.reg && p.g !== st.reg) return false;
      if (st.cat && p.ty !== st.cat) return false;
      if (st.minRating && (p.r || 0) < st.minRating) return false;
      if (st.visitedFilter === 'yes' && !st.visited[p.s]) return false;
      if (st.visitedFilter === 'no' && st.visited[p.s]) return false;
      if (q && ((p.n + ' ' + (p.names || []).join(' ') + ' ' + p.gn).toLowerCase().indexOf(q) < 0)) return false;
      if (st.fitsOnly && !fits(p)) return false;
      return true;
    });
  }
  function mountainRoute() {
    return st.selected.some(function (s) { var p = BY[s]; return p && ((p.rd || 0) >= 2 || (p.el || 0) > 1200); });
  }
  function suggestCar() {
    if (!st.selected.length || !D.fleet || !D.fleet.length) return null;
    if (st.transport === 'own') return null;
    var need4 = mountainRoute();
    var cand = D.fleet.filter(function (c) {
      if (c.seats < Math.min(8, st.people)) return false;
      if (need4) return c.cat === 'offroad' || c.cat === 'suv' || c.cl >= 190;
      return true;
    });
    cand.sort(function (a, b) { return a.price - b.price; });
    return cand[0] || D.fleet[0];
  }

  /* ── map ──────────────────────────────────────────────────────────── */
  var GEO = [[41.52, 41.52], [41.8, 41.7], [42.15, 41.66], [42.35, 41.57], [42.6, 41.62], [42.85, 41.13], [43.05, 40.6], [43.2, 40.3], [43.38, 40.07], [43.55, 40.3], [43.6, 40.8], [43.35, 41.2], [43.2, 41.6], [43.1, 42.1], [43.0, 42.6], [42.9, 43.0], [42.75, 43.4], [42.8, 43.8], [42.7, 44.2], [42.75, 44.6], [42.65, 45.0], [42.6, 45.4], [42.45, 45.7], [42.35, 46.2], [41.9, 46.6], [41.6, 46.5], [41.4, 46.3], [41.2, 45.9], [41.1, 45.5], [41.3, 45.2], [41.45, 44.9], [41.2, 44.6], [41.1, 44.2], [41.25, 43.8], [41.1, 43.45], [41.05, 43.2], [41.2, 42.8], [41.45, 42.6], [41.4, 42.2], [41.55, 41.8], [41.52, 41.52]];
  var map = L.map($('dowmap'), { zoomControl: true, minZoom: 6 }).setView([42.05, 43.6], 7);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap, &copy; CARTO', maxZoom: 18, crossOrigin: true
  }).addTo(map);
  L.polygon([[[85, -180], [85, 180], [-85, 180], [-85, -180]], GEO], {
    stroke: false, fillColor: '#8a97a3', fillOpacity: 0.45, interactive: false
  }).addTo(map);
  L.polyline(GEO, { color: '#0b2f4d', weight: 1.2, opacity: 0.5, interactive: false }).addTo(map);
  var markers = L.layerGroup().addTo(map);
  var wxLayer = L.layerGroup().addTo(map);
  var routeLayer = L.layerGroup().addTo(map);
  window.FH_TRAVEL_MAP = map;
  map.on('zoomend moveend', drawMarkers);

  function drawMarkers() {
    var z = map.getZoom(), list = visible();
    markers.clearLayers();
    var pts = list.map(function (p) { return { p: p, xy: map.latLngToLayerPoint([p.la, p.lo]) }; });
    var groups = [], rad = z >= 11 ? 0 : 44;
    pts.forEach(function (pt) {
      var g = null;
      for (var i = 0; i < groups.length; i++) {
        if (groups[i].xy.distanceTo(pt.xy) < rad) { g = groups[i]; break; }
      }
      if (g) g.items.push(pt.p); else groups.push({ xy: pt.xy, items: [pt.p] });
    });
    groups.forEach(function (g) {
      var first = g.items[0];
      if (g.items.length > 1) {
        var size = g.items.length > 9 ? 40 : 34;
        var mk = L.marker([first.la, first.lo], {
          icon: L.divIcon({ className: '', html: '<div class="do-cluster" style="width:' + size + 'px;height:' + size + 'px">' + g.items.length + '</div>', iconSize: [size, size], iconAnchor: [size / 2, size / 2] }),
          keyboard: true, title: g.items.length + ' ' + T.places
        });
        var clicks = 0;
        mk.on('click', function () {
          clicks++;
          setTimeout(function () {
            if (clicks === 1) { st.detail = g.items.map(function (x) { return x.s; }); render(); }
            else map.setView([first.la, first.lo], Math.min(13, map.getZoom() + 2));
            clicks = 0;
          }, 220);
        });
        markers.addLayer(mk);
      } else {
        var p = first, sel = st.selected.indexOf(p.s), vis = st.visited[p.s], ok = fits(p);
        var bg = sel >= 0 ? '#0d94ae' : vis ? '#7f8c99' : ok ? '#0b2f4d' : '#b9c6d1';
        var label = sel >= 0 ? String(sel + 1) : '';
        var size = sel >= 0 ? 26 : 20;
        var mk1 = L.marker([p.la, p.lo], {
          icon: L.divIcon({ className: '', html: '<div class="do-pin" style="width:' + size + 'px;height:' + size + 'px;background:' + bg + ';opacity:' + (vis && sel < 0 ? '.6' : '1') + '">' + label + '</div>', iconSize: [size, size], iconAnchor: [size / 2, size / 2] }),
          title: p.n, keyboard: true
        });
        mk1.on('click', function () { st.detail = [p.s]; render(); });
        markers.addLayer(mk1);
      }
    });
  }

  /* ამინდი: რეგიონული ჩიპები Open-Meteo-დან (მოგზაურობის პირველი დღე) */
  var wxCache = null, wxFor = '';
  function regionCentroids() {
    var by = {};
    PTS.forEach(function (p) {
      (by[p.g] || (by[p.g] = { la: 0, lo: 0, n: 0, gn: p.gn })).la += p.la;
      by[p.g].lo += p.lo; by[p.g].n += 1;
    });
    return Object.keys(by).map(function (k) {
      var g = by[k];
      return { g: k, gn: g.gn, la: g.la / g.n, lo: g.lo / g.n };
    });
  }
  function drawWeather() {
    wxLayer.clearLayers();
    if (!st.weather || !window.WX) return;
    var day = WX.inRange(st.start) ? st.start : iso(new Date());
    var cents = regionCentroids();
    if (wxCache && wxFor === day) return paintWx(cents, wxCache);
    WX.get(cents.map(function (c) { return { la: c.la, lo: c.lo }; }), day).then(function (w) {
      wxCache = w; wxFor = day;
      if (st.weather) paintWx(cents, w);
    });
  }
  function paintWx(cents, w) {
    wxLayer.clearLayers();
    cents.forEach(function (c, i) {
      if (!w || !w[i]) return;
      var t = Math.round(w[i].tmax);
      wxLayer.addLayer(L.marker([c.la, c.lo], {
        interactive: false,
        icon: L.divIcon({ className: '', html: '<div class="do-wx">' + esc(c.gn) + ' ' + (t > 0 ? '+' : '') + t + '°</div>', iconSize: [null, 18] })
      }));
    });
  }

  var reqToken = 0, fitNext = false;
  function drawRoute() {
    routeLayer.clearLayers();
    var sel = st.selected.map(function (s) { return BY[s]; }).filter(Boolean);
    if (!sel.length) { setStatus(false, false); return; }
    var pts = [st.origin].concat(sel).concat([st.origin]);
    var straight = pts.map(function (p) { return [p.la, p.lo]; });
    routeLayer.addLayer(L.polyline(straight, { color: '#0b2f4d', weight: 3, opacity: 0.35, dashArray: '6 6' }));
    setStatus(true, false);
    var coords = pts.map(function (p) { return p.lo + ',' + p.la; }).join(';');
    var token = ++reqToken;
    fetch('https://router.project-osrm.org/route/v1/driving/' + coords + '?overview=full&geometries=geojson')
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (token !== reqToken) return;
        var g = j && j.routes && j.routes[0] && j.routes[0].geometry;
        if (!g) throw new Error('no geometry');
        routeLayer.clearLayers();
        var line = g.coordinates.map(function (c) { return [c[1], c[0]]; });
        L.polyline(line, { color: '#0b2f4d', weight: 5, opacity: 0.9 }).addTo(routeLayer);
        if (st.traffic) {
          var n = line.length, seg = Math.max(2, Math.floor(n / 9));
          for (var i = 0; i + seg < n; i += seg * 3) {
            L.polyline(line.slice(i, i + seg), { color: i % 2 ? '#c0392b' : '#d98324', weight: 7, opacity: 0.75 }).addTo(routeLayer);
          }
        }
        setStatus(false, false);
        if (fitNext) { fitNext = false; map.fitBounds(L.latLngBounds(line).pad(0.12)); }
      })
      .catch(function () {
        if (token !== reqToken) return;
        setStatus(false, true);
        if (fitNext) { fitNext = false; map.fitBounds(L.latLngBounds(straight).pad(0.15)); }
      });
  }
  var routeKey = '';
  function syncRoute() {
    var key = st.selected.join('>') + '|' + st.origin.n + '|' + (st.traffic ? 't' : '');
    if (key !== routeKey) { routeKey = key; drawRoute(); }
  }
  function setStatus(loading, error) {
    $('dowloading').hidden = !loading;
    $('dowerror').hidden = !error;
  }

  /* ── actions ──────────────────────────────────────────────────────── */
  function toggle(slug) {
    var i = st.selected.indexOf(slug);
    if (i >= 0) st.selected.splice(i, 1);
    else {
      var p = BY[slug];
      if (p && fits(p)) st.selected.push(slug);
    }
    render();
  }
  function setVisited(slug) {
    if (st.visited[slug]) delete st.visited[slug]; else st.visited[slug] = 1;
    try { localStorage.setItem('do-visited', JSON.stringify(st.visited)); } catch (e) {}
    render();
  }
  function moveSel(i, d) {
    var j = i + d;
    if (j < 0 || j >= st.selected.length) return;
    var x = st.selected[j]; st.selected[j] = st.selected[i]; st.selected[i] = x;
    render();
  }
  function setDays(n) {
    st.days = Math.max(1, Math.min(30, n));
    var d = new Date(st.start);
    if (!isNaN(d)) st.end = iso(new Date(d.getTime() + (st.days - 1) * 864e5));
    while (st.dayHours.length < st.days) st.dayHours.push(8);
    render();
  }
  function flash(msg) {
    var el = $('dowmsg');
    el.textContent = msg;
    clearTimeout(flash._t);
    flash._t = setTimeout(function () { el.textContent = ''; }, 3200);
  }

  /* ── render ───────────────────────────────────────────────────────── */
  var typeName = {}; (E.pts || []).forEach(function (p) { typeName[p.ty] = p.t; });

  function chipsSpec() {
    return [
      { label: '3+ ★', on: st.minRating === 3, act: function () { st.minRating = st.minRating === 3 ? 0 : 3; } },
      { label: '4+ ★', on: st.minRating === 4, act: function () { st.minRating = st.minRating === 4 ? 0 : 4; } },
      { label: '5 ★', on: st.minRating === 5, act: function () { st.minRating = st.minRating === 5 ? 0 : 5; } },
      { label: T.visited, on: st.visitedFilter === 'yes', act: function () { st.visitedFilter = st.visitedFilter === 'yes' ? '' : 'yes'; } },
      { label: T.notVisited, on: st.visitedFilter === 'no', act: function () { st.visitedFilter = st.visitedFilter === 'no' ? '' : 'no'; } },
      { label: T.fitsTime, on: st.fitsOnly, act: function () { st.fitsOnly = !st.fitsOnly; } }
    ];
  }

  function render() {
    var used = usedMin(), budget = budgetMin();
    /* form values */
    $('dowstart').value = st.start;
    $('dowend').value = st.end;
    $('dowdays').textContent = st.days + ' ' + T.day;
    $('dowpeople').textContent = st.people + ' ' + T.person;
    $('dowbudget').value = (st.dayHours[0] || 8) + ' ' + T.h;
    $('dowchosen').textContent = hm(budget);
    $('dowused').textContent = hm(used);
    $('dowleft').textContent = hm(Math.max(0, budget - used));
    $('dowmeter').style.width = Math.min(100, Math.round(used / Math.max(1, budget) * 100)) + '%';

    /* by-day grid */
    var dg = $('dowdaygrid');
    dg.hidden = !st.dayGridOpen;
    if (st.dayGridOpen) {
      dg.innerHTML = '';
      for (var i = 0; i < st.days; i++) {
        (function (i) {
          var row = document.createElement('div');
          row.className = 'dow-dayrow';
          row.innerHTML = '<span>' + (i + 1) + ' ' + esc(T.day) + '</span>' +
            '<button type="button" aria-label="−">−</button>' +
            '<b>' + (st.dayHours[i] || 8) + ' ' + esc(T.h) + '</b>' +
            '<button type="button" aria-label="+">+</button>';
          var bs = row.querySelectorAll('button');
          bs[0].onclick = function () { st.dayHours[i] = Math.max(1, (st.dayHours[i] || 8) - 0.5); render(); };
          bs[1].onclick = function () { st.dayHours[i] = Math.min(14, (st.dayHours[i] || 8) + 0.5); render(); };
          dg.appendChild(row);
        })(i);
      }
    }

    /* tour chip */
    var tour = (D.standardTours || []).filter(function (t) { return t.s === st.tourId; })[0];
    $('dowtourchip').hidden = !tour;
    if (tour) {
      $('dowtourname').textContent = tour.n;
      $('dowtourmeta').textContent = tour.days + ' ' + T.day + ' · ' + tour.km + ' ' + T.km + (tour.drive ? ' · ' + tour.drive : '') + ' · ' + tour.carLabel;
    }
    $('dowactions').hidden = !st.selected.length;

    /* list */
    var list = visible();
    $('dowcount').textContent = T.total + ' ' + list.length + ' ' + T.place;
    $('dowselcount').textContent = T.chosenN + ' ' + st.selected.length;
    var selIdx = {}; st.selected.forEach(function (s, i) { selIdx[s] = i + 1; });
    var lb = $('dowlist');
    lb.innerHTML = '';
    list.forEach(function (p) {
      var on = !!selIdx[p.s], ok = fits(p), vis = !!st.visited[p.s];
      var row = document.createElement('div');
      row.className = 'dow-place' + (on ? ' on' : '') + (!ok && !on ? ' dim' : '');
      var d0 = leg(st.origin, p);
      row.innerHTML =
        '<input type="checkbox" aria-label="' + esc(p.n) + '"' + (on ? ' checked' : '') + '>' +
        '<button type="button" class="dow-place-main">' +
        '<span class="dow-ava"' + (on ? ' style="background:#cdeef4"' : '') + '>' + esc(on ? String(selIdx[p.s]) : p.n.slice(0, 1)) + '</span>' +
        '<span class="dow-place-t"><span class="dow-place-n">' + esc(p.n) + '</span>' +
        '<span>' + esc(p.gn) + ' · ' + esc(p.t) + (p.r ? ' · ' + Number(p.r).toFixed(1) + ' ★' : '') + '</span>' +
        '<span>' + hm(p.hh * 60) + ' ' + esc(T.visit) + ' · ' + Math.round(d0.km) + ' ' + esc(T.km) +
        (vis ? ' · ' + esc(T.visited) : (ok ? '' : ' · ' + esc(T.noFit))) + '</span></span></button>' +
        '<button type="button" class="dow-info" aria-label="' + esc(T.details) + '"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0b2f4d" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 11v5M12 8h.01"></path></svg></button>';
      row.querySelector('input').onchange = function () { toggle(p.s); };
      row.querySelector('.dow-place-main').onclick = function () { toggle(p.s); };
      row.querySelector('.dow-info').onclick = function () { st.detail = [p.s]; render(); };
      lb.appendChild(row);
    });
    $('dowempty').hidden = list.length > 0;

    /* chips */
    var cb = $('dowchips');
    cb.innerHTML = '';
    chipsSpec().forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'dow-chip' + (c.on ? ' on' : '');
      b.setAttribute('aria-pressed', c.on ? 'true' : 'false');
      b.textContent = c.label;
      b.onclick = function () { c.act(); render(); };
      cb.appendChild(b);
    });

    /* route chips (map) + route panel (mobile) */
    var rc = $('dowroutechips'), rp = $('dowroutelist');
    rc.innerHTML = ''; rp.innerHTML = '';
    var prev = st.origin;
    st.selected.forEach(function (s, i) {
      var p = BY[s]; if (!p) return;
      var lg = travel(prev, p); prev = p;
      var mkRow = function (compact) {
        var el = document.createElement('div');
        el.className = compact ? 'dow-stop sm' : 'dow-stop';
        el.innerHTML = '<span class="dow-stop-i">' + (i + 1) + '</span><b>' + esc(p.n) + '</b>' +
          '<small>' + hm(lg) + ' ' + esc(T.road) + '</small>' +
          '<button type="button" aria-label="↑">↑</button><button type="button" aria-label="↓">↓</button><button type="button" aria-label="×">×</button>';
        var bs = el.querySelectorAll('button');
        bs[0].onclick = function () { moveSel(i, -1); };
        bs[1].onclick = function () { moveSel(i, 1); };
        bs[2].onclick = function () { toggle(p.s); };
        return el;
      };
      rc.appendChild(mkRow(true));
      rp.appendChild(mkRow(false));
    });
    $('downostops').hidden = st.selected.length > 0;
    $('dowrpused').textContent = hm(used);
    $('dowrpleft').textContent = hm(Math.max(0, budget - used));

    /* car suggestion */
    var car = suggestCar();
    ['dowcar', 'dowcar2'].forEach(function (id) {
      var box = $(id);
      if (!box) return;
      box.hidden = !car;
      if (!car) return;
      box.querySelector('.dow-car-n').textContent = car.n;
      box.querySelector('.dow-car-p').textContent = car.price + ' ₾ / ' + T.day1 + ' · ' + T.sum + ' ' + (car.price * Math.max(1, st.days)) + ' ₾';
      box.querySelector('.dow-car-s').textContent = car.seats + ' ' + T.seat + ' · ' + car.cat_n + (car.fuel ? ' · ' + car.fuel + ' ' + T.per100 : '');
      box.querySelector('.dow-car-r').textContent = mountainRoute() ? T.need4 : T.noNeed4;
    });

    /* toggles */
    $('dowtraffic').classList.toggle('on', st.traffic);
    $('dowtraffic').setAttribute('aria-pressed', st.traffic ? 'true' : 'false');
    $('dowweather').classList.toggle('on', st.weather);
    $('dowweather').setAttribute('aria-pressed', st.weather ? 'true' : 'false');

    /* detail panel */
    var dp = $('dowdetail');
    dp.hidden = !(st.detail && st.detail.length);
    if (st.detail && st.detail.length) {
      $('dowdtitle').textContent = st.detail.length > 1 ? st.detail.length + ' ' + T.inGroup : T.placeDetails;
      var body = $('dowdbody');
      body.innerHTML = '';
      st.detail.forEach(function (s) {
        var p = BY[s]; if (!p) return;
        var on = st.selected.indexOf(p.s) >= 0, ok = fits(p);
        var el = document.createElement('div');
        el.className = 'dow-ditem';
        el.innerHTML = '<b>' + esc(p.n) + '</b>' +
          '<span>' + esc(p.gn) + ' · ' + esc(p.t) + (p.r ? ' · ' + Number(p.r).toFixed(1) + ' ★' : '') + '</span>' +
          '<span>' + esc(T.visit) + ' ' + hm(p.hh * 60) + ' · ' + Math.round(leg(st.origin, p).km) + ' ' + esc(T.km) + '</span>' +
          '<div class="dow-ditem-b"><button type="button" class="a">' + esc(on ? T.removeStop : (ok ? T.addStop : T.noFit)) + '</button>' +
          '<button type="button" class="v">' + esc(st.visited[p.s] ? T.visitedYes : T.markVisited) + '</button>' +
          (p.u ? '<a class="dow-ditem-link" href="' + esc(p.u) + '">' + esc(T.fullPage) + '</a>' : '') + '</div>';
        el.querySelector('.a').onclick = function () { if (on || ok) toggle(p.s); };
        el.querySelector('.v').onclick = function () { setVisited(p.s); };
        body.appendChild(el);
      });
    }

    /* mobile columns */
    var mob = window.innerWidth <= 960;
    root.style.setProperty('--m-places', !mob || st.tab === 'places' || st.tab === 'route' ? 'flex' : 'none');
    root.style.setProperty('--m-map', !mob || st.tab === 'map' ? 'block' : 'none');
    $('dowroutepanel').hidden = !(mob && st.tab === 'route');
    ['places', 'map', 'route'].forEach(function (t) {
      $('dowtab-' + t).classList.toggle('on', st.tab === t);
    });

    drawMarkers();
    drawWeather();
    syncRoute();
  }

  /* ── wire events ──────────────────────────────────────────────────── */
  /* origin autocomplete */
  var pool = TOWNS.map(function (t) { return { n: t.n, meta: t.t, la: t.la, lo: t.lo, f: t.f, v: t.v, names: t.names }; })
    .concat(PTS.map(function (p) { return { n: p.n, meta: p.gn, la: p.la, lo: p.lo, f: p.f, v: p.v, names: p.names }; }));
  var oi = $('doworigin'), sug = $('dowsuggest');
  oi.value = st.origin.n;
  function showSuggest() {
    var q = oi.value.trim().toLowerCase();
    var res = (q ? pool.filter(function (x) {
      return (x.n + ' ' + (x.names || []).join(' ')).toLowerCase().indexOf(q) >= 0;
    }) : pool).slice(0, 8);
    sug.innerHTML = '';
    if (!res.length) {
      sug.innerHTML = '<div class="dow-sug-none">' + esc(T.notFound) + '</div>';
    }
    res.forEach(function (x) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'option');
      b.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0d94ae" stroke-width="2" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path><circle cx="12" cy="10" r="3"></circle></svg>' +
        '<b>' + esc(x.n) + '</b><small>' + esc(x.meta) + '</small>';
      b.onclick = function () {
        st.origin = { n: x.n, la: x.la, lo: x.lo, f: x.f || 1.4, v: x.v || 55 };
        oi.value = x.n;
        sug.hidden = true;
        fitNext = true;
        map.setView([x.la, x.lo], 8);
        routeKey = '';
        render();
      };
      sug.appendChild(b);
    });
    sug.hidden = false;
  }
  oi.addEventListener('input', showSuggest);
  oi.addEventListener('focus', showSuggest);
  oi.addEventListener('keydown', function (e) { if (e.key === 'Escape') sug.hidden = true; });
  document.addEventListener('click', function (e) {
    if (!sug.contains(e.target) && e.target !== oi) sug.hidden = true;
  });
  $('dowmyloc').onclick = function () {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(function (pos) {
      st.origin = { n: T.myLocName, la: pos.coords.latitude, lo: pos.coords.longitude, f: 1.4, v: 55 };
      oi.value = T.myLocName;
      map.setView([pos.coords.latitude, pos.coords.longitude], 9);
      routeKey = '';
      render();
    }, function () { oi.value = st.origin.n; });
  };
  $('dowplan').onclick = function () { oi.focus(); oi.select(); showSuggest(); };

  $('dowstart').onchange = function () {
    st.start = this.value;
    var d = new Date(st.start);
    if (!isNaN(d)) st.end = iso(new Date(d.getTime() + (st.days - 1) * 864e5));
    wxCache = null;
    render();
  };
  $('dowend').onchange = function () {
    st.end = this.value;
    var a = new Date(st.start), b = new Date(st.end);
    if (!isNaN(a) && !isNaN(b)) setDays(Math.max(1, Math.round((b - a) / 864e5) + 1)); else render();
  };
  $('dowdaysminus').onclick = function () { setDays(st.days - 1); };
  $('dowdaysplus').onclick = function () { setDays(st.days + 1); };
  $('dowpplminus').onclick = function () { st.people = Math.max(1, st.people - 1); render(); };
  $('dowpplplus').onclick = function () { st.people = Math.min(12, st.people + 1); render(); };
  $('dowtransport').onchange = function () { st.transport = this.value; render(); };
  $('dowbudminus').onclick = function () { st.dayHours = st.dayHours.map(function (h) { return Math.max(1, (h || 8) - 0.5); }); render(); };
  $('dowbudplus').onclick = function () { st.dayHours = st.dayHours.map(function (h) { return Math.min(14, (h || 8) + 0.5); }); render(); };
  $('dowbudget').onchange = function () {
    var v = parseFloat(String(this.value).replace(',', '.'));
    if (!isNaN(v)) st.dayHours = st.dayHours.map(function () { return Math.max(1, Math.min(14, Math.round(v * 2) / 2)); });
    render();
  };
  $('dowbyday').onclick = function () { st.dayGridOpen = !st.dayGridOpen; render(); };
  $('dowq').oninput = function () { st.q = this.value; render(); };
  $('dowcat').onchange = function () { st.cat = this.value; render(); };
  $('dowreg').onchange = function () { st.reg = this.value; render(); };
  $('dowreset').onclick = function () {
    st.cat = ''; st.reg = ''; st.minRating = 0; st.visitedFilter = ''; st.fitsOnly = false; st.q = '';
    $('dowq').value = ''; $('dowcat').value = ''; $('dowreg').value = '';
    render();
  };
  $('dowtraffic').onclick = function () { st.traffic = !st.traffic; routeKey = ''; render(); };
  $('dowweather').onclick = function () { st.weather = !st.weather; render(); };
  $('dowdclose').onclick = function () { st.detail = null; render(); };
  $('dowtourclear').onclick = function () { st.tourId = ''; st.selected = []; render(); };
  ['places', 'map', 'route'].forEach(function (t) {
    $('dowtab-' + t).onclick = function () {
      st.tab = t; render();
      setTimeout(function () { map.invalidateSize(); }, 60);
    };
  });
  window.addEventListener('resize', function () { render(); });

  /* save / share */
  function tripObj() {
    var tour = (D.standardTours || []).filter(function (t) { return t.s === st.tourId; })[0];
    return {
      name: tour ? tour.n : st.origin.n + ' · ' + st.days + ' ' + T.day,
      start: st.start, end: st.end, people: st.people, stops: st.selected.slice()
    };
  }
  $('dowsave').onclick = function () {
    var trip = tripObj(), saved = [];
    try { saved = JSON.parse(localStorage.getItem('do-trips') || '[]'); } catch (e) { saved = []; }
    saved.push(trip);
    try { localStorage.setItem('do-trips', JSON.stringify(saved)); } catch (e) {}
    if (window.FH && window.FH.addTrip) {
      try {
        window.FH.addTrip({ title: trip.name, date: trip.start, days: st.days, stops: st.selected.map(function (s) { return { n: (BY[s] || {}).n || s }; }), url: shareUrl() });
      } catch (e) {}
    }
    flash(T.saved);
  };
  function shareUrl() { return location.href.split('#')[0] + '#trip=' + encodeURIComponent(st.selected.join(',')); }
  $('dowshare').onclick = function () {
    var trip = tripObj();
    var text = trip.name + ' · ' + st.start + ' – ' + st.end + ' · ' + st.selected.length + ' ' + T.stop;
    var url = shareUrl();
    if (navigator.share) {
      navigator.share({ title: 'Drive On', text: text, url: url }).catch(function () {});
      flash(T.shareOpened);
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(text + ' — ' + url).then(function () { flash(T.linkCopied); })
        .catch(function () { flash(url); });
    } else flash(url);
  };

  /* ── tours drawer ─────────────────────────────────────────────────── */
  var tq = '', tf = { dur: '', type: '', season: '', car: '' };
  function renderTours() {
    var list = (D.standardTours || []).filter(function (r) {
      var s = (r.n + ' ' + (r.sh || '')).toLowerCase();
      if (tq && s.indexOf(tq) < 0) return false;
      if (tf.type && r.purpose !== tf.type) return false;
      if (tf.season && r.season !== tf.season) return false;
      if (tf.car && r.car !== tf.car) return false;
      if (tf.dur === '1-2' && r.days > 2) return false;
      if (tf.dur === '3-4' && (r.days < 3 || r.days > 4)) return false;
      if (tf.dur === '5+' && r.days < 5) return false;
      return true;
    });
    var box = $('dowtlist');
    box.innerHTML = '';
    list.forEach(function (r) {
      var el = document.createElement('div');
      el.className = 'dow-tour';
      el.innerHTML =
        '<div class="dow-tour-ph">' + (r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy">' : esc(r.n)) + '</div>' +
        '<div class="dow-tour-in"><b>' + esc(r.n) + '</b>' +
        '<span>' + r.days + ' ' + esc(T.day) + ' · ' + r.km + ' ' + esc(T.km) + (r.drive ? ' · ' + esc(T.onRoad) + ' ' + esc(r.drive) : '') + '</span>' +
        '<span>' + esc(r.carLabel) + ' · ' + r.minPeople + '–' + r.maxPeople + ' ' + esc(T.person) + (r.region ? ' · ' + esc(r.region) : '') + '</span>' +
        '<span class="dow-tour-d">' + esc(r.sh || '') + '</span>' +
        '<button type="button">' + esc(T.chooseTour) + '</button></div>';
      el.querySelector('button').onclick = function () {
        st.tourId = r.s;
        st.selected = (r.wp || []).filter(function (s) { return BY[s]; });
        st.days = r.days;
        st.dayHours = [];
        for (var i = 0; i < Math.max(r.days, 6); i++) st.dayHours.push(8);
        var d = new Date(st.start);
        if (!isNaN(d)) st.end = iso(new Date(d.getTime() + (st.days - 1) * 864e5));
        closeTours();
        fitNext = true;
        routeKey = '';
        render();
      };
      box.appendChild(el);
    });
    $('dowtempty').hidden = list.length > 0;
  }
  function openTours() { $('dowdrawer').hidden = false; renderTours(); }
  function closeTours() { $('dowdrawer').hidden = true; }
  $('dowtours').onclick = openTours;
  $('dowtclose').onclick = closeTours;
  $('dowtback').onclick = closeTours;
  $('dowtq').oninput = function () { tq = this.value.trim().toLowerCase(); renderTours(); };
  ['dur', 'type', 'season', 'car'].forEach(function (k) {
    $('dowtf-' + k).onchange = function () { tf[k] = this.value; renderTours(); };
  });
  $('dowtreset').onclick = function () {
    tq = ''; tf = { dur: '', type: '', season: '', car: '' };
    $('dowtq').value = '';
    ['dur', 'type', 'season', 'car'].forEach(function (k) { $('dowtf-' + k).value = ''; });
    renderTours();
  };

  /* ── booking modal ────────────────────────────────────────────────── */
  function openBooking() {
    $('dowbooking').hidden = false;
    $('dowbdone').hidden = true;
    $('dowbform').hidden = false;
    $('dowbinvalid').hidden = true;
    var car = suggestCar();
    $('dowbcar').textContent = car ? car.n : '';
    $('dowbsum').textContent = st.start + ' – ' + st.end + ' · ' + st.days + ' ' + T.day + ' · ' + st.people + ' ' + T.person + ' · ' + st.selected.length + ' ' + T.stop;
  }
  root.addEventListener('click', function (e) {
    var b = e.target.closest('[data-dow-book]');
    if (b) openBooking();
  });
  $('dowbclose').onclick = function () { $('dowbooking').hidden = true; };
  $('dowbback').onclick = function () { $('dowbooking').hidden = true; };
  $('dowbsend').onclick = function () {
    var name = $('dowbname').value.trim(), phone = $('dowbphone').value.trim();
    if (!name || !phone) { $('dowbinvalid').hidden = false; return; }
    var car = suggestCar();
    var body = new URLSearchParams({
      'form-name': 'contact', name: name, email: '',
      dates: st.start + ' – ' + st.end,
      message: 'Trip Workspace: ' + (car ? car.n : '') + ' · ' + phone + ' · ' + st.people + ' ppl · ' +
        st.selected.map(function (s) { return (BY[s] || {}).n || s; }).join(', ')
    }).toString();
    var origin = /netlify\.app$/.test(location.hostname) ? '' : 'https://subtle-naiad-c2db5d.netlify.app';
    fetch(origin + '/', { method: 'POST', mode: origin ? 'no-cors' : 'same-origin',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body }).catch(function () {});
    $('dowbform').hidden = true;
    $('dowbdone').hidden = false;
  };

  render();
  setTimeout(function () { map.invalidateSize(); }, 120);
})();
