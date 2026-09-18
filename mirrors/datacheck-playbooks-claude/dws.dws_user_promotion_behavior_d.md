# dws.dws_user_promotion_behavior_d 数据核查剧本

本剧本同时作为下列三张姊妹表的**主剧本**：

- `dws.dws_user_promotion_behavior_h`（渠道评分表·小时）
- `dws.dws_user_promotion_behavior_charge_d`（渠道充值表·日）
- `dws.dws_user_promotion_behavior_charge_h`（渠道充值表·小时）

对应各姊妹表的 playbook 文件只列差异点，核心规则都在这里。

## 1. 表信息

| 表 | 业务名 | 粒度（DUPLICATE KEY） | 指标 |
|---|---|---|---|
| `dws.dws_user_promotion_behavior_d` | 渠道评分·日 | `dt+channel+app_id+uid`（同 uid 可跨 device 多行） | 4 充值金额 + `consume_amount` + `ad_click_count` + `total_play_time` + `is_video_viewer/is_payer/is_order_creator/is_searcher` + `is_day1_ret/is_day7_ret/is_day15_ret/is_day30_ret` + `device` |
| `dws.dws_user_promotion_behavior_h` | 渠道评分·小时 | `hour+dt+channel+app_id+uid(+device)` | 同上（`decimal(18,2)`） |
| `dws.dws_user_promotion_behavior_charge_d` | 渠道充值·日 | `dt+channel+app_id+uid` | 仅 4 充值金额：`recharge_amount / vip_charge_amount / deduction_vip_charge_amount / coin_charge_amount` |
| `dws.dws_user_promotion_behavior_charge_h` | 渠道充值·小时 | `hour+dt+channel+app_id+uid` | 同 charge_d |

- 状态：全部上线
- 绑定程序：`/ops_system/04.dws/dws_user_promotion_behavior_d/` 与 `..._h/`（见 `program_mappings.md`）
- `is_day*_ret` 留存字段已废弃，当前固定为 0，不核。

## 2. 使用前提（所有 part 通用）

1. **只核真实渠道**：`channel IS NOT NULL AND channel != 'organic'`（与 `project_metadata.md` 约定一致）。
2. **按 app 独立核算**，只核对合法格式 app_id：`^[A-Za-z]+-[0-9]+$`（参考项目规则）。
3. **`is_*` tinyint 标志必须按用户粒度先 MAX 再 SUM**：
   - _h 表里同 uid 跨多小时每行 is_*=1，直接 `SUM(is_*)` 会膨胀。
   - _d 表因 DUPLICATE KEY 允许同 uid 跨 device 多行，`SUM(is_*)` 也会膨胀。
   - 规则：`SUM(x) FROM (SELECT MAX(is_*) x FROM ... GROUP BY dt,channel,app_id,uid)`。
4. **金额类字段可直接 SUM**（允许跨 hour/device 相加）。
5. **charge 侧金额 ≡ behavior 侧同名金额**。charge 是 behavior 的充值子集投影，不会出现独立的差异来源。
6. 金额精度：_d / _h 的 decimal 精度不同（behavior_d 用 `decimal(18,4)`，其他用 `decimal(18,2)`）。比较前用 `ROUND(x, 2)`。

## 3. 默认参数

- `target_dt`：默认 T-1（昨天）
- `hourly_dts`：小时核对默认 `[T-1, T]`（昨天整天 + 今天到当前时刻）

## 4. 核查 parts

### part_01_daily_vs_hourly_total（同业务表日=小时汇总）

**charge**：

```sql
SELECT 'charge_d' src,
  ROUND(SUM(recharge_amount),2) r, ROUND(SUM(vip_charge_amount),2) v,
  ROUND(SUM(deduction_vip_charge_amount),2) dv, ROUND(SUM(coin_charge_amount),2) c
FROM dws.dws_user_promotion_behavior_charge_d
WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic'
UNION ALL
SELECT 'charge_h',
  ROUND(SUM(recharge_amount),2), ROUND(SUM(vip_charge_amount),2),
  ROUND(SUM(deduction_vip_charge_amount),2), ROUND(SUM(coin_charge_amount),2)
FROM dws.dws_user_promotion_behavior_charge_h
WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic';
```

**behavior 金额/计数**：

```sql
SELECT 'behavior_d' src,
  ROUND(SUM(recharge_amount),2) r, ROUND(SUM(vip_charge_amount),2) v,
  ROUND(SUM(deduction_vip_charge_amount),2) dv, ROUND(SUM(coin_charge_amount),2) c,
  ROUND(SUM(consume_amount),2) cs,
  SUM(ad_click_count) adc, SUM(total_play_time) tpt
FROM dws.dws_user_promotion_behavior_d
WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic'
UNION ALL
SELECT 'behavior_h', /* 同列 */ ...
FROM dws.dws_user_promotion_behavior_h
WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic';
```

**behavior is_\* 标志**（按用户粒度去重后比）：

```sql
SELECT src, SUM(viewer) v, SUM(payer) p, SUM(creator) c, SUM(searcher) s FROM (
  SELECT 'behavior_d' src, MAX(is_video_viewer) viewer, MAX(is_payer) payer,
    MAX(is_order_creator) creator, MAX(is_searcher) searcher
  FROM dws.dws_user_promotion_behavior_d
  WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic'
  GROUP BY dt, channel, app_id, uid
  UNION ALL
  SELECT 'behavior_h', MAX(is_video_viewer), MAX(is_payer),
    MAX(is_order_creator), MAX(is_searcher)
  FROM dws.dws_user_promotion_behavior_h
  WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic'
  GROUP BY dt, channel, app_id, uid
) t GROUP BY src;
```

判定：每组两行所有字段逐列相等 → 通过。

### part_02_charge_vs_behavior_metrics（跨表同名指标）

4 充值金额字段，charge ↔ behavior 两侧应完全相等。

```sql
-- 天对天
SELECT 'charge_d' src, <4 个 ROUND(SUM)>
FROM dws.dws_user_promotion_behavior_charge_d WHERE dt='${target_dt}' AND ...
UNION ALL
SELECT 'behavior_d', <同>
FROM dws.dws_user_promotion_behavior_d WHERE dt='${target_dt}' AND ...;

-- 小时对小时（昨天 + 今天两天）
WITH ch AS (
  SELECT dt, hour, <4 个 ROUND(SUM)>
  FROM dws.dws_user_promotion_behavior_charge_h
  WHERE dt IN (${hourly_dts}) AND channel IS NOT NULL AND channel!='organic'
  GROUP BY dt, hour
), bh AS (
  SELECT dt, hour, <4 个 ROUND(SUM)>
  FROM dws.dws_user_promotion_behavior_h
  WHERE dt IN (${hourly_dts}) AND channel IS NOT NULL AND channel!='organic'
  GROUP BY dt, hour
)
SELECT ch.dt, ch.hour, ...,
  CASE WHEN 所有字段相等 THEN 'OK' ELSE 'DIFF' END eq
FROM ch JOIN bh USING (dt, hour)
ORDER BY ch.dt, ch.hour;
```

判定：0 DIFF → 通过。

### part_03_per_app_spotcheck（头部 app 四表交叉抽样）

头部 app（按 `recharge_amount` 大小 TOP-5 或业务指定），四张表 × 4 金额字段 逐格比较。

```sql
SELECT app_id, src, ROUND(SUM(r),2) r, ROUND(SUM(v),2) v,
       ROUND(SUM(dv),2) dv, ROUND(SUM(c),2) c
FROM (
  SELECT app_id, 'charge_d' src, recharge_amount r, vip_charge_amount v,
         deduction_vip_charge_amount dv, coin_charge_amount c
    FROM dws.dws_user_promotion_behavior_charge_d
    WHERE dt='${target_dt}' AND channel IS NOT NULL AND channel!='organic'
  UNION ALL SELECT app_id, 'charge_h', ... FROM dws.dws_user_promotion_behavior_charge_h
    WHERE dt='${target_dt}' AND ...
  UNION ALL SELECT app_id, 'behavior_d', ... FROM dws.dws_user_promotion_behavior_d
    WHERE dt='${target_dt}' AND ...
  UNION ALL SELECT app_id, 'behavior_h', ... FROM dws.dws_user_promotion_behavior_h
    WHERE dt='${target_dt}' AND ...
) u
WHERE app_id IN (${sample_apps})
GROUP BY app_id, src
ORDER BY app_id, src;
```

判定：同 app 4 行（= 4 个 src）× 4 列金额 **16 格完全相等**。

### part_04_anomaly_locate（可选，有 diff 时启用）

- 发现 part_01 / part_02 失败 → 缩小到 `(app_id, channel)` 分组找差异最大的 N 行。
- 发现 is_\* 差异 → 按 `(dt, channel, app_id, uid)` 找同 uid 在 _h 出现 ≥2 个不同 MAX(is_\*) 的异常样本。
- 发现金额差异 → 输出 charge 侧 / behavior 侧同 `(dt, channel, app_id, uid)` 的明细对比，定位是 charge 汇总漏数据，还是 behavior 侧重算错误。

## 5. 输出与报告

- 默认写到：`.claude/database/reports/dws.dws_user_promotion_behavior_d/`
- 文件名示例：`consistency_${target_dt}.md`
- 报告结构：
  1. **结论**
  2. **四表基础信息**（粒度 + 当批次行数）
  3. **part_01 结果表**
  4. **part_02 结果表**（天 + 所有小时切片的 OK/DIFF）
  5. **part_03 抽样结果表**
  6. **异常明细 / 处理建议**（如有）

## 6. 历史核查

- 2026-04-20：`04-19` 全天 + `04-20` 17 点前的小时切片。part_01~part_03 全部通过（charge 4 金额字段、behavior 金额/计数/时长/按用户 is_\*、cross-table 同名金额、41 个小时切片、5 个头部 app）0 DIFF。
- 2026-04-30：客户报 `umlyfrws` / `JHG-001` / `dt 2026-04-21~04-29` 的 iOS 注册占比 98.95% 偏高。链路一致性 OK（dwd → dws_settlement → dws 都是 1971/1992），定位为**上游 dwd 注册事件 04-28 起出现"无证据 iOS"回归**：306 行 `device='iOS'` 但 `user_agent` / `device_brand` / `device_model` 三字段全空（其中 04-29 当天 iOS 注册 292 行**全部**是无证据）。剔除后真实 iOS 占比 = 1665 / 1992 = 83.59%。详见 §7。

## 7. 渠道评分查询口径与即席核查

**这个表 = 业务侧"渠道评分"。** 跟客户对话里出现这些词，按下表换算到字段：

| 业务说法 | 表字段 | 含义 |
|---|---|---|
| **渠道评分** | 整张 `dws.dws_user_promotion_behavior_d` | 这张表本身 |
| **结算时间** | `dt` | 用户**当天的行为**统计日期（行的归属日） |
| **推广时间** | `register_date` | 用户**注册**的那一天 |
| **推广时间范围内注册的客户的行为** | `register_date BETWEEN ... AND ... AND dt BETWEEN ... AND ...` | 双范围筛选：人在 A 区间注册 + 行为在 B 区间发生（A 和 B 经常是同一段，但不是必然） |
| **渠道** | `channel` | 含 `'organic'`，业务核查默认排除 |
| **app** | `app_id` | 合法格式 `^[A-Za-z]+-[0-9]+$`，按 app 独立核算 |

> ⚠️ 客户口径里"推广时间"≠"结算时间"。具体什么口径以客户当次说明为准；要么单 register_date 限定，要么单 dt 限定，要么双限定。**默认双限定**："推广时间范围内注册 + 同范围内有行为"。

### 7.1 标准模板：推广 + 结算双范围筛选

**双范围 device 占比**（用户问"X 渠道 Y app 推广时间内注册用户的设备占比"时用）：

```sql
-- ${promo_start}/${promo_end}：推广时间（register_date 范围）
-- ${settle_start}/${settle_end}：结算时间（dt 范围；客户没单独说就用同一段）
SELECT
  device_user,
  COUNT(*) AS uid_cnt,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM (
  SELECT uid, MAX(device) AS device_user
  FROM dws.dws_user_promotion_behavior_d
  WHERE channel='${channel}'
    AND app_id='${app_id}'
    AND dt            BETWEEN '${settle_start}' AND '${settle_end}'
    AND register_date BETWEEN '${promo_start}'  AND '${promo_end}'
  GROUP BY uid
) t
GROUP BY device_user
ORDER BY uid_cnt DESC;
```

**MAX(device) 而非 SUM**：表是 `DUPLICATE KEY(dt,channel,app_id,uid)`，同 uid 跨多天可能多行；先按 uid 聚合再统计才不会膨胀。

**金额 / 计数指标按推广时间筛选**：

```sql
-- "推广时间内注册用户在结算时间内的总充值"
SELECT ROUND(SUM(recharge_amount), 2) AS total_recharge
FROM dws.dws_user_promotion_behavior_d
WHERE channel='${channel}' AND app_id='${app_id}'
  AND dt            BETWEEN '${settle_start}' AND '${settle_end}'
  AND register_date BETWEEN '${promo_start}'  AND '${promo_end}';
```

**`is_*` 标志按用户去重再聚合**（同 §2.3）：

```sql
SELECT SUM(viewer) v, SUM(payer) p, SUM(creator) c, SUM(searcher) s
FROM (
  SELECT MAX(is_video_viewer) viewer, MAX(is_payer) payer,
         MAX(is_order_creator) creator, MAX(is_searcher) searcher
  FROM dws.dws_user_promotion_behavior_d
  WHERE channel='${channel}' AND app_id='${app_id}'
    AND dt            BETWEEN '${settle_start}' AND '${settle_end}'
    AND register_date BETWEEN '${promo_start}'  AND '${promo_end}'
  GROUP BY dt, channel, app_id, uid
) t;
```

### 7.2 device 字段质量检测（"无证据 iOS"判定）

`device` 是上游 SDK / ETL 的**结论字段**，不是用户原报。结论必须有原始字段佐证才可信。

device 来源链路：

```
dwd.dwd_user_register_d_v2 (device + user_agent + device_brand + device_model + system_name)
    → dws.dws_settlement_user_register_h (device 取注册事件的 device)
    → dws.dws_user_promotion_behavior_d  (注册分支 device 来自 settlement_user_register_h)
                                          (其他分支 device=null，靠 LEFT JOIN COALESCE 填，
                                           最终默认 'OTHER'）
```

dws_user_promotion_behavior_d 的 device 三种取值（生产实测）：
- `IOS` / `ANDROID`：来自注册事件，UA / brand / model 解析到的
- `OTHER`：LEFT JOIN settlement_user_register_h 没找到这个 uid（典型情况：用户在 dt 范围之前注册的，本次只有行为没有注册）

**质量判定规则**：所有 `device='IOS'` 的注册事件，必须满足下列**至少一项**才算"有证据"：

| 字段 | 有证据条件 |
|---|---|
| `user_agent` | 不为空 |
| `device_brand` | 不为空且不等于 `'Mozilla'`（`Mozilla` 是 UA 第一段，无判别力） |
| `device_model` | 不为空且包含 `'iPhone'` 或 `'iOS'` |
| `system_name` | 不为空且为 `iOS` |

> 实际生产里 `user_agent` 经常被上游清洗策略剥空（保留 brand / model 副本），所以**主要靠 brand / model / system_name 三选一**。

**全空 = 无证据 = 应归 OTHER 而非 IOS**。生产里发现的 SDK / ETL 兜底 bug：上游在三字段全空时把 `device` 默认填 'iOS'。

### 7.3 device 质量核查 SQL 模板

```sql
-- 把 dwd 注册事件按"是否有证据支持 device 判定"分桶
SELECT
  device,
  CASE
    WHEN (user_agent  IS NULL OR TRIM(user_agent)='')
     AND (device_brand IS NULL OR TRIM(device_brand)='' OR device_brand='Mozilla')
     AND (device_model IS NULL OR TRIM(device_model)='')
     AND (system_name  IS NULL OR TRIM(system_name)='')
    THEN 'A_no_evidence'
    WHEN user_agent IS NOT NULL AND TRIM(user_agent)<>''
    THEN 'C_full_ua'
    ELSE 'B_brand_model_only'
  END AS bucket,
  COUNT(*) AS cnt
FROM dwd.dwd_user_register_d_v2
WHERE app_id='${app_id}'
  AND channel='${channel}'
  AND dt BETWEEN '${start}' AND '${end}'
GROUP BY device, bucket
ORDER BY device, cnt DESC;
```

**A_no_evidence 阈值**：正常历史区间（生产实测）≈ 0；任何 A 类 > 0 都要查 ETL / SDK。

**修正后真实 device 占比**：把 A 类从 IOS 计数中扣除归 OTHER 重算：

```sql
SELECT
  CASE
    WHEN (user_agent  IS NULL OR TRIM(user_agent)='')
     AND (device_brand IS NULL OR TRIM(device_brand)='' OR device_brand='Mozilla')
     AND (device_model IS NULL OR TRIM(device_model)='')
     AND (system_name  IS NULL OR TRIM(system_name)='')
    THEN 'OTHER'
    ELSE UPPER(TRIM(device))
  END AS device_corrected,
  COUNT(*) AS cnt,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM dwd.dwd_user_register_d_v2
WHERE app_id='${app_id}'
  AND channel='${channel}'
  AND dt BETWEEN '${start}' AND '${end}'
GROUP BY device_corrected
ORDER BY cnt DESC;
```

### 7.4 渠道评分条件查询（客户系统参数 → SQL 映射）

客户系统传入的标准参数与表字段对应关系：

| 客户参数 | 表字段 | 说明 |
|---|---|---|
| `startTime` / `endTime` | 按指标定义映射 | 指标相关时间范围（取日期部分） |
| `activityStartTime` / `activityEndTime` | `dt` | 结算日/活动日范围 |
| `channelCode` | `channel` | 渠道编码 |
| `appId` | `app_id` | 应用 ID |

**指标定义（持续追加）：**

| 指标名 | 公式 | 时间字段 | 条件 |
|---|---|---|---|
| 注册人数 | `COUNT(DISTINCT uid)` | `register_date` 对应 `startTime~endTime` | `register_date >= startDate AND register_date <= endDate` |
| 充值金额 | `ROUND(SUM(recharge_amount), 2)` | `register_date` + `dt` | `register_date` 在 `startTime~endTime`，`dt` 在 `activityStartTime~activityEndTime` |
| VIP充值金额 | `ROUND(SUM(vip_charge_amount), 2)` | 同上 | 同上 |
| 扣费VIP充值金额 | `ROUND(SUM(deduction_vip_charge_amount), 2)` | 同上 | 同上 |
| 金币充值金额 | `ROUND(SUM(coin_charge_amount), 2)` | 同上 | 同上 |
| 消费金额 | `ROUND(SUM(consume_amount), 2)` | 同上 | 同上 |

> 后续新增指标在此表追加行即可。

**示例 SQL：**

```sql
-- 注册人数
SELECT COUNT(DISTINCT uid) AS 注册人数
FROM dws.dws_user_promotion_behavior_d
WHERE channel = '{channelCode}'
  AND app_id = '{appId}'
  AND register_date >= '{startDate}'
  AND register_date <= '{endDate}'
  AND dt >= '{activityStartDate}'
  AND dt <= '{activityEndDate}';
```

### 7.5 报告必含项（用户问"渠道评分"+设备问题时）

1. **链路一致性**：dwd → dws_settlement → dws 三层 iOS uid 数 / 占比对比表（应该完全一致；不一致先查 ETL 链路而不是数据质量）
2. **A/B/C 桶分布**（按 dt 拆开看是哪天突变）
3. **A 类抽样明细**（≥5 行，带 event_id / event_time / uid / device / 各原始字段 / device_id / ip，可 SQL 回查）
4. **修正后真实占比**（A 类归 OTHER 后重算）
5. **建议**：短期报表剔除规则、中期 SDK / ETL 兜底逻辑修复、监控阈值

