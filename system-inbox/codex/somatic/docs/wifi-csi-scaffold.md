# WiFi CSI Scaffold

Phase 7B adds a WiFi CSI planning scaffold for the sensor lane. It is fake-backed metadata only, disabled by default, and standard-library only. Phase 8A stages reference sources outside the Somatic checkout for source review only; it does not add a real CSI runtime. Phase 8B adds a standard-library parser scaffold for local fake/sample fixtures only. Phase 8C freezes that scaffold as a stable offline parser contract with deterministic replay validation. Phase 8D routes fixture replay through the sandbox sensor provider. Phase 8E adds sanitized replay evidence scoring metadata. Phase 8F adds sanitized fixture-group batch evaluation for tournament readiness metadata only. Phase 8G adds a sanitized CSI evidence-pack export contract. Phase 8I adds v1 evidence-pack compatibility and fingerprint hardening. Phase 9A introduces the generic sanitized sensor-evidence contract foundation underneath CSI. Phase 9B uses that foundation for compact run-relative evidence-pack artifact refs in run reports and Fabric planning.

## Scope

- `somatic.sensors.csi` defines `CsiCapturePlan`, `CsiFeaturePlan`, `CsiFeatureSet`, `CsiPrivacyBoundary`, and `CsiHardwareProfile`.
- The sandbox n-of-1 provider attaches CSI planning metadata to `sensor_feature_set.json`, `sensor_evidence_record.json`, and `n_of_1_summary.json`.
- Placeholder CSI features include `respiratory_rate`, `heart_rate_placeholder`, `hrv_placeholder`, `motion_score`, `posture_state`, `sleep_state_estimate`, `fall_risk_placeholder`, `pose3d_placeholder`, and `confidence`.
- Fixtures live under `fixtures/sensors/csi/`.
- Phase 8A source inventory lives in `docs/wifi-csi-source-staging.md` and `fixtures/sensors/csi/csi-reference-inventory.json`; Phase 10G extends it with conditional RuView reference status and booth-first planning metadata.
- Phase 10G source-boundary helpers live in `somatic.sensors.csi_adapter` and validate metadata before CSI planning summaries consume it.
- Phase 10H shared real-mode readiness gates live in `somatic.safety.adapter_readiness` and keep CSI source status blocked until every explicit review gate is satisfied.
- Phase 10I shared invariant tests prove the CSI provider, doctor, workflow, inspect, and release-summary surfaces remain metadata-only, reference-only, real-mode blocked, runtime disabled, and network disabled.
- Phase 11A adds RF booth / WiFi CSI contract specs in `somatic.safety.phase11_contracts` for topology metadata, consent/privacy, hardware review, model artifact review, and network policy review. These specs are planning-only and do not add capture, hardware access, model execution, or network behavior.
- Phase 11B adds deterministic review-record fixtures and fail-closed validators for those RF booth / WiFi CSI review gates. Completed review records remain planning evidence only and do not enable capture, hardware access, model execution, or network behavior.
- Phase 11C adds deterministic sanitized preflight dossiers over the RF booth / WiFi CSI contract specs and review records. Completed dossiers remain planning evidence only and do not enable capture, hardware access, model execution, or network behavior.
- Phase 11D adds lifecycle audit records, deterministic dossier comparisons, reviewer signoff metadata, and explicit audit decisions over RF booth / WiFi CSI preflight dossiers. These audit records remain planning evidence only and do not enable capture, hardware access, model execution, or network behavior.
- Phase 11E adds deterministic audit indexes, supersession chains, reviewer-scope summaries, and local export/retention policy metadata over RF booth / WiFi CSI lifecycle records. These audit indexes remain planning evidence only and do not enable capture, hardware access, model execution, or network behavior.
- Phase 11F adds compact audit handoff summaries over RF booth / WiFi CSI audit indexes. These handoffs remain reporting evidence only and do not enable capture, hardware access, model execution, or network behavior.
- Phase 11G adds compact handoff acceptance checks over RF booth / WiFi CSI handoff reports. Accepted means accepted for planning review only; it does not enable capture, hardware access, model execution, or network behavior.
- Phase 11H adds compact follow-up/remediation queues over RF booth / WiFi CSI acceptance records. Resolved-for-planning remains planning review only; it does not enable capture, hardware access, model execution, or network behavior.
- Phase 11I adds compact follow-up queue indexes over RF booth / WiFi CSI follow-up records. Accepted-for-planning queue status remains reviewer navigation only; it does not enable capture, hardware access, model execution, or network behavior.
- Phase 11J adds compact decision closeouts over RF booth / WiFi CSI queue indexes. Closed-for-planning remains planning-decision metadata only; it does not enable capture, hardware access, model execution, or network behavior.
- Phase 11K adds compact review-trail export metadata over the Phase 11A through 11J RF booth / WiFi CSI planning trail. Exported review trails remain reviewer-navigation metadata only; they do not enable capture, hardware access, model execution, or network behavior.
- Phase 11L adds compact runtime gap ledger metadata over the Phase 11A through 11K RF booth / WiFi CSI planning trail. Ledgered gaps remain reviewer-navigation metadata only; they do not enable capture, hardware access, model execution, network behavior, or real-mode runtime.
- Phase 11M adds compact planning/governance closeout metadata over the Phase 11A through 11L RF booth / WiFi CSI planning trail. Governance-complete status remains reviewer-navigation metadata only; it does not enable capture, hardware access, model execution, network behavior, or real-mode runtime.
- Phase 10J records the evidence/adapters checkpoint and next safe lanes in `docs/phase-10-checkpoint.md`.
- Phase 8C parser helpers live in `somatic.sensors.csi_formats` and `somatic.sensors.csi_parser`.
- Phase 8D replay lives on `somatic.sensors.sandbox.SandboxSensorProvider.replay_csi_fixtures(...)` and returns sanitized parser report/summary metadata only.
- Phase 8E scoring lives in `somatic.sensors.csi_scoring` and uses sanitized status/count metadata only.
- Phase 8F batch readiness lives in `somatic.sensors.csi_batch`, routes each group through the sandbox provider, and does not feed tournament rankings.
- Phase 8G evidence-pack export lives in `somatic.sensors.csi_evidence_pack` and packages sanitized counts, statuses, scores, contract versions, and fingerprints only.
- Phase 8I evidence-pack compatibility helpers classify portable packs as `compatible`, `incompatible`, `unsupported_version`, or `malformed` without exposing private field names or values.
- Phase 9A generic sensor-evidence primitives live in `somatic.sensors.evidence` and provide standard-library-only helpers for contract identity, provider/evidence kind, compatibility classification, deterministic fingerprinting, readiness status, artifact refs/hashes, diagnostics/count categories, and privacy boundary flags. CSI v1 remains the first implementation and keeps its public pack shape.
- Phase 9B generic artifact refs also live in `somatic.sensors.evidence`. They carry only run-relative `artifacts/...` paths, SHA-256 hashes, provider/evidence kind, pack ID/fingerprint, compatibility classification, and closed raw-signal flags. n-of-1 summaries, report packets, tournament summaries, run manifests, and Fabric plans can reference `artifacts/csi_evidence_pack.json` through this generic shape without changing the CSI v1 pack body.
- Phase 8B sample parser fixtures are `sample-esp32-csi.csv`, `sample-amplitude-phase.csv`, `sample-csi-jsonl.jsonl`, and `invalid-csi-malformed.csv`.
- N-of-1 replay uses the neutral `csi-tabular-fixture.csv` fixture ref for tabular component data.
- Phase 8C edge fixtures cover blank lines, unknown columns, short vectors, invalid JSONL rows, mixed valid/invalid rows, and unsupported extensions.
- N-of-1 runs with CSI fixture refs write `artifacts/csi_parser_report.json`, `artifacts/csi_parsed_summary.json`, and `artifacts/csi_evidence_pack.json`.

## Boundary

Phase 7B does not access WiFi hardware, ESP32 devices, RTL8812AU adapters, routers, drivers, monitor mode, packet capture, WiFi device probing, camera, microphone, BLE, wearable devices, or network code. Phase 8A performs only Git source staging and read-only inspection. Phase 8B parses local fake/sample fixtures only. Phase 8C keeps the same offline boundary and adds sanitized parser reports, structured parse errors, repo-relative paths, and replay tests. Phase 8D keeps replay fixture-backed and provider-mediated only. Phase 8E scores only sanitized metadata and does not score signal quality. Phase 8F batches sanitized replay metadata only and does not alter `SCORE_FIELDS`, Elo, bracket selection, winner selection, or rankings. Phase 8G exports evidence packs with sanitized metadata only and no fixture refs, source IDs, absolute paths, raw CSI arrays, or signal values. Phase 8I compatibility checks preserve the same portable privacy boundary and fail closed with sanitized counts/categories only. Phase 9A/9B only factor generic metadata-contract and artifact-ref helpers and do not change CSI v1 artifact shape, fingerprints, compatibility behavior, or artifact names. Phase 10G adds a metadata-only CSI source boundary, conditional RuView reference status, and a booth-first planning profile without changing CSI v1 evidence-pack shape or fingerprints. Phase 10H adds a shared real-mode readiness gate for CSI and document adapter status, but no runtime. Phase 10I adds shared invariant coverage, and Phase 10J records the checkpoint without runtime changes. They do not run CSI capture, read live raw RF/CSI data, infer vital signs, import DSP or sensor packages, install dependencies, run package managers, execute staged code, run RuView, download or execute models, flash ESP32 devices, control routers/APs, bridge Home Assistant/Matter/HomeKit/Alexa, open serial ports, read or write SD cards, start MQTT or UDP listeners, use `tcpdump`, `tshark`, `aircrack-ng`, channel hopping, driver changes, or WiFi interface reconfiguration.

Phase 8B explicitly has no serial, no MQTT, no UDP, no pcap, no monitor mode, no live capture, no hardware access, no network calls, and no vital-sign inference.

Raw RF/CSI data is local-first and private by default. The Phase 7B fixtures collect no raw RF/CSI data, retain no raw RF/CSI data, export no raw RF/CSI data, and perform no remote upload.

The scaffold makes no diagnosis, treatment, clinical interpretation, medical claim, monitoring claim, vital-sign inference, or emergency-triage claim.

WiFi CSI, RSSI, pcap, serial CSI logs, SD-card CSVs, raw RF/CSI, derived features, embeddings, ReID sequences, pose outputs, skeleton outputs, and activity labels are sensitive by default. Upstream references to fall detection, respiration, heart rate, sleep, pose, identity-like recognition, person tracking, ReID, monitoring, continuous learning, or production readiness are research context only and are not Somatic capabilities or validation claims.

RuView is conditional reference-only in Phase 10G. Earlier warning history
remains active, including overclaims, model-loading concerns, and unverified
deployment claims. The booth-first profile is future architecture metadata only:
single-subject operation, a small controlled booth, fixed AP plus 4-6 receiver-node
metadata, ESP32-S3 preferred radios, an empty-booth baseline concept, and
phase/conjugation/temporal-embedding notes only.

## Future Real Mode

Any future real WiFi CSI mode requires explicit consent from the operator, intended subject, and all potentially affected people in the sensing area. Do not deploy in shared, public, workplace, household, or care environments unless bystanders are informed and consent is practical. Future real mode also requires local-first storage, raw RF/CSI retention and export controls, redaction review, privacy review, hardware review, license review, source-license review, model artifact review, dependency review, network policy review, test fixtures, safety review, human review, and a separate opt-in configuration. It must remain disabled by default.
