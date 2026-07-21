---
date: 2026-06-27
tags: [worker_ant, self-evolve, collaboration, youchu]
severity: medium
domain: ops
source: 用户私聊#8
---

# 又初 · 依工作狂人指令持续进化

## 背景

用户要求又初根据工作狂人（worker_ant）的派单、复核反馈、知识包**不断优化进化**。

## 正确做法

1. **每条 bus 派单收尾**：提炼可复用规则 → `lessons/` 或更新 `worker_ant/INDEX.md`
2. **工作狂人纠正时**（如「别标🔴标增长趋势」「不用回」「待命中」）→ 立即改行为并写 lesson
3. **交叉验证结果**：与工作狂人数对齐后，更新 context-bootstrap 中的「已知结论」
4. **每日 19:30**：主动请教增量知识，不全靠被动派单
5. **禁止**：重复 ack / 重跑已结案核查 / 连 test 报假异常 / 凭记忆不拉 live SQL

## 验证

- 同类派单第二次应更快、更少返工
- `worker_ant/sessions/` 与 `lessons/` 有连续增量

## 关联

- `~/.dc-platform/memory/worker_ant/README.md`
- `.cursor/rules/worker-ant-daily-learn.mdc`
