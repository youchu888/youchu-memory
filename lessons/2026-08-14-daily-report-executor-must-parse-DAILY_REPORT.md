---
date: 2026-08-14
tags: [daily-report, cursor-executor, launchd, tg]
severity: high
domain: ops
---

# 日报 21:30 断点：executor 必须真解析 DAILY_REPORT；写 lesson 不算修完

## 背景

连续 3 个工作日（08-12 / 08-13 / 08-14）21:30 launchd 都把 `AGENT_LOOP_WAKE_DAILY_REPORT` 写入了 `wake_feed.log`，但私聊要等人催才补推。08-12 已写 lesson「executor 要认日报哨兵」，**代码没改**。

## 坑 / 错误做法

1. `_parse_wake_line` 只认 `AGENT_LOOP_WAKE_AGENT_BUS`，日报行解析为 `None` 后被丢掉；offset 照样往前走，无法补消费。
2. 即便解析成功，`process_wake` 要求 `bus_id>0`，日报 payload 没有 bus_id，仍会被 skip。
3. 21:45 fallback 只是再写一条同样的 wake，走同一条死路。
4. 只写 lesson / 蒸馏摘要，不改运行中的 `~/Library/Application Support/youchu-agent-bus/python/agent_bus_cursor_executor.py`。

## 正确做法

1. executor `_parse_wake_line` 同时认 `AGENT_LOOP_WAKE_DAILY_REPORT` 与 `AGENT_LOOP_WAKE_AGENT_BUS`。
2. 日报走 `process_daily_report_wake`：过期日 skip、已推送 skip、`flock` 防双开、**新会话** `agent --print`（不要 `--continue`）、写完若未推则补跑 `post_daily_report_to_dm.py`。
3. 21:45 fallback：稿在没推 → 直接 post；稿不在 → 写 wake **并且** 直接调 `process_daily_report_wake`（锁去重）。
4. 改完必须 `launchctl kickstart -k gui/$UID/com.youchu.cursor-executor`，否则长驻进程仍是旧代码。
5. 两份 executor 要一起改：CHcode `.claude/database/scripts/notify/agent_bus_cursor_executor.py` 与 Application Support 运行副本。

## 验证

```bash
python3 -c "import sys; sys.path.insert(0, '$HOME/Library/Application Support/youchu-agent-bus/python'); from agent_bus_cursor_executor import _parse_wake_line; p=_parse_wake_line('AGENT_LOOP_WAKE_DAILY_REPORT {\"prompt\":\"x\",\"date\":\"2099-01-01\"}'); assert p and p['_wake_kind']=='AGENT_LOOP_WAKE_DAILY_REPORT'"
launchctl print gui/$(id -u)/com.youchu.cursor-executor | head
python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py --date YYYY-MM-DD --dry-run
```

08-14 当日：主人催后本会话写稿并 `post_daily_report_to_dm.py` 已推到私聊。

## 关联

- `agent_bus_cursor_executor.py`
- `daily-report-fallback.sh`
- lesson `2026-08-12-daily-report-executor-and-dm-queue.md`（要求写了但当时未改代码）
- feedback `feedback_daily_report_push_tg_dm.md`
