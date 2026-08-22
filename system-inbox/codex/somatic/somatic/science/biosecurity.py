"""Biosecurity screen: refuse molecules-of-concern by public name. No uplift."""

from __future__ import annotations

from dataclasses import dataclass

# Public select-agent / high-concern toxin and pathogen *names* used only as a
# refuse-list. This module never emits synthesis, modification, or acquisition
# instructions.
_CONCERN_NAMES = (
    "ricin",
    "saxitoxin",
    "botulinum",
    "variola",
    "ebola",
    "marburg",
    "tularemia",
    "anthrax",
    "yersinia pestis",
    "francisella tularensis",
)


@dataclass(frozen=True)
class BiosecurityResult:
    blocked: bool
    matched: str
    guidance: str


def screen_biosecurity(text: str) -> BiosecurityResult:
    """Return a refuse+log result when ``text`` names a molecule-of-concern."""

    haystack = " ".join(str(text or "").lower().split())
    for name in _CONCERN_NAMES:
        if name in haystack:
            return BiosecurityResult(
                blocked=True,
                matched=name,
                guidance=(
                    "Biosecurity gate refused this request. Somatic will not plan, "
                    "simulate, or retrieve acquisition or modification pathways for "
                    "molecules or pathogens of concern. Consult appropriate authorities."
                ),
            )
    return BiosecurityResult(blocked=False, matched="", guidance="")
