# Blackboard Build Logic

> 17 nodes · cohesion 0.26

## Key Concepts

- **team_orchestrator.py** (16 connections) — `somatic/agents/team_orchestrator.py`
- **run_team_orchestrator()** (10 connections) — `somatic/agents/team_orchestrator.py`
- **_build_team_record()** (7 connections) — `somatic/agents/team_orchestrator.py`
- **_build_summary()** (6 connections) — `somatic/agents/team_orchestrator.py`
- **_build_csi_readiness()** (4 connections) — `somatic/agents/team_orchestrator.py`
- **_build_reorganization_log()** (4 connections) — `somatic/agents/team_orchestrator.py`
- **_reorganization_trigger()** (4 connections) — `somatic/agents/team_orchestrator.py`
- **_build_team_roster()** (3 connections) — `somatic/agents/team_orchestrator.py`
- **_critique_gate_result()** (3 connections) — `somatic/agents/team_orchestrator.py`
- **_stall_summary()** (3 connections) — `somatic/agents/team_orchestrator.py`
- **_build_blackboard()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_build_evidence_budget()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_build_team_critiques()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_confidence_estimate()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_evidence_spend_decision()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_focus_hypothesis_ids()** (2 connections) — `somatic/agents/team_orchestrator.py`
- **_stall_status()** (2 connections) — `somatic/agents/team_orchestrator.py`

## Relationships

- [CSI Batch Readiness](CSI_Batch_Readiness.md) (1 shared connections)
- [CSI Data Parsing](CSI_Data_Parsing.md) (1 shared connections)
- [Hypothesis Tournament Management](Hypothesis_Tournament_Management.md) (1 shared connections)
- [Team Orchestrator Mocking](Team_Orchestrator_Mocking.md) (1 shared connections)

## Source Files

- `somatic/agents/team_orchestrator.py`

## Audit Trail

- EXTRACTED: 70 (95%)
- INFERRED: 4 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*