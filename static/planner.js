/* ტურის დამგეგმავი — მთლიანად ბრაუზერში მუშაობს, სერვერის გარეშე.
   მონაცემები: /assets/planner-<lang>.json (build.py-ს გენერირებული) */
(function () {
  "use strict";
  var D = window.PLANNER_DATA, T = D.t, EL = function (id) { return document.getElementById(id); };
  var UI_LANG = (document.documentElement.lang || "en").slice(0, 2);
  var CAR_COPY = {
    ka: { transport:"ტრანსპორტი", own:"ჩემი მანქანით", ownSaved:"მარშრუტი თქვენი ავტომობილისთვის დაიგეგმა. არჩევანის შეცვლა ნებისმიერ დროს შეგიძლიათ.", driver:"მძღოლით" },
    en: { transport:"Transport", own:"My own car", ownSaved:"This route is planned for your own vehicle. You can change this choice at any time.", driver:"With driver" },
    ru: { transport:"Транспорт", own:"На своей машине", ownSaved:"Маршрут рассчитан для вашего автомобиля. Выбор можно изменить в любое время.", driver:"С водителем" },
    fa: { transport:"حمل‌ونقل", own:"با خودروی خودم", ownSaved:"این مسیر برای خودروی شما برنامه‌ریزی شده است و هر زمان می‌توانید انتخاب را تغییر دهید.", driver:"با راننده" },
    he: { transport:"תחבורה", own:"ברכב שלי", ownSaved:"המסלול תוכנן לרכב שלך. אפשר לשנות את הבחירה בכל עת.", driver:"עם נהג" },
    ar: { transport:"وسيلة النقل", own:"بسيارتي", ownSaved:"تم تخطيط المسار لسيارتك ويمكنك تغيير هذا الاختيار في أي وقت.", driver:"مع سائق" }
  };
  function carCopy(key, fallback) { return (CAR_COPY[UI_LANG] || CAR_COPY.en)[key] || fallback; }
  window.FH_BRAND_LOGO = window.FH_BRAND_LOGO || new Image();
  if (!window.FH_BRAND_LOGO.src) window.FH_BRAND_LOGO.src = "/assets/sl-logo.png";
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
  /* საგზაო კმ და წუთი ორ წერტილს შორის — ტუროპერატორების რეალურ
     დროებზე კალიბრებული მოდელი (2026):
     · f/v — თბილისიდან რეალური მანძილი/დროიდან გამოთვლილი წერტილის პარამეტრები
     · მთის წერტილები (>1200 მ) — პესიმისტური სიჩქარე, მაქს. 45 კმ/სთ (კლასი c)
     · gravel / 4x4 გზები — ბოლო მონაკვეთი ნელი ფაზით (24 / 18 კმ/სთ, კლასი d/e) */
  var RD_SLOW = { 2: { len: 30, v: 24 }, 3: { len: 45, v: 18 } };
  function legKey(a, b) { var x=a.s||"",y=b.s||""; return x<y?x+"|"+y:y+"|"+x; }
  function leg(a, b) {
    var curated=(D.roadLegs||{})[legKey(a,b)];
    if(curated) return {km:+curated.km,min:+curated.minutes,difficulty:curated.difficulty||"paved",seasonal:!!curated.seasonal,curated:true};
    var d = hav(a, b);
    var f = ((a.f || 1.4) + (b.f || 1.4)) / 2;
    var va = a.v || 55, vb = b.v || 55;
    var rank = Math.max(a.rd || 0, b.rd || 0);
    var mtn = (a.el || 0) > 1200 || (b.el || 0) > 1200;
    /* მთაში, უხეშ გზაზე ან ნელ წერტილთან — მინიმალური სიჩქარე; ვაკეზე — საშუალო */
    var v = (rank >= 1 || mtn || Math.min(va, vb) < 45) ? Math.min(va, vb) : (va + vb) / 2;
    if (mtn) { v = Math.min(v, 45); f = Math.max(f, 1.5); }
    if (rank === 1) v = Math.min(v, 40);
    var km = d * f, min;
    if (rank >= 2) {
      var rs = RD_SLOW[rank], kr = Math.min(km, rs.len);
      min = (kr / rs.v + (km - kr) / Math.max(v, 30)) * 60;
    } else {
      if (km < 12) v = Math.min(v, 32);          // ქალაქში ნელა
      min = km / v * 60;
    }
    return { km: km, min: min, difficulty:Object.keys(ROAD_RANK).find(function(k){return ROAD_RANK[k]===rank;})||"paved", seasonal:mtn||rank>=2 };
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


  /* ── ტურის სტილები ────────────────────────────────────────────────────
     types  — რომელ ტიპებს ვამჯობინებთ (ცარიელი = ყველა)
     boost  — ქულის ბონუსი ამ ტიპებზე
     maxRoad— ყველაზე უხეში გზა, რომელსაც ეს სტილი უშვებს
     pace   — რეკომენდებული ტემპი წუთებში (თუ მომხმარებელს არ შეუცვლია)  */
  var ROAD_RANK = { paved: 0, mostly_paved: 1, gravel: 2, "4x4_only": 3 };
  var STYLE_RULES = {
    classic:   { types: [], boost: 3.5, flags: true, maxRoad: 2, pace: 480 },
    family:    { types: ["cave", "lake", "nature", "museum", "town", "beach", "waterfall", "spa"],
                 boost: 3, maxRoad: 1, pace: 400, maxVisit: 3 },
    history:   { types: ["monastery", "fortress", "archaeology", "museum"], boost: 3, maxRoad: 2, pace: 480 },
    nature:    { types: ["nature", "canyon", "waterfall", "lake", "cave", "mountain"], boost: 3, maxRoad: 2, pace: 500 },
    wine:      { types: ["winery", "town", "monastery"], boost: 3.5, maxRoad: 1, pace: 420 },
    mountains: { types: ["mountain", "ski", "lake", "nature"], boost: 3, maxRoad: 3, pace: 540 },
    beach:     { types: ["beach", "spa", "town", "nature"], boost: 3.5, maxRoad: 1, pace: 400 },
    slow:      { types: ["spa", "winery", "town", "lake", "museum"], boost: 2.5, maxRoad: 1, pace: 360, maxPerDay: 3 }
  };
  var curStyle = "classic";

  // ─── ფილტრაცია ──────────────────────────────────────────────────────────
  var CAR_RANK = { economy: 0, suv: 2, offroad: 3 };
  function seasonOK(a, month) {
    if (a.yearRound) return true;
    if (a.season === "all") return true;
    if (a.season === "may-october") return month >= 5 && month <= 10;
    if (a.season === "june-september") return month >= 6 && month <= 9;
    if (a.season === "december-march") return month === 12 || month <= 3;
    return true;
  }
  function carMode() {
    var el = document.querySelector('input[name="carmode"]:checked');
    return el ? el.value : "auto";
  }
  function pick() {
    var regions = chips("regions"), types = chips("interests"),
        month = parseInt(EL("month").value, 10);
    var st = STYLE_RULES[curStyle] || STYLE_RULES.classic;
    var mode = carMode();
    /* "pick" — მომხმარებელი თვითონ ირჩევს კლასს და ეს ზღუდავს ადგილებს.
       "auto"/"own" — ადგილებს სტილი ზღუდავს, მანქანას მერე ვარჩევთ.        */
    var carCap = mode === "pick" ? CAR_RANK[EL("car").value] : 2;
    var selected = window.FH_TRAVEL_SELECTION || [];
    return D.a.filter(function (a) {
      if (selected.length && selected.indexOf(a.s) < 0) return false;
      if (regions.length && regions.indexOf(a.r) < 0) return false;
      if (types.length && types.indexOf(a.ty) < 0) return false;
      var winter=month===12||month<=3,required=Math.max(CAR_RANK[a.car]||0,a.rd||0,(winter&&((a.el||0)>1200||a.rd>=1))?2:0);
      if (mode === "pick" && required > carCap) return false;
      if (ROAD_RANK[a.road] > st.maxRoad) return false;
      if (st.maxVisit && a.h > st.maxVisit) return false;
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
  function twoOpt(start, route, back) {
    /* ღირებულება = რეალური სავალი დრო (და არა სწორი ხაზი) — მთის გვერდის
       ავლით მოკლე 4x4 გზას გრძელი ასფალტი შეიძლება სჯობდეს */
    function cost(r) {
      var c = 0, prev = start;
      for (var i = 0; i < r.length; i++) { c += leg(prev, r[i]).min; prev = r[i]; }
      if (back) c += leg(prev, start).min;
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
    var s = 0, st = STYLE_RULES[curStyle] || {};
    if (st.types && st.types.length && st.types.indexOf(a.ty) >= 0) s += st.boost || 3;
    if (a.fe) s += st.flags ? 3.5 : 2;
    if (a.un) s += st.flags ? 3.5 : 2;
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
    /* ტუროპერატორული წესები: დღეში სავალი დროის ცალკე ლიმიტი (კომფორტული
       დღე ≤ 4-6 სთ საჭესთან, ტემპის მიხედვით); გრძელი გადასვლის დღე
       (მაგ. თბილისი→მესტია) დასაშვებია, მაგრამ მხოლოდ მსუბუქი დათვალიერებით */
    var driveCap = budget / 2 + 60;              // 360→240წთ · 480→300წთ · 600→360წთ
    var TRANSIT_MAX = 600;                       // ერთი გადასვლის აბსოლუტური ჭერი — 10 სთ
    var out = [], cur = start, day = { i: 1, items: [], km: 0, drive: 0, visit: 0 },
        used = 0, clockNow = DAY_START, lunched = false, left = route.slice(), dropped = [];
    while (left.length && day.i <= days) {
      var nx = left[0], L = leg(cur, nx), visit = nx.h * 60;
      var lunch = (day.items.length && !lunched && clockNow + L.min > 13 * 60) ? LUNCH : 0;
      var extra = L.min + visit + lunch;
      if ((used + extra > budget || day.drive + L.min > driveCap) && day.items.length) {
        out.push(day);
        day = { i: day.i + 1, items: [], km: 0, drive: 0, visit: 0 };
        used = 0; clockNow = DAY_START; lunched = false;
        if (day.i > days) break;
        continue;
      }
      if (L.min > TRANSIT_MAX && !day.items.length) { dropped.push(nx); left.shift(); continue; }
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

  /* მიმდინარე გეგმის მდგომარეობა — რედაქტირებისთვის */
  var CUR = { route: null, start: null, days: 3, budget: 480, back: true, pool: [] };

  function plan(all, start, days, budgetMin, back) {
    var route = buildRoute(all, start, days, budgetMin, back);
    CUR = { route: route, start: start, days: days, budget: budgetMin, back: back, pool: all };
    return splitDays(route, start, days, budgetMin, back);
  }
  function replan() {
    render(splitDays(CUR.route, CUR.start, CUR.days, CUR.budget, CUR.back), CUR.start, CUR.pool);
  }
  function editRemove(slug) {
    CUR.route = CUR.route.filter(function (a) { return a.s !== slug; });
    replan();
  }
  function editMove(slug, dir) {
    var i = CUR.route.findIndex(function (a) { return a.s === slug; });
    var j = i + dir;
    if (i < 0 || j < 0 || j >= CUR.route.length) return;
    var t = CUR.route[i]; CUR.route[i] = CUR.route[j]; CUR.route[j] = t;
    replan();
  }
  function editAdd(slug, afterSlug) {
    var a = D.a.find(function (x) { return x.s === slug; });
    if (!a || CUR.route.some(function (x) { return x.s === slug; })) return;
    var i = afterSlug ? CUR.route.findIndex(function (x) { return x.s === afterSlug; }) : -1;
    if (i >= 0) CUR.route.splice(i, 0, a); else CUR.route.push(a);
    replan();
  }
  window._fhEdit = { rm: editRemove, mv: editMove, add: editAdd };

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
    var totKm = 0, totDrive = 0, totVisit = 0, stops = 0, maxRank = 0;
    var month=parseInt(EL("month").value,10),winter=month===12||month<=3;
    var wxDays = [];
    res.days.forEach(function (d) {
      totKm += d.km; totDrive += d.drive; totVisit += d.visit; stops += d.items.length;
      d.items.forEach(function (it) {
        maxRank=Math.max(maxRank,CAR_RANK[it.a.car]||0,it.a.rd||0,(winter&&((it.a.el||0)>1200||it.a.rd>=1))?2:0);
      });
    });

    var h = '<dl class="facts">' +
      f(T.day, res.days.length) + f(T.stops, stops) +
      f(T.distance, Math.round(totKm) + " " + T.km) +
      f(T.driving_time, fmtH(totDrive)) + f(T.visiting_time, fmtH(totVisit)) +
      f(T.need_car, D.car[maxRank>=3?"offroad":(maxRank>=2?"suv":"economy")]) + "</dl>";

    var styleName = "";
    (D.styles || []).forEach(function (st) { if (st.key === curStyle) styleName = st.name; });
    if (T.sum_text) {
      h += '<p class="psum">' + esc(T.sum_text
        .replace("{days}", res.days.length).replace("{stops}", stops)
        .replace("{km}", Math.round(totKm)).replace("{drive}", fmtH(totDrive))
        .replace("{style}", styleName)) + "</p>";
    }
    h += carCard(res, maxRank);

    var rentalCar=recommendCar(res,maxRank).car,tripName=start.n+" · "+res.days.length+" "+T.day;
    h += '<div class="cta" style="margin:0 0 26px"><h2>' + T.book_cta + "</h2><p>" + T.book_text +
         '</p><div class="row"><button class="btn wa" type="button" id="plannerwa">WhatsApp</button>'+
         '<a class="btn ghost" href="' + D.url.fleet + '">' + D.nav.fleet + "</a></div></div>";

    h += "<h2>" + T.day_plan + "</h2>";
    res.days.forEach(function (d, di) {
      var col = DAY_COLORS[di % DAY_COLORS.length];
      h += '<div class="pday"><h3><span class="pdot" style="background:' + col + '"></span>' +
           T.day + " " + d.i + ' <small>' + Math.round(d.km) + " " + T.km + " · " +
           T.drive + " " + fmtH(d.drive) + " · " + T.visit + " " + fmtH(d.visit) + "</small></h3>";
      if(d.drive>480)h+='<div class="note error">⚠ '+esc(T.very_long_drive||"Very long driving day — split this itinerary")+'</div>';
      else if(d.drive>360)h+='<div class="note">⚠ '+esc(T.long_drive||"More than 6 hours of driving")+'</div>';
      if(winter&&d.items.some(function(x){return (x.a.el||0)>1200||x.a.rd>=1;}))h+='<div class="note">❄ '+esc(T.winter_warning||"Winter tyres are required; carry snow chains and verify current road conditions.")+'</div>';
      h += '<ol class="pstops">';
      var prev = di === 0 ? start : res.days[di - 1].items.slice(-1)[0].a;
      d.items.forEach(function (it, ii) {
        h += "<li><div class=\"pleg\">" + T.drive + " " + Math.round(it.legKm) + " " + T.km +
             " · " + fmtH(it.legMin) + "</div>" +
             '<div class="pstop">' +
             (it.a.img ? '<img class="pthumb" src="' + esc(it.a.img) + '" alt="" loading="lazy" ' +
                         'width="112" height="84">' : '') +
             '<div class="pstop-t"><b><a href="' + it.a.u + '">' + esc(it.a.n) + "</a></b>" +
             '<span class="pmeta">' + T.arrive + " " + clock(it.arrive) + " · " + T.visit + " " +
             fmtH(it.visit) + " · " + T.depart + " " + clock(it.depart) + "</span>" +
             '<span class="pshort">' + esc(it.a.sh) + "</span></div>" +
             '<span class="pstop-b">' +
             '<button type="button" data-pmv="-1" data-s="' + esc(it.a.s) + '" title="↑">↑</button>' +
             '<button type="button" data-pmv="1" data-s="' + esc(it.a.s) + '" title="↓">↓</button>' +
             '<button type="button" data-prm="' + esc(it.a.s) + '" title="✕">✕</button>' +
             '</span></div>';
        var opt = alongTheWay(prev, it.a, planSlugs(res), pool);
        if (opt.length) {
          /* +დრო = რეალური ჩასმის დანამატი: (prev→o) + (o→აქ) − (prev→აქ) + ვიზიტი */
          h += '<div class="popt">' + T.optional + ": " +
               opt.map(function (o) {
                 var addMin = Math.max(0, leg(prev, o.p).min + leg(o.p, it.a).min -
                                          leg(prev, it.a).min) + o.p.h * 60;
                 return '<a href="' + o.p.u + '">' + esc(o.p.n) + "</a> <i>+" +
                        fmtH(addMin) + "</i>" +
                        ' <button type="button" class="paddbtn" data-padd="' + esc(o.p.s) +
                        '" data-after="' + esc(it.a.s) + '">＋</button>';
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
      wxDays.push({ i: di, la: d.items[0].a.lat, lo: d.items[0].a.lon });
      if (di < res.days.length - 1) {
        var town = nearestTown(lastA);
        h += '<div class="pnight">' + T.overnight + ": " + esc(town.c) +
             hotelsHtml(town) + "</div>";
      }
      h += "</div>";
    });
    if (res.dropped.length) h += '<div class="note">' + T.too_far + "</div>";
    box.innerHTML = h;
    var oldTools=document.getElementById("triptools");if(oldTools)oldTools.remove();
    var topTools=document.createElement("div");topTools.id="triptools";topTools.className="tour-export-actions";
    topTools.innerHTML=(window.FH?'<button class="btn sm" type="button" id="savetrip">'+esc(T.save_trip||"Save")+'</button>':'')+
      '<button class="btn sm ghost" type="button" id="tourjpg">JPG</button><button class="btn sm ghost" type="button" id="tourpdf">PDF</button>'+
      '<button class="btn sm ghost" type="button" id="tourprint">'+esc(T.print||"Print")+'</button>';
    var expCount=document.getElementById("expcount"),expBar=document.querySelector(".expbar");
    if(expBar)expBar.insertBefore(topTools,expCount||null);

    function wrap(ctx, text, x, y, max, line) {
      var words = String(text || "").split(/\s+/), row = "", lines = [];
      words.forEach(function (word) {
        var test = row ? row + " " + word : word;
        if (row && ctx.measureText(test).width > max) { lines.push(row); row = word; } else row = test;
      });
      if (row) lines.push(row);
      lines.forEach(function (value, i) { ctx.fillText(value, x, y + i * line); });
      return y + lines.length * line;
    }
    function summaryCanvas() {
      var rows = [];
      res.days.forEach(function (day) {
        rows.push({ head: T.day + " " + day.i + " · " + Math.round(day.km) + " " + T.km,
          stops: day.items.map(function (it) { return it.a.n; }) });
      });
      var height = 500 + rows.reduce(function (n, row) { return n + 80 + row.stops.length * 68; }, 0);
      var c = document.createElement("canvas"), ctx = c.getContext("2d"); c.width = 1240; c.height = Math.max(900, height);
      ctx.fillStyle = "#f7fafc"; ctx.fillRect(0, 0, c.width, c.height);
      ctx.fillStyle = "#07111d"; ctx.fillRect(0, 0, c.width, 180);
      var grad = ctx.createLinearGradient(0, 0, 1240, 0); grad.addColorStop(0, "#25bfd1"); grad.addColorStop(1, "#3b82f6");
      var brandLogo = window.FH_BRAND_LOGO;
      if (brandLogo && brandLogo.complete && brandLogo.naturalWidth) ctx.drawImage(brandLogo, 60, 38, 130, 92);
      ctx.fillStyle = "#f4f8fc"; ctx.font = "800 40px sans-serif"; ctx.fillText("Fleet House", 215, 90);
      ctx.fillStyle = "#9fb0c4"; ctx.font = "500 22px sans-serif"; ctx.fillText("TRIP SUMMARY", 215, 126);
      ctx.fillStyle = "#0b1724"; ctx.font = "800 38px sans-serif";
      var y = wrap(ctx, start.n + " · " + res.days.length + " " + T.day, 70, 250, 1100, 48) + 16;
      ctx.font = "600 22px sans-serif"; ctx.fillStyle = "#526274";
      ctx.fillText(stops + " " + T.stops + "   ·   " + Math.round(totKm) + " " + T.km + "   ·   " + fmtH(totDrive), 70, y); y += 70;
      rows.forEach(function (row, di) {
        ctx.fillStyle = DAY_COLORS[di % DAY_COLORS.length]; ctx.beginPath(); ctx.arc(84, y - 7, 12, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#0b1724"; ctx.font = "800 26px sans-serif"; ctx.fillText(row.head, 112, y); y += 44;
        row.stops.forEach(function (name, i) {
          ctx.fillStyle = "#d9e2ec"; ctx.fillRect(82, y - 20, 3, 35);
          ctx.fillStyle = "#617286"; ctx.font = "700 18px sans-serif"; ctx.fillText(String(i + 1), 103, y + 2);
          ctx.fillStyle = "#172536"; ctx.font = "600 21px sans-serif"; y = wrap(ctx, name, 142, y + 2, 980, 29) + 12;
        });
        y += 20;
      });
      ctx.fillStyle = "#07111d"; ctx.fillRect(0, c.height - 132, c.width, 132);
      ctx.fillStyle = "#f4f8fc"; ctx.font = "800 25px sans-serif"; ctx.fillText((D.brand && D.brand.slogan) || "You Drive. We handle the rest.", 64, c.height - 78);
      ctx.fillStyle = "#9fb0c4"; ctx.font = "600 19px sans-serif";
      ctx.fillText(((D.brand && D.brand.site) || location.origin) + "   ·   " + ((D.brand && D.brand.phone) || ""), 64, c.height - 43);
      return c;
    }
    function saveBlob(blob, name) { var url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000); }
    function saveJpg() { summaryCanvas().toBlob(function (b) { if (b) saveBlob(b, "fleet-house-trip.jpg"); }, "image/jpeg", .92); }
    function savePdf() {
      var c=summaryCanvas(), data=c.toDataURL("image/jpeg",.92).split(",")[1], raw=atob(data), img=new Uint8Array(raw.length);
      for(var i=0;i<raw.length;i++)img[i]=raw.charCodeAt(i);
      var enc=new TextEncoder(), parts=[], offsets=[0], size=0;
      function add(x){var b=typeof x==="string"?enc.encode(x):x;parts.push(b);size+=b.length;}
      add("%PDF-1.4\n");
      function obj(n,body){offsets[n]=size;add(n+" 0 obj\n"+body+"\nendobj\n");}
      obj(1,"<< /Type /Catalog /Pages 2 0 R >>"); obj(2,"<< /Type /Pages /Kids [3 0 R] /Count 1 >>");
      var pw=595, ph=Math.round(595*c.height/c.width);
      obj(3,"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "+pw+" "+ph+"] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>");
      offsets[4]=size; add("4 0 obj\n<< /Type /XObject /Subtype /Image /Width "+c.width+" /Height "+c.height+" /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length "+img.length+" >>\nstream\n");add(img);add("\nendstream\nendobj\n");
      var stream="q "+pw+" 0 0 "+ph+" 0 0 cm /Im0 Do Q"; obj(5,"<< /Length "+stream.length+" >>\nstream\n"+stream+"\nendstream");
      var xref=size; add("xref\n0 6\n0000000000 65535 f \n"); for(var n=1;n<=5;n++)add(String(offsets[n]).padStart(10,"0")+" 00000 n \n");
      add("trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"+xref+"\n%%EOF"); saveBlob(new Blob(parts,{type:"application/pdf"}),"fleet-house-trip.pdf");
    }
    var jpg=document.getElementById("tourjpg"),pdf=document.getElementById("tourpdf"),print=document.getElementById("tourprint"); if(jpg)jpg.onclick=saveJpg;if(pdf)pdf.onclick=savePdf;if(print)print.onclick=function(){window.print();};
    var plannerWa=document.getElementById("plannerwa");if(plannerWa)plannerWa.onclick=function(){var cfg=window.FH_CFG||{},num=String(cfg.whatsapp||"").replace(/\D/g,"");if(!num)return;var msg="Hello, I want to rent "+(rentalCar?rentalCar.n:"a suitable car")+" for "+tripName+". Route: "+planSlugs(res).join(", ")+". Distance: "+Math.round(totKm)+" km. Page: "+location.href;window.open("https://wa.me/"+num+"?text="+encodeURIComponent(msg),"_blank","noopener");};
    box.querySelectorAll("[data-prm]").forEach(function (b) {
      b.onclick = function () { editRemove(b.dataset.prm); };
    });
    box.querySelectorAll("[data-pmv]").forEach(function (b) {
      b.onclick = function () { editMove(b.dataset.s, parseInt(b.dataset.pmv, 10)); };
    });
    box.querySelectorAll("[data-padd]").forEach(function (b) {
      b.onclick = function () { editAdd(b.dataset.padd, b.dataset.after); };
    });
    var sv = document.getElementById("savetrip");
    if (sv) sv.onclick = function () {
      var stops = [];
      res.days.forEach(function (d) { d.items.forEach(function (i) { stops.push({ s: i.a.s, n: i.a.n }); }); });
      var form = document.createElement("form"); form.className = "trip-save-form";
      var saveLabels={ka:["თარიღი","მარშრუტის სახელი"],en:["Date","Route name"],ru:["Дата","Название маршрута"],fa:["تاریخ","نام مسیر"],he:["תאריך","שם המסלול"],ar:["التاريخ","اسم المسار"]}[document.documentElement.lang]||["Date","Route name"];
      var chosenDay=document.getElementById("expday"),defaultDay=chosenDay&&chosenDay.value?chosenDay.value:(window.WX?WX.iso(7):"");
      form.innerHTML = '<label>' + esc(T.when || T.date || saveLabels[0]) + '<input type="date" name="when" required value="' +
        esc(defaultDay) + '"></label><label>' + esc(T.trip_name || saveLabels[1]) +
        '<input name="title" required maxlength="120" value="' + esc(start.n + " · " + res.days.length + " " + T.day) +
        '"></label><button class="btn sm" type="submit">' + esc(T.save_trip || "Save") + '</button><button class="btn sm ghost" type="button" data-cancel>×</button><span role="status"></span>';
      sv.replaceWith(form); form.querySelector("[data-cancel]").onclick = function(){form.replaceWith(sv);};
      form.onsubmit = function(e){e.preventDefault();var submit=form.querySelector('[type="submit"]'),status=form.querySelector('[role="status"]');submit.disabled=true;status.textContent="…";
        window.FH.saveTrip({title:form.title.value.trim(),date:form.when.value,days:res.days.length,stops:stops,km:Math.round(totKm),url:location.pathname})
          .then(function(){status.textContent=T.saved;}).catch(function(){submit.disabled=false;status.textContent="!";});};
    };
    drawMap(res.days, start);
    if (window.WX && wxDays.length) {
      var d0 = WX.iso(0);
      wxDays.slice(0, 16).forEach(function (w, k) {
        var day = WX.iso(k);
        WX.get([{ la: w.la, lo: w.lo }], day).then(function (r) {
          if (!r[0]) return;
          var head = box.querySelectorAll(".pday h3")[w.i];
          if (head) head.insertAdjacentHTML("beforeend",
            '<span class="pwx">' + WX.badge(r[0]) + "</span>");
        });
      });
    }
  }

  /* ── ავტომობილის შერჩევა მარშრუტისა და ხალხის რაოდენობის მიხედვით ──── */
  function roughestRoad(res) {
    var worst = "paved";
    res.days.forEach(function (d) {
      d.items.forEach(function (it) {
        if (ROAD_RANK[it.a.road] > ROAD_RANK[worst]) worst = it.a.road;
      });
    });
    return worst;
  }
  function recommendCar(res, minimumRank) {
    var party = parseInt(EL("party").value, 10) || 2;
    var road = roughestRoad(res);
    var needRank = Math.max(minimumRank||0,ROAD_RANK[road]||0);
    var fleet = (D.fleet || []).filter(function (c) {
      return c.seats >= party + 0 && c.rank >= needRank;
    });
    /* Never trade safety for availability: an empty result is preferable to
       recommending a vehicle below the itinerary's minimum class. */
    /* ყველაზე იაფი, რომელიც ორივე პირობას აკმაყოფილებს */
    fleet.sort(function (a, b) { return (a.rank - b.rank) || (a.price - b.price); });
    return { car: fleet[0], road: road, party: party };
  }
  function carCard(res, minimumRank) {
    var mode = carMode();
    if (mode === "own") return '<div class="carrec carrec-own"><div class="carrec-b"><span class="tag">' +
      esc(T.transport || carCopy("transport", "Transport")) + '</span><h3>' + esc(T.own_car || carCopy("own", "My own car")) +
      '</h3><p class="pshort">' + esc(T.own_car_saved || carCopy("ownSaved", "This route is planned for your own vehicle. You can change this choice at any time.")) + '</p></div></div>';
    var r = recommendCar(res,minimumRank);
    if (!r.car) return '<div class="carrec carrec-none"><div class="carrec-b">' +
      '<span class="tag">' + esc(T.car_rec) + '</span><h3>' +
      esc(T.no_safe_car || "No suitable published vehicle is currently available") +
      '</h3><p class="pshort">' + esc(T.contact_for_vehicle || "Contact us for a vehicle that meets this route’s minimum requirement.") +
      '</p></div></div>';
    var days = res.days.length;
    var rate = days >= 7 ? r.car.price7 : r.car.price;
    var total = rate * days;
    var roadName = (D.roads && D.roads[r.road]) || r.road;
    return '<div class="carrec">' +
      (r.car.img ? '<img src="' + esc(r.car.img) + '" alt="" loading="lazy">' : '<div class="carrec-ph"></div>') +
      '<div class="carrec-b"><span class="tag">' + esc(mode === "driver" ? (T.with_driver || carCopy("driver", "With driver")) : T.car_rec) + '</span>' +
      '<h3>' + esc(r.car.n) + '</h3>' +
      '<p class="pshort">' + esc(r.car.cat_n) + ' · ' + r.car.seats + ' ' + esc(T.seats) +
      (r.car.fuel ? ' · ' + esc(r.car.fuel) + ' l/100' : '') + '</p>' +
      '<div class="rentrow"><span>' + esc(T.per_day) + '</span><b>' + rate + ' ₾</b></div>' +
      '<div class="rentrow"><span>' + esc(T.for_days.replace("{n}", days)) + '</span><b>' + total + ' ₾</b></div>' +
      '<p class="pshort why">' + esc(T.why) + ': ' + r.party + ' × ' + esc(T.seats) +
      ' · ' + esc(T.roughest) + ' — ' + esc(roadName) + '</p>' +
      '<div class="row"><button class="btn sm" type="button" data-booking-open data-car="' + esc(r.car.s || r.car.n) + '" data-car-name="' + esc(r.car.n) + '">' + esc(T.book || T.see_car) + '</button>' +
      '<a class="btn sm ghost" href="' + esc(r.car.u) + '">' + esc(T.see_car) + '</a></div></div></div>';
  }


  /* ── სასტუმროები (© OpenStreetMap contributors) ────────────────────── */
  function hotelsHtml(best) {
    var H = D.hotels || {};
    if (!best) return "";
    var budget = (EL("hbudget") || {}).value || "";
    var rows = (H[best.k] || []).filter(function (r) { return !budget || r.b === budget; }).slice(0, 3);
    if (!rows.length) return "";
    return '<span class="pstay">' + T.stay + ': ' + rows.map(function (r) {
      return '<a href="https://www.openstreetmap.org/?mlat=' + r.la + '&mlon=' + r.lo +
        '#map=17/' + r.la + '/' + r.lo + '" rel="nofollow noopener" target="_blank">' +
        esc(r.n) + '</a>' + (r.st ? ' ' + r.st + '★' : '');
    }).join(' · ') + '<small> · ' + esc(T.stay_src) + '</small></span>';
  }

  function f(k, v) { return "<div><dt class=\"k\">" + k + '</dt><dd class="v">' + v + "</dd></div>"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function planSlugs(res) {
    var out = []; res.days.forEach(function (d) { d.items.forEach(function (i) { out.push(i.a.s); }); }); return out;
  }
  function nearestTown(a) {
    var towns = D.towns || [];
    if (!towns.length) return { c: a.n,k:"" };
    var t=towns.reduce(function (b, x) { return hav(a,{lat:x.lat,lon:x.lon}) < hav(a,{lat:b.lat,lon:b.lon}) ? x : b; });
    return {c:t.n,k:t.k,lat:t.lat,lon:t.lon};
  }

  /* რეალური გზის გეომეტრია TomTom Traffic Routing-ით. OSRM გამოიყენება
     მხოლოდ სარეზერვოდ; სწორი ხაზი რუკაზე საბოლოო შედეგად არ რჩება. */
  var geomSeq = 0;
  function osrmGeom(latlons, done, fail) {
    var q = latlons.map(function (p) { return p[1] + "," + p[0]; }).join(";");
    fetch("https://router.project-osrm.org/route/v1/driving/" + q +
          "?overview=full&geometries=geojson", { mode: "cors" })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.code === "Ok" && j.routes && j.routes[0])
          return done(j.routes[0].geometry.coordinates.map(function (c) { return [c[1], c[0]]; }));
        if (fail) fail();
      }).catch(function () { if (fail) fail(); });
  }
  function roadGeom(latlons, done) {
    if (latlons.length < 2 || latlons.length > 25 || !window.fetch) return;
    var mc = D.maps || {}, key = mc.tomtomKey || "";
    function fallback() {
      if (mc.fallback !== "none") osrmGeom(latlons, done);
    }
    if (mc.provider !== "tomtom" || !key || mc.routing === false) return fallback();
    var q = latlons.map(function (p) { return p[0] + "," + p[1]; }).join(":");
    fetch("https://api.tomtom.com/routing/1/calculateRoute/" + q +
      "/json?traffic=true&routeRepresentation=polyline&computeTravelTimeFor=all&key=" +
      encodeURIComponent(key), { mode: "cors" })
      .then(function (r) { if (!r.ok) throw new Error("TomTom " + r.status); return r.json(); })
      .then(function (j) {
        if (!j.routes || !j.routes[0]) return fallback();
        var pts = [];
        (j.routes[0].legs || []).forEach(function (leg) {
          (leg.points || []).forEach(function (p) {
            var xy = [p.latitude, p.longitude];
            if (!pts.length || pts[pts.length - 1][0] !== xy[0] || pts[pts.length - 1][1] !== xy[1]) pts.push(xy);
          });
        });
        if (pts.length > 1) done(pts); else fallback();
      }).catch(fallback);
  }

  function drawMap(days, start) {
    layers.forEach(function (l) { map.removeLayer(l); });
    layers = [];
    var mySeq = ++geomSeq;
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
      roadGeom(pts, function (geom) {
        if (mySeq === geomSeq) pl.setLatLngs(geom);
      });
    });
    var inPlan = {};
    days.forEach(function (d) { d.items.forEach(function (it) { inPlan[it.a.s] = 1; }); });
    (CUR.pool || []).forEach(function (a) {
      if (inPlan[a.s]) return;
      var dm = L.circleMarker([a.lat, a.lon], { radius: 5, color: "#fff", weight: 1,
        fillColor: "#5b6c7d", fillOpacity: .5 }).addTo(map);
      dm.bindPopup('<b>' + esc(a.n) + '</b><br>' +
        '<button type="button" class="btn sm" onclick="window._fhEdit.add(\'' + a.s +
        '\')">＋ ' + (T.add_stop || '+') + '</button>');
      dm.bindTooltip(a.n);
      layers.push(dm);
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
    styleRow();
    var pickSel = EL("car");
    var savedMode = localStorage.getItem("fh-car-mode");
    if (savedMode) {
      var savedRadio = document.querySelector('input[name="carmode"][value="' + savedMode + '"]');
      if (savedRadio) savedRadio.checked = true;
    }
    document.querySelectorAll('input[name="carmode"]').forEach(function (r) {
      r.onchange = function () {
        localStorage.setItem("fh-car-mode", carMode());
        pickSel.hidden = carMode() !== "pick";
        if (CUR.route) replan();
      };
    });
    pickSel.hidden = carMode() !== "pick";
    var from = EL("datefrom"), to = EL("dateto"), today = new Date();
    function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
    from.value = iso(today);
    var end = new Date(today); end.setDate(end.getDate() + 2); to.value = iso(end);
    function syncDatesToDays() {
      if (from.value) EL("month").value = String(new Date(from.value + "T12:00:00").getMonth() + 1);
      if (from.value && to.value) {
        var n = Math.round((new Date(to.value + "T12:00:00") - new Date(from.value + "T12:00:00")) / 86400000) + 1;
        if (n > 0 && n <= 30) EL("days").value = String(n);
      }
      renderStandardTours();
    }
    function syncDaysToDate() {
      var n = Math.max(1, Math.min(30, parseInt(EL("days").value, 10) || 1));
      EL("days").value = String(n);
      if (from.value) { var d = new Date(from.value + "T12:00:00"); d.setDate(d.getDate() + n - 1); to.value = iso(d); }
      renderStandardTours();
    }
    from.addEventListener("change", syncDatesToDays); to.addEventListener("change", syncDatesToDays);
    EL("days").addEventListener("change", syncDaysToDate);
    EL("days").addEventListener("input", function () { if (this.value) syncDaysToDate(); });
    [["daysminus",-1],["daysplus",1]].forEach(function (pair) {
      var b=EL(pair[0]); if(b)b.onclick=function(){EL("days").value=String((parseInt(EL("days").value,10)||1)+pair[1]);syncDaysToDate();};
    });
    [EL("party"), EL("tourpurpose"), EL("month")].forEach(function (x) {
      if (x) x.addEventListener("change", renderStandardTours);
    });
  }

  function renderStandardTours() {
    var box = EL("standardtours"), count = EL("standardcount");
    if (!box) return;
    var days = parseInt(EL("days").value, 10), party = parseInt(EL("party").value, 10);
    var purpose = EL("tourpurpose").value, month = parseInt(EL("month").value, 10);
    var from = EL("datefrom").value, to = EL("dateto").value;
    var related = {
      culinary: ["culinary", "wine"], wine: ["culinary", "wine"],
      cycling: ["cycling", "nature", "mountains"], family: ["family", "culture", "nature", "beach"]
    };
    var accepted = related[purpose] || [purpose];
    var tours = (D.standardTours || []).filter(function (tour) {
      if (party < tour.minPeople || party > tour.maxPeople || !seasonOK(tour, month)) return false;
      if (purpose !== "classic" && accepted.indexOf(tour.purpose) < 0) return false;
      if (tour.availableFrom && to && to < tour.availableFrom) return false;
      if (tour.availableTo && from && from > tour.availableTo) return false;
      return true;
    }).sort(function (a, b) {
      var ap = a.purpose === purpose ? 0 : 2, bp = b.purpose === purpose ? 0 : 2;
      return (Math.abs(a.days - days) * 4 + ap) - (Math.abs(b.days - days) * 4 + bp) || a.days - b.days;
    }).slice(0, 6);
    count.textContent = tours.length ? tours.length : "";
    if (!tours.length) {
      box.innerHTML = '<div class="standard-empty">' + (T.no_results || "No matching tours") + '</div>';
      return;
    }
    var ui = D.tourUi || {};
    box.innerHTML = tours.map(function (tour) {
      var image = tour.img ? '<img src="' + esc(tour.img) + '" alt="">' : '';
      return '<article class="standard-card" data-tour="' + esc(tour.s) + '">' + image + '<div class="standard-copy"><b>' + esc(tour.n) +
        '</b><small>' + tour.days + ' ' + (ui.day || '') + ' · ' + tour.minPeople + '–' + tour.maxPeople + ' ' +
        (ui.people || '') + ' · ' + tour.km + ' km</small><p>' + esc(tour.sh) + '</p></div>' +
        '<button type="button" class="btn sm" data-choose-tour="' + esc(tour.s) + '">' + (ui.view || 'Choose') + '</button></article>';
    }).join('');
    box.querySelectorAll('[data-choose-tour]').forEach(function (button) {
      button.onclick = function () {
        var tour = (D.standardTours || []).find(function (x) { return x.s === button.dataset.chooseTour; });
        if (!tour) return;
        window.FH_TRAVEL_SELECTION = (tour.wp || []).slice();
        EL("days").value = String(Math.max(1, Math.min(30, tour.days || 1)));
        EL("tourpurpose").value = tour.purpose || "classic";
        var modalPurpose = EL("tourpurposemodal");
        if (modalPurpose) modalPurpose.value = EL("tourpurpose").value;
        closeStandardTours();
        run();
        CUR.pool = D.a.slice();
        replan();
      };
    });
  }
  function openStandardTours() {
    var modal = EL("standardmodal"), purpose = EL("tourpurposemodal");
    if (!modal) return;
    if (purpose) purpose.value = EL("tourpurpose").value;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    renderStandardTours();
    setTimeout(function () { (purpose || EL("standardclose")).focus(); }, 20);
  }
  function closeStandardTours() {
    var modal = EL("standardmodal");
    if (!modal) return;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
  }
  function styleRow() {
    var box = EL("styles");
    if (!box || !D.styles) return;
    D.styles.forEach(function (st, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chip style" + (i === 0 ? " on" : "");
      b.dataset.style = st.key;
      b.innerHTML = "<b>" + esc(st.name) + "</b><small>" + esc(st.desc) + "</small>";
      b.onclick = function () {
        box.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("on"); });
        b.classList.add("on");
        curStyle = st.key;
        var rule = STYLE_RULES[st.key];
        if (rule && rule.pace) {
          var pace = EL("pace");
          var want = String(rule.pace <= 400 ? 360 : rule.pace >= 520 ? 600 : 480);
          for (var k = 0; k < pace.options.length; k++) {
            if (pace.options[k].value === want) pace.selectedIndex = k;
          }
        }
        run();
      };
      box.appendChild(b);
    });
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
    renderStandardTours();
  }

  function init() {
    buildForm();
    map = window.FH_TRAVEL_MAP || L.map("pmap", { scrollWheelZoom: false }).setView([42.1, 43.6], 7);
    if (!window.FH_TRAVEL_MAP) {
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        { maxZoom: 17, attribution: "&copy; OpenStreetMap" }).addTo(map);
    }
    var mc = D.maps || {};
    if (mc.provider === "tomtom" && mc.tomtomKey && mc.traffic) {
      var traffic = L.tileLayer(
        "https://api.tomtom.com/traffic/map/4/tile/flow/relative0/{z}/{x}/{y}.png?tileSize=256&key=" +
        encodeURIComponent(mc.tomtomKey),
        { maxZoom: 22, opacity: mc.trafficOpacity || 0.82, attribution: "Traffic &copy; TomTom" }
      ).addTo(map);
      L.control.layers(null, { "Live Traffic": traffic }, { collapsed: false }).addTo(map);
    }
    map.on("click", function () { map.scrollWheelZoom.enable(); });
    EL("build").onclick = run;
    var hb = EL("hbudget");
    if (hb) hb.onchange = function () { if (CUR.route) replan(); };
    EL("reset").onclick = function () {
      document.querySelectorAll(".chip.on").forEach(function (c) { c.classList.remove("on"); });
      updateChipLabel("regions"); updateChipLabel("interests");
      EL("result").innerHTML = ""; drawMap([], D.starts[parseInt(EL("start").value, 10)]);
    };
    var standardOpen = EL("standardopen"), standardClose = EL("standardclose"),
        standardModal = EL("standardmodal"), purposeModal = EL("tourpurposemodal");
    if (standardOpen) standardOpen.onclick = openStandardTours;
    if (standardClose) standardClose.onclick = closeStandardTours;
    if (standardModal) standardModal.onclick = function (e) {
      if (e.target === standardModal) closeStandardTours();
    };
    if (purposeModal) purposeModal.onchange = function () {
      EL("tourpurpose").value = purposeModal.value;
      renderStandardTours();
    };
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && standardModal && !standardModal.hidden) closeStandardTours();
    });
    var workspace = document.querySelector('.travel-workspace');
    renderStandardTours();
    if (workspace && workspace.dataset.mode === 'planner') run();
    document.addEventListener('fh:planner', function () {
      if (!CUR.route) run();
      setTimeout(function () { map.invalidateSize(); }, 30);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
