---
date: 2026-09-24
tags: [vpn-sync,ovpn,launchd, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 仅当 ovpn 成功导入且 `imported_at` 更新后再写冷却；失败清冷却或勿写；过期旧证禁止「复用跳过导入」并打 ✅

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

仅当 ovpn 成功导入且 `imported_at` 更新后再写冷却；失败清冷却或勿写；过期旧证禁止「复用跳过导入」并打 ✅

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
