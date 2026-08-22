"""Live audio-biomarker lane: gating, features-only persistence, adapter."""

from __future__ import annotations

import io
import json
import math
import os
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from somatic.consent import ANALYSIS_INSIGHT, DATA_INGESTION, ConsentLedger
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.safety.core import ConsentRequiredError
from somatic.sensors.audio_features import derive_audio_features
from somatic.sensors.live_audio import (
    AudioBiomarkerIngest,
    LiveAudioAdapter,
    erase_audio_features,
    load_audio_features,
    require_live_audio,
    wav_bytes_to_samples,
)
from somatic.sensors.roster import scan_sensor


def _isolate():
    tmp = tempfile.TemporaryDirectory()
    keys = (
        "SOMATIC_SENSOR_LIVE_PATH",
        "SOMATIC_AUDIO_FEATURES_PATH",
        "SOMATIC_AUDIO_MODEL_ENABLED",
    )
    previous = {key: os.environ.get(key) for key in keys}

    def restore() -> None:
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    os.environ["SOMATIC_SENSOR_LIVE_PATH"] = str(Path(tmp.name) / "sensor-live.json")
    os.environ["SOMATIC_AUDIO_FEATURES_PATH"] = str(Path(tmp.name) / "audio-features.json")
    os.environ.pop("SOMATIC_AUDIO_MODEL_ENABLED", None)
    return restore


def _pcm_clip(sample_hz: int = 16_000) -> list[float]:
    clip: list[float] = []
    for index in range(int(sample_hz * 2.0)):
        t = index / sample_hz
        clip.append(0.05 * math.sin(2 * math.pi * 180.0 * t))
    burst_start = int(sample_hz * 1.0)
    for offset in range(int(sample_hz * 0.08)):
        clip[burst_start + offset] += 0.9 * math.sin(
            2 * math.pi * 700.0 * ((burst_start + offset) / sample_hz)
        )
    return clip


def _wav_bytes(samples: list[float], sample_hz: int = 16_000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_hz)
        frames = b"".join(
            struct.pack("<h", max(-32768, min(32767, int(item * 32767)))) for item in samples
        )
        handle.writeframes(frames)
    return buffer.getvalue()


def _granted_ledger() -> ConsentLedger:
    ledger = ConsentLedger()
    ledger.grant(DATA_INGESTION)
    ledger.grant(ANALYSIS_INSIGHT)
    return ledger


def _grant_live_audio() -> None:
    from somatic.sensors.live_consent import LiveSensorConsent, save_live_consent

    live = LiveSensorConsent()
    live.grant("audio", subject_consent=True)
    save_live_consent(live)


class AudioFeatureDerivationTests(unittest.TestCase):
    def test_derive_features_from_pcm(self):
        sample_hz = 16_000
        features = derive_audio_features(samples=_pcm_clip(sample_hz), sample_hz=sample_hz)
        self.assertEqual(features["record_type"], "live-audio-features")
        self.assertFalse(features["raw_audio_exported"])
        self.assertFalse(features["pcm_exported"])
        self.assertTrue(features["transcript_omitted"])
        self.assertTrue(features["not_a_clinical_normal"])
        self.assertGreater(features["duration_seconds"], 0.0)
        envelope = features["envelope"]
        self.assertTrue(envelope)
        for forbidden in ("pcm", "samples", "waveform", "raw_audio"):
            self.assertNotIn(forbidden, features)

    def test_cough_burst_is_detected(self):
        sample_hz = 16_000
        features = derive_audio_features(samples=_pcm_clip(sample_hz), sample_hz=sample_hz)
        self.assertGreaterEqual(features["cough_event_count"], 1)

    def test_silence_yields_low_activity(self):
        features = derive_audio_features(samples=[0.0] * 16_000, sample_hz=16_000)
        self.assertEqual(features["speech_activity_ratio"], 0.0)
        self.assertEqual(features["cough_event_count"], 0)

    def test_wav_decode_drops_bytes(self):
        samples, rate = wav_bytes_to_samples(_wav_bytes(_pcm_clip()))
        self.assertEqual(rate, 16_000)
        self.assertTrue(samples)
        self.assertTrue(all(-1.0 <= item <= 1.0 for item in samples))

    def test_wav_rejects_garbage(self):
        with self.assertRaises(ValueError):
            wav_bytes_to_samples(b"not a wav file at all")


class AudioLaneGatingTests(unittest.TestCase):
    def test_live_scan_refused_without_grant(self):
        restore = _isolate()
        try:
            ledger = _granted_ledger()
            with self.assertRaises(SensorHardwareDisabled):
                scan_sensor(ledger, "audio", live=True)
        finally:
            restore()

    def test_require_live_audio_needs_both_scopes_and_grant(self):
        restore = _isolate()
        try:
            with self.assertRaises(ConsentRequiredError):
                require_live_audio(ConsentLedger())
            _grant_live_audio()
            from somatic.sensors.live_consent import load_live_consent

            live = load_live_consent()
            self.assertTrue(live.is_granted("audio"))
            self.assertTrue(live.subject_consent("audio"))
        finally:
            restore()

    def test_unknown_modality_grant_rejected(self):
        from somatic.sensors.live_consent import LIVE_SENSOR_MODALITIES, LiveSensorConsent

        self.assertNotIn("telepathy", LIVE_SENSOR_MODALITIES)
        live = LiveSensorConsent()
        with self.assertRaises(ValueError):
            live.grant("telepathy", subject_consent=True)


class AudioPersistenceTests(unittest.TestCase):
    def test_ingest_persists_features_only(self):
        restore = _isolate()
        try:
            ingest = AudioBiomarkerIngest(persist=True)
            result = ingest.ingest_wav_bytes(_wav_bytes(_pcm_clip()))
            self.assertIsNotNone(result)
            stored_path = Path(os.environ["SOMATIC_AUDIO_FEATURES_PATH"])
            raw_text = stored_path.read_text(encoding="utf-8")
            payload = json.loads(raw_text)
            self.assertEqual(payload["schema_version"], 1)
            lowered_keys = set()

            def _collect(node: object) -> None:
                if isinstance(node, dict):
                    for key, value in node.items():
                        lowered_keys.add(str(key).lower())
                        _collect(value)
                elif isinstance(node, list):
                    for item in node:
                        _collect(item)

            _collect(payload)
            for forbidden in (
                "pcm",
                "samples",
                "waveform",
                "raw_audio",
                "audio_bytes",
                "wav_bytes",
                "transcript",
            ):
                self.assertNotIn(forbidden, lowered_keys)
            frames = load_audio_features(stored_path)
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0]["record_type"], "live-audio-features")
            erase_audio_features(stored_path)
            self.assertFalse(stored_path.exists())
        finally:
            restore()

    def test_store_scrub_lists_are_cross_family_supersets(self):
        from somatic.sensors.live_audio import _clean_frame as audio_clean
        from somatic.sensors.live_store import _clean_frame as csi_clean

        dirty = {
            "pcm": [0.1],
            "raw_audio": b"x",
            "transcript": "hello",
            "iq": [1, 2],
            "raw_csi": "y",
            "samples": [3],
            "waveform": [4],
            "confidence": 0.4,
        }
        for clean in (csi_clean, audio_clean):
            out = clean(dict(dirty)) or {}
            for key in ("pcm", "raw_audio", "transcript", "iq", "raw_csi", "samples", "waveform"):
                self.assertNotIn(key, out)
            self.assertIn("confidence", out)

    def test_empty_audio_is_dropped(self):
        restore = _isolate()
        try:
            ingest = AudioBiomarkerIngest(persist=False)
            self.assertIsNone(ingest.ingest_samples([], sample_hz=16_000))
            self.assertEqual(ingest.clips_dropped, 1)
        finally:
            restore()


class AudioAdapterTests(unittest.TestCase):
    def test_plan_and_acquire_are_features_only(self):
        restore = _isolate()
        try:
            ledger = _granted_ledger()
            ingest = AudioBiomarkerIngest(persist=True)
            ingest.ingest_wav_bytes(_wav_bytes(_pcm_clip()))
            adapter = LiveAudioAdapter(ingest=ingest)
            from somatic.evidence_bus.adapter import HypothesisSpec

            hypothesis = HypothesisSpec(
                id="test-audio", statement="test biomarkers", domain="sensing"
            )
            plan = adapter.plan(hypothesis, ledger)
            source = plan.sources[0]
            self.assertEqual(source.modality, "audio")
            self.assertFalse(source.metadata["simulated"])
            self.assertFalse(source.metadata["raw_export"])
            self.assertFalse(source.metadata["raw_audio_exported"])
            raw_evidence = adapter.acquire(plan, ledger)
            self.assertEqual(len(raw_evidence), 1)
            metadata = raw_evidence[0].metadata
            self.assertFalse(metadata["raw_audio_exported"])
            self.assertIn("features", metadata)
            confidence = adapter.confidence(raw_evidence[0])
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
        finally:
            restore()

    def test_end_to_end_live_scan_with_full_grants(self):
        restore = _isolate()
        try:
            _grant_live_audio()
            seed_ingest = AudioBiomarkerIngest(persist=True)
            seed_ingest.ingest_wav_bytes(_wav_bytes(_pcm_clip()))
            report = scan_sensor(_granted_ledger(), "audio", ticks=1, live=True)
            self.assertFalse(report.emergency_triggered)
            self.assertIn("raw-audio-stripped", report.notes)
            self.assertIn("features-only", report.notes)
        finally:
            restore()


class AudioModelPlumbingTests(unittest.TestCase):
    def test_linear_resample_identity_and_rates(self):
        from somatic.sensors.audio_model import TARGET_SAMPLE_HZ, _linear_resample

        clip = [0.01 * ((i % 20) - 10) for i in range(1600)]
        self.assertEqual(_linear_resample(clip, TARGET_SAMPLE_HZ), clip)
        down = _linear_resample(clip, 32_000)
        self.assertAlmostEqual(len(down), len(clip) / 2, delta=1)
        up = _linear_resample(clip, 8_000)
        self.assertGreater(len(up), len(clip))

    def test_configured_model_env_override(self):
        from somatic.sensors import audio_model

        previous = os.environ.get(audio_model.AUDIO_MODEL_ENV)
        try:
            os.environ[audio_model.AUDIO_MODEL_ENV] = "openai/whisper-tiny.en"
            self.assertEqual(audio_model.configured_model(), "openai/whisper-tiny.en")
            os.environ[audio_model.AUDIO_MODEL_ENV] = ""
            self.assertEqual(audio_model.configured_model(), audio_model.DEFAULT_AUDIO_MODEL)
        finally:
            if previous is None:
                os.environ.pop(audio_model.AUDIO_MODEL_ENV, None)
            else:
                os.environ[audio_model.AUDIO_MODEL_ENV] = previous

    def test_use_model_error_is_flagged_not_fatal(self):
        from unittest.mock import patch

        restore = _isolate()
        try:
            ingest = AudioBiomarkerIngest(persist=False, use_model=True)
            with patch(
                "somatic.sensors.audio_model.learned_biomarker_features",
                side_effect=ValueError("no cache"),
            ):
                result = ingest.ingest_wav_bytes(_wav_bytes(_pcm_clip()))
            self.assertIsNotNone(result)
            self.assertTrue(result.get("learned_model_error"))
            self.assertNotIn("learned_embedding", result)
        finally:
            restore()

    def test_ingest_wav_file_round_trip(self):
        restore = _isolate()
        try:
            tmp = Path(tempfile.mkdtemp())
            wav_path = tmp / "clip.wav"
            wav_path.write_bytes(_wav_bytes(_pcm_clip()))
            ingest = AudioBiomarkerIngest(persist=False)
            result = ingest.ingest_wav_file(wav_path)
            self.assertIsNotNone(result)
            self.assertEqual(result["record_type"], "live-audio-features")
        finally:
            restore()

    def test_wav_width_and_channel_variants_decode(self):
        sample_hz = 8_000

        def build(width: int, channels: int) -> bytes:
            buf = io.BytesIO()
            with wave.open(buf, "wb") as handle:
                handle.setnchannels(channels)
                handle.setsampwidth(width)
                handle.setframerate(sample_hz)
                frames = b""
                for _ in range(64):
                    for _ in range(channels):
                        value = 0.5 * (2 ** (8 * width - 1))
                        frames += int(value).to_bytes(width, "little", signed=True)
                handle.writeframes(frames)
            return buf.getvalue()

        for width in (1, 2, 3, 4):
            samples, rate = wav_bytes_to_samples(build(width, 1))
            self.assertEqual(rate, sample_hz)
            self.assertEqual(len(samples), 64)
            self.assertTrue(all(-1.0 <= s <= 1.0 for s in samples))
        stereo, rate = wav_bytes_to_samples(build(2, 2))
        self.assertEqual(rate, sample_hz)
        self.assertEqual(len(stereo), 64)
        self.assertAlmostEqual(stereo[0], 0.5, delta=0.001)


class OptionalModelTests(unittest.TestCase):
    def test_learned_features_raise_cleanly_without_extra(self):
        try:
            import transformers  # noqa: F401
        except ImportError:
            from somatic.sensors.audio_model import learned_biomarker_features

            with self.assertRaises(SensorHardwareDisabled):
                learned_biomarker_features([0.0, 0.1, -0.1], 16_000)
        else:
            self.skipTest("transformers installed; offline model test skipped")

    def test_default_checkpoint_is_permissive(self):
        from somatic.sensors.audio_model import AUDIO_MODEL_LICENSES, DEFAULT_AUDIO_MODEL

        self.assertEqual(DEFAULT_AUDIO_MODEL, "openai/whisper-tiny")
        license_note = AUDIO_MODEL_LICENSES[DEFAULT_AUDIO_MODEL].lower()
        self.assertTrue("apache" in license_note or "mit" in license_note)


if __name__ == "__main__":
    unittest.main()
