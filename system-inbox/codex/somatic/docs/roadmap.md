# Roadmap

## Phase 0: Documentation Skeleton

- Establish repository structure.
- Define standalone boundaries.
- Draft workflow modes.
- Draft package and example placeholders.
- Draft fabric integration concept.
- Define safety and regulatory notes.

## Phase 1A: Contracts and Schema Fixtures

- Define workflow manifest schema.
- Define provider adapter capability schema.
- Define evidence record schema.
- Define safety gate request and response schema.
- Define report packet schema.
- Define run artifact layout.
- Define pack manifest schema.
- Add offline JSON and YAML fixtures for future validation.
- Keep the repository free of runtime loaders, package installs, and external API calls.

## Phase 1B: Minimal CLI Runner

- Add the first runnable local mock CLI.
- Read fixture workflows and validate required contract fields.
- Load mock provider metadata only.
- Emit run artifact folders without calling external services.
- Keep all examples offline, deterministic, and provider-agnostic.

## Phase 1C: Master Plan Foundation

- Add Python project metadata and optional extras.
- Preserve the standard-library mock runner.
- Add master-plan package boundaries.
- Add Evidence Bus interfaces and modality identifiers.
- Add CLI commands for `run`, `launch`, `doctor`, and `replay`.
- Add docs for install modes, integration status, capabilities, sensors, orchestration, and development.
- Keep advanced lanes scaffolded and disabled by default.

## Phase 2: Local-Only Reference Runtime

- Implement a small local orchestrator on top of the Phase 1C package lanes.
- Expand mock providers and deterministic fixtures.
- Add local report generation.
- Add pack verification fixtures.
- Keep all examples offline and reproducible.
- Add the first deterministic offline hypothesis tournament fixture, scoring path, bracket artifact, refinement pass, and ranked hypotheses.
- Phase 2.1 adds deterministic pairwise debate artifacts, Elo-style tournament ratings, a local mock batch scorer interface, and a disabled future team-orchestrator hook.
- Phase 2.5 adds deterministic mock TeamOrchestrator artifacts for team roster, critiques, shared blackboard state, evidence-budget planning, reorganization logs, and scaffold summary.

## Phase 3: Research Engines

- Implement literature-only workflows.
- Implement hypothesis tournament workflows.
- Implement Robin-style loop scaffolding.
- Add provenance and evidence ranking.
- Phase 3A adds the offline Robin-shaped Evidence Bus loop with Crow, Falcon, sandbox EvidenceSource, Finch, StructuredVerdict, report, and next iteration artifacts.

## Phase 3B: Fabric Conformance Alignment

- Add the normative Content Fabric v1.0.0 Somatic copy.
- Add conformance targets and fixtures for future byte-identical manifests and signing payloads.
- Add standard-library precheck scaffolding for integer-only JSON, path confinement, unsigned code packs, and license gates.
- Keep full Fabric runtime, networking, signing, catalog serving, quarantine, sandboxing, explicit enablement, and cross-harness verification as future work.

## Phase 4: Simulation and In-Silico Adapters

- Add sandbox lab simulation.
- Add optional in-silico adapter contracts and fixtures.
- Add dry-run examples for molecular and cheminformatics workflows.
- Phase 4B adds local Content Fabric runtime primitives: integer-only JSON validation, deterministic scaffold canonicalization, signing payload construction, SHA-256 helpers, path and license prechecks, manifest/keyring/catalog validators, and a local `fabric check` CLI.
- Phase 4C adds the optional Fabric crypto/keyring foundation: Ed25519 helpers, deterministic key ids, local signing over scaffold payloads, signed keyring root-threshold checks, signed pack publisher-threshold checks, crypto fixtures, and `fabric check --keyring`.
- Phase 4D prepares for Locus interoperability by inspecting `C:\AI\locus\electron\content-fabric\`, documenting implementation gaps, reserving interop fixture locations, and adding placeholder tests without importing Locus or copying fixtures.
- Phase 4E closes clean-room byte-conformance gaps: raw JSON numeric lexeme rejection, JCS-style payload vectors, keyring replacement continuity, signed catalog vectors, context license decisions, interop metadata fixtures, and CLI helpers for payload digests and keyring rotation checks.
- Phase 4F runs local mutual fixture verification against Locus commit `79f480d592ec82e879b7588a25bad6b4ea2536ca`, records a factual report, and updates interop metadata. The result is partial verification, not certification.
- Phase 4G.1 implements local RFC 8785/JCS canonicalization for Fabric-supported JSON, adds local JCS fixtures, rejects duplicate object names and invalid surrogate strings, and adds `fabric canonicalize` without running full Locus mutual verification.
- Phase 4G.2 adds Somatic-generated shared interop fixtures for signed code/data packs, keyring, catalog, expected digest metadata, invalid rejection cases, and local Somatic self-certification commands without running Locus verification.
- Phase 4G.3 certifies the Somatic-origin shared fixture set against Locus commit `5f81ee360834dc6451c4ea35d7509325813d9d10`, including byte/digest parity, pack/keyring signatures, catalog shape/signature primitive verification, and invalid rejection vectors.
- Broader Locus-owned fixture exchange, high-level catalog signature parity, transport/catalog runtime, install/quarantine/enablement runtime, and expanded cross-verification with Locus remain required before any full Fabric runtime conformance or full Locus-certified interop claim.

## Phase 5: Sensors, Labs, and Human Review

- Add sensor adapter contracts.
- Add WiFi CSI research workflows.
- Add manual lab planning workflows.
- Add strict approval gates for any real lab adapter.
- Phase 5A maps external science integration targets without cloning,
  installing, calling APIs, or enabling live providers. It adds disabled
  provider placeholders for PaperQA2, Robin, scientific-agent-skills,
  AutoScientists, and Boltz-2, plus Somatic-owned adapter interfaces.
- Phase 5A.1 stages external source references under `C:\AI\external-sources\somatic\`.
- Phase 5B adds a disabled optional PaperQA2 adapter scaffold after local source inspection. The scaffold has deterministic fake-backed mode, no basic-install dependency, lazy availability detection, and fail-closed real mode.
- Phase 5C adds a disabled scientific-agent-skills metadata provider scaffold after local source inspection. The scaffold has deterministic fake-backed skill and database connector metadata, no skill execution, no database/API calls, no basic-install dependency, staged MIT source notes, and fail-closed real mode.
- Phase 5D expands Finch with a standard-library local analysis toolbelt for
  CSV profiling, deterministic descriptive stats, preliminary dose-response
  summaries, and provenance hashing inside the offline Robin sandbox loop.
  pandas, scipy, numpy, scanpy, biopython, and real lab/scientific validation
  remain future optional work.
- Phase 5E deepens AutoScientists TeamOrchestrator mapping with read-only
  source inspection, deterministic lifecycle/confidence/critique/stall/
  blackboard/budget/reorganization metadata, report sections, and a disabled
  reference-only provider scaffold. Live AutoScientists runtime work remains
  blocked on license clarification and explicit configuration.
- Phase 5F deepens FutureHouse Robin/Aviary/LDP mapping with read-only source
  inspection, Apache-2.0 license recording, disabled fake-backed Robin provider
  scaffold, Aviary/LDP placeholder fixtures, and docs that keep Somatic's own
  Evidence Bus and Crow/Falcon/Finch shape. Robin, Aviary, LDP, Edison,
  OpenAI, Anthropic, LiteLLM, fhlmi, and PaperQA2 real mode remain disabled.
- Phase 5G scaffolds Finch optional extras for future package-backed local
  analysis. pandas, scipy, numpy, scanpy, and biopython availability is reported
  lazily as disabled metadata only; the Robin loop stays on the
  standard-library Finch toolbelt and no package-backed analysis is enabled.
- Phase 6A adds the disabled Boltz-2 biomodel provider planning scaffold after
  read-only inspection of `C:\AI\external-sources\somatic\boltz` at commit
  `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`. It records MIT licensing,
  deterministic fake-backed `BiomodelPlan` and `BiomodelResult` metadata,
  Evidence Bus mapping, doctor status, and fixture tests without Boltz imports,
  model downloads, MSA server calls, GPU execution, or real predictions.
- Phase 6B wires fake-backed biomodel planning into the local
  `in-silico-screening` workflow. The runner emits biomodel request, plan,
  result, Evidence Bus mapping, raw evidence, structured verdict, summary, and
  report artifacts while preserving the no Boltz import/execution, no downloads,
  no MSA server, no network, no GPU/runtime, and no real prediction boundary.
- Phase 6C adds standard-library biomodel readiness gates, consent placeholders,
  deterministic block reasons, fake-backed readiness artifacts, fail-closed
  Boltz real-mode errors, unsafe workflow constraint rejection, and doctor/docs
  status while preserving no runtime execution even when a dangerous test
  fixture marks every policy flag enabled.
- Phase 6D adds standard-library biomodel artifact provenance helpers,
  deterministic in-silico provenance and pack-plan artifacts, future Fabric
  `data` pack planning, placeholder fixtures, and docs/tests while preserving
  no Boltz import/execution, no downloads, no network/API/MSA server calls, no
  Fabric publishing/transport/install/signing, and no scientific or clinical
  efficacy claims.
- Phase 7A adds standard-library sensor provider dataclasses, a deterministic
  sandbox sensor provider, fake-backed `n-of-1` workflow artifacts, privacy
  placeholder fixtures, docs, and tests while preserving no hardware access, no
  CSI/camera/audio/wearable capture, no network code, no real monitoring, and
  no diagnosis/treatment/emergency-triage claims.
- Phase 7B adds a standard-library WiFi CSI planning scaffold, deterministic
  CSI placeholder metadata, local reference inventory fixtures, docs, and tests
  while preserving no WiFi hardware access, no ESP32/RTL8812AU/router/driver
  use, no monitor mode, no packet capture, no WiFi device probing, no raw
  RF/CSI collection/export, no network code, and no clinical claims. Phase 10G
  reclassifies RuView as conditional reference-only while preserving the
  do-not-copy/import/execute/depend boundary.
- Phase 8A stages WiFi CSI reference sources outside the Somatic checkout for
  read-only source review only, with no runtime dependency, source vendoring,
  hardware access, package install, serial/MQTT/UDP/pcap path, or medical
  claim.
- Phase 8B adds a standard-library WiFi CSI parser scaffold for local
  fake/sample fixtures only, deterministic parser reports, n-of-1 summary
  artifacts, docs, and tests while preserving no serial, no MQTT, no UDP, no
  pcap, no monitor mode, no live capture, no hardware access, no network code,
  no vital-sign inference, and no medical claims.
- Phase 7C adds a standard-library personal baseline graph scaffold,
  deterministic fake-backed profile/graph/comparison artifacts, baseline
  fixtures, docs, and tests while preserving no real health-data loading, no
  real profile storage, no database or external memory runtime, no personal
  health-data export, no hardware access, no network/API code, and no medical,
  clinical, diagnosis, treatment, monitoring, or emergency-triage claims.
- Phase 7D adds a standard-library n-of-1 intervention tag scaffold,
  deterministic fake-backed intervention tag/context/response-plan/mock-ledger
  artifacts, fixtures, docs, and tests while preserving no advice, medical
  advice, recommendation, prescription, treatment recommendation, medication
  action, clinician action, effectiveness claim, real monitoring, reminders,
  automation, scheduling, hardware access, network/API code, database runtime,
  external memory runtime, diagnosis, or emergency-triage claims.
- Phase 7E adds a standard-library n-of-1 response evaluation scaffold,
  deterministic fake-backed follow-up window/snapshot/response-comparison/
  response-summary artifacts, fixtures, docs, and tests while preserving no
  intervention effectiveness claim, no recommendation, no prescription, no
  treatment recommendation, no medical advice, no medication action, no
  clinician action, no reminders, no automation, no notification, no
  scheduling, no real monitoring, no hardware access, no network/API code, no
  database runtime, no external memory runtime, no diagnosis, and no
  emergency-triage claims.
- Phase 7F adds a standard-library consolidated n-of-1 report packet,
  deterministic artifact refs and SHA-256 hashes, loop-stage summary,
  fixtures, docs, and tests while preserving fake-backed/local/research-only
  boundaries, no medical record or health record semantics, no advice, no
  recommendation, no prescription, no treatment recommendation, no medical
  advice, no intervention effectiveness claim, no monitoring, no scheduling,
  no hardware access, no network/API code, no database runtime, no external
  memory runtime, no diagnosis, and no emergency-triage claims. Hashes are for
  reproducibility/provenance only.
- Phase 7G adds a standard-library planning-only n-of-1 Fabric pack plan,
  deterministic report-packet/file refs and hash reuse, placeholder fixtures,
  docs, and tests while preserving private-only defaults, no Fabric manifest,
  no signing, no catalog publication, no transport, no magnet, no WebSeed, no
  seeding, no upload, no install, no execution, no code pack, no executable
  files, no real personal data export, no personal health data export, no raw
  sensor or raw RF/CSI data export, and no medical, clinical, or effectiveness
  claims. Future real packaging requires explicit consent, redaction, license
  review, privacy review, safety review, human review, local-first storage
  controls, retention/export controls, and separate publication approval.

## Phase 6: Fabric and Ecosystem

- Add local and remote catalogs.
- Add verified pack ingest.
- Add code-pack quarantine and enablement.
- Add license gates.
- Add adapter and workflow pack examples.
- Keep Boltz-2 and other biomodel runtime work behind explicit opt-in,
  model/download/MSA consent gates, resource checks, provenance hashes, and
  research-only safety review.
- Keep biomodel Fabric packaging behind license, provenance, hash, safety, and
  explicit publication review; Phase 6D only records local planning metadata.
