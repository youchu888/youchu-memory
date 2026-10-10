# agent-bus 手工迁主（old-mac → new-mac）

单主即可。old-mac 要重启、关机或下线时，不必干等，按下面顺序把收消息迁到 new-mac。  
消息在服务端，不在本机。游标拷对了，新机接着拉，不重放已结案、也不跳号。

**两台不许同时拉。** 先停旧的，确认进程没了，再启新的。

当前权威文件：`~/.dc-platform/memory/work-log/AUTHORITY_HOST`（一行主机名）。  
机器身份别改：各机 `~/.dc-platform/memory/.env.host` 的 `WORKLOG_HOST_ID` 仍是自己的 `old-mac` / `new-mac`。

状态目录（两台路径相同）：

`$HOME/Library/Application Support/youchu-agent-bus/state`

## 顺序

### 1. old-mac 停 poller

`KeepAlive` 开着，只 kill 会被 launchd 拉起来。必须卸掉服务。

```bash
launchctl bootout "gui/$(id -u)/com.youchu.agent-bus-poller"
bash "$HOME/Library/Application Support/youchu-agent-bus/scripts/stop-agent-bus-wake-bridge.sh" || true
bash "$HOME/Library/Application Support/youchu-agent-bus/scripts/stop-agent-bus-poller.sh" || true
```

若 `state/daemon.pid` 里的进程还在，再 `kill` 它。

停干净的判据（两条都要满足）：

```bash
launchctl print "gui/$(id -u)/com.youchu.agent-bus-poller"   # 应报找不到服务
pgrep -lf 'agent_bus_poll|start-agent-bus-daemon|wake-bridge' || echo STOPPED
```

必须看到 `STOPPED`。没停干净不要做第 2 步。

### 2. 拷游标和结案标记到 new-mac

旧 poller 已停之后再拷，避免拷的过程中 offset 还在涨。

| 文件 | 作用 |
|---|---|
| `youchu_ai.offset` | 已拉到的消息号 |
| `youchu_ai_processed.json` | 结案标记 |
| `youchu_ai_history_seal_cutoff` | 封存水位，避免把已封历史重新叫醒 |

拷到 new-mac 的同一状态目录。拷完对 `shasum`，三份都一致再往下。

### 3. 权威主机改为 new-mac

改 `~/.dc-platform/memory/work-log/AUTHORITY_HOST`：第一条非注释行写成 `new-mac`。  
然后：

```bash
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

new-mac 上先拉取记忆仓，确认磁盘上的 `AUTHORITY_HOST` 已是 `new-mac`，再启 poller。

### 4. 只在 new-mac 启 poller

再确认 old-mac 上一步的 `pgrep` 仍是 `STOPPED`。然后在 new-mac：

```bash
bash ~/Desktop/CHcode/.cursor/scripts/install-agent-bus-launchd.sh
```

服务已经装过时，不要在 old-mac 上再跑这份安装脚本。安装脚本会 `bootstrap` + `kickstart` `com.youchu.agent-bus-poller`。

启完在 new-mac 看 poller 心跳和 `youchu_ai.offset`，应从拷过去的号接着涨，而不是从 0 重拉。

## 不要动

- VPN（`com.youchu.vpn-sync`）
- 打卡、TG bot、别的 launchd
- 两台的 `WORKLOG_HOST_ID`
