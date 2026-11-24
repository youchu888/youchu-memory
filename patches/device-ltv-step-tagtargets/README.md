# 设备 LTV · step.json 小尾巴（待旧机/持有会话环境落地）

## 要改

会话 `dev-20261117-001` 的 `step.json` 计算步 `ads_app_device_ltv_d_d`：

1. `tagTargets` 现仅声明明细表，须**补上** pay_gap（SQL 同作业双写）：
   - `paimon.ads.ads_app_device_ltv_d_d`
   - `paimon.ads.ads_app_device_ltv_pay_gap_d`
2. **确认有意**：`pay_gap` 编排无人读、不回写 SR（test SR 仅有明细表；与挂步回执一致）。回写步保持只 pb 明细表即可。

## 为何本机未改

- 公司仓无 `ads_app_device_ltv*` 路径；`git fetch` 经代理失败。
- 平台 `session_get(dev-20261117-001)` 对本 MCP 账号 403。
- 需旧机或会话持有人环境改完 push。

## 首跑核验

见仓内报告 `/.claude/database/reports/ads.ads_app_device_ltv_d_d/validate__2026-11-23__first_daily_run.md`（2026-11-24）。
