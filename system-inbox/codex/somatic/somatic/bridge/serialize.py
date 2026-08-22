"""JSON helpers for bridge responses. Sensor payloads stay features-only."""

from __future__ import annotations

from typing import Any

from somatic.evidence_bus.loop import EvidenceLoopReport, EvidenceStep
from somatic.science.harness import ScienceHarnessReport

# Keys that must never appear on sensor/feature API responses.
RAW_SENSOR_KEYS = frozenset(
    {
        "raw_values",
        "samples",
        "imag",
        "amplitude",
        "phase",
        "rssi",
        "pcm",
        "frames",
        "pixels",
        "bgr_frame",
        "rgb_frame",
        "waveform",
        "iq",
        "source_ids",
        "raw_frames",
        "raw_audio",
        "raw_csi",
        "csi_iq",
    }
)


def sanitize_sensor_features(payload: object) -> dict[str, Any]:
    """Return a features dict with raw-signal keys stripped."""

    if not isinstance(payload, dict):
        return {}
    cleaned: dict[str, Any] = {}
    for key, value in payload.items():
        name = str(key)
        if name.lower() in RAW_SENSOR_KEYS:
            continue
        # Keep integer counts such as envelope_samples; strip list-valued raw series.
        if name.lower().endswith("_samples") and isinstance(value, list):
            continue
        cleaned[name] = value
    return cleaned


def evidence_step_to_dict(step: EvidenceStep) -> dict[str, Any]:
    return {
        "modality": step.modality,
        "raw_id": step.raw_id,
        "sha256": step.sha256,
        "confidence": step.confidence,
        "cost": {
            "compute_units": step.cost.compute_units,
            "privacy_risk": step.cost.privacy_risk,
            "dollars": step.cost.dollars,
            "hardware_required": step.cost.hardware_required,
        },
        "features": sanitize_sensor_features(step.features),
    }


def evidence_loop_to_dict(report: EvidenceLoopReport) -> dict[str, Any]:
    return {
        "hypothesis_id": report.hypothesis_id,
        "emergency_triggered": report.emergency_triggered,
        "notes": list(report.notes),
        "verdict": report.verdict.to_dict(),
        "steps": [evidence_step_to_dict(step) for step in report.steps],
    }


def science_report_to_dict(report: ScienceHarnessReport) -> dict[str, Any]:
    return {
        "goal": report.goal,
        "ranked_hypothesis_id": report.ranked_hypothesis_id,
        "ranked_statement": report.ranked_statement,
        "belief": report.belief,
        "next_measurement": report.next_measurement,
        "team_focus": list(report.team_focus),
        "blocked": report.blocked,
        "summary": report.summary,
        "evidence": evidence_loop_to_dict(report.evidence) if report.evidence else None,
    }
