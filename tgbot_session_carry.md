# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-01 · 最新归档：`sessions/tg-rotate-2026-09-01-2244.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 工作簿口径**：09:01 群进展只写「截至汇报日之前」的累计状态（等同 T-1 截止）；当天新干的活进 work-log，**次日**工作簿再报，禁止混进当天那份。
- 进度汇报约定**（#450）：说人话；每项写「节点 / 卡点 / 要不要主人拍板」；实查 task 板、work-log、本地代码、git，禁止凭印象。
- 设备指纹 + uid 映射**（最高优先）：bus#7787 定起点 **2026-08-01**；本地 SQL/spec 已改，远程仍 `2f95e122`；push → 请知秋再审 → PASS → 沙箱四步；dim / 六张 dwm / 宽表 **全 HOLD**。
- 大漏斗 Spark**：与 uid_map 同交审链（bus#7756/#7760）；等 PASS，prod 未动。
- 「要你拍板：不用」也是有效结论**：口径已定（如 8/1 起点、Phase1 顺序）时明确写，避免主人重复确认。
- [LESSON: daily-report,workbook,work-log|09:01 群进展/工作簿只写 T-1 截止累计进度；当天实活写 work-log，次日工作簿再纳入，禁止当天混报]
- [LESSON: progress-report,agent-bus|主人要任务进度时用人话逐项写节点/卡点/需确认项，并实查 task 板+work-log+git，禁止流水账或凭会话记忆]
- [LESSON: fingerprint,uid-map,HOLD|指纹/uid_map 本地改完须 push 并请知秋再审 PASS 后才可沙箱四步；未 PASS 前 dim/dwm/宽表一律 HOLD]
- **工作簿口径**：09:01 群进展只写「截至汇报日之前」的累计状态（等同 T-1 截止）；当天新干的活进 work-log，**次日**工作簿再报，禁止混进当天那份。
- **举例**：9/1 晚上 push uid_map → 9/1 工作簿不报；9/2 写「9/1 截止：本地已改完，待 push / 待再审」。
- **task 板分两块**：「截至汇报前」vs「当日实活（不进当天群进展）」，整理时先对齐口径再填。
- **进度汇报约定**（#450）：说人话；每项写「节点 / 卡点 / 要不要主人拍板」；实查 task 板、work-log、本地代码、git，禁止凭印象。
- **设备指纹 + uid 映射**（最高优先）：bus#7787 定起点 **2026-08-01**；本地 SQL/spec 已改，远程仍 `2f95e122`；push → 请知秋再审 → PASS → 沙箱四步；dim / 六张 dwm / 宽表 **全 HOLD**。
- **大漏斗 Spark**：与 uid_map 同交审链（bus#7756/#7760）；等 PASS，prod 未动。
- **指标库 Phase1**：test published 约 10→106；**diverged 全 HOLD**，只 enrich 不升正式；4 批脚本在 `docs/` 未 commit；video ~29、other ~112 待归类；顺序 legacy req_ref → user/login → ad → page → video…
- 工作簿三件套须同频**：`project_youchu_workbook_tasks.md`（权威任务板）、`workbook_supplemental.json`（自开/增补项）、`.cursor/work-log/当日.md` 必须按**当天实活**一起更新；只写 work-log 不回写 task 板，群/bus 进展就会和 reality 脱节。
- PINNED #13 铁律**：读到 09:00 群工作簿或当天有新进展 → **当天内整表覆盖** `project_youchu_workbook_tasks.md`；大活自开也要登「自开任务」，不能只记 work-log。
- 11:00 后仍有交付**：不要只依赖 09:01 一次；应自动补发或私聊一句实态摘要，避免下午活漏报。

