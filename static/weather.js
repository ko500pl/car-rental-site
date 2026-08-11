/* Fleet House — ამინდი Open-Meteo-დან (უფასო, გასაღების გარეშე).
   window.WX.get(points, date) -> Promise<[{code,tmax,tmin,rain,wind}|null]>
   ერთი მოთხოვნით ეკითხება ყველა წერტილს.                                */
(function () {
  var CACHE = {};
  var ICON = {
    0: "☀", 1: "🌤", 2: "⛅", 3: "☁", 45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌦", 56: "🌧", 57: "🌧",
    61: "🌦", 63: "🌧", 65: "🌧", 66: "🌧", 67: "🌧",
    71: "🌨", 73: "🌨", 75: "❄", 77: "🌨",
    80: "🌦", 81: "🌧", 82: "⛈", 85: "🌨", 86: "❄",
    95: "⛈", 96: "⛈", 99: "⛈"
  };

  function icon(code) { return ICON[code] || "•"; }

  /* დღეს + 15 დღე — Open-Meteo-ს უფასო პროგნოზის ფარგლები */
  function inRange(date) {
    if (!date) return false;
    var d = new Date(date + "T00:00:00");
    var t = new Date(); t.setHours(0, 0, 0, 0);
    var diff = (d - t) / 86400000;
    return diff >= 0 && diff <= 15;
  }

  function get(points, date) {
    if (!points.length || !inRange(date)) return Promise.resolve(points.map(function () { return null; }));
    var key = date + "|" + points.map(function (p) {
      return p.la.toFixed(2) + "," + p.lo.toFixed(2);
    }).join(";");
    if (CACHE[key]) return Promise.resolve(CACHE[key]);

    var url = "https://api.open-meteo.com/v1/forecast" +
      "?latitude=" + points.map(function (p) { return p.la.toFixed(3); }).join(",") +
      "&longitude=" + points.map(function (p) { return p.lo.toFixed(3); }).join(",") +
      "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max" +
      "&timezone=Asia%2FTbilisi&start_date=" + date + "&end_date=" + date;

    return fetch(url).then(function (r) { return r.json(); }).then(function (j) {
      var arr = Array.isArray(j) ? j : [j];
      var out = arr.map(function (o) {
        var d = o && o.daily;
        if (!d || !d.weather_code || d.weather_code[0] == null) return null;
        return {
          code: d.weather_code[0],
          icon: icon(d.weather_code[0]),
          tmax: Math.round(d.temperature_2m_max[0]),
          tmin: Math.round(d.temperature_2m_min[0]),
          rain: d.precipitation_sum[0],
          wind: Math.round(d.wind_speed_10m_max[0])
        };
      });
      CACHE[key] = out;
      return out;
    }).catch(function () {
      return points.map(function () { return null; });
    });
  }

  function badge(w) {
    if (!w) return "";
    var rain = w.rain > 0.2 ? ' <span class="wxr">' + w.rain.toFixed(1) + " mm</span>" : "";
    return '<span class="wx" title="' + w.tmin + "…" + w.tmax + '°C">' + w.icon +
      " " + w.tmax + "°<small>/" + w.tmin + "°</small>" + rain + "</span>";
  }

  /* დღეს + N — input[type=date]-ისთვის */
  function iso(offset) {
    var d = new Date();
    d.setDate(d.getDate() + (offset || 0));
    return d.toISOString().slice(0, 10);
  }

  window.WX = { get: get, badge: badge, icon: icon, iso: iso, inRange: inRange };
})();
