"""Tests for consent persistence, fail-closed loads, and the consent CLI."""

from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import (
    ANALYSIS_INSIGHT,
    CONSENT_PATH_ENV,
    CONSENT_SCOPES,
    ConsentLedger,
    load_ledger,
    save_ledger,
)
from somatic.consent.store import erase_stored_ledger


def _isolate_consent_store():
    tmp = tempfile.TemporaryDirectory()
    path = str(Path(tmp.name) / "consent.json")
    ingest_path = str(Path(tmp.name) / "readings.json")
    experiment_path = str(Path(tmp.name) / "experiments.json")
    previous = os.environ.get(CONSENT_PATH_ENV)
    previous_ingest = os.environ.get("SOMATIC_INGEST_PATH")
    previous_experiment = os.environ.get("SOMATIC_EXPERIMENT_PATH")

    def _restore() -> None:
        tmp.cleanup()
        if previous is None:
            os.environ.pop(CONSENT_PATH_ENV, None)
        else:
            os.environ[CONSENT_PATH_ENV] = previous
        if previous_ingest is None:
            os.environ.pop("SOMATIC_INGEST_PATH", None)
        else:
            os.environ["SOMATIC_INGEST_PATH"] = previous_ingest
        if previous_experiment is None:
            os.environ.pop("SOMATIC_EXPERIMENT_PATH", None)
        else:
            os.environ["SOMATIC_EXPERIMENT_PATH"] = previous_experiment

    os.environ[CONSENT_PATH_ENV] = path
    os.environ["SOMATIC_INGEST_PATH"] = ingest_path
    os.environ["SOMATIC_EXPERIMENT_PATH"] = experiment_path
    return path, _restore


class ConsentFromDictFailClosedTests(unittest.TestCase):
    def test_valid_round_trip_still_restores_grants(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        restored = ConsentLedger.from_dict(ledger.to_dict())
        self.assertTrue(restored.is_granted(ANALYSIS_INSIGHT))

    def test_unknown_schema_version_is_all_off(self):
        payload = ConsentLedger().to_dict()
        payload["schema_version"] = 2
        restored = ConsentLedger.from_dict(payload)
        self.assertEqual(restored.granted_scopes(), ())
        self.assertEqual(restored.to_dict()["events"], [])

    def test_bool_schema_version_is_all_off(self):
        payload = {"schema_version": True, "grants": {}, "events": []}
        restored = ConsentLedger.from_dict(payload)
        self.assertEqual(restored.granted_scopes(), ())

    def test_unknown_scope_does_not_partially_restore(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        payload = ledger.to_dict()
        payload["grants"]["not-a-scope"] = {
            "scope_id": "not-a-scope",
            "actor": "user",
            "granted_at": "2026-08-17T00:00:00Z",
        }
        restored = ConsentLedger.from_dict(payload)
        self.assertFalse(restored.is_granted(ANALYSIS_INSIGHT))
        self.assertEqual(restored.granted_scopes(), ())

    def test_invalid_timestamp_is_all_off(self):
        ledger = ConsentLedger()
        ledger.grant(ANALYSIS_INSIGHT)
        payload = ledger.to_dict()
        grant = payload["grants"][ANALYSIS_INSIGHT.id]
        grant["granted_at"] = "yesterday"
        restored = ConsentLedger.from_dict(payload)
        self.assertEqual(restored.granted_scopes(), ())

    def test_missing_file_loads_all_off(self):
        path, restore = _isolate_consent_store()
        try:
            self.assertFalse(Path(path).exists())
            ledger = load_ledger()
            for scope in CONSENT_SCOPES:
                self.assertFalse(ledger.is_granted(scope))
        finally:
            restore()

    def test_non_utf8_file_loads_all_off(self):
        path, restore = _isolate_consent_store()
        try:
            Path(path).write_bytes(b"\xff\xfe not-utf8 \xa9")
            ledger = load_ledger()
            self.assertEqual(ledger.granted_scopes(), ())
        finally:
            restore()

    def test_corrupt_json_loads_all_off(self):
        path, restore = _isolate_consent_store()
        try:
            Path(path).write_text("{not-json", encoding="utf-8")
            ledger = load_ledger()
            self.assertEqual(ledger.granted_scopes(), ())
        finally:
            restore()


class ConsentStoreTests(unittest.TestCase):
    def test_save_round_trip_and_owner_only_mode(self):
        path, restore = _isolate_consent_store()
        try:
            ledger = ConsentLedger()
            ledger.grant(ANALYSIS_INSIGHT)
            saved = save_ledger(ledger)
            self.assertEqual(saved, Path(path))
            restored = load_ledger()
            self.assertTrue(restored.is_granted(ANALYSIS_INSIGHT))
            if os.name != "nt":
                mode = saved.stat().st_mode
                self.assertEqual(stat.S_IMODE(mode), 0o600)
        finally:
            restore()

    def test_erase_deletes_file_and_leaves_all_off(self):
        path, restore = _isolate_consent_store()
        try:
            ledger = ConsentLedger()
            ledger.grant(ANALYSIS_INSIGHT)
            save_ledger(ledger)
            self.assertTrue(Path(path).exists())
            ledger.purge_user_data()
            erase_stored_ledger()
            self.assertFalse(Path(path).exists())
            self.assertEqual(load_ledger().granted_scopes(), ())
        finally:
            restore()


class ConsentCliTests(unittest.TestCase):
    def test_grant_status_revoke_erase(self):
        _path, restore = _isolate_consent_store()
        try:
            grant_out = io.StringIO()
            with contextlib.redirect_stdout(grant_out):
                grant_code = main(["consent", "grant", "analysis-insight"])
            self.assertEqual(grant_code, 0)
            self.assertIn("analysis-insight", grant_out.getvalue())

            status_out = io.StringIO()
            with contextlib.redirect_stdout(status_out):
                status_code = main(["consent", "status"])
            self.assertEqual(status_code, 0)
            status_text = status_out.getvalue()
            self.assertIn("analysis-insight: ON", status_text)
            self.assertIn("ai-advisory: OFF (default OFF)", status_text)

            revoke_out = io.StringIO()
            with contextlib.redirect_stdout(revoke_out):
                revoke_code = main(["consent", "revoke", "analysis-insight"])
            self.assertEqual(revoke_code, 0)
            after_revoke = load_ledger()
            self.assertFalse(after_revoke.is_granted(ANALYSIS_INSIGHT))

            erase_out = io.StringIO()
            with contextlib.redirect_stdout(erase_out):
                erase_code = main(["consent", "erase"])
            self.assertEqual(erase_code, 0)
            self.assertIn("erased", erase_out.getvalue().lower())
            self.assertEqual(load_ledger().granted_scopes(), ())
        finally:
            restore()

    def test_unknown_scope_does_not_write(self):
        path, restore = _isolate_consent_store()
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = main(["consent", "grant", "not-a-scope"])
            self.assertEqual(code, 2)
            self.assertIn("unknown consent scope", err.getvalue())
            self.assertFalse(Path(path).exists())
        finally:
            restore()

    def test_corrupt_file_erase_unlinks_without_loading(self):
        path, restore = _isolate_consent_store()
        try:
            Path(path).write_bytes(b"\xff\xfe not-utf8 \xa9")
            ingest = Path(os.environ["SOMATIC_INGEST_PATH"])
            ingest.write_bytes(b"\xff\xfe")
            experiment = Path(os.environ["SOMATIC_EXPERIMENT_PATH"])
            experiment.write_bytes(b"\xff\xfe")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(["consent", "erase"])
            self.assertEqual(code, 0)
            self.assertIn("erased", out.getvalue().lower())
            self.assertFalse(Path(path).exists())
            self.assertFalse(ingest.exists())
            self.assertFalse(experiment.exists())
        finally:
            restore()

    def test_analyze_uses_persisted_grant_without_cli_grant_flag(self):
        _path, restore = _isolate_consent_store()
        try:
            silent = io.StringIO()
            with contextlib.redirect_stdout(silent):
                self.assertEqual(main(["consent", "grant", "analysis-insight"]), 0)
            packet = {"resting_hr": 95}
            references = {
                "resting_hr": {
                    "low": 50,
                    "high": 90,
                    "unit": "bpm",
                    "source": "user-provided-clinician-note",
                }
            }
            with tempfile.TemporaryDirectory() as tmp:
                data_path = Path(tmp) / "packet.json"
                refs_path = Path(tmp) / "refs.json"
                data_path.write_text(json.dumps(packet), encoding="utf-8")
                refs_path.write_text(json.dumps(references), encoding="utf-8")
                buffer = io.StringIO()
                with contextlib.redirect_stdout(buffer):
                    code = main(
                        [
                            "analyze",
                            "--data",
                            str(data_path),
                            "--references",
                            str(refs_path),
                            "--question",
                            "How does my resting heart rate look?",
                        ]
                    )
                output = buffer.getvalue()
            self.assertEqual(code, 0)
            self.assertNotIn("granting:", output)
            self.assertIn("Somatic analyze report", output)
            self.assertIn("reference range you provided", output.lower())
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
