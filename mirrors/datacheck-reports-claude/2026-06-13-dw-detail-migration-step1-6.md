# dw 明细表迁移 — Checklist Step1~6 执行报告

**session**: `dev-20260611-001`  
**状态**: **已完成**（Step7 七天观察由用户手动执行）  
**日期**: 2026-06-13  
**范围**: dwd #1~#4（user_register / user_login 日+小时）  
**环境**: Step1 prod 只读；Step2~6 test

---

## Step1 双跑对账

### 1A 老表 vs 新表（prod，dt=2026-06-09）

| event | A 老 dw | B 新双扫 | Δ | Δ% | 结论 |
|---|---:|---:|---:|---:|---|
| user_register | 8,366,562 | 8,678,939 | +312,377 | +3.73% | B≥A；与方案 §5 晚到 ~3.3% 一致，**可接受** |
| user_login | 24,225,808 | 22,325,092 | -1,900,716 | -7.85% | B<A；prod 切换前须补齐 `_new` login 管道 |

### 1B 单扫 vs 双扫（prod `_new` 表，验证 ETL 逻辑）

| event | 单 dt=T-1 | 双扫 dt∈(T-1,T) | 增益 | Δ% | 结论 |
|---|---:|---:|---:|---:|---|
| user_register | 8,372,183 | 8,678,939 | +306,756 | +3.66% | **PASS** |
| user_login | 22,321,719 | 22,325,092 | +3,373 | +0.015% | **PASS** |

---

## Step2 改 4 路 SQL（仓库 + test 海豚）

| task | wf | 版本 | dt IN |
|---|---|---:|:---:|
| dwd_user_register_d_v2 daily | wf_dwd_事件明细_日 | v35→v36 | ✅ |
| dwd_user_login_d_v2 daily | wf_dwd_事件明细_日 | v36→v37 | ✅ |
| dwd_user_register_d_v2 hourly | wf_用户画像_小时 | v24→v25 | ✅ |
| dwd_user_login_d_v2 hourly | wf_用户画像_小时 | v25→v26 | ✅ |

---

## Step3 停下游 cron（test）

| schedule | wf | 动作 | 时间 |
|---:|---|---|---|
| 100 | wf_dwd_事件明细_日 | OFFLINE | 2026-06-13 11:05 BJ |
| 96 | wf_用户画像_小时 | OFFLINE | 2026-06-13 11:05 BJ |

---

## Step4 dw 表改名（test）

```sql
ALTER TABLE dw.dw_user_event_detail RENAME dw_user_event_detail_old;
ALTER TABLE dw.dw_user_event_detail_new RENAME dw_user_event_detail;
```

改名后 `dw.dw_user_event_detail` 含 `dt` 列；spot `dt=2026-06-12` → 225,400 行。

---

## Step5 手动跑 1 个 dwd ETL（test）

| 项 | 值 |
|---|---|
| 任务 | `dwd_user_register_d_v2` daily |
| 补数 PI | **51065** SUCCESS |
| schedule_time | 2026-06-13 03:20:00（T-1=2026-06-12） |
| raw 双扫 | 26 |
| dwd 分区 | dt=2026-06-12 → **26** |

**结论**: 改名 + 双扫 SQL 端到端 **PASS**。

---

## Step6 开 cron（test）

| schedule | wf | 动作 | 时间 |
|---:|---|---|---|
| 100 | wf_dwd_事件明细_日 | **ONLINE** | 2026-06-13 11:30 BJ |
| 96 | wf_用户画像_小时 | **ONLINE** | 2026-06-13 11:30 BJ |

验证：两 schedule `releaseState=ONLINE`。

---

## Step7 七天观察

**由用户手动执行**（本 session 交付范围外）。

建议每日 spot check：
- `dwd.dwd_user_register_d_v2` / `dwd_user_login_d_v2` 分区行数
- 注册/活跃指标与报表平台差异 ≤ 0.3%

---

## 会话结论

- test 环境 Checklist **Step1~6 全部完成**，session 状态 **已完成**
- prod 切换须另排低谷窗口；切换前补齐 login 管道数据
