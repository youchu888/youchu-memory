---
date: 2026-05-29
tags: [datacheck, ads, dwd, dw, device_id, dad, dau, app_page_view]
severity: high
domain: datacheck
---

# TJ-001 DAD 900w vs DAU 6k：分层根因与逐层核查法

## 背景

`ads.ads_app_metrics_daily_d` 上 TJ-001 出现 DAU≈6k、DAD≈900w。用户质疑 DAU:DAD 比例；要求沿上下游逐层核查到原始层。

## 坑 / 错误做法

1. **只看 ADS 汇总表** → 误以为计算 bug，实际是口径 + 上游埋点。
2. **用 `dws.dws_app_user_d_h.active_devices` 对比 ADS DAD** → 两套口径不同（DWS 排除匿名 uid），会得出「ADS 算错」的错误结论。
3. **DAU 过滤写 `uid IS NOT NULL`** → 拦不住 `uid=''` 空串（SQL 中 `'' IS NOT NULL` 为真）；匿名 uid 在 DAU 侧被 GROUP BY 压成 1 桶，掩盖了 filter 缺陷。
4. **DAD 过滤只写 `device_id IS NOT NULL`** → 935 万匿名 ephemeral device_id 全部计入。
5. **跳过 DW 层** → 无法区分「ETL 写坏」vs「源数据就这样」。

## 分层结论（TJ-001 / 2026-05-27 生产验证）

| 层级 | 对象 | 是否正确 | 问题点 |
|------|------|----------|--------|
| L0 客户端 | uid / device_id 上报 | **主因** | 匿名流量 uid=`''`；device_id 32 位 hex **高 churn**（52% device 仅 1 PV）；集中在 archives/search |
| L1 ODS/Flink | `ods_app_page_view` | 透传 | `COALESCE(uid,'')` 把 NULL 变空串；无 device 质量校验 |
| L2 DW | `dw.dw_user_event_detail` | 原始层如实 | anon: 6167 万 PV / 935 万 device_id / **74 万 fingerprint** |
| L3 DWD | `dwd.dwd_app_page_view_d` | 过滤 page_key 但**不校验身份** | anon: 6043 万 PV / 935 万 device（与 DW device 数一致） |
| L4 ADS | `ads_app_metrics_daily_d` | **次因：口径设计** | DAU 分支 `uid IS NOT NULL`；DAD 分支 `device_id IS NOT NULL` → 含全部匿名 device |
| L4 DWS | `dws_app_user_d_h` | **相对正确** | `TRIM(uid)<>''` + active_devices 仅已登录 ACTIVE |

**根因排序**：① 客户端匿名场景 device_id 不稳定（+ 大量 SEO/H5 流量）→ ② ADS ETL DAD 口径未排除匿名/未用稳定 device 键 → ③ DAU/DAD 过滤条件不对称且未用 `TRIM(uid)<>''`。

## 正确做法

### 逐层核查顺序（任何指标异常必做）

```
ADS/DWS 汇总 → DWD 明细 → DW 原始事件 → ODS/Flink 逻辑 → 客户端埋点规范
```

每层对比：**PV、distinct uid、distinct device_id、distinct device_fingerprint**；anon vs logged_in 分段。

### 关键 SQL（TJ-001  anon 段 DW vs DWD device 数应一致）

```sql
-- DW
SELECT COUNT(*) pv, COUNT(DISTINCT device_id) did,
       COUNT(DISTINCT device_fingerprint) fp
FROM dw.dw_user_event_detail
WHERE event='app_page_view' AND app_id='TJ-001'
  AND event_time BETWEEN '@{dt} 00:00:00' AND '@{dt} 23:59:59'
  AND (uid IS NULL OR TRIM(uid)='');

-- DWD（device 数应与 DW 接近；PV 因 page_key 过滤略少）
SELECT COUNT(*) pv, COUNT(DISTINCT device_id) did
FROM dwd.dwd_app_page_view_d
WHERE dt='@{dt}' AND app_id='TJ-001'
  AND (uid IS NULL OR TRIM(uid)='');
```

### 修复建议

| 层 | 修改 |
|----|------|
| **客户端** | 匿名也持久化 device_id（localStorage/cookie）；禁止每 PV 生成新 UUID |
| **ODS/DW** | 可选：空 uid 存 NULL 而非 `''`；增加 `is_anonymous` 标识 |
| **DWD** | 可选：产出 `uid_valid = TRIM(uid)<>''` 供下游统一使用 |
| **ADS `ads_app_metrics_daily_d.sql`** | DAD 与业务对齐：`TRIM(uid)<>''` 和/或 `COALESCE(device_fingerprint, device_id)`；或拆 `dad_logged_in` / `dad_anon` |
| **ADS DAU** | `uid IS NOT NULL AND TRIM(uid)<>''`（与 DWS 一致） |
| **指标消费** | 业务「设备日活」若指真实用户设备 → 用登录 device（~5738）或 `device_fingerprint`（~74万），不用 raw `dad_ids` |

绑定程序：
- `ops_system/05.ads/job_ads_app_metrics_daily_d/ads_app_metrics_daily_d.sql`（L27-38 did/uid attribution）
- `ops_system/02.dwd/job_dwd_page_type_d/dwd_app_page_view_d/dwd_app_page_view_d_daily.sql`
- `operating-system/ods/dml/dml-ods_app_page_view-应用页面展示事件表.sql`（L97 COALESCE uid）
- `ops_system/04.dws/dws_app_user_active/dws_app_user_d_h/dws_app_user_d_h_hourly.sql`（L64 TRIM uid；L139 active_devices）

## 验证

- DW anon `COUNT(DISTINCT device_id)` = DWD anon 同值 → ETL 未写坏，问题在源或 ADS 口径。
- `BITMAP_COUNT(dad_ids)` = DWD `COUNT(DISTINCT device_id)` → ADS DAD 忠实反映 DWD（非 ADS 计算 bug）。
- 登录段：DAU 6144 vs device 5738 → 比例 ~1.07，正常。
- fingerprint 74 万 << device_id 935 万 → 支持「device_id 不稳定」假设。

## 关联

- 诊断 SQL：`.claude/database/reports/diag_tj001_dau_dad_anomaly.sql`
- Playbook：`.claude/database/playbooks/ads.ads_app_metrics_daily_d.md`
- 逐层核查剧本：`.claude/database/playbooks/datacheck_layered_verification.md`
