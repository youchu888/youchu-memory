---
date: 2026-11-04
tags: [dev-session, request-publish, dolphin_owned_tasks, archive, stage7, 野花]
severity: high
domain: ops
---

# request-publish：禁整份覆盖冲掉 owned；归档 session 须先 uncomplete

## 背景

产品周/月结算口径提审（`dev-20261013-002` / `dev-20261027-001`）。同日两次被拦：野花说看不到申请；打开向导 Step2 报「既无 owned[env=test] 也无 target.task_code」。

## 坑 / 错误做法

1. **已产发 session 仍是 `is_archived=true`** 时直接 `request-publish`：index 上 status=pending，但列表 `include_archived=false` / `scope=review_pending` 默认滤掉 → 审核人侧空白。
2. **`PUT /full` 用精简 `state_json` 整份覆盖**：冲掉 `dolphin_owned_tasks`，`target` 只剩残缺 prod（缺 `project_code`/`wf_code`，或 `env!=test` 无法兜底）→ 产发向导 `resolveOwned(state,"test")` 为空 → Step2「不可同步」。test 海豚上 task 其实还在。同一次还会把 `outputs` 冲成 `[]` → Step1「无 outputs — 回 stage 2/3 补」、ddls/etls=0（表与 DDL 文件其实都在）。

## 正确做法

提审前固定顺序：

1. `GET .../full`，确认 `is_archived`；若已归档 → `POST /api/v1/dev-sessions/{code}/uncomplete`
2. 改 state 时 **合并**：保留原 `dolphin_owned_tasks` / `publish_runs` / stage4～6 产物；需要补绑则 upsert 条目，禁止写成 `[]`
3. 海豚任务至少具备：
   - `dolphin_owned_tasks` 含 `env=test`：`project_code` / `wf_code` / `task_code` / 三元 name
   - `target` 完整 prod + 建议带 `test_task_code`
   - `outputs` 非空：`layer`/`table_name`/`ddl_file`/`etl_files`；prod 已建表则 `prod_table_built=true`
4. `PUT /full` 后再 `request-publish`（`reviewer_username=kakakh7787@gmail.com`）
5. 自检：`index?scope=all` 能搜到该 code 且 `publish_request_status=pending`；`owned[env=test]` 非空；`outputs` 非空

## 验证

```bash
# 非归档 + pending
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/dev-sessions/index?q=<code>&include_archived=false" \
  | python3 -c "import sys,json; i=json.load(sys.stdin)['items'][0]; assert i['publish_request_status']=='pending'"

# owned test 非空
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/dev-sessions/<code>/full" \
  | python3 -c "import sys,json; s=json.load(sys.stdin)['state_json']; assert any(o.get('env')=='test' for o in (s.get('dolphin_owned_tasks') or []))"
```

## 关联

- feedback：`feedback_dev_session_no_fake_stage_done.md`（PUT 合并）
- pinned：`pinned/06-request-publish-owned-archive.md`（红线 35）
- 插件：`vscode-extension/src/owned-resolve.ts` · `prod-publish-wizard.ts` Step2
