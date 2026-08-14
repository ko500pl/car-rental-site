# -*- coding: utf-8 -*-
"""OG-სურათების გენერაცია (1200×630) — ერთხელ გასაშვები სკრიპტი."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import yaml
_S = yaml.safe_load(open('content/settings/site.yml', encoding='utf-8'))
RENTAL_BRAND = _S['rental_brand']
LANGS = ['ka', 'en', 'ru', 'fa', 'he', 'ar']

TXT = {
 "ka": ("ავტომობილების გაქირავება საქართველოში",
        "ავტოპარკი · მარშრუტები · თბილისი · ქუთაისი · ბათუმი"),
 "en": ("Car Rental in Georgia",
        "Fleet · road-trip routes · Tbilisi · Kutaisi · Batumi"),
 "ru": ("Аренда автомобилей в Грузии",
        "Автопарк · цены · маршруты · Тбилиси · Кутаиси · Батуми"),
 "fa": ("اجاره خودرو در گرجستان", "ناوگان · قیمت‌ها · مسیرها · تفلیس · کوتایسی · باتومی"),
 "he": ("השכרת רכב בגאורגיה", "צי רכב · מחירים · מסלולים · טביליסי · קוטאיסי · בטומי"),
 "ar": ("تأجير السيارات في جورجيا", "الأسطول · الأسعار · المسارات · تبليسي · كوتايسي · باتومي"),
}

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@400;600;700&family=Noto+Sans:wght@400;600;700&display=swap">
<style>
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;display:flex;flex-direction:column;justify-content:space-between;
padding:70px 78px;font-family:"Noto Sans Georgian","Noto Sans",sans-serif;
background:linear-gradient(165deg,#0f4c81 0%,#0a3459 62%,#08283f 100%);color:#fff}}
.brand{{display:flex;align-items:center;gap:14px;font-size:34px;font-weight:700;letter-spacing:-.5px}}
.dot{{width:16px;height:16px;border-radius:50%;background:#c8963e}}
h1{{font-size:{fs}px;line-height:1.16;font-weight:700;letter-spacing:-1px;max-width:16ch}}
p{{font-size:27px;color:#a9c8e2;font-weight:400}}
.bar{{height:8px;width:150px;background:#c8963e;border-radius:4px;margin-bottom:26px}}
</style></head><body>
<div class="brand"><span class="dot"></span>{brand}</div>
<div><div class="bar"></div><h1>{title}</h1></div>
<p>{sub}</p>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for l in LANGS:
        t, s = TXT[l]
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        pg.set_content(TPL.format(brand=RENTAL_BRAND, title=t, sub=s,
                                  fs=62 if len(t) > 30 else 74), wait_until="networkidle")
        pg.wait_for_timeout(700)
        pg.screenshot(path=f"static/og-{l}.png")
        pg.close()
    b.close()
print("OG images written to static/")
