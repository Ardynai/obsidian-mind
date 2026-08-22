# Run Artifacts

Somatic runs should produce replayable artifact folders. A run folder records the workflow, inputs, evidence, provider reports, safety decisions, outputs, and next-iteration hints.

Phase 1A defined the layout. Phase 1B adds a minimal local mock runner that writes this layout for fixture workflows without real provider execution.

## Layout

```text
runs/{run_id}/
  manifest.json
  workflow.json
  inputs/
  evidence/
  artifacts/
  safety/
  reports/
  next_iteration.json
```

## `manifest.json`

The run manifest should include:

- `run_id`
- `schema_version`
- `workflow_id`
- `workflow_version`
- `mode`
- `created_at`
- `completed_at`
- `status`
- `providers`
- `input_refs`
- `artifact_refs`
- `evidence_refs`
- `safety_refs`
- `report_refs`
- `hashes`

## `workflow.json`

This file should contain the resolved workflow manifest used for the run. It should preserve provider refs as logical capabilities, not private provider secrets.

## `inputs/`

Inputs should be copied, referenced, or summarized according to sensitivity and retention policy. Sensitive inputs may be represented by metadata and hashes instead of copied content.

## `evidence/`

Evidence records should be stored as JSON records using the evidence model. Each record should include provenance, limitations, confidence, hashes, and chain-of-custody events.

## `artifacts/`

Artifacts include intermediate and final files produced by providers or stages. Each artifact should be listed in `manifest.json` with stable ids, formats, and hashes.

## `safety/`

Safety gate requests and responses should be stored here. A run that produces health-related, lab-facing, sensor, or code-pack outputs should preserve safety decisions even when blocked.

## `reports/`

Report packets and rendered reports should be stored here. Rendered reports should reference the canonical report packet and preserve hashes.

## `next_iteration.json`

This file should describe optional follow-up work:

- Hypotheses to refine.
- Evidence gaps.
- Suggested simulation or literature steps.
- Human review tasks.
- Safety blockers to resolve.

Next-iteration entries must not trigger automatic real-world lab actions.

## Stable IDs and Timestamps

Ids should be stable within a run and should not depend on local absolute paths. Timestamps should use RFC 3339 UTC strings.

## Hashes

Hash fields should use SHA-256 for canonical file or payload digests. Hash scope should be explicit when content is transformed.

## Replayability

A future runner should be able to replay a run when:

- The workflow manifest is present.
- Inputs or their verified substitutes are available.
- Provider versions and mock fixtures are available.
- Pack hashes and licenses are still valid.
- Seeds and parameters are recorded for deterministic stages.

Replay is best effort for non-deterministic providers and real-world observations.

## Phase 1B Mock Runner

The Phase 1B runner writes:

- `manifest.json`
- `workflow.json`
- `inputs/README.md`
- `evidence/evidence.json`
- `artifacts/hypotheses.json`
- `safety/safety-response.json`
- `reports/report.md`
- `next_iteration.json`

These artifacts are generated from local fixtures and mock providers only. They must be marked `mock`, `offline`, and `not_medical_advice`.

## Phase 2 Hypothesis Tournament Additions

The Phase 2 `hypothesis-tournament` fixture preserves every Phase 1B baseline artifact and adds deterministic tournament artifacts under `artifacts/`:

- `candidate_hypotheses.json`: fixed mock candidate pool with evidence refs, assumptions, and limitations.
- `reflection_notes.json`: deterministic mock critique and refinement notes.
- `review_scores.json`: score records for evidence alignment, novelty, feasibility, falsifiability, safety risk, and data requirements.
- `tournament_bracket.json`: seeded deterministic bracket with match winners and shortlist ids.
- `refined_hypotheses.json`: one mock mutation/refinement round for top candidates.
- `ranked_hypotheses.json`: final ranked hypotheses ordered by aggregate score.

For compatibility, `artifacts/hypotheses.json` mirrors `artifacts/ranked_hypotheses.json` in tournament mode.

The rendered report must state that the run is mock/offline, research-only, not medical advice, and not a real scientific conclusion. It must include the workflow mode, candidate count, top-ranked hypotheses, score table, safety summary, limitations, and next-step recommendations.

## Phase 2.1 Pairwise and Elo Additions

Phase 2.1 preserves the Phase 2 artifacts and adds:

- `pairwise_debates.json`: deterministic pairwise matchups over original candidate hypotheses, including pro/con debate notes, dimension scores, dimension winners, aggregate scores, and matchup winners.
- `elo_ratings.json`: deterministic Elo-style ratings derived from the pairwise results. All candidates start at the same base rating.

`ranked_hypotheses.json` and the compatibility mirror `hypotheses.json` now include `aggregate_score`, `elo_rating`, and `elo_rank`. Final ranked hypotheses remain sorted by aggregate score for compatibility with Phase 2.

The report adds aggregate score ranking, Elo ranking, and pairwise debate summary sections.

## Phase 2.5 TeamOrchestrator Additions

Phase 2.5 preserves the Phase 2.1 artifacts and adds deterministic team scaffold artifacts:

- `team_roster.json`: five local mock teams with roles, focus hypotheses, critique goals, evidence requests, risk flags, and decisions.
- `team_critiques.json`: critique records for each team. Critique is marked as completed before evidence-budget planning.
- `shared_blackboard.json`: deterministic shared state event log. The `critique` event appears before the `evidence_budget` event.
- `evidence_budget.json`: mock/offline evidence-point allocation with no external evidence spend allowed.
- `reorganization_log.json`: deterministic no-reorganization, merge, or reassignment decision with a reason.
- `team_orchestrator_summary.json`: scaffold status, focus hypotheses, evidence budget total, and disabled future orchestrator hook.

The rendered tournament report adds team orchestration and evidence budget summary sections.

## Phase 3A Robin Loop Additions

The Phase 3A `robin-loop` fixture preserves every Phase 1B baseline artifact and adds deterministic Robin sandbox artifacts under `artifacts/`:

- `crow_literature_context.json`: mock literature context records created from the workflow goal and evidence requirements.
- `falcon_measurement_plan.json`: local `MeasurementPlan` over `literature`, `sim`, and `wetlab` sandbox sources.
- `raw_evidence.json`: deterministic `RawEvidence` records acquired from `SandboxEvidenceSource`.
- `finch_analysis.json`: mock stats and interpretation over raw evidence.
- `structured_verdict.json`: deterministic `StructuredVerdict` marked mock/offline/research-only.
- `robin_loop_summary.json`: loop shape, counts, verdict id, limitations, and next-iteration hints.

The rendered Robin report must include the mock/offline/research-only boundary, Crow context summary, Falcon measurement plan summary, Finch verdict summary, evidence limitations, safety summary, next-step recommendations, and explicit no-medical-advice/no-real-scientific-conclusion language.

## Phase 5D Finch Toolbelt Additions

Phase 5D preserves the Phase 3A Robin artifacts and adds deterministic Finch
toolbelt artifacts when sandbox raw evidence includes local CSV table refs:

- `finch_toolbelt_summary.json`: capabilities used, table counts, dose-response
  availability, evidence-quality score, and limitations.
- `table_profile.json`: local CSV schema, missing values, numeric column
  detection, and descriptive statistics.
- `dose_response_summary.json`: sorted dose/response points, trend direction,
  baseline-vs-highest-dose delta, and preliminary sandbox interpretation.
- `analysis_provenance.json`: SHA-256 hashes for local table fixtures and JSON
  artifact payloads.

These outputs use only the Python standard library. They do not imply pandas,
scipy, numpy, scanpy, biopython, external APIs, network calls, real lab
validation, medical advice, or real scientific conclusions.

## Phase 6B, 6C, And 6D In-Silico Biomodel Additions

The Phase 6B `in-silico-screening` fixture preserves every Phase 1B baseline
artifact and adds deterministic fake-backed biomodel artifacts under
`artifacts/`. Phase 6C adds readiness and consent artifacts to the same run.
Phase 6D adds provenance and future Fabric `data` pack planning artifacts:

- `biomodel_request.json`: local `BiomodelRequest` with mock target, protein,
  ligand, input refs, constraints, and research-only metadata.
- `biomodel_readiness_report.json`: Phase 6C readiness gate outcome with
  deterministic block reasons and `execution_permitted=false`.
- `biomodel_consent_record.json`: placeholder consent state for future real
  runtime work.
- `biomodel_plan.json`: fake-backed `BiomodelPlan` with the upstream Boltz
  command shape, blocked actions, consent requirements, resource requirements,
  provenance, assumptions, limitations, and readiness metadata.
- `biomodel_result.json`: deterministic `BiomodelResult` metadata with runtime,
  download, MSA, network, GPU flags, and readiness metadata disabled.
- `biomodel_evidence_record.json`: bundled Evidence Bus mapping.
- `biomodel_raw_evidence.json`: simulation-shaped raw evidence pointing at the
  local biomodel result artifact.
- `biomodel_structured_verdict.json`: `StructuredVerdict` with
  `confidence: not-applicable`.
- `biomodel_provenance_bundle.json`: provider/source metadata, assumptions,
  limitations, and local SHA-256 refs for request, readiness, consent, plan,
  result, evidence-record, raw-evidence, and structured-verdict artifacts.
- `biomodel_pack_plan.json`: planning-only recommendation for a future Fabric
  `data` pack candidate of type `dataset` or `document`; it records no code
  pack, executable files, signing, signed pack, catalog publishing, public
  seeding, transport, install, or execution.
- `in_silico_summary.json`: summary of disabled runtime surfaces and future
  real-mode requirements.

The rendered report must state fake-backed planning only, no Boltz execution,
no model weights downloaded, no MSA server call, no GPU/runtime execution, no
real structure or affinity prediction, no medical/lab/scientific conclusion,
Phase 6C biomodel safety gates, Phase 6D biomodel provenance packaging, no
Fabric publishing or transport, no permitted real runtime, and future real mode
requirements.

## Phase 7A Sensor N-of-1 Additions

The Phase 7A `n-of-1` fixture preserves every Phase 1B baseline artifact and
adds deterministic fake-backed sensor artifacts under `artifacts/`:

- `sensor_stream_plan.json`: local-first sandbox stream plan and privacy policy.
- `sensor_observations.json`: fixed mock observations for placeholder features.
- `sensor_feature_set.json`: deterministic feature values for planning only.
- `sensor_evidence_record.json`: Evidence Bus `RawEvidence` and
  `StructuredVerdict` mapping.
- `n_of_1_baseline_placeholder.json`: local baseline placeholder with no real
  baseline collection.
- `n_of_1_summary.json`: disabled runtime surfaces and future real-mode
  requirements.

The rendered report must state fake-backed sensor planning only, no real
hardware access, no CSI/camera/audio/wearable capture, no network calls, no
real monitoring, no diagnosis/treatment/emergency triage, no medical or
clinical claims, research-only/sandbox-only status, and future real sensor mode
requirements for explicit consent, local-first privacy policy, retention/export
controls, and safety review.

## Phase 7B WiFi CSI Planning Additions

Phase 7B adds nested WiFi CSI metadata to the Phase 7A n-of-1 artifacts:

- `sensor_feature_set.json` includes `metadata.csi` with a capture plan,
  feature plan, deterministic CSI placeholder feature set, fake observations,
  privacy boundary, hardware profile, and reference inventory ref.
- `sensor_evidence_record.json` includes CSI Evidence Bus metadata and the
  final `sensor_feature_set.json` SHA-256 hash.
- `n_of_1_summary.json` includes `csi_metadata` with disabled WiFi hardware,
  packet capture, monitor mode, WiFi probing, driver, raw RF/CSI, network, and
  clinical interpretation flags.

CSI fixture artifacts under `fixtures/sensors/csi/` are not generated run
outputs. They are static planning fixtures. Phase 7B does not collect raw
RF/CSI data, access hardware, run capture, call networks, or make clinical
claims.

## Phase 8B/8C/8D/8E/8F WiFi CSI Parser, Replay, Scoring, And Batch Additions

Phase 8B adds two summary-only artifacts to `n-of-1` runs when CSI parser
fixture refs are present. Phase 8D now produces them through the sandbox sensor
provider's fixture replay seam:

- `artifacts/csi_parser_report.json`
- `artifacts/csi_parsed_summary.json`

The parser reads tiny local fake/sample CSV/JSONL fixtures only. Phase 8C keeps
the artifacts summary-only and adds stable contract metadata, structured
sanitized parse errors, repo-relative fixture paths, and deterministic replay
validation. Phase 8D adds provider replay metadata and neutral public fixture
refs/format classes where raw local identifiers would expose signal component
terms. Phase 8E adds an embedded `csi_evidence_scoring` object to these existing
artifacts and copies it into n-of-1 evidence/summary metadata. The score uses
sanitized counts and statuses only: parser status, fixture status counts,
fixture count, frame count, sample count, malformed rows, warning/error counts,
format coverage, and parser contract version. It emits bounded 0-100
`evidence_quality` and `replay_integrity` values with count-based explanations.

The artifacts do not emit raw signal output, source IDs, absolute paths, live
capture, serial, MQTT, UDP, pcap, monitor-mode data, hardware access, network
calls, vital-sign inference, diagnosis, treatment, monitoring, emergency-triage
claims, or medical claims. CSI evidence scoring is replay-integrity metadata
only and is not a signal-quality or clinical interpretation score.

Phase 8F adds no new required artifact path. Tournament runs that configure
local CSI replay groups embed batch readiness metadata in the existing
`artifacts/team_orchestrator_summary.json` under
`csi_evidence_scoring_readiness`. That metadata includes the batch contract
version, group/evaluated/rejected counts, aggregate readiness scores,
scorer/contract IDs, and sanitized per-group status/score summaries. It is not
used for `SCORE_FIELDS`, candidate scoring, Elo, bracket selection, winner
selection, or rankings. The generated `workflow.json` also sanitizes private CSI
batch inputs by replacing fixture refs with synthetic group IDs and ref counts.

Phase 8G adds one sanitized CSI evidence-pack artifact when CSI replay metadata
is present:

- `artifacts/csi_evidence_pack.json`

The evidence pack is deterministic portable JSON with contract version `1`.
It records parser/scorer/batch contract versions, sanitized fixture/group/status
counts, aggregate `evidence_quality` and `replay_integrity`, fail-closed
readiness status, sanitized warning/error counts or categories, and a stable
SHA-256 `pack_fingerprint`. It does not include fixture refs, fixture
filenames, source IDs, absolute paths, unsafe refs, provider payload bodies,
parser report bodies, parser summary bodies, raw CSI arrays, or signal values.

Phase 8I keeps that artifact path stable and adds v1 compatibility checks for
portable readers. The compatibility classifier returns `compatible`,
`incompatible`, `unsupported_version`, or `malformed`; missing required fields
fail closed with sanitized counts, future versions are not coerced into v1, and
generated-from IDs/versions must match v1. Additive unknown fields remain
compatible only when they are simple safe scalar metadata and the full payload
passes the portable privacy scan with a matching deterministic fingerprint.

Phase 9A factors the reusable parts of that CSI pack into
`somatic.sensors.evidence`: contract/version identity, provider/evidence kind,
compatibility classification, deterministic sanitized fingerprinting, readiness
status, privacy boundary flags, sanitized diagnostics/count categories, and
run-relative artifact refs/hashes. CSI is the first implementation and keeps
its v1 public artifact shape, checked-in expected packs, fingerprint scope,
pack id prefix, artifact names, and compatibility behavior.

Phase 9B standardizes how sanitized evidence-pack artifacts are referenced
outside the pack payload. Runs with `artifacts/csi_evidence_pack.json` now add
compact generic `sensor_evidence_artifact_refs` in `manifest.json`, n-of-1
summary/report-packet artifacts, tournament team summaries, and n-of-1 Fabric
pack plans. Each generic ref is run-relative and SHA-256 based, carries the
pack ID/fingerprint and provider/evidence kind when available, and fails closed
for missing, malformed, unsafe, or hash-mismatched artifacts without echoing
raw paths or payloads.

For n-of-1 runs, `n_of_1_report_packet.json` references the evidence pack and
the planning-only `n_of_1_fabric_pack_plan.json` can include it as a local data
file candidate by run-relative path and SHA-256. For tournament runs, the pack
is additive readiness metadata and `team_orchestrator_summary.json` carries only
the pack ref/fingerprint plus the generic artifact ref. Phase 8G/9B do not
alter tournament `SCORE_FIELDS`, candidate scoring, Elo, bracket selection,
winner selection, or rankings.

Phase 9C adds `artifacts/environment_evidence_pack.json` as a second
fixture-only sanitized provider output. It uses the same generic artifact-ref
shape as CSI and is included in run manifests, n-of-1 summaries/report packets,
tournament team summaries, and n-of-1 Fabric pack plans when configured. The
pack contains neutral row/count/status readiness metadata only. Fixture refs,
fixture filenames, row bodies, raw values, source IDs, unsafe refs, absolute
paths, provider payload bodies, parser report bodies, parser summary bodies,
credentials, live capture, hardware access, and network calls are not exported.
The environment pack is additive metadata only and does not alter tournament
rankings, Elo, brackets, winners, or candidate scoring.

Phase 9D adds `somatic.sensors.registry` as the source of truth for configured
fixture-only sensor-evidence provider metadata. Run manifests, n-of-1 packets,
tournament summaries, and Fabric plans continue to reference only the stable
artifact names `csi_evidence_pack` and `environment_evidence_pack` with
run-relative `artifacts/*.json` paths, SHA-256 hashes, pack fingerprints, and
provider/evidence kind. Workflow configs are validated before runtime for known
provider IDs, bounded ref/group counts, fixture-only refs, closed sensor
constraints, and sanitized errors; the emitted `workflow.json` records counts
and provider/evidence identity instead of raw fixture refs.

Phase 9E adds `toy-counter-fixture` as the public extension-template proof.
When explicitly configured by the example workflow, run manifests include
`sensor_evidence_artifact_refs.toy_counter_evidence_pack` with the run-relative
`artifacts/toy_counter_evidence_pack.json` path, SHA-256, provider/evidence
kind, pack ID, and pack fingerprint. The toy provider is examples/tests only
and does not change default CSI or environment artifacts.

## Phase 7C Personal Baseline Graph Additions

Phase 7C adds three deterministic fake-backed baseline artifacts to the
`n-of-1` run folder:

- `personal_profile.json`: local placeholder profile metadata, no real health
  data, no real profile storage, no personal health-data export.
- `baseline_graph.json`: local placeholder baseline graph over
  `respiratory_rate`, `movement_score`, `sleep_state_estimate`,
  `posture_state`, `csi_confidence`, `environmental_context`, and
  `notes_placeholder`.
- `baseline_comparison.json`: local comparison of the finalized
  `sensor_feature_set.json` to the placeholder graph, using only
  `within_baseline`, `outside_baseline`, and `insufficient_data` statuses.

`n_of_1_summary.json` includes a `baseline_comparison_summary` with counts,
status by category, local-only flags, and disabled real-health-data/profile
storage/export surfaces.

The rendered report must state fake-backed local baseline only, no real health
data loaded, no real profile storage, no database or external memory, no
personal health-data export, no medical advice, no diagnosis/treatment/emergency
triage, and future real baseline requirements for explicit local storage
consent, data-locality review, local-first privacy controls, privacy review,
safety review, human review, retention/export controls, and separate opt-in
configuration.

## Phase 7D N-of-1 Intervention Tag Additions

Phase 7D adds four deterministic fake-backed intervention artifacts to the
`n-of-1` run folder:

- `intervention_tag.json`: mock intervention tag summary metadata. It is an
  event label only and no recommendation, no prescription, no treatment
  recommendation, no medication action, no clinician action, and no
  effectiveness claim is generated.
- `intervention_context.json`: artifact refs and hashes for
  `sensor_feature_set.json`, `baseline_comparison.json`,
  `personal_profile.json`, and `baseline_graph.json`.
- `response_evaluation_plan.json`: response evaluation plan summary metadata
  with a future comparison window placeholder, metrics to re-check, and
  baseline categories to compare.
- `mock_intervention_ledger.json`: local placeholder ledger with no real
  intervention performed.

`n_of_1_summary.json` includes `fake_backed_intervention_tags`,
`intervention_summary`, ids and refs for the four intervention artifacts, and
false flags for advice, medical advice, recommendation, prescription, treatment
recommendation, real monitoring, reminders, automation, scheduling,
notifications, and effectiveness claims.

The rendered report must state mock intervention metadata only, response
evaluation is future planning only, medication placeholder disabled, clinician
review placeholder disabled, no recommendation, no prescription, no reminders,
automation, or scheduling, no diagnosis, no emergency triage, and future real
use requirements for explicit consent, human/clinical review, local storage
controls, safety gates, and no emergency-triage substitution.

## Phase 7E N-of-1 Response Evaluation Additions

Phase 7E adds four deterministic fake-backed response evaluation artifacts to
the `n-of-1` run folder:

- `follow_up_observation_window.json`: fake-backed local follow-up window
  metadata. It creates no reminders, automation, notification, scheduling, or
  real monitoring.
- `follow_up_sensor_snapshot.json`: deterministic second placeholder feature
  snapshot. It does not access hardware, sensors, real health data, or networks.
- `response_comparison.json`: mechanical placeholder comparison of the
  follow-up snapshot to the local baseline context, using only
  `toward_baseline`, `away_from_baseline`, `unchanged`, and
  `insufficient_data` fixture trend labels.
- `response_evaluation_summary.json`: aggregate trend summary with no
  effectiveness claim, no recommendation, no prescription, no treatment
  recommendation, no medical advice, and no intervention effectiveness claim.

`n_of_1_summary.json` includes `fake_backed_follow_up_generation`,
`response_evaluation_planning_only`, `no_effectiveness_claim`,
`response_trend_summary`, and refs/hashes for the four Phase 7E artifacts.

The rendered report must state follow-up observation window summary, response
comparison summary, response evaluation summary, fixture trend labels only, no
intervention effectiveness is claimed, no effectiveness claim, no
recommendation, no prescription, no medical advice, no real monitoring, and no
reminders, automation, notification, or scheduling. Future real response
evaluation requires explicit consent, human/clinical review, local storage
controls, privacy/safety gates, real scheduling/monitoring safety review, and
no emergency-triage substitution.

## Phase 7F N-of-1 Report Packet Additions

Phase 7F adds one consolidated fake-backed n-of-1 report packet artifact to the
`n-of-1` run folder:

- `n_of_1_report_packet.json`: a report-packet JSON artifact that references
  `sensor_stream_plan.json`, `sensor_observations.json`,
  `sensor_feature_set.json`, `sensor_evidence_record.json`,
  `n_of_1_baseline_placeholder.json`, `personal_profile.json`,
  `baseline_graph.json`, `baseline_comparison.json`, `intervention_tag.json`,
  `intervention_context.json`, `response_evaluation_plan.json`,
  `mock_intervention_ledger.json`, `follow_up_observation_window.json`,
  `follow_up_sensor_snapshot.json`, `response_comparison.json`,
  `response_evaluation_summary.json`, and `n_of_1_summary.json`.

The packet records SHA-256 hashes for reproducibility/provenance only. It is
fake-backed/local/research-only, not medical advice, not a medical record, and
not a health record. It generates no effectiveness claim or advice, no
recommendation, no prescription, no treatment recommendation, no medical
advice, no diagnosis, no emergency triage, no real monitoring, and no
reminders, automation, notification, or scheduling.

The rendered report must reference `artifacts/n_of_1_report_packet.json` and
include an artifact count/hash summary, loop-stage summary, and strict boundary
summary. Future real use requires consent, privacy review, safety review,
human review, clinical review where applicable, local-first storage controls,
and retention/export controls.

## Phase 7G N-of-1 Fabric Pack Plan Additions

Phase 7G adds one planning-only private Fabric pack-plan artifact to the
`n-of-1` run folder:

- `n_of_1_fabric_pack_plan.json`: a local planning artifact that references
  `n_of_1_report_packet.json`, all report-packet artifact refs, and the
  report packet's SHA-256 hashes. It recommends a future Fabric `data` class
  with `document` as the suggested type and `dataset` as the alternate type.

This artifact is not a Content Fabric `pack.json` manifest. It creates no
publisher, keyring, catalog entry, manifest digest, signatures, transport,
magnet URI, WebSeed, infohash, install target, code-pack permission surface, or
executable file. It uses `file_plans`, not Fabric manifest `files`.

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding,
upload, install, or execution is enabled. The plan is private-only by default
and exports no real personal data, personal health data, baseline data, raw
sensor data, or raw RF/CSI data. Future real packaging requires explicit
consent, redaction, license review, privacy review, safety review, human
review, local-first storage controls, retention/export controls, and separate
publication approval.

## Phase 3B Fabric Conformance Fixtures

Phase 3B adds static Content Fabric conformance fixtures under `fixtures/fabric/conformance/`. They are not generated by the run writer and are not runtime outputs.

The fixtures cover a placeholder signing payload, signed pack, keyring, catalog, expected placeholder digests, and invalid examples for floats, path escape, unsigned code packs, and license-gate failure.

The original conformance fixture signatures and digests are non-cryptographic placeholders. Later crypto fixtures under `fixtures/fabric/crypto/` use deterministic test-only Ed25519 material for local verification. Partial Fabric implementations must not claim conformance.

## Phase 4B Fabric Runtime Foundation

Phase 4B keeps Fabric fixtures outside normal run folders, and `expected-digests.json` records historical scaffold digests for regression only. Phase 4G.1 JCS vectors live under `fixtures/fabric/jcs/`; they are local Somatic vectors and are not shared Locus/Somatic certification vectors. Phase 4G.2 shared fixtures live under `fixtures/fabric/interop/shared/`; they are Somatic-origin self-certified vectors. Phase 4G.3 records Locus verification of that shared fixture set. These fixtures are not runtime outputs.

Use the local CLI precheck against fixture artifacts:

```powershell
python -m somatic fabric check fixtures/fabric/conformance/sample-pack-signed.json
```

The command performs local manifest/keyring/catalog shape validation and prechecks only. With `--keyring`, local crypto fixtures can verify pack publisher thresholds when the optional crypto backend is available. It does not fetch, install, quarantine, enable, seed, serve, or execute code.

## Phase 4E Fabric Fixture Additions

Phase 4E adds Fabric fixtures outside normal run folders:

- `fixtures/fabric/raw-json/`: raw number lexeme acceptance and rejection cases.
- `fixtures/fabric/crypto/rotation/`: keyring replacement continuity vectors.
- `fixtures/fabric/crypto/signed-catalog.json`: signed catalog verification vector.
- `fixtures/fabric/crypto/invalid-catalog-signature.json`: signed catalog rejection vector.
- `fixtures/fabric/interop/somatic-generated-*.json`: Somatic-origin exchange fixtures for future Locus mutual verification.

Useful CLI checks:

```powershell
python -m somatic fabric payload fixtures/fabric/crypto/signed-code-pack.json
python -m somatic fabric check-keyring-rotation fixtures/fabric/crypto/rotation/previous-keyring.json fixtures/fabric/crypto/rotation/valid-rotated-keyring.json
```

These fixtures do not imply full RFC 8785 conformance or Locus-certified interop.

## Phase 4G.2 and 4G.3 Shared Interop Fixture Additions

Phase 4G.2 adds Fabric fixtures outside normal run folders:

- `fixtures/fabric/interop/shared/shared-pack.json`: signed test-only code pack.
- `fixtures/fabric/interop/shared/shared-data-pack.json`: signed test-only data pack.
- `fixtures/fabric/interop/shared/shared-keyring.json`: signed test-only keyring.
- `fixtures/fabric/interop/shared/shared-catalog.json`: signed shared catalog.
- `fixtures/fabric/interop/shared/shared-expected.json`: canonical, signing-payload, manifest, catalog digest, and self-certification metadata.
- `fixtures/fabric/interop/shared/shared-invalid-*.json`: rejection fixtures for bad signatures and under-threshold keyrings.

These fixtures are not run artifacts. Phase 4G.3 certifies the Somatic-origin shared fixture set with Locus, but does not imply full runtime interop. They do not fetch, install, quarantine, enable, seed, serve, or execute code.
