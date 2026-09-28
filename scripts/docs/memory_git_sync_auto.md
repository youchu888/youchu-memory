# 记忆全自动同步（new-mac 权威 · 2026-09-28）

- **仓**：`youchu-memory` → `~/.dc-platform/memory`
- **权威**：`work-log/AUTHORITY_HOST=new-mac`，`WORKLOG_HOST_ID=new-mac`
- **定时**：`config/memory_sync.env`
  - 单机：`MODE=daily` → 每天 **19:00**
  - 双机：`MODE=interval` → 按 `INTERVAL_SEC`（默认 120s）
- **脚本**：`scripts/sync-memory-git.sh`（仓内为权威；runtime 副本会自升级）
- **自愈**：work-log / hosts / recall 索引冲突自动解；不行则 reset 到 origin 再导本机 hosts 重推
- **每次 sync 还会**：`worklog_dual_mac_sync.py` + `ops_mirror_to_memory.py` + `export_noncode_mirrors.py`
- **OneHR / bot / poller**：现由 **new-mac** 常驻；old-mac 停机勿再装同名 LaunchAgent

手动：`bash ~/.dc-platform/scripts/sync-memory-git.sh`  
日志：`~/.dc-platform/logs/memory-git-sync.log`
