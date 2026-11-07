---
date: 2026-11-04
tags: [paimon_shadow, session-rotate, self-evolve]
severity: medium
domain: ops
---

# prod 影子物理表未建/未挂载前，禁止把首跑标记与 prod 行数当闭环验收，reply 里写清阻塞项

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

prod 影子物理表未建/未挂载前，禁止把首跑标记与 prod 行数当闭环验收，reply 里写清阻塞项

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill


归类入口：[`playbook_spark_prod_publish.md`](playbook_spark_prod_publish.md)
