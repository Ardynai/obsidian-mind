import ast
import importlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from somatic.providers.biomodel import BiomodelRequest
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_PATHS = (
    REPO_ROOT / "somatic" / "providers" / "biomodel.py",
    REPO_ROOT / "somatic" / "providers" / "boltz.py",
)


class BoltzProviderScaffoldTests(unittest.TestCase):
    def test_provider_modules_import_without_boltz_installed(self):
        biomodel = importlib.import_module("somatic.providers.biomodel")
        boltz = importlib.import_module("somatic.providers.boltz")

        self.assertIsNotNone(biomodel.BiomodelPlan)
        self.assertIsNotNone(boltz.BoltzProvider)

    def test_fake_backed_provider_returns_deterministic_plan_and_result(self):
        from somatic.providers.boltz import BoltzProvider, BoltzProviderConfig

        request = BiomodelRequest(
            objective="Plan Boltz-2 structure and affinity metadata.",
            target_refs=("target://mock-complex",),
            input_artifact_refs=("fixture://biomodel/input.yaml",),
            constraints={"allow_msa_server": False, "allow_model_download": False},
        )
        provider = BoltzProvider(BoltzProviderConfig(enabled=True, mode="mock"))

        first_plan = provider.plan(request)
        second_plan = provider.plan(request)
        first_result = provider.run(request)
        second_result = provider.run(request)
        evidence_record = provider.evidence_record(request, first_result)

        self.assertEqual(first_plan, second_plan)
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_plan.provider_id, "boltz2-biomodel-provider")
        self.assertIn("boltz", first_plan.command_shape)
        self.assertIn("execute boltz predict", first_plan.blocked_actions)
        self.assertFalse(first_plan.metadata["runtime_execution"])
        self.assertIn("readiness_report", first_plan.metadata)
        self.assertFalse(first_plan.metadata["readiness_report"]["ready"])
        self.assertFalse(first_plan.metadata["readiness_report"]["execution_permitted"])
        self.assertIn(
            "runtime-execution-disabled",
            first_plan.metadata["readiness_report"]["block_reasons"],
        )
        self.assertEqual(
            first_plan.metadata["readiness_report"],
            first_result.metadata["readiness_report"],
        )
        self.assertFalse(first_result.metadata["model_downloads"])
        self.assertEqual(evidence_record.raw_evidence.source.modality, "sim")
        self.assertEqual(
            evidence_record.raw_evidence.source.metadata["submodality"],
            "biomodel",
        )

    def test_real_mode_default_fails_closed_on_readiness_gates(self):
        from somatic.providers.boltz import (
            BoltzProvider,
            BoltzProviderConfig,
            BoltzReadinessGateError,
        )

        provider = BoltzProvider(BoltzProviderConfig(enabled=True, mode="real"))

        with self.assertRaises(BoltzReadinessGateError) as context:
            provider.plan(BiomodelRequest("real mode should fail closed"))

        self.assertIn(
            "runtime-execution-disabled",
            context.exception.readiness_report.block_reasons,
        )

    def test_real_mode_fails_clearly_when_dependency_is_unavailable_after_gates(self):
        from somatic.providers.boltz import (
            BoltzOptionalDependencyError,
            BoltzProvider,
            BoltzProviderConfig,
        )
        from somatic.safety.biomodel import BiomodelConsentRecord, BiomodelRuntimePolicy

        policy = BiomodelRuntimePolicy(
            runtime_execution_enabled=True,
            model_downloads_enabled=True,
            msa_server_enabled=True,
            network_calls_enabled=True,
            gpu_execution_enabled=True,
            resource_review_complete=True,
            provenance_plan_complete=True,
        )
        consent = BiomodelConsentRecord(
            user_consent=True,
            research_only_acknowledged=True,
            resource_review_acknowledged=True,
            provenance_plan_acknowledged=True,
            consent_scope="unit-test",
        )
        provider = BoltzProvider(
            BoltzProviderConfig(
                enabled=True,
                mode="real",
                runtime_policy=policy,
                consent_record=consent,
            )
        )

        with patch("somatic.providers.boltz.find_spec", return_value=None):
            with self.assertRaisesRegex(BoltzOptionalDependencyError, "optional 'boltz'"):
                provider.plan(BiomodelRequest("real mode should fail"))

    def test_real_mode_fails_even_if_dependency_is_detectable(self):
        from somatic.providers.boltz import (
            BoltzProvider,
            BoltzProviderConfig,
            BoltzRuntimeNotEnabledError,
        )
        from somatic.safety.biomodel import BiomodelConsentRecord, BiomodelRuntimePolicy

        policy = BiomodelRuntimePolicy(
            runtime_execution_enabled=True,
            model_downloads_enabled=True,
            msa_server_enabled=True,
            network_calls_enabled=True,
            gpu_execution_enabled=True,
            resource_review_complete=True,
            provenance_plan_complete=True,
        )
        consent = BiomodelConsentRecord(
            user_consent=True,
            research_only_acknowledged=True,
            resource_review_acknowledged=True,
            provenance_plan_acknowledged=True,
            consent_scope="unit-test",
        )
        provider = BoltzProvider(
            BoltzProviderConfig(
                enabled=True,
                mode="real",
                runtime_policy=policy,
                consent_record=consent,
            )
        )

        with patch("somatic.providers.boltz.find_spec", return_value=object()):
            with self.assertRaisesRegex(BoltzRuntimeNotEnabledError, "Phase 6C"):
                provider.run(BiomodelRequest("real mode should still fail"))

    def test_provider_fixtures_parse_and_record_disabled_boundaries(self):
        fixture_names = (
            "boltz2-provider-placeholder.json",
            "boltz2-provider-mock-config.json",
        )

        for fixture_name in fixture_names:
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads(
                    (REPO_ROOT / "fixtures" / "providers" / fixture_name).read_text(
                        encoding="utf-8"
                    )
                )

                self.assertFalse(payload["external_runtime_enabled"])
                self.assertTrue(payload["disabled_by_default"])
                self.assertFalse(payload["limits"]["network_calls_allowed"])
                self.assertFalse(payload["limits"]["runtime_import_allowed"])
                self.assertFalse(payload["limits"]["model_download_allowed"])
                self.assertFalse(payload["limits"]["msa_server_allowed"])
                self.assertFalse(payload["limits"]["gpu_execution_allowed"])
                self.assertEqual(payload["optional_dependency"]["package"], "boltz")

    def test_doctor_reports_boltz_scaffold_status(self):
        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("Boltz-2 biomodel provider: scaffolded", output)
        self.assertIn("Boltz-2 staged source:", output)
        self.assertIn("Boltz-2 optional dependency:", output)
        self.assertIn("Boltz-2 model downloads: disabled", output)
        self.assertIn("Boltz-2 MSA server: disabled", output)
        self.assertIn("Boltz-2 runtime execution: disabled", output)
        self.assertIn("Biomodel safety gates: scaffolded", output)
        self.assertIn("Biomodel fake-backed in-silico mode: available", output)
        self.assertIn("Biomodel provenance packaging: planning only", output)
        self.assertIn("Biomodel Fabric pack class recommendation: data", output)
        self.assertIn("Biomodel Fabric pack publishing: disabled", output)
        self.assertIn("Biomodel Fabric transport/install: disabled", output)
        self.assertIn("Biomodel real runtime: future only", output)

    def test_provider_scaffold_introduces_no_network_or_runtime_imports(self):
        forbidden_import_roots = {
            "boltz",
            "torch",
            "requests",
            "urllib",
            "http",
            "socket",
            "wandb",
            "rdkit",
        }
        forbidden_call_names = {"urlopen", "request", "create_connection", "predict"}

        for path in PROVIDER_PATHS:
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        module = node.module.split(".")[0]
                        self.assertNotIn(module, forbidden_import_roots)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, forbidden_call_names)


if __name__ == "__main__":
    unittest.main()
