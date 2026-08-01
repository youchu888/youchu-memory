# Stage4 必须做完海豚段，禁止 light_no_complement 半截收工

## 场景
开发平台 Stage4：①数据库三勾通过后，②还要 test 海豚发布/补数/对账。

## 错误
只做 playbook + 线上 SQL 核对，设 `light_no_complement` 跳过补数，留下 stage4=`in_progress`，等用户再问才补。

## 正确
Stage4 一次做完：SQL 对齐 → complement T-1 → 等 SUCCESS → playbook → 写报告 → `stage/4/status=done`。
用户没追问也要收口；不要把「解锁海豚」当成 Stage4 完成。

## 标签
stage4, dolphin_test, session_duration

## 关联
- 总规则：`.cursor/rules/dev-session-stage-complete.mdc`
- 总 lesson：`./2026-07-31-dev-session-stages-complete-or-others-cant-open.md`
