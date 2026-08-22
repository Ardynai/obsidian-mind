"""Safety lane: live consent-gated core plus planning-only Phase 11/12 contracts."""

STATUS = "live-spine"
MEDICAL_BOUNDARY = "research-decision-support-human-review"

from .adapter_readiness import (  # noqa: E402
    REAL_MODE_GATE_BLOCKED_STATUS,
    REAL_MODE_GATE_REVIEWED_STATUS,
    REAL_MODE_PHASE_RUNTIME,
    REAL_MODE_READINESS_GATE_CONTRACT_VERSION,
    REAL_MODE_READINESS_GATE_KIND,
    REAL_MODE_REQUIRED_GATES,
    RealModeReadinessReport,
    RealModeReadinessReviewRecord,
    evaluate_real_mode_readiness,
    real_mode_readiness_gate_summary,
)
from .biomodel import (  # noqa: E402
    BiomodelConsentRecord,
    BiomodelReadinessGateError,
    BiomodelReadinessReport,
    BiomodelRuntimePolicy,
    evaluate_biomodel_readiness,
)

__all__ = [
    "STATUS",
    "MEDICAL_BOUNDARY",
    "BiomodelConsentRecord",
    "BiomodelReadinessGateError",
    "BiomodelReadinessReport",
    "BiomodelRuntimePolicy",
    "evaluate_biomodel_readiness",
    "REAL_MODE_GATE_BLOCKED_STATUS",
    "REAL_MODE_GATE_REVIEWED_STATUS",
    "REAL_MODE_PHASE_RUNTIME",
    "REAL_MODE_READINESS_GATE_CONTRACT_VERSION",
    "REAL_MODE_READINESS_GATE_KIND",
    "REAL_MODE_REQUIRED_GATES",
    "RealModeReadinessReport",
    "RealModeReadinessReviewRecord",
    "evaluate_real_mode_readiness",
    "real_mode_readiness_gate_summary",
]
