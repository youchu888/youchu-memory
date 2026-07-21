# Lessons 索引

| 日期 | 标题 | tags | 一句话 |
|------|------|------|--------|
| 2026-06-24 | [ETL 统一 ops_system 分层目录](./2026-06-24-ops-system-etl-directory-layout.md) | ops_system, etl, dev-session, chcode | 禁仓库根 dwd_/dws_ session；SQL+文档同目录进 ops_system 对应层 |
| 2026-06-18 | [work-log 跨 Agent 共享](feedback_work_log_multi_agent_reports.md) | work-log, agent, daily-report | 本地 work-log/ 日流水；子 Agent 收尾必 append；不进 Git |
| 2026-06-18 | [ETL SQL 文件头三行声明](./2026-06-18-sql-etl-header-three-lines.md) | sql, lint, dolphin, etl | 前 30 行须 task/doc/params + 同目录 task.yaml；注释禁占位符 |
| 2026-06-17 | [StarRocks ALTER DEFAULT + PK MODIFY](./2026-06-17-starrocks-alter-default-and-pk-modify.md) | starrocks, ddl, primary-key | ADD DEFAULT 0 报错；主键表 key 列禁止 MODIFY |
| 2026-06-17 | [dc-platform 项目化记忆统一](./2026-06-17-dc-platform-projectization.md) | dc-platform, memory, archive | 公共记忆迁 ~/.dc-platform/memory/；task.yaml project=dc-platform |
| 2026-06-13 | [海豚发布 schedule 仍 OFFLINE](./2026-06-13-dolphin-publish-schedule-offline.md) | dolphin, schedule, dependent, video, test | wf PUT 后须 online_schedule；globalParams 与 repo SQL 须与线上一致 |
| 2026-06-10 | [核查规则沉淀剧本](./20260610-datacheck-playbook-as-asset.md) | datacheck, playbook, attribution, process | 核查认可后必更新 playbooks/；lesson 记坑、剧本记可执行 SQL |
| 2026-06-09 | [attribution_flag 列错位](./20260609-attribution-flag-column-order.md) | attribution, dwd, dolphin, test, schema | ALTER 追加列后须 INSERT 显式列名；小时任务缺字段会把 etl_time 写进 attribution_flag |
| 2026-06-05 | [归因 test 发布补数零行核验](./20260605-attribution-test-deploy-backfill.md) | attribution, dolphin, test, complement, dim | dim 须大写 app_id；补数 SUCCESS+0 行先查注册与落地页 IP 交集 |
| 2026-06-03 | [归因分析按 app 独立](./20260603-attribution-analyze-by-app.md) | attribution, datacheck, prod, per-app | 注册归因必须分 app 看漏斗与匹配因子；混算掩盖无候选/阈值差异 |
| 2026-06-03 | [生产 LTV 补数 readonly 限制](./20260603-prod-ltv-backfill-readonly.md) | prod, ltv, dolphin, complement, readonly | 生产 SR readonly + 无 prod 海豚写权限 → 必须海豚 UI/ETL 账号补数，不能直接 INSERT |
| 2026-05-29 | [dad-dau 分层根因与逐层核查](./2026-05-29-dad-dau-layered-root-cause.md) | datacheck, ads, dwd, dw, device_id, dad, dau | TJ-001 DAD 900w 根因在客户端 device_id 高 churn + ADS 口径含匿名 device；datacheck 必须逐层追到 dw |
