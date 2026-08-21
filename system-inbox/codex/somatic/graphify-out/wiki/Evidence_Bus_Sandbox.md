# Evidence Bus Sandbox

> 21 nodes · cohesion 0.11

## Key Concepts

- **Evidence Bus** (12 connections) — `somatic/evidence_bus/`
- **SandboxEvidenceSource** (8 connections) — `somatic/simulator/sandbox_source.py`
- **SandboxEvidenceSourceTests** (6 connections) — `tests/test_sandbox_source.py`
- **sandbox_source.py** (5 connections) — `somatic/simulator/sandbox_source.py`
- **.acquire()** (4 connections) — `somatic/simulator/sandbox_source.py`
- **EvidenceBusTests** (4 connections) — `tests/test_evidence_bus.py`
- **Master-plan runtime (sandbox)** (3 connections) — `docs/how-it-works/master-plan-runtime.md`
- **_payload_for_modality()** (2 connections) — `somatic/simulator/sandbox_source.py`
- **_stable_hash()** (2 connections) — `somatic/simulator/sandbox_source.py`
- **.test_rejects_unknown_modality()** (2 connections) — `tests/test_evidence_bus.py`
- **test_evidence_bus.py** (2 connections) — `tests/test_evidence_bus.py`
- **test_sandbox_source.py** (2 connections) — `tests/test_sandbox_source.py`
- **.test_supports_robin_modalities()** (2 connections) — `tests/test_sandbox_source.py`
- **SOMATIC — Master Plan (v2)** (2 connections) — `planning/SOMATIC_MASTER_PLAN.md`
- **Deterministic offline EvidenceSource for the Robin-shaped loop.** (1 connections) — `somatic/simulator/sandbox_source.py`
- **.test_declares_master_plan_modalities()** (1 connections) — `tests/test_evidence_bus.py`
- **.test_no_network_or_external_api_surfaces_in_sandbox_source()** (1 connections) — `tests/test_sandbox_source.py`
- **Master Plan** (1 connections) — `docs/master-plan.md`
- **Status Screenshot** (1 connections) — `docs/ui-screenshots/01-status.png`
- **Belief Ledger** (1 connections) — `planning/SOMATIC_MASTER_PLAN.md`
- **Science Harness** (1 connections) — `somatic/science/`

## Relationships

- [Evidence Measurement Planning](Evidence_Measurement_Planning.md) (7 shared connections)
- [Workflow Evidence Analysis](Workflow_Evidence_Analysis.md) (4 shared connections)
- [Sensor Evidence Records](Sensor_Evidence_Records.md) (2 shared connections)
- [Sensor Hardware Ingestion](Sensor_Hardware_Ingestion.md) (1 shared connections)
- [Biomodel Evidence Processing](Biomodel_Evidence_Processing.md) (1 shared connections)

## Source Files

- `docs/how-it-works/master-plan-runtime.md`
- `docs/master-plan.md`
- `docs/ui-screenshots/01-status.png`
- `planning/SOMATIC_MASTER_PLAN.md`
- `somatic/evidence_bus/`
- `somatic/science/`
- `somatic/simulator/sandbox_source.py`
- `tests/test_evidence_bus.py`
- `tests/test_sandbox_source.py`

## Audit Trail

- EXTRACTED: 53 (84%)
- INFERRED: 10 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*