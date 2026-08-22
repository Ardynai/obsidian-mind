"""Render-only avatar: does not alter the verdict; TTS/head stay off."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from somatic.cli import main
from somatic.consent import AI_ADVISORY, ConsentLedger
from somatic.presence import REASONING_PATH_PARTICIPANT, RENDER_ONLY, render_presence
from somatic.safety.core import INFORMATIONAL_NOTICE, ConsentRequiredError


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


class PresenceAvatarTests(unittest.TestCase):
    def test_presence_is_render_only(self):
        self.assertTrue(RENDER_ONLY)
        self.assertFalse(REASONING_PATH_PARTICIPANT)

    def test_requires_ai_advisory(self):
        ledger = ConsentLedger()
        with self.assertRaises(ConsentRequiredError):
            render_presence(ledger, "sandbox observation of sleep duration")

    def test_doctor_keeps_verdict_and_disclaimer(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        verdict = "Your data suggests sleep duration may relate to next-day energy."
        rendered = render_presence(ledger, verdict, persona="doctor")
        self.assertTrue(rendered.verdict_unchanged)
        self.assertIn(verdict, rendered.speech)
        self.assertIn(INFORMATIONAL_NOTICE, rendered.speech)
        self.assertEqual(rendered.tts_runtime, "disabled")
        self.assertEqual(rendered.talking_head_runtime, "disabled")
        self.assertFalse(rendered.camera_registered)
        self.assertFalse(rendered.microphone_registered)

    def test_emergency_verdict_is_not_rephrased_into_advice(self):
        ledger = ConsentLedger()
        ledger.grant(AI_ADVISORY)
        rendered = render_presence(ledger, "Sudden chest pain while resting")
        self.assertIn("emergency", rendered.speech.lower())

    def test_cli_avatar_speak(self):
        restore = _isolate()
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "avatar",
                        "speak",
                        "--persona",
                        "scientist",
                        "--verdict",
                        "Sandbox evidence was simulated and hashed.",
                        "--grant",
                        "ai-advisory",
                    ]
                )
            self.assertEqual(code, 0)
            text = out.getvalue()
            self.assertIn("render-only", text.lower())
            self.assertIn("verdict_unchanged: True", text)
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
