---
date: 2026-09-01
tags: [device-fingerprint, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 设备标签/uid_map 主键用 device_fingerprint，无指纹丢弃；改造顺序 uid_map→dim/dwm/dws，以 bus#7738 覆盖

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

设备标签/uid_map 主键用 device_fingerprint，无指纹丢弃；改造顺序 uid_map→dim/dwm/dws，以 bus#7738 覆盖旧 prod 禁令

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
