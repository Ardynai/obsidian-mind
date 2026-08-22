# Local UI readiness (closeout)

Companion to [CLOSEOUT.md](CLOSEOUT.md). Adversarial visual critique of the **Quiet Instrument** SPA (not the enrich-pass system-ui dashboard).

Proof: full-page screenshots in [docs/ui-screenshots/](../docs/ui-screenshots/) (light) and [docs/ui-screenshots/dark/](../docs/ui-screenshots/dark/) (dark). Audit trail: [ui/DESIGN-NOTES.md](../ui/DESIGN-NOTES.md).

## Design-director critique (strict rubric)

Persona: a product design director who would reject Inter + slate + three cards. Question at every screen: "Would I ship this as a flagship local tool, or does it still look like default Tailwind?"

| Axis | Score | Evidence / remaining nit |
|---|---|---|
| Layout | 4.6 | Spine + moss inner rail + left-aligned display type. Not a card grid. Footer no longer clips. |
| Type | 4.6 | IBM Plex Sans, 1.2 scale, display **All off.** Tabular numbers on the meter. |
| Color | 4.5 | Pure white canvas, moss identity (seed-157 hue 150), slate accent for links. Light default. Token pairs ≥4.5 (ink ≥7). |
| Spacing | 4.5 | 8px grid, 65ch measure, hairline rules instead of cards. |
| Hierarchy | 4.7 | Kicker → display → meter → protocol list. Consent 01–07. |
| Consistency | 4.6 | Same buttons, pills, blocked rail, honest-null rail on every surface. |
| Motion | 4.4 | 160ms, `prefers-reduced-motion` kills it. No page-load choreography (product register). |
| Empty / loading / error | 4.6 | Designed empty, skeleton, blocked grant CTA, honest-null dignity, field errors. |
| Delight | 4.4 | Seven-tick meter and numbered protocol are the signature. No decoration for its own sake. |
| Distinctiveness | 4.6 | Defensible against "generic dashboard": meter, spine rail, Plex, no indigo, no cream-serif. |

**Craft mean: 4.55 / 5.** Clears the ≥4.5 gate. Not 5: the engine informational notice still repeats on every page (verbatim; UI must not rewrite it), and sandbox sensor rows stay utilitarian because the hardware is honestly closed.

What would fail the gate: system-ui, Inter, indigo, equal card grid, tinted cream + serif, skipping contrast math.

## Grades vs prior passes

| Lens | v1 (#86) | Enrich (#87) | Closeout (this) |
|---|---|---|---|
| Overall craft | ~3/5 | 4/5 (rejected as not designed) | **4.55/5** |
| Typeface | system-ui | system-ui | IBM Plex Sans (self-hosted) |
| Status empty | thin table | copy + table | meter + protocol list |
| Consent | checklist | rows | numbered protocol |
| A11y contrast | skipped in jsdom | skipped in jsdom | **token math in `npm run a11y`** |

## Rails (re-probed)

- `pyproject` `[project].dependencies == []`
- Bind `127.0.0.1` only; non-loopback Host/Origin refused
- CSP `script-src 'self'`; fonts from `'self'`
- Engine gates reused; UI does not rewrite advisory text
- No raw sensor egress; `/api/sensors/live` refused
- Presence render-only
- `/api/privacy/erase` complete

## Defaults chosen

| Choice | Value |
|---|---|
| Direction | Quiet Instrument |
| Typeface | IBM Plex Sans latin woff2 (OFL) |
| Charts | Local SVG |
| Live literature | Europe PMC, `SOMATIC_RESEARCH_LIVE`, off by default |
| Crisis | US 988 (engine) |
| Encryption at rest | Not added; 0600 JSON; documented limitation |
| LICENSE | untouched |
