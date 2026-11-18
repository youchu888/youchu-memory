---
date: 2026-11-18
tags: [agent-bus, butler, worker_ant, delivery, silent-drop, bus-13925]
severity: high
domain: ops
---

# butler 收件端会静默丢掉 [REPLY]/[ACK] 与 kind=reply（bus#13925）

## 背景

知秋/工作狂人通知：butler 收件端有 bug（码上飞在修）。正文以 `[REPLY]` / `[ACK]` 开头，或 `payload.kind=reply` 的消息会被当**静默件丢掉**，狂人 inbox 收不到。当晚 bus#13908 即因此丢失，靠又初重发的 #13915（无前缀可达稿）才补上。

## 坑 / 错误做法

- 回狂人时正文加 `[REPLY]` / `[ACK]` 前缀
- `--kind reply`（脚本默认就是 reply，会写入 `payload.kind`）
- 以为 `{"ok": true, "dropped": "silent"}` 等于对方已读

## 正确做法（修好前临时）

1. 正文**直接写内容**，禁止以 `[REPLY]` / `[ACK]` 开头
2. `--kind` 用 `progress`（或非 `reply`），**不要** `reply`
3. 例：
   ```bash
   python3 .claude/database/scripts/notify/agent_bus_send.py \
     --to worker_ant --kind progress --reply-to-bus-id N \
     --text "bus#N 已处理：……"
   ```
4. 因非 `reply` 不会自动结案：出站成功且对方能收后，再本地 `mark_processed`
5. 码上飞修好并经狂人确认可恢复 `[REPLY]`/`kind=reply` 后再改回常规流程

## 验证

- 出站结果有真实 `id`，且 **无** `"dropped": "silent"`
- 狂人 inbox / 群侧确认收到；对方能针对内容回复

## 关联

- `2026-11-18-bus未送达401须重发或群贴要点-bus13908.md`（表象含 401/未推送；本条为 butler 静默丢弃根因）
- `.claude/database/scripts/notify/agent_bus_send.py`（默认 `--kind reply`）

## 变更记录

- 2026-11-18：自 bus#13925 沉淀。
