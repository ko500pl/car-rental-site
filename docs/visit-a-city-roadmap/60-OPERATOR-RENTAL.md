# ტუროპერატორი და კონტექსტური გაქირავება

## OPR-01 — ტუროპერატორის სამუშაო სივრცე

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P2

**მიზანი:** ოპერატორმა შექმნას განმეორებადი ტური, მართოს ჯგუფი და გაუზიაროს კლიენტს.

**სამუშაო:** operator role; reusable templates; customer copy; participant list/status; branded PDF/JPG; vehicle/hotel/guide notes; itinerary version; inquiry tracking.

**Acceptance criteria:** ოპერატორის template მომხმარებლის პირადი ტურისგან იზოლირებულია; კლიენტი ბმულით ხედავს სწორ ვერსიას; export შეიცავს შეთანხმებულ ბრენდსა და საკონტაქტო მონაცემებს.

## RNT-01 — კონტექსტური ავტომობილის რეკომენდაცია

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: PLN-03

**მიზანი:** მანქანა გამოჩნდეს როგორც მოგზაურობის დამხმარე, არა მთავარი გაყიდვა.

**სამუშაო:** own/rent/driver choice; road requirement; group/luggage; dates; cheapest suitable/comfortable alternatives; approximate GEL/USD; explanation why.

**Acceptance criteria:** საკუთარი მანქანის არჩევისას rental CTA არ აწვება მომხმარებელს; 4×4 route არ სთავაზობს შეუსაბამო მანქანას; recommendation აჩვენებს მახასიათებლებსა და სავარაუდო ფასს.

## RNT-02 — დაჯავშნის popup და მოთხოვნის სტატუსი

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: RNT-01, ACC-01

**მიზანი:** მანქანის მოთხოვნა სრულდებოდეს მიმდინარე გვერდიდან.

**სამუშაო:** modal/drawer; prefilled dates/user/car; no duplicate origin; contact; consent; request submission; account rental history/status; later payment boundary.

**Acceptance criteria:** popup არ ტოვებს გვერდს; planner-ის თარიღები ავტომატურად მოდის და იცვლება; წარმატებული მოთხოვნა ჩანს პირად გვერდზე; duplicate submit იბლოკება.

