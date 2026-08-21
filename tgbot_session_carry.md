# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-22 · 最新归档：`sessions/tg-rotate-2026-08-22-0604.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 废弃公式** `(pv_cnt − jump_cnt) / pv_cnt` 会大量负值（08-20 约 5,303 行、整月约 0.84%），因 pv/jump 非同口径；产品/前端勿用
- [LESSON: page_visit,datacheck|跳出率只用 dropout_page_cnt/stay_page_cnt；pv 与 jump 不同维度，pv>jump 正常，禁止 (pv-jump)/pv]
- `ads_product_day_stat_d` · `video_play_cnt` 补跑前先查现网 PI 与上游：08-20 已 SUCCESS（PI 32240），SF-68 与 `dwm_user_video_d` 一致；剩余 NULL 多为上游当天无播放，不是漏补
- `video_play_cnt` / 视频播放**不是又初簿内主责**（又初：归因、标签、页面停留、页面访问/大漏斗）；私聊协查≠长期认领；内容排行→蓝猫、视频漏斗→野花
- `dws_app_page_visit_d_d` prod 补数：ALTER 生效（分区 40→70、`p20260721` 已建）后再补；07-22～08-20 已齐时只补缺口日 **07-21**（PI 32284 · 69,777 行），全窗 31 天齐
- **`pv_cnt > jump_cnt` 是预期分布**（prod 约 97.1% 有 PV 行如此），不是 bug：`pv` 按本页 `page_key`，`jump` 按来路 `referrer_page_key`，维度不同
- 自刷新、unknown 来路、会话末页/无效去向：只抬 `pv`/`entry`，不一定产生 `jump`；消费页（如 read_ks_video）jump 远低于 pv 也正常
- **跳出率定稿口径**：`dropout_page_cnt ÷ stay_page_cnt`（停留层 `is_dropout=1`），区间 [0,1]，prod 补数窗内无负值、无 dropout>stay
- **废弃公式** `(pv_cnt − jump_cnt) / pv_cnt` 会大量负值（08-20 约 5,303 行、整月约 0.84%），因 pv/jump 非同口径；产品/前端勿用
- 产品说明落盘：`ops_system/04.dws/dws_app_page_visit_d_d/页面访问指标说明_产品版.md`；技术细则在同目录 `口径_进入与跳转.md`；待拍板：自刷新是否算「进入」
- test 页面访问新口径 v196 + 07-21～08-20 已齐；**prod 仍待野花发版**后再补历史新口径
- 暂停极客打卡：`JIKE_CHECKIN_ENABLED=false`，**签退窗（22:00–22:30）后再重启 tgbot**；VPN/agent-bus/居家抽查不动；**old-mac 若跑 tgbot 须同步改 .env**
- 日报上传云端须**正文原封不动**；TG 私聊发文档：复制到 `omdb/tgbot/outgoing/` 再发附件
- [LESSON: complement,ads|补跑前先核 SUCCESS PI 与上游；下游 NULL 先判上游是否本日无数，避免重复补跑]
- [LESSON: jike_checkin,tgbot|关极客打卡改 .env 并延迟重启过签退窗；双机 tgbot 都要改，VPN/抽查不受影响]
- 页面访问「进入」改口径前必须先对齐现网**：旧 `entry_cnt` = 来路空/`unknown`（外部直达）；新口径 = 本页且 `referrer_page_key` 非空且 ≠ `unknown`（站内跳入），二者语义相反
- `wf_ads_日报表_日` DAG 顺序坑**：`ads_product_day_stat_d` 跑在 `dwm_user_video_d` 前面，当日 `pt` LEFT JOIN 上游为空 → 全 app `video_play_cnt` NULL；次日回写 `pt-1` 才会补上
- **页面访问「进入」改口径前必须先对齐现网**：旧 `entry_cnt` = 来路空/`unknown`（外部直达）；新口径 = 本页且 `referrer_page_key` 非空且 ≠ `unknown`（站内跳入），二者语义相反

