# new_users vs dim.register_time · test YC-001 · dt=2026-09-04

承接 bus#8295（权威源=dim；拆 52,939 vs 47,870）。

## 结论（一句话）

**不是「当天注册但无活跃」的命名问题，是 `dws_app_user_d` 落表相对现行源少算**：dim 当日新增 52,939 人在 `dwd_user_register_d_v2` 全有 REGISTER；按现行 ETL 重算应得 52,939；落表 `SUM(new_users)=47,870`（`BITMAP_UNION_COUNT=47,663`）。09-04 分区缺次日 daily OVERWRITE 兜底。

## 数

| 口径 | 数 |
|------|-----|
| A = dim `DATE(register_time)=2026-09-04` | 52,939 |
| dwd_v2 当日注册事件 uid | 53,508（−569=老用户重发，设计内） |
| 按 ETL 重算 B（PV∪REGISTER ∩ dim 当日注册） | 52,939（A=B） |
| A 在 dwd 有 REGISTER | 52,939 / 无事件 0 / login-only 0 |
| 落表 `SUM(new_users)` | 47,870 |
| 落表 `BITMAP_UNION_COUNT(new_users)` | 47,663（SUM 多 207=跨小时维值漂移） |
| 分区 `MAX(update_time)` | **2026-09-04 23:30:02**（无次日 05:20 daily） |
| 邻近日 daily 痕迹 | 09-03→09-04 05:20；09-05→09-06 05:20 |

## 缺口拆解（相对 SUM 差 5,069）

1. **小时窗截断**：末次小时累积到 23:30；首注事件 ≥23:30 的 A 侧 uid = **2,713**（日批全天窗本可吃掉）。
2. **其余 ~2.3k**：与小时跑点 dim 未齐、且该日 **未跑 daily OVERWRITE** 一致（现算能进 B，落表没有）。
3. **单 app YC-001**：非多 app 源集中问题。

## 权威

未拍板前不改 ETL。基准数继续用 **dim.register_time → 52,939**；47,870 不能当「新增账号」。
