"""Consent-gated, on-device video/video3d pose ingest. Features only.

Frames are accepted in memory, converted to pose features, then dropped.
No WebRTC, no cloud, no default camera open. Optional OpenCV capture lives
behind the ``video`` extra and stays off until an explicit start.
"""

from __future__ import annotations

import hashlib
import json
import threading
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
from somatic.evidence_bus.adapter import EvidenceCost, HypothesisSpec
from somatic.evidence_bus.records import EvidenceSource, MeasurementPlan, RawEvidence
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.safety.core import require_consent
from somatic.sensors.video_processor import (
    POSE_ORIGIN,
    PoseExtractor,
    VideoProcessor,
    strip_frame_payload,
)

LIVE_VIDEO_MODALITIES = ("video", "video3d")


class LiveVideoIngest:
    """Holds the latest *features* only. Raw frames are not retained."""

    def __init__(
        self,
        *,
        modality: str = "video3d",
        pose_extractor: PoseExtractor | None = None,
    ) -> None:
        name = str(modality or "video3d")
        if name not in LIVE_VIDEO_MODALITIES:
            raise ValueError(f"unsupported live video modality: {name}")
        self.modality = name
        self.processor = VideoProcessor(
            pose_extractor=pose_extractor,
            simulated=False,
            modality=name,
        )
        self._lock = threading.Lock()
        self._latest: dict[str, Any] | None = None
        self.frames_accepted = 0
        self.frames_dropped = 0
        self.camera_opened = False

    def accept_frame(self, frame: object) -> dict[str, Any]:
        if frame is None:
            self.frames_dropped += 1
            raise SensorHardwareDisabled("live video ingest refused an empty frame")
        if self.processor.pose_extractor is None:
            from somatic.sensors.video_pose import MediaPipePoseExtractor

            self.processor.pose_extractor = MediaPipePoseExtractor(
                use_world_landmarks=self.modality == "video3d"
            )
        features = self.processor.process_frame(frame)
        del frame
        features = strip_frame_payload(features)
        features["camera_opened"] = self.camera_opened
        with self._lock:
            self._latest = features
            self.frames_accepted += 1
        return features

    def latest(self) -> dict[str, Any] | None:
        with self._lock:
            if self._latest is None:
                return None
            return dict(self._latest)

    def waiting_features(self) -> dict[str, Any]:
        return {
            "record_type": f"live-{self.modality}-pose-features",
            "simulated": False,
            "waiting_for_frames": True,
            "hardware_access": False,
            "camera_opened": self.camera_opened,
            "frames_exported": False,
            "raw_frames_exported": False,
            "network_calls": False,
            "webrtc": False,
            "pose3d": {
                "origin": POSE_ORIGIN,
                "simulated": False,
                "joints": {},
            },
            "not_a_clinical_normal": True,
        }


_INGEST: dict[str, LiveVideoIngest] = {}
_INGEST_LOCK = threading.Lock()


def get_video_ingest(modality: str = "video3d") -> LiveVideoIngest:
    name = str(modality or "video3d")
    with _INGEST_LOCK:
        ingest = _INGEST.get(name)
        if ingest is None:
            ingest = LiveVideoIngest(modality=name)
            _INGEST[name] = ingest
        return ingest


def start_video_ingest(modality: str = "video3d") -> LiveVideoIngest:
    return get_video_ingest(modality)


def stop_video_ingest(modality: str | None = None) -> None:
    with _INGEST_LOCK:
        if modality is None:
            _INGEST.clear()
            return
        _INGEST.pop(str(modality), None)


def replace_video_ingest(ingest: LiveVideoIngest | None, *, modality: str = "video3d") -> None:
    name = str(modality or "video3d")
    with _INGEST_LOCK:
        if ingest is None:
            _INGEST.pop(name, None)
        else:
            _INGEST[name] = ingest


def open_camera_capture(index: int = 0) -> Any:
    """Lazy OpenCV capture. Never called by the default sandbox or scan path."""

    from somatic.sensors.video_pose import opencv_available

    if not opencv_available():
        raise SensorHardwareDisabled(
            "camera capture needs the video extra (opencv-python); live pose stays off"
        )
    try:
        import cv2
    except ImportError as exc:
        raise SensorHardwareDisabled(
            "camera capture needs the video extra (opencv-python); live pose stays off"
        ) from exc
    capture = cv2.VideoCapture(int(index))
    if not capture.isOpened():
        capture.release()
        raise SensorHardwareDisabled("camera device could not be opened")
    return capture


class LiveVideoAdapter:
    """Evidence Bus adapter for on-device camera pose features."""

    tier = 1
    hardware_access = False

    def __init__(
        self,
        *,
        modality: str = "video3d",
        ingest: LiveVideoIngest | None = None,
    ) -> None:
        name = str(modality or "video3d")
        if name not in LIVE_VIDEO_MODALITIES:
            raise ValueError(f"unsupported live video modality: {name}")
        self.modality = name
        self.adapter_id = f"live-{name}-pose"
        self._ingest = ingest

    def plan(self, hypothesis: HypothesisSpec, ledger: ConsentLedger) -> MeasurementPlan:
        require_consent(ledger, ANALYSIS_INSIGHT)
        source = EvidenceSource(
            id=f"src-{self.modality}-live-pose",
            modality=self.modality,
            provider_ref=self.adapter_id,
            description="On-device camera pose; derived joints only, no raw frames.",
            metadata={
                "simulated": False,
                "tier": 1,
                "hardware_access": False,
                "network_calls": False,
                "webrtc": False,
                "raw_export": False,
                "local_first": True,
            },
        )
        return MeasurementPlan(
            id=f"plan-{self.modality}-live-{hypothesis.id}",
            sources=[source],
            objective=hypothesis.statement,
            safety_profile="research-only",
            metadata={
                "simulated": False,
                "hypothesis_id": hypothesis.id,
                "domain": hypothesis.domain,
                "live_hardware": True,
                "transport": "on-device-frame",
            },
        )

    def acquire(self, plan: MeasurementPlan, ledger: ConsentLedger) -> tuple[RawEvidence, ...]:
        require_consent(ledger, ANALYSIS_INSIGHT)
        ingest = self._ingest or get_video_ingest(self.modality)
        features = ingest.latest() or ingest.waiting_features()
        features = strip_frame_payload(features)
        digest = hashlib.sha256(
            json.dumps(features, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()
        raw = RawEvidence(
            id=f"raw-{self.modality}-live-{digest[:12]}",
            source=plan.sources[0],
            payload_ref=f"live-video://pose/{digest[:12]}",
            sha256=digest,
            metadata={
                "simulated": False,
                "offline": True,
                "hardware_access": False,
                "raw_frames_exported": False,
                "raw_audio_exported": False,
                "raw_csi_iq_exported": False,
                "webrtc": False,
                "features": features,
                "limitations": [
                    "Derived pose features only.",
                    "Raw camera frames were not stored or exported.",
                    "On-device MediaPipe Pose; no cloud or WebRTC.",
                ],
            },
        )
        return (raw,)

    def cost(self, plan: MeasurementPlan) -> EvidenceCost:
        del plan
        return EvidenceCost(
            compute_units=1.3,
            privacy_risk="local-on-device",
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


def require_live_video(ledger: ConsentLedger, modality: str) -> None:
    """DATA_INGESTION + ANALYSIS_INSIGHT + per-modality live grant with subject consent."""

    from somatic.sensors.live_consent import load_live_consent

    name = str(modality)
    if name not in LIVE_VIDEO_MODALITIES:
        raise SensorHardwareDisabled(
            "live hardware capture is disabled; sandbox-simulated by default"
        )
    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    live = load_live_consent()
    if not live.is_granted(name) or not live.subject_consent(name):
        raise SensorHardwareDisabled(
            f"live {name} pose is off by default; "
            f"grant live-sensor {name} with subject consent first"
        )
