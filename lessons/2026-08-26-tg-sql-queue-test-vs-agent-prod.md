---
date: 2026-08-26
tags: [tgbot, sql-queue, my.cnf, dirty-data]
severity: high
domain: ops
---

# TG 先报有数后报 0 行：Agent 看 prod、SQL 队列连 test

## 背景

主人问 TSYH-002 今日脏表注册明细；Bot 先说 4115 条并排队导出，约 1 分钟后又说「0 行 / 无法导出」。

## 坑 / 错误做法

1. Cursor Agent（可走 MCP `sr_prod`）先给出业务结论
2. 同一条回复里 emit `[SQL]` / `[SQL_FILE]`，由 `query_queue` 用 `omdb/.claude/database/my.cnf` 执行
3. 该 my.cnf 指向 **test**（`43.212.113.132`），test 脏表同条件为 **0 行**
4. `_on_query_done` 再发「查询完成（0 行）」→ 与上文矛盾

对照（2026-08-26 `user_register`）：prod ≈4500+；test = 0。

## 正确做法

1. TG 查数默认应对齐 **prod** my.cnf（或显式按用户说的环境切）
2. Agent **禁止**在 SQL 队列结果回来前报确定行数；只能说「已入队」
3. 改 my.cnf / MYSQL_BIN 后重启 bot，并用一条 COUNT smoke

## 验证

同一 SQL：bot runner 行数应与 MCP `sr_prod` 一致（允许分钟级增长差）。

## 主人纠正（2026-08-26）

**不要**把默认 my.cnf 改成 prod。正确做法是：**先分析清指令**——指令写了查 prod，就必须按 prod 执行；分析偏了、口称 prod 实查 test，才是根因。

见 `feedback_analyze_instruction_env.md` / PINNED #22。
