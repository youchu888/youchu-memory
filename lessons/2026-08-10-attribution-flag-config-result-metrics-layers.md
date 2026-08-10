---
date: 2026-08-10
tags: [attribution, metrics, config, flag, datacheck, 断流]
severity: high
domain: datacheck
---

# 归因核查分层：flag ≠ config ≠ result；metrics 断流要单独盯

## 背景

全链路扫 `dt=2026-08-09`：注册 583 万、`attribution_flag=1` 约 12.3 万 / 53 app，但 `dws_register_attribution_result_d` 仅 254 行 / 7 app；`metrics_d_d` 自 2026-06-29 后再无分区数据。

## 坑 / 错误做法

- 用「全站注册数」或「flag=1 行数」直接对 result 行数，判归因 ETL 丢数
- 只看 result 有数就当归因链路健康，忽略 metrics 空窗
- 客户端已打 flag、配置表未 `is_run=1` 仍期望出 result（如大量 HX-*）

## 正确做法

核查四层分开报：

1. **配置**：`dim.dim_app_attribution_config` 中 `is_run=1`
2. **客户端**：`dwd_user_register_d_v2.attribution_flag=1`
3. **结果**：`dws_register_attribution_result_d`（仅入围 app 的计算输出）
4. **指标**：`dws_register_attribution_metrics_d_d`（看板用；**须单独查 MAX(dt)**）

期望关系：`result.app ⊆ config.is_run=1`；`flag=1` 可远大于 result（门槛/无候选/未开通配置）。  
发现 metrics `MAX(dt)` 远小于 T-1 → 记断流，走发版/补数，不要与 result 混成一条结论。

## 验证（样例日）

- result 7 app 均在 config；metrics `MAX(dt)=2026-06-29`
- session/visit 全量重算 PASS，说明「有数专项」与「归因断流」可并存

## 关联

- 工作簿：metrics_d_d 断流发版进行中
- 报告：`reports/youchu_full_chain/validate_all__2026-08-09__20260810_191802.md`
