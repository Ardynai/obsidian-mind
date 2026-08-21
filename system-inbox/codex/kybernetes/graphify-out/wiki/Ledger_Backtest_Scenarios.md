# Ledger Backtest Scenarios

> 36 nodes · cohesion 0.11

## Key Concepts

- **index.ts** (67 connections) — `src/lib/runs/index.ts`
- **runLedgerScenario()** (33 connections) — `src/lib/runs/index.ts`
- **loadLedger()** (32 connections) — `src/lib/ledger/index.ts`
- **remote-pipeline-smoke.test.ts** (12 connections) — `src/lib/runs/remote-pipeline-smoke.test.ts`
- **appendProvenanceEvents()** (10 connections) — `src/lib/ledger/index.ts`
- **event()** (9 connections) — `src/lib/alerts/alerts.test.ts`
- **page.tsx** (7 connections) — `src/app/backtest/page.tsx`
- **empty-window-provenance.test.ts** (7 connections) — `src/lib/data/empty-window-provenance.test.ts`
- **isCompletedReplay()** (6 connections) — `src/lib/runs/index.ts`
- **defaultRunMode()** (5 connections) — `src/lib/bots/index.ts`
- **toIntentId()** (5 connections) — `src/lib/runs/index.ts`
- **canonicalCollection()** (4 connections) — `src/lib/runs/index.ts`
- **pipelineEvents()** (4 connections) — `src/lib/runs/index.ts`
- **toOrderIntent()** (4 connections) — `src/lib/runs/index.ts`
- **BacktestPage()** (3 connections) — `src/app/backtest/page.tsx`
- **LedgerChildReservation** (3 connections) — `src/lib/ledger/types.ts`
- **LedgerRunReservationResult** (3 connections) — `src/lib/ledger/types.ts`
- **childReservationsForRun()** (3 connections) — `src/lib/runs/index.ts`
- **dataQualityProvenance()** (3 connections) — `src/lib/runs/index.ts`
- **isHarnessProvenanceEvent()** (3 connections) — `src/lib/runs/index.ts`
- **issueCodes()** (3 connections) — `src/lib/runs/index.ts`
- **jsonComparable()** (3 connections) — `src/lib/runs/index.ts`
- **RunRequest** (3 connections) — `src/lib/runs/index.ts`
- **stableJsonKey()** (3 connections) — `src/lib/runs/index.ts`
- **validateBotRunResultForSafety()** (3 connections) — `src/lib/runs/index.ts`
- *... and 11 more nodes in this community*

## Relationships

- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (21 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (13 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (11 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (11 shared connections)
- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (9 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (8 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (7 shared connections)
- [OHLC Data Processing](OHLC_Data_Processing.md) (6 shared connections)
- [Alert Notification System](Alert_Notification_System.md) (4 shared connections)
- [Risk Report Routes](Risk_Report_Routes.md) (4 shared connections)
- [Latency Probe Worker](Latency_Probe_Worker.md) (4 shared connections)
- [Remote Smoke Testing](Remote_Smoke_Testing.md) (4 shared connections)

## Source Files

- `src/app/backtest/page.tsx`
- `src/lib/alerts/alerts.test.ts`
- `src/lib/bots/index.ts`
- `src/lib/data/empty-window-provenance.test.ts`
- `src/lib/ledger/index.ts`
- `src/lib/ledger/types.ts`
- `src/lib/runs/index.ts`
- `src/lib/runs/remote-pipeline-smoke.test.ts`

## Audit Trail

- EXTRACTED: 246 (96%)
- INFERRED: 11 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*