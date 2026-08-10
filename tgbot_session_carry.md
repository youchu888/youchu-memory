# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-11 · 最新归档：`sessions/tg-rotate-2026-08-11-0641.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 用户说「推送云端」= 上传**已定稿**日报，以 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 为准，**上传前禁止改字**
- 日报「生成/定稿/推 TG」与「上传云端」分步：用户单独说「推送云端」时才跑上传，不要自动附带上传
- 大漏斗两阶段 ETL 顺序固定为 `metrics → …`（metrics 先行，勿颠倒）
- 收到「别一直发拦截/说明」类指摘：先改脚本或流程堵根因，再继续推进，禁止反复复读同类拦截话术
- `app_2556` 源表 0 行会导致「任务成功但无产出」假成功；Yarn 日跑已在 `run_yarn_daily_sql.sh` 硬拒绝，勿再误传
- 防踩坑文档落 `spark/README.md` + 会话 `memory.md`：写清冒烟命令、默认 app、下一步清单
- 验数通过后再 commit 推仓并推进 dev-session stage4；勿跳过 spot-check 直接全量压测
- [LESSON: daily-report,cloud-upload|用户说「推送云端」时只传已定稿 reports 文件，禁止改写；成功回执须含云端 record id 与 inserted/updated 状态]
- 未指定日期时默认当日（Asia/Shanghai）；脚本：`.cursor/scripts/upload_work_report.py --date YYYY-MM-DD`
- 上传成功回执应带三要素：**文件路径**、**工号 DN6517**、**云端 record id** 及 `inserted`/`updated` 状态
- 用户从「继续大漏斗」（私聊#287）切到「推送云端」时：**先完成最新明确指令**，再一句询问是否续做挂起任务
- TG 群/旁听：仅被显式 `@youchu_ai_bot / @youchu8888 / @又初 / @初儿` 时才回复；裸提名字或只 @ 他人时不回、也不声明「我不插嘴」
- 用户指出「拦截/说明」类问题时：先改脚本或流程堵住根因，再直接推进任务，禁止反复复读同一段拦截话术
- `app_2556` 源表 0 行会导致「任务成功但无产出」的假成功；已在 `run_yarn_daily_sql.sh` 硬拒绝该 app，后续 Yarn 日跑勿再误传
- 防踩坑文档应落在 `spark/README.md` + 会话 `memory.md`：写清冒烟命令、默认 app、下一步清单，避免下轮重踩
- 验数通过后再 commit 推仓，并推进 dev-session stage4；不要跳过 spot-check 直接上全量压测
- [LESSON: agent-communication,feedback|收到「别一直发拦截了」类指摘时，立刻改工具/规则并继续干活，禁止重复发送同类说明]
- 大漏斗两阶段 ETL 顺序固定为 `metrics → wide`；冒烟默认用 `SF-81`，指定 `dt` 先跑通再扩 profile

