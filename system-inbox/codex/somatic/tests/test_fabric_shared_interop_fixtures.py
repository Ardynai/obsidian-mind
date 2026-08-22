import json
import unittest
from pathlib import Path

from somatic.fabric.canonical import canonical_bytes, signing_payload
from somatic.fabric.catalog import validate_catalog_shape, verify_catalog_signature_threshold
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.fabric.digests import manifest_digest, sha256_hex
from somatic.fabric.keyring import (
    validate_keyring_shape,
    verify_keyring_root_threshold,
    verify_pack_publisher_threshold,
)
from somatic.fabric.manifest import validate_pack_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = REPO_ROOT / "fixtures" / "fabric" / "interop" / "shared"
LOCUS_PHASE_4G3_COMMIT = "5f81ee360834dc6451c4ea35d7509325813d9d10"


def load_shared_fixture(filename):
    return json.loads((SHARED_ROOT / filename).read_text(encoding="utf-8"))


class FabricSharedInteropFixtureShapeTests(unittest.TestCase):
    def test_shared_fixture_files_exist_and_parse(self):
        filenames = (
            "README.md",
            "shared-pack.json",
            "shared-data-pack.json",
            "shared-keyring.json",
            "shared-catalog.json",
            "shared-expected.json",
            "shared-invalid-signature-pack.json",
            "shared-invalid-catalog-signature.json",
            "shared-invalid-keyring-threshold.json",
        )

        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertTrue((SHARED_ROOT / filename).exists(), filename)
                if filename.endswith(".json"):
                    load_shared_fixture(filename)

    def test_shared_expected_metadata_describes_test_only_self_certification(self):
        expected = load_shared_fixture("shared-expected.json")

        self.assertTrue(expected["testOnlyKeys"])
        self.assertEqual(expected["generatedBy"]["implementation"], "somatic")
        self.assertEqual(expected["generatedBy"]["phase"], "4G.2")
        self.assertEqual(expected["verification"]["somaticSelfCertification"], "passed")
        self.assertEqual(expected["verification"]["locusVerification"], "passed")
        self.assertEqual(expected["limits"]["network"], False)
        self.assertEqual(expected["limits"]["download"], False)
        self.assertEqual(expected["limits"]["install"], False)
        self.assertEqual(expected["limits"]["quarantine"], False)
        self.assertEqual(expected["limits"]["locusRuntimeDependency"], False)
        self.assertEqual(expected["limits"]["certifiedInterop"], False)
        self.assertEqual(expected["limits"]["sharedFixtureCertification"], True)
        self.assertIn("shared-pack.json", expected["artifacts"])
        self.assertIn("shared-data-pack.json", expected["artifacts"])
        self.assertNotIn("Locus mutual verification", expected["deferred"])
        self.assertIn("Locus-origin companion fixture certification", expected["deferred"])
        self.assertIn("full Locus runtime interop certification", expected["deferred"])
        self.assertEqual(expected["signatureAlgorithms"], ["ed25519"])

    def test_shared_expected_metadata_records_locus_phase4g3_certification(self):
        expected = load_shared_fixture("shared-expected.json")
        locus = expected["locusVerification"]

        self.assertEqual(locus["status"], "certified-shared-fixtures")
        self.assertEqual(locus["path"], "C:\\AI\\locus\\electron\\content-fabric\\")
        self.assertEqual(locus["commit"], LOCUS_PHASE_4G3_COMMIT)
        self.assertEqual(locus["normalCiRequired"], False)
        self.assertEqual(locus["sharedPackCanonicalSha256"], "match")
        self.assertEqual(locus["sharedPackSigningPayloadSha256"], "match")
        self.assertEqual(locus["sharedPackManifestDigest"], "match")
        self.assertEqual(locus["sharedKeyringRootThreshold"], "verified")
        self.assertEqual(locus["sharedPackSignature"], "verified")
        self.assertEqual(locus["sharedDataPackSignature"], "verified")
        self.assertEqual(locus["sharedCatalogValidation"], "verified-shape")
        self.assertEqual(
            locus["sharedCatalogSignature"],
            "verified-with-locus-ed25519-primitive-no-high-level-catalog-verifier",
        )
        self.assertEqual(locus["invalidSignaturePack"], "rejected")
        self.assertEqual(locus["invalidCatalogSignature"], "rejected-with-ed25519-primitive")
        self.assertEqual(locus["invalidKeyringThreshold"], "rejected")
        self.assertIn("npm run test:content", locus["commandsAttempted"])
        self.assertIn("npm run test:security", locus["commandsAttempted"])
        self.assertIn("npm run test:connectivity", locus["commandsAttempted"])

    def test_shared_fixtures_have_expected_shapes_and_unknown_fields(self):
        pack = load_shared_fixture("shared-pack.json")
        data_pack = load_shared_fixture("shared-data-pack.json")
        keyring = load_shared_fixture("shared-keyring.json")
        catalog = load_shared_fixture("shared-catalog.json")

        self.assertTrue(validate_pack_manifest(pack).valid)
        self.assertTrue(validate_pack_manifest(data_pack).valid)
        self.assertTrue(validate_keyring_shape(keyring).valid)
        self.assertTrue(validate_catalog_shape(catalog).valid)
        self.assertIn("xInteropUnknown", pack)
        self.assertIn("xInteropUnknown", data_pack)
        self.assertIn("xInteropUnknown", catalog)
        self.assertEqual(
            [entry["path"] for entry in pack["files"]],
            sorted(entry["path"] for entry in pack["files"]),
        )
        self.assertEqual(
            pack["dependencies"],
            sorted(pack["dependencies"], key=lambda item: item["id"]),
        )
        self.assertEqual(
            [entry["id"] for entry in catalog["packs"]],
            sorted(entry["id"] for entry in catalog["packs"]),
        )

    def test_shared_expected_digests_match_generated_values(self):
        pack = load_shared_fixture("shared-pack.json")
        data_pack = load_shared_fixture("shared-data-pack.json")
        keyring = load_shared_fixture("shared-keyring.json")
        catalog = load_shared_fixture("shared-catalog.json")
        expected = load_shared_fixture("shared-expected.json")

        self.assertEqual(
            expected["digests"]["sharedPackCanonicalSha256"],
            sha256_hex(canonical_bytes(pack)),
        )
        self.assertEqual(
            expected["digests"]["sharedPackSigningPayloadSha256"],
            sha256_hex(signing_payload(pack)),
        )
        self.assertEqual(expected["digests"]["sharedPackManifestDigest"], manifest_digest(pack))
        self.assertEqual(
            expected["digests"]["sharedDataPackSigningPayloadSha256"],
            sha256_hex(signing_payload(data_pack)),
        )
        self.assertEqual(
            expected["digests"]["sharedKeyringSigningPayloadSha256"],
            sha256_hex(signing_payload(keyring)),
        )
        self.assertEqual(
            expected["digests"]["sharedCatalogSigningPayloadSha256"],
            sha256_hex(signing_payload(catalog)),
        )
        self.assertEqual(
            expected["digests"]["sharedCatalogCanonicalSha256"],
            sha256_hex(canonical_bytes(catalog)),
        )


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricSharedInteropFixtureCryptoTests(unittest.TestCase):
    def test_shared_keyring_pack_and_catalog_self_certify(self):
        pack = load_shared_fixture("shared-pack.json")
        data_pack = load_shared_fixture("shared-data-pack.json")
        keyring = load_shared_fixture("shared-keyring.json")
        catalog = load_shared_fixture("shared-catalog.json")

        keyring_result = verify_keyring_root_threshold(keyring)
        pack_result = verify_pack_publisher_threshold(pack, keyring)
        data_pack_result = verify_pack_publisher_threshold(data_pack, keyring)
        catalog_result = verify_catalog_signature_threshold(catalog, keyring)

        self.assertTrue(keyring_result.trusted, keyring_result.reason)
        self.assertTrue(pack_result.trusted, pack_result.reason)
        self.assertTrue(data_pack_result.trusted, data_pack_result.reason)
        self.assertTrue(catalog_result.trusted, catalog_result.reason)

    def test_invalid_shared_fixtures_fail_closed(self):
        keyring = load_shared_fixture("shared-keyring.json")
        invalid_pack = load_shared_fixture("shared-invalid-signature-pack.json")
        invalid_catalog = load_shared_fixture("shared-invalid-catalog-signature.json")
        invalid_keyring = load_shared_fixture("shared-invalid-keyring-threshold.json")

        self.assertFalse(verify_pack_publisher_threshold(invalid_pack, keyring).trusted)
        self.assertFalse(verify_catalog_signature_threshold(invalid_catalog, keyring).trusted)
        self.assertFalse(validate_keyring_shape(invalid_keyring).valid)
        self.assertFalse(verify_keyring_root_threshold(invalid_keyring).trusted)


if __name__ == "__main__":
    unittest.main()
