# Phase 12D Visual/Desktop Consent Gate Requirements

Phase 12D is a non-executing consent-gate-requirements-only contract for future
high-risk visual and desktop supervision capabilities. It builds only from the
Phase 12A runtime authorization design charter, Phase 12B runtime authorization
record candidate, and Phase 12C visual supervision capability profile.

Current status remains blocked:

- `consent_phase: gate-requirements-only`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`

Capability categories are sanitized metadata only:

- screen-observation
- ocr-observation
- dashboard-observation
- terminal-observation
- ci-review-status-observation
- notification-policy
- overlay-policy
- click-input-automation-policy
- clipboard-policy
- camera-policy
- microphone-policy
- recording-policy

Future consent gates are metadata only and are not satisfied by Phase 12D:

- explicit-human-consent-record
- scoped-capability-selection
- visible-indicator-requirement
- retention-redaction-policy
- disable-rollback-plan
- audit-log-requirement
- no-hidden-background-monitoring-declaration
- per-capability-review-requirement
- jules-human-review-for-validator-authorization-semantics

Phase 12D does not satisfy any consent gate and does not authorize any visual or
desktop capability. It grants no screen capture, OCR execution, camera capture,
microphone capture, clipboard capture, recording, click/input automation,
overlay display, notification sending, network calls, runtime adapters,
provider/model execution, active grants, or real-mode authorization.

Validation rejects missing fields, unsupported versions, unknown fields,
approval/grant/permission/consent-looking values, unsafe or private values,
URLs, absolute paths, source/device/router identifiers, raw screenshots, raw OCR,
raw clipboard text, camera/microphone/audio payloads, recording payloads, raw
document/CSI/RF markers, model/parser/provider bodies, medical or clinical
claims, and non-integer counts.
