---
source_file: "src/lib/safety/receipts.ts"
type: "code"
community: "Order Audit Reconciliation"
location: "L267"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Order_Audit_Reconciliation
---

# reconcile()

## Connections
- [[.getOrderByClientOrderId()_2]] - `calls` [EXTRACTED]
- [[RECONCILED_ACCEPTED_STATUSES]] - `references` [EXTRACTED]
- [[ReconcileRequest]] - `references` [EXTRACTED]
- [[appendReconciledSubmission()]] - `calls` [EXTRACTED]
- [[assertIdentifier()]] - `calls` [EXTRACTED]
- [[brokerOrderMatchesAudit()]] - `calls` [EXTRACTED]
- [[collectOrderAudit()]] - `calls` [EXTRACTED]
- [[compareBrokerAndReceipts()]] - `calls` [EXTRACTED]
- [[groupReceipts()]] - `calls` [EXTRACTED]
- [[index.ts_15]] - `imports` [EXTRACTED]
- [[persistObservedBrokerReceipts()]] - `calls` [EXTRACTED]
- [[persistReconciledAcceptedReceipt()]] - `calls` [EXTRACTED]
- [[receipts.test.ts]] - `imports` [EXTRACTED]
- [[receipts.ts]] - `contains` [EXTRACTED]
- [[reconcileRuntime()]] - `calls` [EXTRACTED]
- [[reconciliationEventId()]] - `calls` [EXTRACTED]
- [[uniqueDiscrepancies()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Order_Audit_Reconciliation