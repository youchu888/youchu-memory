---
date: 2026-09-28
tags: [tg, telethon, visible-online, onehr, punch]
severity: medium
domain: ops
---

# TG 绿点跟 OneHR 打卡：上班后间歇绿，下班后灭，离线≤15分钟

## 背景

固定 09:00–22:30 窗口不准；应以上班/下班打卡为准。早先「离线≤20 分钟 + 固定钟点」草案作废。

## 正确做法

- 读 `~/.dc-platform/onehr/schedule_state.json`
  - `checkin == 今日`（或 `_manual_checkin_今日`）且 `checkout != 今日` → 可绿
  - 否则灭
- 窗口内：绿 3–12 分钟 ↔ 灭 1.5–15 分钟（`MAX_OFFLINE_SEC=900`）
- 挂 dispatch Telethon，`UpdateStatus`，不断 TCP
- 模块：`omdb/tgbot/tg_visible_online.py`；runtime 经 App Support deploy

## 验证

```bash
rg 'visible-online' /tmp/tgbot-dc.log | tail
# gate=onehr-punch；今日已上班未下班应见 burst
python3 -c "import json;print(json.load(open('$HOME/.dc-platform/onehr/schedule_state.json')))"
```

## 关联

- 取代固定钟点 / 20 分钟离线草案
- 旧极客计划见 `2026-08-17-tg-visible-online-follows-jike-punch-plan.md`
- 双连抢 session 见 `2026-08-03-查岗未回因work_online克隆session双连抢更新.md`
