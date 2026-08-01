---
date: 2026-07-31
tags: [git, push, feedback, habit]
severity: high
domain: ops
---

# 提交后立刻推远程，禁止分两步

## 背景

入库/commit 后再单独问「要推吗」浪费回合。

## 正确做法

我说提交/入库 → `git commit` 成功 → **马上** `git push origin HEAD`。
远程超前则 rebase 再推。收尾报 SHA + 已同步。

## 例外

我说只提交不推；或需 force / 含密钥。

## 关联

- 规则：`.cursor/rules/git-commit-then-push.mdc`
