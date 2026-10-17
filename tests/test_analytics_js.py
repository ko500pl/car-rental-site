"""Umami events in static/analytics.js, run through node (skipped without node)."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUITE = ROOT / "tests" / "analytics.test.js"
SCRIPT = ROOT / "static" / "analytics.js"


class AnalyticsJsTest(unittest.TestCase):
    def test_the_script_is_where_the_suite_expects_it(self):
        # A renamed or moved file would make the suite below skip silently
        # rather than fail, which is the one outcome worse than failing.
        self.assertTrue(SCRIPT.is_file(), f"{SCRIPT} აღარ არსებობს")
        self.assertTrue(SUITE.is_file(), f"{SUITE} აღარ არსებობს")

    def test_umami_events_behave(self):
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
                "analytics.test.js ჩავარდა:\n"
                + (result.stdout or "")
                + (result.stderr or "")
            )


if __name__ == "__main__":
    unittest.main()
