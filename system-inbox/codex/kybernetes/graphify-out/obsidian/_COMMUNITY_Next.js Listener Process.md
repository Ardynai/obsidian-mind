---
type: community
cohesion: 0.31
members: 10
---

# Next.js Listener Process

**Cohesion:** 0.31 - loosely connected
**Members:** 10 nodes

## Members
- [[command, ...args]] - code - scripts/run-next.mjs
- [[alertDrainUrl()]] - code - scripts/start-alert-drain.mjs
- [[allowedCommands]] - code - scripts/run-next.mjs
- [[next-listener-args.mjs]] - code - scripts/next-listener-args.mjs
- [[next-listener-args.test.ts]] - code - src/lib/auth/next-listener-args.test.ts
- [[resolveHostname()]] - code - scripts/next-listener-args.mjs
- [[resolvePort()]] - code - scripts/next-listener-args.mjs
- [[run-next.mjs]] - code - scripts/run-next.mjs
- [[start-alert-drain.mjs]] - code - scripts/start-alert-drain.mjs
- [[startSelfDrain()]] - code - scripts/start-alert-drain.mjs

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Nextjs_Listener_Process
SORT file.name ASC
```
