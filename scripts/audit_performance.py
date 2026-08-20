"""Measure generated pages in Edge and document the performance baseline."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import functools
import json
import math
import os
import statistics
import threading
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def p75(values: list[float | int | None]) -> float | None:
    clean = sorted(float(x) for x in values if x is not None)
    if not clean:
        return None
    return clean[max(0, math.ceil(len(clean) * 0.75) - 1)]


def human_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.resources: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "link" and data.get("rel") == "stylesheet" and data.get("href"):
            self.resources.append({"kind": "css", "url": data["href"], "blocking": True})
        elif tag == "script" and data.get("src"):
            blocking = not ("defer" in data or "async" in data or data.get("type") == "module")
            self.resources.append({"kind": "js", "url": data["src"], "blocking": blocking})
        elif tag == "img" and data.get("src") and data.get("loading") != "lazy":
            self.resources.append({"kind": "image", "url": data["src"], "blocking": False})


def local_path(dist: Path, url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return dist / parsed.path.lstrip("/")


def static_page_metrics(dist: Path, relative: str) -> dict[str, object]:
    page = dist / relative
    parser = ResourceParser()
    parser.feed(page.read_text(encoding="utf-8"))
    totals = {"css": 0, "js": 0, "image": 0}
    missing: list[str] = []
    local_resources = []
    for item in parser.resources:
        path = local_path(dist, str(item["url"]))
        if path is None:
            continue
        if not path.exists():
            missing.append(str(item["url"]))
            continue
        size = path.stat().st_size
        item = dict(item, bytes=size, path=str(path.relative_to(dist)))
        local_resources.append(item)
        totals[str(item["kind"])] += size
    html_bytes = page.stat().st_size
    return {
        "page": relative.replace("\\", "/"),
        "html_bytes": html_bytes,
        "local_css_bytes": totals["css"],
        "local_js_bytes": totals["js"],
        "local_image_bytes": totals["image"],
        "local_initial_total_bytes": html_bytes + sum(totals.values()),
        "blocking_script_count": sum(1 for x in local_resources if x["kind"] == "js" and x["blocking"]),
        "resources": local_resources,
        "missing": missing,
    }


@dataclass
class BrowserResult:
    page: str
    scenario: str
    run: int
    dom_content_loaded_ms: float | None
    load_ms: float | None
    first_contentful_paint_ms: float | None
    shell_usable_ms: float | None
    map_ready_ms: float | None
    map_ready_after_shell_ms: float | None
    resource_count: int
    transfer_bytes: int
    decoded_bytes: int
    horizontal_overflow_px: int
    error: str | None = None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass


@contextlib.contextmanager
def serve(dist: Path):
    handler = functools.partial(QuietHandler, directory=str(dist))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


PROBE_JS = r"""
(() => {
  window.__fhPerf = {start: performance.now(), shell: null, map: null};
  const sample = () => {
    const p = window.__fhPerf;
    if (!p.shell && document.body && document.body.innerText.trim().length > 20) p.shell = performance.now();
    const map = document.querySelector('.leaflet-map-pane, .leaflet-container .leaflet-pane, #dowmap');
    if (!p.map && map) p.map = performance.now();
  };
  const observe = () => {
    if (!document.documentElement) return requestAnimationFrame(observe);
    new MutationObserver(sample).observe(document.documentElement, {subtree:true, childList:true});
    sample();
  };
  observe();
  document.addEventListener('DOMContentLoaded', sample, {once:true});
  setInterval(sample, 50);
})();
"""


def browser_sample(page, label: str, run: int) -> BrowserResult:
    page.wait_for_timeout(250)
    values = page.evaluate("""() => {
      const nav = performance.getEntriesByType('navigation')[0] || {};
      const paint = performance.getEntriesByType('paint').find(x => x.name === 'first-contentful-paint');
      const res = performance.getEntriesByType('resource');
      const p = window.__fhPerf || {};
      const overflow = Math.max(0, (document.documentElement.scrollWidth || 0) - (document.documentElement.clientWidth || 0));
      return {
        dcl: nav.domContentLoadedEventEnd || null,
        load: nav.loadEventEnd || null,
        fcp: paint ? paint.startTime : null,
        shell: p.shell || nav.domContentLoadedEventEnd || null,
        map: p.map || null,
        count: res.length,
        transfer: res.reduce((n,x) => n + (x.transferSize || 0), 0),
        decoded: res.reduce((n,x) => n + (x.decodedBodySize || 0), 0),
        overflow
      };
    }""")
    shell, map_ready = values["shell"], values["map"]
    return BrowserResult(label, "", run, values["dcl"], values["load"], values["fcp"], shell,
                         map_ready, max(0, map_ready-shell) if map_ready is not None and shell is not None else None,
                         values["count"], values["transfer"], values["decoded"], values["overflow"])


def run_browser(dist: Path, budget: dict[str, object], runs: int) -> list[BrowserResult]:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    pages = {"homepage": "/", "map": "/map/#explore", "planner": "/#planner", "account": "/account/"}
    mobile = budget["mobile_fast_4g"]
    scenarios = (
        ("desktop-cold", False, False),
        ("mobile-cold", True, False),
        ("mobile-warm", True, True),
    )
    results: list[BrowserResult] = []
    with serve(dist) as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        for scenario, is_mobile, warm in scenarios:
            for label, route in pages.items():
                context = browser.new_context(
                    viewport={"width": 390, "height": 844} if is_mobile else {"width": 1440, "height": 900},
                    device_scale_factor=2 if is_mobile else 1,
                    is_mobile=is_mobile,
                    has_touch=is_mobile,
                )
                context.add_init_script(PROBE_JS)
                context.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
                tab = context.new_page()
                cdp = context.new_cdp_session(tab)
                cdp.send("Network.enable")
                if is_mobile:
                    cdp.send("Network.emulateNetworkConditions", {
                        "offline": False,
                        "latency": mobile["latency_ms"],
                        "downloadThroughput": mobile["download_bps"] / 8,
                        "uploadThroughput": mobile["upload_bps"] / 8,
                        "connectionType": "cellular4g",
                    })
                    cdp.send("Emulation.setCPUThrottlingRate", {"rate": mobile["cpu_slowdown"]})
                if warm:
                    try:
                        tab.goto(base + route, wait_until="domcontentloaded", timeout=30000)
                        tab.wait_for_timeout(500)
                    except PlaywrightTimeoutError:
                        pass
                for index in range(1, runs + 1):
                    if not warm:
                        cdp.send("Network.clearBrowserCache")
                    try:
                        tab.goto(base + route, wait_until="domcontentloaded", timeout=30000)
                        if label != "account":
                            try:
                                tab.wait_for_function("window.__fhPerf && window.__fhPerf.map", timeout=8000)
                            except PlaywrightTimeoutError:
                                pass
                        result = browser_sample(tab, label, index)
                        result.scenario = scenario
                    except Exception as exc:
                        result = BrowserResult(label, scenario, index, None, None, None, None, None, None, 0, 0, 0, 0, str(exc))
                    results.append(result)
                context.close()
        browser.close()
    return results


def render_report(dist: Path, static: list[dict[str, object]], browser: list[BrowserResult], budget: dict[str, object]) -> str:
    target = budget["targets"]
    lines = [
        "# PERF-01 — performance baseline",
        "",
        f"- თარიღი: {dt.date.today().isoformat()}",
        f"- build: `{dist.name}`",
        "- გარემო: local HTTP + Microsoft Edge headless",
        "- mobile profile: Fast 4G (150 ms RTT, 1.64 Mbps download, 768 Kbps upload, CPU ×4)",
        "- გარე სერვისები (fonts, Firebase, map tiles, traffic/weather API) დაბლოკილია, რათა source bundle-ის baseline განმეორებადი იყოს.",
        "",
        "## სამიზნეები",
        "",
        f"- p75 shell usable: ≤ {target['shell_usable_ms_p75']} ms",
        f"- p75 map-ready shell-ის შემდეგ: ≤ {target['map_ready_after_shell_ms_p75']} ms",
        f"- horizontal overflow: {target['horizontal_overflow_px']} px",
        "",
        "## ბრაუზერის შედეგები",
        "",
        "| სცენარი | გვერდი | p75 shell | p75 FCP | p75 map დამატებით | მაქს. overflow | შედეგი |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for scenario in ("desktop-cold", "mobile-cold", "mobile-warm"):
        for page in ("homepage", "map", "planner", "account"):
            rows = [x for x in browser if x.scenario == scenario and x.page == page and not x.error]
            shell = p75([x.shell_usable_ms for x in rows]); fcp = p75([x.first_contentful_paint_ms for x in rows])
            map_delta = p75([x.map_ready_after_shell_ms for x in rows]); overflow = max([x.horizontal_overflow_px for x in rows], default=0)
            ok = shell is not None and shell <= target["shell_usable_ms_p75"] and overflow <= target["horizontal_overflow_px"]
            if page != "account": ok = ok and map_delta is not None and map_delta <= target["map_ready_after_shell_ms_p75"]
            fmt = lambda x: "—" if x is None else f"{x:.0f} ms"
            lines.append(f"| {scenario} | {page} | {fmt(shell)} | {fmt(fcp)} | {fmt(map_delta)} | {overflow}px | {'PASS' if ok else 'OVER'} |")
    lines += ["", "## საწყისი payload", "", "| გვერდი | HTML | CSS | JS | eager images | ჯამი | blocking JS |", "|---|---:|---:|---:|---:|---:|---:|"]
    initial_budget = budget["initial_page"]
    for row in static:
        lines.append(f"| `{row['page']}` | {human_bytes(row['html_bytes'])} | {human_bytes(row['local_css_bytes'])} | {human_bytes(row['local_js_bytes'])} | {human_bytes(row['local_image_bytes'])} | {human_bytes(row['local_initial_total_bytes'])} | {row['blocking_script_count']} |")
    lines += ["", "## ყველაზე მძიმე asset-ები და ბიუჯეტი", "", "| asset | ზომა | ბიუჯეტი | შედეგი |", "|---|---:|---:|---|"]
    limits = budget["individual_assets"]
    assets = sorted((x for x in dist.joinpath("assets").rglob("*") if x.is_file()), key=lambda x: x.stat().st_size, reverse=True)
    overages = []
    for asset in assets:
        limit = limits.get(asset.suffix.lower())
        if limit is not None and asset.stat().st_size > limit:
            overages.append(asset)
    for asset in overages[:25]:
        limit = limits[asset.suffix.lower()]
        lines.append(f"| `{asset.relative_to(dist).as_posix()}` | {human_bytes(asset.stat().st_size)} | {human_bytes(limit)} | OVER |")
    lines += [
        "",
        "## დასკვნა და შემდეგი ნაბიჯი",
        "",
        f"- საწყისი გვერდის ბიუჯეტი: HTML ≤ {human_bytes(initial_budget['html_bytes'])}, CSS ≤ {human_bytes(initial_budget['local_css_bytes'])}, JS ≤ {human_bytes(initial_budget['local_js_bytes'])}, სრული local payload ≤ {human_bytes(initial_budget['local_initial_total_bytes'])}.",
        f"- ინდივიდუალური asset-ის ბიუჯეტი დოკუმენტირებულია `performance-budget.json`-ში; ამ baseline-ში {len(overages)} asset აჭარბებს შესაბამის ზღვარს.",
        "- PERF-02-ში პირველ რიგში უნდა გაიყოს `travel-*.js` რეგიონულ/viewport chunk-ებად და რუკის payload ჩაიტვირთოს მოთხოვნის მიხედვით.",
        "- PERF-03-ში უნდა შემცირდეს დიდი PNG/WebP/JPG ფაილები, logo/background variants და დაემატოს ზომაზე მორგებული responsive media/cache.",
        "- გარე provider-ების ცალკე production RUM საჭიროა DATA-01-ში; ეს ანგარიში შეგნებულად ზომავს კონტროლირებად source baseline-ს.",
        "",
        "## ნედლი შედეგები",
        "",
        "ბრაუზერის თითოეული გაშვების მონაცემები ინახება იმავე სახელის `.json` ფაილში.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", default="dist-perf01-baseline")
    parser.add_argument("--report", default="reports/performance-baseline-2026-08-19.md")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--skip-browser", action="store_true")
    args = parser.parse_args()
    dist = (ROOT / args.dist).resolve()
    if not dist.joinpath("index.html").exists():
        raise SystemExit(f"Build not found: {dist}")
    budget = json.loads(ROOT.joinpath("performance-budget.json").read_text(encoding="utf-8"))
    static = [static_page_metrics(dist, x) for x in ("index.html", "map/index.html", "account/index.html")]
    browser = [] if args.skip_browser else run_browser(dist, budget, args.runs)
    report = (ROOT / args.report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(dist, static, browser, budget), encoding="utf-8")
    raw = report.with_suffix(".json")
    raw.write_text(json.dumps({"static": static, "browser": [asdict(x) for x in browser]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Performance report: {report.relative_to(ROOT)}")
    print(f"Raw measurements: {raw.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
