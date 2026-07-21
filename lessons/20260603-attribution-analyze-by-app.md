---
date: 2026-06-03
tags: [attribution, datacheck, prod, per-app]
severity: medium
domain: ops
---

# 注册归因分析必须按 app 独立

## 背景
`dws_register_attribution_result_d` 多 app 共用 default 门槛 70，但 `dim_app_attribution_config` 各 app `is_active`/阈值不同；无候选占比、成功因子差异极大，混算会误判。

## 正确做法
1. 先按 app：`eligible`（`dwd_user_register_d_v2` ios+organic+is_run）→ `in_output` → `success` / `no_candidate`。
2. 成功：看 `score` 分布 + `reg_*` vs `hit_*` 维度匹配率 + `source_event_type`（点击 vs 浏览）。
3. 失败：表内 `score_below_threshold`（分桶 40/60/10）+ 表外 `no_candidate`（注册数 − 输出表）。
4. 配置：`dim_app_attribution_config` 本 app `is_active=1` 否则回落 default（70/60/20/…）。

## 验证
同一 app 成功行 `avg(score)` 应 ≥ 该 app 有效 `min_threshold`；JHA 成功多为 120（品牌+系统+时间），DX-002 成功多为 40（仅时间，阈值 40）。

## 关联
- ETL：`ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql`
- 报告：`.claude/database/reports/attribution_per_app_analysis_20260404_20260602.md`
