---
date: 2026-10-03
tags: [onehr, session-rotate, self-evolve]
severity: medium
domain: ops
---

# screenshot|macos-privacy|新鲜截图失败先查 Accessibility/Screen Recording 是否信任「又初打卡截图」与 p

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

screenshot|macos-privacy|新鲜截图失败先查 Accessibility/Screen Recording 是否信任「又初打卡截图」与 python 解释器；纯 API checkin 正常不等于截图链路过

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
