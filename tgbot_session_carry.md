# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-21 · 最新归档：`sessions/tg-rotate-2026-08-21-1202.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 页面访问「进入」改口径前必须先对齐现网**：旧 `entry_cnt` = 来路空/`unknown`（外部直达）；新口径 = 本页且 `referrer_page_key` 非空且 ≠ `unknown`（站内跳入），二者语义相反
- `wf_ads_日报表_日` DAG 顺序坑**：`ads_product_day_stat_d` 跑在 `dwm_user_video_d` 前面，当日 `pt` LEFT JOIN 上游为空 → 全 app `video_play_cnt` NULL；次日回写 `pt-1` 才会补上
- **页面访问「进入」改口径前必须先对齐现网**：旧 `entry_cnt` = 来路空/`unknown`（外部直达）；新口径 = 本页且 `referrer_page_key` 非空且 ≠ `unknown`（站内跳入），二者语义相反
- **口语「跳出」≠ 表字段 `dropout_*`**：用户说的离开本页去别页 ≈ 现网 `jump_cnt`（来路=本页、去向≠本页、均非空非 `unknown`）；`dropout_page_cnt` 是停留层末页/超 1800s，别混用
- **改口径标准链路**：改 ETL/SQL → test 发布 → 补约一个月 → 选代表性 app 做 DWS↔DWD 重算对账（进入/跳转 diff=0）→ 再 request-publish 生产
- **补数秒失败先查分区**：静态分区表缺目标分区（如 `p20260721`）会直接失败，补分区后再重跑
- **跨 app 对账来源/去向**：TJ-027 与 JHA-124 的 `page_key` 体系不同，只能看路径结构是否合理，不能按同名页硬对齐
- **自刷新（`referrer_page_key = page_key`）会显著抬高进入**：TJ-027 进入里约半数是自刷新；用户未确认前按字面口径跑，不擅自加 `referrer ≠ 本页`
- **日批 T-1**：问「今天有没有 21 号数据」→ 业务日最新一般是昨天；当天分区要等次日凌晨调度
- **页面访问日表**：`dws.dws_app_page_visit_d_d`，粒度 天 × app × `page_key`
- **又初不能直发 prod**：test 验过后走 `request-publish`，上次 prod 审核发布人是**野花**；发版前 prod 仍跑旧 SQL，历史对齐需另补数
- **`video_play_cnt` 当日 NULL 不一定是任务失败**：任务 SUCCESS 但字段全 NULL 时，先查同工作流上游依赖顺序，再查上游分区是否已有数
- **`wf_ads_日报表_日` DAG 顺序坑**：`ads_product_day_stat_d` 跑在 `dwm_user_video_d` 前面，当日 `pt` LEFT JOIN 上游为空 → 全 app `video_play_cnt` NULL；次日回写 `pt-1` 才会补上
- **依赖顺序类问题处理**：上游已齐后对下游 task 做 COMPLEMENT TASK_ONLY 补跑即可；结构性问题需同步调度/DAG 调整（已通过 agent-bus 同步狂人）
- TG 绿点「休息窗」只控制**能否变灰**，与又初/bot **是否即时回消息无关**；禁止用「在休息窗」解释回复延迟
- 其余上班时段 TG **保持长绿**；极客签到/签退上下班时间**原样不动**，改绿点逻辑时不要连带改打卡窗
- 要看页面间来源/去向分布，必须查 **`dwd.dwd_app_page_view_d`**，按 `(referrer_page_key, page_key)` 聚合；DWS 表本身看不出来向
- [LESSON: dws-app-page-visit|看进入/跳转次数用 DWS；看来源→去向分布必须回查 dwd_app_page_view_d 按 referrer_page_key+page_key 聚合]

