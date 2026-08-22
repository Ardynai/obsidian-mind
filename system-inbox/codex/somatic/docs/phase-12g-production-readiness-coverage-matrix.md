# Phase 12G Production Readiness Coverage Matrix

Phase 12G is a non-executing production-readiness coverage matrix. It maps
production-readiness areas to Somatic responsibilities, likely repo-family
owners, current coverage, remaining gaps, blocked runtime requirements, and
review requirements.

Phase 12G does not make Somatic production-ready. It does not authorize runtime.
It does not implement production infrastructure, deployment, runtime adapters,
network calls, active grants, device connections, sensor processing, Secure Drop
send/receive, provider/model execution, or real-mode authorization.

Current status remains blocked:

- `readiness_phase: coverage-matrix-only`
- `source_phase_range: 11A-11M,12A-12F`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`
- `phase12g_makes_somatic_production_ready: false`
- `phase12g_authorizes_runtime: false`

The matrix covers these areas:

- Front-end development: external-owner, likely Locus
- API and backend logic: external-owner, likely deployment layer
- Database and storage: external-owner, likely content-fabric
- Auth and permissions: boundary-only, likely Aegis
- Hosting and deployment: external-owner, likely deployment layer
- Cloud and compute: external-owner, likely deployment layer
- CI/CD and version control: direct, likely Somatic
- Security and RLS: boundary-only, likely Aegis
- Rate limiting: external-owner, likely deployment layer
- Caching and CDN: external-owner, likely deployment layer
- Load balancing and scaling: external-owner, likely deployment layer
- Error tracking and logs: boundary-only, likely Aegis
- Availability and recovery: boundary-only, likely deployment layer
- Infrastructure management and compliance: boundary-only, likely Aegis
- Testing frameworks: direct, likely Somatic
- Operations and reliability: direct, likely Somatic
- Maintenance and governance: direct, likely Somatic
- Secrets management: boundary-only, likely Aegis
- System discovery: boundary-only, likely Locus

Somatic direct responsibility remains limited to testing frameworks, safety
contracts, validator behavior, sensor capability boundaries, evidence/report
metadata, doctor/status surfaces, and governance docs. Boundary-only entries
mean Somatic may describe blocked posture or required future review without
owning production runtime. External-owner entries mean production ownership is
outside Somatic.

Validation rejects missing fields, unsupported versions, unknown fields,
approval/grant/permission-looking values, unsafe or private values, URLs,
absolute paths, API keys, env vars, vault references, source/device/router IDs,
raw document/CSI/RF/sensor payloads, screenshots, raw OCR, medical or clinical
claims, production-ready claims, deployment-enabled claims, runtime-enabled
claims, and non-integer counts.
