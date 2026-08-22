"""Consent-gated AI advisory adapter package."""

from .adapter import (
    AdvisoryConfigError,
    AdvisoryHttpError,
    AdvisoryModelClient,
    AdvisoryModelConfig,
)
from .models import (
    ADVISORY_MODEL_OPTIONS,
    AGENTS_A1,
    DEFAULT_CHAT_PATH,
    OPENAI_COMPATIBLE,
    AdvisoryModelOption,
    get_model_option,
)

__all__ = [
    "ADVISORY_MODEL_OPTIONS",
    "AGENTS_A1",
    "DEFAULT_CHAT_PATH",
    "OPENAI_COMPATIBLE",
    "AdvisoryConfigError",
    "AdvisoryHttpError",
    "AdvisoryModelClient",
    "AdvisoryModelConfig",
    "AdvisoryModelOption",
    "get_model_option",
]
