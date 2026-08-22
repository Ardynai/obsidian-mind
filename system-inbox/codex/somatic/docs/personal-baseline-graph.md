# Personal Baseline Graph

Phase 7C adds a fake-backed local baseline scaffold for the `n-of-1` mock
workflow. It is a research-only planning artifact, not a health record.

The scaffold writes:

- `artifacts/personal_profile.json`
- `artifacts/baseline_graph.json`
- `artifacts/baseline_comparison.json`

The baseline graph contains deterministic placeholder categories only:

- `respiratory_rate`
- `movement_score`
- `sleep_state_estimate`
- `posture_state`
- `csi_confidence`
- `environmental_context`
- `notes_placeholder`

The comparison uses only mechanical local range and string matching. Statuses
are `within_baseline`, `outside_baseline`, and `insufficient_data`. These
statuses are deviation notes for fixture values only. They are not medical
advice, diagnosis, treatment, clinical interpretation, monitoring, or emergency
triage.

## Boundary

- Fake-backed local baseline scaffold only.
- No real health data is loaded.
- No real profile storage is performed.
- No hardware, sensor, WiFi CSI, camera, microphone, wearable, BLE, thermal, or
  environmental device access is used.
- No network code, API call, database, external memory, Hindsight, Mem0, or Zep
  runtime is used.
- No personal data, personal health data, baseline data, raw RF/CSI data, or raw
  sensor data is exported.
- No diagnosis, treatment, emergency triage, clinical claim, or medical advice
  is produced.
- No emergency triage is performed.

Future real baseline storage requires explicit local storage consent,
data-locality review, local-first privacy controls, privacy review, safety
review, human review, retention/export controls, and separate opt-in
configuration. Future real sensor mode requires explicit consent, local-first
privacy controls, and safety review.

## Phase 7D Intervention Tags

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

The n-of-1 intervention tag scaffold consumes the fake-backed local baseline
comparison as metadata only. It is mock intervention planning, not advice. It
provides no recommendation, no prescription, no treatment recommendation, no
medical advice, no diagnosis, no emergency triage, no real monitoring, and no
reminders, automation, or scheduling.

Medication placeholder disabled and clinician review placeholder disabled are
disabled metadata only. Future real intervention use requires explicit consent,
human/clinical review, local storage controls, safety gates, and no
emergency-triage substitution.

## Phase 7E Response Evaluation

The response evaluation scaffold compares a fake-backed follow-up snapshot to
the local placeholder baseline using fixture trend labels only. No intervention
effectiveness is claimed. There is no effectiveness claim, no recommendation,
no prescription, no treatment recommendation, no medical advice, no real
monitoring, and no reminders, automation, notification, or scheduling.
