import hashlib
import json
import unittest
from pathlib import Path

from somatic.fabric.canonical import (
    FabricJsonError,
    canonical_bytes,
    canonical_dumps,
    signing_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
JCS_ROOT = REPO_ROOT / "fixtures" / "fabric" / "jcs"


class FabricJcsVectorTests(unittest.TestCase):
    def test_canonical_text_matches_local_jcs_vectors(self):
        expected = json.loads((JCS_ROOT / "expected-canonical.json").read_text(encoding="utf-8"))

        for filename, expected_canonical in expected.items():
            with self.subTest(filename=filename):
                value = json.loads((JCS_ROOT / filename).read_text(encoding="utf-8"))

                canonical = canonical_dumps(value)

                self.assertEqual(canonical, expected_canonical)
                self.assertEqual(canonical_bytes(value), canonical.encode("utf-8"))
                self.assertNotIn(": ", canonical)
                self.assertNotIn(", ", canonical)

    def test_object_keys_sort_by_utf16_code_units(self):
        value = json.loads((JCS_ROOT / "utf16-key-order.json").read_text(encoding="utf-8"))

        canonical = canonical_dumps(value)

        self.assertEqual(
            canonical,
            '{"a":"ascii","\ud7ff":"before-surrogate","😀":"emoji","\ue000":"private-use"}',
        )

    def test_signing_payload_preserves_signatures_key_as_empty_array(self):
        expected = json.loads(
            (JCS_ROOT / "expected-payload-digests.json").read_text(encoding="utf-8")
        )

        for filename, expected_digest in expected.items():
            with self.subTest(filename=filename):
                value = json.loads((JCS_ROOT / filename).read_text(encoding="utf-8"))

                payload = signing_payload(value)
                parsed = json.loads(payload.decode("utf-8"))

                self.assertIn("signatures", parsed)
                self.assertEqual(parsed["signatures"], [])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), expected_digest)

    def test_rejects_unsupported_python_values_before_serializing(self):
        with self.assertRaises(FabricJsonError):
            canonical_dumps({"bad": (1, 2)})

        with self.assertRaises(FabricJsonError):
            canonical_dumps({1: "non-string key"})


if __name__ == "__main__":
    unittest.main()
