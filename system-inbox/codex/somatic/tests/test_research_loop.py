"""Tests for offline citation-bound research (honest null, no model memory)."""

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
from somatic.research import (
    HONEST_NULL,
    bind_claims,
    load_corpus,
    retrieve,
    run_research_loop,
)
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


class ResearchLoopTests(unittest.TestCase):
    def test_requires_autonomous_research_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            run_research_loop(ledger, "magnesium nutrient")

    def test_offline_miss_is_honest_null(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = run_research_loop(ledger, "zzzxqfoobar")
        self.assertTrue(report.honest_null)
        self.assertEqual(report.claims, ())
        self.assertEqual(report.result.evidence_grade, EvidenceGrade.NONE)
        self.assertIn(HONEST_NULL.lower(), report.result.summary.lower())

    def test_empty_corpus_is_honest_null(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = run_research_loop(ledger, "magnesium", corpus=())
        self.assertTrue(report.honest_null)
        self.assertEqual(report.result.summary, HONEST_NULL)

    def test_unbound_claim_is_dropped(self):
        corpus = load_corpus()
        retrieved = retrieve(corpus, "magnesium nutrient", k=3)
        bound, dropped = bind_claims(
            [
                {"text": "Unbound memory claim about a disease.", "cites": ["P99"]},
                {"text": "Claim with no citation.", "cites": []},
            ],
            retrieved,
        )
        self.assertEqual(bound, ())
        self.assertEqual(len(dropped), 2)

    def test_bound_extracts_only_cite_retrieved_ids(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = run_research_loop(
            ledger,
            "magnesium nutrient enzymatic",
            extra_claims=[{"text": "Invented claim from memory.", "cites": ["P99"]}],
        )
        self.assertFalse(report.honest_null)
        self.assertGreaterEqual(len(report.claims), 1)
        retrieved_ids = {passage.id for passage in report.retrieved}
        for claim in report.claims:
            self.assertTrue(claim.passage_ids)
            self.assertTrue(set(claim.passage_ids).issubset(retrieved_ids))
        self.assertGreaterEqual(report.dropped_unbound, 1)
        self.assertIn("P1", " ".join(claim.passage_ids[0] for claim in report.claims))
        self.assertNotIn("Invented claim from memory", report.result.summary)

    def test_bm25_ranks_magnesium_passage_first(self):
        corpus = load_corpus()
        ranked = retrieve(corpus, "magnesium enzymatic mineral", k=2)
        self.assertTrue(ranked)
        self.assertEqual(ranked[0].id, "P1")

    def test_observational_query_gets_limited_grade(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        report = run_research_loop(ledger, "sleep duration observational alertness")
        self.assertFalse(report.honest_null)
        self.assertIn(
            report.result.evidence_grade, {EvidenceGrade.LIMITED, EvidenceGrade.PRELIMINARY}
        )

    def test_cli_requires_consent_and_prints_honest_null(self):
        restore = _isolate_consent()
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(["research", "ask", "--question", "magnesium"])
            self.assertEqual(denied, 2)
            self.assertIn("autonomous-research consent required", err.getvalue())

            miss = io.StringIO()
            with contextlib.redirect_stdout(miss):
                code = main(
                    [
                        "research",
                        "ask",
                        "--question",
                        "zzzxqfoobar",
                        "--grant",
                        "autonomous-research",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("honest_null: True", miss.getvalue())
            self.assertIn(HONEST_NULL, miss.getvalue())
        finally:
            restore()

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
