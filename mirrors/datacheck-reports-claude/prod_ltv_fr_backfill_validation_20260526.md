# 生产补数 + 血缘 API + 数据核验报告

- **环境**：生产 StarRocks + 生产海豚 `dws_日`
- **补数 cohort**：2025-12-20 ~ 2026-05-26（schedule 2025-12-21 ~ 2026-05-27）
- **海豚**：LTV `21196490850432` TASK_ONLY → 首充 `21196490850433` TASK_POST（串行）

---

## 1. 补数执行

| 任务 | schedule 范围 | 结果 |
|------|---------------|------|
| `dws_user_reg_ltv_d_h` 日批 | 2025-12-21 ~ 2026-04-25 | **126 实例 SUCCESS**（历史段）+ 此前 04-27~05-27 已补 |
| `dws_user_first_recharge_retention_d_h` 日批 | 2025-12-21 ~ 2026-04-25 | **152 实例 SUCCESS**（含同批 filter 内实例） |
| 失败 | — | **0**（本批历史段） |

---

## 2. dc-platform 血缘 API

### 调用

```bash
GET /api/v1/lineage/dws/dws_user_reg_ltv_d_h
GET /api/v1/lineage/dws/dws_user_first_recharge_retention_d_h
GET /api/v1/relations/table/dws/{table}
GET /api/v1/tables/dws.{table}
```

### 返回摘要

| 表 | edge_count | upstream_tables | downstream_tables | related_tasks |
|----|------------|-----------------|-------------------|---------------|
| `dws_user_reg_ltv_d_h` | 0 | [] | [] | — |
| `dws_user_first_recharge_retention_d_h` | 0 | [] | [] | — |

平台元数据 **尚未录入血缘边**（`last_run_at` 2026-05-25，仅表结构/列注释）。表详情 API 可正常返回 38/37 列定义。

### 设计口径血缘（ETL / 文档，供对账）

**`dws_user_reg_ltv_d_h`**

```text
dim.dim_user_all ──────────────┐
dim.dim_region_info_all ───────┤ cohort（register_time）
                               │
dwd.dwd_order_paid_d ──────────┘ pay（uid+amount/100）
         │
         ▼
dws.dws_user_reg_ltv_d_h
```

**`dws_user_first_recharge_retention_d_h`**

```text
dim.dim_user_all ──────────────┐ cohort（first_recharge_time）
dim.dim_region_info_all ───────┤
                               │
dws.dws_app_user_d_h ──────────┘ active_users（strict-channel）
         │
         ▼
dws.dws_user_first_recharge_retention_d_h
```

海豚任务：`dws_日` wf=`20691538136576`；首充日批依赖 `dws_app_user_d_h`（`21497544336640`）。

> 若要在 API 中看到 mermaid 上下游，需 admin 在平台执行血缘同步（OM / lineage prepare）。

---

## 3. 生产库数据核验

### 3.1 覆盖范围

| 表 | min(dt) | max(dt) | 有数据天数 | 说明 |
|----|---------|---------|------------|------|
| `dws_user_reg_ltv_d_h` | **2025-12-20** | **2026-05-26** | **147** | 与 dim 注册日 148 天基本对齐 |
| `dws_user_first_recharge_retention_d_h` | **2025-12-25** | **2026-05-25** | **61** | dim 首充自 12-25 起有量；12-20~12-24 无首充 cohort |

### 3.2 抽样日指标

| dt | LTV new_users | 首充 fr |
|----|---------------|---------|
| 2025-12-20 | 151,668,577 | — |
| 2026-01-15 | 4,138,079 | 20,317 |
| 2026-03-15 | 5,151,261 | — |
| 2026-04-15 | — | — |
| 2026-04-25 | — | — |
| 2026-05-26 | 1,773,149 | — |
| 2026-05-25 | — | 15,637 |

（首充表按「有 cohort 才有行」，无首充日无分区行属正常。）

### 3.3 质量检查

| 检查项 | 结果 |
|--------|------|
| 首充 `fr=0 且 day1>0` | **0 行** |
| 海豚历史补数 FAILURE | **无** |
| LTV 与 dim 注册 cohort 起点 | **2025-12-20 一致** |
| 首充与 dim 首充起点 | **2025-12-25 一致**（dim 12-20~24 首充 count=0） |

### 3.4 合计

| 表 | 合计 |
|----|------|
| LTV `new_users` bitmap 展开合计 | **779,946,186** |
| 首充 `first_recharge_users` | **1,121,899** |

---

## 4. 结论

| 项 | 状态 |
|----|------|
| 分区 2025-12-20 ~ 当前 | ✅ 已建 |
| 历史日批补数 | ✅ SUCCESS |
| 生产数据 LTV 2025-12-20 ~ 2026-05-26 | ✅ |
| 生产数据首充 2025-12-25 ~ 2026-05-25 | ✅（与 dim 一致） |
| API 血缘边 | ⚠️ 平台未同步，已给设计口径 |
| 数据质量异常 | ✅ 未发现 |

---

## 5. 复现 SQL

见各表设计文档 **§8 对账**：

- `ops_system/04.dws/dws_user_reg_ltv_d_h/dws_user_reg_ltv_d_h.md`
- `ops_system/04.dws/dws_user_first_recharge_retention_d_h/dws_user_first_recharge_retention_d_h.md`
