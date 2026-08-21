---
type: community
cohesion: 0.14
members: 20
---

# Order Simulation Testing

**Cohesion:** 0.14 - loosely connected
**Members:** 20 nodes

## Members
- [[OhlcBar_1]] - code - src/lib/bots/types.ts
- [[OhlcResult]] - code - src/lib/data/ohlc.ts
- [[PRE_B2_FIXTURE_BASELINE]] - code - src/lib/runs/runs.test.ts
- [[SafetyOrderProcessor]] - code - src/lib/runs/index.ts
- [[backtest.test.ts]] - code - src/lib/backtest/backtest.test.ts
- [[bar()]] - code - src/lib/runs/runs.test.ts
- [[baseRequest()]] - code - src/lib/runs/runs.test.ts
- [[createOrderCapableStub()]] - code - src/lib/backtest/backtest.test.ts
- [[createOrderEmittingStub()]] - code - src/lib/backtest/backtest.test.ts
- [[dataLoader()]] - code - src/lib/runs/runs.test.ts
- [[emptyResult()]] - code - src/lib/runs/runs.test.ts
- [[groupBySymbol()]] - code - src/lib/bots/adapters/fynn.ts
- [[oneOrderResult()]] - code - src/lib/runs/runs.test.ts
- [[recordingAdapter()]] - code - src/lib/runs/runs.test.ts
- [[resetExecutionReceiptsForTests()]] - code - src/lib/safety/receipts.ts
- [[resetSafetyForTests()]] - code - src/lib/safety/index.ts
- [[runs.test.ts]] - code - src/lib/runs/runs.test.ts
- [[toDeterminismSurface()]] - code - src/lib/runs/runs.test.ts
- [[twoOrderResult()]] - code - src/lib/runs/runs.test.ts
- [[unsortedReplayResult()]] - code - src/lib/runs/runs.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Order_Simulation_Testing
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 7 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 6 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 6 edges to [[_COMMUNITY_Broker Credential Controls]]
- 5 edges to [[_COMMUNITY_Research Signal Generation]]
- 5 edges to [[_COMMUNITY_Mirofish Integration Testing]]
- 5 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 5 edges to [[_COMMUNITY_Order Audit Reconciliation]]
- 5 edges to [[_COMMUNITY_OHLC Data Processing]]
- 5 edges to [[_COMMUNITY_Database Policy Management]]
- 4 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 2 edges to [[_COMMUNITY_Fynn Risk Reporting]]
- 2 edges to [[_COMMUNITY_Safety Control Actions]]

## Top bridge nodes
- [[runs.test.ts]] - degree 39, connects to 11 communities
- [[backtest.test.ts]] - degree 19, connects to 9 communities
- [[OhlcBar_1]] - degree 14, connects to 8 communities
- [[resetExecutionReceiptsForTests()]] - degree 6, connects to 3 communities
- [[resetSafetyForTests()]] - degree 5, connects to 3 communities