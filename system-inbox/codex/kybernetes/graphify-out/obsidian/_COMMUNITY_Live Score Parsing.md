---
type: community
cohesion: 0.12
members: 36
---

# Live Score Parsing

**Cohesion:** 0.12 - loosely connected
**Members:** 36 nodes

## Members
- [[CliCommandContext]] - code - src/lib/bots/adapters/paper-signal.ts
- [[DECISION_KEYS]] - code - src/lib/bots/adapters/live-score.ts
- [[LiveCliHook]] - code - src/lib/bots/adapters/paper-signal.ts
- [[LiveHttpHook]] - code - src/lib/bots/adapters/paper-signal.ts
- [[LiveHttpKind]] - code - src/lib/bots/adapters/paper-signal.ts
- [[NESTED_KEYS]] - code - src/lib/bots/adapters/live-score.ts
- [[NUMERIC_KEYS]] - code - src/lib/bots/adapters/live-score.ts
- [[PaperSignalSpec]] - code - src/lib/bots/adapters/paper-signal.ts
- [[TEXT_KEYS]] - code - src/lib/bots/adapters/live-score.ts
- [[clampScore()]] - code - src/lib/bots/adapters/live-score.ts
- [[correlationToScore()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[fetchLivePayload()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[getJson()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[healthFromEnv()]] - code - src/lib/bots/adapters/mirofish.ts
- [[healthFromSpec()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[isLocalHttpUrl()]] - code - src/lib/stack-runtime/health.ts
- [[isNumberArray()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[isNumberMatrix()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[isoDate()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[joinUrl()_1]] - code - src/lib/bots/adapters/paper-signal.ts
- [[live-score.test.ts]] - code - src/lib/bots/adapters/live-score.test.ts
- [[live-score.ts]] - code - src/lib/bots/adapters/live-score.ts
- [[paper-signal.ts]] - code - src/lib/bots/adapters/paper-signal.ts
- [[parseDecision()]] - code - src/lib/bots/adapters/live-score.ts
- [[parseLiveScore()]] - code - src/lib/bots/adapters/live-score.ts
- [[parseMiroFishScore()]] - code - src/lib/bots/adapters/mirofish.ts
- [[parseScoreText()]] - code - src/lib/bots/adapters/live-score.ts
- [[pingHttp()]] - code - src/lib/stack-runtime/health.ts
- [[postJson()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[roundMetric()_3]] - code - src/lib/bots/adapters/paper-signal.ts
- [[roundMoney()_3]] - code - src/lib/bots/adapters/paper-signal.ts
- [[runFromLiveScore()_1]] - code - src/lib/bots/adapters/paper-signal.ts
- [[runPaperSignal()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[runWithOptionalLive()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[tryLiveCli()]] - code - src/lib/bots/adapters/paper-signal.ts
- [[tryLiveHttp()]] - code - src/lib/bots/adapters/paper-signal.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Live_Score_Parsing
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Trading Stack Paths]]
- 10 edges to [[_COMMUNITY_Mirofish Simulation Execution]]
- 6 edges to [[_COMMUNITY_Safety Control Actions]]
- 4 edges to [[_COMMUNITY_Fynn Adapter Conformance]]
- 3 edges to [[_COMMUNITY_Mirofish Integration Testing]]
- 2 edges to [[_COMMUNITY_Research Signal Generation]]
- 1 edge to [[_COMMUNITY_Git Environment Configuration]]

## Top bridge nodes
- [[paper-signal.ts]] - degree 45, connects to 6 communities
- [[pingHttp()]] - degree 11, connects to 2 communities
- [[isLocalHttpUrl()]] - degree 9, connects to 2 communities
- [[parseLiveScore()]] - degree 13, connects to 1 community
- [[live-score.ts]] - degree 11, connects to 1 community