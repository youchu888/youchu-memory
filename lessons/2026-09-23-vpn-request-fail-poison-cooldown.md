---
date: 2026-09-23
tags: [vpn, launchd, cooldown, telethon]
severity: high
domain: ops
---

# VPN 续期：失败 /request 占冷却导致整天假成功

## 现象

`com.youchu.vpn-sync` 每 30 分钟仍在跑且日志写「✅ VPN 同步完成」，但证书早过 23h 未真正换新；OpenVPN 断连。

## 根因链

1. `mark_request_sent()` 在 `request_ovpn_from_bot` **之前**写入 `last_request_at`
2. TG 连不上 / Bot 超时失败后仍占满 `VPN_MIN_HOURS_BETWEEN_REQUEST`（默认 20h）
3. 后续轮询：需要续期 → 冷却内复用已导入旧 `.ovpn` → 「跳过重复导入」→ **假成功**
4. 另一触发：证书未到期时误发 `/request` 失败，也会提前占冷却，真正到点时被挡

## 修法（已改 `vpn_ovpn_sync.py`）

- 仅在下载成功后 `mark_request_sent`
- 冷却期内只复用「尚未导入」的新文件；本地仍是已导入旧证则忽略冷却重请求
- 需要续期却只拿到已导入旧证时 **raise**，禁止假成功

## 应急

```bash
/usr/local/Caskroom/miniconda/base/envs/tgreport/bin/python -u \
  ~/.dc-platform/scripts/vpn_ovpn_sync.py --force-request-bypass-cooldown
```

## 验证

`cat ~/.dc-platform/vpn/last_sync.json` → `imported_at` 为刚才 UTC；`ls` 目录有当日时间戳存档。
