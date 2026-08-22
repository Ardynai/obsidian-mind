import argparse
import json
import sys
from pathlib import Path

from somatic.fabric.canonical import (
    canonical_bytes,
    canonical_dumps,
    loads_fabric_json,
    signing_payload,
)
from somatic.fabric.catalog import (
    validate_catalog_shape,
    verify_catalog_signature_threshold,
)
from somatic.fabric.crypto import CRYPTO_AVAILABLE
from somatic.fabric.digests import manifest_digest, sha256_hex
from somatic.fabric.keyring import (
    validate_keyring_shape,
    verify_keyring_replacement,
    verify_keyring_root_threshold,
    verify_pack_publisher_threshold,
)
from somatic.fabric.manifest import validate_pack_manifest
from somatic.mock_runtime import run_mock_workflow
from somatic.workflow_loader import parse_simple_yaml


def main(argv=None):
    parser = argparse.ArgumentParser(prog="somatic", description="Somatic local scaffold CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a workflow fixture with mock providers")
    run_parser.add_argument("workflow", help="Path to a workflow YAML fixture")
    run_parser.add_argument("--runs-dir", default="runs", help="Output directory for run artifacts")
    run_parser.add_argument(
        "--run-id", default=None, help="Optional run id for deterministic tests"
    )

    launch_parser = subparsers.add_parser(
        "launch", help="Load a launch config without running advanced lanes"
    )
    launch_parser.add_argument("--config", required=True, help="Path to a local YAML launch config")

    subparsers.add_parser("doctor", help="Report local scaffold status")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Consent-gated informational analysis of a user's own data packet",
    )
    analyze_parser.add_argument(
        "--data",
        required=True,
        help="Path to a JSON data packet of the user's own metrics",
    )
    analyze_parser.add_argument(
        "--question",
        default="What patterns stand out in my data?",
        help="Question to ask about the data packet",
    )
    analyze_parser.add_argument(
        "--references",
        default=None,
        help="Optional JSON file of caller-provided reference ranges by metric",
    )
    analyze_parser.add_argument(
        "--baselines",
        default=None,
        help="Optional JSON file of the user's own baseline series by metric",
    )
    analyze_parser.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    analyze_parser.add_argument(
        "--model-url",
        default=None,
        help="Optional OpenAI-compatible model base URL for an AI read",
    )
    analyze_parser.add_argument(
        "--model",
        default=None,
        help="Optional model name for an AI read",
    )
    analyze_parser.add_argument(
        "--model-key",
        default=None,
        help="Deprecated: keys are read from SOMATIC_ADVISORY_MODEL_KEY, not argv",
    )

    share_parser = subparsers.add_parser(
        "share",
        help="Consent-gated clinician-facing Markdown summary of an analyze report",
    )
    share_parser.add_argument(
        "--data",
        required=True,
        help="Path to a JSON data packet of the user's own metrics",
    )
    share_parser.add_argument(
        "--question",
        default="What patterns stand out in my data?",
        help="Question to ask about the data packet",
    )
    share_parser.add_argument(
        "--references",
        default=None,
        help="Optional JSON file of caller-provided reference ranges by metric",
    )
    share_parser.add_argument(
        "--baselines",
        default=None,
        help="Optional JSON file of the user's own baseline series by metric",
    )
    share_parser.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    share_parser.add_argument(
        "--model-url",
        default=None,
        help="Optional OpenAI-compatible model base URL for an AI read",
    )
    share_parser.add_argument(
        "--model",
        default=None,
        help="Optional model name for an AI read",
    )
    share_parser.add_argument(
        "--model-key",
        default=None,
        help="Deprecated: keys are read from SOMATIC_ADVISORY_MODEL_KEY, not argv",
    )
    share_parser.add_argument(
        "--patient-label",
        default="",
        help="Optional patient label included in the shared Markdown",
    )
    share_parser.add_argument(
        "--clinician-note",
        default="",
        help="Optional requesting note included in the shared Markdown",
    )
    share_parser.add_argument(
        "--out",
        default=None,
        help="Optional path to write the Markdown summary (utf-8)",
    )
    share_parser.add_argument(
        "--fhir-out",
        default=None,
        help="Optional path to write a FHIR-shaped JSON sidecar (utf-8)",
    )

    replay_parser = subparsers.add_parser(
        "replay", help="Inspect a local run manifest or commit placeholder"
    )
    replay_parser.add_argument("commit_or_run_id", help="Run id or commit ref to inspect")
    replay_parser.add_argument(
        "--runs-dir", default="runs", help="Directory containing local run artifacts"
    )

    csi_parser = subparsers.add_parser(
        "csi-parse",
        help="Parse a local WiFi CSI fixture and print sanitized metadata",
    )
    csi_parser.add_argument("fixture", help="CSI fixture filename or fixture:// ref")
    csi_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing fixtures/sensors/csi",
    )
    csi_parser.add_argument(
        "--max-file-size-bytes",
        type=int,
        default=None,
        help="Optional maximum fixture size override",
    )

    sensor_evidence_parser = subparsers.add_parser(
        "sensor-evidence",
        help="Inspect sanitized fixture-only sensor evidence provider metadata",
    )
    sensor_evidence_subparsers = sensor_evidence_parser.add_subparsers(
        dest="sensor_evidence_command",
        required=True,
    )
    sensor_evidence_providers = sensor_evidence_subparsers.add_parser(
        "providers",
        help="List registered fixture-only sensor evidence providers",
    )
    sensor_evidence_providers.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    sensor_evidence_validate = sensor_evidence_subparsers.add_parser(
        "validate",
        help="Validate sensor evidence provider config in a workflow fixture",
    )
    sensor_evidence_validate.add_argument(
        "--workflow",
        required=True,
        help="Path to a local workflow YAML fixture",
    )
    sensor_evidence_validate.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    sensor_evidence_inspect = sensor_evidence_subparsers.add_parser(
        "inspect",
        help="Inspect a persisted sanitized evidence pack artifact",
    )
    sensor_evidence_inspect.add_argument(
        "--artifact",
        required=True,
        help="Path to a local evidence pack JSON artifact",
    )
    sensor_evidence_inspect.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )

    fabric_parser = subparsers.add_parser("fabric", help="Local Content Fabric utilities")
    fabric_subparsers = fabric_parser.add_subparsers(dest="fabric_command", required=True)
    fabric_check = fabric_subparsers.add_parser("check", help="Validate a local Fabric JSON file")
    fabric_check.add_argument("path", help="Path to a pack, keyring, or catalog JSON fixture")
    fabric_check.add_argument(
        "--keyring", default=None, help="Optional keyring for pack signature verification"
    )
    fabric_payload = fabric_subparsers.add_parser(
        "payload", help="Print a local Fabric object's signing payload digest"
    )
    fabric_payload.add_argument("path", help="Path to a local Fabric JSON file")
    fabric_canonicalize = fabric_subparsers.add_parser(
        "canonicalize", help="Print canonical JSON for a local Fabric JSON file"
    )
    fabric_canonicalize.add_argument("path", help="Path to a local Fabric JSON file")
    fabric_digest = fabric_subparsers.add_parser(
        "digest", help="Print canonical and manifest digests for a local Fabric JSON file"
    )
    fabric_digest.add_argument("path", help="Path to a local Fabric JSON file")
    fabric_check_catalog = fabric_subparsers.add_parser(
        "check-catalog", help="Validate and verify a local Fabric catalog JSON file"
    )
    fabric_check_catalog.add_argument("path", help="Path to a local Fabric catalog JSON file")
    fabric_check_catalog.add_argument(
        "--keyring",
        required=True,
        help="Keyring for catalog signature verification",
    )
    fabric_shared = fabric_subparsers.add_parser(
        "check-shared-fixtures", help="Self-certify a local shared Fabric fixture directory"
    )
    fabric_shared.add_argument("path", help="Path to fixtures/fabric/interop/shared")
    fabric_rotation = fabric_subparsers.add_parser(
        "check-keyring-rotation", help="Verify a proposed keyring replacement"
    )
    fabric_rotation.add_argument("old", help="Path to the current trusted keyring JSON")
    fabric_rotation.add_argument("new", help="Path to the proposed replacement keyring JSON")
    fabric_register = fabric_subparsers.add_parser(
        "register",
        help="Register Somatic with the Multiverse fabric registry",
    )
    fabric_register.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    fabric_send = fabric_subparsers.add_parser(
        "send",
        help="Send a file through the out-of-process fabric federation sidecar",
    )
    fabric_send.add_argument("--to-did", required=True, help="Allowlisted sibling recipient DID")
    fabric_send.add_argument("--path", required=True, help="Local file path to send")
    fabric_send.add_argument(
        "--secure",
        action="store_true",
        help="Mark payload as encrypted ciphertext; Somatic does not decrypt it",
    )
    fabric_send.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    fabric_receive_once = fabric_subparsers.add_parser(
        "receive-once",
        help="Poll one inbound fabric federation batch and re-verify contentIds",
    )
    fabric_receive_once.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )

    consent_parser = subparsers.add_parser(
        "consent",
        help="Grant, revoke, inspect, or erase the local consent ledger",
    )
    consent_subparsers = consent_parser.add_subparsers(dest="consent_command", required=True)
    consent_subparsers.add_parser("status", help="Show every scope (all default OFF)")
    consent_grant = consent_subparsers.add_parser(
        "grant",
        help="Persist a grant for one or more scopes",
    )
    consent_grant.add_argument(
        "scopes",
        help="Comma-separated consent scope ids (for example analysis-insight,ai-advisory)",
    )
    consent_revoke = consent_subparsers.add_parser(
        "revoke",
        help="Persist a revocation for one or more scopes",
    )
    consent_revoke.add_argument(
        "scopes",
        help="Comma-separated consent scope ids",
    )
    consent_subparsers.add_parser(
        "erase",
        help="Right-to-erasure: purge grants/events and delete the on-disk ledger",
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Consent-gated CSV or Apple Health import into a timestamped packet",
    )
    ingest_subparsers = ingest_parser.add_subparsers(dest="ingest_command", required=True)
    ingest_csv_parser = ingest_subparsers.add_parser(
        "csv",
        help="Import a local CSV with metric,value,observed_at columns",
    )
    ingest_csv_parser.add_argument("--file", required=True, help="Path to a UTF-8 CSV file")
    ingest_csv_parser.add_argument(
        "--out",
        default=None,
        help="Optional JSON packet output path",
    )
    ingest_csv_parser.add_argument(
        "--save",
        action="store_true",
        help="Append readings to the local ingest store",
    )
    ingest_csv_parser.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    ingest_health_parser = ingest_subparsers.add_parser(
        "apple-health",
        help="Import a local Apple Health export.xml or zip",
    )
    ingest_health_parser.add_argument(
        "--file",
        required=True,
        help="Path to export.xml or an Apple Health export zip",
    )
    ingest_health_parser.add_argument(
        "--out",
        default=None,
        help="Optional JSON packet output path",
    )
    ingest_health_parser.add_argument(
        "--save",
        action="store_true",
        help="Append readings to the local ingest store",
    )
    ingest_health_parser.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    ingest_subparsers.add_parser(
        "status",
        help="Show the local ingest store path and reading count",
    )
    ingest_subparsers.add_parser(
        "erase",
        help="Right-to-erasure: delete the local ingest store",
    )

    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Consent-gated n-of-1 own-baseline experiment tracking",
    )
    experiment_subparsers = experiment_parser.add_subparsers(
        dest="experiment_command",
        required=True,
    )
    experiment_evaluate = experiment_subparsers.add_parser(
        "evaluate",
        help="Compare post-tag readings to the user's own pre-tag baseline",
    )
    experiment_evaluate.add_argument(
        "--data",
        required=True,
        help="Path to a timestamped JSON packet (ingest output or metrics map)",
    )
    experiment_evaluate.add_argument("--metric", required=True, help="Metric id to evaluate")
    experiment_evaluate.add_argument(
        "--started",
        required=True,
        help="Intervention start timestamp (ISO-8601)",
    )
    experiment_evaluate.add_argument("--name", default="untagged-interval")
    experiment_evaluate.add_argument("--ended", default="")
    experiment_evaluate.add_argument("--note", default="")
    experiment_evaluate.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    experiment_tag = experiment_subparsers.add_parser(
        "tag",
        help="Persist an intervention tag in the local experiment store",
    )
    experiment_tag.add_argument("--name", required=True)
    experiment_tag.add_argument("--metric", required=True)
    experiment_tag.add_argument("--started", required=True, help="ISO-8601 start timestamp")
    experiment_tag.add_argument("--ended", default="")
    experiment_tag.add_argument("--note", default="")
    experiment_tag.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )
    experiment_subparsers.add_parser(
        "status",
        help="Show local experiment tag count",
    )
    experiment_subparsers.add_parser(
        "erase",
        help="Right-to-erasure: delete local experiment tags",
    )

    research_parser = subparsers.add_parser(
        "research",
        help="Consent-gated offline research with citation-binding",
    )
    research_subparsers = research_parser.add_subparsers(
        dest="research_command",
        required=True,
    )
    research_ask = research_subparsers.add_parser(
        "ask",
        help="Retrieve offline passages and emit only citation-bound extracts",
    )
    research_ask.add_argument("--question", required=True, help="Research question")
    research_ask.add_argument(
        "--corpus",
        default=None,
        help="Optional offline corpus JSON path (defaults to bundled fixture)",
    )
    research_ask.add_argument("--k", type=int, default=5, help="Max passages to retrieve")
    research_ask.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )

    remedy_parser = subparsers.add_parser(
        "remedy",
        help="Consent-gated evidence-graded informational remedy library",
    )
    remedy_subparsers = remedy_parser.add_subparsers(dest="remedy_command", required=True)
    remedy_lookup = remedy_subparsers.add_parser(
        "lookup",
        help="Look up a topic in the offline remedy library",
    )
    remedy_lookup.add_argument("--query", required=True, help="Remedy topic or question")
    remedy_lookup.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )

    parasite_parser = subparsers.add_parser(
        "parasite",
        help="Consent-gated informational parasite Q&A (not identification)",
    )
    parasite_subparsers = parasite_parser.add_subparsers(
        dest="parasite_command",
        required=True,
    )
    parasite_ask = parasite_subparsers.add_parser(
        "ask",
        help="Ask an informational, source-grounded parasite question",
    )
    parasite_ask.add_argument("--question", required=True)
    parasite_ask.add_argument(
        "--grant",
        default="",
        help="Comma-separated consent scope ids to grant for this run only",
    )

    bus_parser = subparsers.add_parser(
        "bus",
        help="Run the sandbox Evidence Bus (all modalities, hardware closed)",
    )
    bus_sub = bus_parser.add_subparsers(dest="bus_command", required=True)
    bus_run = bus_sub.add_parser("run", help="Acquire sandbox evidence for a hypothesis")
    bus_run.add_argument("--hypothesis", required=True)
    bus_run.add_argument("--id", default="hyp-bus")
    bus_run.add_argument("--domain", default="sensing", choices=("discovery", "n-of-1", "sensing"))
    bus_run.add_argument("--modalities", default="", help="Comma-separated modalities; default all")
    bus_run.add_argument("--grant", default="")
    bus_run.add_argument("--seed", type=int, default=0)

    roster_parser = subparsers.add_parser(
        "sensor-roster",
        help="List or sandbox-scan the full sensor roster (hardware closed)",
    )
    roster_sub = roster_parser.add_subparsers(dest="roster_command", required=True)
    roster_sub.add_parser("list", help="Show roster modalities and extra-lane availability")
    roster_scan = roster_sub.add_parser("scan", help="Sandbox live-scan one modality")
    roster_scan.add_argument("--modality", required=True)
    roster_scan.add_argument("--ticks", type=int, default=1)
    roster_scan.add_argument(
        "--live",
        action="store_true",
        help="CSI loopback or on-device camera pose; needs live grant; refused otherwise",
    )
    roster_scan.add_argument("--grant", default="")
    roster_scan.add_argument("--seed", type=int, default=0)
    roster_fuse = roster_sub.add_parser("fuse", help="Sandbox RF↔vision 3D-pose fusion")
    roster_fuse.add_argument("--grant", default="")
    roster_fuse.add_argument("--seed", type=int, default=0)
    roster_listen = roster_sub.add_parser(
        "listen",
        help="Start loopback UDP CSI ingest (requires live-sensor grant + subject consent)",
    )
    roster_listen.add_argument("--grant", default="")
    roster_live_grant = roster_sub.add_parser(
        "live-grant",
        help="Grant a live-sensor lane (off by default; requires --subject-consent)",
    )
    roster_live_grant.add_argument("--subject-consent", action="store_true")
    roster_live_grant.add_argument(
        "--modality",
        default="csi",
        choices=("csi", "audio", "video", "video3d"),
        help="Live lane to grant: csi (default), audio, video, or video3d",
    )
    roster_live_revoke = roster_sub.add_parser("live-revoke", help="Revoke a live-sensor lane")
    roster_live_revoke.add_argument(
        "--modality",
        default="csi",
        choices=("csi", "audio", "video", "video3d"),
        help="Live lane to revoke: csi (default), audio, video, or video3d",
    )

    science_parser = subparsers.add_parser(
        "science",
        help="Sandbox autonomous-science harness (tournament + bus + belief)",
    )
    science_sub = science_parser.add_subparsers(dest="science_command", required=True)
    science_run = science_sub.add_parser("run", help="One sandbox science cycle")
    science_run.add_argument("--goal", required=True)
    science_run.add_argument("--grant", default="")
    science_run.add_argument("--seed", type=int, default=0)

    avatar_parser = subparsers.add_parser(
        "avatar",
        help="Render-only Scientist/Doctor presence over a gated verdict",
    )
    avatar_sub = avatar_parser.add_subparsers(dest="avatar_command", required=True)
    avatar_speak = avatar_sub.add_parser("speak", help="Rephrase a verdict; never changes it")
    avatar_speak.add_argument("--verdict", required=True)
    avatar_speak.add_argument("--persona", default="doctor", choices=("scientist", "doctor"))
    avatar_speak.add_argument("--grant", default="")

    bench_parser = subparsers.add_parser(
        "bench-run",
        help="Score the sandbox harness on the ripasudil/dAMD fixture task",
    )
    bench_parser.add_argument("--task", default="")
    bench_parser.add_argument("--grant", default="")
    bench_parser.add_argument("--seed", type=int, default=0)

    verify_parser = subparsers.add_parser(
        "evidence-verify",
        help="Re-check a content-addressed evidence JSON from its hash",
    )
    verify_parser.add_argument("--file", required=True)

    ui_parser = subparsers.add_parser(
        "ui",
        help="Open the local-only graphical interface bound to 127.0.0.1",
        description="Serve the local graphical UI on 127.0.0.1. Nothing leaves this machine.",
    )
    ui_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (127.0.0.1 or localhost only)",
    )
    ui_parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="TCP port (0 selects an ephemeral port)",
    )
    ui_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser window",
    )

    args = parser.parse_args(argv)
    if args.command == "run":
        return _run(args)
    if args.command == "launch":
        return _launch(args)
    if args.command == "doctor":
        return _doctor()
    if args.command == "analyze":
        return _analyze(args)
    if args.command == "share":
        return _share(args)
    if args.command == "replay":
        return _replay(args)
    if args.command == "csi-parse":
        return _csi_parse(args)
    if args.command == "sensor-evidence":
        return _sensor_evidence(args)
    if args.command == "fabric":
        return _fabric(args)
    if args.command == "consent":
        return _consent(args)
    if args.command == "ingest":
        return _ingest(args)
    if args.command == "experiment":
        return _experiment(args)
    if args.command == "research":
        return _research(args)
    if args.command == "remedy":
        return _remedy(args)
    if args.command == "parasite":
        return _parasite(args)
    if args.command == "bus":
        return _bus(args)
    if args.command == "sensor-roster":
        return _sensor_roster(args)
    if args.command == "science":
        return _science(args)
    if args.command == "avatar":
        return _avatar(args)
    if args.command == "bench-run":
        return _bench_run(args)
    if args.command == "evidence-verify":
        return _evidence_verify(args)
    if args.command == "ui":
        return _ui(args)

    parser.print_help(sys.stderr)
    return 2


def _run(args):
    repo_root = Path.cwd()
    run_dir = run_mock_workflow(
        Path(args.workflow),
        repo_root=repo_root,
        output_root=repo_root / args.runs_dir,
        run_id=args.run_id,
    )
    print(f"Somatic mock run complete: {run_dir}")
    return 0


def _launch(args):
    config_path = Path(args.config)
    config = parse_simple_yaml(config_path.read_text(encoding="utf-8"))
    mode = config.get("mode", "unspecified")
    workflow = config.get("workflow", "unspecified")
    print(f"Launch plan loaded: {config_path}")
    print(f"- mode: {mode}")
    print(f"- workflow: {workflow}")
    print("- advanced lanes disabled until explicitly configured")
    print("- no provider secrets, network calls, lab actions, sensor access, or model downloads")
    return 0


def _parse_scope_ids(raw: str) -> list[str]:
    return [part.strip() for part in str(raw or "").split(",") if part.strip()]


def _load_json_object_arg(path_value: str, command: str, flag: str) -> dict | None:
    """Load a JSON object from a CLI path, or print a note and return None."""

    try:
        payload = json.loads(Path(path_value).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"{command}: could not read {flag}: {exc}", file=sys.stderr)
        return None
    if not isinstance(payload, dict):
        print(f"{command}: {flag} must contain a JSON object", file=sys.stderr)
        return None
    return payload


def _ledger_for_run(grant_csv: str, command: str):
    """Load the persisted ledger and apply session-only ``--grant`` overlays."""

    from somatic.consent.scopes import get_scope
    from somatic.consent.store import load_ledger

    ledger = load_ledger()
    grant_ids = _parse_scope_ids(grant_csv)
    if grant_ids:
        print(f"granting: {', '.join(grant_ids)}")
    for scope_id in grant_ids:
        scope = get_scope(scope_id)
        if scope is None:
            print(f"{command}: unknown consent scope id: {scope_id}", file=sys.stderr)
            return None
        ledger.grant(scope)
    return ledger


def _model_config_from_args(args, command: str):
    """Build model config from CLI URL/model plus env key. Refuse argv secrets."""

    from somatic.advisory.adapter import AdvisoryModelConfig

    if getattr(args, "model_key", None):
        print(
            f"{command}: --model-key is not accepted; set SOMATIC_ADVISORY_MODEL_KEY",
            file=sys.stderr,
        )
        return None, True
    env_config = AdvisoryModelConfig.from_env()
    model_url = str(args.model_url or env_config.model_url or "").strip()
    model = str(args.model or env_config.model or "").strip()
    model_key = env_config.model_key
    if not (model_url or model or model_key):
        return None, False
    return (
        AdvisoryModelConfig(
            model_url=model_url,
            model=model,
            model_key=model_key,
            timeout_seconds=env_config.timeout_seconds,
            option_id=env_config.option_id,
            chat_path=env_config.chat_path,
        ),
        False,
    )


def _consent(args):
    from somatic.consent.scopes import CONSENT_SCOPES, get_scope
    from somatic.consent.store import (
        default_consent_path,
        erase_stored_ledger,
        load_ledger,
        save_ledger,
    )

    command = str(getattr(args, "consent_command", "") or "")
    if command == "status":
        ledger = load_ledger()
        print("Somatic consent status")
        print(f"- store: {default_consent_path()}")
        for scope in CONSENT_SCOPES:
            state = "ON" if ledger.is_granted(scope) else "OFF"
            print(f"- {scope.id}: {state} (default OFF)")
        return 0
    if command == "erase":
        # Unlink first so a corrupt/non-UTF-8 file cannot crash erasure.
        erase_stored_ledger()
        from somatic.ingest.store import erase_stored_readings

        erase_stored_readings()
        from somatic.experiments.store import erase_stored_tags

        erase_stored_tags()
        from somatic.sensors.live_consent import erase_live_consent
        from somatic.sensors.live_store import erase_csi_features

        erase_live_consent()
        erase_csi_features()
        print(
            "Somatic consent erased (all scopes OFF; on-disk ledger, "
            "readings, experiment tags, live-sensor grants, and CSI features deleted)"
        )
        return 0
    if command in {"grant", "revoke"}:
        scope_ids = _parse_scope_ids(getattr(args, "scopes", ""))
        if not scope_ids:
            print(f"consent {command}: at least one scope id is required", file=sys.stderr)
            return 2
        ledger = load_ledger()
        for scope_id in scope_ids:
            scope = get_scope(scope_id)
            if scope is None:
                print(f"consent {command}: unknown consent scope id: {scope_id}", file=sys.stderr)
                return 2
            if command == "grant":
                ledger.grant(scope)
            else:
                ledger.revoke(scope)
        path = save_ledger(ledger)
        joined = ", ".join(scope_ids)
        print(f"Somatic consent {command}: {joined}")
        print(f"- stored: {path}")
        return 0
    print("consent: unknown subcommand", file=sys.stderr)
    return 2


def _ingest(args):
    from somatic.consent.scopes import DATA_INGESTION
    from somatic.ingest.apple_health import ingest_apple_health
    from somatic.ingest.csv import ingest_csv
    from somatic.ingest.store import (
        append_readings,
        default_ingest_path,
        erase_stored_readings,
        load_readings,
    )
    from somatic.safety.core import ConsentRequiredError, require_consent

    command = str(getattr(args, "ingest_command", "") or "")
    if command == "status":
        stored = load_readings()
        print("Somatic ingest status")
        print(f"- store: {default_ingest_path()}")
        print(f"- readings: {len(stored)}")
        return 0
    if command == "erase":
        erase_stored_readings()
        print("Somatic ingest store erased")
        return 0
    if command not in {"csv", "apple-health"}:
        print("ingest: unknown subcommand", file=sys.stderr)
        return 2

    ledger = _ledger_for_run(getattr(args, "grant", ""), "ingest")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, DATA_INGESTION)
    except ConsentRequiredError:
        print("ingest: data-ingestion consent required", file=sys.stderr)
        return 2

    try:
        if command == "csv":
            packet = ingest_csv(ledger, args.file)
        else:
            packet = ingest_apple_health(ledger, args.file)
    except ValueError as exc:
        print(f"ingest: {exc}", file=sys.stderr)
        return 2

    if getattr(args, "save", False):
        append_readings(packet.readings)
        print(f"Somatic ingest saved: {default_ingest_path()}")

    encoded = json.dumps(packet.to_dict(), indent=2, sort_keys=True) + "\n"
    out_path = getattr(args, "out", None)
    if out_path:
        destination = Path(out_path)
        destination.write_text(encoded, encoding="utf-8")
        print(f"Somatic ingest packet written: {destination}")
    else:
        print(encoded, end="")
    for note in packet.notes:
        print(f"note: {note}", file=sys.stderr)
    return 0


def _experiment(args):
    from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
    from somatic.experiments.n_of_1 import InterventionTag, evaluate_n_of_1
    from somatic.experiments.store import (
        append_tag,
        default_experiment_path,
        erase_stored_tags,
        load_tags,
    )
    from somatic.ingest.packet import normalize_observed_at
    from somatic.safety.core import ConsentRequiredError, emergency_screen, require_consent

    command = str(getattr(args, "experiment_command", "") or "")
    if command == "status":
        tags = load_tags()
        print("Somatic experiment status")
        print(f"- store: {default_experiment_path()}")
        print(f"- tags: {len(tags)}")
        return 0
    if command == "erase":
        erase_stored_tags()
        print("Somatic experiment store erased")
        return 0
    if command == "tag":
        ledger = _ledger_for_run(getattr(args, "grant", ""), "experiment")
        if ledger is None:
            return 2
        try:
            require_consent(ledger, DATA_INGESTION)
        except ConsentRequiredError:
            print("experiment: data-ingestion consent required to save a tag", file=sys.stderr)
            return 2
        screen = emergency_screen(f"{args.name}\n{args.note}\n{args.metric}")
        if screen.triggered:
            print("experiment: emergency screen triggered; tag not saved", file=sys.stderr)
            print(screen.guidance or "")
            return 2
        try:
            tag = InterventionTag(
                name=str(args.name),
                metric=str(args.metric),
                started_at=normalize_observed_at(str(args.started)),
                ended_at=(
                    normalize_observed_at(str(args.ended)) if str(args.ended or "").strip() else ""
                ),
                note=str(args.note or ""),
            )
        except ValueError as exc:
            print(f"experiment: {exc}", file=sys.stderr)
            return 2
        append_tag(tag)
        print(f"Somatic experiment tagged: {tag.name} ({tag.metric} @ {tag.started_at})")
        print(f"- stored: {default_experiment_path()}")
        return 0
    if command != "evaluate":
        print("experiment: unknown subcommand", file=sys.stderr)
        return 2

    ledger = _ledger_for_run(getattr(args, "grant", ""), "experiment")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, ANALYSIS_INSIGHT)
    except ConsentRequiredError:
        print("experiment: analysis-insight consent required", file=sys.stderr)
        return 2
    data_path = Path(args.data)
    try:
        data_packet = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"experiment: could not read --data: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data_packet, dict):
        print("experiment: --data must contain a JSON object", file=sys.stderr)
        return 2
    try:
        report = evaluate_n_of_1(
            ledger,
            data_packet,
            metric=str(args.metric),
            started_at=str(args.started),
            name=str(args.name or "untagged-interval"),
            ended_at=str(args.ended or ""),
            note=str(args.note or ""),
        )
    except (TypeError, ValueError) as exc:
        print(f"experiment: {exc}", file=sys.stderr)
        return 2
    print("Somatic n-of-1 experiment report")
    print(f"- movement: {report.movement}")
    print(f"- baseline_n: {report.baseline_n}")
    print(f"- followup_n: {report.followup_n}")
    print(f"- generated_at: {report.generated_at}")
    print(report.result.summary)
    for note in report.notes:
        print(f"- note: {note}")
    return 0


def _research(args):
    from somatic.consent.scopes import AUTONOMOUS_RESEARCH
    from somatic.research import HONEST_NULL, run_research_loop
    from somatic.safety.core import ConsentRequiredError, require_consent

    command = str(getattr(args, "research_command", "") or "")
    if command != "ask":
        print("research: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "research")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, AUTONOMOUS_RESEARCH)
    except ConsentRequiredError:
        print("research: autonomous-research consent required", file=sys.stderr)
        return 2
    k = int(getattr(args, "k", 5) or 5)
    if k < 1:
        print("research: --k must be >= 1", file=sys.stderr)
        return 2
    report = run_research_loop(
        ledger,
        str(args.question),
        corpus_path=getattr(args, "corpus", None),
        k=k,
    )
    print("Somatic offline research report")
    print(f"- honest_null: {report.honest_null}")
    print(f"- evidence_grade: {report.result.evidence_grade}")
    print(f"- retrieved: {len(report.retrieved)}")
    print(f"- bound_claims: {len(report.claims)}")
    print(f"- dropped_unbound: {report.dropped_unbound}")
    print(report.result.summary)
    if report.honest_null:
        print(HONEST_NULL)
    return 0


def _remedy(args):
    from somatic.consent.scopes import REMEDY_LIBRARY
    from somatic.remedy import lookup_remedy
    from somatic.research import HONEST_NULL
    from somatic.safety.core import ConsentRequiredError, require_consent

    command = str(getattr(args, "remedy_command", "") or "")
    if command != "lookup":
        print("remedy: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "remedy")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, REMEDY_LIBRARY)
    except ConsentRequiredError:
        print("remedy: remedy-library consent required", file=sys.stderr)
        return 2
    report = lookup_remedy(ledger, str(args.query))
    print("Somatic remedy library")
    print(f"- honest_null: {report.honest_null}")
    for index, entry in enumerate(report.entries, start=1):
        print(f"## Entry {index}")
        print(f"- evidence_grade: {entry.evidence_grade}")
        cites = ", ".join(entry.citations) or "(none)"
        print(f"- citations: {cites}")
        print(entry.claim)
        for note in entry.safety_notes:
            print(f"- safety: {note}")
    if report.honest_null:
        print(HONEST_NULL)
    return 0


def _parasite(args):
    from somatic.consent.scopes import AUTONOMOUS_RESEARCH
    from somatic.parasite import ask_parasite
    from somatic.research import HONEST_NULL
    from somatic.safety.core import ConsentRequiredError, require_consent

    command = str(getattr(args, "parasite_command", "") or "")
    if command != "ask":
        print("parasite: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "parasite")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, AUTONOMOUS_RESEARCH)
    except ConsentRequiredError:
        print("parasite: autonomous-research consent required", file=sys.stderr)
        return 2
    report = ask_parasite(ledger, str(args.question))
    print("Somatic parasite Q&A (informational; not identification)")
    print(f"- honest_null: {report.honest_null}")
    print(f"- evidence_grade: {report.research.result.evidence_grade}")
    print(report.research.result.summary)
    print(f"- routing: {report.routing_note}")
    if report.honest_null and report.research.result.consent_scope != "emergency-screen":
        print(HONEST_NULL)
    return 0


def _bus(args):
    from somatic.consent.scopes import ANALYSIS_INSIGHT
    from somatic.evidence_bus.adapter import HypothesisSpec
    from somatic.evidence_bus.loop import run_evidence_loop
    from somatic.safety.core import ConsentRequiredError, require_consent

    if str(getattr(args, "bus_command", "") or "") != "run":
        print("bus: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "bus")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, ANALYSIS_INSIGHT)
    except ConsentRequiredError:
        print("bus: analysis-insight consent required", file=sys.stderr)
        return 2
    modalities = tuple(_parse_scope_ids(getattr(args, "modalities", "")))
    try:
        spec = HypothesisSpec(
            id=str(args.id),
            statement=str(args.hypothesis),
            domain=str(args.domain),
        )
        report = run_evidence_loop(
            ledger,
            spec,
            modalities=modalities or None,
            seed=int(getattr(args, "seed", 0) or 0),
        )
    except ValueError as exc:
        print(f"bus: {exc}", file=sys.stderr)
        return 2
    print("Somatic Evidence Bus (sandbox)")
    print(f"- emergency: {report.emergency_triggered}")
    print(f"- steps: {len(report.steps)}")
    print(report.verdict.summary)
    for step in report.steps:
        print(f"- {step.modality}: confidence={step.confidence:.2f} sha256={step.sha256[:12]}")
    return 0


def _sensor_roster(args):
    from somatic.consent.scopes import ANALYSIS_INSIGHT, DATA_INGESTION
    from somatic.evidence_bus.sandbox_adapters import SensorHardwareDisabled
    from somatic.safety.core import ConsentRequiredError, require_consent
    from somatic.sensors.fusion import fuse_rf_vision
    from somatic.sensors.roster import list_sensor_lanes, scan_sensor

    command = str(getattr(args, "roster_command", "") or "")
    if command == "list":
        print("Somatic sensor roster (sandbox default; hardware closed)")
        for lane in list_sensor_lanes():
            extra = "available" if lane.extra_available else "unavailable"
            print(
                f"- {lane.modality}: extra={lane.extra_package} ({extra}); "
                "live_hardware=false; sandbox=true"
            )
        return 0
    if command == "live-grant":
        from somatic.sensors.live_consent import load_live_consent, save_live_consent

        modality = str(getattr(args, "modality", "") or "csi").strip().lower()
        live = load_live_consent()
        modality = str(getattr(args, "modality", "csi") or "csi")
        try:
            live.grant(modality, subject_consent=bool(getattr(args, "subject_consent", False)))
        except ValueError as exc:
            print(f"sensor-roster: {exc}", file=sys.stderr)
            return 2
        save_live_consent(live)
        if modality == "csi":
            print(
                "Somatic live CSI grant ON (subject consent recorded; still needs data-ingestion)"
            )
        else:
            print(
                f"Somatic live {modality} grant ON (subject consent recorded; "
                "still needs data-ingestion)"
            )
        return 0
    if command == "live-revoke":
        from somatic.sensors.live_consent import load_live_consent, save_live_consent

        modality = str(getattr(args, "modality", "") or "csi").strip().lower()
        live = load_live_consent()
        live.revoke(modality)
        save_live_consent(live)
        if modality == "csi":
            from somatic.sensors.live_csi import stop_ingest

            stop_ingest()
        elif modality in {"video", "video3d"}:
            from somatic.sensors.live_video import stop_video_ingest

            stop_video_ingest(modality)
        print(f"Somatic live {modality} grant OFF")
        return 0
    ledger = _ledger_for_run(getattr(args, "grant", ""), "sensor-roster")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, DATA_INGESTION)
        require_consent(ledger, ANALYSIS_INSIGHT)
    except ConsentRequiredError as exc:
        print(f"sensor-roster: consent required for scope: {exc.scope_id}", file=sys.stderr)
        return 2
    try:
        if command == "scan":
            live = bool(getattr(args, "live", False))
            report = scan_sensor(
                ledger,
                str(args.modality),
                ticks=int(getattr(args, "ticks", 1) or 1),
                seed=int(getattr(args, "seed", 0) or 0),
                live=live,
            )
            label = f"live {str(args.modality)}" if live else "sandbox"
            print(f"Somatic sensor roster scan ({label})")
            print(f"- modality: {args.modality}")
            print(f"- steps: {len(report.steps)}")
            print(report.verdict.summary)
            return 0
        if command == "listen":
            import time

            from somatic.sensors.live_csi import require_live_csi, start_ingest

            require_live_csi(ledger)
            ingest = start_ingest()
            print(
                f"Somatic CSI UDP ingest on {ingest.host}:{ingest.bound_port} "
                "(features only; Ctrl+C to stop)"
            )
            try:
                while ingest.running:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                ingest.stop()
                print("Somatic CSI UDP ingest stopped")
            return 0
        if command == "fuse":
            fused = fuse_rf_vision(ledger, seed=int(getattr(args, "seed", 0) or 0))
            print("Somatic RF↔vision fusion (sandbox)")
            print(json.dumps(fused, indent=2, sort_keys=True))
            return 0
    except SensorHardwareDisabled as exc:
        print(f"sensor-roster: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"sensor-roster: {exc}", file=sys.stderr)
        return 2
    print("sensor-roster: unknown subcommand", file=sys.stderr)
    return 2


def _science(args):
    from somatic.consent.scopes import ANALYSIS_INSIGHT, AUTONOMOUS_RESEARCH
    from somatic.safety.core import ConsentRequiredError, require_consent
    from somatic.science.harness import run_science_loop

    if str(getattr(args, "science_command", "") or "") != "run":
        print("science: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "science")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, AUTONOMOUS_RESEARCH)
        require_consent(ledger, ANALYSIS_INSIGHT)
    except ConsentRequiredError as exc:
        print(f"science: consent required for scope: {exc.scope_id}", file=sys.stderr)
        return 2
    try:
        report = run_science_loop(
            ledger,
            str(args.goal),
            seed=int(getattr(args, "seed", 0) or 0),
        )
    except ValueError as exc:
        print(f"science: {exc}", file=sys.stderr)
        return 2
    print("Somatic science harness (sandbox)")
    print(f"- blocked: {report.blocked or 'no'}")
    print(f"- ranked: {report.ranked_hypothesis_id}")
    print(f"- next_measurement: {report.next_measurement.get('modality') or '(none)'}")
    print(report.summary)
    return 0


def _avatar(args):
    from somatic.consent.scopes import AI_ADVISORY
    from somatic.presence.avatar import render_presence
    from somatic.safety.core import ConsentRequiredError, require_consent

    if str(getattr(args, "avatar_command", "") or "") != "speak":
        print("avatar: unknown subcommand", file=sys.stderr)
        return 2
    ledger = _ledger_for_run(getattr(args, "grant", ""), "avatar")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, AI_ADVISORY)
    except ConsentRequiredError:
        print("avatar: ai-advisory consent required", file=sys.stderr)
        return 2
    try:
        rendered = render_presence(
            ledger,
            str(args.verdict),
            persona=str(args.persona),
        )
    except ValueError as exc:
        print(f"avatar: {exc}", file=sys.stderr)
        return 2
    print("Somatic presence (render-only)")
    print(f"- persona: {rendered.persona}")
    print(f"- verdict_unchanged: {rendered.verdict_unchanged}")
    print(f"- tts: {rendered.tts_runtime}")
    print(f"- talking_head: {rendered.talking_head_runtime}")
    print(rendered.speech)
    return 0


def _bench_run(args):
    from somatic.bench.runner import run_bench
    from somatic.consent.scopes import ANALYSIS_INSIGHT, AUTONOMOUS_RESEARCH
    from somatic.safety.core import ConsentRequiredError, require_consent

    ledger = _ledger_for_run(getattr(args, "grant", ""), "bench-run")
    if ledger is None:
        return 2
    try:
        require_consent(ledger, AUTONOMOUS_RESEARCH)
        require_consent(ledger, ANALYSIS_INSIGHT)
    except ConsentRequiredError as exc:
        print(f"bench-run: consent required for scope: {exc.scope_id}", file=sys.stderr)
        return 2
    task = str(getattr(args, "task", "") or "").strip() or None
    score = run_bench(ledger, task_path=task, seed=int(getattr(args, "seed", 0) or 0))
    print("Somatic bench (sandbox)")
    print(f"- task: {score.task_id}")
    print(f"- passed: {score.passed}")
    print(f"- evidence_efficiency: {score.evidence_efficiency}")
    print(json.dumps(score.leaderboard, indent=2, sort_keys=True))
    return 0


def _evidence_verify(args):
    from somatic.provenance.cas import verify_file

    result = verify_file(str(args.file))
    print("Somatic evidence verify")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


def _ui(args):
    from somatic.bridge.server import serve_ui

    return serve_ui(
        host=str(args.host),
        port=int(args.port),
        open_browser=not bool(args.no_browser),
    )


def _analyze(args):
    from somatic.flows.analyze import analyze_user_data

    data_packet = _load_json_object_arg(str(args.data), "analyze", "--data")
    if data_packet is None:
        return 2

    references = None
    if args.references:
        references = _load_json_object_arg(str(args.references), "analyze", "--references")
        if references is None:
            return 2

    baselines = None
    if getattr(args, "baselines", None):
        baselines = _load_json_object_arg(str(args.baselines), "analyze", "--baselines")
        if baselines is None:
            return 2

    ledger = _ledger_for_run(args.grant, "analyze")
    if ledger is None:
        return 2

    model_config, key_error = _model_config_from_args(args, "analyze")
    if key_error:
        return 2

    report = analyze_user_data(
        ledger,
        data_packet,
        str(args.question),
        references=references,
        baselines=baselines,
        model_config=model_config,
    )

    print("Somatic analyze report")
    print(f"- results: {len(report.results)}")
    print(f"- notes: {len(report.notes)}")
    for index, result in enumerate(report.results, start=1):
        print(f"\n[{index}] evidence_grade={result.evidence_grade}")
        print(f"summary: {result.summary}")
        print(f"informational_notice: {result.informational_notice}")
        print(f"professional_routing: {result.professional_routing}")
    if report.notes:
        print("\nnotes:")
        for note in report.notes:
            print(f"- {note}")
    return 0


def _share(args):
    from somatic.consent.scopes import PROFESSIONAL_SHARING
    from somatic.flows.analyze import analyze_user_data
    from somatic.flows.share import render_fhir_bundle, render_professional_summary
    from somatic.safety.core import ConsentRequiredError, require_consent

    data_packet = _load_json_object_arg(str(args.data), "share", "--data")
    if data_packet is None:
        return 2

    references = None
    if args.references:
        references = _load_json_object_arg(str(args.references), "share", "--references")
        if references is None:
            return 2

    baselines = None
    if getattr(args, "baselines", None):
        baselines = _load_json_object_arg(str(args.baselines), "share", "--baselines")
        if baselines is None:
            return 2

    ledger = _ledger_for_run(args.grant, "share")
    if ledger is None:
        return 2

    try:
        require_consent(ledger, PROFESSIONAL_SHARING)
    except ConsentRequiredError:
        print("share: professional-sharing consent required", file=sys.stderr)
        return 2

    model_config, key_error = _model_config_from_args(args, "share")
    if key_error:
        return 2

    report = analyze_user_data(
        ledger,
        data_packet,
        str(args.question),
        references=references,
        baselines=baselines,
        model_config=model_config,
    )

    try:
        markdown = render_professional_summary(
            ledger,
            report,
            patient_label=str(args.patient_label or ""),
            clinician_note=str(args.clinician_note or ""),
        )
    except ConsentRequiredError:
        print("share: professional-sharing consent required", file=sys.stderr)
        return 2

    out_path = getattr(args, "out", None)
    if out_path:
        destination = Path(out_path)
        destination.write_text(markdown, encoding="utf-8")
        print(f"Somatic share summary written: {destination}")
    else:
        print(markdown)

    fhir_out = getattr(args, "fhir_out", None)
    if fhir_out:
        sidecar = render_fhir_bundle(
            ledger,
            report,
            patient_label=str(args.patient_label or ""),
        )
        fhir_destination = Path(fhir_out)
        fhir_destination.write_text(
            json.dumps(sidecar, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Somatic share FHIR sidecar written: {fhir_destination}")
    return 0


def _doctor():
    from somatic.analysis.provider import FinchExtrasProvider, FinchExtrasProviderConfig
    from somatic.evidence.document_fixture import DocumentFixtureEvidenceProvider
    from somatic.providers.boltz import BoltzProvider, BoltzProviderConfig
    from somatic.providers.paperqa2 import PaperQA2LiteratureProvider, PaperQA2ProviderConfig
    from somatic.providers.robin import (
        AVIARY_SOURCE_PATH,
        LDP_SOURCE_PATH,
        ROBIN_SOURCE_PATH,
    )
    from somatic.providers.scientific_agent_skills import (
        ScientificAgentSkillsProvider,
        ScientificAgentSkillsProviderConfig,
    )
    from somatic.providers.team_orchestration import (
        AUTOSCIENTISTS_LICENSE_STATUS,
        AUTOSCIENTISTS_SOURCE_PATH,
    )
    from somatic.safety.phase11_contracts import (
        PHASE11_DOCUMENT_DOMAIN,
        PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
        phase11_acceptance_followup_status_summary,
        phase11_audit_handoff_status_summary,
        phase11_audit_index_status_summary,
        phase11_decision_closeout_status_summary,
        phase11_document_ingestion_contract_spec,
        phase11_dossier_lifecycle_status_summary,
        phase11_followup_queue_index_status_summary,
        phase11_handoff_acceptance_status_summary,
        phase11_planning_governance_closeout_status_summary,
        phase11_preflight_status_summary,
        phase11_review_record_status_summary,
        phase11_review_trail_export_status_summary,
        phase11_runtime_authorization_gap_ledger_status_summary,
        phase11_wifi_csi_rf_booth_contract_spec,
    )
    from somatic.safety.phase12_contracts import (
        phase12a_runtime_authorization_design_charter_status_summary,
        phase12b_runtime_authorization_record_candidate_status_summary,
        phase12c_visual_supervision_capability_profile_status_summary,
        phase12d_visual_desktop_consent_gate_requirements_status_summary,
        phase12e_physiological_sensor_capability_profile_status_summary,
        phase12f_secure_drop_consumer_boundary_status_summary,
        phase12g_production_readiness_coverage_matrix_status_summary,
        phase12h_somatic_standalone_production_readiness_ownership_map_status_summary,
        phase12i_integrative_herbal_nutrition_knowledge_capability_profile_status_summary,
        phase12k_external_compute_quantum_backend_capability_profile_status_summary,
        phase12l_fabric_interop_a2a_audit_boundary_capability_profile_status_summary,
        phase12m_specialized_model_option_registry_capability_profile_status_summary,
        phase12n_workflow_orchestration_mode_registry_capability_profile_status_summary,
        phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix_status_summary,
        phase12p_workflow_mode_activation_request_review_packet_boundary_status_summary,
        phase12q_non_authorizing_workflow_mode_review_decision_record_status_summary,
        phase12r_workflow_mode_review_audit_trail_index_status_summary,
        phase12s_workflow_mode_review_chain_closeout_summary_status_summary,
    )
    from somatic.sensors.csi_adapter import (
        CSI_RUVIEW_REFERENCE_STATUS,
        booth_first_csi_planning_profile,
        wifi_csi_source_adapter_status,
    )
    from somatic.sensors.environment import EnvironmentFixtureSensorProvider
    from somatic.sensors.registry import (
        sensor_evidence_provider_ids,
        sensor_evidence_provider_manifest,
        validate_sensor_evidence_provider_manifest,
    )
    from somatic.sensors.sandbox import SandboxSensorProvider

    paperqa2_provider = PaperQA2LiteratureProvider(PaperQA2ProviderConfig())
    paperqa2_dependency = "available" if paperqa2_provider.is_available() else "unavailable"
    science_skills_provider = ScientificAgentSkillsProvider(ScientificAgentSkillsProviderConfig())
    science_skills_source = "staged" if science_skills_provider.is_source_staged() else "not staged"
    science_skills_dependency = (
        "available" if science_skills_provider.is_available() else "unavailable"
    )
    autoscientists_source = "staged" if Path(AUTOSCIENTISTS_SOURCE_PATH).exists() else "not staged"
    robin_source = "staged" if Path(ROBIN_SOURCE_PATH).exists() else "not staged"
    aviary_source = "staged" if Path(AVIARY_SOURCE_PATH).exists() else "not staged"
    ldp_source = "staged" if Path(LDP_SOURCE_PATH).exists() else "not staged"
    finch_extras_status = FinchExtrasProvider(FinchExtrasProviderConfig()).status()
    boltz_status = BoltzProvider(BoltzProviderConfig()).status()
    sensor_status = SandboxSensorProvider().status()
    environment_status = EnvironmentFixtureSensorProvider().status()
    document_status = DocumentFixtureEvidenceProvider().status()
    csi_source_adapter_status = wifi_csi_source_adapter_status()
    csi_real_mode_gate = csi_source_adapter_status.get("real_mode_readiness_gate", {})
    csi_source_adapter_labels = ", ".join(
        str(label) for label in csi_source_adapter_status.get("capability_labels", ())
    )
    booth_profile = booth_first_csi_planning_profile()
    document_adapter_labels = ", ".join(
        str(label) for label in document_status.get("adapter_boundary_labels", ())
    )
    document_real_mode_gate = document_status.get("real_mode_readiness_gate", {})
    document_phase11_spec = phase11_document_ingestion_contract_spec()
    csi_phase11_spec = phase11_wifi_csi_rf_booth_contract_spec()
    document_phase11_review_status = phase11_review_record_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_review_status = phase11_review_record_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_preflight_status = phase11_preflight_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_preflight_status = phase11_preflight_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_lifecycle_status = phase11_dossier_lifecycle_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_lifecycle_status = phase11_dossier_lifecycle_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_audit_index_status = phase11_audit_index_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_audit_index_status = phase11_audit_index_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_audit_handoff_status = phase11_audit_handoff_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_audit_handoff_status = phase11_audit_handoff_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_handoff_acceptance_status = phase11_handoff_acceptance_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_handoff_acceptance_status = phase11_handoff_acceptance_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_acceptance_followup_status = phase11_acceptance_followup_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_acceptance_followup_status = phase11_acceptance_followup_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_followup_queue_status = phase11_followup_queue_index_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_followup_queue_status = phase11_followup_queue_index_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_decision_closeout_status = phase11_decision_closeout_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_decision_closeout_status = phase11_decision_closeout_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_review_trail_export_status = phase11_review_trail_export_status_summary(
        domain=PHASE11_DOCUMENT_DOMAIN,
    )
    csi_phase11_review_trail_export_status = phase11_review_trail_export_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    document_phase11_runtime_gap_ledger_status = (
        phase11_runtime_authorization_gap_ledger_status_summary(
            domain=PHASE11_DOCUMENT_DOMAIN,
        )
    )
    csi_phase11_runtime_gap_ledger_status = phase11_runtime_authorization_gap_ledger_status_summary(
        domain=PHASE11_WIFI_CSI_RF_BOOTH_DOMAIN,
    )
    phase11_planning_governance_closeout_status = (
        phase11_planning_governance_closeout_status_summary()
    )
    phase12a_runtime_authorization_charter_status = (
        phase12a_runtime_authorization_design_charter_status_summary()
    )
    phase12b_record_status = phase12b_runtime_authorization_record_candidate_status_summary()
    phase12c_profile_status = phase12c_visual_supervision_capability_profile_status_summary()
    phase12d_consent_gate_status = (
        phase12d_visual_desktop_consent_gate_requirements_status_summary()
    )
    phase12e_physiological_sensor_status = (
        phase12e_physiological_sensor_capability_profile_status_summary()
    )
    phase12f_secure_drop_boundary_status = phase12f_secure_drop_consumer_boundary_status_summary()
    phase12g_production_readiness_status = (
        phase12g_production_readiness_coverage_matrix_status_summary()
    )
    phase12h_standalone_ownership_status = (
        phase12h_somatic_standalone_production_readiness_ownership_map_status_summary()
    )
    phase12i_integrative_knowledge_status = (
        phase12i_integrative_herbal_nutrition_knowledge_capability_profile_status_summary()
    )
    phase12k_external_compute_quantum_status = (
        phase12k_external_compute_quantum_backend_capability_profile_status_summary()
    )
    phase12l_fabric_interop_status = (
        phase12l_fabric_interop_a2a_audit_boundary_capability_profile_status_summary()
    )
    phase12m_model_option_registry_status = (
        phase12m_specialized_model_option_registry_capability_profile_status_summary()
    )
    phase12n_workflow_mode_registry_status = (
        phase12n_workflow_orchestration_mode_registry_capability_profile_status_summary()
    )
    phase12o_workflow_mode_safety_gate_status = (
        phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix_status_summary()
    )
    phase12p_workflow_mode_activation_request_status = (
        phase12p_workflow_mode_activation_request_review_packet_boundary_status_summary()
    )
    phase12q_workflow_mode_review_decision_status = (
        phase12q_non_authorizing_workflow_mode_review_decision_record_status_summary()
    )
    phase12r_workflow_mode_review_audit_trail_index_status = (
        phase12r_workflow_mode_review_audit_trail_index_status_summary()
    )
    phase12s_workflow_mode_review_chain_closeout_status = (
        phase12s_workflow_mode_review_chain_closeout_summary_status_summary()
    )
    sensor_evidence_provider_id_tuple = sensor_evidence_provider_ids()
    sensor_evidence_registry_ids = ", ".join(sensor_evidence_provider_id_tuple)
    sensor_evidence_manifest = sensor_evidence_provider_manifest()
    sensor_evidence_manifest_result = validate_sensor_evidence_provider_manifest(
        sensor_evidence_manifest
    )
    sensor_evidence_registry_status = (
        "valid" if sensor_evidence_manifest_result.compatible else "invalid"
    )

    print("Somatic doctor")
    print("- foundation: Phase 1C scaffold with Phase 2.5 offline tournament")
    print("- runner: offline mock runner, pairwise debate, Elo, and team scaffold available")
    print("- provider secrets: no provider secrets required")
    print("- network: no runtime network code in the basic runner")
    print("- advanced lanes: scaffolded and disabled by default")
    print("- PaperQA2 provider: scaffolded, disabled by default")
    print(f"- PaperQA2 optional dependency: {paperqa2_dependency}")
    print("- scientific-agent-skills provider: scaffolded, disabled by default")
    print(f"- scientific-agent-skills source: {science_skills_source}")
    print(f"- scientific-agent-skills optional dependency/source: {science_skills_dependency}")
    print("- scientific-agent-skills execution: disabled")
    print("- AutoScientists provider: reference-only, disabled by default")
    print(f"- AutoScientists source: {autoscientists_source}")
    print(f"- AutoScientists license status: {AUTOSCIENTISTS_LICENSE_STATUS}")
    print("- AutoScientists execution: disabled")
    print("- FutureHouse Robin provider: reference-only, disabled by default")
    print(f"- FutureHouse Robin source: {robin_source}")
    print(f"- Aviary source: {aviary_source}")
    print(f"- LDP source: {ldp_source}")
    print("- FutureHouse Robin/Aviary/LDP execution: disabled")
    print("- Finch optional extras provider: scaffolded, disabled by default")
    for extra in finch_extras_status["extras"]:
        print(f"- Finch optional dependency {extra['id']}: {extra['availability']}")
    print("- Finch optional extras execution: disabled")
    print("- Finch standard-library fallback: active")
    print("- Boltz-2 biomodel provider: scaffolded, disabled by default")
    print(f"- Boltz-2 staged source: {boltz_status['source_status']}")
    print(f"- Boltz-2 optional dependency: {boltz_status['optional_dependency']}")
    print("- Boltz-2 model downloads: disabled")
    print("- Boltz-2 MSA server: disabled")
    print("- Boltz-2 runtime execution: disabled")
    print("- Boltz-2 GPU execution: disabled")
    print("- Biomodel safety gates: scaffolded")
    print("- Biomodel runtime disabled: true")
    print("- Biomodel model downloads: disabled")
    print("- Biomodel MSA/network: disabled")
    print("- Biomodel fake-backed in-silico mode: available")
    print("- Biomodel provenance packaging: planning only")
    print("- Biomodel Fabric pack class recommendation: data")
    print("- Biomodel Fabric pack publishing: disabled")
    print("- Biomodel Fabric transport/install: disabled")
    print("- Fabric federation connector: out-of-process sidecar ready when configured")
    print("- Fabric federation sidecar: loopback HTTP with bearer token")
    print("- Fabric federation registry: authenticated DID registration and keepalive")
    print("- Fabric federation allowlist: authenticated sibling DIDs only")
    print("- Fabric federation receive integrity: contentId re-verified before delivery")
    print("- Fabric federation private fabric-core import: disabled")
    print("- Fabric federation public DHT/swarm: disabled")
    print("- Biomodel real runtime: future only")
    print("- in-silico-screening workflow: fake-backed biomodel planning only")
    print("- Sensor provider boundary: scaffolded, local-first, private by default")
    print(f"- Sensor evidence provider registry: {sensor_evidence_registry_ids}")
    print(f"- Sensor evidence provider count: {len(sensor_evidence_provider_id_tuple)}")
    print(f"- Sensor evidence registry validation: {sensor_evidence_registry_status}")
    print("- Sensor evidence registry output: sanitized metadata only")
    print(f"- Sandbox sensor provider: {sensor_status['mode']}, fake-backed only")
    print("- Sandbox sensor hardware access: disabled")
    print("- Sandbox sensor network calls: disabled")
    print("- Sandbox sensor clinical interpretation: disabled")
    print("- Sandbox sensor emergency triage: disabled")
    print("- n-of-1 workflow: fake-backed sensor planning only")
    print("- WiFi CSI planning scaffold: fake-backed metadata only")
    print("- WiFi CSI hardware access: disabled")
    print("- WiFi CSI packet capture: disabled")
    print("- WiFi CSI monitor mode: disabled")
    print("- WiFi CSI device probing: disabled")
    print("- WiFi CSI raw RF/CSI export: disabled")
    print("- WiFi CSI source staging: Phase 8A read-only reference inventory")
    print("- WiFi CSI staged source execution/import/vendor: disabled")
    print("- Environment fixture evidence provider: fixture-only metadata pack")
    print(f"- Environment fixture provider mode: {environment_status['mode']}")
    print("- Environment fixture hardware access: disabled")
    print("- Environment fixture network calls: disabled")
    print("- Environment fixture live capture: disabled")
    print("- Document fixture evidence provider: fixture-only metadata pack")
    print(
        "- Document fixture adapter: "
        f"{document_status['adapter_kind']}, "
        f"contract v{document_status['adapter_contract_version']}"
    )
    print(f"- Document fixture adapter boundary: {document_adapter_labels}")
    print("- Document fixture adapter ingestion/parsing/network: disabled")
    print(f"- Document real-mode readiness gate: {document_real_mode_gate.get('status')}")
    print(
        f"- Document real-mode missing gates: {document_real_mode_gate.get('missing_gate_count')}"
    )
    print("- Document real-mode execution permitted: false")
    print("- WiFi CSI parser scaffold: Phase 8C stable offline fixture contract")
    print("- WiFi CSI parser dependency profile: standard-library only")
    print("- WiFi CSI parser output: report and parsed summary metadata only")
    print("- WiFi CSI parser replay validation: deterministic local fixtures")
    print("- WiFi CSI replay provider: Phase 8D fixture-backed sanitized parser replay")
    print("- WiFi CSI evidence scoring: Phase 8E sanitized metadata only")
    print("- WiFi CSI batch replay evaluation: Phase 8F tournament readiness metadata only")
    print("- WiFi CSI evidence-pack export: Phase 8G sanitized metadata only")
    print(
        "- WiFi CSI source adapter: "
        f"{csi_source_adapter_status['adapter_kind']}, "
        f"contract v{csi_source_adapter_status['adapter_contract_version']}"
    )
    print(f"- WiFi CSI source adapter boundary: {csi_source_adapter_labels}")
    print("- WiFi CSI source adapter validation: fail-closed metadata only")
    print(f"- WiFi CSI real-mode readiness gate: {csi_real_mode_gate.get('status')}")
    print(f"- WiFi CSI real-mode missing gates: {csi_real_mode_gate.get('missing_gate_count')}")
    print("- WiFi CSI real-mode execution permitted: false")
    print(f"- WiFi CSI RuView posture: {CSI_RUVIEW_REFERENCE_STATUS}")
    print(f"- WiFi CSI booth-first profile: {booth_profile['profile']}")
    print("- WiFi CSI booth-first topology: future fixed AP plus 4-6 receiver nodes")
    print("- WiFi CSI serial/SD-card/MQTT/UDP listener paths: disabled")
    print("- WiFi CSI monitor mode/tcpdump/tshark/aircrack-ng: disabled")
    print("- WiFi CSI bystander-sensitive real mode: future only after explicit consent and review")
    print("- WiFi CSI RuView execution/import/vendor/model use: disabled")
    print("- Phase 11A real-mode contract specs: planning only, runtime disabled")
    print(
        f"- Phase 11A document contracts: {', '.join(document_phase11_spec['required_contracts'])}"
    )
    print(
        "- Phase 11A document contract runtime: "
        f"{document_phase11_spec['runtime_stage']}, execution permitted false"
    )
    print(f"- Phase 11A RF booth contracts: {', '.join(csi_phase11_spec['required_contracts'])}")
    print(
        "- Phase 11A RF booth contract runtime: "
        f"{csi_phase11_spec['runtime_stage']}, execution permitted false"
    )
    print("- Phase 11B review-record fixtures: planning evidence only, runtime disabled")
    print(
        "- Phase 11B document review status: "
        f"{document_phase11_review_status['review_record_status']}"
    )
    print(
        "- Phase 11B document review missing gates: "
        f"{document_phase11_review_status['missing_gate_count']}"
    )
    print(
        f"- Phase 11B RF booth review status: {csi_phase11_review_status['review_record_status']}"
    )
    print(
        "- Phase 11B RF booth review missing gates: "
        f"{csi_phase11_review_status['missing_gate_count']}"
    )
    print("- Phase 11B review-record execution permitted: false")
    print("- Phase 11C preflight dossiers: planning packets only, runtime disabled")
    print(
        "- Phase 11C document preflight status: "
        f"{document_phase11_preflight_status['preflight_status']}"
    )
    print(
        "- Phase 11C document preflight missing gates: "
        f"{document_phase11_preflight_status['missing_gate_count']}"
    )
    print(
        f"- Phase 11C RF booth preflight status: {csi_phase11_preflight_status['preflight_status']}"
    )
    print(
        "- Phase 11C RF booth preflight missing gates: "
        f"{csi_phase11_preflight_status['missing_gate_count']}"
    )
    print("- Phase 11C preflight execution permitted: false")
    print("- Phase 11D dossier lifecycle audit: audit trail only, runtime disabled")
    print(
        "- Phase 11D document lifecycle stage: "
        f"{document_phase11_lifecycle_status['lifecycle_stage']}"
    )
    print(
        "- Phase 11D document audit decision: "
        f"{document_phase11_lifecycle_status['audit_decision']}"
    )
    print(
        f"- Phase 11D RF booth lifecycle stage: {csi_phase11_lifecycle_status['lifecycle_stage']}"
    )
    print(f"- Phase 11D RF booth audit decision: {csi_phase11_lifecycle_status['audit_decision']}")
    print("- Phase 11D lifecycle audit execution permitted: false")
    print("- Phase 11E audit index/change control: local metadata only, runtime disabled")
    print(
        f"- Phase 11E document audit index status: {document_phase11_audit_index_status['status']}"
    )
    print(
        "- Phase 11E document audit index entries: "
        f"{document_phase11_audit_index_status['entry_count']}"
    )
    print(f"- Phase 11E RF booth audit index status: {csi_phase11_audit_index_status['status']}")
    print(
        f"- Phase 11E RF booth audit index entries: {csi_phase11_audit_index_status['entry_count']}"
    )
    print("- Phase 11E audit index execution permitted: false")
    print("- Phase 11F audit handoffs: compact reporting only, runtime disabled")
    print(f"- Phase 11F document handoff status: {document_phase11_audit_handoff_status['status']}")
    print(
        "- Phase 11F document unresolved reviews: "
        f"{document_phase11_audit_handoff_status['unresolved_review_count']}"
    )
    print(f"- Phase 11F RF booth handoff status: {csi_phase11_audit_handoff_status['status']}")
    print(
        "- Phase 11F RF booth unresolved reviews: "
        f"{csi_phase11_audit_handoff_status['unresolved_review_count']}"
    )
    print("- Phase 11F audit handoff execution permitted: false")
    print("- Phase 11G handoff acceptance checks: planning review only, runtime disabled")
    print(
        "- Phase 11G document acceptance status: "
        f"{document_phase11_handoff_acceptance_status['status']}"
    )
    print(
        "- Phase 11G document accepted for planning: "
        f"{str(document_phase11_handoff_acceptance_status['accepted_for_planning']).lower()}"
    )
    print(
        f"- Phase 11G RF booth acceptance status: {csi_phase11_handoff_acceptance_status['status']}"
    )
    print(
        "- Phase 11G RF booth accepted for planning: "
        f"{str(csi_phase11_handoff_acceptance_status['accepted_for_planning']).lower()}"
    )
    print("- Phase 11G handoff acceptance execution permitted: false")
    print("- Phase 11H follow-up/remediation queues: planning only, runtime disabled")
    print(
        "- Phase 11H document follow-up status: "
        f"{document_phase11_acceptance_followup_status['status']}"
    )
    print(
        "- Phase 11H document follow-up type: "
        f"{document_phase11_acceptance_followup_status['followup_type']}"
    )
    print(
        f"- Phase 11H RF booth follow-up status: {csi_phase11_acceptance_followup_status['status']}"
    )
    print(
        "- Phase 11H RF booth follow-up type: "
        f"{csi_phase11_acceptance_followup_status['followup_type']}"
    )
    print("- Phase 11H follow-up/remediation execution permitted: false")
    print("- Phase 11I follow-up queue indexes: reviewer navigation only, runtime disabled")
    print(f"- Phase 11I document queue status: {document_phase11_followup_queue_status['status']}")
    print(
        "- Phase 11I document queue unresolved reviews: "
        f"{document_phase11_followup_queue_status['unresolved_review_count']}"
    )
    print(f"- Phase 11I RF booth queue status: {csi_phase11_followup_queue_status['status']}")
    print(
        "- Phase 11I RF booth queue stale count: "
        f"{csi_phase11_followup_queue_status['stale_count']}"
    )
    print("- Phase 11I queue index execution permitted: false")
    print("- Phase 11J reviewer decision closeouts: planning metadata only, runtime disabled")
    print(
        "- Phase 11J document closeout decision: "
        f"{document_phase11_decision_closeout_status['closeout_decision']}"
    )
    print(
        "- Phase 11J document closeout status: "
        f"{document_phase11_decision_closeout_status['closeout_status']}"
    )
    print(
        "- Phase 11J RF booth closeout decision: "
        f"{csi_phase11_decision_closeout_status['closeout_decision']}"
    )
    print(
        "- Phase 11J RF booth closeout status: "
        f"{csi_phase11_decision_closeout_status['closeout_status']}"
    )
    print("- Phase 11J decision closeout execution permitted: false")
    print("- Phase 11K review trail export: reviewer navigation only, runtime disabled")
    print(
        "- Phase 11K review trail phase range: "
        f"{document_phase11_review_trail_export_status['phase_range']}, "
        "covered phases "
        f"{document_phase11_review_trail_export_status['covered_phase_count']}"
    )
    print(
        "- Phase 11K document final closeout: "
        f"{document_phase11_review_trail_export_status['final_closeout_decision']}/"
        f"{document_phase11_review_trail_export_status['final_closeout_status']}"
    )
    print(
        "- Phase 11K RF booth final closeout: "
        f"{csi_phase11_review_trail_export_status['final_closeout_decision']}/"
        f"{csi_phase11_review_trail_export_status['final_closeout_status']}"
    )
    print(
        "- Phase 11K readiness gap: "
        f"{document_phase11_review_trail_export_status['readiness_gap_summary']}"
    )
    print("- Phase 11K review trail export execution permitted: false")
    print("- Phase 11L runtime authorization gap ledger: metadata only, runtime disabled")
    print(
        "- Phase 11L ledger phase range: "
        f"{document_phase11_runtime_gap_ledger_status['source_phase_range']}, "
        "covered phases "
        f"{document_phase11_runtime_gap_ledger_status['covered_phase_count']}"
    )
    print(
        "- Phase 11L authorization status: "
        f"{document_phase11_runtime_gap_ledger_status['authorization_status']}"
    )
    print(
        "- Phase 11L missing future gates: "
        f"{document_phase11_runtime_gap_ledger_status['missing_future_gate_count']}"
    )
    print(
        "- Phase 11L document unresolved/blocker/stale: "
        f"{document_phase11_runtime_gap_ledger_status['unresolved_review_count']}/"
        f"{document_phase11_runtime_gap_ledger_status['blocker_count']}/"
        f"{document_phase11_runtime_gap_ledger_status['stale_count']}"
    )
    print(
        "- Phase 11L RF booth unresolved/blocker/stale: "
        f"{csi_phase11_runtime_gap_ledger_status['unresolved_review_count']}/"
        f"{csi_phase11_runtime_gap_ledger_status['blocker_count']}/"
        f"{csi_phase11_runtime_gap_ledger_status['stale_count']}"
    )
    print(
        f"- Phase 11L readiness gap: {document_phase11_runtime_gap_ledger_status['readiness_gap']}"
    )
    print("- Phase 11L runtime gap ledger execution permitted: false")
    print("- Phase 11M planning/governance closeout: complete, runtime disabled")
    print(
        "- Phase 11M phase range: "
        f"{phase11_planning_governance_closeout_status['phase_range']}, "
        "covered phases "
        f"{phase11_planning_governance_closeout_status['covered_phase_count']}"
    )
    print(
        f"- Phase 11M final status: {phase11_planning_governance_closeout_status['final_status']}"
    )
    print(
        "- Phase 11M runtime authorization status: "
        f"{phase11_planning_governance_closeout_status['runtime_authorization_status']}"
    )
    print(
        f"- Phase 11M readiness gap: {phase11_planning_governance_closeout_status['readiness_gap']}"
    )
    print(
        "- Phase 11M next phase requirement: "
        f"{phase11_planning_governance_closeout_status['next_phase_requirement']}"
    )
    print("- Phase 11M governance closeout execution permitted: false")
    print("- Phase 12A runtime authorization design charter: design only, runtime disabled")
    print(
        "- Phase 12A source phase range: "
        f"{phase12a_runtime_authorization_charter_status['source_phase_range']}"
    )
    print(
        "- Phase 12A authorization status: "
        f"{phase12a_runtime_authorization_charter_status['authorization_status']}"
    )
    print(
        "- Phase 12A future required gates: "
        f"{phase12a_runtime_authorization_charter_status['future_required_gate_count']}"
    )
    print("- Phase 12A satisfied future gates: 0")
    print("- Phase 12A execution permitted: false")
    print(
        "- Phase 12B runtime authorization record candidate: "
        "record candidate only, runtime disabled"
    )
    print(f"- Phase 12B source phase: {phase12b_record_status['source_phase']}")
    print(f"- Phase 12B authorization status: {phase12b_record_status['authorization_status']}")
    print(f"- Phase 12B decision status: {phase12b_record_status['decision_status']}")
    print(f"- Phase 12B grant status: {phase12b_record_status['grant_status']}")
    print(f"- Phase 12B requested domains: {phase12b_record_status['requested_domain_count']}")
    print(
        "- Phase 12B future reviewer roles: "
        f"{phase12b_record_status['required_future_reviewer_role_count']}"
    )
    print(f"- Phase 12B future gates: {phase12b_record_status['required_future_gate_count']}")
    print("- Phase 12B satisfied future gates: 0")
    print("- Phase 12B execution permitted: false")
    print(
        "- Phase 12C visual supervision capability profile: "
        "capability profile only, runtime disabled"
    )
    print(f"- Phase 12C source phase: {phase12c_profile_status['source_phase']}")
    print(f"- Phase 12C supervision phase: {phase12c_profile_status['supervision_phase']}")
    print(f"- Phase 12C authorization status: {phase12c_profile_status['authorization_status']}")
    print(f"- Phase 12C grant status: {phase12c_profile_status['grant_status']}")
    print(f"- Phase 12C capability labels: {phase12c_profile_status['capability_label_count']}")
    print("- Phase 12C execution permitted: false")
    print(
        "- Phase 12D visual/desktop consent gate requirements: "
        "consent gate requirements only, runtime disabled"
    )
    print(f"- Phase 12D source phase range: {phase12d_consent_gate_status['source_phase_range']}")
    print(f"- Phase 12D consent phase: {phase12d_consent_gate_status['consent_phase']}")
    print(
        f"- Phase 12D authorization status: {phase12d_consent_gate_status['authorization_status']}"
    )
    print(f"- Phase 12D grant status: {phase12d_consent_gate_status['grant_status']}")
    print(
        "- Phase 12D capability categories: "
        f"{phase12d_consent_gate_status['capability_category_count']}"
    )
    print(
        "- Phase 12D future consent gates: "
        f"{phase12d_consent_gate_status['required_future_gate_count']}"
    )
    print("- Phase 12D satisfied consent gates: 0")
    print("- Phase 12D execution permitted: false")
    print(
        "- Phase 12E physiological sensor capability profile: "
        "capability profile only, runtime disabled"
    )
    print(
        "- Phase 12E source phase range: "
        f"{phase12e_physiological_sensor_status['source_phase_range']}"
    )
    print(f"- Phase 12E sensor phase: {phase12e_physiological_sensor_status['sensor_phase']}")
    print(
        "- Phase 12E authorization status: "
        f"{phase12e_physiological_sensor_status['authorization_status']}"
    )
    print(f"- Phase 12E grant status: {phase12e_physiological_sensor_status['grant_status']}")
    print(
        "- Phase 12E sensor capability labels: "
        f"{phase12e_physiological_sensor_status['sensor_capability_label_count']}"
    )
    print(
        "- Phase 12E non-diagnostic boundaries: "
        f"{phase12e_physiological_sensor_status['non_diagnostic_boundary_count']}"
    )
    print(
        "- Phase 12E future sensor gates: "
        f"{phase12e_physiological_sensor_status['required_future_gate_count']}"
    )
    print("- Phase 12E satisfied sensor gates: 0")
    print("- Phase 12E execution permitted: false")
    print("- Phase 12F Secure Drop consumer boundary: boundary profile only, runtime disabled")
    print(
        "- Phase 12F source phase range: "
        f"{phase12f_secure_drop_boundary_status['source_phase_range']}"
    )
    print(f"- Phase 12F consumer phase: {phase12f_secure_drop_boundary_status['consumer_phase']}")
    print(f"- Phase 12F canonical owner: {phase12f_secure_drop_boundary_status['canonical_owner']}")
    print(
        "- Phase 12F authorization status: "
        f"{phase12f_secure_drop_boundary_status['authorization_status']}"
    )
    print(f"- Phase 12F grant status: {phase12f_secure_drop_boundary_status['grant_status']}")
    print(
        "- Phase 12F allowed artifact labels: "
        f"{phase12f_secure_drop_boundary_status['allowed_future_user_selected_artifact_label_count']}"
    )
    print(
        "- Phase 12F prohibited autonomous sources: "
        f"{phase12f_secure_drop_boundary_status['prohibited_future_autonomous_source_count']}"
    )
    print("- Phase 12F Secure Drop send permitted: false")
    print("- Phase 12F Secure Drop receive permitted: false")
    print("- Phase 12F execution permitted: false")
    print(
        "- Phase 12G production-readiness coverage matrix: coverage matrix only, runtime disabled"
    )
    print(
        "- Phase 12G source phase range: "
        f"{phase12g_production_readiness_status['source_phase_range']}"
    )
    print(f"- Phase 12G readiness phase: {phase12g_production_readiness_status['readiness_phase']}")
    print(
        "- Phase 12G authorization status: "
        f"{phase12g_production_readiness_status['authorization_status']}"
    )
    print(f"- Phase 12G grant status: {phase12g_production_readiness_status['grant_status']}")
    print(
        "- Phase 12G production-readiness areas: "
        f"{phase12g_production_readiness_status['production_readiness_area_count']}"
    )
    print(
        "- Phase 12G Somatic direct areas: "
        f"{phase12g_production_readiness_status['somatic_direct_area_count']}"
    )
    print(
        "- Phase 12G Somatic boundary-only areas: "
        f"{phase12g_production_readiness_status['somatic_boundary_only_area_count']}"
    )
    print(
        "- Phase 12G external-owner areas: "
        f"{phase12g_production_readiness_status['external_owner_area_count']}"
    )
    print("- Phase 12G makes Somatic production-ready: false")
    print("- Phase 12G authorizes runtime: false")
    print("- Phase 12G execution permitted: false")
    print(
        "- Phase 12H standalone production-readiness ownership map: "
        "standalone ownership and optional integration metadata only, runtime disabled"
    )
    print(f"- Phase 12H source phase: {phase12h_standalone_ownership_status['source_phase']}")
    print(f"- Phase 12H readiness phase: {phase12h_standalone_ownership_status['readiness_phase']}")
    print(
        "- Phase 12H authorization status: "
        f"{phase12h_standalone_ownership_status['authorization_status']}"
    )
    print(f"- Phase 12H grant status: {phase12h_standalone_ownership_status['grant_status']}")
    print(
        "- Phase 12H standalone ownership entries: "
        f"{phase12h_standalone_ownership_status['standalone_ownership_entry_count']}"
    )
    print(
        "- Phase 12H optional integration peers: "
        f"{phase12h_standalone_ownership_status['optional_integration_peer_count']}"
    )
    print(
        "- Phase 12H Somatic standalone areas: "
        f"{phase12h_standalone_ownership_status['somatic_standalone_area_count']}"
    )
    print("- Phase 12H Somatic standalone ownership retained: true")
    print("- Phase 12H external integrations optional: true")
    print("- Phase 12H other repo integration replaces Somatic standalone path: false")
    print("- Phase 12H marks Somatic production-ready: false")
    print("- Phase 12H cross-repo mutation permitted: false")
    print("- Phase 12H execution permitted: false")
    print(
        "- Phase 12I integrative/herbal/nutrition knowledge capability profile: "
        "knowledge profile only, runtime disabled"
    )
    print(
        "- Phase 12I source phase range: "
        f"{phase12i_integrative_knowledge_status['source_phase_range']}"
    )
    print(
        f"- Phase 12I capability phase: {phase12i_integrative_knowledge_status['capability_phase']}"
    )
    print(
        "- Phase 12I authorization status: "
        f"{phase12i_integrative_knowledge_status['authorization_status']}"
    )
    print(f"- Phase 12I grant status: {phase12i_integrative_knowledge_status['grant_status']}")
    print(
        "- Phase 12I user preference modes: "
        f"{phase12i_integrative_knowledge_status['user_preference_mode_count']}"
    )
    print(
        "- Phase 12I specialist review profiles: "
        f"{phase12i_integrative_knowledge_status['specialist_profile_label_count']}"
    )
    print(
        "- Phase 12I source classes: "
        f"{phase12i_integrative_knowledge_status['source_class_label_count']}"
    )
    print(
        "- Phase 12I required future gates: "
        f"{phase12i_integrative_knowledge_status['required_future_gate_count']}"
    )
    print("- Phase 12I provides medical advice: false")
    print("- Phase 12I suppresses safety warnings: false")
    print("- Phase 12I authorizes runtime: false")
    print("- Phase 12I execution permitted: false")
    print(
        "- Phase 12K external compute/quantum backend capability profile: "
        "capability profile only, runtime disabled"
    )
    print(
        "- Phase 12K source phase range: "
        f"{phase12k_external_compute_quantum_status['source_phase_range']}"
    )
    print(
        "- Phase 12K capability phase: "
        f"{phase12k_external_compute_quantum_status['capability_phase']}"
    )
    print(
        "- Phase 12K authorization status: "
        f"{phase12k_external_compute_quantum_status['authorization_status']}"
    )
    print(f"- Phase 12K grant status: {phase12k_external_compute_quantum_status['grant_status']}")
    print(
        "- Phase 12K credential policy: "
        f"{phase12k_external_compute_quantum_status['credential_policy']}"
    )
    print(
        "- Phase 12K backend options: "
        f"{phase12k_external_compute_quantum_status['backend_option_count']}"
    )
    print(
        "- Phase 12K workload classes: "
        f"{phase12k_external_compute_quantum_status['workload_class_count']}"
    )
    print(
        "- Phase 12K required future gates: "
        f"{phase12k_external_compute_quantum_status['required_future_gate_count']}"
    )
    print("- Phase 12K human approval required before runtime: true")
    print("- Phase 12K cost guard required before runtime: true")
    print("- Phase 12K private health data allowed: false")
    print("- Phase 12K clinical decision support allowed: false")
    print("- Phase 12K diagnosis or treatment allowed: false")
    print("- Phase 12K authorizes runtime: false")
    print("- Phase 12K execution permitted: false")
    print(
        "- Phase 12L fabric interop/A2A audit-boundary capability profile: "
        "capability profile only, runtime disabled"
    )
    print(f"- Phase 12L source phase range: {phase12l_fabric_interop_status['source_phase_range']}")
    print(f"- Phase 12L capability phase: {phase12l_fabric_interop_status['capability_phase']}")
    print(
        "- Phase 12L authorization status: "
        f"{phase12l_fabric_interop_status['authorization_status']}"
    )
    print(f"- Phase 12L grant status: {phase12l_fabric_interop_status['grant_status']}")
    print(
        "- Phase 12L fabric interop status: "
        f"{phase12l_fabric_interop_status['fabric_interop_status']}"
    )
    print(
        "- Phase 12L message codec status: "
        f"{phase12l_fabric_interop_status['message_codec_status']}"
    )
    print(
        "- Phase 12L A2A transport status: "
        f"{phase12l_fabric_interop_status['a2a_transport_status']}"
    )
    print(f"- Phase 12L MCP interop status: {phase12l_fabric_interop_status['mcp_interop_status']}")
    print(f"- Phase 12L Secure Drop status: {phase12l_fabric_interop_status['secure_drop_status']}")
    print(f"- Phase 12L credential policy: {phase12l_fabric_interop_status['credential_policy']}")
    print(
        "- Phase 12L fabric capability labels: "
        f"{phase12l_fabric_interop_status['fabric_capability_label_count']}"
    )
    print(
        "- Phase 12L forbidden/out-of-scope labels: "
        f"{phase12l_fabric_interop_status['forbidden_out_of_scope_label_count']}"
    )
    print(
        "- Phase 12L required future gates: "
        f"{phase12l_fabric_interop_status['required_future_gate_count']}"
    )
    print("- Phase 12L plaintext JSON default is future requirement only: true")
    print("- Phase 12L decode-to-audit is future requirement only: true")
    print("- Phase 12L opaque traffic allowed: false")
    print("- Phase 12L untrusted content executable: false")
    print("- Phase 12L cross-repo mutation allowed: false")
    print("- Phase 12L Secure Drop agent/automation invocation allowed: false")
    print("- Phase 12L authorizes runtime: false")
    print("- Phase 12L execution permitted: false")
    print(
        "- Phase 12M specialized model option registry capability profile: "
        "metadata only, runtime disabled"
    )
    print(
        "- Phase 12M source phase range: "
        f"{phase12m_model_option_registry_status['source_phase_range']}"
    )
    print(
        "- Phase 12M model option profile phase: "
        f"{phase12m_model_option_registry_status['model_option_profile_phase']}"
    )
    print(
        "- Phase 12M authorization status: "
        f"{phase12m_model_option_registry_status['authorization_status']}"
    )
    print(f"- Phase 12M grant status: {phase12m_model_option_registry_status['grant_status']}")
    print(
        "- Phase 12M model option categories: "
        f"{phase12m_model_option_registry_status['model_option_category_count']}"
    )
    print(
        "- Phase 12M candidate labels: "
        f"{phase12m_model_option_registry_status['candidate_label_count']}"
    )
    print(
        "- Phase 12M required future gates: "
        f"{phase12m_model_option_registry_status['required_future_gate_count']}"
    )
    print("- Phase 12M model execution permitted: false")
    print("- Phase 12M provider execution permitted: false")
    print("- Phase 12M training permitted: false")
    print("- Phase 12M fine-tuning permitted: false")
    print("- Phase 12M clinical decision support allowed: false")
    print("- Phase 12M diagnosis or treatment allowed: false")
    print("- Phase 12M private health data allowed: false")
    print("- Phase 12M authorizes runtime: false")
    print("- Phase 12M execution permitted: false")
    print(
        "- Phase 12N workflow orchestration mode registry capability profile: "
        "metadata only, runtime disabled"
    )
    print(
        "- Phase 12N source phase range: "
        f"{phase12n_workflow_mode_registry_status['source_phase_range']}"
    )
    print(
        "- Phase 12N workflow mode profile phase: "
        f"{phase12n_workflow_mode_registry_status['workflow_mode_profile_phase']}"
    )
    print(
        "- Phase 12N authorization status: "
        f"{phase12n_workflow_mode_registry_status['authorization_status']}"
    )
    print(f"- Phase 12N grant status: {phase12n_workflow_mode_registry_status['grant_status']}")
    print(
        "- Phase 12N workflow modes: "
        f"{phase12n_workflow_mode_registry_status['workflow_mode_count']}"
    )
    print(
        "- Phase 12N fusion concepts: "
        f"{phase12n_workflow_mode_registry_status['fusion_concept_count']}"
    )
    print(
        "- Phase 12N scientist-evolution concepts: "
        f"{phase12n_workflow_mode_registry_status['scientist_evolution_concept_count']}"
    )
    print(
        "- Phase 12N required future gates: "
        f"{phase12n_workflow_mode_registry_status['required_future_gate_count']}"
    )
    print("- Phase 12N workflow mode execution permitted: false")
    print("- Phase 12N autonomous experimentation permitted: false")
    print("- Phase 12N code execution permitted: false")
    print("- Phase 12N model routing execution permitted: false")
    print("- Phase 12N clinical decision support allowed: false")
    print("- Phase 12N diagnosis or treatment allowed: false")
    print("- Phase 12N private health data allowed: false")
    print("- Phase 12N authorizes runtime: false")
    print("- Phase 12N execution permitted: false")
    print(
        "- Phase 12O workflow mode safety gate runtime prerequisite matrix: "
        "metadata only, runtime disabled"
    )
    print(f"- Phase 12O source phase: {phase12o_workflow_mode_safety_gate_status['source_phase']}")
    print(f"- Phase 12O matrix phase: {phase12o_workflow_mode_safety_gate_status['matrix_phase']}")
    print(
        "- Phase 12O authorization status: "
        f"{phase12o_workflow_mode_safety_gate_status['authorization_status']}"
    )
    print(f"- Phase 12O grant status: {phase12o_workflow_mode_safety_gate_status['grant_status']}")
    print(
        "- Phase 12O workflow mode prerequisite entries: "
        f"{phase12o_workflow_mode_safety_gate_status['workflow_mode_prerequisite_count']}"
    )
    print(
        "- Phase 12O required future gates: "
        f"{phase12o_workflow_mode_safety_gate_status['required_future_gate_count']}"
    )
    print(
        "- Phase 12O mode gate requirements: "
        f"{phase12o_workflow_mode_safety_gate_status['mode_gate_requirement_count']}"
    )
    print("- Phase 12O runtime prerequisites satisfied: false")
    print("- Phase 12O workflow execution permitted: false")
    print("- Phase 12O workflow mode execution permitted: false")
    print("- Phase 12O model routing execution permitted: false")
    print("- Phase 12O code execution permitted: false")
    print("- Phase 12O experiment execution permitted: false")
    print("- Phase 12O clinical decision support allowed: false")
    print("- Phase 12O private health data allowed: false")
    print("- Phase 12O active grant present: false")
    print("- Phase 12O authorizes runtime: false")
    print("- Phase 12O execution permitted: false")
    print(
        "- Phase 12P workflow mode activation request review packet boundary: "
        "metadata-only, review-packet-boundary-only"
    )
    print(
        "- Phase 12P source phase range: "
        f"{phase12p_workflow_mode_activation_request_status['source_phase_range']}"
    )
    print(
        "- Phase 12P packet phase: "
        f"{phase12p_workflow_mode_activation_request_status['packet_phase']}"
    )
    print(
        "- Phase 12P authorization status: "
        f"{phase12p_workflow_mode_activation_request_status['authorization_status']}"
    )
    print(
        "- Phase 12P grant status: "
        f"{phase12p_workflow_mode_activation_request_status['grant_status']}"
    )
    print(
        "- Phase 12P runtime stage: "
        f"{phase12p_workflow_mode_activation_request_status['runtime_stage']}"
    )
    print("- Phase 12P workflow mode activation not permitted: true")
    print("- Phase 12P all future gates unsatisfied: true")
    print("- Phase 12P execution permitted: false")
    print("- Phase 12P real mode runtime enabled: false")
    print("- Phase 12P production ready: false")
    print(
        "- Phase 12Q workflow mode review decision record: "
        "metadata-only, review-decision-record-only"
    )
    print(
        "- Phase 12Q source phase range: "
        f"{phase12q_workflow_mode_review_decision_status['source_phase_range']}"
    )
    print(
        "- Phase 12Q decision record phase: "
        f"{phase12q_workflow_mode_review_decision_status['decision_record_phase']}"
    )
    print(
        "- Phase 12Q authorization status: "
        f"{phase12q_workflow_mode_review_decision_status['authorization_status']}"
    )
    print(
        f"- Phase 12Q grant status: {phase12q_workflow_mode_review_decision_status['grant_status']}"
    )
    print(
        "- Phase 12Q decision status: "
        f"{phase12q_workflow_mode_review_decision_status['decision_status']}"
    )
    print(
        "- Phase 12Q runtime stage: "
        f"{phase12q_workflow_mode_review_decision_status['runtime_stage']}"
    )
    print("- Phase 12Q workflow mode activation not permitted: true")
    print("- Phase 12Q runtime authorization not granted: true")
    print("- Phase 12Q execution permitted: false")
    print("- Phase 12Q real mode runtime enabled: false")
    print("- Phase 12Q production ready: false")
    print(
        "- Phase 12R workflow mode review audit trail index: "
        "metadata-only, workflow-mode-review-audit-trail-index-only"
    )
    print(
        "- Phase 12R source phase range: "
        f"{phase12r_workflow_mode_review_audit_trail_index_status['source_phase_range']}"
    )
    print(
        "- Phase 12R audit trail index phase: "
        f"{phase12r_workflow_mode_review_audit_trail_index_status['audit_trail_index_phase']}"
    )
    print(
        "- Phase 12R authorization status: "
        f"{phase12r_workflow_mode_review_audit_trail_index_status['authorization_status']}"
    )
    print(
        "- Phase 12R grant status: "
        f"{phase12r_workflow_mode_review_audit_trail_index_status['grant_status']}"
    )
    print(
        "- Phase 12R runtime stage: "
        f"{phase12r_workflow_mode_review_audit_trail_index_status['runtime_stage']}"
    )
    print("- Phase 12R workflow mode activation not permitted: true")
    print("- Phase 12R runtime authorization not granted: true")
    print("- Phase 12R execution permitted: false")
    print("- Phase 12R real mode runtime enabled: false")
    print("- Phase 12R production ready: false")
    print(
        "- Phase 12S workflow mode review chain closeout summary: "
        "metadata-only, workflow-mode-review-chain-closeout-summary-only"
    )
    print(
        "- Phase 12S source phase range: "
        f"{phase12s_workflow_mode_review_chain_closeout_status['source_phase_range']}"
    )
    print(
        "- Phase 12S closeout summary phase: "
        f"{phase12s_workflow_mode_review_chain_closeout_status['closeout_summary_phase']}"
    )
    print(
        "- Phase 12S authorization status: "
        f"{phase12s_workflow_mode_review_chain_closeout_status['authorization_status']}"
    )
    print(
        "- Phase 12S grant status: "
        f"{phase12s_workflow_mode_review_chain_closeout_status['grant_status']}"
    )
    print(
        "- Phase 12S runtime stage: "
        f"{phase12s_workflow_mode_review_chain_closeout_status['runtime_stage']}"
    )
    print("- Phase 12S workflow mode activation not permitted: true")
    print("- Phase 12S runtime authorization not granted: true")
    print("- Phase 12S execution permitted: false")
    print("- Phase 12S real mode runtime enabled: false")
    print("- Phase 12S production ready: false")
    print("- Personal baseline scaffold: placeholder, local-only, fake-backed")
    print("- Personal baseline real health data: disabled")
    print("- Personal baseline profile storage: disabled")
    print("- Personal baseline database/external memory: disabled")
    print("- Personal baseline comparison: deterministic placeholder matching only")
    print("- Personal baseline medical advice/diagnosis/treatment/triage: disabled")
    print(
        "- Personal baseline future storage: explicit local storage consent, "
        "data-locality review, privacy review, and safety review required"
    )
    print("- n-of-1 intervention tags: mock/local/research-only")
    print("- n-of-1 intervention recommendation/prescription/treatment: disabled")
    print("- n-of-1 intervention medication/clinician placeholders: disabled metadata only")
    print("- n-of-1 response evaluation: future planning only, not monitoring")
    print("- n-of-1 intervention reminders/automation/scheduling: disabled")
    print("- n-of-1 follow-up response evaluation: fake-backed/local/research-only")
    print("- n-of-1 response trend labels: fixture-only, no effectiveness claim")
    print("- n-of-1 response monitoring/scheduling/reminders/notifications: disabled")
    print("- n-of-1 Fabric pack plan: planning-only, private-only by default")
    print("- n-of-1 Fabric signing/publishing/transport/install/execution: disabled")
    print(
        "- real sensor runtime: future only after explicit consent, "
        "local-first privacy policy, and safety review"
    )
    _print_spine_status()
    _print_masterplan_status()
    return 0


def _print_spine_status() -> None:
    from somatic.advisory.adapter import AdvisoryModelConfig
    from somatic.consent.scopes import CONSENT_SCOPES
    from somatic.consent.store import load_ledger
    from somatic.safety.core import LANGUAGE_SCOPE, emergency_screen

    ledger = load_ledger()
    print("- Spine consent scopes (default OFF):")
    for scope in CONSENT_SCOPES:
        print(f"  - {scope.id}: default OFF")
    granted = ledger.granted_scopes()
    if granted:
        print("- Spine persisted grants: " + ", ".join(scope.id for scope in granted))
    else:
        print("- Spine persisted grants: none")
    env_config = AdvisoryModelConfig.from_env()
    adapter_state = "configured" if env_config.model_url and env_config.model else "unset"
    print(f"- Spine adapter config: {adapter_state}")
    screen = emergency_screen("Sudden chest pain while resting")
    print(
        "- Spine emergency-screen self-test: "
        f"{'triggered' if screen.triggered else 'failed'} ({LANGUAGE_SCOPE})"
    )


def _print_masterplan_status() -> None:
    from somatic.evidence_bus.records import EVIDENCE_MODALITIES
    from somatic.sensors.roster import list_sensor_lanes

    print("- Master-plan Evidence Bus: sandbox adapters for every modality; hardware closed")
    print(f"- Master-plan modalities: {', '.join(sorted(EVIDENCE_MODALITIES))}")
    print(
        "- Master-plan sensor roster: sandbox live-scan default; "
        "CSI UDP ingest off until live grant"
    )
    print(f"- Master-plan sensor lanes: {len(list_sensor_lanes())}")
    print("- Master-plan science harness: tournament + belief + falsifier; biosecurity refuse+log")
    print("- Master-plan avatar: render-only Scientist/Doctor; TTS and talking-head disabled")
    print("- Master-plan bench: sandbox ripasudil/dAMD scoring; no lab spend")
    print("- Master-plan provenance: content-addressed verify; p2p distribution disabled")
    print("- Master-plan advanced extras: optional; core stays dependency-free")


def _replay(args):
    run_id = args.commit_or_run_id
    manifest_path = Path(args.runs_dir) / run_id / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"Replay manifest found: {run_id}")
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0

    print(f"Replay target recorded for future support: {run_id}")
    print("- local run manifest not found")
    print("- commit replay is scaffolded but not implemented in Phase 1C")
    return 0


def _csi_parse(args):
    from somatic.sensors.csi_formats import (
        CSI_PARSER_CONTRACT_VERSION,
        MAX_CSI_FIXTURE_BYTES,
    )
    from somatic.sensors.csi_parser import build_csi_parser_artifacts

    max_file_size_bytes = (
        args.max_file_size_bytes if args.max_file_size_bytes is not None else MAX_CSI_FIXTURE_BYTES
    )
    report_payload, summary_payload = build_csi_parser_artifacts(
        (args.fixture,),
        repo_root=Path(args.repo_root),
        max_file_size_bytes=max_file_size_bytes,
    )
    payload = {
        "schema_version": 1,
        "contract_version": CSI_PARSER_CONTRACT_VERSION,
        "id": "csi-parse-cli-report",
        "report": report_payload,
        "summary": summary_payload,
        "scope": "local fake/sample fixtures only; sanitized metadata output",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report_payload["status"] in {"parsed", "partial"} else 1


def _sensor_evidence(args):
    if args.sensor_evidence_command == "providers":
        return _sensor_evidence_providers(args)
    if args.sensor_evidence_command == "validate":
        return _sensor_evidence_validate(args)
    if args.sensor_evidence_command == "inspect":
        return _sensor_evidence_inspect(args)
    return 2


def _sensor_evidence_providers(args):
    payload = _sensor_evidence_provider_listing_payload()
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("Sensor evidence providers")
    for provider in payload["providers"]:
        modes = ",".join(provider["fixture_mode_labels"])
        formats = ",".join(provider["supported_fixture_formats"])
        adapter_labels = ",".join(provider.get("adapter_boundary_labels", ()))
        adapter_text = f" adapter_boundary={adapter_labels}" if adapter_labels else ""
        gate_status = provider.get("readiness_gate_status")
        gate_text = f" readiness_gate={gate_status}" if gate_status else ""
        print(
            "- "
            f"{provider['provider_id']}: "
            f"evidence_kind={provider['evidence_kind']} "
            f"contract_version={provider['contract_version']} "
            f"artifact_name={provider['artifact_name']} "
            f"fixture_only={str(provider['offline_fixture_only']).lower()} "
            f"modes={modes} "
            f"formats={formats}"
            f"{adapter_text}"
            f"{gate_text}"
        )
    print("- registry_validation: sanitized metadata only")
    return 0


def _sensor_evidence_validate(args):
    payload = _sensor_evidence_workflow_validation_payload(Path(args.workflow))
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["valid"] else 1

    status = "valid" if payload["valid"] else "invalid"
    print(f"Sensor evidence workflow validation: {status}")
    print(f"- providers: {payload['provider_count']}")
    print(f"- inputs: {payload['input_count']}")
    categories = payload["error_categories"]
    print(f"- categories: {', '.join(categories) if categories else 'none'}")
    print(f"- sanitized: {str(payload['sanitized']).lower()}")
    print(f"- offline_fixture_only: {str(payload['offline_fixture_only']).lower()}")
    print(f"- metadata_only: {str(payload['metadata_only']).lower()}")
    if payload["errors"]:
        print("- errors:")
        for error in payload["errors"]:
            print(f"  - {error}")
    return 0 if payload["valid"] else 1


def _sensor_evidence_inspect(args):
    payload = _sensor_evidence_artifact_inspection_payload(Path(args.artifact))
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["compatible"] else 1

    status = "compatible" if payload["compatible"] else "incompatible"
    print(f"Sensor evidence artifact inspection: {status}")
    print(f"- provider_kind: {payload['provider_kind']}")
    print(f"- evidence_kind: {payload['evidence_kind']}")
    print(f"- artifact_name: {payload['artifact_name']}")
    print(f"- artifact_ref: {payload['artifact_ref']}")
    print(f"- classification: {payload['classification']}")
    print(f"- status: {payload['status']}")
    print(f"- readiness_status: {payload['readiness_status']}")
    print(f"- pack_fingerprint: {payload['pack_fingerprint']}")
    print(f"- count_summary: {payload['count_summary']}")
    if payload["document_adapter_status"]:
        print(f"- document_adapter_status: {payload['document_adapter_status']['status']}")
        print(f"- document_adapter_boundary: {payload['document_adapter_boundary']}")
        print(
            "- adapter_output_validation: "
            f"{payload['adapter_output_validation'].get('classification', 'unknown')}"
        )
    print(f"- sanitized: {str(payload['sanitized']).lower()}")
    if payload["errors"]:
        print("- errors:")
        for error in payload["errors"]:
            print(f"  - {error}")
    return 0 if payload["compatible"] else 1


def _sensor_evidence_provider_listing_payload():
    from somatic.sensors.registry import sensor_evidence_provider_manifest

    return sensor_evidence_provider_manifest()


def _sensor_evidence_workflow_validation_payload(workflow_path):
    from somatic.sensors.registry import validate_sensor_evidence_workflow_config

    try:
        workflow = parse_simple_yaml(workflow_path.read_text(encoding="utf-8"))
    except Exception:
        result = {
            "valid": False,
            "error_count": 1,
            "errors": ["workflow:workflow_config_parse_failed"],
            "error_categories": ["workflow_shape"],
            "provider_count": 0,
            "input_count": 0,
            "sanitized": True,
            "offline_fixture_only": True,
            "metadata_only": True,
        }
    else:
        result = validate_sensor_evidence_workflow_config(workflow).to_dict()

    payload = {"schema_version": 1}
    payload.update(result)
    return payload


def _sensor_evidence_artifact_inspection_payload(artifact_path):
    from somatic.evidence.document_evidence_pack import (
        DOCUMENT_EVIDENCE_KIND,
        DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME,
        DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF,
        DOCUMENT_EVIDENCE_PROVIDER_KIND,
        validate_document_evidence_pack_v1,
    )
    from somatic.sensors.csi_evidence_pack import validate_csi_evidence_pack_v1
    from somatic.sensors.registry import (
        CSI_EVIDENCE_KIND,
        CSI_EVIDENCE_PACK_ARTIFACT_NAME,
        CSI_EVIDENCE_PACK_ARTIFACT_REF,
        CSI_EVIDENCE_PROVIDER_KIND,
    )

    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except Exception:
        return _sensor_evidence_artifact_inspection_result(
            provider_kind=None,
            evidence_kind=None,
            artifact_name=None,
            artifact_ref=None,
            classification="malformed",
            compatible=False,
            valid=False,
            status="rejected",
            readiness_status="rejected-fail-closed",
            pack_id="",
            pack_fingerprint="",
            counts={},
            scores={},
            errors=("artifact:artifact_json_parse_failed",),
        )

    provider_kind = payload.get("provider_kind") if isinstance(payload, dict) else None
    evidence_kind = payload.get("evidence_kind") if isinstance(payload, dict) else None
    artifact_name = None
    artifact_ref = None
    if provider_kind == DOCUMENT_EVIDENCE_PROVIDER_KIND and evidence_kind == DOCUMENT_EVIDENCE_KIND:
        artifact_name = DOCUMENT_EVIDENCE_PACK_ARTIFACT_NAME
        artifact_ref = DOCUMENT_EVIDENCE_PACK_ARTIFACT_REF
        result = validate_document_evidence_pack_v1(payload)
    elif _looks_like_csi_evidence_pack(payload):
        provider_kind = CSI_EVIDENCE_PROVIDER_KIND
        evidence_kind = CSI_EVIDENCE_KIND
        artifact_name = CSI_EVIDENCE_PACK_ARTIFACT_NAME
        artifact_ref = CSI_EVIDENCE_PACK_ARTIFACT_REF
        result = validate_csi_evidence_pack_v1(payload)
    else:
        result = None

    if result is None:
        return _sensor_evidence_artifact_inspection_result(
            provider_kind=None,
            evidence_kind=None,
            artifact_name=artifact_name,
            artifact_ref=artifact_ref,
            classification="unsupported_version",
            compatible=False,
            valid=False,
            status="rejected",
            readiness_status="rejected-fail-closed",
            pack_id="",
            pack_fingerprint="",
            counts={},
            scores={},
            errors=("artifact:unsupported_evidence_pack_kind",),
        )

    counts = payload.get("counts") if isinstance(payload, dict) else {}
    scores = payload.get("scores") if isinstance(payload, dict) else {}
    adapter_status = payload.get("adapter_status") if isinstance(payload, dict) else {}
    adapter_output_validation = (
        payload.get("adapter_output_validation") if isinstance(payload, dict) else {}
    )
    return _sensor_evidence_artifact_inspection_result(
        provider_kind=provider_kind,
        evidence_kind=evidence_kind,
        artifact_name=artifact_name,
        artifact_ref=artifact_ref,
        classification=result.classification,
        compatible=result.compatible,
        valid=result.valid,
        status=result.status,
        readiness_status=result.readiness_status,
        pack_id=payload.get("pack_id"),
        pack_fingerprint=payload.get("pack_fingerprint"),
        counts=counts if isinstance(counts, dict) else {},
        scores=scores if isinstance(scores, dict) else {},
        errors=tuple(result.errors),
        adapter_status=adapter_status if isinstance(adapter_status, dict) else {},
        adapter_output_validation=(
            adapter_output_validation if isinstance(adapter_output_validation, dict) else {}
        ),
    )


def _sensor_evidence_artifact_inspection_result(
    *,
    provider_kind,
    evidence_kind,
    artifact_name,
    artifact_ref,
    classification,
    compatible,
    valid,
    status,
    readiness_status,
    pack_id,
    pack_fingerprint,
    counts,
    scores,
    errors,
    adapter_status=None,
    adapter_output_validation=None,
):
    safe_counts = _sensor_evidence_count_summary(counts)
    safe_scores = _sensor_evidence_score_summary(scores)
    safe_adapter_status = _sensor_evidence_adapter_status_summary(adapter_status)
    safe_adapter_validation = _sensor_evidence_adapter_validation_summary(adapter_output_validation)
    return {
        "schema_version": 1,
        "inspection_contract_version": 1,
        "classification": classification,
        "compatible": bool(compatible),
        "valid": bool(valid),
        "provider_kind": provider_kind or "unknown",
        "evidence_kind": evidence_kind or "unknown",
        "artifact_name": artifact_name or "unknown",
        "artifact_ref": artifact_ref or "",
        "status": status,
        "readiness_status": readiness_status,
        "pack_id": pack_id or "",
        "pack_fingerprint": pack_fingerprint or "",
        "counts": safe_counts,
        "scores": safe_scores,
        "count_summary": _format_sensor_evidence_count_summary(safe_counts),
        "document_adapter_status": safe_adapter_status,
        "document_adapter_boundary": _format_document_adapter_boundary(safe_adapter_status),
        "adapter_output_validation": safe_adapter_validation,
        "error_count": len(errors),
        "errors": list(errors),
        "sanitized": True,
        "metadata_only": True,
        "fixture_only": True,
        "offline_fixture_only": True,
        "summary_output_only": True,
        "artifact_path_echoed": False,
        "fixture_filenames_exported": False,
        "document_bodies_exported": False,
        "provider_bodies_exported": False,
        "parser_bodies_exported": False,
        "adapter_status_exported": bool(safe_adapter_status),
        "network_calls": False,
        "hardware_access": False,
        "packet_capture": False,
        "monitor_mode": False,
        "model_download": False,
        "model_execution": False,
        "runtime_execution": False,
        "real_mode_execution_permitted": False,
    }


def _looks_like_csi_evidence_pack(payload):
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("id") == "csi-sanitized-evidence-pack"
        and payload.get("evidence_pack_contract_version") == 1
        and payload.get("exporter_id") == "somatic-csi-evidence-pack-exporter-v1"
    )


def _sensor_evidence_count_summary(counts):
    allowed = (
        "fixture_count",
        "document_count",
        "parsed_document_count",
        "partial_document_count",
        "rejected_document_count",
        "total_word_count",
        "total_line_count",
        "total_char_count",
        "format_count",
        "row_count",
        "parsed_row_count",
        "partial_row_count",
        "rejected_row_count",
    )
    return {key: _non_negative_int(counts.get(key)) for key in allowed if key in counts}


def _sensor_evidence_score_summary(scores):
    allowed = (
        "score",
        "evidence_quality",
        "replay_integrity",
        "aggregate_evidence_quality",
        "aggregate_replay_integrity",
    )
    return {key: _non_negative_int(scores.get(key)) for key in allowed if key in scores}


def _sensor_evidence_adapter_status_summary(value):
    from somatic.safety.adapter_readiness import real_mode_readiness_gate_summary

    if not isinstance(value, dict):
        return {}
    labels = value.get("capability_labels")
    safe_labels = (
        [label for label in (_safe_public_cli_label(item) for item in labels) if label]
        if isinstance(labels, list)
        else []
    )
    if not safe_labels and not value.get("adapter_kind"):
        return {}
    summary = {
        "adapter_contract_version": _non_negative_int(value.get("adapter_contract_version")),
        "adapter_kind": _safe_public_cli_label(value.get("adapter_kind")),
        "status": _safe_public_cli_label(value.get("status")),
        "capability_labels": safe_labels,
        "metadata_only": bool(value.get("metadata_only")),
        "fixture_only": bool(value.get("fixture_only")),
        "offline": bool(value.get("offline")),
        "fail_closed_output_validation": bool(value.get("fail_closed_output_validation")),
        "network_calls": bool(value.get("network_calls")),
        "document_bodies_exported": bool(value.get("document_bodies_exported")),
        "origin_ids_exported": bool(value.get("origin_ids_exported")),
        "absolute_paths_exported": bool(value.get("absolute_paths_exported")),
        "urls_exported": bool(value.get("urls_exported")),
    }
    gate = real_mode_readiness_gate_summary(value.get("real_mode_readiness_gate"))
    if gate:
        summary["real_mode_readiness_gate"] = gate
        summary["real_mode_readiness_status"] = gate["status"]
        summary["real_mode_execution_permitted"] = False
    phase11 = _phase11_contract_status_cli_summary(value.get("p11a_contract_status"))
    if phase11:
        summary["p11a_contract_status"] = phase11
    phase11_review = _phase11_review_record_status_cli_summary(
        value.get("p11b_review_record_status")
    )
    if phase11_review:
        summary["p11b_review_record_status"] = phase11_review
    phase11_preflight = _phase11_preflight_status_cli_summary(value.get("p11c_preflight_status"))
    if phase11_preflight:
        summary["p11c_preflight_status"] = phase11_preflight
    phase11_lifecycle = _phase11_lifecycle_status_cli_summary(
        value.get("p11d_lifecycle_audit_status")
    )
    if phase11_lifecycle:
        summary["p11d_lifecycle_audit_status"] = phase11_lifecycle
    phase11_audit_index = _phase11_audit_index_status_cli_summary(
        value.get("p11e_audit_index_status")
    )
    if phase11_audit_index:
        summary["p11e_audit_index_status"] = phase11_audit_index
    phase11_audit_handoff = _phase11_audit_handoff_status_cli_summary(
        value.get("p11f_audit_handoff_status")
    )
    if phase11_audit_handoff:
        summary["p11f_audit_handoff_status"] = phase11_audit_handoff
    phase11_handoff_acceptance = _phase11_handoff_acceptance_status_cli_summary(
        value.get("p11g_handoff_acceptance_status")
    )
    if phase11_handoff_acceptance:
        summary["p11g_handoff_acceptance_status"] = phase11_handoff_acceptance
    phase11_acceptance_followup = _phase11_acceptance_followup_status_cli_summary(
        value.get("p11h_acceptance_followup_status")
    )
    if phase11_acceptance_followup:
        summary["p11h_acceptance_followup_status"] = phase11_acceptance_followup
    phase11_followup_queue = _phase11_followup_queue_status_cli_summary(
        value.get("p11i_followup_queue_index_status")
    )
    if phase11_followup_queue:
        summary["p11i_followup_queue_index_status"] = phase11_followup_queue
    phase11_decision_closeout = _phase11_decision_closeout_status_cli_summary(
        value.get("p11j_decision_closeout_status")
    )
    if phase11_decision_closeout:
        summary["p11j_decision_closeout_status"] = phase11_decision_closeout
    phase11_review_trail_export = _phase11_review_trail_export_status_cli_summary(
        value.get("p11k_review_trail_export_status")
    )
    if phase11_review_trail_export:
        summary["p11k_review_trail_export_status"] = phase11_review_trail_export
    phase11_runtime_gap_ledger = _phase11_runtime_gap_ledger_status_cli_summary(
        value.get("p11l_runtime_gap_ledger_status")
    )
    if phase11_runtime_gap_ledger:
        summary["p11l_runtime_gap_ledger_status"] = phase11_runtime_gap_ledger
    phase11_planning_governance_closeout = _phase11_planning_governance_closeout_status_cli_summary(
        value.get("p11m_planning_governance_closeout_status")
    )
    if phase11_planning_governance_closeout:
        summary["p11m_planning_governance_closeout_status"] = phase11_planning_governance_closeout
    return summary


def _phase11_contract_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "contract_spec_version": _non_negative_int(value.get("contract_spec_version")),
        "domain": _safe_public_cli_label(value.get("domain")),
        "status": _safe_public_cli_label(value.get("status")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "readiness_gate_status": _safe_public_cli_label(value.get("readiness_gate_status")),
        "readiness_gate_missing_count": _non_negative_int(
            value.get("readiness_gate_missing_count")
        ),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_review_record_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "review_record_contract_version": _non_negative_int(
            value.get("review_record_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "review_record_status": _safe_public_cli_label(value.get("review_record_status")),
        "reviewed_gate_count": _non_negative_int(value.get("reviewed_gate_count")),
        "missing_gate_count": _non_negative_int(value.get("missing_gate_count")),
        "rejected_gate_count": _non_negative_int(value.get("rejected_gate_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_preflight_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "preflight_packet_contract_version": _non_negative_int(
            value.get("preflight_packet_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "preflight_packet_label": _safe_public_cli_packet_label(
            value.get("preflight_packet_label")
        ),
        "preflight_packet_id": _safe_public_cli_packet_label(value.get("preflight_packet_id")),
        "preflight_packet_fingerprint": _safe_public_cli_hash(
            value.get("preflight_packet_fingerprint")
        ),
        "preflight_status": _safe_public_cli_label(value.get("preflight_status")),
        "reviewed_gate_count": _non_negative_int(value.get("reviewed_gate_count")),
        "missing_gate_count": _non_negative_int(value.get("missing_gate_count")),
        "rejected_gate_count": _non_negative_int(value.get("rejected_gate_count")),
        "blocking_reason_count": _non_negative_int(value.get("blocking_reason_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_lifecycle_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "lifecycle_contract_version": _non_negative_int(value.get("lifecycle_contract_version")),
        "domain": _safe_public_cli_label(value.get("domain")),
        "lifecycle_record_id": _safe_public_cli_packet_label(value.get("lifecycle_record_id")),
        "lifecycle_record_fingerprint": _safe_public_cli_hash(
            value.get("lifecycle_record_fingerprint")
        ),
        "lifecycle_stage": _safe_public_cli_label(value.get("lifecycle_stage")),
        "lifecycle_status": _safe_public_cli_label(value.get("lifecycle_status")),
        "audit_decision": _safe_public_cli_label(value.get("audit_decision")),
        "signoff_verdict": _safe_public_cli_label(value.get("signoff_verdict")),
        "signoff_count": _non_negative_int(value.get("signoff_count")),
        "decision_count": _non_negative_int(value.get("decision_count")),
        "comparison_changed_field_count": _non_negative_int(
            value.get("comparison_changed_field_count")
        ),
        "blocking_reason_count": _non_negative_int(value.get("blocking_reason_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_audit_index_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "audit_index_contract_version": _non_negative_int(
            value.get("audit_index_contract_version")
        ),
        "domain_scope": _safe_public_cli_label(value.get("domain_scope")),
        "index_id": _safe_phase11e_cli_label(value.get("index_id")),
        "index_fingerprint": _safe_public_cli_hash(value.get("index_fingerprint")),
        "status": _safe_public_cli_label(value.get("status")),
        "entry_count": _non_negative_int(value.get("entry_count")),
        "created_count": _non_negative_int(value.get("created_count")),
        "reviewed_count": _non_negative_int(value.get("reviewed_count")),
        "superseded_count": _non_negative_int(value.get("superseded_count")),
        "rejected_count": _non_negative_int(value.get("rejected_count")),
        "archived_count": _non_negative_int(value.get("archived_count")),
        "decision_recorded_count": _non_negative_int(value.get("decision_recorded_count")),
        "blocking_count": _non_negative_int(value.get("blocking_count")),
        "rejection_count": _non_negative_int(value.get("rejection_count")),
        "coverage_summary_count": _non_negative_int(value.get("coverage_summary_count")),
        "supersession_chain_count": _non_negative_int(value.get("supersession_chain_count")),
        "change_control_record_count": _non_negative_int(value.get("change_control_record_count")),
        "export_retention_policy_count": _non_negative_int(
            value.get("export_retention_policy_count")
        ),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_audit_handoff_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "audit_handoff_contract_version": _non_negative_int(
            value.get("audit_handoff_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "handoff_id": _safe_phase11f_cli_label(value.get("handoff_id")),
        "handoff_fingerprint": _safe_public_cli_hash(value.get("handoff_fingerprint")),
        "status": _safe_public_cli_label(value.get("status")),
        "audit_index_label": _safe_phase11e_cli_label(value.get("audit_index_label")),
        "audit_index_fingerprint": _safe_public_cli_hash(value.get("audit_index_fingerprint")),
        "audit_index_entry_count": _non_negative_int(value.get("audit_index_entry_count")),
        "created_count": _non_negative_int(value.get("created_count")),
        "reviewed_count": _non_negative_int(value.get("reviewed_count")),
        "superseded_count": _non_negative_int(value.get("superseded_count")),
        "rejected_count": _non_negative_int(value.get("rejected_count")),
        "archived_count": _non_negative_int(value.get("archived_count")),
        "decision_recorded_count": _non_negative_int(value.get("decision_recorded_count")),
        "coverage_required_gate_count": _non_negative_int(
            value.get("coverage_required_gate_count")
        ),
        "coverage_covered_gate_count": _non_negative_int(value.get("coverage_covered_gate_count")),
        "coverage_missing_gate_count": _non_negative_int(value.get("coverage_missing_gate_count")),
        "blocking_count": _non_negative_int(value.get("blocking_count")),
        "rejection_count": _non_negative_int(value.get("rejection_count")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_handoff_acceptance_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "handoff_acceptance_contract_version": _non_negative_int(
            value.get("handoff_acceptance_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "acceptance_id": _safe_phase11g_cli_label(value.get("acceptance_id")),
        "acceptance_fingerprint": _safe_public_cli_hash(value.get("acceptance_fingerprint")),
        "status": _safe_public_cli_label(value.get("status")),
        "source_handoff_label": _safe_phase11f_cli_label(value.get("source_handoff_label")),
        "source_handoff_hash": _safe_public_cli_hash(value.get("source_handoff_hash")),
        "handoff_fingerprint": _safe_public_cli_hash(value.get("handoff_fingerprint")),
        "accepted_for_planning": bool(value.get("accepted_for_planning")),
        "blocked": bool(value.get("blocked")),
        "stale": bool(value.get("stale")),
        "missing_review_count": _non_negative_int(value.get("missing_review_count")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "rejection_reason_count": _non_negative_int(value.get("rejection_reason_count")),
        "blocking_reason_count": _non_negative_int(value.get("blocking_reason_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_acceptance_followup_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "acceptance_followup_contract_version": _non_negative_int(
            value.get("acceptance_followup_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "followup_id": _safe_phase11h_cli_label(value.get("followup_id")),
        "followup_type": _safe_public_cli_label(value.get("followup_type")),
        "status": _safe_public_cli_label(value.get("status")),
        "source_acceptance_label": _safe_phase11g_cli_label(value.get("source_acceptance_label")),
        "source_acceptance_hash": _safe_public_cli_hash(value.get("source_acceptance_hash")),
        "blocker_disposition_summary": _safe_public_cli_label(
            value.get("blocker_disposition_summary")
        ),
        "reviewer_queue_summary": _safe_public_cli_label(value.get("reviewer_queue_summary")),
        "stale_renewal_summary": _safe_public_cli_label(value.get("stale_renewal_summary")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocking_count": _non_negative_int(value.get("blocking_count")),
        "rejection_count": _non_negative_int(value.get("rejection_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_followup_queue_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "queue_index_contract_version": _non_negative_int(
            value.get("queue_index_contract_version")
        ),
        "domain": _safe_public_cli_label(value.get("domain")),
        "queue_id": _safe_public_cli_label(value.get("queue_id")),
        "queue_fingerprint": _safe_public_cli_hash(value.get("queue_fingerprint")),
        "status": _safe_public_cli_label(value.get("status")),
        "acceptance_status": _safe_public_cli_label(value.get("acceptance_status")),
        "acceptance_id": _safe_public_cli_label(value.get("acceptance_id")),
        "acceptance_fingerprint": _safe_public_cli_hash(value.get("acceptance_fingerprint")),
        "entry_count": _non_negative_int(value.get("entry_count")),
        "open_count": _non_negative_int(value.get("open_count")),
        "blocked_count": _non_negative_int(value.get("blocked_count")),
        "stale_count": _non_negative_int(value.get("stale_count")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocking_count": _non_negative_int(value.get("blocking_count")),
        "archived_count": _non_negative_int(value.get("archived_count")),
        "rejected_count": _non_negative_int(value.get("rejected_count")),
        "resolved_for_planning_count": _non_negative_int(value.get("resolved_for_planning_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_decision_closeout_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    return {
        "closeout_contract_version": _non_negative_int(value.get("closeout_contract_version")),
        "domain": _safe_public_cli_label(value.get("domain")),
        "closeout_id": _safe_phase11j_cli_label(value.get("closeout_id")),
        "source_queue_label": _safe_public_cli_label(value.get("source_queue_label")),
        "source_queue_hash": _safe_public_cli_hash(value.get("source_queue_hash")),
        "closeout_decision": _safe_public_cli_label(value.get("closeout_decision")),
        "closeout_status": _safe_public_cli_label(value.get("closeout_status")),
        "reviewer_disposition_summary": _safe_public_cli_label(
            value.get("reviewer_disposition_summary")
        ),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocker_count": _non_negative_int(value.get("blocker_count")),
        "stale_count": _non_negative_int(value.get("stale_count")),
        "archived_count": _non_negative_int(value.get("archived_count")),
        "rejected_count": _non_negative_int(value.get("rejected_count")),
        "deferred_count": _non_negative_int(value.get("deferred_count")),
        "planning_only": bool(value.get("planning_only")),
        "metadata_only": bool(value.get("metadata_only")),
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_review_trail_export_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    readiness_gap = _safe_public_cli_label(value.get("readiness_gap_summary"))
    if value.get("readiness_gap_summary") == "real-mode-authorization-missing":
        readiness_gap = "real-mode-authorization-missing"
    return {
        "review_trail_export_contract_version": _non_negative_int(
            value.get("review_trail_export_contract_version")
        ),
        "export_id": _safe_phase11k_cli_label(value.get("export_id")),
        "phase_range": _safe_public_cli_label(value.get("phase_range")),
        "covered_phase_count": _non_negative_int(value.get("covered_phase_count")),
        "domain_label": _safe_public_cli_label(value.get("domain_label")),
        "final_closeout_decision": _safe_public_cli_label(value.get("final_closeout_decision")),
        "final_closeout_status": _safe_public_cli_label(value.get("final_closeout_status")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocker_count": _non_negative_int(value.get("blocker_count")),
        "stale_count": _non_negative_int(value.get("stale_count")),
        "readiness_gap_summary": readiness_gap,
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_runtime_gap_ledger_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    readiness_gap = _safe_public_cli_label(value.get("readiness_gap"))
    if value.get("readiness_gap") == "real-mode-authorization-missing":
        readiness_gap = "real-mode-authorization-missing"
    authorization_status = _safe_public_cli_label(value.get("authorization_status"))
    if value.get("authorization_status") == "not-authorized":
        authorization_status = "not-authorized"
    return {
        "runtime_authorization_gap_ledger_contract_version": _non_negative_int(
            value.get("runtime_authorization_gap_ledger_contract_version")
        ),
        "ledger_id": _safe_phase11l_cli_label(value.get("ledger_id")),
        "source_phase_range": _safe_public_cli_label(value.get("source_phase_range")),
        "covered_phase_count": _non_negative_int(value.get("covered_phase_count")),
        "domain_label": _safe_public_cli_label(value.get("domain_label")),
        "authorization_status": authorization_status,
        "readiness_gap": readiness_gap,
        "missing_future_gate_count": _non_negative_int(value.get("missing_future_gate_count")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocker_count": _non_negative_int(value.get("blocker_count")),
        "stale_count": _non_negative_int(value.get("stale_count")),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase11_planning_governance_closeout_status_cli_summary(value):
    if not isinstance(value, dict):
        return {}
    readiness_gap = _safe_public_cli_label(value.get("readiness_gap"))
    if value.get("readiness_gap") == "real-mode-authorization-missing":
        readiness_gap = "real-mode-authorization-missing"
    runtime_authorization_status = _safe_public_cli_label(value.get("runtime_authorization_status"))
    if value.get("runtime_authorization_status") == "not-authorized":
        runtime_authorization_status = "not-authorized"
    return {
        "planning_governance_closeout_contract_version": _non_negative_int(
            value.get("planning_governance_closeout_contract_version")
        ),
        "closeout_index_id": _safe_phase11m_cli_label(value.get("closeout_index_id")),
        "phase_range": _safe_public_cli_label(value.get("phase_range")),
        "covered_phase_count": _non_negative_int(value.get("covered_phase_count")),
        "final_status": _safe_public_cli_label(value.get("final_status")),
        "runtime_authorization_status": runtime_authorization_status,
        "readiness_gap": readiness_gap,
        "next_phase_requirement": _safe_public_cli_label(value.get("next_phase_requirement")),
        "gap_ledger_id": _safe_phase11l_cli_label(value.get("gap_ledger_id")),
        "domain_count": _non_negative_int(value.get("domain_count")),
        "unresolved_review_count": _non_negative_int(value.get("unresolved_review_count")),
        "blocker_count": _non_negative_int(value.get("blocker_count")),
        "stale_count": _non_negative_int(value.get("stale_count")),
        "missing_future_gate_count": _non_negative_int(value.get("missing_future_gate_count")),
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": _safe_public_cli_label(value.get("runtime_stage")),
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _sensor_evidence_adapter_validation_summary(value):
    if not isinstance(value, dict):
        return {}
    if not any(value.get(field) for field in ("classification", "status")):
        return {}
    return {
        "classification": _safe_public_cli_label(value.get("classification")),
        "compatible": bool(value.get("compatible")),
        "valid": bool(value.get("valid")),
        "error_count": _non_negative_int(value.get("error_count")),
        "privacy_violation_count": _non_negative_int(value.get("privacy_violation_count")),
        "status": _safe_public_cli_label(value.get("status")),
        "readiness_status": _safe_public_cli_label(value.get("readiness_status")),
        "sanitized": bool(value.get("sanitized")),
        "metadata_only": bool(value.get("metadata_only")),
        "fixture_only": bool(value.get("fixture_only")),
    }


def _format_document_adapter_boundary(adapter_status):
    labels = adapter_status.get("capability_labels") if adapter_status else None
    if not labels:
        return "none"
    return ",".join(str(label) for label in labels)


def _safe_public_cli_label(value):
    text = str(value or "").strip()
    lowered = text.lower().replace("\\", "/")
    if not text:
        return ""
    if "://" in lowered or lowered.startswith("/") or "source_id" in lowered:
        return ""
    if len(lowered) >= 3 and lowered[1:3] == ":/" and lowered[0].isalpha():
        return ""
    blocked = (
        "fixture://",
        "fixtures/",
        "api_key",
        "access_token",
        "refresh_token",
        "secret_value",
        "authorization",
        "provider_payload",
        "parser_report_body",
        "parser_summary_body",
    )
    if any(fragment in lowered for fragment in blocked):
        return ""
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in text).strip(
        "-"
    )
    return safe[:96]


def _safe_public_cli_packet_label(value):
    label = _safe_public_cli_label(value)
    normalized = label.lower().replace("-", "_").replace(" ", "_")
    blocked = (
        "source_id",
        "source_ids",
        "device_id",
        "device_ids",
        "router_id",
        "router_ids",
        "parser_body",
        "provider_body",
        "model_body",
        "raw_csi",
        "raw_document_text",
    )
    if any(fragment in normalized for fragment in blocked):
        return ""
    return label


def _safe_phase11e_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11e-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11f_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11f-"):
        return ""
    for fragment in (
        "private",
        "source",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11g_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11g-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11h_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11h-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
        "runtime",
        "execution",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11j_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11j-closeout-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
        "runtime",
        "execution",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11k_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11k-export-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
        "runtime",
        "execution",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11l_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11l-ledger-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider",
        "raw",
        "execution-permitted",
        "runtime-enabled",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_phase11m_cli_label(value):
    text = str(value or "").strip().lower()
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    label = "-".join(part for part in safe.split("-") if part)
    if not label.startswith("p11m-closeout-"):
        return ""
    for fragment in (
        "private",
        "source-id",
        "credential",
        "secret",
        "token",
        "device",
        "router",
        "model",
        "parser",
        "provider-body",
        "raw",
        "execution-permitted",
        "runtime-enabled",
    ):
        if fragment in label:
            return ""
    return label[:96]


def _safe_public_cli_hash(value):
    text = str(value or "")
    if len(text) == 64 and all(char in "0123456789abcdef" for char in text):
        return text
    return ""


def _format_sensor_evidence_count_summary(counts):
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _non_negative_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, number)


def _fabric(args):
    if args.fabric_command == "check":
        return _fabric_check(args)
    if args.fabric_command == "payload":
        return _fabric_payload(args)
    if args.fabric_command == "canonicalize":
        return _fabric_canonicalize(args)
    if args.fabric_command == "digest":
        return _fabric_digest(args)
    if args.fabric_command == "check-catalog":
        return _fabric_check_catalog(args)
    if args.fabric_command == "check-shared-fixtures":
        return _fabric_check_shared_fixtures(args)
    if args.fabric_command == "check-keyring-rotation":
        return _fabric_check_keyring_rotation(args)
    if args.fabric_command == "register":
        return _fabric_register(args)
    if args.fabric_command == "send":
        return _fabric_send(args)
    if args.fabric_command == "receive-once":
        return _fabric_receive_once(args)
    return 2


def _fabric_check(args):
    path = Path(args.path)
    try:
        payload = loads_fabric_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Fabric check: invalid {path}")
        print(f"- could not read JSON: {exc}")
        return 1

    keyring_payload = None
    if args.keyring:
        try:
            keyring_path = Path(args.keyring)
            keyring_payload = loads_fabric_json(keyring_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Fabric check: invalid {path.name}")
            print(f"- could not read keyring JSON: {exc}")
            return 1

    if isinstance(payload, dict) and "packs" in payload:
        result = validate_catalog_shape(payload)
        kind = "catalog"
    elif isinstance(payload, dict) and "rootKeys" in payload:
        result = validate_keyring_shape(payload)
        kind = "keyring"
    else:
        result = validate_pack_manifest(
            payload,
            keyring=keyring_payload,
            verify_crypto=keyring_payload is not None,
        )
        kind = "pack"

    if result.valid and keyring_payload is not None and kind == "catalog":
        signature_result = verify_catalog_signature_threshold(payload, keyring_payload)
        if not signature_result.trusted:
            print(f"Fabric check: invalid {path.name}")
            print(f"- kind: {kind}")
            if not CRYPTO_AVAILABLE:
                print("- cryptographic verification unavailable; failing closed")
            print(f"- catalog signature verification failed: {signature_result.reason}")
            return 1

    if result.valid:
        print(f"Fabric check: valid {path.name}")
        print(f"- kind: {kind}")
        print("- scope: local shape/precheck validation only")
        if keyring_payload is not None:
            if kind == "catalog":
                print("- crypto: catalog signature threshold verified")
            elif kind == "pack":
                print("- crypto: publisher threshold verified")
            else:
                print("- crypto: keyring argument not used for keyring validation")
        else:
            print(
                "- crypto: available; pass --keyring for signature verification"
                if CRYPTO_AVAILABLE
                else "- crypto: cryptographic verification unavailable"
            )
        return 0

    print(f"Fabric check: invalid {path.name}")
    print(f"- kind: {kind}")
    if keyring_payload is not None and not CRYPTO_AVAILABLE:
        print("- cryptographic verification unavailable; failing closed")
    for error in result.errors:
        print(f"- {error}")
    return 1


def _fabric_payload(args):
    path = Path(args.path)
    try:
        payload = loads_fabric_json(path.read_text(encoding="utf-8"))
        signing = signing_payload(payload)
    except Exception as exc:
        print(f"Fabric signing payload: invalid {path.name}")
        print(f"- {exc}")
        return 1

    print(f"Fabric signing payload: {path.name}")
    print("- scope: local payload construction only")
    print("- signatures key set to [] before canonicalization")
    print(f"- bytes: {len(signing)}")
    print(f"- sha256:{sha256_hex(signing)}")
    return 0


def _fabric_canonicalize(args):
    path = Path(args.path)
    try:
        payload = loads_fabric_json(path.read_text(encoding="utf-8"))
        _write_stdout_utf8_line(canonical_dumps(payload))
    except Exception as exc:
        print(f"Fabric canonicalize: invalid {path.name}")
        print(f"- {exc}")
        return 1
    return 0


def _fabric_digest(args):
    path = Path(args.path)
    try:
        payload = loads_fabric_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Fabric digest: invalid {path.name}")
        print(f"- {exc}")
        return 1

    print(f"Fabric digest: {path.name}")
    print(f"- canonicalSha256: {sha256_hex(canonical_bytes(payload))}")
    print(f"- manifestDigest: {manifest_digest(payload)}")
    return 0


def _fabric_check_catalog(args):
    catalog_path = Path(args.path)
    keyring_path = Path(args.keyring)
    try:
        catalog = loads_fabric_json(catalog_path.read_text(encoding="utf-8"))
        keyring = loads_fabric_json(keyring_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Fabric catalog check: invalid {catalog_path.name}")
        print(f"- could not read JSON: {exc}")
        return 1

    shape = validate_catalog_shape(catalog)
    if not shape.valid:
        print(f"Fabric catalog check: invalid {catalog_path.name}")
        for error in shape.errors:
            print(f"- {error}")
        return 1

    result = verify_catalog_signature_threshold(catalog, keyring)
    if not result.trusted:
        print(f"Fabric catalog check: invalid {catalog_path.name}")
        if not CRYPTO_AVAILABLE:
            print("- cryptographic verification unavailable; failing closed")
        print(f"- catalog signature verification failed: {result.reason}")
        return 1

    print(f"Fabric catalog check: valid {catalog_path.name}")
    print("- crypto: catalog signature threshold verified")
    return 0


def _fabric_check_shared_fixtures(args):
    root = Path(args.path)
    try:
        fixtures = {
            "pack": loads_fabric_json((root / "shared-pack.json").read_text(encoding="utf-8")),
            "data_pack": loads_fabric_json(
                (root / "shared-data-pack.json").read_text(encoding="utf-8")
            ),
            "keyring": loads_fabric_json(
                (root / "shared-keyring.json").read_text(encoding="utf-8")
            ),
            "catalog": loads_fabric_json(
                (root / "shared-catalog.json").read_text(encoding="utf-8")
            ),
            "expected": loads_fabric_json(
                (root / "shared-expected.json").read_text(encoding="utf-8")
            ),
            "invalid_pack": loads_fabric_json(
                (root / "shared-invalid-signature-pack.json").read_text(encoding="utf-8")
            ),
            "invalid_catalog": loads_fabric_json(
                (root / "shared-invalid-catalog-signature.json").read_text(encoding="utf-8")
            ),
            "invalid_keyring": loads_fabric_json(
                (root / "shared-invalid-keyring-threshold.json").read_text(encoding="utf-8")
            ),
        }
    except Exception as exc:
        print("Fabric shared fixtures: invalid")
        print(f"- could not read shared fixture JSON: {exc}")
        return 1

    errors = _shared_fixture_errors(fixtures)
    if errors:
        print("Fabric shared fixtures: invalid")
        if not CRYPTO_AVAILABLE:
            print("- cryptographic verification unavailable; failing closed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Fabric shared fixtures: valid")
    print("- shared pack verified with shared keyring")
    print("- shared data pack verified with shared keyring")
    print("- shared catalog verified with shared keyring")
    print("- shared keyring root threshold verified")
    print("- invalid fixtures rejected")
    if fixtures["expected"].get("verification", {}).get("locusVerification") == "passed":
        print("- Locus verification recorded for Phase 4G.3")
    else:
        print("- Locus verification deferred to Phase 4G.3")
    return 0


def _shared_fixture_errors(fixtures):
    errors = []
    pack = fixtures["pack"]
    data_pack = fixtures["data_pack"]
    keyring = fixtures["keyring"]
    catalog = fixtures["catalog"]
    expected = fixtures["expected"]

    for name, result in (
        ("shared pack", validate_pack_manifest(pack)),
        ("shared data pack", validate_pack_manifest(data_pack)),
        ("shared keyring", validate_keyring_shape(keyring)),
        ("shared catalog", validate_catalog_shape(catalog)),
    ):
        if not result.valid:
            errors.append(f"{name} shape failed: {'; '.join(result.errors)}")

    expected_digests = expected.get("digests", {})
    digest_checks = {
        "sharedPackCanonicalSha256": sha256_hex(canonical_bytes(pack)),
        "sharedPackSigningPayloadSha256": sha256_hex(signing_payload(pack)),
        "sharedPackManifestDigest": manifest_digest(pack),
        "sharedDataPackCanonicalSha256": sha256_hex(canonical_bytes(data_pack)),
        "sharedDataPackSigningPayloadSha256": sha256_hex(signing_payload(data_pack)),
        "sharedDataPackManifestDigest": manifest_digest(data_pack),
        "sharedKeyringCanonicalSha256": sha256_hex(canonical_bytes(keyring)),
        "sharedKeyringSigningPayloadSha256": sha256_hex(signing_payload(keyring)),
        "sharedCatalogCanonicalSha256": sha256_hex(canonical_bytes(catalog)),
        "sharedCatalogSigningPayloadSha256": sha256_hex(signing_payload(catalog)),
        "sharedCatalogDigest": f"sha256:{sha256_hex(canonical_bytes(catalog))}",
    }
    for field, actual in digest_checks.items():
        if expected_digests.get(field) != actual:
            errors.append(f"{field} mismatch")

    keyring_result = verify_keyring_root_threshold(keyring)
    pack_result = verify_pack_publisher_threshold(pack, keyring)
    data_pack_result = verify_pack_publisher_threshold(data_pack, keyring)
    catalog_result = verify_catalog_signature_threshold(catalog, keyring)
    invalid_pack_result = verify_pack_publisher_threshold(fixtures["invalid_pack"], keyring)
    invalid_catalog_result = verify_catalog_signature_threshold(
        fixtures["invalid_catalog"], keyring
    )
    invalid_keyring_shape = validate_keyring_shape(fixtures["invalid_keyring"])

    if not keyring_result.trusted:
        errors.append(f"shared keyring threshold failed: {keyring_result.reason}")
    if not pack_result.trusted:
        errors.append(f"shared pack signature failed: {pack_result.reason}")
    if not data_pack_result.trusted:
        errors.append(f"shared data pack signature failed: {data_pack_result.reason}")
    if not catalog_result.trusted:
        errors.append(f"shared catalog signature failed: {catalog_result.reason}")
    if invalid_pack_result.trusted:
        errors.append("invalid signature pack was trusted")
    if invalid_catalog_result.trusted:
        errors.append("invalid catalog signature was trusted")
    if invalid_keyring_shape.valid:
        errors.append("invalid keyring threshold shape was accepted")
    return errors


def _write_stdout_utf8_line(text):
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write(text.encode("utf-8") + b"\n")
        sys.stdout.buffer.flush()
        return None
    print(text)


def _fabric_check_keyring_rotation(args):
    old_path = Path(args.old)
    new_path = Path(args.new)
    try:
        old = loads_fabric_json(old_path.read_text(encoding="utf-8"))
        new = loads_fabric_json(new_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("Fabric keyring rotation: invalid")
        print(f"- could not read keyring JSON: {exc}")
        return 1

    result = verify_keyring_replacement(new, old)
    if result.trusted:
        print("Fabric keyring rotation: valid")
        print(f"- required previous-root signatures: {result.required_signatures}")
        print(f"- valid previous-root signatures: {result.valid_signatures}")
        return 0

    print("Fabric keyring rotation: invalid")
    if not CRYPTO_AVAILABLE:
        print("- cryptographic verification unavailable; failing closed")
    print(f"- {result.reason}")
    return 1


def _fabric_register(args):
    from somatic.fabric.federation import FabricFederationClient, FabricFederationError

    try:
        client = FabricFederationClient.from_env()
        result = client.connect()
    except FabricFederationError as exc:
        print("Fabric federation register: failed")
        print(f"- {exc}")
        return 1

    if args.format == "json":
        _write_stdout_utf8_line(
            json.dumps(
                {
                    "status": "registered",
                    "systemId": result["systemId"],
                    "localDid": result["localDid"],
                    "allowlistedSiblingDidCount": len(result["allowlistedSiblingDids"]),
                    "transport": "out-of-process-fabric-transport-d",
                },
                sort_keys=True,
            )
        )
        return 0

    print("Fabric federation register: registered")
    print(f"- system id: {result['systemId']}")
    print(f"- local DID: {result['localDid']}")
    print(f"- allowlisted sibling DIDs: {len(result['allowlistedSiblingDids'])}")
    print("- transport: out-of-process fabric-transport-d")
    print("- secrets: not printed")
    return 0


def _fabric_send(args):
    from somatic.fabric.federation import FabricFederationClient, FabricFederationError

    try:
        client = FabricFederationClient.from_env()
        result = client.send(args.to_did, Path(args.path), secure=args.secure)
    except FabricFederationError as exc:
        print("Fabric federation send: failed")
        print(f"- {exc}")
        return 1
    except OSError as exc:
        print("Fabric federation send: failed")
        print(f"- could not read payload file: {exc}")
        return 1

    if args.format == "json":
        _write_stdout_utf8_line(
            json.dumps(
                {
                    "status": "sent",
                    "toDid": result.to_did,
                    "contentId": result.content_id,
                    "secure": result.secure,
                    "transport": "out-of-process-fabric-transport-d",
                },
                sort_keys=True,
            )
        )
        return 0

    print("Fabric federation send: sent")
    print(f"- to DID: {result.to_did}")
    print(f"- contentId: {result.content_id}")
    print(f"- secure ciphertext flag: {str(result.secure).lower()}")
    print("- transport: out-of-process fabric-transport-d")
    return 0


def _fabric_receive_once(args):
    from somatic.fabric.federation import FabricFederationClient, FabricFederationError

    try:
        client = FabricFederationClient.from_env()
        received = client.receive_once()
    except FabricFederationError as exc:
        print("Fabric federation receive-once: failed")
        print(f"- {exc}")
        return 1

    if args.format == "json":
        _write_stdout_utf8_line(
            json.dumps(
                {
                    "status": "received",
                    "count": len(received),
                    "items": [
                        {
                            "fromDid": item.from_did,
                            "contentId": item.content_id,
                            "bytes": len(item.payload),
                            "secure": item.secure,
                        }
                        for item in received
                    ],
                    "integrity": "contentId-reverified",
                },
                sort_keys=True,
            )
        )
        return 0

    print("Fabric federation receive-once: received")
    print(f"- count: {len(received)}")
    for item in received:
        print(f"- from DID: {item.from_did}")
        print(f"  contentId: {item.content_id}")
        print(f"  bytes: {len(item.payload)}")
        print(f"  secure ciphertext flag: {str(item.secure).lower()}")
    print("- integrity: contentId re-verified before delivery")
    return 0
