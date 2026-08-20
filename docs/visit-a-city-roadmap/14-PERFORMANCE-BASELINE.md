# PERF-01 — სიჩქარის საბაზისო გაზომვა და ბიუჯეტი

სტატუსი: **დასრულდა**  
გაზომვის თარიღი: 2026-08-20  
გაზომილი build: `dist-perf01-baseline`

## მიზანი

ამ ეტაპზე საიტის სისწრაფე პირველად გაიზომა განმეორებადი წესით. შედეგი გვაძლევს
საწყის ნიშნულს, რომელთანაც შევადარებთ `PERF-02` და `PERF-03` ოპტიმიზაციებს.

## რას ვზომავთ

- **Shell usable** — როდის ჩანს გვერდის ძირითადი შინაარსი და კონტროლები;
- **FCP** — როდის დახატა ბრაუზერმა პირველი ხილული შინაარსი;
- **Local map shell ready** — როდის მზადაა რუკის ადგილობრივი კონტეინერი;
- **Horizontal overflow** — ხომ არ მოითხოვს გვერდი გვერდულად გადაადგილებას;
- საწყისი HTML, CSS, JavaScript და დაუყოვნებლივ ჩატვირთული სურათების მოცულობა;
- ინდივიდუალური მძიმე ფაილების რაოდენობა.

`Local map shell ready` არ ნიშნავს, რომ TomTom/OSM ფილები, traffic ან weather API
უკვე დასრულებულია. გარე სერვისები baseline-ში შეგნებულად იბლოკება, რათა შედეგი
განმეორებადი იყოს და მესამე მხარის დროებითი სიჩქარე არ აირიოს ჩვენს კოდში.

## გარემო და სცენარები

- local HTTP server და Microsoft Edge headless;
- desktop cold load;
- mobile cold load: 150 ms RTT, 1.64 Mbps download, 768 Kbps upload, CPU ×4;
- mobile warm load;
- გვერდები: მთავარი, რუკა, დამგეგმავი და პირადი გვერდი;
- თითო სცენარი შესრულდა სამჯერ და ანგარიშში გამოიყენება p75.

## მიღების სამიზნეები

| საზომი | სამიზნე |
|---|---:|
| p75 shell usable | ≤ 3,000 ms |
| p75 local map shell, shell-ის შემდეგ | ≤ 2,000 ms |
| horizontal overflow | 0 px |
| საწყისი HTML | ≤ 256 KB |
| საწყისი CSS | ≤ 160 KB |
| საწყისი JavaScript | ≤ 820 KB |
| სრული ადგილობრივი საწყისი payload | ≤ 1.1 MB |
| ინდივიდუალური სურათი | ≤ 300 KB |

სამიზნეების machine-readable წყაროა
[`performance-budget.json`](../../performance-budget.json).

## შედეგის შეჯამება

- ყველა 12 ბრაუზერული სცენარი shell/map/overflow სამიზნეებში ჩაეტია;
- mobile cold shell p75: 380–995 ms;
- mobile cold FCP p75: 2,424–3,396 ms — ცალკე გაუმჯობესების ნიშანია;
- map shell-ის დამატებითი დრო: 0–153 ms;
- არც ერთ გაზომილ გვერდზე horizontal overflow არ დაფიქსირდა;
- blocking JavaScript request არ დაფიქსირდა;
- მთავარი გვერდის საწყისი local payload არის დაახლოებით 1.5 MB და ბიუჯეტს
  აჭარბებს;
- 111 ინდივიდუალური asset აჭარბებს მისთვის განსაზღვრულ ზღვარს;
- ყველაზე მძიმე ფაილებია დიდი background PNG-ები, logo-ს დუბლირებული ვარიანტები
  და რამდენიმე 600–900 KB ფოტო.

სრული ცხრილები და კონკრეტული მძიმე ფაილები ინახება
[`reports/performance-baseline-2026-08-20.md`](../../reports/performance-baseline-2026-08-20.md)-ში,
ხოლო ნედლი მონაცემები — იმავე სახელის `.json` ფაილში.

## როგორ განმეორდეს გაზომვა

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe build.py dist-perf01-baseline
.\.venv\Scripts\python.exe scripts\audit_performance.py `
  --dist dist-perf01-baseline `
  --report reports\performance-baseline-2026-08-20.md `
  --runs 3
```

## გადაწყვეტილებები

1. `PERF-02` პირველ რიგში გაყოფს რუკისა და ადგილების მონაცემებს რეგიონულ ან
   viewport-ზე მოთხოვნილ ნაწილებად.
2. `PERF-03` შეამცირებს დიდ ფოტოებს/background-ებს, მოაშორებს logo-ს ზედმეტ
   ვარიანტებს და დაამატებს responsive/lazy media-სა და სწორ cache-ს.
3. რეალურ მომხმარებლებთან tile/API/map-ready და p75 Core Web Vitals გაიზომება
   `DATA-01` ეტაპზე; ეს local baseline მათ შემცვლელად არ ითვლება.
4. ყოველი ოპტიმიზაციის შემდეგ იგივე აუდიტი უნდა განმეორდეს და შედეგი ამ
   baseline-ს შეედაროს.

## დასრულების მტკიცებულება

- ავტომატური აუდიტის ინსტრუმენტი: `scripts/audit_performance.py`;
- ბიუჯეტი: `performance-budget.json`;
- unit tests: `tests/test_performance_audit.py`;
- Markdown და JSON baseline ანგარიშები `reports/`-ში;
- ოთხივე ძირითადი გვერდის desktop/mobile cold/warm გაზომვა;
- payload-ისა და მძიმე asset-ების სია შემდგომი დავალებებისთვის.
