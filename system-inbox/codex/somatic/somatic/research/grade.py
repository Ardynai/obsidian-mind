"""Evidence-grade rubric from source metadata. Default NONE when unbound."""

from __future__ import annotations

from somatic.safety.core import EvidenceGrade

from .bind import BoundClaim
from .corpus import Passage

_STUDY_TYPE_GRADE = {
    "systematic-review": EvidenceGrade.STRONG,
    "meta-analysis": EvidenceGrade.STRONG,
    "rct": EvidenceGrade.MODERATE,
    "randomized-controlled-trial": EvidenceGrade.MODERATE,
    "observational": EvidenceGrade.LIMITED,
    "cohort": EvidenceGrade.LIMITED,
    "case-control": EvidenceGrade.LIMITED,
    "narrative": EvidenceGrade.PRELIMINARY,
    "unknown": EvidenceGrade.PRELIMINARY,
    "fixture": EvidenceGrade.PRELIMINARY,
}

_RANK = {
    EvidenceGrade.NONE: 0,
    EvidenceGrade.PRELIMINARY: 1,
    EvidenceGrade.LIMITED: 2,
    EvidenceGrade.MODERATE: 3,
    EvidenceGrade.STRONG: 4,
}


def grade_study_type(study_type: str) -> str:
    key = str(study_type or "unknown").strip().lower()
    return _STUDY_TYPE_GRADE.get(key, EvidenceGrade.PRELIMINARY)


def grade_from_passages(
    passages: tuple[Passage, ...] | list[Passage],
    *,
    claims: tuple[BoundClaim, ...] | list[BoundClaim] | None = None,
) -> str:
    """Grade cited passages only. No citations → NONE."""

    if not passages:
        return EvidenceGrade.NONE
    allowed = {passage.id: passage for passage in passages}
    if claims is not None:
        cited_ids = {cite for claim in claims for cite in claim.passage_ids}
        if not cited_ids:
            return EvidenceGrade.NONE
        allowed = {key: value for key, value in allowed.items() if key in cited_ids}
        if not allowed:
            return EvidenceGrade.NONE
    best = EvidenceGrade.NONE
    for passage in allowed.values():
        grade = grade_study_type(passage.study_type)
        if _RANK[grade] > _RANK[best]:
            best = grade
    return best
