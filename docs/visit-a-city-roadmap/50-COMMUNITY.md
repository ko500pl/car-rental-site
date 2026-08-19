# Community და თანამშრომლობა

## COM-01 — privacy, sharing და fork

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1

**მიზანი:** გეგმის გაზიარება იყოს უსაფრთხო და გასაგები.

**სამუშაო:** Private / link-only / public; revoke link; copy/fork; author attribution; private fields stripping; share preview.

**Acceptance criteria:** private გეგმა მხოლოდ owner-ს ჩანს; unlisted ბმულის გაუქმება მუშაობს; fork დამოუკიდებელი ასლია; პირადი მონაცემები საჯარო payload-ში არ ხვდება.

## COM-02 — შეტყობინებების ერთიანი ცენტრი

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: COM-01

**მიზანი:** პირადი და ჯგუფური შეტყობინებები მარჯვენა კუთხეში ერთიანად იმართებოდეს.

**სამუშაო:** unread counts; personal/group tabs; deep link; mark read; mute; push/email preferences; pagination.

**Acceptance criteria:** count ემთხვევა რეალურ unread-ს; mute აჩერებს შეტყობინებას, მაგრამ არა შეტყობინების მიღებას; თითო notification სწორ საუბარზე გადადის.

## COM-03 — mute, block, report და moderation

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: COM-01

**მიზანი:** საჯარო Community არ გახდეს უსაფრთხოების რისკი.

**სამუშაო:** user/content report; block; group mute; moderation queue; evidence snapshot; admin action/audit trail; rate limits; abuse policy.

**Acceptance criteria:** blocked მომხმარებელი ვეღარ წერს/იწვევს; report მოდერატორის queue-ში ხვდება; ყველა admin action აღირიცხება; reporter-ის ვინაობა საჯაროდ არ ჩანს.

## COM-04 — ჯგუფები და ტურზე მიწვევა

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P2  
დამოკიდებულება: COM-02, COM-03

**მიზანი:** მომხმარებლებმა შექმნან ინტერესზე დაფუძნებული ჯგუფი და ერთობლივი ტური.

**სამუშაო:** public/private group; roles; invite/request; shared itinerary permissions; RSVP; group chat; member removal/leave.

**Acceptance criteria:** role permissions დაცულია; shared plan edit მხოლოდ უფლებამოსილს შეუძლია; მოწვევა და უარი სწორად აისახება; ჯგუფიდან გასვლა პირად გეგმას არ შლის.

