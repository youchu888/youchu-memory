# 私聊 wake 必须干完 · 打卡窗 1 小时

## 场景
TG 私聊交办只写 wake_feed、标「已叫醒」，Away 下 cursor-executor 原先不消费 `AGENT_LOOP_WAKE_TG_DM`，活没人干。周六签退窗 30 分钟，MFA 失败后窗已关。

## 正确做法
1. `agent_bus_cursor_executor` 的 `WAKE_PREFIXES` 含 `AGENT_LOOP_WAKE_TG_DM`，`process_tg_dm_wake` 必须跑完交办。
2. 私聊 ack 写「已交执行面」；provenance 用 `dispatched`，别假装 completed。
3. OneHR / TG presence 打卡窗各约 1 小时：上班 09:10-10:10；平日下班 22:00-23:00；周六 19:00-20:00。改 `onehr.env` 后 `launchctl kickstart -k …onehr-checkin`。

## 关联
- `omdb/tgbot/tg_dm_ide_wake.py` · `.claude/database/scripts/notify/agent_bus_cursor_executor.py`
- `~/.dc-platform/config/onehr.env`
