---
source_file: "src/lib/launcher/index.ts"
type: "code"
community: "Tool Launcher Containment"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Tool_Launcher_Containment
---

# index.ts

## Connections
- [[LaunchToolDependencies]] - `contains` [EXTRACTED]
- [[LaunchToolResult]] - `contains` [EXTRACTED]
- [[LauncherAuditDependencies]] - `imports` [EXTRACTED]
- [[LauncherContainmentOk]] - `contains` [EXTRACTED]
- [[LauncherContainmentRefused]] - `contains` [EXTRACTED]
- [[LauncherContainmentResult_1]] - `contains` [EXTRACTED]
- [[LauncherRefusalReason]] - `imports` [EXTRACTED]
- [[RegistryToolWithLauncher]] - `imports` [EXTRACTED]
- [[ValidateLauncherContainmentOptions]] - `contains` [EXTRACTED]
- [[allowedLauncherNames()]] - `contains` [EXTRACTED]
- [[allowedLauncherNamesFor()]] - `imports` [EXTRACTED]
- [[audit.ts]] - `imports_from` [EXTRACTED]
- [[child-env.ts]] - `imports_from` [EXTRACTED]
- [[childEnv()]] - `imports` [EXTRACTED]
- [[emitLauncherAuditEvent()]] - `imports` [EXTRACTED]
- [[ensureCounterpartLaunchers()]] - `imports` [EXTRACTED]
- [[findToolByName()]] - `contains` [EXTRACTED]
- [[installNameCandidates()_1]] - `contains` [EXTRACTED]
- [[isPlatformSupported()]] - `imports` [EXTRACTED]
- [[launchToolByName()]] - `contains` [EXTRACTED]
- [[launcher-actions.ts]] - `imports_from` [EXTRACTED]
- [[launcher-containment.mjs]] - `imports_from` [EXTRACTED]
- [[loadRegistry()]] - `imports` [EXTRACTED]
- [[manager.ts]] - `imports_from` [EXTRACTED]
- [[platform.ts]] - `imports_from` [EXTRACTED]
- [[refuse()]] - `contains` [EXTRACTED]
- [[registry.ts]] - `imports_from` [EXTRACTED]
- [[registryInstallNameAliases_1]] - `contains` [EXTRACTED]
- [[scaffold.ts]] - `imports_from` [EXTRACTED]
- [[selectLauncherFile()]] - `imports` [EXTRACTED]
- [[spawnErrorMessage()]] - `contains` [EXTRACTED]
- [[stack-actions.ts]] - `imports_from` [EXTRACTED]
- [[stack-paths.mjs]] - `imports_from` [EXTRACTED]
- [[tradingStackDir()]] - `imports` [EXTRACTED]
- [[types.ts_7]] - `imports_from` [EXTRACTED]
- [[unique()_1]] - `contains` [EXTRACTED]
- [[validateLauncherContainment()]] - `imports` [EXTRACTED]
- [[validateLauncherContainment()_1]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Tool_Launcher_Containment