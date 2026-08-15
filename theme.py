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
.logo img{{height:{d['logo_height']}px;width:auto;max-width:118px;object-fit:contain}}
.logo-name{{display:grid;gap:2px;line-height:1.05}}
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
  clear:both;border:1px solid var(--line);border-radius:var(--radius);padding:9px 12px;background:var(--surface);
  margin-top:12px;position:relative;z-index:0}}
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
  border-bottom:1px solid var(--line);background:var(--bg-2);position:relative}}
.expsearch-wrap{{position:relative;flex:1 1 240px;min-width:180px}}
.expsearch-wrap .expsearch{{width:100%}}
.expqlist{{display:none;position:absolute;z-index:850;top:calc(100% + 6px);inset-inline-start:0;width:100%;
  max-height:420px;overflow:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px;
  box-shadow:0 20px 55px rgba(0,0,0,.48);padding:6px}}
.expqlist.on{{display:block}}
.expqitem{{display:flex;width:100%;align-items:center;gap:10px;text-align:start;border:0;background:transparent;
  color:var(--ink);padding:7px;border-radius:9px;cursor:pointer;font:inherit}}
.expqitem:hover,.expqitem:focus-visible{{background:var(--surface-2)}}
.expqitem img{{width:54px;height:40px;object-fit:cover;border-radius:7px;flex:none}}
.expqitem span{{min-width:0}}
.expqitem b{{display:block;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.expqitem small{{display:block;font-size:11px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.expsearch{{min-width:0}}
.budget-stepper{{display:grid;grid-template-columns:38px minmax(70px,92px) auto 38px;align-items:center;gap:6px}}
.budget-stepper button{{height:38px;border:1px solid var(--line);border-radius:10px;background:var(--surface-2);color:var(--ink);font:700 18px/1 var(--font);cursor:pointer}}
.budget-stepper input{{width:100%;height:38px;text-align:center;padding:6px!important}}
.budget-stepper>span{{font-size:12px;color:var(--ink-2);white-space:nowrap}}
.days-stepper{{display:grid;grid-template-columns:30px minmax(42px,58px) 30px;align-items:center;gap:4px}}
.days-stepper button{{width:30px;height:38px;padding:0;border:1px solid var(--line);border-radius:8px;background:var(--surface-2);color:var(--ink);font:700 16px/1 var(--font);cursor:pointer}}
.days-stepper input{{width:100%;height:38px;padding:5px!important;text-align:center;font-weight:700}}
.expbar input,.expbar select{{font:inherit;font-size:15px;padding:9px 12px;border:1px solid var(--line);
  border-radius:10px;background:var(--surface);color:var(--ink)}}
.expcount{{font-size:14px;color:var(--ink-3);margin-inline-start:auto}}
.expgrid{{display:grid;grid-template-columns:330px 1fr;height:clamp(540px,var(--exph,68vh),720px);min-height:540px}}
.expside{{border-inline-end:1px solid var(--line);display:flex;flex-direction:column;min-height:0;
  background:var(--bg-2);overflow-y:auto;overflow-x:hidden}}
.exproutebox{{padding:9px 11px;border-bottom:1px solid var(--line);background:var(--surface)}}
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
.expslider{{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--ink-3);margin-top:7px}}
.expslider input{{flex:1}}
.exprouteout{{margin-top:10px;font-size:14px}}
.exptot{{display:flex;gap:9px;flex-wrap:wrap;align-items:baseline;padding:7px 9px;border-radius:9px;
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
.hero.tight{{padding:20px 0 18px}}
.hero.tight h1{{font-size:clamp(21px,2.2vw,28px);margin:0 0 5px;max-width:34ch;line-height:1.2}}
.hero.tight .lead{{font-size:clamp(13px,1.1vw,15px);margin:0;max-width:58ch;line-height:1.45}}
.hero.tight .kicker{{font-size:10.5px;letter-spacing:.1em;margin-bottom:6px}}
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
.notify-center{{position:relative;display:inline-flex;align-items:center}}
.notify-button{{position:relative;width:42px;height:42px;border:1px solid var(--line);border-radius:50%;background:var(--surface);color:var(--brand);cursor:pointer}}
.notify-button>span{{font-size:15px}}.notify-button>b{{position:absolute;top:-5px;right:-5px;min-width:19px;height:19px;padding:0 5px;border-radius:10px;background:#e24b55;color:#fff;font:700 11px/19px var(--font)}}
.notify-pop{{position:absolute;z-index:2600;top:calc(100% + 10px);inset-inline-end:0;width:min(360px,88vw);max-height:440px;overflow:auto;padding:10px;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.3)}}
.notify-head,.notify-row{{display:flex;align-items:center;justify-content:space-between;gap:10px}}.notify-head{{padding:5px 7px 10px;border-bottom:1px solid var(--line)}}
.notify-head a{{font-size:12px}}.notify-row{{padding:8px 5px;border-bottom:1px solid var(--line)}}.notify-row>a{{display:grid;min-width:0;color:var(--ink);text-decoration:none}}.notify-row small{{color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.notify-row>button{{border:0;background:transparent;cursor:pointer}}.notify-row.muted{{opacity:.55}}
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
.authcard .facebook{{width:100%;margin-top:10px;background:#1877f2;color:#fff;border-color:#1877f2}}
.authcard .facebook:hover{{background:#166fe5;border-color:#166fe5}}
.fbicon{{display:inline-grid;place-items:center;width:24px;height:24px;margin-inline-end:10px;border-radius:50%;background:#fff;color:#1877f2;font:bold 21px/1 Arial,sans-serif}}
.authnote{{font-size:11.5px;color:var(--ink-3);margin:10px 0 0;line-height:1.5}}
.acchead{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;
  background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 20px;
  margin:0 0 22px}}
.profile-id{{display:flex;align-items:center;gap:13px;min-width:0}}
.profile-avatar{{position:relative;flex:0 0 auto;width:62px;height:62px;border-radius:50%;overflow:hidden;display:grid;place-items:center;background:var(--grad);color:var(--on-brand);font-weight:850;font-size:22px;cursor:pointer;border:2px solid color-mix(in srgb,var(--brand) 55%,#fff);box-shadow:0 8px 24px rgba(0,0,0,.3)}}
.profile-avatar img{{width:100%;height:100%;object-fit:cover;display:block}}.profile-avatar input{{position:absolute;width:1px;height:1px;opacity:0}}
.profile-avatar i{{position:absolute;inset:auto 2px 2px auto;width:20px;height:20px;border-radius:50%;display:grid;place-items:center;background:var(--brand);color:#04222b;font:900 16px/1 sans-serif;border:2px solid var(--surface)}}
.profile-avatar.loading{{opacity:.55;pointer-events:none}}
.avatar-change{{display:block;margin-top:5px;padding:0;border:0;background:none;color:var(--brand-2);font:inherit;font-size:12px;font-weight:700;cursor:pointer}}
.acchead b{{display:block;color:#fff;font-size:17px}}
.acchead span{{font-size:13.5px;color:var(--ink-3)}}
.tripcard{{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:16px 20px;margin:0 0 12px}}
.tripcard.done{{opacity:.72;border-inline-start:3px solid var(--ok)}}
.tripmeta b{{color:#fff;font-size:17px;display:block}}
.tripmeta span{{font-size:13px;color:var(--ink-3);font-family:var(--mono)}}
.triprow{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
.memory-upload{{cursor:pointer}}.memory-upload input{{position:absolute;inline-size:1px;block-size:1px;opacity:0}}
.memory-upload.loading{{opacity:.65;pointer-events:none}}.memory-upload.upload-error{{border-color:#ef4444;color:#fca5a5}}
.booking-box{{margin-top:1rem;padding:1rem;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg2)}}
.booking-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;margin-bottom:.75rem}}
.booking-grid label{{display:grid;gap:.35rem;font-size:.78rem;color:var(--ink2)}}
.booking-grid input{{min-width:0;width:100%;height:44px;padding:.55rem .7rem;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}}
.booking-summary{{min-height:2.5rem;margin:.25rem 0 .75rem;font-size:.82rem;line-height:1.55;color:var(--ink2)}}
.booking-success{{border-color:var(--ok)}}
.share-result{{display:flex;gap:.5rem;margin-top:.65rem}}.share-result input{{flex:1;min-width:0}}
.message-form{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.55rem;align-items:end;margin-top:.75rem}}
.message-form label{{display:grid;gap:.3rem;font-size:.75rem;color:var(--ink2)}}.message-form textarea{{min-height:72px}}
.trip-save-form{{display:grid;grid-template-columns:minmax(130px,.7fr) minmax(190px,1.3fr) auto auto;gap:.4rem;align-items:end}}
.trip-save-form label{{display:grid;gap:.3rem;font-size:.75rem;color:var(--ink2)}}
.booking-list{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:.7rem}}.booking-card{{display:grid;gap:.65rem;padding:1rem;border:1px solid var(--line);border-radius:14px;background:linear-gradient(145deg,var(--bg2),var(--surface-2))}}
.booking-card-head{{display:flex;align-items:flex-start;justify-content:space-between;gap:.75rem}}.booking-card-head>div{{display:grid;gap:.2rem}}.booking-card span{{font-size:.8rem;color:var(--ink2)}}.booking-status{{padding:.3rem .55rem;border-radius:999px;background:rgba(148,163,184,.12);white-space:nowrap}}.booking-status.confirmed,.booking-status.completed{{color:#5eead4;background:rgba(45,212,191,.12)}}.booking-status.cancelled{{color:#fda4af;background:rgba(244,63,94,.12)}}.booking-facts{{display:flex;gap:.8rem;padding-top:.55rem;border-top:1px solid var(--line)}}.booking-ext{{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.2rem}}
.car-review{{display:grid;gap:.55rem;padding-top:.65rem;border-top:1px solid var(--line)}}.rating-pick{{display:flex;flex-direction:row-reverse;justify-content:flex-end;width:max-content}}.rating-pick input{{position:absolute;opacity:0}}.rating-pick span{{font-size:1.45rem;color:#526173;cursor:pointer}}.rating-pick label:hover span,.rating-pick label:hover~label span,.rating-pick input:checked~span,.rating-pick label:has(input:checked)~label span{{color:#fbbf24}}.car-review textarea{{min-height:72px;resize:vertical}}.car-review [role=status]{{font-size:.8rem;color:#5eead4}}.car-review-saved{{display:grid;gap:.25rem;padding-top:.6rem;border-top:1px solid var(--line)}}.car-review-saved .stars{{color:#fbbf24;letter-spacing:2px}}.car-review-saved p{{margin:0;font-size:.82rem;color:var(--ink2)}}
.conversation-list{{display:grid;gap:.75rem}}.conversation{{padding:.9rem;border:1px solid var(--line);border-radius:12px;background:var(--bg2)}}
.message-list{{display:grid;gap:.35rem;margin:.65rem 0;max-height:280px;overflow:auto}}.message{{width:fit-content;max-width:82%;margin:0;padding:.5rem .7rem;border-radius:10px;background:var(--bg)}}
.message.mine{{justify-self:end;background:rgba(45,212,191,.13);border:1px solid rgba(45,212,191,.28)}}.conversation form{{display:grid;grid-template-columns:1fr auto;gap:.45rem;align-items:end}}.conversation textarea{{min-height:54px}}
@media(max-width:640px){{.booking-grid{{grid-template-columns:1fr}}.booking-box .btn{{width:100%}}}}
.memory-strip{{flex-basis:100%;display:flex;gap:7px;overflow:auto;padding-top:5px}}
.memory-strip img{{width:72px;height:54px;object-fit:cover;border-radius:8px;border:1px solid var(--line)}}
.accjournal{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:18px 0}}
.journal-section{{padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}}
.journal-section h2{{font-size:17px;margin:0 0 10px}}.visit-history{{display:grid;gap:6px;max-height:250px;overflow:auto}}
.visit-history div{{display:grid;grid-template-columns:100px 1fr;gap:10px;padding:8px;border-radius:9px;background:var(--surface-2)}}
.visit-history time{{font:12px var(--mono);color:var(--ink-2)}}.visit-history b{{font-size:13px;text-transform:capitalize}}
.my-reviews{{display:grid;gap:8px;max-height:250px;overflow:auto}}.my-reviews article{{padding:9px;border-radius:9px;background:var(--surface-2)}}
.my-reviews article p{{font-size:13px;margin:5px 0}}.my-reviews article img{{width:64px;height:48px;object-fit:cover;border-radius:7px}}
.reviewform fieldset{{border:0;padding:0;margin:0 0 14px}}.reviewform legend{{font-size:13px;color:var(--ink-2);margin-bottom:7px}}
.rating-pick{{display:flex;gap:6px;flex-wrap:wrap}}.rating-pick label{{margin:0}}.rating-pick input{{position:absolute;opacity:0}}
.rating-pick span{{display:block;padding:8px 11px;border:1px solid var(--line);border-radius:10px;color:#fbbf24;cursor:pointer}}
.rating-pick input:checked+span{{background:rgba(251,191,36,.12);border-color:#fbbf24}}
.reviewform textarea{{width:100%;min-height:120px;margin-top:6px;padding:11px 13px;border:1px solid var(--line);border-radius:12px;background:#07101a;color:var(--ink);font:inherit;resize:vertical}}
@media(max-width:720px){{.accjournal{{grid-template-columns:1fr}}}}
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
.expfind{{padding:9px 11px;border-bottom:1px solid var(--line);background:var(--surface);min-height:0}}
.expfindrow{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:7px}}
.expfindrow .btn{{padding:7px 10px;font-size:12.5px}}
.expfindrow .btn.on{{border-color:var(--accent);color:#fff;
  background:color-mix(in srgb,var(--accent) 18%,var(--surface))}}
.expmodes{{display:flex;gap:6px;margin-bottom:6px}}
.tog.sm{{padding:6px 12px;font-size:13px}}
.expnear{{margin-top:7px;font-size:13px;max-height:210px;overflow:auto}}
.travel-workspace[data-mode="explore"] .expfind,
.travel-workspace[data-mode="planner"] .expfind{{display:flex;flex-direction:column;flex:1;min-height:0}}
.travel-workspace[data-mode="explore"] .expnear,
.travel-workspace[data-mode="planner"] .expnear{{flex:1;min-height:0;max-height:none}}
.travel-workspace[data-mode="explore"] .suggest-list,
.travel-workspace[data-mode="planner"] .suggest-list{{padding-bottom:8px}}
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
.map-weather-symbol{{background:transparent!important;border:0!important}}
.map-weather-symbol span{{display:grid;place-items:center;width:42px;height:42px;font-size:30px;line-height:1;
  opacity:.30;filter:saturate(.72) drop-shadow(0 1px 2px rgba(3,12,22,.32));transform:translateZ(0);user-select:none}}
@media (max-width:760px){{.map-weather-symbol span{{width:36px;height:36px;font-size:25px;opacity:.27}}}}
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
/* Account experience — compact travel dashboard */
.head-in{{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:18px}}
nav.main{{justify-self:start;min-width:0;margin-inline-start:0}}
.head-actions{{display:flex;align-items:center;gap:10px;justify-self:end}}
.authbox{{margin-inline-start:0;justify-self:end;flex:none}}
.authlink{{min-height:40px;border-color:color-mix(in srgb,var(--brand) 32%,var(--line));font-weight:650;
  color:var(--brand-ink);box-shadow:0 8px 24px rgba(0,0,0,.18);white-space:nowrap}}
.authlink:hover{{background:color-mix(in srgb,var(--brand) 12%,var(--surface-2))}}
.auth-user-icon{{width:17px;height:17px;border:1.8px solid currentColor;border-radius:50%;position:relative}}
.auth-user-icon::after{{content:"";position:absolute;width:21px;height:10px;border:1.8px solid currentColor;
  border-bottom:0;border-radius:13px 13px 0 0;inset-inline-start:50%;top:15px;transform:translateX(-50%)}}
.ava{{width:30px;height:30px;overflow:hidden}}.ava img{{width:100%;height:100%;object-fit:cover;display:block}}
.authdlg{{background:rgba(2,8,16,.78);backdrop-filter:blur(10px)}}
body.auth-open{{overflow:hidden}}
.authcard{{width:min(440px,100%);background:linear-gradient(180deg,#101a28,#0b141f);
  border:1px solid rgba(148,163,184,.18);border-radius:22px;padding:30px 32px 26px;
  box-shadow:0 32px 90px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.03);max-height:calc(100dvh - 32px)}}
.authbrand{{width:112px;height:62px;border-radius:14px;background:transparent;display:grid;place-items:center;
  margin-bottom:18px;box-shadow:0 10px 28px color-mix(in srgb,var(--brand) 30%,transparent)}}
.authbrand span{{font-weight:850;font-size:14px;color:#04222b}}.authbrand img{{display:block;width:108px;height:58px;object-fit:contain}}
.authcard h3{{font-size:24px;line-height:1.25;color:#f4f8fc}}
.authcard .pshort{{font-size:14px;line-height:1.65;margin-bottom:18px}}
.authcard input{{height:48px;padding:11px 13px;margin-top:6px;border-radius:12px;background:#07101a;transition:.18s ease}}
.authcard input:focus{{outline:0;border-color:var(--brand);box-shadow:0 0 0 3px color-mix(in srgb,var(--brand) 22%,transparent)}}
.authx{{width:40px;height:40px;border-radius:11px}}
.btn.goog{{min-height:48px;margin-top:0;border:1px solid #d6dce4}}
.btn.goog:hover{{filter:none;background:#f5f7fa}}
.btn.goog:disabled{{opacity:.65;cursor:wait}}
.gicon,.gicon svg{{width:21px;height:21px;display:block;flex:none}}
.authrow{{margin-top:10px}}
.autherr{{display:none;min-height:0;color:#fecaca;background:rgba(239,68,68,.1);border:1px solid rgba(248,113,113,.25);
  border-radius:10px;line-height:1.5;padding:9px 11px;margin:6px 0}}
.autherr.show{{display:block}}
.authsignup{{font-size:13px;color:var(--ink-3);margin:14px 0 0;text-align:center}}
.authsignup .lnk{{font-weight:700;color:var(--brand-2)}}
.account-sec{{padding-top:26px}}
.page-account .page-head{{text-align:center;padding-top:34px}}
.page-account .page-head h1{{font-size:clamp(27px,3vw,36px);margin-bottom:10px}}
.page-account .page-head .lead{{font-size:15px;margin-inline:auto}}
.account-shell{{max-width:760px;margin:0 auto}}
.account-empty{{min-height:clamp(330px,48vh,500px);display:flex;flex-direction:column;align-items:center;
  justify-content:center;text-align:center;padding:46px 28px;background:radial-gradient(circle at 50% 0%,rgba(34,184,214,.12),transparent 48%),var(--surface);
  border:1px solid var(--line);border-radius:22px;box-shadow:0 26px 70px rgba(0,0,0,.2)}}
.account-orbit{{width:70px;height:70px;border:1px solid rgba(56,189,248,.35);border-radius:50%;display:grid;
  place-items:center;margin-bottom:20px;box-shadow:inset 0 0 28px rgba(34,184,214,.1),0 0 35px rgba(34,184,214,.08)}}
.account-orbit span{{width:24px;height:30px;border:2px solid var(--brand-2);border-radius:5px;position:relative}}
.account-orbit span::after{{content:"";position:absolute;width:9px;height:9px;border-inline-end:2px solid var(--accent);
  border-bottom:2px solid var(--accent);transform:rotate(45deg);inset-inline-start:5px;top:6px}}
.account-eyebrow{{font-size:11px!important;letter-spacing:.16em;text-transform:uppercase;color:var(--brand-2)!important;margin-bottom:8px!important}}
.account-empty h2{{font-size:23px;margin:0 0 10px}}
.account-empty>p{{font-size:14.5px;color:var(--ink-2);max-width:500px;margin:0 auto 22px}}
.account-actions{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
.account-actions .btn{{min-width:150px}}
/* Explorer place selection and real grouped map markers */
.suggest-list,.cluster-list{{display:grid;gap:6px}}
.place-choice{{display:grid;grid-template-columns:22px 50px minmax(0,1fr);gap:8px;align-items:center;
  min-height:60px;padding:6px;border:1px solid transparent;border-radius:10px;cursor:pointer;
  background:color-mix(in srgb,var(--surface) 82%,transparent);transition:border-color .16s,background .16s}}
.place-choice:hover{{background:var(--surface-2);border-color:var(--line)}}
.place-choice:has(input:checked){{border-color:color-mix(in srgb,var(--accent) 70%,var(--line));
  background:color-mix(in srgb,var(--accent) 9%,var(--surface))}}
.place-choice input{{width:19px;height:19px;accent-color:var(--accent);cursor:pointer}}
.place-choice img,.place-ph{{width:50px;height:38px;object-fit:cover;border-radius:7px;background:var(--surface-2);display:block}}
.place-copy{{min-width:0;display:block}}
.place-copy .lnk{{display:block;font-size:12.5px;line-height:1.3;font-weight:650;text-decoration:none;
  white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.place-line{{display:block;font-size:10.5px;line-height:1.3;color:var(--ink-3);margin-top:2px}}
.place-rating{{display:flex;align-items:center;gap:5px;font-size:11.5px;line-height:1.2;margin-top:3px}}
.place-rating i{{font-style:normal;color:#fbbf24;letter-spacing:.02em}}
.place-rating b{{font-family:var(--mono);color:var(--ink-2)}}
.visited-mini{{grid-column:3;border:0;background:transparent;color:var(--ink-2);padding:2px 0;text-align:start;
  font:600 11px/1.25 var(--sans);cursor:pointer}}
.visited-mini:hover,.visited-mini.on{{color:#9ca3af;text-decoration:underline}}
.visited-toggle.on{{background:#475569!important;border-color:#64748b!important;color:#f1f5f9!important}}
.cluster-intro{{font-size:13px;color:var(--ink-3);margin:0 0 12px}}
.exppanel.group-panel{{width:min(390px,94%)}}
.placecluster{{background:transparent!important;border:0!important}}
.placecluster b{{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#2dd4bf;
  color:#04222b;font-size:17px;font-weight:850;border:4px solid #fff;box-shadow:0 0 0 5px rgba(45,212,191,.24),0 7px 22px rgba(0,0,0,.38);cursor:pointer}}
.placecluster.single b{{width:44px;height:44px;font-size:16px;background:#38bdf8;box-shadow:0 0 0 4px rgba(56,189,248,.22),0 6px 18px rgba(0,0,0,.34)}}
.placecluster.visited b{{background:#788493!important;color:#f8fafc!important;box-shadow:0 0 0 3px rgba(120,132,147,.2),0 4px 12px rgba(0,0,0,.3)!important}}
.mapcluster{{background:transparent!important;border:0!important}}
.mapcluster b{{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:#20c9bd;
  color:#032b35;font-size:17px;font-weight:900;border:4px solid #fff;box-shadow:0 0 0 6px rgba(32,201,189,.25),0 9px 28px rgba(0,0,0,.4);cursor:zoom-in}}
.mapcluster.visited b{{background:#7b8795;color:#fff;box-shadow:0 0 0 6px rgba(123,135,149,.22),0 9px 28px rgba(0,0,0,.35)}}
/* Progressive disclosure from the 100-scenario UX review. */
.expfilters{{position:relative;flex:0 0 auto}}
.expfilters>summary{{height:40px;display:flex;align-items:center;padding:7px 12px;border:1px solid var(--line);
  border-radius:10px;background:var(--surface-2);color:var(--ink-2);font-size:13px;font-weight:650;cursor:pointer;list-style:none;white-space:nowrap}}
.expfilters>summary::-webkit-details-marker{{display:none}}
.expfilters>summary::after{{content:"⌄";margin-inline-start:8px;color:var(--ink-3)}}
.expfilters[open]>summary{{border-color:color-mix(in srgb,var(--brand) 65%,var(--line));color:var(--brand-ink)}}
.expfilters-pop{{position:absolute;z-index:950;inset-block-start:calc(100% + 8px);inset-inline-end:0;width:min(330px,90vw);
  display:grid;gap:8px;padding:12px;border:1px solid var(--line);border-radius:14px;background:var(--surface);box-shadow:0 20px 55px rgba(0,0,0,.45)}}
.expfilters-pop select,.expfilters-pop input{{width:100%;min-width:0}}
.expfilters-pop .expdate{{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:8px}}
.home-more-wrap{{padding:18px 0 40px;border-top:1px solid var(--line)}}
.home-more{{border:1px solid var(--line);border-radius:16px;background:var(--surface);overflow:hidden}}
.home-more>summary{{display:flex;align-items:center;justify-content:space-between;min-height:56px;padding:14px 18px;
  color:var(--brand-ink);font-size:14px;font-weight:750;cursor:pointer;list-style:none}}
.home-more>summary::-webkit-details-marker{{display:none}}
.home-more>summary::after{{content:"+";display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--surface-2);font-size:19px}}
.home-more[open]>summary::after{{content:"−"}}
.home-more-facts{{margin:0 18px 8px;padding:14px 0!important}}
.home-more>.sec{{padding:28px 0}}
.home-more>.sec>.wrap{{padding-inline:18px}}
.hp{{display:none!important}}
.booking-dialog{{position:fixed;inset:0;z-index:9998;display:grid;place-items:center;padding:18px;background:rgba(2,8,16,.8);backdrop-filter:blur(10px)}}
.booking-dialog[hidden]{{display:none}}
body.booking-open{{overflow:hidden}}
.booking-modal-card{{position:relative;width:min(560px,100%);max-height:calc(100dvh - 36px);overflow:auto;padding:28px;border:1px solid rgba(148,163,184,.2);border-radius:22px;background:linear-gradient(180deg,#101b29,#0a141f);box-shadow:0 32px 90px rgba(0,0,0,.6)}}
.booking-close{{position:absolute;inset-block-start:14px;inset-inline-end:14px;width:40px;height:40px;border:1px solid var(--line);border-radius:11px;background:var(--surface-2);color:var(--muted);font-size:25px;line-height:1;cursor:pointer}}
.booking-brand{{display:grid;place-items:center;width:58px;height:46px;margin-bottom:15px;border-radius:13px;background:linear-gradient(135deg,#24bce2,#4385f5);color:#062333;font-weight:900;box-shadow:0 10px 28px rgba(43,184,230,.22)}}
.inquiry-mini{{margin:0;padding:0;background:transparent}}
.inquiry-mini h2{{font-size:24px;line-height:1.25;margin:0 0 6px}}
.booking-lead{{max-width:440px;margin:0 0 16px;color:var(--muted);font-size:13px;line-height:1.55}}
.booking-choice{{display:grid;gap:2px;margin:0 0 14px;padding:10px 12px;border:1px solid rgba(45,212,191,.28);border-radius:12px;background:rgba(45,212,191,.08)}}
.booking-choice small{{color:var(--muted);font-size:11px}}.booking-choice strong{{font-size:14px;color:var(--ink)}}
.inquiry-grid{{display:grid;grid-template-columns:1fr 1fr;gap:11px}}
.inquiry-grid label{{display:grid;gap:5px;font-size:12px;color:var(--muted)}}
.inquiry-grid input,.inquiry-grid textarea{{width:100%;min-width:0;padding:10px 12px;border:1px solid var(--line);border-radius:11px;background:#07101a;color:var(--ink);font:inherit}}
.inquiry-grid input{{height:46px}}.inquiry-grid textarea{{resize:vertical;min-height:68px}}
.inquiry-notes{{grid-column:1/-1}}
.inquiry-actions{{display:grid;grid-template-columns:1.4fr 1fr;gap:10px;margin-top:15px}}
.inquiry-actions .btn{{width:100%;min-height:46px}}
.inquiry-status{{min-height:1.3em;margin:7px 0 0;color:var(--muted);font-size:12px}}
.car-actions{{display:flex;align-items:center;gap:10px}}.book-car-link{{border:0;padding:0;background:none;color:var(--accent);font:inherit;font-size:12px;font-weight:750;cursor:pointer}}
.booking-hero-cta{{margin-top:8px}}
@media(max-width:600px){{.booking-dialog{{place-items:end center;padding:0}}.booking-modal-card{{width:100%;max-height:92dvh;padding:24px 18px calc(20px + env(safe-area-inset-bottom));border-radius:22px 22px 0 0}}.inquiry-grid{{grid-template-columns:1fr}}.inquiry-notes{{grid-column:auto}}.inquiry-actions{{grid-template-columns:1fr}}}}
#expgeo.approx{{border-color:#f59e0b;color:#fbbf24}}
.corner-tools{{position:fixed;inset-block-start:14px;inset-inline-end:18px;z-index:72;display:flex;align-items:center;gap:9px}}
.corner-tools .corner-langs{{display:flex!important;width:auto;border:1px solid var(--line);padding:3px;background:rgba(11,20,31,.94);backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.28)}}
.corner-tools .corner-langs a{{min-width:35px;padding:6px 8px;text-align:center;font-size:11px}}
.corner-tools .authbox{{position:static!important;inset:auto!important;width:auto!important}}
.corner-tools .authlink{{width:auto!important;min-width:44px;background:rgba(11,20,31,.94);backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.32)}}
.app-download{{position:relative}}
.app-download summary{{list-style:none;display:flex;align-items:center;justify-content:center;gap:7px;min-height:42px;padding:0 13px;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);font-size:12px;font-weight:750;cursor:pointer}}
.app-download summary::-webkit-details-marker{{display:none}}
.app-download-icon{{display:grid;place-items:center;width:22px;height:22px;border-radius:7px;background:var(--accent);color:#fff;font-size:16px;line-height:1}}
.app-download-menu{{position:absolute;inset-block-start:calc(100% + 8px);inset-inline-end:0;width:240px;padding:7px;border:1px solid var(--line);border-radius:14px;background:var(--surface);box-shadow:0 18px 45px rgba(0,0,0,.18)}}
.app-download-menu a,.app-download-menu button{{display:grid;width:100%;gap:2px;padding:10px 11px;border:0;border-radius:10px;background:transparent;color:var(--ink);text-align:start;text-decoration:none;font:inherit;cursor:pointer}}
.app-download-menu a:hover,.app-download-menu button:hover{{background:var(--soft)}}
.app-download-menu b{{font-size:12px}}.app-download-menu small{{color:var(--muted);font-size:10px}}
.expnear{{padding-inline-end:3px}}
.maphero+section.sec{{padding:22px 0}}
.maphero+section.sec .hero-facts{{padding-top:14px;gap:8px}}
.maphero+section.sec .hero-facts div{{padding:10px 12px}}
.maphero+section.sec .hero-facts b{{font-size:18px}}
.maphero+section.sec .hero-facts span{{font-size:12px}}
@media(max-width:1000px){{.head-tel,.langs{{display:none}}}}
@media(max-width:760px){{
  .corner-tools{{inset-block-start:9px;inset-inline-end:10px;gap:6px}}
  .corner-tools .corner-langs{{max-width:156px;overflow-x:auto;scrollbar-width:none}}
  .corner-tools .corner-langs::-webkit-scrollbar{{display:none}}
  .corner-tools .corner-langs a{{min-width:31px;padding:6px 5px;font-size:10px}}
  .corner-tools .authtext{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
  .corner-tools .authlink{{width:42px!important;min-width:42px;padding:0}}
  .app-download summary{{width:42px;min-width:42px;padding:0}}
  .app-download-text{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
  .head-in{{grid-template-columns:auto minmax(0,1fr) auto;gap:10px;padding-inline:14px}}
  nav.main{{overflow:hidden}}
  nav.main ul>li:not(.nav-more){{display:none}}
  nav.main{{justify-self:end}}
  nav.main ul{{justify-content:flex-end}}
  .authlink{{width:42px;height:42px;padding:0;justify-content:center}}
  .authtext{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
  .account-empty{{padding:36px 20px;min-height:360px}}
}}
@media(max-width:520px){{
  .authdlg{{place-items:end center;padding:0}}
  .authcard{{width:100%;max-height:94dvh;border-radius:22px 22px 0 0;padding:24px 20px calc(20px + env(safe-area-inset-bottom))}}
  .authbrand{{width:96px;height:54px;margin-bottom:14px}}.authbrand img{{width:92px;height:50px}}
}}

/* community */
.interest-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.interest-card{{min-height:112px;padding:18px;border-radius:16px;border:1px solid var(--line);background:var(--surface);
  color:var(--ink);display:flex;flex-direction:column;justify-content:space-between;text-decoration:none}}
.interest-card:hover{{border-color:var(--brand);transform:translateY(-2px)}}
.interest-card span{{width:38px;height:38px;border-radius:12px;background:var(--grad)}}
.interest-card b{{font-size:15px}}
.community-tabs{{display:flex;gap:6px;padding:5px;margin:0 0 14px;border:1px solid var(--line);border-radius:13px;width:max-content;background:var(--bg-2)}}
.community-tabs button{{border:0;border-radius:9px;background:transparent;color:var(--ink-3);padding:9px 14px;font:700 13px/1 inherit;cursor:pointer}}
.community-tabs button.on{{background:var(--surface-2);color:var(--ink)}}
.community-app{{min-height:240px}}
.community-head{{display:flex;align-items:center;justify-content:space-between}}
.social-form{{display:grid;grid-template-columns:minmax(160px,1fr) minmax(130px,.55fr) auto;gap:8px;margin:0 0 16px;padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}}
.social-form h3{{grid-column:1/-1;margin:0 0 4px;font-size:17px}}
.social-form input,.social-form select,.social-form textarea{{min-height:42px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);padding:9px 11px;font:inherit}}
.social-form textarea,.social-form label{{grid-column:1/-1}}
#community-list{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}
.social-card{{padding:15px;border:1px solid var(--line);border-radius:14px;background:var(--surface);display:flex;flex-direction:column;gap:7px}}
.social-card p{{margin:0;color:var(--ink-2);font-size:13px;line-height:1.55}}
.social-card small{{color:var(--ink-3)}}
.review-card img{{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px}}
.stars{{color:#f6b81a!important;letter-spacing:2px}}
@media(max-width:820px){{.interest-grid,#community-list{{grid-template-columns:repeat(2,minmax(0,1fr))}}.social-form{{grid-template-columns:1fr}}}}
@media(max-width:520px){{.interest-grid,#community-list{{grid-template-columns:1fr}}.community-tabs{{width:100%;overflow:auto}}}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}
/* Planner: one-line controls, maximum map workspace */
.page-planner .page-head{{padding:18px 0 4px}}
.page-planner .page-head h1{{font-size:26px;margin-bottom:6px}}
.page-planner .page-head .lead{{font-size:14px;line-height:1.45;max-width:100ch}}
.planner-controls{{padding:12px 0!important;border-bottom:0}}
.planner-toolbar{{display:grid;grid-template-columns:minmax(180px,1.5fr) minmax(245px,1.4fr) 72px 72px minmax(155px,1fr) minmax(150px,1fr) auto auto;
  align-items:end;gap:8px;padding:10px 12px;margin:0;overflow:visible;border-radius:14px}}
.planner-toolbar>.pf{{min-width:0;gap:3px}}
.planner-toolbar>.pf:first-child{{min-width:0}}
.planner-toolbar .pf label{{font-size:11px;white-space:nowrap;color:var(--ink-3)}}
.planner-toolbar .pf select{{height:38px;min-width:112px;padding:6px 9px;font-size:13px;border-radius:9px}}
.planner-toolbar .start-field input{{width:100%;height:38px;min-width:180px;padding:6px 10px;border:1px solid var(--line);
  border-radius:9px;background:var(--bg);color:var(--ink);font:600 13px/1 var(--font)}}
.date-pair{{display:flex;gap:5px}}
.date-pair input{{height:38px;width:132px;padding:6px 8px;border:1px solid var(--line);border-radius:9px;background:var(--bg);color:var(--ink);font:600 12px/1 inherit}}
.derived-month,.tour-purpose-field,.secondary-planner-field,.planner-toolbar>.pf-check{{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;clip:rect(0 0 0 0)!important}}
.planner-toolbar .carmode{{min-width:0!important}}
.planner-toolbar .carmode{{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px}}
.planner-toolbar .carmode .tog{{height:38px!important;padding:5px 7px!important;justify-content:center;font-size:10.5px!important}}
.planner-toolbar .carmode>select{{display:none!important}}
.standard-launch{{display:flex;justify-content:flex-start;margin:0 0 10px}}
.standard-launch .btn{{height:38px;width:auto;padding:7px 14px;white-space:nowrap}}
.standard-launch .btn span:not(:empty)::before{{content:" ("}}.standard-launch .btn span:not(:empty)::after{{content:")"}}
.standard-modal{{position:fixed;z-index:2500;inset:0;display:grid;place-items:center;padding:24px;background:rgba(2,8,16,.78);backdrop-filter:blur(9px)}}
.standard-modal[hidden]{{display:none}}
.standard-dialog{{position:relative;width:min(920px,94vw);max-height:min(720px,88dvh);overflow:auto;padding:22px;background:linear-gradient(180deg,var(--surface),var(--bg));border:1px solid var(--line);border-radius:20px;box-shadow:0 30px 90px #0009}}
.standard-close{{position:absolute;inset-inline-end:14px;top:14px;width:40px;height:40px;border:1px solid var(--line);border-radius:11px;background:var(--surface-2);color:var(--ink-2);cursor:pointer}}
.standard-dialog-head{{display:grid;grid-template-columns:1fr minmax(180px,240px);align-items:end;gap:14px;margin:0 50px 18px 0}}
.standard-dialog-head h3{{margin:0;font-size:22px}}.standard-dialog-head label{{font-size:11px;color:var(--ink-3)}}
.standard-dialog-head select{{display:block;width:100%;height:40px;margin-top:5px}}
.standard-head{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
.standard-head h3{{margin:0;font-size:13px}}
.standard-head span{{color:var(--brand);font-size:11px}}
.standard-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}}
.standard-card{{min-height:92px;display:grid;grid-template-columns:76px minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px;border:1px solid var(--line);border-radius:13px;background:var(--surface-2)}}
.standard-card>img{{width:62px;height:54px;object-fit:cover;border-radius:8px}}
.standard-card:not(:has(>img)){{grid-template-columns:minmax(0,1fr) auto}}
.standard-copy{{min-width:0;display:grid;gap:2px}}
.standard-copy b{{font-size:12px;line-height:1.3}}
.standard-copy small{{font-size:10px;color:var(--ink-3)}}
.standard-copy p{{margin:0;font-size:10.5px;line-height:1.3;color:var(--ink-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.standard-card .btn{{padding:6px 8px;font-size:10.5px}}
.standard-empty{{font-size:12px;color:var(--ink-3);padding:10px}}
.planner-toolbar .carmode{{display:flex;flex-wrap:nowrap;gap:5px}}
.planner-toolbar .carmode .tog{{height:38px;padding:6px 10px;font-size:12px;white-space:nowrap}}
.planner-toolbar .pf-check{{min-width:max-content;padding-bottom:8px}}
.planner-toolbar .pf-check label{{font-size:12px;color:var(--ink-2)}}
.planner-more{{position:relative;flex:0 0 auto;min-width:max-content}}
.planner-more>summary{{height:38px;display:flex;align-items:center;padding:6px 12px;border:1px solid var(--line);
  border-radius:9px;background:var(--surface-2);font-size:12px;font-weight:650;color:var(--brand-ink);cursor:pointer;white-space:nowrap}}
.planner-more-in{{position:absolute;z-index:800;top:calc(100% + 8px);inset-inline-end:0;width:min(920px,88vw);
  max-height:62vh;overflow:auto;padding:14px;background:var(--surface);border:1px solid var(--line);
  border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.48);display:grid;gap:12px}}
.planner-more-in .chips.styles{{display:flex;flex-wrap:nowrap;overflow-x:auto;gap:6px}}
.planner-more-in .chip.style{{min-width:180px;padding:8px 10px}}
.planner-more-in .chip.style b{{font-size:13px}}
.planner-more-in .chip.style small{{font-size:10.5px}}
.planner-more-in .chips:not(.styles){{gap:5px}}
.planner-more-in .chip{{font-size:11.5px;padding:5px 9px}}
.planner-toolbar>.prow{{display:flex;flex-wrap:nowrap;min-width:max-content;margin:0}}
.planner-toolbar>.prow .btn{{width:auto!important;min-width:0!important;height:34px!important;min-height:34px!important;padding:5px 11px!important;border-radius:8px;font-size:11.5px;white-space:nowrap}}
.planner-toolbar>.prow{{grid-column:auto / span 2;width:max-content;gap:5px;align-self:end}}
.workspace-plan>.standard-launch .btn{{min-width:0;height:36px!important;padding:6px 13px!important;border-radius:9px;font-size:12px}}
.travel-workspace{{position:relative}}
.workspace-tabs{{display:inline-flex;gap:4px;margin:0 0 8px;padding:4px;background:var(--surface-2);
  border:1px solid var(--line);border-radius:12px}}
.workspace-tabs button{{min-height:34px;padding:6px 14px;border:0;border-radius:9px;background:transparent;
  color:var(--ink-3);font:700 12px/1.2 inherit;cursor:pointer}}
.workspace-tabs button.on{{color:var(--ink);background:var(--surface);box-shadow:0 1px 8px #0003}}
.workspace-plan{{display:none;margin-bottom:8px}}
.travel-workspace[data-mode="planner"] .workspace-plan{{display:block}}
.travel-workspace[data-mode="planner"] .planner-toolbar{{margin-bottom:0;padding-bottom:8px}}
.travel-workspace[data-mode="planner"] .workspace-plan+.explorer{{margin-top:0}}
.travel-workspace[data-mode="planner"] .exproutebox{{display:none}}
.travel-workspace[data-mode="route"] .expfind{{display:none}}
.travel-workspace[data-mode="route"] .exproutebox{{display:block}}
.travel-workspace[data-mode="explore"] .exproutebox{{display:none}}
.workspace-result:empty{{display:none}}
.workspace-result:not(:empty){{margin-top:12px}}
.tour-export-actions{{display:flex;align-items:center;gap:6px;flex-wrap:nowrap}}
.tour-export-actions #tourjpg,.tour-export-actions #tourpdf{{min-width:72px;font-weight:800;letter-spacing:.04em}}
.expbar .trip-save-form{{grid-column:1/-1;width:min(760px,100%);margin:0}}
@media(max-width:900px){{.tour-export-actions{{order:8;width:100%;overflow-x:auto;padding-bottom:2px}}.expbar .trip-save-form{{display:flex;align-items:end;overflow-x:auto}}}}
.page-planner .travel-workspace[data-mode="planner"] .expgrid{{grid-template-columns:minmax(250px,320px) 1fr}}
.planner-map-sec{{padding:0 0 18px!important}}
.planner-map-sec>.wrap{{max-width:none;padding:0 12px}}
.page-planner #pmap{{height:clamp(540px,calc(100dvh - 245px),820px);margin:0;border-radius:14px}}
.page-planner #result{{max-width:var(--maxw);margin:18px auto 0}}
@media(max-width:760px){{
  .page-planner .page-head{{display:none}}
  .planner-controls{{padding-top:8px!important}}
  .planner-toolbar{{border-radius:0}}
  .planner-toolbar{{display:flex;overflow-x:auto;overflow-y:visible}}
  .planner-toolbar>.pf{{flex:0 0 auto;min-width:132px}}
  .planner-toolbar>.pf:first-child{{min-width:190px}}
  .standard-dialog{{width:100%;max-height:82dvh;border-radius:20px 20px 0 0;padding:18px}}
  .standard-modal{{place-items:end center;padding:0}}
  .standard-dialog-head{{grid-template-columns:1fr;margin-right:45px}}
  .standard-grid{{grid-template-columns:1fr}}
  .workspace-tabs{{display:flex;position:sticky;top:0;z-index:5}}
  .workspace-tabs button{{flex:1;padding-inline:8px}}
  .planner-more-in{{position:fixed;inset:auto 0 0;width:100%;max-height:72dvh;border-radius:20px 20px 0 0}}
  .page-planner #pmap{{height:calc(100dvh - 176px);min-height:500px;border-radius:10px}}
}}
/* Desktop navigation rail: persistent, compact and column-based. */
.page-map .page-head{{padding:18px 0 8px}}
.page-map .page-head h1{{font-size:clamp(23px,2.2vw,32px);line-height:1.25;margin-bottom:8px;max-width:42ch}}
.page-map .page-head .lead{{font-size:14px;line-height:1.5;max-width:82ch;margin-bottom:6px}}
.page-map .sec.wide{{padding-top:10px}}
@media(min-width:1001px){{
  body{{padding-inline-start:248px}}
  .site-head{{position:fixed;inset-block:0;inset-inline-start:0;width:248px;height:100dvh;
    border-bottom:0;border-inline-end:1px solid var(--line);z-index:40;overflow-y:auto;overscroll-behavior:contain}}
  .head-in{{min-height:100%;width:100%;padding:24px 16px 18px;display:flex;flex-direction:column;
    align-items:stretch;gap:20px;margin:0}}
  .logo{{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;column-gap:10px;
    padding:4px 6px 18px;border-bottom:1px solid var(--line);font-size:18px}}
  .logo .mark,.logo img{{grid-row:1 / 3}}
  .logo small{{font-size:9px;line-height:1.35;white-space:normal}}
  nav.main{{width:100%;margin:0;justify-self:auto;overflow:visible}}
  nav.main ul{{display:flex;flex-direction:column;gap:3px;width:100%}}
  nav.main li{{width:100%;margin:0}}
  nav.main a{{width:100%;padding:10px 12px;border-radius:10px;font-size:13.5px}}
  nav.main a[aria-current="page"]{{background:color-mix(in srgb,var(--brand) 18%,var(--surface-2));
    color:var(--brand-ink);box-shadow:inset 3px 0 0 var(--brand)}}
  .nav-more{{margin-top:4px}}
  .nav-more summary{{display:flex;align-items:center;width:100%;min-height:40px;padding:8px 12px;
    border-radius:10px;letter-spacing:.18em}}
  .nav-more details>ul{{position:static;inset:auto;min-width:0;margin:4px 0 0!important;padding:4px 0 4px 12px!important;
    background:transparent;border:0;border-inline-start:1px solid var(--line);border-radius:0;box-shadow:none}}
  .nav-more details>ul a{{padding-block:8px;white-space:normal;font-size:12.5px}}
  .head-actions{{margin-top:auto;width:100%;display:flex;flex-direction:column;align-items:stretch;gap:10px;justify-self:auto}}
  .head-tel{{order:1}}
  .head-tel a{{width:100%;justify-content:center;padding:9px 10px;font-size:12.5px}}
  .langs{{order:2;width:100%;display:grid;grid-template-columns:repeat(3,1fr);border:0;padding:4px;gap:2px}}
  .langs a{{text-align:center;padding:5px 3px;font-size:11px}}
  .authbox{{order:3;width:100%;margin:0}}
  .authbox .authlink{{width:100%;justify-content:center}}
  .authbox{{position:fixed;inset-block-start:16px;inset-inline-end:18px;width:auto!important;z-index:70}}
  .authbox .authlink{{width:auto;min-width:44px;justify-content:center;background:rgba(11,20,31,.94);backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.34)}}
}}
@media(max-width:760px){{
  .page-map .page-head{{padding:14px 0 5px}}
  .page-map .page-head h1{{font-size:21px;margin-bottom:6px}}
  .page-map .page-head .lead{{font-size:13px;line-height:1.45}}
  html,body{{max-width:100%;overflow-x:hidden}}
  .wrap,.wrap.wide{{width:100%;max-width:100%;padding-inline:12px}}
  .head-in{{display:grid;grid-template-columns:minmax(0,1fr) auto;padding:10px 12px;gap:8px}}
  .logo{{min-width:0;font-size:15px;gap:6px}}
  .logo small{{display:none}}
  nav.main{{grid-column:2;grid-row:1;overflow:visible}}
  nav.main ul>li:not(.nav-more){{display:none!important}}
  .head-actions{{grid-column:1 / -1;grid-row:2;display:flex;justify-content:flex-end}}
  .head-tel,.langs{{display:none!important}}
  nav.main{{margin-inline-end:48px}}
  .authbox{{position:fixed;inset-block-start:10px;inset-inline-end:12px;width:auto;margin:0;z-index:70}}
  .authbox .authlink{{width:42px;min-width:42px;background:rgba(11,20,31,.94);backdrop-filter:blur(10px)}}
  .site-head{{min-height:0}}
  .expbar{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px;padding:8px}}
  .expsearch{{grid-column:1/-1;min-width:0;width:100%}}
  .expbar input,.expbar select{{min-width:0;width:100%;font-size:13px;padding:7px 8px}}
  .expfilters{{min-width:0}}
  .expfilters>summary{{width:100%;height:36px;font-size:12px}}
  .expfilters-pop{{position:fixed;inset:auto 10px 10px;width:auto;max-height:72dvh;overflow:auto;border-radius:18px;z-index:1800}}
  .expdate{{grid-column:1/-1}}
  .expgrid{{min-width:0;display:flex;flex-direction:column}}
  .expmapwrap{{order:1;height:calc(100dvh - 250px);min-height:430px;max-height:620px}}
  .expside{{order:2;max-height:62dvh;border-bottom:0;border-top:1px solid var(--line)}}
  .travel-workspace[data-mode="explore"] .expside,
  .travel-workspace[data-mode="planner"] .expside{{height:62dvh}}
  .expside,.expmapwrap{{min-width:0;width:100%}}
  .planner-toolbar{{max-width:100%;padding:8px}}
  .planner-more-in{{max-width:100vw}}
}}

/* Flat travel product language: restrained surfaces, clear hierarchy, no 3D chrome. */
.hero{{background:var(--bg);border-bottom:1px solid var(--line);box-shadow:none}}
.hero .kicker{{color:var(--accent);font-weight:700}}
.hero.tight{{padding-block:18px 14px}}
.site-head,.travel-workspace,.explorer,.expbar,.expside,.expmapwrap,.planner-toolbar,
.workspace-tabs,.home-more,.journey-steps article,.card,.surface,.booking-card{{box-shadow:none}}
.logo img{{filter:none}}
.head-tel a,.btn{{background:var(--brand);border:0;border-radius:10px;box-shadow:none;filter:none}}
.head-tel a:hover,.btn:hover{{background:var(--brand-2);filter:none}}
.btn.ghost,.btn.alt{{background:transparent;border:1px solid var(--line);border-radius:10px}}
.workspace-tabs{{border:1px solid var(--line);border-radius:10px;background:transparent;padding:3px}}
.workspace-tabs button{{border-radius:7px}}
.workspace-tabs button.on{{background:var(--surface-2);box-shadow:none}}
.travel-workspace{{border-radius:12px}}
.planner-toolbar,.expbar{{background:var(--surface);border-radius:0}}
.place-choice,.standard-card,.booking-card{{background:var(--surface);border-radius:10px;box-shadow:none}}
.place-choice.on{{background:color-mix(in srgb,var(--brand) 8%,var(--surface))}}
.mapcluster b,.placecluster b{{border:2px solid #fff!important;box-shadow:0 0 0 2px rgba(32,201,189,.18)!important}}
.mapcluster.visited b,.placecluster.visited b{{box-shadow:0 0 0 2px rgba(123,135,149,.16)!important}}
.authcard,.booking-modal-card,.standard-dialog{{background:var(--surface);border-radius:14px;box-shadow:0 18px 55px rgba(0,0,0,.34)}}
.corner-tools .corner-langs,.corner-tools .authlink,.authbox .authlink{{backdrop-filter:none;box-shadow:none;background:var(--surface)}}

.journey-flow{{padding:28px 0;border-block:1px solid var(--line);background:var(--bg)}}
.journey-flow-head{{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:18px}}
.journey-flow-head h2{{margin:0 0 4px;font-size:clamp(20px,2.2vw,28px)}}
.journey-flow-head p{{margin:0;color:var(--ink-2);font-size:14px}}
.text-link{{font-weight:700;font-size:14px;white-space:nowrap}}
.journey-steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.journey-steps article{{display:flex;gap:12px;align-items:flex-start;padding:15px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}}
.journey-steps article>span{{display:grid;place-items:center;flex:0 0 28px;width:28px;height:28px;border-radius:50%;background:var(--brand);color:var(--on-brand);font-size:12px;font-weight:800}}
.journey-steps h3{{margin:1px 0 3px;font-size:15px}}
.journey-steps p{{margin:0;color:var(--ink-2);font-size:12.5px;line-height:1.45}}
.home-hero{{padding:34px 0 28px!important;background:var(--bg)!important}}
.home-hero .wrap{{display:grid;justify-items:start}}
.home-hero h1{{max-width:22ch;font-size:clamp(30px,4vw,48px);margin-bottom:10px}}
.home-hero .lead{{max-width:62ch;font-size:clamp(15px,1.5vw,18px);margin-bottom:18px}}
.home-hero-actions{{display:flex;flex-wrap:wrap;gap:9px}}
.home-hero-actions .btn{{min-height:44px;padding-inline:18px;text-decoration:none}}
.home-hero-note{{margin:11px 0 0;color:var(--ink-3);font-size:12px}}
.map-intro{{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:12px}}
.map-intro h2{{margin:0;font-size:clamp(19px,2vw,24px)}}
.map-intro .map-sub{{margin:0;max-width:68ch;text-align:end;font-size:13px;color:var(--ink-2)}}
.maphero{{scroll-margin-top:20px}}
@media(max-width:700px){{
  .home-hero{{padding:26px 0 22px!important}}
  .home-hero h1{{font-size:30px}}
  .home-hero-actions{{display:grid;width:100%}}
  .home-hero-actions .btn{{width:100%;justify-content:center}}
  .map-intro{{display:block}}
  .map-intro .map-sub{{margin-top:5px;text-align:start}}
  .journey-flow{{padding-block:22px}}
  .journey-flow-head{{display:grid;align-items:start}}
  .journey-steps{{grid-template-columns:1fr}}
  .journey-steps article{{padding:12px}}
}}
/* 2026 UX reset: calm, flat and task-first. */
:root{{
  --ink:#17202b;--ink-2:#526170;--ink-3:#718091;--line:#dfe6ec;--line-2:#e9eef2;
  --bg:#f5f7f9;--bg-2:#eef2f5;--bg-3:#e7edf1;--surface:#ffffff;--surface-2:#f7f9fb;
  --brand:#087f8c;--brand-2:#066d78;--brand-ink:#102a32;--accent:#087f8c;--on-brand:#fff;
  --radius:12px
}}
body{{font-size:14px;line-height:1.5;background:var(--bg);color:var(--ink)}}
a{{color:#087f8c}}
.site-head{{background:#fff}}
.btn,.head-tel a{{min-height:42px;padding:9px 16px;border-radius:9px;background:#087f8c;color:#fff;font-weight:750}}
.btn:hover,.head-tel a:hover{{background:#066d78;text-decoration:none}}
.btn.alt,.btn.ghost{{background:#fff;color:#1d3a42;border:1px solid #ccd8de}}
.btn.alt:hover,.btn.ghost:hover{{background:#f2f6f7;color:#102a32}}

/* A first screen that answers “what can I do here?” immediately. */
.home-hero{{padding:40px 0 34px!important;background:#fff!important;border-bottom:1px solid var(--line)!important;color:var(--ink)!important}}
.home-hero-grid{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(330px,.75fr);gap:clamp(30px,6vw,88px);align-items:center}}
.home-hero-copy{{min-width:0}}
.home-hero .kicker{{margin:0 0 10px;color:#087f8c;font-size:11px;letter-spacing:.08em}}
.home-hero h1{{max-width:16ch;margin:0 0 12px;color:#15262d;font-size:clamp(32px,4.2vw,54px);line-height:1.08;letter-spacing:-.035em}}
.home-hero .lead{{max-width:58ch;margin:0 0 20px;color:#526170;font-size:15px;line-height:1.55}}
.home-hero-actions{{display:flex;gap:9px;flex-wrap:wrap}}
.home-hero-note{{margin:10px 0 0;color:#718091;font-size:11.5px}}
.home-quick{{display:grid;gap:8px;padding:8px;border:1px solid #dfe6ec;border-radius:16px;background:#f7f9fb}}
.home-quick-card{{display:grid;grid-template-columns:32px minmax(0,1fr) auto;align-items:center;gap:10px;min-height:64px;padding:10px 12px;border:1px solid transparent;border-radius:11px;color:#17202b;background:#fff;text-decoration:none}}
.home-quick-card:hover{{border-color:#a9cbd0;background:#fbfefe;text-decoration:none}}
.home-quick-card>span{{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:#e6f4f4;color:#087f8c;font-size:12px;font-weight:800}}
.home-quick-card div{{display:grid;gap:2px}}
.home-quick-card b{{font-size:13px;color:#17202b}}
.home-quick-card small{{font-size:11px;color:#718091}}
.home-quick-card i{{font-style:normal;color:#087f8c;font-size:18px}}

/* Keep the map central and remove decorative detours. */
.journey-flow{{padding:22px 0;background:#f5f7f9}}
.journey-flow-head{{margin-bottom:12px}}
.journey-flow-head h2{{font-size:19px}}
.journey-flow-head p{{font-size:12.5px}}
.journey-steps{{gap:8px}}
.journey-steps article{{min-height:0;padding:12px 14px;border-radius:10px;background:#fff}}
.journey-steps article>span{{width:28px;height:28px;font-size:11px;background:#e6f4f4;color:#087f8c}}
.journey-steps h3{{font-size:13px}}
.journey-steps p{{font-size:11.5px}}
.maphero{{padding:22px 0 28px!important;background:#f5f7f9}}
.map-intro{{margin:0 0 10px}}
.map-intro h2{{font-size:20px;color:#17202b}}
.map-intro .map-sub{{font-size:12.5px;color:#718091}}
.travel-workspace,.explorer{{border-color:#d9e2e8;border-radius:14px;background:#fff}}
.workspace-tabs{{margin:0 0 7px;background:#edf2f5;border:0}}
.workspace-tabs button{{color:#687786}}
.workspace-tabs button.on{{background:#fff;color:#17202b}}
.planner-toolbar,.expbar{{background:#fff;border-bottom:1px solid #e1e8ed}}
.planner-toolbar input,.planner-toolbar select,.expbar input,.expbar select{{background:#fff!important;color:#17202b!important;border-color:#d7e0e6!important}}
.expside{{background:#fff}}
.expside button,.expside .tog{{box-shadow:none}}
.place-choice{{background:#fff;border-color:#e0e7ec}}
.place-choice.on{{background:#edf8f7;border-color:#43aeb1}}
.place-choice.candidate{{background:#f4f6f7;border-color:#dfe5e9;color:#526170}}
.place-choice.candidate:not(.blocked){{background:#fff;border-color:#b9d7d9;color:#17202b}}
.place-choice.blocked{{filter:grayscale(1);opacity:.48;cursor:not-allowed}}
.place-choice.blocked input{{cursor:not-allowed}}
.choice-group{{margin:0 0 12px}}
.choice-group h4{{position:sticky;top:0;z-index:2;display:flex;align-items:center;justify-content:space-between;
  gap:8px;margin:0 0 6px;padding:7px 8px;background:var(--surface);border-bottom:1px solid var(--line);
  color:var(--brand-ink);font-size:11.5px;line-height:1.2}}
.choice-group h4 span{{display:grid;place-items:center;min-width:24px;height:22px;padding:0 6px;border-radius:999px;
  background:var(--surface-2);color:var(--ink-2);font:700 11px var(--mono)}}
.choice-group.muted h4{{color:var(--ink-3)}}
.place-fit{{display:inline-flex;margin-top:3px;padding:2px 6px;border-radius:999px;background:#e8f6f3;
  color:#167a70;font-size:10px;font-weight:700;line-height:1.25}}
.place-fit.blocked{{background:#e9edf0;color:#66727e}}
.legend{{background:#fff;border-color:#e0e7ec}}
.home-more-wrap{{padding:18px 0 30px;background:#f5f7f9}}
.home-more{{background:#fff;border-color:#dfe6ec}}

/* The rail is navigation, not the main visual. */
@media(min-width:1001px){{
  body{{padding-inline-start:220px}}
  .site-head{{width:220px;border-inline-end:1px solid #dfe6ec}}
  .head-in{{padding:20px 14px 16px;gap:15px}}
  .logo{{padding:2px 5px 14px}}
  nav.main a{{padding:9px 11px;color:#526170;font-size:12.5px}}
  nav.main a[aria-current="page"]{{background:#e8f3f4;color:#14505a;box-shadow:inset 3px 0 0 #1597a3}}
  .head-tel a{{font-size:11.5px}}
  .langs{{background:#f3f6f8;border-radius:10px}}
  .corner-tools .corner-langs,.corner-tools .authlink,.authbox .authlink{{background:#fff!important;color:#17202b;border:1px solid #dfe6ec}}
}}
@media(max-width:900px){{
  .home-hero-grid{{grid-template-columns:1fr;gap:22px}}
  .home-quick{{grid-template-columns:repeat(3,minmax(0,1fr))}}
  .home-quick-card{{grid-template-columns:28px 1fr;align-items:start}}
  .home-quick-card i{{display:none}}
}}
@media(max-width:600px){{
  .home-hero{{padding:24px 0 20px!important}}
  .home-hero h1{{font-size:32px;max-width:18ch}}
  .home-hero .lead{{font-size:14px}}
  .home-quick{{grid-template-columns:1fr}}
  .journey-flow{{display:none}}
  .maphero{{padding-top:14px!important}}
}}
/* Compact desktop pass: map-first, with the full canvas used efficiently. */
html,body{{max-width:100%;overflow-x:hidden}}
@media(min-width:1001px){{
  .home-hero{{padding:20px 0 16px!important}}
  .home-hero-grid{{max-width:1560px;grid-template-columns:minmax(0,1.55fr) minmax(320px,420px);gap:32px;align-items:center}}
  .home-hero h1{{max-width:24ch;margin:0 0 8px;font-size:clamp(30px,2.35vw,40px);line-height:1.16;letter-spacing:-.02em;font-weight:700}}
  .home-hero .lead{{max-width:72ch;margin:0 0 12px;font-size:14px;line-height:1.45}}
  .home-hero-actions{{gap:8px}}
  .home-hero-actions .btn{{min-height:38px;padding:8px 14px;font-size:13px}}
  .home-hero-note{{margin-top:7px;font-size:11px}}
  .home-quick{{gap:6px;padding:6px;border-radius:12px}}
  .home-quick-card{{grid-template-columns:26px minmax(0,1fr) auto;gap:8px;min-height:48px;padding:7px 9px;border-radius:9px}}
  .home-quick-card>span{{width:24px;height:24px;border-radius:6px;font-size:10px}}
  .home-quick-card b{{font-size:12px}}
  .home-quick-card small{{font-size:10px}}
  .home-quick-card i{{font-size:15px}}
  .journey-flow{{display:none}}
  .maphero{{padding:12px 0 24px!important}}
  .maphero>.wrap.wide{{max-width:1560px}}
  .map-intro{{display:flex;align-items:baseline;justify-content:space-between;gap:20px;margin:0 0 8px}}
  .map-intro h2{{margin:0;font-size:18px}}
  .map-intro .map-sub{{margin:0;font-size:11.5px;white-space:nowrap}}
}}
@media(min-width:1001px) and (max-width:1200px){{
  .home-hero-grid{{grid-template-columns:minmax(0,1fr) 320px;gap:22px}}
  .map-intro .map-sub{{white-space:normal}}
}}
/* Planner result summary: six compact facts instead of oversized empty cards. */
#result>.facts{{grid-template-columns:repeat(6,minmax(0,1fr));gap:7px;margin:8px 0 10px}}
#result>.facts>div{{min-height:54px;padding:8px 11px;border-radius:9px;display:flex;flex-direction:column;justify-content:center}}
#result>.facts .k{{margin:0 0 2px;font-size:10.5px;line-height:1.25}}
#result>.facts .v{{font-size:13.5px;line-height:1.25}}
#result>.psum{{max-width:none;margin:0 0 12px;padding:9px 12px;font-size:12.5px;line-height:1.45}}
/* The former dark theme forced fact values to white; keep them readable on light cards. */
.facts dd,.facts .v{{color:var(--brand-ink)!important}}
@media(max-width:1100px){{#result>.facts{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
@media(max-width:600px){{
  #result>.facts{{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}}
  #result>.facts>div{{min-height:50px;padding:7px 9px}}
}}
@media(max-width:900px){{
  .home-hero{{padding:16px 0 12px!important}}
  .home-hero h1{{font-size:28px;line-height:1.16;max-width:22ch}}
  .home-quick{{display:none}}
  .maphero{{padding-top:10px!important}}
}}

/* Clear section rhythm using restrained white tones. */
.home-hero{{background:#fff!important;border-bottom:1px solid #dfe6e9!important}}
.maphero{{background:#f5f7f8!important;border-block:1px solid #dfe6e9}}
.home-more-wrap{{background:#fff}}
.home-more-wrap .sec:nth-of-type(even),main>.sec.alt{{background:#f7f8f9}}
.home-more-wrap .sec:nth-of-type(odd),main>.sec:not(.alt):not(.maphero){{background:#fff}}
main>.sec+section.sec{{border-top:1px solid #e3e8eb}}

/* Installable Android/iPhone application prompt. */
.app-install-card{{position:fixed;z-index:95;inset-inline-end:18px;bottom:18px;width:min(430px,calc(100% - 36px));display:grid;grid-template-columns:48px minmax(0,1fr) auto 28px;align-items:center;gap:10px;padding:12px;background:rgba(255,255,255,.98);border:1px solid #d7e0e4;border-radius:16px;box-shadow:0 18px 48px rgba(20,38,45,.18);color:#15262d}}
.app-install-card img{{width:48px;height:48px;border-radius:12px}}
.app-install-card div{{display:grid;gap:2px}}
.app-install-card strong{{font-size:13px;line-height:1.3}}
.app-install-card span{{font-size:11px;line-height:1.35;color:#667681}}
.app-install-action{{min-height:38px;padding:7px 12px;border:0;border-radius:10px;background:#0d8e98;color:#fff;font:700 12px var(--font);cursor:pointer}}
.app-install-close{{width:28px;height:28px;padding:0;border:0;background:transparent;color:#657681;font-size:20px;cursor:pointer}}
@media(max-width:600px){{
  .app-install-card{{inset-inline:10px;bottom:10px;width:auto;grid-template-columns:42px minmax(0,1fr) auto 24px;padding:10px;gap:8px;border-radius:14px}}
  .app-install-card img{{width:42px;height:42px;border-radius:10px}}
  .app-install-card span{{font-size:10px}}
  .app-install-action{{padding-inline:10px}}
}}

/* Localized electronic business card — Road Pass. */
.business-card-link{{display:inline-flex;align-items:center;min-height:42px;padding:9px 13px;border:1px solid #ccd8de;border-radius:9px;background:#fff;color:#1d3a42;font-size:13px;font-weight:750;text-decoration:none}}
.business-card-link:hover{{background:#f2f6f7;text-decoration:none}}
.digital-card-page{{min-height:calc(100vh - 220px);display:grid;place-items:center;padding:58px 18px;background:#eef2f5}}
.digital-card-shell{{width:min(900px,100%)}}
.card-languages{{display:flex;justify-content:center;gap:5px;margin:0 auto 14px;padding:5px;width:max-content;max-width:100%;overflow-x:auto;background:#fff;border:1px solid #dfe6ec;border-radius:12px;box-shadow:0 8px 24px rgba(8,21,33,.08)}}
.card-languages a{{min-width:39px;padding:7px 9px;border-radius:8px;color:#526170;font-size:12px;font-weight:700;text-align:center;text-decoration:none}}.card-languages a:hover{{background:#e6f4f4;text-decoration:none}}.card-languages a.on{{background:#087f8c;color:#fff}}
.road-pass-card{{overflow:hidden;background:#fff;border:1px solid #dfe6ec;border-radius:16px;box-shadow:0 24px 64px rgba(8,21,33,.15)}}
.road-pass-top{{min-height:72px;padding:16px 28px;display:flex;align-items:center;justify-content:space-between;gap:18px;background:#081521;color:#fff;letter-spacing:.13em}}
.road-pass-top strong{{font-size:18px;letter-spacing:.05em;white-space:nowrap;color:#fff}}.road-pass-top strong span{{color:#38bdf8;font-size:26px}}
.road-pass-body{{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:34px;padding:38px}}
.road-pass-identity{{padding-inline-end:34px;border-inline-end:2px dotted #98a6b4}}
.road-pass-brand{{display:flex;align-items:center;gap:16px;margin-bottom:20px}}.road-pass-brand img{{width:126px;height:66px;object-fit:contain}}.road-pass-brand b{{font-size:30px;color:#081521}}
.road-pass-identity h1{{margin:0 0 8px;color:#081521;font-size:40px;line-height:1.2}}.road-pass-role{{margin:0 0 24px;color:#526170;font-size:16px}}
.card-contact-line{{width:max-content;max-width:100%;display:flex;align-items:center;gap:12px;margin:12px 0;color:#17202b;font-size:18px;font-weight:700;text-decoration:none}}
.card-contact-line span{{width:34px;height:34px;display:grid;place-items:center;border:1.5px solid #087f8c;border-radius:50%;color:#087f8c}}.card-contact-line:hover,.card-site{{color:#087f8c;text-decoration:none}}
.card-save{{margin-top:18px}}.road-pass-qr{{display:grid;align-content:center;justify-items:center;text-align:center}}.road-pass-qr a{{display:block;padding:12px;border:2px solid #087f8c;border-radius:13px;background:#fff}}.road-pass-qr img{{display:block;width:220px;height:220px}}.road-pass-qr p{{max-width:24ch;margin:13px 0 0;color:#526170;font-size:14px;line-height:1.5}}
html[dir="rtl"] .road-pass-brand{{flex-direction:row-reverse;justify-content:flex-end}}
@media(max-width:760px){{.head-actions .business-card-link{{font-size:0;width:42px;padding:0;justify-content:center}}.head-actions .business-card-link::before{{content:"▣";font-size:18px}}.digital-card-page{{padding:28px 12px}}.road-pass-top{{padding:13px 17px;font-size:10px}}.road-pass-top strong{{font-size:13px}}.road-pass-body{{grid-template-columns:1fr;padding:24px;gap:25px}}.road-pass-identity{{padding:0 0 24px;border-inline-end:0;border-bottom:2px dotted #98a6b4}}.road-pass-brand img{{width:94px;height:50px}}.road-pass-brand b{{font-size:24px}}.road-pass-identity h1{{font-size:31px}}.road-pass-role{{font-size:14px}}.road-pass-qr img{{width:190px;height:190px}}}}
"""
