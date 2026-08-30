"""Replace known-mismatched attraction photos with exact, licensed Commons media.

The allow-list is intentionally manual.  Every title names the attraction itself;
the script never chooses a result from a fuzzy search.  It updates only the image,
gallery and image-credit fields and leaves all attraction copy untouched.
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps


API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "DriveOnAttractionPhotoRemediation/1.0 (https://rentup.ge)"
ALLOWED_LICENSE_MARKERS = ("CC BY", "CC0", "PUBLIC DOMAIN", "PDM")


# First file is the primary image; the following files form the gallery.
EXACT_MEDIA: dict[str, list[str]] = {
    "beshumi": [
        "File:ბეშუმი (29651276755).jpg",
    ],
    "goderdzi-pass": [
        "File:Goderdzi Pass (2025m).jpg",
        "File:Goderdzi Pass kz01.jpg",
        "File:Goderdzi Pass kz02.jpg",
        "File:Goderdzi Pass kz03.jpg",
    ],
    "khulo-cable-car-upper-adjara": [
        "File:Starting point of Khulo - Tago ropeway cable car.jpg",
        "File:Khulo, wiev from Tago Cableway Station.jpg",
        "File:Khulo main street Sh1.jpg",
    ],
    "batumi-botanical-garden": [
        "File:View of Batumi skyline from the Botanical Garden (cropped).jpg",
        "File:Batumi2025botanic-garden-view-to-batumi-2.jpg",
        "File:View of the Black Sea coast from Batumi Botanical Garden.jpg",
        "File:Batumi Botanical Garden.jpg",
    ],
    "sighnaghi": [
        "File:Panorama over Sighnaghi - Georgia (18157038140).jpg",
        "File:Panorama over Sighnaghi from Guesthouse Balcony - Sighnaghi - Georgia (18308941142).jpg",
        "File:St. George’s Church in Sighnaghi Panorama.jpg",
    ],
    "birtvisi-fortress": [
        "File:Birtvisi.jpg",
        "File:2024-01-07 Gate on the way to Birtvisi Fortress 1.jpg",
        "File:2024-01-07 Gate on the way to Birtvisi Fortress 2.jpg",
        "File:Birtvisi 20.jpg",
    ],
    "vardzia": [
        "File:Panorama Wardzia.jpg",
        "File:Vardezia (1).jpg",
        "File:Vardzia (5).jpg",
    ],
    "askana-fortress": [
        "File:Askana fortress.JPG",
        "File:Askana Fortress old photograph.jpg",
        "File:Askana Fortress by A. Gogiashvili.jpg",
    ],
    "atskuri-fortress": [
        "File:Atsquri fortress, Georgia 01.jpg",
        "File:Atsquri fortress, Georgia 03.jpg",
        "File:Atsquri fortress, Georgia 02.jpg",
        "File:Atsquri fortress, Georgia 06.jpg",
    ],
    "dashbashi-canyon": [
        "File:Dashbashi Canyon Natural Monument1.jpg",
        "File:Dashbashi Canyon Natural Monument2.jpg",
        "File:Dashbashi Canyon Natural Monument3.jpg",
        "File:Dashbashi Waterfall situated in the Dashbashi Canyon.jpg",
        "File:Dashbashi Canyon, Tsalka, Kvemo Kartli, Georgia.jpg",
    ],
    "juta-chaukhi": [
        "File:Chaukhi Mountain & Tina Lake, Juta Valley, Mtskheta-Mtianeti, Georgia.jpg",
        "File:Chaukhi Mountain, Mtskheta-Mtianeti, Georgia.jpg",
        "File:Juta Valley at Night, Mtskheta-Mtianeti, Georgia.jpg",
        "File:Khevi, Georgia — Mountainous Village Juta.jpg",
        "File:A view from the trail from Juta to Chaukhi Pass 2023-07-29-2.jpg",
    ],
    "ushguli": [
        "File:Ushguli, Georgia-3883095.jpg",
        "File:Ushguli village.JPG",
        "File:Ushguli Village, Svaneti.jpg",
        "File:Ushguli Village, Svaneti, view of Shkhara mountain.jpg",
        "File:Ushguli towers in Svaneti, Georgia.png",
    ],
    "shkhara-glacier": [
        "File:Shkhara Glacier.jpg",
        "File:Shkhara Mountain, view from Chubedishi Mountain.jpg",
    ],
    "chalaadi-glacier": [
        "File:Chalaadi Glacier and Mt Chatintau.jpg",
        "File:Chalaati Glacier, Samegrelo-Zemo Svaneti, Georgia.jpg",
        "File:Chalaati glacier, Georgia, June, 2018-1.jpg",
        "File:On the trail to Chalaadi Glacier, Samegrelo-Zemo Svaneti, Georgia.jpg",
    ],
    "batumi-boulevard-old-town": [
        "File:Batumi Boulevard From Above.jpg",
        "File:Batumi Boulevard Alley.jpg",
        "File:Batumi Boulevard Bycicle Path.jpg",
        "File:Batumi Boulevard Colonnades.jpg",
    ],
    "khada-valley": [
        "File:Khada gorge as seen from Mt Lomisi (Photo A. Muhranoff, 2011).jpg",
        "File:Khada Gorge Valley Filled with Morning Fog in Georgia.jpg",
    ],
    "shovi-resort": [
        "File:A Trail in The Pine Forest, Shovi, Racha, Georgia.jpg",
        "File:Pine Forest, Shovi, Racha, Georgia.jpg",
        "File:Road to Mamison Pass at Shovi.jpg",
        "File:Shovi - Old Holiday House “Stalin’s House”.jpg",
        "File:Shovi old hotel.jpg",
    ],
    "batumi-argo-cable-car": [
        "File:Argo Cable Car, Batumi (51154214428).jpg",
        "File:Argo Cable Car, Batumi (51155086395).jpg",
        "File:Argo Cable Car, Batumi (51153304742).jpg",
        "File:Argo Cable Car, Batumi (51155124105).jpg",
        "File:Argo Cable Car, Batumi (51154243623).jpg",
    ],
    "holy-trinity-cathedral-sameba": [
        "File:Sameba Cathedral, Holy Trinity Cathedral, Courtyard, Dusk 2, Tbilisi, Georgia.jpg",
        "File:Sameba Cathedral, Courtyard, Holy Trinity Cathedral, Tbilisi, Georgia.jpg",
        "File:Tbilisi Holy Trinity Cathedral (Sameba) IMG 8956 1920.jpg",
        "File:Tbilisi - Holy Trinity Cathedral (Sameba) (9458120939).jpg",
    ],
    "ilia-lake": [
        "File:Ilia Lake, Kakheti, Georgia 02.jpg",
        "File:Ilia Lake, Kakheti, Georgia 04.jpg",
        "File:Ilia Lake, Kakheti, Georgia 05.jpg",
        "File:Ilia Lake, Kakheti, Georgia 07.jpg",
    ],
    "jumati-monastery": [
        "File:Yermakov. Jumati monastery, 1877-1878.JPG",
        "File:Djumati mikael icon.jpg",
        "File:Icon of Archangels from Jumati monastery (Georgia).JPG",
    ],
    "khirsa-monastery": [
        "File:Khirsa Monastery in Tibaani.jpg",
    ],
    "khobi-monastery": [
        "File:Khobi Monastery (A. Muhranoff, 2013) 01.jpg",
        "File:Khobi Monastery (A. Muhranoff, 2013) 07.jpg",
        "File:Khobi Monastery (A. Muhranoff, 2013) 08.jpg",
        "File:Khobi Monastery (A. Muhranoff, 2013) 10.jpg",
    ],
    "khornabuji-fortress": [
        "File:Khornabuji Fortress, Kakheti, Georgia.jpg",
        "File:Khornabuji Fortress, Georgia.jpg",
        "File:Khornabuji Fortress. Ruins.jpg",
        "File:Ruins of Khornabuji.jpg",
    ],
    "kinchkha-waterfall": [
        "File:Kinchkha Waterfall.jpg",
        "File:Kinchkha 08.jpg",
        "File:Kinchkha 13.jpg",
        "File:Kinchkha 24.jpg",
    ],
    "kvariati": [
        "File:Black sea coastline - Kvariati, Georgia.jpg",
        "File:Kvariati, Ajaria, Georgia. Black Sea. (29422670295).jpg",
        "File:Kvariati (5545848197).jpg",
    ],
    "kvetera-fortress": [
        "File:Akhmeta, Kvetera 13.jpg",
    ],
    "mutso": [
        "File:Mutso, Georgia (1).jpg",
        "File:MUTSO (KHEVSURETI).jpg",
        "File:Mutso (9460921390).jpg",
        "File:Mutso 2016.jpg",
    ],
    "nekresi-monastery": [
        "File:Nekresi Monastery complex, Georgia 05.jpg",
        "File:Nekresi Monastery complex, Georgia 10.jpg",
        "File:Nekresi Monastery complex, Georgia 18.jpg",
        "File:Nekresi Monastery complex, Georgia 20.jpg",
    ],
    "ninotsminda-cathedral": [
        "File:Ninotsminda Cathedral 02.jpg",
        "File:Ninotsminda Cathedral 03.jpg",
        "File:2024-08-10 Belfry of Ninotsminda Cathedral.jpg",
        "File:Ninotsminda monastery, Kakheti, Georgia (1).jpg",
    ],
    "skhalta-monastery": [
        "File:სხალთის ტაძარი.jpg",
        "File:Skhalta monastery2.jpg",
        "File:Western door of Skhalta 2.jpg",
        "File:Southern door of Skhalta (2).jpg",
    ],
    "shaori-reservoir": [
        "File:2015-08-27 (27) Shaori reservoir.jpg",
        "File:2015-08-27 (28) Shaori reservoir.jpg",
        "File:2015-08-27 (29) Shaori reservoir.jpg",
        "File:2015-08-27 (30) Shaori reservoir.jpg",
        "File:2015-08-27 (32) Shaori reservoir.jpg",
    ],
    "timotesubani-monastery": [
        "File:Timotesubani church, Georgia 2.jpg",
        "File:Timotesubani church, Georgia 4.jpg",
        "File:Timotesubani church, Georgia 5.jpg",
        "File:Timotesubani church, Georgia 8.jpg",
    ],
    "ujarma-fortress": [
        "File:Ujarma fortress in Georgia 02.jpg",
        "File:Ujarma fortress in Georgia 03.jpg",
        "File:Ujarma fortress in Georgia 07.jpg",
        "File:Ujarma fortress in Georgia 14.jpg",
    ],
    "zhinvali-reservoir": [
        "File:Zhinvali reservoir, Georgia (4).jpg",
        "File:Panoraview of Zhinvali Reservoir 09.23.jpg",
        "File:Zhinvali Dam Gruzia 2019 4.jpg",
    ],
    "zoti": [
        "File:Riv. Gubazeuli in Zoti.jpg",
    ],
    "adishi": [
        "File:Adishi Village (2050m), Samegrelo-Zemo Svaneti, Georgia.jpg",
        "File:Adishi – 03.jpg",
        "File:Adishi Tower.jpg",
        "File:Adishi – 01.jpg",
    ],
    "becho-mazeri": [
        "File:Street in Mazeri village of Becho Community.jpg",
        "File:House in Becho community.jpg",
        "File:Mazeri, Svaneti, Georgia (36060612100).jpg",
        "File:Ushba from Dolasvipi (G.N. 2008).jpg",
    ],
    "shenako-diklo": [
        "File:Shenako panorama.jpg",
        "File:Shenako.Tusheti.JPG",
        "File:From Diklo to Shenako.jpg",
        "File:Tusheti, Georgia — Shenako.jpg",
    ],
    "vashlovani-national-park": [
        "File:Landscape in Vashlovani National Park.jpg",
        "File:Jahlinmarceta vashlovani.jpg",
        "File:Vashlovani State Reserve, Georgia.jpg",
        "File:Vashlovani National Park in Georgia.jpg",
    ],
    "didgori-battle-memorial": [
        "File:Didgori Monument 01.jpg",
        "File:Didgori Monument 04.jpg",
        "File:Didgori Memorial.jpg",
    ],
    "abastumani-observatory": [
        "File:Dome of ASA AZ1500 telescope in Abastumani.jpg",
        "File:Abastumani Astrophysical Observatory (1).jpg",
        "File:Abastumani Astrophysical Observatory (2).jpg",
        "File:Abastumani Astrophysical Observatory (3).jpg",
    ],
    "batumi-6-may-park-dolphinarium": [
        "File:Pokaz delfinarium batumi 1.jpg",
        "File:Batumi dolphinarium.jpg",
        "File:Nuri Lake.jpg",
        "File:Batumi Dolphinarium 3.jpg",
    ],
    "jvari-pass-friendship-monument": [
        "File:Russia-Georgia friendship monument, Dzhvaris pass.jpg",
        "File:Russia–Georgia Friendship Monument 09.23.jpg",
        "File:Russia–Georgia Friendship Monument Gruzia 2019 5.jpg",
        "File:Russia–Georgia Friendship Monument Gruzia 2019 2.jpg",
    ],
}


def clean_html(value: str) -> str:
    value = html.unescape(value or "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def commons_metadata(title: str, width: int) -> dict:
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "extmetadata|url|size",
        "iiurlwidth": str(width),
        "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = json.load(response)
    page = next(iter((payload.get("query") or {}).get("pages", {}).values()), {})
    if page.get("missing") is not None:
        raise ValueError(f"Commons file does not exist: {title}")
    info = (page.get("imageinfo") or [{}])[0]
    ext = info.get("extmetadata") or {}
    license_name = clean_html((ext.get("LicenseShortName") or {}).get("value", ""))
    if not any(marker in license_name.upper() for marker in ALLOWED_LICENSE_MARKERS):
        raise ValueError(f"Unsupported license for {title}: {license_name}")
    return {
        "title": page.get("title", title),
        "author": clean_html((ext.get("Artist") or {}).get("value", "")) or "Wikimedia Commons contributor",
        "license": license_name,
        "license_url": clean_html((ext.get("LicenseUrl") or {}).get("value", "")),
        "source": info.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
        "download_url": info.get("thumburl") or info.get("url"),
        "original_width": info.get("width"),
        "original_height": info.get("height"),
    }


def download_webp(url: str, destination: Path, quality: int) -> tuple[int, int]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read()
    with Image.open(io.BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((1800, 1400), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".part")
        image.save(temporary, "WEBP", quality=quality, method=6)
        temporary.replace(destination)
        return image.size


def yaml_scalar(value: str) -> str:
    # JSON double-quoted strings are valid YAML scalars and safely preserve punctuation.
    return json.dumps(value, ensure_ascii=False)


def update_yaml(path: Path, slug: str, media: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^image:.*$", f"image: /assets/photos/{slug}.webp", text, count=1)

    gallery_lines = ["gallery:"]
    for item in media[1:]:
        local_name = Path(item["local_path"]).name
        gallery_lines.extend([
            f"- image: /assets/photos/{local_name}",
            f"  author: {yaml_scalar(item['author'])}",
            f"  license: {yaml_scalar(item['license'])}",
            f"  license_url: {yaml_scalar(item['license_url'])}",
            f"  source: {yaml_scalar(item['source'])}",
        ])
    gallery_block = "\n".join(gallery_lines) + "\n"
    text, count = re.subn(r"(?ms)^gallery:\n.*?(?=^visit_hours:)", gallery_block, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace gallery in {path}")

    primary = media[0]
    credit_block = "\n".join([
        "image_credit:",
        f"  author: {yaml_scalar(primary['author'])}",
        f"  license: {yaml_scalar(primary['license'])}",
        f"  license_url: {yaml_scalar(primary['license_url'])}",
        f"  source: {yaml_scalar(primary['source'])}",
    ]) + "\n"
    text, count = re.subn(r"(?ms)^image_credit:\n.*?(?=^rating:)", credit_block, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace image credit in {path}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", default="content/attractions")
    parser.add_argument("--photos", default="static/photos")
    parser.add_argument("--report", default="reports/attraction-photo-remediation.json")
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--quality", type=int, default=86)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download and replace existing local media instead of reusing it.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        help="Limit the run to one attraction slug; repeat for multiple slugs.",
    )
    args = parser.parse_args()

    content = Path(args.content)
    photos = Path(args.photos)
    report: list[dict] = []
    targets = EXACT_MEDIA
    if args.slug:
        unknown = sorted(set(args.slug) - set(EXACT_MEDIA))
        if unknown:
            raise SystemExit(f"Unknown attraction slug(s): {', '.join(unknown)}")
        targets = {slug: EXACT_MEDIA[slug] for slug in args.slug}

    for slug, titles in targets.items():
        entry = {"slug": slug, "status": "pending", "media": [], "errors": []}
        print(f"[{slug}] validating {len(titles)} exact Commons files")
        for title in titles:
            try:
                item = commons_metadata(title, args.width)
                entry["media"].append(item)
            except Exception as exc:  # report individual external failures without corrupting content
                entry["errors"].append({"title": title, "error": str(exc)})
            time.sleep(0.12)

        if not entry["media"]:
            entry["status"] = "blocked"
            report.append(entry)
            continue
        if args.apply:
            for index, item in enumerate(entry["media"]):
                suffix = "" if index == 0 else f"-{index}"
                destination = photos / f"{slug}{suffix}.webp"
                try:
                    if destination.exists() and destination.stat().st_size > 0 and not args.force:
                        with Image.open(destination) as existing:
                            width, height = existing.size
                    else:
                        width, height = download_webp(item["download_url"], destination, args.quality)
                    item["local_path"] = destination.as_posix()
                    item["output_width"] = width
                    item["output_height"] = height
                    item["bytes"] = destination.stat().st_size
                except Exception as exc:
                    entry["errors"].append({"title": item["title"], "error": f"download: {exc}"})
            successful = [item for item in entry["media"] if item.get("local_path")]
            if successful:
                update_yaml(content / f"{slug}.yml", slug, successful)
                entry["media"] = successful
                entry["status"] = "updated"
            else:
                entry["status"] = "blocked"
        else:
            entry["status"] = "validated"
        report.append(entry)

    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "entries": len(report),
        "updated": sum(row["status"] == "updated" for row in report),
        "blocked": sum(row["status"] == "blocked" for row in report),
        "media": sum(len(row["media"]) for row in report),
        "errors": sum(len(row["errors"]) for row in report),
        "report": str(output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


