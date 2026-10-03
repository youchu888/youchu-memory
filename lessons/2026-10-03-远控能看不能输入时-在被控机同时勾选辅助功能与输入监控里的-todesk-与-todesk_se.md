---
date: 2026-10-03
tags: [macos-todesk, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 远控能看不能输入时，在被控机同时勾选辅助功能与输入监控里的 ToDesk 与 ToDesk_Session，退出 ToDesk 后重连

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

远控能看不能输入时，在被控机同时勾选辅助功能与输入监控里的 ToDesk 与 ToDesk_Session，退出 ToDesk 后重连

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
