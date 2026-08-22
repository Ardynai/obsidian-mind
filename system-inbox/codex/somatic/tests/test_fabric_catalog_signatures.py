import json
import unittest
from pathlib import Path

from somatic.fabric.catalog import validate_catalog_shape, verify_catalog_signature_threshold
from somatic.fabric.crypto import CRYPTO_AVAILABLE

REPO_ROOT = Path(__file__).resolve().parents[1]
CRYPTO_ROOT = REPO_ROOT / "fixtures" / "fabric" / "crypto"


def load_crypto_fixture(filename):
    return json.loads((CRYPTO_ROOT / filename).read_text(encoding="utf-8"))


class FabricCatalogSignatureFixtureTests(unittest.TestCase):
    def test_catalog_signature_fixtures_exist_and_parse(self):
        for filename in ("signed-catalog.json", "invalid-catalog-signature.json"):
            with self.subTest(filename=filename):
                self.assertTrue((CRYPTO_ROOT / filename).exists(), filename)
                load_crypto_fixture(filename)


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricCatalogSignatureTests(unittest.TestCase):
    def test_signed_catalog_verifies_against_keyring(self):
        catalog = load_crypto_fixture("signed-catalog.json")
        keyring = load_crypto_fixture("keyring-signed.json")

        shape = validate_catalog_shape(catalog)
        result = verify_catalog_signature_threshold(catalog, keyring)

        self.assertTrue(shape.valid, shape.errors)
        self.assertTrue(result.trusted, result.reason)
        self.assertEqual(result.required_signatures, 1)
        self.assertEqual(result.valid_signatures, 1)

    def test_invalid_catalog_signature_fails_closed(self):
        catalog = load_crypto_fixture("invalid-catalog-signature.json")
        keyring = load_crypto_fixture("keyring-signed.json")

        result = verify_catalog_signature_threshold(catalog, keyring)

        self.assertFalse(result.trusted)
        self.assertIn("signature", result.reason.lower())


if __name__ == "__main__":
    unittest.main()
