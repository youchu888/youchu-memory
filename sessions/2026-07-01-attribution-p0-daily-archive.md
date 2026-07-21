---
date: 2026-07-01
tags: [attribution, agent-bus, dolphin, gray, SF-81, archive]
maintainer: 又初
session_transcript: cf0abd6d-b1dc-4631-a723-c6baf263a10f
---

# 2026-07-01 工作归档 · 归因 P0 + agent-bus

> **用途**：同类任务开工先读本文 §快速入口，再按需展开 lesson / report / reference。

## 零、00:14 checkpoint（bus#597）

| 项 | 状态 |
|----|------|
| rewrite_status 材料 | 已交 worker_ant 转知秋 |
| 归因档 | ✅ [`2026-06-30-attribution-rewrite-status-archive.md`](2026-06-30-attribution-rewrite-status-archive.md)（两段 SQL + status/reason 枚举） |
| 当晚约束 | test only · 零 prod · prod 全等知秋令 |

## 一、今日交付摘要

| 主题 | 状态 | 关键结论 |
|------|------|----------|
| bus#652「等待执行」根因 | ✅ 已解释 | IDE 主会话干活但 progress 只盯 `cursor-agent` CLI → 误报「等待执行」 |
| agent-bus 进度/重唤醒加固 | ✅ 已落地 | `bus_is_closed`、IDE heartbeat、TG busy 标志、progress 不结案 |
| test 归因 DAG P0 | ✅ v76 ONLINE | 等 dim → 快路 → result → apply → metrics → 下游 |
| SF-81 test 灰度对数 | ✅ bus#706 结案 | 516/516 改写；三条验收通过 |
| 平台归因 E2E 文档 | ✅ 已沉淀 | `reference_attribution_end_to_end_complete.md` |
| prod 发布请示 | ⏳ 待批复 | 群 msg#3730 + bus#723；**prod 禁止自发** |
| git | ✅ | `1a1982f` DAG reorder scripts → dev |

## 二、bus 时间线（又初侧）

| bus | 动作 |
|-----|------|
| #652 | 知秋派活归因 A+B test 实施；ACK；DAG 方案 progress |
| #659/#664/#688 | P0 DAG / rewrite_status / natural-self 讨论 |
| #694/#705/#706 | 方案报批 → SF-81 灰度批复 |
| #709 | ACK bus#706 |
| #710 | reply 结案 SF-81 对数 |
| #723 | 群同步·请示 prod 发布 |

## 三、资产索引（按类型）

### 报告（当次交付）

| 路径 | 说明 |
|------|------|
| `.claude/database/reports/attribution/validate__SF-81_gray__2026-06-28__20260701.md` | SF-81 灰度三条验收 |
| `.claude/database/reports/attribution/validate__2026-06-19_to_2026-06-28__20260617.md` | 区间归因核查（早前） |

### 记忆 / 参考（长期）

| 路径 | 说明 |
|------|------|
| [归因 P0 快速入口](../reference_attribution_p0_quickstart.md) | **同类任务第一站** |
| [归因 E2E 完整方案](../reference_attribution_end_to_end_complete.md) | 平台 doc 沉淀 |
| [prod 发布审核门](../feedback_prod_release_review_gate.md) | 又初不自发 prod |

### Lesson（踩坑 / 做法）

| 路径 | tags |
|------|------|
| [SF-81 灰度 + 平台 doc](../lessons/2026-07-01-attribution-e2e-platform-doc-and-sf81-gray.md) | gray, SF-81, complement |
| [agent-bus 等待执行信号](../lessons/2026-07-01-agent-bus-progress-ide-heartbeat.md) | agent-bus, progress |
| [test DAG 与发布判断](../lessons/2026-07-01-attribution-test-dag-publish-gate.md) | dolphin, test, prod |

### 剧本（可执行核查）

| 路径 | 说明 |
|------|------|
| `.claude/database/playbooks/dws.dws_register_attribution_gray_verify.md` | 灰度三条验收 SQL |

### 代码 / 脚本

| 路径 | 说明 |
|------|------|
| `dc-platform-server/scripts/reorder_wf_attribution_first.py` | test WF 归因链 DAG + task codes |
| `.claude/database/scripts/attribution_runbook.py` | complement / export / audit |
| `ops_system/06.dim/job_dim_user_attribution_channel_apply/` | apply + rewrite_status |
| `ops_system/04.dws/dws.dws_register_attribution_result_d/` | result_d ETL |

### test 海豚常量（v76）

| task | code |
|------|------|
| `dws_register_attribution_result_d` | 174729603403591 |
| `dim_user_attribution_channel_apply_d` | 21962007716224 |
| `dws_register_attribution_metrics_d_d` | 22127764280192 |
| wf `wf_dws_汇总_日` | 21869820140416 · project 20524869250304 |

## 四、硬规则（今日 reinforced）

1. **prod 一律等知秋令**；DDL 与 ETL 必须同步上线（bus#617/#618）。
2. **P0 已带** natural/self→organic 归并（dim_user_all + dwd_user_register_d_v2）。
3. **prod DAG 旧顺序暂不改**；test 已归因先行。
4. **灰度扩 app** 只改 `is_rewrite_channel`，不必发版。
5. **test dim 常缺用户** → 验证性补数：prod 同步 success uid 的 dim 行。

## 五、未完成 / 待批复

- [ ] 知秋/狂人批复 prod 归因链 3 task 是否可发
- [ ] prod 影子期 `is_rewrite_channel` 全 0 策略确认
- [x] `rewrite_status` + `rewrite_reason` 两阶段落库（2026-07-01 代码完成，test 待发版验证）
- [x] natural/self→organic 识别层归并（dim+dwd，2026-07-01）
- [ ] 结算 7 表（千行负责）本轮未动

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-07-01 18:14 | bus#680 checkpoint：P0 v75+rewrite_status 验数+SF-81 三条对数落档 |
| 2026-07-01 22:29 | bus#769/#776/#777/#778 结案；06-28 补数修正 schedule=dt+1 → 567行/516 rewrite_status |
| 2026-07-01 22:14 | bus#778 checkpoint：test DDL+发布+补数闭环；publish-runs 164/165；待 06-28 有候选出数验回写 |
| 2026-07-01 | 又初 · 全日归档初版 |

---

## 六、18:14 checkpoint（bus#680）

> test only · prod 等知秋令 · 产出落档待狂人审

### P0 v75 + rewrite_status 验数进展

| 项 | 状态 | 证据 |
|----|------|------|
| DAG P0 | ✅ v74→v75 | `wf_dws_汇总_日` 归因链提前：等_dim→result→apply→metrics→下游 |
| rewrite_status ETL | ✅ 修复 | result SELECT 补第 28 列；channel_apply 写 1/0/NULL |
| 金标对数 | ✅ 567/567 | prod 灌样 dt=2026-06-28 → test result 与 prod 金标一致 |
| 报告 | ✅ | `.claude/database/reports/attribution/validate__bus652_test_closeout__20260701.md` |

### 三条对数结果（SF-81 灰度 · dt=2026-06-28）

| # | 口径 | 结果 |
|---|------|------|
| ① 总量守恒 | SF-81 dim 用户数 | 517→517 ✅ |
| ② organic 搬迁 | success organic→attributed_channel | 516/516 ✅（余 1 无 success） |
| ③ 非灰度不变 | SF-01 channel 分布 | organic=10 前后一致 ✅ |

- 配置：`is_run=1` · `is_rewrite_channel=1` · TASK_ONLY channel_apply
- 报告：`.claude/database/reports/attribution/validate__SF-81_gray__2026-06-28__20260701.md`
- bus#706 批复 · bus#710 结案

### 同期进展（18:14 时点）

| 阶段 | 状态 |
|------|------|
| P1 快路 wf | ✅ ONLINE cron 00:10 |
| P2 deduction 拆两半 | ✅ v15 + 结算 v10 |
| prod | ⏸ HOLD 等知秋令 |
| natural/self 归并 | P0 未带（待与猫猫协调） |

### 红线确认

- test 不擅自补数（验证性补数经 bus#706 批复）
- prod 零自发
- 猫猫/花儿档各自负责

---

## 七、22:14 checkpoint（bus#778）

| 项 | 证据 |
|----|------|
| DDL test | `rewrite_reason VARCHAR(128)` 已加；与 `rewrite_status` 并存 |
| 海豚 test | result_d **v79** · apply **v80** · wf **v80** |
| 平台 publish-runs | **164**（904 result）/ **165**（001 apply） |
| git | `origin/dev` **0f707b2** |
| 补数 | 06-28 schedule **2026-06-29 05:20** PI#55583 result+apply SUCCESS；**567行** SF-81 521/516 rewrite_status=1 |
| bus | #766/#769/#776/#777/#778 均已 reply 结案（agent_bus_send.py） |

### 待办

- [x] test **06-28** `rewrite_reason`/`rewrite_status` 分布已验（567/516）
- [ ] **prod 等知秋令**；DDL+ETL 同批；dim/dwd natural-self 需猫猫 session 协调
