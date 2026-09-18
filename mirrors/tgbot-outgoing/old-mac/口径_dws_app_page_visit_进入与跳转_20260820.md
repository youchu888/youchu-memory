# 页面访问日指标 · 进入次数 / 跳转次数取数说明

| 项 | 内容 |
|----|------|
| 表 | `dws.dws_app_page_visit_d_d` |
| 粒度 | `dt + app_id + page_key` |
| 字段 | `entry_cnt`（进入次数）、`jump_cnt`（跳转次数） |
| 上游 | `dwd.dwd_app_page_view_d` |
| 口径权威 | [metric_page_visit_analysis](http://54.255.236.159:8012/library/metric_page_visit_analysis) |
| ETL | `ops_system/04.dws/dws_app_page_visit_d_d/dws_app_page_visit_d_d.sql` |
| 整理日 | 2026-08-20（又初 · 私聊#369/#372） |

---

## 1. 公共过滤（两列共用）

从 `dwd.dwd_app_page_view_d` 取数前：

1. 业务日：`dt = 目标业务日`
2. **只账号**：`uid` 非空且非空白（空 uid 丢弃）
3. 页面键：`page_key` 优先，空则用 `current_page_key`；仍空则丢
4. `page_key` 长度 ≤ 64

不做设备口径。两列均为**次数**（COUNT/SUM），不是 UV。

---

## 2. 进入次数 `entry_cnt`

### 业务含义

从站外或无明确来路，**直接进入本页**的 PV 次数。

### 挂账维度

按**本页** `page_key` 聚合：本页访问条数里，满足「进入」条件的记 1。

### 取数条件（同时满足）

| 条件 | 说明 |
|------|------|
| 本行是本页访问 | 聚合键 = 本页 `page_key` |
| 来路为空 **或** 来路为 `unknown` | `referrer_page_key` 去空后为 NULL，或小写 trim 后等于 `unknown` |

### SQL 语义（节选）

```sql
SUM(
    CASE
        WHEN ref_pk IS NULL OR LOWER(TRIM(ref_pk)) = 'unknown' THEN 1
        ELSE 0
    END
) AS entry_cnt
-- GROUP BY dt, app_id, page_key（本页）
```

### 不算进入的例子

- 来路是其它真实页面 key → 算站内跳入本页，**不进** `entry_cnt`（也不记在本页的 `jump_cnt`；见下节）

---

## 3. 跳转次数 `jump_cnt`

### 业务含义

从**本页离开、跳到别的页**的次数（本页作为来路页）。

### 挂账维度

按**来路页** `referrer_page_key` 聚合：谁是来路，就把跳转次数记到谁身上。

### 取数条件（同时满足）

| 条件 | 说明 |
|------|------|
| 来路非空 | `referrer_page_key` 非空 |
| 来路不是 `unknown` | 小写 trim 后 ≠ `unknown` |
| 目标页 ≠ 来路页 | `page_key ≠ referrer_page_key`（排除自跳） |
| 来路 key 长度 ≤ 64 | 与本页 key 规则一致 |

### SQL 语义（节选）

```sql
SELECT
    dt, app_id,
    ref_pk AS page_key,   -- 挂在「来路页」上
    COUNT(*) AS jump_cnt
FROM base_f
WHERE ref_pk IS NOT NULL
  AND LOWER(TRIM(ref_pk)) <> 'unknown'
  AND ref_pk <> pk
  AND LENGTH(ref_pk) <= 64
GROUP BY dt, app_id, ref_pk
```

### 直观例子

用户路径：`A → B → C`

- 页 A 的 `jump_cnt` +1（离开 A 去 B）
- 页 B 的 `jump_cnt` +1（离开 B 去 C）
- 页 C：若无再离开，本条不增加 C 的 `jump_cnt`

若用户直接打开 B（来路空/`unknown`）：

- B 的 `entry_cnt` +1
- 不增加任何页的 `jump_cnt`

---

## 4. 两列对照

| | `entry_cnt` 进入 | `jump_cnt` 跳转 |
|--|------------------|-----------------|
| 挂在谁身上 | **本页**（当前 `page_key`） | **来路页**（`referrer_page_key`） |
| 看的方向 | 「怎么进来的」 | 「怎么离开的」 |
| 典型条件 | 来路空 / `unknown` | 来路=本页，且目标≠本页 |
| 源表 | `dwd_app_page_view_d` | 同左 |
| 是否 UV | 否，纯次数 | 否，纯次数 |

注意：同一条 page_view **不会**同时既算本页 `entry_cnt` 又算本页 `jump_cnt`——进入看本页来路是否空；跳转记在来路页上。

---

## 5. 非本说明范围

- `pv_cnt` / `uid_cnt`、停留与跳出、加载时长：见同目录 `design.md` / `spec.md`
- 查询侧比率（跳出率等）不落库，现算
- 跳转边表、设备口径：非目标，已不做

---

## 6. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-08-20 | 按仓库 ETL 与 spec 整理进入/跳转取数，私聊确认后落档 |
