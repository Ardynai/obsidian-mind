import ast
import importlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from somatic.providers.literature import LiteratureQuery

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_PATH = REPO_ROOT / "somatic" / "providers" / "paperqa2.py"


class PaperQA2ProviderScaffoldTests(unittest.TestCase):
    def test_provider_module_imports_without_paperqa2_installed(self):
        module = importlib.import_module("somatic.providers.paperqa2")

        self.assertIsNotNone(module.PaperQA2LiteratureProvider)

    def test_is_available_returns_boolean(self):
        from somatic.providers.paperqa2 import PaperQA2LiteratureProvider

        provider = PaperQA2LiteratureProvider()

        self.assertIsInstance(provider.is_available(), bool)

    def test_fake_provider_returns_deterministic_literature_context(self):
        from somatic.providers.paperqa2 import PaperQA2LiteratureProvider, PaperQA2ProviderConfig

        provider = PaperQA2LiteratureProvider(
            PaperQA2ProviderConfig(enabled=True, mode="mock", max_results=2)
        )
        query = LiteratureQuery("protein DNA neural computation", max_results=2)

        first = provider.retrieve_literature_context(query)
        second = provider.retrieve_literature_context(query)

        self.assertEqual(first, second)
        self.assertEqual(first["provider_id"], "paperqa2-literature-provider")
        self.assertEqual(len(first["documents"]), 2)
        self.assertEqual(len(first["evidence"]), 2)
        self.assertFalse(first["external_calls"])
        self.assertIn("PaperQA2 staged source inspection", first["documents"][0]["title"])

    def test_real_mode_fails_clearly_if_paperqa2_is_unavailable(self):
        from somatic.providers.paperqa2 import (
            PaperQA2LiteratureProvider,
            PaperQA2OptionalDependencyError,
            PaperQA2ProviderConfig,
        )

        provider = PaperQA2LiteratureProvider(PaperQA2ProviderConfig(enabled=True, mode="real"))

        with patch("somatic.providers.paperqa2.find_spec", return_value=None):
            self.assertFalse(provider.is_available())
            with self.assertRaisesRegex(PaperQA2OptionalDependencyError, "optional 'paperqa'"):
                provider.search(LiteratureQuery("test"))

    def test_provider_fixtures_parse_and_record_disabled_optional_mode(self):
        for fixture_name in (
            "paperqa2-provider-placeholder.json",
            "paperqa2-provider-mock-config.json",
        ):
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads(
                    (REPO_ROOT / "fixtures" / "providers" / fixture_name).read_text(
                        encoding="utf-8"
                    )
                )

                self.assertFalse(payload["external_runtime_enabled"])
                self.assertTrue(payload["disabled_by_default"])
                self.assertFalse(payload["limits"]["network_calls_allowed"])
                self.assertFalse(payload["limits"]["basic_install_dependency"])
                self.assertEqual(payload["optional_dependency"]["package"], "paperqa")

    def test_provider_scaffold_introduces_no_network_or_api_surfaces(self):
        forbidden_import_roots = {"requests", "urllib", "http", "socket", "openai", "paperqa"}
        forbidden_call_names = {"urlopen", "request", "create_connection"}
        tree = ast.parse(PROVIDER_PATH.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                self.assertTrue(imported.isdisjoint(forbidden_import_roots))
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split(".")[0]
                self.assertNotIn(module, forbidden_import_roots)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, forbidden_call_names)


if __name__ == "__main__":
    unittest.main()
