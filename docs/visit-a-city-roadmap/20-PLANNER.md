# დამგეგმავი და itinerary engine

## PLN-01 — დამგეგმავის ერთიანი state model

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0

**მიზანი:** საწყისი ადგილი, დრო, დღეები, ტრანსპორტი, არჩეული ადგილები და მზა ტური ერთ წყაროში იმართებოდეს.

**სამუშაო:** აღწერე canonical state schema; URL/local/cloud serialization; state transitions; migration ძველი localStorage მონაცემებიდან; duplicate planner/explorer state-ის გაუქმება.

**Acceptance criteria:** ერთი ცვლილება ყველა შესაბამის UI ნაწილში სინქრონულად ჩანს; refresh არ კარგავს გეგმას; ძველი შენახული გეგმა უსაფრთხოდ იტვირთება ან მომხმარებელს ეძლევა გასაგები recovery.

## PLN-02 — საწყისი ადგილი: search, GPS და manual pin

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PLN-01

**მიზანი:** არჩეული ქუთაისის აეროპორტი, სასტუმრო, GPS ან რუკაზე მონიშნული ადგილი რეალურად გახდეს route origin.

**სამუშაო:** მრავალენოვანი alias search; suggestion უშუალოდ input-ის ქვეშ; exact coordinates; GPS accuracy state; manual draggable pin; origin ცვლილებაზე route/time recompute და map fit.

**Acceptance criteria:** თბილისის, ქუთაისის აეროპორტისა და arbitrary pin-ის ტესტებში პირველი route leg სწორ origin-ზე იწყება; არჩეული მნიშვნელობა refresh-ზე ინახება; უარყოფილი GPS-ს აქვს manual fallback.

## PLN-03 — დღიური timeline engine

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PLN-01, CNT-01

**მიზანი:** თითო დღეს ჰქონდეს სანდო განრიგი — start, drive, visit, break, close, return/stay.

**სამუშაო:** event მოდელი; travel-time provider/fallback; visit duration; opening-hours constraints; overnight/hotel; multi-day allocation; conflict explanation; timezone/date.

**Acceptance criteria:** timeline-ის ჯამი ემთხვევა არჩეულ საათებს; დახურულ ადგილზე ჩანს გაფრთხილება; ყოველი გაჩერება აჩვენებს მისვლის/გასვლის დროს; route reorder გადათვლის შემდეგ შედეგი deterministic-ია.

## PLN-04 — დროის ბიუჯეტი და შესაძლო ადგილები

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PLN-03

**მიზანი:** ამორთული ადგილის დრო გათავისუფლდეს და შესაძლო დამატებები ავტომატურად გააქტიურდეს.

**სამუშაო:** selected/available/no-fit ჯგუფები; detour+visit გამოთვლა; ნაცრისფერი disabled მდგომარეობა; fit-ის შემდეგ სრული ფერი; დარჩენილი დრო; რატომ ვერ ეტევა; ±0.5 საათი და ხელით შეყვანა.

**Acceptance criteria:** ადგილის მოხსნა ზრდის დარჩენილ დროს; ახლად ჩატევადი ადგილი ხდება clickable; დაუტევადი რჩება disabled და აჩვენებს რამდენი დრო აკლია; დამატება ხელახლა ითვლის მთელ დღეს.

## PLN-05 — შესვენება, custom place და სასტუმროები

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: PLN-03

**მიზანი:** გეგმა მოერგოს რეალურ ცხოვრებას და არა მხოლოდ POI სიას.

**სამუშაო:** meal/rest/custom event; საკუთარი სახელისა და coordinate-ის ადგილი; ერთი ან რამდენიმე სასტუმრო; check-in/out; overnight start; drag/reorder/delete.

**Acceptance criteria:** custom ადგილი route-ში მონაწილეობს; break ამცირებს ხელმისაწვდომ დროს; სასტუმრო ცვლის შესაბამისი დღის დასასრულსა და შემდეგი დღის დასაწყისს; მონაცემი ინახება/იზიარება.

## PLN-06 — სტანდარტული ტურის გამოყენება და რედაქტირება

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PLN-03, CNT-04

**მიზანი:** ტურის არჩევის შემდეგ popup დაიხუროს, რუკა მოერგოს ტურს და მომხმარებელმა თავისუფლად შეცვალოს იგი.

**სამუშაო:** modal list/filter; მოკლე metadata; apply action; waypoint selection; title badge; duration/car/group/season; copy-to-user-plan; add/remove/reorder; reset to template.

**Acceptance criteria:** არჩეული 2/3/5-დღიანი ტური რუკასა და timeline-ში სრულად ჩანს; ცვლილებები template-ს არ აზიანებს; reset აღადგენს საწყისს; არ ხდება ახალ გვერდზე გადასვლა.

## PLN-07 — მარტივი planner UX

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PLN-01–06

**მიზანი:** პირველად მოსული მომხმარებელი დახმარების გარეშე შექმნის გეგმას.

**სამუშაო:** progressive disclosure; პირველი ნაბიჯი მხოლოდ origin/time/interests; compact controls; primary CTA; advanced options popup; desktop ერთ ეკრანში; mobile map/list/timeline tabs; ადამიანური microcopy.

**Acceptance criteria:** 5 usability სცენარში მონაწილე პოულობს დაგეგმვის დაწყებას ≤10 წამში; არ არის horizontal scroll; ძირითადი map ჩანს fold-ში; keyboard/touch targets მუშაობს; ერთი და იგივე არჩევანი ორჯერ არ მეორდება.

