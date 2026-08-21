---
type: community
cohesion: 0.19
members: 23
---

# OHLC Tape Indicators

**Cohesion:** 0.19 - loosely connected
**Members:** 23 nodes

## Members
- [[IndicatorBar]] - code - src/lib/terminal/indicators.ts
- [[IndicatorPeriods]] - code - src/lib/terminal/indicators.ts
- [[OhlcTape()]] - code - src/components/terminal/ohlc-tape.tsx
- [[QuoteBarView]] - code - src/app/terminal/data-actions.ts
- [[TapeApi]] - code - src/components/terminal/ohlc-tape.tsx
- [[TapeOverlays]] - code - src/components/terminal/ohlc-tape.tsx
- [[TapePoint]] - code - src/components/terminal/ohlc-tape.tsx
- [[bollinger()]] - code - src/lib/terminal/indicators.ts
- [[clampPeriod()]] - code - src/lib/terminal/indicators.ts
- [[computeIndicators()]] - code - src/lib/terminal/indicators.ts
- [[cssToken()_1]] - code - src/components/terminal/ohlc-tape.tsx
- [[ema()]] - code - src/lib/terminal/indicators.ts
- [[indicators.test.ts]] - code - src/lib/terminal/indicators.test.ts
- [[indicators.ts]] - code - src/lib/terminal/indicators.ts
- [[lastFinite()]] - code - src/lib/terminal/indicators.ts
- [[macd()]] - code - src/lib/terminal/indicators.ts
- [[mean()_1]] - code - src/lib/terminal/indicators.ts
- [[ohlc-tape.tsx]] - code - src/components/terminal/ohlc-tape.tsx
- [[overlaySeries()]] - code - src/lib/terminal/indicators.ts
- [[rsi()]] - code - src/lib/terminal/indicators.ts
- [[sma()_1]] - code - src/lib/terminal/indicators.ts
- [[toRsi()]] - code - src/lib/terminal/indicators.ts
- [[vwap()]] - code - src/lib/terminal/indicators.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/OHLC_Tape_Indicators
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Chart Layout Configuration]]
- 2 edges to [[_COMMUNITY_Market Data Actions]]
- 1 edge to [[_COMMUNITY_Market Data Context]]
- 1 edge to [[_COMMUNITY_Market Dashboard Panels]]

## Top bridge nodes
- [[ohlc-tape.tsx]] - degree 12, connects to 2 communities
- [[computeIndicators()]] - degree 11, connects to 2 communities
- [[QuoteBarView]] - degree 3, connects to 2 communities
- [[indicators.ts]] - degree 19, connects to 1 community
- [[OhlcTape()]] - degree 5, connects to 1 community