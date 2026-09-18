---
date: 2026-09-18
tags: [datacheck,funnel,video_play, session-rotate, self-evolve]
severity: medium
domain: ops
---

# play > 详情页 UV 时先比 T-2 同口径；若仅 play 跳涨而 detail 不动，查交集/口径实现而非判跑批失败

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

play > 详情页 UV 时先比 T-2 同口径；若仅 play 跳涨而 detail 不动，查交集/口径实现而非判跑批失败

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
