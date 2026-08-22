"""Disabled Boltz-2 biomodel provider planning scaffold."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from importlib.util import find_spec
from pathlib import Path

from somatic.providers.biomodel import (
    BiomodelEvidenceRecord,
    BiomodelPlan,
    BiomodelRequest,
    BiomodelResult,
    biomodel_result_to_evidence_record,
)
from somatic.safety.biomodel import (
    BiomodelConsentRecord,
    BiomodelReadinessReport,
    BiomodelRuntimePolicy,
    evaluate_biomodel_readiness,
)

BOLTZ_SOURCE_PATH = r"C:\AI\external-sources\somatic\boltz"
BOLTZ_INSPECTED_COMMIT = "b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc"
BOLTZ_LICENSE = "MIT"


class BoltzOptionalDependencyError(RuntimeError):
    """Raised when real Boltz mode is requested without the optional package."""


class BoltzRuntimeNotEnabledError(RuntimeError):
    """Raised when any Boltz execution path is requested in the scaffold phase."""


class BoltzConfigurationError(ValueError):
    """Raised when Boltz provider configuration crosses scaffold boundaries."""


class BoltzReadinessGateError(BoltzRuntimeNotEnabledError):
    """Raised when biomodel readiness gates block real Boltz mode."""

    def __init__(self, message: str, readiness_report: BiomodelReadinessReport):
        super().__init__(message)
        self.readiness_report = readiness_report


@dataclass(frozen=True)
class BoltzProviderConfig:
    enabled: bool = False
    mode: str = "mock"
    package_name: str = "boltz"
    default_model: str = "boltz2"
    output_format: str = "mmcif"
    allow_runtime_execution: bool = False
    allow_model_downloads: bool = False
    allow_msa_server: bool = False
    allow_network_calls: bool = False
    allow_gpu_execution: bool = False
    require_explicit_consent: bool = True
    staged_source_path: str = BOLTZ_SOURCE_PATH
    inspected_commit: str = BOLTZ_INSPECTED_COMMIT
    fake_backed: bool = True
    runtime_policy: BiomodelRuntimePolicy | None = None
    consent_record: BiomodelConsentRecord | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class BoltzProvider:
    """Plan-only Boltz-2 adapter scaffold.

    This provider never imports or executes Boltz. It only records deterministic
    plan/result metadata for future in-silico evidence boundaries.
    """

    provider_id = "boltz2-biomodel-provider"
    offline_supported = True
    capabilities = (
        "biomodel.plan",
        "biomodel.result_metadata",
        "biomodel.evidence_record",
    )

    def __init__(self, config: BoltzProviderConfig | None = None):
        self.config = config or BoltzProviderConfig()

    def is_available(self) -> bool:
        if self.config.package_name != "boltz":
            raise BoltzConfigurationError(
                "Boltz provider package_name must remain the literal top-level package 'boltz'."
            )
        return find_spec(self.config.package_name) is not None

    def is_source_staged(self) -> bool:
        return Path(self.config.staged_source_path).exists()

    def validate_config(self) -> list[str]:
        errors: list[str] = []
        if self.config.mode not in {"mock", "real"}:
            errors.append("Boltz provider mode must be 'mock' or 'real'.")
        if self.config.package_name != "boltz":
            errors.append(
                "Boltz provider package_name must remain the literal top-level package 'boltz'."
            )
        if self.config.default_model not in {"boltz1", "boltz2"}:
            errors.append("Boltz provider default_model must be 'boltz1' or 'boltz2'.")
        if self.config.output_format not in {"mmcif", "pdb"}:
            errors.append("Boltz provider output_format must be 'mmcif' or 'pdb'.")
        if self.config.allow_model_downloads:
            errors.append("Boltz model downloads are disabled in the Phase 6C scaffold.")
        if self.config.allow_msa_server:
            errors.append("Boltz MSA server calls are disabled in the Phase 6C scaffold.")
        if self.config.allow_network_calls:
            errors.append("Boltz network calls are disabled in the Phase 6C scaffold.")
        if self.config.allow_gpu_execution:
            errors.append("Boltz GPU execution is disabled in the Phase 6C scaffold.")
        if self.config.allow_runtime_execution:
            errors.append("Boltz runtime execution is disabled in the Phase 6C scaffold.")
        if self.config.mode == "mock" and not self.config.fake_backed:
            errors.append("Boltz mock mode must remain fake-backed.")
        return errors

    def status(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "provider_id": self.provider_id,
            "status": "scaffolded",
            "disabled_by_default": True,
            "fake_backed": self.config.fake_backed,
            "mode": self.config.mode,
            "offline_supported": self.offline_supported,
            "source_status": "staged" if self.is_source_staged() else "not staged",
            "staged_source_path": self.config.staged_source_path,
            "inspected_commit": self.config.inspected_commit,
            "license": BOLTZ_LICENSE,
            "optional_dependency": "available" if self.is_available() else "unavailable",
            "runtime_import_allowed": False,
            "runtime_execution": False,
            "model_downloads": False,
            "msa_server": False,
            "network_calls": False,
            "gpu_execution": False,
            "research_only": True,
            "safety_gate_scaffold": True,
            "readiness_report": self._readiness_report(
                {
                    "provider_id": self.provider_id,
                    "status": "scaffolded",
                    "mode": self.config.mode,
                }
            ).to_dict(),
        }

    def plan(self, request: BiomodelRequest) -> BiomodelPlan:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode(
                {
                    "provider_id": self.provider_id,
                    "objective": request.objective,
                    "mode": "real",
                }
            )

        request_id = self._request_id(request)
        plan_id = f"boltz2-plan-{request_id}"
        readiness_report = self._readiness_report(
            {
                "id": plan_id,
                "provider_id": self.provider_id,
                "request_id": request_id,
                "objective": request.objective,
                "status": "planned-not-executed",
            }
        ).to_dict()
        return BiomodelPlan(
            id=plan_id,
            provider_id=self.provider_id,
            request_id=request_id,
            objective=request.objective,
            status="planned-not-executed",
            model_family="Boltz",
            model_version=self.config.default_model,
            command_shape=(
                "boltz",
                "predict",
                "<input_path>",
                "--model",
                self.config.default_model,
                "--out_dir",
                "<local-output-dir>",
                "--cache",
                "<explicit-local-cache>",
                "--output_format",
                self.config.output_format,
            ),
            input_artifact_refs=request.input_artifact_refs,
            output_artifact_refs=(
                f"mock-boltz://{plan_id}/predictions",
                f"mock-boltz://{plan_id}/confidence-json",
                f"mock-boltz://{plan_id}/affinity-json",
            ),
            required_local_artifacts=(
                "Boltz YAML input or deprecated FASTA input",
                "precomputed MSA or explicit single-sequence placeholder",
                "explicit local cache path for future real mode",
            ),
            blocked_actions=(
                "import boltz runtime",
                "execute boltz predict",
                "download CCD/molecule data",
                "download Boltz checkpoints",
                "call MMseqs2 or ColabFold MSA server",
                "use GPU/TPU runtime",
                "run training/evaluation/process scripts",
            ),
            consent_requirements=(
                "explicit opt-in before model runtime",
                "explicit opt-in before model/data download",
                "explicit opt-in before any MSA server or cloud call",
                "resource review before GPU execution",
            ),
            resource_requirements={
                "runtime_enabled": False,
                "default_upstream_accelerator": "gpu",
                "basic_install_dependency": False,
                "cpu_mode": "upstream-supported-but-significantly-slower",
                "storage": "future real mode must account for cache, model, and output artifacts",
            },
            assumptions=(
                "Boltz source was inspected read-only for planning.",
                "Mock mode emits metadata only and does not predict structures or affinity.",
            ),
            limitations=(
                "No protein structure, binding affinity, efficacy, safety, lab, or "
                "clinical conclusion is produced.",
                "Future real mode requires explicit implementation, provenance, consent, "
                "and resource gates.",
            ),
            provenance={
                "source_path": self.config.staged_source_path,
                "inspected_commit": self.config.inspected_commit,
                "license": BOLTZ_LICENSE,
                "upstream_entrypoint": "boltz = boltz.main:cli",
                "upstream_command": "boltz predict <INPUT_PATH> [OPTIONS]",
                "source_staged": self.is_source_staged(),
                "optional_dependency_available": self.is_available(),
            },
            metadata={
                "target_refs": list(request.target_refs),
                "constraints": dict(request.constraints),
                "request_metadata": dict(request.metadata),
                "mock": True,
                "runtime_execution": False,
                "model_downloads": False,
                "msa_server": False,
                "network_calls": False,
                "gpu_execution": False,
                "readiness_report": readiness_report,
                "runtime_policy": self._runtime_policy().to_dict(),
                "consent_record": self._consent_record().to_dict(),
                "real_runtime": "future-only",
                "phase": "6C",
            },
        )

    def run(self, request: BiomodelRequest) -> BiomodelResult:
        self._raise_for_invalid_config()
        if self.config.mode == "real":
            self._raise_for_real_mode(
                {
                    "provider_id": self.provider_id,
                    "objective": request.objective,
                    "mode": "real",
                }
            )

        plan = self.plan(request)
        readiness_report = plan.metadata["readiness_report"]
        digest = self._digest({"plan": plan.to_dict(), "provider_id": self.provider_id})
        return BiomodelResult(
            id=f"boltz2-result-{plan.request_id}",
            status="mock-planned-not-executed",
            artifact_refs=(
                f"mock-boltz://{plan.id}/plan.json",
                f"mock-boltz://{plan.id}/result-metadata.json",
            ),
            evidence_refs=(f"mock-boltz://{plan.id}/evidence-record",),
            assumptions=plan.assumptions,
            limitations=plan.limitations,
            metadata={
                "provider_id": self.provider_id,
                "plan": plan.to_dict(),
                "sha256": digest,
                "mock": True,
                "runtime_execution": False,
                "model_downloads": False,
                "msa_server": False,
                "network_calls": False,
                "gpu_execution": False,
                "readiness_report": readiness_report,
                "runtime_policy": self._runtime_policy().to_dict(),
                "consent_record": self._consent_record().to_dict(),
                "real_runtime": "future-only",
                "phase": "6C",
            },
        )

    def evidence_record(
        self,
        request: BiomodelRequest,
        result: BiomodelResult | None = None,
    ) -> BiomodelEvidenceRecord:
        result = result or self.run(request)
        return biomodel_result_to_evidence_record(
            request,
            result,
            provider_id=self.provider_id,
        )

    def _raise_for_invalid_config(self) -> None:
        errors = self.validate_config()
        if errors:
            raise BoltzConfigurationError("; ".join(errors))

    def _raise_for_real_mode(self, plan_context: dict[str, object]) -> None:
        report = self._readiness_report(plan_context)
        if not report.ready:
            raise BoltzReadinessGateError(
                "Boltz real mode blocked by biomodel readiness gates: "
                + ", ".join(report.block_reasons),
                report,
            )
        if not self.config.enabled:
            raise BoltzRuntimeNotEnabledError(
                "Boltz real mode requires enabled=True and a future reviewed runtime "
                "adapter. Phase 6C is safety-gated and runtime-disabled."
            )
        if not self.is_available():
            raise BoltzOptionalDependencyError(
                "Boltz real mode requires the optional 'boltz' package outside the "
                "basic Somatic install. Phase 6C does not install or import Boltz."
            )
        raise BoltzRuntimeNotEnabledError(
            "Boltz is available, but Somatic Phase 6C does not implement real runtime "
            "execution. Readiness gates are recorded for future work only; real "
            "prediction, model downloads, MSA server calls, network calls, and GPU "
            "execution remain disabled."
        )

    def _readiness_report(self, plan_context: dict[str, object]) -> BiomodelReadinessReport:
        return evaluate_biomodel_readiness(
            plan_context,
            self._runtime_policy(),
            self._consent_record(),
        )

    def _runtime_policy(self) -> BiomodelRuntimePolicy:
        return self.config.runtime_policy or BiomodelRuntimePolicy()

    def _consent_record(self) -> BiomodelConsentRecord:
        return self.config.consent_record or BiomodelConsentRecord()

    @staticmethod
    def _request_id(request: BiomodelRequest) -> str:
        return BoltzProvider._digest(
            {
                "objective": request.objective,
                "target_refs": list(request.target_refs),
                "input_artifact_refs": list(request.input_artifact_refs),
                "constraints": request.constraints,
                "metadata": request.metadata,
            }
        )[:12]

    @staticmethod
    def _digest(payload: dict[str, object]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return sha256(encoded).hexdigest()
