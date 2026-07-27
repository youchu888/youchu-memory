# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-28 · 最新归档：`sessions/tg-rotate-2026-07-28-0602.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 群聊被 @ 又初/初儿**：必须给实质答复；禁止「没@我/群里不回」类推脱
- 设计链接是否收到**：先查 agent-bus inbox + 当日 TG 镜像；无记录则 bus 狂人问清 library URL / bus# / file_id，勿空猜
- [LESSON: device_tag,dim|device_id 空率≥90%（本需求 100%）则直建 dim_device_all，勿再设计 uid 反查兜底]
- [LESSON: extension,release|vsix 放 dc-platform-server/extension/ 走 git→pull→scp；CHcode 即 tq-git dmp/dc-parent dev，勿与 Desktop 另一 dc-parent 混用]
- **停留时长两条线不可混查**：PRD 五档看板用 `dws_session_duration_user_d`/`device_d`（墙钟 `session_duration_sec` + `duration_bucket`）；账户日页面停留用 `dws_user_page_stay_d`（`daily_valid_stay_sec`）
- **合表 v2 主表**：`dws_session_duration_user_d`/`device_d` 已吸收废弃的 `dws_session_daily_*_d`；查询必带 `stat_grain`（`session`=单次分档+启动次数，`daily`=当日累加分档+账号/设备数）
- **后端对接稿落点**：`omdb/tgbot/outgoing/停留时长表结构-后端对接-*.md`；设计口径源 `ops_system/04.dws/dws_session_duration_d/design.md`
- **群聊被 @ 又初/初儿**：必须给实质答复；禁止「没@我/群里不回」类推脱
- **设计链接是否收到**：先查 agent-bus inbox + 当日 TG 镜像；无记录则 bus 狂人问清 library URL / bus# / file_id，勿空猜
- **bus 时区 bug 曾吞消息**（如 5543/5544）；狂人需重发，通路修后以重发 bus 为准
- **device_tag 新方案**：Paimon 迁移（6 湖表 + wrapper），废 07-20 phased；参照 `origin/dev` user_tag Spark v2 框架；设计稿在 library（如 `dws_device_tag_d_d_design`）
- **device_tag 阶段 1 拍板**：`order_paid_d_r`/`register_v2` device_id fill=100% → 直建 `dim_device_all`；uid 反查兜底方案作废
- **vsix 发版通道（方案 a）**：vsix+manifest 进 `dc-platform-server/extension/` → commit/push `dev` → 狂人 pull + scp 到 `/data/dcpaltform/metadata/extension/` → 验收 `GET /api/v1/extension/version`
- **工作区归属**：CHcode = `tq-git` 的 `dmp/dc-parent` dev；Desktop 另一份 `opengit datacenter/dc-parent` 不是这条发版线
- **extension API 现状**：`api_v1_extension.py` 仅 GET/download，无 POST upload；长期上传通道需另批
- 没 @ 初儿时**静默跳过**，群里**不要**写「这条没 @ 我」「我不插嘴」之类内心戏。
- 群聊口吻学工作狂人：第一句就是结论/在干啥，短句口语，数字 inline，别铺 wiki 式长文。
- 群聊**禁止**用 `##` 标题、markdown 大表格；真要列点用 `·` 或换行，**最多 4 条**。

