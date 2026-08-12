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
        '<span class="expitem-m">' + esc(p.t) + ' · ' + esc(p.h) +
        (p.r ? ' · ★' + p.r : '') + '</span></button>';
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


  /* ── ჩემი ადგილი, დროის/მანძილის ფილტრი და რუკაზე მოხაზვა ─────────── */
  var me = null, area = null, areaLayer = null, drawing = false;

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
    minutes = chainTime(o, chosen);

    box.innerHTML =
      '<div class="exptot"><b>' + chosen.length + '</b><span>' + esc(U.suggest) + '</span>' +
      (mode === 'time' ? '<span>' + fmtH(minutes) + ' / ' + val + ' ' + esc(U.hrs) + '</span>'
                       : '<span>≤ ' + val + ' ' + esc(U.km) + '</span>') + '</div>' +
      '<ol class="expstops">' + chosen.map(function (p) {
        return '<li><button class="lnk" type="button" data-go="' + esc(p.s) + '">' + esc(p.n) +
          '</button><span class="expmeta">' + esc(p.t) + ' · ' + esc(p.h) + ' · ' +
          Math.round(leg(o, p).km) + ' ' + esc(U.km) + '</span></li>';
      }).join('') + '</ol>';
    drawSuggest(o, chosen);
  }

  /* nearest-neighbour + 2-opt — გონივრული თანმიმდევრობა */
  function order2opt(o, list) {
    if (list.length < 3) return list.slice();
    var left = list.slice(), out = [], cur = o;
    while (left.length) {
      var bi = 0, bd = Infinity;
      for (var i = 0; i < left.length; i++) {
        var d = hav(cur.la, cur.lo, left[i].la, left[i].lo);
        if (d < bd) { bd = d; bi = i; }
      }
      cur = left[bi]; out.push(cur); left.splice(bi, 1);
    }
    function cost(r) {
      var c = 0, prev = o;
      for (var i = 0; i < r.length; i++) { c += hav(prev.la, prev.lo, r[i].la, r[i].lo); prev = r[i]; }
      c += hav(prev.la, prev.lo, o.la, o.lo);
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
  function drawSuggest(o, list) {
    sugLayer.clearLayers();
    if (!list.length) return;
    var pts = [[o.la, o.lo]].concat(list.map(function (p) { return [p.la, p.lo]; }));
    pts.push([o.la, o.lo]);
    L.polyline(pts, { color: '#2dd4bf', weight: 3, opacity: .8 }).addTo(sugLayer);
    list.forEach(function (p, i) {
      L.marker([p.la, p.lo], { icon: L.divIcon({ className: 'numpin',
        html: '<b>' + (i + 1) + '</b>', iconSize: [22, 22] }) }).addTo(sugLayer)
        .bindTooltip(p.n).on('click', function () { open(p.s); });
    });
    L.circleMarker([o.la, o.lo], { radius: 9, color: '#2dd4bf', weight: 3,
      fillColor: '#0b1220', fillOpacity: 1 }).addTo(sugLayer);
    map.fitBounds(L.latLngBounds(pts).pad(0.15));
  }

  function locate() {
    var b = $('expgeo');
    if (!navigator.geolocation) { b.textContent = U.loc_err; return; }
    b.textContent = U.locating;
    navigator.geolocation.getCurrentPosition(function (pos) {
      me = { s: 'me', n: U.my_loc, la: pos.coords.latitude, lo: pos.coords.longitude,
             f: 1.4, v: 55, hh: 0 };
      BY.me = me;
      b.textContent = '◎ ' + U.my_loc;
      b.classList.add('on');
      L.circleMarker([me.la, me.lo], { radius: 8, color: '#2dd4bf', weight: 3,
        fillColor: '#fff', fillOpacity: 1 }).addTo(sugLayer).bindTooltip(U.my_loc);
      map.setView([me.la, me.lo], 9);
      suggestNear();
    }, function () {
      b.textContent = U.loc_fallback || U.loc_err;
      pickLoc = true;
      document.getElementById('expmap').classList.add('drawing');
    }, { timeout: 10000, enableHighAccuracy: false });
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
      wps = [first].concat(order2opt(first, wps.slice(1)));
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
    L.polyline(wps.map(function (p) { return [p.la, p.lo]; }),
      { color: '#38bdf8', weight: 4, opacity: .85 }).addTo(wpLayer);
    wps.forEach(function (p, i) {
      L.marker([p.la, p.lo], { icon: L.divIcon({ className: 'numpin blue',
        html: '<b>' + (i + 1) + '</b>', iconSize: [22, 22] }) }).addTo(wpLayer).bindTooltip(p.n);
    });
    if (wps.length > 1)
      map.fitBounds(L.latLngBounds(wps.map(function (p) { return [p.la, p.lo]; })).pad(0.2));
  }

  /* ── wiring ──────────────────────────────────────────────────────── */
  $('expq').addEventListener('input', function () { state.q = this.value; renderList(); });
  $('exptype').addEventListener('change', function () { state.type = this.value; renderList(); suggestNear(); });
  $('expregion').addEventListener('change', function () { state.region = this.value; renderList(); suggestNear(); });
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
  suggestNear();
})();
