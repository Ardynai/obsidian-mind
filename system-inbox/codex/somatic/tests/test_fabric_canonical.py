import json
import tempfile
import unittest
from pathlib import Path

from somatic.fabric.canonical import (
    FabricIntegerError,
    canonical_bytes,
    canonical_dumps,
    signing_payload,
    validate_integer_only_json,
)
from somatic.fabric.digests import manifest_digest, sha256_hex, sha256_path
from somatic.fabric.fixtures import load_conformance_fixture


class FabricCanonicalTests(unittest.TestCase):
    def test_integer_only_validation_rejects_float_fixture(self):
        with self.assertRaises(FabricIntegerError):
            load_conformance_fixture("invalid-float-pack.json")

        manifest = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "fixtures"
                / "fabric"
                / "conformance"
                / "invalid-float-pack.json"
            ).read_text(encoding="utf-8")
        )
        with self.assertRaises(FabricIntegerError):
            validate_integer_only_json(manifest)

    def test_canonical_dumps_is_sorted_compact_and_deterministic(self):
        payload = {"b": 2, "a": {"z": 1, "m": [True, None, "x"]}}

        first = canonical_dumps(payload)
        second = canonical_dumps({"a": {"m": [True, None, "x"], "z": 1}, "b": 2})

        self.assertEqual(first, '{"a":{"m":[true,null,"x"],"z":1},"b":2}')
        self.assertEqual(first, second)
        self.assertEqual(canonical_bytes(payload), first.encode("utf-8"))

    def test_signing_payload_sets_top_level_signatures_to_empty_array(self):
        manifest = load_conformance_fixture("sample-pack-signed.json")

        payload = signing_payload(manifest)
        parsed = json.loads(payload.decode("utf-8"))

        self.assertEqual(parsed["signatures"], [])
        self.assertNotEqual(manifest["signatures"], [])
        self.assertIn('"signatures":[]', payload.decode("utf-8"))

    def test_digest_helpers_are_deterministic(self):
        self.assertEqual(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        manifest = load_conformance_fixture("sample-pack-signed.json")

        self.assertEqual(manifest_digest(manifest), manifest_digest(dict(manifest)))

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.bin"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_path(path), sha256_hex(b"abc"))

    def test_expected_digest_fixture_matches_current_scaffold(self):
        manifest = load_conformance_fixture("sample-pack-signed.json")
        catalog = load_conformance_fixture("sample-catalog.json")
        expected = load_conformance_fixture("expected-digests.json")

        self.assertEqual(
            expected["samplePackSigningPayloadSha256"],
            sha256_hex(signing_payload(manifest)),
        )
        self.assertEqual(
            expected["sampleSignedPackManifestDigest"],
            manifest_digest(manifest),
        )
        self.assertEqual(
            expected["sampleCatalogDigest"],
            manifest_digest(catalog),
        )


if __name__ == "__main__":
    unittest.main()
