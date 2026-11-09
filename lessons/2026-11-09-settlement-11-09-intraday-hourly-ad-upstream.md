---
date: 2026-11-09
tags: [settlement, hourly, datacheck, ad, upstream, worker_ant_group]
severity: medium
domain: datacheck
source: worker_ant_group
---

# 2026-11-09 结算当日进度：小时追平、凌晨注册次日整日补算、广告表上游未写

## 背景
继 11-08 整日重跑验收放行后，业务日 11-09 结算小时链按小时推进；狂人通报进度正常，并说明两处已知缺口。

## 可复用规则
- 小时进度：北京午后约 14:40，当日小时数据通常已落到上一整点小时（如 13:00~14:00），属正常，非断流。
- 凌晨注册：01、02 点注册可能当日小时内未全计入；待业务日跑完后次日对当日做**整天重算**补漏（本例约 2.7 万人）；日内对账勿据此判失败。
- 广告相关表：上游写入未恢复时表会暂时无数据，先确认上游恢复，勿当 ETL 单点故障改链路。

## 关联
- [11-08 结算重跑验收](./2026-11-09-11-08-settlement-rerun-acceptance.md)
- `docs/sop_settlement_stall_backfill.md`
