---
date: 2026-10-29
tags: [runner, spark_migrate, ownership, bitmap, 知秋, dws_app_user_d_h, LTV, retention]
severity: high
domain: ops
---

# 活跃/留存/LTV/产品报表指标迁 runner · 知秋独占批次（字典号 bitmap）

## 背景

2026-10-29 工作狂人群内转述知秋定案：一批活跃衍生表迁 pipeline-runner 并切换字典号 bitmap，**全部由知秋一人实施**；他人手上半完成的须停下并交接。与 10-29 工作簿第 16 项「活跃表读者迁 runner」一致，属于海豚→runner 大迁移中的**归属收口**，非单表技术 patch。

## 坑 / 错误做法

- 又初/蓝猫等继续改本批 SQL、发海豚或改 runner 步，与知秋并行 → 口径漂移、重复发版。
- 把 `ads_product_day_stat_d` 误纳入知秋**字典号 bitmap** 改造，或误以为「不迁 runner、永久留海豚」；把 `dws_app_order_d_h` 误纳入知秋收回批次。
- test 未对平就抢 prod，或不等生产 HBase 就绪零星发布。

## 正确做法

**本批（知秋独占 · 迁 runner + 字典号 bitmap）**

| 对象 | 说明 |
|------|------|
| `dws_app_user_d_h` | 切字典号 |
| `dws_app_retention_d_h` | 留存 |
| `dws_app_user_w_d_new` / `dws_app_user_m_d_new` | 周/月活跃 |
| `dws_user_first_recharge_retention_d_h` | 首充留存 |
| `dws_user_reg_ltv_d_h` | 注册 LTV |
| `ads_product_report_metric_d_d` | 含上游 `dwm_app_session_sid_d`、`dws_user_base_daily_d` |

**不在本批**

- `ads_product_day_stat_d`（产品日报）：只出人数、**不存 bitmap**，**不在知秋字典号改造批**；海豚→Spark **迁移仍归原负责人野花**，按原计划推进，≠「留海豚不改」。
- `dws_app_order_d_h`：**仍归蓝猫**，不属于知秋收回批次。

**节奏**：先在 **test** 做完并与现网口径对平；**生产 HBase 服务器到位后**再统一发 prod。

半完成工作：停手，把进度/文件告知知秋由其接续。

## 可复用规则（群提炼）

- `[LESSON: runner迁移·活跃留存LTV批次 | 知秋定案下列表迁 runner 并切字典号 bitmap 由知秋一人做；他人勿改，半完成须停并交接进度与文件]`
- `[LESSON: dws_app_user_d_h / 留存 / 周月活跃 / 首充留存 / 注册LTV | 同属知秋独占 runner 批次，又初侧渠道推广周月等下游读这些表时勿动上游实现]`
- `[LESSON: ads_product_report_metric_d_d | 与上游 dwm_app_session_sid_d、dws_user_base_daily_d 打包在同一批次，非本批负责人勿动]`
- `[LESSON: ads_product_day_stat_d | 仅人数、无 bitmap，不在知秋字典号改造批；Spark 迁移仍归野花按原计划，勿与知秋活跃链批次混淆]`
- `[LESSON: dws_app_order_d_h | 订单日终仍归蓝猫，不属于知秋 2026-10-29 runner 收回范围]`
- `[LESSON: runner迁移·发布节奏 | test 对平现口径后再等 prod HBase 就绪统一发产，禁止本批表零星抢发]`

## 验证

- 改本批表前查本 lesson / 工作簿第 16 项是否仍有效。
- 非知秋账号：本批路径无新 commit / 无海豚或 runner 发布记录。

## 关联

- 群消息 2026-10-29 08:48 工作簿（项 16 表述变更）
- 10-26 bus#11555 LTV r69 有条件通过（设备前 30 日充值算法待业务确认，与本条归属独立）
