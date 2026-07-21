---
date: 2026-07-01
tags: [attribution, dim_user_all, channel_apply, gray, settlement, platform-doc]
domain: ops
source_slug: attribution_end_to_end_complete
source_url: http://54.255.236.159:8012/library/attribution_end_to_end_complete
source_updated: 2026-07-01 11:03:51
maintainer: 又初
---

# 渠道归因 · 端到端完整方案（平台文档沉淀）

> **Canonical 来源**：开发平台 slug `attribution_end_to_end_complete`（id=34）。  
> **刷新**：闲暇时 `GET /api/v1/platform/docs` 看 `updated_at`；有变则重拉 raw 并更新本文件 `source_updated` + 变更记录。

## 一句话

归因开启后，把原本 **organic** 用户按注册时落地页点击（IP/设备匹配）反推真实投放渠道，**回写 `dim_user_all.channel`**；此后该用户所有行为在结算里算到归因后渠道。

## 0 点后四步串行（铁律）

| 步 | 任务 | 产出/动作 |
|----|------|-----------|
| 1 识别客户 | `dim_user_all` 构建（小时+日） | PK 去重、**first-non-organic-wins** 定初始 `channel`；`register_channel` 永不变；**natural/self → organic 归并落第 1 步**（知秋 2026-07-01 定） |
| 2 归因计算 | `dws_register_attribution_result_d` | organic 用户反推 `attributed_channel` + 置信度；28 列含 `rewrite_status` |
| 3 归因回写 | `dim_user_attribution_channel_apply_d` | ① UPDATE `dim_user_all.channel` + `channel_updated_time=register_event_time`；② 回标 `result_d.rewrite_status`（两阶段语义，apply 侧待补） |
| 4 结算 | 结算 7 表 | `COALESCE(dua.channel, NULLIF(TRIM(src.channel),''), 'organic')`；排在回写后 |

**预处理输入**（0 点已就绪）：`dw_user_event_detail`（落地页/投放）、`dws_settlement_detail`（注册/付费）。

**test** `wf_dws_汇总_日` v74+ 已按「归因→回写→下游」排 DAG；**prod 一律等知秋令**。

## 两个 channel 列

- **`channel`**：工作渠道；第 3 步 UPDATE 目标；结算 JOIN 取值。
- **`register_channel`**：原始注册渠道；归因永不改。

## 第 3 步回写 SQL 口径（钉死）

```sql
-- 仅灰度 app；仅非 organic 归因结果；仅当前 channel 为 organic/空
WHERE c.is_rewrite_channel = 1
  AND r.attributed_channel IS NOT NULL AND TRIM(r.attributed_channel) <> ''
  AND LOWER(TRIM(r.attributed_channel)) <> 'organic'
  AND (dim_user_all.channel IS NULL OR TRIM(dim_user_all.channel)='' OR dim_user_all.channel = 'organic')
```

## 灰度（`dim_app_attribution_config.is_rewrite_channel`）

逐 app 置 1 → 当晚回写仅该 app → **对数四条**：① app 内 channel 总量守恒；② 未开灰度 app 不变；③ 抽 uid organic→归因后；④ 无 uid 指标不变。回滚置 0（已回写 channel 因 first-non-organic-wins 会保留，需单独复原）。

## 结算 7 表（千行负责）

`dws_app_channel_summary_d/_h`、`dws_app_channel_deduction_h`、`dws_user_promotion_behavior_charge_h/_d`、`dws_user_promotion_behavior_h/_d`。ADS `ads_channel_promotion_summary` 继承。分析类 funnel/metrics **本轮不改**。

## 分工（知秋 2026-07-01）

| 范围 | 负责人 |
|------|--------|
| 第 4 步结算 7 表 | 千行 |
| 识别/归因/回写/归因统计 | 又初 |

## P0 本轮边界（2026-07-01 收尾）

- **natural/self→organic**：已在 `dim_user_all` daily/hourly + `dwd_user_register_d_v2` 归并。
- **rewrite_status + rewrite_reason 两阶段**：result_d INSERT 写识别理由；apply 更新 1/0 + 回写理由。
- **prod DAG**：归因链单独比对；**不改 prod 旧顺序**。
- **结算 7 表**：千行负责，又初不动。

## 对数验收 SQL 速查

```sql
-- 可归因 organic 用户数（回写前）
SELECT COUNT(*) FROM dws.dws_register_attribution_result_d r
JOIN dim.dim_user_all u ON r.uid=u.uid AND r.app_id=u.app_id
WHERE r.app_id=? AND r.dt=? AND r.attribution_status='success'
  AND (u.channel='organic' OR u.channel IS NULL OR TRIM(u.channel)='')
  AND LOWER(TRIM(r.attributed_channel))<>'organic';

-- 回写命中
SELECT COUNT(*) FROM ... WHERE u.channel = r.attributed_channel;
```

## test 补数

- 归因链 TASK_ONLY：`task_codes` = result / channel_apply / metrics（test WF 见 `reorder_wf_attribution_first.py`）。
- test `dim_user_all` 常缺用户 → 从 prod 同步 success uid 的 dim 行后再跑 apply（验证性补数，不违反 test-HOLD）。

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-07-01 | 初版沉淀；bus#706 SF-81 test 灰度 TASK_ONLY apply 516/516 改写通过 |
