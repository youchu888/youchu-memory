---
date: 2026-07-01
tags: [attribution, prod, test, ddl, schema, dolphin, rewrite_status, worker_ant, insert_overwrite]
severity: high
domain: sql
source: worker_ant prod incident + bus#662/663
---

# DDL 加 rewrite_status 未同步 result ETL SELECT 致 28≠27 全链挂

## 背景

`rewrite_status`（TINYINT，1=成功/0=失败/NULL=不适用）按 uid 落在 `dws.dws_register_attribution_result_d` 第 28 列（1–27 为 dt…created_at）。test 影子期已 ALTER + 发布 channel_apply；prod 亦曾半上线 DDL。bus#662/663 锁定 test 侧 result/metrics=0 根因与 prod **同一坑**。

## 坑 / 错误做法

1. 表已 **28 列**（含 `rewrite_status`），`dws_register_attribution_result_d` ETL 仍是 `INSERT OVERWRITE` **无显式列清单**、SELECT **27 列**。
2. StarRocks analyze 拒：`Inserted target column count: 28 doesn't match select/value column count: 27` → task **0 秒 FAILURE**（state=6，重试仍挂），**不是 DAG 卡住**。
3. 表象：result 空 → metrics/app_user 全 0 行；易误判为拓扑或依赖问题。
4. 半上线：只 ALTER 表、不同批改写表 ETL / 未核列数。

## test 实测（bus#662/663）

- task：`dws_register_attribution_result_d`（wf code=21869820140416，instance 55518/55521）
- 缺列：SELECT 尾部漏第 28 列 `rewrite_status`

## 正确做法

1. **ALTER 前**：`DESC` + `rg` / 血缘查所有 INSERT OVERWRITE 写该表的 task。
2. **修法（优先，建议先解 test）**：SELECT 末尾补第 28 列，列序对齐 DDL，例如 `CAST(NULL AS TINYINT) AS rewrite_status`（下游 channel_apply 再写 1/0）；或 INSERT 改**显式 28 列清单**。
3. **备选**：DROP COLUMN `rewrite_status` — 牵涉知秋对灰度列保留决策，**勿擅自**。
4. **DDL + 所有写表 ETL 同批发布**；test 验通再考虑 prod，且 prod 须知秋/狂人令。
5. **修复后顺序**：result **TASK_ONLY** T-1 → 确认 SUCCESS + 分区有行 → 再验 metrics/app_user。

## 验证

- 发布前：`DESC` 列数 = SELECT 列数（或显式 INSERT 列清单一致）。
- 发布后：查 DS task instance state≠FAILURE；`SELECT COUNT(*) FROM … WHERE dt=T-1` 非 0。
- 日志关键词：`column count mismatch` / `doesn't match select`。

## 知秋钦定硬规则（2026-07-01 全员）

1. ALTER 前第一动作：查写表 ETL（尤其无列清单 INSERT OVERWRITE）。
2. 需改 ETL → DDL+ETL 同批上线，禁半上线。
3. 影子/gated DDL 禁偷上 prod。
4. 修法首选 INSERT 显式列清单或 SELECT 补列并核列数。

### rewrite_status 两阶段语义（bus#704 / 知秋钦定，待 ETL 落地）

- **第 1 步识别（dim_user_all 构建）**：写初始 `rewrite_status` + 理由，如 `organic-待归因`、`已有真实渠道-免归因`、`自然增长归并organic`。
- **第 3 步回写（channel_apply）**：更新为回写态 + 理由，如 `已回写-命中X渠道`、`未回写-无候选/低置信/app未灰度/归因仍organic`。
- 用途：单用户从识别到回写全程可审计 + 统计各态数量；列在 dim_user_all/result_d 等链上表，**两阶段都要能写理由**（平台 doc 1.5 + 第3步已更新）。

## 关联

- 同类：[20260609-attribution-flag-column-order.md](./20260609-attribution-flag-column-order.md)
- DAG 验收：[2026-07-01-attribution-dag-v74-topology-datacheck.md](./2026-07-01-attribution-dag-v74-topology-datacheck.md)
- ETL：`ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql`
- DDL：`ops_system/04.dws/dws.dws_register_attribution_result_d/alter_table.sql`
- apply：`ops_system/06.dim/job_dim_user_attribution_channel_apply/dim_user_attribution_channel_apply_d.sql`

