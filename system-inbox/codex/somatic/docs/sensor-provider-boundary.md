# Sensor Provider Boundary

Phase 7A adds Somatic-owned sensor provider contracts and a deterministic sandbox provider. Phase 7B adds a WiFi CSI planning scaffold. Phase 8A stages WiFi CSI reference sources for read-only source review only. Phase 8D adds fixture-backed CSI replay through the sandbox provider without enabling capture. Phase 8F batches configured CSI replay groups through that same sandbox provider and emits tournament readiness metadata only. Phase 8G exports sanitized CSI evidence packs over parser/replay/scoring/batch metadata. Phase 9A adds a generic sanitized sensor-evidence contract foundation, with CSI as the first concrete implementation. Phase 9B adds generic sanitized evidence artifact refs for run reports and Fabric planning. Phase 9C adds a second neutral environment fixture evidence provider as a generic-contract proof, with sanitized row/count/status metadata only. Phase 9D adds a metadata-only provider registry and workflow config validation for configured fixture-only evidence providers. Phase 9E adds a public extension template and a tiny toy counter provider proof through the same registry path. Phase 9F exposes registry discovery and workflow validation through sanitized CLI preflight commands without changing runtime evidence behavior. Phase 9G adds a deterministic sanitized provider manifest/snapshot contract for registry drift checks and machine-readable provider discovery. Phase 9H adds release-summary documentation and a machine-readable subsystem summary without adding runtime, provider, or sensor behavior. Phase 10G adds the WiFi CSI source-adapter boundary, Phase 10H adds the shared real-mode readiness gate, Phase 10I adds shared invariant coverage, and Phase 10J records the checkpoint without enabling live sensor behavior. Phase 11E adds local audit-index/change-control summaries over planning lifecycle records, Phase 11F adds compact audit handoff summaries over those indexes, Phase 11G adds compact handoff acceptance checks over those handoffs, Phase 11H adds compact follow-up/remediation queues over acceptance records, Phase 11I adds compact follow-up queue indexes over those queues, Phase 11J adds compact decision closeouts over those indexes, Phase 11K adds a compact review-trail export over Phase 11A through 11J, Phase 11L adds a compact runtime gap ledger over Phase 11A through 11K, and Phase 11M adds the final planning/governance closeout index over Phase 11A through 11L, without enabling live sensor behavior. Phase 7C consumes sandbox feature artifacts through the memory lane for fake-backed local baseline comparison. The boundary is standard-library only and does not import sensor, camera, audio, BLE, WiFi, wearable, thermal, DSP, packet-capture, driver, database, external-memory, or network packages.

## Scope

- `somatic.providers.sensors` defines `SensorProvider`, `SensorStreamPlan`, `SensorObservation`, `SensorFeatureSet`, `SensorEvidenceRecord`, and `SensorPrivacyPolicy`.
- `somatic.sensors.sandbox` emits fixed mock observations and features for n-of-1 planning and replays local CSI fixtures through the parser contract.
- `somatic.sensors.csi` emits deterministic WiFi CSI planning metadata only.
- `somatic.sensors.csi_adapter` validates conditional RuView reference metadata and the booth-first planning profile before CSI planning summaries consume them.
- `somatic.sensors.csi_parser` parses local CSI fixtures and returns sanitized aggregate report/summary artifacts for replay.
- `somatic.sensors.evidence` defines generic sanitized sensor-evidence contract primitives for identity, compatibility classification, deterministic fingerprinting, readiness vocabulary, artifact refs/hashes, diagnostics/count categories, privacy-boundary flags, and compact run-relative artifact refs with SHA-256 hashes.
- `somatic.sensors.csi_evidence_pack` exports deterministic portable evidence-pack JSON from sanitized CSI metadata only.
- `somatic.sensors.environment` reads neutral local CSV fixtures and emits sanitized row/count/status evaluation metadata only.
- `somatic.sensors.environment_evidence_pack` exports deterministic portable evidence-pack JSON from that neutral environment metadata through the generic contract.
- `somatic.sensors.toy_counter` and `somatic.sensors.toy_counter_evidence_pack` provide the public extension-template proof using checked-in toy count/status fixtures only.
- `somatic.sensors.registry` lists fixture-only sanitized evidence providers and validates workflow evidence-provider config before runtime dispatch; the CLI reads this metadata without instantiating providers.
- `docs/wifi-csi-source-staging.md` records Phase 8A staged-reference paths, commits, license status, dependency notes, and non-adoption rules.
- `somatic.memory.baseline` emits fake-backed personal profile, baseline graph, and baseline comparison artifacts from finalized sandbox features.
- `somatic.memory.intervention` emits fake-backed intervention tags, context, response evaluation plans, and mock ledger metadata from finalized n-of-1 artifacts.
- `somatic.memory.response_evaluation` emits fake-backed follow-up windows, follow-up snapshots, response comparisons, and response evaluation summaries without live capture or effectiveness claims.
- Supported scaffold modalities are `csi`, `video`, `video3d`, `thermal`, `audio`, `wearable`, and `environmental`.
- Sensors are optional adapters. The basic runtime remains dependency-free.

## Phase 7A/7B Runtime Boundary

- Sandbox sensor mode is fake-backed only.
- No hardware, CSI, camera, microphone, audio, BLE, WiFi, wearable, thermal, environmental, or OS sensor device is accessed.
- No ESP32, RTL8812AU, router, WiFi adapter, driver, monitor mode, packet capture, WiFi device probing, raw RF/CSI collection, or CSI runtime is used.
- No serial capture, SD-card read/write, MQTT/UDP listener, channel hopping, `tcpdump`, `tshark`, `aircrack-ng`, driver change, WiFi interface reconfiguration, or staged source execution is used.
- No network code, external API call, provider secret, package install, or sensor package import is added.
- No database, external memory, Hindsight, Mem0, Zep, real profile storage, real health-data loading, personal health-data export, or baseline export is added.
- No real health data is loaded.
- No diagnosis, treatment, emergency triage, clinical interpretation, or real monitoring is produced.
- No emergency triage is performed.
- RuView is conditional reference-only and must not be copied, imported, executed, depended on, or treated as a Somatic implementation source.
- Booth-first WiFi CSI planning is future metadata only: one intended subject, a small controlled booth, fixed AP plus 4-6 receiver-node metadata, ESP32-S3 preferred radios, and an empty-booth baseline concept.

Future real sensor mode requires explicit user consent, a local-first privacy policy, retention/export controls, and safety review before any adapter can run.

Future real WiFi CSI mode requires explicit consent from the operator, intended
subject, and all potentially affected people in the sensing area. Do not deploy
in shared, public, workplace, household, or care environments unless bystanders
are informed and consent is practical. WiFi CSI, RSSI, pcap, serial CSI logs,
SD-card CSVs, raw RF/CSI, derived features, embeddings, ReID sequences, pose
outputs, skeleton outputs, and activity labels are sensitive by default.
Upstream fall-detection, vital-sign, monitoring, identity-like recognition,
ReID, continuous-learning, and pose references are research context only, not
Somatic capabilities.

## Phase 8D CSI Replay Boundary

- `SandboxSensorProvider.replay_csi_fixtures(...)` is fixture-backed only and
  reads files through the Phase 8C parser contract.
- Replay output is sanitized parser metadata: fixture count, frame count, sample
  count, malformed-row count, neutral source format classes, structured
  parse-error codes, and closed boundary flags.
- Replay output does not expose raw sample arrays, source IDs, absolute paths,
  raw signal values, or raw component identifier keys.
- Unsupported, missing, or unsafe fixture refs fail closed as rejected parser
  metadata.
- Replay does not add serial, MQTT, UDP, monitor mode, pcap/radiotap parsing,
  router tooling, credentials, hardware access, live capture, vital-sign
  inference, diagnostic claims, or medical claims.

## Phase 8G CSI Evidence-Pack Boundary

- Evidence packs are standard-library-only JSON metadata.
- Evidence packs package parser, replay, scoring, and batch readiness counts,
  statuses, contract versions, bounded scores, sanitized diagnostic categories,
  and deterministic fingerprints.
- Evidence packs do not include fixture refs, private fixture filenames, source
  IDs, absolute paths, unsafe refs, provider payload bodies, parser report
  bodies, parser summary bodies, raw CSI arrays, or signal values.
- Evidence packs are additive run artifacts only. They do not create Fabric
  manifests, sign, publish, transport, seed, install, execute, alter
  tournament scores, or make clinical claims.

## Phase 9A/9B Generic Sensor-Evidence Contract Boundary

- `somatic.sensors.evidence` is a reusable foundation for future sanitized
  sensor providers. It is not a live sensor adapter and does not add capture,
  parsing, transport, hardware, network, or clinical capability.
- The generic contract captures reusable evidence-pack primitives only:
  contract/version identity, provider/evidence kind, compatibility
  classification, deterministic sanitized fingerprinting, readiness status,
  privacy boundary flags, sanitized diagnostic/count categories, and
  run-artifact refs/hashes.
- CSI remains the first implementation. CSI v1 keeps its existing public
  artifact shape, `artifacts/csi_evidence_pack.json` path, fingerprint scope,
  pack id prefix, compatibility classifications, and checked-in expected packs.
- Future providers must use the generic contract only for sanitized metadata.
  They must not embed raw sensor values, source IDs, unsafe refs, provider
  payload bodies, parser report bodies, parser summary bodies, absolute paths,
  credentials, or private references.
- Phase 9B generic artifact refs are compact references outside the evidence
  pack payload. They use run-relative `artifacts/...` paths plus SHA-256, carry
  provider/evidence kind and pack fingerprint metadata, and classify malformed,
  missing, unsafe, or hash-mismatched artifacts with sanitized error codes.
- Fabric planning consumes only these sanitized evidence-pack refs for the
  portable sensor-evidence surface. CSI parser report and parsed-summary
  artifacts remain local diagnostics and are not portable Fabric candidates.

## Phase 9C Environment Fixture Evidence Boundary

- `artifacts/environment_evidence_pack.json` is the second concrete sanitized
  sensor-evidence provider output. It proves the generic contract can represent
  a non-CSI provider without changing CSI v1 artifact names, shapes,
  fingerprints, compatibility behavior, or public examples.
- The environment provider is fixture-only, mock, offline, deterministic,
  standard-library only, and local-only. It reads configured local CSV fixtures
  and exports only row counts, status counts, bounded quality scores,
  diagnostic category counts, closed boundary flags, pack ID, and pack
  fingerprint.
- The pack does not export fixture refs, fixture filenames, row bodies, raw
  values, source identifiers, unsafe refs, absolute paths, provider payload
  bodies, parser report bodies, parser summary bodies, credentials, CSI terms,
  signal terms, hardware access, network calls, or live capture.
- n-of-1 report packets, run manifests, tournament summaries, and planning-only
  Fabric pack plans reference the pack through the same generic
  `sensor_evidence_artifact_refs` shape used by CSI: run-relative
  `artifacts/environment_evidence_pack.json` plus SHA-256 and pack
  fingerprint.
- Tournament exposure is additive readiness metadata only. It is not ranking
  input and does not modify candidate scoring, Elo, brackets, winners, or
  rankings.

## Phase 9D Provider Registry And Config Validation

- `somatic.sensors.registry` is metadata-only. It lists the current evidence
  providers `wifi-csi`, `environment-fixture`, and `toy-counter-fixture`, their evidence kinds,
  contract versions, artifact names, run-relative artifact refs, supported
  fixture format labels, fixture modes, and offline fixture-only status.
- The registry does not instantiate providers, read fixture bodies, embed
  provider/parser payloads, change evidence-pack JSON, or alter pack
  fingerprints. CSI remains `artifacts/csi_evidence_pack.json`; environment
  remains `artifacts/environment_evidence_pack.json`.
- Workflow validation now checks configured sensor-evidence inputs before
  runtime dispatch. It accepts known provider IDs only, enforces bounded ref
  and group counts, requires fixture-only local refs, and rejects absolute
  paths, unsafe URL refs, device/live/network selectors, credentials, and
  action-enabling sensor constraints with sanitized error codes.
- n-of-1 and tournament dispatch use the registry to find CSI/environment
  fixture refs and generic artifact-ref metadata. This removes ad hoc provider
  wiring while preserving pack shapes, artifact names, compatibility behavior,
  rankings, Elo, brackets, winners, and candidate scoring.
- To add a future sanitized provider, add a registry entry, a fixture-only
  evidence-pack builder, focused validation limits, and tests proving
  deterministic packs, run-relative artifact refs, closed privacy flags, and
  no ranking or live-capture behavior.

## Phase 9E Public Extension Template

- `docs/sensor-evidence-extension-template.md` describes the provider module,
  evidence-pack module, registry entry, fixture config, artifact naming,
  compatibility, fingerprinting, and privacy checklist for future sanitized
  providers.
- `toy-counter-fixture` is the third provider and the first public extension
  proof. It uses only checked-in toy CSV fixtures, exports count/status metadata
  only, and writes `artifacts/toy_counter_evidence_pack.json` when explicitly
  configured.
- The toy provider is registered through `somatic.sensors.registry`, validated
  through the same workflow config path as CSI and environment, and referenced
  through the same run-relative `sensor_evidence_artifact_refs` plus SHA-256
  shape.
- The toy provider is examples/tests only. Default n-of-1 and tournament
  fixtures remain CSI/environment-focused, and CSI/environment pack names,
  shapes, compatibility behavior, and fingerprints are unchanged.

## Phase 9F Discovery And Validation CLI

- `python -m somatic sensor-evidence providers` lists registry metadata only:
  provider ID, evidence kind, contract version, artifact name, fixture-only
  status, fixture mode labels, and supported fixture formats.
- `python -m somatic sensor-evidence validate --workflow <workflow.yaml>`
  validates configured sensor-evidence providers before runtime dispatch and
  returns sanitized error categories. It does not echo rejected fixture refs,
  absolute paths, URLs, provider private values, credential-looking values, or
  payload bodies.
- Validation diagnostics distinguish unknown providers, unsafe refs, excessive
  ref/group counts, live/device/network fields, credential-like fields,
  unsupported fixture modes, unsupported fixture formats, and offline boundary
  flags.
- Discovery and validation are preflight-only. They do not read fixture bodies,
  write run artifacts, change evidence-pack JSON, alter pack fingerprints,
  mutate tournament rankings/Elo/brackets/winners, or plan/publish Fabric packs.

## Phase 9G Provider Manifest Snapshot

- `somatic.sensors.registry.sensor_evidence_provider_manifest()` is the
  canonical public registry snapshot for fixture-only evidence providers.
- `python -m somatic sensor-evidence providers --format json` renders that
  manifest directly. Text output is only a compact human rendering of the same
  provider order and fields.
- The checked-in snapshot
  `fixtures/providers/sensor-evidence-provider-manifest-v1.json` locks provider
  order, provider count, contract identities, artifact names, fixture modes,
  supported formats, offline flags, and public boundary labels.
- Manifest compatibility uses `compatible`, `incompatible`,
  `unsupported_version`, and `malformed`. Additive safe public metadata is
  allowed, but internal registry fields, private values, fixture refs, unsafe
  refs, paths, credentials, provider internals, parser internals, and raw
  value terminology fail closed with sanitized manifest errors.
- The manifest is discovery metadata only. It does not instantiate providers,
  read fixture bodies, write artifacts, change CSI/environment/toy evidence
  packs, alter fingerprints, or modify tournament scoring, Elo, brackets,
  winners, rankings, reports, or Fabric plans.

## Phase 9H Through 11K Release Summary Boundary

- `docs/phase-9h-release-summary.md` summarizes the Phase 8C through 11K
  evidence/adapters subsystem, public commands, registered providers, artifact
  names, compatibility contracts, run/Fabric reference behavior, privacy
  boundary, adapter readiness gates, invariant audit, checkpoint, Phase 11
  planning records, and extension path.
- `docs/phase-10-checkpoint.md` records the current evidence-domain matrix and
  next safe lanes for contract-only future real-mode planning.
- `fixtures/reports/sensor-evidence-subsystem-summary-v1.json` mirrors that
  summary as a compact machine-readable artifact aligned with the provider
  manifest version and provider count.
- Phase 9H through 11K release/status work is documentation, manifest-summary,
  and release evidence only. It does not add providers, read fixture bodies,
  alter evidence fingerprints, write runtime artifacts, enable live capture, or
  modify tournament scoring, Elo, brackets, winners, rankings, reports, or
  Fabric plans.

Future real baseline storage requires explicit local storage consent,
data-locality review, local-first privacy controls, privacy review, safety
review, human review, retention/export controls, and separate opt-in
configuration.

## Phase 7D Intervention Boundary

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

- Mock intervention tags are metadata labels only.
- No recommendation, no prescription, no treatment recommendation, no medical
  advice, no diagnosis, no emergency triage, no real monitoring, and no
  reminders, automation, or scheduling is produced.
- Medication placeholder disabled and clinician review placeholder disabled are
  disabled metadata only.
- Response evaluation is future planning only and does not schedule, notify,
  remind, monitor, or claim effectiveness.
- Future real intervention use requires explicit consent, human/clinical
  review, local storage controls, safety gates, and no emergency-triage
  substitution.

## Phase 7E Response Evaluation Boundary

- Response evaluation is fake-backed local research-only planning only.
- Follow-up comparison uses fixture trend labels only.
- No intervention effectiveness is claimed.
- No effectiveness claim, no recommendation, no prescription, no treatment
  recommendation, no medical advice, no medication action, no clinician action,
  no diagnosis, and no emergency triage is produced.
- No reminders, automation, notification, scheduling, or real monitoring is
  created.
