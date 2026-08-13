import unittest

import build
from sitegen.validation import is_public, validate


class CurrencyTests(unittest.TestCase):
    def test_requested_rounding_examples(self):
        self.assertEqual(build.gel_to_usd(75), 30)
        self.assertEqual(build.gel_to_usd(145), 60)
        self.assertEqual(build.gel_to_usd(330), 130)


class PublishingTests(unittest.TestCase):
    def test_status_visibility(self):
        self.assertTrue(is_public({}))  # legacy records stay published
        self.assertTrue(is_public({"status": "published"}))
        self.assertFalse(is_public({"status": "draft"}))
        self.assertFalse(is_public({"status": "archived"}))

    def test_broken_route_reference_is_blocked(self):
        localized = {lang: {} for lang in ("ka", "en", "ru", "fa", "he", "ar")}
        report = validate(
            {"usd_rate": 2.6, "usd_rounding": 10}, {}, {}, {},
            {"route": {**localized, "waypoints": ["missing"]}}, {}, {})
        self.assertTrue(any("waypoint" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
