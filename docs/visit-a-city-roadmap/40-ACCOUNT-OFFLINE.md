# ანგარიში, შენახვა და ოფლაინ რეჟიმი

## ACC-01 — autosave და cross-device sync

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1

**მიზანი:** გეგმა არ დაიკარგოს და სხვა მოწყობილობაზე გაგრძელდეს.

**სამუშაო:** guest local draft; sign-in merge; cloud schema; debounce autosave; sync indicator; conflict resolution; retry queue; ownership/security rules.

**Acceptance criteria:** refresh/offline/online/sign-in სცენარებში გეგმა არ იკარგება; ორ მოწყობილობას შორის ცვლილება წესის მიხედვით ერთიანდება; სხვის გეგმაზე წვდომა ნებართვის გარეშე შეუძლებელია.

## ACC-02 — itinerary version history და restore

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: ACC-01

**მიზანი:** მომხმარებელმა შეცდომით წაშლილი ან შეცვლილი გეგმა აღადგინოს.

**სამუშაო:** snapshot strategy; meaningful versions; restore preview; retention; template-origin tracking.

**Acceptance criteria:** მინიმუმ ბოლო 10 მნიშვნელოვანი ვერსია ჩანს; restore ქმნის ახალ ვერსიას და ძველს არ შლის; storage limit კონტროლდება.

## OFF-01 — შერჩეული ტურის ოფლაინ რეჟიმი

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: PERF-02, ACC-01

**მიზანი:** მოგზაურობისას ინტერნეტის დაკარგვა არ არღვევს გეგმას.

**სამუშაო:** offline package — itinerary, summary POIs, thumbnails, emergency info, cached map extent/tiles თუ ლიცენზია იძლევა; storage estimate; download/delete/status; stale warning.

**Acceptance criteria:** airplane mode-ში იხსნება არჩეული გეგმა და ძირითადი დეტალები; მომხმარებელი ხედავს მოცულობასა და download progress-ს; traffic/weather მკაფიოდ ინიშნება როგორც offline/stale.

