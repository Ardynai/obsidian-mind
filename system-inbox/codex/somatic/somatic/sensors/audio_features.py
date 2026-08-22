"""Stdlib audio-biomarker feature derivation. Raw PCM never leaves this module.

Audio arrives as in-memory mono samples. Callers receive derived features only:
an RMS frame envelope, speech-activity ratio, speech-envelope statistics, a
heuristic cough-event count, and a breathing-style band estimate. Samples,
WAV bytes, and any waveform representation are dropped before anything is
returned or stored. Optional librosa / transformers enhancements stay in the
``audio`` extra and are never imported here.

Heuristics are research signals, not clinical measurements.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from somatic.sensors.live_features import breathing_rate_per_min

MAX_SAMPLES = 32_000 * 600
FRAME_SECONDS = 0.032
HOP_SECONDS = 0.010
MAX_ENVELOPE_POINTS = 512
MAX_COUGH_EVENTS = 32


def _as_floats(values: Sequence[object]) -> list[float]:
    out: list[float] = []
    for item in list(values)[:MAX_SAMPLES]:
        try:
            number = float(item)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            out.append(max(-1.0, min(1.0, number)))
    return out


def frame_envelope(samples: Sequence[float], sample_hz: float) -> tuple[list[float], float]:
    """RMS per 10 ms hop over 32 ms windows. Returns (envelope, frame_hz).

    Long envelopes are decimated to :data:`MAX_ENVELOPE_POINTS` points.
    """

    if not samples or sample_hz <= 0:
        return [], 0.0
    frame_len = max(1, int(round(FRAME_SECONDS * sample_hz)))
    hop_len = max(1, int(round(HOP_SECONDS * sample_hz)))
    envelope: list[float] = []
    for start in range(0, max(0, len(samples) - frame_len + 1), hop_len):
        window = samples[start : start + frame_len]
        acc = sum(item * item for item in window)
        envelope.append(math.sqrt(acc / len(window)))
    if len(envelope) > MAX_ENVELOPE_POINTS:
        step = len(envelope) / MAX_ENVELOPE_POINTS
        decimated = [envelope[int(index * step)] for index in range(MAX_ENVELOPE_POINTS)]
        envelope = decimated
        frame_hz = round(MAX_ENVELOPE_POINTS / (len(samples) / sample_hz), 4)
    else:
        frame_hz = round(1.0 / HOP_SECONDS, 4)
    return [round(item, 6) for item in envelope], min(frame_hz, 100.0)


def zero_crossing_rate(samples: Sequence[float]) -> float:
    if len(samples) < 2:
        return 0.0
    crossings = 0
    for index in range(1, len(samples)):
        if (samples[index - 1] <= 0.0 < samples[index]) or (
            samples[index] <= 0.0 < samples[index - 1]
        ):
            crossings += 1
    return round(crossings / (len(samples) - 1), 4)


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def speech_activity_ratio(envelope: Sequence[float]) -> float:
    """Fraction of frames above an adaptive floor. Heuristic, not VAD-grade."""

    if not envelope:
        return 0.0
    threshold = max(0.012, 2.5 * _median(envelope))
    active = sum(1 for item in envelope if item >= threshold)
    return round(active / len(envelope), 4)


def detect_cough_events(envelope: Sequence[float], frame_hz: float) -> list[dict[str, object]]:
    """Heuristic transient-burst detector. Research signal, not a diagnosis."""

    if not envelope or frame_hz <= 0 or len(envelope) < 4:
        return []
    floor = max(0.06, 4.0 * _median(envelope))
    min_run = max(1, int(0.04 * frame_hz))
    max_run = max(min_run + 1, int(0.60 * frame_hz))
    events: list[dict[str, object]] = []
    run_start: int | None = None
    for index, value in enumerate(envelope + [0.0]):
        above = value >= floor
        if above and run_start is None:
            run_start = index
            continue
        if not above and run_start is not None:
            length = index - run_start
            if min_run <= length <= max_run:
                peak = max(envelope[run_start:index])
                events.append(
                    {
                        "t_start_s": round(run_start / frame_hz, 3),
                        "duration_s": round(length / frame_hz, 3),
                        "peak_rms": round(float(peak), 6),
                    }
                )
            run_start = None
    return events[:MAX_COUGH_EVENTS]


def derive_audio_features(
    *,
    samples: Sequence[object],
    sample_hz: float,
    timestamp: float | None = None,
    unit_id: str = "",
) -> dict[str, object]:
    """Derive biomarker-style features from mono PCM. Drops the samples."""

    pcm = _as_floats(samples)
    rate = float(sample_hz) if sample_hz and sample_hz > 0 else 0.0
    envelope, frame_hz = frame_envelope(pcm, rate)
    stats = envelope_stats_local(envelope)
    coughs = detect_cough_events(envelope, frame_hz) if frame_hz else []
    breathing = breathing_rate_per_min(envelope, sample_hz=frame_hz) if frame_hz else 0.0
    duration = round(len(pcm) / rate, 3) if rate else 0.0
    activity = speech_activity_ratio(envelope)
    return {
        "record_type": "live-audio-features",
        "simulated": False,
        "hardware_access": False,
        "hardware_validation": (
            "sandbox-verified; needs a real microphone/WAV source to validate live"
        ),
        "unit_id": str(unit_id or ""),
        "timestamp": timestamp,
        "sample_hz": rate,
        "duration_seconds": duration,
        "envelope": envelope,
        "zero_crossing_rate": zero_crossing_rate(pcm),
        "speech_activity_ratio": activity,
        "speech_envelope_mean": stats["mean"],
        "speech_envelope_std": stats["std"],
        "cough_event_count": len(coughs),
        "cough_events": coughs,
        "breathing_rate_per_min": breathing,
        "confidence": 0.4 if activity >= 0.05 else 0.2,
        "not_a_clinical_normal": True,
        "raw_audio_exported": False,
        "pcm_exported": False,
        "transcript_omitted": True,
    }


def envelope_stats_local(envelope: Sequence[float]) -> dict[str, float]:
    if not envelope:
        return {"mean": 0.0, "std": 0.0}
    mean = sum(envelope) / len(envelope)
    variance = sum((item - mean) ** 2 for item in envelope) / len(envelope)
    return {"mean": round(mean, 6), "std": round(math.sqrt(variance), 6)}
