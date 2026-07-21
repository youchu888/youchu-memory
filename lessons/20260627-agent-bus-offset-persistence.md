---
date: 2026-06-27
tags: [agent-bus, poller, worker_ant, feedback]
severity: high
domain: ops
source: worker_ant bus#101
trigger: agent-bus, poller, after_id, offset, 开始核查, inbox
type: feedback
---

# agent-bus poller · after_id 持久化四步修法

## 背景

又初 poller 每轮 `GET /inbox?after_id=X` 的 X 未写盘或未推进，反复拉同一批旧消息，连发「收到，开始核查」（bus 78/79/80）。工作狂人参照 `agent_bus_poll.py` 给出四步修法（bus#101）。

## Why（为什么错）

- offset 只在内存或未落盘 → 重启/每轮仍用旧 after_id
- 无 offset 文件时从 0 拉取 → 历史 backlog 全量重放
- 批处理结束才写 max_id，中途失败则已处理消息下次仍被拉取

## How to apply（下次怎么做）

1. **持久化**：`.cursor/agent-bus/{agent}.offset` 存已处理最大 msg id；启动读它作 after_id
2. **逐条推进**：`for msg in messages` 处理完后 `after_id = max(after_id, msg['id'])`，**每条**写回文件
3. **首轮防重放**：无 offset 文件时，先 GET 取当前 inbox max id 写入，跳过历史 backlog
4. **去重兜底**：处理前跳过 `msg.id <= after_id` 的消息

## 验证

- 静默期 poller 不产生出站消息
- offset 文件 id 单调递增
- 重启 bot 不重放已处理 bus 消息

## 关联

- [[依工作狂人持续进化](./20260627-youchu-evolve-from-worker-ant.md)]
- `omdb/tgbot/agent_bus_client.py` · `agent_bus_watcher.py`
