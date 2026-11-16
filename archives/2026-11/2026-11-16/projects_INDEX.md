# DC Platform 项目索引

> 所有 Dev Session / 数据开发任务统一归属 **dc-platform**。
> 公共记忆：`~/.dc-platform/memory/` · 经验沉淀：`~/.dc-platform/memory/lessons/`
> 维护人：**又初** · 更新：2026-06-17

## 工作区注册

| 工作区 | 路径 | 知识库 | 状态 |
|--------|------|--------|------|
| CHcode（dc-parent） | `/Users/mac/Desktop/CHcode` | `knowledge.md` + `.claude/database/` | 活跃 |

## 活跃 Dev Session

| session | 目录 | project | owner | 状态 |
|---------|------|---------|-------|------|
| dwd_user_register_d_d | `CHcode/dwd_user_register_d_d/` | dc-platform | 又初 | 新建 |
| dw明细表迁移 | `CHcode/.cursor/dev-sessions/dw明细表迁移/` | dc-platform | 又初 | phase2 进行中 |
| dws_user_first_recharge_retention_d_h | `CHcode/.cursor/dev-sessions/dws_user_first_recharge_retention_d_h/` | dc-platform | 又初 | 进行中 |
| dev-20261016-006 【归因看板】 | `ops_system/spark_migrate/ads_register_attribution_board_d_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-007 【归因无候选】 | `ops_system/spark_migrate/ads_register_attribution_no_candidate_reason_d_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-008 【渠道日活】 | `ops_system/spark_migrate/dws_app_channel_dau_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-009 【行为页漏斗】 | `ops_system/spark_migrate/ads_action_page_funnel_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-010 【用户路径】 | `ops_system/spark_migrate/ads_user_page_path_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-011 【用户路径名称】 | `ops_system/spark_migrate/ads_user_page_path_name_d_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-012 【页面热力】 | `ops_system/spark_migrate/ads_page_heatmap_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-013 【渠道日指标】 | `ops_system/spark_migrate/ads_channel_metrics_daily_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-014 【渠道汇总】 | `ops_system/spark_migrate/ads_channel_summary_d/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-017 【部门推广周汇总】 | `ops_system/spark_migrate/ads_dept_promotion_summary_w/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-018 【部门推广月汇总】 | `ops_system/spark_migrate/ads_dept_promotion_summary_m/` | dc-platform | 又初 | Spark 阶段 1 |
| dev-20261016-019 【页面访问】 | `ops_system/spark_migrate/dws_app_page_visit_d_d/` | dc-platform | 又初 | Spark 阶段 1，缺页面停留实时表 |

## 海豚项目映射

Dev Session 的 `task.yaml.project` 统一写 `dc-platform`；海豚调度仍用业务项目名：

| dc-platform session | 海豚 project_name | 说明 |
|---------------------|-------------------|------|
| dw明细表迁移 | 运营系统 | test/prod 双环境 |
| dws_user_first_recharge_retention_d_h | 运营系统 | test/prod 双环境 |
| dwd_user_register_d_d | （发布时选定） | 待绑定 |

## 记忆分层

| 层 | 路径 | 用途 |
|----|------|------|
| 公共记忆 | `~/.dc-platform/memory/*.md` | 跨 workspace 方法论 / 协作偏好 |
| 经验 lesson | `~/.dc-platform/memory/lessons/` | 踩坑与运维捷径（自我进化） |
| 会话记忆 | `<session>/memory.md` | 单需求跨 stage 决策 |
| 存档 | `~/.dc-platform/memory/archives/YYYY-MM/` | 定期快照 |

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-17 | 新增 CHcode 目录索引；清理 -d / .dc-platform / .github |
| 2026-06-17 | 初建索引；三 session 统一 project=dc-platform；公共记忆迁至 ~/.dc-platform/memory/ |

## 代码库目录地图

详见 [`project_chcode_directory_index.md`](../../memory/project_chcode_directory_index.md)（又初查路径先读此文件）。

### 快速分区

| 分区 | 路径 | 用途 |
|------|------|------|
| ETL 主树 | `ops_system/` + `db/` | SQL/DDL，必须双扫 |
| 数据库知识 | `.claude/database/` | 别名、元数据、playbooks、reports |
| Agent 配置 | `.cursor/` + `~/.dc-platform/` | 规则、记忆、hooks、session |
| 海豚运维 | `dolphin_ops/` | 发布、补数脚本 |
| 平台源码 | `vscode-extension/` `dc-platform-server/` | AI 禁改 |
| Java 服务 | `event-*` `ops-api-service` `dc-flink-*` | Maven 多模块 |
| Dev Session | `dwd_user_register_d_d/` `.cursor/dev-sessions/` `pending/` | 七步流工件 |
