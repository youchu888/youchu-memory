# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-01 · 最新归档：`sessions/tg-rotate-2026-09-01-1843.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 沙箱 explain：**材料 push 完 → 交狂人 review → 收到 PASS 再跑**；未审过禁止先 SSH 试跑。
- 任务进入「等审/已交材料」后必须立刻取消后续定时进度推送**；只在有 PASS/打回或状态变更时主动通知，禁止 13/15/17/19 式刷屏。
- [LESSON: tg-progress|agent-bus-review|wait-state|任务已交审或进入等 PASS 状态时，立即取消所有定时进度提醒；仅在审结、打回或需拍板时再私聊通知]
- [LESSON: uid_map|device-fingerprint|_r-retention|四路 `_r` 保留期不一致时，禁止用统一全表扫描默认「生涯首次/换号」语义；须显式分路定义或统一窗口，并在方案/SQL 注释写死字段含义]
- 设备标签 v2：主键改 `device_fingerprint`；顺序固定为 **先 `dwm_device_uid_map_d` → 再 dim / 六张 dwm / `dws_device_tag_d_d`**，审过前下游一律 HOLD。
- dim 活跃宇宙拍板 **选项 C**：login/page_view `_r` 只认近约 50 天；07-13 前沉默设备不进 dim（`last_login_time` / `last_active_time` 相关逻辑按此收敛）。
- 等审期间可并行其他线（如指标库 Phase1），但 Spark/uid_map 相关改动仍须等审结，有卡点再私聊拍板。
- **任务进入「等审/已交材料」后必须立刻取消后续定时进度推送**；只在有 PASS/打回或状态变更时主动通知，禁止 13/15/17/19 式刷屏。
- 指标库 Phase1 存量迁移：`req_ref` 可用过渡前缀 **`legacy:metric_standard/<base_name>`**；有真实 PRD/session 后再替换，不动已 published 口径。
- **`diverged_pending` 一律 HOLD**：可 enrich（definition/entity/event），**不升 published**；等口径对齐或 P2 消歧后再推。
- 指标库 draft→published 推荐批次：**order → user_register+user_login → ad → app_page_view+session → video 单独批 → other 先归类再推**；retention 量小不优先。
- 页面访问类指标 **entity 对齐 `event_ext` 用 `user`**，不能用 `page`/`landing_page`（会撞 FK）。
- Spark 指纹改造催审重点：**bus#7756 / #7760**，仓库 commit **`2f95e122`**；背景规则见 **#7735 / #7738**。
- bus#7778 新阻断：四路 `_r` **保留期不齐**（register/order ~243 天 vs login/page_view ~50 天）；写法层已过，卡在 **uid_map 全表重算时字段语义混用两种历史窗口**。
- **dim 选项 C ≠ uid_map 字段定义**：C 管「谁进 dim」；uid_map 的 `first_uid`/`uid_cnt`/`last_uid_dt` 须单独定案，不能靠 `WHERE dt <= '${DT}'` 四路 UNION 默认拼成「真全史首次」。
- prod 盯盘口径是**告警驱动**，不是又初另起一套夜间全量巡检；检测已在 `server_monitor`（54.255.236.159），禁止再造监控
- 长任务按主人要求**定时私聊汇报**；卡点一次性列清选项私聊拍板，不要边做边猜
- [LESSON: device-fingerprint|设备标签/uid_map 主键用 device_fingerprint，无指纹丢弃；改造顺序 uid_map→dim/dwm/dws，以 bus#7738 覆盖旧 prod 禁令]

