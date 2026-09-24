# geo xwalk 收尾复验 · 又初口径（权威）

> **环境**：test (sr_test)  
> **复验时间**：2026-06-26 19:43+ 北京时间  
> **xwalk 版本**：zh_crosswalk + cn_country_fallback + qita_subfallback  
> **整理**：又初

---

## 一、权威 hash（与 14 个 ETL 一致）

```sql
xx_hash3_64(CONCAT_WS('-',
  f.country,
  NULLIF(NULLIF(f.province, ''), '其他'),
  NULLIF(NULLIF(f.city, ''), '其他')
))
```

`region = COALESCE(x.region, 99999999)`

---

## 二、dim_user_all 结论（又初复验）

| 指标 | 旧 dim_region_info_all | 新 xwalk（收尾后） |
|------|------------------------|-------------------|
| 有效映射率（COALESCE≠99999999） | 92.71% | **83.08%**（狂人报 83.32%，同量级） |
| 真实地名 miss（country≠其他 且 x NULL） | — | **849（0.032%）** ✅ |
| 其他/其他/其他 → 99999999 | — | **437,100（16.65%）** ✅ 知秋确认不管 |

xwalk 增补行：`zh_crosswalk` 1179 + `cn_country_fallback` 169 + `qita_subfallback` 1

---

## 三、达标判定（狂人口径 · 又初采纳）

- ✅ **真实 miss 849 可忽略**（边界：省/市=其他 且 hash 上卷后仍无 xwalk 行，如 `印尼/其他/其他`）
- ✅ **43.7 万「其他/其他/其他」落 99999999** 与标准表一致，非回归
- ✅ **11 模型 ETL 接法不变**，仅 xwalk 表升级；要名字的 ads 仍 `JOIN dim_region_std`
- ⏳ **test 海豚发布 + dwm/dws 补数验数**（又初下一步）
- 🚫 **prod 不动**，等原子切换

---

## 四、复现 SQL

```sql
SELECT
  COUNT(*) AS users,
  ROUND(SUM(CASE WHEN COALESCE(x.region, 99999999) <> 99999999 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS mapped_pct,
  SUM(CASE WHEN x.region IS NULL AND f.country <> '其他' THEN 1 ELSE 0 END) AS real_miss
FROM dim.dim_user_all f
LEFT JOIN dim.dim_geo_region_xwalk x
  ON x.region_hash = xx_hash3_64(CONCAT_WS('-', f.country,
      NULLIF(NULLIF(f.province, ''), '其他'),
      NULLIF(NULLIF(f.city, ''), '其他')))
WHERE f.country IS NOT NULL AND TRIM(f.country) <> '';
-- 2026-06-26: mapped_pct≈83.08%, real_miss=849
```

---

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-06-26 | zh_crosswalk 收尾；又初 NULLIF 口径复验通过；849 miss 可忽略 |
