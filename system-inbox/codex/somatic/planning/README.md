# Somatic — Planning (start here)

The full plan for `Ardynai/somatic`, readable from inside the repo (the coding operator only sees the repo, not Josh's vault or the Claude project folder).

## Read in this order
1. **`current-plan.md`** — the ACTIVE plan: the pivot to a user-owned, consent-gated informational health engine; what's shipped on `main`; the roadmap.
2. **`backlog.md`** — the one-batch-at-a-time queue.
3. **`FABLE5-HANDOFF.md`** — handoff for a fresh Fable 5 planner session (first mission, review checklist, model discipline).
4. **`SOMATIC_MASTER_PLAN.md`** — the north-star vision (v2): the grand autonomous-science + multi-sensor health engine. Aspirational superset; the pivot is the pragmatic first slice of it.
5. **`phase-12t-review-and-plan.md`** — the deep repo review (architecture, safety, phases) done just before the pivot.
6. **`vault-notes/`** — copied Obsidian vault `Somatic/` notes (phase map, safety invariants, runtime blockers, open questions, recommended next phases). Point-in-time; verify against code.

## Operating manuals
- **`../CLAUDE.md`** — the Fable 5 planner manual (workflow, model discipline, Sol prompting, design routing).
- **`../AGENTS.md`** — the operator (Sol / Ultra; currently Cursor + Grok 4.5) manual.

## One-paragraph state
Somatic is a standalone, stdlib-only Python engine (`dependencies = []`, CI = one `unittest` job). It recently pivoted from a large fail-closed metadata/contracts scaffold to a working, consent-gated, **informational** personal-health runtime, including a local UI (`python -m somatic ui`). Product README is the front page; phase archive is `docs/HISTORY.md`. Finishing-suite report: `FINISHING-REPORT.md`. Enrichment charter: `ENRICH-AND-FINISH.md`.
