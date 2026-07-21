---
name: dwd ETL 双模式拆分 + 调度头部规范（2026-05-01）
description: 5 张双模式 dwd ETL 已拆为 _hourly.sql + _daily.sql 并加完整调度头模板；剩余 26 张文件还需补头部。
type: project
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
## 背景 + 头部模板（已落地，已 git 提交）

5 张原"按小时 + 按天"双模式 dwd ETL 已拆成 `_hourly.sql` + `_daily.sql`，每个文件**最上方**统一加调度头：

```sql
-- =============================================================================
-- 任务  : dwd.<table_name> —— 按小时调度 / 按天调度
-- 调度  : 触发频率 + 窗口策略
-- 触发参数（海豚 ${var} 或 $[date] 占位符）：
--   ${hour_partition1/2/3}     当前覆盖窗口的 3 个分区名 (yyyyMMddHH)
--   ${dt_partition1/2/3}       3 个分区对应的日期 (yyyy-MM-dd)
--   ${hour_start_time1/2/3}    3 个分区起点 (yyyy-MM-dd HH:00:00)
--   ${hour_start_time}         INSERT WHERE 区间起
--   ${hour_end_time}           INSERT WHERE 区间止
--   $[yyyy-MM-dd-1]            T-1 日（按天调度用）
--   $[yyyyMMdd-1]              T-1 日（无连字符，分区名 p$[yyyyMMdd-1]HH）
-- 幂等  : INSERT OVERWRITE PARTITION，重跑覆盖目标分区
-- 补数  :
--   * 单点:  海豚补数选定具体时刻 / 日期
--   * 跨段:  按窗口大小批量触发
--   * 整段:  改用对应粒度任务（按天用 _daily / 按小时用 _hourly）
-- =============================================================================

-- INSERT 容错配置（保护字段超长不阻塞整个任务）
SET enable_insert_strict = false;
SET max_filter_ratio = 1.0;

<原 ETL 主体>
```

## 已完成（5 张双模式拆分，已提交）

- `dwd_ad_click_h/` → `_hourly.sql` + `_daily.sql`
- `dwd_coin_consume_h/` → `_hourly.sql` + `_daily.sql`
- `dwd_video_event_h/` → `_hourly.sql` + `_daily.sql`
- `dwd_order_created_h/` → `_hourly.sql` + `_daily.sql`
- `dwd_keyword_search_h/` → `_hourly.sql` + `_daily.sql`

## 待做（26 张文件，下次接着搞）

**12 张已 `_daily.sql / _hourly.sql` 后缀（成对）—— 仅补/规范头部**：
- dwd_ad_impression_h_{daily,hourly}
- dwd_order_paid_d_{daily,hourly}
- dwd_app_page_view_d_{daily,hourly}
- dwd_user_login_d_v2_{daily,hourly}
- dwd_user_register_d_v2_{daily,hourly}
- dwd_user_register_h_{daily,hourly}

**13 张单天调度（`_d.sql`）—— 补头部**：
- dwd_keyword_click_d, dwd_keyword_search_d（在两个目录都有副本）
- dwd_app_page_click_d / dwd_comic_event_d / dwd_novel_event_d
- dwd_ad_click_d / dwd_coin_consume_d / dwd_order_created_d
- dwd_landing_page_click_d / dwd_landing_page_view_d
- dwd_video_collect_d / dwd_video_comment_d / dwd_video_like_d / dwd_video_purchase_d

**1 张单小时调度**：
- `dwd_order_paid_h.sql`

**1 张 df 表（用户指示不动）**：
- `dwd_unknown_event_df.sql`（开发中 + DDL 内置在文件里 + 用户说"我先看看"）

## 校验

- LEFT 截断：[check_dwd_field_truncation.py](../../../Program/datacenter/dc-parent/.claude/database/scripts/check_dwd_field_truncation.py) — 0 OVERSIZE / 0 UNPROTECTED
- SET 容错头：每个文件都有（grep 验证 35/35 都加了）
- 元数据三方覆盖：[check_dwd_metadata_coverage.py](../../../Program/datacenter/dc-parent/.claude/database/scripts/check_dwd_metadata_coverage.py)

## 接续点

下次开搞时直接说"继续 dwd ETL 头部规范化"，按上面"待做 26 张"清单走：
1. 单文件先（13 + 1 + 1 = 15 张），加完头部
2. 12 张成对的（已经有内容，原头部很简短），按统一模板替换头部
3. 跑 LEFT + SET 校验脚本回归一遍
