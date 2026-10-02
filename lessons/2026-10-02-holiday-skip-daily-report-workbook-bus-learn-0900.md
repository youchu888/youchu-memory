---
date: 2026-10-02
tags: [daily-report, workbook, worker-ant, learn, holiday, launchd]
severity: high
domain: ops
---

# 假日不写日报 · 群工作簿须 bus 回进展 · 狂人学习改 09:00

## 主人定调（2026-10-02）

1. **法定假 / 请假日：不生产日报**（flush / wake / fallback 全 skip）
2. **「今日工作簿」派单要回**：以前只镜像私聊「处理中」，`try_workbook_progress_reply` 写死 `return False`
3. **向狂人学习改到工作日 09:00**（上午清闲；晚上下班忙）

## 正确做法

| 项 | 做法 |
|----|------|
| 日报 | `.cursor/scripts/_skip_non_workday.py` + 注入 `daily-report-wake/fallback/pre_flush` |
| 工作簿 | Telethon 见簿 → 实查 → **只** `agent_bus_send` 给狂人；正文【簿内主责】+【自开实责】（任务板自开+supplemental）；**不回群、不推「又初→群」私聊** |
| 学习 | `com.youchu.worker-ant-daily-learn` Mon–Fri 09:00；假日 skip；先发 bus 再 wake |

## 验证

```bash
python3 .cursor/scripts/_skip_non_workday.py   # 假日打印 reason、exit 0
rg 'group→bus ok|workbook-progress' /tmp/tgbot-dc.log | tail
launchctl list | rg worker-ant-daily-learn
plutil -p ~/Library/LaunchAgents/com.youchu.worker-ant-daily-learn.plist | rg Hour
```

## 关联

- `feedback_workbook_progress_list_plus_owned_cutoff.md`
- lesson `2026-09-05-workbook-no-group-alarm-reply-on-bus.md`
- lesson `2026-09-29-worker-ant-learn-must-autosend-bus.md`
