# Module Resolution Utilities

> 21 nodes · cohesion 0.15

## Key Concepts

- **ts-resolve.mjs** (10 connections) — `scripts/ts-resolve.mjs`
- **StdioJsonRpcClient** (9 connections) — `src/lib/connectors/mcp.ts`
- **resolve()** (8 connections) — `scripts/ts-resolve.mjs`
- **probeMcpOverStdio()** (7 connections) — `src/lib/connectors/mcp.ts`
- **.start()** (7 connections) — `src/lib/connectors/mcp.ts`
- **.close()** (6 connections) — `src/lib/connectors/mcp.ts`
- **resolveFile()** (4 connections) — `scripts/ts-resolve.mjs`
- **.handleLine()** (4 connections) — `src/lib/connectors/mcp.ts`
- **.request()** (4 connections) — `src/lib/connectors/mcp.ts`
- **.read()** (3 connections) — `src/lib/connectors/mcp.ts`
- **.rejectPending()** (3 connections) — `src/lib/connectors/mcp.ts`
- **isDirectory()** (2 connections) — `scripts/ts-resolve.mjs`
- **isFile()** (2 connections) — `scripts/ts-resolve.mjs`
- **mapSpecifier()** (2 connections) — `scripts/ts-resolve.mjs`
- **getToolCount()** (2 connections) — `src/lib/connectors/mcp.ts`
- **defaultHaltRetryDelay()** (2 connections) — `src/lib/safety/controls.ts`
- **contractEntry** (1 connections) — `scripts/ts-resolve.mjs`
- **load()** (1 connections) — `scripts/ts-resolve.mjs`
- **repoRoot** (1 connections) — `scripts/ts-resolve.mjs`
- **SOURCE_EXTENSIONS** (1 connections) — `scripts/ts-resolve.mjs`
- **srcRoot** (1 connections) — `scripts/ts-resolve.mjs`

## Relationships

- [MCP JSON-RPC Transport](MCP_JSON-RPC_Transport.md) (5 shared connections)
- [Financial Anomaly Detection](Financial_Anomaly_Detection.md) (3 shared connections)
- [Alert Notification System](Alert_Notification_System.md) (2 shared connections)
- [Trading Stack Paths](Trading_Stack_Paths.md) (1 shared connections)
- [Connector Health Monitoring](Connector_Health_Monitoring.md) (1 shared connections)
- [Market Dashboard Panels](Market_Dashboard_Panels.md) (1 shared connections)
- [Market Data Context](Market_Data_Context.md) (1 shared connections)
- [Tool Launcher Containment](Tool_Launcher_Containment.md) (1 shared connections)
- [Broker Credential Controls](Broker_Credential_Controls.md) (1 shared connections)

## Source Files

- `scripts/ts-resolve.mjs`
- `src/lib/connectors/mcp.ts`
- `src/lib/safety/controls.ts`

## Audit Trail

- EXTRACTED: 69 (86%)
- INFERRED: 11 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*