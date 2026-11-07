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

## 增补 · 2026-11-07

Spark 引擎提审/S7 再加硬项：`state_json.stage4_spark.mount.ok==true`（含 group/slot/steps）。缺此项野花向导①直接报「S4 还没挂过调度」，与 test 是否已挂无关。完整清单见 `2026-11-04-request-publish禁冲owned与先解归档.md` 2026-11-07 增补；专题 checklist 见 `2026-11-07-spark-s7-提审前mount与state合并检查.md`。
