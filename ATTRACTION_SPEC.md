# Attraction file spec — content/attractions/<slug>.yml

Every file is UTF-8 YAML with EXACTLY this key order. Copy the shape from
`content/attractions/ananuri-fortress.yml` (read it first — it is the reference).

```yaml
region: <one of: tbilisi | shida-kartli | kvemo-kartli | mtskheta-mtianeti |
                kakheti | samtskhe-javakheti | imereti | racha-lechkhumi |
                samegrelo-zemo-svaneti | guria | adjara>
type: <one of: archaeology beach canyon cave fortress lake monastery mountain
               museum nature ski spa town waterfall winery>
lat: 41.1234          # 4 decimals, must be inside Georgia
lon: 44.1234
elevation: 830        # metres, integer
unesco: false
featured: false       # true for at most 2 places per region
order: 30             # integer, any value 10..90
image: ''
gallery: []
visit_hours: '1'      # '0.5' '1' '1.5' '2' '3' '4' '6' — realistic time ON SITE
best_season: <all | may-october | june-september | december-march>
open_year_round: true
entry_fee: free       # 'free' or e.g. '15 ₾' / '5 ₾'
distance_tbilisi_km: 70          # integer, by ROAD not straight line
drive_time_tbilisi: '1:20'       # 'H:MM'
road: <paved | mostly_paved | gravel | 4x4_only>
car_category: <economy | suv | offroad>
nearby:                # 2–4 slugs that really exist in content/attractions/
- some-existing-slug
ka: {name, short, body, tip, route}
en: {…}
ru: {…}
fa: {…}
he: {…}
ar: {…}
```

## The six language blocks

Each of `ka en ru fa he ar` has the same five fields:

- **name** — the place name in that language.
- **short** — ONE sentence, 12–25 words. Ends with a full stop.
- **body** — 280–420 words of real, specific, readable description. This is the
  main text a visitor reads. It must contain concrete facts: century, who built
  it, what survives, what you actually see, why it matters, how the site
  changes with season or light. Markdown allowed: `**bold**` for the opening
  clause, and a bulleted list where a place genuinely has separate parts.
  Separate paragraphs with a BLANK LINE.
- **tip** — 60–110 words of practical advice: how long it really takes, stairs
  or steep ground, dress code, toilets, parking, food nearby, winter/summer
  caveats, whether a guide or booking is needed.
- **route** — 60–110 words: the driving route from Tbilisi (road name/number
  where you are sure), distance, time, road surface and condition, where to
  refuel, where to park, and which car category is enough.

## Hard rules

1. **Only real places.** If you are not certain a place exists and roughly
   where it is, leave it out. Never invent a monastery, a canyon or a museum.
2. **Coordinates must be right to ~2 km.** They are validated against a
   Georgia bounding box AND against `distance_tbilisi_km`; a file that fails
   validation is deleted.
3. `distance_tbilisi_km` must be plausible for the road route — always LONGER
   than the straight-line distance, typically 1.2×–2.5× depending on terrain.
4. Do not copy sentences between the six languages mechanically — write each
   one so it reads naturally. Same facts, native phrasing.
5. Persian, Hebrew and Arabic are right-to-left; write plain text, no
   directional marks, no Latin transliteration in brackets.
6. No prices for tours, no phone numbers, no opening hours that change — those
   go stale. `entry_fee` is the only money figure.
7. `nearby` must reference slugs that exist. Run
   `ls content/attractions/` to check before writing.
8. Slug: lowercase ASCII, hyphens, descriptive, e.g. `tsromi-church`,
   `dzveli-shuamta`, `okrostsqali-gorge`.

## Writing quality

The reference file `ananuri-fortress.yml` sets the bar. Aim for a well-edited
guidebook: specific, calm, no marketing adjectives, no "breathtaking",
no "hidden gem", no exclamation marks. Tell the reader something they did not
know. If a place is often disappointing, say what is worth it and what is not.

## How to write the files

Write each file with the Write tool, one file per attraction. Use a literal
block or folded scalars exactly like the reference file. Verify at the end:

```
python -c "import yaml,glob;[yaml.safe_load(open(f,encoding='utf-8')) for f in glob.glob('content/attractions/*.yml')];print('yaml ok')"
```

Report back only: the list of slugs you created, and anything you skipped and why.
