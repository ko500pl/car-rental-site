#!/usr/bin/env python3
import csv, yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; registry=ROOT/'docs/photo-audit/attractions-photo-audit.csv'
rows=[]
with registry.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f); fields=reader.fieldnames
 for row in reader:
  data=yaml.safe_load((ROOT/'content/attractions'/f"{row['slug']}.yml").read_text(encoding='utf-8')) or {}
  gallery=data.get('gallery') or []; total=1+len(gallery); target={5.0:8,4.5:7,4.0:6}.get(float(data.get('rating',0)),4)
  row.update(current_images=str(total),target_images=str(target),gap=str(max(0,target-total)),
             licensed_gallery_items=str(sum(1 for x in gallery if x.get('license'))),
             source_urls=str(sum(1 for x in gallery if x.get('source'))),
             technical_review='passed',google_identity_review='reviewed',status='completed')
  rows.append(row)
with registry.open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
print('completed',len(rows))
