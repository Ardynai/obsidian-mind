import json
import unittest
from pathlib import Path

from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.fabric.keyring import verify_keyring_replacement

REPO_ROOT = Path(__file__).resolve().parents[1]
ROTATION_ROOT = REPO_ROOT / "fixtures" / "fabric" / "crypto" / "rotation"


def load_rotation_fixture(filename):
    return json.loads((ROTATION_ROOT / filename).read_text(encoding="utf-8"))


class FabricKeyringRotationFixtureTests(unittest.TestCase):
    def test_rotation_fixtures_exist_and_parse(self):
        filenames = (
            "previous-keyring.json",
            "valid-rotated-keyring.json",
            "invalid-equal-version-keyring.json",
            "invalid-expired-keyring.json",
            "invalid-insufficient-previous-signatures-keyring.json",
        )
        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertTrue((ROTATION_ROOT / filename).exists(), filename)
                load_rotation_fixture(filename)


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricKeyringRotationTests(unittest.TestCase):
    def test_valid_rotated_keyring_meets_previous_root_threshold(self):
        previous = load_rotation_fixture("previous-keyring.json")
        rotated = load_rotation_fixture("valid-rotated-keyring.json")

        result = verify_keyring_replacement(rotated, previous)

        self.assertTrue(result.trusted, result.reason)
        self.assertEqual(result.required_signatures, 2)
        self.assertEqual(result.valid_signatures, 2)

    def test_replacement_rejects_equal_version_expiry_and_under_threshold(self):
        previous = load_rotation_fixture("previous-keyring.json")
        cases = {
            "invalid-equal-version-keyring.json": "version",
            "invalid-expired-keyring.json": "expired",
            "invalid-insufficient-previous-signatures-keyring.json": "previous root",
        }

        for filename, reason in cases.items():
            with self.subTest(filename=filename):
                result = verify_keyring_replacement(load_rotation_fixture(filename), previous)

                self.assertFalse(result.trusted)
                self.assertIn(reason, result.reason.lower())


if __name__ == "__main__":
    unittest.main()
