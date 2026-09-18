# P2 方案 B · deduction_d 归因渠道 · test 验收

- **dt**: 2026-06-28（手动触发 scheduleTime=2026-06-29 00:15:00）
- **主线**: bus#652 · P2
- **时间**: 2026-07-01

## 发布物（test）

| 项 | 值 |
|---|---|
| SQL | `ops_system/04.dws/dws_app_channel_deduction_d/dws_app_channel_deduction_d.sql`（拆两半 UNION） |
| wf | `wf_渠道分析_日` **21869769870720** v13→**v15** |
| task | `dws_app_channel_deduction_d` SQL 已替换 |
| DEPENDENT | `等_归因落地页快路_日_结算` **22204845161856** → 快路 wf |
| cron | 目标 `0 15 0 * * ? *` — **API 改 schedule 报 10077，仍为 00:05（待 UI/二次修）** |

## 手动触发

- instance **#55551** · **SUCCESS**（dep → deduction → summary → ads）

## 对数（test · dt=2026-06-28）

| 指标 | 改前基线 | P2 跑后 |
|---|---|---|
| 行数 | 895 | 895 |
| SUM(new_user) | 8756 | **8756** ✅ 守恒 |
| SUM(download_num) | 24300 | **24300** ✅ 守恒 |
| SUM(recharge_amount) | 1,453,000 | **1,453,000** ✅ 守恒 |

> test `settlement_detail` 当日仅 **1** 条注册事件 `channel≠dim.channel`，渠道搬移不明显；逻辑已上线，prod 灌样/灰度 app 后再做 organic→真实渠道形态验收。

## 待办

- [ ] 修 `wf_渠道分析_日` schedule cron → 00:15
- [ ] `wf_结算充值_日_首跑` 同样后移 + DEPENDENT（P2b）
- [ ] 灰度 app `is_rewrite_channel=1` 后逐渠道对数
