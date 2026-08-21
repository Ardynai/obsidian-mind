# Launcher Registry Overlays

> 43 nodes · cohesion 0.09

## Key Concepts

- **sync-install-status.mjs** (38 connections) — `scripts/registry/sync-install-status.mjs`
- **syncInstallStatusInternal()** (15 connections) — `scripts/registry/sync-install-status.mjs`
- **launcher-containment.mjs** (8 connections) — `scripts/registry/launcher-containment.mjs`
- **mergeRegistryOverlay()** (8 connections) — `scripts/registry/overlay.mjs`
- **validateLauncherContainment()** (7 connections) — `scripts/registry/launcher-containment.mjs`
- **overlay.mjs** (7 connections) — `scripts/registry/overlay.mjs`
- **computeSyncedRegistry()** (7 connections) — `scripts/registry/sync-install-status.mjs`
- **syncInstallStatus()** (7 connections) — `scripts/registry/sync-install-status.mjs`
- **bootstrap-cli.ts** (7 connections) — `src/lib/stack-runtime/bootstrap-cli.ts`
- **toUserOverlayRecords()** (6 connections) — `scripts/registry/overlay.mjs`
- **exists()** (5 connections) — `scripts/registry/sync-install-status.mjs`
- **readInstallRows()** (4 connections) — `scripts/registry/sync-install-status.mjs`
- **syncInstallStatusByName()** (4 connections) — `scripts/registry/sync-install-status.mjs`
- **writeJsonAtomically()** (4 connections) — `scripts/registry/sync-install-status.mjs`
- **runBootstrapCli()** (4 connections) — `src/lib/stack-runtime/bootstrap-cli.ts`
- **hasName()** (3 connections) — `scripts/registry/launcher-containment.mjs`
- **samePath()** (3 connections) — `scripts/registry/launcher-containment.mjs`
- **sameText()** (3 connections) — `scripts/registry/launcher-containment.mjs`
- **compact()** (3 connections) — `scripts/registry/overlay.mjs`
- **isRecord()** (3 connections) — `scripts/registry/overlay.mjs`
- **discoverToolLauncher()** (3 connections) — `scripts/registry/sync-install-status.mjs`
- **hasFilesystemInstallEvidence()** (3 connections) — `scripts/registry/sync-install-status.mjs`
- **installNameCandidates()** (3 connections) — `scripts/registry/sync-install-status.mjs`
- **isWindowsOnlyCmdLauncher()** (3 connections) — `scripts/registry/sync-install-status.mjs`
- **parseCsvRows()** (3 connections) — `scripts/registry/sync-install-status.mjs`
- *... and 18 more nodes in this community*

## Relationships

- [Git Environment Configuration](Git_Environment_Configuration.md) (6 shared connections)
- [Tool Launcher Containment](Tool_Launcher_Containment.md) (5 shared connections)
- [Launcher Module Dependencies](Launcher_Module_Dependencies.md) (5 shared connections)
- [Trading Stack Paths](Trading_Stack_Paths.md) (3 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (3 shared connections)
- [Performance Comparison UI](Performance_Comparison_UI.md) (1 shared connections)

## Source Files

- `scripts/registry/launcher-containment.mjs`
- `scripts/registry/overlay.mjs`
- `scripts/registry/sync-install-status.mjs`
- `src/lib/registry/overlay.test.ts`
- `src/lib/stack-runtime/bootstrap-cli.ts`

## Audit Trail

- EXTRACTED: 193 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*