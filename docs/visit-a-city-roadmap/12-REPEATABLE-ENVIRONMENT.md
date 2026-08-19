# განმეორებადი სამუშაო გარემო

ეს დოკუმენტი ადგენს ერთსა და იმავე გარემოს Codex-ისთვის, Claude Code-ისთვის,
დეველოპერის კომპიუტერისთვის და CI/build სერვისებისთვის.

## ოფიციალური ვერსიები

- Python: **3.12.13** (`.python-version`)
- PyYAML: **6.0.3**
- Markdown: **3.10.3**
- დამატებითი მედია ხელსაწყოები: Pillow **12.3.0**, Playwright **1.55.0**

`requirements.txt` არის საიტის canonical build-ის მინიმალური, ზუსტად
ვერსირებული dependency სია. `requirements-tools.txt` დამატებით გამოიყენება
ფოტოების აუდიტის, დამუშავებისა და OG სურათების გენერაციისას. ტესტებს ცალკე
პაკეტი არ სჭირდება — ისინი Python-ის ჩაშენებულ `unittest`-ს იყენებს.

## ახალი გარემოს მომზადება

Python 3.12.13-ის დაყენების შემდეგ პროექტის root-ში:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\scripts\setup_environment.ps1 -Python .\.venv\Scripts\python.exe
```

მედია ხელსაწყოებიც თუ საჭიროა:

```powershell
.\scripts\setup_environment.ps1 -WithTools -Python .\.venv\Scripts\python.exe
.\.venv\Scripts\python.exe -m playwright install chromium
```

macOS/Linux-ზე ეკვივალენტური ნაბიჯებია `python3.12 -m venv .venv`,
`source .venv/bin/activate` და `python -m pip install -r requirements.txt`.

## სრული ადგილობრივი შემოწმება

```powershell
python scripts/check_environment.py
python -m unittest discover -s tests -v
python build.py --validate-only
python build.py dist
python scripts/check_internal_links.py dist
```

გარემოს შემმოწმებელი განზრახ აჩერებს პროცესს, თუ Python-ის minor ვერსია ან
რომელიმე პაკეტის ვერსია ოფიციალურ ჩანაწერს არ ემთხვევა.

## საიდუმლო მონაცემების წესი

- პაროლები, OAuth client secrets, private keys და service-account JSON ფაილები
  repository-ში არ ინახება.
- ისინი თავსდება მხოლოდ hosting/CI-ის environment variables ან შესაბამისი
  სერვისის დაცულ configuration-ში.
- ბრაუზერში გამოყენებული Firebase client configuration საჯარო იდენტიფიკატორია;
  უსაფრთხოება მაინც უნდა უზრუნველყოს Firebase-ის authorized domains-მა და
  Firestore/Storage-ის წესებმა.
- `.env`, `.env.*`, service-account და private-key ფაილები `.gitignore`-ით
  იბლოკება; მხოლოდ `.env.example` შეიძლება იყოს ცარიელი ნიმუში.

## ვერსიის შეცვლის წესი

Dependency-ის განახლება ხდება ცალკე ცვლილებად: შეიცვალოს ზუსტი pin, გაეშვას
ტესტები, validation, სრული build და link check. შემოწმების გარეშე მხოლოდ
`>=` დიაპაზონის დამატება დაუშვებელია, რადგან სხვადასხვა გარემომ შეიძლება
სხვადასხვა შედეგი ააწყოს.
