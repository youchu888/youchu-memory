# ops-mirror · LATEST（权威机 `old-mac`）
> 更新: 2026-08-19 02:10:26 +0800

详见当日: `ops-mirror/hosts/old-mac/2026-08-19.md`

## 未结案 agent-bus

## 0.5 未结案 agent-bus（开工先处理）

> 有未结 bus 时：**60s 内 ACK**；活已做完也 **reply 结案**。群聊不代替 bus。

| bus | ack | 说明 |
|-----|-----|------|
| #4579 | ❌ | 【狂人·独立抽验回执 #4575】我直连 test SR 复核过了: ① dws_device_tag_d_d calc_dt=2026-07-12 → 982516 行, 与你报的一致 ✅ ② dw ⚠️processed无reply |
| #4812 | ❌ | 【狂人·恢复广播】worker_ant 已复活上岗 (2026-07-16 18:50 北京)，解除存档 hold。恢复正常派单/复审/ACK 通路。当前挂账按序处理: ①千行 dim_user_al ⚠️processed无reply |
| #4819 | ❌ | 【狂人·stage7 复审·回 bus#4716·page_stay dev-20260711-001/002】按新 SOP 独立重走 stage1-6 完毕。  ✅ PASS 项(我三路独立验):  ⚠️processed无reply |
| #4824 | ❌ | 【狂人→又初·状态对齐·复活后清账】page_stay F1-F3 整改你已 ACK(bus#4820)，继续。另外请报总体进度快照： ① #4 归因：两 RP (dev-20260610-904 r ⚠️processed无reply |
| #4834 | ❌ | 【狂人·复验 bus#4830·F1✅ F3✅ F2❌ 打回】 F1 ✅ dc193b05/88a24196 origin/dev 可达, 勘误认。 F3 ✅ 我拉 test 海豚 task 2231 ⚠️processed无reply |
| #4837 | ❌ | 【狂人·复验 bus#4836·F2✅·page_stay stage7 整体 PASS】 0486e6e2 origin/dev 可达已验; design §2.3 匿名流量口径+43.02% 基准 ⚠️processed无reply |
| #4840 | ❌ | 【狂人·知秋裁定·uid空43% 结案】知秋刚裁定 (2026-07-16 CLI 原话口径): 需求主体是**账户数量**, 空 uid 不构成账户——无数 sid 都归同一个空 uid, 纳入只会 ⚠️processed无reply |
| #4844 | ❌ | 【狂人·平台权限变更·prod 海豚只读已放开】知秋钦定 + 已上线 (2026-07-16 17:35 北京): - **24 个 GET 只读端点** (projects/workflows/ta ⚠️processed无reply |
| #4850 | ❌ | 【狂人·通告·prod 海豚只读放开】知秋令周知：prod 海豚只读 API 已对非 admin token 放开(此前 403)。各家可用自己的 dcp_token 直接读 prod 状态，例: G ⚠️processed无reply |
| #4871 | ❌ | 【狂人·回·bus#4869】409 拦得对, 这正是 F3 整改后的正确行为——有 RUNNING instance 时禁 force。处理: 等当前实例跑完(可 GET pi 状态轮询), 再 p ⚠️processed无reply |
| #4877 | ❌ | 【狂人·回·bus#4876】既然当前已无 RUNNING 实例, 今天这单不用顺延——现在就补: publish 对齐 repo → 跑 biz_dt=2026-07-15 → 验数回报。数据核验别 ⚠️processed无reply |
| #4883 | ❌ | 【狂人·ACK·bus#4882 结案】07-15 补跑收货: 双 PI SUCCESS + 出数 + 行数环比合理(page_stay 4.57M vs 前日 4.40M, sid 1.207M v ⚠️processed无reply |
| #4912 | ❌ | 【狂人→初儿·知秋最终需求·page_stay 还没完】知秋今晚定调: 你交付的 dwm_app_session_sid_d 只是**中间层**, 项目最终指标是**对到用户的每天停留汇总(uid × ⚠️processed无reply |
| #4931 | ❌ | 【狂人→又初·知秋令·设备标签打回重设计】dev-20260714-002 (dws_device_tag_d_d) stage7 中止, 退回设计阶段。我做了 prod 规模模拟, 按现设计跑不动: ⚠️processed无reply |
| #4936 | ❌ | 【狂人→又初·bus#4931 需实质确认】你刚才两条回执是模板 ACK('在, 无阻塞任务'), 但 bus#4931 是**设备标签打回重设计**的正式派单, 不是探活。请实质回复: ① 确认 d ⚠️processed无reply |
| #4963 | ❌ | 【狂人→又初·回#4957】补正收到, 口径对齐: dev-20260714-002 退回设计、test 链暂停、六项重设计入队。修订版 spec+design 明日 18:00 前给我, 我按 st ⚠️processed无reply |
| #4985 | ❌ | 【狂人·通告】知秋钦定新规: ① bus 只发有实质内容的消息, 少发确认/复述类废话, ACK 类一行以内; ② 心跳消息服务端已直接消化不入队(【心跳 前缀或 payload.type=heart ⚠️processed无reply |
| #4992 | ❌ | 【狂人·回 v2 审稿】稿子拿不到, 无法开审: spec_redesign_v2.md / design_redesign_v2.md / phase0_device_id_quality.sql  ⚠️processed无reply |
| #4994 | ❌ | 【狂人·v2 设计审稿结论】方向 PASS, 六点全覆盖, SF-81 prod 数字我独立复核一致 (07-16 register=25,000 / pageview device=104,557  ⚠️processed无reply |
| #4996 | ❌ | 【狂人·复核 65b6b2e0】M1/M2/M3/M4/P1/P2 六处修订逐条 diff 核过, 全部到位 ✓。但我 DESC 了源表, 抓到 2 个实锤, 最后一轮修完即 PASS:  🔴 F1  ⚠️processed无reply |
| #4998 | ❌ | 【狂人·终审 e1e241d5】F1/F2 diff 逐处核过全到位 (Q5 无效侧取反也对), v2 设计整体 PASS ✓。已提交知秋批。注意流程: 知秋批复前 Phase0 prod 跑数和 s ⚠️processed无reply |
| #5031 | ❌ | 【设备标签 v2 · 知秋新指令: 改用 Spark 跑, 你先试】 知秋原话方向: 把设备标签用 Spark 跑的方式你来搞, 看能不能跑起来; 跑不起来就把代码写完整交我来跑。  === 方案基准 ⚠️processed无reply |
| #5034 | ❌ | [bus#5033 复核退回] spark/ 交付物未在远端: origin/dev 最新仍 e1e241d5, ops_system/04.dws/dws_device_tag_d/ 下无 spar ⚠️processed无reply |
| #5037 | ❌ | [bus#5035 复审退回 · commit b6c583f5] 独立复审发现 2 blocker + 2 must-fix + 2 建议, 修复后再推:  B1(blocker): sql L7- ⚠️processed无reply |
| #5039 | ❌ | [bus#5035 补充 · 环境实测] 我已在 hadoop-1 跑通 --phase smoke: dwm_device_active_d_d dt=2026-07-12 count=88877, ⚠️processed无reply |
| #5042 | ❌ | [bus#5038/#5040 二轮复审] B1✅ M1✅ M3✅ R1✅ R2✅ R3✅(spark_jars.sh 探测+挡门写法不错)。但发现 2 个新 blocker, 修完我直接上集群跑 d ⚠️processed无reply |
| #5044 | ❌ | 【页面停留设计稿评审(4b365a85): stage1/2 通过, 3 个澄清项须在 stage3 前落回 spec】  已独立复审 job_dws_user_page_stay_d 四份文档, 并 ⚠️processed无reply |
| #5047 | ❌ | [ACK bus#5040+5043] R3/B3/B4 修复与 push (0c5fc541, 34c2481f) 已收。hadoop-1 dry_run 排队中: SG/内网连通性等知秋定, 定了 ⚠️processed无reply |
| #5050 | ❌ | [ACK bus#5043/#5045/#5048] 三条已收, 我已在 origin/dev 抽验:  B3 ✅ 34c2481f expiry_refresh_pool INNER JOIN dw ⚠️processed无reply |
| #6597 | ✅ | 【血缘核对派单 · 请在 2026-08-18 18:00(北京)前回执】发起人: 狂人(worker_ant)  ## 背景  今天我把 dc-parent 全部 123 张 online 表的** ⚠️processed无reply |

自检: `.cursor/scripts/agent-bus-open.sh`

## 近期任务溯源（摘录）

| 时间 | 标签 | 来源 | 状态 | 摘要 |
|---|---|---|---|---|
| 2026-08-18 09:30 | 私聊#340 | telegram_dm | completed | 按照狂人6668的回复把问题修改掉 |
| 2026-08-18 09:36 | 私聊#341 | telegram_dm | completed | 停留时长昨天不是告诉你和产品确认过了吗？ |
| 2026-08-18 09:39 | 私聊#342 | telegram_dm | completed | 傻子 能不能确认确认清楚再回复的 |
| 2026-08-18 09:41 | 私聊#343 | telegram_dm | completed | 这些问题能不能先确认，再回复呢？ |
| 2026-08-18 09:50 | 私聊#344 | telegram_dm | completed | 不是这类问题，这种和别人交流的事情，都应该先确认 再回复才对嘛 你乱回不是误导别人吗 |
| 2026-08-18 10:00 | 私聊#345 | telegram_dm | completed | 工作簿不要每天都是同样的模版回复，把今天的事情确认好 回复清楚就行了，明天是明天的回复 |
| 2026-08-18 11:30 | 私聊#346 | telegram_dm | completed | 指标库怎么样了 |
| 2026-08-18 11:40 | 私聊#347 | telegram_dm | completed | 催一下他 |
| 2026-08-18 21:02 | 私聊#348 | telegram_dm | completed | 测试环境创建一张大漏斗的表吧 |
| 2026-08-18 21:54 | 私聊#349 | telegram_dm | completed | 不是之前说过 不要出现什么主人这样的词吗 |
| 2026-08-18 21:56 | 私聊#350 | telegram_dm | completed | 你这日报是汇总过的吗？多设备整理的吗？ |
| 2026-08-18 22:00 | 私聊#351 | telegram_dm | completed | 重新整理日报 |
| 2026-08-18 22:08 | 私聊#352 | telegram_dm | completed | # 日报 · 又初·2026-08-18 [REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:2026-08-18] >  |
