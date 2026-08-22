# Somatic history (pre-pivot archive)

The product README (rewritten 2026-08-19 to the kortex-audio documentation bar) is the live front page. This file keeps the moved phase / scaffold history so that front page stays current.

These sections are provenance, not the live product pitch. Live advisory output is informational only. Do not treat archived clinical decision-support language as a product claim.

## Pre-pivot archive

The sections below describe the earlier docs-first scientific-discovery scaffold (mock workflows, Phase 11/12 planning contracts, Fabric). They are kept for provenance. They are **not** the current product pitch. Do not treat "clinical decision-support reports" language below as a product claim — live advisory output is informational only.

---

Somatic also retains a standalone open scientific discovery harness for research workflows. It is designed to connect literature review, hypothesis generation, simulation, sensor observation, manual or cloud lab planning, and safety-gated reporting through provider adapters.

Somatic must not depend on OpenClaw, Locus, Multiverse, or any private harness. The architecture is adapter-first so arbitrary LLM, science, lab, sensor, simulation, dataset, and reporting providers can be added without changing core workflow contracts.

## Positioning (archive)

Somatic's pre-pivot plan combined:

- Co-Scientist-style hypothesis tournaments for structured idea generation and critique.
- Robin-style Crow/Falcon/Finch loops for literature search, experimental design, and analysis.
- In-silico modeling adapters such as Boltz, ESM, Chai, AlphaFold-optional, RDKit, and future model providers.
- Real wet-lab, manual-lab, and cloud-lab adapters with explicit human review.
- Sandbox lab simulation for users without lab access.
- WiFi CSI and other sensor-observation adapters.
- Personal or patient baseline graphs for local-first health research.
- Safety-gated scientific and clinical decision-support reports.
- A BitTorrent/WebSeed content fabric for verified datasets, models, documents, workflows, and plugin packs.

## Phase 0 Scope

This repository currently contains a docs-first skeleton only. There are no runtime installs, package downloads, external API calls, provider credentials, or heavy implementation code in this phase.

Phase 0 establishes:

- Repository structure and package boundaries.
- Workflow mode placeholders.
- Safety and regulatory boundaries.
- Future content fabric design.
- Review checklists for later implementation phases.

## Phase 1A Contracts

Phase 1A adds canonical contract documentation and offline validation fixtures before any real workflow loader or runtime code exists. The contracts define workflow manifests, provider metadata, evidence records, safety gate requests and responses, report packets, run artifacts, and Fabric pack manifests.

The fixtures in `fixtures/` are plain JSON and YAML examples. They are intended for future schema validation and mock-provider tests without package installs, external API calls, or private harness dependencies.

## Phase 1B Local Mock Run

Phase 1B adds the first executable local runner. It uses Python's standard library, local workflow fixtures, and mock provider metadata only.

Run the literature-only fixture:

```powershell
python -m somatic run fixtures/workflows/valid-literature-only.yaml
```

The command writes `runs/{run_id}/` with a manifest, resolved workflow, sample evidence, mock hypotheses, sample safety response, Markdown report, and next-iteration hints. The output is mock/offline, research-only, and not medical advice.

## Phase 1C Master Foundation

Phase 1C upgrades Somatic into a Python monorepo scaffold aligned with the master plan while preserving the Phase 1B mock runner.

- `pyproject.toml` defines the `somatic` project, console script, ruff, mypy, pytest, and optional extras.
- `somatic/` now has explicit package lanes for core, evidence bus, agents, engines, sensors, safety, memory, presence, Fabric, bench, CLI, reports, and simulator work.
- The basic runtime remains standard-library only.
- Advanced lanes are optional extras and disabled unless explicitly configured.
- Presence and avatar work is render-only and never part of the reasoning path.
- Sensors are local-first and private by default.

CLI commands:

```powershell
python -m somatic doctor
python -m somatic sensor-evidence providers
python -m somatic sensor-evidence validate --workflow fixtures/workflows/valid-n-of-1.yaml
python -m somatic run fixtures/workflows/valid-literature-only.yaml
python -m somatic launch --config path/to/config.yaml
python -m somatic replay run-id
```

After installing the package, the equivalent console script is `somatic`.

## Phase 2 Offline Hypothesis Tournament

Phase 2 adds the first deterministic Co-Scientist-style mock tournament while keeping the runtime local, offline, and standard-library only. Phase 2.1 adds deterministic pairwise debates, Elo-style ratings, and a local mock batch scorer interface. Phase 2.5 adds a mock TeamOrchestrator scaffold for team critiques, shared blackboard state, evidence-budget planning, and reorganization logs.

Run the tournament fixture:

```powershell
python -m somatic run fixtures/workflows/valid-hypothesis-tournament.yaml
```

The command preserves the Phase 1B baseline run artifacts and adds candidate hypotheses, reflection notes, review scores, pairwise debates, Elo ratings, mock team orchestration artifacts, a tournament bracket, refined hypotheses, and final ranked hypotheses. `artifacts/hypotheses.json` mirrors the final ranked hypotheses for compatibility.

This mode uses fixed mock data and deterministic scoring only. It does not call external APIs, install dependencies, use provider secrets, run Fabric, execute biomodels, capture WiFi CSI or sensor data, use LangGraph, or perform lab or clinical actions. The output is research-only, not medical advice, and not a real scientific conclusion.

## Phase 3A Robin Sandbox Loop

Phase 3A adds the first runnable Robin-shaped Evidence Bus loop while staying fully offline and standard-library only. Crow creates mock literature context, Falcon creates a local measurement plan, the sandbox EvidenceSource acquires deterministic `literature`, `sim`, and `wetlab`-shaped `RawEvidence`, and Finch emits a deterministic `StructuredVerdict`.

Run the Robin loop fixture:

```powershell
python -m somatic run fixtures/workflows/valid-robin-loop.yaml
```

The command preserves the baseline run artifacts and adds Crow, Falcon, raw
evidence, Finch, Finch toolbelt, structured verdict, and Robin loop summary JSON
artifacts. It does not install dependencies, call external APIs, use PaperQA2,
FutureHouse Robin, scientific-agent-skills, LangGraph, AutoScientists, Fabric
runtime, biomodel runtime, real sensor runtime, or real lab runtime.

See `docs/robin-loop.md` and `docs/evidence-bus-sandbox.md`.

## Phase 3B Content Fabric Conformance Scaffold

Phase 3B aligns Somatic with the canonical Multiverse Content Fabric v1.0.0 standard used across Locus, Multiverse, kortex-audio, locus-evolution-lab, Somatic, and ardynos. Somatic must later cross-verify with Locus `electron/content-fabric/`, but Locus is not a Somatic runtime dependency.

The Fabric layer is for verified datasets, PDF lakes, model weights, CSI sample packs, workflow packs, adapter/plugin packs, benchmark packs, and result/provenance bundles. Data packs and code packs have different safety semantics; code packs require quarantine, explicit consent, sandboxing, and explicit enablement, and must never execute at install time.

Phase 3B adds docs, fixtures, and lightweight standard-library prechecks only. Full Fabric runtime conformance, BitTorrent networking, WebSeed download, signing, keyring verification, catalog serving, install/quarantine runtime, sandboxing, and enablement are future work.

See `docs/content-fabric.md` and `docs/fabric-conformance.md`.

## Phase 4B Fabric Runtime Foundation

Phase 4B adds the first local Fabric runtime primitives without networking, pack download, install, code execution, catalog servers, secrets, external APIs, or runtime dependency on Locus. It implements integer-only JSON validation, deterministic scaffold canonicalization, signing payload construction, SHA-256 digest helpers, path confinement prechecks, license gate prechecks, manifest/keyring/catalog shape validators, and a local CLI check.

Check a local Fabric fixture:

```powershell
python -m somatic fabric check fixtures/fabric/conformance/sample-pack-signed.json
```

At the Phase 4B boundary, Ed25519 cryptographic verification, TUF threshold verification, keyring rotation continuity, BitTorrent/WebSeed transport, catalog HTTP/WS, install/quarantine runtime, sandboxing, explicit enablement, and Locus cross-verification were still future work.

## Phase 4C Fabric Crypto Keyring Foundation

Phase 4C adds optional local Ed25519 signing and verification helpers under the Fabric extra. When the optional crypto backend is available, Somatic can verify a signed keyring's active root threshold and a pack manifest's publisher threshold against local JSON fixtures.

Check a signed local fixture with a keyring:

```powershell
python -m somatic fabric check fixtures/fabric/crypto/signed-code-pack.json --keyring fixtures/fabric/crypto/keyring-signed.json
```

The checked-in crypto fixtures are test vectors only and include non-production private-key material for deterministic tests. They must never be used for real Fabric publishing. Phase 4C still does not add BitTorrent/WebSeed networking, downloads, catalog servers, pack install, code execution, plugin enablement, sandbox runtime, external APIs, or a Locus runtime dependency. The canonicalizer remains a scaffold rather than full RFC 8785 JCS, and keyring rotation continuity plus cross-harness verification remain future work.

## Phase 4D Fabric Locus Interop Preparation

Phase 4D inspects the local Locus implementation at `C:\AI\locus\electron\content-fabric\` and adds Somatic-side preparation docs, a gap analysis, interop fixture placeholders, and a small metadata helper. It does not copy Locus code, import Locus modules, add Locus as a runtime dependency, claim certified interop, add network transport, add catalog servers, download/install packs, or execute code packs.

See [docs/fabric-locus-interop.md](../docs/fabric-locus-interop.md) and [docs/fabric-implementation-gap-analysis.md](../docs/fabric-implementation-gap-analysis.md).

## Phase 4E Fabric Byte-Conformance Gap Closure

Phase 4E closes the first byte-conformance gaps without adding any network, download, install, quarantine, code execution, catalog-server, external API, production-key, or Locus runtime dependency. Somatic now rejects forbidden raw JSON number lexemes before parsing, keeps the signing payload boundary explicit, verifies signed catalog fixtures against trusted publisher keys, evaluates license policy for publish/seed/catalog/install contexts, and verifies keyring replacement continuity with previous active root signatures.

Useful local checks:

```powershell
python -m somatic fabric payload fixtures/fabric/crypto/signed-code-pack.json
python -m somatic fabric check-keyring-rotation fixtures/fabric/crypto/rotation/previous-keyring.json fixtures/fabric/crypto/rotation/valid-rotated-keyring.json
python -m somatic fabric check fixtures/fabric/crypto/signed-code-pack.json --keyring fixtures/fabric/crypto/keyring-signed.json
python -m somatic fabric check fixtures/fabric/crypto/signed-catalog.json --keyring fixtures/fabric/crypto/keyring-signed.json
```

At the Phase 4E boundary, the canonicalizer remained a JCS-parity scaffold and Locus-certified interop still required fixture exchange plus mutual byte verification. Phase 4G.1 later replaces that local canonicalizer for Fabric-supported JSON, but shared Locus certification is still deferred.

## Phase 4F Fabric Mutual Verification

Phase 4F runs local mutual verification against the Locus checkout at `C:\AI\locus\electron\content-fabric\` using test fixtures and existing Locus test/module entrypoints. Locus verified Somatic-generated pack/keyring fixtures, matched the checked signing payload and manifest digests, validated the Somatic catalog shape, and verified the catalog signature through its Ed25519 primitive. Somatic verified Locus-owned pack/keyring fixtures from `C:\AI\locus\tests\fixtures\somatic-fabric\`.

Current result: partial verification, not certified. No Locus files were copied, and no runtime dependency on Locus was added.

See [docs/fabric-mutual-verification-report.md](../docs/fabric-mutual-verification-report.md).

## Phase 4G.1 Fabric JCS Local Vectors

Phase 4G.1 replaces the old sorted-JSON scaffold with local RFC 8785/JCS canonicalization for the Fabric-supported JSON domain: objects, arrays, strings, booleans, null, and non-negative safe integers in `[0, 2^53-1]`. Raw Fabric JSON rejects duplicate object names, invalid surrogate strings, floats, exponents, signs, leading-zero numbers, negatives, and out-of-range integers. Object keys sort by UTF-16 code units, arrays preserve order, canonical output has no insignificant whitespace, and canonical bytes are UTF-8.

Inspect a canonical local fixture:

```powershell
python -m somatic fabric canonicalize fixtures/fabric/jcs/basic-object.json
```

This phase does not run full Locus mutual certification. Locus-certified shared verification remains Phase 4G.3, and BitTorrent/WebSeed transport, catalog servers, pack download, install, quarantine, sandboxing, explicit enablement, external APIs, and production signing remain deferred.

## Phase 4G.2 Fabric Shared Interop Fixtures

Phase 4G.2 adds Somatic-generated shared Fabric fixtures under `fixtures/fabric/interop/shared/` for the next Locus/Somatic certification pass. The set includes a signed test-only code pack, signed test-only data pack, signed keyring, signed catalog, expected digest metadata, and invalid pack/catalog/keyring rejection cases.

Somatic self-certifies the shared fixtures locally:

```powershell
python -m somatic fabric digest fixtures/fabric/interop/shared/shared-pack.json
python -m somatic fabric check-catalog fixtures/fabric/interop/shared/shared-catalog.json --keyring fixtures/fabric/interop/shared/shared-keyring.json
python -m somatic fabric check-shared-fixtures fixtures/fabric/interop/shared
```

The private keys used to create these fixtures are deterministic test vectors in `fixtures/fabric/crypto/` and must never be used for production Fabric signing. This phase does not run Locus mutual verification, copy Locus files, add a Locus runtime dependency, fetch or install packs, quarantine or enable code, start HTTP/WS catalog servers, add BitTorrent/WebSeed networking, use external APIs, or introduce production secrets. Shared Locus/Somatic fixture verification is handled in Phase 4G.3.

## Phase 4G.3 Locus Shared Fixture Certification

Phase 4G.3 verifies the Phase 4G.2 shared fixtures against the local Locus implementation at `C:\AI\locus\electron\content-fabric\`, commit `5f81ee360834dc6451c4ea35d7509325813d9d10`. Locus matched the shared pack, data pack, keyring, and catalog canonical/signing payload digests, verified pack and keyring signatures, validated the catalog shape, verified the catalog signature with its Ed25519 primitive, and rejected the invalid pack, catalog, and keyring fixtures where entrypoints exist.

Current result: shared fixture certification achieved for the Somatic-origin `fixtures/fabric/interop/shared/` set. This is not full Content Fabric runtime certification: Locus-origin companion fixtures, broader edge vectors, BitTorrent/WebSeed transport, catalog servers, pack download, install, quarantine, sandboxing, explicit enablement, external APIs, and production signing remain deferred.

## Phase 5A External Science Integration Intake

Phase 5A maps the next external science systems Somatic may integrate:
PaperQA2, FutureHouse Robin, K-Dense-AI scientific-agent-skills, Harvard
AutoScientists, optional aviary/ldp references, and Boltz-2 planning. No target
repo was locally available under the Phase 5A `C:\AI` search, so this phase does
not claim concrete package entrypoints or licenses.

The phase adds Somatic-owned provider interface scaffolds under
`somatic/providers/`, disabled placeholder provider metadata fixtures, and
adapter-boundary documentation. These additions do not install dependencies,
import external packages, call APIs, fetch models, or enable live provider
runtime.

See [docs/external-science-integrations.md](../docs/external-science-integrations.md),
[docs/adapter-boundaries.md](../docs/adapter-boundaries.md), and
[docs/science-provider-roadmap.md](../docs/science-provider-roadmap.md).

## Phase 5A.1 External Source Staging

Phase 5A.1 stages the target external sources outside the Somatic checkout under
`C:\AI\external-sources\somatic\` for read-only inspection. The staged sources
include PaperQA2, Robin, scientific-agent-skills, AutoScientists, Aviary, LDP,
and the likely Boltz-2 upstream `jwohlwend/boltz`.

This phase still does not install dependencies, run package managers, run setup
scripts, download model weights or datasets, call APIs, modify external repos,
vendor source, or wire runtime adapters.

See [docs/external-source-staging.md](../docs/external-source-staging.md) and
`fixtures/providers/external-source-inventory.json`.

## Phase 5B PaperQA2 Provider Scaffold

Phase 5B inspects the staged PaperQA2 source at
`C:\AI\external-sources\somatic\paper-qa` commit
`d2c3c698fdf06986aa021812ab3186d3696438d8` and adds a disabled optional
PaperQA2 literature provider scaffold in `somatic/providers/paperqa2.py`.

The adapter imports without PaperQA2 installed, uses lazy availability
detection, and has deterministic fake-backed mode for tests. Real PaperQA2
search, indexing, metadata-provider calls, and evidence extraction remain
future work and fail closed in this phase. The basic install still has no
PaperQA2 dependency, and no health or private user data should be sent to an
external literature provider without explicit configuration and consent.

See [docs/paperqa2-source-inspection.md](../docs/paperqa2-source-inspection.md)
and [docs/paperqa2-adapter.md](../docs/paperqa2-adapter.md).

## Phase 5C Scientific Agent Skills Provider Scaffold

Phase 5C inspects the staged `K-Dense-AI/scientific-agent-skills` source at
`C:\AI\external-sources\somatic\scientific-agent-skills` commit
`effb57c5699c1d400ef461a7aa80fc6693939805` and adds a disabled metadata-only
provider scaffold in `somatic/providers/scientific_agent_skills.py`.

The staged source is MIT licensed. The adapter imports without the upstream
skills collection installed, reports local staged-source availability, and
returns deterministic fake-backed skill and database connector metadata. It
does not execute skills, run scanner scripts, install dependencies, call public
databases, or send health/clinical data to external connectors. Real catalog
parsing and any future live connector work require explicit configuration,
consent, and safety review.

See
[docs/scientific-agent-skills-source-inspection.md](../docs/scientific-agent-skills-source-inspection.md)
and
[docs/scientific-agent-skills-adapter.md](../docs/scientific-agent-skills-adapter.md).

## Phase 5D Finch Toolbelt Expansion

Phase 5D expands Finch inside the local Robin sandbox loop with a
standard-library-only analysis toolbelt. It adds CSV parsing, table profiling,
missing value counts, numeric descriptive statistics, simple group summaries,
preliminary dose-response summaries, effect-direction text, mock evidence
quality scoring, and SHA-256 provenance hashing.

Robin mode now emits:

- `artifacts/finch_toolbelt_summary.json`
- `artifacts/table_profile.json`
- `artifacts/dose_response_summary.json`
- `artifacts/analysis_provenance.json`

This is local fixture analysis only. pandas, scipy, numpy, scanpy, biopython,
and other package-backed analysis tools remain future optional extras. Outputs
are deterministic research artifacts, not medical advice, not clinical
evidence, and not real scientific conclusions. Real lab/scientific validation
remains future work.

See [docs/finch-toolbelt.md](../docs/finch-toolbelt.md).

## Phase 5G Finch Optional Extras Scaffold

Phase 5G adds a disabled, fake-backed Finch optional-extras provider scaffold.
It reports lazy local availability for pandas, scipy, numpy, scanpy, and
biopython without importing those packages or making them part of the basic
install.

Robin-loop runs still use the standard-library Finch toolbelt. The only runtime
surface added in this phase is optional provider status under
`artifacts/finch_toolbelt_summary.json`. Real package-backed analysis,
bioinformatics interpretation, clinical interpretation, network access, and
external provider execution remain disabled.

See [docs/finch-extras.md](../docs/finch-extras.md).

## Phase 5E AutoScientists TeamOrchestrator Mapping

Phase 5E inspects the staged AutoScientists source at
`C:\AI\external-sources\somatic\AutoScientists` commit
`c71a92343b9a488ed10134be805845b9473ad18f` as reference material only. No
license file was found in the staged source, so Somatic does not copy, import,
vendor, execute, install, or depend on AutoScientists.

The local TeamOrchestrator now records deterministic lifecycle stage,
confidence estimate, critique gate result, stall/no-stall reason, blackboard
contribution, evidence spend decision, reorganization trigger, next team
action, and future provider hook metadata. The optional AutoScientists provider
scaffold is disabled, fake-backed, reference-only, and fails closed for live
runtime requests.

See
[docs/autoscientists-source-inspection.md](../docs/autoscientists-source-inspection.md)
and [docs/autoscientists-mapping.md](../docs/autoscientists-mapping.md).

## Phase 5F FutureHouse Robin Stack Mapping

Phase 5F inspects staged FutureHouse Robin, Aviary, and LDP sources as
reference material only:

- Robin: `C:\AI\external-sources\somatic\robin` at
  `4a5cce310f3bc7663a67117db88af43b84733ffe`
- Aviary: `C:\AI\external-sources\somatic\aviary` at
  `826577f332a02ec2f5883cdb042fb12f14b4c7b3`
- LDP: `C:\AI\external-sources\somatic\ldp` at
  `d49850ff3addb8369df062d345ea99991b7b200c`

All three staged sources have Apache-2.0 license files. Somatic does not copy,
import, vendor, execute, install, or depend on those runtimes. The new Robin
provider scaffold is disabled, fake-backed, reference-only, and maps Robin
Crow/Falcon/Finch concepts, Aviary-like environments, and LDP-like rollouts to
Somatic-owned interfaces.

See [docs/futurehouse-robin-mapping.md](../docs/futurehouse-robin-mapping.md).

## Phase 6A Boltz Biomodel Provider Scaffold

Phase 6A inspects the staged Boltz source at
`C:\AI\external-sources\somatic\boltz` commit
`b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc` and records the MIT license found
in the source. Somatic now has a disabled Boltz-2 biomodel planning scaffold in
`somatic/providers/boltz.py`.

The scaffold imports without Boltz installed, reports lazy optional dependency
availability, returns deterministic fake-backed `BiomodelPlan` and
`BiomodelResult` metadata, and maps mock results into Evidence Bus
`RawEvidence` / `StructuredVerdict` records. It does not run Boltz, import the
Boltz package, download model weights or molecule data, call MSA servers, use
GPU runtime, or make scientific/clinical/lab conclusions.

Future real biomodel mode requires explicit opt-in, model/download/MSA consent
gates, resource checks, provenance and output hashes, and research-only safety
review.

See [docs/boltz-source-inspection.md](../docs/boltz-source-inspection.md),
[docs/biomodel-provider-boundary.md](../docs/biomodel-provider-boundary.md), and
[docs/boltz-adapter.md](../docs/boltz-adapter.md).

## Phase 6B/6C/6D In-Silico Biomodel Workflow

Phase 6B wires the fake-backed Boltz biomodel planning path into the local mock
run artifact system. Phase 6C adds biomodel safety gates and consent/readiness
artifacts to the same fake-backed path. Phase 6D adds deterministic biomodel
artifact provenance and planning-only Fabric `data` pack mapping.

Run the in-silico fixture:

```powershell
python -m somatic run fixtures/workflows/valid-in-silico-screening.yaml
```

The command preserves the baseline run artifacts and adds biomodel request,
readiness report, consent record, plan, result, Evidence Bus mapping, raw
evidence, structured verdict, provenance bundle, pack plan, and summary JSON
artifacts. It remains fake-backed planning only: no Boltz import or execution,
no model weights or MSA downloads, no MSA server or network calls, no
GPU/runtime execution, no real structure or affinity prediction, no Fabric
publishing/transport/signing/install/execution, and no medical, lab, clinical,
or scientific conclusion.

Phase 6C records deterministic block reasons for disabled runtime execution,
model downloads, MSA server use, network calls, GPU execution, missing resource
review, missing provenance planning, missing user consent, and missing
research-only acknowledgement. Real biomodel runtime remains future-only even
if a negative test fixture marks policy flags enabled.

Phase 6D records the current run's biomodel artifact hashes and recommends a
future Fabric `data` pack candidate of type `dataset` or `document`. It does
not create a Fabric manifest, signed pack, catalog entry, torrent, WebSeed,
install target, code pack, or executable file.

See [docs/in-silico-screening.md](../docs/in-silico-screening.md) and
[docs/biomodel-safety-gates.md](../docs/biomodel-safety-gates.md). See
[docs/biomodel-provenance.md](../docs/biomodel-provenance.md) for the Phase 6D
provenance and Fabric pack-planning boundary.

## Phase 7A Sensor N-of-1 Scaffold

Phase 7A adds a standard-library sensor provider boundary and a deterministic
sandbox sensor provider for `mode: n-of-1`.

Run the n-of-1 fixture:

```powershell
python -m somatic run fixtures/workflows/valid-n-of-1.yaml
```

The command preserves the baseline run artifacts and adds sensor stream plan,
sensor observations, sensor feature set, sensor Evidence Bus mapping, baseline
placeholder, and n-of-1 summary JSON artifacts.

This mode is fake-backed sensor planning only. It does not access hardware,
run WiFi CSI capture, open camera/microphone/audio/wearable/BLE/WiFi/thermal
devices, call networks, export personal data, perform real monitoring, or make
diagnosis, treatment, clinical, or emergency-triage claims. Real sensor mode is
future work and requires explicit user consent, local-first privacy policy,
retention/export controls, and safety review.

See [docs/sensor-provider-boundary.md](../docs/sensor-provider-boundary.md),
[docs/n-of-1-workflow.md](../docs/n-of-1-workflow.md), and
[docs/sensor-privacy-boundary.md](../docs/sensor-privacy-boundary.md).

## Phase 7B WiFi CSI Planning Scaffold

Phase 7B adds a standard-library WiFi CSI planning scaffold under
`somatic.sensors.csi` and CSI-specific fixtures under `fixtures/sensors/csi/`.
The n-of-1 mock run now records CSI planning metadata in `sensor_feature_set`,
`sensor_evidence_record`, and `n_of_1_summary` artifacts without replacing the
generic sensor fields.

This is fake-backed planning only and disabled by default. It does not access
WiFi hardware, ESP32 devices, RTL8812AU adapters, routers, drivers, monitor
mode, packet capture, WiFi device probing, raw RF/CSI data, camera/microphone
devices, BLE, wearables, networks, or external APIs. Raw RF/CSI data is
local-first and private by default; Phase 7B collects, retains, and exports
none. It makes no medical, clinical, diagnosis, treatment, monitoring, or
emergency-triage claim.

Phase 8A later stages and inspects the named WiFi CSI references outside the
Somatic checkout. They remain reference-only and are not runtime dependencies.
`ruvnet/RuView` is conditional reference-only after Phase 10G reassessment and
must not be copied, imported, executed, depended on, or treated as validated
runtime capability.

See [docs/wifi-csi-scaffold.md](../docs/wifi-csi-scaffold.md) and
[docs/wifi-csi-reference-map.md](../docs/wifi-csi-reference-map.md).

## Phase 8A WiFi CSI Source Staging

Phase 8A stages WiFi CSI reference sources under
`C:\AI\external-sources\somatic\wifi-csi\` for read-only source review:

- `NTUMARS/Awesome-WiFi-CSI-Sensing` at commit
  `fc8e21f4392d16fa110f1e00952d7f6bfd8f78c0`, MIT via root `LICENSE`.
- `thu4n/ESP32-WiFi-Sensing` at commit
  `9ebd9204cd695e9772a78f466532a7a99c790a67`, root license unclear; nested
  `esp32-csi-tool/LICENSE` is MIT.
- `MaliosDark/wifi-3d-fusion` at commit
  `0c0f99e6af9fa1a22d850c45b8f23aa75f34f328`, license requires review because
  `LICENSE` says Apache-2.0 while the README badge says GPL-2.0 and vendored
  third-party folders add separate license surfaces.

This phase does not install dependencies, run package managers, run staged
code, access WiFi hardware, flash ESP32 devices, open serial ports, read or
write SD cards, start MQTT or UDP listeners, reconfigure WiFi interfaces, use
monitor mode, run packet capture, use `tcpdump`/`tshark`/`aircrack-ng`, vendor
source, or implement real CSI runtime.

WiFi CSI, RSSI, pcap, serial CSI logs, SD-card CSVs, raw RF/CSI, derived
features, embeddings, ReID sequences, pose outputs, skeleton outputs, and
activity labels are sensitive by default. Future real WiFi CSI use requires
explicit consent from the operator, intended subject, and all potentially
affected people in the sensing area, plus local-first storage, retention/export
controls, redaction review, privacy review, safety review, human review, and a
separate opt-in configuration.

Upstream references to diagnosis, treatment, clinical interpretation, medical
monitoring, fall detection, emergency triage, respiration or heart-rate
monitoring, identity recognition, surveillance, covert monitoring, production
readiness, ReID, continuous learning, or validated pose estimation are research
context only and are not Somatic capabilities or validation claims.

See [docs/wifi-csi-source-staging.md](../docs/wifi-csi-source-staging.md) and
`fixtures/sensors/csi/csi-reference-inventory.json`.

## Phase 8B-8I WiFi CSI Parser, Replay, Scoring, Batch Readiness, Public Examples, And Compatibility

Phase 8B adds a standard-library parser scaffold for local fake/sample WiFi CSI
fixtures only:

- `somatic.sensors.csi_formats`
- `somatic.sensors.csi_parser`
- `fixtures/sensors/csi/sample-esp32-csi.csv`
- `fixtures/sensors/csi/sample-amplitude-phase.csv`
- `fixtures/sensors/csi/sample-csi-jsonl.jsonl`
- `fixtures/sensors/csi/invalid-csi-malformed.csv`

Phase 8C freezes the scaffold into a stable offline parser contract with
structured parse errors, repo-relative report paths, deterministic replay tests
over every local CSI fixture, edge-case fixtures for blank lines, unknown
columns, short vectors, invalid JSONL rows, mixed rows, and unsupported
extensions, plus a sanitized `python -m somatic csi-parse <fixture>` report
path.

Phase 8D routes n-of-1 CSI fixture refs through
`SandboxSensorProvider.replay_csi_fixtures(...)`. The provider reads local
fixture files through the Phase 8C parser contract and returns sanitized parser
report/summary metadata only. Public replay outputs use neutral fixture refs and
format classes when a local filename or format label would expose raw signal
component terms.

Phase 8E adds `somatic.sensors.csi_scoring`, a deterministic evidence scoring
contract over sanitized replay metadata only. The score uses parser status,
fixture status counts, fixture count, frame/sample counts, malformed-row count,
warning/error counts, format coverage, and parser contract version. It emits
neutral `evidence_quality` and `replay_integrity` scores on a bounded 0-100
scale. The score is explainable replay-integrity metadata, not a signal-quality,
health, vital-sign, monitoring, diagnostic, treatment, or medical claim.

Phase 8F adds `somatic.sensors.csi_batch`, a deterministic batch evaluator for
tournament/readiness reports. It accepts configured local CSI fixture groups,
routes each group through `SandboxSensorProvider.replay_csi_fixtures(...)`, and
aggregates sanitized scoring metadata such as group counts, status counts,
format coverage, warning/error counts, `aggregate_evidence_quality`, and
`aggregate_replay_integrity`. Batch readiness uses the minimum group score to
fail closed when any group rejects. It remains metadata-only and does not change
`SCORE_FIELDS`, candidate scores, Elo ratings, bracket selection, winner
selection, or final rankings. Batch output is bounded by small group/ref limits
and does not export fixture refs or filenames.

Phase 8G adds `somatic.sensors.csi_evidence_pack`, a deterministic sanitized
evidence-pack export contract for parser, replay, scoring, and batch readiness
metadata. The portable artifact is `artifacts/csi_evidence_pack.json`; it
contains contract versions, counts, status counts, bounded score summaries,
closed boundary flags, and a deterministic `pack_fingerprint` only.

Phase 8H adds public example manifests and release-readiness docs under
`examples/wifi-csi-demo/` and `docs/wifi-csi-public-examples.md`. The examples
show how to run the parser CLI, n-of-1 CSI replay with evidence-pack export,
and tournament CSI batch readiness metadata from a fresh clone without adding a
new runtime path.

Phase 8I hardens `somatic.sensors.csi_evidence_pack` with a v1 compatibility
reader/classifier and checked-in sanitized pack examples. Compatibility results
use the stable categories `compatible`, `incompatible`, `unsupported_version`,
and `malformed`; missing required fields fail closed, future contract versions
are not coerced, generated-from IDs/versions must match v1, and additive
unknown fields are accepted only as simple safe scalar metadata when the pack
still passes the portable privacy boundary and deterministic fingerprint check.

When the n-of-1 fixture includes CSI replay refs, the mock runner writes
`artifacts/csi_parser_report.json` and
`artifacts/csi_parsed_summary.json`. These are parser metadata summaries only,
not signal-processing outputs. Their additive `csi_evidence_scoring` metadata is
copied into the n-of-1 evidence record and summary so workflow and
tournament-style consumers can inspect sanitized replay quality without new raw
data surfaces. They do not expose raw sample arrays or raw signal-value keys
such as `samples`, `raw_values`, `real`, `imag`, `amplitude`, `phase`, or
`rssi`; they also do not expose source IDs or absolute paths.

This phase has no serial, no MQTT, no UDP, no pcap, no monitor mode, no live
capture, no hardware access, no WiFi device probing, no network calls, no
optional dependencies, no vital-sign inference, and no medical, clinical,
diagnosis, treatment, monitoring, or emergency-triage claim. Future real parser
support requires explicit consent, source-license review, cleared test
fixtures, privacy review, safety review, hardware review, retention/export
controls, and separate opt-in configuration.

Quick public verification from the repository root:

```powershell
python -m somatic csi-parse sample-esp32-csi.csv --repo-root .
python -m somatic run fixtures/workflows/valid-n-of-1.yaml --runs-dir runs/examples --run-id run-csi-n-of-1-example
python -m somatic run fixtures/workflows/valid-hypothesis-tournament.yaml --runs-dir runs/examples --run-id run-csi-tournament-example
```

See [docs/wifi-csi-data-formats.md](../docs/wifi-csi-data-formats.md),
[docs/wifi-csi-parser.md](../docs/wifi-csi-parser.md), and
[docs/wifi-csi-public-examples.md](../docs/wifi-csi-public-examples.md).

## Phase 9E Sensor Evidence Extension Template

Phase 9E adds a public extension template for sanitized fixture-only
sensor-evidence providers. The template documents provider module shape,
evidence-pack contract shape, registry entry fields, fixture config, artifact
naming, deterministic fingerprinting, compatibility expectations, and the
privacy/non-goal checklist.

`toy-counter-fixture` is the third provider and the concrete template proof. It
reads tiny checked-in toy CSV fixtures and exports only count/status metadata in
`artifacts/toy_counter_evidence_pack.json` when explicitly configured by an
example/test workflow. It is standard-library only, fixture-only, offline,
metadata-only, not ranking input, and does not change CSI or environment pack
shapes, artifact names, compatibility behavior, or fingerprints.

See [docs/sensor-evidence-extension-template.md](../docs/sensor-evidence-extension-template.md)
and [examples/sensor-evidence-demo/](../examples/sensor-evidence-demo/).

## Phase 9F Provider Discovery And Workflow Validation CLI

Phase 9F exposes the fixture-only sensor-evidence registry through CLI
preflight commands:

```powershell
python -m somatic sensor-evidence providers
python -m somatic sensor-evidence providers --format json
python -m somatic sensor-evidence validate --workflow examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml
python -m somatic sensor-evidence validate --workflow examples/sensor-evidence-demo/toy-counter-fixture-workflow.yaml --format json
```

Provider discovery lists sanitized registry metadata only: provider ID,
evidence kind, contract version, artifact name, fixture-only status, fixture
mode labels, and supported fixture formats. Workflow validation checks local
workflow YAML before runtime dispatch and returns sanitized category codes for
unknown providers, unsafe refs, excessive counts, live/device/network fields,
credential-like fields, and unsupported fixture modes.

These commands do not read fixture bodies, instantiate providers, create run
artifacts, call networks, export payload bodies, affect rankings, or enable live
sensors. `python -m somatic doctor` also summarizes the registered provider
count and registry validation boundary without printing fixture refs or private
config values.

## Phase 9G Provider Manifest Snapshot

Phase 9G makes `python -m somatic sensor-evidence providers --format json` the
stable sanitized provider manifest contract generated from
`somatic.sensors.registry`. The manifest records the contract version, manifest
kind, provider count, stable provider order, provider/evidence kinds, contract
identities, artifact names, fixture-only flags, fixture mode labels, supported
fixture formats, and public boundary labels.

The checked-in snapshot
`fixtures/providers/sensor-evidence-provider-manifest-v1.json` is a drift guard
for registry metadata. Future provider additions or intentional public metadata
changes should update that fixture, docs, and tests together. The manifest does
not read fixture bodies, print private refs, include provider/parser internals,
create run artifacts, change evidence-pack JSON, alter fingerprints, or affect
tournament rankings, Elo, brackets, winners, scoring, reports, or Fabric plans.

## Phase 9H Through 11D Evidence And Adapter Checkpoint

Phase 9H adds the release-summary closeout for the Phase 8C through 9G
sensor-evidence subsystem. Phases 10A through 10I add document evidence,
baseline cleanup, optional Fabric dependency cleanup, operational document
surfaces, cross-domain evidence helpers, document and WiFi CSI adapter
boundaries, the shared real-mode readiness gate, and shared safety invariants.
Phase 10J records the checkpoint for future real-mode planning. Phase 11A adds
contract/spec-only future real-mode requirements for document ingestion and RF
booth / WiFi CSI review surfaces without enabling runtime behavior. Phase 11D
adds lifecycle audit records and decision metadata around those preflight
dossiers while keeping real runtime disabled. See
[docs/phase-9h-release-summary.md](../docs/phase-9h-release-summary.md),
[docs/phase-10-checkpoint.md](../docs/phase-10-checkpoint.md),
[docs/phase-11a-real-mode-contract-specs.md](../docs/phase-11a-real-mode-contract-specs.md),
[docs/phase-11b-review-record-fixtures.md](../docs/phase-11b-review-record-fixtures.md),
[docs/phase-11c-preflight-dossiers.md](../docs/phase-11c-preflight-dossiers.md),
[docs/phase-11d-dossier-lifecycle.md](../docs/phase-11d-dossier-lifecycle.md),
and the
machine-readable summary at
`fixtures/reports/sensor-evidence-subsystem-summary-v1.json`.

The checkpoint is documentation and release evidence only. It does not add
providers, change evidence-pack shapes, alter fingerprints, affect runtime
scoring, enable ingestion, enable hardware access, run models, or change
tournament rankings, Elo, brackets, winners, reports, or Fabric plans.

Phase 11A uses `somatic.safety.phase11_contracts` to describe the future
document metadata staging, parser boundary, artifact privacy, license/source
review, RF booth topology metadata, consent/privacy, hardware, model artifact,
and network policy contracts. Every Phase 11A contract status remains
planning-only with `runtime_stage` set to `not-implemented` and execution
permitted false.

Phase 11B adds deterministic review-record fixtures and fail-closed validators
for consent, license/source, privacy, hardware, model artifact, dependency, and
network policy review records. Completed review records can satisfy planning
gate counts, but they still report `execution_permitted: false`,
`real_mode_runtime_enabled: false`, and `runtime_stage: not-implemented`.

Phase 11C adds deterministic sanitized preflight dossiers over the Phase 11A
specs and Phase 11B review records. Dossiers report packet ids, fingerprints,
per-gate status, and blocking reasons for planning review only; they still
report `execution_permitted: false`, `real_mode_runtime_enabled: false`, and
`runtime_stage: not-implemented`.

Phase 11D adds deterministic lifecycle records, sanitized dossier comparisons,
reviewer signoff metadata, and explicit audit decision records. A `no-blockers`
signoff or `all-gates-reviewed-runtime-disabled` decision remains planning
evidence only and still reports `execution_permitted: false`,
`real_mode_runtime_enabled: false`, and `runtime_stage: not-implemented`.

Phase 12A adds a runtime authorization design charter under
`somatic.safety.phase12_contracts`, sourced from the Phase 11M governance
closeout and Phase 11L runtime gap ledger. It defines future required gates as
metadata only. It does not satisfy any gate and still reports
`authorization_status: not-authorized`, `execution_permitted: false`,
`real_mode_runtime_enabled: false`, and `runtime_stage: not-implemented`.

See [docs/phase-12a-runtime-authorization-design-charter.md](../docs/phase-12a-runtime-authorization-design-charter.md).

Phase 12B adds a runtime authorization record candidate contract under
`somatic.safety.phase12_contracts`, sourced from the Phase 12A design charter.
It defines the future request/decision record shape as metadata only. It does
not approve, grant, or permit runtime and still reports
`authorization_status: not-authorized`, `decision_status: not-submitted`,
`grant_status: no-grant`, `execution_permitted: false`,
`real_mode_runtime_enabled: false`, and `runtime_stage: not-implemented`.

See [docs/phase-12b-runtime-authorization-record-candidate.md](../docs/phase-12b-runtime-authorization-record-candidate.md).

## Phase 7C Personal Baseline Graph Scaffold

Phase 7C adds a standard-library personal baseline graph scaffold under
`somatic.memory.baseline` for the fake-backed `n-of-1` runtime. The mock run now
writes `personal_profile.json`, `baseline_graph.json`, and
`baseline_comparison.json` artifacts alongside the existing sensor artifacts.

The baseline comparison is deterministic local placeholder matching only. It
uses `within_baseline`, `outside_baseline`, and `insufficient_data` statuses for
the fixture categories `respiratory_rate`, `movement_score`,
`sleep_state_estimate`, `posture_state`, `csi_confidence`,
`environmental_context`, and `notes_placeholder`.

This is a fake-backed local baseline scaffold only. It loads no real health
data, performs no real profile storage, uses no database or external memory,
exports no personal health data, and makes no medical advice, diagnosis,
treatment, clinical, monitoring, or emergency-triage claim. Future real
baseline storage requires explicit local storage consent, data-locality review,
local-first privacy controls, privacy review, safety review, human review,
retention/export controls, and separate opt-in configuration.

See [docs/personal-baseline-graph.md](../docs/personal-baseline-graph.md) and
[docs/baseline-privacy-boundary.md](../docs/baseline-privacy-boundary.md).

## Phase 7D N-of-1 Intervention Tag Scaffold

Phase 7D adds a standard-library n-of-1 intervention tagging scaffold under
`somatic.memory.intervention`. The mock run writes `intervention_tag.json`,
`intervention_context.json`, `response_evaluation_plan.json`, and
`mock_intervention_ledger.json` artifacts alongside the existing sensor and
fake-backed local baseline artifacts.

This is mock intervention metadata only. It creates fake-backed intervention
tags and a response evaluation plan summary for future planning, but no
recommendation, no prescription, no treatment recommendation, no medical
advice, no medication action, no clinician action, no effectiveness claim, no
real monitoring, and no reminders, automation, or scheduling. Medication
placeholder disabled and clinician review placeholder disabled are disabled
metadata only.

Future real intervention use requires explicit consent, human/clinical review,
local storage controls, safety gates, and no emergency-triage substitution.
Future real sensor mode requires explicit user consent, local-first privacy
policy, retention/export controls, and safety review. Future real baseline
storage requires explicit local storage consent, data-locality review,
local-first privacy controls, privacy review, safety review, human review,
retention/export controls, and separate opt-in configuration.

See [docs/n-of-1-intervention-tags.md](../docs/n-of-1-intervention-tags.md).

## Phase 7E N-of-1 Response Evaluation Scaffold

Phase 7E adds a standard-library fake-backed response evaluation scaffold under
`somatic.memory.response_evaluation`. The mock run writes
`follow_up_observation_window.json`, `follow_up_sensor_snapshot.json`,
`response_comparison.json`, and `response_evaluation_summary.json` artifacts
alongside the existing sensor, baseline, and intervention artifacts.

This is fake-backed local research-only planning only: mock/offline,
local-only, research-only, sandbox-only. The response comparison uses fixture
trend labels only (`toward_baseline`, `away_from_baseline`, `unchanged`,
`insufficient_data`). No intervention effectiveness is claimed. It provides no
effectiveness claim, no recommendation, no prescription, no treatment
recommendation, no medical advice, no medication action, no clinician action,
no diagnosis, no emergency triage, no real monitoring, and no reminders,
automation, notification, or scheduling.

Future real response evaluation requires explicit consent, human/clinical
review, local storage controls, privacy/safety gates, real
scheduling/monitoring safety review, and no emergency-triage substitution.

See [docs/n-of-1-response-evaluation.md](../docs/n-of-1-response-evaluation.md).

## Phase 7F N-of-1 Report Packet Consolidation

Phase 7F adds a standard-library consolidated n-of-1 report packet under
`somatic.reports.n_of_1_packet`. The mock run writes
`artifacts/n_of_1_report_packet.json` alongside the existing n-of-1 artifacts.

The packet references the full fake-backed loop: sensor planning, observations,
feature set, Evidence Bus mapping, local baseline placeholder, personal
profile, baseline graph and comparison, mock intervention metadata, follow-up
response evaluation, and `n_of_1_summary.json`. It records SHA-256 hashes for
reproducibility/provenance only.

This packet is fake-backed/local/research-only, not medical advice, not a
medical record, and not a health record. It provides no effectiveness claim, no
recommendation, no prescription, no treatment recommendation, no medical
advice, no diagnosis, no emergency triage, no real monitoring, and no
reminders, automation, notification, or scheduling.

Future real use requires explicit consent, privacy review, safety review,
human review, clinical review where applicable, local-first storage controls,
and retention/export controls.

See [docs/n-of-1-report-packet.md](../docs/n-of-1-report-packet.md).

## Phase 7G N-of-1 Fabric Pack Plan

Phase 7G adds a standard-library, planning-only Fabric data-pack candidate for
the n-of-1 report packet under `somatic.reports.n_of_1_fabric_plan`. The mock
run writes `artifacts/n_of_1_fabric_pack_plan.json` alongside
`artifacts/n_of_1_report_packet.json`.

The plan references the report packet, all report-packet artifact refs, and
artifact hashes. It recommends a future Fabric `data` class with `document` as
the suggested type and `dataset` as the alternate type. It is private-only by
default and creates no Fabric manifest, signed pack, catalog entry, torrent,
magnet, WebSeed, public seed, upload, install target, code pack, or executable
file.

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding,
upload, install, or execution is enabled. No real personal data export,
personal health data export, baseline data export, raw sensor data export, or
raw RF/CSI data export is performed. Future real packaging requires explicit
consent, redaction, license review, privacy review, safety review, human
review, local-first storage controls, retention/export controls, and separate
publication approval.

See [docs/n-of-1-fabric-pack-plan.md](../docs/n-of-1-fabric-pack-plan.md).

## Safety Position

Somatic supports research, decision support, safety-gated reports, and human review. It does not provide diagnosis, treatment, cure, emergency triage, or replacement of clinicians, researchers, lab directors, or institutional review processes.

Clinical and health-related workflows must be reviewed by qualified humans before use. Lab-facing workflows must require explicit operator approval before any real-world action.

## Repository Map

- `docs/` contains architecture, workflow, safety, regulatory, CLI, install, roadmap, source map, and fabric notes.
- `somatic/` contains the Python package and master-plan lane scaffolds.
- `workflows/` contains placeholder workflow manifests.
- `packages/` contains package-level README placeholders for future modules.
- `examples/` contains placeholder demos that will later exercise workflow modes without private dependencies.

See [docs/source-map.md](../docs/source-map.md) for the complete repository map.
See [docs/hypothesis-tournament.md](../docs/hypothesis-tournament.md) for the Phase 2 tournament flow.
See [docs/team-orchestrator.md](../docs/team-orchestrator.md) for the Phase 2.5 team scaffold.
See `docs/robin-loop.md` for the Phase 3A Robin sandbox loop.
See [docs/finch-toolbelt.md](../docs/finch-toolbelt.md) for the Phase 5D Finch toolbelt.
See [docs/finch-extras.md](../docs/finch-extras.md) for the Phase 5G Finch extras scaffold.
See `docs/fabric-conformance.md` for the Fabric runtime and crypto boundary.
See [docs/fabric-locus-interop.md](../docs/fabric-locus-interop.md) for the Locus interop preparation status.
See [docs/fabric-mutual-verification-report.md](../docs/fabric-mutual-verification-report.md) for the Phase 4F mutual verification report.
See [docs/external-science-integrations.md](../docs/external-science-integrations.md) for the Phase 5A external science intake map.
See [docs/external-source-staging.md](../docs/external-source-staging.md) for the Phase 5A.1 staged source inventory.
See [docs/paperqa2-adapter.md](../docs/paperqa2-adapter.md) for the Phase 5B PaperQA2 scaffold.
See [docs/scientific-agent-skills-adapter.md](../docs/scientific-agent-skills-adapter.md) for the Phase 5C scientific-agent-skills scaffold.
See [docs/autoscientists-mapping.md](../docs/autoscientists-mapping.md) for the Phase 5E AutoScientists team mapping.
See [docs/futurehouse-robin-mapping.md](../docs/futurehouse-robin-mapping.md) for the Phase 5F FutureHouse Robin stack mapping.
See [docs/boltz-adapter.md](../docs/boltz-adapter.md) for the Phase 6A Boltz biomodel scaffold.
See [docs/in-silico-screening.md](../docs/in-silico-screening.md) for the Phase 6B/6C/6D fake-backed in-silico workflow.
See [docs/biomodel-safety-gates.md](../docs/biomodel-safety-gates.md) for the Phase 6C biomodel safety gates.
See [docs/biomodel-provenance.md](../docs/biomodel-provenance.md) for the Phase 6D biomodel provenance and Fabric pack-planning boundary.
See [docs/n-of-1-workflow.md](../docs/n-of-1-workflow.md) for the Phase 7A fake-backed sensor n-of-1 workflow.
See [docs/wifi-csi-scaffold.md](../docs/wifi-csi-scaffold.md) for the Phase 7B WiFi CSI planning scaffold and [docs/wifi-csi-source-staging.md](../docs/wifi-csi-source-staging.md) for the Phase 8A source inventory.
See [docs/n-of-1-report-packet.md](../docs/n-of-1-report-packet.md) for the Phase 7F n-of-1 report packet.
See [docs/n-of-1-fabric-pack-plan.md](../docs/n-of-1-fabric-pack-plan.md) for the Phase 7G n-of-1 Fabric pack plan.

## License

The final license is not selected yet. See [LICENSE-DISCUSSION.md](../LICENSE-DISCUSSION.md). Until a final `LICENSE` file is added, do not assume permissions beyond what repository hosting terms provide.
