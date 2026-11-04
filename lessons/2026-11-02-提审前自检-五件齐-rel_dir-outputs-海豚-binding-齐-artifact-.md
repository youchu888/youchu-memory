---
date: 2026-11-02
tags: [dev-session,stage7,rel_dir, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 提审前自检：五件齐、`rel_dir`/outputs/海豚 binding 齐、artifact 非空、本地 SQL 与 test 海豚一致；缺任一项先补再 

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

提审前自检：五件齐、`rel_dir`/outputs/海豚 binding 齐、artifact 非空、本地 SQL 与 test 海豚一致；缺任一项先补再 RP，勿空标 done。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill

## 增补 · 2026-11-04

提审自检再加两条（同日踩坑）：① 归档 session 先 `uncomplete`；② `PUT /full` 合并保留 `dolphin_owned_tasks[env=test]`，禁冲空。详见 `2026-11-04-request-publish禁冲owned与先解归档.md`。
