# tgbot 私聊回写 + 旧机拉回 bot

- 日期：2026-11-23
- 个人仓：`youchu888/youchu-memory`（**不要**推进公司 `dc-parent`）
- 问题：`TG_DM_EXEC_MODE=wake_ide` 只叫醒 IDE，Telegram 看不见后续；双机同 token 会 409 抢轮询
- 定案：私聊默认 `cursor_agent`；日常 bot 权威在 **old-mac**；new-mac 角色 `auxiliary` 不起 bot

## new-mac：停抢（本机执行）

```bash
bash ~/.dc-platform/memory/patches/tgbot-dm-cursor-agent-restore/release-bot-on-new-mac.sh
```

## old-mac：自动拉回（推荐，连不上旧机时用）

个人仓推送后，旧机 `memory-git-sync`（约 2 分钟一轮）pull 会触发 oneshot，**只跑一次**：

- 配置：`config/oneshot_reclaim_tgbot_oldmac.env`（`ENABLED=1` `TARGET_HOST=old-mac`）
- 脚本：`scripts/reclaim_tgbot_oldmac_oneshot.sh` → 调本目录 `reclaim-bot-on-old-mac.sh`
- 成功写 stamp：`~/.dc-platform/state/oneshot_reclaim_tgbot_oldmac.stamp`，并把 `ENABLED` 置 0

手动（能登旧机时）：

```bash
bash ~/.dc-platform/memory/patches/tgbot-dm-cursor-agent-restore/reclaim-bot-on-old-mac.sh
```

## 文件

| 文件 | 用途 |
|------|------|
| `restore-dm-cursor-agent.sh` | 把 `.env` / 默认值改回 `cursor_agent` |
| `release-bot-on-new-mac.sh` | new-mac 停 bot、角色改 auxiliary |
| `reclaim-bot-on-old-mac.sh` | old-mac 应用修复并起 bot |
