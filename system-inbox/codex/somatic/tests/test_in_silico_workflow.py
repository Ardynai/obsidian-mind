import ast
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.mock_runtime import run_mock_workflow
from somatic.workflow_loader import load_mock_provider_metadata, load_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "fixtures" / "workflows"
INSILICO_FIXTURE = WORKFLOW_DIR / "valid-in-silico-screening.yaml"
BIOMODEL_ARTIFACTS = (
    "biomodel_request",
    "biomodel_readiness_report",
    "biomodel_consent_record",
    "biomodel_plan",
    "biomodel_result",
    "biomodel_evidence_record",
    "biomodel_raw_evidence",
    "biomodel_structured_verdict",
    "biomodel_provenance_bundle",
    "biomodel_pack_plan",
    "in_silico_summary",
)


class InSilicoWorkflowTests(unittest.TestCase):
    def test_fixture_loads_with_boltz_fake_backed_provider_metadata(self):
        workflow = load_workflow(INSILICO_FIXTURE)
        providers = load_mock_provider_metadata(workflow, REPO_ROOT)

        self.assertEqual(workflow["mode"], "in-silico-screening")
        self.assertEqual(
            workflow["safety_profile"]["domain"],
            "research-only-in-silico-planning",
        )
        self.assertFalse(workflow["safety_profile"]["external_actions_allowed"])
        self.assertIn("biomodel", providers)
        self.assertEqual(providers["biomodel"]["provider_id"], "boltz2-biomodel-provider")
        self.assertTrue(providers["biomodel"]["fake_backed"])
        self.assertFalse(providers["biomodel"]["limits"]["network_calls_allowed"])
        self.assertFalse(providers["biomodel"]["limits"]["model_download_allowed"])
        self.assertFalse(providers["biomodel"]["limits"]["msa_server_allowed"])
        self.assertFalse(providers["biomodel"]["limits"]["prediction_execution_allowed"])
        for input_item in workflow["inputs"]:
            ref = input_item.get("ref", "")
            if ref.startswith("fixture://"):
                relative = ref.removeprefix("fixture://")
                self.assertTrue((REPO_ROOT / "fixtures" / relative).exists(), ref)

    def test_in_silico_workflow_writes_biomodel_artifacts_and_report_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                INSILICO_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-insilico-test",
            )

            manifest = self._read_json(run_dir / "manifest.json")
            report = (run_dir / "reports" / "report.md").read_text(encoding="utf-8")

            self.assertEqual(manifest["mode"], "in-silico-screening")
            provider_ids = {provider["provider_id"] for provider in manifest["providers"]}
            self.assertIn("boltz2-biomodel-provider", provider_ids)
            for required in (
                "workflow",
                "inputs",
                "evidence",
                "safety_response",
                "report",
                "next_iteration",
            ):
                self.assertIn(required, manifest["artifacts"])
                self.assertTrue((run_dir / manifest["artifacts"][required]).exists())
            for artifact_name in BIOMODEL_ARTIFACTS:
                self.assertIn(artifact_name, manifest["artifacts"])
                self.assertIn(artifact_name, manifest["hashes"])
                payload = self._read_json(run_dir / manifest["artifacts"][artifact_name])
                self.assertEqual(payload["schema_version"], 1)
                self.assertEqual(
                    manifest["hashes"][artifact_name],
                    self._sha256(run_dir / manifest["artifacts"][artifact_name]),
                )

            request = self._read_json(run_dir / "artifacts" / "biomodel_request.json")
            readiness = self._read_json(run_dir / "artifacts" / "biomodel_readiness_report.json")
            consent = self._read_json(run_dir / "artifacts" / "biomodel_consent_record.json")
            plan = self._read_json(run_dir / "artifacts" / "biomodel_plan.json")
            result = self._read_json(run_dir / "artifacts" / "biomodel_result.json")
            raw = self._read_json(run_dir / "artifacts" / "biomodel_raw_evidence.json")
            verdict = self._read_json(run_dir / "artifacts" / "biomodel_structured_verdict.json")
            provenance = self._read_json(run_dir / "artifacts" / "biomodel_provenance_bundle.json")
            pack_plan = self._read_json(run_dir / "artifacts" / "biomodel_pack_plan.json")
            summary = self._read_json(run_dir / "artifacts" / "in_silico_summary.json")

            self.assertEqual(plan["provider_id"], "boltz2-biomodel-provider")
            self.assertEqual(
                plan["metadata"]["readiness_report"]["block_reasons"],
                readiness["block_reasons"],
            )
            self.assertEqual(
                result["metadata"]["readiness_report"]["block_reasons"],
                readiness["block_reasons"],
            )
            self.assertFalse(readiness["ready"])
            self.assertFalse(readiness["execution_permitted"])
            self.assertEqual(readiness["runtime_boundary"], "future-real-runtime-only")
            self.assertIn("runtime-execution-disabled", readiness["block_reasons"])
            self.assertIn("missing-user-consent", readiness["block_reasons"])
            self.assertFalse(consent["user_consent"])
            self.assertFalse(consent["research_only_acknowledged"])
            self.assertEqual(result["status"], "mock-planned-not-executed")
            self.assertFalse(result["metadata"]["runtime_execution"])
            self.assertFalse(result["metadata"]["model_downloads"])
            self.assertFalse(result["metadata"]["msa_server"])
            self.assertFalse(result["metadata"]["network_calls"])
            self.assertFalse(result["metadata"]["gpu_execution"])
            self.assertEqual(raw["source"]["modality"], "sim")
            self.assertEqual(raw["source"]["metadata"]["submodality"], "biomodel")
            self.assertEqual(raw["payload_ref"], "artifacts/biomodel_result.json")
            self.assertEqual(raw["sha256"], self._sha256(run_dir / raw["payload_ref"]))
            self.assertEqual(verdict["confidence"], "not-applicable")
            self.assertTrue(summary["fake_backed_planning_only"])
            self.assertFalse(summary["biomodel_readiness_ready"])
            self.assertFalse(summary["biomodel_runtime_execution_permitted"])
            self.assertTrue(summary["biomodel_runtime_blocked"])
            self.assertEqual(summary["biomodel_block_reasons"], readiness["block_reasons"])
            self.assertFalse(summary["boltz_execution"])
            self.assertFalse(summary["model_weights_downloaded"])
            self.assertFalse(summary["msa_server_call"])
            self.assertFalse(summary["real_prediction"])
            self.assertIn("target://mock-protein-complex", request["target_refs"])
            self.assertEqual(
                summary["biomodel_provenance_bundle_id"],
                provenance["id"],
            )
            self.assertEqual(summary["biomodel_pack_plan_id"], pack_plan["id"])
            self.assertEqual(provenance["phase"], "6D")
            self.assertEqual(provenance["workflow_id"], "valid-in-silico-screening")
            self.assertEqual(provenance["provider_id"], "boltz2-biomodel-provider")
            self.assertEqual(provenance["provider_scaffold_status"], "scaffolded")
            self.assertEqual(provenance["source"]["license"], "MIT")
            self.assertEqual(
                provenance["source"]["inspected_commit"],
                plan["provenance"]["inspected_commit"],
            )
            self.assertTrue(provenance["research_only"])
            self.assertFalse(provenance["runtime_execution"])
            self.assertFalse(provenance["network_calls"])
            self.assertFalse(provenance["fabric_transport_enabled"])
            self.assertFalse(provenance["fabric_install_enabled"])
            artifact_by_id = {item["id"]: item for item in provenance["artifact_refs"]}
            for artifact_name in (
                "biomodel_request",
                "biomodel_readiness_report",
                "biomodel_consent_record",
                "biomodel_plan",
                "biomodel_result",
                "biomodel_evidence_record",
                "biomodel_raw_evidence",
                "biomodel_structured_verdict",
            ):
                with self.subTest(provenance_artifact=artifact_name):
                    self.assertIn(artifact_name, artifact_by_id)
                    self.assertEqual(
                        artifact_by_id[artifact_name]["sha256"],
                        self._sha256(run_dir / artifact_by_id[artifact_name]["relative_path"]),
                    )
            self.assertEqual(pack_plan["bundle_id"], provenance["id"])
            self.assertEqual(pack_plan["phase"], "6D")
            self.assertEqual(pack_plan["status"], "planned-not-packed")
            self.assertEqual(pack_plan["pack_class"], "data")
            self.assertIn(pack_plan["candidate_type"], {"dataset", "document"})
            self.assertFalse(pack_plan["code_pack"])
            self.assertEqual(pack_plan["executable_files"], [])
            self.assertFalse(pack_plan["publishing_enabled"])
            self.assertFalse(pack_plan["catalog_publish_enabled"])
            self.assertFalse(pack_plan["signing_enabled"])
            self.assertFalse(pack_plan["signed_pack_created"])
            self.assertFalse(pack_plan["draft_pack_manifest"])
            self.assertFalse(pack_plan["public_seeding_allowed"])
            self.assertEqual(pack_plan["transport_status"], "absent-future")
            self.assertTrue(pack_plan["license_review_required"])
            for forbidden_key in (
                "transport",
                "signatures",
                "publisher",
                "keyring",
                "catalog",
                "manifestDigest",
                "infohash",
            ):
                self.assertNotIn(forbidden_key, pack_plan)

            boundary_phrases = (
                "fake-backed planning only",
                "no Boltz execution",
                "no model weights downloaded",
                "no MSA server call",
                "no GPU/runtime execution",
                "no real structure or affinity prediction",
                "no medical, lab, or scientific conclusion",
                "biomodel safety gates",
                "biomodel provenance packaging",
                "no Fabric publishing or transport",
                "real biomodel runtime: future only",
                "future real mode requires explicit opt-in",
            )
            for phrase in boundary_phrases:
                with self.subTest(phrase=phrase):
                    self.assertIn(phrase.lower(), report.lower())

    def test_existing_workflows_and_fabric_check_still_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fixture_name in (
                "valid-literature-only.yaml",
                "valid-hypothesis-tournament.yaml",
                "valid-robin-loop.yaml",
            ):
                with self.subTest(fixture_name=fixture_name):
                    run_dir = run_mock_workflow(
                        WORKFLOW_DIR / fixture_name,
                        repo_root=REPO_ROOT,
                        output_root=Path(tmp),
                        run_id=f"run-{fixture_name.replace('.yaml', '')}",
                    )
                    self.assertTrue((run_dir / "manifest.json").exists())

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "fabric",
                    "check",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "signed-code-pack.json"),
                    "--keyring",
                    str(REPO_ROOT / "fixtures" / "fabric" / "crypto" / "keyring-signed.json"),
                ]
            )
        output = stdout.getvalue()
        expected = 0 if CRYPTO_AVAILABLE else 1
        self.assertEqual(exit_code, expected, output)
        if CRYPTO_AVAILABLE:
            self.assertIn("Fabric check: valid signed-code-pack.json", output)
            self.assertIn("crypto: publisher threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())
            self.assertIn("failing closed", output.lower())
            self.assertIn("optional fabric extra", output.lower())

    def test_in_silico_biomodel_artifacts_are_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = run_mock_workflow(
                INSILICO_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-insilico-left",
            )
            right = run_mock_workflow(
                INSILICO_FIXTURE,
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-insilico-right",
            )

            for artifact_name in (
                "biomodel_plan",
                "biomodel_readiness_report",
                "biomodel_consent_record",
                "biomodel_result",
                "biomodel_evidence_record",
                "biomodel_raw_evidence",
                "biomodel_structured_verdict",
                "biomodel_provenance_bundle",
                "biomodel_pack_plan",
                "in_silico_summary",
            ):
                with self.subTest(artifact_name=artifact_name):
                    self.assertEqual(
                        self._read_json(left / "artifacts" / f"{artifact_name}.json"),
                        self._read_json(right / "artifacts" / f"{artifact_name}.json"),
                    )
                    self.assertEqual(
                        self._sha256(left / "artifacts" / f"{artifact_name}.json"),
                        self._sha256(right / "artifacts" / f"{artifact_name}.json"),
                    )

    def test_scaffold_imports_and_runtime_add_no_network_or_download_surfaces(self):
        module_names = (
            "somatic.providers.paperqa2",
            "somatic.providers.scientific_agent_skills",
            "somatic.providers.robin",
            "somatic.providers.team_orchestration",
            "somatic.providers.boltz",
            "somatic.providers.biomodel_provenance",
        )
        for module_name in module_names:
            with self.subTest(module_name=module_name):
                __import__(module_name)

        forbidden_import_roots = {"boltz", "requests", "urllib", "http", "socket"}
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "download",
            "predict",
        }
        for path in (
            REPO_ROOT / "somatic" / "mock_runtime.py",
            REPO_ROOT / "somatic" / "providers" / "boltz.py",
            REPO_ROOT / "somatic" / "safety" / "biomodel.py",
            REPO_ROOT / "somatic" / "providers" / "biomodel_provenance.py",
        ):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        module = node.module.split(".")[0]
                        self.assertNotIn(module, forbidden_import_roots)
                    if isinstance(node, ast.Call):
                        name = (
                            node.func.id
                            if isinstance(node.func, ast.Name)
                            else getattr(node.func, "attr", None)
                        )
                        self.assertNotIn(name, forbidden_call_names)

    @staticmethod
    def _read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
