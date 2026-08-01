---
date: 2026-08-01
tags: [robustness, habit, ops, feedback]
severity: high
domain: ops
---

# 做事要考虑健壮性

## 背景

memory 同步在新 Mac 长期失败：旧脚本无自愈、冲突后本地提交滚雪球。约定以后做事优先健壮性。

## 正确做法

失败可自愈、不滚雪球、脚本单点版本、幂等、可观测、有兜底、改完当场 smoke。

## 关联

- 规则：`.cursor/rules/robustness-first.mdc`
- 样例：`./2026-08-01-new-mac-memory-sync-old-script.md`
