import unittest

from somatic.fabric.fixtures import load_conformance_fixture
from somatic.fabric.manifest import evaluate_license_policy, validate_pack_manifest
from somatic.fabric.pathing import (
    path_confinement_errors,
    type_install_root,
    validate_install_target_for_type,
)


class FabricManifestTests(unittest.TestCase):
    def test_valid_sample_pack_passes_current_shape_validators(self):
        manifest = load_conformance_fixture("sample-pack-signed.json")

        result = validate_pack_manifest(manifest)

        self.assertTrue(result.valid, result.errors)

    def test_unsigned_code_pack_fails_validation(self):
        manifest = load_conformance_fixture("invalid-code-unsigned-pack.json")

        result = validate_pack_manifest(manifest)

        self.assertFalse(result.valid)
        self.assertTrue(
            any("code packs require" in error for error in result.errors), result.errors
        )

    def test_invalid_license_pack_fails_validation(self):
        manifest = load_conformance_fixture("invalid-license-pack.json")

        result = validate_pack_manifest(manifest)

        self.assertFalse(result.valid)
        self.assertTrue(any("license" in error.lower() for error in result.errors), result.errors)

    def test_invalid_path_pack_fails_validation(self):
        manifest = load_conformance_fixture("invalid-path-pack.json")

        result = validate_pack_manifest(manifest)

        self.assertFalse(result.valid)
        self.assertTrue(any("not confined" in error for error in result.errors), result.errors)

    def test_manifest_rejects_class_type_mismatch_and_unsorted_files(self):
        manifest = load_conformance_fixture("sample-pack-signed.json")
        manifest["class"] = "data"
        manifest["type"] = "plugin"
        manifest["files"] = [
            dict(
                manifest["files"][0],
                path="z.json",
                installTarget="somatic/sample-dataset/z.json",
            ),
            dict(
                manifest["files"][0],
                path="a.json",
                installTarget="somatic/sample-dataset/a.json",
            ),
        ]

        result = validate_pack_manifest(manifest)

        self.assertFalse(result.valid)
        self.assertTrue(
            any("type must be legal" in error for error in result.errors), result.errors
        )
        self.assertTrue(
            any("files must be sorted" in error for error in result.errors), result.errors
        )

    def test_pathing_confines_install_target_to_type_root(self):
        self.assertEqual(type_install_root("dataset"), "datasets")
        self.assertEqual(
            validate_install_target_for_type("dataset", "somatic/sample-dataset/records.json"),
            "datasets/somatic/sample-dataset/records.json",
        )
        errors = path_confinement_errors(
            {
                "files": [
                    {
                        "path": "../escape.json",
                        "installTarget": "somatic/../escape.json",
                    }
                ]
            }
        )

        self.assertTrue(errors)

    def test_license_policy_distinguishes_public_private_and_install(self):
        public_manifest = load_conformance_fixture("sample-pack-signed.json")
        public_policy = evaluate_license_policy(public_manifest)

        self.assertTrue(public_policy["publish"]["allowed"])
        self.assertTrue(public_policy["seed"]["allowed"])
        self.assertTrue(public_policy["catalog"]["allowed"])
        self.assertTrue(public_policy["install"]["allowed"])

        private_manifest = dict(
            public_manifest,
            license="proprietary",
            harnesses=["somatic"],
            transport={
                "infohash": "1" * 40,
                "magnet": (
                    "magnet:?xt=urn:btih:1111111111111111111111111111111111111111"
                    "&dn=private&ws=https%3A%2F%2Fexample.invalid%2Fprivate%2F"
                ),
            },
        )
        private_policy = evaluate_license_policy(private_manifest)

        self.assertTrue(private_policy["publish"]["allowed"])
        self.assertFalse(private_policy["seed"]["allowed"])
        self.assertFalse(private_policy["catalog"]["allowed"])
        self.assertTrue(private_policy["install"]["allowed"])

        blocked_policy = evaluate_license_policy(dict(public_manifest, license="NOASSERTION"))

        self.assertFalse(blocked_policy["publish"]["allowed"])
        self.assertFalse(blocked_policy["install"]["allowed"])
        self.assertIn("not redistribution", blocked_policy["publish"]["reason"])


if __name__ == "__main__":
    unittest.main()
