---
type: community
cohesion: 0.11
members: 36
---

# Ledger Backtest Scenarios

**Cohesion:** 0.11 - loosely connected
**Members:** 36 nodes

## Members
- [[BacktestPage()]] - code - src/app/backtest/page.tsx
- [[LedgerChildReservation]] - code - src/lib/ledger/types.ts
- [[LedgerRunReservationResult]] - code - src/lib/ledger/types.ts
- [[OhlcLoader]] - code - src/lib/runs/index.ts
- [[RunRequest]] - code - src/lib/runs/index.ts
- [[SAFETY_ORDER_EVENT_ACTIONS]] - code - src/lib/runs/index.ts
- [[appendProvenanceEventToMemory()]] - code - src/lib/ledger/index.ts
- [[appendProvenanceEvents()]] - code - src/lib/ledger/index.ts
- [[auditProvenance()]] - code - src/lib/runs/index.ts
- [[canonicalCollection()]] - code - src/lib/runs/index.ts
- [[childReservationsForRun()]] - code - src/lib/runs/index.ts
- [[dataQualityProvenance()]] - code - src/lib/runs/index.ts
- [[defaultRunMode()_1]] - code - src/lib/bots/index.ts
- [[empty-window-provenance.test.ts]] - code - src/lib/data/empty-window-provenance.test.ts
- [[event()]] - code - src/lib/alerts/alerts.test.ts
- [[index.ts_14]] - code - src/lib/runs/index.ts
- [[isCompletedReplay()]] - code - src/lib/runs/index.ts
- [[isHarnessProvenanceEvent()]] - code - src/lib/runs/index.ts
- [[issueCodes()]] - code - src/lib/runs/index.ts
- [[jsonComparable()]] - code - src/lib/runs/index.ts
- [[latestValidatedClose()]] - code - src/lib/runs/index.ts
- [[loadLedger()]] - code - src/lib/ledger/index.ts
- [[page.tsx_1]] - code - src/app/backtest/page.tsx
- [[pendingSafetyRecord()]] - code - src/lib/runs/index.ts
- [[pipelineEvent()]] - code - src/lib/runs/index.ts
- [[pipelineEvents()]] - code - src/lib/runs/index.ts
- [[remote-pipeline-smoke.test.ts]] - code - src/lib/runs/remote-pipeline-smoke.test.ts
- [[restoreEnv()]] - code - src/lib/runs/remote-pipeline-smoke.test.ts
- [[restoreEnvValue()]] - code - src/lib/runs/remote-pipeline-smoke.test.ts
- [[runLedgerScenario()]] - code - src/lib/runs/index.ts
- [[skipReason_2]] - code - src/lib/runs/remote-pipeline-smoke.test.ts
- [[sortJsonKeys()]] - code - src/lib/runs/index.ts
- [[stableJsonKey()]] - code - src/lib/runs/index.ts
- [[toIntentId()]] - code - src/lib/runs/index.ts
- [[toOrderIntent()]] - code - src/lib/runs/index.ts
- [[validateBotRunResultForSafety()]] - code - src/lib/runs/index.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Ledger_Backtest_Scenarios
SORT file.name ASC
```

## Connections to other communities
- 21 edges to [[_COMMUNITY_Ledger Memory Reservations]]
- 13 edges to [[_COMMUNITY_Safety Control Actions]]
- 11 edges to [[_COMMUNITY_Strategy Backtesting UI]]
- 11 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 9 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 8 edges to [[_COMMUNITY_Performance Comparison UI]]
- 7 edges to [[_COMMUNITY_Order Simulation Testing]]
- 6 edges to [[_COMMUNITY_OHLC Data Processing]]
- 4 edges to [[_COMMUNITY_Risk Report Routes]]
- 4 edges to [[_COMMUNITY_Alert Notification System]]
- 4 edges to [[_COMMUNITY_Remote Smoke Testing]]
- 4 edges to [[_COMMUNITY_Latency Probe Worker]]
- 3 edges to [[_COMMUNITY_Stack Tool Management]]
- 3 edges to [[_COMMUNITY_Mirofish Integration Testing]]
- 3 edges to [[_COMMUNITY_Database Policy Management]]
- 2 edges to [[_COMMUNITY_Broker Latency Probing]]
- 2 edges to [[_COMMUNITY_System Health Metrics]]
- 1 edge to [[_COMMUNITY_Market Data Actions]]
- 1 edge to [[_COMMUNITY_Trading Blotter Panels]]
- 1 edge to [[_COMMUNITY_Terminal Workspace UI]]
- 1 edge to [[_COMMUNITY_Research Signal Generation]]
- 1 edge to [[_COMMUNITY_Order Audit Reconciliation]]
- 1 edge to [[_COMMUNITY_Broker Order Safety]]

## Top bridge nodes
- [[index.ts_14]] - degree 67, connects to 14 communities
- [[loadLedger()]] - degree 32, connects to 13 communities
- [[runLedgerScenario()]] - degree 33, connects to 11 communities
- [[event()]] - degree 9, connects to 5 communities
- [[page.tsx_1]] - degree 7, connects to 3 communities