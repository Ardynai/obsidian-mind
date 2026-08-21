---
type: community
cohesion: 0.22
members: 27
---

# Market Data Context

**Cohesion:** 0.22 - loosely connected
**Members:** 27 nodes

## Members
- [[AAPL_FIXTURE_BARS]] - code - src/lib/terminal/sim-tape.ts
- [[AAPL_FIXTURE_CLOSES]] - code - src/lib/terminal/sim-tape.ts
- [[FeedMode]] - code - src/lib/terminal/sim-tape.ts
- [[MarketLiveContext]] - code - src/components/terminal/market-live-context.tsx
- [[MarketLiveProvider()]] - code - src/components/terminal/market-live-context.tsx
- [[MarketLiveValue]] - code - src/components/terminal/market-live-context.tsx
- [[NewsSnapshot]] - code - src/app/terminal/data-actions.ts
- [[QuotesSnapshot]] - code - src/app/terminal/data-actions.ts
- [[SIM_BASE_LAST]] - code - src/lib/terminal/sim-tape.ts
- [[WatchlistRowView]] - code - src/app/terminal/data-actions.ts
- [[hashTicker()]] - code - src/lib/terminal/sim-tape.ts
- [[isLiveOhlcSource()]] - code - src/lib/terminal/sim-tape.ts
- [[market-live-context.tsx]] - code - src/components/terminal/market-live-context.tsx
- [[mergeWatchlist()]] - code - src/lib/terminal/sim-tape.ts
- [[mulberry32()]] - code - src/lib/terminal/sim-tape.ts
- [[padSpark()]] - code - src/lib/terminal/sim-tape.ts
- [[resolveFeedMode()]] - code - src/lib/terminal/sim-tape.ts
- [[round2()]] - code - src/lib/terminal/sim-tape.ts
- [[seedQuotes()]] - code - src/lib/terminal/sim-tape.ts
- [[seedWatchlist()]] - code - src/lib/terminal/sim-tape.ts
- [[sim-tape.test.ts]] - code - src/lib/terminal/sim-tape.test.ts
- [[sim-tape.ts]] - code - src/lib/terminal/sim-tape.ts
- [[synthesizeBars()]] - code - src/lib/terminal/sim-tape.ts
- [[synthesizeSpark()]] - code - src/lib/terminal/sim-tape.ts
- [[walkPrice()]] - code - src/lib/terminal/sim-tape.ts
- [[walkQuotes()]] - code - src/lib/terminal/sim-tape.ts
- [[walkWatchlist()]] - code - src/lib/terminal/sim-tape.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Market_Data_Context
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Market Dashboard Panels]]
- 12 edges to [[_COMMUNITY_Market Data Actions]]
- 9 edges to [[_COMMUNITY_Trading Blotter Panels]]
- 2 edges to [[_COMMUNITY_Chart Layout Configuration]]
- 2 edges to [[_COMMUNITY_Terminal Workspace UI]]
- 1 edge to [[_COMMUNITY_OHLC Tape Indicators]]
- 1 edge to [[_COMMUNITY_Module Resolution Utilities]]

## Top bridge nodes
- [[market-live-context.tsx]] - degree 34, connects to 5 communities
- [[sim-tape.ts]] - degree 30, connects to 4 communities
- [[MarketLiveProvider()]] - degree 14, connects to 3 communities
- [[seedWatchlist()]] - degree 8, connects to 1 community
- [[synthesizeBars()]] - degree 6, connects to 1 community