# Design-skill audit trail (v3)

Quiet Instrument rebuilt as Bioluminescence. Source of truth: `planning/UI-BOLD-DIRECTION.md`. Visual target: `docs/ui-mockups/somatic-bold-mockup.html`. Astryx was **not** present. Refero MCP was **not** called.

## Design read

Product UI for one private user. Informational health instrument. Founder direction: **bold, dark, luminous, data-dense** without becoming hype.

Dials remain `VARIANCE 5 / MOTION 7 / DENSITY 8`. Dark is the shipped default. Light is a sibling with the same emerald and reduced glow.

## Bioluminescence spec → shipped surface

| Spec item | Where |
|---|---|
| Pine-black canvas `#07120E`, radial bloom, 44px instrument grid | `tokens.css` + `bio.css` on `html/body` |
| Luminous emerald `#35E7A6` / moss `#12A574` | Primary buttons, eyebrows, ring, Field body, brand mark |
| Cyan / amber / violet data accents | KPI tiles, Field gauges, occupancy, research charts (always labeled) |
| Coral `#FB7185` emergency only | `.alert` clinician banner + inspector "Emergency routing armed" |
| Layered translucent panels, emerald hairlines, glow-as-elevation | `.kpi`, `.tele`, `.ringcard`, `.gauge`, `.scoperows` |
| Space Grotesk + IBM Plex Sans + IBM Plex Mono (self-hosted OFL) | Display / body / numbers |
| 7-segment capability ring | Status (`CapabilityRing`) |
| KPI tiles + sparklines | Status; inspector grant trace (not a vital sign) |
| Glowing 3D body + occupancy waterfall + mono gauges | Field (R3F in-browser; SVG poster in headless) |
| Informational banner on every surface | `Heading` |
| Honest-null dignity | Large type, ink/muted, never coral |
| Dark default + light variant | `data-theme`, `initTheme` defaults dark; `?theme=` for capture |
| Breathing pulse | `.live-pulse` + GSAP reveals, `prefers-reduced-motion` gated |

## Frontend-skill map (unchanged stack, re-skinned)

| Skill | Surface |
|---|---|
| Vite + React IIFE | CSP-clean `app.js` |
| R3F + Drei + bloom + maath + troika + Theatre | Field / Presence, now luminous emerald |
| GSAP / Lenis | Reveals and smooth scroll; reduced-motion skip |
| Zustand | App state |
| Tailwind v4 (no preflight) | Utilities on Bioluminescence tokens |
| lil-gui | Field inspector |
| xterm.js | CLI tools (pine-black terminal) |

Skipped: Rapier, OpenTUI, talking-head, surprise audio. Same reasons as v2.

## Honesty labels

- Field body is a **synthetic template**, not a scan.
- Inspector sparkline is a **scope-grant trace**, not a vital.
- Banner copy: `Sandbox · synthetic · not a real person.`
- Hardware: `sandbox-verified; needs a real ESP32 to validate live`.

## Design-director score (this round)

**4.7 / 5.** Dark Status and Field match the approved mockup: pine-black canvas, instrument grid, KPI tiles, 7-segment ring, glowing Field poster + occupancy + gauges, telemetry rail, coral only on emergency routing. Light is the specified sibling (same emerald, reduced glow, AA cyan `#0C6A92`). Does not read as the old flat Quiet Instrument. Remaining 0.3 is headless WebGL (SVG poster instead of live bloom) and the palette capture running after demo grants.
