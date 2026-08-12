# Feedback：TG 私聊长活占着时另开 agent（已落地）

**来源**：主人 2026-08-12 夜讨论 → 新 Mac 落地  
**状态**：**代码已改**（本机 `omdb/tgbot`）；旧 Mac 用 memory 补丁一键应用

## 定案

> 保持 1 任务 1 agent。长活占着时 TG 新私聊 → **另开新 agent**；新 agent **必读记忆冷启动**。

不做复杂 Fast/Work 白名单。

## 落地位置

| 项 | 路径 |
|----|------|
| Playbook（流程） | `~/.dc-platform/memory/playbook_tg_dm_parallel_agent.md` |
| 补丁文件 | `~/.dc-platform/memory/patches/tgbot-parallel-agent/` |
| 旧机一键应用 | `bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh` |
| 本机源码 | `omdb/tgbot/{agent_queue,bot,prompt_builder,config}.py` |

## 行为摘要

- 空闲：原串行 + 可 resume workspace cursor chat  
- 忙碌私聊：秒回「另开 agent」→ `run_parallel` + `cursor_chat_id=None` + bootstrap  
- 软顶：`AGENT_MAX_PARALLEL=3`  
- 群聊 / bus 派单：仍 `run_locked`

## 旧 Mac

memory sync 后执行：

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh
```

详见 `playbook_tg_dm_parallel_agent.md`。

## 关联

- playbook：`playbook_tg_dm_parallel_agent.md`
- lesson：`2026-08-12-daily-report-executor-and-dm-queue.md`
- 记忆 v2：`2026-08-11-worker-ant-memory-v2-practice.md`
