# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-19 · 最新归档：`sessions/tg-rotate-2026-08-19-0632.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 对外回复（私聊/Cursor）禁止用「主人」等称呼；直接说事，用「你」，少汇报腔、少旁白体
- 内部规则/记忆文档可保留「主人」作决策出处记录，但**对外输出必须剥离**
- 日报标准链路：双机各自写 work-log → memory git 同步 → 读合并稿 + `hosts/new-mac|old-mac` → 扫当日 transcript/派单去重 → old-mac 推 TG；**禁止跳过同步直接写稿**
- 用户给出定稿正文并说「上传云端」：以用户正文**原封不动**落本地并上传，禁止擅自改写后再传
- [LESSON: daily-report|写/推日报前必须先跑双机 work-log 同步并读合并稿，禁止仅靠 transcript 在同步完成前定稿]
- [LESSON: communication|对外回复禁用「主人」，用「你」直说；内部记忆可留出处词，输出必须剥离]
- 定时推送（如 21:35）若早于双机同步完成，会产出「不完整双机汇总」；new-mac 晚间实活若未进 work-log，只能靠 transcript 补，不算规范版
- 实活做完应**及时写入可同步的 work-log**（尤其 new-mac），不能等 21:20 flush 兜底或日报推送后再补
- 被质疑日报是否多设备汇总时，应如实核对时点：work-log 是否齐、同步何时完成、推送是否早于合并稿
- 用户要求「重新整理日报」：先跑双机同步，再以合并稿 + 全量私聊/派单为准重写，并推 TG **覆盖**旧版
- 日报正文归因用**知秋**等人名，不用机器人名（狂人/worker_ant）；也不写「按主人要求」
- 停留时长对外回执：不能把「生产有分区」当「已完成」；有效会话规则（已确认）与离开埋点（待产品答复）须分层写清，工作簿保持 HOLD
- 指标库 v0.2 改稿要点：标签唯一约束、同名指标消歧；又初侧未动测试建表时要在日报里写清边界
- 大漏斗 test 宽表：18 事件 × 用户/会话/次数三类计数 = 54 列；建表完成≠可写入，待接日批/补数验证
- 狂人 bus#6676 U1~U7 评审结论：三层 concept/label/implementation 方向对；staging + 5 条门禁可挡 U5；**MySQL 8 无部分索引时用生成列 NULL 不参与唯一**（`primary_slot`/`biz_term_key`）实现条件唯一
- 设计稿补充铁律：`orphaned` 仅 implementation 层派生禁双写；G6 复核队列 + `v_metric_impl_candidate_rejected_review`；**granularity 是 concept 固有属性**；`diverged_since`/`diverged_owner` + 7 工作日 SLA
- [LESSON: metric-library|DDL 评审后改稿 push 不等于建表；Phase0 test DDL 须等 5 条拍板 + 知秋别名真源/lifecycle 两项，禁止抢跑]
- 指标库分「概念设计 v0.2」与「现网 metadata 存量」两条线；设计交付 ≠ 可发布口径库，264 条存量仍处止血态治理阶段

