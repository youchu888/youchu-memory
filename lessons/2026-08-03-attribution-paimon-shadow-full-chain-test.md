---
date: 2026-08-03
tags: [attribution-shadow, paimon, dolphin, test]
severity: medium
domain: ops
---

# 归因 Paimon 影子全链：test 独立 wf + 全 _r，湖空则 SUCCESS 仍 0 行

## 背景

拍板：口径同现网（含 `attribution_flag=1`）、全链影子、先 test 再 prod、独立 wf 自动调度。

## 坑 / 错误做法

- 只建 `result_d_r`、不建 apply/metrics 影子与独立 wf
- 以为 test 湖有近期数：test `paimon.dwd` 注册/点击/曝光基本停在 06-11~12 或全空
- amend 已推 tip 时未确认 HEAD 是否为目标提交，会误改后续 commit

## 正确做法

1. 影子写出：`result_d_r` → `apply_d_r`（`dim_user_all_r` + `snapshot_r` + 回标 rewrite）→ `metrics_d_d_r`
2. DWD 只读 `paimon.dwd.*`；配置只读共用；禁止写现网
3. test wf：`wf_dws_归因_paimon_shadow_日`（`22565681487488`），cron `0 30 6 * * ? *` ONLINE
4. 建流：`dc-platform-server/scripts/create_wf_attribution_paimon_shadow.py`
5. 探表：`ops_system/.../dws_register_attribution_result_d/paimon_shadow_probe.md`
6. 真耗时：等 test 湖追数，或上 prod 影子（仍只写 `_r`）

## 验证

test 试跑 SUCCESS ~6–8s；行数 0 与湖空 + flag 入围一致。git：`785305d6`。

## 关联

- 脚本 / 文档见上；commit-voice 直述见 `2026-07-31-first-person-commit-voice.md`
