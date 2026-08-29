/* RentUp GA4 tracking. Safe no-op when GA_MEASUREMENT_ID is not configured. */
(function () {
  if (window.RentUpAnalytics) return;
  var cfg = window.FH_ANALYTICS_CONFIG || {};
  var measurementId = String(cfg.measurementId || "").trim();
  var enabled = /^G-[A-Z0-9]+$/i.test(measurementId);
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
  function track(name, params) {
    if (!enabled || typeof window.gtag !== "function") return false;
    window.gtag("event", name, clean(params));
    return true;
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

  window.RentUpAnalytics = { enabled: enabled, track: track, once: once, carParams: carParams, bookingParams: bookingParams };
  if (!enabled) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  var debugMode = new URLSearchParams(location.search).get("ga_debug") === "1";
  window.gtag("js", new Date());
  window.gtag("config", measurementId, { send_page_view: false, debug_mode: debugMode });
  var gaScript = document.createElement("script");
  gaScript.async = true;
  gaScript.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
  document.head.appendChild(gaScript);
  once("page_view:" + location.href, "page_view", { page_title: document.title, page_location: location.href,
    page_path: location.pathname + location.search, debug_mode: debugMode || undefined });

  document.addEventListener("DOMContentLoaded", function () {
    var viewedCar = document.querySelector("[data-analytics-car-view]");
    if (viewedCar) once("car_view:" + location.pathname, "car_view", carParams(viewedCar));
    if (new URLSearchParams(location.search).get("booking_sent") === "1") {
      try {
        var submitted = JSON.parse(sessionStorage.getItem("rentup_pending_booking") || "{}");
        sessionStorage.removeItem("rentup_pending_booking");
        once("booking_submitted:native:" + location.href, "booking_submitted", submitted);
      } catch (e) {}
    }
    document.addEventListener("click", function (event) {
      var target = event.target.closest("a, button");
      if (!target) return;
      var href = String(target.getAttribute("href") || "");
      if (target.matches("[data-car-search]")) track("car_search", carParams(target));
      else if (target.matches("[data-booking-open]")) track("booking_started", carParams(target));
      else if (target.matches("[data-inquiry-wa]") || /wa\.me|whatsapp/i.test(href)) track("whatsapp_click", bookingParams(target));
      else if (/^tel:/i.test(href)) track("phone_click", carParams(target));
      else if (/^mailto:/i.test(href) || /\/contact\/?(?:[?#]|$)/i.test(href)) track("contact_click", carParams(target));
    });
    document.querySelectorAll('[data-car-search-input]').forEach(function (input) {
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
  });
}());
