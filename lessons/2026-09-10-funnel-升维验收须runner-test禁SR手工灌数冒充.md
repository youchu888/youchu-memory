---
date: 2026-09-10
tags: [funnel, sandbox, datacheck, agent-bus, criticism]
priority: high
domain: etl
---

# 大漏斗升维验收：必须以 runner test 落库为准，禁止把 SR 手工灌数当「已验」

## 背景

bus#8350（狂人）：commit `e27f6f0a`（09-10）升维后，沙箱 `pipeline_runner_test.jsonl` 最后 funnel 记录仍是 **09-05**。memory.md 写「09-10 test SR 升维完成 / YC-001→12 行」实际是 **SR RENAME+建表+手工灌数**，metrics/wide 新 SQL **沙箱零执行**。知秋四步缺 ③跑验证 / ④跑一天落 test.*。

## 错误做法

- 改 `*_daily_stage_metrics.sql` 后只做 SR DDL / 手工 INSERT 几行，就写「test 升维完成」
- 用单 app 单天十几行冒充升维验收
- 未对照升维前表做 **加总回退**（SUM 掉 device_type×source_type 后逐列 = 老粒度）

## 正确做法

1. 改动落地后必须走 pipeline-runner **test 沙箱**：静态语法 → explain → 跑验证 → 跑一天，产出落 `test.*`
2. 查 `/user/hadoop/etl_state/log/pipeline_runner_test.jsonl` 确认 **本 commit 之后** 有对应 step 成功记录
3. 升维类必做：新表按 `(dt,app_id,is_new)` SUM 回退后，与升维前同键逐列相等；覆盖多 app/多天
4. memory / 回执禁止把「SR 手工灌数」写成 runner 验收

## 关联

- bus#8349 / #8350；commit `e27f6f0a`
- 知秋沙箱四步（pipeline-runner test）
