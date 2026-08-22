"""Informational parasite Q&A. Source-grounded; never a diagnosis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import AUTONOMOUS_RESEARCH
from somatic.research.loop import ResearchReport, run_research_loop

ROUTING_NOTE = (
    "Informational only. This path does not identify a parasite species "
    "and does not replace stool testing or a licensed clinician."
)


@dataclass(frozen=True)
class ParasiteReport:
    question: str
    research: ResearchReport
    honest_null: bool
    routing_note: str = ROUTING_NOTE

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "honest_null": self.honest_null,
            "routing_note": self.routing_note,
            "summary": self.research.result.summary,
            "research": self.research.to_dict(),
        }


def ask_parasite(ledger: ConsentLedger, question: str, *, k: int = 5) -> ParasiteReport:
    """Answer a parasite question from the offline corpus. Emergency-screened."""

    research = run_research_loop(
        ledger,
        question,
        k=k,
        consent_scope=AUTONOMOUS_RESEARCH,
    )
    routing = (
        research.result.summary
        if research.result.consent_scope == "emergency-screen"
        else ROUTING_NOTE
    )
    return ParasiteReport(
        question=str(question),
        research=research,
        honest_null=research.honest_null,
        routing_note=routing,
    )
