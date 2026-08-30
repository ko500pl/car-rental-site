# Graph Report - car-rental-site  (2026-08-23)

## Corpus Check
- 113 files · ~6,142,388 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1150 nodes · 2046 edges · 99 communities (91 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `222b8769`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build.py
- planner.js
- explorer.js
- workspace.js
- auth.js
- ProductFeatureTests
- leaflet.js
- fetch_photos.py
- 00-DOCUMENTATION-INDEX.md
- booking.js
- main.dart
- ავტოგაქირავების ვებგვერდი + ადმინ-პანელი + საქართველოს ტურისტული რუკა
- 5. SEO / GEO სტრუქტურა — რითი რანჟირდებიან ისინი და რა არ გვაქვს
- F
- დეტალური აუდიტი — 2026-08-14
- app-mobile.js
- Implementation work
- AttractionMediaTests
- MainActivity.kt
- ადმინისტრაციის გამართვა
- Drive On — პროდუქტისა და ტექნიკური აუდიტი
- Drive On — მარტივი სამოგზაურო პროდუქტის დიზაინ-სისტემა
- community.js
- არქიტექტურა და build
- ღირსშესანიშნაობების აუდიტი — 2026-08-16
- ანგარიშების ჩართვა — Firebase (15 წუთი)
- Implementation report
- Ae
- m
- გაქირავების წესები
- ლოკალური იმპლემენტაციის სტატუსი
- e
- Drive On — მოდულების დოკუმენტაცია
- სტანდარტული ტურების კატალოგი
- მთავარი გვერდის UX-აუდიტი — 10,000 სინთეზური მომხმარებლის სცენარი
- UX აუდიტი — 100 სიმულირებული მომხმარებლის სცენარი
- ღირსშესანიშნაობების ფოტოების აუდიტი
- load
- ადმინისტრაცია და წვდომა
- Attraction file spec — content/attractions/<slug>.yml
- ტესტირება, გამოქვეყნება და აღდგენა
- მოთხოვნების შესრულების მატრიცა — ლოკალური ვერსია
- weather.js
- ავტოპარკი და ავტომობილები
- გაქირავების მოთხოვნა და WhatsApp
- build_docs_html.py
- classify_attraction_images.py
- search_missing_attraction_images.py
- app.js
- Je
- fleet_house_app
- i
- __init__.py
- sw.js
- audit_performance.py
- visit-a-city-roadmap/README.md
- PERF-02 — რუკის მონაცემების ნაწილობრივი ჩატვირთვა
- PERF-01 — სიჩქარის საბაზისო გაზომვა და ბიუჯეტი
- დამგეგმავი და itinerary engine
- References
- apply_verified_attraction_images.py
- ke
- trip.js
- სამუშაო წესები აგენტებისთვის
- საფუძველი, რელიზი და სიჩქარე
- ოფიციალური source/build სტრუქტურა
- ადგილები, ფოტოები და სტანდარტული ტურები
- PERF-01 — performance baseline
- audit_attraction_images.py
- პროდუქტის გზის რუკა
- განმეორებადი სამუშაო გარემო
- CI ხარისხის კარიბჭე და ხელით რელიზი
- Community და თანამშრომლობა
- ანალიტიკა, QA და ოპერაციები
- Drive On — Visit A City-ის დონისკენ განვითარების სამუშაო გეგმა
- MapChunkingTests
- ანგარიში, შენახვა და ოფლაინ რეჟიმი
- ტუროპერატორი და კონტექსტური გაქირავება
- მობილური გამოცდილება და ხელმისაწვდომობა
- ღია კითხვები და გადაწყვეტილებების ჟურნალი
- 2026-08-20 — PERF-01-ის შემდეგ
- Q: მინდა რომ შეისწავლო პროგრამა და გავაგრძელოთ მუშაობა
- Q: აბა გაიარე თავიდან
- check_javascript_syntax.py
- verify_repeatable_build.py
- PerformanceAuditTests
- ReleaseGateTests
- read_pins
- run_quality_gate.py
- check_project_layout.py

## God Nodes (most connected - your core abstractions)
1. `main()` - 35 edges
2. `page_url()` - 30 edges
3. `render()` - 28 edges
4. `render_static_page()` - 22 edges
5. `render()` - 22 edges
6. `render_attraction()` - 21 edges
7. `render_map_page()` - 20 edges
8. `suggestNear()` - 19 edges
9. `render_car()` - 18 edges
10. `render_region()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `validate()`  [EXTRACTED]
  build.py → sitegen/validation.py
- `main()` --calls--> `css()`  [EXTRACTED]
  build.py → theme.py
- `one()` --calls--> `dump()`  [EXTRACTED]
  fetch_gallery.py → yaml_io.py
- `main()` --calls--> `dump()`  [EXTRACTED]
  fetch_hotels.py → yaml_io.py
- `one()` --calls--> `dump()`  [EXTRACTED]
  fetch_photos.py → yaml_io.py

## Import Cycles
- None detected.

## Communities (99 total, 8 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.05
Nodes (123): attr_detail(), attr_facts(), attr_url(), bidi(), car_cat_label(), car_node(), car_url(), cars_grid() (+115 more)

### Community 1 - "planner.js"
Cohesion: 0.06
Nodes (71): alongTheWay(), announce(), bindStopGestures(), dropStop(), edgeScroll(), engage(), paint(), reposition() (+63 more)

### Community 2 - "explorer.js"
Cohesion: 0.07
Nodes (60): addWp(), alongTheWay(), budgetMode(), budgetVal(), chainTime(), close(), clusterIcon(), draw() (+52 more)

### Community 3 - "workspace.js"
Cohesion: 0.08
Nodes (56): applyTour(), attachDrag(), move(), rows(), up(), boundsOverlap(), budgetMin(), cachedChunk() (+48 more)

### Community 4 - "auth.js"
Cohesion: 0.10
Nodes (36): accountPage(), esc(), esc0(), fire(), getProfile(), headerBox(), init(), initLocal() (+28 more)

### Community 5 - "ProductFeatureTests"
Cohesion: 0.09
Nodes (6): is_public(), Report, validate(), CurrencyTests, ProductFeatureTests, PublishingTests

### Community 6 - "leaflet.js"
Cohesion: 0.07
Nodes (7): a(), Ci(), ei(), ii(), l(), ri(), x()

### Community 7 - "fetch_photos.py"
Cohesion: 0.12
Nodes (27): candidates(), main(), name_words(), one(), Commons-ის გეოძებნის ყველა შესაფერისი ფაილი, მთავარი ფოტოს გარდა., relevant(), save_g(), fetch() (+19 more)

### Community 8 - "00-DOCUMENTATION-INDEX.md"
Cohesion: 0.12
Nodes (8): ფასები და კომერციული პირობები, მოგზაურობის დამგეგმავი, რუკა და ადგილების აღმოჩენა, კონტენტი, ფოტოები და ექვსი ენა, SEO და სოციალური გაზიარება, ანგარიშები და შენახული ტურები, „ჩემი ჯავშნები" — ამჟამად არააქტიური, ჯგუფები, შეტყობინებები და შეფასებები

### Community 9 - "booking.js"
Cohesion: 0.17
Nodes (20): ajaxifyForms(), boot(), bootAll(), bootDialog(), open(), bootInquiry(), calc(), init() (+12 more)

### Community 10 - "main.dart"
Cohesion: 0.12
Nodes (16): build, _counter, createState, _incrementCounter, main, MyApp, MyHomePage, _MyHomePageState (+8 more)

### Community 11 - "ავტოგაქირავების ვებგვერდი + ადმინ-პანელი + საქართველოს ტურისტული რუკა"
Cohesion: 0.12
Nodes (17): 1. სწრაფი დაწყება, 2. გაშვება: ნაბიჯ-ნაბიჯ, 3. რა იმართება ადმინიდან, 4. რუკა და მარშრუტები, 5. სტრუქტურა, 6. ძიებაში აღმოჩენადობა, 7. გაშვების შემდეგ, 8. რა უნდა შეამოწმოთ გამოქვეყნებამდე (+9 more)

### Community 12 - "5. SEO / GEO სტრუქტურა — რითი რანჟირდებიან ისინი და რა არ გვაქვს"
Cohesion: 0.12
Nodes (17): 1. განხილული საიტები, 2. რაში ვართ უკვე თანაბრად ან წინ, 3. 17 ყველაზე ღირებული ნაკლი, 3.1 კონვერსია, 3.2 ტრაფიკი / SEO, 3.3 პროდუქტი და დაბრუნების მიზეზი, 3.4 მონაცემი და კონტენტი, 4. რა გავაკეთოთ შემდეგ — 6 პრიორიტეტი (+9 more)

### Community 13 - "F"
Cohesion: 0.27
Nodes (10): F(), G(), k(), me(), e(), Oe(), p(), q() (+2 more)

### Community 14 - "დეტალური აუდიტი — 2026-08-14"
Cohesion: 0.14
Nodes (13): 1. უსაფრთხო მანქანის რეკომენდაცია, 2. CMS გალერეის ფორმატი, 3. კონტაქტების დუბლირება, 4. მოთხოვნის ნაკადი, 5. sitemap freshness, 6. დოკუმენტაციის drift, დადასტურებული ძლიერი მხარეები, დარჩენილი მაღალი პრიორიტეტის მფლობელის ბლოკერები (+5 more)

### Community 15 - "app-mobile.js"
Cohesion: 0.11
Nodes (48): bookingSummary(), budgetMin(), cloudMode(), cloudSave(), detour(), dist(), drawMarkers(), drawRoute() (+40 more)

### Community 16 - "Implementation work"
Cohesion: 0.18
Nodes (10): Accounts, Admin/content model, Confirmed findings, Explicitly not changing, Implementation work, Planner and routing, Static-first product hardening implementation plan, Static rental conversion (+2 more)

### Community 17 - "AttractionMediaTests"
Cohesion: 0.18
Nodes (3): AttractionMediaTests, PublicClaimsTests, Keep duplicate detection measurable while the photo audit is resolved.

### Community 18 - "MainActivity.kt"
Cohesion: 0.38
Nodes (6): Activity, Bundle, MainActivity, WebViewClient, WebResourceRequest, WebView

### Community 19 - "ადმინისტრაციის გამართვა"
Cohesion: 0.20
Nodes (10): 1. საიტის გამოქვეყნება, 2. GitHub OAuth, 3. შესვლა, 4. კონტაქტები და ბიზნეს ინფორმაცია, 5. მანქანის დამატება ან შეცვლა, 6. ფოტოების ატვირთვა, 7. ფასები, 8. გამოქვეყნება და დამალვა (+2 more)

### Community 20 - "Drive On — პროდუქტისა და ტექნიკური აუდიტი"
Cohesion: 0.20
Nodes (10): 1. ტუროპერატორის პერსპექტივა, 2. Frontend-ინჟინრის პერსპექტივა, 3. Backend/არქიტექტურის პერსპექტივა, 4. დირექტორის/მარკეტოლოგის პერსპექტივა (კონვერსია), 5. SEO/GEO აუდიტორის პერსპექტივა, 6. QA პერსპექტივა, Drive On — პროდუქტისა და ტექნიკური აუდიტი, პრიორიტეტული TOP-10 (+2 more)

### Community 21 - "Drive On — მარტივი სამოგზაურო პროდუქტის დიზაინ-სისტემა"
Cohesion: 0.20
Nodes (9): Drive On — მარტივი სამოგზაურო პროდუქტის დიზაინ-სისტემა, ავტოპარკი, ვიზუალური პრინციპები, კონტენტის წესი, მთავარი სამუშაო სივრცე, მოგზაურობის სამი ნაბიჯი, პროდუქტის იერარქია, შემდგომი მიგრაცია (+1 more)

### Community 22 - "community.js"
Cohesion: 0.58
Nodes (9): api(), bindMessages(), draw(), esc(), groups(), requireUser(), reviews(), stamp() (+1 more)

### Community 23 - "არქიტექტურა და build"
Cohesion: 0.22
Nodes (8): არქიტექტურა და build, ბრძანებები, განახლება, დოკუმენტაცია build-ში, მიზანი, რატომ არის ნაგულისხმევად გამორთული, უცვლელი პრინციპები, ძირითადი ნაწილები

### Community 24 - "ღირსშესანიშნაობების აუდიტი — 2026-08-16"
Cohesion: 0.22
Nodes (8): აუდიტის საზღვრები, დამატების კანდიდატები შემდეგი ეტაპისთვის, ღირსშესანიშნაობების აუდიტი — 2026-08-16, შედეგი, „ჩემი მდებარეობა“, წაშლის გადაწყვეტილება, წყაროებით დადასტურებული ცვლილებები, ხარისხის კონტროლი

### Community 25 - "ანგარიშების ჩართვა — Firebase (15 წუთი)"
Cohesion: 0.22
Nodes (8): 1. პროექტის შექმნა, 2. ვებ-აპლიკაციის დამატება, 3. დომენის დაშვება, 4. Firestore-ის წესები — აუცილებელი, 5. ლიმიტები (უფასო Spark გეგმა), 6. რაც იურიდიულად უნდა გააკეთოთ, 7. შემოწმება, ანგარიშების ჩართვა — Firebase (15 წუთი)

### Community 26 - "Implementation report"
Cohesion: 0.22
Nodes (9): Admin capabilities, Bugs fixed, Completed, Deployment steps, Future availability integration point, Implementation report, Remaining limitations, Remaining manual owner inputs (+1 more)

### Community 27 - "Ae"
Cohesion: 0.33
Nodes (6): Ae(), Ie(), Le(), O(), Re(), te()

### Community 28 - "m"
Cohesion: 0.31
Nodes (9): at(), be(), d(), m(), ve(), W(), xe(), ye() (+1 more)

### Community 29 - "გაქირავების წესები"
Cohesion: 0.33
Nodes (5): გაქირავების წესები, გზები, მართვა, შინაარსი, წყაროს ერთიანობა

### Community 30 - "ლოკალური იმპლემენტაციის სტატუსი"
Cohesion: 0.25
Nodes (8): Publication blockers — მფლობელის მონაცემები, გადამოწმებული რიცხვები, განზრახ არ არის გაკეთებული, დაუდოკუმენტირებელი არტეფაქტი, ლოკალური იმპლემენტაციის სტატუსი, მუშაობს, შემდეგი ნაბიჯი, ცნობილი არქიტექტურული ვალი — Firebase booking

### Community 31 - "e"
Cohesion: 0.25
Nodes (8): bi(), c(), e(), hi(), Pi(), Qe(), Ti(), u()

### Community 32 - "Drive On — მოდულების დოკუმენტაცია"
Cohesion: 0.29
Nodes (7): Drive On — მოდულების დოკუმენტაცია, HTML ვერსიები, დიზაინი, მოდულები, რომელი დოკუმენტია ავტორიტეტული, საძირკვლის დოკუმენტები (repo root), სტატუსი და აუდიტები

### Community 33 - "სტანდარტული ტურების კატალოგი"
Cohesion: 0.29
Nodes (6): გამოყენებული კვლევის წყაროები, დაგეგმვის პრინციპები, თემატური ჯგუფები, სტანდარტული ტურების კატალოგი, უსაფრთხოების შენიშვნა, შედეგი

### Community 34 - "მთავარი გვერდის UX-აუდიტი — 10,000 სინთეზური მომხმარებლის სცენარი"
Cohesion: 0.29
Nodes (6): განხორციელებული ცვლილებები, დასადასტურებელი რეალური მეტრიკები, კვლევის სტატუსი, მთავარი გვერდის UX-აუდიტი — 10,000 სინთეზური მომხმარებლის სცენარი, მთავარი პრობლემები, მოდელირებული სეგმენტები

### Community 35 - "UX აუდიტი — 100 სიმულირებული მომხმარებლის სცენარი"
Cohesion: 0.29
Nodes (6): UX აუდიტი — 100 სიმულირებული მომხმარებლის სცენარი, განხორციელებული ცვლილებები, მთავარი მიგნებები, მნიშვნელოვანი განმარტება, სცენარების შემადგენლობა, შემდეგი რეალური კვლევა

### Community 36 - "ღირსშესანიშნაობების ფოტოების აუდიტი"
Cohesion: 0.22
Nodes (8): 2026-08-19 — მასობრივი შესწორება (ეს განახლება), აუდიტის მოცულობა, აშკარად არასწორი ან მთავარ ფოტოდ მიუღებელი გამოსახულებები, გადაწყვეტილების წესი, ზუსტი ადგილია, მაგრამ უკეთესი მთავარი ფოტო სჭირდება, ისტორია: 2026-08-15-ის აუდიტი, ღირსშესანიშნაობების ფოტოების აუდიტი, შემოწმების სტანდარტი

### Community 37 - "load"
Cohesion: 0.57
Nodes (6): esc(), load(), draw(), query(), login(), note()

### Community 38 - "ადმინისტრაცია და წვდომა"
Cohesion: 0.33
Nodes (4): ადმინისტრაცია და წვდომა, მისამართი, სამუშაო პროცესი, უსაფრთხო წვდომა

### Community 39 - "Attraction file spec — content/attractions/<slug>.yml"
Cohesion: 0.33
Nodes (5): Attraction file spec — content/attractions/<slug>.yml, Hard rules, How to write the files, The six language blocks, Writing quality

### Community 40 - "ტესტირება, გამოქვეყნება და აღდგენა"
Cohesion: 0.33
Nodes (5): Windows: build-ის კონსოლის კოდირება, ადგილობრივი შემოწმება, აღდგენა და git, დოკუმენტაციის HTML, ტესტირება, გამოქვეყნება და აღდგენა

### Community 41 - "მოთხოვნების შესრულების მატრიცა — ლოკალური ვერსია"
Cohesion: 0.33
Nodes (6): დასრულებული და ლოკალურად შემოწმებული, დასრულებული კოდი, მაგრამ production ინფრასტრუქტურას მოითხოვს, ლოკალური QA შედეგი, მოთხოვნების შესრულების მატრიცა — ლოკალური ვერსია, რეალური მონაცემებით შესავსები publication blockers, საბოლოო დარჩენილი ნაბიჯი

### Community 42 - "weather.js"
Cohesion: 0.47
Nodes (3): get(), icon(), inRange()

### Community 43 - "ავტოპარკი და ავტომობილები"
Cohesion: 0.40
Nodes (4): ადმინისტრატორის შესაძლებლობები, ავტოპარკი და ავტომობილები, საჯარო ქცევა, ფოტო

### Community 44 - "გაქირავების მოთხოვნა და WhatsApp"
Cohesion: 0.40
Nodes (5): WhatsApp, გაქირავების მოთხოვნა და WhatsApp, ნაკადი, ფორმა, ფორმის fallback

### Community 45 - "build_docs_html.py"
Cohesion: 0.60
Nodes (4): main(), md_links_to_html(), Rewrite markdown links to their generated HTML twins. Every generated page…, title_of()

### Community 46 - "classify_attraction_images.py"
Cohesion: 0.80
Nodes (4): classify(), main(), meaningful_tokens(), norm()

### Community 47 - "search_missing_attraction_images.py"
Cohesion: 0.83
Nodes (3): main(), request(), search()

### Community 48 - "app.js"
Cohesion: 0.83
Nodes (3): language(), showInstall(), standalone()

### Community 49 - "Je"
Cohesion: 0.67
Nodes (4): Je(), ni(), oi(), si()

### Community 51 - "i"
Cohesion: 1.00
Nodes (3): i(), Mi(), zi()

### Community 62 - "audit_performance.py"
Cohesion: 0.18
Nodes (16): browser_sample(), BrowserResult, human_bytes(), local_path(), main(), p75(), HTMLParser, Path (+8 more)

### Community 64 - "PERF-02 — რუკის მონაცემების ნაწილობრივი ჩატვირთვა"
Cohesion: 0.22
Nodes (8): PERF-02 — რუკის მონაცემების ნაწილობრივი ჩატვირთვა, გაზომილი შედეგი, განხორციელებული ცვლილებები, დაბრუნება, დარჩენილი სამუშაო, მონაცემთა ნაკადი, შედეგი, შემოწმება

### Community 65 - "PERF-01 — სიჩქარის საბაზისო გაზომვა და ბიუჯეტი"
Cohesion: 0.22
Nodes (9): PERF-01 — სიჩქარის საბაზისო გაზომვა და ბიუჯეტი, გადაწყვეტილებები, გარემო და სცენარები, დასრულების მტკიცებულება, მიზანი, მიღების სამიზნეები, რას ვზომავთ, როგორ განმეორდეს გაზომვა (+1 more)

### Community 66 - "დამგეგმავი და itinerary engine"
Cohesion: 0.22
Nodes (8): PLN-01 — დამგეგმავის ერთიანი state model, PLN-02 — საწყისი ადგილი: search, GPS და manual pin, PLN-03 — დღიური timeline engine, PLN-04 — დროის ბიუჯეტი და შესაძლო ადგილები, PLN-05 — შესვენება, custom place და სასტუმროები, PLN-06 — სტანდარტული ტურის გამოყენება და რედაქტირება, PLN-07 — მარტივი planner UX, დამგეგმავი და itinerary engine

### Community 67 - "References"
Cohesion: 0.28
Nodes (6): main(), HTMLParser, Path, Check generated HTML references without making network requests., References, resolve()

### Community 68 - "apply_verified_attraction_images.py"
Cohesion: 0.46
Nodes (7): clean(), credit_block(), download_webp(), license_url(), main(), Path, replace_sections()

### Community 69 - "ke"
Cohesion: 0.25
Nodes (8): h(), j(), Jt(), ke(), ne(), Qt(), s(), $t()

### Community 70 - "trip.js"
Cohesion: 0.32
Nodes (4): hav(), leg(), mountain(), suggestCar()

### Community 71 - "სამუშაო წესები აგენტებისთვის"
Cohesion: 0.29
Nodes (6): აკრძალული „მოკლე გზები“, განხორციელებისას, დავალების სტატუსის შაბლონი, დასრულების კრიტერიუმი, დაწყებამდე, სამუშაო წესები აგენტებისთვის

### Community 72 - "საფუძველი, რელიზი და სიჩქარე"
Cohesion: 0.29
Nodes (7): FND-01 — ოფიციალური source/build სტრუქტურა, FND-02 — განმეორებადი გარემო და dependency lock, FND-03 — CI test/build/release gate, PERF-01 — performance baseline და ბიუჯეტი, PERF-02 — რუკის მონაცემების ნაწილობრივი ჩატვირთვა, PERF-03 — სურათები, APK და cache ოპტიმიზაცია, საფუძველი, რელიზი და სიჩქარე

### Community 73 - "ოფიციალური source/build სტრუქტურა"
Cohesion: 0.29
Nodes (7): ავტომატური კონტროლი, ერთადერთი build output, ერთი ოფიციალური პროექტი, ოფიციალური source/build სტრუქტურა, რა არის source of truth, შესრულების მტკიცებულება, ძველი არტეფაქტების პოლიტიკა

### Community 74 - "ადგილები, ფოტოები და სტანდარტული ტურები"
Cohesion: 0.29
Nodes (6): CNT-01 — ადგილის სანდო მონაცემთა სქემა, CNT-02 — ფოტოებისა და ობიექტების სრული აუდიტი, CNT-03 — content verification workflow ადმინში, CNT-04 — 80–120 ხარისხიანი სტანდარტული ტური, CNT-05 — ექვსენოვანი ხარისხი და fallback, ადგილები, ფოტოები და სტანდარტული ტურები

### Community 75 - "PERF-01 — performance baseline"
Cohesion: 0.29
Nodes (7): PERF-01 — performance baseline, ბრაუზერის შედეგები, დასკვნა და შემდეგი ნაბიჯი, ნედლი შედეგები, სამიზნეები, საწყისი payload, ყველაზე მძიმე asset-ები და ბიუჯეტი

### Community 76 - "audit_attraction_images.py"
Cohesion: 0.48
Nodes (6): api(), distance_km(), main(), Audit attraction photos against Wikimedia Commons metadata and coordinates., source_title(), strip_html()

### Community 77 - "პროდუქტის გზის რუკა"
Cohesion: 0.33
Nodes (5): LATER — Community, ოპერატორები და native distribution, NEXT — სანდო კონტენტი, მზა ტურები და შენახვა, NOW — საიმედო საფუძველი და მთავარი დაგეგმვის flow, პროდუქტის გზის რუკა, სიმძლავრის განაწილება

### Community 78 - "განმეორებადი სამუშაო გარემო"
Cohesion: 0.33
Nodes (6): ახალი გარემოს მომზადება, განმეორებადი სამუშაო გარემო, ვერსიის შეცვლის წესი, ოფიციალური ვერსიები, საიდუმლო მონაცემების წესი, სრული ადგილობრივი შემოწმება

### Community 79 - "CI ხარისხის კარიბჭე და ხელით რელიზი"
Cohesion: 0.33
Nodes (6): CI ქცევა, CI ხარისხის კარიბჭე და ხელით რელიზი, ბოლო შემოწმების შედეგი, ერთი სრული ადგილობრივი შემოწმება, რელიზის მოკლე checklist, სხვა ჰოსტინგები

### Community 80 - "Community და თანამშრომლობა"
Cohesion: 0.33
Nodes (5): COM-01 — privacy, sharing და fork, COM-02 — შეტყობინებების ერთიანი ცენტრი, COM-03 — mute, block, report და moderation, COM-04 — ჯგუფები და ტურზე მიწვევა, Community და თანამშრომლობა

### Community 81 - "ანალიტიკა, QA და ოპერაციები"
Cohesion: 0.33
Nodes (5): DATA-01 — პროდუქტის ანალიტიკა და funnel, OPS-01 — ოპერაციული runbook და rollback, QA-01 — end-to-end კრიტიკული სცენარები, QA-02 — კონტენტის ავტომატური ვალიდაცია, ანალიტიკა, QA და ოპერაციები

### Community 82 - "Drive On — Visit A City-ის დონისკენ განვითარების სამუშაო გეგმა"
Cohesion: 0.33
Nodes (6): Drive On — Visit A City-ის დონისკენ განვითარების სამუშაო გეგმა, განახლების წესი, დოკუმენტების რუკა, მიზანი, პირველი სამუშაო რიგი, სტატუსების მნიშვნელობა

### Community 84 - "ანგარიში, შენახვა და ოფლაინ რეჟიმი"
Cohesion: 0.40
Nodes (4): ACC-01 — autosave და cross-device sync, ACC-02 — itinerary version history და restore, OFF-01 — შერჩეული ტურის ოფლაინ რეჟიმი, ანგარიში, შენახვა და ოფლაინ რეჟიმი

### Community 85 - "ტუროპერატორი და კონტექსტური გაქირავება"
Cohesion: 0.40
Nodes (4): OPR-01 — ტუროპერატორის სამუშაო სივრცე, RNT-01 — კონტექსტური ავტომობილის რეკომენდაცია, RNT-02 — დაჯავშნის popup და მოთხოვნის სტატუსი, ტუროპერატორი და კონტექსტური გაქირავება

### Community 86 - "მობილური გამოცდილება და ხელმისაწვდომობა"
Cohesion: 0.40
Nodes (4): A11Y-01 — WCAG 2.1 AA და keyboard flow, MOB-01 — responsive/PWA ხარისხის გამყარება, MOB-02 — Android/iOS distribution გეგმა, მობილური გამოცდილება და ხელმისაწვდომობა

### Community 87 - "ღია კითხვები და გადაწყვეტილებების ჟურნალი"
Cohesion: 0.40
Nodes (4): გადაწყვეტილების ჩანაწერის შაბლონი, მიღებული გადაწყვეტილებები, ღია კითხვები, ღია კითხვები და გადაწყვეტილებების ჟურნალი

### Community 88 - "2026-08-20 — PERF-01-ის შემდეგ"
Cohesion: 0.40
Nodes (4): 2026-08-20 — PERF-01-ის შემდეგ, აღდგენის წერტილები, პროექტის ზუსტად დაბრუნება, უსაფრთხოდ დათვალიერება

### Community 89 - "Q: მინდა რომ შეისწავლო პროგრამა და გავაგრძელოთ მუშაობა"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: მინდა რომ შეისწავლო პროგრამა და გავაგრძელოთ მუშაობა, Source Nodes

### Community 90 - "Q: აბა გაიარე თავიდან"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: აბა გაიარე თავიდან, Source Nodes

### Community 91 - "check_javascript_syntax.py"
Cohesion: 0.50
Nodes (4): javascript_files(), main(), Path, Check repository JavaScript syntax with Node.js.

### Community 92 - "verify_repeatable_build.py"
Cohesion: 0.60
Nodes (4): inventory(), main(), Path, Build the site twice and compare every generated file by SHA-256.

### Community 95 - "read_pins"
Cohesion: 0.67
Nodes (3): main(), Path, read_pins()

### Community 96 - "run_quality_gate.py"
Cohesion: 0.67
Nodes (3): main(), Run the complete local/CI quality gate and write a short artifact report., size_label()

## Knowledge Gaps
- **275 isolated node(s):** `title`, `_counter`, `main`, `build`, `createState` (+270 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ადმინისტრაციის გამართვა` connect `ადმინისტრაციის გამართვა` to `ადმინისტრაცია და წვდომა`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `კონკურენტების კვლევა და განვითარების გეგმა` connect `5. SEO / GEO სტრუქტურა — რითი რანჟირდებიან ისინი და რა არ გვაქვს` to `00-DOCUMENTATION-INDEX.md`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `title`, `_counter`, `main` to the rest of the system?**
  _275 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05422222222222222 - nodes in this community are weakly interconnected._
- **Should `planner.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06260406260406261 - nodes in this community are weakly interconnected._
- **Should `explorer.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07341269841269842 - nodes in this community are weakly interconnected._
- **Should `workspace.js` be split into smaller, more focused modules?**
  _Cohesion score 0.0847457627118644 - nodes in this community are weakly interconnected._