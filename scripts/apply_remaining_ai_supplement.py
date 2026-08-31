#!/usr/bin/env python3
"""Fill exact-location source gaps with commissioned AI-assisted images."""
import json, re, yaml
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content/attractions"
PHOTOS = ROOT / "static/photos"
BASE = Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")

SHEETS = {
    "batumi-alphabetic-tower": "00fadd25-7059-4772-a4fa-773c22302137",
    "dandalo-arched-bridge": "d79e0a33-c796-44ad-b4e4-d37e3da1e6aa",
    "dariali-gorge-gveleti-waterfalls": "e67b8ac6-3f86-412a-b5cb-6b7bb28c3e26",
    "fabrika-marjanishvili": "14763914-6404-483e-abef-0a316411d56e",
    "green-lake-goderdzi": "f0d761de-dcd8-4ca6-95a5-04e92158a8e8",
    "keda-wine-cellars": "c8065c94-d235-4e90-9f0f-504e6252a041",
    "khareba-wine-tunnel": "512d0af9-7917-4689-a8a3-588a5ec3fe42",
    "kobuleti": "ce73fd83-90a9-4323-953c-4819daafd37b",
    "kvareli-kindzmarauli": "80bbfc43-d643-4c52-a40b-a03223e04bce",
    "likhauri-church": "5b273494-a3ba-40e4-b31e-40f0afdad31b",
    "makhuntseti-waterfall": "8c30c7f6-24bb-4242-bad0-46a9f69108ab",
    "mtatsminda-park": "d6b08929-91f4-4830-847f-3242a20e7712",
    "nodar-dumbadze-house-museum": "80bfdd20-c8cd-437d-ab4c-a51f34f43c1f",
    "sameba-jikheti-monastery": "631259c4-3920-4519-bda7-59cc67465964",
    "shekvetili-dendrological-park": "94e1cd0e-f666-4452-b965-91ecf340ef20",
    "shukhuti-lelo-burti": "85bdf954-9c0b-4cad-a136-d7dd7e7d9044",
    "sno-valley": "678c4127-5044-4f37-a8fe-e96718447630",
    "sololaki-art-nouveau": "f9393b63-1dc1-4702-a634-29dcf2c407e0",
    "takhti-tepha-mud-volcanoes": "11aa922d-3eba-4253-a89b-1061df123d05",
    "tsitsinatela-amusement-park": "016946c0-e63e-4b29-aecc-cd17781d2855",
    "bolnisi-town": "a609ba9c-c1ad-4b47-8e63-dd34d12c6cbc",
    "khada-valley": "5be1b9ce-15e6-459e-ab26-495a01505124",
    "khulo-cable-car-upper-adjara": "c7d4e6b2-e6ff-4d1c-8013-5ce588d30f64",
    "kvetera-fortress": "8ae23d1d-cff6-442c-8812-15f8572e9ce8",
    "batumi-boulevard-old-town": "46f71a79-5020-45be-b069-89febe0a972b",
    "beshumi": "7bbd67fa-b3b2-46c9-96a4-5d0d7d6f8696",
    "marjanishvili-theatre": "9d8ce9cb-b2fe-4632-8fbc-705e44662af1",
    "narikala-fortress": "2b6c29c6-8989-4d93-a651-b78840f2a348",
    "omalo-tusheti": "c3312a45-e594-4e04-9ede-871452b67728",
    "metekhi-church": "feacb714-5292-4d16-8399-c747bdd66cef",
    "rustaveli-national-theatre": "c3e6cb6b-0537-49f3-8ac7-5a01dbc178e3",
    "svetitskhoveli-cathedral": "b6f02557-e83d-40f5-b4d8-3597954b091f",
    "tbilisi-opera-ballet-theatre": "ea48f820-23bb-4502-838d-41df3d0e054e",
    "ureki": "8e3c4c90-2a25-4092-9e44-d02d83105660",
    "zoti": "ff3cebab-b7f5-477b-9fba-f222caae5bdb",
    "sighnaghi": "e51d6420-0433-4279-b9f5-94c93c1d24b9",
    "sarpi-beach": "9dbd83be-45ec-4c9b-9547-2ed6f46dea20",
    "pitareti-monastery": "e6d2f188-10a3-4c58-b9b2-1cbdd84eccaf",
}

def save(source, destination):
    with Image.open(source) as image:
        image = ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"), (1600, 900), Image.Resampling.LANCZOS)
        image = ImageEnhance.Contrast(image).enhance(1.035)
        image = ImageEnhance.Color(image).enhance(1.025)
        ImageEnhance.Sharpness(image).enhance(1.07).save(destination, "WEBP", quality=88, method=6)

evidence = {}
for slug, uid in SHEETS.items():
    path = CONTENT / f"{slug}.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    target = {5.0: 8, 4.5: 7, 4.0: 6}.get(float(data.get("rating", 0)), 4)
    gallery = list(data.get("gallery") or [])
    gap = max(0, target - 1 - len(gallery))
    added = []
    for index in range(1, min(gap, 5) + 1):
        source = BASE / f"exec-{uid}-{index}.png"
        destination = PHOTOS / f"{slug}-premium-ai-{index}-20260831.webp"
        save(source, destination)
        item = {
            "image": f"/assets/photos/{destination.name}",
            "author": "OpenAI / RentUp",
            "license": "Original commissioned AI-assisted asset",
            "license_url": "",
            "source": "https://rentup.ge/",
        }
        gallery.append(item)
        added.append(str(source))
    gallery = gallery[:target - 1]
    text = path.read_text(encoding="utf-8")
    block = yaml.safe_dump({"gallery": gallery}, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    text, count = re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)", block + "\n", text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(slug)
    path.write_text(text, encoding="utf-8")
    evidence[slug] = {"target": target, "total_images": 1 + len(gallery), "added_ai_assisted": added}
    print(slug, 1 + len(gallery))

(ROOT / "docs/photo-audit/research/remaining-ai-applied.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
)

