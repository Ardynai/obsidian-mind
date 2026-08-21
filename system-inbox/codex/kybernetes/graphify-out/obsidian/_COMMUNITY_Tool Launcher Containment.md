---
type: community
cohesion: 0.08
members: 56
---

# Tool Launcher Containment

**Cohesion:** 0.08 - loosely connected
**Members:** 56 nodes

## Members
- [[LaunchToolResult]] - code - src/lib/launcher/index.ts
- [[LauncherContainmentOk]] - code - src/lib/launcher/index.ts
- [[LauncherContainmentRefused]] - code - src/lib/launcher/index.ts
- [[LauncherContainmentResult_1]] - code - src/lib/launcher/index.ts
- [[LauncherPlatform]] - code - src/lib/launcher/platform.ts
- [[LauncherRefusalReason]] - code - src/lib/launcher/types.ts
- [[ManagedProcess]] - code - src/lib/stack-runtime/manager.ts
- [[RUNTIME_ENV_NAMES]] - code - src/lib/security/child-env.ts
- [[ScaffoldedLaunchers]] - code - src/lib/launcher/scaffold.ts
- [[ValidateLauncherContainmentOptions]] - code - src/lib/launcher/index.ts
- [[allowedLauncherNames()]] - code - src/lib/launcher/index.ts
- [[allowedLauncherNamesFor()]] - code - src/lib/launcher/platform.ts
- [[attachLog()]] - code - src/lib/stack-runtime/manager.ts
- [[child-env.test.ts]] - code - src/lib/security/child-env.test.ts
- [[child-env.ts]] - code - src/lib/security/child-env.ts
- [[childEnv()]] - code - src/lib/security/child-env.ts
- [[counterpartLauncherName()]] - code - src/lib/launcher/platform.ts
- [[detectEntryCommand()]] - code - src/lib/launcher/scaffold.ts
- [[emitLauncherAuditEvent()]] - code - src/lib/launcher/audit.ts
- [[ensureCounterpartLaunchers()]] - code - src/lib/launcher/scaffold.ts
- [[findToolByName()]] - code - src/lib/launcher/index.ts
- [[getManagedSnapshot()]] - code - src/lib/stack-runtime/manager.ts
- [[index.ts_11]] - code - src/lib/launcher/index.ts
- [[installNameCandidates()_1]] - code - src/lib/launcher/index.ts
- [[isManagedRunning()]] - code - src/lib/stack-runtime/manager.ts
- [[isPlatformSupported()]] - code - src/lib/launcher/platform.ts
- [[isSafeEnvName()]] - code - src/lib/security/child-env.ts
- [[launchManagedTool()]] - code - src/lib/stack-runtime/manager.ts
- [[launchToolByName()]] - code - src/lib/launcher/index.ts
- [[launcherAuditRun()]] - code - src/lib/launcher/audit.ts
- [[launcherExtension()]] - code - src/lib/launcher/platform.ts
- [[launcherFileName()]] - code - src/lib/launcher/platform.ts
- [[manager.test.ts]] - code - src/lib/stack-runtime/manager.test.ts
- [[manager.ts]] - code - src/lib/stack-runtime/manager.ts
- [[mocks_11]] - code - src/lib/stack-runtime/manager.test.ts
- [[parseUnixLauncher()]] - code - src/lib/launcher/platform.ts
- [[parseWindowsLauncher()]] - code - src/lib/launcher/platform.ts
- [[platform.test.ts]] - code - src/lib/launcher/platform.test.ts
- [[platform.ts]] - code - src/lib/launcher/platform.ts
- [[preferredLauncherPath()]] - code - src/lib/launcher/platform.ts
- [[processes]] - code - src/lib/stack-runtime/manager.ts
- [[refuse()]] - code - src/lib/launcher/index.ts
- [[registryInstallNameAliases_1]] - code - src/lib/launcher/index.ts
- [[renderUnixLauncher()]] - code - src/lib/launcher/platform.ts
- [[renderWindowsLauncher()]] - code - src/lib/launcher/platform.ts
- [[resetManagedProcessesForTests()]] - code - src/lib/stack-runtime/manager.ts
- [[scaffold.test.ts]] - code - src/lib/launcher/scaffold.test.ts
- [[scaffold.ts]] - code - src/lib/launcher/scaffold.ts
- [[scaffoldLaunchers()]] - code - src/lib/launcher/scaffold.ts
- [[selectLauncherFile()]] - code - src/lib/launcher/platform.ts
- [[spawnErrorMessage()]] - code - src/lib/launcher/index.ts
- [[stopManagedTool()]] - code - src/lib/stack-runtime/manager.ts
- [[unique()_1]] - code - src/lib/launcher/index.ts
- [[unixifyCommand()]] - code - src/lib/launcher/platform.ts
- [[validateLauncherContainment()_1]] - code - src/lib/launcher/index.ts
- [[windowsifyCommand()]] - code - src/lib/launcher/scaffold.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tool_Launcher_Containment
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Trading Stack Paths]]
- 12 edges to [[_COMMUNITY_Stack Tool Management]]
- 11 edges to [[_COMMUNITY_Git Environment Configuration]]
- 11 edges to [[_COMMUNITY_Launcher Module Dependencies]]
- 5 edges to [[_COMMUNITY_Launcher Registry Overlays]]
- 5 edges to [[_COMMUNITY_Safety Control Actions]]
- 4 edges to [[_COMMUNITY_Connector Management Actions]]
- 4 edges to [[_COMMUNITY_MCP JSON-RPC Transport]]
- 3 edges to [[_COMMUNITY_Launcher Security Boundaries]]
- 1 edge to [[_COMMUNITY_Module Resolution Utilities]]

## Top bridge nodes
- [[index.ts_11]] - degree 38, connects to 6 communities
- [[childEnv()]] - degree 15, connects to 5 communities
- [[launchManagedTool()]] - degree 19, connects to 4 communities
- [[child-env.ts]] - degree 11, connects to 4 communities
- [[manager.ts]] - degree 28, connects to 3 communities