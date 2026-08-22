"""Tests for informational parasite Q&A (source-grounded, emergency-screened)."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import AUTONOMOUS_RESEARCH, ConsentLedger
from somatic.parasite import ROUTING_NOTE, ask_parasite
from somatic.research import HONEST_NULL
from somatic.safety.core import ConsentRequiredError

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


class ParasiteQaTests(unittest.TestCase):
    def test_requires_autonomous_research_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            ask_parasite(ledger, "parasite questions")

    def test_emergency_question_short_circuits(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = ask_parasite(
            ledger,
            "I have sudden chest pain and think it is parasites",
        )
        self.assertTrue(report.honest_null)
        self.assertEqual(report.research.result.consent_scope, "emergency-screen")
        self.assertIn("emergency", report.research.result.summary.lower())

    def test_fixture_does_not_identify_species(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = ask_parasite(ledger, "parasite identification from symptoms")
        self.assertFalse(report.honest_null)
        joined = report.research.result.summary.lower()
        self.assertIn("does not identify", joined)
        self.assertNotIn("you have", joined)
        retrieved_ids = {passage.id for passage in report.research.retrieved}
        self.assertIn("P5", retrieved_ids)
        self.assertEqual(report.routing_note, ROUTING_NOTE)

    def test_unknown_query_is_honest_null(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = ask_parasite(ledger, "zzzxqfoobar")
        self.assertTrue(report.honest_null)
        self.assertIn(HONEST_NULL.lower(), report.research.result.summary.lower())

    def test_cli_parasite_ask(self):
        restore = _isolate_consent()
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(["parasite", "ask", "--question", "parasite"])
            self.assertEqual(denied, 2)
            self.assertIn("autonomous-research consent required", err.getvalue())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "parasite",
                        "ask",
                        "--question",
                        "parasite identification from symptoms",
                        "--grant",
                        "autonomous-research",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("not identification", out.getvalue().lower())
            self.assertIn("does not identify", out.getvalue().lower())
        finally:
            restore()

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
