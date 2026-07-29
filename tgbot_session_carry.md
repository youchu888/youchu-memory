# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-30 · 最新归档：`sessions/tg-rotate-2026-07-30-0643.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- `workbook_progress_service.py` 里 `_progress_device_tag()` 等存在硬编码旧进展（如 SF-81、playbook PASS、Scala 待 push），代码未跟 git/session 实际状态同步就会天天发一样的话
- 主人 07-22（私聊#186/#187）已明确：工作簿进度要反映**当天真实完成情况**，禁止固定模板、禁止像例行交差；虽未逐字说「确认后发群」，语义等同**不能未经主人过目就自动发群**
- 草稿必须带当日证据（分区 dt、行数、git SHA、dev session 状态等），**禁止硬编码旧叙事**；已自动发出的错误帖应标注勿当真，可经确认后补发/更正
- 对照：用户标签 `dws_user_tag_d_d.reg_platform` 为 App/Web/**Other** 三档，用 device **LIKE 模糊匹配**；设备标签与用户标签口径不同，回答字段字典勿混用
- [LESSON: tgbot,workbook-progress|机器人群工作簿进度默认私聊草稿待主人确认后再发，草稿须查库/平台取证，禁止硬编码与探针空快照直接发群]
- 机器人群 09:01 自动进度帖不可当真：须交叉核对「本地发帖记录 + `workbook_live_cache.json` 探针快照 + 当场重查库/平台」三层，探针空快照会走兜底模板文案
- 探针超时/连库失败时 `#3` 归因、`#9` 停留会显示空 dt、0 行或 phase-1 模板句，与 prod/test 真实分区行数严重不符
- 正确流程：狂人 9 点工作簿 → **只生成草稿私聊主人** → 主人「可以发」或改字后再发机器人群 → 未确认则群里不发
- 设备标签 `device` 要分两层：上游 DWD `dwd_user_register_d_v2.device` 是端类型（设计 Android/iOS/PC，线上多为 **ANDROID/IOS/PC** 大写，偶发 OTHER）；宽表 `dws_device_tag_d_d` **无 device 列**，落表为 **`reg_platform`**
- 设备标签 `reg_platform` 映射（SR 老版 + Spark 姿态 F 一致）：ANDROID/IOS→App；PC/WEB/BROWSER/H5→Web；其它/NULL→**App 兜底**（**无 Other**）
- TG 群仅在被显式 @（`@youchu_ai_bot` / `@youchu8888` / `@又初` / `@初儿`）时回复；只 @ 主人账号又初收不到，同事转述须 @ 又初而非 @ 主人或只 @ 蓝猫 bot
- 群聊点名必回实质内容**：正文含「又初/初儿」、@ bot 或 @ 主人时，必须在群里给可验收答复；禁止「没@我」「群里不回」类推脱。
- bothub 未触发要重发新 id**：outbound 对方 poller 没拉到时，用**新 bus id** 重发（如 #5600→#5603），不要复用旧 msg_id；可在 bothub 按 `after_id` 核对 `to_agent=worker_ant`。
- DDL 改列勿用 IF NOT EXISTS 裸建**：`CREATE TABLE IF NOT EXISTS` 会**保留旧 schema**（例：`play_day_flag` 挡住新列 `is_eff_play`）；bootstrap 用 **`combined_N_ddl.sql` 全表 DROP+CREATE**，INSERT 补**显式列清单**，单表热修可单独 repair 脚本。
- 新 launcher 走 `_templates/`**：只填 `JOB` / `SQL` / `PROFILE`，调 `ops_system/_templates/spark_yarn_launcher.sh`；新 wf 先 **step0 DDL bootstrap** 再跑数据链，勿手抄 yarn 参数。
- [LESSON: device-tag,spark,ddl|Paimon/Spark 表结构变更时用 DROP+CREATE bootstrap，禁止仅靠 CREATE TABLE IF NOT EXISTS 期望新列生效]
- [LESSON: ops-system,templates,spark|新 Spark 任务 launcher 只填 JOB/SQL/PROFILE 走 _templates，wrapper 必须先 step0 DDL bootstrap 再跑数]
- **群聊点名必回实质内容**：正文含「又初/初儿」、@ bot 或 @ 主人时，必须在群里给可验收答复；禁止「没@我」「群里不回」类推脱。

