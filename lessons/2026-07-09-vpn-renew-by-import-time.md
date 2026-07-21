---
date: 2026-07-09
tags: [vpn, launchd, ops, feedback]
severity: medium
domain: ops
---

# VPN 续期按导入时刻滚动，非固定零点

## 背景

`center_dc_vpn_bot` 签发的 OpenVPN 证书为**导入时起算约 24h** 滚动有效期，不是每天固定时刻到期。主人经验：名义到期后短时间内通常仍可用，但应**提前**换新证，避免断连。

## 坑 / 错误做法

1. launchd 固定每天 00:10/00:05 跑 → 与真实导入时刻错位（例：09:23 导入则次日 09:23 才到期，凌晨任务会误跳过或漏续）。
2. 脚本只比对本地 `.ovpn` 文件指纹（mtime/size）→ 文件未变就跳过，不管已导入多久。
3. 严格按证书 `notAfter` 卡点续期 → 与现场「到期后还能用一会儿」不符，且不如记导入时刻稳。

## 正确做法

- **状态文件**：`~/.dc-platform/vpn/last_sync.json` 字段 `imported_at`（UTC ISO）记录上次成功导入时刻。
- **续期阈值**：距 `imported_at` 满 **23h**（`VPN_RENEW_AFTER_HOURS`，默认提前 1h）即拉新证；`notAfter` 仅作无记录时兜底。
- **轮询**：launchd `StartInterval=1800`（每 30 分钟），到期前某次轮询触发即可。
- **Telethon 锁**：与 `tgbot/bot.py` 共用 `user_telegram.session`；续期若 `database is locked` 需先 `stop.sh` 再跑脚本。

### 本机当前记录（2026-07-09 校正）

| 项 | 值 |
|----|-----|
| 上次导入（北京） | **2026-07-09 09:23:11** |
| 上次导入（UTC） | 2026-07-09T01:23:11+00:00 |
| 计划下次续期（约） | **2026-07-10 08:23**（导入后 23h） |
| 证书名义 notAfter | 2026-07-10 09:23（北京） |
| 配置路径 | `~/Desktop/CH/auto_vpn/center_dc_又初.ovpn` |
| 状态 | `~/.dc-platform/vpn/last_sync.json` |

## 验证

```bash
/usr/local/Caskroom/miniconda/base/envs/tgreport/bin/python \
  ~/.dc-platform/scripts/vpn_ovpn_sync.py
# 应打印「当前配置有效，跳过（上次导入 … 计划 … 前续期）」

cat ~/.dc-platform/vpn/last_sync.json | rg imported_at
tail ~/.dc-platform/vpn/sync.log
```

## 关联

- 脚本：`~/.dc-platform/scripts/vpn_ovpn_sync.py`
- 安装：`~/.dc-platform/scripts/install-vpn-sync-launchd.sh`
- 日志：`~/.dc-platform/vpn/sync.log`
