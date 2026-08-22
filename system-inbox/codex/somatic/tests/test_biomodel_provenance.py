import ast
import json
import tempfile
import unittest
from pathlib import Path

from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PATH = REPO_ROOT / "somatic" / "providers" / "biomodel_provenance.py"


class BiomodelProvenanceTests(unittest.TestCase):
    def test_builds_deterministic_provenance_bundle_from_artifact_payloads(self):
        from somatic.providers.biomodel_provenance import (
            build_biomodel_pack_plan,
            build_biomodel_provenance_bundle,
            hash_artifact_payload,
        )

        artifacts = {
            "biomodel_request": {"schema_version": 1, "id": "request-001"},
            "biomodel_readiness_report": {
                "schema_version": 1,
                "ready": False,
                "execution_permitted": False,
            },
            "biomodel_consent_record": {
                "schema_version": 1,
                "user_consent": False,
            },
            "biomodel_plan": {
                "schema_version": 1,
                "id": "plan-001",
                "provider_id": "boltz2-biomodel-provider",
                "model_version": "boltz2",
                "provenance": {
                    "source_path": "C:\\AI\\external-sources\\somatic\\boltz",
                    "inspected_commit": "b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc",
                    "license": "MIT",
                },
                "assumptions": ["Mock mode emits metadata only."],
                "limitations": ["No real prediction is produced."],
            },
            "biomodel_result": {
                "schema_version": 1,
                "id": "result-001",
                "status": "mock-planned-not-executed",
                "assumptions": ["Mock mode emits metadata only."],
                "limitations": ["No real prediction is produced."],
            },
            "biomodel_evidence_record": {"schema_version": 1, "id": "evidence-001"},
            "biomodel_raw_evidence": {"schema_version": 1, "id": "raw-001"},
            "biomodel_structured_verdict": {
                "schema_version": 1,
                "id": "verdict-001",
            },
        }

        first = build_biomodel_provenance_bundle(artifacts)
        second = build_biomodel_provenance_bundle(artifacts)
        pack_plan = build_biomodel_pack_plan(first)

        self.assertEqual(first, second)
        payload = first.to_dict()
        self.assertEqual(payload["provider_id"], "boltz2-biomodel-provider")
        self.assertEqual(payload["provider_version"], "boltz2")
        self.assertEqual(payload["provider_scaffold_status"], "scaffolded")
        self.assertEqual(payload["source"]["license"], "MIT")
        self.assertTrue(payload["research_only"])
        self.assertFalse(payload["runtime_execution"])
        self.assertFalse(payload["network_calls"])
        self.assertFalse(payload["fabric_publish_enabled"])
        artifact_by_id = {item["id"]: item for item in payload["artifact_refs"]}
        self.assertEqual(
            artifact_by_id["biomodel_result"]["sha256"],
            hash_artifact_payload(artifacts["biomodel_result"]),
        )
        self.assertEqual(
            artifact_by_id["biomodel_result"]["relative_path"],
            "artifacts/biomodel_result.json",
        )

        pack_payload = pack_plan.to_dict()
        self.assertEqual(pack_payload["pack_class"], "data")
        self.assertIn(pack_payload["candidate_type"], {"dataset", "document"})
        self.assertFalse(pack_payload["code_pack"])
        self.assertEqual(pack_payload["executable_files"], [])
        self.assertFalse(pack_payload["publishing_enabled"])
        self.assertEqual(pack_payload["transport_status"], "absent-future")
        self.assertFalse(pack_payload["draft_pack_manifest"])
        self.assertFalse(pack_payload["signing_enabled"])
        self.assertFalse(pack_payload["signed_pack_created"])
        self.assertFalse(pack_payload["catalog_publish_enabled"])
        self.assertFalse(pack_payload["public_seeding_allowed"])
        self.assertTrue(pack_payload["license_review_required"])
        for forbidden_key in (
            "transport",
            "signatures",
            "publisher",
            "keyring",
            "catalog",
            "manifestDigest",
            "infohash",
        ):
            self.assertNotIn(forbidden_key, pack_payload)

        with self.assertRaisesRegex(ValueError, "candidate_type"):
            build_biomodel_pack_plan(first, candidate_type="model")

    def test_hash_artifact_file_matches_payload_hash_for_run_writer_json(self):
        from somatic.providers.biomodel_provenance import (
            hash_artifact_file,
            hash_artifact_payload,
        )

        payload = {"schema_version": 1, "id": "hash-test", "values": [3, 2, 1]}
        expected = hash_artifact_payload(payload)
        tmp_path = REPO_ROOT / "runs" / "tmp-phase6d-hash-test.json"
        try:
            tmp_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path.write_bytes(
                (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            )
            self.assertEqual(hash_artifact_file(tmp_path), expected)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_collects_run_refs_and_rebuilds_bundle_from_run_folder(self):
        from somatic.providers.biomodel_provenance import (
            BIOMODEL_PROVENANCE_ARTIFACT_ORDER,
            build_biomodel_provenance_bundle_from_run,
            collect_run_artifact_refs,
            hash_artifact_file,
        )

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                REPO_ROOT / "fixtures" / "workflows" / "valid-in-silico-screening.yaml",
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-phase6d-provenance-helper-test",
            )

            refs = collect_run_artifact_refs(run_dir)
            bundle = build_biomodel_provenance_bundle_from_run(run_dir)

            self.assertEqual(
                [ref.id for ref in refs],
                list(BIOMODEL_PROVENANCE_ARTIFACT_ORDER),
            )
            for ref in refs:
                self.assertEqual(
                    ref.sha256,
                    hash_artifact_file(run_dir / ref.relative_path),
                )
            self.assertEqual(bundle.workflow_id, "valid-in-silico-screening")
            self.assertEqual(bundle.provider_id, "boltz2-biomodel-provider")
            self.assertEqual(bundle.source["license"], "MIT")
            self.assertFalse(bundle.fabric_publish_enabled)
            self.assertFalse(bundle.fabric_transport_enabled)

    def test_provenance_fixtures_parse_and_stay_planning_only(self):
        bundle = self._read_json(
            REPO_ROOT / "fixtures" / "biomodel" / "biomodel-provenance-bundle-placeholder.json"
        )
        pack_plan = self._read_json(
            REPO_ROOT / "fixtures" / "biomodel" / "biomodel-pack-plan-placeholder.json"
        )

        self.assertEqual(bundle["provider_id"], "boltz2-biomodel-provider")
        self.assertTrue(bundle["research_only"])
        self.assertFalse(bundle["runtime_execution"])
        self.assertFalse(bundle["fabric_publish_enabled"])
        self.assertEqual(
            {item["id"] for item in bundle["artifact_refs"]},
            {
                "biomodel_request",
                "biomodel_readiness_report",
                "biomodel_consent_record",
                "biomodel_plan",
                "biomodel_result",
                "biomodel_evidence_record",
                "biomodel_raw_evidence",
                "biomodel_structured_verdict",
            },
        )
        self.assertEqual(pack_plan["pack_class"], "data")
        self.assertFalse(pack_plan["code_pack"])
        self.assertFalse(pack_plan["publishing_enabled"])
        self.assertFalse(pack_plan["signing_enabled"])
        self.assertFalse(pack_plan["signed_pack_created"])
        self.assertFalse(pack_plan["public_seeding_allowed"])
        self.assertEqual(pack_plan["transport_status"], "absent-future")

    def test_provenance_module_adds_no_network_or_runtime_surfaces(self):
        forbidden_import_roots = {
            "boltz",
            "torch",
            "requests",
            "urllib",
            "http",
            "socket",
            "rdkit",
            "wandb",
        }
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "download",
            "predict",
            "import_module",
        }

        tree = ast.parse(PROVENANCE_PATH.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                self.assertTrue(imported.isdisjoint(forbidden_import_roots))
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                module = node.module.split(".")[0]
                self.assertNotIn(module, forbidden_import_roots)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, forbidden_call_names)

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
