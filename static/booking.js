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
    var start=root.querySelector('[name="start"]'),end=root.querySelector('[name="end"]');
    start.min=today;end.min=today;start.addEventListener('input',function(){end.min=start.value||today;});
    function message(){var fd=new FormData(root),lang=root.dataset.lang||'en';return (lang==='ka'?'გამარჯობა, მსურს ავტომობილის დაჯავშნა. ':'Hello, I would like to book a car. ')+
      (fd.get('requested_car')?'Car: '+fd.get('requested_car')+'. ':'')+(fd.get('start')||'-')+' — '+(fd.get('end')||'-')+'. '+
      'Name: '+(fd.get('name')||'-')+'. Phone: '+(fd.get('phone')||'-')+'. Page: '+location.href+(fd.get('notes')?'. Notes: '+fd.get('notes'):'');}
    root.querySelector('[data-inquiry-wa]').addEventListener('click',function(){if(!root.reportValidity())return;var num=String((window.FH_CFG||{}).whatsapp||'').replace(/\D/g,'');if(!num){status.textContent='WhatsApp is not configured.';return;}window.open('https://wa.me/'+num+'?text='+encodeURIComponent(message()),'_blank','noopener');});
    root.addEventListener('submit',function(){root.querySelector('[name="page_url"]').value=location.href;});
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
      choice.hidden=!car;choice.querySelector('strong').textContent=car;dialog.hidden=false;document.body.classList.add('booking-open');setTimeout(function(){s.focus();},30);
    }
    document.addEventListener('click',function(ev){var trigger=ev.target.closest('[data-booking-open]');if(trigger){ev.preventDefault();open(trigger);return;}if(ev.target===dialog||ev.target.closest('[data-booking-close]'))close();});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!dialog.hidden)close();});
    ['datefrom','dateto','expday'].forEach(function(id){var el=document.getElementById(id);if(el)el.addEventListener('change',rememberDates);});
  }
  function bootInquiry(){document.querySelectorAll('[data-inquiry]').forEach(initInquiry);bootDialog();}
  function bootAll(){boot();bootInquiry();}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bootAll); else bootAll();
}());
