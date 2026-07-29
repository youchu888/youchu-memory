# 死规矩 · Dev Session 禁止空标 stage done（主人 2026-07-29）

**适用**：又初推进任何平台 `dev-session`（含重建、提审、推进 stage、request-publish）。

## 铁律

**stage 1～6 的 `done` 必须伴随 `state_json` 执行产物。**  
列表好看 ≠ 可审。野花 / 审核插件在 stage7 要读前面各阶段「干了什么」；读不到就打不开。

## 禁止

- ❌ 只调 `POST /dev-sessions/{code}/stage/{n}/status` 把 1～6 标成 `done`
- ❌ `PUT /full` 只塞 title / rel_dir / outputs，不写 stage4/5/6 产物
- ❌ 用附件 HTML、口头「已推进」、或「列表 pending 野花」冒充阶段完成
- ❌ 缺产物仍 `request-publish`（等于把空壳交给审核）

## 必须写入 `state_json` 的字段

| key | 含义 | 最低内容 |
|-----|------|----------|
| `strict_mode` | 走法标记 | 如 `light_no_complement` |
| `owner_boundary` | 本侧职责边界 | `our_duty_ends_at` + `we_do_not` |
| `stage4_db_check` | 测试阶段产物 | `created` / `etlRan` / `playbookConfirmed` 全 true，且带 `etlMeta`（真查库结果）；有海豚则带 `live_sql_checks` |
| `stage5_prod_dryrun` | prod 干跑 | `prod_missing`（表/列级）+ `checked_at` |
| `stage6_commit` | 提交记录 | `sha`（`git rev-parse HEAD`）+ `checked_at` |

对照健康样本：`dev-20260727-comic-chapter-001` 等（≥12 key）。空标常见只有 5 个 key。

## 正确顺序

1. 真查 test（列/行/口径）→ 写 `stage4_db_check`
2. 真查 prod 缺什么 → 写 `stage5_prod_dryrun`
3. 记 commit → 写 `stage6_commit` + `owner_boundary` + `strict_mode`
4. `PUT /full` **合并**写入（勿丢既有字段）；stage7 保持 `in_progress`
5. 需要发产才 `request-publish`；**不需要海豚的（如纯 Spark）只补产物、不 RP**

参考脚本：`omdb/projects/event-new-fields/scripts/_strict_rewalk_one.py`

## 自检（提审前必跑）

```bash
# 五件必须齐；缺任一禁止 RP
python3 -c "
import json,urllib.request
# ... GET /api/v1/dev-sessions/<code>/full
need=['strict_mode','owner_boundary','stage4_db_check','stage5_prod_dryrun','stage6_commit']
s4=sj['stage4_db_check']
assert all(k in sj for k in need)
assert s4.get('created') and s4.get('etlRan') and s4.get('playbookConfirmed')
"
```

## 血案

- `dev-20260729-002`：列表 stage7+pending 野花，实质 state 仅 5 key → 审核打不开；主人定性「忽悠」
- 同批 `dev-20260729-001` 亦缺；已严格重走补齐

## 关联

- lesson：`lessons/2026-07-29-dev-session-禁止空标stage须落state产物.md`
- Cursor 规则：`.cursor/rules/dev-session-stage-artifacts-required.mdc`
- 平台文档：`dc-platform-server/docs/task_state_model.md`（Gate1 stage4 三勾）
