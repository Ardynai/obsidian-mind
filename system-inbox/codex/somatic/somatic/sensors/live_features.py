"""Stdlib CSI feature derivation. Optional numpy/scipy stay extra-only.

Raw IQ / amplitude / phase vectors enter this module and never leave it.
Callers receive occupancy rows, envelope, motion, breathing, and presence.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

MAX_SUBCARRIERS = 64
ENVELOPE_HISTORY = 64


def _as_floats(values: Sequence[object], *, limit: int = MAX_SUBCARRIERS) -> list[float]:
    out: list[float] = []
    for item in list(values)[:limit]:
        try:
            number = float(item)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            out.append(number)
    return out


def occupancy_from_amp(amp: Sequence[object]) -> list[float]:
    values = [abs(item) for item in _as_floats(amp)]
    if not values:
        return []
    peak = max(values) or 1.0
    return [round(item / peak, 4) for item in values]


def occupancy_from_iq(vector: Sequence[object]) -> tuple[list[float], list[float]]:
    """Convert interleaved IQ pairs to occupancy + wrapped phase rows. Drops IQ."""

    numbers = _as_floats(vector, limit=MAX_SUBCARRIERS * 2)
    amp: list[float] = []
    phase: list[float] = []
    for index in range(0, len(numbers) - 1, 2):
        real = numbers[index]
        imag = numbers[index + 1]
        amp.append(math.hypot(real, imag))
        phase.append(math.atan2(imag, real))
    occ = occupancy_from_amp(amp)
    wrapped = [round((item + math.pi) / (2 * math.pi), 4) for item in phase[: len(occ)]]
    return occ, wrapped


def phase_row(phase: Sequence[object]) -> list[float]:
    values = _as_floats(phase)
    if not values:
        return []
    return [round(((item + math.pi) % (2 * math.pi)) / (2 * math.pi), 4) for item in values]


def motion_energy(current: Sequence[float], previous: Sequence[float] | None) -> float:
    if not current:
        return 0.0
    if not previous:
        mean = sum(current) / len(current)
        var = sum((item - mean) ** 2 for item in current) / len(current)
        return round(var, 4)
    length = min(len(current), len(previous))
    if length <= 0:
        return 0.0
    acc = sum((current[i] - previous[i]) ** 2 for i in range(length))
    return round(acc / length, 4)


def peak_rate_per_min(series: Sequence[float], sample_hz: float = 10.0) -> float:
    if len(series) < 3 or sample_hz <= 0:
        return 0.0
    peaks = 0
    for index in range(1, len(series) - 1):
        if (
            series[index] > series[index - 1]
            and series[index] >= series[index + 1]
            and series[index] > 0.2
        ):
            peaks += 1
    minutes = (len(series) / sample_hz) / 60.0
    if minutes <= 0:
        return 0.0
    return round(peaks / minutes, 2)


def breathing_rate_per_min(series: Sequence[float], sample_hz: float = 10.0) -> float:
    """Peak-count fallback. FFT band estimate if numpy is installed (optional extra)."""

    values = [float(item) for item in series]
    if len(values) < 8:
        return peak_rate_per_min(values, sample_hz)
    try:
        import numpy as np
    except ImportError:
        return peak_rate_per_min(values, sample_hz)
    centered = np.asarray(values, dtype=float)
    centered = centered - centered.mean()
    spectrum = np.abs(np.fft.rfft(centered))
    freqs = np.fft.rfftfreq(len(centered), d=1.0 / sample_hz)
    band = (freqs >= 0.1) & (freqs <= 0.7)
    if not np.any(band):
        return peak_rate_per_min(values, sample_hz)
    peak_hz = float(freqs[band][int(np.argmax(spectrum[band]))])
    return round(peak_hz * 60.0, 2)


def link_strength(rssi: object) -> float:
    try:
        value = float(rssi)
    except (TypeError, ValueError):
        return 0.0
    # Map typical CSI RSSI (-90..-30) onto 0..1 without emitting RSSI itself.
    scaled = (value + 90.0) / 60.0
    return round(max(0.0, min(1.0, scaled)), 4)


def derive_features(
    *,
    occupancy: Sequence[float],
    phase: Sequence[float] | None = None,
    envelope_history: Sequence[float] | None = None,
    previous_occupancy: Sequence[float] | None = None,
    rssi: object = None,
    unit_id: str = "",
    timestamp: float | None = None,
    sample_hz: float = 10.0,
) -> dict[str, object]:
    row = [round(float(item), 4) for item in occupancy[:MAX_SUBCARRIERS]]
    envelope_point = round(sum(row) / len(row), 4) if row else 0.0
    history = list(envelope_history or [])
    history.append(envelope_point)
    history = history[-ENVELOPE_HISTORY:]
    motion = motion_energy(row, list(previous_occupancy) if previous_occupancy else None)
    breathing = breathing_rate_per_min(history, sample_hz=sample_hz)
    presence = bool(row) and (motion >= 0.01 or envelope_point >= 0.12)
    features: dict[str, object] = {
        "record_type": "live-csi-features",
        "simulated": False,
        "hardware_access": False,
        "hardware_validation": "sandbox-verified; needs a real ESP32 to validate live",
        "unit_id": str(unit_id or ""),
        "timestamp": timestamp,
        "envelope": [round(item, 4) for item in history],
        "occupancy_row": row,
        "amp_heatmap": [row],
        "phase_heatmap": [list(phase[:MAX_SUBCARRIERS])] if phase else [],
        "breathing_rate_per_min": breathing,
        "motion_energy": motion,
        "presence": presence,
        "link_strength": link_strength(rssi),
        "confidence": 0.4 if presence else 0.2,
        "not_a_clinical_normal": True,
        "raw_csi_iq_exported": False,
        "pose3d_omitted": True,
    }
    return features
