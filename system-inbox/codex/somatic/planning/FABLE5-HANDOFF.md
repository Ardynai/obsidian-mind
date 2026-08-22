# Fable 5 — Repo Handoff: Somatic

> You are the **Fable 5 planner + senior dev** for `Ardynai/somatic`, taking over a fresh session. Read this fully, then execute the first mission below.
>
> **Conservative-change principle:** keep most existing content / config the same — change only what is stale, wrong, or clearly better.

## 0. Model discipline (do this before anything else)
The session may have reverted to **Opus 4.8**, and default sub-agents may also be 4.8. So:
- Spawn **Fable 5 sub-agents explicitly** — `Agent` with `model: "fable"` — for ALL delegated work: verification, review, prompt authoring, research fan-out. Never rely on the inherited model.
- Do **not** use `fork` sub-agents for model-sensitive work (forks inherit the parent model).
- Josh's expectation: **Fable 5 does the thinking, via Fable 5 sub-agents.**

## 1. Roles + models
- **Planner (you) = Claude Fable 5.**
- **Operator (build) = GPT-5.6 Sol**; higher tier **Sol Max** for heavy/sensitive batches + full advisory reviews (Josh uses **Sol Max**, not "Ultra"). Recent builds also ran via a Cursor + Grok 4.5 harness — "operator" is the role, not a fixed model.
- **PR review = an org-scoped Cursor agent stack** (Approval Agent + Security Reviewer + nightly Vulnerability Scanner + selective Bugbot) — automatic on every Ardynai repo. You are the **human backstop** for high-risk-path PRs. Detail in `CLAUDE.md` §4a.
- **Founder = Josh (Ardynai).**

## 2. Current state (verified at handoff, 2026-07)
- The pivot spine is on `main`: consent (`somatic/consent/`), safety core (`somatic/safety/core.py`), AI advisory adapter (`somatic/advisory/`), personal insights (`somatic/insights/engine.py`), and flows `analyze` + `share` (`somatic/flows/`).
- Recent PRs: **#75 analyze flow — merged**; **#76 share flow** and **#77 this handoff** — in flight (host-verified; merge on green).
- Per-repo PR-review policy is committed: `.cursor/rules/somatic-review-routing.mdc` + `.cursor/BUGBOT.md` (Somatic's high-risk paths + review rubric).
- stdlib-only; `dependencies = []`; CLI `python -m somatic {doctor,run,analyze,share,replay,...}`; CI = one `unittest` job (~33 min) and is the merge gate.
- The large `somatic/safety/phase12_contracts.py` monolith (~22k lines) still backs `doctor`; leave it unless a batch is about it.
- Full detail: `CLAUDE.md` (planner) + `AGENTS.md` (operator) + `planning/` (plan).

## 3. Workflow doctrine (summary — full in `CLAUDE.md`)
Read-first / anti-hallucination → operator builds-not-pushes → planner host-verifies (read code + run tests in your env; this IS the human review for high-risk paths) → push → draft PR → org Cursor review stack runs → merge on green + approval with the exact-head guard (`gh pr merge <n> --squash --match-head-commit <SHA> --delete-branch`) → one batch at a time. Host tooling caveats: `bandit` broken on host (missing PyYAML, not a CI gate); `doctor` slow (run detached); `fallow` prints then hangs (kill after print).

## 4. How to work with Josh
Founder/owner (Ardynai). Authorizes you to merge when everything lines up — but STOP + surface anything external / destructive / costly / scope-expanding. Switches build harnesses often (currently Sol Max; Cursor + Grok 4.5 recently). Values momentum; dislikes over-restriction. Check in at real decision points.

## 5. Open backlog
See `planning/backlog.md`. After #76, the top item is the **source-grounded research loop / co-scientist** — design the retrieval + grounding spec BEFORE writing the operator prompt (medical content must be evidence-graded + cited, never model memory).

## 6. FIRST MISSION (in order)
**A. Connect + use Josh's dev tools.** Bring up and actually use, as applicable: Composio (GitHub), Windows MCP, the Obsidian vault (`C:\AI\obsidian-mind`), CodeGraph, the `graphify` skill, GitNexus, Tailscale, and the deploy stack (Vercel / Supabase / Cloudflare / fal / ComfyUI). Survey installed plugins/skills (e.g. Superpowers). Read `Ardynai/locus-evolution-lab` (local: `C:\AI\locus-evolution-lab`) — the cross-repo methodology / doctrine / scoring / prompts hub; `prompts/MODEL_PROMPTING_SOL_AND_FABLE5.md` is canonical for prompting Fable 5 (planner) + Sol/Sol Max (operator); `private/integration/pr-review-automation.md` is the PR-review stack; `scoring/` templates are for the finished-product grade.

**B. Load history / context.** Persistent memory (vault `Somatic/` notes — copied here to `planning/vault-notes/`; point-in-time, verify against code), the git + PR history (authoritative record of what shipped), the whole in-repo plan (`planning/`), and Josh's Obsidian vault + CodeGraph + `graphify` (knowledge graph over vault + repo). Vault path: `C:\AI\obsidian-mind`. No need to replay old chat transcripts.

**C. Run a full advisory review** of the repo + plan — coverage checklist in §7. Author your OWN repo-specific **Sol Max** prompt for it (read-only; findings + recommendations only; no building). Run the review via **Fable 5 sub-agents**.

**D. After the review, optimize your OWN Claude config** for this repo — `CLAUDE.md`, `AGENTS.md`, the `.cursor/` review policy, `docs/*`, any Claude/Fable config — with Fable-5 logic and how the repo actually is (conservatively — keep most the same).

**E. Finished-product simulation.** Assume the product is done per the new plan; role-play an experienced user in this repo's category (a health-curious N-of-1 self-tracker; and a clinician receiving a shared summary); grade it against `Ardynai/locus-evolution-lab` `scoring/` templates; list what's missing / desired.

**F. Write your own repo-specific GPT-5.6 Sol Max prompt** (tailored, NOT a canned template) that: hands Sol the whole in-repo plan; asks its opinion on the plan, the code, and fixes / optimizations / security; tells Sol to also optimize its own Codex config (`AGENTS.md`, environment, worktree, any configurable Codex file/folder — conservatively); tells Sol to do the same finished-product simulation + grade + gaps; and includes YOUR review + simulation findings so Sol builds on them.

**G. Triage** all findings into `planning/backlog.md` as a one-batch-at-a-time queue; continue the project.

> **Do NOT run the review as part of reading this handoff.** It is YOUR job now, with full context (tools connected, memory + graph loaded). The prior session deliberately left it for you.

## 7. Advisory review — coverage checklist (write your OWN prompt from this)
The Sol Max review prompt you author hands Sol the whole in-repo plan; is **read-only** (findings + recommendations only — no building, no one-shot); and covers:
- architecture & code quality;
- security & abuse-resistance (auth, payments, personal data, **minor-safety**, multi-instance / horizontal-scale correctness);
- cost & scale (hot paths, per-user compute / bandwidth, super-linear growth);
- latent bugs / correctness gaps;
- the monetization model;
- the rest of the plan — sequencing, risks, dependencies, what's missing;
- bold net-new ideas.

Output = one prioritized report: per item — what / why it matters / rough effort / risk if ignored / code-batch-or-founder-decision; ranked impact-vs-effort; ending with explicit advice on the rest of the plan. The planner triages into the queue; the operator changes nothing in the review pass.

Beyond the review, tell Sol to also: optimize its own Codex config for the repo (conservatively — keep most the same); do a finished-product simulation (assume done per plan, role-play an experienced user in the repo's category, grade it against the lab `scoring/` templates, list gaps); and build on the Fable-5 review + simulation findings you pass it.

## 8. Safety invariants that must survive every change
Consent default-OFF + `require_consent` fail-closed; `emergency_screen` in the path; `frame_advisory` (no diagnosis / prescription / dosing); evidence-graded + source-grounded health claims; stdlib-only, `dependencies = []`. See `planning/vault-notes/Safety Invariants.md` and `.cursor/BUGBOT.md`.
