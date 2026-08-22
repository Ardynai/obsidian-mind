"""Full sensor roster: sandbox-simulated by default.

Live CSI UDP ingest, on-device audio biomarkers, and on-device camera pose are
separate, default-OFF lanes (features only), each requiring an explicit
live-sensor grant with subject consent. Remaining modalities still refuse
``live=True``. Optional extras are reported but not imported by this core
module.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
from somatic.evidence_bus.adapter import HypothesisSpec
from somatic.evidence_bus.loop import EvidenceLoopReport, run_evidence_loop
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.safety.core import require_consent

SENSOR_ROSTER_MODALITIES = (
    "csi",
    "video",
    "video3d",
    "thermal",
    "audio",
    "wearable",
    "environmental",
)

_LANE_EXTRAS = (
    ("csi", "neurokit2"),
    ("video", "cv2"),
    ("video3d", "cv2"),
    ("thermal", "cv2"),
    ("audio", "librosa"),
    ("wearable", "numpy"),
    ("environmental", "numpy"),
)


@dataclass(frozen=True)
class SensorLane:
    modality: str
    extra_package: str
    extra_available: bool
    live_hardware: bool
    sandbox_default: bool
    notes: str


def extra_available(package: str) -> bool:
    try:
        return importlib.util.find_spec(package) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def list_sensor_lanes() -> tuple[SensorLane, ...]:
    lanes: list[SensorLane] = []
    for modality, package in _LANE_EXTRAS:
        if modality == "csi":
            notes = (
                "Sandbox synthesizer by default. Loopback UDP ingest exists but "
                "stays off until an explicit live-sensor grant with subject consent."
            )
        elif modality == "audio":
            notes = (
                "Sandbox synthesizer by default. On-device biomarker features "
                "(raw audio never stored or exported) stay off until an explicit "
                "live-sensor grant with subject consent."
            )
        elif modality in {"video", "video3d"}:
            notes = (
                "Sandbox synthesizer by default. On-device MediaPipe pose exists but "
                "stays off until an explicit live-sensor grant with subject consent. "
                "Raw frames are never stored or emitted."
            )
        else:
            notes = "Sandbox synthesizer only; live hardware capture is disabled."
        lanes.append(
            SensorLane(
                modality=modality,
                extra_package=package,
                extra_available=extra_available(package),
                live_hardware=False,
                sandbox_default=True,
                notes=notes,
            )
        )
    return tuple(lanes)


def scan_sensor(
    ledger: ConsentLedger,
    modality: str,
    *,
    ticks: int = 1,
    seed: int = 0,
    live: bool = False,
) -> EvidenceLoopReport:
    """Scan one roster modality. ``live=True`` is consent-gated per modality."""

    require_consent(ledger, DATA_INGESTION)
    if modality not in SENSOR_ROSTER_MODALITIES:
        raise ValueError(f"unsupported sensor modality: {modality}")
    if ticks < 1:
        raise ValueError("ticks must be >= 1")
    if live:
        return _live_scan(ledger, modality, ticks=ticks, seed=seed)
    hypothesis = HypothesisSpec(
        id=f"scan-{modality}",
        statement=f"Sandbox live-scan of {modality} over {ticks} tick(s) (simulated stream).",
        domain="sensing",
    )
    require_consent(ledger, ANALYSIS_INSIGHT)
    reports = [
        run_evidence_loop(
            ledger,
            hypothesis,
            modalities=(modality,),
            seed=seed + tick,
        )
        for tick in range(ticks)
    ]
    last = reports[-1]
    notes = last.notes + (f"ticks={ticks}", "sandbox-live-scan", "hardware-closed")
    return EvidenceLoopReport(
        hypothesis_id=last.hypothesis_id,
        steps=tuple(step for report in reports for step in report.steps),
        verdict=last.verdict,
        emergency_triggered=any(report.emergency_triggered for report in reports),
        notes=notes,
    )


def _live_scan(
    ledger: ConsentLedger,
    modality: str,
    *,
    ticks: int,
    seed: int,
) -> EvidenceLoopReport:
    if modality == "csi":
        from somatic.sensors.live_csi import LiveCsiAdapter, require_live_csi, start_ingest

        require_live_csi(ledger)
        ingest = start_ingest()
        adapter = LiveCsiAdapter(ingest=ingest)
        hypothesis = HypothesisSpec(
            id="scan-csi-live",
            statement=(
                "Loopback CSI ingest of derived motion, presence, breathing, and heatmap "
                "features. Not a body scan and not a clinical measurement."
            ),
            domain="sensing",
        )
        notes_tail = ("live-csi-udp", "features-only")
        adapters = {"csi": adapter}
    elif modality == "audio":
        from somatic.sensors.live_audio import (
            AudioBiomarkerIngest,
            LiveAudioAdapter,
            require_live_audio,
        )

        require_live_audio(ledger)
        ingest = AudioBiomarkerIngest(persist=True, use_model=_audio_model_requested())
        adapter = LiveAudioAdapter(ingest=ingest)
        hypothesis = HypothesisSpec(
            id="scan-audio-live",
            statement=(
                "On-device audio biomarkers (respiratory, cough-event, speech-envelope "
                "features; optional offline learned embedding). Raw audio is stripped "
                "in-process and never stored or exported. Not a clinical measurement."
            ),
            domain="sensing",
        )
        notes_tail = ("live-audio-on-device", "raw-audio-stripped", "features-only")
        adapters = {"audio": adapter}
    elif modality in {"video", "video3d"}:
        from somatic.sensors.live_video import (
            LiveVideoAdapter,
            require_live_video,
            start_video_ingest,
        )

        require_live_video(ledger, modality)
        ingest = start_video_ingest(modality)
        adapter = LiveVideoAdapter(modality=modality, ingest=ingest)
        hypothesis = HypothesisSpec(
            id=f"scan-{modality}-live",
            statement=(
                "On-device camera pose features from MediaPipe Pose. "
                "Raw frames are not stored. Not a clinical measurement."
            ),
            domain="sensing",
        )
        notes_tail = ("live-video-pose", "features-only")
        adapters = {modality: adapter}
    else:
        raise SensorHardwareDisabled(
            "live hardware capture is disabled; sandbox-simulated by default"
        )
    reports = [
        run_evidence_loop(
            ledger,
            hypothesis,
            modalities=(modality,),
            seed=seed + tick,
            adapters=adapters,
            simulated=False,
        )
        for tick in range(ticks)
    ]
    last = reports[-1]
    notes = last.notes + (f"ticks={ticks}",) + notes_tail
    return EvidenceLoopReport(
        hypothesis_id=last.hypothesis_id,
        steps=tuple(step for report in reports for step in report.steps),
        verdict=last.verdict,
        emergency_triggered=any(report.emergency_triggered for report in reports),
        notes=notes,
    )


def _audio_model_requested() -> bool:
    import os

    return os.environ.get("SOMATIC_AUDIO_MODEL_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "on",
        "yes",
    }
