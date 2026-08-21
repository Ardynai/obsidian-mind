# Alert Notification System

> 47 nodes · cohesion 0.10

## Key Concepts

- **dispatcher.ts** (23 connections) — `src/lib/alerts/dispatcher.ts`
- **alerts.test.ts** (21 connections) — `src/lib/alerts/alerts.test.ts`
- **config.ts** (18 connections) — `src/lib/alerts/config.ts`
- **index.ts** (17 connections) — `src/lib/alerts/index.ts`
- **types.ts** (17 connections) — `src/lib/alerts/types.ts`
- **drain.ts** (14 connections) — `src/lib/alerts/drain.ts`
- **drainLedgerAlerts()** (10 connections) — `src/lib/alerts/drain.ts`
- **page.tsx** (9 connections) — `src/app/alerts/page.tsx`
- **notify.ts** (8 connections) — `src/lib/alerts/notify.ts`
- **createAlertDispatcher()** (7 connections) — `src/lib/alerts/dispatcher.ts`
- **defaultAlertDispatcher()** (7 connections) — `src/lib/alerts/dispatcher.ts`
- **actions.ts** (6 connections) — `src/app/alerts/actions.ts`
- **startAlertDrainLoop()** (6 connections) — `src/lib/alerts/drain.ts`
- **AlertableEvent** (6 connections) — `src/lib/alerts/types.ts`
- **loadAlertStatus()** (5 connections) — `src/lib/alerts/notify.ts`
- **scheduleAlertForEvent()** (5 connections) — `src/lib/alerts/notify.ts`
- **AlertClass** (5 connections) — `src/lib/alerts/types.ts`
- **drainAlertsAction()** (4 connections) — `src/app/alerts/actions.ts`
- **AlertsPage()** (4 connections) — `src/app/alerts/page.tsx`
- **haltWhileNotifying()** (4 connections) — `src/lib/alerts/alerts.test.ts`
- **AlertDeliveryOutcome** (4 connections) — `src/lib/alerts/types.ts`
- **AlertDispatcherStatus** (4 connections) — `src/lib/alerts/types.ts`
- **.notify()** (4 connections) — `src/lib/connectors/mcp.ts`
- **alertClassEnabled()** (3 connections) — `src/lib/alerts/config.ts`
- **alertClassStatuses()** (3 connections) — `src/lib/alerts/config.ts`
- *... and 22 more nodes in this community*

## Relationships

- [Safety Control Actions](Safety_Control_Actions.md) (9 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (6 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (4 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (4 shared connections)
- [Latency Probe Worker](Latency_Probe_Worker.md) (4 shared connections)
- [Authentication Route Handlers](Authentication_Route_Handlers.md) (2 shared connections)
- [Module Resolution Utilities](Module_Resolution_Utilities.md) (2 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (1 shared connections)
- [Ledger Memory Reservations](Ledger_Memory_Reservations.md) (1 shared connections)
- [Financial Anomaly Detection](Financial_Anomaly_Detection.md) (1 shared connections)

## Source Files

- `src/app/alerts/actions.ts`
- `src/app/alerts/page.tsx`
- `src/lib/alerts/alerts.test.ts`
- `src/lib/alerts/config.ts`
- `src/lib/alerts/dispatcher.ts`
- `src/lib/alerts/drain.test.ts`
- `src/lib/alerts/drain.ts`
- `src/lib/alerts/index.ts`
- `src/lib/alerts/notify.ts`
- `src/lib/alerts/types.ts`
- `src/lib/connectors/mcp.ts`

## Audit Trail

- EXTRACTED: 249 (99%)
- INFERRED: 3 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*