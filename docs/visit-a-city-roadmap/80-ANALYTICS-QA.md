# ანალიტიკა, QA და ოპერაციები

## DATA-01 — პროდუქტის ანალიტიკა და funnel

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0

**მიზანი:** გადაწყვეტილებები დაეყრდნოს რეალურ გამოყენებას.

**სამუშაო:** privacy-safe events: planner_opened, origin_selected, plan_generated, place_added/removed, template_applied, save/share/fork, rental_shown/requested, errors, performance; consent; dashboards.

**Acceptance criteria:** funnel ჩანს ენით/device/source-ით პირადი მონაცემის გარეშე; duplicate events არ არის; opt-out მუშაობს; event dictionary დოკუმენტირებულია.

## QA-01 — end-to-end კრიტიკული სცენარები

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0

**მიზანი:** ყველაზე მნიშვნელოვანი მომხმარებლის გზები ყოველი რელიზის წინ ავტომატურად შემოწმდეს.

**სცენარები:** guest plan; Kutaisi Airport origin; 5-hour plan; remove/add fit place; standard tour apply/edit; save/sign-in/sync; share/fork; booking popup; mobile tabs; offline reopen.

**Acceptance criteria:** ყველა P0 სცენარი CI-ში გადის; failure-ზე screenshot/log ინახება; flaky test rate <2%; production-like preview-ზე smoke suite არსებობს.

## QA-02 — კონტენტის ავტომატური ვალიდაცია

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: CNT-01

**მიზანი:** broken reference, duplicate slug, მცდარი coordinate ან არასრული publish build-მდე გაჩერდეს.

**სამუშაო:** schema; reference graph; Georgia bounds; route waypoint; image existence/dimensions; translations; price/time formats; source/license; report.

**Acceptance criteria:** თითო შეცდომა მიუთითებს ფაილსა და ველს; archive reference წესები მუშაობს; validator local და CI გარემოში ერთნაირ შედეგს იძლევა.

## OPS-01 — ოპერაციული runbook და rollback

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P1  
დამოკიდებულება: FND-03, QA-01

**მიზანი:** რელიზი, rollback და ინციდენტის მართვა არ იყოს ერთი ადამიანის მეხსიერებაზე დამოკიდებული.

**სამუშაო:** preview → approval → deploy; health checks; rollback; DNS boundaries; provider credentials; Firebase/traffic/weather degradation; owner/escalation; post-release checks.

**Acceptance criteria:** სხვა უფლებამოსილი შემსრულებელი runbook-ით აკეთებს preview-ს; rollback დრო გაზომილია; secrets დოკუმენტში არ წერია; incident severity და კომუნიკაცია განსაზღვრულია.

