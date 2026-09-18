# prod 核查 · 过滤 0s（PRD 5.5.4）· 2026-08-05

> 范围：`dws.dws_session_duration_user_d` + 上游 `dwm.dwm_app_session_sid_d`  
> 焦点：**剔除无效/0 秒会话**（非五档合表）  
> 环境：prod 只读 · 业务日 T-1=2026-08-05 · 又初

## 结论

1. **结果表已按「仅 is_valid=1」落地**：近 7 日 session 无 `duration_bucket=0`，`bounce_sum=0`，`min_bucket=1`。
2. **线上 SQL 现为仅 `is_valid=1`**（session/daily 两支），与仓库 `dws_session_duration_user_d.sql` 一致；未见 `OR duration_bucket=0`。
3. **DWS session_cnt ≡ DWM is_valid=1**：T-1 全量 22,141,210；抽查多 app diff=0。
4. **旧 OR 口径风险仍在上游可见**：同日 DWM 仍有约 883 万 `is_valid=0 AND duration_bucket=0`；若回退旧 SQL，session 会多进约 **28.5%**，部分 app（如 YC-120）虚增可超百倍。

## 明细

### A. DWS 近 7 日 session（有无 0 档）

| dt | sess_all | sess_bkt0 | bounce | min_bkt |
|----|----------|-----------|--------|---------|
| 07-30 ~ 08-05 | ~21.5M–22.5M | **0** | **0** | **1** |

### B. T-1 分 grain

| grain | rows | sess/user | bkt0 | bounce | buckets |
|-------|------|-----------|------|--------|---------|
| session | — | 22,141,210 sess | 0 | 0 | 1–5 |
| daily | — | — | 0 | — | 1–5 |

### C. is_new × source_type（session）

| is_new | source | sess | bkt0 | bounce |
|--------|--------|------|------|--------|
| 0 | channel | 11,118,091 | 0 | 0 |
| 0 | organic | 7,545,824 | 0 | 0 |
| 1 | channel | 2,740,271 | 0 | 0 |
| 1 | organic | 737,024 | 0 | 0 |

### D. DWM 过滤对比（证明「旧 OR」危害）

| 口径 | 会话数 |
|------|--------|
| is_valid=1（现行） | ~22.1M |
| is_valid=1 OR duration_bucket=0（旧） | ~31.0M |
| 多进的 0s（is_valid=0∧bkt0） | ~8.83M（+28.5%） |

Top 多进 app（旧 OR 虚增）：YC-003 / YC-122 / YC-121 / JHA-157 / YC-123 等。

## 判定

- **过滤 0s：prod 数据侧 PASS**（多维无 0 档、与 valid1 对齐）。
- **SQL 侧：当前 prod 任务定义已是新口径**；勿再按「合表未做」排查。
