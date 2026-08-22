import ast
import contextlib
import importlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from somatic.cli import main
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.mock_runtime import run_mock_workflow
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "fixtures" / "workflows"
PROVIDER_DIR = REPO_ROOT / "fixtures" / "providers"


class FinchExtrasProviderTests(unittest.TestCase):
    def test_provider_modules_import_without_optional_packages(self):
        extras = importlib.import_module("somatic.analysis.extras")
        provider = importlib.import_module("somatic.analysis.provider")

        self.assertEqual(
            [definition.id for definition in extras.EXTRA_DEFINITIONS],
            ["pandas", "scipy", "numpy", "scanpy", "biopython"],
        )
        self.assertIsNotNone(provider.FinchExtrasProvider)

    def test_fake_backed_provider_returns_deterministic_status(self):
        from somatic.analysis.provider import FinchExtrasProvider, FinchExtrasProviderConfig

        provider = FinchExtrasProvider(FinchExtrasProviderConfig(mode="mock"))
        left = provider.status()
        right = provider.status()

        self.assertEqual(left, right)
        self.assertEqual(left["provider_id"], "finch-extras-provider")
        self.assertTrue(left["fake_backed"])
        self.assertFalse(left["runtime_enabled"])
        self.assertEqual(left["default_path"], "standard-library-finch")
        self.assertEqual(
            [item["id"] for item in left["extras"]],
            ["pandas", "scipy", "numpy", "scanpy", "biopython"],
        )
        for item in left["extras"]:
            self.assertIn(item["availability"], {"available", "unavailable"})
            self.assertEqual(item["status"], "disabled-by-default")
            self.assertFalse(item["runtime_enabled"])
            self.assertFalse(item["clinical_or_genomic_interpretation"])

    def test_real_mode_fails_when_optional_dependency_is_unavailable(self):
        from somatic.analysis.provider import (
            FinchExtrasProvider,
            FinchExtrasProviderConfig,
            FinchExtrasRuntimeNotEnabledError,
        )

        with mock.patch("somatic.analysis.extras.importlib.util.find_spec", return_value=None):
            provider = FinchExtrasProvider(
                FinchExtrasProviderConfig(mode="real", enabled=True, selected_extra="scanpy")
            )
            with self.assertRaisesRegex(FinchExtrasRuntimeNotEnabledError, "scanpy"):
                provider.require_real_extra("scanpy")

    def test_provider_fixtures_parse_and_stay_disabled(self):
        for fixture_name in (
            "finch-extras-provider-placeholder.json",
            "finch-extras-provider-mock-config.json",
        ):
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads((PROVIDER_DIR / fixture_name).read_text(encoding="utf-8"))
                self.assertEqual(payload["provider_id"], "finch-extras-provider")
                self.assertTrue(payload["fake_backed"])
                self.assertTrue(payload["disabled_by_default"])
                self.assertFalse(payload["external_runtime_enabled"])
                self.assertFalse(payload["limits"]["network_calls_allowed"])
                self.assertFalse(payload["limits"]["runtime_import_allowed"])
                self.assertFalse(payload["limits"]["live_execution_allowed"])
                self.assertEqual(
                    [item["id"] for item in payload["optional_extras"]],
                    ["pandas", "scipy", "numpy", "scanpy", "biopython"],
                )

    def test_doctor_reports_finch_extras_status(self):
        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("Finch optional extras provider: scaffolded, disabled by default", output)
        self.assertIn("Finch standard-library fallback: active", output)
        self.assertIn("Finch optional dependency pandas:", output)
        self.assertIn("Finch optional dependency scanpy:", output)

    def test_robin_loop_emits_optional_extras_status_in_finch_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = run_mock_workflow(
                WORKFLOW_DIR / "valid-robin-loop.yaml",
                repo_root=REPO_ROOT,
                output_root=Path(tmp),
                run_id="run-phase5g-robin-test",
            )

            summary = json.loads(
                (run_dir / "artifacts" / "finch_toolbelt_summary.json").read_text(encoding="utf-8")
            )

        self.assertEqual(summary["toolbelt_status"], "standard-library-local")
        self.assertIn("optional_extras", summary)
        self.assertEqual(summary["optional_extras"]["provider_id"], "finch-extras-provider")
        self.assertEqual(summary["optional_extras"]["default_path"], "standard-library-finch")
        self.assertFalse(summary["optional_extras"]["runtime_enabled"])

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
                        output_root=Path(tmp) / fixture_name,
                        run_id=f"run-phase5g-{fixture_name.removesuffix('.yaml')}",
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
            self.assertIn("valid signed-code-pack.json", output)
            self.assertIn("crypto: publisher threshold verified", output)
        else:
            self.assertIn("cryptographic verification unavailable", output.lower())
            self.assertIn("failing closed", output.lower())
            self.assertIn("optional fabric extra", output.lower())

    def test_existing_scaffolds_import_without_execution(self):
        for module_name in (
            "somatic.providers.paperqa2",
            "somatic.providers.scientific_agent_skills",
            "somatic.providers.robin",
            "somatic.providers.team_orchestration",
        ):
            with self.subTest(module_name=module_name):
                self.assertIsNotNone(importlib.import_module(module_name))

    def test_finch_extras_modules_have_no_network_or_eager_optional_imports(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "paperqa",
            "scientific_agent_skills",
            "pandas",
            "numpy",
            "scipy",
            "scanpy",
            "Bio",
            "biopython",
        }
        for relative in (
            "somatic/analysis/extras.py",
            "somatic/analysis/provider.py",
            "somatic/agents/finch_toolbelt.py",
        ):
            with self.subTest(relative=relative):
                tree = ast.parse((REPO_ROOT / relative).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                        self.assertTrue(imported.isdisjoint(forbidden_import_roots))
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        self.assertNotIn(node.module.split(".")[0], forbidden_import_roots)


if __name__ == "__main__":
    unittest.main()
