"""Cross-phase regression guard for Phase-12 capability profiles.

This test suite imports every ``phase12*_status_summary`` function from
``somatic.safety.phase12_contracts`` and asserts that the runtime-blocked
posture is locked across all Phase-12 sub-phases.  It is TEST-ONLY — it
reads the existing status summaries and does not modify the contracts module.
"""

from __future__ import annotations

import inspect
import unittest

from somatic.safety import phase12_contracts

# ---------------------------------------------------------------------------
# Discover every phase12*_status_summary callable in the contracts module.
# ---------------------------------------------------------------------------

_SUMMARY_FUNCS = [
    (name, func)
    for name, func in sorted(inspect.getmembers(phase12_contracts, inspect.isfunction))
    if name.startswith("phase12") and name.endswith("_status_summary")
]


class Phase12SeriesInvariantTests(unittest.TestCase):
    """Every Phase-12 capability profile must report a runtime-blocked posture."""

    @classmethod
    def setUpClass(cls):
        cls.summaries: list[tuple[str, dict]] = []
        for name, func in _SUMMARY_FUNCS:
            summary = func()
            if not isinstance(summary, dict):
                raise TypeError(f"{name}() must return a dict, got {type(summary)}")
            cls.summaries.append((name, summary))

    def test_at_least_15_summary_functions_exist(self):
        """Phase-12 series must cover at least 15 sub-phase summaries."""
        self.assertGreaterEqual(len(self.summaries), 15)

    def test_execution_permitted_appears_in_majority(self):
        """Sanity check: execution_permitted must appear in >50% of summaries."""
        count = sum(1 for _, s in self.summaries if "execution_permitted" in s)
        self.assertGreater(count, len(self.summaries) / 2)

    def test_every_summary_reports_runtime_blocked(self):
        """Each Phase-12 profile must lock the runtime-blocked posture."""
        for name, summary in self.summaries:
            with self.subTest(phase=name):
                # PRESENT-IF checks — only assert if the key exists.
                if "execution_permitted" in summary:
                    self.assertFalse(
                        summary["execution_permitted"],
                        f"{name}: execution_permitted must be False",
                    )
                if "real_mode_runtime_enabled" in summary:
                    self.assertFalse(
                        summary["real_mode_runtime_enabled"],
                        f"{name}: real_mode_runtime_enabled must be False",
                    )
                if "real_mode_execution_permitted" in summary:
                    self.assertFalse(
                        summary["real_mode_execution_permitted"],
                        f"{name}: real_mode_execution_permitted must be False",
                    )
                if "production_ready" in summary:
                    self.assertFalse(
                        summary["production_ready"],
                        f"{name}: production_ready must be False",
                    )
                if "runtime_stage" in summary:
                    self.assertEqual(
                        summary["runtime_stage"],
                        "not-implemented",
                        f"{name}: runtime_stage must be 'not-implemented'",
                    )
                if "authorization_status" in summary:
                    self.assertEqual(
                        summary["authorization_status"],
                        "not-authorized",
                        f"{name}: authorization_status must be 'not-authorized'",
                    )
                if "grant_status" in summary:
                    self.assertEqual(
                        summary["grant_status"],
                        "no-grant",
                        f"{name}: grant_status must be 'no-grant'",
                    )


if __name__ == "__main__":
    unittest.main()
