# Somatic — Phase 12T Review & Architecture Plan

**Prepared by:** Fable 5 (review/planning session — no implementation performed)
**Date:** 2026-07-02
**Repo:** `Ardynai/somatic` (private) · local `C:\AI\somatic` · vault `C:\AI\obsidian-mind`
**Method:** GitHub API + `gh` CLI verification, full working-tree mirror analyzed in sandbox, CodeGraph index (5,484 nodes / 19,183 edges), 6 parallel review subagents, independent spot-checks of every high-stakes claim.

> Reading guide: **FACT** = verified against source (file:line, SHA, or API). **REC** = recommendation. Each recommendation is tagged **[safe-now]** (metadata/docs/CI only, no runtime), **[gated]** (changes validator/safety semantics → requires Jules), or **[future]** (requires runtime authorization that does not yet exist). Nothing here was implemented.

---

## 1. Current-state verification

### 1.1 Git refs — all match expected (FACT)

| Ref | Value | Expected | Match |
|---|---|---|---|
| Local `HEAD` (on feature branch) | `9e42a31…` | `9e42a31…` | ✅ |
| Local `main` | `ac4d6226cea63ef3ed17cea68401824acb1e5327` | `ac4d622…` | ✅ |
| `origin/main` | `ac4d622…` | `ac4d622…` | ✅ |
| `git ls-remote origin refs/heads/main` | `ac4d622…` | `ac4d622…` | ✅ |
| GitHub API live `main` | `ac4d622…` | `ac4d622…` | ✅ |
| Worktree | clean (0 dirty lines) | clean | ✅ |
| Current branch | `codex/somatic-phase-12t-fabric-transport-consumer-readiness-intake-boundary` | — | ✅ |

### 1.2 PR #65 (FACT)

| Field | Value |
|---|---|
| State | **OPEN**, **isDraft: true** |
| Mergeable / mergeStateStatus | **MERGEABLE / CLEAN** |
| Head SHA | `9e42a3110a0385836d6fe00f110df0373fe67947` |
| Base | `main` @ `ac4d622…` |
| Diff | **5 files, +2837 / −93** |
| CI | check **`unittest` = pass** (35m30s), run `28536064021` |
| Author | `Ardynai` (human account; `is_bot:false`) |
| Created | 2026-07-01T17:33Z |

**Changed files:** `docs/phase-12t-…md` (+85), `fixtures/reviews/phase-12t-…-v1.json` (+561), `somatic/cli/main.py` (+39), `somatic/safety/phase12_contracts.py` (+1691/−93), `tests/test_phase12t_…py` (+461).

### 1.3 Is PR #65 safe to send to Jules? (FACT + verdict)

**Yes — no blockers.** Phase 12T is genuinely metadata-only and fail-closed (Section 4 + independent spot-checks). It **has not yet been sent to Jules**: across the phase history every implemented phase acquires a *duplicate "APPROVE" PR* as the Jules review artifact (e.g. #64 for 12S, #62 for 12R, #60 for 12Q). **No approval PR exists for 12T yet** → the security/medical-safety gate has not been opened. Because 12T adds validator semantics around future fabric consumption, the PR body itself correctly states Jules review is required before merge. **Recommendation: this PR is ready to route to Jules now.**

### 1.4 The −93 deletions are benign (FACT — independently verified twice)

The 93 deleted lines in `phase12_contracts.py` are a **pure relocation**, not a weakening of any safety check. Independent `comm -23 (removed) (added)` over the diff returns **0 removed-and-not-re-added non-blank lines**; the seven "deleted" helpers (`_phase12a_source_governance_closeout`, `_phase12a_source_runtime_gap_ledger`, `_phase12a_future_required_gates`, `_phase12b_source_design_charter`, `_phase12b_requested_domains`, `_phase12b_required_reviewer_roles`, `_invalid_phase12a_charter_result`) each reappear verbatim, shifted by the 12T insertion. `__all__` changes are additive-only.

---

## 2. Repository map

**Scale (FACT):** 539 tracked files — `fixtures/` 180, `docs/` 114 (107 phase/architecture docs), `tests/` 103, `somatic/` 89, plus `packages/` 15 (placeholder READMEs), `workflows/` 13, `examples/` 13. Runtime is **stdlib-only** (`pyproject.toml` → `dependencies = []`; everything heavy is an optional extra). CI = single `unittest` job + `somatic doctor` + one mock run. `docker-compose.yml` runs with `network_mode: "none"`.

### 2.1 `somatic/` package lanes (FACT)

| Lane | Purpose | Runtime posture |
|---|---|---|
| `core` | Workflow-contract loader, mock-run indirection | mock/offline |
| `cli` | `python -m somatic` surface (`doctor`, `run`, `launch`, `replay`, `sensor-evidence`) | stdlib |
| `safety` | **Fail-closed validators + status surfaces** — `phase11_contracts.py` (10,622 L), `phase12_contracts.py` (22,478 L), `adapter_readiness.py`, `biomodel.py` | metadata-only |
| `evidence` / `evidence_bus` | Evidence records, modalities, sanitized artifact-ref pattern | metadata |
| `agents` | Crow/Falcon/Finch/tournament/orchestrator scaffolds (`STATUS="scaffolded"`) | disabled |
| `engines` | Literature/Robin/Finch/biomodel engine scaffolds | disabled |
| `sensors` | WiFi-CSI + sandbox sensors; "never opens hardware, network, camera, mic, BLE, WiFi" | local-first, disabled |
| `memory` | Fake baseline graph, personal profile, n-of-1 intervention | mock |
| `presence` | `RENDER_ONLY=True`, not on reasoning path | render-only |
| `fabric` | Local pack-manifest / content-addressing / signing / conformance metadata (`RUNTIME_IMPLEMENTED=False`) | **no network** |
| `providers` | Somatic-owned adapter boundaries (biomodel, boltz, literature, paperqa2, robin, sensors, science-skills) | disabled |
| `analysis` | stdlib tables/statistics/dose-response/provenance | pure |
| `reports` | Safety-gated n-of-1 report packet + Fabric pack plan | metadata |
| `simulator` | `REAL_WORLD_ACTIONS_ENABLED=False` | sandbox |

### 2.2 Phase-12 surface shape (FACT)

Every sub-phase 12A–12T (**12J intentionally skipped**; no 12U/13 yet) contributes a symmetric quartet in `phase12_contracts.py` — builder `phase12X_<noun>()`, `phase12X_<noun>_status_summary()`, `validate_phase12X_<noun>()`, `rejected_phase12X_<noun>()` — plus one doc, one `fixtures/reviews/*-v1.json`, one `tests/test_phase12X_*.py`, and doctor wiring. 19 phases × 4 public defs = 76 public defs; 19 frozen `…ValidationResult` dataclasses; ~390 private helpers.

**Doctor/status surface (FACT):** `somatic/cli/main.py::_doctor` (~1,151 lines) hand-imports and prints all 19 Phase-12 summaries + 12 Phase-11 summaries. No orphan (every contracts phase is wired into doctor) — but the wiring is manual, not registry-driven.

---

## 3. Project history (Phase 11 → 12T) — concise

**Phase 0–10 (context):** docs-first skeleton → contract fixtures → stdlib mock runner → monorepo scaffold → offline hypothesis tournament → Robin evidence-bus loop → fabric conformance vs Multiverse v1.0.0 → disabled science-provider scaffolds → biomodel/Boltz scaffold → n-of-1 sensor + baseline graph → WiFi-CSI pipeline → non-sensor evidence domains. Nothing ever executes real work; every runnable path ends fail-closed.

**Phase 11A–11M — planning-governance arc (FACT):** real-mode contract specs → review-record fixtures → preflight dossiers → dossier lifecycle → audit index → handoff → handoff-acceptance → follow-up remediation → follow-up queue → decision closeout → review-trail export → **runtime-authorization gap ledger** → planning-governance closeout. Establishes the review/audit vocabulary reused throughout Phase 12.

**Phase 12A–12T — runtime-authorization design arc (FACT):**

| Phase | Establishes |
|---|---|
| 12A | Runtime authorization **design charter** |
| 12B | Runtime authorization **record candidate** |
| 12C | Visual **supervision** capability profile |
| 12D | Visual **desktop consent gate** requirements |
| 12E | **Physiological sensor** capability profile |
| 12F | **Secure-drop consumer** boundary |
| 12G | **Production-readiness coverage** matrix |
| 12H | **Standalone** production-readiness **ownership map** (revised from "cross-repo handoff") |
| 12I | **Integrative herbal/nutrition** knowledge capability profile |
| 12K | **External compute / quantum** backend capability profile |
| 12L | **Fabric interop / A2A audit** boundary profile |
| 12M | **Specialized model option registry** profile |
| 12N→12S | **Workflow-mode review chain**: registry → safety-gate matrix → activation-request packet → non-authorizing decision record → audit-trail index → chain closeout |
| 12T | **Fabric transport consumer-readiness intake** boundary (PR #65, open) |

**Notable corrections (FACT):** 12H was committed as "cross-repo handoff packet" (`6d0c99a`) then **revised to a standalone ownership map** (`2d18a08`) before merge — a deliberate pull back toward the standalone-first invariant. 12N→12T form a self-contained "review pipeline that authorizes nothing."

---

## 4. Safety-invariant audit

### 4.1 Consistently enforced (FACT — strengths)

- **Reject-by-default across all 19 validators.** Non-`Mapping` → `malformed`; `REQUIRED_FIELDS - set(x)` → missing-field (116 such checks); `set(x) - REQUIRED_FIELDS` → unknown-field (113 checks); a record is `compatible` **only when the error list is empty**. Field allowlists are `frozenset`s (103 of them).
- **`execution_permitted` is structurally never `True`.** Grep of the entire `somatic/` tree returns **zero** assignments to `True`; it is a hard-coded literal `False` in `adapter_readiness.py:199`, `biomodel.py:215`, and every phase status dict — even when all review gates pass. Independently confirmed.
- **Core runtime trio set in all 19 status summaries AND asserted in all 19 test files:** `execution_permitted=False`, `real_mode_runtime_enabled=False`, `runtime_stage="not-implemented"`. Two-layer enforcement (module fails closed itself; tests exercise the real validators).
- **Recursive unsafe scanning** through nested Mappings/lists: `_privacy_violation_count` (blocks URLs, IDs, keys, raw sensor payloads, medical terms) and `_authorization_wording_count` (blocks authorized/granted/permitted-style wording unless allow-listed). Case-insensitive + substring.
- **Doctor renders every phase**, calling summaries **without** `try/except`, so a broken invariant crashes loudly rather than passing silently.
- **Fabric compliance:** zero network imports anywhere in `somatic/` (Section 8).

### 4.2 Fragile / at-risk (FACT — with fix tags)

| # | Fragility | Evidence | Fix |
|---|---|---|---|
| F1 | **Denylists are co-editable with the code they protect and nothing gates them.** No `CODEOWNERS`; CI runs only `unittest`. A single PR can narrow a medical/auth blocked-term list *and* its fixtures together. | no CODEOWNERS (confirmed); `.github/workflows/ci.yml` | **[safe-now]** add CODEOWNERS + CI "denylist golden-snapshot" drift-guard test |
| F2 | **Unsafe-term scanner has no Unicode/NFKC normalization.** Homoglyph / zero-width / full-width splitting (e.g. `gr␣ant`, fullwidth chars) would evade substring matching. `_authorization_wording_count` also scans only `lowered`, not the hyphen/space-`normalized` form (asymmetric with `_unsafe_string_count`), relying on hand-listing both spellings. | `phase12_contracts.py:21739` vs `:21284` | **[gated]** add NFKC normalization + fold both scanners to one normalized pass (Jules — changes validator semantics) |
| F3 | **Doctor completeness is convention, not code.** `_doctor` hand-maintains a 3-site import/assign/print block; a future phase added to contracts but not to `_doctor` would be silently absent from the safety surface. | `cli/main.py:240–422` | **[safe-now]** phase-status **registry** iterated by `_doctor` |
| F4 | **Invariant constants chained by reference through ~18 phases** (grant/authorization statuses). A mid-chain edit propagates silently; only per-phase tests catch drift. | `phase12_contracts.py` constant chain 68→…→1837 | **[gated]** collapse to single authoritative constants |
| F5 | **~13 duplicated term-lists / allowlists** (11 per-phase `_unsafe_semantics_count` scanners + 2 shared) must be hand-synced. | 11 near-identical scanners | **[gated]** shared scanner driven by per-phase data |

### 4.3 Surface inconsistencies (FACT — not runtime holes, but consumer-contract fragility)

- **12A has no `grant_status` key** (independently confirmed: `'grant_status' in 12A fixture → False`; 12T → `True/"no-grant"`). Every other phase carries it. A consumer asserting `grant_status == "no-grant"` uniformly breaks on 12A.
- **12F lacks the `adapter/provider/model_execution_granted` triad** present in the other 18 phases (only carries `network_call_/runtime_adapter_execution_granted`).
- Both still assert `not-authorized` + `execution_permitted=False`, so **no runtime guarantee is lost** — these are symmetry gaps worth normalizing in a future closeout phase.

### 4.4 Missing checks (FACT)

- No NFKC/Unicode normalization on any scanner (F2).
- No programmatic guarantee that every contracts phase is wired into doctor (F3).
- No coverage measurement; ruff/mypy declared in `pyproject.toml` but **never run in CI** (Section 5).

---

## 5. Code-quality audit

**Headline (FACT): `somatic/safety/phase12_contracts.py` is a single 22,478-line module** (542 functions, 0 inline comments). `phase11_contracts.py` adds 10,622 more. Metrics from the code-quality subagent:

| Metric | Value |
|---|---|
| Substantive lines that are exact duplicates of another line | **65.1%** (11,760 / 18,074) |
| Estimated mechanically-repeated fraction of file | **~60–70%** |
| `execution_permitted: False` literal repetitions | 234× (same for `real_mode_runtime_enabled: False`) |
| Sibling validators (12R vs 12T) shared skeleton | ~85–90% identical |
| Type-hint coverage | 97% of functions |
| Docstrings on the 390 private helpers | 0% |
| Exception hygiene | 1 narrow `except (TypeError, ValueError)`; no bare excepts, no silent `pass` |

**Other findings (FACT):**
- **Naming/schema drift.** Function suffixes are uniform, but each phase invents a **bespoke** version key (`<long_noun>_contract_version`) and "kind" key (`charter_kind`, `record_kind`, `profile_kind`, `boundary_kind`, …) — there is **no shared `schema`/`contract_version`/`contract_kind` key**, so a generic consumer can't read version/kind without per-phase knowledge. 12Q's `rejected_` helper drops the `non_authorizing` infix that its builder uses.
- **Tests are copy-pasted per phase** — no `conftest.py`, no shared harness; each test file re-declares a local `_runtime_false_fields()` list that can silently drift from the contract's real flag set.
- **Coverage never measured**; CI uses `unittest` (not pytest), no `--cov`, no threshold; ruff + mypy declared but not enforced.
- **Test gaps:** no upper/mixed-case or Unicode unsafe-term test (the lowercasing path is unverified adversarially); no malformed-type test for count fields (float/bool/negative); no single cross-phase invariant test ("no builder output has any `*_permitted/_granted/_added` flag True").

**Highest-leverage safe refactors (behavior-preserving), ranked (REC):**
1. **[gated]** Extract a generic `validate_contract(record, ContractSpec)` + `somatic/safety/phase12/_common.py`; drive all 19 validators from per-phase data. Collapses ~60–70% of the file. *Gated because it rewrites the safety monolith — must go through Jules with a golden-fixture equivalence test.*
2. **[safe-now]** Phase-status **registry** consumed by `_doctor` (removes the 3-site manual edit; shrinks the 1,151-line function).
3. **[gated]** Split `phase12_contracts.py` into `phase12/{a…t}.py` + thin re-export shim (public import paths unchanged).
4. **[safe-now]** Shared test harness (`conftest.py` + parametrized mixin).
5. **[safe-now]** Add `pytest --cov` with a floor and run the already-declared ruff/mypy in CI.
6. **[gated]** Standardize a shared `schema`/`contract_version`/`contract_kind` key (keep verbose keys as aliases); align 12Q naming; add `grant_status` to 12A.

---

## 6. Architecture gap list

### 6.1 Safe now (metadata / CI / docs — no runtime, no new deps)

- **G1 [safe-now]** Add `CODEOWNERS` (require human review on `somatic/safety/**`, `docs/phase-12*.md`, `fixtures/reviews/phase-12*.json`) — operationalizes the asserted-but-unenforced Jules gate (F1).
- **G2 [safe-now]** CI hardening: run ruff + mypy (already declared) and add `pytest --cov` with a coverage floor; add a **denylist golden-snapshot** test so narrowing a medical/auth term list fails CI.
- **G3 [safe-now]** Phase-12 **closeout / capability-profile master index** phase (see Section 9, recommended next step) — mirrors the 12S closeout pattern for the whole 12A–12T arc; also the natural place to fix the 12A `grant_status` / 12F triad symmetry gaps as *documented* deltas.
- **G4 [safe-now]** Resolve the **dual package taxonomy**: top-level `packages/*` placeholder READMEs use different names (`safety-gate`, `sensor-adapters`) than the live `somatic/*` lanes (`safety`, `sensors`). Either delete the placeholders or add a mapping note.
- **G5 [safe-now]** Trim aspirational README language that implies present-tense capability ("clinical decision-support reports", "BitTorrent/WebSeed content fabric") to "not implemented / gated / consumed externally," matching `CONTRIBUTING.md`.

### 6.2 Medium confidence (structural; behavior-preserving but larger)

- **G6 [gated]** The `validate_contract(spec)` refactor (Section 5 #1) — highest maintainability payoff, but touches safety code → Jules.
- **G7 [safe-now→gated]** Doctor registry (F3) is safe-now on its own; if it changes any status string it becomes gated.
- **G8 [gated]** NFKC normalization of unsafe-term scanners (F2).

### 6.3 Future-only (require runtime authorization that does not exist)

- **G9 [future]** Any consumer runtime for fabric (Section 8), sensors, secure-drop, visual supervision, workflow-mode activation, external compute, or model routing. All are currently metadata contracts; each needs its own explicit enablement + Jules/medical/security review before any code executes.
- **G10 [future]** A semantic (not substring) output classifier as a precondition gate before any free-text medical/nutrition generation — the current keyword scanner cannot catch paraphrased dosing/diagnosis.

---

## 7. Visual / UI recommendations (no implementation; delegation plan)

Somatic is standalone-first and will eventually need **its own UI** (Locus may later provide a more advanced connected layer, but must not be mandatory). None of this is runtime-authorized yet; treat as **design planning**.

**What a standalone Somatic UI should eventually include (future):**
- A **safety/status dashboard** that renders the `doctor` surface visually — per-phase runtime-stage, authorization, grant, execution-permitted, production-ready — as an always-visible "everything is blocked" board. This is the single most valuable first UI because it makes the fail-closed posture legible.
- **Review-chain visualizations** for the 12N→12T workflow-mode pipeline (registry → matrix → packet → decision → audit → closeout) — a read-only audit timeline.
- **n-of-1 / baseline** views (personal profile, intervention tags, response evaluation) — local-first, private-by-default, with prominent "research-only, not medical advice" framing.
- **Capability-profile browser** (12C/12E/12F/12I/12K/12L/12M) showing what each future capability *would* do and what gates block it.
- **Consent-gate UX** (12D) — when a future runtime exists, consent must be an explicit, fail-closed prompt, never implicit.

**Delegation (REC):**
- **Claude Code** (not Codex) for: the dashboard/component system, visual states, accessibility, design tokens, diagrams, and design-to-code. Per the vault Master Plan, the AutoScientists orchestration model itself ships as *Claude Code subagents* — so Claude Code is the natural home for both the visual layer and subagent-style flows.
- **Codex** remains the implementation worker for the metadata/contract/validator phases.
- **Do not** route design-heavy work to Codex by default.

---

## 8. Fabric integration recommendation

**Verdict (FACT): COMPLIANT with the standing fabric rule.** Somatic does **not** design or reimplement transport.

- `somatic/fabric/` (12 modules: canonical, catalog, conformance, crypto, digests, fixtures, interop, keyring, manifest, pathing, signing, spec) is **purely local** pack-manifest / content-addressing / Ed25519-signing / conformance metadata. **Zero** network imports (`socket|http|urllib|requests|aiohttp|httpx|asyncio|websocket|libtorrent`) — independently confirmed across the whole `somatic/` tree. CodeGraph shows "transport" exists only as `manifest.py::_validate_transport` (validates an infohash/magnet **string**) plus the 12T metadata functions.
- The README's "BitTorrent/WebSeed content fabric" line is **aspirational** and deferred everywhere it appears; there is no transport code. (REC [safe-now]: annotate the README line "consumed from external `@multiverse/fabric-core`; not implemented in Somatic.")
- **12L** marks fabric interop / A2A / codecs / transport **out-of-scope** via `PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS`.
- **12T** records the canonical producer as external (`Ardynai/multiverse → packages/fabric-core` + `fabric-transport-d` loopback sidecar), sets Somatic to `future-consumer-only` / `awaiting-repo-specific-consumer-prompt`, retains existing point-to-point transport, and **fail-closed-blocks** every transport/fabric/sidecar/import/bearer/contentId/payload action via `PHASE12T_BLOCKED_ACTIONS` (37 labels). Somatic's designated future path is `non-js-sidecar-consumer` (loopback + local contentId re-verify), correct for a stdlib repo.

**Must wait for the Multiverse consumer prompt (nothing below may be built until `repo_specific_consumer_prompt_received` flips true) [future]:**
`@multiverse/fabric-core` npm import / any JS dependency · `fabric-transport-d` sidecar calls · loopback HTTP client · bearer-token handling · runtime contentId calculation/verification + local re-verify · any payload fetch/write/movement · any transport runtime (content-addressed/chunked/resumable/multi-source/integrity/P2P/DHT/swarm) · retiring the existing point-to-point transport · flipping `fabric_integration_started`/`fabric_runtime_enabled` true.

---

## 9. Suggested next phases

**Immediate question answered:** *Is 12T the right last step before a broader Phase 12 closeout, or should there be one more metadata-only closeout/index phase?* → **Add one more closeout phase (12U).** The 12A–12T arc has grown to 19 capability profiles with no single index, and there are two known symmetry gaps (12A `grant_status`, 12F triad). A closeout mirrors the proven 12S pattern and gives the series a clean cap before any pivot.

| # | Proposed phase | Type | Rationale |
|---|---|---|---|
| **12U** | **Phase 12 capability-profile master index + series closeout** — metadata index over 12A–12T (title, kind, contract_version, blocked-actions count, source refs), re-asserting the runtime-blocked trio for the whole series | **[safe-now]** metadata-only | Natural cap; single source for consumers; document the 12A/12F symmetry deltas |
| **12V** | **Governance-enforcement phase**: add `CODEOWNERS` + CI denylist golden-snapshot + wire ruff/mypy/coverage | **[safe-now]** CI/meta | Turns the asserted Jules gate into an enforced one (F1/G2); no runtime |
| **12W** | **Doctor status registry** refactor (behavior-preserving) | **[safe-now]** if status strings unchanged | Removes F3 fragility; shrinks `_doctor` |
| **12X** | **Contract-validation core** (`validate_contract(spec)` + `phase12/` split), golden-fixture equivalence | **[gated]** Jules | Collapses ~60–70% duplication; must prove identical output |
| **12Y** | **Unsafe-term scanner hardening** (NFKC + normalized single pass + case/Unicode tests) | **[gated]** Jules | Closes F2 bypass surface |
| — | **UI planning track** (dashboard, review-chain viz, capability browser) | **[future]** design → Claude Code | Standalone-first UI seams; no runtime |
| — | **Fabric consumer wiring** | **[future]** blocked | Only after the Multiverse consumer prompt (Section 8) |

**Recommended sequence:** 12U (cap the series) → 12V (enforce governance) → 12W (doctor registry) → then the gated refactors 12X/12Y through Jules → parallel UI planning via Claude Code.

---

## 10. Codex-ready draft prompts

> Drafts only — not executed. Each follows the established one-box, exact-state-aware, safety-gated pattern. **Verify the head SHA is still `ac4d622…` at dispatch time**; if 12T has merged by then, update the base SHA and the "after" state.

### 10.1 Phase 12U — master index + series closeout **[safe-now]**

```
You are Codex, implementing exactly ONE phase in Ardynai/somatic. Do not start any other phase. Do not merge.

PRE-FLIGHT (abort if any check fails; report and stop):
1. git fetch origin; confirm current branch can be created from main.
2. Confirm HEAD == local main == origin/main == `git ls-remote origin refs/heads/main` == ac4d6226cea63ef3ed17cea68401824acb1e5327  (update if 12T/#65 has merged).
3. Worktree clean. Run `python -m somatic doctor` — must pass.

TASK: Implement Phase 12U "Phase 12 capability-profile master index and series closeout" as METADATA-ONLY, fail-closed, standalone-first. It is a non-authorizing index over Phases 12A–12T.
- Branch: codex/somatic-phase-12u-capability-profile-master-index-closeout
- Add exactly: docs/phase-12u-capability-profile-master-index-and-series-closeout.md ; fixtures/reviews/phase-12u-capability-profile-master-index-and-series-closeout-v1.json ; a validator + status_summary + rejected_ quartet in somatic/safety/phase12_contracts.py following the 12S/12T pattern EXACTLY ; doctor wiring in somatic/cli/main.py ; tests/test_phase12u_capability_profile_master_index_and_series_closeout.py
- The index enumerates each phase 12A–12T with: phase_id, title, contract_kind, contract_version, blocked_action_count (where applicable), source_phase_references. It MUST re-assert for the whole series: runtime_stage="not-implemented", authorization_status="not-authorized", grant_status="no-grant", execution_permitted=False, real_mode_runtime_enabled=False, production_ready=False, workflow activation not permitted.
- Document (do NOT silently fix) the known symmetry deltas: Phase 12A omits grant_status; Phase 12F omits the adapter/provider/model_execution_granted triad. Record them as noted-deltas in the index; do not alter 12A/12F behavior in this phase.
- NO runtime, NO network, NO new dependencies, NO fabric wiring, NO model routing. Fail closed on unknown/missing/malformed fields and on any authorization/runtime/production wording.

VALIDATION (run all; paste output): focused 12U unittest; adjacent 12T+12U; full 12A-12U suite; Phase 11A-11M regression; `python -m pytest -q`; `python -m somatic doctor`; changed-file Ruff format+check; changed-file Bandit; `pip-audit --format columns`; `fallow --changed-since origin/main`; `git diff --check`; `git diff --cached --check`.

Then open a DRAFT PR (base main). Do not merge. Do not start 12V. Report PR number, head SHA, file list, and all validation output.
Note in the PR body: Jules review required (adds validator semantics).
```

### 10.2 Phase 12V — governance enforcement (CODEOWNERS + CI guards) **[safe-now]**

```
You are Codex, implementing exactly ONE phase in Ardynai/somatic. Do not merge. Do not start another phase.

PRE-FLIGHT: same exact-SHA / clean-worktree / doctor-pass guard as above.

TASK: Phase 12V "governance enforcement" — no runtime, no product code changes.
- Branch: codex/somatic-phase-12v-governance-enforcement
- Add .github/CODEOWNERS requiring human review for: somatic/safety/**, docs/phase-12*.md, fixtures/reviews/phase-12*.json, .github/workflows/**.
- Extend .github/workflows/ci.yml with SEPARATE non-blocking-to-runtime jobs: `ruff check` + `ruff format --check`; `mypy` (already declared in pyproject); `pytest --cov=somatic --cov-report=term-missing` with a coverage floor set to the CURRENT measured value (measure first, do not lower).
- Add tests/test_safety_denylist_snapshot.py: a golden-snapshot test pinning the medical/auth/fabric blocked-term tuples (PHASE12I blocked_fragments, PHASE12T_BLOCKED_ACTIONS, PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS, PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES) so that narrowing any denylist fails CI. Snapshot the CURRENT values.
- Do NOT change any validator logic or status string. Do NOT add runtime, network, or dependencies (dev-only CI tools are acceptable).

VALIDATION: run existing full unittest + pytest + doctor to prove no behavior change; run the new ruff/mypy/coverage jobs locally; `git diff --check`.
Open DRAFT PR (base main). Do not merge. Report PR number, head SHA, files, output.
Note: touches CI/governance — route to Jules.
```

> 12W/12X/12Y prompts should be drafted after 12U/12V land, because they depend on the then-current main SHA and (for 12X/12Y) on Jules sign-off of the approach.

---

## 11. Handoff summary (paste back to orchestrator)

**Somatic review — Fable 5, 2026-07-02 (review only; nothing implemented, no PR touched).**

- **State verified:** local `main` = `origin/main` = live remote = `ac4d622`; worktree clean. **PR #65 (Phase 12T)** = OPEN/draft/**MERGEABLE/CLEAN**, CI `unittest` **pass**, 5 files +2837/−93.
- **12T verdict:** genuinely **metadata-only & fail-closed** (independently verified). Zero network imports; `execution_permitted` never True; blocks all transport/fabric/sidecar/bearer/contentId/payload actions; retains point-to-point. The **−93 deletions are pure relocation** (0 removed-and-not-re-added lines). **No blocker to Jules.** 12T has **not** been sent to Jules yet — no duplicate approval PR exists. **Recommend routing PR #65 to Jules now.**
- **Fabric:** COMPLIANT with the standing rule — no rebuild, consumer-only path, correctly waiting for the Multiverse consumer prompt.
- **Is 12T the right last step?** Recommend **one more metadata-only phase, 12U** = Phase-12 master index + series closeout (mirrors 12S) before any pivot; it's also where to *document* two known symmetry gaps (12A omits `grant_status`; 12F omits the execution-granted triad — neither loses a runtime guarantee).
- **Top risks (all governance/quality, none are live-runtime holes):** (F1) medical/auth denylists are co-editable with the code and **ungated — no CODEOWNERS, CI runs only unittest**; (F3) `doctor` completeness is hand-maintained, not registry-driven; big one — `phase12_contracts.py` is a **22,478-line monolith, ~60–70% duplicated**; coverage never measured, ruff/mypy declared but not run in CI; unsafe-term scanner has **no Unicode/NFKC normalization** (F2 bypass surface).
- **Recommended next phases:** 12U (index/closeout, safe-now) → 12V (CODEOWNERS + CI ruff/mypy/coverage + denylist golden-snapshot, safe-now) → 12W (doctor registry, safe-now) → 12X (behavior-preserving `validate_contract` refactor, **Jules-gated**) → 12Y (scanner NFKC hardening, **Jules-gated**). Draft Codex prompts for 12U and 12V are ready.
- **UI:** when Somatic reaches its standalone UI, send it to **Claude Code**, not Codex (dashboard of the doctor/fail-closed surface first; review-chain viz; capability browser). Design planning only — no runtime.
- **Workflow hygiene note:** many duplicate "APPROVE"/Jules PRs remain **OPEN** (#50, 49, 46, 44, 42, 40, 33, 31, 28, 26, 22) plus #35 "Cleanup tooling baseline" — the process says close them as superseded; they should be swept.

*Full analysis + Obsidian vault notes accompany this summary.*
