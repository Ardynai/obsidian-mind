"""Lock every committed Phase-12 review fixture to validate as compatible.

This regression test discovers every per-phase Phase-12 validator via
``inspect.getmembers`` and round-trips each validator with its corresponding
committed fixture JSON file from ``fixtures/reviews/``.  It asserts that each
fixture loads cleanly and is reported as ``compatible`` by its own validator,
so that a committed fixture can never silently drift from the contract that
defines it.
"""

import glob
import inspect
import json
import re
import unittest
from pathlib import Path

from somatic.safety import phase12_contracts

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "fixtures" / "reviews"

_VALIDATOR_NAME_RE = re.compile(r"^validate_(phase12[a-z])_")


class Phase12FixtureValidatorRoundTripTests(unittest.TestCase):
    """Every Phase-12 fixture must validate as *compatible* through its validator."""

    @classmethod
    def setUpClass(cls):
        cls.validators = sorted(
            (name, func)
            for name, func in inspect.getmembers(phase12_contracts, inspect.isroutine)
            if _VALIDATOR_NAME_RE.match(name)
        )

    def test_at_least_15_validators_found(self):
        self.assertGreaterEqual(len(self.validators), 15)

    def test_every_validator_fixture_roundtrip_is_compatible(self):
        matched = 0
        for name, func in self.validators:
            with self.subTest(validator=name):
                m = _VALIDATOR_NAME_RE.match(name)
                self.assertIsNotNone(m, f"could not extract phase token from {name}")
                phase_token = m.group(1)  # e.g. "phase12a"

                # Convert "phase12a" to "phase-12a" for fixture filename glob.
                fixture_prefix = phase_token.replace("phase12", "phase-12")
                pattern = str(FIXTURES_DIR / f"{fixture_prefix}-*.json")
                matches = glob.glob(pattern)
                self.assertEqual(
                    len(matches),
                    1,
                    (
                        f"expected exactly one fixture for {phase_token}, "
                        f"found {len(matches)}: {matches}"
                    ),
                )

                fixture_path = Path(matches[0])
                with fixture_path.open(encoding="utf-8") as fh:
                    fixture = json.load(fh)

                result = func(fixture)
                self.assertTrue(
                    result.compatible,
                    f"{name} rejected fixture {fixture_path.name}: {result.errors}",
                )
                matched += 1

        # Every discovered validator must have resolved to exactly one fixture.
        self.assertEqual(matched, len(self.validators))


if __name__ == "__main__":
    unittest.main()
