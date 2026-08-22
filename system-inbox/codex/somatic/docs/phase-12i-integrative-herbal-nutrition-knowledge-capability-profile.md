# Phase 12I Integrative, Herbal, And Nutrition Knowledge Capability Profile

Phase 12I is a non-executing knowledge capability profile. It defines future
metadata-only support for integrative review, traditional medicine informed
review, herbal safety review, nutrition review, metabolic-health review, and
credentialed practitioner source classes while preserving strict medical safety
boundaries.

This phase is docs, metadata, fixtures, contracts, and tests only. It does not
provide medical advice, diagnosis, clinical decision support, treatment
planning, prescribing, herb dosing, supplement dosing, calorie or macro
prescription, weight-loss target prescription, provider/model execution,
database ingestion, web scraping, network calls, runtime adapters, active
grants, or real-mode authorization.

## Contract

- `profile_kind: phase-12i-integrative-herbal-nutrition-knowledge-capability-profile`
- `integrative_herbal_nutrition_profile_contract_version: 1`
- `source_phase_range: 12A-12H,evidence-sensor-safety-boundaries`
- `capability_phase: knowledge-profile-only`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`

## Metadata Labels

Phase 12I includes metadata-only labels for user preference modes, specialist
review profiles, source classes, and required future gates. These labels do not
create recommendations, approvals, grants, provider execution, source ingestion,
or runtime behavior.

User preference modes include natural-first, traditional-medicine-first,
nutrition-first, food-as-medicine-informed, plant-based, animal-based,
mediterranean, low-carb, keto-informed, elimination-diet-informed,
culturally-specific-diet, tcm-informed-review, herbalist-informed-review,
integrative-review, and western-medicine-minimized.

Specialist review profile labels include traditional-medicine-reviewer,
herbal-safety-reviewer, integrative-medicine-reviewer,
natural-preference-review-profile, nutrition-safety-reviewer,
metabolic-health-reviewer, dietary-pattern-reviewer, supplement-safety-reviewer,
and integrative-nutrition-reviewer.

Source class labels include traditional chinese materia medica, herbal formula
reference, pharmacognosy reference, herb-drug interaction reference, botanical
identity/adulteration reference, herbal safety/toxicity monograph, integrative
medicine clinical literature, ethnobotany reference, user-provided practitioner
note, registered-dietitian reference, clinical-nutrition guideline,
nutrition-database reference, food-composition database, micronutrient
reference, supplement-safety monograph, herb-supplement interaction reference,
metabolic-health literature, user-provided meal log, and user-provided lab
report.

## Safety Boundaries

- Phase 12I does not claim Western medicine is invalid.
- Phase 12I does not claim natural remedies are safe by default.
- Phase 12I does not claim food cures disease.
- User preference modes cannot suppress emergency escalation, contraindication
  warnings, medication interaction warnings, pregnancy/liver/kidney/cardiac risk
  warnings, eating-disorder risk warnings, toxicity warnings, or
  contamination/adulteration warnings.
- Source classes require provenance review before any future use.
- Any validator or medical safety semantics change requires Jules/human review.

## Required Future Gates

- source-provenance-review
- clinical-safety-boundary-review
- herb-drug-interaction-review
- supplement-drug-interaction-review
- contraindication-toxicity-review
- botanical-identity-adulteration-review
- nutrition-safety-review
- eating-disorder-risk-review
- pregnancy-liver-kidney-cardiac-risk-review
- user-preference-consent
- evidence-grading-policy
- emergency-escalation-preservation
- jules-human-review-for-validator-or-medical-safety-semantics-changes

## Validation Stance

Validation fails closed on missing fields, unsupported versions, unknown fields,
unsafe/private values, URLs, absolute paths, API keys, env vars, vault
references, source/device/router IDs, raw document/CSI/RF/sensor payloads,
screenshots, raw OCR, medical action claims, runtime-enabled claims,
database-ingestion claims, web-scraping claims, provider/model execution claims,
dosing claims, nutrition prescription claims, unsafe fasting or weight-loss
advice claims, active grant claims, and real-mode authorization claims.
