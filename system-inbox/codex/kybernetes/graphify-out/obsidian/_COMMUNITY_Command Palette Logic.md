---
type: community
cohesion: 0.18
members: 21
---

# Command Palette Logic

**Cohesion:** 0.18 - loosely connected
**Members:** 21 nodes

## Members
- [[PRESET_LAYOUT_NAMES]] - code - src/lib/terminal/layout.ts
- [[PaletteItem]] - code - src/lib/terminal/commands.ts
- [[ParsedCommand]] - code - src/lib/terminal/commands.ts
- [[TERMINAL_VIEWS]] - code - src/lib/terminal/views.ts
- [[TERMINAL_VIEW_IDS]] - code - src/lib/terminal/views.ts
- [[TerminalView]] - code - src/lib/terminal/views.ts
- [[VIEW_BY_ID]] - code - src/lib/terminal/views.ts
- [[bestScore()]] - code - src/lib/terminal/commands.ts
- [[commands.test.ts]] - code - src/lib/terminal/commands.test.ts
- [[commands.ts]] - code - src/lib/terminal/commands.ts
- [[findTerminalView()]] - code - src/lib/terminal/views.ts
- [[isSubsequence()]] - code - src/lib/terminal/commands.ts
- [[isTerminalViewId()]] - code - src/lib/terminal/views.ts
- [[parseCommand()]] - code - src/lib/terminal/commands.ts
- [[parsePane()]] - code - src/lib/terminal/layout.ts
- [[parseSymbolToken()]] - code - src/lib/terminal/commands.ts
- [[parseTargetedOpen()]] - code - src/lib/terminal/commands.ts
- [[rankPaletteItems()]] - code - src/lib/terminal/commands.ts
- [[scoreQuery()]] - code - src/lib/terminal/commands.ts
- [[views.test.ts]] - code - src/lib/terminal/views.test.ts
- [[views.ts]] - code - src/lib/terminal/views.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Command_Palette_Logic
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Workspace Layout Management]]
- 7 edges to [[_COMMUNITY_Terminal Workspace UI]]
- 4 edges to [[_COMMUNITY_Stack Tool Classification]]
- 2 edges to [[_COMMUNITY_Trading Blotter Panels]]
- 2 edges to [[_COMMUNITY_Stack Tool Management]]
- 1 edge to [[_COMMUNITY_Terminal Layout Persistence]]

## Top bridge nodes
- [[commands.ts]] - degree 21, connects to 4 communities
- [[views.ts]] - degree 14, connects to 3 communities
- [[parseTargetedOpen()]] - degree 4, connects to 2 communities
- [[parsePane()]] - degree 3, connects to 2 communities
- [[PRESET_LAYOUT_NAMES]] - degree 3, connects to 2 communities