---
date: 2026-09-18
tags: [todesk,macos,remote, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ToDesk GUI 升级缺辅助功能权限时自动化点不了安装按钮；pkg 直链有反爬，应走 RustDesk 备援或用户经 TG 传安装包覆盖 `/Applica

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ToDesk GUI 升级缺辅助功能权限时自动化点不了安装按钮；pkg 直链有反爬，应走 RustDesk 备援或用户经 TG 传安装包覆盖 `/Applications/ToDesk.app`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
