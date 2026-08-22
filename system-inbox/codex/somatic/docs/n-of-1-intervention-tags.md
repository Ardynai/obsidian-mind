# N-of-1 Intervention Tags

Phase 7D adds a mock intervention tagging scaffold for the fake-backed
`n-of-1` workflow. It is mock/offline, local-only, research-only, sandbox-only,
and uses fake-backed intervention tags.

The runtime writes:

- `artifacts/intervention_tag.json`
- `artifacts/intervention_context.json`
- `artifacts/response_evaluation_plan.json`
- `artifacts/mock_intervention_ledger.json`

The tag is an event label for deterministic planning only. It is not an
instruction, recommendation, prescription, or treatment recommendation.

## Categories

Supported placeholder categories are:

- `rest_placeholder`
- `hydration_placeholder`
- `breathing_exercise_placeholder`
- `medication_placeholder_disabled`
- `clinician_review_placeholder`
- `environmental_change_placeholder`

Medication placeholder disabled and clinician review placeholder disabled are
disabled metadata only. They do not recommend medication, trigger clinician
action, replace clinician review, prescribe, triage, or apply a real
intervention.

## Context

`intervention_context.json` references the existing local n-of-1 artifacts:

- `sensor_feature_set.json`
- `baseline_comparison.json`
- `personal_profile.json`
- `baseline_graph.json`

The context records artifact references and hashes only. It does not access
hardware, load no real health data, store a profile, use a database, use
external memory, call a network, export personal data, or create any real
monitoring path.

## Response Evaluation

The response evaluation plan summary is future planning only. It records a
placeholder comparison window, metrics to re-check, and baseline categories to
compare. It performs no real monitoring, no reminders, automation, or
scheduling, no notifications, no effectiveness claim, no recommendation, no
prescription, no medical advice, no diagnosis, and no emergency triage.

The mock intervention tag summary and response evaluation plan summary are
therefore report metadata, not advice.

## Boundaries

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

- mock intervention metadata only
- fake-backed local baseline and fake-backed intervention tags only
- no hardware, sensors, WiFi CSI, camera, microphone, wearable, BLE, thermal, or
  environmental device access
- no real health data loaded
- no database, external memory, network call, external API, or remote upload
- no recommendation
- no prescription
- no treatment recommendation
- no medical advice
- no diagnosis
- no emergency triage
- no real monitoring
- no reminders, automation, or scheduling
- medication placeholder disabled and clinician review placeholder disabled are
  disabled metadata only

Future real sensor mode requires explicit consent, a local-first privacy
policy, and safety review. Future real baseline storage requires explicit local
storage consent, data-locality review, local-first privacy controls, privacy
review, safety review, human review, retention/export controls, and separate
opt-in configuration.

Future real intervention use requires explicit consent, local storage controls,
safety gates, and human/clinical review before any real response evaluation path
is enabled. It must not substitute for emergency triage.

## Phase 7E Response Evaluation

Phase 7E turns the Phase 7D response evaluation plan into fake-backed local
research-only planning artifacts: follow-up observation window, follow-up sensor
snapshot, response comparison, and response evaluation summary. The output is
fixture trend labels only. No intervention effectiveness is claimed. It
provides no effectiveness claim, no recommendation, no prescription, no
treatment recommendation, no medical advice, no medication action, no clinician
action, no real monitoring, and no reminders, automation, notification, or
scheduling.
