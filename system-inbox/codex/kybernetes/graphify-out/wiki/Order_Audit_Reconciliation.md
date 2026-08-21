# Order Audit Reconciliation

> 57 nodes · cohesion 0.06

## Key Concepts

- **receipts.ts** (65 connections) — `src/lib/safety/receipts.ts`
- **receipts.test.ts** (26 connections) — `src/lib/safety/receipts.test.ts`
- **loadExecutionReceipts()** (17 connections) — `src/lib/safety/receipts.ts`
- **reconcile()** (17 connections) — `src/lib/safety/receipts.ts`
- **persistExecutionReceipt()** (10 connections) — `src/lib/safety/receipts.ts`
- **assertIdentifier()** (7 connections) — `src/lib/safety/receipts.ts`
- **collectOrderAudit()** (6 connections) — `src/lib/safety/receipts.ts`
- **validateReceipt()** (6 connections) — `src/lib/safety/receipts.ts`
- **ExecutionReceiptBase** (4 connections) — `src/lib/safety/receipts.ts`
- **groupReceipts()** (4 connections) — `src/lib/safety/receipts.ts`
- **persistObservedBrokerReceipts()** (4 connections) — `src/lib/safety/receipts.ts`
- **persistReconciledAcceptedReceipt()** (4 connections) — `src/lib/safety/receipts.ts`
- **receiptFromRow()** (4 connections) — `src/lib/safety/receipts.ts`
- **canonicalBrokerTimestamp()** (3 connections) — `src/lib/safety/receipts.ts`
- **compareBrokerAndReceipts()** (3 connections) — `src/lib/safety/receipts.ts`
- **ExecutionReceipt** (3 connections) — `src/lib/safety/receipts.ts`
- **ExecutionReceiptState** (3 connections) — `src/lib/safety/receipts.ts`
- **memoryCompatibilityEnabled()** (3 connections) — `src/lib/safety/receipts.ts`
- **observedReceiptId()** (3 connections) — `src/lib/safety/receipts.ts`
- **partialAuditIdentity()** (3 connections) — `src/lib/safety/receipts.ts`
- **ReconciliationBrokerOrder** (3 connections) — `src/lib/safety/receipts.ts`
- **ReconciliationGateway** (3 connections) — `src/lib/safety/receipts.ts`
- **summarizeExecutionReceipts()** (3 connections) — `src/lib/safety/receipts.ts`
- **appendReconciledSubmission()** (2 connections) — `src/lib/safety/receipts.ts`
- **assertPositiveFinite()** (2 connections) — `src/lib/safety/receipts.ts`
- *... and 32 more nodes in this community*

## Relationships

- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (19 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (10 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (5 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (4 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (4 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (3 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (1 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (1 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (1 shared connections)

## Source Files

- `src/lib/safety/receipts.test.ts`
- `src/lib/safety/receipts.ts`

## Audit Trail

- EXTRACTED: 246 (97%)
- INFERRED: 8 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*