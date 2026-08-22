import unittest

from somatic.fabric.catalog import validate_catalog_shape
from somatic.fabric.fixtures import load_conformance_fixture
from somatic.fabric.keyring import validate_keyring_shape


class FabricKeyringCatalogTests(unittest.TestCase):
    def test_sample_keyring_passes_shape_validation(self):
        keyring = load_conformance_fixture("sample-keyring.json")

        result = validate_keyring_shape(keyring)

        self.assertTrue(result.valid, result.errors)

    def test_keyring_rejects_invalid_threshold_and_status(self):
        keyring = load_conformance_fixture("sample-keyring.json")
        keyring["rootThreshold"] = 2
        keyring["rootKeys"][0]["status"] = "pending"

        result = validate_keyring_shape(keyring)

        self.assertFalse(result.valid)
        self.assertTrue(any("rootThreshold" in error for error in result.errors), result.errors)
        self.assertTrue(any("status" in error for error in result.errors), result.errors)

    def test_sample_catalog_passes_shape_validation(self):
        catalog = load_conformance_fixture("sample-catalog.json")

        result = validate_catalog_shape(catalog)

        self.assertTrue(result.valid, result.errors)

    def test_catalog_rejects_duplicate_pack_entries(self):
        catalog = load_conformance_fixture("sample-catalog.json")
        catalog["packs"].append(dict(catalog["packs"][0]))

        result = validate_catalog_shape(catalog)

        self.assertFalse(result.valid)
        self.assertTrue(any("duplicate" in error for error in result.errors), result.errors)


if __name__ == "__main__":
    unittest.main()
