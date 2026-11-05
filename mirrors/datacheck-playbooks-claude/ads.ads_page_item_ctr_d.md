# 核查剧本 · ads.ads_page_item_ctr_d

## part_01 分区非空
业务日分区行数 > 0。

## part_02 只有曝光也有行
存在 click_cnt=0 且 exposure_cnt>0 的行。

## part_03 两边都没有不落行
不存在 click_cnt=0 且 exposure_cnt=0 的行。

## part_04 次数抽样
对单 app/page/item，曝光、点击次数与明细 COUNT(*) 一致。
对照窗口：业务日 `event_time` 当天 + 次日 03:00 前到达；与两张 dwd_r（`dwd_app_pageitem_exposure_d_r` / `dwd_app_pageitem_click_d_r`）按同窗口直数对平。

## part_05 有点击无曝光键占比（影子期日监控）
口径：同一业务日聚合键上 `click_cnt>0 AND exposure_cnt=0` 的键数 / 当日总键数。
- **非阻断**：ETL FULL OUTER JOIN 允许有点击无曝光落行；业务问「CTR>1 / 无曝光点击」时以此说明，不是脏数。
- **影子期动作**：每天记该比例，观察是否稳定；比例突变再排查 fanout/迟到/解析。
- **基线（prod 只读 · 数据日 2026-11-04 · bus#12440）**：总键 156,440；有点击无曝光 36,774（约 **23.5%**）。

## stage 4 验证记录 · 2026-10-20

- 环境：test；数据日 2026-10-19；组 `g_page_item_ctr` 槽 11
- part_01：`ads.ads_page_item_ctr_d` 436 行 PASS
- part_02：exposure_only=301 PASS
- part_03：both_zero=0 PASS
- part_04：S5 对照生产明细再做（本次 S4 只验跑通回写）
- 单跑/补数：四步 SUCCESS；Paimon/SR 同源 436 行


## stage 5 验证记录 · 2026-10-20

- 结果：**WARN**（新表，生产尚无目标表；验证环境也无产出可对）
- prod SR：`ads.ads_page_item_ctr_d` / `dim.dim_app_page_item_d` 不存在
- prod Paimon：同上，TABLE_OR_VIEW_NOT_FOUND
- 上游 `dw.dw_user_event_detail_new`：存在，字段含 event / event_time / app_id / payload — PASS
- 对数：SKIP（无生产/验证目标数据）；S4 test T-1 已有 436 行跑通
- 未做：verify 送 SQL / 挂 prod 编排（写闸期；本会话仅结构 WARN 收口）

## stage 审回改 · 2026-10-24（bus#11375）

- 去掉表内 `ctr`（表不存比率）；Paimon rebuild；test SR `ALTER DROP COLUMN ctr`
- test 近 3 天 SR/Paimon 行数：`2026-10-21`=1587，`2026-10-22`=1520，`2026-10-23`=1806
- S5 verify 数据日 `2026-10-23`：`test.ads.ads_page_item_ctr_d` rows=106995，exposure_sum=13508036，click_sum=1766525
- 上游 prod `dw.dw_user_event_detail_new` 同口径：exposure=13508036，click=1766525（对得上）
- **先别提发布**

## 变更 · 2026-11-03 bus#12164

- 上游改为 `dwd.dwd_app_pageitem_d_r`（禁直读 dw）；part_04 对明细改为对 dwd_r 去重后行数
- 核查对象改为 SR 影子：`ads.ads_page_item_ctr_d_paimon_shadow` / `dim.dim_app_page_item_d_paimon_shadow`
- 正式表今日不发、不对正式做验收；影子连续 7 数据日对平后再谈切流

## 变更 · 2026-11-03 bus#12191

- dwd_r 必须是 first-row 主键表；日批灌数 SQL 已删；唯一写入=fanout
- ads/dim 探 dwd_r watermark，避免只读 DT 分区漏掉次日 03:00 前迟到
- 曾用日批实跑：曝光+点击=分区总行，证明迟到未进——回归时以此为反例

## 变更 · 2026-11-04 拆表

- 作废合表 `dwd_app_pageitem_d_r`；改为 `dwd_app_pageitem_exposure_d_r`（bucket=8/par=4）+ `dwd_app_pageitem_click_d_r`（bucket=2/par=2）
- ads/dim UNION 两表；探针两表 watermark 均 until 03:00
- part_04 对明细改为分别对两张 `_r` 去重后行数

## 变更 · 2026-11-05 bus#12440（回 #12439）

- 狂人审过 `ops_system/spark_migrate/ads_page_item_ctr_d`：**可发影子**；已派**野花只发 prod 影子**（不发正式表）。
- prod 只读核验 · 数据日 **2026-11-04** · `ads_page_item_ctr_d.sql` 原逻辑：
  - ads 聚合 **156,440** 键；SUM 曝光 **76,251,917** / 点击 **4,606,580**，与两张 dwd_r 同窗口（event_time 当天 + 次日 03:00 前到达）直数逐位相等 → **part_04 PASS**
  - 字段最大长度 app_id 9 / page_key 25 / item_id 51 / page_name 27 / item_name 150，无超 SR 列宽
  - 有点击无曝光键 36,774（约 23%）→ 记入 **part_05**，影子期每日盯比例
- **闸门不变**：影子连续 **7** 个数据日核平后再谈正式表。

