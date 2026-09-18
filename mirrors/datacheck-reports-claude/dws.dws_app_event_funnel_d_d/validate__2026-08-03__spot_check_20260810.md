# 大漏斗 spot-check · SF-81 · dt=2026-08-03

**时间**：2026-08-10 15:52 CST  
**环境**：hadoop-1 · Paimon `paimon.dws.*`  
**YARN 冒烟**：r5b `application_2575`（metrics ~6.3h + wide ~17s）

## 结论：**PASS**（playbook part_01~04 全绿）

## part_01 · 分区有数

| is_new | video_view_ev | novel_view_ev | comic_view_ev | pv_users |
|--------|---------------|---------------|---------------|----------|
| -1 | 73 | 0 | 0 | 0 |
| 0 | 57,661 | 5,151 | 10,663 | 74,309 |
| 1 | 49,172 | 1,293 | 3,145 | 26,540 |

宽表 **3 行**（is_new -1/0/1 各 1）· stg **39 行** · 与 r5b 一致。

## part_02 · 视频大小写

| 源 | `video_view` | `VIDEO_VIEW` |
|----|--------------|--------------|
| dwd_video_event_h | **106,906** | 0 |

漏斗 `video_view_event_cnt` 合计 **106,906**，与源 **逐位对齐**。

## part_03 · 小说/漫画 VIEW 大写

| 源 | `VIEW` | `view` |
|----|--------|--------|
| dwd_novel_event_d | **6,444** | 0 |
| dwd_comic_event_d | **13,808** | 0 |

漏斗 novel/comic view 合计与源 **逐位对齐**（6,444 / 13,808）。

## part_04 · page_key>1 过滤

| 指标 | 数值 |
|------|------|
| 漏斗 `app_page_view_user_cnt` 合计 | **100,849** |
| dwd_app_page_view_d 全量 UV（未过滤） | **103,232** |
| 差值（单页用户被剔除） | 2,383（2.3%） |

漏斗 UV **明显小于** 未过滤 DWD 全量 UV，过滤生效。

> 注：全量 dw 明细对照查询耗时长，UV 代理用 `paimon.dwd.dwd_app_page_view_d`；事件级仍以 ETL 源 `dw_user_event_detail_new` 为准。

## 脚本

`ops_system/04.dws/dws_app_event_funnel_d_d/spark/scripts/spot_check_sf81.sql`
