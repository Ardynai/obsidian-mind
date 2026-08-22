"""Render-only presence: Scientist and Doctor personas over a gated verdict.

Never alters the verdict. Never opens a camera, microphone, or talking-head
runtime. TTS / MiniCPM-o / Duix extras stay unimported in core.
"""

from __future__ import annotations

from dataclasses import dataclass

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import AI_ADVISORY
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryFramingError,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)

PERSONAS = ("scientist", "doctor")


@dataclass(frozen=True)
class PresenceRender:
    persona: str
    speech: str
    verdict_unchanged: bool
    tts_runtime: str
    talking_head_runtime: str
    camera_registered: bool
    microphone_registered: bool


def render_presence(
    ledger: ConsentLedger,
    verdict_summary: str,
    *,
    persona: str = "doctor",
) -> PresenceRender:
    """Rephrase a gated verdict. Requires AI_ADVISORY. Render-only."""

    require_consent(ledger, AI_ADVISORY)
    voice = str(persona or "doctor").strip().lower()
    if voice not in PERSONAS:
        raise ValueError(f"unsupported persona: {persona}")
    text = str(verdict_summary or "").strip()
    if not text:
        raise ValueError("verdict summary must be non-empty")

    screen = emergency_screen(text)
    if screen.triggered:
        return PresenceRender(
            persona=voice,
            speech=screen.guidance or EMERGENCY_GUIDANCE,
            verdict_unchanged=True,
            tts_runtime="disabled",
            talking_head_runtime="disabled",
            camera_registered=False,
            microphone_registered=False,
        )

    if voice == "scientist":
        spoken = (
            f"Scientist presence (render-only): {text} "
            "This is a sandbox research restatement of the gated verdict; methods were not changed."
        )
    else:
        spoken = (
            f"Doctor presence (render-only): {text} {INFORMATIONAL_NOTICE} {PROFESSIONAL_ROUTING}"
        )
    try:
        framed = frame_advisory(
            summary=spoken,
            evidence_grade=EvidenceGrade.NONE,
            sources=("presence-render-only",),
            consent_scope=AI_ADVISORY,
            authoritative_scan=True,
        )
        speech = framed.summary
    except AdvisoryFramingError:
        speech = (
            "The presence layer could not rephrase this verdict as informational. "
            f"{INFORMATIONAL_NOTICE}"
        )
    return PresenceRender(
        persona=voice,
        speech=speech,
        verdict_unchanged=text in speech or speech.startswith("The presence layer"),
        tts_runtime="disabled",
        talking_head_runtime="disabled",
        camera_registered=False,
        microphone_registered=False,
    )
