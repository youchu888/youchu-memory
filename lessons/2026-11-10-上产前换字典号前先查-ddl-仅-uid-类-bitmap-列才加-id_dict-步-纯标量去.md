---
date: 2026-11-10
tags: [uid-dict,spark,ddl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 上产前换字典号前先查 DDL：仅 uid 类 bitmap 列才加 id_dict 步，纯标量去重人数表不改。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

上产前换字典号前先查 DDL：仅 uid 类 bitmap 列才加 id_dict 步，纯标量去重人数表不改。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
