"""On-device MediaPipe Pose extractor. Lazy extra; Apache-2.0.

Do not import this module from ``somatic.sensors`` package init. Callers that
need live pose import it from ``roster`` / ``live_video`` after consent checks.
"""

from __future__ import annotations

import importlib.util
from typing import Any

from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.sensors.field import KNOWN_JOINTS
from somatic.sensors.video_processor import POSE_ORIGIN, frame_shape, strip_frame_payload

# MediaPipe Pose (BlazePose) landmark indices → Field skeleton names.
# https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
LANDMARK_TO_JOINT = {
    0: "head",
    11: "l_shoulder",
    12: "r_shoulder",
    13: "l_elbow",
    14: "r_elbow",
    15: "l_wrist",
    16: "r_wrist",
    23: "l_hip",
    24: "r_hip",
    25: "l_knee",
    26: "r_knee",
    27: "l_ankle",
    28: "r_ankle",
}


def mediapipe_available() -> bool:
    try:
        return importlib.util.find_spec("mediapipe") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def opencv_available() -> bool:
    try:
        return importlib.util.find_spec("cv2") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def video_extra_status() -> dict[str, Any]:
    mp_ok = mediapipe_available()
    cv_ok = opencv_available()
    return {
        "schema": "somatic.sensors.video_pose.extra.v1",
        "extra": "video",
        "mediapipe": mp_ok,
        "opencv": cv_ok,
        "available": mp_ok,
        "runtime_enabled": False,
        "disabled_by_default": True,
        "license": "Apache-2.0",
        "copyleft_pose_backend": False,
        "webrtc": False,
        "cloud": False,
    }


def _as_xyz(item: object) -> list[float] | None:
    if isinstance(item, dict):
        try:
            return [
                round(float(item.get("x", 0.0)), 4),
                round(float(item.get("y", 0.0)), 4),
                round(float(item.get("z", 0.0)), 4),
            ]
        except (TypeError, ValueError):
            return None
    try:
        return [
            round(float(getattr(item, "x", 0.0)), 4),
            round(float(getattr(item, "y", 0.0)), 4),
            round(float(getattr(item, "z", 0.0)), 4),
        ]
    except (TypeError, ValueError):
        return None


def _visibility(item: object) -> float | None:
    for attr in ("visibility", "presence"):
        if isinstance(item, dict) and attr in item:
            try:
                return round(float(item[attr]), 4)
            except (TypeError, ValueError):
                return None
        if hasattr(item, attr):
            try:
                return round(float(getattr(item, attr)), 4)
            except (TypeError, ValueError):
                return None
    return None


def _mid(left: list[float], right: list[float]) -> list[float]:
    return [round((left[axis] + right[axis]) / 2.0, 4) for axis in range(3)]


def landmarks_to_joints(landmarks: object) -> dict[str, list[float]]:
    """Map a 33-landmark pose list to Field joint names. No MediaPipe import."""

    if landmarks is None:
        return {}
    sequence: list[object]
    if isinstance(landmarks, dict):
        sequence = list(landmarks.values())
    elif isinstance(landmarks, (list, tuple)):
        sequence = list(landmarks)
    else:
        try:
            sequence = list(landmarks)
        except TypeError:
            return {}
    joints: dict[str, list[float]] = {}
    for index, name in LANDMARK_TO_JOINT.items():
        if index >= len(sequence):
            continue
        coords = _as_xyz(sequence[index])
        if coords is not None:
            joints[name] = coords
    if "l_shoulder" in joints and "r_shoulder" in joints:
        joints["neck"] = _mid(joints["l_shoulder"], joints["r_shoulder"])
    if "l_hip" in joints and "r_hip" in joints:
        joints["pelvis"] = _mid(joints["l_hip"], joints["r_hip"])
    if "neck" in joints and "pelvis" in joints:
        joints["torso"] = _mid(joints["neck"], joints["pelvis"])
    elif "l_shoulder" in joints and "l_hip" in joints:
        joints["torso"] = _mid(joints["l_shoulder"], joints["l_hip"])
    return {name: joints[name] for name in KNOWN_JOINTS if name in joints}


def landmark_visibility(landmarks: object) -> dict[str, float]:
    if not isinstance(landmarks, (list, tuple)):
        return {}
    out: dict[str, float] = {}
    for index, name in LANDMARK_TO_JOINT.items():
        if index >= len(landmarks):
            continue
        value = _visibility(landmarks[index])
        if value is not None:
            out[name] = value
    return out


class MediaPipePoseExtractor:
    """Lazy MediaPipe Pose. Constructing does not import the extra."""

    def __init__(self, *, use_world_landmarks: bool = True) -> None:
        self.use_world_landmarks = bool(use_world_landmarks)
        self._pose = None

    def _load(self) -> Any:
        if self._pose is not None:
            return self._pose
        if not mediapipe_available():
            raise SensorHardwareDisabled(
                "MediaPipe Pose needs the video extra (mediapipe); live pose stays off"
            )
        try:
            import mediapipe as mp
        except ImportError as exc:
            raise SensorHardwareDisabled(
                "MediaPipe Pose needs the video extra (mediapipe); live pose stays off"
            ) from exc
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=0,
            enable_segmentation=False,
        )
        return self._pose

    def extract(self, frame: object) -> dict[str, Any]:
        pose = self._load()
        rgb = _as_rgb_array(frame)
        result = pose.process(rgb)
        del frame
        del rgb
        landmarks = None
        if result is not None:
            if self.use_world_landmarks and getattr(result, "pose_world_landmarks", None):
                landmarks = result.pose_world_landmarks.landmark
            elif getattr(result, "pose_landmarks", None):
                landmarks = result.pose_landmarks.landmark
        joints = landmarks_to_joints(landmarks)
        return strip_frame_payload(
            {
                "confidence": 0.6 if joints else 0.0,
                "pose3d": {
                    "origin": POSE_ORIGIN,
                    "simulated": False,
                    "joints": joints,
                    "known_joints": list(KNOWN_JOINTS),
                    "visibility": landmark_visibility(landmarks),
                },
            }
        )

    def close(self) -> None:
        if self._pose is not None:
            closer = getattr(self._pose, "close", None)
            if callable(closer):
                closer()
        self._pose = None


def _as_rgb_array(frame: object) -> Any:
    """Convert an in-memory frame to RGB for MediaPipe. Never writes the frame."""

    if not opencv_available():
        array_type = getattr(frame, "ndim", None)
        if array_type is not None:
            return frame
        raise SensorHardwareDisabled(
            "camera-frame conversion needs the video extra (opencv-python)"
        )
    import cv2
    import numpy as np

    if isinstance(frame, np.ndarray):
        if frame.ndim == 3 and frame.shape[2] == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    height, width = frame_shape(frame)
    if height < 1 or width < 1:
        raise SensorHardwareDisabled("pose extractor received an empty frame")
    array = np.asarray(frame, dtype=np.uint8)
    if array.ndim == 3 and array.shape[2] == 3:
        return cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    return array
