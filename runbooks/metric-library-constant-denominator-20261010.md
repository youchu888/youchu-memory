# 指标库常数分母（2026-10-10 定）

bus#9931。知秋要求加速。周一（2026-10-12）下班前向 worker_ant 回四条，实数现查 test，不用本文件里的旧账。

## 已定口径

`window_days_7` / `window_days_30` 走 `metric_kind=constant`。

- G4 跳过 active implementation（常数没有落表实现）
- 不造假 impl，也不把窗口天数写成 atomic
- `definition`、`req_ref` 仍要有
- 门禁在 `dc-platform-server/app/services/metric_gate.py`，目前非 derived 都按 atomic 查聚合和 active impl，还没有 constant 分支

## 周一回执（10-12 下班前）

1. test 库实数做到哪，对照 Phase2 published/draft/orphaned、impl active/diverged_pending，以及 Phase3 是否仍读旧 `metric_standard`。
2. constant 档是否已落到 test 门禁和这两条概念。
3. 到 Phase4 切读还剩的步骤、完成日期、验收判据、卡在谁。
4. 能并行的先开。Phase4 切读仍等知秋 GO。
