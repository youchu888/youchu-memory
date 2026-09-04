---
date: 2026-09-05
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# resume|agent-bus|用户只说「日报呢」时先澄清是要查定稿/TG、生成日报还是上传云端，勿默认走上传

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

resume|agent-bus|用户只说「日报呢」时先澄清是要查定稿/TG、生成日报还是上传云端，勿默认走上传

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
