---
type: community
cohesion: 0.40
members: 5
---

# Cockpit Registry Specs

**Cohesion:** 0.40 - moderately connected
**Members:** 5 nodes

## Members
- [[cockpit-registry.spec.ts]] - code - e2e/cockpit-registry.spec.ts
- [[connectorsSeed]] - code - e2e/cockpit-registry.spec.ts
- [[registrySeed]] - code - e2e/cockpit-registry.spec.ts
- [[registrySeedUrl]] - code - e2e/cockpit-registry.spec.ts
- [[tierTables]] - code - e2e/cockpit-registry.spec.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Cockpit_Registry_Specs
SORT file.name ASC
```
