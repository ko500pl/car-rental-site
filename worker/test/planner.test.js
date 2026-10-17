import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fitDay, findPlaces, getCars, validatePlan, routeDay, TBILISI, legMinutes } from "../src/planner.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const CAT = JSON.parse(fs.readFileSync(path.join(here, "fixtures/ai-catalog.en.json"), "utf8"));

test("fit_day never exceeds the budget and comes back to Tbilisi", () => {
  for (const hours of [4, 6, 8, 10, 12]) {
    const r = fitDay(CAT, { hours });
    assert.ok(r.options.length >= 1, `no option for ${hours}h`);
    for (const o of r.options) {
      assert.ok(o.total_h <= hours + 0.05, `${hours}h: option ${o.region} needs ${o.total_h}`);
      assert.ok(o.back_min > 0);
      assert.ok(o.stops.length >= 1 && o.stops.length <= 6);
    }
  }
});

test("fit_day options are different neighbourhoods", () => {
  const r = fitDay(CAT, { hours: 8, options: 3 });
  const sets = r.options.map((o) => new Set(o.stops.map((s) => s.slug)));
  for (let i = 0; i < sets.length; i++) for (let j = i + 1; j < sets.length; j++) {
    for (const s of sets[i]) assert.ok(!sets[j].has(s), "a stop appears in two options");
  }
});

test("fit_day honours type and car filters", () => {
  const r = fitDay(CAT, { hours: 8, types: ["winery"], car: "economy" });
  for (const o of r.options) for (const s of o.stops) {
    assert.equal(s.type, "winery");
    assert.notEqual(s.car, "offroad");
  }
});

test("find_places ranks by rating and respects max_drive_min", () => {
  const r = findPlaces(CAT, { max_drive_min: 90, limit: 5 });
  assert.ok(r.length > 0 && r.length <= 5);
  for (const p of r) assert.ok(p.drive_min <= 90);
  for (let i = 1; i < r.length; i++) assert.ok(r[i - 1].rating >= r[i].rating);
});

test("get_cars prices are numbers and sorted ascending", () => {
  const cars = getCars(CAT);
  assert.equal(cars.length, 17);
  for (let i = 1; i < cars.length; i++)
    assert.ok(cars[i - 1].price_gel_per_day["1-6_days"] <= cars[i].price_gel_per_day["1-6_days"]);
  assert.ok(getCars(CAT, { seats: 7 }).every((c) => c.seats >= 7));
});

test("propose_plan rejects unknown slugs and empty plans", () => {
  assert.equal(validatePlan(CAT, { places: ["not-a-place"] }).ok, false);
  assert.equal(validatePlan(CAT, { places: [] }).ok, false);
});

test("propose_plan picks a car the roads allow", () => {
  const offroad = CAT.places.find((p) => p.cc === "offroad");
  const economy = CAT.cars.find((c) => c.cat === "economy");
  const r = validatePlan(CAT, { title: "x", days: 2, places: [offroad.s], car: economy.s });
  assert.equal(r.ok, false, "an economy car on a 4x4-only road must be refused");
  const ok = validatePlan(CAT, { title: "x", days: 2, places: [offroad.s] });
  assert.equal(ok.ok, true);
  assert.equal(ok.plan.car.category_key, "offroad");
  assert.equal(ok.plan.car.total_gel, ok.plan.car.price_gel_per_day * 2);
});

test("propose_plan totals come from the catalogue, 7+ days use the weekly price", () => {
  const two = CAT.places.filter((p) => p.cc === "economy" && p.dm <= 120).slice(0, 2);
  const r = validatePlan(CAT, { title: "t", days: 7, places: two.map((p) => p.s) });
  assert.equal(r.ok, true);
  const car = CAT.cars.find((c) => c.s === r.plan.car.slug);
  assert.equal(r.plan.car.price_gel_per_day, car.p[1]);
  const day = routeDay(TBILISI, two);
  assert.equal(r.plan.drive_min, day.drive_min);
  assert.equal(r.plan.stops.length, 2);
});

test("leg estimate uses the planner's road factor and speed", () => {
  // 100 km straight line → 140 road km at 55 km/h ≈ 153 min
  const a = { la: 41.7, lo: 44.8 }, b = { la: 41.7, lo: 44.8 + 100 / (111.32 * Math.cos(41.7 * Math.PI / 180)) };
  assert.ok(Math.abs(legMinutes(a, b) - 153) <= 2);
});
