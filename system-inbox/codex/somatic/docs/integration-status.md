# Integration Status

This page classifies external integrations and references for the master-plan scaffold.

## Currently Implemented

- Standard-library local mock runner.
- Local fixture workflow loader.
- Local run artifact writer.
- Evidence Bus dataclass contracts.
- Phase 5A external science integration intake docs.
- Phase 5A.1 external source staging inventory and documentation.
- Phase 5B PaperQA2 source inspection docs and optional provider scaffold.
- Phase 5C scientific-agent-skills source inspection docs and metadata-only provider scaffold.
- Phase 5E AutoScientists source inspection, TeamOrchestrator mapping, and reference-only provider scaffold.
- Phase 5F FutureHouse Robin/Aviary/LDP source inspection, mapping, fixtures, and reference-only Robin scaffold.
- Phase 6A Boltz source inspection, biomodel boundary docs, fake-backed Boltz provider scaffold, biomodel fixtures, and doctor status.
- Somatic-owned provider interface scaffolds for literature, science skills, biomodel, and team orchestration.

## Scaffolded

- BitTorrent/Fabric: package boundary and docs exist; no transport runtime.
- WiFi CSI reference repos: sensor lane and CSI modality exist; Phase 7B adds planning metadata only, and Phase 8A stages reference sources for read-only source review only; no live CSI implementation.
- Hindsight/mem0/zep: memory lane scaffold only.
- promptfoo/garak/Decepticon-pattern safety: safety lane scaffold only.
- NeuroKit2: optional `csi` extra candidate; no runtime use.
- MiniCPM-V 4.5: planned vision reference; no runtime use.
- MiniCPM-o 4.5: planned multimodal reference; no runtime use.
- PaperQA2: disabled optional provider scaffold in `somatic.providers.paperqa2`, deterministic fake-backed mode, staged read-only source at `C:\AI\external-sources\somatic\paper-qa`, and no basic-install dependency.
- FutureHouse Robin: disabled fake-backed `somatic.providers.robin` scaffold plus staged read-only source at `C:\AI\external-sources\somatic\robin`; Apache-2.0 license found.
- K-Dense-AI/scientific-agent-skills: disabled metadata-only provider scaffold in `somatic.providers.scientific_agent_skills`, deterministic fake-backed skill/database catalog, staged read-only source at `C:\AI\external-sources\somatic\scientific-agent-skills`, MIT license found, and no basic-install dependency.
- AutoScientists: disabled reference-only provider metadata and fake-backed `AutoScientistsTeamOrchestrationProvider` scaffold plus staged read-only source at `C:\AI\external-sources\somatic\AutoScientists`; no license file found.
- Boltz-2: disabled fake-backed `somatic.providers.boltz` scaffold plus staged read-only source at `C:\AI\external-sources\somatic\boltz`; MIT license found; no runtime import, prediction, model download, MSA server call, or GPU execution.
- Aviary and LDP: disabled reference-only provider fixtures plus staged read-only reference sources; Apache-2.0 licenses found; no runtime adoption.

## Planned

- PaperQA2 real mode: pending explicit optional install path, consent/data-locality gates, and real index/search/evidence mapping.
- scientific-agent-skills real catalog parsing: pending explicit static frontmatter parser, allowlisted connector metadata, consent/data-locality gates, and no execution by default.
- AutoScientists: live team-orchestration runtime candidate, pending license review, service boundary design, explicit configuration, and consent.
- FutureHouse Robin/Aviary/LDP real runtime: pending optional extras, Edison/LLM/service boundary design, data-locality gates, and explicit opt-in.
- Boltz-2 real mode: pending explicit optional install path, no-download/cache policy, MSA strategy, resource checks, provenance hashing, and safety review.
- Chai-1: biomodel lane candidate.
- ESM3: biomodel lane candidate.
- DiffDock: biomodel lane candidate.
- Chronos/TimesFM/MOMENT: time-series lane candidates.
- LLaVA-Med/BioMedCLIP/Med-Gemini: medical/biomedical vision-language references, subject to strict research-only and human-review boundaries.

## Needs Inspection

- Real PaperQA2 output shapes under an explicit optional install before enabling non-mock execution.
- Scientific-agent-skills broader catalog parsing and per-skill safety classification beyond the Phase 5C deterministic subset.
- FutureHouse Robin/Aviary/LDP real output shapes under explicit optional installs before any runtime adapter is considered.
- Boltz real prediction output shapes under explicit optional install and local no-download fixtures before any runtime adapter is considered.
- Harvard AutoScientists license status before any source copy, dependency, import, or live runtime implementation.
- Aviary and LDP remain optional references; no runtime adoption planned by default.
- Torrent library choice for Fabric transport.
- Canonical JSON and signature canonicalization details for Fabric.

## Reference-Only

- WiFi CSI research repositories: `NTUMARS/Awesome-WiFi-CSI-Sensing`, `thu4n/ESP32-WiFi-Sensing`, and `MaliosDark/wifi-3d-fusion` are staged under `C:\AI\external-sources\somatic\wifi-csi\` for Phase 8A read-only source review. They remain reference-only and are not adopted, imported, copied, executed, installed, or depended on.
- Decepticon-pattern safety references.
- Biomedical VLM research references.

## Optional and Non-Default

- Kronos: optional and non-default due scope, dependency, and market-data adjacency concerns.

## Conditional Reference-Only

- RuView: conditional reference-only for WiFi CSI reassessment; do not depend on,
  import, vendor, copy, execute, or adopt downstream sensing claims.

## Adoption Rule

No integration becomes active until it has:

- explicit package boundary
- optional extra or install note
- local fixture tests
- safety review
- no secret leakage
- no default network execution
