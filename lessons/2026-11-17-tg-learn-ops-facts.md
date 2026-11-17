---
date: 2026-11-17
tags: [tg-learn, ops_facts, group_chat, 运维, 王毅]
severity: medium
domain: ops
---

# 晚间 TG 学习要把运维执行事实单独入库

## 背景

狂人问「页面访问 SR 影子谁重建的」时，群/私聊里其实有线索，但日学习只写了 reference/口径/需求，没有「谁执行」的可检索沉淀，只能靠当场追问。

## 坑 / 错误做法

- 把运维回执当成闲聊或只塞进 reference，事后按人名/表名查不到
- 只记工单 SQL，不记执行人

## 正确做法

1. 每晚 `daily_group_chat_learn.py` 抽「运维/执行/重建/DROP/建表完成」→ `group_chat/ops_facts.md`
2. 问「谁执行/重建」时先：`bash ~/.dc-platform/scripts/lookup-rules.sh 王毅 表名`（已含运维事实段）
3. 人工核实的事实可直接在 ops_facts 补一行（人员速查表同步维护）

## 验证

`lookup-rules.sh 王毅 page_visit` 能命中 B2 影子重建行。

## 关联

- 脚本：`memory/scripts/host-sync/daily_group_chat_learn.py`
- 产物：`group_chat/ops_facts.md`
- 检索：`scripts/lookup-rules.sh`
