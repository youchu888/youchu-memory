---
name: feedback_prod_monitor_follow_worker_ant
description: 主人确认 prod 盯盘按狂人安排（告警驱动，不另建夜间全量扫）
type: feedback
---

# 盯盘按狂人安排（告警驱动）

## Why

2026-09-01 主人问「为什么不盯盘 / 和狂人怎么约定」后，明确说「按照狂人的安排来吧」。  
狂人口径（bus#7708/#7742）：检测已在 server_monitor；又初做**处置**不是再检测；确认事故立刻修含改代码，修完再报。

## How to apply

1. **不要**另建「每晚全量扫海豚」定时任务。
2. 收到 `env=prod` 告警 → 按 `playbook_server_monitor_incident.md` part_01→04。
3. 六条判据确认事故 → 立刻修，处理完再报；非事故变更仍等知秋 GO。
4. test 告警一律忽略。
5. old-mac 专责入口；new-mac 只同步 memory/文档。
