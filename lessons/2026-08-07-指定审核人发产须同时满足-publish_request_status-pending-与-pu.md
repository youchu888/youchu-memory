---
date: 2026-08-07
tags: [publish-prod,publish_request_status, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 指定审核人发产须同时满足 publish_request_status=pending 与 publish_reviewer_id=审核人；status=non

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

指定审核人发产须同时满足 publish_request_status=pending 与 publish_reviewer_id=审核人；status=none 时让申请人重提申请

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
