---
date: 2026-07-01
tags: [agent-bus, worker_ant, feedback]
severity: high
domain: ops
---

# agent-bus 增补：活已干完也必须 reply（旧规则不变）

## 背景

bus#766 要求 test 归因 DDL→发布→补数；又初在 Cursor 会话里已做完，只发了群通知，未对狂人回 bus，导致「为什么不回复」。

**说明**：`ack→干活→reply`、`learn_only`/`不用回` 不回复、`60秒内ACK` 等**原有铁律不变**；本条仅**新增**一种场景的处理。

## 坑 / 错误做法

- 判断「活儿已经干完了」→ 跳过 agent-bus，只私聊/群聊报结果
- 把 Cursor 内口语交付当成 bus 派活结案

## 正确做法

**原有流程照旧**；仅**新增**：

- **若 bus 到达时活已在 Cursor/其他路径做完**：仍 **60 秒内 ACK** → **立刻 reply「已完成」** + 关键证据（DDL/版本/补数 PI/git），不必重复执行
- 群通知与 bus reply **并行**，不互相替代

```bash
python3 .claude/database/scripts/notify/agent_bus_send.py \
  --to worker_ant --kind ack --reply-to-bus-id N --text "[ACK] bus#N 收到"
# 已做完则立刻 reply，附版本号/PI/结论
```

## 验证

- `youchu_ai_outbox` 或 TG 可见 ack + reply，且 `reply_to_bus_id` 指向原 bus
- 狂人侧不再追问「为什么不回复」

## 关联

- `.cursor/rules/agent-bus-session.mdc`
- bus#766 → bus#773 ack / bus#774 结案
