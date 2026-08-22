"""Consent-gated offline research loop with citation-binding.

Does not call a model. Claims are extracts of retrieved passages only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import AUTONOMOUS_RESEARCH
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryFramingError,
    AdvisoryResult,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)

from .bind import HONEST_NULL, BoundClaim, bind_claims, claims_from_passages
from .corpus import Passage, load_corpus
from .grade import grade_from_passages
from .live import live_enabled
from .retrieve import retrieve


@dataclass(frozen=True)
class ResearchReport:
    """Citation-bound informational research result."""

    question: str
    result: AdvisoryResult
    claims: tuple[BoundClaim, ...]
    retrieved: tuple[Passage, ...]
    dropped_unbound: int
    honest_null: bool
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "result": self.result.to_dict(),
            "claims": [claim.to_dict() for claim in self.claims],
            "retrieved": [passage.to_dict() for passage in self.retrieved],
            "dropped_unbound": self.dropped_unbound,
            "honest_null": self.honest_null,
            "generated_at": self.generated_at,
        }


def run_research_loop(
    ledger: ConsentLedger,
    question: str,
    *,
    corpus: tuple[Passage, ...] | list[Passage] | None = None,
    corpus_path: str | None = None,
    k: int = 5,
    extra_claims: list[dict[str, Any]] | None = None,
    consent_scope: Any = None,
) -> ResearchReport:
    """Retrieve, bind, and frame. Offline corpus only. No model memory."""

    scope = consent_scope if consent_scope is not None else AUTONOMOUS_RESEARCH
    require_consent(ledger, scope)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = str(question or "").strip()
    screen = emergency_screen(query)
    if screen.triggered:
        return ResearchReport(
            question=query,
            result=_emergency_result(screen.guidance or EMERGENCY_GUIDANCE),
            claims=(),
            retrieved=(),
            dropped_unbound=0,
            honest_null=True,
            generated_at=generated_at,
        )

    if live_enabled() and corpus is None and corpus_path is None:
        from .live import retrieve_live

        retrieved = retrieve_live(query, k=k)
        source_tag = "europe-pmc"
    else:
        retrieved = ()
        source_tag = "offline-corpus"
    if not retrieved:
        passages = tuple(corpus) if corpus is not None else load_corpus(corpus_path)
        retrieved = retrieve(passages, query, k=k)
        source_tag = "offline-corpus"
    raw_claims = claims_from_passages(retrieved)
    if extra_claims:
        raw_claims.extend(extra_claims)
    bound, dropped = bind_claims(raw_claims, retrieved)
    if not bound:
        result = _frame_research(
            HONEST_NULL,
            EvidenceGrade.NONE,
            ("research-loop", "honest-null"),
            scope,
        )
        return ResearchReport(
            question=query,
            result=result,
            claims=(),
            retrieved=retrieved,
            dropped_unbound=len(dropped),
            honest_null=True,
            generated_at=generated_at,
        )

    grade = grade_from_passages(retrieved, claims=bound)
    summary = _compose_summary(query, bound)
    sources = ["research-loop", source_tag]
    for claim in bound:
        sources.extend(f"passage:{passage_id}" for passage_id in claim.passage_ids)
    try:
        result = _frame_research(summary, grade, tuple(dict.fromkeys(sources)), scope)
    except AdvisoryFramingError:
        result = _frame_research(
            HONEST_NULL,
            EvidenceGrade.NONE,
            ("research-loop", "honest-null"),
            scope,
        )
        return ResearchReport(
            question=query,
            result=result,
            claims=(),
            retrieved=retrieved,
            dropped_unbound=len(dropped) + len(bound),
            honest_null=True,
            generated_at=generated_at,
        )
    return ResearchReport(
        question=query,
        result=result,
        claims=bound,
        retrieved=retrieved,
        dropped_unbound=len(dropped),
        honest_null=False,
        generated_at=generated_at,
    )


def _compose_summary(question: str, claims: tuple[BoundClaim, ...]) -> str:
    lines = [
        f"Citation-bound research for {question!r} (informational; not a diagnosis).",
    ]
    for claim in claims:
        cited = ", ".join(claim.passage_ids)
        lines.append(f"{claim.text} [cites {cited}]")
    lines.append(
        "These statements are bound to retrieved passages only. "
        "Confirm with a licensed professional."
    )
    return " ".join(lines)


def _frame_research(
    summary: str,
    evidence_grade: str,
    sources: tuple[str, ...],
    consent_scope: Any,
) -> AdvisoryResult:
    return frame_advisory(
        summary=summary,
        evidence_grade=evidence_grade,
        sources=sources,
        consent_scope=consent_scope,
        authoritative_scan=True,
    )


def _emergency_result(guidance: str) -> AdvisoryResult:
    return AdvisoryResult(
        summary=guidance,
        evidence_grade=EvidenceGrade.NONE,
        sources=("emergency-screen", "research-loop"),
        professional_routing=PROFESSIONAL_ROUTING,
        informational_notice=INFORMATIONAL_NOTICE,
        consent_scope="emergency-screen",
    )
