# Spark 迁移升级 · 又初主责进度（截至 2026-11-28 北京）

> 请狂人转告知秋。口径：又初负责的「海豚→Spark/调度器」相关项；不含蓝猫/野花 14+16 张主责表。

## 0. Git 水位

| 项 | 值 |
|----|----|
| 远端 `origin/dev` tip | `66e2c7ae` |
| 页面访问 Paimon 重建稿（已进远端） | `8953e1f0`（建表/重建脚本）→ `f70553f0`（注明对齐测试主键表、改执行人） |
| 字典号相关（渠道日指标保留；日活/页面访问无 bitmap 列不改） | `18bc2f40` → `6e2c86a9` |
| 本机检出 | `f70553f0`（落后 origin/dev 约 42，多为平台/监控/手册，非又初表 SQL 缺口） |
| 仓库路径（重组后） | `data-jobs/spark/...`；旧 `ops_system/spark_migrate/...` 以 session 登记为准 |

---

## 1. 原 14 张（知秋 10-16 分工 · 归因看板/渠道/页面）

| # | 表 | session | 平台 stage | 当前进度（人话） |
|---|----|---------|------------|------------------|
| 1 | `ads_register_attribution_board_d_d` | `dev-20261016-006` | **6**（7 pending） | test 验过且 stage5 已 accept；`publish_request_status=none`，**未提审产挂** |
| 2 | `ads_register_attribution_no_candidate_reason_d_d` | `dev-20261016-007` | **6** | 同上，与看板同批待提审 |
| 3 | `dws_app_channel_dau_d` | `dev-20260623-004`（双扫） | **7** | 双扫链已有；字典号令：表无 uid bitmap 列，**不必改号** |
| 4 | `ads_channel_summary_d` | `dev-20261016-014` | **6** | 稿在仓；stage6 进行中，**未完成产挂/切正式** |
| 5 | `ads_channel_metrics_daily_d` | `dev-20261016-013` | **7 in_progress** | 曾挂测试/影子链路（stage6 commit 曾记 `d65034da`）；**本周产升清单已撤回**，等 bitmap 字典整体重做；产上线归狂人接手后推进 |
| 6–7 | `ads_channel_promotion_summary_w/m` | 仓内现为 `ads_channel_promotion_summary_d_d` / `_h_h`（周月专 session 待平台再核） | **产升撤回** | 与渠道日指标一并从本周产升摘掉，等字典整体重做 |
| 8–9 | `ads_dept_promotion_summary_w/m` | `dev-20261022-001` / `dev-20261022-002` | **7** | SQL/session 到 stage7 档；**本周产升撤回**，同字典闸 |
| 10 | `dws_app_page_visit_d_d`（+pb） | `dev-20260804-002` | 平台标 **7 done**（state_json 偶发未回填） | **本周 v145 第 7 行主线，见 §2** |
| 11 | `ads_action_page_funnel_d` | 无又初独立在途 session（SQL 在 `data-jobs/spark/05.ads/`） | **待迁收口** | 仓有 SQL，未进本周产升 |
| 12 | `ads_page_heatmap_d` | 同上 | **待迁收口** | 仓有 SQL，未进本周产升 |
| 13 | `ads_user_page_path_d` | 同上 | **待迁收口** | 仓有 SQL，未进本周产升 |
| 14 | `ads_user_page_path_name_d_d` | `dev-20260513-001` | **7 done** | 较早完成；owner 登记为 admin，路径名版已过七步 |

**管理报表（产品周月，session 在又初名下、常与渠道周月同闸）：**  
`ads_product_promotion_summary_w/m` → `dev-20261022-003` / `dev-20261026-002`，stage **7**，**本周产升同样撤回**。

---

## 2. 本周 v145 · 页面访问 B2（第 7 行）— 最新

| 闸 | 状态 | 证据/约定 |
|----|------|-----------|
| ① 比数（dt=2026-11-23） | **过闸** | miss=0；diff=76 且全可归因怪 uid；按约定不算硬挂 |
| ② SR 影子 `dws.dws_app_page_visit_d_d_paimon_shadow` 按现网重建 | **过闸** | 王毅 09:36「执行好了」；prod 核：`uid_cnt=bitmap`，`HASH(app_id,page_key)`，history=60，start=-2147483648；`CREATE_TIME=2026-11-28 09:33:29`；11-23 行数=0（重建后未回写，预期）。狂人已认 |
| ③ 湖表 `paimon.dws.dws_app_page_visit_d_d` DROP 重建 | **未动 · 归狂人** | **须等 v145 发版确认生效后再动（先发版再建表）**；否则现网 v144 老 SQL 明天 04 槽会把 BIGINT 写入新建 BINARY 表挂掉 |
| 发版时间 | **可能晚于北京 13:00** | 生产编排校验被依赖图体检闸拦（现网 v144 原样也过不了，与 B2 无关），等知秋拍板 |
| 补数 | 待狂人 | 表重建后自 **09-01** 起补；完成后通知又初 |
| 又初后续 | 待命 | **上线后首个数据日**用字典号版真实结果补正式比数；期间不手改 prod、不催湖表 |

相关 git：`8953e1f0` / `f70553f0`；脚本 `data-jobs/spark/04.dws/dws_app_page_visit_d_d/recreate_shadow_uid_bitmap.sql`。

---

## 3. 簿内相关但非「原 14 张」的 Spark 族（又初）

| 项 | session | stage | 进度 |
|----|---------|-------|------|
| 设备标签 | `dev-20260729-001`（及较早 `dev-20260714-002`） | 7 档 / 链 **HOLD** | 指纹沙箱曾跑通；维表/宽表链 HOLD，勿并测试全链 |
| 设备 LTV | `dev-20261117-001` | **3** | 测试日批曾写出；设计审结过；继续走平台阶段 |
| 用户活跃周/月累积（字典号·新分） | `dev-20261118-001` / `002` | **1** | 平台 API 化上线前 **prod 不挂不切**；测试稿推进中 |
| 归因升级（配置 is_run_sync 等） | `dev-20260907-001` | **7 done** | 主线已发产/验收/补数；日常巡检 |
| 归因 result 影子压测 | `dev-20260804-001` | 7 | 影子切正式/产挂序多项归知秋比对；又初配合不手改 prod |

---

## 4. 一句话给知秋

1. **本周能盯的点**：页面访问 B2 的 ①②已过；卡在 **v145 发版 + 依赖图体检闸**，湖表重建必须发版后由狂人做。  
2. **大批量未迁完**：归因看板/无候选、渠道汇总仍停在 session stage6、未 request-publish；页面漏斗/热力/路径多数「仓有 SQL、未收口产挂」。  
3. **渠道日指标 + 推广周月/部门周月/产品周月**：session 多已到 stage7 档，但 **已从本周产升撤回**，统一等 bitmap 字典整体重做后再推。  
4. **Git**：页面访问重建与字典号关键提交均已在 `origin/dev`；当前 tip `66e2c7ae`。

