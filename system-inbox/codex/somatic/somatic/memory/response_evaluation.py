from dataclasses import asdict, dataclass, field

from .baseline import BASELINE_CATEGORIES

TOWARD_BASELINE = "toward_baseline"
AWAY_FROM_BASELINE = "away_from_baseline"
UNCHANGED = "unchanged"
INSUFFICIENT_DATA = "insufficient_data"

RESPONSE_TREND_STATUSES = (
    TOWARD_BASELINE,
    AWAY_FROM_BASELINE,
    UNCHANGED,
    INSUFFICIENT_DATA,
)

RESPONSE_EVALUATION_BOUNDARY_NOTES = (
    "Fake-backed local research-only planning only.",
    "Response trend labels are fixture trend labels only.",
    "No intervention effectiveness is claimed.",
    "No recommendation, prescription, treatment recommendation, medical advice, "
    "diagnosis, or emergency triage is produced.",
    "No reminders, automation, notification, scheduling, or real monitoring is created.",
)

RESPONSE_EVALUATION_FUTURE_REQUIREMENTS = (
    "explicit consent",
    "human review",
    "clinical review where applicable",
    "local storage controls",
    "privacy gates",
    "safety gates",
    "real scheduling and monitoring safety review",
    "no emergency-triage substitution",
)


@dataclass(frozen=True)
class FollowUpObservationWindow:
    id: str
    workflow_id: str
    source_plan_id: str
    intervention_tag_id: str
    intervention_context_id: str
    metrics_to_recheck: tuple[str, ...]
    baseline_categories_to_compare: tuple[str, ...]
    relative_start: str = "placeholder-t+30m"
    relative_end: str = "placeholder-t+60m"
    window_status: str = "placeholder-follow-up-window"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    effectiveness_claim: bool = False
    claim_effectiveness: bool = False
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_response_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    future_real_use_requirements: tuple[str, ...] = RESPONSE_EVALUATION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = RESPONSE_EVALUATION_BOUNDARY_NOTES

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class FollowUpSensorSnapshot:
    id: str
    workflow_id: str
    window_id: str
    source_feature_set_id: str
    features: dict[str, object]
    provider_id: str = "sandbox-sensor-provider"
    snapshot_status: str = "fixed-follow-up-placeholder"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    effectiveness_claim: bool = False
    claim_effectiveness: bool = False
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_response_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    future_real_use_requirements: tuple[str, ...] = RESPONSE_EVALUATION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = RESPONSE_EVALUATION_BOUNDARY_NOTES

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class ResponseComparison:
    id: str
    workflow_id: str
    follow_up_sensor_snapshot_id: str
    sensor_feature_set_id: str
    baseline_comparison_id: str
    intervention_tag_id: str
    response_evaluation_plan_id: str
    personal_profile_id: str
    baseline_graph_id: str
    results: tuple[dict[str, object], ...]
    trend_counts: dict[str, int]
    artifact_refs: dict[str, str]
    artifact_hashes: dict[str, str]
    trend_status_vocabulary: tuple[str, ...] = RESPONSE_TREND_STATUSES
    comparison_status: str = "fixture-trend-labels-only"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    effectiveness_claim: bool = False
    claim_effectiveness: bool = False
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_response_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    future_real_use_requirements: tuple[str, ...] = RESPONSE_EVALUATION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = RESPONSE_EVALUATION_BOUNDARY_NOTES

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class ResponseEvaluationSummary:
    id: str
    workflow_id: str
    follow_up_observation_window_id: str
    follow_up_sensor_snapshot_id: str
    response_comparison_id: str
    trend_counts: dict[str, int]
    status_by_category: dict[str, str]
    toward_baseline_categories: tuple[str, ...]
    away_from_baseline_categories: tuple[str, ...]
    unchanged_categories: tuple[str, ...]
    insufficient_data_categories: tuple[str, ...]
    trend_status_vocabulary: tuple[str, ...] = RESPONSE_TREND_STATUSES
    summary_status: str = "fixture-trend-labels-only"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    effectiveness_claim: bool = False
    claim_effectiveness: bool = False
    recommendation_generated: bool = False
    prescription_generated: bool = False
    treatment_recommendation: bool = False
    medical_advice: bool = False
    real_intervention_performed: bool = False
    real_health_data_loaded: bool = False
    personal_data_exported: bool = False
    hardware_access: bool = False
    live_sensor_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    external_memory: bool = False
    diagnosis: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    real_response_monitoring: bool = False
    real_scheduling: bool = False
    notification_automation: bool = False
    reminder_automation: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    future_real_use_requirements: tuple[str, ...] = RESPONSE_EVALUATION_FUTURE_REQUIREMENTS
    limitations: tuple[str, ...] = RESPONSE_EVALUATION_BOUNDARY_NOTES

    def to_dict(self) -> dict[str, object]:
        return _json_ready(asdict(self))


def build_follow_up_observation_window(
    workflow: dict[str, object],
    response_evaluation_plan_payload: dict[str, object],
) -> FollowUpObservationWindow:
    return FollowUpObservationWindow(
        id="follow-up-observation-window-placeholder",
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        source_plan_id=str(response_evaluation_plan_payload.get("id")),
        intervention_tag_id=str(response_evaluation_plan_payload.get("intervention_tag_id")),
        intervention_context_id=str(
            response_evaluation_plan_payload.get("intervention_context_id")
        ),
        metrics_to_recheck=tuple(response_evaluation_plan_payload.get("metrics_to_recheck", ())),
        baseline_categories_to_compare=tuple(
            response_evaluation_plan_payload.get(
                "baseline_categories_to_compare", BASELINE_CATEGORIES
            )
        ),
        metadata={
            "fixture_ref": "fixtures/baseline/follow-up-observation-window-placeholder.json",
            "response_evaluation": "future-planning-only",
            "real_scheduling": False,
            "real_monitoring": False,
        },
    )


def build_follow_up_sensor_snapshot(
    workflow: dict[str, object],
    follow_up_window: FollowUpObservationWindow | dict[str, object],
    sensor_feature_set_payload: dict[str, object],
) -> FollowUpSensorSnapshot:
    window_payload = _payload(follow_up_window)
    original_features = sensor_feature_set_payload.get("features", {})
    if not isinstance(original_features, dict):
        original_features = {}
    features = dict(original_features)
    features.update(
        {
            "respiratory_rate": 14,
            "movement_score": 0.14,
            "posture_state": "upright-placeholder",
            "sleep_state_estimate": "awake-placeholder",
            "csi_confidence": "not-applicable",
            "environmental_context_placeholder": "room-context-placeholder",
            "audio_event_placeholder": "none-observed-placeholder",
        }
    )
    features.pop("notes_placeholder", None)
    return FollowUpSensorSnapshot(
        id="follow-up-sensor-snapshot-placeholder",
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        window_id=str(window_payload.get("id")),
        source_feature_set_id=str(sensor_feature_set_payload.get("id")),
        features=features,
        metadata={
            "fixture_ref": "fixtures/baseline/follow-up-sensor-snapshot-placeholder.json",
            "source_feature_set_ref": "artifacts/sensor_feature_set.json",
            "movement_score_generation": "fixed-placeholder-toward-baseline",
            "real_capture": False,
        },
    )


def build_response_comparison(
    workflow: dict[str, object],
    follow_up_snapshot: FollowUpSensorSnapshot | dict[str, object],
    sensor_feature_set_payload: dict[str, object],
    baseline_comparison_payload: dict[str, object],
    intervention_tag_payload: dict[str, object],
    response_evaluation_plan_payload: dict[str, object],
    personal_profile_payload: dict[str, object],
    baseline_graph_payload: dict[str, object],
    artifact_hashes: dict[str, str] | None = None,
) -> ResponseComparison:
    snapshot_payload = _payload(follow_up_snapshot)
    pre_values = _feature_values(sensor_feature_set_payload)
    follow_values = _feature_values(snapshot_payload)
    baseline_results = {
        result.get("category"): result
        for result in baseline_comparison_payload.get("results", ())
        if isinstance(result, dict)
    }
    results = tuple(
        _compare_metric(metric, pre_values, follow_values, baseline_results)
        for metric in baseline_graph_payload.get("metrics", ())
        if isinstance(metric, dict)
    )
    trend_counts = _trend_counts(results)
    return ResponseComparison(
        id="response-comparison-placeholder",
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        follow_up_sensor_snapshot_id=str(snapshot_payload.get("id")),
        sensor_feature_set_id=str(sensor_feature_set_payload.get("id")),
        baseline_comparison_id=str(baseline_comparison_payload.get("id")),
        intervention_tag_id=str(intervention_tag_payload.get("id")),
        response_evaluation_plan_id=str(response_evaluation_plan_payload.get("id")),
        personal_profile_id=str(personal_profile_payload.get("id")),
        baseline_graph_id=str(baseline_graph_payload.get("id")),
        results=results,
        trend_counts=trend_counts,
        artifact_refs={
            "sensor_feature_set": "artifacts/sensor_feature_set.json",
            "baseline_comparison": "artifacts/baseline_comparison.json",
            "intervention_tag": "artifacts/intervention_tag.json",
            "response_evaluation_plan": "artifacts/response_evaluation_plan.json",
            "personal_profile": "artifacts/personal_profile.json",
            "baseline_graph": "artifacts/baseline_graph.json",
        },
        artifact_hashes=dict(artifact_hashes or {}),
        metadata={
            "fixture_ref": "fixtures/baseline/response-comparison-placeholder.json",
            "comparison": "mechanical-placeholder-comparison",
            "effectiveness_claim": False,
        },
    )


def build_response_evaluation_summary(
    workflow: dict[str, object],
    follow_up_window: FollowUpObservationWindow | dict[str, object],
    follow_up_snapshot: FollowUpSensorSnapshot | dict[str, object],
    response_comparison: ResponseComparison | dict[str, object],
) -> ResponseEvaluationSummary:
    window_payload = _payload(follow_up_window)
    snapshot_payload = _payload(follow_up_snapshot)
    comparison_payload = _payload(response_comparison)
    results = tuple(comparison_payload.get("results", ()))
    status_by_category = {
        str(result.get("category")): str(result.get("trend_label"))
        for result in results
        if isinstance(result, dict)
    }
    return ResponseEvaluationSummary(
        id="response-evaluation-summary-placeholder",
        workflow_id=str(workflow.get("id", "unknown-workflow")),
        follow_up_observation_window_id=str(window_payload.get("id")),
        follow_up_sensor_snapshot_id=str(snapshot_payload.get("id")),
        response_comparison_id=str(comparison_payload.get("id")),
        trend_counts=dict(comparison_payload.get("trend_counts", _trend_counts(results))),
        status_by_category=status_by_category,
        toward_baseline_categories=tuple(
            category for category, status in status_by_category.items() if status == TOWARD_BASELINE
        ),
        away_from_baseline_categories=tuple(
            category
            for category, status in status_by_category.items()
            if status == AWAY_FROM_BASELINE
        ),
        unchanged_categories=tuple(
            category for category, status in status_by_category.items() if status == UNCHANGED
        ),
        insufficient_data_categories=tuple(
            category
            for category, status in status_by_category.items()
            if status == INSUFFICIENT_DATA
        ),
        metadata={
            "fixture_ref": "fixtures/baseline/response-evaluation-summary-placeholder.json",
            "summary": "fixture-trend-labels-only",
            "no_effectiveness_claim": True,
        },
    )


def load_fake_response_evaluation(
    workflow: dict[str, object],
    sensor_feature_set_payload: dict[str, object],
    baseline_comparison_payload: dict[str, object],
    intervention_tag_payload: dict[str, object],
    response_evaluation_plan_payload: dict[str, object],
    personal_profile_payload: dict[str, object],
    baseline_graph_payload: dict[str, object],
    artifact_hashes: dict[str, str] | None = None,
) -> tuple[
    FollowUpObservationWindow,
    FollowUpSensorSnapshot,
    ResponseComparison,
    ResponseEvaluationSummary,
]:
    window = build_follow_up_observation_window(workflow, response_evaluation_plan_payload)
    snapshot = build_follow_up_sensor_snapshot(workflow, window, sensor_feature_set_payload)
    comparison = build_response_comparison(
        workflow=workflow,
        follow_up_snapshot=snapshot,
        sensor_feature_set_payload=sensor_feature_set_payload,
        baseline_comparison_payload=baseline_comparison_payload,
        intervention_tag_payload=intervention_tag_payload,
        response_evaluation_plan_payload=response_evaluation_plan_payload,
        personal_profile_payload=personal_profile_payload,
        baseline_graph_payload=baseline_graph_payload,
        artifact_hashes=artifact_hashes,
    )
    summary = build_response_evaluation_summary(
        workflow=workflow,
        follow_up_window=window,
        follow_up_snapshot=snapshot,
        response_comparison=comparison,
    )
    return window, snapshot, comparison, summary


def _compare_metric(
    metric: dict[str, object],
    pre_values: dict[str, object],
    follow_values: dict[str, object],
    baseline_results: dict[object, dict[str, object]],
) -> dict[str, object]:
    category = str(metric.get("category"))
    window = _first_window(metric)
    pre_value = pre_values.get(category, _Missing.VALUE)
    follow_value = follow_values.get(category, _Missing.VALUE)
    baseline_result = baseline_results.get(category, {})
    base = {
        "category": category,
        "metric_id": metric.get("id"),
        "modality": metric.get("modality"),
        "value_kind": metric.get("value_kind"),
        "unit": metric.get("unit"),
        "baseline_status": metric.get("baseline_status"),
        "pre_status": baseline_result.get("status", INSUFFICIENT_DATA),
        "pre_value_available": pre_value is not _Missing.VALUE,
        "pre_value": None if pre_value is _Missing.VALUE else pre_value,
        "follow_up_value_available": follow_value is not _Missing.VALUE,
        "follow_up_value": None if follow_value is _Missing.VALUE else follow_value,
        "baseline_window_id": window.get("id") if window else None,
        "baseline_min": window.get("min_value") if window else None,
        "baseline_max": window.get("max_value") if window else None,
        "expected_values": list(window.get("expected_values", ())) if window else [],
        "effectiveness_claim": False,
        "claim_effectiveness": False,
        "recommendation_generated": False,
        "medical_advice": False,
    }
    if pre_value is _Missing.VALUE or follow_value is _Missing.VALUE or not window:
        return _result(
            base,
            INSUFFICIENT_DATA,
            f"{INSUFFICIENT_DATA}: fixture value or placeholder baseline window is unavailable.",
        )
    if window.get("min_value") is not None or window.get("max_value") is not None:
        if not isinstance(pre_value, int | float) or not isinstance(follow_value, int | float):
            return _result(
                base,
                INSUFFICIENT_DATA,
                f"{INSUFFICIENT_DATA}: numeric placeholder comparison is unavailable.",
            )
        pre_distance = _numeric_distance(pre_value, window)
        follow_distance = _numeric_distance(follow_value, window)
        if follow_distance < pre_distance:
            status = TOWARD_BASELINE
        elif follow_distance > pre_distance:
            status = AWAY_FROM_BASELINE
        else:
            status = UNCHANGED
        return _result(
            base
            | {
                "pre_distance_from_placeholder_window": pre_distance,
                "follow_up_distance_from_placeholder_window": follow_distance,
            },
            status,
            f"{status}: fixture trend label relative to a placeholder baseline only.",
        )
    expected_values = tuple(window.get("expected_values", ()))
    if not expected_values:
        return _result(
            base,
            INSUFFICIENT_DATA,
            f"{INSUFFICIENT_DATA}: no placeholder expected values are available.",
        )
    pre_match = pre_value in expected_values
    follow_match = follow_value in expected_values
    if not pre_match and follow_match:
        status = TOWARD_BASELINE
    elif pre_match and not follow_match:
        status = AWAY_FROM_BASELINE
    else:
        status = UNCHANGED
    return _result(
        base,
        status,
        f"{status}: categorical fixture trend label relative to placeholder values only.",
    )


def _result(base: dict[str, object], status: str, note: str) -> dict[str, object]:
    return base | {
        "trend_label": status,
        "trend_status": status,
        "comparison_note": note,
        "effectiveness_claim": False,
        "medical_or_clinical_claim": False,
    }


def _first_window(metric: dict[str, object]) -> dict[str, object] | None:
    windows = metric.get("windows", ())
    if isinstance(windows, list | tuple) and windows:
        first = windows[0]
        if isinstance(first, dict):
            return first
    return None


def _numeric_distance(value: float | int, window: dict[str, object]) -> float:
    minimum = window.get("min_value")
    maximum = window.get("max_value")
    if isinstance(minimum, int | float) and value < minimum:
        return round(float(minimum) - float(value), 6)
    if isinstance(maximum, int | float) and value > maximum:
        return round(float(value) - float(maximum), 6)
    return 0.0


def _trend_counts(results) -> dict[str, int]:
    counts = {status: 0 for status in RESPONSE_TREND_STATUSES}
    for result in results:
        if not isinstance(result, dict):
            continue
        status = result.get("trend_label")
        if status in counts:
            counts[status] += 1
    return counts


def _feature_values(payload: dict[str, object]) -> dict[str, object]:
    features = payload.get("features", {})
    if not isinstance(features, dict):
        features = {}
    csi_features = (
        payload.get("metadata", {}).get("csi", {}).get("feature_set", {}).get("features", {})
    )
    if not isinstance(csi_features, dict):
        csi_features = {}
    values = {}
    for category in (
        "respiratory_rate",
        "movement_score",
        "sleep_state_estimate",
        "posture_state",
    ):
        if category in features:
            values[category] = features[category]
    if "environmental_context" in features:
        values["environmental_context"] = features["environmental_context"]
    elif "environmental_context_placeholder" in features:
        values["environmental_context"] = features["environmental_context_placeholder"]
    if "csi_confidence" in features:
        values["csi_confidence"] = features["csi_confidence"]
    elif "confidence" in csi_features:
        values["csi_confidence"] = csi_features["confidence"]
    if "notes_placeholder" in features:
        values["notes_placeholder"] = features["notes_placeholder"]
    return values


def _payload(value):
    return value.to_dict() if hasattr(value, "to_dict") else dict(value)


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


class _Missing:
    VALUE = object()


__all__ = [
    "AWAY_FROM_BASELINE",
    "INSUFFICIENT_DATA",
    "RESPONSE_EVALUATION_BOUNDARY_NOTES",
    "RESPONSE_EVALUATION_FUTURE_REQUIREMENTS",
    "RESPONSE_TREND_STATUSES",
    "TOWARD_BASELINE",
    "UNCHANGED",
    "FollowUpObservationWindow",
    "FollowUpSensorSnapshot",
    "ResponseComparison",
    "ResponseEvaluationSummary",
    "build_follow_up_observation_window",
    "build_follow_up_sensor_snapshot",
    "build_response_comparison",
    "build_response_evaluation_summary",
    "load_fake_response_evaluation",
]
