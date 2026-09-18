# geo 归一 xwalk 覆盖率核查 · 请工作狂人核实

> **环境**：test (sr_test)  
> **核查日**：2026-06-24（T-1）  
> **整理**：又初 · 2026-06-25  
> **目的**：新接法 `dim_geo_region_xwalk` vs 旧接法 `dim_region_info_all`（名字 JOIN），解释为何 dim_user_all 大量映射不上

---

## 一、接法对照

| 版本 | 表 | JOIN |
|------|-----|------|
| **旧** | `dim.dim_region_info_all` | `country/province/city` = `country_name/province_name/city_name` |
| **新** | `dim.dim_geo_region_xwalk` | `region_hash = xx_hash3_64(CONCAT_WS('-', country, NULLIF(province,''), NULLIF(city,'')))` |

ETL 取：`COALESCE(x.region, 99999999) AS region`

---

## 二、核查结论（摘要）

| 数据源 | 旧有效映射率 | 新有效映射率 | 判断 |
|--------|-------------|-------------|------|
| **昨日 PV**（`dwd_app_page_view_d` dt=2026-06-24） | 91.54% | **99.99%** | ✅ 新更好 |
| **全量用户**（`dim_user_all`） | **92.71%** | **71.54%** | ❌ 新差 21pp |
| **昨日活跃 UV**（PV uid ∩ 用户画像） | 91.99% | 90.20% | ≈ 持平 |

**PV 侧**：新 xwalk JOIN 失败 **0 行**，「其他」仅 3 行；distinct region 242→237（去碎）。

**用户画像侧**：新接法 **747,011 用户** xwalk JOIN 为 NULL（ETL 会落 99999999），是 prod 切换的主要风险点。

---

## 三、请工作狂人核实：为什么映射不上？

又初判断根因是 **xwalk 键与 dim_user_all 中文/IP 库字符串不一致**，不是 hash 公式写错。请帮忙确认/补数。

### 原因 A：xwalk 缺「中文行政名」键（最大头）

`dim_user_all` 存的是 IP 库**中文**三元组；xwalk 里同国家大量是**英文省/市**或简称，hash 对不上。

**实锤例 1 — 日本东京（5.4 万用户）**

| dim_user_all | xwalk 里有的键 | hash 命中 |
|--------------|----------------|-----------|
| `日本 / 东京都 / 东京` | ❌ 无此行 | ❌ null |
| — | `日本 / Tokyo / Kodaira` 等 | ✅ 有 |

```sql
-- test 已验证
SELECT region FROM dim.dim_geo_region_xwalk
WHERE region_hash = xx_hash3_64('日本-东京都-东京');  -- null

SELECT * FROM dim.dim_geo_region_xwalk
WHERE src_country='日本' AND src_province='Tokyo' LIMIT 1;  -- 有数据
```

**实锤例 2 — 中国省市后缀**

| 键 | 命中 |
|----|------|
| `中国-广东-深圳` | ✅ region=1795565 |
| `中国-广东省-深圳市` | ❌ null |
| `中国-广东`（缺市） | ✅ region=1809935（省级） |

若用户表带「省/市」后缀而 xwalk 只收录简称，会批量 miss。

### 原因 B：「其他/其他/其他」xwalk 无行（44.3 万用户）

| | 旧 dim_region_info_all | 新 xwalk |
|--|------------------------|----------|
| `其他/其他/其他` | 有行，region=**99999999** | **无 region_hash 行** → NULL |

旧表把「其他」当显式维度行；新 xwalk 未收录该三元组 → 全量用户统计上旧算「JOIN 命中」、新算「失败」。

### 原因 C：跨国脏三元组（老表有 hash，xwalk 无）

老维表对脏数据也建了独立 hash 行；xwalk 按 GeoNames 标准地理，不收录逻辑错误组合。

| country | province | city | 用户数 | 旧 | 新 |
|---------|----------|------|--------|----|----|
| 中国 | Singapore | Singapore | 29,029 | ✅ | ❌ |
| 中国 | 东京都 | 东京 | 21,415 | ✅ | ❌ |
| 中国 | Tokyo | Tokyo | 9,773 | ✅ | ❌ |

### 原因 D：miss 用户按国家 Top（新 xwalk NULL）

| country | miss 用户数 | miss 三元组种类数 |
|---------|------------|------------------|
| 其他 | 443,093 | 5 |
| **中国** | **223,816** | 239 |
| **日本** | **55,315** | 19 |
| 新加坡 | 7,078 | 7 |
| 美国 | 6,803 | 88 |

xwalk 全表 85,593 行，其中 `src_country` 含中文/常见中文国名约 22,400 行；**日本仅 1,676 行且多为 Tokyo 英文写法**。

---

## 四、PV 为什么反而 100%？

昨日 PV（27,423 行）用的是**事件当时** IP 解析三元组，与 xwalk 从 **IP 库全集**建表同源，残缺三元组（仅国/省）在 xwalk 里本来就有 level=1/2 行，故：

- 新 JOIN 失败：**0**
- 旧 JOIN 失败：2,320 行（8.5%）— 老名字表反而对不上

**→ 11 模型里读 dwd 事件 country/province/city 的链路，test 上 xwalk 表现正常；读 dim_user_all 画像的链路是缺口。**

---

## 五、请工作狂人确认的问题清单

1. **xwalk 建表口径**：当前是否仅 IP 库英文/原始 segment 字符串？**中文行政名**（东京都、广东省、深圳市）补全计划和时间？
2. **`其他/其他/其他`**：是否应在 xwalk 增加一行 `region_hash=xx_hash3_64('其他')` → region=99999999？
3. **脏三元组**（中国+Singapore 等）：期望落 99999999，还是尝试纠错到真实国？
4. **达标线**：dim_user_all 有效映射率 **≥92.7%**（对齐旧表）— 补中文后能否复测通过？
5. **dim_user_all.region 预解析**：画像改存 geonameid 后，11 模型是否仍要 JOIN xwalk，还是直接读 `dua.region`？

---

## 六、复现 SQL（test 只读）

### 6.1 全量用户覆盖率

```sql
SELECT
  COUNT(*) AS users,
  ROUND(SUM(CASE WHEN old_d.region IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS old_join_pct,
  ROUND(SUM(CASE WHEN new_x.region IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS new_join_pct
FROM dim.dim_user_all f
LEFT JOIN dim.dim_region_info_all old_d
  ON f.country = old_d.country_name AND f.province = old_d.province_name AND f.city = old_d.city_name
LEFT JOIN dim.dim_geo_region_xwalk new_x
  ON new_x.region_hash = xx_hash3_64(CONCAT_WS('-', f.country, NULLIF(f.province, ''), NULLIF(f.city, '')))
WHERE f.country IS NOT NULL AND TRIM(f.country) <> '';
-- 结果：old 92.71% / new 71.54%
```

### 6.2 昨日 PV 覆盖率

```sql
SELECT
  COUNT(*) AS pv,
  ROUND(SUM(CASE WHEN old_d.region IS NOT NULL AND old_d.region <> 99999999 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS old_pct,
  ROUND(SUM(CASE WHEN new_x.region IS NOT NULL AND new_x.region <> 99999999 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS new_pct
FROM dwd.dwd_app_page_view_d f
LEFT JOIN dim.dim_region_info_all old_d
  ON f.country = old_d.country_name AND f.province = old_d.province_name AND f.city = old_d.city_name
LEFT JOIN dim.dim_geo_region_xwalk new_x
  ON new_x.region_hash = xx_hash3_64(CONCAT_WS('-', f.country, NULLIF(f.province, ''), NULLIF(f.city, '')))
WHERE f.dt = '2026-06-24' AND f.uid IS NOT NULL AND TRIM(f.uid) <> '';
-- 结果：old 91.54% / new 99.99%
```

### 6.3 Top miss 三元组（旧命中、新未命中）

```sql
WITH base AS (
  SELECT country, province, city, COUNT(*) AS cnt
  FROM dim.dim_user_all
  WHERE country IS NOT NULL AND TRIM(country) <> ''
  GROUP BY country, province, city
)
SELECT b.country, b.province, b.city, b.cnt, old_d.region AS old_region
FROM base b
LEFT JOIN dim.dim_region_info_all old_d
  ON b.country = old_d.country_name AND b.province = old_d.province_name AND b.city = old_d.city_name
LEFT JOIN dim.dim_geo_region_xwalk new_x
  ON new_x.region_hash = xx_hash3_64(CONCAT_WS('-', b.country, NULLIF(b.province, ''), NULLIF(b.city, '')))
WHERE old_d.region IS NOT NULL AND new_x.region IS NULL
ORDER BY b.cnt DESC LIMIT 20;
```

---

## 七、群聊转发版（可直接复制）

```
@工作狂人 geo xwalk 覆盖率 test 核查完毕，麻烦核实「为什么 dim_user_all 映射不上」：

【结论】
· 昨日 PV（dwd 事件三元组）：新 99.99% > 旧 91.54% ✅
· 全量 dim_user_all：新 71.54% < 旧 92.71% ❌（差 21pp，约 75 万用户 xwalk NULL→99999999）

【又初判断根因 — 请确认】
1. xwalk 键多为 IP 库英文/简称，用户表是中文（例：用户「日本-东京都-东京」无键；xwalk 有「日本-Tokyo-xxx」）
2. 「其他/其他/其他」44 万：旧表有 99999999 行，xwalk 无
3. 脏三元组（中国+Singapore 等）：旧 hash 表有，xwalk 无
4. 中国 miss 22 万 / 日本 miss 5.5 万 — 疑似缺中文行政名 & 省市区后缀不一致（「广东-深圳」有，「广东省-深圳市」无）

【不影响】读 dwd 事件 geo 的 11 模型 ETL，test 上 PV 已 100% JOIN

【待你确认】
· 中文地名补全计划？达标线仍 ≥92.7%？
· 「其他」三元组是否写入 xwalk？
· 详细报告+SQL：CHcode/.claude/database/reports/dim.dim_geo_region_xwalk/validate__2026-06-24__coverage_vs_legacy.md
```

---

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-06-25 | 又初首版：test 对比旧名字 JOIN vs 新 xwalk hash JOIN |
