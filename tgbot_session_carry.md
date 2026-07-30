# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-31 · 最新归档：`sessions/tg-rotate-2026-07-31-0639.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 群聊被显式 `@youchu_ai_bot` / `@youchu8888` / `@又初` / `@初儿` 时必须给实质答复；禁止以「没 @ 我」「群里不回」推脱
- 数仓全链路手册可交付两份：`omdb/tgbot/outgoing/数仓开发手册-人类阅读版.md`（新人 onboarding）与 `…-AI开发版.md`（Agent 执行清单）；内容对齐开发平台 7 阶段 + test 海豚验数 + 提审发 prod，并挂接 `dev_platform_dev` / `dev_platform_publish` 剧本
- `ads.ads_app_event_data_quality_summary_d` 看现网质量用 **prod**；test 同表量级远小，不当 prod 对账口径
- 注册归因「有分数 ≠ 归因成功」：`attribution_status=unattributed` + `unattributed_reason=score_below_threshold` 表示 IP 命中候选并算分，但 `score < score_threshold`（如 JHG-001 门槛 40）
- mvp_v2 总分 = 品牌 + 型号 + 系统名 + 系统版本 + 时间档；设备四维全 miss 时仍可能仅靠时间档拿分（如 11.5h 差 → default 86400 档 +10）
- 归因两开关独立：`is_run=1` 走 result 任务写 `dws_register_attribution_result_d`；`is_rewrite_channel=0` 则 apply 不写 `dim_user_all.channel`——影子期「只算只落表、不改渠道」是预期行为
- 链路拆分：result（算分落结果表）→ apply（仅 `is_rewrite_channel=1` 才 UPDATE 用户渠道）；`rewrite_status` 全 NULL / `rewrite_reason=未回写-app未灰度` 符合未开写回
- 时间衰减分配在 `dim.dim_app_attribution_time_config`（按 `app_id` 多行档：`max_seconds` + `score`）；设备四维分与门槛在 `dim.dim_app_attribution_config`
- 无 app 专属时间分行则 fallback **`default` 四档**：600/40、3600/30、21600/20、86400/10；多档同满足取 **`max_seconds` 最小**（越近分越高）
- ETL（`dws_register_attribution_result_d.sql`）写死：候选须在注册前且间隔 ≤86400s；改配置表 **T+1 日批**生效，历史重算需补跑 result 任务
- 归因口径详述见 `ops_system/04.dws/dws.dws_register_attribution_result_d/归因对接说明.md` §3.3
- 日报「上传云端」：以主人定稿 **原封不动** 更新 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 再跑 `upload_work_report.py`，上传前不改写
- `workbook_progress_service.py` 里 `_progress_device_tag()` 等存在硬编码旧进展（如 SF-81、playbook PASS、Scala 待 push），代码未跟 git/session 实际状态同步就会天天发一样的话
- 主人 07-22（私聊#186/#187）已明确：工作簿进度要反映**当天真实完成情况**，禁止固定模板、禁止像例行交差；虽未逐字说「确认后发群」，语义等同**不能未经主人过目就自动发群**
- 草稿必须带当日证据（分区 dt、行数、git SHA、dev session 状态等），**禁止硬编码旧叙事**；已自动发出的错误帖应标注勿当真，可经确认后补发/更正
- 对照：用户标签 `dws_user_tag_d_d.reg_platform` 为 App/Web/**Other** 三档，用 device **LIKE 模糊匹配**；设备标签与用户标签口径不同，回答字段字典勿混用
- [LESSON: tgbot,workbook-progress|机器人群工作簿进度默认私聊草稿待主人确认后再发，草稿须查库/平台取证，禁止硬编码与探针空快照直接发群]
- 机器人群 09:01 自动进度帖不可当真：须交叉核对「本地发帖记录 + `workbook_live_cache.json` 探针快照 + 当场重查库/平台」三层，探针空快照会走兜底模板文案

