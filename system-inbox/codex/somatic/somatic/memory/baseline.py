from dataclasses import asdict, dataclass, field

BASELINE_CATEGORIES = (
    "respiratory_rate",
    "movement_score",
    "sleep_state_estimate",
    "posture_state",
    "csi_confidence",
    "environmental_context",
    "notes_placeholder",
)

WITHIN_BASELINE = "within_baseline"
OUTSIDE_BASELINE = "outside_baseline"
INSUFFICIENT_DATA = "insufficient_data"

BASELINE_PRIVACY_REQUIREMENTS = (
    "explicit local storage consent",
    "data-locality review",
    "privacy review",
    "safety review",
    "human review",
    "retention and export controls",
    "separate opt-in configuration",
)

BASELINE_BOUNDARY_NOTES = (
    "Fake-backed local baseline scaffold only.",
    "No real health data is loaded.",
    "No real profile storage is performed.",
    "No diagnosis, treatment, or emergency triage is produced.",
)

_MISSING = object()


@dataclass(frozen=True)
class BaselinePrivacyBoundary:
    id: str = "baseline-privacy-boundary-placeholder"
    mock: bool = True
    local_first: bool = True
    private_by_default: bool = True
    fake_backed: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    baseline_data_exported: bool = False
    personal_data_exported: bool = False
    raw_sensor_data_collected: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    remote_upload: bool = False
    diagnosis: bool = False
    treatment_recommendation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    explicit_consent_required_for_real_mode: bool = True
    data_locality_review_required_for_real_mode: bool = True
    future_real_baseline_requirements: tuple[str, ...] = BASELINE_PRIVACY_REQUIREMENTS
    notes: tuple[str, ...] = BASELINE_BOUNDARY_NOTES

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PersonalProfile:
    id: str
    workflow_id: str
    profile_status: str = "placeholder"
    label: str = "local-placeholder-profile"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    personal_data_exported: bool = False
    network_calls: bool = False
    database_access: bool = False
    diagnosis: bool = False
    treatment_recommendation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    pii_fields: tuple[str, ...] = ()
    limitations: tuple[str, ...] = BASELINE_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BaselineWindow:
    id: str
    metric_id: str
    window_label: str
    value_kind: str
    min_value: float | int | None = None
    max_value: float | int | None = None
    expected_values: tuple[object, ...] = ()
    unit: str | None = None
    source: str = "fixed-sandbox-fixture"
    baseline_status: str = "placeholder"
    real_health_data_loaded: bool = False
    limitations: tuple[str, ...] = (
        "Placeholder window only; no real baseline samples are loaded.",
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BaselineMetric:
    id: str
    category: str
    modality: str
    value_kind: str
    unit: str | None
    windows: tuple[BaselineWindow, ...]
    source_refs: tuple[str, ...] = ()
    baseline_status: str = "placeholder"
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    real_health_data_loaded: bool = False
    clinical_interpretation: bool = False
    limitations: tuple[str, ...] = ("Metric exists for deterministic scaffold comparison only.",)

    def __post_init__(self):
        if self.category not in BASELINE_CATEGORIES:
            raise ValueError(f"Unsupported baseline category: {self.category}")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BaselineGraph:
    id: str
    workflow_id: str
    profile_id: str
    profile_ref: str
    privacy_boundary: BaselinePrivacyBoundary
    categories: tuple[str, ...]
    metrics: tuple[BaselineMetric, ...]
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    personal_data_exported: bool = False
    baseline_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    diagnosis: bool = False
    treatment_recommendation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    limitations: tuple[str, ...] = BASELINE_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BaselineComparison:
    id: str
    workflow_id: str
    profile_id: str
    baseline_graph_id: str
    feature_set_id: str
    comparison_status: str
    status_counts: dict[str, int]
    results: tuple[dict[str, object], ...]
    categories: tuple[str, ...] = BASELINE_CATEGORIES
    mock: bool = True
    offline: bool = True
    research_only: bool = True
    sandbox_only: bool = True
    fake_backed: bool = True
    local_only: bool = True
    comparison_only: bool = True
    real_health_data_loaded: bool = False
    real_profile_storage: bool = False
    personal_data_exported: bool = False
    baseline_data_exported: bool = False
    live_sensor_access: bool = False
    hardware_access: bool = False
    network_calls: bool = False
    database_access: bool = False
    diagnosis: bool = False
    treatment_recommendation: bool = False
    emergency_triage: bool = False
    real_monitoring: bool = False
    clinical_interpretation: bool = False
    medical_or_clinical_claim: bool = False
    summary: str = (
        "Fake-backed local baseline comparison using deterministic placeholder "
        "range and string matching only."
    )
    blocked_actions: tuple[str, ...] = (
        "No real health data loading.",
        "No real profile storage.",
        "No database or external memory write.",
        "No baseline export or remote upload.",
        "No diagnosis, treatment, or emergency triage.",
    )
    future_real_baseline_requirements: tuple[str, ...] = BASELINE_PRIVACY_REQUIREMENTS
    limitations: tuple[str, ...] = BASELINE_BOUNDARY_NOTES
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_personal_profile(workflow: dict[str, object] | None = None) -> PersonalProfile:
    workflow_id = str((workflow or {}).get("id", "unknown-workflow"))
    return PersonalProfile(
        id="personal-profile-placeholder",
        workflow_id=workflow_id,
        metadata={
            "fixture_ref": "fixtures/baseline/personal-profile-placeholder.json",
            "storage": "not-performed",
            "real_health_data": False,
        },
    )


def load_fake_personal_profile(
    workflow: dict[str, object] | None = None,
) -> PersonalProfile:
    return build_personal_profile(workflow)


def build_baseline_graph(
    profile: PersonalProfile,
    workflow: dict[str, object] | None = None,
) -> BaselineGraph:
    workflow_id = str((workflow or {}).get("id", profile.workflow_id))
    privacy_boundary = BaselinePrivacyBoundary()
    metrics = (
        _numeric_metric(
            "respiratory_rate",
            "csi",
            "breaths-per-minute-placeholder",
            12,
            18,
        ),
        _numeric_metric("movement_score", "wearable", "unitless-placeholder", 0.05, 0.15),
        _expected_metric(
            "sleep_state_estimate",
            "thermal",
            ("awake-placeholder", "resting-placeholder"),
        ),
        _expected_metric("posture_state", "video3d", ("upright-placeholder",)),
        _expected_metric("csi_confidence", "csi", ("not-applicable",)),
        _expected_metric(
            "environmental_context",
            "environmental",
            ("room-context-placeholder",),
        ),
        BaselineMetric(
            id="baseline-metric-notes-placeholder",
            category="notes_placeholder",
            modality="manual",
            value_kind="text",
            unit=None,
            windows=(),
            source_refs=("fixtures/baseline/baseline-graph-placeholder.json",),
            limitations=("Notes placeholder has no baseline window in Phase 7C.",),
        ),
    )
    return BaselineGraph(
        id="baseline-graph-placeholder",
        workflow_id=workflow_id,
        profile_id=profile.id,
        profile_ref="artifacts/personal_profile.json",
        privacy_boundary=privacy_boundary,
        categories=BASELINE_CATEGORIES,
        metrics=metrics,
        metadata={
            "fixture_ref": "fixtures/baseline/baseline-graph-placeholder.json",
            "privacy_boundary_ref": "fixtures/baseline/baseline-privacy-boundary-placeholder.json",
            "comparison_mode": "deterministic-placeholder",
        },
    )


def load_fake_baseline_graph(
    profile: PersonalProfile,
    workflow: dict[str, object] | None = None,
) -> BaselineGraph:
    return build_baseline_graph(profile, workflow)


def compare_feature_set_to_baseline(
    feature_set_payload: dict[str, object],
    baseline_graph: BaselineGraph,
) -> BaselineComparison:
    current_values = _current_feature_values(feature_set_payload)
    results = tuple(
        _compare_metric(metric, current_values.get(metric.category, _MISSING))
        for metric in baseline_graph.metrics
    )
    status_counts = baseline_status_counts(results)
    if status_counts[OUTSIDE_BASELINE]:
        comparison_status = OUTSIDE_BASELINE
    elif status_counts[INSUFFICIENT_DATA]:
        comparison_status = INSUFFICIENT_DATA
    else:
        comparison_status = WITHIN_BASELINE
    return BaselineComparison(
        id="baseline-comparison-placeholder",
        workflow_id=baseline_graph.workflow_id,
        profile_id=baseline_graph.profile_id,
        baseline_graph_id=baseline_graph.id,
        feature_set_id=str(feature_set_payload.get("id", "unknown-feature-set")),
        comparison_status=comparison_status,
        status_counts=status_counts,
        results=results,
        metadata={
            "source_feature_set_ref": "artifacts/sensor_feature_set.json",
            "baseline_graph_ref": "artifacts/baseline_graph.json",
            "status_vocabulary": (
                WITHIN_BASELINE,
                OUTSIDE_BASELINE,
                INSUFFICIENT_DATA,
            ),
        },
    )


def baseline_status_counts(results: tuple[dict[str, object], ...]) -> dict[str, int]:
    counts = {
        WITHIN_BASELINE: 0,
        OUTSIDE_BASELINE: 0,
        INSUFFICIENT_DATA: 0,
    }
    for result in results:
        status = result.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _numeric_metric(
    category: str,
    modality: str,
    unit: str,
    min_value: float | int,
    max_value: float | int,
) -> BaselineMetric:
    metric_id = f"baseline-metric-{category.replace('_', '-')}"
    window = BaselineWindow(
        id=f"baseline-window-{category.replace('_', '-')}-placeholder",
        metric_id=metric_id,
        window_label="phase-7c-placeholder-window",
        value_kind="numeric",
        min_value=min_value,
        max_value=max_value,
        unit=unit,
    )
    return BaselineMetric(
        id=metric_id,
        category=category,
        modality=modality,
        value_kind="numeric",
        unit=unit,
        windows=(window,),
        source_refs=("fixtures/baseline/baseline-graph-placeholder.json",),
    )


def _expected_metric(
    category: str,
    modality: str,
    expected_values: tuple[object, ...],
) -> BaselineMetric:
    metric_id = f"baseline-metric-{category.replace('_', '-')}"
    window = BaselineWindow(
        id=f"baseline-window-{category.replace('_', '-')}-placeholder",
        metric_id=metric_id,
        window_label="phase-7c-placeholder-window",
        value_kind="categorical",
        expected_values=expected_values,
    )
    return BaselineMetric(
        id=metric_id,
        category=category,
        modality=modality,
        value_kind="categorical",
        unit=None,
        windows=(window,),
        source_refs=("fixtures/baseline/baseline-graph-placeholder.json",),
    )


def _compare_metric(metric: BaselineMetric, current_value: object) -> dict[str, object]:
    window = metric.windows[0] if metric.windows else None
    base = {
        "metric_id": metric.id,
        "category": metric.category,
        "modality": metric.modality,
        "value_kind": metric.value_kind,
        "unit": metric.unit,
        "baseline_window_id": window.id if window else None,
        "baseline_status": metric.baseline_status,
        "current_value_available": current_value is not _MISSING,
        "current_value": None if current_value is _MISSING else current_value,
        "baseline_min": window.min_value if window else None,
        "baseline_max": window.max_value if window else None,
        "expected_values": list(window.expected_values) if window else [],
    }
    if current_value is _MISSING:
        return base | {
            "status": INSUFFICIENT_DATA,
            "direction": "missing_current_value",
            "deviation": None,
            "deviation_note": (
                f"{INSUFFICIENT_DATA}: no current placeholder value was "
                f"available for {metric.category}."
            ),
        }
    if window is None:
        return base | {
            "status": INSUFFICIENT_DATA,
            "direction": "missing_baseline_window",
            "deviation": None,
            "deviation_note": (
                f"{INSUFFICIENT_DATA}: no placeholder baseline window is "
                f"available for {metric.category}."
            ),
        }
    if window.min_value is not None or window.max_value is not None:
        return _compare_numeric(base, current_value, window)
    if window.expected_values:
        return _compare_expected(base, current_value, window)
    return base | {
        "status": INSUFFICIENT_DATA,
        "direction": "missing_baseline_values",
        "deviation": None,
        "deviation_note": (
            f"{INSUFFICIENT_DATA}: placeholder baseline values are not "
            f"available for {metric.category}."
        ),
    }


def _compare_numeric(
    base: dict[str, object],
    current_value: object,
    window: BaselineWindow,
) -> dict[str, object]:
    if not isinstance(current_value, int | float):
        return base | {
            "status": INSUFFICIENT_DATA,
            "direction": "non_numeric_current_value",
            "deviation": None,
            "deviation_note": (f"{INSUFFICIENT_DATA}: current placeholder value is not numeric."),
        }
    if window.min_value is not None and current_value < window.min_value:
        delta = round(float(window.min_value) - float(current_value), 6)
        return base | {
            "status": OUTSIDE_BASELINE,
            "direction": "below_placeholder_window",
            "deviation": delta,
            "deviation_note": (
                f"{OUTSIDE_BASELINE}: current placeholder value is below "
                f"the local placeholder window by {delta}."
            ),
        }
    if window.max_value is not None and current_value > window.max_value:
        delta = round(float(current_value) - float(window.max_value), 6)
        return base | {
            "status": OUTSIDE_BASELINE,
            "direction": "above_placeholder_window",
            "deviation": delta,
            "deviation_note": (
                f"{OUTSIDE_BASELINE}: current placeholder value is above "
                f"the local placeholder window by {delta}."
            ),
        }
    return base | {
        "status": WITHIN_BASELINE,
        "direction": "inside_placeholder_window",
        "deviation": 0,
        "deviation_note": (
            f"{WITHIN_BASELINE}: current placeholder value is inside the local placeholder window."
        ),
    }


def _compare_expected(
    base: dict[str, object],
    current_value: object,
    window: BaselineWindow,
) -> dict[str, object]:
    if current_value in window.expected_values:
        return base | {
            "status": WITHIN_BASELINE,
            "direction": "matches_placeholder_value",
            "deviation": 0,
            "deviation_note": (
                f"{WITHIN_BASELINE}: current placeholder value matches an "
                f"expected placeholder value."
            ),
        }
    return base | {
        "status": OUTSIDE_BASELINE,
        "direction": "differs_from_placeholder_values",
        "deviation": None,
        "deviation_note": (
            f"{OUTSIDE_BASELINE}: current placeholder value differs from "
            f"expected placeholder values."
        ),
    }


def _current_feature_values(feature_set_payload: dict[str, object]) -> dict[str, object]:
    features = feature_set_payload.get("features", {})
    if not isinstance(features, dict):
        features = {}
    csi_features = (
        feature_set_payload.get("metadata", {})
        .get("csi", {})
        .get("feature_set", {})
        .get("features", {})
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


__all__ = [
    "BASELINE_CATEGORIES",
    "BASELINE_PRIVACY_REQUIREMENTS",
    "INSUFFICIENT_DATA",
    "OUTSIDE_BASELINE",
    "WITHIN_BASELINE",
    "BaselineComparison",
    "BaselineGraph",
    "BaselineMetric",
    "BaselinePrivacyBoundary",
    "BaselineWindow",
    "PersonalProfile",
    "baseline_status_counts",
    "build_baseline_graph",
    "build_personal_profile",
    "compare_feature_set_to_baseline",
    "load_fake_baseline_graph",
    "load_fake_personal_profile",
]
