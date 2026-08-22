from dataclasses import asdict, dataclass, field

from .baseline import BASELINE_CATEGORIES

INTERVENTION_CATEGORIES = (
    "rest_placeholder",
    "hydration_placeholder",
    "breathing_exercise_placeholder",
    "medication_placeholder_disabled",
    "clinician_review_placeholder",
    "environmental_change_placeholder",
)

DISABLED_INTERVENTION_CATEGORIES = (
    "medication_placeholder_disabled",
    "clinician_review_placeholder",
)

INTERVENTION_BOUNDARY_NOTES = (
    "Mock local intervention tag scaffold only.",
    "No recommendation or prescription is generated.",
    "No treatment recommendation, medical advice, or emergency triage is produced.",
    "Medication and clinician placeholders are disabled metadata only.",
    "Response evaluation is future planning only, not real monitoring.",
    "No reminders, automation, notification, or scheduling is created.",
)

INTERVENTION_FUTURE_REQUIREMENTS = (
    "explicit consent",
    "human review",
    "clinical review where applicable",
    "local storage controls",
    "safety gates",
    "no emergency-triage substitution",
)


@dataclass(frozen=True)
class InterventionWindow:
    id: str
    label: str
    relative_start: str
    relative_end: str
    window_status: str = "placeholder"
    future_comparison_window: str = "placeholder-follow-up-window"
    observation_only: bool = True
    no_real_scheduling: bool = True
    no_real_monitoring: bool = True
    no_notification_automation: bool = True
    no_reminder_automation: bool = True
    no_effectiveness_claim: bool = True
    limitations: tuple[str, ...] = (
        "Placeholder window only; no reminder, schedule, notification, or monitoring is created.",
    )

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class InterventionTag:
    id: str
    workflow_id: str
    category: str
    label: str
    categories: tuple[str, ...] = INTERVENTION_CATEGORIES
    category_statuses: tuple[dict[str, object], ...] = ()
    source: str = "fixed-sandbox-fixture"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    claim_effectiveness: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    future_real_use_requirements: tuple[str, ...] = INTERVENTION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = INTERVENTION_BOUNDARY_NOTES

    def __post_init__(self):
        if self.category not in INTERVENTION_CATEGORIES:
            raise ValueError(f"Unsupported intervention category: {self.category}")

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class InterventionContext:
    id: str
    workflow_id: str
    intervention_tag_id: str
    sensor_feature_set_id: str
    baseline_comparison_id: str
    personal_profile_id: str
    baseline_graph_id: str
    baseline_comparison_status: str
    baseline_status_counts: dict[str, int]
    artifact_refs: dict[str, str]
    artifact_hashes: dict[str, str]
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    claim_effectiveness: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    personal_data_exported: bool = False
    baseline_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    raw_rf_data_collected: bool = False
    raw_csi_data_collected: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    future_real_use_requirements: tuple[str, ...] = INTERVENTION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = INTERVENTION_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class ResponseEvaluationPlan:
    id: str
    workflow_id: str
    intervention_tag_id: str
    intervention_context_id: str
    future_comparison_window: str
    windows: tuple[InterventionWindow, ...]
    metrics_to_recheck: tuple[str, ...]
    baseline_categories_to_compare: tuple[str, ...]
    evaluation_status: str = "placeholder-future-planning-only"
    status_vocabulary: tuple[str, ...] = (
        "not_evaluated",
        "insufficient_data",
        "no_claim",
    )
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    claim_effectiveness: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    future_real_use_requirements: tuple[str, ...] = INTERVENTION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = INTERVENTION_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class MockInterventionLedger:
    id: str
    workflow_id: str
    intervention_tag_id: str
    intervention_context_id: str
    response_evaluation_plan_id: str
    entries: tuple[dict[str, object], ...]
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    claim_effectiveness: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    future_real_use_requirements: tuple[str, ...] = INTERVENTION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = INTERVENTION_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


def build_intervention_tag(
    workflow: dict[str, object] | None = None,
) -> InterventionTag:
    workflow_id = str((workflow or {}).get("id", "unknown-workflow"))
    return InterventionTag(
        id="intervention-tag-placeholder",
        workflow_id=workflow_id,
        category="rest_placeholder",
        label="Mock local rest event tag",
        category_statuses=_category_statuses(),
        metadata={
            "fixture_ref": "fixtures/baseline/intervention-tag-placeholder.json",
            "tag_status": "mock-event-label-only",
            "medication_placeholder_disabled": True,
            "clinician_review_placeholder_disabled": True,
        },
    )


def load_fake_intervention_tag(
    workflow: dict[str, object] | None = None,
) -> InterventionTag:
    return build_intervention_tag(workflow)


def build_intervention_context(
    workflow: dict[str, object],
    tag: InterventionTag,
    sensor_feature_set_payload: dict[str, object],
    baseline_comparison_payload: dict[str, object],
    personal_profile_payload: dict[str, object],
    baseline_graph_payload: dict[str, object],
    artifact_hashes: dict[str, str] | None = None,
) -> InterventionContext:
    workflow_id = str(workflow.get("id", tag.workflow_id))
    return InterventionContext(
        id="intervention-context-placeholder",
        workflow_id=workflow_id,
        intervention_tag_id=tag.id,
        sensor_feature_set_id=str(sensor_feature_set_payload.get("id")),
        baseline_comparison_id=str(baseline_comparison_payload.get("id")),
        personal_profile_id=str(personal_profile_payload.get("id")),
        baseline_graph_id=str(baseline_graph_payload.get("id")),
        baseline_comparison_status=str(
            baseline_comparison_payload.get("comparison_status", "not_evaluated")
        ),
        baseline_status_counts=dict(baseline_comparison_payload.get("status_counts", {})),
        artifact_refs={
            "sensor_feature_set": "artifacts/sensor_feature_set.json",
            "baseline_comparison": "artifacts/baseline_comparison.json",
            "personal_profile": "artifacts/personal_profile.json",
            "baseline_graph": "artifacts/baseline_graph.json",
        },
        artifact_hashes=dict(artifact_hashes or {}),
        metadata={
            "fixture_ref": "fixtures/baseline/intervention-context-placeholder.json",
            "context_status": "artifact-linking-only",
            "response_evaluation_status": "future-planning-only",
        },
    )


def build_response_evaluation_plan(
    workflow: dict[str, object],
    tag: InterventionTag,
    context: InterventionContext,
    baseline_comparison_payload: dict[str, object],
) -> ResponseEvaluationPlan:
    metrics_to_recheck = _metrics_to_recheck(baseline_comparison_payload)
    return ResponseEvaluationPlan(
        id="response-evaluation-plan-placeholder",
        workflow_id=str(workflow.get("id", tag.workflow_id)),
        intervention_tag_id=tag.id,
        intervention_context_id=context.id,
        future_comparison_window="placeholder-follow-up-window",
        windows=(
            InterventionWindow(
                id="intervention-window-placeholder",
                label="Placeholder follow-up comparison window",
                relative_start="placeholder-t+00m",
                relative_end="placeholder-t+30m",
            ),
        ),
        metrics_to_recheck=metrics_to_recheck,
        baseline_categories_to_compare=BASELINE_CATEGORIES,
        metadata={
            "fixture_ref": "fixtures/baseline/response-evaluation-plan-placeholder.json",
            "no_real_scheduling": True,
            "no_real_monitoring": True,
            "no_notification_or_reminder": True,
        },
    )


def build_mock_intervention_ledger(
    workflow: dict[str, object],
    tag: InterventionTag,
    context: InterventionContext,
    response_plan: ResponseEvaluationPlan,
) -> MockInterventionLedger:
    return MockInterventionLedger(
        id="mock-intervention-ledger-placeholder",
        workflow_id=str(workflow.get("id", tag.workflow_id)),
        intervention_tag_id=tag.id,
        intervention_context_id=context.id,
        response_evaluation_plan_id=response_plan.id,
        entries=(
            {
                "id": "mock-intervention-ledger-entry-placeholder",
                "intervention_tag_id": tag.id,
                "category": tag.category,
                "entry_status": "mock-tag-recorded",
                "real_intervention_performed": False,
                "recommendation_generated": False,
                "prescription_generated": False,
                "treatment_recommendation": False,
                "medical_advice": False,
                "claim_effectiveness": False,
                "real_monitoring": False,
                "real_scheduling": False,
            },
        ),
        metadata={
            "fixture_ref": "fixtures/baseline/mock-intervention-ledger-placeholder.json",
            "ledger_status": "local-placeholder-only",
            "applied_interventions": [],
        },
    )


def load_fake_intervention_plan(
    workflow: dict[str, object],
    sensor_feature_set_payload: dict[str, object],
    baseline_comparison_payload: dict[str, object],
    personal_profile_payload: dict[str, object],
    baseline_graph_payload: dict[str, object],
    artifact_hashes: dict[str, str] | None = None,
) -> tuple[
    InterventionTag,
    InterventionContext,
    ResponseEvaluationPlan,
    MockInterventionLedger,
]:
    tag = build_intervention_tag(workflow)
    context = build_intervention_context(
        workflow=workflow,
        tag=tag,
        sensor_feature_set_payload=sensor_feature_set_payload,
        baseline_comparison_payload=baseline_comparison_payload,
        personal_profile_payload=personal_profile_payload,
        baseline_graph_payload=baseline_graph_payload,
        artifact_hashes=artifact_hashes,
    )
    response_plan = build_response_evaluation_plan(
        workflow, tag, context, baseline_comparison_payload
    )
    ledger = build_mock_intervention_ledger(workflow, tag, context, response_plan)
    return tag, context, response_plan, ledger


def _category_statuses() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "category": category,
            "disabled": category in DISABLED_INTERVENTION_CATEGORIES,
            "status": (
                "disabled-placeholder-only"
                if category in DISABLED_INTERVENTION_CATEGORIES
                else "available-mock-label-only"
            ),
            "recommendation_generated": False,
            "prescription_generated": False,
            "treatment_recommendation": False,
            "medical_advice": False,
            "claim_effectiveness": False,
        }
        for category in INTERVENTION_CATEGORIES
    )


def _metrics_to_recheck(
    baseline_comparison_payload: dict[str, object],
) -> tuple[str, ...]:
    results = baseline_comparison_payload.get("results", ())
    if not isinstance(results, list | tuple):
        results = ()
    selected = [
        str(result.get("category"))
        for result in results
        if result.get("status") in {"outside_baseline", "insufficient_data"}
    ]
    if not selected:
        selected = list(BASELINE_CATEGORIES)
    return tuple(selected)


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


__all__ = [
    "DISABLED_INTERVENTION_CATEGORIES",
    "INTERVENTION_BOUNDARY_NOTES",
    "INTERVENTION_CATEGORIES",
    "INTERVENTION_FUTURE_REQUIREMENTS",
    "InterventionContext",
    "InterventionTag",
    "InterventionWindow",
    "MockInterventionLedger",
    "ResponseEvaluationPlan",
    "build_intervention_context",
    "build_intervention_tag",
    "build_mock_intervention_ledger",
    "build_response_evaluation_plan",
    "load_fake_intervention_plan",
    "load_fake_intervention_tag",
]
