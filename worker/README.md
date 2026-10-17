# RentUp AI — სერვერული ნაწილი (Cloudflare Worker)

საიტზე ჩატი ამ პატარა სერვერს ელაპარაკება, ის კი Claude-ს. API-გასაღები მხოლოდ
აქ ინახება, საიტის კოდში არასდროს. ჩატი არაფერს იმახსოვრებს და არ ინახავს.

## ერთჯერადი გაშვება (მფლობელი, ~10 წუთი)

ყველა ბრძანება ამ საქაღალდოდან (`worker/`), Windows-ის Terminal-ში.

1. **Anthropic API გასაღები** — <https://console.anthropic.com> → API Keys →
   Create Key. დააყენეთ თვიური ლიმიტი (Settings → Limits), მაგალითად $20.
   ეს ცალკე ანგარიშია; Claude-ის პირადი გამოწერა (Pro/Max) საიტს ვერ ამუშავებს.
2. **Cloudflare ანგარიში** — <https://dash.cloudflare.com/sign-up> (უფასო).
3. შესვლა ბრაუზერით:

       npx wrangler login

4. გასაღების ჩაწერა (ბრძანება მოგთხოვთ, ჩასვით და Enter — ეკრანზე არ ჩანს):

       npx wrangler secret put ANTHROPIC_API_KEY

5. გაშვება:

       npx wrangler deploy

   ბოლოს დაწერს მისამართს, მაგ. `https://rentup-ai.<თქვენი-სახელი>.workers.dev`.

6. ეს მისამართი ჩაწერეთ `content/settings/site.yml`-ში:

       ai_assistant:
         endpoint: https://rentup-ai.<თქვენი-სახელი>.workers.dev

   და გამოაქვეყნეთ საიტი (PUSH.bat → Actions → Run workflow ✓ Deploy).
   სანამ `endpoint` ცარიელია, ჩატი საიტზე არ ჩანს.

შემოწმება: `https://rentup-ai.<...>.workers.dev/health` უნდა დააბრუნოს `{"ok":true,...}`.

## ხარჯი

Claude Haiku 5.5: $0.10 / მილიონი შემავალი ტოკენი, $0.50 / მილიონი გამავალი.
ერთი პასუხი ≈ 4–6 ათასი ტოკენი ≈ $0.001–0.002. 1 000 საუბარი თვეში ≈ $5–10.
Cloudflare: 100 000 მოთხოვნა დღეში უფასოა.

## დაცვა

- მხოლოდ rentup.ge-დან იღებს მოთხოვნას (CORS).
- 30 მოთხოვნა წუთში ერთი IP-დან, 12 სვლა საუბარში, 1 000 სიმბოლო შეტყობინებაში.
- ფაქტები მხოლოდ `assets/ai-catalog.<ენა>.json`-იდან (content/-დან იგება);
  ადგილი, ფასი ან წესი, რომელიც იქ არ არის, პასუხში ვერ მოხვდება.

## დეველოპერისთვის

    npm test                 # node --test, Claude-ის გარეშე (MOCK)
    npm run fixtures         # ტესტის კატალოგი content/-იდან
    MOCK=1 npx wrangler dev  # ლოკალურად, გასაღების გარეშე

`src/planner.js` — დღის აწყობის მათემატიკა (ტესტებით), `src/prompt.js` — ინსტრუქცია
და ხელსაწყოები, `src/index.js` — HTTP და აგენტის ციკლი, `src/mock.js` — მოდელის
ჩამნაცვლებელი ტესტებისთვის.
