from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_performance", ROOT / "scripts" / "audit_performance.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class PerformanceAuditTests(unittest.TestCase):
    def test_budget_defines_required_targets(self):
        budget = json.loads((ROOT / "performance-budget.json").read_text(encoding="utf-8"))
        targets = budget["targets"]
        self.assertEqual(targets["shell_usable_ms_p75"], 3000)
        self.assertEqual(targets["map_ready_after_shell_ms_p75"], 2000)
        self.assertEqual(targets["horizontal_overflow_px"], 0)

    def test_p75_uses_nearest_rank(self):
        self.assertEqual(MOD.p75([100, 200, 300, 400]), 300)
        self.assertEqual(MOD.p75([None, 10, 20]), 20)

    def test_static_metrics_count_only_eager_local_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            dist = Path(folder)
            (dist / "assets").mkdir()
            (dist / "assets" / "a.css").write_bytes(b"x" * 10)
            (dist / "assets" / "a.js").write_bytes(b"x" * 20)
            (dist / "assets" / "a.webp").write_bytes(b"x" * 30)
            html = '<link rel="stylesheet" href="/assets/a.css"><script defer src="/assets/a.js"></script><img src="/assets/a.webp"><img loading="lazy" src="/assets/a.webp">'
            (dist / "index.html").write_text(html, encoding="utf-8")
            result = MOD.static_page_metrics(dist, "index.html")
            self.assertEqual(result["local_css_bytes"], 10)
            self.assertEqual(result["local_js_bytes"], 20)
            self.assertEqual(result["local_image_bytes"], 30)
            self.assertEqual(result["blocking_script_count"], 0)


if __name__ == "__main__":
    unittest.main()
