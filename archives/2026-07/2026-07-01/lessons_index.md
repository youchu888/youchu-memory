# Lessons 索引

| 日期 | 标题 | tags | 一句话 |
|------|------|------|--------|
| 2026-07-01 | [agent-bus「等待执行」误报](../lessons/2026-07-01-agent-bus-progress-ide-heartbeat.md) | agent-bus, progress, cursor | IDE 主会话干活但 progress 只盯 CLI；reply:bus 键结案 |
| 2026-07-01 | [归因 test DAG 与发布判断](../lessons/2026-07-01-attribution-test-dag-publish-gate.md) | attribution, dolphin, prod, publish | test 线上=repo 则无需再发；prod 群请示知秋 |
| 2026-07-01 | [归因 E2E 文档 + SF-81 灰度对数](./2026-07-01-attribution-e2e-platform-doc-and-sf81-gray.md) | attribution, gray, SF-81, test, platform-doc | 平台 doc 沉淀；test dim 同步后 TASK_ONLY apply 516/516 通过 |
| 2026-06-29 | [海豚 SQL 块注释 INSERT 0 行](./2026-06-29-dolphin-sql-block-comment-zero-rows.md) | dolphin, sql, attribution, prod | INSERT 前禁 `/* */` 块注释；用 `--`；SUCCESS 仍须查行数 |
| 2026-06-27 | [依工作狂人持续进化](./20260627-youchu-evolve-from-worker-ant.md) | worker_ant, self-evolve | 派单收尾提炼；纠正入库；禁止重复ack |
| 2026-06-27 | [agent-bus offset 四步修法](./20260627-agent-bus-offset-persistence.md) | agent-bus, poller, feedback | after_id 落盘/逐条推进/首轮跳 backlog/去重 |
| 2026-06-27 | [记忆体系与自我进化](./20260627-worker-ant-memory-architecture.md) | memory, feedback, worker_ant | 三级分层/触发词/Why+How/去重铁律 |
| 2026-06-27 | [工作狂人全量协作核心包](./20260627-worker-ant-full-collab-core.md) | worker_ant, etl, migration, dolphin | bus#77 七章；dynamic_overwrite/cat/海豚API/踩坑 |
| 2026-06-26 | [工作狂人协作速查 v1](./20260626-worker-ant-collab-cheatsheet.md) | worker_ant, starrocks, datacheck, prod | 速查简版；agent-bus bus#72 |
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
