# Spark 读 dwd 一律 `_r`（空表不报错）

## 背景
知秋 2026-09-03 钦定（bus#7862/7863）：Spark 任务读 dwd 层一律用 `_r` 后缀表。非 `_r` 老表可能空（如 `dwd_video_event_h` dt=2026-09-01 → 0 行，`_r` → 13亿+），explain/跑批都不报错，指标会静默全 0。

## 做法
- grep `FROM dwd.dwd_*` 无 `_r` 即改；steps watermark 也用 `_r`
- `dw.dw_user_event_detail_new` 不在此规矩（dw 层且无主键去重）
- `_r` 列类型可能不同（如 play_progress VARCHAR 带小数）→ CAST DOUBLE，禁盲目 CAST INT

## 关联
大漏斗：`dws_app_event_funnel_d_d_daily.sql` 6 处 → commit `96378efc`
