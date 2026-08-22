# Science Provider Roadmap

Phase 5A creates the external-science intake map and disabled Somatic-owned
provider interfaces. Phase 5A.1 stages read-only external source references
under `C:\AI\external-sources\somatic\` and records them in
`fixtures/providers/external-source-inventory.json`. Later phases can add real
providers without changing the basic install or handing workflow ownership to
external frameworks.

## Phase 5B: PaperQA2 Adapter Scaffold

Status: implemented as a disabled optional scaffold.

Goal: add a disabled literature adapter scaffold for PaperQA2 using staged
source `C:\AI\external-sources\somatic\paper-qa` at
`d2c3c698fdf06986aa021812ab3186d3696438d8`.

Completed work:

- Use the Apache-2.0 staged source inventory and keep source inspection read-only.
- Map the `pqa = paperqa.agents:main` CLI and `PaperSearch`/`GatherEvidence`/`GenerateAnswer` tool concepts without adopting the agent loop.
- Map PaperQA2 operations to `LiteratureProvider.search` and `LiteratureProvider.extract_evidence`.
- Add local fixture tests with fake documents and no external API calls.
- Keep PaperQA2 out of the basic install and disabled unless configured.
- Add `somatic.providers.paperqa2` with lazy availability detection, deterministic mock mode, and fail-closed real mode.
- Record details in `docs/paperqa2-source-inspection.md` and `docs/paperqa2-adapter.md`.

Exit criteria:

- Adapter imports are optional and isolated.
- Standard-library workflows still run without PaperQA2 installed.
- Tests prove no default network, model, or credential surface.

Remaining future work:

- Add an explicit optional install note or extra before any real PaperQA2 execution.
- Map real PaperQA2 index/search/evidence outputs into Somatic artifacts with consent and data-locality gates.

## Phase 5C: Scientific Agent Skills Adapter Scaffold

Status: implemented as a disabled metadata-only scaffold.

Goal: add a disabled skill/database adapter scaffold for
`K-Dense-AI/scientific-agent-skills` using staged source
`C:\AI\external-sources\somatic\scientific-agent-skills` at
`effb57c5699c1d400ef461a7aa80fc6693939805`.

Completed work:

- Inspect and model `skills/*/SKILL.md` metadata without installing or executing skills.
- Map method lookup to `ScienceSkillProvider.lookup` and `ScienceSkillProvider.describe`.
- Treat skill records as planning metadata, not executable tool calls.
- Add fixture skill and connector records for literature, chemistry, clinical trials, protein/target databases, and safety screening metadata.
- Add safety tests that lookup cannot execute tools or call APIs.
- Add `somatic.providers.scientific_agent_skills` with deterministic skill and database connector metadata.
- Record MIT source inspection details in `docs/scientific-agent-skills-source-inspection.md`.
- Record adapter boundaries in `docs/scientific-agent-skills-adapter.md`.

Exit criteria:

- Skill metadata can support workflow planning without runtime adoption.
- Tool execution remains a separate future provider operation.

Remaining future work:

- Add a static frontmatter parser for staged `skills/*/SKILL.md` if broader catalog coverage is needed.
- Keep execution, package installation, and database/API calls behind later explicit configuration, consent, and safety review.

## Phase 5D: Finch Toolbelt Expansion

Status: implemented for local Finch analysis only.

Goal: expand Somatic's existing Robin sandbox loop with a deterministic Finch
toolbelt that analyzes local tabular fixture evidence while keeping the runtime
standard-library only.

Completed work:

- Add `somatic.analysis` modules for CSV parsing, table profiling,
  descriptive statistics, preliminary dose-response summaries, and provenance
  hashing.
- Add `somatic.agents.finch_toolbelt` as the local bridge from sandbox raw
  evidence table refs to deterministic Finch artifacts.
- Add deterministic CSV fixtures under `fixtures/evidence/tables/`.
- Preserve the local Crow/Falcon/Finch loop as Somatic-owned runtime shape.
- Keep pandas, scipy, numpy, scanpy, biopython, external APIs, and network code
  out of the basic runtime.
- Mark outputs as deterministic research artifacts only, not medical advice or
  real scientific conclusions.

Exit criteria:

- Robin mode emits Finch toolbelt summary, table profile, dose-response
  summary, and analysis provenance artifacts.
- Literature-only, hypothesis-tournament, and Robin-loop workflows still run
  without FutureHouse Robin, PaperQA2 real mode, scientific-agent-skills
  execution, or package-backed analysis dependencies.

Remaining future work:

- Static mapping against staged Robin/Aviary source can deepen reference
  alignment later.
- Real lab/scientific validation, package-backed statistics, and richer
  bioinformatics analysis require explicit optional extras, safety review, and
  user configuration.

## Phase 5G: Finch Optional Extras Scaffold

Status: implemented as a disabled optional scaffold.

Goal: add fake-backed provider/status metadata for future Finch package-backed
analysis without adding basic-install dependencies or runtime imports.

Completed work:

- Add `somatic.analysis.extras` for lazy `find_spec` status over pandas, scipy,
  numpy, scanpy, and biopython.
- Add `somatic.analysis.provider.FinchExtrasProvider` with deterministic status
  metadata and fail-closed real-mode requests.
- Add provider fixtures for placeholder and mock-config status.
- Add optional extras status under `finch_toolbelt_summary.optional_extras`.
- Add doctor output for scaffolded provider state, optional dependency
  availability, disabled execution, and active standard-library fallback.

Exit criteria:

- Standard-library workflows still run without optional analysis packages.
- No external API, network, package import, scientific-agent-skills execution,
  PaperQA2 real mode, Robin/Aviary/LDP runtime, Fabric transport, biomodel, or
  sensor runtime is enabled.

Remaining future work:

- Define reviewed package-backed execution paths before using any optional
  analysis package for real computation.
- Add provenance, safety, consent, and data-locality gates before richer
  statistics, bioinformatics, or sequence analysis.

## Phase 5E: AutoScientists TeamOrchestrator Deeper Mapping

Status: implemented as a reference-only scaffold.

Goal: map AutoScientists-style team orchestration to Somatic's local
TeamOrchestrator and provider boundary using staged source
`C:\AI\external-sources\somatic\AutoScientists` at
`c71a92343b9a488ed10134be805845b9473ad18f`.

Completed work:

- Static read-only inspection; no license file was found in the staged source.
- Record team, critique, blackboard, budget, and reorganization concepts.
- Map those concepts to `TeamOrchestrationProvider`.
- Keep critique-before-budget ordering from the current mock TeamOrchestrator.
- Add lifecycle stage, confidence estimate, critique gate result, stall/no-stall
  reason, blackboard contribution, evidence spend decision, reorganization
  trigger, next action, and future provider hook metadata to the deterministic
  TeamOrchestrator artifacts.
- Add fixture tests for plan-only orchestration and disabled live-agent behavior.

Exit criteria:

- The current deterministic TeamOrchestrator remains functional.
- Future live orchestration has explicit safety and configuration gates.

Remaining future work:

- Clarify AutoScientists license status before any source copy, runtime import,
  dependency install, or live provider execution is considered.
- Specify service, secret, data-locality, and consent boundaries before any
  non-mock adapter work.

## Phase 5F: FutureHouse Robin Stack Mapping

Status: implemented as reference-only mapping and provider metadata.

Goal: map FutureHouse Robin, Aviary, and LDP concepts to Somatic's local
Crow/Falcon/Finch, Evidence Bus, and future provider execution-envelope
interfaces using staged sources:

- Robin at `C:\AI\external-sources\somatic\robin`
  commit `4a5cce310f3bc7663a67117db88af43b84733ffe`
- Aviary at `C:\AI\external-sources\somatic\aviary`
  commit `826577f332a02ec2f5883cdb042fb12f14b4c7b3`
- LDP at `C:\AI\external-sources\somatic\ldp`
  commit `d49850ff3addb8369df062d345ea99991b7b200c`

Completed work:

- Verify Apache-2.0 license files in the staged sources.
- Record Robin, Aviary, and LDP read-only source inspection docs.
- Add `somatic.providers.robin` as a disabled, fake-backed, reference-only
  scaffold.
- Add Aviary and LDP provider placeholder fixtures.
- Keep PaperQA2 real mode, Edison, OpenAI, Anthropic, LiteLLM, fhlmi, Robin,
  Aviary, and LDP runtime execution disabled.

Remaining future work:

- Define an explicit optional extra before any real provider runtime is
  considered.
- Design consent, data-locality, secret, safety, and network gates for any
  non-mock adapter.

## Phase 6: Boltz-2 And Biomodel Adapter Planning

Status: implemented as a disabled planning scaffold with a fake-backed
in-silico workflow integration.

Goal: plan biomodel adapters before enabling any model runtime, weight download,
or GPU/cloud execution. The likely Boltz-2 upstream is staged at
`C:\AI\external-sources\somatic\boltz` commit
`b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`.

Completed work:

- Use the MIT-licensed staged `jwohlwend/boltz` source for planning only.
- Document model inputs, outputs, weights, licenses, compute requirements, and limitations.
- Treat `boltz predict`, cache downloads, Hugging Face model/data URLs, optional MSA server calls, and CUDA execution as disabled runtime behavior.
- Add `BiomodelPlan` and `BiomodelEvidenceRecord` to the Somatic-owned boundary.
- Add `somatic.providers.boltz` with lazy availability detection, deterministic fake-backed plan/result metadata, and fail-closed real mode.
- Map mock biomodel result metadata into `RawEvidence` and `StructuredVerdict`.
- Add Boltz provider and biomodel fixtures.
- Add doctor output for staged source, optional dependency availability, disabled downloads, disabled MSA server calls, disabled runtime execution, and disabled GPU execution.
- Add `fixtures/workflows/valid-in-silico-screening.yaml` and a local mock
  runtime branch that writes biomodel request, plan, result, Evidence Bus
  mapping, raw evidence, structured verdict, summary, and report artifacts.

Exit criteria:

- Somatic can represent biomodel work as evidence-linked artifacts.
- No model download, cloud call, or private data release occurs by default.
- `python -m somatic run fixtures/workflows/valid-in-silico-screening.yaml`
  runs fake-backed planning only and preserves the no-runtime/no-download/no-MSA
  boundary.

Remaining future work:

- Add an explicit optional install and runtime implementation before any real Boltz execution.
- Add no-download mode, model provenance checks, cache review, MSA strategy, output hashing, and resource gates.
- Keep biomodel outputs research-only and prevent clinical/lab/efficacy claims.
