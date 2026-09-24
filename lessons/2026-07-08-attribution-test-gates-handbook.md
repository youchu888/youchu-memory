---
date: 2026-07-08
tags: [attribution, test, gate, handbook, result_d]
severity: high
domain: datacheck
---

# 归因出数硬条件与测试验收手册

## 背景

主人问「归因测试要符合什么规则才会产生数据」，需把入围口径整理成可照着测的清单，并输出 HTML 给测试。

## 坑 / 错误做法

- 以为任意 iOS 注册都会进 `result_d` → 实际还要白名单 + organic 系渠道 + `attribution_flag=1` + **有落地页 IP 候选**
- 只看日批 SUCCESS 就算有数 → metrics 可成功仍 0 行（块注释坑）
- 影子期期望 `rewrite_*` 有数 → `is_rewrite_channel=0` 时写回指标为 0 是预期

## 正确做法

### 进 `dws_register_attribution_result_d`

同时满足：

1. `dim_app_attribution_config.is_run = 1`
2. 设备 `ios`（大小写不敏感）
3. 渠道 organic / natural / self / 空
4. `attribution_flag = 1`（客户端 payload）
5. `uid IS NOT NULL`
6. 同 app + 注册 IP = click/view IP；来源时间在注册前且 ≤86400s；来源 channel 非空且非 organic

### 归因成功

- 打分 ≥ `min_threshold`（常见默认 40）
- 择优：先 click，不够再 view；同分取最近

### 回写 / 看板

- 写回 dim：`is_rewrite_channel=1` 且用户渠道仍 organic/空
- metrics / 看板：依赖 `result_d`，只汇总白名单 app

## 验证

- 测试手册：`~/Downloads/归因测试验收手册_2026-07-08.html`（硬条件 + 12 用例 + 验收 SQL + 空数排查）
- 口径旁注：`ops_system/04.dws/dws.dws_register_attribution_result_d/归因对接说明.md`

## 关联

- lesson 块注释 0 行：`2026-06-29-dolphin-sql-block-comment-zero-rows.md`
- 当日 metrics 断流排查：同根因高概率，test 灌样有数、prod 待发版
