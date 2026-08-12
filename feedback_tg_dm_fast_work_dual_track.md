# Feedback：TG 私聊长任务排队 · 双轨方案（讨论稿 · 待新 Mac 拍板落地）

**来源**：主人 2026-08-12 夜 · old-mac 排查后讨论  
**状态**：方案对齐中；**未改 bot 双轨代码**（仅讨论 + 部分应急修复已上 old-mac）

## 已确认问题

1. 全渠道共用一把 `run_locked` 串行锁；一条长私聊占住，后面全卡（「前面还有 N 条」）。
2. 硬杀 30 分钟不合适：正常长任务常 >30min，不能当主策略。
3. 「忙就新开 agent」若 Fast 也接长任务，堵点只从 1 条变成 2 条，第三条仍卡。

## 主人/又初对齐的目标形态

1. **Fast 轨只准短任务**（白名单）：停了吧 / 进度 / 上传云端 / 整理日报 / 重启 agent / 短问答。  
   长任务（改 ETL、深挖查库、集群跑数、多步核查）**禁止上 Fast**。
2. **长任务单槽串行**（或最多 2 槽，待定）；多出来的长任务排队是正常的。
3. **排队时直连说明 + 三选一**（不占 agent）：  
   `排队` / `打断旧任务改做这个` / `旧的继续、这个先记着稍后做`
4. **急指令永远直连插队**：「停了吧」「重启 agent」不经长队列。
5. **硬超时**：不当常规；若保留仅作僵死兜底（建议 ≥2h 且无心跳才杀）。old-mac 曾临时设 `AI_HARD_TIMEOUT_SEC=1800`，新 Mac 讨论后可改/撤。

## old-mac 已落地的应急项（非双轨本体）

- `cursor_executor` 开始消费 `AGENT_LOOP_WAKE_DAILY_REPORT`（日报不依赖 IDE monitor）
- 21:45 `com.youchu.daily-report-fallback` 未推送则补唤醒
- lesson：`lessons/2026-08-12-daily-report-executor-and-dm-queue.md`
- 08-12 改定日报已云端 `id=70631` + TG 重推

## 新 Mac 续聊时建议拍板

- [ ] Fast 白名单最终列表
- [ ] 长任务并发槽：1 还是 2
- [ ] `AI_HARD_TIMEOUT_SEC`：关掉 / 改 2h+ / 仅无心跳杀
- [ ] 是否立刻改 `omdb/tgbot` 落地双轨（需主人明确允改 bot）

## 关联

- lesson：`2026-08-12-daily-report-executor-and-dm-queue.md`
- 规则：`.cursor/rules/daily-report.mdc`
- 代码（old-mac Application Support）：`agent_bus_cursor_executor.py`、`daily-report-fallback.sh`
