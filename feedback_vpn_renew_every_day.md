# VPN 续期每天必跑（主人 2026-07-27 钦定）

## 铁律

**续 VPN 的动作不论节假日还是请假都不要停止，每天都要。**

适用范围：

- 周日 / 法定节假日 / 调休
- 主人请假日（`personal_leave_dates.json`）
- 打卡 / 居家抽查 / TG 上班在线保活 已跳过的日子

## 禁止

- ❌ 请假/放假时 unload `com.youchu.vpn-sync`
- ❌ 在 `vpn_ovpn_sync.py` / `run.sh` / `away-health` 里加 `should_skip_punch` 或工作日判断
- ❌ 把 VPN 续期当成「上班才要」的任务

## 正确

- ✅ launchd `StartInterval=1800` 全年每天轮询
- ✅ `away-health` 到期强制续期同样不看日历
- ✅ 请假只关打卡 + 抽查 + 上班时段在线保活

## 关联

- 规则：`.cursor/rules/leave-skip-punch-attendance.mdc`
- 脚本：`~/.dc-platform/scripts/vpn_ovpn_sync.py`
- lesson：`lessons/2026-07-27-vpn-renew-never-skip-leave-holiday.md`
