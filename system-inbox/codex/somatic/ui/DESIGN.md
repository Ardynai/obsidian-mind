# Design System: Somatic Bioluminescence

**Project ID:** local-loopback. Visual source of truth: `planning/UI-BOLD-DIRECTION.md` and `docs/ui-mockups/somatic-bold-mockup.html`.

## 1. Visual Theme & Atmosphere

Calm, high-end bio-futurist cockpit. Deep pine-black canvas, luminous emerald as the signal color, cyan / amber / violet as labeled data accents. Distinctiveness lives in the **7-segment capability ring**, KPI tiles, glowing Field body, and mono instrument readouts. **Dark is the default.** Light is a first-class sibling with the same emerald and reduced glow.

Taste dials: **VARIANCE 5 / MOTION 7 / DENSITY 8**. Bold but trustworthy: never hype, crypto, or gamer neon.

## 2. Color Palette & Roles

| Role | Dark (default) | Light | Use |
|---|---|---|---|
| Canvas | `#07120E` | `#F4F7F5` | Page field |
| Spine / panels | `#0B1712` / `#10201A` | `#E8F0EB` | Layered surfaces |
| Ink | `#EAF5EF` | `#0B1712` | Body (≥7:1) |
| Muted | `#93AC9F` | `#3D5348` | Secondary (≥4.5:1) |
| Signal | `#35E7A6` | `#0E7A58` | Live glow, eyebrows |
| Solid fill | `#12A574` | `#12A574` | Primary buttons (ink `#04140D`) |
| Cyan | `#4CC4F5` | `#0C6A92` | Occupancy / RF (labeled; AA on light canvas) |
| Amber | `#F5B84A` | `#9A6B12` | Motion / energy (labeled) |
| Violet | `#AE97F7` | `#5D4DB0` | Research / evidence (labeled) |
| Coral | `#FB7185` | `#C43B52` | Emergency routing **only** |
| Hairline | `rgba(53,231,166,.16)` | `rgba(14,122,88,.22)` | Panel edges |

Glow is elevation: `0 0 24px rgba(53,231,166,.30)` on dark, reduced on light.

## 3. Typography Rules

Display: **Space Grotesk** (self-hosted OFL) for heroes and gauges. Body: **IBM Plex Sans**. Mono: **IBM Plex Mono** for every number, label, code, and status. Uppercase micro-labels with wide tracking. No em dashes.

## 4. Component Stylings

- **Buttons:** 10px corners, 44px min height. Primary is moss-to-emerald gradient + glow. Erasure is outlined, not coral.
- **Layout:** spine · main · telemetry rail. Command palette (`Ctrl+K`). Instrument grid masked into the canvas.
- **Emergency:** translucent coral panel, left bar. Coral appears nowhere else.
- **Honest-null:** large display type, muted body, never error-red.
- **Charts:** local SVG, labeled, never color-only.

## 5. Layout Principles

8px grid. Spine ~15rem. Desktop: three columns. Status hero is Space Grotesk plus the capability ring.
