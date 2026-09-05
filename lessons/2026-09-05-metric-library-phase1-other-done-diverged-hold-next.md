# 指标库 Phase1：other 批已落地，剩余主卡 diverged

- **severity**: medium
- **tags**: metric-library, phase1, published, diverged
- **日期**: 2026-09-05

## 事实

- 2026-09-03 other 批已 `--apply`：`published 200` / `draft 70` / `orphaned 10`
- 2026-09-05 尾批再推 3 条：`uv_ratio`/`max_x`/`max_y` → **published 203**
- OPEN/工作簿曾滞留在「published 120、下一批 other」——以终端 apply 日志 + 真 COUNT 为准，勿只信 OPEN

## 剩余 draft 结构（67）

| 类型 | 条数 | 处理 |
|------|-----:|------|
| diverged_pending HOLD | 64 | 禁止硬升 published |
| avg 不在 G2 白名单 | 2 | `last_month_dau_avg` / `last_week_dau_avg` 等拍板 |
| 运维字段 | 1 | `update_time` 保持 draft |

## 以后怎么做

1. 推进前先 `SELECT lifecycle_status, COUNT(*) FROM metric_concept GROUP BY 1`
2. other/video 脚本跑完立刻改 OPEN + workbook，避免下轮重复开干
3. diverged 只 enrich，不升 published，除非主人/狂人改规则
