# N-of-1 Fabric Pack Plan

Phase 7G adds a planning-only Fabric data-pack candidate for fake-backed
n-of-1 report packet artifacts. The runtime writes:

- `artifacts/n_of_1_fabric_pack_plan.json`

The n-of-1 Fabric pack plan is planning-only and private-only by default. It
references `artifacts/n_of_1_report_packet.json`, the report packet's artifact
refs, the report packet's SHA-256 hashes, and generic sanitized
sensor-evidence artifact refs when present. It does not inline artifact
payloads and does not create a Content Fabric `pack.json` manifest.

## Candidate Shape

The plan recommends a future Fabric `data` class with `document` as the
suggested type and `dataset` as the alternate type. It uses `file_plans`, not
Fabric manifest `files`, and records local run-relative paths plus SHA-256
hashes for reproducibility/provenance only.

Phase 9B adds `sensor_evidence_artifact_refs` and
`planned_sensor_evidence_artifact_ids`. CSI is the first implementation:
`sensor_evidence_artifact_refs.csi_evidence_pack` points to
`artifacts/csi_evidence_pack.json` and carries only the run-relative path,
SHA-256, pack ID/fingerprint, provider/evidence kind, compatibility
classification, and closed privacy flags.

Phase 9C adds the second provider proof:
`sensor_evidence_artifact_refs.environment_evidence_pack` points to
`artifacts/environment_evidence_pack.json` with the same compact generic ref
shape. When the n-of-1 workflow is configured with neutral environment fixture
rows, `planned_sensor_evidence_artifact_ids` includes both `csi_evidence_pack`
and `environment_evidence_pack`.

CSI parser report and parsed-summary artifacts can remain listed as local
report-packet files, but they are marked `include_in_candidate: false`. They are
diagnostic local artifacts, not portable Fabric candidates. The environment
evidence pack is already sanitized portable metadata and can be a local data
candidate. The plan never embeds provider payloads, parser report bodies,
parser summary bodies, raw values, row bodies, fixture refs, private refs,
unsafe refs, absolute paths, credentials, or live-provider output.

The plan is not a code pack. It records no executable files, no install target,
no publisher, no keyring, no catalog entry, no manifest digest, no signatures,
no transport, no magnet URI, no WebSeed, and no infohash.

## Boundary

No Fabric signing, catalog publication, transport, magnet, WebSeed, seeding,
upload, install, or execution is enabled. The plan does not sign, publish,
catalog, torrent, seed, upload, install, enable, or execute anything.

No real personal data export is performed. No real personal data, personal
health data, baseline data, raw sensor data, raw RF/CSI data, or health record
is exported. The source artifacts are fake-backed, local-only, research-only,
and sandbox-only.

Hashes are for local reproducibility/provenance only and do not imply clinical
validity, monitoring, intervention effectiveness, treatment guidance, or
advice. The plan is not medical advice, not a medical record, not a health
record, and not a clinical or effectiveness claim.

Boundary phrase checklist: fake-backed; no hardware; no diagnosis; no emergency triage; real sensor mode requires explicit consent; fake-backed local baseline; no real health data; explicit local storage consent; data-locality review; mock intervention; no prescription; no recommendation; no reminders; no effectiveness claim; no real monitoring; local-first privacy; safety review.

## Future Real Packaging Requirements

Future real packaging requires explicit consent, redaction, license review,
privacy review, safety review, human review, local-first storage controls,
retention and export controls, and separate publication approval. A future pack
must not contain raw real health data unless explicitly consented, redacted
where needed, and reviewed for license, privacy, and safety.
