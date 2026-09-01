---
date: 2026-09-01
tags: [metric-library, session-rotate, self-evolve]
severity: medium
domain: ops
---

# req_ref|phase1-migration|Phase1 存量指标无 PRD 挂点时，用 `legacy:metric_standard/<base_na

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

req_ref|phase1-migration|Phase1 存量指标无 PRD 挂点时，用 `legacy:metric_standard/<base_name>` 作过渡 req_ref 可接受；模型文档须注明过渡前缀，避免审核误判为违规

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
