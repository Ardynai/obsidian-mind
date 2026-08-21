---
type: community
cohesion: 0.22
members: 11
---

# Venue Gateway Interface

**Cohesion:** 0.22 - loosely connected
**Members:** 11 nodes

## Members
- [[.acknowledgeOrderTruth()_1]] - code - src/lib/safety/gateways/venue.ts
- [[.checkConnectivity()_1]] - code - src/lib/safety/gateways/venue.ts
- [[.getOrderByClientOrderId()_1]] - code - src/lib/safety/gateways/venue.ts
- [[.listOpenOrders()_1]] - code - src/lib/safety/gateways/venue.ts
- [[BinanceGateway]] - code - src/lib/safety/gateways/binance.ts
- [[CoinbaseGateway]] - code - src/lib/safety/gateways/coinbase.ts
- [[KalshiGateway]] - code - src/lib/safety/gateways/kalshi.ts
- [[KrakenGateway]] - code - src/lib/safety/gateways/kraken.ts
- [[OandaGateway]] - code - src/lib/safety/gateways/oanda.ts
- [[VenueGateway]] - code - src/lib/safety/gateways/venue.ts
- [[findExistingFlattenClose()]] - code - src/lib/safety/index.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Venue_Gateway_Interface
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Binance Gateway Integration]]
- 5 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 3 edges to [[_COMMUNITY_Broker Order Safety]]
- 1 edge to [[_COMMUNITY_Broker Credential Controls]]

## Top bridge nodes
- [[VenueGateway]] - degree 19, connects to 4 communities
- [[findExistingFlattenClose()]] - degree 5, connects to 1 community
- [[.acknowledgeOrderTruth()_1]] - degree 4, connects to 1 community
- [[.listOpenOrders()_1]] - degree 3, connects to 1 community
- [[BinanceGateway]] - degree 2, connects to 1 community