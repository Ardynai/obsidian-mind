# Phase 12M Specialized Model Option Registry Capability Profile

Phase 12M is a non-executing metadata-only capability profile for future
selectable model roles beyond general LLMs. It records possible future labels
for medical models, scientific generative models, time-series and sensor
models, CSI/RF models, BIA/acoustic/ultrasound models, optimization engines,
evidence-grading models, and safety-gate models.

This phase is docs, contracts, fixtures, tests, and status metadata only. It
does not implement model execution, provider execution, model loading, training,
fine-tuning, database ingestion, web scraping, network calls, runtime adapters,
active grants, real-mode authorization, clinical decision support, diagnosis,
treatment planning, medical advice, herb or supplement dosing, calorie or macro
prescription, or nutrition prescription.

## Contract

- `profile_kind: phase-12m-specialized-model-option-registry-capability-profile`
- `specialized_model_option_registry_profile_contract_version: 1`
- `source_phase_range: 12A-12L,evidence-sensor-model-safety-boundaries`
- `model_option_profile_phase: metadata-only`
- `authorization_status: not-authorized`
- `grant_status: no-grant`
- `runtime_stage: not-implemented`
- `execution_permitted: false`
- `real_mode_runtime_enabled: false`
- `model_execution_permitted: false`
- `provider_execution_permitted: false`
- `training_permitted: false`
- `fine_tuning_permitted: false`
- `clinical_decision_support_allowed: false`
- `diagnosis_or_treatment_allowed: false`
- `private_health_data_allowed: false`

## Future Model-Option Categories

The category labels are selectable metadata only:

- `medical-language-model`
- `medical-multimodal-model`
- `medical-safety-reviewer-model`
- `scientific-generative-model`
- `protein-structure-model`
- `ligand-binding-model`
- `reaction-material-model`
- `herbal-interaction-safety-model`
- `nutrition-risk-safety-model`
- `time-series-foundation-model`
- `csi-rf-signal-model`
- `bia-metabolic-trend-model`
- `acoustic-ultrasound-body-map-model`
- `active-learning-optimization-engine`
- `bayesian-optimization-engine`
- `evidence-grading-model`
- `contraindication-toxicity-reviewer`
- `emergency-escalation-classifier`

## Candidate Labels

The candidate labels are also metadata only:

- `Med-Gemini-style-medical-multimodal-model`
- `MedGemma-style-medical-open-weight-model`
- `Meditron-BioMistral-style-medical-language-model`
- `LOGOS-style-scientific-generative-model`
- `AlphaFold-Boltz-ESM-style-structure-model`
- `Kronos-like-time-series-model`
- `Chronos-MOMENT-Kairos-style-time-series-model`
- `CSI-RF-signal-model`
- `BIA-trend-model`
- `acoustic-ultrasound-body-map-model`
- `ALchemist-style-Bayesian-optimization-engine`
- `herb-drug-interaction-safety-model`
- `supplement-drug-interaction-safety-model`
- `nutrition-risk-safety-model`
- `emergency-escalation-classifier`
- `contraindication-toxicity-reviewer`

These labels do not mean any model, specialist, provider, runtime, clinical,
diagnosis, or treatment capability is enabled, configured, available, trained,
fine-tuned, ready, approved, authorized, or executable from Somatic.

## Required Future Gates

- model-source-provenance-review
- model-license-review
- clinical-safety-boundary-review
- medical-model-validation-review
- sensor-model-validation-review
- csi-rf-privacy-review
- bias-and-evidence-quality-review
- herb-drug-interaction-safety-review
- nutrition-safety-review
- private-health-data-boundary-review
- model-runtime-authorization-review
- jules-security-medical-safety-review-for-validator-or-safety-semantics-changes

The last gate records the required Jules/security/medical-safety review for
validator or safety semantics changes.

## Boundary Statements

Phase 12M names future specialized model options only. It performs no model
loading, model execution, provider execution, training, fine-tuning, network
call, database ingestion, web scraping, runtime adapter, active grant, or
real-mode authorization.

Medical model labels cannot provide diagnosis, treatment planning, medical
advice, prescribing, clinical decision support, herb or supplement dosing,
calorie or macro prescription, or nutrition prescription.

CSI/RF, BIA, acoustic, and ultrasound model labels do not permit device access,
raw sensor processing, monitoring, diagnosis, or clinical decision support.

## Validation Stance

Validation fails closed on missing fields, unsupported versions, unknown fields,
non-integer counts, unsafe/private values, source/device/router IDs, raw
document/CSI/RF/BIA/acoustic/ultrasound payloads, API keys, env vars, vault
references, URLs with tokens, model execution, provider execution, model
loading, training, fine-tuning, database ingestion, web scraping, network calls,
runtime adapters, active grants, real-mode authorization, clinical
recommendations, diagnosis, treatment planning, medical advice, prescribing,
herb or supplement dosing, calorie or macro prescription, nutrition
prescription, private health-data processing, device access, raw sensor
processing, monitoring, and production-ready claims.
