"""Offline literature passages for citation-bound research.

v1 is corpus-only. Live PubMed/ClinicalTrials retrieval would exceed the
``autonomous-research`` scope text (offline/mock only) and is not enabled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CORPUS_PATH = Path(__file__).resolve().parent / "offline_corpus.json"


@dataclass(frozen=True)
class Passage:
    """One retrieved text unit that may be cited by id."""

    id: str
    title: str
    text: str
    source_id: str
    year: int | None
    study_type: str
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "source_id": self.source_id,
            "year": self.year,
            "study_type": self.study_type,
            "url": self.url,
        }


def load_corpus(path: str | Path | None = None) -> tuple[Passage, ...]:
    destination = Path(path) if path is not None else DEFAULT_CORPUS_PATH
    payload = json.loads(destination.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("passages"), list):
        raise ValueError("corpus must be a JSON object with a passages list")
    passages: list[Passage] = []
    seen: set[str] = set()
    for row in payload["passages"]:
        if not isinstance(row, dict):
            raise ValueError("each corpus passage must be an object")
        passage_id = str(row.get("id") or "").strip()
        text = str(row.get("text") or "").strip()
        if not passage_id or not text:
            raise ValueError("passage id and text are required")
        if passage_id in seen:
            raise ValueError(f"duplicate passage id: {passage_id}")
        seen.add(passage_id)
        year_raw = row.get("year")
        year = int(year_raw) if year_raw not in (None, "") else None
        passages.append(
            Passage(
                id=passage_id,
                title=str(row.get("title") or passage_id),
                text=text,
                source_id=str(row.get("source_id") or passage_id),
                year=year,
                study_type=str(row.get("study_type") or "unknown").strip().lower(),
                url=str(row.get("url") or ""),
            )
        )
    return tuple(passages)
