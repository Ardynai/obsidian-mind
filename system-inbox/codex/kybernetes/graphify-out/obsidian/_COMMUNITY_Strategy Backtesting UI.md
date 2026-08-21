---
type: community
cohesion: 0.07
members: 80
---

# Strategy Backtesting UI

**Cohesion:** 0.07 - loosely connected
**Members:** 80 nodes

## Members
- [[BacktestFoldResult]] - code - src/lib/backtest/runner.ts
- [[BacktestFoldView]] - code - src/lib/backtest/view.ts
- [[BacktestForm()]] - code - src/app/backtest/backtest-form.tsx
- [[BacktestReport]] - code - src/lib/backtest/runner.ts
- [[BacktestReportView()]] - code - src/app/backtest/backtest-form.tsx
- [[BacktestRequest]] - code - src/lib/backtest/runner.ts
- [[BacktestView]] - code - src/lib/backtest/view.ts
- [[DEFAULT_BACKTEST_OHLC_PATH]] - code - src/lib/backtest/ohlc-store.ts
- [[FORBIDDEN]] - code - src/lib/strategy-author/validate.ts
- [[FixturePipelineResult]] - code - src/lib/strategy-author/pipeline.ts
- [[GENERATED_MANIFEST_DIR]] - code - src/lib/strategy-author/workspace.ts
- [[LlmComplete]] - code - src/lib/strategy-author/llm.ts
- [[LlmCompleteInput]] - code - src/lib/strategy-author/llm.ts
- [[NlFixture]] - code - src/lib/strategy-author/pipeline.ts
- [[OhlcRequest]] - code - src/lib/data/ohlc.ts
- [[OwnedCertification]] - code - src/lib/strategy-author/pipeline.ts
- [[REQUIRED]] - code - src/lib/strategy-author/validate.ts
- [[SA1_NL_FIXTURE_PATH]] - code - src/lib/strategy-author/pipeline.ts
- [[STRATEGY_AUTHOR_SYSTEM_PROMPT]] - code - src/lib/strategy-author/pipeline.ts
- [[StrategyAuthorForm()]] - code - src/app/strategy/strategy-form.tsx
- [[StrategyAuthorOptions]] - code - src/lib/strategy-author/pipeline.ts
- [[StrategyAuthorPage()]] - code - src/app/strategy/page.tsx
- [[StrategyAuthorView]] - code - src/app/strategy/actions.ts
- [[StrategyDraft]] - code - src/lib/strategy-author/pipeline.ts
- [[StrategyDraftManifest]] - code - src/lib/strategy-author/workspace.ts
- [[WalkForwardOptions]] - code - src/lib/backtest/walk-forward.ts
- [[WalkForwardSplit]] - code - src/lib/backtest/walk-forward.ts
- [[actions.ts_1]] - code - src/app/backtest/actions.ts
- [[actions.ts_4]] - code - src/app/strategy/actions.ts
- [[adapterIdIsSafe()]] - code - src/lib/strategy-author/workspace.ts
- [[assertOwnedSourceMatch()]] - code - src/lib/strategy-author/validate.ts
- [[backtest-form.tsx]] - code - src/app/backtest/backtest-form.tsx
- [[certifyOwnedFixtureAction()]] - code - src/app/strategy/actions.ts
- [[certifyOwnedGeneratedBot()]] - code - src/lib/strategy-author/pipeline.ts
- [[createDefaultLlmComplete()]] - code - src/lib/strategy-author/llm.ts
- [[createGeneratedSmaAdapter()]] - code - src/lib/bots/adapters/generated/sa1-fixture-sma.ts
- [[draftFromNlAction()]] - code - src/app/strategy/actions.ts
- [[draftStrategy()]] - code - src/lib/strategy-author/pipeline.ts
- [[foldMetric()]] - code - src/lib/backtest/runner.ts
- [[index.ts_4]] - code - src/lib/backtest/index.ts
- [[index.ts_17]] - code - src/lib/strategy-author/index.ts
- [[llm.ts]] - code - src/lib/strategy-author/llm.ts
- [[loadBacktestFixture()]] - code - src/lib/strategy-author/pipeline.ts
- [[loadBacktestOhlc()]] - code - src/lib/backtest/ohlc-store.ts
- [[loadNlFixture()]] - code - src/lib/strategy-author/pipeline.ts
- [[loadStrategyAuthorPage()]] - code - src/app/strategy/actions.ts
- [[nlHash()]] - code - src/lib/strategy-author/workspace.ts
- [[normalize()]] - code - src/lib/strategy-author/validate.ts
- [[ohlc-store.test.ts]] - code - src/lib/backtest/ohlc-store.test.ts
- [[ohlc-store.ts]] - code - src/lib/backtest/ohlc-store.ts
- [[overfitRisk()]] - code - src/lib/backtest/walk-forward.ts
- [[page.tsx_8]] - code - src/app/strategy/page.tsx
- [[paperEnv()]] - code - src/lib/strategy-author/pipeline.ts
- [[pipeline.test.ts]] - code - src/lib/strategy-author/pipeline.test.ts
- [[pipeline.ts]] - code - src/lib/strategy-author/pipeline.ts
- [[positiveInt()]] - code - src/lib/backtest/walk-forward.ts
- [[promoteGeneratedToPaper()]] - code - src/lib/strategy-author/pipeline.ts
- [[promotePaperAction()]] - code - src/app/strategy/actions.ts
- [[readOwnedAdapterSource()]] - code - src/lib/strategy-author/workspace.ts
- [[readSource()]] - code - src/lib/strategy-author/llm.ts
- [[runBacktest()]] - code - src/lib/backtest/runner.ts
- [[runFold()]] - code - src/lib/backtest/runner.ts
- [[runOwnedFixturePipeline()]] - code - src/lib/strategy-author/pipeline.ts
- [[runner.ts]] - code - src/lib/backtest/runner.ts
- [[simulationEnv()]] - code - src/lib/backtest/runner.ts
- [[sliceBars()]] - code - src/lib/backtest/ohlc-store.ts
- [[stamps]] - code - src/lib/backtest/walk-forward.test.ts
- [[startBacktestAction()]] - code - src/app/backtest/actions.ts
- [[strategy-form.tsx]] - code - src/app/strategy/strategy-form.tsx
- [[strategyAuthorLlmConfigured()]] - code - src/lib/strategy-author/llm.ts
- [[toBacktestView()]] - code - src/lib/backtest/runner.ts
- [[validate.ts]] - code - src/lib/strategy-author/validate.ts
- [[validateGeneratedSource()]] - code - src/lib/strategy-author/validate.ts
- [[view.ts]] - code - src/lib/backtest/view.ts
- [[walk-forward.test.ts]] - code - src/lib/backtest/walk-forward.test.ts
- [[walk-forward.ts]] - code - src/lib/backtest/walk-forward.ts
- [[walkForwardSplits()]] - code - src/lib/backtest/walk-forward.ts
- [[withBacktestProvenance()]] - code - src/lib/backtest/runner.ts
- [[workspace.ts]] - code - src/lib/strategy-author/workspace.ts
- [[writeDraftManifest()]] - code - src/lib/strategy-author/workspace.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Strategy_Backtesting_UI
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 14 edges to [[_COMMUNITY_Mirofish Integration Testing]]
- 11 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 10 edges to [[_COMMUNITY_Safety Control Actions]]
- 9 edges to [[_COMMUNITY_Database Policy Management]]
- 7 edges to [[_COMMUNITY_Stack Tool Management]]
- 6 edges to [[_COMMUNITY_Market Data Actions]]
- 6 edges to [[_COMMUNITY_Order Simulation Testing]]
- 5 edges to [[_COMMUNITY_OHLC Data Processing]]
- 5 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 4 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 2 edges to [[_COMMUNITY_Authentication Route Handlers]]
- 2 edges to [[_COMMUNITY_Trading Blotter Panels]]
- 2 edges to [[_COMMUNITY_Design System Dashboard]]
- 2 edges to [[_COMMUNITY_Research Signal Generation]]
- 2 edges to [[_COMMUNITY_Broker Credential Controls]]
- 1 edge to [[_COMMUNITY_Order Audit Reconciliation]]

## Top bridge nodes
- [[runner.ts]] - degree 38, connects to 9 communities
- [[pipeline.test.ts]] - degree 23, connects to 8 communities
- [[pipeline.ts]] - degree 42, connects to 5 communities
- [[actions.ts_4]] - degree 23, connects to 5 communities
- [[runBacktest()]] - degree 16, connects to 3 communities