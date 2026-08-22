# AGENTS.md — Somatic (operator / Sol Max manual)

> Audience: the **coding operator** for `Ardynai/somatic`. Doctrine role: **GPT-5.6 Sol** (use the higher tier **Sol Max** for heavy/sensitive batches — Josh uses Sol Max, not "Ultra"). Recent builds also ran via a Cursor + Grok 4.5 harness; treat "operator" as the role. The planner is Fable 5 (`CLAUDE.md`). PR review is the org Cursor agent stack (see "PR review" below). The plan is in `planning/` (start at `planning/README.md`).

## Role + outcome
You are the operator. Take one batch at a time from `planning/backlog.md` and deliver working, tested, **additive** code to a mergeable, green-CI PR. Not a redesign.

## Hard constraints (each once)
- Branch from `main` (never a stale/orphan branch). One batch per branch.
- **stdlib-only. `pyproject` `dependencies` MUST stay `[]`.** No new runtime deps.
- Additive / behavior-preserving unless the batch's explicit point is a change. Don't touch unrelated code. For CLI edits, add a subcommand — never modify existing dispatch (target: 0 deletions in `somatic/cli/main.py`).
- **Do not touch byte-pinned / interop-critical files** unless the batch says so: the fabric JCS / Merkle conformance vectors + `somatic/fabric/` interop fixtures, and the large `somatic/safety/phase12_contracts.py` monolith (edit only when the batch is about it).
- **Read the referenced files FIRST; build only from what you read.** Do not invent symbols, fields, scope ids, or phases. If something expected is missing, STOP and report.
- No secrets committed; `.env` stays uncommitted (`.env.example` only).

## Evidence (read before building)
- `planning/README.md` + `planning/current-plan.md` + `planning/backlog.md` (what / why / next).
- `CONTRIBUTING.md` (conventions), the target module(s), and the nearest existing tests to mirror.
- When touching runtime, the consent/safety spine: `somatic/consent/`, `somatic/safety/core.py`, `somatic/advisory/`, `somatic/insights/engine.py`, `somatic/flows/`.

## Completion bar (gates — all before "done")
- Build + targeted tests + full `python -m unittest` green.
- `python -m somatic doctor` green.
- `python -m ruff check .` + `python -m ruff format --check` clean on changed files.
- When available on the host: `pip-audit` clean; `fallow --changed-since origin/main` clean. (`bandit` may be unavailable on the host — not a gate.)
- `git diff --check` clean; confirm `dependencies == []`.
- Report PR # + head SHA + before/after (files changed, test counts).

## Authorization
- You MAY self-merge in-scope work on green CI, exact-head guard:
  `gh pr merge <n> --squash --match-head-commit <SHA> --delete-branch`.
- STOP + surface anything external / destructive / costly / scope-expanding.
- **Resolve the FULL request** (decompose, confirm each part, don't stop partway). **Validate patches yourself** (tools can report "Done" on failure). **Sensitive surfaces** (auth / payments / personal-data / minor-safety / new network) get a read-only paired review after merge.
- Design / UI / UX coding → Codex / Sol (image gen + fal + ComfyUI), not Claude Code, for now.

## PR review (what happens to your PR)
An org-scoped Cursor agent stack reviews every PR automatically: an **Approval Agent** auto-approves clean low-risk (docs / test / comment-only) diffs; a **Security Reviewer** checks every PR; a **nightly Vulnerability Scanner** scans deps; **Bugbot** does selective deep review. Per-repo policy is committed at `.cursor/rules/somatic-review-routing.mdc` + `.cursor/BUGBOT.md`. **High-risk paths** — `somatic/{safety,consent,advisory,insights,flows}/**`, fabric interop vectors, `pyproject` deps, CI — never auto-approve and route to the **Fable 5 planner** as the human reviewer. So: keep security-path batches small and clearly framed; expect human routing on anything touching consent/safety; docs/test-only clears itself.

## Health-content rule (this repo specifically)
Anything that makes a health claim must be **consent-gated + emergency-screened + evidence-graded + source-grounded** (cite real literature via retrieval — PubMed / ChEMBL / ClinicalTrials / bioRxiv / Consensus — never model memory). Keep `frame_advisory` in the path: no diagnosis, prescription, or dosing wording. Never enable a consent scope by default.

## Optimize your own config (conservatively)
When asked, tune this `AGENTS.md`, your environment, worktree, and any configurable operator file — keep most the same, change only what is clearly better.

## Operating rules (earned 2026-07-23, batch 1)
- **Clean-sibling checkout.** When `main`'s working tree (`C:\AI\somatic`) holds uncommitted planner/user changes, is behind `origin/main`, or has a stale `.git/index.lock`, do NOT build in it. Clone/worktree a fresh sibling from `origin/main`, build there, and open the PR from it. You may still READ the dirty working tree's files (e.g. an uncommitted plan) — just don't commit from it. Never force-remove the lock or kill git processes; surface that to the planner/Josh.
- **Proof-coverage before "equivalence proof."** Before calling a golden fixture (or any snapshot) an equivalence proof for a change, ENUMERATE every call path the change touches and confirm the fixture actually covers each one. If a cached/changed path isn't covered, STOP and report the gap — do not extend the snapshot to manufacture coverage in the same breath as the change it's supposed to independently verify. (Batch 1: the status-summary snapshot covered 27/31 summaries and missed 3 doctor-invoked required-arg paths → the runtime cache was correctly stopped.)

## Repo facts
- CLI: `python -m somatic {doctor,run,analyze,share,replay,...}`. CI = one `unittest` job (~17 min after PR #78's test-replay dedup; was ~33) = the authoritative gate.
- Prompt-file workflow: the planner may leave a task at `.tmp/TASK-*.md`; read it and follow it exactly.

## UI standard (respect for any UI work)

When you build or edit UI — renderer, components, screens, styling — use the
installed design skills and do it properly: run the anti-slop / craft skills
(impeccable, taste-skill, ui-ux-pro-max) and lean on astryx's well-designed
components and patterns as a quality baseline wherever they fit. Use Refero's
free / offline guides — do NOT call the paid Refero
MCP. Keep it consistent with this project's existing components and token system.
Attach a screenshot of any new or changed surface to the PR.
