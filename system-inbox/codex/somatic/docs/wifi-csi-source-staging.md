# WiFi CSI Source Staging

Phase 8A stages WiFi CSI reference sources outside the Somatic checkout for
read-only inspection. The staged sources are reference material only. They are
not vendored into Somatic, imported by Somatic tests, or wired into runtime
adapters.

## Staging Policy

- Staging root: `C:\AI\external-sources\somatic\wifi-csi\`
- Clone mode: shallow source clone with LFS smudge disabled.
- Dependencies installed: no.
- Package managers run: no.
- Setup scripts run: no.
- Hardware accessed: no.
- WiFi adapters, ESP32 devices, routers, drivers, monitor mode, packet capture,
  channel hopping, `tcpdump`, `tshark`, `aircrack-ng`, driver changes, WiFi
  interface reconfiguration, serial ports, SD cards, MQTT, UDP listeners, and
  CSI capture paths used: no.
- External APIs called: no, except Git clone/fetch for source staging.
- External repos modified: no.
- Source vendored into Somatic: no.
- Medical, clinical, monitoring, diagnosis, treatment, or emergency-triage
  claims made: no.

The machine-readable record is
`fixtures/sensors/csi/csi-reference-inventory.json`. The fixture is designed to
parse in CI without requiring these external clones to exist.

Phase 8B uses this staged-source review for format hints only. The parser
fixtures are Somatic-owned tiny CSV/JSONL files under `fixtures/sensors/csi/`;
no upstream parser, dataset, firmware, credential, transport, or runtime path is
copied.

## Staged Source Inventory

| Repo | Local path | Commit | License status | Purpose |
| --- | --- | --- | --- | --- |
| `NTUMARS/Awesome-WiFi-CSI-Sensing` | `C:\AI\external-sources\somatic\wifi-csi\Awesome-WiFi-CSI-Sensing` | `fc8e21f4392d16fa110f1e00952d7f6bfd8f78c0` | MIT via root `LICENSE` | Curated WiFi CSI bibliography, platform list, dataset list, and code-resource map. |
| `thu4n/ESP32-WiFi-Sensing` | `C:\AI\external-sources\somatic\wifi-csi\ESP32-WiFi-Sensing` | `9ebd9204cd695e9772a78f466532a7a99c790a67` | Root license unclear; nested `esp32-csi-tool/LICENSE` is MIT | ESP32 CSI collection, CSV parsing, model training, Jetson Nano inference, MQTT publishing, and Android subscriber example. |
| `MaliosDark/wifi-3d-fusion` | `C:\AI\external-sources\somatic\wifi-csi\wifi-3d-fusion` | `0c0f99e6af9fa1a22d850c45b8f23aa75f34f328` | Requires review: `LICENSE` says Apache-2.0; README badge says GPL-2.0; vendored third-party folders add separate license surfaces | Real-time WiFi CSI/RSSI motion detection, optional 3D pose/visualization bridge, training scripts, and web visualization. |
| `ruvnet/RuView` | Not staged | Conditional reference-only | Not inspected | Reassessable reference only. Do not copy, vendor, import, execute, or depend on it. |

## Per-Source Notes

### Awesome WiFi CSI Sensing

This source is a catalog, not a capture implementation. It is useful for
planning the future CSI research surface: learning-based, model-based, and
hybrid methods; CSI platforms such as Intel 5300, Atheros, Nexmon, ESP32 CSI
Tool, SDR, and router datasets; and caution areas such as data leakage,
privacy-preserving recognition, cross-environment generalization, pose,
occupancy, identification, respiration, fall detection, and multimodal sensing.

Somatic should not infer implementation readiness or license clearance from
linked papers and repositories. Future sample-pack work must inspect each
source independently before copying data, code, models, or benchmark material.

### ESP32 WiFi Sensing

This source demonstrates a hardware path around ESP32 CSI collection. The
README describes two ESP32 microcontrollers as transmitter/receiver, Jetson
Nano edge inference, collected datasets, model artifacts, notebooks, and MQTT
publication to subscribers. The nested ESP32 CSI Tool docs describe active
station, active access point, and passive collection subprojects; `idf.py flash
monitor`; serial output; optional SD-card CSV files; timestamp helpers; and
CSV analysis with Python or MATLAB.

Useful Somatic ideas are narrow: CSV can become a future fixture/sample-pack
format after consent and hardware review; capture provenance should record
clock synchronization limits; and capture metadata must remain separate from
model inference metadata.

Phase 8B mirrors only a tiny local fake ESP32-style `CSI_DATA` CSV shape. It
does not open serial ports, read SD cards, flash ESP32 firmware, publish MQTT,
or infer vital signs.

Somatic must not flash ESP32 firmware, open serial ports, run `idf.py`, read or
write SD-card data, publish MQTT messages, run TensorRT/CUDA inference, or
adopt the root repository while license status is unresolved. Do not reuse
upstream MQTT endpoints, credentials, topics, or cloud publishing code; any
future transport must be local-only by default, authenticated, consent-gated,
and disabled unless explicitly configured.

### WiFi 3D Fusion

This source is a broad real-time sensing system. The README describes ESP32 UDP
JSON, Nexmon plus `tcpdump`/`csiread`, monitor-mode RSSI, real-time movement
detection, person tracking, re-identification, optional 3D pose, Three.js/Open3D
visualization, Flask/WebSocket-style serving, Docker, CUDA, and continuous
learning. `requirements.txt` is heavy and includes NumPy, Open3D, OpenCV,
csiread, Flask, pandas, pyshark, requests, scapy, scikit-learn, scipy, CUDA
Torch packages, and VTK.

The `LICENSE` file says Apache-2.0 and also carries explicit research/safe-use
disclaimer text. The README badge says GPL-2.0. Vendored third-party folders add
more review surface: Person-in-WiFi-3D is Apache-2.0, NeRF2 is MIT, and the
`3D_wifi_scanner` folder has no obvious license file. Treat the license as
requiring review until upstream clarification.

Useful Somatic ideas are limited to future planning: keep source selection
explicit (`esp32`, `nexmon`, `radiotap`, or dummy), gate every source type
behind consent and local retention/export policy, and preserve strong safe-use
language around controlled environments and informed participants.

Phase 8B mirrors only a tiny local JSON-lines fixture shape with CSI-like sample
metadata. It does not start UDP listeners, parse pcap/Nexmon/radiotap captures,
use monitor mode, run `tcpdump`, or import NumPy/OpenCV/Open3D/PyTorch.

Somatic must not adopt packet capture, monitor mode, channel hopping,
`tcpdump`, `tshark`, `aircrack-ng`, driver changes, WiFi interface
reconfiguration, Nexmon, UDP listeners, Flask/WebSocket servers, Docker, CUDA
training, continuous learning, pose estimation, ReID, or person tracking as
default runtime. It must not copy source while license status requires review.

### RuView

RuView is reclassified for Phase 10G as conditional reference-only and
reassessable. It was not cloned into Somatic, copied, imported, executed, or
depended on. Recent v2 materials describe a Rust workspace and wifi-densepose
crate set with CSI preprocessing, phase sanitization, feature extraction,
vitals, hardware, training, and sensing-server crate claims. The reported
temporal embedding metric is representation-context evidence only; it is not
proof of downstream presence, vitals, pose, or deployment accuracy.

The earlier warning history remains active: broad overclaims, incompatible
model-loading concerns, and unverified deployment claims are still audit
warnings. Somatic must not adopt broad sensing, smart-home, hardware deployment,
or vitals claims from RuView without a separate validated real-mode phase.

Phase 10G also adds a booth-first planning profile for future work: one intended
subject, a small controlled booth, fixed AP plus 4-6 receiver-node metadata,
ESP32-S3 preferred radios, an empty-booth baseline concept, and
phase/conjugation/temporal-embedding research notes only. It explicitly skips
broad room-adaptation logic.

## Privacy And Security Cautions

WiFi CSI can be passive, bystander-visible only after disclosure, and capable of
inferring sensitive physical context. Future real WiFi CSI use requires explicit
consent from the operator, intended subject, and all potentially affected people
in the sensing area. Do not deploy in shared, public, workplace, household, or
care environments unless bystanders are informed and consent is practical.

WiFi CSI, RSSI, pcap, serial CSI logs, SD-card CSVs, raw RF/CSI, derived
features, embeddings, ReID sequences, pose outputs, skeleton outputs, and
activity labels are sensitive by default. They may reveal presence, motion,
location, gait, posture, identity-like patterns, sleep or respiration proxies,
or bystander activity. Future real mode requires local-first storage,
retention/export controls, redaction review, privacy review, safety review,
human review, and separate opt-in configuration.

Do not use Phase 8A staging to claim diagnosis, treatment, clinical
interpretation, medical monitoring, fall detection, emergency triage,
respiration or heart-rate monitoring, identity recognition, surveillance,
covert monitoring, production readiness, or validated pose estimation.
Deep-learning and pose references are upstream research context only.
