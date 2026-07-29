---
date: 2026-07-29
tags: [dev-session, state_json, stage4_db_check, stage5_prod_dryrun, stage6_commit, request-publish, 野花]
severity: high
domain: ops
---

# 禁止空标 stage done：野花审核要读 stage4/5/6 产物

> **死规矩**（主人 2026-07-29）：已升格为硬反馈 + alwaysApply Cursor 规则，禁止再犯。

## 背景

停留时长 `dev-20260729-002` 列表显示 stage1~6 done + pending 野花，但插件 stage7 审界面打不开。根因不是接口挂了，而是 `state_json` 缺执行产物。

## 坑 / 错误做法

- 只调 `POST .../stage/{n}/status` 把 1~6 标成 done
- 或 `PUT /full` 只塞 title/rel_dir，不写：
  - `strict_mode`
  - `owner_boundary`
  - `stage4_db_check`（created / etlRan / playbookConfirmed + etlMeta）
  - `stage5_prod_dryrun`（prod_missing）
  - `stage6_commit`（sha）
- 结果：野花插件读不到「前面各阶段干了什么」→ 打不开；看起来像忽悠

对照健康任务（如 `dev-20260727-comic-chapter-001`）约 12+ key；空标任务可能只有 5 个 key。

## 正确做法

1. **真走** stage4：test 查表/列/T-1 有数 +（有海豚时）live SQL marker 核对
2. **真走** stage5：prod dry-run，写 `prod_missing`
3. **真走** stage6：记当前 `git rev-parse HEAD` → `stage6_commit.sha`
4. `PUT /full` 写入完整 `state_json`（合并，勿覆盖丢字段）；stage7 保持 `in_progress`
5. 再 `request-publish`（需海豚发产时）；不需要发产的（如 Spark 设备标签）只补产物、**不要** RP

参考：`omdb/projects/event-new-fields/scripts/_strict_rewalk_one.py`

## 验证

```bash
# state_json 必须含这 5 个 key，且 stage4 三勾为 true
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/dev-sessions/<code>/full" \
  | python3 -c "import sys,json;s=json.load(sys.stdin)['state_json'];print(sorted(s));print('s4',s.get('stage4_db_check'))"
```

## 关联

- **硬反馈**：`../feedback_dev_session_no_fake_stage_done.md`
- **Cursor 规则**：`CHcode/.cursor/rules/dev-session-stage-artifacts-required.mdc`（alwaysApply）
- session：`dev-20260729-002`（停留时长，已严格重走 + RP 野花）
- session：`dev-20260729-001`（设备标签，已补产物，不 RP）
- 报告：`ops_system/04.dws/dws_session_duration_d/_strict_rewalk_report.json`
