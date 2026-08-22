---
title: Somatic — Open Questions
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, decisions, open-questions]
---

# Somatic — Open Questions

Back to [[README]]. Decisions for Josh / the orchestrator. None block PR #65.

## For immediate decision
1. **Route PR #65 (12T) to [[Jules]] now?** Recommended — it's metadata-only & fail-closed, no blocker. It has not yet been sent (no duplicate approval PR exists).
2. **Add a 12U closeout/index phase before any pivot?** Recommended — caps the 19-phase 12A–12T arc and documents the 12A/12F symmetry deltas. → [[Recommended Next Phases]].
3. **Sweep stale approval PRs?** Duplicate "APPROVE"/Jules PRs left OPEN: #50, 49, 46, 44, 42, 40, 33, 31, 28, 26, 22, plus #35 "Cleanup tooling baseline." Process says close as superseded.

## Structural (medium-term)
4. **Standardize a shared `schema` / `contract_version` / `contract_kind` key?** Each phase currently invents bespoke keys → generic consumers can't read version/kind uniformly. Keep verbose keys as aliases.
5. **When to do the big refactor?** `phase12_contracts.py` is 22,478 lines, ~60–70% duplicated. A behavior-preserving `validate_contract(spec)` collapse is high-value but touches safety code → **[[Jules]]-gated** with a golden-fixture equivalence test.
6. **Resolve dual package taxonomy** (`packages/*` placeholders vs `somatic/*` lanes) — delete placeholders or add a mapping note.

## Product direction (future-gated)
7. **Integrative/Eastern-medicine capability** ([[Runtime Blockers]]): stays knowledge/metadata-only until a real safety/legal/clinical architecture exists. What is the intended future gate owner?
8. **Standalone UI scope** — dashboard-first? Which surfaces go to **Claude Code** vs stay CLI? (See review §7.)
9. **README truth-in-advertising** — soften present-tense claims ("clinical decision-support reports", "BitTorrent/WebSeed content fabric") to "not implemented / gated / consumed externally"?
