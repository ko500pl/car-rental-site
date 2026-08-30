# Page alignment to the owner's decisions — 2026-08-30

Aligns `content/pages/terms.yml`, `faq.yml`, `pricing.yml`, `index.yml`, `about.yml` and
`contact.yml` with the seven answers the owner gave to the open questions in
`docs/seo/FACT_RECONCILIATION.md` / `docs/seo/OWNER_DECISIONS_KA.md`.

The owner's answers, as applied here:

1. **No prepayment.** No online payment system exists. A customer sends a request or calls,
   RentUp confirms availability, payment happens at pickup. `contact.yml` was already right;
   `terms.yml`, `faq.yml`, `pricing.yml` and `index.yml` said the opposite and were corrected.
2. **No WiFi router extra.** Not offered.
3. **No maximum rental length.**
4. **Roadside assistance is 24/7.**
5. **Every car is fully insured — CDW + TPL included in the rate on every rental** — but an
   excess still applies per category, so the two are always stated together. "Zero excess" /
   "no deductible" is never written as a general claim.
6. **The USD rate comes from the National Bank of Georgia**, not a hard-coded number.
7. **The young-driver surcharge is real** (15–25 GEL/day by category and age band) and stays.

YAML structure, key names and block order are unchanged throughout — only wording and numbers
were touched. `python3 build.py --validate-only` passes; `build.py` + `scripts/seo_audit.py`
report **0 ERROR** (2 pre-existing WARNs on `/ka/trip-planner/` and `/ru/trip-planner/` title
length, in files not touched by this pass).

---

## Every change

### Answer 1 — prepayment is not required

| File | Lang | Key path | Old → New |
|---|---|---|---|
| `terms.yml` | en | `en.blocks[16].items[0]` | "Booking requests are confirmed after availability is checked and the required payment is completed." → "Booking requests are confirmed by phone or email; no prepayment is required." |
| `terms.yml` | ka, ru, fa, he, ar | `blocks[16].items[0]` | **No change — already correct.** Only the English section still carried the prepayment claim; the other five already said "confirmed by phone or email; no prepayment required". |
| `faq.yml` | ka | `ka.blocks[1].items[2].a` | "ჯავშნის მოთხოვნა საიტიდან იგზავნება… ჯავშანი სავალდებულო გადახდის შემდეგ დასტურდება." → "არა — საიტს ონლაინ გადახდის სისტემა არ აქვს. გამოგვიგზავნეთ ჯავშნის მოთხოვნა ან დაგვირეკეთ; ხელმისაწვდომობის დადასტურების შემდეგ ანგარიშსწორება ავტომობილის მიღებისას ხდება." |
| `faq.yml` | en | `en.blocks[1].items[2].a` | "Submit the booking request on the website… the booking is confirmed after the required payment." → "No — the site has no online payment system. Send us a booking request or call; once we have confirmed availability, payment is made at pickup." |
| `faq.yml` | ru | `ru.blocks[1].items[2].a` | "Отправьте заявку на сайте… бронь подтверждается после обязательной оплаты." → "Нет — системы онлайн-оплаты на сайте нет. Отправьте заявку или позвоните; после подтверждения доступности расчёт производится при получении автомобиля." |
| `faq.yml` | fa | `fa.blocks[1].items[2].a` | "درخواست رزرو را در سایت ارسال کنید… رزرو پس از پرداخت الزامی تأیید می‌شود." → "خیر — این سایت سامانهٔ پرداخت آنلاین ندارد. درخواست رزرو بفرستید یا تماس بگیرید؛ پس از تأیید موجود بودن خودرو، پرداخت هنگام تحویل گرفتن خودرو انجام می‌شود." |
| `faq.yml` | he | `he.blocks[1].items[2].a` | "שלחו בקשת הזמנה באתר… ההזמנה מאושרת לאחר התשלום הנדרש." → "לא — באתר אין מערכת תשלום מקוונת. שלחו בקשת הזמנה או התקשרו; לאחר אישור הזמינות התשלום מתבצע בעת קבלת הרכב." |
| `faq.yml` | ar | `ar.blocks[1].items[2].a` | "أرسل طلب الحجز عبر الموقع… ويُؤكد الحجز بعد إتمام الدفع المطلوب." → "لا — فالموقع لا يتضمّن نظام دفع إلكتروني. أرسل طلب حجز أو اتصل بنا؛ وبعد تأكيد التوفر يتم الدفع عند استلام السيارة." |
| `pricing.yml` | ka | `ka.blocks[17].items[3]` | "ჯავშნის მოთხოვნა იგზავნება საიტიდან; დადასტურება ხდება სავალდებულო გადახდის შემდეგ" → "ჯავშანი დასტურდება ტელეფონით ან ელფოსტით; ანგარიშსწორება ავტომობილის მიღებისას" |
| `pricing.yml` | en | `en.blocks[17].items[3]` | "Submit the booking request online; confirmation follows the required payment" → "Booking is confirmed by phone or email; payment is made at pickup" |
| `pricing.yml` | ru | `ru.blocks[17].items[3]` | "Заявка подаётся на сайте; подтверждение следует после обязательной оплаты" → "Бронь подтверждается по телефону или электронной почте; оплата при получении автомобиля" |
| `pricing.yml` | fa | `fa.blocks[17].items[3]` | "درخواست رزرو در سایت ارسال می‌شود؛ تأیید پس از پرداخت الزامی انجام می‌شود" → "رزرو تلفنی یا از راه ایمیل تأیید می‌شود؛ پرداخت هنگام تحویل گرفتن خودرو" |
| `pricing.yml` | he | `he.blocks[17].items[3]` | "בקשת ההזמנה נשלחת באתר; האישור מתקבל לאחר התשלום הנדרש" → "ההזמנה מאושרת בטלפון או בדוא\"ל; התשלום מתבצע בעת קבלת הרכב" |
| `pricing.yml` | ar | `ar.blocks[17].items[3]` | "يُرسل طلب الحجز عبر الموقع؛ ويأتي التأكيد بعد الدفع المطلوب" → "يُؤكَّد الحجز عبر الهاتف أو البريد الإلكتروني؛ ويتم الدفع عند استلام السيارة" |
| `index.yml` | ka | `ka.blocks[18].text` (cta) | "ჯავშნის მოთხოვნა პირდაპირ საიტიდან გააგზავნეთ… ჯავშანი სავალდებულო გადახდის შემდეგ დასტურდება." → "ეს საიტი ინფორმაციულია — ონლაინ გადახდის სისტემა არ გვაქვს. ავტომობილის დასაჯავშნად დაგვირეკეთ ან მოგვწერეთ; სამუშაო საათებში პასუხს 15 წუთში მიიღებთ." |
| `index.yml` | en | `en.blocks[18].text` (cta) | "Submit a booking request directly from the website… the booking is confirmed after the required payment." → "This site is informational — we have no online payment system. To book a car, call or email us; during business hours you will hear back within 15 minutes." |
| `index.yml` | ru | `ru.blocks[18].text` (cta) | "Отправьте заявку на бронирование прямо с сайта… бронь подтверждается после обязательной оплаты." → "Сайт носит информационный характер — системы онлайн-оплаты у нас нет. Чтобы забронировать автомобиль, позвоните или напишите нам; в рабочее время ответим в течение 15 минут." |
| `index.yml` | fa | `fa.blocks[18].text` (cta) | "درخواست رزرو را مستقیماً از سایت ارسال کنید… رزرو پس از پرداخت الزامی تأیید می‌شود." → "این سایت جنبهٔ اطلاع‌رسانی دارد — سامانهٔ پرداخت آنلاین نداریم. برای رزرو خودرو با ما تماس بگیرید یا ایمیل بفرستید؛ در ساعات کاری ظرف 15 دقیقه پاسخ می‌گیرید." |
| `index.yml` | he | `he.blocks[18].text` (cta) | "שלחו בקשת הזמנה ישירות מהאתר… ההזמנה מאושרת לאחר התשלום הנדרש." → "האתר הזה מידעי בלבד — אין לנו מערכת תשלום מקוונת. להזמנת רכב התקשרו אלינו או שלחו מייל; בשעות הפעילות תקבלו מענה בתוך 15 דקות." |
| `index.yml` | ar | `ar.blocks[18].text` (cta) | **No change — already correct.** The Arabic CTA already said the site has no online payment system; the other five were brought into line with it. |
| `contact.yml` | all 6 | `lead`, `blocks[2].text` | **No change — already correct** in all six languages ("no online form or payment system", "bookings by phone or email"). |

### Answer 5 — insurance included (CDW + TPL), always paired with the excess

| File | Lang | Key path | Old → New |
|---|---|---|---|
| `index.yml` | ka | `ka.hero.lead` | "ფასი მოიცავს **სრულ სადაზღვევო დაფარვას**," → "ფასი მოიცავს **CDW და TPL დაზღვევას ფრანშიზით**," |
| `index.yml` | en | `en.hero.lead` | "The rate includes **full insurance coverage**," → "The rate includes **CDW and TPL cover with an excess**," |
| `index.yml` | ru | `ru.hero.lead` | "В стоимость входят **полное страховое покрытие**," → "В стоимость входят **страховки CDW и TPL с франшизой**," |
| `index.yml` | fa | `fa.hero.lead` | "نرخ اعلام‌شده شامل **پوشش بیمه کامل**،" → "نرخ اعلام‌شده شامل **بیمهٔ CDW و TPL با فرانشیز**،" |
| `index.yml` | he | `he.hero.lead` | "המחיר כולל **כיסוי ביטוחי מלא**," → "המחיר כולל **ביטוח CDW ו-TPL עם השתתפות עצמית**," |
| `index.yml` | ar | `ar.hero.lead` | "ويشمل السعر **تغطية تأمينية كاملة**" → "ويشمل السعر **تأمين CDW وTPL مع مبلغ تحمّل**" |
| `index.yml` | ka | `ka.blocks[2].items[5].v` | "CDW ფასში შედის" → "CDW + TPL, ფრანშიზით" |
| `index.yml` | en | `en.blocks[2].items[5].v` | "CDW included" → "CDW + TPL, excess applies" |
| `index.yml` | ru | `ru.blocks[2].items[5].v` | "CDW включена в цену" → "CDW + TPL, есть франшиза" |
| `index.yml` | fa | `fa.blocks[2].items[5].v` | "شامل CDW" → "CDW و TPL، با فرانشیز" |
| `index.yml` | he | `he.blocks[2].items[5].v` | "כולל CDW" → "CDW + TPL, עם השתתפות עצמית" |
| `index.yml` | ar | `ar.blocks[2].items[5].v` | "يشمل CDW" → "CDW وTPL، مع مبلغ تحمّل" |
| `index.yml` | ka | `ka.blocks[6].text` (note) | "**ფასში შედის:** CDW სადაზღვევო დაფარვა, …" → "**ფასში შედის:** CDW და TPL დაზღვევა (ფრანშიზა კატეგორიის მიხედვით რჩება), …" |
| `index.yml` | en | `en.blocks[6].text` (note) | "**Included in the price:** CDW insurance coverage, …" → "**Included in the price:** CDW and TPL insurance (an excess still applies by category), …" |
| `index.yml` | ru | `ru.blocks[6].text` (note) | "**В цену входит:** страховое покрытие CDW, …" → "**В цену входит:** страховки CDW и TPL (франшиза по категории сохраняется), …" |
| `index.yml` | fa | `fa.blocks[6].text` (note) | "**شامل قیمت:** پوشش بیمه CDW، …" → "**شامل قیمت:** بیمهٔ CDW و TPL (فرانشیز بسته به کلاس همچنان برقرار است)، …" |
| `index.yml` | he | `he.blocks[6].text` (note) | "**כלול במחיר:** כיסוי ביטוחי CDW, …" → "**כלול במחיר:** ביטוח CDW ו-TPL (השתתפות עצמית לפי קטגוריה עדיין חלה), …" |
| `index.yml` | ar | `ar.blocks[6].text` (note) | "**يشمل السعر:** تغطية تأمين CDW، …" → "**يشمل السعر:** تأمين CDW وTPL (مع بقاء مبلغ تحمّل بحسب الفئة)، …" |
| `faq.yml` | ka | `ka.blocks[1].items[4].a` ("hidden charges") | "…მოიცავს დღგ-ს, CDW დაზღვევას, ტექმომსახურებას და შეუზღუდავ გარბენს." → adds TPL and "ზიანის შემთხვევაში რჩება ფრანშიზა კატეგორიის მიხედვით" |
| `faq.yml` | en | `en.blocks[1].items[4].a` | "…includes VAT, CDW insurance, servicing and unlimited mileage." → adds TPL and "In the event of damage an excess still applies by category" |
| `faq.yml` | ru | `ru.blocks[1].items[4].a` | "…включает НДС, страховку CDW, техобслуживание и неограниченный пробег." → adds TPL and "При повреждении сохраняется франшиза по категории" |
| `faq.yml` | fa | `fa.blocks[1].items[4].a` | "…شامل مالیات…، بیمهٔ CDW، سرویس دوره‌ای و کیلومتر نامحدود است." → adds TPL and "در صورت بروز خسارت، فرانشیز بسته به کلاس همچنان برقرار است" |
| `faq.yml` | he | `he.blocks[1].items[4].a` | "…כולל מע\"מ, ביטוח CDW, טיפולים וקילומטראז' ללא הגבלה." → adds TPL and "במקרה של נזק עדיין חלה השתתפות עצמית לפי קטגוריה" |
| `faq.yml` | ar | `ar.blocks[1].items[4].a` | "…تشمل ضريبة القيمة المضافة وتأمين CDW والصيانة والمسافة غير المحدودة." → adds TPL and "وعند وقوع ضرر يبقى مبلغ التحمّل بحسب الفئة" |

`terms.yml` `blocks[9]` (all six languages) already stated the correct model — "the price includes CDW
and TPL; CDW caps the renter's liability at the excess" — and was left as-is.

### Answer 6 — no hard-coded exchange rate in prose

The USD figures in `pricing.yml`'s dollar table are hand-written cell values, not computed, so the
prose was reworded to (a) mark the dollar column as indicative and (b) point at the National Bank
rate as the number that actually governs settlement. The `build.py` change that pulls the live NBG
rate was **not** touched.

| File | Lang | Key path | Old → New |
|---|---|---|---|
| `pricing.yml` | ka | `ka.lead` | "კურსი გაანგარიშებულია 1 USD = 2.70 ₾." → "დოლარის თანხები საორიენტაციოა — ანგარიშსწორება ლარში, ეროვნული ბანკის მიმდინარე კურსით." |
| `pricing.yml` | en | `en.lead` | "Conversions use a rate of 1 USD = 2.70 ₾." → "Dollar figures are indicative — settlement is in GEL at the National Bank of Georgia rate." |
| `pricing.yml` | ru | `ru.lead` | "Пересчёт сделан по курсу 1 USD = 2.70 ₾." → "Суммы в долларах ориентировочные — расчёт в лари по текущему курсу Национального банка." |
| `pricing.yml` | fa | `fa.lead` | "تبدیل ارز با نرخ 1 دلار = 2.70 ₾ انجام شده است." → "مبالغ دلاری تقریبی است — تسویه به لاری و با نرخ روز بانک ملی گرجستان انجام می‌شود." |
| `pricing.yml` | he | `he.lead` | "ההמרה מחושבת לפי שער של 1 דולר = 2.70 ₾." → "הסכומים בדולר להתרשמות בלבד — התשלום בלארי לפי שער הבנק הלאומי העדכני." |
| `pricing.yml` | ar | `ar.lead` | "ويُحتسب التحويل على أساس 1 دولار = 2.70 ₾." → "والمبالغ بالدولار تقديرية — والتسوية باللاري وفق سعر البنك الوطني الجاري." |
| `pricing.yml` | ka | `ka.blocks[2].caption` | "(საორიენტაციო, კურსი 1 USD = 2.70 ₾)" → "(საორიენტაციო, დაახლოებით 2.7 ₾ დოლარზე)" |
| `pricing.yml` | en | `en.blocks[2].caption` | "(indicative, at 1 USD = 2.70 ₾)" → "(indicative, at roughly 2.7 ₾ to the dollar)" |
| `pricing.yml` | ru | `ru.blocks[2].caption` | "(ориентировочно, курс 1 USD = 2.70 ₾)" → "(ориентировочно, примерно 2,7 ₾ за доллар)" |
| `pricing.yml` | fa | `fa.blocks[2].caption` | "(تقریبی، با نرخ 1 دلار = 2.70 ₾)" → "(تقریبی، حدود 2.7 ₾ برای هر دلار)" |
| `pricing.yml` | he | `he.blocks[2].caption` | "(להתרשמות, לפי 1 דולר = 2.70 ₾)" → "(להתרשמות, לפי כ-2.7 ₾ לדולר)" |
| `pricing.yml` | ar | `ar.blocks[2].caption` | "(تقديرية، على أساس 1 دولار = 2.70 ₾)" → "(تقديرية، بنحو 2.7 ₾ للدولار)" |

`faq.yml` and `index.yml` already hedged their dollar figures ("≈28 USD", "roughly 28 USD",
"დაახლოებით 28 აშშ დოლარი") and were left alone. The lari price is the primary figure in every
case. After the change, the string `2.70 ₾` appears nowhere in the built site.

### Answers 2, 3, 4, 7 — no change required

| Answer | Finding |
|---|---|
| 2 — no WiFi router | Searched all six files in all six languages (`wifi`, `wi-fi`, `роутер`, `روتر`, `ראוטר`, `რაუტერ`, `واي فاي`): **zero occurrences.** The claim only ever lived in `content/settings/rental_policy.yml`, where it was already removed. Nothing to delete. |
| 3 — no maximum rental length | **No cap is stated anywhere** in these six files, in any language. (`terms.yml`'s "მაქსიმალური ასაკი შეზღუდული არ არის" / "there is no maximum age" is about the driver's age, not rental length — correctly left alone.) |
| 4 — roadside assistance 24/7 | Already "24/7" in every occurrence: `faq.yml` (6 langs), `pricing.yml` (6 langs), `index.yml` (6 langs), `contact.yml` hotline label (6 langs). No page tied it to office hours. The `hours_key: office_hours` problem is in `content/settings/rental_policy.yml`, which is outside this pass. |
| 7 — young-driver surcharge stays | Verified intact and unchanged: `terms.yml` age/experience table (15 ₾/day ages 23–25 crossover/SUV/minivan; 25 ₾/day ages 25–27 business/4x4) and `faq.yml` ("15–25 GEL per day" for drivers under 27), all six languages. |

### `about.yml` — unsourced claims flagged, not changed

No statement in `about.yml` contradicts any of the seven answers, in any language, so the file is
**unmodified**. Two numbers were checked against the repo as instructed:

| Claim | Key path | Repo support |
|---|---|---|
| "4 800+" / "4,800+" rentals per year | `<lang>.blocks[1].items[3].v` (all 6 langs) | **None.** The string appears only in `about.yml` itself and in `docs/seo/AI_VISIBILITY.md`, which flags it as unverifiable. No dataset, settings file or `content/` record derives it. |
| "34" employees | `<lang>.blocks[1].items[5].v` (all 6 langs) | **None.** No employee count exists anywhere in `content/settings/*` or elsewhere in the repo. |

Left in place per instructions — these may be facts only the owner knows. `docs/seo/AI_VISIBILITY.md`
(lines 155, 850) independently reached the same conclusion and also flags the neighbouring
utilisation figures (65% target / 85% summer / 45% winter) and the "typical vehicle economics"
table as similarly unsourced. **Owner: please confirm or correct these five numbers** — they are
the figures an AI assistant will quote as fact about RentUp.

---

## Could not reconcile / needs a decision

### 1. `pricing.yml` is authored but not published — the whole file is inert

This is the most consequential finding of this pass, and it changes how `FACT_RECONCILIATION.md`
should be read.

`build.py:4781–4782` writes `/pricing/` (and `/<lang>/pricing/` in all six languages) as a
**noindex meta-refresh redirect to `/fleet/`**, and `pricing` is listed in `NOINDEX_PAGES`
(`build.py:2030`). `build.py:374` maps `target = "fleet" if page == "pricing" else page`. Nothing
else renders `pricing.yml`'s body.

Verified against a full build (`/tmp/pg`): of the entire file — `lead`, `h1` and all 19 blocks in
six languages — exactly **one string is published**: `PAGES["pricing"][lang]["title"]`, used at
`build.py:750` as the `name` of an `OfferCatalog` JSON-LD node on `/fleet/`. The rate tables, the
extras table, the deposit/excess table, the delivery-fee table and the payment-methods list appear
nowhere in the 2,292 built pages. `/pricing/index.html` is a 224-byte redirect stub.

Consequences:

- The `pricing.yml` corrections above are **correct in the source but currently invisible** to
  customers and to AI extractors. They will take effect the moment the page is published again.
- `FACT_RECONCILIATION.md` ranks `pricing.yml` as "pre-existing, already-published business
  content" and used that standing to overrule `rental_policy.yml` on the night surcharge, the
  airport/city delivery fees, the additional-driver fee, GPS and the excess table. Those verdicts
  still look right on the merits (they agree with `faq.yml`), but the stated *reason* does not
  hold: **both files are inert.** The doc's line-number citations to `pricing.yml` describe
  authored, not live, content.
- **Knock-on:** `terms.yml` `blocks[9]` (all six languages) tells the reader to "see the
  [pricing page](/pricing/)" for the excess amount. That link now redirects to `/fleet/`, which
  publishes **no excess and no deposit table** — confirmed by grep against the build. The excess
  figures survive publicly only on `/faq/` and in `index.yml`'s FAQ block. I did not repoint the
  link, because whether `/pricing/` gets republished is a `build.py` decision owned by another
  process. **Decision needed:** republish `/pricing/`, or repoint that link to `/faq/`.

### 2. `index.yml`'s `hero.lead` is dead content — the "full insurance coverage" claim was never live

`build.py:1110–1111` does `h = dict(p["hero"]); h.update(HOME_HERO[lang])`, so
`content/settings/home_hero.yml` overrides `kicker`, `h1` and `lead` for every language.
`index.yml`'s `hero.lead` is discarded before render; only `hero.facts` survives the merge (which
is why the fact-tile change above *does* appear on the page).

So the claim flagged as owner question 5 in `OWNER_DECISIONS_KA.md` — "`index.yml`'s hero still says
full insurance coverage" — was true of the file but **never reached a visitor**. I corrected the
line anyway in all six languages (it is wrong wherever it lives, and it will render if
`home_hero.yml` ever stops overriding it), and kept it to the original length as instructed. Two
notes for whoever owns this:

- `content/settings/home_hero.yml` is off-limits to this pass. Its live `lead` is trip-planner
  copy ("Build a trip, shape the route, and share it…") and makes no insurance claim, so there is
  nothing inaccurate on the live home-page hero today.
- The published home page does carry the corrected insurance wording from
  `content/settings/meta.yml`'s `org_desc` ("CDW and TPL insurance included…"), fixed in the
  earlier reconciliation pass.

### 3. "SCDW reduces the excess to zero" — left as written, flagging the judgement call

The owner's answer 5 forbids "zero excess" / "no deductible" **as a general claim**. `terms.yml`
`blocks[9]`, `faq.yml` `blocks[5].items[1]`, `index.yml` `blocks[14].items[4]` and `pricing.yml`
`blocks[6]` each state that the *optional, paid* SCDW add-on (25–45 ₾/day) reduces the excess to
zero. These are conditional statements attached to a priced extra, not general claims about the
standard rate, and every one of them names the standard excess first. I left them unchanged. If
the owner meant that SCDW only *reduces* the excess rather than eliminating it, these twenty-plus
strings (and `pricing.yml`'s "Full excess waiver (SCDW)" row label) all need rewording — say so
and it is a quick follow-up.

### 4. Pre-existing warnings not caused by this pass

- `WARNING: cars: 17 published records have no main image` — from `build.py --validate-only`,
  unrelated, pre-existing.
- `seo_audit.py` WARNs on `/ka/trip-planner/` (75 chars) and `/ru/trip-planner/` (81 chars) title
  length. Neither page is in this pass's editable file list.

---

## Verification

```
$ python3 build.py --validate-only
WARNING: cars: 17 published records have no main image
✔ content validation passed

$ python3 build.py /tmp/pg
✔ 2292 HTML გვერდი (17 ავტომობილი, 4 სტატია, 6 ენა) → /tmp/pg

$ python3 scripts/seo_audit.py /tmp/pg
TOTAL: 0 ERROR, 2 WARN, 20 INFO
```

Every language's blocks list kept its original length after editing (terms 23, faq 13, pricing 19,
index 19, about 14, contact 8 — identical across all six languages, unchanged from before). All 36
prose changes that reach a rendered page were confirmed present in the built HTML for their
language; the only edit that does not appear in the build is `index.yml`'s `hero.lead`, for the
reason given in finding 2.

Georgian terminology follows `docs/seo/TRANSLATION_QA.md` §3.2: `გაქირავება` in company voice,
`დაქირავება` where the customer is the subject, never `ქირაობა` in any new copy.
