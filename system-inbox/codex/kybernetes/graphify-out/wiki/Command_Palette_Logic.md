# Command Palette Logic

> 21 nodes · cohesion 0.18

## Key Concepts

- **commands.ts** (21 connections) — `src/lib/terminal/commands.ts`
- **views.ts** (14 connections) — `src/lib/terminal/views.ts`
- **parseCommand()** (6 connections) — `src/lib/terminal/commands.ts`
- **findTerminalView()** (6 connections) — `src/lib/terminal/views.ts`
- **rankPaletteItems()** (5 connections) — `src/lib/terminal/commands.ts`
- **isTerminalViewId()** (5 connections) — `src/lib/terminal/views.ts`
- **parseTargetedOpen()** (4 connections) — `src/lib/terminal/commands.ts`
- **TERMINAL_VIEWS** (4 connections) — `src/lib/terminal/views.ts`
- **views.test.ts** (4 connections) — `src/lib/terminal/views.test.ts`
- **bestScore()** (3 connections) — `src/lib/terminal/commands.ts`
- **parseSymbolToken()** (3 connections) — `src/lib/terminal/commands.ts`
- **scoreQuery()** (3 connections) — `src/lib/terminal/commands.ts`
- **commands.test.ts** (3 connections) — `src/lib/terminal/commands.test.ts`
- **parsePane()** (3 connections) — `src/lib/terminal/layout.ts`
- **PRESET_LAYOUT_NAMES** (3 connections) — `src/lib/terminal/layout.ts`
- **VIEW_BY_ID** (3 connections) — `src/lib/terminal/views.ts`
- **isSubsequence()** (2 connections) — `src/lib/terminal/commands.ts`
- **ParsedCommand** (2 connections) — `src/lib/terminal/commands.ts`
- **TerminalView** (2 connections) — `src/lib/terminal/views.ts`
- **PaletteItem** (1 connections) — `src/lib/terminal/commands.ts`
- **TERMINAL_VIEW_IDS** (1 connections) — `src/lib/terminal/views.ts`

## Relationships

- [Workspace Layout Management](Workspace_Layout_Management.md) (8 shared connections)
- [Terminal Workspace UI](Terminal_Workspace_UI.md) (7 shared connections)
- [Stack Tool Classification](Stack_Tool_Classification.md) (4 shared connections)
- [Stack Tool Management](Stack_Tool_Management.md) (2 shared connections)
- [Trading Blotter Panels](Trading_Blotter_Panels.md) (2 shared connections)
- [Terminal Layout Persistence](Terminal_Layout_Persistence.md) (1 shared connections)

## Source Files

- `src/lib/terminal/commands.test.ts`
- `src/lib/terminal/commands.ts`
- `src/lib/terminal/layout.ts`
- `src/lib/terminal/views.test.ts`
- `src/lib/terminal/views.ts`

## Audit Trail

- EXTRACTED: 98 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*