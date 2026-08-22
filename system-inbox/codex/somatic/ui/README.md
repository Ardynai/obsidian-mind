# Somatic UI (authoring package)

This directory is the **Vite + React** authoring package. It is **not** a Python dependency.

## What end users run

```powershell
python -m somatic ui
```

That command starts a stdlib HTTP server on `127.0.0.1` and serves the committed static app in `somatic/bridge/static/`. End users do not need Node.

## Why Vite, not Next

The local bridge sends `Content-Security-Policy: script-src 'self'` and refuses inline scripts. Next.js App Router hydration emits inline scripts, which would force `'unsafe-inline'`. The production UI is a CSP-clean **Vite IIFE** bundle (`app.js` + `styles.css`) that talks to the same JSON API. React, R3F, GSAP, Lenis, Theatre, xterm, and lil-gui all compile into that self-hosted file.

```powershell
npm install
npm run build
npm run a11y
npm run dev
```

`npm run dev` proxies `/api` to `http://127.0.0.1:8765`. Keep tokens aligned with Bioluminescence (`ui/src/styles/tokens.css`, `planning/UI-BOLD-DIRECTION.md`).

`npm run a11y` audits a representative DOM (shipped shell + fixture states) with axe-core. jsdom cannot compute layout contrast, so axe color-contrast stays off; `ui/contrast-tokens.json` is checked with relative-luminance math in the same script.

## Local-first rules

- No runtime CDN fonts, analytics, or third-party beacons.
- No cloud accounts or sync.
- Do not add packages to `pyproject.toml` `[project].dependencies`.
- Do not broaden CSP beyond a single justified `wasm-unsafe-eval` token (this build did not need it).
