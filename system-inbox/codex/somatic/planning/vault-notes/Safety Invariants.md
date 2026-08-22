---
title: Somatic — Safety Invariants
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, safety, invariants]
---

# Somatic — Safety Invariants

Back to [[README]]. See also [[Runtime Blockers]].

## Consistently enforced (verified)
- **Reject-by-default** across all 19 Phase-12 validators. Non-`Mapping` → malformed; missing required field (116 checks) and unknown field (113 checks) → reject; a record is `compatible` only when the error list is empty. Field allowlists are `frozenset`s (103).
- **`execution_permitted` is structurally never `True`** — 0 assignments to True anywhere in `somatic/`; hard-coded `False` even when every review gate passes. Independently confirmed.
- **Core trio set + tested in all 19 phases:** `execution_permitted=False`, `real_mode_runtime_enabled=False`, `runtime_stage="not-implemented"`.
- **Recursive unsafe scanning** of nested maps/lists (privacy terms, URLs, IDs, raw sensor payloads, authorization wording), case-insensitive + substring.
- **Doctor renders every phase** with no `try/except` → a broken invariant crashes loudly.

## Fragile / at-risk
- **F1 — denylists are ungated.** No `CODEOWNERS`; CI runs only `unittest`. One PR can narrow a medical/auth term list *and* its fixtures. → fix in [[Recommended Next Phases|12V]].
- **F2 — no Unicode/NFKC normalization** on unsafe-term scanners; homoglyph / zero-width / fullwidth splitting can evade substring match. `_authorization_wording_count` scans only `lowered`, not `normalized`. → [[Recommended Next Phases|12Y]] (Jules-gated).
- **F3 — doctor completeness is convention, not code.** A future phase in contracts but not wired into `_doctor` is silently absent. → [[Recommended Next Phases|12W]] registry.
- **F4 — invariant constants chained by reference** through ~18 phases; a mid-chain edit propagates silently.
- **F5 — ~13 duplicated term-lists/allowlists** must be hand-synced.

## Surface inconsistencies (not runtime holes)
- **12A omits `grant_status`** (every other phase has `"no-grant"`). Confirmed.
- **12F omits the adapter/provider/model_execution_granted triad.**
- Both still assert `not-authorized` + `execution_permitted=False` → no guarantee lost; normalize as documented deltas in [[Recommended Next Phases|12U]].

## Missing checks
- No NFKC normalization (F2). No programmatic doctor-completeness guarantee (F3). No coverage measurement; ruff/mypy declared but not run in CI.
