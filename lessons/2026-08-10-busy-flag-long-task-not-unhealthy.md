---
date: 2026-08-10
tags: [tgbot, away-health, busy-flag, long-task]
severity: high
domain: ops
---

# 长任务勿把 busy.flag 当自检异常

## 背景

主人私聊「继续干大漏斗」约 11 分钟后，away-health 告警：`agent busy.flag 超时 660s 已清`。实为正常长任务，不是挂死。

## 坑 / 错误做法

- `agent_queue` 只在开跑写一次 `youchu_ai_tg_agent_busy.flag`，mtime 不续命
- `away-health-sentinel.sh` 默认 `BUSY_STALE_SEC=600`，超时一律 `rm` + TG「自检异常」
- 清锁也不解进程内 `asyncio.Lock`，只会误报、干扰长活

## 正确做法

1. `omdb/tgbot/agent_queue.py`：`run_locked` 期间每 ~45s `_touch_busy_flag`；`is_agent_busy` 认新鲜 mtime 或持锁 PID 仍存活
2. `.cursor/scripts/away-health-sentinel.sh`：PID 存活 = 活锁，只打日志、不清、不告警；仅 PID 已死且 age>1800s 清孤锁并告警
3. 改完后：`bash .cursor/scripts/install-away-health-launchd.sh` + `bash omdb/tgbot/restart.sh`

## 验证

- 长任务跑 >10min：away-health.log 可见 `busy 长任务进行中 …（活锁，跳过）`，无 TG 自检异常
- bot 崩溃残留 flag：PID 死后超时才清孤锁

## 关联

- 脚本：`.cursor/scripts/away-health-sentinel.sh`、`omdb/tgbot/agent_queue.py`
- 日志：`~/Library/Application Support/youchu-agent-bus/state/away-health.log`
- 旧 lesson：`2026-07-21-tg-agent-stuck-direct-commands.md`（当时加 600s 自清，需本条纠正误伤长任务）
