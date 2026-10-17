"""Generated marketing pack: listing copy limits, UTM vocabulary, sourced prices."""

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import make_marketing_pack as mp  # noqa: E402

LANGS = ("ka", "en", "ru", "fa", "he", "ar")


class MarketingPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.files = {p.name: p.read_text(encoding="utf-8") for p in mp.main(out_dir=cls.tmp.name)}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_four_files(self):
        self.assertEqual(sorted(self.files), ["LISTINGS_PACK.md", "OWNER_STEPS.md",
                                              "REVIEW_REQUEST_TEMPLATES.md", "UTM_CONVENTIONS.md"])

    def test_descriptions_within_limit(self):
        listings = yaml.safe_load((ROOT / "content/settings/listings.yml").read_text(encoding="utf-8"))
        for lang in LANGS:
            text = listings["description"][lang].strip()
            self.assertTrue(text, lang)
            self.assertLessEqual(len(text), 750, lang)

    def test_name_is_exactly_brand(self):
        pack = self.files["LISTINGS_PACK.md"]
        self.assertIn("**Name:** RentUp\n", pack)
        self.assertNotIn("RentUp —", pack)
        self.assertNotIn("RentUp Car Rental", pack)

    def test_utm_url(self):
        self.assertEqual(mp.utm_url("/en/car-rental/", "gbp", "maps", "tbilisi"),
                         "https://rentup.ge/en/car-rental/?utm_source=gbp&utm_medium=maps&utm_campaign=tbilisi")
        self.assertEqual(mp.utm_url("/", "partner-hotel-rooms", "referral"),
                         "https://rentup.ge/?utm_source=partner-hotel-rooms&utm_medium=referral")
        self.assertEqual(mp.utm_url("/he/", "ads-he", "cpc"),
                         "https://rentup.ge/he/?utm_source=ads-he&utm_medium=cpc")
        with self.assertRaises(ValueError):
            mp.utm_url("/", "facebook", "maps")
        with self.assertRaises(ValueError):
            mp.utm_url("/", "gbp", "social")
        with self.assertRaises(ValueError):
            mp.utm_url("/", "ads-xx", "cpc")

    def test_prices_come_from_policy(self):
        policy = yaml.safe_load((ROOT / "content/settings/rental_policy.yml").read_text(encoding="utf-8"))
        fee = policy["delivery"]["airport_fee_gel"]["tbilisi-airport"]
        self.assertIn(f"Tbilisi airport delivery: {fee} GEL", self.files["LISTINGS_PACK.md"])
        self.assertIn(f"One-way between Tbilisi, Kutaisi and Batumi: {policy['one_way']['fee_gel']} GEL",
                      self.files["LISTINGS_PACK.md"])

    def test_no_incentive_words(self):
        text = self.files["REVIEW_REQUEST_TEMPLATES.md"].lower()
        for word in ("discount", "скидк", "ფასდაკლ", "הנחה", "خصم", "تخفیف", "bonus", "бонус"):
            self.assertNotIn(word, text)

    def test_review_templates_cover_all_languages(self):
        text = self.files["REVIEW_REQUEST_TEMPLATES.md"]
        for lang in LANGS:
            self.assertIn(f"## {lang}", text)


if __name__ == "__main__":
    unittest.main()
