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

    return f""":root{{
  --ink:{d['color_ink']};
  --ink-2:{d['color_ink_2']};
  --ink-3:color-mix(in srgb,{d['color_ink_2']} 72%,#ffffff);
  --line:{d['color_line']};
  --line-2:color-mix(in srgb,{d['color_line']} 55%,#ffffff);
  --bg:{d['color_bg']};
  --bg-2:{d['color_bg_2']};
  --bg-3:color-mix(in srgb,{d['color_brand']} 8%,#ffffff);
  --brand:{d['color_brand']};
  --brand-2:{d['color_brand_2']};
  --brand-ink:{d['color_brand_ink']};
  --accent:{d['color_accent']};
  --ok:{d['color_ok']};
  --radius:{d['radius']}px;
  --maxw:{d['max_width']}px;
  --font:{d['font_family']};
}}

*,*::before,*::after{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth}}
body{{margin:0;font-family:var(--font);color:var(--ink);background:var(--bg);
  font-size:{d['base_font_size']}px;line-height:1.72;font-weight:400;
  text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;height:auto;display:block}}
a{{color:var(--brand-2);text-decoration:none}}
a:hover{{text-decoration:underline}}
a:focus-visible{{outline:3px solid var(--accent);outline-offset:2px;border-radius:3px}}

.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 20px}}
.skip{{position:absolute;inset-inline-start:-9999px}}
.skip:focus{{inset-inline-start:12px;top:12px;z-index:99;background:#fff;padding:10px 16px;border:2px solid var(--brand);border-radius:6px}}

/* Header */
.site-head{{border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:20}}
.head-in{{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:14px 20px;max-width:var(--maxw);margin:0 auto}}
.logo{{display:flex;align-items:center;gap:8px;font-weight:700;font-size:20px;color:var(--brand-ink);letter-spacing:-.2px}}
.logo:hover{{text-decoration:none}}
.logo img{{height:{d['logo_height']}px;width:auto}}
.logo .dot{{width:9px;height:9px;border-radius:50%;background:var(--accent)}}
.logo small{{font-weight:500;font-size:12px;color:var(--ink-3);letter-spacing:.06em;text-transform:uppercase}}
nav.main{{margin-inline-start:auto}}
nav.main ul{{display:flex;flex-wrap:wrap;gap:2px;list-style:none;margin:0;padding:0}}
nav.main a{{display:block;padding:7px 10px;border-radius:7px;color:var(--ink-2);font-size:15px;font-weight:500}}
nav.main a:hover{{background:var(--bg-3);color:var(--brand-ink);text-decoration:none}}
nav.main a[aria-current="page"]{{background:var(--brand);color:#fff}}
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
table{{border-collapse:collapse;width:100%;font-size:15.5px;background:#fff}}
caption{{text-align:start;font-size:14px;color:var(--ink-3);padding:12px 14px;border-bottom:1px solid var(--line);background:var(--bg-2);font-weight:500}}
th,td{{padding:11px 14px;text-align:start;border-bottom:1px solid var(--line-2);vertical-align:top}}
thead th{{background:var(--bg-3);color:var(--brand-ink);font-weight:700;font-size:14px;white-space:nowrap}}
tbody tr:last-child td{{border-bottom:0}}
tbody tr:nth-child(even){{background:color-mix(in srgb,var(--bg-2) 45%,#ffffff)}}
td:first-child{{font-weight:600;color:var(--ink)}}

/* Cards */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:18px;margin:6px 0 24px}}
.card{{border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;background:#fff}}
.card h3{{margin:0 0 8px;font-size:17.5px;color:var(--brand-ink)}}
.card p{{font-size:15.5px;color:var(--ink-2);margin:0 0 12px}}
.card ul{{font-size:15px;margin:0;padding-inline-start:19px;color:var(--ink-2)}}
.card .tag{{display:inline-block;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--brand-2);background:var(--bg-3);padding:3px 9px;border-radius:20px;margin-bottom:10px}}
.card .price{{font-size:15px;font-weight:700;color:var(--ok);margin-top:12px;display:block}}

/* Car cards */
.cars{{display:grid;grid-template-columns:repeat(auto-fit,minmax(288px,1fr));gap:20px;margin:8px 0 26px}}
.car{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:#fff;display:flex;flex-direction:column}}
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
.facts div{{background:#fff;padding:16px 18px}}
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
.post-c{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:#fff;display:flex;flex-direction:column}}
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
.note{{border-inline-start:4px solid var(--accent);background:color-mix(in srgb,{d['color_accent']} 9%,#ffffff);padding:14px 18px;border-radius:0 8px 8px 0;margin:0 0 22px;font-size:15.5px;color:var(--ink-2);max-width:74ch}}
.note strong{{color:var(--brand-ink)}}
.cta{{background:var(--bg-3);border:1px solid var(--line);border-radius:var(--radius);padding:26px 28px;margin:30px 0 0}}
.cta h2{{margin:0 0 8px;font-size:22px}}
.cta p{{margin:0 0 6px;color:var(--ink-2)}}
.cta .row{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
.btn{{display:inline-block;background:var(--brand);color:#fff;padding:11px 22px;border-radius:8px;font-weight:600;font-size:15.5px}}
.btn:hover{{background:var(--brand-2);text-decoration:none}}
.btn.ghost{{background:#fff;color:var(--brand-ink);border:1px solid var(--line)}}
.btn.ghost:hover{{background:var(--bg-2)}}

/* Footer */
.site-foot{{background:{d['color_brand_ink']};color:#a9c0d4;padding:46px 0 26px;font-size:15px;margin-top:20px}}
.foot-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:28px}}
.site-foot h2{{color:#fff;font-size:14px;letter-spacing:.09em;text-transform:uppercase;margin:0 0 12px;font-weight:600}}
.site-foot ul{{list-style:none;margin:0;padding:0}}
.site-foot li{{margin:0 0 7px}}
.site-foot a{{color:#cfe0ef}}
.site-foot p{{color:#8fa7bd;font-size:14.5px;margin:0 0 8px}}
.foot-bottom{{border-top:1px solid rgba(255,255,255,.12);margin-top:30px;padding-top:18px;font-size:13.5px;color:#7f97ad;display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between}}

/* Map */
.gmap{{width:100%;border:1px solid var(--line);border-radius:var(--radius);margin:0 0 10px;z-index:1}}
.map-hint{{font-size:14.5px;color:var(--ink-3);margin:0 0 18px}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;font-size:14px;color:var(--ink-2);
  border:1px solid var(--line);border-radius:var(--radius);padding:14px 18px;background:#fff}}
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
.explorer{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:#fff}}
.expbar{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:12px 14px;
  border-bottom:1px solid var(--line);background:var(--bg-2)}}
.expsearch{{flex:1 1 240px;min-width:180px}}
.expbar input,.expbar select{{font:inherit;font-size:15px;padding:9px 12px;border:1px solid var(--line);
  border-radius:10px;background:#fff;color:var(--ink)}}
.expcount{{font-size:14px;color:var(--ink-3);margin-inline-start:auto}}
.expgrid{{display:grid;grid-template-columns:352px 1fr;height:var(--exph,72vh);min-height:520px}}
.expside{{border-inline-end:1px solid var(--line);display:flex;flex-direction:column;min-height:0;
  background:var(--bg-2)}}
.exproutebox{{padding:12px 14px;border-bottom:1px solid var(--line);background:#fff}}
.exppair{{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:end}}
.exppair label{{position:relative;font-size:12.5px;color:var(--ink-3);display:block}}
.exppair input{{width:100%;font:inherit;font-size:14.5px;padding:8px 10px;margin-top:4px;
  border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink)}}
.expsug{{display:none;position:absolute;z-index:600;inset-inline-start:0;top:100%;width:260px;
  background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 30px rgba(0,0,0,.14);
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
.expitem:hover{{background:#fff}}
.expitem i{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-inline-end:8px;
  border:2px solid #fff;box-shadow:0 0 0 1px var(--line)}}
.expitem-n{{font-weight:600;font-size:14.5px}}
.expitem-m{{display:block;font-size:12.5px;color:var(--ink-3);margin-inline-start:19px}}
.expmapwrap{{position:relative;min-height:0}}
.expmap{{position:absolute;inset:0;z-index:1}}
.exppanel{{position:absolute;top:0;bottom:0;inset-inline-end:0;width:min(460px,92%);background:#fff;
  border-inline-start:1px solid var(--line);z-index:500;overflow:auto;padding:20px 22px 40px;
  transform:translateX(103%);transition:transform .22s ease;box-shadow:-14px 0 40px rgba(0,0,0,.10)}}
[dir="rtl"] .exppanel{{transform:translateX(-103%)}}
.exppanel.on{{transform:none}}
.exppanel h3{{margin:0 26px 10px 0;font-size:23px;color:var(--brand-ink)}}
[dir="rtl"] .exppanel h3{{margin:0 0 10px 26px}}
.exppanel h4{{margin:18px 0 6px;font-size:16px;color:var(--brand-ink)}}
.exppanel .article{{font-size:15px}}
.expclose{{position:absolute;top:12px;inset-inline-end:14px;border:1px solid var(--line);
  background:#fff;border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:14px;color:var(--ink-2)}}
.exptags{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}}
.exptags .tag{{background:var(--brand);color:#fff;border-radius:999px;padding:4px 11px;font-size:12.5px;
  font-weight:600;display:inline-block}}
.exptags .tag.u{{background:#7d5ba6;color:#fff}}
.exptags .tag.g{{background:var(--bg-2);color:var(--ink-2);border:1px solid var(--line)}}
.expact{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}}
.chips{{display:flex;gap:7px;flex-wrap:wrap}}
.chip{{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;font:inherit;
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
  border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px;background:#fff;margin:0 0 24px}}
.pf{{display:flex;flex-direction:column;gap:6px;min-width:0}}
.pf-wide{{grid-column:1/-1}}
.pf label{{font-size:14px;font-weight:600;color:var(--brand-ink)}}
.pf label small{{font-weight:400;color:var(--ink-3);font-size:13px;margin-inline-start:6px}}
.pf .cnt{{color:var(--brand-2);font-weight:700}}
.pf select{{font:inherit;font-size:15.5px;padding:9px 11px;border:1px solid var(--line);
  border-radius:8px;background:#fff;color:var(--ink);max-width:100%}}
.pf-check label{{font-weight:500;display:flex;align-items:center;gap:8px;cursor:pointer}}
.pf-check input{{width:17px;height:17px;accent-color:var(--brand)}}
.prow{{display:flex;gap:10px;flex-wrap:wrap;margin-top:2px}}
.chips{{display:flex;flex-wrap:wrap;gap:7px}}
.chip{{font:inherit;font-size:14px;padding:6px 13px;border:1px solid var(--line);background:#fff;
  color:var(--ink-2);border-radius:20px;cursor:pointer;transition:none}}
.chip:hover{{border-color:var(--brand-2);color:var(--brand-ink)}}
.chip.on{{background:var(--brand);border-color:var(--brand);color:#fff;font-weight:600}}
.pday{{border:1px solid var(--line);border-radius:var(--radius);background:#fff;padding:20px 24px;margin:0 0 18px}}
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
  nav.main{{width:100%;margin-inline-start:0;order:3}}
  nav.main ul{{gap:0}}
  nav.main a{{padding:6px 9px;font-size:14.5px}}
  .langs{{margin-inline-start:auto;border:0;padding-inline-start:0}}
  .head-tel{{display:none}}
  .hero{{padding:44px 0 40px}}
  .sec{{padding:36px 0}}
  .site-head{{position:static}}
}}
@media (max-width:520px){{ .facts{{grid-template-columns:1fr}} }}
@media print{{ .site-head,.site-foot,.cta{{display:none}} body{{font-size:12pt}} }}
"""
