---
date: 2026-11-24
tags: [daily-report,troubleshooting, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 双机日报缺条先读 `hosts/new-mac/当日.md` 是否空壳/仅 mirror，再查 sync；勿把「漏写流水」误判为「同步又坏了」

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

双机日报缺条先读 `hosts/new-mac/当日.md` 是否空壳/仅 mirror，再查 sync；勿把「漏写流水」误判为「同步又坏了」

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
