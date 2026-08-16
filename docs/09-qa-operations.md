# ტესტირება, გამოქვეყნება და აღდგენა

## ადგილობრივი შემოწმება

1. content validation;
2. Python და JavaScript syntax;
3. unit/content tests;
4. სრული generated-site build;
5. sitemap, OG, JSON-LD, სურათები და შიდა ბმულები;
6. desktop/mobile smoke test;
7. strict production build.

Strict build აჩერებს placeholder კონტაქტებს, სოციალურ ბმულებს და მთავარი ფოტოს გარეშე გამოქვეყნებულ მანქანებს. მიმდინარე რეალური მფლობელის მონაცემების არქონის გამო production gate განზრახ დაკეტილია.

## Windows: build-ის კონსოლის კოდირება

`build.py` დასასრულს ბეჭდავს `✔` სიმბოლოს. Windows-ის ნაგულისხმევ cp1252 კონსოლზე ეს იძლევა `UnicodeEncodeError`-ს **მას შემდეგ, რაც გვერდები უკვე დაგენერირდა** — build რეალურად წარმატებულია, მაგრამ exit code არასწორია. ყოველთვის გაუშვით:

```
PYTHONIOENCODING=utf-8 python build.py dist --strict
```

წინააღმდეგ შემთხვევაში CI ან სკრიპტი წარმატებულ build-ს ჩავარდნილად ჩათვლის.

## დოკუმენტაციის HTML

`docs/*.html` გენერირებულია და ხელით არ იცვლება. `docs/`-ში markdown-ის შეცვლის შემდეგ გაუშვით:

```
PYTHONIOENCODING=utf-8 python scripts/build_docs_html.py
```

## აღდგენა და git

Git commit არის აღდგენის ძირითადი წერტილი. წაშლას არქივირება სჯობს. deploy/push კეთდება მხოლოდ ლოკალური მიღებისა და მფლობელის მონაცემების შევსების შემდეგ.

**merge-ის დაუსრულებელ მდგომარეობაში მუშაობა აკრძალულია.** თუ `git status` აჩვენებს „unmerged paths", კონფლიქტის ტექსტურად გასწორება საკმარისი არ არის — საჭიროა `git add` და commit. სანამ ეს არ გაკეთდება, აღდგენის წერტილი არ არსებობს და `git merge --abort` გაანადგურებს გასწორებულ ფაილებს.

