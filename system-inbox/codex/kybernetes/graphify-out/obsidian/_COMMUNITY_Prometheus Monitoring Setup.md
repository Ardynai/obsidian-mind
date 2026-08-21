---
type: community
cohesion: 1.00
members: 2
---

# Prometheus Monitoring Setup

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[Grafana Prometheus Datasource]] - code - ops/grafana/provisioning/datasources/prometheus.yml
- [[Prometheus Configuration]] - code - ops/prometheus/prometheus.yml

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Prometheus_Monitoring_Setup
SORT file.name ASC
```
