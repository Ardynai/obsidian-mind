# Tool Registry Sync

> 12 nodes · cohesion 0.17

## Key Concepts

- **ToolRegistryEntry** (8 connections) — `packages/contract/index.ts`
- **registry-sync.test.ts** (8 connections) — `src/lib/registry-sync.test.ts`
- **sync-install-status.d.mts** (5 connections) — `scripts/registry/sync-install-status.d.mts`
- **InstallReportRow** (1 connections) — `scripts/registry/sync-install-status.d.mts`
- **SyncInstallStatusOptions** (1 connections) — `scripts/registry/sync-install-status.d.mts`
- **SyncInstallStatusResult** (1 connections) — `scripts/registry/sync-install-status.d.mts`
- **launcherByName()** (1 connections) — `src/lib/registry-sync.test.ts`
- **loadSyncModule()** (1 connections) — `src/lib/registry-sync.test.ts`
- **statusByName()** (1 connections) — `src/lib/registry-sync.test.ts`
- **SyncModule** (1 connections) — `src/lib/registry-sync.test.ts`
- **tool()** (1 connections) — `src/lib/registry-sync.test.ts`
- **ToolWithLauncher** (1 connections) — `src/lib/registry-sync.test.ts`

## Relationships

- [Core Trading Types](Core_Trading_Types.md) (3 shared connections)
- [Launcher Module Dependencies](Launcher_Module_Dependencies.md) (2 shared connections)
- [Risk Reporting Utilities](Risk_Reporting_Utilities.md) (2 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (1 shared connections)

## Source Files

- `packages/contract/index.ts`
- `scripts/registry/sync-install-status.d.mts`
- `src/lib/registry-sync.test.ts`

## Audit Trail

- EXTRACTED: 30 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*