"""ცოცხალი კატალოგის (static/catalogue.js) რენდერის შემოწმება.

`catalogue.js` ერთადერთი ფაილია, რომელიც *ბრაუზერში* წყვეტს, კლიენტი
დაინახავს თუ არა მანქანას. მისი შეცდომა deploy-ის შემდეგ ჩნდება, ანუ
კლიენტზე — ამიტომ მისი ტესტი კარიბჭეშივე უნდა გადიოდეს, დანარჩენებთან
ერთად, და არა ხელით.

თვითონ ტესტები `tests/catalogue.test.js`-შია და node-ს სჭირდება (CI-ს
აქვს, `pages.yml` node 22-ს აყენებს). თუ node არ არის — ლოკალური
გაშვება Windows-ზე მის გარეშე — ტესტი გამოტოვდება და არ ჩავარდება:
გარემოს არქონა კოდის შეცდომა არ არის.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUITE = ROOT / "tests" / "catalogue.test.js"
SCRIPT = ROOT / "static" / "catalogue.js"


class CatalogueJsTest(unittest.TestCase):
    def test_the_script_is_where_the_suite_expects_it(self):
        # A renamed or moved file would make the suite below skip silently
        # rather than fail, which is the one outcome worse than failing.
        self.assertTrue(SCRIPT.is_file(), f"{SCRIPT} აღარ არსებობს")
        self.assertTrue(SUITE.is_file(), f"{SUITE} აღარ არსებობს")

    def test_the_live_catalogue_renders_what_it_should(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node არ არის — ტესტები CI-ში გაივლის")

        result = subprocess.run(
            [node, str(SUITE)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if result.returncode:
            self.fail(
                "catalogue.test.js ჩავარდა:\n"
                + (result.stdout or "")
                + (result.stderr or "")
            )


if __name__ == "__main__":
    unittest.main()
