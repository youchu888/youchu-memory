---
title: TG/bus 长消息必须分片续发，禁止静默砍尾
date: 2026-09-05
---

# TG / agent-bus 长消息出站

主人钦定（2026-09-05）：消息太长要**分开发**，不要总是 bus/私聊不全。

## 硬规则

1. **禁止** `text[:4096]` / `text[:3500]` 作为出站终态（会砍掉对方要拍板的选项号等）
2. 超长 → **分片续发**（带「续 i/n」），保证全文送达
3. bus 长文优先 `agent_bus_send.py --text-file`；脚本侧也会按 `AGENT_BUS_CHUNK_LEN`（默认 3000）自动分片
4. 对方说截断 → 立刻补发缺段，不要辩解「服务端其实有全文」

## 实现入口

- `omdb/tgbot/tg_text_split.py`
- Bot：`_send_chat_message` / status_mirror `_notify_status`
- Bus：`.claude/database/scripts/notify/agent_bus_send.py`
