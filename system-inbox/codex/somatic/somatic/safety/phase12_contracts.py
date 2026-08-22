"""Phase 12 runtime authorization planning contracts.

These contracts define metadata-only planning surfaces for future runtime
authorization review. They never grant runtime execution.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256

from somatic.safety._builder_cache import install_builder_cache
from somatic.safety.adapter_readiness import REAL_MODE_PHASE_RUNTIME
from somatic.safety.phase11_contracts import (
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
    PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
    PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE,
    PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS,
    phase11_planning_governance_closeout_index,
    phase11_runtime_authorization_gap_ledger,
    rejected_phase11_planning_governance_closeout_index,
    rejected_phase11_runtime_authorization_gap_ledger,
    validate_phase11_planning_governance_closeout_index,
    validate_phase11_runtime_authorization_gap_ledger,
)

PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION = 1
PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND = "phase-12a-runtime-authorization-design-charter"
PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE = "11L-11M"
PHASE12A_AUTHORIZATION_PHASE = "design-only"
PHASE12A_AUTHORIZATION_STATUS = PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_STATUS
PHASE12A_CHARTER_SCOPE = "future-authorization-gate-model-only"
PHASE12A_CHARTER_STATUS = "phase-12a-satisfies-no-future-runtime-gates"
PHASE12A_FUTURE_GATE_STATUS = "future-required-not-satisfied"
PHASE12A_STATUS_LABELS = (
    "p12a-runtime-authorization-design-charter",
    "future-gates-metadata-only",
    "runtime-not-authorized-after-charter",
)
PHASE12A_FUTURE_REQUIRED_GATES = (
    "explicit-human-authorization-record",
    "scoped-runtime-domain-selection",
    "adapter-specific-safety-review",
    "privacy-data-boundary-review",
    "fixture-to-real-data-transition-review",
    "rollback-disable-plan",
    "audit-log-requirements",
    "jules-human-review-for-validator-authorization-semantics",
)

PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION = 1
PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND = "phase-12b-runtime-authorization-record-candidate"
PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE = "12A"
PHASE12B_AUTHORIZATION_PHASE = "record-candidate-only"
PHASE12B_AUTHORIZATION_STATUS = PHASE12A_AUTHORIZATION_STATUS
PHASE12B_DECISION_STATUS_NOT_SUBMITTED = "not-submitted"
PHASE12B_DECISION_STATUS_REVIEW_REQUIRED = "review-required"
PHASE12B_DECISION_STATUSES = (
    PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
    PHASE12B_DECISION_STATUS_REVIEW_REQUIRED,
)
PHASE12B_GRANT_STATUS = "no-grant"
PHASE12B_RECORD_CANDIDATE_STATUS = "phase-12b-record-candidate-not-approval-grant-or-permission"
PHASE12B_REQUEST_STATUS = "record-candidate-only"
PHASE12B_REVIEWER_ROLE_STATUS = "future-review-required"
PHASE12B_FUTURE_GATE_STATUS = "future-review-required-not-passed"
PHASE12B_STATUS_LABELS = (
    "p12b-runtime-authorization-record-candidate",
    "record-candidate-metadata-only",
    "runtime-not-authorized-after-record-candidate",
)
PHASE12B_REQUESTED_DOMAINS = (
    "document-ingestion",
    "wifi-csi-rf-booth",
)
PHASE12B_REQUIRED_REVIEWER_ROLES = (
    "human-runtime-authorizer",
    "privacy-boundary-reviewer",
    "adapter-safety-reviewer",
    "fixture-transition-reviewer",
    "audit-log-reviewer",
    "jules-validator-semantics-reviewer",
)
PHASE12B_REQUIRED_FUTURE_GATES = (
    (
        "explicit-human-authorization-record",
        "human-runtime-authorizer",
    ),
    (
        "scoped-runtime-domain-selection",
        "human-runtime-authorizer",
    ),
    (
        "adapter-specific-safety-review",
        "adapter-safety-reviewer",
    ),
    (
        "privacy-data-boundary-review",
        "privacy-boundary-reviewer",
    ),
    (
        "fixture-to-real-data-transition-review",
        "fixture-transition-reviewer",
    ),
    (
        "rollback-disable-plan",
        "audit-log-reviewer",
    ),
    (
        "audit-log-requirements",
        "audit-log-reviewer",
    ),
    (
        "jules-human-review-for-validator-authorization-semantics",
        "jules-validator-semantics-reviewer",
    ),
)

PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION = 1
PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND = "phase-12c-visual-supervision-capability-profile"
PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE = "12B"
PHASE12C_SUPERVISION_PHASE = "capability-profile-only"
PHASE12C_AUTHORIZATION_STATUS = PHASE12B_AUTHORIZATION_STATUS
PHASE12C_GRANT_STATUS = PHASE12B_GRANT_STATUS
PHASE12C_PROFILE_STATUS = "phase-12c-capability-profile-only-non-executing"
PHASE12C_CAPABILITY_STATUS = "profile-metadata-only"
PHASE12C_STATUS_LABELS = (
    "p12c-visual-supervision-capability-profile",
    "capability-profile-metadata-only",
    "runtime-not-authorized-after-capability-profile",
)
PHASE12C_ALLOWED_CAPABILITY_LABELS = (
    "dashboard-observation",
    "terminal-output-observation",
    "ci-status-observation",
    "doctor-output-observation",
    "review-status-observation",
    "sanitized-visual-event-summary",
    "notification-policy-metadata",
)

PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION = 1
PHASE12D_CONSENT_GATE_PROFILE_KIND = "phase-12d-visual-desktop-consent-gate-requirements"
PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE = "12A-12C"
PHASE12D_CONSENT_PHASE = "gate-requirements-only"
PHASE12D_AUTHORIZATION_STATUS = PHASE12C_AUTHORIZATION_STATUS
PHASE12D_GRANT_STATUS = PHASE12C_GRANT_STATUS
PHASE12D_CONSENT_GATE_STATUS = "phase-12d-consent-gate-requirements-only-non-executing"
PHASE12D_CAPABILITY_CATEGORY_STATUS = "metadata-only-no-consent-satisfied"
PHASE12D_FUTURE_GATE_STATUS = "future-consent-gate-required-not-satisfied"
PHASE12D_STATUS_LABELS = (
    "p12d-visual-desktop-consent-gate-requirements",
    "consent-gates-metadata-only",
    "runtime-not-authorized-after-consent-gate-requirements",
)
PHASE12D_CAPABILITY_CATEGORIES = (
    "screen-observation",
    "ocr-observation",
    "dashboard-observation",
    "terminal-observation",
    "ci-review-status-observation",
    "notification-policy",
    "overlay-policy",
    "click-input-automation-policy",
    "clipboard-policy",
    "camera-policy",
    "microphone-policy",
    "recording-policy",
)
PHASE12D_REQUIRED_FUTURE_GATES = (
    "explicit-human-consent-record",
    "scoped-capability-selection",
    "visible-indicator-requirement",
    "retention-redaction-policy",
    "disable-rollback-plan",
    "audit-log-requirement",
    "no-hidden-background-monitoring-declaration",
    "per-capability-review-requirement",
    "jules-human-review-for-validator-authorization-semantics",
)

PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION = 1
PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND = "phase-12e-physiological-sensor-capability-profile"
PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE = "12A-12B,12D,sensor-evidence"
PHASE12E_SENSOR_PHASE = "capability-profile-only"
PHASE12E_AUTHORIZATION_STATUS = PHASE12D_AUTHORIZATION_STATUS
PHASE12E_GRANT_STATUS = PHASE12D_GRANT_STATUS
PHASE12E_PROFILE_STATUS = "phase-12e-physiological-sensor-profile-only-non-executing"
PHASE12E_CAPABILITY_STATUS = "metadata-only-no-sensor-enabled"
PHASE12E_NON_DIAGNOSTIC_BOUNDARY_STATUS = "non-diagnostic-wellness-trend-metadata-only"
PHASE12E_FUTURE_GATE_STATUS = "future-physiological-sensor-gate-required-not-satisfied"
PHASE12E_SENSOR_EVIDENCE_BOUNDARY_STATUS = "existing-sensor-evidence-boundaries-metadata-only"
PHASE12E_STATUS_LABELS = (
    "p12e-physiological-sensor-capability-profile",
    "physiological-sensor-metadata-only",
    "runtime-not-authorized-after-physiological-sensor-profile",
)
PHASE12E_SENSOR_CAPABILITY_LABELS = (
    "hand-to-foot-bia-scale",
    "hand-to-feet-segmental-bia-scale",
    "multi-frequency-bia",
    "segmental-body-composition",
    "phase-angle-summary",
    "resistance-reactance-summary",
    "hydration-sensitive-body-composition-trend",
    "future-acoustic-body-map",
    "future-ultrasound-body-map",
)
PHASE12E_NON_DIAGNOSTIC_BOUNDARIES = (
    "wellness-body-composition-trend-metadata-only",
    "no-diagnosis",
    "no-clinical-recommendation",
    "no-disease-detection",
    "no-medical-scanner-equivalence-claim",
    "no-mri-ct-ultrasound-replacement-claim",
)
PHASE12E_REQUIRED_FUTURE_GATES = (
    "explicit-human-consent-record",
    "device-specific-safety-review",
    "manufacturer-device-provenance-review",
    "measurement-protocol-review",
    "hydration-meal-exercise-context-capture-policy",
    "privacy-redaction-policy",
    "retention-policy",
    "disable-rollback-plan",
    "clinical-boundary-disclaimer",
    "jules-human-review-for-validator-authorization-semantics",
)
PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES = (
    "fixture-only-sensor-evidence-providers",
    "metadata-only-provider-registry",
    "sensor-privacy-boundary",
    "real-mode-readiness-gate",
)

PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION = 1
PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND = "phase-12f-secure-drop-consumer-boundary"
PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE = "12A-12E,content-fabric-secure-drop"
PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA = "12eb228906d9708bd89b23328f66afba558963b0"
PHASE12F_CANONICAL_OWNER = "content-fabric"
PHASE12F_CANONICAL_REFERENCE = "kortex-audio-content-fabric-secure-drop-design-contract"
PHASE12F_CANONICAL_CONTRACT_STATUS = "canonical-contract-owned-by-content-fabric"
PHASE12F_CONSUMER_PHASE = "boundary-profile-only"
PHASE12F_AUTHORIZATION_STATUS = PHASE12E_AUTHORIZATION_STATUS
PHASE12F_GRANT_STATUS = PHASE12E_GRANT_STATUS
PHASE12F_BOUNDARY_STATUS = "phase-12f-secure-drop-consumer-boundary-only-non-executing"
PHASE12F_ARTIFACT_STATUS = "metadata-only-explicit-user-action-required"
PHASE12F_PROHIBITED_SOURCE_STATUS = "prohibited-autonomous-source"
PHASE12F_ENCRYPTION_REQUIREMENT_STATUS = "future-encryption-required-metadata-only"
PHASE12F_CONCEALMENT_STATUS = "future-concealment-optional-never-security-boundary"
PHASE12F_AUDIT_REQUIREMENT_STATUS = "future-audit-metadata-only-required"
PHASE12F_STATUS_LABELS = (
    "p12f-secure-drop-consumer-boundary",
    "secure-drop-consumer-boundary-metadata-only",
    "secure-drop-not-implemented-or-authorized-by-somatic",
)
PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS = (
    "sanitized-review-report",
    "sanitized-evidence-summary",
    "sanitized-doctor-status",
    "sanitized-sensor-profile-summary",
    "sanitized-runtime-authorization-status",
    "user-attached-document",
)
PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES = (
    "agent-selected-file",
    "automation-selected-file",
    "vault-secret",
    "env-var",
    "api-key",
    "filesystem-autoscan",
    "raw-document-body",
    "raw-csi-rf-capture",
    "raw-bia-reading",
    "raw-acoustic-ultrasound-data",
    "screenshot-or-ocr-dump",
)

PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION = 1
PHASE12G_PRODUCTION_READINESS_MATRIX_KIND = "phase-12g-production-readiness-coverage-matrix"
PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE = "11A-11M,12A-12F"
PHASE12G_READINESS_PHASE = "coverage-matrix-only"
PHASE12G_AUTHORIZATION_STATUS = PHASE12F_AUTHORIZATION_STATUS
PHASE12G_GRANT_STATUS = PHASE12F_GRANT_STATUS
PHASE12G_MATRIX_STATUS = "phase-12g-production-readiness-coverage-matrix-only-non-executing"
PHASE12G_COVERAGE_STATUS = "metadata-only-coverage-label"
PHASE12G_BLOCKED_RUNTIME_STATUS = "blocked-runtime-requirement-metadata-only"
PHASE12G_STATUS_LABELS = (
    "p12g-production-readiness-coverage-matrix",
    "coverage-matrix-metadata-only",
    "production-infrastructure-not-implemented-or-authorized-by-somatic",
)
PHASE12G_SOMATIC_RESPONSIBILITIES = (
    "direct",
    "boundary-only",
    "external-owner",
    "not-applicable-yet",
)
PHASE12G_REPO_FAMILY_OWNERS = (
    "somatic",
    "content-fabric",
    "locus",
    "multiverse",
    "aegis",
    "deployment-layer",
    "undecided",
)
PHASE12G_REVIEW_REQUIREMENTS = (
    "none",
    "codex-tests",
    "jules-review",
    "security-review",
    "human-authorization",
)
PHASE12G_PRODUCTION_READINESS_AREAS = (
    (
        "front-end-development",
        "Front-end development",
        "external-owner",
        "locus",
        "Somatic records only the boundary label for user-facing UI.",
        "User-facing app shell and product UI remain outside Somatic.",
        "separate app-owner runtime phase",
        "human-authorization",
    ),
    (
        "api-and-backend-logic",
        "API and backend logic",
        "external-owner",
        "deployment-layer",
        "Somatic exposes validator and doctor metadata only.",
        "Production API service logic remains outside Somatic.",
        "separate production-api runtime phase",
        "human-authorization",
    ),
    (
        "database-and-storage",
        "Database and storage",
        "external-owner",
        "content-fabric",
        "Somatic stores deterministic fixtures and sanitized docs only.",
        "Durable encrypted storage and transfer fabric remain outside Somatic.",
        "separate storage-runtime phase",
        "security-review",
    ),
    (
        "auth-and-permissions",
        "Auth and permissions",
        "boundary-only",
        "aegis",
        "Somatic reports not-authorized and no-grant metadata only.",
        "Identity, roles, and access-control runtime remain outside Somatic.",
        "human authorization and external access-control runtime phase",
        "security-review",
    ),
    (
        "hosting-and-deployment",
        "Hosting and deployment",
        "external-owner",
        "deployment-layer",
        "Somatic documents deployment gaps only.",
        "Hosting stack and release target remain outside Somatic.",
        "deployment-layer runtime phase",
        "human-authorization",
    ),
    (
        "cloud-and-compute",
        "Cloud and compute",
        "external-owner",
        "deployment-layer",
        "Somatic keeps compute execution blocked.",
        "Cloud compute ownership remains outside Somatic.",
        "deployment-layer compute phase",
        "human-authorization",
    ),
    (
        "ci-cd-and-version-control",
        "CI/CD and version control",
        "direct",
        "somatic",
        "Somatic owns local tests, fixtures, and repo check metadata.",
        "Protected release policy remains a cross-repo governance gap.",
        "repo policy and release-governance review",
        "codex-tests",
    ),
    (
        "security-and-rls",
        "Security and RLS",
        "boundary-only",
        "aegis",
        "Somatic owns fail-closed validators and metadata safety checks.",
        "Threat model, RLS policy, and hardening audit remain external.",
        "security review and separate datastore policy phase",
        "security-review",
    ),
    (
        "rate-limiting",
        "Rate limiting",
        "external-owner",
        "deployment-layer",
        "Somatic has no traffic path and no rate-limit runtime.",
        "Traffic controls remain outside Somatic.",
        "deployment-layer traffic-control phase",
        "security-review",
    ),
    (
        "caching-and-cdn",
        "Caching and CDN",
        "external-owner",
        "deployment-layer",
        "Somatic has no cache or edge-delivery runtime.",
        "Cache policy and CDN delivery remain outside Somatic.",
        "deployment-layer edge-delivery phase",
        "security-review",
    ),
    (
        "load-balancing-and-scaling",
        "Load balancing and scaling",
        "external-owner",
        "deployment-layer",
        "Somatic has no service pool or scaling runtime.",
        "Balancing, capacity, and autoscale plans remain outside Somatic.",
        "deployment-layer scaling phase",
        "security-review",
    ),
    (
        "error-tracking-and-logs",
        "Error tracking and logs",
        "boundary-only",
        "aegis",
        "Somatic exposes sanitized doctor and validation status only.",
        "Central logging, privacy review, and alert routing remain external.",
        "audit pipeline and human privacy review",
        "security-review",
    ),
    (
        "availability-and-recovery",
        "Availability and recovery",
        "boundary-only",
        "deployment-layer",
        "Somatic records recovery gaps only.",
        "SLOs, backups, failover, and incident response remain external.",
        "deployment-layer recovery phase",
        "human-authorization",
    ),
    (
        "infrastructure-management-and-compliance",
        "Infrastructure management and compliance",
        "boundary-only",
        "aegis",
        "Somatic keeps compliance notes as metadata only.",
        "Infrastructure ownership, audits, and compliance evidence remain external.",
        "security compliance review",
        "security-review",
    ),
    (
        "testing-frameworks",
        "Testing frameworks",
        "direct",
        "somatic",
        "Somatic owns focused phase tests and regression checks.",
        "Broader production test strategy remains cross-repo.",
        "none",
        "codex-tests",
    ),
    (
        "operations-and-reliability",
        "Operations and reliability",
        "direct",
        "somatic",
        "Somatic owns doctor/status surfaces for blocked runtime posture.",
        "On-call, runbooks, and reliability telemetry remain external.",
        "operations owner runtime phase",
        "jules-review",
    ),
    (
        "maintenance-and-governance",
        "Maintenance and governance",
        "direct",
        "somatic",
        "Somatic owns governance docs and phase invariant checks.",
        "Cross-repo stewardship and release cadence remain external.",
        "governance owner release phase",
        "jules-review",
    ),
    (
        "secrets-management",
        "Secrets management",
        "boundary-only",
        "aegis",
        "Somatic records that secret access remains blocked.",
        "Secret store, rotation, and breakglass process remain external.",
        "separate secret-management runtime phase",
        "security-review",
    ),
    (
        "system-discovery",
        "System discovery",
        "boundary-only",
        "locus",
        "Somatic reports only static metadata and no service discovery runtime.",
        "Service catalog, orchestration, and discovery remain outside Somatic.",
        "service-discovery owner runtime phase",
        "security-review",
    ),
)

PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION = 1
PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND = (
    "phase-12h-somatic-standalone-production-readiness-ownership-map"
)
PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE = "12G"
PHASE12H_READINESS_PHASE = "standalone-ownership-and-integration-map-only"
PHASE12H_AUTHORIZATION_STATUS = PHASE12G_AUTHORIZATION_STATUS
PHASE12H_GRANT_STATUS = PHASE12G_GRANT_STATUS
PHASE12H_MATRIX_STATUS = "phase-12h-standalone-ownership-map-only-non-executing"
PHASE12H_ENTRY_STATUS = "somatic-standalone-ownership-entry-metadata-only"
PHASE12H_OPTIONAL_PEER_STATUS = "optional-integration-peer-metadata-only"
PHASE12H_STATUS_LABELS = (
    "p12h-somatic-standalone-production-readiness-ownership-map",
    "standalone-ownership-and-integration-map-metadata-only",
    "optional-integration-peers-not-runtime-dependencies",
    "production-infrastructure-still-not-implemented",
)
PHASE12H_OPTIONAL_INTEGRATION_PEERS = (
    "locus",
    "aegis",
    "content-fabric-kortex",
    "multiverse",
    "custos",
)
PHASE12H_OPTIONAL_INTEGRATION_ROLES = (
    "optional",
    "consuming",
    "reviewing",
    "advanced-ui-feature",
    "fabric-transfer-feature",
)
PHASE12H_STANDALONE_UI_STATEMENT = "Somatic owns its own standalone UI path."
PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT = (
    "Locus may provide an advanced connected UI, but Somatic must remain usable without Locus."
)
PHASE12H_PEER_INTEGRATION_STATEMENT = (
    "Other repos may consume Somatic outputs or integrate with Somatic, but Somatic is not "
    "controlling them."
)
PHASE12H_SECURE_DROP_STATEMENT = (
    "Secure Drop canonical fabric remains outside Somatic, but Somatic may later expose "
    "user-selected export candidates to it."
)
PHASE12H_NON_AUTHORIZATION_STATEMENT = (
    "This phase does not make Somatic production-ready and does not authorize runtime."
)
PHASE12H_SOMATIC_STANDALONE_AREAS = (
    (
        "front-end-development",
        (
            "Somatic owns its own standalone UI path for research workflows, sensor evidence "
            "review, runtime authorization status, and local-first operation."
        ),
        "Somatic currently exposes CLI, doctor, docs, fixtures, and validator metadata.",
        (
            "Standalone Somatic UI remains future work behind explicit runtime authorization "
            "and review."
        ),
        (
            (
                "locus",
                "advanced-ui-feature",
                (
                    "Locus may provide an advanced connected UI, but Somatic must remain "
                    "usable without Locus."
                ),
            ),
            (
                "multiverse",
                "advanced-ui-feature",
                "Multiverse may provide a larger app shell, but Somatic keeps its own UI path.",
            ),
        ),
        "human-authorization",
    ),
    (
        "api-and-backend-logic",
        "Somatic owns its own API and service boundary for reviewed local-first operation.",
        "Somatic currently exposes deterministic validators, CLI, doctor, and metadata helpers.",
        "Standalone Somatic API and service runtime remain future work.",
        (
            (
                "locus",
                "optional",
                "Locus may orchestrate against a future reviewed Somatic service boundary.",
            ),
            (
                "custos",
                "consuming",
                "Custos may consume sanitized Somatic outputs without controlling Somatic.",
            ),
        ),
        "human-authorization",
    ),
    (
        "database-and-storage",
        "Somatic owns its own storage boundary for local research state and review metadata.",
        "Somatic currently stores deterministic fixtures and sanitized metadata only.",
        "Standalone durable storage remains future work with privacy and retention review.",
        (
            (
                "content-fabric-kortex",
                "fabric-transfer-feature",
                (
                    "Secure Drop canonical fabric remains outside Somatic, but Somatic may "
                    "later expose user-selected export candidates to it."
                ),
            ),
        ),
        "security-review",
    ),
    (
        "auth-and-permissions",
        "Somatic owns its own auth and permissions model for standalone operation.",
        "Somatic currently reports not-authorized and no-grant metadata only.",
        "Standalone identity, role, and permission enforcement remain future work.",
        (("aegis", "reviewing", "Aegis may review Somatic policy and permission design."),),
        "security-review",
    ),
    (
        "hosting-and-deployment",
        "Somatic owns its own deployment readiness checklist and release boundary.",
        "Somatic currently documents deployment gaps and keeps runtime disabled.",
        "Standalone hosting and deployment runtime remain future work.",
        (),
        "human-authorization",
    ),
    (
        "cloud-and-compute",
        "Somatic owns its own compute boundary and resource posture for standalone use.",
        "Somatic currently keeps compute execution blocked.",
        "Standalone cloud or compute runtime remains future work.",
        (),
        "human-authorization",
    ),
    (
        "ci-cd-and-version-control",
        "Somatic owns its own CI, test, fixture, and version-control hygiene.",
        "Somatic currently owns local tests, fixtures, and repo check metadata.",
        "Protected release policy and production governance remain future work.",
        (),
        "codex-tests",
    ),
    (
        "security-and-rls",
        "Somatic owns its own security and access-isolation model for standalone storage.",
        "Somatic currently owns fail-closed validators and metadata safety checks.",
        "Standalone access isolation, datastore policy, and hardening review remain future work.",
        (("aegis", "reviewing", "Aegis may provide security and abuse-prevention review."),),
        "security-review",
    ),
    (
        "rate-limiting",
        "Somatic owns its own rate-limit and abuse-control requirements for service boundaries.",
        "Somatic currently has no traffic path and no rate-limit runtime.",
        "Standalone traffic-control runtime remains future work.",
        (("aegis", "reviewing", "Aegis may review abuse-prevention and traffic policy."),),
        "security-review",
    ),
    (
        "caching-and-cdn",
        "Somatic owns its own cache and content-delivery policy for standalone deployment.",
        "Somatic currently has no cache or edge-delivery runtime.",
        "Standalone cache policy and delivery runtime remain future work.",
        (),
        "security-review",
    ),
    (
        "load-balancing-and-scaling",
        "Somatic owns its own scaling and capacity readiness model.",
        "Somatic currently has no service pool or scaling runtime.",
        "Standalone balancing, capacity, and autoscale plans remain future work.",
        (),
        "security-review",
    ),
    (
        "error-tracking-and-logs",
        "Somatic owns its own logs, audit, and error-tracking boundary.",
        "Somatic currently exposes sanitized doctor and validation status only.",
        "Standalone logging, audit retention, and alerting remain future work.",
        (
            ("aegis", "reviewing", "Aegis may review logging privacy and policy controls."),
            ("custos", "consuming", "Custos may consume sanitized status or audit summaries."),
        ),
        "security-review",
    ),
    (
        "availability-and-recovery",
        "Somatic owns its own availability, recovery, and rollback requirements.",
        "Somatic currently records recovery gaps only.",
        "Standalone SLOs, backups, failover, and incident response remain future work.",
        (),
        "human-authorization",
    ),
    (
        "infrastructure-management-and-compliance",
        "Somatic owns its own infrastructure and compliance readiness checklist.",
        "Somatic currently keeps compliance notes as metadata only.",
        "Standalone infrastructure evidence and compliance review remain future work.",
        (("aegis", "reviewing", "Aegis may review compliance and policy evidence."),),
        "security-review",
    ),
    (
        "testing-frameworks",
        "Somatic owns its own tests, fixtures, and regression gates.",
        "Somatic currently owns focused phase tests and regression checks.",
        "Broader production test strategy remains future work inside Somatic.",
        (),
        "codex-tests",
    ),
    (
        "operations-and-reliability",
        "Somatic owns its own operations and reliability surfaces.",
        "Somatic currently owns doctor and status surfaces for blocked runtime posture.",
        "Standalone runbooks, on-call policy, and reliability telemetry remain future work.",
        (
            (
                "locus",
                "advanced-ui-feature",
                "Locus may display advanced operational views without replacing Somatic.",
            ),
            ("custos", "consuming", "Custos may consume sanitized operational summaries."),
        ),
        "jules-review",
    ),
    (
        "maintenance-and-governance",
        "Somatic owns its own maintenance, governance, and phase invariant checks.",
        "Somatic currently owns governance docs and phase invariant checks.",
        "Standalone stewardship and release cadence remain future work.",
        (),
        "jules-review",
    ),
    (
        "secrets-management",
        "Somatic owns its own secrets boundary and future secret-access policy.",
        "Somatic currently records that secret access remains blocked.",
        "Standalone secret store, rotation, and breakglass policy remain future work.",
        (("aegis", "reviewing", "Aegis may review secret-management policy and controls."),),
        "security-review",
    ),
    (
        "system-discovery",
        "Somatic owns its own local system-discovery and service metadata boundary.",
        "Somatic currently reports static metadata and no service discovery runtime.",
        "Standalone discovery, service catalog, and coordination runtime remain future work.",
        (
            (
                "locus",
                "advanced-ui-feature",
                "Locus may provide advanced orchestration while Somatic remains standalone.",
            ),
        ),
        "security-review",
    ),
)

PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION = 1
PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND = (
    "phase-12i-integrative-herbal-nutrition-knowledge-capability-profile"
)
PHASE12I_SOURCE_PHASE_RANGE = "12A-12H,evidence-sensor-safety-boundaries"
PHASE12I_CAPABILITY_PHASE = "knowledge-profile-only"
PHASE12I_AUTHORIZATION_STATUS = PHASE12H_AUTHORIZATION_STATUS
PHASE12I_GRANT_STATUS = PHASE12H_GRANT_STATUS
PHASE12I_PROFILE_STATUS = "phase-12i-knowledge-profile-only-non-executing"
PHASE12I_LABEL_STATUS = "integrative-herbal-nutrition-label-metadata-only"
PHASE12I_SPECIALIST_PROFILE_STATUS = "specialist-review-profile-metadata-only"
PHASE12I_SOURCE_CLASS_STATUS = "source-class-metadata-only-no-ingestion"
PHASE12I_FUTURE_GATE_STATUS = "future-gate-required-not-satisfied"
PHASE12I_SOURCE_REFERENCE_STATUS = "referenced-safety-boundary-metadata-only"
PHASE12I_STATUS_LABELS = (
    "p12i-integrative-herbal-nutrition-knowledge-profile",
    "traditional-herbal-nutrition-labels-metadata-only",
    "medical-safety-warnings-preserved",
    "nutrition-and-herbal-runtime-not-implemented",
)
PHASE12I_USER_PREFERENCE_MODES = (
    "natural-first",
    "traditional-medicine-first",
    "nutrition-first",
    "food-as-medicine-informed",
    "plant-based",
    "animal-based",
    "mediterranean",
    "low-carb",
    "keto-informed",
    "elimination-diet-informed",
    "culturally-specific-diet",
    "tcm-informed-review",
    "herbalist-informed-review",
    "integrative-review",
    "western-medicine-minimized",
)
PHASE12I_SPECIALIST_PROFILE_LABELS = (
    "traditional-medicine-reviewer",
    "herbal-safety-reviewer",
    "integrative-medicine-reviewer",
    "natural-preference-review-profile",
    "nutrition-safety-reviewer",
    "metabolic-health-reviewer",
    "dietary-pattern-reviewer",
    "supplement-safety-reviewer",
    "integrative-nutrition-reviewer",
)
PHASE12I_SOURCE_CLASS_LABELS = (
    "traditional chinese materia medica",
    "herbal formula reference",
    "pharmacognosy reference",
    "herb-drug interaction reference",
    "botanical identity/adulteration reference",
    "herbal safety/toxicity monograph",
    "integrative medicine clinical literature",
    "ethnobotany reference",
    "user-provided practitioner note",
    "registered-dietitian reference",
    "clinical-nutrition guideline",
    "nutrition-database reference",
    "food-composition database",
    "micronutrient reference",
    "supplement-safety monograph",
    "herb-supplement interaction reference",
    "metabolic-health literature",
    "user-provided meal log",
    "user-provided lab report",
)
PHASE12I_REQUIRED_FUTURE_GATES = (
    "source-provenance-review",
    "clinical-safety-boundary-review",
    "herb-drug-interaction-review",
    "supplement-drug-interaction-review",
    "contraindication-toxicity-review",
    "botanical-identity-adulteration-review",
    "nutrition-safety-review",
    "eating-disorder-risk-review",
    "pregnancy-liver-kidney-cardiac-risk-review",
    "user-preference-consent",
    "evidence-grading-policy",
    "emergency-escalation-preservation",
    "jules-human-review-for-validator-or-medical-safety-semantics-changes",
)
PHASE12I_SOURCE_REFERENCE_PHASES = (
    (
        "12A",
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id",
        "p12a-charter-",
    ),
    (
        "12B",
        PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id",
        "p12b-record-",
    ),
    (
        "12C",
        PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id",
        "p12c-profile-",
    ),
    (
        "12D",
        PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id",
        "p12d-consent-profile-",
    ),
    (
        "12E",
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id",
        "p12e-sensor-profile-",
    ),
    (
        "12F",
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id",
        "p12f-secure-drop-boundary-",
    ),
    (
        "12G",
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id",
        "p12g-production-matrix-",
    ),
    (
        "12H",
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id",
        "p12h-standalone-ownership-",
    ),
)
PHASE12I_MEDICAL_BOUNDARY_STATEMENT = (
    "Phase 12I provides no medical advice, diagnosis, treatment planning, "
    "prescribing, dosing, nutrition prescription, or clinical decision support."
)
PHASE12I_WESTERN_MEDICINE_STATEMENT = "Phase 12I does not claim Western medicine is invalid."
PHASE12I_NATURAL_REMEDY_STATEMENT = "Phase 12I does not claim natural remedies are safe by default."
PHASE12I_FOOD_CURE_STATEMENT = "Phase 12I does not claim food cures disease."
PHASE12I_SAFETY_WARNING_STATEMENT = (
    "Emergency escalation, contraindication, medication interaction, pregnancy, liver, "
    "kidney, cardiac, eating-disorder, toxicity, contamination, and adulteration "
    "warnings stay preserved."
)

PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION = 1
PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND = (
    "phase-12k-external-compute-quantum-backend-capability-profile"
)
PHASE12K_SOURCE_PHASE_RANGE = "12A-12I,evidence-sensor-safety-boundaries"
PHASE12K_CAPABILITY_PHASE = "external-compute-quantum-profile-only"
PHASE12K_AUTHORIZATION_STATUS = PHASE12I_AUTHORIZATION_STATUS
PHASE12K_GRANT_STATUS = PHASE12I_GRANT_STATUS
PHASE12K_CREDENTIAL_POLICY = "external-secret-only"
PHASE12K_PROFILE_STATUS = "phase-12k-external-compute-quantum-profile-only-non-executing"
PHASE12K_BACKEND_OPTION_STATUS = "backend-label-metadata-only-no-sdk-or-api"
PHASE12K_WORKLOAD_CLASS_STATUS = "workload-class-metadata-only-no-execution"
PHASE12K_FUTURE_GATE_STATUS = "future-gate-required-not-satisfied"
PHASE12K_SOURCE_REFERENCE_STATUS = "referenced-safety-boundary-metadata-only"
PHASE12K_STATUS_LABELS = (
    "p12k-external-compute-quantum-backend-profile",
    "quantum-backend-labels-metadata-only",
    "external-compute-runtime-not-implemented",
    "quantum-workloads-non-authorizing",
)
PHASE12K_BACKEND_OPTION_LABELS = (
    "origin-wukong-qpanda3",
    "ibm-qiskit-runtime",
    "amazon-braket",
    "azure-quantum",
    "d-wave-leap",
)
PHASE12K_WORKLOAD_CLASSES = (
    "quantum simulation",
    "quantum-inspired optimization",
    "QUBO/combinatorial optimization",
    "hybrid quantum-classical optimization",
    "molecular/material candidate search",
    "model-routing optimization",
    "workflow scheduling",
    "sensor feature-selection optimization",
    "evidence-graph ranking",
    "resource-estimation and benchmark comparison",
)
PHASE12K_REQUIRED_FUTURE_GATES = (
    "external-compute-provider-risk-review",
    "credential-provenance-review",
    "external-secret-boundary-review",
    "human-approval-record-required",
    "cost-guard-review",
    "private-health-data-exclusion-review",
    "clinical-safety-boundary-review",
    "sdk-network-execution-review",
    "simulator-execution-review",
    "spending-control-review",
    "jules-security-medical-safety-review",
)
PHASE12K_SOURCE_REFERENCE_PHASES = (
    (
        "12A",
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id",
        "p12a-charter-",
    ),
    (
        "12B",
        PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id",
        "p12b-record-",
    ),
    (
        "12C",
        PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id",
        "p12c-profile-",
    ),
    (
        "12D",
        PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id",
        "p12d-consent-profile-",
    ),
    (
        "12E",
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id",
        "p12e-sensor-profile-",
    ),
    (
        "12F",
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id",
        "p12f-secure-drop-boundary-",
    ),
    (
        "12G",
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id",
        "p12g-production-matrix-",
    ),
    (
        "12H",
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id",
        "p12h-standalone-ownership-",
    ),
    (
        "12I",
        PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        "profile_id",
        "p12i-integrative-profile-",
    ),
)
PHASE12K_COMPUTE_BOUNDARY_STATEMENT = (
    "Phase 12K names future external compute and quantum backend options only; "
    "it performs no API calls, SDK execution, simulator execution, spending, "
    "provider execution, or runtime authorization."
)
PHASE12K_MEDICAL_BOUNDARY_STATEMENT = (
    "Phase 12K cannot produce diagnosis, treatment planning, clinical "
    "recommendations, medical advice, or private health-data processing."
)

PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION = 1
PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND = (
    "phase-12l-fabric-interop-a2a-audit-boundary-capability-profile"
)
PHASE12L_SOURCE_PHASE_RANGE = "12A-12K,evidence-sensor-fabric-safety-boundaries"
PHASE12L_CAPABILITY_PHASE = "fabric-interop-a2a-audit-boundary-profile-only"
PHASE12L_AUTHORIZATION_STATUS = PHASE12K_AUTHORIZATION_STATUS
PHASE12L_GRANT_STATUS = PHASE12K_GRANT_STATUS
PHASE12L_PROFILE_STATUS = "phase-12l-fabric-interop-a2a-audit-boundary-profile-only"
PHASE12L_FABRIC_INTEROP_STATUS = "metadata-only"
PHASE12L_MESSAGE_CODEC_STATUS = "not-implemented"
PHASE12L_A2A_TRANSPORT_STATUS = "not-implemented"
PHASE12L_MCP_INTEROP_STATUS = "not-implemented"
PHASE12L_SECURE_DROP_STATUS = "consumer-boundary-only"
PHASE12L_CREDENTIAL_POLICY = "phase-h-vault-reference-only"
PHASE12L_FABRIC_CAPABILITY_STATUS = "fabric-capability-label-metadata-only"
PHASE12L_FORBIDDEN_LABEL_STATUS = "out-of-scope-label-metadata-only"
PHASE12L_FUTURE_GATE_STATUS = "future-gate-required-not-satisfied"
PHASE12L_SOURCE_REFERENCE_STATUS = "referenced-safety-boundary-metadata-only"
PHASE12L_STATUS_LABELS = (
    "p12l-fabric-interop-a2a-audit-boundary-profile",
    "fabric-interop-labels-metadata-only",
    "a2a-mcp-secure-drop-runtime-not-implemented",
    "decode-to-audit-future-requirement-only",
)
PHASE12L_FABRIC_CAPABILITY_LABELS = (
    "fabric-pack-scan-aware",
    "connector-scan-compatible",
    "message-codec-seam-consumer",
    "plaintext-json-default",
    "decode-to-audit-required",
    "opaque-traffic-rejected",
    "a2a-handshake-aware",
    "capability-advertisement-aware",
    "codec-negotiation-aware",
    "keyring-did-identity-aware",
    "phase-h-gated",
    "agent-protocol-mcp-interop-aware",
    "locus-fusion-target-candidate",
    "locus-agent-expose-consumer-candidate",
    "secure-drop-ui-consumer-candidate",
)
PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS = (
    "no-bundled-agpl-codec",
    "no-glossopetrae-vendoring",
    "no-st3gg-vendoring",
    "no-covert-channel",
    "no-opaque-message-acting",
    "no-secret-in-pack",
    "no-secret-in-log",
    "no-secret-in-ipc",
    "no-secret-in-audit",
    "no-agent-invoked-secure-drop",
    "no-automation-invoked-secure-drop",
    "no-untrusted-content-execution",
)
PHASE12L_REQUIRED_FUTURE_GATES = (
    "shared-fabric-contract-review",
    "message-codec-contract-review",
    "decode-to-audit-policy-review",
    "a2a-handshake-contract-review",
    "phase-h-vault-boundary-review",
    "mcp-agent-protocol-interop-review",
    "secure-drop-user-initiation-review",
    "connector-pack-static-gate-review",
    "cross-repo-mutation-denial-review",
    "jules-security-fabric-safety-review",
)
PHASE12L_SOURCE_REFERENCE_PHASES = (
    (
        "12A",
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id",
        "p12a-charter-",
    ),
    (
        "12B",
        PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id",
        "p12b-record-",
    ),
    (
        "12C",
        PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id",
        "p12c-profile-",
    ),
    (
        "12D",
        PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id",
        "p12d-consent-profile-",
    ),
    (
        "12E",
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id",
        "p12e-sensor-profile-",
    ),
    (
        "12F",
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id",
        "p12f-secure-drop-boundary-",
    ),
    (
        "12G",
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id",
        "p12g-production-matrix-",
    ),
    (
        "12H",
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id",
        "p12h-standalone-ownership-",
    ),
    (
        "12I",
        PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        "profile_id",
        "p12i-integrative-profile-",
    ),
    (
        "12K",
        PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        "profile_id",
        "p12k-compute-quantum-profile-",
    ),
)
PHASE12L_FABRIC_BOUNDARY_STATEMENT = (
    "Phase 12L names future fabric interop and A2A audit boundaries only; "
    "it implements no runtime messaging, codec, transport, connector install, "
    "pack registration, MCP serving, provider call, or cross-repo mutation."
)
PHASE12L_AUDIT_BOUNDARY_STATEMENT = (
    "Plaintext JSON default and decode-to-audit are future fabric requirements only; "
    "Phase 12L implements no MessageCodec, transport, MCP runtime, or audit writer."
)
PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT = (
    "Secure Drop remains a user-initiated content-fabric boundary only; "
    "no agent or automation invocation is allowed."
)

PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION = 1
PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND = (
    "phase-12m-specialized-model-option-registry-capability-profile"
)
PHASE12M_SOURCE_PHASE_RANGE = "12A-12L,evidence-sensor-model-safety-boundaries"
PHASE12M_MODEL_OPTION_PROFILE_PHASE = "metadata-only"
PHASE12M_AUTHORIZATION_STATUS = PHASE12L_AUTHORIZATION_STATUS
PHASE12M_GRANT_STATUS = PHASE12L_GRANT_STATUS
PHASE12M_PROFILE_STATUS = "phase-12m-specialized-model-option-registry-profile-only-non-executing"
PHASE12M_MODEL_OPTION_CATEGORY_STATUS = "model-option-category-metadata-only"
PHASE12M_CANDIDATE_LABEL_STATUS = "model-candidate-label-metadata-only"
PHASE12M_FUTURE_GATE_STATUS = "future-gate-required-not-satisfied"
PHASE12M_SOURCE_REFERENCE_STATUS = "referenced-safety-boundary-metadata-only"
PHASE12M_STATUS_LABELS = (
    "p12m-specialized-model-option-registry-profile",
    "model-option-labels-metadata-only",
    "specialized-model-runtime-not-implemented",
    "medical-sensor-model-labels-non-authorizing",
)
PHASE12M_MODEL_OPTION_CATEGORIES = (
    "medical-language-model",
    "medical-multimodal-model",
    "medical-safety-reviewer-model",
    "scientific-generative-model",
    "protein-structure-model",
    "ligand-binding-model",
    "reaction-material-model",
    "herbal-interaction-safety-model",
    "nutrition-risk-safety-model",
    "time-series-foundation-model",
    "csi-rf-signal-model",
    "bia-metabolic-trend-model",
    "acoustic-ultrasound-body-map-model",
    "active-learning-optimization-engine",
    "bayesian-optimization-engine",
    "evidence-grading-model",
    "contraindication-toxicity-reviewer",
    "emergency-escalation-classifier",
)
PHASE12M_CANDIDATE_LABELS = (
    "Med-Gemini-style-medical-multimodal-model",
    "MedGemma-style-medical-open-weight-model",
    "Meditron-BioMistral-style-medical-language-model",
    "LOGOS-style-scientific-generative-model",
    "AlphaFold-Boltz-ESM-style-structure-model",
    "Kronos-like-time-series-model",
    "Chronos-MOMENT-Kairos-style-time-series-model",
    "CSI-RF-signal-model",
    "BIA-trend-model",
    "acoustic-ultrasound-body-map-model",
    "ALchemist-style-Bayesian-optimization-engine",
    "herb-drug-interaction-safety-model",
    "supplement-drug-interaction-safety-model",
    "nutrition-risk-safety-model",
    "emergency-escalation-classifier",
    "contraindication-toxicity-reviewer",
)
PHASE12M_REQUIRED_FUTURE_GATES = (
    "model-source-provenance-review",
    "model-license-review",
    "clinical-safety-boundary-review",
    "medical-model-validation-review",
    "sensor-model-validation-review",
    "csi-rf-privacy-review",
    "bias-and-evidence-quality-review",
    "herb-drug-interaction-safety-review",
    "nutrition-safety-review",
    "private-health-data-boundary-review",
    "model-runtime-authorization-review",
    "jules-security-medical-safety-review-for-validator-or-safety-semantics-changes",
)
PHASE12M_SOURCE_REFERENCE_PHASES = (
    (
        "12A",
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id",
        "p12a-charter-",
    ),
    (
        "12B",
        PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id",
        "p12b-record-",
    ),
    (
        "12C",
        PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id",
        "p12c-profile-",
    ),
    (
        "12D",
        PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id",
        "p12d-consent-profile-",
    ),
    (
        "12E",
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id",
        "p12e-sensor-profile-",
    ),
    (
        "12F",
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id",
        "p12f-secure-drop-boundary-",
    ),
    (
        "12G",
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id",
        "p12g-production-matrix-",
    ),
    (
        "12H",
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id",
        "p12h-standalone-ownership-",
    ),
    (
        "12I",
        PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        "profile_id",
        "p12i-integrative-profile-",
    ),
    (
        "12K",
        PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        "profile_id",
        "p12k-compute-quantum-profile-",
    ),
    (
        "12L",
        PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        "profile_id",
        "p12l-fabric-a2a-audit-profile-",
    ),
)
PHASE12M_MODEL_BOUNDARY_STATEMENT = (
    "Phase 12M names future specialized model options only; it performs no model loading, "
    "model execution, provider execution, training, fine-tuning, network call, database "
    "ingestion, web scraping, runtime adapter, active grant, or real-mode authorization."
)
PHASE12M_MEDICAL_BOUNDARY_STATEMENT = (
    "Phase 12M medical model labels cannot provide diagnosis, treatment planning, medical "
    "advice, prescribing, clinical decision support, herb or supplement dosing, calorie or "
    "macro prescription, or nutrition prescription."
)
PHASE12M_SENSOR_BOUNDARY_STATEMENT = (
    "Phase 12M CSI/RF, BIA, acoustic, and ultrasound model labels do not permit device "
    "access, raw sensor processing, monitoring, diagnosis, or clinical decision support."
)

PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION = 1
PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND = (
    "phase-12n-workflow-orchestration-mode-registry-capability-profile"
)
PHASE12N_SOURCE_PHASE_RANGE = "12A-12M,evidence-sensor-workflow-safety-boundaries"
PHASE12N_WORKFLOW_MODE_PROFILE_PHASE = "metadata-only"
PHASE12N_AUTHORIZATION_STATUS = PHASE12M_AUTHORIZATION_STATUS
PHASE12N_GRANT_STATUS = PHASE12M_GRANT_STATUS
PHASE12N_PROFILE_STATUS = (
    "phase-12n-workflow-orchestration-mode-registry-profile-only-non-executing"
)
PHASE12N_WORKFLOW_MODE_STATUS = "workflow-mode-metadata-only"
PHASE12N_FUSION_CONCEPT_STATUS = "fusion-concept-metadata-only"
PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS = "scientist-evolution-concept-metadata-only"
PHASE12N_FUTURE_GATE_STATUS = "future-gate-required-not-satisfied"
PHASE12N_SOURCE_REFERENCE_STATUS = "referenced-safety-boundary-metadata-only"
PHASE12N_STATUS_LABELS = (
    "p12n-workflow-orchestration-mode-registry-profile",
    "workflow-mode-labels-metadata-only",
    "fusion-scientist-runtime-not-implemented",
    "orchestration-runtime-non-authorizing",
)
PHASE12N_WORKFLOW_MODES = (
    (
        "normal-mode",
        (
            "Deterministic Somatic workflow; evidence/safety-first; conservative review "
            "path; no adaptive model routing; no autonomous experimentation."
        ),
    ),
    (
        "fusion-mode",
        (
            "Future coordinator may route across selectable model/specialist roles; "
            "inspired by Fugu/TRINITY/Conductor-style learned or policy-driven model "
            "orchestration; no execution in this phase."
        ),
    ),
    (
        "scientist-evolution-mode",
        (
            "Future hypothesis-generation, experiment-design, analysis, critique, and "
            "iteration loop; inspired by AI-Scientist/AI-Scientist-v2/LanguageEvolution-style "
            "research systems; no code execution, experiment execution, web access, "
            "manuscript generation, autonomous publication, or runtime behavior in this phase."
        ),
    ),
)
PHASE12N_FUSION_CONCEPT_LABELS = (
    "multi-model-coordinator-candidate",
    "thinker-worker-verifier-role-candidate",
    "learned-coordinator-candidate",
    "conductor-style-routing-candidate",
    "model-pool-selection-candidate",
    "provider-opt-out-policy-candidate",
    "cost-performance-routing-candidate",
    "privacy-compliance-routing-candidate",
    "verifier-agent-candidate",
)
PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS = (
    "hypothesis-generation-candidate",
    "experiment-design-candidate",
    "tree-search-research-candidate",
    "iterative-critique-candidate",
    "result-analysis-candidate",
    "literature-review-candidate",
    "novelty-check-candidate",
    "manuscript-draft-candidate",
    "reproducibility-check-candidate",
    "sandbox-required-for-code-execution",
    "human-review-required-before-real-experiment",
)
PHASE12N_REQUIRED_FUTURE_GATES = (
    "workflow-mode-policy-review",
    "model-routing-safety-review",
    "provider-selection-privacy-review",
    "cost-control-review",
    "autonomous-experiment-sandbox-review",
    "code-execution-sandbox-review",
    "scientific-claim-validation-review",
    "medical-safety-boundary-review",
    "private-health-data-boundary-review",
    "publication-disclosure-policy-review",
    "jules-security-medical-safety-review-for-validator-or-safety-semantics-changes",
)
PHASE12N_SOURCE_REFERENCE_PHASES = (
    (
        "12A",
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id",
        "p12a-charter-",
    ),
    (
        "12B",
        PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id",
        "p12b-record-",
    ),
    (
        "12C",
        PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id",
        "p12c-profile-",
    ),
    (
        "12D",
        PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id",
        "p12d-consent-profile-",
    ),
    (
        "12E",
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id",
        "p12e-sensor-profile-",
    ),
    (
        "12F",
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id",
        "p12f-secure-drop-boundary-",
    ),
    (
        "12G",
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id",
        "p12g-production-matrix-",
    ),
    (
        "12H",
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id",
        "p12h-standalone-ownership-",
    ),
    (
        "12I",
        PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        "profile_id",
        "p12i-integrative-profile-",
    ),
    (
        "12K",
        PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        "profile_id",
        "p12k-compute-quantum-profile-",
    ),
    (
        "12L",
        PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        "profile_id",
        "p12l-fabric-a2a-audit-profile-",
    ),
    (
        "12M",
        PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        "profile_id",
        "p12m-model-option-registry-profile-",
    ),
)
PHASE12N_WORKFLOW_BOUNDARY_STATEMENT = (
    "Phase 12N names future workflow orchestration modes only; it performs no runtime "
    "orchestration, model routing, model execution, provider execution, model loading, "
    "training, fine-tuning, code execution, experiment execution, network call, database "
    "ingestion, web scraping, runtime adapter, active grant, or real-mode authorization."
)
PHASE12N_FUSION_BOUNDARY_STATEMENT = (
    "Phase 12N fusion-mode labels cannot execute model routing, provider calls, model "
    "loading, learned coordination, agent routing, network calls, or runtime orchestration."
)
PHASE12N_SCIENTIST_BOUNDARY_STATEMENT = (
    "Phase 12N scientist-evolution-mode labels cannot execute code, experiments, web "
    "access, literature search, database ingestion, manuscript generation, autonomous "
    "publication, model training, model fine-tuning, or autonomous research actions."
)
PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT = (
    "Phase 12N workflow modes cannot provide clinical decision support, diagnosis, "
    "treatment planning, medical advice, dosing, nutrition prescription, device access, "
    "raw sensor processing, or private health-data processing."
)

PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION = 1
PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND = (
    "phase-12o-workflow-mode-safety-gate-runtime-prerequisite-matrix"
)
PHASE12O_SOURCE_PHASE = "12N"
PHASE12O_MATRIX_PHASE = "workflow-mode-safety-gate-runtime-prerequisite-matrix-only"
PHASE12O_AUTHORIZATION_STATUS = PHASE12N_AUTHORIZATION_STATUS
PHASE12O_GRANT_STATUS = PHASE12N_GRANT_STATUS
PHASE12O_MATRIX_STATUS = (
    "phase-12o-workflow-mode-safety-gate-runtime-prerequisite-matrix-only-non-executing"
)
PHASE12O_WORKFLOW_MODE_MATRIX_STATUS = "workflow-mode-prerequisite-matrix-metadata-only"
PHASE12O_FUTURE_GATE_STATUS = "future-runtime-prerequisite-required-not-satisfied"
PHASE12O_MODE_GATE_STATUS = "mode-gate-runtime-prerequisite-not-satisfied"
PHASE12O_SOURCE_REFERENCE_STATUS = "phase-12n-workflow-mode-profile-reference-metadata-only"
PHASE12O_GATE_SCOPE = "required-before-any-runtime-mode-authorization"
PHASE12O_STATUS_LABELS = (
    "p12o-workflow-mode-safety-gate-runtime-prerequisite-matrix",
    "workflow-mode-runtime-prerequisites-metadata-only",
    "all-workflow-mode-gates-unsatisfied",
    "runtime-authorization-not-created",
)
PHASE12O_WORKFLOW_MODES = tuple(label for label, _ in PHASE12N_WORKFLOW_MODES)
PHASE12O_REQUIRED_FUTURE_GATES = (
    "workflow-mode-policy-review",
    "model-routing-safety-review",
    "provider-selection-privacy-review",
    "cost-control-review",
    "code-execution-sandbox-review",
    "autonomous-experiment-sandbox-review",
    "scientific-claim-validation-review",
    "medical-safety-boundary-review",
    "private-health-data-boundary-review",
    "publication-disclosure-policy-review",
    "jules-security-medical-safety-review",
)
PHASE12O_MATRIX_BOUNDARY_STATEMENT = (
    "Phase 12O defines future workflow-mode runtime prerequisites only; it performs "
    "no runtime adapter, workflow execution, model or provider execution, model "
    "routing, code execution, experiment execution, web behavior, database behavior, "
    "network behavior, active grant, or real-mode authorization."
)
PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT = (
    "Phase 12O safety gates cannot provide clinical decision support, private "
    "health-data processing, diagnosis, treatment planning, medical advice, dosing, "
    "nutrition prescription, device access, or raw sensor processing."
)
PHASE12O_STANDALONE_FIRST_STATEMENT = (
    "Phase 12O keeps Somatic standalone-first: prerequisite gates describe Somatic "
    "future review requirements and do not require another repository to make Somatic usable."
)

PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION = 1
PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND = (
    "phase-12p-workflow-mode-activation-request-review-packet-boundary"
)
PHASE12P_SOURCE_PHASE_RANGE = "12N-12O"
PHASE12P_PACKET_PHASE = "review-packet-boundary-only"
PHASE12P_AUTHORIZATION_STATUS = PHASE12O_AUTHORIZATION_STATUS
PHASE12P_GRANT_STATUS = PHASE12O_GRANT_STATUS
PHASE12P_REQUESTED_TRANSITION_STATUS = "review-request-only/not-authorized"
PHASE12P_PACKET_STATUS = (
    "phase-12p-workflow-mode-activation-request-review-packet-boundary-only-non-executing"
)
PHASE12P_MODE_PACKET_STATUS = "workflow-mode-activation-review-request-packet-metadata-only"
PHASE12P_FUTURE_GATE_STATUS = "future-review-gate-unsatisfied-not-passed"
PHASE12P_REVIEWER_CLASS_STATUS = "future-reviewer-required-unmet"
PHASE12P_RISK_PLACEHOLDER_STATUS = "risk-summary-placeholder-unfilled"
PHASE12P_EVIDENCE_PLACEHOLDER_STATUS = "evidence-inventory-placeholder-unfilled"
PHASE12P_SOURCE_REFERENCE_STATUS = "phase-12n-12o-review-source-reference-metadata-only"
PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS = (
    "phase-12o-prerequisite-matrix-reference-metadata-only"
)
PHASE12P_DENIAL_BLOCKED_STATUS = "blocked-default-fail-closed"
PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS = "workflow-mode-activation-not-permitted"
PHASE12P_STATUS_LABELS = (
    "p12p-workflow-mode-activation-request-review-packet-boundary",
    "metadata-only-review-packet-boundary",
    "workflow-mode-activation-not-permitted",
    "all-future-gates-unsatisfied",
    "runtime-authorization-not-created",
)
PHASE12P_WORKFLOW_MODES = PHASE12O_WORKFLOW_MODES
PHASE12P_REQUIRED_FUTURE_GATES = PHASE12O_REQUIRED_FUTURE_GATES
PHASE12P_REQUIRED_REVIEWER_CLASSES = (
    "human-reviewer",
    "jules-reviewer",
    "security-reviewer",
    "medical-safety-reviewer",
)
PHASE12P_RISK_SUMMARY_PLACEHOLDERS = (
    "workflow-mode-policy-risk-summary",
    "model-routing-provider-risk-summary",
    "code-experiment-sandbox-risk-summary",
    "scientific-claim-medical-safety-risk-summary",
    "private-health-data-device-sensor-risk-summary",
    "publication-disclosure-production-risk-summary",
)
PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS = (
    "phase-12n-workflow-mode-source-evidence-inventory",
    "phase-12o-prerequisite-matrix-evidence-inventory",
    "future-gate-review-evidence-inventory",
    "reviewer-attestation-evidence-inventory",
)
PHASE12P_PACKET_BOUNDARY_STATEMENT = (
    "Phase 12P defines a human review packet boundary only; it creates no activation, "
    "approval, active grant, runtime authorization, execution permission, workflow "
    "execution, model routing, provider execution, code execution, experiment execution, "
    "network call, database ingestion, web scraping, clinical decision support, private "
    "health-data processing, device access, raw sensor processing, production readiness, "
    "or real-mode authorization."
)
PHASE12P_REVIEW_REQUIREMENT_STATEMENT = (
    "Human, Jules, security, and medical-safety review remain required before any "
    "future runtime authorization review can proceed."
)
PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT = (
    "Phase 12P cannot provide clinical decision support, diagnosis, treatment planning, "
    "medical advice, dosing, nutrition prescription, device access, raw sensor processing, "
    "or private health-data processing."
)

PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION = 1
PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND = (
    "phase-12q-non-authorizing-workflow-mode-review-decision-record"
)
PHASE12Q_SOURCE_PHASE_RANGE = "12N-12P"
PHASE12Q_DECISION_RECORD_PHASE = "review-decision-record-only"
PHASE12Q_AUTHORIZATION_STATUS = PHASE12P_AUTHORIZATION_STATUS
PHASE12Q_GRANT_STATUS = PHASE12P_GRANT_STATUS
PHASE12Q_DECISION_RECORD_STATUS = (
    "phase-12q-non-authorizing-workflow-mode-review-decision-record-only"
)
PHASE12Q_SOURCE_REFERENCE_STATUS = (
    "phase-12n-12o-12p-review-decision-source-reference-metadata-only"
)
PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS = "future-review-gate-unsatisfied-decision-snapshot"
PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS = "reviewer-class-required-for-future-review"
PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS = "reviewer-class-not-represented-in-current-record"
PHASE12Q_DEFAULT_DECISION_STATUS = "review-not-submitted"
PHASE12Q_DEFAULT_DECISION_REASON_CODE = "not-submitted-future-review-required"
PHASE12Q_DECISION_STATUSES = (
    PHASE12Q_DEFAULT_DECISION_STATUS,
    "review-blocked",
    "returned-for-fix-only-changes",
    "denied-no-runtime-authorization",
    "expired-no-runtime-authorization",
    "review-complete-no-runtime-authorization",
)
PHASE12Q_DECISION_REASON_CODES = (
    PHASE12Q_DEFAULT_DECISION_REASON_CODE,
    "blocked-unsatisfied-future-gates",
    "returned-fix-only-no-runtime-authorization",
    "denied-runtime-authorization-not-granted",
    "expired-no-runtime-authorization",
    "review-complete-runtime-authorization-not-granted",
)
PHASE12Q_DECISION_STATUS_REASON_CODES = dict(
    zip(PHASE12Q_DECISION_STATUSES, PHASE12Q_DECISION_REASON_CODES, strict=True)
)
PHASE12Q_DECISION_STATUS_DISPOSITIONS = {
    "review-not-submitted": "not-submitted-no-runtime-authorization",
    "review-blocked": "blocked-no-runtime-authorization",
    "returned-for-fix-only-changes": "returned-for-fix-only-no-runtime-authorization",
    "denied-no-runtime-authorization": "denied-no-runtime-authorization",
    "expired-no-runtime-authorization": "expired-no-runtime-authorization",
    "review-complete-no-runtime-authorization": ("review-complete-without-runtime-authorization"),
}
PHASE12Q_STATUS_LABELS = (
    "p12q-non-authorizing-workflow-mode-review-decision-record",
    "metadata-only-review-decision-record",
    "review-decision-record-only",
    "workflow-mode-activation-not-permitted",
    "runtime-authorization-not-granted",
    "execution-permitted-false",
)
PHASE12Q_WORKFLOW_MODES = PHASE12P_WORKFLOW_MODES
PHASE12Q_REQUIRED_FUTURE_GATES = PHASE12P_REQUIRED_FUTURE_GATES
PHASE12Q_REQUIRED_REVIEWER_CLASSES = PHASE12P_REQUIRED_REVIEWER_CLASSES
PHASE12Q_DECISION_SUMMARY = (
    "Phase 12Q records a future review decision shape only; current review is not "
    "submitted, all future gates remain unsatisfied, and all runtime booleans remain false."
)
PHASE12Q_DECISION_BOUNDARY_STATEMENT = (
    "Phase 12Q defines a non-authorizing workflow-mode review decision record only; it "
    "creates no approval for runtime, active grant, runtime authorization, execution "
    "permission, workflow-mode activation, workflow execution, model routing, provider "
    "execution, model execution, model loading, training, fine-tuning, code execution, "
    "experiment execution, autonomous experimentation, web access, database ingestion, "
    "web scraping, network call, clinical decision support, diagnosis, treatment planning, "
    "medical advice, dosing, nutrition prescription, device access, raw sensor processing, "
    "private health-data processing, production readiness, or real-mode authorization."
)
PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT = (
    "Phase 12Q cannot provide clinical decision support, diagnosis, treatment planning, "
    "medical advice, dosing, nutrition prescription, device access, raw sensor processing, "
    "or private health-data processing."
)

PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION = 1
PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND = (
    "phase-12r-workflow-mode-review-audit-trail-index"
)
PHASE12R_SOURCE_PHASE_RANGE = "12N-12Q"
PHASE12R_AUDIT_TRAIL_INDEX_PHASE = "workflow-mode-review-audit-trail-index-only"
PHASE12R_AUTHORIZATION_STATUS = PHASE12Q_AUTHORIZATION_STATUS
PHASE12R_GRANT_STATUS = PHASE12Q_GRANT_STATUS
PHASE12R_AUDIT_TRAIL_INDEX_STATUS = "phase-12r-workflow-mode-review-audit-trail-index-only"
PHASE12R_SOURCE_REFERENCE_STATUS = (
    "phase-12n-12o-12p-12q-audit-trail-source-reference-metadata-only"
)
PHASE12R_MODE_INDEX_STATUS = "workflow-mode-label-indexed-for-audit-only"
PHASE12R_PACKET_REFERENCE_STATUS = "phase-12p-activation-request-packet-reference-metadata-only"
PHASE12R_DECISION_RECORD_REFERENCE_STATUS = (
    "phase-12q-review-decision-record-reference-metadata-only"
)
PHASE12R_DECISION_STATUS_SUMMARY_STATUS = "phase-12q-decision-status-summary-metadata-only"
PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS = PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS
PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS = PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS
PHASE12R_STALE_STATUS = "not-stale-current-index-metadata-only"
PHASE12R_REVIEW_NEEDED_STATUS = "review-needed-future-human-jules-security-medical-safety-review"
PHASE12R_STALE_REVIEW_NEEDED_STATUS = "review-needed-not-stale-runtime-disabled"
PHASE12R_STATUS_LABELS = (
    "p12r-workflow-mode-review-audit-trail-index",
    "metadata-only-workflow-mode-review-audit-trail-index",
    "audit-trail-index-only",
    "workflow-mode-activation-not-permitted",
    "runtime-authorization-not-granted",
    "execution-permitted-false",
)
PHASE12R_WORKFLOW_MODES = PHASE12Q_WORKFLOW_MODES
PHASE12R_REQUIRED_FUTURE_GATES = PHASE12Q_REQUIRED_FUTURE_GATES
PHASE12R_REQUIRED_REVIEWER_CLASSES = PHASE12Q_REQUIRED_REVIEWER_CLASSES
PHASE12R_DECISION_SUMMARY = (
    "Phase 12R indexes the Phase 12N through Phase 12Q workflow-mode review chain "
    "for audit only; current review remains not submitted, all future gates remain "
    "unsatisfied, and all runtime booleans remain false."
)
PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT = (
    "Phase 12R defines a metadata-only workflow-mode review audit trail index only; "
    "it creates no approval for runtime, active grant, runtime authorization, execution "
    "permission, workflow-mode activation, workflow execution, model routing, provider "
    "execution, model execution, model loading, training, fine-tuning, code execution, "
    "experiment execution, autonomous experimentation, shell execution, process execution, "
    "cache/event-bus/pub-sub runtime, web access, database ingestion, database writes, "
    "query execution, web scraping, network call, clinical decision support, diagnosis, "
    "treatment planning, medical advice, dosing, nutrition prescription, device access, "
    "raw sensor processing, private health-data processing, production readiness, or "
    "real-mode authorization."
)
PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT = (
    "Phase 12R cannot provide clinical decision support, diagnosis, treatment planning, "
    "medical advice, dosing, nutrition prescription, device access, raw sensor processing, "
    "or private health-data processing."
)

PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION = 1
PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND = (
    "phase-12s-workflow-mode-review-chain-closeout-summary"
)
PHASE12S_SOURCE_PHASE_RANGE = "12N-12R"
PHASE12S_CLOSEOUT_SUMMARY_PHASE = "workflow-mode-review-chain-closeout-summary-only"
PHASE12S_AUTHORIZATION_STATUS = PHASE12R_AUTHORIZATION_STATUS
PHASE12S_GRANT_STATUS = PHASE12R_GRANT_STATUS
PHASE12S_SUMMARY_STATUS = "phase-12s-workflow-mode-review-chain-closeout-summary-only"
PHASE12S_SOURCE_REFERENCE_STATUS = (
    "phase-12n-12o-12p-12q-12r-closeout-source-reference-metadata-only"
)
PHASE12S_MODE_COVERAGE_STATUS = "workflow-mode-label-covered-for-closeout-only"
PHASE12S_REVIEW_CHAIN_STATUS = "review-chain-documented-no-runtime-authorization"
PHASE12S_REVIEWER_NAVIGATION_SUMMARY = (
    "Phase 12S gives reviewers a metadata-only navigation summary for the Phase 12N "
    "through Phase 12R workflow-mode review chain; it creates no runtime authorization."
)
PHASE12S_OPERATOR_HANDOFF_SUMMARY = (
    "Phase 12S gives operators a closeout summary for finding the blocked review chain; "
    "future runtime work still requires explicit authorization and review."
)
PHASE12S_CLOSEOUT_STATUSES = (
    "closeout-summary-only",
    "review-chain-documented-no-runtime-authorization",
    "operator-handoff-ready-no-runtime-authorization",
    "blocked-until-future-runtime-authorization",
    "future-review-required-before-runtime",
)
PHASE12S_DEFAULT_CLOSEOUT_STATUS = "closeout-summary-only"
PHASE12S_STATUS_LABELS = (
    "p12s-workflow-mode-review-chain-closeout-summary",
    "metadata-only-workflow-mode-review-chain-closeout-summary",
    "closeout-summary-only",
    "workflow-mode-activation-not-permitted",
    "runtime-authorization-not-granted",
    "execution-permitted-false",
)
PHASE12S_WORKFLOW_MODES = PHASE12R_WORKFLOW_MODES
PHASE12S_REQUIRED_FUTURE_GATES = PHASE12R_REQUIRED_FUTURE_GATES
PHASE12S_REQUIRED_REVIEWER_CLASSES = PHASE12R_REQUIRED_REVIEWER_CLASSES
PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT = (
    "Phase 12S defines a metadata-only workflow-mode review chain closeout summary only; "
    "it creates no approval for runtime, active grant, runtime authorization, execution "
    "permission, workflow-mode activation, workflow execution, model routing, provider "
    "execution, model execution, model loading, training, fine-tuning, code execution, "
    "shell execution, process execution, experiment execution, autonomous experimentation, "
    "web access, network behavior, database ingestion, database writes, query execution, "
    "cache/event-bus/pub-sub runtime, transport implementation, fabric implementation, "
    "P2P implementation, clinical decision support, diagnosis, treatment planning, medical "
    "advice, dosing, nutrition prescription, device access, raw sensor processing, private "
    "health-data processing, deployment readiness, production readiness, or real-mode "
    "authorization."
)
PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT = (
    "Phase 12S cannot provide clinical decision support, diagnosis, treatment planning, "
    "medical advice, dosing, nutrition prescription, device access, raw sensor processing, "
    "or private health-data processing."
)

PHASE12A_SOURCE_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS = frozenset(
    {
        "artifact_kind",
        "contract_version",
        "phase_range",
        "final_status",
        "runtime_authorization_status",
        "readiness_gap",
        "missing_future_gate_count",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12C_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS = frozenset(
    {
        "record_kind",
        "contract_version",
        "record_id",
        "source_phase",
        "authorization_phase",
        "authorization_status",
        "decision_status",
        "grant_status",
        "record_candidate_status",
        "requested_domain_count",
        "required_future_reviewer_role_count",
        "required_future_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12C_CAPABILITY_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "capability_label",
        "capability_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12C_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "visual_supervision_capability_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase",
        "source_record_candidate",
        "supervision_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "phase12c_profiles_are_approvals_grants_or_permissions",
        "capability_labels",
        "capability_label_count",
        "jules_review_required_for_validator_or_authorization_semantics",
        "visual_capture_execution_granted",
        "clipboard_capture_execution_granted",
        "mic_capture_execution_granted",
        "camera_capture_execution_granted",
        "click_automation_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12D_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS = frozenset(
    {
        "artifact_kind",
        "contract_version",
        "charter_id",
        "source_phase_range",
        "authorization_phase",
        "authorization_status",
        "charter_status",
        "future_required_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12D_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS = PHASE12C_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS
PHASE12D_SOURCE_CAPABILITY_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "profile_kind",
        "contract_version",
        "profile_id",
        "source_phase",
        "supervision_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "capability_label_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12D_CAPABILITY_CATEGORY_REQUIRED_FIELDS = frozenset(
    {
        "capability_category",
        "category_status",
        "metadata_only",
        "consent_granted_by_phase12d",
        "authorization_granted_by_phase12d",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12D_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "gate_status",
        "required_before_visual_desktop_runtime",
        "satisfied_by_phase12d",
        "passed",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12D_CONSENT_GATE_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "consent_gate_profile_contract_version",
        "profile_kind",
        "consent_gate_profile_id",
        "source_phase_range",
        "source_design_charter",
        "source_record_candidate",
        "source_capability_profile",
        "consent_phase",
        "authorization_status",
        "grant_status",
        "consent_gate_status",
        "phase12d_satisfies_consent_gates",
        "phase12d_profiles_are_consents_approvals_grants_or_permissions",
        "capability_categories",
        "capability_category_count",
        "required_future_gates",
        "required_future_gate_count",
        "satisfied_consent_gate_count",
        "passed_consent_gate_count",
        "jules_review_required_for_validator_or_authorization_semantics",
        "screen_capture_execution_granted",
        "ocr_execution_granted",
        "camera_capture_execution_granted",
        "microphone_capture_execution_granted",
        "clipboard_capture_execution_granted",
        "recording_execution_granted",
        "click_input_automation_execution_granted",
        "overlay_display_execution_granted",
        "notification_sending_execution_granted",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS = PHASE12D_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS
PHASE12E_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS = PHASE12D_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS
PHASE12E_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "profile_kind",
        "contract_version",
        "consent_gate_profile_id",
        "source_phase_range",
        "consent_phase",
        "authorization_status",
        "grant_status",
        "consent_gate_status",
        "capability_category_count",
        "required_future_gate_count",
        "satisfied_consent_gate_count",
        "passed_consent_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARY_REQUIRED_FIELDS = frozenset(
    {
        "boundary_kind",
        "source_phase_range",
        "boundary_status",
        "boundary_labels",
        "boundary_label_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_SENSOR_CAPABILITY_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "sensor_capability_label",
        "capability_status",
        "metadata_only",
        "sensor_enabled_by_phase12e",
        "measurement_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_NON_DIAGNOSTIC_BOUNDARY_REQUIRED_FIELDS = frozenset(
    {
        "boundary_id",
        "boundary_status",
        "metadata_only",
        "satisfied_by_phase12e",
        "diagnosis_permitted",
        "clinical_recommendation_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "gate_status",
        "required_before_physiological_sensor_runtime",
        "satisfied_by_phase12e",
        "passed",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "physiological_sensor_profile_contract_version",
        "profile_kind",
        "physiological_sensor_profile_id",
        "source_phase_range",
        "source_design_charter",
        "source_record_candidate",
        "source_consent_gate_profile",
        "source_sensor_evidence_boundaries",
        "sensor_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "phase12e_profiles_are_approvals_grants_or_permissions",
        "phase12e_satisfies_sensor_gates",
        "sensor_capability_labels",
        "sensor_capability_label_count",
        "non_diagnostic_boundaries",
        "non_diagnostic_boundary_count",
        "required_future_gates",
        "required_future_gate_count",
        "satisfied_sensor_gate_count",
        "passed_sensor_gate_count",
        "jules_review_required_for_validator_or_authorization_semantics",
        "bia_measurement_execution_granted",
        "device_connection_execution_granted",
        "bluetooth_execution_granted",
        "usb_execution_granted",
        "cloud_sync_execution_granted",
        "acoustic_processing_execution_granted",
        "ultrasound_processing_execution_granted",
        "medical_inference_execution_granted",
        "clinical_recommendation_execution_granted",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12F_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS = PHASE12E_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS
PHASE12F_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS = PHASE12E_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS
PHASE12F_SOURCE_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS = (
    PHASE12D_SOURCE_CAPABILITY_PROFILE_REQUIRED_FIELDS
)
PHASE12F_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS = (
    PHASE12E_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS
)
PHASE12F_SOURCE_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "profile_kind",
        "contract_version",
        "physiological_sensor_profile_id",
        "source_phase_range",
        "sensor_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "sensor_capability_label_count",
        "non_diagnostic_boundary_count",
        "required_future_gate_count",
        "satisfied_sensor_gate_count",
        "passed_sensor_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12F_SOURCE_CONTENT_FABRIC_SECURE_DROP_CONTRACT_REQUIRED_FIELDS = frozenset(
    {
        "source_kind",
        "canonical_owner",
        "canonical_reference",
        "repository",
        "merge_commit_sha",
        "secure_drop_contract_version",
        "contract_status",
        "design_contract_only",
        "somatic_owns_secure_drop_implementation",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12F_ALLOWED_ARTIFACT_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "artifact_label",
        "artifact_status",
        "metadata_only",
        "explicit_user_action_required",
        "selected_by_phase12f",
        "send_permitted",
        "receive_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12F_PROHIBITED_SOURCE_REQUIRED_FIELDS = frozenset(
    {
        "source_label",
        "source_status",
        "metadata_only",
        "permitted_by_phase12f",
        "send_permitted",
        "receive_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS = frozenset(
    {
        "secure_drop_consumer_boundary_contract_version",
        "boundary_kind",
        "secure_drop_consumer_boundary_id",
        "source_phase_range",
        "source_design_charter",
        "source_record_candidate",
        "source_visual_supervision_profile",
        "source_consent_gate_profile",
        "source_physiological_sensor_profile",
        "source_content_fabric_secure_drop_contract",
        "consumer_phase",
        "canonical_owner",
        "canonical_reference",
        "authorization_status",
        "grant_status",
        "boundary_status",
        "phase12f_implements_secure_drop",
        "phase12f_authorizes_secure_drop",
        "phase12f_profiles_are_approvals_grants_or_permissions",
        "allowed_future_user_selected_artifact_labels",
        "allowed_future_user_selected_artifact_label_count",
        "prohibited_future_autonomous_sources",
        "prohibited_future_autonomous_source_count",
        "encryption_required",
        "encryption_requirement_status",
        "concealment_optional",
        "concealment_status",
        "concealment_is_security_boundary",
        "audit_metadata_only_required",
        "audit_requirement_status",
        "jules_security_review_required_for_validator_or_authorization_semantics",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "agent_invocation_permitted",
        "automation_invocation_permitted",
        "connector_invocation_permitted",
        "scheduled_task_invocation_permitted",
        "avatar_invocation_permitted",
        "server_endpoint_invocation_permitted",
        "workflow_invocation_permitted",
        "filesystem_autoscan_permitted",
        "vault_env_secret_access_permitted",
        "raw_sensor_capture_attachment_permitted",
        "automatic_document_attachment_permitted",
        "crypto_implementation_added",
        "transport_implementation_added",
        "stego_implementation_added",
        "keyring_implementation_added",
        "did_implementation_added",
        "send_inbox_ui_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12G_SOURCE_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS = frozenset(
    {
        "boundary_kind",
        "contract_version",
        "secure_drop_consumer_boundary_id",
        "source_phase_range",
        "consumer_phase",
        "canonical_owner",
        "authorization_status",
        "grant_status",
        "boundary_status",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12G_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "coverage_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12G_AREA_ENTRY_REQUIRED_FIELDS = frozenset(
    {
        "area_id",
        "area_label",
        "somatic_responsibility",
        "likely_repo_family_owner",
        "coverage_status",
        "current_coverage_summary",
        "remaining_gap_summary",
        "blocked_runtime_requirement",
        "review_requirement",
        "metadata_only",
        "phase12g_area_grants_runtime",
        "external_owner_entry_grants_runtime",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12G_PRODUCTION_READINESS_MATRIX_REQUIRED_FIELDS = frozenset(
    {
        "production_readiness_matrix_contract_version",
        "matrix_kind",
        "production_readiness_matrix_id",
        "source_phase_range",
        "source_secure_drop_consumer_boundary",
        "readiness_phase",
        "authorization_status",
        "grant_status",
        "matrix_status",
        "status_labels",
        "status_label_count",
        "production_readiness_areas",
        "production_readiness_area_count",
        "somatic_direct_area_count",
        "somatic_boundary_only_area_count",
        "external_owner_area_count",
        "not_applicable_yet_area_count",
        "phase12g_makes_somatic_production_ready",
        "phase12g_authorizes_runtime",
        "phase12g_coverage_labels_are_metadata_only",
        "jules_review_required_for_validator_or_authorization_semantics",
        "security_review_required_before_production_hardening",
        "frontend_implementation_added",
        "backend_service_added",
        "production_api_service_added",
        "database_storage_added",
        "auth_runtime_added",
        "rate_limiting_runtime_added",
        "cache_runtime_added",
        "cdn_runtime_added",
        "load_balancer_runtime_added",
        "logging_service_added",
        "secrets_backend_runtime_added",
        "service_registry_runtime_added",
        "deployment_code_added",
        "hosting_runtime_added",
        "cloud_compute_runtime_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "device_connection_execution_granted",
        "sensor_processing_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12H_SOURCE_MATRIX_REQUIRED_FIELDS = frozenset(
    {
        "matrix_kind",
        "contract_version",
        "production_readiness_matrix_id",
        "source_phase_range",
        "readiness_phase",
        "authorization_status",
        "grant_status",
        "matrix_status",
        "production_readiness_area_count",
        "phase12g_makes_somatic_production_ready",
        "phase12g_authorizes_runtime",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12H_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "entry_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12H_OPTIONAL_INTEGRATION_PEER_REQUIRED_FIELDS = frozenset(
    {
        "peer_label",
        "integration_role",
        "peer_status",
        "integration_summary",
        "optional_integration_metadata_only",
        "required_dependency_for_somatic",
        "replaces_somatic_standalone_path",
        "runtime_grant_created",
        "cross_repo_mutation_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12H_STANDALONE_OWNERSHIP_ENTRY_REQUIRED_FIELDS = frozenset(
    {
        "production_area_id",
        "entry_status",
        "somatic_standalone_responsibility",
        "current_somatic_coverage",
        "remaining_somatic_gap",
        "optional_integration_peers",
        "optional_integration_peer_count",
        "external_integration_optional",
        "external_integration_replaces_somatic_standalone_path",
        "runtime_blocked",
        "review_requirement",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12H_STANDALONE_OWNERSHIP_MATRIX_REQUIRED_FIELDS = frozenset(
    {
        "standalone_ownership_matrix_contract_version",
        "matrix_kind",
        "standalone_ownership_matrix_id",
        "source_phase",
        "source_production_readiness_coverage_matrix",
        "readiness_phase",
        "authorization_status",
        "grant_status",
        "matrix_status",
        "status_labels",
        "status_label_count",
        "standalone_ownership_entries",
        "standalone_ownership_entry_count",
        "optional_integration_peer_count",
        "somatic_standalone_area_count",
        "repo_production_ready_count",
        "phase12h_marks_somatic_production_ready",
        "phase12h_authorizes_runtime",
        "somatic_standalone_ownership_retained",
        "external_integrations_optional",
        "optional_peer_labels_are_integration_metadata_only",
        "external_repo_integration_replaces_somatic_standalone_path",
        "cross_repo_mutation_permitted",
        "external_repo_tasks_executed_by_somatic",
        "standalone_ui_statement",
        "locus_optional_ui_statement",
        "peer_integration_statement",
        "secure_drop_statement",
        "phase12h_non_authorization_statement",
        "jules_review_required_for_validator_or_authorization_semantics",
        "security_review_required_before_production_hardening",
        "frontend_implementation_added",
        "backend_service_added",
        "production_api_service_added",
        "database_storage_added",
        "auth_runtime_added",
        "rate_limiting_runtime_added",
        "cache_runtime_added",
        "cdn_runtime_added",
        "load_balancer_runtime_added",
        "logging_service_added",
        "secrets_backend_runtime_added",
        "service_registry_runtime_added",
        "service_discovery_runtime_added",
        "deployment_code_added",
        "hosting_runtime_added",
        "cloud_compute_runtime_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "device_connection_execution_granted",
        "sensor_processing_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_USER_PREFERENCE_MODE_REQUIRED_FIELDS = frozenset(
    {
        "preference_mode_label",
        "label_status",
        "metadata_only",
        "safety_warnings_preserved",
        "emergency_escalation_preserved",
        "preference_cannot_suppress_warnings",
        "medical_advice_provided",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_SPECIALIST_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "specialist_profile_label",
        "profile_status",
        "metadata_only",
        "review_profile_only",
        "provider_execution_granted",
        "model_execution_granted",
        "clinical_recommendation_added",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_SOURCE_CLASS_REQUIRED_FIELDS = frozenset(
    {
        "source_class_label",
        "source_class_status",
        "metadata_only",
        "provenance_review_required",
        "ingestion_permitted",
        "web_scraping_permitted",
        "database_ingestion_permitted",
        "network_call_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12I_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "integrative_herbal_nutrition_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "capability_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "status_labels",
        "status_label_count",
        "user_preference_modes",
        "user_preference_mode_count",
        "specialist_profile_labels",
        "specialist_profile_label_count",
        "source_class_labels",
        "source_class_label_count",
        "required_future_gates",
        "required_future_gate_count",
        "medical_boundary_statement",
        "western_medicine_boundary_statement",
        "natural_remedy_boundary_statement",
        "food_cure_boundary_statement",
        "safety_warning_preservation_statement",
        "metadata_only",
        "non_authorizing_proof",
        "medical_safety_review_required",
        "jules_human_review_required_for_validator_or_medical_safety_semantics",
        "phase12i_provides_medical_advice",
        "phase12i_authorizes_runtime",
        "phase12i_suppresses_safety_warnings",
        "phase12i_claims_western_medicine_invalid",
        "phase12i_claims_natural_remedies_safe_by_default",
        "phase12i_claims_food_cures_disease",
        "emergency_escalation_preserved",
        "contraindication_warnings_preserved",
        "medication_interaction_warnings_preserved",
        "pregnancy_liver_kidney_cardiac_risk_warnings_preserved",
        "eating_disorder_risk_warnings_preserved",
        "toxicity_warnings_preserved",
        "contamination_adulteration_warnings_preserved",
        "medical_advice_provided",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "prescribing_added",
        "supplement_recommendation_added",
        "herb_dosing_added",
        "supplement_dosing_added",
        "calorie_macro_prescription_added",
        "weight_loss_target_prescription_added",
        "unsafe_fasting_weight_loss_advice_added",
        "nutrition_prescription_added",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "runtime_adapter_execution_granted",
        "real_mode_authorization_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12K_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12K_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12K_BACKEND_OPTION_REQUIRED_FIELDS = frozenset(
    {
        "backend_option_label",
        "backend_option_status",
        "credential_policy",
        "metadata_only",
        "human_approval_required",
        "cost_guard_required",
        "private_health_data_allowed",
        "api_call_execution_granted",
        "sdk_execution_granted",
        "simulator_execution_granted",
        "provider_execution_granted",
        "network_call_execution_granted",
        "spending_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12K_WORKLOAD_CLASS_REQUIRED_FIELDS = frozenset(
    {
        "workload_class_label",
        "workload_class_status",
        "metadata_only",
        "private_health_data_allowed",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "medical_advice_provided",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12K_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "human_approval_required",
        "cost_guard_required",
        "satisfied",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12K_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "external_compute_quantum_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "capability_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "credential_policy",
        "human_approval_required",
        "cost_guard_required",
        "private_health_data_allowed",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "status_labels",
        "status_label_count",
        "backend_options",
        "backend_option_count",
        "workload_classes",
        "workload_class_count",
        "required_future_gates",
        "required_future_gate_count",
        "compute_boundary_statement",
        "medical_boundary_statement",
        "metadata_only",
        "non_authorizing_proof",
        "security_review_required",
        "medical_safety_review_required",
        "jules_human_review_required_for_validator_or_medical_safety_semantics",
        "phase12k_authorizes_runtime",
        "phase12k_allows_external_compute_execution",
        "phase12k_allows_quantum_backend_execution",
        "phase12k_allows_private_health_data_processing",
        "phase12k_provides_medical_advice",
        "phase12k_allows_diagnosis_or_treatment",
        "api_call_execution_granted",
        "sdk_execution_granted",
        "simulator_execution_granted",
        "provider_call_execution_granted",
        "network_call_execution_granted",
        "spending_permitted",
        "credential_loading_added",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "external_compute_execution_granted",
        "quantum_backend_execution_granted",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "private_health_data_processing_added",
        "database_ingestion_added",
        "web_scraping_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12L_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12L_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12L_FABRIC_CAPABILITY_REQUIRED_FIELDS = frozenset(
    {
        "fabric_capability_label",
        "capability_status",
        "metadata_only",
        "future_requirement_only",
        "implementation_added",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12L_FORBIDDEN_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "forbidden_label",
        "forbidden_status",
        "metadata_only",
        "out_of_scope",
        "allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12L_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12L_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "fabric_interop_a2a_audit_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "capability_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "fabric_interop_status",
        "message_codec_status",
        "a2a_transport_status",
        "mcp_interop_status",
        "secure_drop_status",
        "credential_policy",
        "opaque_traffic_allowed",
        "untrusted_content_executable",
        "cross_repo_mutation_allowed",
        "status_labels",
        "status_label_count",
        "fabric_capability_labels",
        "fabric_capability_label_count",
        "forbidden_out_of_scope_labels",
        "forbidden_out_of_scope_label_count",
        "required_future_gates",
        "required_future_gate_count",
        "fabric_boundary_statement",
        "audit_boundary_statement",
        "secure_drop_boundary_statement",
        "metadata_only",
        "non_authorizing_proof",
        "security_review_required",
        "fabric_safety_review_required",
        "jules_human_review_required_for_validator_or_fabric_safety_semantics",
        "plaintext_json_default_future_requirement_only",
        "decode_to_audit_future_requirement_only",
        "secure_drop_user_initiated_boundary_only",
        "phase12l_authorizes_runtime",
        "phase12l_allows_fabric_runtime",
        "phase12l_allows_a2a_transport",
        "phase12l_allows_mcp_runtime",
        "phase12l_allows_secure_drop_send_receive",
        "message_codec_implementation_added",
        "a2a_transport_implementation_added",
        "mcp_server_implementation_added",
        "mcp_client_implementation_added",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "crypto_implementation_added",
        "credential_loading_added",
        "vault_env_access_granted",
        "secrets_access_granted",
        "network_call_execution_granted",
        "filesystem_autoscan_added",
        "connector_installation_added",
        "pack_registration_added",
        "provider_execution_granted",
        "provider_call_execution_granted",
        "model_execution_granted",
        "runtime_model_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "agent_invoked_secure_drop_allowed",
        "automation_invoked_secure_drop_allowed",
        "bundled_agpl_codec_allowed",
        "glossopetrae_vendoring_allowed",
        "st3gg_vendoring_allowed",
        "covert_channel_allowed",
        "opaque_message_acting_allowed",
        "untrusted_content_execution_added",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12M_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12M_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12M_MODEL_OPTION_CATEGORY_REQUIRED_FIELDS = frozenset(
    {
        "model_option_category_label",
        "category_status",
        "selectable_metadata_only",
        "metadata_only",
        "future_option_only",
        "model_loading_added",
        "model_execution_permitted",
        "provider_execution_permitted",
        "training_permitted",
        "fine_tuning_permitted",
        "private_health_data_allowed",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "device_access_allowed",
        "raw_sensor_processing_allowed",
        "monitoring_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12M_CANDIDATE_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "candidate_label",
        "candidate_status",
        "selectable_metadata_only",
        "metadata_only",
        "future_option_only",
        "model_loading_added",
        "model_execution_permitted",
        "provider_execution_permitted",
        "training_permitted",
        "fine_tuning_permitted",
        "private_health_data_allowed",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "prescribing_allowed",
        "medical_advice_allowed",
        "device_access_allowed",
        "raw_sensor_processing_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12M_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12M_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "specialized_model_option_registry_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "model_option_profile_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "status_labels",
        "status_label_count",
        "model_option_categories",
        "model_option_category_count",
        "candidate_labels",
        "candidate_label_count",
        "required_future_gates",
        "required_future_gate_count",
        "model_boundary_statement",
        "medical_boundary_statement",
        "sensor_boundary_statement",
        "metadata_only",
        "non_authorizing_proof",
        "security_review_required",
        "medical_safety_review_required",
        "jules_human_review_required_for_validator_or_model_safety_semantics",
        "model_labels_selectable_metadata_only",
        "phase12m_authorizes_runtime",
        "phase12m_allows_model_execution",
        "phase12m_allows_provider_execution",
        "phase12m_allows_model_loading",
        "phase12m_allows_training",
        "phase12m_allows_fine_tuning",
        "phase12m_allows_clinical_decision_support",
        "phase12m_allows_diagnosis_or_treatment",
        "phase12m_allows_private_health_data_processing",
        "phase12m_allows_device_access",
        "phase12m_allows_raw_sensor_processing",
        "phase12m_provides_medical_advice",
        "phase12m_provides_prescribing",
        "model_execution_permitted",
        "provider_execution_permitted",
        "training_permitted",
        "fine_tuning_permitted",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "private_health_data_allowed",
        "model_loading_added",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "prescribing_added",
        "herb_dosing_added",
        "supplement_dosing_added",
        "calorie_macro_prescription_added",
        "nutrition_prescription_added",
        "private_health_data_processing_added",
        "device_access_granted",
        "device_connection_execution_granted",
        "raw_sensor_processing_added",
        "sensor_processing_execution_granted",
        "monitoring_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12N_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_WORKFLOW_MODE_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_label",
        "mode_status",
        "mode_definition",
        "metadata_only",
        "future_mode_only",
        "workflow_mode_execution_permitted",
        "runtime_orchestration_added",
        "model_routing_execution_permitted",
        "autonomous_experimentation_permitted",
        "code_execution_permitted",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "private_health_data_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_FUSION_CONCEPT_REQUIRED_FIELDS = frozenset(
    {
        "fusion_concept_label",
        "concept_status",
        "metadata_only",
        "future_concept_only",
        "model_routing_execution_permitted",
        "provider_call_execution_granted",
        "model_loading_added",
        "learned_coordination_execution_granted",
        "agent_routing_execution_granted",
        "network_call_execution_granted",
        "runtime_orchestration_added",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_REQUIRED_FIELDS = frozenset(
    {
        "scientist_evolution_concept_label",
        "concept_status",
        "metadata_only",
        "future_concept_only",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "web_access_permitted",
        "literature_search_execution_permitted",
        "database_ingestion_added",
        "manuscript_generation_added",
        "autonomous_publication_allowed",
        "model_training_execution_granted",
        "model_fine_tuning_execution_granted",
        "autonomous_research_action_permitted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12N_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "workflow_orchestration_mode_registry_profile_contract_version",
        "profile_kind",
        "profile_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "workflow_mode_profile_phase",
        "authorization_status",
        "grant_status",
        "profile_status",
        "status_labels",
        "status_label_count",
        "workflow_modes",
        "workflow_mode_count",
        "fusion_concepts",
        "fusion_concept_count",
        "scientist_evolution_concepts",
        "scientist_evolution_concept_count",
        "required_future_gates",
        "required_future_gate_count",
        "workflow_boundary_statement",
        "fusion_boundary_statement",
        "scientist_boundary_statement",
        "medical_sensor_boundary_statement",
        "metadata_only",
        "non_authorizing_proof",
        "security_review_required",
        "medical_safety_review_required",
        "jules_human_review_required_for_validator_or_workflow_safety_semantics",
        "workflow_modes_metadata_only",
        "phase12n_authorizes_runtime",
        "phase12n_allows_workflow_mode_execution",
        "phase12n_allows_runtime_orchestration",
        "phase12n_allows_model_routing",
        "phase12n_allows_provider_execution",
        "phase12n_allows_model_execution",
        "phase12n_allows_model_loading",
        "phase12n_allows_training",
        "phase12n_allows_fine_tuning",
        "phase12n_allows_code_execution",
        "phase12n_allows_experiment_execution",
        "phase12n_allows_autonomous_experimentation",
        "phase12n_allows_web_access",
        "phase12n_allows_autonomous_publication",
        "phase12n_allows_clinical_decision_support",
        "phase12n_allows_diagnosis_or_treatment",
        "phase12n_allows_private_health_data_processing",
        "phase12n_allows_device_or_sensor_access",
        "phase12n_provides_medical_advice",
        "workflow_mode_execution_permitted",
        "autonomous_experimentation_permitted",
        "code_execution_permitted",
        "model_routing_execution_permitted",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "private_health_data_allowed",
        "runtime_orchestration_added",
        "fusion_coordination_execution_granted",
        "learned_coordination_execution_granted",
        "agent_routing_execution_granted",
        "provider_call_execution_granted",
        "provider_execution_granted",
        "model_loading_added",
        "runtime_model_execution_granted",
        "model_execution_granted",
        "training_permitted",
        "fine_tuning_permitted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "model_training_execution_granted",
        "model_fine_tuning_execution_granted",
        "experiment_execution_permitted",
        "experiment_execution_granted",
        "web_access_permitted",
        "literature_search_execution_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "device_access_granted",
        "device_connection_execution_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "sensor_processing_execution_granted",
        "private_health_data_processing_added",
        "manuscript_generation_added",
        "autonomous_publication_allowed",
        "autonomous_research_action_permitted",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12O_SOURCE_PROFILE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12O_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12O_WORKFLOW_MODE_MATRIX_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_label",
        "matrix_entry_status",
        "source_phase12n_mode_label",
        "metadata_only",
        "standalone_first",
        "runtime_prerequisite_only",
        "required_future_gate_labels",
        "required_future_gate_count",
        "all_prerequisites_satisfied",
        "runtime_blocked",
        "review_required",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "model_routing_execution_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "clinical_decision_support_allowed",
        "private_health_data_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12O_MODE_GATE_REQUIREMENT_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_label",
        "future_gate_label",
        "gate_status",
        "gate_scope",
        "metadata_only",
        "satisfied",
        "passed",
        "runtime_prerequisite_satisfied",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12O_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "gate_scope",
        "metadata_only",
        "satisfied",
        "passed",
        "runtime_prerequisite_satisfied",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12O_MATRIX_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_safety_gate_matrix_contract_version",
        "matrix_kind",
        "matrix_id",
        "source_phase",
        "source_phase12n_profile",
        "matrix_phase",
        "authorization_status",
        "grant_status",
        "matrix_status",
        "status_labels",
        "status_label_count",
        "workflow_mode_prerequisite_matrix",
        "workflow_mode_prerequisite_count",
        "required_future_gates",
        "required_future_gate_count",
        "mode_gate_requirements",
        "mode_gate_requirement_count",
        "matrix_boundary_statement",
        "medical_privacy_boundary_statement",
        "standalone_first_statement",
        "metadata_only",
        "non_authorizing_proof",
        "standalone_first",
        "security_review_required",
        "medical_safety_review_required",
        "jules_human_review_required_for_validator_or_workflow_safety_semantics",
        "workflow_mode_safety_gates_metadata_only",
        "phase12o_authorizes_runtime",
        "phase12o_satisfies_runtime_prerequisites",
        "phase12o_allows_workflow_execution",
        "phase12o_allows_workflow_mode_execution",
        "phase12o_allows_runtime_adapter",
        "phase12o_allows_model_routing",
        "phase12o_allows_provider_execution",
        "phase12o_allows_model_execution",
        "phase12o_allows_code_execution",
        "phase12o_allows_experiment_execution",
        "phase12o_allows_web_database_network_behavior",
        "phase12o_allows_clinical_decision_support",
        "phase12o_allows_private_health_data_processing",
        "phase12o_active_grant_present",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "runtime_prerequisite_satisfied",
        "all_prerequisites_satisfied",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "active_grant_present",
        "real_mode_authorization_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "device_access_granted",
        "raw_sensor_processing_added",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12P_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_PREREQUISITE_MATRIX_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "required_future_gate_labels",
        "required_future_gate_count",
        "workflow_mode_prerequisite_count",
        "runtime_prerequisites_satisfied",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_MODE_REVIEW_PACKET_REQUIRED_FIELDS = frozenset(
    {
        "requested_workflow_mode_label",
        "packet_entry_status",
        "requested_transition_status",
        "prerequisite_matrix_reference_id",
        "required_future_gate_labels",
        "required_future_gate_count",
        "required_reviewer_class_labels",
        "required_reviewer_class_count",
        "risk_summary_placeholder_labels",
        "evidence_inventory_placeholder_labels",
        "denial_blocked_default_fail_closed_status",
        "metadata_only",
        "review_packet_boundary_only",
        "standalone_first",
        "not_authorized",
        "no_active_grant",
        "no_runtime_authorization",
        "no_execution_permission",
        "workflow_mode_activation_not_permitted",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "clinical_decision_support_allowed",
        "private_health_data_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "review_completed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_REVIEWER_CLASS_REQUIRED_FIELDS = frozenset(
    {
        "reviewer_class_label",
        "reviewer_class_status",
        "required",
        "completed",
        "approved",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_RISK_SUMMARY_PLACEHOLDER_REQUIRED_FIELDS = frozenset(
    {
        "risk_summary_placeholder_label",
        "placeholder_status",
        "required",
        "filled",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDER_REQUIRED_FIELDS = frozenset(
    {
        "evidence_inventory_placeholder_label",
        "placeholder_status",
        "required",
        "filled",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12P_REVIEW_PACKET_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_activation_request_review_packet_contract_version",
        "packet_kind",
        "activation_request_packet_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "prerequisite_matrix_reference",
        "packet_phase",
        "authorization_status",
        "grant_status",
        "requested_transition_status",
        "packet_status",
        "status_labels",
        "status_label_count",
        "workflow_mode_review_packets",
        "workflow_mode_review_packet_count",
        "required_future_gates",
        "required_future_gate_count",
        "required_reviewer_classes",
        "required_reviewer_class_count",
        "risk_summary_placeholders",
        "risk_summary_placeholder_count",
        "evidence_inventory_placeholders",
        "evidence_inventory_placeholder_count",
        "packet_boundary_statement",
        "review_requirement_statement",
        "medical_privacy_boundary_statement",
        "metadata_only",
        "review_packet_boundary_only",
        "standalone_first",
        "non_authorizing_proof",
        "not_authorized",
        "human_review_required",
        "jules_review_required",
        "security_review_required",
        "medical_safety_review_required",
        "human_jules_security_medical_safety_review_required",
        "all_future_gates_unsatisfied",
        "denial_blocked_default_fail_closed",
        "denial_blocked_default_fail_closed_status",
        "no_active_grant",
        "no_runtime_authorization",
        "no_execution_permission",
        "workflow_mode_activation_not_permitted",
        "workflow_mode_activation_not_permitted_status",
        "phase12p_authorizes_runtime",
        "phase12p_creates_active_grant",
        "phase12p_grants_execution_permission",
        "phase12p_allows_workflow_execution",
        "phase12p_allows_workflow_mode_execution",
        "phase12p_allows_runtime_adapter",
        "phase12p_allows_model_routing",
        "phase12p_allows_provider_execution",
        "phase12p_allows_model_execution",
        "phase12p_allows_model_loading",
        "phase12p_allows_training",
        "phase12p_allows_fine_tuning",
        "phase12p_allows_code_execution",
        "phase12p_allows_experiment_execution",
        "phase12p_allows_autonomous_experimentation",
        "phase12p_allows_web_access",
        "phase12p_allows_database_ingestion",
        "phase12p_allows_web_scraping",
        "phase12p_allows_network_calls",
        "phase12p_allows_clinical_decision_support",
        "phase12p_allows_diagnosis_or_treatment",
        "phase12p_allows_medical_advice",
        "phase12p_allows_dosing_or_nutrition_prescription",
        "phase12p_allows_private_health_data_processing",
        "phase12p_allows_device_or_sensor_access",
        "phase12p_allows_raw_sensor_processing",
        "phase12p_marks_production_ready",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12Q_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12Q_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12Q_FUTURE_GATE_SNAPSHOT_REQUIRED_FIELDS = frozenset(
    {
        "future_gate_label",
        "gate_status",
        "metadata_only",
        "satisfied",
        "passed",
        "review_completed",
        "blocks_runtime_authorization",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12Q_REVIEWER_CLASS_REQUIRED_FIELDS = frozenset(
    {
        "reviewer_class_label",
        "reviewer_class_status",
        "required",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12Q_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS = frozenset(
    {
        "reviewer_class_label",
        "reviewer_class_status",
        "represented",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12Q_DECISION_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_review_decision_record_contract_version",
        "decision_record_kind",
        "decision_record_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "source_activation_request_packet_id",
        "requested_workflow_mode_label",
        "decision_record_phase",
        "authorization_status",
        "grant_status",
        "decision_record_status",
        "status_labels",
        "status_label_count",
        "decision_status",
        "decision_reason_code",
        "decision_summary",
        "request_disposition_status",
        "required_future_gates_snapshot",
        "required_future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
        "reviewer_classes_required",
        "reviewer_class_required_count",
        "reviewer_classes_represented",
        "reviewer_class_represented_count",
        "decision_boundary_statement",
        "medical_privacy_boundary_statement",
        "metadata_only",
        "review_decision_record_only",
        "standalone_first",
        "non_authorizing_proof",
        "not_authorized",
        "request_review_not_submitted",
        "request_review_blocked",
        "request_returned_for_fix_only_changes",
        "request_denied_no_runtime_authorization",
        "request_expired_no_runtime_authorization",
        "request_review_complete_no_runtime_authorization",
        "no_active_grant",
        "no_runtime_authorization",
        "no_execution_permission",
        "runtime_authorization_not_granted",
        "workflow_mode_activation_not_permitted",
        "workflow_mode_activation_not_permitted_status",
        "phase12q_authorizes_runtime",
        "phase12q_creates_active_grant",
        "phase12q_grants_execution_permission",
        "phase12q_allows_workflow_activation",
        "phase12q_allows_workflow_execution",
        "phase12q_allows_workflow_mode_execution",
        "phase12q_allows_runtime_adapter",
        "phase12q_allows_model_routing",
        "phase12q_allows_provider_execution",
        "phase12q_allows_model_execution",
        "phase12q_allows_model_loading",
        "phase12q_allows_training",
        "phase12q_allows_fine_tuning",
        "phase12q_allows_code_execution",
        "phase12q_allows_experiment_execution",
        "phase12q_allows_autonomous_experimentation",
        "phase12q_allows_web_access",
        "phase12q_allows_database_ingestion",
        "phase12q_allows_web_scraping",
        "phase12q_allows_network_calls",
        "phase12q_allows_clinical_decision_support",
        "phase12q_allows_diagnosis_or_treatment",
        "phase12q_allows_medical_advice",
        "phase12q_allows_dosing_or_nutrition_prescription",
        "phase12q_allows_private_health_data_processing",
        "phase12q_allows_device_or_sensor_access",
        "phase12q_allows_raw_sensor_processing",
        "phase12q_marks_production_ready",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12R_SOURCE_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "source_reference_id",
        "reference_status",
        "metadata_only",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_STATUS_LABEL_REQUIRED_FIELDS = frozenset(
    {
        "status_label",
        "label_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_INDEXED_WORKFLOW_MODE_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_label",
        "mode_index_status",
        "metadata_only",
        "indexed_for_audit_only",
        "required_future_gate_count",
        "unsatisfied_gate_count",
        "workflow_mode_activation_not_permitted",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "clinical_decision_support_allowed",
        "private_health_data_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_PACKET_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "activation_request_packet_id",
        "reference_status",
        "requested_workflow_mode_label",
        "metadata_only",
        "workflow_mode_activation_not_permitted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_DECISION_RECORD_REFERENCE_REQUIRED_FIELDS = frozenset(
    {
        "source_phase_label",
        "source_kind",
        "decision_record_id",
        "reference_status",
        "decision_status",
        "decision_reason_code",
        "request_disposition_status",
        "metadata_only",
        "runtime_authorization_not_granted",
        "workflow_mode_activation_not_permitted",
        "no_active_grant",
        "no_execution_permission",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_DECISION_STATUS_SUMMARY_REQUIRED_FIELDS = frozenset(
    {
        "decision_status",
        "decision_reason_code",
        "request_disposition_status",
        "decision_status_summary_status",
        "request_review_not_submitted",
        "request_review_blocked",
        "request_returned_for_fix_only_changes",
        "request_denied_no_runtime_authorization",
        "request_expired_no_runtime_authorization",
        "request_review_complete_no_runtime_authorization",
        "metadata_only",
        "runtime_authorization_not_granted",
        "workflow_mode_activation_not_permitted",
        "no_execution_permission",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12R_REVIEWER_CLASS_REQUIRED_FIELDS = PHASE12Q_REVIEWER_CLASS_REQUIRED_FIELDS
PHASE12R_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS = (
    PHASE12Q_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS
)
PHASE12R_AUDIT_TRAIL_INDEX_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_review_audit_trail_index_contract_version",
        "audit_trail_index_kind",
        "audit_trail_index_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "audit_trail_index_phase",
        "authorization_status",
        "grant_status",
        "audit_trail_index_status",
        "status_labels",
        "status_label_count",
        "indexed_workflow_modes",
        "indexed_workflow_mode_count",
        "activation_request_packet_reference_metadata",
        "review_decision_record_reference_metadata",
        "decision_status_summary",
        "decision_status",
        "decision_reason_code",
        "request_disposition_status",
        "required_future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
        "stale_count",
        "review_needed_count",
        "stale_status",
        "review_needed_status",
        "stale_review_needed_status",
        "reviewer_classes_required",
        "reviewer_class_required_count",
        "reviewer_classes_represented",
        "reviewer_class_represented_count",
        "audit_trail_boundary_statement",
        "medical_privacy_boundary_statement",
        "metadata_only",
        "workflow_mode_review_audit_trail_index_only",
        "standalone_first",
        "non_authorizing_proof",
        "not_authorized",
        "no_active_grant",
        "no_runtime_authorization",
        "no_execution_permission",
        "runtime_authorization_not_granted",
        "workflow_mode_activation_not_permitted",
        "phase12r_authorizes_runtime",
        "phase12r_creates_active_grant",
        "phase12r_grants_execution_permission",
        "phase12r_allows_workflow_activation",
        "phase12r_allows_workflow_execution",
        "phase12r_allows_workflow_mode_execution",
        "phase12r_allows_runtime_adapter",
        "phase12r_allows_model_routing",
        "phase12r_allows_provider_execution",
        "phase12r_allows_model_execution",
        "phase12r_allows_model_loading",
        "phase12r_allows_training",
        "phase12r_allows_fine_tuning",
        "phase12r_allows_code_execution",
        "phase12r_allows_experiment_execution",
        "phase12r_allows_autonomous_experimentation",
        "phase12r_allows_shell_execution",
        "phase12r_allows_process_execution",
        "phase12r_allows_cache_event_bus_pubsub_runtime",
        "phase12r_allows_web_access",
        "phase12r_allows_database_ingestion",
        "phase12r_allows_database_writes",
        "phase12r_allows_query_execution",
        "phase12r_allows_web_scraping",
        "phase12r_allows_network_calls",
        "phase12r_allows_clinical_decision_support",
        "phase12r_allows_diagnosis_or_treatment",
        "phase12r_allows_medical_advice",
        "phase12r_allows_dosing_or_nutrition_prescription",
        "phase12r_allows_private_health_data_processing",
        "phase12r_allows_device_or_sensor_access",
        "phase12r_allows_raw_sensor_processing",
        "phase12r_marks_production_ready",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "shell_execution_permitted",
        "process_execution_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "database_write_permitted",
        "query_execution_permitted",
        "cache_event_bus_runtime_added",
        "pubsub_runtime_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12S_SOURCE_REFERENCE_REQUIRED_FIELDS = PHASE12R_SOURCE_REFERENCE_REQUIRED_FIELDS
PHASE12S_STATUS_LABEL_REQUIRED_FIELDS = PHASE12R_STATUS_LABEL_REQUIRED_FIELDS
PHASE12S_WORKFLOW_MODE_COVERAGE_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_label",
        "mode_coverage_status",
        "metadata_only",
        "covered_for_closeout_only",
        "workflow_mode_activation_not_permitted",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "code_execution_permitted",
        "shell_execution_permitted",
        "process_execution_permitted",
        "experiment_execution_permitted",
        "clinical_decision_support_allowed",
        "private_health_data_allowed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12S_CLOSEOUT_SUMMARY_REQUIRED_FIELDS = frozenset(
    {
        "workflow_mode_review_chain_closeout_summary_contract_version",
        "closeout_summary_kind",
        "closeout_summary_id",
        "source_phase_range",
        "source_phase_references",
        "source_phase_reference_count",
        "closeout_summary_phase",
        "authorization_status",
        "grant_status",
        "summary_status",
        "status_labels",
        "status_label_count",
        "workflow_mode_labels_covered",
        "workflow_mode_label_count",
        "future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
        "review_chain_status",
        "closeout_status",
        "reviewer_navigation_summary",
        "operator_handoff_summary",
        "closeout_boundary_statement",
        "medical_privacy_boundary_statement",
        "metadata_only",
        "workflow_mode_review_chain_closeout_summary_only",
        "standalone_first",
        "non_authorizing_proof",
        "not_authorized",
        "no_active_grant",
        "no_runtime_authorization",
        "no_execution_permission",
        "runtime_authorization_not_granted",
        "workflow_mode_activation_not_permitted",
        "phase12s_authorizes_runtime",
        "phase12s_creates_active_grant",
        "phase12s_grants_execution_permission",
        "phase12s_allows_workflow_activation",
        "phase12s_allows_workflow_execution",
        "phase12s_allows_workflow_mode_execution",
        "phase12s_allows_runtime_adapter",
        "phase12s_allows_model_routing",
        "phase12s_allows_provider_execution",
        "phase12s_allows_model_execution",
        "phase12s_allows_model_loading",
        "phase12s_allows_training",
        "phase12s_allows_fine_tuning",
        "phase12s_allows_code_execution",
        "phase12s_allows_shell_execution",
        "phase12s_allows_process_execution",
        "phase12s_allows_experiment_execution",
        "phase12s_allows_autonomous_experimentation",
        "phase12s_allows_web_access",
        "phase12s_allows_network_behavior",
        "phase12s_allows_database_ingestion",
        "phase12s_allows_database_writes",
        "phase12s_allows_query_execution",
        "phase12s_allows_cache_event_bus_pubsub_runtime",
        "phase12s_allows_transport_implementation",
        "phase12s_allows_fabric_implementation",
        "phase12s_allows_p2p_implementation",
        "phase12s_allows_clinical_decision_support",
        "phase12s_allows_diagnosis_or_treatment",
        "phase12s_allows_medical_advice",
        "phase12s_allows_dosing_or_nutrition_prescription",
        "phase12s_allows_private_health_data_processing",
        "phase12s_allows_device_or_sensor_access",
        "phase12s_allows_raw_sensor_processing",
        "phase12s_marks_deployment_ready",
        "phase12s_marks_production_ready",
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "shell_execution_permitted",
        "process_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "network_behavior_added",
        "database_ingestion_added",
        "database_write_permitted",
        "query_execution_permitted",
        "cache_event_bus_runtime_added",
        "pubsub_runtime_added",
        "transport_implementation_added",
        "fabric_implementation_added",
        "p2p_implementation_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "deployment_ready",
        "production_ready",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12B_SOURCE_CHARTER_REQUIRED_FIELDS = frozenset(
    {
        "artifact_kind",
        "contract_version",
        "charter_id",
        "source_phase_range",
        "authorization_phase",
        "authorization_status",
        "charter_status",
        "future_required_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12B_REQUESTED_DOMAIN_REQUIRED_FIELDS = frozenset(
    {
        "domain_label",
        "request_status",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12B_REVIEWER_ROLE_REQUIRED_FIELDS = frozenset(
    {
        "reviewer_role",
        "review_status",
        "metadata_only",
        "satisfied_by_phase12b",
        "passed",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12B_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "reviewer_role",
        "gate_status",
        "required_before_runtime_authorization",
        "submitted_by_phase12b",
        "satisfied_by_phase12b",
        "passed",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12B_RUNTIME_AUTHORIZATION_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "runtime_authorization_record_candidate_contract_version",
        "record_kind",
        "record_id",
        "source_phase",
        "source_design_charter",
        "authorization_phase",
        "authorization_status",
        "decision_status",
        "grant_status",
        "record_candidate_status",
        "phase12b_records_are_approvals_grants_or_permissions",
        "requested_domains",
        "requested_domain_count",
        "required_future_reviewer_roles",
        "required_future_reviewer_role_count",
        "required_future_gates",
        "required_future_gate_count",
        "submitted_future_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
        "jules_review_required_for_validator_or_authorization_semantics",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)

PHASE12A_SOURCE_RUNTIME_GAP_LEDGER_REQUIRED_FIELDS = frozenset(
    {
        "artifact_kind",
        "contract_version",
        "source_phase_range",
        "authorization_status",
        "readiness_gap",
        "missing_future_gate_count",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12A_FUTURE_GATE_REQUIRED_FIELDS = frozenset(
    {
        "gate_id",
        "gate_status",
        "required_before_runtime_authorization",
        "satisfied_by_phase12a",
        "passed",
        "metadata_only",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)
PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_REQUIRED_FIELDS = frozenset(
    {
        "runtime_authorization_design_charter_contract_version",
        "charter_kind",
        "charter_id",
        "source_phase_range",
        "source_governance_closeout",
        "source_runtime_gap_ledger",
        "authorization_phase",
        "authorization_status",
        "charter_scope",
        "charter_status",
        "phase12a_satisfies_future_gates",
        "future_required_gates",
        "future_required_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
        "jules_review_required_for_validator_or_authorization_semantics",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "runtime_stage",
        "execution_permitted",
        "real_mode_runtime_enabled",
    }
)


@dataclass(frozen=True)
class Phase12ARuntimeAuthorizationDesignCharterValidationResult:
    """Sanitized validation result for Phase 12A design-only charters."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    design_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12A_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "design_only": self.design_only,
            "metadata_only": self.metadata_only,
            "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
            "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12CVisualSupervisionCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12C capability profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    capability_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12C_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "capability_profile_only": self.capability_profile_only,
            "metadata_only": self.metadata_only,
            "supervision_phase": PHASE12C_SUPERVISION_PHASE,
            "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
            "grant_status": PHASE12C_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12DConsentGateRequirementsValidationResult:
    """Sanitized validation result for Phase 12D consent gate requirements."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    consent_gate_requirements_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12D_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "consent_gate_requirements_only": self.consent_gate_requirements_only,
            "metadata_only": self.metadata_only,
            "consent_phase": PHASE12D_CONSENT_PHASE,
            "authorization_status": PHASE12D_AUTHORIZATION_STATUS,
            "grant_status": PHASE12D_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12EPhysiologicalSensorCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12E physiological sensor profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    physiological_sensor_capability_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12E_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "physiological_sensor_capability_profile_only": (
                self.physiological_sensor_capability_profile_only
            ),
            "metadata_only": self.metadata_only,
            "sensor_phase": PHASE12E_SENSOR_PHASE,
            "authorization_status": PHASE12E_AUTHORIZATION_STATUS,
            "grant_status": PHASE12E_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12FSecureDropConsumerBoundaryValidationResult:
    """Sanitized validation result for Phase 12F Secure Drop consumer boundaries."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    secure_drop_consumer_boundary_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12F_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "secure_drop_consumer_boundary_only": self.secure_drop_consumer_boundary_only,
            "metadata_only": self.metadata_only,
            "consumer_phase": PHASE12F_CONSUMER_PHASE,
            "canonical_owner": PHASE12F_CANONICAL_OWNER,
            "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
            "grant_status": PHASE12F_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "secure_drop_send_permitted": False,
            "secure_drop_receive_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12GProductionReadinessCoverageMatrixValidationResult:
    """Sanitized validation result for Phase 12G production-readiness matrices."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    production_readiness_coverage_matrix_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12G_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "production_readiness_coverage_matrix_only": (
                self.production_readiness_coverage_matrix_only
            ),
            "metadata_only": self.metadata_only,
            "readiness_phase": PHASE12G_READINESS_PHASE,
            "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
            "grant_status": PHASE12G_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "phase12g_makes_somatic_production_ready": False,
            "phase12g_authorizes_runtime": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult:
    """Sanitized validation result for Phase 12H standalone ownership maps."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    standalone_ownership_map_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12H_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "standalone_ownership_map_only": self.standalone_ownership_map_only,
            "metadata_only": self.metadata_only,
            "readiness_phase": PHASE12H_READINESS_PHASE,
            "authorization_status": PHASE12H_AUTHORIZATION_STATUS,
            "grant_status": PHASE12H_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "phase12h_marks_somatic_production_ready": False,
            "phase12h_authorizes_runtime": False,
            "somatic_standalone_ownership_retained": True,
            "external_integrations_optional": True,
            "external_repo_integration_replaces_somatic_standalone_path": False,
            "cross_repo_mutation_permitted": False,
            "external_repo_tasks_executed_by_somatic": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12I knowledge profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    knowledge_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12I_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "knowledge_profile_only": self.knowledge_profile_only,
            "metadata_only": self.metadata_only,
            "capability_phase": PHASE12I_CAPABILITY_PHASE,
            "authorization_status": PHASE12I_AUTHORIZATION_STATUS,
            "grant_status": PHASE12I_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "phase12i_provides_medical_advice": False,
            "phase12i_authorizes_runtime": False,
            "phase12i_suppresses_safety_warnings": False,
            "phase12i_claims_western_medicine_invalid": False,
            "phase12i_claims_natural_remedies_safe_by_default": False,
            "phase12i_claims_food_cures_disease": False,
            "medical_advice_provided": False,
            "clinical_decision_support_added": False,
            "clinical_recommendation_added": False,
            "diagnosis_provided": False,
            "treatment_plan_provided": False,
            "herb_dosing_added": False,
            "supplement_dosing_added": False,
            "calorie_macro_prescription_added": False,
            "unsafe_fasting_weight_loss_advice_added": False,
            "database_ingestion_added": False,
            "web_scraping_added": False,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "active_grant_present": False,
            "runtime_adapter_execution_granted": False,
            "real_mode_authorization_added": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12K external compute profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    external_compute_quantum_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12K_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "external_compute_quantum_profile_only": (self.external_compute_quantum_profile_only),
            "metadata_only": self.metadata_only,
            "capability_phase": PHASE12K_CAPABILITY_PHASE,
            "authorization_status": PHASE12K_AUTHORIZATION_STATUS,
            "grant_status": PHASE12K_GRANT_STATUS,
            "credential_policy": PHASE12K_CREDENTIAL_POLICY,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "human_approval_required": True,
            "cost_guard_required": True,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "phase12k_authorizes_runtime": False,
            "phase12k_allows_external_compute_execution": False,
            "phase12k_allows_quantum_backend_execution": False,
            "phase12k_allows_private_health_data_processing": False,
            "phase12k_provides_medical_advice": False,
            "phase12k_allows_diagnosis_or_treatment": False,
            "api_call_execution_granted": False,
            "sdk_execution_granted": False,
            "simulator_execution_granted": False,
            "provider_call_execution_granted": False,
            "network_call_execution_granted": False,
            "spending_permitted": False,
            "credential_loading_added": False,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "training_execution_granted": False,
            "fine_tuning_execution_granted": False,
            "runtime_adapter_execution_granted": False,
            "active_grant_present": False,
            "real_mode_authorization_added": False,
            "clinical_decision_support_added": False,
            "clinical_recommendation_added": False,
            "medical_advice_provided": False,
            "diagnosis_provided": False,
            "treatment_plan_provided": False,
            "private_health_data_processing_added": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12L fabric boundary profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    fabric_interop_a2a_audit_boundary_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12L_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "fabric_interop_a2a_audit_boundary_profile_only": (
                self.fabric_interop_a2a_audit_boundary_profile_only
            ),
            "metadata_only": self.metadata_only,
            "capability_phase": PHASE12L_CAPABILITY_PHASE,
            "authorization_status": PHASE12L_AUTHORIZATION_STATUS,
            "grant_status": PHASE12L_GRANT_STATUS,
            "fabric_interop_status": PHASE12L_FABRIC_INTEROP_STATUS,
            "message_codec_status": PHASE12L_MESSAGE_CODEC_STATUS,
            "a2a_transport_status": PHASE12L_A2A_TRANSPORT_STATUS,
            "mcp_interop_status": PHASE12L_MCP_INTEROP_STATUS,
            "secure_drop_status": PHASE12L_SECURE_DROP_STATUS,
            "credential_policy": PHASE12L_CREDENTIAL_POLICY,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "opaque_traffic_allowed": False,
            "untrusted_content_executable": False,
            "cross_repo_mutation_allowed": False,
            "plaintext_json_default_future_requirement_only": True,
            "decode_to_audit_future_requirement_only": True,
            "secure_drop_user_initiated_boundary_only": True,
            "phase12l_authorizes_runtime": False,
            "phase12l_allows_fabric_runtime": False,
            "phase12l_allows_a2a_transport": False,
            "phase12l_allows_mcp_runtime": False,
            "phase12l_allows_secure_drop_send_receive": False,
            "message_codec_implementation_added": False,
            "a2a_transport_implementation_added": False,
            "mcp_server_implementation_added": False,
            "mcp_client_implementation_added": False,
            "secure_drop_send_permitted": False,
            "secure_drop_receive_permitted": False,
            "crypto_implementation_added": False,
            "credential_loading_added": False,
            "vault_env_access_granted": False,
            "secrets_access_granted": False,
            "network_call_execution_granted": False,
            "filesystem_autoscan_added": False,
            "connector_installation_added": False,
            "pack_registration_added": False,
            "provider_execution_granted": False,
            "provider_call_execution_granted": False,
            "model_execution_granted": False,
            "runtime_model_execution_granted": False,
            "runtime_adapter_execution_granted": False,
            "active_grant_present": False,
            "real_mode_authorization_added": False,
            "connector_grant_present": False,
            "fabric_transfer_execution_granted": False,
            "ws_stream_execution_granted": False,
            "http_execution_granted": False,
            "mcp_tool_exposure_added": False,
            "task_execution_granted": False,
            "service_discovery_runtime_added": False,
            "schedule_enforcement_added": False,
            "filesystem_access_granted": False,
            "process_control_granted": False,
            "db_storage_write_added": False,
            "agent_invoked_secure_drop_allowed": False,
            "automation_invoked_secure_drop_allowed": False,
            "bundled_agpl_codec_allowed": False,
            "glossopetrae_vendoring_allowed": False,
            "st3gg_vendoring_allowed": False,
            "covert_channel_allowed": False,
            "opaque_message_acting_allowed": False,
            "untrusted_content_execution_added": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12M model option registry profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    specialized_model_option_registry_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12M_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "specialized_model_option_registry_profile_only": (
                self.specialized_model_option_registry_profile_only
            ),
            "metadata_only": self.metadata_only,
            "model_option_profile_phase": PHASE12M_MODEL_OPTION_PROFILE_PHASE,
            "authorization_status": PHASE12M_AUTHORIZATION_STATUS,
            "grant_status": PHASE12M_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "model_execution_permitted": False,
            "provider_execution_permitted": False,
            "training_permitted": False,
            "fine_tuning_permitted": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "private_health_data_allowed": False,
            "phase12m_authorizes_runtime": False,
            "phase12m_allows_model_execution": False,
            "phase12m_allows_provider_execution": False,
            "phase12m_allows_model_loading": False,
            "phase12m_allows_training": False,
            "phase12m_allows_fine_tuning": False,
            "phase12m_allows_clinical_decision_support": False,
            "phase12m_allows_diagnosis_or_treatment": False,
            "phase12m_allows_private_health_data_processing": False,
            "phase12m_allows_device_access": False,
            "phase12m_allows_raw_sensor_processing": False,
            "phase12m_provides_medical_advice": False,
            "phase12m_provides_prescribing": False,
            "model_loading_added": False,
            "runtime_model_execution_granted": False,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "training_execution_granted": False,
            "fine_tuning_execution_granted": False,
            "runtime_adapter_execution_granted": False,
            "active_grant_present": False,
            "real_mode_authorization_added": False,
            "database_ingestion_added": False,
            "web_scraping_added": False,
            "network_call_execution_granted": False,
            "clinical_decision_support_added": False,
            "clinical_recommendation_added": False,
            "medical_advice_provided": False,
            "diagnosis_provided": False,
            "treatment_plan_provided": False,
            "prescribing_added": False,
            "herb_dosing_added": False,
            "supplement_dosing_added": False,
            "calorie_macro_prescription_added": False,
            "nutrition_prescription_added": False,
            "private_health_data_processing_added": False,
            "device_access_granted": False,
            "device_connection_execution_granted": False,
            "raw_sensor_processing_added": False,
            "sensor_processing_execution_granted": False,
            "monitoring_added": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult:
    """Sanitized validation result for Phase 12N workflow mode registry profiles."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_orchestration_mode_registry_profile_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12N_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_orchestration_mode_registry_profile_only": (
                self.workflow_orchestration_mode_registry_profile_only
            ),
            "metadata_only": self.metadata_only,
            "workflow_mode_profile_phase": PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
            "authorization_status": PHASE12N_AUTHORIZATION_STATUS,
            "grant_status": PHASE12N_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "workflow_modes_metadata_only": True,
            "phase12n_authorizes_runtime": False,
            "phase12n_allows_workflow_mode_execution": False,
            "phase12n_allows_runtime_orchestration": False,
            "phase12n_allows_model_routing": False,
            "phase12n_allows_provider_execution": False,
            "phase12n_allows_model_execution": False,
            "phase12n_allows_model_loading": False,
            "phase12n_allows_training": False,
            "phase12n_allows_fine_tuning": False,
            "phase12n_allows_code_execution": False,
            "phase12n_allows_experiment_execution": False,
            "phase12n_allows_autonomous_experimentation": False,
            "phase12n_allows_web_access": False,
            "phase12n_allows_autonomous_publication": False,
            "phase12n_allows_clinical_decision_support": False,
            "phase12n_allows_diagnosis_or_treatment": False,
            "phase12n_allows_private_health_data_processing": False,
            "phase12n_allows_device_or_sensor_access": False,
            "phase12n_provides_medical_advice": False,
            **{field: False for field in _phase12n_runtime_false_fields()},
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult:
    """Sanitized validation result for Phase 12O workflow-mode prerequisite matrices."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_mode_safety_gate_matrix_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12O_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_mode_safety_gate_matrix_only": (self.workflow_mode_safety_gate_matrix_only),
            "metadata_only": self.metadata_only,
            "matrix_phase": PHASE12O_MATRIX_PHASE,
            "authorization_status": PHASE12O_AUTHORIZATION_STATUS,
            "grant_status": PHASE12O_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "workflow_mode_safety_gates_metadata_only": True,
            "phase12o_authorizes_runtime": False,
            "phase12o_satisfies_runtime_prerequisites": False,
            "phase12o_allows_workflow_execution": False,
            "phase12o_allows_workflow_mode_execution": False,
            "phase12o_allows_runtime_adapter": False,
            "phase12o_allows_model_routing": False,
            "phase12o_allows_provider_execution": False,
            "phase12o_allows_model_execution": False,
            "phase12o_allows_code_execution": False,
            "phase12o_allows_experiment_execution": False,
            "phase12o_allows_web_database_network_behavior": False,
            "phase12o_allows_clinical_decision_support": False,
            "phase12o_allows_private_health_data_processing": False,
            "phase12o_active_grant_present": False,
            **{field: False for field in _phase12o_runtime_false_fields()},
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12PWorkflowModeActivationRequestReviewPacketValidationResult:
    """Sanitized validation result for Phase 12P workflow-mode review packets."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_mode_activation_request_review_packet_boundary_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12P_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_mode_activation_request_review_packet_boundary_only": (
                self.workflow_mode_activation_request_review_packet_boundary_only
            ),
            "metadata_only": self.metadata_only,
            "packet_phase": PHASE12P_PACKET_PHASE,
            "authorization_status": PHASE12P_AUTHORIZATION_STATUS,
            "grant_status": PHASE12P_GRANT_STATUS,
            "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "review_packet_boundary_only": True,
            "all_future_gates_unsatisfied": True,
            "denial_blocked_default_fail_closed": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "workflow_mode_activation_not_permitted": True,
            "phase12p_authorizes_runtime": False,
            "phase12p_creates_active_grant": False,
            "phase12p_grants_execution_permission": False,
            "phase12p_allows_workflow_execution": False,
            "phase12p_allows_workflow_mode_execution": False,
            "phase12p_allows_runtime_adapter": False,
            "phase12p_allows_model_routing": False,
            "phase12p_allows_provider_execution": False,
            "phase12p_allows_model_execution": False,
            "phase12p_allows_model_loading": False,
            "phase12p_allows_training": False,
            "phase12p_allows_fine_tuning": False,
            "phase12p_allows_code_execution": False,
            "phase12p_allows_experiment_execution": False,
            "phase12p_allows_autonomous_experimentation": False,
            "phase12p_allows_web_access": False,
            "phase12p_allows_database_ingestion": False,
            "phase12p_allows_web_scraping": False,
            "phase12p_allows_network_calls": False,
            "phase12p_allows_clinical_decision_support": False,
            "phase12p_allows_diagnosis_or_treatment": False,
            "phase12p_allows_medical_advice": False,
            "phase12p_allows_dosing_or_nutrition_prescription": False,
            "phase12p_allows_private_health_data_processing": False,
            "phase12p_allows_device_or_sensor_access": False,
            "phase12p_allows_raw_sensor_processing": False,
            "phase12p_marks_production_ready": False,
            **{field: False for field in _phase12p_runtime_false_fields()},
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12QWorkflowModeReviewDecisionRecordValidationResult:
    """Sanitized validation result for Phase 12Q review decision records."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_mode_review_decision_record_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("decision_status") or PHASE12Q_DEFAULT_DECISION_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_mode_review_decision_record_only": (
                self.workflow_mode_review_decision_record_only
            ),
            "metadata_only": self.metadata_only,
            "decision_record_phase": PHASE12Q_DECISION_RECORD_PHASE,
            "authorization_status": PHASE12Q_AUTHORIZATION_STATUS,
            "grant_status": PHASE12Q_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "review_decision_record_only": True,
            "not_authorized": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "runtime_authorization_not_granted": True,
            "workflow_mode_activation_not_permitted": True,
            "phase12q_authorizes_runtime": False,
            "phase12q_creates_active_grant": False,
            "phase12q_grants_execution_permission": False,
            "phase12q_allows_workflow_activation": False,
            "phase12q_allows_workflow_execution": False,
            "phase12q_allows_workflow_mode_execution": False,
            "phase12q_allows_runtime_adapter": False,
            "phase12q_allows_model_routing": False,
            "phase12q_allows_provider_execution": False,
            "phase12q_allows_model_execution": False,
            "phase12q_allows_model_loading": False,
            "phase12q_allows_training": False,
            "phase12q_allows_fine_tuning": False,
            "phase12q_allows_code_execution": False,
            "phase12q_allows_experiment_execution": False,
            "phase12q_allows_autonomous_experimentation": False,
            "phase12q_allows_web_access": False,
            "phase12q_allows_database_ingestion": False,
            "phase12q_allows_web_scraping": False,
            "phase12q_allows_network_calls": False,
            "phase12q_allows_clinical_decision_support": False,
            "phase12q_allows_diagnosis_or_treatment": False,
            "phase12q_allows_medical_advice": False,
            "phase12q_allows_dosing_or_nutrition_prescription": False,
            "phase12q_allows_private_health_data_processing": False,
            "phase12q_allows_device_or_sensor_access": False,
            "phase12q_allows_raw_sensor_processing": False,
            "phase12q_marks_production_ready": False,
            **{field: False for field in _phase12q_runtime_false_fields()},
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12RWorkflowModeReviewAuditTrailIndexValidationResult:
    """Sanitized validation result for Phase 12R audit trail indexes."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_mode_review_audit_trail_index_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("decision_status") or PHASE12Q_DEFAULT_DECISION_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_mode_review_audit_trail_index_only": (
                self.workflow_mode_review_audit_trail_index_only
            ),
            "metadata_only": self.metadata_only,
            "audit_trail_index_phase": PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
            "authorization_status": PHASE12R_AUTHORIZATION_STATUS,
            "grant_status": PHASE12R_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "not_authorized": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "runtime_authorization_not_granted": True,
            "workflow_mode_activation_not_permitted": True,
            "phase12r_authorizes_runtime": False,
            "phase12r_creates_active_grant": False,
            "phase12r_grants_execution_permission": False,
            "phase12r_allows_workflow_activation": False,
            "phase12r_allows_workflow_execution": False,
            "phase12r_allows_workflow_mode_execution": False,
            "phase12r_allows_runtime_adapter": False,
            "phase12r_allows_model_routing": False,
            "phase12r_allows_provider_execution": False,
            "phase12r_allows_model_execution": False,
            "phase12r_allows_model_loading": False,
            "phase12r_allows_training": False,
            "phase12r_allows_fine_tuning": False,
            "phase12r_allows_code_execution": False,
            "phase12r_allows_experiment_execution": False,
            "phase12r_allows_autonomous_experimentation": False,
            "phase12r_allows_shell_execution": False,
            "phase12r_allows_process_execution": False,
            "phase12r_allows_cache_event_bus_pubsub_runtime": False,
            "phase12r_allows_web_access": False,
            "phase12r_allows_database_ingestion": False,
            "phase12r_allows_database_writes": False,
            "phase12r_allows_query_execution": False,
            "phase12r_allows_web_scraping": False,
            "phase12r_allows_network_calls": False,
            "phase12r_allows_clinical_decision_support": False,
            "phase12r_allows_diagnosis_or_treatment": False,
            "phase12r_allows_medical_advice": False,
            "phase12r_allows_dosing_or_nutrition_prescription": False,
            "phase12r_allows_private_health_data_processing": False,
            "phase12r_allows_device_or_sensor_access": False,
            "phase12r_allows_raw_sensor_processing": False,
            "phase12r_marks_production_ready": False,
            **{field: False for field in _phase12r_runtime_false_fields()},
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult:
    """Sanitized validation result for Phase 12S closeout summaries."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    workflow_mode_review_chain_closeout_summary_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(self.sanitized_record.get("closeout_status") or PHASE12S_DEFAULT_CLOSEOUT_STATUS)

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "workflow_mode_review_chain_closeout_summary_only": (
                self.workflow_mode_review_chain_closeout_summary_only
            ),
            "metadata_only": self.metadata_only,
            "closeout_summary_phase": PHASE12S_CLOSEOUT_SUMMARY_PHASE,
            "authorization_status": PHASE12S_AUTHORIZATION_STATUS,
            "grant_status": PHASE12S_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "not_authorized": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "runtime_authorization_not_granted": True,
            "workflow_mode_activation_not_permitted": True,
            "phase12s_authorizes_runtime": False,
            "phase12s_creates_active_grant": False,
            "phase12s_grants_execution_permission": False,
            "phase12s_allows_workflow_activation": False,
            "phase12s_allows_workflow_execution": False,
            "phase12s_allows_workflow_mode_execution": False,
            "phase12s_allows_runtime_adapter": False,
            "phase12s_allows_model_routing": False,
            "phase12s_allows_provider_execution": False,
            "phase12s_allows_model_execution": False,
            "phase12s_allows_model_loading": False,
            "phase12s_allows_training": False,
            "phase12s_allows_fine_tuning": False,
            "phase12s_allows_code_execution": False,
            "phase12s_allows_shell_execution": False,
            "phase12s_allows_process_execution": False,
            "phase12s_allows_experiment_execution": False,
            "phase12s_allows_autonomous_experimentation": False,
            "phase12s_allows_web_access": False,
            "phase12s_allows_network_behavior": False,
            "phase12s_allows_database_ingestion": False,
            "phase12s_allows_database_writes": False,
            "phase12s_allows_query_execution": False,
            "phase12s_allows_cache_event_bus_pubsub_runtime": False,
            "phase12s_allows_transport_implementation": False,
            "phase12s_allows_fabric_implementation": False,
            "phase12s_allows_p2p_implementation": False,
            "phase12s_allows_clinical_decision_support": False,
            "phase12s_allows_diagnosis_or_treatment": False,
            "phase12s_allows_medical_advice": False,
            "phase12s_allows_dosing_or_nutrition_prescription": False,
            "phase12s_allows_private_health_data_processing": False,
            "phase12s_allows_device_or_sensor_access": False,
            "phase12s_allows_raw_sensor_processing": False,
            "phase12s_marks_deployment_ready": False,
            "phase12s_marks_production_ready": False,
            **{field: False for field in _phase12s_runtime_false_fields()},
            "deployment_ready": False,
            "production_ready": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


@dataclass(frozen=True)
class Phase12BRuntimeAuthorizationRecordCandidateValidationResult:
    """Sanitized validation result for Phase 12B record candidates."""

    classification: str
    valid: bool
    errors: tuple[str, ...]
    privacy_violation_count: int
    authorization_wording_count: int
    sanitized_record: dict[str, object]
    sanitized: bool = True
    record_candidate_only: bool = True
    metadata_only: bool = True

    @property
    def compatible(self) -> bool:
        return self.valid and self.classification == "compatible"

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def status(self) -> str:
        return str(
            self.sanitized_record.get("authorization_status") or PHASE12B_AUTHORIZATION_STATUS
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "compatible": self.compatible,
            "valid": self.valid,
            "error_count": self.error_count,
            "errors": list(self.errors),
            "privacy_violation_count": self.privacy_violation_count,
            "authorization_wording_count": self.authorization_wording_count,
            "status": self.status,
            "sanitized": self.sanitized,
            "record_candidate_only": self.record_candidate_only,
            "metadata_only": self.metadata_only,
            "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
            "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
            "decision_status": PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
            "grant_status": PHASE12B_GRANT_STATUS,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }


def phase12a_runtime_authorization_design_charter(
    *,
    governance_closeout: Mapping[str, object] | None = None,
    runtime_gap_ledger: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12A runtime authorization design charter.

    This defines future authorization gates as unsatisfied metadata. It does not
    authorize, prepare, or execute runtime behavior.
    """

    closeout = governance_closeout or phase11_planning_governance_closeout_index()
    closeout_result = validate_phase11_planning_governance_closeout_index(closeout)
    safe_closeout = (
        closeout_result.sanitized_record
        if closeout_result.compatible
        else rejected_phase11_planning_governance_closeout_index()
    )
    ledger = runtime_gap_ledger or phase11_runtime_authorization_gap_ledger()
    ledger_result = validate_phase11_runtime_authorization_gap_ledger(ledger)
    safe_ledger = (
        ledger_result.sanitized_record
        if ledger_result.compatible
        else rejected_phase11_runtime_authorization_gap_ledger()
    )
    payload = {
        "runtime_authorization_design_charter_contract_version": (
            PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION
        ),
        "charter_kind": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id": None,
        "source_phase_range": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE,
        "source_governance_closeout": _phase12a_source_governance_closeout(safe_closeout),
        "source_runtime_gap_ledger": _phase12a_source_runtime_gap_ledger(safe_ledger),
        "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "charter_scope": PHASE12A_CHARTER_SCOPE,
        "charter_status": PHASE12A_CHARTER_STATUS,
        "phase12a_satisfies_future_gates": False,
        "future_required_gates": _phase12a_future_required_gates(),
        "future_required_gate_count": len(PHASE12A_FUTURE_REQUIRED_GATES),
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    charter = _finalize_phase12a_runtime_authorization_design_charter(payload)
    result = validate_phase12a_runtime_authorization_design_charter(charter)
    return (
        charter if result.compatible else rejected_phase12a_runtime_authorization_design_charter()
    )


def phase12a_runtime_authorization_design_charter_status_summary() -> dict[str, object]:
    """Return compact Phase 12A status safe for public surfaces."""

    charter = phase12a_runtime_authorization_design_charter()
    result = validate_phase12a_runtime_authorization_design_charter(charter)
    safe = result.sanitized_record
    return {
        "runtime_authorization_design_charter_contract_version": (
            PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION
        ),
        "charter_id": _safe_phase12a_charter_id(safe.get("charter_id")),
        "source_phase_range": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE,
        "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "grant_status": "no-grant",
        "charter_scope": PHASE12A_CHARTER_SCOPE,
        "charter_status": PHASE12A_CHARTER_STATUS,
        "future_required_gate_count": _safe_int(safe.get("future_required_gate_count")),
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12a_runtime_authorization_design_charter(
    charter: object,
) -> Phase12ARuntimeAuthorizationDesignCharterValidationResult:
    """Validate a Phase 12A charter and fail closed on grant-like content."""

    if not isinstance(charter, Mapping):
        return _invalid_phase12a_charter_result(
            ("phase12a_charter_not_object",),
            "malformed",
            rejected_phase12a_runtime_authorization_design_charter(),
        )
    privacy_violations = _privacy_violation_count(charter)
    authorization_wording = _authorization_wording_count(charter)
    errors: list[str] = []
    if PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_REQUIRED_FIELDS - set(charter):
        errors.append("phase12a_charter_required_field_missing")
    if set(str(key) for key in charter) - PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_REQUIRED_FIELDS:
        errors.append("phase12a_charter_unknown_field")
    if (
        charter.get("runtime_authorization_design_charter_contract_version")
        != PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION
    ):
        errors.append("phase12a_charter_contract_version_unsupported")
    if charter.get("charter_kind") != PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND:
        errors.append("phase12a_charter_kind_invalid")
    if _safe_phase12a_charter_id(charter.get("charter_id")) != charter.get("charter_id"):
        errors.append("phase12a_charter_id_invalid")
    if (
        charter.get("source_phase_range")
        != PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE
    ):
        errors.append("phase12a_charter_source_phase_range_invalid")
    errors.extend(_source_governance_closeout_errors(charter.get("source_governance_closeout")))
    errors.extend(_source_runtime_gap_ledger_errors(charter.get("source_runtime_gap_ledger")))
    if charter.get("authorization_phase") != PHASE12A_AUTHORIZATION_PHASE:
        errors.append("phase12a_charter_authorization_phase_invalid")
    if charter.get("authorization_status") != PHASE12A_AUTHORIZATION_STATUS:
        errors.append("phase12a_charter_authorization_status_invalid")
    if charter.get("charter_scope") != PHASE12A_CHARTER_SCOPE:
        errors.append("phase12a_charter_scope_invalid")
    if charter.get("charter_status") != PHASE12A_CHARTER_STATUS:
        errors.append("phase12a_charter_status_invalid")
    if charter.get("phase12a_satisfies_future_gates") is not False:
        errors.append("phase12a_charter_future_gate_satisfaction_implied")
    errors.extend(_future_gate_errors(charter.get("future_required_gates")))
    for field in (
        "future_required_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
    ):
        if not _is_non_negative_int(charter.get(field)):
            errors.append("phase12a_charter_count_invalid")
            break
    if charter.get("future_required_gate_count") != len(PHASE12A_FUTURE_REQUIRED_GATES):
        errors.append("phase12a_charter_required_gate_count_invalid")
    if charter.get("satisfied_future_gate_count") != 0:
        errors.append("phase12a_charter_satisfied_gate_count_invalid")
    if charter.get("passed_future_gate_count") != 0:
        errors.append("phase12a_charter_passed_gate_count_invalid")
    if charter.get("jules_review_required_for_validator_or_authorization_semantics") is not True:
        errors.append("phase12a_charter_jules_review_requirement_invalid")
    for field in (
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if charter.get(field) is not False:
            errors.append("phase12a_charter_runtime_implied")
            break
    if charter.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase12a_charter_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase12a_charter_privacy_boundary")
    if authorization_wording:
        errors.append("phase12a_charter_authorization_wording")
    expected_id = _phase12a_charter_id(charter)
    if not expected_id:
        errors.append("phase12a_charter_payload_not_json")
    elif charter.get("charter_id") != expected_id:
        errors.append("phase12a_charter_id_invalid")
    if errors:
        return _invalid_phase12a_charter_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12a_charter_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12a_runtime_authorization_design_charter(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12ARuntimeAuthorizationDesignCharterValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(charter),
    )


def rejected_phase12a_runtime_authorization_design_charter() -> dict[str, object]:
    """Return sanitized rejected Phase 12A charter metadata."""

    payload = {
        "runtime_authorization_design_charter_contract_version": (
            PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION
        ),
        "charter_kind": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "charter_id": None,
        "source_phase_range": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE,
        "source_governance_closeout": _phase12a_source_governance_closeout(
            rejected_phase11_planning_governance_closeout_index()
        ),
        "source_runtime_gap_ledger": _phase12a_source_runtime_gap_ledger(
            rejected_phase11_runtime_authorization_gap_ledger()
        ),
        "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "charter_scope": PHASE12A_CHARTER_SCOPE,
        "charter_status": PHASE12A_CHARTER_STATUS,
        "phase12a_satisfies_future_gates": False,
        "future_required_gates": _phase12a_future_required_gates(),
        "future_required_gate_count": len(PHASE12A_FUTURE_REQUIRED_GATES),
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase12a_runtime_authorization_design_charter(payload)


def phase12b_runtime_authorization_record_candidate(
    *,
    source_charter: Mapping[str, object] | None = None,
    decision_status: str = PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
) -> dict[str, object]:
    """Return the Phase 12B runtime authorization record candidate.

    This defines the shape of future request and decision records as metadata
    only. It is not an approval, grant, permission, or runtime authorization.
    """

    charter = source_charter or phase12a_runtime_authorization_design_charter()
    charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
    safe_charter = (
        charter_result.sanitized_record
        if charter_result.compatible
        else rejected_phase12a_runtime_authorization_design_charter()
    )
    safe_decision_status = (
        decision_status
        if decision_status in PHASE12B_DECISION_STATUSES
        else PHASE12B_DECISION_STATUS_NOT_SUBMITTED
    )
    payload = {
        "runtime_authorization_record_candidate_contract_version": (
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION
        ),
        "record_kind": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id": None,
        "source_phase": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE,
        "source_design_charter": _phase12b_source_design_charter(safe_charter),
        "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
        "decision_status": safe_decision_status,
        "grant_status": PHASE12B_GRANT_STATUS,
        "record_candidate_status": PHASE12B_RECORD_CANDIDATE_STATUS,
        "phase12b_records_are_approvals_grants_or_permissions": False,
        "requested_domains": _phase12b_requested_domains(),
        "requested_domain_count": len(PHASE12B_REQUESTED_DOMAINS),
        "required_future_reviewer_roles": _phase12b_required_reviewer_roles(),
        "required_future_reviewer_role_count": len(PHASE12B_REQUIRED_REVIEWER_ROLES),
        "required_future_gates": _phase12b_required_future_gates(),
        "required_future_gate_count": len(PHASE12B_REQUIRED_FUTURE_GATES),
        "submitted_future_gate_count": 0,
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    record = _finalize_phase12b_runtime_authorization_record_candidate(payload)
    result = validate_phase12b_runtime_authorization_record_candidate(record)
    return (
        record if result.compatible else rejected_phase12b_runtime_authorization_record_candidate()
    )


def phase12b_runtime_authorization_record_candidate_status_summary() -> dict[str, object]:
    """Return compact Phase 12B status safe for public surfaces."""

    record = phase12b_runtime_authorization_record_candidate()
    result = validate_phase12b_runtime_authorization_record_candidate(record)
    safe = result.sanitized_record
    return {
        "runtime_authorization_record_candidate_contract_version": (
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION
        ),
        "record_id": _safe_phase12b_record_id(safe.get("record_id")),
        "source_phase": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE,
        "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
        "decision_status": PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
        "grant_status": PHASE12B_GRANT_STATUS,
        "record_candidate_status": PHASE12B_RECORD_CANDIDATE_STATUS,
        "requested_domain_count": _safe_int(safe.get("requested_domain_count")),
        "required_future_reviewer_role_count": _safe_int(
            safe.get("required_future_reviewer_role_count")
        ),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "submitted_future_gate_count": 0,
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12b_runtime_authorization_record_candidate(
    record: object,
) -> Phase12BRuntimeAuthorizationRecordCandidateValidationResult:
    """Validate a Phase 12B record candidate and reject runtime grants."""

    if not isinstance(record, Mapping):
        return _invalid_phase12b_record_result(
            ("phase12b_record_not_object",),
            "malformed",
            rejected_phase12b_runtime_authorization_record_candidate(),
        )
    privacy_violations = _privacy_violation_count(record)
    authorization_wording = _authorization_wording_count(record)
    errors: list[str] = []
    if PHASE12B_RUNTIME_AUTHORIZATION_RECORD_REQUIRED_FIELDS - set(record):
        errors.append("phase12b_record_required_field_missing")
    if set(str(key) for key in record) - PHASE12B_RUNTIME_AUTHORIZATION_RECORD_REQUIRED_FIELDS:
        errors.append("phase12b_record_unknown_field")
    if (
        record.get("runtime_authorization_record_candidate_contract_version")
        != PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION
    ):
        errors.append("phase12b_record_contract_version_unsupported")
    if record.get("record_kind") != PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND:
        errors.append("phase12b_record_kind_invalid")
    if _safe_phase12b_record_id(record.get("record_id")) != record.get("record_id"):
        errors.append("phase12b_record_id_invalid")
    if record.get("source_phase") != PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE:
        errors.append("phase12b_record_source_phase_invalid")
    errors.extend(_source_design_charter_errors(record.get("source_design_charter")))
    if record.get("authorization_phase") != PHASE12B_AUTHORIZATION_PHASE:
        errors.append("phase12b_record_authorization_phase_invalid")
    if record.get("authorization_status") != PHASE12B_AUTHORIZATION_STATUS:
        errors.append("phase12b_record_authorization_status_invalid")
    if record.get("decision_status") not in PHASE12B_DECISION_STATUSES:
        errors.append("phase12b_record_decision_status_invalid")
    if record.get("grant_status") != PHASE12B_GRANT_STATUS:
        errors.append("phase12b_record_grant_status_invalid")
    if record.get("record_candidate_status") != PHASE12B_RECORD_CANDIDATE_STATUS:
        errors.append("phase12b_record_candidate_status_invalid")
    if record.get("phase12b_records_are_approvals_grants_or_permissions") is not False:
        errors.append("phase12b_record_approval_grant_or_permission_implied")
    errors.extend(_requested_domain_errors(record.get("requested_domains")))
    errors.extend(_required_reviewer_role_errors(record.get("required_future_reviewer_roles")))
    errors.extend(_phase12b_future_gate_errors(record.get("required_future_gates")))
    for field in (
        "requested_domain_count",
        "required_future_reviewer_role_count",
        "required_future_gate_count",
        "submitted_future_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
    ):
        if not _is_non_negative_int(record.get(field)):
            errors.append("phase12b_record_count_invalid")
            break
    if record.get("requested_domain_count") != len(PHASE12B_REQUESTED_DOMAINS):
        errors.append("phase12b_record_requested_domain_count_invalid")
    if record.get("required_future_reviewer_role_count") != len(PHASE12B_REQUIRED_REVIEWER_ROLES):
        errors.append("phase12b_record_reviewer_role_count_invalid")
    if record.get("required_future_gate_count") != len(PHASE12B_REQUIRED_FUTURE_GATES):
        errors.append("phase12b_record_required_gate_count_invalid")
    for field in (
        "submitted_future_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
    ):
        if record.get(field) != 0:
            errors.append("phase12b_record_gate_count_implies_passed_gate")
            break
    if record.get("jules_review_required_for_validator_or_authorization_semantics") is not True:
        errors.append("phase12b_record_jules_review_requirement_invalid")
    for field in (
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if record.get(field) is not False:
            errors.append("phase12b_record_runtime_implied")
            break
    if record.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase12b_record_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase12b_record_privacy_boundary")
    if authorization_wording:
        errors.append("phase12b_record_authorization_wording")
    expected_id = _phase12b_record_id(record)
    if not expected_id:
        errors.append("phase12b_record_payload_not_json")
    elif record.get("record_id") != expected_id:
        errors.append("phase12b_record_id_invalid")
    if errors:
        return _invalid_phase12b_record_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12b_record_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12b_runtime_authorization_record_candidate(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12BRuntimeAuthorizationRecordCandidateValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(record),
    )


def rejected_phase12b_runtime_authorization_record_candidate() -> dict[str, object]:
    """Return sanitized rejected Phase 12B record candidate metadata."""

    payload = {
        "runtime_authorization_record_candidate_contract_version": (
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION
        ),
        "record_kind": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "record_id": None,
        "source_phase": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE,
        "source_design_charter": _phase12b_source_design_charter(
            rejected_phase12a_runtime_authorization_design_charter()
        ),
        "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
        "decision_status": PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
        "grant_status": PHASE12B_GRANT_STATUS,
        "record_candidate_status": PHASE12B_RECORD_CANDIDATE_STATUS,
        "phase12b_records_are_approvals_grants_or_permissions": False,
        "requested_domains": _phase12b_requested_domains(),
        "requested_domain_count": len(PHASE12B_REQUESTED_DOMAINS),
        "required_future_reviewer_roles": _phase12b_required_reviewer_roles(),
        "required_future_reviewer_role_count": len(PHASE12B_REQUIRED_REVIEWER_ROLES),
        "required_future_gates": _phase12b_required_future_gates(),
        "required_future_gate_count": len(PHASE12B_REQUIRED_FUTURE_GATES),
        "submitted_future_gate_count": 0,
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase12b_runtime_authorization_record_candidate(payload)


def phase12c_visual_supervision_capability_profile(
    *,
    source_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12C visual supervision capability profile.

    This defines future visual supervision capability labels as metadata only.
    It is not an approval, grant, permission, or runtime authorization.
    """

    record = source_record or phase12b_runtime_authorization_record_candidate()
    record_result = validate_phase12b_runtime_authorization_record_candidate(record)
    safe_record = (
        record_result.sanitized_record
        if record_result.compatible
        else rejected_phase12b_runtime_authorization_record_candidate()
    )
    payload = {
        "visual_supervision_capability_profile_contract_version": (
            PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id": None,
        "source_phase": PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE,
        "source_record_candidate": _phase12c_source_record_candidate(safe_record),
        "supervision_phase": PHASE12C_SUPERVISION_PHASE,
        "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
        "grant_status": PHASE12C_GRANT_STATUS,
        "profile_status": PHASE12C_PROFILE_STATUS,
        "phase12c_profiles_are_approvals_grants_or_permissions": False,
        "capability_labels": _phase12c_capability_labels(),
        "capability_label_count": len(PHASE12C_ALLOWED_CAPABILITY_LABELS),
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "visual_capture_execution_granted": False,
        "clipboard_capture_execution_granted": False,
        "mic_capture_execution_granted": False,
        "camera_capture_execution_granted": False,
        "click_automation_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    profile = _finalize_phase12c_visual_supervision_capability_profile(payload)
    result = validate_phase12c_visual_supervision_capability_profile(profile)
    return (
        profile if result.compatible else rejected_phase12c_visual_supervision_capability_profile()
    )


def phase12c_visual_supervision_capability_profile_status_summary() -> dict[str, object]:
    """Return compact Phase 12C status safe for public surfaces."""

    profile = phase12c_visual_supervision_capability_profile()
    result = validate_phase12c_visual_supervision_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "visual_supervision_capability_profile_contract_version": (
            PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12c_profile_id(safe.get("profile_id")),
        "source_phase": PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE,
        "supervision_phase": PHASE12C_SUPERVISION_PHASE,
        "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
        "grant_status": PHASE12C_GRANT_STATUS,
        "profile_status": PHASE12C_PROFILE_STATUS,
        "capability_label_count": _safe_int(safe.get("capability_label_count")),
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "visual_capture_execution_granted": False,
        "click_automation_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12c_visual_supervision_capability_profile(
    profile: object,
) -> Phase12CVisualSupervisionCapabilityProfileValidationResult:
    """Validate a Phase 12C profile and fail closed on prohibited values."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12c_profile_result(
            ("phase12c_profile_not_object",),
            "malformed",
            rejected_phase12c_visual_supervision_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    errors: list[str] = []
    if PHASE12C_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12c_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12C_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12c_profile_unknown_field")
    if (
        profile.get("visual_supervision_capability_profile_contract_version")
        != PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12c_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND:
        errors.append("phase12c_profile_kind_invalid")
    if _safe_phase12c_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12c_profile_id_invalid")
    if profile.get("source_phase") != PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE:
        errors.append("phase12c_profile_source_phase_invalid")
    errors.extend(_source_record_candidate_errors(profile.get("source_record_candidate")))
    if profile.get("supervision_phase") != PHASE12C_SUPERVISION_PHASE:
        errors.append("phase12c_profile_supervision_phase_invalid")
    if profile.get("authorization_status") != PHASE12C_AUTHORIZATION_STATUS:
        errors.append("phase12c_profile_authorization_status_invalid")
    if profile.get("grant_status") != PHASE12C_GRANT_STATUS:
        errors.append("phase12c_profile_grant_status_invalid")
    if profile.get("profile_status") != PHASE12C_PROFILE_STATUS:
        errors.append("phase12c_profile_status_invalid")
    if profile.get("phase12c_profiles_are_approvals_grants_or_permissions") is not False:
        errors.append("phase12c_profile_approval_grant_or_permission_implied")
    errors.extend(_capability_label_errors(profile.get("capability_labels")))
    if not _is_non_negative_int(profile.get("capability_label_count")):
        errors.append("phase12c_profile_count_invalid")
    elif profile.get("capability_label_count") != len(PHASE12C_ALLOWED_CAPABILITY_LABELS):
        errors.append("phase12c_profile_capability_label_count_invalid")
    if profile.get("jules_review_required_for_validator_or_authorization_semantics") is not True:
        errors.append("phase12c_profile_jules_review_requirement_invalid")
    for field in (
        "visual_capture_execution_granted",
        "clipboard_capture_execution_granted",
        "mic_capture_execution_granted",
        "camera_capture_execution_granted",
        "click_automation_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if profile.get(field) is not False:
            errors.append("phase12c_profile_runtime_implied")
            break
    if profile.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase12c_profile_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase12c_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12c_profile_authorization_wording")
    expected_id = _phase12c_profile_id(profile)
    if not expected_id:
        errors.append("phase12c_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12c_profile_id_invalid")
    if errors:
        return _invalid_phase12c_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12c_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12c_visual_supervision_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12CVisualSupervisionCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12c_visual_supervision_capability_profile() -> dict[str, object]:
    """Return sanitized rejected Phase 12C profile metadata."""

    payload = {
        "visual_supervision_capability_profile_contract_version": (
            PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "profile_id": None,
        "source_phase": PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE,
        "source_record_candidate": _phase12c_source_record_candidate(
            rejected_phase12b_runtime_authorization_record_candidate()
        ),
        "supervision_phase": PHASE12C_SUPERVISION_PHASE,
        "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
        "grant_status": PHASE12C_GRANT_STATUS,
        "profile_status": PHASE12C_PROFILE_STATUS,
        "phase12c_profiles_are_approvals_grants_or_permissions": False,
        "capability_labels": _phase12c_capability_labels(),
        "capability_label_count": len(PHASE12C_ALLOWED_CAPABILITY_LABELS),
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "visual_capture_execution_granted": False,
        "clipboard_capture_execution_granted": False,
        "mic_capture_execution_granted": False,
        "camera_capture_execution_granted": False,
        "click_automation_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    return _finalize_phase12c_visual_supervision_capability_profile(payload)


def phase12d_visual_desktop_consent_gate_requirements(
    *,
    source_charter: Mapping[str, object] | None = None,
    source_record: Mapping[str, object] | None = None,
    source_profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12D visual/desktop consent gate requirements.

    This defines future consent and gate metadata only. It does not satisfy any
    consent gate, grant permission, authorize runtime, or run a capability.
    """

    charter = source_charter or phase12a_runtime_authorization_design_charter()
    charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
    safe_charter = (
        charter_result.sanitized_record
        if charter_result.compatible
        else rejected_phase12a_runtime_authorization_design_charter()
    )
    record = source_record or phase12b_runtime_authorization_record_candidate()
    record_result = validate_phase12b_runtime_authorization_record_candidate(record)
    safe_record = (
        record_result.sanitized_record
        if record_result.compatible
        else rejected_phase12b_runtime_authorization_record_candidate()
    )
    capability_profile = source_profile or phase12c_visual_supervision_capability_profile()
    profile_result = validate_phase12c_visual_supervision_capability_profile(capability_profile)
    safe_profile = (
        profile_result.sanitized_record
        if profile_result.compatible
        else rejected_phase12c_visual_supervision_capability_profile()
    )
    payload = _phase12d_consent_gate_profile_payload(
        safe_charter,
        safe_record,
        safe_profile,
    )
    profile = _finalize_phase12d_visual_desktop_consent_gate_requirements(payload)
    result = validate_phase12d_visual_desktop_consent_gate_requirements(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12d_visual_desktop_consent_gate_requirements()
    )


def phase12d_visual_desktop_consent_gate_requirements_status_summary() -> dict[str, object]:
    """Return compact Phase 12D status safe for public surfaces."""

    profile = phase12d_visual_desktop_consent_gate_requirements()
    result = validate_phase12d_visual_desktop_consent_gate_requirements(profile)
    safe = result.sanitized_record
    return {
        "consent_gate_profile_contract_version": (PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION),
        "consent_gate_profile_id": _safe_phase12d_profile_id(safe.get("consent_gate_profile_id")),
        "source_phase_range": PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE,
        "consent_phase": PHASE12D_CONSENT_PHASE,
        "authorization_status": PHASE12D_AUTHORIZATION_STATUS,
        "grant_status": PHASE12D_GRANT_STATUS,
        "consent_gate_status": PHASE12D_CONSENT_GATE_STATUS,
        "capability_category_count": _safe_int(safe.get("capability_category_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "satisfied_consent_gate_count": 0,
        "passed_consent_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "screen_capture_execution_granted": False,
        "ocr_execution_granted": False,
        "camera_capture_execution_granted": False,
        "microphone_capture_execution_granted": False,
        "clipboard_capture_execution_granted": False,
        "recording_execution_granted": False,
        "click_input_automation_execution_granted": False,
        "overlay_display_execution_granted": False,
        "notification_sending_execution_granted": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12d_visual_desktop_consent_gate_requirements(
    profile: object,
) -> Phase12DConsentGateRequirementsValidationResult:
    """Validate Phase 12D consent requirements and reject active consent/grants."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12d_profile_result(
            ("phase12d_profile_not_object",),
            "malformed",
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    errors: list[str] = []
    if PHASE12D_CONSENT_GATE_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12d_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12D_CONSENT_GATE_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12d_profile_unknown_field")
    if (
        profile.get("consent_gate_profile_contract_version")
        != PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12d_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12D_CONSENT_GATE_PROFILE_KIND:
        errors.append("phase12d_profile_kind_invalid")
    if _safe_phase12d_profile_id(profile.get("consent_gate_profile_id")) != profile.get(
        "consent_gate_profile_id"
    ):
        errors.append("phase12d_profile_id_invalid")
    if profile.get("source_phase_range") != PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE:
        errors.append("phase12d_profile_source_phase_range_invalid")
    errors.extend(_phase12d_source_design_charter_errors(profile.get("source_design_charter")))
    errors.extend(_phase12d_source_record_candidate_errors(profile.get("source_record_candidate")))
    errors.extend(
        _phase12d_source_capability_profile_errors(profile.get("source_capability_profile"))
    )
    if profile.get("consent_phase") != PHASE12D_CONSENT_PHASE:
        errors.append("phase12d_profile_consent_phase_invalid")
    if profile.get("authorization_status") != PHASE12D_AUTHORIZATION_STATUS:
        errors.append("phase12d_profile_authorization_status_invalid")
    if profile.get("grant_status") != PHASE12D_GRANT_STATUS:
        errors.append("phase12d_profile_grant_status_invalid")
    if profile.get("consent_gate_status") != PHASE12D_CONSENT_GATE_STATUS:
        errors.append("phase12d_profile_status_invalid")
    if profile.get("phase12d_satisfies_consent_gates") is not False:
        errors.append("phase12d_profile_consent_gate_satisfaction_implied")
    if profile.get("phase12d_profiles_are_consents_approvals_grants_or_permissions") is not False:
        errors.append("phase12d_profile_consent_approval_grant_permission_implied")
    errors.extend(_phase12d_capability_category_errors(profile.get("capability_categories")))
    errors.extend(_phase12d_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "capability_category_count",
        "required_future_gate_count",
        "satisfied_consent_gate_count",
        "passed_consent_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12d_profile_count_invalid")
            break
    if profile.get("capability_category_count") != len(PHASE12D_CAPABILITY_CATEGORIES):
        errors.append("phase12d_profile_capability_category_count_invalid")
    if profile.get("required_future_gate_count") != len(PHASE12D_REQUIRED_FUTURE_GATES):
        errors.append("phase12d_profile_required_gate_count_invalid")
    if profile.get("satisfied_consent_gate_count") != 0:
        errors.append("phase12d_profile_satisfied_gate_count_invalid")
    if profile.get("passed_consent_gate_count") != 0:
        errors.append("phase12d_profile_passed_gate_count_invalid")
    if profile.get("jules_review_required_for_validator_or_authorization_semantics") is not True:
        errors.append("phase12d_profile_jules_review_requirement_invalid")
    for field in (
        "screen_capture_execution_granted",
        "ocr_execution_granted",
        "camera_capture_execution_granted",
        "microphone_capture_execution_granted",
        "clipboard_capture_execution_granted",
        "recording_execution_granted",
        "click_input_automation_execution_granted",
        "overlay_display_execution_granted",
        "notification_sending_execution_granted",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if profile.get(field) is not False:
            errors.append("phase12d_profile_runtime_implied")
            break
    if profile.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase12d_profile_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase12d_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12d_profile_authorization_wording")
    expected_id = _phase12d_profile_id(profile)
    if not expected_id:
        errors.append("phase12d_profile_payload_not_json")
    elif profile.get("consent_gate_profile_id") != expected_id:
        errors.append("phase12d_profile_id_invalid")
    if errors:
        return _invalid_phase12d_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12d_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12DConsentGateRequirementsValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12d_visual_desktop_consent_gate_requirements() -> dict[str, object]:
    """Return sanitized rejected Phase 12D consent gate requirements."""

    payload = _phase12d_consent_gate_profile_payload(
        rejected_phase12a_runtime_authorization_design_charter(),
        rejected_phase12b_runtime_authorization_record_candidate(),
        rejected_phase12c_visual_supervision_capability_profile(),
    )
    return _finalize_phase12d_visual_desktop_consent_gate_requirements(payload)


def phase12e_physiological_sensor_capability_profile(
    *,
    source_charter: Mapping[str, object] | None = None,
    source_record: Mapping[str, object] | None = None,
    source_consent_gate_profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12E physiological sensor capability profile.

    This defines future physiological sensor labels and gates as metadata only.
    It does not connect to devices, measure, process signals, infer clinical
    meaning, grant permission, authorize runtime, or run a capability.
    """

    charter = source_charter or phase12a_runtime_authorization_design_charter()
    charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
    safe_charter = (
        charter_result.sanitized_record
        if charter_result.compatible
        else rejected_phase12a_runtime_authorization_design_charter()
    )
    record = source_record or phase12b_runtime_authorization_record_candidate()
    record_result = validate_phase12b_runtime_authorization_record_candidate(record)
    safe_record = (
        record_result.sanitized_record
        if record_result.compatible
        else rejected_phase12b_runtime_authorization_record_candidate()
    )
    consent_profile = (
        source_consent_gate_profile or phase12d_visual_desktop_consent_gate_requirements()
    )
    consent_result = validate_phase12d_visual_desktop_consent_gate_requirements(consent_profile)
    safe_consent_profile = (
        consent_result.sanitized_record
        if consent_result.compatible
        else rejected_phase12d_visual_desktop_consent_gate_requirements()
    )
    payload = _phase12e_physiological_sensor_profile_payload(
        safe_charter,
        safe_record,
        safe_consent_profile,
    )
    profile = _finalize_phase12e_physiological_sensor_capability_profile(payload)
    result = validate_phase12e_physiological_sensor_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12e_physiological_sensor_capability_profile()
    )


def phase12e_physiological_sensor_capability_profile_status_summary() -> dict[str, object]:
    """Return compact Phase 12E status safe for public surfaces."""

    profile = phase12e_physiological_sensor_capability_profile()
    result = validate_phase12e_physiological_sensor_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "physiological_sensor_profile_contract_version": (
            PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION
        ),
        "physiological_sensor_profile_id": _safe_phase12e_profile_id(
            safe.get("physiological_sensor_profile_id")
        ),
        "source_phase_range": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE,
        "sensor_phase": PHASE12E_SENSOR_PHASE,
        "authorization_status": PHASE12E_AUTHORIZATION_STATUS,
        "grant_status": PHASE12E_GRANT_STATUS,
        "profile_status": PHASE12E_PROFILE_STATUS,
        "sensor_capability_label_count": _safe_int(safe.get("sensor_capability_label_count")),
        "non_diagnostic_boundary_count": _safe_int(safe.get("non_diagnostic_boundary_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "satisfied_sensor_gate_count": 0,
        "passed_sensor_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "bia_measurement_execution_granted": False,
        "device_connection_execution_granted": False,
        "bluetooth_execution_granted": False,
        "usb_execution_granted": False,
        "cloud_sync_execution_granted": False,
        "acoustic_processing_execution_granted": False,
        "ultrasound_processing_execution_granted": False,
        "medical_inference_execution_granted": False,
        "clinical_recommendation_execution_granted": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12e_physiological_sensor_capability_profile(
    profile: object,
) -> Phase12EPhysiologicalSensorCapabilityProfileValidationResult:
    """Validate Phase 12E profiles and reject active sensor/runtime grants."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12e_profile_result(
            ("phase12e_profile_not_object",),
            "malformed",
            rejected_phase12e_physiological_sensor_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    errors: list[str] = []
    if PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12e_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12e_profile_unknown_field")
    if (
        profile.get("physiological_sensor_profile_contract_version")
        != PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12e_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND:
        errors.append("phase12e_profile_kind_invalid")
    if _safe_phase12e_profile_id(profile.get("physiological_sensor_profile_id")) != profile.get(
        "physiological_sensor_profile_id"
    ):
        errors.append("phase12e_profile_id_invalid")
    if (
        profile.get("source_phase_range")
        != PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE
    ):
        errors.append("phase12e_profile_source_phase_range_invalid")
    errors.extend(_phase12e_source_design_charter_errors(profile.get("source_design_charter")))
    errors.extend(_phase12e_source_record_candidate_errors(profile.get("source_record_candidate")))
    errors.extend(
        _phase12e_source_consent_gate_profile_errors(profile.get("source_consent_gate_profile"))
    )
    errors.extend(
        _phase12e_source_sensor_evidence_boundary_errors(
            profile.get("source_sensor_evidence_boundaries")
        )
    )
    if profile.get("sensor_phase") != PHASE12E_SENSOR_PHASE:
        errors.append("phase12e_profile_sensor_phase_invalid")
    if profile.get("authorization_status") != PHASE12E_AUTHORIZATION_STATUS:
        errors.append("phase12e_profile_authorization_status_invalid")
    if profile.get("grant_status") != PHASE12E_GRANT_STATUS:
        errors.append("phase12e_profile_grant_status_invalid")
    if profile.get("profile_status") != PHASE12E_PROFILE_STATUS:
        errors.append("phase12e_profile_status_invalid")
    if profile.get("phase12e_profiles_are_approvals_grants_or_permissions") is not False:
        errors.append("phase12e_profile_approval_grant_permission_implied")
    if profile.get("phase12e_satisfies_sensor_gates") is not False:
        errors.append("phase12e_profile_sensor_gate_satisfaction_implied")
    errors.extend(_phase12e_sensor_capability_label_errors(profile.get("sensor_capability_labels")))
    errors.extend(
        _phase12e_non_diagnostic_boundary_errors(profile.get("non_diagnostic_boundaries"))
    )
    errors.extend(_phase12e_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "sensor_capability_label_count",
        "non_diagnostic_boundary_count",
        "required_future_gate_count",
        "satisfied_sensor_gate_count",
        "passed_sensor_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12e_profile_count_invalid")
            break
    if profile.get("sensor_capability_label_count") != len(PHASE12E_SENSOR_CAPABILITY_LABELS):
        errors.append("phase12e_profile_sensor_capability_count_invalid")
    if profile.get("non_diagnostic_boundary_count") != len(PHASE12E_NON_DIAGNOSTIC_BOUNDARIES):
        errors.append("phase12e_profile_non_diagnostic_boundary_count_invalid")
    if profile.get("required_future_gate_count") != len(PHASE12E_REQUIRED_FUTURE_GATES):
        errors.append("phase12e_profile_required_gate_count_invalid")
    if profile.get("satisfied_sensor_gate_count") != 0:
        errors.append("phase12e_profile_satisfied_gate_count_invalid")
    if profile.get("passed_sensor_gate_count") != 0:
        errors.append("phase12e_profile_passed_gate_count_invalid")
    if profile.get("jules_review_required_for_validator_or_authorization_semantics") is not True:
        errors.append("phase12e_profile_jules_review_requirement_invalid")
    for field in (
        "bia_measurement_execution_granted",
        "device_connection_execution_granted",
        "bluetooth_execution_granted",
        "usb_execution_granted",
        "cloud_sync_execution_granted",
        "acoustic_processing_execution_granted",
        "ultrasound_processing_execution_granted",
        "medical_inference_execution_granted",
        "clinical_recommendation_execution_granted",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if profile.get(field) is not False:
            errors.append("phase12e_profile_runtime_implied")
            break
    if profile.get("runtime_stage") != REAL_MODE_PHASE_RUNTIME:
        errors.append("phase12e_profile_runtime_stage_invalid")
    if privacy_violations:
        errors.append("phase12e_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12e_profile_authorization_wording")
    expected_id = _phase12e_profile_id(profile)
    if not expected_id:
        errors.append("phase12e_profile_payload_not_json")
    elif profile.get("physiological_sensor_profile_id") != expected_id:
        errors.append("phase12e_profile_id_invalid")
    if errors:
        return _invalid_phase12e_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12e_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12e_physiological_sensor_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12EPhysiologicalSensorCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12e_physiological_sensor_capability_profile() -> dict[str, object]:
    """Return sanitized rejected Phase 12E physiological sensor profile."""

    payload = _phase12e_physiological_sensor_profile_payload(
        rejected_phase12a_runtime_authorization_design_charter(),
        rejected_phase12b_runtime_authorization_record_candidate(),
        rejected_phase12d_visual_desktop_consent_gate_requirements(),
    )
    return _finalize_phase12e_physiological_sensor_capability_profile(payload)


def phase12f_secure_drop_consumer_boundary(
    *,
    source_charter: Mapping[str, object] | None = None,
    source_record: Mapping[str, object] | None = None,
    source_visual_profile: Mapping[str, object] | None = None,
    source_consent_gate_profile: Mapping[str, object] | None = None,
    source_physiological_sensor_profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12F Secure Drop consumer boundary.

    This defines only how Somatic may later reference the canonical content-fabric
    Secure Drop contract for user-selected encrypted artifact transfer. Somatic
    does not implement crypto, transport, stego, keyring/DID, send/receive, UI,
    network calls, authorization grants, or runtime behavior.
    """

    charter = source_charter or phase12a_runtime_authorization_design_charter()
    charter_result = validate_phase12a_runtime_authorization_design_charter(charter)
    safe_charter = (
        charter_result.sanitized_record
        if charter_result.compatible
        else rejected_phase12a_runtime_authorization_design_charter()
    )
    record = source_record or phase12b_runtime_authorization_record_candidate()
    record_result = validate_phase12b_runtime_authorization_record_candidate(record)
    safe_record = (
        record_result.sanitized_record
        if record_result.compatible
        else rejected_phase12b_runtime_authorization_record_candidate()
    )
    visual_profile = source_visual_profile or phase12c_visual_supervision_capability_profile()
    visual_result = validate_phase12c_visual_supervision_capability_profile(visual_profile)
    safe_visual_profile = (
        visual_result.sanitized_record
        if visual_result.compatible
        else rejected_phase12c_visual_supervision_capability_profile()
    )
    consent_profile = (
        source_consent_gate_profile or phase12d_visual_desktop_consent_gate_requirements()
    )
    consent_result = validate_phase12d_visual_desktop_consent_gate_requirements(consent_profile)
    safe_consent_profile = (
        consent_result.sanitized_record
        if consent_result.compatible
        else rejected_phase12d_visual_desktop_consent_gate_requirements()
    )
    physiological_profile = (
        source_physiological_sensor_profile or phase12e_physiological_sensor_capability_profile()
    )
    physiological_result = validate_phase12e_physiological_sensor_capability_profile(
        physiological_profile
    )
    safe_physiological_profile = (
        physiological_result.sanitized_record
        if physiological_result.compatible
        else rejected_phase12e_physiological_sensor_capability_profile()
    )
    payload = _phase12f_secure_drop_consumer_boundary_payload(
        safe_charter,
        safe_record,
        safe_visual_profile,
        safe_consent_profile,
        safe_physiological_profile,
    )
    boundary = _finalize_phase12f_secure_drop_consumer_boundary(payload)
    result = validate_phase12f_secure_drop_consumer_boundary(boundary)
    return boundary if result.compatible else rejected_phase12f_secure_drop_consumer_boundary()


def phase12f_secure_drop_consumer_boundary_status_summary() -> dict[str, object]:
    """Return compact Phase 12F status safe for public surfaces."""

    boundary = phase12f_secure_drop_consumer_boundary()
    result = validate_phase12f_secure_drop_consumer_boundary(boundary)
    safe = result.sanitized_record
    return {
        "secure_drop_consumer_boundary_contract_version": (
            PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION
        ),
        "secure_drop_consumer_boundary_id": _safe_phase12f_boundary_id(
            safe.get("secure_drop_consumer_boundary_id")
        ),
        "source_phase_range": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE,
        "consumer_phase": PHASE12F_CONSUMER_PHASE,
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "canonical_reference": PHASE12F_CANONICAL_REFERENCE,
        "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
        "grant_status": PHASE12F_GRANT_STATUS,
        "boundary_status": PHASE12F_BOUNDARY_STATUS,
        "allowed_future_user_selected_artifact_label_count": _safe_int(
            safe.get("allowed_future_user_selected_artifact_label_count")
        ),
        "prohibited_future_autonomous_source_count": _safe_int(
            safe.get("prohibited_future_autonomous_source_count")
        ),
        "encryption_required": True,
        "concealment_optional": True,
        "concealment_is_security_boundary": False,
        "audit_metadata_only_required": True,
        "jules_security_review_required_for_validator_or_authorization_semantics": True,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "agent_invocation_permitted": False,
        "automation_invocation_permitted": False,
        "filesystem_autoscan_permitted": False,
        "vault_env_secret_access_permitted": False,  # nosec B105
        "crypto_implementation_added": False,
        "transport_implementation_added": False,
        "stego_implementation_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12f_secure_drop_consumer_boundary(
    boundary: object,
) -> Phase12FSecureDropConsumerBoundaryValidationResult:
    """Validate Phase 12F boundaries and reject Secure Drop runtime semantics."""

    if not isinstance(boundary, Mapping):
        return _invalid_phase12f_boundary_result(
            ("phase12f_boundary_not_object",),
            "malformed",
            rejected_phase12f_secure_drop_consumer_boundary(),
        )
    privacy_violations = _privacy_violation_count(boundary)
    authorization_wording = _authorization_wording_count(boundary)
    errors: list[str] = []
    if PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS - set(boundary):
        errors.append("phase12f_boundary_required_field_missing")
    if set(str(key) for key in boundary) - PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS:
        errors.append("phase12f_boundary_unknown_field")
    if (
        boundary.get("secure_drop_consumer_boundary_contract_version")
        != PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION
    ):
        errors.append("phase12f_boundary_contract_version_unsupported")
    if boundary.get("boundary_kind") != PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND:
        errors.append("phase12f_boundary_kind_invalid")
    if _safe_phase12f_boundary_id(boundary.get("secure_drop_consumer_boundary_id")) != boundary.get(
        "secure_drop_consumer_boundary_id"
    ):
        errors.append("phase12f_boundary_id_invalid")
    if (
        boundary.get("source_phase_range")
        != PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE
    ):
        errors.append("phase12f_boundary_source_phase_range_invalid")
    errors.extend(_phase12f_source_design_charter_errors(boundary.get("source_design_charter")))
    errors.extend(_phase12f_source_record_candidate_errors(boundary.get("source_record_candidate")))
    errors.extend(
        _phase12f_source_visual_supervision_profile_errors(
            boundary.get("source_visual_supervision_profile")
        )
    )
    errors.extend(
        _phase12f_source_consent_gate_profile_errors(boundary.get("source_consent_gate_profile"))
    )
    errors.extend(
        _phase12f_source_physiological_sensor_profile_errors(
            boundary.get("source_physiological_sensor_profile")
        )
    )
    errors.extend(
        _phase12f_source_content_fabric_secure_drop_contract_errors(
            boundary.get("source_content_fabric_secure_drop_contract")
        )
    )
    expected = {
        "consumer_phase": PHASE12F_CONSUMER_PHASE,
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "canonical_reference": PHASE12F_CANONICAL_REFERENCE,
        "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
        "grant_status": PHASE12F_GRANT_STATUS,
        "boundary_status": PHASE12F_BOUNDARY_STATUS,
        "encryption_requirement_status": PHASE12F_ENCRYPTION_REQUIREMENT_STATUS,
        "concealment_status": PHASE12F_CONCEALMENT_STATUS,
        "audit_requirement_status": PHASE12F_AUDIT_REQUIREMENT_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if boundary.get(key) != expected_value:
            errors.append("phase12f_boundary_value_invalid")
            break
    if boundary.get("phase12f_implements_secure_drop") is not False:
        errors.append("phase12f_boundary_implementation_implied")
    if boundary.get("phase12f_authorizes_secure_drop") is not False:
        errors.append("phase12f_boundary_authorization_implied")
    if boundary.get("phase12f_profiles_are_approvals_grants_or_permissions") is not False:
        errors.append("phase12f_boundary_approval_grant_permission_implied")
    errors.extend(
        _phase12f_allowed_artifact_label_errors(
            boundary.get("allowed_future_user_selected_artifact_labels")
        )
    )
    errors.extend(
        _phase12f_prohibited_autonomous_source_errors(
            boundary.get("prohibited_future_autonomous_sources")
        )
    )
    for field in (
        "allowed_future_user_selected_artifact_label_count",
        "prohibited_future_autonomous_source_count",
    ):
        if not _is_non_negative_int(boundary.get(field)):
            errors.append("phase12f_boundary_count_invalid")
            break
    if boundary.get("allowed_future_user_selected_artifact_label_count") != len(
        PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS
    ):
        errors.append("phase12f_boundary_artifact_label_count_invalid")
    if boundary.get("prohibited_future_autonomous_source_count") != len(
        PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES
    ):
        errors.append("phase12f_boundary_prohibited_source_count_invalid")
    for field, expected_value in (
        ("encryption_required", True),
        ("concealment_optional", True),
        ("audit_metadata_only_required", True),
        (
            "jules_security_review_required_for_validator_or_authorization_semantics",
            True,
        ),
        ("concealment_is_security_boundary", False),
    ):
        if boundary.get(field) is not expected_value:
            errors.append("phase12f_boundary_requirement_value_invalid")
            break
    for field in (
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "agent_invocation_permitted",
        "automation_invocation_permitted",
        "connector_invocation_permitted",
        "scheduled_task_invocation_permitted",
        "avatar_invocation_permitted",
        "server_endpoint_invocation_permitted",
        "workflow_invocation_permitted",
        "filesystem_autoscan_permitted",
        "vault_env_secret_access_permitted",
        "raw_sensor_capture_attachment_permitted",
        "automatic_document_attachment_permitted",
        "crypto_implementation_added",
        "transport_implementation_added",
        "stego_implementation_added",
        "keyring_implementation_added",
        "did_implementation_added",
        "send_inbox_ui_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "adapter_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if boundary.get(field) is not False:
            errors.append("phase12f_boundary_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12f_boundary_privacy_boundary")
    if authorization_wording:
        errors.append("phase12f_boundary_authorization_wording")
    expected_id = _phase12f_boundary_id(boundary)
    if not expected_id:
        errors.append("phase12f_boundary_payload_not_json")
    elif boundary.get("secure_drop_consumer_boundary_id") != expected_id:
        errors.append("phase12f_boundary_id_invalid")
    if errors:
        return _invalid_phase12f_boundary_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12f_boundary_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12f_secure_drop_consumer_boundary(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12FSecureDropConsumerBoundaryValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(boundary),
    )


def rejected_phase12f_secure_drop_consumer_boundary() -> dict[str, object]:
    """Return sanitized rejected Phase 12F Secure Drop consumer boundary."""

    payload = _phase12f_secure_drop_consumer_boundary_payload(
        rejected_phase12a_runtime_authorization_design_charter(),
        rejected_phase12b_runtime_authorization_record_candidate(),
        rejected_phase12c_visual_supervision_capability_profile(),
        rejected_phase12d_visual_desktop_consent_gate_requirements(),
        rejected_phase12e_physiological_sensor_capability_profile(),
    )
    return _finalize_phase12f_secure_drop_consumer_boundary(payload)


def phase12g_production_readiness_coverage_matrix(
    *,
    source_secure_drop_boundary: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12G production-readiness coverage matrix.

    This maps production-readiness areas to Somatic metadata responsibilities and
    cross-repo owners. It does not implement production infrastructure, runtime
    adapters, device paths, network calls, grants, or real-mode execution.
    """

    secure_drop_boundary = source_secure_drop_boundary or phase12f_secure_drop_consumer_boundary()
    secure_drop_result = validate_phase12f_secure_drop_consumer_boundary(secure_drop_boundary)
    safe_secure_drop_boundary = (
        secure_drop_result.sanitized_record
        if secure_drop_result.compatible
        else rejected_phase12f_secure_drop_consumer_boundary()
    )
    payload = _phase12g_production_readiness_coverage_matrix_payload(
        safe_secure_drop_boundary,
    )
    matrix = _finalize_phase12g_production_readiness_coverage_matrix(payload)
    result = validate_phase12g_production_readiness_coverage_matrix(matrix)
    return matrix if result.compatible else rejected_phase12g_production_readiness_coverage_matrix()


def phase12g_production_readiness_coverage_matrix_status_summary() -> dict[str, object]:
    """Return compact Phase 12G status safe for public surfaces."""

    matrix = phase12g_production_readiness_coverage_matrix()
    result = validate_phase12g_production_readiness_coverage_matrix(matrix)
    safe = result.sanitized_record
    return {
        "production_readiness_matrix_contract_version": (
            PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION
        ),
        "production_readiness_matrix_id": _safe_phase12g_matrix_id(
            safe.get("production_readiness_matrix_id")
        ),
        "source_phase_range": PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE,
        "readiness_phase": PHASE12G_READINESS_PHASE,
        "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
        "grant_status": PHASE12G_GRANT_STATUS,
        "matrix_status": PHASE12G_MATRIX_STATUS,
        "production_readiness_area_count": _safe_int(safe.get("production_readiness_area_count")),
        "somatic_direct_area_count": _safe_int(safe.get("somatic_direct_area_count")),
        "somatic_boundary_only_area_count": _safe_int(safe.get("somatic_boundary_only_area_count")),
        "external_owner_area_count": _safe_int(safe.get("external_owner_area_count")),
        "not_applicable_yet_area_count": _safe_int(safe.get("not_applicable_yet_area_count")),
        "phase12g_makes_somatic_production_ready": False,
        "phase12g_authorizes_runtime": False,
        "phase12g_coverage_labels_are_metadata_only": True,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "security_review_required_before_production_hardening": True,
        "frontend_implementation_added": False,
        "backend_service_added": False,
        "production_api_service_added": False,
        "database_storage_added": False,
        "auth_runtime_added": False,
        "rate_limiting_runtime_added": False,
        "cache_runtime_added": False,
        "cdn_runtime_added": False,
        "load_balancer_runtime_added": False,
        "logging_service_added": False,
        "secrets_backend_runtime_added": False,
        "service_registry_runtime_added": False,
        "deployment_code_added": False,
        "hosting_runtime_added": False,
        "cloud_compute_runtime_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "device_connection_execution_granted": False,
        "sensor_processing_execution_granted": False,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "active_grant_present": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12g_production_readiness_coverage_matrix(
    matrix: object,
) -> Phase12GProductionReadinessCoverageMatrixValidationResult:
    """Validate Phase 12G matrices and reject production/runtime semantics."""

    if not isinstance(matrix, Mapping):
        return _invalid_phase12g_matrix_result(
            ("phase12g_matrix_not_object",),
            "malformed",
            rejected_phase12g_production_readiness_coverage_matrix(),
        )
    privacy_violations = _privacy_violation_count(matrix)
    authorization_wording = _authorization_wording_count(matrix)
    errors: list[str] = []
    if PHASE12G_PRODUCTION_READINESS_MATRIX_REQUIRED_FIELDS - set(matrix):
        errors.append("phase12g_matrix_required_field_missing")
    if set(str(key) for key in matrix) - PHASE12G_PRODUCTION_READINESS_MATRIX_REQUIRED_FIELDS:
        errors.append("phase12g_matrix_unknown_field")
    if (
        matrix.get("production_readiness_matrix_contract_version")
        != PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION
    ):
        errors.append("phase12g_matrix_contract_version_unsupported")
    if matrix.get("matrix_kind") != PHASE12G_PRODUCTION_READINESS_MATRIX_KIND:
        errors.append("phase12g_matrix_kind_invalid")
    if _safe_phase12g_matrix_id(matrix.get("production_readiness_matrix_id")) != matrix.get(
        "production_readiness_matrix_id"
    ):
        errors.append("phase12g_matrix_id_invalid")
    if matrix.get("source_phase_range") != PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE:
        errors.append("phase12g_matrix_source_phase_range_invalid")
    errors.extend(
        _phase12g_source_secure_drop_boundary_errors(
            matrix.get("source_secure_drop_consumer_boundary")
        )
    )
    expected = {
        "readiness_phase": PHASE12G_READINESS_PHASE,
        "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
        "grant_status": PHASE12G_GRANT_STATUS,
        "matrix_status": PHASE12G_MATRIX_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if matrix.get(key) != expected_value:
            errors.append("phase12g_matrix_value_invalid")
            break
    errors.extend(_phase12g_status_label_errors(matrix.get("status_labels")))
    errors.extend(_phase12g_area_entry_errors(matrix.get("production_readiness_areas")))
    for field in (
        "status_label_count",
        "production_readiness_area_count",
        "somatic_direct_area_count",
        "somatic_boundary_only_area_count",
        "external_owner_area_count",
        "not_applicable_yet_area_count",
    ):
        if not _is_non_negative_int(matrix.get(field)):
            errors.append("phase12g_matrix_count_invalid")
            break
    expected_counts = _phase12g_responsibility_counts()
    if matrix.get("status_label_count") != len(PHASE12G_STATUS_LABELS):
        errors.append("phase12g_matrix_status_label_count_invalid")
    if matrix.get("production_readiness_area_count") != len(PHASE12G_PRODUCTION_READINESS_AREAS):
        errors.append("phase12g_matrix_area_count_invalid")
    if matrix.get("somatic_direct_area_count") != expected_counts["direct"]:
        errors.append("phase12g_matrix_direct_count_invalid")
    if matrix.get("somatic_boundary_only_area_count") != expected_counts["boundary-only"]:
        errors.append("phase12g_matrix_boundary_count_invalid")
    if matrix.get("external_owner_area_count") != expected_counts["external-owner"]:
        errors.append("phase12g_matrix_external_count_invalid")
    if matrix.get("not_applicable_yet_area_count") != expected_counts["not-applicable-yet"]:
        errors.append("phase12g_matrix_not_applicable_count_invalid")
    if matrix.get("phase12g_makes_somatic_production_ready") is not False:
        errors.append("phase12g_matrix_production_ready_claim_implied")
    if matrix.get("phase12g_authorizes_runtime") is not False:
        errors.append("phase12g_matrix_runtime_authorization_implied")
    if matrix.get("phase12g_coverage_labels_are_metadata_only") is not True:
        errors.append("phase12g_matrix_metadata_only_invalid")
    for field, expected_value in (
        ("jules_review_required_for_validator_or_authorization_semantics", True),
        ("security_review_required_before_production_hardening", True),
    ):
        if matrix.get(field) is not expected_value:
            errors.append("phase12g_matrix_review_requirement_invalid")
            break
    for field in (
        "frontend_implementation_added",
        "backend_service_added",
        "production_api_service_added",
        "database_storage_added",
        "auth_runtime_added",
        "rate_limiting_runtime_added",
        "cache_runtime_added",
        "cdn_runtime_added",
        "load_balancer_runtime_added",
        "logging_service_added",
        "secrets_backend_runtime_added",
        "service_registry_runtime_added",
        "deployment_code_added",
        "hosting_runtime_added",
        "cloud_compute_runtime_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "device_connection_execution_granted",
        "sensor_processing_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "execution_permitted",
        "real_mode_runtime_enabled",
    ):
        if matrix.get(field) is not False:
            errors.append("phase12g_matrix_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12g_matrix_privacy_boundary")
    if authorization_wording:
        errors.append("phase12g_matrix_authorization_wording")
    expected_id = _phase12g_matrix_id(matrix)
    if not expected_id:
        errors.append("phase12g_matrix_payload_not_json")
    elif matrix.get("production_readiness_matrix_id") != expected_id:
        errors.append("phase12g_matrix_id_invalid")
    if errors:
        return _invalid_phase12g_matrix_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12g_matrix_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12g_production_readiness_coverage_matrix(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12GProductionReadinessCoverageMatrixValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(matrix),
    )


def rejected_phase12g_production_readiness_coverage_matrix() -> dict[str, object]:
    """Return sanitized rejected Phase 12G production-readiness matrix."""

    payload = _phase12g_production_readiness_coverage_matrix_payload(
        rejected_phase12f_secure_drop_consumer_boundary(),
    )
    return _finalize_phase12g_production_readiness_coverage_matrix(payload)


def phase12h_somatic_standalone_production_readiness_ownership_map(
    *,
    source_production_readiness_matrix: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the Phase 12H standalone ownership and optional integration map.

    This maps every Phase 12G production-readiness area to Somatic-owned
    standalone responsibilities. Optional repo-family integrations are metadata
    only and never replace Somatic's standalone path.
    """

    source_matrix = source_production_readiness_matrix or (
        phase12g_production_readiness_coverage_matrix()
    )
    source_result = validate_phase12g_production_readiness_coverage_matrix(source_matrix)
    safe_source_matrix = (
        source_result.sanitized_record
        if source_result.compatible
        else rejected_phase12g_production_readiness_coverage_matrix()
    )
    payload = _phase12h_standalone_ownership_matrix_payload(safe_source_matrix)
    matrix = _finalize_phase12h_standalone_ownership_matrix(payload)
    result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(matrix)
    return (
        matrix
        if result.compatible
        else rejected_phase12h_somatic_standalone_production_readiness_ownership_map()
    )


def phase12h_somatic_standalone_production_readiness_ownership_map_status_summary():
    """Return compact Phase 12H status safe for public surfaces."""

    matrix = phase12h_somatic_standalone_production_readiness_ownership_map()
    result = validate_phase12h_somatic_standalone_production_readiness_ownership_map(matrix)
    safe = result.sanitized_record
    return {
        "standalone_ownership_matrix_contract_version": (
            PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION
        ),
        "standalone_ownership_matrix_id": _safe_phase12h_matrix_id(
            safe.get("standalone_ownership_matrix_id")
        ),
        "source_phase": PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE,
        "readiness_phase": PHASE12H_READINESS_PHASE,
        "authorization_status": PHASE12H_AUTHORIZATION_STATUS,
        "grant_status": PHASE12H_GRANT_STATUS,
        "matrix_status": PHASE12H_MATRIX_STATUS,
        "standalone_ownership_entry_count": _safe_int(safe.get("standalone_ownership_entry_count")),
        "optional_integration_peer_count": _safe_int(safe.get("optional_integration_peer_count")),
        "somatic_standalone_area_count": _safe_int(safe.get("somatic_standalone_area_count")),
        "repo_production_ready_count": 0,
        "phase12h_marks_somatic_production_ready": False,
        "phase12h_authorizes_runtime": False,
        "somatic_standalone_ownership_retained": True,
        "external_integrations_optional": True,
        "optional_peer_labels_are_integration_metadata_only": True,
        "external_repo_integration_replaces_somatic_standalone_path": False,
        "cross_repo_mutation_permitted": False,
        "external_repo_tasks_executed_by_somatic": False,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "security_review_required_before_production_hardening": True,
        "frontend_implementation_added": False,
        "backend_service_added": False,
        "production_api_service_added": False,
        "database_storage_added": False,
        "auth_runtime_added": False,
        "rate_limiting_runtime_added": False,
        "cache_runtime_added": False,
        "cdn_runtime_added": False,
        "load_balancer_runtime_added": False,
        "logging_service_added": False,
        "secrets_backend_runtime_added": False,
        "service_registry_runtime_added": False,
        "service_discovery_runtime_added": False,
        "deployment_code_added": False,
        "hosting_runtime_added": False,
        "cloud_compute_runtime_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "device_connection_execution_granted": False,
        "sensor_processing_execution_granted": False,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "active_grant_present": False,
        "real_mode_authorization_added": False,
        "production_ready": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12h_somatic_standalone_production_readiness_ownership_map(
    matrix: object,
) -> Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult:
    """Validate Phase 12H maps and reject dependency/runtime semantics."""

    if not isinstance(matrix, Mapping):
        return _invalid_phase12h_ownership_map_result(
            ("phase12h_ownership_map_not_object",),
            "malformed",
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
        )
    privacy_violations = _privacy_violation_count(matrix)
    authorization_wording = _authorization_wording_count(matrix)
    standalone_contradictions = _phase12h_standalone_contradiction_count(matrix)
    errors: list[str] = []
    if PHASE12H_STANDALONE_OWNERSHIP_MATRIX_REQUIRED_FIELDS - set(matrix):
        errors.append("phase12h_ownership_map_required_field_missing")
    if set(str(key) for key in matrix) - PHASE12H_STANDALONE_OWNERSHIP_MATRIX_REQUIRED_FIELDS:
        errors.append("phase12h_ownership_map_unknown_field")
    if (
        matrix.get("standalone_ownership_matrix_contract_version")
        != PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION
    ):
        errors.append("phase12h_ownership_map_contract_version_unsupported")
    if matrix.get("matrix_kind") != PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND:
        errors.append("phase12h_ownership_map_kind_invalid")
    if _safe_phase12h_matrix_id(matrix.get("standalone_ownership_matrix_id")) != matrix.get(
        "standalone_ownership_matrix_id"
    ):
        errors.append("phase12h_ownership_map_id_invalid")
    expected = {
        "source_phase": PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE,
        "readiness_phase": PHASE12H_READINESS_PHASE,
        "authorization_status": PHASE12H_AUTHORIZATION_STATUS,
        "grant_status": PHASE12H_GRANT_STATUS,
        "matrix_status": PHASE12H_MATRIX_STATUS,
        "standalone_ui_statement": PHASE12H_STANDALONE_UI_STATEMENT,
        "locus_optional_ui_statement": PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT,
        "peer_integration_statement": PHASE12H_PEER_INTEGRATION_STATEMENT,
        "secure_drop_statement": PHASE12H_SECURE_DROP_STATEMENT,
        "phase12h_non_authorization_statement": PHASE12H_NON_AUTHORIZATION_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if matrix.get(key) != expected_value:
            errors.append("phase12h_ownership_map_value_invalid")
            break
    errors.extend(
        _phase12h_source_production_readiness_matrix_errors(
            matrix.get("source_production_readiness_coverage_matrix")
        )
    )
    errors.extend(_phase12h_status_label_errors(matrix.get("status_labels")))
    errors.extend(
        _phase12h_standalone_ownership_entry_errors(matrix.get("standalone_ownership_entries"))
    )
    for field in (
        "status_label_count",
        "standalone_ownership_entry_count",
        "optional_integration_peer_count",
        "somatic_standalone_area_count",
        "repo_production_ready_count",
    ):
        if not _is_non_negative_int(matrix.get(field)):
            errors.append("phase12h_ownership_map_count_invalid")
            break
    if matrix.get("status_label_count") != len(PHASE12H_STATUS_LABELS):
        errors.append("phase12h_ownership_map_status_label_count_invalid")
    if matrix.get("standalone_ownership_entry_count") != len(PHASE12H_SOMATIC_STANDALONE_AREAS):
        errors.append("phase12h_ownership_map_entry_count_invalid")
    if matrix.get("optional_integration_peer_count") != _phase12h_optional_peer_count():
        errors.append("phase12h_ownership_map_peer_count_invalid")
    if matrix.get("somatic_standalone_area_count") != len(PHASE12G_PRODUCTION_READINESS_AREAS):
        errors.append("phase12h_ownership_map_somatic_area_count_invalid")
    if matrix.get("repo_production_ready_count") != 0:
        errors.append("phase12h_ownership_map_repo_production_ready_count_invalid")
    for field, expected_value in (
        ("phase12h_marks_somatic_production_ready", False),
        ("phase12h_authorizes_runtime", False),
        ("somatic_standalone_ownership_retained", True),
        ("external_integrations_optional", True),
        ("optional_peer_labels_are_integration_metadata_only", True),
        ("external_repo_integration_replaces_somatic_standalone_path", False),
        ("cross_repo_mutation_permitted", False),
        ("external_repo_tasks_executed_by_somatic", False),
    ):
        if matrix.get(field) is not expected_value:
            errors.append("phase12h_ownership_map_semantics_invalid")
            break
    for field in _phase12h_runtime_false_fields():
        if matrix.get(field) is not False:
            errors.append("phase12h_ownership_map_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12h_ownership_map_privacy_boundary")
    if authorization_wording:
        errors.append("phase12h_ownership_map_authorization_wording")
    if standalone_contradictions:
        errors.append("phase12h_ownership_map_standalone_ownership_contradiction")
    expected_id = _phase12h_matrix_id(matrix)
    if not expected_id:
        errors.append("phase12h_ownership_map_payload_not_json")
    elif matrix.get("standalone_ownership_matrix_id") != expected_id:
        errors.append("phase12h_ownership_map_id_invalid")
    if errors:
        return _invalid_phase12h_ownership_map_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12h_ownership_map_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(matrix),
    )


def rejected_phase12h_somatic_standalone_production_readiness_ownership_map() -> dict[str, object]:
    """Return sanitized rejected Phase 12H standalone ownership map."""

    payload = _phase12h_standalone_ownership_matrix_payload(
        rejected_phase12g_production_readiness_coverage_matrix(),
    )
    return _finalize_phase12h_standalone_ownership_matrix(payload)


def phase12i_integrative_herbal_nutrition_knowledge_capability_profile() -> dict[str, object]:
    """Return the Phase 12I integrative/herbal/nutrition knowledge profile.

    The profile only names future knowledge and source classes. It is not
    advice, diagnosis, treatment planning, dosing, nutrition prescription, or
    runtime authorization.
    """

    source_references = _phase12i_source_phase_references(
        phase12a_runtime_authorization_design_charter(),
        phase12b_runtime_authorization_record_candidate(),
        phase12c_visual_supervision_capability_profile(),
        phase12d_visual_desktop_consent_gate_requirements(),
        phase12e_physiological_sensor_capability_profile(),
        phase12f_secure_drop_consumer_boundary(),
        phase12g_production_readiness_coverage_matrix(),
        phase12h_somatic_standalone_production_readiness_ownership_map(),
    )
    payload = _phase12i_knowledge_capability_profile_payload(source_references)
    profile = _finalize_phase12i_knowledge_capability_profile(payload)
    result = validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile()
    )


def phase12i_integrative_herbal_nutrition_knowledge_capability_profile_status_summary():
    """Return compact Phase 12I status safe for public surfaces."""

    profile = phase12i_integrative_herbal_nutrition_knowledge_capability_profile()
    result = validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "integrative_herbal_nutrition_profile_contract_version": (
            PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12i_profile_id(safe.get("profile_id")),
        "source_phase_range": PHASE12I_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12I_CAPABILITY_PHASE,
        "authorization_status": PHASE12I_AUTHORIZATION_STATUS,
        "grant_status": PHASE12I_GRANT_STATUS,
        "profile_status": PHASE12I_PROFILE_STATUS,
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "user_preference_mode_count": _safe_int(safe.get("user_preference_mode_count")),
        "specialist_profile_label_count": _safe_int(safe.get("specialist_profile_label_count")),
        "source_class_label_count": _safe_int(safe.get("source_class_label_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "medical_safety_review_required": True,
        "phase12i_provides_medical_advice": False,
        "phase12i_authorizes_runtime": False,
        "phase12i_suppresses_safety_warnings": False,
        "phase12i_claims_western_medicine_invalid": False,
        "phase12i_claims_natural_remedies_safe_by_default": False,
        "phase12i_claims_food_cures_disease": False,
        "emergency_escalation_preserved": True,
        "contraindication_warnings_preserved": True,
        "medication_interaction_warnings_preserved": True,
        "pregnancy_liver_kidney_cardiac_risk_warnings_preserved": True,
        "eating_disorder_risk_warnings_preserved": True,
        "toxicity_warnings_preserved": True,
        "contamination_adulteration_warnings_preserved": True,
        **{field: False for field in _phase12i_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(
    profile: object,
) -> Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult:
    """Validate Phase 12I profiles and reject medical/runtime semantics."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12i_profile_result(
            ("phase12i_profile_not_object",),
            "malformed",
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    unsafe_semantics = _phase12i_unsafe_semantics_count(profile)
    errors: list[str] = []
    if PHASE12I_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12i_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12I_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12i_profile_unknown_field")
    if (
        profile.get("integrative_herbal_nutrition_profile_contract_version")
        != PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12i_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND:
        errors.append("phase12i_profile_kind_invalid")
    if _safe_phase12i_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12i_profile_id_invalid")
    expected = {
        "source_phase_range": PHASE12I_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12I_CAPABILITY_PHASE,
        "authorization_status": PHASE12I_AUTHORIZATION_STATUS,
        "grant_status": PHASE12I_GRANT_STATUS,
        "profile_status": PHASE12I_PROFILE_STATUS,
        "medical_boundary_statement": PHASE12I_MEDICAL_BOUNDARY_STATEMENT,
        "western_medicine_boundary_statement": PHASE12I_WESTERN_MEDICINE_STATEMENT,
        "natural_remedy_boundary_statement": PHASE12I_NATURAL_REMEDY_STATEMENT,
        "food_cure_boundary_statement": PHASE12I_FOOD_CURE_STATEMENT,
        "safety_warning_preservation_statement": PHASE12I_SAFETY_WARNING_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if profile.get(key) != expected_value:
            errors.append("phase12i_profile_value_invalid")
            break
    errors.extend(_phase12i_source_reference_errors(profile.get("source_phase_references")))
    errors.extend(_phase12i_status_label_errors(profile.get("status_labels")))
    errors.extend(_phase12i_user_preference_mode_errors(profile.get("user_preference_modes")))
    errors.extend(_phase12i_specialist_profile_errors(profile.get("specialist_profile_labels")))
    errors.extend(_phase12i_source_class_errors(profile.get("source_class_labels")))
    errors.extend(_phase12i_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "user_preference_mode_count",
        "specialist_profile_label_count",
        "source_class_label_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12i_profile_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": len(PHASE12I_SOURCE_REFERENCE_PHASES),
        "status_label_count": len(PHASE12I_STATUS_LABELS),
        "user_preference_mode_count": len(PHASE12I_USER_PREFERENCE_MODES),
        "specialist_profile_label_count": len(PHASE12I_SPECIALIST_PROFILE_LABELS),
        "source_class_label_count": len(PHASE12I_SOURCE_CLASS_LABELS),
        "required_future_gate_count": len(PHASE12I_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if profile.get(key) != expected_value:
            errors.append("phase12i_profile_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("medical_safety_review_required", True),
        ("jules_human_review_required_for_validator_or_medical_safety_semantics", True),
        ("phase12i_provides_medical_advice", False),
        ("phase12i_authorizes_runtime", False),
        ("phase12i_suppresses_safety_warnings", False),
        ("phase12i_claims_western_medicine_invalid", False),
        ("phase12i_claims_natural_remedies_safe_by_default", False),
        ("phase12i_claims_food_cures_disease", False),
        ("emergency_escalation_preserved", True),
        ("contraindication_warnings_preserved", True),
        ("medication_interaction_warnings_preserved", True),
        ("pregnancy_liver_kidney_cardiac_risk_warnings_preserved", True),
        ("eating_disorder_risk_warnings_preserved", True),
        ("toxicity_warnings_preserved", True),
        ("contamination_adulteration_warnings_preserved", True),
    ):
        if profile.get(field) is not expected_value:
            errors.append("phase12i_profile_safety_semantics_invalid")
            break
    for field in _phase12i_runtime_false_fields():
        if profile.get(field) is not False:
            errors.append("phase12i_profile_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12i_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12i_profile_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12i_profile_unsafe_medical_or_runtime_semantics")
    expected_id = _phase12i_profile_id(profile)
    if not expected_id:
        errors.append("phase12i_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12i_profile_id_invalid")
    if errors:
        return _invalid_phase12i_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12i_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile():
    """Return sanitized rejected Phase 12I knowledge profile."""

    payload = _phase12i_knowledge_capability_profile_payload(
        _phase12i_source_phase_references(
            rejected_phase12a_runtime_authorization_design_charter(),
            rejected_phase12b_runtime_authorization_record_candidate(),
            rejected_phase12c_visual_supervision_capability_profile(),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            rejected_phase12e_physiological_sensor_capability_profile(),
            rejected_phase12f_secure_drop_consumer_boundary(),
            rejected_phase12g_production_readiness_coverage_matrix(),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
        )
    )
    return _finalize_phase12i_knowledge_capability_profile(payload)


def phase12k_external_compute_quantum_backend_capability_profile() -> dict[str, object]:
    """Return the Phase 12K external compute and quantum backend profile.

    The profile only names future backend and workload classes. It performs no
    provider calls, SDK execution, simulator execution, spending, credential
    loading, health-data processing, medical advice, or runtime authorization.
    """

    source_references = _phase12k_source_phase_references(
        phase12a_runtime_authorization_design_charter(),
        phase12b_runtime_authorization_record_candidate(),
        phase12c_visual_supervision_capability_profile(),
        phase12d_visual_desktop_consent_gate_requirements(),
        phase12e_physiological_sensor_capability_profile(),
        phase12f_secure_drop_consumer_boundary(),
        phase12g_production_readiness_coverage_matrix(),
        phase12h_somatic_standalone_production_readiness_ownership_map(),
        phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
    )
    payload = _phase12k_external_compute_quantum_profile_payload(source_references)
    profile = _finalize_phase12k_external_compute_quantum_profile(payload)
    result = validate_phase12k_external_compute_quantum_backend_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12k_external_compute_quantum_backend_capability_profile()
    )


def phase12k_external_compute_quantum_backend_capability_profile_status_summary():
    """Return compact Phase 12K status safe for public surfaces."""

    profile = phase12k_external_compute_quantum_backend_capability_profile()
    result = validate_phase12k_external_compute_quantum_backend_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "external_compute_quantum_profile_contract_version": (
            PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12k_profile_id(safe.get("profile_id")),
        "source_phase_range": PHASE12K_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12K_CAPABILITY_PHASE,
        "authorization_status": PHASE12K_AUTHORIZATION_STATUS,
        "grant_status": PHASE12K_GRANT_STATUS,
        "profile_status": PHASE12K_PROFILE_STATUS,
        "credential_policy": PHASE12K_CREDENTIAL_POLICY,
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "backend_option_count": _safe_int(safe.get("backend_option_count")),
        "workload_class_count": _safe_int(safe.get("workload_class_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "human_approval_required": True,
        "cost_guard_required": True,
        "private_health_data_allowed": False,
        "clinical_decision_support_allowed": False,
        "diagnosis_or_treatment_allowed": False,
        "phase12k_authorizes_runtime": False,
        "phase12k_allows_external_compute_execution": False,
        "phase12k_allows_quantum_backend_execution": False,
        "phase12k_allows_private_health_data_processing": False,
        "phase12k_provides_medical_advice": False,
        "phase12k_allows_diagnosis_or_treatment": False,
        **{field: False for field in _phase12k_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12k_external_compute_quantum_backend_capability_profile(
    profile: object,
) -> Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult:
    """Validate Phase 12K profiles and reject compute/runtime semantics."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12k_profile_result(
            ("phase12k_profile_not_object",),
            "malformed",
            rejected_phase12k_external_compute_quantum_backend_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    unsafe_semantics = _phase12k_unsafe_semantics_count(profile)
    errors: list[str] = []
    if PHASE12K_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12k_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12K_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12k_profile_unknown_field")
    if (
        profile.get("external_compute_quantum_profile_contract_version")
        != PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12k_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND:
        errors.append("phase12k_profile_kind_invalid")
    if _safe_phase12k_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12k_profile_id_invalid")
    expected = {
        "source_phase_range": PHASE12K_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12K_CAPABILITY_PHASE,
        "authorization_status": PHASE12K_AUTHORIZATION_STATUS,
        "grant_status": PHASE12K_GRANT_STATUS,
        "profile_status": PHASE12K_PROFILE_STATUS,
        "credential_policy": PHASE12K_CREDENTIAL_POLICY,
        "compute_boundary_statement": PHASE12K_COMPUTE_BOUNDARY_STATEMENT,
        "medical_boundary_statement": PHASE12K_MEDICAL_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if profile.get(key) != expected_value:
            errors.append("phase12k_profile_value_invalid")
            break
    errors.extend(_phase12k_source_reference_errors(profile.get("source_phase_references")))
    errors.extend(_phase12k_status_label_errors(profile.get("status_labels")))
    errors.extend(_phase12k_backend_option_errors(profile.get("backend_options")))
    errors.extend(_phase12k_workload_class_errors(profile.get("workload_classes")))
    errors.extend(_phase12k_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "backend_option_count",
        "workload_class_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12k_profile_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": len(PHASE12K_SOURCE_REFERENCE_PHASES),
        "status_label_count": len(PHASE12K_STATUS_LABELS),
        "backend_option_count": len(PHASE12K_BACKEND_OPTION_LABELS),
        "workload_class_count": len(PHASE12K_WORKLOAD_CLASSES),
        "required_future_gate_count": len(PHASE12K_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if profile.get(key) != expected_value:
            errors.append("phase12k_profile_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("security_review_required", True),
        ("medical_safety_review_required", True),
        ("jules_human_review_required_for_validator_or_medical_safety_semantics", True),
        ("human_approval_required", True),
        ("cost_guard_required", True),
        ("private_health_data_allowed", False),
        ("clinical_decision_support_allowed", False),
        ("diagnosis_or_treatment_allowed", False),
        ("phase12k_authorizes_runtime", False),
        ("phase12k_allows_external_compute_execution", False),
        ("phase12k_allows_quantum_backend_execution", False),
        ("phase12k_allows_private_health_data_processing", False),
        ("phase12k_provides_medical_advice", False),
        ("phase12k_allows_diagnosis_or_treatment", False),
    ):
        if profile.get(field) is not expected_value:
            errors.append("phase12k_profile_safety_semantics_invalid")
            break
    for field in _phase12k_runtime_false_fields():
        if profile.get(field) is not False:
            errors.append("phase12k_profile_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12k_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12k_profile_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12k_profile_unsafe_compute_or_medical_semantics")
    expected_id = _phase12k_profile_id(profile)
    if not expected_id:
        errors.append("phase12k_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12k_profile_id_invalid")
    if errors:
        return _invalid_phase12k_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12k_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12k_external_compute_quantum_backend_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12k_external_compute_quantum_backend_capability_profile():
    """Return sanitized rejected Phase 12K external compute profile."""

    payload = _phase12k_external_compute_quantum_profile_payload(
        _phase12k_source_phase_references(
            rejected_phase12a_runtime_authorization_design_charter(),
            rejected_phase12b_runtime_authorization_record_candidate(),
            rejected_phase12c_visual_supervision_capability_profile(),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            rejected_phase12e_physiological_sensor_capability_profile(),
            rejected_phase12f_secure_drop_consumer_boundary(),
            rejected_phase12g_production_readiness_coverage_matrix(),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
        )
    )
    return _finalize_phase12k_external_compute_quantum_profile(payload)


def phase12l_fabric_interop_a2a_audit_boundary_capability_profile() -> dict[str, object]:
    """Return the Phase 12L fabric interop and A2A audit-boundary profile.

    The profile only names future shared fabric, A2A, MCP, and Secure Drop
    boundary requirements. It implements no codecs, transport, connector pack
    install, MCP server or client, Secure Drop send/receive, credential access,
    provider call, network call, cross-repo mutation, or runtime authorization.
    """

    source_references = _phase12l_source_phase_references(
        phase12a_runtime_authorization_design_charter(),
        phase12b_runtime_authorization_record_candidate(),
        phase12c_visual_supervision_capability_profile(),
        phase12d_visual_desktop_consent_gate_requirements(),
        phase12e_physiological_sensor_capability_profile(),
        phase12f_secure_drop_consumer_boundary(),
        phase12g_production_readiness_coverage_matrix(),
        phase12h_somatic_standalone_production_readiness_ownership_map(),
        phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
        phase12k_external_compute_quantum_backend_capability_profile(),
    )
    payload = _phase12l_fabric_interop_a2a_audit_profile_payload(source_references)
    profile = _finalize_phase12l_fabric_interop_a2a_audit_profile(payload)
    result = validate_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile()
    )


def phase12l_fabric_interop_a2a_audit_boundary_capability_profile_status_summary():
    """Return compact Phase 12L status safe for public surfaces."""

    profile = phase12l_fabric_interop_a2a_audit_boundary_capability_profile()
    result = validate_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "fabric_interop_a2a_audit_profile_contract_version": (
            PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12l_profile_id(safe.get("profile_id")),
        "source_phase_range": PHASE12L_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12L_CAPABILITY_PHASE,
        "authorization_status": PHASE12L_AUTHORIZATION_STATUS,
        "grant_status": PHASE12L_GRANT_STATUS,
        "profile_status": PHASE12L_PROFILE_STATUS,
        "fabric_interop_status": PHASE12L_FABRIC_INTEROP_STATUS,
        "message_codec_status": PHASE12L_MESSAGE_CODEC_STATUS,
        "a2a_transport_status": PHASE12L_A2A_TRANSPORT_STATUS,
        "mcp_interop_status": PHASE12L_MCP_INTEROP_STATUS,
        "secure_drop_status": PHASE12L_SECURE_DROP_STATUS,
        "credential_policy": PHASE12L_CREDENTIAL_POLICY,
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "fabric_capability_label_count": _safe_int(safe.get("fabric_capability_label_count")),
        "forbidden_out_of_scope_label_count": _safe_int(
            safe.get("forbidden_out_of_scope_label_count")
        ),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "fabric_safety_review_required": True,
        "plaintext_json_default_future_requirement_only": True,
        "decode_to_audit_future_requirement_only": True,
        "secure_drop_user_initiated_boundary_only": True,
        "opaque_traffic_allowed": False,
        "untrusted_content_executable": False,
        "cross_repo_mutation_allowed": False,
        "phase12l_authorizes_runtime": False,
        "phase12l_allows_fabric_runtime": False,
        "phase12l_allows_a2a_transport": False,
        "phase12l_allows_mcp_runtime": False,
        "phase12l_allows_secure_drop_send_receive": False,
        **{field: False for field in _phase12l_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(
    profile: object,
) -> Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult:
    """Validate Phase 12L profiles and reject fabric/runtime semantics."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12l_profile_result(
            ("phase12l_profile_not_object",),
            "malformed",
            rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    unsafe_semantics = _phase12l_unsafe_semantics_count(profile)
    errors: list[str] = []
    if PHASE12L_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12l_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12L_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12l_profile_unknown_field")
    if (
        profile.get("fabric_interop_a2a_audit_profile_contract_version")
        != PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12l_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND:
        errors.append("phase12l_profile_kind_invalid")
    if _safe_phase12l_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12l_profile_id_invalid")
    expected = {
        "source_phase_range": PHASE12L_SOURCE_PHASE_RANGE,
        "capability_phase": PHASE12L_CAPABILITY_PHASE,
        "authorization_status": PHASE12L_AUTHORIZATION_STATUS,
        "grant_status": PHASE12L_GRANT_STATUS,
        "profile_status": PHASE12L_PROFILE_STATUS,
        "fabric_interop_status": PHASE12L_FABRIC_INTEROP_STATUS,
        "message_codec_status": PHASE12L_MESSAGE_CODEC_STATUS,
        "a2a_transport_status": PHASE12L_A2A_TRANSPORT_STATUS,
        "mcp_interop_status": PHASE12L_MCP_INTEROP_STATUS,
        "secure_drop_status": PHASE12L_SECURE_DROP_STATUS,
        "credential_policy": PHASE12L_CREDENTIAL_POLICY,
        "fabric_boundary_statement": PHASE12L_FABRIC_BOUNDARY_STATEMENT,
        "audit_boundary_statement": PHASE12L_AUDIT_BOUNDARY_STATEMENT,
        "secure_drop_boundary_statement": PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if profile.get(key) != expected_value:
            errors.append("phase12l_profile_value_invalid")
            break
    errors.extend(_phase12l_source_reference_errors(profile.get("source_phase_references")))
    errors.extend(_phase12l_status_label_errors(profile.get("status_labels")))
    errors.extend(_phase12l_fabric_capability_label_errors(profile.get("fabric_capability_labels")))
    errors.extend(
        _phase12l_forbidden_out_of_scope_label_errors(profile.get("forbidden_out_of_scope_labels"))
    )
    errors.extend(_phase12l_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "fabric_capability_label_count",
        "forbidden_out_of_scope_label_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12l_profile_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": len(PHASE12L_SOURCE_REFERENCE_PHASES),
        "status_label_count": len(PHASE12L_STATUS_LABELS),
        "fabric_capability_label_count": len(PHASE12L_FABRIC_CAPABILITY_LABELS),
        "forbidden_out_of_scope_label_count": len(PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS),
        "required_future_gate_count": len(PHASE12L_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if profile.get(key) != expected_value:
            errors.append("phase12l_profile_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("security_review_required", True),
        ("fabric_safety_review_required", True),
        ("jules_human_review_required_for_validator_or_fabric_safety_semantics", True),
        ("plaintext_json_default_future_requirement_only", True),
        ("decode_to_audit_future_requirement_only", True),
        ("secure_drop_user_initiated_boundary_only", True),
        ("opaque_traffic_allowed", False),
        ("untrusted_content_executable", False),
        ("cross_repo_mutation_allowed", False),
        ("phase12l_authorizes_runtime", False),
        ("phase12l_allows_fabric_runtime", False),
        ("phase12l_allows_a2a_transport", False),
        ("phase12l_allows_mcp_runtime", False),
        ("phase12l_allows_secure_drop_send_receive", False),
    ):
        if profile.get(field) is not expected_value:
            errors.append("phase12l_profile_safety_semantics_invalid")
            break
    for field in _phase12l_runtime_false_fields():
        if profile.get(field) is not False:
            errors.append("phase12l_profile_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12l_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12l_profile_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12l_profile_unsafe_fabric_semantics")
    expected_id = _phase12l_profile_id(profile)
    if not expected_id:
        errors.append("phase12l_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12l_profile_id_invalid")
    if errors:
        return _invalid_phase12l_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12l_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile():
    """Return sanitized rejected Phase 12L fabric boundary profile."""

    payload = _phase12l_fabric_interop_a2a_audit_profile_payload(
        _phase12l_source_phase_references(
            rejected_phase12a_runtime_authorization_design_charter(),
            rejected_phase12b_runtime_authorization_record_candidate(),
            rejected_phase12c_visual_supervision_capability_profile(),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            rejected_phase12e_physiological_sensor_capability_profile(),
            rejected_phase12f_secure_drop_consumer_boundary(),
            rejected_phase12g_production_readiness_coverage_matrix(),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
            rejected_phase12k_external_compute_quantum_backend_capability_profile(),
        )
    )
    return _finalize_phase12l_fabric_interop_a2a_audit_profile(payload)


def phase12m_specialized_model_option_registry_capability_profile() -> dict[str, object]:
    """Return the Phase 12M specialized model option registry profile.

    The profile only names future selectable specialized model role labels. It
    implements no model loading, model/provider execution, training,
    fine-tuning, database ingestion, web scraping, network call, clinical
    decision support, device access, raw sensor processing, or runtime grant.
    """

    source_references = _phase12m_source_phase_references(
        rejected_phase12a_runtime_authorization_design_charter(),
        rejected_phase12b_runtime_authorization_record_candidate(),
        rejected_phase12c_visual_supervision_capability_profile(),
        rejected_phase12d_visual_desktop_consent_gate_requirements(),
        rejected_phase12e_physiological_sensor_capability_profile(),
        rejected_phase12f_secure_drop_consumer_boundary(),
        rejected_phase12g_production_readiness_coverage_matrix(),
        rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
        rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
        rejected_phase12k_external_compute_quantum_backend_capability_profile(),
        rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
    )
    payload = _phase12m_specialized_model_option_registry_profile_payload(source_references)
    profile = _finalize_phase12m_specialized_model_option_registry_profile(payload)
    result = validate_phase12m_specialized_model_option_registry_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12m_specialized_model_option_registry_capability_profile()
    )


def phase12m_specialized_model_option_registry_capability_profile_status_summary():
    """Return compact Phase 12M status safe for public surfaces."""

    profile = phase12m_specialized_model_option_registry_capability_profile()
    result = validate_phase12m_specialized_model_option_registry_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "specialized_model_option_registry_profile_contract_version": (
            PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12m_profile_id(safe.get("profile_id")),
        "source_phase_range": PHASE12M_SOURCE_PHASE_RANGE,
        "model_option_profile_phase": PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        "authorization_status": PHASE12M_AUTHORIZATION_STATUS,
        "grant_status": PHASE12M_GRANT_STATUS,
        "profile_status": PHASE12M_PROFILE_STATUS,
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "model_option_category_count": _safe_int(safe.get("model_option_category_count")),
        "candidate_label_count": _safe_int(safe.get("candidate_label_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "model_labels_selectable_metadata_only": True,
        "phase12m_authorizes_runtime": False,
        "phase12m_allows_model_execution": False,
        "phase12m_allows_provider_execution": False,
        "phase12m_allows_model_loading": False,
        "phase12m_allows_training": False,
        "phase12m_allows_fine_tuning": False,
        "phase12m_allows_clinical_decision_support": False,
        "phase12m_allows_diagnosis_or_treatment": False,
        "phase12m_allows_private_health_data_processing": False,
        "phase12m_allows_device_access": False,
        "phase12m_allows_raw_sensor_processing": False,
        "phase12m_provides_medical_advice": False,
        "phase12m_provides_prescribing": False,
        **{field: False for field in _phase12m_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12m_specialized_model_option_registry_capability_profile(
    profile: object,
) -> Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult:
    """Validate Phase 12M profiles and reject model/runtime/clinical semantics."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12m_profile_result(
            ("phase12m_profile_not_object",),
            "malformed",
            rejected_phase12m_specialized_model_option_registry_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    unsafe_semantics = _phase12m_unsafe_semantics_count(profile)
    errors: list[str] = []
    if PHASE12M_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12m_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12M_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12m_profile_unknown_field")
    if (
        profile.get("specialized_model_option_registry_profile_contract_version")
        != PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12m_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND:
        errors.append("phase12m_profile_kind_invalid")
    if _safe_phase12m_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12m_profile_id_invalid")
    expected = {
        "source_phase_range": PHASE12M_SOURCE_PHASE_RANGE,
        "model_option_profile_phase": PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        "authorization_status": PHASE12M_AUTHORIZATION_STATUS,
        "grant_status": PHASE12M_GRANT_STATUS,
        "profile_status": PHASE12M_PROFILE_STATUS,
        "model_boundary_statement": PHASE12M_MODEL_BOUNDARY_STATEMENT,
        "medical_boundary_statement": PHASE12M_MEDICAL_BOUNDARY_STATEMENT,
        "sensor_boundary_statement": PHASE12M_SENSOR_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if profile.get(key) != expected_value:
            errors.append("phase12m_profile_value_invalid")
            break
    errors.extend(_phase12m_source_reference_errors(profile.get("source_phase_references")))
    errors.extend(_phase12m_status_label_errors(profile.get("status_labels")))
    errors.extend(_phase12m_model_option_category_errors(profile.get("model_option_categories")))
    errors.extend(_phase12m_candidate_label_errors(profile.get("candidate_labels")))
    errors.extend(_phase12m_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "model_option_category_count",
        "candidate_label_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12m_profile_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": len(PHASE12M_SOURCE_REFERENCE_PHASES),
        "status_label_count": len(PHASE12M_STATUS_LABELS),
        "model_option_category_count": len(PHASE12M_MODEL_OPTION_CATEGORIES),
        "candidate_label_count": len(PHASE12M_CANDIDATE_LABELS),
        "required_future_gate_count": len(PHASE12M_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if profile.get(key) != expected_value:
            errors.append("phase12m_profile_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("security_review_required", True),
        ("medical_safety_review_required", True),
        ("jules_human_review_required_for_validator_or_model_safety_semantics", True),
        ("model_labels_selectable_metadata_only", True),
        ("phase12m_authorizes_runtime", False),
        ("phase12m_allows_model_execution", False),
        ("phase12m_allows_provider_execution", False),
        ("phase12m_allows_model_loading", False),
        ("phase12m_allows_training", False),
        ("phase12m_allows_fine_tuning", False),
        ("phase12m_allows_clinical_decision_support", False),
        ("phase12m_allows_diagnosis_or_treatment", False),
        ("phase12m_allows_private_health_data_processing", False),
        ("phase12m_allows_device_access", False),
        ("phase12m_allows_raw_sensor_processing", False),
        ("phase12m_provides_medical_advice", False),
        ("phase12m_provides_prescribing", False),
    ):
        if profile.get(field) is not expected_value:
            errors.append("phase12m_profile_safety_semantics_invalid")
            break
    for field in _phase12m_runtime_false_fields():
        if profile.get(field) is not False:
            errors.append("phase12m_profile_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12m_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12m_profile_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12m_profile_unsafe_model_or_medical_semantics")
    expected_id = _phase12m_profile_id(profile)
    if not expected_id:
        errors.append("phase12m_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12m_profile_id_invalid")
    if errors:
        return _invalid_phase12m_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12m_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12m_specialized_model_option_registry_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12m_specialized_model_option_registry_capability_profile():
    """Return sanitized rejected Phase 12M model option registry profile."""

    payload = _phase12m_specialized_model_option_registry_profile_payload(
        _phase12m_source_phase_references(
            rejected_phase12a_runtime_authorization_design_charter(),
            rejected_phase12b_runtime_authorization_record_candidate(),
            rejected_phase12c_visual_supervision_capability_profile(),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            rejected_phase12e_physiological_sensor_capability_profile(),
            rejected_phase12f_secure_drop_consumer_boundary(),
            rejected_phase12g_production_readiness_coverage_matrix(),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
            rejected_phase12k_external_compute_quantum_backend_capability_profile(),
            rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
        )
    )
    return _finalize_phase12m_specialized_model_option_registry_profile(payload)


def phase12n_workflow_orchestration_mode_registry_capability_profile() -> dict[str, object]:
    """Return the Phase 12N workflow orchestration mode registry profile.

    The profile only names future workflow mode labels. It implements no
    runtime orchestration, model/provider execution, model routing, code or
    experiment execution, database ingestion, web scraping, network call,
    clinical decision support, sensor access, private health-data processing,
    active grant, or real-mode authorization.
    """

    source_references = _phase12n_source_phase_references(
        rejected_phase12a_runtime_authorization_design_charter(),
        rejected_phase12b_runtime_authorization_record_candidate(),
        rejected_phase12c_visual_supervision_capability_profile(),
        rejected_phase12d_visual_desktop_consent_gate_requirements(),
        rejected_phase12e_physiological_sensor_capability_profile(),
        rejected_phase12f_secure_drop_consumer_boundary(),
        rejected_phase12g_production_readiness_coverage_matrix(),
        rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
        rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
        rejected_phase12k_external_compute_quantum_backend_capability_profile(),
        rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
        rejected_phase12m_specialized_model_option_registry_capability_profile(),
    )
    payload = _phase12n_workflow_orchestration_mode_registry_profile_payload(source_references)
    profile = _finalize_phase12n_workflow_orchestration_mode_registry_profile(payload)
    result = validate_phase12n_workflow_orchestration_mode_registry_capability_profile(profile)
    return (
        profile
        if result.compatible
        else rejected_phase12n_workflow_orchestration_mode_registry_capability_profile()
    )


def phase12n_workflow_orchestration_mode_registry_capability_profile_status_summary():
    """Return compact Phase 12N status safe for public surfaces."""

    profile = phase12n_workflow_orchestration_mode_registry_capability_profile()
    result = validate_phase12n_workflow_orchestration_mode_registry_capability_profile(profile)
    safe = result.sanitized_record
    return {
        "workflow_orchestration_mode_registry_profile_contract_version": (
            PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION
        ),
        "profile_id": _safe_phase12n_profile_id(safe.get("profile_id")),
        "source_phase_range": PHASE12N_SOURCE_PHASE_RANGE,
        "workflow_mode_profile_phase": PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        "authorization_status": PHASE12N_AUTHORIZATION_STATUS,
        "grant_status": PHASE12N_GRANT_STATUS,
        "profile_status": PHASE12N_PROFILE_STATUS,
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "workflow_mode_count": _safe_int(safe.get("workflow_mode_count")),
        "fusion_concept_count": _safe_int(safe.get("fusion_concept_count")),
        "scientist_evolution_concept_count": _safe_int(
            safe.get("scientist_evolution_concept_count")
        ),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "workflow_modes_metadata_only": True,
        "phase12n_authorizes_runtime": False,
        "phase12n_allows_workflow_mode_execution": False,
        "phase12n_allows_runtime_orchestration": False,
        "phase12n_allows_model_routing": False,
        "phase12n_allows_provider_execution": False,
        "phase12n_allows_model_execution": False,
        "phase12n_allows_model_loading": False,
        "phase12n_allows_training": False,
        "phase12n_allows_fine_tuning": False,
        "phase12n_allows_code_execution": False,
        "phase12n_allows_experiment_execution": False,
        "phase12n_allows_autonomous_experimentation": False,
        "phase12n_allows_web_access": False,
        "phase12n_allows_autonomous_publication": False,
        "phase12n_allows_clinical_decision_support": False,
        "phase12n_allows_diagnosis_or_treatment": False,
        "phase12n_allows_private_health_data_processing": False,
        "phase12n_allows_device_or_sensor_access": False,
        "phase12n_provides_medical_advice": False,
        **{field: False for field in _phase12n_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12n_workflow_orchestration_mode_registry_capability_profile(
    profile: object,
) -> Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult:
    """Validate Phase 12N profiles and reject orchestration/runtime semantics."""

    if not isinstance(profile, Mapping):
        return _invalid_phase12n_profile_result(
            ("phase12n_profile_not_object",),
            "malformed",
            rejected_phase12n_workflow_orchestration_mode_registry_capability_profile(),
        )
    privacy_violations = _privacy_violation_count(profile)
    authorization_wording = _authorization_wording_count(profile)
    unsafe_semantics = _phase12n_unsafe_semantics_count(profile)
    errors: list[str] = []
    if PHASE12N_PROFILE_REQUIRED_FIELDS - set(profile):
        errors.append("phase12n_profile_required_field_missing")
    if set(str(key) for key in profile) - PHASE12N_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12n_profile_unknown_field")
    if (
        profile.get("workflow_orchestration_mode_registry_profile_contract_version")
        != PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION
    ):
        errors.append("phase12n_profile_contract_version_unsupported")
    if profile.get("profile_kind") != PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND:
        errors.append("phase12n_profile_kind_invalid")
    if _safe_phase12n_profile_id(profile.get("profile_id")) != profile.get("profile_id"):
        errors.append("phase12n_profile_id_invalid")
    expected = {
        "source_phase_range": PHASE12N_SOURCE_PHASE_RANGE,
        "workflow_mode_profile_phase": PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        "authorization_status": PHASE12N_AUTHORIZATION_STATUS,
        "grant_status": PHASE12N_GRANT_STATUS,
        "profile_status": PHASE12N_PROFILE_STATUS,
        "workflow_boundary_statement": PHASE12N_WORKFLOW_BOUNDARY_STATEMENT,
        "fusion_boundary_statement": PHASE12N_FUSION_BOUNDARY_STATEMENT,
        "scientist_boundary_statement": PHASE12N_SCIENTIST_BOUNDARY_STATEMENT,
        "medical_sensor_boundary_statement": PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if profile.get(key) != expected_value:
            errors.append("phase12n_profile_value_invalid")
            break
    errors.extend(_phase12n_source_reference_errors(profile.get("source_phase_references")))
    errors.extend(_phase12n_status_label_errors(profile.get("status_labels")))
    errors.extend(_phase12n_workflow_mode_errors(profile.get("workflow_modes")))
    errors.extend(_phase12n_fusion_concept_errors(profile.get("fusion_concepts")))
    errors.extend(
        _phase12n_scientist_evolution_concept_errors(profile.get("scientist_evolution_concepts"))
    )
    errors.extend(_phase12n_future_gate_errors(profile.get("required_future_gates")))
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "workflow_mode_count",
        "fusion_concept_count",
        "scientist_evolution_concept_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(profile.get(field)):
            errors.append("phase12n_profile_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": len(PHASE12N_SOURCE_REFERENCE_PHASES),
        "status_label_count": len(PHASE12N_STATUS_LABELS),
        "workflow_mode_count": len(PHASE12N_WORKFLOW_MODES),
        "fusion_concept_count": len(PHASE12N_FUSION_CONCEPT_LABELS),
        "scientist_evolution_concept_count": len(PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS),
        "required_future_gate_count": len(PHASE12N_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if profile.get(key) != expected_value:
            errors.append("phase12n_profile_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("security_review_required", True),
        ("medical_safety_review_required", True),
        (
            "jules_human_review_required_for_validator_or_workflow_safety_semantics",
            True,
        ),
        ("workflow_modes_metadata_only", True),
        ("phase12n_authorizes_runtime", False),
        ("phase12n_allows_workflow_mode_execution", False),
        ("phase12n_allows_runtime_orchestration", False),
        ("phase12n_allows_model_routing", False),
        ("phase12n_allows_provider_execution", False),
        ("phase12n_allows_model_execution", False),
        ("phase12n_allows_model_loading", False),
        ("phase12n_allows_training", False),
        ("phase12n_allows_fine_tuning", False),
        ("phase12n_allows_code_execution", False),
        ("phase12n_allows_experiment_execution", False),
        ("phase12n_allows_autonomous_experimentation", False),
        ("phase12n_allows_web_access", False),
        ("phase12n_allows_autonomous_publication", False),
        ("phase12n_allows_clinical_decision_support", False),
        ("phase12n_allows_diagnosis_or_treatment", False),
        ("phase12n_allows_private_health_data_processing", False),
        ("phase12n_allows_device_or_sensor_access", False),
        ("phase12n_provides_medical_advice", False),
    ):
        if profile.get(field) is not expected_value:
            errors.append("phase12n_profile_safety_semantics_invalid")
            break
    for field in _phase12n_runtime_false_fields():
        if profile.get(field) is not False:
            errors.append("phase12n_profile_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12n_profile_privacy_boundary")
    if authorization_wording:
        errors.append("phase12n_profile_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12n_profile_unsafe_workflow_or_runtime_semantics")
    expected_id = _phase12n_profile_id(profile)
    if not expected_id:
        errors.append("phase12n_profile_payload_not_json")
    elif profile.get("profile_id") != expected_id:
        errors.append("phase12n_profile_id_invalid")
    if errors:
        return _invalid_phase12n_profile_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12n_profile_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12n_workflow_orchestration_mode_registry_capability_profile(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(profile),
    )


def rejected_phase12n_workflow_orchestration_mode_registry_capability_profile():
    """Return sanitized rejected Phase 12N workflow mode registry profile."""

    payload = _phase12n_workflow_orchestration_mode_registry_profile_payload(
        _phase12n_source_phase_references(
            rejected_phase12a_runtime_authorization_design_charter(),
            rejected_phase12b_runtime_authorization_record_candidate(),
            rejected_phase12c_visual_supervision_capability_profile(),
            rejected_phase12d_visual_desktop_consent_gate_requirements(),
            rejected_phase12e_physiological_sensor_capability_profile(),
            rejected_phase12f_secure_drop_consumer_boundary(),
            rejected_phase12g_production_readiness_coverage_matrix(),
            rejected_phase12h_somatic_standalone_production_readiness_ownership_map(),
            rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile(),
            rejected_phase12k_external_compute_quantum_backend_capability_profile(),
            rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile(),
            rejected_phase12m_specialized_model_option_registry_capability_profile(),
        )
    )
    return _finalize_phase12n_workflow_orchestration_mode_registry_profile(payload)


def phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix() -> dict[str, object]:
    """Return the Phase 12O workflow-mode runtime prerequisite matrix.

    The matrix only records future gates that must remain unsatisfied until a
    future authorization phase. It implements no workflow execution, model
    routing, runtime adapter, provider/model execution, code execution,
    experiment execution, web/database/network behavior, clinical decision
    support, private health-data processing, active grant, or real-mode
    authorization.
    """

    source_profile = phase12n_workflow_orchestration_mode_registry_capability_profile()
    source_result = validate_phase12n_workflow_orchestration_mode_registry_capability_profile(
        source_profile
    )
    safe_source = (
        source_result.sanitized_record
        if source_result.compatible
        else rejected_phase12n_workflow_orchestration_mode_registry_capability_profile()
    )
    payload = _phase12o_workflow_mode_safety_gate_matrix_payload(
        _phase12o_source_phase12n_profile(safe_source)
    )
    matrix = _finalize_phase12o_workflow_mode_safety_gate_matrix(payload)
    result = validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(matrix)
    return (
        matrix
        if result.compatible
        else rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix()
    )


def phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix_status_summary():
    """Return compact Phase 12O status safe for public surfaces."""

    matrix = phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix()
    result = validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(matrix)
    safe = result.sanitized_record
    return {
        "workflow_mode_safety_gate_matrix_contract_version": (
            PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION
        ),
        "matrix_id": _safe_phase12o_matrix_id(safe.get("matrix_id")),
        "source_phase": PHASE12O_SOURCE_PHASE,
        "matrix_phase": PHASE12O_MATRIX_PHASE,
        "authorization_status": PHASE12O_AUTHORIZATION_STATUS,
        "grant_status": PHASE12O_GRANT_STATUS,
        "matrix_status": PHASE12O_MATRIX_STATUS,
        "workflow_mode_prerequisite_count": _safe_int(safe.get("workflow_mode_prerequisite_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "mode_gate_requirement_count": _safe_int(safe.get("mode_gate_requirement_count")),
        "metadata_only": True,
        "non_authorizing_proof": True,
        "standalone_first": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "workflow_mode_safety_gates_metadata_only": True,
        "phase12o_authorizes_runtime": False,
        "phase12o_satisfies_runtime_prerequisites": False,
        "phase12o_allows_workflow_execution": False,
        "phase12o_allows_workflow_mode_execution": False,
        "phase12o_allows_runtime_adapter": False,
        "phase12o_allows_model_routing": False,
        "phase12o_allows_provider_execution": False,
        "phase12o_allows_model_execution": False,
        "phase12o_allows_code_execution": False,
        "phase12o_allows_experiment_execution": False,
        "phase12o_allows_web_database_network_behavior": False,
        "phase12o_allows_clinical_decision_support": False,
        "phase12o_allows_private_health_data_processing": False,
        "phase12o_active_grant_present": False,
        **{field: False for field in _phase12o_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(
    matrix: object,
) -> Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult:
    """Validate Phase 12O matrices and reject runtime-prerequisite satisfaction."""

    if not isinstance(matrix, Mapping):
        return _invalid_phase12o_matrix_result(
            ("phase12o_matrix_not_object",),
            "malformed",
            rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(),
        )
    privacy_violations = _privacy_violation_count(matrix)
    authorization_wording = _authorization_wording_count(matrix)
    unsafe_semantics = _phase12o_unsafe_semantics_count(matrix)
    errors: list[str] = []
    if PHASE12O_MATRIX_REQUIRED_FIELDS - set(matrix):
        errors.append("phase12o_matrix_required_field_missing")
    if set(str(key) for key in matrix) - PHASE12O_MATRIX_REQUIRED_FIELDS:
        errors.append("phase12o_matrix_unknown_field")
    if (
        matrix.get("workflow_mode_safety_gate_matrix_contract_version")
        != PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION
    ):
        errors.append("phase12o_matrix_contract_version_unsupported")
    if matrix.get("matrix_kind") != PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND:
        errors.append("phase12o_matrix_kind_invalid")
    if _safe_phase12o_matrix_id(matrix.get("matrix_id")) != matrix.get("matrix_id"):
        errors.append("phase12o_matrix_id_invalid")
    expected = {
        "source_phase": PHASE12O_SOURCE_PHASE,
        "matrix_phase": PHASE12O_MATRIX_PHASE,
        "authorization_status": PHASE12O_AUTHORIZATION_STATUS,
        "grant_status": PHASE12O_GRANT_STATUS,
        "matrix_status": PHASE12O_MATRIX_STATUS,
        "matrix_boundary_statement": PHASE12O_MATRIX_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "standalone_first_statement": PHASE12O_STANDALONE_FIRST_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if matrix.get(key) != expected_value:
            errors.append("phase12o_matrix_value_invalid")
            break
    errors.extend(_phase12o_source_profile_errors(matrix.get("source_phase12n_profile")))
    errors.extend(_phase12o_status_label_errors(matrix.get("status_labels")))
    errors.extend(
        _phase12o_workflow_mode_prerequisite_errors(matrix.get("workflow_mode_prerequisite_matrix"))
    )
    errors.extend(_phase12o_future_gate_errors(matrix.get("required_future_gates")))
    errors.extend(_phase12o_mode_gate_requirement_errors(matrix.get("mode_gate_requirements")))
    for field in (
        "status_label_count",
        "workflow_mode_prerequisite_count",
        "required_future_gate_count",
        "mode_gate_requirement_count",
    ):
        if not _is_non_negative_int(matrix.get(field)):
            errors.append("phase12o_matrix_count_invalid")
            break
    expected_counts = {
        "status_label_count": len(PHASE12O_STATUS_LABELS),
        "workflow_mode_prerequisite_count": len(PHASE12O_WORKFLOW_MODES),
        "required_future_gate_count": len(PHASE12O_REQUIRED_FUTURE_GATES),
        "mode_gate_requirement_count": len(PHASE12O_WORKFLOW_MODES)
        * len(PHASE12O_REQUIRED_FUTURE_GATES),
    }
    for key, expected_value in expected_counts.items():
        if matrix.get(key) != expected_value:
            errors.append("phase12o_matrix_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("non_authorizing_proof", True),
        ("standalone_first", True),
        ("security_review_required", True),
        ("medical_safety_review_required", True),
        ("jules_human_review_required_for_validator_or_workflow_safety_semantics", True),
        ("workflow_mode_safety_gates_metadata_only", True),
        ("phase12o_authorizes_runtime", False),
        ("phase12o_satisfies_runtime_prerequisites", False),
        ("phase12o_allows_workflow_execution", False),
        ("phase12o_allows_workflow_mode_execution", False),
        ("phase12o_allows_runtime_adapter", False),
        ("phase12o_allows_model_routing", False),
        ("phase12o_allows_provider_execution", False),
        ("phase12o_allows_model_execution", False),
        ("phase12o_allows_code_execution", False),
        ("phase12o_allows_experiment_execution", False),
        ("phase12o_allows_web_database_network_behavior", False),
        ("phase12o_allows_clinical_decision_support", False),
        ("phase12o_allows_private_health_data_processing", False),
        ("phase12o_active_grant_present", False),
    ):
        if matrix.get(field) is not expected_value:
            errors.append("phase12o_matrix_safety_semantics_invalid")
            break
    for field in _phase12o_runtime_false_fields():
        if matrix.get(field) is not False:
            errors.append("phase12o_matrix_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12o_matrix_privacy_boundary")
    if authorization_wording:
        errors.append("phase12o_matrix_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12o_matrix_unsafe_runtime_semantics")
    expected_id = _phase12o_matrix_id(matrix)
    if not expected_id:
        errors.append("phase12o_matrix_payload_not_json")
    elif matrix.get("matrix_id") != expected_id:
        errors.append("phase12o_matrix_id_invalid")
    if errors:
        return _invalid_phase12o_matrix_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12o_matrix_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(matrix),
    )


def rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix():
    """Return sanitized rejected Phase 12O workflow-mode safety gate matrix."""

    payload = _phase12o_workflow_mode_safety_gate_matrix_payload(
        _phase12o_source_phase12n_profile(
            rejected_phase12n_workflow_orchestration_mode_registry_capability_profile()
        )
    )
    return _finalize_phase12o_workflow_mode_safety_gate_matrix(payload)


def phase12p_workflow_mode_activation_request_review_packet_boundary() -> dict[str, object]:
    """Return the Phase 12P workflow-mode activation request review packet boundary.

    The packet records metadata for future human/Jules/security/medical-safety review
    only. It implements no activation, grant, runtime authorization, workflow
    execution, model routing, provider/model execution, code or experiment execution,
    network/database/web behavior, clinical use, private health-data processing,
    device access, sensor processing, or production readiness.
    """

    source_profile = phase12n_workflow_orchestration_mode_registry_capability_profile()
    source_matrix = phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix()
    source_profile_result = (
        validate_phase12n_workflow_orchestration_mode_registry_capability_profile(source_profile)
    )
    source_matrix_result = validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix(
        source_matrix
    )
    safe_profile = (
        source_profile_result.sanitized_record
        if source_profile_result.compatible
        else rejected_phase12n_workflow_orchestration_mode_registry_capability_profile()
    )
    safe_matrix = (
        source_matrix_result.sanitized_record
        if source_matrix_result.compatible
        else rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix()
    )
    payload = _phase12p_review_packet_payload(
        _phase12p_source_phase_references(safe_profile, safe_matrix),
        _phase12p_prerequisite_matrix_reference(safe_matrix),
    )
    packet = _finalize_phase12p_review_packet(payload)
    result = validate_phase12p_workflow_mode_activation_request_review_packet_boundary(packet)
    return (
        packet
        if result.compatible
        else rejected_phase12p_workflow_mode_activation_request_review_packet_boundary()
    )


def phase12p_workflow_mode_activation_request_review_packet_boundary_status_summary():
    """Return compact Phase 12P status safe for public surfaces."""

    packet = phase12p_workflow_mode_activation_request_review_packet_boundary()
    result = validate_phase12p_workflow_mode_activation_request_review_packet_boundary(packet)
    safe = result.sanitized_record
    return {
        "workflow_mode_activation_request_review_packet_contract_version": (
            PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION
        ),
        "activation_request_packet_id": _safe_phase12p_packet_id(
            safe.get("activation_request_packet_id")
        ),
        "source_phase_range": PHASE12P_SOURCE_PHASE_RANGE,
        "packet_phase": PHASE12P_PACKET_PHASE,
        "authorization_status": PHASE12P_AUTHORIZATION_STATUS,
        "grant_status": PHASE12P_GRANT_STATUS,
        "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
        "packet_status": PHASE12P_PACKET_STATUS,
        "workflow_mode_review_packet_count": _safe_int(
            safe.get("workflow_mode_review_packet_count")
        ),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "required_reviewer_class_count": _safe_int(safe.get("required_reviewer_class_count")),
        "risk_summary_placeholder_count": _safe_int(safe.get("risk_summary_placeholder_count")),
        "evidence_inventory_placeholder_count": _safe_int(
            safe.get("evidence_inventory_placeholder_count")
        ),
        "metadata_only": True,
        "review_packet_boundary_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "human_review_required": True,
        "jules_review_required": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "human_jules_security_medical_safety_review_required": True,
        "all_future_gates_unsatisfied": True,
        "denial_blocked_default_fail_closed": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12p_authorizes_runtime": False,
        "phase12p_creates_active_grant": False,
        "phase12p_grants_execution_permission": False,
        "phase12p_allows_workflow_execution": False,
        "phase12p_allows_workflow_mode_execution": False,
        "phase12p_allows_runtime_adapter": False,
        "phase12p_allows_model_routing": False,
        "phase12p_allows_provider_execution": False,
        "phase12p_allows_model_execution": False,
        "phase12p_allows_model_loading": False,
        "phase12p_allows_training": False,
        "phase12p_allows_fine_tuning": False,
        "phase12p_allows_code_execution": False,
        "phase12p_allows_experiment_execution": False,
        "phase12p_allows_autonomous_experimentation": False,
        "phase12p_allows_web_access": False,
        "phase12p_allows_database_ingestion": False,
        "phase12p_allows_web_scraping": False,
        "phase12p_allows_network_calls": False,
        "phase12p_allows_clinical_decision_support": False,
        "phase12p_allows_diagnosis_or_treatment": False,
        "phase12p_allows_medical_advice": False,
        "phase12p_allows_dosing_or_nutrition_prescription": False,
        "phase12p_allows_private_health_data_processing": False,
        "phase12p_allows_device_or_sensor_access": False,
        "phase12p_allows_raw_sensor_processing": False,
        "phase12p_marks_production_ready": False,
        **{field: False for field in _phase12p_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12p_workflow_mode_activation_request_review_packet_boundary(
    packet: object,
) -> Phase12PWorkflowModeActivationRequestReviewPacketValidationResult:
    """Validate Phase 12P packets and reject activation/runtime semantics."""

    if not isinstance(packet, Mapping):
        return _invalid_phase12p_packet_result(
            ("phase12p_packet_not_object",),
            "malformed",
            rejected_phase12p_workflow_mode_activation_request_review_packet_boundary(),
        )
    privacy_violations = _privacy_violation_count(packet)
    authorization_wording = _authorization_wording_count(packet)
    unsafe_semantics = _phase12p_unsafe_semantics_count(packet)
    errors: list[str] = []
    if PHASE12P_REVIEW_PACKET_REQUIRED_FIELDS - set(packet):
        errors.append("phase12p_packet_required_field_missing")
    if set(str(key) for key in packet) - PHASE12P_REVIEW_PACKET_REQUIRED_FIELDS:
        errors.append("phase12p_packet_unknown_field")
    if (
        packet.get("workflow_mode_activation_request_review_packet_contract_version")
        != PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION
    ):
        errors.append("phase12p_packet_contract_version_unsupported")
    if packet.get("packet_kind") != PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND:
        errors.append("phase12p_packet_kind_invalid")
    if _safe_phase12p_packet_id(packet.get("activation_request_packet_id")) != packet.get(
        "activation_request_packet_id"
    ):
        errors.append("phase12p_packet_id_invalid")
    expected = {
        "source_phase_range": PHASE12P_SOURCE_PHASE_RANGE,
        "packet_phase": PHASE12P_PACKET_PHASE,
        "authorization_status": PHASE12P_AUTHORIZATION_STATUS,
        "grant_status": PHASE12P_GRANT_STATUS,
        "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
        "packet_status": PHASE12P_PACKET_STATUS,
        "denial_blocked_default_fail_closed_status": PHASE12P_DENIAL_BLOCKED_STATUS,
        "workflow_mode_activation_not_permitted_status": (PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS),
        "packet_boundary_statement": PHASE12P_PACKET_BOUNDARY_STATEMENT,
        "review_requirement_statement": PHASE12P_REVIEW_REQUIREMENT_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if packet.get(key) != expected_value:
            errors.append("phase12p_packet_value_invalid")
            break
    errors.extend(_phase12p_source_reference_errors(packet.get("source_phase_references")))
    errors.extend(
        _phase12p_prerequisite_matrix_reference_errors(packet.get("prerequisite_matrix_reference"))
    )
    errors.extend(_phase12p_status_label_errors(packet.get("status_labels")))
    errors.extend(_phase12p_mode_review_packet_errors(packet.get("workflow_mode_review_packets")))
    errors.extend(_phase12p_future_gate_errors(packet.get("required_future_gates")))
    errors.extend(_phase12p_reviewer_class_errors(packet.get("required_reviewer_classes")))
    errors.extend(
        _phase12p_risk_summary_placeholder_errors(packet.get("risk_summary_placeholders"))
    )
    errors.extend(
        _phase12p_evidence_inventory_placeholder_errors(
            packet.get("evidence_inventory_placeholders")
        )
    )
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "workflow_mode_review_packet_count",
        "required_future_gate_count",
        "required_reviewer_class_count",
        "risk_summary_placeholder_count",
        "evidence_inventory_placeholder_count",
    ):
        if not _is_non_negative_int(packet.get(field)):
            errors.append("phase12p_packet_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": 2,
        "status_label_count": len(PHASE12P_STATUS_LABELS),
        "workflow_mode_review_packet_count": len(PHASE12P_WORKFLOW_MODES),
        "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
        "required_reviewer_class_count": len(PHASE12P_REQUIRED_REVIEWER_CLASSES),
        "risk_summary_placeholder_count": len(PHASE12P_RISK_SUMMARY_PLACEHOLDERS),
        "evidence_inventory_placeholder_count": len(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS),
    }
    for key, expected_value in expected_counts.items():
        if packet.get(key) != expected_value:
            errors.append("phase12p_packet_count_value_invalid")
            break
    for field, expected_value in (
        ("metadata_only", True),
        ("review_packet_boundary_only", True),
        ("standalone_first", True),
        ("non_authorizing_proof", True),
        ("not_authorized", True),
        ("human_review_required", True),
        ("jules_review_required", True),
        ("security_review_required", True),
        ("medical_safety_review_required", True),
        ("human_jules_security_medical_safety_review_required", True),
        ("all_future_gates_unsatisfied", True),
        ("denial_blocked_default_fail_closed", True),
        ("no_active_grant", True),
        ("no_runtime_authorization", True),
        ("no_execution_permission", True),
        ("workflow_mode_activation_not_permitted", True),
        ("phase12p_authorizes_runtime", False),
        ("phase12p_creates_active_grant", False),
        ("phase12p_grants_execution_permission", False),
        ("phase12p_allows_workflow_execution", False),
        ("phase12p_allows_workflow_mode_execution", False),
        ("phase12p_allows_runtime_adapter", False),
        ("phase12p_allows_model_routing", False),
        ("phase12p_allows_provider_execution", False),
        ("phase12p_allows_model_execution", False),
        ("phase12p_allows_model_loading", False),
        ("phase12p_allows_training", False),
        ("phase12p_allows_fine_tuning", False),
        ("phase12p_allows_code_execution", False),
        ("phase12p_allows_experiment_execution", False),
        ("phase12p_allows_autonomous_experimentation", False),
        ("phase12p_allows_web_access", False),
        ("phase12p_allows_database_ingestion", False),
        ("phase12p_allows_web_scraping", False),
        ("phase12p_allows_network_calls", False),
        ("phase12p_allows_clinical_decision_support", False),
        ("phase12p_allows_diagnosis_or_treatment", False),
        ("phase12p_allows_medical_advice", False),
        ("phase12p_allows_dosing_or_nutrition_prescription", False),
        ("phase12p_allows_private_health_data_processing", False),
        ("phase12p_allows_device_or_sensor_access", False),
        ("phase12p_allows_raw_sensor_processing", False),
        ("phase12p_marks_production_ready", False),
    ):
        if packet.get(field) is not expected_value:
            errors.append("phase12p_packet_safety_semantics_invalid")
            break
    for field in _phase12p_runtime_false_fields():
        if packet.get(field) is not False:
            errors.append("phase12p_packet_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12p_packet_privacy_boundary")
    if authorization_wording:
        errors.append("phase12p_packet_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12p_packet_unsafe_activation_or_runtime_semantics")
    expected_id = _phase12p_packet_id(packet)
    if not expected_id:
        errors.append("phase12p_packet_payload_not_json")
    elif packet.get("activation_request_packet_id") != expected_id:
        errors.append("phase12p_packet_id_invalid")
    if errors:
        return _invalid_phase12p_packet_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12p_packet_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12p_workflow_mode_activation_request_review_packet_boundary(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12PWorkflowModeActivationRequestReviewPacketValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(packet),
    )


def rejected_phase12p_workflow_mode_activation_request_review_packet_boundary():
    """Return sanitized rejected Phase 12P workflow-mode review packet boundary."""

    source_profile = rejected_phase12n_workflow_orchestration_mode_registry_capability_profile()
    source_matrix = rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix()
    payload = _phase12p_review_packet_payload(
        _phase12p_source_phase_references(source_profile, source_matrix),
        _phase12p_prerequisite_matrix_reference(source_matrix),
    )
    return _finalize_phase12p_review_packet(payload)


def phase12q_non_authorizing_workflow_mode_review_decision_record() -> dict[str, object]:
    """Return the Phase 12Q workflow-mode review decision record contract.

    The record defines future human/Jules/security/medical-safety decision metadata
    only. It does not approve runtime, create grants, activate workflow modes, run
    workflows, route models, execute providers or code, process clinical/private
    health data, access devices or sensors, or mark production readiness.
    """

    source_packet = phase12p_workflow_mode_activation_request_review_packet_boundary()
    source_packet_result = (
        validate_phase12p_workflow_mode_activation_request_review_packet_boundary(source_packet)
    )
    safe_packet = (
        source_packet_result.sanitized_record
        if source_packet_result.compatible
        else rejected_phase12p_workflow_mode_activation_request_review_packet_boundary()
    )
    payload = _phase12q_decision_record_payload(
        _phase12q_source_phase_references(safe_packet),
        safe_packet,
    )
    record = _finalize_phase12q_decision_record(payload)
    result = validate_phase12q_non_authorizing_workflow_mode_review_decision_record(record)
    return record if result.compatible else rejected_phase12q_workflow_mode_review_decision_record()


def phase12q_non_authorizing_workflow_mode_review_decision_record_status_summary():
    """Return compact Phase 12Q status safe for public surfaces."""

    record = phase12q_non_authorizing_workflow_mode_review_decision_record()
    result = validate_phase12q_non_authorizing_workflow_mode_review_decision_record(record)
    safe = result.sanitized_record
    return {
        "workflow_mode_review_decision_record_contract_version": (
            PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION
        ),
        "decision_record_id": _safe_phase12q_decision_record_id(safe.get("decision_record_id")),
        "source_phase_range": PHASE12Q_SOURCE_PHASE_RANGE,
        "decision_record_phase": PHASE12Q_DECISION_RECORD_PHASE,
        "authorization_status": PHASE12Q_AUTHORIZATION_STATUS,
        "grant_status": PHASE12Q_GRANT_STATUS,
        "decision_record_status": PHASE12Q_DECISION_RECORD_STATUS,
        "requested_workflow_mode_label": _safe_phase12q_workflow_mode_label(
            safe.get("requested_workflow_mode_label")
        ),
        "decision_status": _safe_phase12q_decision_status(safe.get("decision_status")),
        "decision_reason_code": _safe_phase12q_decision_reason_code(
            safe.get("decision_reason_code")
        ),
        "request_disposition_status": _safe_phase12q_request_disposition_status(
            safe.get("request_disposition_status")
        ),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "unsatisfied_gate_count": _safe_int(safe.get("unsatisfied_gate_count")),
        "blocker_count": _safe_int(safe.get("blocker_count")),
        "reviewer_class_required_count": _safe_int(safe.get("reviewer_class_required_count")),
        "reviewer_class_represented_count": _safe_int(safe.get("reviewer_class_represented_count")),
        "metadata_only": True,
        "review_decision_record_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12q_authorizes_runtime": False,
        "phase12q_creates_active_grant": False,
        "phase12q_grants_execution_permission": False,
        "phase12q_allows_workflow_activation": False,
        "phase12q_allows_workflow_execution": False,
        "phase12q_allows_workflow_mode_execution": False,
        "phase12q_allows_runtime_adapter": False,
        "phase12q_allows_model_routing": False,
        "phase12q_allows_provider_execution": False,
        "phase12q_allows_model_execution": False,
        "phase12q_allows_model_loading": False,
        "phase12q_allows_training": False,
        "phase12q_allows_fine_tuning": False,
        "phase12q_allows_code_execution": False,
        "phase12q_allows_experiment_execution": False,
        "phase12q_allows_autonomous_experimentation": False,
        "phase12q_allows_web_access": False,
        "phase12q_allows_database_ingestion": False,
        "phase12q_allows_web_scraping": False,
        "phase12q_allows_network_calls": False,
        "phase12q_allows_clinical_decision_support": False,
        "phase12q_allows_diagnosis_or_treatment": False,
        "phase12q_allows_medical_advice": False,
        "phase12q_allows_dosing_or_nutrition_prescription": False,
        "phase12q_allows_private_health_data_processing": False,
        "phase12q_allows_device_or_sensor_access": False,
        "phase12q_allows_raw_sensor_processing": False,
        "phase12q_marks_production_ready": False,
        **{field: False for field in _phase12q_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12q_non_authorizing_workflow_mode_review_decision_record(
    record: object,
) -> Phase12QWorkflowModeReviewDecisionRecordValidationResult:
    """Validate Phase 12Q records and reject runtime/approval semantics."""

    if not isinstance(record, Mapping):
        return _invalid_phase12q_decision_record_result(
            ("phase12q_decision_record_not_object",),
            "malformed",
            rejected_phase12q_workflow_mode_review_decision_record(),
        )
    privacy_violations = _privacy_violation_count(record)
    authorization_wording = _authorization_wording_count(record)
    unsafe_semantics = _phase12q_unsafe_semantics_count(record)
    errors: list[str] = []
    if PHASE12Q_DECISION_RECORD_REQUIRED_FIELDS - set(record):
        errors.append("phase12q_decision_record_required_field_missing")
    if set(str(key) for key in record) - PHASE12Q_DECISION_RECORD_REQUIRED_FIELDS:
        errors.append("phase12q_decision_record_unknown_field")
    if (
        record.get("workflow_mode_review_decision_record_contract_version")
        != PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION
    ):
        errors.append("phase12q_decision_record_contract_version_unsupported")
    if record.get("decision_record_kind") != PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND:
        errors.append("phase12q_decision_record_kind_invalid")
    if _safe_phase12q_decision_record_id(record.get("decision_record_id")) != record.get(
        "decision_record_id"
    ):
        errors.append("phase12q_decision_record_id_invalid")
    decision_status = _safe_phase12q_decision_status(record.get("decision_status"))
    if decision_status != record.get("decision_status"):
        errors.append("phase12q_decision_status_invalid")
    expected_reason = PHASE12Q_DECISION_STATUS_REASON_CODES.get(decision_status)
    if expected_reason != record.get("decision_reason_code"):
        errors.append("phase12q_decision_reason_code_invalid")
    expected_disposition = PHASE12Q_DECISION_STATUS_DISPOSITIONS.get(decision_status)
    if expected_disposition != record.get("request_disposition_status"):
        errors.append("phase12q_request_disposition_status_invalid")
    expected = {
        "source_phase_range": PHASE12Q_SOURCE_PHASE_RANGE,
        "decision_record_phase": PHASE12Q_DECISION_RECORD_PHASE,
        "authorization_status": PHASE12Q_AUTHORIZATION_STATUS,
        "grant_status": PHASE12Q_GRANT_STATUS,
        "decision_record_status": PHASE12Q_DECISION_RECORD_STATUS,
        "decision_summary": PHASE12Q_DECISION_SUMMARY,
        "workflow_mode_activation_not_permitted_status": PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        "decision_boundary_statement": PHASE12Q_DECISION_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if record.get(key) != expected_value:
            errors.append("phase12q_decision_record_value_invalid")
            break
    if _safe_phase12p_packet_id(record.get("source_activation_request_packet_id")) != record.get(
        "source_activation_request_packet_id"
    ):
        errors.append("phase12q_source_activation_request_packet_id_invalid")
    if _safe_phase12q_workflow_mode_label(
        record.get("requested_workflow_mode_label")
    ) != record.get("requested_workflow_mode_label"):
        errors.append("phase12q_requested_workflow_mode_label_invalid")
    errors.extend(_phase12q_source_reference_errors(record.get("source_phase_references")))
    errors.extend(_phase12q_status_label_errors(record.get("status_labels")))
    errors.extend(
        _phase12q_future_gate_snapshot_errors(record.get("required_future_gates_snapshot"))
    )
    errors.extend(_phase12q_reviewer_class_required_errors(record.get("reviewer_classes_required")))
    errors.extend(
        _phase12q_reviewer_class_represented_errors(record.get("reviewer_classes_represented"))
    )
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "required_future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
        "reviewer_class_required_count",
        "reviewer_class_represented_count",
    ):
        if not _is_non_negative_int(record.get(field)):
            errors.append("phase12q_decision_record_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": 3,
        "status_label_count": len(PHASE12Q_STATUS_LABELS),
        "required_future_gate_count": len(PHASE12Q_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12Q_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12Q_REQUIRED_FUTURE_GATES)
        + len(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        "reviewer_class_required_count": len(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        "reviewer_class_represented_count": 0,
    }
    for key, expected_value in expected_counts.items():
        if record.get(key) != expected_value:
            errors.append("phase12q_decision_record_count_value_invalid")
            break
    expected_status_flags = _phase12q_decision_status_flags(decision_status)
    expected_safety = {
        "metadata_only": True,
        "review_decision_record_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12q_authorizes_runtime": False,
        "phase12q_creates_active_grant": False,
        "phase12q_grants_execution_permission": False,
        "phase12q_allows_workflow_activation": False,
        "phase12q_allows_workflow_execution": False,
        "phase12q_allows_workflow_mode_execution": False,
        "phase12q_allows_runtime_adapter": False,
        "phase12q_allows_model_routing": False,
        "phase12q_allows_provider_execution": False,
        "phase12q_allows_model_execution": False,
        "phase12q_allows_model_loading": False,
        "phase12q_allows_training": False,
        "phase12q_allows_fine_tuning": False,
        "phase12q_allows_code_execution": False,
        "phase12q_allows_experiment_execution": False,
        "phase12q_allows_autonomous_experimentation": False,
        "phase12q_allows_web_access": False,
        "phase12q_allows_database_ingestion": False,
        "phase12q_allows_web_scraping": False,
        "phase12q_allows_network_calls": False,
        "phase12q_allows_clinical_decision_support": False,
        "phase12q_allows_diagnosis_or_treatment": False,
        "phase12q_allows_medical_advice": False,
        "phase12q_allows_dosing_or_nutrition_prescription": False,
        "phase12q_allows_private_health_data_processing": False,
        "phase12q_allows_device_or_sensor_access": False,
        "phase12q_allows_raw_sensor_processing": False,
        "phase12q_marks_production_ready": False,
        **expected_status_flags,
    }
    for field, expected_value in expected_safety.items():
        if record.get(field) is not expected_value:
            errors.append("phase12q_decision_record_safety_semantics_invalid")
            break
    for field in _phase12q_runtime_false_fields():
        if record.get(field) is not False:
            errors.append("phase12q_decision_record_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12q_decision_record_privacy_boundary")
    if authorization_wording:
        errors.append("phase12q_decision_record_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12q_decision_record_unsafe_runtime_semantics")
    expected_id = _phase12q_decision_record_id(record)
    if not expected_id:
        errors.append("phase12q_decision_record_payload_not_json")
    elif record.get("decision_record_id") != expected_id:
        errors.append("phase12q_decision_record_id_invalid")
    if errors:
        return _invalid_phase12q_decision_record_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12q_decision_record_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12q_workflow_mode_review_decision_record(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12QWorkflowModeReviewDecisionRecordValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(record),
    )


def rejected_phase12q_workflow_mode_review_decision_record() -> dict[str, object]:
    """Return sanitized rejected Phase 12Q workflow-mode decision record."""

    source_packet = rejected_phase12p_workflow_mode_activation_request_review_packet_boundary()
    payload = _phase12q_decision_record_payload(
        _phase12q_source_phase_references(source_packet),
        source_packet,
    )
    return _finalize_phase12q_decision_record(payload)


def phase12r_workflow_mode_review_audit_trail_index() -> dict[str, object]:
    """Return the Phase 12R workflow-mode review audit trail index contract.

    The index links the Phase 12N workflow mode registry, Phase 12O prerequisite
    matrix, Phase 12P activation request review packet, and Phase 12Q decision
    record for audit only. It does not approve runtime, create grants, activate
    workflow modes, run workflows, route models, execute code, execute shell or
    process commands, use storage/query/network runtime, process clinical/private
    health data, access devices or sensors, or mark production readiness.
    """

    source_record = phase12q_non_authorizing_workflow_mode_review_decision_record()
    source_record_result = validate_phase12q_non_authorizing_workflow_mode_review_decision_record(
        source_record
    )
    safe_record = (
        source_record_result.sanitized_record
        if source_record_result.compatible
        else rejected_phase12q_workflow_mode_review_decision_record()
    )
    payload = _phase12r_audit_trail_index_payload(
        _phase12r_source_phase_references(safe_record),
        safe_record,
    )
    index = _finalize_phase12r_audit_trail_index(payload)
    result = validate_phase12r_workflow_mode_review_audit_trail_index(index)
    return (
        index if result.compatible else rejected_phase12r_workflow_mode_review_audit_trail_index()
    )


def phase12r_workflow_mode_review_audit_trail_index_status_summary() -> dict[str, object]:
    """Return compact Phase 12R status safe for public surfaces."""

    index = phase12r_workflow_mode_review_audit_trail_index()
    result = validate_phase12r_workflow_mode_review_audit_trail_index(index)
    safe = result.sanitized_record
    return {
        "workflow_mode_review_audit_trail_index_contract_version": (
            PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION
        ),
        "audit_trail_index_id": _safe_phase12r_audit_trail_index_id(
            safe.get("audit_trail_index_id")
        ),
        "source_phase_range": PHASE12R_SOURCE_PHASE_RANGE,
        "audit_trail_index_phase": PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        "authorization_status": PHASE12R_AUTHORIZATION_STATUS,
        "grant_status": PHASE12R_GRANT_STATUS,
        "audit_trail_index_status": PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        "decision_status": _safe_phase12q_decision_status(safe.get("decision_status")),
        "decision_reason_code": _safe_phase12q_decision_reason_code(
            safe.get("decision_reason_code")
        ),
        "request_disposition_status": _safe_phase12q_request_disposition_status(
            safe.get("request_disposition_status")
        ),
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "indexed_workflow_mode_count": _safe_int(safe.get("indexed_workflow_mode_count")),
        "required_future_gate_count": _safe_int(safe.get("required_future_gate_count")),
        "unsatisfied_gate_count": _safe_int(safe.get("unsatisfied_gate_count")),
        "blocker_count": _safe_int(safe.get("blocker_count")),
        "stale_count": _safe_int(safe.get("stale_count")),
        "review_needed_count": _safe_int(safe.get("review_needed_count")),
        "reviewer_class_required_count": _safe_int(safe.get("reviewer_class_required_count")),
        "reviewer_class_represented_count": _safe_int(safe.get("reviewer_class_represented_count")),
        "metadata_only": True,
        "workflow_mode_review_audit_trail_index_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12r_authorizes_runtime": False,
        "phase12r_creates_active_grant": False,
        "phase12r_grants_execution_permission": False,
        "phase12r_allows_workflow_activation": False,
        "phase12r_allows_workflow_execution": False,
        "phase12r_allows_workflow_mode_execution": False,
        "phase12r_allows_runtime_adapter": False,
        "phase12r_allows_model_routing": False,
        "phase12r_allows_provider_execution": False,
        "phase12r_allows_model_execution": False,
        "phase12r_allows_model_loading": False,
        "phase12r_allows_training": False,
        "phase12r_allows_fine_tuning": False,
        "phase12r_allows_code_execution": False,
        "phase12r_allows_experiment_execution": False,
        "phase12r_allows_autonomous_experimentation": False,
        "phase12r_allows_shell_execution": False,
        "phase12r_allows_process_execution": False,
        "phase12r_allows_cache_event_bus_pubsub_runtime": False,
        "phase12r_allows_web_access": False,
        "phase12r_allows_database_ingestion": False,
        "phase12r_allows_database_writes": False,
        "phase12r_allows_query_execution": False,
        "phase12r_allows_web_scraping": False,
        "phase12r_allows_network_calls": False,
        "phase12r_allows_clinical_decision_support": False,
        "phase12r_allows_diagnosis_or_treatment": False,
        "phase12r_allows_medical_advice": False,
        "phase12r_allows_dosing_or_nutrition_prescription": False,
        "phase12r_allows_private_health_data_processing": False,
        "phase12r_allows_device_or_sensor_access": False,
        "phase12r_allows_raw_sensor_processing": False,
        "phase12r_marks_production_ready": False,
        **{field: False for field in _phase12r_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12r_workflow_mode_review_audit_trail_index(
    index: object,
) -> Phase12RWorkflowModeReviewAuditTrailIndexValidationResult:
    """Validate Phase 12R indexes and reject runtime/approval semantics."""

    if not isinstance(index, Mapping):
        return _invalid_phase12r_audit_trail_index_result(
            ("phase12r_audit_trail_index_not_object",),
            "malformed",
            rejected_phase12r_workflow_mode_review_audit_trail_index(),
        )
    privacy_violations = _privacy_violation_count(index)
    authorization_wording = _authorization_wording_count(index)
    unsafe_semantics = _phase12r_unsafe_semantics_count(index)
    errors: list[str] = []
    if PHASE12R_AUDIT_TRAIL_INDEX_REQUIRED_FIELDS - set(index):
        errors.append("phase12r_audit_trail_index_required_field_missing")
    if set(str(key) for key in index) - PHASE12R_AUDIT_TRAIL_INDEX_REQUIRED_FIELDS:
        errors.append("phase12r_audit_trail_index_unknown_field")
    if (
        index.get("workflow_mode_review_audit_trail_index_contract_version")
        != PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION
    ):
        errors.append("phase12r_audit_trail_index_contract_version_unsupported")
    if index.get("audit_trail_index_kind") != PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND:
        errors.append("phase12r_audit_trail_index_kind_invalid")
    if _safe_phase12r_audit_trail_index_id(index.get("audit_trail_index_id")) != index.get(
        "audit_trail_index_id"
    ):
        errors.append("phase12r_audit_trail_index_id_invalid")
    decision_status = _safe_phase12q_decision_status(index.get("decision_status"))
    if decision_status != index.get("decision_status"):
        errors.append("phase12r_decision_status_invalid")
    expected_reason = PHASE12Q_DECISION_STATUS_REASON_CODES.get(decision_status)
    if expected_reason != index.get("decision_reason_code"):
        errors.append("phase12r_decision_reason_code_invalid")
    expected_disposition = PHASE12Q_DECISION_STATUS_DISPOSITIONS.get(decision_status)
    if expected_disposition != index.get("request_disposition_status"):
        errors.append("phase12r_request_disposition_status_invalid")
    expected = {
        "source_phase_range": PHASE12R_SOURCE_PHASE_RANGE,
        "audit_trail_index_phase": PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        "authorization_status": PHASE12R_AUTHORIZATION_STATUS,
        "grant_status": PHASE12R_GRANT_STATUS,
        "audit_trail_index_status": PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        "stale_status": PHASE12R_STALE_STATUS,
        "review_needed_status": PHASE12R_REVIEW_NEEDED_STATUS,
        "stale_review_needed_status": PHASE12R_STALE_REVIEW_NEEDED_STATUS,
        "audit_trail_boundary_statement": PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if index.get(key) != expected_value:
            errors.append("phase12r_audit_trail_index_value_invalid")
            break
    errors.extend(_phase12r_source_reference_errors(index.get("source_phase_references")))
    errors.extend(_phase12r_status_label_errors(index.get("status_labels")))
    errors.extend(_phase12r_indexed_workflow_mode_errors(index.get("indexed_workflow_modes")))
    errors.extend(
        _phase12r_activation_packet_reference_errors(
            index.get("activation_request_packet_reference_metadata")
        )
    )
    errors.extend(
        _phase12r_decision_record_reference_errors(
            index.get("review_decision_record_reference_metadata")
        )
    )
    errors.extend(_phase12r_decision_status_summary_errors(index.get("decision_status_summary")))
    errors.extend(_phase12r_reviewer_class_required_errors(index.get("reviewer_classes_required")))
    errors.extend(
        _phase12r_reviewer_class_represented_errors(index.get("reviewer_classes_represented"))
    )
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "indexed_workflow_mode_count",
        "required_future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
        "stale_count",
        "review_needed_count",
        "reviewer_class_required_count",
        "reviewer_class_represented_count",
    ):
        if not _is_non_negative_int(index.get(field)):
            errors.append("phase12r_audit_trail_index_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": 4,
        "status_label_count": len(PHASE12R_STATUS_LABELS),
        "indexed_workflow_mode_count": len(PHASE12R_WORKFLOW_MODES),
        "required_future_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12R_REQUIRED_FUTURE_GATES)
        + len(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        "stale_count": 0,
        "review_needed_count": 1,
        "reviewer_class_required_count": len(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        "reviewer_class_represented_count": 0,
    }
    for key, expected_value in expected_counts.items():
        if index.get(key) != expected_value:
            errors.append("phase12r_audit_trail_index_count_value_invalid")
            break
    expected_safety = {
        "metadata_only": True,
        "workflow_mode_review_audit_trail_index_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12r_authorizes_runtime": False,
        "phase12r_creates_active_grant": False,
        "phase12r_grants_execution_permission": False,
        "phase12r_allows_workflow_activation": False,
        "phase12r_allows_workflow_execution": False,
        "phase12r_allows_workflow_mode_execution": False,
        "phase12r_allows_runtime_adapter": False,
        "phase12r_allows_model_routing": False,
        "phase12r_allows_provider_execution": False,
        "phase12r_allows_model_execution": False,
        "phase12r_allows_model_loading": False,
        "phase12r_allows_training": False,
        "phase12r_allows_fine_tuning": False,
        "phase12r_allows_code_execution": False,
        "phase12r_allows_experiment_execution": False,
        "phase12r_allows_autonomous_experimentation": False,
        "phase12r_allows_shell_execution": False,
        "phase12r_allows_process_execution": False,
        "phase12r_allows_cache_event_bus_pubsub_runtime": False,
        "phase12r_allows_web_access": False,
        "phase12r_allows_database_ingestion": False,
        "phase12r_allows_database_writes": False,
        "phase12r_allows_query_execution": False,
        "phase12r_allows_web_scraping": False,
        "phase12r_allows_network_calls": False,
        "phase12r_allows_clinical_decision_support": False,
        "phase12r_allows_diagnosis_or_treatment": False,
        "phase12r_allows_medical_advice": False,
        "phase12r_allows_dosing_or_nutrition_prescription": False,
        "phase12r_allows_private_health_data_processing": False,
        "phase12r_allows_device_or_sensor_access": False,
        "phase12r_allows_raw_sensor_processing": False,
        "phase12r_marks_production_ready": False,
    }
    for field, expected_value in expected_safety.items():
        if index.get(field) is not expected_value:
            errors.append("phase12r_audit_trail_index_safety_semantics_invalid")
            break
    for field in _phase12r_runtime_false_fields():
        if index.get(field) is not False:
            errors.append("phase12r_audit_trail_index_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12r_audit_trail_index_privacy_boundary")
    if authorization_wording:
        errors.append("phase12r_audit_trail_index_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12r_audit_trail_index_unsafe_runtime_semantics")
    expected_id = _phase12r_audit_trail_index_id(index)
    if not expected_id:
        errors.append("phase12r_audit_trail_index_payload_not_json")
    elif index.get("audit_trail_index_id") != expected_id:
        errors.append("phase12r_audit_trail_index_id_invalid")
    if errors:
        return _invalid_phase12r_audit_trail_index_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12r_audit_trail_index_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12r_workflow_mode_review_audit_trail_index(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12RWorkflowModeReviewAuditTrailIndexValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(index),
    )


def rejected_phase12r_workflow_mode_review_audit_trail_index() -> dict[str, object]:
    """Return sanitized rejected Phase 12R workflow-mode audit trail index."""

    source_record = rejected_phase12q_workflow_mode_review_decision_record()
    payload = _phase12r_audit_trail_index_payload(
        _phase12r_source_phase_references(source_record),
        source_record,
    )
    return _finalize_phase12r_audit_trail_index(payload)


def phase12s_workflow_mode_review_chain_closeout_summary() -> dict[str, object]:
    """Return the Phase 12S workflow-mode review chain closeout summary.

    The summary closes out the Phase 12N through Phase 12R workflow-mode review
    chain for reviewer/operator navigation only. It does not approve runtime,
    create grants, activate workflow modes, execute code/shell/processes, add
    transport/fabric/P2P behavior, process clinical/private health data, or mark
    deployment or production readiness.
    """

    source_index = phase12r_workflow_mode_review_audit_trail_index()
    source_index_result = validate_phase12r_workflow_mode_review_audit_trail_index(source_index)
    safe_index = (
        source_index_result.sanitized_record
        if source_index_result.compatible
        else rejected_phase12r_workflow_mode_review_audit_trail_index()
    )
    payload = _phase12s_closeout_summary_payload(
        _phase12s_source_phase_references(safe_index),
        safe_index,
    )
    summary = _finalize_phase12s_closeout_summary(payload)
    result = validate_phase12s_workflow_mode_review_chain_closeout_summary(summary)
    return (
        summary
        if result.compatible
        else rejected_phase12s_workflow_mode_review_chain_closeout_summary()
    )


def phase12s_workflow_mode_review_chain_closeout_summary_status_summary() -> dict[str, object]:
    """Return compact Phase 12S status safe for public surfaces."""

    summary = phase12s_workflow_mode_review_chain_closeout_summary()
    result = validate_phase12s_workflow_mode_review_chain_closeout_summary(summary)
    safe = result.sanitized_record
    return {
        "workflow_mode_review_chain_closeout_summary_contract_version": (
            PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION
        ),
        "closeout_summary_id": _safe_phase12s_closeout_summary_id(safe.get("closeout_summary_id")),
        "source_phase_range": PHASE12S_SOURCE_PHASE_RANGE,
        "closeout_summary_phase": PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        "authorization_status": PHASE12S_AUTHORIZATION_STATUS,
        "grant_status": PHASE12S_GRANT_STATUS,
        "summary_status": PHASE12S_SUMMARY_STATUS,
        "review_chain_status": PHASE12S_REVIEW_CHAIN_STATUS,
        "closeout_status": _safe_phase12s_closeout_status(safe.get("closeout_status")),
        "source_phase_reference_count": _safe_int(safe.get("source_phase_reference_count")),
        "workflow_mode_label_count": _safe_int(safe.get("workflow_mode_label_count")),
        "future_gate_count": _safe_int(safe.get("future_gate_count")),
        "unsatisfied_gate_count": _safe_int(safe.get("unsatisfied_gate_count")),
        "blocker_count": _safe_int(safe.get("blocker_count")),
        "metadata_only": True,
        "workflow_mode_review_chain_closeout_summary_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12s_authorizes_runtime": False,
        "phase12s_creates_active_grant": False,
        "phase12s_grants_execution_permission": False,
        "phase12s_allows_workflow_activation": False,
        "phase12s_allows_workflow_execution": False,
        "phase12s_allows_workflow_mode_execution": False,
        "phase12s_allows_runtime_adapter": False,
        "phase12s_allows_model_routing": False,
        "phase12s_allows_provider_execution": False,
        "phase12s_allows_model_execution": False,
        "phase12s_allows_model_loading": False,
        "phase12s_allows_training": False,
        "phase12s_allows_fine_tuning": False,
        "phase12s_allows_code_execution": False,
        "phase12s_allows_shell_execution": False,
        "phase12s_allows_process_execution": False,
        "phase12s_allows_experiment_execution": False,
        "phase12s_allows_autonomous_experimentation": False,
        "phase12s_allows_web_access": False,
        "phase12s_allows_network_behavior": False,
        "phase12s_allows_database_ingestion": False,
        "phase12s_allows_database_writes": False,
        "phase12s_allows_query_execution": False,
        "phase12s_allows_cache_event_bus_pubsub_runtime": False,
        "phase12s_allows_transport_implementation": False,
        "phase12s_allows_fabric_implementation": False,
        "phase12s_allows_p2p_implementation": False,
        "phase12s_allows_clinical_decision_support": False,
        "phase12s_allows_diagnosis_or_treatment": False,
        "phase12s_allows_medical_advice": False,
        "phase12s_allows_dosing_or_nutrition_prescription": False,
        "phase12s_allows_private_health_data_processing": False,
        "phase12s_allows_device_or_sensor_access": False,
        "phase12s_allows_raw_sensor_processing": False,
        "phase12s_marks_deployment_ready": False,
        "phase12s_marks_production_ready": False,
        **{field: False for field in _phase12s_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def validate_phase12s_workflow_mode_review_chain_closeout_summary(
    summary: object,
) -> Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult:
    """Validate Phase 12S summaries and reject runtime/approval semantics."""

    if not isinstance(summary, Mapping):
        return _invalid_phase12s_closeout_summary_result(
            ("phase12s_closeout_summary_not_object",),
            "malformed",
            rejected_phase12s_workflow_mode_review_chain_closeout_summary(),
        )
    privacy_violations = _privacy_violation_count(summary)
    authorization_wording = _authorization_wording_count(summary)
    unsafe_semantics = _phase12s_unsafe_semantics_count(summary)
    errors: list[str] = []
    if PHASE12S_CLOSEOUT_SUMMARY_REQUIRED_FIELDS - set(summary):
        errors.append("phase12s_closeout_summary_required_field_missing")
    if set(str(key) for key in summary) - PHASE12S_CLOSEOUT_SUMMARY_REQUIRED_FIELDS:
        errors.append("phase12s_closeout_summary_unknown_field")
    if (
        summary.get("workflow_mode_review_chain_closeout_summary_contract_version")
        != PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION
    ):
        errors.append("phase12s_closeout_summary_contract_version_unsupported")
    if (
        summary.get("closeout_summary_kind")
        != PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND
    ):
        errors.append("phase12s_closeout_summary_kind_invalid")
    if _safe_phase12s_closeout_summary_id(summary.get("closeout_summary_id")) != summary.get(
        "closeout_summary_id"
    ):
        errors.append("phase12s_closeout_summary_id_invalid")
    closeout_status = _safe_phase12s_closeout_status(summary.get("closeout_status"))
    if closeout_status != summary.get("closeout_status"):
        errors.append("phase12s_closeout_status_invalid")
    expected = {
        "source_phase_range": PHASE12S_SOURCE_PHASE_RANGE,
        "closeout_summary_phase": PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        "authorization_status": PHASE12S_AUTHORIZATION_STATUS,
        "grant_status": PHASE12S_GRANT_STATUS,
        "summary_status": PHASE12S_SUMMARY_STATUS,
        "review_chain_status": PHASE12S_REVIEW_CHAIN_STATUS,
        "reviewer_navigation_summary": PHASE12S_REVIEWER_NAVIGATION_SUMMARY,
        "operator_handoff_summary": PHASE12S_OPERATOR_HANDOFF_SUMMARY,
        "closeout_boundary_statement": PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append("phase12s_closeout_summary_value_invalid")
            break
    errors.extend(_phase12s_source_reference_errors(summary.get("source_phase_references")))
    errors.extend(_phase12s_status_label_errors(summary.get("status_labels")))
    errors.extend(
        _phase12s_workflow_mode_label_coverage_errors(summary.get("workflow_mode_labels_covered"))
    )
    for field in (
        "source_phase_reference_count",
        "status_label_count",
        "workflow_mode_label_count",
        "future_gate_count",
        "unsatisfied_gate_count",
        "blocker_count",
    ):
        if not _is_non_negative_int(summary.get(field)):
            errors.append("phase12s_closeout_summary_count_invalid")
            break
    expected_counts = {
        "source_phase_reference_count": 5,
        "status_label_count": len(PHASE12S_STATUS_LABELS),
        "workflow_mode_label_count": len(PHASE12S_WORKFLOW_MODES),
        "future_gate_count": len(PHASE12S_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12S_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12S_REQUIRED_FUTURE_GATES)
        + len(PHASE12S_REQUIRED_REVIEWER_CLASSES),
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append("phase12s_closeout_summary_count_value_invalid")
            break
    expected_safety = {
        "metadata_only": True,
        "workflow_mode_review_chain_closeout_summary_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12s_authorizes_runtime": False,
        "phase12s_creates_active_grant": False,
        "phase12s_grants_execution_permission": False,
        "phase12s_allows_workflow_activation": False,
        "phase12s_allows_workflow_execution": False,
        "phase12s_allows_workflow_mode_execution": False,
        "phase12s_allows_runtime_adapter": False,
        "phase12s_allows_model_routing": False,
        "phase12s_allows_provider_execution": False,
        "phase12s_allows_model_execution": False,
        "phase12s_allows_model_loading": False,
        "phase12s_allows_training": False,
        "phase12s_allows_fine_tuning": False,
        "phase12s_allows_code_execution": False,
        "phase12s_allows_shell_execution": False,
        "phase12s_allows_process_execution": False,
        "phase12s_allows_experiment_execution": False,
        "phase12s_allows_autonomous_experimentation": False,
        "phase12s_allows_web_access": False,
        "phase12s_allows_network_behavior": False,
        "phase12s_allows_database_ingestion": False,
        "phase12s_allows_database_writes": False,
        "phase12s_allows_query_execution": False,
        "phase12s_allows_cache_event_bus_pubsub_runtime": False,
        "phase12s_allows_transport_implementation": False,
        "phase12s_allows_fabric_implementation": False,
        "phase12s_allows_p2p_implementation": False,
        "phase12s_allows_clinical_decision_support": False,
        "phase12s_allows_diagnosis_or_treatment": False,
        "phase12s_allows_medical_advice": False,
        "phase12s_allows_dosing_or_nutrition_prescription": False,
        "phase12s_allows_private_health_data_processing": False,
        "phase12s_allows_device_or_sensor_access": False,
        "phase12s_allows_raw_sensor_processing": False,
        "phase12s_marks_deployment_ready": False,
        "phase12s_marks_production_ready": False,
    }
    for field, expected_value in expected_safety.items():
        if summary.get(field) is not expected_value:
            errors.append("phase12s_closeout_summary_safety_semantics_invalid")
            break
    for field in _phase12s_runtime_false_fields():
        if summary.get(field) is not False:
            errors.append("phase12s_closeout_summary_runtime_implied")
            break
    if privacy_violations:
        errors.append("phase12s_closeout_summary_privacy_boundary")
    if authorization_wording:
        errors.append("phase12s_closeout_summary_authorization_wording")
    if unsafe_semantics:
        errors.append("phase12s_closeout_summary_unsafe_runtime_semantics")
    expected_id = _phase12s_closeout_summary_id(summary)
    if not expected_id:
        errors.append("phase12s_closeout_summary_payload_not_json")
    elif summary.get("closeout_summary_id") != expected_id:
        errors.append("phase12s_closeout_summary_id_invalid")
    if errors:
        return _invalid_phase12s_closeout_summary_result(
            tuple(sorted(set(errors))),
            (
                "unsupported_version"
                if "phase12s_closeout_summary_contract_version_unsupported" in errors
                else "incompatible"
            ),
            rejected_phase12s_workflow_mode_review_chain_closeout_summary(),
            privacy_violation_count=privacy_violations,
            authorization_wording_count=authorization_wording,
        )
    return Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult(
        classification="compatible",
        valid=True,
        errors=(),
        privacy_violation_count=0,
        authorization_wording_count=0,
        sanitized_record=dict(summary),
    )


def rejected_phase12s_workflow_mode_review_chain_closeout_summary() -> dict[str, object]:
    """Return sanitized rejected Phase 12S workflow-mode closeout summary."""

    source_index = rejected_phase12r_workflow_mode_review_audit_trail_index()
    payload = _phase12s_closeout_summary_payload(
        _phase12s_source_phase_references(source_index),
        source_index,
    )
    return _finalize_phase12s_closeout_summary(payload)


def _phase12a_source_governance_closeout(
    closeout: Mapping[str, object],
) -> dict[str, object]:
    return {
        "artifact_kind": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND,
        "contract_version": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
        "phase_range": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        "final_status": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        "runtime_authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "missing_future_gate_count": _safe_int(closeout.get("missing_future_gate_count")),
        "unresolved_review_count": _safe_int(closeout.get("unresolved_review_count")),
        "blocker_count": _safe_int(closeout.get("blocker_count")),
        "stale_count": _safe_int(closeout.get("stale_count")),
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12a_source_runtime_gap_ledger(
    ledger: Mapping[str, object],
) -> dict[str, object]:
    return {
        "artifact_kind": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND,
        "contract_version": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
        "source_phase_range": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "missing_future_gate_count": _safe_int(ledger.get("missing_future_gate_count")),
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12a_future_required_gates() -> list[dict[str, object]]:
    return [
        {
            "gate_id": gate_id,
            "gate_status": PHASE12A_FUTURE_GATE_STATUS,
            "required_before_runtime_authorization": True,
            "satisfied_by_phase12a": False,
            "passed": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for gate_id in PHASE12A_FUTURE_REQUIRED_GATES
    ]


def _phase12b_source_design_charter(
    charter: Mapping[str, object],
) -> dict[str, object]:
    return {
        "artifact_kind": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "contract_version": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION,
        "charter_id": _safe_phase12a_charter_id(charter.get("charter_id")),
        "source_phase_range": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE,
        "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "charter_status": PHASE12A_CHARTER_STATUS,
        "future_required_gate_count": _safe_int(charter.get("future_required_gate_count")),
        "satisfied_future_gate_count": 0,
        "passed_future_gate_count": 0,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12b_requested_domains() -> list[dict[str, object]]:
    return [
        {
            "domain_label": domain,
            "request_status": PHASE12B_REQUEST_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for domain in PHASE12B_REQUESTED_DOMAINS
    ]


def _phase12b_required_reviewer_roles() -> list[dict[str, object]]:
    return [
        {
            "reviewer_role": reviewer_role,
            "review_status": PHASE12B_REVIEWER_ROLE_STATUS,
            "metadata_only": True,
            "satisfied_by_phase12b": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for reviewer_role in PHASE12B_REQUIRED_REVIEWER_ROLES
    ]


def _phase12b_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "gate_id": gate_id,
            "reviewer_role": reviewer_role,
            "gate_status": PHASE12B_FUTURE_GATE_STATUS,
            "required_before_runtime_authorization": True,
            "submitted_by_phase12b": False,
            "satisfied_by_phase12b": False,
            "passed": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for gate_id, reviewer_role in PHASE12B_REQUIRED_FUTURE_GATES
    ]


def _phase12c_source_record_candidate(
    record: Mapping[str, object],
) -> dict[str, object]:
    return {
        "record_kind": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "contract_version": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION,
        "record_id": _safe_phase12b_record_id(record.get("record_id")),
        "source_phase": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE,
        "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
        "decision_status": PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
        "grant_status": PHASE12B_GRANT_STATUS,
        "record_candidate_status": PHASE12B_RECORD_CANDIDATE_STATUS,
        "requested_domain_count": _safe_int(record.get("requested_domain_count")),
        "required_future_reviewer_role_count": _safe_int(
            record.get("required_future_reviewer_role_count")
        ),
        "required_future_gate_count": _safe_int(record.get("required_future_gate_count")),
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12c_capability_labels() -> list[dict[str, object]]:
    return [
        {
            "capability_label": label,
            "capability_status": PHASE12C_CAPABILITY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12C_ALLOWED_CAPABILITY_LABELS
    ]


def _phase12d_consent_gate_profile_payload(
    charter: Mapping[str, object],
    record: Mapping[str, object],
    capability_profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "consent_gate_profile_contract_version": (PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION),
        "profile_kind": PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "consent_gate_profile_id": None,
        "source_phase_range": PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE,
        "source_design_charter": _phase12d_source_design_charter(charter),
        "source_record_candidate": _phase12d_source_record_candidate(record),
        "source_capability_profile": _phase12d_source_capability_profile(capability_profile),
        "consent_phase": PHASE12D_CONSENT_PHASE,
        "authorization_status": PHASE12D_AUTHORIZATION_STATUS,
        "grant_status": PHASE12D_GRANT_STATUS,
        "consent_gate_status": PHASE12D_CONSENT_GATE_STATUS,
        "phase12d_satisfies_consent_gates": False,
        "phase12d_profiles_are_consents_approvals_grants_or_permissions": False,
        "capability_categories": _phase12d_capability_categories(),
        "capability_category_count": len(PHASE12D_CAPABILITY_CATEGORIES),
        "required_future_gates": _phase12d_required_future_gates(),
        "required_future_gate_count": len(PHASE12D_REQUIRED_FUTURE_GATES),
        "satisfied_consent_gate_count": 0,
        "passed_consent_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "screen_capture_execution_granted": False,
        "ocr_execution_granted": False,
        "camera_capture_execution_granted": False,
        "microphone_capture_execution_granted": False,
        "clipboard_capture_execution_granted": False,
        "recording_execution_granted": False,
        "click_input_automation_execution_granted": False,
        "overlay_display_execution_granted": False,
        "notification_sending_execution_granted": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12d_source_design_charter(
    charter: Mapping[str, object],
) -> dict[str, object]:
    return _phase12b_source_design_charter(charter)


def _phase12d_source_record_candidate(
    record: Mapping[str, object],
) -> dict[str, object]:
    return _phase12c_source_record_candidate(record)


def _phase12d_source_capability_profile(
    profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "profile_kind": PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "contract_version": PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION,
        "profile_id": _safe_phase12c_profile_id(profile.get("profile_id")),
        "source_phase": PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE,
        "supervision_phase": PHASE12C_SUPERVISION_PHASE,
        "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
        "grant_status": PHASE12C_GRANT_STATUS,
        "profile_status": PHASE12C_PROFILE_STATUS,
        "capability_label_count": _safe_int(profile.get("capability_label_count")),
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12d_capability_categories() -> list[dict[str, object]]:
    return [
        {
            "capability_category": category,
            "category_status": PHASE12D_CAPABILITY_CATEGORY_STATUS,
            "metadata_only": True,
            "consent_granted_by_phase12d": False,
            "authorization_granted_by_phase12d": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for category in PHASE12D_CAPABILITY_CATEGORIES
    ]


def _phase12d_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "gate_id": gate_id,
            "gate_status": PHASE12D_FUTURE_GATE_STATUS,
            "required_before_visual_desktop_runtime": True,
            "satisfied_by_phase12d": False,
            "passed": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for gate_id in PHASE12D_REQUIRED_FUTURE_GATES
    ]


def _phase12e_physiological_sensor_profile_payload(
    charter: Mapping[str, object],
    record: Mapping[str, object],
    consent_profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "physiological_sensor_profile_contract_version": (
            PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "physiological_sensor_profile_id": None,
        "source_phase_range": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE,
        "source_design_charter": _phase12e_source_design_charter(charter),
        "source_record_candidate": _phase12e_source_record_candidate(record),
        "source_consent_gate_profile": _phase12e_source_consent_gate_profile(consent_profile),
        "source_sensor_evidence_boundaries": _phase12e_source_sensor_evidence_boundaries(),
        "sensor_phase": PHASE12E_SENSOR_PHASE,
        "authorization_status": PHASE12E_AUTHORIZATION_STATUS,
        "grant_status": PHASE12E_GRANT_STATUS,
        "profile_status": PHASE12E_PROFILE_STATUS,
        "phase12e_profiles_are_approvals_grants_or_permissions": False,
        "phase12e_satisfies_sensor_gates": False,
        "sensor_capability_labels": _phase12e_sensor_capability_labels(),
        "sensor_capability_label_count": len(PHASE12E_SENSOR_CAPABILITY_LABELS),
        "non_diagnostic_boundaries": _phase12e_non_diagnostic_boundaries(),
        "non_diagnostic_boundary_count": len(PHASE12E_NON_DIAGNOSTIC_BOUNDARIES),
        "required_future_gates": _phase12e_required_future_gates(),
        "required_future_gate_count": len(PHASE12E_REQUIRED_FUTURE_GATES),
        "satisfied_sensor_gate_count": 0,
        "passed_sensor_gate_count": 0,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "bia_measurement_execution_granted": False,
        "device_connection_execution_granted": False,
        "bluetooth_execution_granted": False,
        "usb_execution_granted": False,
        "cloud_sync_execution_granted": False,
        "acoustic_processing_execution_granted": False,
        "ultrasound_processing_execution_granted": False,
        "medical_inference_execution_granted": False,
        "clinical_recommendation_execution_granted": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12e_source_design_charter(
    charter: Mapping[str, object],
) -> dict[str, object]:
    return _phase12d_source_design_charter(charter)


def _phase12e_source_record_candidate(
    record: Mapping[str, object],
) -> dict[str, object]:
    return _phase12d_source_record_candidate(record)


def _phase12e_source_consent_gate_profile(
    profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "profile_kind": PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "contract_version": PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION,
        "consent_gate_profile_id": _safe_phase12d_profile_id(
            profile.get("consent_gate_profile_id")
        ),
        "source_phase_range": PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE,
        "consent_phase": PHASE12D_CONSENT_PHASE,
        "authorization_status": PHASE12D_AUTHORIZATION_STATUS,
        "grant_status": PHASE12D_GRANT_STATUS,
        "consent_gate_status": PHASE12D_CONSENT_GATE_STATUS,
        "capability_category_count": _safe_int(profile.get("capability_category_count")),
        "required_future_gate_count": _safe_int(profile.get("required_future_gate_count")),
        "satisfied_consent_gate_count": 0,
        "passed_consent_gate_count": 0,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12e_source_sensor_evidence_boundaries() -> dict[str, object]:
    return {
        "boundary_kind": "existing-sensor-evidence-boundaries",
        "source_phase_range": "7A-11M",
        "boundary_status": PHASE12E_SENSOR_EVIDENCE_BOUNDARY_STATUS,
        "boundary_labels": list(PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES),
        "boundary_label_count": len(PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES),
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12e_sensor_capability_labels() -> list[dict[str, object]]:
    return [
        {
            "sensor_capability_label": label,
            "capability_status": PHASE12E_CAPABILITY_STATUS,
            "metadata_only": True,
            "sensor_enabled_by_phase12e": False,
            "measurement_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12E_SENSOR_CAPABILITY_LABELS
    ]


def _phase12e_non_diagnostic_boundaries() -> list[dict[str, object]]:
    return [
        {
            "boundary_id": boundary_id,
            "boundary_status": PHASE12E_NON_DIAGNOSTIC_BOUNDARY_STATUS,
            "metadata_only": True,
            "satisfied_by_phase12e": False,
            "diagnosis_permitted": False,
            "clinical_recommendation_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for boundary_id in PHASE12E_NON_DIAGNOSTIC_BOUNDARIES
    ]


def _phase12e_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "gate_id": gate_id,
            "gate_status": PHASE12E_FUTURE_GATE_STATUS,
            "required_before_physiological_sensor_runtime": True,
            "satisfied_by_phase12e": False,
            "passed": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for gate_id in PHASE12E_REQUIRED_FUTURE_GATES
    ]


def _phase12f_secure_drop_consumer_boundary_payload(
    charter: Mapping[str, object],
    record: Mapping[str, object],
    visual_profile: Mapping[str, object],
    consent_profile: Mapping[str, object],
    physiological_profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "secure_drop_consumer_boundary_contract_version": (
            PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION
        ),
        "boundary_kind": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "secure_drop_consumer_boundary_id": None,
        "source_phase_range": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE,
        "source_design_charter": _phase12f_source_design_charter(charter),
        "source_record_candidate": _phase12f_source_record_candidate(record),
        "source_visual_supervision_profile": _phase12f_source_visual_supervision_profile(
            visual_profile
        ),
        "source_consent_gate_profile": _phase12f_source_consent_gate_profile(consent_profile),
        "source_physiological_sensor_profile": _phase12f_source_physiological_sensor_profile(
            physiological_profile
        ),
        "source_content_fabric_secure_drop_contract": (
            _phase12f_source_content_fabric_secure_drop_contract()
        ),
        "consumer_phase": PHASE12F_CONSUMER_PHASE,
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "canonical_reference": PHASE12F_CANONICAL_REFERENCE,
        "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
        "grant_status": PHASE12F_GRANT_STATUS,
        "boundary_status": PHASE12F_BOUNDARY_STATUS,
        "phase12f_implements_secure_drop": False,
        "phase12f_authorizes_secure_drop": False,
        "phase12f_profiles_are_approvals_grants_or_permissions": False,
        "allowed_future_user_selected_artifact_labels": _phase12f_allowed_artifact_labels(),
        "allowed_future_user_selected_artifact_label_count": len(
            PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS
        ),
        "prohibited_future_autonomous_sources": _phase12f_prohibited_autonomous_sources(),
        "prohibited_future_autonomous_source_count": len(PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES),
        "encryption_required": True,
        "encryption_requirement_status": PHASE12F_ENCRYPTION_REQUIREMENT_STATUS,
        "concealment_optional": True,
        "concealment_status": PHASE12F_CONCEALMENT_STATUS,
        "concealment_is_security_boundary": False,
        "audit_metadata_only_required": True,
        "audit_requirement_status": PHASE12F_AUDIT_REQUIREMENT_STATUS,
        "jules_security_review_required_for_validator_or_authorization_semantics": True,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "agent_invocation_permitted": False,
        "automation_invocation_permitted": False,
        "connector_invocation_permitted": False,
        "scheduled_task_invocation_permitted": False,
        "avatar_invocation_permitted": False,
        "server_endpoint_invocation_permitted": False,
        "workflow_invocation_permitted": False,
        "filesystem_autoscan_permitted": False,
        "vault_env_secret_access_permitted": False,  # nosec B105
        "raw_sensor_capture_attachment_permitted": False,
        "automatic_document_attachment_permitted": False,
        "crypto_implementation_added": False,
        "transport_implementation_added": False,
        "stego_implementation_added": False,
        "keyring_implementation_added": False,
        "did_implementation_added": False,
        "send_inbox_ui_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "adapter_execution_granted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "active_grant_present": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12f_source_design_charter(
    charter: Mapping[str, object],
) -> dict[str, object]:
    return _phase12e_source_design_charter(charter)


def _phase12f_source_record_candidate(
    record: Mapping[str, object],
) -> dict[str, object]:
    return _phase12e_source_record_candidate(record)


def _phase12f_source_visual_supervision_profile(
    profile: Mapping[str, object],
) -> dict[str, object]:
    return _phase12d_source_capability_profile(profile)


def _phase12f_source_consent_gate_profile(
    profile: Mapping[str, object],
) -> dict[str, object]:
    return _phase12e_source_consent_gate_profile(profile)


def _phase12f_source_physiological_sensor_profile(
    profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "profile_kind": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "contract_version": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION,
        "physiological_sensor_profile_id": _safe_phase12e_profile_id(
            profile.get("physiological_sensor_profile_id")
        ),
        "source_phase_range": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE,
        "sensor_phase": PHASE12E_SENSOR_PHASE,
        "authorization_status": PHASE12E_AUTHORIZATION_STATUS,
        "grant_status": PHASE12E_GRANT_STATUS,
        "profile_status": PHASE12E_PROFILE_STATUS,
        "sensor_capability_label_count": _safe_int(profile.get("sensor_capability_label_count")),
        "non_diagnostic_boundary_count": _safe_int(profile.get("non_diagnostic_boundary_count")),
        "required_future_gate_count": _safe_int(profile.get("required_future_gate_count")),
        "satisfied_sensor_gate_count": 0,
        "passed_sensor_gate_count": 0,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12f_source_content_fabric_secure_drop_contract() -> dict[str, object]:
    return {
        "source_kind": "content-fabric-secure-drop-design-contract",
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "canonical_reference": PHASE12F_CANONICAL_REFERENCE,
        "repository": "Ardynai/kortex-audio",
        "merge_commit_sha": PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
        "secure_drop_contract_version": 1,
        "contract_status": PHASE12F_CANONICAL_CONTRACT_STATUS,
        "design_contract_only": True,
        "somatic_owns_secure_drop_implementation": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12f_allowed_artifact_labels() -> list[dict[str, object]]:
    return [
        {
            "artifact_label": label,
            "artifact_status": PHASE12F_ARTIFACT_STATUS,
            "metadata_only": True,
            "explicit_user_action_required": True,
            "selected_by_phase12f": False,
            "send_permitted": False,
            "receive_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS
    ]


def _phase12f_prohibited_autonomous_sources() -> list[dict[str, object]]:
    return [
        {
            "source_label": source,
            "source_status": PHASE12F_PROHIBITED_SOURCE_STATUS,
            "metadata_only": True,
            "permitted_by_phase12f": False,
            "send_permitted": False,
            "receive_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for source in PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES
    ]


def _phase12g_production_readiness_coverage_matrix_payload(
    secure_drop_boundary: Mapping[str, object],
) -> dict[str, object]:
    counts = _phase12g_responsibility_counts()
    return {
        "production_readiness_matrix_contract_version": (
            PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION
        ),
        "matrix_kind": PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "production_readiness_matrix_id": None,
        "source_phase_range": PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE,
        "source_secure_drop_consumer_boundary": (
            _phase12g_source_secure_drop_consumer_boundary(secure_drop_boundary)
        ),
        "readiness_phase": PHASE12G_READINESS_PHASE,
        "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
        "grant_status": PHASE12G_GRANT_STATUS,
        "matrix_status": PHASE12G_MATRIX_STATUS,
        "status_labels": _phase12g_status_labels(),
        "status_label_count": len(PHASE12G_STATUS_LABELS),
        "production_readiness_areas": _phase12g_production_readiness_areas(),
        "production_readiness_area_count": len(PHASE12G_PRODUCTION_READINESS_AREAS),
        "somatic_direct_area_count": counts["direct"],
        "somatic_boundary_only_area_count": counts["boundary-only"],
        "external_owner_area_count": counts["external-owner"],
        "not_applicable_yet_area_count": counts["not-applicable-yet"],
        "phase12g_makes_somatic_production_ready": False,
        "phase12g_authorizes_runtime": False,
        "phase12g_coverage_labels_are_metadata_only": True,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "security_review_required_before_production_hardening": True,
        "frontend_implementation_added": False,
        "backend_service_added": False,
        "production_api_service_added": False,
        "database_storage_added": False,
        "auth_runtime_added": False,
        "rate_limiting_runtime_added": False,
        "cache_runtime_added": False,
        "cdn_runtime_added": False,
        "load_balancer_runtime_added": False,
        "logging_service_added": False,
        "secrets_backend_runtime_added": False,
        "service_registry_runtime_added": False,
        "deployment_code_added": False,
        "hosting_runtime_added": False,
        "cloud_compute_runtime_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "device_connection_execution_granted": False,
        "sensor_processing_execution_granted": False,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "active_grant_present": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12g_source_secure_drop_consumer_boundary(
    boundary: Mapping[str, object],
) -> dict[str, object]:
    return {
        "boundary_kind": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "contract_version": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION,
        "secure_drop_consumer_boundary_id": _safe_phase12f_boundary_id(
            boundary.get("secure_drop_consumer_boundary_id")
        ),
        "source_phase_range": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE,
        "consumer_phase": PHASE12F_CONSUMER_PHASE,
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
        "grant_status": PHASE12F_GRANT_STATUS,
        "boundary_status": PHASE12F_BOUNDARY_STATUS,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12g_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "coverage_status": PHASE12G_COVERAGE_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12G_STATUS_LABELS
    ]


def _phase12g_production_readiness_areas() -> list[dict[str, object]]:
    return [
        {
            "area_id": area_id,
            "area_label": area_label,
            "somatic_responsibility": responsibility,
            "likely_repo_family_owner": owner,
            "coverage_status": PHASE12G_COVERAGE_STATUS,
            "current_coverage_summary": current_coverage,
            "remaining_gap_summary": remaining_gap,
            "blocked_runtime_requirement": blocked_requirement,
            "review_requirement": review_requirement,
            "metadata_only": True,
            "phase12g_area_grants_runtime": False,
            "external_owner_entry_grants_runtime": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for (
            area_id,
            area_label,
            responsibility,
            owner,
            current_coverage,
            remaining_gap,
            blocked_requirement,
            review_requirement,
        ) in PHASE12G_PRODUCTION_READINESS_AREAS
    ]


def _phase12g_responsibility_counts() -> dict[str, int]:
    return {
        responsibility: sum(
            1 for area in PHASE12G_PRODUCTION_READINESS_AREAS if area[2] == responsibility
        )
        for responsibility in PHASE12G_SOMATIC_RESPONSIBILITIES
    }


def _phase12h_standalone_ownership_matrix_payload(
    source_matrix: Mapping[str, object],
) -> dict[str, object]:
    return {
        "standalone_ownership_matrix_contract_version": (
            PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION
        ),
        "matrix_kind": PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        "standalone_ownership_matrix_id": None,
        "source_phase": PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE,
        "source_production_readiness_coverage_matrix": _phase12h_source_matrix_summary(
            source_matrix
        ),
        "readiness_phase": PHASE12H_READINESS_PHASE,
        "authorization_status": PHASE12H_AUTHORIZATION_STATUS,
        "grant_status": PHASE12H_GRANT_STATUS,
        "matrix_status": PHASE12H_MATRIX_STATUS,
        "status_labels": _phase12h_status_labels(),
        "status_label_count": len(PHASE12H_STATUS_LABELS),
        "standalone_ownership_entries": _phase12h_standalone_ownership_entries(),
        "standalone_ownership_entry_count": len(PHASE12H_SOMATIC_STANDALONE_AREAS),
        "optional_integration_peer_count": _phase12h_optional_peer_count(),
        "somatic_standalone_area_count": len(PHASE12G_PRODUCTION_READINESS_AREAS),
        "repo_production_ready_count": 0,
        "phase12h_marks_somatic_production_ready": False,
        "phase12h_authorizes_runtime": False,
        "somatic_standalone_ownership_retained": True,
        "external_integrations_optional": True,
        "optional_peer_labels_are_integration_metadata_only": True,
        "external_repo_integration_replaces_somatic_standalone_path": False,
        "cross_repo_mutation_permitted": False,
        "external_repo_tasks_executed_by_somatic": False,
        "standalone_ui_statement": PHASE12H_STANDALONE_UI_STATEMENT,
        "locus_optional_ui_statement": PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT,
        "peer_integration_statement": PHASE12H_PEER_INTEGRATION_STATEMENT,
        "secure_drop_statement": PHASE12H_SECURE_DROP_STATEMENT,
        "phase12h_non_authorization_statement": PHASE12H_NON_AUTHORIZATION_STATEMENT,
        "jules_review_required_for_validator_or_authorization_semantics": True,
        "security_review_required_before_production_hardening": True,
        "frontend_implementation_added": False,
        "backend_service_added": False,
        "production_api_service_added": False,
        "database_storage_added": False,
        "auth_runtime_added": False,
        "rate_limiting_runtime_added": False,
        "cache_runtime_added": False,
        "cdn_runtime_added": False,
        "load_balancer_runtime_added": False,
        "logging_service_added": False,
        "secrets_backend_runtime_added": False,
        "service_registry_runtime_added": False,
        "service_discovery_runtime_added": False,
        "deployment_code_added": False,
        "hosting_runtime_added": False,
        "cloud_compute_runtime_added": False,
        "network_call_execution_granted": False,
        "runtime_adapter_execution_granted": False,
        "device_connection_execution_granted": False,
        "sensor_processing_execution_granted": False,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "provider_execution_granted": False,
        "model_execution_granted": False,
        "active_grant_present": False,
        "real_mode_authorization_added": False,
        "production_ready": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12h_source_matrix_summary(matrix: Mapping[str, object]) -> dict[str, object]:
    return {
        "matrix_kind": PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "contract_version": PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION,
        "production_readiness_matrix_id": _safe_phase12g_matrix_id(
            matrix.get("production_readiness_matrix_id")
        ),
        "source_phase_range": PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE,
        "readiness_phase": PHASE12G_READINESS_PHASE,
        "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
        "grant_status": PHASE12G_GRANT_STATUS,
        "matrix_status": PHASE12G_MATRIX_STATUS,
        "production_readiness_area_count": _safe_int(matrix.get("production_readiness_area_count")),
        "phase12g_makes_somatic_production_ready": False,
        "phase12g_authorizes_runtime": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12h_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "entry_status": PHASE12H_ENTRY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12H_STATUS_LABELS
    ]


def _phase12h_standalone_ownership_entries() -> list[dict[str, object]]:
    return [
        {
            "production_area_id": area_id,
            "entry_status": PHASE12H_ENTRY_STATUS,
            "somatic_standalone_responsibility": responsibility,
            "current_somatic_coverage": current_coverage,
            "remaining_somatic_gap": remaining_gap,
            "optional_integration_peers": _phase12h_optional_integration_peers(peers),
            "optional_integration_peer_count": len(peers),
            "external_integration_optional": True,
            "external_integration_replaces_somatic_standalone_path": False,
            "runtime_blocked": True,
            "review_requirement": review_requirement,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for area_id, responsibility, current_coverage, remaining_gap, peers, review_requirement in (
            PHASE12H_SOMATIC_STANDALONE_AREAS
        )
    ]


def _phase12h_optional_integration_peers(
    peers: tuple[tuple[str, str, str], ...],
) -> list[dict[str, object]]:
    return [
        {
            "peer_label": peer_label,
            "integration_role": integration_role,
            "peer_status": PHASE12H_OPTIONAL_PEER_STATUS,
            "integration_summary": integration_summary,
            "optional_integration_metadata_only": True,
            "required_dependency_for_somatic": False,
            "replaces_somatic_standalone_path": False,
            "runtime_grant_created": False,
            "cross_repo_mutation_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for peer_label, integration_role, integration_summary in peers
    ]


def _phase12h_optional_peer_count() -> int:
    return sum(len(peers) for _, _, _, _, peers, _ in PHASE12H_SOMATIC_STANDALONE_AREAS)


def _phase12i_knowledge_capability_profile_payload(
    source_references: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "integrative_herbal_nutrition_profile_contract_version": (
            PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        "profile_id": None,
        "source_phase_range": PHASE12I_SOURCE_PHASE_RANGE,
        "source_phase_references": source_references,
        "source_phase_reference_count": len(PHASE12I_SOURCE_REFERENCE_PHASES),
        "capability_phase": PHASE12I_CAPABILITY_PHASE,
        "authorization_status": PHASE12I_AUTHORIZATION_STATUS,
        "grant_status": PHASE12I_GRANT_STATUS,
        "profile_status": PHASE12I_PROFILE_STATUS,
        "status_labels": _phase12i_status_labels(),
        "status_label_count": len(PHASE12I_STATUS_LABELS),
        "user_preference_modes": _phase12i_user_preference_modes(),
        "user_preference_mode_count": len(PHASE12I_USER_PREFERENCE_MODES),
        "specialist_profile_labels": _phase12i_specialist_profile_labels(),
        "specialist_profile_label_count": len(PHASE12I_SPECIALIST_PROFILE_LABELS),
        "source_class_labels": _phase12i_source_class_labels(),
        "source_class_label_count": len(PHASE12I_SOURCE_CLASS_LABELS),
        "required_future_gates": _phase12i_required_future_gates(),
        "required_future_gate_count": len(PHASE12I_REQUIRED_FUTURE_GATES),
        "medical_boundary_statement": PHASE12I_MEDICAL_BOUNDARY_STATEMENT,
        "western_medicine_boundary_statement": PHASE12I_WESTERN_MEDICINE_STATEMENT,
        "natural_remedy_boundary_statement": PHASE12I_NATURAL_REMEDY_STATEMENT,
        "food_cure_boundary_statement": PHASE12I_FOOD_CURE_STATEMENT,
        "safety_warning_preservation_statement": PHASE12I_SAFETY_WARNING_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "medical_safety_review_required": True,
        "jules_human_review_required_for_validator_or_medical_safety_semantics": True,
        "phase12i_provides_medical_advice": False,
        "phase12i_authorizes_runtime": False,
        "phase12i_suppresses_safety_warnings": False,
        "phase12i_claims_western_medicine_invalid": False,
        "phase12i_claims_natural_remedies_safe_by_default": False,
        "phase12i_claims_food_cures_disease": False,
        "emergency_escalation_preserved": True,
        "contraindication_warnings_preserved": True,
        "medication_interaction_warnings_preserved": True,
        "pregnancy_liver_kidney_cardiac_risk_warnings_preserved": True,
        "eating_disorder_risk_warnings_preserved": True,
        "toxicity_warnings_preserved": True,
        "contamination_adulteration_warnings_preserved": True,
        **{field: False for field in _phase12i_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12i_source_phase_references(
    phase12a_charter: Mapping[str, object],
    phase12b_record: Mapping[str, object],
    phase12c_profile: Mapping[str, object],
    phase12d_profile: Mapping[str, object],
    phase12e_profile: Mapping[str, object],
    phase12f_boundary: Mapping[str, object],
    phase12g_matrix: Mapping[str, object],
    phase12h_matrix: Mapping[str, object],
) -> list[dict[str, object]]:
    payloads = (
        phase12a_charter,
        phase12b_record,
        phase12c_profile,
        phase12d_profile,
        phase12e_profile,
        phase12f_boundary,
        phase12g_matrix,
        phase12h_matrix,
    )
    return [
        {
            "phase_label": phase_label,
            "source_kind": source_kind,
            "source_reference_id": _safe_phase12i_source_reference_id(
                payload.get(reference_key),
                prefix,
            ),
            "reference_status": PHASE12I_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for payload, (phase_label, source_kind, reference_key, prefix) in zip(
            payloads,
            PHASE12I_SOURCE_REFERENCE_PHASES,
            strict=True,
        )
    ]


def _phase12i_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12I_LABEL_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12I_STATUS_LABELS
    ]


def _phase12i_user_preference_modes() -> list[dict[str, object]]:
    return [
        {
            "preference_mode_label": label,
            "label_status": PHASE12I_LABEL_STATUS,
            "metadata_only": True,
            "safety_warnings_preserved": True,
            "emergency_escalation_preserved": True,
            "preference_cannot_suppress_warnings": True,
            "medical_advice_provided": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12I_USER_PREFERENCE_MODES
    ]


def _phase12i_specialist_profile_labels() -> list[dict[str, object]]:
    return [
        {
            "specialist_profile_label": label,
            "profile_status": PHASE12I_SPECIALIST_PROFILE_STATUS,
            "metadata_only": True,
            "review_profile_only": True,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "clinical_recommendation_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12I_SPECIALIST_PROFILE_LABELS
    ]


def _phase12i_source_class_labels() -> list[dict[str, object]]:
    return [
        {
            "source_class_label": label,
            "source_class_status": PHASE12I_SOURCE_CLASS_STATUS,
            "metadata_only": True,
            "provenance_review_required": True,
            "ingestion_permitted": False,
            "web_scraping_permitted": False,
            "database_ingestion_permitted": False,
            "network_call_execution_granted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12I_SOURCE_CLASS_LABELS
    ]


def _phase12i_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12I_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12I_REQUIRED_FUTURE_GATES
    ]


def _phase12k_external_compute_quantum_profile_payload(
    source_references: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "external_compute_quantum_profile_contract_version": (
            PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        "profile_id": None,
        "source_phase_range": PHASE12K_SOURCE_PHASE_RANGE,
        "source_phase_references": source_references,
        "source_phase_reference_count": len(PHASE12K_SOURCE_REFERENCE_PHASES),
        "capability_phase": PHASE12K_CAPABILITY_PHASE,
        "authorization_status": PHASE12K_AUTHORIZATION_STATUS,
        "grant_status": PHASE12K_GRANT_STATUS,
        "profile_status": PHASE12K_PROFILE_STATUS,
        "credential_policy": PHASE12K_CREDENTIAL_POLICY,
        "human_approval_required": True,
        "cost_guard_required": True,
        "private_health_data_allowed": False,
        "clinical_decision_support_allowed": False,
        "diagnosis_or_treatment_allowed": False,
        "status_labels": _phase12k_status_labels(),
        "status_label_count": len(PHASE12K_STATUS_LABELS),
        "backend_options": _phase12k_backend_options(),
        "backend_option_count": len(PHASE12K_BACKEND_OPTION_LABELS),
        "workload_classes": _phase12k_workload_classes(),
        "workload_class_count": len(PHASE12K_WORKLOAD_CLASSES),
        "required_future_gates": _phase12k_required_future_gates(),
        "required_future_gate_count": len(PHASE12K_REQUIRED_FUTURE_GATES),
        "compute_boundary_statement": PHASE12K_COMPUTE_BOUNDARY_STATEMENT,
        "medical_boundary_statement": PHASE12K_MEDICAL_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "jules_human_review_required_for_validator_or_medical_safety_semantics": True,
        "phase12k_authorizes_runtime": False,
        "phase12k_allows_external_compute_execution": False,
        "phase12k_allows_quantum_backend_execution": False,
        "phase12k_allows_private_health_data_processing": False,
        "phase12k_provides_medical_advice": False,
        "phase12k_allows_diagnosis_or_treatment": False,
        **{field: False for field in _phase12k_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12k_source_phase_references(
    phase12a_charter: Mapping[str, object],
    phase12b_record: Mapping[str, object],
    phase12c_profile: Mapping[str, object],
    phase12d_profile: Mapping[str, object],
    phase12e_profile: Mapping[str, object],
    phase12f_boundary: Mapping[str, object],
    phase12g_matrix: Mapping[str, object],
    phase12h_matrix: Mapping[str, object],
    phase12i_profile: Mapping[str, object],
) -> list[dict[str, object]]:
    payloads = (
        phase12a_charter,
        phase12b_record,
        phase12c_profile,
        phase12d_profile,
        phase12e_profile,
        phase12f_boundary,
        phase12g_matrix,
        phase12h_matrix,
        phase12i_profile,
    )
    return [
        {
            "phase_label": phase_label,
            "source_kind": source_kind,
            "source_reference_id": _safe_phase12k_source_reference_id(
                payload.get(reference_key),
                prefix,
            ),
            "reference_status": PHASE12K_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for payload, (phase_label, source_kind, reference_key, prefix) in zip(
            payloads,
            PHASE12K_SOURCE_REFERENCE_PHASES,
            strict=True,
        )
    ]


def _phase12k_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12K_BACKEND_OPTION_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12K_STATUS_LABELS
    ]


def _phase12k_backend_options() -> list[dict[str, object]]:
    return [
        {
            "backend_option_label": label,
            "backend_option_status": PHASE12K_BACKEND_OPTION_STATUS,
            "credential_policy": PHASE12K_CREDENTIAL_POLICY,
            "metadata_only": True,
            "human_approval_required": True,
            "cost_guard_required": True,
            "private_health_data_allowed": False,
            "api_call_execution_granted": False,
            "sdk_execution_granted": False,
            "simulator_execution_granted": False,
            "provider_execution_granted": False,
            "network_call_execution_granted": False,
            "spending_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12K_BACKEND_OPTION_LABELS
    ]


def _phase12k_workload_classes() -> list[dict[str, object]]:
    return [
        {
            "workload_class_label": label,
            "workload_class_status": PHASE12K_WORKLOAD_CLASS_STATUS,
            "metadata_only": True,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "medical_advice_provided": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12K_WORKLOAD_CLASSES
    ]


def _phase12k_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12K_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "human_approval_required": True,
            "cost_guard_required": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12K_REQUIRED_FUTURE_GATES
    ]


def _phase12l_fabric_interop_a2a_audit_profile_payload(
    source_references: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "fabric_interop_a2a_audit_profile_contract_version": (
            PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        "profile_id": None,
        "source_phase_range": PHASE12L_SOURCE_PHASE_RANGE,
        "source_phase_references": source_references,
        "source_phase_reference_count": len(PHASE12L_SOURCE_REFERENCE_PHASES),
        "capability_phase": PHASE12L_CAPABILITY_PHASE,
        "authorization_status": PHASE12L_AUTHORIZATION_STATUS,
        "grant_status": PHASE12L_GRANT_STATUS,
        "profile_status": PHASE12L_PROFILE_STATUS,
        "fabric_interop_status": PHASE12L_FABRIC_INTEROP_STATUS,
        "message_codec_status": PHASE12L_MESSAGE_CODEC_STATUS,
        "a2a_transport_status": PHASE12L_A2A_TRANSPORT_STATUS,
        "mcp_interop_status": PHASE12L_MCP_INTEROP_STATUS,
        "secure_drop_status": PHASE12L_SECURE_DROP_STATUS,
        "credential_policy": PHASE12L_CREDENTIAL_POLICY,
        "opaque_traffic_allowed": False,
        "untrusted_content_executable": False,
        "cross_repo_mutation_allowed": False,
        "status_labels": _phase12l_status_labels(),
        "status_label_count": len(PHASE12L_STATUS_LABELS),
        "fabric_capability_labels": _phase12l_fabric_capability_labels(),
        "fabric_capability_label_count": len(PHASE12L_FABRIC_CAPABILITY_LABELS),
        "forbidden_out_of_scope_labels": _phase12l_forbidden_out_of_scope_labels(),
        "forbidden_out_of_scope_label_count": len(PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS),
        "required_future_gates": _phase12l_required_future_gates(),
        "required_future_gate_count": len(PHASE12L_REQUIRED_FUTURE_GATES),
        "fabric_boundary_statement": PHASE12L_FABRIC_BOUNDARY_STATEMENT,
        "audit_boundary_statement": PHASE12L_AUDIT_BOUNDARY_STATEMENT,
        "secure_drop_boundary_statement": PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "fabric_safety_review_required": True,
        "jules_human_review_required_for_validator_or_fabric_safety_semantics": True,
        "plaintext_json_default_future_requirement_only": True,
        "decode_to_audit_future_requirement_only": True,
        "secure_drop_user_initiated_boundary_only": True,
        "phase12l_authorizes_runtime": False,
        "phase12l_allows_fabric_runtime": False,
        "phase12l_allows_a2a_transport": False,
        "phase12l_allows_mcp_runtime": False,
        "phase12l_allows_secure_drop_send_receive": False,
        **{field: False for field in _phase12l_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12l_source_phase_references(
    phase12a_charter: Mapping[str, object],
    phase12b_record: Mapping[str, object],
    phase12c_profile: Mapping[str, object],
    phase12d_profile: Mapping[str, object],
    phase12e_profile: Mapping[str, object],
    phase12f_boundary: Mapping[str, object],
    phase12g_matrix: Mapping[str, object],
    phase12h_matrix: Mapping[str, object],
    phase12i_profile: Mapping[str, object],
    phase12k_profile: Mapping[str, object],
) -> list[dict[str, object]]:
    payloads = (
        phase12a_charter,
        phase12b_record,
        phase12c_profile,
        phase12d_profile,
        phase12e_profile,
        phase12f_boundary,
        phase12g_matrix,
        phase12h_matrix,
        phase12i_profile,
        phase12k_profile,
    )
    return [
        {
            "phase_label": phase_label,
            "source_kind": source_kind,
            "source_reference_id": _safe_phase12l_source_reference_id(
                payload.get(reference_key),
                prefix,
            ),
            "reference_status": PHASE12L_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for payload, (phase_label, source_kind, reference_key, prefix) in zip(
            payloads,
            PHASE12L_SOURCE_REFERENCE_PHASES,
            strict=True,
        )
    ]


def _phase12l_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12L_FABRIC_CAPABILITY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12L_STATUS_LABELS
    ]


def _phase12l_fabric_capability_labels() -> list[dict[str, object]]:
    return [
        {
            "fabric_capability_label": label,
            "capability_status": PHASE12L_FABRIC_CAPABILITY_STATUS,
            "metadata_only": True,
            "future_requirement_only": True,
            "implementation_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12L_FABRIC_CAPABILITY_LABELS
    ]


def _phase12l_forbidden_out_of_scope_labels() -> list[dict[str, object]]:
    return [
        {
            "forbidden_label": label,
            "forbidden_status": PHASE12L_FORBIDDEN_LABEL_STATUS,
            "metadata_only": True,
            "out_of_scope": True,
            "allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS
    ]


def _phase12l_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12L_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12L_REQUIRED_FUTURE_GATES
    ]


def _phase12m_specialized_model_option_registry_profile_payload(
    source_references: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "specialized_model_option_registry_profile_contract_version": (
            PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        "profile_id": None,
        "source_phase_range": PHASE12M_SOURCE_PHASE_RANGE,
        "source_phase_references": source_references,
        "source_phase_reference_count": len(PHASE12M_SOURCE_REFERENCE_PHASES),
        "model_option_profile_phase": PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        "authorization_status": PHASE12M_AUTHORIZATION_STATUS,
        "grant_status": PHASE12M_GRANT_STATUS,
        "profile_status": PHASE12M_PROFILE_STATUS,
        "status_labels": _phase12m_status_labels(),
        "status_label_count": len(PHASE12M_STATUS_LABELS),
        "model_option_categories": _phase12m_model_option_categories(),
        "model_option_category_count": len(PHASE12M_MODEL_OPTION_CATEGORIES),
        "candidate_labels": _phase12m_candidate_labels(),
        "candidate_label_count": len(PHASE12M_CANDIDATE_LABELS),
        "required_future_gates": _phase12m_required_future_gates(),
        "required_future_gate_count": len(PHASE12M_REQUIRED_FUTURE_GATES),
        "model_boundary_statement": PHASE12M_MODEL_BOUNDARY_STATEMENT,
        "medical_boundary_statement": PHASE12M_MEDICAL_BOUNDARY_STATEMENT,
        "sensor_boundary_statement": PHASE12M_SENSOR_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "jules_human_review_required_for_validator_or_model_safety_semantics": True,
        "model_labels_selectable_metadata_only": True,
        "phase12m_authorizes_runtime": False,
        "phase12m_allows_model_execution": False,
        "phase12m_allows_provider_execution": False,
        "phase12m_allows_model_loading": False,
        "phase12m_allows_training": False,
        "phase12m_allows_fine_tuning": False,
        "phase12m_allows_clinical_decision_support": False,
        "phase12m_allows_diagnosis_or_treatment": False,
        "phase12m_allows_private_health_data_processing": False,
        "phase12m_allows_device_access": False,
        "phase12m_allows_raw_sensor_processing": False,
        "phase12m_provides_medical_advice": False,
        "phase12m_provides_prescribing": False,
        **{field: False for field in _phase12m_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12m_source_phase_references(
    phase12a_charter: Mapping[str, object],
    phase12b_record: Mapping[str, object],
    phase12c_profile: Mapping[str, object],
    phase12d_profile: Mapping[str, object],
    phase12e_profile: Mapping[str, object],
    phase12f_boundary: Mapping[str, object],
    phase12g_matrix: Mapping[str, object],
    phase12h_matrix: Mapping[str, object],
    phase12i_profile: Mapping[str, object],
    phase12k_profile: Mapping[str, object],
    phase12l_profile: Mapping[str, object],
) -> list[dict[str, object]]:
    payloads = (
        phase12a_charter,
        phase12b_record,
        phase12c_profile,
        phase12d_profile,
        phase12e_profile,
        phase12f_boundary,
        phase12g_matrix,
        phase12h_matrix,
        phase12i_profile,
        phase12k_profile,
        phase12l_profile,
    )
    return [
        {
            "phase_label": phase_label,
            "source_kind": source_kind,
            "source_reference_id": _safe_phase12m_source_reference_id(
                payload.get(reference_key),
                prefix,
            ),
            "reference_status": PHASE12M_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for payload, (phase_label, source_kind, reference_key, prefix) in zip(
            payloads,
            PHASE12M_SOURCE_REFERENCE_PHASES,
            strict=True,
        )
    ]


def _phase12m_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12M_STATUS_LABELS
    ]


def _phase12m_model_option_categories() -> list[dict[str, object]]:
    return [
        {
            "model_option_category_label": label,
            "category_status": PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
            "selectable_metadata_only": True,
            "metadata_only": True,
            "future_option_only": True,
            "model_loading_added": False,
            "model_execution_permitted": False,
            "provider_execution_permitted": False,
            "training_permitted": False,
            "fine_tuning_permitted": False,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "device_access_allowed": False,
            "raw_sensor_processing_allowed": False,
            "monitoring_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12M_MODEL_OPTION_CATEGORIES
    ]


def _phase12m_candidate_labels() -> list[dict[str, object]]:
    return [
        {
            "candidate_label": label,
            "candidate_status": PHASE12M_CANDIDATE_LABEL_STATUS,
            "selectable_metadata_only": True,
            "metadata_only": True,
            "future_option_only": True,
            "model_loading_added": False,
            "model_execution_permitted": False,
            "provider_execution_permitted": False,
            "training_permitted": False,
            "fine_tuning_permitted": False,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "prescribing_allowed": False,
            "medical_advice_allowed": False,
            "device_access_allowed": False,
            "raw_sensor_processing_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12M_CANDIDATE_LABELS
    ]


def _phase12m_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12M_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12M_REQUIRED_FUTURE_GATES
    ]


def _phase12n_workflow_orchestration_mode_registry_profile_payload(
    source_references: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "workflow_orchestration_mode_registry_profile_contract_version": (
            PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION
        ),
        "profile_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        "profile_id": None,
        "source_phase_range": PHASE12N_SOURCE_PHASE_RANGE,
        "source_phase_references": source_references,
        "source_phase_reference_count": len(PHASE12N_SOURCE_REFERENCE_PHASES),
        "workflow_mode_profile_phase": PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        "authorization_status": PHASE12N_AUTHORIZATION_STATUS,
        "grant_status": PHASE12N_GRANT_STATUS,
        "profile_status": PHASE12N_PROFILE_STATUS,
        "status_labels": _phase12n_status_labels(),
        "status_label_count": len(PHASE12N_STATUS_LABELS),
        "workflow_modes": _phase12n_workflow_modes(),
        "workflow_mode_count": len(PHASE12N_WORKFLOW_MODES),
        "fusion_concepts": _phase12n_fusion_concepts(),
        "fusion_concept_count": len(PHASE12N_FUSION_CONCEPT_LABELS),
        "scientist_evolution_concepts": _phase12n_scientist_evolution_concepts(),
        "scientist_evolution_concept_count": len(PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS),
        "required_future_gates": _phase12n_required_future_gates(),
        "required_future_gate_count": len(PHASE12N_REQUIRED_FUTURE_GATES),
        "workflow_boundary_statement": PHASE12N_WORKFLOW_BOUNDARY_STATEMENT,
        "fusion_boundary_statement": PHASE12N_FUSION_BOUNDARY_STATEMENT,
        "scientist_boundary_statement": PHASE12N_SCIENTIST_BOUNDARY_STATEMENT,
        "medical_sensor_boundary_statement": PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "jules_human_review_required_for_validator_or_workflow_safety_semantics": True,
        "workflow_modes_metadata_only": True,
        "phase12n_authorizes_runtime": False,
        "phase12n_allows_workflow_mode_execution": False,
        "phase12n_allows_runtime_orchestration": False,
        "phase12n_allows_model_routing": False,
        "phase12n_allows_provider_execution": False,
        "phase12n_allows_model_execution": False,
        "phase12n_allows_model_loading": False,
        "phase12n_allows_training": False,
        "phase12n_allows_fine_tuning": False,
        "phase12n_allows_code_execution": False,
        "phase12n_allows_experiment_execution": False,
        "phase12n_allows_autonomous_experimentation": False,
        "phase12n_allows_web_access": False,
        "phase12n_allows_autonomous_publication": False,
        "phase12n_allows_clinical_decision_support": False,
        "phase12n_allows_diagnosis_or_treatment": False,
        "phase12n_allows_private_health_data_processing": False,
        "phase12n_allows_device_or_sensor_access": False,
        "phase12n_provides_medical_advice": False,
        **{field: False for field in _phase12n_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12n_source_phase_references(
    phase12a_charter: Mapping[str, object],
    phase12b_record: Mapping[str, object],
    phase12c_profile: Mapping[str, object],
    phase12d_profile: Mapping[str, object],
    phase12e_profile: Mapping[str, object],
    phase12f_boundary: Mapping[str, object],
    phase12g_matrix: Mapping[str, object],
    phase12h_matrix: Mapping[str, object],
    phase12i_profile: Mapping[str, object],
    phase12k_profile: Mapping[str, object],
    phase12l_profile: Mapping[str, object],
    phase12m_profile: Mapping[str, object],
) -> list[dict[str, object]]:
    payloads = (
        phase12a_charter,
        phase12b_record,
        phase12c_profile,
        phase12d_profile,
        phase12e_profile,
        phase12f_boundary,
        phase12g_matrix,
        phase12h_matrix,
        phase12i_profile,
        phase12k_profile,
        phase12l_profile,
        phase12m_profile,
    )
    return [
        {
            "phase_label": phase_label,
            "source_kind": source_kind,
            "source_reference_id": _safe_phase12n_source_reference_id(
                payload.get(reference_key),
                prefix,
            ),
            "reference_status": PHASE12N_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for payload, (phase_label, source_kind, reference_key, prefix) in zip(
            payloads,
            PHASE12N_SOURCE_REFERENCE_PHASES,
            strict=True,
        )
    ]


def _phase12n_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12N_WORKFLOW_MODE_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12N_STATUS_LABELS
    ]


def _phase12n_workflow_modes() -> list[dict[str, object]]:
    return [
        {
            "workflow_mode_label": label,
            "mode_status": PHASE12N_WORKFLOW_MODE_STATUS,
            "mode_definition": definition,
            "metadata_only": True,
            "future_mode_only": True,
            "workflow_mode_execution_permitted": False,
            "runtime_orchestration_added": False,
            "model_routing_execution_permitted": False,
            "autonomous_experimentation_permitted": False,
            "code_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label, definition in PHASE12N_WORKFLOW_MODES
    ]


def _phase12n_fusion_concepts() -> list[dict[str, object]]:
    return [
        {
            "fusion_concept_label": label,
            "concept_status": PHASE12N_FUSION_CONCEPT_STATUS,
            "metadata_only": True,
            "future_concept_only": True,
            "model_routing_execution_permitted": False,
            "provider_call_execution_granted": False,
            "model_loading_added": False,
            "learned_coordination_execution_granted": False,
            "agent_routing_execution_granted": False,
            "network_call_execution_granted": False,
            "runtime_orchestration_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12N_FUSION_CONCEPT_LABELS
    ]


def _phase12n_scientist_evolution_concepts() -> list[dict[str, object]]:
    return [
        {
            "scientist_evolution_concept_label": label,
            "concept_status": PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS,
            "metadata_only": True,
            "future_concept_only": True,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "web_access_permitted": False,
            "literature_search_execution_permitted": False,
            "database_ingestion_added": False,
            "manuscript_generation_added": False,
            "autonomous_publication_allowed": False,
            "model_training_execution_granted": False,
            "model_fine_tuning_execution_granted": False,
            "autonomous_research_action_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS
    ]


def _phase12n_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12N_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12N_REQUIRED_FUTURE_GATES
    ]


def _phase12o_workflow_mode_safety_gate_matrix_payload(
    source_phase12n_profile: dict[str, object],
) -> dict[str, object]:
    return {
        "workflow_mode_safety_gate_matrix_contract_version": (
            PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION
        ),
        "matrix_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        "matrix_id": None,
        "source_phase": PHASE12O_SOURCE_PHASE,
        "source_phase12n_profile": source_phase12n_profile,
        "matrix_phase": PHASE12O_MATRIX_PHASE,
        "authorization_status": PHASE12O_AUTHORIZATION_STATUS,
        "grant_status": PHASE12O_GRANT_STATUS,
        "matrix_status": PHASE12O_MATRIX_STATUS,
        "status_labels": _phase12o_status_labels(),
        "status_label_count": len(PHASE12O_STATUS_LABELS),
        "workflow_mode_prerequisite_matrix": _phase12o_workflow_mode_prerequisite_matrix(),
        "workflow_mode_prerequisite_count": len(PHASE12O_WORKFLOW_MODES),
        "required_future_gates": _phase12o_required_future_gates(),
        "required_future_gate_count": len(PHASE12O_REQUIRED_FUTURE_GATES),
        "mode_gate_requirements": _phase12o_mode_gate_requirements(),
        "mode_gate_requirement_count": len(PHASE12O_WORKFLOW_MODES)
        * len(PHASE12O_REQUIRED_FUTURE_GATES),
        "matrix_boundary_statement": PHASE12O_MATRIX_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "standalone_first_statement": PHASE12O_STANDALONE_FIRST_STATEMENT,
        "metadata_only": True,
        "non_authorizing_proof": True,
        "standalone_first": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "jules_human_review_required_for_validator_or_workflow_safety_semantics": True,
        "workflow_mode_safety_gates_metadata_only": True,
        "phase12o_authorizes_runtime": False,
        "phase12o_satisfies_runtime_prerequisites": False,
        "phase12o_allows_workflow_execution": False,
        "phase12o_allows_workflow_mode_execution": False,
        "phase12o_allows_runtime_adapter": False,
        "phase12o_allows_model_routing": False,
        "phase12o_allows_provider_execution": False,
        "phase12o_allows_model_execution": False,
        "phase12o_allows_code_execution": False,
        "phase12o_allows_experiment_execution": False,
        "phase12o_allows_web_database_network_behavior": False,
        "phase12o_allows_clinical_decision_support": False,
        "phase12o_allows_private_health_data_processing": False,
        "phase12o_active_grant_present": False,
        **{field: False for field in _phase12o_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12o_source_phase12n_profile(
    source_profile: Mapping[str, object],
) -> dict[str, object]:
    return {
        "source_phase_label": PHASE12O_SOURCE_PHASE,
        "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        "source_reference_id": _safe_phase12n_profile_id(source_profile.get("profile_id")),
        "reference_status": PHASE12O_SOURCE_REFERENCE_STATUS,
        "metadata_only": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12o_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12O_STATUS_LABELS
    ]


def _phase12o_workflow_mode_prerequisite_matrix() -> list[dict[str, object]]:
    return [
        {
            "workflow_mode_label": mode,
            "matrix_entry_status": PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
            "source_phase12n_mode_label": mode,
            "metadata_only": True,
            "standalone_first": True,
            "runtime_prerequisite_only": True,
            "required_future_gate_labels": list(PHASE12O_REQUIRED_FUTURE_GATES),
            "required_future_gate_count": len(PHASE12O_REQUIRED_FUTURE_GATES),
            "all_prerequisites_satisfied": False,
            "runtime_blocked": True,
            "review_required": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for mode in PHASE12O_WORKFLOW_MODES
    ]


def _phase12o_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12O_FUTURE_GATE_STATUS,
            "gate_scope": PHASE12O_GATE_SCOPE,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "runtime_prerequisite_satisfied": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12O_REQUIRED_FUTURE_GATES
    ]


def _phase12o_mode_gate_requirements() -> list[dict[str, object]]:
    return [
        {
            "workflow_mode_label": mode,
            "future_gate_label": gate,
            "gate_status": PHASE12O_MODE_GATE_STATUS,
            "gate_scope": PHASE12O_GATE_SCOPE,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "runtime_prerequisite_satisfied": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for mode in PHASE12O_WORKFLOW_MODES
        for gate in PHASE12O_REQUIRED_FUTURE_GATES
    ]


def _phase12p_review_packet_payload(
    source_phase_references: list[dict[str, object]],
    prerequisite_matrix_reference: dict[str, object],
) -> dict[str, object]:
    return {
        "workflow_mode_activation_request_review_packet_contract_version": (
            PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION
        ),
        "packet_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        "activation_request_packet_id": None,
        "source_phase_range": PHASE12P_SOURCE_PHASE_RANGE,
        "source_phase_references": source_phase_references,
        "source_phase_reference_count": 2,
        "prerequisite_matrix_reference": prerequisite_matrix_reference,
        "packet_phase": PHASE12P_PACKET_PHASE,
        "authorization_status": PHASE12P_AUTHORIZATION_STATUS,
        "grant_status": PHASE12P_GRANT_STATUS,
        "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
        "packet_status": PHASE12P_PACKET_STATUS,
        "status_labels": _phase12p_status_labels(),
        "status_label_count": len(PHASE12P_STATUS_LABELS),
        "workflow_mode_review_packets": _phase12p_workflow_mode_review_packets(
            prerequisite_matrix_reference
        ),
        "workflow_mode_review_packet_count": len(PHASE12P_WORKFLOW_MODES),
        "required_future_gates": _phase12p_required_future_gates(),
        "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
        "required_reviewer_classes": _phase12p_required_reviewer_classes(),
        "required_reviewer_class_count": len(PHASE12P_REQUIRED_REVIEWER_CLASSES),
        "risk_summary_placeholders": _phase12p_risk_summary_placeholders(),
        "risk_summary_placeholder_count": len(PHASE12P_RISK_SUMMARY_PLACEHOLDERS),
        "evidence_inventory_placeholders": _phase12p_evidence_inventory_placeholders(),
        "evidence_inventory_placeholder_count": len(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS),
        "packet_boundary_statement": PHASE12P_PACKET_BOUNDARY_STATEMENT,
        "review_requirement_statement": PHASE12P_REVIEW_REQUIREMENT_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "review_packet_boundary_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "human_review_required": True,
        "jules_review_required": True,
        "security_review_required": True,
        "medical_safety_review_required": True,
        "human_jules_security_medical_safety_review_required": True,
        "all_future_gates_unsatisfied": True,
        "denial_blocked_default_fail_closed": True,
        "denial_blocked_default_fail_closed_status": PHASE12P_DENIAL_BLOCKED_STATUS,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "workflow_mode_activation_not_permitted": True,
        "workflow_mode_activation_not_permitted_status": (PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS),
        "phase12p_authorizes_runtime": False,
        "phase12p_creates_active_grant": False,
        "phase12p_grants_execution_permission": False,
        "phase12p_allows_workflow_execution": False,
        "phase12p_allows_workflow_mode_execution": False,
        "phase12p_allows_runtime_adapter": False,
        "phase12p_allows_model_routing": False,
        "phase12p_allows_provider_execution": False,
        "phase12p_allows_model_execution": False,
        "phase12p_allows_model_loading": False,
        "phase12p_allows_training": False,
        "phase12p_allows_fine_tuning": False,
        "phase12p_allows_code_execution": False,
        "phase12p_allows_experiment_execution": False,
        "phase12p_allows_autonomous_experimentation": False,
        "phase12p_allows_web_access": False,
        "phase12p_allows_database_ingestion": False,
        "phase12p_allows_web_scraping": False,
        "phase12p_allows_network_calls": False,
        "phase12p_allows_clinical_decision_support": False,
        "phase12p_allows_diagnosis_or_treatment": False,
        "phase12p_allows_medical_advice": False,
        "phase12p_allows_dosing_or_nutrition_prescription": False,
        "phase12p_allows_private_health_data_processing": False,
        "phase12p_allows_device_or_sensor_access": False,
        "phase12p_allows_raw_sensor_processing": False,
        "phase12p_marks_production_ready": False,
        **{field: False for field in _phase12p_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12p_source_phase_references(
    source_profile: Mapping[str, object],
    source_matrix: Mapping[str, object],
) -> list[dict[str, object]]:
    return [
        {
            "source_phase_label": "12N",
            "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
            "source_reference_id": _safe_phase12n_profile_id(source_profile.get("profile_id")),
            "reference_status": PHASE12P_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12O",
            "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
            "source_reference_id": _safe_phase12o_matrix_id(source_matrix.get("matrix_id")),
            "reference_status": PHASE12P_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
    ]


def _phase12p_prerequisite_matrix_reference(
    source_matrix: Mapping[str, object],
) -> dict[str, object]:
    return {
        "source_phase_label": "12O",
        "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        "source_reference_id": _safe_phase12o_matrix_id(source_matrix.get("matrix_id")),
        "reference_status": PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
        "required_future_gate_labels": list(PHASE12P_REQUIRED_FUTURE_GATES),
        "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
        "workflow_mode_prerequisite_count": len(PHASE12P_WORKFLOW_MODES),
        "runtime_prerequisites_satisfied": False,
        "metadata_only": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12p_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12P_MODE_PACKET_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12P_STATUS_LABELS
    ]


def _phase12p_workflow_mode_review_packets(
    prerequisite_matrix_reference: Mapping[str, object],
) -> list[dict[str, object]]:
    return [
        {
            "requested_workflow_mode_label": mode,
            "packet_entry_status": PHASE12P_MODE_PACKET_STATUS,
            "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
            "prerequisite_matrix_reference_id": _safe_phase12o_matrix_id(
                prerequisite_matrix_reference.get("source_reference_id")
            ),
            "required_future_gate_labels": list(PHASE12P_REQUIRED_FUTURE_GATES),
            "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
            "required_reviewer_class_labels": list(PHASE12P_REQUIRED_REVIEWER_CLASSES),
            "required_reviewer_class_count": len(PHASE12P_REQUIRED_REVIEWER_CLASSES),
            "risk_summary_placeholder_labels": list(PHASE12P_RISK_SUMMARY_PLACEHOLDERS),
            "evidence_inventory_placeholder_labels": list(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS),
            "denial_blocked_default_fail_closed_status": PHASE12P_DENIAL_BLOCKED_STATUS,
            "metadata_only": True,
            "review_packet_boundary_only": True,
            "standalone_first": True,
            "not_authorized": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "autonomous_experimentation_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for mode in PHASE12P_WORKFLOW_MODES
    ]


def _phase12p_required_future_gates() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12P_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "review_completed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12P_REQUIRED_FUTURE_GATES
    ]


def _phase12p_required_reviewer_classes() -> list[dict[str, object]]:
    return [
        {
            "reviewer_class_label": label,
            "reviewer_class_status": PHASE12P_REVIEWER_CLASS_STATUS,
            "required": True,
            "completed": False,
            "approved": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12P_REQUIRED_REVIEWER_CLASSES
    ]


def _phase12p_risk_summary_placeholders() -> list[dict[str, object]]:
    return [
        {
            "risk_summary_placeholder_label": label,
            "placeholder_status": PHASE12P_RISK_PLACEHOLDER_STATUS,
            "required": True,
            "filled": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12P_RISK_SUMMARY_PLACEHOLDERS
    ]


def _phase12p_evidence_inventory_placeholders() -> list[dict[str, object]]:
    return [
        {
            "evidence_inventory_placeholder_label": label,
            "placeholder_status": PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
            "required": True,
            "filled": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS
    ]


def _phase12q_decision_record_payload(
    source_phase_references: list[dict[str, object]],
    source_packet: Mapping[str, object],
) -> dict[str, object]:
    return {
        "workflow_mode_review_decision_record_contract_version": (
            PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION
        ),
        "decision_record_kind": PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        "decision_record_id": None,
        "source_phase_range": PHASE12Q_SOURCE_PHASE_RANGE,
        "source_phase_references": source_phase_references,
        "source_phase_reference_count": 3,
        "source_activation_request_packet_id": _safe_phase12p_packet_id(
            source_packet.get("activation_request_packet_id")
        ),
        "requested_workflow_mode_label": PHASE12Q_WORKFLOW_MODES[0],
        "decision_record_phase": PHASE12Q_DECISION_RECORD_PHASE,
        "authorization_status": PHASE12Q_AUTHORIZATION_STATUS,
        "grant_status": PHASE12Q_GRANT_STATUS,
        "decision_record_status": PHASE12Q_DECISION_RECORD_STATUS,
        "status_labels": _phase12q_status_labels(),
        "status_label_count": len(PHASE12Q_STATUS_LABELS),
        "decision_status": PHASE12Q_DEFAULT_DECISION_STATUS,
        "decision_reason_code": PHASE12Q_DEFAULT_DECISION_REASON_CODE,
        "decision_summary": PHASE12Q_DECISION_SUMMARY,
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS[
            PHASE12Q_DEFAULT_DECISION_STATUS
        ],
        "required_future_gates_snapshot": _phase12q_required_future_gates_snapshot(),
        "required_future_gate_count": len(PHASE12Q_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12Q_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12Q_REQUIRED_FUTURE_GATES)
        + len(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        "reviewer_classes_required": _phase12q_reviewer_classes_required(),
        "reviewer_class_required_count": len(PHASE12Q_REQUIRED_REVIEWER_CLASSES),
        "reviewer_classes_represented": _phase12q_reviewer_classes_represented(),
        "reviewer_class_represented_count": 0,
        "decision_boundary_statement": PHASE12Q_DECISION_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "review_decision_record_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "request_review_not_submitted": True,
        "request_review_blocked": False,
        "request_returned_for_fix_only_changes": False,
        "request_denied_no_runtime_authorization": False,
        "request_expired_no_runtime_authorization": False,
        "request_review_complete_no_runtime_authorization": False,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "workflow_mode_activation_not_permitted_status": PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        "phase12q_authorizes_runtime": False,
        "phase12q_creates_active_grant": False,
        "phase12q_grants_execution_permission": False,
        "phase12q_allows_workflow_activation": False,
        "phase12q_allows_workflow_execution": False,
        "phase12q_allows_workflow_mode_execution": False,
        "phase12q_allows_runtime_adapter": False,
        "phase12q_allows_model_routing": False,
        "phase12q_allows_provider_execution": False,
        "phase12q_allows_model_execution": False,
        "phase12q_allows_model_loading": False,
        "phase12q_allows_training": False,
        "phase12q_allows_fine_tuning": False,
        "phase12q_allows_code_execution": False,
        "phase12q_allows_experiment_execution": False,
        "phase12q_allows_autonomous_experimentation": False,
        "phase12q_allows_web_access": False,
        "phase12q_allows_database_ingestion": False,
        "phase12q_allows_web_scraping": False,
        "phase12q_allows_network_calls": False,
        "phase12q_allows_clinical_decision_support": False,
        "phase12q_allows_diagnosis_or_treatment": False,
        "phase12q_allows_medical_advice": False,
        "phase12q_allows_dosing_or_nutrition_prescription": False,
        "phase12q_allows_private_health_data_processing": False,
        "phase12q_allows_device_or_sensor_access": False,
        "phase12q_allows_raw_sensor_processing": False,
        "phase12q_marks_production_ready": False,
        **{field: False for field in _phase12q_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12q_source_phase_references(
    source_packet: Mapping[str, object],
) -> list[dict[str, object]]:
    packet_source_refs = source_packet.get("source_phase_references")
    refs_by_phase: dict[str, Mapping[str, object]] = {}
    if isinstance(packet_source_refs, list):
        refs_by_phase = {
            str(item.get("source_phase_label") or ""): item
            for item in packet_source_refs
            if isinstance(item, Mapping)
        }
    phase12n_ref = refs_by_phase.get("12N", {})
    phase12o_ref = refs_by_phase.get("12O", {})
    return [
        {
            "source_phase_label": "12N",
            "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
            "source_reference_id": _safe_phase12n_profile_id(
                phase12n_ref.get("source_reference_id")
            ),
            "reference_status": PHASE12Q_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12O",
            "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
            "source_reference_id": _safe_phase12o_matrix_id(
                phase12o_ref.get("source_reference_id")
            ),
            "reference_status": PHASE12Q_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12P",
            "source_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
            "source_reference_id": _safe_phase12p_packet_id(
                source_packet.get("activation_request_packet_id")
            ),
            "reference_status": PHASE12Q_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
    ]


def _phase12q_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12Q_DECISION_RECORD_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12Q_STATUS_LABELS
    ]


def _phase12q_required_future_gates_snapshot() -> list[dict[str, object]]:
    return [
        {
            "future_gate_label": label,
            "gate_status": PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "review_completed": False,
            "blocks_runtime_authorization": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12Q_REQUIRED_FUTURE_GATES
    ]


def _phase12q_reviewer_classes_required() -> list[dict[str, object]]:
    return [
        {
            "reviewer_class_label": label,
            "reviewer_class_status": PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
            "required": True,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12Q_REQUIRED_REVIEWER_CLASSES
    ]


def _phase12q_reviewer_classes_represented() -> list[dict[str, object]]:
    return [
        {
            "reviewer_class_label": label,
            "reviewer_class_status": PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
            "represented": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12Q_REQUIRED_REVIEWER_CLASSES
    ]


def _phase12r_audit_trail_index_payload(
    source_phase_references: list[dict[str, object]],
    source_record: Mapping[str, object],
) -> dict[str, object]:
    decision_status = (
        _safe_phase12q_decision_status(source_record.get("decision_status"))
        or PHASE12Q_DEFAULT_DECISION_STATUS
    )
    return {
        "workflow_mode_review_audit_trail_index_contract_version": (
            PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION
        ),
        "audit_trail_index_kind": PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        "audit_trail_index_id": None,
        "source_phase_range": PHASE12R_SOURCE_PHASE_RANGE,
        "source_phase_references": source_phase_references,
        "source_phase_reference_count": 4,
        "audit_trail_index_phase": PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        "authorization_status": PHASE12R_AUTHORIZATION_STATUS,
        "grant_status": PHASE12R_GRANT_STATUS,
        "audit_trail_index_status": PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        "status_labels": _phase12r_status_labels(),
        "status_label_count": len(PHASE12R_STATUS_LABELS),
        "indexed_workflow_modes": _phase12r_indexed_workflow_modes(),
        "indexed_workflow_mode_count": len(PHASE12R_WORKFLOW_MODES),
        "activation_request_packet_reference_metadata": (
            _phase12r_activation_packet_reference(source_record)
        ),
        "review_decision_record_reference_metadata": (
            _phase12r_review_decision_record_reference(source_record)
        ),
        "decision_status_summary": _phase12r_decision_status_summary(decision_status),
        "decision_status": decision_status,
        "decision_reason_code": PHASE12Q_DECISION_STATUS_REASON_CODES[decision_status],
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS[decision_status],
        "required_future_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12R_REQUIRED_FUTURE_GATES)
        + len(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        "stale_count": 0,
        "review_needed_count": 1,
        "stale_status": PHASE12R_STALE_STATUS,
        "review_needed_status": PHASE12R_REVIEW_NEEDED_STATUS,
        "stale_review_needed_status": PHASE12R_STALE_REVIEW_NEEDED_STATUS,
        "reviewer_classes_required": _phase12r_reviewer_classes_required(),
        "reviewer_class_required_count": len(PHASE12R_REQUIRED_REVIEWER_CLASSES),
        "reviewer_classes_represented": _phase12r_reviewer_classes_represented(),
        "reviewer_class_represented_count": 0,
        "audit_trail_boundary_statement": PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "workflow_mode_review_audit_trail_index_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12r_authorizes_runtime": False,
        "phase12r_creates_active_grant": False,
        "phase12r_grants_execution_permission": False,
        "phase12r_allows_workflow_activation": False,
        "phase12r_allows_workflow_execution": False,
        "phase12r_allows_workflow_mode_execution": False,
        "phase12r_allows_runtime_adapter": False,
        "phase12r_allows_model_routing": False,
        "phase12r_allows_provider_execution": False,
        "phase12r_allows_model_execution": False,
        "phase12r_allows_model_loading": False,
        "phase12r_allows_training": False,
        "phase12r_allows_fine_tuning": False,
        "phase12r_allows_code_execution": False,
        "phase12r_allows_experiment_execution": False,
        "phase12r_allows_autonomous_experimentation": False,
        "phase12r_allows_shell_execution": False,
        "phase12r_allows_process_execution": False,
        "phase12r_allows_cache_event_bus_pubsub_runtime": False,
        "phase12r_allows_web_access": False,
        "phase12r_allows_database_ingestion": False,
        "phase12r_allows_database_writes": False,
        "phase12r_allows_query_execution": False,
        "phase12r_allows_web_scraping": False,
        "phase12r_allows_network_calls": False,
        "phase12r_allows_clinical_decision_support": False,
        "phase12r_allows_diagnosis_or_treatment": False,
        "phase12r_allows_medical_advice": False,
        "phase12r_allows_dosing_or_nutrition_prescription": False,
        "phase12r_allows_private_health_data_processing": False,
        "phase12r_allows_device_or_sensor_access": False,
        "phase12r_allows_raw_sensor_processing": False,
        "phase12r_marks_production_ready": False,
        **{field: False for field in _phase12r_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12r_source_phase_references(
    source_record: Mapping[str, object],
) -> list[dict[str, object]]:
    record_source_refs = source_record.get("source_phase_references")
    refs_by_phase: dict[str, Mapping[str, object]] = {}
    if isinstance(record_source_refs, list):
        refs_by_phase = {
            str(item.get("source_phase_label") or ""): item
            for item in record_source_refs
            if isinstance(item, Mapping)
        }
    phase12n_ref = refs_by_phase.get("12N", {})
    phase12o_ref = refs_by_phase.get("12O", {})
    phase12p_ref = refs_by_phase.get("12P", {})
    return [
        {
            "source_phase_label": "12N",
            "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
            "source_reference_id": _safe_phase12n_profile_id(
                phase12n_ref.get("source_reference_id")
            ),
            "reference_status": PHASE12R_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12O",
            "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
            "source_reference_id": _safe_phase12o_matrix_id(
                phase12o_ref.get("source_reference_id")
            ),
            "reference_status": PHASE12R_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12P",
            "source_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
            "source_reference_id": _safe_phase12p_packet_id(
                phase12p_ref.get("source_reference_id")
            ),
            "reference_status": PHASE12R_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12Q",
            "source_kind": PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
            "source_reference_id": _safe_phase12q_decision_record_id(
                source_record.get("decision_record_id")
            ),
            "reference_status": PHASE12R_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
    ]


def _phase12r_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12R_STATUS_LABELS
    ]


def _phase12r_indexed_workflow_modes() -> list[dict[str, object]]:
    return [
        {
            "workflow_mode_label": label,
            "mode_index_status": PHASE12R_MODE_INDEX_STATUS,
            "metadata_only": True,
            "indexed_for_audit_only": True,
            "required_future_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
            "unsatisfied_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12R_WORKFLOW_MODES
    ]


def _phase12r_activation_packet_reference(
    source_record: Mapping[str, object],
) -> dict[str, object]:
    return {
        "source_phase_label": "12P",
        "source_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        "activation_request_packet_id": _safe_phase12p_packet_id(
            source_record.get("source_activation_request_packet_id")
        ),
        "reference_status": PHASE12R_PACKET_REFERENCE_STATUS,
        "requested_workflow_mode_label": (
            _safe_phase12q_workflow_mode_label(source_record.get("requested_workflow_mode_label"))
            or PHASE12R_WORKFLOW_MODES[0]
        ),
        "metadata_only": True,
        "workflow_mode_activation_not_permitted": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12r_review_decision_record_reference(
    source_record: Mapping[str, object],
) -> dict[str, object]:
    decision_status = (
        _safe_phase12q_decision_status(source_record.get("decision_status"))
        or PHASE12Q_DEFAULT_DECISION_STATUS
    )
    return {
        "source_phase_label": "12Q",
        "source_kind": PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        "decision_record_id": _safe_phase12q_decision_record_id(
            source_record.get("decision_record_id")
        ),
        "reference_status": PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
        "decision_status": decision_status,
        "decision_reason_code": PHASE12Q_DECISION_STATUS_REASON_CODES[decision_status],
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS[decision_status],
        "metadata_only": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "no_active_grant": True,
        "no_execution_permission": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12r_decision_status_summary(decision_status: str) -> dict[str, object]:
    status = _safe_phase12q_decision_status(decision_status) or PHASE12Q_DEFAULT_DECISION_STATUS
    return {
        "decision_status": status,
        "decision_reason_code": PHASE12Q_DECISION_STATUS_REASON_CODES[status],
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS[status],
        "decision_status_summary_status": PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
        **_phase12q_decision_status_flags(status),
        "metadata_only": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "no_execution_permission": True,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12r_reviewer_classes_required() -> list[dict[str, object]]:
    return [
        {
            "reviewer_class_label": label,
            "reviewer_class_status": PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
            "required": True,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12R_REQUIRED_REVIEWER_CLASSES
    ]


def _phase12r_reviewer_classes_represented() -> list[dict[str, object]]:
    return [
        {
            "reviewer_class_label": label,
            "reviewer_class_status": PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
            "represented": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12R_REQUIRED_REVIEWER_CLASSES
    ]


def _phase12s_closeout_summary_payload(
    source_phase_references: list[dict[str, object]],
    source_index: Mapping[str, object],
) -> dict[str, object]:
    return {
        "workflow_mode_review_chain_closeout_summary_contract_version": (
            PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION
        ),
        "closeout_summary_kind": PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
        "closeout_summary_id": None,
        "source_phase_range": PHASE12S_SOURCE_PHASE_RANGE,
        "source_phase_references": source_phase_references,
        "source_phase_reference_count": 5,
        "closeout_summary_phase": PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        "authorization_status": PHASE12S_AUTHORIZATION_STATUS,
        "grant_status": PHASE12S_GRANT_STATUS,
        "summary_status": PHASE12S_SUMMARY_STATUS,
        "status_labels": _phase12s_status_labels(),
        "status_label_count": len(PHASE12S_STATUS_LABELS),
        "workflow_mode_labels_covered": _phase12s_workflow_mode_labels_covered(),
        "workflow_mode_label_count": len(PHASE12S_WORKFLOW_MODES),
        "future_gate_count": len(PHASE12S_REQUIRED_FUTURE_GATES),
        "unsatisfied_gate_count": len(PHASE12S_REQUIRED_FUTURE_GATES),
        "blocker_count": len(PHASE12S_REQUIRED_FUTURE_GATES)
        + len(PHASE12S_REQUIRED_REVIEWER_CLASSES),
        "review_chain_status": PHASE12S_REVIEW_CHAIN_STATUS,
        "closeout_status": PHASE12S_DEFAULT_CLOSEOUT_STATUS,
        "reviewer_navigation_summary": PHASE12S_REVIEWER_NAVIGATION_SUMMARY,
        "operator_handoff_summary": PHASE12S_OPERATOR_HANDOFF_SUMMARY,
        "closeout_boundary_statement": PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT,
        "medical_privacy_boundary_statement": PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT,
        "metadata_only": True,
        "workflow_mode_review_chain_closeout_summary_only": True,
        "standalone_first": True,
        "non_authorizing_proof": True,
        "not_authorized": True,
        "no_active_grant": True,
        "no_runtime_authorization": True,
        "no_execution_permission": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "phase12s_authorizes_runtime": False,
        "phase12s_creates_active_grant": False,
        "phase12s_grants_execution_permission": False,
        "phase12s_allows_workflow_activation": False,
        "phase12s_allows_workflow_execution": False,
        "phase12s_allows_workflow_mode_execution": False,
        "phase12s_allows_runtime_adapter": False,
        "phase12s_allows_model_routing": False,
        "phase12s_allows_provider_execution": False,
        "phase12s_allows_model_execution": False,
        "phase12s_allows_model_loading": False,
        "phase12s_allows_training": False,
        "phase12s_allows_fine_tuning": False,
        "phase12s_allows_code_execution": False,
        "phase12s_allows_shell_execution": False,
        "phase12s_allows_process_execution": False,
        "phase12s_allows_experiment_execution": False,
        "phase12s_allows_autonomous_experimentation": False,
        "phase12s_allows_web_access": False,
        "phase12s_allows_network_behavior": False,
        "phase12s_allows_database_ingestion": False,
        "phase12s_allows_database_writes": False,
        "phase12s_allows_query_execution": False,
        "phase12s_allows_cache_event_bus_pubsub_runtime": False,
        "phase12s_allows_transport_implementation": False,
        "phase12s_allows_fabric_implementation": False,
        "phase12s_allows_p2p_implementation": False,
        "phase12s_allows_clinical_decision_support": False,
        "phase12s_allows_diagnosis_or_treatment": False,
        "phase12s_allows_medical_advice": False,
        "phase12s_allows_dosing_or_nutrition_prescription": False,
        "phase12s_allows_private_health_data_processing": False,
        "phase12s_allows_device_or_sensor_access": False,
        "phase12s_allows_raw_sensor_processing": False,
        "phase12s_marks_deployment_ready": False,
        "phase12s_marks_production_ready": False,
        **{field: False for field in _phase12s_runtime_false_fields()},
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }


def _phase12s_source_phase_references(
    source_index: Mapping[str, object],
) -> list[dict[str, object]]:
    index_refs = source_index.get("source_phase_references")
    refs_by_phase: dict[str, Mapping[str, object]] = {}
    if isinstance(index_refs, list):
        refs_by_phase = {
            str(item.get("source_phase_label") or ""): item
            for item in index_refs
            if isinstance(item, Mapping)
        }
    return [
        {
            "source_phase_label": "12N",
            "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
            "source_reference_id": _safe_phase12n_profile_id(
                refs_by_phase.get("12N", {}).get("source_reference_id")
            ),
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12O",
            "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
            "source_reference_id": _safe_phase12o_matrix_id(
                refs_by_phase.get("12O", {}).get("source_reference_id")
            ),
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12P",
            "source_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
            "source_reference_id": _safe_phase12p_packet_id(
                refs_by_phase.get("12P", {}).get("source_reference_id")
            ),
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12Q",
            "source_kind": PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
            "source_reference_id": _safe_phase12q_decision_record_id(
                refs_by_phase.get("12Q", {}).get("source_reference_id")
            ),
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
        {
            "source_phase_label": "12R",
            "source_kind": PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
            "source_reference_id": _safe_phase12r_audit_trail_index_id(
                source_index.get("audit_trail_index_id")
            ),
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        },
    ]


def _phase12s_status_labels() -> list[dict[str, object]]:
    return [
        {
            "status_label": label,
            "label_status": PHASE12S_SUMMARY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12S_STATUS_LABELS
    ]


def _phase12s_workflow_mode_labels_covered() -> list[dict[str, object]]:
    return [
        {
            "workflow_mode_label": label,
            "mode_coverage_status": PHASE12S_MODE_COVERAGE_STATUS,
            "metadata_only": True,
            "covered_for_closeout_only": True,
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "code_execution_permitted": False,
            "shell_execution_permitted": False,
            "process_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for label in PHASE12S_WORKFLOW_MODES
    ]


def _source_governance_closeout_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12a_charter_source_governance_not_object",)
    errors: list[str] = []
    if PHASE12A_SOURCE_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS - set(value):
        errors.append("phase12a_charter_source_governance_field_missing")
    if set(str(key) for key in value) - PHASE12A_SOURCE_GOVERNANCE_CLOSEOUT_REQUIRED_FIELDS:
        errors.append("phase12a_charter_source_governance_unknown_field")
    expected = {
        "artifact_kind": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND,
        "contract_version": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_CONTRACT_VERSION,
        "phase_range": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_PHASE_RANGE,
        "final_status": PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        "runtime_authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12a_charter_source_governance_value_invalid")
            break
    for field in (
        "missing_future_gate_count",
        "unresolved_review_count",
        "blocker_count",
        "stale_count",
    ):
        if not _is_non_negative_int(value.get(field)):
            errors.append("phase12a_charter_source_governance_count_invalid")
            break
    return tuple(errors)


def _source_runtime_gap_ledger_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12a_charter_source_ledger_not_object",)
    errors: list[str] = []
    if PHASE12A_SOURCE_RUNTIME_GAP_LEDGER_REQUIRED_FIELDS - set(value):
        errors.append("phase12a_charter_source_ledger_field_missing")
    if set(str(key) for key in value) - PHASE12A_SOURCE_RUNTIME_GAP_LEDGER_REQUIRED_FIELDS:
        errors.append("phase12a_charter_source_ledger_unknown_field")
    expected = {
        "artifact_kind": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND,
        "contract_version": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_CONTRACT_VERSION,
        "source_phase_range": PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_PHASE_RANGE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "readiness_gap": PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12a_charter_source_ledger_value_invalid")
            break
    if not _is_non_negative_int(value.get("missing_future_gate_count")):
        errors.append("phase12a_charter_source_ledger_count_invalid")
    return tuple(errors)


def _future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12a_charter_future_gates_invalid",)
    errors: list[str] = []
    gate_ids: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12a_charter_future_gate_not_object")
            continue
        if PHASE12A_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12a_charter_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12A_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12a_charter_future_gate_unknown_field")
        gate_id = _safe_gate_id(item.get("gate_id"))
        gate_ids.append(gate_id)
        if gate_id != item.get("gate_id"):
            errors.append("phase12a_charter_future_gate_id_invalid")
        if item.get("gate_status") != PHASE12A_FUTURE_GATE_STATUS:
            errors.append("phase12a_charter_future_gate_status_invalid")
        if item.get("required_before_runtime_authorization") is not True:
            errors.append("phase12a_charter_future_gate_required_invalid")
        for field in (
            "satisfied_by_phase12a",
            "passed",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12a_charter_future_gate_passed_implied")
                break
        if item.get("metadata_only") is not True:
            errors.append("phase12a_charter_future_gate_metadata_only_invalid")
    if gate_ids != list(PHASE12A_FUTURE_REQUIRED_GATES) or len(gate_ids) != len(set(gate_ids)):
        errors.append("phase12a_charter_future_gate_order_invalid")
    return tuple(errors)


def _source_design_charter_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12b_record_source_charter_not_object",)
    errors: list[str] = []
    if PHASE12B_SOURCE_CHARTER_REQUIRED_FIELDS - set(value):
        errors.append("phase12b_record_source_charter_field_missing")
    if set(str(key) for key in value) - PHASE12B_SOURCE_CHARTER_REQUIRED_FIELDS:
        errors.append("phase12b_record_source_charter_unknown_field")
    expected = {
        "artifact_kind": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        "contract_version": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION,
        "source_phase_range": PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE,
        "authorization_phase": PHASE12A_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12A_AUTHORIZATION_STATUS,
        "charter_status": PHASE12A_CHARTER_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12b_record_source_charter_value_invalid")
            break
    if _safe_phase12a_charter_id(value.get("charter_id")) != value.get("charter_id"):
        errors.append("phase12b_record_source_charter_id_invalid")
    for field in (
        "future_required_gate_count",
        "satisfied_future_gate_count",
        "passed_future_gate_count",
    ):
        if not _is_non_negative_int(value.get(field)):
            errors.append("phase12b_record_source_charter_count_invalid")
            break
    if value.get("future_required_gate_count") != len(PHASE12A_FUTURE_REQUIRED_GATES):
        errors.append("phase12b_record_source_charter_gate_count_invalid")
    if value.get("satisfied_future_gate_count") != 0:
        errors.append("phase12b_record_source_charter_satisfied_count_invalid")
    if value.get("passed_future_gate_count") != 0:
        errors.append("phase12b_record_source_charter_passed_count_invalid")
    return tuple(errors)


def _requested_domain_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12b_record_requested_domains_invalid",)
    errors: list[str] = []
    domains: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12b_record_requested_domain_not_object")
            continue
        if PHASE12B_REQUESTED_DOMAIN_REQUIRED_FIELDS - set(item):
            errors.append("phase12b_record_requested_domain_field_missing")
        if set(str(key) for key in item) - PHASE12B_REQUESTED_DOMAIN_REQUIRED_FIELDS:
            errors.append("phase12b_record_requested_domain_unknown_field")
        domain = _safe_domain_label(item.get("domain_label"))
        domains.append(domain)
        if domain != item.get("domain_label"):
            errors.append("phase12b_record_requested_domain_label_invalid")
        if item.get("request_status") != PHASE12B_REQUEST_STATUS:
            errors.append("phase12b_record_requested_domain_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12b_record_requested_domain_metadata_only_invalid")
        for field in ("execution_permitted", "real_mode_runtime_enabled"):
            if item.get(field) is not False:
                errors.append("phase12b_record_requested_domain_runtime_implied")
                break
    if domains != list(PHASE12B_REQUESTED_DOMAINS) or len(domains) != len(set(domains)):
        errors.append("phase12b_record_requested_domain_order_invalid")
    return tuple(errors)


def _required_reviewer_role_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12b_record_reviewer_roles_invalid",)
    errors: list[str] = []
    reviewer_roles: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12b_record_reviewer_role_not_object")
            continue
        if PHASE12B_REVIEWER_ROLE_REQUIRED_FIELDS - set(item):
            errors.append("phase12b_record_reviewer_role_field_missing")
        if set(str(key) for key in item) - PHASE12B_REVIEWER_ROLE_REQUIRED_FIELDS:
            errors.append("phase12b_record_reviewer_role_unknown_field")
        reviewer_role = _safe_reviewer_role(item.get("reviewer_role"))
        reviewer_roles.append(reviewer_role)
        if reviewer_role != item.get("reviewer_role"):
            errors.append("phase12b_record_reviewer_role_invalid")
        if item.get("review_status") != PHASE12B_REVIEWER_ROLE_STATUS:
            errors.append("phase12b_record_reviewer_role_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12b_record_reviewer_role_metadata_only_invalid")
        for field in (
            "satisfied_by_phase12b",
            "passed",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12b_record_reviewer_role_passed_implied")
                break
    if reviewer_roles != list(PHASE12B_REQUIRED_REVIEWER_ROLES) or len(reviewer_roles) != len(
        set(reviewer_roles)
    ):
        errors.append("phase12b_record_reviewer_role_order_invalid")
    return tuple(errors)


def _phase12b_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12b_record_future_gates_invalid",)
    errors: list[str] = []
    gates: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12b_record_future_gate_not_object")
            continue
        if PHASE12B_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12b_record_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12B_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12b_record_future_gate_unknown_field")
        gate_id = _safe_gate_id(item.get("gate_id"))
        reviewer_role = _safe_reviewer_role(item.get("reviewer_role"))
        gates.append((gate_id, reviewer_role))
        if gate_id != item.get("gate_id"):
            errors.append("phase12b_record_future_gate_id_invalid")
        if reviewer_role != item.get("reviewer_role"):
            errors.append("phase12b_record_future_gate_reviewer_role_invalid")
        if item.get("gate_status") != PHASE12B_FUTURE_GATE_STATUS:
            errors.append("phase12b_record_future_gate_status_invalid")
        if item.get("required_before_runtime_authorization") is not True:
            errors.append("phase12b_record_future_gate_required_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12b_record_future_gate_metadata_only_invalid")
        for field in (
            "submitted_by_phase12b",
            "satisfied_by_phase12b",
            "passed",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12b_record_future_gate_passed_implied")
                break
    if gates != list(PHASE12B_REQUIRED_FUTURE_GATES) or len(gates) != len(set(gates)):
        errors.append("phase12b_record_future_gate_order_invalid")
    return tuple(errors)


def _source_record_candidate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12c_profile_source_record_not_object",)
    errors: list[str] = []
    if PHASE12C_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS - set(value):
        errors.append("phase12c_profile_source_record_field_missing")
    if set(str(key) for key in value) - PHASE12C_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS:
        errors.append("phase12c_profile_source_record_unknown_field")
    expected = {
        "record_kind": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
        "contract_version": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION,
        "source_phase": PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE,
        "authorization_phase": PHASE12B_AUTHORIZATION_PHASE,
        "authorization_status": PHASE12B_AUTHORIZATION_STATUS,
        "decision_status": PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
        "grant_status": PHASE12B_GRANT_STATUS,
        "record_candidate_status": PHASE12B_RECORD_CANDIDATE_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12c_profile_source_record_value_invalid")
            break
    if _safe_phase12b_record_id(value.get("record_id")) != value.get("record_id"):
        errors.append("phase12c_profile_source_record_id_invalid")
    for field in (
        "requested_domain_count",
        "required_future_reviewer_role_count",
        "required_future_gate_count",
    ):
        if not _is_non_negative_int(value.get(field)):
            errors.append("phase12c_profile_source_record_count_invalid")
            break
    if value.get("requested_domain_count") != len(PHASE12B_REQUESTED_DOMAINS):
        errors.append("phase12c_profile_source_record_domain_count_invalid")
    if value.get("required_future_reviewer_role_count") != len(PHASE12B_REQUIRED_REVIEWER_ROLES):
        errors.append("phase12c_profile_source_record_reviewer_count_invalid")
    if value.get("required_future_gate_count") != len(PHASE12B_REQUIRED_FUTURE_GATES):
        errors.append("phase12c_profile_source_record_gate_count_invalid")
    return tuple(errors)


def _capability_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12c_profile_capability_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12c_profile_capability_label_not_object")
            continue
        if PHASE12C_CAPABILITY_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12c_profile_capability_label_field_missing")
        if set(str(key) for key in item) - PHASE12C_CAPABILITY_LABEL_REQUIRED_FIELDS:
            errors.append("phase12c_profile_capability_label_unknown_field")
        label = _safe_capability_label(item.get("capability_label"))
        labels.append(label)
        if label != item.get("capability_label"):
            errors.append("phase12c_profile_capability_label_invalid")
        if item.get("capability_status") != PHASE12C_CAPABILITY_STATUS:
            errors.append("phase12c_profile_capability_label_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12c_profile_capability_label_metadata_only_invalid")
        for field in ("execution_permitted", "real_mode_runtime_enabled"):
            if item.get(field) is not False:
                errors.append("phase12c_profile_capability_label_runtime_implied")
                break
    if labels != list(PHASE12C_ALLOWED_CAPABILITY_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12c_profile_capability_label_order_invalid")
    return tuple(errors)


def _phase12d_source_design_charter_errors(value: object) -> tuple[str, ...]:
    errors = list(_source_design_charter_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12D_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS - set(value):
        errors.append("phase12d_profile_source_charter_field_missing")
    if set(str(key) for key in value) - PHASE12D_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS:
        errors.append("phase12d_profile_source_charter_unknown_field")
    return tuple(errors)


def _phase12d_source_record_candidate_errors(value: object) -> tuple[str, ...]:
    errors = list(_source_record_candidate_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12D_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS - set(value):
        errors.append("phase12d_profile_source_record_field_missing")
    if set(str(key) for key in value) - PHASE12D_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS:
        errors.append("phase12d_profile_source_record_unknown_field")
    return tuple(errors)


def _phase12d_source_capability_profile_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12d_profile_source_capability_profile_not_object",)
    errors: list[str] = []
    if PHASE12D_SOURCE_CAPABILITY_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12d_profile_source_capability_profile_field_missing")
    if set(str(key) for key in value) - PHASE12D_SOURCE_CAPABILITY_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12d_profile_source_capability_profile_unknown_field")
    expected = {
        "profile_kind": PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
        "contract_version": PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION,
        "source_phase": PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE,
        "supervision_phase": PHASE12C_SUPERVISION_PHASE,
        "authorization_status": PHASE12C_AUTHORIZATION_STATUS,
        "grant_status": PHASE12C_GRANT_STATUS,
        "profile_status": PHASE12C_PROFILE_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12d_profile_source_capability_profile_value_invalid")
            break
    if _safe_phase12c_profile_id(value.get("profile_id")) != value.get("profile_id"):
        errors.append("phase12d_profile_source_capability_profile_id_invalid")
    if not _is_non_negative_int(value.get("capability_label_count")):
        errors.append("phase12d_profile_source_capability_profile_count_invalid")
    elif value.get("capability_label_count") != len(PHASE12C_ALLOWED_CAPABILITY_LABELS):
        errors.append("phase12d_profile_source_capability_profile_count_invalid")
    return tuple(errors)


def _phase12d_capability_category_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12d_profile_capability_categories_invalid",)
    errors: list[str] = []
    categories: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12d_profile_capability_category_not_object")
            continue
        if PHASE12D_CAPABILITY_CATEGORY_REQUIRED_FIELDS - set(item):
            errors.append("phase12d_profile_capability_category_field_missing")
        if set(str(key) for key in item) - PHASE12D_CAPABILITY_CATEGORY_REQUIRED_FIELDS:
            errors.append("phase12d_profile_capability_category_unknown_field")
        category = _safe_phase12d_capability_category(item.get("capability_category"))
        categories.append(category)
        if category != item.get("capability_category"):
            errors.append("phase12d_profile_capability_category_invalid")
        if item.get("category_status") != PHASE12D_CAPABILITY_CATEGORY_STATUS:
            errors.append("phase12d_profile_capability_category_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12d_profile_capability_category_metadata_only_invalid")
        for field in (
            "consent_granted_by_phase12d",
            "authorization_granted_by_phase12d",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12d_profile_capability_category_runtime_implied")
                break
    if categories != list(PHASE12D_CAPABILITY_CATEGORIES) or len(categories) != len(
        set(categories)
    ):
        errors.append("phase12d_profile_capability_category_order_invalid")
    return tuple(errors)


def _phase12d_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12d_profile_future_gates_invalid",)
    errors: list[str] = []
    gate_ids: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12d_profile_future_gate_not_object")
            continue
        if PHASE12D_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12d_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12D_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12d_profile_future_gate_unknown_field")
        gate_id = _safe_phase12d_future_gate(item.get("gate_id"))
        gate_ids.append(gate_id)
        if gate_id != item.get("gate_id"):
            errors.append("phase12d_profile_future_gate_id_invalid")
        if item.get("gate_status") != PHASE12D_FUTURE_GATE_STATUS:
            errors.append("phase12d_profile_future_gate_status_invalid")
        if item.get("required_before_visual_desktop_runtime") is not True:
            errors.append("phase12d_profile_future_gate_required_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12d_profile_future_gate_metadata_only_invalid")
        for field in (
            "satisfied_by_phase12d",
            "passed",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12d_profile_future_gate_passed_implied")
                break
    if gate_ids != list(PHASE12D_REQUIRED_FUTURE_GATES) or len(gate_ids) != len(set(gate_ids)):
        errors.append("phase12d_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12e_source_design_charter_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12d_source_design_charter_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12E_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS - set(value):
        errors.append("phase12e_profile_source_charter_field_missing")
    if set(str(key) for key in value) - PHASE12E_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS:
        errors.append("phase12e_profile_source_charter_unknown_field")
    return tuple(errors)


def _phase12e_source_record_candidate_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12d_source_record_candidate_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12E_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS - set(value):
        errors.append("phase12e_profile_source_record_field_missing")
    if set(str(key) for key in value) - PHASE12E_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS:
        errors.append("phase12e_profile_source_record_unknown_field")
    return tuple(errors)


def _phase12e_source_consent_gate_profile_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12e_profile_source_consent_gate_profile_not_object",)
    errors: list[str] = []
    if PHASE12E_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12e_profile_source_consent_gate_profile_field_missing")
    if set(str(key) for key in value) - PHASE12E_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12e_profile_source_consent_gate_profile_unknown_field")
    expected = {
        "profile_kind": PHASE12D_CONSENT_GATE_PROFILE_KIND,
        "contract_version": PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION,
        "source_phase_range": PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE,
        "consent_phase": PHASE12D_CONSENT_PHASE,
        "authorization_status": PHASE12D_AUTHORIZATION_STATUS,
        "grant_status": PHASE12D_GRANT_STATUS,
        "consent_gate_status": PHASE12D_CONSENT_GATE_STATUS,
        "satisfied_consent_gate_count": 0,
        "passed_consent_gate_count": 0,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12e_profile_source_consent_gate_profile_value_invalid")
            break
    if _safe_phase12d_profile_id(value.get("consent_gate_profile_id")) != value.get(
        "consent_gate_profile_id"
    ):
        errors.append("phase12e_profile_source_consent_gate_profile_id_invalid")
    if not _is_non_negative_int(value.get("capability_category_count")):
        errors.append("phase12e_profile_source_consent_gate_profile_count_invalid")
    elif value.get("capability_category_count") != len(PHASE12D_CAPABILITY_CATEGORIES):
        errors.append("phase12e_profile_source_consent_gate_profile_count_invalid")
    if not _is_non_negative_int(value.get("required_future_gate_count")):
        errors.append("phase12e_profile_source_consent_gate_profile_count_invalid")
    elif value.get("required_future_gate_count") != len(PHASE12D_REQUIRED_FUTURE_GATES):
        errors.append("phase12e_profile_source_consent_gate_profile_count_invalid")
    return tuple(errors)


def _phase12e_source_sensor_evidence_boundary_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12e_profile_source_sensor_evidence_boundary_not_object",)
    errors: list[str] = []
    if PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARY_REQUIRED_FIELDS - set(value):
        errors.append("phase12e_profile_source_sensor_evidence_boundary_field_missing")
    if set(str(key) for key in value) - PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARY_REQUIRED_FIELDS:
        errors.append("phase12e_profile_source_sensor_evidence_boundary_unknown_field")
    expected = {
        "boundary_kind": "existing-sensor-evidence-boundaries",
        "source_phase_range": "7A-11M",
        "boundary_status": PHASE12E_SENSOR_EVIDENCE_BOUNDARY_STATUS,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12e_profile_source_sensor_evidence_boundary_value_invalid")
            break
    labels = value.get("boundary_labels")
    if not isinstance(labels, list):
        errors.append("phase12e_profile_source_sensor_evidence_boundary_labels_invalid")
    elif labels != list(PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES):
        errors.append("phase12e_profile_source_sensor_evidence_boundary_labels_invalid")
    if not _is_non_negative_int(value.get("boundary_label_count")):
        errors.append("phase12e_profile_source_sensor_evidence_boundary_count_invalid")
    elif value.get("boundary_label_count") != len(PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES):
        errors.append("phase12e_profile_source_sensor_evidence_boundary_count_invalid")
    return tuple(errors)


def _phase12e_sensor_capability_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12e_profile_sensor_capability_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12e_profile_sensor_capability_label_not_object")
            continue
        if PHASE12E_SENSOR_CAPABILITY_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12e_profile_sensor_capability_label_field_missing")
        if set(str(key) for key in item) - PHASE12E_SENSOR_CAPABILITY_LABEL_REQUIRED_FIELDS:
            errors.append("phase12e_profile_sensor_capability_label_unknown_field")
        label = _safe_phase12e_sensor_capability_label(item.get("sensor_capability_label"))
        labels.append(label)
        if label != item.get("sensor_capability_label"):
            errors.append("phase12e_profile_sensor_capability_label_invalid")
        if item.get("capability_status") != PHASE12E_CAPABILITY_STATUS:
            errors.append("phase12e_profile_sensor_capability_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12e_profile_sensor_capability_metadata_only_invalid")
        for field in (
            "sensor_enabled_by_phase12e",
            "measurement_permitted",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12e_profile_sensor_capability_runtime_implied")
                break
    if labels != list(PHASE12E_SENSOR_CAPABILITY_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12e_profile_sensor_capability_order_invalid")
    return tuple(errors)


def _phase12e_non_diagnostic_boundary_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12e_profile_non_diagnostic_boundaries_invalid",)
    errors: list[str] = []
    boundary_ids: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12e_profile_non_diagnostic_boundary_not_object")
            continue
        if PHASE12E_NON_DIAGNOSTIC_BOUNDARY_REQUIRED_FIELDS - set(item):
            errors.append("phase12e_profile_non_diagnostic_boundary_field_missing")
        if set(str(key) for key in item) - PHASE12E_NON_DIAGNOSTIC_BOUNDARY_REQUIRED_FIELDS:
            errors.append("phase12e_profile_non_diagnostic_boundary_unknown_field")
        boundary_id = _safe_phase12e_non_diagnostic_boundary(item.get("boundary_id"))
        boundary_ids.append(boundary_id)
        if boundary_id != item.get("boundary_id"):
            errors.append("phase12e_profile_non_diagnostic_boundary_id_invalid")
        if item.get("boundary_status") != PHASE12E_NON_DIAGNOSTIC_BOUNDARY_STATUS:
            errors.append("phase12e_profile_non_diagnostic_boundary_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12e_profile_non_diagnostic_boundary_metadata_only_invalid")
        for field in (
            "satisfied_by_phase12e",
            "diagnosis_permitted",
            "clinical_recommendation_permitted",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12e_profile_non_diagnostic_boundary_runtime_implied")
                break
    if boundary_ids != list(PHASE12E_NON_DIAGNOSTIC_BOUNDARIES) or len(boundary_ids) != len(
        set(boundary_ids)
    ):
        errors.append("phase12e_profile_non_diagnostic_boundary_order_invalid")
    return tuple(errors)


def _phase12e_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12e_profile_future_gates_invalid",)
    errors: list[str] = []
    gate_ids: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12e_profile_future_gate_not_object")
            continue
        if PHASE12E_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12e_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12E_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12e_profile_future_gate_unknown_field")
        gate_id = _safe_phase12e_future_gate(item.get("gate_id"))
        gate_ids.append(gate_id)
        if gate_id != item.get("gate_id"):
            errors.append("phase12e_profile_future_gate_id_invalid")
        if item.get("gate_status") != PHASE12E_FUTURE_GATE_STATUS:
            errors.append("phase12e_profile_future_gate_status_invalid")
        if item.get("required_before_physiological_sensor_runtime") is not True:
            errors.append("phase12e_profile_future_gate_required_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12e_profile_future_gate_metadata_only_invalid")
        for field in (
            "satisfied_by_phase12e",
            "passed",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12e_profile_future_gate_passed_implied")
                break
    if gate_ids != list(PHASE12E_REQUIRED_FUTURE_GATES) or len(gate_ids) != len(set(gate_ids)):
        errors.append("phase12e_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12f_source_design_charter_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12e_source_design_charter_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12F_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_charter_field_missing")
    if set(str(key) for key in value) - PHASE12F_SOURCE_DESIGN_CHARTER_REQUIRED_FIELDS:
        errors.append("phase12f_boundary_source_charter_unknown_field")
    return tuple(errors)


def _phase12f_source_record_candidate_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12e_source_record_candidate_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12F_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_record_field_missing")
    if set(str(key) for key in value) - PHASE12F_SOURCE_RECORD_CANDIDATE_REQUIRED_FIELDS:
        errors.append("phase12f_boundary_source_record_unknown_field")
    return tuple(errors)


def _phase12f_source_visual_supervision_profile_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12d_source_capability_profile_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12F_SOURCE_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_visual_profile_field_missing")
    if set(str(key) for key in value) - PHASE12F_SOURCE_VISUAL_SUPERVISION_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12f_boundary_source_visual_profile_unknown_field")
    return tuple(errors)


def _phase12f_source_consent_gate_profile_errors(value: object) -> tuple[str, ...]:
    errors = list(_phase12e_source_consent_gate_profile_errors(value))
    if not isinstance(value, Mapping):
        return tuple(errors)
    if PHASE12F_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_consent_gate_profile_field_missing")
    if set(str(key) for key in value) - PHASE12F_SOURCE_CONSENT_GATE_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12f_boundary_source_consent_gate_profile_unknown_field")
    return tuple(errors)


def _phase12f_source_physiological_sensor_profile_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12f_boundary_source_physiological_sensor_profile_not_object",)
    errors: list[str] = []
    if PHASE12F_SOURCE_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_physiological_sensor_profile_field_missing")
    if (
        set(str(key) for key in value)
        - PHASE12F_SOURCE_PHYSIOLOGICAL_SENSOR_PROFILE_REQUIRED_FIELDS
    ):
        errors.append("phase12f_boundary_source_physiological_sensor_profile_unknown_field")
    expected = {
        "profile_kind": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        "contract_version": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION,
        "source_phase_range": PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE,
        "sensor_phase": PHASE12E_SENSOR_PHASE,
        "authorization_status": PHASE12E_AUTHORIZATION_STATUS,
        "grant_status": PHASE12E_GRANT_STATUS,
        "profile_status": PHASE12E_PROFILE_STATUS,
        "satisfied_sensor_gate_count": 0,
        "passed_sensor_gate_count": 0,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12f_boundary_source_physiological_sensor_profile_value_invalid")
            break
    if _safe_phase12e_profile_id(value.get("physiological_sensor_profile_id")) != value.get(
        "physiological_sensor_profile_id"
    ):
        errors.append("phase12f_boundary_source_physiological_sensor_profile_id_invalid")
    expected_counts = {
        "sensor_capability_label_count": len(PHASE12E_SENSOR_CAPABILITY_LABELS),
        "non_diagnostic_boundary_count": len(PHASE12E_NON_DIAGNOSTIC_BOUNDARIES),
        "required_future_gate_count": len(PHASE12E_REQUIRED_FUTURE_GATES),
    }
    for field, expected_count in expected_counts.items():
        if not _is_non_negative_int(value.get(field)) or value.get(field) != expected_count:
            errors.append("phase12f_boundary_source_physiological_sensor_profile_count_invalid")
            break
    return tuple(errors)


def _phase12f_source_content_fabric_secure_drop_contract_errors(
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12f_boundary_source_content_fabric_contract_not_object",)
    errors: list[str] = []
    if PHASE12F_SOURCE_CONTENT_FABRIC_SECURE_DROP_CONTRACT_REQUIRED_FIELDS - set(value):
        errors.append("phase12f_boundary_source_content_fabric_contract_field_missing")
    if (
        set(str(key) for key in value)
        - PHASE12F_SOURCE_CONTENT_FABRIC_SECURE_DROP_CONTRACT_REQUIRED_FIELDS
    ):
        errors.append("phase12f_boundary_source_content_fabric_contract_unknown_field")
    expected = {
        "source_kind": "content-fabric-secure-drop-design-contract",
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "canonical_reference": PHASE12F_CANONICAL_REFERENCE,
        "repository": "Ardynai/kortex-audio",
        "merge_commit_sha": PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
        "secure_drop_contract_version": 1,
        "contract_status": PHASE12F_CANONICAL_CONTRACT_STATUS,
        "design_contract_only": True,
        "somatic_owns_secure_drop_implementation": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12f_boundary_source_content_fabric_contract_value_invalid")
            break
    return tuple(errors)


def _phase12f_allowed_artifact_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12f_boundary_allowed_artifact_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12f_boundary_allowed_artifact_label_not_object")
            continue
        if PHASE12F_ALLOWED_ARTIFACT_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12f_boundary_allowed_artifact_label_field_missing")
        if set(str(key) for key in item) - PHASE12F_ALLOWED_ARTIFACT_LABEL_REQUIRED_FIELDS:
            errors.append("phase12f_boundary_allowed_artifact_label_unknown_field")
        label = _safe_phase12f_allowed_artifact_label(item.get("artifact_label"))
        labels.append(label)
        if label != item.get("artifact_label"):
            errors.append("phase12f_boundary_allowed_artifact_label_invalid")
        if item.get("artifact_status") != PHASE12F_ARTIFACT_STATUS:
            errors.append("phase12f_boundary_allowed_artifact_label_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12f_boundary_allowed_artifact_label_metadata_only_invalid")
        if item.get("explicit_user_action_required") is not True:
            errors.append("phase12f_boundary_allowed_artifact_label_user_action_invalid")
        for field in (
            "selected_by_phase12f",
            "send_permitted",
            "receive_permitted",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12f_boundary_allowed_artifact_label_runtime_implied")
                break
    if labels != list(PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS) or len(labels) != len(
        set(labels)
    ):
        errors.append("phase12f_boundary_allowed_artifact_label_order_invalid")
    return tuple(errors)


def _phase12f_prohibited_autonomous_source_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12f_boundary_prohibited_sources_invalid",)
    errors: list[str] = []
    sources: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12f_boundary_prohibited_source_not_object")
            continue
        if PHASE12F_PROHIBITED_SOURCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12f_boundary_prohibited_source_field_missing")
        if set(str(key) for key in item) - PHASE12F_PROHIBITED_SOURCE_REQUIRED_FIELDS:
            errors.append("phase12f_boundary_prohibited_source_unknown_field")
        source = _safe_phase12f_prohibited_source(item.get("source_label"))
        sources.append(source)
        if source != item.get("source_label"):
            errors.append("phase12f_boundary_prohibited_source_invalid")
        if item.get("source_status") != PHASE12F_PROHIBITED_SOURCE_STATUS:
            errors.append("phase12f_boundary_prohibited_source_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12f_boundary_prohibited_source_metadata_only_invalid")
        for field in (
            "permitted_by_phase12f",
            "send_permitted",
            "receive_permitted",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12f_boundary_prohibited_source_runtime_implied")
                break
    if sources != list(PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES) or len(sources) != len(set(sources)):
        errors.append("phase12f_boundary_prohibited_source_order_invalid")
    return tuple(errors)


def _phase12g_source_secure_drop_boundary_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12g_matrix_source_secure_drop_boundary_not_object",)
    errors: list[str] = []
    if PHASE12G_SOURCE_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS - set(value):
        errors.append("phase12g_matrix_source_secure_drop_boundary_field_missing")
    if (
        set(str(key) for key in value)
        - PHASE12G_SOURCE_SECURE_DROP_CONSUMER_BOUNDARY_REQUIRED_FIELDS
    ):
        errors.append("phase12g_matrix_source_secure_drop_boundary_unknown_field")
    expected = {
        "boundary_kind": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        "contract_version": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION,
        "source_phase_range": PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE,
        "consumer_phase": PHASE12F_CONSUMER_PHASE,
        "canonical_owner": PHASE12F_CANONICAL_OWNER,
        "authorization_status": PHASE12F_AUTHORIZATION_STATUS,
        "grant_status": PHASE12F_GRANT_STATUS,
        "boundary_status": PHASE12F_BOUNDARY_STATUS,
        "secure_drop_send_permitted": False,
        "secure_drop_receive_permitted": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12g_matrix_source_secure_drop_boundary_value_invalid")
            break
    if _safe_phase12f_boundary_id(value.get("secure_drop_consumer_boundary_id")) != value.get(
        "secure_drop_consumer_boundary_id"
    ):
        errors.append("phase12g_matrix_source_secure_drop_boundary_id_invalid")
    return tuple(errors)


def _phase12g_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12g_matrix_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12g_matrix_status_label_not_object")
            continue
        if PHASE12G_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12g_matrix_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12G_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12g_matrix_status_label_unknown_field")
        label = _safe_phase12g_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12g_matrix_status_label_invalid")
        if item.get("coverage_status") != PHASE12G_COVERAGE_STATUS:
            errors.append("phase12g_matrix_status_label_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12g_matrix_status_label_metadata_only_invalid")
        for field in ("execution_permitted", "real_mode_runtime_enabled"):
            if item.get(field) is not False:
                errors.append("phase12g_matrix_status_label_runtime_implied")
                break
    if labels != list(PHASE12G_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12g_matrix_status_label_order_invalid")
    return tuple(errors)


def _phase12g_area_entry_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12g_matrix_areas_invalid",)
    errors: list[str] = []
    area_ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12g_matrix_area_not_object")
            continue
        if PHASE12G_AREA_ENTRY_REQUIRED_FIELDS - set(item):
            errors.append("phase12g_matrix_area_field_missing")
        if set(str(key) for key in item) - PHASE12G_AREA_ENTRY_REQUIRED_FIELDS:
            errors.append("phase12g_matrix_area_unknown_field")
        expected_area = (
            PHASE12G_PRODUCTION_READINESS_AREAS[index]
            if index < len(PHASE12G_PRODUCTION_READINESS_AREAS)
            else None
        )
        area_id = _safe_phase12g_area_id(item.get("area_id"))
        area_ids.append(area_id)
        if area_id != item.get("area_id") or expected_area is None:
            errors.append("phase12g_matrix_area_id_invalid")
            continue
        expected = {
            "area_id": expected_area[0],
            "area_label": expected_area[1],
            "somatic_responsibility": expected_area[2],
            "likely_repo_family_owner": expected_area[3],
            "coverage_status": PHASE12G_COVERAGE_STATUS,
            "current_coverage_summary": expected_area[4],
            "remaining_gap_summary": expected_area[5],
            "blocked_runtime_requirement": expected_area[6],
            "review_requirement": expected_area[7],
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12g_matrix_area_value_invalid")
                break
        if item.get("metadata_only") is not True:
            errors.append("phase12g_matrix_area_metadata_only_invalid")
        for field in (
            "phase12g_area_grants_runtime",
            "external_owner_entry_grants_runtime",
            "execution_permitted",
            "real_mode_runtime_enabled",
        ):
            if item.get(field) is not False:
                errors.append("phase12g_matrix_area_runtime_implied")
                break
    expected_ids = [area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS]
    if area_ids != expected_ids or len(area_ids) != len(set(area_ids)):
        errors.append("phase12g_matrix_area_order_invalid")
    return tuple(errors)


def _phase12h_source_production_readiness_matrix_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12h_ownership_map_source_matrix_not_object",)
    errors: list[str] = []
    if PHASE12H_SOURCE_MATRIX_REQUIRED_FIELDS - set(value):
        errors.append("phase12h_ownership_map_source_matrix_field_missing")
    if set(str(key) for key in value) - PHASE12H_SOURCE_MATRIX_REQUIRED_FIELDS:
        errors.append("phase12h_ownership_map_source_matrix_unknown_field")
    expected = {
        "matrix_kind": PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        "contract_version": PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION,
        "source_phase_range": PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE,
        "readiness_phase": PHASE12G_READINESS_PHASE,
        "authorization_status": PHASE12G_AUTHORIZATION_STATUS,
        "grant_status": PHASE12G_GRANT_STATUS,
        "matrix_status": PHASE12G_MATRIX_STATUS,
        "production_readiness_area_count": len(PHASE12G_PRODUCTION_READINESS_AREAS),
        "phase12g_makes_somatic_production_ready": False,
        "phase12g_authorizes_runtime": False,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12h_ownership_map_source_matrix_value_invalid")
            break
    if _safe_phase12g_matrix_id(value.get("production_readiness_matrix_id")) != value.get(
        "production_readiness_matrix_id"
    ):
        errors.append("phase12h_ownership_map_source_matrix_id_invalid")
    return tuple(errors)


def _phase12h_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12h_ownership_map_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12h_ownership_map_status_label_not_object")
            continue
        if PHASE12H_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12h_ownership_map_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12H_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12h_ownership_map_status_label_unknown_field")
        label = _safe_phase12h_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12h_ownership_map_status_label_invalid")
        if item.get("entry_status") != PHASE12H_ENTRY_STATUS:
            errors.append("phase12h_ownership_map_status_label_status_invalid")
        if item.get("metadata_only") is not True:
            errors.append("phase12h_ownership_map_status_label_metadata_only_invalid")
        for field in ("execution_permitted", "real_mode_runtime_enabled"):
            if item.get(field) is not False:
                errors.append("phase12h_ownership_map_status_label_runtime_implied")
                break
    if labels != list(PHASE12H_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12h_ownership_map_status_label_order_invalid")
    return tuple(errors)


def _phase12h_standalone_ownership_entry_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12h_ownership_map_entries_invalid",)
    errors: list[str] = []
    area_ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12h_ownership_map_entry_not_object")
            continue
        if PHASE12H_STANDALONE_OWNERSHIP_ENTRY_REQUIRED_FIELDS - set(item):
            errors.append("phase12h_ownership_map_entry_field_missing")
        if set(str(key) for key in item) - PHASE12H_STANDALONE_OWNERSHIP_ENTRY_REQUIRED_FIELDS:
            errors.append("phase12h_ownership_map_entry_unknown_field")
        expected_area = (
            PHASE12H_SOMATIC_STANDALONE_AREAS[index]
            if index < len(PHASE12H_SOMATIC_STANDALONE_AREAS)
            else None
        )
        area_id = _safe_phase12h_area_id(item.get("production_area_id"))
        area_ids.append(area_id)
        if area_id != item.get("production_area_id") or expected_area is None:
            errors.append("phase12h_ownership_map_entry_area_id_invalid")
            continue
        (
            _,
            responsibility,
            current_coverage,
            remaining_gap,
            peers,
            review_requirement,
        ) = expected_area
        expected = {
            "entry_status": PHASE12H_ENTRY_STATUS,
            "somatic_standalone_responsibility": responsibility,
            "current_somatic_coverage": current_coverage,
            "remaining_somatic_gap": remaining_gap,
            "optional_integration_peer_count": len(peers),
            "external_integration_optional": True,
            "external_integration_replaces_somatic_standalone_path": False,
            "runtime_blocked": True,
            "review_requirement": review_requirement,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12h_ownership_map_entry_value_invalid")
                break
        if not _is_non_negative_int(item.get("optional_integration_peer_count")):
            errors.append("phase12h_ownership_map_entry_peer_count_invalid")
        errors.extend(
            _phase12h_optional_integration_peer_errors(
                item.get("optional_integration_peers"),
                expected_peers=peers,
            )
        )
    expected_area_ids = [area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS]
    if area_ids != expected_area_ids or len(area_ids) != len(set(area_ids)):
        errors.append("phase12h_ownership_map_entry_order_invalid")
    return tuple(errors)


def _phase12h_optional_integration_peer_errors(
    value: object,
    *,
    expected_peers: tuple[tuple[str, str, str], ...],
) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12h_ownership_map_optional_peers_invalid",)
    errors: list[str] = []
    peer_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12h_ownership_map_optional_peer_not_object")
            continue
        if PHASE12H_OPTIONAL_INTEGRATION_PEER_REQUIRED_FIELDS - set(item):
            errors.append("phase12h_ownership_map_optional_peer_field_missing")
        if set(str(key) for key in item) - PHASE12H_OPTIONAL_INTEGRATION_PEER_REQUIRED_FIELDS:
            errors.append("phase12h_ownership_map_optional_peer_unknown_field")
        expected_peer = expected_peers[index] if index < len(expected_peers) else None
        peer_label = _safe_phase12h_peer_label(item.get("peer_label"))
        peer_labels.append(peer_label)
        if peer_label != item.get("peer_label") or expected_peer is None:
            errors.append("phase12h_ownership_map_optional_peer_label_invalid")
            continue
        expected_label, expected_role, expected_summary = expected_peer
        expected = {
            "peer_label": expected_label,
            "integration_role": expected_role,
            "peer_status": PHASE12H_OPTIONAL_PEER_STATUS,
            "integration_summary": expected_summary,
            "optional_integration_metadata_only": True,
            "required_dependency_for_somatic": False,
            "replaces_somatic_standalone_path": False,
            "runtime_grant_created": False,
            "cross_repo_mutation_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12h_ownership_map_optional_peer_value_invalid")
                break
    expected_labels = [peer[0] for peer in expected_peers]
    if peer_labels != expected_labels or len(peer_labels) != len(set(peer_labels)):
        errors.append("phase12h_ownership_map_optional_peer_order_invalid")
    return tuple(errors)


def _phase12h_standalone_contradiction_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12h_standalone_contradiction_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12h_standalone_contradiction_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    blocked_fragments = (
        "external-owner",
        "external owner",
        "required dependency",
        "required owner",
        "must use locus",
        "depends on locus",
        "depends on aegis",
        "depends on multiverse",
        "depends on content-fabric",
        "somatic lacks standalone",
        "somatic has no standalone",
        "replaces somatic standalone",
        "other repo owns somatic",
        "handoff owner",
        "assigned owner repo",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12i_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_source_references_invalid",)
    errors: list[str] = []
    phase_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_source_reference_not_object")
            continue
        if PHASE12I_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12I_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12i_profile_source_reference_unknown_field")
        expected = (
            PHASE12I_SOURCE_REFERENCE_PHASES[index]
            if index < len(PHASE12I_SOURCE_REFERENCE_PHASES)
            else None
        )
        phase_label = str(item.get("phase_label") or "")
        phase_labels.append(phase_label)
        if expected is None:
            errors.append("phase12i_profile_source_reference_phase_invalid")
            continue
        expected_phase, expected_kind, _, expected_prefix = expected
        expected_values = {
            "phase_label": expected_phase,
            "source_kind": expected_kind,
            "reference_status": PHASE12I_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_source_reference_value_invalid")
                break
        if _safe_phase12i_source_reference_id(
            item.get("source_reference_id"),
            expected_prefix,
        ) != item.get("source_reference_id"):
            errors.append("phase12i_profile_source_reference_id_invalid")
    expected_phases = [phase[0] for phase in PHASE12I_SOURCE_REFERENCE_PHASES]
    if phase_labels != expected_phases or len(phase_labels) != len(set(phase_labels)):
        errors.append("phase12i_profile_source_reference_order_invalid")
    return tuple(errors)


def _phase12i_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_status_label_not_object")
            continue
        if PHASE12I_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12I_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12i_profile_status_label_unknown_field")
        label = _safe_phase12i_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12i_profile_status_label_invalid")
        expected = {
            "label_status": PHASE12I_LABEL_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_status_label_value_invalid")
                break
    if labels != list(PHASE12I_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12i_profile_status_label_order_invalid")
    return tuple(errors)


def _phase12i_user_preference_mode_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_preference_modes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_preference_mode_not_object")
            continue
        if PHASE12I_USER_PREFERENCE_MODE_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_preference_mode_field_missing")
        if set(str(key) for key in item) - PHASE12I_USER_PREFERENCE_MODE_REQUIRED_FIELDS:
            errors.append("phase12i_profile_preference_mode_unknown_field")
        label = _safe_phase12i_user_preference_mode(item.get("preference_mode_label"))
        labels.append(label)
        if label != item.get("preference_mode_label"):
            errors.append("phase12i_profile_preference_mode_label_invalid")
        expected = {
            "label_status": PHASE12I_LABEL_STATUS,
            "metadata_only": True,
            "safety_warnings_preserved": True,
            "emergency_escalation_preserved": True,
            "preference_cannot_suppress_warnings": True,
            "medical_advice_provided": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_preference_mode_value_invalid")
                break
    if labels != list(PHASE12I_USER_PREFERENCE_MODES) or len(labels) != len(set(labels)):
        errors.append("phase12i_profile_preference_mode_order_invalid")
    return tuple(errors)


def _phase12i_specialist_profile_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_specialists_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_specialist_not_object")
            continue
        if PHASE12I_SPECIALIST_PROFILE_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_specialist_field_missing")
        if set(str(key) for key in item) - PHASE12I_SPECIALIST_PROFILE_REQUIRED_FIELDS:
            errors.append("phase12i_profile_specialist_unknown_field")
        label = _safe_phase12i_specialist_profile_label(item.get("specialist_profile_label"))
        labels.append(label)
        if label != item.get("specialist_profile_label"):
            errors.append("phase12i_profile_specialist_label_invalid")
        expected = {
            "profile_status": PHASE12I_SPECIALIST_PROFILE_STATUS,
            "metadata_only": True,
            "review_profile_only": True,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "clinical_recommendation_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_specialist_value_invalid")
                break
    expected_labels = list(PHASE12I_SPECIALIST_PROFILE_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12i_profile_specialist_order_invalid")
    return tuple(errors)


def _phase12i_source_class_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_source_classes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_source_class_not_object")
            continue
        if PHASE12I_SOURCE_CLASS_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_source_class_field_missing")
        if set(str(key) for key in item) - PHASE12I_SOURCE_CLASS_REQUIRED_FIELDS:
            errors.append("phase12i_profile_source_class_unknown_field")
        label = _safe_phase12i_source_class_label(item.get("source_class_label"))
        labels.append(label)
        if label != item.get("source_class_label"):
            errors.append("phase12i_profile_source_class_label_invalid")
        expected = {
            "source_class_status": PHASE12I_SOURCE_CLASS_STATUS,
            "metadata_only": True,
            "provenance_review_required": True,
            "ingestion_permitted": False,
            "web_scraping_permitted": False,
            "database_ingestion_permitted": False,
            "network_call_execution_granted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_source_class_value_invalid")
                break
    expected_labels = list(PHASE12I_SOURCE_CLASS_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12i_profile_source_class_order_invalid")
    return tuple(errors)


def _phase12i_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12i_profile_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12i_profile_future_gate_not_object")
            continue
        if PHASE12I_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12i_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12I_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12i_profile_future_gate_unknown_field")
        label = _safe_phase12i_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12i_profile_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12I_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12i_profile_future_gate_value_invalid")
                break
    expected_labels = list(PHASE12I_REQUIRED_FUTURE_GATES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12i_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12i_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12i_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12i_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12I_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12I_WESTERN_MEDICINE_STATEMENT.lower(),
        PHASE12I_NATURAL_REMEDY_STATEMENT.lower(),
        PHASE12I_FOOD_CURE_STATEMENT.lower(),
        PHASE12I_SAFETY_WARNING_STATEMENT.lower(),
        *PHASE12I_USER_PREFERENCE_MODES,
        *PHASE12I_SPECIALIST_PROFILE_LABELS,
        *PHASE12I_SOURCE_CLASS_LABELS,
        *PHASE12I_REQUIRED_FUTURE_GATES,
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "provide medical advice",
        "medical advice provided",
        "clinical decision support",
        "clinical recommendation",
        "diagnosis",
        "diagnose",
        "treatment plan",
        "treat disease",
        "prescribe",
        "prescribing",
        "herb dosing",
        "herbal dosing",
        "supplement dosing",
        "supplement recommendation",
        "calorie prescription",
        "macro prescription",
        "weight-loss target",
        "unsafe fasting",
        "database ingestion",
        "web scraping",
        "network call",
        "provider execution",
        "model execution",
        "runtime adapter",
        "real-mode authorization",
        "western medicine is invalid",
        "natural remedies are safe",
        "food cures disease",
        "suppress emergency",
        "suppress contraindication",
        "suppress medication",
        "suppress pregnancy",
        "suppress liver",
        "suppress kidney",
        "suppress cardiac",
        "suppress eating-disorder",
        "suppress toxicity",
        "suppress contamination",
        "suppress adulteration",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12k_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12k_profile_source_references_invalid",)
    errors: list[str] = []
    phase_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12k_profile_source_reference_not_object")
            continue
        if PHASE12K_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12k_profile_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12K_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12k_profile_source_reference_unknown_field")
        expected = (
            PHASE12K_SOURCE_REFERENCE_PHASES[index]
            if index < len(PHASE12K_SOURCE_REFERENCE_PHASES)
            else None
        )
        phase_label = str(item.get("phase_label") or "")
        phase_labels.append(phase_label)
        if expected is None:
            errors.append("phase12k_profile_source_reference_phase_invalid")
            continue
        expected_phase, expected_kind, _, expected_prefix = expected
        expected_values = {
            "phase_label": expected_phase,
            "source_kind": expected_kind,
            "reference_status": PHASE12K_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12k_profile_source_reference_value_invalid")
                break
        if _safe_phase12k_source_reference_id(
            item.get("source_reference_id"),
            expected_prefix,
        ) != item.get("source_reference_id"):
            errors.append("phase12k_profile_source_reference_id_invalid")
    expected_phases = [phase[0] for phase in PHASE12K_SOURCE_REFERENCE_PHASES]
    if phase_labels != expected_phases or len(phase_labels) != len(set(phase_labels)):
        errors.append("phase12k_profile_source_reference_order_invalid")
    return tuple(errors)


def _phase12k_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12k_profile_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12k_profile_status_label_not_object")
            continue
        if PHASE12K_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12k_profile_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12K_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12k_profile_status_label_unknown_field")
        label = _safe_phase12k_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12k_profile_status_label_invalid")
        expected = {
            "label_status": PHASE12K_BACKEND_OPTION_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12k_profile_status_label_value_invalid")
                break
    if labels != list(PHASE12K_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12k_profile_status_label_order_invalid")
    return tuple(errors)


def _phase12k_backend_option_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12k_profile_backend_options_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12k_profile_backend_option_not_object")
            continue
        if PHASE12K_BACKEND_OPTION_REQUIRED_FIELDS - set(item):
            errors.append("phase12k_profile_backend_option_field_missing")
        if set(str(key) for key in item) - PHASE12K_BACKEND_OPTION_REQUIRED_FIELDS:
            errors.append("phase12k_profile_backend_option_unknown_field")
        label = _safe_phase12k_backend_option_label(item.get("backend_option_label"))
        labels.append(label)
        if label != item.get("backend_option_label"):
            errors.append("phase12k_profile_backend_option_label_invalid")
        expected = {
            "backend_option_status": PHASE12K_BACKEND_OPTION_STATUS,
            "credential_policy": PHASE12K_CREDENTIAL_POLICY,
            "metadata_only": True,
            "human_approval_required": True,
            "cost_guard_required": True,
            "private_health_data_allowed": False,
            "api_call_execution_granted": False,
            "sdk_execution_granted": False,
            "simulator_execution_granted": False,
            "provider_execution_granted": False,
            "network_call_execution_granted": False,
            "spending_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12k_profile_backend_option_value_invalid")
                break
    expected_labels = list(PHASE12K_BACKEND_OPTION_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12k_profile_backend_option_order_invalid")
    return tuple(errors)


def _phase12k_workload_class_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12k_profile_workload_classes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12k_profile_workload_class_not_object")
            continue
        if PHASE12K_WORKLOAD_CLASS_REQUIRED_FIELDS - set(item):
            errors.append("phase12k_profile_workload_class_field_missing")
        if set(str(key) for key in item) - PHASE12K_WORKLOAD_CLASS_REQUIRED_FIELDS:
            errors.append("phase12k_profile_workload_class_unknown_field")
        label = _safe_phase12k_workload_class_label(item.get("workload_class_label"))
        labels.append(label)
        if label != item.get("workload_class_label"):
            errors.append("phase12k_profile_workload_class_label_invalid")
        expected = {
            "workload_class_status": PHASE12K_WORKLOAD_CLASS_STATUS,
            "metadata_only": True,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "medical_advice_provided": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12k_profile_workload_class_value_invalid")
                break
    expected_labels = list(PHASE12K_WORKLOAD_CLASSES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12k_profile_workload_class_order_invalid")
    return tuple(errors)


def _phase12k_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12k_profile_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12k_profile_future_gate_not_object")
            continue
        if PHASE12K_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12k_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12K_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12k_profile_future_gate_unknown_field")
        label = _safe_phase12k_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12k_profile_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12K_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "human_approval_required": True,
            "cost_guard_required": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12k_profile_future_gate_value_invalid")
                break
    expected_labels = list(PHASE12K_REQUIRED_FUTURE_GATES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12k_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12k_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12k_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12k_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        PHASE12K_SOURCE_PHASE_RANGE.lower(),
        PHASE12K_CAPABILITY_PHASE,
        PHASE12K_AUTHORIZATION_STATUS,
        PHASE12K_GRANT_STATUS,
        PHASE12K_CREDENTIAL_POLICY,
        PHASE12K_PROFILE_STATUS,
        PHASE12K_BACKEND_OPTION_STATUS,
        PHASE12K_WORKLOAD_CLASS_STATUS,
        PHASE12K_FUTURE_GATE_STATUS,
        PHASE12K_SOURCE_REFERENCE_STATUS,
        *PHASE12K_STATUS_LABELS,
        *PHASE12K_BACKEND_OPTION_LABELS,
        *(label.lower() for label in PHASE12K_WORKLOAD_CLASSES),
        *PHASE12K_REQUIRED_FUTURE_GATES,
        PHASE12K_COMPUTE_BOUNDARY_STATEMENT.lower(),
        PHASE12K_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        PHASE12L_SOURCE_PHASE_RANGE.lower(),
        PHASE12L_CAPABILITY_PHASE,
        PHASE12L_AUTHORIZATION_STATUS,
        PHASE12L_GRANT_STATUS,
        PHASE12L_PROFILE_STATUS,
        PHASE12L_FABRIC_INTEROP_STATUS,
        PHASE12L_MESSAGE_CODEC_STATUS,
        PHASE12L_A2A_TRANSPORT_STATUS,
        PHASE12L_MCP_INTEROP_STATUS,
        PHASE12L_SECURE_DROP_STATUS,
        PHASE12L_CREDENTIAL_POLICY,
        PHASE12L_FABRIC_CAPABILITY_STATUS,
        PHASE12L_FORBIDDEN_LABEL_STATUS,
        PHASE12L_FUTURE_GATE_STATUS,
        PHASE12L_SOURCE_REFERENCE_STATUS,
        *PHASE12L_STATUS_LABELS,
        *PHASE12L_FABRIC_CAPABILITY_LABELS,
        *PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS,
        *PHASE12L_REQUIRED_FUTURE_GATES,
        PHASE12L_FABRIC_BOUNDARY_STATEMENT.lower(),
        PHASE12L_AUDIT_BOUNDARY_STATEMENT.lower(),
        PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        PHASE12M_SOURCE_PHASE_RANGE.lower(),
        PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        PHASE12M_AUTHORIZATION_STATUS,
        PHASE12M_GRANT_STATUS,
        PHASE12M_PROFILE_STATUS,
        PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
        PHASE12M_CANDIDATE_LABEL_STATUS,
        PHASE12M_FUTURE_GATE_STATUS,
        PHASE12M_SOURCE_REFERENCE_STATUS,
        *PHASE12M_STATUS_LABELS,
        *PHASE12M_MODEL_OPTION_CATEGORIES,
        *(label.lower() for label in PHASE12M_CANDIDATE_LABELS),
        *PHASE12M_REQUIRED_FUTURE_GATES,
        PHASE12M_MODEL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SENSOR_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "api call",
        "api-call",
        "sdk execution",
        "simulator execution",
        "provider call",
        "provider execution",
        "network call",
        "spending permitted",
        "spend permitted",
        "credential loading",
        "load credential",
        "runtime adapter",
        "model execution",
        "training execution",
        "fine-tuning execution",
        "fine tuning execution",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "clinical recommendation",
        "clinical decision support",
        "medical advice",
        "private health-data processing",
        "private health data processing",
        "private health-data allowed",
        "private health data allowed",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12l_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12l_profile_source_references_invalid",)
    errors: list[str] = []
    phase_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12l_profile_source_reference_not_object")
            continue
        if PHASE12L_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12l_profile_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12L_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12l_profile_source_reference_unknown_field")
        expected = (
            PHASE12L_SOURCE_REFERENCE_PHASES[index]
            if index < len(PHASE12L_SOURCE_REFERENCE_PHASES)
            else None
        )
        phase_label = str(item.get("phase_label") or "")
        phase_labels.append(phase_label)
        if expected is None:
            errors.append("phase12l_profile_source_reference_phase_invalid")
            continue
        expected_phase, expected_kind, _, expected_prefix = expected
        expected_values = {
            "phase_label": expected_phase,
            "source_kind": expected_kind,
            "reference_status": PHASE12L_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12l_profile_source_reference_value_invalid")
                break
        if _safe_phase12l_source_reference_id(
            item.get("source_reference_id"),
            expected_prefix,
        ) != item.get("source_reference_id"):
            errors.append("phase12l_profile_source_reference_id_invalid")
    expected_phases = [phase[0] for phase in PHASE12L_SOURCE_REFERENCE_PHASES]
    if phase_labels != expected_phases or len(phase_labels) != len(set(phase_labels)):
        errors.append("phase12l_profile_source_reference_order_invalid")
    return tuple(errors)


def _phase12l_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12l_profile_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12l_profile_status_label_not_object")
            continue
        if PHASE12L_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12l_profile_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12L_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12l_profile_status_label_unknown_field")
        label = _safe_phase12l_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12l_profile_status_label_invalid")
        expected = {
            "label_status": PHASE12L_FABRIC_CAPABILITY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12l_profile_status_label_value_invalid")
                break
    if labels != list(PHASE12L_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12l_profile_status_label_order_invalid")
    return tuple(errors)


def _phase12l_fabric_capability_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12l_profile_fabric_capability_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12l_profile_fabric_capability_not_object")
            continue
        if PHASE12L_FABRIC_CAPABILITY_REQUIRED_FIELDS - set(item):
            errors.append("phase12l_profile_fabric_capability_field_missing")
        if set(str(key) for key in item) - PHASE12L_FABRIC_CAPABILITY_REQUIRED_FIELDS:
            errors.append("phase12l_profile_fabric_capability_unknown_field")
        label = _safe_phase12l_fabric_capability_label(item.get("fabric_capability_label"))
        labels.append(label)
        if label != item.get("fabric_capability_label"):
            errors.append("phase12l_profile_fabric_capability_label_invalid")
        expected = {
            "capability_status": PHASE12L_FABRIC_CAPABILITY_STATUS,
            "metadata_only": True,
            "future_requirement_only": True,
            "implementation_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12l_profile_fabric_capability_value_invalid")
                break
    expected_labels = list(PHASE12L_FABRIC_CAPABILITY_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12l_profile_fabric_capability_order_invalid")
    return tuple(errors)


def _phase12l_forbidden_out_of_scope_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12l_profile_forbidden_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12l_profile_forbidden_label_not_object")
            continue
        if PHASE12L_FORBIDDEN_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12l_profile_forbidden_label_field_missing")
        if set(str(key) for key in item) - PHASE12L_FORBIDDEN_LABEL_REQUIRED_FIELDS:
            errors.append("phase12l_profile_forbidden_label_unknown_field")
        label = _safe_phase12l_forbidden_label(item.get("forbidden_label"))
        labels.append(label)
        if label != item.get("forbidden_label"):
            errors.append("phase12l_profile_forbidden_label_invalid")
        expected = {
            "forbidden_status": PHASE12L_FORBIDDEN_LABEL_STATUS,
            "metadata_only": True,
            "out_of_scope": True,
            "allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12l_profile_forbidden_label_value_invalid")
                break
    expected_labels = list(PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12l_profile_forbidden_label_order_invalid")
    return tuple(errors)


def _phase12l_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12l_profile_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12l_profile_future_gate_not_object")
            continue
        if PHASE12L_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12l_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12L_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12l_profile_future_gate_unknown_field")
        label = _safe_phase12l_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12l_profile_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12L_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12l_profile_future_gate_value_invalid")
                break
    expected_labels = list(PHASE12L_REQUIRED_FUTURE_GATES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12l_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12l_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12l_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12l_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        PHASE12L_SOURCE_PHASE_RANGE.lower(),
        PHASE12L_CAPABILITY_PHASE,
        PHASE12L_AUTHORIZATION_STATUS,
        PHASE12L_GRANT_STATUS,
        PHASE12L_PROFILE_STATUS,
        PHASE12L_FABRIC_INTEROP_STATUS,
        PHASE12L_MESSAGE_CODEC_STATUS,
        PHASE12L_A2A_TRANSPORT_STATUS,
        PHASE12L_MCP_INTEROP_STATUS,
        PHASE12L_SECURE_DROP_STATUS,
        PHASE12L_CREDENTIAL_POLICY,
        PHASE12L_FABRIC_CAPABILITY_STATUS,
        PHASE12L_FORBIDDEN_LABEL_STATUS,
        PHASE12L_FUTURE_GATE_STATUS,
        PHASE12L_SOURCE_REFERENCE_STATUS,
        *PHASE12L_STATUS_LABELS,
        *PHASE12L_FABRIC_CAPABILITY_LABELS,
        *PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS,
        *PHASE12L_REQUIRED_FUTURE_GATES,
        PHASE12L_FABRIC_BOUNDARY_STATEMENT.lower(),
        PHASE12L_AUDIT_BOUNDARY_STATEMENT.lower(),
        PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        PHASE12M_SOURCE_PHASE_RANGE.lower(),
        PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        PHASE12M_AUTHORIZATION_STATUS,
        PHASE12M_GRANT_STATUS,
        PHASE12M_PROFILE_STATUS,
        PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
        PHASE12M_CANDIDATE_LABEL_STATUS,
        PHASE12M_FUTURE_GATE_STATUS,
        PHASE12M_SOURCE_REFERENCE_STATUS,
        *PHASE12M_STATUS_LABELS,
        *PHASE12M_MODEL_OPTION_CATEGORIES,
        *(label.lower() for label in PHASE12M_CANDIDATE_LABELS),
        *PHASE12M_REQUIRED_FUTURE_GATES,
        PHASE12M_MODEL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SENSOR_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "messagecodec implementation",
        "message codec implementation",
        "codec implementation",
        "codec execution",
        "runtime messaging",
        "a2a transport",
        "handshake execution",
        "mcp serving",
        "mcp server",
        "mcp client",
        "mcp runtime",
        "secure drop send",
        "secure drop receive",
        "agent invoked secure drop",
        "automation invoked secure drop",
        "crypto implementation",
        "credential loading",
        "vault access",
        "env access",
        "secret access",
        "api key",
        "network call",
        "filesystem autoscan",
        "connector install",
        "connector installation",
        "pack registration",
        "pack install",
        "provider call",
        "provider execution",
        "model execution",
        "runtime adapter",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
        "cross-repo mutation",
        "cross repo mutation",
        "opaque traffic allowed",
        "opaque message acting",
        "covert channel",
        "bundled agpl codec",
        "glossopetrae vendoring",
        "st3gg vendoring",
        "untrusted content execution",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12m_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12m_profile_source_references_invalid",)
    errors: list[str] = []
    phase_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12m_profile_source_reference_not_object")
            continue
        if PHASE12M_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12m_profile_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12M_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12m_profile_source_reference_unknown_field")
        expected = (
            PHASE12M_SOURCE_REFERENCE_PHASES[index]
            if index < len(PHASE12M_SOURCE_REFERENCE_PHASES)
            else None
        )
        phase_label = str(item.get("phase_label") or "")
        phase_labels.append(phase_label)
        if expected is None:
            errors.append("phase12m_profile_source_reference_phase_invalid")
            continue
        expected_phase, expected_kind, _, expected_prefix = expected
        expected_values = {
            "phase_label": expected_phase,
            "source_kind": expected_kind,
            "reference_status": PHASE12M_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12m_profile_source_reference_value_invalid")
                break
        if _safe_phase12m_source_reference_id(
            item.get("source_reference_id"),
            expected_prefix,
        ) != item.get("source_reference_id"):
            errors.append("phase12m_profile_source_reference_id_invalid")
    expected_phases = [phase[0] for phase in PHASE12M_SOURCE_REFERENCE_PHASES]
    if phase_labels != expected_phases or len(phase_labels) != len(set(phase_labels)):
        errors.append("phase12m_profile_source_reference_order_invalid")
    return tuple(errors)


def _phase12m_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12m_profile_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12m_profile_status_label_not_object")
            continue
        if PHASE12M_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12m_profile_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12M_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12m_profile_status_label_unknown_field")
        label = _safe_phase12m_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12m_profile_status_label_invalid")
        expected = {
            "label_status": PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12m_profile_status_label_value_invalid")
                break
    if labels != list(PHASE12M_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12m_profile_status_label_order_invalid")
    return tuple(errors)


def _phase12m_model_option_category_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12m_profile_model_option_categories_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12m_profile_model_option_category_not_object")
            continue
        if PHASE12M_MODEL_OPTION_CATEGORY_REQUIRED_FIELDS - set(item):
            errors.append("phase12m_profile_model_option_category_field_missing")
        if set(str(key) for key in item) - PHASE12M_MODEL_OPTION_CATEGORY_REQUIRED_FIELDS:
            errors.append("phase12m_profile_model_option_category_unknown_field")
        label = _safe_phase12m_model_option_category_label(item.get("model_option_category_label"))
        labels.append(label)
        if label != item.get("model_option_category_label"):
            errors.append("phase12m_profile_model_option_category_label_invalid")
        expected = {
            "category_status": PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
            "selectable_metadata_only": True,
            "metadata_only": True,
            "future_option_only": True,
            "model_loading_added": False,
            "model_execution_permitted": False,
            "provider_execution_permitted": False,
            "training_permitted": False,
            "fine_tuning_permitted": False,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "device_access_allowed": False,
            "raw_sensor_processing_allowed": False,
            "monitoring_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12m_profile_model_option_category_value_invalid")
                break
    expected_labels = list(PHASE12M_MODEL_OPTION_CATEGORIES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12m_profile_model_option_category_order_invalid")
    return tuple(errors)


def _phase12m_candidate_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12m_profile_candidate_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12m_profile_candidate_label_not_object")
            continue
        if PHASE12M_CANDIDATE_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12m_profile_candidate_label_field_missing")
        if set(str(key) for key in item) - PHASE12M_CANDIDATE_LABEL_REQUIRED_FIELDS:
            errors.append("phase12m_profile_candidate_label_unknown_field")
        label = _safe_phase12m_candidate_label(item.get("candidate_label"))
        labels.append(label)
        if label != item.get("candidate_label"):
            errors.append("phase12m_profile_candidate_label_invalid")
        expected = {
            "candidate_status": PHASE12M_CANDIDATE_LABEL_STATUS,
            "selectable_metadata_only": True,
            "metadata_only": True,
            "future_option_only": True,
            "model_loading_added": False,
            "model_execution_permitted": False,
            "provider_execution_permitted": False,
            "training_permitted": False,
            "fine_tuning_permitted": False,
            "private_health_data_allowed": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "prescribing_allowed": False,
            "medical_advice_allowed": False,
            "device_access_allowed": False,
            "raw_sensor_processing_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12m_profile_candidate_label_value_invalid")
                break
    expected_labels = list(PHASE12M_CANDIDATE_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12m_profile_candidate_label_order_invalid")
    return tuple(errors)


def _phase12m_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12m_profile_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12m_profile_future_gate_not_object")
            continue
        if PHASE12M_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12m_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12M_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12m_profile_future_gate_unknown_field")
        label = _safe_phase12m_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12m_profile_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12M_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12m_profile_future_gate_value_invalid")
                break
    expected_labels = list(PHASE12M_REQUIRED_FUTURE_GATES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12m_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12m_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12m_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12m_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        PHASE12M_SOURCE_PHASE_RANGE.lower(),
        PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        PHASE12M_AUTHORIZATION_STATUS,
        PHASE12M_GRANT_STATUS,
        PHASE12M_PROFILE_STATUS,
        PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
        PHASE12M_CANDIDATE_LABEL_STATUS,
        PHASE12M_FUTURE_GATE_STATUS,
        PHASE12M_SOURCE_REFERENCE_STATUS,
        *PHASE12M_STATUS_LABELS,
        *PHASE12M_MODEL_OPTION_CATEGORIES,
        *(label.lower() for label in PHASE12M_CANDIDATE_LABELS),
        *PHASE12M_REQUIRED_FUTURE_GATES,
        PHASE12M_MODEL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SENSOR_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "model execution",
        "model loading",
        "load model",
        "provider execution",
        "provider call",
        "training execution",
        "fine-tuning execution",
        "fine tuning execution",
        "fine-tuned for runtime",
        "database ingestion",
        "web scraping",
        "network call",
        "runtime adapter",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
        "clinical decision support",
        "clinical recommendation",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "prescribing",
        "herb dosing",
        "supplement dosing",
        "calorie prescription",
        "macro prescription",
        "nutrition prescription",
        "private health data processing",
        "private health-data processing",
        "device access",
        "device connection",
        "raw sensor processing",
        "raw csi",
        "raw rf",
        "raw bia",
        "raw acoustic",
        "raw ultrasound",
        "monitoring enabled",
        "monitoring execution",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12n_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_source_references_invalid",)
    errors: list[str] = []
    phase_labels: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_source_reference_not_object")
            continue
        if PHASE12N_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12N_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12n_profile_source_reference_unknown_field")
        expected = (
            PHASE12N_SOURCE_REFERENCE_PHASES[index]
            if index < len(PHASE12N_SOURCE_REFERENCE_PHASES)
            else None
        )
        phase_label = str(item.get("phase_label") or "")
        phase_labels.append(phase_label)
        if expected is None:
            errors.append("phase12n_profile_source_reference_phase_invalid")
            continue
        expected_phase, expected_kind, _, expected_prefix = expected
        expected_values = {
            "phase_label": expected_phase,
            "source_kind": expected_kind,
            "reference_status": PHASE12N_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_source_reference_value_invalid")
                break
        if _safe_phase12n_source_reference_id(
            item.get("source_reference_id"),
            expected_prefix,
        ) != item.get("source_reference_id"):
            errors.append("phase12n_profile_source_reference_id_invalid")
    expected_phases = [phase[0] for phase in PHASE12N_SOURCE_REFERENCE_PHASES]
    if phase_labels != expected_phases or len(phase_labels) != len(set(phase_labels)):
        errors.append("phase12n_profile_source_reference_order_invalid")
    return tuple(errors)


def _phase12n_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_status_label_not_object")
            continue
        if PHASE12N_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12N_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12n_profile_status_label_unknown_field")
        label = _safe_phase12n_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12n_profile_status_label_invalid")
        expected = {
            "label_status": PHASE12N_WORKFLOW_MODE_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_status_label_value_invalid")
                break
    if labels != list(PHASE12N_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12n_profile_status_label_order_invalid")
    return tuple(errors)


def _phase12n_workflow_mode_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_workflow_modes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    definitions = dict(PHASE12N_WORKFLOW_MODES)
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_workflow_mode_not_object")
            continue
        if PHASE12N_WORKFLOW_MODE_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_workflow_mode_field_missing")
        if set(str(key) for key in item) - PHASE12N_WORKFLOW_MODE_REQUIRED_FIELDS:
            errors.append("phase12n_profile_workflow_mode_unknown_field")
        label = _safe_phase12n_workflow_mode_label(item.get("workflow_mode_label"))
        labels.append(label)
        if label != item.get("workflow_mode_label"):
            errors.append("phase12n_profile_workflow_mode_label_invalid")
        expected = {
            "mode_status": PHASE12N_WORKFLOW_MODE_STATUS,
            "mode_definition": definitions.get(label, ""),
            "metadata_only": True,
            "future_mode_only": True,
            "workflow_mode_execution_permitted": False,
            "runtime_orchestration_added": False,
            "model_routing_execution_permitted": False,
            "autonomous_experimentation_permitted": False,
            "code_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "diagnosis_or_treatment_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_workflow_mode_value_invalid")
                break
    expected_labels = [label for label, _ in PHASE12N_WORKFLOW_MODES]
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12n_profile_workflow_mode_order_invalid")
    return tuple(errors)


def _phase12n_fusion_concept_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_fusion_concepts_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_fusion_concept_not_object")
            continue
        if PHASE12N_FUSION_CONCEPT_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_fusion_concept_field_missing")
        if set(str(key) for key in item) - PHASE12N_FUSION_CONCEPT_REQUIRED_FIELDS:
            errors.append("phase12n_profile_fusion_concept_unknown_field")
        label = _safe_phase12n_fusion_concept_label(item.get("fusion_concept_label"))
        labels.append(label)
        if label != item.get("fusion_concept_label"):
            errors.append("phase12n_profile_fusion_concept_label_invalid")
        expected = {
            "concept_status": PHASE12N_FUSION_CONCEPT_STATUS,
            "metadata_only": True,
            "future_concept_only": True,
            "model_routing_execution_permitted": False,
            "provider_call_execution_granted": False,
            "model_loading_added": False,
            "learned_coordination_execution_granted": False,
            "agent_routing_execution_granted": False,
            "network_call_execution_granted": False,
            "runtime_orchestration_added": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_fusion_concept_value_invalid")
                break
    expected_labels = list(PHASE12N_FUSION_CONCEPT_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12n_profile_fusion_concept_order_invalid")
    return tuple(errors)


def _phase12n_scientist_evolution_concept_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_scientist_evolution_concepts_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_scientist_evolution_concept_not_object")
            continue
        if PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_scientist_evolution_concept_field_missing")
        if set(str(key) for key in item) - PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_REQUIRED_FIELDS:
            errors.append("phase12n_profile_scientist_evolution_concept_unknown_field")
        label = _safe_phase12n_scientist_evolution_concept_label(
            item.get("scientist_evolution_concept_label")
        )
        labels.append(label)
        if label != item.get("scientist_evolution_concept_label"):
            errors.append("phase12n_profile_scientist_evolution_concept_label_invalid")
        expected = {
            "concept_status": PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS,
            "metadata_only": True,
            "future_concept_only": True,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "web_access_permitted": False,
            "literature_search_execution_permitted": False,
            "database_ingestion_added": False,
            "manuscript_generation_added": False,
            "autonomous_publication_allowed": False,
            "model_training_execution_granted": False,
            "model_fine_tuning_execution_granted": False,
            "autonomous_research_action_permitted": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_scientist_evolution_concept_value_invalid")
                break
    expected_labels = list(PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12n_profile_scientist_evolution_concept_order_invalid")
    return tuple(errors)


def _phase12n_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12n_profile_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12n_profile_future_gate_not_object")
            continue
        if PHASE12N_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12n_profile_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12N_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12n_profile_future_gate_unknown_field")
        label = _safe_phase12n_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12n_profile_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12N_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12n_profile_future_gate_value_invalid")
                break
    expected_labels = list(PHASE12N_REQUIRED_FUTURE_GATES)
    if labels != expected_labels or len(labels) != len(set(labels)):
        errors.append("phase12n_profile_future_gate_order_invalid")
    return tuple(errors)


def _phase12n_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12n_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12n_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12N_SOURCE_PHASE_RANGE.lower(),
        PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        PHASE12N_AUTHORIZATION_STATUS,
        PHASE12N_GRANT_STATUS,
        PHASE12N_PROFILE_STATUS,
        PHASE12N_WORKFLOW_MODE_STATUS,
        PHASE12N_FUSION_CONCEPT_STATUS,
        PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS,
        PHASE12N_FUTURE_GATE_STATUS,
        PHASE12N_SOURCE_REFERENCE_STATUS,
        *PHASE12N_STATUS_LABELS,
        *(label for label, _ in PHASE12N_WORKFLOW_MODES),
        *(definition.lower() for _, definition in PHASE12N_WORKFLOW_MODES),
        *PHASE12N_FUSION_CONCEPT_LABELS,
        *PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS,
        *PHASE12N_REQUIRED_FUTURE_GATES,
        PHASE12N_WORKFLOW_BOUNDARY_STATEMENT.lower(),
        PHASE12N_FUSION_BOUNDARY_STATEMENT.lower(),
        PHASE12N_SCIENTIST_BOUNDARY_STATEMENT.lower(),
        PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "runtime orchestration",
        "orchestration execution",
        "workflow execution",
        "workflow mode execution",
        "model routing",
        "agent routing",
        "learned coordination",
        "provider call",
        "provider execution",
        "model loading",
        "model execution",
        "training execution",
        "fine-tuning execution",
        "fine tuning execution",
        "code execution",
        "experiment execution",
        "autonomous experimentation",
        "autonomous experiment",
        "autonomous research action",
        "web access",
        "literature search",
        "database ingestion",
        "web scraping",
        "network call",
        "runtime adapter",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
        "clinical decision support",
        "clinical recommendation",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "private health-data processing",
        "private health data processing",
        "device access",
        "sensor access",
        "raw sensor processing",
        "manuscript generation",
        "autonomous publication",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12o_source_profile_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12o_matrix_source_profile_not_object",)
    errors: list[str] = []
    if PHASE12O_SOURCE_PROFILE_REQUIRED_FIELDS - set(value):
        errors.append("phase12o_matrix_source_profile_field_missing")
    if set(str(key) for key in value) - PHASE12O_SOURCE_PROFILE_REQUIRED_FIELDS:
        errors.append("phase12o_matrix_source_profile_unknown_field")
    expected = {
        "source_phase_label": PHASE12O_SOURCE_PHASE,
        "source_kind": PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        "reference_status": PHASE12O_SOURCE_REFERENCE_STATUS,
        "metadata_only": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12o_matrix_source_profile_value_invalid")
            break
    if _safe_phase12n_profile_id(value.get("source_reference_id")) != value.get(
        "source_reference_id"
    ):
        errors.append("phase12o_matrix_source_profile_id_invalid")
    return tuple(errors)


def _phase12o_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12o_matrix_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12o_matrix_status_label_not_object")
            continue
        if PHASE12O_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12o_matrix_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12O_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12o_matrix_status_label_unknown_field")
        label = _safe_phase12o_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12o_matrix_status_label_invalid")
        expected = {
            "label_status": PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12o_matrix_status_label_value_invalid")
                break
    if labels != list(PHASE12O_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12o_matrix_status_label_order_invalid")
    return tuple(errors)


def _phase12o_workflow_mode_prerequisite_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12o_matrix_workflow_modes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12o_matrix_workflow_mode_not_object")
            continue
        if PHASE12O_WORKFLOW_MODE_MATRIX_REQUIRED_FIELDS - set(item):
            errors.append("phase12o_matrix_workflow_mode_field_missing")
        if set(str(key) for key in item) - PHASE12O_WORKFLOW_MODE_MATRIX_REQUIRED_FIELDS:
            errors.append("phase12o_matrix_workflow_mode_unknown_field")
        label = _safe_phase12o_workflow_mode_label(item.get("workflow_mode_label"))
        labels.append(label)
        if label != item.get("workflow_mode_label"):
            errors.append("phase12o_matrix_workflow_mode_label_invalid")
        gate_labels = item.get("required_future_gate_labels")
        if gate_labels != list(PHASE12O_REQUIRED_FUTURE_GATES):
            errors.append("phase12o_matrix_workflow_mode_gate_labels_invalid")
        expected = {
            "matrix_entry_status": PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
            "source_phase12n_mode_label": label,
            "metadata_only": True,
            "standalone_first": True,
            "runtime_prerequisite_only": True,
            "required_future_gate_count": len(PHASE12O_REQUIRED_FUTURE_GATES),
            "all_prerequisites_satisfied": False,
            "runtime_blocked": True,
            "review_required": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12o_matrix_workflow_mode_value_invalid")
                break
    if labels != list(PHASE12O_WORKFLOW_MODES) or len(labels) != len(set(labels)):
        errors.append("phase12o_matrix_workflow_mode_order_invalid")
    return tuple(errors)


def _phase12o_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12o_matrix_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12o_matrix_future_gate_not_object")
            continue
        if PHASE12O_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12o_matrix_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12O_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12o_matrix_future_gate_unknown_field")
        label = _safe_phase12o_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12o_matrix_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12O_FUTURE_GATE_STATUS,
            "gate_scope": PHASE12O_GATE_SCOPE,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "runtime_prerequisite_satisfied": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12o_matrix_future_gate_value_invalid")
                break
    if labels != list(PHASE12O_REQUIRED_FUTURE_GATES) or len(labels) != len(set(labels)):
        errors.append("phase12o_matrix_future_gate_order_invalid")
    return tuple(errors)


def _phase12o_mode_gate_requirement_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12o_matrix_mode_gate_requirements_invalid",)
    errors: list[str] = []
    pairs: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12o_matrix_mode_gate_requirement_not_object")
            continue
        if PHASE12O_MODE_GATE_REQUIREMENT_REQUIRED_FIELDS - set(item):
            errors.append("phase12o_matrix_mode_gate_requirement_field_missing")
        if set(str(key) for key in item) - PHASE12O_MODE_GATE_REQUIREMENT_REQUIRED_FIELDS:
            errors.append("phase12o_matrix_mode_gate_requirement_unknown_field")
        mode = _safe_phase12o_workflow_mode_label(item.get("workflow_mode_label"))
        gate = _safe_phase12o_future_gate(item.get("future_gate_label"))
        pairs.append((mode, gate))
        if mode != item.get("workflow_mode_label"):
            errors.append("phase12o_matrix_mode_gate_requirement_mode_invalid")
        if gate != item.get("future_gate_label"):
            errors.append("phase12o_matrix_mode_gate_requirement_gate_invalid")
        expected = {
            "gate_status": PHASE12O_MODE_GATE_STATUS,
            "gate_scope": PHASE12O_GATE_SCOPE,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "runtime_prerequisite_satisfied": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12o_matrix_mode_gate_requirement_value_invalid")
                break
    expected_pairs = [
        (mode, gate) for mode in PHASE12O_WORKFLOW_MODES for gate in PHASE12O_REQUIRED_FUTURE_GATES
    ]
    if pairs != expected_pairs or len(pairs) != len(set(pairs)):
        errors.append("phase12o_matrix_mode_gate_requirement_order_invalid")
    return tuple(errors)


def _phase12o_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12o_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12o_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12O_SOURCE_PHASE.lower(),
        PHASE12O_MATRIX_PHASE,
        PHASE12O_AUTHORIZATION_STATUS,
        PHASE12O_GRANT_STATUS,
        PHASE12O_MATRIX_STATUS,
        PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
        PHASE12O_FUTURE_GATE_STATUS,
        PHASE12O_MODE_GATE_STATUS,
        PHASE12O_SOURCE_REFERENCE_STATUS,
        PHASE12O_GATE_SCOPE,
        *PHASE12O_STATUS_LABELS,
        *PHASE12O_WORKFLOW_MODES,
        *PHASE12O_REQUIRED_FUTURE_GATES,
        PHASE12O_MATRIX_BOUNDARY_STATEMENT.lower(),
        PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12O_STANDALONE_FIRST_STATEMENT.lower(),
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12P_SOURCE_PHASE_RANGE.lower(),
        PHASE12P_PACKET_PHASE,
        PHASE12P_AUTHORIZATION_STATUS,
        PHASE12P_GRANT_STATUS,
        PHASE12P_REQUESTED_TRANSITION_STATUS,
        PHASE12P_PACKET_STATUS,
        PHASE12P_MODE_PACKET_STATUS,
        PHASE12P_FUTURE_GATE_STATUS,
        PHASE12P_REVIEWER_CLASS_STATUS,
        PHASE12P_RISK_PLACEHOLDER_STATUS,
        PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
        PHASE12P_SOURCE_REFERENCE_STATUS,
        PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
        PHASE12P_DENIAL_BLOCKED_STATUS,
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        *PHASE12P_STATUS_LABELS,
        *PHASE12P_WORKFLOW_MODES,
        *PHASE12P_REQUIRED_FUTURE_GATES,
        *PHASE12P_REQUIRED_REVIEWER_CLASSES,
        *PHASE12P_RISK_SUMMARY_PLACEHOLDERS,
        *PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS,
        PHASE12P_PACKET_BOUNDARY_STATEMENT.lower(),
        PHASE12P_REVIEW_REQUIREMENT_STATEMENT.lower(),
        PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        PHASE12Q_SOURCE_PHASE_RANGE.lower(),
        PHASE12Q_DECISION_RECORD_PHASE,
        PHASE12Q_AUTHORIZATION_STATUS,
        PHASE12Q_GRANT_STATUS,
        PHASE12Q_DECISION_RECORD_STATUS,
        PHASE12Q_SOURCE_REFERENCE_STATUS,
        PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
        PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
        *PHASE12Q_DECISION_STATUSES,
        *PHASE12Q_DECISION_REASON_CODES,
        *PHASE12Q_DECISION_STATUS_DISPOSITIONS.values(),
        *PHASE12Q_STATUS_LABELS,
        *PHASE12Q_WORKFLOW_MODES,
        *PHASE12Q_REQUIRED_FUTURE_GATES,
        *PHASE12Q_REQUIRED_REVIEWER_CLASSES,
        PHASE12Q_DECISION_SUMMARY.lower(),
        PHASE12Q_DECISION_BOUNDARY_STATEMENT.lower(),
        PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        PHASE12R_SOURCE_PHASE_RANGE.lower(),
        PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        PHASE12R_AUTHORIZATION_STATUS,
        PHASE12R_GRANT_STATUS,
        PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        PHASE12R_SOURCE_REFERENCE_STATUS,
        PHASE12R_MODE_INDEX_STATUS,
        PHASE12R_PACKET_REFERENCE_STATUS,
        PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
        PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
        PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
        PHASE12R_STALE_STATUS,
        PHASE12R_REVIEW_NEEDED_STATUS,
        PHASE12R_STALE_REVIEW_NEEDED_STATUS,
        *PHASE12R_STATUS_LABELS,
        *PHASE12R_WORKFLOW_MODES,
        *PHASE12R_REQUIRED_FUTURE_GATES,
        *PHASE12R_REQUIRED_REVIEWER_CLASSES,
        PHASE12R_DECISION_SUMMARY.lower(),
        PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT.lower(),
        PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
        PHASE12S_SOURCE_PHASE_RANGE.lower(),
        PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        PHASE12S_AUTHORIZATION_STATUS,
        PHASE12S_GRANT_STATUS,
        PHASE12S_SUMMARY_STATUS,
        PHASE12S_SOURCE_REFERENCE_STATUS,
        PHASE12S_MODE_COVERAGE_STATUS,
        PHASE12S_REVIEW_CHAIN_STATUS,
        PHASE12S_REVIEWER_NAVIGATION_SUMMARY.lower(),
        PHASE12S_OPERATOR_HANDOFF_SUMMARY.lower(),
        *PHASE12S_CLOSEOUT_STATUSES,
        *PHASE12S_STATUS_LABELS,
        *PHASE12S_WORKFLOW_MODES,
        *PHASE12S_REQUIRED_FUTURE_GATES,
        *PHASE12S_REQUIRED_REVIEWER_CLASSES,
        PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT.lower(),
        PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    blocked_fragments = (
        "runtime adapter",
        "workflow execution",
        "workflow mode execution",
        "runtime prerequisite satisfied",
        "all prerequisites satisfied",
        "model routing",
        "provider execution",
        "model execution",
        "code execution",
        "experiment execution",
        "web behavior",
        "database behavior",
        "network behavior",
        "web access",
        "database ingestion",
        "web scraping",
        "network call",
        "clinical decision support",
        "private health-data processing",
        "private health data processing",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "device access",
        "raw sensor processing",
        "production ready",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12p_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_source_references_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    expected = (
        ("12N", PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND),
        ("12O", PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND),
    )
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_source_reference_not_object")
            continue
        if PHASE12P_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12P_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12p_packet_source_reference_unknown_field")
        label = str(item.get("source_phase_label") or "")
        labels.append(label)
        if label == "12N":
            if _safe_phase12n_profile_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12p_packet_source_reference_id_invalid")
        elif label == "12O":
            if _safe_phase12o_matrix_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12p_packet_source_reference_id_invalid")
        else:
            errors.append("phase12p_packet_source_reference_phase_invalid")
        expected_values = {
            "reference_status": PHASE12P_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_source_reference_value_invalid")
                break
    if labels != [phase for phase, _ in expected]:
        errors.append("phase12p_packet_source_reference_order_invalid")
    for item, (phase, kind) in zip(
        value if isinstance(value, list) else [], expected, strict=False
    ):
        if isinstance(item, Mapping) and (
            item.get("source_phase_label") != phase or item.get("source_kind") != kind
        ):
            errors.append("phase12p_packet_source_reference_kind_invalid")
            break
    return tuple(errors)


def _phase12p_prerequisite_matrix_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12p_packet_prerequisite_matrix_reference_not_object",)
    errors: list[str] = []
    if PHASE12P_PREREQUISITE_MATRIX_REFERENCE_REQUIRED_FIELDS - set(value):
        errors.append("phase12p_packet_prerequisite_matrix_reference_field_missing")
    if set(str(key) for key in value) - PHASE12P_PREREQUISITE_MATRIX_REFERENCE_REQUIRED_FIELDS:
        errors.append("phase12p_packet_prerequisite_matrix_reference_unknown_field")
    expected = {
        "source_phase_label": "12O",
        "source_kind": PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        "reference_status": PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
        "required_future_gate_labels": list(PHASE12P_REQUIRED_FUTURE_GATES),
        "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
        "workflow_mode_prerequisite_count": len(PHASE12P_WORKFLOW_MODES),
        "runtime_prerequisites_satisfied": False,
        "metadata_only": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12p_packet_prerequisite_matrix_reference_value_invalid")
            break
    if _safe_phase12o_matrix_id(value.get("source_reference_id")) != value.get(
        "source_reference_id"
    ):
        errors.append("phase12p_packet_prerequisite_matrix_reference_id_invalid")
    return tuple(errors)


def _phase12p_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_status_label_not_object")
            continue
        if PHASE12P_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12P_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12p_packet_status_label_unknown_field")
        label = _safe_phase12p_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12p_packet_status_label_invalid")
        expected = {
            "label_status": PHASE12P_MODE_PACKET_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_status_label_value_invalid")
                break
    if labels != list(PHASE12P_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_status_label_order_invalid")
    return tuple(errors)


def _phase12p_mode_review_packet_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_mode_review_packets_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_mode_review_packet_not_object")
            continue
        if PHASE12P_MODE_REVIEW_PACKET_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_mode_review_packet_field_missing")
        if set(str(key) for key in item) - PHASE12P_MODE_REVIEW_PACKET_REQUIRED_FIELDS:
            errors.append("phase12p_packet_mode_review_packet_unknown_field")
        label = _safe_phase12p_workflow_mode_label(item.get("requested_workflow_mode_label"))
        labels.append(label)
        if label != item.get("requested_workflow_mode_label"):
            errors.append("phase12p_packet_mode_review_packet_label_invalid")
        expected = {
            "packet_entry_status": PHASE12P_MODE_PACKET_STATUS,
            "requested_transition_status": PHASE12P_REQUESTED_TRANSITION_STATUS,
            "required_future_gate_labels": list(PHASE12P_REQUIRED_FUTURE_GATES),
            "required_future_gate_count": len(PHASE12P_REQUIRED_FUTURE_GATES),
            "required_reviewer_class_labels": list(PHASE12P_REQUIRED_REVIEWER_CLASSES),
            "required_reviewer_class_count": len(PHASE12P_REQUIRED_REVIEWER_CLASSES),
            "risk_summary_placeholder_labels": list(PHASE12P_RISK_SUMMARY_PLACEHOLDERS),
            "evidence_inventory_placeholder_labels": list(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS),
            "denial_blocked_default_fail_closed_status": PHASE12P_DENIAL_BLOCKED_STATUS,
            "metadata_only": True,
            "review_packet_boundary_only": True,
            "standalone_first": True,
            "not_authorized": True,
            "no_active_grant": True,
            "no_runtime_authorization": True,
            "no_execution_permission": True,
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "model_execution_granted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "autonomous_experimentation_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_mode_review_packet_value_invalid")
                break
        if _safe_phase12o_matrix_id(item.get("prerequisite_matrix_reference_id")) != item.get(
            "prerequisite_matrix_reference_id"
        ):
            errors.append("phase12p_packet_mode_review_packet_matrix_id_invalid")
    if labels != list(PHASE12P_WORKFLOW_MODES) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_mode_review_packet_order_invalid")
    return tuple(errors)


def _phase12p_future_gate_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_future_gates_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_future_gate_not_object")
            continue
        if PHASE12P_FUTURE_GATE_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_future_gate_field_missing")
        if set(str(key) for key in item) - PHASE12P_FUTURE_GATE_REQUIRED_FIELDS:
            errors.append("phase12p_packet_future_gate_unknown_field")
        label = _safe_phase12p_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12p_packet_future_gate_label_invalid")
        expected = {
            "gate_status": PHASE12P_FUTURE_GATE_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "review_completed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_future_gate_value_invalid")
                break
    if labels != list(PHASE12P_REQUIRED_FUTURE_GATES) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_future_gate_order_invalid")
    return tuple(errors)


def _phase12p_reviewer_class_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_reviewer_classes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_reviewer_class_not_object")
            continue
        if PHASE12P_REVIEWER_CLASS_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_reviewer_class_field_missing")
        if set(str(key) for key in item) - PHASE12P_REVIEWER_CLASS_REQUIRED_FIELDS:
            errors.append("phase12p_packet_reviewer_class_unknown_field")
        label = _safe_phase12p_reviewer_class(item.get("reviewer_class_label"))
        labels.append(label)
        if label != item.get("reviewer_class_label"):
            errors.append("phase12p_packet_reviewer_class_label_invalid")
        expected = {
            "reviewer_class_status": PHASE12P_REVIEWER_CLASS_STATUS,
            "required": True,
            "completed": False,
            "approved": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_reviewer_class_value_invalid")
                break
    if labels != list(PHASE12P_REQUIRED_REVIEWER_CLASSES) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_reviewer_class_order_invalid")
    return tuple(errors)


def _phase12p_risk_summary_placeholder_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_risk_placeholders_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_risk_placeholder_not_object")
            continue
        if PHASE12P_RISK_SUMMARY_PLACEHOLDER_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_risk_placeholder_field_missing")
        if set(str(key) for key in item) - PHASE12P_RISK_SUMMARY_PLACEHOLDER_REQUIRED_FIELDS:
            errors.append("phase12p_packet_risk_placeholder_unknown_field")
        label = _safe_phase12p_risk_placeholder(item.get("risk_summary_placeholder_label"))
        labels.append(label)
        if label != item.get("risk_summary_placeholder_label"):
            errors.append("phase12p_packet_risk_placeholder_label_invalid")
        expected = {
            "placeholder_status": PHASE12P_RISK_PLACEHOLDER_STATUS,
            "required": True,
            "filled": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_risk_placeholder_value_invalid")
                break
    if labels != list(PHASE12P_RISK_SUMMARY_PLACEHOLDERS) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_risk_placeholder_order_invalid")
    return tuple(errors)


def _phase12p_evidence_inventory_placeholder_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12p_packet_evidence_placeholders_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12p_packet_evidence_placeholder_not_object")
            continue
        if PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDER_REQUIRED_FIELDS - set(item):
            errors.append("phase12p_packet_evidence_placeholder_field_missing")
        if set(str(key) for key in item) - PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDER_REQUIRED_FIELDS:
            errors.append("phase12p_packet_evidence_placeholder_unknown_field")
        label = _safe_phase12p_evidence_placeholder(
            item.get("evidence_inventory_placeholder_label")
        )
        labels.append(label)
        if label != item.get("evidence_inventory_placeholder_label"):
            errors.append("phase12p_packet_evidence_placeholder_label_invalid")
        expected = {
            "placeholder_status": PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
            "required": True,
            "filled": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12p_packet_evidence_placeholder_value_invalid")
                break
    if labels != list(PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS) or len(labels) != len(set(labels)):
        errors.append("phase12p_packet_evidence_placeholder_order_invalid")
    return tuple(errors)


def _phase12p_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12p_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12p_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12P_SOURCE_PHASE_RANGE.lower(),
        PHASE12P_PACKET_PHASE,
        PHASE12P_AUTHORIZATION_STATUS,
        PHASE12P_GRANT_STATUS,
        PHASE12P_REQUESTED_TRANSITION_STATUS,
        PHASE12P_PACKET_STATUS,
        PHASE12P_MODE_PACKET_STATUS,
        PHASE12P_FUTURE_GATE_STATUS,
        PHASE12P_REVIEWER_CLASS_STATUS,
        PHASE12P_RISK_PLACEHOLDER_STATUS,
        PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
        PHASE12P_SOURCE_REFERENCE_STATUS,
        PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
        PHASE12P_DENIAL_BLOCKED_STATUS,
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        *PHASE12P_STATUS_LABELS,
        *PHASE12P_WORKFLOW_MODES,
        *PHASE12P_REQUIRED_FUTURE_GATES,
        *PHASE12P_REQUIRED_REVIEWER_CLASSES,
        *PHASE12P_RISK_SUMMARY_PLACEHOLDERS,
        *PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS,
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12P_PACKET_BOUNDARY_STATEMENT.lower(),
        PHASE12P_REVIEW_REQUIREMENT_STATEMENT.lower(),
        PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    if lowered.startswith("p12p-workflow-mode-review-packet-"):
        return 0
    blocked_fragments = (
        "activation",
        "activate",
        "enablement",
        "enabled",
        "approval",
        "approved",
        "grant",
        "granted",
        "runtime authorization",
        "execution permission",
        "workflow execution",
        "workflow mode execution",
        "mode execution",
        "model routing",
        "provider execution",
        "model execution",
        "model loading",
        "training",
        "fine-tuning",
        "code execution",
        "experiment execution",
        "autonomous experimentation",
        "web access",
        "database ingestion",
        "web scraping",
        "network call",
        "clinical decision support",
        "clinical use",
        "private health-data processing",
        "private health data processing",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "device access",
        "sensor access",
        "raw sensor processing",
        "production ready",
        "production readiness",
        "active grant",
        "real-mode authorization",
        "real mode authorization",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12q_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12q_decision_record_source_references_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    expected = (
        ("12N", PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND),
        ("12O", PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND),
        ("12P", PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND),
    )
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12q_decision_record_source_reference_not_object")
            continue
        if PHASE12Q_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12q_decision_record_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12Q_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12q_decision_record_source_reference_unknown_field")
        label = str(item.get("source_phase_label") or "")
        labels.append(label)
        if label == "12N":
            if _safe_phase12n_profile_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12q_decision_record_source_reference_id_invalid")
        elif label == "12O":
            if _safe_phase12o_matrix_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12q_decision_record_source_reference_id_invalid")
        elif label == "12P":
            if _safe_phase12p_packet_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12q_decision_record_source_reference_id_invalid")
        else:
            errors.append("phase12q_decision_record_source_reference_phase_invalid")
        expected_values = {
            "reference_status": PHASE12Q_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12q_decision_record_source_reference_value_invalid")
                break
    if labels != [phase for phase, _ in expected]:
        errors.append("phase12q_decision_record_source_reference_order_invalid")
    for item, (phase, kind) in zip(
        value if isinstance(value, list) else [], expected, strict=False
    ):
        if isinstance(item, Mapping) and (
            item.get("source_phase_label") != phase or item.get("source_kind") != kind
        ):
            errors.append("phase12q_decision_record_source_reference_kind_invalid")
            break
    return tuple(errors)


def _phase12q_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12q_decision_record_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12q_decision_record_status_label_not_object")
            continue
        if PHASE12Q_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12q_decision_record_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12Q_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12q_decision_record_status_label_unknown_field")
        label = _safe_phase12q_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12q_decision_record_status_label_invalid")
        expected = {
            "label_status": PHASE12Q_DECISION_RECORD_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12q_decision_record_status_label_value_invalid")
                break
    if labels != list(PHASE12Q_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12q_decision_record_status_label_order_invalid")
    return tuple(errors)


def _phase12q_future_gate_snapshot_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12q_decision_record_future_gate_snapshot_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12q_decision_record_future_gate_snapshot_not_object")
            continue
        if PHASE12Q_FUTURE_GATE_SNAPSHOT_REQUIRED_FIELDS - set(item):
            errors.append("phase12q_decision_record_future_gate_snapshot_field_missing")
        if set(str(key) for key in item) - PHASE12Q_FUTURE_GATE_SNAPSHOT_REQUIRED_FIELDS:
            errors.append("phase12q_decision_record_future_gate_snapshot_unknown_field")
        label = _safe_phase12q_future_gate(item.get("future_gate_label"))
        labels.append(label)
        if label != item.get("future_gate_label"):
            errors.append("phase12q_decision_record_future_gate_snapshot_label_invalid")
        expected = {
            "gate_status": PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
            "metadata_only": True,
            "satisfied": False,
            "passed": False,
            "review_completed": False,
            "blocks_runtime_authorization": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12q_decision_record_future_gate_snapshot_value_invalid")
                break
    if labels != list(PHASE12Q_REQUIRED_FUTURE_GATES) or len(labels) != len(set(labels)):
        errors.append("phase12q_decision_record_future_gate_snapshot_order_invalid")
    return tuple(errors)


def _phase12q_reviewer_class_required_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12q_decision_record_reviewer_classes_required_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12q_decision_record_reviewer_class_required_not_object")
            continue
        if PHASE12Q_REVIEWER_CLASS_REQUIRED_FIELDS - set(item):
            errors.append("phase12q_decision_record_reviewer_class_required_field_missing")
        if set(str(key) for key in item) - PHASE12Q_REVIEWER_CLASS_REQUIRED_FIELDS:
            errors.append("phase12q_decision_record_reviewer_class_required_unknown_field")
        label = _safe_phase12q_reviewer_class(item.get("reviewer_class_label"))
        labels.append(label)
        if label != item.get("reviewer_class_label"):
            errors.append("phase12q_decision_record_reviewer_class_required_label_invalid")
        expected = {
            "reviewer_class_status": PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
            "required": True,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12q_decision_record_reviewer_class_required_value_invalid")
                break
    if labels != list(PHASE12Q_REQUIRED_REVIEWER_CLASSES) or len(labels) != len(set(labels)):
        errors.append("phase12q_decision_record_reviewer_class_required_order_invalid")
    return tuple(errors)


def _phase12q_reviewer_class_represented_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12q_decision_record_reviewer_classes_represented_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12q_decision_record_reviewer_class_represented_not_object")
            continue
        if PHASE12Q_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS - set(item):
            errors.append("phase12q_decision_record_reviewer_class_represented_field_missing")
        if set(str(key) for key in item) - PHASE12Q_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS:
            errors.append("phase12q_decision_record_reviewer_class_represented_unknown_field")
        label = _safe_phase12q_reviewer_class(item.get("reviewer_class_label"))
        labels.append(label)
        if label != item.get("reviewer_class_label"):
            errors.append("phase12q_decision_record_reviewer_class_represented_label_invalid")
        expected = {
            "reviewer_class_status": PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
            "represented": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12q_decision_record_reviewer_class_represented_value_invalid")
                break
    if labels != list(PHASE12Q_REQUIRED_REVIEWER_CLASSES) or len(labels) != len(set(labels)):
        errors.append("phase12q_decision_record_reviewer_class_represented_order_invalid")
    return tuple(errors)


def _phase12q_decision_status_flags(decision_status: str) -> dict[str, bool]:
    status = _safe_phase12q_decision_status(decision_status) or PHASE12Q_DEFAULT_DECISION_STATUS
    return {
        "request_review_not_submitted": status == "review-not-submitted",
        "request_review_blocked": status == "review-blocked",
        "request_returned_for_fix_only_changes": status == "returned-for-fix-only-changes",
        "request_denied_no_runtime_authorization": status == "denied-no-runtime-authorization",
        "request_expired_no_runtime_authorization": status == "expired-no-runtime-authorization",
        "request_review_complete_no_runtime_authorization": (
            status == "review-complete-no-runtime-authorization"
        ),
    }


def _phase12q_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12q_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12q_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        PHASE12Q_SOURCE_PHASE_RANGE.lower(),
        PHASE12Q_DECISION_RECORD_PHASE,
        PHASE12Q_AUTHORIZATION_STATUS,
        PHASE12Q_GRANT_STATUS,
        PHASE12Q_DECISION_RECORD_STATUS,
        PHASE12Q_SOURCE_REFERENCE_STATUS,
        PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
        PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        *PHASE12Q_DECISION_STATUSES,
        *PHASE12Q_DECISION_REASON_CODES,
        *PHASE12Q_DECISION_STATUS_DISPOSITIONS.values(),
        *PHASE12Q_STATUS_LABELS,
        *PHASE12Q_WORKFLOW_MODES,
        *PHASE12Q_REQUIRED_FUTURE_GATES,
        *PHASE12Q_REQUIRED_REVIEWER_CLASSES,
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12Q_DECISION_SUMMARY.lower(),
        PHASE12Q_DECISION_BOUNDARY_STATEMENT.lower(),
        PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    if lowered.startswith(
        (
            "p12n-workflow-mode-registry-profile-",
            "p12o-workflow-safety-gate-matrix-",
            "p12p-workflow-mode-review-packet-",
            "p12q-workflow-mode-review-decision-",
        )
    ):
        return 0
    blocked_fragments = (
        "approval-for-runtime",
        "approval for runtime",
        "approved-for-runtime",
        "approved for runtime",
        "approval",
        "approved",
        "activation approved",
        "activation permitted",
        "activation enabled",
        "mode enablement",
        "enablement",
        "active grant",
        "grant created",
        "runtime authorization granted",
        "runtime enabled",
        "execution permission granted",
        "execution permitted true",
        "workflow execution",
        "workflow mode execution",
        "model routing",
        "provider execution",
        "model execution",
        "model loading",
        "training",
        "fine-tuning",
        "fine tuning",
        "code execution",
        "experiment execution",
        "autonomous experimentation",
        "web access",
        "database ingestion",
        "web scraping",
        "network call",
        "clinical use",
        "clinical decision support",
        "diagnosis",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "device access",
        "sensor access",
        "raw sensor processing",
        "private health-data processing",
        "private health data processing",
        "production ready",
        "production readiness",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12r_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12r_audit_trail_index_source_references_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    expected = (
        ("12N", PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND),
        ("12O", PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND),
        ("12P", PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND),
        ("12Q", PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND),
    )
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12r_audit_trail_index_source_reference_not_object")
            continue
        if PHASE12R_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12r_audit_trail_index_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12R_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12r_audit_trail_index_source_reference_unknown_field")
        label = str(item.get("source_phase_label") or "")
        labels.append(label)
        if label == "12N":
            if _safe_phase12n_profile_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12r_audit_trail_index_source_reference_id_invalid")
        elif label == "12O":
            if _safe_phase12o_matrix_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12r_audit_trail_index_source_reference_id_invalid")
        elif label == "12P":
            if _safe_phase12p_packet_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12r_audit_trail_index_source_reference_id_invalid")
        elif label == "12Q":
            if _safe_phase12q_decision_record_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12r_audit_trail_index_source_reference_id_invalid")
        else:
            errors.append("phase12r_audit_trail_index_source_reference_phase_invalid")
        expected_values = {
            "reference_status": PHASE12R_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12r_audit_trail_index_source_reference_value_invalid")
                break
    if labels != [phase for phase, _ in expected]:
        errors.append("phase12r_audit_trail_index_source_reference_order_invalid")
    for item, (phase, kind) in zip(
        value if isinstance(value, list) else [], expected, strict=False
    ):
        if isinstance(item, Mapping) and (
            item.get("source_phase_label") != phase or item.get("source_kind") != kind
        ):
            errors.append("phase12r_audit_trail_index_source_reference_kind_invalid")
            break
    return tuple(errors)


def _phase12r_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12r_audit_trail_index_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12r_audit_trail_index_status_label_not_object")
            continue
        if PHASE12R_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12r_audit_trail_index_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12R_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12r_audit_trail_index_status_label_unknown_field")
        label = _safe_phase12r_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12r_audit_trail_index_status_label_invalid")
        expected = {
            "label_status": PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12r_audit_trail_index_status_label_value_invalid")
                break
    if labels != list(PHASE12R_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12r_audit_trail_index_status_label_order_invalid")
    return tuple(errors)


def _phase12r_indexed_workflow_mode_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12r_audit_trail_index_workflow_modes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12r_audit_trail_index_workflow_mode_not_object")
            continue
        if PHASE12R_INDEXED_WORKFLOW_MODE_REQUIRED_FIELDS - set(item):
            errors.append("phase12r_audit_trail_index_workflow_mode_field_missing")
        if set(str(key) for key in item) - PHASE12R_INDEXED_WORKFLOW_MODE_REQUIRED_FIELDS:
            errors.append("phase12r_audit_trail_index_workflow_mode_unknown_field")
        label = _safe_phase12r_workflow_mode_label(item.get("workflow_mode_label"))
        labels.append(label)
        if label != item.get("workflow_mode_label"):
            errors.append("phase12r_audit_trail_index_workflow_mode_label_invalid")
        expected = {
            "mode_index_status": PHASE12R_MODE_INDEX_STATUS,
            "metadata_only": True,
            "indexed_for_audit_only": True,
            "required_future_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
            "unsatisfied_gate_count": len(PHASE12R_REQUIRED_FUTURE_GATES),
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "code_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12r_audit_trail_index_workflow_mode_value_invalid")
                break
    if labels != list(PHASE12R_WORKFLOW_MODES) or len(labels) != len(set(labels)):
        errors.append("phase12r_audit_trail_index_workflow_mode_order_invalid")
    return tuple(errors)


def _phase12r_activation_packet_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12r_audit_trail_index_packet_reference_not_object",)
    errors: list[str] = []
    if PHASE12R_PACKET_REFERENCE_REQUIRED_FIELDS - set(value):
        errors.append("phase12r_audit_trail_index_packet_reference_field_missing")
    if set(str(key) for key in value) - PHASE12R_PACKET_REFERENCE_REQUIRED_FIELDS:
        errors.append("phase12r_audit_trail_index_packet_reference_unknown_field")
    expected = {
        "source_phase_label": "12P",
        "source_kind": PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        "reference_status": PHASE12R_PACKET_REFERENCE_STATUS,
        "metadata_only": True,
        "workflow_mode_activation_not_permitted": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12r_audit_trail_index_packet_reference_value_invalid")
            break
    if _safe_phase12p_packet_id(value.get("activation_request_packet_id")) != value.get(
        "activation_request_packet_id"
    ):
        errors.append("phase12r_audit_trail_index_packet_reference_id_invalid")
    if _safe_phase12r_workflow_mode_label(value.get("requested_workflow_mode_label")) != value.get(
        "requested_workflow_mode_label"
    ):
        errors.append("phase12r_audit_trail_index_packet_reference_workflow_mode_invalid")
    return tuple(errors)


def _phase12r_decision_record_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12r_audit_trail_index_decision_record_reference_not_object",)
    errors: list[str] = []
    if PHASE12R_DECISION_RECORD_REFERENCE_REQUIRED_FIELDS - set(value):
        errors.append("phase12r_audit_trail_index_decision_record_reference_field_missing")
    if set(str(key) for key in value) - PHASE12R_DECISION_RECORD_REFERENCE_REQUIRED_FIELDS:
        errors.append("phase12r_audit_trail_index_decision_record_reference_unknown_field")
    decision_status = _safe_phase12q_decision_status(value.get("decision_status"))
    expected = {
        "source_phase_label": "12Q",
        "source_kind": PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        "reference_status": PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
        "decision_reason_code": PHASE12Q_DECISION_STATUS_REASON_CODES.get(decision_status),
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS.get(decision_status),
        "metadata_only": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "no_active_grant": True,
        "no_execution_permission": True,
        "runtime_stage": REAL_MODE_PHASE_RUNTIME,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12r_audit_trail_index_decision_record_reference_value_invalid")
            break
    if not decision_status or decision_status != value.get("decision_status"):
        errors.append("phase12r_audit_trail_index_decision_record_reference_status_invalid")
    if _safe_phase12q_decision_record_id(value.get("decision_record_id")) != value.get(
        "decision_record_id"
    ):
        errors.append("phase12r_audit_trail_index_decision_record_reference_id_invalid")
    return tuple(errors)


def _phase12r_decision_status_summary_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("phase12r_audit_trail_index_decision_status_summary_not_object",)
    errors: list[str] = []
    if PHASE12R_DECISION_STATUS_SUMMARY_REQUIRED_FIELDS - set(value):
        errors.append("phase12r_audit_trail_index_decision_status_summary_field_missing")
    if set(str(key) for key in value) - PHASE12R_DECISION_STATUS_SUMMARY_REQUIRED_FIELDS:
        errors.append("phase12r_audit_trail_index_decision_status_summary_unknown_field")
    decision_status = _safe_phase12q_decision_status(value.get("decision_status"))
    expected_flags = _phase12q_decision_status_flags(decision_status)
    expected = {
        "decision_reason_code": PHASE12Q_DECISION_STATUS_REASON_CODES.get(decision_status),
        "request_disposition_status": PHASE12Q_DECISION_STATUS_DISPOSITIONS.get(decision_status),
        "decision_status_summary_status": PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
        **expected_flags,
        "metadata_only": True,
        "runtime_authorization_not_granted": True,
        "workflow_mode_activation_not_permitted": True,
        "no_execution_permission": True,
        "execution_permitted": False,
        "real_mode_runtime_enabled": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append("phase12r_audit_trail_index_decision_status_summary_value_invalid")
            break
    if not decision_status or decision_status != value.get("decision_status"):
        errors.append("phase12r_audit_trail_index_decision_status_summary_status_invalid")
    return tuple(errors)


def _phase12r_reviewer_class_required_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12r_audit_trail_index_reviewer_classes_required_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12r_audit_trail_index_reviewer_class_required_not_object")
            continue
        if PHASE12R_REVIEWER_CLASS_REQUIRED_FIELDS - set(item):
            errors.append("phase12r_audit_trail_index_reviewer_class_required_field_missing")
        if set(str(key) for key in item) - PHASE12R_REVIEWER_CLASS_REQUIRED_FIELDS:
            errors.append("phase12r_audit_trail_index_reviewer_class_required_unknown_field")
        label = _safe_phase12r_reviewer_class(item.get("reviewer_class_label"))
        labels.append(label)
        if label != item.get("reviewer_class_label"):
            errors.append("phase12r_audit_trail_index_reviewer_class_required_label_invalid")
        expected = {
            "reviewer_class_status": PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
            "required": True,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12r_audit_trail_index_reviewer_class_required_value_invalid")
                break
    if labels != list(PHASE12R_REQUIRED_REVIEWER_CLASSES) or len(labels) != len(set(labels)):
        errors.append("phase12r_audit_trail_index_reviewer_class_required_order_invalid")
    return tuple(errors)


def _phase12r_reviewer_class_represented_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12r_audit_trail_index_reviewer_classes_represented_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12r_audit_trail_index_reviewer_class_represented_not_object")
            continue
        if PHASE12R_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS - set(item):
            errors.append("phase12r_audit_trail_index_reviewer_class_represented_field_missing")
        if set(str(key) for key in item) - PHASE12R_REVIEWER_CLASS_REPRESENTED_REQUIRED_FIELDS:
            errors.append("phase12r_audit_trail_index_reviewer_class_represented_unknown_field")
        label = _safe_phase12r_reviewer_class(item.get("reviewer_class_label"))
        labels.append(label)
        if label != item.get("reviewer_class_label"):
            errors.append("phase12r_audit_trail_index_reviewer_class_represented_label_invalid")
        expected = {
            "reviewer_class_status": PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
            "represented": False,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12r_audit_trail_index_reviewer_class_represented_value_invalid")
                break
    if labels != list(PHASE12R_REQUIRED_REVIEWER_CLASSES) or len(labels) != len(set(labels)):
        errors.append("phase12r_audit_trail_index_reviewer_class_represented_order_invalid")
    return tuple(errors)


def _phase12r_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12r_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12r_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        PHASE12R_SOURCE_PHASE_RANGE.lower(),
        PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        PHASE12R_AUTHORIZATION_STATUS,
        PHASE12R_GRANT_STATUS,
        PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        PHASE12R_SOURCE_REFERENCE_STATUS,
        PHASE12R_MODE_INDEX_STATUS,
        PHASE12R_PACKET_REFERENCE_STATUS,
        PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
        PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
        PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
        PHASE12R_STALE_STATUS,
        PHASE12R_REVIEW_NEEDED_STATUS,
        PHASE12R_STALE_REVIEW_NEEDED_STATUS,
        *PHASE12R_STATUS_LABELS,
        *PHASE12R_WORKFLOW_MODES,
        *PHASE12R_REQUIRED_FUTURE_GATES,
        *PHASE12R_REQUIRED_REVIEWER_CLASSES,
        *PHASE12Q_DECISION_STATUSES,
        *PHASE12Q_DECISION_REASON_CODES,
        *PHASE12Q_DECISION_STATUS_DISPOSITIONS.values(),
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        PHASE12R_DECISION_SUMMARY.lower(),
        PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT.lower(),
        PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    if lowered.startswith(
        (
            "p12n-workflow-mode-registry-profile-",
            "p12o-workflow-safety-gate-matrix-",
            "p12p-workflow-mode-review-packet-",
            "p12q-workflow-mode-review-decision-",
            "p12r-workflow-mode-review-audit-trail-index-",
        )
    ):
        return 0
    blocked_fragments = (
        "approval-for-runtime",
        "approval for runtime",
        "approved-for-runtime",
        "approved for runtime",
        "approval",
        "approved",
        "activation approved",
        "activation permitted",
        "activation enabled",
        "mode enablement",
        "enablement",
        "active grant",
        "grant created",
        "runtime authorization granted",
        "runtime enabled",
        "execution permission granted",
        "execution permitted true",
        "workflow execution",
        "workflow mode execution",
        "model routing",
        "provider execution",
        "model execution",
        "model loading",
        "training",
        "fine-tuning",
        "fine tuning",
        "code execution",
        "experiment execution",
        "autonomous experimentation",
        "shell execution",
        "process execution",
        "cache runtime",
        "event-bus runtime",
        "event bus runtime",
        "pub-sub runtime",
        "pubsub runtime",
        "web access",
        "database ingestion",
        "database write",
        "database writes",
        "query execution",
        "web scraping",
        "network call",
        "clinical use",
        "clinical decision support",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "device access",
        "sensor access",
        "raw sensor processing",
        "private health-data processing",
        "private health data processing",
        "production ready",
        "production readiness",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _phase12s_source_reference_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12s_closeout_summary_source_references_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    expected = (
        ("12N", PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND),
        ("12O", PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND),
        ("12P", PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND),
        ("12Q", PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND),
        ("12R", PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND),
    )
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12s_closeout_summary_source_reference_not_object")
            continue
        if PHASE12S_SOURCE_REFERENCE_REQUIRED_FIELDS - set(item):
            errors.append("phase12s_closeout_summary_source_reference_field_missing")
        if set(str(key) for key in item) - PHASE12S_SOURCE_REFERENCE_REQUIRED_FIELDS:
            errors.append("phase12s_closeout_summary_source_reference_unknown_field")
        label = str(item.get("source_phase_label") or "")
        labels.append(label)
        if label == "12N":
            if _safe_phase12n_profile_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12s_closeout_summary_source_reference_id_invalid")
        elif label == "12O":
            if _safe_phase12o_matrix_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12s_closeout_summary_source_reference_id_invalid")
        elif label == "12P":
            if _safe_phase12p_packet_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12s_closeout_summary_source_reference_id_invalid")
        elif label == "12Q":
            if _safe_phase12q_decision_record_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12s_closeout_summary_source_reference_id_invalid")
        elif label == "12R":
            if _safe_phase12r_audit_trail_index_id(item.get("source_reference_id")) != item.get(
                "source_reference_id"
            ):
                errors.append("phase12s_closeout_summary_source_reference_id_invalid")
        else:
            errors.append("phase12s_closeout_summary_source_reference_phase_invalid")
        expected_values = {
            "reference_status": PHASE12S_SOURCE_REFERENCE_STATUS,
            "metadata_only": True,
            "runtime_stage": REAL_MODE_PHASE_RUNTIME,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected_values.items():
            if item.get(key) != expected_value:
                errors.append("phase12s_closeout_summary_source_reference_value_invalid")
                break
    if labels != [phase for phase, _ in expected]:
        errors.append("phase12s_closeout_summary_source_reference_order_invalid")
    for item, (phase, kind) in zip(
        value if isinstance(value, list) else [], expected, strict=False
    ):
        if isinstance(item, Mapping) and (
            item.get("source_phase_label") != phase or item.get("source_kind") != kind
        ):
            errors.append("phase12s_closeout_summary_source_reference_kind_invalid")
            break
    return tuple(errors)


def _phase12s_status_label_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12s_closeout_summary_status_labels_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12s_closeout_summary_status_label_not_object")
            continue
        if PHASE12S_STATUS_LABEL_REQUIRED_FIELDS - set(item):
            errors.append("phase12s_closeout_summary_status_label_field_missing")
        if set(str(key) for key in item) - PHASE12S_STATUS_LABEL_REQUIRED_FIELDS:
            errors.append("phase12s_closeout_summary_status_label_unknown_field")
        label = _safe_phase12s_status_label(item.get("status_label"))
        labels.append(label)
        if label != item.get("status_label"):
            errors.append("phase12s_closeout_summary_status_label_invalid")
        expected = {
            "label_status": PHASE12S_SUMMARY_STATUS,
            "metadata_only": True,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12s_closeout_summary_status_label_value_invalid")
                break
    if labels != list(PHASE12S_STATUS_LABELS) or len(labels) != len(set(labels)):
        errors.append("phase12s_closeout_summary_status_label_order_invalid")
    return tuple(errors)


def _phase12s_workflow_mode_label_coverage_errors(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ("phase12s_closeout_summary_workflow_modes_invalid",)
    errors: list[str] = []
    labels: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            errors.append("phase12s_closeout_summary_workflow_mode_not_object")
            continue
        if PHASE12S_WORKFLOW_MODE_COVERAGE_REQUIRED_FIELDS - set(item):
            errors.append("phase12s_closeout_summary_workflow_mode_field_missing")
        if set(str(key) for key in item) - PHASE12S_WORKFLOW_MODE_COVERAGE_REQUIRED_FIELDS:
            errors.append("phase12s_closeout_summary_workflow_mode_unknown_field")
        label = _safe_phase12s_workflow_mode_label(item.get("workflow_mode_label"))
        labels.append(label)
        if label != item.get("workflow_mode_label"):
            errors.append("phase12s_closeout_summary_workflow_mode_label_invalid")
        expected = {
            "mode_coverage_status": PHASE12S_MODE_COVERAGE_STATUS,
            "metadata_only": True,
            "covered_for_closeout_only": True,
            "workflow_mode_activation_not_permitted": True,
            "workflow_execution_permitted": False,
            "workflow_mode_execution_permitted": False,
            "model_routing_execution_permitted": False,
            "provider_execution_granted": False,
            "code_execution_permitted": False,
            "shell_execution_permitted": False,
            "process_execution_permitted": False,
            "experiment_execution_permitted": False,
            "clinical_decision_support_allowed": False,
            "private_health_data_allowed": False,
            "execution_permitted": False,
            "real_mode_runtime_enabled": False,
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append("phase12s_closeout_summary_workflow_mode_value_invalid")
                break
    if labels != list(PHASE12S_WORKFLOW_MODES) or len(labels) != len(set(labels)):
        errors.append("phase12s_closeout_summary_workflow_mode_order_invalid")
    return tuple(errors)


def _phase12s_unsafe_semantics_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_phase12s_unsafe_semantics_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_phase12s_unsafe_semantics_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
        PHASE12S_SOURCE_PHASE_RANGE.lower(),
        PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        PHASE12S_AUTHORIZATION_STATUS,
        PHASE12S_GRANT_STATUS,
        PHASE12S_SUMMARY_STATUS,
        PHASE12S_SOURCE_REFERENCE_STATUS,
        PHASE12S_MODE_COVERAGE_STATUS,
        PHASE12S_REVIEW_CHAIN_STATUS,
        PHASE12S_REVIEWER_NAVIGATION_SUMMARY.lower(),
        PHASE12S_OPERATOR_HANDOFF_SUMMARY.lower(),
        *PHASE12S_CLOSEOUT_STATUSES,
        *PHASE12S_STATUS_LABELS,
        *PHASE12S_WORKFLOW_MODES,
        *PHASE12S_REQUIRED_FUTURE_GATES,
        *PHASE12S_REQUIRED_REVIEWER_CLASSES,
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT.lower(),
        PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in safe_values:
        return 0
    if lowered.startswith(
        (
            "p12n-workflow-mode-registry-profile-",
            "p12o-workflow-safety-gate-matrix-",
            "p12p-workflow-mode-review-packet-",
            "p12q-workflow-mode-review-decision-",
            "p12r-workflow-mode-review-audit-trail-index-",
            "p12s-workflow-mode-review-chain-closeout-summary-",
        )
    ):
        return 0
    blocked_fragments = (
        "approval-for-runtime",
        "approval for runtime",
        "approved-for-runtime",
        "approved for runtime",
        "approval",
        "approved",
        "activation approved",
        "activation permitted",
        "activation enabled",
        "mode enablement",
        "enablement",
        "active grant",
        "grant created",
        "runtime authorization granted",
        "runtime enabled",
        "execution permission granted",
        "execution permitted true",
        "workflow execution",
        "workflow mode execution",
        "model routing",
        "provider execution",
        "model execution",
        "model loading",
        "training",
        "fine-tuning",
        "fine tuning",
        "code execution",
        "shell execution",
        "process execution",
        "experiment execution",
        "autonomous experimentation",
        "web access",
        "network behavior",
        "database ingestion",
        "database write",
        "database writes",
        "query execution",
        "cache runtime",
        "event-bus runtime",
        "event bus runtime",
        "pub-sub runtime",
        "pubsub runtime",
        "transport implementation",
        "fabric implementation",
        "p2p implementation",
        "peer-to-peer",
        "bittorrent",
        "swarm",
        "public dht",
        "clinical use",
        "clinical decision support",
        "diagnosis",
        "treatment plan",
        "treatment planning",
        "medical advice",
        "dosing",
        "nutrition prescription",
        "device access",
        "sensor access",
        "raw sensor processing",
        "private health-data processing",
        "private health data processing",
        "deployment ready",
        "deployment readiness",
        "production ready",
        "production readiness",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered)


def _invalid_phase12a_charter_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12ARuntimeAuthorizationDesignCharterValidationResult:
    return Phase12ARuntimeAuthorizationDesignCharterValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12b_record_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12BRuntimeAuthorizationRecordCandidateValidationResult:
    return Phase12BRuntimeAuthorizationRecordCandidateValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12c_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12CVisualSupervisionCapabilityProfileValidationResult:
    return Phase12CVisualSupervisionCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12d_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12DConsentGateRequirementsValidationResult:
    return Phase12DConsentGateRequirementsValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12e_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12EPhysiologicalSensorCapabilityProfileValidationResult:
    return Phase12EPhysiologicalSensorCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12f_boundary_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12FSecureDropConsumerBoundaryValidationResult:
    return Phase12FSecureDropConsumerBoundaryValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12g_matrix_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12GProductionReadinessCoverageMatrixValidationResult:
    return Phase12GProductionReadinessCoverageMatrixValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12h_ownership_map_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult:
    return Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12i_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult:
    return Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12k_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult:
    return Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12l_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult:
    return Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12m_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult:
    return Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12n_profile_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult:
    return Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12o_matrix_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult:
    return Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12p_packet_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12PWorkflowModeActivationRequestReviewPacketValidationResult:
    return Phase12PWorkflowModeActivationRequestReviewPacketValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12q_decision_record_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12QWorkflowModeReviewDecisionRecordValidationResult:
    return Phase12QWorkflowModeReviewDecisionRecordValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12r_audit_trail_index_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12RWorkflowModeReviewAuditTrailIndexValidationResult:
    return Phase12RWorkflowModeReviewAuditTrailIndexValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _invalid_phase12s_closeout_summary_result(
    errors: tuple[str, ...],
    classification: str,
    sanitized_record: dict[str, object],
    *,
    privacy_violation_count: int = 0,
    authorization_wording_count: int = 0,
) -> Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult:
    return Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult(
        classification=classification,
        valid=False,
        errors=tuple(sorted(set(errors))),
        privacy_violation_count=privacy_violation_count,
        authorization_wording_count=authorization_wording_count,
        sanitized_record=sanitized_record,
    )


def _finalize_phase12a_runtime_authorization_design_charter(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["charter_id"] = None
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["charter_id"] = _phase12a_charter_id(payload)
    return payload


def _finalize_phase12b_runtime_authorization_record_candidate(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["record_id"] = None
    payload["phase12b_records_are_approvals_grants_or_permissions"] = False
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["record_id"] = _phase12b_record_id(payload)
    return payload


def _finalize_phase12c_visual_supervision_capability_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["phase12c_profiles_are_approvals_grants_or_permissions"] = False
    payload["visual_capture_execution_granted"] = False
    payload["clipboard_capture_execution_granted"] = False
    payload["mic_capture_execution_granted"] = False
    payload["camera_capture_execution_granted"] = False
    payload["click_automation_execution_granted"] = False
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12c_profile_id(payload)
    return payload


def _finalize_phase12d_visual_desktop_consent_gate_requirements(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["consent_gate_profile_id"] = None
    payload["phase12d_satisfies_consent_gates"] = False
    payload["phase12d_profiles_are_consents_approvals_grants_or_permissions"] = False
    payload["screen_capture_execution_granted"] = False
    payload["ocr_execution_granted"] = False
    payload["camera_capture_execution_granted"] = False
    payload["microphone_capture_execution_granted"] = False
    payload["clipboard_capture_execution_granted"] = False
    payload["recording_execution_granted"] = False
    payload["click_input_automation_execution_granted"] = False
    payload["overlay_display_execution_granted"] = False
    payload["notification_sending_execution_granted"] = False
    payload["network_call_execution_granted"] = False
    payload["runtime_adapter_execution_granted"] = False
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["consent_gate_profile_id"] = _phase12d_profile_id(payload)
    return payload


def _finalize_phase12e_physiological_sensor_capability_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["physiological_sensor_profile_id"] = None
    payload["phase12e_profiles_are_approvals_grants_or_permissions"] = False
    payload["phase12e_satisfies_sensor_gates"] = False
    payload["bia_measurement_execution_granted"] = False
    payload["device_connection_execution_granted"] = False
    payload["bluetooth_execution_granted"] = False
    payload["usb_execution_granted"] = False
    payload["cloud_sync_execution_granted"] = False
    payload["acoustic_processing_execution_granted"] = False
    payload["ultrasound_processing_execution_granted"] = False
    payload["medical_inference_execution_granted"] = False
    payload["clinical_recommendation_execution_granted"] = False
    payload["network_call_execution_granted"] = False
    payload["runtime_adapter_execution_granted"] = False
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["physiological_sensor_profile_id"] = _phase12e_profile_id(payload)
    return payload


def _finalize_phase12f_secure_drop_consumer_boundary(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["secure_drop_consumer_boundary_id"] = None
    payload["phase12f_implements_secure_drop"] = False
    payload["phase12f_authorizes_secure_drop"] = False
    payload["phase12f_profiles_are_approvals_grants_or_permissions"] = False
    payload["concealment_is_security_boundary"] = False
    payload["secure_drop_send_permitted"] = False
    payload["secure_drop_receive_permitted"] = False
    payload["agent_invocation_permitted"] = False
    payload["automation_invocation_permitted"] = False
    payload["connector_invocation_permitted"] = False
    payload["scheduled_task_invocation_permitted"] = False
    payload["avatar_invocation_permitted"] = False
    payload["server_endpoint_invocation_permitted"] = False
    payload["workflow_invocation_permitted"] = False
    payload["filesystem_autoscan_permitted"] = False
    payload["vault_env_secret_access_permitted"] = False
    payload["raw_sensor_capture_attachment_permitted"] = False
    payload["automatic_document_attachment_permitted"] = False
    payload["crypto_implementation_added"] = False
    payload["transport_implementation_added"] = False
    payload["stego_implementation_added"] = False
    payload["keyring_implementation_added"] = False
    payload["did_implementation_added"] = False
    payload["send_inbox_ui_added"] = False
    payload["network_call_execution_granted"] = False
    payload["runtime_adapter_execution_granted"] = False
    payload["adapter_execution_granted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["active_grant_present"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["secure_drop_consumer_boundary_id"] = _phase12f_boundary_id(payload)
    return payload


def _finalize_phase12g_production_readiness_coverage_matrix(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["production_readiness_matrix_id"] = None
    payload["phase12g_makes_somatic_production_ready"] = False
    payload["phase12g_authorizes_runtime"] = False
    payload["phase12g_coverage_labels_are_metadata_only"] = True
    payload["frontend_implementation_added"] = False
    payload["backend_service_added"] = False
    payload["production_api_service_added"] = False
    payload["database_storage_added"] = False
    payload["auth_runtime_added"] = False
    payload["rate_limiting_runtime_added"] = False
    payload["cache_runtime_added"] = False
    payload["cdn_runtime_added"] = False
    payload["load_balancer_runtime_added"] = False
    payload["logging_service_added"] = False
    payload["secrets_backend_runtime_added"] = False
    payload["service_registry_runtime_added"] = False
    payload["deployment_code_added"] = False
    payload["hosting_runtime_added"] = False
    payload["cloud_compute_runtime_added"] = False
    payload["network_call_execution_granted"] = False
    payload["runtime_adapter_execution_granted"] = False
    payload["device_connection_execution_granted"] = False
    payload["sensor_processing_execution_granted"] = False
    payload["secure_drop_send_permitted"] = False
    payload["secure_drop_receive_permitted"] = False
    payload["provider_execution_granted"] = False
    payload["model_execution_granted"] = False
    payload["active_grant_present"] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["production_readiness_matrix_id"] = _phase12g_matrix_id(payload)
    return payload


def _finalize_phase12h_standalone_ownership_matrix(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["standalone_ownership_matrix_id"] = None
    payload["phase12h_marks_somatic_production_ready"] = False
    payload["phase12h_authorizes_runtime"] = False
    payload["somatic_standalone_ownership_retained"] = True
    payload["external_integrations_optional"] = True
    payload["optional_peer_labels_are_integration_metadata_only"] = True
    payload["external_repo_integration_replaces_somatic_standalone_path"] = False
    payload["cross_repo_mutation_permitted"] = False
    payload["external_repo_tasks_executed_by_somatic"] = False
    payload["repo_production_ready_count"] = 0
    for field in _phase12h_runtime_false_fields():
        payload[field] = False
    payload["standalone_ownership_matrix_id"] = _phase12h_matrix_id(payload)
    return payload


def _phase12h_runtime_false_fields() -> tuple[str, ...]:
    return (
        "frontend_implementation_added",
        "backend_service_added",
        "production_api_service_added",
        "database_storage_added",
        "auth_runtime_added",
        "rate_limiting_runtime_added",
        "cache_runtime_added",
        "cdn_runtime_added",
        "load_balancer_runtime_added",
        "logging_service_added",
        "secrets_backend_runtime_added",
        "service_registry_runtime_added",
        "service_discovery_runtime_added",
        "deployment_code_added",
        "hosting_runtime_added",
        "cloud_compute_runtime_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "device_connection_execution_granted",
        "sensor_processing_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12i_knowledge_capability_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["medical_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_medical_safety_semantics"] = True
    payload["phase12i_provides_medical_advice"] = False
    payload["phase12i_authorizes_runtime"] = False
    payload["phase12i_suppresses_safety_warnings"] = False
    payload["phase12i_claims_western_medicine_invalid"] = False
    payload["phase12i_claims_natural_remedies_safe_by_default"] = False
    payload["phase12i_claims_food_cures_disease"] = False
    payload["emergency_escalation_preserved"] = True
    payload["contraindication_warnings_preserved"] = True
    payload["medication_interaction_warnings_preserved"] = True
    payload["pregnancy_liver_kidney_cardiac_risk_warnings_preserved"] = True
    payload["eating_disorder_risk_warnings_preserved"] = True
    payload["toxicity_warnings_preserved"] = True
    payload["contamination_adulteration_warnings_preserved"] = True
    for field in _phase12i_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12i_profile_id(payload)
    return payload


def _phase12i_runtime_false_fields() -> tuple[str, ...]:
    return (
        "medical_advice_provided",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "prescribing_added",
        "supplement_recommendation_added",
        "herb_dosing_added",
        "supplement_dosing_added",
        "calorie_macro_prescription_added",
        "weight_loss_target_prescription_added",
        "unsafe_fasting_weight_loss_advice_added",
        "nutrition_prescription_added",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "active_grant_present",
        "runtime_adapter_execution_granted",
        "real_mode_authorization_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12k_external_compute_quantum_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["credential_policy"] = PHASE12K_CREDENTIAL_POLICY
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["security_review_required"] = True
    payload["medical_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_medical_safety_semantics"] = True
    payload["human_approval_required"] = True
    payload["cost_guard_required"] = True
    payload["private_health_data_allowed"] = False
    payload["clinical_decision_support_allowed"] = False
    payload["diagnosis_or_treatment_allowed"] = False
    payload["phase12k_authorizes_runtime"] = False
    payload["phase12k_allows_external_compute_execution"] = False
    payload["phase12k_allows_quantum_backend_execution"] = False
    payload["phase12k_allows_private_health_data_processing"] = False
    payload["phase12k_provides_medical_advice"] = False
    payload["phase12k_allows_diagnosis_or_treatment"] = False
    for field in _phase12k_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12k_profile_id(payload)
    return payload


def _phase12k_runtime_false_fields() -> tuple[str, ...]:
    return (
        "api_call_execution_granted",
        "sdk_execution_granted",
        "simulator_execution_granted",
        "provider_call_execution_granted",
        "network_call_execution_granted",
        "spending_permitted",
        "credential_loading_added",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "external_compute_execution_granted",
        "quantum_backend_execution_granted",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "private_health_data_processing_added",
        "database_ingestion_added",
        "web_scraping_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12l_fabric_interop_a2a_audit_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["authorization_status"] = PHASE12L_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12L_GRANT_STATUS
    payload["fabric_interop_status"] = PHASE12L_FABRIC_INTEROP_STATUS
    payload["message_codec_status"] = PHASE12L_MESSAGE_CODEC_STATUS
    payload["a2a_transport_status"] = PHASE12L_A2A_TRANSPORT_STATUS
    payload["mcp_interop_status"] = PHASE12L_MCP_INTEROP_STATUS
    payload["secure_drop_status"] = PHASE12L_SECURE_DROP_STATUS
    payload["credential_policy"] = PHASE12L_CREDENTIAL_POLICY
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["security_review_required"] = True
    payload["fabric_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_fabric_safety_semantics"] = True
    payload["plaintext_json_default_future_requirement_only"] = True
    payload["decode_to_audit_future_requirement_only"] = True
    payload["secure_drop_user_initiated_boundary_only"] = True
    payload["opaque_traffic_allowed"] = False
    payload["untrusted_content_executable"] = False
    payload["cross_repo_mutation_allowed"] = False
    payload["phase12l_authorizes_runtime"] = False
    payload["phase12l_allows_fabric_runtime"] = False
    payload["phase12l_allows_a2a_transport"] = False
    payload["phase12l_allows_mcp_runtime"] = False
    payload["phase12l_allows_secure_drop_send_receive"] = False
    for field in _phase12l_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12l_profile_id(payload)
    return payload


def _phase12l_runtime_false_fields() -> tuple[str, ...]:
    return (
        "message_codec_implementation_added",
        "a2a_transport_implementation_added",
        "mcp_server_implementation_added",
        "mcp_client_implementation_added",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "crypto_implementation_added",
        "credential_loading_added",
        "vault_env_access_granted",
        "secrets_access_granted",
        "network_call_execution_granted",
        "filesystem_autoscan_added",
        "connector_installation_added",
        "pack_registration_added",
        "provider_execution_granted",
        "provider_call_execution_granted",
        "model_execution_granted",
        "runtime_model_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "agent_invoked_secure_drop_allowed",
        "automation_invoked_secure_drop_allowed",
        "bundled_agpl_codec_allowed",
        "glossopetrae_vendoring_allowed",
        "st3gg_vendoring_allowed",
        "covert_channel_allowed",
        "opaque_message_acting_allowed",
        "untrusted_content_execution_added",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12m_specialized_model_option_registry_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["authorization_status"] = PHASE12M_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12M_GRANT_STATUS
    payload["model_option_profile_phase"] = PHASE12M_MODEL_OPTION_PROFILE_PHASE
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["security_review_required"] = True
    payload["medical_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_model_safety_semantics"] = True
    payload["model_labels_selectable_metadata_only"] = True
    payload["phase12m_authorizes_runtime"] = False
    payload["phase12m_allows_model_execution"] = False
    payload["phase12m_allows_provider_execution"] = False
    payload["phase12m_allows_model_loading"] = False
    payload["phase12m_allows_training"] = False
    payload["phase12m_allows_fine_tuning"] = False
    payload["phase12m_allows_clinical_decision_support"] = False
    payload["phase12m_allows_diagnosis_or_treatment"] = False
    payload["phase12m_allows_private_health_data_processing"] = False
    payload["phase12m_allows_device_access"] = False
    payload["phase12m_allows_raw_sensor_processing"] = False
    payload["phase12m_provides_medical_advice"] = False
    payload["phase12m_provides_prescribing"] = False
    for field in _phase12m_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12m_profile_id(payload)
    return payload


def _phase12m_runtime_false_fields() -> tuple[str, ...]:
    return (
        "model_execution_permitted",
        "provider_execution_permitted",
        "training_permitted",
        "fine_tuning_permitted",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "private_health_data_allowed",
        "model_loading_added",
        "runtime_model_execution_granted",
        "provider_execution_granted",
        "model_execution_granted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "prescribing_added",
        "herb_dosing_added",
        "supplement_dosing_added",
        "calorie_macro_prescription_added",
        "nutrition_prescription_added",
        "private_health_data_processing_added",
        "device_access_granted",
        "device_connection_execution_granted",
        "raw_sensor_processing_added",
        "sensor_processing_execution_granted",
        "monitoring_added",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12n_workflow_orchestration_mode_registry_profile(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["profile_id"] = None
    payload["authorization_status"] = PHASE12N_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12N_GRANT_STATUS
    payload["workflow_mode_profile_phase"] = PHASE12N_WORKFLOW_MODE_PROFILE_PHASE
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["security_review_required"] = True
    payload["medical_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_workflow_safety_semantics"] = True
    payload["workflow_modes_metadata_only"] = True
    payload["phase12n_authorizes_runtime"] = False
    payload["phase12n_allows_workflow_mode_execution"] = False
    payload["phase12n_allows_runtime_orchestration"] = False
    payload["phase12n_allows_model_routing"] = False
    payload["phase12n_allows_provider_execution"] = False
    payload["phase12n_allows_model_execution"] = False
    payload["phase12n_allows_model_loading"] = False
    payload["phase12n_allows_training"] = False
    payload["phase12n_allows_fine_tuning"] = False
    payload["phase12n_allows_code_execution"] = False
    payload["phase12n_allows_experiment_execution"] = False
    payload["phase12n_allows_autonomous_experimentation"] = False
    payload["phase12n_allows_web_access"] = False
    payload["phase12n_allows_autonomous_publication"] = False
    payload["phase12n_allows_clinical_decision_support"] = False
    payload["phase12n_allows_diagnosis_or_treatment"] = False
    payload["phase12n_allows_private_health_data_processing"] = False
    payload["phase12n_allows_device_or_sensor_access"] = False
    payload["phase12n_provides_medical_advice"] = False
    for field in _phase12n_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["profile_id"] = _phase12n_profile_id(payload)
    return payload


def _phase12n_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_mode_execution_permitted",
        "autonomous_experimentation_permitted",
        "code_execution_permitted",
        "model_routing_execution_permitted",
        "clinical_decision_support_allowed",
        "diagnosis_or_treatment_allowed",
        "private_health_data_allowed",
        "runtime_orchestration_added",
        "fusion_coordination_execution_granted",
        "learned_coordination_execution_granted",
        "agent_routing_execution_granted",
        "provider_call_execution_granted",
        "provider_execution_granted",
        "model_loading_added",
        "runtime_model_execution_granted",
        "model_execution_granted",
        "training_permitted",
        "fine_tuning_permitted",
        "training_execution_granted",
        "fine_tuning_execution_granted",
        "model_training_execution_granted",
        "model_fine_tuning_execution_granted",
        "experiment_execution_permitted",
        "experiment_execution_granted",
        "web_access_permitted",
        "literature_search_execution_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "runtime_adapter_execution_granted",
        "active_grant_present",
        "real_mode_authorization_added",
        "clinical_decision_support_added",
        "clinical_recommendation_added",
        "medical_advice_provided",
        "diagnosis_provided",
        "treatment_plan_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "device_access_granted",
        "device_connection_execution_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "sensor_processing_execution_granted",
        "private_health_data_processing_added",
        "manuscript_generation_added",
        "autonomous_publication_allowed",
        "autonomous_research_action_permitted",
        "command_execution_granted",
        "connector_grant_present",
        "fabric_transfer_execution_granted",
        "ws_stream_execution_granted",
        "http_execution_granted",
        "mcp_tool_exposure_added",
        "task_execution_granted",
        "secure_drop_send_permitted",
        "secure_drop_receive_permitted",
        "service_discovery_runtime_added",
        "schedule_enforcement_added",
        "filesystem_access_granted",
        "process_control_granted",
        "db_storage_write_added",
        "secrets_access_granted",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12o_workflow_mode_safety_gate_matrix(
    payload: dict[str, object],
) -> dict[str, object]:
    payload["matrix_id"] = None
    payload["authorization_status"] = PHASE12O_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12O_GRANT_STATUS
    payload["matrix_phase"] = PHASE12O_MATRIX_PHASE
    payload["metadata_only"] = True
    payload["non_authorizing_proof"] = True
    payload["standalone_first"] = True
    payload["security_review_required"] = True
    payload["medical_safety_review_required"] = True
    payload["jules_human_review_required_for_validator_or_workflow_safety_semantics"] = True
    payload["workflow_mode_safety_gates_metadata_only"] = True
    payload["phase12o_authorizes_runtime"] = False
    payload["phase12o_satisfies_runtime_prerequisites"] = False
    payload["phase12o_allows_workflow_execution"] = False
    payload["phase12o_allows_workflow_mode_execution"] = False
    payload["phase12o_allows_runtime_adapter"] = False
    payload["phase12o_allows_model_routing"] = False
    payload["phase12o_allows_provider_execution"] = False
    payload["phase12o_allows_model_execution"] = False
    payload["phase12o_allows_code_execution"] = False
    payload["phase12o_allows_experiment_execution"] = False
    payload["phase12o_allows_web_database_network_behavior"] = False
    payload["phase12o_allows_clinical_decision_support"] = False
    payload["phase12o_allows_private_health_data_processing"] = False
    payload["phase12o_active_grant_present"] = False
    for field in _phase12o_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["matrix_id"] = _phase12o_matrix_id(payload)
    return payload


def _phase12o_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "runtime_prerequisite_satisfied",
        "all_prerequisites_satisfied",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "active_grant_present",
        "real_mode_authorization_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "device_access_granted",
        "raw_sensor_processing_added",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12p_review_packet(payload: dict[str, object]) -> dict[str, object]:
    payload["activation_request_packet_id"] = None
    payload["authorization_status"] = PHASE12P_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12P_GRANT_STATUS
    payload["packet_phase"] = PHASE12P_PACKET_PHASE
    payload["requested_transition_status"] = PHASE12P_REQUESTED_TRANSITION_STATUS
    payload["metadata_only"] = True
    payload["review_packet_boundary_only"] = True
    payload["standalone_first"] = True
    payload["non_authorizing_proof"] = True
    payload["not_authorized"] = True
    payload["human_review_required"] = True
    payload["jules_review_required"] = True
    payload["security_review_required"] = True
    payload["medical_safety_review_required"] = True
    payload["human_jules_security_medical_safety_review_required"] = True
    payload["all_future_gates_unsatisfied"] = True
    payload["denial_blocked_default_fail_closed"] = True
    payload["denial_blocked_default_fail_closed_status"] = PHASE12P_DENIAL_BLOCKED_STATUS
    payload["no_active_grant"] = True
    payload["no_runtime_authorization"] = True
    payload["no_execution_permission"] = True
    payload["workflow_mode_activation_not_permitted"] = True
    payload["workflow_mode_activation_not_permitted_status"] = (
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS
    )
    payload["phase12p_authorizes_runtime"] = False
    payload["phase12p_creates_active_grant"] = False
    payload["phase12p_grants_execution_permission"] = False
    payload["phase12p_allows_workflow_execution"] = False
    payload["phase12p_allows_workflow_mode_execution"] = False
    payload["phase12p_allows_runtime_adapter"] = False
    payload["phase12p_allows_model_routing"] = False
    payload["phase12p_allows_provider_execution"] = False
    payload["phase12p_allows_model_execution"] = False
    payload["phase12p_allows_model_loading"] = False
    payload["phase12p_allows_training"] = False
    payload["phase12p_allows_fine_tuning"] = False
    payload["phase12p_allows_code_execution"] = False
    payload["phase12p_allows_experiment_execution"] = False
    payload["phase12p_allows_autonomous_experimentation"] = False
    payload["phase12p_allows_web_access"] = False
    payload["phase12p_allows_database_ingestion"] = False
    payload["phase12p_allows_web_scraping"] = False
    payload["phase12p_allows_network_calls"] = False
    payload["phase12p_allows_clinical_decision_support"] = False
    payload["phase12p_allows_diagnosis_or_treatment"] = False
    payload["phase12p_allows_medical_advice"] = False
    payload["phase12p_allows_dosing_or_nutrition_prescription"] = False
    payload["phase12p_allows_private_health_data_processing"] = False
    payload["phase12p_allows_device_or_sensor_access"] = False
    payload["phase12p_allows_raw_sensor_processing"] = False
    payload["phase12p_marks_production_ready"] = False
    for field in _phase12p_runtime_false_fields():
        payload[field] = False
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["activation_request_packet_id"] = _phase12p_packet_id(payload)
    return payload


def _phase12p_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12q_decision_record(payload: dict[str, object]) -> dict[str, object]:
    payload["decision_record_id"] = None
    decision_status = (
        _safe_phase12q_decision_status(payload.get("decision_status"))
        or PHASE12Q_DEFAULT_DECISION_STATUS
    )
    payload["decision_status"] = decision_status
    payload["decision_reason_code"] = PHASE12Q_DECISION_STATUS_REASON_CODES[decision_status]
    payload["request_disposition_status"] = PHASE12Q_DECISION_STATUS_DISPOSITIONS[decision_status]
    payload["authorization_status"] = PHASE12Q_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12Q_GRANT_STATUS
    payload["decision_record_phase"] = PHASE12Q_DECISION_RECORD_PHASE
    payload["decision_record_status"] = PHASE12Q_DECISION_RECORD_STATUS
    payload["decision_summary"] = PHASE12Q_DECISION_SUMMARY
    payload["decision_boundary_statement"] = PHASE12Q_DECISION_BOUNDARY_STATEMENT
    payload["medical_privacy_boundary_statement"] = PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT
    payload["metadata_only"] = True
    payload["review_decision_record_only"] = True
    payload["standalone_first"] = True
    payload["non_authorizing_proof"] = True
    payload["not_authorized"] = True
    for field, value in _phase12q_decision_status_flags(decision_status).items():
        payload[field] = value
    payload["no_active_grant"] = True
    payload["no_runtime_authorization"] = True
    payload["no_execution_permission"] = True
    payload["runtime_authorization_not_granted"] = True
    payload["workflow_mode_activation_not_permitted"] = True
    payload["workflow_mode_activation_not_permitted_status"] = (
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS
    )
    payload["phase12q_authorizes_runtime"] = False
    payload["phase12q_creates_active_grant"] = False
    payload["phase12q_grants_execution_permission"] = False
    payload["phase12q_allows_workflow_activation"] = False
    payload["phase12q_allows_workflow_execution"] = False
    payload["phase12q_allows_workflow_mode_execution"] = False
    payload["phase12q_allows_runtime_adapter"] = False
    payload["phase12q_allows_model_routing"] = False
    payload["phase12q_allows_provider_execution"] = False
    payload["phase12q_allows_model_execution"] = False
    payload["phase12q_allows_model_loading"] = False
    payload["phase12q_allows_training"] = False
    payload["phase12q_allows_fine_tuning"] = False
    payload["phase12q_allows_code_execution"] = False
    payload["phase12q_allows_experiment_execution"] = False
    payload["phase12q_allows_autonomous_experimentation"] = False
    payload["phase12q_allows_web_access"] = False
    payload["phase12q_allows_database_ingestion"] = False
    payload["phase12q_allows_web_scraping"] = False
    payload["phase12q_allows_network_calls"] = False
    payload["phase12q_allows_clinical_decision_support"] = False
    payload["phase12q_allows_diagnosis_or_treatment"] = False
    payload["phase12q_allows_medical_advice"] = False
    payload["phase12q_allows_dosing_or_nutrition_prescription"] = False
    payload["phase12q_allows_private_health_data_processing"] = False
    payload["phase12q_allows_device_or_sensor_access"] = False
    payload["phase12q_allows_raw_sensor_processing"] = False
    payload["phase12q_marks_production_ready"] = False
    for field in _phase12q_runtime_false_fields():
        payload[field] = False
    payload["runtime_stage"] = REAL_MODE_PHASE_RUNTIME
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["decision_record_id"] = _phase12q_decision_record_id(payload)
    return payload


def _phase12q_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12r_audit_trail_index(payload: dict[str, object]) -> dict[str, object]:
    payload["audit_trail_index_id"] = None
    decision_status = (
        _safe_phase12q_decision_status(payload.get("decision_status"))
        or PHASE12Q_DEFAULT_DECISION_STATUS
    )
    payload["decision_status"] = decision_status
    payload["decision_reason_code"] = PHASE12Q_DECISION_STATUS_REASON_CODES[decision_status]
    payload["request_disposition_status"] = PHASE12Q_DECISION_STATUS_DISPOSITIONS[decision_status]
    payload["authorization_status"] = PHASE12R_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12R_GRANT_STATUS
    payload["audit_trail_index_phase"] = PHASE12R_AUDIT_TRAIL_INDEX_PHASE
    payload["audit_trail_index_status"] = PHASE12R_AUDIT_TRAIL_INDEX_STATUS
    payload["stale_status"] = PHASE12R_STALE_STATUS
    payload["review_needed_status"] = PHASE12R_REVIEW_NEEDED_STATUS
    payload["stale_review_needed_status"] = PHASE12R_STALE_REVIEW_NEEDED_STATUS
    payload["audit_trail_boundary_statement"] = PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT
    payload["medical_privacy_boundary_statement"] = PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT
    payload["metadata_only"] = True
    payload["workflow_mode_review_audit_trail_index_only"] = True
    payload["standalone_first"] = True
    payload["non_authorizing_proof"] = True
    payload["not_authorized"] = True
    payload["no_active_grant"] = True
    payload["no_runtime_authorization"] = True
    payload["no_execution_permission"] = True
    payload["runtime_authorization_not_granted"] = True
    payload["workflow_mode_activation_not_permitted"] = True
    payload["phase12r_authorizes_runtime"] = False
    payload["phase12r_creates_active_grant"] = False
    payload["phase12r_grants_execution_permission"] = False
    payload["phase12r_allows_workflow_activation"] = False
    payload["phase12r_allows_workflow_execution"] = False
    payload["phase12r_allows_workflow_mode_execution"] = False
    payload["phase12r_allows_runtime_adapter"] = False
    payload["phase12r_allows_model_routing"] = False
    payload["phase12r_allows_provider_execution"] = False
    payload["phase12r_allows_model_execution"] = False
    payload["phase12r_allows_model_loading"] = False
    payload["phase12r_allows_training"] = False
    payload["phase12r_allows_fine_tuning"] = False
    payload["phase12r_allows_code_execution"] = False
    payload["phase12r_allows_experiment_execution"] = False
    payload["phase12r_allows_autonomous_experimentation"] = False
    payload["phase12r_allows_shell_execution"] = False
    payload["phase12r_allows_process_execution"] = False
    payload["phase12r_allows_cache_event_bus_pubsub_runtime"] = False
    payload["phase12r_allows_web_access"] = False
    payload["phase12r_allows_database_ingestion"] = False
    payload["phase12r_allows_database_writes"] = False
    payload["phase12r_allows_query_execution"] = False
    payload["phase12r_allows_web_scraping"] = False
    payload["phase12r_allows_network_calls"] = False
    payload["phase12r_allows_clinical_decision_support"] = False
    payload["phase12r_allows_diagnosis_or_treatment"] = False
    payload["phase12r_allows_medical_advice"] = False
    payload["phase12r_allows_dosing_or_nutrition_prescription"] = False
    payload["phase12r_allows_private_health_data_processing"] = False
    payload["phase12r_allows_device_or_sensor_access"] = False
    payload["phase12r_allows_raw_sensor_processing"] = False
    payload["phase12r_marks_production_ready"] = False
    for field in _phase12r_runtime_false_fields():
        payload[field] = False
    payload["runtime_stage"] = REAL_MODE_PHASE_RUNTIME
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["audit_trail_index_id"] = _phase12r_audit_trail_index_id(payload)
    return payload


def _phase12r_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "shell_execution_permitted",
        "process_execution_permitted",
        "web_access_permitted",
        "database_ingestion_added",
        "database_write_permitted",
        "query_execution_permitted",
        "cache_event_bus_runtime_added",
        "pubsub_runtime_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _finalize_phase12s_closeout_summary(payload: dict[str, object]) -> dict[str, object]:
    payload["closeout_summary_id"] = None
    closeout_status = (
        _safe_phase12s_closeout_status(payload.get("closeout_status"))
        or PHASE12S_DEFAULT_CLOSEOUT_STATUS
    )
    payload["closeout_status"] = closeout_status
    payload["authorization_status"] = PHASE12S_AUTHORIZATION_STATUS
    payload["grant_status"] = PHASE12S_GRANT_STATUS
    payload["closeout_summary_phase"] = PHASE12S_CLOSEOUT_SUMMARY_PHASE
    payload["summary_status"] = PHASE12S_SUMMARY_STATUS
    payload["review_chain_status"] = PHASE12S_REVIEW_CHAIN_STATUS
    payload["reviewer_navigation_summary"] = PHASE12S_REVIEWER_NAVIGATION_SUMMARY
    payload["operator_handoff_summary"] = PHASE12S_OPERATOR_HANDOFF_SUMMARY
    payload["closeout_boundary_statement"] = PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT
    payload["medical_privacy_boundary_statement"] = PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT
    payload["metadata_only"] = True
    payload["workflow_mode_review_chain_closeout_summary_only"] = True
    payload["standalone_first"] = True
    payload["non_authorizing_proof"] = True
    payload["not_authorized"] = True
    payload["no_active_grant"] = True
    payload["no_runtime_authorization"] = True
    payload["no_execution_permission"] = True
    payload["runtime_authorization_not_granted"] = True
    payload["workflow_mode_activation_not_permitted"] = True
    payload["phase12s_authorizes_runtime"] = False
    payload["phase12s_creates_active_grant"] = False
    payload["phase12s_grants_execution_permission"] = False
    payload["phase12s_allows_workflow_activation"] = False
    payload["phase12s_allows_workflow_execution"] = False
    payload["phase12s_allows_workflow_mode_execution"] = False
    payload["phase12s_allows_runtime_adapter"] = False
    payload["phase12s_allows_model_routing"] = False
    payload["phase12s_allows_provider_execution"] = False
    payload["phase12s_allows_model_execution"] = False
    payload["phase12s_allows_model_loading"] = False
    payload["phase12s_allows_training"] = False
    payload["phase12s_allows_fine_tuning"] = False
    payload["phase12s_allows_code_execution"] = False
    payload["phase12s_allows_shell_execution"] = False
    payload["phase12s_allows_process_execution"] = False
    payload["phase12s_allows_experiment_execution"] = False
    payload["phase12s_allows_autonomous_experimentation"] = False
    payload["phase12s_allows_web_access"] = False
    payload["phase12s_allows_network_behavior"] = False
    payload["phase12s_allows_database_ingestion"] = False
    payload["phase12s_allows_database_writes"] = False
    payload["phase12s_allows_query_execution"] = False
    payload["phase12s_allows_cache_event_bus_pubsub_runtime"] = False
    payload["phase12s_allows_transport_implementation"] = False
    payload["phase12s_allows_fabric_implementation"] = False
    payload["phase12s_allows_p2p_implementation"] = False
    payload["phase12s_allows_clinical_decision_support"] = False
    payload["phase12s_allows_diagnosis_or_treatment"] = False
    payload["phase12s_allows_medical_advice"] = False
    payload["phase12s_allows_dosing_or_nutrition_prescription"] = False
    payload["phase12s_allows_private_health_data_processing"] = False
    payload["phase12s_allows_device_or_sensor_access"] = False
    payload["phase12s_allows_raw_sensor_processing"] = False
    payload["phase12s_marks_deployment_ready"] = False
    payload["phase12s_marks_production_ready"] = False
    for field in _phase12s_runtime_false_fields():
        payload[field] = False
    payload["runtime_stage"] = REAL_MODE_PHASE_RUNTIME
    payload["execution_permitted"] = False
    payload["real_mode_runtime_enabled"] = False
    payload["closeout_summary_id"] = _phase12s_closeout_summary_id(payload)
    return payload


def _phase12s_runtime_false_fields() -> tuple[str, ...]:
    return (
        "workflow_execution_permitted",
        "workflow_mode_execution_permitted",
        "workflow_mode_activation_permitted",
        "runtime_adapter_execution_granted",
        "model_routing_execution_permitted",
        "provider_execution_granted",
        "model_execution_granted",
        "model_loading_added",
        "training_permitted",
        "fine_tuning_permitted",
        "code_execution_permitted",
        "shell_execution_permitted",
        "process_execution_permitted",
        "experiment_execution_permitted",
        "autonomous_experimentation_permitted",
        "web_access_permitted",
        "network_behavior_added",
        "database_ingestion_added",
        "database_write_permitted",
        "query_execution_permitted",
        "cache_event_bus_runtime_added",
        "pubsub_runtime_added",
        "transport_implementation_added",
        "fabric_implementation_added",
        "p2p_implementation_added",
        "web_scraping_added",
        "network_call_execution_granted",
        "clinical_decision_support_allowed",
        "clinical_decision_support_added",
        "diagnosis_provided",
        "treatment_plan_provided",
        "medical_advice_provided",
        "dosing_added",
        "nutrition_prescription_added",
        "private_health_data_allowed",
        "private_health_data_processing_added",
        "device_access_granted",
        "sensor_access_granted",
        "raw_sensor_processing_added",
        "active_grant_present",
        "runtime_authorization_granted",
        "real_mode_authorization_added",
        "approval_for_runtime_present",
        "deployment_ready",
        "production_ready",
        "execution_permitted",
        "real_mode_runtime_enabled",
    )


def _phase12a_charter_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "charter_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12a-charter-{fingerprint[:16]}"


def _phase12b_record_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "record_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12b-record-{fingerprint[:16]}"


def _phase12c_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12c-profile-{fingerprint[:16]}"


def _phase12d_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "consent_gate_profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12d-consent-profile-{fingerprint[:16]}"


def _phase12e_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "physiological_sensor_profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12e-sensor-profile-{fingerprint[:16]}"


def _phase12f_boundary_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "secure_drop_consumer_boundary_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12f-secure-drop-boundary-{fingerprint[:16]}"


def _phase12g_matrix_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "production_readiness_matrix_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12g-production-matrix-{fingerprint[:16]}"


def _phase12h_matrix_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "standalone_ownership_matrix_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12h-standalone-ownership-{fingerprint[:16]}"


def _phase12i_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12i-integrative-profile-{fingerprint[:16]}"


def _phase12k_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12k-compute-quantum-profile-{fingerprint[:16]}"


def _phase12l_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12l-fabric-a2a-audit-profile-{fingerprint[:16]}"


def _phase12m_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12m-model-option-registry-profile-{fingerprint[:16]}"


def _phase12n_profile_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "profile_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12n-workflow-mode-registry-profile-{fingerprint[:16]}"


def _phase12o_matrix_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "matrix_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12o-workflow-safety-gate-matrix-{fingerprint[:16]}"


def _phase12p_packet_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "activation_request_packet_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12p-workflow-mode-review-packet-{fingerprint[:16]}"


def _phase12q_decision_record_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "decision_record_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12q-workflow-mode-review-decision-{fingerprint[:16]}"


def _phase12r_audit_trail_index_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "audit_trail_index_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12r-workflow-mode-review-audit-trail-index-{fingerprint[:16]}"


def _phase12s_closeout_summary_id(value: Mapping[str, object]) -> str:
    fingerprint = _payload_sha256({**dict(value), "closeout_summary_id": None})
    if not _looks_sha256(fingerprint):
        return ""
    return f"p12s-workflow-mode-review-chain-closeout-summary-{fingerprint[:16]}"


def _payload_sha256(value: object) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return ""
    return sha256(encoded).hexdigest()


def _safe_phase12a_charter_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12a-charter-") and _privacy_violation_count(text) == 0:
        return text
    return "p12a-charter-redacted"


def _safe_phase12b_record_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12b-record-") and _privacy_violation_count(text) == 0:
        return text
    return "p12b-record-redacted"


def _safe_phase12c_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12c-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12c-profile-redacted"


def _safe_phase12d_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12d-consent-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12d-consent-profile-redacted"


def _safe_phase12e_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12e-sensor-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12e-sensor-profile-redacted"


def _safe_phase12f_boundary_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12f-secure-drop-boundary-") and _privacy_violation_count(text) == 0:
        return text
    return "p12f-secure-drop-boundary-redacted"


def _safe_phase12g_matrix_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12g-production-matrix-") and _privacy_violation_count(text) == 0:
        return text
    return "p12g-production-matrix-redacted"


def _safe_gate_id(value: object) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    safe = "".join(char if char.isalnum() or char == "-" else "-" for char in text)
    return "-".join(part for part in safe.split("-") if part)


def _safe_domain_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12B_REQUESTED_DOMAINS else ""


def _safe_reviewer_role(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12B_REQUIRED_REVIEWER_ROLES else ""


def _safe_capability_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12C_ALLOWED_CAPABILITY_LABELS else ""


def _safe_phase12d_capability_category(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12D_CAPABILITY_CATEGORIES else ""


def _safe_phase12d_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12D_REQUIRED_FUTURE_GATES else ""


def _safe_phase12e_sensor_capability_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12E_SENSOR_CAPABILITY_LABELS else ""


def _safe_phase12e_non_diagnostic_boundary(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12E_NON_DIAGNOSTIC_BOUNDARIES else ""


def _safe_phase12e_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12E_REQUIRED_FUTURE_GATES else ""


def _safe_phase12f_allowed_artifact_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS else ""


def _safe_phase12f_prohibited_source(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES else ""


def _safe_phase12g_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12G_STATUS_LABELS else ""


def _safe_phase12g_area_id(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in (area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS) else ""


def _safe_phase12h_matrix_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12h-standalone-ownership-") and _privacy_violation_count(text) == 0:
        return text
    return "p12h-standalone-ownership-redacted"


def _safe_phase12h_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12H_STATUS_LABELS else ""


def _safe_phase12h_area_id(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in (area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS) else ""


def _safe_phase12h_peer_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12H_OPTIONAL_INTEGRATION_PEERS else ""


def _safe_phase12h_integration_role(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12H_OPTIONAL_INTEGRATION_ROLES else ""


def _safe_phase12i_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12i-integrative-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12i-integrative-profile-redacted"


def _safe_phase12i_source_reference_id(value: object, prefix: str) -> str:
    text = _safe_gate_id(value)
    if text.startswith(prefix) and _privacy_violation_count(text) == 0:
        return text
    return f"{prefix}redacted"


def _safe_phase12i_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12I_STATUS_LABELS else ""


def _safe_phase12i_user_preference_mode(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12I_USER_PREFERENCE_MODES else ""


def _safe_phase12i_specialist_profile_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12I_SPECIALIST_PROFILE_LABELS else ""


def _safe_phase12i_source_class_label(value: object) -> str:
    label = str(value or "").strip().lower()
    return label if label in PHASE12I_SOURCE_CLASS_LABELS else ""


def _safe_phase12i_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12I_REQUIRED_FUTURE_GATES else ""


def _safe_phase12k_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12k-compute-quantum-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12k-compute-quantum-profile-redacted"


def _safe_phase12k_source_reference_id(value: object, prefix: str) -> str:
    text = _safe_gate_id(value)
    if text.startswith(prefix) and _privacy_violation_count(text) == 0:
        return text
    return f"{prefix}redacted"


def _safe_phase12k_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12K_STATUS_LABELS else ""


def _safe_phase12k_backend_option_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12K_BACKEND_OPTION_LABELS else ""


def _safe_phase12k_workload_class_label(value: object) -> str:
    label = str(value or "").strip().lower()
    for canonical in PHASE12K_WORKLOAD_CLASSES:
        if label == canonical.lower():
            return canonical
    return ""


def _safe_phase12k_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12K_REQUIRED_FUTURE_GATES else ""


def _safe_phase12l_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12l-fabric-a2a-audit-profile-") and _privacy_violation_count(text) == 0:
        return text
    return "p12l-fabric-a2a-audit-profile-redacted"


def _safe_phase12l_source_reference_id(value: object, prefix: str) -> str:
    text = _safe_gate_id(value)
    if text.startswith(prefix) and _privacy_violation_count(text) == 0:
        return text
    return f"{prefix}redacted"


def _safe_phase12l_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12L_STATUS_LABELS else ""


def _safe_phase12l_fabric_capability_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12L_FABRIC_CAPABILITY_LABELS else ""


def _safe_phase12l_forbidden_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS else ""


def _safe_phase12l_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12L_REQUIRED_FUTURE_GATES else ""


def _safe_phase12m_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if (
        text.startswith("p12m-model-option-registry-profile-")
        and _privacy_violation_count(text) == 0
    ):
        return text
    return "p12m-model-option-registry-profile-redacted"


def _safe_phase12m_source_reference_id(value: object, prefix: str) -> str:
    text = _safe_gate_id(value)
    if text.startswith(prefix) and _privacy_violation_count(text) == 0:
        return text
    return f"{prefix}redacted"


def _safe_phase12m_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12M_STATUS_LABELS else ""


def _safe_phase12m_model_option_category_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12M_MODEL_OPTION_CATEGORIES else ""


def _safe_phase12m_candidate_label(value: object) -> str:
    label = str(value or "").strip().lower()
    for canonical in PHASE12M_CANDIDATE_LABELS:
        if label == canonical.lower():
            return canonical
    return ""


def _safe_phase12m_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12M_REQUIRED_FUTURE_GATES else ""


def _safe_phase12n_profile_id(value: object) -> str:
    text = _safe_gate_id(value)
    if (
        text.startswith("p12n-workflow-mode-registry-profile-")
        and _privacy_violation_count(text) == 0
    ):
        return text
    return "p12n-workflow-mode-registry-profile-redacted"


def _safe_phase12n_source_reference_id(value: object, prefix: str) -> str:
    text = _safe_gate_id(value)
    if text.startswith(prefix) and _privacy_violation_count(text) == 0:
        return text
    return f"{prefix}redacted"


def _safe_phase12n_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12N_STATUS_LABELS else ""


def _safe_phase12n_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in (mode[0] for mode in PHASE12N_WORKFLOW_MODES) else ""


def _safe_phase12n_fusion_concept_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12N_FUSION_CONCEPT_LABELS else ""


def _safe_phase12n_scientist_evolution_concept_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS else ""


def _safe_phase12n_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12N_REQUIRED_FUTURE_GATES else ""


def _safe_phase12o_matrix_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12o-workflow-safety-gate-matrix-") and _privacy_violation_count(text) == 0:
        return text
    return "p12o-workflow-safety-gate-matrix-redacted"


def _safe_phase12o_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12O_STATUS_LABELS else ""


def _safe_phase12o_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12O_WORKFLOW_MODES else ""


def _safe_phase12o_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12O_REQUIRED_FUTURE_GATES else ""


def _safe_phase12p_packet_id(value: object) -> str:
    text = _safe_gate_id(value)
    if text.startswith("p12p-workflow-mode-review-packet-") and _privacy_violation_count(text) == 0:
        return text
    return "p12p-workflow-mode-review-packet-redacted"


def _safe_phase12p_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_STATUS_LABELS else ""


def _safe_phase12p_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_WORKFLOW_MODES else ""


def _safe_phase12p_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_REQUIRED_FUTURE_GATES else ""


def _safe_phase12p_reviewer_class(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_REQUIRED_REVIEWER_CLASSES else ""


def _safe_phase12p_risk_placeholder(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_RISK_SUMMARY_PLACEHOLDERS else ""


def _safe_phase12p_evidence_placeholder(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS else ""


def _safe_phase12q_decision_record_id(value: object) -> str:
    text = _safe_gate_id(value)
    if (
        text.startswith("p12q-workflow-mode-review-decision-")
        and _privacy_violation_count(text) == 0
    ):
        return text
    return "p12q-workflow-mode-review-decision-redacted"


def _safe_phase12q_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_STATUS_LABELS else ""


def _safe_phase12q_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_WORKFLOW_MODES else ""


def _safe_phase12q_future_gate(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_REQUIRED_FUTURE_GATES else ""


def _safe_phase12q_reviewer_class(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_REQUIRED_REVIEWER_CLASSES else ""


def _safe_phase12q_decision_status(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_DECISION_STATUSES else ""


def _safe_phase12q_decision_reason_code(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_DECISION_REASON_CODES else ""


def _safe_phase12q_request_disposition_status(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12Q_DECISION_STATUS_DISPOSITIONS.values() else ""


def _safe_phase12r_audit_trail_index_id(value: object) -> str:
    text = _safe_gate_id(value)
    if (
        text.startswith("p12r-workflow-mode-review-audit-trail-index-")
        and _privacy_violation_count(text) == 0
    ):
        return text
    return "p12r-workflow-mode-review-audit-trail-index-redacted"


def _safe_phase12r_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12R_STATUS_LABELS else ""


def _safe_phase12r_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12R_WORKFLOW_MODES else ""


def _safe_phase12r_reviewer_class(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12R_REQUIRED_REVIEWER_CLASSES else ""


def _safe_phase12s_closeout_summary_id(value: object) -> str:
    text = _safe_gate_id(value)
    if (
        text.startswith("p12s-workflow-mode-review-chain-closeout-summary-")
        and _privacy_violation_count(text) == 0
    ):
        return text
    return "p12s-workflow-mode-review-chain-closeout-summary-redacted"


def _safe_phase12s_status_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12S_STATUS_LABELS else ""


def _safe_phase12s_workflow_mode_label(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12S_WORKFLOW_MODES else ""


def _safe_phase12s_closeout_status(value: object) -> str:
    label = _safe_gate_id(value)
    return label if label in PHASE12S_CLOSEOUT_STATUSES else ""


def _is_non_negative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _safe_int(value: object) -> int:
    return value if _is_non_negative_int(value) else 0


def _looks_sha256(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def _privacy_violation_count(value: object) -> int:
    if isinstance(value, Mapping):
        violations = 0
        for key, item in value.items():
            if _unsafe_key(key):
                violations += 1
            violations += _privacy_violation_count(item)
        return violations
    if isinstance(value, list):
        return sum(_privacy_violation_count(item) for item in value)
    if isinstance(value, str):
        return _unsafe_string_count(value)
    return 0


def _unsafe_key(key: object) -> bool:
    text = str(key or "").lower()
    normalized = text.replace("-", "_").replace(" ", "_")
    allowed = {
        "vault_env_secret_access_permitted",
        "keyring_implementation_added",
        "did_implementation_added",
        "prohibited_future_autonomous_sources",
        "prohibited_future_autonomous_source_count",
        "source_content_fabric_secure_drop_contract",
        "source_kind",
        "source_label",
        "source_status",
        "source_phase_range",
        "source_design_charter",
        "source_record_candidate",
        "source_visual_supervision_profile",
        "source_consent_gate_profile",
        "source_physiological_sensor_profile",
        "source_secure_drop_consumer_boundary",
        "secrets_backend_runtime_added",
        "secrets_access_granted",
        "vault_env_access_granted",
        "credential_policy",
        "credential_loading_added",
        "private_health_data_allowed",
        "phase12k_allows_private_health_data_processing",
        "phase12m_allows_private_health_data_processing",
        "phase12n_allows_private_health_data_processing",
        "phase12o_allows_private_health_data_processing",
        "phase12p_allows_private_health_data_processing",
        "phase12q_allows_private_health_data_processing",
        "phase12r_allows_private_health_data_processing",
        "phase12s_allows_private_health_data_processing",
        "private_health_data_processing_added",
    }
    if normalized in allowed:
        return False
    blocked = {
        "source_id",
        "source_ids",
        "device_id",
        "device_ids",
        "serial_number",
        "serial_numbers",
        "bluetooth_mac",
        "bluetooth_macs",
        "router_id",
        "router_ids",
        "api_key",
        "access_token",
        "refresh_token",
        "secret_value",
        "password",
        "raw_document_text",
        "raw_csi",
        "raw_rf",
        "raw_bia",
        "raw_impedance",
        "raw_impedance_trace",
        "raw_ultrasound",
        "raw_acoustic",
        "bia_reading",
        "bia_readings",
        "impedance_trace",
        "ultrasound_payload",
        "acoustic_payload",
        "raw_screenshot",
        "raw_ocr",
        "raw_clipboard_text",
        "screenshot_payload",
        "ocr_payload",
        "camera_payload",
        "microphone_payload",
        "audio_payload",
        "recording_payload",
        "raw_recording_payload",
        "camera_capture",
        "microphone_capture",
        "clipboard_capture",
        "screen_recording",
        "audio_recording",
        "click_automation",
        "input_automation",
        "hidden_monitoring",
        "background_monitoring",
        "payload_content",
        "payload_body",
        "content_body",
        "audit_payload",
        "audit_content",
        "secure_drop_payload",
        "unencrypted_transfer",
        "anonymous_recipient",
        "unkeyed_recipient",
        "stego_security_boundary",
        "recipient_did",
        "keyring_id",
        "model_body",
        "parser_body",
        "provider_body",
    }
    blocked_fragments = (
        "private",
        "credential",
        "token",
        "secret",
        "source_id",
        "device_id",
        "serial_number",
        "bluetooth_mac",
        "mac_address",
        "router_id",
        "absolute_path",
        "remote_url",
        "raw_bia",
        "raw_impedance",
        "raw_ultrasound",
        "raw_acoustic",
        "bia_reading",
        "impedance_trace",
        "ultrasound_payload",
        "acoustic_payload",
        "payload_content",
        "payload_body",
        "audit_content",
        "secure_drop_payload",
        "unencrypted",
        "anonymous",
        "unkeyed",
        "stego_security",
        "recipient_did",
        "keyring",
    )
    return normalized in blocked or any(fragment in normalized for fragment in blocked_fragments)


def _unsafe_string_count(value: str) -> int:
    lowered = value.lower().replace("\\", "/")
    normalized = lowered.replace("-", "_").replace(" ", "_")
    privacy_safe_values = {
        *PHASE12D_CAPABILITY_CATEGORIES,
        *PHASE12D_REQUIRED_FUTURE_GATES,
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
        PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE.lower(),
        PHASE12E_SENSOR_PHASE,
        PHASE12E_AUTHORIZATION_STATUS,
        PHASE12E_GRANT_STATUS,
        PHASE12E_PROFILE_STATUS,
        PHASE12E_CAPABILITY_STATUS,
        PHASE12E_NON_DIAGNOSTIC_BOUNDARY_STATUS,
        PHASE12E_FUTURE_GATE_STATUS,
        PHASE12E_SENSOR_EVIDENCE_BOUNDARY_STATUS,
        *PHASE12E_STATUS_LABELS,
        *PHASE12E_SENSOR_CAPABILITY_LABELS,
        *PHASE12E_NON_DIAGNOSTIC_BOUNDARIES,
        *PHASE12E_REQUIRED_FUTURE_GATES,
        *PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES,
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
        PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE.lower(),
        PHASE12F_CANONICAL_OWNER,
        PHASE12F_CANONICAL_REFERENCE,
        PHASE12F_CANONICAL_CONTRACT_STATUS,
        PHASE12F_CONSUMER_PHASE,
        PHASE12F_AUTHORIZATION_STATUS,
        PHASE12F_GRANT_STATUS,
        PHASE12F_BOUNDARY_STATUS,
        PHASE12F_ARTIFACT_STATUS,
        PHASE12F_PROHIBITED_SOURCE_STATUS,
        PHASE12F_ENCRYPTION_REQUIREMENT_STATUS,
        PHASE12F_CONCEALMENT_STATUS,
        PHASE12F_AUDIT_REQUIREMENT_STATUS,
        *PHASE12F_STATUS_LABELS,
        *PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS,
        *PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES,
        "content-fabric-secure-drop-design-contract",
        "ardynai/kortex-audio",
        PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
        PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
        PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE.lower(),
        PHASE12G_READINESS_PHASE,
        PHASE12G_AUTHORIZATION_STATUS,
        PHASE12G_GRANT_STATUS,
        PHASE12G_MATRIX_STATUS,
        PHASE12G_COVERAGE_STATUS,
        PHASE12G_BLOCKED_RUNTIME_STATUS,
        *PHASE12G_STATUS_LABELS,
        *PHASE12G_SOMATIC_RESPONSIBILITIES,
        *PHASE12G_REPO_FAMILY_OWNERS,
        *PHASE12G_REVIEW_REQUIREMENTS,
        *(area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS),
        *(area[1].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
        *(area[4].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
        *(area[5].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
        *(area[6].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
        PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE.lower(),
        PHASE12H_READINESS_PHASE,
        PHASE12H_AUTHORIZATION_STATUS,
        PHASE12H_GRANT_STATUS,
        PHASE12H_MATRIX_STATUS,
        PHASE12H_ENTRY_STATUS,
        PHASE12H_OPTIONAL_PEER_STATUS,
        *PHASE12H_STATUS_LABELS,
        *PHASE12H_OPTIONAL_INTEGRATION_PEERS,
        *PHASE12H_OPTIONAL_INTEGRATION_ROLES,
        PHASE12H_STANDALONE_UI_STATEMENT.lower(),
        PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT.lower(),
        PHASE12H_PEER_INTEGRATION_STATEMENT.lower(),
        PHASE12H_SECURE_DROP_STATEMENT.lower(),
        PHASE12H_NON_AUTHORIZATION_STATEMENT.lower(),
        *(area[0] for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
        *(area[1].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
        *(area[2].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
        *(area[3].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
        *(area[5] for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
        *(peer[0] for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
        *(peer[1] for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
        *(peer[2].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
        PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
        PHASE12I_SOURCE_PHASE_RANGE.lower(),
        PHASE12I_CAPABILITY_PHASE,
        PHASE12I_AUTHORIZATION_STATUS,
        PHASE12I_GRANT_STATUS,
        PHASE12I_PROFILE_STATUS,
        PHASE12I_LABEL_STATUS,
        PHASE12I_SPECIALIST_PROFILE_STATUS,
        PHASE12I_SOURCE_CLASS_STATUS,
        PHASE12I_FUTURE_GATE_STATUS,
        PHASE12I_SOURCE_REFERENCE_STATUS,
        *PHASE12I_STATUS_LABELS,
        *PHASE12I_USER_PREFERENCE_MODES,
        *PHASE12I_SPECIALIST_PROFILE_LABELS,
        *PHASE12I_SOURCE_CLASS_LABELS,
        *PHASE12I_REQUIRED_FUTURE_GATES,
        PHASE12I_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12I_WESTERN_MEDICINE_STATEMENT.lower(),
        PHASE12I_NATURAL_REMEDY_STATEMENT.lower(),
        PHASE12I_FOOD_CURE_STATEMENT.lower(),
        PHASE12I_SAFETY_WARNING_STATEMENT.lower(),
        PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
        PHASE12K_SOURCE_PHASE_RANGE.lower(),
        PHASE12K_CAPABILITY_PHASE,
        PHASE12K_AUTHORIZATION_STATUS,
        PHASE12K_GRANT_STATUS,
        PHASE12K_CREDENTIAL_POLICY,
        PHASE12K_PROFILE_STATUS,
        PHASE12K_BACKEND_OPTION_STATUS,
        PHASE12K_WORKLOAD_CLASS_STATUS,
        PHASE12K_FUTURE_GATE_STATUS,
        PHASE12K_SOURCE_REFERENCE_STATUS,
        *PHASE12K_STATUS_LABELS,
        *PHASE12K_BACKEND_OPTION_LABELS,
        *(label.lower() for label in PHASE12K_WORKLOAD_CLASSES),
        *PHASE12K_REQUIRED_FUTURE_GATES,
        PHASE12K_COMPUTE_BOUNDARY_STATEMENT.lower(),
        PHASE12K_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
        PHASE12L_SOURCE_PHASE_RANGE.lower(),
        PHASE12L_CAPABILITY_PHASE,
        PHASE12L_AUTHORIZATION_STATUS,
        PHASE12L_GRANT_STATUS,
        PHASE12L_PROFILE_STATUS,
        PHASE12L_FABRIC_INTEROP_STATUS,
        PHASE12L_MESSAGE_CODEC_STATUS,
        PHASE12L_A2A_TRANSPORT_STATUS,
        PHASE12L_MCP_INTEROP_STATUS,
        PHASE12L_SECURE_DROP_STATUS,
        PHASE12L_CREDENTIAL_POLICY,
        PHASE12L_FABRIC_CAPABILITY_STATUS,
        PHASE12L_FORBIDDEN_LABEL_STATUS,
        PHASE12L_FUTURE_GATE_STATUS,
        PHASE12L_SOURCE_REFERENCE_STATUS,
        *PHASE12L_STATUS_LABELS,
        *PHASE12L_FABRIC_CAPABILITY_LABELS,
        *PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS,
        *PHASE12L_REQUIRED_FUTURE_GATES,
        PHASE12L_FABRIC_BOUNDARY_STATEMENT.lower(),
        PHASE12L_AUDIT_BOUNDARY_STATEMENT.lower(),
        PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
        PHASE12M_SOURCE_PHASE_RANGE.lower(),
        PHASE12M_MODEL_OPTION_PROFILE_PHASE,
        PHASE12M_AUTHORIZATION_STATUS,
        PHASE12M_GRANT_STATUS,
        PHASE12M_PROFILE_STATUS,
        PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
        PHASE12M_CANDIDATE_LABEL_STATUS,
        PHASE12M_FUTURE_GATE_STATUS,
        PHASE12M_SOURCE_REFERENCE_STATUS,
        *PHASE12M_STATUS_LABELS,
        *PHASE12M_MODEL_OPTION_CATEGORIES,
        *(label.lower() for label in PHASE12M_CANDIDATE_LABELS),
        *PHASE12M_REQUIRED_FUTURE_GATES,
        PHASE12M_MODEL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_MEDICAL_BOUNDARY_STATEMENT.lower(),
        PHASE12M_SENSOR_BOUNDARY_STATEMENT.lower(),
        PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
        PHASE12N_SOURCE_PHASE_RANGE.lower(),
        PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
        PHASE12N_AUTHORIZATION_STATUS,
        PHASE12N_GRANT_STATUS,
        PHASE12N_PROFILE_STATUS,
        PHASE12N_WORKFLOW_MODE_STATUS,
        PHASE12N_FUSION_CONCEPT_STATUS,
        PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS,
        PHASE12N_FUTURE_GATE_STATUS,
        PHASE12N_SOURCE_REFERENCE_STATUS,
        *PHASE12N_STATUS_LABELS,
        *(label for label, _ in PHASE12N_WORKFLOW_MODES),
        *(definition.lower() for _, definition in PHASE12N_WORKFLOW_MODES),
        *PHASE12N_FUSION_CONCEPT_LABELS,
        *PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS,
        *PHASE12N_REQUIRED_FUTURE_GATES,
        PHASE12N_WORKFLOW_BOUNDARY_STATEMENT.lower(),
        PHASE12N_FUSION_BOUNDARY_STATEMENT.lower(),
        PHASE12N_SCIENTIST_BOUNDARY_STATEMENT.lower(),
        PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT.lower(),
        PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
        PHASE12O_SOURCE_PHASE.lower(),
        PHASE12O_MATRIX_PHASE,
        PHASE12O_AUTHORIZATION_STATUS,
        PHASE12O_GRANT_STATUS,
        PHASE12O_MATRIX_STATUS,
        PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
        PHASE12O_FUTURE_GATE_STATUS,
        PHASE12O_MODE_GATE_STATUS,
        PHASE12O_SOURCE_REFERENCE_STATUS,
        PHASE12O_GATE_SCOPE,
        *PHASE12O_STATUS_LABELS,
        *PHASE12O_WORKFLOW_MODES,
        *PHASE12O_REQUIRED_FUTURE_GATES,
        PHASE12O_MATRIX_BOUNDARY_STATEMENT.lower(),
        PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12O_STANDALONE_FIRST_STATEMENT.lower(),
        PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
        PHASE12P_SOURCE_PHASE_RANGE.lower(),
        PHASE12P_PACKET_PHASE,
        PHASE12P_AUTHORIZATION_STATUS,
        PHASE12P_GRANT_STATUS,
        PHASE12P_REQUESTED_TRANSITION_STATUS,
        PHASE12P_PACKET_STATUS,
        PHASE12P_MODE_PACKET_STATUS,
        PHASE12P_FUTURE_GATE_STATUS,
        PHASE12P_REVIEWER_CLASS_STATUS,
        PHASE12P_RISK_PLACEHOLDER_STATUS,
        PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
        PHASE12P_SOURCE_REFERENCE_STATUS,
        PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
        PHASE12P_DENIAL_BLOCKED_STATUS,
        PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
        *PHASE12P_STATUS_LABELS,
        *PHASE12P_WORKFLOW_MODES,
        *PHASE12P_REQUIRED_FUTURE_GATES,
        *PHASE12P_REQUIRED_REVIEWER_CLASSES,
        *PHASE12P_RISK_SUMMARY_PLACEHOLDERS,
        *PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS,
        PHASE12P_PACKET_BOUNDARY_STATEMENT.lower(),
        PHASE12P_REVIEW_REQUIREMENT_STATEMENT.lower(),
        PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
        PHASE12Q_SOURCE_PHASE_RANGE.lower(),
        PHASE12Q_DECISION_RECORD_PHASE,
        PHASE12Q_AUTHORIZATION_STATUS,
        PHASE12Q_GRANT_STATUS,
        PHASE12Q_DECISION_RECORD_STATUS,
        PHASE12Q_SOURCE_REFERENCE_STATUS,
        PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
        PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
        *PHASE12Q_DECISION_STATUSES,
        *PHASE12Q_DECISION_REASON_CODES,
        *PHASE12Q_DECISION_STATUS_DISPOSITIONS.values(),
        *PHASE12Q_STATUS_LABELS,
        *PHASE12Q_WORKFLOW_MODES,
        *PHASE12Q_REQUIRED_FUTURE_GATES,
        *PHASE12Q_REQUIRED_REVIEWER_CLASSES,
        PHASE12Q_DECISION_SUMMARY.lower(),
        PHASE12Q_DECISION_BOUNDARY_STATEMENT.lower(),
        PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
        PHASE12R_SOURCE_PHASE_RANGE.lower(),
        PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
        PHASE12R_AUTHORIZATION_STATUS,
        PHASE12R_GRANT_STATUS,
        PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
        PHASE12R_SOURCE_REFERENCE_STATUS,
        PHASE12R_MODE_INDEX_STATUS,
        PHASE12R_PACKET_REFERENCE_STATUS,
        PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
        PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
        PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
        PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
        PHASE12R_STALE_STATUS,
        PHASE12R_REVIEW_NEEDED_STATUS,
        PHASE12R_STALE_REVIEW_NEEDED_STATUS,
        *PHASE12R_STATUS_LABELS,
        *PHASE12R_WORKFLOW_MODES,
        *PHASE12R_REQUIRED_FUTURE_GATES,
        *PHASE12R_REQUIRED_REVIEWER_CLASSES,
        PHASE12R_DECISION_SUMMARY.lower(),
        PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT.lower(),
        PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
        PHASE12S_SOURCE_PHASE_RANGE.lower(),
        PHASE12S_CLOSEOUT_SUMMARY_PHASE,
        PHASE12S_AUTHORIZATION_STATUS,
        PHASE12S_GRANT_STATUS,
        PHASE12S_SUMMARY_STATUS,
        PHASE12S_SOURCE_REFERENCE_STATUS,
        PHASE12S_MODE_COVERAGE_STATUS,
        PHASE12S_REVIEW_CHAIN_STATUS,
        PHASE12S_REVIEWER_NAVIGATION_SUMMARY.lower(),
        PHASE12S_OPERATOR_HANDOFF_SUMMARY.lower(),
        *PHASE12S_CLOSEOUT_STATUSES,
        *PHASE12S_STATUS_LABELS,
        *PHASE12S_WORKFLOW_MODES,
        *PHASE12S_REQUIRED_FUTURE_GATES,
        *PHASE12S_REQUIRED_REVIEWER_CLASSES,
        PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT.lower(),
        PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
    }
    if lowered in privacy_safe_values:
        return 0
    blocked_fragments = (
        "://",
        "http://",
        "https://",
        "fixture://",
        "fixtures/",
        "c:/",
        "source_id",
        "source-id",
        "device_id",
        "device-id",
        "serial_number",
        "serial-number",
        "bluetooth_mac",
        "bluetooth-mac",
        "mac_address",
        "mac-address",
        "router_id",
        "router-id",
        "api_key",
        "access_token",
        "refresh_token",
        "secret_value",
        "password",
        "raw_document_text",
        "raw-document-text",
        "raw_csi",
        "raw-csi",
        "raw_rf",
        "raw-rf",
        "raw_bia",
        "raw-bia",
        "raw_impedance",
        "raw-impedance",
        "raw_impedance_trace",
        "raw-impedance-trace",
        "raw_ultrasound",
        "raw-ultrasound",
        "raw_acoustic",
        "raw-acoustic",
        "bia_reading",
        "bia-reading",
        "bia_readings",
        "bia-readings",
        "impedance_trace",
        "impedance-trace",
        "ultrasound_payload",
        "ultrasound-payload",
        "acoustic_payload",
        "acoustic-payload",
        "raw_screenshot",
        "raw-screenshot",
        "raw_ocr",
        "raw-ocr",
        "raw_clipboard_text",
        "raw-clipboard-text",
        "screenshot_payload",
        "screenshot-payload",
        "ocr_payload",
        "ocr-payload",
        "camera_payload",
        "camera-payload",
        "microphone_payload",
        "microphone-payload",
        "audio_payload",
        "audio-payload",
        "recording_payload",
        "recording-payload",
        "raw_recording_payload",
        "raw-recording-payload",
        "camera_capture",
        "camera-capture",
        "microphone_capture",
        "microphone-capture",
        "clipboard_capture",
        "clipboard-capture",
        "screen_recording",
        "screen-recording",
        "audio_recording",
        "audio-recording",
        "click_automation",
        "click-automation",
        "input_automation",
        "input-automation",
        "hidden_monitoring",
        "hidden-monitoring",
        "background_monitoring",
        "background-monitoring",
        "model_body",
        "model-body",
        "parser_body",
        "parser-body",
        "provider_body",
        "provider-body",
        "diagnosis",
        "diagnostic",
        "disease detection",
        "disease-detection",
        "mri replacement",
        "mri-replacement",
        "ct replacement",
        "ct-replacement",
        "scanner equivalence",
        "scanner-equivalence",
        "treatment",
        "medical",
        "clinical",
        "payload_content",
        "payload-content",
        "payload body",
        "payload-body",
        "content body",
        "content-body",
        "audit payload",
        "audit-payload",
        "audit content",
        "audit-content",
        "secure_drop_payload",
        "secure-drop-payload",
        "unencrypted",
        "anonymous recipient",
        "anonymous-recipient",
        "unkeyed",
        "did:",
        "recipient did",
        "recipient-did",
        "keyring",
        "send executed",
        "send-executed",
        "receive executed",
        "receive-executed",
        "network send",
        "network-send",
        "inbox ui",
        "inbox-ui",
        "stego security",
        "stego-security",
        "steganography security",
        "steganography-security",
    )
    return sum(1 for fragment in blocked_fragments if fragment in lowered or fragment in normalized)


def _authorization_wording_count(value: object) -> int:
    if isinstance(value, Mapping):
        return sum(_authorization_wording_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_authorization_wording_count(item) for item in value)
    if not isinstance(value, str):
        return 0
    lowered = value.lower().replace("\\", "/")
    safe_values = {
        PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND,
        PHASE12A_AUTHORIZATION_PHASE,
        PHASE12A_AUTHORIZATION_STATUS,
        PHASE12A_CHARTER_SCOPE,
        PHASE12A_CHARTER_STATUS,
        PHASE12A_FUTURE_GATE_STATUS,
        PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_FIXTURE_KIND,
        PHASE11_RUNTIME_AUTHORIZATION_GAP_LEDGER_FIXTURE_KIND,
        PHASE11_PLANNING_GOVERNANCE_CLOSEOUT_STATUS,
        PHASE11_REVIEW_TRAIL_EXPORT_READINESS_GAP,
        *PHASE12A_FUTURE_REQUIRED_GATES,
    }
    safe_values.update(
        {
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND,
            PHASE12B_AUTHORIZATION_PHASE,
            PHASE12B_AUTHORIZATION_STATUS,
            PHASE12B_DECISION_STATUS_NOT_SUBMITTED,
            PHASE12B_DECISION_STATUS_REVIEW_REQUIRED,
            PHASE12B_GRANT_STATUS,
            PHASE12B_RECORD_CANDIDATE_STATUS,
            PHASE12B_REQUEST_STATUS,
            PHASE12B_REVIEWER_ROLE_STATUS,
            PHASE12B_FUTURE_GATE_STATUS,
            PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE.lower(),
            *PHASE12B_STATUS_LABELS,
            *PHASE12B_REQUESTED_DOMAINS,
            *PHASE12B_REQUIRED_REVIEWER_ROLES,
        }
    )
    safe_values.update(gate_id for gate_id, _ in PHASE12B_REQUIRED_FUTURE_GATES)
    safe_values.update(
        {
            PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND,
            PHASE12C_SUPERVISION_PHASE,
            PHASE12C_AUTHORIZATION_STATUS,
            PHASE12C_GRANT_STATUS,
            PHASE12C_PROFILE_STATUS,
            PHASE12C_CAPABILITY_STATUS,
            PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE.lower(),
            *PHASE12C_STATUS_LABELS,
            *PHASE12C_ALLOWED_CAPABILITY_LABELS,
        }
    )
    safe_values.update(
        {
            PHASE12D_CONSENT_GATE_PROFILE_KIND,
            PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE.lower(),
            PHASE12D_CONSENT_PHASE,
            PHASE12D_AUTHORIZATION_STATUS,
            PHASE12D_GRANT_STATUS,
            PHASE12D_CONSENT_GATE_STATUS,
            PHASE12D_CAPABILITY_CATEGORY_STATUS,
            PHASE12D_FUTURE_GATE_STATUS,
            *PHASE12D_STATUS_LABELS,
            *PHASE12D_CAPABILITY_CATEGORIES,
            *PHASE12D_REQUIRED_FUTURE_GATES,
        }
    )
    safe_values.update(
        {
            PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND,
            PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE.lower(),
            PHASE12E_SENSOR_PHASE,
            PHASE12E_AUTHORIZATION_STATUS,
            PHASE12E_GRANT_STATUS,
            PHASE12E_PROFILE_STATUS,
            PHASE12E_CAPABILITY_STATUS,
            PHASE12E_NON_DIAGNOSTIC_BOUNDARY_STATUS,
            PHASE12E_FUTURE_GATE_STATUS,
            PHASE12E_SENSOR_EVIDENCE_BOUNDARY_STATUS,
            *PHASE12E_STATUS_LABELS,
            *PHASE12E_SENSOR_CAPABILITY_LABELS,
            *PHASE12E_NON_DIAGNOSTIC_BOUNDARIES,
            *PHASE12E_REQUIRED_FUTURE_GATES,
            *PHASE12E_SOURCE_SENSOR_EVIDENCE_BOUNDARIES,
        }
    )
    safe_values.update(
        {
            PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND,
            PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE.lower(),
            PHASE12F_CANONICAL_OWNER,
            PHASE12F_CANONICAL_REFERENCE,
            PHASE12F_CANONICAL_CONTRACT_STATUS,
            PHASE12F_CONSUMER_PHASE,
            PHASE12F_AUTHORIZATION_STATUS,
            PHASE12F_GRANT_STATUS,
            PHASE12F_BOUNDARY_STATUS,
            PHASE12F_ARTIFACT_STATUS,
            PHASE12F_PROHIBITED_SOURCE_STATUS,
            PHASE12F_ENCRYPTION_REQUIREMENT_STATUS,
            PHASE12F_CONCEALMENT_STATUS,
            PHASE12F_AUDIT_REQUIREMENT_STATUS,
            *PHASE12F_STATUS_LABELS,
            *PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS,
            *PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES,
            "content-fabric-secure-drop-design-contract",
            "ardynai/kortex-audio",
            PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA,
        }
    )
    safe_values.update(
        {
            PHASE12G_PRODUCTION_READINESS_MATRIX_KIND,
            PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE.lower(),
            PHASE12G_READINESS_PHASE,
            PHASE12G_AUTHORIZATION_STATUS,
            PHASE12G_GRANT_STATUS,
            PHASE12G_MATRIX_STATUS,
            PHASE12G_COVERAGE_STATUS,
            PHASE12G_BLOCKED_RUNTIME_STATUS,
            *PHASE12G_STATUS_LABELS,
            *PHASE12G_SOMATIC_RESPONSIBILITIES,
            *PHASE12G_REPO_FAMILY_OWNERS,
            *PHASE12G_REVIEW_REQUIREMENTS,
            *(area[0] for area in PHASE12G_PRODUCTION_READINESS_AREAS),
            *(area[1].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
            *(area[4].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
            *(area[5].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
            *(area[6].lower() for area in PHASE12G_PRODUCTION_READINESS_AREAS),
            PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND,
            PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE.lower(),
            PHASE12H_READINESS_PHASE,
            PHASE12H_AUTHORIZATION_STATUS,
            PHASE12H_GRANT_STATUS,
            PHASE12H_MATRIX_STATUS,
            PHASE12H_ENTRY_STATUS,
            PHASE12H_OPTIONAL_PEER_STATUS,
            *PHASE12H_STATUS_LABELS,
            *PHASE12H_OPTIONAL_INTEGRATION_PEERS,
            *PHASE12H_OPTIONAL_INTEGRATION_ROLES,
            PHASE12H_STANDALONE_UI_STATEMENT.lower(),
            PHASE12H_LOCUS_OPTIONAL_UI_STATEMENT.lower(),
            PHASE12H_PEER_INTEGRATION_STATEMENT.lower(),
            PHASE12H_SECURE_DROP_STATEMENT.lower(),
            PHASE12H_NON_AUTHORIZATION_STATEMENT.lower(),
            *(area[0] for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
            *(area[1].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
            *(area[2].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
            *(area[3].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
            *(area[5] for area in PHASE12H_SOMATIC_STANDALONE_AREAS),
            *(peer[0] for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
            *(peer[1] for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
            *(peer[2].lower() for area in PHASE12H_SOMATIC_STANDALONE_AREAS for peer in area[4]),
            PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND,
            PHASE12I_SOURCE_PHASE_RANGE.lower(),
            PHASE12I_CAPABILITY_PHASE,
            PHASE12I_AUTHORIZATION_STATUS,
            PHASE12I_GRANT_STATUS,
            PHASE12I_PROFILE_STATUS,
            PHASE12I_LABEL_STATUS,
            PHASE12I_SPECIALIST_PROFILE_STATUS,
            PHASE12I_SOURCE_CLASS_STATUS,
            PHASE12I_FUTURE_GATE_STATUS,
            PHASE12I_SOURCE_REFERENCE_STATUS,
            *PHASE12I_STATUS_LABELS,
            *PHASE12I_USER_PREFERENCE_MODES,
            *PHASE12I_SPECIALIST_PROFILE_LABELS,
            *PHASE12I_SOURCE_CLASS_LABELS,
            *PHASE12I_REQUIRED_FUTURE_GATES,
            PHASE12I_MEDICAL_BOUNDARY_STATEMENT.lower(),
            PHASE12I_WESTERN_MEDICINE_STATEMENT.lower(),
            PHASE12I_NATURAL_REMEDY_STATEMENT.lower(),
            PHASE12I_FOOD_CURE_STATEMENT.lower(),
            PHASE12I_SAFETY_WARNING_STATEMENT.lower(),
            PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND,
            PHASE12K_SOURCE_PHASE_RANGE.lower(),
            PHASE12K_CAPABILITY_PHASE,
            PHASE12K_AUTHORIZATION_STATUS,
            PHASE12K_GRANT_STATUS,
            PHASE12K_CREDENTIAL_POLICY,
            PHASE12K_PROFILE_STATUS,
            PHASE12K_BACKEND_OPTION_STATUS,
            PHASE12K_WORKLOAD_CLASS_STATUS,
            PHASE12K_FUTURE_GATE_STATUS,
            PHASE12K_SOURCE_REFERENCE_STATUS,
            *PHASE12K_STATUS_LABELS,
            *PHASE12K_BACKEND_OPTION_LABELS,
            *(label.lower() for label in PHASE12K_WORKLOAD_CLASSES),
            *PHASE12K_REQUIRED_FUTURE_GATES,
            PHASE12K_COMPUTE_BOUNDARY_STATEMENT.lower(),
            PHASE12K_MEDICAL_BOUNDARY_STATEMENT.lower(),
            PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND,
            PHASE12L_SOURCE_PHASE_RANGE.lower(),
            PHASE12L_CAPABILITY_PHASE,
            PHASE12L_AUTHORIZATION_STATUS,
            PHASE12L_GRANT_STATUS,
            PHASE12L_PROFILE_STATUS,
            PHASE12L_FABRIC_INTEROP_STATUS,
            PHASE12L_MESSAGE_CODEC_STATUS,
            PHASE12L_A2A_TRANSPORT_STATUS,
            PHASE12L_MCP_INTEROP_STATUS,
            PHASE12L_SECURE_DROP_STATUS,
            PHASE12L_CREDENTIAL_POLICY,
            PHASE12L_FABRIC_CAPABILITY_STATUS,
            PHASE12L_FORBIDDEN_LABEL_STATUS,
            PHASE12L_FUTURE_GATE_STATUS,
            PHASE12L_SOURCE_REFERENCE_STATUS,
            *PHASE12L_STATUS_LABELS,
            *PHASE12L_FABRIC_CAPABILITY_LABELS,
            *PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS,
            *PHASE12L_REQUIRED_FUTURE_GATES,
            PHASE12L_FABRIC_BOUNDARY_STATEMENT.lower(),
            PHASE12L_AUDIT_BOUNDARY_STATEMENT.lower(),
            PHASE12L_SECURE_DROP_BOUNDARY_STATEMENT.lower(),
            PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND,
            PHASE12M_SOURCE_PHASE_RANGE.lower(),
            PHASE12M_MODEL_OPTION_PROFILE_PHASE,
            PHASE12M_AUTHORIZATION_STATUS,
            PHASE12M_GRANT_STATUS,
            PHASE12M_PROFILE_STATUS,
            PHASE12M_MODEL_OPTION_CATEGORY_STATUS,
            PHASE12M_CANDIDATE_LABEL_STATUS,
            PHASE12M_FUTURE_GATE_STATUS,
            PHASE12M_SOURCE_REFERENCE_STATUS,
            *PHASE12M_STATUS_LABELS,
            *PHASE12M_MODEL_OPTION_CATEGORIES,
            *(label.lower() for label in PHASE12M_CANDIDATE_LABELS),
            *PHASE12M_REQUIRED_FUTURE_GATES,
            PHASE12M_MODEL_BOUNDARY_STATEMENT.lower(),
            PHASE12M_MEDICAL_BOUNDARY_STATEMENT.lower(),
            PHASE12M_SENSOR_BOUNDARY_STATEMENT.lower(),
            PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND,
            PHASE12N_SOURCE_PHASE_RANGE.lower(),
            PHASE12N_WORKFLOW_MODE_PROFILE_PHASE,
            PHASE12N_AUTHORIZATION_STATUS,
            PHASE12N_GRANT_STATUS,
            PHASE12N_PROFILE_STATUS,
            PHASE12N_WORKFLOW_MODE_STATUS,
            PHASE12N_FUSION_CONCEPT_STATUS,
            PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_STATUS,
            PHASE12N_FUTURE_GATE_STATUS,
            PHASE12N_SOURCE_REFERENCE_STATUS,
            *PHASE12N_STATUS_LABELS,
            *(label for label, _ in PHASE12N_WORKFLOW_MODES),
            *(definition.lower() for _, definition in PHASE12N_WORKFLOW_MODES),
            *PHASE12N_FUSION_CONCEPT_LABELS,
            *PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS,
            *PHASE12N_REQUIRED_FUTURE_GATES,
            PHASE12N_WORKFLOW_BOUNDARY_STATEMENT.lower(),
            PHASE12N_FUSION_BOUNDARY_STATEMENT.lower(),
            PHASE12N_SCIENTIST_BOUNDARY_STATEMENT.lower(),
            PHASE12N_MEDICAL_SENSOR_BOUNDARY_STATEMENT.lower(),
            PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND,
            PHASE12O_SOURCE_PHASE.lower(),
            PHASE12O_MATRIX_PHASE,
            PHASE12O_AUTHORIZATION_STATUS,
            PHASE12O_GRANT_STATUS,
            PHASE12O_MATRIX_STATUS,
            PHASE12O_WORKFLOW_MODE_MATRIX_STATUS,
            PHASE12O_FUTURE_GATE_STATUS,
            PHASE12O_MODE_GATE_STATUS,
            PHASE12O_SOURCE_REFERENCE_STATUS,
            PHASE12O_GATE_SCOPE,
            *PHASE12O_STATUS_LABELS,
            *PHASE12O_WORKFLOW_MODES,
            *PHASE12O_REQUIRED_FUTURE_GATES,
            PHASE12O_MATRIX_BOUNDARY_STATEMENT.lower(),
            PHASE12O_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
            PHASE12O_STANDALONE_FIRST_STATEMENT.lower(),
            PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND,
            PHASE12P_SOURCE_PHASE_RANGE.lower(),
            PHASE12P_PACKET_PHASE,
            PHASE12P_AUTHORIZATION_STATUS,
            PHASE12P_GRANT_STATUS,
            PHASE12P_REQUESTED_TRANSITION_STATUS,
            PHASE12P_PACKET_STATUS,
            PHASE12P_MODE_PACKET_STATUS,
            PHASE12P_FUTURE_GATE_STATUS,
            PHASE12P_REVIEWER_CLASS_STATUS,
            PHASE12P_RISK_PLACEHOLDER_STATUS,
            PHASE12P_EVIDENCE_PLACEHOLDER_STATUS,
            PHASE12P_SOURCE_REFERENCE_STATUS,
            PHASE12P_PREREQUISITE_MATRIX_REFERENCE_STATUS,
            PHASE12P_DENIAL_BLOCKED_STATUS,
            PHASE12P_ACTIVATION_NOT_PERMITTED_STATUS,
            *PHASE12P_STATUS_LABELS,
            *PHASE12P_WORKFLOW_MODES,
            *PHASE12P_REQUIRED_FUTURE_GATES,
            *PHASE12P_REQUIRED_REVIEWER_CLASSES,
            *PHASE12P_RISK_SUMMARY_PLACEHOLDERS,
            *PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS,
            PHASE12P_PACKET_BOUNDARY_STATEMENT.lower(),
            PHASE12P_REVIEW_REQUIREMENT_STATEMENT.lower(),
            PHASE12P_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
            PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND,
            PHASE12Q_SOURCE_PHASE_RANGE.lower(),
            PHASE12Q_DECISION_RECORD_PHASE,
            PHASE12Q_AUTHORIZATION_STATUS,
            PHASE12Q_GRANT_STATUS,
            PHASE12Q_DECISION_RECORD_STATUS,
            PHASE12Q_SOURCE_REFERENCE_STATUS,
            PHASE12Q_FUTURE_GATE_SNAPSHOT_STATUS,
            PHASE12Q_REVIEWER_CLASS_REQUIRED_STATUS,
            PHASE12Q_REVIEWER_CLASS_REPRESENTED_STATUS,
            *PHASE12Q_DECISION_STATUSES,
            *PHASE12Q_DECISION_REASON_CODES,
            *PHASE12Q_DECISION_STATUS_DISPOSITIONS.values(),
            *PHASE12Q_STATUS_LABELS,
            *PHASE12Q_WORKFLOW_MODES,
            *PHASE12Q_REQUIRED_FUTURE_GATES,
            *PHASE12Q_REQUIRED_REVIEWER_CLASSES,
            PHASE12Q_DECISION_SUMMARY.lower(),
            PHASE12Q_DECISION_BOUNDARY_STATEMENT.lower(),
            PHASE12Q_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
            PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND,
            PHASE12R_SOURCE_PHASE_RANGE.lower(),
            PHASE12R_AUDIT_TRAIL_INDEX_PHASE,
            PHASE12R_AUTHORIZATION_STATUS,
            PHASE12R_GRANT_STATUS,
            PHASE12R_AUDIT_TRAIL_INDEX_STATUS,
            PHASE12R_SOURCE_REFERENCE_STATUS,
            PHASE12R_MODE_INDEX_STATUS,
            PHASE12R_PACKET_REFERENCE_STATUS,
            PHASE12R_DECISION_RECORD_REFERENCE_STATUS,
            PHASE12R_DECISION_STATUS_SUMMARY_STATUS,
            PHASE12R_REVIEWER_CLASS_REQUIRED_STATUS,
            PHASE12R_REVIEWER_CLASS_REPRESENTED_STATUS,
            PHASE12R_STALE_STATUS,
            PHASE12R_REVIEW_NEEDED_STATUS,
            PHASE12R_STALE_REVIEW_NEEDED_STATUS,
            *PHASE12R_STATUS_LABELS,
            *PHASE12R_WORKFLOW_MODES,
            *PHASE12R_REQUIRED_FUTURE_GATES,
            *PHASE12R_REQUIRED_REVIEWER_CLASSES,
            PHASE12R_DECISION_SUMMARY.lower(),
            PHASE12R_AUDIT_TRAIL_BOUNDARY_STATEMENT.lower(),
            PHASE12R_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
            PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND,
            PHASE12S_SOURCE_PHASE_RANGE.lower(),
            PHASE12S_CLOSEOUT_SUMMARY_PHASE,
            PHASE12S_AUTHORIZATION_STATUS,
            PHASE12S_GRANT_STATUS,
            PHASE12S_SUMMARY_STATUS,
            PHASE12S_SOURCE_REFERENCE_STATUS,
            PHASE12S_MODE_COVERAGE_STATUS,
            PHASE12S_REVIEW_CHAIN_STATUS,
            PHASE12S_REVIEWER_NAVIGATION_SUMMARY.lower(),
            PHASE12S_OPERATOR_HANDOFF_SUMMARY.lower(),
            *PHASE12S_CLOSEOUT_STATUSES,
            *PHASE12S_STATUS_LABELS,
            *PHASE12S_WORKFLOW_MODES,
            *PHASE12S_REQUIRED_FUTURE_GATES,
            *PHASE12S_REQUIRED_REVIEWER_CLASSES,
            PHASE12S_CLOSEOUT_BOUNDARY_STATEMENT.lower(),
            PHASE12S_MEDICAL_PRIVACY_BOUNDARY_STATEMENT.lower(),
        }
    )
    if lowered in safe_values:
        return 0
    exact_fragments = {
        "sent",
        "received",
        "encrypted",
        "concealed",
        "user-selected",
        "user_selected",
    }
    if lowered in exact_fragments:
        return 1
    fragments = (
        "authorized",
        "approved",
        "ready",
        "complete",
        "chartered",
        "designed",
        "gate-defined",
        "candidate",
        "submitted",
        "review-required",
        "permission",
        "permitted",
        "grant",
        "granted",
        "passed",
        "satisfied",
        "runtime-enabled",
        "runtime_enabled",
        "execution-permitted",
        "execution_permitted",
        "accepted-for-runtime",
        "observed",
        "profiled",
        "configured",
        "connected",
        "measured",
        "scanned",
        "consented",
        "enabled",
        "consent-granted",
        "consent_granted",
    )
    return sum(1 for fragment in fragments if fragment in lowered)


__all__ = [
    "PHASE12A_AUTHORIZATION_PHASE",
    "PHASE12A_AUTHORIZATION_STATUS",
    "PHASE12A_CHARTER_SCOPE",
    "PHASE12A_CHARTER_STATUS",
    "PHASE12A_FUTURE_REQUIRED_GATES",
    "PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_CONTRACT_VERSION",
    "PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_KIND",
    "PHASE12A_RUNTIME_AUTHORIZATION_CHARTER_SOURCE_PHASE_RANGE",
    "PHASE12A_STATUS_LABELS",
    "PHASE12B_AUTHORIZATION_PHASE",
    "PHASE12B_AUTHORIZATION_STATUS",
    "PHASE12B_DECISION_STATUS_NOT_SUBMITTED",
    "PHASE12B_DECISION_STATUS_REVIEW_REQUIRED",
    "PHASE12B_GRANT_STATUS",
    "PHASE12B_RECORD_CANDIDATE_STATUS",
    "PHASE12B_REQUESTED_DOMAINS",
    "PHASE12B_REQUIRED_FUTURE_GATES",
    "PHASE12B_REQUIRED_REVIEWER_ROLES",
    "PHASE12B_RUNTIME_AUTHORIZATION_RECORD_CONTRACT_VERSION",
    "PHASE12B_RUNTIME_AUTHORIZATION_RECORD_KIND",
    "PHASE12B_RUNTIME_AUTHORIZATION_RECORD_SOURCE_PHASE",
    "PHASE12B_STATUS_LABELS",
    "PHASE12C_ALLOWED_CAPABILITY_LABELS",
    "PHASE12C_AUTHORIZATION_STATUS",
    "PHASE12C_GRANT_STATUS",
    "PHASE12C_PROFILE_STATUS",
    "PHASE12C_STATUS_LABELS",
    "PHASE12C_SUPERVISION_PHASE",
    "PHASE12C_VISUAL_SUPERVISION_PROFILE_CONTRACT_VERSION",
    "PHASE12C_VISUAL_SUPERVISION_PROFILE_KIND",
    "PHASE12C_VISUAL_SUPERVISION_PROFILE_SOURCE_PHASE",
    "PHASE12D_AUTHORIZATION_STATUS",
    "PHASE12D_CAPABILITY_CATEGORIES",
    "PHASE12D_CONSENT_GATE_PROFILE_CONTRACT_VERSION",
    "PHASE12D_CONSENT_GATE_PROFILE_KIND",
    "PHASE12D_CONSENT_GATE_PROFILE_SOURCE_PHASE_RANGE",
    "PHASE12D_CONSENT_GATE_STATUS",
    "PHASE12D_CONSENT_PHASE",
    "PHASE12D_GRANT_STATUS",
    "PHASE12D_REQUIRED_FUTURE_GATES",
    "PHASE12D_STATUS_LABELS",
    "PHASE12E_AUTHORIZATION_STATUS",
    "PHASE12E_GRANT_STATUS",
    "PHASE12E_NON_DIAGNOSTIC_BOUNDARIES",
    "PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_CONTRACT_VERSION",
    "PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_KIND",
    "PHASE12E_PHYSIOLOGICAL_SENSOR_PROFILE_SOURCE_PHASE_RANGE",
    "PHASE12E_PROFILE_STATUS",
    "PHASE12E_REQUIRED_FUTURE_GATES",
    "PHASE12E_SENSOR_CAPABILITY_LABELS",
    "PHASE12E_SENSOR_PHASE",
    "PHASE12E_STATUS_LABELS",
    "PHASE12F_ALLOWED_USER_SELECTED_ARTIFACT_LABELS",
    "PHASE12F_AUTHORIZATION_STATUS",
    "PHASE12F_CANONICAL_OWNER",
    "PHASE12F_CANONICAL_REFERENCE",
    "PHASE12F_CONTENT_FABRIC_SECURE_DROP_MERGE_SHA",
    "PHASE12F_CONSUMER_PHASE",
    "PHASE12F_GRANT_STATUS",
    "PHASE12F_PROHIBITED_AUTONOMOUS_SOURCES",
    "PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_CONTRACT_VERSION",
    "PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_KIND",
    "PHASE12F_SECURE_DROP_CONSUMER_BOUNDARY_SOURCE_PHASE_RANGE",
    "PHASE12F_STATUS_LABELS",
    "PHASE12G_AUTHORIZATION_STATUS",
    "PHASE12G_GRANT_STATUS",
    "PHASE12G_PRODUCTION_READINESS_AREAS",
    "PHASE12G_PRODUCTION_READINESS_MATRIX_CONTRACT_VERSION",
    "PHASE12G_PRODUCTION_READINESS_MATRIX_KIND",
    "PHASE12G_PRODUCTION_READINESS_MATRIX_SOURCE_PHASE_RANGE",
    "PHASE12G_READINESS_PHASE",
    "PHASE12G_REPO_FAMILY_OWNERS",
    "PHASE12G_REVIEW_REQUIREMENTS",
    "PHASE12G_SOMATIC_RESPONSIBILITIES",
    "PHASE12G_STATUS_LABELS",
    "PHASE12H_AUTHORIZATION_STATUS",
    "PHASE12H_GRANT_STATUS",
    "PHASE12H_OPTIONAL_INTEGRATION_PEERS",
    "PHASE12H_OPTIONAL_INTEGRATION_ROLES",
    "PHASE12H_READINESS_PHASE",
    "PHASE12H_SOMATIC_STANDALONE_AREAS",
    "PHASE12H_STANDALONE_OWNERSHIP_MATRIX_CONTRACT_VERSION",
    "PHASE12H_STANDALONE_OWNERSHIP_MATRIX_KIND",
    "PHASE12H_STANDALONE_OWNERSHIP_MATRIX_SOURCE_PHASE",
    "PHASE12H_STATUS_LABELS",
    "PHASE12I_AUTHORIZATION_STATUS",
    "PHASE12I_CAPABILITY_PHASE",
    "PHASE12I_GRANT_STATUS",
    "PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_CONTRACT_VERSION",
    "PHASE12I_INTEGRATIVE_HERBAL_NUTRITION_PROFILE_KIND",
    "PHASE12I_REQUIRED_FUTURE_GATES",
    "PHASE12I_SOURCE_CLASS_LABELS",
    "PHASE12I_SOURCE_PHASE_RANGE",
    "PHASE12I_SPECIALIST_PROFILE_LABELS",
    "PHASE12I_STATUS_LABELS",
    "PHASE12I_USER_PREFERENCE_MODES",
    "PHASE12K_AUTHORIZATION_STATUS",
    "PHASE12K_BACKEND_OPTION_LABELS",
    "PHASE12K_CAPABILITY_PHASE",
    "PHASE12K_CREDENTIAL_POLICY",
    "PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_CONTRACT_VERSION",
    "PHASE12K_EXTERNAL_COMPUTE_QUANTUM_PROFILE_KIND",
    "PHASE12K_GRANT_STATUS",
    "PHASE12K_REQUIRED_FUTURE_GATES",
    "PHASE12K_SOURCE_PHASE_RANGE",
    "PHASE12K_STATUS_LABELS",
    "PHASE12K_WORKLOAD_CLASSES",
    "PHASE12L_A2A_TRANSPORT_STATUS",
    "PHASE12L_AUTHORIZATION_STATUS",
    "PHASE12L_CAPABILITY_PHASE",
    "PHASE12L_CREDENTIAL_POLICY",
    "PHASE12L_FABRIC_CAPABILITY_LABELS",
    "PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_CONTRACT_VERSION",
    "PHASE12L_FABRIC_INTEROP_A2A_AUDIT_PROFILE_KIND",
    "PHASE12L_FABRIC_INTEROP_STATUS",
    "PHASE12L_FORBIDDEN_OUT_OF_SCOPE_LABELS",
    "PHASE12L_GRANT_STATUS",
    "PHASE12L_MCP_INTEROP_STATUS",
    "PHASE12L_MESSAGE_CODEC_STATUS",
    "PHASE12L_REQUIRED_FUTURE_GATES",
    "PHASE12L_SECURE_DROP_STATUS",
    "PHASE12L_SOURCE_PHASE_RANGE",
    "PHASE12L_STATUS_LABELS",
    "PHASE12M_AUTHORIZATION_STATUS",
    "PHASE12M_CANDIDATE_LABELS",
    "PHASE12M_GRANT_STATUS",
    "PHASE12M_MODEL_OPTION_CATEGORIES",
    "PHASE12M_MODEL_OPTION_PROFILE_PHASE",
    "PHASE12M_REQUIRED_FUTURE_GATES",
    "PHASE12M_SOURCE_PHASE_RANGE",
    "PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_CONTRACT_VERSION",
    "PHASE12M_SPECIALIZED_MODEL_OPTION_REGISTRY_PROFILE_KIND",
    "PHASE12M_STATUS_LABELS",
    "PHASE12N_AUTHORIZATION_STATUS",
    "PHASE12N_FUSION_CONCEPT_LABELS",
    "PHASE12N_GRANT_STATUS",
    "PHASE12N_REQUIRED_FUTURE_GATES",
    "PHASE12N_SCIENTIST_EVOLUTION_CONCEPT_LABELS",
    "PHASE12N_SOURCE_PHASE_RANGE",
    "PHASE12N_STATUS_LABELS",
    "PHASE12N_WORKFLOW_MODE_PROFILE_PHASE",
    "PHASE12N_WORKFLOW_MODES",
    "PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_CONTRACT_VERSION",
    "PHASE12N_WORKFLOW_ORCHESTRATION_MODE_REGISTRY_PROFILE_KIND",
    "PHASE12O_AUTHORIZATION_STATUS",
    "PHASE12O_GRANT_STATUS",
    "PHASE12O_MATRIX_PHASE",
    "PHASE12O_REQUIRED_FUTURE_GATES",
    "PHASE12O_SOURCE_PHASE",
    "PHASE12O_STATUS_LABELS",
    "PHASE12O_WORKFLOW_MODES",
    "PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_CONTRACT_VERSION",
    "PHASE12O_WORKFLOW_MODE_SAFETY_GATE_MATRIX_KIND",
    "PHASE12P_AUTHORIZATION_STATUS",
    "PHASE12P_GRANT_STATUS",
    "PHASE12P_PACKET_PHASE",
    "PHASE12P_REQUIRED_FUTURE_GATES",
    "PHASE12P_REQUIRED_REVIEWER_CLASSES",
    "PHASE12P_RISK_SUMMARY_PLACEHOLDERS",
    "PHASE12P_EVIDENCE_INVENTORY_PLACEHOLDERS",
    "PHASE12P_SOURCE_PHASE_RANGE",
    "PHASE12P_STATUS_LABELS",
    "PHASE12P_WORKFLOW_MODES",
    "PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_CONTRACT_VERSION",
    "PHASE12P_WORKFLOW_MODE_ACTIVATION_REQUEST_REVIEW_PACKET_KIND",
    "PHASE12Q_AUTHORIZATION_STATUS",
    "PHASE12Q_DECISION_RECORD_PHASE",
    "PHASE12Q_DECISION_REASON_CODES",
    "PHASE12Q_DECISION_STATUSES",
    "PHASE12Q_DEFAULT_DECISION_REASON_CODE",
    "PHASE12Q_DEFAULT_DECISION_STATUS",
    "PHASE12Q_GRANT_STATUS",
    "PHASE12Q_REQUIRED_FUTURE_GATES",
    "PHASE12Q_REQUIRED_REVIEWER_CLASSES",
    "PHASE12Q_SOURCE_PHASE_RANGE",
    "PHASE12Q_STATUS_LABELS",
    "PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_CONTRACT_VERSION",
    "PHASE12Q_WORKFLOW_MODE_REVIEW_DECISION_RECORD_KIND",
    "PHASE12Q_WORKFLOW_MODES",
    "PHASE12R_AUDIT_TRAIL_INDEX_PHASE",
    "PHASE12R_AUTHORIZATION_STATUS",
    "PHASE12R_GRANT_STATUS",
    "PHASE12R_REQUIRED_FUTURE_GATES",
    "PHASE12R_REQUIRED_REVIEWER_CLASSES",
    "PHASE12R_SOURCE_PHASE_RANGE",
    "PHASE12R_STATUS_LABELS",
    "PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_CONTRACT_VERSION",
    "PHASE12R_WORKFLOW_MODE_REVIEW_AUDIT_TRAIL_INDEX_KIND",
    "PHASE12R_WORKFLOW_MODES",
    "PHASE12S_AUTHORIZATION_STATUS",
    "PHASE12S_CLOSEOUT_STATUSES",
    "PHASE12S_CLOSEOUT_SUMMARY_PHASE",
    "PHASE12S_DEFAULT_CLOSEOUT_STATUS",
    "PHASE12S_GRANT_STATUS",
    "PHASE12S_REQUIRED_FUTURE_GATES",
    "PHASE12S_SOURCE_PHASE_RANGE",
    "PHASE12S_STATUS_LABELS",
    "PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT_VERSION",
    "PHASE12S_WORKFLOW_MODE_REVIEW_CHAIN_CLOSEOUT_SUMMARY_KIND",
    "PHASE12S_WORKFLOW_MODES",
    "Phase12ARuntimeAuthorizationDesignCharterValidationResult",
    "Phase12BRuntimeAuthorizationRecordCandidateValidationResult",
    "Phase12CVisualSupervisionCapabilityProfileValidationResult",
    "Phase12DConsentGateRequirementsValidationResult",
    "Phase12EPhysiologicalSensorCapabilityProfileValidationResult",
    "Phase12FSecureDropConsumerBoundaryValidationResult",
    "Phase12GProductionReadinessCoverageMatrixValidationResult",
    "Phase12HSomaticStandaloneProductionReadinessOwnershipMapValidationResult",
    "Phase12IIntegrativeHerbalNutritionKnowledgeCapabilityProfileValidationResult",
    "Phase12KExternalComputeQuantumBackendCapabilityProfileValidationResult",
    "Phase12LFabricInteropA2AAuditBoundaryCapabilityProfileValidationResult",
    "Phase12MSpecializedModelOptionRegistryCapabilityProfileValidationResult",
    "Phase12NWorkflowOrchestrationModeRegistryCapabilityProfileValidationResult",
    "Phase12OWorkflowModeSafetyGateRuntimePrerequisiteMatrixValidationResult",
    "Phase12PWorkflowModeActivationRequestReviewPacketValidationResult",
    "Phase12QWorkflowModeReviewDecisionRecordValidationResult",
    "Phase12RWorkflowModeReviewAuditTrailIndexValidationResult",
    "Phase12SWorkflowModeReviewChainCloseoutSummaryValidationResult",
    "phase12a_runtime_authorization_design_charter",
    "phase12a_runtime_authorization_design_charter_status_summary",
    "phase12b_runtime_authorization_record_candidate",
    "phase12b_runtime_authorization_record_candidate_status_summary",
    "phase12c_visual_supervision_capability_profile",
    "phase12c_visual_supervision_capability_profile_status_summary",
    "phase12d_visual_desktop_consent_gate_requirements",
    "phase12d_visual_desktop_consent_gate_requirements_status_summary",
    "phase12e_physiological_sensor_capability_profile",
    "phase12e_physiological_sensor_capability_profile_status_summary",
    "phase12f_secure_drop_consumer_boundary",
    "phase12f_secure_drop_consumer_boundary_status_summary",
    "phase12g_production_readiness_coverage_matrix",
    "phase12g_production_readiness_coverage_matrix_status_summary",
    "phase12h_somatic_standalone_production_readiness_ownership_map",
    "phase12h_somatic_standalone_production_readiness_ownership_map_status_summary",
    "phase12i_integrative_herbal_nutrition_knowledge_capability_profile",
    "phase12i_integrative_herbal_nutrition_knowledge_capability_profile_status_summary",
    "phase12k_external_compute_quantum_backend_capability_profile",
    "phase12k_external_compute_quantum_backend_capability_profile_status_summary",
    "phase12l_fabric_interop_a2a_audit_boundary_capability_profile",
    "phase12l_fabric_interop_a2a_audit_boundary_capability_profile_status_summary",
    "phase12m_specialized_model_option_registry_capability_profile",
    "phase12m_specialized_model_option_registry_capability_profile_status_summary",
    "phase12n_workflow_orchestration_mode_registry_capability_profile",
    "phase12n_workflow_orchestration_mode_registry_capability_profile_status_summary",
    "phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix",
    "phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix_status_summary",
    "phase12p_workflow_mode_activation_request_review_packet_boundary",
    "phase12p_workflow_mode_activation_request_review_packet_boundary_status_summary",
    "phase12q_non_authorizing_workflow_mode_review_decision_record",
    "phase12q_non_authorizing_workflow_mode_review_decision_record_status_summary",
    "phase12r_workflow_mode_review_audit_trail_index",
    "phase12r_workflow_mode_review_audit_trail_index_status_summary",
    "phase12s_workflow_mode_review_chain_closeout_summary",
    "phase12s_workflow_mode_review_chain_closeout_summary_status_summary",
    "rejected_phase12a_runtime_authorization_design_charter",
    "rejected_phase12b_runtime_authorization_record_candidate",
    "rejected_phase12c_visual_supervision_capability_profile",
    "rejected_phase12d_visual_desktop_consent_gate_requirements",
    "rejected_phase12e_physiological_sensor_capability_profile",
    "rejected_phase12f_secure_drop_consumer_boundary",
    "rejected_phase12g_production_readiness_coverage_matrix",
    "rejected_phase12h_somatic_standalone_production_readiness_ownership_map",
    "rejected_phase12i_integrative_herbal_nutrition_knowledge_capability_profile",
    "rejected_phase12k_external_compute_quantum_backend_capability_profile",
    "rejected_phase12l_fabric_interop_a2a_audit_boundary_capability_profile",
    "rejected_phase12m_specialized_model_option_registry_capability_profile",
    "rejected_phase12n_workflow_orchestration_mode_registry_capability_profile",
    "rejected_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix",
    "rejected_phase12p_workflow_mode_activation_request_review_packet_boundary",
    "rejected_phase12q_workflow_mode_review_decision_record",
    "rejected_phase12r_workflow_mode_review_audit_trail_index",
    "rejected_phase12s_workflow_mode_review_chain_closeout_summary",
    "validate_phase12a_runtime_authorization_design_charter",
    "validate_phase12b_runtime_authorization_record_candidate",
    "validate_phase12c_visual_supervision_capability_profile",
    "validate_phase12d_visual_desktop_consent_gate_requirements",
    "validate_phase12e_physiological_sensor_capability_profile",
    "validate_phase12f_secure_drop_consumer_boundary",
    "validate_phase12g_production_readiness_coverage_matrix",
    "validate_phase12h_somatic_standalone_production_readiness_ownership_map",
    "validate_phase12i_integrative_herbal_nutrition_knowledge_capability_profile",
    "validate_phase12k_external_compute_quantum_backend_capability_profile",
    "validate_phase12l_fabric_interop_a2a_audit_boundary_capability_profile",
    "validate_phase12m_specialized_model_option_registry_capability_profile",
    "validate_phase12n_workflow_orchestration_mode_registry_capability_profile",
    "validate_phase12o_workflow_mode_safety_gate_runtime_prerequisite_matrix",
    "validate_phase12p_workflow_mode_activation_request_review_packet_boundary",
    "validate_phase12q_non_authorizing_workflow_mode_review_decision_record",
    "validate_phase12r_workflow_mode_review_audit_trail_index",
    "validate_phase12s_workflow_mode_review_chain_closeout_summary",
]

install_builder_cache(globals())
