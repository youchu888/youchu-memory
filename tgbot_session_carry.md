# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-24 · 最新归档：`sessions/tg-rotate-2026-10-24-1111.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 问「Spark 跑完没 / 三表有数没」时，不要只看 prod SR 行数；应串联 **prod SR → prod Paimon → 生产 `full_chain.json` 是否挂任务 → dev session 是否已产发 → 上游 snap**。
- 对外结论宜拆两层：**基础设施/上游就绪**（表建好、snap 有数） vs **Spark 三表未挂产/未跑**（产 SR/Paimon 全空）；避免只说「没跑完」造成歧义。
- **prod SR 与 prod Paimon 同为 0 行**，可判定 Spark 链路**从未在产写出过数**（不是「跑慢」或「只没落 SR」）。
- 任务只在 **`full_chain_testcluster` 测试编排**里、**生产 `full_chain.json` 无对应节点** → 产上**根本没挂 Spark 跑**，与「任务失败」要区分开。
- **test SR 有数**（如部门月/周、产品周）可能是**旧海豚口径**；**不能**当作「prod Spark 已跑通」的证据。
- 表按日期重建完成、上游 **snap 已有数**（如 `snap_dt=2026-10-23`），**不自动**代表下游 ADS 三表会有数；中间还缺 **挂产 + 跑批 + 产发**。
- 管理报表三表常一起核对：**`ads_dept_promotion_summary_m` / `_w`**、**`ads_product_promotion_summary_w`**。
- session 停在 **stage7** 且 **`publish_runs_count=0`** → **尚未产发**；产表为空在此状态下是**预期**，不是偶发缺数。
- 要出数的路径：**审核通过（如 `ad004aed`）→ 挂生产 Spark 编排 → 跑批**；或经审批的**手工补跑**，不能假设 snap 好了会自动出 ADS。
- 主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER ADD COLUMN` 完成从「渠道×部门」到「部门×是否免费」的迁移。
- 运维建表脚本要回读原文**：群里的 **`1023.sql` 若按「渠道×部门」主键建表**，等于用旧 PK 覆盖了新 DDL 意图，是「给了新 DDL 但线上仍旧结构」的常见根因之一。
- 交付物要对齐三件套**：交给运维的 DDL、海豚发布 SQL、仓库 canonical DDL/ETL 必须同一批、同一 PK 定义；交付后应用 `SHOW CREATE`/元数据 + live SQL 验收，不能只听「昨天建过了」。
- 与 10-20 同类根因**：**DDL/改表与写表 ETL 未同批对齐**；发版 checklist 应含「表 PK + 任务 INSERT 列清单 + 下游维表是否就绪」。
- [LESSON: ads_dept_promotion_summary_m|ddl|dolphin|半上线|主键变更] 粒度或主键变更时禁止仅 ALTER 加列；运维脚本、SR 现网 PK、海豚 live、Spark 回写须同批对齐，交付后用 SHOW CREATE + live SQL 四方交叉验收。
- **半上线判定**：改口径表要同时核对「仓库 DDL/SQL、海豚 live SQL、test/prod 现网表 PK/粒度、Spark 回写」四层；任一层不一致即半上线，不单看仓库有没有字段。
- **`ads_dept_promotion_summary_m` 目标粒度**：`month × dept × paid_type`，主键含 `paid_type`，**不含 `channel`**；旧口径是 `month × channel × dept`。
- **只 ALTER 加列 ≠ 换主键落地**：现网 PK 仍是 `(month_start_dt, channel, dept_id)`、`paid_type` 可空且不在 PK 时，业务上仍是渠道×部门，不算新 DDL 生效。
- **主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER ADD COLUMN` 完成从「渠道×部门」到「部门×是否免费」的迁移。

