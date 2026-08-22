import json
from hashlib import sha256
from pathlib import Path

from somatic.evidence.document_evidence_pack import (  # noqa: E402
    DOCUMENT_EVIDENCE_PROVIDER_KIND,
    document_evidence_pack_artifact_metadata,
)
from somatic.evidence.document_fixture import DocumentFixtureEvidenceProvider  # noqa: E402

from .agents.crow import build_literature_context
from .agents.falcon import build_measurement_plan, build_measurement_plan_artifact
from .agents.finch import analyze_raw_evidence, build_structured_verdict_artifact
from .agents.finch_toolbelt import analyze_robin_tables
from .agents.tournament import run_hypothesis_tournament
from .memory.baseline import (
    build_baseline_graph,
    build_personal_profile,
    compare_feature_set_to_baseline,
)
from .memory.intervention import load_fake_intervention_plan
from .memory.response_evaluation import (
    RESPONSE_TREND_STATUSES,
    load_fake_response_evaluation,
)
from .providers.biomodel import BiomodelRequest
from .providers.biomodel_provenance import (
    build_biomodel_pack_plan,
    build_biomodel_provenance_bundle,
)
from .providers.boltz import BoltzProvider, BoltzProviderConfig
from .reports.n_of_1_fabric_plan import build_n_of_1_fabric_pack_plan
from .reports.n_of_1_packet import build_n_of_1_report_packet
from .run_writer import make_run_id, write_run_artifacts
from .safety.adapter_readiness import real_mode_readiness_gate_summary
from .safety.biomodel import (
    BiomodelConsentRecord,
    BiomodelReadinessGateError,
    BiomodelRuntimePolicy,
)
from .safety.phase11_contracts import (
    phase11_audit_handoff_status_summary,
    phase11_audit_index_status_summary,
    phase11_contract_status_summary,
    phase11_dossier_lifecycle_status_summary,
    phase11_handoff_acceptance_status_summary,
    phase11_planning_governance_closeout_status_summary,
    phase11_preflight_status_summary,
    phase11_review_record_status_summary,
    phase11_review_trail_export_status_summary,
    phase11_runtime_authorization_gap_ledger_status_summary,
)
from .sensors.csi import build_csi_evidence_metadata, build_csi_summary_metadata
from .sensors.csi_batch import evaluate_csi_replay_batch
from .sensors.csi_evidence_pack import (
    build_csi_evidence_pack,
    csi_evidence_pack_artifact_metadata,
)
from .sensors.environment import (
    EnvironmentFixtureSensorProvider,
)
from .sensors.environment_evidence_pack import (
    ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF,
    ENVIRONMENT_EVIDENCE_PROVIDER_KIND,
    environment_evidence_pack_artifact_metadata,
)
from .sensors.evidence import build_sensor_evidence_artifact_ref
from .sensors.registry import (
    CSI_EVIDENCE_PACK_ARTIFACT_REF,
    CSI_EVIDENCE_PROVIDER_ID,
    list_sensor_evidence_providers,
    sanitize_sensor_evidence_input_spec,
    sensor_evidence_provider_by_artifact_name,
    sensor_evidence_provider_by_id,
    workflow_sensor_evidence_fixture_refs,
    workflow_sensor_evidence_groups,
)
from .sensors.sandbox import SandboxSensorProvider
from .sensors.toy_counter import ToyCounterFixtureSensorProvider
from .sensors.toy_counter_evidence_pack import (
    TOY_COUNTER_EVIDENCE_PROVIDER_KIND,
    toy_counter_evidence_pack_artifact_metadata,
)
from .simulator.sandbox_source import SandboxEvidenceSource
from .workflow_loader import load_mock_provider_metadata, load_workflow


def run_mock_workflow(workflow_path, repo_root=None, output_root=None, run_id=None):
    """Run a fixture workflow with local mock providers.

    Non-CLI callers should pass repo_root when the current working directory is
    not the repository root. If repo_root is omitted, fixture resolution assumes
    Path.cwd() is the Somatic checkout root.
    """
    root = Path(repo_root) if repo_root else Path.cwd()
    workflow = load_workflow(workflow_path)
    resolved_run_id = run_id or make_run_id()
    provider_metadata = load_mock_provider_metadata(workflow, root)
    evidence = _load_json(root / "fixtures" / "evidence" / "sample-evidence-record.json")
    safety_response = _load_json(root / "fixtures" / "safety" / "sample-safety-response.json")
    extra_artifacts = None
    if workflow.get("mode") == "hypothesis-tournament":
        csi_batch_evaluation = _evaluate_workflow_csi_replay_batch(workflow, root)
        tournament = run_hypothesis_tournament(
            workflow,
            evidence,
            csi_batch_evaluation_metadata=csi_batch_evaluation,
        )
        if csi_batch_evaluation is not None:
            csi_evidence_pack = build_csi_evidence_pack(
                batch_payload=csi_batch_evaluation,
            )
            csi_evidence_pack_sha256 = _artifact_payload_sha256(csi_evidence_pack)
            tournament["csi_evidence_pack"] = csi_evidence_pack
            tournament["team_orchestrator"]["team_orchestrator_summary"]["csi_evidence_pack"] = (
                csi_evidence_pack_artifact_metadata(
                    csi_evidence_pack,
                    artifact_sha256=csi_evidence_pack_sha256,
                )
            )
            tournament["team_orchestrator"]["team_orchestrator_summary"][
                "sensor_evidence_artifact_refs"
            ] = _csi_sensor_evidence_artifact_refs(
                csi_evidence_pack,
                csi_evidence_pack_sha256,
            )
        configured_sensor_evidence_packs = _configured_fixture_evidence_pack_specs(
            workflow,
            root,
        )
        if configured_sensor_evidence_packs:
            _attach_configured_sensor_evidence_packs(
                tournament,
                configured_sensor_evidence_packs,
                summary=tournament["team_orchestrator"]["team_orchestrator_summary"],
            )
        hypotheses = tournament["ranked_hypotheses"]
        report = _render_tournament_report(
            workflow, provider_metadata, evidence, safety_response, tournament
        )
        next_iteration = _tournament_next_iteration(tournament)
        extra_artifacts = _tournament_artifacts(tournament)
    elif workflow.get("mode") == "robin-loop":
        robin_loop = _run_robin_loop(workflow, root)
        hypotheses = robin_loop["hypotheses"]
        report = _render_robin_report(workflow, provider_metadata, safety_response, robin_loop)
        next_iteration = robin_loop["next_iteration"]
        extra_artifacts = _robin_artifacts(robin_loop)
    elif workflow.get("mode") == "in-silico-screening":
        in_silico = _run_in_silico_screening(workflow)
        hypotheses = in_silico["hypotheses"]
        report = _render_in_silico_report(workflow, provider_metadata, safety_response, in_silico)
        next_iteration = in_silico["next_iteration"]
        extra_artifacts = _in_silico_artifacts(in_silico)
    elif workflow.get("mode") == "n-of-1":
        n_of_1 = _run_n_of_1(workflow, resolved_run_id, root)
        hypotheses = n_of_1["hypotheses"]
        report = _render_n_of_1_report(workflow, provider_metadata, safety_response, n_of_1)
        next_iteration = n_of_1["next_iteration"]
        extra_artifacts = _n_of_1_artifacts(n_of_1)
    else:
        hypotheses = _mock_hypotheses(workflow, evidence)
        report = _render_report(workflow, provider_metadata, evidence, safety_response, hypotheses)
        next_iteration = _baseline_next_iteration()
    workflow_artifact = _sanitize_workflow_for_artifact(workflow)
    return write_run_artifacts(
        output_root=Path(output_root) if output_root else root / "runs",
        run_id=resolved_run_id,
        workflow=workflow_artifact,
        provider_metadata=provider_metadata,
        evidence=evidence,
        safety_response=safety_response,
        hypotheses=hypotheses,
        report_markdown=report,
        next_iteration=next_iteration,
        extra_artifacts=extra_artifacts,
    )


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sanitize_workflow_for_artifact(workflow):
    payload = json.loads(json.dumps(workflow))
    for input_spec in payload.get("inputs", []):
        if not isinstance(input_spec, dict):
            continue
        sanitized = sanitize_sensor_evidence_input_spec(input_spec)
        input_spec.clear()
        input_spec.update(sanitized)
    return payload


def _evaluate_workflow_csi_replay_batch(workflow, repo_root):
    groups = workflow_sensor_evidence_groups(workflow, CSI_EVIDENCE_PROVIDER_ID)
    if groups:
        return evaluate_csi_replay_batch(groups, repo_root=repo_root)
    return None


def _mock_hypotheses(workflow, evidence):
    evidence_id = evidence.get("id")
    return [
        {
            "id": "hyp-mock-001",
            "statement": f"The {workflow.get('mode')} workflow can preserve provenance "
            "through local fixture evidence.",
            "supporting_evidence_refs": [evidence_id],
            "confidence": "low",
            "mock": True,
        },
        {
            "id": "hyp-mock-002",
            "statement": "Provider-agnostic contracts can be exercised before real "
            "provider integration.",
            "supporting_evidence_refs": [evidence_id],
            "confidence": "low",
            "mock": True,
        },
        {
            "id": "hyp-mock-003",
            "statement": "Safety-gated report artifacts can be generated from offline fixtures.",
            "supporting_evidence_refs": [evidence_id],
            "confidence": "low",
            "mock": True,
        },
    ]


def _baseline_next_iteration():
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "recommended_actions": [
            "Review the mock report packet structure.",
            "Add schema validation in a future phase.",
            "Replace fixture providers only after safety and secrets boundaries are implemented.",
        ],
        "blocked_actions": [
            "No external provider calls.",
            "No real lab, biomodel, Fabric, or sensor execution.",
        ],
    }


def _tournament_artifacts(tournament):
    artifacts = {
        "candidate_hypotheses": {
            "relative_path": "artifacts/candidate_hypotheses.json",
            "payload": tournament["candidate_hypotheses"],
        },
        "reflection_notes": {
            "relative_path": "artifacts/reflection_notes.json",
            "payload": tournament["reflection_notes"],
        },
        "pairwise_debates": {
            "relative_path": "artifacts/pairwise_debates.json",
            "payload": tournament["pairwise_debates"],
        },
        "elo_ratings": {
            "relative_path": "artifacts/elo_ratings.json",
            "payload": tournament["elo_ratings"],
        },
        "team_roster": {
            "relative_path": "artifacts/team_roster.json",
            "payload": tournament["team_orchestrator"]["team_roster"],
        },
        "team_critiques": {
            "relative_path": "artifacts/team_critiques.json",
            "payload": tournament["team_orchestrator"]["team_critiques"],
        },
        "shared_blackboard": {
            "relative_path": "artifacts/shared_blackboard.json",
            "payload": tournament["team_orchestrator"]["shared_blackboard"],
        },
        "evidence_budget": {
            "relative_path": "artifacts/evidence_budget.json",
            "payload": tournament["team_orchestrator"]["evidence_budget"],
        },
        "reorganization_log": {
            "relative_path": "artifacts/reorganization_log.json",
            "payload": tournament["team_orchestrator"]["reorganization_log"],
        },
        "team_orchestrator_summary": {
            "relative_path": "artifacts/team_orchestrator_summary.json",
            "payload": tournament["team_orchestrator"]["team_orchestrator_summary"],
        },
        "refined_hypotheses": {
            "relative_path": "artifacts/refined_hypotheses.json",
            "payload": tournament["refined_hypotheses"],
        },
        "review_scores": {
            "relative_path": "artifacts/review_scores.json",
            "payload": tournament["review_scores"],
        },
        "tournament_bracket": {
            "relative_path": "artifacts/tournament_bracket.json",
            "payload": tournament["tournament_bracket"],
        },
        "ranked_hypotheses": {
            "relative_path": "artifacts/ranked_hypotheses.json",
            "payload": tournament["ranked_hypotheses"],
        },
    }
    _add_sensor_evidence_pack_artifacts(artifacts, tournament)
    return artifacts


def _tournament_next_iteration(tournament):
    top = tournament["ranked_hypotheses"][:3]
    team_summary = tournament["team_orchestrator"]["team_orchestrator_summary"]
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "workflow_mode": "hypothesis-tournament",
        "future_orchestration_hook": tournament["orchestration_hook"],
        "team_orchestrator_status": team_summary["orchestrator_status"],
        "team_focus_hypothesis_ids": team_summary["focus_hypothesis_ids"],
        "recommended_actions": [
            "Have a human reviewer inspect the ranked mock hypotheses before reuse.",
            "Add additional local evidence fixtures with supporting and contradictory records.",
            "Convert the top hypothesis into a falsification plan only after safety review.",
        ],
        "top_hypothesis_ids": [item["id"] for item in top],
        "blocked_actions": [
            "No external provider calls.",
            "No real lab, biomodel, Fabric, live WiFi CSI capture, live sensor, or "
            "LangGraph execution.",
            "No medical, clinical, treatment, or diagnostic recommendation.",
        ],
    }


def _run_robin_loop(workflow, repo_root):
    workflow_goal = workflow.get("description") or workflow.get("title") or workflow.get("id")
    hypothesis = (
        "A local Evidence Bus sandbox can carry Crow context, Falcon planning, "
        "fixture acquisition, Finch analysis, and a StructuredVerdict without external runtime."
    )
    crow_context = build_literature_context(
        workflow_goal=workflow_goal,
        evidence_requirements=workflow.get("evidence_requirements", {}),
    )
    measurement_plan = build_measurement_plan(
        hypothesis=hypothesis,
        literature_context=crow_context,
    )
    falcon_plan = build_measurement_plan_artifact(
        measurement_plan=measurement_plan,
        hypothesis=hypothesis,
        literature_context=crow_context,
    )
    raw_records = SandboxEvidenceSource().acquire(measurement_plan)
    raw_evidence = {
        "schema_version": 1,
        "source": "SandboxEvidenceSource",
        "mock": True,
        "offline": True,
        "research_only": True,
        "boundary": "mock/offline/research-only",
        "records": [record.to_dict() for record in raw_records],
    }
    finch_toolbelt = analyze_robin_tables(raw_records, repo_root=repo_root)
    finch_analysis = analyze_raw_evidence(raw_records)
    finch_analysis["analysis"]["toolbelt_summary"] = finch_toolbelt["finch_toolbelt_summary"]
    structured_verdict = build_structured_verdict_artifact(finch_analysis)
    next_iteration = _robin_next_iteration(structured_verdict)
    summary = {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "research_only": True,
        "loop_shape": "crow-falcon-sandbox-finch-verdict-next",
        "crow_record_count": len(crow_context["records"]),
        "falcon_source_modalities": [
            source["modality"] for source in falcon_plan["measurement_plan"]["sources"]
        ],
        "raw_evidence_count": len(raw_evidence["records"]),
        "finch_toolbelt_status": finch_toolbelt["finch_toolbelt_summary"]["toolbelt_status"],
        "finch_toolbelt_table_count": finch_toolbelt["finch_toolbelt_summary"]["table_count"],
        "dose_response_available": finch_toolbelt["finch_toolbelt_summary"][
            "dose_response_available"
        ],
        "structured_verdict_id": structured_verdict["structured_verdict"]["id"],
        "next_iteration": next_iteration,
        "limitations": [
            "Deterministic mock artifacts only.",
            "No real provider, PaperQA2, FutureHouse Robin, scientific-agent-skills, "
            "LangGraph, AutoScientists, Fabric, biomodel, sensor, or wetlab runtime.",
            "No medical advice and no real scientific conclusion.",
        ],
    }
    hypotheses = [
        {
            "id": "hyp-robin-sandbox-001",
            "statement": hypothesis,
            "supporting_evidence_refs": [record["id"] for record in raw_evidence["records"]],
            "confidence": structured_verdict["structured_verdict"]["confidence"],
            "mock": True,
            "offline": True,
            "research_only": True,
        }
    ]
    return {
        "crow_literature_context": crow_context,
        "falcon_measurement_plan": falcon_plan,
        "raw_evidence": raw_evidence,
        "finch_analysis": finch_analysis,
        "finch_toolbelt_summary": finch_toolbelt["finch_toolbelt_summary"],
        "table_profile": finch_toolbelt["table_profile"],
        "dose_response_summary": finch_toolbelt["dose_response_summary"],
        "analysis_provenance": finch_toolbelt["analysis_provenance"],
        "structured_verdict": structured_verdict,
        "robin_loop_summary": summary,
        "next_iteration": next_iteration,
        "hypotheses": hypotheses,
    }


def _robin_next_iteration(structured_verdict):
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "workflow_mode": "robin-loop",
        "recommended_mode": "mock-local-repeat",
        "structured_verdict_id": structured_verdict["structured_verdict"]["id"],
        "recommended_actions": [
            "Review the mock artifacts and report language with a human reviewer.",
            "Add more local fixture records before changing confidence language.",
            "Keep future provider, lab, sensor, Fabric, biomodel, PaperQA2, and Robin "
            "integrations disabled until explicitly approved.",
        ],
        "blocked_actions": [
            "No external provider calls.",
            "No real lab, clinical, biomodel, Fabric, sensor, or treatment action.",
            "No diagnosis, treatment, cure, emergency triage, or real scientific conclusion.",
        ],
    }


def _robin_artifacts(robin_loop):
    return {
        "crow_literature_context": {
            "relative_path": "artifacts/crow_literature_context.json",
            "payload": robin_loop["crow_literature_context"],
        },
        "falcon_measurement_plan": {
            "relative_path": "artifacts/falcon_measurement_plan.json",
            "payload": robin_loop["falcon_measurement_plan"],
        },
        "raw_evidence": {
            "relative_path": "artifacts/raw_evidence.json",
            "payload": robin_loop["raw_evidence"],
        },
        "finch_analysis": {
            "relative_path": "artifacts/finch_analysis.json",
            "payload": robin_loop["finch_analysis"],
        },
        "finch_toolbelt_summary": {
            "relative_path": "artifacts/finch_toolbelt_summary.json",
            "payload": robin_loop["finch_toolbelt_summary"],
        },
        "table_profile": {
            "relative_path": "artifacts/table_profile.json",
            "payload": robin_loop["table_profile"],
        },
        "dose_response_summary": {
            "relative_path": "artifacts/dose_response_summary.json",
            "payload": robin_loop["dose_response_summary"],
        },
        "analysis_provenance": {
            "relative_path": "artifacts/analysis_provenance.json",
            "payload": robin_loop["analysis_provenance"],
        },
        "structured_verdict": {
            "relative_path": "artifacts/structured_verdict.json",
            "payload": robin_loop["structured_verdict"],
        },
        "robin_loop_summary": {
            "relative_path": "artifacts/robin_loop_summary.json",
            "payload": robin_loop["robin_loop_summary"],
        },
    }


def _run_in_silico_screening(workflow):
    _assert_in_silico_workflow_gates(workflow)
    request = _in_silico_biomodel_request(workflow)
    policy = BiomodelRuntimePolicy()
    consent = BiomodelConsentRecord()
    provider = BoltzProvider(
        BoltzProviderConfig(
            enabled=True,
            mode="mock",
            runtime_policy=policy,
            consent_record=consent,
        )
    )
    plan = provider.plan(request)
    result = provider.run(request)
    evidence_record = provider.evidence_record(request, result)
    raw_evidence = evidence_record.raw_evidence
    structured_verdict = evidence_record.structured_verdict
    request_payload = _schema_artifact(request.to_dict())
    readiness_payload = _schema_artifact(plan.metadata["readiness_report"])
    consent_payload = _schema_artifact(consent.to_dict())
    plan_payload = _schema_artifact(plan.to_dict())
    result_payload = _schema_artifact(result.to_dict())
    evidence_record_payload = _schema_artifact(evidence_record.to_dict())
    raw_evidence_payload = _schema_artifact(raw_evidence.to_dict())
    structured_verdict_payload = _schema_artifact(structured_verdict.to_dict())
    raw_evidence_payload["metadata"]["provider_payload_ref"] = raw_evidence_payload["payload_ref"]
    raw_evidence_payload["payload_ref"] = "artifacts/biomodel_result.json"
    raw_evidence_payload["sha256"] = _artifact_payload_sha256(result_payload)
    evidence_record_payload["raw_evidence"] = dict(raw_evidence_payload)
    evidence_record_payload["raw_evidence"].pop("schema_version", None)
    provenance_artifacts = {
        "biomodel_request": request_payload,
        "biomodel_readiness_report": readiness_payload,
        "biomodel_consent_record": consent_payload,
        "biomodel_plan": plan_payload,
        "biomodel_result": result_payload,
        "biomodel_evidence_record": evidence_record_payload,
        "biomodel_raw_evidence": raw_evidence_payload,
        "biomodel_structured_verdict": structured_verdict_payload,
    }
    provenance_bundle = build_biomodel_provenance_bundle(
        provenance_artifacts,
        provider.status(),
        workflow.get("id"),
    )
    pack_plan = build_biomodel_pack_plan(provenance_bundle)
    provenance_payload = provenance_bundle.to_dict()
    pack_plan_payload = pack_plan.to_dict()
    summary = {
        "schema_version": 1,
        "workflow_id": workflow.get("id"),
        "workflow_mode": workflow.get("mode"),
        "provider_id": provider.provider_id,
        "biomodel_request_id": plan.request_id,
        "biomodel_plan_id": plan.id,
        "biomodel_result_id": result.id,
        "biomodel_evidence_record_id": evidence_record.id,
        "biomodel_provenance_bundle_id": provenance_bundle.id,
        "biomodel_pack_plan_id": pack_plan.id,
        "raw_evidence_id": raw_evidence.id,
        "structured_verdict_id": structured_verdict.id,
        "fake_backed_planning_only": True,
        "research_only": True,
        "biomodel_readiness_ready": readiness_payload["ready"],
        "biomodel_runtime_execution_permitted": readiness_payload["execution_permitted"],
        "biomodel_runtime_blocked": not readiness_payload["execution_permitted"],
        "biomodel_block_reasons": list(readiness_payload["block_reasons"]),
        "biomodel_research_only_boundary_acknowledged": consent_payload[
            "research_only_acknowledged"
        ],
        "real_biomodel_runtime": "future only",
        "biomodel_provenance_packaging": "planning only",
        "fabric_pack_class_recommendation": pack_plan.pack_class,
        "fabric_pack_candidate_type": pack_plan.candidate_type,
        "fabric_code_pack": pack_plan.code_pack,
        "fabric_publishing_enabled": pack_plan.publishing_enabled,
        "fabric_transport_status": pack_plan.transport_status,
        "fabric_signed_pack_created": pack_plan.signed_pack_created,
        "boltz_execution": False,
        "model_weights_downloaded": False,
        "msa_server_call": False,
        "network_calls": False,
        "gpu_or_runtime_execution": False,
        "real_prediction": False,
        "clinical_or_lab_conclusion": False,
        "evidence_modality": raw_evidence.source.modality,
        "evidence_submodality": raw_evidence.source.metadata.get("submodality"),
        "blocked_actions": list(plan.blocked_actions),
        "limitations": list(result.limitations),
        "future_real_mode_requirements": [
            "explicit opt-in",
            "resource checks",
            "model and input provenance",
            "safety review",
            "consent gates before downloads, MSA servers, network, or GPU execution",
            "license, provenance, and safety review before any Fabric packaging",
        ],
    }
    next_iteration = _in_silico_next_iteration(summary)
    hypotheses = [
        {
            "id": "hyp-insilico-planning-001",
            "statement": (
                "The in-silico workflow can produce fake-backed biomodel planning "
                "artifacts and Evidence Bus metadata without real prediction."
            ),
            "supporting_evidence_refs": [raw_evidence.id],
            "confidence": "not-applicable",
            "mock": True,
            "offline": True,
            "research_only": True,
        }
    ]
    return {
        "biomodel_request": request_payload,
        "biomodel_readiness_report": readiness_payload,
        "biomodel_consent_record": consent_payload,
        "biomodel_plan": plan_payload,
        "biomodel_result": result_payload,
        "biomodel_evidence_record": evidence_record_payload,
        "biomodel_raw_evidence": raw_evidence_payload,
        "biomodel_structured_verdict": structured_verdict_payload,
        "biomodel_provenance_bundle": provenance_payload,
        "biomodel_pack_plan": pack_plan_payload,
        "in_silico_summary": summary,
        "next_iteration": next_iteration,
        "hypotheses": hypotheses,
    }


def _in_silico_biomodel_request(workflow):
    refs = {
        item.get("id"): item.get("ref")
        for item in workflow.get("inputs", [])
        if isinstance(item, dict) and item.get("ref")
    }
    constraints = _in_silico_constraints(workflow)
    return BiomodelRequest(
        objective=workflow.get("description") or workflow.get("title") or workflow.get("id"),
        target_refs=tuple(
            ref
            for ref in (
                refs.get("target_complex"),
                refs.get("target_protein"),
                refs.get("ligand_candidate"),
            )
            if ref
        ),
        input_artifact_refs=tuple(
            ref
            for ref in (
                refs.get("boltz_yaml_input"),
                refs.get("precomputed_msa_placeholder"),
            )
            if ref
        ),
        constraints=constraints,
        metadata={
            "workflow_id": workflow.get("id"),
            "workflow_mode": workflow.get("mode"),
            "mock": True,
            "research_only": True,
            "clinical_or_lab_conclusion": False,
            "fake_backed": True,
        },
    )


def _in_silico_constraints(workflow):
    constraints = {
        "allow_runtime_execution": False,
        "allow_model_download": False,
        "allow_msa_server": False,
        "allow_network_calls": False,
        "allow_gpu_execution": False,
        "research_only": True,
    }
    for provider in workflow.get("providers", []):
        if provider.get("class") == "biomodel":
            constraints.update(provider.get("constraints", {}))
    return constraints


def _assert_in_silico_workflow_gates(workflow):
    blocked = []
    safety_profile = workflow.get("safety_profile", {})
    if safety_profile.get("external_actions_allowed"):
        blocked.append("safety_profile.external_actions_allowed")

    forbidden_constraint_keys = (
        "allow_runtime_execution",
        "allow_model_download",
        "allow_model_downloads",
        "allow_msa_server",
        "allow_network_calls",
        "allow_gpu_execution",
    )
    required_false_keys = (
        "mock_only",
        "fake_backed",
        "offline_required",
        "research_only",
    )
    for provider in workflow.get("providers", []):
        if provider.get("class") != "biomodel":
            continue
        constraints = provider.get("constraints", {})
        for key in forbidden_constraint_keys:
            if constraints.get(key) not in (False, None):
                blocked.append(f"providers.biomodel.constraints.{key}")
        for key in required_false_keys:
            if constraints.get(key) is False:
                blocked.append(f"providers.biomodel.constraints.{key}")

    if blocked:
        raise BiomodelReadinessGateError(
            "In-silico biomodel workflow failed readiness gates: " + ", ".join(blocked)
        )


def _in_silico_artifacts(in_silico):
    return {
        name: {
            "relative_path": f"artifacts/{name}.json",
            "payload": in_silico[name],
        }
        for name in (
            "biomodel_request",
            "biomodel_readiness_report",
            "biomodel_consent_record",
            "biomodel_plan",
            "biomodel_result",
            "biomodel_evidence_record",
            "biomodel_raw_evidence",
            "biomodel_structured_verdict",
            "biomodel_provenance_bundle",
            "biomodel_pack_plan",
            "in_silico_summary",
        )
    }


def _in_silico_next_iteration(summary):
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "workflow_mode": "in-silico-screening",
        "recommended_mode": "fake-backed-biomodel-planning",
        "structured_verdict_id": summary["structured_verdict_id"],
        "recommended_actions": [
            "Review the fake-backed biomodel plan and Evidence Bus mapping with a human reviewer.",
            "Keep any future real Boltz path behind explicit opt-in, provenance, "
            "resource, and safety gates.",
            "Add local-only input validation fixtures before considering a real biomodel adapter.",
        ],
        "blocked_actions": [
            "No Boltz execution.",
            "No model weights, dataset, or MSA downloads.",
            "No MSA server, external API, network, or GPU/runtime execution.",
            "No real structure, affinity, medical, lab, or scientific conclusion.",
        ],
    }


def _run_n_of_1(workflow, run_id, repo_root):
    # Artifact assembly is ordered by dependency so every later reference hashes
    # the exact payload that will be written into the run directory.
    _assert_n_of_1_workflow_gates(workflow)
    provider = SandboxSensorProvider()
    stream_plan = provider.plan_stream(workflow)
    observations = provider.observations(stream_plan)
    feature_set = provider.features(stream_plan, observations)
    evidence_record = provider.evidence_record(stream_plan, feature_set)
    stream_plan_payload = _schema_artifact(stream_plan.to_dict())
    _mark_n_of_1_payload_boundary(stream_plan_payload)
    observations_payload = _schema_artifact(
        {
            "id": "sensor-observations-n-of-1-sandbox",
            "stream_plan_id": stream_plan.id,
            "provider_id": provider.provider_id,
            "mock": True,
            "offline": True,
            "research_only": True,
            "simulated": True,
            "live_sensor_access": False,
            "hardware_access": False,
            "network_calls": False,
            "diagnosis": False,
            "treatment_recommendation": False,
            "emergency_triage": False,
            "real_monitoring": False,
            "observations": [observation.to_dict() for observation in observations],
        }
    )
    feature_set_payload = _schema_artifact(feature_set.to_dict())
    _mark_n_of_1_payload_boundary(feature_set_payload)
    csi_fixture_refs = _n_of_1_csi_fixture_refs(workflow)
    # CSI replay stays on sanitized fixtures; the returned payloads are public
    # metadata summaries, not raw sensor capture or live network evidence.
    csi_replay_payload = provider.replay_csi_fixtures(
        csi_fixture_refs,
        repo_root=repo_root,
    )
    csi_parser_report_payload = csi_replay_payload["report"]
    csi_parsed_summary_payload = csi_replay_payload["summary"]
    csi_evidence_scoring = dict(csi_parser_report_payload.get("csi_evidence_scoring", {}))
    _mark_n_of_1_payload_boundary(csi_parser_report_payload)
    _mark_n_of_1_payload_boundary(csi_parsed_summary_payload)
    evidence_record_payload = _schema_artifact(evidence_record.to_dict())
    _mark_n_of_1_payload_boundary(evidence_record_payload)
    feature_set_sha256 = _artifact_payload_sha256(feature_set_payload)
    csi_parser_report_sha256 = _artifact_payload_sha256(csi_parser_report_payload)
    csi_parsed_summary_sha256 = _artifact_payload_sha256(csi_parsed_summary_payload)
    evidence_record_payload["raw_evidence"]["sha256"] = feature_set_sha256
    evidence_record_payload["metadata"]["feature_set_sha256"] = feature_set_sha256
    csi_evidence_metadata = build_csi_evidence_metadata(
        feature_set_ref="artifacts/sensor_feature_set.json",
        feature_set_sha256=feature_set_sha256,
        csi_metadata=feature_set_payload["metadata"]["csi"],
        csi_evidence_scoring=csi_evidence_scoring,
    )
    evidence_record_payload["metadata"]["csi"] = csi_evidence_metadata
    evidence_record_payload["raw_evidence"]["metadata"]["csi"] = csi_evidence_metadata
    evidence_record_payload["structured_verdict"]["metadata"]["csi"] = {
        "status": "placeholder-metadata-only",
        "planning_only": True,
        "clinical_claim": False,
        "medical_or_clinical_claim": False,
        "diagnosis": False,
        "treatment_recommendation": False,
        "emergency_triage": False,
        "evidence_scoring": csi_evidence_scoring,
    }
    baseline_payload = _n_of_1_baseline_placeholder(workflow)
    _mark_n_of_1_payload_boundary(baseline_payload)
    personal_profile = build_personal_profile(workflow)
    personal_profile_payload = _schema_artifact(personal_profile.to_dict())
    _mark_n_of_1_payload_boundary(personal_profile_payload)
    baseline_graph = build_baseline_graph(personal_profile, workflow)
    baseline_graph_payload = _schema_artifact(baseline_graph.to_dict())
    _mark_n_of_1_payload_boundary(baseline_graph_payload)
    personal_profile_sha256 = _artifact_payload_sha256(personal_profile_payload)
    baseline_graph_sha256 = _artifact_payload_sha256(baseline_graph_payload)
    evidence_record_sha256 = _artifact_payload_sha256(evidence_record_payload)
    csi_evidence_pack_payload = build_csi_evidence_pack(
        parser_report_payload=csi_parser_report_payload,
        parsed_summary_payload=csi_parsed_summary_payload,
        scoring_payload=csi_evidence_scoring,
        artifact_hashes={
            "parser_metadata": csi_parser_report_sha256,
            "parsed_metadata": csi_parsed_summary_sha256,
            "sensor_evidence_metadata": evidence_record_sha256,
        },
        artifact_refs={
            "parser_metadata": "artifacts/csi_parser_report.json",
            "parsed_metadata": "artifacts/csi_parsed_summary.json",
            "sensor_evidence_metadata": "artifacts/sensor_evidence_record.json",
        },
    )
    csi_evidence_pack_sha256 = _artifact_payload_sha256(csi_evidence_pack_payload)
    configured_sensor_evidence_packs = _configured_fixture_evidence_pack_specs(
        workflow,
        repo_root,
    )
    environment_evidence_pack_payload = _configured_evidence_pack_payload(
        configured_sensor_evidence_packs,
        "environment_evidence_pack",
    )
    baseline_comparison = compare_feature_set_to_baseline(feature_set_payload, baseline_graph)
    baseline_comparison_payload = _schema_artifact(baseline_comparison.to_dict())
    _mark_n_of_1_payload_boundary(baseline_comparison_payload)
    baseline_comparison_payload["artifact_refs"] = {
        "sensor_feature_set": "artifacts/sensor_feature_set.json",
        "sensor_evidence_record": "artifacts/sensor_evidence_record.json",
        "personal_profile": "artifacts/personal_profile.json",
        "baseline_graph": "artifacts/baseline_graph.json",
    }
    baseline_comparison_payload["artifact_hashes"] = {
        "sensor_feature_set": feature_set_sha256,
        "sensor_evidence_record": evidence_record_sha256,
        "personal_profile": personal_profile_sha256,
        "baseline_graph": baseline_graph_sha256,
    }
    baseline_comparison_sha256 = _artifact_payload_sha256(baseline_comparison_payload)
    (
        intervention_tag,
        intervention_context,
        response_evaluation_plan,
        mock_intervention_ledger,
    ) = load_fake_intervention_plan(
        workflow=workflow,
        sensor_feature_set_payload=feature_set_payload,
        baseline_comparison_payload=baseline_comparison_payload,
        personal_profile_payload=personal_profile_payload,
        baseline_graph_payload=baseline_graph_payload,
        artifact_hashes={
            "sensor_feature_set": feature_set_sha256,
            "baseline_comparison": baseline_comparison_sha256,
            "personal_profile": personal_profile_sha256,
            "baseline_graph": baseline_graph_sha256,
        },
    )
    intervention_tag_payload = _schema_artifact(intervention_tag.to_dict())
    _mark_n_of_1_payload_boundary(intervention_tag_payload)
    intervention_context_payload = _schema_artifact(intervention_context.to_dict())
    _mark_n_of_1_payload_boundary(intervention_context_payload)
    response_evaluation_plan_payload = _schema_artifact(response_evaluation_plan.to_dict())
    _mark_n_of_1_payload_boundary(response_evaluation_plan_payload)
    mock_intervention_ledger_payload = _schema_artifact(mock_intervention_ledger.to_dict())
    _mark_n_of_1_payload_boundary(mock_intervention_ledger_payload)
    intervention_tag_sha256 = _artifact_payload_sha256(intervention_tag_payload)
    intervention_context_sha256 = _artifact_payload_sha256(intervention_context_payload)
    response_evaluation_plan_sha256 = _artifact_payload_sha256(response_evaluation_plan_payload)
    mock_intervention_ledger_sha256 = _artifact_payload_sha256(mock_intervention_ledger_payload)
    (
        follow_up_observation_window,
        follow_up_sensor_snapshot,
        response_comparison,
        response_evaluation_summary,
    ) = load_fake_response_evaluation(
        workflow=workflow,
        sensor_feature_set_payload=feature_set_payload,
        baseline_comparison_payload=baseline_comparison_payload,
        intervention_tag_payload=intervention_tag_payload,
        response_evaluation_plan_payload=response_evaluation_plan_payload,
        personal_profile_payload=personal_profile_payload,
        baseline_graph_payload=baseline_graph_payload,
        artifact_hashes={
            "sensor_feature_set": feature_set_sha256,
            "baseline_comparison": baseline_comparison_sha256,
            "intervention_tag": intervention_tag_sha256,
            "response_evaluation_plan": response_evaluation_plan_sha256,
            "personal_profile": personal_profile_sha256,
            "baseline_graph": baseline_graph_sha256,
        },
    )
    follow_up_observation_window_payload = _schema_artifact(follow_up_observation_window.to_dict())
    _mark_n_of_1_payload_boundary(follow_up_observation_window_payload)
    follow_up_sensor_snapshot_payload = _schema_artifact(follow_up_sensor_snapshot.to_dict())
    _mark_n_of_1_payload_boundary(follow_up_sensor_snapshot_payload)
    response_comparison_payload = _schema_artifact(response_comparison.to_dict())
    _mark_n_of_1_payload_boundary(response_comparison_payload)
    response_evaluation_summary_payload = _schema_artifact(response_evaluation_summary.to_dict())
    _mark_n_of_1_payload_boundary(response_evaluation_summary_payload)
    follow_up_observation_window_sha256 = _artifact_payload_sha256(
        follow_up_observation_window_payload
    )
    follow_up_sensor_snapshot_sha256 = _artifact_payload_sha256(follow_up_sensor_snapshot_payload)
    response_comparison_sha256 = _artifact_payload_sha256(response_comparison_payload)
    response_evaluation_summary_sha256 = _artifact_payload_sha256(
        response_evaluation_summary_payload
    )
    summary = _n_of_1_summary(
        workflow,
        provider.status(),
        stream_plan_payload,
        observations_payload,
        feature_set_payload,
        csi_parser_report_payload,
        csi_parsed_summary_payload,
        csi_evidence_pack_payload,
        environment_evidence_pack_payload,
        evidence_record_payload,
        baseline_payload,
        personal_profile_payload,
        baseline_graph_payload,
        baseline_comparison_payload,
        intervention_tag_payload,
        intervention_context_payload,
        response_evaluation_plan_payload,
        mock_intervention_ledger_payload,
        follow_up_observation_window_payload,
        follow_up_sensor_snapshot_payload,
        response_comparison_payload,
        response_evaluation_summary_payload,
        {
            "sensor_feature_set": feature_set_sha256,
            "csi_parser_report": csi_parser_report_sha256,
            "csi_parsed_summary": csi_parsed_summary_sha256,
            "csi_evidence_pack": csi_evidence_pack_sha256,
            "sensor_evidence_record": evidence_record_sha256,
            "personal_profile": personal_profile_sha256,
            "baseline_graph": baseline_graph_sha256,
            "baseline_comparison": baseline_comparison_sha256,
            "intervention_tag": intervention_tag_sha256,
            "intervention_context": intervention_context_sha256,
            "response_evaluation_plan": response_evaluation_plan_sha256,
            "mock_intervention_ledger": mock_intervention_ledger_sha256,
            "follow_up_observation_window": follow_up_observation_window_sha256,
            "follow_up_sensor_snapshot": follow_up_sensor_snapshot_sha256,
            "response_comparison": response_comparison_sha256,
            "response_evaluation_summary": response_evaluation_summary_sha256,
            **_configured_evidence_pack_hashes(configured_sensor_evidence_packs),
        },
        configured_sensor_evidence_packs,
    )
    # The packet builder validates this registry against the files that
    # run_writer later persists, so names here are part of the report contract.
    packet_payloads = {
        "sensor_stream_plan": stream_plan_payload,
        "sensor_observations": observations_payload,
        "sensor_feature_set": feature_set_payload,
        "csi_parser_report": csi_parser_report_payload,
        "csi_parsed_summary": csi_parsed_summary_payload,
        "csi_evidence_pack": csi_evidence_pack_payload,
        "sensor_evidence_record": evidence_record_payload,
        "n_of_1_baseline_placeholder": baseline_payload,
        "personal_profile": personal_profile_payload,
        "baseline_graph": baseline_graph_payload,
        "baseline_comparison": baseline_comparison_payload,
        "intervention_tag": intervention_tag_payload,
        "intervention_context": intervention_context_payload,
        "response_evaluation_plan": response_evaluation_plan_payload,
        "mock_intervention_ledger": mock_intervention_ledger_payload,
        "follow_up_observation_window": follow_up_observation_window_payload,
        "follow_up_sensor_snapshot": follow_up_sensor_snapshot_payload,
        "response_comparison": response_comparison_payload,
        "response_evaluation_summary": response_evaluation_summary_payload,
        "n_of_1_summary": summary,
    }
    packet_payloads.update(_configured_evidence_pack_payloads(configured_sensor_evidence_packs))
    report_packet_payload = build_n_of_1_report_packet(
        run_id=run_id,
        workflow=workflow,
        artifact_payloads=packet_payloads,
        generated_at=run_id,
    ).to_dict()
    _mark_n_of_1_payload_boundary(report_packet_payload)
    fabric_pack_plan_payload = build_n_of_1_fabric_pack_plan(
        run_dir=Path("runs") / run_id,
        report_packet=report_packet_payload,
        generated_at=run_id,
    ).to_dict()
    _mark_n_of_1_payload_boundary(fabric_pack_plan_payload)
    next_iteration = _n_of_1_next_iteration(summary)
    hypotheses = [
        {
            "id": "hyp-n-of-1-sandbox-planning-001",
            "statement": (
                "The n-of-1 workflow can produce fake-backed sensor planning "
                "artifacts and Evidence Bus metadata without real monitoring."
            ),
            "supporting_evidence_refs": [
                evidence_record.raw_evidence.id,
                evidence_record.structured_verdict.id,
            ],
            "confidence": "not-applicable",
            "mock": True,
            "offline": True,
            "research_only": True,
        }
    ]
    return {
        "sensor_stream_plan": stream_plan_payload,
        "sensor_observations": observations_payload,
        "sensor_feature_set": feature_set_payload,
        "csi_parser_report": csi_parser_report_payload,
        "csi_parsed_summary": csi_parsed_summary_payload,
        "csi_evidence_pack": csi_evidence_pack_payload,
        "environment_evidence_pack": environment_evidence_pack_payload,
        "sensor_evidence_record": evidence_record_payload,
        "n_of_1_baseline_placeholder": baseline_payload,
        "personal_profile": personal_profile_payload,
        "baseline_graph": baseline_graph_payload,
        "baseline_comparison": baseline_comparison_payload,
        "intervention_tag": intervention_tag_payload,
        "intervention_context": intervention_context_payload,
        "response_evaluation_plan": response_evaluation_plan_payload,
        "mock_intervention_ledger": mock_intervention_ledger_payload,
        "follow_up_observation_window": follow_up_observation_window_payload,
        "follow_up_sensor_snapshot": follow_up_sensor_snapshot_payload,
        "response_comparison": response_comparison_payload,
        "response_evaluation_summary": response_evaluation_summary_payload,
        "n_of_1_summary": summary,
        "n_of_1_report_packet": report_packet_payload,
        "n_of_1_fabric_pack_plan": fabric_pack_plan_payload,
        "next_iteration": next_iteration,
        "hypotheses": hypotheses,
        **_configured_evidence_pack_payloads(configured_sensor_evidence_packs),
    }


def _assert_n_of_1_workflow_gates(workflow):
    # Fail closed before constructing artifacts: a workflow that requests real
    # capture, storage, advice, or intervention is outside this mock runtime.
    blocked = []
    safety_profile = workflow.get("safety_profile", {})
    if safety_profile.get("external_actions_allowed"):
        blocked.append("safety_profile.external_actions_allowed")
    if safety_profile.get("clinical_safety_gate_required"):
        blocked.append("safety_profile.clinical_safety_gate_required")

    forbidden_truthy_constraint_keys = (
        "allow_hardware_access",
        "allow_live_capture",
        "allow_camera",
        "allow_microphone",
        "allow_audio_capture",
        "allow_ble",
        "allow_wifi_csi_capture",
        "allow_packet_capture",
        "allow_wifi_network_probing",
        "allow_monitor_mode",
        "allow_driver_access",
        "allow_raw_rf_collection",
        "allow_raw_rf_export",
        "allow_raw_csi_collection",
        "allow_raw_csi_export",
        "allow_wearable_capture",
        "allow_thermal_capture",
        "allow_network_calls",
        "allow_personal_data_export",
        "allow_personal_health_data_export",
        "allow_real_health_data",
        "allow_health_data_import",
        "allow_profile_storage",
        "allow_real_profile_storage",
        "allow_baseline_export",
        "allow_database",
        "allow_external_memory",
        "allow_hindsight_runtime",
        "allow_mem0_runtime",
        "allow_zep_runtime",
        "allow_real_intervention",
        "allow_recommendation",
        "allow_medical_advice",
        "allow_intervention_recommendation",
        "allow_prescription",
        "allow_medication_recommendation",
        "allow_medication_action",
        "allow_clinician_action",
        "allow_clinician_review_action",
        "allow_effectiveness_claim",
        "allow_intervention_effectiveness_claim",
        "allow_response_effectiveness_claim",
        "allow_follow_up_capture",
        "allow_real_scheduling",
        "allow_notification_automation",
        "allow_reminder_automation",
        "allow_real_response_monitoring",
        "allow_real_monitoring",
        "allow_diagnosis",
        "allow_treatment_recommendation",
        "allow_emergency_triage",
    )
    required_truthy_constraint_keys = (
        "mock_only",
        "fake_backed",
        "offline_required",
        "research_only",
    )
    for provider in workflow.get("providers", []):
        if provider.get("class") != "sensor":
            continue
        constraints = provider.get("constraints", {})
        for key in forbidden_truthy_constraint_keys:
            if constraints.get(key) not in (False, None):
                blocked.append(f"providers.sensor.constraints.{key}")
        for key in required_truthy_constraint_keys:
            if constraints.get(key) is not True:
                blocked.append(f"providers.sensor.constraints.{key}")

    if blocked:
        raise ValueError("n-of-1 sensor workflow failed sandbox gates: " + ", ".join(blocked))


def _n_of_1_csi_fixture_refs(workflow):
    return workflow_sensor_evidence_fixture_refs(workflow, CSI_EVIDENCE_PROVIDER_ID)


def _workflow_environment_fixture_refs(workflow):
    return workflow_sensor_evidence_fixture_refs(workflow, ENVIRONMENT_EVIDENCE_PROVIDER_KIND)


def _configured_fixture_evidence_pack_specs(workflow, repo_root):
    providers = {
        ENVIRONMENT_EVIDENCE_PROVIDER_KIND: {
            "provider": EnvironmentFixtureSensorProvider,
            "artifact_metadata": environment_evidence_pack_artifact_metadata,
        },
        TOY_COUNTER_EVIDENCE_PROVIDER_KIND: {
            "provider": ToyCounterFixtureSensorProvider,
            "artifact_metadata": toy_counter_evidence_pack_artifact_metadata,
        },
        DOCUMENT_EVIDENCE_PROVIDER_KIND: {
            "provider": DocumentFixtureEvidenceProvider,
            "artifact_metadata": document_evidence_pack_artifact_metadata,
        },
    }
    specs = {}
    for provider_id, runtime_spec in sorted(providers.items()):
        entry = sensor_evidence_provider_by_id(provider_id)
        if entry is None:
            continue
        refs = workflow_sensor_evidence_fixture_refs(workflow, provider_id)
        if not refs:
            continue
        provider = runtime_spec["provider"]()
        payload = provider.evidence_pack(refs, repo_root=repo_root)
        sha256_value = _artifact_payload_sha256(payload)
        specs[entry.artifact_name] = {
            "payload": payload,
            "relative_path": entry.artifact_ref,
            "sha256": sha256_value,
            "provider_kind": entry.provider_kind,
            "evidence_kind": entry.evidence_kind,
            "artifact_metadata": runtime_spec["artifact_metadata"](
                payload,
                artifact_sha256=sha256_value,
            ),
            "readiness_metadata": _sensor_evidence_readiness_metadata(payload),
        }
    return specs


def _attach_configured_sensor_evidence_packs(target, pack_specs, *, summary):
    for name, spec in sorted(pack_specs.items()):
        payload = spec.get("payload")
        if not isinstance(payload, dict):
            continue
        target[name] = payload
        summary[name] = dict(spec.get("artifact_metadata") or {})
        summary[_readiness_metadata_key(name)] = dict(spec.get("readiness_metadata") or {})
    summary.setdefault("sensor_evidence_artifact_refs", {}).update(
        _sensor_evidence_artifact_refs_for_packs(pack_specs)
    )


def _configured_evidence_pack_payload(pack_specs, name):
    spec = _configured_evidence_pack_spec(pack_specs, name)
    payload = spec.get("payload") if spec else None
    return payload if isinstance(payload, dict) else None


def _configured_evidence_pack_payloads(pack_specs):
    return {
        name: spec["payload"]
        for name, spec in sorted((pack_specs or {}).items())
        if isinstance(spec, dict) and isinstance(spec.get("payload"), dict)
    }


def _configured_evidence_pack_hashes(pack_specs):
    return {
        name: spec.get("sha256")
        for name, spec in sorted((pack_specs or {}).items())
        if isinstance(spec, dict) and isinstance(spec.get("payload"), dict)
    }


def _configured_evidence_pack_metadata(pack_specs, name):
    spec = _configured_evidence_pack_spec(pack_specs, name)
    metadata = spec.get("artifact_metadata") if spec else None
    return dict(metadata) if isinstance(metadata, dict) else None


def _configured_evidence_pack_readiness(pack_specs, name):
    spec = _configured_evidence_pack_spec(pack_specs, name)
    metadata = spec.get("readiness_metadata") if spec else None
    return dict(metadata) if isinstance(metadata, dict) else None


def _configured_evidence_pack_metadata_map(pack_specs, *, skip_names=None):
    skipped = set(skip_names or ())
    return {
        name: dict(spec.get("artifact_metadata") or {})
        for name, spec in sorted((pack_specs or {}).items())
        if name not in skipped
        and isinstance(spec, dict)
        and isinstance(spec.get("artifact_metadata"), dict)
    }


def _configured_evidence_pack_readiness_map(pack_specs, *, skip_names=None):
    skipped = set(skip_names or ())
    return {
        name: dict(spec.get("readiness_metadata") or {})
        for name, spec in sorted((pack_specs or {}).items())
        if name not in skipped
        and isinstance(spec, dict)
        and isinstance(spec.get("readiness_metadata"), dict)
    }


def _configured_evidence_pack_ref_specs(pack_specs):
    return {
        name: spec
        for name, spec in sorted((pack_specs or {}).items())
        if isinstance(spec, dict) and isinstance(spec.get("payload"), dict)
    }


def _configured_evidence_pack_spec(pack_specs, name):
    if not isinstance(pack_specs, dict):
        return None
    spec = pack_specs.get(name)
    return spec if isinstance(spec, dict) else None


def _readiness_metadata_key(artifact_name):
    if artifact_name.endswith("_evidence_pack"):
        return artifact_name.removesuffix("_evidence_pack") + "_readiness_metadata"
    return f"{artifact_name}_readiness_metadata"


def _mark_n_of_1_payload_boundary(payload):
    # Keep the public boundary stamp identical across derived artifacts so later
    # docs, manifests, and reports cannot imply real-world execution.
    payload.update(
        {
            "mock": True,
            "offline": True,
            "research_only": True,
            "sandbox_only": True,
            "simulated": True,
            "fake_backed": True,
            "local_only": True,
            "live_sensor_access": False,
            "hardware_access": False,
            "network_calls": False,
            "personal_data_exported": False,
            "personal_health_data_exported": False,
            "baseline_data_exported": False,
            "real_health_data_loaded": False,
            "real_profile_storage": False,
            "database_access": False,
            "raw_sensor_data_collected": False,
            "recommendation_generated": False,
            "prescription_generated": False,
            "medical_advice": False,
            "effectiveness_claim": False,
            "no_effectiveness_claim": True,
            "claim_effectiveness": False,
            "real_intervention_performed": False,
            "real_response_monitoring": False,
            "real_scheduling": False,
            "notification_automation": False,
            "reminder_automation": False,
            "external_memory": False,
            "diagnosis": False,
            "treatment_recommendation": False,
            "emergency_triage": False,
            "real_monitoring": False,
            "clinical_interpretation": False,
            "medical_or_clinical_claim": False,
        }
    )
    return payload


def _n_of_1_baseline_placeholder(workflow):
    return {
        "schema_version": 1,
        "id": "n-of-1-baseline-placeholder",
        "workflow_id": workflow.get("id"),
        "mock": True,
        "offline": True,
        "research_only": True,
        "local_baseline": "placeholder",
        "observation_window": "placeholder-window-local-only",
        "baseline_collection": "not-performed",
        "real_health_data_loaded": False,
        "real_health_data": False,
        "real_profile_storage": False,
        "personal_health_data_exported": False,
        "baseline_data_exported": False,
        "personal_data_exported": False,
        "live_sensor_access": False,
        "hardware_access": False,
        "network_calls": False,
        "database_access": False,
        "diagnosis": False,
        "treatment_recommendation": False,
        "emergency_triage": False,
        "real_monitoring": False,
        "clinical_interpretation": False,
        "medical_or_clinical_claim": False,
        "limitations": [
            "No real baseline was collected.",
            "No real health data was loaded.",
            "No real profile storage was performed.",
            "No CSI, camera, microphone, wearable, thermal, or environmental device was accessed.",
            "No clinical conclusion or emergency triage was produced.",
        ],
    }


def _n_of_1_summary(
    workflow,
    provider_status,
    stream_plan,
    observations,
    feature_set,
    csi_parser_report,
    csi_parsed_summary,
    csi_evidence_pack,
    environment_evidence_pack,
    evidence_record,
    baseline,
    personal_profile,
    baseline_graph,
    baseline_comparison,
    intervention_tag,
    intervention_context,
    response_evaluation_plan,
    mock_intervention_ledger,
    follow_up_observation_window,
    follow_up_sensor_snapshot,
    response_comparison,
    response_evaluation_summary,
    artifact_hashes,
    configured_sensor_evidence_packs=None,
):
    csi_metadata = feature_set.get("metadata", {}).get("csi", {})
    csi_evidence_scoring = dict(csi_parser_report.get("csi_evidence_scoring", {}))
    csi_evidence_pack_reference = csi_evidence_pack_artifact_metadata(
        csi_evidence_pack,
        artifact_sha256=artifact_hashes.get("csi_evidence_pack"),
    )
    sensor_evidence_artifact_refs = _csi_sensor_evidence_artifact_refs(
        csi_evidence_pack,
        artifact_hashes.get("csi_evidence_pack"),
    )
    environment_evidence_pack_reference = None
    if isinstance(environment_evidence_pack, dict):
        environment_evidence_pack_reference = _configured_evidence_pack_metadata(
            configured_sensor_evidence_packs,
            "environment_evidence_pack",
        ) or environment_evidence_pack_artifact_metadata(
            environment_evidence_pack,
            artifact_sha256=artifact_hashes.get("environment_evidence_pack"),
        )
    configured_sensor_evidence_metadata = _configured_evidence_pack_metadata_map(
        configured_sensor_evidence_packs,
        skip_names={"environment_evidence_pack"},
    )
    configured_sensor_evidence_readiness = _configured_evidence_pack_readiness_map(
        configured_sensor_evidence_packs,
        skip_names={"environment_evidence_pack"},
    )
    sensor_evidence_artifact_refs.update(
        _sensor_evidence_artifact_refs_for_packs(
            _configured_evidence_pack_ref_specs(configured_sensor_evidence_packs)
        )
    )
    csi_summary = build_csi_summary_metadata(
        workflow_mode=workflow.get("mode"),
        provider_id=provider_status["provider_id"],
        feature_set_id=feature_set["id"],
        sensor_evidence_record_id=evidence_record["id"],
        csi_metadata=csi_metadata,
    )
    csi_parser_metadata = {
        "schema_version": 1,
        "parser_id": csi_parser_report["parser_id"],
        "replay_provider": dict(csi_parser_report.get("replay_provider", {})),
        "replay_mode": csi_parser_report.get("replay_provider", {}).get(
            "mode",
            "fixture-replay",
        ),
        "status": csi_parser_report["status"],
        "fixture_count": csi_parser_report["fixture_count"],
        "source_formats": list(csi_parsed_summary["source_formats"]),
        "frame_count": csi_parser_report["frame_count"],
        "sample_count": csi_parser_report["sample_count"],
        "malformed_rows": csi_parser_report["malformed_rows"],
        "evidence_scoring": dict(csi_evidence_scoring),
        "artifact_refs": {
            "report": "artifacts/csi_parser_report.json",
            "summary": "artifacts/csi_parsed_summary.json",
            "evidence_pack": "artifacts/csi_evidence_pack.json",
        },
        "scope": "local fake/sample fixtures only",
        "summary_output_only": True,
        "fixture_replay_provider": True,
        "raw_signal_values_exported": False,
        "hardware_access": False,
        "network_calls": False,
        "serial_access": False,
        "mqtt_udp_listener": False,
        "packet_capture": False,
        "monitor_mode": False,
        "live_capture": False,
        "clinical_interpretation": False,
        "medical_or_clinical_claim": False,
    }
    return {
        "schema_version": 1,
        "id": "n-of-1-summary-sandbox",
        "workflow_id": workflow.get("id"),
        "workflow_mode": workflow.get("mode"),
        "provider_id": provider_status["provider_id"],
        "sensor_stream_plan_id": stream_plan["id"],
        "observation_count": len(observations["observations"]),
        "feature_set_id": feature_set["id"],
        "sensor_evidence_record_id": evidence_record["id"],
        "baseline_placeholder_id": baseline["id"],
        "personal_profile_id": personal_profile["id"],
        "baseline_graph_id": baseline_graph["id"],
        "baseline_comparison_id": baseline_comparison["id"],
        "intervention_tag_id": intervention_tag["id"],
        "intervention_context_id": intervention_context["id"],
        "response_evaluation_plan_id": response_evaluation_plan["id"],
        "mock_intervention_ledger_id": mock_intervention_ledger["id"],
        "follow_up_observation_window_id": follow_up_observation_window["id"],
        "follow_up_sensor_snapshot_id": follow_up_sensor_snapshot["id"],
        "response_comparison_id": response_comparison["id"],
        "response_evaluation_summary_id": response_evaluation_summary["id"],
        "csi_evidence_pack_id": csi_evidence_pack["id"],
        "csi_evidence_pack_ref": "artifacts/csi_evidence_pack.json",
        "environment_evidence_pack_id": (
            environment_evidence_pack.get("id")
            if isinstance(environment_evidence_pack, dict)
            else None
        ),
        "environment_evidence_pack_ref": (
            ENVIRONMENT_EVIDENCE_PACK_ARTIFACT_REF
            if isinstance(environment_evidence_pack, dict)
            else None
        ),
        "personal_profile_ref": "artifacts/personal_profile.json",
        "baseline_graph_ref": "artifacts/baseline_graph.json",
        "baseline_comparison_ref": "artifacts/baseline_comparison.json",
        "intervention_tag_ref": "artifacts/intervention_tag.json",
        "intervention_context_ref": "artifacts/intervention_context.json",
        "response_evaluation_plan_ref": "artifacts/response_evaluation_plan.json",
        "mock_intervention_ledger_ref": "artifacts/mock_intervention_ledger.json",
        "follow_up_observation_window_ref": "artifacts/follow_up_observation_window.json",
        "follow_up_sensor_snapshot_ref": "artifacts/follow_up_sensor_snapshot.json",
        "response_comparison_ref": "artifacts/response_comparison.json",
        "response_evaluation_summary_ref": "artifacts/response_evaluation_summary.json",
        "artifact_hashes": dict(artifact_hashes),
        "mock": True,
        "offline": True,
        "research_only": True,
        "sandbox_only": True,
        "fake_backed_sensor_planning_only": True,
        "fake_backed_local_baseline": True,
        "fake_backed_intervention_tags": True,
        "fake_backed_follow_up_generation": True,
        "response_evaluation_planning_only": True,
        "simulated": True,
        "live_sensor_access": False,
        "hardware_access": False,
        "network_calls": False,
        "database_access": False,
        "personal_data_exported": False,
        "personal_health_data_exported": False,
        "baseline_data_exported": False,
        "real_health_data_loaded": False,
        "real_profile_storage": False,
        "baseline_graph_local_only": True,
        "baseline_comparison_planning_only": True,
        "personal_profile_exported": False,
        "personal_baseline_medical_claim": False,
        "raw_sensor_data_collected": False,
        "recommendation_generated": False,
        "prescription_generated": False,
        "medical_advice": False,
        "effectiveness_claim": False,
        "no_effectiveness_claim": True,
        "claim_effectiveness": False,
        "real_intervention_performed": False,
        "real_response_monitoring": False,
        "real_scheduling": False,
        "notification_automation": False,
        "reminder_automation": False,
        "external_memory": False,
        "csi_capture": False,
        "csi_planning_only": True,
        "wifi_csi_capture": False,
        "packet_capture": False,
        "wifi_network_probing": False,
        "monitor_mode": False,
        "esp32_access": False,
        "rtl8812au_access": False,
        "router_access": False,
        "driver_access": False,
        "raw_rf_data_collected": False,
        "raw_csi_data_collected": False,
        "raw_rf_data_exported": False,
        "raw_csi_data_exported": False,
        "camera_capture": False,
        "audio_capture": False,
        "wearable_capture": False,
        "ble_access": False,
        "wifi_device_access": False,
        "thermal_capture": False,
        "real_monitoring": False,
        "diagnosis": False,
        "treatment_recommendation": False,
        "emergency_triage": False,
        "clinical_interpretation": False,
        "medical_or_clinical_claim": False,
        "feature_names": list(feature_set["features"]),
        "modalities": list(stream_plan["modalities"]),
        "baseline_categories": list(baseline_graph["categories"]),
        "baseline_comparison_summary": _baseline_comparison_summary(baseline_comparison),
        "intervention_summary": _intervention_summary(
            intervention_tag,
            intervention_context,
            response_evaluation_plan,
            mock_intervention_ledger,
        ),
        "response_trend_summary": _response_trend_summary(
            response_comparison,
            response_evaluation_summary,
        ),
        "response_trend_status_vocabulary": list(RESPONSE_TREND_STATUSES),
        "csi_metadata": csi_summary,
        "csi_parser_metadata": csi_parser_metadata,
        "csi_evidence_scoring_metadata": dict(csi_evidence_scoring),
        "csi_evidence_pack_metadata": csi_evidence_pack_reference,
        "environment_evidence_pack_metadata": environment_evidence_pack_reference,
        "environment_readiness_metadata": (
            _configured_evidence_pack_readiness(
                configured_sensor_evidence_packs,
                "environment_evidence_pack",
            )
            or _environment_readiness_metadata(environment_evidence_pack)
            if isinstance(environment_evidence_pack, dict)
            else {}
        ),
        "configured_sensor_evidence_pack_metadata": configured_sensor_evidence_metadata,
        "configured_sensor_evidence_readiness_metadata": (configured_sensor_evidence_readiness),
        "sensor_evidence_artifact_refs": sensor_evidence_artifact_refs,
        "blocked_actions": [
            "No real hardware access.",
            "No CSI, camera, audio, wearable, BLE, WiFi, thermal, or environmental capture.",
            "No WiFi CSI packet capture, monitor mode, or WiFi device probing.",
            "No ESP32, RTL8812AU, router, adapter, or driver access.",
            "No raw RF/CSI collection, retention, export, or remote upload.",
            "No network calls or external API calls.",
            "No real health data loading, profile storage, database, external memory, or "
            "baseline export.",
            "No recommendation, prescription, treatment recommendation, medication "
            "action, clinician action, or effectiveness claim.",
            "No intervention effectiveness claim, response recommendation, prescription, "
            "medical advice, or action.",
            "No reminders, automation, notification, scheduling, or real response monitoring.",
            "No real monitoring.",
            "No diagnosis, treatment, or emergency triage.",
            "No medical or clinical claims.",
        ],
        "future_real_mode_requirements": [
            "explicit user consent",
            "explicit local storage consent",
            "local-first privacy policy",
            "data-locality review",
            "privacy review",
            "retention and export controls",
            "safety review",
            "human review",
            "clinical review where applicable",
            "local storage controls",
            "no emergency-triage substitution",
            "separate opt-in configuration",
            "separate WiFi CSI hardware and raw RF privacy review",
        ],
    }


def _n_of_1_artifacts(n_of_1):
    artifacts = {
        name: {
            "relative_path": f"artifacts/{name}.json",
            "payload": n_of_1[name],
        }
        for name in (
            "sensor_stream_plan",
            "sensor_observations",
            "sensor_feature_set",
            "csi_parser_report",
            "csi_parsed_summary",
            "csi_evidence_pack",
            "sensor_evidence_record",
            "n_of_1_baseline_placeholder",
            "personal_profile",
            "baseline_graph",
            "baseline_comparison",
            "intervention_tag",
            "intervention_context",
            "response_evaluation_plan",
            "mock_intervention_ledger",
            "follow_up_observation_window",
            "follow_up_sensor_snapshot",
            "response_comparison",
            "response_evaluation_summary",
            "n_of_1_summary",
            "n_of_1_report_packet",
            "n_of_1_fabric_pack_plan",
        )
        if isinstance(n_of_1.get(name), dict)
    }
    _add_sensor_evidence_pack_artifacts(artifacts, n_of_1)
    return artifacts


def _baseline_comparison_summary(baseline_comparison):
    results = list(baseline_comparison["results"])
    status_by_category = {result["category"]: result["status"] for result in results}
    return {
        "comparison_status": baseline_comparison["comparison_status"],
        "status_counts": dict(baseline_comparison["status_counts"]),
        "status_by_category": status_by_category,
        "outside_baseline_categories": [
            result["category"] for result in results if result["status"] == "outside_baseline"
        ],
        "insufficient_data_categories": [
            result["category"] for result in results if result["status"] == "insufficient_data"
        ],
        "fake_backed_local_baseline": True,
        "real_health_data_loaded": False,
        "real_profile_storage": False,
        "personal_data_exported": False,
        "diagnosis": False,
        "treatment_recommendation": False,
        "emergency_triage": False,
        "medical_or_clinical_claim": False,
    }


def _intervention_summary(
    intervention_tag,
    intervention_context,
    response_evaluation_plan,
    mock_intervention_ledger,
):
    return {
        "intervention_tag_id": intervention_tag["id"],
        "intervention_context_id": intervention_context["id"],
        "response_evaluation_plan_id": response_evaluation_plan["id"],
        "mock_intervention_ledger_id": mock_intervention_ledger["id"],
        "category": intervention_tag["category"],
        "category_statuses": list(intervention_tag["category_statuses"]),
        "metrics_to_recheck": list(response_evaluation_plan["metrics_to_recheck"]),
        "future_comparison_window": response_evaluation_plan["future_comparison_window"],
        "recommendation_generated": False,
        "prescription_generated": False,
        "treatment_recommendation": False,
        "medical_advice": False,
        "claim_effectiveness": False,
        "real_intervention_performed": False,
        "real_monitoring": False,
        "real_scheduling": False,
        "notification_automation": False,
        "reminder_automation": False,
        "medication_placeholder_disabled": True,
        "clinician_review_placeholder_disabled": True,
    }


def _response_trend_summary(response_comparison, response_evaluation_summary):
    results = list(response_comparison["results"])
    return {
        "response_comparison_id": response_comparison["id"],
        "response_evaluation_summary_id": response_evaluation_summary["id"],
        "trend_counts": dict(response_evaluation_summary["trend_counts"]),
        "status_by_category": dict(response_evaluation_summary["status_by_category"]),
        "toward_baseline_categories": list(
            response_evaluation_summary["toward_baseline_categories"]
        ),
        "away_from_baseline_categories": list(
            response_evaluation_summary["away_from_baseline_categories"]
        ),
        "unchanged_categories": list(response_evaluation_summary["unchanged_categories"]),
        "insufficient_data_categories": list(
            response_evaluation_summary["insufficient_data_categories"]
        ),
        "result_count": len(results),
        "trend_status_vocabulary": list(RESPONSE_TREND_STATUSES),
        "fixture_trend_labels_only": True,
        "effectiveness_claim": False,
        "claim_effectiveness": False,
        "recommendation_generated": False,
        "prescription_generated": False,
        "treatment_recommendation": False,
        "medical_advice": False,
        "real_monitoring": False,
        "real_response_monitoring": False,
        "real_scheduling": False,
        "notification_automation": False,
        "reminder_automation": False,
    }


def _n_of_1_next_iteration(summary):
    return {
        "schema_version": 1,
        "mock": True,
        "offline": True,
        "workflow_mode": "n-of-1",
        "recommended_mode": "fake-backed-sensor-planning",
        "sensor_evidence_record_id": summary["sensor_evidence_record_id"],
        "baseline_comparison_id": summary["baseline_comparison_id"],
        "intervention_tag_id": summary["intervention_tag_id"],
        "response_comparison_id": summary["response_comparison_id"],
        "recommended_actions": [
            "Review the fake-backed sensor plan and privacy policy with a human reviewer.",
            "Review the fake-backed local baseline comparison boundary with a human reviewer.",
            "Review the mock intervention tag and response-evaluation boundary with a "
            "human reviewer.",
            "Review the fake-backed response trend labels as non-clinical planning metadata only.",
            "Keep future real sensor adapters disabled until explicit consent and safety "
            "review exist.",
            "Keep future real baseline storage disabled until explicit local storage "
            "consent and data-locality review exist.",
            "Keep future real intervention use disabled until consent, human review, "
            "clinical review where applicable, local storage controls, and safety gates exist.",
            "Add local-only schema fixtures before considering any live capture mode.",
        ],
        "blocked_actions": list(summary["blocked_actions"]),
        "future_real_mode_requirements": list(summary["future_real_mode_requirements"]),
    }


def _render_n_of_1_report(workflow, provider_metadata, safety_response, n_of_1):
    provider_lines = "\n".join(
        "- "
        f"`{ref}`: `{metadata.get('provider_id') or metadata.get('id')}` ({metadata.get('class')})"
        for ref, metadata in sorted(provider_metadata.items())
    )
    plan = n_of_1["sensor_stream_plan"]
    observations = n_of_1["sensor_observations"]
    feature_set = n_of_1["sensor_feature_set"]
    evidence_record = n_of_1["sensor_evidence_record"]
    baseline = n_of_1["n_of_1_baseline_placeholder"]
    personal_profile = n_of_1["personal_profile"]
    baseline_graph = n_of_1["baseline_graph"]
    baseline_comparison = n_of_1["baseline_comparison"]
    intervention_tag = n_of_1["intervention_tag"]
    intervention_context = n_of_1["intervention_context"]
    response_plan = n_of_1["response_evaluation_plan"]
    intervention_ledger = n_of_1["mock_intervention_ledger"]
    follow_up_window = n_of_1["follow_up_observation_window"]
    follow_up_snapshot = n_of_1["follow_up_sensor_snapshot"]
    response_comparison = n_of_1["response_comparison"]
    response_eval_summary = n_of_1["response_evaluation_summary"]
    summary = n_of_1["n_of_1_summary"]
    report_packet = n_of_1["n_of_1_report_packet"]
    fabric_pack_plan = n_of_1["n_of_1_fabric_pack_plan"]
    feature_lines = "\n".join(
        f"- `{name}`: `{value}`" for name, value in feature_set["features"].items()
    )
    csi_summary = summary["csi_metadata"]
    csi_parser_metadata = summary["csi_parser_metadata"]
    csi_evidence_scoring = summary["csi_evidence_scoring_metadata"]
    csi_evidence_pack_metadata = summary["csi_evidence_pack_metadata"]
    environment_evidence_pack_metadata = summary.get("environment_evidence_pack_metadata") or {}
    environment_readiness_metadata = summary.get("environment_readiness_metadata") or {}
    csi_sensor_evidence_ref = summary.get("sensor_evidence_artifact_refs", {}).get(
        "csi_evidence_pack",
        {},
    )
    csi_ruview_reference = dict(csi_summary.get("ruview_reference", {}))
    csi_booth_profile = dict(csi_summary.get("booth_planning_profile", {}))
    csi_source_adapter_status = dict(csi_summary.get("source_adapter_status", {}))
    csi_source_adapter_validation = dict(csi_summary.get("source_adapter_output_validation", {}))
    csi_real_mode_gate = dict(csi_source_adapter_status.get("real_mode_readiness_gate", {}))
    csi_source_adapter_labels = ", ".join(
        str(label) for label in csi_source_adapter_status.get("capability_labels", ())
    )
    csi_booth_notes = ", ".join(
        str(label) for label in csi_booth_profile.get("research_note_labels", ())
    )
    environment_sensor_evidence_ref = summary.get(
        "sensor_evidence_artifact_refs",
        {},
    ).get("environment_evidence_pack", {})
    environment_pack_lines = ""
    if environment_evidence_pack_metadata:
        environment_pack_lines = f"""
## Environment Fixture Evidence Pack

- Environment evidence pack: `{environment_evidence_pack_metadata.get("artifact_ref")}`
- Environment evidence pack status: `{environment_evidence_pack_metadata.get("status")}`
- Environment evidence pack fingerprint: `{environment_evidence_pack_metadata.get("pack_fingerprint")}`
- Environment row count: `{environment_readiness_metadata.get("row_count")}`
- Environment generic evidence ref: `{environment_sensor_evidence_ref.get("artifact_ref")}`
- Environment generic evidence SHA-256: `{environment_sensor_evidence_ref.get("sha256")}`
"""
    csi_feature_lines = "\n".join(f"- `{name}`" for name in csi_summary["mapped_feature_names"])
    csi_parser_format_lines = "\n".join(
        f"- `{name}`" for name in csi_parser_metadata["source_formats"]
    )
    baseline_summary = summary["baseline_comparison_summary"]
    baseline_status_lines = "\n".join(
        (f"- `{result['category']}`: `{result['status']}` ({result['deviation_note']})")
        for result in baseline_comparison["results"]
    )
    intervention_summary = summary["intervention_summary"]
    intervention_category_lines = "\n".join(
        (f"- `{item['category']}`: `{item['status']}` (disabled: `{item['disabled']}`)")
        for item in intervention_tag["category_statuses"]
    )
    response_metric_lines = "\n".join(f"- `{name}`" for name in response_plan["metrics_to_recheck"])
    response_trend_lines = "\n".join(
        (f"- `{result['category']}`: `{result['trend_label']}` ({result['comparison_note']})")
        for result in response_comparison["results"]
    )
    follow_up_feature_lines = "\n".join(
        f"- `{name}`: `{value}`" for name, value in follow_up_snapshot["features"].items()
    )
    blocked_actions = "\n".join(f"- {item}" for item in summary["blocked_actions"])
    future_requirements = "\n".join(
        f"- {item}" for item in summary["future_real_mode_requirements"]
    )
    packet_stage_lines = "\n".join(
        (
            f"- `{stage['stage']}`: {stage['present_count']} present, "
            f"{stage['missing_count']} missing"
        )
        for stage in report_packet["loop_stages"]
    )
    packet_boundary_lines = "\n".join(
        f"- `{name}`: `{value}`" for name, value in report_packet["safety_boundary_flags"].items()
    )
    fabric_file_lines = "\n".join(
        (f"- `{file_plan['id']}`: `{file_plan['path']}` (`{file_plan['sha256']}`)")
        for file_plan in fabric_pack_plan["file_plans"]
    )
    return f"""# Somatic N-of-1 Sensor Planning Report

This is fake-backed sensor planning only. It is mock/offline/research-only and sandbox-only metadata from the local Somatic runner.

## Workflow

- ID: `{workflow.get("id")}`
- Mode: `{workflow.get("mode")}`
- Status: mock/offline
- Provider: `{summary["provider_id"]}`

## N-of-1 Report Packet

The consolidated n-of-1 report packet is `artifacts/n_of_1_report_packet.json`. It is fake-backed/local/research-only. The packet is not a medical record and is not a health record. Hashes are for reproducibility/provenance only; they do not imply intervention effectiveness, clinical validity, treatment guidance, monitoring, scheduling, or advice.

### Artifact Count/Hash Summary

- Report packet: `{report_packet["id"]}`
- Packet status: `{report_packet["packet_status"]}`
- Packet complete: `{report_packet["packet_complete"]}`
- Artifact count: `{report_packet["artifact_count"]}`
- Present artifact count: `{report_packet["present_artifact_count"]}`
- Missing artifacts: {", ".join(report_packet["missing_artifacts"]) or "none"}
- Hash algorithm: `sha256`
- Hash scope: `json-dumps-indent-2-sort-keys-newline`
- Hash purpose: reproducibility/provenance only

### Loop-Stage Summary

{packet_stage_lines}

### Strict Boundary Summary

This packet generates no effectiveness claim, no advice, no recommendation, no prescription, no treatment recommendation, no medical advice, no diagnosis, no emergency triage, no real monitoring, and no reminders, automation, notification, or scheduling.

{packet_boundary_lines}

## N-of-1 Fabric Pack Plan

The n-of-1 Fabric pack plan is `artifacts/n_of_1_fabric_pack_plan.json`. The n-of-1 Fabric pack plan is planning-only and private-only by default. It is not a Content Fabric `pack.json` manifest and does not create, sign, publish, seed, transport, install, enable, or execute a pack.

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding, upload, install, or execution is enabled. No real personal data export is performed. No real personal data, personal health data, baseline data, raw sensor data, raw RF/CSI data, or health record is exported. Hashes are for local reproducibility/provenance only and do not imply clinical validity, monitoring, intervention effectiveness, treatment guidance, or advice.

- Class recommendation: `{fabric_pack_plan["class"]}`
- Suggested type: `{fabric_pack_plan["suggested_type"]}`
- Alternate type: `{fabric_pack_plan["alternate_suggested_type"]}`
- Report packet ref: `{fabric_pack_plan["report_packet_ref"]}`
- Report packet sha256: `{fabric_pack_plan["report_packet_sha256"]}`
- Publishing enabled: `{fabric_pack_plan["publishing_enabled"]}`
- Signing enabled: `{fabric_pack_plan["signing_enabled"]}`
- Catalog publication enabled: `{fabric_pack_plan["catalog_publication_enabled"]}`
- Transport enabled: `{fabric_pack_plan["transport_enabled"]}`
- Seedable: `{fabric_pack_plan["seedable"]}`
- Contains code: `{fabric_pack_plan["contains_code"]}`
- Contains executable files: `{fabric_pack_plan["contains_executable_files"]}`
- Personal health data exported: `{fabric_pack_plan["personal_health_data_exported"]}`
- Raw real health data allowed: `{fabric_pack_plan["raw_real_health_data_allowed"]}`

### Planned Local File Refs

{fabric_file_lines}

## Providers

{provider_lines or "- No provider metadata loaded."}

## Sensor Planning Summary

- Stream plan: `{plan["id"]}`
- Modalities: {", ".join(plan["modalities"])}
- Observation window: `{plan["observation_window"]}`
- Baseline placeholder: `{baseline["id"]}`
- Observation records: {len(observations["observations"])}
- Feature set: `{feature_set["id"]}`
- Evidence record: `{evidence_record["id"]}`
- Raw evidence: `{evidence_record["raw_evidence"]["id"]}`
- Structured verdict: `{evidence_record["structured_verdict"]["id"]}`

## Personal Baseline Planning

This is a fake-backed local baseline scaffold. No real health data is loaded, no real profile storage is performed, and the baseline comparison is not medical advice, diagnosis, treatment, clinical interpretation, monitoring, or emergency triage.

- Personal profile: `{personal_profile["id"]}`
- Baseline graph: `{baseline_graph["id"]}`
- Baseline comparison: `{baseline_comparison["id"]}`
- Comparison status: `{baseline_summary["comparison_status"]}`
- Status vocabulary: `within_baseline`, `outside_baseline`, `insufficient_data`
- Status counts: `{baseline_summary["status_counts"]}`
- Baseline graph local only: `{summary["baseline_graph_local_only"]}`
- Baseline comparison planning only: `{summary["baseline_comparison_planning_only"]}`
- Fake-backed local baseline: `{summary["fake_backed_local_baseline"]}`
- No real health data: `{not summary["real_health_data_loaded"]}`
- No real profile storage: `{not summary["real_profile_storage"]}`
- Personal health data exported: `{summary["personal_health_data_exported"]}`

### Baseline Comparison Results

{baseline_status_lines}

## N-of-1 Intervention Tagging

This is a mock intervention tag summary for local research planning only. It records a fake-backed event label and response evaluation plan summary. It provides no recommendation, no prescription, no treatment recommendation, no medical advice, no medication action, no clinician action, no effectiveness claim, no real monitoring, and no emergency triage.

- Intervention tag: `{intervention_tag["id"]}`
- Intervention category: `{intervention_tag["category"]}`
- Intervention context: `{intervention_context["id"]}`
- Response evaluation plan: `{response_plan["id"]}`
- Mock intervention ledger: `{intervention_ledger["id"]}`
- Medication placeholder disabled: `{intervention_summary["medication_placeholder_disabled"]}`
- Clinician review placeholder disabled: `{intervention_summary["clinician_review_placeholder_disabled"]}`
- Recommendation generated: `{intervention_summary["recommendation_generated"]}`
- Prescription generated: `{intervention_summary["prescription_generated"]}`
- Treatment recommendation generated: `{intervention_summary["treatment_recommendation"]}`
- Effectiveness claim generated: `{intervention_summary["claim_effectiveness"]}`
- Real scheduling: `{intervention_summary["real_scheduling"]}`
- Real monitoring: `{intervention_summary["real_monitoring"]}`
- No reminders, automation, or scheduling: true

### Intervention Category Status

{intervention_category_lines}

### Response Evaluation Plan Summary

- Future comparison window: `{response_plan["future_comparison_window"]}`
- No real scheduling: `{not response_plan["real_scheduling"]}`
- No real monitoring: `{not response_plan["real_monitoring"]}`
- No notification automation: `{not response_plan["notification_automation"]}`
- No reminder automation: `{not response_plan["reminder_automation"]}`
- No recommendation: `{not response_plan["recommendation_generated"]}`
- No prescription: `{not response_plan["prescription_generated"]}`
- No medical advice: `{not response_plan["medical_advice"]}`
- No effectiveness claim: `{not response_plan["claim_effectiveness"]}`

Metrics to re-check:

{response_metric_lines}

## N-of-1 Response Evaluation

Follow-up comparison is deterministic fake-backed placeholder metadata. Trend status describes movement relative to a placeholder baseline only; it is not an effectiveness claim, medical advice, monitoring result, treatment recommendation, diagnosis, or emergency triage. These are fixture trend labels only. No intervention effectiveness is claimed.

### Follow-Up Observation Window Summary

- Follow-up observation window: `{follow_up_window["id"]}`
- Source response evaluation plan: `{follow_up_window["source_plan_id"]}`
- Relative start: `{follow_up_window["relative_start"]}`
- Relative end: `{follow_up_window["relative_end"]}`
- Response evaluation is future planning only, not real monitoring: true
- No real scheduling: `{not follow_up_window["real_scheduling"]}`
- No real monitoring: `{not follow_up_window["real_monitoring"]}`
- No reminders, automation, notification, or scheduling: true

### Follow-Up Snapshot Features

{follow_up_feature_lines}

### Response Comparison Summary

- Response comparison: `{response_comparison["id"]}`
- Response trend status vocabulary: {", ".join(response_comparison["trend_status_vocabulary"])}
- Mechanical placeholder comparison: true
- No effectiveness claim: `{not response_comparison["effectiveness_claim"]}`
- No recommendation: `{not response_comparison["recommendation_generated"]}`
- No prescription: `{not response_comparison["prescription_generated"]}`
- No medical advice: `{not response_comparison["medical_advice"]}`

{response_trend_lines}

### Response Evaluation Summary

- Response evaluation summary: `{response_eval_summary["id"]}`
- Trend counts: `{response_eval_summary["trend_counts"]}`
- Toward baseline categories: {", ".join(response_eval_summary["toward_baseline_categories"]) or "none"}
- Unchanged categories: {", ".join(response_eval_summary["unchanged_categories"]) or "none"}
- Insufficient data categories: {", ".join(response_eval_summary["insufficient_data_categories"]) or "none"}
- No intervention effectiveness is claimed: true
- No effectiveness claim: `{not response_eval_summary["effectiveness_claim"]}`
- No recommendation: `{not response_eval_summary["recommendation_generated"]}`
- No prescription: `{not response_eval_summary["prescription_generated"]}`
- No medical advice: `{not response_eval_summary["medical_advice"]}`
- No real monitoring: `{not response_eval_summary["real_monitoring"]}`
- No reminders, automation, or scheduling: true

## Placeholder Features

{feature_lines}

## WiFi CSI Planning Metadata

- CSI status: `{csi_summary["status"]}`
- CSI planning only: `{csi_summary["planning_only"]}`
- CSI disabled by default: `{csi_summary["disabled_by_default"]}`
- CSI capture plan: `{csi_summary["csi_capture_plan_id"]}`
- CSI feature set: `{csi_summary["csi_feature_set_id"]}`
- CSI reference inventory: `{csi_summary["reference_inventory_ref"]}`
- CSI hardware access: `{csi_summary["hardware_access"]}`
- CSI packet capture: `{csi_summary["packet_capture"]}`
- CSI WiFi network probing: `{csi_summary["wifi_network_probing"]}`
- CSI monitor mode: `{csi_summary["monitor_mode"]}`
- CSI raw RF data collected: `{csi_summary["raw_rf_data_collected"]}`
- CSI raw CSI data collected: `{csi_summary["raw_csi_data_collected"]}`
- CSI raw RF data exported: `{csi_summary["raw_rf_data_exported"]}`
- CSI raw CSI data exported: `{csi_summary["raw_csi_data_exported"]}`
- CSI clinical interpretation: `{csi_summary["clinical_interpretation"]}`
- RuView dependency: `{csi_summary["ruview_dependency"]}`
- RuView reference status: `{csi_ruview_reference.get("status")}`
- RuView downstream accuracy validated: `{csi_ruview_reference.get("v2_reassessment", {}).get("downstream_accuracy_validated")}`
- RuView deployment claims verified: `{csi_ruview_reference.get("v2_reassessment", {}).get("deployment_claims_verified")}`
- CSI source adapter: `{csi_source_adapter_status.get("adapter_kind")}`
- CSI source adapter validation: `{csi_source_adapter_validation.get("classification")}`
- CSI source adapter boundary labels: {csi_source_adapter_labels}
- Booth-first profile: `{csi_booth_profile.get("profile")}`
- Booth scope: single subject in a small controlled booth
- Booth future topology: `{csi_booth_profile.get("future_topology")}`
- Booth preferred radio family: `{csi_booth_profile.get("preferred_radio_family")}`
- Booth empty baseline concept: `{csi_booth_profile.get("empty_booth_baseline")}`
- Booth broad room adaptation logic: `{csi_booth_profile.get("room_adaptation_logic")}`
- Booth research notes: {csi_booth_notes}
- CSI model download: `{csi_source_adapter_status.get("model_download")}`
- CSI model execution: `{csi_source_adapter_status.get("model_execution")}`
- CSI vitals inference: `{csi_source_adapter_status.get("vitals_inference")}`
- CSI real-mode readiness gate: `{csi_real_mode_gate.get("status")}`
- CSI real-mode missing gates: {csi_real_mode_gate.get("missing_gate_count")}
- CSI real-mode execution permitted: `{csi_real_mode_gate.get("execution_permitted")}`

### CSI Placeholder Feature Names

{csi_feature_lines}

## WiFi CSI Parser Metadata

The CSI parser report is `artifacts/csi_parser_report.json` and the parsed summary is `artifacts/csi_parsed_summary.json`. They are local fake/sample fixtures only. No serial, MQTT, UDP, pcap, monitor mode, or live capture is used. The parser output is summary metadata only; it is not signal processing output, vital-sign inference, medical advice, diagnosis, treatment, monitoring, or emergency triage.

- CSI parser: `{csi_parser_metadata["parser_id"]}`
- CSI parser status: `{csi_parser_metadata["status"]}`
- CSI parser fixtures: `{csi_parser_metadata["fixture_count"]}`
- CSI parser frames: `{csi_parser_metadata["frame_count"]}`
- CSI parser sample count: `{csi_parser_metadata["sample_count"]}`
- CSI parser malformed rows: `{csi_parser_metadata["malformed_rows"]}`
- CSI evidence quality score: `{csi_evidence_scoring["evidence_quality"]}` / 100
- CSI replay integrity score: `{csi_evidence_scoring["replay_integrity"]}` / 100
- CSI scoring status: `{csi_evidence_scoring["status"]}`
- CSI scoring status counts: `{csi_evidence_scoring["status_counts"]}`
- CSI evidence pack: `{csi_evidence_pack_metadata["artifact_ref"]}`
- CSI evidence pack status: `{csi_evidence_pack_metadata["status"]}`
- CSI evidence pack fingerprint: `{csi_evidence_pack_metadata["pack_fingerprint"]}`
- Generic sensor evidence ref: `{csi_sensor_evidence_ref.get("artifact_ref")}`
- Generic sensor evidence SHA-256: `{csi_sensor_evidence_ref.get("sha256")}`
{environment_pack_lines}
- CSI parser report ref: `{csi_parser_metadata["artifact_refs"]["report"]}`
- CSI parsed summary ref: `{csi_parser_metadata["artifact_refs"]["summary"]}`
- CSI parser hardware access: `{csi_parser_metadata["hardware_access"]}`
- CSI parser serial access: `{csi_parser_metadata["serial_access"]}`
- CSI parser network calls: `{csi_parser_metadata["network_calls"]}`
- CSI parser packet capture: `{csi_parser_metadata["packet_capture"]}`
- CSI parser monitor mode: `{csi_parser_metadata["monitor_mode"]}`
- CSI parser medical or clinical claim: `{csi_parser_metadata["medical_or_clinical_claim"]}`

### CSI Parser Source Formats

{csi_parser_format_lines}

## Safety Summary

- Safety response: `{safety_response.get("id")}`
- Decision: `{safety_response.get("decision")}`
- Human review required: `{safety_response.get("human_review", {}).get("required")}`
- External actions allowed: `{workflow.get("safety_profile", {}).get("external_actions_allowed")}`
- Research-only boundary: true

## Boundaries

- fake-backed sensor planning only: true
- mock/offline: true
- research-only / sandbox-only: true
- no real hardware access: true
- no live sensor access: true
- no CSI/camera/audio/wearable capture: true
- no WiFi CSI packet capture, monitor mode, or WiFi device probing: true
- no ESP32, RTL8812AU, router, adapter, or driver access: true
- raw RF/CSI data is local-first and private by default: true
- raw RF/CSI data collected: false
- raw RF/CSI data exported: false
- no BLE, WiFi device, thermal, environmental, camera, microphone, or wearable device access: true
- no network calls or external API calls: true
- fake-backed local baseline notice: true
- mock intervention tag summary: true
- response evaluation plan summary: true
- follow-up observation window summary: true
- response comparison summary: true
- response evaluation summary: true
- fixture trend labels only: true
- no recommendation: true
- no prescription: true
- no effectiveness claim: true
- no intervention effectiveness is claimed: true
- medication placeholder disabled: true
- clinician review placeholder disabled: true
- no reminders, automation, or scheduling: true
- response evaluation is future planning, not real monitoring: true
- no real health data loaded: true
- no real profile storage: true
- baseline graph local-only: true
- personal health data exported: false
- no real monitoring: true
- no diagnosis, treatment, or emergency triage: true
- no medical or clinical claims: true
- not medical advice: true
- raw sensor data leaves machine: false
- personal data exported: false

## Blocked Runtime Actions

{blocked_actions}

## Future Real Sensor Mode Requirements

future real sensor mode requires explicit user consent, local-first privacy policy, and safety review before any runtime adapter is enabled.

future real baseline requires explicit local storage consent, data-locality review, privacy review, safety review, human review, retention/export controls, and separate opt-in configuration before any real profile or baseline storage is enabled.

future real intervention tag use requires explicit consent, human review, clinical review where applicable, local storage controls, safety gates, and no emergency-triage substitution before any real response evaluation path is enabled.

{future_requirements}
"""


def _render_in_silico_report(workflow, provider_metadata, safety_response, in_silico):
    provider_lines = "\n".join(
        "- "
        f"`{ref}`: `{metadata.get('provider_id') or metadata.get('id')}` ({metadata.get('class')})"
        for ref, metadata in sorted(provider_metadata.items())
    )
    request = in_silico["biomodel_request"]
    readiness = in_silico["biomodel_readiness_report"]
    consent = in_silico["biomodel_consent_record"]
    plan = in_silico["biomodel_plan"]
    result = in_silico["biomodel_result"]
    raw = in_silico["biomodel_raw_evidence"]
    verdict = in_silico["biomodel_structured_verdict"]
    provenance = in_silico["biomodel_provenance_bundle"]
    pack_plan = in_silico["biomodel_pack_plan"]
    summary = in_silico["in_silico_summary"]
    blocked_actions = "\n".join(f"- {item}" for item in summary["blocked_actions"])
    future_requirements = "\n".join(
        f"- {item}" for item in summary["future_real_mode_requirements"]
    )
    readiness_reasons = "\n".join(f"- {item}" for item in readiness["block_reasons"])
    return f"""# Somatic In-Silico Screening Report

This is fake-backed planning only. It is mock/offline/research-only metadata from the local Somatic runner.

## Workflow

- ID: `{workflow.get("id")}`
- Mode: `{workflow.get("mode")}`
- Status: mock/offline
- Provider: `{summary["provider_id"]}`

## Providers

{provider_lines or "- No provider metadata loaded."}

## Biomodel Planning Summary

- Request objective: {request["objective"]}
- Target refs: {", ".join(request.get("target_refs", []))}
- Input artifact refs: {", ".join(request.get("input_artifact_refs", []))}
- Plan ID: `{plan["id"]}`
- Plan status: `{plan["status"]}`
- Result ID: `{result["id"]}`
- Result status: `{result["status"]}`
- Evidence modality: `{raw["source"]["modality"]}`
- Evidence submodality: `{raw["source"]["metadata"].get("submodality")}`
- Structured verdict: `{verdict["id"]}`
- Confidence: `{verdict["confidence"]}`
- Provenance bundle: `{provenance["id"]}`
- Pack plan: `{pack_plan["id"]}`

## Safety Summary

- Safety response: `{safety_response.get("id")}`
- Decision: `{safety_response.get("decision")}`
- Human review required: `{safety_response.get("human_review", {}).get("required")}`
- External actions allowed: `{workflow.get("safety_profile", {}).get("external_actions_allowed")}`
- Real lab action requires approval: `{workflow.get("safety_profile", {}).get("real_lab_action_requires_approval")}`
- Biomodel safety gates: scaffolded
- Readiness ready for real runtime: `{readiness["ready"]}`
- Runtime execution permitted: `{readiness["execution_permitted"]}`
- Real biomodel runtime: future only
- User consent recorded: `{consent["user_consent"]}`
- Research-only boundary acknowledged: `{consent["research_only_acknowledged"]}`

## Boundaries

- fake-backed planning only: true
- no Boltz execution: true
- no model weights downloaded: true
- no MSA server call: true
- no GPU/runtime execution: true
- no real structure or affinity prediction: true
- no medical, lab, or scientific conclusion: true
- no external API calls or network calls: true
- no provider secrets were used.
- no package downloads were performed.

## Biomodel Provenance Packaging

- biomodel provenance packaging: planning only
- recommended Fabric pack class: `{pack_plan["pack_class"]}`
- recommended Fabric candidate type: `{pack_plan["candidate_type"]}`
- code pack: `{pack_plan["code_pack"]}`
- executable files: `{len(pack_plan["executable_files"])}`
- publishing enabled: `{pack_plan["publishing_enabled"]}`
- catalog publishing enabled: `{pack_plan["catalog_publish_enabled"]}`
- signing enabled: `{pack_plan["signing_enabled"]}`
- signed pack created: `{pack_plan["signed_pack_created"]}`
- transport status: `{pack_plan["transport_status"]}`
- license review required: `{pack_plan["license_review_required"]}`
- no Fabric publishing or transport is enabled.
- no Fabric pack install or execution is enabled.

## Biomodel Readiness Block Reasons

{readiness_reasons}

## Blocked Runtime Actions

{blocked_actions}

## Future Real Mode Requirements

future real mode requires explicit opt-in, resource checks, provenance, and safety review before any runtime adapter is enabled.

{future_requirements}
"""


def _schema_artifact(payload):
    artifact = {"schema_version": 1}
    artifact.update(payload)
    return artifact


def _add_sensor_evidence_pack_artifacts(artifacts, payloads):
    for entry in list_sensor_evidence_providers():
        payload = payloads.get(entry.artifact_name)
        if not isinstance(payload, dict):
            continue
        artifacts[entry.artifact_name] = {
            "relative_path": entry.artifact_ref,
            "payload": payload,
            "sensor_evidence_ref": entry.artifact_ref_spec(),
        }


def _artifact_payload_sha256(payload):
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return sha256(encoded).hexdigest()


def _csi_sensor_evidence_artifact_refs(csi_evidence_pack, artifact_sha256):
    return _sensor_evidence_artifact_refs_for_packs(
        {
            "csi_evidence_pack": {
                "payload": csi_evidence_pack,
                "relative_path": CSI_EVIDENCE_PACK_ARTIFACT_REF,
                "sha256": artifact_sha256,
            }
        }
    )


def _sensor_evidence_artifact_refs_for_packs(pack_specs):
    refs = {}
    for name, spec in sorted(pack_specs.items()):
        if not isinstance(spec, dict):
            continue
        payload = spec.get("payload")
        if not isinstance(payload, dict):
            continue
        entry = sensor_evidence_provider_by_artifact_name(name)
        provider_kind = (
            spec.get("provider_kind")
            or payload.get("provider_kind")
            or (entry.provider_kind if entry is not None else None)
        )
        evidence_kind = (
            spec.get("evidence_kind")
            or payload.get("evidence_kind")
            or (entry.evidence_kind if entry is not None else None)
        )
        if not provider_kind or not evidence_kind:
            continue
        refs[name] = build_sensor_evidence_artifact_ref(
            name,
            spec.get("relative_path")
            or (entry.artifact_ref if entry is not None else f"artifacts/{name}.json"),
            artifact_sha256=spec.get("sha256"),
            evidence_pack=payload,
            provider_kind=provider_kind,
            evidence_kind=evidence_kind,
        )
    return refs


def _sensor_evidence_ref_marker(artifact_name):
    entry = sensor_evidence_provider_by_artifact_name(artifact_name)
    return entry.artifact_ref_spec() if entry is not None else {}


def _environment_readiness_metadata(environment_evidence_pack):
    metadata = _sensor_evidence_readiness_metadata(environment_evidence_pack)
    metadata.pop("fixture_count", None)
    return metadata


def _sensor_evidence_readiness_metadata(evidence_pack):
    counts = dict(evidence_pack.get("counts", {}))
    scores = dict(evidence_pack.get("scores", {}))
    status_counts = dict(evidence_pack.get("status_counts", {}))
    metadata = {
        "schema_version": 1,
        "provider_kind": evidence_pack.get("provider_kind"),
        "evidence_kind": evidence_pack.get("evidence_kind"),
        "status": evidence_pack.get("status"),
        "readiness_status": evidence_pack.get("readiness_status"),
        "metadata_only": True,
        "fixture_only": True,
        "fixture_count": counts.get("fixture_count", 0),
        "row_count": counts.get("row_count", 0),
        "parsed_row_count": counts.get("parsed_row_count", 0),
        "partial_row_count": counts.get("partial_row_count", 0),
        "rejected_row_count": counts.get("rejected_row_count", 0),
        "document_count": counts.get("document_count", 0),
        "parsed_document_count": counts.get("parsed_document_count", 0),
        "partial_document_count": counts.get("partial_document_count", 0),
        "rejected_document_count": counts.get("rejected_document_count", 0),
        "total_word_count": counts.get("total_word_count", 0),
        "total_line_count": counts.get("total_line_count", 0),
        "total_char_count": counts.get("total_char_count", 0),
        "format_count": counts.get("format_count", 0),
        "status_counts": status_counts,
        "evidence_quality": scores.get("evidence_quality", 0),
        "ranking_input": False,
        "core_tournament_scores_modified": False,
        "tournament_rankings_modified": False,
        "hardware_access": False,
        "network_calls": False,
        "live_capture": False,
    }
    adapter_status = evidence_pack.get("adapter_status")
    if isinstance(adapter_status, dict):
        metadata["document_adapter_status"] = {
            "adapter_contract_version": adapter_status.get("adapter_contract_version"),
            "adapter_kind": adapter_status.get("adapter_kind"),
            "status": adapter_status.get("status"),
            "capability_labels": list(adapter_status.get("capability_labels", ())),
            "metadata_only": bool(adapter_status.get("metadata_only")),
            "fixture_only": bool(adapter_status.get("fixture_only")),
            "offline": bool(adapter_status.get("offline")),
            "fail_closed_output_validation": bool(
                adapter_status.get("fail_closed_output_validation")
            ),
        }
        gate = real_mode_readiness_gate_summary(adapter_status.get("real_mode_readiness_gate"))
        if gate:
            metadata["document_adapter_status"]["real_mode_readiness_gate"] = gate
            metadata["document_adapter_status"]["real_mode_readiness_status"] = gate["status"]
            metadata["document_adapter_status"]["real_mode_execution_permitted"] = False
            metadata["document_adapter_status"]["p11a_contract_status"] = (
                phase11_contract_status_summary(
                    domain="document-ingestion",
                    readiness_gate=gate,
                )
            )
            metadata["document_adapter_status"]["p11b_review_record_status"] = (
                phase11_review_record_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11c_preflight_status"] = (
                phase11_preflight_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11d_lifecycle_audit_status"] = (
                phase11_dossier_lifecycle_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11e_audit_index_status"] = (
                phase11_audit_index_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11f_audit_handoff_status"] = (
                phase11_audit_handoff_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11g_handoff_acceptance_status"] = (
                phase11_handoff_acceptance_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11k_review_trail_export_status"] = (
                phase11_review_trail_export_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11l_runtime_gap_ledger_status"] = (
                phase11_runtime_authorization_gap_ledger_status_summary(
                    domain="document-ingestion",
                )
            )
            metadata["document_adapter_status"]["p11m_planning_governance_closeout_status"] = (
                phase11_planning_governance_closeout_status_summary()
            )
    adapter_validation = evidence_pack.get("adapter_output_validation")
    if isinstance(adapter_validation, dict):
        metadata["document_adapter_output_validation"] = {
            "classification": adapter_validation.get("classification"),
            "compatible": bool(adapter_validation.get("compatible")),
            "privacy_violation_count": adapter_validation.get("privacy_violation_count"),
            "status": adapter_validation.get("status"),
            "readiness_status": adapter_validation.get("readiness_status"),
            "sanitized": bool(adapter_validation.get("sanitized")),
        }
    return metadata


def _render_report(workflow, provider_metadata, evidence, safety_response, hypotheses):
    provider_lines = "\n".join(
        f"- `{ref}`: `{metadata.get('id')}` ({metadata.get('class')})"
        for ref, metadata in sorted(provider_metadata.items())
    )
    hypothesis_lines = "\n".join(
        f"{index}. `{item['id']}`: {item['statement']}"
        for index, item in enumerate(hypotheses, start=1)
    )
    return f"""# Somatic Mock Run Report

This is a mock/offline research-only output from the local Somatic runner. It is not medical advice and is not a clinical, lab, sensor, biomodel, Fabric, or provider integration result.

## Workflow

- ID: `{workflow.get("id")}`
- Mode: `{workflow.get("mode")}`
- Status: mock/offline

## Providers

{provider_lines or "- No provider metadata loaded."}

## Evidence

- Evidence ID: `{evidence.get("id")}`
- Source type: `{evidence.get("source_type")}`
- Review state: `{evidence.get("review_state")}`

## Mock Hypotheses

{hypothesis_lines}

## Safety

- Safety response: `{safety_response.get("id")}`
- Decision: `{safety_response.get("decision")}`
- Human review required: `{safety_response.get("human_review", {}).get("required")}`

## Boundaries

- Mock: true
- Offline: true
- Not medical advice: true
- No external API calls were made.
- No provider secrets were used.
- No package downloads were performed.
"""


def _render_robin_report(workflow, provider_metadata, safety_response, robin_loop):
    provider_lines = "\n".join(
        f"- `{ref}`: `{metadata.get('id')}` ({metadata.get('class')})"
        for ref, metadata in sorted(provider_metadata.items())
    )
    context = robin_loop["crow_literature_context"]
    plan = robin_loop["falcon_measurement_plan"]["measurement_plan"]
    raw_evidence = robin_loop["raw_evidence"]
    toolbelt = robin_loop["finch_toolbelt_summary"]
    table_profile = robin_loop["table_profile"]
    dose_response = robin_loop["dose_response_summary"]
    provenance = robin_loop["analysis_provenance"]
    verdict = robin_loop["structured_verdict"]["structured_verdict"]
    stats = verdict["metadata"]["stats"]
    modalities = ", ".join(
        f"{modality}: {count}" for modality, count in stats["modality_counts"].items()
    )
    safety_notes = "\n".join(
        f"- {note}" for note in workflow.get("safety_profile", {}).get("notes", [])
    )
    next_steps = "\n".join(
        f"- {action}" for action in robin_loop["next_iteration"]["recommended_actions"]
    )
    limitations = "\n".join(f"- {item}" for item in verdict["limitations"])
    table_lines = "\n".join(
        (
            f"- `{table['source_file']}`: {table['row_count']} rows, "
            f"{len(table['numeric_columns'])} numeric columns, "
            f"role `{table['role']}`"
        )
        for table in table_profile["tables"]
    )
    provenance_lines = "\n".join(
        f"- `{item['name']}`: `{item['sha256']}`" for item in provenance["source_files"]
    )
    return f"""# Somatic Robin Sandbox Loop Report

This is a mock/offline/research-only output from the local Somatic runner. It is not medical advice, not a real scientific conclusion, and not a clinical, lab, sensor, biomodel, Fabric, PaperQA2, FutureHouse Robin, scientific-agent-skills, LangGraph, AutoScientists, or provider integration result.

## Workflow

- ID: `{workflow.get("id")}`
- Mode: `{workflow.get("mode")}`
- Status: mock/offline
- Loop shape: `crow-falcon-sandbox-finch-verdict-next`

## Providers

{provider_lines or "- No provider metadata loaded."}

## Crow Context Summary

- Records: {len(context["records"])}
- Boundary: `{context["boundary"]}`
- Summary: {context["summary"]}

## Falcon Measurement Plan Summary

- Plan ID: `{plan["id"]}`
- Objective: {plan["objective"]}
- Source modalities: {", ".join(source["modality"] for source in plan["sources"])}
- Safety profile: `{plan["safety_profile"]}`

## Finch Verdict Summary

- Verdict ID: `{verdict["id"]}`
- Confidence: `{verdict["confidence"]}`
- Raw evidence refs: {", ".join(verdict["raw_evidence_refs"])}
- Mock stats: {stats["raw_record_count"]} records; {modalities}; mean mock signal {stats["mean_mock_signal"]}
- Interpretation: {verdict["metadata"]["interpretation"]}

## Finch Toolbelt Summary

- Status: `{toolbelt["toolbelt_status"]}`
- Scope: standard-library local analysis only
- Tables analyzed: {toolbelt["table_count"]}
- Numeric tables: {toolbelt["numeric_table_count"]}
- Dose-response available: `{toolbelt["dose_response_available"]}`
- Evidence quality score: {toolbelt["evidence_quality_score"]}

## Table Profile Summary

{table_lines or "- No local CSV tables were available for profiling."}

## Dose-Response Summary

- Trend direction: `{dose_response["trend_direction"]}`
- Effect direction: `{dose_response["effect_direction"]}`
- Baseline-vs-highest-dose delta: `{dose_response["baseline_vs_highest_delta"]}`
- Interpretation: {dose_response["interpretation"]}

## Analysis Provenance

- Dependencies: {", ".join(provenance["dependencies"])}
- Network calls: `{provenance["network_calls"]}`
- External API calls: `{provenance["external_api_calls"]}`
{provenance_lines or "- No local source files were hashed."}

## Evidence Limitations

{limitations}
- Sandbox raw evidence records: {len(raw_evidence["records"])}
- The artifacts demonstrate local pipeline shape only.
- Finch toolbelt outputs are deterministic research artifacts, not medical advice, clinical evidence, or real scientific conclusions.

## Safety Summary

- Safety response: `{safety_response.get("id")}`
- Decision: `{safety_response.get("decision")}`
- Human review required: `{safety_response.get("human_review", {}).get("required")}`
- External actions allowed: `{workflow.get("safety_profile", {}).get("external_actions_allowed")}`
- Real lab action requires approval: `{workflow.get("safety_profile", {}).get("real_lab_action_requires_approval")}`
{safety_notes}

## Next-Step Recommendations

{next_steps}

## Boundaries

- Mock: true
- Offline: true
- Research-only: true
- Not medical advice: true
- Not a real scientific conclusion: true
- No external API calls were made.
- No provider secrets were used.
- No package downloads were performed.
- No real sensor, wetlab, biomodel, Fabric, PaperQA2, FutureHouse Robin, scientific-agent-skills, LangGraph, or AutoScientists runtime was used.
"""


def _render_tournament_report(workflow, provider_metadata, evidence, safety_response, tournament):
    provider_lines = "\n".join(
        f"- `{ref}`: `{metadata.get('id')}` ({metadata.get('class')})"
        for ref, metadata in sorted(provider_metadata.items())
    )
    ranked = tournament["ranked_hypotheses"]
    aggregate_lines = "\n".join(
        (
            f"{item['rank']}. `{item['id']}` "
            f"(aggregate {item['aggregate_score']}, Elo {item['elo_rating']}): "
            f"{item['statement']}"
        )
        for item in ranked[:3]
    )
    elo_rows = "\n".join(
        "| {rank} | `{candidate_id}` | {rating} | {wins}-{losses} | {aggregate_score} |".format(
            rank=item["rank"],
            candidate_id=item["candidate_id"],
            rating=item["rating"],
            wins=item["wins"],
            losses=item["losses"],
            aggregate_score=item["aggregate_score"],
        )
        for item in tournament["elo_ratings"]["ratings"]
    )
    debate_lines = "\n".join(
        (
            f"- `{matchup['matchup_id']}`: `{matchup['candidate_ids'][0]}` vs "
            f"`{matchup['candidate_ids'][1]}` -> `{matchup['winner_id']}`"
        )
        for matchup in tournament["pairwise_debates"]["matchups"][:5]
    )
    team_summary = tournament["team_orchestrator"]["team_orchestrator_summary"]
    evidence_budget = tournament["team_orchestrator"]["evidence_budget"]
    team_lines = "\n".join(
        (
            f"- `{team['team_id']}` ({team['role']}): {team['decision']} "
            f"for {', '.join(team['focus_hypothesis_ids'])}; "
            f"stage `{team['lifecycle_stage']}`, confidence "
            f"{team['confidence_estimate']['score']} ({team['confidence_estimate']['label']}), "
            f"next `{team['next_team_action']}`"
        )
        for team in tournament["team_orchestrator"]["team_roster"]["teams"]
    )
    critique_gate = team_summary["critique_gate"]
    stall_summary = team_summary["stall_summary"]
    reorganization_trigger = team_summary["reorganization_trigger"]
    future_provider_hook = team_summary["future_provider_hook"]
    csi_scoring_readiness = team_summary.get("csi_evidence_scoring_readiness", {})
    csi_evidence_pack = team_summary.get("csi_evidence_pack", {})
    csi_sensor_evidence_ref = team_summary.get(
        "sensor_evidence_artifact_refs",
        {},
    ).get("csi_evidence_pack", {})
    environment_evidence_pack = team_summary.get("environment_evidence_pack", {})
    environment_readiness = team_summary.get("environment_readiness_metadata", {})
    environment_sensor_evidence_ref = team_summary.get(
        "sensor_evidence_artifact_refs",
        {},
    ).get("environment_evidence_pack", {})
    document_evidence_pack = team_summary.get("document_evidence_pack", {})
    document_readiness = team_summary.get("document_readiness_metadata", {})
    document_adapter_status = document_readiness.get("document_adapter_status", {})
    document_adapter_validation = document_readiness.get("document_adapter_output_validation", {})
    document_real_mode_gate = document_adapter_status.get("real_mode_readiness_gate", {})
    document_adapter_labels = ", ".join(
        str(label) for label in document_adapter_status.get("capability_labels", ())
    )
    document_sensor_evidence_ref = team_summary.get(
        "sensor_evidence_artifact_refs",
        {},
    ).get("document_evidence_pack", {})
    environment_lines = ""
    if environment_evidence_pack:
        environment_lines = f"""
#### Environment Fixture Evidence

- Environment evidence pack ref: `{environment_evidence_pack.get("artifact_ref")}`
- Environment evidence pack fingerprint: `{environment_evidence_pack.get("pack_fingerprint")}`
- Environment row count: {environment_readiness.get("row_count")}
- Environment evidence status: `{environment_readiness.get("status")}`
- Environment generic evidence ref: `{environment_sensor_evidence_ref.get("artifact_ref")}`
- Environment generic evidence SHA-256: `{environment_sensor_evidence_ref.get("sha256")}`
"""
    document_lines = ""
    if document_evidence_pack:
        document_lines = f"""
#### Document Fixture Evidence

- Document evidence pack ref: `{document_evidence_pack.get("artifact_ref")}`
- Document evidence pack fingerprint: `{document_evidence_pack.get("pack_fingerprint")}`
- Document count: {document_readiness.get("document_count")}
- Parsed documents: {document_readiness.get("parsed_document_count")}
- Partial documents: {document_readiness.get("partial_document_count")}
- Rejected documents: {document_readiness.get("rejected_document_count")}
- Document evidence status: `{document_readiness.get("status")}`
- Document evidence readiness: `{document_readiness.get("readiness_status")}`
- Document adapter status: `{document_adapter_status.get("status")}`
- Document adapter boundary: `{document_adapter_labels}`
- Document adapter validation: `{document_adapter_validation.get("classification")}`
- Document real-mode readiness gate: `{document_real_mode_gate.get("status")}`
- Document real-mode missing gates: {document_real_mode_gate.get("missing_gate_count")}
- Document real-mode execution permitted: `{document_real_mode_gate.get("execution_permitted")}`
- Document generic evidence ref: `{document_sensor_evidence_ref.get("artifact_ref")}`
- Document generic evidence SHA-256: `{document_sensor_evidence_ref.get("sha256")}`
"""
    csi_group_lines = "\n".join(
        (
            f"- `{group.get('group_id')}`: status `{group.get('status')}`, "
            f"score {group.get('score')} / 100"
        )
        for group in csi_scoring_readiness.get("group_summaries", [])
        if isinstance(group, dict)
    )
    csi_batch_lines = ""
    if "csi_batch_evaluation_contract_version" in csi_scoring_readiness:
        csi_batch_lines = f"""
- Batch contract version: `{csi_scoring_readiness.get("csi_batch_evaluation_contract_version")}`
- Group count: {csi_scoring_readiness.get("group_count")}
- Evaluated groups: {csi_scoring_readiness.get("evaluated_group_count")}
- Rejected groups: {csi_scoring_readiness.get("rejected_group_count")}
- Aggregate evidence quality: {csi_scoring_readiness.get("aggregate_evidence_quality")} / 100
- Aggregate replay integrity: {csi_scoring_readiness.get("aggregate_replay_integrity")} / 100
- Scorer: `{csi_scoring_readiness.get("scorer_id")}`
- Scoring contract version: `{csi_scoring_readiness.get("scoring_contract_version")}`
- CSI evidence pack ref: `{csi_evidence_pack.get("artifact_ref")}`
- CSI evidence pack fingerprint: `{csi_evidence_pack.get("pack_fingerprint")}`
- Generic sensor evidence ref: `{csi_sensor_evidence_ref.get("artifact_ref")}`
- Generic sensor evidence SHA-256: `{csi_sensor_evidence_ref.get("sha256")}`

#### CSI Batch Replay Evaluation

{csi_group_lines or "- No CSI fixture groups evaluated."}
{environment_lines}
"""
    budget_lines = "\n".join(
        (
            f"- `{item['team_id']}`: {item['point_budget']} "
            f"{evidence_budget['currency']} ({item['spend_status']}; "
            f"{item['evidence_spend_decision']['decision']})"
        )
        for item in evidence_budget["allocations"]
    )
    score_rows = "\n".join(
        "| {rank} | `{id}` | {evidence_alignment} | {novelty} | {feasibility} | "
        "{falsifiability} | {safety_risk} | {data_requirements} | "
        "{aggregate_score} | {elo_rating} |".format(
            rank=item["rank"],
            id=item["id"],
            evidence_alignment=item["scores"]["evidence_alignment"],
            novelty=item["scores"]["novelty"],
            feasibility=item["scores"]["feasibility"],
            falsifiability=item["scores"]["falsifiability"],
            safety_risk=item["scores"]["safety_risk"],
            data_requirements=item["scores"]["data_requirements"],
            aggregate_score=item["aggregate_score"],
            elo_rating=item["elo_rating"],
        )
        for item in ranked
    )
    safety_notes = "\n".join(
        f"- {note}" for note in workflow.get("safety_profile", {}).get("notes", [])
    )
    return f"""# Somatic Hypothesis Tournament Report

This is a mock/offline research-only output from the local Somatic runner. It is not medical advice and is not a real scientific conclusion. It is not a clinical, lab, sensor, biomodel, Fabric, LangGraph, or provider integration result.

## Workflow

- ID: `{workflow.get("id")}`
- Mode: `{workflow.get("mode")}`
- Status: mock/offline
- Candidate count: {len(tournament["candidate_hypotheses"])}
- Pairwise debates: {tournament["pairwise_debates"]["matchup_count"]}
- Team orchestrator: `{team_summary["orchestrator_status"]}`
- Refined candidates: {len(tournament["refined_hypotheses"])}

## Providers

{provider_lines or "- No provider metadata loaded."}

## Evidence

- Evidence ID: `{evidence.get("id")}`
- Source type: `{evidence.get("source_type")}`
- Review state: `{evidence.get("review_state")}`

## Aggregate Score Ranking

{aggregate_lines}

## Elo Ranking

All original candidate hypotheses start at the same base rating. Ratings update after each deterministic pairwise comparison.

| Elo rank | Candidate | Rating | Record | Aggregate score |
| --- | --- | ---: | ---: | ---: |
{elo_rows}

## Pairwise Debate Summary

Each matchup contains deterministic mock pro/con notes for both hypotheses. The summary below shows the first five of {tournament["pairwise_debates"]["matchup_count"]} pairwise debates.

{debate_lines}

## Team Orchestration Summary

The TeamOrchestrator is a deterministic scaffold of local data structures, not live agents. Critique is recorded before mock evidence budget planning.

### Team Formation Summary

{team_lines}

### Critique Gate Summary

- Gate: `{critique_gate["gate_id"]}`
- Result: `{critique_gate["result"]}`
- Passed before budget: `{critique_gate["passed"]}`

### Reorganization And Stall Summary

- Reorganization triggered: `{reorganization_trigger["triggered"]}`
- Reason: `{reorganization_trigger["reason"]}`
- Stalled teams: {len(stall_summary["stalled_team_ids"])}

### AutoScientists Reference Boundary

- Provider hook: `{future_provider_hook["provider_id"]}`
- Reference-only: `{future_provider_hook["reference_only"]}`
- Runtime enabled: `{future_provider_hook["runtime_enabled"]}`
- License status: `{future_provider_hook["license_status"]}`
- Inspected commit: `{future_provider_hook["source_commit"]}`

### CSI Evidence Scoring Readiness

- Status: `{csi_scoring_readiness.get("status")}`
- Metadata only: `{csi_scoring_readiness.get("metadata_only")}`
- Core tournament scores modified: `{csi_scoring_readiness.get("core_tournament_scores_modified")}`
- Ranking input: `{csi_scoring_readiness.get("ranking_input")}`
{csi_batch_lines}
{document_lines}

## Evidence Budget Summary

- Total mock evidence budget: {evidence_budget["total_points"]} {evidence_budget["currency"]}
- Critique completed before budget: `{evidence_budget["critique_completed_before_budget"]}`
- External evidence spend allowed: `{evidence_budget["external_evidence_spend_allowed"]}`

{budget_lines}

## Score Table

Safety risk is a risk score where lower is safer; it is inverted when calculating aggregate score and does not boost pairwise or Elo outcomes.

| Rank | Hypothesis | Evidence | Novelty | Feasibility | Falsifiability | Safety risk | Data req. | Aggregate | Elo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{score_rows}

## Safety Summary

- Safety response: `{safety_response.get("id")}`
- Decision: `{safety_response.get("decision")}`
- Human review required: `{safety_response.get("human_review", {}).get("required")}`
- External actions allowed: `{workflow.get("safety_profile", {}).get("external_actions_allowed")}`
- Real lab action requires approval: `{workflow.get("safety_profile", {}).get("real_lab_action_requires_approval")}`
{safety_notes}

## Limitations

- Deterministic mock data only.
- One local fixture evidence record only.
- Scores are ordering hints, not scientific measurements.
- No external literature, lab, biomodel, live sensor, Fabric, LangGraph, or provider runtime was used.
- Pairwise debates and Elo ratings are deterministic mock review artifacts.
- Team orchestration is scaffold-only and uses plain local mock data structures.
- This is not medical advice and not a real scientific conclusion.

## Next-Step Recommendations

- Review the ranked shortlist with a qualified human reviewer.
- Add more local evidence fixtures, including counterevidence, before expanding conclusions.
- Convert one hypothesis into a local falsification plan only after safety review.
- Keep future provider, lab, live sensor, Fabric, and biomodel integrations disabled until explicit safety and secrets boundaries exist.

## Boundaries

- Mock: true
- Offline: true
- Research-only: true
- Not medical advice: true
- Not a real scientific conclusion: true
- No external API calls were made.
- No provider secrets were used.
- No package downloads were performed.
"""
