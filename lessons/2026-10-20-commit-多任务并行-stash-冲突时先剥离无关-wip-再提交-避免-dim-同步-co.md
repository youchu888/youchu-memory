---
date: 2026-10-20
tags: [git, session-rotate, self-evolve]
severity: medium
domain: ops
---

# commit|多任务并行 stash 冲突时先剥离无关 WIP 再提交，避免 dim 同步 commit 夹带广告等半成品

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

commit|多任务并行 stash 冲突时先剥离无关 WIP 再提交，避免 dim 同步 commit 夹带广告等半成品

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
