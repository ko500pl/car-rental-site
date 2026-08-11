# ანგარიშების ჩართვა — Firebase (15 წუთი)

საიტი ისე მუშაობს, თითქოს ავტორიზაცია არ არსებობს, სანამ `content/settings/auth.yml`-ში
`enabled: true` არ დაწერეთ და გასაღებები არ ჩასვით. ანუ ჯერ მშვიდად შეგიძლიათ ყველაფერი
გამართოთ და მერე ჩართოთ.

---

## 1. პროექტის შექმნა

1. <https://console.firebase.google.com> → **Add project** → სახელი: `fleet-house`
2. Google Analytics — შეგიძლიათ გამორთოთ, არ არის საჭირო
3. მარცხნივ **Build → Authentication → Get started**
   - **Email/Password** → Enable
   - **Google** → Enable → აირჩიეთ support email
4. **Build → Firestore Database → Create database** → **Production mode** → რეგიონი: `eur3` (ევროპა)

> რეგიონი ევროპაში აირჩიეთ — მომხმარებელთა მონაცემები ევროპაში დარჩება,
> რაც GDPR-ის თვალსაზრისით ბევრად მარტივია.

## 2. ვებ-აპლიკაციის დამატება

**Project settings** (ჭანჭიკი) → **Your apps** → **Web** (`</>`) → სახელი `fleet-house-web`
→ Register app. მიიღებთ ასეთ ბლოკს:

```js
const firebaseConfig = {
  apiKey: "AIza…",
  authDomain: "fleet-house.firebaseapp.com",
  projectId: "fleet-house",
  storageBucket: "fleet-house.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

ეს მნიშვნელობები ჩასვით `content/settings/auth.yml`-ში და `enabled` გახადეთ `true`.

> **ეს გასაღებები საჯაროა და ასე უნდა იყოს.** Firebase-ის უსაფრთხოება პაროლზე კი არა,
> ქვემოთ მოცემულ წესებზეა დამოკიდებული. ისინი ბრაუზერში მაინც ჩანს.

## 3. დომენის დაშვება

**Authentication → Settings → Authorized domains → Add domain**

დაამატეთ:
- `subtle-naiad-c2db5d.netlify.app` (ან თქვენი Netlify-ის მისამართი)
- თქვენი დომენი, როცა მიაბამთ — მაგ. `fleethouse.ge` და `www.fleethouse.ge`

ამის გარეშე Google-ით შესვლა არ იმუშავებს.

## 4. Firestore-ის წესები — აუცილებელი

**Firestore Database → Rules** → ჩასვით ზუსტად ეს და **Publish**:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /trips/{tripId} {
      // წაკითხვა და შეცვლა შეუძლია მხოლოდ იმ მომხმარებელს, ვისიც არის ჩანაწერი
      allow read, update, delete: if request.auth != null
                                  && resource.data.uid == request.auth.uid;

      // შექმნისას uid უნდა ემთხვეოდეს შემსვლელს და ველები შეზღუდულია
      allow create: if request.auth != null
                    && request.resource.data.uid == request.auth.uid
                    && request.resource.data.keys().hasOnly(
                         ['uid','title','date','days','stops','km','url','status','created'])
                    && request.resource.data.title is string
                    && request.resource.data.title.size() <= 120
                    && request.resource.data.stops.size() <= 200;
    }

    // ყველაფერი დანარჩენი — აკრძალული
    match /{document=**} { allow read, write: if false; }
  }
}
```

ეს წესები ნიშნავს: **ერთ მომხმარებელს მეორის მარშრუტები ვერანაირად ვერ ნახავს.**

## 5. ლიმიტები (უფასო Spark გეგმა)

| | უფასო ლიმიტი |
|---|---|
| Firestore წაკითხვა | 50 000 / დღეში |
| Firestore ჩაწერა | 20 000 / დღეში |
| შენახული მონაცემები | 1 GB |
| ავტორიზაცია | შეუზღუდავი (email + Google) |

ერთი მარშრუტი ≈ 2 კბ. ანუ 1 GB ≈ ნახევარი მილიონი შენახული მარშრუტი.
ამ მასშტაბამდე ბევრი გაქვთ.

## 6. რაც იურიდიულად უნდა გააკეთოთ

ავტორიზაციის ჩართვა ნიშნავს, რომ პერსონალურ მონაცემებს ამუშავებთ. საჭიროა:

1. **კონფიდენციალურობის პოლიტიკა** — მოამზადეთ `content/pages/privacy.yml`-ის მიხედვით
   (პროექტი უკვე დაწერილია, იურისტმა უნდა შეამოწმოს)
2. **მომსახურების პირობები** — `content/pages/terms.yml`
3. **Google Cloud-ის DPA** — Firebase Console → Project settings → Privacy & security →
   მიიღეთ Data Processing Amendment
4. საქართველოს პერსონალურ მონაცემთა დაცვის სამსახურში რეგისტრაცია, თუ საჭიროა —
   ეს იურისტმა უნდა შეაფასოს

## 7. შემოწმება

1. `enabled: true` + გასაღებები → `PUSH.bat`
2. საიტზე ჰედერში გამოჩნდება **შესვლა**
3. შედით Google-ით → დაგეგმეთ მარშრუტი → **მარშრუტის შენახვა** → თარიღი და სახელი
4. **ჩემი გვერდი** → უნდა ჩანდეს დაგეგმილში
5. **შესრულებულად მონიშვნა** → გადავა „შესრულებულში"

თუ Google-ით შესვლა `auth/unauthorized-domain`-ს აბრუნებს — მე-3 ნაბიჯი გამოგრჩათ.
