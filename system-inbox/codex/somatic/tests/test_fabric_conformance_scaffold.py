import json
import tempfile
import unittest
from pathlib import Path

from somatic.fabric.canonical import FabricIntegerError
from somatic.fabric.conformance import (
    code_signature_threshold_errors,
    integer_only_json_errors,
    license_gate_errors,
    path_confinement_errors,
)
from somatic.fabric.fixtures import FABRIC_CONFORMANCE_FIXTURES, load_conformance_fixture
from somatic.mock_runtime import run_mock_workflow

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_ROOT = REPO_ROOT / "fixtures" / "fabric" / "conformance"


class FabricConformanceScaffoldTests(unittest.TestCase):
    def test_fabric_conformance_fixtures_exist_and_parse(self):
        expected = {
            "README.md",
            "sample-pack-signing-payload.json",
            "sample-pack-signed.json",
            "sample-keyring.json",
            "sample-catalog.json",
            "expected-digests.json",
            "invalid-float-pack.json",
            "invalid-path-pack.json",
            "invalid-code-unsigned-pack.json",
            "invalid-license-pack.json",
        }

        self.assertEqual(set(FABRIC_CONFORMANCE_FIXTURES), expected)
        for filename in expected:
            path = CONFORMANCE_ROOT / filename
            self.assertTrue(path.exists(), filename)
            if filename.endswith(".json"):
                with self.subTest(filename=filename):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_invalid_float_fixture_is_detected_by_integer_only_walk(self):
        with self.assertRaises(FabricIntegerError):
            load_conformance_fixture("invalid-float-pack.json")

        manifest = json.loads(
            (CONFORMANCE_ROOT / "invalid-float-pack.json").read_text(encoding="utf-8")
        )
        errors = integer_only_json_errors(manifest)

        self.assertTrue(any("float" in error for error in errors), errors)

    def test_invalid_path_fixture_is_detected_by_path_precheck(self):
        manifest = load_conformance_fixture("invalid-path-pack.json")

        errors = path_confinement_errors(manifest)

        self.assertTrue(any(".." in error or "not confined" in error for error in errors), errors)

    def test_unsigned_code_pack_fails_signature_threshold_precheck(self):
        manifest = load_conformance_fixture("invalid-code-unsigned-pack.json")

        errors = code_signature_threshold_errors(manifest)

        self.assertTrue(any("code packs require" in error for error in errors), errors)

    def test_invalid_license_fixture_fails_license_gate_precheck(self):
        manifest = load_conformance_fixture("invalid-license-pack.json")

        errors = license_gate_errors(manifest)

        self.assertTrue(any("license" in error.lower() for error in errors), errors)

    def test_existing_workflows_still_run(self):
        fixtures = (
            "valid-literature-only.yaml",
            "valid-hypothesis-tournament.yaml",
            "valid-robin-loop.yaml",
        )
        with tempfile.TemporaryDirectory() as tmp:
            for fixture in fixtures:
                with self.subTest(fixture=fixture):
                    run_dir = run_mock_workflow(
                        REPO_ROOT / "fixtures" / "workflows" / fixture,
                        repo_root=REPO_ROOT,
                        output_root=Path(tmp) / fixture,
                        run_id=f"run-{fixture.removesuffix('.yaml')}",
                    )
                    self.assertTrue((run_dir / "manifest.json").exists())
                    self.assertTrue((run_dir / "reports" / "report.md").exists())


if __name__ == "__main__":
    unittest.main()
