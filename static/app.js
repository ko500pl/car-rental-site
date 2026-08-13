(function () {
  "use strict";
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {});
    });
  }
  var promptEvent = null;
  window.addEventListener("beforeinstallprompt", function (event) {
    event.preventDefault();
    promptEvent = event;
    document.documentElement.classList.add("app-installable");
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
})();
