# მფლობელის ნაბიჯები (თითო ~5 წუთი)

**ყველაფერი უფასოა.** ბიუჯეტი 0 ₾ (გადაწყვეტილება 2026-10-17). ბარათს არსად შეიყვანთ. თუ რომელიმე სერვისი ბარათს, „Upgrade“-ს, „Premium“-ს ან „დაწინაურებას“ (Promote / Реклама / Продвижение) გთავაზობთ, გამოტოვეთ.

ანგარიშებს და დადასტურებას თქვენ აკეთებთ; Claude ამზადებს ყველა ტექსტს.

1. **Umami Cloud** — cloud.umami.is → რეგისტრაცია **Hobby (უფასო)** გეგმით → *Add website* → `rentup.ge` → დააკოპირეთ *Website ID* და გამომიგზავნეთ (ან ჩაწერეთ `content/settings/site.yml → analytics.website_id`). ფასიან გეგმაზე არ გადახვიდეთ.
2. **Bing Webmaster Tools** (უფასო) — bing.com/webmasters → *Import from Google Search Console* → rentup.ge.
3. **Yandex Webmaster** (უფასო) — webmaster.yandex.com → საიტის დამატება → *Meta tag* → გამომიგზავნეთ `content=` მნიშვნელობა (`site.yml → verification.yandex`).
4. **Google Business Profile** (უფასო) — business.google.com → სახელი ზუსტად `RentUp` → ველები `LISTINGS_PACK.md`-დან → დადასტურება → გამომიგზავნეთ რუკის ბმული. Google Ads-ის შეთავაზებას გამოტოვეთ.
5. **Yandex Business, 2GIS, Apple Business Connect** (საბაზისო ბარათი უფასოა) — იგივე, პაკეტის შესაბამისი ნაწილით. „Продвижение“ / „Реклама“ / ფასიანი პაკეტები არ აირჩიოთ.
6. **Localrent**, შემდეგ **DiscoverCars** — წინასწარ გადასახადს არ ითხოვენ, მაგრამ თითო ჯავშანზე იღებენ საკომისიოს (commission) — ანუ იხდით მხოლოდ მაშინ, როცა კლიენტი მოიყვანეს. ხელმოწერამდე ხელშეკრულებაში გადაამოწმეთ: საკომისიოს %, აბონემენტი ან რეგისტრაციის საფასური (თუ ითხოვენ — შეჩერდით და მითხარით). შემდეგ ატვირთეთ `exports/fleet-<platform>.csv` (`python scripts/export_fleet.py localrent`). თუ მათ შაბლონს სხვა სვეტები აქვს, `scripts/export_fleet.py`-ში შეიცვლება `COLUMNS[platform]` (თითო სვეტი — ერთი ხაზი).
7. ყოველი გამოქვეყნების შემდეგ: `python scripts/indexnow_submit.py` (უფასო).
