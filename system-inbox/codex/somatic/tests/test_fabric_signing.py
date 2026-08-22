import json
import unittest
from pathlib import Path

from somatic.fabric.crypto import CRYPTO_AVAILABLE, private_key_from_raw_bytes
from somatic.fabric.fixtures import load_conformance_fixture
from somatic.fabric.signing import sign_object, signing_payload, verify_object_signature

REPO_ROOT = Path(__file__).resolve().parents[1]


class FabricSigningPayloadTests(unittest.TestCase):
    def test_signing_payload_sets_top_level_signatures_to_empty_array(self):
        manifest = load_conformance_fixture("sample-pack-signed.json")

        payload = signing_payload(manifest)
        parsed = json.loads(payload.decode("utf-8"))

        self.assertEqual(parsed["signatures"], [])
        self.assertNotEqual(manifest["signatures"], [])


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricSigningCryptoTests(unittest.TestCase):
    def test_sign_object_adds_verifiable_signature(self):
        private_key = private_key_from_raw_bytes(b"\x02" * 32)
        manifest = load_conformance_fixture("sample-pack-signing-payload.json")

        signed = sign_object(manifest, private_key)

        self.assertEqual(len(signed["signatures"]), 1)
        self.assertTrue(
            verify_object_signature(signed, signed["signatures"][0], private_key.public_key())
        )

        tampered = dict(signed, version="0.1.1")
        self.assertFalse(
            verify_object_signature(tampered, signed["signatures"][0], private_key.public_key())
        )


if __name__ == "__main__":
    unittest.main()
