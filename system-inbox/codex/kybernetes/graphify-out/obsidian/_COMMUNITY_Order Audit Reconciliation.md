---
type: community
cohesion: 0.06
members: 57
---

# Order Audit Reconciliation

**Cohesion:** 0.06 - loosely connected
**Members:** 57 nodes

## Members
- [[.getOrderByClientOrderId()_2]] - code - src/lib/safety/receipts.ts
- [[AuditWriter]] - code - src/lib/safety/receipts.ts
- [[ExecutionAckReceipt]] - code - src/lib/safety/receipts.ts
- [[ExecutionCancelledReceipt]] - code - src/lib/safety/receipts.ts
- [[ExecutionFillReceipt]] - code - src/lib/safety/receipts.ts
- [[ExecutionReceipt]] - code - src/lib/safety/receipts.ts
- [[ExecutionReceiptBase]] - code - src/lib/safety/receipts.ts
- [[ExecutionReceiptState]] - code - src/lib/safety/receipts.ts
- [[ExecutionReceiptSummary]] - code - src/lib/safety/receipts.ts
- [[GatewayHasSubmit]] - code - src/lib/safety/receipts.test.ts
- [[LedgerLoader]] - code - src/lib/safety/receipts.ts
- [[RECONCILED_ACCEPTED_STATUSES]] - code - src/lib/safety/receipts.ts
- [[RECONCILIATION_DISCREPANCY_KINDS]] - code - src/lib/safety/receipts.ts
- [[ReceiptLoader]] - code - src/lib/safety/receipts.ts
- [[ReceiptSource]] - code - src/lib/safety/receipts.ts
- [[ReceiptWriter]] - code - src/lib/safety/receipts.ts
- [[ReconcileRequest]] - code - src/lib/safety/receipts.ts
- [[ReconciliationBrokerOrder]] - code - src/lib/safety/receipts.ts
- [[ReconciliationDiscrepancy]] - code - src/lib/safety/receipts.ts
- [[ReconciliationDiscrepancyKind]] - code - src/lib/safety/receipts.ts
- [[ReconciliationGateway]] - code - src/lib/safety/receipts.ts
- [[ReconciliationResult]] - code - src/lib/safety/receipts.ts
- [[acceptedReceipt()]] - code - src/lib/safety/receipts.test.ts
- [[alpacaAuditEvent()]] - code - src/lib/safety/receipts.test.ts
- [[alpacaFlattenAuditRef()]] - code - src/lib/safety/receipts.test.ts
- [[appendReconciledSubmission()]] - code - src/lib/safety/receipts.ts
- [[assertIdentifier()]] - code - src/lib/safety/receipts.ts
- [[assertPositiveFinite()]] - code - src/lib/safety/receipts.ts
- [[auditEvent()_1]] - code - src/lib/safety/receipts.test.ts
- [[brokerOrderMatchesAudit()]] - code - src/lib/safety/receipts.ts
- [[canonicalBrokerTimestamp()]] - code - src/lib/safety/receipts.ts
- [[collectOrderAudit()]] - code - src/lib/safety/receipts.ts
- [[compareBrokerAndReceipts()]] - code - src/lib/safety/receipts.ts
- [[compareReceipts()]] - code - src/lib/safety/receipts.ts
- [[flattenAuditEvent()]] - code - src/lib/safety/receipts.test.ts
- [[get()_3]] - code - src/lib/safety/receipts.test.ts
- [[groupReceipts()]] - code - src/lib/safety/receipts.ts
- [[ledger()]] - code - src/lib/safety/receipts.test.ts
- [[loadExecutionReceipts()]] - code - src/lib/safety/receipts.ts
- [[memoryCompatibilityEnabled()]] - code - src/lib/safety/receipts.ts
- [[nullableDatabaseString()]] - code - src/lib/safety/receipts.ts
- [[observedReceiptId()]] - code - src/lib/safety/receipts.ts
- [[partialAuditIdentity()]] - code - src/lib/safety/receipts.ts
- [[persistExecutionReceipt()]] - code - src/lib/safety/receipts.ts
- [[persistObservedBrokerReceipts()]] - code - src/lib/safety/receipts.ts
- [[persistReconciledAcceptedReceipt()]] - code - src/lib/safety/receipts.ts
- [[receiptFromRow()]] - code - src/lib/safety/receipts.ts
- [[receiptMemoryGlobal]] - code - src/lib/safety/receipts.ts
- [[receiptState()]] - code - src/lib/safety/receipts.test.ts
- [[receipts.test.ts]] - code - src/lib/safety/receipts.test.ts
- [[receipts.ts]] - code - src/lib/safety/receipts.ts
- [[reconcile()]] - code - src/lib/safety/receipts.ts
- [[reconciliationEventId()]] - code - src/lib/safety/receipts.ts
- [[sameAuditedOrder()]] - code - src/lib/safety/receipts.ts
- [[summarizeExecutionReceipts()]] - code - src/lib/safety/receipts.ts
- [[uniqueDiscrepancies()]] - code - src/lib/safety/receipts.ts
- [[validateReceipt()]] - code - src/lib/safety/receipts.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Order_Audit_Reconciliation
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 10 edges to [[_COMMUNITY_Safety Control Actions]]
- 5 edges to [[_COMMUNITY_Order Simulation Testing]]
- 4 edges to [[_COMMUNITY_Database Policy Management]]
- 4 edges to [[_COMMUNITY_Broker Credential Controls]]
- 3 edges to [[_COMMUNITY_Broker Order Safety]]
- 1 edge to [[_COMMUNITY_Ledger Memory Reservations]]
- 1 edge to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 1 edge to [[_COMMUNITY_Strategy Backtesting UI]]

## Top bridge nodes
- [[receipts.ts]] - degree 65, connects to 9 communities
- [[loadExecutionReceipts()]] - degree 17, connects to 4 communities
- [[receipts.test.ts]] - degree 26, connects to 3 communities
- [[persistExecutionReceipt()]] - degree 10, connects to 3 communities
- [[reconcile()]] - degree 17, connects to 1 community