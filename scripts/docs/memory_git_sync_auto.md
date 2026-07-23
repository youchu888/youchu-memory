# 双 Mac 记忆全自动同步

- **仓**：`youchu-memory` → `~/.dc-platform/memory`
- **定时**：`com.youchu.memory-git-sync` 每 10 分钟
- **脚本**：`scripts/sync-memory-git.sh`（仓内为权威；launchd 副本会自升级）
- **自愈**：work-log / hosts / recall 索引冲突自动解；不行则 reset 到 origin 再导本机 hosts 重推
- **本机 id**：`memory/.env.host` 里 `WORKLOG_HOST_ID=old-mac|new-mac`

手动：`bash ~/.dc-platform/scripts/sync-memory-git.sh`
日志：`~/.dc-platform/logs/memory-git-sync.log`
