# Safety Boundaries

Somatic is a research and decision-support harness. Safety boundaries are part of the architecture, not a later feature.

## Clinical and Health Boundaries

- Use research, decision support, safety-gated reports, and human review language.
- Do not claim diagnosis, treatment, cure, emergency triage, or replacement of clinicians.
- Require qualified human review for health-related reports.
- Separate user-provided observations from model-generated interpretations.
- Preserve evidence links, assumptions, and uncertainty.
- Keep personal and patient baseline data local-first unless explicitly exported.

## Lab Boundaries

- No autonomous wet-lab execution in Phase 0.
- Future lab adapters must require explicit operator approval before real-world actions.
- Manual lab plans must include human checkpoints.
- Cloud-lab adapters must expose cost, safety, sample, and compliance gates.
- Simulation must be clearly labeled as simulation.

## Sensor Boundaries

- Sensor adapters must document consent, environment, retention, and privacy assumptions.
- WiFi CSI workflows must avoid hidden surveillance use cases.
- Raw observation data should be minimized, labeled, and stored with retention controls.
- Phase 7A sensor artifacts are fake-backed only and must not access hardware,
  capture CSI/camera/audio/wearable data, call networks, export personal data,
  perform real monitoring, or claim diagnosis, treatment, or emergency triage.
- Phase 7B WiFi CSI artifacts are planning metadata only and must not access
  ESP32, RTL8812AU, routers, adapters, drivers, monitor mode, packet capture,
  WiFi device probing, raw RF/CSI data, networks, or clinical interpretation.
  Raw RF/CSI data is local-first and private by default.
- Future real sensor mode requires explicit user consent, local-first privacy
  policy, retention/export controls, privacy review, safety review, and human
  review.
- Phase 7C personal baseline artifacts are fake-backed local placeholders only.
  They must not load real health data, perform real profile storage, use a
  database or external memory, export personal health data, perform real
  monitoring, or claim diagnosis, treatment, clinical interpretation, medical
  advice, or emergency triage.
- Future real baseline storage requires explicit local storage consent,
  data-locality review, local-first privacy controls, privacy review, safety
  review, human review, retention/export controls, and separate opt-in
  configuration.
- Phase 7D intervention tag artifacts are mock intervention metadata only.
  They must not generate advice, medical advice, recommendation, prescription,
  treatment recommendation, medication action, clinician action, effectiveness
  claims, real monitoring, reminders, automation, scheduling, diagnosis, or
  emergency triage.
- Medication placeholder disabled and clinician review placeholder disabled are
  disabled metadata only.
- Future real intervention use requires explicit consent, human/clinical
  review, local storage controls, safety gates, and no emergency-triage
  substitution.
- Phase 7E response evaluation artifacts are fake-backed local research-only
  planning only. They use fixture trend labels only and no intervention
  effectiveness is claimed.
- Phase 7E must not generate an effectiveness claim, recommendation,
  prescription, treatment recommendation, medical advice, medication action,
  clinician action, reminders, automation, notification, scheduling, real
  monitoring, diagnosis, or emergency triage.
- Future real response evaluation requires explicit consent, human/clinical
  review, local storage controls, privacy/safety gates, real
  scheduling/monitoring safety review, and no emergency-triage substitution.

## Fabric Boundaries

- Verify hashes before trusting pack files.
- Verify signatures before trusting publisher identity.
- Quarantine code packs by default.
- Enforce license gates before indexing restricted content.
- Keep data packs and executable code packs separate.

## Report Boundaries

Every safety-gated report should include:

- Workflow mode.
- Data sources.
- Adapter versions.
- Evidence summary.
- Uncertainty and limitations.
- Human review status.
- Actions that were not taken.
