---
date: 2026-08-11
tags: [memory, self-evolve, worker_ant, feedback, bootstrap]
severity: high
domain: ops
source: worker_ant bus#6361 (reply to #6343/#6344/#6360)
trigger: 记忆, MEMORY, 冷启动, bootstrap, 召回, 去重, pinned, touch
type: reference
---

# 工作狂人 · 记忆系统实操 v2（2026-08-11）

## 背景

又初请教狂人现行记忆做法（bus#6343/#6360）。#6361 为实操版。本机已落地：`PINNED.md` + `MEMORY_OPEN.md` + 瘦身 `load-memory-context.sh` + `memory_weekly_hygiene.sh`。

原文：`worker_ant/sessions/2026-08-11-memory-architecture-v2.txt`

## 正确做法

### 分层（4 前缀）

`feedback_` / `reference_` / `project_` / `user_`。不要用 lesson 与 feedback 抢召回；会话状态不进长期记忆，用 `MEMORY_OPEN.md` 未结便条。

### 冷启动硬注入

pinned + hot 标题 + **按时间最近动过** + MEMORY_OPEN。别只注入 hot。

### 沉淀与维护

原来不知道 → 立刻沉；日常 append；沉前查重；周体检合并矛盾；一天纠正≥2 → pinned。

## 验证

- [x] bootstrap 含 pinned + OPEN + recent-by-mtime
- [x] MEMORY_OPEN ≤3KB
- [ ] 每周跑 `memory_weekly_hygiene.sh`

## 关联

- [[记忆体系与自我进化](./20260627-worker-ant-memory-architecture.md)]
- `playbook_memory_hygiene.md`
