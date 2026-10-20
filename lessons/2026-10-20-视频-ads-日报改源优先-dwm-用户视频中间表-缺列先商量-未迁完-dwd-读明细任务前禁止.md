---
date: 2026-10-20
tags: [video-migration,paimon,dwd, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 视频 ADS/日报改源优先 dwm 用户视频中间表，缺列先商量；未迁完 dwd 读明细任务前禁止停拆事件慢 task。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

视频 ADS/日报改源优先 dwm 用户视频中间表，缺列先商量；未迁完 dwd 读明细任务前禁止停拆事件慢 task。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
