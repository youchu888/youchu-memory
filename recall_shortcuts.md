# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| bootstrap daily memory_open repor report | `sessions/tg-rotate-2026-10-19-2208.md` | 冷启动仍先读 bootstrap / MEMORY_OPEN，按任务再查规则；上 |
| g） pr prepare_daily_report_sync sync tg  | `sessions/tg-rotate-2026-10-19-2208.md` | 日报生成链路（双机 sync → 写稿 → 推 TG）与上传云端是**两阶段** |
| id inserted） 不必 不必写入长期记忆索引 主人 于主 | `sessions/tg-rotate-2026-10-19-2208.md` | 成功回执应包含：**日期**、**记录 ID**、**接口状态**（如 inse |
| api config） token upload_work_report.py  | `sessions/tg-rotate-2026-10-19-2208.md` | 凭证与 API 走既有脚本（如 `upload_work_report.py`  |
| asia dd mm shanghai yyyy 定日 | `sessions/tg-rotate-2026-10-19-2208.md` | 未指定日期时默认用 **Asia/Shanghai 当日** `YYYY-MM- |
| tg 一版 上传 上传前宜对照私聊推送记录 不一致 与定 | `sessions/tg-rotate-2026-10-19-2208.md` | 若当日已推 TG，上传前宜对照私聊推送记录，确认与定稿同一版，避免双机/手改导致 |
| dd.md memory mm reports yyyy 一正 | `sessions/tg-rotate-2026-10-19-2208.md` | 上传前以本地定稿 `reports/日报-YYYY-MM-DD.md`（或 me |
| 「上 「生 」分 」时 上传 不重 | `sessions/tg-rotate-2026-10-19-2208.md` | 用户说「上传云端」时，与「生成日报」分离：只跑上传脚本，不重写、不重新汇总正文。 |
| id」 tg 「已 上传 不要 保持 | `sessions/tg-rotate-2026-10-19-2208.md` | 对话收尾保持简短：确认「已上传 + 日期 + 记录 ID」，**不要**再贴完整 |
| markdown 「顺 」后 上传 上传必须 不动 | `sessions/tg-rotate-2026-10-19-2208.md` | 上传必须**原封不动**提交 Markdown；禁止「顺手润色、补条、改格式」后 |
| ## 10 19 2026 agent_session_rotate commi | `~/.dc-platform/memory/lessons/2026-10-19-commit-后默认立即-push-已-push-内容与说明不-retroactive-修改-除.md` | 2026-10-19-commit-后默认立即-push-已-push-内容与说 |
| ## 10 19 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-19-已有-pinned-规则清单默认只追加-改删须先指段落并等用户明确-改.md` | 2026-10-19-已有-pinned-规则清单默认只追加-改删须先指段落并等 |
| 00 02 一指 一日 不删 与私 | `sessions/tg-rotate-2026-10-19-1607.md` | 每日 02:00 扫前一日群聊与私聊；未完成需求记入未做清单，完成只改状态不删行 |
| 1–30 31 pinned pinned.md 写到 新红 | `sessions/tg-rotate-2026-10-19-1607.md` | `PINNED.md` 第 1–30 条不动；新红线写到 `pinned/`，编 |
| 「改 」再 不删 不改 先说 内容 | `sessions/tg-rotate-2026-10-19-1607.md` | 记忆/规则写入：新内容直接追加；已有句子、规则、清单不改不删；要改先说明段落，用 |
| lookup rules.sh 不灌 中后 事时 体事 | `sessions/tg-rotate-2026-10-19-1607.md` | 冷启动不灌规则全文；做到具体事时用 `lookup-rules.sh` 按关键词 |
| api_v1 commit 不夹 不夹带进 不顺 不顺手改 | `sessions/tg-rotate-2026-10-19-1607.md` | 默认只提交业务目录；平台插件与 `api_v1` 不顺手改、不夹带进 commi |
| push 「改 」再 一段 不回 与文 | `sessions/tg-rotate-2026-10-19-1607.md` | 已 push 的说明与文件不回头改；若要改已有内容，先说明改哪一段，等用户明确说 |
| lesson 一轮 不要 不要用旧的提交说明规 不要用旧的提交说明规矩顶上 交及 | `sessions/tg-rotate-2026-10-19-1607.md` | [LESSON: 记忆同步/用户说新规并给出记忆仓提交号时，先看该提交及同一轮同 |
| 23a56c3a48 38e0dc870a 「提 」顶 一轮 交及 | `sessions/tg-rotate-2026-10-19-1607.md` | 用户给出记忆仓提交号（如 `38e0dc870a`）时，先读该提交及同一轮同步的 |
| author co commit cursor pre 上的 | `sessions/tg-rotate-2026-10-19-1607.md` | pre-commit 等钩子会去掉自动加上的 Cursor 署名，提交说明里也不 |
| commit push 「要 不再 不再询问「要不要推」 不要 | `sessions/tg-rotate-2026-10-19-1607.md` | 本地 commit 成功后默认立刻 push 远程，不再询问「要不要推」。 |
| bu bus diff feat git scope | `sessions/tg-rotate-2026-10-19-1607.md` | 提交说明以当前 `git diff` 为准：可保留 `feat(scope):` |
| upload 「按 上传 不是 不是重新生成或改写日报正文 个上 | `sessions/tg-rotate-2026-10-17-2007.md` | 私聊「按你这个上传云端」= 走既有 upload 流程，不是重新生成或改写日报正 |
| id record 「正 写明 对用 尾对 | `sessions/tg-rotate-2026-10-17-2007.md` | 收尾对用户：报日期、record id、状态、稿路径，并写明「正文未改」。 |
| api code id inserted record 一般 | `sessions/tg-rotate-2026-10-17-2007.md` | 成功标准：API `code=0`，响应里可见 record id 与 `ins |
| .cursor config.js date dd downloads git） | `sessions/tg-rotate-2026-10-17-2007.md` | 推荐命令：`.cursor/scripts/upload_work_report |
| as date dd ia mm shanghai） | `sessions/tg-rotate-2026-10-17-2007.md` | 未指定日期时用当日业务日（Asia/Shanghai）；需要时用 `--date |
| 一致 上传 上传前只做一致性核对（路径 上传过程禁止改字 传前 传过 | `sessions/tg-rotate-2026-10-17-2007.md` | 上传前只做一致性核对（路径、日期、正文是否已定稿），上传过程禁止改字、润色或补写 |
| .cursor dd.md log markdown memory mm | `sessions/tg-rotate-2026-10-17-2007.md` | 上传对象必须是已定稿 Markdown：本地 `.cursor/work-log |
| tg 「上 「上传云端」与写日报 」与 」才 上传 | `sessions/tg-rotate-2026-10-17-2007.md` | 「上传云端」与写日报、推 TG 分开；只有用户明确说「上传云端」才跑上传脚本，不 |
| ## 013 013～018 10 17 2026 | `~/.dc-platform/memory/lessons/2026-10-17-周月新增次留不能日人数相加-日表-bitmap-口径-spark-不能照搬-mysql-013-.md` | 2026-10-17-周月新增次留不能日人数相加-日表-bitmap-口径-sp |
| ## 019 10 17 2026 agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-17-019-停留四列写-0-在实时表未就绪前仅可到-s4-禁止发布替换现网.md` | 2026-10-17-019-停留四列写-0-在实时表未就绪前仅可到-s4-禁止 |
| ## 10 17 2026 agent_session_rotate ar | `~/.dc-platform/memory/lessons/2026-10-17-迁-spark-批-s4-只验跑通回写-生产对数放-s5-未点测试五步禁止标验数通过.md` | 2026-10-17-迁-spark-批-s4-只验跑通回写-生产对数放-s5- |
| 00 01 013～018 019 06 07 | `sessions/tg-rotate-2026-10-17-1136.md` | agent-bus：知秋令（10620）回 10616 卡点——007～012、 |
| 00 008）要补进 08 8） dev session | `sessions/tg-rotate-2026-10-17-1136.md` | 远端已有代码（如渠道日活 008）要补进 dev session，避免会话仍停在 |
| _a _日 ad ads.ads_channel_summary_d ads_c | `sessions/tg-rotate-2026-10-17-1136.md` | 渠道汇总仓内无现网 SQL；新 prod 海豚：`wf_ads_日报表_日` → |
| 01 013～018（渠道日指标 13 18 3～ 8（ | `sessions/tg-rotate-2026-10-17-1136.md` | 013～018（渠道日指标、渠道汇总、渠道/部门推广周月等）本轮不推：周月新增/ |
| s4 s5 —— —只 「测 」— | `sessions/tg-rotate-2026-10-17-1136.md` | **S4**：插件里建表、挂调度、跑一天、点「测试五步」——只验能跑通、能回写； |
| 00 007 008 009 010 011 | `sessions/tg-rotate-2026-10-17-1136.md` | 14 张迁 Spark 单里，归因看板（006）已在验数；007/008/009 |
