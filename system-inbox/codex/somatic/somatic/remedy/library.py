"""Evidence-graded informational remedy library. Default grade NONE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import REMEDY_LIBRARY
from somatic.research.bind import HONEST_NULL, BoundClaim
from somatic.research.grade import grade_from_passages
from somatic.research.loop import ResearchReport, run_research_loop
from somatic.safety.core import EvidenceGrade

SAFETY_NOTES = (
    "Informational library access only; not a prescription or dosing authority.",
    "Absence of retrieved evidence is reported as no evidence available.",
)

_RANK = {
    EvidenceGrade.NONE: 0,
    EvidenceGrade.PRELIMINARY: 1,
    EvidenceGrade.LIMITED: 2,
    EvidenceGrade.MODERATE: 3,
    EvidenceGrade.STRONG: 4,
}


@dataclass(frozen=True)
class RemedyEntry:
    """One citation-bound library row. Grade defaults to NONE when unbound."""

    claim: str
    evidence_grade: str
    citations: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "evidence_grade": self.evidence_grade,
            "citations": list(self.citations),
            "safety_notes": list(self.safety_notes),
        }


@dataclass(frozen=True)
class RemedyReport:
    query: str
    entries: tuple[RemedyEntry, ...]
    research: ResearchReport
    honest_null: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "entries": [entry.to_dict() for entry in self.entries],
            "honest_null": self.honest_null,
            "research": self.research.to_dict(),
        }


def lookup_remedy(ledger: ConsentLedger, query: str, *, k: int = 5) -> RemedyReport:
    """Look up a remedy topic against the offline corpus. Requires REMEDY_LIBRARY."""

    research = run_research_loop(
        ledger,
        query,
        k=k,
        consent_scope=REMEDY_LIBRARY,
    )
    if research.honest_null:
        entry = RemedyEntry(
            claim=HONEST_NULL,
            evidence_grade=EvidenceGrade.NONE,
            citations=(),
            safety_notes=SAFETY_NOTES,
        )
        return RemedyReport(
            query=str(query),
            entries=(entry,),
            research=research,
            honest_null=True,
        )
    entries = tuple(
        RemedyEntry(
            claim=claim.text,
            evidence_grade=_cap_grade(
                _grade_for_claim(claim, research),
            ),
            citations=claim.passage_ids,
            safety_notes=SAFETY_NOTES,
        )
        for claim in research.claims
    )
    return RemedyReport(
        query=str(query),
        entries=entries,
        research=research,
        honest_null=False,
    )


def _grade_for_claim(claim: BoundClaim, research: ResearchReport) -> str:
    cited = [passage for passage in research.retrieved if passage.id in set(claim.passage_ids)]
    return grade_from_passages(cited, claims=(claim,))


def _cap_grade(grade: str) -> str:
    """Folk-remedy surface never inflates above LIMITED."""

    if _RANK.get(grade, 0) > _RANK[EvidenceGrade.LIMITED]:
        return EvidenceGrade.LIMITED
    return grade
