import unittest
from pathlib import Path

from somatic.analysis.dose_response import summarize_dose_response
from somatic.analysis.provenance import build_analysis_provenance
from somatic.analysis.tables import read_csv_table

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "fixtures" / "evidence" / "tables"


class FinchToolbeltDoseResponseTests(unittest.TestCase):
    def test_dose_response_summary_is_deterministic(self):
        rows = read_csv_table(FIXTURE_DIR / "dose-response.csv")

        first = summarize_dose_response(rows, dose_column="dose", response_column="response")
        second = summarize_dose_response(rows, dose_column="dose", response_column="response")

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], 1)
        self.assertEqual([point["dose"] for point in first["points"]], [0.0, 1.0, 3.0, 10.0])
        self.assertEqual([point["response"] for point in first["points"]], [10.0, 12.5, 18.0, 25.0])
        self.assertEqual(first["trend_direction"], "increasing")
        self.assertEqual(first["baseline_vs_highest_delta"], 15.0)
        self.assertEqual(first["effect_direction"], "increase")
        self.assertEqual(first["evidence_quality_score"], 0.67)
        self.assertTrue(first["preliminary_sandbox_analysis"])
        self.assertIn("preliminary sandbox", first["interpretation"])

    def test_dose_response_handles_missing_columns_without_crashing(self):
        rows = read_csv_table(FIXTURE_DIR / "non-numeric-table.csv")

        summary = summarize_dose_response(rows, dose_column="dose", response_column="response")

        self.assertEqual(summary["points"], [])
        self.assertEqual(summary["trend_direction"], "unavailable")
        self.assertEqual(summary["effect_direction"], "unavailable")
        self.assertEqual(summary["evidence_quality_score"], 0.0)
        self.assertTrue(summary["preliminary_sandbox_analysis"])

    def test_analysis_provenance_includes_stable_hashes(self):
        path = FIXTURE_DIR / "dose-response.csv"
        summary = summarize_dose_response(
            read_csv_table(path),
            dose_column="dose",
            response_column="response",
        )

        first = build_analysis_provenance(
            source_files=[path],
            artifacts={"dose_response_summary": summary},
        )
        second = build_analysis_provenance(
            source_files=[path],
            artifacts={"dose_response_summary": summary},
        )

        self.assertEqual(first, second)
        self.assertEqual(first["source_files"][0]["name"], "dose-response.csv")
        self.assertEqual(
            first["artifacts"]["dose_response_summary"]["hash"],
            second["artifacts"]["dose_response_summary"]["hash"],
        )
        self.assertEqual(first["network_calls"], False)
        self.assertEqual(first["dependencies"], ["python-standard-library"])


if __name__ == "__main__":
    unittest.main()
