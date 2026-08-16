# არქიტექტურა და build

## მიზანი

საიტი რჩება static-first სისტემად: YAML კონტენტი → Python გენერატორი → ცალკეული HTML გვერდები → ჰოსტინგი. React/Next.js ან მუდმივი ბიზნეს-ბაზა საჭირო არ არის.

## ძირითადი ნაწილები

- `content/` — ადმინისტრატორის მონაცემები;
- `admin/config.yml` — Decap CMS ფორმები;
- `build.py` — HTML, sitemap, JSON-LD და მონაცემთა პაკეტები;
- `static/` — Leaflet, ანგარიშები, მოთხოვნის ფორმები და დიზაინის რესურსები;
- `sitegen/validation.py` — გამოქვეყნებამდე ვალიდაცია;
- `tests/` — რეგრესიის ტესტები.

## ბრძანებები

`python build.py --validate-only` ამოწმებს მონაცემებს. `python build.py dist --strict` არის production gate და placeholder მონაცემებზე exit code 2-ით ჩერდება.

## დოკუმენტაცია build-ში

`build.py` `docs/*.html`-ს აკოპირებს `dist/docs/`-ში, ანუ დოკუმენტაცია პროდუქტთან ერთად ვრცელდება. markdown წყაროები repository-ში რჩება და არ იგზავნება.

ეს არის **შიდა გუნდის დოკუმენტაცია**: `robots.txt` მას კრძალავს (`Disallow: /docs/`), sitemap-ში არ შედის და `netlify.toml` აყენებს `X-Robots-Tag: noindex, nofollow`. მაგრამ **ბმულის მცოდნე ნებისმიერს შეუძლია წაკითხვა** — noindex არ არის წვდომის კონტროლი. თუ შიგთავსი კონფიდენციალურად ჩაითვლება, საჭიროა Netlify-ის პაროლით დაცვა ან `dist/docs/`-ის გამორთვა.

HTML-ის განახლება: `python scripts/build_docs_html.py`, შემდეგ build.

## უცვლელი პრინციპები

საჯარო URL-ები, ექვსი ენა, RTL, canonical/hreflang და სტატიკური SEO გვერდები შენარჩუნებულია. Firebase არასავალდებულოა და არ გამოიყენება გაქირავების მოთხოვნისთვის.

