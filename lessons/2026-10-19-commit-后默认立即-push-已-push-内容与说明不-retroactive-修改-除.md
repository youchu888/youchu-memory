---
date: 2026-10-19
tags: [git, session-rotate, self-evolve]
severity: medium
domain: ops
---

# commit 后默认立即 push；已 push 内容与说明不 retroactive 修改，除非用户指定段落并说「改」

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

commit 后默认立即 push；已 push 内容与说明不 retroactive 修改，除非用户指定段落并说「改」

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
