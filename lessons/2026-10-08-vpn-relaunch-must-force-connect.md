---
date: 2026-10-08
tags: [vpn, openvpn, connect-on-launch]
severity: high
domain: ops
---

# VPN 续期后必须退出再连，不能只 open 已在跑的客户端

## 背景

2026-10-08 15:13 续期导入新证书后，日志写「connectOnLaunch 将自动连接」，但隧道已断。客户端从 15:13 开着，直到 15:51 才重新 CONNECTED（utun5 / 10.8.0.11）。

## 坑 / 错误做法

1. `settings.json` 里 `connect:connectOnLaunch` 从 2026-10-04 23:07 起就是 false。已连上的会话不受影响，一退进程就不再拨号。
2. `import_profile` 的 CLI（`--list-profiles` / `--import-profile`）会先把 OpenVPN Connect 拉起来。后面的 `open -a` 对已在跑的进程是空操作，启动时自动连接不会再触发。
3. 本版 CLI `--help` 没有 `--connect`。真正强制拨号的参数是 `--connect-shortcut=<profile id>`。

## 正确做法

续期导入后：`--set-setting=connect-on-launch --value=true`，再 `quit`，然后：

```bash
open -a "OpenVPN Connect" --args --connect-shortcut=<最新 profile id>
```

连通标志：日志 `EVENT: CONNECTED`，地址 `10.8.0.11`。不要用家里的默认路由判断（这条 VPN 不改默认网关）。

## 验证

2026-10-08 15:51:53 `EVENT: CONNECTED … utun5/10.8.0.11/`。`connectOnLaunch` 已回到 true。

## 关联

- `~/.dc-platform/scripts/vpn_ovpn_sync.py` 的 `relaunch_openvpn`
- 同步副本：`~/.dc-platform/memory/scripts/vpn_ovpn_sync.py`
