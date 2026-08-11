/* Fleet House — ანგარიში და შენახული მარშრუტები (Firebase).
   კონფიგურაცია: window.FH_CFG (content/settings/auth.yml-იდან).
   თუ კონფიგურაცია ცარიელია, სკრიპტი ჩუმად ითიშება და საიტი ისე მუშაობს,
   როგორც აქამდე — ავტორიზაციის ღილაკები უბრალოდ არ ჩანს.                */
(function () {
  var C = window.FH_CFG || {};
  var T = (C.t || {});
  if (!C.apiKey || !C.projectId) return;

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
    import(SDK + "firebase-firestore.js")
  ]).then(function (mods) {
    M.app = mods[0]; M.auth = mods[1]; M.db = mods[2];
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
        ? '<a class="authlink" href="' + esc(C.accountUrl) + '">' +
          '<span class="ava">' + esc((u.displayName || u.email || "?").slice(0, 1).toUpperCase()) +
          "</span>" + esc(T.account || "Account") + "</a>"
        : '<button class="authlink" type="button" id="authopen">' + esc(T.sign_in || "Sign in") + "</button>";
      var b = document.getElementById("authopen");
      if (b) b.onclick = openDialog;
    });
  }

  /* ── UI: შესვლა / რეგისტრაცია ─────────────────────────────────────── */
  function openDialog(mode) {
    var d = document.getElementById("authdlg");
    if (d) d.remove();
    d = document.createElement("div");
    d.id = "authdlg";
    d.className = "authdlg";
    d.innerHTML =
      '<div class="authcard" role="dialog" aria-modal="true">' +
      '<button class="authx" type="button" aria-label="×">✕</button>' +
      "<h3>" + esc(T.sign_in || "Sign in") + "</h3>" +
      '<p class="pshort">' + esc(T.why_account || "") + "</p>" +
      '<button class="btn goog" type="button" id="authgoogle">' +
      '<span class="gicon">G</span>' + esc(T.with_google || "Continue with Google") + "</button>" +
      '<div class="author"><span>' + esc(T.or_email || "or") + "</span></div>" +
      '<label>' + esc(T.email || "Email") + '<input id="authem" type="email" autocomplete="email"></label>' +
      '<label>' + esc(T.password || "Password") +
      '<input id="authpw" type="password" autocomplete="current-password"></label>' +
      '<div id="autherr" class="autherr"></div>' +
      '<div class="authrow">' +
      '<button class="btn" type="button" id="authin">' + esc(T.sign_in || "Sign in") + "</button>" +
      '<button class="btn ghost" type="button" id="authup">' + esc(T.sign_up || "Create account") + "</button>" +
      "</div>" +
      '<button class="lnk" type="button" id="authreset">' + esc(T.forgot || "Forgot password") + "</button>" +
      '<p class="authnote">' + esc(T.legal_note || "") + "</p>" +
      "</div>";
    document.body.appendChild(d);
    var err = d.querySelector("#autherr");
    function fail(e) {
      var m = String((e && e.code) || e || "").replace("auth/", "").replace(/-/g, " ");
      err.textContent = T["e_" + ((e && e.code) || "").replace("auth/", "")] || m;
    }
    d.querySelector(".authx").onclick = function () { d.remove(); };
    d.onclick = function (e) { if (e.target === d) d.remove(); };
    boot.then(function () {
      d.querySelector("#authgoogle").onclick = function () {
        var p = new M.auth.GoogleAuthProvider();
        M.auth.signInWithPopup(auth, p).then(function () { d.remove(); }).catch(fail);
      };
      d.querySelector("#authin").onclick = function () {
        M.auth.signInWithEmailAndPassword(auth, val("authem"), val("authpw"))
          .then(function () { d.remove(); }).catch(fail);
      };
      d.querySelector("#authup").onclick = function () {
        M.auth.createUserWithEmailAndPassword(auth, val("authem"), val("authpw"))
          .then(function () { d.remove(); }).catch(fail);
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
        uid: user.uid, status: "planned", created: M.db.serverTimestamp()
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
  function removeTrip(id) {
    return boot.then(function () { return M.db.deleteDoc(M.db.doc(db, "trips", id)); });
  }

  /* ── ანგარიშის გვერდი ─────────────────────────────────────────────── */
  function accountPage() {
    var root = document.getElementById("account");
    if (!root) return;
    on(function (u) {
      if (!u) {
        root.innerHTML = '<div class="note">' + esc(T.please_sign_in || "") +
          '</div><p><button class="btn" type="button" id="accin">' +
          esc(T.sign_in || "Sign in") + "</button></p>";
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
      '<button class="btn sm ghost" type="button" data-del="' + esc(t.id) + '">' + esc(T.delete || "Delete") + "</button>" +
      "</div></div>";
  }

  window.FH = { on: on, saveTrip: saveTrip, listTrips: listTrips, openDialog: openDialog,
                user: function () { return user; } };

  function init() { headerBox(); accountPage(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
