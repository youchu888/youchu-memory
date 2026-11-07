# Spark / 产发踩坑总册（又初）

> **用途**：提审野花、走 Stage7、影子/正式上产前的**唯一归类入口**。  
> **读法**：按类勾选；细节仍以文末「分册」lesson/feedback/红线为准。  
> **更新**：2026-11-07（七张影子 + 点击率正式 + mount 冲掉）

---

## 0. 角色与权限

| 谁 | 能做 | 不能做 |
|----|------|--------|
| 又初 | test 建表/挂 S4、写 state、`request-publish`、prod **只读**核验 | prod DDL/写库、自发 prod 海豚、代点野花完成发布 |
| 野花 | Stage7 向导：prod 建表、挂编排、补数、完成发布 | — |
| 狂人 | 逻辑/可发批、prod 编排 seed（常按 #12151） | — |

- `sr_prod` = **readonly**；`db_run_ddl_etl` **仅 test**
- 普通用户 RP 必须带 `reviewer_username`（野花：`kakakh7787@gmail.com`）
- 群/提审 @ 野花用约定 bot，不代审甩锅

---

## 1. 影子 vs 正式（先定路线）

| 类型 | 规则 |
|------|------|
| **升级表**（海豚现网仍有正式写方） | 可发 `*_paimon_shadow`；pb/`countTable` 写影子；正式表不动，等对平再切 |
| **全新业务**（无旧写方可对账） | **直写正式**；禁影子双跑（红线 36 / #12455） |
| 改 pb 目标 | 必须扫：ETL/`countTable`/DDL/对接/`testcluster` step，禁止只改一处 |

相关：`feedback_new_biz_no_shadow_write_formal.md` · `2026-11-05-全新业务禁影子…` · `2026-11-03-bus12214…`

---

## 2. state / PUT / 提审可见性（最常炸）

| 坑 | 表现 | 正确做法 |
|----|------|----------|
| `PUT /full` 精简覆盖 | owned 空、mount 没了、outputs=[] | **先 GET 再合并**；禁整份精简 state |
| 缺 `stage4_spark.mount` | S7①「S4 还没挂过调度」（test 其实已挂） | 断言 `mount={ok,group,slot,steps}`；冲掉则从备份合并写回 |
| 已归档仍 RP | 野花「待我审核」看不到 | 先 `POST .../uncomplete` |
| index pending / state 不同步 | 审核人无按钮 | RP 后看 index；必要时重提审刷新 note |

红线 35 / 35b · `2026-11-04-request-publish禁冲owned…` · `2026-11-07-spark-s7-提审前mount…`

---

## 3. Stage 证据（禁空标 done）

| Stage | 必有 |
|-------|------|
| 1–3 | spec/design/playbook + DDL/ETL/`task.yaml`/`step.json` 落盘 |
| 4 | 三勾 `created`+`etlRan`+`playbookConfirmed`；**Spark 另要** `stage4_spark.mount`；test 补数 SUCCESS |
| 5 | prod 只读 dry-run / 结构记录；影子未建 → 写 `prod_missing`，勿装已建 |
| 6 | `stage6_commit.sha` 在 `origin/dev`，`pushed` 对齐 |
| 7 | 只 `request-publish`；完成发布走硬闸（见 §5） |

红线 6 · `feedback_dev_session_no_fake_stage_done.md` · `2026-11-02-提审前自检…`

---

## 4. 编排挂载（S4 test → S7 prod）

- test 挂调度：插件 S4 五步自挂；**禁手改** prod/test `full_chain`（除非明确授权）
- S7 **照搬** S4 的 group/slot/steps，不在向导里改组
- 生产组不存在：部署会停或告警；组内步清单上产前扫干净（禁夹带未就绪步，如 CTR 曾夹 `dwd_app_pageitem_d_r`）
- 挂 prod 编排/seed 默认归审核侧/狂人；提审 note 写清分工

`2026-10-27-S4测试五步自挂…` · CTR 组清单 lessons（11-05/11-06）

---

## 5. 建表 / 完成发布硬闸

- Step1 勾 DDL：**先查 prod 实表**（`prod_table_built`），禁只靠 checkbox  
  → `2026-10-28-prod-publish-step1-must-verify-table-exists.md`
- `complete` 硬闸：S1–6 done、表存在、dolphin/spark 步在产、PublishRun>0，否则 **409**  
  → `2026-10-28-prod-publish-complete-hard-gates-all-blockers.md`
- `publish_runs_count=0` = **未产发**；产表 0 行在审发前可以正常  
  → `2026-10-24-stage7-且-publish_runs_count-0…`

---

## 6. 补数 / 验收禁假闭环

- prod 影子**物理表未建、编排未挂**前：禁止编造首跑 HDFS 标记 / prod 行数当闭环  
  → `2026-11-03-bus12214…` · `2026-11-04-prod-影子物理表未建…`
- T-1 偶发 0 行（等上游）：笔记写清近有数日；**不**用空数证明「已上产成功」
- 有点击无曝光等：按 playbook 非阻断项说明，勿当脏数误杀（点击率 part_05）

---

## 7. bucket / 并行度 / 三处代码一致

- 产发 bucket/并行度 **只认 prod 探数**，禁 test 估（红线 33）  
  → `feedback_prod_bucket_from_prod_probe.md` · `pinned/04`
- 发布完成口令：`git SHA` = 本地 `ops_system/...` = 海豚/调度 live SQL  
  → `feedback_publish_git_local_dolphin_triple_sync.md`

---

## 8. 一页检查清单（每次 RP / 催 S7 前）

```text
[ ] 路线：升级影子 or 全新正式（红线 36）已定，pb/countTable/DDL 一致
[ ] GET /full：非归档；或已 uncomplete
[ ] stage4_spark.mount.ok + group/slot/steps（与 testcluster 一致）
[ ] stage4_db_check 三勾；stage5 有记录；stage6_commit.sha 在 origin/dev
[ ] outputs[] 含 layer/table_name/ddl_file（及 etl）
[ ] 海豚任务：owned[env=test] 齐；或 Spark 不依赖海豚 owned
[ ] PUT 只用合并；改前备份 full JSON
[ ] request-publish → reviewer=野花；note 含 commit、影子/正式、prod_missing、分工
[ ] 又初不建 prod 表；不报未建影子的「首跑成功」
[ ] bucket 来自 prod 探数（若本批新建 _r / sink）
[ ] SR DDL 分区：空列表+hist30 或显式≥30 天（禁只写两三天）
```


快速断言：

```bash
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/dev-sessions/<code>/full" | python3 -c "
import sys,json
s=json.load(sys.stdin).get('state_json') or {}
m=((s.get('stage4_spark') or {}).get('mount') or {})
assert m.get('ok') and m.get('group') and m.get('steps'), m
assert s.get('outputs') and (s.get('stage6_commit') or {}).get('sha')
print('OK', m.get('group'), '@', m.get('slot'))
"
```

---

## 9. 分册索引（原文仍保留，本册只归类）

| 主题 | 文件 |
|------|------|
| PUT/owned/归档/mount | `lessons/2026-11-04-request-publish禁冲owned与先解归档.md` |
| mount 专题 | `lessons/2026-11-07-spark-s7-提审前mount与state合并检查.md` |
| 提审五件齐 | `lessons/2026-11-02-提审前自检-五件齐-…` |
| 七张影子 RP | `lessons/2026-11-03-bus12214-…` |
| 影子未建禁假闭环 | `lessons/2026-11-04-prod-影子物理表未建-…` |
| 全新禁影子 | `feedback_new_biz_no_shadow_write_formal.md` · `lessons/2026-11-05-全新业务…` |
| 完成硬闸 | `lessons/2026-10-28-prod-publish-complete-hard-gates-…` |
| Step1 实表 | `lessons/2026-10-28-prod-publish-step1-must-verify-…` |
| 未产发判定 | `lessons/2026-10-24-stage7-且-publish_runs_count-0-…` |
| 三处一致 | `feedback_publish_git_local_dolphin_triple_sync.md` |
| bucket | `feedback_prod_bucket_from_prod_probe.md` · `pinned/04` |
| 空标 done | `feedback_dev_session_no_fake_stage_done.md` |
| 红线续篇 | `pinned/06-request-publish-owned-archive.md` · `pinned/07-new-biz-no-shadow-formal.md` |
| SR 分区说过仍漏 | `lessons/2026-11-07-sr分区红线说过仍漏-影子ddl须空列表或够长历史.md` |

## 10. SR 影子/正式 DDL 分区（建表前硬核 · 说过仍漏过）

规矩早定（`sr-create-history-partitions.mdc` / 红线 26）。**`history_partition_num=30` 写在 PROPERTIES 里 ≠ CREATE 里只列两天也有历史。**

| 对 | 错 |
|----|----|
| `PARTITION BY RANGE(...) ()` + `history_partition_num=30` + `start=-10000` | 只写 `p20261016`/`p20261017` 两天 |
| 或显式 ≥30 天 / 够长的 `START…END…EVERY` | 写了 history=30 却仍只列 2～3 个 `PARTITION` |
| 长列表 + `history=0`（全量历史写死） | 空列表 + `history=0` |

提审 / S7 建表前对 `ops_system/spark_migrate/**/*ddl*.sql`（`ENGINE=OLAP`）：显式 `PARTITION p20*` 个数若 `0 < n < 28` → **阻断**，先改 DDL 再让野花建。

漏检根因（2026-11-07）：影子 DDL 从试验窗口/SHOW CREATE 抄短分区；产发总册盯了 mount/owned，**分区未做成硬勾**。lesson：`2026-11-07-sr分区红线说过仍漏-影子ddl须空列表或够长历史.md`。
