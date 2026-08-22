# Somatic UI — "Bioluminescence" bold visual direction

The target that `docs/ui-mockups/somatic-bold-mockup.html` renders. Bold, dark, dimensional, data-dense — a premium sensing instrument where the user's living signals **glow**. The opposite of the flat white "Quiet Instrument." Bold **but trustworthy**: calm-luminous, not neon-gamer; this is still an informational health tool.

## Mood
A calm, high-end bio-futurist cockpit. Deep pine-black canvas, luminous emerald as the "signal" color, a small set of data accents (cyan / amber / violet), subtle bloom/glow on live elements, faint instrument grid. Confident display type, mono for all numbers. Everything reads as *alive* and *measured*.

## Palette (dark-first; ship a light variant too)
Backgrounds: `--bg0:#07120E` `--bg1:#0B1712` `--bg2:#10201A` `--bg3:#173029`
Ink: `--ink:#EAF5EF` · muted `--muted:#93AC9F` · faint `--faint:#516A5F`
Signal (brand, luminous): `--emerald:#35E7A6` · solid fill `--moss:#12A574` · dim `#1E6B4E`
Data accents (categorical, per dataviz — never color-only, always labeled): cyan `#4CC4F5` (RF/occupancy), amber `#F5B84A` (motion/energy), violet `#AE97F7` (research/evidence).
**Coral `#FB7185` is reserved for emergency ONLY** — it appears nowhere else, so red always means "see a clinician."
Lines: emerald hairline `rgba(53,231,166,.16)`; neutral `rgba(255,255,255,.06)`. Glow: `0 0 24px rgba(53,231,166,.30)`.
Light variant: warm off-white `#F4F7F5` canvas, same luminous emerald + accent set at higher saturation, gl!ow reduced.

## Type
Display: a strong geometric grotesk (self-hosted OFL — **Space Grotesk** or similar), big, tight tracking, for hero numbers/titles. Body: Inter / IBM Plex Sans. **Mono (IBM Plex Mono) for every number, label, code, status** — the "instrument readout" feel. Uppercase micro-labels with wide letter-spacing.

## Surfaces & texture (the "bold" is here)
Layered translucent panels (`linear-gradient` over `--bg`, 1px emerald hairline, 14–18px radius), elevation by **glow** not just shadow, a faint 44px instrument grid masked into the canvas, radial accent bloom behind key panels, occasional pulsing hairline. Not flat.

## Data-viz everywhere (dataviz skill)
Every surface carries a signature visualization: **Status** = a 7-segment radial "capability ring" + KPI tiles with sparklines; **Field** = the glowing 3D body + occupancy waterfall + big mono gauges; **Consent** = glowing segmented toggles with a mini activity trace; **Research/Analyze** = luminous line/area charts. Numbers animate (count-up). Accessible: never color-only, labels + values on everything, AA contrast on dark.

## Motion (GSAP / Theatre / Lenis — all `prefers-reduced-motion` gated)
Live elements **breathe** (slow luminous pulse). Route changes reveal with presence (staggered fade/rise). Values animate to their number. The 3D body slowly rotates with bloom. Smooth scroll. Nothing frantic — calm and premium.

## Density & layout
Keep the three-column cockpit (spine · main · telemetry rail) but **fill it**: KPI tile rows, multi-panel dashboards, the rail becomes a rich telemetry readout with a live sparkline. More visible controls, filters, inspectors. Feels capable, not empty.

## Trust guardrails (non-negotiable — it's a health tool)
Bold must not become alarming. Keep the informational banner prominent on every surface; emergency routing uses the **only** red in the system; no fake vitals or clinical certainty; honest-null still rendered with dignity (large calm type, no error-red). Luminous ≠ loud. If a choice reads as "hype/crypto/gamer," it's wrong — aim "high-end scientific instrument."

## Accessibility
WCAG 2.1 AA on the dark canvas (verify token contrast — glow is decorative, never the only signal), full keyboard nav, visible focus rings (emerald), reduced-motion path, non-3D fallback for the Field. `npm run a11y` → 0 axe violations.
