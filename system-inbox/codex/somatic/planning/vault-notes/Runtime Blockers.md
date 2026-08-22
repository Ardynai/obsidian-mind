---
title: Somatic — Runtime Blockers
reviewer: Fable 5
last_updated: 2026-07-02
tags: [somatic, safety, runtime]
---

# Somatic — Runtime Blockers

Back to [[README]]. These must all remain OFF. Current status: **all blocked** (verified in status surfaces + tests).

## Hard blocks (must stay false / not-implemented)
- Runtime stage = `not-implemented`; `execution_permitted = false`; no active grants; `authorization_status = not-authorized`.
- No model/provider execution, routing, loading, training, fine-tuning.
- No code / shell / process execution; no experiment or autonomous experimentation.
- No web/network behavior (0 network imports in `somatic/` — verified). No DB ingestion/writes/queries. No cache/event-bus/pub-sub runtime.
- No clinical decision support, diagnosis, treatment planning, medical advice, dosing, nutrition prescription.
- No device access, raw sensor processing, private-health-data processing.
- No real-mode authorization, deployment readiness, or production readiness.

## Medical / integrative posture (12I is the sensitive surface)
Josh wants future capability in **Eastern/traditional medicine, herbal remedies, nutrition, "food as medicine."** Currently: **knowledge/metadata-only**, strongly fenced. 12I blocks (exact fragments in code): diagnosis/diagnose, treatment plan, prescribe/prescribing, herb/supplement dosing, calorie/macro prescription, unsafe fasting/weight-loss target, "food cures disease", and any suppression of emergency/contraindication/interaction/toxicity warnings. Preference metadata may exist; **prescription behavior must not**.
- **Future gate [G10]:** before any free-text medical/nutrition generation, require a *semantic* (not substring) output classifier — the current keyword scanner cannot catch paraphrased dosing/diagnosis.

## Fabric
Blocked until the Multiverse consumer prompt → [[Fabric Consumer Boundary]].

## What "unblocking" would require (future, not now)
Each capability needs its own explicit enablement + **[[Jules]]** security/medical-safety review before any code executes. None is authorized today.
