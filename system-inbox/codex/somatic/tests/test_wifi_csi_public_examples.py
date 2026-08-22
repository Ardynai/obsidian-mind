import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples" / "wifi-csi-demo"

FORBIDDEN_PUBLIC_CSI_KEYS = {
    "fixture_refs",
    "source_id",
    "source_ids",
    "samples",
    "raw_values",
    "real",
    "imag",
    "amplitude",
    "phase",
    "rssi",
    "mac",
    "bssid",
    "ssid",
    "device_id",
    "adapter_id",
    "router_id",
    "ip_address",
    "local_path",
    "source_path",
    "staging_root",
    "api_key",
    "access_token",
    "refresh_token",
    "secret",
    "secret_value",
    "password",
    "authorization",
    "bearer",
}

FORBIDDEN_PUBLIC_CSI_WORDS = (
    "fixture_refs",
    "source_id",
    "source_ids",
    "raw_values",
    "sample-esp32-csi",
    "sample-amplitude-phase",
    "sample-csi-jsonl",
    "mixed-valid-invalid-csi",
    "unsupported-csi",
    "invalid-utf8-csi",
    "example.invalid",
)


class WifiCsiPublicExamplesTests(unittest.TestCase):
    def test_public_example_manifests_load_and_reference_existing_paths(self):
        parser = self._read_example("csi-parser-cli-example.json")
        n_of_1 = self._read_example("n-of-1-csi-replay-example.json")
        tournament = self._read_example("tournament-csi-readiness-example.json")

        self.assertEqual(parser["schema_version"], 1)
        self.assertEqual(parser["cli_args"][0], "csi-parse")
        parser_fixture = REPO_ROOT / "fixtures" / "sensors" / "csi" / parser["cli_args"][1]
        self.assertTrue(parser_fixture.exists())
        for manifest in (n_of_1, tournament):
            with self.subTest(example=manifest["example_id"]):
                workflow_path = REPO_ROOT / manifest["workflow_path"]
                self.assertTrue(workflow_path.exists())
                self.assertEqual(manifest["cli_args"][0], "run")
                self.assertEqual(
                    manifest["primary_portable_artifact"], "artifacts/csi_evidence_pack.json"
                )
                self.assertIn(
                    "artifacts/csi_evidence_pack.json",
                    manifest["public_artifacts_to_inspect"],
                )

    def test_parser_cli_public_example_runs_with_sanitized_metadata(self):
        manifest = self._read_example("csi-parser-cli-example.json")
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(manifest["cli_args"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, manifest["expected_exit_code"])
        self.assertEqual(
            payload["contract_version"], manifest["expected_output"]["contract_version"]
        )
        self.assertEqual(payload["report"]["status"], manifest["expected_output"]["status"])
        self.assertFalse(manifest["expected_output"]["portable_public_export"])
        self.assertTrue(manifest["expected_output"]["local_parser_contract_report"])
        self.assertTrue(payload["summary"]["fixture_only"])
        self.assertFalse(payload["summary"]["hardware_access"])
        self.assertFalse(payload["summary"]["network_calls"])
        self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), stdout.getvalue().replace("\\", "/"))
        self._assert_no_raw_signal_keys(payload)

    def test_n_of_1_public_example_emits_private_sanitized_evidence_pack(self):
        manifest = self._read_example("n-of-1-csi-replay-example.json")

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_manifest(manifest, Path(tmp))
            evidence_pack = self._read_json(run_dir / manifest["primary_portable_artifact"])
            public_artifacts = [
                self._read_json(run_dir / relative_path)
                for relative_path in manifest["public_artifacts_to_inspect"]
            ]

        self.assertEqual(evidence_pack["status"], "parsed")
        self.assertEqual(evidence_pack["readiness_status"], "ready-with-sanitized-metadata")
        self.assertEqual(evidence_pack["counts"]["fixture_count"], 3)
        self.assertEqual(len(evidence_pack["pack_fingerprint"]), 64)
        self.assertTrue(evidence_pack["metadata_only"])
        for payload in public_artifacts:
            self._assert_public_artifact_sanitized(payload)

    def test_tournament_public_example_emits_readiness_only_evidence_pack(self):
        manifest = self._read_example("tournament-csi-readiness-example.json")

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_manifest(manifest, Path(tmp))
            evidence_pack = self._read_json(run_dir / manifest["primary_portable_artifact"])
            team_summary = self._read_json(run_dir / "artifacts" / "team_orchestrator_summary.json")
            public_artifacts = [
                self._read_json(run_dir / relative_path)
                for relative_path in manifest["public_artifacts_to_inspect"]
            ]
            ranked = self._read_json(run_dir / "artifacts" / "ranked_hypotheses.json")

        self.assertEqual(evidence_pack["status"], "partial")
        self.assertFalse(evidence_pack["ranking_input"])
        self.assertFalse(evidence_pack["core_tournament_scores_modified"])
        self.assertFalse(evidence_pack["tournament_rankings_modified"])
        self.assertEqual(
            {item["rank"] for item in ranked},
            set(range(1, len(ranked) + 1)),
        )
        readiness = team_summary["csi_evidence_scoring_readiness"]
        compact_pack_ref = team_summary["csi_evidence_pack"]
        self.assertEqual(readiness["status"], "partial")
        self.assertEqual(compact_pack_ref["artifact_ref"], "artifacts/csi_evidence_pack.json")
        self.assertEqual(compact_pack_ref["pack_fingerprint"], evidence_pack["pack_fingerprint"])
        self._assert_public_artifact_sanitized(readiness)
        self._assert_public_artifact_sanitized(compact_pack_ref)
        for payload in public_artifacts:
            self._assert_public_artifact_sanitized(payload)

    def test_public_guide_and_demo_readme_include_quick_verification(self):
        guide = (REPO_ROOT / "docs" / "wifi-csi-public-examples.md").read_text(encoding="utf-8")
        demo = (EXAMPLES_DIR / "README.md").read_text(encoding="utf-8")

        for text in (guide, demo):
            with self.subTest(document=text[:32]):
                self.assertIn(
                    "python -m somatic csi-parse sample-esp32-csi.csv --repo-root .", text
                )
                self.assertIn("fixtures/workflows/valid-n-of-1.yaml", text)
                self.assertIn("fixtures/workflows/valid-hypothesis-tournament.yaml", text)
                self.assertIn("csi_evidence_pack.json", text)
                self.assertIn("fixture-only", text.lower())
                self.assertIn("portable public export", text.lower())

    def _run_manifest(self, manifest, output_root):
        args = list(manifest["cli_args"])
        runs_index = args.index("--runs-dir") + 1
        run_id_index = args.index("--run-id") + 1
        args[runs_index] = str(output_root)
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = main(args)
        self.assertEqual(exit_code, 0)
        return output_root / args[run_id_index]

    @staticmethod
    def _read_example(name):
        return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _assert_public_artifact_sanitized(self, payload):
        self._assert_no_forbidden_keys(payload)
        self._assert_no_forbidden_words(payload)
        self._assert_no_absolute_paths(payload)

    def _assert_no_raw_signal_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(csi_key=key):
                    self.assertNotIn(
                        str(key).lower(),
                        {
                            "samples",
                            "raw_values",
                            "real",
                            "imag",
                            "amplitude",
                            "phase",
                            "rssi",
                            "source_id",
                            "source_ids",
                        },
                    )
                self._assert_no_raw_signal_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_raw_signal_keys(item)

    def _assert_no_forbidden_keys(self, payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                with self.subTest(public_csi_key=key):
                    self.assertNotIn(str(key).lower(), FORBIDDEN_PUBLIC_CSI_KEYS)
                self._assert_no_forbidden_keys(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_keys(item)

    def _assert_no_forbidden_words(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_forbidden_words(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_forbidden_words(item)
        elif isinstance(payload, str):
            lowered = (
                payload.lower()
                .replace(
                    "real-mode-authorization-missing",
                    "real-mode-gap-missing",
                )
                .replace("not-authorized", "not-runtime-status")
                .replace("authorization_status", "runtime_status")
                .replace(
                    "runtime_authorization_gap_ledger_contract_version",
                    "runtime_gap_ledger_contract_version",
                )
            )
            for word in FORBIDDEN_PUBLIC_CSI_WORDS:
                with self.subTest(public_csi_word=word):
                    self.assertNotIn(word, lowered)

    def _assert_no_absolute_paths(self, payload):
        if isinstance(payload, dict):
            for value in payload.values():
                self._assert_no_absolute_paths(value)
        elif isinstance(payload, list):
            for item in payload:
                self._assert_no_absolute_paths(item)
        elif isinstance(payload, str):
            normalized = payload.replace("\\", "/")
            self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), normalized)
            self.assertNotRegex(normalized, r"^[A-Za-z]:/")


if __name__ == "__main__":
    unittest.main()
