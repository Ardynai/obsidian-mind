# Venue Gateway Interface

> 11 nodes · cohesion 0.22

## Key Concepts

- **VenueGateway** (19 connections) — `src/lib/safety/gateways/venue.ts`
- **findExistingFlattenClose()** (5 connections) — `src/lib/safety/index.ts`
- **.acknowledgeOrderTruth()** (4 connections) — `src/lib/safety/gateways/venue.ts`
- **.listOpenOrders()** (3 connections) — `src/lib/safety/gateways/venue.ts`
- **BinanceGateway** (2 connections) — `src/lib/safety/gateways/binance.ts`
- **CoinbaseGateway** (2 connections) — `src/lib/safety/gateways/coinbase.ts`
- **KalshiGateway** (2 connections) — `src/lib/safety/gateways/kalshi.ts`
- **KrakenGateway** (2 connections) — `src/lib/safety/gateways/kraken.ts`
- **OandaGateway** (2 connections) — `src/lib/safety/gateways/oanda.ts`
- **.getOrderByClientOrderId()** (2 connections) — `src/lib/safety/gateways/venue.ts`
- **.checkConnectivity()** (1 connections) — `src/lib/safety/gateways/venue.ts`

## Relationships

- [Binance Gateway Integration](Binance_Gateway_Integration.md) (11 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (5 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (3 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (1 shared connections)

## Source Files

- `src/lib/safety/gateways/binance.ts`
- `src/lib/safety/gateways/coinbase.ts`
- `src/lib/safety/gateways/kalshi.ts`
- `src/lib/safety/gateways/kraken.ts`
- `src/lib/safety/gateways/oanda.ts`
- `src/lib/safety/gateways/venue.ts`
- `src/lib/safety/index.ts`

## Audit Trail

- EXTRACTED: 44 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*