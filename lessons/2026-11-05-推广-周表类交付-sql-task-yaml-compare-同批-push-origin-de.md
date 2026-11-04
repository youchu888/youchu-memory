---
date: 2026-11-05
tags: [git-audit-gate, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 推广/周表类交付：SQL+task.yaml+compare 同批 push origin/dev，缺 push 不进狂人审核

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

推广/周表类交付：SQL+task.yaml+compare 同批 push origin/dev，缺 push 不进狂人审核

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
