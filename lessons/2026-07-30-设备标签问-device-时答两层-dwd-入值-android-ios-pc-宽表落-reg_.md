---
date: 2026-07-30
tags: [device-tag,field-dict, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 设备标签问 device 时答两层：DWD 入值 ANDROID/IOS/PC，宽表落 reg_platform 仅 App/Web 且无 Other

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

设备标签问 device 时答两层：DWD 入值 ANDROID/IOS/PC，宽表落 reg_platform 仅 App/Web 且无 Other

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
