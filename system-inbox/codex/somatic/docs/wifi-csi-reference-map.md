# WiFi CSI Reference Map

Phase 8A stages the named WiFi CSI references under
`C:\AI\external-sources\somatic\wifi-csi\` and inspects them read-only for
license, capture, dependency, privacy, and safety signals. The staged sources
remain reference-only. Somatic does not copy source, vendor code, import
external packages, install dependencies, run package managers, access hardware,
run WiFi adapters, run packet capture, use monitor mode, flash ESP32 devices,
open serial ports, read or write SD-card data, start MQTT/UDP listeners,
reconfigure WiFi interfaces, run `tcpdump`/`tshark`/`aircrack-ng`, or implement
a real CSI runtime.

The detailed staging record is in
`docs/wifi-csi-source-staging.md`, and the machine-readable inventory is
`fixtures/sensors/csi/csi-reference-inventory.json`.

Phase 8B uses the references only for format hints. The Somatic parser accepts
local fake/sample fixtures only and does not copy upstream parsers, datasets, or
runtime paths.

## Local Inventory

| Reference | Local status | Phase 8A handling |
| --- | --- | --- |
| `NTUMARS/Awesome-WiFi-CSI-Sensing` | Staged at `C:\AI\external-sources\somatic\wifi-csi\Awesome-WiFi-CSI-Sensing`, commit `fc8e21f4392d16fa110f1e00952d7f6bfd8f78c0`, MIT via root `LICENSE` | Catalog-only reference for research taxonomy, platforms, datasets, privacy/data-leakage concerns, and future sample-pack planning. |
| `thu4n/ESP32-WiFi-Sensing` | Staged at `C:\AI\external-sources\somatic\wifi-csi\ESP32-WiFi-Sensing`, commit `9ebd9204cd695e9772a78f466532a7a99c790a67`, root license unclear with nested ESP32 CSI Tool MIT license | Reference for ESP32 active/passive collection concepts, CSV output, timestamping limits, model/inference separation, and consent-gated future capture provenance. |
| `MaliosDark/wifi-3d-fusion` | Staged at `C:\AI\external-sources\somatic\wifi-csi\wifi-3d-fusion`, commit `0c0f99e6af9fa1a22d850c45b8f23aa75f34f328`, license requires review because `LICENSE` says Apache-2.0 while README badge says GPL-2.0 and vendored third-party folders add separate surfaces | Reference for real-time source-type taxonomy and safe-use warnings only. Do not copy while license requires review. |
| `ruvnet/RuView` | Conditional reference-only and not staged | Reassessable metadata reference only. Do not depend on, import, vendor, copy, execute, or use as an implementation source. |

## Adoption Rule

The staged references may inform future planning only after their specific
source, license, and privacy constraints are carried into a Somatic-owned design
review. None of them is a runtime dependency. No staged code is copied into
Somatic.

Future real WiFi CSI work must stay disabled by default and require explicit
consent from the operator, intended subject, and all potentially affected people
in the sensing area. It must not be deployed in shared, public, workplace,
household, or care environments unless bystanders are informed and consent is
practical. It also requires local-first storage, raw RF/CSI retention and export
controls, hardware review, license review, security review, privacy review,
safety review, human review, and separate opt-in configuration.

RuView is conditional reference-only for Phase 10G. Somatic preserves the prior
warning history around broad overclaims, incompatible model-loading concerns,
and unverified deployment claims. V2 materials can be tracked for reassessment,
but Somatic does not run RuView, download models, flash devices, bridge
smart-home systems, or adopt downstream sensing/vitals/pose accuracy claims.

The future WiFi CSI direction is booth-first: a single intended subject in a
small controlled booth, fixed AP plus 4-6 receiver-node metadata, ESP32-S3 as
the preferred radio family, an empty-booth baseline concept, and
phase/conjugation/temporal-embedding ideas as research notes only. Broad
room-adaptation logic remains out of scope.

## Safety Boundary

Phase 8A adds source inventory only. It does not use real WiFi capture, raw
RF/CSI streams, hardware drivers, device probing, network code, clinical
interpretation, monitoring claims, or medical claims.

Phase 8B adds local fixture parsing only. It has no serial, no MQTT, no UDP, no
pcap, no monitor mode, no live capture, no vital-sign inference, and no medical
claim.

The staged sources mention surveillance-sensitive capabilities and artifacts
such as occupancy, human identification, gesture recognition, respiration, fall
detection, sleep, pose, person tracking, re-identification, monitor mode, pcap
capture, MQTT publication, UDP streams, serial/SD-card CSI logs, raw RF/CSI,
RSSI, derived features, embeddings, ReID sequences, pose outputs, skeleton
outputs, and activity labels. Those capabilities remain future-only and blocked
unless a later real-mode phase adds explicit consent and review gates.

Upstream language about real-time person detection, monitoring, fall detection,
vital signs, respiration, heart rate, sleep, pose, ReID, identity-like
recognition, continuous learning, or production readiness is research context
only. It is not a Somatic capability, validation, medical-monitoring claim,
diagnosis claim, emergency-triage claim, identity-recognition claim, or
pose-estimation claim.
