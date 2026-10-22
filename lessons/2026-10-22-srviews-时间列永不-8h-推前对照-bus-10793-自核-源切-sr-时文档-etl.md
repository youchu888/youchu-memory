---
date: 2026-10-22
tags: [dim_channel_info_all_snap, session-rotate, self-evolve]
severity: medium
domain: ops
---

# srViews 时间列永不 -8h，推前对照 bus#10793 自核；源切 SR 时文档/ETL 须写明 INSERT-only 导致字段过期风险，直至 SR

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

srViews 时间列永不 -8h，推前对照 bus#10793 自核；源切 SR 时文档/ETL 须写明 INSERT-only 导致字段过期风险，直至 SR 写入模型改为全量/可更新。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
