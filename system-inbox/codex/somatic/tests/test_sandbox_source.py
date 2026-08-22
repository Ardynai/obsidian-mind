import ast
import unittest
from pathlib import Path

from somatic.evidence_bus import EvidenceSource, MeasurementPlan
from somatic.simulator.sandbox_source import SandboxEvidenceSource

REPO_ROOT = Path(__file__).resolve().parents[1]


class SandboxEvidenceSourceTests(unittest.TestCase):
    def test_supports_robin_modalities(self):
        source = SandboxEvidenceSource()

        self.assertEqual(source.supported_modalities, ("literature", "sim", "wetlab"))

    def test_acquires_deterministic_raw_evidence_for_plan(self):
        literature = EvidenceSource(
            id="src-literature",
            modality="literature",
            provider_ref="sandbox",
            description="Mock literature source.",
        )
        sim = EvidenceSource(
            id="src-sim",
            modality="sim",
            provider_ref="sandbox",
            description="Mock simulation source.",
        )
        wetlab = EvidenceSource(
            id="src-wetlab",
            modality="wetlab",
            provider_ref="sandbox",
            description="Mock wetlab source.",
        )
        plan = MeasurementPlan(
            id="plan-robin-001",
            sources=[literature, sim, wetlab],
            objective="Exercise the offline Robin evidence loop.",
        )
        source = SandboxEvidenceSource()

        first = [item.to_dict() for item in source.acquire(plan)]
        second = [item.to_dict() for item in source.acquire(plan)]

        self.assertEqual(first, second)
        self.assertEqual(
            [item["source"]["modality"] for item in first], ["literature", "sim", "wetlab"]
        )
        for item in first:
            self.assertEqual(len(item["sha256"]), 64)
            self.assertTrue(item["metadata"]["mock"])
            self.assertTrue(item["metadata"]["offline"])
            self.assertIn("research-only", item["metadata"]["boundary"])

    def test_rejects_unsupported_plan_modality(self):
        unsupported_source = EvidenceSource(
            id="src-audio",
            modality="audio",
            provider_ref="sandbox",
            description="Audio is not supported by the Robin sandbox source.",
        )
        plan = MeasurementPlan(
            id="plan-invalid",
            sources=[unsupported_source],
            objective="Unsupported modality.",
        )

        with self.assertRaisesRegex(ValueError, "Unsupported sandbox modality"):
            SandboxEvidenceSource().acquire(plan)

    def test_no_network_or_external_api_surfaces_in_sandbox_source(self):
        forbidden_import_roots = (
            "requests",
            "urllib",
            "http",
            "socket",
            "openai",
            "langgraph",
            "paperqa",
            "futurehouse",
            "scientific_agent_skills",
        )
        forbidden_call_names = ("urlopen", "request", "create_connection")
        path = REPO_ROOT / "somatic" / "simulator" / "sandbox_source.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name.split(".")[0] for alias in node.names]
                for module in imported:
                    with self.subTest(module=module):
                        self.assertNotIn(module, forbidden_import_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split(".")[0]
                with self.subTest(module=module):
                    self.assertNotIn(module, forbidden_import_roots)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                with self.subTest(call=node.func.id):
                    self.assertNotIn(node.func.id, forbidden_call_names)


if __name__ == "__main__":
    unittest.main()
