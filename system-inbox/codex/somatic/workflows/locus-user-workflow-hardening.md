# Locus User Workflow Hardening

Source spec: `LOCUS_USER_WORKFLOW_SPEC.md` from Locus, dated 2026-06-01.

## Purpose

This workflow converts the Locus end-user first-run → daily-use spec into a Locus Evolution Lab planning, hardening, and evolution target.

The goal is to make Locus onboarding and daily operation:

- guided
- permission-gated
- auditable
- detect-first
- non-destructive
- accessible without 3D
- safe for advanced lanes like Content Fabric, sandbox access, trading, Somatic, and IDE/tool control

## Canonical design rules to preserve

1. **Detect-first, never reinstall**
   - Locus should detect existing tools and offer Connect.
   - Install appears only when genuinely absent and user-approved.

2. **Phase H gates everything**
   - Command, spawn, filesystem, network, trading, browser, and automation actions must be gated and audited.
   - The gate is part of the UX and must be visible to the user.

3. **Sticky safety defaults**
   - Trading is paper-first.
   - Somatic science is display-only with disclaimers.
   - Code packs require consent and sandbox.
   - Sandbox-to-host access is read-only by default.

4. **Motion on interaction only**
   - Respect reduced-motion.
   - 3D is a showpiece, not a dependency.
   - Every workflow needs a 2D fallback.

## Core stage model

| Stage | Name | Core/Advanced | Primary gate |
| --- | --- | --- | --- |
| 0 | Install and first launch | Core | App launch/prereq fallback |
| 1 | Onboarding and orientation | Core | Workspace/project-root registration |
| 2 | Add a tool flow | Core | Connect/install permission + vault token handling |
| 3 | Add agents and multi-AI rooms | Core | Least-privilege agent capability grants |
| 4 | Mission Control and Observe | Core | Pause/resume/approve/deny audited controls |
| 5 | Code search via semble | Core | Workspace-confined indexing/search |
| 6 | Content Fabric packs | Advanced | Signature/hash/license/path/code-quarantine gates |
| 7 | Sandbox-to-host broker | Advanced | Read-only grant by default; writable explicit and audited |
| 8 | Advanced lanes | Advanced | Trading/science/3D/IDE lane-specific gates |

## Planner output format

Each stage must be expanded into:

- trigger
- preconditions
- user steps
- gated actions
- audit events
- success check
- fallback
- evolution metrics
- regression tests

## Hardening targets

### Stage 0 — Install and first launch

Hardening focus:

- native-module/build failure messaging
- low-power/reduced-motion 2D fallback
- theme/skin onboarding resilience

Success tests:

- launch succeeds on clean install
- 2D fallback works when 3D is unavailable
- native prerequisite failure is actionable, not a stack trace

### Stage 1 — Onboarding and orientation

Hardening focus:

- user understands systems, agents, rooms, observe, search, and fabric
- workspace root is registered in place; no forced relocation
- audit records initial workspace registration

Success tests:

- dashboard/home opens with graph populated or fallback state
- project root registration does not move user files

### Stage 2 — Add a tool flow

Hardening focus:

- detect running tools before offering install
- connect-by-endpoint fallback
- vault-token retrieval without visible secret logging
- embedded web UI panel isolation

Initial tool detection list:

- ComfyUI
- Ollama
- LM Studio
- JupyterLab
- code-server
- n8n
- Agent Zero
- Space Agent
- HiClaw / Matrix
- kortex-audio
- Blender bridge
- Somatic
- Multiverse

Success tests:

- detected tool offers Connect, not Install
- absent tool shows guidance only
- token never appears in logs

### Stage 3 — Agents and rooms

Hardening focus:

- builtin agent templates
- cross-talk in shared rooms
- least-privilege capabilities
- gated browser/automation actions

Success tests:

- 2+ agents exchange messages in one room
- agent action request surfaces gate before execution

### Stage 4 — Mission Control and Observe

Hardening focus:

- live task/plan visibility
- terminal mirror containment
- artifact/diff visibility
- tool-call stream visibility
- gated pause/resume/approve/deny controls

Success tests:

- terminal and artifacts show live state
- gated control writes an audit entry

### Stage 5 — Code search via semble

Hardening focus:

- workspace-confined indexing
- active workspace default
- agents call `search` and `find_related`
- result opens at file/line

Success tests:

- query returns ranked results
- clicking result opens correct line
- registered folders only are indexed

### Stage 6 — Content Fabric

Hardening focus:

- data pack integrity auto-route policy
- code pack quarantine -> signature -> explicit consent -> sandbox -> explicit enable
- license and publisher surfacing
- path confinement
- signature/infohash/per-file hash enforcement

Success tests:

- data pack verifies and installs under `installed/<type>/`
- code pack never executes at install
- invalid hash/signature/license/path is rejected

### Stage 7 — Sandbox-to-host broker

Hardening focus:

- read-only folder grants by default
- writable grants explicit and audited
- network toggle visibility
- broad host roots rejected

Success tests:

- tool reads only granted folder
- broader access attempt fails and logs

### Stage 8 — Advanced lanes

Hardening focus:

- trading is paper-first
- live trading requires native dialog, typed phrase, caps, and kill switch
- Somatic science is display-only with verbatim disclaimers
- 3D/Unreal always has Three.js/2D fallback
- IDE hub launches/connects editors through gated pathways

Success tests:

- no advanced lane performs side effects without explicit user approval
- paper/live trading distinction is always visible
- Somatic red-flag escalation is prominent

## Evolution metrics

Use these metrics to evolve the workflow without weakening safety:

| Metric | Target |
| --- | --- |
| Time to first connected tool | Decrease |
| User confusion/fallback rate | Decrease |
| Ungated side-effect count | Must remain zero |
| Visible secret leakage | Must remain zero |
| 2D fallback completion parity | Must match 3D flow |
| Tool detection precision | Increase |
| Install instead of connect false positives | Decrease to zero |
| Content Fabric verification failures caught | Increase during test, zero in happy path |
| Audit completeness | 100% for side-effectful actions |

## First GitNexus/OpenClaw prompt

```text
Use GitNexus/source review on Ardynai/locus only. Do not install tools, run services, create cron jobs, or change live systems. Compare the implemented Locus onboarding/tool-add/Mission Control/search/Content Fabric/sandbox/trading/Somatic flows against `LOCUS_USER_WORKFLOW_SPEC.md`. Output a stage-by-stage gap table: implemented, missing, risky, recommended first fix. Stop after reporting.
```

## First implementation candidates after gap review

1. Add workflow-state tests for all stages 0-5.
2. Add audit-entry assertions for every side-effectful gate.
3. Add 2D fallback parity tests for graph/Mission Control flows.
4. Add Add-a-tool detection tests to ensure existing tools show Connect before Install.
5. Add Content Fabric install/quarantine tests with bad hash, bad signature, bad path, and bad license fixtures.

## Gate

Do not implement or evolve this workflow until the Locus source review maps current implementation coverage. The planner must preserve all safety defaults from the source spec.
