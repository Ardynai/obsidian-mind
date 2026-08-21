---
type: community
cohesion: 0.16
members: 20
---

# Multi-Venue Gateway Factory

**Cohesion:** 0.16 - loosely connected
**Members:** 20 nodes

## Members
- [[BINANCE_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[COINBASE_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[KRAKEN_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[OANDA_ENDPOINTS]] - code - src/lib/safety/config.ts
- [[binanceConfig]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[binanceEnv]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[binanceTruth()]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[clientOrderIdLimit()]] - code - src/lib/safety/client-order-id.ts
- [[createBinanceGateway()]] - code - src/lib/safety/gateways/binance.ts
- [[createCoinbaseGateway()]] - code - src/lib/safety/gateways/coinbase.ts
- [[createKalshiGateway()]] - code - src/lib/safety/gateways/kalshi.ts
- [[createKrakenGateway()]] - code - src/lib/safety/gateways/kraken.ts
- [[createOandaGateway()]] - code - src/lib/safety/gateways/oanda.ts
- [[createSelectedGateway()]] - code - src/lib/safety/index.ts
- [[marketTruth()]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[order_5]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[positiveTimeout()_1]] - code - src/lib/safety/gateways/http.ts
- [[requestUrl()_6]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[response()_2]] - code - src/lib/safety/gateways/w1-gateways.test.ts
- [[w1-gateways.test.ts]] - code - src/lib/safety/gateways/w1-gateways.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Multi-Venue_Gateway_Factory
SORT file.name ASC
```

## Connections to other communities
- 24 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 9 edges to [[_COMMUNITY_Broker Order Safety]]
- 8 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 7 edges to [[_COMMUNITY_Broker Environment Config]]
- 1 edge to [[_COMMUNITY_Alpaca Gateway Integration]]

## Top bridge nodes
- [[w1-gateways.test.ts]] - degree 24, connects to 4 communities
- [[createSelectedGateway()]] - degree 9, connects to 3 communities
- [[createKalshiGateway()]] - degree 6, connects to 3 communities
- [[clientOrderIdLimit()]] - degree 16, connects to 2 communities
- [[createBinanceGateway()]] - degree 6, connects to 2 communities