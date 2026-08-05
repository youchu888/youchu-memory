# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-06 · 最新归档：`sessions/tg-rotate-2026-08-06-0617.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 问「平台指标有没有改」须**先查平台文档**（如 `metric_page_visit_analysis`），再对本地 spec；私聊上文（如 #263「指标已上平台」）必须接上，勿只翻 bus/本地
- agent-bus 发狂人须防**正文截断**；对方回「没看到问题」时补发完整说明，勿只留尾巴
- [LESSON: context-continuity,platform-docs|问指标是否被改时先查平台 metric 文档并对本地 diff，同时读齐私聊上文，禁止跨轮次漏读 #263 类指令]
- 狂人工作簿未更新时，自开任务写入 `omdb/tgbot/data/workbook_supplemental.json`，由 `workbook_progress_service.py` 与狂人清单按编号/标题合并去重，9 点进展与兜底模板一并带上
- 增补项字段：`no`、`title`、`assignee`、可选 `sessions`；狂人日后正式加同名项不会重复两条
- 页面访问 #10 绑定 `dev-20260804-002`（visit_d）+ `dev-20260804-003`（jump_d）；进度探针查 test 最新分区 + 平台 session 状态
- 页面访问在主人说可发前卡点：**stage1–6 不发**（不 commit、不 publish、不 request-publish）
- **8/4 主人拍板即终稿**，不再等知秋改口径；平台文档、spec、ETL 统一按该版
- 进入 = **会话第一页 AND 来路非空**（首屏来路空不算）；跳转 = **去向≠来路**（刷新 from=to 不算）
- 跳出率 `(pv−jump)/pv`，用 `GREATEST` 防负、防 >1；jump 按「来路=本页、去向≠本页」，**非**严格会话 LEAD（#7 可选细化，未改 ETL）
- 平均停留账号+设备都做；末页或 >1800s 不进平均；平均加载仅 `page_load_time > 0`；空 uid/device_id 丢弃
- 数仓只管按天落表；默认日期、筛选、Top5 截断在前端/查询侧；**visit_d + jump_d 两张表**，来源+去向全量落表
- 知秋 8/4 群聊让查 `dwd_app_page_view.page_load_time` 是**探源字段可行性**，不是 visit_d/jump_d 口径修正
- 截至 2026-08-05 初：上述两目录本地仍为 **未跟踪**（`git status` 可见 `??`），入库前勿当已交付
- [LESSON: dev-session-stage|主人说「stage1-6 干完先不发」时：可标 stage done + test 跑通，但 **禁止** 擅自 commit/push/海豚 publish/request-publish]
- 「运营系统·页面访问」表 `dws.dws_app_page_visit_d_d`（`dev-20260804-002`）；口径权威 http://54.255.236.159:8012/library/metric_page_visit_analysis
- 只账号；进入=来路空/`unknown`；只落分子分母；uid_cnt=BITMAP；跳转边表已删
- 代码目录：`ops_system/04.dws/dws_app_page_visit_d_d/`

