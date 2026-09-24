---
date: 2026-07-27
tags: [tgbot, watchdog, alert, ops]
severity: medium
domain: ops
---

# bot 自查告警：连续失败才私聊

## 背景

主人反馈自查异常刷屏。根因：`check_health` 在 getMe 已成功后仍跑 urllib liveness，父超时 20s < 子重试总时长 → 误报「liveness 超时」，且 `consecutive_bad == 1` 就 TG。

## 正确做法

- 通知阈值：`BOT_SELF_CHECK_NOTIFY_AFTER`（默认 **3**，约 6min）才私聊
- 冷却：`BOT_SELF_CHECK_NOTIFY_COOLDOWN` 默认 **1800s**
- watchdog getMe 成功后 `check_health(skip_tg_liveness=True)`
- 探活父超时 ≥ 子进程最坏时长（默认 45s）

## 验证

```bash
rg 'NOTIFY_AFTER|skip_tg_liveness|暂不 TG' omdb/tgbot/bot_watchdog.py omdb/tgbot/config.py
# 抖动时日志有「暂不告警/暂不 TG」，不应再每 2min 私聊一条
```
