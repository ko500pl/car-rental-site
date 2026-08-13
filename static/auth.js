/* Fleet House — ანგარიში და შენახული მარშრუტები (Firebase).
   კონფიგურაცია: window.FH_CFG (content/settings/auth.yml-იდან).
   თუ კონფიგურაცია ცარიელია, სკრიპტი ჩუმად ითიშება და საიტი ისე მუშაობს,
   როგორც აქამდე — ავტორიზაციის ღილაკები უბრალოდ არ ჩანს.                */
(function () {
  var C = window.FH_CFG || {};
  var T = (C.t || {});

  /* ── ლოკალური რეჟიმი: Firebase ჯერ არ არის ჩართული ─────────────────
     მარშრუტები ინახება ამ ბრაუზერში (localStorage). როცა auth.yml-ში
     Firebase ჩაირთვება, იგივე ინტერფეისი ღრუბელში გადავა.            */
  if (!C.apiKey || !C.projectId) {
    var KEY = "fh_trips";
    function lread() { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
    function lwrite(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
    window.FH = {
      local: true,
      on: function (fn) { fn(null); },
      user: function () { return null; },
      openDialog: function () {},
      saveTrip: function (t) {
        var a = lread();
        t.id = "t" + (a.length + 1) + "_" + String(a.length * 7919 % 100000);
        t.status = "planned";
        a.push(t); lwrite(a);
        return Promise.resolve(t);
      },
      listTrips: function () { return Promise.resolve(lread().slice().reverse()); },
      setStatus: function (id, st) {
        var a = lread(); a.forEach(function (t) { if (t.id === id) t.status = st; }); lwrite(a);
        return Promise.resolve();
      },
      removeTrip: function (id) { lwrite(lread().filter(function (t) { return t.id !== id; }));
        return Promise.resolve(); }
    };
    function esc0(x) { return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function initLocal() {
      var box = document.getElementById("authbox");
      if (box) box.innerHTML = '<a class="authlink" href="' + esc0(C.accountUrl || "/account/") +
        '">' + esc0(T.account || "My page") + "</a>";
      var root = document.getElementById("account");
      if (!root) return;
      function draw() {
        window.FH.listTrips().then(function (trips) {
          if (!trips.length) {
            root.innerHTML = '<div class="note">' + esc0(T.no_trips || "") + '</div>' +
              '<p><a class="btn" href="' + esc0(C.plannerUrl || "/planner/") + '">' +
              esc0(T.to_planner || "Planner") + "</a></p>";
            return;
          }
          var g = { planned: [], done: [] };
          trips.forEach(function (t) { (g[t.status] || g.planned).push(t); });
          root.innerHTML = ["planned", "done"].map(function (k) {
            if (!g[k].length) return "";
            return "<h2>" + esc0(k === "planned" ? T.planned : T.done) + " · " + g[k].length + "</h2>" +
              g[k].map(function (t) {
                var stops = (t.stops || []).slice(0, 8).map(function (s) { return esc0(s.n || s); }).join(" · ");
                return '<div class="tripcard' + (k === "done" ? " done" : "") + '">' +
                  '<div class="tripmeta"><b>' + esc0(t.title) + "</b><span>" + esc0(t.date || "") +
                  " · " + (t.days || 1) + " " + esc0(T.days || "d") + " · " + (t.stops || []).length +
                  " " + esc0(T.stops || "") + (t.km ? " · " + t.km + " km" : "") + "</span></div>" +
                  '<p class="pshort">' + stops + "</p><div class=\"triprow\">" +
                  (k === "planned"
                    ? '<button class="btn sm" data-a="done" data-id="' + t.id + '">' + esc0(T.mark_done) + "</button>"
                    : '<button class="btn sm ghost" data-a="planned" data-id="' + t.id + '">' + esc0(T.mark_planned) + "</button>") +
                  (t.url ? '<a class="btn sm ghost" href="' + esc0(t.url) + '">' + esc0(T.open) + "</a>" : "") +
                  '<button class="btn sm ghost" data-a="del" data-id="' + t.id + '">' + esc0(T.delete) + "</button>" +
                  "</div></div>";
              }).join("");
          }).join("");
          root.querySelectorAll("[data-a]").forEach(function (b) {
            b.onclick = function () {
              var act = b.dataset.a;
              (act === "del"
                ? (confirm(T.confirm_del || "?") ? window.FH.removeTrip(b.dataset.id) : Promise.reject())
                : window.FH.setStatus(b.dataset.id, act)
              ).then(draw, function () {});
            };
          });
        });
      }
      draw();
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initLocal);
    else initLocal();
    return;
  }

  var SDK = "https://www.gstatic.com/firebasejs/10.12.5/";
  var app, auth, db, user = null, ready = false;
  var listeners = [];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function on(fn) { listeners.push(fn); if (ready) fn(user); }
  function fire() { listeners.forEach(function (f) { try { f(user); } catch (e) {} }); }

  var M = {};
  var boot = Promise.all([
    import(SDK + "firebase-app.js"),
    import(SDK + "firebase-auth.js"),
    import(SDK + "firebase-firestore.js"),
    import(SDK + "firebase-storage.js")
  ]).then(function (mods) {
    M.app = mods[0]; M.auth = mods[1]; M.db = mods[2]; M.storage = mods[3];
    app = M.app.initializeApp({
      apiKey: C.apiKey, authDomain: C.authDomain, projectId: C.projectId,
      storageBucket: C.storageBucket, messagingSenderId: C.messagingSenderId, appId: C.appId
    });
    auth = M.auth.getAuth(app);
    db = M.db.getFirestore(app);
    return new Promise(function (res) {
      M.auth.onAuthStateChanged(auth, function (u) { user = u; ready = true; fire(); res(u); });
    });
  }).catch(function (e) { console.warn("[auth] disabled:", e && e.message); });

  /* ── UI: ჰედერის ღილაკი ────────────────────────────────────────────── */
  function headerBox() {
    var box = document.getElementById("authbox");
    if (!box) return;
    on(function (u) {
      box.innerHTML = u
        ? '<a class="authlink" href="' + esc(C.accountUrl) + '" aria-label="' + esc(T.account || "Account") + '">' +
          '<span class="ava">' + esc((u.displayName || u.email || "?").slice(0, 1).toUpperCase()) +
          '</span><span class="authtext">' + esc(T.account || "Account") + "</span></a>"
        : '<button class="authlink" type="button" id="authopen" aria-label="' + esc(T.sign_in || "Sign in") +
          '"><span class="auth-user-icon" aria-hidden="true"></span><span class="authtext">' +
          esc(T.sign_in || "Sign in") + "</span></button>";
      var b = document.getElementById("authopen");
      if (b) b.onclick = openDialog;
    });
  }

  /* ── UI: შესვლა / რეგისტრაცია ─────────────────────────────────────── */
  function openDialog(mode) {
    var opener = document.activeElement;
    var d = document.getElementById("authdlg");
    if (d) d.remove();
    d = document.createElement("div");
    d.id = "authdlg";
    d.className = "authdlg";
    d.innerHTML =
      '<div class="authcard" role="dialog" aria-modal="true" aria-labelledby="authtitle">' +
      '<button class="authx" type="button" aria-label="×">✕</button>' +
      '<div class="authbrand" aria-hidden="true"><span>FH</span></div>' +
      '<h3 id="authtitle">' + esc(T.sign_in || "Sign in") + "</h3>" +
      '<p class="pshort">' + esc(T.why_account || "") + "</p>" +
      '<button class="btn goog" type="button" id="authgoogle">' +
      '<span class="gicon" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.5-.2-2.2H12v4.3h5.4a4.6 4.6 0 0 1-2 3v2.8h3.3c1.9-1.8 2.9-4.4 2.9-7.9z"/><path fill="#34A853" d="M12 22c2.7 0 5-.9 6.7-2.4l-3.3-2.8c-.9.6-2.1 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3v2.8A10 10 0 0 0 12 22z"/><path fill="#FBBC05" d="M6.4 13.7A6 6 0 0 1 6.1 12c0-.6.1-1.2.3-1.7V7.5H3A10 10 0 0 0 2 12c0 1.6.4 3.1 1 4.5l3.4-2.8z"/><path fill="#EA4335" d="M12 6.2c1.5 0 2.8.5 3.8 1.5l2.9-2.8A9.7 9.7 0 0 0 12 2a10 10 0 0 0-9 5.5l3.4 2.8A6 6 0 0 1 12 6.2z"/></svg></span>' + esc(T.with_google || "Continue with Google") + "</button>" +
      '<div class="author"><span>' + esc(T.or_email || "or") + "</span></div>" +
      '<label>' + esc(T.email || "Email") + '<input id="authem" type="email" autocomplete="email"></label>' +
      '<label>' + esc(T.password || "Password") +
      '<input id="authpw" type="password" autocomplete="current-password"></label>' +
      '<div id="autherr" class="autherr" role="alert" aria-live="polite"></div>' +
      '<div class="authrow">' +
      '<button class="btn" type="button" id="authin">' + esc(T.sign_in || "Sign in") + "</button>" +
      "</div>" +
      '<button class="lnk" type="button" id="authreset">' + esc(T.forgot || "Forgot password") + "</button>" +
      '<p class="authsignup"><button class="lnk" type="button" id="authup">' + esc(T.sign_up || "Create account") + "</button></p>" +
      '<p class="authnote">' + esc(T.legal_note || "") + "</p>" +
      "</div>";
    document.body.appendChild(d);
    document.body.classList.add("auth-open");
    var err = d.querySelector("#autherr");
    function fail(e) {
      var m = String((e && e.code) || e || "").replace("auth/", "").replace(/-/g, " ");
      if (m === "configuration not found") {
        var unavailable = {ka:"შესვლა დროებით მიუწვდომელია. ვააქტიურებთ ანგარიშის სერვისს — გთხოვთ, მალე სცადოთ.",
          en:"Sign-in is temporarily unavailable. Please try again shortly.",ru:"Вход временно недоступен. Пожалуйста, попробуйте позже.",
          fa:"ورود موقتاً در دسترس نیست. لطفاً کمی بعد دوباره امتحان کنید.",he:"הכניסה אינה זמינה זמנית. נסו שוב בקרוב.",
          ar:"تسجيل الدخول غير متاح مؤقتًا. يرجى المحاولة بعد قليل."};
        m = T.auth_unavailable || unavailable[document.documentElement.lang] || unavailable.en;
      }
      err.textContent = T["e_" + ((e && e.code) || "").replace("auth/", "")] || m;
      err.classList.add("show");
    }
    function close() { d.remove(); document.body.classList.remove("auth-open"); if (opener && opener.focus) opener.focus(); }
    d.querySelector(".authx").onclick = close;
    d.onclick = function (e) { if (e.target === d) close(); };
    d.onkeydown = function (e) { if (e.key === "Escape") close(); };
    setTimeout(function () { var em = d.querySelector("#authem"); if (em) em.focus(); }, 80);
    boot.then(function () {
      d.querySelector("#authgoogle").onclick = function () {
        var btn = this; btn.disabled = true; btn.classList.add("loading"); err.textContent = ""; err.classList.remove("show");
        var p = new M.auth.GoogleAuthProvider();
        M.auth.signInWithPopup(auth, p).then(close).catch(function(e){ fail(e); btn.disabled = false; btn.classList.remove("loading"); });
      };
      d.querySelector("#authin").onclick = function () {
        M.auth.signInWithEmailAndPassword(auth, val("authem"), val("authpw"))
          .then(close).catch(fail);
      };
      d.querySelector("#authup").onclick = function () {
        M.auth.createUserWithEmailAndPassword(auth, val("authem"), val("authpw"))
          .then(close).catch(fail);
      };
      d.querySelector("#authreset").onclick = function () {
        M.auth.sendPasswordResetEmail(auth, val("authem"))
          .then(function () { err.textContent = T.reset_sent || "Check your inbox."; }).catch(fail);
      };
    });
  }
  function val(id) { var e = document.getElementById(id); return e ? e.value.trim() : ""; }

  /* ── მარშრუტების შენახვა ──────────────────────────────────────────── */
  function saveTrip(trip) {
    return boot.then(function () {
      if (!user) { openDialog(); return Promise.reject("no-user"); }
      return M.db.addDoc(M.db.collection(db, "trips"), Object.assign({
        uid: user.uid, ownerName: user.displayName || user.email || "Traveller",
        status: "planned", visibility: "private", purpose: "general",
        created: M.db.serverTimestamp()
      }, trip));
    });
  }
  function listTrips() {
    return boot.then(function () {
      if (!user) return [];
      var q = M.db.query(M.db.collection(db, "trips"), M.db.where("uid", "==", user.uid));
      return M.db.getDocs(q).then(function (snap) {
        var out = [];
        snap.forEach(function (doc) { out.push(Object.assign({ id: doc.id }, doc.data())); });
        out.sort(function (a, b) { return String(b.date || "").localeCompare(String(a.date || "")); });
        return out;
      });
    });
  }
  function setStatus(id, status) {
    return boot.then(function () {
      return M.db.updateDoc(M.db.doc(db, "trips", id), { status: status });
    });
  }
  function updateTrip(id, data) {
    return boot.then(function () {
      if (!user) return Promise.reject("no-user");
      return M.db.updateDoc(M.db.doc(db, "trips", id), data);
    });
  }
  function removeTrip(id) {
    return boot.then(function () { return M.db.deleteDoc(M.db.doc(db, "trips", id)); });
  }
  function shareTrip(trip) {
    return boot.then(function () {
      if (!user) return Promise.reject("no-user");
      return M.db.addDoc(M.db.collection(db, "sharedTrips"), {
        uid: user.uid, tripId: trip.id, title: trip.title || "", date: trip.date || "",
        days: trip.days || 1, stops: trip.stops || [], km: trip.km || 0,
        url: trip.url || "", created: M.db.serverTimestamp()
      }).then(function (doc) { return location.origin + location.pathname + "?shared=" + doc.id; });
    });
  }
  function loadShared(id) {
    return boot.then(function () {
      return M.db.getDoc(M.db.doc(db, "sharedTrips", id)).then(function (doc) {
        return doc.exists() ? Object.assign({ id: doc.id }, doc.data()) : null;
      });
    });
  }

  /* ── ანგარიშის გვერდი ─────────────────────────────────────────────── */
  function accountPage() {
    var root = document.getElementById("account");
    if (!root) return;
    on(function (u) {
      if (!u) {
        root.innerHTML = '<div class="account-empty"><div class="account-orbit" aria-hidden="true"><span></span></div>' +
          '<p class="account-eyebrow">Fleet House</p><h2>' + esc(T.account || "My page") + '</h2><p>' +
          esc(T.please_sign_in || "") + '</p><div class="account-actions"><button class="btn" type="button" id="accin">' +
          esc(T.sign_in || "Sign in") + '</button><a class="btn ghost" href="' + esc(C.plannerUrl || "/planner/") + '">' +
          esc(T.to_planner || "Planner") + "</a></div></div>";
        var b = document.getElementById("accin"); if (b) b.onclick = openDialog;
        return;
      }
      root.innerHTML = '<div class="acchead"><div><b>' + esc(u.displayName || u.email) +
        "</b><span>" + esc(u.email || "") + "</span></div>" +
        '<button class="btn ghost sm" type="button" id="accout">' + esc(T.sign_out || "Sign out") +
        "</button></div><div id=\"acclist\"><p class=\"muted\">…</p></div>";
      document.getElementById("accout").onclick = function () { M.auth.signOut(auth); };
      renderTrips();
    });
  }
  function renderTrips() {
    var box = document.getElementById("acclist");
    if (!box) return;
    listTrips().then(function (trips) {
      if (!trips.length) {
        box.innerHTML = '<div class="note">' + esc(T.no_trips || "") + '</div>' +
          '<p><a class="btn" href="' + esc(C.plannerUrl) + '">' + esc(T.to_planner || "") + "</a></p>";
        return;
      }
      var groups = { planned: [], done: [] };
      trips.forEach(function (t) { (groups[t.status] || groups.planned).push(t); });
      box.innerHTML = ["planned", "done"].map(function (g) {
        if (!groups[g].length) return "";
        return "<h2>" + esc(g === "planned" ? (T.planned || "Planned") : (T.done || "Done")) +
          " · " + groups[g].length + "</h2>" +
          groups[g].map(function (t) { return tripCard(t, g); }).join("");
      }).join("");
      box.querySelectorAll("[data-done]").forEach(function (b) {
        b.onclick = function () { setStatus(b.dataset.done, "done").then(renderTrips); };
      });
      box.querySelectorAll("[data-undo]").forEach(function (b) {
        b.onclick = function () { setStatus(b.dataset.undo, "planned").then(renderTrips); };
      });
      box.querySelectorAll("[data-del]").forEach(function (b) {
        b.onclick = function () {
          if (confirm(T.confirm_del || "Delete?")) removeTrip(b.dataset.del).then(renderTrips);
        };
      });
      box.querySelectorAll("[data-share]").forEach(function (b) {
        b.onclick = function () {
          var trip = trips.find(function (t) { return t.id === b.dataset.share; });
          if (!trip) return;
          shareTrip(trip).then(function (url) {
            if (navigator.clipboard) navigator.clipboard.writeText(url);
            prompt("Share link", url);
          });
        };
      });
      box.querySelectorAll("[data-public]").forEach(function (b) {
        b.onclick = function () {
          var trip = trips.find(function (t) { return t.id === b.dataset.public; });
          updateTrip(b.dataset.public, { visibility: trip && trip.visibility === "public" ? "private" : "public" })
            .then(renderTrips);
        };
      });
    }).catch(function (e) {
      box.innerHTML = '<div class="note">' + esc(String(e && e.message || e)) + "</div>";
    });
  }
  function tripCard(t, g) {
    var stops = (t.stops || []).slice(0, 8).map(function (s) { return esc(s.n || s); }).join(" · ");
    var more = (t.stops || []).length > 8 ? " +" + ((t.stops || []).length - 8) : "";
    return '<div class="tripcard' + (g === "done" ? " done" : "") + '">' +
      '<div class="tripmeta"><b>' + esc(t.title || "") + "</b>" +
      "<span>" + esc(t.date || "") + " · " + (t.days || 1) + " " + esc(T.days || "d") +
      " · " + ((t.stops || []).length) + " " + esc(T.stops || "stops") +
      (t.km ? " · " + Math.round(t.km) + " km" : "") + "</span></div>" +
      '<p class="pshort">' + stops + more + "</p>" +
      '<div class="triprow">' +
      (g === "planned"
        ? '<button class="btn sm" type="button" data-done="' + esc(t.id) + '">' + esc(T.mark_done || "Mark done") + "</button>"
        : '<button class="btn sm ghost" type="button" data-undo="' + esc(t.id) + '">' + esc(T.mark_planned || "Move back") + "</button>") +
      (t.url ? '<a class="btn sm ghost" href="' + esc(t.url) + '">' + esc(T.open || "Open") + "</a>" : "") +
      '<button class="btn sm ghost" type="button" data-public="' + esc(t.id) + '">' +
      (t.visibility === "public" ? "Public: on" : "Public: off") + "</button>" +
      '<button class="btn sm ghost" type="button" data-share="' + esc(t.id) + '">Share</button>' +
      '<button class="btn sm ghost" type="button" data-del="' + esc(t.id) + '">' + esc(T.delete || "Delete") + "</button>" +
      "</div></div>";
  }

  window.FH = { on: on, saveTrip: saveTrip, listTrips: listTrips, shareTrip: shareTrip,
                loadShared: loadShared, openDialog: openDialog,
                firebase: function () { return boot.then(function () { return { db: db, auth: auth, M: M, app: app }; }); },
                user: function () { return user; } };

  function init() { headerBox(); accountPage(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
