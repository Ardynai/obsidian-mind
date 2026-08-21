# Simulation Risk Kernel

> 71 nodes · cohesion 0.07

## Key Concepts

- **index.ts** (134 connections) — `src/lib/safety/index.ts`
- **processOrderIntents()** (22 connections) — `src/lib/safety/index.ts`
- **controlsFor()** (19 connections) — `src/lib/safety/index.ts`
- **lock.ts** (19 connections) — `src/lib/safety/lock.ts`
- **getSafetySnapshot()** (17 connections) — `src/lib/safety/index.ts`
- **forceClearFlattenUnknown()** (16 connections) — `src/lib/safety/index.ts`
- **simulation-kernel.ts** (14 connections) — `src/lib/backtest/simulation-kernel.ts`
- **armBroker()** (14 connections) — `src/lib/safety/index.ts`
- **getRuntime()** (14 connections) — `src/lib/safety/index.ts`
- **safetyConfigurationFromEnv()** (13 connections) — `src/lib/safety/config.ts`
- **reconcileRuntime()** (11 connections) — `src/lib/safety/index.ts`
- **isVenueGateway()** (10 connections) — `src/lib/safety/gateways/venue.ts`
- **haltRuntime()** (10 connections) — `src/lib/safety/index.ts`
- **flattenBroker()** (9 connections) — `src/lib/safety/index.ts`
- **loadRiskContext()** (9 connections) — `src/lib/safety/index.ts`
- **recordSafetyHeartbeat()** (9 connections) — `src/lib/safety/index.ts`
- **serializeMutation()** (9 connections) — `src/lib/safety/index.ts`
- **.assertOwned()** (9 connections) — `src/lib/safety/lock.ts`
- **poisonDurableSafetyFence()** (9 connections) — `src/lib/safety/lock.ts`
- **withDurableSafetyLock()** (9 connections) — `src/lib/safety/lock.ts`
- **isUnknownAck()** (8 connections) — `src/lib/safety/types.ts`
- **processBacktestOrderIntents()** (7 connections) — `src/lib/backtest/simulation-kernel.ts`
- **SafetyActionOptions** (7 connections) — `src/lib/safety/index.ts`
- **createDurableKernelStateStore()** (7 connections) — `src/lib/safety/state.ts`
- **receiptSinkFor()** (6 connections) — `src/lib/safety/index.ts`
- *... and 46 more nodes in this community*

## Relationships

- [Broker Order Safety](Broker_Order_Safety.md) (31 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (23 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (20 shared connections)
- [Order Audit Reconciliation](Order_Audit_Reconciliation.md) (19 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (16 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (11 shared connections)
- [Binance Gateway Integration](Binance_Gateway_Integration.md) (8 shared connections)
- [Multi-Venue Gateway Factory](Multi-Venue_Gateway_Factory.md) (8 shared connections)
- [Cockpit Navigation Layout](Cockpit_Navigation_Layout.md) (6 shared connections)
- [Venue Gateway Interface](Venue_Gateway_Interface.md) (5 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (5 shared connections)
- [Order Simulation Testing](Order_Simulation_Testing.md) (5 shared connections)

## Source Files

- `src/lib/backtest/simulation-kernel.ts`
- `src/lib/safety/config.ts`
- `src/lib/safety/gateways/venue.ts`
- `src/lib/safety/index.ts`
- `src/lib/safety/kernel.ts`
- `src/lib/safety/lock.ts`
- `src/lib/safety/receipts.test.ts`
- `src/lib/safety/receipts.ts`
- `src/lib/safety/state.ts`
- `src/lib/safety/types.ts`

## Audit Trail

- EXTRACTED: 534 (98%)
- INFERRED: 10 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*