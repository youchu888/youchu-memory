---
date: 2026-10-07
tags: [ethan-jobs-watch, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 第三国远程与到岗类一律不推；「无需到岗」不拦；改 `ethan_channel_bigdata_jobs.py` 后重启 watch

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

第三国远程与到岗类一律不推；「无需到岗」不拦；改 `ethan_channel_bigdata_jobs.py` 后重启 watch

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
