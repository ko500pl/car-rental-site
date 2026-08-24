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

  /* Regional enrichment. The initial asset contains only the country-wide
     routing/search index; richer card data is merged in-place on demand. */
  var chunkManifest = E.chunks || {}, chunkLoaded = {}, chunkPending = {};
  var chunkAbort = null, chunkRequest = 0, chunkTimer = 0;
  function mergeChunk(data) {
    (data && data.pts || []).forEach(function (rich) {
      if (BY[rich.s]) Object.assign(BY[rich.s], rich);
      else { BY[rich.s] = rich; PTS.push(rich); }
    });
  }
  function cachedChunk(key) {
    try { return JSON.parse(localStorage.getItem('do-map-chunk:' + key) || 'null'); }
    catch (e) { return null; }
  }
  function fetchChunk(region, signal) {
    if (!region || !chunkManifest[region] || chunkLoaded[region]) return Promise.resolve();
    var pending = chunkPending[region];
    if (pending && (!pending.signal || !pending.signal.aborted)) return pending.promise;
    var spec = chunkManifest[region], cacheKey = spec.url;
    var promise = fetch(spec.url, { signal: signal, credentials: 'same-origin' })
      .then(function (res) { if (!res.ok) throw new Error('chunk ' + res.status); return res.json(); })
      .then(function (data) {
        if (signal && signal.aborted) return;
        mergeChunk(data); chunkLoaded[region] = true;
        try { localStorage.setItem('do-map-chunk:' + cacheKey, JSON.stringify(data)); } catch (e) {}
      })
      .catch(function (err) {
        if (err && err.name === 'AbortError') throw err;
        var offline = cachedChunk(cacheKey);
        if (offline) { mergeChunk(offline); chunkLoaded[region] = true; }
      })
      .finally(function () {
        if (chunkPending[region] && chunkPending[region].promise === promise) delete chunkPending[region];
      });
    chunkPending[region] = { promise: promise, signal: signal };
    return promise;
  }
  function ensurePointRegions(points) {
    var regions = {};
    (points || []).forEach(function (p) { if (p && p.g) regions[p.g] = 1; });
    return Promise.all(Object.keys(regions).map(function (region) { return fetchChunk(region); }))
      .then(function () { render(); });
  }

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
    ret: 'back', stay: null, carOverride: '',
    tab: 'map'
  };
  try { var v0 = JSON.parse(localStorage.getItem('do-visited') || '{}'); if (v0 && typeof v0 === 'object') st.visited = v0; } catch (e) {}
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
        if (k === 'd') st.days = Math.max(1, Math.min(30, parseInt(v, 10) || st.days));
        if (k === 'o') st._originName = v;
      });
      var d0 = new Date(st.start);
      if (!isNaN(d0)) st.end = iso(new Date(d0.getTime() + (st.days - 1) * 864e5));
    } catch (e) {}
  }

  /* ── engine ───────────────────────────────────────────────────────── */
  function lastPoint() {
    if (!st.selected.length) return st.origin;
    return BY[st.selected[st.selected.length - 1]] || st.origin;
  }
  function travel(a, b) { return leg(a, b).min; }
  function endPoint() {
    if (st.ret === 'back') return st.origin;
    if (st.ret === 'other' && st.stay) return st.stay;
    return null; /* ვრჩები ბოლო გაჩერებაზე */
  }
  function usedMin() {
    var t = 0, prev = st.origin;
    st.selected.forEach(function (s) { var p = BY[s]; if (!p) return; t += travel(prev, p) + p.hh * 60; prev = p; });
    var ep = endPoint();
    if (st.selected.length && ep) t += travel(prev, ep);
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
    if (st.carOverride) {
      var o = D.fleet.filter(function (c) { return c.s === st.carOverride; })[0];
      if (o) return o;
    }
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

  /* ── map ──────────────────────────────────────────────────────────── */
  var GEO = [[41.107,43.44],[41.127,43.44],[41.156,43.433],[41.177,43.404],[41.191,43.361],[41.186,43.278],[41.199,43.206],[41.236,43.152],[41.265,43.141],[41.288,43.17],[41.307,43.148],[41.352,43.058],[41.467,42.907],[41.493,42.821],[41.564,42.788],[41.58,42.756],[41.587,42.684],[41.58,42.608],[41.571,42.59],[41.559,42.569],[41.47,42.507],[41.439,42.468],[41.455,42.363],[41.475,42.281],[41.486,42.212],[41.495,42.079],[41.496,41.924],[41.432,41.823],[41.441,41.78],[41.472,41.701],[41.498,41.575],[41.517,41.51],[41.705,41.701],[41.817,41.759],[41.885,41.762],[41.97,41.762],[42.147,41.665],[42.397,41.579],[42.659,41.489],[42.738,41.42],[42.828,41.129],[42.93,41.06],[43.064,40.837],[43.121,40.524],[43.146,40.463],[43.312,40.189],[43.42,39.977],[43.484,40.023],[43.553,40.085],[43.569,40.149],[43.543,40.344],[43.512,40.52],[43.534,40.65],[43.481,40.801],[43.418,40.941],[43.375,41.082],[43.333,41.359],[43.276,41.46],[43.218,41.582],[43.191,42.05],[43.199,42.086],[43.208,42.122],[43.229,42.281],[43.224,42.417],[43.156,42.565],[43.159,42.659],[43.17,42.759],[43.133,42.889],[43.092,42.99],[43.05,43.001],[42.989,43.091],[42.897,43.346],[42.845,43.559],[42.807,43.623],[42.746,43.782],[42.727,43.8],[42.703,43.796],[42.658,43.749],[42.618,43.739],[42.593,43.76],[42.571,43.825],[42.566,43.958],[42.595,44.005],[42.616,44.102],[42.654,44.199],[42.703,44.329],[42.748,44.505],[42.748,44.577],[42.734,44.646],[42.71,44.693],[42.616,44.772],[42.746,44.851],[42.757,44.873],[42.731,44.945],[42.694,45.071],[42.675,45.161],[42.649,45.207],[42.529,45.344],[42.536,45.564],[42.517,45.654],[42.498,45.704],[42.475,45.726],[42.357,45.69],[42.234,45.636],[42.205,45.639],[42.159,45.726],[42.109,45.845],[42.071,45.909],[42.036,45.953],[42.008,46.05],[41.993,46.161],[41.989,46.212],[41.96,46.269],[41.904,46.41],[41.89,46.431],[41.856,46.406],[41.79,46.349],[41.757,46.302],[41.752,46.251],[41.738,46.201],[41.703,46.183],[41.658,46.183],[41.625,46.19],[41.613,46.205],[41.602,46.255],[41.508,46.305],[41.46,46.385],[41.406,46.507],[41.344,46.619],[41.286,46.673],[41.246,46.662],[41.16,46.626],[41.088,46.536],[41.071,46.457],[41.076,46.431],[41.099,46.381],[41.154,46.28],[41.198,46.172],[41.184,46.086],[41.166,46.032],[41.187,45.92],[41.224,45.794],[41.262,45.726],[41.29,45.697],[41.338,45.715],[41.425,45.423],[41.449,45.279],[41.423,45.218],[41.291,45.002],[41.278,44.977],[41.26,44.811],[41.248,44.811],[41.22,44.847],[41.212,44.84],[41.208,44.563],[41.191,44.473],[41.213,44.228],[41.203,44.145],[41.182,44.077],[41.16,43.908],[41.132,43.793],[41.116,43.645],[41.116,43.49],[41.107,43.44]];
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
  map.on('zoomend moveend', function () { drawMarkers(); scheduleViewportChunks(); });

  function boundsOverlap(a, b) {
    return a[2] >= b.getSouth() && a[0] <= b.getNorth() &&
      a[3] >= b.getWest() && a[1] <= b.getEast();
  }
  function scheduleViewportChunks() {
    clearTimeout(chunkTimer);
    if (map.getZoom() < 8) return;
    chunkTimer = setTimeout(function () {
      var bounds = map.getBounds();
      var regions = Object.keys(chunkManifest).filter(function (region) {
        return !chunkLoaded[region] && boundsOverlap(chunkManifest[region].bounds, bounds);
      });
      if (!regions.length) return;
      if (chunkAbort) chunkAbort.abort();
      chunkAbort = window.AbortController ? new AbortController() : null;
      var signal = chunkAbort ? chunkAbort.signal : undefined;
      var request = ++chunkRequest;
      Promise.all(regions.map(function (region) { return fetchChunk(region, signal); }))
        .then(function () {
          if (request !== chunkRequest || (signal && signal.aborted)) return;
          render();
        }).catch(function (err) {
          if (!err || err.name !== 'AbortError') return;
        });
    }, 180);
  }

  function drawMarkers() {
    var z = map.getZoom(), list = visible();
    if (z >= 8) {
      var viewport = map.getBounds().pad(0.18);
      list = list.filter(function (p) { return viewport.contains([p.la, p.lo]); });
    }
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
            if (clicks === 1) {
              st.detail = g.items.map(function (x) { return x.s; });
              render(); ensurePointRegions(g.items);
            }
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
        mk1.on('click', function () { st.detail = [p.s]; render(); ensurePointRegions([p]); });
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
    /* ამინდი მხოლოდ არჩეული თარიღით — თუ პროგნოზის ფარგლებს გარეთაა, არ ვაჩვენებთ */
    if (!WX.inRange(st.start)) return;
    var day = st.start;
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
    var ep = endPoint();
    var pts = [st.origin].concat(sel).concat(ep ? [ep] : []);
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
    var ep = endPoint();
    var key = st.selected.join('>') + '|' + st.origin.n + '|' + (st.traffic ? 't' : '') +
      '|' + st.ret + '|' + (ep ? ep.n : '');
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
      else if (p) {
        var short = cost(p) - (budgetMin() - usedMin());
        flash(T.noFitNeed + ' ~' + hm(short), true);
      }
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

  /* ── მარშრუტის ხანგრძლივობა და უმოკლეს დროზე გადალაგება ───────────
     ვითვლით იმავე კალიბრებული leg()-ით, რითიც მრიცხველი მუშაობს:
     საწყისი → გაჩერებები (დათვალიერების დროებით) → დაბრუნება.       */
  function orderMin(order) {
    var t = 0, prev = st.origin;
    order.forEach(function (s) {
      var p = BY[s]; if (!p) return;
      t += travel(prev, p) + p.hh * 60; prev = p;
    });
    var ep = endPoint();
    if (order.length && ep) t += travel(prev, ep);
    return t;
  }
  /* ── გადახვევა: რამდენად აგრძელებს ადგილი უკვე აგებულ გზას ──────────
     ვიანგარიშებთ ყველაზე იაფ ჩასმას მარშრუტის ნებისმიერ მონაკვეთში:
     (a→p) + (p→b) − (a→b). სიაში ჯერ ყველაზე მცირე გადახვევიანები.  */
  function detour(p) {
    /* გეომეტრიული მანძილი (გზის კოეფიციენტის გარეშე) — სამკუთხედის
       წესით ყოველთვის ≥ 0, ამიტომ სიაში რიცხვები ერთმანეთს ეწყობა. */
    function dist(a, b) { return hav(a.la, a.lo, b.la, b.lo); }
    var seq = [st.origin];
    st.selected.forEach(function (s) { var x = BY[s]; if (x) seq.push(x); });
    var ep = endPoint();
    if (ep) seq.push(ep);
    if (seq.length < 2) return { km: dist(st.origin, p), min: leg(st.origin, p).min };
    var best = null;
    for (var i = 0; i < seq.length - 1; i++) {
      var a = seq[i], b = seq[i + 1];
      var extra = dist(a, p) + dist(p, b) - dist(a, b);
      if (!best || extra < best.km) {
        best = { km: Math.max(0, extra),
                 min: Math.max(0, leg(a, p).min + leg(p, b).min - leg(a, b).min) };
      }
    }
    if (!ep) { /* ბოლო გაჩერებაზე რჩება — ბოლოში მიბმაც შესაძლებელია */
      var last = seq[seq.length - 1], e2 = dist(last, p);
      if (!best || e2 < best.km) best = { km: e2, min: leg(last, p).min };
    }
    return best;
  }

  function optimizeOrder(order) {
    if (order.length < 3) return order.slice();
    /* 1) უახლოესი მეზობელი საწყისიდან */
    var left = order.slice(), out = [], cur = st.origin;
    while (left.length) {
      var bi = 0, bv = Infinity;
      for (var i = 0; i < left.length; i++) {
        var p = BY[left[i]]; if (!p) continue;
        var v = travel(cur, p);
        if (v < bv) { bv = v; bi = i; }
      }
      out.push(left[bi]);
      cur = BY[left[bi]] || cur;
      left.splice(bi, 1);
    }
    /* 2) 2-opt — გადაკვეთილი მონაკვეთების გასწორება */
    var best = orderMin(out), improved = true, guard = 0;
    while (improved && guard++ < 60) {
      improved = false;
      for (var a = 0; a < out.length - 1; a++) {
        for (var b = a + 1; b < out.length; b++) {
          var cand = out.slice(0, a).concat(out.slice(a, b + 1).reverse(), out.slice(b + 1));
          var v2 = orderMin(cand);
          if (v2 < best - 0.5) { out = cand; best = v2; improved = true; }
        }
      }
    }
    return out;
  }
  function setDays(n) {
    st.days = Math.max(1, Math.min(30, n));
    var d = new Date(st.start);
    if (!isNaN(d)) st.end = iso(new Date(d.getTime() + (st.days - 1) * 864e5));
    while (st.dayHours.length < st.days) st.dayHours.push(8);
    render();
  }
  function flash(msg, warn, undoFn) {
    var el = $('dowmsg');
    el.innerHTML = '';
    el.appendChild(document.createTextNode(msg));
    el.classList.toggle('warn', !!warn);
    if (undoFn) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'dow-undo';
      b.textContent = T.undo;
      b.onclick = function () { undoFn(); el.innerHTML = ''; };
      el.appendChild(b);
    }
    $('dowactions').hidden = false;
    clearTimeout(flash._t);
    flash._t = setTimeout(function () { el.innerHTML = ''; el.classList.remove('warn'); }, warn || undoFn ? 6000 : 3200);
  }

  /* ── არჩეული გაჩერებების გადათრევა სიაში ──────────────────────────
     მუშაობს მაუსითაც და თითითაც. გადათრევისას მხოლოდ DOM მოძრაობს —
     ხელის აშვებისას ერთხელ ვამატებთ ახალ რიგს და ვხატავთ ხელახლა.  */
  function attachDrag(row) {
    var handle = row.querySelector('.dow-grab');
    if (!handle) return;
    handle.style.touchAction = 'none';
    handle.addEventListener('pointerdown', function (ev) {
      if (ev.button != null && ev.button !== 0) return;
      ev.preventDefault();
      var lb = row.parentNode;
      if (!lb) return;
      var startY = ev.clientY;
      var moved = false;
      row.classList.add('dragging');
      try { handle.setPointerCapture(ev.pointerId); } catch (e) {}

      function rows() {
        return Array.prototype.filter.call(lb.children, function (el) {
          return el.classList.contains('drag');
        });
      }
      function move(e) {
        if (!moved && Math.abs(e.clientY - startY) < 4) return;
        moved = true;
        var y = e.clientY;
        var list = rows();
        for (var i = 0; i < list.length; i++) {
          var el = list[i];
          if (el === row) continue;
          var r = el.getBoundingClientRect();
          var mid = r.top + r.height / 2;
          if (y < mid && el.compareDocumentPosition(row) & Node.DOCUMENT_POSITION_FOLLOWING) {
            lb.insertBefore(row, el); return;
          }
          if (y > mid && el.compareDocumentPosition(row) & Node.DOCUMENT_POSITION_PRECEDING) {
            lb.insertBefore(row, el.nextSibling); return;
          }
        }
      }
      function up() {
        handle.removeEventListener('pointermove', move);
        handle.removeEventListener('pointerup', up);
        handle.removeEventListener('pointercancel', up);
        row.classList.remove('dragging');
        if (!moved) return;
        var order = rows().map(function (el) { return el.dataset.slug; })
          .filter(function (s) { return s && st.selected.indexOf(s) >= 0; });
        if (order.length === st.selected.length) st.selected = order;
        routeKey = '';
        render();
      }
      handle.addEventListener('pointermove', move);
      handle.addEventListener('pointerup', up);
      handle.addEventListener('pointercancel', up);
    });
  }

  /* ── render ───────────────────────────────────────────────────────── */
  var typeName = {}; (E.pts || []).forEach(function (p) { typeName[p.ty] = p.t; });

  /* კომპაქტური ფილტრები: 3 ჩიპი — შეფასების ციკლი, ნამყოფის ციკლი, „ეტევა დროში" */
  function chipsSpec() {
    var rLabel = st.minRating ? '★ ' + st.minRating + (st.minRating < 5 ? '+' : '') : T.ratingAll;
    var vLabel = st.visitedFilter === 'no' ? T.notVisited :
      st.visitedFilter === 'yes' ? T.visited : T.visited + ' ✓✗';
    return [
      { label: rLabel, on: !!st.minRating, act: function () {
        st.minRating = st.minRating === 0 ? 3 : st.minRating === 3 ? 4 : st.minRating === 4 ? 5 : 0;
      } },
      { label: vLabel, on: !!st.visitedFilter, act: function () {
        st.visitedFilter = st.visitedFilter === '' ? 'no' : st.visitedFilter === 'no' ? 'yes' : '';
      } },
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
    var mpc = Math.min(100, Math.round(used / Math.max(1, budget) * 100));
    var meterEl = $('dowmeter');
    meterEl.style.width = mpc + '%';
    meterEl.className = mpc >= 100 ? 'full' : (mpc > 85 ? 'high' : '');
    $('dowmeterhint').textContent = st.selected.length ? '' : T.meterHint;
    $('dowstart').min = iso(new Date());
    $('dowend').min = st.start || '';
    $('dowstay').hidden = st.ret !== 'other';

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
    $('dowactions').hidden = !(st.selected.length || $('dowmsg').textContent);
    $('dowopt').hidden = st.selected.length < 3;
    var tripBtn = $('dowtrip');
    if (tripBtn) {
      tripBtn.hidden = !st.selected.length;
      tripBtn.href = (T.tripUrl || '/trip/') + '#trip=' + encodeURIComponent(
        st.selected.join(',') + ';o=' + st.origin.n + ';s=' + st.start + ';d=' + st.days +
        ';h=' + (st.dayHours[0] || 8) + ';p=' + st.people);
    }

    /* list — ჯერ არჩეულები, მერე ხელმისაწვდომები, ჩამქრალები ბოლოში */
    var list = visible();
    $('dowcount').textContent = T.total + ' ' + list.length + ' ' + T.place;
    $('dowselcount').textContent = T.chosenN + ' ' + st.selected.length;
    var selIdx = {}; st.selected.forEach(function (s, i) { selIdx[s] = i + 1; });
    var fitCache = {}, detCache = {};
    list.forEach(function (p) {
      fitCache[p.s] = selIdx[p.s] ? 0 : (fits(p) ? 1 : 2);
      if (!selIdx[p.s]) detCache[p.s] = detour(p);
    });
    /* არჩეულები ზემოთ (მარშრუტის რიგით), მერე ყველაზე მცირე გადახვევა,
       ბოლოში — დროში ვერჩამტევი. */
    list = list.slice().sort(function (a, b) {
      var d = fitCache[a.s] - fitCache[b.s];
      if (d) return d;
      if (fitCache[a.s] === 0) return selIdx[a.s] - selIdx[b.s];
      var da = detCache[a.s] || { km: 0, min: 0 }, db = detCache[b.s] || { km: 0, min: 0 };
      var dm = da.min - db.min;
      if (Math.abs(dm) > 1) return dm;
      return da.km - db.km;
    });
    var lb = $('dowlist');
    lb.innerHTML = '';
    list.forEach(function (p) {
      var on = !!selIdx[p.s], ok = fits(p), vis = !!st.visited[p.s];
      var row = document.createElement('div');
      row.className = 'dow-place' + (on ? ' on' : '') + (!ok && !on ? ' dim' : '');
      var d0 = leg(st.origin, p);
      var ava = on
        ? '<span class="dow-ava sel">' + esc(String(selIdx[p.s])) + '</span>'
        : (p.img
          ? '<span class="dow-ava img"><img src="' + esc(p.img) + '" alt="" loading="lazy"></span>'
          : '<span class="dow-ava">' + esc(p.n.slice(0, 1)) + '</span>');
      if (on) { row.dataset.slug = p.s; row.classList.add('drag'); }
      row.innerHTML =
        (on ? '<span class="dow-grab" title="' + esc(T.dragHint) + '" aria-hidden="true">⠿</span>' : '') +
        '<input type="checkbox" aria-label="' + esc(p.n) + '"' + (on ? ' checked' : '') + '>' +
        '<button type="button" class="dow-place-main">' + ava +
        '<span class="dow-place-t"><span class="dow-place-n">' + esc(p.n) + '</span>' +
        '<span>' + esc(p.gn) + ' · ' + esc(p.t) + (p.r ? ' · ' + Number(p.r).toFixed(1) + ' ★' : '') + '</span>' +
        '<span>' + hm(p.hh * 60) + ' ' + esc(T.visit) + ' · ' +
        (on || !detCache[p.s] || !st.selected.length
          ? Math.round(d0.km) + ' ' + esc(T.km)
          : '<b class="dow-det">' + (detCache[p.s].km >= 1
              ? '+' + Math.round(detCache[p.s].km) + ' ' + esc(T.km) + ' ' + esc(T.detour)
              : (detCache[p.s].min >= 10
                ? '+' + hm(detCache[p.s].min) + ' ' + esc(T.detour)
                : esc(T.onWay))) + '</b>') +
        (vis ? ' · ' + esc(T.visited) : (ok ? '' : ' · ' + esc(T.noFit))) + '</span></span></button>' +
        '<button type="button" class="dow-info" aria-label="' + esc(T.details) + '"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0b2f4d" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 11v5M12 8h.01"></path></svg></button>';
      row.querySelector('input').onchange = function () { toggle(p.s); };
      row.querySelector('.dow-place-main').onclick = function () { toggle(p.s); };
      row.querySelector('.dow-info').onclick = function () { st.detail = [p.s]; render(); };
      if (on) attachDrag(row);
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
          '<button type="button" aria-label="' + esc(T.moveUp) + '">↑</button>' +
          '<button type="button" aria-label="' + esc(T.moveDown) + '">↓</button>' +
          '<button type="button" class="x" aria-label="' + esc(T.removeL) + '">×</button>';
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

    /* car suggestion — შეცვლადი ჩამონათვალით, teaser ცარიელ მდგომარეობაში */
    var car = suggestCar();
    var minPrice = D.fleet && D.fleet.length
      ? D.fleet.reduce(function (m, c) { return Math.min(m, c.price); }, Infinity) : 0;
    var tSel = $('dowtransport');
    var tName = tSel.options[tSel.selectedIndex] ? tSel.options[tSel.selectedIndex].text : '';
    ['dowcar', 'dowcar2'].forEach(function (id) {
      var box = $(id);
      if (!box) return;
      var teaser = !car && st.transport !== 'own' && minPrice && id === 'dowcar';
      box.hidden = !car && !teaser;
      box.classList.toggle('teaser', !!teaser);
      var selEl = box.querySelector('.dow-car-sel');
      var bkBtn = box.querySelector('[data-dow-book]');
      if (teaser) {
        box.querySelector('.dow-car-n').textContent = '';
        box.querySelector('.dow-car-p').textContent = '';
        box.querySelector('.dow-car-s').textContent = T.teaserA + ' ' + minPrice + ' ' + T.teaserB;
        box.querySelector('.dow-car-r').textContent = '';
        if (selEl) selEl.hidden = true;
        if (bkBtn) bkBtn.hidden = true;
        return;
      }
      if (!car) return;
      if (bkBtn) bkBtn.hidden = false;
      var total = car.price * Math.max(1, st.days);
      var usd = car.priceUsd ? ' · ≈ $' + (car.priceUsd * Math.max(1, st.days)) : '';
      box.querySelector('.dow-car-n').textContent = car.n;
      box.querySelector('.dow-car-p').textContent = car.price + ' ₾ / ' + T.day1 + ' · ' + T.sum + ' ' + total + ' ₾' + usd;
      box.querySelector('.dow-car-s').textContent = car.seats + ' ' + T.seat + ' · ' + car.cat_n + (car.fuel ? ' · ' + car.fuel + ' ' + T.per100 : '');
      box.querySelector('.dow-car-r').textContent = (mountainRoute() ? T.need4 : T.noNeed4) +
        (st.transport === 'driver' ? ' · ' + tName : '');
      if (selEl) {
        selEl.hidden = false;
        if (!selEl.dataset.filled) {
          selEl.dataset.filled = '1';
          D.fleet.forEach(function (c) {
            var o = document.createElement('option');
            o.value = c.s;
            o.textContent = c.n + ' — ' + c.price + ' ₾';
            selEl.appendChild(o);
          });
          selEl.onchange = function () { st.carOverride = this.value; render(); };
        }
        selEl.value = car.s;
      }
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
        el.innerHTML = (p.img ? '<img class="dow-ditem-img" src="' + esc(p.img) + '" alt="" loading="lazy">' : '') +
          '<b>' + esc(p.n) + '</b>' +
          '<span>' + esc(p.gn) + ' · ' + esc(p.t) + (p.r ? ' · ' + Number(p.r).toFixed(1) + ' ★' : '') + '</span>' +
          '<span>' + esc(T.visit) + ' ' + hm(p.hh * 60) + ' · ' + Math.round(leg(st.origin, p).km) + ' ' + esc(T.km) + '</span>' +
          '<div class="dow-ditem-b"><button type="button" class="a">' + esc(on ? T.removeStop : (ok ? T.addStop : T.noFit)) + '</button>' +
          '<button type="button" class="v">' + esc(st.visited[p.s] ? T.visitedYes : T.markVisited) + '</button>' +
          (p.u ? '<a class="dow-ditem-link" href="' + esc(p.u) + '" target="_blank" rel="noopener">' + esc(T.fullPage) + '</a>' : '') + '</div>';
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
    var badge = $('dowtabroutec');
    if (badge) {
      badge.hidden = !st.selected.length;
      badge.textContent = st.selected.length;
    }
    var mcta = $('dowmcta');
    if (mcta) {
      var showM = mob && st.selected.length > 0 && car;
      mcta.hidden = !showM;
      if (showM) $('dowmctatxt').textContent = car.n + ' · ' + (car.price * Math.max(1, st.days)) + ' ₾';
    }

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
  function findPlaceByName(n) {
    n = String(n || '').trim().toLowerCase();
    for (var i = 0; i < pool.length; i++) if (pool[i].n.toLowerCase() === n) return pool[i];
    return null;
  }
  if (st._originName) {
    var op0 = findPlaceByName(st._originName);
    if (op0) st.origin = { n: op0.n, la: op0.la, lo: op0.lo, f: op0.f || 1.4, v: op0.v || 55 };
    oi.value = st.origin.n;
    delete st._originName;
  }
  var stayList = $('dowstaylist');
  if (stayList) {
    TOWNS.forEach(function (t) {
      var o = document.createElement('option');
      o.value = t.n;
      stayList.appendChild(o);
    });
  }
  $('dowret').onchange = function () {
    st.ret = this.value;
    routeKey = '';
    render();
    if (st.ret === 'other') { var si = $('dowstay'); si.hidden = false; si.focus(); }
  };
  $('dowstay').onchange = function () {
    var x = findPlaceByName(this.value);
    st.stay = x ? { n: x.n, la: x.la, lo: x.lo, f: x.f || 1.4, v: x.v || 55 } : null;
    routeKey = '';
    render();
  };
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
  function snapshot() {
    return { selected: st.selected.slice(), days: st.days, dayHours: st.dayHours.slice(), tourId: st.tourId };
  }
  function restore(s) {
    st.selected = s.selected; st.days = s.days; st.dayHours = s.dayHours; st.tourId = s.tourId;
    routeKey = '';
    render();
  }
  $('dowtourclear').onclick = function () {
    var prev = snapshot();
    st.tourId = ''; st.selected = [];
    routeKey = '';
    render();
    flash('✓', false, function () { restore(prev); });
  };
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
  /* შენახვა — ანგარიშზე (Firebase). შეუსვლელ მომხმარებელს ლოგინის
     ფანჯარა უხტება; შესვლისთანავე დაწყებული შენახვა თავად სრულდება. */
  var pendingSave = null, retryReg = false;
  function regSaveRetry() {
    if (retryReg || !window.FH || !window.FH.on) return;
    retryReg = true;
    window.FH.on(function (u) {
      if (u && pendingSave) { var p = pendingSave; pendingSave = null; cloudSave(p); }
    });
  }
  function cloudSave(payload) {
    window.FH.saveTrip(payload).then(function () {
      flash(T.saved);
    }).catch(function (e) {
      if (e === 'no-user') { pendingSave = payload; regSaveRetry(); flash(T.signinToSave); }
      else flash(T.saveErr || T.sendErr);
    });
  }
  $('dowopt').onclick = function () {
    if (st.selected.length < 3) return;
    var prev = snapshot();
    var before = orderMin(st.selected);
    var next = optimizeOrder(st.selected);
    var after = orderMin(next);
    if (after >= before - 1) { flash(T.optNone); return; }
    st.selected = next;
    routeKey = '';
    render();
    flash(T.optDone.replace('%s', hm(before - after)), false, function () { restore(prev); routeKey = ''; render(); });
  };
  $('dowsave').onclick = function () {
    var trip = tripObj();
    var payload = { title: trip.name, date: trip.start, days: st.days,
      stops: st.selected.map(function (s) { return { n: (BY[s] || {}).n || s }; }), url: shareUrl() };
    if (window.FH && !window.FH.local && window.FH.saveTrip) { cloudSave(payload); return; }
    var saved = [];
    try { saved = JSON.parse(localStorage.getItem('do-trips') || '[]'); } catch (e) { saved = []; }
    saved.push(trip);
    try { localStorage.setItem('do-trips', JSON.stringify(saved)); } catch (e) {}
    flash(T.saved);
  };
  function shareUrl() {
    return location.href.split('#')[0] + '#trip=' + encodeURIComponent(
      st.selected.join(',') + ';o=' + st.origin.n + ';s=' + st.start + ';d=' + st.days);
  }
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
      /* გაჩერებები სურათებით — თითო ახალ ტაბში იხსნება, მთავარი გვერდი არ იკარგება */
      var stops = (r.wp || []).filter(function (s) { return BY[s]; }).slice(0, 6)
        .map(function (s) {
          var p = BY[s];
          var inner = p.img
            ? '<img src="' + esc(p.img) + '" alt="" loading="lazy">'
            : '<i>' + esc(p.n.slice(0, 1)) + '</i>';
          return '<a class="dow-tstop" href="' + esc(p.u) + '" target="_blank" rel="noopener" title="' + esc(p.n) + '">' +
            inner + '<span>' + esc(p.n) + '</span></a>';
        }).join('');
      var el = document.createElement('div');
      el.className = 'dow-tour';
      el.innerHTML =
        '<div class="dow-tour-ph">' + (r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy">' : esc(r.n)) + '</div>' +
        '<div class="dow-tour-in"><b>' + esc(r.n) + '</b>' +
        '<span>' + r.days + ' ' + esc(T.day) + ' · ' + r.km + ' ' + esc(T.km) + (r.drive ? ' · ' + esc(T.onRoad) + ' ' + esc(r.drive) : '') + '</span>' +
        '<span>' + esc(r.carLabel) + ' · ' + r.minPeople + '–' + r.maxPeople + ' ' + esc(T.person) + (r.region ? ' · ' + esc(r.region) : '') + '</span>' +
        '<span class="dow-tour-d">' + esc(r.sh || '') + '</span>' +
        (stops ? '<div class="dow-tstops">' + stops + '</div>' : '') +
        '<button type="button">' + esc(T.chooseTour) + '</button></div>';
      el.querySelector('button').onclick = function () { applyTour(r); };
      box.appendChild(el);
    });
    $('dowtempty').hidden = list.length > 0;
  }
  function openTours() { $('dowdrawer').hidden = false; renderTours(); }
  function closeTours() { $('dowdrawer').hidden = true; }
  function applyTour(r) {
    var prev = snapshot();
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
    ensurePointRegions(st.selected.map(function (slug) { return BY[slug]; }).filter(Boolean));
    flash(T.tourApplied, false, function () { restore(prev); });
    root.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  /* „დაგეგმვა" ღილაკები გვერდის ნებისმიერ ადგილას (მთავარი გვერდის ტურის
     ბარათები, hero) — data-tour შლის კონკრეტულ ტურს რუკაზე, უამისოდ drawer იხსნება */
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-open-standard-tour]');
    if (!t) return;
    e.preventDefault();
    var slug = t.getAttribute('data-tour');
    var r = slug ? (D.standardTours || []).filter(function (x) { return x.s === slug; })[0] : null;
    if (r) applyTour(r);
    else { root.scrollIntoView({ behavior: 'smooth', block: 'start' }); openTours(); }
  });
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
  function tripSummary() {
    return st.start + ' – ' + st.end + ' · ' + st.days + ' ' + T.day + ' · ' + st.people + ' ' + T.person + ' · ' + st.selected.length + ' ' + T.stop;
  }
  function waHref(car) {
    var num = String((window.FH_CFG || {}).whatsapp || '').replace(/\D/g, '');
    if (!num) return '';
    var text = 'Drive On: ' + (car ? car.n : '') + ' · ' + tripSummary() + ' · ' +
      st.selected.map(function (s) { return (BY[s] || {}).n || s; }).join(', ') + ' · ' + shareUrl();
    return 'https://wa.me/' + num + '?text=' + encodeURIComponent(text);
  }
  function openBooking() {
    $('dowbooking').hidden = false;
    $('dowbdone').hidden = true;
    $('dowbform').hidden = false;
    $('dowbinvalid').hidden = true;
    $('dowberr').hidden = true;
    var car = suggestCar();
    $('dowbcar').textContent = car ? car.n : '';
    $('dowbsum').textContent = tripSummary();
    var total = car ? car.price * Math.max(1, st.days) : 0;
    var usd = car && car.priceUsd ? ' · ≈ $' + (car.priceUsd * Math.max(1, st.days)) : '';
    $('dowbprice').textContent = car ? car.price + ' ₾ × ' + st.days + ' ' + T.day + ' = ' + total + ' ₾' + usd : '';
    try {
      $('dowbname').value = $('dowbname').value || localStorage.getItem('do-bk-name') || '';
      $('dowbphone').value = $('dowbphone').value || localStorage.getItem('do-bk-phone') || '';
    } catch (e) {}
    var wa = waHref(car);
    ['dowbwa', 'dowbwa2'].forEach(function (id) {
      var a = $(id);
      if (a) { a.hidden = !wa; if (wa) a.href = wa; }
    });
  }
  root.addEventListener('click', function (e) {
    var b = e.target.closest('[data-dow-book]');
    if (b) openBooking();
  });
  $('dowbclose').onclick = function () { $('dowbooking').hidden = true; };
  $('dowbback').onclick = function () { $('dowbooking').hidden = true; };
  $('dowbsend').onclick = function () {
    var btn = $('dowbsend');
    var name = $('dowbname').value.trim(), phone = $('dowbphone').value.trim();
    $('dowbname').classList.toggle('bad', !name);
    $('dowbphone').classList.toggle('bad', !phone);
    if (!name || !phone) { $('dowbinvalid').hidden = false; return; }
    $('dowbinvalid').hidden = true;
    $('dowberr').hidden = true;
    try {
      localStorage.setItem('do-bk-name', name);
      localStorage.setItem('do-bk-phone', phone);
    } catch (e) {}
    var car = suggestCar();
    var tSel = $('dowtransport');
    var tName = tSel.options[tSel.selectedIndex] ? tSel.options[tSel.selectedIndex].text : '';
    var body = new URLSearchParams({
      'form-name': 'contact', name: name, email: '',
      dates: st.start + ' – ' + st.end,
      message: 'Trip Workspace: ' + (car ? car.n : '') + ' · ' + phone + ' · ' + st.people + ' ppl · ' + tName + ' · ' +
        st.selected.map(function (s) { return (BY[s] || {}).n || s; }).join(', ') + ' · ' + shareUrl()
    }).toString();
    var origin = /netlify\.app$/.test(location.hostname) ? '' : 'https://subtle-naiad-c2db5d.netlify.app';
    btn.disabled = true;
    var old = btn.textContent;
    btn.textContent = T.sending;
    fetch(origin + '/', { method: 'POST', mode: origin ? 'no-cors' : 'same-origin',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body })
      .then(function () {
        $('dowbform').hidden = true;
        $('dowbdone').hidden = false;
        $('dowbsum2').textContent = (car ? car.n + ' · ' : '') + tripSummary();
      })
      .catch(function () { $('dowberr').hidden = false; })
      .then(function () { btn.disabled = false; btn.textContent = old; });
  };

  render();
  setTimeout(function () { map.invalidateSize(); }, 120);
})();
