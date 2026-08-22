# N-of-1 Report Packet

Phase 7F adds a consolidated n-of-1 report packet for the fake-backed
`n-of-1` workflow. The packet is fake-backed/local/research-only,
mock/offline, local-only, research-only, and sandbox-only.

The runtime writes:

- `artifacts/n_of_1_report_packet.json`
- `artifacts/n_of_1_fabric_pack_plan.json` in Phase 7G, as a planning-only
  private Fabric data-pack candidate that references this packet.

The packet references the current n-of-1 artifact chain:

- `sensor_stream_plan.json`
- `sensor_observations.json`
- `sensor_feature_set.json`
- `sensor_evidence_record.json`
- `n_of_1_baseline_placeholder.json`
- `personal_profile.json`
- `baseline_graph.json`
- `baseline_comparison.json`
- `intervention_tag.json`
- `intervention_context.json`
- `response_evaluation_plan.json`
- `mock_intervention_ledger.json`
- `follow_up_observation_window.json`
- `follow_up_sensor_snapshot.json`
- `response_comparison.json`
- `response_evaluation_summary.json`
- `n_of_1_summary.json`

## Packet Contents

The packet records artifact refs, SHA-256 hashes, a loop-stage summary, strict
safety boundary flags, limitations, and future real-use requirements. Hashes
are for reproducibility/provenance only. They are not evidence of clinical
validity, monitoring, intervention effectiveness, diagnosis, or treatment.

The loop stages are:

- `observation`
- `baseline`
- `intervention_tag`
- `follow_up`
- `response_comparison`

Missing artifacts fail closed: the packet marks the missing artifact as
`present: false`, sets its `sha256` to `null`, records
`missing-required-n-of-1-artifact`, and sets `packet_complete: false`.

## Boundary

The n-of-1 report packet is not medical advice, not a medical record, and not a
health record. It is a local reproducibility/provenance packet for fixture
planning outputs only.

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

- fake-backed sensor planning only
- fake-backed local research-only planning only
- No hardware is accessed.
- no live sensor access
- Raw RF/CSI data is local-first and private by default; this fixture collects, retains, and exports none.
- no network calls or external API calls
- No database, external memory, Hindsight, Mem0, or Zep runtime is used.
- mock intervention metadata only
- event label only, not advice
- fixture trend labels only
- No intervention effectiveness is claimed.
- response evaluation is future planning only, not real monitoring
- no recommendation
- no prescription
- no treatment recommendation
- no medical advice
- no medication action
- no clinician action
- no effectiveness claim
- no reminders, automation, notification, or scheduling
- no real monitoring
- no diagnosis, treatment, or emergency triage
- No emergency triage is performed.
- no medical or clinical claims

Future real use requires explicit consent, privacy review, safety review,
human review, clinical review where applicable, local-first storage controls,
retention/export controls, and separate opt-in configuration.

## Phase 7G Fabric Pack Planning

Phase 7G adds a local n-of-1 Fabric pack plan for this report packet. The plan
is planning-only and private-only by default. It is not a Content Fabric
`pack.json` manifest and does not sign, publish, catalog, torrent, seed,
upload, install, enable, or execute anything.

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding,
upload, install, or execution is enabled. No real personal data export,
personal health data export, baseline data export, raw sensor data export, or
raw RF/CSI data export is performed. Future real packaging requires explicit
consent, redaction, license review, privacy review, safety review, and human
review, local-first storage controls, retention/export controls, and separate
publication approval.
