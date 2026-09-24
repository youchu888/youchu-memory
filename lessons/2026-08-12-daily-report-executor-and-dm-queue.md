---
date: 2026-08-12
tags: [daily-report, tgbot, queue, cursor-executor]
severity: high
domain: ops
---

# 日报唤醒须由 cursor-executor 消费；私聊串行锁要有硬超时

## 背景

2026-08-12：21:30 launchd 已写 `AGENT_LOOP_WAKE_DAILY_REPORT`，但未自动写稿推送。TG 提示「前面还有 2 条在处理」。

## 根因

1. **日报**：`cursor_executor` 只认 `AGENT_LOOP_WAKE_AGENT_BUS`，丢掉日报哨兵；依赖 IDE monitor 不可靠。
2. **私聊队列**：全渠道 `run_locked` 串行。私聊#297「你自己先查啊」自 20:27 占锁近 2h，stdout 持续则 idle 超时杀不掉；`AI_HARD_TIMEOUT_SEC` 未设（示例为 0）。后面的「整理日报 / 改定稿」只能排队。

## 正确做法

1. executor 解析并执行 `AGENT_LOOP_WAKE_DAILY_REPORT`（新会话 `--print`，写完必须 `post_daily_report_to_dm`）
2. 21:45 `com.youchu.daily-report-fallback` 若未推送再补唤醒
3. `.env` 设 `AI_HARD_TIMEOUT_SEC=1800`（墙钟硬杀，防刷屏拖死队列）
4. 卡住时主人可发「重启 agent」（直连指令，不经队列）

## 验证

```bash
# executor 能 parse 日报
python3 -c "..."  # _parse_wake_line DAILY_REPORT
launchctl print gui/$UID/com.youchu.daily-report-fallback
rg AI_HARD_TIMEOUT_SEC omdb/tgbot/.env
```

## 后续（2026-08-14）

08-12 只写了要求，**代码当时没改**。08-12～08-14 连续三天仍断在同一点。真正修法见 `2026-08-14-daily-report-executor-must-parse-DAILY_REPORT.md`。

## 关联

- `agent_bus_cursor_executor.py`
- `daily-report-wake.sh` / `daily-report-fallback.sh`
- lesson `2026-08-11-daily-report-wake-authority-parse.md`
