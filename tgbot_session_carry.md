# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-20 · 最新归档：`sessions/tg-rotate-2026-08-20-0638.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 上传云端以主人私聊贴的正文为准原封不动传；说「按我发的传」时以 #356 定稿版为准，禁止 Agent 自行改字后再传
- [LESSON: daily-report,bus|明日动作术语对齐 bus/工单原文（审核人漏填、回复、上一次与下一次），勿用近义错词]
- 漫画分析链路当前只有账号维 ADS 表 `ads_comic_analysis_account_d`；补数/对码前先确认 scope，别按设备维误查
- test/prod 一致性：拉海豚线版 SQL，去注释后比逻辑；与仓库 `ops_system/05.ads/ads_comic_analysis_account_d/ads_comic_analysis_account_d.sql` 对齐
- 文件头 `doc/params`、design 版本号差异不算逻辑不一致；一致才允许 prod 补数
- 补数前先查 prod 分区缺口和上游 `dwd_comic_event_d` 是否有数；本次 prod 仅 08-18 一天，上游 07-20～08-18 共 30 天齐全
- 漫画分析 task：test `22699282398336`、prod `181879084574848`，同在 `wf_ads_日报表_日`
- prod 近一月补数：`TASK_ONLY` + `RUN_MODE_SERIAL`，07-20～08-18，30 个 PI 全 SUCCESS；验收看分区齐全、日级行数约 4.4～4.7 万、核心指标非零
- 单 task 补历史不影响定时 T-1；次日 06:25 仍正常跑
- 写日报前先跑双机 work-log 同步（`prepare_daily_report_sync.sh`），new-mac / old-mac hosts 齐了再定稿
- 主人改「今日结果」：只留指定 TOP 项（本次留漫画分析补数 + 指标库 v0.2），其余删掉后 `--force` 重推 TG
- 明日动作用词对齐工单/bus 原文：「回复」非「回覆」，「上一次与下一次」非「上次与下次」，「审核人漏填」非「审核人空缺」（bus#6679 / dev-20260729-002）
- 对外回复（私聊/Cursor）禁止用「主人」等称呼；直接说事，用「你」，少汇报腔、少旁白体
- 内部规则/记忆文档可保留「主人」作决策出处记录，但**对外输出必须剥离**
- 日报标准链路：双机各自写 work-log → memory git 同步 → 读合并稿 + `hosts/new-mac|old-mac` → 扫当日 transcript/派单去重 → old-mac 推 TG；**禁止跳过同步直接写稿**
- 用户给出定稿正文并说「上传云端」：以用户正文**原封不动**落本地并上传，禁止擅自改写后再传
- [LESSON: daily-report|写/推日报前必须先跑双机 work-log 同步并读合并稿，禁止仅靠 transcript 在同步完成前定稿]
- [LESSON: communication|对外回复禁用「主人」，用「你」直说；内部记忆可留出处词，输出必须剥离]

