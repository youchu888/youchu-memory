---
name: feedback_agent_bus_action_items_must_work
description: 狂人 bus 夹带动作清单时必须干活，禁止快车道已知悉空结案
---

# 狂人 bus：有动作就干，禁止「已知悉」

主人 2026-09-12 批评：回「收到，已知悉」等于没干活。狂人安排的事要马上做，并沉淀经验。

- 默认 `work`：ACK 一行 → 查库/贴 SQL/停手都在同会话做完 → reply 带材料结案
- `reply_only` 仅当狂人写明不用做/先待命，且正文没有「贴 bus / 要核 / 确认环境」
- 「pending 别动」「HOLD」是指令，不是整封信放假；夹带 checklist 仍按 work
- 禁止快车道模板「已知悉 / 待命 / rest」代替交付
