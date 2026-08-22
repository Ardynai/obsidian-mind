"""Tests for the live n-of-1 experiment designer (own-baseline only)."""

from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import ANALYSIS_INSIGHT, ConsentLedger
from somatic.experiments import (
    AWAITING_FOLLOWUP,
    AWAY_FROM_BASELINE,
    INSUFFICIENT_BASELINE,
    TOWARD_BASELINE,
    evaluate_n_of_1,
    load_tags,
)
from somatic.safety.core import ConsentRequiredError

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = REPO_ROOT / "somatic" / "experiments" / "n_of_1.py"


def _packet(pairs: list[tuple[str, float]]) -> dict:
    return {
        "resting_hr": [
            {"value": value, "observed_at": stamp, "unit": "bpm", "source": "test"}
            for stamp, value in pairs
        ]
    }


def _isolate_env():
    tmp = tempfile.TemporaryDirectory()
    previous_consent = os.environ.get("SOMATIC_CONSENT_PATH")
    previous_ingest = os.environ.get("SOMATIC_INGEST_PATH")
    previous_experiment = os.environ.get("SOMATIC_EXPERIMENT_PATH")

    def restore() -> None:
        tmp.cleanup()
        if previous_consent is None:
            os.environ.pop("SOMATIC_CONSENT_PATH", None)
        else:
            os.environ["SOMATIC_CONSENT_PATH"] = previous_consent
        if previous_ingest is None:
            os.environ.pop("SOMATIC_INGEST_PATH", None)
        else:
            os.environ["SOMATIC_INGEST_PATH"] = previous_ingest
        if previous_experiment is None:
            os.environ.pop("SOMATIC_EXPERIMENT_PATH", None)
        else:
            os.environ["SOMATIC_EXPERIMENT_PATH"] = previous_experiment

    os.environ["SOMATIC_CONSENT_PATH"] = str(Path(tmp.name) / "consent.json")
    os.environ["SOMATIC_INGEST_PATH"] = str(Path(tmp.name) / "readings.json")
    os.environ["SOMATIC_EXPERIMENT_PATH"] = str(Path(tmp.name) / "experiments.json")
    return Path(tmp.name), restore


class LiveNOf1Tests(unittest.TestCase):
    def test_requires_analysis_insight_consent(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            evaluate_n_of_1(
                ledger,
                _packet([("2026-05-01T08:00:00Z", 70.0)]),
                metric="resting_hr",
                started_at="2026-05-03T00:00:00Z",
            )

    def test_insufficient_pre_tag_baseline(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = evaluate_n_of_1(
            ledger,
            _packet([("2026-05-01T08:00:00Z", 70.0)]),
            metric="resting_hr",
            started_at="2026-05-03T00:00:00Z",
        )
        self.assertEqual(report.movement, INSUFFICIENT_BASELINE)
        self.assertIn("fewer than two", report.result.summary.lower())

    def test_awaiting_followup(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = evaluate_n_of_1(
            ledger,
            _packet(
                [
                    ("2026-05-01T08:00:00Z", 70.0),
                    ("2026-05-02T08:00:00Z", 72.0),
                ]
            ),
            metric="resting_hr",
            started_at="2026-05-03T00:00:00Z",
        )
        self.assertEqual(report.movement, AWAITING_FOLLOWUP)

    def test_toward_own_baseline(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = evaluate_n_of_1(
            ledger,
            _packet(
                [
                    ("2026-05-01T08:00:00Z", 70.0),
                    ("2026-05-01T12:00:00Z", 72.0),
                    ("2026-05-02T08:00:00Z", 71.0),
                    ("2026-05-02T12:00:00Z", 69.0),
                    ("2026-05-03T08:00:00Z", 70.0),
                    ("2026-05-03T12:00:00Z", 73.0),
                    ("2026-05-04T08:00:00Z", 71.0),
                    ("2026-05-04T12:00:00Z", 70.0),
                    ("2026-05-05T08:00:00Z", 95.0),
                    ("2026-05-10T08:00:00Z", 72.0),
                ]
            ),
            metric="resting_hr",
            started_at="2026-05-05T00:00:00Z",
            name="sleep window",
        )
        self.assertEqual(report.movement, TOWARD_BASELINE)
        self.assertIn("72", report.result.summary)
        self.assertIn("not evidence that an intervention worked", report.result.summary.lower())
        self.assertGreaterEqual(report.baseline_n, 2)
        self.assertEqual(report.followup_n, 2)

    def test_away_from_own_baseline(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        report = evaluate_n_of_1(
            ledger,
            _packet(
                [
                    ("2026-05-01T08:00:00Z", 70.0),
                    ("2026-05-01T12:00:00Z", 72.0),
                    ("2026-05-02T08:00:00Z", 71.0),
                    ("2026-05-02T12:00:00Z", 69.0),
                    ("2026-05-03T08:00:00Z", 70.0),
                    ("2026-05-03T12:00:00Z", 73.0),
                    ("2026-05-05T08:00:00Z", 72.0),
                    ("2026-05-10T08:00:00Z", 95.0),
                ]
            ),
            metric="resting_hr",
            started_at="2026-05-05T00:00:00Z",
        )
        self.assertEqual(report.movement, AWAY_FROM_BASELINE)

    def test_bare_numbers_fail_loud(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        with self.assertRaises(ValueError):
            evaluate_n_of_1(
                ledger,
                {"resting_hr": [70, 72, 71, 95]},
                metric="resting_hr",
                started_at="2026-05-03T00:00:00Z",
            )

    def test_cli_evaluate_and_tag(self):
        root, restore = _isolate_env()
        try:
            packet_path = root / "packet.json"
            packet_path.write_text(
                json.dumps(
                    _packet(
                        [
                            ("2026-05-01T08:00:00Z", 70.0),
                            ("2026-05-02T08:00:00Z", 72.0),
                            ("2026-05-03T08:00:00Z", 71.0),
                            ("2026-05-06T08:00:00Z", 90.0),
                            ("2026-05-12T08:00:00Z", 73.0),
                        ]
                    )
                ),
                encoding="utf-8",
            )
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                denied = main(
                    [
                        "experiment",
                        "evaluate",
                        "--data",
                        str(packet_path),
                        "--metric",
                        "resting_hr",
                        "--started",
                        "2026-05-05T00:00:00Z",
                    ]
                )
            self.assertEqual(denied, 2)
            self.assertIn("analysis-insight consent required", err.getvalue())

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "experiment",
                        "evaluate",
                        "--data",
                        str(packet_path),
                        "--metric",
                        "resting_hr",
                        "--started",
                        "2026-05-05T00:00:00Z",
                        "--name",
                        "sleep window",
                        "--grant",
                        "analysis-insight",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("toward_baseline", out.getvalue())

            tag_err = io.StringIO()
            with contextlib.redirect_stderr(tag_err):
                tag_denied = main(
                    [
                        "experiment",
                        "tag",
                        "--name",
                        "sleep window",
                        "--metric",
                        "resting_hr",
                        "--started",
                        "2026-05-05T00:00:00Z",
                    ]
                )
            self.assertEqual(tag_denied, 2)

            tag_out = io.StringIO()
            with contextlib.redirect_stdout(tag_out):
                tag_code = main(
                    [
                        "experiment",
                        "tag",
                        "--name",
                        "sleep window",
                        "--metric",
                        "resting_hr",
                        "--started",
                        "2026-05-05T00:00:00Z",
                        "--grant",
                        "data-ingestion",
                    ]
                )
            self.assertEqual(tag_code, 0)
            self.assertEqual(len(load_tags()), 1)
        finally:
            restore()

    def test_non_utf8_tags_file_loads_empty(self):
        _root, restore = _isolate_env()
        try:
            path = Path(os.environ["SOMATIC_EXPERIMENT_PATH"])
            path.write_bytes(b"\xff\xfe not-utf8 \xa9")
            self.assertEqual(load_tags(), ())
        finally:
            restore()

    def test_no_hardcoded_medical_normals(self):
        source = ENGINE_PATH.read_text(encoding="utf-8")
        lowered = source.lower()
        for fragment in (
            "normal range",
            "population normal",
            "clinical normal",
            "who guideline",
        ):
            self.assertNotIn(fragment, lowered)
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "normal" in target.id.lower():
                        self.fail(f"unexpected normal-like constant: {target.id}")

    def test_dependencies_stay_empty(self):
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["project"]["dependencies"], [])


if __name__ == "__main__":
    unittest.main()
