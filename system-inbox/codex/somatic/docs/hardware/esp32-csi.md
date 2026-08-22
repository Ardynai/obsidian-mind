# ESP32 WiFi-CSI quickstart

Status: **sandbox-verified; needs a real ESP32 to validate live.**

This document is the "what do I do with my ESP32" guide for Somatic's loopback CSI ingest. The Field / Body view already renders **sandbox** pose, occupancy, and a breathing-like rate with no hardware. The live lane uses the **same UI components** for derived features (heatmap, motion, presence, breathing estimate). It does **not** draw a skeleton from one radio.

Somatic has not been validated against a physical ESP32 in this change. Do not treat a sandbox tick, a synthetic UDP packet, or a loopback demo as a live body scan.

## What one ESP32 can actually show

| Output | One ESP32 | Booth (N units) | Part 4 pose model |
| --- | --- | --- | --- |
| Amplitude / occupancy heatmap | Yes (derived; raw IQ discarded) | Fused occupancy row | Not required |
| Motion energy / presence | Yes (research-grade estimate) | Stronger with more angles | Not required |
| Breathing-rate estimate | Peak-count (stdlib) or FFT band if `numpy` extra is installed | Same | Not required |
| Recognizable body pose / silhouette | **No.** Field hides the skeleton in live mode. | Still no, without the model | Founder-gated, off, no weights in-repo |

## Rails (do not weaken these)

- Core Python `dependencies` stay `[]`. UDP ingest is stdlib `socket`.
- Bind **127.0.0.1** (or `localhost`) only. Default port **53721** (`SOMATIC_CSI_UDP_PORT`). Off-loopback bind raises `LoopbackBindError`. Non-loopback senders are dropped.
- Raw CSI IQ / amplitude / phase / RSSI never leave the machine, are never stored, and are never sent to the UI. Features only: `occupancy_row`, `amp_heatmap`, `phase_heatmap`, `envelope`, `motion_energy`, `breathing_rate_per_min`, `presence`, `link_strength`.
- Live ingest is **off by default**. It needs `data-ingestion` + `analysis-insight` **and** an explicit live-sensor grant with **subject consent**.
- Right-to-erasure (`consent erase` / Privacy → erase) deletes live grants and stored feature frames.
- CSP stays `script-src 'self'`. Nothing is served off `127.0.0.1`.

## Why the ESP32 does not UDP to `127.0.0.1` itself

`127.0.0.1` on the ESP32 is the **chip's** loopback, not the PC. Somatic's ingest also **refuses** to bind a LAN address, and it **drops** packets whose sender is not loopback.

The supported hop onto the PC is therefore:

```
ESP32 firmware
  --USB serial (JSON or CSV lines)-->
host forwarder (this repo: examples/hardware/csi_udp_forward.py)
  --UDP 127.0.0.1:53721-->
python -m somatic sensor-roster listen
  (or the Field page after a live grant)
```

Optional `pyserial` lives in the `csi` / `sensors` extras (`pip install "somatic[csi]"`). The core never imports it. A stdlib-only path is: firmware prints lines on USB-CDC; the forwarder reads **stdin** (pipe from any serial tool) and sends loopback UDP.

WiFi UDP from the ESP32 to the PC's LAN IP is **not** accepted by Somatic. Do not open `0.0.0.0` to make that work.

## Firmware

ESP32 and ESP32-S3 both work as CSI receivers. Flash with ESP-IDF or Arduino-ESP32 + esptool.

### Espressif `esp-csi`

Source: [github.com/espressif/esp-csi](https://github.com/espressif/esp-csi)

1. Install [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/).
2. Clone `esp-csi` and build one of the CSI receive examples for your target (`esp32` or `esp32s3`).
3. Configure the example for **station** mode on the same AP as your traffic source.
4. Change the example's log/print path so each CSI frame becomes **one line** on USB serial in a format below (JSON preferred). Do not ship raw IQ to the network.
5. Flash with `idf.py -p <PORT> flash monitor` (or esptool).

### ESP32-CSI-Tool

Docs: [stevenmhernandez.github.io/ESP32-CSI-Tool](https://stevenmhernandez.github.io/ESP32-CSI-Tool/)

1. Flash the **CSI receiver** sketch (Arduino-ESP32) onto the unit that will sit in the booth.
2. The stock tool prints `CSI_DATA,...` CSV lines on serial. Somatic's ingest accepts that shape: `CSI_DATA,<frame_id>,<timestamp>,<unit_id>,<rssi>,"<iq pairs>",...`
3. IQ pairs are converted to occupancy + wrapped phase **in memory** and then dropped. They are not stored.

A minimal Arduino sketch that prints Somatic JSON (not IQ) is `examples/hardware/esp32_csi_serial.ino`. Adapt it to your CSI API (`esp_wifi_set_csi_rx_cb` on ESP-IDF, or the CSI-Tool callback). The sketch in this repo is a **line-format reference**, not a complete CSI driver.

## Traffic source (CSI is receive-side)

CSI is measured on **received** packets. A silent room yields almost no frames. You need a steady sender on the same channel/AP.

### Option A — ping flood from the PC (simplest)

On the host, while the ESP32 is associated to your AP:

```powershell
ping -t -l 32 <ap-or-gateway-ip>
```

On Unix: `ping -i 0.2 <ap-or-gateway-ip>`. This is a local diagnostic flood, not a WAN attack. Stop it when you are done.

### Option B — second ESP32 as a TX beacon

Flash a second board as a WiFi **transmitter** (periodic UDP/ICMP to the AP, or an `esp-csi` TX example). Place it opposite the receiver so the subject sits in the path. Tag receivers with distinct `unit_id` values; the TX board does not need to send CSI.

## Stream format (what ingest expects)

One datagram or serial line. UTF-8. Max **8192** bytes. Preferred JSON:

```json
{
  "v": 1,
  "ts": 1710000000.123,
  "unit_id": "esp32-a",
  "rssi": -48,
  "amp": [0.12, 0.40, 0.88, 0.41],
  "phase": [-0.2, 0.0, 0.3, -0.1]
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `amp` (aliases: `occupancy`, `subcarriers`) | Yes, unless `iq`/`csi`/`csi_data` is present | Per-subcarrier amplitudes. Ingest normalizes to 0..1 and keeps at most 64 bins. |
| `phase` (aliases: `ph`, `phases`) | No | Wrapped to 0..1 for `phase_heatmap`. Never exported under the key `phase`. |
| `iq` / `csi` / `csi_data` | Alternative to `amp` | Interleaved I/Q floats. Converted then **discarded**. |
| `ts` / `timestamp` | No | Unix seconds; default is host time. |
| `unit_id` / `unit` | No | Default `esp32`. Used by booth fusion. |
| `rssi` | No | Mapped to `link_strength` only. The `rssi` key is stripped. |

CSV accepted as well:

1. **CSI_DATA / CSI** (ESP32-CSI-Tool-ish):  
   `CSI_DATA,<frame_id>,<ts>,<unit_id>,<rssi>,"<i q i q ...>"`
2. **Simple CSV:** `ts,unit_id,rssi,amp0,amp1,...`

Host-side emit (stdlib, no ESP32):

```powershell
python examples/hardware/csi_udp_forward.py --demo
```

That flag sends **synthetic** packets. It is for lighting up the live Field path without hardware. It is not a live scan.

Real serial (after `pip install "somatic[csi]"`):

```powershell
python examples/hardware/csi_udp_forward.py --serial COM5 --baud 115200 --unit-id esp32-a
```

Stdlib pipe (any serial monitor printing lines):

```powershell
Get-Content -Path \\.\COM5 -Wait | python examples/hardware/csi_udp_forward.py --stdin
```

## Run Somatic on the host

1. Grant the two analysis scopes (UI Consent screen, or CLI):

   ```powershell
   python -m somatic consent grant data-ingestion,analysis-insight
   ```

2. Record **subject consent**, then grant live CSI (still off until you do this):

   ```powershell
   python -m somatic sensor-roster live-grant --subject-consent
   python -m somatic sensor-roster listen --grant data-ingestion,analysis-insight
   ```

   Listen binds `127.0.0.1:53721` (or `SOMATIC_CSI_UDP_PORT`). Ctrl+C stops it.

3. Start the forwarder (demo or serial) in another terminal.

4. Open Field (`python -m somatic ui` → Field). Watch sandbox first. Then **Grant live CSI ingest** (check subject consent) and **Watch live CSI (loopback)**. The skeleton hides; the heatmap / motion / breathing readout should move when packets arrive.

Revoke: `python -m somatic sensor-roster live-revoke`. Erase features + grants: `python -m somatic consent erase`.

## Booth topology (N ESP32s)

Place 4–6 receivers around the subject (front, back, two sides, optional elevation). One AP. One TX beacon or ping source. Each receiver is a **tagged** stream (`unit_id` unique). USB hubs are the honest way to keep every hop on the host; do not bind Somatic to the LAN.

Time alignment is **nearest-frame / caller-supplied snapshots**, not a PTP clock. Somatic averages occupancy rows:

```powershell
# conceptually: POST /api/sensors/fuse-units
# { "units": [ { "unit_id": "esp32-a", "occupancy_row": [...] }, ... ] }
```

`fuse_csi_units` does not invent joints. A clean silhouette needs the Part 4 model (founder-gated, optional extra, no in-repo weights). The existing sandbox RF↔vision seam (`sensor-roster fuse`) still averages **simulated** CSI + depth joints only.

## Subject consent and signage

A booth can scan **other people**, not just the operator. Before a live grant:

- Confirm you are the only subject, **or** every person in the field consented.
- Put on-device signage in view: that this is an informational WiFi-CSI demo, not a medical device, not a body scanner, data stays on this machine, and anyone can refuse.
- Keep capture local. Do not stream features off `127.0.0.1`.
- Right-to-erasure covers stored feature frames.

The Field page repeats this as a required checkbox. The grant API returns 400 without `subject_consent: true`. This is not one of the seven core consent scopes; it is a separate default-OFF hardware grant (`~/.somatic/sensor-live.json`).

## Part 4 pose model (wired, off)

Research-grade CSI pose (see the open WiFi-CSI pose / `wifi-3d-fusion` line of work) is **founder-gated**:

- Env `SOMATIC_CSI_POSE_MODEL=1`
- Weights file at `SOMATIC_CSI_POSE_WEIGHTS` on this machine
- `csi` extra (numpy) installed

No weights ship in this repository. Even with the flag on, inference currently returns **empty joints** until the founder supplies a real on-device model. Enabling the model, buying hardware, and any public release stay founder-gated.

## Honesty checklist

- Field sandbox banner: `Sandbox · synthetic · not a real person.`
- Live payloads include `hardware_validation`: `sandbox-verified; needs a real ESP32 to validate live`.
- `LIVE_SENSOR_INTEGRATION_IMPLEMENTED` remains **False** (webcam/BLE/CSI-as-body-scan are not done). `LIVE_CSI_UDP_INGEST_IMPLEMENTED` is True for this loopback lane.
- `/api/tools` keeps `csi_live_capture: false` and reports `csi_udp_ingest: true`.
