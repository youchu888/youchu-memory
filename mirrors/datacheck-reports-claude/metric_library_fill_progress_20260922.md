# 指标库 · ads+dws 填数收口 · 2026-09-22

> test metadata · 未灌 prod · 隧道恢复后续跑完成

## 最终盘点

| 项 | 开干前 | 现在 |
|----|--------|------|
| published | 301 | **658** |
| orphaned | 11 | 11 |
| active implementation | 419 | **1290** |
| 有实现的 ads/dws 表 | 37 | **108** |

## candidate（lineage=`batch_rest_20260922`）

| 状态 | 数 |
|------|----|
| promoted | 826 |
| pending | 99（主要为比率/avg hold + 弱特征列） |
| rejected_non_metric | 45 |

## 批次脚本

- 活跃域：`docs/metric_library_batch1_active_fill_20260922.py`
- 剩余扫表：`docs/metric_library_batch_rest_fill_20260922.py`
- 升档续跑：`docs/metric_library_batch_rest_promote_20260922.py`

## 有意未升 published

- 比率/avg（需人工定 derived 分子分母）
- 无指标名特征的弱度量列
- 影子/备份表（范围外）
