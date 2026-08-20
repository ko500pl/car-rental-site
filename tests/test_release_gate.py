from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseGateTests(unittest.TestCase):
    def test_workflow_verifies_pull_requests_and_main(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("run_quality_gate.py --output dist", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)

    def test_deploy_is_manual_and_conditioned(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("inputs.deploy", workflow)
        self.assertIn("github.event_name == 'workflow_dispatch'", workflow)

    def test_gate_contains_all_required_stages(self):
        gate = (ROOT / "scripts/run_quality_gate.py").read_text(encoding="utf-8")
        for required in (
            "check_environment.py", "check_project_layout.py", "--validate-only",
            "unittest", "check_javascript_syntax.py", "check_internal_links.py",
            "quality-gate-summary.md",
        ):
            self.assertIn(required, gate)


if __name__ == "__main__":
    unittest.main()
