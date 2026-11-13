# A7 test 核对 · ads_register_attribution_no_candidate_reason_d_d · 2026-11-12

## 范围
- ENV: test
- 步: `ads_register_attribution_no_candidate_reason_d_d` + pb
- 目录: `ops_system/spark_migrate/ads_register_attribution_no_candidate_reason_d_d/`

## 执行
| 步 | 结果 |
|---|---|
| ETL | SUCCESS · `rows_out=1` |
| pb | SUCCESS · 影子当日 1 行 |

## 上游（test 湖）
| 源 | 11-12 |
|---|---|
| 入围 iOS 自然 `attribution_flag=1` | 6 |
| `dws_register_attribution_result_d` | 0（无候选） |

## 影子 vs 正式
| src | app_id | reason_code | register_cnt |
|---|---|---|---|
| shadow | YC-159 | no_landing_same_ip | 6 |
| formal | YC-159 | no_landing_same_ip | 6 |

全键一致；合计=入围且无候选=6。

## 交审说明
- 代码与 step 已在 test 编排挂载；产编排部署归狂人。
- test 归因结果当日为空，属上游水位；正式同日同口径对齐，可作切海豚前样例。
- 不依赖 attr_rewrite（本表不读 rewrite_*）。
