---
type: community
cohesion: 0.43
members: 7
---

# Ledger Availability UI

**Cohesion:** 0.43 - moderately connected
**Members:** 7 nodes

## Members
- [[LedgerAvailabilityNotice()]] - code - src/app/ledger-availability.ts
- [[LedgerEmptyRow()]] - code - src/app/ledger-availability.ts
- [[LedgerSource]] - code - src/lib/ledger/types.ts
- [[LedgerUnavailableViews()]] - code - src/app/ledger-availability.ts
- [[ledger-availability.ts]] - code - src/app/ledger-availability.ts
- [[page.test.ts]] - code - src/app/page.test.ts
- [[pageSource]] - code - src/app/page.test.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Ledger_Availability_UI
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Performance Comparison UI]]
- 2 edges to [[_COMMUNITY_Safety Control Actions]]
- 1 edge to [[_COMMUNITY_Design System Dashboard]]

## Top bridge nodes
- [[ledger-availability.ts]] - degree 7, connects to 2 communities
- [[LedgerSource]] - degree 3, connects to 2 communities
- [[LedgerAvailabilityNotice()]] - degree 3, connects to 1 community
- [[LedgerEmptyRow()]] - degree 3, connects to 1 community
- [[LedgerUnavailableViews()]] - degree 3, connects to 1 community