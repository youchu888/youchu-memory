---
date: 2026-06-10
tags: [datacheck, playbook, attribution, process]
severity: medium
domain: ops
---

# 核查规则沉淀剧本：playbook 是核心资产

## 原则
- 表/套表核查认可后，规则写进 `.claude/database/playbooks/<db>.<table>.md`
- lesson 记踩坑；playbook 记可执行 SQL + 期望；report 记当次结果
- ETL 无设计文档时，从代码抠出的口径**只能**靠剧本留存

## 归因剧本示例（2026-06-10 增补）
- `part_00` 海豚 schedule ONLINE
- `part_00b` attribution_flag 列错位
- `part_02b` valid_click 漏斗（0 行门禁）
- 硬规则：`attribution_flag=1` 入围、阈值 40、`is_rewrite_channel` 影子期

## 关联
- `.cursor/rules/datacheck-playbook.mdc`
- `.claude/database/playbooks/dws.dws_register_attribution_result_d.md`
