# Sensors And CSI

## Owns

Fixture-only sensor planning, sanitized WiFi CSI replay, the sandbox roster, the Field snapshot, and loopback CSI ingest:

- `somatic/sensors/`
- `somatic/providers/sensors.py`
- `fixtures/sensors/`
- `examples/sensor-evidence-demo/`
- `examples/wifi-csi-demo/`
- `examples/hardware/` (host forwarder + serial line-format sketch)
- `docs/hardware/esp32-csi.md`

## Main Flow

The sandbox sensor provider creates a fake stream plan, deterministic observations, a feature set, and an Evidence Bus record. WiFi CSI fixture refs are resolved only under `fixtures/sensors/csi/`, parsed as supported CSV/JSONL formats, and summarized without exporting raw signal values.

Sensor evidence providers are registered in `somatic/sensors/registry.py`. The registry validates workflow config, publishes provider metadata, and maps generated evidence packs to artifact refs.

The Field view ticks `scan_sensor` (sandbox), loopback CSI features (live CSI grant), or on-device camera pose (live `video` / `video3d` grant). Live CSI binds `127.0.0.1` only. Camera pose uses MediaPipe on-device and never stores or emits raw frames. Status: sandbox-verified; CSI needs a real ESP32 to validate live.

## Gotchas

- CSI parser outputs are sanitized metadata. They must not expose raw CSI arrays, RSSI, source IDs, absolute paths, or live capture data.
- Fixture refs use a constrained `fixture://sensors/csi/...` shape. Absolute paths and remote schemes are rejected.
- The Phase 8 fixture parser still has no MQTT/UDP listener (`no_mqtt_udp_listener`). The new loopback ingest is a separate module (`somatic/sensors/live_csi.py`).
- Raw CSI IQ never hits disk or the UI. Derived keys only (`occupancy_row`, heatmaps, envelope, motion, breathing, presence).
- Live CSI is off until `data-ingestion` + `analysis-insight` + live-sensor grant with subject consent. Live `video` / `video3d` camera pose uses the same per-modality grant (default OFF) and stays sandbox-simulated until granted.
- `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` remains false. One ESP32 is not a body scan. The Part 4 CSI pose model is founder-gated and off. Camera pose is the MediaPipe lane in the optional `video` extra (lazy import, Apache-2.0).
- Hardware access, packet capture, monitor mode, WiFi probing, unconsented camera/microphone access, WebRTC/cloud frame streaming, and clinical interpretation remain blocked. Raw frames never leave the machine.

## Start Reading

Start with `SandboxSensorProvider` in `somatic/sensors/sandbox.py`, then `somatic/sensors/csi_parser.py`, then the roster in `somatic/sensors/roster.py`, then Field in `somatic/sensors/field.py`, CSI ingest in `somatic/sensors/live_csi.py`, and camera pose in `somatic/sensors/video_processor.py` + `somatic/sensors/video_pose.py`. Hardware how-to: `docs/hardware/esp32-csi.md`.
