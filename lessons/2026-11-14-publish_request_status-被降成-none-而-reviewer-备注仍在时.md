---
date: 2026-11-14
tags: [产发门禁, session-rotate, self-evolve]
severity: medium
domain: ops
---

# publish_request_status 被降成 none 而 reviewer/备注仍在时 i_can_publish_prod=false；须会话持有人

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

publish_request_status 被降成 none 而 reviewer/备注仍在时 i_can_publish_prod=false；须会话持有人 request-publish，审核人只审不发产自救

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
