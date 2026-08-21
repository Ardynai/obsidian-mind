---
source_file: "src/lib/stack-runtime/manager.ts"
type: "code"
community: "Tool Launcher Containment"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Tool_Launcher_Containment
---

# manager.ts

## Connections
- [[ManagedProcess]] - `contains` [EXTRACTED]
- [[attachLog()]] - `contains` [EXTRACTED]
- [[catalog.ts]] - `imports_from` [EXTRACTED]
- [[child-env.ts]] - `imports_from` [EXTRACTED]
- [[childEnv()]] - `imports` [EXTRACTED]
- [[ensureCounterpartLaunchers()]] - `imports` [EXTRACTED]
- [[getManagedSnapshot()]] - `contains` [EXTRACTED]
- [[getStackService()]] - `imports` [EXTRACTED]
- [[health.ts]] - `imports_from` [EXTRACTED]
- [[index.ts_11]] - `imports_from` [EXTRACTED]
- [[index.ts_16]] - `re_exports` [EXTRACTED]
- [[isManagedRunning()]] - `contains` [EXTRACTED]
- [[isPlatformSupported()]] - `imports` [EXTRACTED]
- [[launchManagedTool()]] - `contains` [EXTRACTED]
- [[launchToolByName()]] - `imports` [EXTRACTED]
- [[loadRegistry()]] - `imports` [EXTRACTED]
- [[manager.test.ts]] - `imports_from` [EXTRACTED]
- [[platform.ts]] - `imports_from` [EXTRACTED]
- [[processes]] - `contains` [EXTRACTED]
- [[registry.ts]] - `imports_from` [EXTRACTED]
- [[resetManagedProcessesForTests()]] - `contains` [EXTRACTED]
- [[sanitize.ts]] - `imports_from` [EXTRACTED]
- [[sanitizeRuntimeText()]] - `imports` [EXTRACTED]
- [[scaffold.ts]] - `imports_from` [EXTRACTED]
- [[selectLauncherFile()]] - `imports` [EXTRACTED]
- [[stopManagedTool()]] - `contains` [EXTRACTED]
- [[tradingStackDir()_1]] - `imports` [EXTRACTED]
- [[validateLauncherContainment()_1]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Tool_Launcher_Containment