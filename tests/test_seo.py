"""Programmatic SEO checks against the built dist/ tree.

Mirrors docs/seo/SEO_VALIDATION.md's automated assertions by calling into
scripts/seo_audit.py directly (no subprocess). Skips cleanly if dist/ has
not been built. To keep this fast, the expensive per-page checks run
against a bounded sample of pages — sitemap coverage and the noindex /
indexable guard lists always run against the *whole* site regardless,
since scripts/seo_audit.audit() never lets `sample` narrow those two.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"

sys.path.insert(0, str(ROOT / "scripts"))
import seo_audit  # noqa: E402  (import after sys.path setup)


SAMPLE_SIZE = 60

# Checks verified clean against the full ~2000-page corpus in the
# 2026-08-29 baseline (docs/seo/SEO_AUDIT.md) — any ERROR surfacing here is
# a genuine regression. Deliberately excluded from this list are the site's
# real, tracked issues: meta-keywords and legacy-brand (present on nearly
# every page) and sitemap-coverage (/map/, /tours/, /business-card/ are
# missing from the sitemap). Those are exercised in
# test_known_debt_checks_still_run below without asserting they are clean.
ZERO_ERROR_CHECKS = (
    seo_audit.CHECK_CANONICAL,
    seo_audit.CHECK_TITLE,
    seo_audit.CHECK_DESCRIPTION,
    seo_audit.CHECK_HREFLANG,
    seo_audit.CHECK_SITEMAP_VALID,
    seo_audit.CHECK_GUARD_INDEXABLE,
    seo_audit.CHECK_GUARD_NOINDEX,
    seo_audit.CHECK_LDJSON,
    seo_audit.CHECK_BREADCRUMBS,
    seo_audit.CHECK_INTERNAL_LINKS,
    seo_audit.CHECK_ROBOTS_TXT,
    seo_audit.CHECK_IMG_ALT,
)

_DIST_BUILT = DIST_DIR.is_dir() and any(DIST_DIR.glob("*.html"))


@unittest.skipUnless(
    _DIST_BUILT,
    f"dist/ not found at {DIST_DIR} — run `python build.py dist` first, then re-run this test",
)
class SeoAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # sample=SAMPLE_SIZE bounds the expensive per-page checks; sitemap
        # coverage + guard lists ignore `sample` by design (see seo_audit.audit).
        cls.report = seo_audit.audit(DIST_DIR, sample=SAMPLE_SIZE)

    def _errors(self, check):
        return [f for f in self.report.findings if f.check == check and f.severity == seo_audit.ERROR]

    def test_curated_checks_report_zero_errors(self):
        for check in ZERO_ERROR_CHECKS:
            with self.subTest(check=check):
                errors = self._errors(check)
                sample_msgs = [f"{e.page}: {e.message}" for e in errors[:3]]
                self.assertEqual(
                    errors, [],
                    f"{check}: {len(errors)} unexpected ERROR(s) — e.g. {sample_msgs}",
                )

    def test_known_debt_checks_still_run(self):
        """These are real, open issues (see SEO_VALIDATION.md) — not
        asserted clean, just confirmed the check itself still executes."""
        for check in (seo_audit.CHECK_KEYWORDS, seo_audit.CHECK_BRAND, seo_audit.CHECK_SITEMAP_COVERAGE):
            with self.subTest(check=check):
                self.assertIsInstance(self.report.by_check(check), list)

    def test_sitemap_and_guard_lists_ignore_the_sample_size(self):
        """Sitemap coverage and the guard lists must always reflect the
        whole site, never just the sampled subset — verify by comparing
        two audits with very different sample sizes."""
        tiny = seo_audit.audit(DIST_DIR, sample=1)
        full_sample = seo_audit.audit(DIST_DIR, sample=SAMPLE_SIZE)
        always_full_checks = (
            seo_audit.CHECK_SITEMAP_VALID,
            seo_audit.CHECK_SITEMAP_COVERAGE,
            seo_audit.CHECK_GUARD_INDEXABLE,
            seo_audit.CHECK_GUARD_NOINDEX,
        )
        for check in always_full_checks:
            with self.subTest(check=check):
                self.assertEqual(
                    len(tiny.by_check(check)), len(full_sample.by_check(check)),
                    f"{check} finding count changed with sample size — it must scan the whole site",
                )

    def test_robots_txt_is_present_and_sane(self):
        robots = DIST_DIR / "robots.txt"
        self.assertTrue(robots.is_file(), "dist/robots.txt is missing")
        text = robots.read_text(encoding="utf-8")
        self.assertIn("Allow: /", text)
        self.assertIn("Disallow: /admin/", text)
        self.assertIn("Sitemap:", text)

    def test_full_sitemap_file_is_present_and_nonempty(self):
        sitemap = DIST_DIR / "sitemap.xml"
        self.assertTrue(sitemap.is_file(), "dist/sitemap.xml is missing")
        self.assertGreater(sitemap.stat().st_size, 0)

    def test_audit_exits_nonzero_when_errors_exist(self):
        # Sanity-check the Report/CLI contract: has_errors reflects the
        # presence of ERROR-severity findings (there are real, tracked ones
        # today — see test_known_debt_checks_still_run).
        self.assertEqual(self.report.has_errors, any(f.severity == seo_audit.ERROR for f in self.report.findings))


if __name__ == "__main__":
    unittest.main()
