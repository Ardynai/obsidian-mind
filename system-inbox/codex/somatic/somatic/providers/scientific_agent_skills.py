from dataclasses import dataclass, field
from importlib.util import find_spec
from pathlib import Path

from .science_skills import DatabaseConnectorRecord, ScienceSkillRecord, SkillLookupRequest

SCIENTIFIC_AGENT_SKILLS_SOURCE_PATH = r"C:\AI\external-sources\somatic\scientific-agent-skills"
SCIENTIFIC_AGENT_SKILLS_INSPECTED_COMMIT = "effb57c5699c1d400ef461a7aa80fc6693939805"


class ScientificAgentSkillsRuntimeNotEnabledError(RuntimeError):
    """Raised when real skill catalog loading or execution is requested."""


@dataclass(frozen=True)
class ScientificAgentSkillsProviderConfig:
    enabled: bool = False
    mode: str = "mock"
    package_name: str = "scientific_agent_skills"
    max_skills: int = 5
    max_database_connectors: int = 5
    allow_external_calls: bool = False
    allow_skill_execution: bool = False
    require_explicit_consent: bool = True
    staged_source_path: str = SCIENTIFIC_AGENT_SKILLS_SOURCE_PATH
    inspected_commit: str = SCIENTIFIC_AGENT_SKILLS_INSPECTED_COMMIT
    mock_catalog_id: str = "scientific-agent-skills-sample-catalog"
    metadata: dict[str, object] = field(default_factory=dict)


class ScientificAgentSkillsProvider:
    provider_id = "scientific-agent-skills-provider"
    offline_supported = True
    capabilities = (
        "science_skills.lookup",
        "science_skills.describe",
        "science_skills.list",
        "science_database_connectors.list",
        "science_database_connectors.describe",
    )

    def __init__(self, config: ScientificAgentSkillsProviderConfig | None = None):
        self.config = config or ScientificAgentSkillsProviderConfig()

    def is_available(self) -> bool:
        return self.is_source_staged() or find_spec(self.config.package_name) is not None

    def is_source_staged(self) -> bool:
        return Path(self.config.staged_source_path).exists()

    def validate_config(self) -> list[str]:
        errors: list[str] = []
        if self.config.mode not in {"mock", "real"}:
            errors.append("Scientific Agent Skills provider mode must be 'mock' or 'real'.")
        if self.config.max_skills < 1:
            errors.append("Scientific Agent Skills max_skills must be at least 1.")
        if self.config.max_database_connectors < 1:
            errors.append("Scientific Agent Skills max_database_connectors must be at least 1.")
        if self.config.allow_external_calls:
            errors.append("External database/API calls are disabled in the Phase 5C scaffold.")
        if self.config.allow_skill_execution:
            errors.append("Skill execution is disabled in the Phase 5C scaffold.")
        if self.config.mode == "real" and not self.config.enabled:
            errors.append(
                "Scientific Agent Skills real mode requires enabled=True and explicit "
                "configuration."
            )
        return errors

    def lookup(self, request: SkillLookupRequest) -> list[ScienceSkillRecord]:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()

        tokens = self._request_tokens(request)
        if not tokens:
            return self.list_skills()

        matches = [skill for skill in self._mock_skills() if tokens & self._skill_tokens(skill)]
        return matches[: self.config.max_skills] if matches else self.list_skills()

    def describe(self, skill_id: str) -> ScienceSkillRecord:
        return self.describe_skill(skill_id)

    def list_skills(self) -> list[ScienceSkillRecord]:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()
        return list(self._mock_skills())[: self.config.max_skills]

    def list_database_connectors(self) -> list[DatabaseConnectorRecord]:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()
        return list(self._mock_database_connectors())[: self.config.max_database_connectors]

    def describe_skill(self, skill_id: str) -> ScienceSkillRecord:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()
        for skill in self._mock_skills():
            if skill.id == skill_id:
                return skill
        raise KeyError(f"Unknown Scientific Agent Skills mock skill: {skill_id}")

    def describe_database_connector(self, connector_id: str) -> DatabaseConnectorRecord:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode()
        for connector in self._mock_database_connectors():
            if connector.id == connector_id:
                return connector
        raise KeyError(f"Unknown Scientific Agent Skills mock database connector: {connector_id}")

    def catalog_summary(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "mode": self.config.mode,
            "available": self.is_available(),
            "source_staged": self.is_source_staged(),
            "execution_enabled": False,
            "external_calls": False,
            "skills": [self._skill_to_dict(skill) for skill in self.list_skills()],
            "database_connectors": [
                self._connector_to_dict(connector) for connector in self.list_database_connectors()
            ],
        }

    def _raise_for_invalid_config(self) -> None:
        errors = self.validate_config()
        if errors:
            raise ValueError("; ".join(errors))

    def _raise_for_real_mode(self) -> None:
        raise ScientificAgentSkillsRuntimeNotEnabledError(
            "Scientific Agent Skills real mode is not implemented in Phase 5C. "
            "This scaffold is metadata-only and does not load source catalogs, execute "
            "skills, call databases, or send data externally."
        )

    @staticmethod
    def _request_tokens(request: SkillLookupRequest) -> set[str]:
        values = (request.task, request.organism or "", request.modality or "", *request.tags)
        return {
            token
            for value in values
            for token in value.lower().replace("-", " ").split()
            if len(token) > 2
        }

    @staticmethod
    def _skill_tokens(skill: ScienceSkillRecord) -> set[str]:
        values = (
            skill.id,
            skill.name,
            skill.description,
            *skill.input_requirements,
            *skill.output_artifacts,
            *skill.safety_notes,
            *[str(tag) for tag in skill.metadata.get("tags", ())],
            str(skill.metadata.get("category", "")),
        )
        return {
            token
            for value in values
            for token in value.lower().replace("-", " ").split()
            if len(token) > 2
        }

    def _mock_skills(self) -> tuple[ScienceSkillRecord, ...]:
        provenance = {
            "mock_catalog_id": self.config.mock_catalog_id,
            "staged_source_path": self.config.staged_source_path,
            "inspected_commit": self.config.inspected_commit,
            "metadata_only": True,
            "skill_execution": False,
            "external_calls": False,
        }
        return (
            ScienceSkillRecord(
                id="paper-lookup",
                name="Paper Lookup",
                description=(
                    "Mock metadata for the staged paper-lookup skill covering PubMed, "
                    "PMC, bioRxiv, medRxiv, arXiv, OpenAlex, Crossref, Semantic "
                    "Scholar, CORE, and Unpaywall."
                ),
                input_requirements=("literature query", "DOI/PMID/arXiv id optional"),
                output_artifacts=("paper metadata list", "citation metadata"),
                safety_notes=(
                    "Metadata-only in Somatic Phase 5C.",
                    "Future live use must declare database/API calls and consent.",
                ),
                metadata=provenance
                | {
                    "category": "literature",
                    "source_skill_path": "skills/paper-lookup/SKILL.md",
                    "tags": ("literature", "papers", "citations"),
                },
            ),
            ScienceSkillRecord(
                id="database-lookup",
                name="Database Lookup",
                description=(
                    "Mock metadata for the unified database-lookup skill covering "
                    "public scientific, biomedical, materials, patent, economic, and "
                    "clinical databases."
                ),
                input_requirements=("entity or topic query", "database selection"),
                output_artifacts=("raw database response metadata", "queried database list"),
                safety_notes=(
                    "No database calls are made by this scaffold.",
                    "Clinical or health data must remain local unless explicitly configured.",
                ),
                metadata=provenance
                | {
                    "category": "database",
                    "source_skill_path": "skills/database-lookup/SKILL.md",
                    "tags": ("database", "pubchem", "chembl", "uniprot", "clinicaltrials"),
                },
            ),
            ScienceSkillRecord(
                id="medchem",
                name="Medchem",
                description=(
                    "Mock metadata for medicinal chemistry filtering, structural alerts, "
                    "drug-likeness rules, and library triage."
                ),
                input_requirements=("SMILES or molecule set", "filter criteria"),
                output_artifacts=("compound triage metadata", "filter rationale"),
                safety_notes=(
                    "No molecule processing or package import occurs in Phase 5C.",
                    "Future use must preserve provenance and scientific limitations.",
                ),
                metadata=provenance
                | {
                    "category": "chemistry",
                    "source_skill_path": "skills/medchem/SKILL.md",
                    "tags": ("chemistry", "drug-discovery", "screening"),
                },
            ),
            ScienceSkillRecord(
                id="clinical-decision-support",
                name="Clinical Decision Support",
                description=(
                    "Mock metadata for group-level clinical research document guidance, "
                    "evidence grading, biomarker cohort analysis, and treatment "
                    "recommendation report structure."
                ),
                input_requirements=("de-identified cohort evidence", "clinical question"),
                output_artifacts=("clinical research report plan", "evidence grading notes"),
                safety_notes=(
                    "Not for bedside or individual patient care.",
                    "No health data leaves Somatic in this scaffold.",
                ),
                metadata=provenance
                | {
                    "category": "clinical",
                    "source_skill_path": "skills/clinical-decision-support/SKILL.md",
                    "tags": ("clinical", "trials", "evidence-grading"),
                },
            ),
            ScienceSkillRecord(
                id="esm-responsible-biodesign-note",
                name="Protein Design Safety Placeholder",
                description=(
                    "Mock metadata derived from the staged ESM skill's responsible "
                    "biodesign note for future protein design safety review."
                ),
                input_requirements=("protein sequence/design objective", "safety review context"),
                output_artifacts=("biosecurity review note", "protein design caveats"),
                safety_notes=(
                    "Safety/biosecurity screening is metadata-only in Phase 5C.",
                    "Future live use requires explicit review before protein design work.",
                ),
                metadata=provenance
                | {
                    "category": "safety",
                    "source_skill_path": "skills/esm/SKILL.md",
                    "tags": ("protein", "biosecurity", "safety"),
                    "mock_placeholder": True,
                },
            ),
        )

    def _mock_database_connectors(self) -> tuple[DatabaseConnectorRecord, ...]:
        provenance = {
            "mock_catalog_id": self.config.mock_catalog_id,
            "staged_source_path": self.config.staged_source_path,
            "inspected_commit": self.config.inspected_commit,
            "metadata_only": True,
            "external_calls": False,
        }
        return (
            DatabaseConnectorRecord(
                id="pubchem",
                name="PubChem",
                description="Mock metadata for compound, synonym, and property lookup.",
                source_skill_id="database-lookup",
                domains=("chemistry", "drug-discovery"),
                auth_notes=("Public API; future live use must respect rate limits.",),
                safety_notes=("No PubChem calls are made by the Phase 5C scaffold.",),
                metadata=provenance | {"reference_file": "references/pubchem.md"},
            ),
            DatabaseConnectorRecord(
                id="chembl",
                name="ChEMBL",
                description="Mock metadata for bioactivity and drug-target lookup.",
                source_skill_id="database-lookup",
                domains=("chemistry", "pharmacology"),
                auth_notes=("Public API; future live use must declare data locality.",),
                safety_notes=("No ChEMBL calls are made by the Phase 5C scaffold.",),
                metadata=provenance | {"reference_file": "references/chembl.md"},
            ),
            DatabaseConnectorRecord(
                id="clinicaltrials",
                name="ClinicalTrials.gov",
                description="Mock metadata for clinical trial registry lookup.",
                source_skill_id="database-lookup",
                domains=("clinical", "trials"),
                auth_notes=("Public API; future live use must avoid sending private data.",),
                safety_notes=("No clinical trial lookup is performed by this scaffold.",),
                metadata=provenance | {"reference_file": "references/clinicaltrials.md"},
            ),
            DatabaseConnectorRecord(
                id="uniprot",
                name="UniProt",
                description="Mock metadata for protein sequence and annotation lookup.",
                source_skill_id="database-lookup",
                domains=("biology", "protein"),
                auth_notes=("Public API; future live use must declare organism and query scope.",),
                safety_notes=("No UniProt calls are made by the Phase 5C scaffold.",),
                metadata=provenance | {"reference_file": "references/uniprot.md"},
            ),
            DatabaseConnectorRecord(
                id="pdb",
                name="RCSB PDB",
                description="Mock metadata for experimental 3D protein structures.",
                source_skill_id="database-lookup",
                domains=("biology", "structure"),
                auth_notes=("Public API; future live use must track provenance.",),
                safety_notes=("No PDB calls are made by the Phase 5C scaffold.",),
                metadata=provenance | {"reference_file": "references/pdb.md"},
            ),
        )

    @staticmethod
    def _skill_to_dict(skill: ScienceSkillRecord) -> dict[str, object]:
        return {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "input_requirements": list(skill.input_requirements),
            "output_artifacts": list(skill.output_artifacts),
            "safety_notes": list(skill.safety_notes),
            "metadata": skill.metadata,
        }

    @staticmethod
    def _connector_to_dict(connector: DatabaseConnectorRecord) -> dict[str, object]:
        return {
            "id": connector.id,
            "name": connector.name,
            "description": connector.description,
            "source_skill_id": connector.source_skill_id,
            "domains": list(connector.domains),
            "auth_notes": list(connector.auth_notes),
            "safety_notes": list(connector.safety_notes),
            "metadata": connector.metadata,
        }
