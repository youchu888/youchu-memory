---
date: 2026-11-09
tags: [群聊@, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 禁止 @ 不在当前群的人；斯科特不在群，Fanout/Flink 升级改走有权限的人或 bus，禁止群里 @斯科特

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

禁止 @ 不在当前群的人；斯科特不在群，Fanout/Flink 升级改走有权限的人或 bus，禁止群里 @斯科特

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
