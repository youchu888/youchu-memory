# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-21 · 最新归档：`sessions/tg-rotate-2026-08-21-0000.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- TG 绿点「休息窗」只控制**能否变灰**，与又初/bot **是否即时回消息无关**；禁止用「在休息窗」解释回复延迟
- 其余上班时段 TG **保持长绿**；极客签到/签退上下班时间**原样不动**，改绿点逻辑时不要连带改打卡窗
- 要看页面间来源/去向分布，必须查 **`dwd.dwd_app_page_view_d`**，按 `(referrer_page_key, page_key)` 聚合；DWS 表本身看不出来向
- [LESSON: dws-app-page-visit|看进入/跳转次数用 DWS；看来源→去向分布必须回查 dwd_app_page_view_d 按 referrer_page_key+page_key 聚合]
- 休息窗终版：**周一至周五** 13:00–15:00、19:00–20:00 可灰；**周六** 仅 13:00–15:00 可灰；周六 19:00 已是下班，**不套**晚间休息窗
- 改 TG 在线/绿点逻辑后需**重启相关进程**并口头确认生效时段
- `dws.dws_app_page_visit_d_d` 粒度为 `dt × app × page_key`，只落汇总次数，**不含**来源→去向边
- **`entry_cnt`（进入次数）**：源 `dwd.dwd_app_page_view_d`，按本页 `page_key` 聚合；来路为空或去空格小写后=`unknown` 计 1 次（站外/无明确来路直进）
- **`jump_cnt`（跳转次数）**：同源，按来路页 `referrer_page_key` 挂到本页；来路非空且非 `unknown`、且目标页≠来路页（排除自跳）计 1 次（从本页跳走）
- 两列公共过滤：**仅统计有 uid 账号流量**，空 uid 丢弃；均为 **SUM 次数**，不是 UV
- 表口径文档落仓：`ops_system/04.dws/dws_app_page_visit_d_d/口径_进入与跳转.md`；TG 侧可另导 outgoing 副本
- Cursor 查 ETL/spec 若耗时数分钟，TG bot 可能 **timeout**（库未挂）；长任务应先短回说明，或并行 agent 独立处理
- 用户贴定稿日报要求「上传云端」时，正文**原封不动**上传，不改字；成功返回云端记录 ID 与状态
- 指标库定位是「口径登记 + 物理绑定 + 发布门禁」，不是第四套 BI；ETL 仍在 StarRocks，旁路建新表，不破坏现网 `metric_standard`。
- 发布硬规矩：AI 只能 `propose`，`published` 必须人审；晋升要齐定义、绑定、合规聚合、`req_ref`；比率只存分子/分母；UV 聚合写死 `bitmap_union_count`。
- 指标边界：统计取值条件不同、结果不同 → 必须拆成不同指标，不能同名硬塞；别名可挂多表多列，但口径必须一致。
- 标签链只走 `wrapper_daily_v3.sh`，禁手工逐步跑 base；否则水位不提交会导致翻倍。
- prod 分区是否上线必须问知秋拍板，又初不替主人决策。

