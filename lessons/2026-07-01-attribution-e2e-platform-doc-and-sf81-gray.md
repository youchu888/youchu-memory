---
date: 2026-07-01
tags: [attribution, gray, SF-81, test, platform-doc, complement]
severity: medium
domain: ops
---

# 归因 E2E 平台文档 + SF-81 test 灰度对数

## 背景

bus#706 批准 SF-81 test `is_rewrite_channel=1` 开灰；要求 TASK_ONLY 验证三条（总量守恒 / organic 搬迁 / 非灰度 app 不变）。用户要求读平台文档 `attribution_end_to_end_complete` 并沉淀记忆。

## 坑

- test `dim_user_all` 对 SF-81 仅 1 行，result_d 有 516 条 success → **0 organic 可归因**，直接跑 apply 无改写。
- 平台 raw 文档需 Bearer token：`GET /api/v1/platform/docs/raw/attribution_end_to_end_complete`。
- `agent_bus_send.py` 与部署态 `agent_bus_state` 曾不同步；ACK 可用平台 API 直发。

## 正确做法

1. 读文档：token + raw API；沉淀到 `reference_attribution_end_to_end_complete.md`。
2. 验证性补数：从 prod 同步 SF-81 success uid 的 `dim_user_all`（organic）到 test。
3. TASK_ONLY 仅跑 `channel_apply`（code `21962007716224`），schedule = 业务日+1 05:20。
4. 三条验收 + 非灰度 app（如 SF-01）channel 分布前后对比。

## 验证（2026-06-28 · SF-81 · test）

| 检查 | 结果 |
|------|------|
| 总量守恒 | 517→517 ✅ |
| organic 搬迁 | 516 organic→真实渠道；516 uid channel=attributed_channel ✅ |
| 非灰度不变 | SF-01 分布前后一致 ✅ |

## 关联

- 记忆：`~/.dc-platform/memory/reference_attribution_end_to_end_complete.md`
- 快速入口：`~/.dc-platform/memory/reference_attribution_p0_quickstart.md`
- 全日归档：`~/.dc-platform/memory/sessions/2026-07-01-attribution-p0-daily-archive.md`
- 灰度剧本：`.claude/database/playbooks/dws.dws_register_attribution_gray_verify.md`
- 脚本：`dc-platform-server/scripts/reorder_wf_attribution_first.py`（test task codes）
- runbook：`.claude/database/scripts/attribution_runbook.py`
