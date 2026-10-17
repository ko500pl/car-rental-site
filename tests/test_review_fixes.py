"""Regression tests for the final whole-branch review of release M."""
import re
import unittest
from pathlib import Path

import yaml

from sitegen.validation import validate_branches

ROOT = Path(__file__).resolve().parents[1]


def good_branch():
    langs = ("ka", "en", "ru", "fa", "he", "ar")
    return {"id": "x", "name": {l: "RentUp" for l in langs},
            "address": {l: {"street": "s", "city": "c"} for l in langs},
            "zip": "0186", "lat": 41.7, "lon": 44.7, "opens": "09:00", "closes": "21:00",
            "phone_e164": "+995597555565", "maps": {}}


class WhatsAppOpensAreCountedTests(unittest.TestCase):
    def test_every_programmatic_wa_open_tracks_whatsapp_click(self):
        found = 0
        for js in sorted((ROOT / "static").glob("*.js")):
            src = js.read_text(encoding="utf-8")
            for m in re.finditer(r"window\.open\(\s*['\"]https://wa\.me/", src):
                found += 1
                before = src[max(0, m.start() - 400):m.start()]
                self.assertRegex(before, r"track\(\s*['\"]whatsapp_click['\"]",
                                 f"{js.name}:{src.count(chr(10), 0, m.start()) + 1} opens WhatsApp untracked")
        self.assertGreaterEqual(found, 4)


class BranchValidationTests(unittest.TestCase):
    def test_real_branches_file_is_valid_and_typed_as_strings(self):
        branches = yaml.safe_load((ROOT / "content/settings/branches.yml").read_text(encoding="utf-8"))
        self.assertEqual(validate_branches(branches), [])
        for b in branches:
            for k in ("zip", "opens", "closes"):
                self.assertIsInstance(b[k], str, k)

    def test_yaml_sexagesimal_hours_are_rejected(self):
        b = good_branch()
        b["opens"] = 600  # what PyYAML makes of an unquoted 10:00
        self.assertTrue(any("opens" in e for e in validate_branches([b])))

    def test_octal_like_zip_is_rejected(self):
        b = good_branch()
        b["zip"] = 120  # what PyYAML makes of an unquoted 0170
        self.assertTrue(any("zip" in e for e in validate_branches([b])))

    def test_missing_language_is_rejected(self):
        b = good_branch()
        del b["address"]["he"]
        self.assertTrue(any("he" in e for e in validate_branches([b])))

    def test_good_branch_passes(self):
        self.assertEqual(validate_branches([good_branch()]), [])


if __name__ == "__main__":
    unittest.main()
