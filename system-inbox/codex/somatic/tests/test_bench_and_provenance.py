"""Sandbox bench + content-addressed evidence verify."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from somatic.bench import run_bench
from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, AUTONOMOUS_RESEARCH, ConsentLedger
from somatic.provenance.cas import address_record, verify_file, verify_record

REPO_ROOT = Path(__file__).resolve().parents[1]


def _isolate():
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


class BenchAndProvenanceTests(unittest.TestCase):
    def test_ripasudil_sandbox_bench_scores(self):
        ledger = ConsentLedger()
        ledger.grant(AUTONOMOUS_RESEARCH)
        ledger.grant(ANALYSIS_INSIGHT)
        score = run_bench(ledger, seed=1)
        self.assertEqual(score.task_id, "ripasudil-damd-sandbox")
        self.assertTrue(score.reproducible)
        self.assertEqual(score.leaderboard["dollars_spent"], 0)
        self.assertFalse(score.leaderboard["hardware_used"])
        self.assertTrue(score.passed)
        self.assertTrue(score.final_answer_ok)

    def test_address_and_verify_round_trip(self):
        record = address_record({"kind": "sandbox-evidence", "simulated": True})
        self.assertEqual(len(record["content_id"]), 64)
        self.assertTrue(verify_record(record)["ok"])
        broken = dict(record)
        broken["kind"] = "tampered"
        self.assertFalse(verify_record(broken)["ok"])

    def test_cli_bench_and_verify(self):
        restore = _isolate()
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "bench-run",
                        "--grant",
                        "autonomous-research,analysis-insight",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("ripasudil-damd-sandbox", out.getvalue())
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "evidence.json"
                payload = address_record({"kind": "sandbox", "n": 1})
                path.write_text(json.dumps(payload), encoding="utf-8")
                verify_out = io.StringIO()
                with contextlib.redirect_stdout(verify_out):
                    verify_code = main(["evidence-verify", "--file", str(path)])
                self.assertEqual(verify_code, 0)
                self.assertTrue(json.loads(path.read_text(encoding="utf-8")))
                self.assertIn('"ok": true', verify_out.getvalue())
                self.assertTrue(verify_file(path)["ok"])
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
