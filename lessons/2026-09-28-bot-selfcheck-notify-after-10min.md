---
date: 2026-09-28
tags: [tgbot, watchdog, alert, ops]
severity: medium
domain: ops
---

# bot 自查：持续 ≥10 分钟才私聊；自愈静默

## 背景

getMe TimedOut / ConnectError 几分钟自愈，但旧逻辑第一次失败就发「自查异常」，恢复再发「自查恢复」，刷屏。

## 正确做法

- `BOT_SELF_CHECK_NOTIFY_AFTER_SEC=600`（默认 10 分钟）
- 异常未满阈值：只打日志「暂不 TG（等自愈）」
- 满阈值：发一条「需人工恢复」；**不发**「自查恢复」
- getMe 已通时 `check_health(skip_tg_liveness=True)`，避免二次 urllib 误报
- 冷却 `BOT_SELF_CHECK_NOTIFY_COOLDOWN` 抑制重复告警

## 验证

```bash
rg 'notify_after|暂不 TG|需人工恢复' /tmp/tgbot-dc.log | tail
# 启动日志应含 notify_after=600s
```

## 关联

- 取代连续次数版：`2026-07-27-bot-selfcheck-notify-after-sustained.md`
