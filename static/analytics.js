/* RentUp analytics — cookieless Umami events.
   The Umami tag (emitted by build.py only when site.yml → analytics.website_id
   is set) records page views. This file adds the events the business cares
   about: call_click, whatsapp_click and booking_request, each tagged with the
   page language and page type. Every call is a safe no-op when Umami is
   absent, blocked or still loading, and never blocks a link's navigation. */
(function () {
  if (window.RentUpAnalytics) return;
  var onceKeys = Object.create(null), searchTimers = new WeakMap(), lastSearches = new WeakMap();

  function clean(params) {
    var out = {};
    Object.keys(params || {}).forEach(function (key) {
      var value = params[key];
      if (value !== undefined && value !== null && value !== "") out[key] = value;
    });
    if (out.car_name && (!out.brand || !out.model)) {
      var parts = String(out.car_name).split(/\s+/);
      out.brand = out.brand || parts.shift();
      out.model = out.model || parts.join(" ");
    }
    return out;
  }
  function ready() {
    return !!(window.umami && typeof window.umami.track === "function");
  }
  function pageType() {
    var m = /(?:^|\s)page-(\S+)/.exec((document.body && document.body.className) || "");
    return m ? m[1] : "other";
  }
  function track(name, params) {
    if (!ready()) return false;
    try {
      var data = clean(params);
      data.lang = (document.documentElement && document.documentElement.lang) || "";
      data.page_type = pageType();
      window.umami.track(name, data);
      return true;
    } catch (e) { return false; }
  }
  function once(key, name, params) {
    if (onceKeys[key]) return false;
    onceKeys[key] = true;
    return track(name, params);
  }
  function carParams(el) {
    var node = el && el.closest ? el.closest("[data-car], [data-analytics-car]") : null;
    node = node || document.querySelector("[data-analytics-car]");
    if (!node) return {};
    return clean({ car_id: node.dataset.car || node.dataset.carId, car_name: node.dataset.carName,
      brand: node.dataset.brand, model: node.dataset.model, price: Number(node.dataset.price) || undefined,
      rental_days: Number(node.dataset.rentalDays) || undefined });
  }
  function bookingParams(root) {
    var form = root && root.matches && root.matches("form") ? root : (root && root.closest ? root.closest("form") : null);
    var params = carParams(root);
    if (!form) return params;
    var slug = form.querySelector('[name="car_slug"]'), name = form.querySelector('[name="requested_car"]');
    var start = form.querySelector('[name="start"]'), end = form.querySelector('[name="end"]');
    if (slug && slug.value) params.car_id = slug.value;
    if (name && name.value) params.car_name = name.value;
    if (params.car_name && (!params.brand || !params.model)) {
      var parts = params.car_name.split(/\s+/);
      params.brand = params.brand || parts.shift();
      params.model = params.model || parts.join(" ");
    }
    if (start && end && start.value && end.value) {
      var days = Math.ceil((new Date(end.value + "T12:00:00") - new Date(start.value + "T12:00:00")) / 86400000);
      if (days > 0) params.rental_days = days;
    }
    var car = ((window.FH_CFG || {}).cars || {})[params.car_id];
    if (car) params.price = params.rental_days >= 30 ? car.p30 : (params.rental_days >= 7 ? car.p7 : car.p1);
    return clean(params);
  }

  window.RentUpAnalytics = { get enabled() { return ready(); }, track: track, once: once,
    carParams: carParams, bookingParams: bookingParams };

  document.addEventListener("click", function (event) {
    var target = event.target && event.target.closest ? event.target.closest("a") : null;
    if (!target) target = event.target && event.target.closest ? event.target.closest("button") : null;
    if (!target) return;
    var href = String((target.getAttribute && target.getAttribute("href")) || "");
    if (/^tel:/i.test(href)) track("call_click", { href_kind: "tel" });
    else if (/wa\.me\//i.test(href) || (target.matches && target.matches("[data-inquiry-wa]")))
      track("whatsapp_click", {});
    else if (target.matches && target.matches("[data-car-search]")) track("car_search", carParams(target));
    else if (target.matches && target.matches("[data-booking-open]")) track("booking_started", carParams(target));
  });

  function onReady() {
    var viewedCar = document.querySelector("[data-analytics-car-view]");
    if (viewedCar) once("car_view:" + location.pathname, "car_view", carParams(viewedCar));
    if (new URLSearchParams(location.search).get("booking_sent") === "1") {
      try {
        var submitted = JSON.parse(sessionStorage.getItem("rentup_pending_booking") || "{}");
        sessionStorage.removeItem("rentup_pending_booking");
        once("booking_request:native:" + location.href, "booking_request", submitted);
      } catch (e) {}
    }
    (document.querySelectorAll ? document.querySelectorAll("[data-car-search-input]") : []).forEach(function (input) {
      input.addEventListener("input", function () {
        clearTimeout(searchTimers.get(input));
        searchTimers.set(input, setTimeout(function () {
          var term = input.value.trim();
          if (!term || lastSearches.get(input) === term) return;
          lastSearches.set(input, term);
          var params = carParams(input); params.search_term = term; track("car_search", params);
        }, 700));
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", onReady);
  else onReady();
}());
