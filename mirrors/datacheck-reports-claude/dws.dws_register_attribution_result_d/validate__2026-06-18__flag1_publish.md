# 数据核查 · 归因 flag=1 口径发布测试海豚

**日期**: 2026-06-18  
**环境**: test (sr_test)  
**Git**: `7497454` alter_table.sql 合并后发布

## 发布

| 任务 | task_code | 版本 | schedule |
|------|-----------|------|----------|
| `dws_register_attribution_result_d` | 174729603403591 | v37→**v38** | 103 ONLINE |
| `dim_user_attribution_channel_apply_d` | 21962007716224 | v38→**v39** | 103 ONLINE |

海豚 SQL 抽检：含 `AND r.attribution_flag = 1`，**无** `<> 1` 旧口径。

## 补数

窗口：2026-06-11 05:20 ~ 2026-06-19 05:05（TASK_ONLY，两 task）  
业务日覆盖：06-10 ~ 06-17

| 调度日 | PI | 归因 | 回写 |
|--------|-----|------|------|
| 06-11 ~ 06-18 | 52774~52781 | SUCCESS | SUCCESS |

## 验数

### 配置（part_01）

| 检查项 | 结果 |
|--------|------|
| `is_run=1` app 数 | **15** ✅ |
| `is_rewrite_channel` | 全 **0**（影子期）✅ |

### DWD 入围（part_00b）

| dt | `attribution_flag=1` | 旧口径 eligible (flag≠1) |
|----|----------------------|---------------------------|
| 06-15 | 0 | 1 |
| 06-16 | 0 | 5 |
| 06-17 | 0 | 3 |

测试库 **无 flag=1 注册**，新口径下 `reg_base` 为空属预期。

### 结果表

`dws.dws_register_attribution_result_d`：补数后 **0 行**（OVERWRITE 清空；无 flag=1 入围用户）。

## 结论

| 维度 | 判定 |
|------|------|
| 发布 / 补数实例 | ✅ 全 SUCCESS |
| SQL 口径对齐 Git | ✅ `attribution_flag=1` |
| 结果表有数 | ⚠️ 0 行（**数据侧**：API 未上报 flag=1，非 ETL 故障） |

**下一步**：API 联调写入 `payload.attribution_flag=1` 后，重跑 DWD 注册 + 归因补数再验。
