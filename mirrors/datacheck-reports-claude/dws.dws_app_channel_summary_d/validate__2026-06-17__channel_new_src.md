# 数据核查 · 渠道 DWS 切源 dw_user_event_detail_new

**日期**: 2026-06-17  
**环境**: test (sr_test)  
**范围**: `dws_app_channel_summary_d` / `dws_app_channel_dau_d` / `dws_app_channel_summary_h`  
**源表**: `dw.dw_user_event_detail_new`（dt 覆盖 2026-06-10 ~ 2026-06-17，6 个分区）

## 发布

| 任务 | 工作流 | task_code | 版本 | schedule |
|------|--------|-----------|------|----------|
| dws_app_channel_summary_d | wf_渠道分析_日 | 174798586263360 | v11→v12 | 105 ONLINE |
| dws_app_channel_dau_d | wf_dws_汇总_日 | 174729603403601 | v34→v35 | 103 ONLINE |
| dws_app_channel_summary_h | wf_广告渠道扣量_小时 | 174729504382789 | v38→v39 | 97 ONLINE |

Git: `a416a4c` on `origin/dev`

## 补数

- **日表** `summary_d`：COMPLEMENT 调度 2026-06-11 00:00 ~ 2026-06-18 00:05（业务日 06-10~06-17），全部 SUCCESS
- **日表** `dau_d`：COMPLEMENT 调度 2026-06-11 05:20 ~ 2026-06-18 05:20，全部 SUCCESS
- **小时表** `summary_h`：COMPLEMENT 2026-06-10 01:03 ~ 2026-06-18（按 wf 小时 cron 对齐）；增量 INSERT，历史旧源数据仍保留

## UC 对账（日表 vs _new）

### dws_app_channel_summary_d · new_user

| 业务日 | 源 DISTINCT uid (register) | DWS SUM(new_user) | 判定 |
|--------|---------------------------|-------------------|------|
| 2026-06-10 | 14503 | 14503 | ✅ |
| 2026-06-11 | 41172 | 41176 | ⚠️ 差 4（渠道维度 SUM 与全局 DISTINCT 口径差） |
| 2026-06-12 | 无有效事件 | 无分区 | ✅ 源仅 9 行 |
| 2026-06-15 | 3 | 3 | ✅ |
| 2026-06-16 | 58 | 58 | ✅ |
| 2026-06-17 | 2 | 2 | ✅ |

### dws_app_channel_dau_d · active_user_num

| 业务日 | 源 DISTINCT uid (login) | DWS SUM(active_user_num) | 判定 |
|--------|------------------------|--------------------------|------|
| 2026-06-10 | 0 | 无行 | ✅ |
| 2026-06-11 | 0 | 无行 | ✅ |
| 2026-06-15 | 6 | 6 | ✅ |
| 2026-06-16 | 79 | 79 | ✅ |
| 2026-06-17 | 12 | 12 | ✅ |

## 小时表说明

`dws_app_channel_summary_h` 为 **INSERT 增量**，本次仅对 06-10 部分小时槽位跑通新 SQL；06-11 及以后仍含旧源 `dw_user_event_detail` 写入的历史行。若需全量纯净对账，需先按 `date_key` 清理目标区间再按小时补数。

## 结论

- **日表切源 + 补数**：通过（06-11 注册数微小偏差可接受）
- **小时表**：SQL 已发布，调度下一小时起走新源；全量历史重刷待确认是否清表
