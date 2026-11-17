# 记忆全自动同步（old-mac 权威 · new-mac 贡献每日动作）

- **仓**：`youchu-memory` → `~/.dc-platform/memory`
- **权威**：`work-log/AUTHORITY_HOST=old-mac`（正式日报 / TG 推送 / 自动化主控）
- **工作机**：`WORKLOG_HOST_ID=new-mac` → 只写 `work-log/hosts/new-mac/`，经 Git 合并；**不覆盖** `work-log/reports/` 权威稿
- **本机禁用自动化**：`~/.dc-platform/config/DISABLE_LOCAL_AUTOMATION`（new-mac 保留；不抢 bot/poller/权威日报）
- **定时**：`config/memory_sync.env`
  - 双机：`MODE=interval` → 按 `INTERVAL_SEC`（默认 120s）
- **脚本**：`scripts/sync-memory-git.sh`（仓内为权威；runtime 副本会自升级）
- **自愈**：work-log / hosts / recall 索引冲突自动解；不行则 reset 到 origin 再导本机 hosts 重推
- **每次 sync 还会**：`worklog_dual_mac_sync.py` + `ops_mirror_to_memory.py` + `export_noncode_mirrors.py`
- **OneHR / bot / poller**：由 **old-mac** 常驻；new-mac 勿抢同名 LaunchAgent

## new-mac 每日动作怎么进双机

1. 收尾写 `CHcode/.cursor/work-log/YYYY-MM-DD.md`（不写则对端汇不到）
2. `sync-memory-git.sh` / LaunchAgent 每约 2 分钟导出到 `hosts/new-mac/` 并推仓
3. old-mac 拉仓后合并进 `work-log/当日.md`；正式日报仍只认 old-mac 权威稿

手动：`bash ~/.dc-platform/scripts/sync-memory-git.sh`  
日志：`~/.dc-platform/logs/memory-git-sync.log`  
架构说明：`feedback_dual_mac_hub_sync.md`
