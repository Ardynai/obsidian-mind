---
type: community
cohesion: 0.09
members: 43
---

# Launcher Registry Overlays

**Cohesion:** 0.09 - loosely connected
**Members:** 43 nodes

## Members
- [[LaunchRefusalReason]] - code - scripts/registry/launcher-containment.mjs
- [[bootstrap-cli.ts]] - code - src/lib/stack-runtime/bootstrap-cli.ts
- [[compact()]] - code - scripts/registry/overlay.mjs
- [[computeSyncedRegistry()]] - code - scripts/registry/sync-install-status.mjs
- [[defaultConnectorsPath]] - code - scripts/registry/sync-install-status.mjs
- [[defaultOverlayPath]] - code - scripts/registry/sync-install-status.mjs
- [[defaultSeedPath]] - code - scripts/registry/sync-install-status.mjs
- [[discoverToolLauncher()]] - code - scripts/registry/sync-install-status.mjs
- [[exists()]] - code - scripts/registry/sync-install-status.mjs
- [[hasFilesystemInstallEvidence()]] - code - scripts/registry/sync-install-status.mjs
- [[hasName()]] - code - scripts/registry/launcher-containment.mjs
- [[installNameCandidates()]] - code - scripts/registry/sync-install-status.mjs
- [[isInstalledReportRow()]] - code - scripts/registry/sync-install-status.mjs
- [[isRecord()]] - code - scripts/registry/overlay.mjs
- [[isWindowsOnlyCmdLauncher()]] - code - scripts/registry/sync-install-status.mjs
- [[launcher-containment.mjs]] - code - scripts/registry/launcher-containment.mjs
- [[main()]] - code - scripts/registry/sync-install-status.mjs
- [[mergeRegistryOverlay()]] - code - scripts/registry/overlay.mjs
- [[overlay.mjs]] - code - scripts/registry/overlay.mjs
- [[overlay.test.ts]] - code - src/lib/registry/overlay.test.ts
- [[parseCsv()]] - code - scripts/registry/sync-install-status.mjs
- [[parseCsvRows()]] - code - scripts/registry/sync-install-status.mjs
- [[readConnectedConnectorNames()]] - code - scripts/registry/sync-install-status.mjs
- [[readConnectedConnectorNamesFromDatabase()]] - code - scripts/registry/sync-install-status.mjs
- [[readInstallRows()]] - code - scripts/registry/sync-install-status.mjs
- [[readRegistryOverlay()]] - code - scripts/registry/sync-install-status.mjs
- [[readRegistrySeed()]] - code - scripts/registry/sync-install-status.mjs
- [[refused()]] - code - scripts/registry/launcher-containment.mjs
- [[registryInstallNameAliases]] - code - scripts/registry/sync-install-status.mjs
- [[root_5]] - code - scripts/registry/sync-install-status.mjs
- [[runBootstrapCli()]] - code - src/lib/stack-runtime/bootstrap-cli.ts
- [[samePath()]] - code - scripts/registry/launcher-containment.mjs
- [[sameText()]] - code - scripts/registry/launcher-containment.mjs
- [[summarize()]] - code - scripts/registry/sync-install-status.mjs
- [[sync-install-status.mjs]] - code - scripts/registry/sync-install-status.mjs
- [[syncInstallStatus()]] - code - scripts/registry/sync-install-status.mjs
- [[syncInstallStatusByName()]] - code - scripts/registry/sync-install-status.mjs
- [[syncInstallStatusInternal()]] - code - scripts/registry/sync-install-status.mjs
- [[toUserOverlayRecords()]] - code - scripts/registry/overlay.mjs
- [[unique()]] - code - scripts/registry/sync-install-status.mjs
- [[upsertToolsToDatabase()]] - code - scripts/registry/sync-install-status.mjs
- [[validateLauncherContainment()]] - code - scripts/registry/launcher-containment.mjs
- [[writeJsonAtomically()]] - code - scripts/registry/sync-install-status.mjs

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Launcher_Registry_Overlays
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Git Environment Configuration]]
- 5 edges to [[_COMMUNITY_Tool Launcher Containment]]
- 5 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 3 edges to [[_COMMUNITY_Trading Stack Paths]]
- 3 edges to [[_COMMUNITY_Stack Tool Management]]
- 1 edge to [[_COMMUNITY_Performance Comparison UI]]

## Top bridge nodes
- [[sync-install-status.mjs]] - degree 38, connects to 4 communities
- [[bootstrap-cli.ts]] - degree 7, connects to 2 communities
- [[syncInstallStatusByName()]] - degree 4, connects to 2 communities
- [[runBootstrapCli()]] - degree 4, connects to 2 communities
- [[syncInstallStatusInternal()]] - degree 15, connects to 1 community