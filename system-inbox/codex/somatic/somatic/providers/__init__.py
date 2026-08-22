"""Provider adapter interface scaffolds.

These modules define Somatic-owned protocol boundaries only. They do not import
or initialize PaperQA2, Robin, scientific-agent-skills, AutoScientists, Boltz,
or any other external runtime.
"""

from .biomodel import (
    BiomodelEvidenceRecord,
    BiomodelPlan,
    BiomodelProvider,
    BiomodelRequest,
    BiomodelResult,
    biomodel_result_to_evidence_record,
)
from .boltz import (
    BoltzOptionalDependencyError,
    BoltzProvider,
    BoltzProviderConfig,
    BoltzRuntimeNotEnabledError,
)
from .literature import (
    LiteratureDocument,
    LiteratureEvidenceDraft,
    LiteratureProvider,
    LiteratureQuery,
)
from .paperqa2 import (
    PaperQA2LiteratureProvider,
    PaperQA2OptionalDependencyError,
    PaperQA2ProviderConfig,
    PaperQA2RuntimeNotEnabledError,
)
from .robin import (
    RobinPlanRequest,
    RobinProvider,
    RobinProviderConfig,
    RobinReferencePlan,
    RobinRuntimeNotEnabledError,
)
from .science_skills import (
    DatabaseConnectorRecord,
    ScienceSkillProvider,
    ScienceSkillRecord,
    SkillLookupRequest,
)
from .scientific_agent_skills import (
    ScientificAgentSkillsProvider,
    ScientificAgentSkillsProviderConfig,
    ScientificAgentSkillsRuntimeNotEnabledError,
)
from .sensors import (
    SensorEvidenceRecord,
    SensorFeatureSet,
    SensorObservation,
    SensorPrivacyPolicy,
    SensorProvider,
    SensorStreamPlan,
)
from .team_orchestration import (
    AutoScientistsRuntimeNotEnabledError,
    AutoScientistsTeamOrchestrationProvider,
    AutoScientistsTeamOrchestrationProviderConfig,
    TeamMemberSpec,
    TeamOrchestrationPlan,
    TeamOrchestrationProvider,
    TeamOrchestrationRequest,
)

__all__ = [
    "BiomodelEvidenceRecord",
    "BiomodelPlan",
    "BiomodelProvider",
    "BiomodelRequest",
    "BiomodelResult",
    "BoltzOptionalDependencyError",
    "BoltzProvider",
    "BoltzProviderConfig",
    "BoltzRuntimeNotEnabledError",
    "DatabaseConnectorRecord",
    "LiteratureDocument",
    "LiteratureEvidenceDraft",
    "LiteratureProvider",
    "LiteratureQuery",
    "PaperQA2LiteratureProvider",
    "PaperQA2OptionalDependencyError",
    "PaperQA2ProviderConfig",
    "PaperQA2RuntimeNotEnabledError",
    "RobinPlanRequest",
    "RobinProvider",
    "RobinProviderConfig",
    "RobinReferencePlan",
    "RobinRuntimeNotEnabledError",
    "ScienceSkillProvider",
    "ScienceSkillRecord",
    "ScientificAgentSkillsProvider",
    "ScientificAgentSkillsProviderConfig",
    "ScientificAgentSkillsRuntimeNotEnabledError",
    "SensorEvidenceRecord",
    "SensorFeatureSet",
    "SensorObservation",
    "SensorPrivacyPolicy",
    "SensorProvider",
    "SensorStreamPlan",
    "SkillLookupRequest",
    "AutoScientistsRuntimeNotEnabledError",
    "AutoScientistsTeamOrchestrationProvider",
    "AutoScientistsTeamOrchestrationProviderConfig",
    "TeamMemberSpec",
    "TeamOrchestrationPlan",
    "TeamOrchestrationProvider",
    "TeamOrchestrationRequest",
    "biomodel_result_to_evidence_record",
]
