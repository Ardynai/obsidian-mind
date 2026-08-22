# N-of-1 And Reports

## Owns

The fake-backed local n-of-1 planning loop and report packet:

- `_run_n_of_1` in `somatic/mock_runtime.py`
- `somatic/memory/`
- `somatic/reports/n_of_1_packet.py`
- `somatic/reports/n_of_1_fabric_plan.py`
- `fixtures/workflows/valid-n-of-1.yaml`

## Main Flow

The n-of-1 mode builds artifacts in phases:

1. Sandbox sensor plan, observations, feature set, and evidence record.
2. Sanitized CSI parser report, parsed summary, and CSI evidence pack.
3. Fake personal profile, baseline graph, and baseline comparison.
4. Mock intervention tag, context, response plan, and ledger.
5. Fake follow-up observation window, sensor snapshot, response comparison, and response evaluation summary.
6. Consolidated report packet and planning-only private Fabric pack plan.

## Gotchas

- `_run_n_of_1` is the hardest-to-read function in the current repo. Follow the phase comments and avoid top-to-bottom edits unless you need the full artifact chain.
- Hashes are for reproducibility and provenance only. They are not authorization, signing, medical-record, or Fabric-publication proof.
- The mode is fake-backed, offline, local-only, and research-only. No real monitoring, scheduling, notification, recommendation, diagnosis, treatment, or emergency triage is created.

## Start Reading

Start at `_assert_n_of_1_workflow_gates`, then `_run_n_of_1`, then `build_n_of_1_report_packet`.
