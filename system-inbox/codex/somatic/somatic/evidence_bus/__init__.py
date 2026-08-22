"""Evidence Bus public surface.

Record types stay import-compatible (`from somatic.evidence_bus import EvidenceSource`).
Runnable adapters are additive and sandbox-only in the core.
"""

from .adapter import EvidenceAdapter, EvidenceCost, HypothesisSpec
from .loop import EvidenceLoopReport, EvidenceStep, run_evidence_loop
from .records import (
    EVIDENCE_MODALITIES,
    EvidenceSource,
    MeasurementPlan,
    RawEvidence,
    StructuredVerdict,
)
from .sandbox_adapters import (
    SandboxModalityAdapter,
    SensorHardwareDisabled,
    sandbox_adapters,
)

__all__ = [
    "EVIDENCE_MODALITIES",
    "EvidenceAdapter",
    "EvidenceCost",
    "EvidenceLoopReport",
    "EvidenceSource",
    "EvidenceStep",
    "HypothesisSpec",
    "MeasurementPlan",
    "RawEvidence",
    "SandboxModalityAdapter",
    "SensorHardwareDisabled",
    "StructuredVerdict",
    "run_evidence_loop",
    "sandbox_adapters",
]
