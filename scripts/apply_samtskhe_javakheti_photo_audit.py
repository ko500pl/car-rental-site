#!/usr/bin/env python3
"""Apply the verified Samtskhe-Javakheti attraction gallery audit."""
import json,re,time,html,urllib.request,yaml
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageEnhance
R=Path(__file__).resolve().parents[1];C=R/"content/attractions";P=R/"static/photos"
rows=json.loads((R/"docs/photo-audit/research/samtskhe-javakheti-commons.json").read_text(encoding="utf-8"));g={}
for x in rows:g.setdefault(x["slug"],[]).append(x)
S={"abastumani-observatory":[10,11,12],"bakuriani":[2,4,12,14],"borjomi-central-park":[1,2,0,3],"borjomi-kharagauli-national-park":[1,13],"javakheti-national-park":[0,2,5,7,13],"kumurdo-cathedral":[0],"rabati-castle":[3,8,9,10],"sapara-monastery":[1,4,6,13],"tmogvi-fortress":[5,6,9,10,11],"vanis-kvabebi":[0,9,10,12],"vardzia":[1,3,4,8,12],"zarzma-monastery":[4,9]}
B=Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")
A={"bakuriani-botanical-garden":["e8ab9569-f242-4939-9600-51c42ffcc0c4","df3cd31e-a409-4e28-8755-a344516ea7fd","0ab459ea-73b2-49ef-b6c4-ebc2ed3e2461","d71f7dfc-1419-48f0-8702-b893a4438477"],"kukushka-narrow-gauge-railway":["4b968936-327a-4460-bdad-19fc14692e93","cf774165-0d72-49ed-ab6f-59bb0eda6262","3cc3ea3e-2a34-4133-9233-6af197046018"],"paravani-tabatskuri-lakes":["2782609b-d978-4f5e-8d65-99011f83ff48","8b774f03-0d4f-4add-91d9-9bfc40d9add3","8638941a-14ab-4686-a30d-0f6e6a29fb04","1cf0850c-a160-4aee-8ec5-0fb973322a83"],"likani-palace":["8ee8fb38-eaa1-46f9-8371-d6d8798e3541","55e1b59e-e1dd-4593-b612-3dec4aced347","645ea4fb-5eb4-4458-8e97-f134172a7c12"]}
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
 if s=="bakuriani-botanical-garden":G=G[:1]
 src=[]
 for n,i in enumerate(S.get(s,[]),1):
  x=g[s][i];o=P/f"{s}-verified-{n}-20260831.webp"
  if not o.is_file():dl(x,o)
  G.append({"image":f"/assets/photos/{o.name}","author":cl(x.get("artist","")),"license":cl(x.get("license","")),"license_url":lu(x.get("license","")),"source":x["page_url"]});src.append(x["page_url"]);time.sleep(2)
 for n,k in enumerate(A.get(s,[]),1):
  f=B/f"exec-{k}.png";o=P/f"{s}-premium-ai-{n}-20260831.webp"
  with Image.open(f) as im:sv(im,o)
  G.append({"image":f"/assets/photos/{o.name}","author":"OpenAI / RentUp","license":"Original commissioned AI-assisted asset","license_url":"","source":"https://rentup.ge/"})
 y=yaml.safe_dump({"gallery":G},allow_unicode=True,sort_keys=False,width=1000).rstrip();t=p.read_text(encoding="utf-8");t,c=re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)",y+"\n",t,count=1,flags=re.S)
 if c!=1:raise RuntimeError(s)
 p.write_text(t,encoding="utf-8");E[s]={"gallery_items":len(G),"total_images_including_primary":len(G)+1,"commons_sources":src,"ai_assisted_originals":len(A.get(s,[])),"identity_review":"passed"};print(s,len(G)+1,flush=True)
(R/"docs/photo-audit/research/samtskhe-javakheti-applied.json").write_text(json.dumps(E,ensure_ascii=False,indent=2),encoding="utf-8")
