---
date: 2026-10-28
tags: [prod-publish, stage7, hard-gate, dolphin, spark]
severity: high
domain: ops
---

# 完成发布硬闸：不达标一律 409，禁止空 PublishRun / 假完成

## 背景

仅拦「未建表」不够：Step2 可空勾、Step3/4 可不核、task 未同步、wf OFFLINE、schedule 全下线、缺参、0 条 PublishRun 仍可能点「完成发布」→ 产上定时失败或 SQL 炸。

## 正确做法（双保险）

**服务端** `POST /prod-publish/{code}/complete` → `_assert_prod_complete_hard_gates`：

| # | 条件 | 不达标 |
|---|------|--------|
| 1 | stage 1–6 均为 `done` | 409 |
| 2 | SR 产出表（ads/dws/…）在 prod information_schema 存在 | 409 |
| 3 | dolphin：`body.tasks` 非空且有 wf/task code | 409 |
| 4 | dolphin：test `owned` 任务名全部覆盖 | 409 |
| 5 | dolphin：prod wf `ONLINE`、task 存在、`flag≠NO` | 409 |
| 6 | dolphin：若有 schedule 则至少一条 ONLINE（无 schedule=DEPENDENT 子流不拦） | 409 |
| 7 | spark：必须传 `spark_steps`，且步在 prod 编排 | 409 |
| 8 | 写出 PublishRun 条数 > 0 才允许归档 | 409 |

**插件向导**：

- Step2 完成：每 task 已有 prod 三码 + 无缺参 + 无 warning
- Step3/4 完成：必须勾「已核」
- Step6 / spark⑤：客户端再跑一轮缺表与前置 step，再调 complete

## 验证

故意缺表 / 不同步 / OFFLINE → complete 返回 409，且无新 PublishRun、不归档。

## 关联

- `api_v1_prod_publish.py` · `prod-publish-wizard.ts` · `stage7-spark-panel.ts`
- 前序：`2026-10-28-prod-publish-step1-must-verify-table-exists.md`
