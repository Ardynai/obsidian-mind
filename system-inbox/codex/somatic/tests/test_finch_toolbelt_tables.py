import ast
import unittest
from pathlib import Path

from somatic.analysis.provenance import hash_file, hash_payload
from somatic.analysis.statistics import group_by_summary
from somatic.analysis.tables import profile_csv_table, read_csv_table

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "fixtures" / "evidence" / "tables"


class FinchToolbeltTableTests(unittest.TestCase):
    def test_csv_fixture_parses_and_profiles_numeric_columns(self):
        rows = read_csv_table(FIXTURE_DIR / "simple-lab-results.csv")
        profile = profile_csv_table(FIXTURE_DIR / "simple-lab-results.csv")

        self.assertEqual(len(rows), 4)
        self.assertEqual(
            profile["columns"],
            ["sample_id", "group", "replicate", "signal", "quality_score"],
        )
        self.assertEqual(profile["row_count"], 4)
        self.assertEqual(profile["missing_values"]["signal"], 0)
        self.assertEqual(profile["numeric_columns"], ["replicate", "signal", "quality_score"])
        self.assertEqual(profile["numeric_stats"]["signal"]["count"], 4)
        self.assertEqual(profile["numeric_stats"]["signal"]["min"], 0.1)
        self.assertEqual(profile["numeric_stats"]["signal"]["max"], 0.35)
        self.assertEqual(profile["numeric_stats"]["signal"]["mean"], 0.2175)
        self.assertEqual(profile["numeric_stats"]["signal"]["median"], 0.21)
        self.assertAlmostEqual(profile["numeric_stats"]["signal"]["stdev"], 0.126062, places=6)

    def test_missing_values_and_non_numeric_tables_are_handled(self):
        missing = profile_csv_table(FIXTURE_DIR / "missing-values.csv")
        non_numeric = profile_csv_table(FIXTURE_DIR / "non-numeric-table.csv")

        self.assertEqual(missing["missing_values"]["group"], 1)
        self.assertEqual(missing["missing_values"]["signal"], 1)
        self.assertEqual(missing["missing_values"]["response"], 1)
        self.assertEqual(missing["missing_values"]["notes"], 1)
        self.assertEqual(missing["numeric_columns"], ["signal", "response"])
        self.assertEqual(non_numeric["numeric_columns"], [])
        self.assertEqual(non_numeric["numeric_stats"], {})

    def test_group_by_summary_is_deterministic(self):
        rows = read_csv_table(FIXTURE_DIR / "simple-lab-results.csv")

        grouped = group_by_summary(rows, group_column="group", value_column="signal")

        self.assertEqual(grouped["group_column"], "group")
        self.assertEqual(grouped["value_column"], "signal")
        self.assertEqual(list(grouped["groups"]), ["control", "treatment"])
        self.assertEqual(grouped["groups"]["control"]["row_count"], 2)
        self.assertEqual(grouped["groups"]["control"]["numeric_stats"]["mean"], 0.11)
        self.assertEqual(grouped["groups"]["treatment"]["numeric_stats"]["mean"], 0.325)

    def test_provenance_hashes_are_deterministic(self):
        path = FIXTURE_DIR / "simple-lab-results.csv"
        payload = {"fixture": path.name, "rows": 4}

        self.assertEqual(hash_file(path), hash_file(path))
        self.assertEqual(hash_payload(payload), hash_payload({"rows": 4, "fixture": path.name}))

    def test_analysis_toolbelt_has_no_network_imports(self):
        forbidden_import_roots = {"requests", "urllib", "http", "socket", "openai"}
        for path in (
            REPO_ROOT / "somatic" / "analysis" / "tables.py",
            REPO_ROOT / "somatic" / "analysis" / "statistics.py",
            REPO_ROOT / "somatic" / "analysis" / "dose_response.py",
            REPO_ROOT / "somatic" / "analysis" / "provenance.py",
            REPO_ROOT / "somatic" / "agents" / "finch_toolbelt.py",
        ):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        self.assertNotIn(node.module.split(".")[0], forbidden_import_roots)


if __name__ == "__main__":
    unittest.main()
