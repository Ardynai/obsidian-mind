# Sensor Privacy Boundary

Sensor data is local-first and private by default. Phase 7A stores only deterministic fake-backed placeholder metadata and never exports raw sensor data. Phase 7B extends that rule to WiFi CSI raw RF/CSI data. Phase 8A stages WiFi CSI references for source review only and adds no real capture path. Phase 8B adds local fake/sample WiFi CSI parser fixtures only and exports summary metadata only. Phase 8E scores only sanitized CSI replay metadata counts/statuses and exports no raw signal values. Phase 8F batches those sanitized replay summaries for tournament readiness only and does not add raw data export or ranking inputs. Phase 8G exports sanitized CSI evidence packs with counts, scores, contract versions, and fingerprints only. Phase 9A factors the reusable privacy and compatibility primitives into a generic sensor-evidence contract foundation for future sanitized providers, with CSI as the first implementation. Phase 9B adds generic compact artifact refs for sanitized evidence packs in reports and Fabric planning. Phase 9C adds a second neutral environment fixture provider that exports sanitized row/count/status metadata only. Phase 9D validates fixture-only evidence-provider config through a metadata-only registry before runtime dispatch. Phase 9E adds a public provider extension template and a toy count/status fixture proof through the same sanitized registry path. Phase 7C extends it to fake-backed personal baseline graph placeholders.

## Defaults

- Raw CSI, camera, microphone, wearable, thermal, environmental, and baseline data must not leave the machine without explicit configuration and consent.
- Raw RF/CSI data is local-first and private by default. Phase 7B collects, retains, and exports none.
- Sandbox sensor fixtures use `fixture://` references and fixed metadata only.
- `observe:sensor` is future permission vocabulary. Phase 7A uses fixture reads and sandbox placeholders, not live observation.
- Sensor provider metadata must declare no secrets, no network, no live sensor access, and no remote upload.
- No hardware is accessed.
- No ESP32, RTL8812AU, router, WiFi adapter, driver, monitor mode, packet capture, or WiFi device probing is used.
- No serial capture, SD-card read/write, MQTT/UDP listener, cloud endpoint, channel hopping, `tcpdump`, `tshark`, `aircrack-ng`, driver change, WiFi interface reconfiguration, or staged source execution is used.
- Phase 8B/8E/8G CSI parser/scoring/evidence-pack fixtures are local fake/sample fixtures only: no serial, no MQTT, no UDP, no pcap, no monitor mode, no live capture, no vital-sign inference, no signal-quality claim, no fixture-ref export in evidence packs, and no medical claim.
- Phase 9A/9B generic sensor-evidence helpers are metadata-only: contract identity, compatibility class, fingerprint, readiness status, closed privacy flags, sanitized diagnostics/counts, and run-relative artifact refs/hashes. They must reject raw keys, raw signal values, source IDs, provider/parser payload bodies, unsafe refs, absolute paths, credentials, network refs, and private staged-source refs.
- Phase 9B report and Fabric surfaces use compact `sensor_evidence_artifact_refs` for sanitized evidence packs. These refs carry only run-relative paths, SHA-256 hashes, provider/evidence kind, pack ID/fingerprint, compatibility classification, and closed privacy flags.
- Phase 9C environment evidence packs are fixture-only and metadata-only. They do not export fixture refs, fixture filenames, row bodies, raw values, source IDs, provider payload bodies, parser report bodies, parser summary bodies, unsafe refs, absolute paths, credentials, hardware access, network calls, live capture, or ranking input.
- Phase 9D registry metadata is sanitized and public-boundary only. Workflow validation errors are stable codes and paths; they must not echo rejected refs, absolute paths, URLs, credential values, device selectors, source IDs, provider/parser bodies, or private fixture names.
- Phase 9E toy counter evidence packs are examples/tests only and export count/status metadata, pack identity, deterministic fingerprint, and generic artifact refs. The toy fixtures prove extension mechanics without exporting row bodies, raw values, private fixture refs, unsafe refs, absolute paths, source IDs, provider payload bodies, credentials, live-capture fields, or ranking input.
- CSI parser report and parsed-summary artifacts are local diagnostics. Fabric planning can list them for local provenance, but they are marked outside the candidate package surface and are not the portable sensor-evidence refs.
- Personal profile and baseline graph artifacts are fake-backed local baseline placeholders only.
- No real health data is loaded and no real profile storage is performed.
- No database, external memory, Hindsight, Mem0, or Zep runtime is used.
- No personal health data or baseline data is exported.
- Phase 7G n-of-1 Fabric pack planning is private-only by default and exports
  no real personal data, personal health data, baseline data, raw sensor data,
  or raw RF/CSI data.

## Future Real Mode Requirements

Future real sensor adapters need:

- explicit user and subject consent
- local-first storage and private-by-default handling
- capture scope, environment, retention, and export controls
- privacy review
- safety review
- human review
- separate opt-in configuration
- separate WiFi CSI hardware and raw RF privacy review
- source-license review and cleared test fixtures before real CSI parser support
- explicit local storage consent before real profile or baseline storage
- data-locality review before real profile or baseline storage

Future real WiFi CSI use requires explicit consent from the operator, intended
subject, and all potentially affected people in the sensing area. Do not deploy
in shared, public, workplace, household, or care environments unless bystanders
are informed and consent is practical. WiFi CSI, RSSI, pcap, serial CSI logs,
SD-card CSVs, raw RF/CSI, derived features, embeddings, ReID sequences, pose
outputs, skeleton outputs, and activity labels are sensitive by default and may
reveal presence, motion, location, gait, posture, identity-like patterns, sleep
or respiration proxies, or bystander activity.

Do not reuse upstream MQTT endpoints, credentials, topics, or cloud publishing
code. Any future transport must be local-only by default, authenticated,
consent-gated, and disabled unless explicitly configured.

No sensor workflow may claim diagnosis, treatment, cure, emergency triage, clinician replacement, or real monitoring from Phase 7A artifacts. No diagnosis is made. No emergency triage is performed. Future real sensor mode requires explicit consent, local-first privacy controls, and safety review.

No Phase 7C baseline comparison is medical advice, diagnosis, treatment,
clinical interpretation, monitoring, or emergency triage. Future real baseline
storage requires explicit local storage consent, data-locality review,
local-first privacy controls, privacy review, safety review, human review,
retention/export controls, and separate opt-in configuration.

Phase 7D intervention tags are mock intervention metadata only. They provide no
recommendation, no prescription, no treatment recommendation, no medical
advice, no diagnosis, no emergency triage, no real monitoring, and no
reminders, automation, or scheduling. Medication placeholder disabled and
clinician review placeholder disabled are disabled metadata only. Response
evaluation is future planning only and must not become monitoring or
notification automation without explicit consent, human/clinical review, local
storage controls, safety gates, and no emergency-triage substitution.

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

Phase 7E response evaluation is fake-backed local research-only planning only.
It uses fixture trend labels only and no intervention effectiveness is claimed.
It provides no effectiveness claim, no recommendation, no prescription, no
treatment recommendation, no medical advice, no medication action, no clinician
action, no diagnosis, and no emergency triage. It creates no reminders,
automation, notification, scheduling, or real monitoring.

Phase 7G n-of-1 Fabric pack planning is planning-only and private-only by
default. No Fabric signing, catalog publication, transport, magnet, WebSeed,
seeding, upload, install, or execution is enabled. Future real packaging
requires explicit consent, redaction, license review, privacy review, safety
review, human review, local-first storage controls, retention/export controls,
and separate publication approval.
