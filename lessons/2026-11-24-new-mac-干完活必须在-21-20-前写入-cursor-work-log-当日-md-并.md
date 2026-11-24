---
date: 2026-11-24
tags: [daily-report,dual-mac,work-log, session-rotate, self-evolve]
severity: medium
domain: ops
---

# new-mac 干完活必须在 21:20 前写入 `.cursor/work-log/当日.md` 并参与 flush；只停在 transcript 里 old

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

new-mac 干完活必须在 21:20 前写入 `.cursor/work-log/当日.md` 并参与 flush；只停在 transcript 里 old-mac 汇稿必漏，与双机 sync 是否正常无关

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
