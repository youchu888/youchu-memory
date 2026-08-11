---
date: 2026-08-11
tags: [daily-report, work-log, dual-mac, sync]
severity: high
domain: ops
---

# 「hosts 缺」≠「记忆没同步」

## 背景

主人纠正：先同步再整理；双机 21:30 前都要上传记忆。又初交日报时说「双机 hosts 都缺」，被理解成没同步。

## 事实

- old-mac `com.youchu.memory-git-sync` 当晚 21:05~21:47 仍在 push
- 日志反复：`export: (no local day/report)` → 没写 `.cursor/work-log/当日.md`，hosts 导不出
- new-mac 当日无 `hosts/new-mac/当日.md`（上一日有）；记忆仓仍有 `@MacBookdeMacBook-Pro` 提交

## 正确说法

- 同步：youchu-memory git pull/push
- hosts：各机日流水文件；要靠本机写 work-log（或 ops-mirror 兜底）再 export

## 修复

`worklog_dual_mac_sync.py`：本机无日流水时用 `ops-mirror/hosts/<host>/当日.md` 兜底写 hosts。
