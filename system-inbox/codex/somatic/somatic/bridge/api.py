"""JSON API for the local UI. Reuses engine functions; never bypasses gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from somatic.advisory.adapter import AdvisoryModelConfig
from somatic.bench.runner import run_bench
from somatic.bridge.serialize import (
    RAW_SENSOR_KEYS,
    evidence_loop_to_dict,
    sanitize_sensor_features,
    science_report_to_dict,
)
from somatic.consent.scopes import (
    AI_ADVISORY,
    ANALYSIS_INSIGHT,
    AUTONOMOUS_RESEARCH,
    CONSENT_SCOPES,
    DATA_INGESTION,
    PROACTIVE_SUGGESTIONS,
    PROFESSIONAL_SHARING,
    REMEDY_LIBRARY,
    get_scope,
)
from somatic.consent.store import (
    default_consent_path,
    erase_stored_ledger,
    load_ledger,
    save_ledger,
)
from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
from somatic.experiments.n_of_1 import InterventionTag, evaluate_n_of_1
from somatic.experiments.store import (
    append_tag,
    default_experiment_path,
    erase_stored_tags,
    load_tags,
)
from somatic.flows.analyze import analyze_user_data
from somatic.flows.share import render_fhir_bundle, render_professional_summary
from somatic.ingest.apple_health import ingest_apple_health_xml
from somatic.ingest.csv import ingest_csv_text
from somatic.ingest.packet import IngestedPacket, normalize_observed_at
from somatic.ingest.store import (
    append_readings,
    default_ingest_path,
    erase_stored_readings,
    load_readings,
)
from somatic.parasite import ask_parasite
from somatic.presence import REASONING_PATH_PARTICIPANT, RENDER_ONLY, render_presence
from somatic.presence.avatar import PERSONAS
from somatic.remedy import lookup_remedy
from somatic.research import HONEST_NULL, run_research_loop
from somatic.safety.core import (
    CRISIS_GUIDANCE,
    CRISIS_LINE_POLICY,
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    LANGUAGE_SCOPE,
    PROFESSIONAL_ROUTING,
    ConsentRequiredError,
    emergency_screen,
    require_consent,
)
from somatic.science.biosecurity import screen_biosecurity
from somatic.science.harness import run_science_loop
from somatic.sensors.field import HARDWARE_VALIDATION, field_snapshot
from somatic.sensors.fusion import fuse_csi_units, fuse_rf_vision
from somatic.sensors.live_consent import (
    LIVE_SENSOR_MODALITIES,
    default_live_consent_path,
    erase_live_consent,
    load_live_consent,
    save_live_consent,
)
from somatic.sensors.live_store import (
    default_csi_features_path,
    erase_csi_features,
    load_csi_features,
)
from somatic.sensors.pose_model import pose_model_status
from somatic.sensors.roster import SENSOR_ROSTER_MODALITIES, list_sensor_lanes, scan_sensor


class BridgeError(Exception):
    """HTTP-mappable API error."""

    def __init__(self, status: int, code: str, message: str, extra: dict[str, Any] | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.extra = extra or {}


def dispatch(
    method: str,
    path: str,
    body: dict[str, Any] | None,
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Route a JSON API call. Raises :class:`BridgeError` on failure."""

    payload: dict[str, Any] = {}
    if isinstance(query, dict):
        payload.update(query)
    if isinstance(body, dict):
        payload.update(body)
    key = (method.upper(), path.rstrip("/") or "/")
    handlers = {
        ("GET", "/api/meta"): _meta,
        ("GET", "/api/status"): _status,
        ("GET", "/api/consent"): _consent_get,
        ("POST", "/api/consent/grant"): lambda: _consent_change("grant", payload),
        ("POST", "/api/consent/revoke"): lambda: _consent_change("revoke", payload),
        ("POST", "/api/consent/erase"): _erase_all,
        ("GET", "/api/privacy"): _privacy,
        ("POST", "/api/privacy/erase"): _erase_all,
        ("POST", "/api/analyze"): lambda: _analyze(payload),
        ("POST", "/api/share"): lambda: _share(payload),
        ("GET", "/api/ingest"): _ingest_status,
        ("POST", "/api/ingest/csv"): lambda: _ingest_csv(payload),
        ("POST", "/api/ingest/apple-health"): lambda: _ingest_apple(payload),
        ("POST", "/api/ingest/erase"): _ingest_erase,
        ("GET", "/api/experiments"): _experiment_status,
        ("POST", "/api/experiments/tag"): lambda: _experiment_tag(payload),
        ("POST", "/api/experiments/evaluate"): lambda: _experiment_evaluate(payload),
        ("POST", "/api/experiments/erase"): _experiment_erase,
        ("POST", "/api/research"): lambda: _research(payload),
        ("POST", "/api/remedy"): lambda: _remedy(payload),
        ("POST", "/api/parasite"): lambda: _parasite(payload),
        ("GET", "/api/suggestions"): _suggestions,
        ("GET", "/api/tools"): _tools,
        ("GET", "/api/sensors"): _sensors_list,
        ("GET", "/api/sensors/field"): lambda: _sensors_field(payload),
        ("POST", "/api/sensors/field"): lambda: _sensors_field(payload),
        ("POST", "/api/sensors/scan"): lambda: _sensors_scan(payload),
        ("POST", "/api/sensors/live"): lambda: _sensors_live(payload),
        ("GET", "/api/sensors/live-consent"): _live_consent_get,
        ("POST", "/api/sensors/live-consent/grant"): lambda: _live_consent_change("grant", payload),
        ("POST", "/api/sensors/live-consent/revoke"): lambda: _live_consent_change(
            "revoke", payload
        ),
        ("POST", "/api/sensors/fuse"): lambda: _sensors_fuse(payload),
        ("POST", "/api/sensors/fuse-units"): lambda: _sensors_fuse_units(payload),
        ("POST", "/api/science"): lambda: _science(payload),
        ("POST", "/api/avatar"): lambda: _avatar(payload),
        ("POST", "/api/bench"): lambda: _bench(payload),
        ("GET", "/api/replay"): lambda: _replay(payload),
        ("POST", "/api/replay"): lambda: _replay(payload),
    }
    handler = handlers.get(key)
    if handler is None:
        raise BridgeError(404, "not_found", f"unknown route: {method} {path}")
    try:
        return handler()
    except BridgeError:
        raise
    except ConsentRequiredError as exc:
        raise BridgeError(
            403,
            "consent_required",
            f"grant {exc.scope_id} to use this",
            {"scope_id": exc.scope_id},
        ) from exc
    except SensorHardwareDisabled as exc:
        raise BridgeError(403, "hardware_disabled", str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise BridgeError(400, "invalid_request", str(exc)) from exc


def _meta() -> dict[str, Any]:
    return {
        "name": "Somatic",
        "bind": "127.0.0.1",
        "informational_notice": INFORMATIONAL_NOTICE,
        "professional_routing": PROFESSIONAL_ROUTING,
        "emergency_guidance": EMERGENCY_GUIDANCE,
        "crisis_guidance": CRISIS_GUIDANCE,
        "crisis_line_policy": CRISIS_LINE_POLICY,
        "language_scope": LANGUAGE_SCOPE,
        "honest_null": HONEST_NULL,
        "personas": list(PERSONAS),
        "sensor_modalities": list(SENSOR_ROSTER_MODALITIES),
        "presence_render_only": RENDER_ONLY,
        "presence_in_reasoning_path": REASONING_PATH_PARTICIPANT,
    }


def _status() -> dict[str, Any]:
    from somatic.local_crypto import encryption_enabled

    ledger = load_ledger()
    env_config = AdvisoryModelConfig.from_env()
    adapter_state = "configured" if env_config.model_url and env_config.model else "unset"
    screen = emergency_screen("Sudden chest pain while resting")
    lanes = [
        {
            "modality": lane.modality,
            "extra_package": lane.extra_package,
            "extra_available": lane.extra_available,
            "live_hardware": lane.live_hardware,
            "sandbox_default": lane.sandbox_default,
            "notes": lane.notes,
        }
        for lane in list_sensor_lanes()
    ]
    granted = [scope.id for scope in ledger.granted_scopes()]
    return {
        "ok": bool(screen.triggered),
        "all_scopes_off": not granted,
        "adapter_config": adapter_state,
        "emergency_self_test": {
            "triggered": screen.triggered,
            "kind": screen.kind,
            "language_scope": LANGUAGE_SCOPE,
        },
        "informational_notice": INFORMATIONAL_NOTICE,
        "professional_routing": PROFESSIONAL_ROUTING,
        "crisis_guidance": CRISIS_GUIDANCE,
        "consent_store": str(default_consent_path()),
        "granted_scopes": granted,
        "scopes": _scope_rows(ledger),
        "sensor_lanes": lanes,
        "encryption_at_rest": encryption_enabled(),
        "presence": {
            "status": "render-only",
            "render_only": RENDER_ONLY,
            "reasoning_path_participant": REASONING_PATH_PARTICIPANT,
        },
        "notes": [
            "This dashboard is the local safety spine. Full `somatic doctor` remains in the CLI.",
            "Every capability is OFF until you grant it. That empty state is the product.",
        ],
    }


def _scope_rows(ledger: Any) -> list[dict[str, Any]]:
    snapshot = ledger.to_dict()
    grants = snapshot.get("grants") if isinstance(snapshot.get("grants"), dict) else {}
    rows: list[dict[str, Any]] = []
    for scope in CONSENT_SCOPES:
        record = grants.get(scope.id) if isinstance(grants.get(scope.id), dict) else {}
        rows.append(
            {
                "id": scope.id,
                "human_label": scope.human_label,
                "description": scope.description,
                "limits": scope.limits,
                "granted": ledger.is_granted(scope),
                "default": "OFF",
                "granted_at": str(record.get("granted_at", "")),
                "actor": str(record.get("actor", "")),
            }
        )
    return rows


def _consent_get() -> dict[str, Any]:
    ledger = load_ledger()
    snapshot = ledger.to_dict()
    return {
        "store": str(default_consent_path()),
        "scopes": _scope_rows(ledger),
        "events": list(snapshot.get("events") or []),
        "all_off": not ledger.granted_scopes(),
    }


def _consent_change(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    scope_ids = _as_scope_ids(payload)
    if not scope_ids:
        raise BridgeError(400, "invalid_request", "at least one scope id is required")
    ledger = load_ledger()
    for scope_id in scope_ids:
        scope = get_scope(scope_id)
        if scope is None:
            raise BridgeError(400, "unknown_scope", f"unknown consent scope id: {scope_id}")
        if action == "grant":
            ledger.grant(scope)
        else:
            ledger.revoke(scope)
    path = save_ledger(ledger)
    return {
        "ok": True,
        "action": action,
        "scopes": scope_ids,
        "stored": str(path),
        "consent": _consent_get(),
    }


def _erase_all() -> dict[str, Any]:
    from somatic.sensors.live_audio import erase_audio_features

    erase_stored_ledger()
    erase_stored_readings()
    erase_stored_tags()
    erase_live_consent()
    erase_csi_features()
    erase_audio_features()
    return {
        "ok": True,
        "erased": [
            "consent",
            "readings",
            "experiment_tags",
            "live_sensor_grants",
            "csi_features",
            "audio_features",
        ],
        "message": (
            "Right-to-erasure complete. All scopes are OFF. Local readings, tags, "
            "live-sensor grants, and stored sensor features (CSI and audio) were "
            "deleted."
        ),
        "consent": _consent_get(),
        "privacy": _privacy(),
    }


def _privacy() -> dict[str, Any]:
    from somatic.local_crypto import ENCRYPT_STORES_ENV, encryption_enabled
    from somatic.sensors.live_audio import default_audio_features_path, load_audio_features

    readings = load_readings()
    tags = load_tags()
    frames = load_csi_features()
    audio_frames = load_audio_features()
    live = load_live_consent()
    return {
        "consent_store": str(default_consent_path()),
        "readings_store": str(default_ingest_path()),
        "experiments_store": str(default_experiment_path()),
        "live_sensor_store": str(default_live_consent_path()),
        "csi_features_store": str(default_csi_features_path()),
        "audio_features_store": str(default_audio_features_path()),
        "reading_count": len(readings),
        "tag_count": len(tags),
        "sensor_captures": len(frames),
        "audio_feature_clips": len(audio_frames),
        "sensor_capture_note": (
            "Only derived sensor features may be stored (CSI and audio). Raw CSI "
            "IQ and raw audio are never written. Live ingest stays off until you "
            "grant it."
        ),
        "encryption_at_rest": encryption_enabled(),
        "encryption_note": (
            "Opt-in via SOMATIC_ENCRYPT_STORES=1 (AES-256-GCM, optional "
            "'cryptography' package). Default stays plaintext + 0600. See SECURITY.md."
        ),
        "encryption_flag": ENCRYPT_STORES_ENV,
        "csi_live_granted": live.is_granted("csi"),
        "audio_live_granted": live.is_granted("audio"),
        "video_live_granted": live.is_granted("video"),
        "video3d_live_granted": live.is_granted("video3d"),
        "local_only": True,
    }


def _analyze(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    question = str(payload.get("question") or "What patterns stand out in my data?")
    # Screen the raw caller text BEFORE consent so crisis language still routes
    # to help even from an ungranted session, and so payload validation can
    # never answer ahead of the consent gate.
    screen = emergency_screen(f"{question}\n{json.dumps(payload, sort_keys=True, default=str)}")
    if not screen.triggered:
        if not ledger.is_granted(ANALYSIS_INSIGHT) and not ledger.is_granted(AI_ADVISORY):
            raise ConsentRequiredError(ANALYSIS_INSIGHT.id)
    try:
        packet = _data_packet(payload)
    except BridgeError:
        if not screen.triggered:
            raise
        packet = {}
    deep_screen = emergency_screen(f"{question}\n{json.dumps(packet, sort_keys=True, default=str)}")
    if deep_screen.triggered:
        screen = deep_screen
    env_config = AdvisoryModelConfig.from_env()
    model_config = env_config if env_config.model_url and env_config.model else None
    report = analyze_user_data(
        ledger,
        packet,
        question,
        references=_optional_object(payload, "references"),
        baselines=_optional_object(payload, "baselines"),
        model_config=model_config,
    )
    return {
        "report": report.to_dict(),
        "emergency": {
            "triggered": screen.triggered,
            "kind": screen.kind,
            "guidance": screen.guidance if screen.triggered else "",
        },
        "informational_notice": INFORMATIONAL_NOTICE,
        "professional_routing": PROFESSIONAL_ROUTING,
    }


def _share(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, PROFESSIONAL_SHARING)
    question = str(payload.get("question") or "What patterns stand out in my data?")
    packet = _data_packet(payload)
    report = analyze_user_data(
        ledger,
        packet,
        question,
        references=_optional_object(payload, "references"),
        baselines=_optional_object(payload, "baselines"),
        model_config=None,
    )
    patient_label = str(payload.get("patient_label") or "")
    clinician_note = str(payload.get("clinician_note") or "")
    markdown = render_professional_summary(
        ledger,
        report,
        patient_label=patient_label,
        clinician_note=clinician_note,
    )
    fhir = render_fhir_bundle(ledger, report, patient_label=patient_label)
    return {
        "preview": True,
        "title": "Patient-generated informational summary - not a diagnosis",
        "markdown": markdown,
        "fhir": fhir,
        "report": report.to_dict(),
        "informational_notice": INFORMATIONAL_NOTICE,
        "professional_routing": PROFESSIONAL_ROUTING,
        "note": "This summary stays on this machine until you download it. Nothing is uploaded.",
    }


def _ingest_status() -> dict[str, Any]:
    readings = load_readings()
    packet = IngestedPacket(readings=readings, notes=(), source_kind="store")
    return {
        "store": str(default_ingest_path()),
        "reading_count": len(readings),
        "packet": packet.to_dict() if readings else {"schema": "somatic.packet.v1", "readings": []},
    }


def _ingest_csv(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, DATA_INGESTION)
    text = str(payload.get("text") or "")
    if not text.strip():
        raise BridgeError(400, "invalid_request", "CSV text is required")
    packet = ingest_csv_text(ledger, text, default_source="csv", origin="ui-csv")
    saved = False
    if bool(payload.get("save")):
        append_readings(packet.readings)
        saved = True
    return {"preview": not saved, "saved": saved, "packet": packet.to_dict()}


def _ingest_apple(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, DATA_INGESTION)
    text = str(payload.get("text") or "")
    if not text.strip():
        raise BridgeError(400, "invalid_request", "Apple Health XML text is required")
    packet = ingest_apple_health_xml(ledger, text, origin="ui-apple-health")
    saved = False
    if bool(payload.get("save")):
        append_readings(packet.readings)
        saved = True
    return {"preview": not saved, "saved": saved, "packet": packet.to_dict()}


def _ingest_erase() -> dict[str, Any]:
    erase_stored_readings()
    return {"ok": True, "erased": ["readings"], "ingest": _ingest_status()}


def _experiment_status() -> dict[str, Any]:
    tags = load_tags()
    return {
        "store": str(default_experiment_path()),
        "tags": [tag.to_dict() for tag in tags],
    }


def _experiment_tag(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, DATA_INGESTION)
    name = str(payload.get("name") or "")
    metric = str(payload.get("metric") or "")
    note = str(payload.get("note") or "")
    screen = emergency_screen(f"{name}\n{note}\n{metric}")
    if screen.triggered:
        return {
            "emergency": True,
            "kind": screen.kind,
            "guidance": screen.guidance or EMERGENCY_GUIDANCE,
            "saved": False,
        }
    tag = InterventionTag(
        name=name,
        metric=metric,
        started_at=normalize_observed_at(str(payload.get("started_at") or "")),
        ended_at=(
            normalize_observed_at(str(payload.get("ended_at") or ""))
            if str(payload.get("ended_at") or "").strip()
            else ""
        ),
        note=note,
    )
    append_tag(tag)
    return {
        "saved": True,
        "emergency": False,
        "tag": tag.to_dict(),
        "experiments": _experiment_status(),
    }


def _experiment_evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, ANALYSIS_INSIGHT)
    packet = _data_packet(payload)
    report = evaluate_n_of_1(
        ledger,
        packet,
        metric=str(payload.get("metric") or ""),
        started_at=str(payload.get("started_at") or ""),
        name=str(payload.get("name") or "untagged-interval"),
        ended_at=str(payload.get("ended_at") or ""),
        note=str(payload.get("note") or ""),
    )
    return {"report": report.to_dict(), "informational_notice": INFORMATIONAL_NOTICE}


def _experiment_erase() -> dict[str, Any]:
    erase_stored_tags()
    return {"ok": True, "erased": ["experiment_tags"], "experiments": _experiment_status()}


def _research(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, AUTONOMOUS_RESEARCH)
    question = str(payload.get("question") or payload.get("query") or "")
    blocked = _biosecurity_or_emergency(question)
    if blocked is not None:
        return blocked
    k = int(payload.get("k") or 5)
    if k < 1:
        raise BridgeError(400, "invalid_request", "k must be >= 1")
    report = run_research_loop(ledger, question, k=k)
    return {
        "report": report.to_dict(),
        "honest_null": report.honest_null,
        "honest_null_text": HONEST_NULL,
        "informational_notice": report.result.informational_notice,
        "professional_routing": report.result.professional_routing,
    }


def _remedy(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, REMEDY_LIBRARY)
    query = str(payload.get("query") or payload.get("question") or "")
    blocked = _biosecurity_or_emergency(query)
    if blocked is not None:
        return blocked
    report = lookup_remedy(ledger, query)
    return {
        "report": report.to_dict(),
        "honest_null": report.honest_null,
        "honest_null_text": HONEST_NULL,
        "default_grade": "none",
    }


def _parasite(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, AUTONOMOUS_RESEARCH)
    question = str(payload.get("question") or payload.get("query") or "")
    blocked = _biosecurity_or_emergency(question)
    if blocked is not None:
        return blocked
    report = ask_parasite(ledger, question)
    return {
        "report": report.to_dict(),
        "honest_null": report.honest_null,
        "honest_null_text": HONEST_NULL,
        "routing_note": report.routing_note,
        "identifies_species": False,
    }


def _suggestions() -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, PROACTIVE_SUGGESTIONS)
    return {
        "implemented": False,
        "unsolicited": False,
        "suggestions": [],
        "message": (
            "Proactive suggestions are reserved. Somatic does not currently "
            "send unsolicited suggestions."
        ),
    }


def _tools() -> dict[str, Any]:
    return {
        "local_only": True,
        "fabric_runtime": False,
        "csi_live_capture": False,
        "csi_udp_ingest": True,
        "notes": [
            "Fabric check/send/receive stay in the CLI so byte-pinned vectors are not wrapped.",
            "csi-parse stays a local fixture parser in the CLI; Sensors is the sandbox roster.",
            "Full `somatic doctor` stays in the CLI because it replays the contract cascade.",
            "python -m somatic run / launch remain CLI mock-workflow tools.",
        ],
        "cli": [
            "python -m somatic doctor",
            "python -m somatic run <workflow.yaml>",
            "python -m somatic csi-parse <fixture>",
            "python -m somatic fabric check <pack.json>",
            "python -m somatic bus run --hypothesis ...",
            "python -m somatic evidence-verify --file <json>",
        ],
    }


def _sensors_list() -> dict[str, Any]:
    live = load_live_consent()
    lanes = [
        {
            "modality": lane.modality,
            "extra_package": lane.extra_package,
            "extra_available": lane.extra_available,
            "live_hardware": False,
            "sandbox_default": True,
            "go_live": (
                "loopback UDP ingest; off until live-sensor grant + subject consent"
                if lane.modality == "csi"
                else (
                    "on-device MediaPipe pose; off until live-sensor grant + subject consent"
                    if lane.modality in {"video", "video3d"}
                    else "needs hardware; not implemented"
                )
            ),
            "live_granted": live.is_granted(lane.modality),
            "notes": lane.notes,
        }
        for lane in list_sensor_lanes()
    ]
    return {
        "modalities": list(SENSOR_ROSTER_MODALITIES),
        "lanes": lanes,
        "features_only": True,
        "raw_export": False,
        "live_implemented": False,
        "csi_udp_ingest": True,
        "video_pose": True,
        "csi_live_granted": live.is_granted("csi"),
        "audio_live_granted": live.is_granted("audio"),
        "video_live_granted": live.is_granted("video"),
        "video3d_live_granted": live.is_granted("video3d"),
        "pose_model": pose_model_status(),
        "hardware_validation": HARDWARE_VALIDATION,
    }


def _sensors_scan(payload: dict[str, Any]) -> dict[str, Any]:
    live = _as_bool(payload.get("live"), False)
    modality = str(payload.get("modality") or "")
    if live and (
        modality not in LIVE_SENSOR_MODALITIES or not load_live_consent().is_granted(modality)
    ):
        raise SensorHardwareDisabled(
            "live hardware capture is disabled; sandbox-simulated by default"
        )
    ledger = load_ledger()
    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    report = scan_sensor(
        ledger,
        modality,
        ticks=int(payload.get("ticks") or 1),
        seed=int(payload.get("seed") or 0),
        live=live,
    )
    encoded = evidence_loop_to_dict(report)
    _assert_no_raw(encoded)
    return {
        "sandbox": not live,
        "live": live,
        "features_only": True,
        "hardware_validation": HARDWARE_VALIDATION,
        "report": encoded,
    }


def _sensors_live(payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    if not load_live_consent().is_granted("csi"):
        raise SensorHardwareDisabled(
            "live hardware capture is disabled; sandbox-simulated by default"
        )
    ledger = load_ledger()
    from somatic.sensors.live_csi import require_live_csi, start_ingest

    require_live_csi(ledger)
    ingest = start_ingest()
    latest = ingest.latest()
    return {
        "live": True,
        "sandbox": False,
        "features_only": True,
        "raw_export": False,
        "transport": "udp-loopback",
        "bind": f"{ingest.host}:{ingest.bound_port}",
        "packets_accepted": ingest.packets_accepted,
        "waiting_for_packets": latest is None,
        "hardware_validation": HARDWARE_VALIDATION,
        "pose_model": pose_model_status(),
    }


def _sensors_field(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, DATA_INGESTION)
    require_consent(ledger, ANALYSIS_INSIGHT)
    live = _as_bool(payload.get("live"), False)
    tick = int(payload.get("tick") or payload.get("seed") or 0)
    modality = str(payload.get("modality") or "csi")
    if live:
        live_modality = modality if modality in LIVE_SENSOR_MODALITIES else "csi"
        if not load_live_consent().is_granted(live_modality):
            raise SensorHardwareDisabled(
                "live hardware capture is disabled; sandbox-simulated by default"
            )
        report = scan_sensor(ledger, live_modality, ticks=1, seed=tick, live=True)
        step = report.steps[-1] if report.steps else None
        features = sanitize_sensor_features(step.features if step else {})
        snapshot = field_snapshot(
            features,
            mode="live",
            modality=live_modality,
            tick=tick,
            notes=report.notes,
        )
    else:
        report = scan_sensor(ledger, modality, ticks=1, seed=tick, live=False)
        step = report.steps[-1] if report.steps else None
        features = sanitize_sensor_features(step.features if step else {})
        snapshot = field_snapshot(
            features,
            mode="sandbox",
            modality=modality,
            tick=tick,
            notes=report.notes,
        )
    _assert_no_raw(snapshot)
    return snapshot


def _live_consent_get() -> dict[str, Any]:
    live = load_live_consent()
    return {
        "modalities": list(LIVE_SENSOR_MODALITIES),
        "grants": {
            name: {
                "granted": live.is_granted(name),
                "subject_consent": live.subject_consent(name),
                "default": "OFF",
            }
            for name in LIVE_SENSOR_MODALITIES
        },
        "store": str(default_live_consent_path()),
        "hardware_validation": HARDWARE_VALIDATION,
        "subject_consent_note": (
            "A booth can scan other people, not just the operator. "
            "Confirm every person in the field consented, or that you are the only subject. "
            "Keep on-device signage visible."
        ),
    }


def _live_consent_change(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    modality = str(payload.get("modality") or "csi")
    live = load_live_consent()
    if action == "grant":
        live.grant(
            modality,
            subject_consent=_as_bool(payload.get("subject_consent"), False),
        )
    else:
        live.revoke(modality)
        if modality == "csi":
            from somatic.sensors.live_csi import stop_ingest

            stop_ingest()
        elif modality in {"video", "video3d"}:
            from somatic.sensors.live_video import stop_video_ingest

            stop_video_ingest(modality)
    save_live_consent(live)
    return {"ok": True, "action": action, "consent": _live_consent_get()}


def _sensors_fuse(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    vision = payload.get("vision_features")
    rf = payload.get("rf_features") or payload.get("csi_features")
    fused = fuse_rf_vision(
        ledger,
        seed=int(payload.get("seed") or 0),
        rf_features=rf if isinstance(rf, dict) else None,
        vision_features=vision if isinstance(vision, dict) else None,
    )
    _assert_no_raw(fused)
    return {"sandbox": bool(fused.get("simulated")), "fusion": fused}


def _sensors_fuse_units(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    units = payload.get("units") or payload.get("unit_features") or []
    if not isinstance(units, list):
        raise BridgeError(400, "invalid_request", "units must be a list of feature snapshots")
    fused = fuse_csi_units(
        ledger,
        units,
        enable_pose_model=_as_bool(payload.get("enable_pose_model"), False),
    )
    _assert_no_raw(fused)
    return {"sandbox": False, "fusion": fused}


def _science(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, AUTONOMOUS_RESEARCH)
    require_consent(ledger, ANALYSIS_INSIGHT)
    goal = str(payload.get("goal") or payload.get("question") or "")
    report = run_science_loop(ledger, goal, seed=int(payload.get("seed") or 0))
    return {
        "sandbox": True,
        "read_only": True,
        "report": science_report_to_dict(report),
    }


def _avatar(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, AI_ADVISORY)
    rendered = render_presence(
        ledger,
        str(payload.get("verdict") or payload.get("summary") or ""),
        persona=str(payload.get("persona") or "doctor"),
    )
    return {
        "render_only": True,
        "reasoning_path_participant": False,
        "persona": rendered.persona,
        "speech": rendered.speech,
        "verdict_unchanged": rendered.verdict_unchanged,
        "tts_runtime": rendered.tts_runtime,
        "talking_head_runtime": rendered.talking_head_runtime,
        "camera_registered": rendered.camera_registered,
        "microphone_registered": rendered.microphone_registered,
    }


def _bench(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = load_ledger()
    require_consent(ledger, AUTONOMOUS_RESEARCH)
    require_consent(ledger, ANALYSIS_INSIGHT)
    task = str(payload.get("task") or "").strip() or None
    score = run_bench(ledger, task_path=task, seed=int(payload.get("seed") or 0))
    return {
        "sandbox": True,
        "task_id": score.task_id,
        "passed": score.passed,
        "final_answer_ok": score.final_answer_ok,
        "evidence_efficiency": score.evidence_efficiency,
        "reproducible": score.reproducible,
        "blocked": score.blocked,
        "notes": list(score.notes),
        "leaderboard": score.leaderboard,
    }


def _replay(payload: dict[str, Any]) -> dict[str, Any]:
    run_id = str(payload.get("id") or payload.get("run_id") or "").strip()
    runs_dir = str(payload.get("runs_dir") or "runs")
    if not run_id:
        raise BridgeError(400, "invalid_request", "run id is required")
    manifest_path = Path(runs_dir) / run_id / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return {"found": True, "run_id": run_id, "manifest": manifest}
    return {
        "found": False,
        "run_id": run_id,
        "message": "No local run manifest found. Replay records the id for future support.",
    }


def _optional_object(payload: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = payload.get(key)
    return value if isinstance(value, dict) else None


def _data_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("packet") or payload.get("data")
    if isinstance(packet, dict) and packet:
        return packet
    readings = load_readings()
    if not readings:
        if isinstance(packet, dict):
            return packet
        raise BridgeError(
            400,
            "invalid_request",
            "data packet is empty and no stored readings exist",
        )
    grouped = IngestedPacket(readings=readings, notes=(), source_kind="store")
    return grouped.to_analyze_packet()


def _as_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_scope_ids(payload: dict[str, Any]) -> list[str]:
    raw = payload.get("scopes") or payload.get("scope") or ""
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def _biosecurity_or_emergency(text: str) -> dict[str, Any] | None:
    screen = emergency_screen(text)
    if screen.triggered:
        return {
            "emergency": True,
            "kind": screen.kind,
            "guidance": screen.guidance or EMERGENCY_GUIDANCE,
            "honest_null": True,
            "honest_null_text": HONEST_NULL,
            "blocked": "emergency",
        }
    bio = screen_biosecurity(text)
    if bio.blocked:
        return {
            "emergency": False,
            "biosecurity": True,
            "blocked": "biosecurity",
            "guidance": bio.guidance,
            "honest_null": True,
            "honest_null_text": HONEST_NULL,
        }
    return None


def _assert_no_raw(payload: object) -> None:
    blob = json.dumps(payload, default=str).lower()
    for key in RAW_SENSOR_KEYS:
        token = f'"{key.lower()}"'
        if token in blob:
            raise BridgeError(500, "raw_sensor_blocked", f"refused to emit raw sensor key: {key}")
