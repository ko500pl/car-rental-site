#!/usr/bin/env python3
"""Apply the verified remaining-region attraction gallery audit."""
import json,re,time,html,urllib.request,yaml
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageEnhance
R=Path(__file__).resolve().parents[1];C=R/"content/attractions";P=R/"static/photos"
rows=json.loads((R/"docs/photo-audit/research/remaining-commons.json").read_text(encoding="utf-8"));g={}
for x in rows:g.setdefault(x["slug"],[]).append(x)
REG={"tbilisi","kakheti","adjara","mtskheta-mtianeti","kvemo-kartli","guria"}
for z in g:g[z].sort(key=lambda x:(x.get("query")!="manual exact allow-list",-int(x.get("width") or 0)*int(x.get("height") or 0)))
S={}
for p in C.glob("*.yml"):
 d=yaml.safe_load(p.read_text(encoding="utf-8")) or {}
 if d.get("region") not in REG:continue
 target={5.0:8,4.5:7,4.0:6}.get(float(d.get("rating",0)),4);gap=max(0,target-1-len(d.get("gallery") or []))
 if gap and g.get(p.stem):S[p.stem]=list(range(min(gap,len(g[p.stem]))))
B=Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")
A={}
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
 for a in range(2):
  try:
   with urllib.request.urlopen(req,timeout=20) as z:r=z.read()
   with Image.open(BytesIO(r)) as im:sv(im,d)
   return
  except Exception:
   if a==1:raise
   time.sleep(1)
def fresh(G):
 return [x for x in G if "-verified-" not in str(x.get("image","")) and "-premium-ai-" not in str(x.get("image",""))]
E={}
for s in sorted(set(S)|set(A)):
 if s <= "lomisa-church":continue
 p=C/(s+".yml");d=yaml.safe_load(p.read_text(encoding="utf-8"));G=fresh(list(d.get("gallery") or []))
 if False:G=[]
 src=[]
 for n,i in enumerate(S.get(s,[]),1):
  x=g[s][i];o=P/f"{s}-verified-{n}-20260831.webp"
  if not o.is_file():dl(x,o)
  G.append({"image":f"/assets/photos/{o.name}","author":cl(x.get("artist","")),"license":cl(x.get("license","")),"license_url":lu(x.get("license","")),"source":x["page_url"]});src.append(x["page_url"]);time.sleep(.25)
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
(R/"docs/photo-audit/research/remaining-applied.json").write_text(json.dumps(E,ensure_ascii=False,indent=2),encoding="utf-8")


















