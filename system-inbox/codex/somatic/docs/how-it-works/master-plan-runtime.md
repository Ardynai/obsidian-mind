# Master-plan runtime (sandbox)

The north-star in `planning/SOMATIC_MASTER_PLAN.md` is wired as **stdlib sandbox plugins**. Core `dependencies` stay `[]`. Advanced packages (OpenCV, NeuroKit2, librosa, NumPyro, MiniCPM, Duix) are optional extras and are **never imported** by these paths.

## Commands

| Command | Consent | What it does |
| --- | --- | --- |
| `python -m somatic bus run --hypothesis "..." --grant analysis-insight` | `analysis-insight` | Evidence Bus loop over sandbox adapters (every modality). |
| `python -m somatic sensor-roster list` | none | Roster + extra availability. Hardware stays closed. |
| `python -m somatic sensor-roster scan --modality csi --grant data-ingestion,analysis-insight` | ingestion + insight | Synthetic live-scan ticks. `--live` is CSI loopback or on-device camera pose and stays refused without a per-modality live grant. |
| `python -m somatic sensor-roster live-grant --subject-consent` | extra hardware grant | Default-OFF live CSI grant. `--modality video3d` grants camera pose. Not one of the seven core scopes. |
| `python -m somatic sensor-roster listen --grant data-ingestion,analysis-insight` | ingestion + insight + live grant | Bind `127.0.0.1:53721` for derived features. |
| `python -m somatic sensor-roster fuse --grant data-ingestion,analysis-insight` | ingestion + insight | RF↔vision pose fusion of simulated joints. |
| `python -m somatic science run --goal "..." --grant autonomous-research,analysis-insight` | research + insight | Tournament + teams + bus + Beta belief + falsifier. Biosecurity refuse+log. |
| `python -m somatic avatar speak --verdict "..." --grant ai-advisory` | `ai-advisory` | Render-only Scientist/Doctor restatement. TTS/head off. |
| `python -m somatic bench-run --grant autonomous-research,analysis-insight` | research + insight | Score the sandbox ripasudil/dAMD fixture. |
| `python -m somatic evidence-verify --file artifact.json` | none | Re-check content-addressed SHA-256. P2P distribution disabled. |

## Safety rails

- Consent default-OFF; these commands call `require_consent`.
- `emergency_screen` short-circuits the bus, science loop, and avatar.
- Biosecurity is a **name refuse-list** (no synthesis/uplift).
- Sensor privacy: no raw frames, PCM, CSI IQ, or BLE identifiers; local-first; `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` remains false. Loopback CSI ingest is a separate default-OFF lane (`LIVE_CSI_UDP_INGEST_IMPLEMENTED`). On-device camera pose is a separate default-OFF lane (`LIVE_VIDEO_POSE_IMPLEMENTED`) in the `video` extra.
- Advisory output still goes through `frame_advisory`.
- No hardcoded medical normals; sandbox numbers are labeled simulated.

## Where to read

- `somatic/evidence_bus/` — records, adapters, loop
- `somatic/sensors/roster.py` + `fusion.py` + `live_csi.py` + `live_video.py` + `video_processor.py` + `video_pose.py` + `field.py` + `pose_model.py`
- Hardware how-to: `docs/hardware/esp32-csi.md` (sandbox-verified; needs a real ESP32 to validate live)
- `somatic/science/`
- `somatic/presence/avatar.py`
- `somatic/bench/runner.py`
- `somatic/provenance/cas.py`
