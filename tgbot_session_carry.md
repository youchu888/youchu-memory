# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-06 · 最新归档：`sessions/tg-rotate-2026-09-06-0607.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 用户问「为什么失败」时，先对齐**失败对象**（日报上传 / 大漏斗 / 打卡 / TG 会话状态），不要默认某一种。
- 回报结论要带可核验字段：日期、云端 record ID、最终状态（inserted/updated），便于用户自助核对。
- [LESSON: daily-report,upload|同日重复上传云端是 updated 覆盖同一条记录，inserted→updated 属正常，勿误判为异常]
- 排查顺序：终端输出 → 相关任务日志（如 explain）→ 最近建表/跑数记录 → 再查对应 API/脚本结果。
- 日报「上传云端」成功判定：查 `upload_work_report.py` 执行结果；`code=0` 且有云端记录 ID 即成功。
- 同日同类型日报重复上传会走 **update 覆盖**（先 `inserted` 后 `updated` 是正常行为，不是失败）。
- 云端填报页看不到记录时，优先核对**日期筛选**（如 `2026-09-05`）和页面缓存，让用户刷新后再查。
- TG 里 agent 会话**变红/显示失败**，常与真实 API 结果脱钩；需单独核对实际上传/任务日志，不能只看 TG 状态。
- 若排除上传问题后仍不明，应**追问具体场景**（大漏斗 / 打卡 / 其它），再定向查对应链路。
- 「日报呢」与「上传云端」是不同意图：前者常指定稿/TG 是否已出，后者只执行云端上传，不要混为一谈
- 「上传云端」前置条件：当日定稿 `reports/日报-YYYY-MM-DD.md`（或 memory 镜像）必须已存在
- 定稿已在 → 直接原样上传，禁止改写、润色或补写后再传
- 定稿不在 → 必须先走双机同步 + 写定稿（`prepare_daily_report_sync.sh`），再上传，不可跳过写稿
- 用户指定「上传云端」且定稿日期明确时，以定稿文件日期为准（如周五晚传 2026-09-04），不要默认 T-1
- [LESSON: daily-report|resume|agent-bus|用户只说「日报呢」时先澄清是要查定稿/TG、生成日报还是上传云端，勿默认走上传]
- [LESSON: daily-report|upload|上传云端必须以定稿 Markdown 原封不动上传；定稿缺失时先同步双机写稿，禁止边传边改]
- Cursor 会话 resume 失败时会自动丢弃旧上下文，应提示用户重发指令或发「重启 agent」强制新开
- 上传命令：`.cursor/scripts/upload_work_report.py --date YYYY-MM-DD`；凭证读 `~/Downloads/工作报告/config.js`

