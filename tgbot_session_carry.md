# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-04 · 最新归档：`sessions/tg-rotate-2026-11-04-0601.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- prod 影子表未建时**：首跑 HDFS 标记、行数**现在不能当验收报**；test 影子 T-1 可有数、prod 影子可为 0，结论写进 reply 并等野花审发建表挂载后再补报。
- [LESSON: paimon_shadow|prod 影子物理表未建/未挂载前，禁止把首跑标记与 prod 行数当闭环验收，reply 里写清阻塞项]
- **归因前渠道**：取事件/注册 DWD 自带 `channel`（上报清洗码），**不是** `dim.dim_user_all.channel`（用户级、可归因后回写）。
- **常用归因前来源**：注册 `dwd.dwd_user_register_d_v2.channel`；浏览拆渠道 `dwd.dwd_app_page_view_d.channel`；更底层 `dw.dw_user_event_detail` / `_new.channel`。
- **按 app+渠道看日活**：无现成汇总表；`dwm.dwm_app_active_user_d` **无 channel 列**，需从注册 DWD ∪ 浏览 DWD 自行汇总。
- **渠道产品周/月**（`ads.ads_product_promotion_summary_w` / `_m`）：表内**无 channel**，粒度是 **部门 × 产品**，与「归因前事件 channel」是不同问题，先对齐业务对象再答。
- **产品周/月渠道链路**：上游 `ads.ads_channel_metrics_daily_d`（app_id + channel）→ JOIN `dim.dim_channel_info_all.channel_code` 得 `dept_id/dept_name`；维表对不上的渠道**不进**产品周/月。
- **渠道日表 channel 口径**：有 uid 的指标（注册/活跃/充值等）用 **`dim.dim_user_all.channel`**；无 uid（如落地页）才用事件自带 channel。
- **生产 Paimon 影子发布（bus#12214 类）**：A+B 七张可跟野花发生产影子，**只回写 `*_paimon_shadow`，正式表不动**；002 不发。
- **009/010/011/012/019 核查约定**：只读 `dt=DT`；010/011 的 `event_time` 仅路径排序，**不按 event_time 截天**；`time_basis=到达`、槽 **02**。
- **013 渠道日指标**：`snap_dt=DT` 写死；分区闸 `partition = '[${DT}]'`（生产实测格式如 `[2026-11-02]`，需在 `dim_user_snap$partitions` 能命中）。
- **提审前**：七 session 须齐 **stage 五件产物**（strict_mode / owner_boundary / stage4~6 等），再 `request-publish` 给野花；`rel_dir`、`project_id` 与 `origin/dev` 指定 commit 对齐。
- **prod 影子表未建时**：首跑 HDFS 标记、行数**现在不能当验收报**；test 影子 T-1 可有数、prod 影子可为 0，结论写进 reply 并等野花审发建表挂载后再补报。
- **agent-bus**：60s 内 ack、干完再 reply 才结案；ack 若返回 `dropped: silent` 仍要核对发送/落盘状态，避免误以为未发出。
- 临发布被拦**：先写清现状（session 阶段、源表/事件、目标表、是否影子/对平），**bus 狂人拍板**，勿自行改 `pb_*` 或硬提审。
- 须狂人定的四项**：是否必须先挂影子、影子/正式表名、当日能否发、是否立刻改 `pb_*`；回执后再改稿或继续 Stage7。
- [LESSON: dev-session|agent-bus|临发布] 野花指「不符合狂人规则」且当日要发：汇总口径与表结构 → bus 狂人 → 收到表名/影子/能否发后再动 SQL 或提审，禁止未拍板就改 pb 或 request-publish。]
- **页面点击率**链路：`dev-20261020-002`，Stage1–6 已完、Stage7 待审；产表**尚未建、未发过**，当日仍有机会改口径再首发。

