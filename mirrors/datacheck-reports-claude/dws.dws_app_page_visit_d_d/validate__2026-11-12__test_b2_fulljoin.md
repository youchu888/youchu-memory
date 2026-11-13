# B2 FULL JOIN · dws_app_page_visit_d_d · test · 2026-11-12

## 总量（影子 / 正式）

| src | rows | pv | uid_card | stay_sec | stay_pages |
|---|---:|---:|---:|---:|---:|
| shadow | 3484 | 428816 | 132850 | 13090347 | 367351 |
| formal | 3239 | 367326 | 93854 | 13096372 | 367326 |

## 全键分类（app_id×page_key；equal 含 pv+stay）

| 类 | 键数 | pv_abs | stay_abs |
|---|---:|---:|---:|
| equal_pv_stay | 3109 | 0 | 0 |
| pv_eq_other_diff | 118 | 0 | 44289 |
| metric_diff | 12 | 672 | 596 |
| only_shadow | 245 | 60818 | 0 |
| only_formal | 0 | — | — |

闭合：equal+pv_eq+metric+only_shadow=3484；equal+pv_eq+metric=3239。

## 成因
1. **停留**：`stay_pages` 总量接近（367351 vs 367326）；多数键 pv+stay 对齐（3109）。
2. **uid_cnt**：影子字典号 bitmap vs 正式旧口径 → uid_card 差大，属切字典预期，不对齐不算错。
3. **only_shadow 245**：影子多页键（字典/停留并集展开），pv 增量主要在此类。

## 判定
- id_dict + stay + pb 链路 PASS。
- pv/stay 大体可对齐；uid 换字典号后不与正式 bitmap_count 直接比平。
