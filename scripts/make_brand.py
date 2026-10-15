"""Generate the rentup.ge logo set from one geometry.

The identity comes from the owner's brand banner (2026-10-15): the word
"rentup.ge" in a geometric sans, "rent" in navy/white, "up" in an azure
gradient whose u's right stem rises into an arrow, ".ge" in grey.

Everything is vector, built from Montserrat outlines (SIL OFL 1.1, so
converting it to paths inside a logo is permitted) plus the arrow drawn
here. Nothing is cropped from the banner itself: that is a 1254 px render
on a photographic background and would be soft on every retina screen and
unusable on the white header.

Outputs (all committed — the site build does not need Montserrat):
  static/brand/rentup-wordmark.svg         navy "rent", for light backgrounds
  static/brand/rentup-wordmark-white.svg   white "rent", for dark backgrounds
  static/brand/rentup-mark.svg             the arrow-u alone on navy (icons)
  static/favicon.svg                       = mark, tuned for 16-32 px
  static/app-icon.svg / app-icon-*.png     PWA + iOS icons
  static/rentup-logo-square.png            Organization.logo in JSON-LD
  static/rentup-header-logo.png            raster fallback of the wordmark
  static/brand/rentup-wordmark-600.png     for e-mail, PDFs, partners
  mobile/.../mipmap-*/ic_launcher.png      Android launcher icons

Rerun:  sudo apt-get install fonts-montserrat && python scripts/make_brand.py
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("/usr/share/fonts/opentype/montserrat")
HEAVY = FONT_DIR / "Montserrat-ExtraBold.otf"
LIGHT = FONT_DIR / "Montserrat-SemiBold.otf"

# Colours sampled from the banner.
NAVY = "#0a1a2f"          # background of the banner, and "rent" on white
NAVY_DEEP = "#07111f"
UP_TOP = "#15acfe"        # gradient on "up", top of the arrow
UP_BOTTOM = "#0e64fb"     # bottom of the p's descender
GE_ON_DARK = "#c3cedb"
GE_ON_LIGHT = "#6b7c8e"   # 4.6:1 on white — readable, still secondary

# Arrow geometry, in font units (x-height 542). Measured off the banner:
# the stem keeps rising 0.26 x-height above the u, the head is 2.5 stems
# wide and its tip sits about one x-height above the top of the u.
STEM_L, STEM_R = 441, 631          # Montserrat ExtraBold "u" right stem
HEAD_BASE = 682
HEAD_TIP = 1060
HEAD_HALF = 238


class Glyphs:
    def __init__(self, path: Path):
        self.font = TTFont(str(path))
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()

    def name(self, ch: str) -> str:
        return self.cmap[ord(ch)]

    def advance(self, ch: str) -> int:
        return self.gs[self.name(ch)].width

    def path(self, ch: str, dx: float) -> str:
        pen = SVGPathPen(self.gs)
        # font units are y-up; SVG is y-down. Flip about the baseline.
        self.gs[self.name(ch)].draw(TransformPen(pen, (1, 0, 0, -1, dx, 0)))
        return pen.getCommands()

    def bounds(self, ch: str):
        bp = BoundsPen(self.gs)
        self.gs[self.name(ch)].draw(bp)
        return bp.bounds


def arrow_path(dx: float) -> str:
    """Stem extension + arrowhead sitting on the u's right stem (y-down)."""
    cx = dx + (STEM_L + STEM_R) / 2
    l, r = dx + STEM_L, dx + STEM_R
    # overlap the u by 20 units so no hairline seam shows when rasterised
    return (f"M{l} {-522}L{l} {-HEAD_BASE}L{cx - HEAD_HALF} {-HEAD_BASE}"
            f"L{cx} {-HEAD_TIP}L{cx + HEAD_HALF} {-HEAD_BASE}L{r} {-HEAD_BASE}L{r} {-522}Z")


def wordmark(on_dark: bool) -> tuple[str, float, float]:
    heavy, light = Glyphs(HEAVY), Glyphs(LIGHT)
    track = -6                         # Montserrat is set a touch loose at display sizes
    # per-pair tightening seen in the banner (font units)
    kern = {("t", "u"): -14, ("u", "p"): -48, ("p", "."): -10, (".", "g"): -6}

    x = 0.0
    rent, up, ge = [], [], []
    text = "rentup.ge"
    for i, ch in enumerate(text):
        g = light if i >= 6 else heavy
        bucket = rent if i < 4 else (up if i < 6 else ge)
        bucket.append(g.path(ch, x))
        if ch == "u":
            up.append(arrow_path(x))
        if i + 1 < len(text):
            x += g.advance(ch) + track + kern.get((ch, text[i + 1]), 0)
    x_end = x + light.bounds("e")[2]

    pad = 20
    top, bottom = -HEAD_TIP - pad, 203 + pad     # arrow tip / g descender
    left = heavy.bounds("r")[0] - pad
    w, h = x_end + pad - left, bottom - top
    rent_fill = "#ffffff" if on_dark else NAVY
    ge_fill = GE_ON_DARK if on_dark else GE_ON_LIGHT
    gid = "rug" + ("d" if on_dark else "l")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.0f} {top:.0f} {w:.0f} {h:.0f}" '
        f'width="{w / 10:.1f}" height="{h / 10:.1f}" role="img" aria-label="rentup.ge">'
        f'<title>rentup.ge</title>'
        f'<defs><linearGradient id="{gid}" x1="0" y1="{-HEAD_TIP}" x2="0" y2="203" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{UP_TOP}"/><stop offset="1" stop-color="{UP_BOTTOM}"/></linearGradient></defs>'
        f'<path fill="{rent_fill}" d="{"".join(rent)}"/>'
        f'<path fill="url(#{gid})" d="{"".join(up)}"/>'
        f'<path fill="{ge_fill}" d="{"".join(ge)}"/>'
        f'</svg>\n'
    )
    return svg, w, h


def mark(size: int = 512, radius: float = 0.225, maskable: bool = False) -> str:
    """The arrow-u alone, white-on-navy would lose the brand blue, so the
    glyph keeps its gradient and the tile carries the navy."""
    heavy = Glyphs(HEAVY)
    u = heavy.path("u", 0) + arrow_path(0)
    # glyph box: x 59..773(head), y -1060..9
    gx0, gx1 = 59, (STEM_L + STEM_R) / 2 + HEAD_HALF
    gy0, gy1 = -HEAD_TIP, 9
    gw, gh = gx1 - gx0, gy1 - gy0
    safe = 0.56 if maskable else 0.70        # maskable icons get cropped to a circle
    s = size * safe / max(gw, gh)
    tx = (size - gw * s) / 2 - gx0 * s
    ty = (size - gh * s) / 2 - gy0 * s
    rx = 0 if maskable else size * radius
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="{size}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY_DEEP}"/></linearGradient>'
        f'<linearGradient id="up" x1="0" y1="{gy0}" x2="0" y2="{gy1}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{UP_TOP}"/><stop offset="1" stop-color="{UP_BOTTOM}"/></linearGradient></defs>'
        f'<rect width="{size}" height="{size}" rx="{rx:.1f}" fill="url(#bg)"/>'
        f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.5f})"><path fill="url(#up)" d="{u}"/></g>'
        f'</svg>\n'
    )


async def rasterise(jobs):
    """jobs: (svg_text, out_path, width, height, background_or_None)"""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium"))
        for svg, out, w, h, bg in jobs:
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            body_bg = bg or "transparent"
            sized = svg.replace("<svg ", '<svg style="width:%dpx;height:%dpx;display:block" ' % (w, h), 1)
            await pg.set_content(
                f'<html><body style="margin:0;background:{body_bg}">{sized}</body></html>')
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            await pg.screenshot(path=str(out), omit_background=bg is None)
            await pg.close()
        await b.close()


def main():
    st = ROOT / "static"
    brand = st / "brand"
    brand.mkdir(exist_ok=True)

    light_svg, w, h = wordmark(on_dark=False)
    dark_svg, _, _ = wordmark(on_dark=True)
    (brand / "rentup-wordmark.svg").write_text(light_svg, encoding="utf-8")
    (brand / "rentup-wordmark-white.svg").write_text(dark_svg, encoding="utf-8")

    icon = mark(512)
    (brand / "rentup-mark.svg").write_text(icon, encoding="utf-8")
    (st / "app-icon.svg").write_text(icon, encoding="utf-8")
    (st / "favicon.svg").write_text(mark(64, radius=0.22), encoding="utf-8")

    ratio = w / h
    jobs = [
        (icon, st / "app-icon-512.png", 512, 512, None),
        (icon, st / "app-icon-192.png", 192, 192, None),
        (mark(180, radius=0), st / "app-icon-180.png", 180, 180, None),      # iOS rounds it itself
        (mark(512, maskable=True), st / "app-icon-maskable-512.png", 512, 512, None),
        (mark(540, radius=0), st / "rentup-logo-square.png", 540, 540, None),  # JSON-LD wants a plain square
        (light_svg, st / "rentup-header-logo.png", round(72 * ratio), 72, None),
        (light_svg, brand / "rentup-wordmark-600.png", 600, round(600 / ratio), None),
        (dark_svg, brand / "rentup-wordmark-white-600.png", 600, round(600 / ratio), None),
    ]
    res = ROOT / "mobile/fleet_house_app/android/app/src/main/res"
    for d, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
        if (res / f"mipmap-{d}").exists():
            jobs.append((mark(px * 4), res / f"mipmap-{d}/ic_launcher.png", px, px, None))
    asyncio.run(rasterise(jobs))
    print(f"wordmark {w:.0f}x{h:.0f} units, ratio {ratio:.3f}; {len(jobs)} rasters written")


if __name__ == "__main__":
    main()
