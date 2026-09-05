---
date: 2026-09-05
tags: [workbook, agent-bus, progress, no-group-alarm]
severity: high
domain: ops
---

# 群收不到工作簿就不要闹钟发群：等 bus 入站后再按实查 reply

## 背景

主人 2026-09-05：约定是监控到狂人原文再按方案回。群收不到时不要闹钟往群里发，走 bus；也必须收到后再按实际进度回。

## 坑 / 错误做法

- `maybe_daily_fallback` 09:01 无原文仍发群（`message_id=0`）
- 用写死 1/2 条冒充当日簿

## 正确做法

1. **真群消息**（Bot API / Telethon / tg_status 且有 msg_id）→ 实查后回群
2. **真 bus 入站**（worker_ant 清单点名）→ 实查后 `agent_bus_send --kind reply`，**不发群**
3. **没有入站 → 什么都不发**（废止群闹钟）

## 验证

```bash
python3 -c "import inspect; from group_workbook_progress_handler import maybe_daily_fallback; assert 'post_workbook_pipeline' not in inspect.getsource(maybe_daily_fallback)"
```

## 关联

- `workbook_trigger_watcher.py`
- `group_workbook_progress_handler.py`（`reply_workbook_via_bus`）
- `feedback_workbook_progress_list_plus_owned_cutoff.md`
