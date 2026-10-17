/* RentUp AI — Cloudflare Worker.
   POST /chat {lang, messages, page} → {reply, plan?}
   The only place the Claude API key lives. Nothing is stored. */

import { findPlaces, fitDay, getCars, validatePlan } from "./planner.js";
import { systemPrompt, TOOLS } from "./prompt.js";
import { mockModel } from "./mock.js";

const LANGS = ["ka", "en", "ru", "fa", "he", "ar"];
const MAX_TURNS = 12;            // messages kept (user + assistant)
const MAX_CHARS = 1000;          // per user message
const MAX_TOOL_ROUNDS = 4;
const MODEL = "claude-haiku-5-5";
const CATALOG_TTL_MS = 60 * 60 * 1000;

const catalogs = new Map();      // lang → {at, data}

export function corsHeaders(origin, env) {
  const allowed = String(env.ALLOWED_ORIGINS || "https://rentup.ge,https://www.rentup.ge")
    .split(",").map((s) => s.trim()).filter(Boolean);
  const ok = origin && (allowed.includes(origin) || /^http:\/\/localhost(:\d+)?$/.test(origin)
    || /^http:\/\/127\.0\.0\.1(:\d+)?$/.test(origin));
  return {
    "Access-Control-Allow-Origin": ok ? origin : allowed[0],
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
    "X-Origin-Allowed": ok ? "1" : "0",
  };
}

const json = (body, status, headers) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...headers } });

export async function loadCatalog(lang, env, fetchFn = fetch) {
  const hit = catalogs.get(lang);
  if (hit && Date.now() - hit.at < CATALOG_TTL_MS) return hit.data;
  const base = String(env.SITE_URL || "https://rentup.ge").replace(/\/$/, "");
  const r = await fetchFn(`${base}/assets/ai-catalog.${lang}.json`, { cf: { cacheTtl: 3600 } });
  if (!r.ok) throw new Error(`catalog ${lang}: HTTP ${r.status}`);
  const data = await r.json();
  catalogs.set(lang, { at: Date.now(), data });
  return data;
}

/** Shape-check the request; returns {lang, messages, page} or {error}. */
export function parseRequest(body) {
  if (!body || typeof body !== "object") return { error: "bad json" };
  const lang = LANGS.includes(body.lang) ? body.lang : "en";
  if (!Array.isArray(body.messages) || !body.messages.length) return { error: "no messages" };
  const msgs = [];
  for (const m of body.messages.slice(-MAX_TURNS)) {
    if (!m || (m.role !== "user" && m.role !== "assistant")) return { error: "bad role" };
    const text = String(m.content ?? "").slice(0, MAX_CHARS).trim();
    if (!text) continue;
    if (msgs.length && msgs[msgs.length - 1].role === m.role) msgs[msgs.length - 1].content += "\n" + text;
    else msgs.push({ role: m.role, content: text });
  }
  if (!msgs.length || msgs[0].role !== "user") msgs.unshift({ role: "user", content: "Hello" });
  if (msgs[msgs.length - 1].role !== "user") return { error: "last message must be from the user" };
  return { lang, messages: msgs, page: String(body.page || "").slice(0, 200) };
}

export function runTool(cat, name, input) {
  switch (name) {
    case "find_places": return findPlaces(cat, input);
    case "fit_day": return fitDay(cat, input);
    case "get_cars": return getCars(cat, input);
    case "get_policy": return { policy: cat.policy, contact: { phone: cat.site.phone, whatsapp: cat.site.whatsapp, hours: cat.site.hours, address: cat.site.address } };
    case "propose_plan": return validatePlan(cat, input);
    default: return { error: `unknown tool ${name}` };
  }
}

async function callClaude(env, payload) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(`claude ${r.status}: ${t.slice(0, 300)}`);
  }
  return r.json();
}

/** The agent loop: model ↔ tools until a text answer (or a validated plan). */
export async function chat(cat, req, env, model = callClaude) {
  const messages = req.messages.map((m) => ({ role: m.role, content: m.content }));
  const system = systemPrompt(cat, req.lang, req.page);
  let plan = null, reply = "", usage = { in: 0, out: 0 };
  for (let round = 0; round <= MAX_TOOL_ROUNDS; round++) {
    const res = await model(env, {
      model: env.MODEL || MODEL, max_tokens: 900, system, tools: TOOLS, messages,
    });
    usage.in += res.usage?.input_tokens || 0; usage.out += res.usage?.output_tokens || 0;
    const blocks = res.content || [];
    const text = blocks.filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
    const calls = blocks.filter((b) => b.type === "tool_use");
    if (text) reply = text;
    if (!calls.length || res.stop_reason !== "tool_use") break;
    messages.push({ role: "assistant", content: blocks });
    const results = [];
    for (const c of calls) {
      const out = runTool(cat, c.name, c.input || {});
      if (c.name === "propose_plan" && out.ok) plan = out.plan;
      results.push({ type: "tool_result", tool_use_id: c.id, content: JSON.stringify(out).slice(0, 12000) });
    }
    messages.push({ role: "user", content: results });
    if (round === MAX_TOOL_ROUNDS) {
      // give the model one last text-only turn is not possible here; keep what we have
      break;
    }
  }
  if (!reply && plan) reply = plan.why || plan.title;
  return { reply, plan, usage };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, model: env.MODEL || MODEL, mock: !!env.MOCK, cached: [...catalogs.keys()] }, 200, cors);
    }
    if (request.method !== "POST" || url.pathname !== "/chat") return json({ error: "not found" }, 404, cors);
    if (cors["X-Origin-Allowed"] !== "1") return json({ error: "origin not allowed" }, 403, cors);

    if (env.RATE_LIMITER) {
      const ip = request.headers.get("CF-Connecting-IP") || "0";
      const { success } = await env.RATE_LIMITER.limit({ key: ip });
      if (!success) return json({ error: "rate_limited" }, 429, cors);
    }
    if (!env.ANTHROPIC_API_KEY && !env.MOCK) return json({ error: "not_configured" }, 503, cors);

    let body;
    try { body = await request.json(); } catch { return json({ error: "bad json" }, 400, cors); }
    const req = parseRequest(body);
    if (req.error) return json({ error: req.error }, 400, cors);

    try {
      const cat = await loadCatalog(req.lang, env);
      const out = await chat(cat, req, env, env.MOCK ? mockModel : callClaude);
      return json({ reply: out.reply, plan: out.plan, usage: out.usage }, 200, cors);
    } catch (e) {
      console.error(String(e));
      return json({ error: "upstream", detail: String(e.message || e).slice(0, 200) }, 502, cors);
    }
  },
};
