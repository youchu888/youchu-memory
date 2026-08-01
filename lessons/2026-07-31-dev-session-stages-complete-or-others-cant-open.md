---
date: 2026-07-31
tags: [dev-session, stage1-6, publish_runs, session_duration, strict]
severity: high
domain: ops
---

# Dev Session 必须逐步做完 1–6，少产物别人打不开

## 背景

`dev-20260729-002`（停留时长合表）推进时多次半截收工：只改 stage 状态、Stage4 跳过补数、误删 `spec/design`、缺 `publish_runs`。结果详情页 `undefined.slice`、审核人打不开、用户要追问才补。

约定：**新建需求每一步都要完成，不能少东西。**

## 坑 / 错误做法

1. 空标 `stage_status[n]=done`，无文件 / 无跑数证据
2. Stage4 只勾数据库三勾或 `light_no_complement`，不补数不对账
3. 「目录清爽」删掉 `spec.md`/`design.md`/`playbook.md`，平台详情缺件
4. `state` 缺 `publish_runs`（须至少 `[]`）、`outputs` 缺 `layer`/`table_name`
5. Stage6 本地有文件但未 commit/push，审核人仍看不到
6. 等用户再问「步骤做完了吗」才补 —— 违规

## 正确做法

1. 按 Stage 1→6 **顺序实做**（见 `.cursor/rules/dev-session-stage-complete.mdc` 清单）
2. 每 stage 退出前：产物落 `rel_dir` → 必要则平台 `bulk-pull`/写 state → 再 `stage/n/status=done`
3. Stage4：`SQL 对齐 → complement T-1 → SUCCESS → playbook → 报告 → done`
4. Stage5：prod 只读验证；缺口（如上游表未上 prod）写 WARN，不假装 PASS 满贯
5. Stage6：文档+SQL 一并 commit **并 push**；回写 `stage6_commit`
6. Stage7：默认只 `request-publish`；不自发 prod

## 验证

- `GET /api/v1/dev-sessions/{code}/full`：`files` 含 spec/design/playbook/DDL/ETL/task
- `stage_status` 1–6=`done`；证据块 `stage4_db_check`/`stage4_dolphin_check`/`stage5_prod_dryrun`/`stage6_commit` 齐全
- `publish_runs` 字段存在；详情页可打开
- `git status` 该 `rel_dir` 干净且与 `origin` 同步

## 关联

- 规则：`.cursor/rules/dev-session-stage-complete.mdc`
- 姊妹：`./2026-07-31-stage4-finish-dolphin-not-skip.md`
- session 样例：`dev-20260729-002`
- 报告：`.claude/database/reports/dws.dws_session_duration_user_d/stage4_dolphin__*` / `stage5_prod_dryrun__*`
