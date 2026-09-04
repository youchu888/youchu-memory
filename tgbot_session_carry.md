# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-05 · 最新归档：`sessions/tg-rotate-2026-09-05-0617.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 「日报呢」与「上传云端」是不同意图：前者常指定稿/TG 是否已出，后者只执行云端上传，不要混为一谈
- 「上传云端」前置条件：当日定稿 `reports/日报-YYYY-MM-DD.md`（或 memory 镜像）必须已存在
- 定稿已在 → 直接原样上传，禁止改写、润色或补写后再传
- 定稿不在 → 必须先走双机同步 + 写定稿（`prepare_daily_report_sync.sh`），再上传，不可跳过写稿
- 用户指定「上传云端」且定稿日期明确时，以定稿文件日期为准（如周五晚传 2026-09-04），不要默认 T-1
- [LESSON: daily-report|resume|agent-bus|用户只说「日报呢」时先澄清是要查定稿/TG、生成日报还是上传云端，勿默认走上传]
- [LESSON: daily-report|upload|上传云端必须以定稿 Markdown 原封不动上传；定稿缺失时先同步双机写稿，禁止边传边改]
- Cursor 会话 resume 失败时会自动丢弃旧上下文，应提示用户重发指令或发「重启 agent」强制新开
- 上传命令：`.cursor/scripts/upload_work_report.py --date YYYY-MM-DD`；凭证读 `~/Downloads/工作报告/config.js`
- 成功回执应报三项：日期、云端记录 ID、`inserted`/`updated` 状态
- 「上传云端」不替代「生成日报」：写稿、推 TG 是独立链路；用户只说上传时不必再贴全文或重复推 TG
- 连接失败后的续接：用户重发「日报上传云端」即可按标准流程继续，无需复述上一轮失败细节
- 大漏斗沙箱 **explain PASS ≠ 已出数**；explain 结束后必须立刻接 metric 真跑 → wide 真跑，中间不能停，否则 `test.dws` 宽表仍 0 行
- `hadoop-1` 直连常被拒，查 explain/YARN 实况应走**已知入口**，不要死磕直连
- 狂人 **stage_metrics 复审**对象：`563013e7` + 冻结 tag `8b613fb6`；PASS 5 条含 11 张 `_r` 全切、`${DT}` 裸串、18 路 `COUNT(DISTINCT event_id)`、`reg_uids` 换 `dwd_user_register_d_v2_r` 等
- 长时间无回可先查是否已有 reply，再发 **bus 催促**（如 #7911），写明「今天要出数、请优先审」+ 当前 test 进展 + 还差什么 PASS/打回
- [LESSON: funnel|explain PASS 后同一轮会话内立刻接 metric→wide 真跑，开跑前确认源表 T-1 分区有数且 `--dt` 任务日与业务日对齐]
- [LESSON: agent-bus|狂人侧消息常被压缩截断，reply 须贴回 #7900 等待审原文一字不动并写明 commit+tag，勿让进度汇报冒充复审单]

