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
  /* road distance & time between two points, using each point's own
     sinuosity factor f and average speed v (calibrated in build.py)     */
  function leg(a, b) {
    var d = hav(a.la, a.lo, b.la, b.lo);
    var f = ((a.f || 1.4) + (b.f || 1.4)) / 2;
    var v = Math.min(a.v || 55, b.v || 55);
    var km = d * f;
    return { km: km, min: (km / v) * 60 };
  }
  function fmtH(min) {
    min = Math.round(min);
    var h = Math.floor(min / 60), m = min % 60;
    if (h && m) return h + ' ' + U.h_short + ' ' + m + ' ' + U.min_short;
    if (h) return h + ' ' + U.h_short;
    return m + ' ' + U.min_short;
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

  function mk(p, dim) {
    var m = L.circleMarker([p.la, p.lo], {
      radius: dim ? 4 : 7, color: '#fff', weight: dim ? 1 : 2,
      fillColor: p.c, fillOpacity: dim ? .35 : 1
    });
    m.bindTooltip(p.n, { direction: 'top' });
    m.on('click', function () { open(p.s); });
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
  var state = { q: '', type: '', region: '', from: null, to: null };

  function norm(s) { return String(s || '').toLowerCase(); }

  function filtered() {
    var q = norm(state.q);
    return PTS.filter(function (p) {
      if (state.type && p.ty !== state.type) return false;
      if (state.region && p.g !== state.region) return false;
      if (q && norm(p.n).indexOf(q) < 0 && norm(p.t).indexOf(q) < 0 &&
        norm(p.gn).indexOf(q) < 0 && norm(p.s).indexOf(q) < 0) return false;
      return true;
    });
  }

  function renderList() {
    var list = filtered(), box = $('explist');
    $('expcount').textContent = list.length + ' ' + U.found;
    if (!list.length) { box.innerHTML = '<p class="muted">' + esc(U.none) + '</p>'; draw(list); return; }
    box.innerHTML = list.slice(0, 400).map(function (p) {
      return '<button class="expitem" data-s="' + esc(p.s) + '">' +
        (p.img ? '<img class="expthumb" src="' + esc(p.img) + '" alt="" loading="lazy">' : '') +
        '<i style="background:' + esc(p.c) + '"></i>' +
        '<span class="expitem-n">' + esc(p.n) + '</span>' +
        '<span class="expitem-m">' + esc(p.t) + ' · ' + esc(p.h) + '</span></button>';
    }).join('');
    draw(list);
  }

  /* ── detail panel ────────────────────────────────────────────────── */
  var cache = {}, cur = null;

  function open(slug) {
    var p = BY[slug]; if (!p) return;
    cur = slug;
    var panel = $('exppanel');
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
      '<div class="exptags"><span class="tag">' + esc(d.t) + '</span>' +
      (d.unesco ? '<span class="tag u">UNESCO</span>' : '') +
      '<span class="tag g">' + esc(d.gn) + '</span></div>' +
      '<div class="expact">' +
      '<button class="btn sm" data-set="from">' + esc(U.set_start) + '</button>' +
      '<button class="btn sm alt" data-set="to">' + esc(U.set_end) + '</button>' +
      '<a class="btn sm ghost" href="' + esc(d.u) + '">' + esc(U.full_page) + '</a></div>' +
      '<dl class="facts">' + facts + '</dl>' +
      '<div class="article">' + d.body + '</div>' +
      (d.tip ? '<h4>' + esc(U.tip_title) + '</h4><div class="article">' + d.tip + '</div>' : '') +
      (d.route ? '<h4>' + esc(U.route_title) + '</h4><div class="article">' + d.route + '</div>' : '') +
      (near ? '<h4>' + esc(U.nearby_title) + '</h4><div class="chips">' + near + '</div>' : '');
  }

  function close() {
    cur = null;
    var panel = $('exppanel');
    panel.classList.remove('on');
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
    /* detour is measured geometrically so it can never come out negative */
    var base = hav(a.la, a.lo, b.la, b.lo), out = [];
    PTS.forEach(function (p) {
      if (p.s === a.s || p.s === b.s) return;
      var da = hav(a.la, a.lo, p.la, p.lo), db = hav(p.la, p.lo, b.la, b.lo);
      var det = (da + db - base) * 1.35;          /* straight line -> road */
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
    L.polyline(seq.map(function (p) { return [p.la, p.lo]; }),
      { color: '#0f4c81', weight: 4, opacity: .85, lineCap: 'round' }).addTo(routeLayer);
    seq.forEach(function (p, i) {
      L.circleMarker([p.la, p.lo], {
        radius: 9, color: '#0f4c81', weight: 3,
        fillColor: i === 0 ? '#1a7f5a' : (i === seq.length - 1 ? '#c0392b' : '#fff'),
        fillOpacity: 1
      }).addTo(routeLayer).bindTooltip((i + 1) + '. ' + p.n);
    });
    map.fitBounds(L.latLngBounds(seq.map(function (p) { return [p.la, p.lo]; })).pad(0.12));

    var days = Math.max(1, Math.ceil((drive + visit) / (9 * 60)));
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
  }

  /* ── autocomplete for the two endpoint inputs ────────────────────── */
  function suggest(which) {
    var inp = $('exp' + which), box = $('exp' + which + 'list');
    var q = norm(inp.value);
    if (!q) { box.innerHTML = ''; box.classList.remove('on'); return; }
    var hits = ALL.filter(function (p) { return norm(p.n).indexOf(q) >= 0; });
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

  /* ── wiring ──────────────────────────────────────────────────────── */
  $('expq').addEventListener('input', function () { state.q = this.value; renderList(); });
  $('exptype').addEventListener('change', function () { state.type = this.value; renderList(); });
  $('expregion').addEventListener('change', function () { state.region = this.value; renderList(); });
  $('expreset').addEventListener('click', function () {
    state.q = ''; state.type = ''; state.region = '';
    $('expq').value = ''; $('exptype').value = ''; $('expregion').value = '';
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
  });
  $('expclose').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-s],[data-go],[data-set],[data-pick]') : null;
    if (!t) return;
    if (t.hasAttribute('data-pick')) {
      setEnd(t.getAttribute('data-pick'), t.getAttribute('data-s'));
      $('exp' + t.getAttribute('data-pick') + 'list').classList.remove('on');
      return;
    }
    if (t.hasAttribute('data-set')) { if (cur) setEnd(t.getAttribute('data-set'), cur); return; }
    if (t.hasAttribute('data-go')) { open(t.getAttribute('data-go')); return; }
    if (t.classList.contains('expitem')) { open(t.getAttribute('data-s')); }
  });

  renderList();
  route();
})();
