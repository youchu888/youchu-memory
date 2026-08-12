# Playbook：TG 私聊长活占着时另开 agent（2026-08-12）

**定案**：保持 1 任务 1 agent；长活占着时新私聊再开新 agent；新 agent 必读记忆冷启动。  
**权威补丁**：`~/.dc-platform/memory/patches/tgbot-parallel-agent/`  
**一键应用（旧 Mac）**：`bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh`

## 行为

```
私聊到来
  ├─ agent 空闲 → 原串行路径（exclusive lock + 可 resume workspace cursor chat）
  └─ agent 忙碌 → 另开并行 agent
        · 秒回：「当前有任务在跑，另开 agent 处理本条（会读记忆冷启动）。」
        · 不进「前面还有 N 条」队列
        · cursor_chat_id = None（不 resume 长活会话）
        · system prompt 注入记忆 bootstrap（可刷新 load-memory-context.sh）
        · 不把新 chat id 写回 workspace（避免覆盖长活 resume）
```

软顶：`AGENT_MAX_PARALLEL`（默认 3）。群聊 / agent-bus 派单仍走原 `run_locked` 串行。

## 旧 Mac 更新步骤（同步文档后）

1. 等 memory sync 拉到本 playbook + `patches/tgbot-parallel-agent/` + apply 脚本  
2. 在旧机执行：

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh
# 默认目标：~/Desktop/CHcode/omdb/tgbot
# 可覆盖：TGBOT_DIR=/path/to/omdb/tgbot bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh
```

脚本会：备份 → 覆盖 4 个 py → upsert `.env` → 清 pyc → `restart.sh`

3. 冒烟：

```bash
bash ~/Desktop/CHcode/omdb/tgbot/status.sh
rg 'AGENT_PARALLEL|AGENT_MAX|AGENT_MEMORY' ~/Desktop/CHcode/omdb/tgbot/.env
```

4. 实测：私聊先丢一条长活，再丢「进度」→ 应立刻提示另开 agent，且回复带实查证据。

## 环境变量

| 变量 | 默认 | 含义 |
|------|------|------|
| `AGENT_PARALLEL_WHEN_BUSY` | `true` | 忙时私聊另开并行 |
| `AGENT_MAX_PARALLEL` | `3` | 并行软顶 |
| `AGENT_MEMORY_REFRESH_ON_SPAWN` | `true` | 新开前刷新 bootstrap |

## 改动文件

- `agent_queue.py` — `run_parallel` / `should_spawn_parallel_for_dm`
- `bot.py` — 私聊忙时走并行 + `force_new_agent`
- `prompt_builder.py` — `_load_memory_bootstrap` + 并行说明段
- `config.py` — 三个环境变量

## 关联

- feedback：`feedback_tg_dm_fast_work_dual_track.md`
- lesson：`2026-08-12-daily-report-executor-and-dm-queue.md`
- 记忆 v2：`lessons/2026-08-11-worker-ant-memory-v2-practice.md`
