---
date: 2026-09-28
tags: [memory-git, launchd, dual-mac, solo, daily]
severity: medium
domain: ops
---

# 单机 memory sync 改下班一次；双机恢复改 MODE=interval

## 背景

old-mac 停机后，new-mac 单独运作不需要每 2 分钟 push/pull。

## 坑 / 错误做法

只改 LaunchAgents plist：下次 `sync-memory-git.sh` / `worklog_dual_mac_sync.py` 会按旧 `INTERVAL_SEC=120` 自愈重装，改了白改。

## 正确做法

1. 改仓内 `~/.dc-platform/memory/config/memory_sync.env`：`MODE=daily` + `MEMORY_SYNC_HOUR=22` + `MEMORY_SYNC_MINUTE=30`
2. 同步改 `scripts/install-memory-git-sync-launchd.sh`、`sync-memory-git.sh`、`worklog_dual_mac_sync.py` 的 ensure 逻辑
3. 跑一次 sync 推到 youchu-memory（new-mac 为权威，覆盖远程）

双机恢复：

```bash
# 编辑 config/memory_sync.env → MODE=interval
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

## 验证

```bash
rg 'StartCalendar|Hour|StartInterval' ~/Library/LaunchAgents/com.youchu.memory-git-sync.plist
# 期望：Hour=22 Minute=30，无 StartInterval
```

## 关联

- 配置：`~/.dc-platform/memory/config/memory_sync.env`
- 脚本：`memory/scripts/install-memory-git-sync-launchd.sh`
