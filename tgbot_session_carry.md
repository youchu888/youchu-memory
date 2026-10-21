# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-21 · 最新归档：`sessions/tg-rotate-2026-10-21-2208.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 「上传云端」是独立触发词：与写日报、推 TG 分开，主人明确说后才跑上传，不要定稿后自动上传。
- 上传前必须先确认定稿文件存在（如 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 或 memory 镜像路径），再执行脚本。
- 上传内容必须与定稿 Markdown **原封不动**，禁止在上传前改字或二次润色。
- （本段无新坑；未追加 `[LESSON: …]`。）
- 未指定日期时，默认用当日 Asia/Shanghai 的 `YYYY-MM-DD` 作为 `--date`。
- 标准命令：`python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`（凭证走本机 `~/Downloads/工作报告/config.js`，不进 Git、不写进记忆）。
- 成功回执应带三要素：文件名、云端记录 ID、操作类型（如 `inserted` / 覆盖更新），便于主人核对。
- 本段流程前提：日报通常已在 old-mac 定稿并推 TG；「上传云端」是后续可选一步，不重复贴全文到对话（防双推）。
- 私聊编号（如私聊#571）仅作会话溯源，蒸馏记忆时不写入 lesson 正文。
- 主人说「上传云端」时：以当日已定稿 `reports/日报-YYYY-MM-DD.md` 为准，**改字后再传**；未指定日期用当天。
- agent-bus `mode=work`：同一 Cursor 主会话处理，**60 秒内先 ACK**，干完再 **reply** 才结案；reply 成功前不要 `mark_processed`。
- S5 开放后的执行姿态：在平台内对指定 session **自己做 S5**，不要另找绕路（test 假跑、手改 prod 等）。
- [LESSON: dev-platform|S5|stage5|prod-dryrun|知秋定案|2026-10-20|008-012|019|开发者可在生产调度器自送 SQL 跑 S5；禁止覆盖生产在跑步正在用的 SQL 文件；申请发布须 S1～S6 全部完成]
- [LESSON: agent-bus|ack|silent|no-dedup|ACK 可能被 silent 丢弃时用 --no-dedup 重发；结案与对账以 reply 为准，勿因 ACK 未镜像而重复整单]
- 上传前先确认本地定稿文件存在，再跑 `python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`。
- 上传成功以 API 回执为准（如 `status=inserted`、记录 ID）；对话里报结果即可，不必再贴全文（防与 TG 双份）。
- ACK 可能被服务端 **silent 吞掉**（去重/静默策略）；若需确保对方看到，可用 `agent_bus_send.py --no-dedup` 重发 ACK，**以 reply 为结案依据**。
- 平台政策类派单：除 reply 外应同步 **MEMORY_OPEN**（删过时 HOLD/闸）并 **增补 lesson**，避免下次仍按旧闸执行。

