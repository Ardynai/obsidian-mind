---
type: community
cohesion: 0.10
members: 47
---

# Alert Notification System

**Cohesion:** 0.10 - loosely connected
**Members:** 47 nodes

## Members
- [[.notify()]] - code - src/lib/connectors/mcp.ts
- [[ACTION_TO_CLASS]] - code - src/lib/alerts/config.ts
- [[ALERT_CLASSES]] - code - src/lib/alerts/types.ts
- [[ALERT_CLASS_ENV]] - code - src/lib/alerts/config.ts
- [[ARMED]] - code - src/lib/alerts/alerts.test.ts
- [[AlertClass]] - code - src/lib/alerts/types.ts
- [[AlertClassStatus]] - code - src/lib/alerts/types.ts
- [[AlertDeliveryOutcome]] - code - src/lib/alerts/types.ts
- [[AlertDeliveryStatus]] - code - src/lib/alerts/types.ts
- [[AlertDispatcherDependencies]] - code - src/lib/alerts/types.ts
- [[AlertDispatcherStatus]] - code - src/lib/alerts/types.ts
- [[AlertEnv]] - code - src/lib/alerts/config.ts
- [[AlertFetch]] - code - src/lib/alerts/types.ts
- [[AlertableEvent]] - code - src/lib/alerts/types.ts
- [[AlertsPage()]] - code - src/app/alerts/page.tsx
- [[CLASS_EVENTS]] - code - src/lib/alerts/alerts.test.ts
- [[START_1]] - code - src/lib/alerts/alerts.test.ts
- [[TELEGRAM_ENV]] - code - src/lib/alerts/alerts.test.ts
- [[actions.ts]] - code - src/app/alerts/actions.ts
- [[alertClassEnabled()]] - code - src/lib/alerts/config.ts
- [[alertClassStatuses()]] - code - src/lib/alerts/config.ts
- [[alertGlobal]] - code - src/lib/alerts/dispatcher.ts
- [[alertThrottleMs()]] - code - src/lib/alerts/config.ts
- [[alerts.test.ts]] - code - src/lib/alerts/alerts.test.ts
- [[classifyProvenanceAction()]] - code - src/lib/alerts/config.ts
- [[config.ts]] - code - src/lib/alerts/config.ts
- [[createAlertDispatcher()]] - code - src/lib/alerts/dispatcher.ts
- [[defaultAlertDispatcher()]] - code - src/lib/alerts/dispatcher.ts
- [[defaultFetch()]] - code - src/lib/alerts/dispatcher.ts
- [[dispatcher.ts]] - code - src/lib/alerts/dispatcher.ts
- [[drain.test.ts]] - code - src/lib/alerts/drain.test.ts
- [[drain.ts]] - code - src/lib/alerts/drain.ts
- [[drainAlertsAction()]] - code - src/app/alerts/actions.ts
- [[drainLedgerAlerts()]] - code - src/lib/alerts/drain.ts
- [[haltWhileNotifying()]] - code - src/lib/alerts/alerts.test.ts
- [[index.ts_2]] - code - src/lib/alerts/index.ts
- [[loadAlertStatus()]] - code - src/lib/alerts/notify.ts
- [[notify.ts]] - code - src/lib/alerts/notify.ts
- [[okFetch()]] - code - src/lib/alerts/alerts.test.ts
- [[page.tsx]] - code - src/app/alerts/page.tsx
- [[redactSecrets()]] - code - src/lib/alerts/config.ts
- [[scheduleAlertForEvent()]] - code - src/lib/alerts/notify.ts
- [[startAlertDrainLoop()]] - code - src/lib/alerts/drain.ts
- [[telegramCredentialsPresent()]] - code - src/lib/alerts/config.ts
- [[telegramSendUrl()]] - code - src/lib/alerts/config.ts
- [[telegramText()]] - code - src/lib/alerts/dispatcher.ts
- [[types.ts]] - code - src/lib/alerts/types.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Alert_Notification_System
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Safety Control Actions]]
- 6 edges to [[_COMMUNITY_Broker Credential Controls]]
- 4 edges to [[_COMMUNITY_Stack Tool Management]]
- 4 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 4 edges to [[_COMMUNITY_Latency Probe Worker]]
- 2 edges to [[_COMMUNITY_Authentication Route Handlers]]
- 2 edges to [[_COMMUNITY_Module Resolution Utilities]]
- 1 edge to [[_COMMUNITY_Broker Order Safety]]
- 1 edge to [[_COMMUNITY_Ledger Memory Reservations]]
- 1 edge to [[_COMMUNITY_Financial Anomaly Detection]]

## Top bridge nodes
- [[drain.ts]] - degree 14, connects to 4 communities
- [[alerts.test.ts]] - degree 21, connects to 3 communities
- [[drainLedgerAlerts()]] - degree 10, connects to 2 communities
- [[page.tsx]] - degree 9, connects to 2 communities
- [[actions.ts]] - degree 6, connects to 2 communities