---
type: community
cohesion: 0.33
members: 6
---

# Reference Bot Architecture

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[Bot Adapters]] - code - src/lib/bots
- [[Fynn Contract Mirror]] - code - packages/contract
- [[Fynn Reference Bot]] - concept - CLAUDE.md
- [[Kybernetes Harness]] - concept - AGENTS.md
- [[Model C Order Flow]] - concept - AGENTS.md
- [[Safety Kernel]] - code - src/lib/safety

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Reference_Bot_Architecture
SORT file.name ASC
```
