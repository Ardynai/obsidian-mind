# Tool Launcher Containment

> 56 nodes · cohesion 0.08

## Key Concepts

- **index.ts** (38 connections) — `src/lib/launcher/index.ts`
- **manager.ts** (28 connections) — `src/lib/stack-runtime/manager.ts`
- **launchManagedTool()** (19 connections) — `src/lib/stack-runtime/manager.ts`
- **platform.ts** (17 connections) — `src/lib/launcher/platform.ts`
- **ensureCounterpartLaunchers()** (17 connections) — `src/lib/launcher/scaffold.ts`
- **launchToolByName()** (16 connections) — `src/lib/launcher/index.ts`
- **scaffold.ts** (16 connections) — `src/lib/launcher/scaffold.ts`
- **childEnv()** (15 connections) — `src/lib/security/child-env.ts`
- **child-env.ts** (11 connections) — `src/lib/security/child-env.ts`
- **platform.test.ts** (9 connections) — `src/lib/launcher/platform.test.ts`
- **scaffoldLaunchers()** (7 connections) — `src/lib/launcher/scaffold.ts`
- **getManagedSnapshot()** (7 connections) — `src/lib/stack-runtime/manager.ts`
- **stopManagedTool()** (7 connections) — `src/lib/stack-runtime/manager.ts`
- **emitLauncherAuditEvent()** (6 connections) — `src/lib/launcher/audit.ts`
- **isPlatformSupported()** (6 connections) — `src/lib/launcher/platform.ts`
- **selectLauncherFile()** (6 connections) — `src/lib/launcher/platform.ts`
- **isManagedRunning()** (6 connections) — `src/lib/stack-runtime/manager.ts`
- **manager.test.ts** (6 connections) — `src/lib/stack-runtime/manager.test.ts`
- **parseWindowsLauncher()** (5 connections) — `src/lib/launcher/platform.ts`
- **renderUnixLauncher()** (5 connections) — `src/lib/launcher/platform.ts`
- **renderWindowsLauncher()** (5 connections) — `src/lib/launcher/platform.ts`
- **allowedLauncherNames()** (4 connections) — `src/lib/launcher/index.ts`
- **allowedLauncherNamesFor()** (4 connections) — `src/lib/launcher/platform.ts`
- **launcherFileName()** (4 connections) — `src/lib/launcher/platform.ts`
- **installNameCandidates()** (3 connections) — `src/lib/launcher/index.ts`
- *... and 31 more nodes in this community*

## Relationships

- [Trading Stack Paths](Trading_Stack_Paths.md) (19 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (12 shared connections)
- [Launcher Module Dependencies](Launcher_Module_Dependencies.md) (11 shared connections)
- [Git Environment Configuration](Git_Environment_Configuration.md) (11 shared connections)
- [Safety Control Actions](Safety_Control_Actions.md) (5 shared connections)
- [Launcher Registry Overlays](Launcher_Registry_Overlays.md) (5 shared connections)
- [MCP JSON-RPC Transport](MCP_JSON-RPC_Transport.md) (4 shared connections)
- [Connector Management Actions](Connector_Management_Actions.md) (4 shared connections)
- [Launcher Security Boundaries](Launcher_Security_Boundaries.md) (3 shared connections)
- [Module Resolution Utilities](Module_Resolution_Utilities.md) (1 shared connections)

## Source Files

- `src/lib/launcher/audit.ts`
- `src/lib/launcher/index.ts`
- `src/lib/launcher/platform.test.ts`
- `src/lib/launcher/platform.ts`
- `src/lib/launcher/scaffold.test.ts`
- `src/lib/launcher/scaffold.ts`
- `src/lib/launcher/types.ts`
- `src/lib/security/child-env.test.ts`
- `src/lib/security/child-env.ts`
- `src/lib/stack-runtime/manager.test.ts`
- `src/lib/stack-runtime/manager.ts`

## Audit Trail

- EXTRACTED: 327 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*