"""Guarded live audio-biomarker lane. Consent-gated, default-OFF, features only.

Mirrors the loopback CSI lane: an explicit live-sensor grant with subject
consent plus DATA_INGESTION + ANALYSIS_INSIGHT is required before any audio is
processed. Audio arrives in memory (mono PCM samples or WAV bytes); raw audio
is stripped in-process and never written to disk or exported. Only derived
features persist, under ``SOMATIC_AUDIO_FEATURES_PATH``.

Opt-in encryption at rest via ``SOMATIC_ENCRYPT_STORES``; the default stays
plaintext under user-only file permissions (see :mod:`somatic.local_crypto`).
"""

from __future__ import annotations

import array
import hashlib
import io
import json
import os
import tempfile
import wave
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
from somatic.evidence_bus.adapter import EvidenceCost, HypothesisSpec
from somatic.evidence_bus.records import EvidenceSource, MeasurementPlan, RawEvidence
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.local_crypto import decode_store_payload, encode_store_payload, erase_store_key
from somatic.safety.core import require_consent
from somatic.sensors.audio_features import derive_audio_features
from somatic.sensors.live_store import _FORBIDDEN as _STORE_FORBIDDEN

AUDIO_FEATURES_PATH_ENV = "SOMATIC_AUDIO_FEATURES_PATH"
MAX_STORED_FRAMES = 128
MAX_WAV_BYTES = 32 * 1024 * 1024
# Superset of the shared store scrub list plus audio-specific raw keys.
_FORBIDDEN = _STORE_FORBIDDEN


def default_audio_features_path() -> Path:
    override = os.environ.get(AUDIO_FEATURES_PATH_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / ".somatic" / "audio-features.json"


def wav_bytes_to_samples(data: bytes) -> tuple[list[float], int]:
    """Decode little-endian PCM WAV bytes to mono floats. Drops the bytes.

    Multi-channel audio is averaged to mono. Raises ValueError for non-PCM or
    oversized payloads; the caller never receives the raw bytes back.
    """

    if len(data) > MAX_WAV_BYTES:
        raise ValueError("WAV payload exceeds the in-memory size cap")
    try:
        with wave.open(io.BytesIO(data), "rb") as handle:
            channels = handle.getnchannels()
            width = handle.getsampwidth()
            rate = handle.getframerate()
            raw = handle.readframes(handle.getnframes())
    except (wave.Error, EOFError) as exc:
        raise ValueError(f"unsupported WAV payload: {exc}") from exc
    if width not in (1, 2, 3, 4):
        raise ValueError("unsupported WAV sample width")
    code = {1: "b", 2: "h", 3: None, 4: "i"}[width]
    if code is None:
        values = [
            int.from_bytes(raw[index : index + 3], "little", signed=True)
            for index in range(0, len(raw) - 2, 3)
        ]
    else:
        values = array.array(code, raw).tolist()
    scale = float(2 ** (8 * width - 1))
    mono: list[float] = []
    step = max(1, channels)
    for index in range(0, len(values) - step + 1, step):
        chunk = values[index : index + step]
        mono.append(sum(chunk) / len(chunk) / scale)
    return mono, int(rate)


def _clean_frame(frame: object) -> dict[str, Any] | None:
    if not isinstance(frame, dict):
        return None
    cleaned: dict[str, Any] = {}
    for key, value in frame.items():
        name = str(key)
        if name.lower() in _FORBIDDEN:
            continue
        cleaned[name] = value
    if not cleaned:
        return None
    return cleaned


def load_audio_features(path: Path | None = None) -> tuple[dict[str, Any], ...]:
    destination = path if path is not None else default_audio_features_path()
    try:
        raw = destination.read_bytes()
    except OSError:
        return ()
    payload = decode_store_payload(raw, destination)
    if not isinstance(payload, dict):
        return ()
    if type(payload.get("schema_version")) is not int or payload.get("schema_version") != 1:
        return ()
    rows = payload.get("frames")
    if not isinstance(rows, list):
        return ()
    frames: list[dict[str, Any]] = []
    for row in rows[-MAX_STORED_FRAMES:]:
        cleaned = _clean_frame(row)
        if cleaned is not None:
            frames.append(cleaned)
    return tuple(frames)


def save_audio_features(
    frames: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    path: Path | None = None,
) -> Path:
    destination = path if path is not None else default_audio_features_path()
    cleaned = [item for item in (_clean_frame(frame) for frame in frames) if item]
    payload = {"schema_version": 1, "frames": cleaned[-MAX_STORED_FRAMES:]}
    encrypted = encode_store_payload(destination, payload, prefix=".audio-features-")
    if encrypted is not None:
        return encrypted
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=".audio-features-",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
        os.replace(tmp_name, destination)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    try:
        os.chmod(destination, 0o600)
    except OSError:
        pass
    return destination


def append_audio_features(
    frame: dict[str, Any], path: Path | None = None
) -> tuple[dict[str, Any], ...]:
    frames = list(load_audio_features(path))
    cleaned = _clean_frame(frame)
    if cleaned is not None:
        frames.append(cleaned)
    save_audio_features(frames, path)
    return tuple(frames[-MAX_STORED_FRAMES:])


def erase_audio_features(path: Path | None = None) -> None:
    destination = path if path is not None else default_audio_features_path()
    erase_store_key(destination)
    try:
        destination.unlink()
    except FileNotFoundError:
        return


class AudioBiomarkerIngest:
    """In-memory audio-to-features gate. Raw PCM is accepted and dropped."""

    def __init__(self, *, persist: bool = True, use_model: bool = False) -> None:
        self.persist = persist
        self.use_model = use_model
        self._latest: dict[str, Any] | None = None
        self.clips_accepted = 0
        self.clips_dropped = 0

    def latest(self) -> dict[str, Any] | None:
        return dict(self._latest) if self._latest else None

    def ingest_wav_bytes(self, data: bytes) -> dict[str, Any] | None:
        samples, rate = wav_bytes_to_samples(data)
        del data
        return self.ingest_samples(samples, sample_hz=rate)

    def ingest_samples(
        self, samples: Sequence[object], *, sample_hz: float
    ) -> dict[str, Any] | None:
        import time

        from somatic.sensors.audio_features import MAX_SAMPLES

        floats = [float(item) for item in list(samples)[:MAX_SAMPLES]]
        features = derive_audio_features(
            samples=floats,
            sample_hz=sample_hz,
            timestamp=time.time(),
            unit_id="microphone",
        )
        if self.use_model:
            from somatic.sensors.audio_model import (
                TARGET_SAMPLE_HZ,
                learned_biomarker_features,
            )

            window = floats[: TARGET_SAMPLE_HZ * 30]
            try:
                features.update(learned_biomarker_features(window, sample_hz))
            except SensorHardwareDisabled:
                raise
            except (ValueError, TypeError, KeyError, OSError, RuntimeError):
                features["learned_model_error"] = True
        del floats, samples
        if not features.get("duration_seconds"):
            self.clips_dropped += 1
            return None
        return self._accept(features)

    def _accept(self, features: dict[str, Any]) -> dict[str, Any]:
        persist_now = self.persist
        if persist_now:
            append_audio_features(features)
        self._latest = features
        self.clips_accepted += 1
        return dict(features)

    def ingest_wav_file(self, path: Path | str) -> dict[str, Any] | None:
        data = Path(path).read_bytes()
        return self.ingest_wav_bytes(data)


def require_live_audio(ledger: ConsentLedger) -> None:
    """DATA_INGESTION + ANALYSIS_INSIGHT + explicit live-audio grant."""

    from somatic.sensors.live_consent import load_live_consent

    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    live = load_live_consent()
    if not live.is_granted("audio") or not live.subject_consent("audio"):
        raise SensorHardwareDisabled(
            "live audio biomarkers are off by default; grant live-sensor audio "
            "with subject consent first"
        )


class LiveAudioAdapter:
    """Evidence Bus adapter for on-device audio biomarkers. Features only."""

    tier = 1
    hardware_access = False

    def __init__(self, ingest: AudioBiomarkerIngest | None = None) -> None:
        self.modality = "audio"
        self.adapter_id = "live-audio-biomarkers"
        self._ingest = ingest

    def plan(self, hypothesis: HypothesisSpec, ledger: ConsentLedger) -> MeasurementPlan:
        require_consent(ledger, ANALYSIS_INSIGHT)
        source = EvidenceSource(
            id="src-audio-live-biomarkers",
            modality="audio",
            provider_ref=self.adapter_id,
            description=(
                "On-device audio biomarkers; respiratory/cough/speech-envelope "
                "features only. Raw audio never leaves this machine."
            ),
            metadata={
                "simulated": False,
                "tier": 1,
                "hardware_access": False,
                "network_calls": False,
                "raw_export": False,
                "local_first": True,
                "raw_audio_exported": False,
            },
        )
        return MeasurementPlan(
            id=f"plan-audio-live-{hypothesis.id}",
            sources=[source],
            objective=hypothesis.statement,
            safety_profile="research-only",
            metadata={
                "simulated": False,
                "hypothesis_id": hypothesis.id,
                "domain": hypothesis.domain,
                "live_hardware": False,
                "transport": "in-memory-pcm",
            },
        )

    def acquire(self, plan: MeasurementPlan, ledger: ConsentLedger) -> tuple[RawEvidence, ...]:
        require_consent(ledger, ANALYSIS_INSIGHT)
        ingest = self._ingest
        features = ingest.latest() if ingest is not None else None
        if features is None:
            stored = load_audio_features()
            features = (
                dict(stored[-1])
                if stored
                else {
                    "record_type": "live-audio-features",
                    "simulated": False,
                    "waiting_for_audio": True,
                    "envelope": [],
                    "cough_event_count": 0,
                    "speech_activity_ratio": 0.0,
                    "breathing_rate_per_min": 0.0,
                    "hardware_validation": "sandbox-verified; needs a real source to validate live",
                    "not_a_clinical_normal": True,
                    "raw_audio_exported": False,
                    "transcript_omitted": True,
                }
            )
        digest = hashlib.sha256(
            json.dumps(features, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()
        raw = RawEvidence(
            id=f"raw-audio-live-{digest[:12]}",
            source=plan.sources[0],
            payload_ref=f"live-audio://features/{digest[:12]}",
            sha256=digest,
            metadata={
                "simulated": False,
                "offline": True,
                "hardware_access": False,
                "raw_frames_exported": False,
                "raw_audio_exported": False,
                "features": features,
                "limitations": [
                    "Derived audio-biomarker features only.",
                    "Raw PCM was never stored or exported.",
                    "Heuristic research signals; not a clinical measurement.",
                ],
            },
        )
        return (raw,)

    def cost(self, plan: MeasurementPlan) -> EvidenceCost:
        del plan
        return EvidenceCost(
            compute_units=1.1,
            privacy_risk="on-device",
            dollars=0.0,
            hardware_required=False,
        )

    def confidence(self, raw: RawEvidence) -> float:
        features = raw.metadata.get("features")
        if not isinstance(features, dict):
            return 0.2
        value = features.get("confidence")
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.3
