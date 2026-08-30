/* RentUp — day-trip finder.
 *
 * "I'm free today. I haven't seen that church nearby. What else fits?"
 *
 * Everything here runs on the same data the rest of the site publishes:
 * window.EXP holds every place with lat/lon, type, hours needed, the road's
 * measured winding factor (f) and its measured average speed (v), both derived
 * from the real distance and drive time from Tbilisi. So a drive-time estimate
 * from any starting point uses that place's own road behaviour, not a guess.
 *
 * Estimates are labelled as estimates in the UI. We never present them as
 * routed driving directions.
 */
(function () {
  "use strict";

  var T = window.DAYTRIP_T || {};
  // window.EXP is {pts:[…], …} — the explorer config, not a bare array.
  var EXP = (window.EXP && window.EXP.pts) || (Array.isArray(window.EXP) ? window.EXP : []);
  var root = document.getElementById("daytrip");
  if (!root || !EXP.length) return;

  var R = 6371;
  function hav(a, b, c, d) {
    var p = Math.PI / 180;
    var x = 0.5 - Math.cos((c - a) * p) / 2 +
            Math.cos(a * p) * Math.cos(c * p) * (1 - Math.cos((d - b) * p)) / 2;
    return 2 * R * Math.asin(Math.sqrt(x));
  }

  // Road distance and drive time from an origin, using this place's own
  // measured winding factor and average speed.
  function leg(from, p) {
    var straight = hav(from.la, from.lo, p.la, p.lo);
    var km = straight * (p.f || 1.5);
    return { km: km, h: km / (p.v || 50) };
  }

  // The shared map index stays lightweight and ships no per-place URL, so we
  // build it from the slug and this language's attraction prefix.
  function placeUrl(p) {
    return p.u || ((T.attr_prefix || "/attractions/") + p.s + "/");
  }

  function fmtH(h) {
    var m = Math.round(h * 60);
    return Math.floor(m / 60) + ":" + String(m % 60).padStart(2, "0");
  }

  // ── month → which places are actually worth going to now ────────────────
  var MONTHS = {
    "all": null, "year-round": null,
    "april-october": [4, 10], "may-october": [5, 10], "june-september": [6, 9],
    "july-september": [7, 9], "march-november": [3, 11], "december-march": [12, 3]
  };
  function inSeason(p, month) {
    var w = MONTHS[p.bs];
    if (!w) return true;
    var a = w[0], b = w[1];
    return a <= b ? (month >= a && month <= b) : (month >= a || month <= b);
  }

  // ── state ───────────────────────────────────────────────────────────────
  var st = {
    from: null,          // {la, lo, name}
    people: 2,
    types: [],
    hours: 5,
    month: new Date().getMonth() + 1
  };

  var $ = function (sel) { return root.querySelector(sel); };
  var $$ = function (sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); };

  // ── the plan ────────────────────────────────────────────────────────────
  // Pick the best headline destination, then greedily add stops that still fit
  // the remaining budget, preferring ones close to what we already have.
  function plan() {
    if (!st.from) return null;
    var budget = st.hours;
    var pool = EXP.filter(function (p) {
      if (st.types.length && st.types.indexOf(p.ty) < 0) return false;
      if (!inSeason(p, st.month)) return false;
      return true;
    }).map(function (p) {
      var l = leg(st.from, p);
      return { p: p, km: l.km, h: l.h };
    }).filter(function (c) {
      // must be reachable there and back with time left to actually look at it
      if (c.h * 2 + c.p.hh > budget) return false;
      // With no interest chosen the question is "where do I go today", so the
      // answer has to involve going somewhere: require a drive proportional to
      // the day. (A three-hour window still allows the church down the road.)
      // When an interest IS chosen we honour it — someone who picks "theatre"
      // wants the theatre, however close it is.
      if (!st.types.length && c.h < budget * 0.06) return false;
      return true;
    });
    if (!pool.length) return null;

    // Score: how well the trip uses the day, then how good the place is.
    // A flat distance penalty made a 12-minute city walk win a nine-hour day,
    // which is not what someone with a free day is asking for. Instead we aim
    // to fill about three quarters of the budget: with three hours that picks
    // the church down the road, with nine it picks somewhere worth the drive.
    var TARGET = 0.72;
    function score(c) {
      var frac = (c.h * 2 + c.p.hh) / budget;
      return (c.p.r || 3) - Math.abs(frac - TARGET) * 6;
    }
    pool.sort(function (a, b) { return score(b) - score(a); });

    var head = pool[0];
    var stops = [head];
    var used = head.h * 2 + head.p.hh;
    var seen = {};
    seen[head.p.s] = 1;

    // Add detours that are genuinely on the way: cost is the extra driving.
    for (var round = 0; round < 4; round++) {
      var best = null, bestCost = Infinity;
      for (var i = 0; i < pool.length; i++) {
        var c = pool[i];
        if (seen[c.p.s]) continue;
        var last = stops[stops.length - 1].p;
        var d = hav(last.la, last.lo, c.p.la, c.p.lo) * (c.p.f || 1.5);
        var extra = d / (c.p.v || 50) + c.p.hh;
        // returning home from the new last stop instead of the old one
        var back = leg(st.from, c.p).h - leg(st.from, last).h;
        var cost = extra + back;
        if (used + cost <= budget && cost < bestCost) { best = c; bestCost = cost; }
      }
      if (!best) break;
      stops.push(best);
      seen[best.p.s] = 1;
      used += bestCost;
    }

    // The car has to satisfy two independent things: the roughest road on the
    // trip, and how many people are travelling. They can conflict — a group of
    // seven heading somewhere that needs a 4x4 cannot do both in one vehicle —
    // so say that plainly rather than quietly recommending the wrong car.
    var carRank = { economy: 0, suv: 1, offroad: 2 };
    var roadCar = stops.reduce(function (acc, s) {
      return (carRank[s.p.cc] || 0) > (carRank[acc] || 0) ? s.p.cc : acc;
    }, "economy");
    var seatCar = st.people >= 7 ? "minivan" : (st.people >= 4 ? "suv" : "economy");
    var car = roadCar, conflict = false;
    if (seatCar === "minivan") {
      if (roadCar === "offroad") { conflict = true; }   // seats vs clearance
      else { car = "minivan"; }
    } else if ((carRank[seatCar] || 0) > (carRank[roadCar] || 0)) {
      car = seatCar;
    }

    var totalKm = stops.reduce(function (a, s, i) {
      if (i === 0) return s.km;
      var prev = stops[i - 1].p;
      return a + hav(prev.la, prev.lo, s.p.la, s.p.lo) * (s.p.f || 1.5);
    }, 0) + stops[stops.length - 1].km;

    return { stops: stops, hours: used, km: totalKm, car: car, conflict: conflict };
  }

  // ── rendering ───────────────────────────────────────────────────────────
  function render() {
    var out = $("#dt-result");
    if (!st.from) {
      out.innerHTML = '<p class="dt-hint">' + esc(T.pick_start || "Choose where you are starting from.") + "</p>";
      return;
    }
    var r = plan();
    if (!r) {
      out.innerHTML = '<p class="dt-hint">' + esc(T.nothing || "Nothing fits that combination — try more hours or another interest.") + "</p>";
      return;
    }
    var head = r.stops[0].p;
    var rest = r.stops.slice(1);
    var h = "";
    h += '<div class="dt-head"><span class="tag">' + esc(T.best || "Best today") + "</span>" +
         "<h3><a href=\"" + placeUrl(head) + "\">" + esc(head.n) + "</a></h3>" +
         '<p class="dt-meta">' + esc(head.t) + " · " + esc(head.gn) + " · " +
         Math.round(r.stops[0].km) + " " + esc(T.km || "km") + " · " +
         fmtH(r.stops[0].h) + " " + esc(T.drive || "drive") + "</p></div>";

    if (rest.length) {
      h += "<h4>" + esc(T.also || "Also fits in your day") + "</h4><ul class=\"linklist\">";
      rest.forEach(function (s) {
        h += "<li><a href=\"" + placeUrl(s.p) + "\">" + esc(s.p.n) + "</a> <small>" +
             esc(s.p.t) + " · " + s.p.hh + " " + esc(T.h || "h") + "</small></li>";
      });
      h += "</ul>";
    }

    h += '<dl class="facts dt-facts">' +
         fact(T.total_drive || "Driving", fmtH(r.hours - r.stops.reduce(function (a, s) { return a + s.p.hh; }, 0))) +
         fact(T.total_km || "Distance", Math.round(r.km) + " " + esc(T.km || "km")) +
         fact(T.day_total || "Whole day", fmtH(r.hours)) +
         fact(T.car_needed || "Car you need",
              '<a href="' + (T.car_urls || {})[r.car] + '">' + esc((T.car_names || {})[r.car] || r.car) + "</a>") +
         "</dl>";

    if (r.conflict) {
      h += '<p class="dt-note dt-warn">' + esc(T.seat_conflict ||
           "This route needs a 4x4, and a 4x4 does not seat your group — you would need two cars.") + "</p>";
    }
    h += '<p class="dt-note">' + esc(T.estimate ||
         "Drive times are estimates from the measured road speed to each place, not routed directions.") + "</p>";

    var slugs = r.stops.map(function (s) { return s.p.s; }).join(",");
    h += '<div class="row"><a class="btn" href="' + (T.planner_url || "/map/") + "#stops=" + slugs + '">' +
         esc(T.open_planner || "Open in the planner") + "</a>" +
         '<a class="btn ghost" href="' + ((T.car_urls || {})[r.car] || "/car-rental/") + '">' +
         esc(T.book_car || "Rent the car for it") + "</a></div>";
    out.innerHTML = h;
  }

  function fact(k, v) {
    return '<div><dt class="k">' + esc(k) + '</dt><dd class="v">' + v + "</dd></div>";
  }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // ── inputs ──────────────────────────────────────────────────────────────
  $$("[data-dt-city]").forEach(function (b) {
    b.addEventListener("click", function () {
      $$("[data-dt-city]").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      st.from = { la: parseFloat(b.dataset.la), lo: parseFloat(b.dataset.lo), name: b.textContent };
      render();
    });
  });

  var geo = $("#dt-geo");
  if (geo) {
    if (!navigator.geolocation) geo.style.display = "none";
    geo.addEventListener("click", function () {
      geo.disabled = true;
      geo.textContent = T.locating || "Locating…";
      navigator.geolocation.getCurrentPosition(function (pos) {
        st.from = { la: pos.coords.latitude, lo: pos.coords.longitude, name: T.you_are_here || "Your location" };
        $$("[data-dt-city]").forEach(function (x) { x.classList.remove("on"); });
        geo.classList.add("on");
        geo.disabled = false;
        geo.textContent = T.you_are_here || "Your location";
        render();
      }, function () {
        geo.disabled = false;
        geo.textContent = T.geo_failed || "Couldn't get your location — pick a city";
      }, { timeout: 8000, maximumAge: 300000 });
    });
  }

  $$("[data-dt-type]").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = b.dataset.dtType;
      var i = st.types.indexOf(t);
      if (i < 0) { st.types.push(t); b.classList.add("on"); }
      else { st.types.splice(i, 1); b.classList.remove("on"); }
      render();
    });
  });

  $$("[data-dt-hours]").forEach(function (b) {
    b.addEventListener("click", function () {
      $$("[data-dt-hours]").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      st.hours = parseFloat(b.dataset.dtHours);
      render();
    });
  });

  $$("[data-dt-people]").forEach(function (b) {
    b.addEventListener("click", function () {
      $$("[data-dt-people]").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      st.people = parseInt(b.dataset.dtPeople, 10);
      render();
    });
  });

  render();
})();
