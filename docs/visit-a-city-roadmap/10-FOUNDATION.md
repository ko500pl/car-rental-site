# საფუძველი, რელიზი და სიჩქარე

## FND-01 — ოფიციალური source/build სტრუქტურა

სტატუსი: **დასრულდა**  
პრიორიტეტი: P0  
დამოკიდებულება: —

**მიზანი:** აღარ არსებობდეს გაურკვევლობა, რომელი დირექტორიაა წყარო და რომელი output ქვეყნდება.

**სამუშაო:** დააფიქსირე აქტიური root; აღწერე source დირექტორიები; აირჩიე ერთი build output; დაამატე ძველი `dist-*` არტეფაქტების უსაფრთხო არქივაციის სია; გაასწორე build/deploy კონფიგურაცია; არ წაშალო ძველი ვერსიები ცალკე თანხმობის გარეშე.

**Acceptance criteria:** README-დან ერთი ბრძანებით იქმნება ერთი canonical output; deploy config მასზე მიუთითებს; source-ში ხელით გენერირებული ფაილები არ ირევა; ძველი outputs-ის გავლენა build-ზე ნულია.

**შემოწმება:** clean checkout simulation; build ორჯერ და ფაილების deterministic შედარება; broken link smoke test.

**შესრულების ჩანაწერი (2026-08-19):** ოფიციალურ root-ად დაფიქსირდა
`C:\Projects\car-rental-site\car-rental-site`; source და output წესები აღწერილია
[`11-SOURCE-BUILD-STRUCTURE.md`](11-SOURCE-BUILD-STRUCTURE.md)-ში. დამატებულია
read-only სტრუქტურის კონტროლი `scripts/check_project_layout.py` და ორმაგი build-ის
hash შედარება `scripts/verify_repeatable_build.py`. ძველი `dist-*`, ZIP და ჩადგმული
repository ასლები არ წაშლილა და deploy-ში არ მონაწილეობს.

**საბოლოო შემოწმება:**

- პროექტის სტრუქტურის კონტროლი — წარმატებული;
- კონტენტის წინასწარი ვალიდაცია — წარმატებული (დაფიქსირდა ცალკე კონტენტური
  გაფრთხილება: 17 გამოქვეყნებულ ავტომობილს მთავარი ფოტო არ აქვს);
- ავტომატური ტესტები — 26/26 წარმატებული;
- canonical build — წარმატებული, შეიქმნა 2,070 HTML გვერდი;
- 2,080 HTML ფაილის შიდა ბმულებისა და რესურსების smoke test — გატეხილი
  მისამართების გარეშე;
- ორმაგი build-ის შედარება — 4,631 ფაილი სრულად იდენტურია.

**შედეგი:** ერთი ოფიციალური source root, ერთი canonical `dist` output და ყველა
არსებული deploy workflow-ის ერთი build წესზე შეთანხმება დადასტურებულია.

## FND-02 — განმეორებადი გარემო და dependency lock

სტატუსი: **დასრულდა**  
პრიორიტეტი: P0  
დამოკიდებულება: FND-01

**მიზანი:** Codex-მა, Claude Code-მა და CI-მ ერთნაირი გარემოთი ააშენონ საიტი.

**სამუშაო:** Python/runtime ვერსიის დაფიქსირება; ყველა რეალური dependency-ის ჩამოწერა; lock ან ზუსტად ვერსირებული requirements; setup/check script; Markdown/PyYAML/test dependency-ების დაფიქსირება; secrets მხოლოდ environment/configured service-ში.

**Acceptance criteria:** ახალ გარემოში დოკუმენტირებული ნაბიჯებით სრულდება install, tests და build; missing dependency შეცდომა აღარ არის; საიდუმლო გასაღებები repo-ში არ ხვდება.

**შესრულების ჩანაწერი (2026-08-19):** Python დაფიქსირდა `3.12.13`-ზე
`.python-version`-ში, Netlify-სა და GitHub Actions-ში. ძირითადი build dependency-ები
ზუსტი ვერსიებით ჩაიკეტა `requirements.txt`-ში, ხოლო არჩევითი ვიზუალური/ბრაუზერის
ინსტრუმენტები — `requirements-tools.txt`-ში. დაემატა Windows-ის setup script,
გარემოს ავტომატური შემმოწმებელი და საიდუმლო მონაცემების შენახვის წესები.
სრული ინსტრუქციაა [`12-REPEATABLE-ENVIRONMENT.md`](12-REPEATABLE-ENVIRONMENT.md)-ში.

**საბოლოო შემოწმება:**

- სრულიად ახალ virtual environment-ში dependency install — წარმატებული;
- runtime და package-version კონტროლი — წარმატებული (Python 3.12.13);
- ავტომატური ტესტები — 26/26 წარმატებული;
- canonical build — წარმატებული, შეიქმნა 2,080 HTML გვერდი;
- 2,080 HTML გვერდის შიდა ბმულებისა და რესურსების შემოწმება — წარმატებული;
- repository secret-pattern შემოწმება — გავრცელებული private key/token ნიშნების გარეშე;
- strict publish რეჟიმი სწორად ბლოკავს არსებულ კონტენტურ პრობლემას: 17 მანქანას
  მთავარი ფოტო აკლია. ეს dependency-ის პრობლემა არ არის და ცალკე კონტენტის
  დავალებად რჩება.

**შედეგი:** Codex-ის, Claude Code-ისა და CI-ისთვის არსებობს ერთი დოკუმენტირებული,
ვერსირებული და ავტომატურად შემოწმებადი გარემო.

## FND-03 — CI test/build/release gate

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: FND-02

**მიზანი:** გატეხილი კონტენტი ან UI production-ში ვერ მოხვდეს.

**სამუშაო:** content validation; unit tests; build; HTML/link smoke tests; artifact summary; deploy ცალკე approval ნაბიჯად; failure-ის ადამიანური აღწერა.

**Acceptance criteria:** შეგნებულად გატეხილი reference, YAML და JS smoke test აჩერებს pipeline-ს; წარმატებულ pipeline-ს აქვს build artifact და მოკლე ანგარიში; deploy ავტომატურად არ ხდება approval-ის გარეშე.

## PERF-01 — performance baseline და ბიუჯეტი

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: FND-01

**მიზანი:** სისწრაფე გაიზომოს და აღარ შეფასდეს მხოლოდ ვიზუალური შეგრძნებით.

**სამუშაო:** homepage/map/planner/account გვერდების cold/warm load; mobile throttling; JS/CSS/image/data waterfall; first content, interactive, map-ready საზომები; asset budget.

**Acceptance criteria:** baseline ანგარიში ინახება `reports/`; განსაზღვრულია p75 სამიზნეები: shell usable ≤3 წმ, map-ready დამატებით ≤2 წმ, horizontal blocking request-ის გარეშე; ყოველი მთავარი bundle/asset budget დოკუმენტირებულია.

## PERF-02 — რუკის მონაცემების ნაწილობრივი ჩატვირთვა

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PERF-01

**მიზანი:** 267+ ადგილის სრული payload და მარკერები აღარ მომზადდეს ყველა გახსნაზე.

**სამუშაო:** მონაცემების რეგიონულ/viewport chunk-ებად დაყოფა; summary/detail payload განცალკევება; map move debounce; cache; request cancellation; cluster-ში მხოლოდ ხილული მონაცემები.

**Acceptance criteria:** პირველ ჩატვირთვაზე მოდის მხოლოდ საჭირო chunk; pan/zoom-ზე არ ჩანს duplicate marker; ძველი request ვერ ფარავს ახალ შედეგს; offline fallback ინარჩუნებს ბოლოს მიღებულ მონაცემს.

## PERF-03 — სურათები, APK და cache ოპტიმიზაცია

სტატუსი: **არ დაწყებულა**  
პრიორიტეტი: P0  
დამოკიდებულება: PERF-01

**მიზანი:** მძიმე მედია არ აფერხებდეს planner-ს.

**სამუშაო:** responsive image sizes; lazy loading; მთავარი thumbnail/detail gallery განცალკევება; duplicate logos/backgrounds; APK მხოლოდ download click-ზე; cache headers; compression და immutable filenames.

**Acceptance criteria:** above-the-fold-ში არ იტვირთება gallery/full-size/APK; broken image fallback არსებობს; ვიზუალური ხარისხი მიღებულია 360/768/1440 px-ზე; repeat visit მნიშვნელოვნად იყენებს cache-ს.
