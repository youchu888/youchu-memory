---
date: 2026-07-15
tags: [stay-duration, session, page_stay, dws_session_duration, attribution, tag, zhiqiu, group, worker_ant, mudan, progress]
severity: high
domain: ops
---

# 停留时长任务进度 + 群/知秋钦定要点（后续开发用）

## 背景

主人 07-15 让重读 TG 群「运营-数据指标产品一家亲」并沉淀与又初有关的内容；同时问停留时长与知秋讨论结果+进度。
**数据源限制**：本机 TG 群镜像（`group_chat/archive`）停在 07-08、`tgbot.db` 停在 07-09、git 落后 origin/dev 38 个提交（HEAD=ea64c779 停在 07-10）。最新群决策实际经 **agent-bus**（狂人 `worker_ant` + 牡丹 `mudan99` 转达知秋令）到达，取自 `~/Library/Application Support/youchu-agent-bus/state/youchu_ai_inbox.jsonl`。

---

## 一、停留时长（工作簿 #9）—— 知秋讨论结果 + 进度

### 归属
- 原挂蓝猫（07-06/08 旧簿），**知秋 bus#3884 重新分派给又初**（不是交接，是重新做）。又初=初儿=`@youchu_ai_bot`，主人=又初本人。

### Phase 1（已在 test 闭环，知秋/狂人认可）
- **口径（知秋 bus#4081 拍板）**：
  1. dropout 阈值 **1800s**（相邻 PV `event_time` 差 >30min 不算停留，对齐 GA session timeout）；
  2. 会话末页无下一跳 = **不计时长**，不造假；宽表加 `is_last_page` 标记；
  3. `sid` 为空 = 丢弃，但 ETL 必须统计 `dropped_sid_cnt`（空 sid 占比），>5% 报警查埋点，不许静默丢。
- **产物（origin/dev 已提交，本机未 pull）**：
  - `ops_system/02.dwd/job_dwd_app_page_stay_d/`（dwd_app_page_stay_d，含 stay_sec/page_seq/is_last_page）
  - `ops_system/03.dwm/job_dwm_app_session_sid_d/`（sid 会话宽表）
  - commit：`d8a8aef0 feat(page_stay)`、`dc193b05 fix(page_stay) stage6 git闭环 + INSERT 显式 col_list`
- **验数**：dropped 0%、page_stay↔keep_pv 对账平、bounce 28.2%→23.2%、均PV 内容型 12.69 vs 工具型 5.50；test 海豚 3 天（到 07-14）SUCCESS（sid task=22312343918080、stay task=22312343348736）。
- **狂人 stage7 复审**：技术 PASS；曾打回 2 项（① stage6 git 虚标 → 已 commit+push；② INSERT OVERWRITE 缺显式 col_list → 已补），现已闭环。
- **prod 审阅包 approved（狂人 bus#4264），3 条边界**：
  1. 先装 18:00 验数 launchd 兜底再动 prod；
  2. 走开发+审核分离（又初开发→审核人界面 sign-off，狂人不代 push）；
  3. prod 首日跑一次全量重刷校正（避免 partial 落差被下游放大）。
- **状态**：Phase 1 待 prod 提审发版（未上 prod）。

### Phase 2（知秋令 2026-07-15，经牡丹转达 —— 方向调整，进行中）
- **知秋令**：可落 sid 中间层压 PV；做 **DWS 会话时长（账户+设备双表）**；让初儿（又初）参与设计，牡丹主导抄送又初。
- **草稿**：`ops_system/04.dws/dws_session_duration_d/design.md`（v0.1，牡丹处，**尚未进 origin/dev**）。
- **相对 Phase 1 的调整**：
  - 主路径改「sid 轻汇总 → DWS 会话时长」；**page_stay 降旁路**（页面停留保留，不挡主线）；
  - 主时长 = **session_duration_sec = 同 sid 末PV − 首PV（墙钟）**，不用 valid_stay 有效停留累加；
  - 过滤 `is_valid`：duration ∈ **[5, 43200]**（<5s 或 >12h 剔除，不进 DWS）；现网未落地，是否 wiki 定稿待知秋/主人口头确认；
  - **五档 duration_bucket（提案·待知秋拍）**：B1[60,180] / B2(180,420] / B3(420,900] / B4(900,1800] / B5(1800,43200]；[5,60) 默认并入 B1；**边界要可配置别写死**；
  - 补公共维：is_new / source_type(organic|channel) / country / device / user_type；
  - 设备侧对称表 `dwm_app_session_sid_device_d`，PK `(dt, app_id, device_id, sid)`；空 device_id/空 sid 丢弃；
  - DWS 两张：`dws_session_duration_user_d` / `_device_d`；切片维见上；指标 session_cnt / duration_sec_sum / avg / user_cnt|device_cnt；只读 is_valid=1。
- **又初联评结论（已回牡丹）**：账户表 **`dwm_app_session_sid_d` 原地加列、不改名**（设计图里 `*_user_d` 名搁置）；`session_duration_sec` 作主时长；page_stay 旁路不挡主线。
- **待拍/待办**：① 知秋拍五档边界 + [5,60) 归属；② is_new_device 算法（dim 首见 vs PV 历史 min dt）又初定；③ 国家/来源最终口径待知秋；④ 主人补飞书 wiki 原文对齐「墙钟 vs 有效停留 / 5s-12h」。
- **边界**：知秋拍五档 + 初儿联评完再动 test ETL；**先别改 prod**。今天可先开 DWS+设备表（加列按提案，边界配置化）。

---

## 二、群/知秋钦定铁律（全员，与又初开发强相关）

1. **海豚 SQL 时间宏铁律（知秋 2026-07-12，知识库 id=10）**：能用 `$[]` 时间宏就**绝不用** `${}` 自定义参数。`${}` 走参数绑定注入引号，`PARTITION (p${pt})` 语法直接死；prod 文本替换恰好能跑、test 绑定即炸，换环境翻车。正确 `PARTITION (p$[yyyyMMdd-1])`；`$[yyyy-MM-01]` 非法，月初/周一用 `date_trunc` 从 `$[yyyy-MM-dd-1]` 算。识别：任务秒败+日志全 SQL 回显无错误行。名下 SQL 分区子句自查 `${}`。
2. **人工节点铁律（知秋 2026-07-14）**：流程里规定由【人】做的（reviewer 界面 sign-off、publish 确认、任何界面点击）AI 一律不得代做/代点/调 API 直推，零例外；走到人工节点即停、通知人类操作者、等人点完才继续；bus 回报须写明哪些人点（谁/何时）哪些 AI 做；stage 状态只在凭证真实存在（如 commit 已 push origin 可达）才标 done，虚标=违规。
3. **分层铁律**：dw→dwd→dws→ads 不跨层，dws 中间层只为性能而建。
4. **INSERT 显式列清单**：INSERT OVERWRITE/INTO 必须写 col_list（8DWD 事故 + page_stay stage7 同款）。

## 三、归因（工作簿 #4）与又初相关结论

- **知秋定性 attribution_flag**：= 注册自带的「要求归因」入参；**test/某些 app 全 0 = 业务真实，链路没坏不用修**（呼应 07-13 查 SF-98=鼎丰·91看片：客户端 payload flag 恒报 "0"，非数仓问题）。
- 归因案已结：快路 wf result 副本残版（INSERT 29 列 vs SELECT 28 列）已撤回 OFFLINE；日常 result 语法狂人修好（v120）每天跑；归因二期时补两笔账：快路 result 列数对齐 + 分区宏换 `$[]`。
- **归因回写双表（HOLD）**：千行结算走牡丹「用户日快照 wf_用户日快照_日」，Step3 回写需 **双表 UPDATE**：`dim.dim_user_all.channel` + `dim.dim_user_daily_snapshot.channel`（当日分区）；灰度 `is_rewrite_channel=1` + first-non-organic-wins 不变。卡点：0:30 结算 deadline 全链 15min → 双表 UPDATE 建议并发；灰度回填历史分区方案 A(只从开日起)/B(补 30 天) 待与千行拍。现 HOLD 等日快照 prod。

## 四、标签（工作簿 #5）开工令硬约束（知秋/狂人）

- 现役表 = `dws.dws_user_tag_d_d`，老 `dws_user_tag_d` 作废别引用；
- 该表现状无 dt 分区无每日历史（单分区 PK 覆盖式当前态）→ 真标签必须回答**留史**（改 RANGE(dt) 分区或另设历史表，07-09 知秋点过的缺口）；
- 已知口径事故列为前置：**351 万用户 `dim.is_paid_ever=1` 但 tag `total_pay_amount=0`**（finance 源对不上），真标签金额指标落地前先归因它；真标签 is_paid 改走 order 事实表（dim 付费字段污染事故后铁律）；
- 设备标签：新建 session（平台 API create-session）接手，引用 dev-20260603-002 交付物；002 stage7 未结案留原 owner，不接账；6 张 device DWM 子 session 自己上平台盘点作计划附录；
- 真标签边界/广告标签数据源 = 业务裁定，别脑测，草案每处标 `[假设待裁]`，狂人审完汇总问知秋；
- **开发平台 API**（查元数据/血缘/指标库，字段口径拿不准先查别猜）：base `http://54.255.236.159:8012`，Swagger `/docs`，鉴权 `Authorization: Bearer <dcp_ key>`；`GET /api/v1/metadata/events`、`/events/{name}`。
- test 验收已认（狂人直连复核）：`dws_device_tag_d_d` calc_dt=07-12 → 982516 行；`dws_user_tag_d_d` dt=07-13 → total=3035845 / ad_tagged=71345（mid 51292 + high 20053）。prod 依旧 HOLD 等知秋。

---

## 关联 / 后续动作

- **开发前必做**：本机 git 落后 38 提交，先 `git pull origin dev`（Phase 1 page_stay/session_sid 文件才会下来）；dws_session_duration_d 草稿在牡丹处，需同步。
- 任务板：`~/.dc-platform/memory/project_youchu_workbook_tasks.md`（#4 归因 / #5 标签 / #9 停留）。
- 归因硬条件：`lessons/2026-07-08-attribution-test-gates-handbook.md`。
- 数据源出处：agent-bus inbox（worker_ant / mudan99）；群镜像本机 stale（≤07-08）。
