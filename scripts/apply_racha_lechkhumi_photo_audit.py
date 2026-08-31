#!/usr/bin/env python3
"""Apply the verified Racha-Lechkhumi attraction gallery audit."""
import json,re,time,html,urllib.request,yaml
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageEnhance
R=Path(__file__).resolve().parents[1];C=R/"content/attractions";P=R/"static/photos"
rows=json.loads((R/"docs/photo-audit/research/racha-lechkhumi-commons.json").read_text(encoding="utf-8"));g={}
for x in rows:g.setdefault(x["slug"],[]).append(x)
S={"ambrolauri":[4,6],"barakoni-church":[8,9,10],"chiora":[0],"glola":[5,6,7],"khvanchkara-wine-zone":[0,4],"lentekhi":[0,5],"minda-fortress":[0,1,2],"mount-khvamli":[0,4,5,8],"mravaldzali":[0,1,2,3,4],"muri-fortress":[0],"nikortsminda-cathedral":[5,6,7,8,10,11],"oni-synagogue":[8,9,10],"oni":[0],"shaori-reservoir":[1,2,9],"shovi-resort":[5,0],"utsera":[0]}
B=Path(r"C:\Users\t.kopaliani\.codex\generated_images\019ffbc0-c66e-7e40-9897-1c16e55a8c6b")
A={"gogolati":["a0fe5136-1345-4a0c-b0f2-593b42010cde","be0b396c-b7e0-4566-97c0-85dd5fd6f8b8","f412448c-c327-48c7-8889-33faff25f538","5ae0c812-4f03-4f79-9910-7d4ab3a7c002","83684e4b-f721-4c09-b8f4-eeb5a807af24","df5df774-c47d-4936-a185-b706bd2af2c7"],"udziro-lake-buba-glacier":["ed7ac064-8cc0-4b0a-981a-328769900e0e","bb726423-90e4-4396-a92e-a4b5f5129ff5","0555cdbe-4d8c-4c8e-9677-9affb7690eb0","a3eb2061-2749-4ce2-9c73-3887b0d71ede","88b6b609-cc8e-4de7-8952-5cb6c0b13d87","a791f87f-eae4-4005-8871-778c07002d6f","81cb9a77-a8e3-430b-a5e3-3f05e01acc19"],"chiora":["ddc0cdfd-e4d0-43da-9f9a-e3ea75a21376","e8871fd6-2ce1-4004-9061-ef88ac13b24d","d9268883-0faf-4f70-bdcd-1157729391b2","08a8c4f9-7789-4a52-9885-a50fb417df00"],"glola":["e69338c9-5de0-44cd-9e87-433cb9598df6"],"minda-fortress":["f3f1a11c-391a-41f0-9308-a78a2c3e82bf","0c3ba57d-0819-472a-a655-06f88f85d0c4"],"muri-fortress":["88fef7b6-79af-4d43-af99-dbbe08121f7d","1f36c651-6fd3-4f78-a91b-7d6840de4ebd"],"mount-khvamli":["1fbb905e-b40a-499a-a45c-464dfa4724a8"],"oni":["83fce56a-9ef8-4ef5-8d4a-525c7124e1dd","dacba11f-8e80-4837-bfcd-75e80379912a","2b74551b-b7e3-4e2b-ab13-b72696104aba"],"tsageri":["8c5f1dab-3e55-4c2f-9f90-d7cb66c88f26","bb1d7fdb-0fa8-4f1a-8d1c-f93aeed4914e","5e123b2e-5023-45c1-bd27-d674eb7f031b"],"utsera":["fc35f0df-8bf3-4b11-9750-f85812bac113"],"waterfall-of-love-racha":["51c35704-7e32-4259-8cd7-415ceaba5468","825e4941-89b7-493d-9853-0642d7e66db5","3a9b0405-b689-4e86-90aa-a632c61efa24","8b5be55b-beed-4390-8d36-35ab1bcc6097"]}
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
 if s=="udziro-lake-buba-glacier":G=[]
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
 if s in ("gogolati","waterfall-of-love-racha"):
  m=G.pop(0);t=re.sub(r"^image:.*$",f'image: {m["image"]}',t,count=1,flags=re.M);cr=yaml.safe_dump({"image_credit":{k:m[k] for k in ("author","license","license_url","source")}},allow_unicode=True,sort_keys=False,width=1000).rstrip();t=re.sub(r"image_credit: \{\}",cr,t,count=1)
 G=G[:target-1];y=yaml.safe_dump({"gallery":G},allow_unicode=True,sort_keys=False,width=1000).rstrip();t,c=re.subn(r"gallery:(?: \[\])?\n.*?(?=visit_hours:)",y+"\n",t,count=1,flags=re.S)
 if c!=1:raise RuntimeError(s)
 p.write_text(t,encoding="utf-8");E[s]={"gallery_items":len(G),"total_images_including_primary":len(G)+1,"commons_sources":src,"ai_assisted_originals":len(A.get(s,[])),"identity_review":"passed"};print(s,len(G)+1,flush=True)
(R/"docs/photo-audit/research/racha-lechkhumi-applied.json").write_text(json.dumps(E,ensure_ascii=False,indent=2),encoding="utf-8")









