(function () {
  var root = document.getElementById("booking-admin");
  var cfg = window.FH_ADMIN_CFG || {};
  var SDK = "https://www.gstatic.com/firebasejs/10.12.5/";
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>\"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  }); }
  function note(t, c) { root.innerHTML = '<div class="admin-note ' + (c || "") + '">' + esc(t) + "</div>"; }
  if (!root || !cfg.apiKey) { if (root) note("Firebase configuration is missing.", "error"); return; }
  Promise.all([import(SDK + "firebase-app.js"), import(SDK + "firebase-auth.js"), import(SDK + "firebase-firestore.js")])
    .then(function (m) {
      var app = m[0].initializeApp(cfg), A = m[1], D = m[2];
      var auth = A.getAuth(app), db = D.getFirestore(app);
      function login() {
        root.innerHTML = '<section class="admin-login"><h1>ჯავშნების მართვა</h1><p>შედით Firebase-ის ადმინისტრატორის ანგარიშით.</p><button class="btn" id="admin-google">Google-ით შესვლა</button></section>';
        root.querySelector("button").onclick = function () {
          A.signInWithPopup(auth, new A.GoogleAuthProvider()).catch(function (e) { note(e.message, "error"); });
        };
      }
      function load(user) {
        user.getIdTokenResult(true).then(function (token) {
          if (!token.claims.admin) { note("ამ ანგარიშს ადმინისტრატორის უფლება არ აქვს.", "error"); return; }
          root.innerHTML = '<header class="admin-head"><div><h1>ჯავშნები</h1><p>' + esc(user.email || "") + '</p></div><button class="btn ghost" id="admin-out">გასვლა</button></header><div class="admin-filters"><select id="admin-status"><option value="">ყველა სტატუსი</option><option>pending</option><option>confirmed</option><option>cancelled</option><option>completed</option></select><button class="btn ghost" id="admin-refresh">განახლება</button></div><div id="admin-list">იტვირთება…</div>';
          root.querySelector("#admin-out").onclick = function () { A.signOut(auth); };
          root.querySelector("#admin-refresh").onclick = query;
          root.querySelector("#admin-status").onchange = query;
          query();
          function query() {
            D.getDocs(D.collection(db, "bookings")).then(function (snap) {
              var rows = []; snap.forEach(function (doc) { rows.push(Object.assign({ id: doc.id }, doc.data())); });
              rows.sort(function (a, b) { return String(b.start || "").localeCompare(String(a.start || "")); });
              var status = root.querySelector("#admin-status").value;
              if (status) rows = rows.filter(function (x) { return x.status === status; });
              draw(rows);
            }).catch(function (e) { root.querySelector("#admin-list").textContent = e.message; });
          }
          function draw(rows) {
            var box = root.querySelector("#admin-list");
            box.innerHTML = rows.map(function (x) {
              var who = x.name ? esc(x.name) : "—";
              if (x.phone) who += ' · <a href="tel:' + esc(x.phone) + '" dir="ltr">' + esc(x.phone) + "</a>";
              if (x.email) who += ' · <a href="mailto:' + esc(x.email) + '">' + esc(x.email) + "</a>";
              var extra = [];
              if (x.pickup) extra.push("აღება: " + esc(x.pickup));
              if (x.assignedPlate) extra.push("ნომერი: " + esc(x.assignedPlate));
              if (x.notes) extra.push(esc(x.notes));
              return '<article class="admin-booking" data-id="' + esc(x.id) + '"><div><b>' + esc(x.carName || x.carSlug) + '</b><span class="admin-who">' + who + '</span><span>' + esc(x.start) + " → " + esc(x.end) + " · " + x.days + " დღე · " + (x.drivers || 1) + ' მძღოლი</span><span>' + Math.round(x.paymentDueGel || 0) + " GEL · გადახდა: " + esc(x.paymentStatus) + '</span>' + (extra.length ? '<span class="admin-extra">' + extra.join(" · ") + "</span>" : "") + '</div><label>სტატუსი<select data-status><option>pending</option><option>confirmed</option><option>cancelled</option><option>completed</option></select></label><label>გადახდა<select data-payment><option>required</option><option>pending</option><option>paid</option><option>refunded</option></select></label><button class="btn sm" data-save>შენახვა</button></article>';
            }).join("") || '<p class="admin-note">ჩანაწერი არ არის.</p>';
            box.querySelectorAll(".admin-booking").forEach(function (card) {
              var x = rows.find(function (row) { return row.id === card.dataset.id; });
              card.querySelector("[data-status]").value = x.status || "pending";
              card.querySelector("[data-payment]").value = x.paymentStatus || "required";
              card.querySelector("[data-save]").onclick = function () {
                var button = this; button.disabled = true;
                D.updateDoc(D.doc(db, "bookings", x.id), {
                  status: card.querySelector("[data-status]").value,
                  paymentStatus: card.querySelector("[data-payment]").value,
                  updated: D.serverTimestamp()
                }).then(function () { button.textContent = "✓"; })
                  .catch(function (e) { button.disabled = false; button.textContent = e.message; });
              };
            });
          }
        }).catch(function (e) { note(e.message, "error"); });
      }
      A.onAuthStateChanged(auth, function (user) { if (user) load(user); else login(); });
    }).catch(function (e) { note(e.message, "error"); });
}());
