# ლოკალური იმპლემენტაციის სტატუსი

**ეს არის პროექტის ერთადერთი მიმდინარე სტატუს-დოკუმენტი.** სხვა დოკუმენტებში (AUDIT.md, REQUIREMENTS_MATRIX.md, IMPLEMENTATION_REPORT.md) მოცემული რიცხვები ეხება მათი დაწერის თარიღს.

განახლდა: 2026-08-16 · branch `harden-static-rental-funnel` · deploy და DNS არ შეცვლილა.

## გადამოწმებული რიცხვები

ყველა ქვემოთ მოცემული მნიშვნელობა გაზომილია 2026-08-16-ს, ამ branch-ზე:

| მაჩვენებელი | მნიშვნელობა |
|---|---|
| ავტომატური ტესტი | 26 / 26 გადის |
| სრული build | 2,004 გვერდი (17 ავტომობილი, 4 სტატია, 6 ენა) |
| `dist/` ბოლო გენერაცია | 2,014 HTML ფაილი |
| ღირსშესანიშნაობა | 257 |
| strict build | **ბლოკავს** (იხ. publication blockers) |

## მუშაობს

- ერთი Leaflet სამუშაო სივრცე: დაგეგმვა / აღმოჩენა / მარშრუტი.
- ექვსენოვანი KA/EN/RU/FA/HE/AR გენერაცია RTL-ით და მრავალენოვანი ძებნით.
- პროგრესული კლასტერები, რეალურ გზებზე მარშრუტი, traffic, GPS/ხელით მდებარეობა, ნამყოფის ფილტრი, ველოკანდიდატები.
- Curated რთული გზების matrix, ზამთრის კონსერვატიული გაფრთხილებები, ერთიანი ღამისთევა/სასტუმრო, მკაცრი ავტომობილის მინიმუმი.
- სტანდარტული ტურები და ადგილის რეიტინგის ფილტრი.
- სტატიკური გაქირავების მოთხოვნა: WhatsApp + Netlify Forms, კონტექსტით.
- ადმინისტრაცია: სტატუსი, ხელმისაწვდომობა, ფოტოები, სამი GEL ტარიფი, დეპოზიტი, ფრანშიზა, დაზღვევა, გარბენი, დამატებითი სერვისები.
- PWA manifest/service worker.

## ცნობილი არქიტექტურული ვალი — Firebase booking

**გაქირავების საჯარო ნაკადი სტატიკურია** (`static/booking.js` → WhatsApp / Netlify Forms). ეს არის ფაზა 1-ის სწორი და მოქმედი გზა.

**მაგრამ Firebase-ის ძველი booking ფენა ბოლომდე არ ამოღებულა:**

- `bookings` კოლექციას **არცერთი კოდი არ წერს** — `addDoc(collection(db,'bookings'))` არსად არსებობს;
- `static/auth.js:370` და `static/admin-bookings.js:29` მას მხოლოდ **კითხულობენ**;
- `extensionRequests` და მანქანის `reviews` წერისას `bookingId`-ს ეყრდნობიან, ანუ ისინიც მიუწვდომელია.

შედეგი: ანგარიშის გვერდზე „ჩემი ჯავშნები" და ადმინის ჯავშნების კონსოლი ყოველთვის ცარიელი იქნება. ეს **მკვდარი ტოტია**, არა დასრულებული ფუნქცია.

გადაწყვეტილება საჭიროა ორიდან ერთი:
1. ფენა წაიშალოს, სანამ ფაზა 3 (რეალური ჯავშანი) არ დადგება; ან
2. შენარჩუნდეს, მაგრამ UI-ში აშკარად აღინიშნოს, რომ ჯერ არ არის აქტიური.

სანამ ეს არ გადაწყდება, [REQUIREMENTS_MATRIX.md](REQUIREMENTS_MATRIX.md)-ის შესაბამისი სტრიქონები „დასრულებულად" არ ჩაითვლება.

## Publication blockers — მფლობელის მონაცემები

strict build-ის რეალური გამოსავალი 2026-08-16:

```
WARNING: settings/site.yml: 'phone' still contains placeholder data
WARNING: settings/site.yml: 'mobile' still contains placeholder data
WARNING: settings/site.yml: 'email' still contains placeholder data
WARNING: settings/site.yml: 'software_email' still contains placeholder data
WARNING: settings/site.yml: social links still contain placeholder data
WARNING: cars: 17 published records have no main image
ERROR: strict mode treats warnings as publication blockers
```

ეს სია **2026-08-14-დან უცვლელია**. ის არ არის პროგრამირების ამოცანა — საჭიროა რეალური ტელეფონი, WhatsApp, ელფოსტა, სოციალური ბმულები და 17 ავტომობილის მთავარი ფოტო. სანამ არ შეივსება, ყველა სხვა სამუშაო გამოქვეყნებამდე ვერ მიდის.

დამატებით საჭიროა: ღირსშესანიშნაობების ფოტოების ადამიანური ვიზუალური დადასტურება; hosting OAuth და (სურვილისამებრ) Firebase კონფიგურაცია.

## განზრახ არ არის გაკეთებული

- გადახდის gateway, realtime fleet lock, ავტომატურად დადასტურებული ჯავშანი.
- გამოგონილი შეფასება, ფასი, ხელმისაწვდომობა, ფოტო ან ბიზნეს-ფაქტი.
- ხელმოწერილი App Store / Google Play პაკეტი; deliverable არის PWA.

## დაუდოკუმენტირებელი არტეფაქტი

repo-ს root-ში დევს `Drive-On-release.apk` (42MB) და `mobile/fleet_house_app/`, მაშინ როცა ყველა დოკუმენტი PWA-ს ასახელებს deliverable-ად. ამ native ნაწილს მართვადი დოკუმენტი არ აქვს — საჭიროა ან დოკუმენტირება, ან repo-დან ამოღება.

## შემდეგი ნაბიჯი

1. მფლობელის მონაცემები (ზემოთ) — ხსნის strict build-ს.
2. Firebase booking ფენის გადაწყვეტა (წაშლა ან აშკარა „არააქტიური" მდგომარეობა).
3. [RESEARCH.md](../RESEARCH.md)-ის პრიორიტეტები #2 და #3 — ალგორითმი დაწერილია, build-ზე რენდერი აკლია.
4. მხოლოდ ამის შემდეგ: commit/push, deploy, production smoke test.
