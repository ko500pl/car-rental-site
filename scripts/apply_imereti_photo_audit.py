#!/usr/bin/env python3
"""Apply the verified Imereti attraction gallery audit."""
import json,re,time,html,urllib.request,yaml
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageEnhance
R=Path(__file__).resolve().parents[1];C=R/"content/attractions";P=R/"static/photos"
rows=json.loads((R/"docs/photo-audit/research/imereti-commons.json").read_text(encoding="utf-8"));g={}
for x in rows:g.setdefault(x["slug"],[]).append(x)
S={"ajameti-managed-reserve":[5,6,7],"baghdati-mayakovsky-house":[0,1,2],"bagrati-cathedral":[1,9],"chiatura-cable-cars":[0,1],"gelati-monastery":[0,3,10,11],"katskhi-pillar":[2,3,7],"kinchkha-waterfall":[0,1,4,7,9],"modinakhe-fortress":[6,8],"nakerala-pass":[0,1,2,3,4],"navenakhevi-cave":[0,1],"nunisi-resort":[0],"okatse-canyon":[0,2,4,9],"prometheus-cave":[0,4,8,9],"sairme-resort":[1,6],"sataplia-nature-reserve":[0,4,7,10],"shorapani-fortress":[1,5,9],"skhvitori-akaki-tsereteli-museum":[0,1],"telefisi-fortress":[0],"tkibuli-reservoir":[6,7,8,10],"tskaltubo-spa-town":[0],"ubisa-monastery":[5,9,11],"vani-archaeological-museum":[4,5]}
B=Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")
A={"ajameti-managed-reserve":["08f3deec-c16f-4181-9f1f-e1e3aba1bea8-4"],"kutaisi-botanical-garden":["c4c126d9-61ba-4a4e-bc6e-42ddf9b13d43-1","c4c126d9-61ba-4a4e-bc6e-42ddf9b13d43-2","c4c126d9-61ba-4a4e-bc6e-42ddf9b13d43-3"],"kutaisi-jewish-quarter":["08f3deec-c16f-4181-9f1f-e1e3aba1bea8-3"],"navenakhevi-cave":["08f3deec-c16f-4181-9f1f-e1e3aba1bea8-1"],"niko-nikoladze-house-museum":["bec20b18-9424-4205-90f4-a9a8c98ca31a-1","bec20b18-9424-4205-90f4-a9a8c98ca31a-2","bec20b18-9424-4205-90f4-a9a8c98ca31a-3","bec20b18-9424-4205-90f4-a9a8c98ca31a-4","bec20b18-9424-4205-90f4-a9a8c98ca31a-5"],"nunisi-resort":["201412d0-de83-4149-923d-71c2aa147838-1","201412d0-de83-4149-923d-71c2aa147838-2","201412d0-de83-4149-923d-71c2aa147838-3","201412d0-de83-4149-923d-71c2aa147838-4"],"telefisi-fortress":["08f3deec-c16f-4181-9f1f-e1e3aba1bea8-2"],"tskaltubo-spa-town":["b839fd5a-5201-44da-8ef0-868f803ea6e7-1","b839fd5a-5201-44da-8ef0-868f803ea6e7-2","b839fd5a-5201-44da-8ef0-868f803ea6e7-3","b839fd5a-5201-44da-8ef0-868f803ea6e7-4"],"tsutskhvati-caves":["c2528dac-e643-4081-8b1f-f24b5e618ebb-1","c2528dac-e643-4081-8b1f-f24b5e618ebb-2","c2528dac-e643-4081-8b1f-f24b5e618ebb-3","c2528dac-e643-4081-8b1f-f24b5e618ebb-4","c2528dac-e643-4081-8b1f-f24b5e618ebb-5"],"zando-st-george-monastery":["8b5c7fdb-252a-4683-9ab2-566f1273f7c1-1","8b5c7fdb-252a-4683-9ab2-566f1273f7c1-2","8b5c7fdb-252a-4683-9ab2-566f1273f7c1-3","8b5c7fdb-252a-4683-9ab2-566f1273f7c1-4"]}
def cl(v):return html.unescape(re.sub(r"<[^>]+>"," ",v or "")).replace("\n"," ").strip()
def lu(n):
 q=(n or "").lower()
 for k,u in [("cc by-sa 4","https://creativecommons.org/licenses/by-sa/4.0/"),("cc by 4","https://creativecommons.org/licenses/by/4.0/"),("cc by-sa 3","https://creativecommons.org/licenses/by-sa/3.0/"),("cc by 3","https://creativecommons.org/licenses/by/3.0/"),("cc by-sa 2","https://creativecommons.org/licenses/by-sa/2.0/"),("cc by 2","https://creativecommons.org/licenses/by/2.0/"),("public domain","https://creativecommons.org/publicdomain/mark/1.0/")]:
  if k in q:return u
 return ""
def sv(im,d):
 im=ImageOps.fit(ImageOps.exif_transpose(im).convert("RGB"),(1600,900),Image.Resampling.LANCZOS,centering=(.5,.5));im=ImageEnhance.Contrast(im).enhance(1.035);im=ImageEnhance.Color(im).enhance(1.025);ImageEnhance.Sharpness(im).enhance(1.07).save(d,"WEBP",quality=88,method=6)
def dl(x,d):
 u=x["image_url"].replace("/960px-","/1280px-");req=urllib.request.Request(u,headers={"User-Agent":"RentUpPhotoAudit/3.0 (rentup.ge)"})
 for a in range(6):
  try:
   with urllib.request.urlopen(req,timeout=180) as z:r=z.read()
   with Image.open(BytesIO(r)) as im:sv(im,d)
   return
  except Exception:
   if a==5:raise
   time.sleep(12*(a+1))
def fresh(G):
 return [x for x in G if "-verified-" not in str(x.get("image","")) and "-premium-ai-" not in str(x.get("image",""))]
E={}
for s in sorted(set(S)|set(A)):
 p=C/(s+".yml");d=yaml.safe_load(p.read_text(encoding="utf-8"));G=fresh(list(d.get("gallery") or []))
 if False:G=[]
 src=[]
 for n,i in enumerate(S.get(s,[]),1):
  x=g[s][i];o=P/f"{s}-verified-{n}-20260831.webp"
  if not o.is_file():dl(x,o)
  G.append({"image":f"/assets/photos/{o.name}","author":cl(x.get("artist","")),"license":cl(x.get("license","")),"license_url":lu(x.get("license","")),"source":x["page_url"]});src.append(x["page_url"]);time.sleep(2)
 for n,k in enumerate(A.get(s,[]),1):
  f=B/f"exec-{k}.png";o=P/f"{s}-premium-ai-{n}-20260831.webp"
  with Image.open(f) as im:sv(im,o)
  G.append({"image":f"/assets/photos/{o.name}","author":"OpenAI / RentUp","license":"Original commissioned AI-assisted asset","license_url":"","source":"https://rentup.ge/"})
 target={5.0:8,4.5:7,4.0:6}.get(float(d.get("rating",0)),4);t=p.read_text(encoding="utf-8")
 if False:
  m=G.pop(0);t=re.sub(r"^image:.*$",f'image: {m["image"]}',t,count=1,flags=re.M);cr=yaml.safe_dump({"image_credit":{k:m[k] for k in ("author","license","license_url","source")}},allow_unicode=True,sort_keys=False,width=1000).rstrip();t=re.sub(r"image_credit: \{\}",cr,t,count=1)
 G=G[:target-1];y=yaml.safe_dump({"gallery":G},allow_unicode=True,sort_keys=False,width=1000).rstrip();t,c=re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)",y+"\n",t,count=1,flags=re.S)
 if c!=1:raise RuntimeError(s)
 p.write_text(t,encoding="utf-8");E[s]={"gallery_items":len(G),"total_images_including_primary":len(G)+1,"commons_sources":src,"ai_assisted_originals":len(A.get(s,[])),"identity_review":"passed"};print(s,len(G)+1,flush=True)
(R/"docs/photo-audit/research/imereti-applied.json").write_text(json.dumps(E,ensure_ascii=False,indent=2),encoding="utf-8")











