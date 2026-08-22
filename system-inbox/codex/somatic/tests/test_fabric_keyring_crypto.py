import json
import unittest
from pathlib import Path

from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.fabric.keyring import (
    validate_keyring_shape,
    verify_keyring_root_threshold,
    verify_pack_publisher_threshold,
)
from somatic.fabric.manifest import validate_pack_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
CRYPTO_ROOT = REPO_ROOT / "fixtures" / "fabric" / "crypto"


def load_crypto_fixture(filename):
    return json.loads((CRYPTO_ROOT / filename).read_text(encoding="utf-8"))


class FabricCryptoFixtureShapeTests(unittest.TestCase):
    def test_crypto_fixtures_exist_and_parse(self):
        filenames = (
            "test-root-key.json",
            "test-publisher-key.json",
            "signed-data-pack.json",
            "signed-code-pack.json",
            "keyring-signed.json",
            "invalid-signature-pack.json",
        )
        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertTrue((CRYPTO_ROOT / filename).exists(), filename)
                load_crypto_fixture(filename)


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricKeyringCryptoTests(unittest.TestCase):
    def test_signed_keyring_passes_shape_and_root_threshold(self):
        keyring = load_crypto_fixture("keyring-signed.json")

        shape = validate_keyring_shape(keyring)
        trusted = verify_keyring_root_threshold(keyring)

        self.assertTrue(shape.valid, shape.errors)
        self.assertTrue(trusted.trusted, trusted.reason)
        self.assertEqual(trusted.valid_signatures, 1)

    def test_signed_pack_verifies_publisher_threshold(self):
        keyring = load_crypto_fixture("keyring-signed.json")
        manifest = load_crypto_fixture("signed-data-pack.json")

        result = verify_pack_publisher_threshold(manifest, keyring)

        self.assertTrue(validate_pack_manifest(manifest).valid)
        self.assertTrue(result.trusted, result.reason)
        self.assertEqual(result.valid_signatures, 1)

    def test_signed_code_pack_verifies_and_unsigned_code_still_fails(self):
        keyring = load_crypto_fixture("keyring-signed.json")
        signed_code = load_crypto_fixture("signed-code-pack.json")
        unsigned_code = json.loads(
            (
                REPO_ROOT
                / "fixtures"
                / "fabric"
                / "conformance"
                / "invalid-code-unsigned-pack.json"
            ).read_text(encoding="utf-8")
        )

        signed_result = verify_pack_publisher_threshold(signed_code, keyring)
        unsigned_result = verify_pack_publisher_threshold(unsigned_code, keyring)

        self.assertTrue(validate_pack_manifest(signed_code).valid)
        self.assertTrue(signed_result.trusted, signed_result.reason)
        self.assertFalse(unsigned_result.trusted)
        self.assertIn("signature", unsigned_result.reason.lower())

    def test_invalid_signature_fails_publisher_threshold(self):
        keyring = load_crypto_fixture("keyring-signed.json")
        manifest = load_crypto_fixture("invalid-signature-pack.json")

        result = verify_pack_publisher_threshold(manifest, keyring)

        self.assertFalse(result.trusted)
        self.assertIn("threshold", result.reason.lower())

    def test_revoked_key_valid_until_logic_is_basic_and_deterministic(self):
        keyring = load_crypto_fixture("keyring-signed.json")
        manifest = load_crypto_fixture("signed-data-pack.json")
        keyring["publishers"][0]["keys"][0]["status"] = "revoked"
        keyring["publishers"][0]["keys"][0]["validUntil"] = "2026-05-28T17:04:08Z"

        result = verify_pack_publisher_threshold(manifest, keyring)

        self.assertFalse(result.trusted)
        self.assertIn("threshold", result.reason.lower())


if __name__ == "__main__":
    unittest.main()
