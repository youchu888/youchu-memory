---
date: 2026-07-31
tags: [git, commit, voice, feedback]
severity: high
domain: ops
updated: 2026-08-03
---

# 提交说明用第一人称直述，禁「我 / 主人 / 旁白」

## 背景

commit / 备注要像同事自己交的代码。旁白体或口头自称都不合适。

## 坑 / 错误做法

- 主人、钦定、用户让我
- 正文出现「我把…」「我做了…」
- 旁白体：非某主责、目录禁改、按规则恢复、已沉淀
- 复读内部索引黑话当 commit 正文

反例：`我把归因影子压测落到 _r 表…`  
反例：`api_v1 与 vscode-extension 非又初主责（目录禁改），恢复为提交前版本。`

## 正确做法

**直述**做了什么、为什么；语气是提交人，但**不要写出「我 / 主人」字面**。

正例：`归因影子压测按现网 result→apply→metrics 落到 _r 表与 task 绑定，并加上 test 建 wf 脚本与探表记录，便于后续上 prod 影子。`

## 关联

- 规则：`.cursor/rules/first-person-commit-voice.mdc`
- 纠正：2026-08-03（禁「我」字面 + 禁旁白）
