"""Optional learned audio biomarkers via ``transformers[torch]``. Extra-only.

Never imported by package import and never required: callers get a clear
:class:`~somatic.evidence_bus.sandbox_adapters.SensorHardwareDisabled` when the
optional extra is missing. Inference is forced offline — ``HF_HUB_OFFLINE`` and
``TRANSFORMERS_OFFLINE`` are set before transformers is imported — so the
pre-cached checkpoint can never fetch at run time and no audio or features
leave the machine.

Default checkpoint: ``openai/whisper-tiny`` (Hugging Face checkpoint under
Apache-2.0; upstream Whisper code MIT). Override with ``SOMATIC_AUDIO_MODEL``
only with another permissively-licensed checkpoint you have verified and
pre-cached. Output is a mean-pooled encoder embedding — features only; no
transcript is produced or exported.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled

DEFAULT_AUDIO_MODEL = "openai/whisper-tiny"
AUDIO_MODEL_ENV = "SOMATIC_AUDIO_MODEL"
TARGET_SAMPLE_HZ = 16_000
MAX_EMBEDDING_DIMS = 64
AUDIO_MODEL_LICENSES = {
    "openai/whisper-tiny": "apache-2.0 (HF checkpoint); MIT (upstream openai/whisper code)",
    "openai/whisper-tiny.en": "apache-2.0 (HF checkpoint); MIT (upstream openai/whisper code)",
}


def configured_model() -> str:
    override = os.environ.get(AUDIO_MODEL_ENV, "").strip()
    return override or DEFAULT_AUDIO_MODEL


def _linear_resample(samples: Sequence[float], sample_hz: float) -> list[float]:
    if sample_hz <= 0 or not samples:
        return []
    if abs(sample_hz - TARGET_SAMPLE_HZ) < 1e-6:
        return list(samples)
    ratio = sample_hz / TARGET_SAMPLE_HZ
    out_len = int(len(samples) / ratio)
    out: list[float] = []
    for index in range(out_len):
        position = index * ratio
        low = int(position)
        high = min(low + 1, len(samples) - 1)
        fraction = position - low
        out.append(samples[low] * (1.0 - fraction) + samples[high] * fraction)
    return out


def learned_biomarker_features(samples: Sequence[float], sample_hz: float) -> dict[str, Any]:
    """Mean-pooled encoder embedding via the pre-cached offline checkpoint."""

    model_id = configured_model()
    try:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        import torch
        import transformers
    except ImportError as exc:
        raise SensorHardwareDisabled(
            "learned audio biomarkers need the audio extra "
            "(pip install 'somatic[audio]') with the model pre-cached offline"
        ) from exc
    try:
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
    except ImportError as exc:
        raise SensorHardwareDisabled(
            f"transformers is missing the speech seq2seq classes needed for checkpoint {model_id}"
        ) from exc

    resampled = _linear_resample(list(samples), float(sample_hz))
    if not resampled:
        raise ValueError("audio samples are empty")
    del transformers
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
    model.eval()
    inputs = processor(
        resampled, sampling_rate=TARGET_SAMPLE_HZ, return_tensors="pt"
    ).input_features
    with torch.no_grad():
        encoder = model.get_encoder()(inputs.float())
    hidden = encoder.last_hidden_state.squeeze(0).mean(dim=0).tolist()
    embedding = [round(float(value), 6) for value in hidden[:MAX_EMBEDDING_DIMS]]
    return {
        "record_type": "live-audio-learned-features",
        "learned_model": model_id,
        "model_license": AUDIO_MODEL_LICENSES.get(model_id, "unverified-checkpoint"),
        "offline_forced": True,
        "embedding_dim": len(embedding),
        "learned_embedding": embedding,
        "transcript_exported": False,
        "raw_audio_exported": False,
        "simulated": False,
    }
