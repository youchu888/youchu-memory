---
date: 2026-09-01
tags: [fingerprint,uid-map,HOLD, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 指纹/uid_map 本地改完须 push 并请知秋再审 PASS 后才可沙箱四步；未 PASS 前 dim/dwm/宽表一律 HOLD

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

指纹/uid_map 本地改完须 push 并请知秋再审 PASS 后才可沙箱四步；未 PASS 前 dim/dwm/宽表一律 HOLD

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
