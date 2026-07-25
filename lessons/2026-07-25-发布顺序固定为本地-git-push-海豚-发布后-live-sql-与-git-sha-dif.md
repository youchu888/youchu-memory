---
date: 2026-07-25
tags: [publish,dolphin,git, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 发布顺序固定为本地→git push→海豚，发布后 live SQL 与 git SHA diff 为空才算完，汇报必带 commit SHA

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

发布顺序固定为本地→git push→海豚，发布后 live SQL 与 git SHA diff 为空才算完，汇报必带 commit SHA

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
