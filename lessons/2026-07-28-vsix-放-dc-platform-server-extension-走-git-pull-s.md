---
date: 2026-07-28
tags: [extension,release, session-rotate, self-evolve]
severity: medium
domain: ops
---

# vsix 放 dc-platform-server/extension/ 走 git→pull→scp；CHcode 即 tq-git dmp/dc-paren

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

vsix 放 dc-platform-server/extension/ 走 git→pull→scp；CHcode 即 tq-git dmp/dc-parent dev，勿与 Desktop 另一 dc-parent 混用

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
