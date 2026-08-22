"""Frozen registry of OpenAI-compatible advisory model options.

Entries describe endpoint style only. No secrets are stored here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdvisoryModelOption:
    """One known OpenAI-compatible model endpoint style."""

    id: str
    label: str
    model: str
    endpoint_style: str
    default_path: str
    notes: str


AGENTS_A1 = AdvisoryModelOption(
    id="agents-a1",
    label="Agents-A1 (InternScience)",
    model="InternScience/Agents-A1",
    endpoint_style="openai-chat",
    default_path="/v1/chat/completions",
    notes="Served via vLLM or SGLang behind an OpenAI-compatible chat endpoint.",
)

OPENAI_COMPATIBLE = AdvisoryModelOption(
    id="openai-compatible",
    label="OpenAI-compatible (generic)",
    model="",
    endpoint_style="openai-chat",
    default_path="/v1/chat/completions",
    notes="Works with Ollama and other OpenAI-compatible local or remote servers.",
)

ADVISORY_MODEL_OPTIONS: tuple[AdvisoryModelOption, ...] = (
    AGENTS_A1,
    OPENAI_COMPATIBLE,
)

_OPTION_BY_ID: dict[str, AdvisoryModelOption] = {
    option.id: option for option in ADVISORY_MODEL_OPTIONS
}

DEFAULT_CHAT_PATH = "/v1/chat/completions"


def get_model_option(option_id: str) -> AdvisoryModelOption | None:
    """Return a registry entry by id, or None if unknown."""

    return _OPTION_BY_ID.get(str(option_id))
