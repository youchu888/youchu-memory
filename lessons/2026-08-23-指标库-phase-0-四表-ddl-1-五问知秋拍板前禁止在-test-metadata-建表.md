---
date: 2026-08-23
tags: [metric-library,phase0, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 指标库 Phase 0 四表：DDL §1 五问知秋拍板前禁止在 test metadata 建表；`metric.search` 仍走 `metric_sta

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

指标库 Phase 0 四表：DDL §1 五问知秋拍板前禁止在 test metadata 建表；`metric.search` 仍走 `metric_standard` 即未落地

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
