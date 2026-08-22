# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-23 · 最新归档：`sessions/tg-rotate-2026-08-23-0614.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- Phase 0 建表门禁：DDL 草案 §1 五问（test 旁路建四表、口语真源进 `metric_label`、存量可迁不删、derived 只存分子分母、与 Phase2 并行）须知秋拍板；**拍板前不在 test metadata 执行 DDL**
- [LESSON: attribution-report|归因报告脚本跑完后必须核对是否已私聊/发出文件，不能仅以「文件已生成」结案]
- [LESSON: metric-library,phase0|指标库 Phase 0 四表：DDL §1 五问知秋拍板前禁止在 test metadata 建表；`metric.search` 仍走 `metric_standard` 即未落地]
- [LESSON: daily-report,upload|日报上传必须与用户定稿逐字一致，先落盘再上传；同日重复上传为 updated 覆盖，勿擅自改措辞]
- 本周归因产品报告走现成 runbook/脚本生成，产物为 `outgoing/本周归因计算产品报告-{起止日期}.html` + `.md`；算完须核对是否已私聊发出，避免「已生成未投递」
- 归因周报核心口径：开通产品数、有产出数、候选/成功量、综合成功率；需单列表现好（如 DX-092、YC-169 >96%）与需关注（低成功率/低覆盖）产品
- 回写状态仍几乎全影子期，仅 SF-81 开回写——写报告时要带这一背景，避免产品误判已全量回写
- 并行 agent 场景：长任务占一路时，新私聊须独立冷启动读记忆，先 ack/查状态再干活，不假设另一路已交付
- 续推进日计划：对照昨日日报「明日动作」+ 当日 work-log + `MEMORY_OPEN` hold 项，列优先级表再动手
- 指标库 Phase 0：设计稿 `docs/metric_library_concept_model_v0.2_20260817.md`（§3–§4 U1–U7 + G1–G6），DDL 草案 `docs/metric_library_concept_model_ddl_draft.md`；bus#6850 修订已 push dev（`c18e2bdc`），审阅走 bus#6990
- 概念层拆条边界：`granularity` → **`time_window`**（参与拆 concept）；**`storage_granularity`** 放 implementation（`_d`/`_h` 不拆 concept）；`definition` draft 可空；Phase1 存量 264 条迁移一律 **draft**；补 **`v_metric_concept_lifecycle`** 视图
- 验 Phase 0 是否落地：`metric.search` 仍走旧 `metric_standard`（含 `granularity`）即四表未建；MCP 仅有 SR 连接，metadata MySQL DDL 需平台侧或知秋 GO 后跑
- 页面访问 DWS 本地改动默认 **hold**，未明确要求不 commit
- 日报上传：以用户定稿正文**原封不动**落 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 再跑 `upload_work_report.py`；同日同类型云端 **覆盖更新**（非新建）
- 极客小助手打卡：`.env` 设 `JIKE_CHECKIN_ENABLED=false` 即可暂停；TG 日报推送由 old-mac 定时任务处理，上传云端与 TG 推送分开
- 废弃公式** `(pv_cnt − jump_cnt) / pv_cnt` 会大量负值（08-20 约 5,303 行、整月约 0.84%），因 pv/jump 非同口径；产品/前端勿用
- [LESSON: page_visit,datacheck|跳出率只用 dropout_page_cnt/stay_page_cnt；pv 与 jump 不同维度，pv>jump 正常，禁止 (pv-jump)/pv]
- `ads_product_day_stat_d` · `video_play_cnt` 补跑前先查现网 PI 与上游：08-20 已 SUCCESS（PI 32240），SF-68 与 `dwm_user_video_d` 一致；剩余 NULL 多为上游当天无播放，不是漏补

