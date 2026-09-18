# dim_user_all → xwalk 命中率 gate · prod 实测

> dt: 2026-07-02 · env: **prod 只读** · 又初

## 结论

| 指标 | 结果 | gate | 判定 |
|------|------|------|------|
| **xwalk 裸命中率（用户加权）** | **80.99%** | ≥92.7% | ❌ 未达标 |
| 老维表 dim_region_info_all 裸命中 | 92.61% | — | 参照基线 |
| 中国用户 xwalk 命中 | 99.97% | — | ✅ |
| 非中国用户 xwalk 命中 | 33.60% | — | ❌ 主因 |

**prod 不能上**：gate 未过。根因是 **xwalk 对 dim_user_all 非中国地名覆盖不足**（2.93 亿非 CN 用户仅 33.6% 命中），不是 JOIN 口径写错。

## gate SQL（用户加权 · 三元组去重后回乘）

```sql
WITH triplet_wt AS (
  SELECT COALESCE(country,'其他') country, COALESCE(province,'其他') province,
         COALESCE(city,'其他') city, COUNT(*) user_cnt
  FROM dim.dim_user_all GROUP BY 1,2,3
), mapped AS (
  SELECT w.*, x.region IS NOT NULL AS xwalk_hit
  FROM triplet_wt w
  LEFT JOIN dim.dim_geo_region_xwalk x
    ON x.region_hash = xx_hash3_64(CONCAT_WS('-', w.country,
      NULLIF(NULLIF(w.province,''),'其他'), NULLIF(NULLIF(w.city,''),'其他')))
)
SELECT ROUND(100*SUM(CASE WHEN xwalk_hit THEN user_cnt END)/SUM(user_cnt),2) AS xwalk_hit_pct
FROM mapped;
-- 结果: 80.99%
```

## 分段

| 分段 | 用户数 | xwalk 命中 |
|------|--------|-----------|
| 中国 | 733,004,754 | 99.97% |
| 非中国 | 293,470,387 | 33.60% |

非 CN Top miss 样本：country 字段标「中国」但 province 实为美国地名（爱荷华州/Iowa）等脏数据。

## 代码进度（批 1）

| 项 | 状态 |
|----|------|
| 11 消费方 + video 2 表 → xwalk JOIN | ✅ git 已改 |
| ads_user_region_geo_d | ✅ 口径对齐（不挂批 1） |
| dim_user_all hourly | ✅ region + UPPER(user_type) + xwalk |
| dim_user_all daily | ✅ 同上（本轮补完） |
| dim_user_all ALTER region | ✅ 草案 `dim_user_all_alter_geo_region.sql` |
| prod DDL 执行 | ❌ 未做 |
| test 海豚发布 | ❌ 未做 |

## 变更记录

- 2026-07-02：又初 prod 实测 gate，确认未达标原因=非 CN xwalk 覆盖
