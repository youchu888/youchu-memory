# test 灌样验数 · dt=2026-06-28

- 时间：2026-07-01
- 环境：prod 只读灌样 → test ETL（v75 · `rewrite_status`）
- 业务日：**2026-06-28**（补跑 schedule `2026-06-29 05:20:00`）

## 灌样规模

| 表 | 行数 |
|---|---:|
| `dwd_user_register_d_v2`（flag=1 · ios · organic） | 7553 |
| `dwd_landing_page_click_d`（T-1~T · 关联 IP） | 3359+ |
| `dwd_landing_page_view_d` | 5792 |

## ETL

- test `dws_register_attribution_result_d` / `channel_apply` / `metrics`：**SUCCESS**
- pi#55530（实例 FAILURE 因下游 `dws_app_user_w_d_new`，归因链无影响）

## 对账（prod 金标 vs test 重算）

| 指标 | prod | test | 判定 |
|---|---:|---:|---|
| `result_d` 行数 | 567 | **567** | ✅ |
| 字段一致（channel/score/status） | — | **567/567** | ✅ |
| `metrics_d_d` 行数 | 3 | **3** | ✅ |
| `rewrite_status` | NULL | NULL（567 行） | ✅ 影子期 |

## 结论

P0 验数通过：test 归因链在 prod 整日样本上与生产结果 **完全一致**。

## 命令

```bash
python3 .claude/database/scripts/attribution_runbook.py copy-sample-to-test \
  --dt 2026-06-28 --limit 8000 --sync-only
# 补 view 后清结果 + complement（schedule T+1 05:20）
```
