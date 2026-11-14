---
date: 2026-11-15
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 主人粘贴改定稿并要求上传云端时，先覆盖本地 `reports/日报-YYYY-MM-DD.md` 再上传，并据改定差异更新 lesson

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

主人粘贴改定稿并要求上传云端时，先覆盖本地 `reports/日报-YYYY-MM-DD.md` 再上传，并据改定差异更新 lesson

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
