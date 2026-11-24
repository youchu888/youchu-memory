# 设备 LTV · step.json tagTargets（已落地）

- 远端：`3494717f`（蓝猫）已把计算步 `tagTargets` 写成：
  - `paimon.ads.ads_app_device_ltv_d_d`
  - `paimon.ads.ads_app_device_ltv_pay_gap_d`
- pay_gap 仍不回写 SR（仅 pb 明细表）——有意。
- 2026-11-24 VPN 恢复后：`git fetch` 成功，本机已检出 `data-jobs/spark/05.ads/ads_app_device_ltv_d_d/`。
- 首跑核验：`.claude/database/reports/ads.ads_app_device_ltv_d_d/validate__2026-11-23__first_daily_run.md`
