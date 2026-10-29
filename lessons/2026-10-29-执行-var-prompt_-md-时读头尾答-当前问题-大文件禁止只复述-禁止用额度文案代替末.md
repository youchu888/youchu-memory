---
date: 2026-10-29
tags: [tgbot-prompt, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 执行 `/var/.../prompt_*.md` 时读头尾答「当前问题」；大文件禁止只复述、禁止用额度文案代替末尾问题的真实答案

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

执行 `/var/.../prompt_*.md` 时读头尾答「当前问题」；大文件禁止只复述、禁止用额度文案代替末尾问题的真实答案

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
