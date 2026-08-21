---
type: community
cohesion: 0.17
members: 12
---

# Tool Registry Sync

**Cohesion:** 0.17 - loosely connected
**Members:** 12 nodes

## Members
- [[InstallReportRow]] - code - scripts/registry/sync-install-status.d.mts
- [[SyncInstallStatusOptions]] - code - scripts/registry/sync-install-status.d.mts
- [[SyncInstallStatusResult]] - code - scripts/registry/sync-install-status.d.mts
- [[SyncModule]] - code - src/lib/registry-sync.test.ts
- [[ToolRegistryEntry]] - code - packages/contract/index.ts
- [[ToolWithLauncher]] - code - src/lib/registry-sync.test.ts
- [[launcherByName()]] - code - src/lib/registry-sync.test.ts
- [[loadSyncModule()]] - code - src/lib/registry-sync.test.ts
- [[registry-sync.test.ts]] - code - src/lib/registry-sync.test.ts
- [[statusByName()]] - code - src/lib/registry-sync.test.ts
- [[sync-install-status.d.mts]] - code - scripts/registry/sync-install-status.d.mts
- [[tool()_1]] - code - src/lib/registry-sync.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tool_Registry_Sync
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Core Trading Types]]
- 2 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 2 edges to [[_COMMUNITY_Risk Reporting Utilities]]
- 1 edge to [[_COMMUNITY_Performance Comparison UI]]

## Top bridge nodes
- [[ToolRegistryEntry]] - degree 8, connects to 4 communities
- [[registry-sync.test.ts]] - degree 8, connects to 1 community
- [[sync-install-status.d.mts]] - degree 5, connects to 1 community