# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-01 · 最新归档：`sessions/tg-rotate-2026-08-01-1002.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 停留时长链路改审核人时，要扫**同链路所有 pending 的 request-publish**，不要只改当前 session；`dev-20260729-002` / `dev-20260711-002` / `dev-20260716-001` 三处曾一并从野花改到蓝猫（`hull367660@gmail.com`）。
- 他人已在 prod 发版后本地跟 session：**先 GET 服务端最新 state，再 merge PUT**；禁止整包覆盖，避免冲掉狂人写的 prod 信息。
- 2026-07 prod 结论：30 业务日全覆盖、分档符合设计、07-30 与上游对账无差；本地大改后**未 commit**，推 `origin/dev` 需主人明示。
- [LESSON: dev-session|session 被 admin 用 fix-metadata 摘表后，本地须同步改 task.yaml、文档口径，设备文件移 `_parked_*` 并为摘出范围新建独立 session，勿把已摘表推回 PUT `/full`]
- 已是 **approved** 的旧 session（如 `dev-20260711-001` DWD page_stay）不会随 pending 批量改审；若 prod 发版也要换人，需**单独处理**。
- `dev-20260729-002` 已收敛为**单目标表** `dws.dws_session_duration_user_d`；设备侧 `dws_session_duration_device_d` 从 outputs / `dolphin_owned_tasks` 摘掉，本地设备文件**移入** `ops_system/04.dws/_parked_session_duration_device_d/`，不要直接删。
- 设备 DWM 独立成新 session **`dev-20260731-001`**（`job_dwm_app_session_sid_device_d`）；用户侧 session 的 `task.yaml` / spec / README / playbook / design / memory 都要改成**单表口径**。
- 平台 session 同步用 **PUT `/full`**，并更新 `related_tables`、`title`、`target.note`；设备侧标 **`stage5.upstream_device=OUT_OF_SCOPE_SEPARATE_SESSION`**。
- prod 海豚已挂：`运营系统` → `wf_dws_汇总_日` → **task_code `180283360953472`**，链尾在 `dws_ad_request_metric_d` 之后；`task_user.yaml` 要补 prod task 绑定。
- DDL 对齐 prod：`start=-10000`、`history_partition_num=30`；`design.md` 补 §10 字段字典、§11 口径说明、§12 prod 发布记录。
- `dolphin_owned_tasks` 可 **test + prod 两条并存**；`related_tables` 仍只保留 user 表。
- prod 验 `dws.dws_session_duration_user_d` 本月：看**分区覆盖**（T-1 下当月最新业务日 0 行正常）、**缺天**、日量级波动。
- 质量抽查：**daily 无 `duration_bucket=0`**（应为 1~5）；**session 为 0~5**；T-1 日与上游 `dwm_app_session_sid_d` 对 `SUM(session_cnt)` / bucket 行数。
- 群聊被显式 `@youchu_ai_bot` / `@youchu8888` / `@又初` / `@初儿` 时必须给实质答复；禁止以「没 @ 我」「群里不回」推脱
- 数仓全链路手册可交付两份：`omdb/tgbot/outgoing/数仓开发手册-人类阅读版.md`（新人 onboarding）与 `…-AI开发版.md`（Agent 执行清单）；内容对齐开发平台 7 阶段 + test 海豚验数 + 提审发 prod，并挂接 `dev_platform_dev` / `dev_platform_publish` 剧本
- `ads.ads_app_event_data_quality_summary_d` 看现网质量用 **prod**；test 同表量级远小，不当 prod 对账口径
- 注册归因「有分数 ≠ 归因成功」：`attribution_status=unattributed` + `unattributed_reason=score_below_threshold` 表示 IP 命中候选并算分，但 `score < score_threshold`（如 JHG-001 门槛 40）
- mvp_v2 总分 = 品牌 + 型号 + 系统名 + 系统版本 + 时间档；设备四维全 miss 时仍可能仅靠时间档拿分（如 11.5h 差 → default 86400 档 +10）

