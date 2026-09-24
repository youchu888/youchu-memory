---
date: 2026-07-27
tags: [vpn, leave, holiday, launchd, ops, feedback]
severity: high
domain: ops
---

# VPN 续期不因请假/节假日停止

## 背景

主人钦定：续 VPN 不论节假日还是请假都不要停，每天都要。打卡日历（周日/法定假/请假）只管极客打卡、居家抽查、上班时段 TG 在线；**不管 VPN**。

## 坑 / 错误做法

1. 请假流程里顺手 bootout / 停 `com.youchu.vpn-sync`
2. 以为「不上班就不用 VPN」——证书按导入时刻约 24h 滚动，断一天就断链
3. 把 `should_skip_punch` 复用到 VPN 脚本

## 正确做法

- 请假：只写 `personal_leave_dates.json`，**不动** VPN launchd
- `vpn_ovpn_sync.py` / `run.sh` / `away-health` **无日历门禁**
- 验证：`launchctl print gui/$(id -u)/com.youchu.vpn-sync` 仍 loaded；日志每天有轮询

## 验证

```bash
launchctl print "gui/$(id -u)/com.youchu.vpn-sync" | rg 'state|run interval|last exit'
tail -20 ~/.dc-platform/vpn/sync.log
# 请假日也不该出现「因假日跳过」类日志（脚本根本无此分支）
```

## 关联

- feedback：`feedback_vpn_renew_every_day.md`
- 规则：`.cursor/rules/leave-skip-punch-attendance.mdc`
- 既有：`lessons/2026-07-09-vpn-renew-by-import-time.md`
