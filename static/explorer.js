/* Fleet House — interactive map explorer
   Needs window.EXP = {pts, ui, lang, base, center, zoom, planner}          */
(function () {
  var E = window.EXP;
  if (!E || !window.L) return;
  var U = E.ui, PTS = E.pts, TOWNS = E.towns || [], BY = {};
  PTS.forEach(function (p) { BY[p.s] = p; });
  TOWNS.forEach(function (p) { BY[p.s] = p; });
  var ALL = PTS.concat(TOWNS);

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  };

  /* ── geo helpers ─────────────────────────────────────────────────── */
  function hav(a1, o1, a2, o2) {
    var R = 6371, t = Math.PI / 180,
      dA = (a2 - a1) * t, dO = (o2 - o1) * t,
      x = Math.sin(dA / 2) * Math.sin(dA / 2) +
        Math.cos(a1 * t) * Math.cos(a2 * t) * Math.sin(dO / 2) * Math.sin(dO / 2);
    return 2 * R * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  }
  /* road distance & time between two points — calibrated against real
     Georgian tour-operator times (2026). Mountain points (>1200 m) cap at
     45 km/h (class c); gravel / 4x4 legs get a slow final phase (24 / 18). */
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
  function fmtH(min) {
    min = Math.round(min);
    var h = Math.floor(min / 60), m = min % 60;
    if (h && m) return h + ' ' + U.h_short + ' ' + m + ' ' + U.min_short;
    if (h) return h + ' ' + U.h_short;
    return m + ' ' + U.min_short;
  }

  /* real road geometry via OSRM: the straight line is drawn instantly as a
     fallback, then snapped to actual roads when the response arrives.
     Times always come from our calibrated model — OSRM is drawing only. */
  var geomSeq = 0;
  function roadGeom(latlons, done) {
    if (latlons.length < 2 || latlons.length > 25 || !window.fetch) return;
    var q = latlons.map(function (p) { return p[1] + ',' + p[0]; }).join(';');
    fetch('https://router.project-osrm.org/route/v1/driving/' + q +
          '?overview=full&geometries=geojson', { mode: 'cors' })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.code === 'Ok' && j.routes && j.routes[0])
          done(j.routes[0].geometry.coordinates.map(function (c) { return [c[1], c[0]]; }));
      }).catch(function () { /* keep the straight line */ });
  }

  /* ── map ─────────────────────────────────────────────────────────── */
  var map = L.map('expmap', { scrollWheelZoom: false, zoomControl: true })
    .setView(E.center, E.zoom);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    { maxZoom: 17, attribution: '&copy; OpenStreetMap' }).addTo(map);
  map.on('click', function () { map.scrollWheelZoom.enable(); });

  var layer = L.layerGroup().addTo(map);
  var routeLayer = L.layerGroup().addTo(map);
  var marks = {};
  /* One canonical map is shared by Explore, point-to-point routing and the
     multi-day planner. Other modules may add their own layers, but must not
     create a second Leaflet instance. */
  window.FH_TRAVEL_MAP = map;
  window.FH_TRAVEL_EXPLORER = {
    map: map,
    clearRoute: function () { routeLayer.clearLayers(); }
  };

  var visited = {};
  try { visited = JSON.parse(localStorage.getItem('fh-visited-places') || '{}') || {}; } catch (e) {}

  function refreshVisited() {
    renderList();
    draw(filtered());
    suggestNear();
    if (cur && BY[cur]) open(cur);
  }
  function persistVisited() {
    localStorage.setItem('fh-visited-places', JSON.stringify(visited));
    if (!window.FH || !window.FH.user || !window.FH.user()) return;
    var u = window.FH.user();
    window.FH.firebase().then(function (a) {
      return a.M.db.setDoc(a.M.db.doc(a.db, 'userPlaces', u.uid), {
        uid: u.uid, slugs: Object.keys(visited).filter(function (s) { return visited[s]; }),
        updatedAt: a.M.db.serverTimestamp()
      }, { merge: true });
    }).catch(function () {});
  }
  function toggleVisited(slug) {
    if (visited[slug]) delete visited[slug]; else visited[slug] = true;
    persistVisited(); refreshVisited();
  }
  function loadCloudVisited() {
    if (!window.FH || !window.FH.user || !window.FH.user()) return;
    var u = window.FH.user();
    window.FH.firebase().then(function (a) {
      return a.M.db.getDoc(a.M.db.doc(a.db, 'userPlaces', u.uid)).then(function (snap) {
        if (snap.exists()) {
          visited = {}; (snap.data().slugs || []).forEach(function (s) { visited[s] = true; });
          localStorage.setItem('fh-visited-places', JSON.stringify(visited)); refreshVisited();
        } else if (Object.keys(visited).length) persistVisited();
      });
    }).catch(function () {});
  }
  document.addEventListener('fh:auth', loadCloudVisited);
  setTimeout(loadCloudVisited, 800);

  function mk(p, dim) {
    var wasVisited = !!visited[p.s];
    var m = L.circleMarker([p.la, p.lo], {
      radius: dim ? 4 : 7, color: '#fff', weight: dim ? 1 : 2,
      fillColor: wasVisited ? '#788493' : p.c, fillOpacity: dim ? .35 : (wasVisited ? .72 : 1)
    });
    m.bindTooltip(p.n, { direction: 'top' });
    m.on('click', function () { if (wpMode) { addWp(p.la, p.lo, p); } else { open(p.s); } });
    return m;
  }

  var townLayer = L.layerGroup().addTo(map);
  TOWNS.forEach(function (p) {
    var m = L.circleMarker([p.la, p.lo], {
      radius: p.k === 'airport' ? 5 : 6, color: '#fff', weight: 2,
      fillColor: p.c, fillOpacity: .9
    });
    m.bindTooltip(p.n, { direction: 'top' });
    m.on('click', function () { setEnd(state.from ? 'to' : 'from', p.s); });
    townLayer.addLayer(m);
  });

  function draw(list) {
    layer.clearLayers(); marks = {};
    var on = {}; list.forEach(function (p) { on[p.s] = 1; });
    PTS.forEach(function (p) {
      var m = mk(p, !on[p.s]);
      marks[p.s] = m; layer.addLayer(m);
    });
  }

  /* ── filtering & search ──────────────────────────────────────────── */
  var state = { q: '', type: '', region: '', visited: '', from: null, to: null };
  var interest = new URLSearchParams(location.search).get('interest');
  if (interest === 'food') state.type = 'winery';
  if (interest === 'culture') state.q = 'museum monastery fortress archaeology';
  if (interest === 'cycling') state.q = 'nature lake town mountain';
  if (interest === 'hotel') state.q = 'hotel guest hostel';

  function norm(s) { return String(s || '').toLowerCase(); }
  function searchable(p) {
    return [p.n, p.t, p.gn, p.s].concat(p.names || []).map(norm).join(' ');
  }

  function filtered() {
    var q = norm(state.q);
    return PTS.filter(function (p) {
      if (state.type && p.ty !== state.type) return false;
      if (state.region && p.g !== state.region) return false;
      if (state.visited === 'yes' && !visited[p.s]) return false;
      if (state.visited === 'no' && visited[p.s]) return false;
      if (q && !q.split(/\s+/).some(function (term) { return searchable(p).indexOf(term) >= 0; })) return false;
      return true;
    });
  }

  function renderList() {
    var list = filtered();
    $('expcount').textContent = list.length + ' ' + U.found;
    var qbox = $('expqlist');
    if (qbox) {
      qbox.innerHTML = state.q ? list.slice(0, 8).map(function (p) {
        return '<button type="button" class="expqitem" data-s="' + esc(p.s) + '">' +
          (p.img ? '<img src="' + esc(p.img) + '" alt="" loading="lazy">' : '') +
          '<span><b>' + esc(p.n) + '</b><small>' + esc(p.t) + ' · ' + esc(p.gn) + '</small></span></button>';
      }).join('') : '';
      qbox.classList.toggle('on', !!state.q && !!list.length);
    }
    draw(list);
  }

  /* ── detail panel ────────────────────────────────────────────────── */
  var cache = {}, cur = null;

  function open(slug) {
    var p = BY[slug]; if (!p) return;
    cur = slug;
    var panel = $('exppanel');
    panel.classList.remove('group-panel');
    panel.classList.add('on');
    panel.setAttribute('aria-hidden', 'false');
    map.setView([p.la, p.lo], Math.max(map.getZoom(), 10), { animate: true });
    if (marks[slug]) marks[slug].openTooltip();
    if (cache[slug]) return paint(cache[slug]);
    $('expbody').innerHTML = '<p class="muted">' + esc(U.loading) + '</p>';
    $('exptitle').textContent = p.n;
    fetch(E.base + 'data/attr/' + E.lang + '/' + slug + '.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { cache[slug] = d; if (cur === slug) paint(d); })
      .catch(function () {
        $('expbody').innerHTML = '<p class="muted"><a href="' + esc(p.u) + '">' +
          esc(U.full_page) + '</a></p>';
      });
  }

  function paint(d) {
    $('exptitle').textContent = d.n;
    var p = BY[d.s];
    var facts = d.facts.map(function (f) {
      return '<div><dt class="k">' + esc(f[0]) + '</dt><dd class="v">' + esc(f[1]) + '</dd></div>';
    }).join('');
    var near = (d.near || []).map(function (x) {
      return '<button class="chip" data-go="' + esc(x[0]) + '">' + esc(x[1]) + '</button>';
    }).join('');
    $('expbody').innerHTML =
      (d.img ? '<figure class="photo"><img src="' + esc(d.img) + '" alt="" loading="lazy">' +
        (d.credit ? '<figcaption>' + (d.credit_url
          ? '<a href="' + esc(d.credit_url) + '" rel="nofollow noopener" target="_blank">' + esc(d.credit) + '</a>'
          : esc(d.credit)) + '</figcaption>' : '') + '</figure>' : '') +
      ((d.gal && d.gal.length) ? '<div class="galstrip">' + d.gal.map(function (g) {
        return '<img src="' + esc(g) + '" alt="" loading="lazy">';
      }).join('') + '</div>' : '') +
      '<div class="exptags"><span class="tag">' + esc(d.t) + '</span>' +
      (d.r ? '<span class="stars sm" title="' + esc(U.rate_label) + '"><i>' +
        '★'.repeat(Math.floor(d.r)) + (d.r % 1 ? '½' : '') + '</i><b>' + d.r + '</b></span>' : '') +
      (d.unesco ? '<span class="tag u">UNESCO</span>' : '') +
      '<span class="tag g">' + esc(d.gn) + '</span></div>' +
      '<div class="expact">' +
      '<button class="btn sm visited-toggle' + (visited[d.s] ? ' on' : '') + '" type="button" data-visited="' + esc(d.s) + '">' +
      (visited[d.s] ? '✓ ' : '') + esc(visited[d.s] ? (U.visited_yes || 'Visited') : (U.visited_mark || 'Mark visited')) + '</button>' +
      '<button class="btn sm" data-set="from">' + esc(U.set_start) + '</button>' +
      '<button class="btn sm alt" data-set="to">' + esc(U.set_end) + '</button>' +
      '<a class="btn sm ghost" href="' + esc(d.u) + '">' + esc(U.full_page) + '</a></div>' +
      '<dl class="facts">' + facts + '</dl>' +
      '<div class="article">' + d.body + '</div>' +
      (d.tip ? '<h4>' + esc(U.tip_title) + '</h4><div class="article">' + d.tip + '</div>' : '') +
      (d.route ? '<h4>' + esc(U.route_title) + '</h4><div class="article">' + d.route + '</div>' : '') +
      (near ? '<h4>' + esc(U.nearby_title) + '</h4><div class="chips">' + near + '</div>' : '');
    if (p && window.WX) {
      var day = $('expday').value;
      WX.get([p], day).then(function (w) {
        if (cur !== d.s || !w[0]) return;
        var el = document.createElement('div');
        el.className = 'wxbox';
        el.innerHTML = '<b>' + esc(U.weather) + ' · ' + esc(day) + '</b>' + WX.badge(w[0]) +
          '<small>' + esc(U.wx_source) + '</small>';
        var tags = $('expbody').querySelector('.exptags');
        if (tags) tags.parentNode.insertBefore(el, tags.nextSibling);
      });
    }
  }

  function close() {
    cur = null;
    var panel = $('exppanel');
    panel.classList.remove('on');
    panel.classList.remove('group-panel');
    panel.setAttribute('aria-hidden', 'true');
  }

  /* ── from → to route with stops along the way ────────────────────── */
  function setEnd(which, slug) {
    autopick = true;
    state[which] = slug;
    $('exp' + which).value = BY[slug] ? BY[slug].n : '';
    route();
  }

  function alongTheWay(a, b, maxDetour) {
    /* detour = the real extra road km of inserting the stop on the leg */
    var base = leg(a, b).km, out = [];
    PTS.forEach(function (p) {
      if (p.s === a.s || p.s === b.s) return;
      var da = hav(a.la, a.lo, p.la, p.lo), db = hav(p.la, p.lo, b.la, b.lo);
      var det = leg(a, p).km + leg(p, b).km - base;
      if (det > maxDetour) return;
      out.push({ p: p, det: Math.max(0, det), t: da / (da + db || 1) });
    });
    out.sort(function (x, y) { return x.t - y.t; });
    var keep = [];
    out.forEach(function (c) {
      for (var i = 0; i < keep.length; i++) {
        if (hav(keep[i].p.la, keep[i].p.lo, c.p.la, c.p.lo) < 6) {
          if (c.det < keep[i].det) keep[i] = c;
          return;
        }
      }
      keep.push(c);
    });
    return keep;
  }

  var off = {}, autopick = true;   /* stops the user unticked */
  function score(c) {
    return (c.p.un ? 2.2 : 0) + (c.p.fe ? 1.4 : 0) - c.det / 12;
  }

  function route() {
    routeLayer.clearLayers();
    var box = $('exproute');
    var a = state.from && BY[state.from], b = state.to && BY[state.to];
    if (!a || !b) {
      box.innerHTML = '<p class="muted">' + esc(!a ? U.pick_start : U.pick_end) + '</p>';
      return;
    }
    var maxDetour = parseInt($('expdetour').value, 10) || 15;
    var all = alongTheWay(a, b, maxDetour);
    /* by default keep the ~8 most rewarding stops; the rest start unticked */
    if (autopick) {
      off = {};
      var rank = all.slice().sort(function (x, y) {
        return score(y) - score(x);
      }).slice(8);
      rank.forEach(function (c) { off[c.p.s] = true; });
      autopick = false;
    }
    var chosen = all.filter(function (c) { return !off[c.p.s]; });

    var direct = leg(a, b);
    var seq = [a].concat(chosen.map(function (c) { return c.p; })).concat([b]);
    var km = 0, drive = 0, visit = 0;
    for (var i = 1; i < seq.length; i++) {
      var l = leg(seq[i - 1], seq[i]); km += l.km; drive += l.min;
    }
    chosen.forEach(function (c) { visit += (c.p.hh || 1) * 60; });

    L.polyline([[a.la, a.lo], [b.la, b.lo]],
      { color: '#94a7ba', weight: 3, opacity: .55, dashArray: '4 8' }).addTo(routeLayer);
    var routePl = L.polyline(seq.map(function (p) { return [p.la, p.lo]; }),
      { color: '#0f4c81', weight: 4, opacity: .85, lineCap: 'round' }).addTo(routeLayer);
    var mySeq = ++geomSeq;
    roadGeom(seq.map(function (p) { return [p.la, p.lo]; }), function (geom) {
      if (mySeq === geomSeq && routeLayer.hasLayer(routePl)) routePl.setLatLngs(geom);
    });
    seq.forEach(function (p, i) {
      L.circleMarker([p.la, p.lo], {
        radius: 9, color: '#0f4c81', weight: 3,
        fillColor: i === 0 ? '#1a7f5a' : (i === seq.length - 1 ? '#c0392b' : '#fff'),
        fillOpacity: 1
      }).addTo(routeLayer).bindTooltip((i + 1) + '. ' + p.n);
    });
    map.fitBounds(L.latLngBounds(seq.map(function (p) { return [p.la, p.lo]; })).pad(0.12));

    /* დღეები — დამგეგმავის ნაგულისხმევი ტემპით (8 სთ/დღე), 9 სთ საჭესთან არარეალურია */
    var days = Math.max(1, Math.ceil((drive + visit) / (8 * 60)));
    box.innerHTML =
      '<div class="exptot">' +
      '<b>' + Math.round(km) + ' ' + esc(U.km) + '</b>' +
      '<span>' + esc(U.drive) + ' ' + fmtH(drive) + '</span>' +
      '<span>' + esc(U.total) + ' ' + fmtH(drive + visit) + '</span>' +
      '<span class="expdays">' + days + ' ' + esc(U.days) + '</span></div>' +
      '<p class="muted sm">' + esc(U.direct) + ': ' + Math.round(direct.km) + ' ' +
      esc(U.km) + ' · ' + fmtH(direct.min) + '</p>' +
      '<h4>' + esc(U.stops_on_way) + ' · ' + chosen.length + '/' + all.length + '</h4>' +
      (all.length
        ? '<ul class="expstops">' + all.map(function (c) {
          return '<li><label class="expchk"><input type="checkbox" data-stop="' + esc(c.p.s) +
            '"' + (off[c.p.s] ? '' : ' checked') + '>' +
            '<span><button class="lnk" type="button" data-go="' + esc(c.p.s) + '">' +
            esc(c.p.n) + '</button>' +
            '<span class="expmeta">' + esc(c.p.t) + ' · ' + esc(c.p.h) +
            ' · +' + Math.round(c.det) + ' ' + esc(U.km) + ' ' + esc(U.detour) +
            '</span></span></label></li>';
        }).join('') + '</ul>'
        : '<p class="muted">' + esc(U.none) + '</p>') +
      (E.planner ? '<a class="btn sm" href="' + esc(E.planner) + '">' + esc(U.open_planner) + '</a>' : '');

    if (window.WX) {
      var day = $('expday').value;
      WX.get(seq, day).then(function (ws) {
        if (!ws.some(Boolean)) return;
        var cells = box.querySelectorAll('.expstops li');
        var head = '<div class="wxrow"><b>' + esc(U.weather) + ' · ' + esc(day) + '</b>' +
          seq.map(function (pt, i) {
            return ws[i] ? '<span class="wxcell" title="' + esc(pt.n) + '">' +
              WX.badge(ws[i]) + '</span>' : '';
          }).join('') + '<small>' + esc(U.wx_source) + '</small></div>';
        var tot = box.querySelector('.exptot');
        if (tot) tot.insertAdjacentHTML('afterend', head);
      });
    }
  }

  /* ── autocomplete for the two endpoint inputs ────────────────────── */
  function suggest(which) {
    var inp = $('exp' + which), box = $('exp' + which + 'list');
    var q = norm(inp.value);
    if (!q) { box.innerHTML = ''; box.classList.remove('on'); return; }
    var hits = ALL.filter(function (p) { return searchable(p).indexOf(q) >= 0; });
    hits.sort(function (a, b) {
      var ta = a.k ? 0 : 1, tb = b.k ? 0 : 1;
      if (ta !== tb) return ta - tb;
      return norm(a.n).indexOf(q) - norm(b.n).indexOf(q);
    });
    hits = hits.slice(0, 10);
    box.innerHTML = hits.map(function (p) {
      return '<button data-pick="' + which + '" data-s="' + esc(p.s) + '">' +
        esc(p.n) + '<small>' + esc(p.k ? p.t : p.gn) + '</small></button>';
    }).join('');
    box.classList.toggle('on', !!hits.length);
  }


  /* ── ჩემი ადგილი, დროის/მანძილის ფილტრი და რუკაზე მოხაზვა ─────────── */
  var me = null, area = null, areaLayer = null, drawing = false;
  var suggested = [], sugOff = {};
  function publishSelection() {
    var slugs = suggested.filter(function (p) { return !sugOff[p.s]; }).map(function (p) { return p.s; });
    window.FH_TRAVEL_SELECTION = slugs;
    document.dispatchEvent(new CustomEvent('fh:selection', { detail: slugs }));
  }

  function ratingStars(p) {
    var r = Number(p.r || 0), full = Math.floor(r);
    return '<span class="place-rating" aria-label="' + esc(U.rate_label || 'Rating') + ' ' + r + '">' +
      '<i>' + '★'.repeat(full) + '☆'.repeat(Math.max(0, 5 - full)) + '</i>' +
      (r ? '<b>' + r + '</b>' : '') + '</span>';
  }

  function placeChoice(p, checked, compact) {
    return '<label class="place-choice' + (compact ? ' compact' : '') + '">' +
      '<input type="checkbox" data-suggest="' + esc(p.s) + '"' + (checked ? ' checked' : '') + '>' +
      (p.img ? '<img src="' + esc(p.img) + '" alt="" loading="lazy">' : '<span class="place-ph" aria-hidden="true"></span>') +
      '<span class="place-copy"><button class="lnk" type="button" data-go="' + esc(p.s) + '">' + esc(p.n) + '</button>' +
      '<span class="place-line">' + esc(p.t) + ' · ' + esc(p.h) + '</span>' + ratingStars(p) + '</span></label>';
  }

  var basePlaceChoice = placeChoice;
  placeChoice = function (p, checked, compact) {
    var html = basePlaceChoice(p, checked, compact);
    var label = visited[p.s] ? (U.visited_yes || 'Visited') : (U.visited_mark || 'Mark as visited');
    return html.replace('</span></label>', '<button class="visited-mini' + (visited[p.s] ? ' on' : '') +
      '" type="button" data-visited="' + esc(p.s) + '">' + (visited[p.s] ? '✓ ' : '') + esc(label) + '</button></span></label>');
  };

  function openGroup(points) {
    var list = points.slice().sort(function (a, b) { return Number(b.r || 0) - Number(a.r || 0); });
    cur = null;
    var panel = $('exppanel');
    panel.classList.add('on', 'group-panel'); panel.setAttribute('aria-hidden', 'false');
    $('exptitle').textContent = list.length === 1 ? list[0].n : list.length + ' ' + (U.found || 'places');
    $('expbody').innerHTML = '<p class="cluster-intro">' + esc(list.length === 1 ?
      (U.single_hint || U.cluster_hint || 'Choose or remove this place from your route.') :
      (U.cluster_hint || 'Choose places for your route. Highest rated appear first.')) + '</p>' +
      '<div class="cluster-list">' + list.map(function (p) { return placeChoice(p, !sugOff[p.s], true); }).join('') + '</div>';
  }

  function budgetMode() {
    var el = document.querySelector('input[name="expmode"]:checked');
    return el ? el.value : 'time';
  }
  function budgetVal() { return parseInt($('expbudget').value, 10) || 8; }

  function origin() {
    if (me) return me;
    if (state.from && BY[state.from]) return BY[state.from];
    var tb = BY['town:tbilisi'];
    if (tb) return tb;
    return { la: E.center[0], lo: E.center[1], f: 1.4, v: 55, n: '' };
  }

  function pointInPoly(la, lo, poly) {
    var inside = false;
    for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      var xi = poly[i][1], yi = poly[i][0], xj = poly[j][1], yj = poly[j][0];
      if (((yi > la) !== (yj > la)) && (lo < (xj - xi) * (la - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }

  /* რა ჩაეტევა მოცემულ დროში / რადიუსში — ჩასმის ევრისტიკა */
  function suggestNear() {
    var box = $('expnear');
    var o = origin();
    var mode = budgetMode(), val = budgetVal();
    var pool = PTS.filter(function (p) {
      if (area && !pointInPoly(p.la, p.lo, area)) return false;
      if (state.type && p.ty !== state.type) return false;
      if (state.region && p.g !== state.region) return false;
      if (mode === 'km' && leg(o, p).km > val) return false;
      return true;
    });
    if (!pool.length) { box.innerHTML = '<p class="muted sm">' + esc(U.none) + '</p>'; return; }

    var chosen = [], minutes = 0;
    if (mode === 'time') {
      var cap = val * 60;
      var cand = pool.slice().sort(function (a, b) {
        return (score2(b, o) - score2(a, o));
      }).slice(0, 60);
      for (var g = 0; g < 30; g++) {
        var best = null, bestPos = 0, bestGain = -Infinity, bestT = 0;
        for (var i = 0; i < cand.length; i++) {
          if (chosen.indexOf(cand[i]) >= 0) continue;
          for (var pos = 0; pos <= chosen.length; pos++) {
            var trial = chosen.slice(0, pos).concat([cand[i]], chosen.slice(pos));
            var t = chainTime(o, trial);
            if (t > cap) continue;
            var gain = ((cand[i].un ? 2 : 0) + (cand[i].fe ? 1.5 : 0) + 1) / Math.max(t - minutes, 12);
            if (gain > bestGain) { bestGain = gain; best = cand[i]; bestPos = pos; bestT = t; }
          }
        }
        if (!best) break;
        chosen.splice(bestPos, 0, best); minutes = bestT;
      }
    } else {
      chosen = pool.slice().sort(function (a, b) { return leg(o, a).km - leg(o, b).km; }).slice(0, 25);
    }
    chosen = order2opt(o, chosen);
    suggested = chosen;
    publishSelection();
    var active = chosen.filter(function (p) { return !sugOff[p.s]; });
    minutes = chainTime(o, active);

    box.innerHTML =
      '<div class="exptot"><b>' + active.length + '/' + chosen.length + '</b><span>' + esc(U.suggest) + '</span>' +
      (mode === 'time' ? '<span>' + fmtH(minutes) + ' / ' + val + ' ' + esc(U.hrs) + '</span>'
                       : '<span>≤ ' + val + ' ' + esc(U.km) + '</span>') + '</div>' +
      '<div class="suggest-list">' + chosen.map(function (p) {
        return placeChoice(p, !sugOff[p.s], false);
      }).join('') + '</div>';
    drawSuggest(o, active);
  }

  /* nearest-neighbour + 2-opt — გონივრული თანმიმდევრობა.
     ღირებულება = სავალი დრო (კალიბრებული მოდელით), არა სწორი ხაზი.
     open=true → ღია მარშრუტი (საწყისში დაბრუნების გარეშე) — წერტილებით
     მარშრუტისთვის, სადაც უკან დაბრუნება არ იგეგმება */
  function order2opt(o, list, open) {
    if (list.length < 3) return list.slice();
    var left = list.slice(), out = [], cur = o;
    while (left.length) {
      var bi = 0, bd = Infinity;
      for (var i = 0; i < left.length; i++) {
        var d = leg(cur, left[i]).min;
        if (d < bd) { bd = d; bi = i; }
      }
      cur = left[bi]; out.push(cur); left.splice(bi, 1);
    }
    function cost(r) {
      var c = 0, prev = o;
      for (var i = 0; i < r.length; i++) { c += leg(prev, r[i]).min; prev = r[i]; }
      if (!open) c += leg(prev, o).min;
      return c;
    }
    var best = out, bc = cost(best), improved = true, guard = 0;
    while (improved && guard++ < 30) {
      improved = false;
      for (var i2 = 0; i2 < best.length - 1; i2++) {
        for (var j = i2 + 1; j < best.length; j++) {
          var cand = best.slice(0, i2).concat(best.slice(i2, j + 1).reverse(), best.slice(j + 1));
          var cc = cost(cand);
          if (cc < bc - 0.01) { best = cand; bc = cc; improved = true; }
        }
      }
    }
    return best;
  }
  function score2(p, o) {
    return (p.un ? 2.4 : 0) + (p.fe ? 1.6 : 0) - leg(o, p).km / 160;
  }
  function chainTime(o, list) {
    var t = 0, prev = o;
    for (var i = 0; i < list.length; i++) { t += leg(prev, list[i]).min + (list[i].hh || 1) * 60; prev = list[i]; }
    t += leg(prev, o).min;
    return t;
  }
  var sugLayer = L.layerGroup().addTo(map);
  function spatialGroups(list) {
    var left = list.slice(), groups = [];
    while (left.length) {
      var seed = left.shift(), group = [seed];
      for (var i = left.length - 1; i >= 0; i--) {
        if (hav(seed.la, seed.lo, left[i].la, left[i].lo) <= 18) group.push(left.splice(i, 1)[0]);
      }
      groups.push(group);
    }
    return groups;
  }
  function drawSuggest(o, list) {
    sugLayer.clearLayers();
    if (!list.length) return;
    var pts = [[o.la, o.lo]].concat(list.map(function (p) { return [p.la, p.lo]; }));
    pts.push([o.la, o.lo]);
    var sugPl = L.polyline(pts, { color: '#2dd4bf', weight: 3, opacity: .8 }).addTo(sugLayer);
    var mySeq = ++geomSeq;
    roadGeom(pts, function (geom) {
      if (mySeq === geomSeq && sugLayer.hasLayer(sugPl)) sugPl.setLatLngs(geom);
    });
    spatialGroups(list).forEach(function (group) {
      var la = 0, lo = 0; group.forEach(function (p) { la += p.la; lo += p.lo; });
      la /= group.length; lo /= group.length;
      var label = group.length > 1 ? group.length : '•';
      var allVisited = group.every(function (p) { return !!visited[p.s]; });
      var marker = L.marker([la, lo], { icon: L.divIcon({ className: 'placecluster' + (group.length === 1 ? ' single' : '') + (allVisited ? ' visited' : ''),
        html: '<b>' + label + '</b>', iconSize: [34, 34] }) }).addTo(sugLayer);
      marker.bindTooltip(group.length > 1 ? group.length + ' ' + (U.found || 'places') : group[0].n);
      // One marker and a cluster use the same selectable panel. Previously a single
      // place opened only the read-only details view, so it could not be removed.
      marker.on('click', function () { openGroup(group); });
    });
    L.circleMarker([o.la, o.lo], { radius: 9, color: '#2dd4bf', weight: 3,
      fillColor: '#0b1220', fillOpacity: 1 }).addTo(sugLayer);
    map.fitBounds(L.latLngBounds(pts).pad(0.15));
  }

  function locate() {
    var b = $('expgeo');
    if (!navigator.geolocation) { b.textContent = U.loc_err; return; }
    b.textContent = U.locating;
    var done = false;
    navigator.geolocation.getCurrentPosition(function (pos) {
      done = true;
      me = { s: 'me', n: U.my_loc, la: pos.coords.latitude, lo: pos.coords.longitude,
             f: 1.4, v: 55, hh: 0 };
      BY.me = me;
      b.textContent = '◎ ' + U.my_loc;
      b.title = '±' + Math.round(pos.coords.accuracy || 0) + ' m';
      b.classList.add('on');
      b.classList.toggle('approx', (pos.coords.accuracy || 0) >= 100);
      if (pos.coords.accuracy) L.circle([me.la, me.lo], { radius: pos.coords.accuracy,
        color: (pos.coords.accuracy >= 100 ? '#f59e0b' : '#38bdf8'), weight: 1,
        fillOpacity: .08, interactive: false }).addTo(sugLayer);
      L.circleMarker([me.la, me.lo], { radius: 8, color: '#2dd4bf', weight: 3,
        fillColor: '#fff', fillOpacity: 1 }).addTo(sugLayer).bindTooltip(U.my_loc);
      map.setView([me.la, me.lo], 9);
      suggestNear();
    }, function (err) {
      if (done) return;
      var why = err && err.code === 1 ? (U.loc_denied || U.loc_fallback) :
        (err && err.code === 3 ? (U.loc_timeout || U.loc_fallback) : (U.loc_fallback || U.loc_err));
      b.textContent = why || U.loc_err;
      pickLoc = true;
      document.getElementById('expmap').classList.add('drawing');
    }, { timeout: 20000, maximumAge: 60000, enableHighAccuracy: true });
  }
  var pickLoc = false;
  map.on('click', function (e) {
    if (pickLoc) {
      pickLoc = false;
      document.getElementById('expmap').classList.remove('drawing');
      me = { s: 'me', n: U.my_loc, la: e.latlng.lat, lo: e.latlng.lng, f: 1.4, v: 55, hh: 0 };
      BY.me = me;
      var b = $('expgeo');
      b.textContent = '◎ ' + U.my_loc; b.classList.add('on');
      L.circleMarker([me.la, me.lo], { radius: 8, color: '#2dd4bf', weight: 3,
        fillColor: '#fff', fillOpacity: 1 }).addTo(sugLayer).bindTooltip(U.my_loc);
      suggestNear();
      return;
    }
    if (wpMode) { addWp(e.latlng.lat, e.latlng.lng, null); }
  });

  /* freehand lasso */
  function toggleDraw() {
    drawing = !drawing;
    $('expdraw').classList.toggle('on', drawing);
    document.getElementById('expmap').classList.toggle('drawing', drawing);
    if (!drawing) return;
    if (areaLayer) { map.removeLayer(areaLayer); areaLayer = null; }
    area = null;
    map.dragging.disable();
    var pts = [], line = null;
    function move(e) {
      pts.push([e.latlng.lat, e.latlng.lng]);
      if (!line) { line = L.polyline(pts, { color: '#2dd4bf', weight: 3, dashArray: '4 6' }).addTo(map); }
      else line.setLatLngs(pts);
    }
    function up() {
      map.off('mousemove', move); map.off('mouseup', up); map.off('mousedown', down);
      map.dragging.enable();
      if (line) map.removeLayer(line);
      if (pts.length > 4) {
        area = pts;
        areaLayer = L.polygon(pts, { color: '#2dd4bf', weight: 2, fillOpacity: .08 }).addTo(map);
      }
      drawing = false;
      $('expdraw').classList.remove('on');
      document.getElementById('expmap').classList.remove('drawing');
      suggestNear();
    }
    function down(e) { pts = [[e.latlng.lat, e.latlng.lng]]; map.on('mousemove', move); map.on('mouseup', up); }
    map.on('mousedown', down);
  }


  /* ── წერტილებით მარშრუტი: ვაჭერ რუკას თანმიმდევრობით ────────────── */
  var wpMode = false, wps = [], wpLayer = L.layerGroup().addTo(map);

  function toggleWp() {
    wpMode = !wpMode;
    $('expwp').classList.toggle('on', wpMode);
    document.getElementById('expmap').classList.toggle('drawing', wpMode);
    if (wpMode && !wps.length) $('expnear').innerHTML =
      '<p class="muted sm">' + esc(U.wp_hint) + '</p>';
  }
  function addWp(la, lo, ref) {
    /* თუ ღირსშესანიშნაობასთან ახლოსაა (6 კმ) — თვითონ ის ავიღოთ */
    if (!ref) {
      var best = null, bd = 6;
      PTS.forEach(function (p) {
        var d = hav(la, lo, p.la, p.lo);
        if (d < bd) { bd = d; best = p; }
      });
      ref = best;
    }
    wps.push(ref || { s: 'wp' + wps.length, n: (U.point || 'Point') + ' ' + (wps.length + 1),
                      la: la, lo: lo, f: 1.4, v: 55, hh: 0, t: '', h: '' });
    renderWp();
  }
  function wpTime() {
    var t = 0, km = 0;
    for (var i = 1; i < wps.length; i++) {
      var l = leg(wps[i - 1], wps[i]); t += l.min; km += l.km;
    }
    wps.forEach(function (p, i) { if (i > 0) t += (p.hh || 0) * 60; });
    return { min: t, km: km };
  }
  function renderWp() {
    var box = $('expnear');
    if (!wps.length) { box.innerHTML = ''; wpLayer.clearLayers(); return; }
    var tot = wpTime();
    box.innerHTML =
      '<div class="exptot"><b>' + Math.round(tot.km) + ' ' + esc(U.km) + '</b>' +
      '<span>' + esc(U.total) + ' ' + fmtH(tot.min) + '</span>' +
      '<span>' + wps.length + '</span></div>' +
      '<ol class="expstops wplist">' + wps.map(function (p, i) {
        return '<li data-i="' + i + '">' +
          '<button class="lnk" type="button"' + (p.u ? ' data-go="' + esc(p.s) + '"' : '') + '>' +
          esc(p.n) + '</button>' +
          '<span class="expmeta">' + (i > 0 ? '+' + fmtH(leg(wps[i - 1], p).min +
            (p.hh || 0) * 60) : '') + '</span>' +
          '<span class="wpbtns">' +
          '<button type="button" data-wpup="' + i + '" title="' + esc(U.up) + '">↑</button>' +
          '<button type="button" data-wpdn="' + i + '" title="' + esc(U.down) + '">↓</button>' +
          '<button type="button" data-wpx="' + i + '" title="' + esc(U.remove) + '">✕</button>' +
          '</span></li>';
      }).join('') + '</ol>' +
      '<div class="prow">' +
      '<button class="btn sm" type="button" id="wpopt">' + esc(U.optimize) + '</button>' +
      '<button class="btn sm ghost" type="button" id="wpclear">' + esc(U.reset) + '</button></div>';
    drawWp();
    var opt = document.getElementById('wpopt');
    if (opt) opt.onclick = function () {
      if (wps.length < 3) return;
      var first = wps[0];
      wps = [first].concat(order2opt(first, wps.slice(1), true));
      renderWp();
    };
    var clr = document.getElementById('wpclear');
    if (clr) clr.onclick = function () { wps = []; renderWp(); };
    box.querySelectorAll('[data-wpup]').forEach(function (b) {
      b.onclick = function () {
        var i = +b.dataset.wpup;
        if (i > 0) { var t = wps[i - 1]; wps[i - 1] = wps[i]; wps[i] = t; renderWp(); }
      };
    });
    box.querySelectorAll('[data-wpdn]').forEach(function (b) {
      b.onclick = function () {
        var i = +b.dataset.wpdn;
        if (i < wps.length - 1) { var t = wps[i + 1]; wps[i + 1] = wps[i]; wps[i] = t; renderWp(); }
      };
    });
    box.querySelectorAll('[data-wpx]').forEach(function (b) {
      b.onclick = function () { wps.splice(+b.dataset.wpx, 1); renderWp(); };
    });
  }
  function drawWp() {
    wpLayer.clearLayers();
    if (!wps.length) return;
    var wpPl = L.polyline(wps.map(function (p) { return [p.la, p.lo]; }),
      { color: '#38bdf8', weight: 4, opacity: .85 }).addTo(wpLayer);
    var mySeq = ++geomSeq;
    roadGeom(wps.map(function (p) { return [p.la, p.lo]; }), function (geom) {
      if (mySeq === geomSeq && wpLayer.hasLayer(wpPl)) wpPl.setLatLngs(geom);
    });
    wps.forEach(function (p, i) {
      L.marker([p.la, p.lo], { icon: L.divIcon({ className: 'numpin blue',
        html: '<b>' + (i + 1) + '</b>', iconSize: [22, 22] }) }).addTo(wpLayer).bindTooltip(p.n);
    });
    if (wps.length > 1)
      map.fitBounds(L.latLngBounds(wps.map(function (p) { return [p.la, p.lo]; })).pad(0.2));
  }

  /* ── wiring ──────────────────────────────────────────────────────── */
  $('expq').addEventListener('input', function () { state.q = this.value; renderList(); });
  $('expq').addEventListener('focus', function () { if (state.q) renderList(); });
  $('expq').addEventListener('blur', function () { setTimeout(function () { var q = $('expqlist'); if (q) q.classList.remove('on'); }, 180); });
  $('exptype').addEventListener('change', function () { state.type = this.value; renderList(); suggestNear(); });
  $('expregion').addEventListener('change', function () { state.region = this.value; renderList(); suggestNear(); });
  $('expvisited').addEventListener('change', function () { state.visited = this.value; renderList(); suggestNear(); });
  $('expreset').addEventListener('click', function () {
    state.q = ''; state.type = ''; state.region = ''; state.visited = '';
    $('expq').value = ''; $('exptype').value = ''; $('expregion').value = ''; $('expvisited').value = '';
    renderList(); map.setView(E.center, E.zoom);
  });
  ['from', 'to'].forEach(function (w) {
    $('exp' + w).addEventListener('input', function () { suggest(w); });
    $('exp' + w).addEventListener('blur', function () {
      setTimeout(function () { $('exp' + w + 'list').classList.remove('on'); }, 180);
    });
  });
  $('expswap').addEventListener('click', function () {
    var f = state.from; state.from = state.to; state.to = f;
    $('expfrom').value = state.from && BY[state.from] ? BY[state.from].n : '';
    $('expto').value = state.to && BY[state.to] ? BY[state.to].n : '';
    route();
  });
  $('expdetour').addEventListener('input', function () {
    $('expdetourv').textContent = this.value + ' ' + U.km;
    autopick = true;
    route();
  });
  document.addEventListener('change', function (e) {
    var t = e.target;
    if (t && t.hasAttribute && t.hasAttribute('data-stop')) {
      off[t.getAttribute('data-stop')] = !t.checked;
      route();
    }
    if (t && t.hasAttribute && t.hasAttribute('data-suggest')) {
      sugOff[t.getAttribute('data-suggest')] = !t.checked;
      document.querySelectorAll('[data-suggest="' + CSS.escape(t.getAttribute('data-suggest')) + '"]').forEach(function (x) {
        if (x !== t) x.checked = t.checked;
      });
      var active = suggested.filter(function (p) { return !sugOff[p.s]; });
      publishSelection();
      drawSuggest(origin(), active);
      suggestNear();
    }
  });
  $('expday').value = window.WX ? WX.iso(0) : '';
  $('expday').addEventListener('change', function () { route(); if (cur) { delete cache[cur]; open(cur); } });
  $('expgeo').addEventListener('click', locate);
  $('expwp').addEventListener('click', toggleWp);
  $('expdraw').addEventListener('click', toggleDraw);
  document.querySelectorAll('input[name="expmode"]').forEach(function (r) {
    r.addEventListener('change', function () {
      var b = $('expbudget');
      if (budgetMode() === 'km') { b.min = 10; b.max = 400; b.step = 10; b.value = 100; }
      else { b.min = 2; b.max = 72; b.step = 1; b.value = 8; }
      updBudget(); suggestNear();
    });
  });
  function updBudget() {
    $('expbudgetv').textContent = budgetVal() + ' ' + (budgetMode() === 'km' ? U.km : U.hrs);
  }
  $('expbudget').addEventListener('input', function () { updBudget(); suggestNear(); });
  updBudget();
  $('expclose').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-s],[data-go],[data-set],[data-pick],[data-visited]') : null;
    if (!t) return;
    if (t.hasAttribute('data-visited')) { e.preventDefault(); e.stopPropagation(); toggleVisited(t.getAttribute('data-visited')); return; }
    if (t.hasAttribute('data-pick')) {
      setEnd(t.getAttribute('data-pick'), t.getAttribute('data-s'));
      $('exp' + t.getAttribute('data-pick') + 'list').classList.remove('on');
      return;
    }
    if (t.hasAttribute('data-set')) { if (cur) setEnd(t.getAttribute('data-set'), cur); return; }
    if (t.hasAttribute('data-go')) { e.preventDefault(); e.stopPropagation(); open(t.getAttribute('data-go')); return; }
  });

  if (state.type) $('exptype').value = state.type;
  if (state.q) $('expq').value = state.q;
  renderList();
  route();
  suggestNear();
})();
