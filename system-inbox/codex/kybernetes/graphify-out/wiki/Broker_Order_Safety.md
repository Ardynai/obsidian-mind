# Broker Order Safety

> 80 nodes · cohesion 0.06

## Key Concepts

- **kernel.ts** (57 connections) — `src/lib/safety/kernel.ts`
- **types.ts** (38 connections) — `src/lib/safety/types.ts`
- **BrokerOrder** (27 connections) — `src/lib/safety/types.ts`
- **controls.test.ts** (24 connections) — `src/lib/safety/controls.test.ts`
- **BrokerAck** (19 connections) — `src/lib/safety/types.ts`
- **client-order-id.ts** (18 connections) — `src/lib/safety/client-order-id.ts`
- **paper.ts** (17 connections) — `src/lib/safety/gateways/paper.ts`
- **executeBatch()** (16 connections) — `src/lib/safety/kernel.ts`
- **ControllableBrokerGateway** (16 connections) — `src/lib/safety/types.ts`
- **kernel.test.ts** (15 connections) — `src/lib/safety/kernel.test.ts`
- **order-audit.ts** (15 connections) — `src/lib/safety/order-audit.ts`
- **BrokerPosition** (12 connections) — `src/lib/safety/types.ts`
- **OrderIntent** (10 connections) — `src/lib/safety/types.ts`
- **isRemoteBrokerGatewayName()** (9 connections) — `src/lib/safety/config.ts`
- **parseBrokerOrderAuditRef()** (9 connections) — `src/lib/safety/order-audit.ts`
- **executeFlatten()** (8 connections) — `src/lib/safety/kernel.ts`
- **SafetyLimits** (8 connections) — `src/lib/safety/types.ts`
- **createPaperGateway()** (7 connections) — `src/lib/safety/gateways/paper.ts`
- **evaluate()** (7 connections) — `src/lib/safety/kernel.ts`
- **paper.test.ts** (6 connections) — `src/lib/safety/gateways/paper.test.ts`
- **ExecuteFlattenRequest** (6 connections) — `src/lib/safety/kernel.ts`
- **ExecuteOrderIntentRequest** (6 connections) — `src/lib/safety/kernel.ts`
- **toBrokerOrder()** (6 connections) — `src/lib/safety/kernel.ts`
- **brokerOrderAuditRef()** (6 connections) — `src/lib/safety/order-audit.ts`
- **BrokerGateway** (6 connections) — `src/lib/safety/types.ts`
- *... and 55 more nodes in this community*

## Relationships

- [Binance Gateway Integration](Binance_Gateway_Integration.md) (34 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (31 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (30 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (12 shared connections)
- [Alpaca Gateway Integration](Alpaca_Gateway_Integration.md) (11 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (11 shared connections)
- [Multi-Venue Gateway Factory](Multi-Venue_Gateway_Factory.md) (9 shared connections)
- [Order Audit Reconciliation](Order_Audit_Reconciliation.md) (3 shared connections)
- [Venue Gateway Interface](Venue_Gateway_Interface.md) (3 shared connections)
- [Alert Notification System](Alert_Notification_System.md) (1 shared connections)
- [Durable State Store](Durable_State_Store.md) (1 shared connections)
- [Ledger Backtest Scenarios](Ledger_Backtest_Scenarios.md) (1 shared connections)

## Source Files

- `src/lib/safety/client-order-id.test.ts`
- `src/lib/safety/client-order-id.ts`
- `src/lib/safety/config.ts`
- `src/lib/safety/controls.test.ts`
- `src/lib/safety/gateways/paper.test.ts`
- `src/lib/safety/gateways/paper.ts`
- `src/lib/safety/kernel.test.ts`
- `src/lib/safety/kernel.ts`
- `src/lib/safety/order-audit.ts`
- `src/lib/safety/types.ts`

## Audit Trail

- EXTRACTED: 493 (100%)
- INFERRED: 2 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*