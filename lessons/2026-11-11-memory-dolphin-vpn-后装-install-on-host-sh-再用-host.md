---
date: 2026-11-11
tags: [testcluster-ssh, session-rotate, self-evolve]
severity: medium
domain: ops
---

# memory|dolphin|VPN 后装 `install-on-host.sh`，再用 hostname/whoami 验 `dolphinschedule

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

memory|dolphin|VPN 后装 `install-on-host.sh`，再用 hostname/whoami 验 `dolphinscheduler-2`，跑集群用 `sudo -iu hadoop`。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
