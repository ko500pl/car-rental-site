/* Static-first rental inquiry: contextual WhatsApp plus Netlify Forms fallback. */
(function () {
  var TEXT = {
    ka: { choose: "მიუთითეთ დაწყებისა და დასრულების თარიღები.", invalid: "დასრულება დაწყების შემდეგ უნდა იყოს.", days: "დღე", rate: "დღიური ფასი", total: "ქირა", deposit: "დეპოზიტი", due: "გადასახდელი", login: "მოთხოვნის გასაგზავნად შედით ანგარიშში.", sending: "იგზავნება…", success: "მოთხოვნა მიღებულია. ჯავშანი დადასტურებული არ არის, სანამ გადახდა არ შესრულდება.", failed: "მოთხოვნა ვერ გაიგზავნა. სცადეთ ხელახლა." },
    en: { choose: "Choose start and end dates.", invalid: "End must be after start.", days: "days", rate: "Daily rate", total: "Rental", deposit: "Deposit", due: "Payment due", login: "Sign in to send the request.", sending: "Sending…", success: "Request received. The booking is not confirmed until payment is completed.", failed: "The request could not be sent. Please try again." },
    ru: { choose: "Укажите даты начала и окончания.", invalid: "Дата окончания должна быть позже начала.", days: "дн.", rate: "Цена в день", total: "Аренда", deposit: "Депозит", due: "К оплате", login: "Войдите, чтобы отправить запрос.", sending: "Отправка…", success: "Запрос получен. Бронирование не подтверждено до оплаты.", failed: "Не удалось отправить запрос." },
    fa: { choose: "تاریخ شروع و پایان را انتخاب کنید.", invalid: "پایان باید بعد از شروع باشد.", days: "روز", rate: "نرخ روزانه", total: "اجاره", deposit: "ودیعه", due: "مبلغ پرداخت", login: "برای ارسال درخواست وارد شوید.", sending: "در حال ارسال…", success: "درخواست دریافت شد. رزرو تا زمان پرداخت تأیید نمی‌شود.", failed: "ارسال درخواست ناموفق بود." },
    he: { choose: "בחרו תאריכי התחלה וסיום.", invalid: "הסיום חייב להיות אחרי ההתחלה.", days: "ימים", rate: "מחיר יומי", total: "השכרה", deposit: "פיקדון", due: "לתשלום", login: "יש להתחבר כדי לשלוח בקשה.", sending: "שולח…", success: "הבקשה התקבלה. ההזמנה אינה מאושרת עד להשלמת התשלום.", failed: "לא ניתן לשלוח את הבקשה." },
    ar: { choose: "اختر تاريخي البداية والنهاية.", invalid: "يجب أن تكون النهاية بعد البداية.", days: "أيام", rate: "السعر اليومي", total: "الإيجار", deposit: "التأمين", due: "المبلغ المستحق", login: "سجّل الدخول لإرسال الطلب.", sending: "جارٍ الإرسال…", success: "تم استلام الطلب. لا يتأكد الحجز حتى يكتمل الدفع.", failed: "تعذر إرسال الطلب." }
  };
  function n(v) { v = Number(v); return Number.isFinite(v) ? v : 0; }
  function calc(root) {
    var start = root.querySelector('[name="start"]').value;
    var end = root.querySelector('[name="end"]').value;
    if (!start || !end) return null;
    var days = Math.ceil((new Date(end + "T12:00:00") - new Date(start + "T12:00:00")) / 86400000);
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
    var today = new Date().toISOString().slice(0, 10);
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
    var status=root.querySelector('.inquiry-status'), today=new Date().toISOString().slice(0,10);
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
      quoteBox.textContent = q.days + ' ' + t.days +
        (q.rate ? ' · ' + t.rate + ': ' + money(q.rate) + ' · ' + t.total + ': ' + money(q.rental) +
          (q.deposit ? ' · ' + t.deposit + ': ' + money(q.deposit) : '') : '');
      return q;
    }
    ['start', 'end'].forEach(function (n) {
      var el = root.querySelector('[name="' + n + '"]');
      if (el) el.addEventListener('input', drawQuote);
    });
    document.addEventListener('fh:booking-car', drawQuote);
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
          .then(function () { return postForm(root).catch(function () { return null; }); })
          .then(function () {
            status.textContent = t.success;
            root.reset();
            if (quoteBox) quoteBox.textContent = '';
          })
          .catch(function () { status.textContent = cloud ? t.success : t.failed; })
          .then(function () { if (button) button.disabled = false; });
      });
    } else {
      root.addEventListener('submit', function () { root.querySelector('[name="page_url"]').value = location.href; });
    }
  }

  /* დღეების დათვლა და ტარიფის ბენდი — იგივე წესი, რაც პროგრამაშია. */
  function quoteFor(root) {
    var fd = new FormData(root);
    var start = String(fd.get('start') || ''), end = String(fd.get('end') || '');
    if (!validDate(start) || !validDate(end)) return null;
    var days = Math.ceil((new Date(end + 'T12:00:00') - new Date(start + 'T12:00:00')) / 86400000);
    if (!(days >= 1)) return null;
    var slug = String(fd.get('car_slug') || '');
    var c = ((window.FH_CFG || {}).cars || {})[slug];
    if (!c) return { days: days, slug: slug, rate: 0, rental: 0, deposit: 0, due: 0 };
    var rate = days >= 30 ? c.p30 : (days >= 7 ? c.p7 : c.p1);
    var rental = Math.round(rate * days), deposit = c.dep || 0;
    return { days: days, slug: slug, rate: rate, rental: rental, deposit: deposit, due: rental + deposit };
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
          notes: String(fd.get('notes') || '').slice(0, 2000),
          lang: root.dataset.lang || 'en',
          source: 'site',
          pageUrl: location.href.slice(0, 400)
        };
        return M.db.addDoc(M.db.collection(db, 'bookings'), doc);
      });
    });
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
    if(location.hostname.indexOf('netlify.app')>=0)return; /* Netlify-ზე ჩვეულებრივ მუშაობს */
    document.querySelectorAll('form[data-netlify]').forEach(function(f){
      if(f.dataset.fhCloud==='1')return; /* ღრუბლის გზა თავად აგზავნის — დუბლიკატი არ გვინდა */
      f.addEventListener('submit',function(e){
        e.preventDefault();
        if(!f.reportValidity())return;
        var pu=f.querySelector('[name="page_url"]');if(pu)pu.value=location.href;
        var body=new URLSearchParams(new FormData(f)).toString();
        var st=f.querySelector('.inquiry-status')||f.querySelector('[role="status"]');
        if(!st){st=document.createElement('p');st.className='inquiry-status';st.setAttribute('role','status');f.appendChild(st);}
        st.textContent='…';
        fetch(NETLIFY_ORIGIN+'/',{method:'POST',mode:'no-cors',
          headers:{'Content-Type':'application/x-www-form-urlencoded'},body:body})
          .then(function(){var l=f.dataset.lang||document.documentElement.lang||'en';
            st.textContent=(l==='ka')?'✓ მოთხოვნა გაგზავნილია — მალე დაგიკავშირდებით':'✓ Sent — we will contact you shortly';f.reset();})
          .catch(function(){st.textContent='✗';});
      });
    });
  }
  function bootAll(){boot();bootInquiry();ajaxifyForms();}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bootAll); else bootAll();
}());
