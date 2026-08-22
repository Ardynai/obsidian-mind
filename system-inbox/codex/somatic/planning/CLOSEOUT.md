# Somatic — Autonomous Build: professional-grade closeout (Grok 4.6)

You are **Grok 4.6**, the sole builder for `Ardynai/somatic`. This is the final push, by yourself — no other AI, no hand-offs, self-review + self-merge, PR after PR until it's all done. Make Somatic look and feel like a **professional product team** built it, then finish and **harden** it so it's ready for the founder to actually use.

**Direct feedback on the last pass:** the shipped UI does **not** look like the design skills were used. A token set and "craft 4/5" self-grade is not enough. This time you will **execute the design skills as processes** (not cite them), prove it with an audit trail and screenshots, and clear a **hard visual design-critique gate**. If a screen still looks like default/un-designed Tailwind, it is not done.

**Step 0 of your first commit:** save this charter to `planning/CLOSEOUT.md`.

## Standing rails — verified holding in v1; nothing here may regress them

Re-run your adversarial self-review after every change and confirm each still holds:

- Core **`pyproject` `dependencies == []`** (stdlib-only core). Frontend/build/a11y deps live only in `ui/package.json`.
- Bridge **binds `127.0.0.1` only**, refuses non-loopback `Host`/`Origin`; **CSP stays `script-src 'self'`** (self-host everything — fonts, icons, charts; no CDN/runtime external fetch; `no-store`, `nosniff`, `no-referrer`).
- Every API path **reuses the real engine gates** (`require_consent` → `emergency_screen` → framed advisory via the adapter / citation-binding / `screen_biosecurity` / honest-null). Never reimplement or bypass a gate; never rewrite advisory text into something more authoritative.
- **No raw sensor egress** (features only; `/api/sensors/live` refused). **Presence render-only.** **Right-to-erasure** (`/api/privacy/erase`) reachable and complete.
- Don't touch the fabric byte-pinned JCS/Merkle vectors or rewrite `phase12_contracts.py`. No secrets committed.

## Part 1 — The best UI possible (professional-team quality). This is the priority.

**Execute the design skills, don't cite them.** For each skill in `C:\AI\design-skills\` — `impeccable`, `taste-skill`, `ui-ux-pro-max-skill`, `open-design`, `stitch-sdk`, `stitch-skills`, `refero_skill` (offline) — open its `SKILL.md`, run its actual workflow, and produce the artifacts it's meant to produce. Write `ui/DESIGN-NOTES.md` mapping **which skill drove which decision** (type scale, palette, spacing, components, motion) so the use is auditable. Follow `AGENTS.md` "UI standard" and lean on **astryx** components/patterns as the quality baseline. Use **Refero's free/offline guides — never the paid Refero MCP.**

**Design the language first, then the screens.** Before restyling surfaces, establish and commit:

- A named **visual direction** for Somatic — calm, trustworthy, private, personal-health-but-not-clinical; distinctive, not a generic dashboard or an EHR.
- A real **token system**: full color ramps + semantic tokens (AA+ contrast, cohesive light **and** dark), a modular **type scale** on a real self-hosted typeface (deliberate, not the browser default), and spacing / radius / elevation / motion scales on a consistent grid.
- A real **component library**: buttons, inputs, selects, cards, nav, tables, modals, toasts, badges, charts — every one with hover / focus / active / disabled / **loading / empty / error** states. Bundle a consistent local **icon set** (self-hosted SVG/sprite).

**Then compose every surface to a high bar.** Real hierarchy, rhythm, alignment, and tasteful micro-interactions (≤200ms, fully `prefers-reduced-motion` gated). **A strict CSP is not an excuse for plain design** — self-host the assets and make it beautiful.

**Accessibility stays a real audit:** `npm run a11y` in `ui/` to **0 violations**, WCAG 2.1 AA, plus the Python landmark/CSP/gate tests. Don't let contrast be "skipped in jsdom" — verify token contrast explicitly.

**Hard visual design-critique gate.** Iterate until it genuinely clears **≥ 4.5/5**. Attach full-page screenshots of every surface in light and dark. Record the critique in `planning/UI-READINESS.md`.

## Part 2 — The best README + presentation (flagship-OSS quality)

Fully apply the Locus GitHub presentation and visual-diagram workflows. Commit visuals as static local assets. No LICENSE file. Stay honest about v1, offline corpus default, English-only.

## Part 3 — Finish the substance

- Wire real citation-bound literature retrieval (stdlib urllib, consent-gated, host-allowlisted, https-only, SSRF-guarded, size-capped, OFF by default). CI stays hermetic.
- Close safety fix-soons: SSRF, `frame_advisory` live-model residual, NaN/inf ingest, graceful CLI notes.
- Fix GitHub Actions so unittest + doctor actually run.

## Part 4 — Harden it

DAST against loopback, static hardening, observability without egress, 0600 files, document encryption-at-rest as a known limitation unless a clean optional extra exists. Evidence in `planning/FINISHING-REPORT.md`.

## Only stop for

Python core deps, rail weakening, public URL/release/spend, LICENSE changes, identity changes (accounts/cloud). Small choices: pick a safe default and continue.
