/* ტურის დამგეგმავი — მთლიანად ბრაუზერში მუშაობს, სერვერის გარეშე.
   მონაცემები: /assets/planner-<lang>.json (build.py-ს გენერირებული) */
(function () {
  "use strict";
  var D = window.PLANNER_DATA, T = D.t, EL = function (id) { return document.getElementById(id); };
  var map, layers = [], DAY_COLORS = ["#0f4c81", "#c8963e", "#1d7a53", "#8e6bb5", "#b5563f",
                                      "#2b8a9e", "#8f2f52", "#4a76b5", "#3f8f5f", "#a0703c"];

  // ─── გეომეტრია და დროის მოდელი ──────────────────────────────────────────
  function hav(a, b) {
    var R = 6371, p1 = a.lat * Math.PI / 180, p2 = b.lat * Math.PI / 180,
        dp = p2 - p1, dl = (b.lon - a.lon) * Math.PI / 180;
    var h = Math.sin(dp / 2) * Math.sin(dp / 2) +
            Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) * Math.sin(dl / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  /* საგზაო კმ და წუთი ორ წერტილს შორის.
     თითოეულ ობიექტს აქვს f (გზის კლაკნილობა) და v (საშუალო სიჩქარე),
     გამოთვლილი თბილისიდან რეალურ მანძილსა და დროზე დაყრდნობით. */
  function leg(a, b) {
    var d = hav(a, b);
    var f = ((a.f || 1.4) + (b.f || 1.4)) / 2;
    var v = ((a.v || 55) + (b.v || 55)) / 2;
    var km = d * f;
    if (km < 12) v = Math.min(v, 32);            // ქალაქში ნელა
    return { km: km, min: km / v * 60 };
  }
  function fmtH(m) {
    m = Math.round(m);
    var h = Math.floor(m / 60), r = m % 60;
    return h ? (h + " " + T.hours + (r ? " " + r + " " + T.min : "")) : (r + " " + T.min);
  }
  function clock(m) {
    m = Math.round(m) % (24 * 60);
    return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
  }

  // ─── ფილტრაცია ──────────────────────────────────────────────────────────
  var CAR_RANK = { economy: 0, suv: 1, offroad: 2 };
  function seasonOK(a, month) {
    if (a.season === "all") return true;
    if (a.season === "may-october") return month >= 5 && month <= 10;
    if (a.season === "june-september") return month >= 6 && month <= 9;
    if (a.season === "december-march") return month === 12 || month <= 3;
    return true;
  }
  function pick() {
    var regions = chips("regions"), types = chips("interests"),
        car = EL("car").value, month = parseInt(EL("month").value, 10);
    return D.a.filter(function (a) {
      if (regions.length && regions.indexOf(a.r) < 0) return false;
      if (types.length && types.indexOf(a.ty) < 0) return false;
      if (CAR_RANK[a.car] > CAR_RANK[car]) return false;
      if (!seasonOK(a, month)) return false;
      return true;
    });
  }
  function chips(name) {
    return Array.prototype.slice
      .call(document.querySelectorAll('[data-chip="' + name + '"].on'))
      .map(function (e) { return e.dataset.val; });
  }

  // ─── მარშრუტის აგება ────────────────────────────────────────────────────
  function nearestNeighbour(start, pts) {
    var out = [], cur = start, left = pts.slice();
    while (left.length) {
      var bi = 0, bd = Infinity;
      for (var i = 0; i < left.length; i++) {
        var d = hav(cur, left[i]);
        if (d < bd) { bd = d; bi = i; }
      }
      cur = left[bi]; out.push(cur); left.splice(bi, 1);
    }
    return out;
  }
  function twoOpt(start, route, back) {
    function cost(r) {
      var c = 0, prev = start;
      for (var i = 0; i < r.length; i++) { c += hav(prev, r[i]); prev = r[i]; }
      if (back) c += hav(prev, start);
      return c;
    }
    var best = route.slice(), bc = cost(best), improved = true, guard = 0;
    while (improved && guard++ < 40) {
      improved = false;
      for (var i = 0; i < best.length - 1; i++) {
        for (var j = i + 1; j < best.length; j++) {
          var cand = best.slice(0, i).concat(best.slice(i, j + 1).reverse(), best.slice(j + 1));
          var cc = cost(cand);
          if (cc < bc - 0.001) { best = cand; bc = cc; improved = true; }
        }
      }
    }
    return best;
  }
  /* ობიექტების შერჩევა: ჯერ გამორჩეულები და UNESCO, მერე „ღირებულება დროზე“ */
  function score(a, start) {
    var s = 0;
    if (a.fe) s += 3;
    if (a.un) s += 3;
    s += 2 / Math.max(a.h, 0.5);                 // მოკლე ვიზიტი — მეტი ეტევა
    s -= hav(start, a) / 220;                    // შორეული — ნაკლებად
    return s;
  }

  var DAY_START = 9 * 60, LUNCH = 45;

  /* მარშრუტის აგება ჩასმის ევრისტიკით: ყოველ ბიჯზე ვამატებთ იმ ობიექტს,
     რომელიც საუკეთესო შეფარდებას იძლევა „ღირებულება / დამატებული დრო“.
     ეს ბუნებრივად აჯგუფებს ახლომდებარე ადგილებს — არა უბრალოდ საუკეთესოებს
     მთელი ქვეყნის მასშტაბით. */
  function routeTime(r, start, back) {
    var t = 0, prev = start;
    for (var i = 0; i < r.length; i++) { t += leg(prev, r[i]).min + r[i].h * 60; prev = r[i]; }
    if (back) t += leg(prev, start).min;
    return t;
  }
  function buildRoute(pool, start, days, budget, back) {
    var cap = days * budget * 0.94;
    var cand = pool.slice().sort(function (x, y) { return score(y, start) - score(x, start); })
                   .slice(0, 45);
    var route = [], used = 0, guard = 0;
    while (guard++ < 40) {
      var bg = -Infinity, bi = -1, bp = -1, bt = 0;
      for (var i = 0; i < cand.length; i++) {
        for (var pos = 0; pos <= route.length; pos++) {
          var trial = route.slice(0, pos).concat([cand[i]], route.slice(pos));
          var t = routeTime(trial, start, back);
          if (t > cap) continue;
          var gain = score(cand[i], start) / Math.max(t - used, 25);
          if (gain > bg) { bg = gain; bi = i; bp = pos; bt = t; }
        }
      }
      if (bi < 0) break;
      route.splice(bp, 0, cand[bi]);
      cand.splice(bi, 1);
      used = bt;
    }
    return twoOpt(start, route, back);
  }

  function splitDays(route, start, days, budget, back) {
    var out = [], cur = start, day = { i: 1, items: [], km: 0, drive: 0, visit: 0 },
        used = 0, clockNow = DAY_START, lunched = false, left = route.slice(), dropped = [];
    while (left.length && day.i <= days) {
      var nx = left[0], L = leg(cur, nx), visit = nx.h * 60;
      var lunch = (day.items.length && !lunched && clockNow + L.min > 13 * 60) ? LUNCH : 0;
      var extra = L.min + visit + lunch;
      if (used + extra > budget && day.items.length) {
        out.push(day);
        day = { i: day.i + 1, items: [], km: 0, drive: 0, visit: 0 };
        used = 0; clockNow = DAY_START; lunched = false;
        if (day.i > days) break;
        continue;
      }
      if (used + extra > budget * 1.3 && !day.items.length) { dropped.push(nx); left.shift(); continue; }
      clockNow += L.min;
      if (lunch) { clockNow += lunch; used += lunch; lunched = true; }
      var arrive = clockNow;
      clockNow += visit;
      day.items.push({ a: nx, legKm: L.km, legMin: L.min, arrive: arrive, depart: clockNow, visit: visit });
      day.km += L.km; day.drive += L.min; day.visit += visit;
      used += L.min + visit;
      cur = nx; left.shift();
    }
    if (day.items.length) out.push(day);
    dropped = dropped.concat(left);
    if (back && out.length) {
      var last = out[out.length - 1], la = last.items[last.items.length - 1];
      var R = leg(la.a, start);
      last.back = { km: R.km, min: R.min, arrive: la.depart + R.min };
      last.km += R.km; last.drive += R.min;
    }
    return { days: out, dropped: dropped };
  }

  function plan(all, start, days, budgetMin, back) {
    return splitDays(buildRoute(all, start, days, budgetMin, back), start, days, budgetMin, back);
  }

  /* გზაში გასაჩერებელი ადგილები: ობიექტები, რომლებიც ახლოსაა
     A→B მონაკვეთთან და გეგმაში არ არიან */
  function alongTheWay(a, b, exclude, pool) {
    var res = [];
    for (var i = 0; i < pool.length; i++) {
      var p = pool[i];
      if (exclude.indexOf(p.s) >= 0) continue;
      var dAB = hav(a, b);
      if (dAB < 12) continue;
      var d = hav(a, p) + hav(p, b) - dAB;        // შემოვლის დანამატი
      if (d < Math.min(18, dAB * 0.22)) res.push({ p: p, detour: d });
    }
    return res.sort(function (x, y) { return x.detour - y.detour; }).slice(0, 3);
  }

  // ─── რენდერი ────────────────────────────────────────────────────────────
  function render(res, start, pool) {
    var box = EL("result");
    if (!res.days.length) { box.innerHTML = '<div class="note">' + T.no_results + "</div>"; drawMap([], start); return; }
    var totKm = 0, totDrive = 0, totVisit = 0, stops = 0, maxCar = "economy";
    res.days.forEach(function (d) {
      totKm += d.km; totDrive += d.drive; totVisit += d.visit; stops += d.items.length;
      d.items.forEach(function (it) {
        if (CAR_RANK[it.a.car] > CAR_RANK[maxCar]) maxCar = it.a.car;
      });
    });

    var h = '<dl class="facts">' +
      f(T.day, res.days.length) + f(T.stops, stops) +
      f(T.distance, Math.round(totKm) + " " + T.km) +
      f(T.driving_time, fmtH(totDrive)) + f(T.visiting_time, fmtH(totVisit)) +
      f(T.need_car, D.car[maxCar]) + "</dl>";

    h += '<div class="cta" style="margin:0 0 26px"><h2>' + T.book_cta + "</h2><p>" + T.book_text +
         '</p><div class="row"><a class="btn" href="' + D.url.contact + '">' + D.nav.contact +
         '</a><a class="btn ghost" href="' + D.url.fleet + '">' + D.nav.fleet + "</a></div></div>";

    h += "<h2>" + T.day_plan + "</h2>";
    res.days.forEach(function (d, di) {
      var col = DAY_COLORS[di % DAY_COLORS.length];
      h += '<div class="pday"><h3><span class="pdot" style="background:' + col + '"></span>' +
           T.day + " " + d.i + ' <small>' + Math.round(d.km) + " " + T.km + " · " +
           T.drive + " " + fmtH(d.drive) + " · " + T.visit + " " + fmtH(d.visit) + "</small></h3>";
      h += '<ol class="pstops">';
      var prev = di === 0 ? start : res.days[di - 1].items.slice(-1)[0].a;
      d.items.forEach(function (it, ii) {
        h += "<li><div class=\"pleg\">" + T.drive + " " + Math.round(it.legKm) + " " + T.km +
             " · " + fmtH(it.legMin) + "</div>" +
             '<div class="pstop"><b><a href="' + it.a.u + '">' + esc(it.a.n) + "</a></b>" +
             '<span class="pmeta">' + T.arrive + " " + clock(it.arrive) + " · " + T.visit + " " +
             fmtH(it.visit) + " · " + T.depart + " " + clock(it.depart) + "</span>" +
             '<span class="pshort">' + esc(it.a.sh) + "</span></div>";
        var opt = alongTheWay(prev, it.a, planSlugs(res), pool);
        if (opt.length) {
          h += '<div class="popt">' + T.optional + ": " +
               opt.map(function (o) {
                 return '<a href="' + o.p.u + '">' + esc(o.p.n) + "</a> <i>+" +
                        fmtH(leg(prev, o.p).min * 0.35 + o.p.h * 60) + "</i>";
               }).join(" · ") + "</div>";
        }
        h += "</li>";
        prev = it.a;
      });
      if (d.back) {
        h += '<li><div class="pleg">' + T.back_to + " " + esc(start.n) + " — " +
             Math.round(d.back.km) + " " + T.km + " · " + fmtH(d.back.min) +
             " · " + T.arrive + " " + clock(d.back.arrive) + "</div></li>";
      }
      h += "</ol>";
      var lastA = d.items.slice(-1)[0].a;
      if (di < res.days.length - 1) h += '<div class="pnight">' + T.overnight + ": " + esc(nearestTown(lastA).c) + "</div>";
      h += "</div>";
    });
    if (res.dropped.length) h += '<div class="note">' + T.too_far + "</div>";
    h += '<p><button class="btn ghost" onclick="window.print()">' + T.print + "</button></p>";
    box.innerHTML = h;
    drawMap(res.days, start);
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function f(k, v) { return "<div><dt class=\"k\">" + k + '</dt><dd class="v">' + v + "</dd></div>"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function planSlugs(res) {
    var out = []; res.days.forEach(function (d) { d.items.forEach(function (i) { out.push(i.a.s); }); }); return out;
  }
  function nearestTown(a) {
    var towns = D.a.filter(function (x) { return x.c; });
    if (!towns.length) return { c: a.n };
    return towns.reduce(function (b, x) { return hav(a, x) < hav(a, b) ? x : b; });
  }

  function drawMap(days, start) {
    layers.forEach(function (l) { map.removeLayer(l); });
    layers = [];
    var all = [[start.lat, start.lon]];
    var m0 = L.circleMarker([start.lat, start.lon],
      { radius: 9, color: "#fff", weight: 3, fillColor: "#12181f", fillOpacity: 1 }).addTo(map);
    m0.bindTooltip(start.n); layers.push(m0);
    days.forEach(function (d, di) {
      var col = DAY_COLORS[di % DAY_COLORS.length];
      var pts = [di === 0 ? [start.lat, start.lon] :
                 [days[di - 1].items.slice(-1)[0].a.lat, days[di - 1].items.slice(-1)[0].a.lon]];
      d.items.forEach(function (it, ii) {
        pts.push([it.a.lat, it.a.lon]);
        all.push([it.a.lat, it.a.lon]);
        var mk = L.circleMarker([it.a.lat, it.a.lon],
          { radius: 8, color: "#fff", weight: 2, fillColor: col, fillOpacity: 1 }).addTo(map);
        mk.bindPopup("<b><a href=\"" + it.a.u + "\">" + esc(it.a.n) + "</a></b><br>" +
                     T.day + " " + d.i + " · " + clock(it.arrive) + "–" + clock(it.depart) +
                     "<br>" + T.visit + " " + fmtH(it.visit));
        mk.bindTooltip(T.day + " " + d.i + ": " + it.a.n);
        layers.push(mk);
      });
      if (d.back) pts.push([start.lat, start.lon]);
      var pl = L.polyline(pts, { color: col, weight: 4, opacity: 0.8 }).addTo(map);
      layers.push(pl);
    });
    if (all.length > 1) map.fitBounds(L.latLngBounds(all).pad(0.15));
  }

  // ─── ინტერფეისი ─────────────────────────────────────────────────────────
  function buildForm() {
    var s = EL("start");
    D.starts.forEach(function (p, i) {
      var o = document.createElement("option");
      o.value = i; o.textContent = p.n; s.appendChild(o);
    });
    var m = EL("month"), now = new Date().getMonth() + 1;
    T.months.forEach(function (name, i) {
      var o = document.createElement("option");
      o.value = i + 1; o.textContent = name; if (i + 1 === now) o.selected = true;
      m.appendChild(o);
    });
    chipRow("regions", D.regions);
    chipRow("interests", D.types);
  }
  function chipRow(name, items) {
    var box = EL(name);
    items.forEach(function (it) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.dataset.chip = name; b.dataset.val = it.k;
      b.textContent = it.n;
      b.onclick = function () { b.classList.toggle("on"); updateChipLabel(name); };
      box.appendChild(b);
    });
  }
  function updateChipLabel(name) {
    var n = chips(name).length, lab = EL(name + "-count");
    if (lab) lab.textContent = n ? "(" + n + ")" : "";
  }

  function run() {
    var start = D.starts[parseInt(EL("start").value, 10)];
    var days = parseInt(EL("days").value, 10);
    var budget = parseInt(EL("pace").value, 10);
    var back = EL("back").checked;
    var pool = pick();
    if (!pool.length) { EL("result").innerHTML = '<div class="note">' + T.no_results + "</div>"; return; }
    render(plan(pool, start, days, budget, back), start, D.a);
  }

  function init() {
    buildForm();
    map = L.map("pmap", { scrollWheelZoom: false }).setView([42.1, 43.6], 7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      { maxZoom: 17, attribution: "&copy; OpenStreetMap" }).addTo(map);
    map.on("click", function () { map.scrollWheelZoom.enable(); });
    EL("build").onclick = run;
    EL("reset").onclick = function () {
      document.querySelectorAll(".chip.on").forEach(function (c) { c.classList.remove("on"); });
      updateChipLabel("regions"); updateChipLabel("interests");
      EL("result").innerHTML = ""; drawMap([], D.starts[parseInt(EL("start").value, 10)]);
    };
    run();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
