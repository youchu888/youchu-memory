# 文档完整链验证 · test · dt=2026-07-27 · SF-81

> 对齐 `attribution_end_to_end_complete` §3 回写 + §6 对数  
> 环境：test 只写；prod 只读取候选 result  
> 时间：2026-07-28

## 链覆盖

| 步 | 文档 | 本次 |
|----|------|------|
| 1 日快照 | 牡丹 `dim_user_daily_snapshot` | 对 5 个候选 uid **灌 organic 种子**（模拟 Step1 输出，因 test 无对应行） |
| 2 归因计算 | `result_d` | **prod 当日真实 result** 灌入 test（5 行，`rewrite_*` 清空） |
| 3 回写主链 | 日快照 UPDATE + result 回标 | **跑文档对齐 SQL**（独立 wf 同源文件） |
| 3 后置 | `dim_user_all` UPDATE | **跑文档对齐 SQL** |
| 4 结算 | 千行 7 表 | **不在本次范围** |
| §7 统计 | metrics | 未跑（文档写后续详细设计） |

## §6 对数

| 条 | 结果 |
|----|------|
| ① 灰度 app 内：organic→真实渠道（5/5），守恒（5 organic→5 个真实渠道各 1） | PASS |
| ② 未开灰度 app（JHA-102）日快照 channel 分布不变 | PASS |
| ③ 抽 uid：snap_ch = all_ch = attributed_channel，rewrite_status=1，理由「已回写-命中…」 | PASS 5/5 |
| ④ 无 uid 指标 | N/A（本步不涉及） |

## 明细

5/5：`snap_eq=5 all_eq=5 rewrite1=5`

## 结论

文档 **Step3 主链+后置** 在 test 用真实 SF-81 候选验通。  
未在本轮重跑独立 wf 海豚实例（DEPENDENT/调度）；SQL 与 wf task 已同源。
