"""Frame → on-device features. Raw frames are never stored or emitted.

This is the Vision-Agents ``VideoProcessor`` *pattern* (frame in, features out)
without their runtime: no WebRTC, no cloud edge, no streaming frames off-box.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol

from somatic.sensors.field import KNOWN_JOINTS

VIDEO_PROCESSOR_SCHEMA = "somatic.sensors.video_processor.v1"
POSE_ORIGIN = "mediapipe-pose"
FORBIDDEN_FRAME_KEYS = frozenset(
    {
        "frame",
        "frames",
        "raw_frame",
        "raw_frames",
        "pixels",
        "bgr",
        "rgb",
        "bgr_frame",
        "rgb_frame",
        "image",
        "ndarray",
        "jpeg",
        "png",
        "camera_buffer",
    }
)


class PoseExtractor(Protocol):
    """On-device pose backend. Implementations must drop the frame after use."""

    def extract(self, frame: object) -> dict[str, Any]: ...


def frame_shape(frame: object) -> tuple[int, int]:
    """Return (height, width) without copying pixel data."""

    if frame is None:
        return (0, 0)
    shape = getattr(frame, "shape", None)
    if isinstance(shape, tuple) and len(shape) >= 2:
        try:
            return (int(shape[0]), int(shape[1]))
        except (TypeError, ValueError):
            return (0, 0)
    if isinstance(frame, (list, tuple)) and frame:
        height = len(frame)
        first = frame[0]
        width = len(first) if isinstance(first, (list, tuple)) else 0
        return (height, width)
    return (0, 0)


def strip_frame_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop any key that could carry a raw frame or pixel buffer."""

    cleaned: dict[str, Any] = {}
    for key, value in payload.items():
        name = str(key)
        if name.lower() in FORBIDDEN_FRAME_KEYS:
            continue
        cleaned[name] = value
    return cleaned


def sandbox_pose_features(*, seed: int = 0, modality: str = "video3d") -> dict[str, Any]:
    """Deterministic synthetic pose joints. No pixels, no extra imports."""

    joints = {
        "head": [0.50, 0.12, 0.18],
        "neck": [0.50, 0.22, 0.12],
        "torso": [0.50, 0.40, 0.08],
        "pelvis": [0.50, 0.58, 0.06],
        "l_shoulder": [0.38, 0.26, 0.10],
        "r_shoulder": [0.62, 0.26, 0.10],
        "l_elbow": [0.32, 0.40, 0.08],
        "r_elbow": [0.68, 0.40, 0.08],
        "l_wrist": [0.30, 0.52, 0.06],
        "r_wrist": [0.70, 0.52, 0.06],
        "l_hip": [0.44, 0.58, 0.06],
        "r_hip": [0.56, 0.58, 0.06],
        "l_knee": [0.44, 0.74, 0.04],
        "r_knee": [0.56, 0.74, 0.04],
        "l_ankle": [0.44, 0.90, 0.02],
        "r_ankle": [0.56, 0.90, 0.02],
    }
    jitter = ((seed % 7) - 3) * 0.002
    shifted = {
        name: [round(coords[0] + jitter, 4), round(coords[1], 4), round(coords[2], 4)]
        for name, coords in joints.items()
    }
    return {
        "record_type": f"sandbox-{modality}-pose-features",
        "schema": VIDEO_PROCESSOR_SCHEMA,
        "simulated": True,
        "hardware_access": False,
        "camera_opened": False,
        "frames_exported": False,
        "raw_frames_exported": False,
        "network_calls": False,
        "webrtc": False,
        "confidence": 0.42,
        "pose3d": {
            "origin": "sandbox",
            "simulated": True,
            "joints": shifted,
            "known_joints": list(KNOWN_JOINTS),
        },
        "not_a_clinical_normal": True,
    }


class VideoProcessor:
    """Frame in → on-device inference → publish features only.

    Default path is sandbox-simulated. The live path never retains ``frame``.
    """

    def __init__(
        self,
        *,
        pose_extractor: PoseExtractor | None = None,
        simulated: bool = True,
        modality: str = "video3d",
        seed: int = 0,
    ) -> None:
        self.pose_extractor = pose_extractor
        self.simulated = bool(simulated)
        self.modality = str(modality or "video3d")
        self.seed = int(seed)
        self.frames_seen = 0
        self.last_shape: tuple[int, int] = (0, 0)

    def process_frame(self, frame: object = None) -> dict[str, Any]:
        """Run on-device pose and return features. ``frame`` is not stored."""

        shape = frame_shape(frame)
        self.last_shape = shape
        self.frames_seen += 1
        if self.simulated or frame is None or self.pose_extractor is None:
            features = sandbox_pose_features(
                seed=self.seed + self.frames_seen,
                modality=self.modality,
            )
            features["frame_height"] = shape[0]
            features["frame_width"] = shape[1]
            return strip_frame_payload(features)
        extracted = dict(self.pose_extractor.extract(frame))
        del frame
        features = {
            "record_type": f"live-{self.modality}-pose-features",
            "schema": VIDEO_PROCESSOR_SCHEMA,
            "simulated": False,
            "hardware_access": False,
            "camera_opened": False,
            "frames_exported": False,
            "raw_frames_exported": False,
            "network_calls": False,
            "webrtc": False,
            "frame_height": shape[0],
            "frame_width": shape[1],
            "not_a_clinical_normal": True,
        }
        features.update(extracted)
        features["pose3d"] = _normalize_pose(features.get("pose3d"), origin=POSE_ORIGIN)
        return strip_frame_payload(features)

    def features_digest(self, features: dict[str, Any]) -> str:
        payload = strip_frame_payload(dict(features))
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _normalize_pose(pose: object, *, origin: str) -> dict[str, Any]:
    if not isinstance(pose, dict):
        pose = {}
    joints = pose.get("joints") if isinstance(pose.get("joints"), dict) else {}
    cleaned: dict[str, list[float]] = {}
    for name, coords in joints.items():
        if not isinstance(coords, (list, tuple)) or len(coords) < 2:
            continue
        try:
            numbers = [round(float(item), 4) for item in coords[:3]]
        except (TypeError, ValueError):
            continue
        while len(numbers) < 3:
            numbers.append(0.0)
        cleaned[str(name)] = numbers
    return {
        "origin": str(pose.get("origin") or origin),
        "simulated": False,
        "joints": cleaned,
        "known_joints": list(KNOWN_JOINTS),
        "visibility": pose.get("visibility") if isinstance(pose.get("visibility"), dict) else {},
    }
