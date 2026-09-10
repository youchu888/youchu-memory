---
date: 2026-09-10
tags: [pipeline-runner, sandbox, test_sandbox, funnel, agent-bus]
priority: high
domain: ops
---

# pipeline-runner test 四步 + test_sandbox 铁律（禁动 full_chain）

## 背景

bus#8354（狂人→又初）：完整教程。大漏斗升维 metrics/wide 已由狂人代跑 explain + 真跑 09-08；本 lesson 固化入口与隔离规矩。

## 坑 / 错误做法

- 往生产 `full_chain.json` 塞未排槽步 → StepsLoader 漏排检查失败被 daemon catch 吞掉 → **生产链静默停摆**
- 只写 `steps[]` 不排 `slots{}` → 报「步定义了却没排进任何槽位」
- 把 `--dt` 当数据日（unit=day 时 `--dt=D` 实际数据段是 **D-1**）
- 用 SR 手工灌数冒充 runner 验收（见同日 funnel lesson）

## 正确做法

1. **四步**（知秋）：①静态语法 ②`--explain` ③跑验证 ④跑一天；产出一律 `test.*`；unit=day 时④=单步真跑
2. **入口**：`hadoop-1:/home/ec2-user/pipeline-runner/run_test.sh`
3. **隔离（勿改程序）**：test jar、`application_test.conf`（`pipelineName=pipeline_runner_test` 分水位/run_log）、test catalog（`s3a://dc-data-backup/backup/lakehouse_test/`）、资源约生产三成
4. **编排只用** `steps/test_sandbox.json`；**生产 `full_chain.json` 一个字不动**
5. **命令**：
   - `bash run_test.sh probe`
   - `bash run_test.sh run --step=<步> --dt=<任务日> --explain`
   - `bash run_test.sh run --step=<步> --dt=<任务日>`（真跑写 test.*）
6. **挂步三件齐**：`steps[]`（`impl:spark_sql`、`sqlFile` 绝对路径、`params.render.OUT_DB=test.dws`）+ `slots{}` 排槽 + `tagTargets=test.dws.<表>`
7. SQL 用 `${OUT_DB}` 参数化，生产/沙箱共用一份

## 验证

- explain：`rc=0`，日期渲染正确（任务日 vs 数据日）
- 真跑：查 `pipeline_runner_test` 水位/run_log；升维对账按 `(dt,app_id,is_new)` SUM 掉 device_type×source_type 回退对 prod 老值

## 关联

- bus#8354；funnel lesson `2026-09-10-funnel-升维验收须runner-test禁SR手工灌数冒充.md`
- 既有：`2026-09-03-沙箱-explain-必须用-run_test-sh-*`、`2026-09-01-加-spark-任务*禁动full_chain*`
