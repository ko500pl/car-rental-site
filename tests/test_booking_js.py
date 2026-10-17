"""ჯავშნის ფორმის (static/booking.js) გაგზავნის შემოწმება.

`booking.js` კლიენტის ფულს ითვლის და ჯავშანში წერს. მისი შეცდომა deploy-ის
შემდეგ ჩნდება, ანუ კლიენტის ჯავშანში — ამიტომ მისი ტესტი კარიბჭეშივე უნდა
გადიოდეს, დანარჩენებთან ერთად, და არა ხელით.

თვითონ ტესტები `tests/booking.test.js`-შია და node-ს სჭირდება (CI-ს აქვს,
`pages.yml` node 22-ს აყენებს). თუ node არ არის — ლოკალური გაშვება Windows-ზე
მის გარეშე — ტესტი გამოტოვდება და არ ჩავარდება: გარემოს არქონა კოდის
შეცდომა არ არის.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUITE = ROOT / "tests" / "booking.test.js"
SCRIPT = ROOT / "static" / "booking.js"


class BookingJsTest(unittest.TestCase):
    def test_the_script_is_where_the_suite_expects_it(self):
        # A renamed or moved file would make the suite below skip silently
        # rather than fail, which is the one outcome worse than failing.
        self.assertTrue(SCRIPT.is_file(), f"{SCRIPT} აღარ არსებობს")
        self.assertTrue(SUITE.is_file(), f"{SUITE} აღარ არსებობს")

    def test_the_booking_form_quotes_and_sends_what_it_should(self):
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
                "booking.test.js ჩავარდა:\n"
                + (result.stdout or "")
                + (result.stderr or "")
            )


if __name__ == "__main__":
    unittest.main()
