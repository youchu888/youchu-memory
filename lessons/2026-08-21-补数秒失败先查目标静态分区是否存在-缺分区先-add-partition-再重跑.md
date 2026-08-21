---
date: 2026-08-21
tags: [complement,partition, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 补数秒失败先查目标静态分区是否存在，缺分区先 ADD PARTITION 再重跑

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

补数秒失败先查目标静态分区是否存在，缺分区先 ADD PARTITION 再重跑

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
