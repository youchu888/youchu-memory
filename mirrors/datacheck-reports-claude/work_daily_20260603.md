# 工作日报

| 项 | 内容 |
|----|------|
| **日期** | 2026-06-03（周三） |
| **环境** | 生产 / 测试 StarRocks、生产&测试海豚、本仓库 `CHcode` |
| **关联数据日报** | [生产数据日报](./prod_daily_report_20260603.md)（账期 06-02 + 当日切片） |

---

## 一、今日工作摘要

围绕 **海豚调度与绑定**、**LTV 生产补数**、**注册归因全量分 app 分析**、**仓库与文档沉淀** 四条线完成排查、补数、报告与提交；生产核心宽表账期至 **2026-06-02**，归因日批 **06-03 尚未产出**。

---

## 二、已完成事项

### 2.1 海豚与平台

| 事项 | 结果 |
|------|------|
| 测试环境批量绑定 SQL 任务 | 测试项目下 **81** 个任务与仓库绑定；`wf_用户活跃留存_小时` **7** 个任务（含 LTV/留存/漏斗等）全部绑定 |
| Cursor 扩展 | 安装 `dc-platform-0.0.77.vsix` |
| 测试海豚巡检 | `wf_用户活跃留存_小时` v15 整体 SUCCESS；**16:30** 仅 `dws_user_reg_ltv_d_h` 失败（StarRocks Connection refused，属基础设施） |
| 小时 DAG 与血缘核对 | 对照 SQL 上游：LTV/订单/漏斗/财务 **不应** 串在 user→retention 等无依据边上；建议改为并行 + `user→retention/first_recharge` |
| 生产 LTV 补数 | 无 `dolphin_ods` CLI，改用 **生产 Dolphin API**（项目 `20524837077760`）：`dws_日` @ 05-28 05:20、`dws_小时` @ 05-27 07:30–23:30，**全部 SUCCESS** |
| 生产 LTV 验证 | `dt=2026-05-27`：`new_users` 由 0 恢复，UC-01 对齐 **4,734,545** |

### 2.2 数据问题排查与对账

| 事项 | 结果 |
|------|------|
| `dws_user_reg_ltv_d_h` @ 2026-05-27 生产空窗 | 根因：上线日 **reg_incr 未跑**，仅 pay 残留；日批 OVERWRITE + 小时链补全 |
| 注册归因规则梳理 | 输出表、配置表、DWD 上游、打分/赢家逻辑说明 |
| **分 app 归因分析**（生产 04-04~06-02） | 12 个 app 独立漏斗、成功因子、失败原因、改进路线 |
| 生产数据日报（06-03） | 平台 & TOP App & 当日实时 & 06-02 归因快照 |

### 2.3 代码与文档

| 事项 | 结果 |
|------|------|
| Git 同步 | `git pull origin dev`（快进 2 提交，含 `dws_user_tag_d` 重构） |
| Git 提交 | `9961a9b`：`dws_user_ltv_d` 移至 `弃用dws_user_ltv_d/` |
| 文档产出 | 见下文「交付物清单」 |
| 经验沉淀 | `20260603-prod-ltv-backfill-readonly.md`、`20260603-attribution-analyze-by-app.md` |

---

## 三、核心结论（便于汇报）

### 3.1 LTV（生产 2026-05-27 cohort）

- 补数前：`new_users=0`，仅 pay 增量。  
- 补数后：日批 + 17 个小时槽成功，分区数据与 dim UC-01 一致。  
- **待办**：生产 `dws_user_reg_ltv_daily_d` 视图需 **ETL 写账号** 执行 `dws_user_reg_ltv_daily_d_view_ddl.sql`（readonly 无法 DDL）。

### 3.2 注册归因（必须按 app 看）

| 层级 | 全量占比（约） | 说明 |
|------|----------------|------|
| 无候选（不进输出表） | **~80%** | 同 IP 无 24h 内落地页 |
| 有候选未过线 | **~17%** | 多为浏览 60/40 分，注册 `brand/version` 空 |
| 归因成功 | **~3.6%** | JHA-069/063/017/160、DX-002 等形态差异大 |

- **JHA-027**：注册量大，**近 7 日候选内成功率≈0**（60 分卡点）。  
- **DX-002**：门槛 40，成功几乎仅靠 **≤10min 时间分**。  
- 详细分 app 表与改进见专项报告。

### 3.3 生产数据（06-02 账期）

- DAU / 新注册 / 充值环比 **正增长**；落地页浏览 **-32%** 需跟进。  
- **06-03 归因分区暂无数据**，需确认日批任务。

---

## 四、遇到的问题与处理

| 问题 | 处理 |
|------|------|
| dc-platform prod 补数 **403** | 改生产 Dolphin REST + `dolphinscheduler.json` token |
| 生产 SR **readonly** 无法 INSERT/DDL | 补数走海豚；验证用只读 SQL |
| `dolphin_ods` 不存在 | 文档记录等价 API / MCP `dolphin.complement_data` |
| 测试 vs 生产海豚 **project/wf code 不同** | 补数 playbook 写明 prod code |
| 归因分析混算误导 | 约定 + lesson：**按 app 独立分析** |

---

## 五、交付物清单

| 类型 | 路径 |
|------|------|
| 归因专项（分 app） | `.claude/database/reports/attribution_per_app_analysis_20260404_20260602.md` |
| LTV 生产补数记录 | `.claude/database/reports/dws_user_reg_ltv_backfill_20260527_prod.md` |
| LTV 补数 SQL（渲染） | `.claude/database/reports/dws_user_reg_ltv_daily_20260527_prod.sql` |
| **生产数据日报** | `.claude/database/reports/prod_daily_report_20260603.md` |
| **本工作日报** | `.claude/database/reports/work_daily_20260603.md` |
| 经验 | `.claude/memory/lessons/20260603-prod-ltv-backfill-readonly.md` |
| 经验 | `.claude/memory/lessons/20260603-attribution-analyze-by-app.md` |
| 代码提交 | `dev` @ `9961a9b`（弃用 `dws_user_ltv_d` 目录） |

---

## 六、待办 / 明日建议

| 优先级 | 事项 | 负责人建议 |
|--------|------|------------|
| P0 | 确认 **06-03** `dws_register_attribution_result_d` 日批是否失败/未调度 | 海豚 + ETL |
| P0 | 生产执行 LTV **视图 DDL**（`dws_user_reg_ltv_daily_d_view_ddl.sql`） | ETL 写账号 |
| P1 | **JHA-027 / JHA-056** 注册埋点 `device_brand`、`system_version` | 客户端 + 数据 |
| P1 | 落地页浏览环比 **-32%** 归因（推广 vs 埋点） | 运营 + 数据 |
| P1 | 测试/生产 `dws_小时` DAG 改为并行（去 LTV 挡全链） | 调度配置 |
| P2 | 本地 `dev` 分支 **push** `9961a9b`（若尚未推送） | 研发 |
| P2 | 清洗落地页 `channel='{}'` | 埋点 |

---

## 七、工时与协作（可选填）

| 模块 | 预估占比 |
|------|----------|
| 海豚 / LTV 补数与验证 | ~35% |
| 归因分 app 分析与文档 | ~40% |
| 日报 / 巡检 / Git | ~25% |

---

*本日报由当日会话与生产库查询整理；数据口径以各报告正文为准。*
