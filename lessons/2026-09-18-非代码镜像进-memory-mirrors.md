---
date: 2026-09-18
tags: [memory-git, dual-mac, mirrors, sync]
severity: medium
domain: ops
---

# 非代码产物进 youchu-memory mirrors

## 背景

双机只靠 `~/.dc-platform/memory` 同步时，核查报告（在 CHcode `.claude/database/reports`）、Cursor transcript、playbook 副本不进仓，导致两台结论「看起来不一致」。

## 做法

- 新增 `export_noncode_mirrors.py`：每轮 sync 前镜像报告/playbook/近 21 天 transcript/tgbot outgoing → `memory/mirrors/`
- 仍不同步：业务代码、密钥、session、agent-bus 全量 state
- launchd 默认间隔改为 **120 秒**

## 旧机

**无需 SSH。** 旧机只要还能跑定时 `sync-memory-git`（即使仍是 10 分钟旧脚本）：

1. 某轮 `pull` 拉到本 lesson / `config/memory_sync.env` / 新脚本  
2. 同轮或下一轮 `worklog_dual_mac_sync` **自动重装** launchd 为 120 秒，并带上 mirrors 导出  

前提：旧机能访问 GitHub。完全断网时需等恢复后自行跑一轮。
