/* RentUp AI — the chat widget. Plain script, no build step.
   Needs window.FH_CFG.ai = {endpoint, lang}; without an endpoint it does
   nothing. Talks to the Worker (worker/), shows its reply and, when the
   Worker returns a plan, a card with "Show on map" and "Book this car".
   History lives in sessionStorage only. */
(function () {
  "use strict";
  var cfg = (window.FH_CFG && window.FH_CFG.ai) || {};
  if (!cfg.endpoint || document.getElementById("rai")) return;
  var lang = cfg.lang || document.documentElement.lang || "en";
  var rtl = document.documentElement.dir === "rtl";
  var KEY = "rentup-ai-" + lang;

  var T = {
    ka: { open: "AI დამგეგმავი", title: "RentUp AI", sub: "მოგზაურობის დამგეგმავი", hint: "სად წავიდეთ? რამდენი საათი გაქვს?",
      ph: "მაგ.: 8 საათი მაქვს თბილისიდან, რა მირჩევ?", send: "გაგზავნა", map: "რუკაზე ნახვა", book: "ამ მანქანის დაჯავშნა",
      clear: "ახალი საუბარი", close: "დახურვა", thinking: "ვფიქრობ…", err: "ვერ დავუკავშირდი. დარეკე ან მოგვწერე WhatsApp-ზე.",
      limit: "ძალიან ბევრი შეტყობინებაა, ცოტა ხანში სცადე.", h: "სთ", min: "წთ", day: "დღე", days: "დღე", perday: "₾/დღე", total: "სულ",
      hello: "გამარჯობა! მითხარი, რამდენი დრო გაქვს და რა გაინტერესებს — მარშრუტს შემოგთავაზებ და რუკაზე გაჩვენებ.",
      q: ["8 საათი მაქვს თბილისიდან", "2 დღე კახეთში ღვინით", "რომელი მანქანა სჭირდება თუშეთს?", "რა არის დეპოზიტი?"] },
    en: { open: "AI trip planner", title: "RentUp AI", sub: "Trip planner", hint: "Where to? How many hours do you have?",
      ph: "e.g. I have 8 hours from Tbilisi — ideas?", send: "Send", map: "Show on map", book: "Book this car",
      clear: "New chat", close: "Close", thinking: "Thinking…", err: "Could not connect. Call us or write on WhatsApp.",
      limit: "Too many messages — try again in a minute.", h: "h", min: "min", day: "day", days: "days", perday: "₾/day", total: "total",
      hello: "Hi! Tell me how much time you have and what you like — I'll suggest a route and show it on the map.",
      q: ["I have 8 hours from Tbilisi", "2 days in Kakheti with wine", "Which car for Tusheti?", "What is the deposit?"] },
    ru: { open: "AI-планировщик", title: "RentUp AI", sub: "Планировщик поездок", hint: "Куда? Сколько часов у вас есть?",
      ph: "напр.: у меня 8 часов из Тбилиси — что посоветуете?", send: "Отправить", map: "Показать на карте", book: "Забронировать эту машину",
      clear: "Новый чат", close: "Закрыть", thinking: "Думаю…", err: "Нет связи. Позвоните или напишите в WhatsApp.",
      limit: "Слишком много сообщений — попробуйте через минуту.", h: "ч", min: "мин", day: "день", days: "дн.", perday: "₾/день", total: "итого",
      hello: "Здравствуйте! Скажите, сколько у вас времени и что вам интересно — предложу маршрут и покажу на карте.",
      q: ["У меня 8 часов из Тбилиси", "2 дня в Кахетии с вином", "Какая машина нужна для Тушети?", "Какой депозит?"] },
    fa: { open: "برنامه‌ریز سفر AI", title: "RentUp AI", sub: "برنامه‌ریز سفر", hint: "کجا؟ چند ساعت وقت دارید؟",
      ph: "مثلاً: ۸ ساعت از تفلیس وقت دارم، چه پیشنهادی دارید؟", send: "ارسال", map: "نمایش روی نقشه", book: "رزرو این خودرو",
      clear: "گفتگوی جدید", close: "بستن", thinking: "در حال فکر…", err: "اتصال برقرار نشد. تماس بگیرید یا در واتس‌اپ بنویسید.",
      limit: "پیام‌ها زیاد است — یک دقیقه دیگر امتحان کنید.", h: "ساعت", min: "دقیقه", day: "روز", days: "روز", perday: "₾/روز", total: "جمع",
      hello: "سلام! بگویید چقدر وقت دارید و چه چیزی دوست دارید — مسیری پیشنهاد می‌دهم و روی نقشه نشان می‌دهم.",
      q: ["۸ ساعت از تفلیس وقت دارم", "۲ روز در کاختی با شراب", "برای توشتی چه خودرویی لازم است؟", "ودیعه چقدر است؟"] },
    he: { open: "מתכנן טיולים AI", title: "RentUp AI", sub: "מתכנן טיולים", hint: "לאן? כמה שעות יש לכם?",
      ph: "לדוגמה: יש לי 8 שעות מטביליסי — רעיונות?", send: "שליחה", map: "להציג על המפה", book: "להזמין את הרכב הזה",
      clear: "שיחה חדשה", close: "סגירה", thinking: "חושב…", err: "אין חיבור. התקשרו או כתבו בוואטסאפ.",
      limit: "יותר מדי הודעות — נסו שוב בעוד דקה.", h: "ש׳", min: "דק׳", day: "יום", days: "ימים", perday: "₾/יום", total: "סה״כ",
      hello: "שלום! ספרו לי כמה זמן יש לכם ומה אתם אוהבים — אציע מסלול ואראה אותו על המפה.",
      q: ["יש לי 8 שעות מטביליסי", "יומיים בקחתי עם יין", "איזה רכב לתושתי?", "מה הפיקדון?"] },
    ar: { open: "مخطّط الرحلات AI", title: "RentUp AI", sub: "مخطّط الرحلات", hint: "إلى أين؟ كم ساعة لديك؟",
      ph: "مثلاً: لديّ 8 ساعات من تبليسي، بماذا تنصح؟", send: "إرسال", map: "عرض على الخريطة", book: "احجز هذه السيارة",
      clear: "محادثة جديدة", close: "إغلاق", thinking: "أفكّر…", err: "تعذّر الاتصال. اتصل بنا أو راسلنا على واتساب.",
      limit: "رسائل كثيرة — حاول بعد دقيقة.", h: "س", min: "د", day: "يوم", days: "أيام", perday: "₾/يوم", total: "المجموع",
      hello: "مرحباً! أخبرني كم لديك من الوقت وماذا تحب، وسأقترح مساراً وأعرضه على الخريطة.",
      q: ["لديّ 8 ساعات من تبليسي", "يومان في كاخيتي مع النبيذ", "أي سيارة لتوشيتي؟", "ما هو مبلغ التأمين؟"] },
  }[lang] || null;
  if (!T) return;

  var MARK = '<img class="rai-mark" src="/assets/brand/rentup-mark.svg" alt="" width="28" height="28">';

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function track(name, data) { try { window.RentUpAnalytics && window.RentUpAnalytics.track(name, data); } catch (e) {} }
  function hm(min) { min = Math.round(min || 0); var h = Math.floor(min / 60), m = min % 60; return (h ? h + " " + T.h + " " : "") + (m || !h ? m + " " + T.min : ""); }

  var state = { messages: [], open: false, busy: false };
  try { var saved = JSON.parse(sessionStorage.getItem(KEY) || "null"); if (saved && saved.messages) state.messages = saved.messages.slice(-20); } catch (e) {}
  function persist() { try { sessionStorage.setItem(KEY, JSON.stringify({ messages: state.messages })); } catch (e) {} }

  /* ---- DOM ---- */
  var root = el("div", "rai"); root.id = "rai";
  root.innerHTML =
    '<button type="button" class="rai-fab" aria-expanded="false" aria-controls="rai-panel">' + MARK + '<span>' + esc(T.open) + '</span></button>' +
    '<section class="rai-panel" id="rai-panel" role="dialog" aria-label="' + esc(T.title) + '" hidden>' +
      '<header class="rai-head">' + MARK + '<div><b>' + esc(T.title) + '</b><small>' + esc(T.sub) + '</small></div>' +
        '<button type="button" class="rai-ic rai-clear" title="' + esc(T.clear) + '" aria-label="' + esc(T.clear) + '">&#8635;</button>' +
        '<button type="button" class="rai-ic rai-close" aria-label="' + esc(T.close) + '">&times;</button></header>' +
      '<div class="rai-log" aria-live="polite"></div>' +
      '<div class="rai-quick"></div>' +
      '<form class="rai-form"><textarea rows="1" maxlength="1000" placeholder="' + esc(T.ph) + '" aria-label="' + esc(T.hint) + '"></textarea>' +
        '<button type="submit" aria-label="' + esc(T.send) + '">&#10148;</button></form>' +
    '</section>';
  document.body.appendChild(root);
  var fab = root.querySelector(".rai-fab"), panel = root.querySelector(".rai-panel"), log = root.querySelector(".rai-log"),
      quick = root.querySelector(".rai-quick"), form = root.querySelector(".rai-form"), input = form.querySelector("textarea");

  function render() {
    log.innerHTML = "";
    if (!state.messages.length) log.appendChild(bubble("assistant", T.hello));
    state.messages.forEach(function (m) { log.appendChild(bubble(m.role, m.content, m.plan)); });
    if (state.busy) log.appendChild(el("div", "rai-msg rai-a rai-wait", esc(T.thinking)));
    quick.innerHTML = ""; quick.hidden = state.messages.length > 0;
    if (!quick.hidden) T.q.forEach(function (q) {
      var b = el("button", "rai-chip", esc(q)); b.type = "button"; b.onclick = function () { send(q); }; quick.appendChild(b);
    });
    log.scrollTop = log.scrollHeight;
  }

  function bubble(role, text, plan) {
    var w = el("div", "rai-msg " + (role === "user" ? "rai-u" : "rai-a"));
    var p = el("div", "rai-text"); p.textContent = text; w.appendChild(p);
    if (plan) w.appendChild(planCard(plan));
    return w;
  }

  function planCard(plan) {
    var c = el("div", "rai-plan");
    var stops = (plan.stops || []).map(function (s) {
      return '<li><b>' + esc(s.name) + '</b><small>' + (s.drive_min ? "🚗 " + hm(s.drive_min) + " · " : "") + "⏱ " + esc(s.visit_h) + " " + esc(T.h) + '</small></li>';
    }).join("");
    var days = plan.days > 1 ? plan.days + " " + T.days : "1 " + T.day;
    c.innerHTML = '<div class="rai-plan-h"><b>' + esc(plan.title || "") + '</b><span>' + esc(days) + ' · ' + esc(T.total) + ' ≈ ' + esc(plan.total_h) + ' ' + esc(T.h) + '</span></div>' +
      '<ol>' + stops + '</ol>' +
      (plan.car ? '<div class="rai-car"><span>🚘 ' + esc(plan.car.name) + ' · ' + esc(plan.car.category) + '</span><b>' + esc(plan.car.price_gel_per_day) + ' ' + esc(T.perday) + '</b></div>' : "") +
      '<div class="rai-plan-b"><button type="button" class="rai-map">' + esc(T.map) + '</button>' +
      (plan.car ? '<button type="button" class="rai-book">' + esc(T.book) + '</button>' : "") + '</div>';
    c.querySelector(".rai-map").onclick = function () { showOnMap(plan); };
    var bk = c.querySelector(".rai-book"); if (bk) bk.onclick = function () { book(plan); };
    return c;
  }

  function showOnMap(plan) {
    var slugs = (plan.stops || plan.places || []).map(function (s) { return s.slug; });
    track("ai_show_on_map", { stops: slugs.length });
    var ws = window.FH_TRAVEL_WORKSPACE, exp = window.FH_TRAVEL_EXPLORER;
    var applied = ws && ws.applyPlan ? ws.applyPlan(slugs, { days: plan.days || 1, name: plan.title })
      : exp && exp.applyTour ? (exp.applyTour(slugs, { days: plan.days || 1, name: plan.title }), true) : false;
    if (applied) {
      var target = document.getElementById("planner"); if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      if (window.innerWidth < 760) toggle(false);
      return;
    }
    var base = (window.FH_CFG && window.FH_CFG.plannerUrl) || "/map/#planner";
    var path = base.split("#")[0];
    location.href = path + "?plan=" + encodeURIComponent(slugs.join(",")) + "&days=" + (plan.days || 1) + "#planner";
  }

  function book(plan) {
    var num = String((window.FH_CFG && window.FH_CFG.whatsapp) || "").replace(/\D/g, "");
    var stops = (plan.stops || []).map(function (s) { return s.name; }).join(", ");
    var msg = "Hello! I'd like to book " + (plan.car ? plan.car.name : "a car") + " for " + (plan.days || 1) + " day(s). Route: " +
      (plan.title ? plan.title + " — " : "") + stops + ". Page: " + location.href;
    track("whatsapp_click", { source: "assistant" });
    track("booking_started", { source: "assistant", car: plan.car && plan.car.slug });
    if (num) window.open("https://wa.me/" + num + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
  }

  function toggle(open) {
    state.open = open == null ? !state.open : open;
    panel.hidden = !state.open; fab.setAttribute("aria-expanded", String(state.open));
    root.classList.toggle("rai-open", state.open);
    if (state.open) { render(); if (!state.messages.length) track("ai_chat_open"); setTimeout(function () { input.focus(); }, 30); }
  }

  function send(text) {
    text = String(text || "").trim(); if (!text || state.busy) return;
    state.messages.push({ role: "user", content: text }); state.busy = true; input.value = ""; render(); persist();
    track("ai_message", { n: state.messages.length });
    var payload = { lang: lang, page: location.pathname, messages: state.messages.slice(-12).map(function (m) { return { role: m.role, content: m.content }; }) };
    var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    var timer = ctrl && setTimeout(function () { ctrl.abort(); }, 45000);
    fetch(cfg.endpoint.replace(/\/$/, "") + "/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: ctrl && ctrl.signal })
      .then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); })
      .then(function (res) {
        var b = res.body || {};
        if (res.status === 429) throw new Error("limit");
        if (res.status >= 400 || !b.reply) throw new Error(b.error || "upstream");
        state.messages.push({ role: "assistant", content: b.reply, plan: b.plan || null });
        if (b.plan) track("ai_plan", { stops: (b.plan.stops || []).length, days: b.plan.days });
      })
      .catch(function (e) {
        state.messages.push({ role: "assistant", content: e && e.message === "limit" ? T.limit : T.err, error: true });
      })
      .then(function () { clearTimeout(timer); state.busy = false; render(); persist(); });
  }

  fab.onclick = function () { toggle(); };
  root.querySelector(".rai-close").onclick = function () { toggle(false); };
  root.querySelector(".rai-clear").onclick = function () { state.messages = []; persist(); render(); };
  form.onsubmit = function (e) { e.preventDefault(); send(input.value); };
  input.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input.value); } });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && state.open) toggle(false); });

  window.RentUpAI = { open: function () { toggle(true); }, ask: function (q) { toggle(true); send(q); }, showPlan: showOnMap };
  render();
})();
