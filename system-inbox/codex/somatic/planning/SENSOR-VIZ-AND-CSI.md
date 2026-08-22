# Somatic — Autonomous Build: sensor visualization now + real ESP32-CSI lane (Grok 4.6)

You are **Grok 4.6**, sole builder for `Ardynai/somatic`. Build the piece that turns the sensor roster from a list into something you can *watch* — a visualization that shows a body/field **before any hardware is plugged in**, and a **real ESP32 WiFi-CSI ingest lane** so it lights up with live data when the founder connects a device. By yourself: self-review + self-merge on green, part after part, until it's all in. Only stop for the hard-stops.

**Step 0 of your first commit:** save this charter to `planning/SENSOR-VIZ-AND-CSI.md`.

## Ground it in the real code first (no invention)
Read these before building: `somatic/sensors/roster.py` (`SENSOR_ROSTER_MODALITIES`, `scan_sensor`, `SensorLane`), `somatic/sensors/csi.py` (existing CSI parsing), `somatic/evidence_bus/sandbox_adapters.py` (`SandboxModalityAdapter`, `_features_for`, `SensorHardwareDisabled`), `somatic/bridge/api.py` (the `/api/sensors/*` endpoints), and the UI shell. **Key hook:** the sandbox `csi` and `video3d` adapters already emit a synthetic `pose3d` (`joints: head[x,y,z], torso[x,y,z]`) plus a breathing-like envelope series and a peak-rate — render *that existing data*, don't invent a new shape.

## The rails hold (verified in the shipped build — don't regress)
- Core `pyproject` `dependencies == []`. The live ingest's default transport is **stdlib `socket` (UDP)** so the core stays dependency-free. DSP / serial / model libs go in the existing `[project.optional-dependencies]` extras (`csi`, `sensors`, `video`), lazy-imported, sandbox-simulated by default.
- **No raw sensor egress, ever.** Raw CSI IQ / frames / audio never leave the machine and are never stored as raw — the UI shows **derived features only** (amplitude/phase heatmap, motion energy, breathing rate, coarse pose). On-device only; nothing leaves `127.0.0.1`.
- Consent-gated (the roster path already requires `DATA_INGESTION` + `ANALYSIS_INSIGHT`); live capture requires an explicit grant and stays **off by default**. Right-to-erasure covers any stored sensor features. CSP stays `script-src 'self'` (render locally, no CDN).

## Part 1 — The sandbox "Field" visualization (works NOW, no hardware)
Add a real visual surface (e.g. a **Field / Body** view, and enrich the Sensors screen) that renders the **existing sandbox features** live:
- A **body skeleton** drawn from the sandbox `pose3d.joints` (head/torso now; lay the component out so more joints slot in later), animated across ticks.
- A **CSI/occupancy heatmap or waterfall** from the synthetic envelope series, and a **breathing/motion readout** from the peak-rate.
- Drive it by ticking `scan_sensor(...)` (or a small stream endpoint on the bridge) so it moves. Local `<canvas>`/SVG, CSP-safe, accessible (aria labels, reduced-motion), styled to the **Quiet Instrument** system.
- Label it unmistakably: **"Sandbox · synthetic · not a real person."** This is the demo the founder can show before plugging anything in.

## Part 2 — The real ESP32 WiFi-CSI ingest lane (lights up the same view)
Build a `csi` **live EvidenceSource** that turns real ESP32 CSI into the same features the viz already renders:
- **Transport (core, stdlib):** listen on a loopback **UDP** port for CSI packets streamed from an ESP32 (JSON or CSV lines). Parse → derive features (per-subcarrier **amplitude/phase**, **motion energy**, **breathing-rate** estimate, **presence/occupancy**). Optional **serial/USB** transport behind the `csi`/`sensors` extra (`pyserial`), lazy-imported. Heavier DSP (numpy/scipy) also extra-only; a stdlib fallback computes basic features so the core works with nothing installed.
- **Gating:** a per-modality live-sensor consent grant flips the `csi` lane from sandbox to live; **off by default**; `scan_sensor(live=True)` stays refused for every modality without a real adapter. When live CSI is on, the Field view shows the **real** heatmap/motion instead of the synthetic one — same components, real data. Raw CSI stays local; only features are shown; features are erasable.
- Keep it honest: one ESP32 yields **motion / presence / breathing + a raw-CSI heatmap** reliably; a recognizable **body pose/silhouette** is Part 4 (model + multiple units). Don't render a fake skeleton from one unit's CSI and imply it's a real body scan.

## Part 3 — Firmware + booth quickstart (`docs/hardware/esp32-csi.md`)
Write the real how-to (this is the "what do I do with my ESP32" doc):
- **Firmware:** flash **Espressif `esp-csi`** (github.com/espressif/esp-csi) or the **ESP32-CSI-Tool** (stevenmhernandez.github.io/ESP32-CSI-Tool); ESP32 / ESP32-S3 both work. Flash via ESP-IDF or Arduino-ESP32 + esptool.
- **Traffic source:** CSI is measured on *received* packets, so you need a steady WiFi sender — your router (ping flood) or a **second ESP32 as a TX beacon**. Document both.
- **Stream format:** define the exact UDP/serial line schema Somatic's ingest expects (timestamp, subcarrier amplitudes/phases, RSSI, unit-id) and give a tiny reference sketch/config that emits it to `127.0.0.1:<port>`.
- **Booth topology:** N ESP32s around the subject, each a tagged UDP stream, placement + rough time-alignment; how Somatic fuses multiple unit-ids. Be explicit that a clean silhouette needs the model in Part 4.
- **Subject consent (important for a booth):** a booth scans *other people*, not just the operator — add on-screen **subject-consent + signage** guidance and keep everything on-device. You can build and sandbox-test all of this, but you **cannot validate live capture** — mark it "sandbox-verified; needs a real ESP32 to validate live," never claim a live scan you didn't run.

## Part 4 — Booth fusion + pose model (roadmap; research-grade; founder-gated)
Spec, and stub the seams for, the real "body image": multi-unit CSI **fusion + calibration** and a **trained pose model** (reference the open WiFi-CSI pose / `wifi-3d-fusion` line of work) that maps CSI features → coarse body pose/occupancy. Keep it in optional extras, on-device, no core dep; mark it research-grade (needs training data or a pretrained model, ideally multiple units). Keep the existing `somatic/sensors/fusion.py` RF↔vision seam. Building/enabling this for real, and any model weights, is **founder-gated** — leave it as a documented, wired-but-off lane.

## How you work + authorization
Read first; build additively from real symbols. Tight PRs (viz → ingest → docs → fusion seam). Green each time: `python -m unittest` (sandbox/UDP-loopback tests, deps-free; extra-only tests skip cleanly), `python -m somatic doctor`, ruff clean, `ui/` build + a11y clean, **core `dependencies == []`**. Adversarial self-review: try to make the lane egress raw CSI, reach live capture without consent, or bind off-loopback — all must fail. Then merge yourself on green. Fresh clone off `origin/main`; never build in the locked `C:\AI\somatic`.

## Only stop for these (log in `planning/AUTONOMOUS-LOG.md`; keep working other parts)
- Adding a dep to the **Python core**, weakening a safety/privacy rail (raw egress, consent, loopback, no-raw), or faking a live/hardware result — stop instead.
- Irreversible/external/costly: releasing / deploying / publishing a public URL, **buying hardware**, spending money, emailing/posting, deleting user data, force-push. Serving on `127.0.0.1` is fine.
- **LICENSE stays untouched** (founder decides later). Turning on the real pose **model** or shipping model weights is founder-gated. Small choices (UDP port default, heatmap palette within the token system) — pick the safe default, note it, continue.
- Stuck on a lane that truly needs the physical ESP32 — ship the sandbox + ingest software, mark it "needs hardware to validate," move on.

## Done
When the Field/Body view renders the sandbox pose + heatmap live with no hardware, the ESP32 UDP-CSI ingest lane feeds the same view (sandbox-verified, real-hardware quickstart written), and the booth/model path is documented + wired-but-off — self-reviewed, rails intact, merged to `main` — update `planning/AUTONOMOUS-LOG.md` (what's real vs sandbox vs needs-hardware, founder-defaults, anything unsure) and stop. Founder-gated: the **LICENSE**, **buying/validating hardware**, enabling the **pose model**, and any **public release**.
