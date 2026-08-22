# Local UI

## Owns

The graphical interface a non-technical person can run without the rest of the CLI:

- `somatic/cli/main.py` `ui` subcommand
- `somatic/bridge/` stdlib loopback server + JSON API
- `somatic/bridge/static/` shipped SPA (HTML/CSS/JS)
- `ui/` Vite + React authoring package (not a Python dependency)

## Main Flow

`python -m somatic ui` binds **127.0.0.1** (never a public interface), serves the static app, and opens a browser. Every privileged JSON call reuses the existing engine functions. Consent, emergency screening, advisory framing, citation-binding, and biosecurity refusals stay in the Python path.

The Vite app in `ui/` is for authoring (`npm run build` writes the static bundle; `npm run dev` proxies `/api` to the stdlib bridge). Production ships a CSP-clean IIFE because the bridge CSP is `script-src 'self'`.

## Gotchas

- `[project] dependencies` in `pyproject.toml` must stay `[]`. Frontend packages live only in `ui/package.json`.
- A present non-loopback `Origin` or `Host` is 403. Missing Origin is allowed for same-machine tools.
- Sensor endpoints emit features only. Live lanes are per-modality and default OFF: the **Sensors** screen grants/revokes csi / audio / video / video3d via `/api/sensors/live-consent` (each grant needs subject consent); the **Field** modality selector streams sandbox or a granted live lane through `/api/sensors/field`. Raw signals never reach the browser or disk.
- Analyze draws a local SVG of the user's own packet series. No CDN chart library.
- Authoring a11y: `npm run a11y` in `ui/` (axe-core + token contrast). Python tests still cover landmarks, CSP, and gates.
- Typefaces are self-hosted OFL under `somatic/bridge/static/fonts/`: Space Grotesk (display), IBM Plex Sans (body), IBM Plex Mono (readouts). No CDN. Dark Bioluminescence is the default theme.
- Optional live literature (`SOMATIC_RESEARCH_LIVE`) is off by default; CI uses the offline corpus.
- Ingest previews do not persist until `save: true`.
- Full `somatic doctor` remains CLI-only (slow contract cascade). The Status screen is the live safety spine.

## Start Reading

Start with `serve_ui` in `somatic/bridge/server.py`, then `dispatch` in `somatic/bridge/api.py`, then `ui/src/main.tsx` (the bundled output is `somatic/bridge/static/app.js`). Architecture drawings: [docs/diagrams/somatic-local-architecture.svg](../diagrams/somatic-local-architecture.svg) and [docs/diagrams/somatic-data-flow-gates.svg](../diagrams/somatic-data-flow-gates.svg) (draw.io + Mermaid alternates next to each SVG).
