# bus#13228 · test 推进状态 · 2026-11-13

## 已完成（test）

| 项 | 状态 | 证据 |
|---|---|---|
| B2 page_visit 字典号+停留 | PASS | ETL/pb OK；FULL JOIN 见 `dws.dws_app_page_visit_d_d/validate__2026-11-12__test_b2_fulljoin.md` |
| A1 channel_summary 换留存源 | 可跑、对账未平（换源预期） | `ads.ads_channel_summary_d/validate__2026-11-12__test_a1_fulljoin.md` |
| A7 no_candidate | PASS 对齐正式 | `ads...no_candidate.../validate__2026-11-12__test_a7.md` |
| A6 board 烟测 | PASS（result 空→候选0） | 影子=正式 eligible=6 |
| B1 attr_rewrite | **已挂** `g_dimuser_close`（snap_v2 后） | 试跑阻塞：test 湖 result **无分区** |

## HOLD
- A2–A5 dept/product 周月：bus#13074 等字典整体重做，不动。

## 编排 bak（test）
- `full_chain.json.bak_20261113_page_visit_id_dict`
- `full_chain.json.bak_20261113_a1_stay`
- `full_chain.json.bak_20261113_attr_rewrite`

## 待狂人/上游
1. 产编排部署（禁手改 prod full_chain）
2. test `dws_register_attribution_result_d` 出数后试跑 `attr_rewrite_status` + board rewrite 全量
3. A1 换源差是否接受「跟结算全量渠道」业务确认后切产
