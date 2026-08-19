# ადგილები, ფოტოები და სტანდარტული ტურები

## CNT-01 — ადგილის სანდო მონაცემთა სქემა

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0

**მიზანი:** planner-ს ჰქონდეს რეალისტური განრიგისთვის საჭირო მონაცემები.

**სამუშაო:** immutable ID/slug; status; coordinates; opening hours; visit duration; entry fee; season/closure; source URL; last_verified; accessibility; parking; road/car rule; images/alt/credit/license; six-language content; migration და schema validator.

**Acceptance criteria:** incomplete published record ვერ გადის validation-ს; draft შესაძლებელია; ძველი 267 ჩანაწერი მიგრირდება მონაცემის დაკარგვის გარეშე; frontend fallback აღწერილია.

## CNT-02 — ფოტოებისა და ობიექტების სრული აუდიტი

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: CNT-01

**მიზანი:** არც ერთი ფოტო არ ასახავდეს სხვა ადგილს ან გაურკვეველ ობიექტს.

**სამუშაო:** თითო ადგილის სახელი/coordinate/source/photo შედარება; hero + gallery; license/credit; duplicate/perceptual match; ხარისხი; პრობლემის severity; ჩანაცვლების წყარო.

**Acceptance criteria:** 100% ჩანაწერს აქვს audit status და reviewer/date; მცდარი ფოტო ამოღებულია ან ჩანაცვლებულია; დაუდასტურებელი ჩანაწერი არ ითვლება verified-ად; report გენერირებულია.

## CNT-03 — content verification workflow ადმინში

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: CNT-01

**მიზანი:** ადმინისტრატორმა მარტივად ნახოს რა აკლია და რა მოძველდა.

**სამუშაო:** Draft → Needs verification → Ready → Published → Archived; filters; missing hours/photo/source; stale >6 months; impact preview; archive/restore; reference guards.

**Acceptance criteria:** ადმინი ზუსტ სიას იღებს გადასამოწმებელი ჩანაწერებით; referenced place-ის hard delete იბლოკება; publish-მდე cross-reference და translations მოწმდება.

## CNT-04 — 80–120 ხარისხიანი სტანდარტული ტური

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: CNT-01–03

**მიზანი:** რაოდენობის ნაცვლად შეიქმნას სანდო, მრავალფეროვანი ქართული ბიბლიოთეკა.

**სამუშაო:** gap analysis რეგიონი×ხანგრძლივობა×თემა×სეზონი; 1–14 დღე; city/history/wine/culinary/hiking/cycling/family/theatre/seasonal/4×4; day plans; alternative bad-weather plan; operator/source review.

**Acceptance criteria:** მინიმუმ 80 published verified tour; ყველა რეგიონი დაფარულია შეთანხმებული მინიმუმით; ყველა route reference არსებობს; duration timeline-თან თანხვედრილია; ტური editable template-ად იტვირთება.

## CNT-05 — ექვსენოვანი ხარისხი და fallback

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: CNT-01

**მიზანი:** ყველა ენაზე flow გასაგები იყოს, ნაწილობრივი თარგმანი კი build-ს არ აზიანებდეს.

**სამუშაო:** completeness meter; glossary; fallback chain; RTL; search aliases ყველა ენაზე; machine-generated ტექსტის review status; SEO/meta.

**Acceptance criteria:** publish rule ამოწმებს სავალდებულო ენებს; ქალაქის ძიება ყველა alias-ით მუშაობს არჩეული UI ენის მიუხედავად; RTL ვიზუალურად შემოწმებულია.

