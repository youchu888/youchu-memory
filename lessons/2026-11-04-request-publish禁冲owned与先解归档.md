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
   - **Spark**：必须有 `stage4_spark.mount = {ok:true, group, slot, steps}`（Stage7 只认这个；testcluster 已挂但 state 缺记录 → 向导仍报「S4 还没挂过调度」）
4. `PUT /full` 后再 `request-publish`（`reviewer_username=kakakh7787@gmail.com`）
5. 自检：`index?scope=all` 能搜到该 code 且 `publish_request_status=pending`；`owned[env=test]` 非空（海豚）或 `stage4_spark.mount.ok`（Spark）；`outputs` 非空

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

## 增补 · 2026-11-07（Spark S7 / 七张影子提审）

野花打开 Stage7 报「S4 还没挂过调度」：testcluster **已经挂了**，但是 `state_json.stage4_spark` 被 `PUT /full` 精简覆盖冲掉。插件 S7 **只读** `stage4_spark.mount.ok`（`stage7-spark-panel.ts`），不看 testcluster 现网。

同批还确认：

- 又初 `sr_prod` **只读**，`db_run_ddl_etl` 仅 test → **prod `*_paimon_shadow` 不能自己建**，只能野花审发建表
- 提审/重提审前必须先 `GET /full` 核 mount；缺了从备份或 test 挂载实况 **合并写回**，禁止整份精简 state 覆盖
- 渠道日指标等 T-1 可能为空，笔记写清近有数日即可，不挡影子建表；但 mount 缺失会挡死向导 ①

### Spark 产发前检查清单（每次 request-publish / 催野花 S7 前必跑）

```bash
# 对每个 session code：
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/dev-sessions/<code>/full" | python3 -c "
import sys,json
d=json.load(sys.stdin); s=d.get('state_json') or {}
m=((s.get('stage4_spark') or {}).get('mount') or {})
assert m.get('ok') is True and m.get('group') and m.get('steps'), m
assert s.get('outputs'), 'no outputs'
assert (s.get('stage6_commit') or {}).get('sha'), 'no stage6'
print('OK', m.get('group'), '@', m.get('slot'), 'steps=', m.get('steps'))
"
```

勾选：

1. [ ] `stage4_spark.mount = {ok:true, group, slot, steps}` 与 testcluster 一致
2. [ ] `stage4_db_check`：`created` + `etlRan` + `playbookConfirmed`
3. [ ] `stage5_prod_dryrun` 有记录（影子未建则 `prod_missing` 写明，勿假装已建）
4. [ ] `stage6_commit.sha` 在 `origin/dev`
5. [ ] `outputs[]` 含 `layer` / `table_name` / `ddl_file`
6. [ ] `PUT /full` 只做 **合并**；改前先 GET，保留 mount / owned / publish_runs / s4–s6
7. [ ] `publish_request_status=pending` 且 reviewer=野花；归档先 uncomplete
8. [ ] prod 影子/正式建表：又初无写权限 → 交野花；勿自行 `sr_prod` DDL

修复 mount 被冲：从仍含 mount 的旧 full 备份 **合并** 回 `stage4_spark`（及 s4_db / s5 / s6），再让审核人刷新面板。
