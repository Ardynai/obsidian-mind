# Provider Contracts

Somatic providers are adapters that expose capabilities to workflow manifests. Providers can wrap local models, remote APIs, document stores, biomodel tools, lab systems, sensors, simulators, storage layers, safety gates, fabric catalogs, and report renderers.

Phase 1A defines contracts only. It does not implement provider loading or execution.

## Provider Classes

Provider class ids:

- `llm`: language, reasoning, summarization, and critique providers.
- `literature`: paper, document, citation, and corpus search providers.
- `science-skills`: scientific method, protocol, database, and tool-description providers.
- `robin-planner`: Robin-style planner and analyzer providers mapped through Somatic Evidence Bus artifacts.
- `team-orchestration`: critique, role assignment, evidence-budget, and team-summary providers.
- `biomodel`: biomolecular, cheminformatics, and in-silico modeling providers.
- `lab`: manual, wet-lab, and cloud-lab planning or execution providers.
- `simulator`: sandbox lab and dry-run simulation providers.
- `sensor`: WiFi CSI and other sensor observation providers. In Phase 7A/7B
  this means fake-backed planning metadata or sandbox placeholders only, not
  live capture.
- `storage`: local, remote, catalog, and artifact storage providers.
- `safety`: safety gate and policy evaluation providers.
- `fabric`: pack verification, catalog, and transport metadata providers.
- `report`: report packet generation and export providers.

## Lifecycle

Providers should follow this lifecycle:

1. `discover`: publish provider metadata without secrets.
2. `configure`: accept local configuration references and environment bindings.
3. `validate`: prove required capabilities, permissions, and offline or locality constraints.
4. `run`: execute a declared operation with explicit inputs and scoped permissions.
5. `report`: return artifacts, evidence references, metrics, warnings, and safety notes.
6. `teardown`: release handles, close sessions, and remove temporary state.

Lifecycle methods should be idempotent where practical. Teardown should be safe to call after partial failure.

## Capability Metadata

Provider declarations should include:

- `id`: stable provider id.
- `class`: provider class.
- `name`
- `version`
- `description`
- `capabilities`: capability ids with input and output types.
- `modes_supported`: compatible workflow modes.
- `data_locality`: `local-only`, `remote`, `hybrid`, or `unknown`.
- `determinism`: `deterministic`, `seeded`, `best-effort`, or `non-deterministic`.
- `offline_supported`: boolean.
- `permissions_required`: permission scope ids.
- `secrets_required`: named secret references, never secret values.
- `limits`: rate, size, latency, cost, or safety limits.
- `artifacts_emitted`: artifact kinds.
- `evidence_emitted`: evidence source types.

## Auth and Secrets Boundaries

Provider metadata must never include raw secrets. Configuration may reference secret names, local keychain entries, environment variable names, or user-supplied handles.

Providers must declare:

- Which operations require secrets.
- Whether data leaves the local machine.
- Whether outputs may be retained by the provider.
- Whether user or patient data is accepted.
- Whether a provider can operate in mock or offline mode.

Fixtures must use `auth.type: none` or placeholder secret references only.

## Permission Scopes

Permission scopes should be explicit and narrow. Initial scope ids:

- `read:workflow`
- `read:input`
- `read:evidence`
- `write:evidence`
- `write:artifact`
- `write:report`
- `read:catalog`
- `write:catalog`
- `verify:pack`
- `execute:model`
- `execute:simulation`
- `observe:sensor`
- `plan:lab`
- `request:lab-action`
- `evaluate:safety`
- `export:user-selected`

Real lab actions, live sensor observation, and code-pack execution require
separate explicit enablement beyond ordinary provider configuration. In Phase
7A, `observe:sensor` is future permission vocabulary; mock sensor fixtures use
local fixture reads and sandbox placeholders only. In Phase 7B, WiFi CSI
planning fixtures also disable ESP32, RTL8812AU, routers, adapters, drivers,
monitor mode, packet capture, WiFi device probing, raw RF/CSI collection, and
network calls.
Phase 8D/8F CSI replay and batch readiness are provider-mediated local fixture
metadata paths only; they are not live sensor observation or hardware
operations.

## Mock Provider Expectations

Mock providers should:

- Be deterministic by default.
- Require no secrets.
- Make no network calls.
- Declare fixture inputs and outputs.
- Emit stable artifact ids and timestamps when provided with a seed.
- Exercise the same capability metadata shape as real providers.
- Return warnings when a real provider would require human review, consent, license gates, or approval.
- For sensor providers, explicitly mark live capture, hardware access, network
  calls, remote upload, real monitoring, diagnosis, treatment, and emergency
  triage as disabled.
- For WiFi CSI providers, also explicitly mark packet capture, monitor mode,
  WiFi device probing, raw RF/CSI collection/export, ESP32, RTL8812AU, router,
  adapter, and driver access as disabled.

## Provider Reports

A provider report should include:

- `provider_id`
- `operation`
- `started_at`
- `completed_at`
- `status`: `ok`, `warning`, `blocked`, or `error`
- `artifacts`
- `evidence_refs`
- `warnings`
- `errors`
- `metrics`
- `safety_notes`

Provider reports become part of run artifacts and may be referenced by report packets.
