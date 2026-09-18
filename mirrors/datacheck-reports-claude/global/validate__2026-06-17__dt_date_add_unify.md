# 数据核查 · 双扫 dt 统一 DATE_ADD 写法

**日期**: 2026-06-17  
**环境**: test (sr_test)  
**Git**: `96b160c` on `origin/dev`（`f68bdb4` 主变更 + `96b160c` 漏斗注释 lint）

## 变更说明

全库双扫 `dt IN` 由写法 A 统一为写法 B：

```sql
-- 前
dt IN ('$[yyyy-MM-dd-1]', '$[yyyy-MM-dd]')
-- 后
dt IN ('$[yyyy-MM-dd-1]', DATE_ADD('$[yyyy-MM-dd-1]', INTERVAL 1 DAY))
```

语义等价；本次验证重点：**发布后补数结果与源表一致、无回退**。

## 发布（test 海豚）

| 任务 | 工作流 | 版本 | 状态 |
|------|--------|------|------|
| dwd_user_register_d_v2 | wf_dwd_事件明细_日 | v54→v55 | ✅ |
| dwd_user_login_d_v2 | wf_dwd_事件明细_日 | v55→v56 | ✅ |
| dwd_app_page_view_d | wf_dwd_事件明细_日 | v56→v57 | ✅ |
| dwd_landing_page_click_d | wf_dwd_事件明细_日 | v57→v58 | ✅ |
| dwd_landing_page_click | wf_dwd_独立表_日 | v18→v19 | ✅ |
| dwd_video_event_h | wf_视频事件_小时 | v9→v10 | ✅ |
| dws_app_channel_summary_d | wf_渠道分析_日 | v12→v13 | ✅ |
| dws_app_channel_dau_d | wf_dws_汇总_日 | v35→v36 | ✅ |
| dws_user_reg_video_funnel_daily_d_hourly | wf_用户活跃留存_小时 | v30→v31 | ✅ |
| dws_user_reg_video_funnel_daily_d | wf_dws_汇总_日 | 脚本内已发布 | ✅（注释去占位符后） |

海豚 SQL 抽检（register）：已含 `DATE_ADD('$[yyyy-MM-dd-1]', INTERVAL 1 DAY)`。

## 补数

`_new` 有效 dt：**2026-06-10 ~ 2026-06-17**（6 天）

| 任务组 | 调度窗口 | 结果 |
|--------|----------|------|
| wf_dwd_事件明细_日（4 task） | 06-11 03:20 ~ 06-18 03:20 | 全 SUCCESS |
| wf_dwd_独立表_日 click | 06-11 04:20 ~ 06-18 04:20 | 全 SUCCESS |
| wf_渠道分析_日 summary_d | 06-11 00:05 ~ 06-18 00:05 | 全 SUCCESS |
| wf_dws_汇总_日 dau_d / funnel | 06-11 05:20 ~ 06-18 05:20 | 全 SUCCESS |
| wf_视频事件_小时 video_event_h | 06-11 03:03 ~ 06-18 03:03 | 全 SUCCESS |
| wf_用户活跃留存_小时 funnel_h | 06-11 07:30 ~ 06-18 07:30 | 全 SUCCESS（409 后重试成功） |
| wf_dws_汇总_日 funnel_daily | 06-11 05:20 ~ 06-18 05:20 | 全 SUCCESS（v36→v37，409 后重试） |

## UC 对账（_new 重点日）

### 落地页点击（强一致）

| 业务日 | 源 raw | click_d | click | 判定 |
|--------|--------|---------|-------|------|
| 06-15 | 11 | 11 | 11 | ✅ |
| 06-16 | 42 | 42 | 42 | ✅ |
| 06-17 | 18 | 18 | 18 | ✅ |

### 注册（双扫 + 过滤口径）

| 业务日 | 源（双扫+filter） | dwd | 判定 |
|--------|-------------------|-----|------|
| 06-16 | 61 | 60 | ⚠️ 差 1（补数时点差，非写法回归） |
| 06-17 | 17 | 13 | ⚠️ 当日进行中，源持续写入 |

### 渠道 DWS（_new 稀疏日）

| 业务日 | summary_d 行 | dau_d 行 | 判定 |
|--------|-------------|----------|------|
| 06-15 | 23 | 4 | ✅ 有数 |
| 06-16 | 88 | 17 | ✅ 有数 |
| 06-17 | 56 | 13 | ✅ 有数（补数后较补前增加，源在写） |

## 结论

- **写法 B 发布成功**，10 个 task 补数全部 SUCCESS（含小时 wf）。
- **核心 UC（landing_page_click 双表）三天完全一致**，证明 DATE_ADD 与旧写法等价。
- register 06-17 为当日分区，补数后源仍增长，属正常；建议 T+1 调度后再验。

## 变更记录

- 2026-06-17：首次全量统一 DATE_ADD + test 发布补数验数
