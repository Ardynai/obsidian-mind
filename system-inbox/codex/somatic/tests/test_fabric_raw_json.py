import json
import unittest
from pathlib import Path

from somatic.fabric.canonical import (
    FabricIntegerError,
    FabricJsonError,
    loads_fabric_json,
    validate_raw_json_numbers,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = REPO_ROOT / "fixtures" / "fabric" / "raw-json"


class FabricRawJsonTests(unittest.TestCase):
    def test_raw_numeric_lexeme_rejections_ignore_json_strings(self):
        for raw in (
            '{"size":1.5}',
            '{"size":1e3}',
            '{"size":01}',
            '{"size":+1}',
            '{"size":-1}',
            '{"size":9007199254740992}',
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(FabricIntegerError):
                    validate_raw_json_numbers(raw)

        validate_raw_json_numbers('{"note":"1.5 1e3 01 +1 -1 9007199254740992 are text","size":0}')

    def test_valid_max_integer_loads_and_stays_integer_only(self):
        parsed = loads_fabric_json('{"size":9007199254740991,"items":[0,12]}')

        self.assertEqual(parsed["size"], 9007199254740991)
        self.assertEqual(parsed["items"], [0, 12])

    def test_raw_json_fixtures_cover_numeric_edges(self):
        cases = {
            "invalid-exponent.json": False,
            "invalid-leading-zero.json": False,
            "invalid-plus-number.json": False,
            "invalid-negative-number.json": False,
            "invalid-huge-integer.json": False,
            "valid-max-integer.json": True,
        }

        for filename, should_parse in cases.items():
            with self.subTest(filename=filename):
                raw = (RAW_ROOT / filename).read_text(encoding="utf-8")
                if should_parse:
                    self.assertIsInstance(loads_fabric_json(raw), dict)
                else:
                    with self.assertRaises(FabricIntegerError):
                        loads_fabric_json(raw)

    def test_invalid_json_still_raises_json_decode_error_after_numeric_scan(self):
        with self.assertRaises(json.JSONDecodeError):
            loads_fabric_json('{"size":1,,}')

    def test_duplicate_object_names_are_rejected(self):
        with self.assertRaises(FabricJsonError):
            loads_fabric_json('{"id":"first","id":"second"}')

        with self.assertRaises(FabricJsonError):
            loads_fabric_json('{"outer":{"id":"first","id":"second"}}')

    def test_lone_surrogate_escapes_are_rejected(self):
        with self.assertRaises(FabricJsonError):
            loads_fabric_json('{"bad":"\\ud800"}')


if __name__ == "__main__":
    unittest.main()
