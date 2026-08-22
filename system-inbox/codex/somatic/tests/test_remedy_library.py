"""Tests for the evidence-graded informational remedy library."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import REMEDY_LIBRARY, ConsentLedger
from somatic.remedy import lookup_remedy
from somatic.research import HONEST_NULL
from somatic.safety.core import ConsentRequiredError, EvidenceGrade

REPO_ROOT = Path(__file__).resolve().parents[1]


def _isolate_consent():
    tmp = tempfile.TemporaryDirectory()
    previous = os.environ.get("SOMATIC_CONSENT_PATH")

    def restore() -> None:
        tmp.cleanup()
        if previous is None:
            os.environ.pop("SOMATIC_CONSENT_PATH", None)
        else:
            os.environ["SOMATIC_CONSENT_PATH"] = previous

    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    return restore


class RemedyLibraryTests(unittest.TestCase):
    def test_requires_remedy_library_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            lookup_remedy(ledger, "magnesium")

    def test_unknown_topic_is_honest_null_none_grade(self):
        ledger = ConsentLedger()
        ledger.grant(REMEDY_LIBRARY)
        report = lookup_remedy(ledger, "zzzxqfoobar")
        self.assertTrue(report.honest_null)
        self.assertEqual(len(report.entries), 1)
        self.assertEqual(report.entries[0].evidence_grade, EvidenceGrade.NONE)
        self.assertEqual(report.entries[0].claim, HONEST_NULL)
        self.assertEqual(report.entries[0].citations, ())

    def test_bound_entry_never_exceeds_limited_and_cites_passages(self):
        ledger = ConsentLedger()
        ledger.grant(REMEDY_LIBRARY)
        report = lookup_remedy(ledger, "magnesium nutrient enzymatic")
        self.assertFalse(report.honest_null)
        self.assertTrue(report.entries)
        for entry in report.entries:
            self.assertIn(
                entry.evidence_grade,
                {
                    EvidenceGrade.NONE,
                    EvidenceGrade.PRELIMINARY,
                    EvidenceGrade.LIMITED,
                },
            )
            self.assertNotEqual(entry.evidence_grade, EvidenceGrade.STRONG)
            self.assertTrue(entry.citations)
            self.assertTrue(entry.safety_notes)

    def test_cli_lookup(self):
        restore = _isolate_consent()
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(["remedy", "lookup", "--query", "magnesium"])
            self.assertEqual(denied, 2)
            self.assertIn("remedy-library consent required", err.getvalue())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "remedy",
                        "lookup",
                        "--query",
                        "zzzxqfoobar",
                        "--grant",
                        "remedy-library",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn(HONEST_NULL, out.getvalue())
            self.assertIn("evidence_grade: none", out.getvalue())
        finally:
            restore()

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
