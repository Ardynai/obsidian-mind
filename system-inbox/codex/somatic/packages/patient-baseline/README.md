# `@somatic/patient-baseline`

Placeholder for local-first personal or patient baseline graphs.

Phase 7C provides a fake-backed personal baseline scaffold only. It uses
local-only deterministic placeholders and no real health data, no real
patient/profile storage, no database or external memory runtime, and no
personal health-data export.

Planned responsibilities:

- Baseline graph schemas.
- Local storage boundaries.
- Consent and export metadata.
- Decision-support report inputs.

Current boundaries:

- no diagnosis, treatment, emergency triage, clinical interpretation,
  monitoring, or medical advice
- no hardware, sensor, WiFi CSI, camera, microphone, wearable, BLE, thermal, or
  environmental device access
- no network/API calls, Hindsight, Mem0, Zep, database, or remote upload
- future real profile or baseline storage requires explicit local storage
  consent, data-locality review, local-first privacy controls, retention/export
  controls, privacy review, safety review, human review, and separate opt-in
  configuration

Phase 7D adds mock intervention metadata beside the fake-backed local baseline.
It provides no recommendation, no prescription, no treatment recommendation, no
medical advice, no diagnosis, no emergency triage, no real monitoring, and no
reminders, automation, or scheduling. Medication placeholder disabled and
clinician review placeholder disabled are disabled metadata only. Future real
sensor mode requires explicit consent, local-first privacy controls, and safety
review; future real intervention use requires explicit consent,
human/clinical review, local storage controls, safety gates, and no
emergency-triage substitution.
