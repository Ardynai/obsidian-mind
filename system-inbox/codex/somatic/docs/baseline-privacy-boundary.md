# Baseline Privacy Boundary

Phase 7C keeps personal baseline planning local-first and private by default.
The current implementation is fake-backed and fixture-only. It does not load
real health data, persist a real profile, or export personal baseline data.

## Defaults

- Personal profile and baseline graph artifacts are placeholders.
- Fake-backed local baseline scaffold only.
- Baseline comparison is local deterministic metadata only.
- No real health data is loaded.
- No real profile storage is performed.
- No database, external memory, Hindsight, Mem0, Zep, network, API, or remote
  upload surface is added.
- No hardware, sensor, WiFi CSI, camera, microphone, wearable, BLE, thermal, or
  environmental device access is used.
- No personal data, personal health data, baseline data, raw RF/CSI data, or raw
  sensor data is exported.
- No diagnosis, treatment, emergency triage, clinical interpretation, medical
  claim, or medical advice is produced.
- No emergency triage is performed.

## Future Real Baseline Requirements

Future real baseline storage requires:

- explicit local storage consent
- data-locality review
- local-first privacy controls
- privacy review
- safety review
- human review
- retention and export controls
- separate opt-in configuration

Future real sensor mode requires explicit consent, local-first privacy controls,
and safety review. A future real profile or baseline path must remain disabled
until these requirements are implemented and reviewed.

## Phase 7D Intervention Tag Boundary

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

The n-of-1 intervention tag path is mock intervention metadata only. It links to
the fake-backed local baseline artifacts and provides no recommendation, no
prescription, no treatment recommendation, no medical advice, no diagnosis, no
emergency triage, no real monitoring, and no reminders, automation, or
scheduling.

Medication placeholder disabled and clinician review placeholder disabled are
disabled metadata only. Real use requires explicit consent, human/clinical
review, local storage controls, safety gates, and no emergency-triage
substitution.

## Phase 7E Response Evaluation Boundary

Response evaluation is fake-backed local research-only planning only. It uses
fixture trend labels only; no intervention effectiveness is claimed. It
provides no effectiveness claim, no recommendation, no prescription, no
treatment recommendation, no medical advice, no diagnosis, no emergency triage,
no real monitoring, and no reminders, automation, notification, or scheduling.
