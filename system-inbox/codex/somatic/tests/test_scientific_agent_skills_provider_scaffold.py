import ast
import importlib
import json
import unittest
from pathlib import Path

from somatic.providers.science_skills import SkillLookupRequest
from tests.doctor_fixture import DOCTOR_RESULT

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_PATH = REPO_ROOT / "somatic" / "providers" / "scientific_agent_skills.py"


class ScientificAgentSkillsProviderScaffoldTests(unittest.TestCase):
    def test_provider_module_imports_without_external_dependency(self):
        module = importlib.import_module("somatic.providers.scientific_agent_skills")

        self.assertIsNotNone(module.ScientificAgentSkillsProvider)

    def test_fake_provider_returns_deterministic_skill_catalog(self):
        from somatic.providers.scientific_agent_skills import (
            ScientificAgentSkillsProvider,
            ScientificAgentSkillsProviderConfig,
        )

        provider = ScientificAgentSkillsProvider(
            ScientificAgentSkillsProviderConfig(enabled=True, mode="mock")
        )

        first = provider.catalog_summary()
        second = provider.catalog_summary()

        self.assertEqual(first, second)
        self.assertEqual(first["provider_id"], "scientific-agent-skills-provider")
        self.assertFalse(first["execution_enabled"])
        self.assertFalse(first["external_calls"])
        self.assertGreaterEqual(len(first["skills"]), 5)
        self.assertEqual(first["skills"][0]["id"], "paper-lookup")

    def test_fake_provider_returns_deterministic_database_connector_metadata(self):
        from somatic.providers.scientific_agent_skills import ScientificAgentSkillsProvider

        provider = ScientificAgentSkillsProvider()
        first = provider.list_database_connectors()
        second = provider.list_database_connectors()

        self.assertEqual(first, second)
        self.assertEqual(first[0].id, "pubchem")
        self.assertIn("chemistry", first[0].domains)
        self.assertEqual(provider.describe_database_connector("uniprot").name, "UniProt")

    def test_fake_lookup_and_describe_are_metadata_only(self):
        from somatic.providers.scientific_agent_skills import ScientificAgentSkillsProvider

        provider = ScientificAgentSkillsProvider()
        matches = provider.lookup(
            SkillLookupRequest(task="Find papers and clinical trials", tags=("literature",))
        )

        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0].id, "paper-lookup")
        described = provider.describe_skill("clinical-decision-support")
        self.assertIn("clinical", described.metadata["tags"])
        self.assertFalse(described.metadata["skill_execution"])
        self.assertFalse(described.metadata["external_calls"])

    def test_real_mode_fails_clearly(self):
        from somatic.providers.scientific_agent_skills import (
            ScientificAgentSkillsProvider,
            ScientificAgentSkillsProviderConfig,
            ScientificAgentSkillsRuntimeNotEnabledError,
        )

        provider = ScientificAgentSkillsProvider(
            ScientificAgentSkillsProviderConfig(enabled=True, mode="real")
        )

        with self.assertRaisesRegex(ScientificAgentSkillsRuntimeNotEnabledError, "metadata-only"):
            provider.list_skills()

    def test_provider_fixtures_parse_and_record_disabled_metadata_mode(self):
        for fixture_name in (
            "scientific-agent-skills-provider-placeholder.json",
            "scientific-agent-skills-provider-mock-config.json",
            "scientific-agent-skills-sample-catalog.json",
        ):
            with self.subTest(fixture_name=fixture_name):
                payload = json.loads(
                    (REPO_ROOT / "fixtures" / "providers" / fixture_name).read_text(
                        encoding="utf-8"
                    )
                )

                limits = payload["limits"]
                self.assertFalse(limits["network_calls_allowed"])
                self.assertFalse(limits["basic_install_dependency"])
                if "skill_execution_allowed" in limits:
                    self.assertFalse(limits["skill_execution_allowed"])
                if "database_calls_allowed" in limits:
                    self.assertFalse(limits["database_calls_allowed"])

    def test_doctor_mentions_scaffolded_disabled_status(self):
        exit_code, output = DOCTOR_RESULT
        self.assertEqual(exit_code, 0)
        self.assertIn("scientific-agent-skills provider: scaffolded", output)
        self.assertIn("scientific-agent-skills execution: disabled", output)

    def test_provider_scaffold_introduces_no_network_or_api_surfaces(self):
        forbidden_import_roots = {
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "skill_scanner",
            "scientific_agent_skills",
        }
        forbidden_call_names = {"urlopen", "request", "create_connection"}
        tree = ast.parse(PROVIDER_PATH.read_text(encoding="utf-8"))

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
