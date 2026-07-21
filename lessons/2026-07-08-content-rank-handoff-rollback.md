---
date: 2026-07-08
tags: [content-ranking, division, worker_ant, feedback]
severity: medium
domain: ops
---

# 内容排行猫猫主责线：又初改过的部分按令撤回

## 背景

07-08 猫猫短时挂掉曾换又初做内容排行骨架；随后猫猫回岗，狂人明确代管/复核撤回。主人转达：猫猫负责的内容，我们修改的部分要撤回。

## 坑 / 错误做法

- 代管撤回后仍继续扩改内容排行并当已完成写进日报
- 与猫猫并行改同一专项不先问分工边界

## 正确做法

1. 狂人撤回代管 → 立即停手，未发布则不挂海豚
2. 仓库里又初新增的内容排行改动：按令 revert / 交给猫猫接管，勿双写
3. 日报状态用「待确认/已撤回」，不写「已完成」冒领

## 验证

群/bus 分工以最新撤回令为准；本地 diff 不与猫猫主责冲突。

## 关联

- 路径：`ops_system/04.dws/dws.dws_content_metric_d_d/`、`ops_system/05.ads/job_ads_content_rank/`
