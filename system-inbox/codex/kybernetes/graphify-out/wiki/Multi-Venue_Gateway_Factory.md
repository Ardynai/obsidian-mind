# Multi-Venue Gateway Factory

> 20 nodes · cohesion 0.16

## Key Concepts

- **w1-gateways.test.ts** (24 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **clientOrderIdLimit()** (16 connections) — `src/lib/safety/client-order-id.ts`
- **positiveTimeout()** (11 connections) — `src/lib/safety/gateways/http.ts`
- **createSelectedGateway()** (9 connections) — `src/lib/safety/index.ts`
- **createBinanceGateway()** (6 connections) — `src/lib/safety/gateways/binance.ts`
- **createCoinbaseGateway()** (6 connections) — `src/lib/safety/gateways/coinbase.ts`
- **createKalshiGateway()** (6 connections) — `src/lib/safety/gateways/kalshi.ts`
- **createKrakenGateway()** (6 connections) — `src/lib/safety/gateways/kraken.ts`
- **createOandaGateway()** (6 connections) — `src/lib/safety/gateways/oanda.ts`
- **BINANCE_ENDPOINTS** (3 connections) — `src/lib/safety/config.ts`
- **COINBASE_ENDPOINTS** (3 connections) — `src/lib/safety/config.ts`
- **KRAKEN_ENDPOINTS** (3 connections) — `src/lib/safety/config.ts`
- **OANDA_ENDPOINTS** (3 connections) — `src/lib/safety/config.ts`
- **binanceConfig** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **binanceEnv** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **binanceTruth()** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **marketTruth()** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **order** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **requestUrl()** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`
- **response()** (1 connections) — `src/lib/safety/gateways/w1-gateways.test.ts`

## Relationships

- [Binance Gateway Integration](Binance_Gateway_Integration.md) (24 shared connections)
- [Broker Order Safety](Broker_Order_Safety.md) (9 shared connections)
- [Simulation Risk Kernel](Simulation_Risk_Kernel.md) (8 shared connections)
- [Broker Environment Config](Broker_Environment_Config.md) (7 shared connections)
- [Alpaca Gateway Integration](Alpaca_Gateway_Integration.md) (1 shared connections)

## Source Files

- `src/lib/safety/client-order-id.ts`
- `src/lib/safety/config.ts`
- `src/lib/safety/gateways/binance.ts`
- `src/lib/safety/gateways/coinbase.ts`
- `src/lib/safety/gateways/http.ts`
- `src/lib/safety/gateways/kalshi.ts`
- `src/lib/safety/gateways/kraken.ts`
- `src/lib/safety/gateways/oanda.ts`
- `src/lib/safety/gateways/w1-gateways.test.ts`
- `src/lib/safety/index.ts`

## Audit Trail

- EXTRACTED: 109 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*