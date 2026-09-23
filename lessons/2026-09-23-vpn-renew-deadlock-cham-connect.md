# VPN 续期死结：变色龙「点击连接」后再续期

- **date**: 2026-09-23
- **tags**: vpn, telethon, cham, 变色龙, renew, deadlock
- **symptom**: vpn-sync 续期失败 + TG 全挂
- **root_cause**: 续期依赖 TG，TG 依赖 OpenVPN；双向同时断
- **fix**: 开 Cham → 点「点击连接」通外网 → TG 续期导入 ovpn → 关变色龙
- **not**: 向日葵；只打开 App 不点连接
- **ref**: feedback_vpn_renew_deadlock_use_cham.md
