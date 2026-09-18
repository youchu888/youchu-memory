# Lesson · 经 memory-git 远程升级旧机 ToDesk

**日期**：2026-09-18  
**tags**: `todesk` `dual-mac` `memory-git` `oneshot`

## 结论

旧机 ToDesk 过旧、SSH/远控不通时，可用 `youchu-memory` 下发 oneshot：

1. `config/oneshot_upgrade_todesk.env` → `ENABLED=1` `TARGET_HOST=old-mac`
2. `scripts/upgrade_todesk_oneshot.sh`：拉官方 DMG → UI 点「立即安装」→ **截获** `ToDesk_*.pkg`（杀安装器，避开密码框）→ `pkgutil --expand` → 覆盖 `/Applications/ToDesk.app`（目录可写即可，不必 sudo）→ 重启客户端
3. `sync-memory-git.sh` 在 **pull 之后**后台触发；`worklog_dual_mac_sync` 作旧 sync 兜底

## 硬条件

- 旧机 launchd 仍在跑 memory sync
- 自动化点安装器需要「辅助功能」授权给执行方（Terminal / osascript）；失败会冷却 30 分钟重试，并把安装器放到 `~/Downloads`
- 官方 DMG：`https://dl.todesk.com/official/ToDesk_Installer.dmg`（`www.todesk.com/official/...` 会 404）

## 验收

看旧机下一轮 sync 后：

- `~/.dc-platform/state/oneshot_upgrade_todesk.stamp` → `status=ok`
- `ops-mirror/hosts/old-mac/todesk_upgrade.md`
- `defaults read /Applications/ToDesk.app/Contents/Info CFBundleShortVersionString`
