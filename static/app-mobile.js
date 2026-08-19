/* Drive On — Mobile App (მომხმარებლის მაკეტის ზუსტი პორტი).
   Needs: window.EXP (pts, towns), window.PLANNER_DATA (fleet, standardTours),
   window.DOAT (ლოკალიზებული ტექსტები), window.WX (ამინდი), Leaflet. */
(function () {
  var E = window.EXP, D = window.PLANNER_DATA, T = window.DOAT;
  if (!E || !D || !T || !window.L) return;
  var $ = function (id) { return document.getElementById(id); };
  if (!$('doa')) return;
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
  /* კალიბრებული სავალი დროის მოდელი — იგივე, რაც Trip Workspace-ში */
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
    return h && r ? h + ':' + (r < 10 ? '0' + r : r) : h ? h + ':00' : r + ' ' + T.minU;
  }
  function iso(d) { return d.toISOString().slice(0, 10); }

  /* ── state ─────────────────────────────────────────────────────────── */
  var origin0 = TOWNS.filter(function (t) { return t.s === 'town:tbilisi'; })[0] ||
    TOWNS.filter(function (t) { return t.k === 'city'; })[0] || TOWNS[0] || PTS[0];
  var st = {
    tab: 'home', bellOpen: false,
    origin: { n: origin0.n, la: origin0.la, lo: origin0.lo, f: origin0.f, v: origin0.v },
    originQuery: origin0.n, suggestOpen: false,
    start: iso(new Date(Date.now() + 6048e5)), end: iso(new Date(Date.now() + 7776e5)),
    days: 3, people: 2, transport: 'suggest', hours: 8,
    selected: [], visited: {}, placeQuery: '', minRating: 0, visitedFilter: '', fitsOnly: false,
    tourId: '', toursOpen: false, tourQuery: '', tourCar: '',
    detail: null, weather: true, routeLoading: false, routeError: false,
    bookingOpen: false, bookingDone: false, bkInvalid: false,
    joined: {}, tripMsg: '', savedCount: 0, toast: ''
  };
  try {
    var v0 = JSON.parse(localStorage.getItem('do-visited') || '{}');
    if (v0 && typeof v0 === 'object') st.visited = v0;
    var t0 = JSON.parse(localStorage.getItem('do-trips') || '[]');
    if (Object.prototype.toString.call(t0) === '[object Array]') st.savedCount = t0.length;
  } catch (e) {}
  var mh = location.hash.match(/#trip=([^&]+)/);
  if (mh) {
    try {
      var parts = decodeURIComponent(mh[1]).split(';');
      st.selected = parts[0].split(',').filter(function (s) { return BY[s]; });
      parts.slice(1).forEach(function (kv) {
        var i = kv.indexOf('=');
        if (i < 0) return;
        var k = kv.slice(0, i), v = kv.slice(i + 1);
        if (k === 's' && /^\d{4}-\d{2}-\d{2}$/.test(v)) st.start = v;
        if (k === 'd') st.days = Math.max(1, Math.min(14, parseInt(v, 10) || st.days));
      });
      var d0 = new Date(st.start);
      if (!isNaN(d0)) st.end = iso(new Date(d0.getTime() + (st.days - 1) * 864e5));
      if (st.selected.length) st.tab = 'route';
    } catch (e) {}
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
  function budgetMin() { return st.hours * Math.max(1, st.days) * 60; }
  function fits(p) {
    if (st.selected.indexOf(p.s) >= 0) return true;
    return p.hh * 60 + travel(lastPoint(), p) * 1.2 <= budgetMin() - usedMin() + 1;
  }
  function visible() {
    var q = st.placeQuery.trim().toLowerCase();
    return PTS.filter(function (p) {
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
    var seats = Math.min(8, st.people + (st.transport === 'driver' ? 1 : 0));
    var cand = D.fleet.filter(function (c) {
      if (c.seats < seats) return false;
      if (need4) return c.cat === 'offroad' || c.cat === 'suv' || c.cl >= 190;
      return true;
    });
    cand.sort(function (a, b) { return a.price - b.price; });
    return cand[0] || D.fleet[0];
  }
  function toggle(slug) {
    var i = st.selected.indexOf(slug);
    if (i >= 0) st.selected.splice(i, 1);
    else {
      var p = BY[slug];
      if (!p || !fits(p)) { flash(T.noTime); return; }
      st.selected.push(slug);
    }
    render();
  }
  function setVisited(slug) {
    if (st.visited[slug]) delete st.visited[slug]; else st.visited[slug] = 1;
    try { localStorage.setItem('do-visited', JSON.stringify(st.visited)); } catch (e) {}
    render();
  }
  var toastTimer = null;
  function flash(msg) {
    st.toast = msg;
    renderToast();
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { st.toast = ''; renderToast(); }, 2600);
  }

  /* ── map ──────────────────────────────────────────────────────────── */
  var GEO = null, map = null, markers = null, wxLayer = null, routeLayer = null;
  var wxCache = null, wxFor = '';
  function geoRing() {
    if (GEO) return GEO;
    GEO = [[41.107,43.44],[41.127,43.44],[41.156,43.433],[41.177,43.404],[41.191,43.361],[41.186,43.278],[41.199,43.206],[41.236,43.152],[41.265,43.141],[41.288,43.17],[41.307,43.148],[41.352,43.058],[41.467,42.907],[41.493,42.821],[41.564,42.788],[41.58,42.756],[41.587,42.684],[41.58,42.608],[41.571,42.59],[41.559,42.569],[41.47,42.507],[41.439,42.468],[41.455,42.363],[41.475,42.281],[41.486,42.212],[41.495,42.079],[41.496,41.924],[41.432,41.823],[41.441,41.78],[41.472,41.701],[41.498,41.575],[41.517,41.51],[41.705,41.701],[41.817,41.759],[41.885,41.762],[41.97,41.762],[42.147,41.665],[42.397,41.579],[42.659,41.489],[42.738,41.42],[42.828,41.129],[42.93,41.06],[43.064,40.837],[43.121,40.524],[43.146,40.463],[43.312,40.189],[43.42,39.977],[43.484,40.023],[43.553,40.085],[43.569,40.149],[43.543,40.344],[43.512,40.52],[43.534,40.65],[43.481,40.801],[43.418,40.941],[43.375,41.082],[43.333,41.359],[43.276,41.46],[43.218,41.582],[43.191,42.05],[43.199,42.086],[43.208,42.122],[43.229,42.281],[43.224,42.417],[43.156,42.565],[43.159,42.659],[43.17,42.759],[43.133,42.889],[43.092,42.99],[43.05,43.001],[42.989,43.091],[42.897,43.346],[42.845,43.559],[42.807,43.623],[42.746,43.782],[42.727,43.8],[42.703,43.796],[42.658,43.749],[42.618,43.739],[42.593,43.76],[42.571,43.825],[42.566,43.958],[42.595,44.005],[42.616,44.102],[42.654,44.199],[42.703,44.329],[42.748,44.505],[42.748,44.577],[42.734,44.646],[42.71,44.693],[42.616,44.772],[42.746,44.851],[42.757,44.873],[42.731,44.945],[42.694,45.071],[42.675,45.161],[42.649,45.207],[42.529,45.344],[42.536,45.564],[42.517,45.654],[42.498,45.704],[42.475,45.726],[42.357,45.69],[42.234,45.636],[42.205,45.639],[42.159,45.726],[42.109,45.845],[42.071,45.909],[42.036,45.953],[42.008,46.05],[41.993,46.161],[41.989,46.212],[41.96,46.269],[41.904,46.41],[41.89,46.431],[41.856,46.406],[41.79,46.349],[41.757,46.302],[41.752,46.251],[41.738,46.201],[41.703,46.183],[41.658,46.183],[41.625,46.19],[41.613,46.205],[41.602,46.255],[41.508,46.305],[41.46,46.385],[41.406,46.507],[41.344,46.619],[41.286,46.673],[41.246,46.662],[41.16,46.626],[41.088,46.536],[41.071,46.457],[41.076,46.431],[41.099,46.381],[41.154,46.28],[41.198,46.172],[41.184,46.086],[41.166,46.032],[41.187,45.92],[41.224,45.794],[41.262,45.726],[41.29,45.697],[41.338,45.715],[41.425,45.423],[41.449,45.279],[41.423,45.218],[41.291,45.002],[41.278,44.977],[41.26,44.811],[41.248,44.811],[41.22,44.847],[41.212,44.84],[41.208,44.563],[41.191,44.473],[41.213,44.228],[41.203,44.145],[41.182,44.077],[41.16,43.908],[41.132,43.793],[41.116,43.645],[41.116,43.49],[41.107,43.44]];
    return GEO;
  }
  function initMap() {
    if (map || !$('doamap')) return;
    map = L.map($('doamap'), { zoomControl: false, minZoom: 6, tap: true }).setView([42.05, 43.6], 7);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap, &copy; CARTO', maxZoom: 18, crossOrigin: true
    }).addTo(map);
    var ring = geoRing();
    L.polygon([[[85, -180], [85, 180], [-85, 180], [-85, -180]], ring], {
      stroke: false, fillColor: '#8a97a3', fillOpacity: 0.42, interactive: false
    }).addTo(map);
    L.polyline(ring, { color: '#0b2f4d', weight: 1.2, opacity: 0.5, interactive: false }).addTo(map);
    markers = L.layerGroup().addTo(map);
    wxLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    map.on('zoomend moveend', drawMarkers);
    setTimeout(function () { map.invalidateSize(); }, 120);
    drawMarkers();
    drawWeather();
    drawRoute();
  }
  function drawMarkers() {
    if (!markers) return;
    var z = map.getZoom(), list = visible();
    markers.clearLayers();
    var pts = list.map(function (p) { return { p: p, xy: map.latLngToLayerPoint([p.la, p.lo]) }; });
    var groups = [], rad = z >= 10 ? 0 : 48;
    pts.forEach(function (pt) {
      var g = null;
      for (var i = 0; i < groups.length; i++) if (groups[i].xy.distanceTo(pt.xy) < rad) { g = groups[i]; break; }
      if (g) g.items.push(pt.p); else groups.push({ xy: pt.xy, items: [pt.p] });
    });
    groups.forEach(function (g) {
      var first = g.items[0];
      if (g.items.length > 1) {
        var size = g.items.length > 9 ? 44 : 38;
        var mk = L.marker([first.la, first.lo], {
          icon: L.divIcon({ className: '', html: '<div class="do-cluster" style="width:' + size + 'px;height:' + size + 'px">' + g.items.length + '</div>', iconSize: [size, size], iconAnchor: [size / 2, size / 2] })
        });
        mk.on('click', function () { st.detail = g.items.map(function (x) { return x.s; }); renderDetail(); });
        markers.addLayer(mk);
      } else {
        var p = first, sel = st.selected.indexOf(p.s), vis = st.visited[p.s], ok = fits(p);
        var bg = sel >= 0 ? '#0d94ae' : vis ? '#7f8c99' : ok ? '#0b2f4d' : '#b9c6d1';
        var sz = sel >= 0 ? 30 : 24;
        var mk2 = L.marker([p.la, p.lo], {
          title: p.n,
          icon: L.divIcon({ className: '', html: '<div class="do-pin" style="width:' + sz + 'px;height:' + sz + 'px;background:' + bg + '">' + (sel >= 0 ? sel + 1 : '') + '</div>', iconSize: [sz, sz], iconAnchor: [sz / 2, sz / 2] })
        });
        mk2.on('click', function () { st.detail = [p.s]; renderDetail(); });
        markers.addLayer(mk2);
      }
    });
  }
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
  function paintWx(cents, w) {
    wxLayer.clearLayers();
    cents.forEach(function (c, i) {
      if (!w || !w[i]) return;
      var t = Math.round(w[i].tmax);
      wxLayer.addLayer(L.marker([c.la, c.lo], {
        interactive: false,
        icon: L.divIcon({ className: '', html: '<div style="background:rgba(255,255,255,.88);border:1px solid #dde5ec;border-radius:8px;padding:1px 6px;font-size:11px;color:#5a6b7b;white-space:nowrap">' + (t > 0 ? '+' : '') + t + '°</div>', iconSize: [null, 18] })
      }));
    });
  }
  function drawWeather() {
    if (!wxLayer) return;
    wxLayer.clearLayers();
    if (!st.weather || !window.WX || !WX.inRange(st.start)) return;
    var day = st.start, cents = regionCentroids();
    if (wxCache && wxFor === day) return paintWx(cents, wxCache);
    WX.get(cents.map(function (c) { return { la: c.la, lo: c.lo }; }), day).then(function (w) {
      wxCache = w; wxFor = day;
      if (st.weather && wxLayer) paintWx(cents, w);
    });
  }
  var reqToken = 0, fitNext = false;
  function drawRoute() {
    if (!routeLayer) return;
    routeLayer.clearLayers();
    var sel = st.selected.map(function (s) { return BY[s]; }).filter(Boolean);
    if (!sel.length) { st.routeLoading = false; st.routeError = false; renderStatus(); return; }
    var pts = [st.origin].concat(sel).concat([st.origin]);
    var straight = pts.map(function (p) { return [p.la, p.lo]; });
    L.polyline(straight, { color: '#0b2f4d', weight: 3, opacity: 0.32, dashArray: '6 6' }).addTo(routeLayer);
    st.routeLoading = true; st.routeError = false; renderStatus();
    var tok = ++reqToken;
    fetch('https://router.project-osrm.org/route/v1/driving/' +
      pts.map(function (p) { return p.lo + ',' + p.la; }).join(';') + '?overview=full&geometries=geojson')
      .then(function (r) { return r.json(); }).then(function (j) {
        if (tok !== reqToken) return;
        var g = j && j.routes && j.routes[0] && j.routes[0].geometry;
        if (!g) throw new Error('no geometry');
        routeLayer.clearLayers();
        var line = g.coordinates.map(function (c) { return [c[1], c[0]]; });
        L.polyline(line, { color: '#0b2f4d', weight: 5, opacity: 0.9 }).addTo(routeLayer);
        st.routeLoading = false; st.routeError = false; renderStatus();
        if (fitNext) { fitNext = false; map.fitBounds(L.latLngBounds(line).pad(0.15)); }
      }).catch(function () {
        if (tok !== reqToken) return;
        st.routeLoading = false; st.routeError = true; renderStatus();
        if (fitNext) { fitNext = false; map.fitBounds(L.latLngBounds(straight).pad(0.18)); }
      });
  }
  var routeKey = '';
  function syncMap() {
    if (!map) return;
    drawMarkers();
    drawWeather();
    var key = st.selected.join('>') + '|' + st.origin.n;
    if (key !== routeKey) { routeKey = key; drawRoute(); }
  }

  /* ── render ───────────────────────────────────────────────────────── */
  function show(id, on) { var el = $(id); if (el) el.hidden = !on; }
  function goTab(tab) {
    st.tab = tab;
    st.bellOpen = false;
    render();
    if (tab === 'map') { initMap(); setTimeout(function () { if (map) { map.invalidateSize(); syncMap(); } }, 140); }
  }
  function renderTabs() {
    ['home', 'map', 'route', 'community', 'account'].forEach(function (t) {
      var b = $('doatab-' + t);
      if (!b) return;
      var on = st.tab === t;
      b.setAttribute('aria-current', on ? 'page' : 'false');
      b.style.color = on ? '#0b2f4d' : '#8494a2';
    });
  }
  function renderMeter() {
    var used = usedMin(), budget = budgetMin(), remain = Math.max(0, budget - used);
    ['doabudget', 'doabudget2'].forEach(function (id) { var el = $(id); if (el) el.textContent = hm(budget); });
    ['doaused', 'doaused2'].forEach(function (id) { var el = $(id); if (el) el.textContent = hm(used); });
    ['doaleft', 'doaleft2'].forEach(function (id) { var el = $(id); if (el) el.textContent = hm(remain); });
  }
  function renderHome() {
    $('doaorigin').value = st.originQuery;
    $('doastart').value = st.start;
    $('doaend').value = st.end;
    $('doadays').textContent = Math.max(1, st.days) + ' ' + T.day;
    $('doapeople').textContent = String(st.people);
    $('doatransport').value = st.transport;
    $('doahours').textContent = st.hours + ' ' + T.hU;
    renderSuggest();
    renderMeter();
  }
  function renderSuggest() {
    var box = $('doasuggest');
    if (!box) return;
    if (!st.suggestOpen) { box.hidden = true; return; }
    var q = st.originQuery.trim().toLowerCase();
    var pool = TOWNS.map(function (t) { return { n: t.n, meta: '', la: t.la, lo: t.lo, f: t.f, v: t.v }; })
      .concat(PTS.map(function (p) { return { n: p.n, meta: p.gn, la: p.la, lo: p.lo, f: p.f, v: p.v, names: p.names }; }));
    var sug = (q ? pool.filter(function (x) {
      return (x.n + ' ' + (x.names || []).join(' ')).toLowerCase().indexOf(q) >= 0;
    }) : pool).slice(0, 7);
    box.innerHTML = '';
    sug.forEach(function (x) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'option');
      b.style.cssText = 'display:flex;width:100%;align-items:center;gap:8px;min-height:46px;padding:8px 10px;border:0;border-bottom:1px solid #f1f5f8;background:#fff;text-align:start;cursor:pointer';
      b.innerHTML = '<span style="font-size:14px;font-weight:600">' + esc(x.n) + '</span>' +
        '<span style="font-size:12px;color:#5a6b7b;margin-inline-start:auto">' + esc(x.meta) + '</span>';
      b.onclick = function () {
        st.origin = { n: x.n, la: x.la, lo: x.lo, f: x.f, v: x.v };
        st.originQuery = x.n; st.suggestOpen = false;
        fitNext = true;
        if (map) map.setView([x.la, x.lo], 8);
        routeKey = '';
        render();
      };
      box.appendChild(b);
    });
    box.hidden = sug.length === 0;
  }
  function renderList() {
    var list = visible(), box = $('doalist');
    var selMap = {};
    st.selected.forEach(function (s, i) { selMap[s] = i + 1; });
    /* ჩამქრალი (დროში ვერჩამტევი) ადგილები სიის ბოლოში */
    var fitCache = {};
    list.forEach(function (p) { fitCache[p.s] = selMap[p.s] ? 0 : (fits(p) ? 1 : 2); });
    list = list.slice().sort(function (a, b) {
      var d = fitCache[a.s] - fitCache[b.s];
      if (d) return d;
      if (fitCache[a.s] === 0) return selMap[a.s] - selMap[b.s];
      return 0;
    });
    $('doacount').textContent = list.length + ' ' + T.placesWord;
    $('doaselcount').textContent = st.selected.length + ' / ' + list.length;
    box.innerHTML = '';
    show('doaempty', list.length === 0);
    list.forEach(function (p) {
      var on = !!selMap[p.s], ok = fitCache[p.s] < 2, vis = !!st.visited[p.s];
      var tint = on ? '#cdeef4' : ok ? '#e8eff4' : '#eef1f4';
      var row = document.createElement('div');
      row.style.cssText = 'display:flex;gap:10px;align-items:center;padding:9px 12px;border-bottom:1px solid #f1f5f8;background:' + (on ? '#f4fcfd' : '#fff');
      row.innerHTML =
        '<button type="button" aria-pressed="' + on + '" style="flex:1;display:flex;gap:10px;align-items:center;min-height:48px;border:0;background:transparent;padding:0;text-align:start;min-width:0;cursor:pointer">' +
          '<span style="width:42px;height:42px;border-radius:10px;background:' + tint + ';color:#0b2f4d;font-size:13px;font-weight:700;display:grid;place-items:center;flex:0 0 auto">' + esc(on ? String(selMap[p.s]) : p.n.slice(0, 1)) + '</span>' +
          '<span style="display:flex;flex-direction:column;gap:2px;min-width:0">' +
            '<span style="font-size:14px;font-weight:600;color:' + (ok || on ? '#0e2333' : '#4d5b69') + '">' + esc(p.n) + '</span>' +
            '<span style="font-size:12px;color:' + (ok || on ? '#5a6b7b' : '#5f6d7a') + '">' +
              esc(hm(p.hh * 60) + ' · ' + Math.round(hav(st.origin.la, st.origin.lo, p.la, p.lo)) + ' ' + T.kmU + ' · ' + (p.r || 0).toFixed(1) + ' ★' + (vis ? ' · ' + T.visited : ok ? '' : ' · ' + T.noTime)) + '</span>' +
          '</span>' +
        '</button>' +
        '<button type="button" aria-label="' + esc(T.details) + '" style="width:44px;height:44px;border:1px solid #dde5ec;border-radius:10px;background:#fff;flex:0 0 auto;display:grid;place-items:center;cursor:pointer">' +
          '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0b2f4d" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 11v5M12 8h.01"></path></svg>' +
        '</button>';
      var btns = row.querySelectorAll('button');
      btns[0].onclick = function () { toggle(p.s); };
      btns[1].onclick = function () { st.detail = [p.s]; renderDetail(); };
      box.appendChild(row);
    });
    renderChips();
    renderSearchHits(list);
  }
  function renderChips() {
    var chips = [
      { label: '4+ ★', on: st.minRating === 4, act: function () { st.minRating = st.minRating === 4 ? 0 : 4; } },
      { label: '5 ★', on: st.minRating === 5, act: function () { st.minRating = st.minRating === 5 ? 0 : 5; } },
      { label: T.fitsL, on: st.fitsOnly, act: function () { st.fitsOnly = !st.fitsOnly; } },
      { label: T.visited, on: st.visitedFilter === 'yes', act: function () { st.visitedFilter = st.visitedFilter === 'yes' ? '' : 'yes'; } },
      { label: T.notVisited, on: st.visitedFilter === 'no', act: function () { st.visitedFilter = st.visitedFilter === 'no' ? '' : 'no'; } }
    ];
    var box = $('doachips');
    box.innerHTML = '';
    chips.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-pressed', String(c.on));
      b.style.cssText = 'height:36px;padding:0 12px;border:1px solid ' + (c.on ? '#0b2f4d' : '#dde5ec') + ';border-radius:999px;background:' + (c.on ? '#0b2f4d' : '#fff') + ';color:' + (c.on ? '#fff' : '#0e2333') + ';font-size:13px;font-weight:600;white-space:nowrap;cursor:pointer';
      b.textContent = c.label;
      b.onclick = function () { c.act(); render(); };
      box.appendChild(b);
    });
  }
  function renderSearchHits(list) {
    var pq = st.placeQuery.trim(), box = $('doahits');
    if (pq.length <= 1 || !list.length) { box.hidden = true; return; }
    box.hidden = false;
    box.innerHTML = '';
    list.slice(0, 8).forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.style.cssText = 'display:flex;width:100%;gap:10px;align-items:center;min-height:52px;padding:8px 10px;border:0;border-bottom:1px solid #f1f5f8;background:#fff;text-align:start;cursor:pointer';
      b.innerHTML =
        '<span style="width:34px;height:34px;border-radius:8px;background:#e8eff4;color:#0b2f4d;font-size:12px;font-weight:700;display:grid;place-items:center;flex:0 0 auto">' + esc(p.n.slice(0, 1)) + '</span>' +
        '<span style="display:flex;flex-direction:column;gap:2px;min-width:0">' +
          '<span style="font-size:14px;font-weight:600">' + esc(p.n) + '</span>' +
          '<span style="font-size:12px;color:#5a6b7b">' + esc(p.gn + ' · ' + (p.r || 0).toFixed(1) + ' ★') + '</span>' +
        '</span>';
      b.onclick = function () {
        if (map) map.setView([p.la, p.lo], 11);
        st.detail = [p.s]; st.placeQuery = '';
        $('doasearch').value = '';
        renderDetail(); renderList();
      };
      box.appendChild(b);
    });
  }
  function renderStatus() {
    show('doaloading', st.routeLoading);
    show('doarouteerr', st.routeError);
  }
  function renderRoute() {
    var box = $('doastops');
    box.innerHTML = '';
    var selPlaces = st.selected.map(function (s) { return BY[s]; }).filter(Boolean);
    show('doaroutempty', selPlaces.length === 0);
    show('doasavegrid', selPlaces.length > 0);
    var tour = (D.standardTours || []).filter(function (r) { return r.s === st.tourId; })[0];
    show('doatourchip', !!tour);
    if (tour) $('doatourname').textContent = tour.n + ' · ' + tour.days + ' ' + T.day;
    var prev = st.origin;
    selPlaces.forEach(function (p, i) {
      var lg = travel(prev, p);
      prev = p;
      var row = document.createElement('div');
      row.style.cssText = 'display:flex;gap:8px;align-items:center;padding:10px;background:#fff;border:1px solid #dde5ec;border-radius:14px';
      row.innerHTML =
        '<span style="width:26px;height:26px;border-radius:999px;background:#0b2f4d;color:#fff;font-size:12px;font-weight:700;display:grid;place-items:center;flex:0 0 auto">' + (i + 1) + '</span>' +
        '<span style="display:flex;flex-direction:column;gap:2px;flex:1;min-width:0">' +
          '<span style="font-size:14px;font-weight:600">' + esc(p.n) + '</span>' +
          '<span style="font-size:12px;color:#5a6b7b">' + esc(hm(lg)) + '</span>' +
        '</span>' +
        '<button type="button" aria-label="↑" style="width:40px;height:40px;border:1px solid #dde5ec;border-radius:10px;background:#fff;cursor:pointer">↑</button>' +
        '<button type="button" aria-label="↓" style="width:40px;height:40px;border:1px solid #dde5ec;border-radius:10px;background:#fff;cursor:pointer">↓</button>' +
        '<button type="button" aria-label="×" style="width:40px;height:40px;border:1px solid #dde5ec;border-radius:10px;background:#fff;cursor:pointer">×</button>';
      var bs = row.querySelectorAll('button');
      bs[0].onclick = function () { if (i > 0) { var s = st.selected; var x = s[i - 1]; s[i - 1] = s[i]; s[i] = x; render(); } };
      bs[1].onclick = function () { var s = st.selected; if (i < s.length - 1) { var x = s[i + 1]; s[i + 1] = s[i]; s[i] = x; render(); } };
      bs[2].onclick = function () { toggle(p.s); };
      box.appendChild(row);
    });
    var car = suggestCar();
    show('doacar', !!car);
    if (car) {
      var days = Math.max(1, st.days);
      $('doacarname').textContent = car.n;
      $('doacarprice').textContent = (days >= 7 ? car.price7 : car.price) * days + ' ₾';
      $('doacarspecs').textContent = car.cat_n + ' · ' + car.seats + ' ' + T.seats + ' · ' + car.cl + ' mm' + (car.fuel ? ' · ' + car.fuel + ' l/100' : '');
      $('doacartiers').textContent = car.price + ' ₾/' + T.day + ' · 7+: ' + car.price7 + ' ₾/' + T.day;
      $('doacarwhy').textContent = mountainRoute() ? T.carWhy4 : T.carWhyStd;
    }
    $('doatripmsg').textContent = st.tripMsg;
    renderMeter();
  }
  function renderDetail() {
    var openD = !!(st.detail && st.detail.length);
    show('doadetailwrap', openD);
    if (!openD) return;
    $('doadetailtitle').textContent = st.detail.length > 1 ? st.detail.length + ' ' + T.inGroup : T.placeDetails;
    var box = $('doadetailitems');
    box.innerHTML = '';
    st.detail.map(function (s) { return BY[s]; }).filter(Boolean).forEach(function (p) {
      var on = st.selected.indexOf(p.s) >= 0, ok = fits(p);
      var d = document.createElement('div');
      d.style.cssText = 'display:flex;flex-direction:column;gap:6px;padding:10px;border:1px solid #eef3f6;border-radius:12px';
      d.innerHTML =
        (p.img ? '<img src="' + esc(p.img) + '" alt="" loading="lazy" style="width:100%;height:130px;object-fit:cover;border-radius:10px">' : '') +
        '<span style="font-size:15px;font-weight:600">' + esc(p.n) + '</span>' +
        '<span style="font-size:13px;color:#5a6b7b">' + esc(p.gn + ' · ' + (p.r || 0).toFixed(1) + ' ★') + '</span>' +
        '<span style="font-size:13px;color:#5a6b7b">' + esc(hm(p.hh * 60) + ' · ' + Math.round(hav(st.origin.la, st.origin.lo, p.la, p.lo)) + ' ' + T.kmU) + '</span>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' +
          '<button type="button" style="min-height:46px;border:0;border-radius:10px;background:#0b2f4d;color:#fff;font-size:14px;font-weight:600;cursor:pointer">' + esc(on ? T.remove : ok ? T.add : T.noTime) + '</button>' +
          '<button type="button" style="min-height:46px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:14px;cursor:pointer">' + esc(st.visited[p.s] ? T.visited : T.visitedMark) + '</button>' +
        '</div>' +
        (p.u ? '<a href="' + esc(p.u) + '" target="_blank" rel="noopener" style="font-size:13px;color:#0b5f73;font-weight:600">' + esc(T.details) + ' ›</a>' : '');
      var bs = d.querySelectorAll('button');
      bs[0].onclick = function () { if (on || ok) { toggle(p.s); renderDetail(); } };
      bs[1].onclick = function () { setVisited(p.s); renderDetail(); };
      box.appendChild(d);
    });
  }
  function renderTours() {
    show('doatourswrap', st.toursOpen);
    if (!st.toursOpen) return;
    var tq = st.tourQuery.trim().toLowerCase();
    var tours = (D.standardTours || []).filter(function (r) {
      if (tq && (r.n + ' ' + (r.sh || '')).toLowerCase().indexOf(tq) < 0) return false;
      if (st.tourCar === 'offroad' && r.car !== '4x4') return false;
      if (st.tourCar === 'road' && r.car === '4x4') return false;
      return true;
    });
    var chipBox = $('doatourchips');
    chipBox.innerHTML = '';
    [['', T.all], ['road', T.stdCar], ['offroad', '4×4']].forEach(function (c) {
      var on = st.tourCar === c[0];
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-pressed', String(on));
      b.style.cssText = 'height:38px;padding:0 12px;border:1px solid ' + (on ? '#0b2f4d' : '#dde5ec') + ';border-radius:999px;background:' + (on ? '#0b2f4d' : '#fff') + ';color:' + (on ? '#fff' : '#0e2333') + ';font-size:13px;font-weight:600;white-space:nowrap;cursor:pointer';
      b.textContent = c[1];
      b.onclick = function () { st.tourCar = c[0]; renderTours(); };
      chipBox.appendChild(b);
    });
    var box = $('doatourlist');
    box.innerHTML = '';
    show('doatoursempty', tours.length === 0);
    tours.forEach(function (r) {
      var card = document.createElement('div');
      card.style.cssText = 'border:1px solid #dde5ec;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:6px';
      card.innerHTML =
        (r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy" style="width:100%;height:120px;object-fit:cover;border-radius:10px">' : '') +
        '<span style="font-size:15px;font-weight:700">' + esc(r.n) + '</span>' +
        '<span style="font-size:12px;color:#5a6b7b">' + esc(r.days + ' ' + T.day + ' · ' + r.km + ' ' + T.kmU + (r.drive ? ' · ' + r.drive : '')) + '</span>' +
        '<span style="font-size:12px;color:#5a6b7b">' + esc((r.carLabel || '') + ' · ' + r.minPeople + '–' + r.maxPeople + ' ' + T.people2) + '</span>' +
        '<span style="font-size:13px;color:#0e2333">' + esc(r.sh || '') + '</span>' +
        '<button type="button" style="height:48px;border:0;border-radius:12px;background:#0b2f4d;color:#fff;font-size:14px;font-weight:600;cursor:pointer">' + esc(T.chooseTour) + '</button>';
      card.querySelector('button').onclick = function () {
        st.tourId = r.s;
        st.selected = (r.wp || []).filter(function (s) { return BY[s]; });
        st.days = r.days;
        st.toursOpen = false;
        fitNext = true;
        routeKey = '';
        goTab('map');
      };
      box.appendChild(card);
    });
  }
  function renderCommunity() {
    var box = $('doacomm');
    if (!box || box.childNodes.length) return;
    var tours = D.standardTours || [];
    var samples = [
      { org: 'გიორგი ბ.', trips: 12, seats: 2, pub: true },
      { org: 'ანა მ.', trips: 7, seats: 3, pub: true },
      { org: 'ლევან ქ.', trips: 21, seats: 1, pub: true },
      { org: 'ნინო კ.', trips: 4, seats: 0, pub: false }
    ];
    samples.forEach(function (c, i) {
      var r = tours[i % Math.max(1, tours.length)];
      if (!r) return;
      var card = document.createElement('div');
      card.style.cssText = 'padding:12px;background:#fff;border:1px solid #dde5ec;border-radius:14px;display:flex;flex-direction:column;gap:6px';
      card.innerHTML =
        '<div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline">' +
          '<span style="font-size:15px;font-weight:700">' + esc(r.n) + '</span>' +
          '<span style="font-size:12px;font-weight:600;color:' + (c.pub ? '#0b5f73' : '#5a6b7b') + '">' + esc(c.pub ? T.pub : T.priv) + '</span>' +
        '</div>' +
        '<span style="font-size:12px;color:#5a6b7b">' + esc(r.days + ' ' + T.day + ' · ' + (r.carLabel || '') + ' · ' + r.km + ' ' + T.kmU) + '</span>' +
        '<span style="font-size:12px;color:#5a6b7b">' + esc(c.org + ' · ' + c.trips + ' ' + T.tripsWord + (c.seats ? ' · ' + c.seats + ' ' + T.freeSeats : ' · ' + T.noSeats)) + '</span>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:2px">' +
          '<button type="button" style="height:46px;border:0;border-radius:10px;background:#0d94ae;color:#fff;font-size:14px;font-weight:600;cursor:pointer">' + esc(T.join) + '</button>' +
          '<button type="button" style="height:46px;border:1px solid #dde5ec;border-radius:10px;background:#fff;font-size:14px;cursor:pointer">' + esc(T.share) + '</button>' +
        '</div>';
      var bs = card.querySelectorAll('button');
      bs[0].onclick = function () {
        st.joined[r.s] = !st.joined[r.s];
        bs[0].textContent = st.joined[r.s] ? T.joined : T.join;
        if (st.joined[r.s]) flash(T.joined);
        renderAccount();
      };
      bs[1].onclick = function () {
        var url = location.origin + (r.u || '');
        if (navigator.share) navigator.share({ title: r.n, text: r.sh || r.n, url: url }).catch(function () {});
        else if (navigator.clipboard) { navigator.clipboard.writeText(url).catch(function () {}); flash(T.copied); }
      };
      box.appendChild(card);
    });
  }
  var cloudCountFetched = false;
  function renderAccount() {
    if (st.tab === 'account' && !cloudCountFetched && cloudMode()) {
      cloudCountFetched = true;
      window.FH.listTrips().then(function (list) {
        if (list && list.length !== undefined) {
          st.savedCount = list.length;
          var el = $('doaacc-saved');
          if (el) el.textContent = String(list.length);
        }
      }).catch(function () {});
    }
    var vals = {
      'doaacc-planned': String(st.selected.length ? 1 : 0),
      'doaacc-saved': String(st.savedCount),
      'doaacc-visited': String(Object.keys(st.visited).length),
      'doaacc-groups': String(Object.keys(st.joined).filter(function (k) { return st.joined[k]; }).length),
      'doaacc-cars': (function () { try { return localStorage.getItem('do-bk-sent') || '0'; } catch (e) { return '0'; } })()
    };
    Object.keys(vals).forEach(function (id) { var el = $(id); if (el) el.textContent = vals[id]; });
  }
  function renderToast() {
    var el = $('doatoast');
    el.hidden = !st.toast;
    el.textContent = st.toast;
  }
  function renderViews() {
    show('doav-home', st.tab === 'home');
    show('doav-map', st.tab === 'map');
    show('doav-route', st.tab === 'route');
    show('doav-community', st.tab === 'community');
    show('doav-account', st.tab === 'account');
    show('doabell', st.bellOpen);
  }
  function render() {
    renderViews();
    renderTabs();
    renderHome();
    renderList();
    renderRoute();
    renderCommunity();
    renderAccount();
    renderTours();
    syncMap();
  }

  /* ── wiring ───────────────────────────────────────────────────────── */
  ['home', 'map', 'route', 'community', 'account'].forEach(function (t) {
    $('doatab-' + t).onclick = function () { goTab(t); };
  });
  $('doabellbtn').onclick = function () { st.bellOpen = !st.bellOpen; renderViews(); };
  $('doabellclose').onclick = function () { st.bellOpen = false; renderViews(); };
  $('doalang').onchange = function () {
    var u = (T.langUrls || {})[this.value];
    if (u) location.href = u + location.hash;
  };
  $('doaorigin').oninput = function () { st.originQuery = this.value; st.suggestOpen = true; renderSuggest(); };
  $('doaorigin').onfocus = function () { st.suggestOpen = true; renderSuggest(); };
  document.addEventListener('click', function (e) {
    if (!e.target.closest('#doasuggest') && e.target !== $('doaorigin') && st.suggestOpen) {
      st.suggestOpen = false; renderSuggest();
    }
  });
  $('doamyloc').onclick = function () {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(function (pos) {
      st.origin = { n: T.myLoc, la: pos.coords.latitude, lo: pos.coords.longitude, f: 1.4, v: 55 };
      st.originQuery = T.myLoc; st.suggestOpen = false;
      if (map) map.setView([pos.coords.latitude, pos.coords.longitude], 9);
      routeKey = '';
      render();
    }, function () {});
  };
  $('doastart').onchange = function () {
    var v = this.value, d = new Date(v);
    if (!isNaN(d)) { st.start = v; st.end = iso(new Date(d.getTime() + (Math.max(1, st.days) - 1) * 864e5)); }
    wxCache = null;
    render();
  };
  $('doaend').onchange = function () {
    var v = this.value, a = new Date(st.start), b = new Date(v);
    if (!isNaN(b)) { st.end = v; st.days = Math.max(1, Math.round((b - a) / 864e5) + 1); }
    render();
  };
  $('doadaysdown').onclick = function () { st.days = Math.max(1, st.days - 1); st.end = iso(new Date(new Date(st.start).getTime() + (st.days - 1) * 864e5)); render(); };
  $('doadaysup').onclick = function () { st.days = Math.min(14, st.days + 1); st.end = iso(new Date(new Date(st.start).getTime() + (st.days - 1) * 864e5)); render(); };
  $('doapeopledown').onclick = function () { st.people = Math.max(1, st.people - 1); render(); };
  $('doapeopleup').onclick = function () { st.people = Math.min(12, st.people + 1); render(); };
  $('doatransport').onchange = function () { st.transport = this.value; render(); };
  $('doahoursdown').onclick = function () { st.hours = Math.max(1, st.hours - 0.5); render(); };
  $('doahoursup').onclick = function () { st.hours = Math.min(14, st.hours + 0.5); render(); };
  $('doaplan').onclick = function () { goTab('map'); };
  $('doatoursbtn').onclick = function () { st.toursOpen = true; renderTours(); };
  $('doatoursclose').onclick = function () { st.toursOpen = false; renderTours(); };
  $('doatoursearch').oninput = function () { st.tourQuery = this.value; renderTours(); };
  $('doasearch').oninput = function () { st.placeQuery = this.value; renderList(); if (map) drawMarkers(); };
  $('doawx').onclick = function () {
    st.weather = !st.weather;
    this.style.background = st.weather ? '#e6f6f9' : '#fff';
    this.setAttribute('aria-pressed', String(st.weather));
    drawWeather();
  };
  $('doaresetf').onclick = function () {
    st.minRating = 0; st.visitedFilter = ''; st.fitsOnly = false; st.placeQuery = '';
    $('doasearch').value = '';
    render();
  };
  $('doadetailclose').onclick = function () { st.detail = null; renderDetail(); };
  $('doadetailbg').onclick = function () { st.detail = null; renderDetail(); };
  $('doacleartour').onclick = function () { st.tourId = ''; st.selected = []; render(); };
  $('doaroutemap').onclick = function () { goTab('map'); };

  function tripName() {
    var tour = (D.standardTours || []).filter(function (r) { return r.s === st.tourId; })[0];
    return tour ? tour.n : st.origin.n;
  }
  function shareUrl() {
    return location.href.split('#')[0] + '#trip=' + encodeURIComponent(
      st.selected.join(',') + ';o=' + st.origin.n + ';s=' + st.start + ';d=' + st.days);
  }
  /* შენახვა — ანგარიშზე (Firebase). შეუსვლელს ლოგინის ფანჯარა უხტება;
     შესვლისთანავე დაწყებული შენახვა თავად სრულდება. */
  function cloudMode() { return !!(window.FH && !window.FH.local && window.FH.saveTrip); }
  var pendingSave = null, retryReg = false;
  function savedOk() {
    st.tripMsg = T.saved;
    flash(T.saved);
    renderRoute(); renderAccount();
    setTimeout(function () { st.tripMsg = ''; var el = $('doatripmsg'); if (el) el.textContent = ''; }, 2500);
  }
  function regSaveRetry() {
    if (retryReg || !window.FH || !window.FH.on) return;
    retryReg = true;
    window.FH.on(function (u) {
      if (u && pendingSave) { var p = pendingSave; pendingSave = null; cloudSave(p); }
    });
  }
  function cloudSave(payload) {
    window.FH.saveTrip(payload).then(function () { st.savedCount += 1; savedOk(); }).catch(function (e) {
      if (e === 'no-user') { pendingSave = payload; regSaveRetry(); flash(T.signinToSave); }
      else flash(T.saveErr);
    });
  }
  $('doasave').onclick = function () {
    var payload = { title: tripName(), date: st.start, days: Math.max(1, st.days),
      stops: st.selected.map(function (s) { return { n: (BY[s] || {}).n || s }; }), url: shareUrl() };
    if (cloudMode()) { cloudSave(payload); return; }
    var saved = [];
    try { saved = JSON.parse(localStorage.getItem('do-trips') || '[]'); } catch (e) { saved = []; }
    saved.push({ name: tripName(), start: st.start, end: st.end, stops: st.selected.slice() });
    try { localStorage.setItem('do-trips', JSON.stringify(saved)); } catch (e) {}
    st.savedCount = saved.length;
    savedOk();
  };
  $('doashare').onclick = function () {
    var text = tripName() + ' · ' + st.start + ' – ' + st.end + ' · ' + st.selected.length;
    var url = shareUrl();
    if (navigator.share) navigator.share({ title: 'Drive On', text: text, url: url }).catch(function () {});
    else if (navigator.clipboard) {
      navigator.clipboard.writeText(text + ' — ' + url).catch(function () {});
      st.tripMsg = T.copied;
      $('doatripmsg').textContent = T.copied;
      setTimeout(function () { st.tripMsg = ''; var el = $('doatripmsg'); if (el) el.textContent = ''; }, 2500);
    }
  };

  /* booking */
  try {
    $('doabkname').value = localStorage.getItem('do-bk-name') || '';
    $('doabkphone').value = localStorage.getItem('do-bk-phone') || '';
  } catch (e) {}
  function bookingSummary() {
    var car = suggestCar();
    return (car ? car.n + ' · ' : '') + st.start + ' – ' + st.end + ' · ' + Math.max(1, st.days) + ' ' + T.day + ' · ' + st.people + ' · ' + st.selected.length;
  }
  $('doabook').onclick = function () {
    st.bookingOpen = true; st.bookingDone = false; st.bkInvalid = false;
    show('doabookingwrap', true);
    show('doabkdone', false);
    show('doabkform', true);
    show('doabkinvalid', false);
    show('doabkerr', false);
    $('doabksum').textContent = bookingSummary();
  };
  $('doabkclose').onclick = function () { st.bookingOpen = false; show('doabookingwrap', false); };
  $('doabksend').onclick = function () {
    var btn = this;
    var name = $('doabkname').value.trim(), phone = $('doabkphone').value.trim();
    if (!name || !phone) { show('doabkinvalid', true); return; }
    show('doabkinvalid', false);
    show('doabkerr', false);
    try {
      localStorage.setItem('do-bk-name', name);
      localStorage.setItem('do-bk-phone', phone);
    } catch (e) {}
    var car = suggestCar();
    var tSel = $('doatransport');
    var tName = tSel.options[tSel.selectedIndex] ? tSel.options[tSel.selectedIndex].text : '';
    var body = new URLSearchParams({
      'form-name': 'contact', name: name, email: '',
      dates: st.start + ' – ' + st.end,
      message: 'Mobile App: ' + (car ? car.n : '') + ' · ' + phone + ' · ' + st.people + ' ppl · ' + tName + ' · ' +
        st.selected.map(function (s) { return (BY[s] || {}).n || s; }).join(', ') + ' · ' + shareUrl()
    }).toString();
    var origin = /netlify\.app$/.test(location.hostname) ? '' : 'https://subtle-naiad-c2db5d.netlify.app';
    btn.disabled = true;
    var old = btn.textContent;
    btn.textContent = T.sending;
    fetch(origin + '/', { method: 'POST', mode: origin ? 'no-cors' : 'same-origin',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body })
      .then(function () {
        show('doabkform', false);
        show('doabkdone', true);
        $('doabksum2').textContent = bookingSummary();
        try {
          var n = parseInt(localStorage.getItem('do-bk-sent') || '0', 10) + 1;
          localStorage.setItem('do-bk-sent', String(n));
        } catch (e) {}
        renderAccount();
      })
      .catch(function () { show('doabkerr', true); })
      .then(function () { btn.disabled = false; btn.textContent = old; });
  };
  $('doainstall').onclick = function () {
    if (window.FH_INSTALL_APP) {
      window.FH_INSTALL_APP().then(function (ok) { if (!ok) flash(T.installHint); });
    } else flash(T.installHint);
  };

  window.DOA_GO = function (k) {
    if (k === 'visited') { st.visitedFilter = 'yes'; goTab('map'); }
    else if (k === 'saved' && cloudMode() && T.accountUrl) location.href = T.accountUrl;
    else if (k === 'saved') goTab('route');
    else goTab(k);
  };

  render();
})();
