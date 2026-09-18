---
date: 2026-09-18
tags: [old-mac,ops, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 判 old-mac 是否存活先看 sync 身份 + bot/poller + youchu-memory，ToDesk 断连单独当远控故障排查

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

判 old-mac 是否存活先看 sync 身份 + bot/poller + youchu-memory，ToDesk 断连单独当远控故障排查

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
