---
title: butler 原生图记忆取代 dc-platform 脚本维护
date: 2026-08-01
tags: [memory, butler, self-evolve, worker_ant]
severity: medium
---

## 变更

记忆体系已做进 **butler 原生**（bus#5858/#5860）：项目 `.claude/memory/` + sqlite 图；六工具 hot/query/upsert/touch/neighbors/timeline。

## 又初已对齐

- `reference_butler_memory_system_v2.md` + `feedback_memory_hot_misses_new_nodes.md`
- `MEMORY.md` 索引两行；`README.md` 改写
- `bootstrap-memory` / `self-evolve` skill 更新读写流程

## 铁律摘要

写：遇到就存 → query 查重 → upsert；读：timeline+query，勿只看 hot；真用到再 touch。
