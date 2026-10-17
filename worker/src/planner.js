/* Deterministic trip maths for the AI assistant.
   Pure functions over the catalog (assets/ai-catalog.<lang>.json) — no I/O,
   no model. The model asks; these answer with numbers it cannot bend. */

export const TBILISI = { la: 41.7151, lo: 44.8271 };
const ROAD_FACTOR = 1.4;   // straight line → road km, same as the planner (f: 1.4)
const SPEED_KMH = 55;      // same as the planner (v: 55)

export function haversineKm(a, b) {
  const R = 6371, d = Math.PI / 180;
  const dLat = (b.la - a.la) * d, dLon = (b.lo - a.lo) * d;
  const x = Math.sin(dLat / 2) ** 2
    + Math.cos(a.la * d) * Math.cos(b.la * d) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}

/** Estimated driving minutes between two points (road factor + planner speed). */
export function legMinutes(a, b) {
  return Math.round(haversineKm(a, b) * ROAD_FACTOR / SPEED_KMH * 60);
}

/** Drive minutes from an origin to a place: the catalogue's measured figure
    when the origin is Tbilisi, an estimate otherwise. */
export function fromOrigin(origin, p) {
  if (!origin || origin.s === "tbilisi") return p.dm;
  return legMinutes(origin, p);
}

const num = (v, dflt = 0) => (typeof v === "number" && isFinite(v) ? v : dflt);

export function findPlaces(cat, q = {}) {
  const origin = q.origin || TBILISI;
  let list = cat.places.filter((p) => {
    if (q.types && q.types.length && !q.types.includes(p.t)) return false;
    if (q.regions && q.regions.length && !q.regions.includes(p.r)) return false;
    if (q.max_drive_min != null && fromOrigin(origin, p) > q.max_drive_min) return false;
    if (q.max_visit_h != null && num(p.vh, 99) > q.max_visit_h) return false;
    if (q.car && q.car !== "offroad" && p.cc === "offroad") return false;
    if (q.query) {
      const s = String(q.query).toLowerCase();
      if (!(p.n.toLowerCase().includes(s) || (p.short || "").toLowerCase().includes(s)
        || (p.r || "").includes(s) || (p.t || "").includes(s))) return false;
    }
    return true;
  });
  list.sort((a, b) => num(b.rt) - num(a.rt) || fromOrigin(origin, a) - fromOrigin(origin, b));
  const limit = Math.min(Math.max(num(q.limit, 10), 1), 15);
  return list.slice(0, limit).map((p) => brief(cat, p, origin));
}

export function brief(cat, p, origin = TBILISI) {
  return {
    slug: p.s, name: p.n, type: p.t, region: cat.labels.regions[p.r] || p.r,
    km_from_tbilisi: p.km, drive_min: fromOrigin(origin, p), visit_h: p.vh,
    rating: p.rt, road: p.road, car: p.cc, fee: p.fee, season: p.season,
    unesco: p.uns || undefined, about: (p.short || "").slice(0, 140),
  };
}

/** Nearest-neighbour order starting from the origin; returns stops + totals. */
export function routeDay(origin, places) {
  const left = places.slice(); const stops = []; let cur = origin; let drive = 0;
  while (left.length) {
    left.sort((a, b) => legMinutes(cur, a) - legMinutes(cur, b));
    const p = left.shift();
    const d = cur === origin ? fromOrigin(origin, p) : legMinutes(cur, p);
    drive += d; stops.push({ place: p, drive_min: d }); cur = p;
  }
  const back = fromOrigin(origin, cur);
  const visit = places.reduce((s, p) => s + num(p.vh) * 60, 0);
  return { stops, back_min: back, drive_min: drive + back, visit_min: visit, total_min: drive + back + visit };
}

/** Greedy day plans: up to `options` alternative sets that fit `hours`
    (drive out, visits, drive back). Each option is anchored on a strong place
    and filled with neighbours within `radius_km` of the anchor. */
export function fitDay(cat, q = {}) {
  const hours = Math.min(Math.max(num(q.hours, 8), 2), 16);
  const budget = hours * 60;
  const origin = q.origin || TBILISI;
  const radius = num(q.radius_km, 35);
  // A day "from Tbilisi" is a drive out of the city: the capital's own
  // sights are left out unless the caller asks for the tbilisi region.
  const wantsCity = Array.isArray(q.regions) && q.regions.includes("tbilisi");
  const pool = cat.places.filter((p) => {
    if (q.types && q.types.length && !q.types.includes(p.t)) return false;
    if (q.regions && q.regions.length && !q.regions.includes(p.r)) return false;
    if (!wantsCity && p.r === "tbilisi") return false;
    if (q.car && q.car !== "offroad" && p.cc === "offroad") return false;
    if (q.exclude && q.exclude.includes(p.s)) return false;
    return 2 * fromOrigin(origin, p) + num(p.vh) * 60 <= budget;   // reachable at all
  });
  const anchors = pool.slice().sort((a, b) => num(b.rt) - num(a.rt) || fromOrigin(origin, a) - fromOrigin(origin, b));
  const options = []; const usedAnchors = new Set();
  for (const anchor of anchors) {
    if (options.length >= Math.min(num(q.options, 3), 4)) break;
    // one option per neighbourhood: skip anchors already inside an option
    if (usedAnchors.has(anchor.s)) continue;
    const near = pool.filter((p) => p.s !== anchor.s && !usedAnchors.has(p.s) && haversineKm(anchor, p) <= radius)
      .sort((a, b) => num(b.rt) - num(a.rt));
    let chosen = [anchor]; let day = routeDay(origin, chosen);
    for (const p of near) {
      if (chosen.length >= 6) break;
      const trial = routeDay(origin, chosen.concat([p]));
      if (trial.total_min <= budget) { chosen = chosen.concat([p]); day = trial; }
    }
    chosen.forEach((p) => usedAnchors.add(p.s));
    options.push({
      region: cat.labels.regions[anchor.r] || anchor.r,
      stops: day.stops.map((s) => ({ slug: s.place.s, name: s.place.n, type: s.place.t,
        drive_min: s.drive_min, visit_h: s.place.vh, rating: s.place.rt, car: s.place.cc })),
      back_min: day.back_min, drive_min: day.drive_min, visit_min: day.visit_min,
      total_h: Math.round(day.total_min / 6) / 10, budget_h: hours,
    });
  }
  return { hours, origin: origin.s || "tbilisi", options };
}

export function getCars(cat, q = {}) {
  let list = cat.cars.slice();
  if (q.category) list = list.filter((c) => c.cat === q.category);
  if (q.seats) list = list.filter((c) => num(c.seats) >= num(q.seats));
  list.sort((a, b) => num(a.p[0]) - num(b.p[0]));
  return list.map((c) => ({
    slug: c.s, name: c.n, category: cat.labels.car_categories[c.cat] || c.cat, category_key: c.cat,
    seats: c.seats, transmission: c.tr, drive: c.drive, clearance_mm: c.cl,
    price_gel_per_day: { "1-6_days": c.p[0], "7-29_days": c.p[1], "30+_days": c.p[2] },
    deposit_gel: c.dep,
  }));
}

/** Which fleet category a set of places needs (the strictest wins). */
export function neededCategory(cat, slugs) {
  const rank = { economy: 0, suv: 1, offroad: 2 };
  let need = "economy";
  for (const s of slugs) {
    const p = cat.places.find((x) => x.s === s);
    if (p && rank[p.cc] > rank[need]) need = p.cc;
  }
  return need;
}

/** Validate a propose_plan call: known slugs only, real totals, a real car. */
export function validatePlan(cat, input = {}) {
  const errors = [];
  const slugs = Array.isArray(input.places) ? input.places.map(String) : [];
  const places = slugs.map((s) => cat.places.find((p) => p.s === s)).filter(Boolean);
  const unknown = slugs.filter((s) => !cat.places.some((p) => p.s === s));
  if (unknown.length) errors.push(`unknown places: ${unknown.join(", ")}`);
  if (!places.length) errors.push("no places");
  const days = Math.min(Math.max(num(input.days, 1), 1), 14);
  let car = input.car ? cat.cars.find((c) => c.s === input.car || c.n === input.car) : null;
  const need = neededCategory(cat, places.map((p) => p.s));
  if (car && need === "offroad" && car.cat !== "offroad") {
    errors.push(`${car.n} cannot do a 4x4-only road; pick an offroad car`);
    car = null;
  }
  if (!car) {
    // cheapest car of the category the roads demand
    const fit = cat.cars.filter((c) => c.cat === need).sort((a, b) => num(a.p[0]) - num(b.p[0]));
    car = fit[0] || null;
  }
  if (!car) errors.push("no car in the fleet fits");
  if (errors.length) return { ok: false, errors };
  const day = routeDay(TBILISI, places);
  const perDay = Math.round(day.total_min / days);
  const price = days >= 30 ? car.p[2] : days >= 7 ? car.p[1] : car.p[0];
  return {
    ok: true,
    plan: {
      title: String(input.title || "").slice(0, 80),
      origin: "tbilisi",
      days,
      places: places.map((p) => ({ slug: p.s, name: p.n, type: p.t, visit_h: p.vh, drive_min: null })),
      stops: day.stops.map((s) => ({ slug: s.place.s, name: s.place.n, drive_min: s.drive_min, visit_h: s.place.vh })),
      drive_min: day.drive_min, visit_min: day.visit_min, total_h: Math.round(day.total_min / 6) / 10,
      hours_per_day: Math.round(perDay / 6) / 10,
      car: { slug: car.s, name: car.n, category: cat.labels.car_categories[car.cat] || car.cat,
        category_key: car.cat, price_gel_per_day: price, total_gel: price * days },
      why: String(input.why || "").slice(0, 300),
    },
  };
}
