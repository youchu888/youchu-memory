# bus#652 · 归因方案 A+B · test 落地结案报告

- **DATE**: 2026-07-01
- **ENV**: test only · **prod 未动**（知秋发版令前 HOLD）

## 交付摘要

| 阶段 | 交付物 | 状态 |
|---|---|---|
| **P0 方案 A** | `wf_dws_汇总_日` v74→v75 归因链提前；`rewrite_status` 修复 | ✅ |
| **P0 验数** | prod 灌样 dt=2026-06-28 → **567/567** 金标一致 | ✅ |
| **P1 快路** | `wf_归因落地页快路_日` 22204696592512 · cron 00:10；汇总日 v76 DEPENDENT | ✅ |
| **P2 方案 B** | `deduction_d` 拆两半 SQL · 渠道分析 v15 DEPENDENT · cron **00:15** | ✅ |
| **P2b 结算** | 结算首跑 v10 `等_渠道分析_日_结算` · cron **00:18** | ✅ |
| **P3 冒烟** | 结算首跑 #55561 SUCCESS；deduction 总量守恒 | ✅ |

## 脚本

- `dc-platform-server/scripts/reorder_wf_attribution_first.py`
- `dc-platform-server/scripts/create_wf_attribution_fast_path.py`
- `dc-platform-server/scripts/patch_wf_settlement_p2_tail.py`
- `.claude/database/scripts/attribution_runbook.py`（`copy-sample-to-test`）

## test 海豚关键版本

| wf | code | ver | cron |
|---|---|---|---|
| wf_dws_汇总_日 | 21869820140416 | 76 | 05:20 |
| wf_归因落地页快路_日 | 22204696592512 | 1 | 00:10 |
| wf_渠道分析_日 | 21869769870720 | 15 | **00:15** (sched#125) |
| wf_结算充值_日_首跑 | 21869770152192 | 10 | **00:18** (sched#126) |

## 0 点后时序（目标）

```
~00:08  dim_user_all + _new 齐
~00:10  快路 click→view→归因→回写
~00:15  渠道分析 deduction_d(归因渠道)→summary→ads
~00:18  结算充值 charge_d/h
~05:20  汇总日（DEPENDENT 等快路后再跑归因链）
```

## 已知限制 / 后续

1. **小时扣量** `wf_广告渠道扣量_小时` 仍原始渠道（日终归因双口径，待业务确认）
2. **B 类旁路** channel_dau/retention/landing 未改（知秋 07-01 暂不动）
3. **灰度 app** `is_rewrite_channel=1` + 逐渠道 organic→真实渠道对数 — prod 前必做
4. test `result_d` 分区曾被 sync 清空；P0 金标 **567/567** 已验，日常靠快路/汇总补跑

## prod 上线条件

- 知秋发版令
- 狂人/主人 prod 发布审批
- 灰度对数通过
