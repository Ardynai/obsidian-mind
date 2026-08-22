# Local UI build notes

First ship: PR #86 (`python -m somatic ui`). Enrichment charter: [ENRICH-AND-FINISH.md](ENRICH-AND-FINISH.md). Grades: [UI-READINESS.md](UI-READINESS.md).

## Architecture (unchanged)

- Shipped UI: `somatic/bridge/static/` (HTML/CSS/JS) served by stdlib HTTP on 127.0.0.1.
- Authoring: `ui/` Next.js + Tailwind. Not a Python dependency. Not the production bundle (CSP forbids inline hydration scripts).
- API: `somatic/bridge/api.py` wraps existing engine functions.

## What enrichment added

Token scale, grouped nav, Status empty state, Consent tone, own-series SVG charts, honest-null dignity, sensor sandbox/hardware labels, Privacy reassurance, axe authoring check, product README, architecture SVG, finishing reports.
