import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
SAFETY_PATH = REPO_ROOT / "somatic" / "safety" / "biomodel.py"
DEFAULT_BLOCK_REASONS = (
    "runtime-execution-disabled",
    "model-downloads-disabled",
    "msa-server-disabled",
    "network-calls-disabled",
    "gpu-execution-disabled",
    "missing-resource-review",
    "missing-provenance-plan",
    "missing-user-consent",
    "research-only-boundary-not-acknowledged",
)


class BiomodelSafetyGateTests(unittest.TestCase):
    def test_default_policy_blocks_real_runtime_with_deterministic_reasons(self):
        from somatic.safety.biomodel import (
            BiomodelConsentRecord,
            BiomodelRuntimePolicy,
            evaluate_biomodel_readiness,
        )

        report = evaluate_biomodel_readiness(
            {"id": "plan-placeholder"},
            BiomodelRuntimePolicy(),
            BiomodelConsentRecord(),
        )

        self.assertFalse(report.ready)
        self.assertFalse(report.execution_permitted)
        self.assertEqual(report.block_reasons, DEFAULT_BLOCK_REASONS)
        self.assertEqual(report.to_dict()["block_reasons"], list(DEFAULT_BLOCK_REASONS))
        self.assertEqual(report.to_dict()["runtime_boundary"], "future-real-runtime-only")

    def test_missing_consent_blocks_even_when_runtime_policy_flags_are_enabled(self):
        from somatic.safety.biomodel import (
            BiomodelConsentRecord,
            BiomodelRuntimePolicy,
            evaluate_biomodel_readiness,
        )

        policy = BiomodelRuntimePolicy(
            runtime_execution_enabled=True,
            model_downloads_enabled=True,
            msa_server_enabled=True,
            network_calls_enabled=True,
            gpu_execution_enabled=True,
            resource_review_complete=True,
            provenance_plan_complete=True,
        )
        report = evaluate_biomodel_readiness(
            {"id": "dangerous-plan-placeholder"},
            policy,
            BiomodelConsentRecord(),
        )

        self.assertFalse(report.ready)
        self.assertFalse(report.execution_permitted)
        self.assertEqual(
            report.block_reasons,
            (
                "missing-user-consent",
                "research-only-boundary-not-acknowledged",
            ),
        )

    def test_dangerous_enabled_policy_fixture_still_never_executes(self):
        from somatic.providers.biomodel import BiomodelRequest
        from somatic.providers.boltz import (
            BoltzProvider,
            BoltzProviderConfig,
            BoltzRuntimeNotEnabledError,
        )
        from somatic.safety.biomodel import (
            BiomodelConsentRecord,
            BiomodelRuntimePolicy,
            evaluate_biomodel_readiness,
        )

        policy = BiomodelRuntimePolicy.from_dict(
            self._read_json(
                REPO_ROOT
                / "fixtures"
                / "biomodel"
                / "biomodel-runtime-policy-dangerous-enabled.json"
            )
        )
        consent = BiomodelConsentRecord(
            user_consent=True,
            research_only_acknowledged=True,
            resource_review_acknowledged=True,
            provenance_plan_acknowledged=True,
            consent_scope="fixture-real-mode-test",
        )
        report = evaluate_biomodel_readiness({"id": "all-gates-satisfied"}, policy, consent)

        self.assertTrue(report.ready)
        self.assertFalse(report.execution_permitted)
        self.assertEqual(report.block_reasons, ())
        self.assertEqual(report.to_dict()["phase_runtime"], "not-implemented")

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
                provider.run(BiomodelRequest("dangerous fixture should not execute"))

    def test_unsafe_workflow_constraints_fail_before_fake_artifacts_are_written(self):
        from somatic.mock_runtime import BiomodelReadinessGateError, run_mock_workflow

        with tempfile.TemporaryDirectory() as tmp:
            workflow_path = Path(tmp) / "unsafe-in-silico.yaml"
            workflow_path.write_text(
                """schema_version: 1
id: unsafe-in-silico
title: Unsafe In-Silico Fixture
mode: in-silico-screening
description: Unsafe workflow should fail before artifact generation.
version: 0.1.0
status: fixture
stages: []
inputs: []
providers:
  - ref: biomodel
    class: biomodel
    constraints:
      allow_network_calls: true
artifacts: []
safety_profile:
  domain: research-only-in-silico-planning
  external_actions_allowed: false
  real_lab_action_requires_approval: true
evidence_requirements: {}
output_packet: {}
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(BiomodelReadinessGateError, "allow_network_calls"):
                run_mock_workflow(workflow_path, repo_root=REPO_ROOT, output_root=Path(tmp))

    def test_boltz_package_name_is_locked_before_optional_dependency_probe(self):
        from somatic.providers.biomodel import BiomodelRequest
        from somatic.providers.boltz import (
            BoltzConfigurationError,
            BoltzProvider,
            BoltzProviderConfig,
        )

        provider = BoltzProvider(BoltzProviderConfig(package_name="boltz.main"))

        with patch("somatic.providers.boltz.find_spec") as find_spec:
            with self.assertRaisesRegex(BoltzConfigurationError, "package_name"):
                provider.plan(BiomodelRequest("custom package names are forbidden"))
            find_spec.assert_not_called()

    def test_boltz_config_runtime_flags_raise_typed_configuration_error(self):
        from somatic.providers.biomodel import BiomodelRequest
        from somatic.providers.boltz import (
            BoltzConfigurationError,
            BoltzProvider,
            BoltzProviderConfig,
        )

        blocked_configs = (
            ("allow_runtime_execution", {"allow_runtime_execution": True}),
            ("allow_model_downloads", {"allow_model_downloads": True}),
            ("allow_msa_server", {"allow_msa_server": True}),
            ("allow_network_calls", {"allow_network_calls": True}),
            ("allow_gpu_execution", {"allow_gpu_execution": True}),
        )

        for flag, kwargs in blocked_configs:
            with self.subTest(flag=flag):
                provider = BoltzProvider(BoltzProviderConfig(**kwargs))
                with self.assertRaisesRegex(BoltzConfigurationError, "Phase 6C"):
                    provider.plan(BiomodelRequest(f"{flag} should stay disabled"))

    def test_biomodel_safety_fixtures_parse(self):
        from somatic.safety.biomodel import (
            BiomodelConsentRecord,
            BiomodelReadinessReport,
            BiomodelRuntimePolicy,
        )

        policy = BiomodelRuntimePolicy.from_dict(
            self._read_json(
                REPO_ROOT / "fixtures" / "biomodel" / "biomodel-runtime-policy-safe-default.json"
            )
        )
        consent = BiomodelConsentRecord.from_dict(
            self._read_json(
                REPO_ROOT / "fixtures" / "biomodel" / "biomodel-consent-record-placeholder.json"
            )
        )
        report = BiomodelReadinessReport.from_dict(
            self._read_json(
                REPO_ROOT / "fixtures" / "biomodel" / "biomodel-readiness-report-placeholder.json"
            )
        )

        self.assertFalse(policy.runtime_execution_enabled)
        self.assertFalse(policy.model_downloads_enabled)
        self.assertFalse(consent.user_consent)
        self.assertFalse(consent.research_only_acknowledged)
        self.assertFalse(report.ready)
        self.assertEqual(report.block_reasons, DEFAULT_BLOCK_REASONS)

    def test_biomodel_safety_module_adds_no_network_or_runtime_surfaces(self):
        forbidden_import_roots = {"boltz", "torch", "requests", "urllib", "http", "socket"}
        forbidden_call_names = {
            "urlopen",
            "urlretrieve",
            "request",
            "create_connection",
            "download",
            "predict",
        }

        tree = ast.parse(SAFETY_PATH.read_text(encoding="utf-8"))
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
