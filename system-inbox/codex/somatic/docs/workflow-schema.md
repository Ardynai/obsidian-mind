# Workflow Schema

Somatic workflows are declarative manifests. They describe intent, stages, provider capabilities, evidence requirements, safety boundaries, and output packets without binding to a specific runtime, vendor, model, lab, sensor, storage system, or private harness.

Phase 1A defines the contract only. It does not implement a workflow loader, runtime, scheduler, or provider execution layer.

## Required Top-Level Fields

Every workflow manifest must include:

- `schema_version`: integer contract version. Phase 1A fixtures use `1`.
- `id`: stable lowercase identifier, unique within a catalog.
- `title`: human-readable name.
- `mode`: one supported workflow mode.
- `description`: concise statement of research intent.
- `version`: workflow template version.
- `status`: expected to be `draft`, `active`, `deprecated`, or `fixture`.
- `stages`: ordered declarative workflow stages.
- `inputs`: declared user, dataset, sensor, pack, or file inputs.
- `providers`: provider capability requirements, not concrete vendor bindings.
- `artifacts`: expected intermediate artifacts.
- `safety_profile`: safety classification and gate requirements.
- `evidence_requirements`: evidence records needed for reportable outputs.
- `output_packet`: report or artifact packet produced by the workflow.

## Supported Modes

The `mode` field must be one of:

- `literature-only`
- `hypothesis-tournament`
- `robin-loop`
- `in-silico-screening`
- `n-of-1`
- `wet-lab-manual`
- `sandbox-lab`
- `wifi-csi-observation`
- `hybrid-clinical`
- `fabric-pack-ingest`

`robin-loop` currently means the Phase 3A local sandbox loop: Crow context, Falcon plan, sandbox EvidenceSource acquisition, Finch analysis, StructuredVerdict, report, and next iteration. It remains mock/offline/research-only and does not imply FutureHouse Robin, PaperQA2, scientific-agent-skills, LangGraph, AutoScientists, Fabric, biomodel, sensor, or lab runtime availability.

`in-silico-screening` currently means the Phase 6B fake-backed biomodel planning
workflow. It can emit biomodel request, plan, result, Evidence Bus mapping, and
report artifacts, but it does not execute Boltz, import Boltz, download model
weights or MSAs, call MSA servers, use network/GPU runtime, or produce real
structure or affinity predictions.

`n-of-1` currently means the Phase 7A fake-backed sensor planning workflow with Phase 7B WiFi CSI planning metadata. It
can emit a sensor stream plan, mock observations, feature set, Evidence Bus
mapping, local baseline placeholder, and summary artifacts, but it does not
access hardware, capture CSI/camera/audio/wearable data, perform real
monitoring, or make diagnosis, treatment, clinical, or emergency-triage claims.
The Phase 7B CSI metadata also keeps ESP32, RTL8812AU, routers, adapters,
drivers, monitor mode, packet capture, WiFi probing, raw RF/CSI collection,
raw RF/CSI export, and network calls disabled.

## Stages

Each stage should include:

- `id`: stable stage identifier.
- `kind`: stage class, such as `literature-search`, `hypothesis-generation`, `planning`, `simulation`, `sensor-ingest`, `fabric-verify`, `analysis`, `safety-check`, or `report`.
- `requires`: dependency stage ids.
- `provider_refs`: logical provider references required by the stage.
- `inputs`: logical input ids consumed by the stage.
- `outputs`: artifact ids produced by the stage.
- `safety_gate`: optional gate id that must pass before or after the stage.

Stages must not name private services or require private harness state. Provider selection happens outside the manifest through capability matching.

## Inputs

Input declarations should include:

- `id`
- `kind`: `text`, `file`, `directory`, `dataset`, `pack`, `sensor-stream`, `baseline-graph`, or `configuration`.
- `required`: boolean.
- `sensitivity`: `public`, `internal`, `personal`, `patient`, or `restricted`.
- `description`

Inputs should describe data shape and sensitivity, not runtime storage paths that only work on one machine.

## Providers

Provider requirements should include:

- `ref`: logical name used by stages.
- `class`: provider class from the provider contract.
- `capabilities`: required capability ids.
- `required`: boolean.
- `constraints`: optional version, locality, privacy, or offline requirements.

Provider classes are defined in [provider-contracts.md](provider-contracts.md). Workflows must remain provider-agnostic and portable.

## Artifacts

Artifact declarations should include:

- `id`
- `kind`: `evidence-table`, `hypothesis-set`, `plan`, `simulation-result`, `sensor-dataset`, `model-output`, `safety-decision`, `report-packet`, or `pack-catalog-record`.
- `format`: expected data format, such as `json`, `yaml`, `markdown`, `csv`, `parquet`, or `binary`.
- `retention`: `ephemeral`, `run`, `catalog`, or `user-export`.
- `hash_required`: boolean.

Artifacts that feed reports should be reproducible and hashable.

For `robin-loop`, the fixture may declare Crow context, Falcon plan, raw evidence, Finch analysis, structured verdict, and loop summary artifacts. The runner writes those artifacts as JSON under `artifacts/` while preserving baseline run files.

For `in-silico-screening`, the fixture may declare biomodel request, plan,
result, Evidence Bus record, raw evidence, structured verdict, and summary
artifacts. The runner writes those artifacts as JSON under `artifacts/` while
preserving baseline run files.

For `n-of-1`, the fixture may declare sensor stream plan, sensor observations,
sensor feature set, sensor evidence record, baseline placeholder, and summary
artifacts. The runner writes those artifacts as JSON under `artifacts/` while
preserving baseline run files. Every Phase 7A/7B sensor artifact must be marked
mock/offline/research-only and must keep live capture, hardware access, network
calls, personal data export, real monitoring, diagnosis, treatment, emergency
triage, packet capture, monitor mode, WiFi probing, raw RF/CSI collection, and
raw RF/CSI export disabled.

## Safety Profile

The `safety_profile` should include:

- `risk_class`: `low`, `moderate`, or `high`.
- `domain`: `general-research`, `health-research`, `lab-research`, `sensor-research`, `fabric-ingest`, `research-only-in-silico-planning`, or `mixed`.
- `human_review_required`: boolean.
- `external_actions_allowed`: boolean.
- `real_lab_action_requires_approval`: boolean.
- `clinical_safety_gate_required`: boolean.
- `code_pack_quarantine_required`: boolean.
- `notes`: short boundary notes.

Medical and health workflows must stay within research, decision support, safety-gated reporting, and human review. They must not claim diagnosis, treatment, cure, emergency triage, or replacement of clinicians.

## Evidence Requirements

Evidence requirements should include:

- `min_records`: minimum evidence record count before report generation.
- `accepted_source_types`: source types from [evidence-model.md](evidence-model.md).
- `citation_required`: boolean.
- `provenance_required`: boolean.
- `hash_required`: boolean.
- `limitations_required`: boolean.
- `counterevidence_required`: boolean.

## Output Packet

The `output_packet` should include:

- `kind`: usually `report-packet`, `run-artifact`, or `catalog-record`.
- `schema_ref`: local schema document or future schema id.
- `required_sections`: sections expected in the report or packet.
- `review_state`: expected human review state before publication or use.

See [report-packet.md](report-packet.md) for report structure and [run-artifacts.md](run-artifacts.md) for replayable run outputs.

## Validation Expectations

Future validators should reject manifests when:

- A required top-level field is missing.
- `mode` is not in the supported list.
- Stages reference undeclared providers, inputs, artifacts, or gates.
- Health research workflows omit human review or clinical safety gates.
- Lab workflows allow real-world actions without explicit approval.
- Sensor workflows enable live capture, network calls, personal data export, or
  real monitoring without explicit consent, local-first privacy controls, and
  safety review.
- Fabric code-pack workflows omit quarantine and explicit enablement gates.
