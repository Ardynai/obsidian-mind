from dataclasses import dataclass, field
from typing import Protocol

AUTOSCIENTISTS_SOURCE_PATH = "C:\\AI\\external-sources\\somatic\\AutoScientists"
AUTOSCIENTISTS_SOURCE_COMMIT = "c71a92343b9a488ed10134be805845b9473ad18f"
AUTOSCIENTISTS_LICENSE_STATUS = "unresolved-no-license-file-found"


@dataclass(frozen=True)
class TeamMemberSpec:
    id: str
    role: str
    responsibilities: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TeamOrchestrationRequest:
    hypothesis_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()
    requested_roles: tuple[str, ...] = ()
    safety_profile: str = "research-only"
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TeamOrchestrationPlan:
    id: str
    team_members: tuple[TeamMemberSpec, ...]
    critique_steps: tuple[str, ...]
    evidence_budget: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)


class TeamOrchestrationProvider(Protocol):
    provider_id: str
    offline_supported: bool

    def plan(self, request: TeamOrchestrationRequest) -> TeamOrchestrationPlan:
        """Return a reviewable plan without starting live agents or providers."""
        ...

    def summarize(self, plan: TeamOrchestrationPlan) -> dict[str, object]:
        """Return artifact-ready orchestration metadata for Somatic runs."""
        ...


class AutoScientistsRuntimeNotEnabledError(RuntimeError):
    """Raised when a caller tries to enable the reference-only adapter."""


@dataclass(frozen=True)
class AutoScientistsTeamOrchestrationProviderConfig:
    enabled: bool = False
    mode: str = "mock"
    allow_runtime_execution: bool = False
    reference_only: bool = True
    fake_backed: bool = True
    staged_source_path: str = AUTOSCIENTISTS_SOURCE_PATH
    inspected_commit: str = AUTOSCIENTISTS_SOURCE_COMMIT
    license_status: str = AUTOSCIENTISTS_LICENSE_STATUS
    metadata: dict[str, object] = field(default_factory=dict)


class AutoScientistsTeamOrchestrationProvider:
    """Reference-only placeholder for future team orchestration.

    This class records the Somatic adapter boundary. It does not import,
    execute, install, or call AutoScientists, ClawInstitute, Claude Code, or
    any live provider runtime.
    """

    provider_id = "autoscientists-reference"
    offline_supported = True

    def __init__(self, config: AutoScientistsTeamOrchestrationProviderConfig | None = None):
        self.config = config or AutoScientistsTeamOrchestrationProviderConfig()

    def plan(self, request: TeamOrchestrationRequest) -> TeamOrchestrationPlan:
        self._raise_if_live_runtime_requested()
        requested_roles = request.requested_roles or (
            "GeneratorTeam",
            "FalsifierTeam",
            "EvidenceTeam",
            "SafetyTeam",
            "SynthesisTeam",
        )
        members = tuple(
            TeamMemberSpec(
                id=f"autoscientists-reference-{index}",
                role=role,
                responsibilities=(
                    "map local hypothesis references into a reviewable team plan",
                    "record critique before mock evidence budget allocation",
                ),
                risk_flags=(
                    "reference-only-license-unresolved",
                    "no-live-agent-runtime",
                ),
                metadata={
                    "reference_only": self.config.reference_only,
                    "fake_backed": self.config.fake_backed,
                    "runtime_enabled": False,
                    "hypothesis_refs": request.hypothesis_refs,
                },
            )
            for index, role in enumerate(requested_roles, start=1)
        )
        return TeamOrchestrationPlan(
            id="autoscientists-reference-plan",
            team_members=members,
            critique_steps=(
                "critique-before-evidence",
                "record-stall-or-no-stall-reason",
                "keep-external-runtime-disabled",
            ),
            evidence_budget={
                "currency": "mock-evidence-points",
                "external_evidence_spend_allowed": False,
                "decision": "allow-mock-budget-only",
            },
            metadata=self._metadata(request),
        )

    def summarize(self, plan: TeamOrchestrationPlan) -> dict[str, object]:
        self._raise_if_live_runtime_requested()
        return {
            "provider_id": self.provider_id,
            "plan_id": plan.id,
            "team_count": len(plan.team_members),
            "reference_only": self.config.reference_only,
            "fake_backed": self.config.fake_backed,
            "runtime_enabled": False,
            "runtime_import_allowed": False,
            "live_execution_allowed": False,
            "license_status": self.config.license_status,
            "staged_source_path": self.config.staged_source_path,
            "inspected_commit": self.config.inspected_commit,
            "critique_steps": list(plan.critique_steps),
            "evidence_budget": dict(plan.evidence_budget),
        }

    def _metadata(self, request: TeamOrchestrationRequest) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "mode": self.config.mode,
            "enabled": self.config.enabled,
            "reference_only": self.config.reference_only,
            "fake_backed": self.config.fake_backed,
            "runtime_enabled": False,
            "runtime_import_allowed": False,
            "live_execution_allowed": False,
            "license_status": self.config.license_status,
            "staged_source_path": self.config.staged_source_path,
            "inspected_commit": self.config.inspected_commit,
            "hypothesis_refs": request.hypothesis_refs,
            "evidence_refs": request.evidence_refs,
            "safety_profile": request.safety_profile,
        }

    def _raise_if_live_runtime_requested(self):
        live_requested = (
            self.config.enabled or self.config.mode != "mock" or self.config.allow_runtime_execution
        )
        if live_requested:
            raise AutoScientistsRuntimeNotEnabledError(
                "AutoScientists remains reference-only because no license file was found; "
                "live execution, runtime imports, dependency installs, and network calls "
                "are disabled."
            )
