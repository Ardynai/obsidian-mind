# Order Simulation Testing

> 20 nodes · cohesion 0.14

## Key Concepts

- **runs.test.ts** (39 connections) — `src/lib/runs/runs.test.ts`
- **backtest.test.ts** (19 connections) — `src/lib/backtest/backtest.test.ts`
- **OhlcBar** (14 connections) — `src/lib/bots/types.ts`
- **resetExecutionReceiptsForTests()** (6 connections) — `src/lib/safety/receipts.ts`
- **resetSafetyForTests()** (5 connections) — `src/lib/safety/index.ts`
- **OhlcResult** (4 connections) — `src/lib/data/ohlc.ts`
- **emptyResult()** (4 connections) — `src/lib/runs/runs.test.ts`
- **groupBySymbol()** (3 connections) — `src/lib/bots/adapters/fynn.ts`
- **bar()** (3 connections) — `src/lib/runs/runs.test.ts`
- **twoOrderResult()** (3 connections) — `src/lib/runs/runs.test.ts`
- **createOrderCapableStub()** (2 connections) — `src/lib/backtest/backtest.test.ts`
- **createOrderEmittingStub()** (2 connections) — `src/lib/backtest/backtest.test.ts`
- **SafetyOrderProcessor** (2 connections) — `src/lib/runs/index.ts`
- **oneOrderResult()** (2 connections) — `src/lib/runs/runs.test.ts`
- **recordingAdapter()** (2 connections) — `src/lib/runs/runs.test.ts`
- **unsortedReplayResult()** (2 connections) — `src/lib/runs/runs.test.ts`
- **baseRequest()** (1 connections) — `src/lib/runs/runs.test.ts`
- **dataLoader()** (1 connections) — `src/lib/runs/runs.test.ts`
- **PRE_B2_FIXTURE_BASELINE** (1 connections) — `src/lib/runs/runs.test.ts`
- **toDeterminismSurface()** (1 connections) — `src/lib/runs/runs.test.ts`

## Relationships

- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (7 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (7 shared connections)
- [Strategy Backtesting UI](Strategy_Backtesting_UI.md) (6 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (6 shared connections)
- [Research Signal Generation](Research_Signal_Generation.md) (5 shared connections)
- [Mirofish Integration Testing](Mirofish_Integration_Testing.md) (5 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (5 shared connections)
- [Order Audit Reconciliation](Order_Audit_Reconciliation.md) (5 shared connections)
- [OHLC Data Processing](OHLC_Data_Processing.md) (5 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (5 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (4 shared connections)
- [Fynn Risk Reporting](Fynn_Risk_Reporting.md) (2 shared connections)

## Source Files

- `src/lib/backtest/backtest.test.ts`
- `src/lib/bots/adapters/fynn.ts`
- `src/lib/bots/types.ts`
- `src/lib/data/ohlc.ts`
- `src/lib/runs/index.ts`
- `src/lib/runs/runs.test.ts`
- `src/lib/safety/index.ts`
- `src/lib/safety/receipts.ts`

## Audit Trail

- EXTRACTED: 113 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*