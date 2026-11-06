---
date: 2026-11-07
tags: [datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ctr-exposure|tracing|当单 App 在 dw 中缺 `app_pageitem_exposure` 但同 App 其它事件正常、且其它 Ap

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ctr-exposure|tracing|当单 App 在 dw 中缺 `app_pageitem_exposure` 但同 App 其它事件正常、且其它 App 有曝光时，先定责为 App 埋点/SDK，再考虑数仓链路

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
