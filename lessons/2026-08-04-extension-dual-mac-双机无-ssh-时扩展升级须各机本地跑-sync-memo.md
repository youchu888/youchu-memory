---
date: 2026-08-04
tags: [dc-platform, session-rotate, self-evolve]
severity: medium
domain: ops
---

# extension|dual-mac|双机无 SSH 时扩展升级须各机本地跑 sync-memory-git + install-dc-extension-la

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

extension|dual-mac|双机无 SSH 时扩展升级须各机本地跑 sync-memory-git + install-dc-extension-latest.sh，装后 Reload Window 并核对版本

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
