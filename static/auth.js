/* Drive On — ანგარიში და შენახული მარშრუტები (Firebase).
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
      getProfile: function () {
        try {
          return Promise.resolve({ name: localStorage.getItem("do-bk-name") || "",
                                   phone: localStorage.getItem("do-bk-phone") || "" });
        } catch (e) { return Promise.resolve({ name: "", phone: "" }); }
      },
      saveProfile: function (p) {
        try {
          localStorage.setItem("do-bk-name", String(p.name || "").trim());
          localStorage.setItem("do-bk-phone", String(p.phone || "").trim());
        } catch (e) {}
        return Promise.resolve(p);
      },
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
  function fire() {
    listeners.forEach(function (f) { try { f(user); } catch (e) {} });
    document.dispatchEvent(new CustomEvent("fh:auth", { detail: user ? { uid: user.uid } : null }));
  }

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
    /* მობილურ ბრაუზერებში sessionStorage სექციონირებულია — ავტორიზაცია
       IndexedDB-ში უნდა შენახოს, თორემ დაბრუნებისას სესია იკარგება. */
    var persist = M.auth.setPersistence(auth, M.auth.indexedDBLocalPersistence)
      .catch(function () { return M.auth.setPersistence(auth, M.auth.browserLocalPersistence); })
      .catch(function () {});
    return persist.then(function () {
      /* redirect-ით შესვლის შედეგი. "missing initial state" მაშინ ხდება,
         როცა sessionStorage მიუწვდომელია — მომხმარებელი ხშირად მაინც
         შესულია, ამიტომ შეცდომას ვწყვეტთ და currentUser-ს ვენდობით. */
      return M.auth.getRedirectResult(auth).catch(function (e) {
        console.warn("[auth] redirect:", e && e.code);
        return null;
      });
    }).then(function () {
      return new Promise(function (res) {
        M.auth.onAuthStateChanged(auth, function (u) {
          user = u; ready = true;
          if (u) loadProfile(u).catch(function () {});
          fire(); res(u);
        });
      });
    });
  }).catch(function (e) { console.warn("[auth] disabled:", e && e.message); });

  /* ── პროფილი: სახელი და ტელეფონი ───────────────────────────────────
     Firestore-ში users/{uid}, ასლი ბრაუზერშიც — ჯავშნის ფორმები აქედან
     ივსება ავტომატურად და მომხმარებელს იქვე შეუძლია შეცვლა.          */
  var profile = { name: "", phone: "" };
  function localProfile() {
    try {
      return { name: localStorage.getItem("do-bk-name") || "",
               phone: localStorage.getItem("do-bk-phone") || "" };
    } catch (e) { return { name: "", phone: "" }; }
  }
  function mirror(p) {
    try {
      if (p.name) localStorage.setItem("do-bk-name", p.name);
      if (p.phone) localStorage.setItem("do-bk-phone", p.phone);
    } catch (e) {}
    document.dispatchEvent(new CustomEvent("fh:profile", { detail: p }));
  }
  function loadProfile(u) {
    return M.db.getDoc(M.db.doc(db, "users", u.uid)).then(function (d) {
      var data = d.exists() ? d.data() : {};
      profile = {
        name: data.name || u.displayName || localProfile().name || "",
        phone: data.phone || u.phoneNumber || localProfile().phone || ""
      };
      mirror(profile);
      return profile;
    });
  }
  function getProfile() {
    if (profile.name || profile.phone) return Promise.resolve(profile);
    var l = localProfile();
    if (!user) return Promise.resolve(l);
    return boot.then(function () { return user ? loadProfile(user) : l; }).catch(function () { return l; });
  }
  function saveProfile(p) {
    profile = { name: String(p.name || "").trim(), phone: String(p.phone || "").trim() };
    mirror(profile);
    if (!user) return Promise.resolve(profile);
    return boot.then(function () {
      return M.db.setDoc(M.db.doc(db, "users", user.uid), {
        name: profile.name, phone: profile.phone,
        email: user.email || "", updated: M.db.serverTimestamp()
      }, { merge: true });
    }).then(function () {
      if (profile.name && profile.name !== user.displayName) {
        return M.auth.updateProfile(auth.currentUser, { displayName: profile.name })
          .then(function () { user = auth.currentUser; fire(); }).catch(function () {});
      }
    }).then(function () { return profile; });
  }

  /* ── UI: ჰედერის ღილაკი ────────────────────────────────────────────── */
  function headerBox() {
    var box = document.getElementById("authbox");
    if (!box) return;
    on(function (u) {
      box.innerHTML = u
        ? '<a class="authlink" href="' + esc(C.accountUrl) + '" aria-label="' + esc(T.account || "Account") + '">' +
          '<span class="ava">' + (u.photoURL ? '<img src="' + esc(u.photoURL) + '" alt="">' : esc((u.displayName || u.email || "?").slice(0, 1).toUpperCase())) +
          '</span><span class="authtext">' + esc(T.account || "Account") + "</span></a>"
        : '<button class="authlink" type="button" id="authopen" aria-label="' + esc(T.sign_in || "Sign in") +
          '"><span class="auth-user-icon" aria-hidden="true"></span><span class="authtext">' +
          esc(T.sign_in || "Sign in") + "</span></button>";
      var b = document.getElementById("authopen");
      if (b) b.onclick = openDialog;
      if (u) notificationCenter(box, u);
    });
  }

  /* პირადი და ჯგუფური შეტყობინებების მსუბუქი ცენტრი. დადუმება ინახება
     კონკრეტული მომხმარებლის ბრაუზერში და არ ცვლის სხვა წევრების ხედს. */
  function notificationCenter(box, u) {
    var wrap = document.createElement("div"); wrap.className = "notify-center";
    wrap.innerHTML = '<button class="notify-button" type="button" aria-label="Messages" aria-expanded="false">' +
      '<span aria-hidden="true">●</span><b hidden>0</b></button><div class="notify-pop" hidden><div class="notify-head"><strong>Messages</strong><a href="' + esc(C.accountUrl) + '">Open all</a></div><div class="notify-list"><p class="muted">…</p></div></div>';
    box.insertBefore(wrap, box.firstChild);
    var button = wrap.querySelector(".notify-button"), pop = wrap.querySelector(".notify-pop"), list = wrap.querySelector(".notify-list");
    button.onclick = function () { var open = pop.hidden; pop.hidden = !open; button.setAttribute("aria-expanded", String(open)); if (open && wrap._markSeen) wrap._markSeen(); };
    document.addEventListener("click", function (e) { if (!wrap.contains(e.target)) { pop.hidden = true; button.setAttribute("aria-expanded", "false"); } });
    boot.then(function () {
      return M.db.getDocs(M.db.query(M.db.collection(db, "conversations"), M.db.where("memberIds", "array-contains", u.uid)));
    }).then(function (snap) {
      var rows = []; snap.forEach(function (d) { rows.push(Object.assign({ id:d.id }, d.data())); });
      function stamp(r) { return (r.updatedAt && r.updatedAt.seconds || r.updated && r.updated.seconds || 0); }
      rows.sort(function (a,b) { return stamp(b) - stamp(a); });
      var muted = {}; try { muted = JSON.parse(localStorage.getItem("fh-muted-" + u.uid) || "{}"); } catch(e) {}
      var seen = {}; try { seen = JSON.parse(localStorage.getItem("fh-seen-" + u.uid) || "{}"); } catch(e) {}
      var unread = rows.filter(function (r) { return !muted[r.id] && stamp(r) > (seen[r.id] || 0); }).length;
      var badge = button.querySelector("b"); badge.textContent = unread; badge.hidden = !unread;
      wrap._markSeen = function () {
        rows.forEach(function (r) { seen[r.id] = Math.max(seen[r.id] || 0, stamp(r)); });
        localStorage.setItem("fh-seen-" + u.uid, JSON.stringify(seen)); badge.hidden = true;
      };
      list.innerHTML = rows.length ? rows.slice(0,8).map(function (r) {
        var name = r.groupName || r.title || r.otherName || (r.kind === "group" ? "Group" : "Conversation");
        return '<div class="notify-row ' + (muted[r.id] ? 'muted' : '') + '"><a href="' + esc(C.accountUrl) + '"><b>' + esc(name) + '</b><small>' + esc(r.lastMessage || r.preview || '') + '</small></a><button type="button" data-mute="' + esc(r.id) + '" title="Mute">' + (muted[r.id] ? '○' : '🔕') + '</button></div>';
      }).join('') : '<p class="muted">No messages yet.</p>';
      list.querySelectorAll('[data-mute]').forEach(function (m) { m.onclick = function () {
        muted[m.dataset.mute] = !muted[m.dataset.mute]; localStorage.setItem("fh-muted-" + u.uid, JSON.stringify(muted));
        wrap.remove(); notificationCenter(box, u);
      }; });
    }).catch(function () { list.innerHTML = '<p class="muted">Messages are temporarily unavailable.</p>'; });
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
      '<div class="authbrand" aria-hidden="true"><img src="/assets/do-logo-tight.png" alt=""></div>' +
      '<h3 id="authtitle">' + esc(T.sign_in || "Sign in") + "</h3>" +
      '<p class="pshort">' + esc(T.why_account || "") + "</p>" +
      '<button class="btn goog" type="button" id="authgoogle">' +
      '<span class="gicon" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.5-.2-2.2H12v4.3h5.4a4.6 4.6 0 0 1-2 3v2.8h3.3c1.9-1.8 2.9-4.4 2.9-7.9z"/><path fill="#34A853" d="M12 22c2.7 0 5-.9 6.7-2.4l-3.3-2.8c-.9.6-2.1 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3v2.8A10 10 0 0 0 12 22z"/><path fill="#FBBC05" d="M6.4 13.7A6 6 0 0 1 6.1 12c0-.6.1-1.2.3-1.7V7.5H3A10 10 0 0 0 2 12c0 1.6.4 3.1 1 4.5l3.4-2.8z"/><path fill="#EA4335" d="M12 6.2c1.5 0 2.8.5 3.8 1.5l2.9-2.8A9.7 9.7 0 0 0 12 2a10 10 0 0 0-9 5.5l3.4 2.8A6 6 0 0 1 12 6.2z"/></svg></span>' + esc(T.with_google || "Continue with Google") + "</button>" +
      '<button class="btn facebook" type="button" id="authfacebook">' +
      '<span class="fbicon" aria-hidden="true">f</span>' + esc(T.with_facebook || "Continue with Facebook") + "</button>" +
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
      if (m === "unauthorized domain") {
        var domainError = {ka:"ამ მისამართიდან შესვლა ჯერ არ არის დაშვებული. ადმინისტრატორმა Firebase-ში უნდა დაამატოს საიტის დომენი.",
          en:"Sign-in is not enabled for this website address yet. The site administrator must authorize this domain in Firebase.",
          ru:"Вход с этого адреса сайта пока не разрешён. Администратор должен добавить домен в Firebase.",
          fa:"ورود از این نشانی وب‌سایت هنوز مجاز نیست. مدیر سایت باید دامنه را در Firebase تأیید کند.",
          he:"הכניסה מכתובת אתר זו עדיין אינה מורשית. מנהל האתר צריך לאשר את הדומיין ב-Firebase.",
          ar:"تسجيل الدخول من عنوان الموقع هذا غير مسموح بعد. يجب على مدير الموقع اعتماد النطاق في Firebase."};
        m = domainError[document.documentElement.lang] || domainError.en;
      }
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
      /* ტელეფონზე pop-up ხშირად იბლოკება ან სესიას კარგავს — მაშინ იმავე
         ფანჯარაში redirect-ს ვუშვებთ და დაბრუნებისას სესია აღდგება. */
      function social(btn, provider) {
        btn.disabled = true; btn.classList.add("loading");
        err.textContent = ""; err.classList.remove("show");
        function release() { btn.disabled = false; btn.classList.remove("loading"); }
        M.auth.signInWithPopup(auth, provider).then(close).catch(function (e) {
          var code = String((e && e.code) || "");
          var soft = /popup-blocked|popup-closed|cancelled-popup|operation-not-supported|web-storage-unsupported|internal-error|missing initial state/i;
          if (soft.test(code) || soft.test(String((e && e.message) || ""))) {
            M.auth.signInWithRedirect(auth, provider).catch(function (e2) { fail(e2); release(); });
            return;
          }
          fail(e); release();
        });
      }
      d.querySelector("#authgoogle").onclick = function () {
        social(this, new M.auth.GoogleAuthProvider());
      };
      d.querySelector("#authfacebook").onclick = function () {
        var p = new M.auth.FacebookAuthProvider();
        p.addScope("email");
        social(this, p);
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
          '<p class="account-eyebrow">Drive On</p><h2>' + esc(T.account || "My page") + '</h2><p>' +
          esc(T.please_sign_in || "") + '</p><div class="account-actions"><button class="btn" type="button" id="accin">' +
          esc(T.sign_in || "Sign in") + '</button><a class="btn ghost" href="' + esc(C.plannerUrl || "/planner/") + '">' +
          esc(T.to_planner || "Planner") + "</a></div></div>";
        var b = document.getElementById("accin"); if (b) b.onclick = openDialog;
        return;
      }
      root.innerHTML = '<div class="acchead"><div class="profile-id"><label class="profile-avatar" title="Upload profile photo">' +
        (u.photoURL ? '<img src="' + esc(u.photoURL) + '" alt="">' : '<span>' + esc((u.displayName || u.email || "?").slice(0,1).toUpperCase()) + '</span>') +
        '<input id="avatarfile" type="file" accept="image/jpeg,image/png,image/webp" aria-label="Upload profile photo"><i aria-hidden="true">+</i></label><div><b>' + esc(u.displayName || u.email) +
        "</b><span>" + esc(u.email || "") + "</span><button class=\"avatar-change\" type=\"button\" id=\"avatarpick\">" +
        (document.documentElement.lang === 'ka' ? 'ფოტოს შეცვლა' : 'Change photo') + "</button></div></div>" +
        '<button class="btn ghost sm" type="button" id="accout">' + esc(T.sign_out || "Sign out") +
        "</button></div><div id=\"accjournal\" class=\"accjournal\"><p class=\"muted\">…</p></div>" +
        '<div id="acclist"><p class="muted">…</p></div>';
      document.getElementById("accout").onclick = function () { M.auth.signOut(auth); };
      var avatarFile=document.getElementById('avatarfile'),avatarPick=document.getElementById('avatarpick');
      if(avatarPick)avatarPick.onclick=function(){avatarFile.click();};
      if(avatarFile)avatarFile.onchange=function(){
        var file=avatarFile.files&&avatarFile.files[0];if(!file)return;
        if(!/^image\/(jpeg|png|webp)$/.test(file.type)||file.size>5*1024*1024){alert(document.documentElement.lang==='ka'?'აირჩიეთ JPG, PNG ან WebP სურათი (მაქს. 5 MB).':'Choose a JPG, PNG or WebP image (max 5 MB).');return;}
        var wrap=avatarFile.closest('.profile-avatar');wrap.classList.add('loading');
        var storage=M.storage.getStorage(app),ext=(file.name.split('.').pop()||'jpg').replace(/[^a-z0-9]/gi,'');
        var ref=M.storage.ref(storage,'avatars/'+u.uid+'/profile.'+ext);
        M.storage.uploadBytes(ref,file).then(function(){return M.storage.getDownloadURL(ref);}).then(function(url){return M.auth.updateProfile(auth.currentUser,{photoURL:url});}).then(function(){user=auth.currentUser;fire();}).catch(function(err){console.warn('[avatar]',err);alert(document.documentElement.lang==='ka'?'ფოტო ვერ აიტვირთა. სცადეთ ხელახლა.':'Photo upload failed. Please try again.');}).finally(function(){wrap.classList.remove('loading');avatarFile.value='';});
      };
      renderProfileCard();
      renderTrips();
      renderBookings();
      renderMessages();
      renderJournal();
    });
  }

  /* „ჩემი ინფორმაცია“ — სახელი და ტელეფონი. ჯავშნის ფორმები აქედან
     ივსება, მაგრამ იქ შეცვლაც შეიძლება — ეს მხოლოდ ნაგულისხმევია. */
  function renderProfileCard() {
    var root = document.getElementById("account");
    if (!root || !user || root.querySelector(".accprofile")) return;
    var lang = document.documentElement.lang || "en";
    var C2 = {
      ka: { title: "ჩემი ინფორმაცია", lead: "ეს მონაცემები ავტომატურად ჩაისმება ავტომობილის მოთხოვნაში — იქვე შეგიძლიათ შეცვლა.", name: "სახელი და გვარი", phone: "ტელეფონი", save: "შენახვა", saved: "შენახულია ✓", err: "ვერ შეინახა — სცადეთ ხელახლა" },
      en: { title: "My details", lead: "These are filled into the car request automatically — you can still change them there.", name: "Full name", phone: "Phone", save: "Save", saved: "Saved ✓", err: "Could not save — try again" },
      ru: { title: "Мои данные", lead: "Эти данные подставляются в заявку на автомобиль — там их можно изменить.", name: "Имя и фамилия", phone: "Телефон", save: "Сохранить", saved: "Сохранено ✓", err: "Не удалось сохранить — попробуйте ещё раз" },
      fa: { title: "اطلاعات من", lead: "این اطلاعات به‌طور خودکار در درخواست خودرو وارد می‌شود — همان‌جا قابل تغییر است.", name: "نام و نام خانوادگی", phone: "تلفن", save: "ذخیره", saved: "ذخیره شد ✓", err: "ذخیره نشد — دوباره تلاش کنید" },
      he: { title: "הפרטים שלי", lead: "פרטים אלה ממולאים אוטומטית בבקשת הרכב — אפשר לשנות אותם שם.", name: "שם מלא", phone: "טלפון", save: "שמירה", saved: "נשמר ✓", err: "השמירה נכשלה — נסו שוב" },
      ar: { title: "بياناتي", lead: "تُدرج هذه البيانات تلقائياً في طلب السيارة — ويمكن تعديلها هناك.", name: "الاسم الكامل", phone: "الهاتف", save: "حفظ", saved: "تم الحفظ ✓", err: "تعذر الحفظ — حاول مجدداً" }
    }[lang] || null;
    var t = C2 || { title: "My details", lead: "", name: "Full name", phone: "Phone", save: "Save", saved: "Saved ✓", err: "Could not save" };
    var box = document.createElement("section");
    box.className = "journal-section accprofile";
    box.innerHTML = "<h2>" + esc(t.title) + "</h2><p class=\"muted\">" + esc(t.lead) + "</p>" +
      '<div class="accprofile-row">' +
      '<label>' + esc(t.name) + '<input id="profname" type="text" autocomplete="name"></label>' +
      '<label>' + esc(t.phone) + '<input id="profphone" type="tel" inputmode="tel" autocomplete="tel"></label>' +
      '</div><div class="accprofile-row2"><button class="btn sm" type="button" id="profsave">' +
      esc(t.save) + '</button><span id="profmsg" role="status"></span></div>';
    var journal = document.getElementById("accjournal");
    root.insertBefore(box, journal);
    var nameEl = box.querySelector("#profname"), phoneEl = box.querySelector("#profphone");
    var msg = box.querySelector("#profmsg");
    getProfile().then(function (p) {
      if (!nameEl.value) nameEl.value = p.name || "";
      if (!phoneEl.value) phoneEl.value = p.phone || "";
    });
    box.querySelector("#profsave").onclick = function () {
      var b = this; b.disabled = true;
      saveProfile({ name: nameEl.value, phone: phoneEl.value })
        .then(function () { msg.textContent = t.saved; })
        .catch(function () { msg.textContent = t.err; })
        .then(function () { b.disabled = false; setTimeout(function () { msg.textContent = ""; }, 2500); });
    };
  }

  /* ჯავშნის ფორმების ავტომატური შევსება — ველები რჩება რედაქტირებადი. */
  function prefillForms() {
    getProfile().then(function (p) {
      if (!p.name && !p.phone) return;
      document.querySelectorAll("form[data-inquiry], form[data-booking], [data-booking-dialog] form").forEach(function (f) {
        var n = f.querySelector('[name="name"]'), ph = f.querySelector('[name="phone"]');
        if (n && !n.value) n.value = p.name;
        if (ph && !ph.value) ph.value = p.phone;
      });
    });
  }
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.querySelector) return;
    var n = f.querySelector('[name="name"]'), ph = f.querySelector('[name="phone"]');
    if (!n && !ph) return;
    var v = { name: n ? n.value : "", phone: ph ? ph.value : "" };
    if (!v.name && !v.phone) return;
    mirror({ name: v.name.trim(), phone: v.phone.trim() });
  }, true);
  function renderBookings() {
    var root = document.getElementById("account"); if (!root || !user || root.querySelector(".accbookings")) return;
    var box=document.createElement("section");box.className="journal-section accbookings";var journal=document.getElementById("accjournal");root.insertBefore(box,journal);
    var lang=document.documentElement.lang||"en";
    var copy={
      ka:{title:"ჩემი ავტომობილები",empty:"ჯერ ავტომობილი არ დაგიჯავშნიათ.",days:"დღე",paid:"გადახდილია",required:"გადასახდელია",pending:"მოლოდინში",confirmed:"დადასტურებული",completed:"დასრულებული",cancelled:"გაუქმებული",rate:"შეაფასეთ ავტომობილი",review:"თქვენი შთაბეჭდილება",send:"შეფასების შენახვა",saved:"შეფასება შენახულია",loadError:"ავტომობილების ისტორია დროებით ვერ ჩაიტვირთა."},
      en:{title:"My cars",empty:"You have not booked a car yet.",days:"days",paid:"Paid",required:"Payment required",pending:"Pending",confirmed:"Confirmed",completed:"Completed",cancelled:"Cancelled",rate:"Rate this car",review:"Share your experience",send:"Save rating",saved:"Rating saved",loadError:"Your rental history could not be loaded right now."},
      ru:{title:"Мои автомобили",empty:"Вы ещё не бронировали автомобиль.",days:"дн.",paid:"Оплачено",required:"Требуется оплата",pending:"Ожидает",confirmed:"Подтверждено",completed:"Завершено",cancelled:"Отменено",rate:"Оцените автомобиль",review:"Ваши впечатления",send:"Сохранить оценку",saved:"Оценка сохранена",loadError:"Историю аренды сейчас загрузить не удалось."}
    }[lang]||null;
    if(!copy)copy={title:"My cars",empty:"You have not booked a car yet.",days:"days",paid:"Paid",required:"Payment required",pending:"Pending",confirmed:"Confirmed",completed:"Completed",cancelled:"Cancelled",rate:"Rate this car",review:"Share your experience",send:"Save rating",saved:"Rating saved",loadError:"Your rental history could not be loaded right now."};
    box.innerHTML='<h2>'+esc(copy.title)+'</h2><p class="muted">…</p>';
    boot.then(function(){
      var bookings=M.db.getDocs(M.db.query(M.db.collection(db,"bookings"),M.db.where("uid","==",user.uid)));
      var reviews=M.db.getDocs(M.db.query(M.db.collection(db,"reviews"),M.db.where("uid","==",user.uid)));
      return Promise.all([bookings,reviews]);
    }).then(function(data){
      var rows=[],reviewByBooking={};
      data[0].forEach(function(d){rows.push(Object.assign({id:d.id},d.data()));});
      data[1].forEach(function(d){var r=Object.assign({id:d.id},d.data());if(r.kind==="car"&&r.bookingId)reviewByBooking[r.bookingId]=r;});
      rows.sort(function(a,b){return String(b.start||"").localeCompare(String(a.start||""));});
      function statusLabel(value){return esc(copy[value]||value||copy.pending);}
      box.innerHTML='<h2>'+esc(copy.title)+' · '+rows.length+'</h2>'+(rows.length?'<div class="booking-list">'+rows.map(function(x){
        var cfg=C.booking||{},rules=cfg.extension_rules||[],review=reviewByBooking[x.id];
        var finished=x.status==="completed"||(!["pending","cancelled"].includes(x.status)&&x.end&&x.end<new Date().toISOString().slice(0,10));
        var ext=x.status==="confirmed"&&cfg.extension_enabled?'<div class="booking-ext">'+rules.filter(function(r){return r.extra_days>=cfg.extension_min_days&&r.extra_days<=cfg.extension_max_days;}).map(function(r){return '<button class="btn sm ghost" data-extend="'+esc(x.id)+'" data-days="'+r.extra_days+'" data-discount="'+r.discount_percent+'">+'+r.extra_days+' '+esc(copy.days)+' · -'+r.discount_percent+'%</button>';}).join('')+'</div>':'';
        var rating=review?'<div class="car-review-saved"><span class="stars">'+"★".repeat(review.rating||0)+"☆".repeat(5-(review.rating||0))+'</span>'+(review.text?'<p>'+esc(review.text)+'</p>':'')+'</div>':finished?'<form class="car-review" data-review-booking="'+esc(x.id)+'"><b>'+esc(copy.rate)+'</b><div class="rating-pick" role="radiogroup">'+[1,2,3,4,5].map(function(n){return '<label><input type="radio" name="rating-'+esc(x.id)+'" value="'+n+'" required><span>★</span></label>';}).join('')+'</div><textarea maxlength="800" placeholder="'+esc(copy.review)+'"></textarea><button class="btn sm" type="submit">'+esc(copy.send)+'</button><span role="status"></span></form>':'';
        return '<article class="booking-card"><div class="booking-card-head"><div><b>'+esc(x.carName||x.carSlug)+'</b><span>'+esc(x.start)+' → '+esc(x.end)+' · '+(x.days||1)+' '+esc(copy.days)+'</span></div><span class="booking-status '+esc(x.status||"pending")+'">'+statusLabel(x.status)+'</span></div><div class="booking-facts"><span>'+Math.round(x.paymentDueGel||0)+' GEL</span><span>'+esc(x.paymentStatus==="paid"?copy.paid:copy.required)+'</span></div>'+ext+rating+'</article>';
      }).join('')+'</div>':'<p class="note">'+esc(copy.empty)+'</p>');
      box.querySelectorAll('[data-extend]').forEach(function(b){b.onclick=function(){var x=rows.find(function(r){return r.id===b.dataset.extend;});if(!x)return;b.disabled=true;boot.then(function(){return M.db.addDoc(M.db.collection(db,'extensionRequests'),{uid:user.uid,bookingId:x.id,carSlug:x.carSlug,extraDays:parseInt(b.dataset.days,10),discountPercent:parseInt(b.dataset.discount,10),status:'pending',paymentStatus:'required',created:M.db.serverTimestamp()});}).then(function(){b.textContent='✓';}).catch(function(){b.disabled=false;});};});
      box.querySelectorAll('.car-review').forEach(function(form){form.onsubmit=function(e){e.preventDefault();var booking=rows.find(function(r){return r.id===form.dataset.reviewBooking;});var checked=form.querySelector('input:checked'),status=form.querySelector('[role="status"]');if(!booking||!checked)return;var button=form.querySelector('button');button.disabled=true;status.textContent='…';M.db.addDoc(M.db.collection(db,'reviews'),{uid:user.uid,bookingId:booking.id,carSlug:booking.carSlug||'',subject:booking.carName||booking.carSlug||'',kind:'car',rating:parseInt(checked.value,10),text:form.querySelector('textarea').value.trim(),authorName:user.displayName||user.email||'Traveller',created:M.db.serverTimestamp()}).then(function(){status.textContent=copy.saved;setTimeout(function(){box.remove();renderBookings();},500);}).catch(function(){button.disabled=false;status.textContent='!';});};});
    }).catch(function(err){console.warn('[bookings]',err);box.innerHTML='<h2>'+esc(copy.title)+'</h2><p class="note error">'+esc(copy.loadError)+'</p>';});
  }
  function renderMessages() {
    var account = document.getElementById("account"); if (!account || !user || account.querySelector(".accmessages")) return;
    var box = document.createElement("section"); box.className = "journal-section accmessages";
    var journal = document.getElementById("accjournal"); account.insertBefore(box, journal); box.innerHTML = "<h2>Messages</h2><p class=\"muted\">…</p>";
    boot.then(function () {
      var q = M.db.query(M.db.collection(db, "conversations"), M.db.where("memberIds", "array-contains", user.uid));
      return M.db.getDocs(q);
    }).then(function (snap) {
      var conversations = []; snap.forEach(function (doc) { conversations.push(Object.assign({ id: doc.id }, doc.data())); });
      if (!conversations.length) { box.innerHTML = '<h2>Messages · 0</h2><p class="note">No conversations yet.</p>'; return; }
      return Promise.all(conversations.map(function (conversation) {
        return M.db.getDocs(M.db.collection(db, "conversations", conversation.id, "messages")).then(function (messages) {
          conversation.messages = []; messages.forEach(function (doc) { conversation.messages.push(Object.assign({ id: doc.id }, doc.data())); });
          conversation.messages.sort(function (a, b) { return (a.created && a.created.seconds || 0) - (b.created && b.created.seconds || 0); });
          return conversation;
        });
      })).then(function (rows) {
        box.innerHTML = '<h2>Messages · ' + rows.length + '</h2><div class="conversation-list">' + rows.map(function (c) {
          var other = (c.memberIds || []).filter(function (id) { return id !== user.uid; })[0] || "";
          return '<article class="conversation" data-conversation="' + esc(c.id) + '"><b>' + esc(c.otherName || other) + '</b><div class="message-list">' + c.messages.map(function (message) {
            return '<p class="message ' + (message.uid === user.uid ? "mine" : "theirs") + '">' + esc(message.text) + "</p>";
          }).join("") + '</div><form><label><span class="sr-only">Message</span><textarea required maxlength="2000"></textarea></label><button class="btn sm" type="submit">Send</button><span role="status"></span></form></article>';
        }).join("") + "</div>";
        box.querySelectorAll(".conversation").forEach(function (card) {
          card.querySelector("form").onsubmit = function (event) {
            event.preventDefault(); var input = card.querySelector("textarea"), status = card.querySelector('[role="status"]');
            var value = input.value.trim(); if (!value) return; status.textContent = "…";
            M.db.addDoc(M.db.collection(db, "conversations", card.dataset.conversation, "messages"), {
              uid: user.uid, text: value, created: M.db.serverTimestamp()
            }).then(function () { input.value = ""; renderMessagesRefresh(); }).catch(function () { status.textContent = "!"; });
          };
        });
      });
    }).catch(function () { box.innerHTML = ""; });
    function renderMessagesRefresh() { box.remove(); renderMessages(); }
  }
  function renderTrips() {
    var box = document.getElementById("acclist");
    if (!box) return;
    Promise.all([listTrips(), listMemories()]).then(function (data) {
      var trips = data[0], memories = data[1];
      trips.forEach(function (t) { t.memoryUrls = memories[t.id] || []; });
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
            var note = document.createElement("div");
            note.className = "share-result"; note.setAttribute("role", "status");
            note.innerHTML = '<input readonly value="' + esc(url) + '"><button class="btn sm ghost" type="button">Copy</button>';
            b.closest(".tripcard").appendChild(note);
            note.querySelector("button").onclick = function () {
              if (navigator.clipboard) navigator.clipboard.writeText(url);
              this.textContent = "Copied";
            };
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
      box.querySelectorAll('[data-memory]').forEach(function (input) {
        input.onchange = function () {
          var label=input.closest('.memory-upload'); if(label) label.classList.add('loading');
          uploadMemories(input.dataset.memory, input.files).then(renderTrips).catch(function(e){
            if(label){label.classList.remove('loading');label.classList.add('upload-error');label.title=String(e&&e.message||e);}
          });
        };
      });
    }).catch(function (e) {
      box.innerHTML = '<div class="note">' + esc(String(e && e.message || e)) + "</div>";
    });
  }
  function listMemories() {
    return boot.then(function () {
      if (!user) return {};
      var q = M.db.query(M.db.collection(db, 'tripMemories'), M.db.where('uid', '==', user.uid));
      return M.db.getDocs(q).then(function (snap) {
        var out = {}; snap.forEach(function (d) { var x=d.data(); out[x.tripId]=x.photoUrls||[]; }); return out;
      });
    });
  }
  function tripHref(u) {
    /* ძველი შენახული ბმულები მთავარ გვერდზე მიდიოდა — ჰეშს ვიღებთ და
       მიმდინარე ენის „ჩემი ტურის" გვერდზე გადაგვყავს, ენა არ იცვლება */
    var s = String(u || ""), i = s.indexOf("#trip=");
    if (i < 0) return s;
    return (C.tripUrl || "/trip/") + s.slice(i);
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
      (t.url ? '<a class="btn sm ghost" href="' + esc(tripHref(t.url)) + '">' + esc(T.open || "Open") + "</a>" : "") +
      '<button class="btn sm ghost" type="button" data-public="' + esc(t.id) + '">' +
      (t.visibility === "public" ? "Public: on" : "Public: off") + "</button>" +
      '<button class="btn sm ghost" type="button" data-share="' + esc(t.id) + '">Share</button>' +
      '<label class="btn sm ghost memory-upload">📷 ' + esc(T.memories || 'Memories') +
      '<input type="file" accept="image/*" multiple data-memory="' + esc(t.id) + '"></label>' +
      ((t.memoryUrls || []).length ? '<div class="memory-strip">' + t.memoryUrls.slice(0, 8).map(function(url){
        return '<a href="'+esc(url)+'" target="_blank" rel="noopener"><img src="'+esc(url)+'" alt=""></a>';
      }).join('') + '</div>' : '') +
      '<button class="btn sm ghost" type="button" data-del="' + esc(t.id) + '">' + esc(T.delete || "Delete") + "</button>" +
      "</div></div>";
  }

  function uploadMemories(tripId, files) {
    files = Array.prototype.slice.call(files || []).slice(0, 20);
    if (!user || !files.length) return Promise.resolve();
    return boot.then(function () {
      var storage = M.storage.getStorage(app);
      return Promise.all(files.map(function (file) {
        if (!/^image\//.test(file.type)) return Promise.reject(new Error(T.image_only || 'Only image files are allowed.'));
        if (file.size > 10 * 1024 * 1024) return Promise.reject(new Error(T.image_too_large || 'Each image must be under 10 MB.'));
        var name = Date.now() + '-' + Math.random().toString(36).slice(2) + '-' + file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
        var ref = M.storage.ref(storage, 'memories/' + user.uid + '/' + tripId + '/' + name);
        return M.storage.uploadBytes(ref, file).then(function () { return M.storage.getDownloadURL(ref); });
      })).then(function (urls) {
        var ref = M.db.doc(db, 'tripMemories', user.uid + '_' + tripId);
        return M.db.getDoc(ref).then(function (snap) {
          var old = snap.exists() ? (snap.data().photoUrls || []) : [];
          return M.db.setDoc(ref, { uid:user.uid, tripId:tripId, photoUrls:old.concat(urls).slice(0,80), updated:M.db.serverTimestamp() }, { merge:true });
        });
      });
    });
  }

  function renderJournal() {
    var root = document.getElementById('accjournal');
    if (!root || !user) return;
    boot.then(function () {
      var places = M.db.getDoc(M.db.doc(db, 'userPlaces', user.uid));
      var rq = M.db.query(M.db.collection(db, 'reviews'), M.db.where('uid', '==', user.uid));
      return Promise.all([places, M.db.getDocs(rq)]);
    }).then(function (data) {
      var visits = data[0].exists() ? (data[0].data().visits || (data[0].data().slugs || []).map(function(s){return {slug:s};})) : [];
      visits.sort(function(a,b){return String(b.visitedAt||'').localeCompare(String(a.visitedAt||''));});
      var reviews=[]; data[1].forEach(function(d){reviews.push(d.data());});
      reviews.sort(function(a,b){return (b.created&&b.created.seconds||0)-(a.created&&a.created.seconds||0);});
      root.innerHTML = '<section class="journal-section"><h2>' + esc(T.visit_history || 'Visit history') + ' · ' + visits.length + '</h2>' +
        (visits.length ? '<div class="visit-history">' + visits.map(function(v){return '<div><time>' + esc(v.visitedAt||'—') + '</time><b>' + esc(String(v.slug||'').replace(/-/g,' ')) + '</b></div>';}).join('') + '</div>' : '<p class="note">' + esc(T.no_visits || 'No visited places yet.') + '</p>') + '</section>' +
        '<section class="journal-section"><h2>' + esc(T.my_reviews || 'My reviews') + ' · ' + reviews.length + '</h2>' +
        (reviews.length ? '<div class="my-reviews">' + reviews.map(function(r){return '<article><b>' + esc(r.subject||'') + '</b><span class="stars">' + '★'.repeat(r.rating||0) + '</span><p>' + esc(r.text||'') + '</p>' + (r.photoUrl?'<img src="'+esc(r.photoUrl)+'" alt="">':'') + '</article>';}).join('') + '</div>' : '<p class="note">' + esc(T.no_reviews || 'No reviews yet.') + '</p>') + '</section>';
    }).catch(function(){ root.innerHTML=''; });
  }

  window.FH = { on: on, saveTrip: saveTrip, listTrips: listTrips, shareTrip: shareTrip,
                loadShared: loadShared, openDialog: openDialog,
                getProfile: getProfile, saveProfile: saveProfile,
                firebase: function () { return boot.then(function () { return { db: db, auth: auth, M: M, app: app }; }); },
                user: function () { return user; } };

  function init() {
    headerBox(); accountPage(); prefillForms();
    /* დიალოგი გვიან იხსნება — გახსნისას ხელახლა შევავსოთ */
    document.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("[data-booking-open], [data-book], [data-dow-book]")) {
        setTimeout(prefillForms, 60);
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
