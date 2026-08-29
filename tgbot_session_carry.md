# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-29 · 最新归档：`sessions/tg-rotate-2026-08-29-1656.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主人令「不要等狂人点头」：拍板类清库/改口径可先干完，再 bus 回执请他只读复核，不等事前确认
- G5 应用层门禁（service 校验）未落地；API 尚未切概念层读，需更多正式 published 后再切
- 未到打卡窗（如下班 19:00 前）API 会拒；禁止为验通知提前/强制打卡
- [LESSON: agent-bus协作|拍板/清库类任务主人说「不等点头」时：先执行落库，再 bus reply 对齐复核，禁止空等事前确认]
- [LESSON: onehr打卡|「打完卡通知」只加成功/失败后的 TG 私聊；禁止为验通知提前/强制打卡，须等到计划窗内自动跑完]
- 指标库 G2：`ratio` 不在 `default_aggregation` 白名单；derived 比率用分子/分母 FK，`default_aggregation` 留空
- 白名单仍是 `sum` / `count` / `bitmap_union_count` / `max` / `min`
- test 库曾清 12 条 derived 的 `agg=ratio`（含已 published 的 `order_paid_rate`）；清后 G2 缺 FK=0
- 指标库 Phase1（test）结构 v0.3 三表+约束已过关；lifecycle 约 published 10 / draft 260 / orphaned 10
- 10 条 G4 四件套齐全；impl 419、candidate 230、存量 `metric_standard` 264 未动
- 260 条 draft 缺 `definition` + `req_ref`，不能硬推 published，须按事件分批补语义
- 汇报指标库进展：先实查 test 库再答，分「已过关 / 卡点 / 下一步」
- OneHR「加一条打卡通知」= 到点自动打完后再 TG 私聊推时间与成功/失败，不是立刻补打
- 上班卡已打过时不重复打；只保留计划窗内自动跑 + 结果通知
- 狂人 #201 卡点：**数据层**（published=0、G4 空跑），不是 v0.3 结构层；解法是推已齐门禁的样例，不是改表结构。
- 260 条 draft 缺 `definition`/`req_ref`：**禁止**批量改 lifecycle；要上 published 须 P1 补齐再迁。
- 样例推送 SQL：`docs/metric_library_phase1_publish_samples_20260829.sql`；修完 bus 报三数请对方只读重验（#7602 → #7603 PASS）。
- G5 分两层**：库内 `diverged_pending` 且 `is_primary` 违规可为 0；**应用层**门禁（service/router 做 G4/G5 validate）当时**未落地**，勿混为一谈。

