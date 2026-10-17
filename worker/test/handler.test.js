import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import worker, { parseRequest, corsHeaders, chat } from "../src/index.js";
import { mockModel } from "../src/mock.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const CAT = JSON.parse(fs.readFileSync(path.join(here, "fixtures/ai-catalog.en.json"), "utf8"));

// serve the fixture to loadCatalog
globalThis.fetch = async (url) => {
  if (String(url).includes("/assets/ai-catalog.")) {
    const lang = /ai-catalog\.(\w+)\.json/.exec(String(url))[1];
    const file = path.join(here, `fixtures/ai-catalog.${lang}.json`);
    if (!fs.existsSync(file)) return new Response("nope", { status: 404 });
    return new Response(fs.readFileSync(file), { status: 200, headers: { "content-type": "application/json" } });
  }
  throw new Error("unexpected fetch " + url);
};

const ENV = { MOCK: "1", SITE_URL: "https://rentup.ge" };
const post = (body, origin = "https://rentup.ge") => worker.fetch(new Request("https://ai.example/chat", {
  method: "POST", headers: { "content-type": "application/json", "Origin": origin }, body: JSON.stringify(body),
}), ENV);

test("parseRequest trims, caps and merges", () => {
  const r = parseRequest({ lang: "ka", messages: [
    { role: "user", content: "a" }, { role: "user", content: "b" }, { role: "assistant", content: "c" }, { role: "user", content: "x".repeat(5000) },
  ] });
  assert.equal(r.lang, "ka");
  assert.equal(r.messages.length, 3);
  assert.equal(r.messages[0].content, "a\nb");
  assert.equal(r.messages[2].content.length, 1000);
  assert.equal(parseRequest({ messages: [] }).error, "no messages");
  assert.equal(parseRequest({ messages: [{ role: "assistant", content: "hi" }] }).error, "last message must be from the user");
  assert.equal(parseRequest({ lang: "xx", messages: [{ role: "user", content: "hi" }] }).lang, "en");
});

test("CORS allows the site and localhost only", () => {
  assert.equal(corsHeaders("https://rentup.ge", {})["X-Origin-Allowed"], "1");
  assert.equal(corsHeaders("http://localhost:8874", {})["X-Origin-Allowed"], "1");
  assert.equal(corsHeaders("https://evil.example", {})["X-Origin-Allowed"], "0");
  assert.equal(corsHeaders("https://evil.example", {})["Access-Control-Allow-Origin"], "https://rentup.ge");
});

test("a foreign origin is refused", async () => {
  const r = await post({ lang: "en", messages: [{ role: "user", content: "hi" }] }, "https://evil.example");
  assert.equal(r.status, 403);
});

test("without a key and without MOCK the worker says not_configured", async () => {
  const r = await worker.fetch(new Request("https://ai.example/chat", {
    method: "POST", headers: { "content-type": "application/json", "Origin": "https://rentup.ge" },
    body: JSON.stringify({ lang: "en", messages: [{ role: "user", content: "hi" }] }),
  }), { SITE_URL: "https://rentup.ge" });
  assert.equal(r.status, 503);
});

test("8 hours from Tbilisi → a validated plan that fits, in the asked language", async () => {
  const r = await post({ lang: "en", page: "/", messages: [{ role: "user", content: "I have 8 hours from Tbilisi, suggest something" }] });
  assert.equal(r.status, 200);
  const b = await r.json();
  assert.ok(b.reply.length > 10);
  assert.ok(b.plan, "plan missing");
  assert.ok(b.plan.places.length >= 1);
  assert.ok(b.plan.total_h <= 8.05, `plan needs ${b.plan.total_h}h`);
  assert.ok(b.plan.car.price_gel_per_day > 0);
  assert.ok(b.usage.in > 0);
});

test("the rate limiter binding is honoured", async () => {
  const env = { ...ENV, RATE_LIMITER: { limit: async () => ({ success: false }) } };
  const r = await worker.fetch(new Request("https://ai.example/chat", {
    method: "POST", headers: { "content-type": "application/json", "Origin": "https://rentup.ge", "CF-Connecting-IP": "1.2.3.4" },
    body: JSON.stringify({ lang: "en", messages: [{ role: "user", content: "hi" }] }),
  }), env);
  assert.equal(r.status, 429);
});

test("the agent loop stops after the tool-round cap", async () => {
  let n = 0;
  const loopy = async () => { n++; return { stop_reason: "tool_use", usage: {}, content: [
    { type: "tool_use", id: "x" + n, name: "get_policy", input: {} }] }; };
  const out = await chat(CAT, { lang: "en", page: "/", messages: [{ role: "user", content: "hi" }] }, {}, loopy);
  assert.ok(n <= 5);
  assert.equal(out.plan, null);
});

test("health endpoint", async () => {
  const r = await worker.fetch(new Request("https://ai.example/health", { headers: { Origin: "https://rentup.ge" } }), ENV);
  assert.equal((await r.json()).ok, true);
});

test("mock model answers in Georgian when asked", async () => {
  const out = await chat(CAT, { lang: "ka", page: "/", messages: [{ role: "user", content: "8 საათი მაქვს" }] }, ENV, mockModel);
  assert.ok(/სთ|საათ/.test(out.reply), out.reply);
});
