# agent-bus 只读镜像

权威机（`work-log/AUTHORITY_HOST`，当前多为 `old-mac`）导出 `from-<host>/`：

- `youchu_ai_inbox.jsonl` / `youchu_ai_sent.json` / `youchu_ai_processed.json` / `youchu_ai.offset`
- `OPEN.md`（未结案摘要）
- `MANIFEST.json`

非权威机（如 `new-mac`）经 `sync-memory-git.sh` 拉取后，物化到：

`~/Library/Application Support/youchu-agent-bus/readonly-mirror/`

查看：

```bash
bash ~/.dc-platform/memory/scripts/agent-bus-readonly-status.sh
# 或
bash ~/Desktop/CHcode/.cursor/scripts/agent-bus-readonly-status.sh
```

## 触发

1. **定时**：memory-git-sync 每轮 `both`（权威 export + 非权威 materialize）
2. **结案**：权威机 `agent_bus_send.py --kind reply` 成功后 best-effort `export`（跨机仍等下一轮 sync）

## 禁止

- 非权威机用本目录启 poller / 改 `AGENT_BUS_STATE_DIR` 指过来
- 在只读副本上 ack / reply / mark_processed
