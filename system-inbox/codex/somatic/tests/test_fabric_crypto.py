import hashlib
import unittest

from somatic.fabric.crypto import (
    CRYPTO_AVAILABLE,
    CryptoUnavailableError,
    key_id_for_public_key_bytes,
    private_key_from_raw_bytes,
    public_key_base64,
    public_key_from_base64,
    public_key_raw_bytes,
    sign_bytes,
    signature_from_base64,
    signature_to_base64,
    verify_signature_bytes,
)


@unittest.skipUnless(CRYPTO_AVAILABLE, "optional Fabric crypto backend is unavailable")
class FabricCryptoTests(unittest.TestCase):
    def test_key_id_derivation_is_sha256_lowercase_hex(self):
        raw_public_key = bytes(range(32))

        self.assertEqual(
            key_id_for_public_key_bytes(raw_public_key),
            hashlib.sha256(raw_public_key).hexdigest(),
        )

    def test_ed25519_roundtrip_sign_verify_and_base64_helpers(self):
        private_key = private_key_from_raw_bytes(b"\x01" * 32)
        public_key = public_key_from_base64(public_key_base64(private_key.public_key()))
        signature = sign_bytes(private_key, b"payload")

        encoded_signature = signature_to_base64(signature)

        self.assertEqual(signature_from_base64(encoded_signature), signature)
        self.assertEqual(len(public_key_raw_bytes(public_key)), 32)
        self.assertTrue(verify_signature_bytes(public_key, b"payload", signature))
        self.assertFalse(verify_signature_bytes(public_key, b"tampered", signature))


class FabricCryptoUnavailableTests(unittest.TestCase):
    def test_unavailable_error_type_exists(self):
        self.assertTrue(issubclass(CryptoUnavailableError, RuntimeError))


if __name__ == "__main__":
    unittest.main()
