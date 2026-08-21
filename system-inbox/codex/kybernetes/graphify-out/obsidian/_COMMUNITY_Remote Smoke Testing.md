---
type: community
cohesion: 0.22
members: 18
---

# Remote Smoke Testing

**Cohesion:** 0.22 - loosely connected
**Members:** 18 nodes

## Members
- [[.stop()]] - code - src/lib/fynn/remote-smoke.ts
- [[FynnSmokeChild]] - code - src/lib/fynn/remote-smoke.ts
- [[RemoteFynnSmokeProcess]] - code - src/lib/fynn/remote-smoke.ts
- [[allocatePort()]] - code - src/lib/fynn/remote-smoke.ts
- [[assertFynnSmokePortClosed()]] - code - src/lib/fynn/remote-smoke.ts
- [[canConnect()]] - code - src/lib/fynn/remote-smoke.ts
- [[collectLogs()]] - code - src/lib/fynn/remote-smoke.ts
- [[formatLogs()]] - code - src/lib/fynn/remote-smoke.ts
- [[fynnRepoDir()]] - code - src/lib/fynn/remote-smoke.ts
- [[npmRunDevCommand()]] - code - src/lib/fynn/remote-smoke.ts
- [[remote-client-smoke.test.ts]] - code - src/lib/fynn/remote-client-smoke.test.ts
- [[remote-smoke.ts]] - code - src/lib/fynn/remote-smoke.ts
- [[remoteFynnSmokeSkipReason()]] - code - src/lib/fynn/remote-smoke.ts
- [[skipReason]] - code - src/lib/fynn/remote-client-smoke.test.ts
- [[startRemoteFynnSmoke()]] - code - src/lib/fynn/remote-smoke.ts
- [[terminateProcessTree()]] - code - src/lib/fynn/remote-smoke.ts
- [[waitForHealth()]] - code - src/lib/fynn/remote-smoke.ts
- [[waitForPortClosed()]] - code - src/lib/fynn/remote-smoke.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Remote_Smoke_Testing
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Remote Parity Testing]]
- 4 edges to [[_COMMUNITY_Ledger Backtest Scenarios]]
- 3 edges to [[_COMMUNITY_Fynn Risk Reporting]]
- 1 edge to [[_COMMUNITY_Remote Fynn Client]]
- 1 edge to [[_COMMUNITY_Fynn Bot Adapter]]
- 1 edge to [[_COMMUNITY_Fynn Adapter Conformance]]

## Top bridge nodes
- [[remote-client-smoke.test.ts]] - degree 11, connects to 4 communities
- [[remote-smoke.ts]] - degree 17, connects to 2 communities
- [[startRemoteFynnSmoke()]] - degree 13, connects to 2 communities
- [[remoteFynnSmokeSkipReason()]] - degree 6, connects to 2 communities
- [[RemoteFynnSmokeProcess]] - degree 5, connects to 2 communities