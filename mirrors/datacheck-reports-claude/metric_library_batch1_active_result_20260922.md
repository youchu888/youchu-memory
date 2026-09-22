# 指标库 · 第一批活跃域填数结果 · 2026-09-22

> test metadata · 已 apply · 脚本 `docs/metric_library_batch1_active_fill_20260922.py`

## 范围

| 表 | 动作 |
|----|------|
| `dws.dws_app_user_d_h` / `m_d_new` / `w_d_new` | 挂到已有日/周/月 concept；primary 从空旧表切到现网有数表 |
| `ads.ads_app_metrics_daily_d` / `hourly_d` | 活跃列补挂；`dad_*` 新建 published |
| `dws.dws_session_duration_user_d` / `device_d` | 新建原子 + derived(avg) |
| `dws.dws_source_analysis_active_d` | 新建 `active_user_30d_by_source` / `source_analysis_new_users` |

非活跃列（充值/视频等）只进 `metric_impl_candidate` pending，留给后续批次。

## 结果

| 项 | 数 |
|----|----|
| concept published（库内合计） | **322**（原 301，+21） |
| orphaned | 11（未动） |
| 本批新增/补挂 implementation | 45 条新 + 14 条已存在确认 |
| primary 切换 | 15 |
| candidate 扫入（本批 lineage） | 108（含后续批次 pending） |

## 验收点

- `active_users` / `active_devices` 等 primary 已在 `dws_app_user_d_h`（日）与 `*_d_new`（周/月）
- 时长 avg 为 derived，分子分母 FK 已挂
- 未碰 `metric_standard` / 未灌 prod

## 下一批建议

注册/留存（`dws_app_retention_d_h`、`ads_user_retention_d` 等）或充值域。
