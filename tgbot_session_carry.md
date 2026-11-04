# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-05 · 最新归档：`sessions/tg-rotate-2026-11-05-0602.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 代主人发 TG 群：先私聊贴改稿等确认，未确认前禁止发群、禁止重复发。
- 群消息忌 AI/知识库腔（「正在检索」「上下文整理」「已沉淀」等），宜短句、口语、先结论。
- 忌工单腔（【背景】【请你做】【不做】）；宜对齐主人日常（如 `@xxx 生产执行下`、老哥麻烦…）。
- 事说清即可，忌「定了@我」「好了@我」等收尾；可日常读 TG 学主人群聊口吻。
- 推广周表改源：须 spark+SR 共 4 份 SQL、两份 task.yaml、compare 报告一并 commit 并 push 到 origin/dev，否则不进审核。
- compare 若在 `.claude` 且被 gitignore，提交前先拷到可跟踪路径再 push。
- 狂人审 spark_migrate：分区列 WHERE（如 `dt`、`retention_day`）用字符串比较以保分区裁剪；推广窗相关行同步改。
- 改后须重算对照周（如 10-26）合计/行数，与上一 commit 的 new 一致再提交。
- 审核放行后：先发 test 海豚，再 request-publish 给野花；本侧不自发 prod；首周分区出数后再回行数。
- pageitem 点击率 fanout：作废单表合入，以曝光/点击两张表 + 指定 commit 为准；与 bucket/并行度 bus 流程分开。
- 用户/设备维 SQL 以平台文档 `/library/guide-user-device-base-tables-usage`（doc 83）为准：`dim_user_snap`+`snap_dt`、键 `(app_id,uid)`、设备认 sdk_init、渠道不重算。
- prod 影子表未建时**：首跑 HDFS 标记、行数**现在不能当验收报**；test 影子 T-1 可有数、prod 影子可为 0，结论写进 reply 并等野花审发建表挂载后再补报。
- [LESSON: paimon_shadow|prod 影子物理表未建/未挂载前，禁止把首跑标记与 prod 行数当闭环验收，reply 里写清阻塞项]
- **归因前渠道**：取事件/注册 DWD 自带 `channel`（上报清洗码），**不是** `dim.dim_user_all.channel`（用户级、可归因后回写）。
- **常用归因前来源**：注册 `dwd.dwd_user_register_d_v2.channel`；浏览拆渠道 `dwd.dwd_app_page_view_d.channel`；更底层 `dw.dw_user_event_detail` / `_new.channel`。
- **按 app+渠道看日活**：无现成汇总表；`dwm.dwm_app_active_user_d` **无 channel 列**，需从注册 DWD ∪ 浏览 DWD 自行汇总。
- **渠道产品周/月**（`ads.ads_product_promotion_summary_w` / `_m`）：表内**无 channel**，粒度是 **部门 × 产品**，与「归因前事件 channel」是不同问题，先对齐业务对象再答。
- **产品周/月渠道链路**：上游 `ads.ads_channel_metrics_daily_d`（app_id + channel）→ JOIN `dim.dim_channel_info_all.channel_code` 得 `dept_id/dept_name`；维表对不上的渠道**不进**产品周/月。

