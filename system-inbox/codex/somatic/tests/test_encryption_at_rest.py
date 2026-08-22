"""Opt-in encryption at rest: round-trip, erase-clears-everything, fail-closed."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from somatic.consent.ledger import ConsentLedger
from somatic.consent.store import (
    default_consent_path,
    erase_stored_ledger,
    load_ledger,
    save_ledger,
)
from somatic.experiments.store import erase_stored_tags, load_tags, save_tags
from somatic.ingest.store import erase_stored_readings, load_readings, save_readings
from somatic.local_crypto import (
    ENCRYPT_STORES_ENV,
    ENVELOPE_FORMAT,
    STORE_PASSPHRASE_ENV,
    decode_store_payload,
    encryption_enabled,
    is_envelope,
    key_path_for,
)
from somatic.sensors.live_audio import (
    default_audio_features_path,
    erase_audio_features,
    load_audio_features,
    save_audio_features,
)
from somatic.sensors.live_store import erase_csi_features, load_csi_features, save_csi_features

try:
    import cryptography  # noqa: F401

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def _isolate():
    tmp = tempfile.TemporaryDirectory()
    keys = (
        "SOMATIC_CONSENT_PATH",
        "SOMATIC_INGEST_PATH",
        "SOMATIC_EXPERIMENT_PATH",
        "SOMATIC_CSI_FEATURES_PATH",
        "SOMATIC_AUDIO_FEATURES_PATH",
        ENCRYPT_STORES_ENV,
        STORE_PASSPHRASE_ENV,
    )
    previous = {key: os.environ.get(key) for key in keys}

    def restore() -> None:
        tmp.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    base = Path(tmp.name)
    os.environ["SOMATIC_CONSENT_PATH"] = str(base / "consent.json")
    os.environ["SOMATIC_INGEST_PATH"] = str(base / "readings.json")
    os.environ["SOMATIC_EXPERIMENT_PATH"] = str(base / "experiments.json")
    os.environ["SOMATIC_CSI_FEATURES_PATH"] = str(base / "csi-features.json")
    os.environ["SOMATIC_AUDIO_FEATURES_PATH"] = str(base / "audio-features.json")
    for key in (ENCRYPT_STORES_ENV, STORE_PASSPHRASE_ENV):
        os.environ.pop(key, None)
    return restore


class FlagAndFormatTests(unittest.TestCase):
    def test_encryption_disabled_by_default(self):
        previous = os.environ.pop(ENCRYPT_STORES_ENV, None)
        try:
            self.assertFalse(encryption_enabled())
        finally:
            if previous is not None:
                os.environ[ENCRYPT_STORES_ENV] = previous

    def test_flag_parsing(self):
        for value in ("1", "true", "TRUE", "On", "yes"):
            os.environ[ENCRYPT_STORES_ENV] = value
            self.assertTrue(encryption_enabled(), value)
        for value in ("", "0", "false", "off", "no", "maybe"):
            os.environ[ENCRYPT_STORES_ENV] = value
            self.assertFalse(encryption_enabled(), value)
        os.environ.pop(ENCRYPT_STORES_ENV, None)

    def test_envelope_detection(self):
        self.assertFalse(is_envelope(b'{"schema_version": 1}'))
        self.assertFalse(is_envelope(b"not json at all"))
        envelope = {
            "format": ENVELOPE_FORMAT,
            "kdf": "scrypt",
            "salt": "00",
            "nonce": "00",
            "ciphertext": "00",
        }
        encoded = json.dumps(envelope).encode("utf-8")
        self.assertTrue(is_envelope(encoded))

    def test_decode_plaintext_passthrough(self):
        payload = {"schema_version": 1, "readings": []}
        decoded = decode_store_payload(json.dumps(payload).encode("utf-8"))
        self.assertEqual(decoded, payload)

    def test_default_writes_stay_plaintext(self):
        restore = _isolate()
        try:
            ledger = ConsentLedger()
            ledger.grant("analysis-insight")
            destination = save_ledger(ledger)
            raw_text = Path(destination).read_text(encoding="utf-8")
            self.assertIn("analysis-insight", raw_text)
            self.assertFalse(is_envelope(Path(destination).read_bytes()))
            loaded = load_ledger(destination)
            self.assertTrue(loaded.is_granted("analysis-insight"))
        finally:
            restore()

    def test_default_audio_writes_stay_plaintext(self):
        restore = _isolate()
        try:
            frame = {"record_type": "live-audio-features", "cough_event_count": 1}
            destination = save_audio_features([frame])
            raw_text = Path(destination).read_text(encoding="utf-8")
            self.assertIn("cough_event_count", raw_text)
            self.assertFalse(is_envelope(Path(destination).read_bytes()))
        finally:
            restore()


@unittest.skipUnless(CRYPTO_AVAILABLE, "cryptography extra not installed")
class EncryptedRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.restore = _isolate()
        os.environ[ENCRYPT_STORES_ENV] = "1"

    def tearDown(self):
        self.restore()

    def test_consent_ledger_round_trip_is_enrypted(self):
        ledger = ConsentLedger()
        ledger.grant("analysis-insight")
        destination = save_ledger(ledger)
        raw_text = Path(destination).read_text(encoding="utf-8")
        self.assertNotIn("analysis-insight", raw_text)
        self.assertTrue(is_envelope(Path(destination).read_bytes()))
        loaded = load_ledger(destination)
        self.assertTrue(loaded.is_granted("analysis-insight"))

    def test_readings_and_tags_round_trip(self):
        from somatic.experiments.n_of_1 import InterventionTag
        from somatic.ingest.packet import Reading

        reading = Reading(
            metric="sleep-hours",
            value=7.5,
            observed_at="2026-08-21T07:30:00Z",
        )
        saved = save_readings([reading])
        self.assertNotIn("sleep-hours", Path(saved).read_text(encoding="utf-8"))
        loaded = load_readings(saved)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].metric, "sleep-hours")

        tag = InterventionTag(
            name="caffeine-cut",
            metric="sleep-hours",
            started_at="2026-08-20T00:00:00Z",
            ended_at="",
            note="n=1 trial",
        )
        tag_path = save_tags([tag])
        self.assertNotIn("caffeine-cut", Path(tag_path).read_text(encoding="utf-8"))
        tags_loaded = load_tags(tag_path)
        self.assertEqual(len(tags_loaded), 1)
        self.assertEqual(tags_loaded[0].name, "caffeine-cut")

    def test_csi_features_round_trip(self):
        frame = {
            "record_type": "live-csi-features",
            "breathing_rate_per_min": 14.2,
            "presence": True,
        }
        saved = save_csi_features([frame])
        self.assertNotIn("breathing_rate_per_min", Path(saved).read_text(encoding="utf-8"))
        frames = load_csi_features(saved)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]["breathing_rate_per_min"], 14.2)

    def test_audio_features_round_trip(self):
        frame = {
            "record_type": "live-audio-features",
            "speech_activity_ratio": 0.31,
            "cough_event_count": 2,
        }
        saved = save_audio_features([frame])
        self.assertNotIn("speech_activity_ratio", Path(saved).read_text(encoding="utf-8"))
        self.assertTrue(is_envelope(Path(saved).read_bytes()))
        frames = load_audio_features(saved)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]["cough_event_count"], 2)

    def test_corrupt_ciphertext_fails_closed_all_off(self):
        ledger = ConsentLedger()
        ledger.grant("data-ingestion")
        destination = save_ledger(ledger)
        raw = Path(destination).read_text(encoding="utf-8")
        envelope = json.loads(raw)
        flipped = bytearray(bytes.fromhex(envelope["ciphertext"]))
        flipped[0] ^= 0xFF
        envelope["ciphertext"] = bytes(flipped).hex()
        Path(destination).write_text(json.dumps(envelope), encoding="utf-8")
        loaded = load_ledger(destination)
        self.assertEqual(len(loaded.to_dict().get("grants", {})), 0)

        readings_path = Path(os.environ["SOMATIC_INGEST_PATH"])
        readings_path.write_text("{not valid json", encoding="utf-8")
        self.assertEqual(load_readings(readings_path), ())
        tags_path = Path(os.environ["SOMATIC_EXPERIMENT_PATH"])
        tags_path.write_text('{"schema_version": 9, "tags": []}', encoding="utf-8")
        self.assertEqual(load_tags(tags_path), ())
        csi_path = Path(os.environ["SOMATIC_CSI_FEATURES_PATH"])
        csi_path.write_bytes(b"\x00\x01\x02garbage")
        self.assertEqual(load_csi_features(csi_path), ())
        audio_path = Path(os.environ["SOMATIC_AUDIO_FEATURES_PATH"])
        audio_path.write_text("{truncated envelope", encoding="utf-8")
        self.assertEqual(load_audio_features(audio_path), ())

    def test_wrong_passphrase_fails_closed(self):
        ledger = ConsentLedger()
        ledger.grant("data-ingestion")
        os.environ[STORE_PASSPHRASE_ENV] = "correct-horse"
        destination = save_ledger(ledger)
        os.environ[STORE_PASSPHRASE_ENV] = "wrong-staple"
        loaded = load_ledger(destination)
        self.assertEqual(len(loaded.to_dict().get("grants", {})), 0)

    def test_passphrase_mode_creates_no_key_file(self):
        os.environ[STORE_PASSPHRASE_ENV] = "correct-horse"
        ledger = ConsentLedger()
        destination = save_ledger(ledger)
        key_file = key_path_for(Path(destination))
        self.assertIsNotNone(key_file)
        self.assertFalse(key_file.exists())
        self.assertTrue(load_ledger(destination) is not None)

    def test_keyfile_mode_round_trip_without_passphrase(self):
        os.environ.pop(STORE_PASSPHRASE_ENV, None)
        ledger = ConsentLedger()
        ledger.grant("professional-sharing")
        destination = save_ledger(ledger)
        key_file = key_path_for(Path(destination))
        self.assertTrue(key_file.exists())
        loaded = load_ledger(destination)
        self.assertTrue(loaded.is_granted("professional-sharing"))

    def test_short_key_file_is_replaced_on_next_write(self):
        os.environ.pop(STORE_PASSPHRASE_ENV, None)
        ledger = ConsentLedger()
        destination = Path(save_ledger(ledger))
        key_file = key_path_for(destination)
        key_file.write_bytes(b"short")  # corrupt/truncated key material
        self.assertEqual(load_ledger(destination).to_dict().get("grants", {}), {})
        ledger.grant("analysis-insight")
        save_ledger(ledger, destination)
        self.assertEqual(len(key_file.read_bytes()), 32)
        self.assertTrue(load_ledger(destination).is_granted("analysis-insight"))

    def test_envelope_missing_fields_fail_closed(self):
        from somatic.local_crypto import decrypt_bytes

        material = b"somatic-passphrase:x"
        envelope = {"format": ENVELOPE_FORMAT, "kdf": "scrypt", "salt": "00", "nonce": "00"}
        self.assertIsNone(decrypt_bytes(material, envelope))
        payload = decode_store_payload(json.dumps(envelope).encode("utf-8"))
        self.assertIsNone(payload)

    def test_non_dict_json_payload_decodes_to_none(self):
        self.assertIsNone(decode_store_payload(b"[1, 2, 3]"))
        self.assertIsNone(decode_store_payload(b'"just a string"'))

    def test_erase_clears_ciphertext_and_key_material(self):
        os.environ.pop(STORE_PASSPHRASE_ENV, None)
        ledger = ConsentLedger()
        ledger.grant("data-ingestion")
        destination = Path(save_ledger(ledger))
        key_file = key_path_for(destination)
        self.assertTrue(destination.exists())
        self.assertTrue(key_file.exists())
        erase_stored_ledger(destination)
        self.assertFalse(destination.exists())
        self.assertFalse(key_file.exists())

        from somatic.ingest.packet import Reading

        readings_destination = Path(os.environ["SOMATIC_INGEST_PATH"])
        save_readings([Reading(metric="m", value=1.0, observed_at="2026-08-21T00:00:00Z")])
        readings_key = key_path_for(readings_destination)
        erase_stored_readings(readings_destination)
        self.assertFalse(readings_destination.exists())
        self.assertFalse(readings_key.exists())

        tags_destination = Path(os.environ["SOMATIC_EXPERIMENT_PATH"])
        save_tags([])
        tags_key = key_path_for(tags_destination)
        erase_stored_tags(tags_destination)
        self.assertFalse(tags_destination.exists())
        self.assertFalse(tags_key.exists())

        csi_destination = Path(os.environ["SOMATIC_CSI_FEATURES_PATH"])
        save_csi_features([])
        csi_key = key_path_for(csi_destination)
        erase_csi_features(csi_destination)
        self.assertFalse(csi_destination.exists())
        self.assertFalse(csi_key.exists())

        audio_destination = Path(os.environ["SOMATIC_AUDIO_FEATURES_PATH"])
        save_audio_features([])
        audio_key = key_path_for(audio_destination)
        erase_audio_features(audio_destination)
        self.assertFalse(audio_destination.exists())
        self.assertFalse(audio_key.exists())
        self.assertEqual(default_audio_features_path(), audio_destination)
        self.assertEqual(default_consent_path(), Path(os.environ["SOMATIC_CONSENT_PATH"]))


if __name__ == "__main__":
    unittest.main()
