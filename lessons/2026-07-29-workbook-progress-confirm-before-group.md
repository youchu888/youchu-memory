---
date: 2026-07-29
tags: [tg, workbook, group, confirm, feedback]
severity: high
domain: ops
---

# 工作簿进展发机器人群前必须主人确认

## 背景

主人 2026-07-29 私聊纠正：每天确认以后再发群；此前 `workbook` 定时兜底每天 09:01 直接发机器人群，且探针挂掉时内容像同一套模板。

## 正确做法

1. `GROUP_WORKBOOK_REQUIRE_OWNER_CONFIRM=true`（默认）
2. 自动链路只私聊草稿；主人回「确认发群」才发群
3. 勿再默认 `force_post` 绕过确认

## 验证

次日 09:01 后主人私聊应收到草稿而非群里直接出现进展；确认后群里才有一条。
