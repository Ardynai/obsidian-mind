import unittest
from pathlib import Path

from somatic.fabric.interop import compare_fixture_metadata, describe_interop_fixture_locations

REPO_ROOT = Path(__file__).resolve().parents[1]


class FabricInteropPlaceholderTests(unittest.TestCase):
    def test_docs_and_placeholder_fixtures_exist(self):
        expected_paths = (
            REPO_ROOT / "docs" / "fabric-locus-interop.md",
            REPO_ROOT / "docs" / "fabric-implementation-gap-analysis.md",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "README.md",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "locus-fixtures-placeholder.md",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "somatic-fixtures-placeholder.md",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "somatic-generated-pack.json",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "somatic-generated-keyring.json",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "somatic-generated-catalog.json",
            REPO_ROOT / "fixtures" / "fabric" / "interop" / "somatic-generated-metadata.json",
        )

        for path in expected_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

        interop_doc = (REPO_ROOT / "docs" / "fabric-locus-interop.md").read_text(encoding="utf-8")
        self.assertIn("partial mutual verification", interop_doc.lower())
        self.assertIn("not certified", interop_doc.lower())

    def test_helper_describes_locations_and_metadata_differences(self):
        locations = describe_interop_fixture_locations(REPO_ROOT)

        self.assertIn("fixtures/fabric/interop", locations["somatic_interop_dir"])
        self.assertTrue(locations["somatic_generated_pack"].endswith("somatic-generated-pack.json"))
        self.assertTrue(
            locations["somatic_generated_metadata"].endswith("somatic-generated-metadata.json")
        )
        self.assertIn(
            "C:/AI/locus/electron/content-fabric",
            locations["locus_expected_paths"],
        )

        comparison = compare_fixture_metadata(
            {"schemaVersion": "1.0.0", "id": "somatic/example", "version": "1.0.0"},
            {"schemaVersion": "1.0.0", "id": "somatic/example", "version": "1.0.1"},
            fields=("schemaVersion", "id", "version"),
        )

        self.assertEqual(comparison["matching"], ("id", "schemaVersion"))
        self.assertEqual(comparison["different"], ("version",))
        self.assertEqual(comparison["missing"], ())


if __name__ == "__main__":
    unittest.main()
