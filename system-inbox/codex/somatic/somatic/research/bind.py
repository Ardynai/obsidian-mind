"""Citation-binding: claims may only cite retrieved passage ids.

It is structurally impossible to emit a claim whose citation does not resolve
to a passage returned by retrieval. Unbound claims are dropped, never filled
from model memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .corpus import Passage

HONEST_NULL = "No evidence available; consult a professional."


@dataclass(frozen=True)
class BoundClaim:
    """A user-facing claim that cites only retrieved passages."""

    text: str
    passage_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "passage_ids": list(self.passage_ids)}


def bind_claims(
    raw_claims: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    retrieved: tuple[Passage, ...] | list[Passage],
) -> tuple[tuple[BoundClaim, ...], tuple[dict[str, Any], ...]]:
    """Keep claims whose every cite resolves; drop the rest."""

    retrieved_ids = {passage.id for passage in retrieved}
    bound: list[BoundClaim] = []
    dropped: list[dict[str, Any]] = []
    for item in raw_claims:
        if not isinstance(item, dict):
            dropped.append({"text": str(item), "cites": []})
            continue
        text = str(item.get("text") or "").strip()
        cites_raw = item.get("cites") or item.get("passage_ids") or ()
        if isinstance(cites_raw, str):
            cites = (cites_raw,)
        else:
            cites = tuple(str(cite).strip() for cite in cites_raw if str(cite).strip())
        if not text or not cites or any(cite not in retrieved_ids for cite in cites):
            dropped.append({"text": text, "cites": list(cites)})
            continue
        bound.append(BoundClaim(text=text, passage_ids=cites))
    return tuple(bound), tuple(dropped)


def claims_from_passages(retrieved: tuple[Passage, ...] | list[Passage]) -> list[dict[str, Any]]:
    """Build cite-by-id extracts. Claims are slices of retrieved text only."""

    claims: list[dict[str, Any]] = []
    for passage in retrieved:
        excerpt = " ".join(passage.text.split())
        if len(excerpt) > 280:
            excerpt = excerpt[:277].rstrip() + "..."
        claims.append(
            {
                "text": f"Passage {passage.id} ({passage.title}) states: {excerpt}",
                "cites": [passage.id],
            }
        )
    return claims
