import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_ai_catalog as bac  # noqa: E402


class AiCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = bac.build()
        cls.text = bac.dumps(cls.cat)

    def test_every_place_is_plannable(self):
        """The Worker fits days from dm (drive minutes) and vh (visit hours);
        a place missing either would silently never be proposed."""
        bad = [p["s"] for p in self.cat["places"]
               if not p["la"] or not p["lo"] or p["dm"] is None or p["vh"] in (None, 0)]
        self.assertEqual(bad, [], f"places the assistant could never plan: {bad[:10]}")

    def test_every_place_has_all_six_names(self):
        bad = [p["s"] for p in self.cat["places"] if any(not p["n"][l] for l in bac.LANGS)]
        self.assertEqual(bad, [], f"places with a missing name: {bad[:10]}")

    def test_fleet_is_priced(self):
        self.assertEqual(len(self.cat["cars"]), 17)
        bad = [c["s"] for c in self.cat["cars"] if not c["p"][0] or not c["cat"]]
        self.assertEqual(bad, [], f"cars without a 1–6 day price or category: {bad}")

    def test_route_waypoints_exist(self):
        slugs = {p["s"] for p in self.cat["places"]}
        bad = [(r["s"], w) for r in self.cat["routes"] for w in r["wp"] if w not in slugs]
        self.assertEqual(bad, [], f"route waypoints that are not places: {bad[:10]}")

    def test_policy_facts_present(self):
        for k in ("min_driver_age", "fuel_policy", "deposit", "cancellation", "delivery"):
            self.assertIn(k, self.cat["policy"])

    def test_each_language_file_stays_small(self):
        """Loaded by the Worker on a cold start and cached; keep it light."""
        for lang in bac.LANGS:
            text = bac.dumps(bac.for_lang(self.cat, lang))
            self.assertLess(len(text.encode("utf-8")), 300 * 1024, lang)
            data = json.loads(text)
            self.assertEqual(data["lang"], lang)
            self.assertIsInstance(data["places"][0]["n"], str, "names must be collapsed to one language")
            self.assertIsInstance(data["labels"]["regions"]["kakheti"], str)

    def test_numbers_are_numbers(self):
        p = self.cat["places"][0]; c = self.cat["cars"][0]
        self.assertIsInstance(p["vh"], (int, float)); self.assertIsInstance(p["dm"], int)
        self.assertIsInstance(c["p"][0], (int, float)); self.assertIsInstance(c["seats"], int)


if __name__ == "__main__":
    unittest.main()
