# მობილური გამოცდილება და ხელმისაწვდომობა

## MOB-01 — responsive/PWA ხარისხის გამყარება

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0

**მიზანი:** მობილურზე planner იყოს ძირითადი პროდუქტი და არა desktop-ის დაპატარავებული ვერსია.

**სამუშაო:** map/list/timeline tabs; bottom sheets; safe areas; keyboard resize; offline/install states; no nested scrolling; app header/download button; manifest/service worker audit.

**Acceptance criteria:** 360×800, 390×844, tablet და desktop-ზე horizontal scroll ნულია; ძირითადი CTA ჩანს; input suggestion keyboard-ის ზემოთ ჩანს; install/update flow გასაგებია.

## MOB-02 — Android/iOS distribution გეგმა

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P2  
დამოკიდებულება: MOB-01, OFF-01

**მიზანი:** ჩამოტვირთვის ღილაკს ჰქონდეს რეალურად მხარდაჭერილი Android და iOS გზა.

**სამუშაო:** PWA vs wrapper/native ADR; signing; package IDs; privacy declarations; store assets; release channel; crash reporting; update policy; APK checksum.

**Acceptance criteria:** Android build ხელმოწერილია და install/update მოწმდება; iOS-ის ლინკი მხოლოდ რეალური TestFlight/App Store არსებობისას ჩანს; release runbook არსებობს.

## A11Y-01 — WCAG 2.1 AA და keyboard flow

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: PLN-07

**მიზანი:** planner, modal, map controls და account გამოყენებადი იყოს კლავიატურითა და screen reader-ით.

**სამუშაო:** semantics; labels; focus trap/restore; contrast; selected state არა მხოლოდ ფერით; live regions; reduced motion; RTL focus order; keyboard route editing.

**Acceptance criteria:** ძირითადი flow სრულდება mouse-ის გარეშე; automated audit-ში critical violation ნულია; focus არ იკარგება modal/drawer დახურვისას; touch target ≥44px.

