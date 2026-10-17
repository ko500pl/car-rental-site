import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("export_fleet", ROOT / "scripts/export_fleet.py")
ef = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ef)

PRICES = ("price_1_6_gel", "price_7_29_gel", "price_30_gel")


def public_car_count():
    n = 0
    for f in (ROOT / "content/cars").glob("*.yml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if d.get("status") in (None, "published") and not d.get("draft", False):
            n += 1
    return n


class ExportFleetTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.warnings = ef.fleet_rows()

    def test_all_public_cars_exported(self):
        self.assertEqual(len(self.rows), public_car_count())
        self.assertEqual(len(self.rows), 17)

    def test_prices_are_ints(self):
        for r in self.rows:
            for k in PRICES + ("deposit_gel", "excess_gel", "min_age"):
                self.assertIsInstance(r[k], int, f"{r['slug']} {k}")

    def test_blank_price_is_warned_not_fatal(self):
        car = {"category": "economy", "price_1_6": "100", "price_7_29": "", "price_30": "80",
               "deposit": "300", "en": {"name": "Test Car"}}
        rows, warnings = ef.fleet_rows(cars={"test-car": car})
        self.assertIsNone(rows[0]["price_7_29_gel"])
        self.assertTrue(any("test-car" in w for w in warnings))

    def test_tier_order(self):
        for r in self.rows:
            self.assertGreaterEqual(r["price_1_6_gel"], r["price_7_29_gel"], r["slug"])
            self.assertGreaterEqual(r["price_7_29_gel"], r["price_30_gel"], r["slug"])

    def test_policy_by_category(self):
        by_slug = {r["slug"]: r for r in self.rows}
        self.assertEqual(by_slug["toyota-prius"]["excess_gel"], 300)
        self.assertEqual(by_slug["toyota-prius"]["min_age"], 21)
        self.assertEqual(by_slug["bmw-5-series"]["min_age"], 25)
        self.assertEqual(by_slug["toyota-land-cruiser-prado"]["excess_gel"], 1200)
        self.assertEqual(by_slug["ford-transit"]["excess_gel"], 800)
        self.assertEqual({r["mileage"] for r in self.rows}, {"unlimited"})

    def test_unknown_platform_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                ef.write_csv("foo", Path(tmp))

    def test_csv_has_bom_and_all_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = ef.write_csv("localrent", Path(tmp))
            self.assertEqual(p.name, "fleet-localrent.csv")
            raw = p.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
            with p.open(encoding="utf-8-sig", newline="") as fh:
                data = list(csv.DictReader(fh))
            self.assertEqual(len(data), 17)
            self.assertEqual(list(data[0].keys()), [ef.COLUMNS["localrent"][k] for k in ef.KEYS])


if __name__ == "__main__":
    unittest.main()
