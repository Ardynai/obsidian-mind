# Somatic — Finish the README to the Kortex-Audio bar (Grok 4.6)

You are **Grok 4.6**, sole builder for `Ardynai/somatic`. The README is a product front page but not yet at the bar Josh wants. The target is the **`Ardynai/kortex-audio`** README — match its **structure, rigor, and honesty**, rendered in Somatic's own **Quiet Instrument** identity (moss / white / near-black — **not** kortex's neon). README + docs + diagrams only; self-review + self-merge on green.

**Step 0 of your first commit:** save this charter to `planning/README-FINISH.md`.

**Read the target first.** The kortex README is private and your local `C:\AI\kortex-audio` clone is stale — read the real one from the remote: `gh api repos/Ardynai/kortex-audio/contents/README.md --jq .content | base64 -d` (or `git -C C:\AI\kortex-audio fetch origin && git show origin/main:README.md`). Study its shape, then apply it to Somatic's real content.

## Match this structure (kortex-audio README), in order

Emoji section headers, **named figures with captions + source provenance**, an **architecture table**, radical honesty.

1. **Hero** — "Somatic" + one tight positioning paragraph (a consent-gated, local-first, **informational** personal-health engine; nothing leaves the machine; never diagnosis / prescription / dosing) + a one-line honest status note (local v1; informational-not-medical; research runs on an offline corpus by default). Then **Figure 1 — architecture**: embed the existing `docs/diagrams/somatic-local-architecture.svg` with a kortex-style caption, e.g. *"Figure 1 — Somatic local architecture: engine ↔ stdlib loopback bridge ↔ local UI; consent / emergency / citation / biosecurity gates sit on every path. Source: docs/diagrams/somatic-local-architecture.svg (draw.io + Mermaid alternates)."*
2. **🎛️ What it is** — prose + a boundary map of the **real** packages: `somatic/{consent,safety,advisory,insights,flows,research,remedy,parasite,ingest,experiments,sensors,evidence_bus,science,presence,bench,bridge}`, the `ui/` authoring package, and the CLI.
3. **🧠 Why it matters** — audience-framed: for a person tracking their own signals; for a clinician receiving a share; for a privacy-first user.
4. **🚦 Status** — the honest real / sandbox / gated split (kortex's stub-vs-real mix): **Real** — consent spine, safety gates, analyze/share, citation-bound research over the offline corpus, the local UI. **Sandbox** — sensor roster (features-only, live refused), science harness + presence (render-only). **Off by default** — live literature (`SOMATIC_RESEARCH_LIVE`), AI advisory (bring-your-own model). **Founder-gated** — LICENSE, public release, live hardware.
5. **✨ Features** — grouped by subsystem with specific bullets: Consent & safety spine · Analyze & share · Research / Remedy / Parasite (evidence grades, real citations, honest-null) · N-of-1 experiments · Ingestion (CSV / Apple Health) · Sensor roster (sandbox, features-only) · Science & presence (render-only) · Local UI (`python -m somatic ui`).
6. **📸 Screenshots** — embed the real `docs/ui-screenshots/` shots (consent, status, research, sensors), each with an honest caption (local; all scopes off by default; sandbox / synthetic).
7. **🧭 Architecture** — a **table** with columns **Surface | What it owns | First files**, mapping each `somatic/*` package + `bridge/` + `ui/` to its responsibility and real entry files. Then **Figure 2** — the data-flow / gate diagram with a caption + `Source:`.
8. **🚀 Quickstart** — commands **verified** against the real CLI. Lead with `python -m somatic ui` (opens the local app on 127.0.0.1). Note: stdlib-only core, needs only Python 3.11, nothing to install for the core. Then `python -m somatic {doctor,analyze,share,consent status}`.
9. **⚙️ Configuration** — only env toggles that actually exist (`SOMATIC_RESEARCH_LIVE`, the `SOMATIC_ADVISORY_MODEL_*` set, consent/store paths); never-commit-secrets; `.env.example`.
10. **🧪 Development** — `python -m unittest`, `ruff`, `python -m somatic doctor`, the CI job (name it: `CI` / `unittest`), branch protection, pointers to `AGENTS.md` + `CLAUDE.md`.
11. **🛡️ Security / Privacy** — the differentiator; make it strong and specific: 7 default-off consent scopes; local-first + loopback bind + CSP `script-src 'self'`; **no raw sensor egress** (features only); right-to-erasure; informational framing + emergency routing; biosecurity refuse-list. Honest limitations: plaintext-at-rest + `0600`, English-only, offline corpus. Pointers to `SECURITY.md` + `planning/FINISHING-REPORT.md`.
12. **🛤️ Roadmap** — honest: local v1 → optional live literature (consent-gated) → live sensor hardware (founder-gated) → mobile / adaptive UI (deferred).
13. **📜 License** — honest, like kortex: *"No LICENSE selected yet — treat this repository as all-rights-reserved until the founder adopts an explicit license."* **Do not pick or add a license.**

## Style rules (match kortex, keep Somatic's identity)

- Emoji section headers; **Figure N** captions with **Source: docs/diagrams/…** provenance; the surface→owns→first-files table; radical honesty (real/sandbox/gated, honest screenshot captions, honest license note); audience framing; **verified** commands only.
- Render diagrams in Somatic's **Quiet Instrument** identity (moss / white / near-black), **not** neon. Commit any new/updated diagram as static SVG under `docs/diagrams/` with a draw.io or Mermaid **source alternate**. Documentation only — no external widgets, hotlinked images, tracking badges, or website runtime deps.
- Truthful static badges only (CI once green; license once chosen). Move any remaining dev/phase history to `docs/HISTORY.md`.

## Ground everything in reality (no invention)

Read the real files first: `somatic/cli/`, the package dirs above, `pyproject.toml`, existing `docs/diagrams/` + `docs/ui-screenshots/`, `planning/FINISHING-REPORT.md`, `AGENTS.md`, `CLAUDE.md`, and the kortex README. Every command, path, env var, and feature must be verified against the code. Anything aspirational goes under **Roadmap**, labelled — never implied as shipped.

## Gates + authorization

README / docs / diagrams only — additive, low-risk. Keep `python -m somatic doctor` green and core `dependencies == []`. Self-review for honesty (no overclaiming) + broken links + that every embedded image/diagram path resolves. Then merge yourself on green. Fresh clone off `origin/main`; never build in the locked `C:\AI\somatic`.

## Hard-stops

Don't pick/modify the **LICENSE**. Don't publish a public site/URL or add website runtime deps. Don't invent features or claim live-hardware / real-corpus results that aren't real. Everything else (README + docs + diagrams) is yours to finish and merge.

## Done

When `README.md` matches the kortex-audio bar — emoji sections, captioned Quiet-Instrument figures with `Source:` lines, the Surface/Owns/First-files table, verified quickstart, a strong Security/Privacy section, honest Status + License — with the phase history moved to `docs/HISTORY.md` and the PR merged to `main`, note it in `planning/AUTONOMOUS-LOG.md` and stop.
