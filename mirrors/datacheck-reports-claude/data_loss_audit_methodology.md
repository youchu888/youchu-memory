# 缺失数据核查方法论

> 来源：工作狂人 bus#75（2026-06-29）· 知秋 `comic_event` 砍头核查实践标准化  
> 维护：又初 · 供 `/datacheck`、迁移对账、清洗误杀排查复用

## 适用场景

- dw → dwd 迁移后行数/覆盖度下降（「砍头」）
- 清洗规则变更导致 event 被拦入脏表（「误杀」）
- 下游 dws/ads 为 0 或骤降，需定位是源无数还是中间丢失

## 四铁律

| # | 规则 |
|---|------|
| ① | 查砍因**先拉脏表** `paimon.dw.dwd_standard_dirty_data_df` 的 `error_value`，**禁止猜测** |
| ② | **量级对账**：脏表被拦量 ≈ dw→dwd 缺口量，才坐实清洗/规则原因 |
| ③ | **结论必带明细样本**：`event_id` + 相关字段原值，可 SQL 回查 |
| ④ | **数据 0 先查源头**：先确认 dw 同期是否有数，再查 dwd/下游 |

## 六步流程

```
覆盖度比 → 按 app 拆缺口 → 拉脏表(error_type/column/value)
    → 量级对账 → 合规统计+抽样 → 出报告文件
```

### Step 1 · 覆盖度比

- dw 与 dwd 使用相同 `event_time` 边界（半开区间 `< 次日 0 点`）
- 同 event 类型、同分区粒度对比 COUNT / DISTINCT event_id
- 输出：总缺口率、按日缺口（若跨多日）

### Step 2 · 按 app 拆缺口

- **必须**分 `app_id` 独立核算缺口率
- 禁止多 app 混算掩盖单 app 塌方

### Step 3 · 拉脏表

- 表：`paimon.dw.dwd_standard_dirty_data_df`（prod paimon **dw** 库）
- 关键字段：`error_column`、`type`（error_type）、`error_value`、`raw_data`
- 按 Step 2 发现的缺口 app/event 过滤，GROUP BY 看 Top error 分布

### Step 4 · 量级对账

- 脏表被拦行数（或 DISTINCT event_id）与 Step 1 缺口量级比对
- 近似相等 → 坐实「清洗规则砍头」
- 显著不等 → 继续查 dw 边界、ETL 未跑、或其他丢数路径

### Step 5 · 合规统计 + 抽样

- 汇总 error_type / error_column / error_value 分布
- 每类 Top error 抽 ≥3 条 `event_id` 明细，附字段原值
- 违规行必须给真实原值，不可用统计摘要替代（见 team feedback）

### Step 6 · 出文件

- 报告路径：`.claude/database/reports/<db>.<table>/validate__<dt>__<timestamp>.md`
- 核查规则认可后同步更新 `.claude/database/playbooks/<db>.<table>.md`

## 脏表查询模板

```sql
-- 按 event + 业务日看 Top 拦截原因
SELECT
    error_column,
    type AS error_type,
    error_value,
    COUNT(*) AS cnt,
    COUNT(DISTINCT JSON_EXTRACT(raw_data, '$.event_id')) AS event_cnt
FROM paimon.dw.dwd_standard_dirty_data_df
WHERE dt = '${biz_date}'
  AND event_name = '${event_name}'
GROUP BY 1, 2, 3
ORDER BY cnt DESC
LIMIT 100;
```

```sql
-- 单条 error_value 抽样回查
SELECT event_id, error_column, error_value, raw_data
FROM paimon.dw.dwd_standard_dirty_data_df
WHERE dt = '${biz_date}'
  AND error_value = '${target_error_value}'
LIMIT 20;
```

## 与现有规范的关系

- 缺数三步（dw → dwd/_new → 脏表）见 `~/.dc-platform/memory/worker_ant/INDEX.md` §核查铁律
- 默认核查日 **T-1**；用户未指定日期禁止擅自扩窗
- prod 核数连 `my.cnf.prod`（52.221.240.167），test 数据稀疏易假异常

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-06-29 | 初版：工作狂人 comic_event 砍头实践 → 团队方法论 |
