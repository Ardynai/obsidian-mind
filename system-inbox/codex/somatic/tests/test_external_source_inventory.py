import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "fixtures" / "providers" / "external-source-inventory.json"


class ExternalSourceInventoryTests(unittest.TestCase):
    def test_inventory_parses_and_has_expected_shape(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["phase"], "5A.1")
        self.assertIn("staging_root", inventory)
        self.assertIsInstance(inventory["entries"], list)
        self.assertGreaterEqual(len(inventory["entries"]), 7)

    def test_entries_include_status_repo_path_or_failure_and_commit_when_available(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

        for entry in inventory["entries"]:
            with self.subTest(repo=entry.get("repo")):
                self.assertIn("repo", entry)
                self.assertIn("status", entry)
                self.assertIn(entry["status"], {"staged", "failed", "ambiguous", "skipped"})

                if entry["status"] == "staged":
                    self.assertTrue(entry.get("local_path"))
                    self.assertTrue(entry.get("remote_url"))
                    self.assertRegex(entry.get("inspected_commit", ""), r"^[0-9a-f]{40}$")
                    self.assertIsNone(entry.get("failure_reason"))
                    self.assertIn("license", entry)
                    self.assertIn("identifier", entry["license"])
                    self.assertGreaterEqual(len(entry.get("likely_entrypoints", [])), 1)
                else:
                    self.assertTrue(entry.get("failure_reason"))

    def test_inventory_does_not_require_external_repos_for_ci(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

        # CI should validate the recorded inventory only. It must not read from
        # C:\AI\external-sources or import any staged external package.
        for entry in inventory["entries"]:
            with self.subTest(repo=entry["repo"]):
                self.assertIsInstance(entry.get("local_path"), (str, type(None)))
                self.assertNotIn("import_check", entry)
                self.assertNotIn("external_package_imported", entry)

    def test_staging_policy_records_no_runtime_actions(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        policy = inventory["policy"]

        self.assertTrue(policy["clone_or_source_stage_only"])
        self.assertFalse(policy["dependencies_installed"])
        self.assertFalse(policy["package_managers_run"])
        self.assertFalse(policy["setup_scripts_run"])
        self.assertFalse(policy["model_weights_or_datasets_downloaded"])
        self.assertFalse(policy["external_apis_called"])
        self.assertFalse(policy["external_repos_modified"])
        self.assertFalse(policy["vendored_into_somatic"])


if __name__ == "__main__":
    unittest.main()
