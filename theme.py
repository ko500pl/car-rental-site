# -*- coding: utf-8 -*-
"""CSS გენერაცია content/settings/design.yml-ის მიხედვით."""


def css(d):
    hero_bg = {
        "gradient": ("linear-gradient(165deg,{b} 0%,{i} 62%,#08283f 100%)"
                     .format(b=d["color_brand"], i=d["color_brand_ink"])),
        "solid": d["color_brand_ink"],
        "image": ("linear-gradient(rgba(8,40,63,{o}),rgba(8,40,63,{o})),url('{u}') center/cover"
                  .format(o=d.get("hero_overlay", "0.62"), u=d.get("hero_image") or "")),
    }.get(d.get("hero_style", "gradient"), "")

    dark = str(d.get("theme", "dark")).lower() == "dark"
    mixb = "#000000" if dark else "#ffffff"
    ink3 = ("color-mix(in srgb,{i2} 78%,{m})".format(i2=d['color_ink_2'], m=mixb))
    grad = ("linear-gradient(100deg,{a} 0%,{b} 100%)"
            .format(a=d['color_brand'], b=d.get('color_accent_2', d['color_brand_2'])))

    return f""":root{{
  --ink:{d['color_ink']};
  --ink-2:{d['color_ink_2']};
  --ink-3:{ink3};
  --line:{d['color_line']};
  --line-2:color-mix(in srgb,{d['color_line']} 62%,{mixb});
  --bg:{d['color_bg']};
  --bg-2:{d['color_bg_2']};
  --bg-3:{d.get('color_bg_3', d['color_bg_2'])};
  --surface:{d['color_bg_2']};
  --surface-2:{d.get('color_bg_3', d['color_bg_2'])};
  --mixb:{mixb};
  --brand:{d['color_brand']};
  --brand-2:{d['color_brand_2']};
  --brand-ink:{d['color_brand_ink']};
  --accent:{d['color_accent']};
  --accent-2:{d.get('color_accent_2', d['color_brand_2'])};
  --grad:{grad};
  --on-brand:{d.get('color_on_brand', '#ffffff')};
  --ok:{d['color_ok']};
  --radius:{d['radius']}px;
  --maxw:{d['max_width']}px;
  --font:{d['font_family']};
  --mono:{d.get('font_mono', 'ui-monospace,Consolas,monospace')};
}}

*,*::before,*::after{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;font-family:var(--font);color:var(--ink);background:var(--bg);
  font-size:{d['base_font_size']}px;line-height:1.62;font-weight:400;
  text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;height:auto;display:block}}
a{{color:var(--brand-2);text-decoration:none}}
a:hover{{text-decoration:underline}}
a:focus-visible{{outline:3px solid var(--accent);outline-offset:2px;border-radius:3px}}

.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 20px}}
.skip{{position:absolute;inset-inline-start:-9999px}}
.skip:focus{{inset-inline-start:12px;top:12px;z-index:99;background:var(--surface);padding:10px 16px;border:2px solid var(--brand);border-radius:6px}}

/* Header */
.site-head{{border-bottom:1px solid var(--line);background:var(--surface);position:sticky;top:0;z-index:20}}
.head-in{{display:flex;align-items:center;gap:16px;flex-wrap:nowrap;padding:14px 20px;max-width:var(--maxw);margin:0 auto}}
.logo{{display:flex;align-items:center;gap:8px;font-weight:700;font-size:20px;color:var(--brand-ink);letter-spacing:-.2px}}
.logo:hover{{text-decoration:none}}
.logo img{{height:{d['logo_height']}px;width:auto}}
.logo .dot{{width:9px;height:9px;border-radius:50%;background:var(--accent)}}
.logo small{{font-weight:500;font-size:12px;color:var(--ink-3);letter-spacing:.06em;text-transform:uppercase}}
nav.main{{margin-inline-start:auto}}
nav.main ul{{display:flex;flex-wrap:wrap;gap:2px;list-style:none;margin:0;padding:0}}
nav.main a{{display:block;padding:7px 10px;border-radius:7px;color:var(--ink-2);font-size:15px;font-weight:500}}
nav.main a:hover{{background:var(--bg-3);color:var(--brand-ink);text-decoration:none}}
nav.main a[aria-current="page"]{{background:var(--brand);color:var(--on-brand)}}
.nav-more{{position:relative}}
.nav-more details{{position:relative}}
.nav-more summary{{list-style:none;cursor:pointer;padding:7px 12px;border-radius:9px;color:var(--ink-2);font-weight:800;letter-spacing:.12em}}
.nav-more summary::-webkit-details-marker{{display:none}}
.nav-more summary:hover,.nav-more details[open] summary{{background:var(--bg-3);color:var(--brand-ink)}}
.nav-more details>ul{{position:absolute;inset-inline-end:0;top:calc(100% + 8px);min-width:190px;padding:8px!important;background:var(--surface);border:1px solid var(--line);border-radius:12px;box-shadow:0 18px 45px rgba(0,0,0,.25);display:block!important;z-index:50}}
.nav-more details>ul li{{display:block}}
.nav-more details>ul a{{white-space:nowrap}}
.langs{{display:flex;gap:4px;align-items:center;border-inline-start:1px solid var(--line);padding-inline-start:12px}}
.langs a{{font-size:13px;font-weight:600;color:var(--ink-3);padding:5px 8px;border-radius:6px}}
.langs a:hover{{background:var(--bg-3);text-decoration:none}}
.langs a.on{{background:var(--bg-3);color:var(--brand-ink)}}
.head-tel{{font-size:15px;font-weight:600;color:var(--brand-ink);white-space:nowrap}}

/* Hero */
.hero{{background:{hero_bg};color:#fff;padding:64px 0 58px}}
.hero h1{{margin:0 0 16px;font-size:clamp(29px,4.4vw,46px);line-height:1.22;letter-spacing:-.4px;font-weight:700;max-width:20ch}}
.hero .lead{{font-size:clamp(17px,2vw,20px);line-height:1.66;color:#d3e2f0;max-width:66ch;margin:0 0 26px}}
.hero .kicker{{display:inline-block;font-size:12.5px;letter-spacing:.13em;text-transform:uppercase;color:#8fc0e8;font-weight:600;margin-bottom:14px}}
.hero-facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:14px;margin-top:34px;padding-top:28px;border-top:1px solid rgba(255,255,255,.18)}}
.hero-facts b{{display:block;font-size:26px;font-weight:700;color:#fff;line-height:1.25}}
.hero-facts span{{font-size:14px;color:#a9c8e2}}

/* Sections */
.sec{{padding:48px 0;border-bottom:1px solid var(--line-2)}}
.sec:last-of-type{{border-bottom:0}}
.sec.alt{{background:var(--bg-2)}}
h1{{font-size:clamp(27px,3.6vw,40px);line-height:1.24;letter-spacing:-.3px;margin:0 0 18px;font-weight:700}}
h2{{font-size:clamp(21px,2.5vw,28px);line-height:1.32;letter-spacing:-.2px;margin:38px 0 14px;font-weight:700;color:var(--brand-ink)}}
h2:first-child{{margin-top:0}}
h3{{font-size:18px;line-height:1.42;margin:26px 0 8px;font-weight:700;color:var(--ink)}}
p{{margin:0 0 15px;max-width:74ch}}
ul,ol{{margin:0 0 16px;padding-inline-start:22px;max-width:74ch}}
li{{margin:0 0 7px}}
strong{{font-weight:700;color:var(--ink)}}
.page-head{{padding:40px 0 8px}}
.page-head .lead{{font-size:19px;color:var(--ink-2);max-width:70ch}}

.crumbs{{font-size:14px;color:var(--ink-3);padding:14px 0 0}}
.crumbs ol{{list-style:none;display:flex;flex-wrap:wrap;gap:7px;margin:0;padding:0}}
.crumbs li+li::before{{content:"›";margin-inline-end:7px;color:var(--line)}}

/* Tables */
.tbl-wrap{{overflow-x:auto;margin:0 0 22px;border:1px solid var(--line);border-radius:var(--radius)}}
table{{border-collapse:collapse;width:100%;font-size:15.5px;background:var(--surface)}}
caption{{text-align:start;font-size:14px;color:var(--ink-3);padding:12px 14px;border-bottom:1px solid var(--line);background:var(--bg-2);font-weight:500}}
th,td{{padding:11px 14px;text-align:start;border-bottom:1px solid var(--line-2);vertical-align:top}}
thead th{{background:var(--bg-3);color:var(--brand-ink);font-weight:700;font-size:14px;white-space:nowrap}}
tbody tr:last-child td{{border-bottom:0}}
tbody tr:nth-child(even){{background:color-mix(in srgb,var(--bg-2) 45%,var(--mixb))}}
td:first-child{{font-weight:600;color:var(--ink)}}

/* Cards */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:18px;margin:6px 0 24px}}
.card{{border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;background:var(--surface)}}
.card h3{{margin:0 0 8px;font-size:17.5px;color:var(--brand-ink)}}
.card p{{font-size:15.5px;color:var(--ink-2);margin:0 0 12px}}
.card ul{{font-size:15px;margin:0;padding-inline-start:19px;color:var(--ink-2)}}
.card .tag{{display:inline-block;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--brand-2);background:var(--bg-3);padding:3px 9px;border-radius:20px;margin-bottom:10px}}
.card .price{{font-size:15px;font-weight:700;color:var(--ok);margin-top:12px;display:block}}

/* Car cards */
.cars{{display:grid;grid-template-columns:repeat(auto-fit,minmax(288px,1fr));gap:20px;margin:8px 0 26px}}
.car{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:var(--surface);display:flex;flex-direction:column}}
.car .ph{{aspect-ratio:16/10;background:var(--bg-3);display:flex;align-items:center;justify-content:center;color:var(--ink-3);font-size:13px}}
.car .ph img{{width:100%;height:100%;object-fit:cover}}
.car .in{{padding:18px 20px 20px;display:flex;flex-direction:column;flex:1}}
.car h3{{margin:0 0 4px;font-size:18px;color:var(--brand-ink)}}
.car h3 a{{color:inherit}}
.car .sub{{font-size:14px;color:var(--ink-3);margin:0 0 12px}}
.car ul{{font-size:14.5px;margin:0 0 14px;padding-inline-start:18px;color:var(--ink-2)}}
.car .foot{{margin-top:auto;display:flex;align-items:baseline;justify-content:space-between;gap:10px;padding-top:12px;border-top:1px solid var(--line-2)}}
.car .p{{font-size:17px;font-weight:700;color:var(--ok)}}
.car .p small{{font-size:13px;font-weight:500;color:var(--ink-3)}}
.car .more{{font-size:14.5px;font-weight:600}}

/* Car detail */
.cardetail{{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:32px;align-items:start}}
.cardetail .gal img{{border-radius:var(--radius);border:1px solid var(--line);margin-bottom:12px}}
.cardetail .ph{{aspect-ratio:16/10;background:var(--bg-3);border:1px solid var(--line);border-radius:var(--radius);display:flex;align-items:center;justify-content:center;color:var(--ink-3);font-size:14px}}
.spec{{width:100%;font-size:15.5px}}
.spec th{{width:48%;font-weight:500;color:var(--ink-3);background:none}}
.pricebox{{border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;background:var(--bg-2);margin:0 0 18px}}
.pricebox .big{{font-size:30px;font-weight:700;color:var(--brand-ink);line-height:1.2}}
.pricebox .big small{{font-size:15px;font-weight:500;color:var(--ink-3)}}

/* Facts */
.facts{{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:var(--line);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;margin:6px 0 26px}}
.facts div{{background:var(--surface);padding:16px 18px}}
.facts dt,.facts .k{{font-size:13px;color:var(--ink-3);margin-bottom:3px}}
.facts dd,.facts .v{{font-size:17px;font-weight:700;color:var(--brand-ink);margin:0}}

/* FAQ */
.faq{{margin:0 0 10px;max-width:80ch}}
.faq .qa{{border-top:1px solid var(--line);padding:20px 0}}
.faq .qa:last-child{{border-bottom:1px solid var(--line)}}
.faq h3{{margin:0 0 7px;font-size:17.5px;color:var(--brand-ink);font-weight:700}}
.faq p{{margin:0;color:var(--ink-2);font-size:16px}}

/* Blog */
.posts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px;margin:8px 0 20px}}
.post-c{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:var(--surface);display:flex;flex-direction:column}}
.post-c .ph{{aspect-ratio:16/9;background:var(--bg-3)}}
.post-c .ph img{{width:100%;height:100%;object-fit:cover}}
.post-c .in{{padding:18px 20px 20px}}
.post-c time{{font-size:13px;color:var(--ink-3);letter-spacing:.03em}}
.post-c h2{{font-size:19px;margin:6px 0 8px;color:var(--brand-ink)}}
.post-c h2 a{{color:inherit}}
.post-c p{{font-size:15.5px;color:var(--ink-2);margin:0}}
.article{{max-width:74ch}}
.article h2{{font-size:25px;margin:34px 0 12px}}
.article h3{{font-size:19px;margin:24px 0 8px}}
.article table{{font-size:15px}}
.article .tbl-wrap,.article table{{margin-bottom:20px}}
.meta-line{{font-size:14.5px;color:var(--ink-3);margin:0 0 22px}}

/* Notes / CTA */
.note{{border-inline-start:4px solid var(--accent);background:color-mix(in srgb,{d['color_accent']} 9%,var(--mixb));padding:14px 18px;border-radius:0 8px 8px 0;margin:0 0 22px;font-size:15.5px;color:var(--ink-2);max-width:74ch}}
.note strong{{color:var(--brand-ink)}}
.cta{{background:var(--bg-3);border:1px solid var(--line);border-radius:var(--radius);padding:26px 28px;margin:30px 0 0}}
.cta h2{{margin:0 0 8px;font-size:22px}}
.cta p{{margin:0 0 6px;color:var(--ink-2)}}
.cta .row{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
.btn{{display:inline-block;background:var(--brand);color:var(--on-brand);padding:11px 22px;border-radius:8px;font-weight:600;font-size:15.5px}}
.btn:hover{{background:var(--brand-2);text-decoration:none}}
.btn.ghost{{background:var(--surface);color:var(--brand-ink);border:1px solid var(--line)}}
.btn.ghost:hover{{background:var(--bg-2)}}

/* Footer */
.site-foot{{background:{d['color_brand_ink']};color:#a9c0d4;padding:18px 0 12px;font-size:13px;margin-top:20px}}
.foot-compact{{display:flex;align-items:center;justify-content:space-between;gap:14px 28px;flex-wrap:wrap}}
.foot-compact nav,.foot-contact{{display:flex;align-items:center;gap:10px 20px;flex-wrap:wrap}}
.foot-compact nav a{{font-weight:700;color:#e4eef7}}
.foot-contact span{{color:#8fa7bd}}
.foot-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:28px}}
.site-foot h2{{color:#fff;font-size:14px;letter-spacing:.09em;text-transform:uppercase;margin:0 0 12px;font-weight:600}}
.site-foot ul{{list-style:none;margin:0;padding:0}}
.site-foot li{{margin:0 0 7px}}
.site-foot a{{color:#cfe0ef}}
.site-foot p{{color:#8fa7bd;font-size:14.5px;margin:0 0 8px}}
.foot-bottom{{border-top:1px solid rgba(255,255,255,.1);margin-top:12px;padding-top:9px;font-size:12px;color:#7f97ad;display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between}}

/* Map */
.gmap{{width:100%;border:1px solid var(--line);border-radius:var(--radius);margin:0 0 10px;z-index:1}}
.map-hint{{font-size:14.5px;color:var(--ink-3);margin:0 0 18px}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;font-size:14px;color:var(--ink-2);
  border:1px solid var(--line);border-radius:var(--radius);padding:14px 18px;background:var(--surface)}}
.legend b{{color:var(--brand-ink)}}
.lg{{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}}
.lg i{{width:11px;height:11px;border-radius:50%;display:inline-block;border:2px solid #fff;
  box-shadow:0 0 0 1px var(--line)}}
.leaflet-popup-content{{font-family:var(--font);font-size:14px;line-height:1.55}}
.leaflet-popup-content b a{{color:var(--brand-ink)}}
.leaflet-container{{font-family:var(--font)}}

/* ── interactive explorer ───────────────────────────────────────── */
.wrap.wide{{max-width:1560px}}
.vh{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
.map-sub{{color:var(--ink-2);margin:0 0 14px;max-width:70ch}}
.explorer{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:var(--surface)}}
.expbar{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 14px;
  border-bottom:1px solid var(--line);background:var(--bg-2)}}
.expsearch{{flex:1 1 240px;min-width:180px}}
.expbar input,.expbar select{{font:inherit;font-size:15px;padding:9px 12px;border:1px solid var(--line);
  border-radius:10px;background:var(--surface);color:var(--ink)}}
.expcount{{font-size:14px;color:var(--ink-3);margin-inline-start:auto}}
.expgrid{{display:grid;grid-template-columns:352px 1fr;height:var(--exph,72vh);min-height:520px}}
.expside{{border-inline-end:1px solid var(--line);display:flex;flex-direction:column;min-height:0;
  background:var(--bg-2)}}
.exproutebox{{padding:12px 14px;border-bottom:1px solid var(--line);background:var(--surface)}}
.exppair{{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:end}}
.exppair label{{position:relative;font-size:12.5px;color:var(--ink-3);display:block}}
.exppair input{{width:100%;font:inherit;font-size:14.5px;padding:8px 10px;margin-top:4px;
  border:1px solid var(--line);border-radius:9px;background:var(--surface);color:var(--ink)}}
.expsug{{display:none;position:absolute;z-index:600;inset-inline-start:0;top:100%;width:260px;
  background:var(--surface);border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 30px rgba(0,0,0,.14);
  max-height:250px;overflow:auto}}
.expsug.on{{display:block}}
.expsug button{{display:block;width:100%;text-align:start;padding:8px 11px;border:0;background:none;
  font:inherit;font-size:14px;cursor:pointer;color:var(--ink)}}
.expsug button:hover{{background:var(--bg-2)}}
.expsug small{{display:block;color:var(--ink-3);font-size:12px}}
.expslider{{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ink-3);margin-top:10px}}
.expslider input{{flex:1}}
.exprouteout{{margin-top:10px;font-size:14px}}
.exptot{{display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;padding:8px 10px;border-radius:9px;
  background:var(--bg-2);margin-bottom:8px}}
.exptot b{{color:var(--brand-ink);font-size:17px}}
.exptot span{{font-size:13px;color:var(--ink-2)}}
.expstops{{margin:0 0 10px;padding-inline-start:20px}}
.expstops{{list-style:none;padding:0}}
.expstops li{{margin:0 0 6px}}
.expchk{{display:flex;gap:8px;align-items:flex-start;cursor:pointer}}
.expchk input{{margin-top:3px;flex:none}}
.expdays{{font-weight:600;color:var(--brand-ink)}}
.muted.sm{{font-size:12.5px;margin:0 0 10px}}
.expmeta{{display:block;font-size:12.5px;color:var(--ink-3)}}
.lnk{{border:0;background:none;padding:0;font:inherit;color:var(--brand-ink);cursor:pointer;
  text-decoration:underline;text-align:start}}
.explist{{flex:1;overflow:auto;min-height:0;padding:6px}}
.expitem{{display:block;width:100%;text-align:start;border:0;background:none;padding:9px 10px;
  border-radius:9px;cursor:pointer;font:inherit;color:var(--ink);position:relative}}
.expitem:hover{{background:var(--surface)}}
.expitem i{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-inline-end:8px;
  border:2px solid #fff;box-shadow:0 0 0 1px var(--line)}}
.expitem-n{{font-weight:600;font-size:14.5px}}
.expitem-m{{display:block;font-size:12.5px;color:var(--ink-3);margin-inline-start:19px}}
.expmapwrap{{position:relative;min-height:0}}
.expmap{{position:absolute;inset:0;z-index:1}}
.exppanel{{position:absolute;top:0;bottom:0;inset-inline-end:0;width:min(460px,92%);background:var(--surface);
  border-inline-start:1px solid var(--line);z-index:500;overflow:auto;padding:20px 22px 40px;
  transform:translateX(103%);transition:transform .22s ease;box-shadow:-14px 0 40px rgba(0,0,0,.10)}}
[dir="rtl"] .exppanel{{transform:translateX(-103%)}}
.exppanel.on{{transform:none}}
.exppanel h3{{margin:0 26px 10px 0;font-size:23px;color:var(--brand-ink)}}
[dir="rtl"] .exppanel h3{{margin:0 0 10px 26px}}
.exppanel h4{{margin:18px 0 6px;font-size:16px;color:var(--brand-ink)}}
.exppanel .article{{font-size:15px}}
.expclose{{position:absolute;top:12px;inset-inline-end:14px;border:1px solid var(--line);
  background:var(--surface);border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:14px;color:var(--ink-2)}}
.exptags{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}}
.exptags .tag{{background:var(--brand);color:var(--on-brand);border-radius:999px;padding:4px 11px;font-size:12.5px;
  font-weight:600;display:inline-block}}
.exptags .tag.u{{background:#7d5ba6;color:var(--on-brand)}}
.exptags .tag.g{{background:var(--bg-2);color:var(--ink-2);border:1px solid var(--line)}}
.expact{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}}
.chips{{display:flex;gap:7px;flex-wrap:wrap}}
.chip{{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 12px;font:inherit;
  font-size:13.5px;cursor:pointer;color:var(--ink-2)}}
.chip:hover{{border-color:var(--brand);color:var(--brand-ink)}}
.btn.sm{{padding:8px 14px;font-size:14px}}
.hero.tight{{padding:30px 0 26px}}
.hero.tight h1{{font-size:clamp(25px,3vw,34px);margin:0 0 8px;max-width:28ch}}
.hero.tight .lead{{font-size:clamp(15.5px,1.4vw,17.5px);margin:0;max-width:78ch;line-height:1.55}}
.hero.tight .kicker{{margin-bottom:8px}}
.maphero{{padding:16px 0 26px}}
.maphero .map-sub{{margin:0 0 12px}}
.sec.wide{{padding-top:18px}}
.hero-facts{{margin-top:0;padding-top:0;border-top:0}}
.sec .hero-facts b{{color:var(--brand-ink)}}
.sec .hero-facts span{{color:var(--ink-3)}}
.sec .hero-facts{{border-top:1px solid var(--line);padding-top:22px}}
@media(max-width:1000px){{
  .expgrid{{grid-template-columns:1fr;height:auto}}
  .expside{{border-inline-end:0;border-bottom:1px solid var(--line)}}
  .explist{{max-height:320px}}
  .expmapwrap{{height:64vh;min-height:420px}}
  .exppanel{{width:100%}}
}}

/* RTL */
[dir="rtl"] .crumbs li+li::before{{content:"‹"}}
[dir="rtl"] .note{{border-radius:8px 0 0 8px}}
[dir="rtl"] .hero h1,[dir="rtl"] .hero .lead,[dir="rtl"] p,[dir="rtl"] ul,[dir="rtl"] ol{{text-align:start}}
[dir="rtl"] a[href^="tel:"],[dir="rtl"] a[href^="mailto:"]{{direction:ltr;unicode-bidi:embed;display:inline-block}}
[dir="rtl"] .leaflet-container{{direction:ltr}}
[dir="rtl"] .leaflet-popup-content{{direction:rtl;text-align:right}}

/* Planner */
.pform{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px 18px;
  border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px;background:var(--surface);margin:0 0 24px}}
.pf{{display:flex;flex-direction:column;gap:6px;min-width:0}}
.pf-wide{{grid-column:1/-1}}
.pf label{{font-size:14px;font-weight:600;color:var(--brand-ink)}}
.pf label small{{font-weight:400;color:var(--ink-3);font-size:13px;margin-inline-start:6px}}
.pf .cnt{{color:var(--brand-2);font-weight:700}}
.pf select{{font:inherit;font-size:15.5px;padding:9px 11px;border:1px solid var(--line);
  border-radius:8px;background:var(--surface);color:var(--ink);max-width:100%}}
.pf-check label{{font-weight:500;display:flex;align-items:center;gap:8px;cursor:pointer}}
.pf-check input{{width:17px;height:17px;accent-color:var(--brand)}}
.prow{{display:flex;gap:10px;flex-wrap:wrap;margin-top:2px}}
.chips{{display:flex;flex-wrap:wrap;gap:7px}}
.chip{{font:inherit;font-size:14px;padding:6px 13px;border:1px solid var(--line);background:var(--surface);
  color:var(--ink-2);border-radius:20px;cursor:pointer;transition:none}}
.chip:hover{{border-color:var(--brand-2);color:var(--brand-ink)}}
.chip.on{{background:var(--brand);border-color:var(--brand);color:var(--on-brand);font-weight:600}}
.pday{{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:20px 24px;margin:0 0 18px}}
.pday h3{{margin:0 0 14px;font-size:19px;color:var(--brand-ink);display:flex;align-items:center;gap:9px;flex-wrap:wrap}}
.pday h3 small{{font-weight:500;font-size:14px;color:var(--ink-3)}}
.pdot{{width:12px;height:12px;border-radius:50%;display:inline-block;flex:none}}
.pstops{{list-style:none;margin:0;padding:0;max-width:none}}
.pstops li{{margin:0;padding:0 0 0 2px}}
.pleg{{font-size:13.5px;color:var(--ink-3);padding:7px 0 7px 14px;border-inline-start:2px dashed var(--line);margin-inline-start:5px}}
.pstop{{display:flex;flex-direction:column;gap:3px;padding:11px 14px;border:1px solid var(--line-2);
  border-radius:9px;background:var(--bg-2);margin:0 0 2px}}
.pstop b{{font-size:16.5px}}
.pmeta{{font-size:14px;color:var(--brand-2);font-weight:600}}
.pshort{{font-size:14.5px;color:var(--ink-2)}}
.popt{{font-size:13.5px;color:var(--ink-3);padding:6px 0 8px 16px;margin-inline-start:5px}}
.popt i{{font-style:normal;color:var(--ok);font-weight:600}}
.pnight{{font-size:14.5px;color:var(--ink-2);border-top:1px solid var(--line-2);margin-top:12px;padding-top:11px}}
@media print{{ .pform,#pmap{{display:none}} .pday{{break-inside:avoid}} }}

@media (max-width:900px){{
  .facts{{grid-template-columns:repeat(2,1fr)}}
  .cardetail{{grid-template-columns:1fr;gap:24px}}
}}
@media (max-width:760px){{
  body{{font-size:16px}}
  .head-in{{gap:10px;padding:12px 16px}}
  .head-in{{flex-wrap:wrap}}
  nav.main{{width:100%;margin-inline-start:0;order:3}}
  nav.main>ul{{gap:0;flex-wrap:nowrap;overflow:visible}}
  nav.main a{{padding:6px 9px;font-size:14.5px}}
  .langs{{margin-inline-start:auto;border:0;padding-inline-start:0}}
  .head-tel{{display:none}}
  .hero{{padding:44px 0 40px}}
  .sec{{padding:36px 0}}
  .site-head{{position:sticky}}
}}
@media (max-width:520px){{ .facts{{grid-template-columns:1fr}} }}

/* Compact typography — keeps information-dense pages comfortable on desktop. */
.hero h1{{font-size:clamp(25px,3.4vw,38px)}}
.hero .lead{{font-size:clamp(15px,1.6vw,17px);line-height:1.58}}
.hero-facts b{{font-size:22px}}
h1{{font-size:clamp(24px,2.8vw,33px)}}
h2{{font-size:clamp(19px,2vw,24px);margin-top:30px}}
h3{{font-size:16.5px}}
.page-head{{padding:30px 0 6px}}
.page-head .lead{{font-size:16px;line-height:1.65}}
.sec{{padding:38px 0}}
.article h2{{font-size:22px;margin-top:28px}}
.article h3{{font-size:17px;margin-top:20px}}
.post-c h2{{font-size:17px}}
.post-c p,.card p{{font-size:14px}}
.post-c .in,.card{{padding:16px 18px}}
.car h3{{font-size:16.5px}}
.car .sub,.car ul,.car .more{{font-size:13.5px}}
.car .p{{font-size:15px}}
.spec,table{{font-size:14px}}
.facts dd,.facts .v{{font-size:15px}}
.faq h3{{font-size:16px}}
.faq p,.note,.cta p{{font-size:14px}}
.btn{{font-size:14px;padding:9px 18px}}
.pricebox .big{{font-size:24px}}
.pday h3{{font-size:17px}}
.pstop b{{font-size:15px}}
.pshort,.pnight{{font-size:13.5px}}
.logo{{font-size:18px}}
nav.main a{{font-size:13.5px;padding:6px 9px}}
.head-tel{{font-size:13.5px}}
.crumbs{{font-size:13px}}

@media print{{ .site-head,.site-foot,.cta{{display:none}} body{{font-size:12pt}} }}

/* ═══════════════ Fleet House — dark design layer ═══════════════ */
::selection{{background:color-mix(in srgb,var(--brand) 40%,transparent);color:#fff}}
::-webkit-scrollbar{{width:11px;height:11px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--line);border-radius:99px;border:3px solid var(--bg)}}
::-webkit-scrollbar-thumb:hover{{background:var(--ink-3)}}
input,select,textarea,button{{color-scheme:dark}}

/* header */
.site-head{{background:color-mix(in srgb,var(--bg) 86%,#000);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}}
.head-in{{padding:12px 22px;gap:14px}}
.logo{{color:var(--brand-ink);font-size:19.5px;gap:11px}}
.logo .mark{{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:10px;
  background:var(--grad);color:var(--on-brand);font-size:13px;font-weight:800;letter-spacing:.02em;
  box-shadow:0 4px 14px color-mix(in srgb,var(--brand) 34%,transparent)}}
.logo small{{color:var(--ink-3);font-size:11.5px;letter-spacing:.14em}}
nav.main a{{color:var(--ink-2);border-radius:9px;padding:7px 11px}}
nav.main a:hover{{background:var(--surface-2);color:#fff}}
nav.main a[aria-current="page"]{{background:transparent;color:#fff;font-weight:700}}
.langs{{border:0;padding:3px;background:var(--surface-2);border-radius:999px;gap:2px}}
.langs a{{padding:5px 10px;border-radius:999px;font-size:12.5px;color:var(--ink-3);text-transform:uppercase}}
.langs a:hover{{background:color-mix(in srgb,#fff 8%,transparent)}}
.langs a.on{{background:var(--accent-2);color:#fff}}
.head-tel{{margin-inline-start:2px}}
.head-tel a{{display:inline-flex;align-items:center;gap:9px;background:var(--grad);color:var(--on-brand);
  font-weight:700;padding:10px 18px;border-radius:999px;font-size:15px;letter-spacing:.01em;
  box-shadow:0 6px 20px color-mix(in srgb,var(--brand) 28%,transparent)}}
.head-tel a:hover{{text-decoration:none;filter:brightness(1.08)}}
.head-tel a::before{{content:"";width:16px;height:16px;flex:none;background:currentColor;
  -webkit-mask:var(--ico-tel) center/contain no-repeat;mask:var(--ico-tel) center/contain no-repeat}}
:root{{--ico-tel:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z'/%3E%3C/svg%3E")}}

/* page top glow */
.crumbs{{position:relative}}
main{{position:relative}}
body::before{{content:"";position:fixed;inset-inline:0;top:0;height:420px;pointer-events:none;z-index:0;
  background:radial-gradient(120% 100% at 50% 0%,color-mix(in srgb,var(--brand) 13%,transparent) 0%,transparent 62%)}}
.site-head,main,.site-foot{{z-index:1}}
.site-head{{position:sticky;top:0;z-index:30}}
main,.site-foot{{position:relative}}

/* hero */
.hero{{background:linear-gradient(165deg,color-mix(in srgb,var(--brand) 12%,var(--bg)) 0%,var(--bg) 70%);
  border-bottom:1px solid var(--line)}}
.hero .kicker{{color:var(--accent)}}
.hero .lead{{color:var(--ink-2)}}
.page-head{{padding-top:26px}}
h1,h2,h3,h4{{color:var(--brand-ink)}}
.lead{{color:var(--ink-2)}}
.sec.alt{{background:color-mix(in srgb,var(--bg-2) 60%,var(--bg))}}

/* tags & chips */
.tag{{background:var(--accent);color:var(--on-brand);border-radius:999px;padding:5px 13px;
  font-size:12.5px;font-weight:700;display:inline-block;letter-spacing:.01em}}
.exptags .tag.g,.tag.muted{{background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line)}}

/* facts — mono values, like the mock */
.facts div{{background:var(--surface);border:1px solid var(--line);border-radius:12px}}
.facts{{gap:12px;border:0;background:none}}
.facts .k{{font-size:12.5px;color:var(--ink-3);letter-spacing:.02em}}
.facts .v{{font-family:var(--mono);font-size:17px;color:#fff;font-weight:600;letter-spacing:-.01em}}
.price,.exptot b{{font-family:var(--mono)}}

/* buttons */
.btn{{background:var(--grad);color:var(--on-brand);border-radius:999px;padding:12px 24px;font-weight:700;
  box-shadow:0 6px 20px color-mix(in srgb,var(--brand) 24%,transparent)}}
.btn:hover{{filter:brightness(1.08);text-decoration:none}}
.btn.ghost,.btn.alt{{background:var(--surface-2);color:var(--brand-ink);border:1px solid var(--line);
  box-shadow:none}}
.btn.ghost:hover,.btn.alt:hover{{border-color:var(--brand);color:#fff;filter:none}}

/* surfaces */
.card,.car,.post-c,.pday,.pform,.legend,.explorer{{background:var(--surface);border-color:var(--line)}}
.card:hover,.car:hover,.post-c:hover{{border-color:color-mix(in srgb,var(--brand) 45%,var(--line))}}
table{{background:var(--surface)}}
thead th{{background:var(--surface-2);color:var(--brand-ink)}}
tbody tr:nth-child(even){{background:color-mix(in srgb,#fff 3%,transparent)}}
.note{{background:color-mix(in srgb,var(--accent) 10%,var(--surface));border-inline-start-color:var(--accent);
  color:var(--ink-2)}}
.article strong,.article b{{color:#fff}}
.article a{{color:var(--brand-2);text-decoration:underline;text-underline-offset:3px}}

/* explorer on dark */
.expbar{{background:color-mix(in srgb,var(--bg-2) 70%,var(--bg))}}
.expbar input,.expbar select,.exppair input,.pform input,.pform select{{background:var(--bg);
  border-color:var(--line);color:var(--ink)}}
.expbar input::placeholder,.exppair input::placeholder{{color:var(--ink-3)}}
.expside{{background:color-mix(in srgb,var(--bg-2) 70%,var(--bg))}}
.exproutebox,.exppanel,.expsug{{background:var(--surface)}}
.expitem:hover{{background:var(--surface-2)}}
.exptot{{background:var(--surface-2)}}
.expclose{{background:var(--surface-2);color:var(--ink-2);border-color:var(--line)}}
.chip{{background:var(--surface-2);color:var(--ink-2);border-color:var(--line)}}
.chip:hover{{border-color:var(--brand);color:#fff}}
.chip.on{{background:var(--grad);color:var(--on-brand);border-color:transparent}}
.leaflet-container{{background:var(--bg-2)}}
.leaflet-popup-content-wrapper,.leaflet-popup-tip{{background:var(--surface);color:var(--ink)}}
.leaflet-tooltip{{background:var(--surface);color:var(--ink);border-color:var(--line)}}
.leaflet-bar a{{background:var(--surface);color:var(--ink);border-color:var(--line)}}
.leaflet-bar a:hover{{background:var(--surface-2)}}
.leaflet-control-attribution{{background:color-mix(in srgb,var(--bg) 78%,transparent)!important;
  color:var(--ink-3)}}
.leaflet-control-attribution a{{color:var(--ink-2)}}

/* footer */
.site-foot{{background:color-mix(in srgb,var(--bg) 60%,#000);border-top:1px solid var(--line)}}

/* the "rent a car for this trip" side card */
.attr-grid{{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:34px;align-items:start}}
.rentbox{{position:sticky;top:96px;background:var(--surface);border:1px solid var(--line);
  border-radius:16px;padding:22px 24px}}
.rentbox h3{{margin:0 0 8px;font-size:19px;color:#fff}}
.rentbox p{{margin:0 0 16px;font-size:14.5px;color:var(--ink-2);line-height:1.6}}
.rentrow{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;
  font-size:14.5px;color:var(--ink-2);padding:7px 0;border-bottom:1px solid var(--line)}}
.rentrow b{{font-family:var(--mono);color:#fff;font-weight:600;font-size:15px}}
.rentbox .btn{{display:flex;width:100%;justify-content:center;margin-top:16px}}
.rentnote{{font-size:12.5px;color:var(--ink-3);text-align:center;margin:10px 0 0;line-height:1.5}}
.tagrow{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}}
.maphero .wrap.wide{{max-width:var(--maxw)}}
.maphero{{padding-top:26px}}
.rentbox .btn::before{{content:"";width:16px;height:16px;flex:none;margin-inline-end:9px;
  background:currentColor;-webkit-mask:var(--ico-tel) center/contain no-repeat;
  mask:var(--ico-tel) center/contain no-repeat}}
.rentbox .btn{{align-items:center}}
.expitem i{{box-shadow:0 0 0 1px var(--line)}}

/* ── photos ─────────────────────────────────────────────────────── */
.photo{{margin:0 0 22px;border-radius:14px;overflow:hidden;background:var(--surface-2);
  border:1px solid var(--line)}}
.photo img{{width:100%;height:auto;display:block;aspect-ratio:16/9;object-fit:cover}}
.photo figcaption{{font-size:12px;color:var(--ink-3);padding:8px 12px;line-height:1.4}}
.photo figcaption a{{color:var(--ink-2)}}
.hero-photo img{{aspect-ratio:21/9}}
.card-img{{display:block;margin:-20px -22px 14px;overflow:hidden}}
.card-img img{{width:100%;height:170px;object-fit:cover;display:block;
  transition:transform .35s ease}}
.card:hover .card-img img{{transform:scale(1.04)}}
.expthumb{{width:46px;height:34px;object-fit:cover;border-radius:6px;float:inline-start;
  margin-inline-end:9px}}
.expitem{{overflow:hidden}}
.exppanel .photo{{margin-bottom:16px}}

/* ── planner: styles, photos, car recommendation ────────────────── */
.chips.styles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:10px}}
.chip.style{{display:block;text-align:start;padding:12px 15px;border-radius:12px;line-height:1.4;
  background:var(--surface);border:1px solid var(--line)}}
.chip.style b{{display:block;font-size:15px;color:var(--brand-ink);font-weight:700;margin-bottom:3px}}
.chip.style small{{display:block;font-size:12.5px;color:var(--ink-3);line-height:1.45}}
.chip.style.on{{border-color:var(--brand);background:color-mix(in srgb,var(--brand) 12%,var(--surface))}}
.chip.style.on b{{color:#fff}}
.carmode{{display:flex;flex-direction:row;gap:10px;flex-wrap:wrap;align-items:center;justify-content:flex-start}}
.tog{{display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--line);
  border-radius:999px;padding:9px 16px;font-size:14.5px;cursor:pointer;color:var(--ink-2)}}
.tog:has(input:checked){{border-color:var(--brand);color:#fff;
  background:color-mix(in srgb,var(--brand) 14%,var(--surface))}}
.tog input{{accent-color:var(--brand)}}
.pstop{{display:flex;gap:14px;align-items:flex-start}}
.pstop-t{{flex:1;min-width:0}}
.pthumb{{width:112px;height:84px;object-fit:cover;border-radius:10px;flex:none}}
.carrec{{display:grid;grid-template-columns:260px 1fr;gap:22px;align-items:center;
  background:var(--surface);border:1px solid var(--line);border-radius:16px;
  padding:20px 24px;margin:0 0 26px}}
.carrec img{{width:100%;height:auto;border-radius:12px}}
.carrec-ph{{width:100%;aspect-ratio:16/10;border-radius:12px;background:var(--surface-2)}}
.carrec h3{{margin:8px 0 4px;font-size:21px;color:#fff}}
.carrec .rentrow:last-of-type{{border-bottom:0}}
.carrec .why{{margin:10px 0 14px;font-size:13px;color:var(--ink-3)}}
.carrec .btn{{margin-top:2px}}
/* ── account & auth ─────────────────────────────────────────────── */
.authbox{{margin-inline-start:6px}}
.authlink{{display:inline-flex;align-items:center;gap:8px;background:var(--surface-2);
  border:1px solid var(--line);border-radius:999px;padding:7px 14px;font:inherit;font-size:14px;
  color:var(--ink-2);cursor:pointer}}
.authlink:hover{{border-color:var(--brand);color:#fff;text-decoration:none}}
.ava{{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;font-size:12px;
  font-weight:700;background:var(--grad);color:var(--on-brand)}}
.authdlg{{position:fixed;inset:0;z-index:900;background:rgba(2,6,12,.72);display:grid;
  place-items:center;padding:20px;backdrop-filter:blur(3px)}}
.authcard{{position:relative;width:min(420px,100%);background:var(--surface);
  border:1px solid var(--line);border-radius:18px;padding:26px 26px 22px;
  box-shadow:0 30px 80px rgba(0,0,0,.5);max-height:92vh;overflow:auto}}
.authcard h3{{margin:0 0 6px;font-size:22px;color:#fff}}
.authcard label{{display:block;font-size:13px;color:var(--ink-3);margin:0 0 10px}}
.authcard input{{width:100%;font:inherit;font-size:15px;padding:10px 12px;margin-top:4px;
  border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}}
.authx{{position:absolute;top:12px;inset-inline-end:14px;background:var(--surface-2);
  border:1px solid var(--line);border-radius:8px;width:30px;height:30px;cursor:pointer;
  color:var(--ink-2)}}
.btn.goog{{width:100%;justify-content:center;display:flex;align-items:center;gap:10px;
  background:#fff;color:#1f2937;margin:14px 0 4px;box-shadow:none}}
.gicon{{width:20px;height:20px;border-radius:50%;display:grid;place-items:center;
  background:#4285f4;color:#fff;font-weight:700;font-size:13px}}
.author{{display:flex;align-items:center;gap:10px;color:var(--ink-3);font-size:12.5px;margin:14px 0}}
.author::before,.author::after{{content:"";flex:1;height:1px;background:var(--line)}}
.authrow{{display:flex;gap:9px;margin:6px 0 10px}}
.authrow .btn{{flex:1;justify-content:center;display:flex}}
.autherr{{color:#fca5a5;font-size:13px;min-height:18px;margin:2px 0 6px}}
.authnote{{font-size:11.5px;color:var(--ink-3);margin:10px 0 0;line-height:1.5}}
.acchead{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;
  background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 20px;
  margin:0 0 22px}}
.acchead b{{display:block;color:#fff;font-size:17px}}
.acchead span{{font-size:13.5px;color:var(--ink-3)}}
.tripcard{{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:16px 20px;margin:0 0 12px}}
.tripcard.done{{opacity:.72;border-inline-start:3px solid var(--ok)}}
.tripmeta b{{color:#fff;font-size:17px;display:block}}
.tripmeta span{{font-size:13px;color:var(--ink-3);font-family:var(--mono)}}
.triprow{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
.btn.sm.ghost{{padding:7px 13px}}
.btn.wa{{background:#1faa53;color:#fff;box-shadow:0 6px 20px rgba(31,170,83,.25)}}
.btn.wa:hover{{filter:brightness(1.08)}}
.rentbox .btn.wa{{display:flex;width:100%;justify-content:center;margin-top:9px}}
.cform{{max-width:640px;background:var(--surface);border:1px solid var(--line);
  border-radius:16px;padding:24px 26px}}
.cform label{{display:block;font-size:13.5px;color:var(--ink-3);margin:0 0 14px}}
.cform input,.cform textarea{{width:100%;font:inherit;font-size:15px;padding:11px 13px;
  margin-top:5px;border:1px solid var(--line);border-radius:10px;background:var(--bg);
  color:var(--ink)}}
.cf2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:600px){{ .cf2{{grid-template-columns:1fr}} }}
.fok{{color:var(--ok);text-align:start;font-size:14.5px}}

.expdate{{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--ink-3)}}
.expdate input{{font:inherit;font-size:14px;padding:7px 10px;border:1px solid var(--line);
  border-radius:9px;background:var(--bg);color:var(--ink)}}
.expfind{{padding:12px 14px;border-bottom:1px solid var(--line);background:var(--surface)}}
.expfindrow{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:9px}}
.expfindrow .btn.on{{border-color:var(--accent);color:#fff;
  background:color-mix(in srgb,var(--accent) 18%,var(--surface))}}
.expmodes{{display:flex;gap:7px;margin-bottom:8px}}
.tog.sm{{padding:6px 12px;font-size:13px}}
.expnear{{margin-top:10px;font-size:14px;max-height:260px;overflow:auto}}
.expmap.drawing{{cursor:crosshair}}
.stars{{display:inline-flex;align-items:baseline;gap:7px;white-space:nowrap}}
.stars i{{font-style:normal;color:#fbbf24;letter-spacing:2px;font-size:16px}}
.stars b{{font-family:var(--mono);font-size:13.5px;color:var(--ink-2);font-weight:600}}
.stars.sm i{{font-size:13px;letter-spacing:1px}}
.stars.sm b{{font-size:12px}}
.card .stars.sm{{display:flex;margin:8px 0 2px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;
  margin:24px 0 6px}}
.gph{{margin:0;border-radius:12px;overflow:hidden;background:var(--surface-2);
  border:1px solid var(--line)}}
.gph img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;
  transition:transform .35s ease}}
.gph:hover img{{transform:scale(1.05)}}
.gph figcaption{{font-size:10.5px;color:var(--ink-3);padding:5px 9px;line-height:1.35}}
.gph figcaption a{{color:var(--ink-3)}}
.galstrip{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:0 0 14px}}
.galstrip img{{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block}}
.numpin b{{display:grid;place-items:center;width:22px;height:22px;border-radius:50%;
  background:#2dd4bf;color:#04222b;font-size:12px;font-weight:800;border:2px solid #fff;
  box-shadow:0 2px 8px rgba(0,0,0,.4)}}
.numpin.blue b{{background:#38bdf8}}
.wpbtns{{display:inline-flex;gap:4px;margin-inline-start:8px}}
.wpbtns button,.pstop-b button{{border:1px solid var(--line);background:var(--surface-2);
  color:var(--ink-2);border-radius:6px;width:24px;height:24px;cursor:pointer;font-size:12px;
  line-height:1}}
.wpbtns button:hover,.pstop-b button:hover{{border-color:var(--brand);color:#fff}}
.pstop-b{{display:flex;flex-direction:column;gap:4px;flex:none}}
.paddbtn{{border:1px solid var(--line);background:var(--surface-2);color:var(--ok);
  border-radius:6px;width:22px;height:22px;cursor:pointer;font-size:13px;line-height:1;
  vertical-align:middle}}
.paddbtn:hover{{border-color:var(--ok)}}
.psum{{font-size:16px;color:var(--ink-2);background:var(--surface);border:1px solid var(--line);
  border-inline-start:3px solid var(--brand);border-radius:10px;padding:13px 17px;margin:0 0 22px}}
.pstay{{display:block;margin-top:6px;font-size:13.5px}}
.pstay a{{color:var(--brand-2)}}
.pstay small{{color:var(--ink-3);font-size:11px;display:block;margin-top:2px}}
.wx{{display:inline-flex;align-items:baseline;gap:4px;font-family:var(--mono);font-size:14px;
  color:#fff;white-space:nowrap}}
.wx small{{color:var(--ink-3);font-size:12px}}
.wxr{{color:#7dd3fc;font-size:12px}}
.wxbox{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:var(--surface-2);
  border:1px solid var(--line);border-radius:10px;padding:9px 13px;margin:0 0 14px;font-size:13.5px}}
.wxbox b{{color:var(--ink-3);font-weight:600;font-size:12.5px}}
.wxbox small{{color:var(--ink-3);font-size:11.5px;margin-inline-start:auto}}
.wxrow{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 10px;font-size:13px}}
.wxrow b{{color:var(--ink-3);font-size:12.5px;font-weight:600;width:100%}}
.wxcell{{background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:4px 9px}}
.wxrow small{{color:var(--ink-3);font-size:11.5px;width:100%}}
.pwx{{display:inline-flex;gap:6px;align-items:center;margin-inline-start:10px}}
@media(max-width:760px){{
  .carrec{{grid-template-columns:1fr}}
  .pthumb{{width:78px;height:60px}}
  .card-img img{{height:140px}}
}}
.page-head .tag{{font-size:13px}}
@media(max-width:980px){{ .attr-grid{{grid-template-columns:1fr}} .rentbox{{position:static}} }}
/* Final compact scale overrides for extended travel/planner components. */
.logo{{font-size:18px}}
nav.main a{{font-size:13.5px;padding:6px 9px}}
.head-in{{padding-block:9px}}
.psum{{font-size:14px;padding:10px 14px}}
.carrec h3,.rentbox h3{{font-size:17px}}
.rentrow,.attr-facts,.route-meta,.timeline{{font-size:13.5px}}
.explorer h2,.maphero h2{{font-size:22px}}
.map-sub,.rentbox p{{font-size:14px}}
.card-title{{font-size:16px}}
.card-text{{font-size:13.5px}}
@media(max-width:760px){{
  body{{font-size:14px}}
  h1{{font-size:26px}}
  .page-head .lead{{font-size:15px}}
  .sec{{padding:30px 0}}
}}
"""
