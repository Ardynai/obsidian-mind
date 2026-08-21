---
type: community
cohesion: 0.18
members: 15
---

# Cockpit Navigation Layout

**Cohesion:** 0.18 - loosely connected
**Members:** 15 nodes

## Members
- [[CockpitNav()]] - code - src/components/shell/cockpit-nav.tsx
- [[CockpitShell()]] - code - src/components/shell/cockpit-shell.tsx
- [[LINKS]] - code - src/components/shell/cockpit-nav.tsx
- [[RootLayout()]] - code - src/app/layout.tsx
- [[TradingMode]] - code - src/components/shell/mode.ts
- [[cockpit-nav.tsx]] - code - src/components/shell/cockpit-nav.tsx
- [[cockpit-shell.tsx]] - code - src/components/shell/cockpit-shell.tsx
- [[layout.tsx]] - code - src/app/layout.tsx
- [[metadata_1]] - code - src/app/layout.tsx
- [[mode.test.ts]] - code - src/components/shell/mode.test.ts
- [[mode.ts]] - code - src/components/shell/mode.ts
- [[mono]] - code - src/app/layout.tsx
- [[sans]] - code - src/app/layout.tsx
- [[snapshot()_1]] - code - src/components/shell/mode.test.ts
- [[tradingModeFromSnapshot()]] - code - src/components/shell/mode.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Cockpit_Navigation_Layout
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Simulation Risk Kernel]]
- 5 edges to [[_COMMUNITY_Design System Dashboard]]
- 3 edges to [[_COMMUNITY_Safety Control Actions]]
- 3 edges to [[_COMMUNITY_Terminal Layout Persistence]]
- 3 edges to [[_COMMUNITY_Broker Credential Controls]]
- 2 edges to [[_COMMUNITY_Trading Blotter Panels]]

## Top bridge nodes
- [[cockpit-shell.tsx]] - degree 15, connects to 5 communities
- [[mode.ts]] - degree 8, connects to 4 communities
- [[tradingModeFromSnapshot()]] - degree 8, connects to 2 communities
- [[mode.test.ts]] - degree 5, connects to 2 communities
- [[layout.tsx]] - degree 8, connects to 1 community