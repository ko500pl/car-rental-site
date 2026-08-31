#!/usr/bin/env python3
"""Crop and apply the final audited AI-assisted attraction sheets."""
import json, re, yaml
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONTENT, PHOTOS = ROOT / "content/attractions", ROOT / "static/photos"
BASE = Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")

# slug: (sheet uuid, panel count, allowed panel numbers)
SHEETS = {
 "samtavro-monastery":("234fc723-8f5c-4bb8-820e-1ffdc20d03ac",4,None),
 "shekvetili-black-sea-arena":("01f0501d-1774-49df-b388-bdac6b68acb7",4,None),
 "tbilisi-botanical-garden":("d5082d96-e5b8-4a02-9bb2-be635b7be120",4,None),
 "tbilisi-sea":("c6ac3147-6e48-41f2-8aef-87e2502d2063",5,None),
 "truso-valley":("915ba808-8a01-4951-9f64-1c55d5e3a0cd",4,None),
 "vashlovani-national-park":("abeb316f-4ff0-4e3d-a734-899a276a9b66",4,None),
 "marneuli":("bfa42ac3-a310-4a6f-a347-57f90fa83d35",4,None),
 "mtirala-national-park":("bedfb226-dcad-4a79-a1ff-acbc15fc0894",4,None),
 "mutso":("1cc3130b-8076-4668-80d1-657f4f1c4e46",4,None),
 "napareuli":("162217f6-f6f6-45c7-bb65-c79aa8698b3f",4,None),
 "nekresi-monastery":("268e6e94-c989-4fc7-ac63-f57ed0938361",4,None),
 "pankisi-gorge":("cbb61454-d94c-48f4-a76a-aefb48edd788",4,[1,3,4]),
 "ozurgeti":("596c61f7-c9b9-4d19-8032-4b9ef6d8e7e5",4,None),
 "rustavi":("664b18a6-76f8-457b-9a2f-a2b6a988540b",4,None),
 "samshvilde":("c27b8de1-4abf-4d35-a8d2-8435717d55e6",4,None),
 "shatili":("80b4e8a6-e82e-4bb9-bfde-d78faf225050",4,None),
 "shemokmedi-monastery":("9c154e83-3ddf-4865-8d68-4290f49bf691",4,None),
 "shenako-diklo":("ec9438f9-8d81-489a-88e5-3d8d9128252e",4,None),
 "shiomghvime-monastery":("f9dc40d1-fcbe-421b-a6e3-7da3dd19046c",4,None),
 "tbilisi-silk-museum":("774b6918-a470-4924-b2b1-d52777554834",4,None),
 "telavi-batonis-tsikhe":("faba7133-b87b-4a4a-88d7-03ddf1eba5dc",4,None),
 "tianeti":("e404c624-e4af-4205-8a6c-728f56ec4ed7",4,None),
 "tsalka-reservoir":("35518860-b069-4dfa-b542-176163dcb239",4,None),
 "tsughrughasheni-church":("d0e41872-a73c-4503-830d-6e5e3d84c9d3",4,None),
 "turtle-lake-vake-park":("c9b8560c-b4de-4eb8-b4fd-6fc7460d25a2",4,None),
 "zedazeni-monastery":("83e775ce-e595-4902-b439-94315b591775",4,None),
 "rustaveli-avenue":("0bc7b33f-f17a-4e6c-a26c-abde888a72e2",4,None),
 "nabeghlavi":("8a879cae-f996-436c-9e21-da3bcff5d8af",4,None),
 "petra-fortress":("b7bef2c2-aa41-47a2-9402-ddfb8721b021",4,None),
 "sioni-cathedral":("329d78ab-c250-4eeb-a6c6-26de2fd04fca",4,None),
 "zhinvali-reservoir":("5290987c-fc48-4faf-a6e7-6bbf206b11f4",4,None),
 "narikala-fortress":("e2527348-9a8f-4378-9c5f-3e41c125a4b1",4,None),
 "omalo-tusheti":("63918cc1-977d-4e16-86b7-0eb614fde45d",4,None),
}

EXTRA_SHEETS = {
 "marjanishvili-theatre":("8b9cc5a5-f609-4f90-a732-48822c2887e1",4,[1]),
 "rustaveli-national-theatre":("8b9cc5a5-f609-4f90-a732-48822c2887e1",4,[2]),
 "svetitskhoveli-cathedral":("8b9cc5a5-f609-4f90-a732-48822c2887e1",4,[3]),
 "ureki":("8b9cc5a5-f609-4f90-a732-48822c2887e1",4,[4]),
 "tbilisi-opera-ballet-theatre":("c9d98638-3392-4789-9153-6c641da40480",4,[1,3]),
}
SHEETS.update(EXTRA_SHEETS)
LAST_SHEETS = {
 "askana-fortress":("c32f0609-f47e-4c59-9964-f007b2048afa",4,[1]),
 "batumi-archaeological-museum":("c32f0609-f47e-4c59-9964-f007b2048afa",4,[2]),
 "geguti-palace":("c32f0609-f47e-4c59-9964-f007b2048afa",4,[3]),
 "kutaisi-historical-museum":("c32f0609-f47e-4c59-9964-f007b2048afa",4,[4]),
 "napareuli":("3e3fed7c-f186-46bc-a843-85cfd212a902",4,[1]),
 "nodar-dumbadze-house-museum":("3e3fed7c-f186-46bc-a843-85cfd212a902",4,[2]),
 "takhti-tepha-mud-volcanoes":("3e3fed7c-f186-46bc-a843-85cfd212a902",4,[3]),
 "telefisi-fortress":("3e3fed7c-f186-46bc-a843-85cfd212a902",4,[4]),
 "zando-st-george-monastery":("add99454-7537-41fb-8753-904badab572f",4,[1]),
}
SHEETS.update(LAST_SHEETS)

def boxes(count):
 return [(0,0,.5,.55),(.5,0,1,.55),(0,.55,1/3,1),(1/3,.55,2/3,1),(2/3,.55,1,1)] if count==5 else [(0,0,.5,.5),(.5,0,1,.5),(0,.5,.5,1),(.5,.5,1,1)]

def save(image, destination):
 image=ImageOps.fit(image.convert("RGB"),(1600,900),Image.Resampling.LANCZOS)
 image=ImageEnhance.Contrast(image).enhance(1.035)
 image=ImageEnhance.Color(image).enhance(1.025)
 ImageEnhance.Sharpness(image).enhance(1.07).save(destination,"WEBP",quality=88,method=6)

evidence={}
for slug,(uid,count,allowed) in SHEETS.items():
 path=CONTENT/f"{slug}.yml"; data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
 target={5.0:8,4.5:7,4.0:6}.get(float(data.get("rating",0)),4)
 gallery=list(data.get("gallery") or []); gap=max(0,target-1-len(gallery)); added=[]
 with Image.open(BASE/f"exec-{uid}.png") as sheet:
  w,h=sheet.size
  panels=allowed or list(range(1,count+1))
  for panel in panels[:gap]:
   b=boxes(count)[panel-1]; crop=sheet.crop(tuple(round(v*(w if j%2==0 else h)) for j,v in enumerate(b)))
   seq=len(gallery)+1; dest=PHOTOS/f"{slug}-premium-ai-final-{seq}-20260831.webp"; save(crop,dest)
   gallery.append({"image":f"/assets/photos/{dest.name}","author":"OpenAI / RentUp","license":"Original commissioned AI-assisted asset","license_url":"","source":"https://rentup.ge/"})
   added.append(f"exec-{uid}.png#panel-{panel}")
 text=path.read_text(encoding="utf-8"); block=yaml.safe_dump({"gallery":gallery[:target-1]},allow_unicode=True,sort_keys=False,width=1000).rstrip()
 text,n=re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)",block+"\n",text,count=1,flags=re.S)
 if n!=1: raise RuntimeError(slug)
 path.write_text(text,encoding="utf-8")
 evidence[slug]={"target":target,"total_images":1+len(gallery[:target-1]),"added":added}
 print(slug,evidence[slug]["total_images"],"/",target)
(ROOT/"docs/photo-audit/research/final-ai-applied.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
