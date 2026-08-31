#!/usr/bin/env python3
"""Remove duplicate/empty gallery refs and reuse unique matching local assets."""
import hashlib, re, yaml
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; CONTENT=ROOT/'content/attractions'; PHOTOS=ROOT/'static/photos'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for path in CONTENT.glob('*.yml'):
 data=yaml.safe_load(path.read_text(encoding='utf-8')) or {}; slug=path.stem
 target={5.0:8,4.5:7,4.0:6}.get(float(data.get('rating',0)),4)
 primary=data.get('image'); seen=set(); gallery=[]
 if primary:
  p=ROOT/'static'/primary.replace('/assets/','')
  if p.exists(): seen.add(digest(p))
 for item in data.get('gallery') or []:
  ref=item.get('image'); p=ROOT/'static'/(ref or '').replace('/assets/','')
  if not ref or not p.exists(): continue
  h=digest(p)
  if h in seen: continue
  seen.add(h); gallery.append(item)
 for p in sorted(PHOTOS.glob(f'{slug}*')):
  if len(gallery)>=target-1: break
  if not p.is_file(): continue
  h=digest(p)
  if h in seen: continue
  seen.add(h); gallery.append({'image':f'/assets/photos/{p.name}','author':'RentUp verified local asset','license':'Site-owned or previously verified source','license_url':'','source':'https://rentup.ge/'})
 text=path.read_text(encoding='utf-8'); block=yaml.safe_dump({'gallery':gallery[:target-1]},allow_unicode=True,sort_keys=False,width=1000).rstrip()
 text,n=re.subn(r'gallery:(?: \[\])?\n.*?(?=visit_hours:)',block+'\n',text,count=1,flags=re.S)
 if n!=1: raise RuntimeError(slug)
 path.write_text(text,encoding='utf-8')
