# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-10 · 最新归档：`sessions/tg-rotate-2026-08-10-0914.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 用户指出「拦截/说明」类问题时：先改脚本或流程堵住根因，再直接推进任务，禁止反复复读同一段拦截话术
- `app_2556` 源表 0 行会导致「任务成功但无产出」的假成功；已在 `run_yarn_daily_sql.sh` 硬拒绝该 app，后续 Yarn 日跑勿再误传
- 防踩坑文档应落在 `spark/README.md` + 会话 `memory.md`：写清冒烟命令、默认 app、下一步清单，避免下轮重踩
- 验数通过后再 commit 推仓，并推进 dev-session stage4；不要跳过 spot-check 直接上全量压测
- TG 群/旁听：仅被显式 `@youchu_ai_bot / @youchu8888 / @又初 / @初儿` 时才回复；裸提名字或只 @ 他人时直接不回，也不要声明「我不插嘴」
- [LESSON: agent-communication,feedback|收到「别一直发拦截了」类指摘时，立刻改工具/规则并继续干活，禁止重复发送同类说明]
- 大漏斗两阶段 ETL 顺序固定为 `metrics → wide`；冒烟默认用 `SF-81`，指定 `dt` 先跑通再扩 profile
- `stage_metrics` 是墙钟瓶颈（样例 ~6.3h），`stage_wide` 通常很快（样例 ~17s）；全量压测前先盯 metrics 阶段是否可接受
- 冒烟验收可看行数结构：宽表 `is_new = -1/0/1` 各 1 行（共 3 行），stg 约 39 行；OOM 未出现才算链路基本可用
- 全量 `M` profile 压 T-1 之前，先按 `playbook.md` 做 SF-81 口径 spot-check（如 `video_view` 大小写、`page_view` 过滤）
- 用户指出「拦截了」时，应直接处理问题并推进，禁止反复复读拦截说明
- r5「假成功」根因：误传 `app_2556`，其源表 0 行仍可能跑完但不产出有效数据
- 防踩坑文档应同步：`spark/README.md` 写冒烟命令，`memory.md` 写下一步清单
- [LESSON: 协作|TG|收到用户「不要一直重复发拦截」时，立刻改行为并交付修复，禁止复读状态模板]
- 大漏斗两阶段 ETL（metrics → wide）在 SF-81、dt=2026-08-03 已跑通，无 OOM，r5b 闭环
- 冒烟默认用 SF-81；宽表 is_new=-1/0/1 各 1 行共 3 行，stg 39 行，可作为最小验收样本
- stage_metrics 墙钟约 6.3h，stage_wide 约 17s；性能瓶颈在 metrics 阶段，压测重点盯 metrics
- 已在 `run_yarn_daily_sql.sh` 硬拒 `app_2556`，从脚本层防误传 app

