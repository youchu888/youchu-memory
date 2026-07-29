---
date: 2026-07-29
tags: [vscode-extension, advanceToStage, byCode, session-state-not-found, review]
severity: high
domain: ops
---

# 进入 stage 失败 session state not found：advanceToStage 必须带 byCode

## 背景

野花审 `dev-20260729-002` 点 stage → 报 `进入 stage 失败: session state not found in …`

## 坑

`openDevSessionStage` → `advanceToStage(dir)` 只 `readState(dir)`，靠 `resolveCodeByDir` 反查。审核人侧/workspace 与 assignee 不一致时反查失败 → null。

## 正确做法

`advanceToStage(dir, stage, { byCode: session.state.code })`（与 `setStageStatus` 对齐）。

已改：`dev-session.ts` / `extension.ts` / `stage4-test-panel.ts` / `tool-executor.ts`；版本 **0.0.122**。

## 发布

- **又初不得自行升版号 / 打 vsix 发版**（主人 2026-07-29 纠正）
- 代码修了应交给平台同学（野花/超管）正式发版
- 误升的 0.0.122 已回退；线上仍以 **0.0.121** 为准

## 关联

- feedback：`feedback_dev_session_no_fake_stage_done.md`
