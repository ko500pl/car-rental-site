(function () {
  "use strict";
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {});
    });
  }
  var promptEvent = null;
  var copy = {
    ka: ["Fleet House აპლიკაცია", "დააინსტალირეთ ტელეფონზე და დაგეგმეთ მოგზაურობა სწრაფად.", "ინსტალაცია", "iPhone-ზე: Share → Add to Home Screen"],
    en: ["Fleet House app", "Install it on your phone and plan trips faster.", "Install", "On iPhone: Share → Add to Home Screen"],
    ru: ["Приложение Fleet House", "Установите на телефон и планируйте поездки быстрее.", "Установить", "На iPhone: Поделиться → На экран Домой"],
    fa: ["اپلیکیشن Fleet House", "روی تلفن نصب کنید و سریع‌تر سفر بسازید.", "نصب", "در iPhone: Share → Add to Home Screen"],
    he: ["אפליקציית Fleet House", "התקינו בטלפון ותכננו טיולים מהר יותר.", "התקנה", "ב-iPhone: Share → Add to Home Screen"],
    ar: ["تطبيق Fleet House", "ثبّته على هاتفك وخطط للرحلات بسرعة.", "تثبيت", "على iPhone: Share → Add to Home Screen"]
  };
  function language() {
    var value = (document.documentElement.lang || "ka").toLowerCase().split("-")[0];
    return copy[value] ? value : "en";
  }
  function standalone() {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  }
  function showInstall(forceIos) {
    if (standalone() || document.getElementById("app-install-card")) return;
    var text = copy[language()];
    var ios = forceIos || /iphone|ipad|ipod/i.test(navigator.userAgent);
    var card = document.createElement("aside");
    card.id = "app-install-card";
    card.className = "app-install-card";
    card.setAttribute("aria-label", text[0]);
    card.innerHTML = '<img src="/assets/app-icon-192.png" alt="">' +
      '<div><strong>' + text[0] + '</strong><span>' + (ios ? text[3] : text[1]) + '</span></div>' +
      '<button type="button" class="app-install-action">' + text[2] + '</button>' +
      '<button type="button" class="app-install-close" aria-label="Close">×</button>';
    card.querySelector(".app-install-close").addEventListener("click", function () { card.remove(); });
    card.querySelector(".app-install-action").addEventListener("click", function () {
      if (ios) return;
      window.FH_INSTALL_APP().then(function (accepted) { if (accepted) card.remove(); });
    });
    document.body.appendChild(card);
  }
  window.addEventListener("beforeinstallprompt", function (event) {
    event.preventDefault();
    promptEvent = event;
    document.documentElement.classList.add("app-installable");
    showInstall();
  });
  window.FH_INSTALL_APP = function () {
    if (!promptEvent) return Promise.resolve(false);
    promptEvent.prompt();
    return promptEvent.userChoice.then(function (choice) {
      promptEvent = null;
      document.documentElement.classList.remove("app-installable");
      return choice.outcome === "accepted";
    });
  };
  window.FH_SHOW_IOS_INSTALL = function () { showInstall(true); };
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-ios-install]");
    if (!button) return;
    var menu = button.closest("details");
    if (menu) menu.removeAttribute("open");
    showInstall(true);
  });
  window.addEventListener("appinstalled", function () {
    var card = document.getElementById("app-install-card");
    if (card) card.remove();
  });
  window.addEventListener("load", function () {
    if (/iphone|ipad|ipod/i.test(navigator.userAgent)) showInstall();
  });
})();
