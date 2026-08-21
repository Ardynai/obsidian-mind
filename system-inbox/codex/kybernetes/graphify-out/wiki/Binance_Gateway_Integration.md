# Binance Gateway Integration

> 135 nodes · cohesion 0.04

## Key Concepts

- **kraken.ts** (61 connections) — `src/lib/safety/gateways/kraken.ts`
- **kalshi.ts** (59 connections) — `src/lib/safety/gateways/kalshi.ts`
- **coinbase.ts** (55 connections) — `src/lib/safety/gateways/coinbase.ts`
- **binance.ts** (53 connections) — `src/lib/safety/gateways/binance.ts`
- **oanda.ts** (43 connections) — `src/lib/safety/gateways/oanda.ts`
- **isRecord()** (35 connections) — `src/lib/safety/gateways/http.ts`
- **stringField()** (26 connections) — `src/lib/safety/gateways/http.ts`
- **numericField()** (25 connections) — `src/lib/safety/gateways/http.ts`
- **http.ts** (22 connections) — `src/lib/safety/gateways/http.ts`
- **finitePositive()** (19 connections) — `src/lib/safety/gateways/http.ts`
- **venue.ts** (18 connections) — `src/lib/safety/gateways/venue.ts`
- **submit-retry.ts** (16 connections) — `src/lib/safety/gateways/submit-retry.ts`
- **validClientOrderId()** (15 connections) — `src/lib/safety/client-order-id.ts`
- **unknownArray()** (12 connections) — `src/lib/safety/gateways/http.ts`
- **reverseBinanceTrades()** (9 connections) — `src/lib/safety/gateways/binance.ts`
- **submitWithReconcileRetry()** (9 connections) — `src/lib/safety/gateways/submit-retry.ts`
- **boundedJsonRequest()** (8 connections) — `src/lib/safety/gateways/http.ts`
- **midPrice()** (8 connections) — `src/lib/safety/gateways/http.ts`
- **parseKalshiFill()** (8 connections) — `src/lib/safety/gateways/kalshi.ts`
- **VenueOrderTruth** (8 connections) — `src/lib/safety/gateways/venue.ts`
- **coinbaseSodPrice()** (7 connections) — `src/lib/safety/gateways/coinbase.ts`
- **coinbaseSpotPrice()** (7 connections) — `src/lib/safety/gateways/coinbase.ts`
- **utcMidnightMs()** (7 connections) — `src/lib/safety/gateways/http.ts`
- **parseKalshiSettlement()** (7 connections) — `src/lib/safety/gateways/kalshi.ts`
- **loadKrakenSodPrices()** (7 connections) — `src/lib/safety/gateways/kraken.ts`
- *... and 110 more nodes in this community*

## Relationships

- [Broker Order Safety](Broker_Order_Safety.md) (34 shared connections)
- [Multi-Venue Gateway Factory](Multi-Venue_Gateway_Factory.md) (24 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (17 shared connections)
- [Venue Gateway Interface](Venue_Gateway_Interface.md) (11 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (8 shared connections)
- [Venue Presence Monitoring](Venue_Presence_Monitoring.md) (5 shared connections)
- [Alpaca Gateway Integration](Alpaca_Gateway_Integration.md) (2 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (1 shared connections)

## Source Files

- `src/lib/safety/client-order-id.ts`
- `src/lib/safety/config.ts`
- `src/lib/safety/gateways/binance.ts`
- `src/lib/safety/gateways/coinbase.ts`
- `src/lib/safety/gateways/http.ts`
- `src/lib/safety/gateways/kalshi.ts`
- `src/lib/safety/gateways/kraken.ts`
- `src/lib/safety/gateways/oanda.ts`
- `src/lib/safety/gateways/submit-retry.ts`
- `src/lib/safety/gateways/venue.ts`

## Audit Trail

- EXTRACTED: 822 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*