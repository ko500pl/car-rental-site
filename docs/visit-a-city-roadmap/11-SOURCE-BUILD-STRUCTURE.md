# ოფიციალური source/build სტრუქტურა

სტატუსი: **დასრულდა**  
დავალება: `FND-01`  
განახლებულია: 2026-08-19

## ერთი ოფიციალური პროექტი

აქტიური repository root არის `C:\Projects\car-rental-site\car-rental-site`.
ყველა build, test და content ცვლილება ამ დირექტორიიდან სრულდება. მის გარეთ ან
მის შიგნით ჩადგმული სხვა `car-rental-site` ასლი ოფიციალური წყარო არ არის.

## რა არის source of truth

| ნაწილი | ოფიციალური წყარო | დანიშნულება |
|---|---|---|
| კონტენტი | `content/` | ავტომობილები, ადგილები, ტურები, გვერდები და პარამეტრები |
| გენერატორის მოდულები | `sitegen/` | ვალიდაცია და გენერაციის დამხმარე ლოგიკა |
| ძირითადი გენერატორი | `build.py`, `theme.py`, `yaml_io.py` | HTML/data/assets build |
| ბრაუზერის კოდი და მედია | `static/` | JavaScript, სურათები, PWA და ჩამოსატვირთი ფაილები |
| CMS | `admin/` | ადმინისტრატორის ინტერფეისი და კონფიგურაცია |
| მობილური აპი | `mobile/` | Android/iOS/PWA-ს მობილური პროექტი |
| ტესტები | `tests/` | ავტომატური შემოწმებები |

გენერირებულ HTML-ში ხელით ცვლილება დაუშვებელია: შემდეგი build მას გადაწერს.

## ერთადერთი build output

ერთადერთი ოფიციალური output არის `dist/`.

```powershell
python build.py --validate-only
python build.py dist
python -m http.server 8000 --directory dist
```

| გარემო | build | publish |
|---|---|---|
| Render | `python3 build.py dist` | `./dist` |
| Netlify | `python3 build.py dist` | `dist` |
| GitHub Pages | `python build.py dist` | `dist` artifact |

## ავტომატური კონტროლი

`python scripts/check_project_layout.py` ამოწმებს აუცილებელ source ნაწილებს,
სამივე deploy კონფიგურაციას და Git-ში გენერირებული output-ის არყოფნას. სკრიპტი
არაფერს ცვლის ან შლის.

`python scripts/verify_repeatable_build.py` საიტს ორჯერ აგებს და ყველა ფაილის
SHA-256 hash-ს ადარებს. ერთსა და იმავე დღესა და source-ზე შედეგი იდენტური უნდა
იყოს. გვერდებში მიმდინარე თარიღი/წელი გენერირდება, ამიტომ სხვადასხვა დღეს
შექმნილი build-ის hash შეიძლება განსხვავდებოდეს.

## ძველი არტეფაქტების პოლიტიკა

აღმოჩენილი `dist-*` დირექტორიები, root-ის `*.zip` არქივები და ჩადგმული
`car-rental-site/` ასლი წინა ტესტების/რელიზების ლოკალური არტეფაქტებია. ისინი
Git-ში tracked არ არის, `.gitignore`-ით გამორიცხულია, deploy-ში არ გამოიყენება
და canonical build-ზე გავლენა არ აქვს.

ეს ფაილები ამ დავალებაში არ წაშლილა. მათი მომავალი გასუფთავება შეიძლება მხოლოდ
ზუსტი სიისა და ზომის შემოწმების შემდეგ, მომხმარებლის ცალკე თანხმობით.

## შესრულების მტკიცებულება

- `python scripts/check_project_layout.py`
- `python build.py --validate-only`
- `python scripts/verify_repeatable_build.py`
- `python -m unittest discover -s tests -v`

დასრულების ჩანაწერი ინახება [საფუძვლის სამუშაო დოკუმენტში](10-FOUNDATION.md).
