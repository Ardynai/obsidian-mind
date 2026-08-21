---
source_file: "src/app/safety-actions.ts"
type: "code"
community: "Safety Control Actions"
location: "L83"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Safety_Control_Actions
---

# persistSafetyControlAudit()

## Connections
- [[appendProvenanceEvent()]] - `calls` [EXTRACTED]
- [[armAction()]] - `indirect_call` [INFERRED]
- [[disarmAction()]] - `indirect_call` [INFERRED]
- [[ensureLedgerRunHeader()]] - `calls` [EXTRACTED]
- [[flattenAction()]] - `indirect_call` [INFERRED]
- [[forceClearFlattenUnknownAction()]] - `indirect_call` [INFERRED]
- [[killSwitchAction()]] - `indirect_call` [INFERRED]
- [[safety-actions.ts]] - `contains` [EXTRACTED]
- [[safetyControlAuditRun()]] - `calls` [EXTRACTED]
- [[scheduleAlertForEvent()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Safety_Control_Actions