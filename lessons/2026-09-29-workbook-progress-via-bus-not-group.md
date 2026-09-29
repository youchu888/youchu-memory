---
date: 2026-09-29
tags: [workbook, agent-bus, tg, group]
severity: high
domain: ops
---

# 工作簿进展：不回群，读 bus 后按前一日实查 reply

## 定案

- TG Bot 收不全群消息 → `GROUP_WORKBOOK_PROGRESS_ENABLED=false`，**禁止群内 @ 报进展**
- 狂人把「报进展」转 **agent-bus**；又初整理簿内【又初】+ 簿外自开项，按**前一日实查** `reply`，禁空模版

## 关联

- 规则：`.cursor/rules/workbook-tasks.mdc`「群进展怎么回」
- 快照：`~/.dc-platform/memory/project_youchu_workbook_tasks.md`
