/* Static-first rental inquiry: contextual WhatsApp plus Netlify Forms fallback. */
(function () {
  var TEXT = {
    ka: { busy: "ამ თარიღებზე ეს მოდელი დაკავებული ჩანს — მოთხოვნას მაინც განვიხილავთ.", choose: "მიუთითეთ დაწყებისა და დასრულების თარიღები.", invalid: "დასრულება დაწყების შემდეგ უნდა იყოს.", days: "დღე", rate: "დღიური ფასი", total: "ქირა", deposit: "დეპოზიტი", due: "გადასახდელი", login: "მოთხოვნის გასაგზავნად შედით ანგარიშში.", sending: "იგზავნება…", success: "მოთხოვნა მიღებულია. ჯავშანი დადასტურებული არ არის, სანამ გადახდა არ შესრულდება.", failed: "მოთხოვნა ვერ გაიგზავნა. სცადეთ ხელახლა.", season: "ივლის–აგვისტოს სეზონური {p}% უკვე ჩათვლილია ქირაში: {s}", seasonPart: "ივლის–აგვისტოს სეზონური {p}% უკვე ჩათვლილია ქირაში: {d} ღამიდან {n} ღამეზე, {s}", young: "{age} წლამდე მძღოლს ემატება ახალგაზრდა მძღოლის დანამატი {min}–{max} ₾ დღეში." },
    en: { busy: "This model looks fully booked for these dates — we will still review your request.", choose: "Choose start and end dates.", invalid: "End must be after start.", days: "days", rate: "Daily rate", total: "Rental", deposit: "Deposit", due: "Payment due", login: "Sign in to send the request.", sending: "Sending…", success: "Request received. The booking is not confirmed until payment is completed.", failed: "The request could not be sent. Please try again.", season: "The July–August seasonal {p}% is already included in the rental: {s}", seasonPart: "The July–August seasonal {p}% is already included in the rental: {n} of {d} nights, {s}", young: "Drivers under {age} pay a young driver surcharge of {min}–{max} GEL per day." },
    ru: { busy: "На эти даты эта модель занята — мы всё равно рассмотрим ваш запрос.", choose: "Укажите даты начала и окончания.", invalid: "Дата окончания должна быть позже начала.", days: "дн.", rate: "Цена в день", total: "Аренда", deposit: "Депозит", due: "К оплате", login: "Войдите, чтобы отправить запрос.", sending: "Отправка…", success: "Запрос получен. Бронирование не подтверждено до оплаты.", failed: "Не удалось отправить запрос.", season: "Сезонная надбавка июля–августа {p}% уже включена в стоимость аренды: {s}", seasonPart: "Сезонная надбавка июля–августа {p}% уже включена в стоимость аренды: {n} из {d} ночей, {s}", young: "Водителям младше {age} лет начисляется надбавка молодого водителя {min}–{max} лари в сутки." },
    fa: { busy: "در این تاریخ‌ها این خودرو رزرو به نظر می‌رسد — درخواست شما را بررسی می‌کنیم.", choose: "تاریخ شروع و پایان را انتخاب کنید.", invalid: "پایان باید بعد از شروع باشد.", days: "روز", rate: "نرخ روزانه", total: "اجاره", deposit: "ودیعه", due: "مبلغ پرداخت", login: "برای ارسال درخواست وارد شوید.", sending: "در حال ارسال…", success: "درخواست دریافت شد. رزرو تا زمان پرداخت تأیید نمی‌شود.", failed: "ارسال درخواست ناموفق بود.", season: "ضریب فصلی {p}% ژوئیه و اوت در مبلغ اجاره لحاظ شده است: {s}", seasonPart: "ضریب فصلی {p}% ژوئیه و اوت در مبلغ اجاره لحاظ شده است: {n} شب از {d} شب، {s}", young: "رانندگان زیر {age} سال روزانه {min} تا {max} لاری هزینهٔ رانندهٔ جوان می‌پردازند." },
    he: { busy: "בתאריכים אלה הרכב נראה תפוס — נבדוק את הבקשה בכל מקרה.", choose: "בחרו תאריכי התחלה וסיום.", invalid: "הסיום חייב להיות אחרי ההתחלה.", days: "ימים", rate: "מחיר יומי", total: "השכרה", deposit: "פיקדון", due: "לתשלום", login: "יש להתחבר כדי לשלוח בקשה.", sending: "שולח…", success: "הבקשה התקבלה. ההזמנה אינה מאושרת עד להשלמת התשלום.", failed: "לא ניתן לשלוח את הבקשה.", season: "מקדם עונתי של {p}% ליולי–אוגוסט כבר כלול בהשכרה: {s}", seasonPart: "מקדם עונתי של {p}% ליולי–אוגוסט כבר כלול בהשכרה: {n} מתוך {d} לילות, {s}", young: "נהגים מתחת לגיל {age} משלמים תוספת נהג צעיר של {min} עד {max} לארי ליום." },
    ar: { busy: "في هذه التواريخ يبدو الطراز محجوزاً — سنراجع طلبك على أي حال.", choose: "اختر تاريخي البداية والنهاية.", invalid: "يجب أن تكون النهاية بعد البداية.", days: "أيام", rate: "السعر اليومي", total: "الإيجار", deposit: "التأمين", due: "المبلغ المستحق", login: "سجّل الدخول لإرسال الطلب.", sending: "جارٍ الإرسال…", success: "تم استلام الطلب. لا يتأكد الحجز حتى يكتمل الدفع.", failed: "تعذر إرسال الطلب.", season: "المعامل الموسمي {p}% ليوليو وأغسطس محتسب في الإيجار: {s}", seasonPart: "المعامل الموسمي {p}% ليوليو وأغسطس محتسب في الإيجار: {n} من {d} ليلة، {s}", young: "يدفع السائقون دون {age} سنة رسوم سائق شاب من {min} إلى {max} لاري يومياً." }
  };
  function n(v) { v = Number(v); return Number.isFinite(v) ? v : 0; }
  /* დღეები UTC-ში: ლოკალური დროით თვლა შემოდგომის საათის გადაწევისას
     25-საათიან დღეს აჩენდა და ceil-ი ზედმეტ დღეს (და ზოგჯერ სხვა ტარიფის
     ზოლს) აბრუნებდა. */
  function utcDays(start, end) {
    var a = String(start).split('-'), b = String(end).split('-');
    if (a.length !== 3 || b.length !== 3) return 0;
    return Math.round((Date.UTC(+b[0], +b[1] - 1, +b[2]) -
      Date.UTC(+a[0], +a[1] - 1, +a[2])) / 86400000);
  }
  /* დღევანდელი თარიღი ლოკალურად: toISOString UTC-ს იძლევა და თბილისში
     00:00–04:00 შუალედში გუშინდელ დღეს უშვებდა მინიმუმად. */
  function todayLocal() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') +
      '-' + String(d.getDate()).padStart(2, '0');
  }
  function calc(root) {
    var start = root.querySelector('[name="start"]').value;
    var end = root.querySelector('[name="end"]').value;
    if (!start || !end) return null;
    var days = utcDays(start, end);
    if (days < 1) return { invalid: true };
    var rate = n(days >= 30 ? root.getAttribute("data-price-30") :
      (days >= 7 ? root.getAttribute("data-price-7-29") : root.getAttribute("data-price-1-6")));
    var deposit = n(root.dataset.deposit), rental = rate * days;
    return { start: start, end: end, days: days, rate: rate, deposit: deposit, rental: rental, due: rental + deposit };
  }
  function money(v) { return Math.round(v) + " ₾"; }
  function init(root) {
    var lang = root.dataset.lang || "en", t = TEXT[lang] || TEXT.en;
    var out = root.querySelector(".booking-summary"), button = root.querySelector('[type="submit"]'), wa=root.querySelector("[data-wa]");
    var inputs = root.querySelectorAll("input");
    var today = todayLocal();
    root.querySelector('[name="start"]').min = today;
    root.querySelector('[name="end"]').min = today;
    function draw(message) {
      if (message) { out.textContent = message; return null; }
      var x = calc(root);
      if (!x) { out.textContent = t.choose; return null; }
      if (x.invalid) { out.textContent = t.invalid; return null; }
      out.textContent = x.days + " " + t.days + " · " + t.rate + ": " + money(x.rate) + " · " + t.total + ": " + money(x.rental) + " · " + t.deposit + ": " + money(x.deposit) + " · " + t.due + ": " + money(x.due);
      return x;
    }
    inputs.forEach(function (el) { el.addEventListener("input", function () {
      if (el.name === "start") root.querySelector('[name="end"]').min = el.value || today;
      draw();
    }); });
    function context(){var x=draw(),fd=new FormData(root);if(!x||x.invalid)return null;return "Hello, I want to rent "+root.dataset.carName+" from "+x.start+" to "+x.end+" ("+x.days+" days), pickup at "+(fd.get("pickup")||"not specified")+", return at "+(fd.get("return_location")||fd.get("pickup")||"not specified")+". Travellers: "+(fd.get("travellers")||1)+". Estimated rental: "+money(x.rental)+". Page: "+location.href+(fd.get("notes")?". Notes: "+fd.get("notes"):"");}
    if(wa)wa.addEventListener("click",function(){var msg=context();if(!msg)return;var cfg=window.FH_CFG||{},num=String(cfg.whatsapp||"").replace(/\D/g,"");if(!num){out.textContent=t.failed;return;}window.open("https://wa.me/"+num+"?text="+encodeURIComponent(msg),"_blank","noopener");});
    root.addEventListener("submit",function(e){var x=draw();if(!x||x.invalid){e.preventDefault();return;}root.querySelector('[name="page_url"]').value=location.href;});
    draw();
  }
  function boot() { document.querySelectorAll("[data-booking]").forEach(init); }
  function initInquiry(root) {
    var status=root.querySelector('.inquiry-status'), today=todayLocal();
    var lang=root.dataset.lang||'en', t=TEXT[lang]||TEXT.en;
    var start=root.querySelector('[name="start"]'),end=root.querySelector('[name="end"]');
    start.min=today;end.min=today;start.addEventListener('input',function(){end.min=start.value||today;});
    function message(){var fd=new FormData(root),lang=root.dataset.lang||'en';return (lang==='ka'?'გამარჯობა, მსურს ავტომობილის დაჯავშნა. ':'Hello, I would like to book a car. ')+
      (fd.get('requested_car')?'Car: '+fd.get('requested_car')+'. ':'')+(fd.get('start')||'-')+' — '+(fd.get('end')||'-')+'. '+
      'Name: '+(fd.get('name')||'-')+'. Phone: '+(fd.get('phone')||'-')+'. Page: '+location.href+(fd.get('notes')?'. Notes: '+fd.get('notes'):'');}
    root.querySelector('[data-inquiry-wa]').addEventListener('click',function(){if(!root.reportValidity())return;var num=String((window.FH_CFG||{}).whatsapp||'').replace(/\D/g,'');if(!num){status.textContent='WhatsApp is not configured.';return;}window.open('https://wa.me/'+num+'?text='+encodeURIComponent(message()),'_blank','noopener');});

    /* ── ფასის შეფასება დიალოგში ────────────────────────────────────────
       ბენდები ზუსტად ისეთია, როგორიც გამქირავებლის პროგრამაშია:
       1+ / 7+ / 30+ ღამე. დღეები exclusive-ია (წაყვანის დღე არ ითვლება). */
    var quoteBox = root.querySelector('[data-quote]');
    function drawQuote() {
      if (!quoteBox) return null;
      var q = quoteFor(root);
      if (!q) { quoteBox.textContent = ''; return null; }
      if (q.slug) fetchLive(q.slug); /* cached; redraws via fh:live-availability */
      quoteBox.textContent = q.days + ' ' + t.days +
        (q.rate ? ' · ' + t.rate + ': ' + money(q.rate) + ' · ' + t.total + ': ' + money(q.rental) +
          (q.deposit ? ' · ' + t.deposit + ': ' + money(q.deposit) : '') : '');
      /* სეზონური დანამატი უკვე ქირაშია — იმავე ხაზზე ვწერთ, რამდენია და
         რატომ, რომ ბაზისურ ტარიფსა და ჯამს შორის სხვაობა არ იკითხებოდეს
         შეცდომად. */
      if (q.seasonGel > 0 && t.season) {
        /* სრულად პიკურ შუალედზე ღამეების თვლა ზედმეტია („5-დან 5“) და
           ნაწილში ბრუნვაც ეშლება — ამიტომ ორი ცალკე ფრაზაა. */
        var st = (q.peakNights < q.days && t.seasonPart) ? t.seasonPart : t.season;
        quoteBox.textContent += ' · ' + fill(st, {
          p: q.seasonPercent, n: q.peakNights, d: q.days, s: money(q.seasonGel)
        });
      }
      if (q.slug && t.busy && busyFor(q.slug, q.start, q.end)) {
        quoteBox.textContent += ' · ⚠ ' + t.busy;
      }
      return q;
    }
    /* ასაკის დანამატი თარიღებზე არ არის დამოკიდებული და მძღოლის ასაკი
       ჩვენ არ ვიცით — ამიტომ ეს უბრალოდ ერთი საინფორმაციო ხაზია ფასის
       ქვეშ და არაფერს კეტავს. */
    var yc = youngCfg();
    if (quoteBox && yc && t.young && !root.querySelector('[data-young-note]')) {
      var note = document.createElement('p');
      note.className = 'inquiry-note';
      note.setAttribute('data-young-note', '');
      note.style.cssText = 'margin:6px 0 0;font-size:12px;color:var(--muted)';
      note.textContent = fill(t.young, { age: yc.age, min: yc.min, max: yc.max });
      quoteBox.parentNode.insertBefore(note, quoteBox.nextSibling);
    }
    ['start', 'end'].forEach(function (n) {
      var el = root.querySelector('[name="' + n + '"]');
      if (el) el.addEventListener('input', drawQuote);
    });
    document.addEventListener('fh:booking-car', drawQuote);
    document.addEventListener('fh:live-availability', drawQuote);
    drawQuote();

    /* ── გაგზავნა ───────────────────────────────────────────────────────
       ორი მისამართით ერთდროულად:
         1. Firestore `bookings` — აქედან კითხულობს გამქირავებლის პროგრამა
         2. Netlify Forms — ლიდი არ იკარგება მაშინაც, თუ Firebase ვერ მუშაობს
       თუ Firebase საერთოდ არ არის ჩართული, ფორმა ისე იქცევა, როგორც აქამდე. */
    if (window.FH && typeof window.FH.firebase === 'function') {
      root.dataset.fhCloud = '1';   /* ajaxifyForms-მა ხელი აღარ ახლოს */
      root.addEventListener('submit', function (ev) {
        ev.preventDefault();
        root.querySelector('[name="page_url"]').value = location.href;
        if (!root.reportValidity()) return;
        var button = root.querySelector('[type="submit"]');
        if (button) button.disabled = true;
        status.textContent = t.sending;
        var cloud = false;
        sendToCloud(root, drawQuote())
          .then(function () { cloud = true; })
          .catch(function (err) { console.warn('[booking] cloud:', err && (err.code || err.message)); })
          /* Netlify-ს ასლი მიდის, მაგრამ no-cors პასუხი 404-ზეც „წარმატებაა" —
             ამიტომ ის აღარასოდეს ითვლება მიწოდების დასტურად. */
          .then(function () { return postForm(root).catch(function () { return null; }); })
          .then(function () {
            /* წარმატება მხოლოდ მაშინ ითქმის, როცა ჩანაწერი მართლა დაიწერა.
               აქამდე ორივე გზის ჩავარდნისას მაინც „მიღებულია" ეწერებოდა და
               ფორმა იშლებოდა — კლიენტი დაჯავშნილი ეგონა, მოთხოვნა კი არსად
               იყო. */
            status.textContent = cloud ? t.success : t.failed;
            if (cloud && window.RentUpAnalytics) window.RentUpAnalytics.track('booking_submitted', window.RentUpAnalytics.bookingParams(root));
            if (cloud) {
              root.reset();
              if (quoteBox) quoteBox.textContent = '';
            }
          })
          .catch(function () { status.textContent = cloud ? t.success : t.failed; })
          .then(function () { if (button) button.disabled = false; });
      });
    } else {
      root.addEventListener('submit', function () {
        root.querySelector('[name="page_url"]').value = location.href;
        if (window.RentUpAnalytics) try { sessionStorage.setItem('rentup_pending_booking', JSON.stringify(window.RentUpAnalytics.bookingParams(root))); } catch (e) {}
      });
    }
  }

  /* ── სეზონური კოეფიციენტი და ახალგაზრდა მძღოლის დანამატი ────────────
     ორივე FAQ-შია გამოცხადებული, ფასის ხაზში კი აქამდე არსად ჩანდა:
     აგვისტოს ჯავშანს ~15%-ით ნაკლები ეწერა, ვიდრე ფილიალში იხდიდა.
     კონფიგურაცია არასავალდებულოა — ძველ, ქეშირებულ გვერდზე window.FH_CFG
     ამ ველების გარეშე მოვა და ყველაფერი ისე მუშაობს, როგორც აქამდე. */
  function fill(str, vars) {
    return String(str).replace(/\{(\w+)\}/g, function (m, k) {
      return (vars[k] === undefined || vars[k] === null) ? m : String(vars[k]);
    });
  }
  function seasonCfg() {
    var s = (window.FH_CFG || {}).season;
    if (!s || !s.peakMonths || !s.peakMonths.length) return null;
    var pct = Number(s.peakPercent);
    if (!(pct > 0)) return null;
    return { months: s.peakMonths, percent: pct };
  }
  function youngCfg() {
    var y = (window.FH_CFG || {}).youngDriver;
    if (!y) return null;
    var age = Number(y.underAge), lo = Number(y.minGel), hi = Number(y.maxGel);
    if (!(age > 0) || !(lo > 0) || !(hi > 0)) return null;
    return { age: age, min: lo, max: hi };
  }
  /* პიკურ თვეებში მოხვედრილი ღამეების რაოდენობა. ღამეს ითვლის დაწყების
     თარიღი (დაბრუნების დღე exclusive-ია, ისევე როგორც utcDays-ში), ამიტომ
     28 ივნისი → 3 ივლისი სწორად იძლევა ივლისში 2 ღამეს. UTC-ში ითვლება,
     რომ საათის გადაწევამ დღე არ დაკარგოს. */
  function peakNights(start, end, months) {
    var a = String(start).split('-'), b = String(end).split('-');
    if (a.length !== 3 || b.length !== 3) return 0;
    var t = Date.UTC(+a[0], +a[1] - 1, +a[2]), e = Date.UTC(+b[0], +b[1] - 1, +b[2]);
    if (!isFinite(t) || !isFinite(e) || !(e > t)) return 0;
    /* აშკარად შეცდომით აკრეფილ თარიღზე (ათწლეულები) ციკლს არ ვუშვებთ. */
    if ((e - t) / 86400000 > 3660) return 0;
    var count = 0;
    for (; t < e; t += 86400000) {
      if (months.indexOf(new Date(t).getUTCMonth() + 1) >= 0) count++;
    }
    return count;
  }

  /* დღეების დათვლა და ტარიფის ბენდი — იგივე წესი, რაც პროგრამაშია. */
  function quoteFor(root) {
    var fd = new FormData(root);
    var start = String(fd.get('start') || ''), end = String(fd.get('end') || '');
    if (!validDate(start) || !validDate(end)) return null;
    var days = utcDays(start, end);
    if (!(days >= 1)) return null;
    var slug = String(fd.get('car_slug') || '');
    var c = ((window.FH_CFG || {}).cars || {})[slug];
    if (!c) return { days: days, slug: slug, start: start, end: end, rate: 0, rental: 0, deposit: 0, due: 0, peakNights: 0, seasonPercent: 0, seasonGel: 0 };
    /* ზოლების ჯაჭვი დაცვით: p1 -> p7 -> p30. თუ რომელიმე ზოლი აკლია
       (ხელით შევსებული YAML, ან ღრუბლიდან მოსული ნაკლული დოკუმენტი),
       ფასი წინა ზოლზე ბრუნდება. აქამდე c.p30-ის უქონლობა NaN-ს იძლეოდა
       და ეს NaN ჯავშანშივე იწერებოდა. */
    var b1 = Number(c.p1) || 0;
    var b7 = Number(c.p7) || b1;
    var b30 = Number(c.p30) || b7;
    var rate = days >= 30 ? b30 : (days >= 7 ? b7 : b1);
    var rental = Math.round(rate * days), deposit = Number(c.dep) || 0;
    /* სეზონი მხოლოდ იმ ღამეებზე ერიცხება, რომლებიც პიკურ თვეშია —
       ნაწილობრივ გადამკვეთ შუალედს მთლიან ჯავშანზე არ ვამძიმებთ. */
    var sc = seasonCfg(), peak = 0, pct = 0, seasonGel = 0;
    if (sc && rate > 0) {
      peak = peakNights(start, end, sc.months);
      if (peak > 0) { pct = sc.percent; seasonGel = Math.round(rate * peak * pct / 100); }
    }
    rental += seasonGel;
    return { days: days, slug: slug, start: start, end: end, rate: rate, rental: rental, deposit: deposit, due: rental + deposit, peakNights: peak, seasonPercent: pct, seasonGel: seasonGel };
  }

  function sendToCloud(root, q) {
    var fd = new FormData(root);
    /* მანქანის გარეშე გახსნილი დიალოგიც იწერება — მოდელს გამქირავებელი
       ირჩევს პროგრამაში. დაკარგული მოთხოვნა უარესია, ვიდრე არასრული. */
    var slug = String(fd.get('car_slug') || '') || 'any';
    return window.FH.firebase().then(function (fb) {
      var M = fb.M, db = fb.db, auth = fb.auth;
      var signed = auth.currentUser
        ? Promise.resolve(auth.currentUser)
        : M.auth.signInAnonymously(auth).then(function (c) { return c.user; });
      return signed.then(function (user) {
        var doc = {
          uid: user.uid,
          carSlug: slug,
          carName: String(fd.get('requested_car') || ''),
          start: String(fd.get('start') || ''),
          end: String(fd.get('end') || ''),
          days: q ? q.days : 1,
          drivers: 1,
          dailyRateGel: q ? q.rate : 0,
          rentalGel: q ? q.rental : 0,
          depositGel: q ? q.deposit : 0,
          paymentDueGel: q ? q.due : 0,
          currency: 'GEL',
          status: 'pending',
          paymentStatus: 'required',
          created: M.db.serverTimestamp(),
          name: String(fd.get('name') || '').slice(0, 120),
          phone: String(fd.get('phone') || '').slice(0, 32),
          email: String(fd.get('email') || '').slice(0, 160),
          pickup: String(fd.get('pickup') || '').slice(0, 160),
          dropoff: String(fd.get('return_location') || fd.get('dropoff') || '').slice(0, 160),
          withDriver: fd.get('with_driver') ? true : false,
          notes: String(fd.get('notes') || '').slice(0, 2000),
          lang: root.dataset.lang || 'en',
          source: 'site',
          pageUrl: location.href.slice(0, 400)
        };
        return M.db.addDoc(M.db.collection(db, 'bookings'), doc);
      });
    });
  }

  /* ── ცოცხალი ფასები და კალენდარი ─────────────────────────────────────
     გამქირავებლის პროგრამა Firestore-ში აქვეყნებს fleet/{slug}-ს (ფასები) და
     availability/{slug}-ს (თავისუფალი ერთეულები დღეების მიხედვით). ორივე
     საჯაროდ იკითხება, ამიტომ არც SDK სჭირდება და არც შესვლა — ერთი fetch.

     ნდობის ფანჯარა 48 საათია: ტელეფონი შეიძლება უსიგნალოდ იყოს დღეები, და
     კვირისწინანდელი კალენდარი, რომელიც თავისუფალ მანქანას მალავს, უარესია,
     ვიდრე არავითარი. ძველი მონაცემი უბრალოდ უგულებელყოფილია და გვერდი ისე
     იქცევა, როგორც აქამდე — ჩაშენებული ფასებით, გაფრთხილების გარეშე. */
  var LIVE = {}, LIVE_RES = {}, TRUST_MS = 48 * 3600 * 1000;
  function fsValue(v){
    if (!v || typeof v !== 'object') return v;
    if ('integerValue' in v) return Number(v.integerValue);
    if ('doubleValue' in v) return Number(v.doubleValue);
    if ('stringValue' in v) return v.stringValue;
    if ('timestampValue' in v) return v.timestampValue;
    if ('booleanValue' in v) return v.booleanValue;
    if ('arrayValue' in v) return ((v.arrayValue||{}).values || []).map(fsValue);
    return null;
  }
  function fsDoc(json){
    if (!json || !json.fields) return null;
    var out = {};
    Object.keys(json.fields).forEach(function(k){ out[k] = fsValue(json.fields[k]); });
    return out;
  }
  function freshDoc(doc){
    if (!doc || !doc.updatedAt) return false;
    var t = Date.parse(doc.updatedAt);
    return isFinite(t) && (Date.now() - t) < TRUST_MS;
  }
  function fetchLive(slug){
    if (!slug) return Promise.resolve(null);
    if (LIVE[slug]) return LIVE[slug];
    var pid = (window.FH_CFG || {}).projectId;
    if (!pid || typeof fetch !== 'function') return Promise.resolve(null);
    var base = 'https://firestore.googleapis.com/v1/projects/' + pid +
      '/databases/(default)/documents/';
    function grab(col){
      return fetch(base + col + '/' + encodeURIComponent(slug))
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(fsDoc)
        .catch(function(){ return null; });
    }
    LIVE[slug] = Promise.all([grab('fleet'), grab('availability')]).then(function(a){
      var d = { fleet: a[0], avail: a[1] };
      LIVE_RES[slug] = d;
      /* ცოცხალი ფასი ჩაშენებულს ფარავს — quoteFor ავტომატურად აიღებს. */
      if (freshDoc(d.fleet)) {
        var cfg = window.FH_CFG = window.FH_CFG || {};
        cfg.cars = cfg.cars || {};
        var prev = cfg.cars[slug] || {};
        /* ჯაჭვი გამოთვლილ მნიშვნელობებზე გადის და არა ნედლ დოკუმენტზე:
           p30-ის გარეშე მოსული დოკუმენტი 30+ დღეს 0 ₾-ად აფასებდა და იმ
           ნულს ჯავშანშიც წერდა. ნულოვანი p1 საერთოდ არ გადაფარავს
           ჩაშენებულს — ცუდი დოკუმენტი ფასს ვერ შლის. */
        var p1 = Number(d.fleet.p1) || Number(prev.p1) || 0;
        var p7 = Number(d.fleet.p7) || p1;
        var p30 = Number(d.fleet.p30) || p7;
        if (p1 > 0) {
          cfg.cars[slug] = {
            p1: p1, p7: p7, p30: p30,
            dep: Number(d.fleet.dep) || Number(prev.dep) || 0
          };
        }
      }
      document.dispatchEvent(new CustomEvent('fh:live-availability', { detail: { slug: slug } }));
      return d;
    });
    return LIVE[slug];
  }
  /* true = მოთხოვნილ შუალედში არის ღამე, რომელზეც არც ერთი ერთეული არ არის
     თავისუფალი. მხოლოდ ახალ (48სთ) მონაცემზე — ძველი პასუხს არ იძლევა. */
  function busyFor(slug, start, end){
    var d = LIVE_RES[slug];
    if (!d || !freshDoc(d.avail)) return false;
    var a = d.avail;
    if (!Array.isArray(a.free)) return false;
    var from = Date.parse(String(a.from) + 'T12:00:00');
    var s = Date.parse(start + 'T12:00:00'), e = Date.parse(end + 'T12:00:00');
    if (!isFinite(from) || !isFinite(s) || !isFinite(e)) return false;
    for (var t = s; t < e; t += 86400000) {
      var i = Math.round((t - from) / 86400000);
      if (i >= 0 && i < a.free.length && Number(a.free[i]) <= 0) return true;
    }
    return false;
  }

  function validDate(v){return /^\d{4}-\d{2}-\d{2}$/.test(v||'');}
  function sourceDates(){
    var from=document.querySelector('#datefrom'),to=document.querySelector('#dateto'),day=document.querySelector('#expday');
    var saved={};try{saved=JSON.parse(localStorage.getItem('fh-rental-dates')||'{}');}catch(e){}
    var s=(from&&from.value)||(day&&day.value)||saved.start||'', e=(to&&to.value)||saved.end||'';
    var q=new URLSearchParams(location.search);s=q.get('start')||q.get('from')||s;e=q.get('end')||q.get('to')||e;
    if(validDate(s)&&!validDate(e)){var d=new Date(s+'T12:00:00');d.setDate(d.getDate()+1);e=d.toISOString().slice(0,10);}
    return {start:validDate(s)?s:'',end:validDate(e)?e:''};
  }
  function rememberDates(){var d=sourceDates();if(d.start||d.end)try{localStorage.setItem('fh-rental-dates',JSON.stringify(d));}catch(e){}}
  function bootDialog(){
    var dialog=document.querySelector('[data-booking-dialog]');if(!dialog)return;
    var form=dialog.querySelector('[data-inquiry]'),choice=dialog.querySelector('[data-booking-choice]'),last=null;
    function close(){dialog.hidden=true;document.body.classList.remove('booking-open');if(last)last.focus();}
    function open(trigger){last=trigger;var dates=sourceDates(),s=form.querySelector('[name="start"]'),e=form.querySelector('[name="end"]');
      if(dates.start)s.value=dates.start;if(dates.end)e.value=dates.end;e.min=s.value||e.min;
      var car=trigger.dataset.carName||'',slug=trigger.dataset.car||'';form.querySelector('[name="requested_car"]').value=car;form.querySelector('[name="context"]').value=slug||form.querySelector('[name="context"]').value;
      var slugField=form.querySelector('[name="car_slug"]');if(slugField)slugField.value=slug;
      document.dispatchEvent(new CustomEvent('fh:booking-car',{detail:{slug:slug,name:car}}));
      choice.hidden=!car;choice.querySelector('strong').textContent=car;dialog.hidden=false;document.body.classList.add('booking-open');setTimeout(function(){s.focus();},30);
    }
    document.addEventListener('click',function(ev){var trigger=ev.target.closest('[data-booking-open]');if(trigger){ev.preventDefault();open(trigger);return;}if(ev.target===dialog||ev.target.closest('[data-booking-close]'))close();});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!dialog.hidden)close();});
    ['datefrom','dateto','expday'].forEach(function(id){var el=document.getElementById(id);if(el)el.addEventListener('change',rememberDates);});
  }
  function bootInquiry(){document.querySelectorAll('[data-inquiry]').forEach(initInquiry);bootDialog();}
  /* GitHub Pages-ზე ფორმის POST-ს მიმღები არ აქვს — Netlify Forms-ს AJAX-ით
     ვაწვდით ძველი Netlify მისამართიდან, რომ ლიდები ისევ შეგროვდეს. */
  var NETLIFY_ORIGIN='https://subtle-naiad-c2db5d.netlify.app';
  /* ლიდის ასლი Netlify Forms-ში. Firestore-ის ჩაწერის შემდეგაც იგზავნება —
     ორივე ერთდროულად რომ არ ჩავარდეს. */
  function postForm(f){
    var origin=(location.hostname.indexOf('netlify.app')>=0)?location.origin:NETLIFY_ORIGIN;
    return fetch(origin+'/',{method:'POST',mode:'no-cors',
      headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:new URLSearchParams(new FormData(f)).toString()});
  }
  function ajaxifyForms(){
    /* ძველი Netlify-მისამართი მკვდარია (404, ფორმები არ აქვს) და no-cors
       პასუხით ამის გაგება შეუძლებელი იყო — ფორმა „გაგზავნილია"-ს წერდა და
       წერილი არსად მიდიოდა. საკონტაქტო ფორმა ახლა WhatsApp-ზე გადის:
       ერთადერთი არხი ამ სტატიკურ ჰოსტინგზე, რომლის მიწოდებაც მართლა ჩანს. */
    document.querySelectorAll('form[data-netlify]').forEach(function(f){
      if(f.dataset.fhCloud==='1')return; /* ღრუბლის გზა თავად აგზავნის */
      f.addEventListener('submit',function(e){
        e.preventDefault();
        if(!f.reportValidity())return;
        var st=f.querySelector('.inquiry-status')||f.querySelector('[role="status"]');
        if(!st){st=document.createElement('p');st.className='inquiry-status';st.setAttribute('role','status');f.appendChild(st);}
        var num=String((window.FH_CFG||{}).whatsapp||'').replace(/\D/g,'');
        if(!num){st.textContent='✗';return;}
        var fd=new FormData(f),parts=[];
        fd.forEach(function(v,k){
          if(k==='company'||k==='form-name'||k==='page_url'||!String(v).trim())return;
          parts.push(k+': '+String(v).trim());
        });
        var msg='Message from '+location.href+'\n'+parts.join('\n');
        window.open('https://wa.me/'+num+'?text='+encodeURIComponent(msg),'_blank','noopener');
        var l=f.dataset.lang||document.documentElement.lang||'en';
        st.textContent=(l==='ka')?'გაგრძელება WhatsApp-შია — გაგზავნე იქ გახსნილი წერილი':'Continue in WhatsApp — send the message that just opened';
      });
    });
  }
  function bootAll(){boot();bootInquiry();ajaxifyForms();}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bootAll); else bootAll();
}());
