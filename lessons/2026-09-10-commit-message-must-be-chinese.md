---
date: 2026-09-10
tags: [git, commit-message, chinese, voice, feedback]
severity: high
domain: ops
---

# 本仓库 commit message 冒号后必须汉字

## 背景

主人 09-07 / 09-10 两次纠正：git 提交说明要写汉字。又初仍写成整段英文 subject（如 `fix(attribution): stop-placeholder…`、`feat(funnel): add device_type…`）。

## 正确做法

- 可保留 `feat(scope):` / `fix:` 前缀，**冒号后写中文**
- 起草只看 `git diff`；禁 bus# / 我/主人
- 例：`fix(attribution): 停写占位改为零行 INSERT，兼容海豚 NON_QUERY`
- 例：`feat(funnel): 大漏斗粒度补注册设备与自然/渠道`

## 反例

- 整段英文 subject（已 push 的不擅自 amend；下一条起纠正）

## 硬闸

- 规则：`.cursor/rules/first-person-commit-voice.mdc`
- 钩子：`.githooks/commit-msg` 拒无汉字正文
- 红线：`PINNED.md` §25
