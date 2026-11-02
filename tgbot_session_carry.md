# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-02 · 最新归档：`sessions/tg-rotate-2026-11-02-2100.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 补齐流程：**对照健康 session → 真查 test（stage4）与 prod 缺口（stage5）→ 写回五件 → 挂 outputs / 海豚 target → 补全 playbook**；禁止只改 stage 状态。
- spark_migrate 与 05.ads 海豚稿分离**：周表 Spark 稿勿被海豚 SQL 覆盖；只对齐 **05.ads 海豚发布路径**。
- [LESSON: dev-session,stage7,rel_dir|提审前自检：五件齐、`rel_dir`/outputs/海豚 binding 齐、artifact 非空、本地 SQL 与 test 海豚一致；缺任一项先补再 RP，勿空标 done。]
- dev session 列表能 **pending**，但 stage7 审发布打不开，常见原因是 **stage 1～6 标了 done 却缺 `state_json` 五件**（`strict_mode`、`owner_boundary`、`stage4_db_check`、`stage5_prod_dryrun`、`stage6_commit`），不是单纯「没提审」。
- 五件缺任一项，审核插件读不到真查库 / dryrun / commit 证据，**审发布界面会挂**；仅有 `stage6_commit` 仍不够。
- **`rel_dir` 为空或 `outputs=[]`** 时，插件无法在本机对上目录，**连打开都困难**；本地已有 `ops_system/...` 也要在平台上挂好路径与 outputs。
- 平台 artifact 里 **playbook/README 空壳**、海豚 **`wf_code`/`project_code` 空**，和 state 缺件叠加时，即使有 `rel_dir` 也 **审不了**。
- 提审前 **本地 SQL 须与 test 海豚线上一致**（如推广窗 `promote_start/end`）；发现 test 已改、git 未跟时，**先对齐再 RP**。
- **spark_migrate 与 05.ads 海豚稿分离**：周表 Spark 稿勿被海豚 SQL 覆盖；只对齐 **05.ads 海豚发布路径**。
- 月表从 Spark 迁海豚后，session 目录里 **清掉旧 spark 路径残留**，避免审核误读错误产物。
- 大改 state / outputs / SQL 后：**撤旧 pending 申请 → 重新 request-publish**，避免野花仍看旧快照。
- 审核人侧：**工作区 `dmp/dc-parent` + `git pull`**，再按 session 的 `rel_dir`（如 `ops_system/05.ads/ads_product_promotion_summary_w|_m`）打开。
- 回写补数 / 完成标记必须带 `--hh=<台账槽位>`（与挂账格一致）；缺 `--hh` 会落到墙钟槽位，次日仍判「前一格未了结」、继续挡写。
- 日切附近常见瞬时挂账：告警瞬间水位卡在上一格、`g_day_close_all` 被「前一格未了结」挡住；先拉心跳看是否已自愈，勿立刻手工 `run_step_once`。
- 日结线仍在跑（如 `g_day_close_all` 进度未满）时，不要对挂账那几步重复手工单步跑，避免与调度抢写。
- 上游未就绪（如 `g_base` 等 `dwd_order_paid_d_r`）会连带卡水位与回写；根因要链到挡住的格与依赖，不单看回写步名。
- [LESSON: pushback|complement|台账槽位|回写补数/结案必须 --dt+--hh 对齐挂账格，禁止只用墙钟 hour 否则次日仍判前一格未了结]
- [LESSON: day-close|自愈|日切挂账|日切瞬时挂账先查心跳 pending 与正式表分区，已自愈且日结在跑则勿手跑 run_step_once]

