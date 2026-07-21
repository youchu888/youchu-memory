---
date: 2026-07-02
tags: [agent-bus, worker_ant, 协作约定, feedback]
severity: high
domain: ops
source: user + 又初提案
type: feedback
---

# 又初 ↔ 狂人 · agent-bus 三分法约定（2026-07-02）

## 背景

漏判根因是 `message_needs_reply` 靠关键词猜意图。用户建议：**默认都要干活**，仅狂人写明 opt-out 时例外。

## 约定（待狂人拍板）

| 模式 | 狂人正文关键词 | 又初行为 |
|------|----------------|----------|
| **默认·要干** | （无 opt-out） | 60s ACK → 查库/改SQL/发海豚等 → reply 结案 |
| **只回不干** | 不用做 / 暂停 / 不用回 / HOLD / 先待命 / learn_only / 先别动 | 60s short ACK + reply，**不展开技术活** |
| **完全静默** | 这条不用回 / 无需回复 / 不要回复 / 下线存档 | 不 ack、不 reply（TG 可镜像原文） |

### 适用范围

- `from_agent=worker_ant` 且指向又初：`to_agent=youchu_ai` / `to=all` / 正文含又初|初儿

### 代码落点

- `message_needs_reply()` → 默认 True（狂人→又初）
- `message_needs_work()` → 默认 True；只回不干/审核把关结论 → False
- `message_bus_mode()` → `work` | `reply_only` | `silent`
- wake prompt 带 `mode=`，reply_only 时写明「勿查库/改SQL」

## 验证

```bash
python3 -c "
from agent_bus_state import message_bus_mode
assert message_bus_mode('可以开始交付', from_agent='worker_ant', to_agent='all')=='work'
assert message_bus_mode('先 HOLD', from_agent='worker_ant', to_agent='youchu_ai')=='reply_only'
"
```

## 关联

- [静默吞单两坑](./2026-07-02-agent-bus-静默吞单两坑.md)
- `.cursor/rules/agent-bus-session.mdc`
- `agent_bus_state.py`
