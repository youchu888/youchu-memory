# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-20 · 最新归档：`sessions/tg-rotate-2026-08-20-1912.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 指标库定位是「口径登记 + 物理绑定 + 发布门禁」，不是第四套 BI；ETL 仍在 StarRocks，旁路建新表，不破坏现网 `metric_standard`。
- 发布硬规矩：AI 只能 `propose`，`published` 必须人审；晋升要齐定义、绑定、合规聚合、`req_ref`；比率只存分子/分母；UV 聚合写死 `bitmap_union_count`。
- 指标边界：统计取值条件不同、结果不同 → 必须拆成不同指标，不能同名硬塞；别名可挂多表多列，但口径必须一致。
- 标签链只走 `wrapper_daily_v3.sh`，禁手工逐步跑 base；否则水位不提交会导致翻倍。
- prod 分区是否上线必须问知秋拍板，又初不替主人决策。
- [LESSON: spark|标签链 prod 只跑 wrapper_daily_v3.sh，禁手工逐步跑 base，否则水位不提交会翻倍]
- [LESSON: metric-library|取值条件不同导致结果不同即拆新指标，禁止同名不同义硬合并]
- prod 已确认存在 `dwd.dwd_app_page_view_d`、`ads.ads_product_day_stat_d`；查表存在性优先走 `sr_prod` 的 `information_schema`，别凭记忆答。
- 三层模型：`metric_concept`（业务口径/窗口/聚合，改口径升版）→ `metric_label`（多名字指向同一概念）→ `metric_implementation`（表.列 + formula + 是否主实现；天表/小时表是存储档位，不拆概念）。
- 知秋定调：指标库核心是数据模型，不是人工维护指标清单；日常新增不靠界面手填，走「需求进开发平台 → 程序+AI 对库复用或新建」。
- 人的角色是录需求、审发布；不应承担「指标大姨妈式」手工维稳——口径会变，不能指望人长期手工对齐。
- prod Spark 可用：`hadoop-1` · `/opt/bigdata/spark` · `--master yarn --deploy-mode client`；2026-08-20 03:57 已跑通 dt=2026-08-15 全链（天链→小时框架→结算）。
- 标签链错峰约 03:10；`dim_user_all_d` 下游次日 01:03 才跑，不必赶早。
- TG 在线绿点由 `should_appear_online` 控制：休息窗 13:00–15:00、19:00–20:00 可不绿，其余上班时段保持绿。
- 上传云端以主人私聊贴的正文为准原封不动传；说「按我发的传」时以 #356 定稿版为准，禁止 Agent 自行改字后再传
- [LESSON: daily-report,bus|明日动作术语对齐 bus/工单原文（审核人漏填、回复、上一次与下一次），勿用近义错词]
- 漫画分析链路当前只有账号维 ADS 表 `ads_comic_analysis_account_d`；补数/对码前先确认 scope，别按设备维误查
- test/prod 一致性：拉海豚线版 SQL，去注释后比逻辑；与仓库 `ops_system/05.ads/ads_comic_analysis_account_d/ads_comic_analysis_account_d.sql` 对齐

