# Somatic — Autonomous Build: rebuild the UI rich + dense with the real frontend stack

Charter saved as step 0 of the first commit. Founder direction: **"the works" — rich + dense** (premium motion AND real 3D AND a denser, option-rich, keyboard-friendly layout).

## Why this exists (read once)

The lab's own UI standard (`AGENTS.md`) only names the *craft rulebooks* (impeccable, taste-skill, ui-ux-pro-max) + astryx. It does **not** name the ~50 rich frontend libraries the founder maintains in `C:\AI\frontend-skills`. So past builds were "standard-compliant" yet plain. This charter **expands** the toolset: keep the craft rulebooks for taste, and **actually use** the frontend stack for richness.

## Hard boundary — rebuild the FRONTEND only; the backend rails are verified, leave them

- **Do not touch** the stdlib bridge, the JSON API, or any engine gate. The bridge keeps binding `127.0.0.1`, keeps `script-src 'self'`, keeps serving built static assets + the same `/api/*` JSON. Consent / emergency / citation / biosecurity / no-raw-sensor / loopback / right-to-erasure all stay exactly as they are (they were independently verified). This work replaces `ui/` (the presentation layer) and the static bundle it produces — nothing behind the API.
- **Core `pyproject` `dependencies == []`** stays. All frontend/build deps live in `ui/package.json`. The app compiles to **self-hosted static assets**; end users still run `python -m somatic ui` with no Node at runtime.
- **Local-first, strict CSP hold.** Everything bundles locally — no CDN, no external fonts/scripts/telemetry. React, R3F, GSAP, etc. all compile into self-hosted JS served under `script-src 'self'`; that is allowed. If any library needs `wasm-unsafe-eval` (e.g. physics/WASM), either avoid it or add the **minimal** CSP token and justify it in `planning/AUTONOMOUS-LOG.md` — never broaden CSP beyond the one token, never allow remote origins.

## Use the real frontend stack (prove each one) — `C:\AI\frontend-skills`

Rebuild `ui/` as a bundled React app (`ardynai-next.js` static export or `ardynai-vite`) and genuinely use:

- **3D / the "wow":** `ardynai-react-three-fiber` + `ardynai-drei` for the **Field/body view** (a real 3D body/point-cloud/pose in a lit scene — not a 2-joint stick) and the **Presence avatar**; `pmndrs-postprocessing` / `pmndrs-react-postprocessing` for depth/bloom, `pmndrs-maath` for math, `protectwise-troika` for 3D text. Physics (`pmndrs-react-three-rapier`) only if it earns its place.
- **Motion / feel:** `greensock-gsap` for choreographed transitions and reveals, `darkroomengineering-lenis` for smooth scroll, `theatre-js-theatre` for any sequenced/scrubbable animation, `ardynai-yocto-spinner` for loaders. All gated by `prefers-reduced-motion`.
- **Framework / styling / state:** `ardynai-tailwindcss` on the existing Quiet-Instrument tokens, `pmndrs-zustand` for state, `georgealways-lil-gui` for a real controls/inspector panel (fits the instrument identity).
- **Terminal surface:** render the actual CLI in-app with `ardynai-opentui` or `xtermjs-xterm.js` on the "CLI tools" screen.
- **Avatar/audio (Presence, optional, off by default):** `ardynai-stableavatar` / `ardynai-gaussiantalker` / `ardynai-audio2face-3d` render-only; `goldfire-howler.js` / `joshwcomeau-use-sound` only if sound is opt-in and muted by default (health context — no surprise audio).
- **Keep the craft rulebooks** (`C:\AI\design-skills`: impeccable, taste-skill, ui-ux-pro-max-skill, open-design, stitch-sdk/stitch-skills, refero_skill offline) so richness stays tasteful, not slop. Use astryx components if present; note honestly if not.

Write **`ui/DESIGN-NOTES.md` v2** mapping **each frontend-skill actually used → the surface it's used on**. If a listed tool genuinely doesn't fit, say why. The bar: a reviewer can see GSAP / R3F / Drei / Lenis are really in the shipped bundle and on screen.

## Make it dense + optioned + intuitive (not minimal)

- **Fill the width.** Kill the empty right gutter — multi-panel layouts, a persistent context/detail panel, dashboards with real information density.
- **A command palette (⌘K)** to reach every surface and action; full keyboard navigation; visible shortcuts.
- **More visible controls**: filters, toggles, inspectors, live status with counts, per-surface options — the product should feel capable and explorable, not empty. Every consent scope, sensor lane, and evidence view should feel like a place with depth.
- Rich empty/loading/error/success states everywhere; micro-interactions on every control.

## Quality gates (same rigor as before, judged on richness this time)

- Keep every rail provably intact: re-run the adversarial self-review (no-consent → blocked, emergency → banner, citation-less → honest-null, sensor → features-only/no-raw, non-loopback → refused, live-CSI → off without grant). Screenshot proof.
- **Accessibility stays AA even with 3D/motion:** `npm run a11y` → 0 axe violations, keyboard to everything, reduced-motion path, non-3D fallback where a 3D surface carries meaning, labels/roles on canvases.
- **Visual design-critique gate, judged on depth:** a design-director persona scores it against "does this look rich, optioned, and premium — or plain?" Iterate until **≥ 4.5/5 and it clearly does not read as a minimal vanilla app.** Full light + dark screenshots of every surface attached to the PR + refreshed `docs/ui-screenshots/`.
- Green each time: `python -m unittest`, `python -m somatic doctor`, ruff clean on any changed Python, `ui/` build + a11y clean, **core `dependencies == []`**. Then merge yourself on green. Fresh clone off `origin/main`; never build in the locked `C:\AI\somatic`.

## Only stop for these (log in `planning/AUTONOMOUS-LOG.md`)

- Adding a dep to the **Python core**, weakening a safety/privacy rail, bypassing a gate, or broadening CSP beyond a single justified `wasm-unsafe-eval` token — stop instead.
- Irreversible/external/costly: public URL/deploy, npm/registry publish, buying anything, force-push. Local `127.0.0.1` is fine.
- **LICENSE untouched** (founder decides later). The **real** 3D body from live sensors still needs the founder-gated pose model — the rich 3D Field view renders **sandbox/synthetic or loopback features only**, clearly labeled, never a real body scan without hardware + the model.
- Genuinely stuck (a lib won't bundle under CSP after real attempts) — swap for an equivalent from the stack, note it, keep going.

## Done

When the UI is a bundled React app that visibly uses the frontend stack (3D Field/avatar, GSAP/Lenis/Theatre motion), reads as rich + dense + optioned (not plain), clears the depth-judged critique gate (≥4.5, screenshots attached), keeps every rail intact and `dependencies == []`, and is merged to `main` — write `planning/AUTONOMOUS-LOG.md` with `DESIGN-NOTES.md` v2 (each frontend-skill → where used), before/after screenshots, and any CSP/default notes — then stop. Founder-gated: LICENSE, public release, the live-sensor pose model.

## Implementation notes (this build)

- **Bundler choice:** Vite + React (not Next static export). Next hydration emits inline scripts, which would force `unsafe-inline`. The charter allows either; Vite keeps `script-src 'self'`.
- **Taste dials (founder override):** VARIANCE 5 / MOTION 7 / DENSITY 8. Quiet Instrument moss identity stays. Motion and density go up; identity does not become a generic Tailwind dashboard.
- **3D honesty:** sandbox/synthetic template body from head+torso joints plus occupancy; live CSI is occupancy cloud only (no skeleton). Banner: `Sandbox · synthetic · not a real person.`
- **OpenTUI:** `@opentui/core` is a Zig native TUI, not a browser terminal. CLI tools uses `xterm.js` instead.
- **yocto-spinner:** Node TTY spinner; braille frames are ported into the React loader.
- **lil-gui / xterm CSS:** inlined into the bundled `styles.css` with `injectStyles: false` so `style-src 'self'` holds.
- **Astryx:** not present at `C:\AI\astryx`; noted honestly in DESIGN-NOTES.
