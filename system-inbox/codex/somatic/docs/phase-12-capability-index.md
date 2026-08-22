# Phase 12 Capability Index

Cross-phase index of every Phase-12 sub-phase capability profile present on `main`. Titles are taken verbatim from `docs/phase-12*.md`. This document is metadata-only; real-mode runtime remains blocked for all profiles.

Note: there is no Phase 12J (the letter was skipped). A Phase 12T (fabric transport consumer-readiness intake boundary) was proposed in PR #65 but closed as superseded by the out-of-process fabric federation connector merged in PR #66; it is not part of `main`.

## Capability profiles

| Sub-phase | Title | Purpose | Artifact type |
|---|---|---|---|
| 12A | Runtime Authorization Design Charter | Non-authorizing design charter for a future runtime-authorization contract | Charter |
| 12B | Runtime Authorization Record Candidate | Candidate record shape for a future, non-authorizing runtime authorization | Record candidate |
| 12C | Visual Supervision Capability Profile | Capability profile for future visual supervision | Capability profile |
| 12D | Visual/Desktop Consent Gate Requirements | Consent-gate requirements for future visual/desktop capture | Requirements |
| 12E | Physiological Sensor Capability Profile | Capability profile for future physiological sensors | Capability profile |
| 12F | Secure Drop Consumer Boundary | Consumer boundary for a future secure-drop path | Boundary |
| 12G | Production Readiness Coverage Matrix | Coverage matrix for future production readiness | Matrix |
| 12H | Somatic Standalone Production-Readiness Ownership Map | Standalone ownership/integration map; Somatic owns its own path with no mandatory external owner | Ownership map |
| 12I | Integrative, Herbal, and Nutrition Knowledge Capability Profile | Metadata-only knowledge profile; explicitly blocks diagnosis, treatment planning, dosing, and prescription | Capability profile |
| 12K | External Compute and Quantum Backend Capability Profile | Capability profile for future external compute / quantum backends | Capability profile |
| 12L | Fabric Interop and A2A Audit-Boundary Capability Profile | Audit-boundary profile marking fabric transport / A2A runtime out-of-scope | Capability profile / audit boundary |
| 12M | Specialized Model Option Registry Capability Profile | Registry profile for specialized model options | Capability profile / registry |
| 12N | Workflow Orchestration Mode Registry Capability Profile | Registry of future workflow orchestration modes | Capability profile / registry |
| 12O | Workflow Mode Safety Gate Runtime Prerequisite Matrix | Safety-gate / runtime-prerequisite matrix for workflow modes | Matrix |
| 12P | Workflow Mode Activation Request Review Packet Boundary | Review-packet boundary for future workflow-mode activation requests | Boundary |
| 12Q | Non-Authorizing Workflow Mode Review Decision Record | Non-authorizing decision record for workflow-mode reviews | Decision record |
| 12R | Workflow Mode Review Audit Trail Index | Audit-trail index tying the workflow-mode review chain together | Audit index |
| 12S | Workflow Mode Review Chain Closeout Summary | Closeout summary of the 12N-12R workflow-mode review chain | Closeout summary |

## Runtime posture

Every Phase-12 capability profile is metadata-only. Real-mode runtime remains blocked across the series, enforced by `tests/test_phase12_series_invariants.py` (present-if checks over every `phase12*_status_summary` function):

- `execution_permitted` = False
- `real_mode_runtime_enabled` = False
- `real_mode_execution_permitted` = False
- `production_ready` = False
- `runtime_stage` = "not-implemented"
- `authorization_status` = "not-authorized"
- `grant_status` = "no-grant"

## Known symmetry deltas

These are documented here and are not changed by this phase:

- Phase 12A omits `grant_status` (it still reports `execution_permitted=False` and `authorization_status=not-authorized`).
- Phase 12F omits the adapter/provider/model execution-granted triad that the other profiles carry (it still reports the core runtime-blocked keys).

## Fabric status

The out-of-process fabric federation consumer connector was added in PR #66 and security-reviewed in PR #67 (see `docs/reviews/fabric-federation-security-review.md`). It routes all fabric I/O through a loopback HTTP sidecar, re-verifies content integrity before delivery, and keeps Secure Drop payloads as ciphertext. Real-mode runtime for Somatic''s own providers remains blocked.
