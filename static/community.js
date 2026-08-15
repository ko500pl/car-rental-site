(function () {
  var root = document.getElementById("community-app");
  if (!root) return;
  var active = "trips";
  var I18N = { ka: {
    newGroup:"ჯგუფის შექმნა", name:"სახელი", purpose:"მიზნობრიობა", create:"შექმნა",
    review:"შთაბეჭდილების გაზიარება", subject:"ადგილი ან ტური", rating:"შეფასება", text:"თქვენი გამოცდილება",
    photo:"ფოტო", publish:"გამოქვეყნება", publicTrips:"საჯარო პერიოდული ტურები", join:"მიწერა",
    empty:"ჯერ ჩანაწერი არ არის.", login:"გასაგრძელებლად გაიარეთ ავტორიზაცია."
  }, en: {newGroup:"Create group",name:"Name",purpose:"Purpose",create:"Create",review:"Share an experience",
    subject:"Place or trip",rating:"Rating",text:"Your experience",photo:"Photo",publish:"Publish",
    publicTrips:"Public trips",join:"Message",empty:"Nothing here yet.",login:"Sign in to participate."},
  ru:{newGroup:"Создать группу",name:"Название",purpose:"Цель",create:"Создать",review:"Поделиться впечатлением",subject:"Место или тур",rating:"Оценка",text:"Ваш опыт",photo:"Фото",publish:"Опубликовать",publicTrips:"Публичные туры",join:"Написать",empty:"Записей пока нет.",login:"Войдите, чтобы участвовать."},
  fa:{newGroup:"ایجاد گروه",name:"نام",purpose:"هدف",create:"ایجاد",review:"اشتراک تجربه",subject:"مکان یا تور",rating:"امتیاز",text:"تجربه شما",photo:"عکس",publish:"انتشار",publicTrips:"تورهای عمومی",join:"پیام",empty:"هنوز موردی نیست.",login:"برای مشارکت وارد شوید."},
  he:{newGroup:"יצירת קבוצה",name:"שם",purpose:"מטרה",create:"יצירה",review:"שיתוף חוויה",subject:"מקום או טיול",rating:"דירוג",text:"החוויה שלך",photo:"תמונה",publish:"פרסום",publicTrips:"טיולים ציבוריים",join:"הודעה",empty:"עדיין אין פריטים.",login:"יש להתחבר כדי להשתתף."},
  ar:{newGroup:"إنشاء مجموعة",name:"الاسم",purpose:"الهدف",create:"إنشاء",review:"مشاركة تجربة",subject:"مكان أو جولة",rating:"التقييم",text:"تجربتك",photo:"صورة",publish:"نشر",publicTrips:"الجولات العامة",join:"مراسلة",empty:"لا توجد عناصر بعد.",login:"سجّل الدخول للمشاركة."}};
  var labels = I18N[document.documentElement.lang] || I18N.en;
  function esc(v){return String(v == null ? "" : v).replace(/[&<>\"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function api(){ return window.FH.firebase(); }
  function requireUser(){ var u=window.FH.user(); if(!u){window.FH.openDialog(); throw new Error("no-user");} return u; }
  function stamp(x){ return x && x.toDate ? x.toDate().toLocaleDateString() : ""; }
  function draw(){
    if(!window.FH || !window.FH.firebase){ root.innerHTML='<p class="note">'+esc(labels.login)+'</p>'; return; }
    if(active === "trips") return trips();
    if(active === "groups") return groups();
    reviews();
  }
  function trips(){
    root.innerHTML='<div class="community-head"><h3>'+esc(labels.publicTrips)+'</h3></div><div id="community-list"><p class="muted">…</p></div>';
    api().then(function(a){var q=a.M.db.query(a.M.db.collection(a.db,"trips"),a.M.db.where("visibility","==","public"));return a.M.db.getDocs(q);})
      .then(function(s){var h=[];s.forEach(function(d){var x=d.data();h.push('<article class="social-card"><b>'+esc(x.title)+'</b><p>'+esc(x.date||"")+' · '+esc(x.purpose||"general")+' · '+((x.stops||[]).length)+' stops</p><small>'+esc(x.ownerName||"Traveller")+'</small><button class="btn sm ghost" data-message="'+esc(x.uid)+'">'+esc(labels.join)+'</button></article>');});
        document.getElementById("community-list").innerHTML=h.join("")||'<p class="note">'+esc(labels.empty)+'</p>'; bindMessages();});
  }
  function groups(){
    root.innerHTML='<form id="group-form" class="social-form"><h3>'+esc(labels.newGroup)+'</h3><input name="name" maxlength="80" required placeholder="'+esc(labels.name)+'"><select name="purpose"><option value="culinary">Culinary</option><option value="cycling">Cycling</option><option value="culture">Culture</option><option value="nature">Nature</option><option value="family">Family</option></select><button class="btn sm">'+esc(labels.create)+'</button></form><div id="community-list"><p class="muted">…</p></div>';
    root.querySelector("form").onsubmit=function(e){e.preventDefault();var f=e.currentTarget,u;try{u=requireUser();}catch(x){return;}api().then(function(a){return a.M.db.addDoc(a.M.db.collection(a.db,"groups"),{uid:u.uid,ownerName:u.displayName||u.email,name:f.name.value,purpose:f.purpose.value,memberIds:[u.uid],created:a.M.db.serverTimestamp()});}).then(groups);};
    api().then(function(a){return a.M.db.getDocs(a.M.db.collection(a.db,"groups")).then(function(s){return [a,s];});}).then(function(v){var a=v[0],s=v[1],u=window.FH.user(),rows=[];s.forEach(function(d){rows.push(Object.assign({id:d.id},d.data()));});document.getElementById("community-list").innerHTML=rows.map(function(x){var joined=u&&(x.memberIds||[]).indexOf(u.uid)>=0;return '<article class="social-card"><b>'+esc(x.name)+'</b><p>'+esc(x.purpose)+' · '+(x.memberIds||[]).length+' members</p><small>'+esc(x.ownerName||"")+'</small>'+(!joined?'<button class="btn sm ghost" data-join="'+esc(x.id)+'">'+esc(labels.join)+'</button>':'<span class="joined">✓</span>')+'</article>';}).join("")||'<p class="note">'+esc(labels.empty)+'</p>';document.querySelectorAll('[data-join]').forEach(function(b){b.onclick=function(){var u;try{u=requireUser();}catch(e){return;}var row=rows.find(function(x){return x.id===b.dataset.join;});if(!row)return;b.disabled=true;a.M.db.updateDoc(a.M.db.doc(a.db,'groups',row.id),{memberIds:(row.memberIds||[]).concat([u.uid])}).then(groups).catch(function(){b.disabled=false;});};});});
  }
  function reviews(){
    root.innerHTML='<form id="review-form" class="social-form"><h3>'+esc(labels.review)+'</h3><input name="subject" maxlength="120" required placeholder="'+esc(labels.subject)+'"><select name="rating"><option value="5">★★★★★</option><option value="4">★★★★</option><option value="3">★★★</option><option value="2">★★</option><option value="1">★</option></select><textarea name="text" maxlength="3000" required placeholder="'+esc(labels.text)+'"></textarea><label>'+esc(labels.photo)+'<input name="photo" type="file" accept="image/*"></label><button class="btn sm">'+esc(labels.publish)+'</button></form><div id="community-list"><p class="muted">…</p></div>';
    root.querySelector("form").onsubmit=function(e){e.preventDefault();var f=e.currentTarget,u;try{u=requireUser();}catch(x){return;}var file=f.photo.files[0];api().then(function(a){if(!file)return [a,""];var storage=a.M.storage.getStorage(a.app),ref=a.M.storage.ref(storage,"community/"+u.uid+"/"+Date.now()+"-"+file.name.replace(/[^a-zA-Z0-9._-]/g,"_"));return a.M.storage.uploadBytes(ref,file).then(function(){return a.M.storage.getDownloadURL(ref);}).then(function(url){return [a,url];});}).then(function(v){var a=v[0];return a.M.db.addDoc(a.M.db.collection(a.db,"reviews"),{uid:u.uid,authorName:u.displayName||u.email,subject:f.subject.value,rating:parseInt(f.rating.value,10),text:f.text.value,photoUrl:v[1],created:a.M.db.serverTimestamp()});}).then(reviews);};
    api().then(function(a){return a.M.db.getDocs(a.M.db.collection(a.db,"reviews"));}).then(function(s){var rows=[];s.forEach(function(d){rows.push(d.data());});rows.sort(function(a,b){return (b.created&&b.created.seconds||0)-(a.created&&a.created.seconds||0);});document.getElementById("community-list").innerHTML=rows.map(function(x){return '<article class="social-card review-card">'+(x.photoUrl?'<img src="'+esc(x.photoUrl)+'" alt="'+esc(x.subject)+'">':'')+'<div><b>'+esc(x.subject)+'</b><p class="stars">'+"★".repeat(x.rating||0)+'</p><p>'+esc(x.text)+'</p><small>'+esc(x.authorName||"")+' · '+esc(stamp(x.created))+'</small></div></article>';}).join("")||'<p class="note">'+esc(labels.empty)+'</p>';});
  }
  function bindMessages(){root.querySelectorAll("[data-message]").forEach(function(b){b.onclick=function(){var u;try{u=requireUser();}catch(x){return;}var other=b.dataset.message;if(other===u.uid)return;var card=b.closest(".social-card"),old=card.querySelector(".message-form");if(old){old.remove();return;}var form=document.createElement("form");form.className="message-form";form.innerHTML='<label>'+esc(labels.text)+'<textarea required maxlength="2000"></textarea></label><button class="btn sm" type="submit">'+esc(labels.join)+'</button><span role="status"></span>';card.appendChild(form);form.querySelector("textarea").focus();form.onsubmit=function(e){e.preventDefault();var text=form.querySelector("textarea").value.trim(),status=form.querySelector("span");if(!text)return;status.textContent="…";api().then(function(a){var ids=[u.uid,other].sort(),id=ids.join("_");var ref=a.M.db.doc(a.db,"conversations",id);return a.M.db.setDoc(ref,{uid:u.uid,memberIds:ids,kind:"private",lastMessage:text,updatedAt:a.M.db.serverTimestamp()},{merge:true}).then(function(){return a.M.db.addDoc(a.M.db.collection(a.db,"conversations",id,"messages"),{uid:u.uid,text:text,created:a.M.db.serverTimestamp()});});}).then(function(){status.textContent="✓";form.querySelector("textarea").value="";}).catch(function(){status.textContent="!";});};};});}
  document.querySelectorAll("[data-community-tab]").forEach(function(b){b.onclick=function(){document.querySelectorAll("[data-community-tab]").forEach(function(x){x.classList.remove("on");});b.classList.add("on");active=b.dataset.communityTab;draw();};});
  setTimeout(draw,0);
})();
