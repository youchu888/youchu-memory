---
name: feedback_analyze_instruction_env
description: 指令写明查 prod/test 时必须按该环境执行，禁止分析偏了或口说 prod、实查 test
type: feedback
---

# 分析清楚指令里的环境

## 规矩（主人 2026-08-26）

1. **先读清指令**：用户写了「查 prod / 生产 / 现网」→ 全程按 **prod**；写了 test → 按 test。
2. **禁止**口头说「去 prod 看」却让 `[SQL]` 队列连 test（或反过来）。
3. **禁止**因默认 my.cnf 是 test，就把「查 prod」当成 test 跑完还报 0。
4. 环境冲突时（Agent/MCP 与 SQL 队列不一致）→ **以用户指令环境为准**，不要两套结论打架。
5. **不要擅自改默认 my.cnf**；要解决的是「按指令选对环境」，不是把默认永久切 prod。

## 反例

用户：查 prod 脏表 TSYH-002 注册…  
Bot：好，去 prod 看 → 报 4115 → SQL 队列 test 回 0 行。

## 正例

指令含 prod → COUNT/明细/导出全部 prod，一行结论、一个环境。
