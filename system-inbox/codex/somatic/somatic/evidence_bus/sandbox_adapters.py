"""Tier-0 sandbox adapters for every Evidence Bus modality.

Each adapter emits deterministic synthetic *features* (never raw camera frames,
microphone PCM, CSI IQ samples, or BLE identifiers). Hardware stays closed.
"""

from __future__ import annotations

import hashlib
import json
import math
import random

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT
from somatic.evidence_bus.adapter import EvidenceCost, HypothesisSpec
from somatic.evidence_bus.records import (
    EVIDENCE_MODALITIES,
    EvidenceSource,
    MeasurementPlan,
    RawEvidence,
)
from somatic.safety.core import require_consent

_SANDBOX_LIMITATIONS = (
    "Sandbox-simulated features only.",
    "No hardware, network, camera, microphone, BLE, or WiFi capture.",
    "Not a clinical measurement and not a medical normal.",
)


class SandboxModalityAdapter:
    """One fake-backed adapter bound to a single Evidence Bus modality."""

    tier = 0
    hardware_access = False

    def __init__(self, modality: str, *, seed: int = 0) -> None:
        if modality not in EVIDENCE_MODALITIES:
            raise ValueError(f"unsupported evidence modality: {modality}")
        self.modality = modality
        self.adapter_id = f"sandbox-{modality}"
        self._seed = int(seed)

    def plan(self, hypothesis: HypothesisSpec, ledger: ConsentLedger) -> MeasurementPlan:
        require_consent(ledger, ANALYSIS_INSIGHT)
        source = EvidenceSource(
            id=f"src-{self.modality}-sandbox",
            modality=self.modality,
            provider_ref=self.adapter_id,
            description=f"Tier-0 sandbox {self.modality} adapter; hardware closed.",
            metadata={
                "simulated": True,
                "tier": 0,
                "hardware_access": False,
                "network_calls": False,
                "raw_export": False,
                "local_first": True,
            },
        )
        return MeasurementPlan(
            id=f"plan-{self.modality}-{hypothesis.id}",
            sources=[source],
            objective=hypothesis.statement,
            safety_profile="research-only",
            metadata={
                "simulated": True,
                "hypothesis_id": hypothesis.id,
                "domain": hypothesis.domain,
                "live_hardware": False,
            },
        )

    def acquire(self, plan: MeasurementPlan, ledger: ConsentLedger) -> tuple[RawEvidence, ...]:
        require_consent(ledger, ANALYSIS_INSIGHT)
        if plan.metadata.get("live_hardware"):
            raise SensorHardwareDisabled(
                "live hardware capture is disabled; sandbox-simulated by default"
            )
        payload = _features_for(self.modality, self._seed, plan.objective)
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        source = plan.sources[0]
        raw = RawEvidence(
            id=f"raw-{self.modality}-{digest[:12]}",
            source=source,
            payload_ref=f"sandbox://{self.modality}/{digest[:12]}",
            sha256=digest,
            metadata={
                "simulated": True,
                "offline": True,
                "hardware_access": False,
                "raw_frames_exported": False,
                "raw_audio_exported": False,
                "raw_csi_iq_exported": False,
                "features": payload,
                "limitations": list(_SANDBOX_LIMITATIONS),
            },
        )
        return (raw,)

    def cost(self, plan: MeasurementPlan) -> EvidenceCost:
        del plan
        weights = {
            "literature": 1.0,
            "sim": 1.2,
            "wetlab": 1.5,
            "csi": 1.1,
            "video": 1.3,
            "video3d": 1.4,
            "thermal": 1.2,
            "audio": 1.1,
            "wearable": 1.0,
            "environmental": 0.8,
        }
        return EvidenceCost(
            compute_units=weights.get(self.modality, 1.0),
            privacy_risk="local-sandbox",
            dollars=0.0,
            hardware_required=False,
        )

    def confidence(self, raw: RawEvidence) -> float:
        features = raw.metadata.get("features")
        if not isinstance(features, dict):
            return 0.0
        value = features.get("confidence")
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.4
        return max(0.0, min(1.0, parsed))


class SensorHardwareDisabled(RuntimeError):
    """Raised when a caller asks for live hardware that the core will not open."""


def sandbox_adapters(*, seed: int = 0) -> dict[str, SandboxModalityAdapter]:
    """Return a tier-0 adapter for every Evidence Bus modality."""

    return {
        modality: SandboxModalityAdapter(modality, seed=seed)
        for modality in sorted(EVIDENCE_MODALITIES)
    }


def _features_for(modality: str, seed: int, objective: str) -> dict[str, object]:
    rng = random.Random(seed + sum(ord(ch) for ch in modality))
    series = _synthetic_series(rng, freq_hz=_band_for(modality))
    rate = _peak_rate_per_min(series)
    base: dict[str, object] = {
        "record_type": f"sandbox-{modality}-features",
        "objective_echo": objective,
        "simulated": True,
        "hardware_access": False,
        "confidence": round(0.35 + (rng.random() * 0.2), 3),
        "envelope_samples": len(series),
        "sandbox_peak_rate_per_min": rate,
        "envelope": [round(item, 4) for item in series],
        "occupancy_row": [round(max(0.0, min(1.0, (item + 1.0) / 2.0)), 4) for item in series],
        "motion_energy": round(abs(rate - 12.0) / 40.0, 4),
        "presence": True,
        "not_a_clinical_normal": True,
    }
    extras = {
        "literature": {"fixture_passages": 2, "live_http": False},
        "sim": {"affinity_placeholder": round(0.4 + rng.random() * 0.1, 3)},
        "wetlab": {"real_wetlab_action_performed": False},
        "csi": {"sandbox_respiratory_envelope": True, "pose3d": _pose(rng, "csi")},
        "video": {"sandbox_rppg_envelope": True, "frames_exported": False},
        "video3d": {"pose3d": _pose(rng, "depth"), "depth_frames_exported": False},
        "thermal": {"sandbox_mean_temp_c": round(32.0 + rng.random(), 2)},
        "audio": {"sandbox_event_count": int(rng.random() * 3), "pcm_exported": False},
        "wearable": {"sandbox_hr": round(60 + rng.random() * 20, 1), "ble_opened": False},
        "environmental": {
            "sandbox_co2_ppm": round(420 + rng.random() * 80, 1),
            "sandbox_humidity_pct": round(40 + rng.random() * 20, 1),
        },
    }
    base.update(extras.get(modality, {}))
    return base


def _band_for(modality: str) -> float:
    bands = {
        "csi": 0.25,
        "video": 1.2,
        "video3d": 0.3,
        "thermal": 0.2,
        "audio": 2.0,
        "wearable": 1.15,
        "environmental": 0.05,
        "sim": 0.4,
        "wetlab": 0.1,
        "literature": 0.01,
    }
    return bands.get(modality, 0.2)


def _synthetic_series(
    rng: random.Random, *, freq_hz: float, length: int = 64, sample_hz: float = 10.0
) -> tuple[float, ...]:
    series: list[float] = []
    for index in range(length):
        t = index / sample_hz
        noise = (rng.random() - 0.5) * 0.08
        series.append(math.sin(2 * math.pi * freq_hz * t) + noise)
    return tuple(series)


def _peak_rate_per_min(series: tuple[float, ...], sample_hz: float = 10.0) -> float:
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


def _pose(rng: random.Random, origin: str) -> dict[str, object]:
    return {
        "origin": origin,
        "simulated": True,
        "joints": {
            "head": [
                round(rng.random(), 3),
                round(rng.random(), 3),
                round(0.1 + rng.random() * 0.2, 3),
            ],
            "torso": [round(rng.random(), 3), round(rng.random(), 3), round(rng.random() * 0.1, 3)],
        },
    }
