from dataclasses import dataclass, field
from importlib.util import find_spec

from .literature import LiteratureDocument, LiteratureQuery

PAPERQA2_SOURCE_PATH = r"C:\AI\external-sources\somatic\paper-qa"
PAPERQA2_INSPECTED_COMMIT = "d2c3c698fdf06986aa021812ab3186d3696438d8"


class PaperQA2OptionalDependencyError(RuntimeError):
    """Raised when the optional PaperQA2 runtime is requested but unavailable."""


class PaperQA2RuntimeNotEnabledError(RuntimeError):
    """Raised when real PaperQA2 execution is requested before a runtime adapter exists."""


@dataclass(frozen=True)
class PaperQA2ProviderConfig:
    enabled: bool = False
    mode: str = "mock"
    package_name: str = "paperqa"
    max_results: int = 3
    allow_external_calls: bool = False
    require_explicit_consent: bool = True
    staged_source_path: str = PAPERQA2_SOURCE_PATH
    inspected_commit: str = PAPERQA2_INSPECTED_COMMIT
    mock_corpus_id: str = "paperqa2-source-inspection"
    metadata: dict[str, object] = field(default_factory=dict)


class PaperQA2LiteratureProvider:
    provider_id = "paperqa2-literature-provider"
    offline_supported = True
    capabilities = (
        "literature.search",
        "literature.evidence_extract",
        "literature.context",
    )

    def __init__(self, config: PaperQA2ProviderConfig | None = None):
        self.config = config or PaperQA2ProviderConfig()

    def is_available(self) -> bool:
        return find_spec(self.config.package_name) is not None

    def validate_config(self) -> list[str]:
        errors: list[str] = []
        if self.config.mode not in {"mock", "real"}:
            errors.append("PaperQA2 provider mode must be 'mock' or 'real'.")
        if self.config.max_results < 1:
            errors.append("PaperQA2 provider max_results must be at least 1.")
        if self.config.allow_external_calls:
            errors.append("PaperQA2 external calls are disabled in the Phase 5B scaffold.")
        if self.config.mode == "real" and not self.config.enabled:
            errors.append("PaperQA2 real mode requires enabled=True and explicit configuration.")
        return errors

    def search(self, query: LiteratureQuery) -> list[LiteratureDocument]:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()

        limit = max(1, min(query.max_results, self.config.max_results))
        return list(self._mock_documents(query))[:limit]

    def extract_evidence(self, documents: list[LiteratureDocument]) -> list[dict[str, object]]:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()

        evidence_records: list[dict[str, object]] = []
        for index, document in enumerate(documents, start=1):
            evidence_records.append(
                {
                    "id": f"paperqa2-mock-evidence-{index:03d}",
                    "provider_id": self.provider_id,
                    "document_id": document.id,
                    "record_type": "literature-context",
                    "title": document.title,
                    "citation": document.citation,
                    "source_ref": document.source_ref,
                    "evidence_refs": list(document.evidence_refs),
                    "summary": (
                        "Deterministic PaperQA2 scaffold evidence generated from "
                        "local Somatic fixture metadata only."
                    ),
                    "provenance": {
                        "mode": self.config.mode,
                        "mock": True,
                        "external_calls": False,
                        "staged_source_path": self.config.staged_source_path,
                        "inspected_commit": self.config.inspected_commit,
                    },
                }
            )
        return evidence_records

    def retrieve_literature_context(self, query: LiteratureQuery | str) -> dict[str, object]:
        literature_query = (
            query if isinstance(query, LiteratureQuery) else LiteratureQuery(query=query)
        )
        documents = self.search(literature_query)
        evidence = self.extract_evidence(documents)
        return {
            "provider_id": self.provider_id,
            "mode": self.config.mode,
            "available": self.is_available(),
            "offline_supported": self.offline_supported,
            "query": literature_query.query,
            "corpus_refs": list(literature_query.corpus_refs),
            "documents": [self._document_to_dict(document) for document in documents],
            "evidence": evidence,
            "external_calls": False,
        }

    def _raise_for_invalid_config(self) -> None:
        errors = self.validate_config()
        if errors:
            raise ValueError("; ".join(errors))

    def _raise_for_real_mode(self) -> None:
        if not self.is_available():
            raise PaperQA2OptionalDependencyError(
                "PaperQA2 real mode requires the optional 'paperqa' package. "
                "Install/configure it outside the basic Somatic install before enabling "
                "a future real adapter."
            )
        raise PaperQA2RuntimeNotEnabledError(
            "PaperQA2 is installed, but Somatic Phase 5B only provides the disabled "
            "adapter scaffold. Real PaperQA2 search/evidence execution is future work."
        )

    def _mock_documents(self, query: LiteratureQuery) -> tuple[LiteratureDocument, ...]:
        normalized_query = " ".join(query.query.split()) or "unspecified literature query"
        return (
            LiteratureDocument(
                id="paperqa2-mock-doc-001",
                title="PaperQA2 staged source inspection",
                source_ref=f"mock-paperqa2://{self.config.mock_corpus_id}/source-inspection",
                citation=(
                    f"Future-House/paper-qa {self.config.inspected_commit[:12]} source inspection"
                ),
                evidence_refs=("paperqa2-mock-evidence-001",),
                metadata={
                    "query": normalized_query,
                    "role": "source-boundary",
                    "staged_source_path": self.config.staged_source_path,
                    "external_calls": False,
                },
            ),
            LiteratureDocument(
                id="paperqa2-mock-doc-002",
                title="PaperQA2 adapter boundary note",
                source_ref=f"mock-paperqa2://{self.config.mock_corpus_id}/adapter-boundary",
                citation="Somatic PaperQA2 adapter scaffold documentation",
                evidence_refs=("paperqa2-mock-evidence-002",),
                metadata={
                    "query": normalized_query,
                    "role": "adapter-contract",
                    "wrap": "LiteratureProvider.search and extract_evidence",
                    "external_calls": False,
                },
            ),
            LiteratureDocument(
                id="paperqa2-mock-doc-003",
                title="PaperQA2 dependency and consent boundary",
                source_ref=f"mock-paperqa2://{self.config.mock_corpus_id}/safety-boundary",
                citation="Somatic Phase 5B provider fixture",
                evidence_refs=("paperqa2-mock-evidence-003",),
                metadata={
                    "query": normalized_query,
                    "role": "safety",
                    "requires_explicit_consent": self.config.require_explicit_consent,
                    "external_calls": False,
                },
            ),
        )

    @staticmethod
    def _document_to_dict(document: LiteratureDocument) -> dict[str, object]:
        return {
            "id": document.id,
            "title": document.title,
            "source_ref": document.source_ref,
            "citation": document.citation,
            "evidence_refs": list(document.evidence_refs),
            "metadata": document.metadata,
        }
