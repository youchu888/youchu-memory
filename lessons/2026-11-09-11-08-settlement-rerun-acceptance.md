---
date: 2026-11-09
tags: [settlement, datacheck, sr, lake, 结算详情]
severity: medium
domain: datacheck
source: worker_ant_group
---

# 2026-11-08 结算整链重跑验收口径（狂人通报）

## 背景
业务日 11-08 结算全天重跑（含结算详情依赖的推广汇总天表、充值天表），回写 SR 后狂人完成最终核对并放行。

## 可复用判据
- 重跑收口前：注册、订单丢数核对为 0（重跑过程通报）。
- 放行门槛：SR 与湖上 **744 项逐字段 0 差异**。
- 金额三边：汇总天表、小时表、订单侧总金额一致（本日示例 **640,726,184**）。

## 关联
- `docs/sop_settlement_stall_backfill.md`（补数/重跑流程）
- `db/dws/结算详情.sql`（接口读表）
