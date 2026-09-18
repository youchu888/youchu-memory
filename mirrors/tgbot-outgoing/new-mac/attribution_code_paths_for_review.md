# 注册归因 · 代码路径清单（prod 审核用）

> 根目录：`/Users/mac/Desktop/CHcode`（以下均为相对路径）
> 整理人：又初 · 2026-06-27
> 背景：私聊#13 转问 prod 上线；狂人回复须获知秋拍板。本清单供狂人审核代码范围与影响面。

---

## 1. 核心 ETL（三块：计算 / 回写 / 统计）

| 模块 | 海豚 task | 相对路径 | 说明 |
|------|-----------|----------|------|
| **归因计算** | `dws_register_attribution_result_d` | `ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql` | mvp_v2 两阶段打分；读 `attribution_flag=1` 注册 + 落地页 |
| **渠道回写** | `dim_user_attribution_channel_apply_d` | `ops_system/06.dim/job_dim_user_attribution_channel_apply/dim_user_attribution_channel_apply_d.sql` | `is_rewrite_channel=1` 时 UPDATE `dim.dim_user_all.channel` |
| **看板统计** | `dws_register_attribution_metrics_d_d` | `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/dws_register_attribution_metrics_d_d.sql` | 8 KPI 日汇总；须在结果表+回写之后 |

**调度绑定（task.yaml）**

- `ops_system/04.dws/dws.dws_register_attribution_result_d/task.yaml` → wf `wf_dws_汇总_日`
- `ops_system/06.dim/job_dim_user_attribution_channel_apply/task.yaml` → wf `wf_dws_汇总_日`
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/task.yaml` → workflow 待发布时选定

---

## 2. 是否归因 · attribution_flag 接入（DWD 修改）

| 文件 | 说明 |
|------|------|
| `ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/dwd_user_register_d_v2_daily.sql` | 日批 OVERWRITE；显式列名 INSERT；`CAST(payload.attribution_flag AS INT)` |
| `ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/dwd_user_register_d_v2_hourly.sql` | 小时 INSERT INTO；同上 attribution_flag 解析 |
| `ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/dwd_user_register_d_v2_ddl.sql` | 表 DDL；`attribution_flag int` 列定义 |
| `ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/task.yaml` | 绑定 wf `wf_dwd_事件明细_日` + `wf_用户画像_小时`；test task_code 已登记 |

**Flink 侧类型说明（非 SQL 改码，链路相关）**

- `flink-dwd-fanout/README.md` — upsert 表含 `dwd_user_register_d_v2.attribution_flag INT`

**注意**：`dwd_user_register_d_v2_d_d.sql` 为 TODO 空壳，**非** prod 链路。

---

## 3. DDL / 建表 / 配置种子

| 文件 | 说明 |
|------|------|
| `ops_system/04.dws/dws.dws_register_attribution_result_d/alter_table.sql` | 建 `dim_app_attribution_config` / `dim_app_attribution_time_config`；ALTER 结果表；15 app 白名单种子 |
| `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/dws_register_attribution_metrics_d_d_ddl.sql` | 看板指标表 DDL |
| `ops_system/04.dws/dws.dws_register_attribution_alter_table/task.yaml` | 手工 DDL 任务占位（manual） |
| `ops_system/修改字段长度.sql` | 含 `dws_register_attribution_result_d.uid` 扩长注释（L79，按需执行） |

---

## 4. 文档 / 剧本 / 设计（审核参考，非运行时）

### 4.1 归因结果 + 回写

- `ops_system/04.dws/dws.dws_register_attribution_result_d/归因对接说明.md` — 后端对接、影子期、三层职责
- `ops_system/04.dws/dws.dws_register_attribution_result_d/归因两阶段上线方案.md` — 上线阶段
- `ops_system/04.dws/dws.dws_register_attribution_result_d/spec.md`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/design.md`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/memory.md`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/README.md`
- `ops_system/04.dws/dws.dws_register_attribution_result_d/playbook.md`
- `.claude/database/playbooks/dws.dws_register_attribution_result_d.md` — canonical 核查剧本

### 4.2 看板统计

- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/spec.md`
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/design.md`
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/memory.md`
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/README.md`
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/playbook.md`

### 4.3 历史 lesson / 报告

- `.claude/memory/lessons/20260609-attribution-flag-column-order.md` — 列错位踩坑
- `.claude/memory/lessons/20260605-attribution-test-deploy-backfill.md`
- `.claude/memory/lessons/20260603-attribution-analyze-by-app.md`
- `.claude/memory/feedback_attribution_ua_from_dw_and_focus_ip.md`
- `.claude/database/reports/attribution_per_app_analysis_20260404_20260602.md`

---

## 5. 链路依赖（本次未改码，prod 须已存在）

| 对象 | 角色 |
|------|------|
| `dwd.dwd_user_register_d_v2` | 注册源；`attribution_flag` 入围条件 |
| `dwd.dwd_landing_page_click_d` / `dwd_landing_page_view_d` | 落地页候选 |
| `dim.dim_app_attribution_config` | 白名单 `is_run` / 回写开关 `is_rewrite_channel` |
| `dim.dim_app_attribution_time_config` | 时间窗打分 |
| `dim.dim_user_all` | 回写目标表 |

---

## 6. 当前 prod 策略（影子期）

- 15 app：`is_run=1`，`is_rewrite_channel=0` → **只写结果表，不改用户渠道**
- 开回写：按 app 将 `is_rewrite_channel` 改为 `1`
- prod 上线授权：**知秋拍板**（狂人已转递，见 bus#106）

---

## 7. 明确排除（同名「归因」但非注册归因链路）

以下文件 CTE 名含 `uid_attribution`，指 **PV 用户身份终态归因**，与注册归因无关，**不在本次 prod 审核范围**：

- `ops_system/05.ads/job_ads_app_metrics_daily_d/ads_app_metrics_daily_d.sql`
- `ops_system/05.ads/job_ads_app_metrics_hourly_d/ads_app_metrics_hourly_d.sql`
- `ops_system/05.ads/job_ads_channel_metrics_daily_d/ads_channel_metrics_daily_d.sql`

---

## 8. 文件计数摘要

| 类别 | 数量 |
|------|------|
| 可执行 SQL（ETL+DDL） | 7 |
| task.yaml | 4 |
| 设计/剧本/对接文档 | 15+ |
| lesson/报告 | 5 |
