---
date: 2026-09-28
tags: [vpn, onehr, punch, accessibility, launchd, auto_vpn]
severity: high
domain: ops
---

# VPN 放 auto_vpn；onehr 只放打卡截图；截图失败先查辅助功能

## 背景

2026-09-28：`~/Desktop/CH/onehr/` 根目录出现 `.ovpn`；同日上班卡三次失败，TG 报「拒绝上传超过 180s 的旧图」。

## 坑 / 错误做法

1. `vpn_ovpn_sync.env` / 脚本默认把 `VPN_OVPN_DIR` 写成 `~/Desktop/CH/onehr`（与 lesson `2026-07-09` 的 `auto_vpn` 约定冲突）。
2. 把 TG 文案「拒绝旧图」当根因——那只是安全网；真因是截图脚本失败。
3. launchd 跑打卡时 `onehr_tg_click_account` 报 `Accessibility not trusted`；在 Cursor 交互壳里测 helper 会误判「权限正常」。

## 正确做法

| 目录 | 用途 |
|------|------|
| `~/Desktop/CH/auto_vpn/` | `.ovpn` 最新 + 带时间戳存档 |
| `~/Desktop/CH/onehr/YYYYMMDD/` | 打卡设备页截图 `telegram_devices_*.png` |

- 配置：`VPN_OVPN_DIR` / `VPN_DOWNLOADS_DIR` = `~/Desktop/CH/auto_vpn`；`DEFAULT_OVPN_DIR` 同步。
- 打卡失败先看 `~/.dc-platform/onehr/logs/checkin_YYYYMMDD.log` 里截图 ERROR。
- 若 `Accessibility not trusted`：系统设置 → 隐私与安全性 → 辅助功能，打开 **Homebrew `python3.14`**（及必要时 `onehr_tg_click_account`）；须在 **launchd 语境**复测，不能只在 Cursor 里点一次。
- 上班窗已过且 `_missed_checkin`：先问是否已手动打卡；已打则禁止自动补打。

## 验证

```bash
ls ~/Desktop/CH/onehr/            # 不应有 .ovpn
ls ~/Desktop/CH/auto_vpn/*.ovpn
/opt/homebrew/bin/python3 ~/.dc-platform/scripts/vpn_ovpn_sync.py --check
# 期望：配置目录 / 监听目录均为 auto_vpn

rg "Accessibility|截图失败|将上传截图" ~/.dc-platform/onehr/logs/checkin_$(date +%Y%m%d).log
```

## 关联

- `~/.dc-platform/scripts/vpn_ovpn_sync.{py,env}`
- `~/.dc-platform/scripts/onehr_telegram_devices_screenshot.sh`
- `~/.dc-platform/scripts/onehr_tg_click_account.swift`
- lesson：`2026-07-09-vpn-renew-by-import-time.md`、`2026-08-31-OneHR打卡禁止上传过期截图.md`、`2026-09-23-主人说已手动打卡时-禁止再重试或自动补打-当次打卡视为已完成.md`
