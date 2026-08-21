---
type: community
cohesion: 0.35
members: 11
---

# Repository Kind Detection

**Cohesion:** 0.35 - loosely connected
**Members:** 11 nodes

## Members
- [[DetectedRepoKind]] - code - src/lib/registry/detect.ts
- [[RegistryBucket_1]] - code - src/lib/registry/detect.ts
- [[detect.test.ts]] - code - src/lib/registry/detect.test.ts
- [[detect.ts]] - code - src/lib/registry/detect.ts
- [[detectRepoBucket()]] - code - src/lib/registry/detect.ts
- [[detectRepoBucketFromDir()]] - code - src/lib/registry/detect.ts
- [[hasWebUi()]] - code - src/lib/registry/detect.ts
- [[isRecord()_11]] - code - src/lib/registry/detect.ts
- [[readFirst()]] - code - src/lib/registry/detect.ts
- [[readOptional()]] - code - src/lib/registry/detect.ts
- [[safeJson()]] - code - src/lib/registry/detect.ts

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Repository_Kind_Detection
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Git Environment Configuration]]
- 1 edge to [[_COMMUNITY_Stack Tool Management]]

## Top bridge nodes
- [[RegistryBucket_1]] - degree 3, connects to 2 communities
- [[detect.ts]] - degree 11, connects to 1 community
- [[detectRepoBucketFromDir()]] - degree 6, connects to 1 community