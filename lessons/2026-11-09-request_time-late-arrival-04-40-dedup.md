---
date: 2026-11-09
tags: [request_time, settlement, dedup, datacheck, register, order]
severity: high
domain: caliber
source: worker_ant_group
---

# request_time 分区 · 晚到漏算 · 04:40 丢数核对 · 订单/注册去重差异

（正文与项目 `.claude/memory/lessons/2026-11-09-request_time-late-arrival-04-40-dedup.md` 同步）

## 可复用要点

- 分天/分小时按 request_time；入湖晚不挪日。
- 末格 00:00 封账 + 订单不跨天回看 → 单次晚到首遍漏。
- 04:40 丢数核对 → 重跑原日格。
- 订单全局先去重；注册同日事件去重 + 首次到达日新增。
- 第一份不能丢。
