# Somatic — Autonomous Build: re-skin the UI to the "Bioluminescence" bold identity (Grok 4.6)

You are **Grok 4.6**, sole builder for `Ardynai/somatic`. The rich UI (PR #91, Vite + React) works but its visual identity is too plain for the founder. **Re-skin it to a bold, dark, luminous, data-dense identity — "Bioluminescence" — matching the concrete target the founder approved.** This is a **re-theme, not a re-architecture**: keep the app, the cockpit/inspector/command-palette/3D/terminal, and the whole frontend stack; change the visual language. Self-review + self-merge on green.

**Step 0:** commit the target files so they're in the repo, then build to them:
- `planning/UI-BOLD-DIRECTION.md` — the identity spec (palette values, type, surfaces, data-viz, motion, trust rules). **This is the source of truth.**
- `docs/ui-mockups/somatic-bold-mockup.html` — the rendered visual target (Status + Field). **Match its look** (dark pine-black canvas, luminous emerald signal, cyan/amber/violet data accents, layered glowing panels, faint instrument grid, mono readouts, radial capability ring, glowing body + occupancy waterfall, telemetry rail). Also save this charter as `planning/UI-BOLD.md`.

## Do
- Rebuild the **design tokens / theme** to the Bioluminescence palette + type from the spec. Self-host the new display + mono fonts (OFL) locally — no CDN. Apply layered translucent surfaces, emerald hairlines, glow-as-elevation, the masked instrument grid, and the accent set across **every** surface.
- Keep and re-skin the existing structure: three-column cockpit (spine · main · telemetry rail), ⌘K palette, filters, lil-gui, in-app xterm, and the **R3F/Drei Field** — now dark with bloom and a luminous body. Lean on the frontend stack (`greensock-gsap`, `theatre-js`, `darkroomengineering-lenis` for the breathing/pulse/reveal motion; `pmndrs-postprocessing` for bloom) — all `prefers-reduced-motion` gated.
- **Data-viz on every surface** (dataviz principles): the 7-segment capability ring, KPI tiles + sparklines, luminous charts, animated count-up numbers — accessible, labeled, never color-only.
- Ship **both themes**: Bioluminescence **dark as the new default** + the light variant from the spec; keep the theme toggle.

## Trust guardrails (non-negotiable — health tool)
Keep the informational banner prominent on every surface. **Coral/red is used for emergency routing and nothing else.** No fake vitals, no clinical certainty; honest-null stays calm and dignified (large type, never error-red). Aim "high-end scientific instrument," never hype/crypto/gamer.

## Rails that must stay intact (backend untouched — do not edit it)
- Core `pyproject` `dependencies == []`; all frontend/build/font deps live in `ui/package.json`; ships as self-hosted static assets (`python -m somatic ui`, no Node at runtime).
- Bridge keeps binding `127.0.0.1`; **CSP stays `script-src 'self'`** (bold is CSS/tokens/canvas/self-hosted-fonts — no CDN, no inline-script; keep the Vite IIFE approach that avoids `unsafe-inline`; at most one justified `wasm-unsafe-eval` if postprocessing needs it, logged).
- Consent / emergency / citation / biosecurity / no-raw-sensor / loopback / right-to-erasure all unchanged and still surfaced. The Field stays sandbox/synthetic or loopback-features-only, labeled; live off by default.

## Gate (judged on the bold target this time)
- Visual design-critique gate: a design-director persona scores **"does it match the Bioluminescence target and read as bold/premium — or did it drift back to flat/minimal?"** Iterate until **≥4.6/5 and it clearly matches the mockup.** Full light + dark screenshots of every surface attached + `docs/ui-screenshots/` refreshed.
- Re-prove every rail (no-consent→blocked, emergency→banner, citation-less→honest-null, sensor→features-only, non-loopback→refused, live-CSI→off-without-grant). `npm run a11y` → 0 axe violations (AA on the dark canvas — verify token contrast). `python -m unittest`, `python -m somatic doctor`, ruff clean, **`dependencies == []`**. Then merge yourself on green. Fresh clone off `origin/main`; never build in the locked `C:\AI\somatic`. Write `ui/DESIGN-NOTES.md` **v3** mapping the shipped surfaces to the Bioluminescence spec.

## Only stop for these (log in `planning/AUTONOMOUS-LOG.md`)
- Adding a core dep, weakening a rail, bypassing a gate, or broadening CSP beyond one justified `wasm-unsafe-eval` — stop instead.
- Irreversible/external: public URL/deploy, npm publish, buying anything, force-push. Local `127.0.0.1` is fine.
- **LICENSE untouched.** The real live-sensor body still needs the founder-gated pose model — the bold 3D Field renders sandbox/loopback features only.

## Done
When the UI matches the Bioluminescence target (dark luminous cockpit, glowing data-viz on every surface, bold but trustworthy), clears the critique gate (≥4.6, screenshots), keeps every rail + `dependencies == []`, ships dark-default + light, and is merged to `main` — write `planning/AUTONOMOUS-LOG.md` + `DESIGN-NOTES.md` v3 and stop. Founder-gated: LICENSE, public release, the live-sensor pose model.
