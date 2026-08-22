# Phase 12F Secure Drop Consumer Boundary

Phase 12F is a non-executing Secure-Drop-consumer-boundary-only contract. It
defines how Somatic may later reference the canonical content-fabric Secure Drop
design contract for future user-selected encrypted artifact transfer, without
implementing Secure Drop in Somatic.

The canonical owner is content-fabric. The canonical reference is the
kortex-audio content-fabric Secure Drop design contract merged at
`12eb228906d9708bd89b23328f66afba558963b0`.

Current status remains blocked:

- `consumer_phase: boundary-profile-only`
- `canonical_owner: content-fabric`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`
- `secure_drop_send_permitted: false`
- `secure_drop_receive_permitted: false`

Future user-selected artifact labels are metadata only:

- sanitized-review-report
- sanitized-evidence-summary
- sanitized-doctor-status
- sanitized-sensor-profile-summary
- sanitized-runtime-authorization-status
- user-attached-document

Prohibited future or autonomous sources are explicit:

- agent-selected-file
- automation-selected-file
- vault-secret
- env-var
- api-key
- filesystem-autoscan
- raw-document-body
- raw-csi-rf-capture
- raw-bia-reading
- raw-acoustic-ultrasound-data
- screenshot-or-ocr-dump

Future Secure Drop requirements are metadata only:

- encryption is required by the canonical future contract
- concealment is optional and is never the security boundary
- audit records must remain metadata-only
- explicit user action is required before any future send candidate

Phase 12F does not implement crypto, transport, steganography, keyring, DID,
send, receive, inbox, UI, network calls, runtime adapters, active grants, or
real-mode authorization. It does not allow agent, automation, connector,
scheduled task, avatar, server endpoint, or workflow invocation. It does not
allow filesystem autoscan, vault/env/API-key/secret-file access, raw sensor
capture attachment, or automatic document attachment.

Validation rejects missing fields, unsupported versions, unknown fields,
approval/grant/permission-looking values, unsafe or private values, URLs,
absolute paths, API keys, env vars, vault references, source/device/router IDs,
raw document/CSI/RF/sensor payloads, raw BIA/acoustic/ultrasound data,
screenshots, raw OCR, medical or clinical claims, send/receive execution
wording, unencrypted-transfer wording, stego-as-security wording,
anonymous/unkeyed-recipient wording, audit payload content, and non-integer
counts.
