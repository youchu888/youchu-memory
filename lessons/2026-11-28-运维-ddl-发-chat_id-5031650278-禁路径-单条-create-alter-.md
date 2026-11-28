---
date: 2026-11-28
tags: [协作DDL交付, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 运维 DDL 发 chat_id=-5031650278；禁路径；单条 CREATE/ALTER 可贴 SQL 或单文件，组合 DROP+CREATE 打一份可

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

运维 DDL 发 chat_id=-5031650278；禁路径；单条 CREATE/ALTER 可贴 SQL 或单文件，组合 DROP+CREATE 打一份可打开文件（优先 .txt）；真人号 Telethon 发送；@wangyi00001 只写生产/测试+执行、SQL 少注释；续跑用独立进程盯 group_raw，不占 tgbot Telethon

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
