---
date: 2026-06-30
tags: [attribution, rewrite_status, rewrite_reason, archive, channel_apply]
maintainer: 又初
source: bus#581 存档提醒 · 材料已交 worker_ant 转知秋
---

# 2026-06-30 归因档 · rewrite_status 回写方案

> **用途**：知秋/狂人问「回写状态落哪、怎么取值」时读本文；完整核查见 playbook。

## 一、两段 SQL 路径

| 阶段 | 海豚 task | SQL 路径 | 职责 |
|------|-----------|----------|------|
| **第 2 步·归因计算** | `dws_register_attribution_result_d` | `ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql` | INSERT 29 列显式清单；识别阶段写 `rewrite_reason`；`rewrite_status` INSERT 时为 `NULL AS rewrite_status` |
| **第 3 步·渠道回写** | `dim_user_attribution_channel_apply_d` | `ops_system/06.dim/job_dim_user_attribution_channel_apply/dim_user_attribution_channel_apply_d.sql` | Step1 UPDATE `dim.dim_user_all.channel`；Step2 UPDATE `result_d.rewrite_status` + `rewrite_reason` |

DDL / 加列：`ops_system/04.dws/dws.dws_register_attribution_result_d/alter_table.sql`

task.yaml：`ops_system/04.dws/dws.dws_register_attribution_result_d/task.yaml`（含 apply 子任务引用）

## 二、rewrite_status 取值枚举

字段：`dws.dws_register_attribution_result_d.rewrite_status` · `TINYINT`

| 值 | 含义 | 写入方 |
|----|------|--------|
| **1** | 回写成功（`dim_user_all.channel` 已变为 `attributed_channel`） | apply Step2 |
| **0** | 回写失败（归因 success 但 channel 未变更） | apply Step2 |
| **NULL** | 不适用 | apply Step2 判定跳过 |

**NULL 适用条件**（任一即 NULL，不覆盖已有真实渠道）：

- `is_rewrite_channel = 0`（app 未开灰度 / 影子期）
- `attribution_status <> 'success'`
- `attributed_channel` 为空或 organic
- `dim_user_all.channel` 已有非 organic/natural/self/unknown 且 ≠ `attributed_channel`

> 设计决策（私聊#30 / worker_ant 审核 bus#518）：**status 落结果表**，不加 `dim_app_attribution_config`。

## 三、rewrite_reason 取值枚举（apply Step2）

| reason 文案 | 触发条件 |
|-------------|----------|
| `未回写-app未灰度` | `is_rewrite_channel = 0` |
| `未回写-无候选` | unattributed + `no_candidate` |
| `未回写-低置信` | unattributed + `score_below_threshold` |
| `organic-待归因` 等 | 其他非 success（保留 result 识别阶段 reason） |
| `未回写-归因仍organic` | success 但 attributed 仍 organic |
| `已有真实渠道-免归因` | 用户已有非 organic 渠道且 ≠ attributed |
| `已回写-命中{channel}` | 回写成功 |
| `未回写-渠道未变更` | success 但 dim channel 未更新 |

识别阶段 reason 由 result ETL 在 INSERT 时写入；apply 回写阶段可覆盖/补充。

## 四、DAG 与验数基准

- 顺序：**result → apply → metrics**（禁止单独重跑 result，OVERWRITE 会清 status）
- 影子期基准（test 2026-06-28）：`is_rewrite_channel=0` → 全分区 `rewrite_status` NULL（567 行）
- 灰度验数三条：总量守恒 / organic 搬迁 / 非灰度 app 不变 → playbook `dws.dws_register_attribution_gray_verify.md`

## 五、当晚约束（06-30）

- **test only，零 prod**
- 材料已由 worker_ant 转知秋答疑；后续 prod 发布等知秋令

## 六、后续归档

- 07-01 进展 → [`2026-07-01-attribution-p0-daily-archive.md`](2026-07-01-attribution-p0-daily-archive.md)
- 快速入口 → [`../reference_attribution_p0_quickstart.md`](../reference_attribution_p0_quickstart.md)
