# test 归因回写验数 · dt=2026-06-28

- 时间：2026-07-01 22:30
- 环境：test（prod 只读对照）
- 业务日：**2026-06-28**（补跑 schedule `2026-06-29 05:20:00`）
- 触发：bus#776/#777

## 根因（0 行覆盖）

| 错误 | 正确 |
|------|------|
| complement schedule = `2026-06-28 05:20` 或 `2026-06-30 05:20` | schedule = **`(dt+1) 05:20`**，即 `2026-06-29 05:20` |
| `dt=$[yyyy-MM-dd-1]` 宏与 schedule 错位 → INSERT OVERWRITE 0 行 | 对齐后出数正常 |

## ETL

| 任务 | 版本 | PI | 状态 |
|------|------|-----|------|
| `dws_register_attribution_result_d` | v79 | #55583 | SUCCESS |
| `dim_user_attribution_channel_apply_d` | v80 | complement 同 schedule | SUCCESS |

## 实表（test）

| 指标 | 值 | 判定 |
|------|---:|---|
| `result_d` 总行数 | **567** | ✅ |
| SF-81 行数 | **521** | ✅ |
| `rewrite_status=1` | **516** | ✅ |
| `rewrite_reason` 非空 | **567** | ✅ |
| `rewrite_reason` 含「已回写」 | **516** | ✅ |
| `rewrite_status` NULL | 51（JHG-001 等影子/未回写） | 预期 |

## 抽样（SF-81 rewrite_status=1）

| rewrite_reason | n |
|----------------|---:|
| 已回写-命中TMGFTF05Y4 | 52 |
| 已回写-命中JTO4PHNK6A | 52 |
| 已回写-命中N4KDQT7C0G | 42 |

## 结论

test **06-28** 归因识别 + 渠道回写两阶段落库验证通过；可供狂人抽样转知秋。**prod 等知秋令。**
