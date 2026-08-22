from dataclasses import dataclass, field

ROBIN_SOURCE_PATH = "C:\\AI\\external-sources\\somatic\\robin"
ROBIN_SOURCE_COMMIT = "4a5cce310f3bc7663a67117db88af43b84733ffe"
AVIARY_SOURCE_PATH = "C:\\AI\\external-sources\\somatic\\aviary"
AVIARY_SOURCE_COMMIT = "826577f332a02ec2f5883cdb042fb12f14b4c7b3"
LDP_SOURCE_PATH = "C:\\AI\\external-sources\\somatic\\ldp"
LDP_SOURCE_COMMIT = "d49850ff3addb8369df062d345ea99991b7b200c"
FUTUREHOUSE_LICENSE = "Apache-2.0"


class RobinRuntimeNotEnabledError(RuntimeError):
    """Raised when a caller tries to enable the reference-only Robin scaffold."""


@dataclass(frozen=True)
class RobinProviderConfig:
    enabled: bool = False
    mode: str = "mock"
    allow_runtime_execution: bool = False
    reference_only: bool = True
    fake_backed: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RobinPlanRequest:
    workflow_id: str
    goal: str
    evidence_refs: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RobinReferencePlan:
    id: str
    workflow_id: str
    crow: dict[str, object]
    falcon: dict[str, object]
    finch: dict[str, object]
    environment: dict[str, object]
    learning_process: dict[str, object]
    dependencies: dict[str, object]
    metadata: dict[str, object] = field(default_factory=dict)


class RobinProvider:
    """Reference-only FutureHouse Robin stack scaffold.

    This provider records how Robin, Aviary, and LDP concepts map to Somatic.
    It does not import or execute those packages, call Edison, call external
    LLM providers, run PaperQA2, or start a live environment.
    """

    provider_id = "futurehouse-robin-reference"
    offline_supported = True

    def __init__(self, config: RobinProviderConfig | None = None):
        self.config = config or RobinProviderConfig()

    def plan(self, request: RobinPlanRequest) -> RobinReferencePlan:
        self._raise_if_live_runtime_requested()
        return RobinReferencePlan(
            id="futurehouse-robin-reference-plan",
            workflow_id=request.workflow_id,
            crow={
                "reference": "Robin Crow literature and hypothesis-report agents",
                "maps_to": "LiteratureProvider",
                "somatic_artifact": "artifacts/crow_literature_context.json",
                "runtime_enabled": False,
            },
            falcon={
                "reference": "Robin Falcon therapeutic-candidate report role",
                "maps_to": "MeasurementPlan",
                "somatic_artifact": "artifacts/falcon_measurement_plan.json",
                "runtime_enabled": False,
            },
            finch={
                "reference": "Robin Finch data-analysis trajectory",
                "maps_to": "StructuredVerdict",
                "somatic_artifacts": (
                    "artifacts/finch_toolbelt_summary.json",
                    "artifacts/structured_verdict.json",
                ),
                "runtime_enabled": False,
            },
            environment={
                "reference": "Aviary-like Environment reset/step/message/tool boundary",
                "maps_to": "future provider execution envelope",
                "runtime_enabled": False,
            },
            learning_process={
                "reference": "LDP-like agent state/action/value and rollout boundary",
                "maps_to": "future optional optimization lane",
                "runtime_enabled": False,
            },
            dependencies={
                "edison": "not-used-by-somatic-core",
                "openai": "not-used-by-somatic-core",
                "anthropic": "not-used-by-somatic-core",
                "paperqa2": "disabled-literature-provider-scaffold-only",
            },
            metadata=self._metadata(request),
        )

    def summarize(self, plan: RobinReferencePlan) -> dict[str, object]:
        self._raise_if_live_runtime_requested()
        return {
            "provider_id": self.provider_id,
            "plan_id": plan.id,
            "workflow_id": plan.workflow_id,
            "reference_only": self.config.reference_only,
            "fake_backed": self.config.fake_backed,
            "runtime_enabled": False,
            "runtime_import_allowed": False,
            "live_execution_allowed": False,
            "licenses": {
                "robin": FUTUREHOUSE_LICENSE,
                "aviary": FUTUREHOUSE_LICENSE,
                "ldp": FUTUREHOUSE_LICENSE,
            },
            "source_commits": {
                "robin": ROBIN_SOURCE_COMMIT,
                "aviary": AVIARY_SOURCE_COMMIT,
                "ldp": LDP_SOURCE_COMMIT,
            },
            "attachments": {
                "crow": dict(plan.crow),
                "falcon": dict(plan.falcon),
                "finch": dict(plan.finch),
                "environment": dict(plan.environment),
                "learning_process": dict(plan.learning_process),
            },
            "dependencies": dict(plan.dependencies),
        }

    def _metadata(self, request: RobinPlanRequest) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "mode": self.config.mode,
            "enabled": self.config.enabled,
            "reference_only": self.config.reference_only,
            "fake_backed": self.config.fake_backed,
            "runtime_enabled": False,
            "runtime_import_allowed": False,
            "live_execution_allowed": False,
            "source_paths": {
                "robin": ROBIN_SOURCE_PATH,
                "aviary": AVIARY_SOURCE_PATH,
                "ldp": LDP_SOURCE_PATH,
            },
            "source_commits": {
                "robin": ROBIN_SOURCE_COMMIT,
                "aviary": AVIARY_SOURCE_COMMIT,
                "ldp": LDP_SOURCE_COMMIT,
            },
            "goal": request.goal,
            "evidence_refs": request.evidence_refs,
        }

    def _raise_if_live_runtime_requested(self):
        live_requested = (
            self.config.enabled or self.config.mode != "mock" or self.config.allow_runtime_execution
        )
        if live_requested:
            raise RobinRuntimeNotEnabledError(
                "FutureHouse Robin/Aviary/LDP remain reference-only in Phase 5F; "
                "runtime imports, Edison/API calls, dependency installs, and live "
                "execution are disabled."
            )
