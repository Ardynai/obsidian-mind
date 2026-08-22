# N-of-1 Workflow

Phase 7A adds `mode: n-of-1` as a fake-backed planning workflow for local sensor and baseline metadata. Phase 7B adds WiFi CSI planning metadata to the same artifacts without enabling capture. Phase 8A stages WiFi CSI references for source review only without enabling capture. Phase 8B adds local fake/sample WiFi CSI parser fixture metadata only. Phase 8C freezes that parser as a deterministic offline contract with sanitized reports. Phase 8D routes those fixtures through a sandbox sensor-provider replay seam. Phase 8E adds sanitized CSI replay evidence scoring metadata. Phase 8G adds a sanitized CSI evidence-pack export artifact. Phase 9A/9B add generic sanitized sensor-evidence contract and artifact-reference helpers underneath CSI. Phase 9C adds a second neutral environment fixture evidence pack through the same generic contract. Phase 9D adds registry-backed fixture-provider config validation before the n-of-1 runtime dispatch. Phase 7C adds fake-backed personal baseline graph artifacts. Phase 7D adds mock intervention tag metadata and a response evaluation plan scaffold. Phase 7E adds fake-backed follow-up response evaluation artifacts. Phase 7F adds a consolidated n-of-1 report packet. It is research-only and sandbox-only.

Run the fixture:

```powershell
python -m somatic run fixtures/workflows/valid-n-of-1.yaml
```

The runner preserves the baseline run files and writes:

- `artifacts/sensor_stream_plan.json`
- `artifacts/sensor_observations.json`
- `artifacts/sensor_feature_set.json`
- `artifacts/csi_parser_report.json`
- `artifacts/csi_parsed_summary.json`
- `artifacts/csi_evidence_pack.json`
- `artifacts/environment_evidence_pack.json`
- `artifacts/sensor_evidence_record.json`
- `artifacts/n_of_1_baseline_placeholder.json`
- `artifacts/personal_profile.json`
- `artifacts/baseline_graph.json`
- `artifacts/baseline_comparison.json`
- `artifacts/intervention_tag.json`
- `artifacts/intervention_context.json`
- `artifacts/response_evaluation_plan.json`
- `artifacts/mock_intervention_ledger.json`
- `artifacts/follow_up_observation_window.json`
- `artifacts/follow_up_sensor_snapshot.json`
- `artifacts/response_comparison.json`
- `artifacts/response_evaluation_summary.json`
- `artifacts/n_of_1_summary.json`
- `artifacts/n_of_1_report_packet.json`
- `artifacts/n_of_1_fabric_pack_plan.json`

All n-of-1 artifacts are deterministic and marked `mock`, `offline`, `research_only`, and `sandbox_only`.

Phase 7B adds CSI-specific metadata inside:

- `sensor_feature_set.json`: nested `metadata.csi` with capture, feature, privacy, hardware, and reference-inventory metadata.
- `sensor_evidence_record.json`: nested CSI Evidence Bus metadata with the final feature-set artifact hash.
- `n_of_1_summary.json`: `csi_metadata` with disabled hardware, packet capture, WiFi probing, monitor mode, raw RF/CSI, and clinical interpretation flags.

Phase 8B/8C/8D/8E/8G adds CSI parser metadata when fixture refs are present:

- `csi_parser_report.json`: deterministic provider replay report over local fake/sample fixtures only.
- `csi_parsed_summary.json`: parsed frame/sample-count summary without raw signal-value output.
- `csi_evidence_pack.json`: deterministic portable evidence-pack JSON with sanitized parser/replay/scoring metadata, contract versions, counts/status counts, bounded scores, fail-closed readiness status, and a stable SHA-256 fingerprint.
- `n_of_1_summary.json`: `csi_parser_metadata` with parser id, replay provider metadata, fixture count, frame count, sample count, neutral source format classes, artifact refs, and closed hardware/network/serial/pcap/medical flags. It does not repeat fixture filenames or fixture refs.
- `sensor_evidence_record.json` and `n_of_1_summary.json`: additive `evidence_scoring` / `csi_evidence_scoring_metadata` with bounded `evidence_quality` and `replay_integrity` scores computed only from sanitized parser counts, statuses, warnings/errors, format coverage, fixture count, and contract version.
- `n_of_1_summary.json`: `csi_evidence_pack_metadata` with only the evidence-pack artifact ref, SHA-256, pack ID, fingerprint, status, and closed boundary flags.
- `manifest.json`, `n_of_1_summary.json`, `n_of_1_report_packet.json`, and `n_of_1_fabric_pack_plan.json`: additive `sensor_evidence_artifact_refs.csi_evidence_pack` with a generic run-relative `artifacts/csi_evidence_pack.json` ref, SHA-256, pack ID/fingerprint, provider/evidence kind, compatibility classification, and closed raw-signal flags.

Phase 9C adds a neutral second provider proof when
`environment-fixture-rows` inputs are configured:

- `environment_evidence_pack.json`: deterministic portable evidence-pack JSON
  with provider/evidence kind, contract version, row/status counts, bounded
  quality scores, sanitized diagnostic categories, closed boundary flags, and
  a stable SHA-256 fingerprint.
- `n_of_1_summary.json`: `environment_evidence_pack_metadata` and
  `environment_readiness_metadata` with only compact readiness counts and the
  evidence-pack artifact ref/fingerprint.
- `manifest.json`, `n_of_1_summary.json`, `n_of_1_report_packet.json`, and
  `n_of_1_fabric_pack_plan.json`: additive
  `sensor_evidence_artifact_refs.environment_evidence_pack` with the
  run-relative `artifacts/environment_evidence_pack.json` ref and SHA-256.

The environment pack is the generic-contract proof outside CSI. It does not
export fixture refs, fixture filenames, row bodies, raw values, source IDs,
unsafe refs, absolute paths, provider payload bodies, parser report bodies,
parser summary bodies, credentials, hardware access, network calls, live
capture, or ranking input.

Phase 9D validates configured evidence providers through
`somatic.sensors.registry` before the runner builds artifacts. The n-of-1
fixture declares `provider_id: wifi-csi` for CSI parser fixtures and
`provider_id: environment-fixture` for environment rows. Validation requires
known provider IDs, bounded ref counts, fixture-only local refs, closed sensor
constraints, and sanitized errors. The emitted `workflow.json` keeps only ref
counts, provider/evidence identity, artifact names, and run-relative artifact
refs; it removes the configured fixture filenames and free-text
sensor-evidence input fields.

The `emit-sandbox-observations` stage declares `csi_parser_fixtures` as a local
fixture input and emits both parser artifacts. Parser reports include stable
structured parse-error codes and sanitized fixture refs/paths only. The
evidence pack is stricter: it exports no fixture refs, fixture filenames,
source IDs, absolute paths, unsafe refs, provider payload bodies, parser report
bodies, parser summary bodies, raw CSI arrays, or signal values.
Parser report and parsed-summary artifacts remain local diagnostic artifacts.
The Fabric plan marks them outside the candidate package surface; the portable
sensor-evidence ref points to `artifacts/csi_evidence_pack.json`.

Phase 7C adds personal baseline metadata:

- `personal_profile.json`: fake-backed local profile placeholder with no real health data or real profile storage.
- `baseline_graph.json`: fake-backed local graph over `respiratory_rate`, `movement_score`, `sleep_state_estimate`, `posture_state`, `csi_confidence`, `environmental_context`, and `notes_placeholder`.
- `baseline_comparison.json`: deterministic local comparison with `within_baseline`, `outside_baseline`, and `insufficient_data` statuses.
- `n_of_1_summary.json`: `baseline_comparison_summary` with status counts, status by category, and disabled real-health-data/profile/export flags.

Phase 7D adds n-of-1 intervention tag metadata:

- `intervention_tag.json`: a fake-backed intervention tag label, not a recommendation, prescription, treatment recommendation, medication action, clinician action, or effectiveness claim.
- `intervention_context.json`: local references to `sensor_feature_set.json`, `baseline_comparison.json`, `personal_profile.json`, and `baseline_graph.json`.
- `response_evaluation_plan.json`: a future comparison window placeholder with metrics to re-check and baseline categories to compare.
- `mock_intervention_ledger.json`: a local placeholder ledger proving no real intervention was performed.
- `n_of_1_summary.json`: `intervention_summary` with disabled recommendation, prescription, treatment, scheduling, reminder, monitoring, and effectiveness flags.

Phase 7E adds response evaluation metadata:

- `follow_up_observation_window.json`: fake-backed local follow-up window metadata with no reminders, automation, notification, scheduling, or real monitoring.
- `follow_up_sensor_snapshot.json`: deterministic second placeholder snapshot with no hardware, live capture, real health data, or network call.
- `response_comparison.json`: mechanical placeholder comparison using `toward_baseline`, `away_from_baseline`, `unchanged`, and `insufficient_data` fixture trend labels only.
- `response_evaluation_summary.json`: aggregate response trend summary with no effectiveness claim, no recommendation, no prescription, no medical advice, and no intervention effectiveness claim.

Phase 7F adds report packet consolidation:

- `n_of_1_report_packet.json`: consolidated fake-backed/local/research-only packet that references every n-of-1 artifact, records SHA-256 hashes for reproducibility/provenance only, and summarizes observation, baseline, intervention tag, follow-up, and response comparison stages.

The packet is not a medical record and not a health record. It generates no effectiveness claim, no advice, no recommendation, no prescription, no treatment recommendation, no medical advice, no diagnosis, no emergency triage, no real monitoring, and no reminders, automation, notification, or scheduling.

The report packet includes `csi_evidence_pack` as a required observation-stage
artifact and can include optional future/provider evidence packs such as
`environment_evidence_pack`. The planning-only n-of-1 Fabric pack plan can
reference those sanitized evidence packs by run-relative path and SHA-256 only.
It does not create a Content Fabric `pack.json`, sign, publish, transport,
seed, install, execute, or expose raw CSI data or environment row bodies.

## Boundary

The workflow does not collect a real baseline, load real health data, store a real profile, open devices, capture CSI, use camera/audio/wearable streams, call a network, use a database or external memory, monitor a person, diagnose, treat, or triage emergencies. No hardware is accessed. No diagnosis is made. No emergency triage is performed. Placeholder values such as `respiratory_rate`, `movement_score`, `posture_state`, `sleep_state_estimate`, `audio_event_placeholder`, and `environmental_context_placeholder` are fixed sandbox values.

The WiFi CSI metadata is fake-backed planning only and disabled by default. It does not access ESP32 devices, RTL8812AU adapters, routers, WiFi adapters, drivers, monitor mode, packet capture, WiFi device probing, raw RF/CSI data, or network code. Raw RF/CSI data is local-first and private by default; the workflow collects, retains, and exports none.

The Phase 8C/8D/8E/8G WiFi CSI parser, replay-provider, scoring, and evidence-pack path is local fake/sample fixtures only. Phase 8F tournament batch readiness reuses the same sanitized replay metadata boundary. It has no serial, no MQTT, no UDP, no pcap, no monitor mode, no live capture, no hardware access, no network calls, no vital-sign inference, and no medical claim. It does not export raw sample arrays, source IDs, absolute paths, raw signal-value keys, raw signal values, fixture refs, private fixture filenames, or unsafe refs in the evidence pack. CSI scoring is replay metadata quality only, not signal quality, monitoring, diagnosis, treatment advice, medical advice, or a clinical claim. Real parser support requires explicit consent, source-license review, cleared test fixtures, privacy review, safety review, hardware review, retention/export controls, and separate opt-in configuration.

Phase 8A source staging is also non-runtime. It does not execute staged source,
install dependencies, run package managers, flash ESP32 devices, open serial
ports, read or write SD cards, start MQTT or UDP listeners, enable monitor
mode, run packet capture, use channel hopping, change drivers, or reconfigure
WiFi interfaces. WiFi CSI, RSSI, pcap, serial CSI logs, SD-card CSVs, raw
RF/CSI, derived features, embeddings, ReID sequences, pose outputs, skeleton
outputs, and activity labels are sensitive by default. Upstream monitoring,
fall-detection, vital-sign, respiration, heart-rate, sleep, identity-like,
ReID, continuous-learning, and pose claims are research context only, not
Somatic n-of-1 capabilities.

The personal baseline graph is a fake-backed local baseline scaffold only. It is not medical advice, diagnosis, treatment, clinical interpretation, monitoring, or emergency triage.

The intervention tag scaffold is mock intervention metadata only. It provides no recommendation, no prescription, no treatment recommendation, no medical advice, no diagnosis, no emergency triage, no effectiveness claim, no real monitoring, and no reminders, automation, or scheduling. Medication placeholder disabled and clinician review placeholder disabled are disabled metadata only.

The response evaluation scaffold is fake-backed local research-only planning only. It emits fixture trend labels only; no intervention effectiveness is claimed. It provides no effectiveness claim, no recommendation, no prescription, no treatment recommendation, no medical advice, no medication action, no clinician action, no diagnosis, no emergency triage, no real monitoring, and no reminders, automation, notification, or scheduling.

The n-of-1 report packet is fake-backed local research-only planning only. Hashes are for reproducibility/provenance only. It is not medical advice, not a medical record, and not a health record. No hardware is accessed. No database, external memory, Hindsight, Mem0, or Zep runtime is used. No network calls or external API calls are made.

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

Future real n-of-1 work requires explicit consent, local-first storage, explicit local storage consent for real baseline storage, data-locality review, privacy review, safety review, human review, retention/export controls, and separate opt-in configuration.

Future real sensor mode requires explicit consent, local-first privacy controls, and safety review.
