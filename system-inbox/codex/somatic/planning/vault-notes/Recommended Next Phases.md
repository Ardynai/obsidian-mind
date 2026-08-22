---
title: Somatic — Recommended Next Phases
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, roadmap, phases]
---

# Somatic — Recommended Next Phases

Back to [[README]] · [[Open Questions]]. Tags: **[safe-now]** = metadata/CI/docs, no runtime · **[gated]** = changes safety semantics → [[Jules]] · **[future]** = needs runtime authorization (does not exist yet).

## Recommended sequence
1. **12U — Phase-12 capability-profile master index + series closeout** · **[safe-now]**
   Metadata index over 12A–12T (phase_id, title, contract_kind, contract_version, blocked-action count, source refs) re-asserting the runtime-blocked trio for the whole series. Document (don't silently fix) the **12A `grant_status` omission** and **12F execution-granted-triad omission** as noted deltas. Mirrors the 12S closeout pattern. *Draft Codex prompt ready in review §10.1.*
2. **12V — Governance enforcement** · **[safe-now]**
   Add `CODEOWNERS` (human review on `somatic/safety/**`, `docs/phase-12*`, `fixtures/reviews/phase-12*`, CI); wire **ruff + mypy + `pytest --cov`** (all declared but unused) into CI; add a **denylist golden-snapshot** test so narrowing any medical/auth/fabric term list fails CI. Fixes [[Safety Invariants|F1]]. *Draft prompt in review §10.2.*
3. **12W — Doctor status registry** · **[safe-now]** (gated only if a status string changes)
   Replace the hand-maintained 3-site import/print block with a registry `_doctor` iterates. Fixes [[Safety Invariants|F3]]; shrinks the 1,151-line function.
4. **12X — Contract-validation core** · **[gated]**
   Extract `validate_contract(record, ContractSpec)` + `somatic/safety/phase12/{a…t}.py` + thin re-export shim. Collapses ~60–70% duplication with **identical output** (golden-fixture equivalence). Public import paths unchanged.
5. **12Y — Unsafe-term scanner hardening** · **[gated]**
   NFKC normalization + single normalized scan pass + case/Unicode adversarial tests. Closes [[Safety Invariants|F2]].

## Parallel tracks (not Codex)
- **UI planning** · **[future]** → **Claude Code**: dashboard of the doctor/fail-closed surface first; review-chain viz for [[Workflow Mode Chain 12N-12T]]; capability-profile browser; consent-gate UX. Design only.
- **Fabric consumer wiring** · **[future]**: blocked until the [[Fabric Consumer Boundary|Multiverse consumer prompt]].

## Do NOT (without explicit Josh approval)
Merge/ready/close PRs · start 12U · change source code · add runtime/deps/fabric/model routing · alter CI · reimplement transport.
