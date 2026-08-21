# Alpaca Gateway Integration

> 41 nodes · cohesion 0.07

## Key Concepts

- **alpaca.ts** (42 connections) — `src/lib/safety/gateways/alpaca.ts`
- **alpaca.test.ts** (16 connections) — `src/lib/safety/gateways/alpaca.test.ts`
- **createAlpacaGateway()** (8 connections) — `src/lib/safety/gateways/alpaca.ts`
- **AlpacaGateway** (7 connections) — `src/lib/safety/gateways/alpaca.ts`
- **parseOrderTruth()** (6 connections) — `src/lib/safety/gateways/alpaca.ts`
- **parsePosition()** (5 connections) — `src/lib/safety/gateways/alpaca.ts`
- **acknowledgementFromAlpacaTruth()** (4 connections) — `src/lib/safety/gateways/alpaca.ts`
- **finitePositive()** (4 connections) — `src/lib/safety/gateways/alpaca.ts`
- **isRecord()** (4 connections) — `src/lib/safety/gateways/alpaca.ts`
- **stringField()** (4 connections) — `src/lib/safety/gateways/alpaca.ts`
- **ackFromTruth()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **.acknowledgeOrderTruth()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **numericField()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **parseCancellationResult()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **rejected()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **validateOrder()** (3 connections) — `src/lib/safety/gateways/alpaca.ts`
- **.getOrderByClientOrderId()** (2 connections) — `src/lib/safety/gateways/alpaca.ts`
- **classifyHttpStatus()** (2 connections) — `src/lib/safety/gateways/alpaca.ts`
- **optionalTimestampField()** (2 connections) — `src/lib/safety/gateways/alpaca.ts`
- **positiveTimeout()** (2 connections) — `src/lib/safety/gateways/alpaca.ts`
- **truthMatchesOrder()** (2 connections) — `src/lib/safety/gateways/alpaca.ts`
- **ACCEPTED_ORDER_STATUSES** (1 connections) — `src/lib/safety/gateways/alpaca.ts`
- **AlpacaErrorTaxonomy** (1 connections) — `src/lib/safety/gateways/alpaca.ts`
- **.checkConnectivity()** (1 connections) — `src/lib/safety/gateways/alpaca.ts`
- **.getDailyLoss()** (1 connections) — `src/lib/safety/gateways/alpaca.ts`
- *... and 16 more nodes in this community*

## Relationships

- [Broker Order Safety](Broker_Order_Safety.md) (11 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (10 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (3 shared connections)
- [Binance Gateway Integration](Binance_Gateway_Integration.md) (2 shared connections)
- [Venue Presence Monitoring](Venue_Presence_Monitoring.md) (1 shared connections)
- [Multi-Venue Gateway Factory](Multi-Venue_Gateway_Factory.md) (1 shared connections)

## Source Files

- `src/lib/safety/gateways/alpaca.test.ts`
- `src/lib/safety/gateways/alpaca.ts`

## Audit Trail

- EXTRACTED: 146 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*