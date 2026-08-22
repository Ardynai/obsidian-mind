import json
import tempfile
import unittest
from pathlib import Path

from somatic.evidence.document_fixture import DocumentFixtureEvidenceProvider
from somatic.run_writer import write_run_artifacts
from somatic.sensors.environment import EnvironmentFixtureSensorProvider
from somatic.sensors.toy_counter import ToyCounterFixtureSensorProvider


class RunWriterTests(unittest.TestCase):
    def test_writes_expected_run_artifact_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_run_artifacts(
                output_root=Path(tmp),
                run_id="run-test-001",
                workflow={"id": "wf", "mode": "literature-only"},
                provider_metadata={"literature": {"id": "mock-literature-provider"}},
                evidence={"id": "ev-001"},
                safety_response={"id": "safe-001"},
                hypotheses=[{"id": "hyp-001", "statement": "Example"}],
                report_markdown="# Report\n",
                next_iteration={"recommended_actions": []},
            )

            expected_files = [
                "manifest.json",
                "workflow.json",
                "inputs/README.md",
                "evidence/evidence.json",
                "artifacts/hypotheses.json",
                "safety/safety-response.json",
                "reports/report.md",
                "next_iteration.json",
            ]
            for relative in expected_files:
                self.assertTrue((run_dir / relative).exists(), relative)

            manifest = json.loads((run_dir / "manifest.json").read_text())
            self.assertEqual(manifest["run_id"], "run-test-001")
            self.assertTrue(manifest["mock"])
            self.assertTrue(manifest["offline"])
            self.assertTrue(manifest["not_medical_advice"])

    def test_written_json_artifacts_are_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_run_artifacts(
                output_root=Path(tmp),
                run_id="run-test-002",
                workflow={"id": "wf", "mode": "literature-only"},
                provider_metadata={},
                evidence={"id": "ev-001"},
                safety_response={"id": "safe-001"},
                hypotheses=[],
                report_markdown="# Report\n",
                next_iteration={"recommended_actions": []},
            )

            for relative in (
                "manifest.json",
                "workflow.json",
                "evidence/evidence.json",
                "artifacts/hypotheses.json",
                "safety/safety-response.json",
                "next_iteration.json",
            ):
                json.loads((run_dir / relative).read_text())

    def test_manifest_sensor_evidence_refs_include_multiple_provider_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            environment_pack = EnvironmentFixtureSensorProvider().evidence_pack(
                ("environment-parsed.csv",),
                repo_root=Path.cwd(),
            )
            toy_pack = ToyCounterFixtureSensorProvider().evidence_pack(
                ("toy-counter-parsed.csv",),
                repo_root=Path.cwd(),
            )
            document_pack = DocumentFixtureEvidenceProvider().evidence_pack(
                ("document-parsed.json",),
                repo_root=Path.cwd(),
            )
            csi_pack = {
                "schema_version": 1,
                "pack_id": "csi-evidence-pack-" + "a" * 16,
                "pack_fingerprint": "a" * 64,
                "status": "parsed",
                "readiness_status": "ready-with-sanitized-metadata",
            }
            run_dir = write_run_artifacts(
                output_root=Path(tmp),
                run_id="run-test-sensor-evidence-refs",
                workflow={"id": "wf", "mode": "n-of-1"},
                provider_metadata={},
                evidence={"id": "ev-001"},
                safety_response={"id": "safe-001"},
                hypotheses=[],
                report_markdown="# Report\n",
                next_iteration={"recommended_actions": []},
                extra_artifacts={
                    "csi_evidence_pack": {
                        "relative_path": "artifacts/csi_evidence_pack.json",
                        "payload": csi_pack,
                    },
                    "environment_evidence_pack": {
                        "relative_path": "artifacts/environment_evidence_pack.json",
                        "payload": environment_pack,
                    },
                    "toy_counter_evidence_pack": {
                        "relative_path": "artifacts/toy_counter_evidence_pack.json",
                        "payload": toy_pack,
                    },
                    "document_evidence_pack": {
                        "relative_path": "artifacts/document_evidence_pack.json",
                        "payload": document_pack,
                    },
                    "environment_local_diagnostic": {
                        "relative_path": "artifacts/environment_local_diagnostic.json",
                        "payload": {"schema_version": 1, "id": "local-diagnostic"},
                    },
                },
            )

            manifest = json.loads((run_dir / "manifest.json").read_text())

        refs = manifest["sensor_evidence_artifact_refs"]
        self.assertEqual(
            set(refs),
            {
                "csi_evidence_pack",
                "document_evidence_pack",
                "environment_evidence_pack",
                "toy_counter_evidence_pack",
            },
        )
        self.assertEqual(
            refs["csi_evidence_pack"]["artifact_ref"], "artifacts/csi_evidence_pack.json"
        )
        self.assertEqual(
            refs["environment_evidence_pack"]["artifact_ref"],
            "artifacts/environment_evidence_pack.json",
        )
        self.assertEqual(refs["environment_evidence_pack"]["provider_kind"], "environment-fixture")
        self.assertEqual(
            refs["environment_evidence_pack"]["sha256"],
            manifest["hashes"]["environment_evidence_pack"],
        )
        self.assertEqual(
            refs["toy_counter_evidence_pack"]["artifact_ref"],
            "artifacts/toy_counter_evidence_pack.json",
        )
        self.assertEqual(
            refs["toy_counter_evidence_pack"]["provider_kind"],
            "toy-counter-fixture",
        )
        self.assertEqual(
            refs["toy_counter_evidence_pack"]["sha256"],
            manifest["hashes"]["toy_counter_evidence_pack"],
        )
        self.assertEqual(
            refs["document_evidence_pack"]["artifact_ref"],
            "artifacts/document_evidence_pack.json",
        )
        self.assertEqual(
            refs["document_evidence_pack"]["provider_kind"],
            "document-fixture",
        )
        self.assertEqual(
            refs["document_evidence_pack"]["evidence_kind"],
            "document-evidence-pack",
        )
        self.assertEqual(
            refs["document_evidence_pack"]["sha256"],
            manifest["hashes"]["document_evidence_pack"],
        )
        self.assertNotIn("environment_local_diagnostic", refs)


if __name__ == "__main__":
    unittest.main()
