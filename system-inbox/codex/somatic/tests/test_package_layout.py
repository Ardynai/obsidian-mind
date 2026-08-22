import importlib
import unittest


class PackageLayoutTests(unittest.TestCase):
    def test_master_plan_package_boundaries_are_importable(self):
        for module_name in (
            "somatic.core",
            "somatic.evidence_bus",
            "somatic.science",
            "somatic.provenance",
            "somatic.agents",
            "somatic.engines",
            "somatic.sensors",
            "somatic.safety",
            "somatic.memory",
            "somatic.presence",
            "somatic.fabric",
            "somatic.bench",
            "somatic.cli",
            "somatic.reports",
            "somatic.simulator",
            "somatic.providers",
            "somatic.analysis",
        ):
            with self.subTest(module_name=module_name):
                importlib.import_module(module_name)


if __name__ == "__main__":
    unittest.main()
