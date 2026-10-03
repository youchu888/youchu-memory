---
date: 2026-10-03
tags: [onehr, session-rotate, self-evolve]
severity: medium
domain: ops
---

# duty-day|launchd|值班日登记或改 duty 配置后，重启 OneHR 打卡调度进程，否则内存日历不含新值班日，法定假/周末仍会误 skip

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

duty-day|launchd|值班日登记或改 duty 配置后，重启 OneHR 打卡调度进程，否则内存日历不含新值班日，法定假/周末仍会误 skip

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
