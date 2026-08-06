---
date: 2026-08-06
tags: [dolphin, prod, publish-status, agent-bus, session_duration]
severity: high
domain: ops
---

# 回报「是否已上线」须先验 prod live SQL，禁信平台 pending / 旧 memory

## 背景

bus#6073 知秋问「用户时长过滤 0 秒」是否改完等发。又初凭 session `memory.md` + 平台 `publish_request_status=pending` 回「prod 新 SQL 未发、卡野花」，被主人纠正。

## 坑 / 错误做法

- 只读平台 session：`stage7 in_progress` / `pending` / `publish_runs_count=0` 当真相
- 只读旧 `memory.md`「prod 未发」（08-03/08-04 时点）不复验
- 未拉 `dolphin_get_task_sql(env=prod)`，未查目标表 T-1 / 近几日 `bucket0` / `etl_time`

## 正确做法

回报发布状态前硬核三件（并行）：

1. **prod live SQL**：`dolphin_get_task_sql` 看过滤条件是否已是目标口径（本例 `AND is_valid = 1`，无 `OR duration_bucket=0`）
2. **prod 表探针**：目标分区行数 + 口径探针（本例 session `duration_bucket=0` 行数应为 0）+ 必要时看 `etl_time` 是否新刷
3. **平台 RP**：仅作辅助；`pending` 可与线上已发并存（元数据滞后 / 改派 RP 未关单）

bus 短回也要基于上述实核，错了立刻发更正条，勿等对方再问。

## 验证

本例实核：prod task `180283360953472` live SQL 已 PRD §5.5.4；`dt=2026-08-01~05` session `bucket0=0`，`etl_time≈2026-08-06 18:06`。

## 关联

- session：`ops_system/04.dws/dws_session_duration_d/`（`dev-20260729-002`）
- 错误回执：bus#6075；更正：bus#6076
