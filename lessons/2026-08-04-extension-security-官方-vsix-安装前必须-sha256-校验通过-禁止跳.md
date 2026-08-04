---
date: 2026-08-04
tags: [dc-platform, session-rotate, self-evolve]
severity: medium
domain: ops
---

# extension|security|官方 vsix 安装前必须 SHA256 校验通过，禁止跳过校验直接装

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

extension|security|官方 vsix 安装前必须 SHA256 校验通过，禁止跳过校验直接装

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
