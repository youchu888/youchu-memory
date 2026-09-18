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

pull 到新脚本后执行一次：

```bash
INTERVAL_SEC=120 bash ~/.dc-platform/memory/scripts/install-memory-git-sync-launchd.sh
```
