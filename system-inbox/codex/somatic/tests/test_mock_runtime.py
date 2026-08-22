import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]


class MockRuntimeTests(unittest.TestCase):
    def test_runs_literature_fixture_and_writes_mock_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                REPO_ROOT / "fixtures" / "workflows" / "valid-literature-only.yaml",
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-mock-test",
            )

            hypotheses = json.loads((run_dir / "artifacts" / "hypotheses.json").read_text())
            evidence = json.loads((run_dir / "evidence" / "evidence.json").read_text())
            safety = json.loads((run_dir / "safety" / "safety-response.json").read_text())
            report = (run_dir / "reports" / "report.md").read_text()

            self.assertEqual(len(hypotheses), 3)
            self.assertEqual(evidence["id"], "ev-phase1a-sample-001")
            self.assertEqual(safety["id"], "safety-response-phase1a-001")
            self.assertIn("mock/offline", report)
            self.assertIn("research-only", report)
            self.assertIn("not medical advice", report.lower())


if __name__ == "__main__":
    unittest.main()
