from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class LiteratureQuery:
    query: str
    max_results: int = 10
    corpus_refs: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LiteratureDocument:
    id: str
    title: str
    source_ref: str
    citation: str | None = None
    evidence_refs: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LiteratureEvidenceDraft:
    id: str
    document_id: str
    claim: str
    source_ref: str
    provenance_refs: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


class LiteratureProvider(Protocol):
    provider_id: str
    offline_supported: bool

    def search(self, query: LiteratureQuery) -> list[LiteratureDocument]:
        """Return provider-scoped document metadata without leaking raw secrets."""
        ...

    def extract_evidence(self, documents: list[LiteratureDocument]) -> list[dict[str, object]]:
        """Map documents into Somatic evidence records or evidence-record drafts."""
        ...
