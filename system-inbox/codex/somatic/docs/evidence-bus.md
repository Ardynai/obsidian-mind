# Evidence Bus

The Evidence Bus is the shared contract layer for observations and verdicts across Somatic lanes.

## Phase 1C Interfaces

The initial standard-library interfaces are:

- `EvidenceSource`
- `MeasurementPlan`
- `RawEvidence`
- `StructuredVerdict`

These are lightweight dataclasses. They do not implement storage, indexing, streaming, sensor capture, model execution, or remote transport.

Phase 3A adds `to_dict()` helpers on these dataclasses so the standard-library runner can write deterministic JSON artifacts without adding a schema package.

## Modalities

Supported modality identifiers:

- `sim`
- `wetlab`
- `csi`
- `video`
- `video3d`
- `thermal`
- `audio`
- `wearable`
- `environmental`
- `literature`

## Boundary

The Evidence Bus preserves source identity, modality, hashes, payload references, limitations, and confidence. It must not make clinical claims by itself. Reports and safety gates decide how evidence may be presented.

## Phase 3A Sandbox Source

The first runnable Evidence Bus source is `SandboxEvidenceSource` in `somatic/simulator/sandbox_source.py`. It supports only `literature`, `sim`, and `wetlab` modalities for the Robin sandbox loop.

The source is deterministic and offline. It returns mock `RawEvidence` records with SHA-256 hashes and metadata that clearly marks the output as mock/offline/research-only. The `wetlab` record is a wetlab-shaped fixture only; no real lab action occurs.

See [evidence-bus-sandbox.md](evidence-bus-sandbox.md).

## Phase 5F Robin Stack Mapping

FutureHouse Robin, Aviary, and LDP remain reference-only in Somatic. Their
staged Apache-2.0 sources clarify future attachment points, but the Evidence
Bus remains Somatic-owned:

- Crow-style literature work maps to literature providers and evidence records.
- Falcon-style planning maps to `MeasurementPlan`.
- Finch-style analysis maps to the Finch toolbelt and `StructuredVerdict`.
- Aviary-like environments map to future provider execution envelopes.
- LDP-like rollouts map to a future optional optimization/evolution lane.

No Robin, Aviary, LDP, Edison, OpenAI, Anthropic, LiteLLM, fhlmi, or PaperQA2
real runtime is imported or executed by the Evidence Bus.

## Phase 6A Biomodel Mapping

The Evidence Bus does not add a new biomodel modality in Phase 6A. Biomodel
provider output is represented as simulation-shaped research evidence:

- `EvidenceSource.modality = "sim"`
- `EvidenceSource.metadata.submodality = "biomodel"`
- `RawEvidence` points to local or mock biomodel artifact refs and carries
  runtime/download/MSA/GPU flags.
- `StructuredVerdict.confidence = "not-applicable"` for planning/mock results.

`somatic.providers.biomodel.biomodel_result_to_evidence_record` performs this
mapping for disabled provider scaffolds such as Boltz-2. The mapping is
metadata-only and does not imply model execution, lab validation, clinical
meaning, or scientific efficacy.

## Phase 6B In-Silico Run Artifacts

The `in-silico-screening` mock workflow serializes the Phase 6A biomodel mapping
into run artifacts. It keeps the modality list unchanged and writes:

- `biomodel_raw_evidence.json` with modality `sim` and submodality `biomodel`
- `biomodel_structured_verdict.json` with `confidence: not-applicable`
- `biomodel_evidence_record.json` bundling both records
- `in_silico_summary.json` with disabled runtime/download/MSA/network/GPU flags

The workflow is fake-backed planning only. It produces no real structure,
affinity, lab, clinical, safety, or scientific conclusion.

## Phase 7A Sensor Mapping

The `n-of-1` mock workflow serializes fake-backed sensor planning into run
artifacts. `somatic.providers.sensors` defines sensor-specific planning,
observation, feature-set, evidence-record, and privacy-policy dataclasses, then
maps sandbox output back to Evidence Bus `RawEvidence` and `StructuredVerdict`
records.

The mapping is sandbox-only and deterministic. It does not capture CSI, camera,
audio, wearable, thermal, environmental, BLE, WiFi, or hardware data; it does
not call networks; and it does not produce diagnosis, treatment, emergency
triage, clinical interpretation, or real monitoring.

## Phase 7B WiFi CSI Planning Metadata

Phase 7B keeps the generic Evidence Bus mapping unchanged and adds nested WiFi
CSI metadata to the n-of-1 sensor artifacts. The CSI metadata records capture
plans, feature plans, fake-backed feature names, privacy boundaries, hardware
exclusions, reference inventory, and the final feature-set artifact hash.

It is metadata-only. It does not change `EvidenceSource.modality`, run CSI
capture, access WiFi hardware, use ESP32 or RTL8812AU devices, enter monitor
mode, perform packet capture, probe WiFi devices, collect raw RF/CSI data, call
networks, or make diagnosis, treatment, clinical, monitoring, or emergency
triage claims. RuView is conditional reference-only and must not be copied,
imported, executed, depended on, or treated as a Somatic implementation source.

## Phase 7C Personal Baseline Metadata

Phase 7C does not add a new Evidence Bus modality. The n-of-1 runtime compares
the finalized fake-backed `sensor_feature_set.json` to a local placeholder
baseline graph in `somatic.memory.baseline`, then emits
`personal_profile.json`, `baseline_graph.json`, and
`baseline_comparison.json`.

The baseline comparison is deterministic local metadata only. It uses
`within_baseline`, `outside_baseline`, and `insufficient_data` statuses for
placeholder categories. It loads no real health data, performs no real profile
storage, uses no database or external memory, exports no personal health data,
and makes no diagnosis, treatment, clinical interpretation, monitoring,
emergency-triage, or medical-advice claim.

Future real baseline storage requires explicit local storage consent,
data-locality review, local-first privacy controls, privacy review, safety
review, human review, retention/export controls, and separate opt-in
configuration. Future real sensor mode requires explicit consent,
local-first privacy controls, and safety review.

## Phase 7D N-of-1 Intervention Metadata

Phase 7D does not add a new Evidence Bus modality. It adds mock intervention
metadata derived from existing local n-of-1 artifacts: `intervention_tag.json`,
`intervention_context.json`, `response_evaluation_plan.json`, and
`mock_intervention_ledger.json`.

These artifacts are fake-backed, local-only, research-only, and sandbox-only.
They provide no advice, no medical advice, no recommendation, no prescription,
no treatment recommendation, no medication action, no clinician action, no
effectiveness claim, no real monitoring, no reminders, automation, or
scheduling, no diagnosis, and no emergency triage. Medication placeholder
disabled and clinician review placeholder disabled are disabled metadata only.

## Future Work

- Pydantic schemas under the optional `schemas` extra.
- Local evidence store.
- Cross-run evidence indexing.
- Chain-of-custody event helpers.
- Modality-specific validators.
