---
date: 2026-09-28
tags: [vpn, renew, notAfter, launchd]
severity: high
domain: ops
---

# VPN 续期须同时看证书 notAfter，不能只看导入滚动钟

## 背景

证书 `notAfter=22:03 CST` 已过期，但 `vpn_ovpn_sync` 只按 `imported_at+23h` 判断，日志一直「当前配置有效，跳过」，计划次日 09:34 才续。

## 正确做法

`needs_renew = import_needs_renewal(...) or cert_needs_renewal(ovpn)`  
有 `imported_at` 时也要跑 `notAfter`（到期前 `VPN_CERT_RENEW_BEFORE_MINUTES`，默认 60）。

## 验证

```bash
python3 ~/.dc-platform/scripts/vpn_ovpn_sync.py
# 过期时应见「证书已过期」并拉新证导入
openssl … # 或脚本日志里的 notAfter
```

## 关联

- `~/.dc-platform/memory/scripts/vpn_ovpn_sync.py`（同步到 `~/.dc-platform/scripts/`）
- lesson：仅成功导入才写冷却
