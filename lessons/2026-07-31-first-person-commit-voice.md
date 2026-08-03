---
date: 2026-07-31
tags: [git, commit, voice, feedback]
severity: high
domain: ops
updated: 2026-08-03
---

# 提交说明用第一人称直诉，别写旁白

## 背景

commit / 备注要像同事自己交的代码。写「主人要求」「非又初主责（目录禁改）」一眼假。

## 坑 / 错误做法

- 主人、钦定、用户让我
- 旁白体：非某主责、目录禁改、按规则恢复、已沉淀
- 复读内部索引黑话当 commit 正文

反例：`api_v1 与 vscode-extension 非又初主责（目录禁改），恢复为提交前版本。`

## 正确做法

用「我」直说做了啥、为啥。短、口语、可对同事念。

正例：`撤回平台 API 和插件相关改动。这两块不是我维护的，误提交了，已还原。`

## 关联

- `.cursor/rules/first-person-commit-voice.mdc`
- 2026-08-03 禁改撤回那条曾踩坑
