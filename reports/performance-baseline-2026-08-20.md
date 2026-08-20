# PERF-01 — performance baseline

- თარიღი: 2026-08-20
- build: `dist-perf01-baseline`
- გარემო: local HTTP + Microsoft Edge headless
- mobile profile: Fast 4G (150 ms RTT, 1.64 Mbps download, 768 Kbps upload, CPU ×4)
- გარე სერვისები (fonts, Firebase, map tiles, traffic/weather API) დაბლოკილია, რათა source bundle-ის baseline განმეორებადი იყოს.

## სამიზნეები

- p75 shell usable: ≤ 3000 ms
- p75 map-ready shell-ის შემდეგ: ≤ 2000 ms
- horizontal overflow: 0 px

## ბრაუზერის შედეგები

| სცენარი | გვერდი | p75 shell | p75 FCP | p75 map დამატებით | მაქს. overflow | შედეგი |
|---|---|---:|---:|---:|---:|---|
| desktop-cold | homepage | 161 ms | 192 ms | 0 ms | 0px | PASS |
| desktop-cold | map | 108 ms | 128 ms | 0 ms | 0px | PASS |
| desktop-cold | planner | 89 ms | 112 ms | 0 ms | 0px | PASS |
| desktop-cold | account | 54 ms | 80 ms | — | 0px | PASS |
| mobile-cold | homepage | 955 ms | 3384 ms | 144 ms | 0px | PASS |
| mobile-cold | map | 941 ms | 3288 ms | 134 ms | 0px | PASS |
| mobile-cold | planner | 852 ms | 3400 ms | 117 ms | 0px | PASS |
| mobile-cold | account | 398 ms | 2368 ms | — | 0px | PASS |
| mobile-warm | homepage | 865 ms | 3036 ms | 141 ms | 0px | PASS |
| mobile-warm | map | 934 ms | 3132 ms | 145 ms | 0px | PASS |
| mobile-warm | planner | 925 ms | 3336 ms | 83 ms | 0px | PASS |
| mobile-warm | account | 308 ms | 2332 ms | — | 0px | PASS |

## საწყისი payload

| გვერდი | HTML | CSS | JS | eager images | ჯამი | blocking JS |
|---|---:|---:|---:|---:|---:|---:|
| `index.html` | 132.7 KB | 157.1 KB | 726.9 KB | 518.3 KB | 1.5 MB | 0 |
| `map/index.html` | 999.0 B | 0.0 B | 0.0 B | 0.0 B | 999.0 B | 0 |
| `account/index.html` | 14.9 KB | 142.6 KB | 79.5 KB | 518.3 KB | 755.3 KB | 0 |

## ყველაზე მძიმე asset-ები და ბიუჯეტი

| asset | ზომა | ბიუჯეტი | შედეგი |
|---|---:|---:|---|
| `assets/georgia-id-security-bg.png` | 2.5 MB | 300.0 KB | OVER |
| `assets/georgian-heritage-watermark.png` | 1.7 MB | 300.0 KB | OVER |
| `assets/do-logo-modern.png` | 1023.8 KB | 300.0 KB | OVER |
| `assets/do-logo.png` | 987.7 KB | 300.0 KB | OVER |
| `assets/do-logo-premium.png` | 920.5 KB | 300.0 KB | OVER |
| `assets/photos/armaztsikhe-bagineti.webp` | 904.5 KB | 300.0 KB | OVER |
| `assets/photos/armaztsikhe-bagineti-4.webp` | 895.6 KB | 300.0 KB | OVER |
| `assets/photos/mtatsminda-pantheon-4.webp` | 891.8 KB | 300.0 KB | OVER |
| `assets/photos/ozurgeti.webp` | 807.4 KB | 300.0 KB | OVER |
| `assets/photos/lagodekhi-protected-areas.webp` | 764.4 KB | 300.0 KB | OVER |
| `assets/photos/sameba-jikheti-monastery-3.jpg` | 748.4 KB | 300.0 KB | OVER |
| `assets/do-logo-transparent.png` | 744.6 KB | 300.0 KB | OVER |
| `assets/do-logo-clean.png` | 740.8 KB | 300.0 KB | OVER |
| `assets/photos/grakliani-hill.webp` | 719.7 KB | 300.0 KB | OVER |
| `assets/photos/betania-monastery-2.webp` | 713.1 KB | 300.0 KB | OVER |
| `assets/photos/tbilisi-botanical-garden.webp` | 699.3 KB | 300.0 KB | OVER |
| `assets/photos/tbilisi-botanical-garden-4.webp` | 696.3 KB | 300.0 KB | OVER |
| `assets/photos/bateti-lake-2.webp` | 685.7 KB | 300.0 KB | OVER |
| `assets/photos/abudelauri-lakes-2.webp` | 682.7 KB | 300.0 KB | OVER |
| `assets/photos/abudelauri-lakes-1.webp` | 672.1 KB | 300.0 KB | OVER |
| `assets/photos/shekvetili-black-sea-arena-4.webp` | 654.0 KB | 300.0 KB | OVER |
| `assets/photos/sameba-jikheti-monastery-summer.jpg` | 647.8 KB | 300.0 KB | OVER |
| `assets/photos/chokhatauri-1.webp` | 643.9 KB | 300.0 KB | OVER |
| `assets/photos/artsivi-eagle-gorge-1.webp` | 634.4 KB | 300.0 KB | OVER |
| `assets/photos/tsaishi-cathedral-4.webp` | 634.4 KB | 300.0 KB | OVER |

## დასკვნა და შემდეგი ნაბიჯი

- საწყისი გვერდის ბიუჯეტი: HTML ≤ 250.0 KB, CSS ≤ 156.2 KB, JS ≤ 800.8 KB, სრული local payload ≤ 1.0 MB.
- ინდივიდუალური asset-ის ბიუჯეტი დოკუმენტირებულია `performance-budget.json`-ში; ამ baseline-ში 111 asset აჭარბებს შესაბამის ზღვარს.
- PERF-02-ში პირველ რიგში უნდა გაიყოს `travel-*.js` რეგიონულ/viewport chunk-ებად და რუკის payload ჩაიტვირთოს მოთხოვნის მიხედვით.
- PERF-03-ში უნდა შემცირდეს დიდი PNG/WebP/JPG ფაილები, logo/background variants და დაემატოს ზომაზე მორგებული responsive media/cache.
- გარე provider-ების ცალკე production RUM საჭიროა DATA-01-ში; ეს ანგარიში შეგნებულად ზომავს კონტროლირებად source baseline-ს.

## ნედლი შედეგები

ბრაუზერის თითოეული გაშვების მონაცემები ინახება იმავე სახელის `.json` ფაილში.
