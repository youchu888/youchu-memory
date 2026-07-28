# 合表/废弃必须同批下线旧海豚 task

- **日期**：2026-07-28
- **触发**：`dws_session_daily_*` 合进 `duration_*` 后旧 task 仍 ONLINE → test 汇总日连续挂

## 习惯

1. 合表 / DROP 旧表 / outputs 缩表 = **未完成**，直到 test 海豚旧 task 已 `delete_task_in_workflow`
2. README「待下线」禁止当交付；stage 4 工作流含 3b，stage 6 commit 前自检
3. DEPRECATED 的 `task.yaml` 禁止再 `publish-task-sql`（平台后端已 400）
4. 验收至少跑一趟整 wf 调度路径，不要只 TASK_ONLY 新节点

## 关联

- lesson：`lessons/2026-07-28-deprecate-must-offline-old-dolphin-task.md`
- playbook：`server-mcp/prompts/a2a3/playbook/dolphin.md` §5b
