# Adapter Boundaries

Somatic owns the workflow, safety, evidence, run artifact, and provider
lifecycle contracts. External science systems are adapters behind those
contracts, not core runtime owners.

## Boundary Principles

- The basic install stays standard-library and lightweight.
- Advanced integrations activate through explicit extras and configuration.
- Provider metadata never contains raw secrets.
- No provider gets raw health, patient, or private user data unless the workflow is explicitly configured for that provider and the user has consented.
- Real lab actions, code-pack execution, model downloads, and live agent runs require separate explicit enablement.
- Placeholder modules must import only the Python standard library and Somatic-owned modules.

## Literature Providers

Literature providers wrap systems such as PaperQA2 behind
`somatic.providers.literature`.

The Somatic surface is:

- `LiteratureQuery`: query text, corpus references, and metadata.
- `LiteratureDocument`: document metadata and optional evidence references.
- `LiteratureProvider.search`: returns provider-scoped document metadata.
- `LiteratureProvider.extract_evidence`: returns evidence-record drafts.

The adapter must preserve citation/provenance fields and must not own the
workflow loop. A future PaperQA2 adapter may run local or remote search only
after the provider is explicitly configured and its data-locality behavior is
declared.

Phase 5B adds `somatic.providers.paperqa2` as the first disabled PaperQA2
scaffold. It imports without PaperQA2 installed, uses `find_spec` for optional
availability checks, and exposes deterministic fake-backed context for tests.
Real PaperQA2 mode fails closed unless a later phase explicitly implements and
configures it. No user health data should be sent to PaperQA2 or another
external literature provider without explicit configuration and consent.

## Skill And Database Providers

Skill providers wrap systems such as `scientific-agent-skills` behind
`somatic.providers.science_skills`.

The Somatic surface is:

- `SkillLookupRequest`: task, organism, modality, tags, and metadata.
- `ScienceSkillRecord`: static skill metadata, inputs, outputs, and safety notes.
- `ScienceSkillProvider.lookup`: returns relevant skill records without executing tools.
- `ScienceSkillProvider.describe`: returns static method metadata for review.

Lookup is planning only. Tool execution belongs to a later provider operation
with explicit permissions, input validation, and safety gates.

Phase 5C adds `somatic.providers.scientific_agent_skills` as a disabled
metadata-only scaffold for the staged MIT-licensed
`K-Dense-AI/scientific-agent-skills` source. It returns deterministic fake
skill and database connector metadata for tests. It does not execute skills,
import external packages, install dependencies, call public databases, or send
health/clinical data outside Somatic. Future real adapters must require
explicit configuration and consent before any connector is used.

## Robin-Style Planner And Analyzer Providers

Robin-style providers wrap planner/analyzer behavior behind Somatic Evidence
Bus artifacts, not behind a foreign orchestration loop.

The Somatic surface remains:

- Crow-like literature context as local artifact metadata.
- Falcon-like measurement plans through `EvidenceSource` and `MeasurementPlan`.
- Raw evidence through `RawEvidence`.
- Finch-like analysis through `StructuredVerdict`.

Future Robin adapters must map into this shape. They must not bypass Somatic run
artifacts, safety summaries, or no-medical-advice/report language.

Phase 5F adds `somatic.providers.robin` as a disabled reference-only scaffold
for FutureHouse Robin/Aviary/LDP mapping. The staged sources are Apache-2.0,
but Somatic does not import, vendor, execute, or depend on them. Robin's
Edison/OpenAI/Anthropic/fhlmi dependencies are explicitly outside Somatic core.
Aviary-like environments may inform provider execution envelopes, and LDP-like
rollouts may inform a future optional optimization lane, but both stay
metadata-only until explicitly enabled in a later phase.

## Team-Orchestration Providers

Team orchestration providers wrap AutoScientists-style concepts behind
`somatic.providers.team_orchestration`.

The Somatic surface is:

- `TeamOrchestrationRequest`: hypotheses, evidence refs, roles, and safety profile.
- `TeamMemberSpec`: role and responsibility metadata.
- `TeamOrchestrationPlan`: reviewable critique steps and evidence budget.
- `TeamOrchestrationProvider.plan`: returns a plan without starting live agents.
- `TeamOrchestrationProvider.summarize`: returns artifact-ready metadata.

Critique should precede evidence-budget planning. Live agents, tool execution,
cloud scorers, and external evidence spend stay disabled until a later explicit
phase enables them.

Phase 5E adds `AutoScientistsTeamOrchestrationProvider` as a disabled
reference-only scaffold. It is fake-backed, standard-library only, and fails
closed when live runtime execution is requested. The staged AutoScientists
source at `C:\AI\external-sources\somatic\AutoScientists` has no license file,
so Somatic uses only conceptual mapping and does not copy, import, vendor, or
execute AutoScientists code.

## Biomodel Providers

Biomodel providers wrap systems such as Boltz-2 behind
`somatic.providers.biomodel`.

The Somatic surface is:

- `BiomodelRequest`: objective, target refs, input artifact refs, constraints, and metadata.
- `BiomodelPlan`: describes data, model, weights, compute, license, consent, provenance, and safety requirements before execution.
- `BiomodelProvider.plan`: produces a `BiomodelPlan` before any execution, download, MSA call, or data release.
- `BiomodelProvider.run`: reserved for future explicitly configured execution; current concrete scaffolds are fake-backed or fail closed.
- `BiomodelResult`: result status, artifact refs, evidence refs, assumptions, and limitations.
- `BiomodelEvidenceRecord`: maps result metadata to `RawEvidence` and `StructuredVerdict`.

Future biomodel adapters must keep model downloads, GPU execution, cloud calls,
and private data release off by default. Every result needs assumptions,
provenance, and limitations.

Phase 6A adds `somatic.providers.boltz` as a disabled Boltz-2 scaffold for the
MIT-licensed staged `jwohlwend/boltz` source. It imports without Boltz
installed, uses `find_spec` for optional availability detection, returns
deterministic fake-backed plan/result metadata, and fails closed for real mode.
It does not run `boltz predict`, download checkpoints or molecule data, call an
MSA server, use GPU runtime, import Boltz, or emit real structures/affinity.
Biomodel result metadata maps into Evidence Bus `RawEvidence` using modality
`sim` with metadata `submodality: biomodel`, plus a `StructuredVerdict` that
preserves the research-only/no-conclusion limitation.

## Sensor Providers

Sensor providers wrap CSI, video, video3d, thermal, audio, wearable, and
environmental observations behind `somatic.providers.sensors`.

The Somatic surface is:

- `SensorPrivacyPolicy`: local-first retention, export, consent, and review metadata.
- `SensorStreamPlan`: planned modalities, features, baseline ref, and blocked runtime actions.
- `SensorObservation`: deterministic observation metadata.
- `SensorFeatureSet`: derived or placeholder feature metadata.
- `SensorEvidenceRecord`: Evidence Bus `RawEvidence` and `StructuredVerdict` mapping.
- `SensorProvider`: protocol for privacy policy, planning, observations, features, and evidence records.

Phase 7A adds `somatic.sensors.sandbox.SandboxSensorProvider` as a fake-backed
provider for `n-of-1` planning. It returns fixed placeholder features and fails
closed by omission: there is no real-mode implementation, no sensor package
import, no hardware access, no network access, and no background monitoring.
Future real sensor adapters must require explicit user consent, local-first
privacy policy, retention/export controls, privacy review, safety review, human
review, and separate opt-in configuration. They must not send camera, mic, CSI,
wearable, thermal, environmental, or baseline data off-machine without explicit
configuration and consent. No sensor adapter may make diagnosis, treatment,
emergency-triage, clinical, or real-monitoring claims from sandbox artifacts.

## Shared Real-Mode Readiness Gate

Phase 10H adds `somatic.safety.adapter_readiness` as a shared readiness gate
for future real-mode adapters. The gate is descriptive only: it records which
review gates are missing, reports why the provider remains fixture or
reference-only, and keeps execution disabled.

The required gate IDs are:

- `consent`
- `license-review`
- `privacy-review`
- `hardware-review`
- `model-artifact-review`
- `dependency-review`
- `network-policy-review`

Mode vocabulary:

- Fixture mode: deterministic checked-in or fake-backed local inputs only.
- Reference-only mode: external projects or methods may be tracked as planning
  references, but are not copied, imported, run, or depended on.
- Metadata-only adapter mode: a provider boundary may emit sanitized counts,
  statuses, labels, and readiness metadata, but no source bodies or runtime
  payloads.
- Future real mode: a separate, not-implemented mode that remains unavailable
  until every shared gate is explicitly satisfied and a later phase adds an
  opt-in runtime. Phase 10H does not add that runtime.

Phase 11A adds `somatic.safety.phase11_contracts` on top of this gate. The
Phase 11A layer is contract/spec planning only: it records the future document
and RF booth review requirements while keeping `runtime_stage` as
`not-implemented` and execution disabled.

Phase 11B adds review-record fixtures and fail-closed validators for those
requirements. The records can prove planning reviews are complete or incomplete,
but they still cannot permit runtime execution.

Phase 11C adds sanitized preflight dossier builders and validators over the
Phase 11A specs and Phase 11B records. The dossiers can summarize planning
status, fingerprints, and rejection reasons, but they still cannot permit
runtime execution.

Phase 11D adds lifecycle audit records, deterministic dossier comparisons,
reviewer signoff metadata, and explicit audit decisions around those preflight
dossiers. The audit records can document planning review state, but they still
cannot permit runtime execution.

Phase 11E adds deterministic audit indexes, change-control records,
supersession chains, reviewer-scope coverage summaries, and local
export/retention policy metadata around those lifecycle audit records. The
audit-index records can document planning change control, but they still
cannot permit runtime execution.

Phase 11F adds compact audit handoff records over those audit-index records.
The handoffs communicate sanitized status and counts for review handoff, but
they still cannot permit runtime execution.

Phase 11G adds compact acceptance/check records over those audit handoffs. An
accepted handoff is accepted for planning review only; it still cannot permit
runtime execution.

Phase 11H adds compact follow-up/remediation queues over those acceptance
records. Resolved-for-planning follow-ups summarize planning disposition only;
they still cannot permit runtime execution.

Phase 11I adds compact queue indexes and acceptance checks over those
follow-up/remediation records. Accepted queues are reviewer-navigation metadata
only; they still cannot permit runtime execution.

Phase 11J adds compact reviewer decision-closeout records over those queue
indexes. Closed-for-planning closeouts are planning metadata only; they still
cannot permit runtime execution.

Phase 11K adds a compact review-trail export over the Phase 11A through 11J
planning trail. Exported review trails are reviewer-navigation metadata only;
they still cannot permit runtime execution.

Phase 11L adds a compact runtime-authorization gap ledger over the Phase 11A
through 11K planning trail. Ledgered gaps are reviewer-navigation metadata only;
they document missing future prerequisites and still cannot permit runtime
execution.

Phase 11M adds the final compact planning/governance closeout index over the
Phase 11A through 11L planning trail. Governance-complete status is
reviewer-navigation metadata only; it declares Phase 11 complete as a
pre-runtime planning phase and still cannot permit runtime execution.

## WiFi CSI Source Adapters

WiFi CSI source adapters sit ahead of CSI planning metadata and portable CSI
evidence packs. Phase 10G adds `somatic.sensors.csi_adapter` as a strict
metadata-only boundary for RuView reassessment metadata and the future
booth-first profile.

The current adapter boundary is:

- Fixture-backed, offline, reference-only, and metadata-only.
- No hardware access, packet capture, monitor mode, WiFi probing, ESP32
  flashing, router/AP control, MQTT/UDP listener, or smart-home bridge.
- No model download, model execution, vitals inference, diagnosis, treatment,
  emergency triage, clinical interpretation, or raw-signal export.
- RuView is conditional reference-only: do not copy, vendor, import, execute, or
  depend on it.
- The booth-first profile is future architecture metadata for one intended
  subject in a small controlled booth with fixed AP plus receiver-node planning
  metadata, ESP32-S3 preferred radios, and an empty-booth baseline concept.
- Invalid or unsafe adapter output fails closed to rejected sanitized metadata
  before CSI planning summaries consume it.
- The Phase 10H shared real-mode readiness gate is present and blocked by
  default; execution remains disabled even when reviewing the gate contract.
- Phase 11A adds an RF booth contract/spec checklist for topology metadata,
  consent/privacy, hardware review, model artifact review, and network policy
  review. It does not add capture, hardware, RuView, model, or network runtime.
- Phase 11B adds RF booth review-record fixtures and validators. Completed
  records remain planning evidence only and keep execution disabled.
- Phase 11C adds RF booth preflight dossiers with per-gate status,
  fingerprints, and rejection reasons. Completed dossiers remain planning
  evidence only and keep execution disabled.
- Phase 11D adds RF booth lifecycle audit records and decisions. No-blocker
  signoffs remain planning evidence only and keep execution disabled.
- Phase 11E adds RF booth audit-index and change-control summaries. Completed
  indexes remain planning evidence only and keep execution disabled.
- Phase 11F adds RF booth compact audit handoff summaries. Completed handoffs
  remain reporting evidence only and keep execution disabled.
- Phase 11G adds RF booth handoff acceptance checks. Accepted handoffs remain
  planning-review evidence only and keep execution disabled.
- Phase 11H adds RF booth follow-up/remediation queues. Resolved follow-ups
  remain planning evidence only and keep execution disabled.
- Phase 11I adds RF booth follow-up queue indexes. Accepted queues remain
  reviewer-navigation evidence only and keep execution disabled.
- Phase 11J adds RF booth decision closeouts. Closed-for-planning closeouts
  remain planning-decision metadata only and keep execution disabled.
- Phase 11K adds RF booth review-trail export metadata across Phase 11A through
  11J. Exported trails remain reviewer-navigation metadata only and keep
  execution disabled.
- Phase 11L adds RF booth runtime gap ledger metadata across Phase 11A through
  11K. Ledgered gaps remain reviewer-navigation metadata only and keep
  execution disabled.
- Phase 11M adds RF booth planning/governance closeout metadata across Phase
  11A through 11L. Governance-complete status remains reviewer-navigation
  metadata only and keeps execution disabled.

Future real CSI source adapters must stay behind this boundary until a separate
phase adds explicit consent, local retention controls, hardware review, privacy
review, safety review, dependency gating, and reproducibility gates.

## Document Evidence Adapters

Document evidence adapters sit in front of sanitized document evidence packs.
Phase 10F adds `somatic.evidence.document_adapter` as the first strict
metadata-only adapter contract, with `document-fixture` as the first
implementation.

The current adapter boundary is:

- Fixture-only and offline.
- No file crawling, PDF parsing, real ingestion, or network access.
- No document body export, origin identifier export, absolute path export, URL
  export, provider body export, or parser body export.
- Adapter output must validate as bounded count/status metadata before
  evidence-pack construction.
- Invalid or unknown adapter output fails closed to rejected sanitized metadata.
- The Phase 10H shared real-mode readiness gate is present and blocked by
  default; execution remains disabled even when reviewing the gate contract.
- Phase 11A adds document contract/spec requirements for metadata-only staging,
  parser boundary, artifact privacy, and license/source review. It does not add
  crawling, PDF parsing, ingestion, parser execution, or network behavior.
- Phase 11B adds document review-record fixtures and validators. Completed
  records remain planning evidence only and keep execution disabled.
- Phase 11C adds document preflight dossiers with per-gate status,
  fingerprints, and rejection reasons. Completed dossiers remain planning
  evidence only and keep execution disabled.
- Phase 11D adds document lifecycle audit records and decisions. No-blocker
  signoffs remain planning evidence only and keep execution disabled.
- Phase 11E adds document audit-index and change-control summaries. Completed
  indexes remain planning evidence only and keep execution disabled.
- Phase 11F adds document compact audit handoff summaries. Completed handoffs
  remain reporting evidence only and keep execution disabled.
- Phase 11G adds document handoff acceptance checks. Accepted handoffs remain
  planning-review evidence only and keep execution disabled.
- Phase 11H adds document follow-up/remediation queues. Resolved follow-ups
  remain planning evidence only and keep execution disabled.
- Phase 11I adds document follow-up queue indexes. Accepted queues remain
  reviewer-navigation evidence only and keep execution disabled.
- Phase 11J adds document decision closeouts. Closed-for-planning closeouts
  remain planning-decision metadata only and keep execution disabled.
- Phase 11K adds document review-trail export metadata across Phase 11A through
  11J. Exported trails remain reviewer-navigation metadata only and keep
  execution disabled.
- Phase 11L adds document runtime gap ledger metadata across Phase 11A through
  11K. Ledgered gaps remain reviewer-navigation metadata only and keep
  execution disabled.
- Phase 11M adds document planning/governance closeout metadata across Phase
  11A through 11L. Governance-complete status remains reviewer-navigation
  metadata only and keeps execution disabled.

Future real document adapters must stay behind this boundary until a separate
phase adds explicit ingestion consent, local retention controls, parser review,
privacy review, and dependency gating.

## Benchmark Providers

Benchmark providers are future adapter surfaces for local regression,
capability, and scientific quality checks.

The safe first surface is:

- Run only against local fixtures and saved run artifacts.
- Emit benchmark reports as Somatic artifacts.
- Avoid external leaderboards, telemetry, or cloud evaluators by default.
- Declare dataset licenses, metric assumptions, and reproducibility limits.

## Activation Path

1. Add disabled provider metadata and interface tests.
2. Inspect a local clone read-only and document entrypoints, dependencies, and licenses.
3. Add an optional extra or install note.
4. Add adapter code that imports external packages only inside the optional adapter module.
5. Add local fixture tests and no-network tests.
6. Add safety review, consent, and secret-boundary checks.
7. Enable runtime behavior only in a later phase after every shared readiness
   gate is satisfied, a separate opt-in runtime contract exists, and the
   workflow explicitly selects that runtime.
