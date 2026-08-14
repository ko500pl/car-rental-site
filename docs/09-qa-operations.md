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

Git commit არის აღდგენის ძირითადი წერტილი. წაშლას არქივირება სჯობს. deploy/push კეთდება მხოლოდ ლოკალური მიღებისა და მფლობელის მონაცემების შევსების შემდეგ.

