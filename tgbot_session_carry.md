# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-02 · 最新归档：`sessions/tg-rotate-2026-09-02-0913.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 日报定稿后**默认只推 TG**，**不会自动上传云端**；云端上传须主人明确说「上传云端」
- 核对「是否已上传云端」：查当日 work-log 有无 `upload_work_report.py` 执行记录，**不能**因 TG 已推就推断云端已传
- TG 是否已推：查 `.daily_report_dm_posted.json`（含推送时间戳）
- 定稿稿源：`~/.dc-platform/memory/work-log/reports/日报-YYYY-MM-DD.md`；本地镜像 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`
- 历史日报可补传：定稿仍在则跑 `python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`，**原稿原样**上传，上传前不改字
- 补传成功回执应含：日期、云端 record ID、状态（如 `inserted`）；让用户在填报页按日期核对
- 主人问「昨天日报有没有上传云端」→ 先核三件套：**定稿是否存在 / TG 是否已推 / 云端是否已传**，分项回报
- 工作簿口径**：09:01 群进展只写「截至汇报日之前」的累计状态（等同 T-1 截止）；当天新干的活进 work-log，**次日**工作簿再报，禁止混进当天那份。
- 进度汇报约定**（#450）：说人话；每项写「节点 / 卡点 / 要不要主人拍板」；实查 task 板、work-log、本地代码、git，禁止凭印象。
- 设备指纹 + uid 映射**（最高优先）：`bb905feb` 已按 #7830 改完并交复审；等 PASS 再 explain；dim/dwm/宽表仍 HOLD。
- **本机网络卡点（2026-09-02）**：SR/metadata/跳板 TCP→HTTP404；指标库 video 批与 T-1 巡检挂起，TG#9514。
- **任务自主往下推**：有下一步直接干；卡点 TG 私聊主人，勿等追问。
- 大漏斗 Spark**：sandbox 本地已对齐 test.dws OUT_DB/tagTargets（#7834）；待入库；PASS 前不 explain。
- 「要你拍板：不用」也是有效结论**：口径已定（如 8/1 起点、Phase1 顺序）时明确写，避免主人重复确认。
- [LESSON: daily-report,workbook,work-log|09:01 群进展/工作簿只写 T-1 截止累计进度；当天实活写 work-log，次日工作簿再纳入，禁止当天混报]
- [LESSON: progress-report,agent-bus|主人要任务进度时用人话逐项写节点/卡点/需确认项，并实查 task 板+work-log+git，禁止流水账或凭会话记忆]
- [LESSON: fingerprint,uid-map,HOLD|指纹/uid_map 本地改完须 push 并请知秋再审 PASS 后才可沙箱四步；未 PASS 前 dim/dwm/宽表一律 HOLD]
- **工作簿口径**：09:01 群进展只写「截至汇报日之前」的累计状态（等同 T-1 截止）；当天新干的活进 work-log，**次日**工作簿再报，禁止混进当天那份。
- **举例**：9/1 晚上 push uid_map → 9/1 工作簿不报；9/2 写「9/1 截止：本地已改完，待 push / 待再审」。

