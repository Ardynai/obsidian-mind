# Strategy Backtesting UI

> 80 nodes · cohesion 0.07

## Key Concepts

- **pipeline.ts** (42 connections) — `src/lib/strategy-author/pipeline.ts`
- **runner.ts** (38 connections) — `src/lib/backtest/runner.ts`
- **index.ts** (26 connections) — `src/lib/strategy-author/index.ts`
- **actions.ts** (23 connections) — `src/app/strategy/actions.ts`
- **pipeline.test.ts** (23 connections) — `src/lib/strategy-author/pipeline.test.ts`
- **index.ts** (21 connections) — `src/lib/backtest/index.ts`
- **runBacktest()** (16 connections) — `src/lib/backtest/runner.ts`
- **draftStrategy()** (14 connections) — `src/lib/strategy-author/pipeline.ts`
- **ohlc-store.ts** (11 connections) — `src/lib/backtest/ohlc-store.ts`
- **BacktestView** (11 connections) — `src/lib/backtest/view.ts`
- **certifyOwnedGeneratedBot()** (11 connections) — `src/lib/strategy-author/pipeline.ts`
- **actions.ts** (10 connections) — `src/app/backtest/actions.ts`
- **createGeneratedSmaAdapter()** (10 connections) — `src/lib/bots/adapters/generated/sa1-fixture-sma.ts`
- **readOwnedAdapterSource()** (10 connections) — `src/lib/strategy-author/workspace.ts`
- **backtest-form.tsx** (9 connections) — `src/app/backtest/backtest-form.tsx`
- **certifyOwnedFixtureAction()** (8 connections) — `src/app/strategy/actions.ts`
- **loadBacktestOhlc()** (8 connections) — `src/lib/backtest/ohlc-store.ts`
- **toBacktestView()** (8 connections) — `src/lib/backtest/runner.ts`
- **walk-forward.ts** (8 connections) — `src/lib/backtest/walk-forward.ts`
- **loadNlFixture()** (8 connections) — `src/lib/strategy-author/pipeline.ts`
- **promoteGeneratedToPaper()** (8 connections) — `src/lib/strategy-author/pipeline.ts`
- **workspace.ts** (8 connections) — `src/lib/strategy-author/workspace.ts`
- **startBacktestAction()** (7 connections) — `src/app/backtest/actions.ts`
- **promotePaperAction()** (7 connections) — `src/app/strategy/actions.ts`
- **page.tsx** (7 connections) — `src/app/strategy/page.tsx`
- *... and 55 more nodes in this community*

## Relationships

- [Fynn Adapter Conformance](Fynn_Adapter_Conformance.md) (15 shared connections)
- [Mirofish Integration Testing](Mirofish_Integration_Testing.md) (14 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (11 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (10 shared connections)
- [Database Policy Management](Database_Policy_Management.md) (9 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (7 shared connections)
- [Market Data Actions](Market_Data_Actions.md) (6 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (6 shared connections)
- [OHLC Data Processing](OHLC_Data_Processing.md) (5 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (5 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (4 shared connections)
- [Authentication Route Handlers](Authentication_Route_Handlers.md) (2 shared connections)

## Source Files

- `src/app/backtest/actions.ts`
- `src/app/backtest/backtest-form.tsx`
- `src/app/strategy/actions.ts`
- `src/app/strategy/page.tsx`
- `src/app/strategy/strategy-form.tsx`
- `src/lib/backtest/index.ts`
- `src/lib/backtest/ohlc-store.test.ts`
- `src/lib/backtest/ohlc-store.ts`
- `src/lib/backtest/runner.ts`
- `src/lib/backtest/view.ts`
- `src/lib/backtest/walk-forward.test.ts`
- `src/lib/backtest/walk-forward.ts`
- `src/lib/bots/adapters/generated/sa1-fixture-sma.ts`
- `src/lib/data/ohlc.ts`
- `src/lib/strategy-author/index.ts`
- `src/lib/strategy-author/llm.ts`
- `src/lib/strategy-author/pipeline.test.ts`
- `src/lib/strategy-author/pipeline.ts`
- `src/lib/strategy-author/validate.ts`
- `src/lib/strategy-author/workspace.ts`

## Audit Trail

- EXTRACTED: 548 (100%)
- INFERRED: 1 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*