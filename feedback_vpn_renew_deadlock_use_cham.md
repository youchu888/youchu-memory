# VPN 续期死结 · 用变色龙打通外网（主人 2026-09-23）

## 死结

OpenVPN 证书过期 / `vpn-sync` 续期失败 → 无隧道 → Telethon/Bot 连不上 TG → 续期本身依赖 TG → 空转强刷无效。

## 破局（带外通道 = 变色龙加速器，不是向日葵）

1. `open -a Cham`（`/Applications/Cham.app`，显示名「变色龙加速器」，bundle `com.hellocham.app`）
2. **必须再点主页正中电源钮「点击连接」**（连上所选线路，如「香港大区 / VIP付费线路」）——只打开 App 不算连外网
3. 确认已连接后，切回 TG / 跑 `vpn_ovpn_sync` 续期并导入 OpenVPN Connect
4. 隧道 `utun` 正常后 **关闭变色龙连接（或退出）**，回到日常自动 `com.youchu.vpn-sync`

## 禁止

- ❌ 把向日葵当破死结通道（听错；向日葵是远程桌面）
- ❌ 只 `open -a Cham` 不点「点击连接」就当外网已通
- ❌ 隧道已恢复后还强刷 `--force-request`（主人：稳定后不要再 force）

## 自检

- Cham 进程：`pgrep -fl '/Applications/Cham.app'`
- OpenVPN 隧道：`ifconfig` 见 `utun*` 且有 `10.8.0.x`
- 续期成功：`~/.dc-platform/vpn/last_sync.json` 的 `imported_at` 为近次成功
