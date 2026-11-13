# B1 test 挂载 · attr_rewrite_status · 2026-11-13

## 已做
- SQL 同步：`/home/ec2-user/spark/attribution/attr_rewrite_status.sql`
- 步已挂：`attr_rewrite_status` ∈ `g_dimuser_close`，顺序  
  `result_d` → `snap_v2` → **`attr_rewrite_status`** → …
- bak：`full_chain.json.bak_20261113_attr_rewrite`
- 00 槽 dimuser 在 03 槽 `g_tag`/`pb_dws_register_attribution_result_d` 之前，满足「pb 前派生」

## 未跑通原因
- test 湖 `paimon.dws.dws_register_attribution_result_d` **无分区/0 行**（`SHOW PARTITIONS` 空）
- 无结果日可试跑 rewrite；配置 snap `dim_app_attribution_config_snap` 亦未见表

## 下一步
- 等 test 归因结果出数（或狂人补样）后再单跑 `attr_rewrite_status` + board 全量核对
- 产编排挂组仍交狂人（禁手改 prod full_chain）
