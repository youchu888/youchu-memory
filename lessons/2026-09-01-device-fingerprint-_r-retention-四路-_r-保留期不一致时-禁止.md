---
date: 2026-09-01
tags: [uid_map, session-rotate, self-evolve]
severity: medium
domain: ops
---

# device-fingerprint|_r-retention|四路 `_r` 保留期不一致时，禁止用统一全表扫描默认「生涯首次/换号」语义；须显式分路定义或统

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

device-fingerprint|_r-retention|四路 `_r` 保留期不一致时，禁止用统一全表扫描默认「生涯首次/换号」语义；须显式分路定义或统一窗口，并在方案/SQL 注释写死字段含义

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
