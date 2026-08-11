#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dist/ → preview/ — ბმულებს ფარდობითში გადაიყვანს, რომ საიტი
სერვერის გარეშე, ფაილის ორმაგი დაწკაპუნებით გაიხსნას (file://).

გამოყენება:  python3 build.py dist && python3 make_preview.py
ეს ვერსია მხოლოდ ლოკალური დათვალიერებისთვისაა — ჰოსტინგზე dist/ იტვირთება.
"""
import os, re, shutil, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "dist"
OUT = sys.argv[2] if len(sys.argv) > 2 else "preview"

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)

ATTR = re.compile(r'(?P<a>href|src)="(?P<u>/[^"]*)"')
# რუკის JSON-ში ჩაწერილი ბმულები: "u": "/attractions/x/"
JSONU = re.compile(r'"u":\s*"(?P<u>/[^"]*)"')


def fix(html, depth):
    prefix = "../" * depth if depth else ""

    def rep(m):
        u = m.group("u")
        if u == "/":
            t = "index.html"
        elif u.endswith("/"):
            t = u.lstrip("/") + "index.html"
        else:
            t = u.lstrip("/")
        return f'{m.group("a")}="{prefix}{t}"'

    def rep2(m):
        u = m.group("u")
        t = "index.html" if u == "/" else (
            u.lstrip("/") + "index.html" if u.endswith("/") else u.lstrip("/"))
        return f'"u": "{prefix}{t}"'

    return JSONU.sub(rep2, ATTR.sub(rep, html))


n = 0
for root, _, files in os.walk(OUT):
    for f in files:
        if not f.endswith(".html"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, OUT)
        depth = len(rel.split(os.sep)) - 1
        with open(p, encoding="utf-8") as fh:
            h = fh.read()
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(fix(h, depth))
        n += 1

# ინსტრუქცია საქაღალდეში
with open(os.path.join(OUT, "_როგორ-ვნახო.txt"), "w", encoding="utf-8") as fh:
    fh.write(
        "საიტის სანახავად უბრალოდ გახსენით ფაილი  index.html  (ორმაგი დაწკაპუნებით).\n\n"
        "ეს ვერსია მხოლოდ ლოკალური დათვალიერებისთვისაა — ბმულები ფარდობითია.\n"
        "ჰოსტინგზე ასატვირთად გამოიყენეთ dist/ საქაღალდე, არა ეს.\n\n"
        "რას ნახავთ:\n"
        "  index.html                      — მთავარი (ქართული)\n"
        "  map/index.html                  — რუკა მარშრუტებით\n"
        "  attractions/vardzia/index.html  — ღირსშესანიშნაობის გვერდი\n"
        "  routes/svaneti-expedition/index.html — მარშრუტი\n"
        "  ar/index.html                   — არაბული (RTL)\n\n"
        "რუკის ფონი (OpenStreetMap) ინტერნეტს საჭიროებს.\n"
        "ადმინი (/admin/) ლოკალურად ვერ იმუშავებს — GitHub-ს უკავშირდება.\n")

print(f"✔ {n} გვერდი → ./{OUT}  (გახსენით {OUT}/index.html)")
