---
date: 2026-05-25
tags: [dolphin, complement, serial, test, prod]
severity: high
domain: ops
---

# 海豚补数：同一工作流勿并行提交两条 SERIAL complement

## 背景

对 **`wf_dws_汇总_日`**（prod wf_code 20691538136576；UI legacy `dws_日`）同时触发 LTV 与首充两条 `RUN_MODE_SERIAL` 补数链，期望覆盖 2026-01-01~今天。

## 坑 / 错误做法

- 短时间内连续 `complement` 两次（不同 `start-nodes`），两条链在 `SERIAL_WAIT` 交错执行。
- 结果：实例列表里 SUCCESS 的 `scheduleTime` 不连续（如只有 01-01~01-16 与 05-10~05-24），中间大段日期未跑。
- 误判「补数完成」：仅看 `active=0`，未核对 schedule 是否连续。

## 正确做法

1. **串行提交**：先跑完一条链（轮询至无 RUNNING/SERIAL_WAIT），再提交下一条。
2. **或单链 TASK_POST**：首充用 `TASK_POST` 一次提交，依赖链自动带 `user_d_h`。
3. **验收**：按日期 diff 缺失分区，或列 complement 的 `scheduleTime` 是否连续。

```bash
# 示例：先 LTV 再首充（prod）
python3 -m dolphin_ops.cli complement --env prod ... --start-nodes <ltv_daily> --task-dep TASK_ONLY
# 等待 DONE 后再
python3 -m dolphin_ops.cli complement --env prod ... --start-nodes <fr_daily> --task-dep TASK_POST
```

## 验证

- 海豚：`commandType=COMPLEMENT_DATA` 且目标日期段内每日一条 SUCCESS。
- 库：`COUNT(DISTINCT dt)` 与预期天数一致。

## 关联

- 脚本：`dolphin_ops/dolphin_ops/cli.py complement`
- 报告：`.claude/database/reports/test_ltv_first_recharge_datacheck_20260525.md`
