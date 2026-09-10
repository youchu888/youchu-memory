---
date: 2026-09-10
tags: [agent-bus, git, funnel, commit]
severity: medium
domain: ops
---

# 给审核人 commit hash 前必须确认已在 origin

## 背景

bus#8346：又初给狂人 `72e070e0`，远端不存在；实际对应已推的 `e27f6f0a`（origin/dev）。

## 正确做法

1. 先 `git push`（提交即推）
2. 再 `git rev-parse origin/<branch>` / `git log -1 --oneline origin/<branch>` 取 hash
3. 禁止甩本地未推、rebase 前、或仅存在于本机的短 hash

## 关联

- bus#8346 大漏斗升维 prod 排队
- PINNED：提交即 push
