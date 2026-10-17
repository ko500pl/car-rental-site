/* A stand-in for the model (MOCK=1): no network, same agent loop.
   It parses "N hours/days" from the last user message, calls fit_day, then
   propose_plan with the first option, then answers in text. Used by the
   Worker tests and by the site's Playwright run. */

const TEXT = {
  ka: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" → ")} — სულ ≈ ${o.total_h} სთ ${o.budget_h} საათიდან. გინდა რუკაზე ნახვა?`,
  en: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" → ")} — about ${o.total_h} h of your ${o.budget_h}. Want it on the map?`,
  ru: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" → ")} — около ${o.total_h} ч из ${o.budget_h}. Показать на карте?`,
  fa: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" ← ")} — حدود ${o.total_h} ساعت از ${o.budget_h}. روی نقشه ببینید؟`,
  he: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" ← ")} — בערך ${o.total_h} שעות מתוך ${o.budget_h}. להציג על המפה?`,
  ar: (o) => `${o.region}: ${o.stops.map((s) => s.name).join(" ← ")} — نحو ${o.total_h} ساعة من ${o.budget_h}. أعرضها على الخريطة؟`,
};

let seq = 0;

export async function mockModel(env, payload) {
  const lang = /Answer in (\w+)/.exec(payload.system)?.[1];
  const code = { Georgian: "ka", English: "en", Russian: "ru", Persian: "fa", Hebrew: "he", Arabic: "ar" }[lang] || "en";
  const msgs = payload.messages;
  const last = msgs[msgs.length - 1];
  const lastUser = [...msgs].reverse().find((m) => m.role === "user" && typeof m.content === "string");
  const text = lastUser ? lastUser.content : "";
  const hours = Number((/(\d+)\s*(h|hour|საათ|час|ساعت|שע|ساع)/i.exec(text) || [])[1]) || 8;
  const usage = { input_tokens: 1000, output_tokens: 100 };

  // 1st turn: ask for a day plan
  if (typeof last.content === "string") {
    return { stop_reason: "tool_use", usage, content: [
      { type: "tool_use", id: `t${++seq}`, name: "fit_day", input: { hours, options: 2 } },
    ] };
  }
  // tool results came back
  const results = last.content.filter((b) => b.type === "tool_result");
  const data = JSON.parse(results[0].content);
  if (data.options) {
    const o = data.options[0];
    if (!o) return { stop_reason: "end_turn", usage, content: [{ type: "text", text: "Nothing fits that budget; try more hours." }] };
    return { stop_reason: "tool_use", usage, content: [
      { type: "text", text: TEXT[code](o) },
      { type: "tool_use", id: `t${++seq}`, name: "propose_plan",
        input: { title: o.region, days: 1, places: o.stops.map((s) => s.slug), why: TEXT[code](o) } },
    ] };
  }
  if (data.ok && data.plan) {
    return { stop_reason: "end_turn", usage, content: [{ type: "text", text: data.plan.why }] };
  }
  return { stop_reason: "end_turn", usage, content: [{ type: "text", text: "Mock: " + JSON.stringify(data).slice(0, 200) }] };
}
