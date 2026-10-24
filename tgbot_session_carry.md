# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-24 · 最新归档：`sessions/tg-rotate-2026-10-24-1011.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER ADD COLUMN` 完成从「渠道×部门」到「部门×是否免费」的迁移。
- 运维建表脚本要回读原文**：群里的 **`1023.sql` 若按「渠道×部门」主键建表**，等于用旧 PK 覆盖了新 DDL 意图，是「给了新 DDL 但线上仍旧结构」的常见根因之一。
- 交付物要对齐三件套**：交给运维的 DDL、海豚发布 SQL、仓库 canonical DDL/ETL 必须同一批、同一 PK 定义；交付后应用 `SHOW CREATE`/元数据 + live SQL 验收，不能只听「昨天建过了」。
- 与 10-20 同类根因**：**DDL/改表与写表 ETL 未同批对齐**；发版 checklist 应含「表 PK + 任务 INSERT 列清单 + 下游维表是否就绪」。
- [LESSON: ads_dept_promotion_summary_m|ddl|dolphin|半上线|主键变更] 粒度或主键变更时禁止仅 ALTER 加列；运维脚本、SR 现网 PK、海豚 live、Spark 回写须同批对齐，交付后用 SHOW CREATE + live SQL 四方交叉验收。
- **半上线判定**：改口径表要同时核对「仓库 DDL/SQL、海豚 live SQL、test/prod 现网表 PK/粒度、Spark 回写」四层；任一层不一致即半上线，不单看仓库有没有字段。
- **`ads_dept_promotion_summary_m` 目标粒度**：`month × dept × paid_type`，主键含 `paid_type`，**不含 `channel`**；旧口径是 `month × channel × dept`。
- **只 ALTER 加列 ≠ 换主键落地**：现网 PK 仍是 `(month_start_dt, channel, dept_id)`、`paid_type` 可空且不在 PK 时，业务上仍是渠道×部门，不算新 DDL 生效。
- **主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER ADD COLUMN` 完成从「渠道×部门」到「部门×是否免费」的迁移。
- **prod 典型错配**：海豚 task 已按新列写（无 `channel`、有 `paid_type`），SR 表 PK 仍要 `channel` → 写表对不上；叠加 **`dim_channel_info_all` 空** 等依赖，可出现 **prod 0 行**。
- **test 典型错配**：表半改（加列未换 PK），海豚 live 仍 **渠道拆行 + `paid_type` 用 MAX 当属性**，与仓库 `ops_system/05.ads/...` 新稿不一致；有行数也不代表新口径。
- **prod 海豚 vs test 海豚可能不同步**：摘录中 prod live 已接近仓库新稿，test live 仍旧 SQL——环境间不能假设「一起升了」。
- **Spark 影子/回写链也要对**：除海豚外，Spark 写 SR 的 SQL 是否含 `paid_type`、粒度是否与 DDL 一致，要单独查，避免「海豚对了、回写漏维」。
- **运维建表脚本要回读原文**：群里的 **`1023.sql` 若按「渠道×部门」主键建表**，等于用旧 PK 覆盖了新 DDL 意图，是「给了新 DDL 但线上仍旧结构」的常见根因之一。
- **交付物要对齐三件套**：交给运维的 DDL、海豚发布 SQL、仓库 canonical DDL/ETL 必须同一批、同一 PK 定义；交付后应用 `SHOW CREATE`/元数据 + live SQL 验收，不能只听「昨天建过了」。
- 上游缺表时**不要只修 snap 或 SR DDL**；应 **spark-sql 实查 prod Paimon 表是否存在**，并对照 prod/test 编排是否含该任务。
- 三表 SR 正式表 **主键与 `ad004aed` 不一致时禁止 ALTER**，须 **DROP + CREATE**；部门周/月现网 0 行可直重建；**产品周等有历史行**（如约 799 行）须先确认**新粒度会清空**，再交运维执行。
- agent-bus：**60s 内 ACK**；若 ACK 被 silent/dedup 丢掉，用 `agent_bus_send.py` **`--no-dedup` 重发**，勿当已 ack；干完再 **reply 结案**。

