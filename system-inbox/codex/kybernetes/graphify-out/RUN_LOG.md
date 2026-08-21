---
title: Kybernetes final-state graph — run log
source_commit: 8cfacc4
date: 2026-08-21
---

# Kybernetes final-state graph — run log

| Field | Value |
| --- | --- |
| Date | 2026-08-21 (local) |
| Title | Kybernetes final-state graph |
| Source | `C:\AI\kybernetes` (read-only; detached worktree at `8cfacc4`) |
| Commit | `8cfacc4` on `feat/stack-install-after-clone` (`8cfacc4568c5aa17320d0252727a4582ecde282b`) |
| Graphify | 0.9.19 (`graphify extract --backend gemini --force`) then `cluster-only --backend=gemini` |
| Output | `C:\AI\obsidian-mind\system-inbox\codex\kybernetes\graphify-out` |
| Corpus | 407 code · 98 docs · 156 images (661 classified; 21 unclassified skipped) |
| Graph | 2931 nodes · 7745 edges · 281 communities |
| Extract tokens | 324,914 in / 17,755 out · est. ~$0.2157 (Gemini) |
| Label tokens | 7,955 in / 3,290 out (cluster-only community naming) |
| Benchmark | 12.7x fewer tokens per query vs naive corpus (~195k tokens) |

## Pipeline

1. Confirmed `C:\AI\kybernetes` working tree clean. HEAD `8cfacc4` already matches `origin/feat/stack-install-after-clone`. Did not edit Kybernetes source. Did not merge open PR #57 onto `main`.
2. `git worktree add --detach` at `8cfacc4`.
3. `graphify extract <worktree> --backend gemini --force --out …/_kybernetes-final-graph --timing`
4. `graphify cluster-only` (labels + `GRAPH_REPORT.md` + `graph.html`)
5. `graphify export wiki` · `export obsidian` · `tree` · `benchmark`
6. Stamped this MOC/report with commit `8cfacc4` and date 2026-08-21.
7. Replaced the previous vault `graphify-out` (built from `d17aa5a`) so only this bundle remains.
8. Removed the temporary worktree.

## Origin

- GitHub `Ardynai/kybernetes` `feat/stack-install-after-clone` confirmed at `8cfacc4`.
- `origin/main` remains at `d17aa5a` (one commit behind). PR #57 is still open and was not merged (no new PRs / no Kybernetes code change).
