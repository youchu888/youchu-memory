---
name: repo reorg path mapping
description: 2026-11-21 仓库重组新旧路径对照；改记忆路径时先查此表。
type: project
---

# 仓库重组路径对照（bus#14190）

权威表：`data-platform/docs/repo_reorg_20261121_path_mapping.tsv`

| 旧顶层 | 新顶层 |
|--------|--------|
| `ops_system/` | `data-jobs/dolphin/`（spark_migrate→`data-jobs/archive/spark_legacy/spark_migrate/`） |
| `spark/` | `data-jobs/spark/` |
| `pipeline-runner/` | `data-platform/pipeline-runner/` |
| `vscode-extension/` | `data-platform/vscode-extension/` |
| `dc-platform-server/` | `data-platform/dc-platform-server/` |
| `omdb/` / `operating-system/` | `data-jobs/archive/...` |

内容类记忆（表/口径/规则）不因路径迁移改写。

