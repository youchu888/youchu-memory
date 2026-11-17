# 运维事实

群/私聊里「谁对哪张表或哪份 SQL 做了执行」的短事实（建表、重建、DROP、生产执行回执）。
闲聊不进。问「谁重建的 / 谁执行的」时先查本文件，再翻 `learn/` / `archive/`。
每晚 `daily_group_chat_learn.py` 自动追加；人工核实的也可直接补一行。

## 人员速查

| 称呼 / TG | 角色 | 备注 |
|-----------|------|------|
| 王毅 / @wangyi00001 | 大数据运维 | prod/test SR 建表、重建、节点与权限类执行 |
| 希安 / @jiangyan0803 | （群里偶发点名生产执行） | 以当日消息为准 |

## 事实清单

- 2026-08-21 | 私聊 | 执行回执 | 表 dws.dws_app_page_visit_d_d | 用户确认「执行好了」——当日为扩历史分区 ALTER；随后又初继续 prod 补数
- 2026-11-12 | 私聊/bus | 运维已执行 | 表 dws.dws_register_attribution_result_d_paimon_shadow | ALTER 六句（补 rewrite 相关列）运维已跑完；狂人 SHOW COLUMNS 核过 35 列
- 2026-11-17 | 核对补记 | 执行人=运维王毅（@wangyi00001） | 表 dws.dws_app_page_visit_d_d（SR 影子） | B2：uid_cnt bigint→BITMAP，按 `recreate_shadow_uid_bitmap.sql` DROP/CREATE；又初出工单+只读核验，不手改 prod
- 2026-11-16 | 大数据运维群（主人↔王毅互@）+ 私聊收口 | 执行人=王毅 @wangyi00001 | 表 dws.dws_app_page_visit_d_d_paimon_shadow | 跑 recreate_shadow_uid_bitmap.sql（uid_cnt bigint→BITMAP）；主人确认群内互@派执行；19:57 私聊「已经改好了，bitmap」；又初只读 SHOW COLUMNS 核过。问谁重建以此为准，勿写成「对不上是谁」。
