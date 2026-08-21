---
source_file: "src/lib/safety/receipts.ts"
type: "code"
community: "Order Audit Reconciliation"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Order_Audit_Reconciliation
---

# receipts.ts

## Connections
- [[AuditWriter]] - `contains` [EXTRACTED]
- [[AuditedBrokerOrder]] - `imports` [EXTRACTED]
- [[ExecutionAckReceipt]] - `contains` [EXTRACTED]
- [[ExecutionCancelledReceipt]] - `contains` [EXTRACTED]
- [[ExecutionFillReceipt]] - `contains` [EXTRACTED]
- [[ExecutionReceipt]] - `contains` [EXTRACTED]
- [[ExecutionReceiptBase]] - `contains` [EXTRACTED]
- [[ExecutionReceiptState]] - `contains` [EXTRACTED]
- [[ExecutionReceiptSummary]] - `contains` [EXTRACTED]
- [[LedgerLoader]] - `contains` [EXTRACTED]
- [[LedgerState]] - `imports` [EXTRACTED]
- [[ProvenanceEvent_1]] - `imports` [EXTRACTED]
- [[RECONCILED_ACCEPTED_STATUSES]] - `contains` [EXTRACTED]
- [[RECONCILIATION_DISCREPANCY_KINDS]] - `contains` [EXTRACTED]
- [[ReceiptLoader]] - `contains` [EXTRACTED]
- [[ReceiptSource]] - `contains` [EXTRACTED]
- [[ReceiptWriter]] - `contains` [EXTRACTED]
- [[ReconcileRequest]] - `contains` [EXTRACTED]
- [[ReconciliationBrokerOrder]] - `contains` [EXTRACTED]
- [[ReconciliationDiscrepancy]] - `contains` [EXTRACTED]
- [[ReconciliationDiscrepancyKind]] - `contains` [EXTRACTED]
- [[ReconciliationGateway]] - `contains` [EXTRACTED]
- [[ReconciliationResult]] - `contains` [EXTRACTED]
- [[appendProvenanceEvent()]] - `imports` [EXTRACTED]
- [[appendReconciledSubmission()]] - `contains` [EXTRACTED]
- [[assertIdentifier()]] - `contains` [EXTRACTED]
- [[assertPositiveFinite()]] - `contains` [EXTRACTED]
- [[backtest.test.ts]] - `imports_from` [EXTRACTED]
- [[brokerOrderMatchesAudit()]] - `contains` [EXTRACTED]
- [[canonicalBrokerTimestamp()]] - `contains` [EXTRACTED]
- [[client.ts]] - `imports_from` [EXTRACTED]
- [[collectOrderAudit()]] - `contains` [EXTRACTED]
- [[compareBrokerAndReceipts()]] - `contains` [EXTRACTED]
- [[compareReceipts()]] - `contains` [EXTRACTED]
- [[groupReceipts()]] - `contains` [EXTRACTED]
- [[index.test.ts]] - `imports_from` [EXTRACTED]
- [[index.ts_12]] - `imports_from` [EXTRACTED]
- [[index.ts_15]] - `imports_from` [EXTRACTED]
- [[loadExecutionReceipts()]] - `contains` [EXTRACTED]
- [[loadLedger()]] - `imports` [EXTRACTED]
- [[memoryCompatibilityEnabled()]] - `contains` [EXTRACTED]
- [[nullableDatabaseString()]] - `contains` [EXTRACTED]
- [[observedReceiptId()]] - `contains` [EXTRACTED]
- [[openDatabase()]] - `imports` [EXTRACTED]
- [[order-audit.ts]] - `imports_from` [EXTRACTED]
- [[parseBrokerOrderAuditRef()]] - `imports` [EXTRACTED]
- [[partialAuditIdentity()]] - `contains` [EXTRACTED]
- [[persistExecutionReceipt()]] - `contains` [EXTRACTED]
- [[persistObservedBrokerReceipts()]] - `contains` [EXTRACTED]
- [[persistReconciledAcceptedReceipt()]] - `contains` [EXTRACTED]
- [[pipeline.test.ts]] - `imports_from` [EXTRACTED]
- [[receiptFromRow()]] - `contains` [EXTRACTED]
- [[receiptMemoryGlobal]] - `contains` [EXTRACTED]
- [[receipts.test.ts]] - `imports_from` [EXTRACTED]
- [[reconcile()]] - `contains` [EXTRACTED]
- [[reconciliationEventId()]] - `contains` [EXTRACTED]
- [[resetExecutionReceiptsForTests()]] - `contains` [EXTRACTED]
- [[runs.test.ts]] - `imports_from` [EXTRACTED]
- [[sameAuditedOrder()]] - `contains` [EXTRACTED]
- [[summarizeExecutionReceipts()]] - `contains` [EXTRACTED]
- [[types.ts_2]] - `imports_from` [EXTRACTED]
- [[types.ts_8]] - `imports_from` [EXTRACTED]
- [[uniqueDiscrepancies()]] - `contains` [EXTRACTED]
- [[unresolvedUnknownClientOrderIds()]] - `contains` [EXTRACTED]
- [[validateReceipt()]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Order_Audit_Reconciliation